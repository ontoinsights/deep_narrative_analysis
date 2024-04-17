# Processing related to spaCy Named Entities (PERSON, NORP, ORG, GPE, LOC, FAC, EVENT, DATE, LAW,
#    PRODUCT, TIME, WORK_OF_ART)

import re

from dna.create_entities_turtle import create_agent_ttl, create_location_ttl, create_named_entity_ttl, create_norp_ttl
from dna.query_openai import access_api, name_check_prompt, wikipedia_prompt
from dna.query_sources import get_event_details_from_wikidata, get_wikidata_labels, get_wikipedia_description
from dna.utilities_and_language_specific import check_name_gender, days, empty_string, months, \
    names_to_geo_dict, ner_dict, underscore

agent_classes = (':Person', ':Person, :Collection', ':GovernmentalEntity', ':OrganizationalEntity',
                 ':EthnicGroup', ':PoliticalGroup', ':ReligiousGroup', ':Animal', ':Plant')

honorifics = ('Mr. ', 'Mrs. ', 'Ms. ', 'Doctor ', 'Dr. ', 'Messrs. ', 'Miss ', 'Mx. ', 'Sir ',
              'Dame ', 'Lady ', 'Esq. ', 'Professor ', 'Fr. ', 'Sr. ')

# TODO: Non-US dates
month_pattern = re.compile('|'.join(months))
year_pattern = re.compile('[0-9]{4}')
day_pattern1 = re.compile('[0-9] | [0-9],|[0-2][0-9] |[0-2][0-9],|3[0-1] |3[0-1],')
day_pattern2 = re.compile('|'.join(days))

ner_translation = {'PERSON': 'person',
                   'NORP': 'group of people',
                   'ORG': 'organization',
                   'GPE': 'geopolitical entity',
                   'LOC': 'location',
                   'FAC': 'location',
                   'EVENT': 'event or condition',
                   'LAW': 'law or policy',
                   'PRODUCT': 'product',
                   'WORK_OF_ART': 'work of art'}


def _check_wikipedia_match(entity_type: str, wiki_details: str) -> bool:
    """
    Using OpenAI, evaluate if the entity identified by Wikipedia matches the NER type identified
    by spaCy.

    :param entity_type: String holding the NER entity type from spaCy
    :param wiki_details: String holding the results returned by Wikipedia for the noun
    :return: True if the Wikipedia details are consistent with the entity_type; Otherwise, False
    """
    results_dict = access_api(
        wikipedia_prompt.replace("{text_type}", ner_translation[entity_type]).replace("{wiki_def}", wiki_details))
    if type(results_dict['consistent']) is int:
        return results_dict['consistent']
    else:
        return False


def _create_time_iri(before_after_str: str, str_text: str, ymd_required: bool) -> str:
    """
    Creates an IRI for a time that is defined by a year, month and/or day.

    :param before_after_str: A string = 'before', 'after' or the empty string
    :param str_text: Text which holds a time
    :param ymd_required: Boolean indicating that a result should not be returned unless the
                time is specified using the format, name of the month - space - day numeric -
                space - 4 digit year (or just month, or month - space - year)  # TODO: Expand
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
             the alt_names array may be updated
    """
    no_paren = agent_text.replace('(', empty_string).replace(')', empty_string)
    split_names = no_paren.split()
    for name in split_names:
        if name not in alt_names:
            alt_names.append(name)
    perm_list = []
    family_names = []
    if len(split_names) > 1:
        for i in range(1, len(split_names)):      # TODO: Does not distinguish middle names vs last names
            if split_names[i].endswith('s'):
                family_names.append(f'{split_names[i]}es')
            else:
                family_names.append(f'{split_names[i]}s')
        perm_list = get_name_permutations(no_paren)
    for name in perm_list:
        if name not in alt_names:
            alt_names.append(name)
    if agent_text not in alt_names:
        alt_names.append(agent_text)
    if no_paren not in alt_names:
        alt_names.append(no_paren)
    return family_names


