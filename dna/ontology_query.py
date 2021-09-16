# Query ontology class details
# To avoid passing a store name parameter, the ontology files are pre-loaded into an 'ontologies' database
# Called by create_event_turtle.py

import logging
from PyDictionary import PyDictionary

from database import query_database
from idiom_processing import process_idiom_detail
from nlp import get_named_entity_in_string, get_noun
from utilities import empty_string, event_and_state, owl_thing, processed_prepositions

dictionary = PyDictionary()

explicit_plural = ('group', 'people')
part_of_group = ('member', 'group', 'citizen', 'people', 'affiliate', 'representative', 'associate', 'comrade')

ontologies_database = 'ontologies'

query_event1 = 'prefix : <urn:ontoinsights:dna:> SELECT ?class ?prob WHERE ' \
               '{ { { ?class :verb_synonym ?vsyn . FILTER(?vsyn = "keyword") . BIND(100 as ?prob) } UNION ' \
               '{ ?class :noun_synonym ?nsyn . FILTER(?nsyn = "keyword") . BIND(90 as ?prob) } } ' \
               '?class rdfs:subClassOf+ :EventAndState } ORDER BY DESC(?prob)'

query_noun1 = 'prefix : <urn:ontoinsights:dna:> SELECT ?class WHERE ' \
               '{ ?class :noun_synonym ?nsyn . FILTER(?nsyn = "keyword") . ' \
              'FILTER NOT EXISTS { ?class rdfs:subClassOf+ :EventAndState } ' \
              'FILTER NOT EXISTS { ?class rdfs:subClassOf+ :Enumeration } }'

query_event2 = 'prefix : <urn:ontoinsights:dna:> SELECT ?class ?prob WHERE ' \
               '{ { { ?class :verb_synonym ?vsyn . FILTER(CONTAINS(?vsyn, "keyword")) . BIND(75 as ?prob) } UNION ' \
               '{ ?class :noun_synonym ?nsyn . FILTER(CONTAINS(?nsyn, "keyword")) . BIND(65 as ?prob) } UNION ' \
               '{ ?class rdfs:label ?label . FILTER(CONTAINS(lcase(?label), "keyword")) . BIND(55 as ?prob) } UNION ' \
               '{ ?class :example ?ex . FILTER(CONTAINS(?ex, "keyword")) . BIND(65 as ?prob) } } ' \
               '?class rdfs:subClassOf+ :EventAndState } ORDER BY DESC(?prob)'

query_noun2 = 'prefix : <urn:ontoinsights:dna:> SELECT ?class ?prob WHERE ' \
               '{ { { ?class :noun_synonym ?nsyn . FILTER(CONTAINS(?nsyn, "keyword")) . BIND(65 as ?prob) } UNION ' \
               '{ ?class rdfs:label ?label . FILTER(CONTAINS(lcase(?label), "keyword")) . BIND(65 as ?prob) } UNION ' \
               '{ ?class :example ?ex . FILTER(CONTAINS(?ex, "keyword")) . BIND(65 as ?prob) } } ' \
               'FILTER NOT EXISTS { ?class rdfs:subClassOf+ :EventAndState } ' \
               'FILTER NOT EXISTS { ?class rdfs:subClassOf+ :Enumeration } } ORDER BY DESC(?prob)'

query_event3 = 'prefix : <urn:ontoinsights:dna:> SELECT ?class ?prob WHERE ' \
               '{ { { ?class :verb_synonym ?vsyn . FILTER(CONTAINS("keyword", ?vsyn)) . BIND(50 as ?prob) } UNION ' \
               '{ ?class :noun_synonym ?nsyn . FILTER(CONTAINS("keyword", ?nsyn)) . BIND(40 as ?prob) } } ' \
               '?class rdfs:subClassOf+ :EventAndState } ORDER BY DESC(?prob)'

