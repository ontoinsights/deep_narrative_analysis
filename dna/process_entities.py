# Processing related to spaCy Named Entities (PERSON, NORP, ORG, GPE, LOC, FAC, EVENT, DATE, LAW,
#    PRODUCT, TIME, WORK_OF_ART)

import re
from unidecode import unidecode

from dna.create_entities_turtle import create_agent_ttl, create_location_ttl, create_named_entity_ttl, create_norp_ttl
from dna.prompting_ontology_details import event_categories
from dna.query_openai import access_api, noun_events_prompt
from dna.query_sources import get_event_details_from_wikidata, get_wikipedia_description
from dna.sentence_classes import Entity
from dna.utilities_and_language_specific import add_unique_to_array, check_name_gender, days, empty_string, \
    literal, months, names_to_geo_dict, ner_dict, ner_types, underscore

agent_classes = (':Person', ':Person, :Collection', ':GovernmentalEntity', ':GovernmentalEntity, :Collection',
                 ':GeopoliticalEntity', ':GeopoliticalEntity, :Collection', ':OrganizationalEntity',
                 ':OrganizationalEntity, :Collection', ':EthnicGroup', ':EthnicGroup, :Collection',
                 ':PoliticalGroup', ':PoliticalGroup, :Collection', ':ReligiousGroup',
                 ':ReligiousGroup, :Collection', ':Animal', ':Animal, :Collection',
                 ':Plant', ':Plant, :Collection')

# TODO: (Future) Non-US dates
month_pattern = re.compile('|'.join(months))
year_pattern = re.compile('[0-9]{4}')
day_pattern1 = re.compile('[0-9] | [0-9],|[0-2][0-9] |[0-2][0-9],|3[0-1] |3[0-1],')
day_pattern2 = re.compile('|'.join(days))


def _get_names(agent_text: str) -> list:
    """
    Get the last names for a person's name text. If there are multiple last names (e.g.,
    Mary Gardner Smith), then return both "Smith" and "Gardner Smith".

    :param agent_text: Text specifying the person's name
    :return: An array holding first, middle and last names when names are separated by space or hyphen
    """
    all_names = []
    split_names = agent_text.split()
    for split_name in split_names:
        for name in split_name.split('-'):
            all_names.append(name)
    return all_names


