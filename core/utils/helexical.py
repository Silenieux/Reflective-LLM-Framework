# /core/utils/helexical.py

import spacy
from typing import List, Dict

# Load small English model
nlp = spacy.load("en_core_web_sm")

def get_lexical_types(text: str) -> List[Dict[str, str]]:
    """
    Analyze input text and return lexical typing information.
    Each token includes its text, lemma, part-of-speech, syntactic tag,
    dependency role, and the word it depends on.
    """
    doc = nlp(text)
    result = []
    for token in doc:
        result.append({
            "text": token.text,
            "lemma": token.lemma_,
            "pos": token.pos_,       # e.g., NOUN, VERB, ADJ
            "tag": token.tag_,       # e.g., NN, VBD
            "dep": token.dep_,       # e.g., nsubj, dobj
            "head": token.head.text  # e.g., what word this depends on
        })
    return result