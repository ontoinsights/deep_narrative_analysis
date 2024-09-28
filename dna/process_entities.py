# Processing related to spaCy Named Entities (PERSON, NORP, ORG, GPE, LOC, FAC, EVENT, DATE, LAW,
#    PRODUCT, TIME, WORK_OF_ART)

import re
from rdflib import Literal
from unidecode import unidecode

from dna.create_entities_turtle import create_agent_ttl, create_location_ttl, create_named_entity_ttl, create_norp_ttl
from dna.query_openai import access_api, event_categories, noun_events_prompt
from dna.query_sources import get_event_details_from_wikidata, get_wikipedia_description
from dna.sentence_classes import Entity
from dna.utilities_and_language_specific import (check_name_gender, days, empty_string, months, names_to_geo_dict,
                                                 ner_dict, ner_types, underscore)

agent_classes = (':Person', ':Person, :Collection', ':GovernmentalEntity', ':GovernmentalEntity, :Collection',
                 ':OrganizationalEntity', ':OrganizationalEntity, :Collection', ':EthnicGroup',
                 ':EthnicGroup, :Collection', ':PoliticalGroup', ':PoliticalGroup, :Collection',
                 ':ReligiousGroup', ':ReligiousGroup, :Collection', ':Animal', ':Animal, :Collection',
                 ':Plant', ':Plant, :Collection')

location_classes = (':Location', ':PhysicalLocation', ':GovernmentalEntity', ':GovernmentalEntity, :Collection',
                    ':OrganizationalEntity', ':OrganizationalEntity, :Collection', ':EthnicGroup',
                    ':EthnicGroup, :Collection', ':PoliticalGroup', ':PoliticalGroup, :Collection',
                    ':ReligiousGroup', ':ReligiousGroup, :Collection', ':Animal', ':Animal, :Collection',
                    ':Plant', ':Plant, :Collection')

# TODO: (Future) Non-US dates
month_pattern = re.compile('|'.join(months))
year_pattern = re.compile('[0-9]{4}')
day_pattern1 = re.compile('[0-9] | [0-9],|[0-2][0-9] |[0-2][0-9],|3[0-1] |3[0-1],')
day_pattern2 = re.compile('|'.join(days))


def _create_time_iri(before_after_str: str, str_text: str, ymd_required: bool) -> str:
    """
    Creates an IRI for a time that is defined by a year, month and/or day.

    :param before_after_str: A string = 'before', 'after' or the empty string
    :param str_text: Text which holds a time
    :param ymd_required: Boolean indicating that a result should not be returned unless the
                time is specified using the format, name of the month - space - day numeric -
                space - 4 digit year (or just month, or month - space - year)
    :return: A string specified as ":PiT_", followed by an optional "_Yrxxxx", an optional
              "_Moxxxx" and an optional "_Dayxx", or an empty sting
    """
    year_search = year_pattern.search(str_text)
    month_search = month_pattern.search(str_text)
    day_search1 = day_pattern1.search(str_text)
    day_search2 = day_pattern2.search(str_text)
    if not year_search and not month_search and not day_search1 and not day_search2:
        if ymd_required:
            return empty_string
        else:
            return f':PiT_{str_text.lower().replace(space, underscore).replace(".", empty_string)}'
    if year_search or month_search or day_search1:
        return ':PiT' + (f'_{before_after_str}' if before_after_str else empty_string) \
               + (f'_Yr{year_search.group()}' if year_search else empty_string) \
               + (f'_Mo{month_search.group()}' if month_search else empty_string) \
               + (f'_Day{day_search1.group().replace(",", empty_string).strip()}' if day_search1 else empty_string)
    return ':PiT' + (f'_{before_after_str}' if before_after_str else empty_string) \
           + (f'_Day{day_search2.group()}' if day_search2 else empty_string)


def _get_last_name(agent_text: str) -> (str, str):
    """
    Get the last names for a person's name text. If there are multiple last names (e.g.,
    Mary Gardner Smith), then return both "Smith" and "Gardner Smith".

    :param agent_text: Text specifying the person's name
    :return: A tuple of two string holding a person's last names
    """
    split_names = agent_text.split()
    if len(split_names) == 1:
        return empty_string, empty_string
    if len(split_names) == 2:
        return split_names[1], empty_string
    return split_names[-1], " ".join(split_names)[-2:]    # TODO: (Future) Is this acceptable if a middle name is given?


# Future
def _get_name_permutations(name: str) -> list:
    """
    Get the combinations of first and middle/maiden/last names.

    :param name: A string holding a Person's full name
    :return: A list of strings combining the first and second, first and third, ... names
    """
    poss_names = []
    names = name.split()
    for i in range(1, len(names)):
        poss_names.append(f'{names[0]} {names[i]}')
    return poss_names


