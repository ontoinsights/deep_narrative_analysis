# Functions to create the Turtle for Named Entities and obtain Wiki* details
#    which are requested in the query_sources.py methods

import re
import uuid
from rdflib import Literal

from dna.query_sources import get_geonames_location, get_wikipedia_description
from dna.utilities_and_language_specific import concept_map, empty_string, names_to_geo_dict


def _add_labels_to_ttl(entity_iri: str, labels: list, ttl_list: list):
    """
    Processing of the labels' text and their addition to the Turtle.

    :param entity_iri: String holding the IRI of the entity
    :param labels: Array of the entity's labels
    :param ttl_list: An array of the current Turtle for the entity
    :return: None (ttl_list is updated)
    """
    new_labels = []
    for label in labels:
        # Remove articles
        new_label = label
        for article in ('a ', 'A ', 'an ', 'An ', 'the ', 'The '):
            if label.startswith(article):
                new_label = label[len(article):]
                break
        new_labels.append(new_label)
    labels_str = '", "'.join(new_labels)
    ttl_list.append(f'{entity_iri} rdfs:label "{labels_str}" .')
    return ttl_list


def _add_wikidata_triples(entity_iri: str, description: str, wiki_url: str, wiki_id: str, ttl_list: list):
    """
    Definition of triples defining Wikipedia/Wikidata information.

    :param entity_iri: String holding the IRI of the entity
    :param description: Text of the first paragraph of the Wikipedia description of the entity
                        (if available); Otherwise, an empty string
    :param wiki_url: String holding the Wikipedia page URL where the paragraph and full article
                     are found (if available); Otherwise, an empty string
    :param wiki_id: Text holding the Wikidata identifier for the entity (if available);
                    Otherwise, an empty string
    :param ttl_list: An array of the current Turtle for the entity
    :return: None (ttl_list is updated)
    """
    if description:
        ttl_list.append(f'{entity_iri} rdfs:comment "{description}" .')
    if wiki_url:
        ttl_list.append(f'{entity_iri} :external_link "{wiki_url}" .')
    if wiki_id:
        # TODO: Pending pystardog fix; predicate = ':external_identifier {:identifier_source "Wikidata"}'
        predicate = ':external_identifier'    # For now, the only identifier using this predicate is Wikidata
        ttl_list.append(f'{entity_iri} {predicate} "{wiki_id}" .')


