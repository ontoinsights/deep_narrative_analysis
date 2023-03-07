# Processing related to time and locations
# Called from create_narrative_turtle.py

import re

from dna.create_noun_turtle import create_named_event_ttl, create_time_ttl
from dna.get_ontology_mapping import get_event_mapping_detail
from dna.query_sources import get_event_details_from_wikidata
from dna.nlp import get_time_details
from dna.utilities_and_language_specific import add_unique_to_array, days, empty_string, \
    incremental_time_keywords, months, space, underscore

# Future: Is this regex adequate for non-US dates?
month_pattern = re.compile('|'.join(months))
year_pattern = re.compile('[0-9]{4}')
day_pattern1 = re.compile('[0-9] | [0-9],|[0-2][0-9] |[0-2][0-9],|[3][0-1] |[3][0-1],')
day_pattern2 = re.compile('|'.join(days))


def _create_time_iri(before_after_str: str, str_text: str) -> str:
    """
    Creates an IRI for a time that is defined by a year, month and/or day.

    :param before_after_str: A string = 'before', 'after' or the empty string
    :param str_text: Text which holds a time
    :return: A string specified as ":PiT_", followed by an optional "_Yrxxxx", an optional
              "_Moxxxx" and an optional "_Dayxx", or an empty sting
    """
    year_search = year_pattern.search(str_text)
    month_search = month_pattern.search(str_text)
    day_search1 = day_pattern1.search(str_text)
    day_search2 = day_pattern2.search(str_text)
    if not year_search and not month_search and not day_search1 and not day_search2:
        return f':PiT_{str_text.lower().replace(space, underscore).replace(".", empty_string)}'
    if year_search or month_search or day_search1:
        return ':PiT' + (f'_{before_after_str}' if before_after_str else empty_string) \
               + (f'_Yr{year_search.group()}' if year_search else empty_string) \
               + (f'_Mo{month_search.group()}' if month_search else empty_string) \
               + (f'_Day{day_search1.group().replace(",", empty_string).strip()}' if day_search1 else empty_string)
    return ':PiT' + (f'_{before_after_str}' if before_after_str else empty_string) \
           + (f'_Day{day_search2.group()}' if day_search2 else empty_string)


def _get_before_after(sent_str: str, time_text: str) -> str:
    """
    Add the text, 'before' or 'after', if these words are the prepositions related to the TIME or EVENT.
    These words are NOT included in SpaCy's NER date/time/event named entity extractions.

    :param sent_str: The sentence string
    :param time_text: String holding the time or event
    :return: A string = 'Before', 'After' or the empty string
    """
    ba_str = empty_string
    if f'before {time_text}' in sent_str or f'Before {time_text}' in sent_str:
        ba_str = 'Before'
    if f'after {time_text}' in sent_str or f'After {time_text}' in sent_str:
        ba_str = 'After'
    return ba_str


def _get_relative_time(time_text: str, last_time: str, alet_dict: dict) -> (str, list):
    """
    Handle times identified by spaCy's NER, that have the form <number> <increment> <earlier|later|...>,
    such as "one year earlier". Return the time IRI and any new Turtle defining it.

    :param time_text: String specifying the time
    :param last_time: A string indicating the last known date from which the increment is
                      calculated
    :param alet_dict: A dictionary holding the agents, locations, events & times encountered in
             the full narrative - For co-reference resolution (it may be updated by this function);
             Keys = 'agents', 'locs', 'events', 'times', Values (for 'times') = array of strings
             storing the time's IRI
    :return: A tuple with the IRI identifying the new time and an array of Turtle statements
             defining any new times identified (also the alet_dict will be updated)
    """
    # Is the date relative (e.g., 'a year earlier')?
    new_time_lower = time_text.lower()
    new_time_lower = 'one day earlier' if new_time_lower == 'yesterday' else new_time_lower
    new_time_lower = 'one day later' if new_time_lower == 'tomorrow' else new_time_lower
    # Earlier/later/previous/... are extracted as part of SpaCy's NER for dates and times
    found_keyword = False
    for inc_keyword in incremental_time_keywords:
        if inc_keyword in new_time_lower:
            found_keyword = True
            break
    if not found_keyword:
        return empty_string, []
    time_ttl = []
    new_time_iri = f':PiT_{time_text.replace(space, underscore)}'.replace('.', empty_string)
    number, increment = get_time_details(new_time_lower)
    if 'ago' in new_time_lower or 'earlier' in new_time_lower or 'previous' in new_time_lower \
            or 'prior' in new_time_lower:
        number *= -1
    if last_time and ('_Yr' in last_time or '_Mo' in last_time):
        new_time_iri = _update_time(last_time, number, increment)
        if new_time_iri in alet_dict['times']:
            return new_time_iri, []
        time_ttl = create_time_ttl(time_text, new_time_iri)
        known_times = alet_dict['times']
        known_times.append(new_time_iri)
        alet_dict['times'] = known_times
    if not time_ttl:
        time_ttl = [f'{new_time_iri} a :PointInTime ; rdfs:label "{time_text}" .']
    return new_time_iri, time_ttl


