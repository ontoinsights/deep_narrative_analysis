# Processing related to spaCy Named Entities (PERSON, NORP, ORG, GPE, LOC, FAC, EVENT, DATE, LAW,
#    PRODUCT, TIME, WORK_OF_ART)

import re
from rdflib import Literal

from dna.create_entities_turtle import create_agent_ttl, create_location_ttl, create_named_entity_ttl, create_norp_ttl
from dna.query_openai import access_api, categories, noun_category_prompt, wikipedia_prompt
from dna.query_sources import get_event_details_from_wikidata, get_wikipedia_description
from dna.sentence_classes import Entity
from dna.utilities_and_language_specific import add_unique_to_array, check_name_gender, days, empty_string, months, \
    names_to_geo_dict, ner_dict, ner_types, underscore

agent_classes = (':Person', ':Person, :Collection', ':GovernmentalEntity', ':GovernmentalEntity, :Collection',
                 ':OrganizationalEntity', ':OrganizationalEntity, :Collection', ':EthnicGroup',
                 ':EthnicGroup, :Collection', ':PoliticalGroup', ':PoliticalGroup, :Collection',
                 ':ReligiousGroup', ':ReligiousGroup, :Collection', ':Animal', ':Animal, :Collection',
                 ':Plant', ':Plant, :Collection')

honorifics = ('Mr. ', 'Mrs. ', 'Ms. ', 'Doctor ', 'Dr. ', 'Messrs. ', 'Miss ', 'Mx. ', 'Sir ',
              'Dame ', 'Lady ', 'Esq. ', 'Professor ', 'Fr. ', 'Sr. ')

# TODO: Non-US dates
month_pattern = re.compile('|'.join(months))
year_pattern = re.compile('[0-9]{4}')
day_pattern1 = re.compile('[0-9] | [0-9],|[0-2][0-9] |[0-2][0-9],|3[0-1] |3[0-1],')
day_pattern2 = re.compile('|'.join(days))

ner_translation = {'PERSON': 'person',
                   'NORP': 'nationality, religion or political group/ideology',
                   'ORG': 'organization',
                   'GPE': 'geopolitical entity',
                   'LOC': 'location',
                   'FAC': 'facility',
                   'EVENT': 'event or condition',
                   'LAW': 'law or policy',
                   'PRODUCT': 'product',
                   'WORK_OF_ART': 'work of art'}


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


