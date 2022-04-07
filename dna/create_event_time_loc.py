# Processing related to time and locations
# Called from create_event_turtle.py

import logging
import re

from database import query_database
from query_ontology_and_sources import get_geonames_location
from nlp import get_named_entity_in_string, get_time_details
from utilities import domain_database, empty_string, months, names_to_geo_dict, objects_string, \
    preps_string, space, subjects_string, verbs_string

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
                   '{ iri a ?type . OPTIONAL { iri :has_time ?time } ' \
                   'OPTIONAL { iri :has_beginning ?begin } OPTIONAL { iri :has_end ?end } }'


def check_to_loc(dictionary: dict, list_locs: list, new_locs: list):
    """
    Identify locations associated with a verb using the preposition, 'to'.

    :param dictionary: A verb dictionary
    :param list_locs: An array of location entities
    :param new_locs: An array of location entities whose associating preposition is 'to'
    :returns: None (new_locs is updated)
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
    :returns: The time as defined by an Event's :has_time, :has_beginning or :has_end predicates
    """
    # SHOULD find the event in the domain ontology modules
    results = query_database(
        'select', query_domain_event.replace('keyword', sent_date), domain_database)
    if results:
        event_iri = f":{results[0]['inst']['value'].split(':')[-1]}"
        # Get the :has_time, :has_beginning or :has_end details for the event
        time_results = query_database(
            'select', query_event_time.replace('iri', event_iri), domain_database)
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