def _process_date_time(before_after: str, time_text: str, event_iri: str, new_time_iri: str, time_iri: str,
                       alet_dict: dict) -> (str, list):
    """
    Determine the time relationship of a chunk/verb to a point in time/date.

    :param before_after: A string = 'Before', 'After' or the empty string
    :param time_text: A string holding the time's text
    :param event_iri: The verb's/event's IRI
    :param new_time_iri: A date identified as a named entity by spaCy
    :param time_iri: The last known event date in the narrative
    :param alet_dict: A dictionary holding the agents, locations, events & times encountered in
             the full narrative - For co-reference resolution (it may be updated by this function);
             Keys = 'agents', 'locs', 'events', 'times', Values (for 'times') = array of strings
             storing the time's IRI
    :return: A tuple with a string holding the time IRI and a statement specifying the Turtle for the event's time
    """
    time_ttl = []
    if not before_after:
        new_time, time_ttl = _get_relative_time(time_text, time_iri, alet_dict)
        if new_time:
            time_ttl.append(f'{event_iri} :has_time {new_time} .')
            return new_time, time_ttl
        elif new_time_iri:
            time_ttl.append(f'{event_iri} :has_time {new_time_iri} .')
            return new_time_iri, time_ttl
        else:
            time_ttl.append(f'{event_iri} :has_time {time_iri} .')
    elif before_after == 'Before':
        time_ttl.append(f'{event_iri} :has_latest_end {time_iri} .')
    elif before_after == 'After':
        time_ttl.append(f'{event_iri} :has_earliest_beginning {time_iri} .')
    return time_iri, time_ttl


def _process_event_time(before_after: str, event_text: str, event_iri: str, alet_dict: dict) -> (str, list):
    """
    Determine the time relationship of a chunk/verb to a referenced, named event.

    :param before_after: A string = 'Before', 'After' or the empty string
    :param event_text: A string holding the event's text
    :param event_iri: The verb's/event's IRI
    :param alet_dict: A dictionary holding the agents, locations, events & times encountered in
             the full narrative; Keys = 'agents', 'locs', 'events', 'times', Values (for 'events')
             = array of arrays with index 0 holding an array of strings naming the event, index 1
             storing an array of DNA class mappings, index 2 holding the event's IRI, and indexes
             3 and 4 tracking the start/end time IRIs
    :return: A tuple with a string holding the time IRI and a statement specifying the Turtle
             for the event's time, or an empty string and array
    """
    known_events = alet_dict['events'] if 'events' in alet_dict else []
    start_iri = empty_string
    end_iri = empty_string
    known_iri = empty_string
    for known_event in known_events:
        if event_text in known_event[0]:     # Found event, get details
            known_iri = known_event[2]       # Format: ':Event_{name}'
            start_iri = known_event[3]
            end_iri = known_event[4]
            break
    if before_after == 'Before' and start_iri:
        return start_iri, [f'{event_iri} :has_latest_end {start_iri} .']
    elif before_after == 'After' and end_iri:
        return end_iri, [f'{event_iri} :has_earliest_beginning {end_iri} .']
    elif before_after == 'Before':
        return f':Event_Before_{known_iri.split(underscore)[1]}', \
               [f'{event_iri} :has_latest_end :Event_Before_{known_iri.split(underscore)[1]} .']
    elif before_after == 'After':
        return f':Event_After_{known_iri.split(underscore)[1]}', \
               [f'{event_iri} :has_earliest_beginning :Event_After_{known_iri.split(underscore)[1]} .']
    elif known_iri:
        # TODO: has_time or no time?
        return known_iri, [f'{event_iri} :has_time {known_iri} .']
    return empty_string, []


