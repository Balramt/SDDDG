"""Test suite for SADDG Class Expression Verbalization engine."""

import sys
from pathlib import Path

# Resolve project 'src' directory relative to this test file location
SRC_DIR = Path(__file__).resolve().parents[3]
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from owlapy.class_expression import (
    OWLClass,
    OWLObjectHasValue,
    OWLObjectIntersectionOf,
    OWLObjectMinCardinality,
    OWLObjectSomeValuesFrom,
)
from owlapy.iri import IRI
from owlapy.owl_property import OWLObjectProperty

# Robust OWLAPY Import for Individuals
try:
    from owlapy.owl_individual import OWLNamedIndividual
except ImportError:
    try:
        from owlapy.model import OWLNamedIndividual
    except ImportError:
        from owlapy import OWLNamedIndividual

from verbalizer.owl2nl.converters.class_expression import ClassExpressionConverter
from verbalizer.owl2nl.input import OntologyInput


def test_fallback_complex_expression():
    """Test verbalization of nested class expressions without an ontology input."""
    converter = ClassExpressionConverter()

    # Define Entities
    person = OWLClass(IRI.create("http://example.org/ontology#Person"))
    city = OWLClass(IRI.create("http://example.org/ontology#City"))
    doctor = OWLClass(IRI.create("http://example.org/ontology#Doctor"))

    birth_place = OWLObjectProperty(IRI.create("http://example.org/ontology#birthPlace"))
    located_in = OWLObjectProperty(IRI.create("http://example.org/ontology#locatedIn"))
    has_child = OWLObjectProperty(IRI.create("http://example.org/ontology#hasChild"))

    france = OWLNamedIndividual(IRI.create("http://example.org/ontology#France"))

    # Build Subtree: (City AND locatedIn VALUE France)
    inner_city_expr = OWLObjectIntersectionOf(
        [city, OWLObjectHasValue(located_in, france)]
    )

    # Build Complex Expression:
    # Person AND birthPlace SOME (City AND locatedIn VALUE France) AND MIN 2 hasChild Doctor
    complex_expression = OWLObjectIntersectionOf(
        [
            person,
            OWLObjectSomeValuesFrom(birth_place, inner_city_expr),
            OWLObjectMinCardinality(2, has_child, doctor),
        ]
    )

    result = converter.convert(complex_expression)
    print("\n--- Test 1: Fallback Verbalization ---")
    print(f"Output: {result}")

    result_lower = result.lower()
    assert "people" in result_lower
    assert "birth place is a city that is located in france" in result_lower
    assert "at least two has child who are doctors" in result_lower


def test_with_ontology_input():
    """Test verbalization using rdfs:label extraction from sample_family.owl."""
    owl_file_path = str(
        SRC_DIR / "verbalizer" / "owl2nl" / "resource" / "sample_family.owl"
    )

    if not Path(owl_file_path).exists():
        print("\nSkipping Test 2: sample_family.owl resource file not found.")
        return

    ontology_input = OntologyInput(owl_file_path)
    converter = ClassExpressionConverter(ontology_input=ontology_input)

    # Entities matching sample_family.owl
    female_person = OWLClass(IRI.create("http://example.org/family#FemalePerson"))
    has_child = OWLObjectProperty(IRI.create("http://example.org/family#hasChild"))
    person = OWLClass(IRI.create("http://example.org/family#Person"))

    # Expression: FemalePerson AND hasChild SOME Person
    mother_expr = OWLObjectIntersectionOf(
        [female_person, OWLObjectSomeValuesFrom(has_child, person)]
    )

    result = converter.convert(mother_expr)
    print("\n--- Test 2: Ontology Label Verbalization ---")
    print(f"Output: {result}")

    result_lower = result.lower()
    assert "women" in result_lower
    assert "is parent of" in result_lower


if __name__ == "__main__":
    test_fallback_complex_expression()
    test_with_ontology_input()
    print("\nSUCCESS: All Class Expression Verbalizer tests passed!")