"""Base axiom converter module for OWL to NL conversion."""

from abc import ABC, abstractmethod

from owlapy.class_expression import OWLClassExpression
from owlapy.owl_axiom import OWLAxiom

from verbalizer.common.base import BaseConverter, VerbalizerMode
from verbalizer.common.grammar import EnglishGrammar
from verbalizer.owl2nl.input import OntologyInput


class BaseAxiomConverter(BaseConverter[OWLAxiom, str], ABC):
    """Base class for all OWL axiom and class expression converters."""

    def __init__(
        self,
        ontology_input: OntologyInput | None = None,
        grammar: EnglishGrammar | None = None,
        mode: VerbalizerMode = VerbalizerMode.STANDARD,
    ):
        super().__init__(mode=mode)
        self.ontology_input = ontology_input
        self.grammar = grammar or EnglishGrammar()

    def get_label(self, item: OWLClassExpression | OWLAxiom | str) -> str:
        """Helper to resolve human-readable labels for entities or class expressions."""
        if self.ontology_input:
            return self.ontology_input.get_english_label(item)

        iri_str = item.iri.as_str() if hasattr(item, "iri") else str(item)
        return self.grammar.clean_iri_fragment(iri_str)

    @abstractmethod
    def convert(self, item: OWLAxiom) -> str:
        """Convert an OWL Axiom into natural English text."""