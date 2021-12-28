# Processing related to time and locations
# Called from create_event_turtle.py

import logging
import os
import pickle
import re

from database import query_database
from query_ontology_and_sources import get_geonames_location
from nlp import get_named_entity_in_string, get_proper_nouns, get_time_details
from utilities import domain_database, empty_string, months, preps_string, resources_root, space, verbs_string

# A dictionary where the keys are country names and the values are the GeoNames country codes
geocodes_file = os.path.join(resources_root, 'country_names_mapped_to_geo_codes.pickle')
with open(geocodes_file, 'rb') as inFile:
    names_to_geo_dict = pickle.load(inFile)

month_pattern = re.compile('|'.join(months))
year_pattern = re.compile('[0-9]{4}')

query_domain_event = \
    'prefix : <urn:ontoinsights:dna:> SELECT ?inst ?prob WHERE ' \
    '{ { ?inst :noun_synonym ?nsyn . FILTER(?nsyn = "keyword") . BIND(100 as ?prob) } UNION ' \
    '{ ?inst rdfs:label ?label . FILTER(?label = "keyword") . BIND(100 as ?prob) } UNION ' \
    '{ ?inst :noun_synonym ?nsyn . FILTER(CONTAINS(?nsyn, "keyword")) . BIND(90 as ?prob) } UNION ' \
    '{ ?inst rdfs:label ?label . FILTER(CONTAINS(?label, "keyword")) . BIND(90 as ?prob) } UNION ' \
    '{ ?inst :noun_synonym ?nsyn . FILTER(CONTAINS("keyword", ?nsyn)) . BIND(85 as ?prob) } UNION ' \
    '{ ?inst rdfs:label ?label . FILTER(CONTAINS("keyword", ?label)) . BIND(85 as ?prob) } } ' \
    'ORDER BY DESC(?prob)'

query_event_time = 'prefix : <urn:ontoinsights:dna:> SELECT ?time ?begin ?end WHERE ' \
                   '{ uri a ?type . OPTIONAL { uri :has_time ?time } ' \
                   'OPTIONAL { uri :has_beginning ?begin } OPTIONAL { uri :has_end ?end } }'


def check_to_loc(dictionary: dict, list_locs: list, new_locs: list):
    """
    Identify locations associated with a verb using the preposition, 'to'.

    :param dictionary: A verb dictionary
    :param list_locs: An array of location entities
    :param new_locs: An array of location entities whose associating preposition is 'to'
    :return: None (new_locs is updated)
    """
    for prep in dictionary:
        prep_str = str(prep)
        if prep_str[prep_str.find("prep_text': '") + 13:].startswith('to'):
            for loc in list_locs:
                if loc in prep_str:
                    new_locs.append(loc)
    return


def get_event_time_from_domain(sent_date: str, time: str) -> str:
    """
    Check if an Event mentioned in the sentence details (and extracted as a named entity) is found
    in the domain ontology files.

    :param sent_date: The event text
    :param time: The current time details (at this point, only the string, 'before', 'after' or
                 an empty string
    :return: The time as defined by an Event's :has_time, :has_beginning or :has_end predicates
    """
    # SHOULD find the event in the domain ontology modules
    results = query_database(
        'select', query_domain_event.replace('keyword', sent_date), domain_database)
    if results:
        event_uri = f":{results[0]['inst']['value'].split(':')[-1]}"
        # Get the :has_time, :has_beginning or :has_end details for the event
        time_results = query_database(
            'select', query_event_time.replace('uri', event_uri), domain_database)
        if time_results:
            time_result = time_results[0]
            time_result_keys = time_result.keys()
            if 'time' in time_result_keys:
                time += time_result['time']['value']
            elif 'begin' in time_result_keys and 'end' in time_result_keys:
                if time.startswith('before'):
                    time += time_result['begin']['value']
                elif time.startswith('after'):
                    time += time_result['end']['value']
                else:
                    # TODO: Needs both beginning and end times
                    time += time_result['begin']['value']
            elif 'begin' in time_result_keys and 'end' not in time_result_keys:
                time += time_result['begin']['value']
            elif 'end' in time_result_keys and 'begin' not in time_result_keys:
                time += time_result['end']['value']
    else:
        logging.warning(f'Could not find the event, {sent_date}, in the domain ontologies')
        time += f':Event{sent_date.replace(" ", "_")}'
    return time