def _get_noun_ttl(sentence_text: str, noun_text: str, noun_entity: Entity, nouns_dict: dict) -> (str, str, list):
    """
    Create Turtle for a new noun/entity.

    :param sentence_text: String holding the sentence
    :param noun_text: Text for the entity/noun
    :param noun_entity: String holding Entity class details for the noun
    :param nouns_dict: A dictionary holding the nouns/named entities encountered in the narrative;
             The dictionary keys are the text for the noun, and its values are a tuple consisting
             of the spaCy entity type and the noun's IRI. An IRI value may be associated with
             more than 1 text. Note that this parameter is only used when processing quotations
             (in order to get the IRI of the speaker).
    :return: A tuple holding 2 strings with the noun's entity type and IRI, and an array of
             Turtle statements defining the noun (also, the nouns_dict may be updated)
    """
    labels = []
    noun_type = noun_entity.ner_type
    base_type = noun_type.replace('PLURAL', empty_string).replace('SING', empty_string).\
        replace('FEMALE', empty_string).replace('MALE', empty_string)
    class_map = f'{ner_dict[base_type]}, :Correction'     # Identifying as possible Correction for co-ref resolution
    class_map = f'{class_map}, :Collection' if 'PLURAL' in noun_type and ':Collection' not in class_map else class_map
    if base_type == 'DATE':
        # TODO: Resolve how dates are managed
        # noun_iri = create_time_iri(empty_string, noun_text, True)
        return empty_string, empty_string, []
    else:
        noun_iri = re.sub(r'[^:a-zA-Z0-9_]', underscore, noun_text.strip()).replace('__', underscore)
    noun_iri = f':{noun_iri[1:]}' if noun_iri.startswith(underscore) else f':{noun_iri}'
    noun_iri = noun_iri[:-2] if noun_iri.endswith(underscore) else noun_iri
    noun_ttl = [f'{noun_iri} :text {literal(noun_text)} .']
    # Process by location, agent, and event/other NER types
    if base_type in ('GPE', 'LOC', 'FAC', 'ORG'):    # spaCy incorrectly reports some locations as ORG
        geo_ttl, labels = create_location_ttl(noun_iri, noun_text, class_map, base_type, noun_entity.also_knowns)
        if geo_ttl:
            noun_ttl.extend(geo_ttl)
            base_type = 'LOC' if base_type == 'ORG' else base_type    # Found a location; Update the base_type
            class_map = class_map.replace('OrganizationalEntity', 'Location')    # And class_map
    if base_type in ('PERSON', 'NORP', 'ORG'):   # TODO: spaCy does not identify some companies as ORGs
        description_details = get_wikipedia_description(noun_text, base_type)
        if description_details.labels:
            labels.extend(description_details.labels)
        if noun_text not in description_details.labels:
            labels.append(noun_text)
        add_unique_to_array(noun_entity.also_knowns, labels)
        if 'NORP' not in noun_type:
            if 'PERSON' in noun_type:
                noun_type = check_name_gender(noun_text)
                names = _get_names(noun_text)
                for name in names:
                    if name not in labels:
                        labels.append(name)
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
        add_unique_to_array(noun_entity.also_knowns, labels)
        start_time_iri = empty_string if not event_details.start_time else f':PiT_{event_details.start_time}'
        end_time_iri = empty_string if not event_details.end_time else f':PiT_{event_details.end_time}'
        noun_ttl.extend(create_named_entity_ttl(noun_iri, event_details.labels, class_map, event_details.wiki_desc,
                                                event_details.wiki_url, event_details.wikidata_id, start_time_iri,
                                                end_time_iri))
    else:
        if noun_text not in labels:
            labels.append(noun_text)
        add_unique_to_array(noun_entity.also_knowns, labels)
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
    if not noun_text:
        return noun_type, empty_string
    if noun_text in names_to_geo_dict:                           # Location is a country name
        return noun_type, f'geo:{names_to_geo_dict[noun_text]}'
    if noun_text in nouns_dict:                                  # Key is text; exact match of text
        return nouns_dict[noun_text]
    base_words = empty_string
    if ' ' in noun_text and any(c.isupper() for c in noun_text):
        # Start from the end of the string, e.g., "campaign" in "Democratic campaign" or
        #    "Harriet Hageman" in "challenger Harriet Hageman"
        noun_words = noun_text.split()
        noun_words.reverse()
        if noun_words[0][0].isupper():     # Get only upper case words
            for noun_word in noun_words:
                if noun_word[0].islower():
                    break
                base_words = f'{noun_word} {base_words}'.strip()
        else:     # Get only lower case words
            for noun_word in noun_words:
                if noun_word[0].isupper():
                    break
                base_words = f'{noun_word} {base_words}'.strip()
    noun_string = noun_text if not base_words else base_words
    # Check for a substring match in base_words
    matches = [noun for noun in nouns_dict.keys() if noun in noun_string]   # E.g., "Cheney" in "Rep. Liz Cheney"
    if len(matches) >= 1:
        return nouns_dict[matches[0]]
    # TODO: else: Return most recent match
    # Check for the base_word in the encountered nouns - e.g., "campaign" in "Biden-Harris campaign"
    matches = [noun for noun in nouns_dict.keys() if noun_string in noun]
    if len(matches) >= 1:
        return nouns_dict[matches[0]]
    # TODO: else: Return most recent match
    return noun_type, empty_string


def create_time_iri(before_after_str: str, str_text: str, ymd_required: bool) -> str:
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
            time_text = re.sub(r'[^A-Za-z0-9 ]', '', str_text)
            return f':PiT_{time_text.lower().replace(" ", underscore)}'
    if year_search or month_search or day_search1:
        return ':PiT' + (f'_{before_after_str}' if before_after_str else empty_string) \
               + (f'_Yr{year_search.group()}' if year_search else empty_string) \
               + (f'_Mo{month_search.group()}' if month_search else empty_string) \
               + (f'_Day{day_search1.group().replace(",", empty_string).strip()}' if day_search1 else empty_string)
    return ':PiT' + (f'_{before_after_str}' if before_after_str else empty_string) \
           + (f'_Day{day_search2.group()}' if day_search2 else empty_string)


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
                                               entities[offset].ner_type, []))
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
        # Remove articles and conjunctions
        for article in ('a ', 'A ', 'an ', 'An ', 'the ', 'The '):
            if entity_text.startswith(article):
                entity_text = entity_text[len(article):].strip()
                break
        for conj in (' and', ' or'):
            if entity_text.endswith(conj):
                entity_text = entity_text[:len(article) * -1].strip()
                break
        # Does the entity start with a capital letter (e.g., is it a proper noun)?
        if not entity_text[0].isupper():
            found = -1
            for i, char in enumerate(entity_text):
                if char.isupper():
                    found = i
                    break
            entity_text = entity_text[found:].strip()
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
                 _get_noun_ttl(sentence_text, entity_text, new_entity, nouns_dict)
            if new_ttl:
                entities_ttl.extend(new_ttl)
        if entity_iri:
            entity_iris.append(entity_iri)
    return entity_iris, entities_ttl
