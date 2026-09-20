from owlapy.class_expression import OWLClass
from owlapy.iri import IRI
from owlapy.owl_property import OWLObjectProperty

from verbalizer.owl2nl.input import OntologyInput

# 1. Initialize OntologyInput with sample OWL file
ontology_input = OntologyInput("/home/tiwari/workspace_dice/verbalizer/src/verbalizer/owl2nl/resource/sample_family.owl")  

# Case A: OWLClass WITH rdfs:label ("woman")
female_person = OWLClass(IRI.create("http://example.org/family#FemalePerson"))
label_a = ontology_input.get_english_label(female_person)

# Case B: OWLClass WITHOUT rdfs:label (Falls back to cleaning "GrandFather" -> "grand father")
grandfather = OWLClass(IRI.create("http://example.org/family#GrandFather"))
label_b = ontology_input.get_english_label(grandfather)

# Case C: OWLObjectProperty WITH rdfs:label ("is parent of")
has_child = OWLObjectProperty(IRI.create("http://example.org/family#hasChild"))
label_c = ontology_input.get_english_label(has_child)

# Case D: OWLObjectProperty WITHOUT rdfs:label (Falls back to cleaning "hasSpouse" -> "has spouse")
has_spouse = OWLObjectProperty(IRI.create("http://example.org/family#hasSpouse"))
label_d = ontology_input.get_english_label(has_spouse)

# Case E: Plain String IRI
label_e = ontology_input.get_english_label("http://example.org/family#isEmployedBy")

print("\n================ SUMMARY ================")
print(f"FemalePerson -> '{label_a}'")
print(f"GrandFather  -> '{label_b}'")
print(f"hasChild     -> '{label_c}'")
print(f"hasSpouse    -> '{label_d}'")
print(f"isEmployedBy -> '{label_e}'")