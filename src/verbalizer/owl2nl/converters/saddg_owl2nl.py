# """
# Semantic Abstract Dependency Directed Graph (SADDG) V2 - OWL2NL Engine.
# """

# from dataclasses import dataclass, field
# from enum import Enum, auto
# from typing import List, Optional, Any

# from owlapy.class_expression import (
#     OWLClass,
#     OWLClassExpression,
#     OWLObjectSomeValuesFrom,
#     OWLObjectAllValuesFrom,
#     OWLObjectHasValue,
#     OWLObjectMinCardinality,
#     OWLObjectMaxCardinality,
#     OWLObjectExactCardinality,
#     OWLObjectIntersectionOf,
#     OWLObjectUnionOf,
#     OWLObjectOneOf,
#     OWLDataHasValue,
# )

# from verbalizer.common.grammar_owl2nl import OWL2NLGrammar, LinguisticContext


# class SADDGNodeType(Enum):
#     ROOT_NOUN = auto()
#     EXISTENTIAL_RELATION = auto()
#     UNIVERSAL_RELATION = auto()
#     CARDINALITY_RELATION = auto()
#     NOMINAL_VALUE = auto()
#     DATA_VALUE = auto()
#     CONJUNCTION = auto()
#     DISJUNCTION = auto()


# @dataclass
# class SADDGNode:
#     node_type: SADDGNodeType
#     label: str = ""
#     quantifier: Optional[str] = None
#     children: List["SADDGNode"] = field(default_factory=list)
#     raw_owl: Optional[Any] = None


# class SADDGGraphConverterOWL2NL:
#     """
#     SADDG V2 Graph Converter Engine for OWL2NL.
#     """

#     def __init__(self):
#         self.grammar = OWL2NLGrammar()

#     def convert(self, expr: OWLClassExpression) -> str:
#         """Main entry point: converts OWLClassExpression to natural language."""
#         if not expr:
#             return "everything"

#         # Step 1: Forward Graph Construction
#         graph_root = self._build_graph(expr)

#         # Step 2: Backward Linearization Traversal
#         context = LinguisticContext(is_plural=True)
#         return self._linearize_graph(graph_root, context)

#     def _build_graph(self, expr: OWLClassExpression) -> SADDGNode:
#         """Forward construction of SADDG graph from DL expression."""

#         # 1. Atomic Named Class
#         if isinstance(expr, OWLClass):
#             clean_class = self.grammar.clean_name(expr)
#             if self.grammar.is_owl_thing(expr) or self.grammar.is_owl_thing(clean_class):
#                 label = "everything"
#             else:
#                 label = self.grammar.plural(clean_class) if clean_class.lower() != "children" else "children"
#             return SADDGNode(node_type=SADDGNodeType.ROOT_NOUN, label=label, raw_owl=expr)

#         # 2. Intersection (Conjunction)
#         if isinstance(expr, OWLObjectIntersectionOf):
#             node = SADDGNode(node_type=SADDGNodeType.CONJUNCTION, raw_owl=expr)
#             for child in expr.operands():
#                 node.children.append(self._build_graph(child))
#             return node

#         # 3. Union (Disjunction)
#         if isinstance(expr, OWLObjectUnionOf):
#             node = SADDGNode(node_type=SADDGNodeType.DISJUNCTION, raw_owl=expr)
#             for child in expr.operands():
#                 node.children.append(self._build_graph(child))
#             return node

#         # 4. Nominal HasValue (OWLObjectHasValue)
#         if isinstance(expr, OWLObjectHasValue):
#             prop_clean = self.grammar.clean_property_name(expr.get_property())
#             ind_label = self.grammar.format_individual_name(expr.get_filler())
#             return SADDGNode(
#                 node_type=SADDGNodeType.NOMINAL_VALUE,
#                 label=prop_clean,
#                 quantifier=ind_label,
#                 raw_owl=expr
#             )

#         # 5. Data HasValue (OWLDataHasValue)
#         if isinstance(expr, OWLDataHasValue):
#             prop_clean = self.grammar.clean_property_name(expr.get_property())
#             val_literal = expr.get_filler().value
#             return SADDGNode(
#                 node_type=SADDGNodeType.DATA_VALUE,
#                 label=prop_clean,
#                 quantifier=str(val_literal),
#                 raw_owl=expr
#             )

#         # 6. Existential Restriction (SomeValuesFrom)
#         if isinstance(expr, OWLObjectSomeValuesFrom):
#             prop_clean = self.grammar.clean_property_name(expr.get_property())
#             filler = expr.get_filler()

