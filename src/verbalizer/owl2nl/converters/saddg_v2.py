# """
# SADDG V2 Class Expression Converter.
# Implements a 3-Stage Micro-Planning Pipeline (AST -> DSyntG Tree -> Feature Propagation -> Surface Text)
# using Deep Syntactic Graphs (DSyntG) and dynamic property frame classification.
# """

# from typing import Any, List, Optional, Set

# # Safe OWLAPY imports avoiding circular dependency triggers
# import owlapy.class_expression as ce

# from verbalizer.common.base import VerbalizerMode
# from verbalizer.common.grammar import EnglishGrammar, LinguisticContext, Words
# from verbalizer.owl2nl.converters.base import BaseClassExpressionConverter
# from verbalizer.owl2nl.converters.dsyntg import DSyntNode, FrameType, SyntacticRole
# from verbalizer.owl2nl.converters.frame_classifier import PropertyFrameClassifier


# class SADDGGraphConverterV2(BaseClassExpressionConverter):
#     """
#     Syntax-Aware Dynamic Dependency Graph (SADDG) V2 Verbalizer Engine.
#     Decouples Description Logic AST parsing from surface English realization via DSyntG trees.
#     """

#     def __init__(
#         self,
#         ontology_input: Any | None = None,
#         grammar: EnglishGrammar | None = None,
#         mode: VerbalizerMode = VerbalizerMode.STANDARD,
#     ):
#         super().__init__(ontology_input=ontology_input, grammar=grammar, mode=mode)
#         self.frame_classifier = PropertyFrameClassifier(self.grammar)

#     # -------------------------------------------------------------------------
#     # Safe OWLAPY Attribute Accessors
#     # -------------------------------------------------------------------------
#     def _extract_property(self, rest: Any) -> Any:
#         if hasattr(rest, "get_property"):
#             return rest.get_property()
#         if hasattr(rest, "property"):
#             return rest.property
#         raise AttributeError(f"Unable to extract property from {type(rest)}")

#     def _extract_filler_or_value(self, rest: Any) -> Any:
#         if hasattr(rest, "get_filler"):
#             return rest.get_filler()
#         if hasattr(rest, "get_value"):
#             return rest.get_value()
#         if hasattr(rest, "filler"):
#             return rest.filler
#         if hasattr(rest, "value"):
#             return rest.value
#         raise AttributeError(f"Unable to extract filler/value from {type(rest)}")

#     def _extract_cardinality(self, rest: Any) -> int:
#         if hasattr(rest, "get_cardinality"):
#             return rest.get_cardinality()
#         if hasattr(rest, "cardinality"):
#             return rest.cardinality
#         raise AttributeError(f"Unable to extract cardinality from {type(rest)}")

#     def _verbalize_literal(self, val: Any) -> str:
#         if hasattr(val, "get_literal"):
#             return str(val.get_literal())
#         if hasattr(val, "literal"):
#             return str(val.literal)
#         return str(val)

#     # -------------------------------------------------------------------------
#     # Helper AST Flattening Logic
#     # -------------------------------------------------------------------------
#     def _flatten_intersection(
#         self, expression: ce.OWLClassExpression, visited: Optional[Set[int]] = None
#     ) -> List[ce.OWLClassExpression]:
#         visited = visited or set()
#         expr_id = id(expression)
#         if expr_id in visited:
#             return []
#         visited.add(expr_id)

#         if isinstance(expression, ce.OWLObjectIntersectionOf):
#             flattened: List[ce.OWLClassExpression] = []
#             for operand in expression.operands():
#                 flattened.extend(self._flatten_intersection(operand, visited))
#             return flattened
#         return [expression]

#     def _flatten_union(
#         self, expression: ce.OWLClassExpression, visited: Optional[Set[int]] = None
#     ) -> List[ce.OWLClassExpression]:
#         visited = visited or set()
#         expr_id = id(expression)
#         if expr_id in visited:
#             return []
#         visited.add(expr_id)

#         if isinstance(expression, ce.OWLObjectUnionOf):
#             flattened: List[ce.OWLClassExpression] = []
#             for operand in expression.operands():
#                 flattened.extend(self._flatten_union(operand, visited))
#             return flattened
#         return [expression]

#     # -------------------------------------------------------------------------
#     # Stage 1: Build DSyntG Tree from OWL AST
#     # -------------------------------------------------------------------------
#     def _build_dsynt_tree(self, expr: ce.OWLClassExpression, ctx: LinguisticContext) -> DSyntNode:
#         if isinstance(expr, ce.OWLClass):
#             label = self.get_label(expr)
#             is_human = self.grammar.is_human(label)
#             return DSyntNode(
#                 role=SyntacticRole.SUBJECT,
#                 head_lemma=label,
#                 is_plural=ctx.is_plural,
#                 is_human=is_human,
#                 is_filler=ctx.is_filler,
#             )

#         elif isinstance(expr, ce.OWLObjectIntersectionOf):
#             operands = self._flatten_intersection(expr)
#             atomic_classes: List[ce.OWLClass] = [op for op in operands if isinstance(op, ce.OWLClass)]
#             restrictions: List[ce.OWLClassExpression] = [op for op in operands if not isinstance(op, ce.OWLClass)]

