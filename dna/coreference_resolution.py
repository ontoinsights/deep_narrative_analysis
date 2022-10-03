# Functions for co-reference resolution
# Called by create_narrative_turtle.py

import uuid
import re
from typing import Union

from dna.create_noun_turtle import create_noun_ttl
from dna.database import query_database
from dna.get_ontology_mapping import get_agent_class, get_noun_mapping
from dna.queries import query_specific_noun
from dna.utilities import dna_prefix, empty_string, names_to_geo_dict, ontologies_database, owl_thing2

pronouns = ['I', 'we', 'us', 'they', 'them', 'he', 'she', 'it',
            'myself', 'ourselves', 'themselves', 'herself', 'himself', 'itself']


def _check_criteria(text: str, last_nouns: list, looking_for_singular: Union[bool, None],
                    looking_for_female: Union[bool, None], looking_for_person: bool) -> list:
    """
    Checks the values of the nouns in the last_nouns array for matches of the specified
    gender/number criteria.

    :param text: A string with the noun text
    :param last_nouns: A list of noun texts, types, class mappings and IRIs, from the current paragraph
    :param looking_for_singular: Boolean indicating that a singular noun is needed
    :param looking_for_female: Boolean indicating that a female gender noun is needed
    :param looking_for_person: Boolean indicating that a 'matched' noun should be a person
    :return: Array of tuples of texts, types, class_mappings and IRIs of already processed nouns that
              match the criteria; Note that an array is returned to support matching the pronouns 'they'/'them'
    """
    poss_nouns = []
    alt_nouns = []
    for noun_tuple in last_nouns:
        noun_text, noun_type, noun_mapping, noun_iri = noun_tuple
        if text not in pronouns and (text not in noun_text or noun_text not in text):
            continue     # First match the text if not a pronoun; If no match, skip the rest of the criteria
        if (looking_for_person and 'PERSON' not in noun_type) or \
                (not looking_for_person and 'PERSON' in noun_type):
            continue
        # Check number
        found_number = False
        if looking_for_singular is None or (looking_for_singular and 'SING' in noun_type) or \
                (not looking_for_singular and 'PLURAL' in noun_type):
            found_number = True
        found_gender = False
        if looking_for_female is None or (looking_for_female and 'FEMALE' in noun_type) or \
                (not looking_for_female and 'FEMALE' not in noun_type and 'MALE' in noun_type):
            found_gender = True
        # Check criteria
        if found_gender and found_number:
            poss_nouns.append(noun_tuple)
        elif found_gender or found_number:
            alt_nouns.append(noun_tuple)
    match_nouns = poss_nouns if poss_nouns else (alt_nouns if alt_nouns else [])
    if looking_for_singular and len(match_nouns) > 1:
        return [match_nouns[-1]]
    return match_nouns


def _check_last_nouns(text: str, text_type: str, last_nouns: list) -> list:
    """
    Get the most likely co-reference for the noun text using the last_nouns details.
    Subject/object information (the noun, and its type, mapping and IRI) is returned.

    :param text: String holding the noun text
    :param text_type: String holding the noun type (such as 'FEMALESINGPERSON')
    :param last_nouns: An array of tuples of noun texts, types, mappings and IRI, from the current paragraph
    :return: A tuple that is the 'matched' noun mapping and IRI, or two empty strings (if
              no match is found)
    """
    looking_for_female = True if 'FEMALE' in text_type else (False if 'MALE' in text_type else None)
    looking_for_singular = False if 'PLURAL' in text_type else (True if 'SING' in text_type else None)
    looking_for_person = True if 'PERSON' in text_type else False
    match_nouns = _check_criteria(text, last_nouns, looking_for_singular, looking_for_female, looking_for_person)
    final_nouns = []
    for match_noun in match_nouns:
        # Don't need the noun texts or entity types (those are used for pronouns)
        final_nouns.append((match_noun[2], match_noun[3]))
    return final_nouns