#             # Check for nominal set inside existential (e.g. OneOf({BA, BS}))
#             if isinstance(filler, OWLObjectOneOf):
#                 nominals = [self.grammar.format_individual_name(ind) for ind in filler.individuals()]
#                 nom_str = " or ".join(sorted(nominals))
#                 return SADDGNode(
#                     node_type=SADDGNodeType.EXISTENTIAL_RELATION,
#                     label=prop_clean,
#                     quantifier=nom_str,
#                     raw_owl=expr
#                 )

#             child_node = self._build_graph(filler)
#             node = SADDGNode(node_type=SADDGNodeType.EXISTENTIAL_RELATION, label=prop_clean, raw_owl=expr)
#             node.children.append(child_node)
#             return node

#         # 7. Universal Restriction (AllValuesFrom)
#         if isinstance(expr, OWLObjectAllValuesFrom):
#             prop_clean = self.grammar.clean_property_name(expr.get_property())
#             child_node = self._build_graph(expr.get_filler())
#             node = SADDGNode(node_type=SADDGNodeType.UNIVERSAL_RELATION, label=prop_clean, raw_owl=expr)
#             node.children.append(child_node)
#             return node

#         # 8. Cardinality Restrictions
#         if isinstance(expr, (OWLObjectExactCardinality, OWLObjectMinCardinality, OWLObjectMaxCardinality)):
#             head_noun = self.grammar.extract_property_head_noun(expr.get_property())
#             card = expr.get_cardinality()
#             card_str = self.grammar.number(card)

#             if isinstance(expr, OWLObjectExactCardinality):
#                 quant = f"exactly {card_str}"
#             elif isinstance(expr, OWLObjectMinCardinality):
#                 quant = f"at least {card_str}"
#             else:
#                 quant = f"at most {card_str}"

#             node = SADDGNode(
#                 node_type=SADDGNodeType.CARDINALITY_RELATION,
#                 label=head_noun,
#                 quantifier=quant,
#                 raw_owl=expr
#             )

#             filler = expr.get_filler()
#             # Suppress owl:Thing fillers in cardinalities
#             if not self.grammar.is_owl_thing(filler):
#                 node.children.append(self._build_graph(filler))

#             return node

#         # Default fallback
#         fallback = self.grammar.clean_name(expr)
#         return SADDGNode(node_type=SADDGNodeType.ROOT_NOUN, label=fallback)

#     def _linearize_graph(self, node: SADDGNode, context: LinguisticContext) -> str:
#         """Backward graph linearization traversal."""

#         if node.node_type == SADDGNodeType.ROOT_NOUN:
#             return node.label

#         if node.node_type == SADDGNodeType.DATA_VALUE:
#             formatted = self.grammar.format_data_value(node.label, node.quantifier)
#             return f"whose {formatted}" if "is" in formatted else f"that {formatted}"

#         if node.node_type == SADDGNodeType.NOMINAL_VALUE:
#             return f"whose {node.label} is {node.quantifier}"

#         if node.node_type == SADDGNodeType.CONJUNCTION:
#             head_nodes = [c for c in node.children if c.node_type == SADDGNodeType.ROOT_NOUN]
#             clause_nodes = [c for c in node.children if c.node_type != SADDGNodeType.ROOT_NOUN]

#             head_str = " ".join([self._linearize_graph(h, context) for h in head_nodes]) if head_nodes else "everything"
#             context.is_human = self.grammar.is_human(head_str)
#             rel_pronoun = context.relative_pronoun()

#             clauses = [self._linearize_graph(c, context) for c in clause_nodes]

#             if not clauses:
#                 return head_str

#             formatted_clauses = []
#             for cl in clauses:
#                 if cl.startswith("whose") or cl.startswith("that") or cl.startswith("who"):
#                     formatted_clauses.append(cl)
#                 else:
#                     formatted_clauses.append(f"{rel_pronoun} {cl}")

#             return f"{head_str} {' and '.join(formatted_clauses)}"

#         if node.node_type == SADDGNodeType.EXISTENTIAL_RELATION:
#             if node.quantifier:
#                 return f"whose {node.label} is {node.quantifier}"

#             if node.children:
#                 child_str = self._linearize_graph(node.children[0], context)
#                 sing_child = self.grammar.singular(child_str)
#                 with_art = self.grammar.with_article(sing_child)
#                 return f"whose {node.label} is {with_art}"

#             return f"has {node.label}"

#         if node.node_type == SADDGNodeType.UNIVERSAL_RELATION:
#             head_noun = self.grammar.extract_property_head_noun(node.label)
#             if node.children:
#                 child_str = self._linearize_graph(node.children[0], context)
#                 sing_child = self.grammar.singular(child_str)
#                 return f"only has {sing_child} as {head_noun}"
#             return f"only has {head_noun}"

#         if node.node_type == SADDGNodeType.CARDINALITY_RELATION:
#             plural_noun = node.label
#             if node.quantifier and "one" in node.quantifier:
#                 plural_noun = self.grammar.singular(node.label)

