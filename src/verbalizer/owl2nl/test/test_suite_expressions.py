# """
# Benchmark Test Suite for OWL Class Expression Verbalization.
# Contains 8 distinct OWL queries across Simple, Complex, and Very Complex categories.
# """

# import sys
# from pathlib import Path

# # Resolve project 'src' directory relative to this test file location
# SRC_DIR = Path(__file__).resolve().parents[3]
# if str(SRC_DIR) not in sys.path:
#     sys.path.insert(0, str(SRC_DIR))

# from owlapy.class_expression import (
#     OWLClass,
#     OWLObjectAllValuesFrom,
#     OWLObjectComplementOf,
#     OWLObjectExactCardinality,
#     OWLObjectHasValue,
#     OWLObjectIntersectionOf,
#     OWLObjectMinCardinality,
#     OWLObjectSomeValuesFrom,
#     OWLObjectUnionOf,
# )
# from owlapy.iri import IRI
# from owlapy.owl_property import OWLObjectProperty

# # Robust OWLAPY Import for Individuals
# try:
#     from owlapy.owl_individual import OWLNamedIndividual
# except ImportError:
#     try:
#         from owlapy.model import OWLNamedIndividual
#     except ImportError:
#         from owlapy import OWLNamedIndividual

# from verbalizer.owl2nl.converters.class_expression import ClassExpressionConverter


# def run_benchmark_suite():
#     converter = ClassExpressionConverter()

#     # Common Entities
#     student = OWLClass(IRI.create("http://example.org/ontology#Student"))
#     course = OWLClass(IRI.create("http://example.org/ontology#Course"))
#     doctor = OWLClass(IRI.create("http://example.org/ontology#Doctor"))
#     professor = OWLClass(IRI.create("http://example.org/ontology#Professor"))
#     teacher = OWLClass(IRI.create("http://example.org/ontology#Teacher"))
#     grad_course = OWLClass(IRI.create("http://example.org/ontology#GraduateCourse"))
#     company = OWLClass(IRI.create("http://example.org/ontology#Company"))
#     engineer = OWLClass(IRI.create("http://example.org/ontology#Engineer"))
#     author = OWLClass(IRI.create("http://example.org/ontology#Author"))
#     book = OWLClass(IRI.create("http://example.org/ontology#Book"))
#     article = OWLClass(IRI.create("http://example.org/ontology#Article"))
#     researcher = OWLClass(IRI.create("http://example.org/ontology#Researcher"))
#     university = OWLClass(IRI.create("http://example.org/ontology#University"))
#     project = OWLClass(IRI.create("http://example.org/ontology#Project"))
#     journal_art = OWLClass(IRI.create("http://example.org/ontology#JournalArticle"))
#     manager = OWLClass(IRI.create("http://example.org/ontology#Manager"))
#     department = OWLClass(IRI.create("http://example.org/ontology#Department"))
#     organization = OWLClass(IRI.create("http://example.org/ontology#Organization"))
#     budget = OWLClass(IRI.create("http://example.org/ontology#Budget"))
#     vehicle = OWLClass(IRI.create("http://example.org/ontology#Vehicle"))
#     electric_vehicle = OWLClass(IRI.create("http://example.org/ontology#ElectricVehicle"))
#     wheel = OWLClass(IRI.create("http://example.org/ontology#Wheel"))