def _check_alet_dict(text: str, text_type: str, alet_dict: dict, last_nouns: list) -> (list, str):
    """
    Get the most likely co-reference for the text using the alet_dict details to
    resolve co-references/anaphora. Subject/object information (the noun, and its types
    and IRI) is returned.

    :param text: String holding the noun text
    :param text_type: String holding the noun type (such as 'FEMALESINGPERSON')
    :param alet_dict: A dictionary holding the agents, locations, events & times encountered in
             the full narrative - For co-reference resolution; Keys = 'agents', 'locs', 'events',
             'times' and Values vary by the key
    :param last_nouns: An array of tuples of noun texts, types, mappings and IRI, from the current paragraph
    :return: A tuple that consists of the matched noun's class mappings and IRI, or an empty array and string
    """
    agent_match = []          # Match of text and type
    agent_text_match = []     # Match of text only, not type
    loc_text_match = []
    event_text_match = []
    # text_type may be missing from spaCy for some nouns due to removal of commas from text; Should punct be retained?
    if not text_type or 'PERSON' in text_type or text_type.endswith('ORG') or \
            text_type.endswith('GPE') or text_type.endswith('NORP') or text_type.endswith('NOUN'):
        agent_arrays = alet_dict['agents'] if 'agents' in alet_dict else []
        for agent_array in agent_arrays:
            alt_names = agent_array[0]
            agent_type = agent_array[1]
            if text not in pronouns and text in alt_names:
                if text_type and (text_type in agent_type or agent_type in text_type):
                    agent_match.append((agent_type, agent_array[2]))    # index 2 holds the IRI
                    break
                else:
                    agent_text_match.append((agent_type, agent_array[2]))
    if not text_type or 'LOC' in text_type or 'GPE' in text_type or 'FAC' in text_type or 'NOUN' in text_type:
        loc_arrays = alet_dict['locs'] if 'locs' in alet_dict else []
        for loc_array in loc_arrays:
            alt_names = loc_array[0]
            loc_map = loc_array[1]
            if text in alt_names:
                loc_text_match.append((loc_map, loc_array[2]))   # index 2 holds the IRI
    if not text_type or 'EVENT' in text_type or 'NOUN' in text_type:
        event_arrays = alet_dict['events'] if 'events' in alet_dict else []
        for event_array in event_arrays:
            alt_names = event_array[0]
            if text in alt_names:
                # event_array[1] holds the class mappings and [2] holds the IRI
                event_text_match.append((event_array[1], event_array[2]))
    return (_update_last_nouns(text, agent_match[-1][0], agent_match[-1][1], [get_agent_class(text_type)],
                               last_nouns) if agent_match
            else (_update_last_nouns(text, agent_text_match[-1][0], agent_text_match[-1][1],
                                     [get_agent_class(text_type)], last_nouns) if agent_text_match
                  else (_update_last_nouns(text, text_type, loc_text_match[-1][1], loc_text_match[-1][0], last_nouns)
                        if loc_text_match
                        else (_update_last_nouns(text, text_type, event_text_match[-1][1], event_text_match[-1][0],
                                                 last_nouns) if event_text_match else [], empty_string))))


def _check_pronouns(pronoun: str, last_nouns: list) -> list:
    """
    Get the most likely co-reference(s) for the pronoun using the last_nouns details.
    Subject/object information (the noun, and its types, mappings and IRI) is returned.

    :param pronoun: String holding the pronoun text
    :param last_nouns: An array of tuples of noun texts, types, mappings and IRI, from the current paragraph
    :return: Array of tuples of class_mappings and IRIs of already processed nouns that match the criteria;
              Note that an array is returned to support matching the pronouns 'they'/'them'
    """
    pronoun_details = []
    pronoun_lower = pronoun.lower()
    if pronoun == 'I' or pronoun_lower in ('me', 'myself'):
        pronoun_details.append(('Narrator', 'SINGPERSON', ':Person', ':Narrator'))
    elif pronoun_lower in ('we', 'us', 'ourselves'):
        # Find singular or plural person nouns (any gender)
        pronoun_details.extend(_check_criteria(pronoun_lower, last_nouns, None, None, True))
        pronoun_details.append(('Narrator', 'SINGPERSON', ':Person', ':Narrator'))
    elif pronoun_lower in ('they', 'them', 'themselves'):
        # Give preference to persons (any gender or number)
        noun_list = _check_criteria(pronoun_lower, last_nouns, None, None, True)
        if noun_list:
            pronoun_details.extend(noun_list)
        else:
            # Check for non-persons
            pronoun_details.extend(_check_criteria(pronoun_lower, last_nouns, None, None, False))
    elif pronoun_lower in ('she', 'herself'):
        # Find singular, feminine, person nouns
        pronoun_details.extend(_check_criteria(pronoun_lower, last_nouns, True, True, True))
    elif pronoun_lower in ('he', 'himself'):
        # Find singular, masculine, person nouns
        pronoun_details.extend(_check_criteria(pronoun_lower, last_nouns, True, False, True))
    elif pronoun_lower in ('it', 'itself'):
        # Find singular, non-person nouns (no gender)
        pronoun_details.extend(_check_criteria(pronoun_lower, last_nouns, True, None, False))
    return pronoun_details


