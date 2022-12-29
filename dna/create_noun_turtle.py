# Functions to clean up the Turtle (before storage in Stardog)
# Called by create_narrative_turtle.py

import re
import uuid

from dna.create_specific_turtle import create_type_turtle
from dna.database import query_database
from dna.get_ontology_mapping import determine_norp_emotion_or_lob, get_noun_mapping
from dna.nlp import get_named_entities_in_string
from dna.queries import query_agent_or_location
from dna.query_ontology import get_norp_emotion_or_lob
from dna.query_sources import get_geonames_location, get_wikipedia_description
from dna.utilities_and_language_specific import concept_map, days, empty_string, explicit_plural, months, \
    names_to_geo_dict, ner_dict, ontologies_database, processed_prepositions

person = ':Person'
person_collection = ':Person, :Collection'


def _check_presence_of_words(text: str, words: tuple) -> bool:
    """
    Determines if one of the 'words' in the input tuple is found in the 'text' string. Returns
    True if so.

    :param text: The string to be checked
    :param words: A tuple holding words to be searched for
    :return: True if one of the 'words' is found in the 'text; False otherwise
    """
    for word in words:
        if word in text:
            return True
    return False


def _create_norp_details(noun_text: str, noun_type: str, noun_iri: str, is_subj: bool,
                         ext_sources: bool) -> (list, list):
    """
    Definition of the details to create the Turtle for a Person or Group that was identified
    by spaCy as a 'NORP' (nationality, religious group, political party, ...).

    :param noun_text: String holding the noun text
    :param noun_type: String holding the type of the noun (e.g., 'FEMALESINGPERSON' or 'PLURALNOUN')
    :param noun_iri: String identifying the noun concept as an IRI
    :param is_subj: Boolean indicating that the noun is the subject of a sentence
    :param ext_sources: A boolean indicating that data from GeoNames, Wikidata, etc. should be
                        added to the parse results if available
    :return: A tuple holding the type of noun (e.g., Person or OrganizationalEntity) and an array of
             the defining Turtle (if appropriate)
    """
    norp_class = empty_string
    norp_type = empty_string
    # Check if ethnic group, religious group, ... that is already defined in the DNA ontology
    for word in noun_text.split():
        norp_type, norp_class = get_norp_emotion_or_lob(word)
        # Should not be LOB or emotion
        if norp_class and norp_type != 'EmotionalResponse' and norp_type != 'LineOfBusiness':
            break
    if ext_sources and (not norp_class or norp_type == 'EmotionalResponse' or norp_type == 'LineOfBusiness'):
        # Check if a type of ethnic, religious or political group by checking the Wikipedia description
        wikipedia_desc, wiki_url = get_wikipedia_description(noun_text.replace(' ', '_'))
        if wikipedia_desc:
            wikipedia_lower = wikipedia_desc.lower()
            for concept in concept_map.keys():
                if concept in wikipedia_lower:
                    norp_class = concept_map[concept]
    if not norp_class or norp_type == 'EmotionalResponse' or norp_type == 'LineOfBusiness':
        # Did not find match of the word or any details from its definition
        norp_class = ':AgentAspect'
    if is_subj:
        return [norp_class], create_norp_ttl(noun_text, noun_type, noun_iri, norp_class, empty_string, [])
    return [person_collection if 'PLURAL' in noun_type else person], []