#     # Object Properties
#     enrolled_in = OWLObjectProperty(IRI.create("http://example.org/ontology#enrolledIn"))
#     teaches = OWLObjectProperty(IRI.create("http://example.org/ontology#teaches"))
#     has_employee = OWLObjectProperty(IRI.create("http://example.org/ontology#hasEmployee"))
#     headquartered_in = OWLObjectProperty(IRI.create("http://example.org/ontology#headquarteredIn"))
#     wrote = OWLObjectProperty(IRI.create("http://example.org/ontology#wrote"))
#     affiliated_with = OWLObjectProperty(IRI.create("http://example.org/ontology#affiliatedWith"))
#     located_in = OWLObjectProperty(IRI.create("http://example.org/ontology#locatedIn"))
#     leads_project = OWLObjectProperty(IRI.create("http://example.org/ontology#leadsProject"))
#     funded_by = OWLObjectProperty(IRI.create("http://example.org/ontology#fundedBy"))
#     published_paper = OWLObjectProperty(IRI.create("http://example.org/ontology#publishedPaper"))
#     manages = OWLObjectProperty(IRI.create("http://example.org/ontology#manages"))
#     belongs_to = OWLObjectProperty(IRI.create("http://example.org/ontology#belongsTo"))
#     approves = OWLObjectProperty(IRI.create("http://example.org/ontology#approves"))
#     has_wheel = OWLObjectProperty(IRI.create("http://example.org/ontology#hasWheel"))
#     manufactured_by = OWLObjectProperty(IRI.create("http://example.org/ontology#manufacturedBy"))

#     # Individuals
#     germany = OWLNamedIndividual(IRI.create("http://example.org/ontology#Germany"))
#     japan = OWLNamedIndividual(IRI.create("http://example.org/ontology#Japan"))
#     nsf = OWLNamedIndividual(IRI.create("http://example.org/ontology#NSF"))
#     usa = OWLNamedIndividual(IRI.create("http://example.org/ontology#USA"))
#     france = OWLNamedIndividual(IRI.create("http://example.org/ontology#France"))

#     # Define the 8 Benchmark Expressions
#     test_cases = [
#         # --- SIMPLE / EASY (2 Cases) ---
#         {
#             "id": 1,
#             "category": "EASY",
#             "description": "Atomic Class Conjunction with Existential Restriction",
#             "dl": "Student ⊓ ∃enrolledIn.Course",
#             "manchester": "Student AND enrolledIn SOME Course",
#             "expr": OWLObjectIntersectionOf([student, OWLObjectSomeValuesFrom(enrolled_in, course)]),
#         },
#         {
#             "id": 2,
#             "category": "EASY",
#             "description": "Disjunction (Union) of Atomic Classes",
#             "dl": "Doctor ⊔ Professor",
#             "manchester": "Doctor OR Professor",
#             "expr": OWLObjectUnionOf([doctor, professor]),
#         },

#         # --- COMPLEX (3 Cases) ---
#         {
#             "id": 3,
#             "category": "COMPLEX",
#             "description": "Universal Quantifier with Negated Class Filler",
#             "dl": "Teacher ⊓ ∀teaches.(¬GraduateCourse)",
#             "manchester": "Teacher AND teaches ONLY (NOT GraduateCourse)",
#             "expr": OWLObjectIntersectionOf([
#                 teacher,
#                 OWLObjectAllValuesFrom(teaches, OWLObjectComplementOf(grad_course))
#             ]),
#         },
#         {
#             "id": 4,
#             "category": "COMPLEX",
#             "description": "Minimum Cardinality with Value Restriction",
#             "dl": "Company ⊓ (≥ 5 hasEmployee.Engineer) ⊓ headquarteredIn.Value(Germany)",
#             "manchester": "Company AND hasEmployee MIN 5 Engineer AND headquarteredIn VALUE Germany",
#             "expr": OWLObjectIntersectionOf([
#                 company,
#                 OWLObjectMinCardinality(5, has_employee, engineer),
#                 OWLObjectHasValue(headquartered_in, germany)
#             ]),
#         },
#         {
#             "id": 5,
#             "category": "COMPLEX",
#             "description": "Existential Restriction with Union Filler",
#             "dl": "Author ⊓ ∃wrote.(Book ⊔ Article)",
#             "manchester": "Author AND wrote SOME (Book OR Article)",
#             "expr": OWLObjectIntersectionOf([
#                 author,
#                 OWLObjectSomeValuesFrom(wrote, OWLObjectUnionOf([book, article]))
#             ]),
#         },

