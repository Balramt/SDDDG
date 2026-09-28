"""
Linguistic utilities, vocabulary constants, and grammar helpers.
Replaces Java's Words.java, English.java, and DBPedia.java.
Provides feature propagation context and Part-Of-Speech (POS) property framing.
"""

from dataclasses import dataclass
import re
from typing import Optional
import inflect


@dataclass
class LinguisticContext:
    """
    Syntactic feature context passed down during AST traversal
    for top-down agreement and feature propagation.
    """
    is_plural: bool = True
    is_filler: bool = False
    person: int = 3
    is_human: bool = False

    def copula(self) -> str:
        """Returns 'are' if plural, otherwise 'is'."""
        return "are" if self.is_plural else "is"

    def relative_pronoun(self) -> str:
        """Returns 'who' if human/person, otherwise 'that'."""
        return "who" if self.is_human else "that"


class Words:
    """Vocabulary constants for Controlled Natural Language (Replaces Words.java)."""
    A = "a"
    AN = "an"
    AND = "and"
    OR = "or"
    NOT = "not"
    EVERY = "every"
    EVERYTHING = "everything"
    EXACTLY = "exactly"
    AT_LEAST = "at least"
    AT_MOST = "at most"
    HAS = "has"
    IS_A_TYPE_OF = "is a type of"
    IS_DEFINED_AS = "is defined as"
    PAIRWISE_DISJOINT = "pairwise disjoint"
    WHO = "who"
    THAT = "that"

    @staticmethod
    def number_to_word(val: int) -> str:
        """Converts digits 1-9 to words (1 -> 'one', 10 -> '10')."""
        words = {
            1: "one", 2: "two", 3: "three", 4: "four", 5: "five",
            6: "six", 7: "seven", 8: "eight", 9: "nine"
        }
        return words.get(val, str(val))


class EnglishGrammar:
    """
    Unified English Grammar & Vocabulary Engine with POS classification,
    feature propagation support, and irregular verb handling.
    """

    HUMAN_NOUNS = {
        "person", "people", "student", "students", "doctor", "doctors",
        "professor", "professors", "teacher", "teachers", "engineer", "engineers",
        "author", "authors", "researcher", "researchers", "child", "children",
        "parent", "parents", "employee", "employees", "user", "users"
    }

    PAST_TENSE_VERBS = {
        "wrote", "built", "created", "led", "taught", "directed",
        "managed", "designed", "published", "manufactured", "founded"
    }

    PREPOSITIONS = {
        "in", "at", "by", "from", "of", "to", "with", "on", "for",
        "about", "through", "over", "under"
    }

    def __init__(self):
        self._engine = inflect.engine()

    def plural(self, word: str) -> str:
        """Return plural form of a noun."""
        res = self._engine.plural(word)
        return res if res else word

    def singular(self, word: str) -> str:
        """Return singular form of a noun."""
        res = self._engine.singular_noun(word)
        return res if res else word

    def with_article(self, word: str) -> str:
        """Prepend 'a' or 'an' based on phonetics."""
        return self._engine.a(word)

    def number(self, val: int) -> str:
        """Format number (1 -> 'one', 12 -> '12')."""
        return Words.number_to_word(val)

    def is_human(self, noun: str) -> bool:
        """Checks if a noun concept explicitly refers to a human entity."""
        clean = noun.lower().strip()
        return clean in self.HUMAN_NOUNS or self.singular(clean) in self.HUMAN_NOUNS

    def adjust_verb_agreement(self, verb_phrase: str, is_plural: bool) -> str:
        """
        Adjusts present tense active verbs for subject agreement.
        e.g., if is_plural=True: 'teaches' -> 'teach', 'leads' -> 'lead'.
        Past tense verbs like 'wrote' or 'built' remain unchanged.
        """
        words = verb_phrase.strip().split()
        if not words:
            return verb_phrase

        first_word = words[0]
        if first_word in self.PAST_TENSE_VERBS:
            return verb_phrase

        if is_plural:
            if first_word.endswith("ies"):
                base = first_word[:-3] + "y"
            elif first_word.endswith("es") and len(first_word) > 3:
                base = first_word[:-2]
            elif first_word.endswith("s") and not first_word.endswith("ss"):
                base = first_word[:-1]
            else:
                base = first_word
            return " ".join([base] + words[1:])
        return verb_phrase

    def extract_head_noun_plural(self, property_label: str) -> str:
        """Extracts and pluralizes head noun from property (e.g. 'has child' -> 'children')."""
        clean = self.clean_iri_fragment(property_label)
        clean = re.sub(r"^has\s+", "", clean, flags=re.IGNORECASE).strip()
        words = clean.split()
        if not words:
            return "items"

        head_word = words[-1]
        plural_head = self.plural(head_word)
        if len(words) > 1:
            return f"{' '.join(words[:-1])} {plural_head}"
        return plural_head

    def is_verb_headed(self, property_label: str) -> bool:
        """Detects if property label is headed by an active verb."""
        words = property_label.strip().lower().split()
        if not words:
            return False

        first_word = words[0]
        if first_word in self.PAST_TENSE_VERBS:
            return True
        if re.match(r"^[a-z]+s$", first_word) and not first_word.endswith("ss"):
            return True
            return False

    @staticmethod
    def clean_iri_fragment(iri_or_str: str) -> str:
        """Extract short fragment from IRI and clean case formatting."""
        if not iri_or_str:
            return ""

        fragment = str(iri_or_str).split("#")[-1].split("/")[-1]
        if fragment.isupper():
            return fragment

        clean_text = re.sub(r"(?<=[a-z])(?=[A-Z])|_", " ", fragment).lower()
        return clean_text.strip()