def _get_noun_ttl(noun_text: str, noun_type: str, nouns_dict: dict) -> (str, str, list):
    """
    Create Turtle for a new noun/entity.

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
    noun_iri = re.sub(r'[^:a-zA-Z0-9_]', underscore, f':{noun_text}').replace('__', '_')
    noun_ttl = []
    labels = []
    base_type = noun_type.replace('PLURAL', empty_string).replace('SING', empty_string).\
        replace('FEMALE', empty_string).replace('MALE', empty_string)
    class_map = ner_dict[base_type]
    if 'PLURAL' in noun_type and ':Collection' not in class_map:
        class_map += ', :Collection'
    # Process by location, agent, and event/other NER types
    if 'GPE' in noun_type or 'LOC' in noun_type or 'FAC' in noun_type:
        geo_ttl, labels = create_location_ttl(noun_iri, noun_text, class_map)
        noun_ttl.extend(geo_ttl)
    elif 'PERSON' in noun_type or 'NORP' in noun_type or 'ORG' in noun_type:
        wiki_details, wiki_url, wikidata_id = get_wikipedia_description(noun_text.replace(' ', underscore))
        if wiki_details and 'See the web site' not in wiki_details:
            consistent_semantics = _check_wikipedia_match(noun_type, wiki_details)
            if consistent_semantics:
                labels = get_wikidata_labels(wikidata_id)
            else:
                wiki_details = wiki_url = wikidata_id = empty_string
                labels = []
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
                create_norp_ttl(noun_iri, noun_type, labels, class_map, wiki_details, wiki_url, wikidata_id))
    elif 'DATE' in noun_type:
        time_iri = _create_time_iri(empty_string, noun_text, True)
        if not time_iri:
            return empty_string, empty_string, []
        noun_ttl.append(f'{time_iri} a :PointInTime ; rdfs:label "{noun_text}" .')
    else:
        start_time_iri = empty_string
        end_time_iri = empty_string
        if 'EVENT' in noun_type:
            wiki_details, wiki_url, wikidata_id, start_time, end_time, labels = \
                get_event_details_from_wikidata(noun_text)
            if start_time:
                start_time_iri = _create_time_iri(empty_string, start_time, False)
            if end_time:
                end_time_iri = _create_time_iri(empty_string, end_time, False)
        else:
            wiki_details, wiki_url, wikidata_id = get_wikipedia_description(noun_text.replace(' ', underscore))
            if wiki_details and 'See the web site' not in wiki_details:
                consistent_semantics = _check_wikipedia_match(noun_type, wiki_details)
                if consistent_semantics:
                    labels = get_wikidata_labels(wiki_details.split('wikibase_item: ')[1].split(')')[0])
                else:
                    wikidata_id = wiki_details = wiki_url = empty_string
                    labels = []
        if noun_text not in labels:
            labels.append(noun_text)
        noun_ttl.extend(create_named_entity_ttl(noun_iri, labels, class_map, wiki_details,
                                                wiki_url, wikidata_id, start_time_iri, end_time_iri))
    for label in labels:
        if label not in nouns_dict:
            nouns_dict[label] = (noun_type, noun_iri)
    return noun_type, noun_iri, noun_ttl


def check_if_noun_is_known(noun_text: str, noun_type: str, nouns_dict: dict) -> (str, str):
    """
    Determines if the noun is already processed and identified in the nouns_dict.

    :param noun_text: Input string specifying the noun text
    :param noun_type: String identifying NER type for the text, as defined by spaCy
    :param nouns_dict: A dictionary holding the nouns/named entities encountered in the narrative;
             The dictionary keys are the text for the noun, and its values are a tuple consisting
             of the spaCy entity type and the noun's IRI. An IRI value may be associated with
             more than 1 text. Note that this parameter is only used when processing quotations
             (in order to get the IRI of the speaker).
    :return: A tuple holding the spaCy entity type and IRI of the noun; The IRI may be
             empty if the noun is not known
    """
    if noun_text in names_to_geo_dict:                           # Location is a country name
        return noun_type, f'geo:{names_to_geo_dict[noun_text]}'
    for noun_key in nouns_dict:                                  # Key is text
        if noun_key == noun_text:                                # Strings match
            return nouns_dict[noun_key]
    for noun_key in nouns_dict:                                  # Trying again with partial match
        if noun_text in noun_key or noun_key in noun_text:       # Strings might match
            match_dict = access_api(
                name_check_prompt.replace("{noun1_text}", noun_text).replace("{noun2_text}", noun_key))
            if 'probability' in match_dict and (type(match_dict['probability']) is int or
                                                match_dict['probability'].isdigit()):
                if int(match_dict['probability']) > 85:
                    return nouns_dict[noun_key]
    return noun_type, empty_string


def get_name_permutations(name: str) -> list:
    """
    Get the combinations of first and maiden/last names. This is public to enable testing.

    :param name: A string holding a Person's full name
    :return: A list of strings combining the first and second, first and third, ... names
    """
    poss_names = []
    names = name.split()
    for i in range(1, len(names)):
        poss_names.append(f'{names[0]} {names[i]}')
    return poss_names


def get_sentence_entities(sentence: str, entities: list, nouns_dict: dict) -> (list, list):
    """
    Handle entities identified by spaCy's NER.

    :param sentence: The sentence text
    :param entities: An array of strings identifying the named entities using the format,
                     "entity_text+spaCy_entity_type"
    :param nouns_dict: A dictionary holding the nouns/named entities encountered in the narrative;
             The dictionary keys are the text for the noun, and its values are a tuple consisting
             of the spaCy entity type and the noun's IRI. An IRI value may be associated with
             more than 1 text.
    :return: A tuple consisting of two arrays: (1) the IRIs of the agents identified in the sentence,
             and 2) Turtle statements defining them (also the nouns_dict may be updated)
    """
    new_entities = []
    # Handle location words occurring together - for ex, 'Paris, Texas' - which are returned as 2 separate entities
    if len(entities) > 1:
        offset = 0
        while offset < (len(entities) - 1):
            if not ('GPE' in entities[offset].split("+")[1] or 'LOC' in entities[offset].split("+")[1]):
                new_entities.append(entities[offset])
                offset += 1
            else:
                if f'{entities[offset]}, {entities[offset + 1]}' in sentence and \
                        (entities[offset].split("+")[1] == entities[offset + 1].split("+")[1]):  # Types same
                    new_entities.append(
                        f'{entities[offset].split("+")[0]},{entities[offset + 1].split("+")[0]}'
                        f'+{entities[offset].split("+")[1]}')
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
        entity_split = new_entity.split('+')
        entity_text = entity_split[0]
        # Remove articles
        if entity_text.startswith('a ') or entity_text.startswith('A '):
            entity_text = entity_text[2:]
        if entity_text.startswith('an ') or entity_text.startswith('An '):
            entity_text = entity_text[3:]
        if entity_text.startswith('the ') or entity_text.startswith('The '):
            entity_text = entity_text[4:]
        if len(entity_text) < 2:
            continue
        # Remove "apostrophe" or "apostrophe s" at the end of the entity text (spaCy includes possessive)
        if re.findall(r"\u0027$", entity_text) or re.findall(r"\u2019$", entity_text):
            entity_text = entity_text[0:-1]
        elif re.findall(r"\u0027\u0073$", entity_text) or re.findall(r"\u2019\u0073$", entity_text):
            entity_text = entity_text[0:-2]
        entity_type, entity_iri = check_if_noun_is_known(entity_text, entity_split[1], nouns_dict)
        if not entity_iri:
            # Need to define the Turtle for a new entity
            # Future: Check ontology; Is the entity already defined in a background ontology?
            entity_type, entity_iri, new_ttl = \
                _get_noun_ttl(entity_text, entity_type, nouns_dict)
            if new_ttl:
                entities_ttl.extend(new_ttl)
        if entity_iri:
            entity_iris.append(entity_iri)
    return entity_iris, entities_ttl