def _update_last_nouns(text: str, text_type: str, text_iri: str, class_maps: list, last_nouns: list) -> (list, str):
    """
    Update the last_nouns array and return the class mappings and IRI.

    :param text: String holding the noun text
    :param text_type: String holding the noun type (such as 'FEMALESINGPERSON')
    :param text_iri: String holding the noun IRI
    :param class_maps: An array of strings holding the mapping(s) to the DNA ontology for the text
    :param last_nouns: An array of tuples of noun texts, types, mappings and IRI, from the current paragraph
    :return: A tuple that consists of the matched noun's class mappings and IRI, or an empty array and string
    """
    last_nouns.append((text, text_type, class_maps, text_iri))
    return class_maps, text_iri


def check_event(text: str, last_events: list) -> (list, str):
    """
    Get a possible verb/event mapping for the noun and check it against any events
    (from the current paragraph) that have a type = mapping.

    :param text: The text which is possibly mapped to an event
    :param last_events: The list/array of tuples defining event types and IRIs from the
                        current paragraph
    :return: A tuple specifying the event class mappings and IRI if there is a type match,
              or an empty list and string otherwise
    """
    ontol_classes, noun_ttl = get_noun_mapping(text, empty_string)   # Get the event class to which the noun is mapped
    if not ontol_classes:
        return [], empty_string
    poss_events = []
    for event_type, event_iri in last_events:
        if event_type in ontol_classes:
            poss_events.append(event_iri)
    if poss_events:
        return ontol_classes, poss_events[-1]
    return [], empty_string


