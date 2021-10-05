# Query ontology class details
# To avoid passing a store name parameter, the ontology files are pre-loaded into an 'ontologies' database
# Called by create_event_turtle.py

import logging
import os
import pickle
import requests
import unicodedata
import uuid
from PyDictionary import PyDictionary

from database import query_database
from idiom_processing import process_idiom_detail, get_noun_idiom
from nlp import get_lemma, get_named_entity_in_string, get_noun
from utilities import empty_string, ontologies_database, resources_root, event_and_state_class, owl_thing, \
    processed_prepositions

dictionary = PyDictionary()

explicit_plural = ('group', 'people')
part_of_group = ('member', 'group', 'citizen', 'people', 'affiliate', 'representative', 'associate', 'comrade')

nouns_file = os.path.join(resources_root, 'verb-idioms.pickle')
with open(nouns_file, 'rb') as inFile:
    nouns_dict = pickle.load(inFile)

query_ethnicity_or_religion = \
    'prefix : <urn:ontoinsights:dna:> SELECT ?class ?prob WHERE ' \
    '{ ?class rdfs:subClassOf+ :class_type . ' \
    '{ { ?class :noun_synonym ?nsyn . FILTER(?nsyn = "keyword") . BIND(100 as ?prob) } UNION ' \
    '{ ?class rdfs:label ?label . FILTER(?label = "keyword") . BIND(85 as ?prob) } UNION ' \
    '{ ?class :noun_synonym ?nsyn . FILTER(CONTAINS(?nsyn, "keyword")) . BIND(90 as ?prob) } UNION ' \
    '{ ?class rdfs:label ?label . FILTER(CONTAINS(?label, "keyword")) . BIND(85 as ?prob) } UNION ' \
    '{ ?class :noun_synonym ?nsyn . FILTER(CONTAINS("keyword", ?nsyn)) . BIND(90 as ?prob) } UNION ' \
    '{ ?class rdfs:label ?label . FILTER(CONTAINS("keyword", ?label)) . BIND(85 as ?prob) } } ' \
    '} ORDER BY DESC(?prob)'

query_event = 'prefix : <urn:ontoinsights:dna:> SELECT ?class ?prob WHERE ' \
              '{ { { ?class :verb_synonym ?vsyn . FILTER(?vsyn = "keyword") . BIND(100 as ?prob) } UNION ' \
              '{ ?class :noun_synonym ?nsyn . FILTER(?nsyn = "keyword") . BIND(95 as ?prob) } UNION ' \
              '{ ?class :verb_synonym ?vsyn . FILTER(CONTAINS(?vsyn, "keyword")) . BIND(85 as ?prob) } UNION ' \
              '{ ?class :noun_synonym ?nsyn . FILTER(CONTAINS(?nsyn, "keyword")) . BIND(80 as ?prob) } UNION ' \
              '{ ?class rdfs:label ?label . FILTER(CONTAINS(lcase(?label), "keyword")) . BIND(75 as ?prob) } ' \
              'UNION { ?class :example ?ex . FILTER(CONTAINS(?ex, "keyword")) . BIND(70 as ?prob) } ' \
              'UNION { ?class :verb_synonym ?nsyn . FILTER(CONTAINS("keyword", ?vsyn)) . BIND(65 as ?prob) } ' \
              'UNION { ?class :noun_synonym ?vsyn . FILTER(CONTAINS("keyword", ?nsyn)) . BIND(60 as ?prob) } } ' \
              '?class rdfs:subClassOf+ :EventAndState } ORDER BY DESC(?prob)'

query_noun = 'prefix : <urn:ontoinsights:dna:> SELECT ?class ?prob WHERE ' \
             '{ ?class a owl:Class ' \
             '{ { ?class :noun_synonym ?nsyn . FILTER(?nsyn = "keyword") . BIND(100 as ?prob) } UNION ' \
             '{ ?class :noun_synonym ?nsyn . FILTER(CONTAINS(?nsyn, "keyword")) . BIND(90 as ?prob) } UNION ' \
             '{ ?class rdfs:label ?label . FILTER(CONTAINS(lcase(?label), "keyword")) . BIND(85 as ?prob) } ' \
             'UNION { ?class :example ?ex . FILTER(CONTAINS(?ex, "keyword")) . BIND(80 as ?prob) } ' \
             'UNION { ?class :noun_synonym ?nsyn . FILTER(CONTAINS("keyword", ?nsyn)) . BIND(65 as ?prob) } } ' \
             'FILTER NOT EXISTS { ?class rdfs:subClassOf+ :EventAndState } ' \
             'FILTER NOT EXISTS { ?class rdfs:subClassOf+ :Ethnicity } ' \
             'FILTER NOT EXISTS { ?class rdfs:subClassOf+ :Enumeration } } ORDER BY DESC(?prob)'