#             if atomic_classes:
#                 primary_label = self.get_label(atomic_classes[0])
#                 is_human = self.grammar.is_human(primary_label)
#                 head_node = DSyntNode(
#                     role=SyntacticRole.SUBJECT,
#                     head_lemma=primary_label,
#                     is_plural=ctx.is_plural,
#                     is_human=is_human,
#                     is_filler=ctx.is_filler,
#                 )
#                 extra_atomic = atomic_classes[1:]
#             else:
#                 head_node = DSyntNode(
#                     role=SyntacticRole.SUBJECT,
#                     head_lemma=Words.EVERYTHING if self.mode == VerbalizerMode.STANDARD else "thing",
#                     is_plural=False,
#                     is_human=False,
#                     is_filler=ctx.is_filler,
#                 )
#                 extra_atomic = []

#             for ac in extra_atomic:
#                 ac_label = self.get_label(ac)
#                 extra_node = DSyntNode(
#                     role=SyntacticRole.RELATIVE_CLAUSE,
#                     head_lemma=ac_label,
#                     is_plural=ctx.is_plural,
#                     is_human=self.grammar.is_human(ac_label),
#                 )
#                 head_node.relative_clauses.append(extra_node)

#             for rest in restrictions:
#                 rel_node = self._build_restriction_node(rest, ctx)
#                 if rel_node:
#                     head_node.relative_clauses.append(rel_node)

#             return head_node

#         elif isinstance(expr, ce.OWLObjectUnionOf):
#             operands = self._flatten_union(expr)
#             coord_node = DSyntNode(
#                 role=SyntacticRole.COORDINATION,
#                 head_lemma="",
#                 coordination_type="OR",
#                 is_plural=ctx.is_plural,
#                 is_filler=ctx.is_filler,
#             )
#             for op in operands:
#                 child_node = self._build_dsynt_tree(op, ctx)
#                 coord_node.coordinated_nodes.append(child_node)
#             return coord_node

#         elif isinstance(expr, ce.OWLObjectComplementOf):
#             operand = expr.get_operand()
#             operand_node = self._build_dsynt_tree(operand, ctx)
#             operand_node.is_negated = True
#             return operand_node

#         # Single Restriction
#         elif isinstance(
#             expr,
#             (
#                 ce.OWLObjectSomeValuesFrom,
#                 ce.OWLObjectHasValue,
#                 ce.OWLObjectAllValuesFrom,
#                 ce.OWLObjectMinCardinality,
#                 ce.OWLObjectMaxCardinality,
#                 ce.OWLObjectExactCardinality,
#             ),
#         ) or (
#             hasattr(ce, "OWLDataSomeValuesFrom")
#             and isinstance(expr, (getattr(ce, "OWLDataSomeValuesFrom"), getattr(ce, "OWLDataHasValue", type(None))))
#         ):
#             rel_node = self._build_restriction_node(expr, ctx)
#             head_node = DSyntNode(
#                 role=SyntacticRole.SUBJECT,
#                 head_lemma=Words.EVERYTHING if self.mode == VerbalizerMode.STANDARD else "thing",
#                 is_plural=False,
#                 is_human=False,
#             )
#             if rel_node:
#                 head_node.relative_clauses.append(rel_node)
#             return head_node

#         # Fallback
#         return DSyntNode(
#             role=SyntacticRole.SUBJECT,
#             head_lemma="thing",
#             is_plural=ctx.is_plural,
#             is_human=False,
#         )

#     def _build_restriction_node(
#         self, rest: ce.OWLClassExpression, ctx: LinguisticContext
#     ) -> Optional[DSyntNode]:
#         # Case A: Object Some Values & Has Value
#         if isinstance(rest, (ce.OWLObjectSomeValuesFrom, ce.OWLObjectHasValue)):
#             prop = self._extract_property(rest)
#             prop_label = self.get_label(prop)
#             frame = self.frame_classifier.classify_property(prop_label, ctx)

#             filler = self._extract_filler_or_value(rest)
#             filler_ctx = LinguisticContext(is_plural=False, is_filler=True)

#             if isinstance(filler, ce.OWLObjectUnionOf):
#                 union_ops = self._flatten_union(filler)
#                 coord_filler = DSyntNode(
#                     role=SyntacticRole.COORDINATION,
#                     head_lemma="",
#                     coordination_type="OR",
#                     is_plural=False,
#                     is_filler=True,
#                 )
#                 for op in union_ops:
#                     coord_filler.coordinated_nodes.append(self._build_dsynt_tree(op, filler_ctx))

#                 rel_node = DSyntNode(
#                     role=SyntacticRole.RELATIVE_CLAUSE,
#                     head_lemma=frame["phrase"],
#                     frame_type=frame["type"],
#                     is_plural=ctx.is_plural,
#                 )
#                 rel_node.relative_clauses.append(coord_filler)
#                 return rel_node

#             elif isinstance(filler, ce.OWLObjectOneOf):
#                 individuals = list(filler.individuals())
#                 nom_nodes = []
#                 for ind in individuals:
#                     ind_label = self.get_label(ind)
#                     clean_ind = ind_label.title() if not ind_label.isupper() else ind_label
#                     nom_nodes.append(
#                         DSyntNode(
#                             role=SyntacticRole.OBJECT,
#                             head_lemma=clean_ind,
#                             is_plural=False,
#                             is_filler=True,
#                         )
#                     )

#                 coord_filler = DSyntNode(
#                     role=SyntacticRole.COORDINATION,
#                     head_lemma="",
#                     coordination_type="OR",
#                     is_plural=False,
#                     is_filler=True,
#                 )
#                 coord_filler.coordinated_nodes = nom_nodes

#                 rel_node = DSyntNode(
#                     role=SyntacticRole.RELATIVE_CLAUSE,
#                     head_lemma=frame["phrase"],
#                     frame_type=frame["type"],
#                     is_plural=ctx.is_plural,
#                 )
#                 rel_node.relative_clauses.append(coord_filler)
#                 return rel_node

