# Handles querying the idiom details and returning information on special processing
# Called by create_event_turtle and nlp_sentence_dictionary.py

import logging
import os
import pickle

from query_ontology_specific_classes import get_norp_emotion_or_enum
from utilities import empty_string, objects_string, resources_root

verb_idioms_file = os.path.join(resources_root, 'verb-idioms.pickle')
with open(verb_idioms_file, 'rb') as inFile:
    verb_idiom_dict = pickle.load(inFile)

nouns_file = os.path.join(resources_root, 'noun-idioms.pickle')
with open(nouns_file, 'rb') as inFile:
    nouns_dict = pickle.load(inFile)

verb_nouns_file = os.path.join(resources_root, 'verb-noun-idioms.pickle')
with open(verb_nouns_file, 'rb') as inFile:
    verb_noun_idiom_dict = pickle.load(inFile)


def determine_processing_be(verb_dict: dict, event_uri: str) -> str:
    """
    Handle semantic variations of the verb, 'be', such as 'being', 'become', 'am', ...

    :param verb_dict: The dictionary for the verb, 'be' (with prepositions, objects, adverbs, ...)
    :param event_uri: String holding the URI/IRI for the event
    :return A string with details on how to render the semantics
    """
    verb_keys = list(verb_dict.keys())
    verb_str = str(verb_dict)
    turtle = empty_string
    # PROPRIETARY; Replace with code from private repository
    return turtle


def get_noun_idiom(noun: str, noun_phrase: str, noun_type: str, sentence: str, noun_uri: str) -> list:
    """
    Specific semantics have been defined for several nouns - as specified by fixes to the knowledge
    graph. This method looks up the input noun in the nouns dictionary and retrieves the
    semantics.

    :param noun: String holding the noun text
    :param noun_phrase: String specifying the complete noun phrase from the original narrative sentence
    :param noun_type: String holding the type of the noun (e.g., 'FEMALESINGPERSON' or 'PLURALNOUN')
    :param sentence: The full text of the sentence (needed for checking for idioms)
    :param noun_uri: String identifying the URI/URL/individual associated with the noun_text
    :return Returns an array of strings defining the Turtle for the noun/noun_phrase
    """
    process_ttl = []
    if noun in nouns_dict.keys():
        processing = nouns_dict[noun]
        if processing:
            noun_dict = {'text': noun, 'type': noun_type}
            process_ttl = process_idiom_detail(processing, sentence, noun_uri, noun_dict)
            process_ttl.append(f'{noun_uri} rdfs:label "{noun_phrase}" .')
            if noun_type.startswith('NEG'):
                process_ttl.append(f'{noun_uri} :negation true .')
    return process_ttl


def get_verb_processing(verb_dict: dict, event_uri: str) -> str:
    """
    Specific semantics have been defined for idiomatic text, where the text has meaning different
    than the individual words (such as 'fish around' meaning 'search'). This method looks up verb +
    acomp or xcomp combinations in the verb-idioms dictionary and retrieves the
    semantics.

    :param verb_dict: Dictionary holding the verb details
    :param event_uri: String holding the URI/IRI for the event
    :return If special processing is found, return the details
    """
    lemma = verb_dict['verb_lemma']
    if lemma in ('be', 'being', 'become', 'becoming'):
        return determine_processing_be(verb_dict, event_uri)
    if lemma in verb_idiom_dict.keys():
        return verb_idiom_dict[lemma]
    for dep in ('acomp', 'ccomp', 'xcomp'):    # TODO: Also check advmod?
        if f'verb_{dep}' in verb_dict.keys():
            processing = get_verb_word_idiom(lemma, verb_dict[f'verb_{dep}'][0]['verb_lemma'])
            return processing
    # TODO: Check verb-noun
    return empty_string


def get_verb_word_idiom(verb: str, word: str) -> str:
    """
    Specific semantics have been defined for idiomatic text, where the text has meaning different
    than the individual words (such as 'fish around' meaning 'search'). This method looks up verb +
    prt (phrasal verb particle) or verb + prep in the verb-idioms dictionary and retrieves the
    semantics.

    :param verb: String holding the verb lemma
    :param word: String holding the word (phrasal verb particle, preposition, ..) if applicable
    :return If special processing is found, return the details
    """
    if f'{verb} {word}' in verb_idiom_dict.keys():
        return verb_idiom_dict[f'{verb} {word}']
    elif f"{verb} '{word}'" in verb_idiom_dict.keys():
        return verb_idiom_dict[f"{verb} '{word}'"]
    return empty_string


