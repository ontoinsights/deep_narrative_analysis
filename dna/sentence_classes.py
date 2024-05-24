# Sentence class structure for output from NLP analysis

import uuid
from enum import Enum

from dna.utilities_and_language_specific import empty_string


class Sentence:
    """
    Class holding sentence details from the NLP processing
    """
    text: str = empty_string       # Sentence text
    offset: int = 1                # Offset of the sentence within the narrative/article (starting with 1)
    entities: list = []            # List of the Entity Class instances from NER processing
    punctuations: list = []        # List of enumerated values indicating the punctuation in the sentence
    verbs: list = []               # List of root and clausal verbs (strings) in the sentence
    iri: str = empty_string        # Sentence IRI (in resulting Turtle)

    def __init__(self, text: str, offset: int, entities: list, punctuations: list, verbs: list):
        self.text = text
        self.offset = offset
        self.entities = entities
        self.punctuations = punctuations
        self.verbs = verbs
        self.iri = f':Sentence_{str(uuid.uuid4())[:13]}'


class Quotation(Sentence):
    """
    Extension of the Sentence Class to hold attribution details for a quotation
    """
    attribution: str = empty_string      # Speaker attribution

    def __init__(self, text: str, offset: int, entities: list, punctuations: list, verbs: list, attribution: str):
        super(Quotation, self).__init__(text, offset, entities, punctuations, verbs)
        self.attribution = attribution
        self.iri = f':Quotation{str(offset)}'


class Entity:
    """
    Class holding the details of "named entities" found in a sentence/quotation
    """
    text: str = empty_string      # Entity's text
    ner_type: str = empty_string  # NER type as defined by spaCy (PERSON, NORP, GPE, LOC, ...)

    def __init__(self, text: str, ner_type: str):
        self.text = text
        self.ner_type = ner_type


class Punctuation(Enum):
    QUESTION = 1
    EXCLAMATION = 2