def _get_family_names(agent_text: str, alt_names: list) -> list:
    """
    Create the possible permutations of a person's name.

    :param agent_text: Text specifying the person's name
    :param alt_names: An array of possible alternative names for the person
    :return: An array of possible family names (if the agent_name includes a space) and
             the alt_names array is likely updated
    """
    no_paren_agent_text = agent_text.replace('(', empty_string).replace(')', empty_string)
    split_names = no_paren_agent_text.split()
    family_names = []
    if len(split_names) > 1:
        for i in range(1, len(split_names)):      # TODO: Need to distinguish middle names vs last names?
            if split_names[i].endswith('s'):
                family_names.append(f'{split_names[i]}es')
            else:
                family_names.append(f'{split_names[i]}s')
    add_unique_to_array(split_names, alt_names)
    add_unique_to_array(get_name_permutations(no_paren_agent_text), alt_names)
    add_unique_to_array([agent_text, no_paren_agent_text], alt_names)
    return family_names


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
    class_map = ner_dict[base_type]
    if 'PLURAL' in noun_type and ':Collection' not in class_map:
        class_map += ', :Collection'
    if base_type == 'DATE':
        # TODO: Resolve how dates are managed
        # noun_iri = _create_time_iri(empty_string, noun_text, True)
        return empty_string, empty_string, []
    else:
        noun_iri = re.sub(r'[^:a-zA-Z0-9_]', underscore, f':{noun_text}').replace('__', '_')
    noun_ttl = [f'{noun_iri} :text {Literal(noun_text).n3()} .']
    # Process by location, agent, and event/other NER types
    org_as_loc = False
    if base_type in ('GPE', 'LOC', 'FAC', 'ORG'):     # spaCy incorrectly reports some locations as ORG
        geo_ttl, labels = create_location_ttl(noun_iri, noun_text, class_map)
        if geo_ttl:
            noun_ttl.extend(geo_ttl)
            org_as_loc = True if base_type == 'ORG' else False
    if base_type in ('PERSON', 'NORP', 'ORG') and not org_as_loc:
        wiki_details, wiki_url, wikidata_id, labels = \
            get_wikipedia_description(noun_text, class_map)
        if not labels:
            wiki_details = wiki_url = wikidata_id = empty_string
        if noun_text not in labels:
            labels.append(noun_text)
        if 'NORP' not in noun_type:
            family_names = []
            if 'PERSON' in noun_type:
                noun_type = check_name_gender(noun_text)
                family_names = _get_family_names(noun_text, labels)
            noun_ttl.extend(create_agent_ttl(noun_iri, labels, noun_type, class_map, wiki_details,
                                             wiki_url, wikidata_id))      # Put more specific name first
            for fam_name in family_names:
                if fam_name not in nouns_dict:
                    nouns_dict[fam_name] = ('PLURALPERSON', f':{fam_name}')
                    noun_ttl.append(f':{fam_name} a :Person, :Collection ; '
                                    f'rdfs:label "{fam_name}" ; :role "family" .')
        else:   # NORP
            noun_ttl.extend(
                create_norp_ttl(noun_iri, noun_type, labels, wiki_details, wiki_url, wikidata_id))
    elif base_type == 'EVENT':
        semantic_dict = access_api(noun_category_prompt.replace('{sent_text}', sentence_text)
                                   .replace('{noun_text}', noun_text))
        if 'category_number' in semantic_dict and (0 < semantic_dict['category_number']
                                                     < len(categories)):
            class_map = categories[semantic_dict['category_number'] - 1]
        else:
            class_map = ':EventAndState'
        wiki_details, wiki_url, wikidata_id, start_time, end_time, labels = \
            get_event_details_from_wikidata(noun_text)
        if noun_text not in labels:
            labels.append(noun_text)
        start_time_iri = empty_string if not start_time else _create_time_iri(empty_string, start_time, False)
        end_time_iri = empty_string if not end_time else _create_time_iri(empty_string, end_time, False)
        noun_ttl.extend(create_named_entity_ttl(noun_iri, labels, class_map, wiki_details,
                                                wiki_url, wikidata_id, start_time_iri, end_time_iri))
    else:
        if noun_text not in labels:
            labels.append(noun_text)
        noun_ttl.extend(create_named_entity_ttl(noun_iri, labels, class_map, empty_string))
    for label in labels:
        if label not in nouns_dict:
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
    for noun_key in nouns_dict:                                  # Key is text
        if noun_key == noun_text or ('PERSON' in noun_type and noun_key in noun_text):      # Strings match
            return nouns_dict[noun_key]
    return noun_type, empty_string


def get_name_permutations(name: str) -> list:
    """
    Get the combinations of first and maiden/last names.

    :param name: A string holding a Person's full name
    :return: A list of strings combining the first and second, first and third, ... names
    """
    poss_names = []
    names = name.split()
    for i in range(1, len(names)):
        poss_names.append(f'{names[0]} {names[i]}')
    return poss_names


def get_ner_base_type(ner_text: str) -> str:
    """
    Iterate through the NER types to get the base type in the string, ner_text.

    :param ner_text: String holding the full NER categorization
    :return: String holding the NER base type (PERSON, LOC, GPE, ...)
    """
    ner_base = empty_string
    for ner_type in ner_types:
        if ner_type in ner_text:
            ner_base = ner_type
            break
    return ner_base


def process_ner_entities(sentence_text: str, entities: list, nouns_dict: dict) -> (list, list):
    """
    Handle entities identified by spaCy's NER.

    :param sentence_text: String holding the sentence
    :param entities: An array of instances of the Entity Class
    :param nouns_dict: A dictionary holding the nouns/named entities encountered in the narrative;
             The dictionary keys are the text for the noun, and its values are a tuple consisting
             of the spaCy entity type and the noun's IRI. An IRI value may be associated with
             more than 1 text.
    :return: A tuple consisting of two arrays: (1) the IRIs of the agents identified in the sentence,
             and 2) Turtle statements defining them (also the nouns_dict is likely updated)
    """
    new_entities = []
    # Handle location words occurring together - for ex, 'Paris, Texas' - which are returned as 2 separate entities
    if len(entities) > 1:
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
        new_entities.append(entities[0])
    entities_ttl = []
    entity_iris = []
    for new_entity in new_entities:
        entity_text = new_entity.text
        # Remove articles
        for article in ('a ', 'A ', 'an ', 'An ', 'the ', 'The '):
            if entity_text.startswith(article):
                entity_text = entity_text[len(article):]
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
