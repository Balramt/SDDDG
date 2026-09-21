"""
SADDG Class Expression Converter implementation for OWL to Natural Language conversion.
Handles N-ary AST normalization, property frame extraction, dependency graph factorization,
and morphological surface realization for Description Logic concepts.
"""

from dataclasses import dataclass, field
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
from verbalizer.common.grammar import EnglishGrammar, Words
from verbalizer.owl2nl.converters.base import BaseClassExpressionConverter
from verbalizer.owl2nl.input import OntologyInput


@dataclass
class SyntacticClause:
    """Represents a factored linguistic dependency clause prior to surface text realization."""

    head_noun: str
    is_plural: bool = True
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
    and subject-verb agreement enforcement for OWL class expressions.
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

    def _determine_property_frame(self, prop_item: Any) -> dict[str, str]:
        """
        Categorizes object/data properties into linguistic syntactic frames:
        - TVP (Transitive Verb Phrase): 'located in', 'lives in', 'owns'
        - RNP (Relational Noun Phrase): 'birth place', 'mother', 'author'
        - PP (Prepositional Phrase): 'born in', 'part of'
        """
        label = self.get_label(prop_item).lower().strip()
        words = label.split()

        prepositions = {
            "in", "at", "by", "from", "of", "to", "with", "on", "for", "about", "through", "over"
        }

        if not words:
            return {
                "type": "TVP",
                "phrase": label,
                "rel_clause_prefix": f"that {label}",
            }

        first_word = words[0]
        last_word = words[-1]

        # 1. Expressed with auxiliary verbs or explicit action verbs
        if first_word in ("is", "are", "was", "were"):
            return {
                "type": "TVP",
                "phrase": label,
                "rel_clause_prefix": f"that {label}",
            }
        elif first_word in ("has", "have", "contains", "owns", "includes"):
            return {
                "type": "TVP",
                "phrase": label,
                "rel_clause_prefix": f"that {label}",
            }

        # 2. Ends with a preposition
        elif last_word in prepositions:
            if first_word.endswith("ed") or first_word in ("born", "known", "made"):
                return {
                    "type": "PP",
                    "phrase": label,
                    "rel_clause_prefix": f"that is {label}",
                }
            else:
                return {
                    "type": "TVP",
                    "phrase": label,
                    "rel_clause_prefix": f"that {label}",
                }

        # 3. Third person singular verbs
        elif first_word.endswith("s") and not first_word.endswith("ss"):
            return {
                "type": "TVP",
                "phrase": label,
                "rel_clause_prefix": f"that {label}",
            }

        # 4. Relational Noun Phrase (RNP)
        else:
            return {
                "type": "RNP",
                "phrase": label,
                "rel_clause_prefix": f"whose {label} is",
            }

    def _verbalize_filler(self, filler: Any) -> str:
        """Verbalizes restriction fillers cleanly based on entity type."""
        if isinstance(filler, OWLClass):
            label = self.get_label(filler)
            singular_label = self.grammar.singular(label)
            return self.grammar.with_article(singular_label)
        elif isinstance(filler, OWLNamedIndividual):
            label = self.get_label(filler)
            return label.title()
        elif isinstance(filler, OWLLiteral):
            return str(filler.literal)
        elif isinstance(filler, OWLClassExpression):
            return self.convert(filler, is_filler=True)
        else:
            return str(filler)

    def _verbalize_restriction(self, rest: OWLClassExpression) -> str:
        """Translates single DL restrictions into dependent relative clauses."""
        if isinstance(rest, OWLObjectSomeValuesFrom):
            prop = rest.get_property()
            frame = self._determine_property_frame(prop)
            filler_str = self._verbalize_filler(rest.get_filler())

            if frame["type"] == "RNP":
                return f"whose {frame['phrase']} is {filler_str}"
            else:
                return f"{frame['rel_clause_prefix']} {filler_str}"

        elif isinstance(rest, OWLObjectHasValue):
            prop = rest.get_property()
            frame = self._determine_property_frame(prop)
            val = rest.get_value() if hasattr(rest, "get_value") else rest.get_filler()
            val_str = self._verbalize_filler(val)

            if frame["type"] == "RNP":
                return f"whose {frame['phrase']} is {val_str}"
            else:
                return f"{frame['rel_clause_prefix']} {val_str}"

        elif isinstance(rest, OWLObjectAllValuesFrom):
            prop = rest.get_property()
            frame = self._determine_property_frame(prop)
            filler = rest.get_filler()
            filler_label = (
                self.grammar.plural(self.get_label(filler))
                if isinstance(filler, OWLClass)
                else self._verbalize_filler(filler)
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

            filler_label = (
                self.grammar.plural(self.get_label(filler))
                if isinstance(filler, OWLClass)
                else self._verbalize_filler(filler)
            )

            if isinstance(rest, OWLObjectMinCardinality):
                prefix = Words.AT_LEAST
            elif isinstance(rest, OWLObjectMaxCardinality):
                prefix = Words.AT_MOST
            else:
                prefix = Words.EXACTLY

            return f"who have {prefix} {card_word} {prop_label} who are {filler_label}"

        elif isinstance(rest, OWLObjectComplementOf):
            operand = rest.get_operand()
            if isinstance(operand, OWLClass):
                label = self.get_label(operand)
                return f"that is not a {label}"
            else:
                return f"that is not {self.convert(operand, is_filler=True)}"

        elif isinstance(rest, (OWLDataSomeValuesFrom, OWLDataHasValue)):
            prop = rest.get_property()
            prop_label = self.get_label(prop)
            if isinstance(rest, OWLDataHasValue):
                val = rest.get_value() if hasattr(rest, "get_value") else rest.get_filler()
                val_str = str(val.literal) if hasattr(val, "literal") else str(val)
                return f"whose {prop_label} is {val_str}"
            else:
                return f"that has a {prop_label}"

        # Fallback for unhandled restriction constructs
        iri_str = rest.iri.as_str() if hasattr(rest, "iri") else str(rest)
        return f"that is related via {self.grammar.clean_iri_fragment(iri_str)}"

    def _verbalize_intersection(
        self, expr: OWLObjectIntersectionOf, is_filler: bool = False
    ) -> str:
        """Processes intersection AST nodes via SADDG graph factorization."""
        operands = self._flatten_intersection(expr)

        atomic_classes: List[OWLClass] = []
        restrictions: List[OWLClassExpression] = []

        for op in operands:
            if isinstance(op, OWLClass):
                atomic_classes.append(op)
            else:
                restrictions.append(op)

        # 1. Determine Head Noun from Atomic Classes
        if atomic_classes:
            primary_label = self.get_label(atomic_classes[0])
            if is_filler:
                singular_label = self.grammar.singular(primary_label)
                head_noun = self.grammar.with_article(singular_label)
            else:
                head_noun = self.grammar.plural(primary_label)
            extra_atomic = atomic_classes[1:]
        else:
            head_noun = (
                Words.EVERYTHING
                if self.mode == VerbalizerMode.STANDARD
                else "things"
            )
            extra_atomic = []

        clause = SyntacticClause(head_noun=head_noun)

        # 2. Add extra atomic class constraints
        for ac in extra_atomic:
            label = self.get_label(ac)
            if is_filler:
                singular_label = self.grammar.singular(label)
                clause.relative_clauses.append(f"that is a {singular_label}")
            else:
                plural_label = self.grammar.plural(label)
                clause.relative_clauses.append(f"that are {plural_label}")

        # 3. Factorize and aggregate restrictions
        for rest in restrictions:
            rel_str = self._verbalize_restriction(rest)
            if rel_str:
                clause.relative_clauses.append(rel_str)

        return clause.realize()

    def _verbalize_union(self, expr: OWLObjectUnionOf, is_filler: bool = False) -> str:
        """Processes union AST nodes cleanly with logical disjunction ('or')."""
        operands = self._flatten_union(expr)
        parts: List[str] = [self.convert(op, is_filler=is_filler) for op in operands]

        if len(parts) == 1:
            return parts[0]
        elif len(parts) == 2:
            return f"{parts[0]} or {parts[1]}"
        else:
            return ", ".join(parts[:-1]) + f", or {parts[-1]}"

    def _verbalize_standalone_restriction(
        self, expr: OWLClassExpression, is_filler: bool = False
    ) -> str:
        """Wraps a standalone restriction with a root subject placeholder."""
        rel_clause = self._verbalize_restriction(expr)
        head = Words.EVERYTHING if self.mode == VerbalizerMode.STANDARD else "things"
        return f"{head} {rel_clause}"

    def convert(self, item: OWLClassExpression, is_filler: bool = False) -> str:
        """
        Converts an OWLAPY OWLClassExpression into natural English text.
        Entry point for SADDG processing.
        """
        if isinstance(item, OWLClass):
            label = self.get_label(item)
            if is_filler:
                singular_label = self.grammar.singular(label)
                return self.grammar.with_article(singular_label)
            return self.grammar.plural(label)

        elif isinstance(item, OWLObjectIntersectionOf):
            return self._verbalize_intersection(item, is_filler=is_filler)

        elif isinstance(item, OWLObjectUnionOf):
            return self._verbalize_union(item, is_filler=is_filler)

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
            return self._verbalize_standalone_restriction(item, is_filler=is_filler)

        elif isinstance(item, OWLObjectComplementOf):
            operand_text = self.convert(item.get_operand(), is_filler=True)
            return f"everything that is not {operand_text}"

        else:
            # General fallback for non-standard class expressions
            iri_str = item.iri.as_str() if hasattr(item, "iri") else str(item)
            return self.grammar.clean_iri_fragment(iri_str)