#         # --- VERY COMPLEX (3 Cases) ---
#         {
#             "id": 6,
#             "category": "VERY COMPLEX",
#             "description": "Multi-Restriction Intersection with Nested Fillers & Cardinality",
#             "dl": "Researcher ⊓ ∃affiliatedWith.(University ⊓ locatedIn.Value(Japan)) ⊓ ∃leadsProject.(Project ⊓ fundedBy.Value(NSF)) ⊓ (≥ 3 publishedPaper.JournalArticle)",
#             "manchester": "Researcher AND affiliatedWith SOME (University AND locatedIn VALUE Japan) AND leadsProject SOME (Project AND fundedBy VALUE NSF) AND publishedPaper MIN 3 JournalArticle",
#             "expr": OWLObjectIntersectionOf([
#                 researcher,
#                 OWLObjectSomeValuesFrom(affiliated_with, OWLObjectIntersectionOf([university, OWLObjectHasValue(located_in, japan)])),
#                 OWLObjectSomeValuesFrom(leads_project, OWLObjectIntersectionOf([project, OWLObjectHasValue(funded_by, nsf)])),
#                 OWLObjectMinCardinality(3, published_paper, journal_art)
#             ]),
#         },
#         {
#             "id": 7,
#             "category": "VERY COMPLEX",
#             "description": "Deeply Nested Existential Quantifiers with Universal Constraint",
#             "dl": "Manager ⊓ ∃manages.(Department ⊓ ∃belongsTo.(Organization ⊓ locatedIn.Value(USA))) ⊓ ∀approves.Budget",
#             "manchester": "Manager AND manages SOME (Department AND belongsTo SOME (Organization AND locatedIn VALUE USA)) AND approves ONLY Budget",
#             "expr": OWLObjectIntersectionOf([
#                 manager,
#                 OWLObjectSomeValuesFrom(manages, OWLObjectIntersectionOf([
#                     department,
#                     OWLObjectSomeValuesFrom(belongs_to, OWLObjectIntersectionOf([organization, OWLObjectHasValue(located_in, usa)]))
#                 ])),
#                 OWLObjectAllValuesFrom(approves, budget)
#             ]),
#         },
#         {
#             "id": 8,
#             "category": "VERY COMPLEX",
#             "description": "Negation, Exact Cardinality, and Disjunction within Nested Filler",
#             "dl": "Vehicle ⊓ ¬ElectricVehicle ⊓ (= 4 hasWheel.Wheel) ⊓ ∃manufacturedBy.(Company ⊓ (locatedIn.Value(Germany) ⊔ locatedIn.Value(France)))",
#             "manchester": "Vehicle AND NOT ElectricVehicle AND hasWheel EXACT 4 Wheel AND manufacturedBy SOME (Company AND (locatedIn VALUE Germany OR locatedIn VALUE France))",
#             "expr": OWLObjectIntersectionOf([
#                 vehicle,
#                 OWLObjectComplementOf(electric_vehicle),
#                 OWLObjectExactCardinality(4, has_wheel, wheel),
#                 OWLObjectSomeValuesFrom(manufactured_by, OWLObjectIntersectionOf([
#                     company,
#                     OWLObjectUnionOf([
#                         OWLObjectHasValue(located_in, germany),
#                         OWLObjectHasValue(located_in, france)
#                     ])
#                 ]))
#             ]),
#         },
#     ]

#     # Run and Print Output
#     print("=" * 80)
#     print("      OWL CLASS EXPRESSION VERBALIZATION BENCHMARK SUITE")
#     print("=" * 80)

#     for case in test_cases:
#         nl_output = converter.convert(case["expr"])

#         print(f"\n[Test Query #{case['id']}] Category: {case['category']}")
#         print(f"Description : {case['description']}")
#         print(f"DL Query    : {case['dl']}")
#         print(f"Manchester  : {case['manchester']}")
#         print("-" * 80)
#         print(f"Generated NL Output: {nl_output}")
#         print("=" * 80)


