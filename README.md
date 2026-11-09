```markdown
# SADDG: Syntax-Aware Dynamic Dependency Graph for OWL2NL

Welcome to the **SADDG** (Syntax-Aware Dynamic Dependency Graph) framework. This project is an advanced Natural Language Generation (NLG) engine designed to verbalize formal Description Logic (OWL) axioms into fluent, grammatically correct English. 

Developed as part of research at the **DICE Group (Paderborn University)**, this engine is currently in its initial phase but already demonstrates state-of-the-art potential by solving the limitations of traditional string-aggregation methods.

---

## 🧠 The Core Engine (How It Works)
Traditional OWL-to-text systems (like LD2NL) rely on "bottom-up" string concatenation. When class expressions become heavily nested (e.g., intersections of multiple restrictions), naive string concatenation creates fragmented, robotic, and grammatically incorrect sentences.

**SADDG V2** solves this by using a **Deep Syntactic Graph (DSyntG)** approach:
1. **Tree Parsing & Normalization:** It flattens complex binary intersections into clean, N-ary lists.
2. **Graph-Level Micro-Planning:** Instead of blindly merging strings, the engine builds a dependency graph of subjects, verbs, and objects.
3. **Top-Down Feature Propagation:** It calculates linguistic features (pluralization, human vs. non-human pronouns like "who" vs. "that", and active/passive verb frames) *before* generating the final text. 

### 🔗 Key Architecture Files (Click to View Code)
* **[The Main Engine (`saddg_v2.py`)](src/verbalizer/owl2nl/converters/saddg_v2.py)**: The brain of the project. This file contains the `SADDG_V2` class, which handles the graph construction, feature propagation, and final surface realization of the OWL axioms.
* **[Grammar & Vocabulary (`grammar.py`)](src/verbalizer/common/grammar.py)**: Contains the linguistic rules, irregular plural mappings, and property frame classifiers (detecting if a property is an active verb, passive verb, or relational noun).
* **[Benchmark Evaluator (`benchmark_evaluator.py`)](src/verbalizer/owl2nl/evaluations/benchmark_evaluator.py)**: The scoring script that evaluates SADDG's outputs against the LD2NL paper baseline using linguistic heuristics and NLTK-based lexical similarity metrics.

---

## 🌍 A Real-World Example
SADDG takes a formal OWL expression as input and translates it directly into fluent natural language. Here is how it handles a complex, nested restriction:

**1. Pass the OWL Expression to the Engine:**
```python
# The machine-readable OWL axiom
axiom = OWLSubClassOfAxiom(
  sub_class=OWLClass(IRI('#Koala')),
  super_class=OWLObjectSomeValuesFrom(
    property=OWLObjectProperty(IRI('#hasHabitat')),
    filler=OWLClass(IRI('#DryEucalyptForest'))
  )
)

# Translate it into natural language
natural_language_text = engine.verbalize(axiom)
print(natural_language_text)

```

**2. The Translation Output:**

* **Traditional/Naive Output (Bottom-Up):**
> *"Every koala is a thing and has habitat some dry eucalypt forest."* ❌ (Fragmented, unnatural)


* **SADDG V2 Output (Graph-Based):**
> *"Every koala has a habitat that is a dry eucalypt forest."* ✅ (Fluent, grammatically accurate)



---

## 📊 Current Status & Benchmarks

The engine is currently being benchmarked against the **Koala Ontology** (36 core logical expressions).

Based on our heuristic evaluation script (which estimates the human-rating metrics defined in the LD2NL 2019 framework):

* **Adequacy:** `5.0 / 5.0` *(LD2NL Baseline: 4.40)*
* **Fluency:** `5.0 / 5.0` *(LD2NL Baseline: 4.38)*

---

## 🚀 Getting Started

### Prerequisites

* Python 3.10+
* Conda environment recommended (`verbalizer`)
* Dependencies: `owlapy`, `inflect`, `nltk`, `numpy`

### Running the Project

**1. Generate English sentences from the Koala Ontology:**

```bash
python src/verbalizer/owl2nl/evaluations/evaluate_koala_engine2.py

```

*(This will generate `koala_engine2_results.json` in the results folder).*

**2. Run the Evaluation Benchmark:**

```bash
python src/verbalizer/owl2nl/evaluations/benchmark_evaluator.py

```

*(This calculates the Adequacy/Fluency heuristics and compares them to the LD2NL baseline).*

```