def _update_time(last_date: str, number: int, increment: str) -> str:
    """
    Update a PointInTime date by the specified 'number' of months/years/weeks/days (as defined by the
    increment).

    :param last_date: The inferred (or explicit) time of the event, formatted as:
                      ('before'|'after'|'') PointInTime_date
    :param number: Positive or negative integer indicating whether the month, day or year is updated
    :param increment: String specifying year, month, day, decade, century
    :return: String specifying the updated last_date as a IRI (or the last_date is returned if the update
             cannot be performed)
    """
    if ':PiT_' in last_date:
        year = last_date.split('_Yr')[1].split(underscore)[0] if '_Yr' in last_date else empty_string
        month = last_date.split('_Mo')[1].split(underscore)[0] if '_Mo' in last_date else empty_string
        day = last_date.split('_Day')[1] if '_Day' in last_date else empty_string
        if increment in ('year', 'decade', 'century'):
            if year:
                if increment == 'year':
                    return ':PiT' + f'_Yr{str(int(year) + number)}'
                elif increment == 'decade':
                    return ':PiT' + f'_Yr{str(int(year) + (number * 10))}'
                elif increment == 'century':
                    return ':PiT' + f'_Yr{str(int(year) + (number * 100))}'
            else:
                return f':PiT_{str(abs(number))}Yrs' + ('Earlier' if number < 0 else 'Later')
        if increment == 'month':
            if month:
                month_index = months.index(month) + number
                if 1 <= month_index <= 12:
                    return ':PiT' + (f'_Yr{year}' if year else empty_string) + f'_Mo{months[month_index - 1]}'
                elif month_index < 1:
                    new_year = str(int(year) - 1) if year else '1YrEarlier'
                    return ':PiT' + f'_Yr{new_year}' + f'_Mo{months[11 + month_index]}'
                else:   # number > 12
                    new_year = str(int(year) + 1) if year else '1YrLater'
                    return ':PiT' + f'_Yr{new_year}' + f'_Mo{months[month_index - 13]}'
            else:
                return ':PiT' + (f'_Yr{year}' if year else empty_string) + \
                       f'_{str(abs(number))}Mos' + ('Earlier' if number < 0 else 'Later')
        if increment == 'week':
            return last_date + f'_{str(abs(number))}Weeks' + ('Earlier' if number < 0 else 'Later')
        if increment == 'day':
            if day:
                return last_date + f'_{str(abs(number))}Days' + ('Earlier' if number < 0 else 'Later')
    return last_date


def check_if_event_is_known(event_text: str, alet_dict: dict) -> (list, str):
    """
    Determines if the event is already processed and stored in the alet_dict.

    The acronym, alet, stands for agent-location-event-time.

    :param event_text: Input event string
    :param alet_dict: A dictionary holding the agents, locations, events & times encountered in
             the full narrative - For co-reference resolution (it may be updated by this function);
             Keys = 'agents', 'locs', 'events', 'times' and Values (for 'events') = array of arrays
             with index 0 holding an array of strings naming the event, index 1 storing an array of
             DNA class mappings, index 2 holding the event's IRI, and indexes 3 and 4 tracking
             the start/end time IRIs
    :return: A tuple holding the class mappings and IRI of the agent, or an empty list and string
    """
    if 'events' not in alet_dict:
        return [], empty_string
    known_events = alet_dict['events']
    for known_event in known_events:
        if event_text in known_event[0]:               # Strings match
            return known_event[1], known_event[2]      # NER maps to a known/processed event, with an IRI
    return [], empty_string