def create_affiliation_ttl(noun_iri: str, noun_text: str, affiliated_text: str, affiliated_type: str,
                           alet_dict:dict) -> list:
    """
    Creates the Turtle for an Affiliation.

    :param noun_iri: String holding the entity/IRI to be affiliated
    :param noun_text: String holding the sentence text for the entity
    :param affiliated_text: String specifying the entity (organization, group, etc.) to which the
                            noun is affiliated
    :param affiliated_type: String specifying the class type of the entity
    :param alet_dict: A dictionary holding the agents, locations, events & times encountered in
             the full narrative - For co-reference resolution; Keys = 'agents', 'locs', 'events',
             'times' and Values vary by the key; For 'agents', dict = array of arrays with
             index 0 holding an array of labels associated with the agent (variations on their
             name), index 1 storing the agent's entity type and index 2 storing the agent's IRI;
             For 'locs', dict = array of arrays with index 0 holding an array of strings/alt names
             associated with the location, index 1 storing the class mappings, and index 2 defining
             the location's IRI
    :return: An array of strings holding the Turtle representation of the Affiliation
    """
    affiliated_iri = empty_string
    if 'agents' not in alet_dict and 'locs' not in alet_dict:
        logging.error(f'Affiliation ({affiliated_text}) indicated for {noun_text} but no values in alet_dict')
    else:
        if 'agents' in alet_dict:
            for known_agent in alet_dict['agents']:
                if affiliated_text in known_agent[0]:
                    affiliated_iri = known_agent[2]
                    break
        if not affiliated_iri and 'locs' in alet_dict:
            for known_locs in alet_dict['locs']:
                if affiliated_text in known_locs[0]:
                    affiliated_iri = known_locs[2]
                    break
    if not affiliated_iri:
        return []
    affiliation_iri = f'{noun_iri}_{affiliated_iri[1:]}_Affiliation'
    noun_str = f"'{noun_text}'"
    ttl = [f'{affiliation_iri} a :Affiliation ; :affiliated_with {affiliated_iri} ; :affiliated_agent {noun_iri} .',
           f'{affiliation_iri} rdfs:label "Relationship based on the text, {noun_str}" .']
    return ttl


def create_agent_ttl(agent_iri: str, alt_names: list, agent_type: str, agent_class: str,
                     description: str, wiki_url: str, family_names: list) -> list:
    """
    Create the Turtle for a named entity that is identified as an Agent/Person.

    :param agent_iri: String holding the IRI to be assigned to the Agent
    :param alt_names: An array of strings of alternative names
    :param agent_type: The entity type for the Agent (for ex, FEMALESINGPERSON)
    :param agent_class: The mapping of the entity type to the DNA ontology
    :param description: A description of the person from Wikipedia, if available; Otherwise,
                        an empty string
    :param wiki_url: A string holding the URL of the full Wikipedia article (if available);
                     Otherwise, an empty string
    :param family_names: An array of family names for a Person (there may be multiple names
                         - for example, for a married woman)
    :return: A tuple holding the agent_class and an array of its Turtle declaration
    """
    labels = '", "'.join(alt_names)
    agent_ttl = [f'{agent_iri} a {agent_class} .',
                 f'{agent_iri} rdfs:label "{labels}" .']
    if description:
        agent_ttl.append(f'{agent_iri} :description "{description}" .')
    if wiki_url:
        agent_ttl.append(f'{agent_iri} :external_link "{wiki_url}" .')
    if 'MALE' in agent_type:
        gender = "Female" if "FEMALE" in agent_type else "Male"
        agent_ttl.append(f'{agent_iri} :gender "{gender}" .')
    if family_names:
        for fam_name in family_names:
            agent_ttl.append(f':{fam_name} a :Person, :Collection ; rdfs:label "{fam_name}" ; :role "family" .')
    return agent_ttl


def create_geonames_ttl(loc_iri: str, loc_text: str) -> (list, str, list):
    """
    Create the Turtle for a location that is a location described by GeoNames.

    :param loc_iri: String holding the IRI to be assigned to the location
    :param loc_text: The location text
    :return: A tuple holding an array that are the individual Turtle statements describing
              the location (if available; otherwise, an empty array), the location's class mapping
              (there is only 1), and an array of alternate names for the location (if available;
              otherwise, an array with the loc_text)
    """
    geonames_ttl = []
    class_type, country, admin_level, alt_names, wiki_link = get_geonames_location(loc_text)
    if class_type:
        geonames_ttl.extend(create_type_turtle([class_type], loc_iri, False, loc_text))
        names_text = '", "'.join(alt_names)
        geonames_ttl.append(f'{loc_iri} rdfs:label "{names_text}" .')
        wiki_desc, wiki_url = get_wikipedia_description(loc_text, wiki_link)
        if wiki_desc:
            geonames_ttl.append(f'{loc_iri} :description "{wiki_desc}" .')
        if wiki_url:
            geonames_ttl.append(f'{loc_iri} :external_link "{wiki_url}" .')
        if admin_level > 0:
            geonames_ttl.append(f'{loc_iri} :admin_level {str(admin_level)} .')
        if country and country != "None":
            geonames_ttl.append(f'{loc_iri} :country_name "{country}" .')
            if country in names_to_geo_dict:
                geonames_ttl.append(f'geo:{names_to_geo_dict[country]} :has_component {loc_iri} .')
    return geonames_ttl, class_type, alt_names


