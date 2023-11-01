# Functions to create the Turtle for Named Entities

import re
import uuid

from dna.query_sources import get_geonames_location, get_wikipedia_description
from dna.utilities_and_language_specific import concept_map, empty_string, explicit_plural, names_to_geo_dict, ner_dict

person = ':Person'
person_collection = ':Person, :Collection'


def create_agent_ttl(agent_iri: str, alt_names: list, agent_type: str, agent_class: str,
                     description: str, wiki_url: str) -> list:
    """
    Create the Turtle for a named entity that is identified as an Agent (Person, Organization, ...).

    :param agent_iri: String holding the IRI to be assigned to the Agent
    :param alt_names: An array of strings of alternative names
    :param agent_type: The entity type for the Agent (for ex, FEMALESINGPERSON)
    :param agent_class: The mapping of the entity type to the DNA ontology
    :param description: A description of the person from Wikipedia, if available; Otherwise,
                        an empty string
    :param wiki_url: A string holding the URL of the full Wikipedia article (if available);
                     Otherwise, an empty string
    :return: Returns an array of the Agent's Turtle declaration
    """
    labels = '", "'.join(alt_names)
    agent_ttl = [f'{agent_iri} a {agent_class} .',
                 f'{agent_iri} rdfs:label "{labels}" .']
    if description:
        agent_ttl.append(f'{agent_iri} rdfs:comment "{description}" .')
    if wiki_url:
        agent_ttl.append(f'{agent_iri} :external_link "{wiki_url}" .')
    if 'MALE' in agent_type:
        gender = "female" if "FEMALE" in agent_type else "male"
        agent_ttl.append(f'{agent_iri} :gender "{gender}" .')
    return agent_ttl


def create_location_ttl(loc_iri: str, loc_text: str, loc_class: str) -> (list, list):
    """
    Create the Turtle for a location including additional details as described by GeoNames.

    :param loc_iri: String holding the IRI to be assigned to the location
    :param loc_text: The text of the location
    :param loc_class: The mapping of the entity type to the DNA ontology
    :return: A tuple consisting of a list of the Location's Turtle declaration, and a list of
             alternate names for the Location
    """
    geonames_ttl = []
    class_type, country, admin_level, alt_names, wiki_link = get_geonames_location(loc_text)
    if class_type:
        geonames_ttl.append(f'{loc_iri} a {class_type} .')
        names_text = '", "'.join(alt_names)
        geonames_ttl.append(f'{loc_iri} rdfs:label "{names_text}" .')
        wiki_desc, wiki_url = get_wikipedia_description(loc_text, wiki_link)
        if wiki_desc:
            geonames_ttl.append(f'{loc_iri} rdfs:comment "{wiki_desc}" .')
        if wiki_url:
            geonames_ttl.append(f'{loc_iri} :external_link "{wiki_url}" .')
        if admin_level > 0:
            geonames_ttl.append(f'{loc_iri} :admin_level {str(admin_level)} .')
        if country and country != "None":
            geonames_ttl.append(f'{loc_iri} :country_name "{country}" .')
            if country in names_to_geo_dict:
                geonames_ttl.append(f'geo:{names_to_geo_dict[country]} :has_component {loc_iri} .')
    else:
        geonames_ttl.extend(f'{loc_iri} a {loc_class} ; :text "{loc_text}" .')
    return geonames_ttl, alt_names


def create_named_entity_ttl(ent_iri: str, alt_names: list, class_map: str, description: str,
                            wiki_url: str, start_time_iri: str, end_time_iri: str) -> list:
    """
    Return the Turtle for a 'default' named entity (not addressed by the other functions).

    :param ent_iri: The IRI created for the entity
    :param alt_names: An array of strings which represent alternate names for the entity
    :param class_map: Mapping of the entity to the DNA ontology
    :param description: A description of the entity from Wikipedia, if available; Otherwise,
                        an empty string
    :param wiki_url: A string holding the URL of the full Wikipedia article (if available);
                     Otherwise, an empty string
    :param start_time_iri: The IRI created for the starting time of an event;
                           Otherwise, an empty string
    :param end_time_iri: The IRI created for the ending time of the event; Otherwise, an empty string
    :return: An array of Turtle declarations for the entity
    """
    labels = '", "'.join(alt_names)
    entity_ttl = [f'{ent_iri} a {class_map} .',
                  f'{ent_iri} rdfs:label "{labels}" .']
    if description:
        entity_ttl.append(f'{ent_iri} rdfs:comment "{description}" .')
    if wiki_url:
        entity_ttl.append(f'{ent_iri} :external_link "{wiki_url}" .')
    if start_time_iri:
        entity_ttl.append(f'{ent_iri} :has_beginning {start_time_iri} .')
    if end_time_iri:
        entity_ttl.append(f'{ent_iri} :has_end {end_time_iri} .')
    return entity_ttl


def create_norp_ttl(norp_iri: str, norp_type: str, labels: list, norp_class: str,
                    description: str, wiki_url: str) -> list:
    """
    Definition of the Turtle for a Group that was identified by spaCy as a 'NORP'
    (nationality, religious group, political party, ...).

    :param norp_iri: String identifying the concept as an IRI
    :param norp_type: String holding the spaCy entity type
    :param labels: An array of labels/alternate names for the noun
    :param norp_class: String identifying the NORP class type
    :param description: A description of the nationality, ideology, religion, ... from Wikipedia, if available;
                        Otherwise, an empty string
    :param wiki_url: A string holding the URL of the full Wikipedia article (if available);
                     Otherwise, an empty string
    :return: An array defining the Turtle declarations for the NORP entity
    """
    type_str = person_collection if 'PLURAL' in norp_type else person
    labels_str = '", "'.join(labels)
    norp_ttl = [f'{norp_iri} a {type_str} ; rdfs:label "{labels_str}" .']
    if description:
        norp_aspect = empty_string
        wiki_lower = description.lower()
        for concept in concept_map.keys():
            if concept in wiki_lower:
                norp_aspect = concept_map[concept]
                break
        norp_ttl.append(f'{norp_iri} rdfs:comment "{description}" .')
        if norp_aspect:
            norp_ttl.append(f'{norp_iri} :has_aspect {norp_class} .')
    if wiki_url:
        norp_ttl.append(f'{norp_iri} :external_link "{wiki_url}" .')
    return norp_ttl