def get_location_uri_and_ttl(loc: str, processed_locs: dict) -> (str, list):
    """
    Get a location URI based on the input string and if appropriate, add the Turtle explaining/
    defining that location.

    :param loc: Input location string
    :param processed_locs: A dictionary of location texts (keys) and their URI (values) of
                           all locations already processed
    :return: A string holding the location URI using a GeoNames prefix or the DNA prefix, and an
             array of strings that are the Turtle for a new location
    """
    loc_ttl = []
    if loc in names_to_geo_dict.keys():   # Location is a country name
        return f'geo:{names_to_geo_dict[loc]}', loc_ttl
    if loc in processed_locs.keys():      # Location is already captured
        return processed_locs[loc], loc_ttl
    split_locs = loc.split(space)
    if len(split_locs) == 1:
        loc_uri = f':{loc}'
    else:
        if loc.lower().startswith('the '):
            loc = space.join(split_locs[1:])
        loc_uri = f':{loc.replace(space,"_")}'
    # Check if the location is known - May be a city/town name
    loc_ttl = _create_geonames_ttl(loc_uri, loc)
    if not loc_ttl:
        containing_uri = empty_string
        # Need to get strings that are the Proper Nouns
        # Can't parse "loc" text directly since there is a problem in the NLP results
        # For example, the phrase, "Czernowitz ghetto", is completely returned as a GPE
        # But the text, "New York City ghetto", only returns "New York City" as the GPE
        proper_nouns = get_proper_nouns(loc)
        if proper_nouns:
            if proper_nouns in processed_locs.keys():
                containing_uri = processed_locs[proper_nouns]
            else:
                containing_uri = proper_nouns.replace(space, "_")
                containing_ttl = _create_geonames_ttl(containing_uri, proper_nouns)
                if containing_ttl:
                    loc_ttl.extend(containing_ttl)
                    processed_locs[proper_nouns] = containing_uri
                else:
                    # Could not get geonames definition
                    containing_uri = empty_string
        # TODO: Generalize a part of a city beyond ghetto
        if 'ghetto' in loc:
            loc_ttl.append(f'{loc_uri} a :Ghetto ; rdfs:label "{loc}" .')
        else:
            loc_ttl.append(f'{loc_uri} a :PopulatedPlace ; rdfs:label "{loc}" .')
        if containing_uri:
            loc_ttl.append(f'{containing_uri} :has_component {loc_uri} .')
    # Record location text in processed_locs so that the details are not added again
    processed_locs[loc] = loc_uri
    return loc_uri, loc_ttl


def get_sentence_location(sentence_dictionary: dict, last_loc: str) -> str:
    """
    Determine if a new location is specified in the sentence (as defined by the
    sentence_dictionary). A location in the sentence is identified by spaCy's entity
    recognition and stored in the sentence dictionary, with the key, LOCS. If any of the
    strings in the LOCS value are defined in the verb clause (likely as the objects of the
    prepositions, 'in', 'at', 'to', 'from'), then they are retained. Subsequent processing
    (in this function) tries to select a single string as the main location for the sentence.

    :param sentence_dictionary: The sentence dictionary
    :param last_loc: The location from the previous sentence
    :return: A new location or the empty string (if there is no new location)
    """
    # TODO: Imprecise location (home, house, town, village, ...)
    new_locs = []
    _add_str_to_array(sentence_dictionary, 'LOCS', new_locs)
    if not new_locs and not last_loc:
        # There is no location in the verb prepositions, and there is no previous loc
        # So, use the LOCS value despite it not being in the verb prepositions
        new_locs.extend(sentence_dictionary['LOCS'])
    if len(new_locs) == 1:
        return new_locs[0]
    elif len(new_locs) > 1:
        # Try to reduce locations to only ones associated directly with the main verb using the preposition 'to'
        revised_locs = []
        for verb in sentence_dictionary[verbs_string]:
            if preps_string in verb.keys():
                check_to_loc(verb[preps_string], new_locs, revised_locs)
            if 'verb_xcomp' in verb.keys():
                for xcomp in verb['verb_xcomp']:
                    if preps_string in xcomp.keys():
                        check_to_loc(xcomp[preps_string], new_locs, revised_locs)
        if len(revised_locs):
            return revised_locs[0]
        else:
            return new_locs[0]
    else:
        return empty_string


