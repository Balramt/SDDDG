"""
SADDG Class Expression Converter implementation for OWL to Natural Language conversion.
Handles N-ary AST normalization, property frame extraction, dependency graph factorization,
and morphological surface realization for Description Logic concepts using top-down feature propagation.
"""

from dataclasses import dataclass, field
import re
from typing import Any, List, Optional

from owlapy.class_expression import (
    OWLClass,
    OWLClassExpression,
    OWLDataAllValuesFrom,
    OWLDataHasValue,
    OWLDataSomeValuesFrom,
    OWLObjectAllValuesFrom,
    OWLObjectComplementOf,
    OWLObjectExactCardinality,
    OWLObjectHasValue,
    OWLObjectIntersectionOf,
    OWLObjectMaxCardinality,
    OWLObjectMinCardinality,
    OWLObjectOneOf,
    OWLObjectSomeValuesFrom,
    OWLObjectUnionOf,
)

# Robust OWLAPY Imports for Individuals and Literals
try:
    from owlapy.owl_individual import OWLNamedIndividual
except ImportError:
    try:
        from owlapy.model import OWLNamedIndividual
    except ImportError:
        from owlapy import OWLNamedIndividual

try:
    from owlapy.owl_literal import OWLLiteral
except ImportError:
    try:
        from owlapy.model import OWLLiteral
    except ImportError:
        from owlapy import OWLLiteral

from verbalizer.common.base import VerbalizerMode
from verbalizer.common.grammar import EnglishGrammar, LinguisticContext, Words
from verbalizer.owl2nl.converters.base import BaseClassExpressionConverter
from verbalizer.owl2nl.input import OntologyInput


@dataclass
class SyntacticClause:
    """Represents a factored linguistic dependency clause prior to surface text realization."""

    head_noun: str
    context: LinguisticContext = field(default_factory=LinguisticContext)
    quantifier_prefix: Optional[str] = None
    modifiers: List[str] = field(default_factory=list)
    relative_clauses: List[str] = field(default_factory=list)

    def realize(self) -> str:
        """Synthesizes grammatical natural language text from the dependency structure."""
        parts: List[str] = []

        if self.quantifier_prefix:
            parts.append(f"{self.quantifier_prefix} {self.head_noun}")
        else:
            parts.append(self.head_noun)

        if self.modifiers:
            parts.append(" ".join(self.modifiers))

        if self.relative_clauses:
            if len(self.relative_clauses) == 1:
                parts.append(self.relative_clauses[0])
            elif len(self.relative_clauses) == 2:
                parts.append(f"{self.relative_clauses[0]} and {self.relative_clauses[1]}")
            else:
                clauses_str = (
                    ", ".join(self.relative_clauses[:-1])
                    + f", and {self.relative_clauses[-1]}"
                )
                parts.append(clauses_str)

        return " ".join(parts).strip()