#             filler_node = self._build_dsynt_tree(filler, filler_ctx)
#             phrase = frame["phrase"]

#             if frame["type"] == FrameType.VERB_ACTIVE and isinstance(filler, ce.OWLClass):
#                 prop_words = phrase.split()
#                 if len(prop_words) > 1:
#                     filler_singular = self.grammar.singular(self.get_label(filler))
#                     if prop_words[-1].lower() == filler_singular.lower():
#                         phrase = " ".join(prop_words[:-1])

#             rel_node = DSyntNode(
#                 role=SyntacticRole.RELATIVE_CLAUSE,
#                 head_lemma=phrase,
#                 frame_type=frame["type"],
#                 is_plural=ctx.is_plural,
#             )
#             rel_node.relative_clauses.append(filler_node)
#             return rel_node

#         # Case B: Cardinality Restrictions
#         elif isinstance(
#             rest, (ce.OWLObjectMinCardinality, ce.OWLObjectMaxCardinality, ce.OWLObjectExactCardinality)
#         ):
#             card = self._extract_cardinality(rest)
#             card_word = self.grammar.number(card)
#             prop = self._extract_property(rest)
#             prop_label = self.get_label(prop)
#             filler = self._extract_filler_or_value(rest)

#             is_card_plural = (card != 1)
#             plural_head = self.grammar.extract_head_noun_plural(prop_label)
#             if card == 1:
#                 plural_head = self.grammar.singular(plural_head)

#             prefix_str = (
#                 Words.AT_LEAST if isinstance(rest, ce.OWLObjectMinCardinality)
#                 else Words.AT_MOST if isinstance(rest, ce.OWLObjectMaxCardinality)
#                 else Words.EXACTLY
#             )
#             quant_str = f"{prefix_str} {card_word}"

#             filler_ctx = LinguisticContext(is_plural=is_card_plural, is_filler=True)
#             filler_node = self._build_dsynt_tree(filler, filler_ctx)

#             rel_node = DSyntNode(
#                 role=SyntacticRole.RELATIVE_CLAUSE,
#                 head_lemma=plural_head,
#                 quantifier_prefix=quant_str,
#                 is_plural=ctx.is_plural,
#             )
#             rel_node.relative_clauses.append(filler_node)
#             return rel_node

#         # Case C: All Values From
#         elif isinstance(rest, ce.OWLObjectAllValuesFrom):
#             prop = self._extract_property(rest)
#             frame = self.frame_classifier.classify_property(self.get_label(prop), ctx)
#             filler = self._extract_filler_or_value(rest)

#             if isinstance(filler, ce.OWLObjectComplementOf):
#                 inner_operand = filler.get_operand()
#                 if isinstance(inner_operand, ce.OWLClass):
#                     inner_label = self.grammar.plural(self.get_label(inner_operand))
#                     phrase = frame["phrase"]

#                     # Build structured non-X object node
#                     non_filler_node = DSyntNode(
#                         role=SyntacticRole.OBJECT,
#                         head_lemma=f"non-{inner_label}",
#                     )

#                     rel_node = DSyntNode(
#                         role=SyntacticRole.RELATIVE_CLAUSE,
#                         head_lemma=f"only {phrase}" if frame["type"] == FrameType.VERB_ACTIVE else f"only have non-{inner_label} as {phrase}",
#                         frame_type=FrameType.VERB_ACTIVE,
#                         is_plural=ctx.is_plural,
#                     )
#                     rel_node.relative_clauses.append(non_filler_node)
#                     return rel_node

#             filler_ctx = LinguisticContext(is_plural=True, is_filler=True)
#             filler_node = self._build_dsynt_tree(filler, filler_ctx)

#             rel_node = DSyntNode(
#                 role=SyntacticRole.RELATIVE_CLAUSE,
#                 head_lemma=frame["phrase"],
#                 frame_type=frame["type"],
#                 quantifier_prefix="only",
#                 is_plural=ctx.is_plural,
#             )
#             rel_node.relative_clauses.append(filler_node)
#             return rel_node

#         # Case D: Data Properties
#         elif hasattr(ce, "OWLDataSomeValuesFrom") and isinstance(
#             rest, (getattr(ce, "OWLDataSomeValuesFrom"), getattr(ce, "OWLDataHasValue", type(None)))
#         ):
#             prop = self._extract_property(rest)
#             prop_label = self.grammar.clean_iri_fragment(self.get_label(prop))

#             if prop_label.lower().startswith("has ") and len(prop_label.split()) > 1:
#                 clean_prop = " ".join(prop_label.split()[1:])
#             else:
#                 clean_prop = prop_label

#             if hasattr(ce, "OWLDataHasValue") and isinstance(rest, getattr(ce, "OWLDataHasValue")):
#                 val = self._extract_filler_or_value(rest)
#                 val_str = self._verbalize_literal(val)
#                 val_node = DSyntNode(role=SyntacticRole.OBJECT, head_lemma=val_str)
#                 rel_node = DSyntNode(
#                     role=SyntacticRole.RELATIVE_CLAUSE,
#                     head_lemma=clean_prop,
#                     frame_type=FrameType.RNP,
#                     is_plural=ctx.is_plural,
#                 )
#                 rel_node.relative_clauses.append(val_node)
#                 return rel_node
#             else:
#                 filler_node = DSyntNode(role=SyntacticRole.OBJECT, head_lemma=clean_prop)
#                 rel_node = DSyntNode(
#                     role=SyntacticRole.RELATIVE_CLAUSE,
#                     head_lemma="has",
#                     frame_type=FrameType.VERB_ACTIVE,
#                     is_plural=ctx.is_plural,
#                 )
#                 rel_node.relative_clauses.append(filler_node)
#                 return rel_node