def get_location_iri_and_ttl(loc: str, processed_locs: dict) -> (str, list):
    """
    Get a location IRI based on the input string and if appropriate, add the Turtle explaining/
    defining that location. (Before this function is called, the current ontologies - both general
    and domain - have already been checked for the location details.)

    :param loc: Input location string
    :param processed_locs: A dictionary of location texts (keys) and their IRI (values) of
                           all locations already processed
    :returns: A string holding the location IRI using a GeoNames prefix or the DNA prefix, and an
             array of strings that are the Turtle for a new location
    """
    loc_ttl = []
    loc_iri = _check_if_loc_is_known(loc, processed_locs)
    if loc_iri:
        return loc_iri, loc_ttl
    # Location is not already defined/known, so determine its IRI, and check for city/town names
    split_locs = loc.split(space)
    if len(split_locs) == 1:
        loc_iri = f':{loc}'
    else:
        if loc.lower().startswith('the '):
            loc = space.join(split_locs[1:])
        loc_iri = f':{loc.replace(space,"_")}'
    # Determine if the location includes a proper noun (begins with capital letter)
    proper_noun = empty_string
    for word in loc.split(space):
        if word[0].isupper():
            proper_noun += word + space
    if proper_noun:
        proper_noun = proper_noun.strip()
        proper_noun_iri = _check_if_loc_is_known(proper_noun, processed_locs)   # Do we know about this text?
        if not proper_noun_iri:
            proper_noun_iri = f':{proper_noun.replace(space, "_")}'
            proper_noun_ttl = _create_geonames_ttl(proper_noun_iri, proper_noun)
            if proper_noun_ttl:
                loc_ttl.extend(proper_noun_ttl)
            else:
                loc_ttl.append(f'{proper_noun_iri} a :Location .')
        if proper_noun != loc:
            # Location has more text than just the proper noun - likely that it describes a part of a city/town/...
            loc_ttl.append(f'{proper_noun_iri} :has_component {loc_iri} .')
            # TODO: Generalize a part of a city beyond ghetto (in the ontology)
            if 'ghetto' in loc.lower():
                loc_ttl.append(f'{loc_iri} a :Ghetto, :Location ; rdfs:label "{loc}" .')
            else:
                loc_ttl.append(f'{loc_iri} a :PopulatedPlace ; rdfs:label "{loc}" .')
    # Record location text in processed_locs so that the details are not added again
    processed_locs[loc] = loc_iri
    return loc_iri, loc_ttl


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
    :returns: A new location or the empty string (if there is no new location)
    """
    # TODO: Imprecise location (home, house, town, village, ...)
    new_locs = []
    _add_str_to_array(sentence_dictionary, 'LOCS', new_locs)
    if not new_locs and not last_loc:
        # There is no location in the verb prepositions, and there is no previous loc
        # So, use the LOCS value despite it not being in the verb prepositions
        new_locs.extend(sentence_dictionary['LOCS'])
    if not new_locs:  # Check if the sentence subject is a location, or the sentence object if a passive verb
        if subjects_string in sentence_dictionary.keys():
            for subj in sentence_dictionary[subjects_string]:
                subj_type = subj['subject_type']
                if subj_type.endswith('GPE') or subj_type.endswith('LOC') or subj_type.endswith('FAC'):
                    return subj['subject_text']
        if objects_string in sentence_dictionary.keys():
            # Check if the subject of a passive verb is a location (it is an object in the dictionary)
            for obj in sentence_dictionary[objects_string]:
                obj_type = obj['object_type']
                if obj_type.endswith('GPE') or obj_type.endswith('LOC') or obj_type.endswith('FAC'):
                    return obj['object_text']
        return empty_string
    elif len(new_locs) == 1:
        return new_locs[0]
    elif len(new_locs) > 1:
        # Try to reduce locations to ones associated with the main verb using the preposition, 'to'
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
                      ('before'|'after'|'') (PointInTime_date|Existing_Event_iri)
    :param processed_dates: A list of all dates whose Turtle has already been created
    :returns: A tuple consisting of the string, ('before'|'after'|'') (PointInTime_date|Existing_Event_iri),
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
    # ('before'|'after'|'') (PointInTime_date|Existing_Event_iri)
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
    instance_iri = f':{time.split(":")[-1]}'
    if instance_iri in processed_dates:
        return time, []
    else:
        processed_dates.append(instance_iri)    # Track that the Turtle details have been created
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
            time = f'after {instance_iri}'
        elif time.startswith('before'):
            time = f'before {instance_iri}'
        else:
            time = instance_iri
        # Need to create the Turtle for the time or event instance
        time_ttl = [f'{instance_iri} a :PointInTime ; rdfs:label "{new_label}" .']
        new_year_search = year_pattern.search(instance_iri)   # New search since the IRI may be updated
        new_month_search = month_pattern.search(instance_iri)
        if new_month_search:
            time_ttl.append(f'{instance_iri} :month_of_year {str(months.index(new_month_search.group()) + 1)} .')
        if new_year_search:
            time_ttl.append(f'{instance_iri} :year {str(new_year_search.group())} .')
        return time, time_ttl


def process_event_date(sent_text: str, event_iri: str, last_date: str, ttl_list: list):
    """
    Creates the Turtle for an event's date.

    :param sent_text: The text of the sentence being processed
    :param event_iri: IRI identifying the event
    :param last_date: A string holding the date text
    :param ttl_list: An array of the Turtle statements for the event (updated in this function)
    :returns: None (ttl_list is updated)
    """
    date_iri = f":{last_date.split(':')[1]}"   # Format of last_date: ('before'|'after'|'') (PointInTime date)
    if last_date.startswith('before'):
        ttl_list.append(f'{event_iri} :has_latest_end {date_iri} .')
    elif last_date.startswith('after') or 'eventually' in sent_text.lower() \
            or 'afterwards' in sent_text.lower() or 'finally' in sent_text.lower():
        ttl_list.append(f'{event_iri} :has_earliest_beginning {date_iri} .')
    else:
        ttl_list.append(f'{event_iri} :has_time {date_iri} .')
    return


def update_time(last_date: str, number: int, increment: str) -> str:
    """
    Update a PointInTime date by the specified 'number' of months/years/days (as defined by the increment).

    :param last_date: The inferred (or explicit) time of the event, formatted as:
                      ('before'|'after'|'') (PointInTime_date|Existing_Event_iri)
    :param number: Positive or negative integer indicating whether the month, day or year is updated
    :param increment: String specifying year, month, day
    :returns: String specifying the updated last_date as a IRI (or the last_date is returned if the update
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
    :returns: None (the specified array is updated if the conditions specified above are met)
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


def _check_if_loc_is_known(loc_text: str, processed_locs: dict) -> str:
    """
    Determines if the location is already known/defined in either the geo-names country list or if
    it has been already processed.

    :param loc_text: Input location string
    :param processed_locs: A dictionary of location texts (keys) and their IRI (values) of
                           all locations already processed
    :returns: The IRI of a country or already processed location, or an empty string
    """
    if loc_text in names_to_geo_dict.keys():   # Location is a country name
        return f'geo:{names_to_geo_dict[loc_text]}'
    if loc_text in processed_locs.keys():      # Location is already captured
        return processed_locs[loc_text]
    return empty_string


def _create_geonames_ttl(loc_iri: str, loc_text: str) -> list:
    """
    Create the Turtle for a location that is a populated place.

    :param loc_iri: String holding the IRI to be assigned to the location
    :param loc_text: The location text
    :returns: An array holding the Turtle for the location/location IRI if the information is
             obtainable from GeoNames or an empty array
    """
    geonames_ttl = []
    class_type, country, admin_level = get_geonames_location(loc_text)
    if class_type:
        geonames_ttl.append(f'{loc_iri} a {class_type} ; rdfs:label "{loc_text.strip()}" .')
        if admin_level > 0:
            geonames_ttl.append(f'{loc_iri} :admin_level {str(admin_level)} .')
        if country and country != "None":
            geonames_ttl.append(f'{loc_iri} :country_name "{country}" .')
            if country in names_to_geo_dict.keys():
                geonames_ttl.append(f'geo:{names_to_geo_dict[country]} :has_component {loc_iri} .')
    return geonames_ttl


def _get_before_after(prep_str: str, element: str) -> str:
    """
    Add the text, 'before' or 'after', if these words are the prepositions related to the TIME or EVENT.
    These words are NOT included in SpaCy's NER date/time/event named entity extractions.

    :param prep_str: String holding the dictionary entry for the preposition
    :param element: String holding the named entity element text
    :returns: A string of either the element_text (if 'before'/'after' is not found) or the element_text
             preceded by 'before' or 'after'
    """
    elem_text = element
    prep_str = prep_str.split("prep_text': '")[-1].lower()
    if prep_str.lower().startswith('after'):
        elem_text = 'after ' + element
    elif prep_str.lower().startswith('before'):
        elem_text = 'before ' + element
    return elem_text
