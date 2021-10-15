# Query ontology class details
# To avoid passing a store name parameter, the ontology files are pre-loaded into an 'ontologies' database
# Called by create_event_turtle.py

import configparser as cp
import logging
import os
import pickle
import requests
import uuid
import xml.etree.ElementTree as etree

from PyDictionary import PyDictionary

from database import query_database
from idiom_processing import process_idiom_detail, get_noun_idiom
from nlp import get_synonym, get_named_entity_in_string, get_noun
from utilities import dna_prefix, domain_database, empty_string, ontologies_database, resources_root, \
    event_and_state_class, owl_thing, processed_prepositions

config = cp.RawConfigParser()
config.read(f'{resources_root}dna.config')
# Set geoname user id
geonamesUser = config.get('GeoNamesConfig', 'geonamesUser')

dictionary = PyDictionary()

explicit_plural = ('group', 'people')
part_of_group = ('member', 'group', 'citizen', 'people', 'affiliate', 'representative', 'associate', 'comrade')

nouns_file = os.path.join(resources_root, 'verb-idioms.pickle')
with open(nouns_file, 'rb') as inFile:
    nouns_dict = pickle.load(inFile)

domain_query_class = 'prefix : <urn:ontoinsights:dna:> SELECT ?class WHERE { ' \
                     '{ { SERVICE <db://domain-database> { <keyword> rdfs:subClassOf* ?class } } UNION ' \
                     '{ SERVICE <db://ontologies-database> { <keyword> rdfs:subClassOf* ?class } } } ' \
                     'SERVICE <db://ontologies-database> { ?class rdfs:subClassOf+ :searchClass } } '

query_class = 'prefix : <urn:ontoinsights:dna:> SELECT ?class WHERE { ' \
              '<keyword> rdfs:subClassOf+ :searchClass . BIND("keyword" as ?class) }'

domain_query_ethnicity_or_religion = \
    'prefix : <urn:ontoinsights:dna:> SELECT ?class ?prob WHERE { ' \
    'SERVICE <db://domain-database> { ?class rdfs:subClassOf* ?domain_class_type . ' \
    '{ ?class :noun_synonym ?nsyn . FILTER(?nsyn = "keyword") . BIND(100 as ?prob) } UNION ' \
    '{ ?class rdfs:label ?label . FILTER(?label = "keyword") . BIND(85 as ?prob) } UNION ' \
    '{ ?class :noun_synonym ?nsyn . FILTER(CONTAINS(?nsyn, "keyword")) . BIND(90 as ?prob) } UNION ' \
    '{ ?class rdfs:label ?label . FILTER(CONTAINS(?label, "keyword")) . BIND(85 as ?prob) } UNION ' \
    '{ ?class :noun_synonym ?nsyn . FILTER(CONTAINS("keyword", ?nsyn)) . BIND(90 as ?prob) } UNION ' \
    '{ ?class rdfs:label ?label . FILTER(CONTAINS("keyword", ?label)) . BIND(85 as ?prob) } } ' \
    'SERVICE <db://ontologies-database> { ?domain_class_type rdfs:subClassOf* :class_type } ' \
    '} ORDER BY DESC(?prob)'

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

query_match = 'prefix : <urn:ontoinsights:dna:> SELECT ?class WHERE ' \
              '{ { ?class :verb_synonym ?vsyn . FILTER(?vsyn = "keyword") } UNION ' \
              '{ ?class :noun_synonym ?nsyn . FILTER(?nsyn = "keyword") } UNION ' \
              '{ ?class rdfs:label ?label . FILTER(lcase(?label) = "keyword") } }'

domain_query_event = \
    'prefix : <urn:ontoinsights:dna:> SELECT ?class ?prob WHERE ' \
    '{ SERVICE <db://domain-database> { ?class rdfs:subClassOf* ?domain_class_type . ' \
    '{ { ?class :verb_synonym ?vsyn . FILTER(CONTAINS(?vsyn, "keyword")) . BIND(85 as ?prob) } UNION ' \
    '{ ?class :noun_synonym ?nsyn . FILTER(CONTAINS(?nsyn, "keyword")) . BIND(80 as ?prob) } UNION ' \
    '{ ?class rdfs:label ?label . FILTER(CONTAINS(lcase(?label), "keyword")) . BIND(75 as ?prob) } ' \
    'UNION { ?class :example ?ex . FILTER(CONTAINS(?ex, "keyword")) . BIND(70 as ?prob) } ' \
    'UNION { ?class :verb_synonym ?nsyn . FILTER(CONTAINS("keyword", ?vsyn)) . BIND(65 as ?prob) } ' \
    'UNION { ?class :noun_synonym ?vsyn . FILTER(CONTAINS("keyword", ?nsyn)) . BIND(60 as ?prob) } } } ' \
    'SERVICE <db://ontologies-database> { ?domain_class_type rdfs:subClassOf+ :EventAndState } } ' \
    'ORDER BY DESC(?prob)'