def get_sentence_times(sentence_dictionary: dict, published: str, alet_dict: dict, last_nouns: list,
                       use_sources: bool) -> (list, list):
    """
    Handle times identified by spaCy's NER, stored in the sentence dictionary with the
    key, 'TIMES'. If there is only 1 time specified, it is returned as "the" time for the
    events of this sentence.

    :param sentence_dictionary: The sentence dictionary
    :param published: A string indicating the date that the article was published, if provided
                      (otherwise, the empty string)
    :param alet_dict: A dictionary holding the agents, locations, events & times encountered in
             the full narrative - For co-reference resolution (it may be updated by this function);
             Keys = 'agents', 'locs', 'events', 'times', Values (for 'times') = array of strings
             storing the time's IRI, and Values (for 'events') = array of arrays with index 0
             holding an array of strings naming the event, index 1 storing an array of DNA class
             mappings, index 2 holding the event's IRI, and indexes 3 and 4 tracking the
             start/end time IRIs
    :param last_nouns: An array of tuples = noun texts, type, class mapping and IRI
                       from the current paragraph
    :param use_sources: Boolean indicating whether additional information on an event should
                        be retrieved from Wikidata (recommended)
    :return: A tuple consisting of two arrays: (1) the IRIs of the events identified in the sentence
             (if any), and 2) Turtle statements defining them and times (also the alet_dict may be updated)
    """
    # TODO: With no specific reference, use the published date as the default; Can also address weekday names
    #       (intDay = datetime.date(year=2000, month=12, day=1).weekday()
    #       where days [], print(days[intDay])  (if news on Wednesday, Tuesday mention is previous day))
    # TODO: Handle imprecise time (morning, evening, day, night, summer, winter, ...)
    time_turtle = []
    new_times = []
    new_events = []
    known_times = alet_dict['times'] if 'times' in alet_dict else []
    if 'TIMES' in sentence_dictionary:
        add_unique_to_array(sentence_dictionary['TIMES'], new_times)
    if 'EVENTS' in sentence_dictionary:
        add_unique_to_array(sentence_dictionary['EVENTS'], new_events)
    # Handle the times
    for new_time in new_times:
        new_times_lower = new_time.lower()
        # Earlier/later/previous/... are extracted as part of SpaCy's NER for dates and times
        if 'earlier' in new_times_lower or 'later' in new_times_lower or 'next' in new_times_lower \
                or 'previous' in new_times_lower or 'prior' in new_times_lower \
                or 'following' in new_times_lower:
            continue      # Will be processed as part of handling the chunk
        time_iri = _create_time_iri(empty_string, new_time)
        if time_iri not in known_times:
            time_turtle.extend(create_time_ttl(new_time, time_iri))
            known_times.append(time_iri)    # Add the new times
    alet_dict['times'] = known_times
    # Handle the events
    event_iris = []
    known_events = alet_dict['events'] if 'events' in alet_dict else []
    for new_event in new_events:
        event_classes, event_iri = check_if_event_is_known(new_event, alet_dict)
        if not event_iri:
            event_iri = f':Event_{new_event.replace(space, underscore)}'.replace('.', empty_string)
            # Try to classify the event, for example 'World War II' is a :War
            event_classes = get_event_mapping_detail(new_event, dict(), [], False)
            if not event_classes:
                event_classes = [':EventAndState']
            start_time_iri = empty_string
            end_time_iri = empty_string
            alt_names = [new_event]
            wiki_details = empty_string
            wiki_url = empty_string
            if use_sources:
                wiki_details, wiki_url, start_time, end_time, alt_names = get_event_details_from_wikidata(new_event)
                if start_time:
                    start_time_iri = _create_time_iri(empty_string, start_time)
                if end_time:
                    end_time_iri = _create_time_iri(empty_string, end_time)
            if new_event not in alt_names:
                alt_names.append(new_event)
            time_turtle.extend(
                create_named_event_ttl(event_iri, alt_names, event_classes, wiki_details, wiki_url,
                                       start_time_iri, end_time_iri))
            known_events.append([alt_names, event_classes, event_iri, start_time_iri, end_time_iri])
        last_nouns.append((new_event, 'EVENT', event_classes, event_iri))
        event_iris.append(event_iri)
    alet_dict['events'] = known_events
    return event_iris, time_turtle


def process_chunk_time(chunk_text: str, named_entities: list, event_iri: str, time_iri: str,
                       alet_dict: dict, is_bio: bool, ttl_list: list) -> str:
    """
    Creates the Turtle to associate a date with an event (chunk verb).

    :param chunk_text: The text of the chunk being processed
    :param named_entities: An array of tuples of a named entity's text and type
    :param event_iri: IRI identifying the event
    :param time_iri: IRI identifying the last event time from the narrative
    :param alet_dict: A dictionary holding the agents, locations, events & times encountered in
             the narrative to-date - For co-reference resolution (it may be updated by this function);
             Keys = 'agents', 'locs', 'events', 'times', Values (for 'times') = array of strings
             storing the time's IRI, and Values (for 'events') = array of arrays with index 0
             holding an array of strings naming the event, index 1 storing an array of DNA class
             mappings, index 2 holding the event's IRI, and indexes 3 and 4 tracking the
             start/end time IRIs
    :param is_bio: A boolean indicating that the text is biographical/autobiographical
    :param ttl_list: An array of the Turtle statements for the event (updated in this function)
    :return: A new time IRI (and ttl_list is updated) or an empty string
    """
    poss_times = []
    for ent_details in named_entities:
        ent, ent_type = ent_details
        if ent_type in ('DATE', 'EVENT'):
            poss_times.append((ent, ent_type))
    if not poss_times:
        if is_bio:        # Possible to indicate a time; Use last known time
            ttl_list.append(f'{event_iri} :has_approximate_time {time_iri} .')
        return empty_string
    poss_time = poss_times[0]    # Defaulting to the first in case 'before'/'after' is not specified
    before_after = empty_string
    for time, time_type in poss_times:
        before_after = _get_before_after(chunk_text, time)
        if before_after:
            poss_time = (time, time_type)
            break
    time_text, time_type = poss_time
    new_time = _create_time_iri(before_after, time_text)
    if time_type == 'EVENT':
        new_time, time_ttl = _process_event_time(before_after, time_text, event_iri, alet_dict)
        ttl_list.extend(time_ttl)
    elif time_type == 'DATE':
        new_time, time_ttl = _process_date_time(before_after, time_text, event_iri, new_time, time_iri, alet_dict)
        ttl_list.extend(time_ttl)
    return new_time