def _get_noun_ttl(sentence_text: str, noun_text: str, noun_type: str, nouns_dict: dict) -> (str, str, list):
    """
    Create Turtle for a new noun/entity.

    :param sentence_text: String holding the sentence
    :param noun_text: Text for the entity/noun
    :param noun_type: String holding the NER type identified by spaCy
    :param nouns_dict: A dictionary holding the nouns/named entities encountered in the narrative;
             The dictionary keys are the text for the noun, and its values are a tuple consisting
             of the spaCy entity type and the noun's IRI. An IRI value may be associated with
             more than 1 text. Note that this parameter is only used when processing quotations
             (in order to get the IRI of the speaker).
    :return: A tuple holding 2 strings with the noun's entity type and IRI, and an array of
             Turtle statements defining the noun (also, the nouns_dict may be updated)
    """
    labels = []
    base_type = noun_type.replace('PLURAL', empty_string).replace('SING', empty_string).\
        replace('FEMALE', empty_string).replace('MALE', empty_string)
    class_map = f'{ner_dict[base_type]}, :Correction'     # Identifying as possible Correction for co-ref resolution
    class_map = f'{class_map}, :Collection' if 'PLURAL' in noun_type and ':Collection' not in class_map else class_map
    if base_type == 'DATE':
        # TODO: Resolve how dates are managed
        # noun_iri = _create_time_iri(empty_string, noun_text, True)
        return empty_string, empty_string, []
    else:
        noun_iri = re.sub(r'[^:a-zA-Z0-9_]', underscore, noun_text.strip()).replace('__', underscore)
    noun_iri = f':{noun_iri[1:]}' if noun_iri.startswith(underscore) else f':{noun_iri}'
    noun_iri = noun_iri[:-2] if noun_iri.endswith(underscore) else noun_iri
    noun_ttl = [f'{noun_iri} :text {Literal(noun_text).n3()} .']
    # Process by location, agent, and event/other NER types
    if base_type in ('GPE', 'LOC', 'FAC', 'ORG'):    # spaCy incorrectly reports some locations as ORG
        geo_ttl, labels = create_location_ttl(noun_iri, noun_text, class_map, base_type)
        if geo_ttl:
            noun_ttl.extend(geo_ttl)
            base_type = 'LOC' if base_type == 'ORG' else base_type    # Found a location; Update the base_type
            class_map = class_map.replace('OrganizationalEntity', 'Location')    # And class_map
    if base_type in ('PERSON', 'NORP', 'ORG'):   # TODO: spaCy does not identify some companies as ORGs
        description_details = get_wikipedia_description(noun_text, class_map)
        if description_details.labels:
            labels.extend(description_details.labels)
        if noun_text not in description_details.labels:
            labels.append(noun_text)
        if 'NORP' not in noun_type:
            if 'PERSON' in noun_type:
                noun_type = check_name_gender(noun_text)
                last_name, last_name2 = _get_last_name(noun_text)
                if last_name and last_name not in nouns_dict and last_name not in labels:
                    labels.append(last_name)
            noun_ttl.extend(create_agent_ttl(noun_iri, labels, noun_type, class_map, description_details.wiki_desc,
                                             description_details.wiki_url, description_details.wikidata_id))
        else:   # NORP
            noun_ttl.extend(
                create_norp_ttl(noun_iri, labels, class_map, description_details.wiki_desc,
                                description_details.wiki_url, description_details.wikidata_id))
    elif base_type == 'EVENT':
        semantic_dict = access_api(noun_events_prompt.replace('{sent_text}', sentence_text)
                                   .replace('{noun_texts}', noun_text))
        if 'category_number' in semantic_dict and 0 < int(semantic_dict['category_number']) < len(event_categories):
            class_map = event_categories[int(semantic_dict['category_number']) - 1]
        else:
            class_map = ':EventAndState'
        event_details = get_event_details_from_wikidata(noun_text)
        if noun_text not in labels:
            labels.append(noun_text)
        start_time_iri = empty_string if not event_details.start_time else f':PiT_{event_details.start_time}'
        end_time_iri = empty_string if not event_details.end_time else f':PiT_{event_details.end_time}'
        noun_ttl.extend(create_named_entity_ttl(noun_iri, event_details.labels, class_map, event_details.wiki_desc,
                                                event_details.wiki_url, event_details.wikidata_id, start_time_iri,
                                                end_time_iri))
    else:
        if noun_text not in labels:
            labels.append(noun_text)
        noun_ttl.extend(create_named_entity_ttl(noun_iri, labels, class_map, empty_string))
    if len(noun_ttl) > 1:    # More than just the noun text is in the Turtle
        for label in labels:
            nouns_dict[label] = (noun_type, noun_iri)
    return noun_type, noun_iri, noun_ttl