query_event = 'prefix : <urn:ontoinsights:dna:> SELECT ?class ?prob WHERE ' \
              '{ { { ?class :verb_synonym ?vsyn . FILTER(CONTAINS(?vsyn, "keyword")) . BIND(85 as ?prob) } UNION ' \
              '{ ?class :noun_synonym ?nsyn . FILTER(CONTAINS(?nsyn, "keyword")) . BIND(80 as ?prob) } UNION ' \
              '{ ?class rdfs:label ?label . FILTER(CONTAINS(lcase(?label), "keyword")) . BIND(75 as ?prob) } ' \
              'UNION { ?class :example ?ex . FILTER(CONTAINS(?ex, "keyword")) . BIND(70 as ?prob) } ' \
              'UNION { ?class :verb_synonym ?nsyn . FILTER(CONTAINS("keyword", ?vsyn)) . BIND(65 as ?prob) } ' \
              'UNION { ?class :noun_synonym ?vsyn . FILTER(CONTAINS("keyword", ?nsyn)) . BIND(60 as ?prob) } } ' \
              '?class rdfs:subClassOf+ :EventAndState } ORDER BY DESC(?prob)'

domain_query_noun = \
    'prefix : <urn:ontoinsights:dna:> SELECT ?class ?prob WHERE ' \
    '{ SERVICE <db://domain-database> { ?class rdfs:subClassOf* ?domain_class_type . ' \
    '{ { ?class :noun_synonym ?nsyn . FILTER(CONTAINS(?nsyn, "keyword")) . BIND(90 as ?prob) } UNION ' \
    '{ ?class rdfs:label ?label . FILTER(CONTAINS(lcase(?label), "keyword")) . BIND(85 as ?prob) } ' \
    'UNION { ?class :example ?ex . FILTER(CONTAINS(?ex, "keyword")) . BIND(80 as ?prob) } ' \
    'UNION { ?class :noun_synonym ?nsyn . FILTER(CONTAINS("keyword", ?nsyn)) . BIND(65 as ?prob) } } } ' \
    'SERVICE <db://ontologies-database> { ?domain_class_type a owl:Class . ' \
    'FILTER NOT EXISTS { ?domain_class_type rdfs:subClassOf+ :EventAndState } ' \
    'FILTER NOT EXISTS { ?domain_class_type rdfs:subClassOf+ :Ethnicity } ' \
    'FILTER NOT EXISTS { ?domain_class_type rdfs:subClassOf+ :Enumeration } } } ORDER BY DESC(?prob)'

