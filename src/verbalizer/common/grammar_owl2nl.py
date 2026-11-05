# """
# OWL2NL-specific linguistic utilities and grammar handlers.
# """

# import re
# from verbalizer.common.grammar import EnglishGrammar, LinguisticContext, Words


# class OWL2NLGrammar(EnglishGrammar):
#     """
#     Extends base EnglishGrammar with specific handling for Description Logic (DL) constructs.
#     """

#     @staticmethod
#     def is_owl_thing(expr) -> bool:
#         """Checks if expression or string represents owl:Thing / top concept."""
#         if expr is None:
#             return True
#         if hasattr(expr, "is_owl_thing"):
#             return expr.is_owl_thing()
#         if hasattr(expr, "is_anonymous") and not expr.is_anonymous():
#             if hasattr(expr, "iri") and "Thing" in str(expr.iri):
#                 return True
#         expr_str = str(expr).lower()
#         return "owl#thing" in expr_str or expr_str.endswith("thing") or expr_str == "thing"

#     @staticmethod
#     def extract_iri_fragment(owl_obj) -> str:
#         """Safely extracts the clean local name fragment from any owlapy object or IRI."""
#         if owl_obj is None:
#             return ""

#         if hasattr(owl_obj, "iri"):
#             iri_obj = owl_obj.iri
#             if hasattr(iri_obj, "remainder") and iri_obj.remainder:
#                 return str(iri_obj.remainder)
#             if hasattr(iri_obj, "to_string_id"):
#                 raw_str = iri_obj.to_string_id()
#                 return raw_str.split("#")[-1].split("/")[-1]

#         raw = str(owl_obj)
#         quoted_tokens = re.findall(r"'([^']+)'", raw)
#         if quoted_tokens:
#             raw = quoted_tokens[-1]
        
#         return raw.split("#")[-1].split("/")[-1]

#     def clean_name(self, owl_obj) -> str:
#         """Extracts fragment and formats it with proper spaces."""
#         fragment = self.extract_iri_fragment(owl_obj)
#         if fragment.isupper():
#             return fragment
#         clean_text = re.sub(r"(?<=[a-z])(?=[A-Z])|_", " ", fragment).lower()
#         return clean_text.strip()

#     def clean_property_name(self, prop_obj) -> str:
#         """Extracts property fragment and strips leading 'has'/'is' prefixes for clean possessives."""
#         clean = self.clean_name(prop_obj)
#         clean_no_has = re.sub(r"^(has|is)\s+", "", clean, flags=re.IGNORECASE).strip()
#         return clean_no_has if clean_no_has else clean

#     def format_individual_name(self, ind) -> str:
#         """Extracts individual IRI remainder as short clean label (e.g. 'PhD', 'female')."""
#         fragment = self.extract_iri_fragment(ind)
#         if fragment in {"BA", "BS", "MA", "PhD"}:
#             return fragment
#         return self.clean_name(ind)

#     def extract_property_head_noun(self, prop_obj) -> str:
#         """Extracts and pluralizes noun from property (e.g., 'hasChildren' -> 'children', 'hasHabitat' -> 'habitats')."""
#         clean_prop = self.clean_property_name(prop_obj)
#         words = clean_prop.split()
#         if not words:
#             return "items"

#         head_word = words[-1]
#         # Prevent double pluralization on already pluralized irregulars like 'children'
#         if head_word.lower() == "children":
#             plural_head = "children"
#         else:
#             plural_head = self.plural(head_word)

#         if len(words) > 1:
#             return f"{' '.join(words[:-1])} {plural_head}"
#         return plural_head

#     def format_data_value(self, prop_obj, literal_val: str) -> str:
#         """Formats DataHasValue expressions (e.g. boolean properties)."""
#         prop_clean = self.clean_property_name(prop_obj)
#         val_str = str(literal_val).lower()

#         if val_str == "true":
#             return f"is {prop_clean}"
#         elif val_str == "false":
#             return f"is not {prop_clean}"
#         return f"{prop_clean} is {literal_val}"


"""
Linguistic Grammar & Surface Realization Utilities for SADDG OWL2NL Engine.
"""

import re
from dataclasses import dataclass
from typing import Any


@dataclass
class LinguisticContext:
    """Tracks contextual state during graph linearization."""
    is_plural: bool = True
    is_human: bool = False

    def relative_pronoun(self) -> str:
        return "who" if self.is_human else "that"