def process_idiom_detail(processing: str, sentence_text: str, inst_uri: str, term_dict: dict) -> list:
    """
    Translate the processing string into Turtle, which may require the sentence_dictionary to get info
    such as the sentence object, preposition object, subject, ... An example of a processing string is
    '+acomp > EmotionalResponse verb | :has_agent_aspect NORP' which indicates that if an adjectival
    complement is present in the sentence, and its text is a kind of EmotionalResponse, then that Response
    verb is the Event in the sentence and processing is complete. Or, if the adjectival complement is a
    NORP (nationality, religion or other org), then the subject of the sentence is related to that NORP
    via the :has_agent_aspect predicate.

    :param processing: A string holding the possible processing 'rules'/idioms
    :param sentence_text: String holding the complete sentence text
    :param inst_uri: String holding the URI identifying the instance (a noun or an EventAndState)
    :param term_dict: Either a noun dictionary () or a verb dictionary (which is described
    :return An array holding the individual Turtle statements for the processing
    """
    logging.info(f'Processing the idiom string, {processing}, for the sentence, {sentence_text}')
    ttl_list = []
    preposition = empty_string
    # If this rule is related to a preposition, then that preposition will come first (prefixed by "prep_")
    if processing.startswith("prep_"):
        # Looking for the details of a preposition
        preposition = processing[5:processing.index(" ")]
    if '(' in processing:   # Alternatives are defined within right/left parentheses which are separated by "|"
        # Ignore whatever is before the first parentheses since it is nothing or the preposition captured above
        process_strs = processing.split('(')[1:]
    else:
        process_strs = [processing]   # No alternatives
    # Process all the individual strings, looking for a match
    # Once a match is found, we are finished since the processing rules should be ordered from specific to default
    for process_str in process_strs:
        process_text = process_str.replace(')', empty_string).replace('|', empty_string)
        if preposition and preposition in sentence_text:
            ttl_list.append(f'{inst_uri} a :NeedPrep ; rdfs:label "{preposition}" .')  # TODO
            ttl_list.append(f'{inst_uri} a :InvestigatePobj ; rdfs:label "process_text" .')   # TODO
            break  # Exit for loop to clean up the rule
        if process_text.startswith('subj_uri') or process_text.startswith(':Event'):
            # Processing details are a complete Turtle statement
            ttl_list.append(process_text)
            break
        if process_text.startswith('inst_uri'):
            # Details are just about the inst_uri
            ttl_list.append(f'{process_text.replace("inst_uri", inst_uri)} .')
            break
        if process_text.startswith('default > '):
            # Default processing is a class name and does not depend on direct or prepositional objects
            process_detail = process_text.split('> ')[1]
            ttl_list.append(f'{inst_uri} a {process_detail.split("> ")[1]} .')
            break
        if process_text.startswith(':'):
            # Processing is a reference to 1+ noun or verb classes
            if 'type' in term_dict.keys() and 'PLURAL' in term_dict['type']:
                ttl_list.append(f'{inst_uri} a {process_str} . {inst_uri} a :Collection .')
            else:
                ttl_list.append(f'{inst_uri} a {process_str} .')
            break
        if process_text.startswith("'"):
            # Opening text is a specific word that should be found in the sentence
            ref_word = process_text[1:process_text.index(f"'")]
            if ref_word in sentence_text:
                process_detail = process_text.split('> ')[1]
                if process_detail.startswith('inst_uri'):
                    ttl_list.append(f'{process_detail.replace("inst_uri", inst_uri)} .')
                elif process_detail.startswith(':'):
                    ttl_list.append(f'{inst_uri} a {process_detail} .')
                break
        # if process_text.startswith('dobj'):   PROPRIETARY
        # if process_text.startswith('pobj'):   PROPRIETARY
        # if process_text.startswith(Plant, Person, Agent, Resource)     PROPRIETARY
    if not ttl_list:
        return [f'{inst_uri} a owl:Thing .']
    return ttl_list
