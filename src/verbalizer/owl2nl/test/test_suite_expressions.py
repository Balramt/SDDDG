"""
Expanded Benchmark Test Suite for OWL Class Expression Verbalization.
Contains original benchmarks + stress-test queries to expose edge cases in:
- Contextual filler agreement (singular vs. plural subject propagation)
- Deeply nested unions, intersections, and complements
- Cardinality folding and exact/min/max bounds
- Data properties, nominals (OWLObjectOneOf), and inverse property patterns
"""

import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[3]
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from owlapy.class_expression import (
    OWLClass,
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
from owlapy.iri import IRI
from owlapy.owl_datatype import OWLDatatype
from owlapy.owl_property import OWLDataProperty, OWLObjectProperty

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

from verbalizer.owl2nl.converters.class_expression import ClassExpressionConverter


def run_benchmark_suite():
    converter = ClassExpressionConverter()

    # --- Classes ---
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
    country = OWLClass(IRI.create("http://example.org/ontology#Country"))
    award = OWLClass(IRI.create("http://example.org/ontology#Award"))
    paper = OWLClass(IRI.create("http://example.org/ontology#Paper"))

    # --- Object Properties ---
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
    won_award = OWLObjectProperty(IRI.create("http://example.org/ontology#wonAward"))
    has_citizenship = OWLObjectProperty(IRI.create("http://example.org/ontology#hasCitizenship"))

    # --- Data Properties ---
    has_age = OWLDataProperty(IRI.create("http://example.org/ontology#hasAge"))
    has_name = OWLDataProperty(IRI.create("http://example.org/ontology#hasName"))

    # --- Datatypes, Individuals & Literals ---
    string_datatype = OWLDatatype(IRI.create("http://www.w3.org/2001/XMLSchema#string"))
    germany = OWLNamedIndividual(IRI.create("http://example.org/ontology#Germany"))
    france = OWLNamedIndividual(IRI.create("http://example.org/ontology#France"))
    japan = OWLNamedIndividual(IRI.create("http://example.org/ontology#Japan"))
    nsf = OWLNamedIndividual(IRI.create("http://example.org/ontology#NSF"))
    nobel = OWLNamedIndividual(IRI.create("http://example.org/ontology#NobelPrize"))
    age_30 = OWLLiteral(30)

    # List of Test Cases: (Description / Label, Expression)
    test_cases = [
        # ==========================================
        # SECTION 1: Standard Benchmark Suite (1–8)
        # ==========================================
        (
            "1. Student ⊓ ∃enrolledIn.Course",
            OWLObjectIntersectionOf([student, OWLObjectSomeValuesFrom(enrolled_in, course)])
        ),
        (
            "2. Doctor ⊔ Professor",
            OWLObjectUnionOf([doctor, professor])
        ),
        (
            "3. Teacher ⊓ ∀teaches.(¬GraduateCourse)",
            OWLObjectIntersectionOf([teacher, OWLObjectAllValuesFrom(teaches, OWLObjectComplementOf(grad_course))])
        ),
        (
            "4. Company ⊓ (≥ 5 hasEmployee.Engineer) ⊓ headquarteredIn.Value(Germany)",
            OWLObjectIntersectionOf([company, OWLObjectMinCardinality(5, has_employee, engineer), OWLObjectHasValue(headquartered_in, germany)])
        ),
        (
            "5. Author ⊓ ∃wrote.(Book ⊔ Article)",
            OWLObjectIntersectionOf([author, OWLObjectSomeValuesFrom(wrote, OWLObjectUnionOf([book, article]))])
        ),
        (
            "6. Person ⊓ ∃birthPlace.(City ⊓ locatedIn.Value(France)) ⊓ (≥ 2 hasChild.Doctor)",
            OWLObjectIntersectionOf([person, OWLObjectSomeValuesFrom(birth_place, OWLObjectIntersectionOf([city, OWLObjectHasValue(located_in, france)])), OWLObjectMinCardinality(2, has_child, doctor)])
        ),
        (
            "7. Researcher ⊓ ∃affiliatedWith.(University ⊓ locatedIn.Value(Japan)) ⊓ ∃leadsProject.(Project ⊓ fundedBy.Value(NSF)) ⊓ (≥ 3 publishedPaper.JournalArticle)",
            OWLObjectIntersectionOf([researcher, OWLObjectSomeValuesFrom(affiliated_with, OWLObjectIntersectionOf([university, OWLObjectHasValue(located_in, japan)])), OWLObjectSomeValuesFrom(leads_project, OWLObjectIntersectionOf([project, OWLObjectHasValue(funded_by, nsf)])), OWLObjectMinCardinality(3, published_paper, journal_art)])
        ),
        (
            "8. Vehicle ⊓ ¬ElectricVehicle ⊓ (= 4 hasWheel.Wheel) ⊓ ∃manufacturedBy.(Company ⊓ (locatedIn.Value(Germany) ⊔ locatedIn.Value(France)))",
            OWLObjectIntersectionOf([
                vehicle,
                OWLObjectComplementOf(electric_vehicle),
                OWLObjectExactCardinality(4, has_wheel, wheel),
                OWLObjectSomeValuesFrom(
                    manufactured_by,
                    OWLObjectIntersectionOf([
                        company,
                        OWLObjectUnionOf([
                            OWLObjectHasValue(located_in, germany),
                            OWLObjectHasValue(located_in, france)
                        ])
                    ])
                )
            ])
        ),

        # ==========================================
        # SECTION 2: Edge Cases & Stress-Test Queries (9–18)
        # ==========================================
        (
            "9. [Max Cardinality] Person ⊓ (≤ 1 hasChild.Person)",
            OWLObjectIntersectionOf([person, OWLObjectMaxCardinality(1, has_child, person)])
        ),
        (
            "10. [Nested Filler Plurality Check] Professor ⊓ ∃teaches.(Course ⊓ ∃enrolledIn.Student)",
            OWLObjectIntersectionOf([
                professor,
                OWLObjectSomeValuesFrom(
                    teaches,
                    OWLObjectIntersectionOf([course, OWLObjectSomeValuesFrom(enrolled_in, student)])
                )
            ])
        ),
        (
            "11. [Data Property HasValue & SomeValues] Person ⊓ hasAge.Value(30) ⊓ ∃hasName.String",
            OWLObjectIntersectionOf([
                person,
                OWLDataHasValue(has_age, age_30),
                OWLDataSomeValuesFrom(has_name, string_datatype)
            ])
        ),
        (
            "12. [Nominals / OWLObjectOneOf] Person ⊓ ∃hasCitizenship.{Germany, France}",
            OWLObjectIntersectionOf([
                person,
                OWLObjectSomeValuesFrom(has_citizenship, OWLObjectOneOf([germany, france]))
            ])
        ),
        (
            "13. [Deep Negation & Union] Person ⊓ ¬(Doctor ⊔ Professor)",
            OWLObjectIntersectionOf([
                person,
                OWLObjectComplementOf(OWLObjectUnionOf([doctor, professor]))
            ])
        ),
        (
            "14. [Disjunction of Restrictions] ∃wrote.Book ⊔ ∃wrote.Article",
            OWLObjectUnionOf([
                OWLObjectSomeValuesFrom(wrote, book),
                OWLObjectSomeValuesFrom(wrote, article)
            ])
        ),
        (
            "15. [Triple Cardinality Mix] Company ⊓ (≥ 10 hasEmployee.Engineer) ⊓ (≤ 20 hasEmployee.Person) ⊓ (= 1 headquarteredIn.Country)",
            OWLObjectIntersectionOf([
                company,
                OWLObjectMinCardinality(10, has_employee, engineer),
                OWLObjectMaxCardinality(20, has_employee, person),
                OWLObjectExactCardinality(1, headquartered_in, country)
            ])
        ),
        (
            "16. [Complex Nesting with Awards] Researcher ⊓ ∃wonAward.Value(NobelPrize) ⊓ ∀publishedPaper.(JournalArticle ⊔ Book)",
            OWLObjectIntersectionOf([
                researcher,
                OWLObjectHasValue(won_award, nobel),
                OWLObjectAllValuesFrom(published_paper, OWLObjectUnionOf([journal_art, book]))
            ])
        ),
        (
            "17. [Anonymous Root Restriction] ∃enrolledIn.GraduateCourse",
            OWLObjectSomeValuesFrom(enrolled_in, grad_course)
        ),
        (
            "18. [Multiple Atomic Classes - Conjunction] Student ⊓ Employee ⊓ Person",
            OWLObjectIntersectionOf([student, OWLClass(IRI.create("http://example.org/ontology#Employee")), person])
        ),
    ]

    print("================================================================================")
    print("                     SADDG VERBALIZER BENCHMARK TEST SUITE                      ")
    print("================================================================================\n")

    for label, expr in test_cases:
        nl_output = converter.convert(expr)
        print(f"[{label}]")
        #print(f"  DL Expression: {expr}")
        print(f"  Verbalized NL: {nl_output}\n" + "-" * 80)


if __name__ == "__main__":
    run_benchmark_suite()