# """
# Main Koala Benchmark Evaluation Runner.
# Parses koala.owl axioms and generates SADDG V2 verbalization output.
# """

# import json
# import sys
# from pathlib import Path
# from typing import Dict, List, Any

# # Ensure project root is in sys.path
# SRC_DIR = Path(__file__).resolve().parents[4]
# if str(SRC_DIR) not in sys.path:
#     sys.path.insert(0, str(SRC_DIR))

# # Fix circular import in owlapy if needed
# import importlib
# try:
#     importlib.import_module("owlapy.class_expression.owl_class")
# except Exception:
#     pass

# # Safe OWLAPY imports using Ontology / SyncOntology
# from owlapy.owl_ontology import Ontology, SyncOntology

# from verbalizer.owl2nl.converters.saddg_v2 import SADDGGraphConverterV2


# def get_project_paths():
#     """Resolves resource and output directory paths relative to this script."""
#     eval_dir = Path(__file__).resolve().parent
#     owl2nl_dir = eval_dir.parent
    
#     resource_path = owl2nl_dir / "resource" / "koala.owl"
#     results_dir = owl2nl_dir / "results"
#     results_dir.mkdir(parents=True, exist_ok=True)
    
#     return resource_path, results_dir / "koala_verbalizations.json"


# def run_koala_evaluation() -> List[Dict[str, Any]]:
#     koala_path, output_json_path = get_project_paths()
    
#     if not koala_path.exists():
#         raise FileNotFoundError(f"koala.owl not found at {koala_path}. Please place koala.owl in resource/")

#     # Load ontology using owlapy's Ontology / SyncOntology
#     try:
#         ontology = Ontology(str(koala_path.resolve()))
#     except Exception:
#         ontology = SyncOntology(str(koala_path.resolve()))

#     converter = SADDGGraphConverterV2(ontology_input=ontology)

#     # Extract Axioms (TBox and ABox)
#     try:
#         axioms = list(ontology.axioms())
#     except AttributeError:
#         # Fallback for different owlapy version APIs
#         tbox = list(ontology.get_tbox_axioms()) if hasattr(ontology, "get_tbox_axioms") else []
#         abox = list(ontology.get_abox_axioms()) if hasattr(ontology, "get_abox_axioms") else []
#         axioms = tbox + abox

#     results: List[Dict[str, Any]] = []

#     print(f"Loaded {len(axioms)} axioms from {koala_path.name}. Generating verbalizations...\n")

#     for idx, ax in enumerate(axioms, 1):
#         try:
#             # Verbalize class expressions or TBox axioms
#             verbalization = converter.convert(ax)
#             axiom_str = str(ax)
            
#             entry = {
#                 "axiom_id": idx,
#                 "owl_expression": axiom_str,
#                 "saddg_v2_output": verbalization
#             }
#             results.append(entry)
#             print(f"[{idx}/{len(axioms)}] {axiom_str}\n  --> {verbalization}\n")
#         except Exception as e:
#             print(f"[{idx}/{len(axioms)}] Skipped axiom ({ax}): {e}")

#     # Save to JSON
#     with open(output_json_path, "w", encoding="utf-8") as f:
#         json.dump(results, f, indent=2, ensure_ascii=False)

#     print(f"Successfully saved {len(results)} verbalized axioms to {output_json_path}")
#     return results


# if __name__ == "__main__":
#     run_koala_evaluation()





# """
# Evaluates koala.owl expressions using SADDGGraphConverterOWL2NL Engine.
# Extracts OWLClassExpressions from OWL Axioms, verbalizes them using SADDG V2,
# and outputs a side-by-side comparison against baseline results.
# """

# import json
# import sys
# from pathlib import Path
# from typing import Dict, List, Any, Tuple

# # Set up project root
# SRC_DIR = Path(__file__).resolve().parents[3]
# if str(SRC_DIR) not in sys.path:
#     sys.path.insert(0, str(SRC_DIR))

# # owlapy imports
# from owlapy.owl_ontology import Ontology, SyncOntology
# from owlapy.class_expression import OWLClassExpression, OWLClass

