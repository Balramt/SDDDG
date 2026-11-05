"""
Dynamic Property Subcategorization Frame Classifier.
Uses spaCy Part-of-Speech (POS) tagging to classify object/data properties 
into formal linguistic subcategorization frames without hardcoded lists.
"""

from typing import Dict, Any, Optional
import spacy

from verbalizer.common.grammar import EnglishGrammar, LinguisticContext
from verbalizer.owl2nl.converters.dsyntg import FrameType

# Load spaCy model safely with fallback handling
try:
    _NLP = spacy.load("en_core_web_sm")
except Exception:
    _NLP = None


class PropertyFrameClassifier:
    """
    Classifies OWL Object/Data properties into universal linguistic frames:
    - VERB_ACTIVE: Active verb constructions ("who leads")
    - PASSIVE_PP: Passive/Prepositional constructions ("that is located in")
    - RNP: Relational Noun Phrases ("whose age is")
    - ATTRIBUTIVE: Data attributes
    """

    def __init__(self, grammar: EnglishGrammar):
        self.grammar = grammar
        self.nlp = _NLP

    def classify_property(self, label: str, ctx: LinguisticContext) -> Dict[str, Any]:
        """
        Dynamically inspects property POS tags and maps to a FrameType dict.
        """
        clean_label = self.grammar.clean_iri_fragment(label)
        words = clean_label.split()

        if not words:
            return {
                "type": FrameType.VERB_ACTIVE,
                "phrase": clean_label,
                "rel_clause_prefix": f"{ctx.relative_pronoun()} {clean_label}",
            }

        copula = ctx.copula()
        rel_pronoun = ctx.relative_pronoun()
        first_word = words[0].lower()
        last_word = words[-1].lower()

        # Handle 'has' / 'have' + Noun pattern (e.g. 'hasAge' -> 'age', 'hasChild' -> 'child')
        if first_word in ("has", "have") and len(words) > 1:
            remainder = " ".join(words[1:])
            # If remainder ends with a preposition, treat as passive (e.g. 'hasPartIn')
            if last_word in self.grammar.PREPOSITIONS:
                return {
                    "type": FrameType.PASSIVE_PP,
                    "phrase": clean_label,
                    "rel_clause_prefix": f"{rel_pronoun} {copula} {remainder}",
                }
            return {
                "type": FrameType.RNP,
                "phrase": remainder,
                "rel_clause_prefix": f"whose {remainder} is",
            }

        # spaCy POS Tagging analysis if model is available
        if self.nlp:
            doc = self.nlp(clean_label)
            last_token = doc[-1]
            first_token = doc[0]

            # Rule 1: Ends with Preposition (ADP) or Passive Verb -> PASSIVE_PP
            if last_token.pos_ in ("ADP", "PART") or last_token.tag_ == "VBN":
                return {
                    "type": FrameType.PASSIVE_PP,
                    "phrase": clean_label,
                    "rel_clause_prefix": f"{rel_pronoun} {copula} {clean_label}",
                }

            # Rule 2: Starts with Verb -> VERB_ACTIVE
            if first_token.pos_ in ("VERB", "AUX"):
                adjusted_verb = self.grammar.adjust_verb_agreement(clean_label, ctx.is_plural)
                return {
                    "type": FrameType.VERB_ACTIVE,
                    "phrase": adjusted_verb,
                    "rel_clause_prefix": f"{rel_pronoun} {adjusted_verb}",
                }

        # Fallback POS checks if spaCy is unavailable
        if last_word in self.grammar.PREPOSITIONS or last_word.endswith("ed"):
            return {
                "type": FrameType.PASSIVE_PP,
                "phrase": clean_label,
                "rel_clause_prefix": f"{rel_pronoun} {copula} {clean_label}",
            }

        if self.grammar.is_verb_headed(clean_label):
            adjusted_verb = self.grammar.adjust_verb_agreement(clean_label, ctx.is_plural)
            return {
                "type": FrameType.VERB_ACTIVE,
                "phrase": adjusted_verb,
                "rel_clause_prefix": f"{rel_pronoun} {adjusted_verb}",
            }

        # Default Frame: Relational Noun Phrase
        return {
            "type": FrameType.RNP,
            "phrase": clean_label,
            "rel_clause_prefix": f"whose {clean_label} is",
        }