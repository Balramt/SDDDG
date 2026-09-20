"""
Linguistic utilities, vocabulary constants, and grammar helpers.
Replaces Java's Words.java, English.java, and DBPedia.java.
"""

import re
import inflect


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
    Unified English Grammar & Vocabulary Engine.
    Replaces Java's English.java, IWordLevelGrammar, and DBPedia.java.
    """

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

    @staticmethod
    def clean_iri_fragment(iri_or_str: str) -> str:
        """
        Extract short fragment from IRI and convert CamelCase/snake_case
        to plain English words.
        """
        if not iri_or_str:
            return ""
            
        fragment = str(iri_or_str).split("#")[-1].split("/")[-1]
        clean_text = re.sub(r"(?<=[a-z])(?=[A-Z])|_", " ", fragment).lower()
        return clean_text.strip()