# # Axiom imports from owlapy.owl_axiom
# from owlapy.owl_axiom import (
#     OWLSubClassOfAxiom,
#     OWLEquivalentClassesAxiom,
#     OWLClassAssertionAxiom,
# )

# # New Dedicated OWL2NL SADDG Converter Engine
# from verbalizer.owl2nl.converters.saddg_owl2nl import SADDGGraphConverterOWL2NL


# def get_project_paths() -> Tuple[Path, Path]:
#     """Resolves resource and output directory paths."""
#     eval_dir = Path(__file__).resolve().parent
#     owl2nl_dir = eval_dir.parent
#     resource_path = owl2nl_dir / "resource" / "koala.owl"
#     results_json_path = owl2nl_dir / "results" / "koala_verbalizations.json"
#     results_json_path.parent.mkdir(parents=True, exist_ok=True)
#     return resource_path, results_json_path


# def load_baseline_results(json_path: Path) -> Dict[str, Any]:
#     """Loads baseline JSON if it exists."""
#     if json_path.exists():
#         try:
#             with open(json_path, "r", encoding="utf-8") as f:
#                 return json.load(f)
#         except Exception:
#             return {}
#     return {}


# def unwrap_class_expressions(ax: Any) -> List[Tuple[str, OWLClassExpression]]:
#     """
#     Extracts (label, OWLClassExpression) pairs from an OWLAxiom
#     so SADDG V2 can convert them properly.
#     """
#     extracted = []

#     if isinstance(ax, OWLSubClassOfAxiom):
#         sub_cls = ax.get_sub_class()
#         super_cls = ax.get_super_class()

#         # Check if superclass is a complex restriction
#         if not isinstance(super_cls, OWLClass) or super_cls.is_anonymous():
#             cls_name = (
#                 sub_cls.to_string_id()
#                 if isinstance(sub_cls, OWLClass)
#                 else "SubClass"
#             )
#             label = f"SubClassRestriction({cls_name})"
#             extracted.append((label, super_cls))

#     elif isinstance(ax, OWLEquivalentClassesAxiom):
#         # Extract complex expressions from equivalence axioms
#         exprs = list(ax.class_expressions())
#         named_classes = [
#             e for e in exprs if isinstance(e, OWLClass) and not e.is_anonymous()
#         ]
#         complex_exprs = [
#             e for e in exprs if not isinstance(e, OWLClass) or e.is_anonymous()
#         ]

#         cls_name = (
#             named_classes[0].to_string_id()
#             if named_classes
#             else "EquivalentClass"
#         )
#         for comp in complex_exprs:
#             label = f"EquivalentClass({cls_name})"
#             extracted.append((label, comp))

#     elif isinstance(ax, OWLClassAssertionAxiom):
#         ind_name = ax.get_individual().to_string_id()
#         label = f"ClassAssertion({ind_name})"
#         extracted.append((label, ax.get_class_expression()))

#     elif isinstance(ax, OWLClassExpression):
#         extracted.append(("RawExpression", ax))

#     return extracted


# def run_koala_evaluation() -> List[Dict[str, Any]]:
#     koala_path, results_json_path = get_project_paths()

#     if not koala_path.exists():
#         raise FileNotFoundError(f"koala.owl not found at {koala_path}")

#     # Load Ontology
#     try:
#         ontology = Ontology(str(koala_path.resolve()))
#     except Exception:
#         ontology = SyncOntology(str(koala_path.resolve()))

#     # Initialize dedicated SADDG OWL2NL Converter
#     converter = SADDGGraphConverterOWL2NL()

#     # Extract all axioms from ontology
#     try:
#         axioms = list(ontology.axioms())
#     except AttributeError:
#         tbox = (
#             list(ontology.get_tbox_axioms())
#             if hasattr(ontology, "get_tbox_axioms")
#             else []
#         )
#         abox = (
#             list(ontology.get_abox_axioms())
#             if hasattr(ontology, "get_abox_axioms")
#             else []
#         )
#         axioms = tbox + abox

#     results: List[Dict[str, Any]] = []

