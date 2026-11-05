"""
Deep Syntactic Graph (DSyntG) Intermediate Representation for Description Logic.
Defines typed linguistic graph nodes and feature matrices prior to surface realization.
Inspired by Meaning-Text Theory (MTT) for formal natural language generation.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Optional


class FrameType(Enum):
    """Categorizes property labels into syntactic subcategorization frames."""
    VERB_ACTIVE = auto()  # Active verb phrases (e.g., "leads", "publishes")
    PASSIVE_PP = auto()   # Passive / Prepositional phrases (e.g., "located in", "manufactured by")
    RNP = auto()          # Relational Noun Phrases (e.g., "whose birth place is")
    ATTRIBUTIVE = auto()  # Data attributes with direct values (e.g., "whose age is")


class SyntacticRole(Enum):
    """Defines the grammatical function of a node within a sentence tree."""
    SUBJECT = auto()          # Main noun phrase or head entity
    PREDICATE = auto()        # Verb or copula expression
    OBJECT = auto()           # Target entity, literal value, or filler
    RELATIVE_CLAUSE = auto() # Dependent relative clause (who/that/whose)
    COORDINATION = auto()     # Logical conjunction (AND) or disjunction (OR)
    MODIFIER = auto()         # Adjectival or adverbial modifier


@dataclass
class DSyntNode:
    """
    Represents a formal linguistic constituent node in the Deep Syntactic Tree (DSyntG).
    Decouples Description Logic AST structures from surface English string formatting.
    """

    role: SyntacticRole
    head_lemma: str
    frame_type: Optional[FrameType] = None

    # Bi-directional Morpho-syntactic Feature Matrix (F)
    is_plural: bool = True
    is_human: bool = False
    is_negated: bool = False
    is_filler: bool = False

    quantifier_prefix: Optional[str] = None  # e.g., "at least 5", "exactly 1"

    # Child Dependency Constituents
    modifiers: List[str] = field(default_factory=list)
    relative_clauses: List["DSyntNode"] = field(default_factory=list)
    coordinated_nodes: List["DSyntNode"] = field(default_factory=list)
    coordination_type: Optional[str] = None  # "AND" or "OR"

    def is_coordination(self) -> bool:
        """Helper to check if this node represents a logical conjunction or disjunction."""
        return self.role == SyntacticRole.COORDINATION or bool(self.coordination_type)