def get_sentence_time(sentence_dictionary: dict, last_date: str, processed_dates: list) -> (str, list):
    """
    Determine if a date/time is specified in the sentence (as defined by the sentence_dictionary).
    An event/date/time in the sentence is identified by spaCy's entity recognition and stored in the
    sentence dictionary, with the key, TIMES. If any of the strings in the TIMES value are specified
    in the verb clause (likely as the objects of the prepositions, 'in', 'at', 'during', 'before',
    'after'), then they are retained. Subsequent processing (in this function) tries to select
    a single string as the defining time for the sentence.

    :param sentence_dictionary: The sentence dictionary
    :param last_date: The inferred (or explicit) time of the event, formatted as:
                      ('before'|'after'|'') (PointInTime_date|Existing_Event_URI)
    :param processed_dates: A list of all dates whose Turtle has already been created
    :return: A tuple consisting of the string, ('before'|'after'|'') (PointInTime_date|Existing_Event_URI),
             and the Turtle for any new date/event instances. In addition, the processed_dates array may
             be updated.
    """
    # TODO: Imprecise time (morning, evening, day, night, ...)
    new_dates = []
    times_in_key = False
    events_in_key = False
    if 'TIMES' in sentence_dictionary.keys():
        times_in_key = True
        _add_str_to_array(sentence_dictionary, 'TIMES', new_dates)
    if 'EVENTS' in sentence_dictionary.keys():
        events_in_key = True
        _add_str_to_array(sentence_dictionary, 'EVENTS', new_dates)
    if not new_dates and not last_date:
        # There is no date in the verb prepositions, and there is no previous date
        # So, use the TIMES/EVENTS values despite it not being in the verb prepositions
        if times_in_key:
            new_dates.extend(sentence_dictionary['TIMES'])
        if events_in_key:
            new_dates.extend(sentence_dictionary['EVENTS'])
    elif not new_dates:
        return last_date, []

    # Process new_dates
    sent_date = new_dates[0]
    if len(new_dates) > 1:
        # Override the default sent_date (the 1st array value) with the most precise date
        # (e.g., one with a year) if possible
        for new_date in new_dates:
            if year_pattern.search(new_date) or month_pattern.search(new_date):
                sent_date = new_date
                break
    # Set up variable to hold time details using the format,
    # ('before'|'after'|'') (PointInTime_date|Existing_Event_URI)
    if 'before' in sent_date:
        time = 'before '
        sent_date = sent_date[7:]
    elif 'after' in sent_date:
        time = 'after '
        sent_date = sent_date[6:]
    else:
        time = empty_string
    # Get the sent_date month, day and year, if available
    year_search = year_pattern.search(sent_date)
    month_search = month_pattern.search(sent_date)
    # TODO: Add day search
    if year_search and month_search:
        time += f':PiT{month_search.group()}_{str(year_search.group())}'
    elif year_search:
        time += f':PiT{str(year_search.group())}'
    elif month_search:
        time += f':PiT{month_search.group()}'
    else:
        # Text did not mention a month or year ->
        # Check if the date is a known 'event' (from the domain-specific ontologies)?
        entity, ent_class = get_named_entity_in_string(sent_date)
        if ent_class == ':EventAndState':
            time = get_event_time_from_domain(sent_date, time)
        else:
            # Is the date relative (e.g., 'a year earlier')?
            sent_date_lower = sent_date.lower()
            # Earlier/later/previous/... are extracted as part of SpaCy's NER for dates and times
            if 'earlier' in sent_date_lower or 'later' in sent_date_lower or 'next' in sent_date_lower \
                    or 'previous' in sent_date_lower or 'prior' in sent_date_lower \
                    or 'following' in sent_date_lower:
                number, increment = get_time_details(sent_date_lower)
                if 'earlier' in sent_date_lower or 'previous' in sent_date_lower or 'prior' in sent_date_lower:
                    number *= -1
                time += update_time(last_date, number, increment)

    # Check if a new date instance should be created
    if ':' not in time:
        return last_date, []
    instance_uri = f':{time.split(":")[-1]}'
    if instance_uri in processed_dates:
        return time, []
    else:
        processed_dates.append(instance_uri)    # Track that the Turtle details have been created
        if ':ontoinsights:dna' in time:         # Note that the time is 'related' to the event
            if time.startswith('after'):
                new_label = f'Related to after {sent_date}'
            elif time.startswith('before'):
                new_label = f'Related to before {sent_date}'
            else:
                new_label = f'Related to {sent_date}'
        else:
            new_label = sent_date
        # Update the time (which is returned) to be consistent with the processed_dates
        if time.startswith('after'):
            time = f'after {instance_uri}'
        elif time.startswith('before'):
            time = f'before {instance_uri}'
        else:
            time = instance_uri
        # Need to create the Turtle for the time or event instance
        time_ttl = [f'{instance_uri} a :PointInTime ; rdfs:label "{new_label}" .']
        new_year_search = year_pattern.search(instance_uri)   # New search since the URI may be updated
        new_month_search = month_pattern.search(instance_uri)
        if new_month_search:
            time_ttl.append(f'{instance_uri} :month_of_year {str(months.index(new_month_search.group()) + 1)} .')
        if new_year_search:
            time_ttl.append(f'{instance_uri} :year {str(new_year_search.group())} .')
        return time, time_ttl