#         # Case E: Complement
#         elif isinstance(rest, ce.OWLObjectComplementOf):
#             operand = rest.get_operand()
#             operand_node = self._build_dsynt_tree(operand, ctx)
#             operand_node.is_negated = True
#             return operand_node

#         return None

#     # -------------------------------------------------------------------------
#     # Stage 2: Bi-directional Feature Propagation Engine
#     # -------------------------------------------------------------------------
#     def _propagate_features(self, node: DSyntNode) -> None:
#         for child in node.relative_clauses:
#             child.is_plural = node.is_plural
#             self._propagate_features(child)
#             if child.role == SyntacticRole.RELATIVE_CLAUSE:
#                 for deep_child in child.relative_clauses:
#                     if deep_child.is_human:
#                         node.is_human = True

#         for coord_child in node.coordinated_nodes:
#             coord_child.is_plural = node.is_plural
#             self._propagate_features(coord_child)

#     # -------------------------------------------------------------------------
#     # Stage 3: Surface Text Realization & Oxford Comma Factorization
#     # -------------------------------------------------------------------------
#     def _realize_node(self, node: DSyntNode) -> str:
#         parts: List[str] = []

#         if node.is_negated:
#             if node.role == SyntacticRole.SUBJECT:
#                 singular_head = self.grammar.singular(node.head_lemma)
#                 return f"everything that is not a {singular_head}"
#             else:
#                 node.is_negated = False
#                 rendered_inner = self._realize_node(node)
#                 return f"not {rendered_inner}"

#         if node.role == SyntacticRole.COORDINATION or node.coordination_type:
#             rendered_children = [self._realize_node(child) for child in node.coordinated_nodes]
#             conj_word = node.coordination_type.lower() if node.coordination_type else "or"

#             if len(rendered_children) == 1:
#                 return rendered_children[0]
#             elif len(rendered_children) == 2:
#                 return f"{rendered_children[0]} {conj_word} {rendered_children[1]}"
#             else:
#                 return f"{', '.join(rendered_children[:-1])}, {conj_word} {rendered_children[-1]}"

#         if node.role == SyntacticRole.OBJECT:
#             return node.head_lemma

#         if node.role == SyntacticRole.SUBJECT:
#             if node.head_lemma in (Words.EVERYTHING, "thing"):
#                 parts.append(node.head_lemma)
#             elif node.is_filler:
#                 singular_head = self.grammar.singular(node.head_lemma)
#                 parts.append(self.grammar.with_article(singular_head))
#             elif node.is_plural:
#                 parts.append(self.grammar.plural(node.head_lemma))
#             else:
#                 singular_head = self.grammar.singular(node.head_lemma)
#                 parts.append(self.grammar.with_article(singular_head))

#         if node.relative_clauses:
#             rel_clauses_rendered = []
#             rel_pronoun = "who" if node.is_human else "that"

#             for child in node.relative_clauses:
#                 if child.quantifier_prefix and child.quantifier_prefix != "only":
#                     have_verb = "have" if node.is_plural else "has"
#                     filler_str = self._realize_node(child.relative_clauses[0])
#                     rel_card_pronoun = "who" if child.relative_clauses[0].is_human else "that"
#                     copula_card = "are" if child.relative_clauses[0].is_plural else "is"

#                     if child.relative_clauses[0].role == SyntacticRole.SUBJECT and child.head_lemma == self.grammar.singular(child.relative_clauses[0].head_lemma):
#                         clause_str = f"who {have_verb} {child.quantifier_prefix} {child.head_lemma}" if node.is_human else f"that {have_verb} {child.quantifier_prefix} {child.head_lemma}"
#                     else:
#                         clause_str = f"who {have_verb} {child.quantifier_prefix} {child.head_lemma} {rel_card_pronoun} {copula_card} {filler_str}"

#                 elif child.quantifier_prefix == "only":
#                     if child.frame_type == FrameType.VERB_ACTIVE:
#                         clause_str = f"that {child.head_lemma}"
#                     else:
#                         clause_str = f"that only has {self._realize_node(child.relative_clauses[0])} as {child.head_lemma}"

#                 elif child.frame_type == FrameType.RNP:
#                     clause_str = f"whose {child.head_lemma} is {self._realize_node(child.relative_clauses[0])}"

#                 elif child.frame_type == FrameType.PASSIVE_PP:
#                     copula = "are" if node.is_plural else "is"
#                     clause_str = f"{rel_pronoun} {copula} {child.head_lemma} {self._realize_node(child.relative_clauses[0])}"

#                 elif child.frame_type == FrameType.VERB_ACTIVE:
#                     if child.relative_clauses:
#                         clause_str = f"{rel_pronoun} {child.head_lemma} {self._realize_node(child.relative_clauses[0])}"
#                     else:
#                         clause_str = f"{rel_pronoun} {child.head_lemma}"

#                 else:
#                     copula = "are" if node.is_plural else "is"
#                     rendered_child = self._realize_node(child)
#                     clause_str = f"{rel_pronoun} {copula} {rendered_child}"

#                 rel_clauses_rendered.append(clause_str)