def check_nouns(elem_dictionary: dict, key: str, alet_dict: dict, last_nouns: list, last_events: list,
                turtle: list, ext_sources: bool) -> list:
    """
    Get the subject or object nouns (as indicated by the key input parameter) in the dictionary,
    using last_nouns, alet_dict and last_events details to attempt to resolve co-references/anaphora.
    Subject/object information (the nouns and their types and IRIs) is returned.

    The order of checking for a match is last_nouns, alet_dict and then last_events. If there are no
    matches, a new noun is created and added to either last_nouns or last_events.

    For example, consider the sentence/chunk "She was sickly." following "Mary was born on June 12,
    1972, in Znojmo, Czechia." If the function parameters are (chunk_dictionary, 'subjects', 
    alet_dict, last_events), then the tuple, 'Mary', 'FEMALESINGPERSON' and ':Mary' will be returned
    since 'she' should be resolved to Mary.

    :param elem_dictionary: The dictionary (holding the details for the noun text and type from the spaCy parse)
    :param key: Either 'subjects' or 'objects'
    :param alet_dict: A dictionary holding the agents, locations, events & times encountered in
             the full narrative - For co-reference resolution; Keys = 'agents', 'locs', 'events', 
             'times' and Values vary by the key
    :param last_nouns: An array of tuples of noun texts, types, class mappings and IRIs,
                       found in the current paragraph
    :param last_events: An array of verb texts, mappings and IRIs from the current paragraph
    :param turtle: A list of Turtle statements which will be updated in this function if a new
                   noun is found
    :param ext_sources: A boolean indicating that data from GeoNames, Wikidata, etc. should be
                        added to the parse results if available
    :return: A tuple holding an array of tuples of the noun's texts, types, mappings and IRIs (also, the last_nouns and
              last_events arrays may be updated)
    """
    nouns = []
    for elem in elem_dictionary[key]:    # The subject or object nouns
        elem_key = key[0:-1]             # Create dictionary key = 'subject' or 'object'
        elem_text = elem[f'{elem_key}_text']
        elem_type = elem[f'{elem_key}_type']
        if elem_type == 'CARDINAL':      # For example, 'one of the band'
            if 'preps' in elem:
                # Assemble the full text to aid in the ontology mapping
                for prep in elem['preps']:
                    # TODO: Assess if more than the first detail_text is needed, since it is an array
                    elem_text += f' {prep["prep_text"]} {prep["prep_details"][0]["detail_text"]}'
            iri = f":{elem_text.replace(' ', '_')}_{str(uuid.uuid4())[:13]}"
            nouns.append((elem_text, 'CARDINAL', [owl_thing2], iri))
            turtle.extend([f'{iri} a owl:Thing .',
                           f'{iri} rdfs:label "{elem_text}" .'])
            continue
        if elem_text.lower() in pronouns:
            # Array of tuples of matched text, type, mappings and IRIs
            nouns.extend(_check_pronouns(elem_text, last_nouns))
            continue
        # Not a pronoun; Check for a match in instances of the ontology
        if ('PERSON' in elem_type or elem_type.endswith('GPE') or
                elem_type.endswith('ORG') or elem_type.endswith('NORP')):
            match_iri, match_type = check_specific_match(elem_text, elem_type)
            if match_iri:
                # Tuple = noun text, type and IRI
                nouns.append((elem_text, elem_type, match_type, match_iri))
                continue
        # No match - Try to match text and type in last_nouns and then the alet_dict
        match_noun_tuples = _check_last_nouns(elem_text, elem_type, last_nouns)
        if match_noun_tuples:
            nouns.append((elem_text, elem_type, match_noun_tuples[0][0], match_noun_tuples[0][1]))
            continue
        match_maps, match_iri = _check_alet_dict(elem_text, elem_type, alet_dict, last_nouns)   # May update last_nouns
        if match_iri:
            nouns.append((elem_text, elem_type, match_maps, match_iri))
            continue
        # No match - Check if the noun is aligned with an event that has already been described
        event_classes, event_iri = check_event(elem_text, last_events)
        if event_iri:
            # Tuple = string = 'event' and the noun text, event class mapping and IRI
            nouns.append((elem_text, elem_type, event_classes, event_iri))
            continue
        # No match - Create new entity
        # TODO: possessives - 'her father', 'her arm' or "Sue's arm" (versus 'her book')
        init_iri = f":{elem_text.replace(' ', '_')}_{str(uuid.uuid4())[:13]}"
        iri = re.sub(r'[^:a-zA-Z0-9_]', empty_string, init_iri)
        # Tuple = noun text, type and IRI
        noun_mappings, noun_turtle = create_noun_ttl(iri, elem_text, elem_type,
                                                     True if key == 'subjects' else False, ext_sources)
        nouns.append((elem_text, elem_type, noun_mappings, iri))
        turtle.extend(noun_turtle)
        last_nouns.append((elem_text, elem_type, noun_mappings, iri))
    return nouns


def check_specific_match(noun: str, noun_type: str) -> (str, str):
    """
    Checks if the concept/Agent/Location/... is already defined in the DNA ontologies.

    :param noun: String holding the text to be matched
    :param noun_type: String holding the noun type (PERSON/GPE/LOC/...) from spacy's NER
    :return: A tuple consisting of the matched IRI and its class mapping (if a match is found),
              or two empty strings
    """
    if noun_type.endswith('GPE') and noun in names_to_geo_dict:
        return f'geo:{names_to_geo_dict[noun]}', ':Country'
    class_type = get_agent_class(noun_type).replace('+:Collection', empty_string)   # PLURAL details ignored here
    match_details = query_database(
        'select', query_specific_noun.replace('keyword', noun).replace('class_type', class_type), ontologies_database)
    if match_details:
        return match_details[0]['iri']['value'].replace(dna_prefix, ':'), match_details[0]['type']['value']
    return empty_string, empty_string