query_noun = 'prefix : <urn:ontoinsights:dna:> SELECT ?class ?prob WHERE ' \
             '{ ?class a owl:Class ' \
             '{ { ?class :noun_synonym ?nsyn . FILTER(CONTAINS(?nsyn, "keyword")) . BIND(90 as ?prob) } UNION ' \
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
    :param is_noun: Boolean indicating if the word/term should be checked as a noun first
    :return String holding the concept's class name
    """
    try:
        word_def = dictionary.meaning(word, disable_errors=True)
        if word_def:
            term_types = ('Verb', 'Noun')
            if is_noun:
                term_types = ('Noun', 'Verb')
            for term_type in term_types:
                if term_type in word_def.keys():
                    count = 0
                    for clause in word_def[term_type]:
                        count += 1
                        if count > 3:   # TODO: How many definitions should be checked?
                            break
                        for sub_clause in clause.split(';'):
                            if term_type == 'Noun':
                                word = get_noun(sub_clause, True)  # Return first noun in clause
                                query_str = query_noun
                                domain_query_str = domain_query_noun
                            else:
                                word = sub_clause.split(' ')[0]
                                query_str = query_event
                                domain_query_str = domain_query_event
                            # First check for exact match
                            class_name = _query_ontology(word, query_match, query_match)
                            if class_name != owl_thing:
                                return class_name
                            class_name = _query_ontology(word, query_str, domain_query_str)
                            if class_name != owl_thing:
                                return class_name
        return owl_thing
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


def get_event_state_ttl(sentence_text: str, event_uri: str, verb_dict: dict, processing: list) -> list:
    """
    Determine the appropriate event or state in the DNA ontology, that matches the semantics of
    the verb and create the resulting Turtle. If the semantics are defined by idiom processing,
    return any triples dictated by the idiom processing.

    :param sentence_text: String holding the text of the sentence
    :param event_uri: The URI identifying the event for the verb, in the resulting Turtle file
    :param verb_dict: Dictionary holding the verb details
    :param processing: A list of string holding special processing for idioms
    :return Mapping of the verb/sentence semantics to the DNA ontology, returning the Turtle details
    """
    if processing:
        ttl_list = process_idiom_detail(processing, sentence_text, event_uri, verb_dict)
        if ttl_list:
            return ttl_list
    # First check for an exact match
    lemma = verb_dict['verb_lemma']
    class_name = _query_ontology(lemma, query_match, query_match)
    if class_name == owl_thing:
        class_name = _query_ontology(lemma, query_event, domain_query_event)
        if class_name == owl_thing:
            # Applicable class not found, check dictionary and synonyms
            class_name = check_dictionary(lemma, False)   # False = Not a noun
            if class_name == owl_thing:
                logging.warning(f'Could not map the verb, {lemma}, to the ontology')
    # Check if this is a movement/travel/transportation event
    if class_name != owl_thing and _indicate_location_or_movement(class_name, True):
        class_name = f'{class_name}>, <{dna_prefix}MovementTravelAndTransportation'
    if class_name == owl_thing:   # Simplified return from _query_ontology but need to correct for a verb
        class_name = event_and_state_class
    return [f'{event_uri} a <{class_name}> .']


def get_geonames_location(loc_text: str) -> (str, str, int):
    """
    Get the type of location from its text as well as its country and administrative level (if relevant).

    :param loc_text: Location text
    :return A tuple holding the location's class type, country name (or an empty string or None),
            and an administrative level (if 0, then admin level is not applicable) or GeoNames ID
            (for a Country)
    """
    logging.info(f'Getting location details for {loc_text}')
    # TODO: Add sleep to meet geonames timing requirements?
    response = requests.get(
        f'http://api.geonames.org/search?q={loc_text.lower().replace(" ", "+")}&maxRows=1&username={geonamesUser}')
    root = etree.fromstring(response.content)
    country = _get_xml_value('./geoname/countryName', root)
    feature = _get_xml_value('./geoname/fcl', root)
    fcode = _get_xml_value('./geoname/fcode', root)
    if not country and not feature and not fcode:
        return empty_string, empty_string, 0
    # Defaults
    admin_level = 0
    class_type = ":PopulatedPlace"
    if feature == 'A':     # Administrative area
        if fcode.startswith('ADM'):
            class_type += ', :AdministrativeDivision'
            # Get administrative level
            if any([i for i in fcode if i.isdigit()]):
                admin_level = [int(i) for i in fcode if i.isdigit()][0]
        elif fcode.startswith('PCL'):  # Some kind of political entity, assuming for now that it is a country
            class_type = ":Country"
            country = empty_string
        elif fcode.startswith('L') or fcode.startswith('Z'):
            # Leased area usually for military installations or a zone, such as a demilitarized zone
            return empty_string, empty_string, admin_level
    elif feature == 'P':   # Populated Place
        if fcode.startswith('PPLA'):
            class_type += ', :AdministrativeDivision'
            # Get administrative level
            admin_levels = [int(i) for i in fcode if i.isdigit()]
            if admin_levels:
                admin_level = admin_levels[0]
            else:
                admin_level = 1
    return class_type, country, admin_level


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
            noun_text, query_ethnicity_or_religion.replace('class_type', 'Ethnicity'),
            domain_query_ethnicity_or_religion.replace('class_type', 'Ethnicity'))
        if ethnicity != owl_thing:
            new_uri = f'{noun_uri}_{str(uuid.uuid4())[:13]}'   # Is some subset of people of a certain ethnicity
            ethnicity_ttl = [f'{new_uri} a <{class_name}> ; rdfs:label "{noun_text}" .',
                             f'{new_uri} :has_agent_aspect <{ethnicity}> .']
            if noun_type.startswith('NEG'):
                ethnicity_ttl = [f'{new_uri} :negation true .']
            return new_uri, ethnicity_ttl
        # Check if religious or political groups by getting description from Wikidata
        if wikipedia_desc:
            if 'political' in wikipedia_desc.lower():
                class_name = 'urn:ontoinsights:dna::PoliticalParty'
            else:
                new_uri = f'{noun_uri}_{str(uuid.uuid4())[:13]}'   # Is some subset of people of a certain religion
                words = wikipedia_desc.split(' ')
                for word in words:
                    religion = _query_ontology(
                        word, query_ethnicity_or_religion.replace('class_type', 'ReligiousBelief'),
                        domain_query_ethnicity_or_religion.replace('class_type', 'ReligiousBelief'))
                    if religion != owl_thing:
                        religion_ttl = [f'{new_uri} a <{class_name}> ; rdfs:label "{noun_text}" .',
                                        f'{new_uri} :has_agent_aspect <{religion}> .']
                        if noun_type.startswith('NEG'):
                            religion_ttl.append(f'{new_uri} :negation true .')
                        return new_uri, religion_ttl
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
                # TODO: Generalize group
                if 'army' in noun_type.lower():
                    new_ttl = create_affiliation_ttl(noun_uri, noun_text, 'army', ':ArmedForce')
                    new_ttl.append(f'{noun_uri} a :Person ; rdfs:label "{noun_text}" .')
                    return noun_uri, new_ttl
                else:
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
            # First check for an exact match
            class_name = _query_ontology(noun, query_match, query_match)
            if class_name == owl_thing:
                class_name = _query_ontology(noun, query_noun, domain_query_noun)
                if class_name == owl_thing:   # Nothing found for the word as a noun
                    words = get_synonym(noun)   # Get verb/noun synonyms
                    for word in words:
                        class_name = _query_ontology(word, query_noun, domain_query_noun)
                        if class_name == owl_thing:
                            # Check for event/state
                            class_name = _query_ontology(word, query_event, domain_query_event)
                        if class_name != owl_thing:
                            break
                if class_name == owl_thing:   # Nothing found for the word synonyms
                    # Check the dictionary for alternate terms
                    class_name = check_dictionary(noun, True)    # True = Check nouns first
    if class_name == owl_thing:
        logging.warning(f'Could not map the noun, {noun_text}, to the ontology')
    if class_name != owl_thing and _indicate_location_or_movement(class_name, False):
        class_name = f'{class_name}>, <{dna_prefix}Location'
    if 'PLURAL' in noun_type and 'PERSON' not in noun_type:
        class_name = f'{class_name}>, <urn:ontoinsights:dna:Collection'
    ttl_list = [f'{noun_uri} a <{class_name}> ; rdfs:label "{noun_text}" .']
    if noun_type.startswith('NEG'):
        ttl_list.append(f'{noun_uri} :negation true .')
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
def _get_xml_value(xpath: str, root: etree.Element) -> str:
    """
    Uses an xpath string to access specific elements in an XML tree.

    :param xpath: String identifying the path to the element to be retrieved
    :param root: The root element of the XML tree
    :return String representing the value of the specified element or an empty string
            (if not defined)
    """
    elems = root.findall(xpath)
    if elems:
        return elems[0].text
    else:
        return empty_string


def _indicate_location_or_movement(class_name: str, for_movement: bool) -> bool:
    """
    Check if the event/class_name is a subclass of :MovementTravelAndTransportation.

    :param class_name: The type of event as defined by its class name
    :param for_movement: Boolean indicating that the query is for subclasses of
                         :MovementTravelAndTransportation if true, and for subclasses of :Location
                         if false
    :return Boolean of True if a subclass of :MovementTravelAndTransportation or :Location
            (depending on the value of the for_movement boolean) and False otherwise
    """
    query_str = query_class.replace('searchClass', 'Location')
    domain_query_str = domain_query_class.replace('searchClass', 'Location')
    if for_movement:
        query_str = query_class.replace('searchClass', 'MovementTravelAndTransportation')
        domain_query_str = domain_query_class.replace('searchClass', 'MovementTravelAndTransportation')
    result = _query_ontology(class_name, query_str, domain_query_str)
    if result == owl_thing:
        return False
    return True


def _query_ontology(text: str, query: str, domain_query: str) -> str:
    """
    Attempts to match the text to verb/noun_synonyms, labels and definitions in the ontology
    using the specified query.

    :param text: Text to match
    :param query: String holding the query to execute for the core ontologies
    :param domain_query: String holding the query to execute for the domain ontologies
    :return The highest probability class name returned by the query
    """
    domain_query_replaced = domain_query.replace('domain-database', domain_database).\
        replace('ontologies-database', ontologies_database)
    results = query_database('select', domain_query_replaced.replace('keyword', text), domain_database)
    for result in results:
        return result['class']['value']
    results = query_database('select', query.replace('keyword', text), ontologies_database)
    for result in results:
        return result['class']['value']
    return owl_thing