#             if len(rel_clauses_rendered) == 1:
#                 parts.append(rel_clauses_rendered[0])
#             elif len(rel_clauses_rendered) == 2:
#                 parts.append(f"{rel_clauses_rendered[0]} and {rel_clauses_rendered[1]}")
#             else:
#                 parts.append(f"{', '.join(rel_clauses_rendered[:-1])}, and {rel_clauses_rendered[-1]}")

#         return " ".join(parts).strip()

#     # -------------------------------------------------------------------------
#     # Public Entry Point
#     # -------------------------------------------------------------------------
#     def convert(
#         self,
#         item: ce.OWLClassExpression,
#         is_filler: bool = False,
#         context: Optional[LinguisticContext] = None,
#     ) -> str:
#         ctx = context or LinguisticContext(is_plural=not is_filler, is_filler=is_filler)

#         # 1. Construct Intermediate Representation
#         tree = self._build_dsynt_tree(item, ctx)
#         # 2. Propagate Morpho-Syntactic Features
#         self._propagate_features(tree)
#         # 3. Linearize Surface English Text
#         return self._realize_node(tree)






"""
SADDG V2 Class Expression Converter.
Implements a 3-Stage Micro-Planning Pipeline (AST -> DSyntG Tree -> Feature Propagation -> Surface Text)
using Deep Syntactic Graphs (DSyntG) and dynamic property frame classification.
"""

from typing import Any, List, Optional, Set

# Safe OWLAPY imports avoiding circular dependency triggers
import owlapy.class_expression as ce

from verbalizer.common.base import VerbalizerMode
from verbalizer.common.grammar import EnglishGrammar, LinguisticContext, Words
from verbalizer.owl2nl.converters.base import BaseClassExpressionConverter
from verbalizer.owl2nl.converters.dsyntg import DSyntNode, FrameType, SyntacticRole
from verbalizer.owl2nl.converters.frame_classifier import PropertyFrameClassifier