def update_time(last_date: str, number: int, increment: str) -> str:
    """
    Update a PointInTime date by the specified 'number' of months/years/days (as defined by the increment).

    :param last_date: The inferred (or explicit) time of the event, formatted as:
                      ('before'|'after'|'') (PointInTime_date|Existing_Event_URI)
    :param number: Positive or negative integer indicating whether the month, day or year is updated
    :param increment: String specifying year, month, day
    :return: String specifying the updated last_date as a URI (or the last_date is returned if the update
             cannot be performed)
    """
    if ':PiT' in last_date:
        year_search = year_pattern.search(last_date)
        month_search = month_pattern.search(last_date)
        if increment == 'year' and year_search:
            return f':PiT{str(int(year_search.group()) + number)}'
        elif increment == 'month' and month_search:
            month_index = months.index(month_search.group()) + number
            if 1 <= month_index <= 12 and year_search:
                return f':PiT{months[month_index - 1]}_{str(year_search.group())}'
            elif 1 <= month_index <= 12:
                return f':PiT{months[month_index - 1]}'
            elif month_index < 1 and year_search:
                new_year = int(year_search.group()) - 1
                new_month_index = 11 + month_index
                return f':PiT{months[new_month_index]}_{str(new_year)}'
            elif month_index > 12 and year_search:
                new_year = int(year_search.group()) + 1
                new_month_index = month_index - 13
                return f':PiT{months[new_month_index]}_{str(new_year)}'
    return last_date[last_date.index(':'):]