query_noun3 = 'prefix : <urn:ontoinsights:dna:> SELECT ?class WHERE ' \
              '{ ?class :noun_synonym ?nsyn . FILTER(CONTAINS("keyword", ?nsyn)) . ' \
              'FILTER NOT EXISTS { ?class rdfs:subClassOf+ :EventAndState } ' \
              'FILTER NOT EXISTS { ?class rdfs:subClassOf+ :Enumeration } }'


def create_affiliation_ttl(noun_uri: str, affiliated_text: str, affiliated_type: str) -> list:
    """
    Creates the Turtle for an Affiliation.

    :param noun_uri: String holding the entity/URI to be affiliated
    :param affiliated_text: String specifying the entity (organization, group, etc.) to which the
                            noun is affiliated
    :param affiliated_type: String specifying the class type of the entity
    :return An array of strings holding the Turtle representation of the Affiliation
    """
    affiliated_uri = f':{affiliated_text.replace(" ", "_")}'
    ttl = [f'{noun_uri}{affiliated_text.replace(" ", "_")}Affiliation a :Affiliation ; ',
           f'  :affiliated_with {affiliated_uri} ; :affiliated_agent {noun_uri} . ',
           f'{affiliated_uri} a {affiliated_type} ; rdfs:label "{affiliated_text}" ; '
           f':definition "Insert from Wikidata" .']  # TODO: Get definition of org from Wikidata
    return ttl


def check_dictionary(word: str, is_noun: bool) -> str:
    """
    Check dictionary for an unmapped term and see if a mapping can be created.

    :param word: The term to be mapped
    :param is_noun: Boolean indicating if the word/term is a noun
    :return String holding the concept's class name
    """
    try:
        word_def = dictionary.meaning(word, disable_errors=True)
        if word_def:
            term_type = 'Verb'
            if is_noun:
                term_type = 'Noun'
            if term_type in word_def.keys():
                for clause in word_def[term_type]:
                    for sub_clause in clause.split(';'):
                        if is_noun:
                            noun = get_noun(sub_clause, True)
                            class_name = _query_ontology(noun, query_noun1, query_noun2, query_noun3)
                        else:
                            verb = sub_clause.split(' ')[0]
                            class_name = _query_ontology(verb, query_event1, query_event2, query_event3)
                        if class_name != owl_thing and class_name != event_and_state:
                            return class_name
    finally:
        return owl_thing if is_noun else event_and_state


def check_text(text: str, words: tuple) -> bool:
    """
    Determines if one of the 'words' in the input tuple is found in the 'text' string. Returns
    True if so.

    :param text: The string to be checked
    :param words: A tuple holding words to be searched for
    :return True if one of the 'words' is found in the 'text; False otherwise
    """
    for word in words:
        if word in text:
            return True
    return False