class SADDGGraphConverterV2(BaseClassExpressionConverter):
    """
    Syntax-Aware Dynamic Dependency Graph (SADDG) V2 Verbalizer Engine.
    Decouples Description Logic AST parsing from surface English realization via DSyntG trees.
    """

    def __init__(
        self,
        ontology_input: Any | None = None,
        grammar: EnglishGrammar | None = None,
        mode: VerbalizerMode = VerbalizerMode.STANDARD,
    ):
        super().__init__(ontology_input=ontology_input, grammar=grammar, mode=mode)
        self.frame_classifier = PropertyFrameClassifier(self.grammar)

    def _extract_property(self, rest: Any) -> Any:
        if hasattr(rest, "get_property"): return rest.get_property()
        if hasattr(rest, "property"): return rest.property
        raise AttributeError(f"Unable to extract property from {type(rest)}")

    def _extract_filler_or_value(self, rest: Any) -> Any:
        if hasattr(rest, "get_filler"): return rest.get_filler()
        if hasattr(rest, "get_value"): return rest.get_value()
        if hasattr(rest, "filler"): return rest.filler
        if hasattr(rest, "value"): return rest.value
        raise AttributeError(f"Unable to extract filler/value from {type(rest)}")

    def _extract_cardinality(self, rest: Any) -> int:
        if hasattr(rest, "get_cardinality"): return rest.get_cardinality()
        if hasattr(rest, "cardinality"): return rest.cardinality
        raise AttributeError(f"Unable to extract cardinality from {type(rest)}")

    def _verbalize_literal(self, val: Any) -> str:
        if hasattr(val, "get_literal"): return str(val.get_literal())
        if hasattr(val, "literal"): return str(val.literal)
        return str(val)

    def _flatten_intersection(self, expression: ce.OWLClassExpression, visited: Optional[Set[int]] = None) -> List[ce.OWLClassExpression]:
        visited = visited or set()
        if id(expression) in visited: return []
        visited.add(id(expression))
        if isinstance(expression, ce.OWLObjectIntersectionOf):
            flattened = []
            for operand in expression.operands():
                flattened.extend(self._flatten_intersection(operand, visited))
            return flattened
        return [expression]

    def _flatten_union(self, expression: ce.OWLClassExpression, visited: Optional[Set[int]] = None) -> List[ce.OWLClassExpression]:
        visited = visited or set()
        if id(expression) in visited: return []
        visited.add(id(expression))
        if isinstance(expression, ce.OWLObjectUnionOf):
            flattened = []
            for operand in expression.operands():
                flattened.extend(self._flatten_union(operand, visited))
            return flattened
        return [expression]

    def _build_dsynt_tree(self, expr: Any, ctx: LinguisticContext) -> DSyntNode:
        # BUGFIX 1: Explicitly catch and extract Named Individuals (e.g., PhD, male)
        if hasattr(expr, "is_anonymous") and not expr.is_anonymous() and not isinstance(expr, ce.OWLClass):
            label = self.get_label(expr)
            clean_label = label.title() if not label.isupper() else label
            return DSyntNode(role=SyntacticRole.OBJECT, head_lemma=clean_label, is_plural=False, is_filler=True)

        # BUGFIX 2: Explicitly catch Literals
        if hasattr(expr, "get_literal"):
            return DSyntNode(role=SyntacticRole.OBJECT, head_lemma=str(expr.get_literal()), is_plural=False, is_filler=True)

        if isinstance(expr, ce.OWLClass):
            label = self.get_label(expr)
            if label.lower() == "thing" or expr.iri.as_str().endswith("Thing"):
                return DSyntNode(role=SyntacticRole.SUBJECT, head_lemma="thing", is_plural=ctx.is_plural, is_human=False, is_filler=ctx.is_filler)
            is_human = self.grammar.is_human(label)
            return DSyntNode(role=SyntacticRole.SUBJECT, head_lemma=label, is_plural=ctx.is_plural, is_human=is_human, is_filler=ctx.is_filler)

        elif isinstance(expr, ce.OWLObjectIntersectionOf):
            operands = self._flatten_intersection(expr)
            atomic_classes = [op for op in operands if isinstance(op, ce.OWLClass)]
            restrictions = [op for op in operands if not isinstance(op, ce.OWLClass)]

            if atomic_classes:
                primary_label = self.get_label(atomic_classes[0])
                is_human = self.grammar.is_human(primary_label)
                head_node = DSyntNode(role=SyntacticRole.SUBJECT, head_lemma=primary_label, is_plural=ctx.is_plural, is_human=is_human, is_filler=ctx.is_filler)
                extra_atomic = atomic_classes[1:]
            else:
                head_node = DSyntNode(role=SyntacticRole.SUBJECT, head_lemma=Words.EVERYTHING if self.mode == VerbalizerMode.STANDARD else "thing", is_plural=False, is_human=False, is_filler=ctx.is_filler)
                extra_atomic = []

            for ac in extra_atomic:
                ac_label = self.get_label(ac)
                extra_node = DSyntNode(role=SyntacticRole.RELATIVE_CLAUSE, head_lemma=ac_label, is_plural=ctx.is_plural, is_human=self.grammar.is_human(ac_label))
                head_node.relative_clauses.append(extra_node)

            for rest in restrictions:
                rel_node = self._build_restriction_node(rest, ctx)
                if rel_node: head_node.relative_clauses.append(rel_node)
            return head_node

        elif isinstance(expr, ce.OWLObjectUnionOf):
            operands = self._flatten_union(expr)
            coord_node = DSyntNode(role=SyntacticRole.COORDINATION, head_lemma="", coordination_type="OR", is_plural=ctx.is_plural, is_filler=ctx.is_filler)
            for op in operands:
                coord_node.coordinated_nodes.append(self._build_dsynt_tree(op, ctx))
            return coord_node

        elif isinstance(expr, ce.OWLObjectComplementOf):
            operand = expr.get_operand()
            operand_node = self._build_dsynt_tree(operand, ctx)
            operand_node.is_negated = True
            return operand_node

        elif isinstance(expr, (ce.OWLObjectSomeValuesFrom, ce.OWLObjectHasValue, ce.OWLObjectAllValuesFrom, ce.OWLObjectMinCardinality, ce.OWLObjectMaxCardinality, ce.OWLObjectExactCardinality)) or (hasattr(ce, "OWLDataSomeValuesFrom") and isinstance(expr, (getattr(ce, "OWLDataSomeValuesFrom"), getattr(ce, "OWLDataHasValue", type(None))))):
            rel_node = self._build_restriction_node(expr, ctx)
            head_node = DSyntNode(role=SyntacticRole.SUBJECT, head_lemma=Words.EVERYTHING if self.mode == VerbalizerMode.STANDARD else "thing", is_plural=False, is_human=False)
            if rel_node: head_node.relative_clauses.append(rel_node)
            return head_node

        return DSyntNode(role=SyntacticRole.SUBJECT, head_lemma="thing", is_plural=ctx.is_plural, is_human=False)

    def _build_restriction_node(self, rest: Any, ctx: LinguisticContext) -> Optional[DSyntNode]:
        if isinstance(rest, (ce.OWLObjectSomeValuesFrom, ce.OWLObjectHasValue)):
            prop = self._extract_property(rest)
            prop_label = self.get_label(prop)
            frame = self.frame_classifier.classify_property(prop_label, ctx)
            filler = self._extract_filler_or_value(rest)
            filler_ctx = LinguisticContext(is_plural=False, is_filler=True)

            if isinstance(filler, ce.OWLObjectUnionOf):
                union_ops = self._flatten_union(filler)
                coord_filler = DSyntNode(role=SyntacticRole.COORDINATION, head_lemma="", coordination_type="OR", is_plural=False, is_filler=True)
                for op in union_ops: coord_filler.coordinated_nodes.append(self._build_dsynt_tree(op, filler_ctx))
                rel_node = DSyntNode(role=SyntacticRole.RELATIVE_CLAUSE, head_lemma=frame["phrase"], frame_type=frame["type"], is_plural=ctx.is_plural)
                rel_node.relative_clauses.append(coord_filler)
                return rel_node

            elif isinstance(filler, ce.OWLObjectOneOf):
                individuals = list(filler.individuals())
                nom_nodes = []
                for ind in individuals:
                    ind_label = self.get_label(ind)
                    clean_ind = ind_label.title() if not ind_label.isupper() else ind_label
                    nom_nodes.append(DSyntNode(role=SyntacticRole.OBJECT, head_lemma=clean_ind, is_plural=False, is_filler=True))
                coord_filler = DSyntNode(role=SyntacticRole.COORDINATION, head_lemma="", coordination_type="OR", is_plural=False, is_filler=True)
                coord_filler.coordinated_nodes = nom_nodes
                rel_node = DSyntNode(role=SyntacticRole.RELATIVE_CLAUSE, head_lemma=frame["phrase"], frame_type=frame["type"], is_plural=ctx.is_plural)
                rel_node.relative_clauses.append(coord_filler)
                return rel_node

            filler_node = self._build_dsynt_tree(filler, filler_ctx)
            phrase = frame["phrase"]

            if frame["type"] == FrameType.VERB_ACTIVE and isinstance(filler, ce.OWLClass):
                prop_words = phrase.split()
                if len(prop_words) > 1:
                    filler_singular = self.grammar.singular(self.get_label(filler))
                    if prop_words[-1].lower() == filler_singular.lower():
                        phrase = " ".join(prop_words[:-1])

            rel_node = DSyntNode(role=SyntacticRole.RELATIVE_CLAUSE, head_lemma=phrase, frame_type=frame["type"], is_plural=ctx.is_plural)
            rel_node.relative_clauses.append(filler_node)
            return rel_node

        elif isinstance(rest, (ce.OWLObjectMinCardinality, ce.OWLObjectMaxCardinality, ce.OWLObjectExactCardinality)):
            card = self._extract_cardinality(rest)
            card_word = self.grammar.number(card)
            prop = self._extract_property(rest)
            prop_label = self.get_label(prop)
            filler = self._extract_filler_or_value(rest)
            is_card_plural = (card != 1)
            
            # BUGFIX 3: Prevent double pluralization ("childrens")
            head_noun = self.grammar.extract_property_head_noun(prop_label)
            if card == 1:
                target_noun = self.grammar.singular(head_noun)
            else:
                target_noun = self.grammar.plural(head_noun) if head_noun.lower() != "children" else "children"

            prefix_str = Words.AT_LEAST if isinstance(rest, ce.OWLObjectMinCardinality) else Words.AT_MOST if isinstance(rest, ce.OWLObjectMaxCardinality) else Words.EXACTLY
            quant_str = f"{prefix_str} {card_word}"

            filler_ctx = LinguisticContext(is_plural=is_card_plural, is_filler=True)
            filler_node = self._build_dsynt_tree(filler, filler_ctx)

            rel_node = DSyntNode(role=SyntacticRole.RELATIVE_CLAUSE, head_lemma=target_noun, quantifier_prefix=quant_str, is_plural=ctx.is_plural)
            rel_node.relative_clauses.append(filler_node)
            return rel_node

        elif isinstance(rest, ce.OWLObjectAllValuesFrom):
            prop = self._extract_property(rest)
            frame = self.frame_classifier.classify_property(self.get_label(prop), ctx)
            filler = self._extract_filler_or_value(rest)

            if isinstance(filler, ce.OWLObjectComplementOf):
                inner_operand = filler.get_operand()
                if isinstance(inner_operand, ce.OWLClass):
                    inner_label = self.grammar.plural(self.get_label(inner_operand))
                    phrase = frame["phrase"]
                    non_filler_node = DSyntNode(role=SyntacticRole.OBJECT, head_lemma=f"non-{inner_label}")
                    rel_node = DSyntNode(role=SyntacticRole.RELATIVE_CLAUSE, head_lemma=f"only {phrase}" if frame["type"] == FrameType.VERB_ACTIVE else f"only have non-{inner_label} as {phrase}", frame_type=FrameType.VERB_ACTIVE, is_plural=ctx.is_plural)
                    rel_node.relative_clauses.append(non_filler_node)
                    return rel_node

            filler_ctx = LinguisticContext(is_plural=True, is_filler=True)
            filler_node = self._build_dsynt_tree(filler, filler_ctx)
            rel_node = DSyntNode(role=SyntacticRole.RELATIVE_CLAUSE, head_lemma=frame["phrase"], frame_type=frame["type"], quantifier_prefix="only", is_plural=ctx.is_plural)
            rel_node.relative_clauses.append(filler_node)
            return rel_node

        elif hasattr(ce, "OWLDataSomeValuesFrom") and isinstance(rest, (getattr(ce, "OWLDataSomeValuesFrom"), getattr(ce, "OWLDataHasValue", type(None)))):
            prop = self._extract_property(rest)
            prop_label = self.grammar.clean_iri_fragment(self.get_label(prop))
            clean_prop = " ".join(prop_label.split()[1:]) if prop_label.lower().startswith("has ") and len(prop_label.split()) > 1 else prop_label

            if hasattr(ce, "OWLDataHasValue") and isinstance(rest, getattr(ce, "OWLDataHasValue")):
                val = self._extract_filler_or_value(rest)
                val_str = self._verbalize_literal(val)
                
                # BUGFIX 4: Handle boolean values elegantly instead of printing "is false"
                if val_str.lower() in ("true", "false"):
                    is_true = val_str.lower() == "true"
                    prefix = "whose is" if clean_prop.startswith("is") else "that has a"
                    if not is_true: prefix = "whose is not" if clean_prop.startswith("is") else "that does not have a"
                    clean_prop = clean_prop[3:] if clean_prop.startswith("is ") else clean_prop
                    
                    return DSyntNode(role=SyntacticRole.RELATIVE_CLAUSE, head_lemma=f"{prefix} {clean_prop}".strip(), frame_type="BOOLEAN", is_plural=ctx.is_plural)

                val_node = DSyntNode(role=SyntacticRole.OBJECT, head_lemma=val_str)
                rel_node = DSyntNode(role=SyntacticRole.RELATIVE_CLAUSE, head_lemma=clean_prop, frame_type=FrameType.RNP, is_plural=ctx.is_plural)
                rel_node.relative_clauses.append(val_node)
                return rel_node
            else:
                filler_node = DSyntNode(role=SyntacticRole.OBJECT, head_lemma=clean_prop)
                rel_node = DSyntNode(role=SyntacticRole.RELATIVE_CLAUSE, head_lemma="has", frame_type=FrameType.VERB_ACTIVE, is_plural=ctx.is_plural)
                rel_node.relative_clauses.append(filler_node)
                return rel_node

        elif isinstance(rest, ce.OWLObjectComplementOf):
            operand = rest.get_operand()
            operand_node = self._build_dsynt_tree(operand, ctx)
            operand_node.is_negated = True
            return operand_node

        return None

    def _propagate_features(self, node: DSyntNode) -> None:
        for child in node.relative_clauses:
            child.is_plural = node.is_plural
            self._propagate_features(child)
            if child.role == SyntacticRole.RELATIVE_CLAUSE:
                for deep_child in child.relative_clauses:
                    if deep_child.is_human: node.is_human = True
        for coord_child in node.coordinated_nodes:
            coord_child.is_plural = node.is_plural
            self._propagate_features(coord_child)

    def _realize_node(self, node: DSyntNode) -> str:
        parts: List[str] = []

        if node.is_negated:
            if node.role == SyntacticRole.SUBJECT:
                singular_head = self.grammar.singular(node.head_lemma)
                return f"everything that is not a {singular_head}"
            else:
                node.is_negated = False
                return f"not {self._realize_node(node)}"

        if node.role == SyntacticRole.COORDINATION or node.coordination_type:
            rendered_children = [self._realize_node(child) for child in node.coordinated_nodes]
            conj_word = node.coordination_type.lower() if node.coordination_type else "or"
            if len(rendered_children) == 1: return rendered_children[0]
            elif len(rendered_children) == 2: return f"{rendered_children[0]} {conj_word} {rendered_children[1]}"
            else: return f"{', '.join(rendered_children[:-1])}, {conj_word} {rendered_children[-1]}"

        if node.role == SyntacticRole.OBJECT:
            return node.head_lemma

        if node.role == SyntacticRole.SUBJECT:
            if node.head_lemma in (Words.EVERYTHING, "thing"):
                parts.append(node.head_lemma)
            elif node.is_filler:
                singular_head = self.grammar.singular(node.head_lemma)
                parts.append(self.grammar.with_article(singular_head))
            elif node.is_plural:
                parts.append(self.grammar.plural(node.head_lemma))
            else:
                singular_head = self.grammar.singular(node.head_lemma)
                parts.append(self.grammar.with_article(singular_head))

        if node.relative_clauses:
            rel_clauses_rendered = []
            rel_pronoun = "who" if node.is_human else "that"

            for child in node.relative_clauses:
                if getattr(child, "frame_type", None) == "BOOLEAN":
                    clause_str = child.head_lemma

                elif child.quantifier_prefix and child.quantifier_prefix != "only":
                    have_verb = "have" if node.is_plural else "has"
                    # BUGFIX 5: Safely drop "that is thing" suffix if the filler is implicit
                    if child.relative_clauses and child.relative_clauses[0].head_lemma != "thing":
                        filler_str = self._realize_node(child.relative_clauses[0])
                        rel_card_pronoun = "who" if child.relative_clauses[0].is_human else "that"
                        copula_card = "are" if child.relative_clauses[0].is_plural else "is"
                        clause_str = f"who {have_verb} {child.quantifier_prefix} {child.head_lemma} {rel_card_pronoun} {copula_card} {filler_str}"
                    else:
                        clause_str = f"who {have_verb} {child.quantifier_prefix} {child.head_lemma}" if node.is_human else f"that {have_verb} {child.quantifier_prefix} {child.head_lemma}"

                elif child.quantifier_prefix == "only":
                    if child.frame_type == FrameType.VERB_ACTIVE:
                        clause_str = f"that {child.head_lemma}"
                    else:
                        clause_str = f"that only has {self._realize_node(child.relative_clauses[0])} as {child.head_lemma}"

                elif child.frame_type == FrameType.RNP:
                    if child.relative_clauses and child.relative_clauses[0].head_lemma != "thing":
                        clause_str = f"whose {child.head_lemma} is {self._realize_node(child.relative_clauses[0])}"
                    else:
                        clause_str = f"whose {child.head_lemma}"

                elif child.frame_type == FrameType.PASSIVE_PP:
                    copula = "are" if node.is_plural else "is"
                    clause_str = f"{rel_pronoun} {copula} {child.head_lemma} {self._realize_node(child.relative_clauses[0])}"

                elif child.frame_type == FrameType.VERB_ACTIVE:
                    if child.relative_clauses and child.relative_clauses[0].head_lemma != "thing":
                        clause_str = f"{rel_pronoun} {child.head_lemma} {self._realize_node(child.relative_clauses[0])}"
                    else:
                        clause_str = f"{rel_pronoun} {child.head_lemma}"

                else:
                    copula = "are" if node.is_plural else "is"
                    rendered_child = self._realize_node(child)
                    clause_str = f"{rel_pronoun} {copula} {rendered_child}"

                rel_clauses_rendered.append(clause_str)

            if len(rel_clauses_rendered) == 1: parts.append(rel_clauses_rendered[0])
            elif len(rel_clauses_rendered) == 2: parts.append(f"{rel_clauses_rendered[0]} and {rel_clauses_rendered[1]}")
            else: parts.append(f"{', '.join(rel_clauses_rendered[:-1])}, and {rel_clauses_rendered[-1]}")

        return " ".join(parts).strip()

    def convert(self, item: ce.OWLClassExpression, is_filler: bool = False, context: Optional[LinguisticContext] = None) -> str:
        ctx = context or LinguisticContext(is_plural=not is_filler, is_filler=is_filler)
        tree = self._build_dsynt_tree(item, ctx)
        self._propagate_features(tree)
        return self._realize_node(tree)