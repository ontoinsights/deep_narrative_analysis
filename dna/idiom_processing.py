# Handles querying the idiom details and returning information on special processing
# Called by create_event_turtle and nlp_sentence_dictionary.py

import os
import pickle

from utilities import base_dir, objects_string

verb_idioms_file = os.path.join(base_dir, 'dna/resources/verb-idioms.pickle')
with open(verb_idioms_file, 'rb') as inFile:
    verb_idiom_dict = pickle.load(inFile)


def determine_processing_be(sentence_text: str, verb_dict: dict) -> list:
    """
    Handle semantic variations of the verb, 'be'.

    :param sentence_text: The full text of the sentence
    :param verb_dict: The dictionary for the verb, 'be' (with prepositions, objects, adverbs, ...)
    :return An array with details on how to render the semantics
    """
    processing = []
    verb_keys = list(verb_dict.keys())
    verb_str = str(verb_dict)
    if 'acomp' in verb_str:
        # Special processing for am/is/was/... + adjectival complement
        # For example, "I am Slavic/angry" => be as the verb lemma + Slavic/angry as the acomp
        # acomp could be an emotion, ethnicity, religion, line of business
        processing = ['+acomp > verb | :has_agent_aspect']
    elif 'with' in verb_str:
        # Get the type of the entity that the subject is 'with'
        with_details = verb_str.split("'with', ")[1].split("'prep_type': '")[1].split("'")[0]
        if with_details.endswith('PERSON'):
            processing = ['pobj > :MeetingAndEncounter & :has_active_agent pobj']
        # TODO: Are other types related using 'with'?
    # TODO: elif 'no way to' in sentence_text:
    elif 'preps' not in verb_keys and objects_string in verb_keys:
        processing = ['dobj > :has_agent_aspect dobj | :Affiliation & :affiliated_with dobj | '
                      ':has_line_of_business dobj']
    return processing


def get_verb_idiom(verb: str, next_word: str) -> (str, list):
    """
    Specific semantics have been defined for idiomatic text, where the text has meaning different
    than the individual words (such as 'fish around' meaning 'search'). This method looks up verb +
    prt (phrasal verb particle) or verb + prep in the verb-idioms dictionary and retrieves the
    semantics.

    :param verb: String holding the verb lemma
    :param next_word: String holding the 'prt' or prepositional text
    :return If special processing is found, return a string identifying the idiom and an array
            specifying how the verb text should be processed (note that there may be more than
            one string - for ex, the processing for a dobj that is an Agent, vs a Resource)
    """
    idiom = f'{verb} {next_word}'
    processing = []
    if idiom in verb_idiom_dict.keys():
        processing.append(verb_idiom_dict[idiom])
    if processing:
        return idiom, processing
    else:
        return '', []


def process_idiom_detail(process: str, sentence_text: str, verb_dict: dict, lemma: str) -> (str, list):
    # TODO: Proprietary; Replace with full code from private repository
    return 'urn:ontology:dna:Idiom', [f'event_uri a :Idiom ; rdfs:label "{process}" .']
