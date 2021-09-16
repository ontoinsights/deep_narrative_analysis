# Processing related to time and locations
# Called from create_event_turtle.py

import re

from nlp import get_time_details
from utilities import months, empty_string, verbs_string

month_pattern = re.compile('|'.join(months))
year_pattern = re.compile('[0-9]{4}')


def check_to_loc(dictionary: dict, list_locs: list, new_locs: list):
    """
    Identify locations associated with a verb using the preposition, 'to'.

    :param dictionary: A verb dictionary
    :param list_locs: An array of location entities
    :param new_locs: An array of location entities whose associating preposition is 'to'
    :return None (new_locs is updated)
    """
    for prep in dictionary:
        prep_str = str(prep)
        if prep_str[prep_str.find("prep_text': '") + 13:].startswith('to'):
            for loc in list_locs:
                if loc in prep_str:
                    new_locs.append(loc)
    return


def get_location_uri(loc: str, names_to_geo_dict: dict) -> str:
    """
    Get a location URI based on the input string.

    :param loc: Input location string
    :param names_to_geo_dict: A dictionary where the keys are country names and the values are the
                              GeoNames country codes
    :return A string holding the URI using a GeoNames prefix or the DNA prefix
    """
    if loc in names_to_geo_dict.keys():
        return f'geo:{names_to_geo_dict[loc]}'
    else:
        return f":{loc.replace(' ', '_')}"


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
    :return A new location or the empty string (if there is no new location)
    """
    # TODO: Imprecise location (home, house, town, village, ...)
    check_verb_str = str(sentence_dictionary[verbs_string])  # String with all the details for the verb(s)
    new_locs = []
    _add_str_to_array(check_verb_str, sentence_dictionary, 'LOCS', new_locs)
    if not new_locs and not last_loc:
        # There is no location in the verb prepositions, and there is no previous loc - So, use the LOCS value
        new_locs.extend(sentence_dictionary['LOCS'])
    if len(new_locs) == 1:
        return new_locs[0]
    elif len(new_locs) > 1:
        # Try to reduce locations to only ones associated directly with the main verb using the preposition, to
        revised_locs = []
        for verb in sentence_dictionary[verbs_string]:
            if 'preps' in verb.keys():
                check_to_loc(verb['preps'], new_locs, revised_locs)
            if 'verb_xcomp' in verb.keys():
                for xcomp in verb['verb_xcomp']:
                    if 'preps' in xcomp.keys():
                        check_to_loc(xcomp['preps'], new_locs, revised_locs)
        if len(revised_locs):
            return revised_locs[0]
        else:
            return new_locs[0]
    else:
        return empty_string


def get_sentence_time(sentence_dictionary: dict, last_date: str) -> str:
    """
    Determine if a date/time is specified in the sentence (as defined by the sentence_dictionary).
    An event/date/time in the sentence is identified by spaCy's entity recognition and stored in the
    sentence dictionary, with the key, TIMES. If any of the strings in the TIMES value are specified
    in the verb clause (likely as the objects of the prepositions, 'in', 'at', 'during', 'before',
    'after'), then they are retained. Subsequent processing (in this function) tries to select
    a single string as the defining time for the sentence.

    :param sentence_dictionary: The sentence dictionary
    :param last_date: The time from the previous sentence
    :return A new time or the empty string (if there is no new time)
    """
    # TODO: Imprecise time (morning, evening, day, night, ...)
    check_verb_str = str(sentence_dictionary[verbs_string])  # String with all the details for the verb(s)
    new_dates = []
    _add_str_to_array(check_verb_str, sentence_dictionary, 'TIMES', new_dates)
    if not new_dates and not last_date:
        # There is no date in the verb prepositions, and there is no previous date - So, use the TIMES value
        new_dates.extend(sentence_dictionary['TIMES'])
    if new_dates:
        date = new_dates[0]
        if len(new_dates) > 1:
            # Get most precise date (e.g., one with a year)
            for new_date in new_dates:
                if year_pattern.search(new_date):    # TODO: Expand to month, day, ...
                    date = new_date
                    break
        date_lower = date.lower()
        if 'earlier' in date_lower or 'later' in date_lower or 'next' in date_lower \
                or 'previous' in date_lower or 'prior' in date_lower or 'following' in date_lower:
            number, increment = get_time_details(date_lower)
            if increment == 'year':                  # TODO: Expand to month, day, ...
                if 'earlier' in date_lower or 'previous' in date_lower or 'prior' in date_lower:
                    number *= -1
                int_date = int(last_date)
                int_date += number
                date = str(int_date)
        return date
    else:
        return empty_string


# Functions internal to the module
def _add_str_to_array(check_str: str, sent_dictionary: dict, key: str, array: list):
    """
    Add one or more of the strings from the dictionary element specified by the key, to the input 'array'.
    The string(s) are added to the array IF any of their text is found in check_str.

    For example, for the sentence "Mary was born on June 12, 1928, in Znojmo, Czechia, which was settled
    in the thirteenth century.", the sent_dictionary will be defined as {'DATE': ['June 12 1928',
    'thirteenth century'], 'GPE': ['Znojmo', 'Czechia'], 'verbs': [{'verb_text': 'born',
    'verb_lemma': 'bear', 'tense': 'Past', 'objects': [{'object_text': 'Mary', 'object_type': 'SINGPERSON'}],
    'preps': [{'prep_text': 'on', 'prep_details': [{'prep_text': ' June', 'prep_type': 'DATE'}]},
    {'prep_text': 'in', 'prep_details': [{'prep_text': ' Znojmo', 'prep_type': 'GPE'}]}]}]}.

    check_str is the string value of sent_dictionary['verbs']. If the function parameters are
    ("Mary was born ...", sent_dictionary, 'DATE', new_dates), then the text, 'June 12 1928' will be
    retained in the array, 'new_dates'. But, the text, 'thirteenth century', will not be kept as it is
    not found in the 'verbs' details in sent_dictionary.

    :param check_str: The string value of the sent_dictionary's 'verbs' element
    :param sent_dictionary: The dictionary (which are the details from the nlp parse of a
                            sentence in a narrative)
    :param key: A string specifying the dictionary key whose values are checked
    :param array: The list/array to be updated
    :return None (the specified array is updated if the conditions specified above are met)
    """
    for elem in sent_dictionary[key]:
        split_elems = elem.split(' ')
        for split_elem in split_elems:
            if len(split_elem) < 3:    # Avoid determiners such as 'a', and short words/abbreviations
                continue
            if split_elem in check_str:
                elem_text = elem.replace(',', empty_string).replace('the ', empty_string)
                if key == 'TIMES':     # Need to track before/after
                    prep_str = check_str.split(split_elem)[0]
                    if 'prep_text' in prep_str:
                        prep_str = prep_str.split("prep_text': '")[-2].lower()
                        if prep_str.startswith('after'):
                            elem_text = 'after ' + elem_text
                        elif prep_str.startswith('before'):
                            elem_text += 'before ' + elem_text
                if elem_text not in array:
                    array.append(elem_text)
                    break
    return