class OWL2NLGrammar:
    """
    Grammar rules, string cleaning, pluralization, and surface realization
    for converting Description Logic primitives into natural English.
    """

    def clean_name(self, owl_obj: Any) -> str:
        """Extracts readable fragment/label from an OWL entity or string representation."""
        if hasattr(owl_obj, "str"):
            s = owl_obj.str
        elif hasattr(owl_obj, "to_string_id"):
            s = owl_obj.to_string_id()
        else:
            s = str(owl_obj)

        if "#" in s:
            s = s.split("#")[-1]
        elif "/" in s:
            s = s.split("/")[-1]

        # Strip surrounding quotes or IRI markers
        s = s.strip("<>'\"")

        # Split CamelCase into spaced words (e.g., MaleStudentWith3Daughters -> Male Student With 3 Daughters)
        s = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", s)
        s = re.sub(r"(?<=[A-Z])(?=[A-Z][a-z])", " ", s)

        return s.lower().strip()

    def clean_property_name(self, prop_obj: Any) -> str:
        """Cleans property IRIs into natural verbal phrases."""
        raw = self.clean_name(prop_obj)

        # Standard prefix removals
        if raw.startswith("has "):
            raw = raw[4:]
        elif raw.startswith("is "):
            raw = raw[3:]

        return raw.strip()

    def extract_property_head_noun(self, prop_obj: Any) -> str:
        """Extracts the head noun from a property phrase (e.g., 'hasChildren' -> 'children')."""
        clean_prop = self.clean_property_name(prop_obj)
        tokens = clean_prop.split()
        return tokens[-1] if tokens else clean_prop

    def singular(self, word: str) -> str:
        """Naive singularization helper for domain concepts."""
        w = word.strip()
        w_lower = w.lower()

        irregular = {
            "children": "child",
            "people": "person",
            "degrees": "degree",
            "genders": "gender",
            "marsupials": "marsupial",
            "koalas": "koala",
            "quokkas": "quokka",
            "students": "student",
            "animals": "animal",
            "forests": "forest",
            "habitats": "habitat",
            "universities": "university",
        }

        if w_lower in irregular:
            return irregular[w_lower]

        if w_lower.endswith("ies") and len(w_lower) > 3:
            return w[:-3] + "y"
        if w_lower.endswith("es") and len(w_lower) > 2 and not w_lower.endswith("tes"):
            return w[:-2]
        if w_lower.endswith("s") and not w_lower.endswith("ss") and len(w_lower) > 1:
            return w[:-1]

        return w

    def plural(self, word: str) -> str:
        """Naive pluralization helper for domain concepts."""
        w = word.strip()
        w_lower = w.lower()

        irregular = {
            "child": "children",
            "person": "people",
            "degree": "degrees",
            "gender": "genders",
            "marsupial": "marsupials",
            "quokka": "quokkas",
            "koala": "koalas",
            "student": "students",
            "animal": "animals",
            "forest": "forests",
            "habitat": "habitats",
            "university": "universities",
        }

        if w_lower in irregular:
            return irregular[w_lower]

        if w_lower.endswith("y") and len(w_lower) > 1 and w_lower[-2] not in "aeiou":
            return w[:-1] + "ies"
        if w_lower.endswith(("s", "sh", "ch", "x", "z")):
            return w + "es"

        return w + "s"

    def with_article(self, word: str) -> str:
        """Adds indefinte article ('a' or 'an') based on leading phonetics."""
        w = word.strip()
        if not w:
            return ""

        first_char = w[0].lower()
        if first_char in "aeiou":
            return f"an {w}"
        return f"a {w}"

    def format_individual_name(self, ind_obj: Any) -> str:
        """Formats individual names (e.g. 'female', 'PhD', 'BA')."""
        s = self.clean_name(ind_obj)
        # Preserve capitalization for short degree abbreviations
        if len(s) <= 3:
            return s.upper()
        return s

    def format_data_value(self, prop_name: str, val: str) -> str:
        """Formats data literal values (handles booleans cleanly)."""
        clean_prop = self.clean_property_name(prop_name)
        val_lower = str(val).strip().lower()

        if val_lower in ["true", "1"]:
            return f"is {clean_prop}"
        elif val_lower in ["false", "0"]:
            return f"is not {clean_prop}"
        else:
            return f"{clean_prop} is {val}"

    def is_human(self, word: str) -> bool:
        """Detects human domain concepts for relative pronoun selection ('who' vs 'that')."""
        w = word.lower()
        human_terms = ["person", "people", "student", "students", "parent", "parents", "graduate student"]
        return any(term in w for term in human_terms)

    def is_owl_thing(self, obj: Any) -> bool:
        """Checks if an object or string corresponds to owl:Thing."""
        s = str(obj).lower()
        return "thing" in s or "owl#thing" in s

    def number(self, val: int) -> str:
        """Converts integer digits to English word numerals."""
        words = {
            0: "zero",
            1: "one",
            2: "two",
            3: "three",
            4: "four",
            5: "five",
            6: "six",
            7: "seven",
            8: "eight",
            9: "nine",
            10: "ten",
        }
        return words.get(val, str(val))