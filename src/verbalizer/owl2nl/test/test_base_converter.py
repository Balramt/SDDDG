# import sys
# from pathlib import Path

# # Resolve project 'src' directory relative to this test file location:
# # File location: src/verbalizer/owl2nl/test/test_base_converter.py (4 parents to reach 'src')
# SRC_DIR = Path(__file__).resolve().parents[3]
# if str(SRC_DIR) not in sys.path:
#     sys.path.insert(0, str(SRC_DIR))

# from owlapy.class_expression import OWLClass
# from owlapy.iri import IRI

# from verbalizer.owl2nl.converters.base import BaseAxiomConverter
# from verbalizer.owl2nl.input import OntologyInput


# class ConcreteAxiomConverter(BaseAxiomConverter):
#     """Concrete dummy class to test abstract BaseAxiomConverter."""

#     def convert(self, item) -> str:
#         label = self.get_label(item)
#         return f"Verbalized: {label}"


# # 1. Test fallback without OntologyInput
# converter_no_input = ConcreteAxiomConverter()
# cls_entity = OWLClass(IRI.create("http://example.org/family#GrandFather"))

# result1 = converter_no_input.convert(cls_entity)
# print(f"Fallback Result: {result1}")
# assert result1 == "Verbalized: grand father"

# # 2. Test with OntologyInput pointing to your exact resource folder
# OWL_FILE_PATH = str(SRC_DIR / "verbalizer" / "owl2nl" / "resource" / "sample_family.owl")

# if Path(OWL_FILE_PATH).exists():
#     ontology_input = OntologyInput(OWL_FILE_PATH)
#     converter_with_input = ConcreteAxiomConverter(ontology_input=ontology_input)
#     result2 = converter_with_input.convert(cls_entity)
#     print(f"OntologyInput Result: {result2}")

# print("\nSUCCESS: BaseAxiomConverter is working correctly!")



import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[3]
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from owlapy.class_expression import OWLClass
from owlapy.owl_property import OWLObjectProperty
from owlapy.iri import IRI

from verbalizer.owl2nl.converters.base import BaseAxiomConverter
from verbalizer.owl2nl.input import OntologyInput


class ConcreteAxiomConverter(BaseAxiomConverter):
    """Concrete dummy class to test abstract BaseAxiomConverter."""

    def convert(self, item) -> str:
        label = self.get_label(item)
        return f"Verbalized: {label}"


# Entities for testing
cls_grandfather = OWLClass(IRI.create("http://example.org/family#GrandFather"))
cls_femaleperson = OWLClass(IRI.create("http://example.org/family#FemalePerson"))
prop_haschild = OWLObjectProperty(IRI.create("http://example.org/family#hasChild"))

# 1. Test fallback without OntologyInput
converter_no_input = ConcreteAxiomConverter()
result_fallback = converter_no_input.convert(cls_grandfather)
print(f"Fallback Result: {result_fallback}")
assert result_fallback == "Verbalized: grand father"

# 2. Test with OntologyInput (rdfs:label extraction + fallback)
OWL_FILE_PATH = str(SRC_DIR / "verbalizer" / "owl2nl" / "resource" / "sample_family.owl")

if Path(OWL_FILE_PATH).exists():
    ontology_input = OntologyInput(OWL_FILE_PATH)
    converter_with_input = ConcreteAxiomConverter(ontology_input=ontology_input)

    # Test entity with rdfs:label -> "woman"
    res_label = converter_with_input.convert(cls_femaleperson)
    print(f"Label Extraction Result (FemalePerson): {res_label}")
    assert res_label == "Verbalized: woman"

    # Test property with rdfs:label -> "is parent of"
    res_prop = converter_with_input.convert(prop_haschild)
    print(f"Label Extraction Result (hasChild): {res_prop}")
    assert res_prop == "Verbalized: is parent of"

    # Test entity without rdfs:label -> fallback to "grand father"
    res_no_label = converter_with_input.convert(cls_grandfather)
    print(f"Fallback Result inside OntologyInput (GrandFather): {res_no_label}")
    assert res_no_label == "Verbalized: grand father"

print("\nSUCCESS: All rdfs:label and fallback tests passed!")