def check_if_noun_is_known(noun_text: str, noun_type: str, nouns_dict: dict) -> (str, str):
    """
    Determines if the noun text has already been seen/processed and so is identified in the nouns_dict.

    :param noun_text: Input string specifying the noun text
    :param noun_type: String identifying NER type for the text, as defined by spaCy
    :param nouns_dict: A dictionary holding the nouns/named entities encountered in the narrative;
             The dictionary keys are the text for the noun, and its values are a tuple consisting
             of the spaCy entity type and the noun's IRI. An IRI value may be associated with
             more than 1 text. Note that this parameter is only used when processing quotations
             (in order to get the IRI of the speaker).
    :return: A tuple holding the spaCy entity type and IRI of the noun; The IRI may be
             empty if the noun has not already been encountered
    """
    if noun_text in names_to_geo_dict:                           # Location is a country name
        return noun_type, f'geo:{names_to_geo_dict[noun_text]}'
    if noun_text in nouns_dict:                                  # Key is text; exact match of text
        return nouns_dict[noun_text]
    if noun_text.islower() and len(noun_text) > 5:               # Check match of substring if not a proper noun
        for noun in nouns_dict:
            if noun_text in noun:
                return nouns_dict[noun]
    # TODO: (Future) Improve with synonym check
    return noun_type, empty_string


def process_ner_entities(sentence_text: str, entities: list, nouns_dict: dict) -> (list, list):
    """
    Handle entities identified by spaCy's NER.

    :param sentence_text: String holding the sentence
    :param entities: An array of instances of the Entity Class
    :param nouns_dict: A dictionary holding the nouns/named entities encountered in the narrative;
             The dictionary keys are the text for the noun, and its values are a tuple consisting
             of the spaCy entity type and the noun's IRI. An IRI value may be associated with
             more than 1 text.
    :return: A tuple consisting of two arrays: (1) the IRIs of the entities identified in the sentence,
             and 2) Turtle statements defining them (also the nouns_dict is likely updated)
    """
    new_entities = []
    # Handle location words occurring together - for ex, 'Paris, Texas' - which are returned as 2 separate entities
    if sentence_text and len(entities) > 1:
        offset = 0
        while offset < (len(entities) - 1):
            if not ('GPE' in entities[offset].ner_type or 'LOC' in entities[offset].ner_type):
                new_entities.append(entities[offset])
                offset += 1
            else:
                if f'{entities[offset].text}, {entities[offset + 1].text}' in sentence_text and \
                        (entities[offset].ner_type == entities[offset + 1].ner_type):  # Types same
                    new_entities.append(Entity(f'{entities[offset].text},{entities[offset + 1].text}',
                                               entities[offset].ner_type))
                    offset += 2
                else:
                    new_entities.append(entities[offset])
                    offset += 1
        if offset == (len(entities) - 1):
            new_entities.append(entities[offset])   # Add last entity
    else:
        new_entities.extend(entities)
    entities_ttl = []
    entity_iris = []
    for new_entity in new_entities:
        # Remove '.' to easily disambiguate (e.g.) US Supreme Court and U.S. Supreme Court
        entity_text = unidecode(new_entity.text.replace('.', empty_string))
        # Does the entity start with a capital letter (e.g., a proper noun)?
        if not entity_text[0].isupper():
            continue
        # Remove articles
        for article in ('a ', 'A ', 'an ', 'An ', 'the ', 'The '):
            if entity_text.startswith(article):
                entity_text = entity_text[len(article):]
                break
        if len(entity_text) < 2:
            continue
        # Remove "apostrophe" or "apostrophe s" at the end of the entity text (spaCy includes possessive)
        if re.findall(r"\u0027$", entity_text) or re.findall(r"\u2019$", entity_text):
            entity_text = entity_text[0:-1]
        elif re.findall(r"\u0027\u0073$", entity_text) or re.findall(r"\u2019\u0073$", entity_text):
            entity_text = entity_text[0:-2]
        entity_type, entity_iri = check_if_noun_is_known(entity_text, new_entity.ner_type, nouns_dict)
        if not entity_iri:
            # Need to define the Turtle for a new entity
            entity_type, entity_iri, new_ttl = \
                 _get_noun_ttl(sentence_text, entity_text, new_entity.ner_type, nouns_dict)
            if new_ttl:
                entities_ttl.extend(new_ttl)
        if entity_iri:
            entity_iris.append(entity_iri)
    return entity_iris, entities_ttl
