# Functions for co-reference resolution
# Called by create_event_turtle.py

from typing import Union

from utilities import subjects_string

dependency_refs = ('acomp', 'dobj', 'pobj', 'xcomp')


def check_nouns(narr_gender: str, sent_dictionary: dict, key: str, last_nouns: list) -> list:
    """
    Get the subject or object nouns (as indicated by the key input parameter) in the sent_dictionary,
    using the last_nouns details to attempt to resolve co-references/anaphora. Subject/object
    information (the nouns and their types) is returned.

    For example, for the sentence "Narrator was born on June 12, 1928, in Znojmo, Czechia, which was settled
    in the thirteenth century.", the sent_dictionary will be defined as {'text': 'Narrator was born ...',
    'offset': 1, 'TIMES': ['June 12, 1928', 'the thirteenth century'], 'LOCS': ['Znojmo', 'Czechia'],
    'verbs': [{'verb_text': 'born', 'verb_lemma': 'bear', 'tense': 'Past',
    'objects': [{'object_text': 'Narrator', 'object_type': 'FEMALESINGPERSON'}],
    'preps': [{'prep_text': 'on', 'prep_details': [{'detail_text': 'June', 'detail_type': 'DATE'}]},
    {'prep_text': 'in', 'prep_details': [{'detail_text': 'Znojmo', 'detail_type': 'SINGGPE'}]}]}]}.

    If the function parameters are ('Female', sent_dictionary, 'objects', last_nouns), then the text,
    'Mary' and 'FEMALESINGPERSON' will be returned.

    :param narr_gender: Either an empty string or one of the values, AGENDER, BIGENDER, FEMALE or MALE -
                        indicating the gender of the narrator
    :param sent_dictionary: The dictionary (holding the details from the nlp parse of a
                            sentence in a narrative)
    :param key: Either 'subjects' or 'objects'
    :param last_nouns: The list/array of tuples defining the noun text and its type
    :return Array of tuples that are the noun text and type for subjects or objects
    """
    # TODO: Use previous sentence to give context to nouns (ex: bloody attacks => during the violence)
    nouns = set()
    for elem in sent_dictionary[key]:
        elem_key = key[0:-1]
        elem_text = elem[f'{elem_key}_text']
        elem_type = elem[f'{elem_key}_type']
        if elem_type == 'INCLUSIVE':                  # E.g., 'we', 'us'
            # Find singular or plural person nouns (any gender) in last_nouns
            nouns.update(_check_last_nouns(last_nouns, None, None, True))
            nouns.update(('Narrator', f'{narr_gender}SINGPERSON'))
        elif elem_text.lower() in ('they', 'them'):
            # Find all nouns (any gender) in last_nouns
            if elem_key == subjects_string:
                # TODO: subject = 'they' is NOT always a PERSON
                nouns.update(_check_last_nouns(last_nouns, None, None, True))
            else:
                nouns.update(_check_last_nouns(last_nouns, None, None, False))
        elif elem_text.lower() in ('she', 'her'):
            # Find singular, feminine, person nouns in last_nouns
            nouns.update(_check_last_nouns(last_nouns, True, True, True))
        elif elem_text.lower() in ('he', 'him'):
            # Find singular, masculine, person nouns in last_nouns
            nouns.update(_check_last_nouns(last_nouns, True, False, True))
        elif elem_text.lower() == 'it':
            # Find singular, non-person nouns (no gender) in last_nouns
            nouns.update(_check_last_nouns(last_nouns, True, None, False))
        else:
            found = False
            for text, ent_type in last_nouns:
                if elem_text in text:
                    found = True
                    nouns.add((text, ent_type))
                    break
            if not found:
                if 'preps' in elem.keys():
                    elem_text = _get_noun_preposition_text(elem, elem_text)
                nouns.add((elem_text, elem_type))
    return list(nouns)