def create_named_event_ttl(event_iri: str, alt_names: list, event_classes: list, description: str, wiki_url: str,
                           start_time_iri: str, end_time_iri: str) -> list:
    """
    Return the Turtle related to a named event.

    :param event_iri: The IRI created for the event
    :param alt_names: An array of strings which represent alternate names for the event
    :param event_classes: An array with mappings of the event to the DNA ontology
    :param description: A description of the event from Wikipedia, if available; Otherwise,
                        an empty string
    :param wiki_url: A string holding the URL of the full Wikipedia article (if available);
                     Otherwise, an empty string
    :param start_time_iri: The IRI created for the starting time of the event
    :param end_time_iri: The IRI created for the ending time of the event
    :return: An array of Turtle statements
    """
    labels = '", "'.join(alt_names)
    event_ttl = [f'{event_iri} a {", ".join(event_classes)} .',
                 f'{event_iri} rdfs:label "{labels}" .']
    if description:
        event_ttl.append(f'{event_iri} :description "{description}" .')
    if wiki_url:
        event_ttl.append(f'{event_iri} :external_link "{wiki_url}" .')
    if start_time_iri:
        event_ttl.append(f'{event_iri} :has_beginning {start_time_iri} .')
    if end_time_iri:
        event_ttl.append(f'{event_iri} :has_end {end_time_iri} .')
    return event_ttl


def create_norp_ttl(noun_text: str, noun_type: str, noun_iri: str, description: str, wiki_url: str,
                    labels: list) -> list:
    """
    Definition of the Turtle for a Person or Group that was identified by spaCy as a 'NORP'
    (nationality, religious group, political party, ...).

    :param noun_text: String holding the noun text
    :param noun_type: String holding the type of the noun (e.g., 'FEMALESINGPERSON' or 'PLURALNOUN')
    :param noun_iri: String identifying the noun concept as an IRI
    :param description: A description of the nationality, ideology, religion, ... from Wikipedia, if available;
                        Otherwise, an empty string
    :param wiki_url: A string holding the URL of the full Wikipedia article (if available);
                     Otherwise, an empty string
    :param labels: An array of labels/alternate names for the noun
    :return: An array defining the Turtle for the NORP entity
    """
    type_str = person_collection if 'PLURAL' in noun_type else person
    if noun_text not in labels:
        labels.append(noun_text)
    labels_str = '", "'.join(labels)
    norp_ttl = [f'{noun_iri} a {type_str} ; rdfs:label "{labels_str}" .']
    if description:
        norp_ttl.append(f'{noun_iri} :description "{description}" .')
    if wiki_url:
        norp_ttl.append(f'{noun_iri} :external_link "{wiki_url}" .')
    norp_class = determine_norp_emotion_or_lob(noun_text, [(empty_string, empty_string, [], noun_iri)])
    if norp_class in (':AgentAspect', ':ReligiousBelief', ':Ethnicity', ':PoliticalIdeology'):
        norp_ttl.append(f'{noun_iri} :has_agent_aspect {norp_class} ; :agent_aspect "{noun_text}" .')
    if noun_type.startswith('NEG'):
        norp_ttl.append(f'{noun_iri} :negation true .')
    return norp_ttl