def create_affiliation_ttl(noun_uri: str, noun_text: str, affiliated_text: str, affiliated_type: str) -> list:
    """
    Creates the Turtle for an Affiliation.

    :param noun_uri: String holding the entity/URI to be affiliated
    :param noun_text: String holding the sentence text for the entity
    :param affiliated_text: String specifying the entity (organization, group, etc.) to which the
                            noun is affiliated
    :param affiliated_type: String specifying the class type of the entity
    :return An array of strings holding the Turtle representation of the Affiliation
    """
    affiliated_uri = f':{affiliated_text.replace(" ", "_")}'
    affiliation_uri = f'{noun_uri}{affiliated_text.replace(" ", "_")}Affiliation'
    noun_str = f"'{noun_text}'"
    ttl = [f'{affiliation_uri} a :Affiliation ; :affiliated_with {affiliated_uri} ; :affiliated_agent {noun_uri} .',
           f'{affiliation_uri} rdfs:label "Relationship based on the text, {noun_str}" .',
           f'{affiliated_uri} a {affiliated_type} ; rdfs:label "{affiliated_text}" .']
    wikidata_desc = get_wikipedia_description(affiliated_text)
    if wikidata_desc:
        ttl.append(f'{affiliated_uri} :definition "{wikidata_desc}" .')
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
                count = 0
                for clause in word_def[term_type]:
                    count += 1
                    if count > 3:   # TODO: How many definitions should be checked?
                        break
                    for sub_clause in clause.split(';'):
                        if is_noun:
                            word = get_noun(sub_clause, True)  # Return first noun in clause
                            query_str = query_noun
                        else:
                            word = sub_clause.split(' ')[0]
                            query_str = query_event
                        class_name = _query_ontology(word, query_str)
                        if class_name != owl_thing:
                            return class_name
        if is_noun:
            class_name = _query_ontology(word, query_event)
            return class_name
        else:
            return event_and_state_class
    except Exception as e:
        logging.error(f'Exception when getting noun class for {word}: {e}')
        return owl_thing


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


def get_event_state_ttl(sentence_text: str, event_uri: str, verb_dict: dict, lemma: str,
                        processing: list) -> list:
    """
    Determine the appropriate event or state in the DNA ontology, that matches the semantics of
    the verb and create the resulting Turtle. If the semantics are defined by idiom processing,
    return any triples dictated by the idiom processing.

    :param sentence_text: String holding the text of the sentence
    :param event_uri: The URI identifying the event for the verb, in the resulting Turtle file
    :param verb_dict: Dictionary holding the verb details
    :param lemma: The verb lemma or idiom
    :param processing: A list of string holding special processing for idioms
    :return Mapping of the verb/sentence semantics to the DNA ontology, returning the Turtle details
    """
    if processing:
        # TODO: Select the best process_str if len(processing) > 1
        ttl_list = process_idiom_detail(processing[0], sentence_text, event_uri, verb_dict)
        if ttl_list:
            return ttl_list
    class_name = _query_ontology(lemma, query_event)
    if class_name == event_and_state_class:
        # Applicable class not found, check dictionary and synonyms
        class_name = check_dictionary(lemma, False)   # Not a noun
        if class_name == event_and_state_class:
            logging.warning(f'Could not map the verb, {lemma}, to the ontology')
    return [f'{event_uri} a <{class_name}> .']