# Functions internal to the module
def _check_criteria(last_nouns: list, looking_for_singular: Union[bool, None],
                    looking_for_female: Union[bool, None], looking_for_person: bool, is_exact: bool) -> list:
    """
    Checks the values of the nouns in last_nouns for matches of the specified gender/number
    criteria.

    :param last_nouns: The list/array of tuples defining the text and type of the nouns
                       from the last sentence(s) that were analyzed
    :param looking_for_singular: Boolean indicating that a singular noun is needed from last_nouns
    :param looking_for_female: Boolean indicating that a female gender noun is needed from last_nouns
    :param looking_for_person: Boolean indicating that a Person is needed from last_nouns
    :param is_exact: Boolean indicating that the gender and number MUST match when the looking_for
                     parameters are not None
    :return A list/array of tuples of subjects/objects (text and type) from last_nouns that fit the
            criteria defined by the parameters
    """
    poss_nouns = []
    for text, ent_type in last_nouns:
        is_female = None
        if 'FEMALE' in ent_type:
            is_female = True
        elif 'MALE' in ent_type:
            is_female = False
        is_singular = None
        if 'PLURAL' in ent_type:
            is_singular = False
        elif 'SING' in ent_type:
            is_singular = True
        found_gender = False   # Default
        if looking_for_female is not None:
            if is_female is not None:
                if looking_for_female == is_female:
                    found_gender = True
            else:
                if not is_exact:   # Not exact means that no detail could be a match
                    found_gender = True
        else:
            found_gender = True    # Not looking for gender
        found_number = False    # Default
        if looking_for_singular is not None:
            if is_singular is not None:
                if looking_for_singular == is_singular:
                    found_number = True
            else:
                if not is_exact:   # Not exact means that no detail could be a match
                    found_number = True
        else:
            found_number = True    # Not looking for number
        found_person = False   # Default
        if looking_for_person is not None:
            if 'PERSON' in ent_type:
                found_person = True
            else:
                if not is_exact:   # Not exact means that no detail could be a match
                    found_person = True
        else:
            found_person = True    # Not looking for gender
        if found_gender and found_number and found_person:
            poss_nouns.append((text, ent_type))
    return poss_nouns


def _check_last_nouns(last_nouns: list, looking_for_singular: Union[bool, None],
                      looking_for_female: Union[bool, None], looking_for_person: Union[bool, None]):
    """
    Determine if any nouns in the last_nouns array meet the criteria defined by the input parameters.
    This function first looks for exact matches of the criteria and then allows matching if no value
    for gender, number and personhood are given ('inexact').

    :param last_nouns: The list/array of tuples defining the text and type of the nouns
                       from the last sentence(s) that were analyzed
    :param looking_for_singular: Boolean indicating that a singular noun is needed from last_nouns
    :param looking_for_female: Boolean indicating that a female gender noun is needed from last_nouns
    :param looking_for_person: Boolean indicating that a Person is needed from last_nouns
    :return None (last_nouns is updated)
    """
    possible_nouns = _check_criteria(last_nouns, looking_for_singular, looking_for_female,
                                     looking_for_person, True)        # Exact
    if not possible_nouns:
        # No exact matches found, so try again more broadly
        possible_nouns = _check_criteria(last_nouns, looking_for_singular, looking_for_female,
                                         looking_for_person, False)   # Inexact
    return possible_nouns


def _get_noun_preposition_text(dictionary: dict, text: str) -> str:
    """
    Get prepositional details for a noun.

    :param dictionary: Dictionary holding the details to be added
    :param text: Input noun text
    :return The updated noun text or the original text if no change is warranted
    """
    new_text = text
    preps = dictionary['preps']
    for prep in preps:
        prep_str = str(prep)
        if "_text': '" not in prep_str:
            continue
        prep_texts = prep_str.split("_text': '")
        for i in range(1, len(prep_texts)):
            if "'," in prep_texts[i]:
                end_index = prep_texts[i].index("',")
                new_text += ' ' + prep_texts[i][0:end_index]
    return new_text