# Functions internal to the module
def _add_str_to_array(sent_dictionary: dict, key: str, array: list):
    """
    Add one or more of the strings from the dictionary element specified by the key, to the input 'array'.
    The string(s) are added to the array IF any of their text is found in check_str.

    For example, for the sentence "Narrator was born on June 12, 1928, in Znojmo, Czechia, which was settled
    in the thirteenth century.", the sent_dictionary will be defined as {'text': 'Narrator was born ...',
    'offset': 1, 'TIMES': ['June 12, 1928', 'the thirteenth century'], 'LOCS': ['Znojmo', 'Czechia'],
    'verbs': [{'verb_text': 'born', 'verb_lemma': 'bear', 'tense': 'Past',
    'objects': [{'object_text': 'Narrator', 'object_type': 'FEMALESINGPERSON'}],
    'preps': [{'prep_text': 'on', 'prep_details': [{'detail_text': 'June', 'detail_type': 'DATE'}]},
    {'prep_text': 'in', 'prep_details': [{'detail_text': 'Znojmo', 'detail_type': 'SINGGPE'}]}]}]}.

    If the function parameters are the sentence dictionary (from above), 'TIMES', and an array of dates,
    then the text, 'June 12 1928' will be retained in the array, 'new_dates'. But, the text, 'thirteenth
    century', will not be kept as it is not found in the 'verbs' details in the sentence dictionary.

    :param sent_dictionary: The dictionary (which are the details from the nlp parse of a
                            sentence in a narrative)
    :param key: A string specifying the dictionary key whose values are checked
    :param array: The list/array to be updated
    :return: None (the specified array is updated if the conditions specified above are met)
    """
    check_str = str(sent_dictionary[verbs_string])  # String with all the details for the verb(s)
    for elem in sent_dictionary[key]:
        array_text = empty_string
        elem_text = elem.replace(',', empty_string)
        split_elems = elem_text.split(' ')
        if key == 'TIMES':
            for split_elem in split_elems:
                if split_elem in ('earlier', 'later', 'next', 'previous', 'prior', 'following'):
                    array_text = elem_text
                    break
                elif split_elem in check_str:
                    if len(split_elem) < 4:    # Avoid determiners, short words/abbreviations/...
                        continue
                    prep_str = check_str.split(split_elem)[0]
                    if 'prep_text' in prep_str:
                        array_text = _get_before_after(prep_str, elem_text)
                        break
        elif key == 'EVENTS':
            if elem_text in check_str:
                prep_str = check_str.split(elem_text)[0]
                if 'prep_text' in prep_str:
                    array_text = _get_before_after(prep_str, elem_text)
        elif key == 'LOCS':
            for split_elem in split_elems:
                if split_elem in check_str:
                    prep_str = check_str.split(elem_text)[0]
                    if 'prep_text' in prep_str:
                        array_text = elem_text
                        break
        if array_text and array_text not in array:
            array.append(array_text)
    return


def _create_geonames_ttl(loc_uri: str, loc_text: str) -> list:
    """
    Create the Turtle for a location that is a populated place.

    :param loc_uri: String holding the URI to be assigned to the location
    :param loc_text: The location text
    :return: An array holding the Turtle for the location/location URI if the information is
             obtainable from GeoNames or an empty array
    """
    geonames_ttl = []
    class_type, country, admin_level = get_geonames_location(loc_text)
    if class_type:
        geonames_ttl.append(f'{loc_uri} a {class_type} ; rdfs:label "{loc_text.strip()}" .')
        if admin_level > 0:
            geonames_ttl.append(f'{loc_uri} :admin_level {str(admin_level)} .')
        if country and country != "None":
            geonames_ttl.append(f'{loc_uri} :country_name "{country}" .')
            if country in names_to_geo_dict.keys():
                geonames_ttl.append(f'geo:{names_to_geo_dict[country]} :has_component {loc_uri} .')
    return geonames_ttl


def _get_before_after(prep_str: str, element: str) -> str:
    """
    Add the text, 'before' or 'after', if these words are the prepositions related to the TIME or EVENT.
    These words are NOT included in SpaCy's NER date/time/event named entity extractions.

    :param prep_str: String holding the dictionary entry for the preposition
    :param element: String holding the named entity element text
    :return: A string of either the element_text (if 'before'/'after' is not found) or the element_text
             preceded by 'before' or 'after'
    """
    elem_text = element
    prep_str = prep_str.split("prep_text': '")[-1].lower()
    if prep_str.lower().startswith('after'):
        elem_text = 'after ' + element
    elif prep_str.lower().startswith('before'):
        elem_text = 'before ' + element
    return elem_text