# if __name__ == "__main__":
#     run_benchmark_suite()




"""
Benchmark Test Suite for OWL Class Expression Verbalization.
Clean console output using Unicode Description Logic symbols.
"""

import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[3]
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from owlapy.class_expression import (
    OWLClass,
    OWLObjectAllValuesFrom,
    OWLObjectComplementOf,
    OWLObjectExactCardinality,
    OWLObjectHasValue,
    OWLObjectIntersectionOf,
    OWLObjectMinCardinality,
    OWLObjectSomeValuesFrom,
    OWLObjectUnionOf,
)
from owlapy.iri import IRI
from owlapy.owl_property import OWLObjectProperty

try:
    from owlapy.owl_individual import OWLNamedIndividual
except ImportError:
    try:
        from owlapy.model import OWLNamedIndividual
    except ImportError:
        from owlapy import OWLNamedIndividual

from verbalizer.owl2nl.converters.class_expression import ClassExpressionConverter


def run_benchmark_suite():
    converter = ClassExpressionConverter()

    # Entities
    person = OWLClass(IRI.create("http://example.org/ontology#Person"))
    student = OWLClass(IRI.create("http://example.org/ontology#Student"))
    course = OWLClass(IRI.create("http://example.org/ontology#Course"))
    doctor = OWLClass(IRI.create("http://example.org/ontology#Doctor"))
    professor = OWLClass(IRI.create("http://example.org/ontology#Professor"))
    teacher = OWLClass(IRI.create("http://example.org/ontology#Teacher"))
    grad_course = OWLClass(IRI.create("http://example.org/ontology#GraduateCourse"))
    company = OWLClass(IRI.create("http://example.org/ontology#Company"))
    engineer = OWLClass(IRI.create("http://example.org/ontology#Engineer"))
    author = OWLClass(IRI.create("http://example.org/ontology#Author"))
    book = OWLClass(IRI.create("http://example.org/ontology#Book"))
    article = OWLClass(IRI.create("http://example.org/ontology#Article"))
    city = OWLClass(IRI.create("http://example.org/ontology#City"))
    researcher = OWLClass(IRI.create("http://example.org/ontology#Researcher"))
    university = OWLClass(IRI.create("http://example.org/ontology#University"))
    project = OWLClass(IRI.create("http://example.org/ontology#Project"))
    journal_art = OWLClass(IRI.create("http://example.org/ontology#JournalArticle"))
    vehicle = OWLClass(IRI.create("http://example.org/ontology#Vehicle"))
    electric_vehicle = OWLClass(IRI.create("http://example.org/ontology#ElectricVehicle"))
    wheel = OWLClass(IRI.create("http://example.org/ontology#Wheel"))

    # Object Properties
    enrolled_in = OWLObjectProperty(IRI.create("http://example.org/ontology#enrolledIn"))
    teaches = OWLObjectProperty(IRI.create("http://example.org/ontology#teaches"))
    has_employee = OWLObjectProperty(IRI.create("http://example.org/ontology#hasEmployee"))
    headquartered_in = OWLObjectProperty(IRI.create("http://example.org/ontology#headquarteredIn"))
    wrote = OWLObjectProperty(IRI.create("http://example.org/ontology#wrote"))
    birth_place = OWLObjectProperty(IRI.create("http://example.org/ontology#birthPlace"))
    located_in = OWLObjectProperty(IRI.create("http://example.org/ontology#locatedIn"))
    has_child = OWLObjectProperty(IRI.create("http://example.org/ontology#hasChild"))
    affiliated_with = OWLObjectProperty(IRI.create("http://example.org/ontology#affiliatedWith"))
    leads_project = OWLObjectProperty(IRI.create("http://example.org/ontology#leadsProject"))
    funded_by = OWLObjectProperty(IRI.create("http://example.org/ontology#fundedBy"))
    published_paper = OWLObjectProperty(IRI.create("http://example.org/ontology#publishedPaper"))
    has_wheel = OWLObjectProperty(IRI.create("http://example.org/ontology#hasWheel"))
    manufactured_by = OWLObjectProperty(IRI.create("http://example.org/ontology#manufacturedBy"))

    # Individuals
    germany = OWLNamedIndividual(IRI.create("http://example.org/ontology#Germany"))
    france = OWLNamedIndividual(IRI.create("http://example.org/ontology#France"))
    japan = OWLNamedIndividual(IRI.create("http://example.org/ontology#Japan"))
    nsf = OWLNamedIndividual(IRI.create("http://example.org/ontology#NSF"))

    # 8 Benchmark Expressions with Unicode Symbols
    test_cases = [
        (
            "Student ⊓ ∃enrolledIn.Course",
            OWLObjectIntersectionOf([student, OWLObjectSomeValuesFrom(enrolled_in, course)])
        ),
        (
            "Doctor ⊔ Professor",
            OWLObjectUnionOf([doctor, professor])
        ),
        (
            "Teacher ⊓ ∀teaches.(¬GraduateCourse)",
            OWLObjectIntersectionOf([teacher, OWLObjectAllValuesFrom(teaches, OWLObjectComplementOf(grad_course))])
        ),
        (
            "Company ⊓ (≥ 5 hasEmployee.Engineer) ⊓ headquarteredIn.Value(Germany)",
            OWLObjectIntersectionOf([company, OWLObjectMinCardinality(5, has_employee, engineer), OWLObjectHasValue(headquartered_in, germany)])
        ),
        (
            "Author ⊓ ∃wrote.(Book ⊔ Article)",
            OWLObjectIntersectionOf([author, OWLObjectSomeValuesFrom(wrote, OWLObjectUnionOf([book, article]))])
        ),
        (
            "Person ⊓ ∃birthPlace.(City ⊓ locatedIn.Value(France)) ⊓ (≥ 2 hasChild.Doctor)",
            OWLObjectIntersectionOf([person, OWLObjectSomeValuesFrom(birth_place, OWLObjectIntersectionOf([city, OWLObjectHasValue(located_in, france)])), OWLObjectMinCardinality(2, has_child, doctor)])
        ),
        (
            "Researcher ⊓ ∃affiliatedWith.(University ⊓ locatedIn.Value(Japan)) ⊓ ∃leadsProject.(Project ⊓ fundedBy.Value(NSF)) ⊓ (≥ 3 publishedPaper.JournalArticle)",
            OWLObjectIntersectionOf([researcher, OWLObjectSomeValuesFrom(affiliated_with, OWLObjectIntersectionOf([university, OWLObjectHasValue(located_in, japan)])), OWLObjectSomeValuesFrom(leads_project, OWLObjectIntersectionOf([project, OWLObjectHasValue(funded_by, nsf)])), OWLObjectMinCardinality(3, published_paper, journal_art)])
        ),
        # (
        #     "Vehicle ⊓ ¬ElectricVehicle ⊓ (= 4 hasWheel.Wheel) ⊓ ∃manufacturedBy.(Company ⊓ (locatedIn.Value(Germany) ⊔ locatedIn.Value(France)))",
        #     OWLObjectIntersectionOf([vehicle, OWLObjectComplementOf(electric_vehicle), OWLObjectExactCardinality(4, has_wheel, wheel), OWLObjectSomeValuesFrom(manufactured_by, OWLObjectIntersectionOf([company, OWLObjectUnionOf([OWLObjectHasValue(located_in, germany), OWLObjectHasValue(located_in, france)])]))])
        # ),
    ]

    for dl_str, expr in test_cases:
        nl_output = converter.convert(expr)
        print(f"input:  {dl_str}")
        print(f"output: {nl_output}\n")


if __name__ == "__main__":
    run_benchmark_suite()