def find_noun_class(noun_uri: str, noun_text: str, noun_type: str) -> (str, []):
    """
    Determine the appropriate class in the DNA ontology, that matches the semantics of the noun_text.

    :param noun_uri: String specifying the URI/URL/individual associated with the noun_text
    :param noun_text: String specifying the noun
    :param noun_type: String holding the type of the noun (e.g., 'FEMALESINGPERSON' or 'PLURALNOUN')
    :return Mapping of the semantics to a DNA ontology class; Also if the mapping is to a GroupOfAgents
            AND the agents are affiliated with a Person, Organization, GPE, etc. then the Turtle details
            of the affiliation are returned (as an array of strings)
    """
    class_name = empty_string
    noun = empty_string
    affiliation_ttl = []
    if 'SINGPERSON' in noun_type or noun_text == 'Narrator':
        class_name = 'urn:ontoinsights:dna:Person'
    elif 'PLURALPERSON' in noun_type:
        class_name = 'urn:ontoinsights:dna:GroupOfAgents'
    elif noun_type.endswith('GPE'):
        class_name = 'urn:ontoinsights:dna:GeopoliticalEntity'
    elif noun_type.endswith('ORG') or noun_type.endswith('NORP'):
        class_name = 'urn:ontoinsights:dna:Organization'
    else:
        found_prep = False
        for prep in processed_prepositions:
            found_prep = (True if noun_text.lower().startswith(f'{prep} ') else False) or \
                         (True if f' {prep} ' in noun_text.lower() else False)
            if found_prep:
                break
        if found_prep:
            # TODO: Improve coverage
            if check_text(noun_text, part_of_group):  # May be a reference to members of an org, group, ...
                if 'PLURAL' in noun_type or check_text(noun_text, explicit_plural):
                    class_name = 'urn:ontoinsights:dna:GroupOfAgents'
                else:
                    class_name = 'urn:ontoinsights:dna:Person'
                # Check if the org, group, ... is mentioned
                if ' of ' in noun_text or ' in ' in noun_text or ' from ' in noun_text:
                    agent_text, agent_type = get_named_entity_in_string(noun_text)
                    if agent_text:    # Found a named entity that is an affiliated agent
                        affiliation_ttl = create_affiliation_ttl(noun_uri, agent_text, agent_type)
            else:
                noun = get_noun(noun_text, True)    # Use first noun of the phrase
        else:
            noun = get_noun(noun_text, False)   # Use the last word of the phrase
        if noun:
            class_name = _query_ontology(noun, query_noun1, query_noun2, query_noun3)
            if class_name == owl_thing:
                class_name = check_dictionary(noun, True)
    if not class_name:
        class_name = owl_thing
    if class_name == owl_thing:
        logging.warning(f'Could not map the noun, {noun_text}, to the ontology')
    if 'PLURAL' in noun_type and 'PERSON' not in noun_type:
        class_name = f'{class_name}>, <urn:ontoinsights:dna:Collection'
    return class_name, affiliation_ttl


def find_event_state_class(sentence_text: str, verb_dict: dict, lemma: str, processing: list) -> (str, list):
    """
    Determine the appropriate event or state in the DNA ontology, that matches the semantics of
    the verb. If the semantics are defined by idiom processing, return the event or state class and
    any triples dictated by the idiom processing.

    :param sentence_text: String holding the text of the sentence
    :param verb_dict: Dictionary holding the verb details
    :param lemma: The verb lemma or idiom
    :param processing: A list of string holding special processing for idioms
    :return Mapping of the verb/sentence semantics to the DNA ontology - either to a subclass of
            EventAndState or both the subclass and the complete ttl details for idiom processing
    """
    ttl_list = []
    for process in processing:
        class_name, ttl_list = process_idiom_detail(process, sentence_text, verb_dict, lemma)
        if ttl_list:
            return empty_string, ttl_list
    class_name = _query_ontology(lemma, query_event1, query_event2, query_event3)
    if class_name != event_and_state:
        return class_name, ttl_list  # ttl_list is empty
    # Applicable class not found, check dictionary and synonyms
    class_name = check_dictionary(lemma, False)
    if class_name == event_and_state:
        logging.warning(f'Could not map the verb, {lemma}, to the ontology')
    return class_name, ttl_list      # ttl_list is empty


# Functions internal to the module
def _query_ontology(text: str, query1: str, query2: str, query3: str) -> str:
    """
    Attempts to match the text to verb/noun_synonyms, labels and definitions in the ontology.

    :param text: Text to match
    :param query1: The first query to execute with the most exact results (equally of synonyms)
    :param query2: The second query to execute (if the first did not obtain results) which checks
                   that the text is contained in the synonyms, label or examples of a class
    :param query3: The last query to execute (if the second did not obtain results) which checks
                   if the synonyms contain the text (the least exact results)
    :return The class name that best matches the text
    """
    results1 = query_database('select', query1.replace('keyword', text), ontologies_database)
    for result in results1:
        return result['class']['value']
    results2 = query_database('select', query2.replace('keyword', text), ontologies_database)
    for result in results2:
        return result['class']['value']
    results3 = query_database('select', query3.replace('keyword', text), ontologies_database)
    for result in results3:
        return result['class']['value']
    return 'urn:ontoinsights:dna:EventAndState' if query1 == 'query_event1' else owl_thing