def create_noun_ttl(noun_iri: str, noun_text: str, noun_type: str, alet_dict: dict, is_subj: bool,
                    ext_sources: bool) -> (list, list):
    """
    Create the Turtle for a noun, given all the input information. And, if a new concept
    is found, update the last_nouns array and return its Turtle statement.

    :param noun_iri: String identifying the IRI/URL/individual associated with the noun_text
    :param noun_text: String specifying the noun text from the original narrative sentence
    :param noun_type: String holding the type of the noun (e.g., 'FEMALESINGPERSON' or 'PLURALNOUN')
    :param alet_dict: A dictionary holding the agents, locations, events & times encountered in
             the full narrative - For co-reference resolution; Keys = 'agents', 'locs', 'events',
             'times' and Values vary by the key
    :param is_subj: Boolean indicating that the noun is the subject of a sentence
    :param ext_sources: A boolean indicating that data from GeoNames, Wikidata, etc. should be
                        added to the parse results if available
    :return: A tuple holding two arrays - 1) class mappings and 2) the Turtle of the noun semantics
    """
    # Process nouns based on their (mutually exclusive) entity type from spaCy
    init_mapping = []
    noun_ttl = []
    if 'PERSON' in noun_type:
        class_name = person
        if 'MALE' in noun_type:
            gender = "Female" if "FEMALE" in noun_type else "Male"
            noun_ttl.append(f'{noun_iri} :gender "{gender}" .')
    if noun_type.endswith('GPE'):
        init_mapping = [':GeopoliticalEntity+:Location']
    # Nationalities, religious or political groups
    if noun_type.endswith('NORP'):
        return _create_norp_details(noun_text, noun_type, noun_iri, is_subj, ext_sources)
    if noun_type.endswith('ORG'):
        init_mapping = [':Organization']
    if noun_type.endswith('LOC'):
        init_mapping = [':Location']
    if not init_mapping:
        noun_mapping, noun_ttl = get_noun_mapping(noun_text, noun_iri)
        found_agent_or_loc = False      # Focus on finding affiliations for agents and locations; Future: Other nouns?
        for noun_map in noun_mapping:   # Matches if any mapping is an Agent or Location; Should this be more specific?
            if '+' in noun_map:
                for map_name in noun_map.split('+'):
                    query_results = query_database('select', query_agent_or_location.replace('keyword', map_name),
                                                   ontologies_database)
                    if any(['result' in query_result for query_result in query_results]):
                        found_agent_or_loc = True
                        init_mapping = [noun_map]
                        break
            else:
                init_mapping = [noun_map]           # Only a single mapping
                query_results = query_database('select', query_agent_or_location.replace('keyword', noun_map),
                                               ontologies_database)
                if any(['result' in query_result for query_result in query_results]):
                    found_agent_or_loc = True
            if found_agent_or_loc:
                # Check for named entity in phrase (already know that it is not the main noun)
                # Future: Refine by other words in phrase?
                named_entities = get_named_entities_in_string(noun_text)
                if named_entities:
                    for ne_text, ne_type in named_entities:
                        if ne_type in ('NORP', 'ORG'):
                            noun_ttl.extend(create_affiliation_ttl(noun_iri, noun_text, ne_text, ne_type, alet_dict))
                break     # Preference given to Agents
    class_mapping = []
    if 'PLURAL' in noun_type:
        for init_map in init_mapping:
            class_mapping.append(f'{init_map}, :Collection')
    else:
        class_mapping = init_mapping
    noun_ttl.extend(create_type_turtle(class_mapping, noun_iri, False, noun_text))
    noun_ttl.append(f'{noun_iri} rdfs:label "{noun_text}" .')
    if noun_type.startswith('NEG'):
        noun_ttl.append(f'{noun_iri} :negation true .')
    return class_mapping, noun_ttl


def create_time_ttl(time_text: str, time_iri: str) -> list:
    """
    Return the Turtle related to a point in time.

    :param time_text: The text defining the time
    :param time_iri: The IRI created for the time
    :return: An array of Turtle statements
    """
    time_ttl = [f'{time_iri} a :PointInTime ; rdfs:label "{time_text}" .']
    if '_Yr' in time_iri:
        time_ttl.append(f'{time_iri} :year {time_iri.split("_Yr")[1].split("_")[0]} .')
    if '_Mo' in time_iri:
        time_ttl.append(f'{time_iri} :month_of_year '
                        f'{str(months.index(time_iri.split("_Mo")[1].split("_")[0]) + 1)} .')
    if '_Day' in time_iri:
        day = time_iri.split("_Day")[1]
        if day in days:
            time_ttl.append(f'{time_iri} :day_of_week {days.index(day) + 1} .')
        else:
            time_ttl.append(f'{time_iri} :day_of_month {day} .')
    return time_ttl