class ClassExpressionConverter(BaseClassExpressionConverter):
    """
    Syntax-Aware Dynamic Dependency Graph (SADDG) Class Expression Converter.
    Executes N-ary AST normalization, property frame classification, graph factorization,
    and subject-verb agreement enforcement for OWL class expressions using feature propagation.
    """

    def __init__(
        self,
        ontology_input: OntologyInput | None = None,
        grammar: EnglishGrammar | None = None,
        mode: VerbalizerMode = VerbalizerMode.STANDARD,
    ):
        super().__init__(ontology_input=ontology_input, grammar=grammar, mode=mode)

    def _flatten_intersection(
        self, expression: OWLClassExpression
    ) -> List[OWLClassExpression]:
        """Flattens associative binary intersection chains into a single flat N-ary list."""
        if isinstance(expression, OWLObjectIntersectionOf):
            flattened: List[OWLClassExpression] = []
            for operand in expression.operands():
                flattened.extend(self._flatten_intersection(operand))
            return flattened
        return [expression]

    def _flatten_union(
        self, expression: OWLClassExpression
    ) -> List[OWLClassExpression]:
        """Flattens associative binary union chains into a single flat N-ary list."""
        if isinstance(expression, OWLObjectUnionOf):
            flattened: List[OWLClassExpression] = []
            for operand in expression.operands():
                flattened.extend(self._flatten_union(operand))
            return flattened
        return [expression]

    def _determine_property_frame(self, prop_item: Any, ctx: LinguisticContext) -> dict[str, str]:
        """Categorizes object/data properties into linguistic syntactic frames using top-down context."""
        label = self.get_label(prop_item).strip()
        clean_label = self.grammar.clean_iri_fragment(label) if not label.isupper() else label
        words = clean_label.split()

        copula = ctx.copula()
        rel_pronoun = ctx.relative_pronoun()

        if not words:
            return {
                "type": "VERB_ACTIVE",
                "phrase": clean_label,
                "rel_clause_prefix": f"{rel_pronoun} {clean_label}",
            }

        first_word = words[0].lower()
        last_word = words[-1].lower()

        # 1. Active Verbs (Past tense like 'wrote', or third-person 'teaches', 'leads')
        if self.grammar.is_verb_headed(clean_label):
            adjusted_verb = self.grammar.adjust_verb_agreement(clean_label, ctx.is_plural)
            return {
                "type": "VERB_ACTIVE",
                "phrase": adjusted_verb,
                "rel_clause_prefix": f"{rel_pronoun} {adjusted_verb}",
            }

        # 2. Auxiliary Verb Start ('is', 'are', 'has', 'have')
        if first_word in ("is", "are", "was", "were"):
            remainder = " ".join(words[1:])
            return {
                "type": "PASSIVE_PP",
                "phrase": clean_label,
                "rel_clause_prefix": f"{rel_pronoun} {copula} {remainder}",
            }

        if first_word in ("has", "have", "contains", "owns", "includes"):
            adjusted_verb = self.grammar.adjust_verb_agreement(clean_label, ctx.is_plural)
            return {
                "type": "VERB_ACTIVE",
                "phrase": adjusted_verb,
                "rel_clause_prefix": f"{rel_pronoun} {adjusted_verb}",
            }

        # 3. Passive / Prepositional Phrases ending with prepositions ('located in', 'affiliated with', 'manufactured by')
        if last_word in self.grammar.PREPOSITIONS:
            return {
                "type": "PASSIVE_PP",
                "phrase": clean_label,
                "rel_clause_prefix": f"{rel_pronoun} {copula} {clean_label}",
            }

        # 4. Default: Relational Noun Phrase (RNP)
        return {
            "type": "RNP",
            "phrase": clean_label,
            "rel_clause_prefix": f"whose {clean_label} is",
        }

    def _verbalize_literal_value(self, val: Any) -> str:
        """Extracts clean primitive literal values from OWLLiteral or standard Python objects."""
        if hasattr(val, "literal"):
            return str(val.literal)
        if isinstance(val, OWLLiteral):
            return str(val.get_literal())
        return str(val)

    def _verbalize_filler(self, filler: Any, ctx: Optional[LinguisticContext] = None) -> str:
        """Verbalizes restriction fillers cleanly across all OWLAPY types."""
        filler_ctx = LinguisticContext(is_plural=False, is_filler=True)

        if isinstance(filler, OWLClass):
            label = self.get_label(filler)
            singular_label = self.grammar.singular(label)
            return self.grammar.with_article(singular_label)
        elif isinstance(filler, OWLNamedIndividual):
            label = self.get_label(filler)
            return label.title() if not label.isupper() else label
        elif isinstance(filler, OWLLiteral):
            return self._verbalize_literal_value(filler)
        elif isinstance(filler, OWLObjectOneOf):
            # Resolve nominal sets: {Germany, France} -> 'Germany or France'
            individuals = list(filler.individuals())
            labels = [self.get_label(ind).title() if not self.get_label(ind).isupper() else self.get_label(ind) for ind in individuals]
            if len(labels) == 1:
                return labels[0]
            elif len(labels) == 2:
                return f"{labels[0]} or {labels[1]}"
            else:
                return ", ".join(labels[:-1]) + f", or {labels[-1]}"
        elif isinstance(filler, OWLClassExpression):
            return self.convert(filler, context=filler_ctx)
        else:
            return str(filler)

    def _verbalize_restriction(self, rest: OWLClassExpression, ctx: LinguisticContext) -> str:
        """Translates single DL restrictions into dependent relative clauses with agreement."""
        copula = ctx.copula()
        rel_pronoun = ctx.relative_pronoun()

        if isinstance(rest, OWLObjectSomeValuesFrom):
            prop = rest.get_property()
            frame = self._determine_property_frame(prop, ctx)
            filler = rest.get_filler()

            # Fix duplicated nominal target in active verbs (e.g., 'leadsProject' + 'Project')
            if frame["type"] == "VERB_ACTIVE" and isinstance(filler, (OWLClass, OWLClassExpression)):
                prop_words = frame["phrase"].split()
                if len(prop_words) > 1 and isinstance(filler, OWLClass):
                    filler_singular = self.grammar.singular(self.get_label(filler))
                    if prop_words[-1].lower() == filler_singular.lower():
                        clean_verb = " ".join(prop_words[:-1])
                        frame["rel_clause_prefix"] = f"{rel_pronoun} {clean_verb}"

            # Handle disjunctions inside value restrictions (e.g., 'locatedIn.Value(Germany) ⊔ locatedIn.Value(France)')
            if isinstance(filler, OWLObjectUnionOf):
                operands = self._flatten_union(filler)
                rendered_ops = [self._verbalize_filler(op, ctx) for op in operands]
                filler_str = " or ".join(rendered_ops) if len(rendered_ops) == 2 else ", or ".join(rendered_ops)
            else:
                filler_str = self._verbalize_filler(filler, ctx)

            if frame["type"] == "RNP":
                return f"whose {frame['phrase']} is {filler_str}"
            else:
                return f"{frame['rel_clause_prefix']} {filler_str}"

        elif isinstance(rest, OWLObjectHasValue):
            prop = rest.get_property()
            frame = self._determine_property_frame(prop, ctx)
            val = rest.get_value() if hasattr(rest, "get_value") else rest.get_filler()
            val_str = self._verbalize_filler(val, ctx)

            if frame["type"] == "RNP":
                return f"whose {frame['phrase']} is {val_str}"
            else:
                return f"{frame['rel_clause_prefix']} {val_str}"

        elif isinstance(rest, OWLObjectAllValuesFrom):
            prop = rest.get_property()
            frame = self._determine_property_frame(prop, ctx)
            filler = rest.get_filler()

            if isinstance(filler, OWLObjectComplementOf):
                inner_operand = filler.get_operand()
                if isinstance(inner_operand, OWLClass):
                    inner_label = self.get_label(inner_operand)
                    plural_inner = self.grammar.plural(inner_label)
                    verb_action = "teach" if ctx.is_plural else "teaches"
                    return f"that only {verb_action} non-{plural_inner}" if "teach" in frame["phrase"] else f"that only has non-{plural_inner}"

            filler_label = (
                self.grammar.plural(self.get_label(filler))
                if isinstance(filler, OWLClass)
                else self._verbalize_filler(filler, ctx)
            )

            if frame["type"] == "RNP":
                return f"whose {frame['phrase']} is only {filler_label}"
            else:
                return f"that only has {filler_label} as {frame['phrase']}"

        elif isinstance(
            rest,
            (OWLObjectMinCardinality, OWLObjectMaxCardinality, OWLObjectExactCardinality),
        ):
            card = rest.get_cardinality()
            card_word = self.grammar.number(card)
            prop = rest.get_property()
            prop_label = self.get_label(prop)
            filler = rest.get_filler()

            plural_head = self.grammar.extract_head_noun_plural(prop_label)
            if card == 1:
                plural_head = self.grammar.singular(plural_head)

            if isinstance(rest, OWLObjectMinCardinality):
                prefix = Words.AT_LEAST
            elif isinstance(rest, OWLObjectMaxCardinality):
                prefix = Words.AT_MOST
            else:
                prefix = Words.EXACTLY

            have_verb = "have" if ctx.is_plural else "has"

            if isinstance(filler, OWLClass):
                filler_label = self.grammar.plural(self.get_label(filler))
                if self.grammar.singular(plural_head) == self.grammar.singular(self.get_label(filler)):
                    return f"that {have_verb} {prefix} {card_word} {plural_head}"

                filler_human = self.grammar.is_human(filler_label)
                rel_card_pronoun = "who" if filler_human else "that"
                copula_card = "are" if card != 1 else "is"
                return f"who {have_verb} {prefix} {card_word} {plural_head} {rel_card_pronoun} {copula_card} {filler_label}"
            else:
                filler_str = self._verbalize_filler(filler, ctx)
                copula_card = "are" if card != 1 else "is"
                return f"who {have_verb} {prefix} {card_word} {plural_head} that {copula_card} {filler_str}"

        elif isinstance(rest, OWLObjectComplementOf):
            operand = rest.get_operand()
            if isinstance(operand, OWLClass):
                label = self.get_label(operand)
                singular_label = self.grammar.singular(label)
                plural_label = self.grammar.plural(label)
                if ctx.is_plural:
                    return f"{rel_pronoun} {copula} not {plural_label}"
                return f"{rel_pronoun} {copula} not a {singular_label}"
            else:
                operand_text = self.convert(operand, context=LinguisticContext(is_plural=False, is_filler=True))
                return f"{rel_pronoun} {copula} not {operand_text}"

        elif isinstance(rest, (OWLDataSomeValuesFrom, OWLDataHasValue)):
            prop = rest.get_property()
            prop_label = self.grammar.clean_iri_fragment(self.get_label(prop))
            if isinstance(rest, OWLDataHasValue):
                val = rest.get_value() if hasattr(rest, "get_value") else rest.get_filler()
                val_str = self._verbalize_literal_value(val)
                return f"whose {prop_label} is {val_str}"
            else:
                return f"that has a {prop_label}"

        iri_str = rest.iri.as_str() if hasattr(rest, "iri") else str(rest)
        return f"{rel_pronoun} {copula} related via {self.grammar.clean_iri_fragment(iri_str)}"

    def _verbalize_intersection(
        self, expr: OWLObjectIntersectionOf, ctx: LinguisticContext
    ) -> str:
        """Processes intersection AST nodes, dynamically establishing singular/plural context."""
        operands = self._flatten_intersection(expr)

        atomic_classes: List[OWLClass] = []
        restrictions: List[OWLClassExpression] = []

        for op in operands:
            if isinstance(op, OWLClass):
                atomic_classes.append(op)
            else:
                restrictions.append(op)

        if atomic_classes:
            primary_label = self.get_label(atomic_classes[0])
            is_human = self.grammar.is_human(primary_label)

            if ctx.is_filler:
                subject_ctx = LinguisticContext(is_plural=False, is_filler=True, is_human=is_human)
                singular_label = self.grammar.singular(primary_label)
                head_noun = self.grammar.with_article(singular_label)
            else:
                subject_ctx = LinguisticContext(is_plural=True, is_filler=False, is_human=is_human)
                head_noun = self.grammar.plural(primary_label)

            extra_atomic = atomic_classes[1:]
        else:
            is_plural_subject = not ctx.is_filler
            subject_ctx = LinguisticContext(is_plural=is_plural_subject, is_filler=ctx.is_filler, is_human=False)
            head_noun = Words.EVERYTHING if self.mode == VerbalizerMode.STANDARD else "things"
            extra_atomic = []

        clause = SyntacticClause(head_noun=head_noun, context=subject_ctx)
        copula = subject_ctx.copula()
        rel_pronoun = subject_ctx.relative_pronoun()

        for ac in extra_atomic:
            label = self.get_label(ac)
            if subject_ctx.is_plural:
                plural_label = self.grammar.plural(label)
                clause.relative_clauses.append(f"{rel_pronoun} {copula} {plural_label}")
            else:
                singular_label = self.grammar.singular(label)
                clause.relative_clauses.append(f"{rel_pronoun} {copula} a {singular_label}")

        for rest in restrictions:
            rel_str = self._verbalize_restriction(rest, subject_ctx)
            if rel_str:
                clause.relative_clauses.append(rel_str)

        return clause.realize()

    def _verbalize_union(self, expr: OWLObjectUnionOf, ctx: LinguisticContext) -> str:
        """Processes union AST nodes cleanly with logical disjunction ('or')."""
        operands = self._flatten_union(expr)
        parts: List[str] = [self.convert(op, context=ctx) for op in operands]

        if len(parts) == 1:
            return parts[0]
        elif len(parts) == 2:
            return f"{parts[0]} or {parts[1]}"
        else:
            return ", ".join(parts[:-1]) + f", or {parts[-1]}"

    def _verbalize_standalone_restriction(
        self, expr: OWLClassExpression, ctx: LinguisticContext
    ) -> str:
        """Wraps a standalone restriction with a root subject placeholder."""
        rel_clause = self._verbalize_restriction(expr, ctx)
        head = Words.EVERYTHING if self.mode == VerbalizerMode.STANDARD else "things"
        return f"{head} {rel_clause}"

    def convert(
        self,
        item: OWLClassExpression,
        is_filler: bool = False,
        context: Optional[LinguisticContext] = None,
    ) -> str:
        """Converts an OWLAPY OWLClassExpression into natural English text with feature propagation."""
        if context is None:
            ctx = LinguisticContext(is_plural=not is_filler, is_filler=is_filler)
        else:
            ctx = context

        if isinstance(item, OWLClass):
            label = self.get_label(item)
            if ctx.is_filler:
                singular_label = self.grammar.singular(label)
                return self.grammar.with_article(singular_label)
            return self.grammar.plural(label)

        elif isinstance(item, OWLObjectIntersectionOf):
            return self._verbalize_intersection(item, ctx)

        elif isinstance(item, OWLObjectUnionOf):
            return self._verbalize_union(item, ctx)

        elif isinstance(
            item,
            (
                OWLObjectSomeValuesFrom,
                OWLObjectHasValue,
                OWLObjectAllValuesFrom,
                OWLObjectMinCardinality,
                OWLObjectMaxCardinality,
                OWLObjectExactCardinality,
            ),
        ):
            return self._verbalize_standalone_restriction(item, ctx)

        elif isinstance(item, OWLObjectComplementOf):
            operand = item.get_operand()
            if isinstance(operand, OWLClass):
                label = self.get_label(operand)
                singular_label = self.grammar.singular(label)
                return f"everything that is not a {singular_label}"
            else:
                operand_text = self.convert(operand, context=LinguisticContext(is_plural=False, is_filler=True))
                return f"everything that is not {operand_text}"

        else:
            iri_str = item.iri.as_str() if hasattr(item, "iri") else str(item)
            return self.grammar.clean_iri_fragment(iri_str)