def create_agent_ttl(agent_iri: str, alt_names: list, agent_type: str, agent_class: str,
                     description: str, wiki_url: str, wikidata_id: str) -> list:
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
    :param wikidata_id: A string holding the Wikidata identifier of the entity (if available);
                        Otherwise, an empty string
    :return: Returns an array of the Agent's Turtle declaration
    """
    agent_ttl = [f'{agent_iri} a {agent_class} .']
    _add_labels_to_ttl(agent_iri, alt_names, agent_ttl)
    _add_wikidata_triples(agent_iri, description, wiki_url, wikidata_id, agent_ttl)
    if 'MALE' in agent_type:
        gender = "female" if "FEMALE" in agent_type else "male"
        agent_ttl.append(f'{agent_iri} :gender "{gender}" .')
    return agent_ttl


def create_location_ttl(loc_iri: str, loc_text: str, loc_class: str, ner_type: str) -> (list, list):
    """
    Create the Turtle for a location including additional details as described by GeoNames and Wikidata.

    :param loc_iri: String holding the IRI to be assigned to the location
    :param loc_text: The text of the location
    :param loc_class: The mapping of the entity type to the DNA ontology
    :param ner_type: The NER type assigned by spaCy
    :return: A tuple consisting of a list of the Location's Turtle declaration, and a list of
             alternate names for the Location
    """
    geonames_ttl = []
    alt_names = []
    geonames_details = get_geonames_location(loc_text)
    if geonames_details.location_class:
        geonames_ttl.append(f'{loc_iri} a {geonames_details.location_class} .')
        _add_labels_to_ttl(loc_iri, geonames_details.alt_names, geonames_ttl)
        alt_names.extend(geonames_details.alt_names)
        description_details = get_wikipedia_description(loc_text, ':Location', geonames_details.wiki_link)
        for label in description_details.labels:
            if label not in geonames_details.alt_names:
                alt_names.append(label)
        _add_wikidata_triples(loc_iri, description_details.wiki_desc, description_details.wiki_url,
                              description_details.wikidata_id, geonames_ttl)
        if geonames_details.admin_level > 0:
            geonames_ttl.append(f'{loc_iri} :admin_level {str(geonames_details.admin_level)} .')
        if geonames_details.country and geonames_details.country != "None":
            geonames_ttl.append(f'{loc_iri} :country_name "{geonames_details.country}" .')
            if geonames_details.country in names_to_geo_dict:
                geonames_ttl.append(f'geo:{names_to_geo_dict[geonames_details.country]} :has_component {loc_iri} .')
    elif ner_type != 'ORG':
        geonames_ttl.append(f'{loc_iri} a {loc_class} ; :text {Literal(loc_text).n3()} .')
    return geonames_ttl, alt_names


def create_named_entity_ttl(ent_iri: str, alt_names: list, class_map: str, description: str,
                            wiki_url: str = empty_string, wikidata_id: str = empty_string,
                            start_time_iri: str = empty_string, end_time_iri: str = empty_string) -> list:
    """
    Return the Turtle for a named entity not addressed by the other functions.

    :param ent_iri: The IRI created for the entity
    :param alt_names: An array of strings which represent alternate names for the entity
    :param class_map: Mapping of the entity to the DNA ontology
    :param description: A description of the entity from Wikipedia, if available; Otherwise,
                        an empty string
    :param wiki_url: A string holding the URL of the full Wikipedia article (if available);
                     Otherwise, an empty string
    :param wikidata_id: A string holding the Wikidata identifier of the entity (if available);
                        Otherwise, an empty string
    :param start_time_iri: The IRI created for the starting time of an event;
                           Otherwise, an empty string
    :param end_time_iri: The IRI created for the ending time of the event; Otherwise, an empty string
    :return: An array of Turtle declarations for the entity
    """
    if 'owl:Thing' in class_map:
        return []
    entity_ttl = [f'{ent_iri} a {class_map} .']
    _add_labels_to_ttl(ent_iri, alt_names, entity_ttl)
    _add_wikidata_triples(ent_iri, description, wiki_url, wikidata_id, entity_ttl)
    if start_time_iri:
        entity_ttl.append(f'{ent_iri} :has_beginning {start_time_iri} .')
    if end_time_iri:
        entity_ttl.append(f'{ent_iri} :has_end {end_time_iri} .')
    return entity_ttl


def create_norp_ttl(norp_iri: str, labels: list, norp_class: str, description: str, wiki_url: str,
                    wikidata_id: str) -> list:
    """
    Definition of the Turtle for a Group that was identified by spaCy as a 'NORP'
    (nationality, religious group, political party, ...).

    :param norp_iri: String identifying the concept as an IRI
    :param labels: An array of labels/alternate names for the noun
    :param norp_class: The mapping of the entity type to the DNA ontology
    :param description: A description of the nationality, ideology, religion, ... from Wikipedia, if available;
                        Otherwise, an empty string
    :param wiki_url: A string holding the URL of the full Wikipedia article (if available);
                     Otherwise, an empty string
    :param wikidata_id: A string holding the Wikidata identifier of the entity (if available);
                        Otherwise, an empty string
    :return: An array defining the Turtle declarations for the NORP entity
    """
    type_str = norp_class
    if description:
        wiki_lower = description.lower()
        for concept in concept_map:
            if concept in wiki_lower:
                type_str = norp_class.replace(':Affiliation', concept_map[concept])
                break
    norp_ttl = []
    _add_labels_to_ttl(norp_iri, labels, norp_ttl)
    norp_ttl.append(f'{norp_iri} a {type_str} .')
    _add_wikidata_triples(norp_iri, description, wiki_url, wikidata_id, norp_ttl)
    return norp_ttl