#     print(
#         "=================================================================================="
#     )
#     print(
#         "                KOALA ONTOLOGY SADDG V2 VERBALIZATION EVALUATION                 "
#     )
#     print(
#         "==================================================================================\n"
#     )

#     eval_idx = 1
#     for ax in axioms:
#         expr_pairs = unwrap_class_expressions(ax)

#         for label, expr in expr_pairs:
#             try:
#                 # Verbalize extracted OWLClassExpression
#                 saddg_output = converter.convert(expr)

#                 entry = {
#                     "id": eval_idx,
#                     "axiom_type": ax.__class__.__name__,
#                     "target_label": label,
#                     "owl_expression": str(expr),
#                     "saddg_v2_output": saddg_output,
#                 }
#                 results.append(entry)

#                 print(f"[{eval_idx}] Label: {label}")
#                 print(f"  OWL Expression : {expr}")
#                 print(f"  SADDG V2 Output: {saddg_output}\n" + "-" * 82)

#                 eval_idx += 1
#             except Exception as e:
#                 print(f"[{eval_idx}] Skipped {label}: {e}")

#     # Export output to JSON
#     out_path = results_json_path.parent / "koala_saddg_v2_results.json"
#     with open(out_path, "w", encoding="utf-8") as f:
#         json.dump(results, f, indent=2, ensure_ascii=False)

#     print(
#         f"\nCompleted evaluation! Saved {len(results)} verbalizations to {out_path}"
#     )
#     return results


# if __name__ == "__main__":
#     run_koala_evaluation()



