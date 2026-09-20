from contextlib import suppress
from pathlib import Path
from typing import Union

from owlapy.class_expression import OWLClass
from owlapy.iri import IRI
from owlapy.owl_individual import OWLNamedIndividual
from owlapy.owl_ontology import SyncOntology
from owlapy.owl_property import OWLDataProperty, OWLObjectProperty

from verbalizer.common.grammar import EnglishGrammar


class OntologyInput:
    """Handles loading OWL ontologies and extracting human-readable labels using SyncOntology."""

    def __init__(self, ontology_or_path: Union[str, Path, SyncOntology], lang: str = "en"):
        self.lang = lang
        self.grammar = EnglishGrammar()

        if isinstance(ontology_or_path, (str, Path)):
            self.file_path = str(ontology_or_path)
            self.ontology = SyncOntology(str(ontology_or_path))
        else:
            self.file_path = None
            self.ontology = ontology_or_path

    def get_english_label(
        self,
        entity: Union[
            OWLClass,
            OWLObjectProperty,
            OWLDataProperty,
            OWLNamedIndividual,
            IRI,
            str,
        ],
    ) -> str:
        """
        Resolves an entity to a readable English label.
        Queries rdfs:label annotations via SyncOntology Java OWL API interface, falling back to clean_iri_fragment.
        """
        # 1. Safely extract IRI string and construct proper OWLEntity
        if isinstance(entity, str):
            iri_str = entity
            owl_entity = OWLClass(IRI.create(iri_str))
        elif isinstance(entity, IRI):
            iri_str = entity.as_str()
            owl_entity = OWLClass(entity)
        else:
            iri_str = entity.iri.as_str()
            owl_entity = entity

        # 2. Extract rdfs:label annotations using owlapy Java OWL API bridge
        if isinstance(self.ontology, SyncOntology):
            with suppress(Exception):
                # Convert Python IRI to Java IRI object for direct OWL API call
                java_iri = self.ontology.mapper.map_(owl_entity.iri)
                
                # Query Java OWLOntology for annotation assertion axioms using Java IRI
                java_axioms = self.ontology.owlapi_ontology.getAnnotationAssertionAxioms(java_iri)
                print("java_axioms:", java_axioms, len(java_axioms))

                for ax in java_axioms:
                    # Java OWL API annotation property check for rdfs:label
                    if ax.getProperty().isLabel():
                        val = ax.getValue()
                        # Extract literal text and language tag from Java OWLLiteral / Optional
                        if hasattr(val, "asLiteral"):
                            lit_opt = val.asLiteral()
                            if lit_opt.isPresent():
                                lit = lit_opt.get()
                                label_text = str(lit.getLiteral())
                                lang = str(lit.getLang()) if lit.hasLang() else None

                                # Match language tag or accept untagged labels
                                if not lang or lang.lower() == self.lang.lower():
                                    return label_text

        # 3. Fallback: Clean IRI fragment using common grammar utility
        return self.grammar.clean_iri_fragment(iri_str)