def get_noun_ttl(noun_uri: str, noun_text: str, noun_type: str, sentence_text: str) -> (str, list):
    """
    Determine the appropriate class in the DNA ontology, that matches the semantics of the noun_text.

    :param noun_uri: String identifying the URI/URL/individual associated with the noun_text
    :param noun_text: String specifying the noun text from the original narrative sentence
    :param noun_type: String holding the type of the noun (e.g., 'FEMALESINGPERSON' or 'PLURALNOUN')
    :param sentence_text: The full text of the sentence (needed for checking for idioms)
    :return A tuple holding the noun_uri (in case it was adjusted) and an array of the resulting
            Turtle for a mapping of the semantics to a DNA ontology class
    """
    wikipedia_desc = empty_string
    if noun_type.endswith('GPE') or noun_type.endswith('ORG') or noun_type.endswith('NORP'):
        wikipedia_desc = get_wikipedia_description(noun_text)
    if 'PERSON' in noun_type or noun_text == 'Narrator':
        class_name = 'urn:ontoinsights:dna:Person'
        if 'PLURAL' in noun_type:
            class_name = 'urn:ontoinsights:dna:GroupOfAgents'
    elif noun_type.endswith('GPE'):
        class_name = 'urn:ontoinsights:dna:GeopoliticalEntity'
    elif noun_type.endswith('NORP'):   # Nationalities, religious or political groups
        class_name = 'urn:ontoinsights:dna:Person'
        if 'PLURAL' in noun_type:
            class_name = 'urn:ontoinsights:dna:GroupOfAgents'
        # Check if ethnic group
        ethnicity = _query_ontology(
            noun_text, query_ethnicity_or_religion.replace('class_type', 'Ethnicity'))
        if ethnicity != owl_thing:
            new_uri = f'{noun_uri}_{str(uuid.uuid4())[:13]}'   # Is some subset of people of a certain ethnicity
            return new_uri, [f'{new_uri} a <{class_name}> ; rdfs:label "{noun_text}" .',
                             f'{new_uri} :has_agent_aspect <{ethnicity}> .']
        # Check if religious or political groups by getting description from Wikidata
        if wikipedia_desc:
            if 'political' in wikipedia_desc.lower():
                class_name = 'urn:ontoinsights:dna::PoliticalParty'
            else:
                new_uri = f'{noun_uri}_{str(uuid.uuid4())[:13]}'   # Is some subset of people of a certain religion
                words = wikipedia_desc.split(' ')
                for word in words:
                    religion = _query_ontology(
                        word, query_ethnicity_or_religion.replace('class_type', 'ReligiousBelief'))
                    if religion != owl_thing:
                        return new_uri, [f'{new_uri} a <{class_name}> ; rdfs:label "{noun_text}" .',
                                         f'{new_uri} :has_agent_aspect <{religion}> .']
                class_name = 'urn:ontoinsights:dna::Organization'   # Default is an Organization
    elif noun_type.endswith('ORG'):
        class_name = 'urn:ontoinsights:dna::Organization'
    else:
        found_prep = False
        for prep in processed_prepositions:
            found_prep = (True if noun_text.lower().startswith(f'{prep} ') else False) or \
                         (True if f' {prep} ' in noun_text.lower() else False)
            if found_prep:
                break
        if found_prep and check_text(noun_text, part_of_group):  # May be a reference to members of an org, group, ...
            if 'PLURAL' in noun_type or check_text(noun_text, explicit_plural):
                class_name = 'urn:ontoinsights:dna:GroupOfAgents'
            else:
                class_name = 'urn:ontoinsights:dna:Person'
            # Check if the org, group, ... is mentioned
            if ' of ' in noun_text or ' in ' in noun_text or ' from ' in noun_text:
                agent_text, agent_type = get_named_entity_in_string(noun_text)
                if agent_text:    # Found a named entity that is an affiliated agent
                    new_ttl = create_affiliation_ttl(noun_uri, noun_text, agent_text, agent_type)
                    new_ttl.append(f'{noun_uri} a <{class_name}> ; rdfs:label "{noun_text}" .')
                    return noun_uri, new_ttl
        else:
            noun = get_noun(noun_text, False)   # Use the last word of the phrase
            # First check noun overrides and idioms
            new_ttl = get_noun_idiom(noun, noun_text, noun_type, sentence_text, noun_uri)
            if new_ttl:
                return noun_uri, new_ttl
            class_name = _query_ontology(noun, query_noun)
            if class_name == owl_thing:   # Nothing found for the word as a noun
                class_name = _query_ontology(get_lemma(noun), query_event)  # Check if this is an event/state semantic
                if class_name == owl_thing:   # Nothing found for the word as an event/state
                    class_name = check_dictionary(noun, True)    # Check the dictionary for alternate terms
    if class_name == owl_thing:
        logging.warning(f'Could not map the noun, {noun_text}, to the ontology')
    if 'PLURAL' in noun_type and 'PERSON' not in noun_type:
        class_name = f'{class_name}>, <urn:ontoinsights:dna:Collection'
    ttl_list = [f'{noun_uri} a <{class_name}> ; rdfs:label "{noun_text}" .']
    if wikipedia_desc:
        ttl_list.append(f'{noun_uri} :description "{wikipedia_desc}" .')
    return noun_uri, ttl_list


def get_wikipedia_description(noun: str) -> str:
    """
    Get the first paragraph of the Wikipedia web page for the specified organization, group, ...

    :param noun: String holding the organization/group name
    :return String that is the first paragraph of the Wikipedia page (if the org/group is found);
            otherwise, an empty string
    """
    resp = requests.get(f'https://en.wikipedia.org/api/rest_v1/page/summary/{noun.replace(" ", "_")}')
    wikipedia = resp.json()
    if "extract" in wikipedia.keys():
        wiki_text = wikipedia['extract'].replace('"', "'").replace('\xa0', ' ').\
            encode('ASCII', errors='replace').decode('utf-8')
        wiki_text = f"'{wiki_text}'"
        return f'From Wikipedia (wikibase_item: {wikipedia["wikibase_item"]}): {wiki_text}'
    return empty_string


# Functions internal to the module
def _query_ontology(text: str, query_str: str) -> str:
    """
    Attempts to match the text to verb/noun_synonyms, labels and definitions in the ontology
    using the specified query.

    :param text: Text to match
    :param query_str: String holding the query to execute
    :return The highest probability class name returned by the query
    """
    results = query_database('select', query_str.replace('keyword', text), ontologies_database)
    for result in results:
        return result['class']['value']
    return owl_thing