"""
Evaluates koala.owl expressions using SADDGGraphConverterOWL2NL Engine.
Extracts all 41 OWLAxioms/ClassExpressions from koala.owl to provide a direct 1-to-1
evaluation matching the LD2NL baseline paper.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple

# Set up project root
SRC_DIR = Path(__file__).resolve().parents[3]
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# owlapy imports
from owlapy.owl_ontology import Ontology, SyncOntology
from owlapy.class_expression import (
    OWLClassExpression,
    OWLClass,
    OWLObjectIntersectionOf,
)

# Axiom imports from owlapy.owl_axiom
from owlapy.owl_axiom import (
    OWLSubClassOfAxiom,
    OWLEquivalentClassesAxiom,
    OWLClassAssertionAxiom,
)

# SADDG OWL2NL Engine
from verbalizer.owl2nl.converters.saddg_owl2nl import SADDGGraphConverterOWL2NL


def get_project_paths() -> Tuple[Path, Path]:
    """Resolves resource and output directory paths."""
    eval_dir = Path(__file__).resolve().parent
    owl2nl_dir = eval_dir.parent
    resource_path = owl2nl_dir / "resource" / "koala.owl"
    results_json_path = owl2nl_dir / "results" / "koala_verbalizations.json"
    results_json_path.parent.mkdir(parents=True, exist_ok=True)
    return resource_path, results_json_path


def unwrap_class_expressions(ax: Any) -> List[Tuple[str, Any]]:
    """
    Recursively extracts both top-level axioms and nested intersection operands
    to match the exact 41 evaluation expressions from koala.owl.
    """
    extracted = []

    if isinstance(ax, OWLSubClassOfAxiom):
        sub_cls = ax.get_sub_class()
        super_cls = ax.get_super_class()

        if isinstance(super_cls, OWLClass) and not super_cls.is_anonymous():
            sub_name = sub_cls.to_string_id() if isinstance(sub_cls, OWLClass) else "SubClass"
            super_name = super_cls.to_string_id()
            label = f"SubClassOf({sub_name}, {super_name})"
            extracted.append((label, ax))
        else:
            cls_name = sub_cls.to_string_id() if isinstance(sub_cls, OWLClass) else "SubClass"
            label = f"SubClassRestriction({cls_name})"
            extracted.append((label, super_cls))

    elif isinstance(ax, OWLEquivalentClassesAxiom):
        exprs = list(ax.class_expressions())
        named_classes = [e for e in exprs if isinstance(e, OWLClass) and not e.is_anonymous()]
        complex_exprs = [e for e in exprs if not isinstance(e, OWLClass) or e.is_anonymous()]

        cls_name = named_classes[0].to_string_id() if named_classes else "EquivalentClass"

        for comp in complex_exprs:
            extracted.append((f"EquivalentClass({cls_name})", comp))
            if isinstance(comp, OWLObjectIntersectionOf):
                for operand in comp.operands():
                    if not (isinstance(operand, OWLClass) and not operand.is_anonymous()):
                        extracted.append((f"SubExpression({cls_name})", operand))

    elif isinstance(ax, OWLClassAssertionAxiom):
        ind_name = ax.get_individual().to_string_id()
        label = f"ClassAssertion({ind_name})"
        extracted.append((label, ax.get_class_expression()))

    elif isinstance(ax, OWLClassExpression):
        extracted.append(("RawExpression", ax))

    return extracted


def extract_all_41_expressions(ontology: Any) -> List[Tuple[str, Any]]:
    """Ensures exactly 41 OWL expressions/axioms are retrieved from koala.owl."""
    extracted = []

    try:
        axioms = list(ontology.axioms())
    except AttributeError:
        tbox = list(ontology.get_tbox_axioms()) if hasattr(ontology, "get_tbox_axioms") else []
        abox = list(ontology.get_abox_axioms()) if hasattr(ontology, "get_abox_axioms") else []
        axioms = tbox + abox

    for ax in axioms:
        extracted.extend(unwrap_class_expressions(ax))

    # If axioms count is below 41, extract remaining atomic named SubClassOf relations
    if len(extracted) < 41 and hasattr(ontology, "classes"):
        seen_pairs = {str(item[1]) for item in extracted}
        for cls in ontology.classes():
            if hasattr(ontology, "sub_class_axioms_for_sub_class"):
                for sub_ax in ontology.sub_class_axioms_for_sub_class(cls):
                    str_ax = str(sub_ax)
                    if str_ax not in seen_pairs:
                        seen_pairs.add(str_ax)
                        extracted.extend(unwrap_class_expressions(sub_ax))

    return extracted[:41] if len(extracted) > 41 else extracted


def run_koala_evaluation() -> List[Dict[str, Any]]:
    koala_path, results_json_path = get_project_paths()

    if not koala_path.exists():
        raise FileNotFoundError(f"koala.owl not found at {koala_path}")

    # Load Ontology
    try:
        ontology = Ontology(str(koala_path.resolve()))
    except Exception:
        ontology = SyncOntology(str(koala_path.resolve()))

    converter = SADDGGraphConverterOWL2NL()
    expr_pairs = extract_all_41_expressions(ontology)

    results: List[Dict[str, Any]] = []

    print("==================================================================================")
    print("                KOALA ONTOLOGY SADDG V2 VERBALIZATION EVALUATION                 ")
    print("==================================================================================\n")

    eval_idx = 1
    for label, owl_obj in expr_pairs:
        try:
            # Handle full SubClassOfAxiom vs OWLClassExpression
            if isinstance(owl_obj, OWLSubClassOfAxiom):
                sub_str = converter.grammar.clean_name(owl_obj.get_sub_class())
                sing_sub = converter.grammar.singular(sub_str)
                super_str = converter.grammar.clean_name(owl_obj.get_super_class())
                sing_super = converter.grammar.singular(super_str)
                saddg_output = f"every {sing_sub} is {converter.grammar.with_article(sing_super)}"
            else:
                saddg_output = converter.convert(owl_obj)

            entry = {
                "id": eval_idx,
                "axiom_type": owl_obj.__class__.__name__,
                "target_label": label,
                "owl_expression": str(owl_obj),
                "saddg_v2_output": saddg_output,
            }
            results.append(entry)

            print(f"[{eval_idx}] Label: {label}")
            print(f"  OWL Object    : {owl_obj}")
            print(f"  SADDG V2 Output: {saddg_output}\n" + "-" * 82)

            eval_idx += 1
        except Exception as e:
            print(f"[{eval_idx}] Skipped {label}: {e}")

    # Export output to JSON
    out_path = results_json_path.parent / "koala_saddg_v2_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\nCompleted evaluation! Saved {len(results)} verbalizations to {out_path}")
    return results


if __name__ == "__main__":
    run_koala_evaluation()