#             if not node.children:
#                 return f"has {node.quantifier} {plural_noun}"

#             child_str = self._linearize_graph(node.children[0], context)
#             return f"has {node.quantifier} {plural_noun} that are {child_str}"

#         return node.label



"""
Semantic Abstract Dependency Directed Graph (SADDG) V2 - OWL2NL Engine.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Optional, Any

from owlapy.class_expression import (
    OWLClass,
    OWLClassExpression,
    OWLObjectSomeValuesFrom,
    OWLObjectAllValuesFrom,
    OWLObjectHasValue,
    OWLObjectMinCardinality,
    OWLObjectMaxCardinality,
    OWLObjectExactCardinality,
    OWLObjectIntersectionOf,
    OWLObjectUnionOf,
    OWLObjectOneOf,
    OWLDataHasValue,
)

from verbalizer.common.grammar_owl2nl import OWL2NLGrammar, LinguisticContext


class SADDGNodeType(Enum):
    ROOT_NOUN = auto()
    EXISTENTIAL_RELATION = auto()
    UNIVERSAL_RELATION = auto()
    CARDINALITY_RELATION = auto()
    NOMINAL_VALUE = auto()
    DATA_VALUE = auto()
    CONJUNCTION = auto()
    DISJUNCTION = auto()


@dataclass
class SADDGNode:
    node_type: SADDGNodeType
    label: str = ""
    quantifier: Optional[str] = None
    children: List["SADDGNode"] = field(default_factory=list)
    raw_owl: Optional[Any] = None


class SADDGGraphConverterOWL2NL:
    """
    SADDG V2 Graph Converter Engine for OWL2NL.
    """

    def __init__(self):
        self.grammar = OWL2NLGrammar()

    def convert(self, expr: OWLClassExpression) -> str:
        """Main entry point: converts OWLClassExpression to natural language."""
        if not expr:
            return "everything"

        # Step 1: Forward Graph Construction
        graph_root = self._build_graph(expr)

        # Step 2: Backward Linearization Traversal
        context = LinguisticContext(is_plural=True)
        return self._linearize_graph(graph_root, context)

    def _build_graph(self, expr: OWLClassExpression) -> SADDGNode:
        """Forward construction of SADDG graph from DL expression."""

        # 1. Atomic Named Class
        if isinstance(expr, OWLClass):
            clean_class = self.grammar.clean_name(expr)
            if self.grammar.is_owl_thing(expr) or self.grammar.is_owl_thing(clean_class):
                label = "everything"
            else:
                label = self.grammar.plural(clean_class) if clean_class.lower() != "children" else "children"
            return SADDGNode(node_type=SADDGNodeType.ROOT_NOUN, label=label, raw_owl=expr)

        # 2. Intersection (Conjunction)
        if isinstance(expr, OWLObjectIntersectionOf):
            node = SADDGNode(node_type=SADDGNodeType.CONJUNCTION, raw_owl=expr)
            for child in expr.operands():
                node.children.append(self._build_graph(child))
            return node

        # 3. Union (Disjunction)
        if isinstance(expr, OWLObjectUnionOf):
            node = SADDGNode(node_type=SADDGNodeType.DISJUNCTION, raw_owl=expr)
            for child in expr.operands():
                node.children.append(self._build_graph(child))
            return node

        # 4. Nominal HasValue (OWLObjectHasValue)
        if isinstance(expr, OWLObjectHasValue):
            prop_clean = self.grammar.clean_property_name(expr.get_property())
            ind_label = self.grammar.format_individual_name(expr.get_filler())
            return SADDGNode(
                node_type=SADDGNodeType.NOMINAL_VALUE,
                label=prop_clean,
                quantifier=ind_label,
                raw_owl=expr
            )

        # 5. Data HasValue (OWLDataHasValue - Robust Boolean & Literal Handling)
        if isinstance(expr, OWLDataHasValue):
            prop_clean = self.grammar.clean_property_name(expr.get_property())
            filler = expr.get_filler()

            # Robust extraction across owlapy OWLLiteral types
            if hasattr(filler, "get_literal"):
                val_literal = str(filler.get_literal())
            elif hasattr(filler, "to_python"):
                val_literal = str(filler.to_python())
            elif hasattr(filler, "value"):
                val_literal = str(filler.value)
            else:
                val_literal = str(filler)

            return SADDGNode(
                node_type=SADDGNodeType.DATA_VALUE,
                label=prop_clean,
                quantifier=val_literal,
                raw_owl=expr
            )

        # 6. Existential Restriction (SomeValuesFrom)
        if isinstance(expr, OWLObjectSomeValuesFrom):
            prop_clean = self.grammar.clean_property_name(expr.get_property())
            filler = expr.get_filler()

            if isinstance(filler, OWLObjectOneOf):
                nominals = [self.grammar.format_individual_name(ind) for ind in filler.individuals()]
                nom_str = " or ".join(sorted(nominals))
                return SADDGNode(
                    node_type=SADDGNodeType.EXISTENTIAL_RELATION,
                    label=prop_clean,
                    quantifier=nom_str,
                    raw_owl=expr
                )

            child_node = self._build_graph(filler)
            node = SADDGNode(node_type=SADDGNodeType.EXISTENTIAL_RELATION, label=prop_clean, raw_owl=expr)
            node.children.append(child_node)
            return node

        # 7. Universal Restriction (AllValuesFrom)
        if isinstance(expr, OWLObjectAllValuesFrom):
            prop_clean = self.grammar.clean_property_name(expr.get_property())
            child_node = self._build_graph(expr.get_filler())
            node = SADDGNode(node_type=SADDGNodeType.UNIVERSAL_RELATION, label=prop_clean, raw_owl=expr)
            node.children.append(child_node)
            return node

        # 8. Cardinality Restrictions
        if isinstance(expr, (OWLObjectExactCardinality, OWLObjectMinCardinality, OWLObjectMaxCardinality)):
            head_noun = self.grammar.extract_property_head_noun(expr.get_property())
            card = expr.get_cardinality()
            card_str = self.grammar.number(card)

            if isinstance(expr, OWLObjectExactCardinality):
                quant = f"exactly {card_str}"
            elif isinstance(expr, OWLObjectMinCardinality):
                quant = f"at least {card_str}"
            else:
                quant = f"at most {card_str}"

            node = SADDGNode(
                node_type=SADDGNodeType.CARDINALITY_RELATION,
                label=head_noun,
                quantifier=quant,
                raw_owl=expr
            )

            filler = expr.get_filler()
            if not self.grammar.is_owl_thing(filler):
                node.children.append(self._build_graph(filler))

            return node

        # Default fallback
        fallback = self.grammar.clean_name(expr)
        return SADDGNode(node_type=SADDGNodeType.ROOT_NOUN, label=fallback)

    def _linearize_graph(self, node: SADDGNode, context: LinguisticContext) -> str:
        """Backward graph linearization traversal."""

        if node.node_type == SADDGNodeType.ROOT_NOUN:
            return node.label

        if node.node_type == SADDGNodeType.DATA_VALUE:
            formatted = self.grammar.format_data_value(node.label, node.quantifier)
            return f"whose {formatted}" if "is" in formatted else f"that {formatted}"

        if node.node_type == SADDGNodeType.NOMINAL_VALUE:
            return f"whose {node.label} is {node.quantifier}"

        if node.node_type == SADDGNodeType.CONJUNCTION:
            head_nodes = [c for c in node.children if c.node_type == SADDGNodeType.ROOT_NOUN]
            clause_nodes = [c for c in node.children if c.node_type != SADDGNodeType.ROOT_NOUN]

            head_str = " ".join([self._linearize_graph(h, context) for h in head_nodes]) if head_nodes else "everything"
            context.is_human = self.grammar.is_human(head_str)
            rel_pronoun = context.relative_pronoun()

            clauses = [self._linearize_graph(c, context) for c in clause_nodes]

            if not clauses:
                return head_str

            formatted_clauses = []
            for cl in clauses:
                if cl.startswith("whose") or cl.startswith("that") or cl.startswith("who"):
                    formatted_clauses.append(cl)
                else:
                    formatted_clauses.append(f"{rel_pronoun} {cl}")

            return f"{head_str} {' and '.join(formatted_clauses)}"

        if node.node_type == SADDGNodeType.EXISTENTIAL_RELATION:
            if node.quantifier:
                return f"whose {node.label} is {node.quantifier}"

            if node.children:
                child_str = self._linearize_graph(node.children[0], context)
                sing_child = self.grammar.singular(child_str)
                with_art = self.grammar.with_article(sing_child)
                return f"whose {node.label} is {with_art}"

            return f"has {node.label}"

        if node.node_type == SADDGNodeType.UNIVERSAL_RELATION:
            head_noun = self.grammar.extract_property_head_noun(node.label)
            if node.children:
                child_str = self._linearize_graph(node.children[0], context)
                sing_child = self.grammar.singular(child_str)
                return f"only has {sing_child} as {head_noun}"
            return f"only has {head_noun}"

        if node.node_type == SADDGNodeType.CARDINALITY_RELATION:
            plural_noun = node.label
            if node.quantifier and "one" in node.quantifier:
                plural_noun = self.grammar.singular(node.label)

            if not node.children:
                return f"has {node.quantifier} {plural_noun}"

            child_str = self._linearize_graph(node.children[0], context)
            return f"has {node.quantifier} {plural_noun} that are {child_str}"

        return node.label