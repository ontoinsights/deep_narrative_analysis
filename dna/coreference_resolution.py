# Functions for co-reference resolution
# Called by create_event_turtle.py

import uuid

from typing import Union

from database import query_database
from utilities import dna_prefix, empty_string, names_to_geo_dict, domain_database

query_specific_noun = \
    'prefix : <urn:ontoinsights:dna:> SELECT ?iri ?type ?prob WHERE ' \
    '{ ?iri a ?type . ' \
    '{ { ?iri rdfs:label ?label . FILTER(?label = "keyword") . BIND(100 as ?prob) } UNION ' \
    '{ ?iri :noun_synonym ?nsyn . FILTER(?nsyn = "keyword") . BIND(100 as ?prob) } UNION ' \
    '{ ?iri rdfs:label ?label . FILTER(CONTAINS("keyword", ?label)) . BIND(90 as ?prob) } UNION ' \
    '{ ?class :noun_synonym ?nsyn . FILTER(CONTAINS("keyword", ?nsyn)) . BIND(90 as ?prob) } UNION ' \
    '{ ?iri rdfs:label ?label . FILTER(CONTAINS(?label, "keyword")) . BIND(85 as ?prob) } UNION ' \
    '{ ?iri :noun_synonym ?nsyn . FILTER(CONTAINS(?nsyn, "keyword")) . BIND(80 as ?prob) } } } ' \
    'ORDER BY DESC(?prob)'


def check_nouns(narr_gender: str, elem_dictionary: dict, key: str, last_nouns: list) -> list:
    """
    Get the subject or object nouns (as indicated by the key input parameter) in the sent_dictionary,
    using the last_nouns details to attempt to resolve co-references/anaphora. Subject/object
    information (the nouns and their types and IRIs) is returned.

    For example, for the sentence "Narrator was born on June 12, 1928, in Znojmo, Czechia, which was settled
    in the thirteenth century.", the sent_dictionary will be defined as {'text': 'Narrator was born ...',
    'offset': 1, 'TIMES': ['June 12, 1928', 'the thirteenth century'], 'LOCS': ['Znojmo', 'Czechia'],
    'verbs': [{'verb_text': 'born', 'verb_lemma': 'bear', 'tense': 'Past',
    'objects': [{'object_text': 'Narrator', 'object_type': 'FEMALESINGPERSON'}],
    'preps': [{'prep_text': 'on', 'prep_details': [{'detail_text': 'June', 'detail_type': 'DATE'}]},
    {'prep_text': 'in', 'prep_details': [{'detail_text': 'Znojmo', 'detail_type': 'SINGGPE'}]}]}]}.

    If the function parameters are ('Female', sent_dictionary, 'objects', last_nouns), then the text,
    'Narrator', 'FEMALESINGPERSON' and ':Narrator' will be returned.

    :param narr_gender: Either an empty string or one of the values, AGENDER, BIGENDER, FEMALE or MALE -
                        indicating the gender of the narrator
    :param elem_dictionary: The dictionary (holding the details from the nlp parse of a
                            sentence in a narrative)
    :param key: Either 'subjects' or 'objects'
    :param last_nouns: The list/array of tuples defining the noun text, type and its IRI
    :returns: Array of tuples that are the noun text, type and IRI
    """
    # TODO: Use previous sentence to give context to nouns (ex: bloody attacks => during the violence)
    nouns = set()
    for elem in elem_dictionary[key]:
        elem_key = key[0:-1]
        elem_text = elem[f'{elem_key}_text']
        elem_type = elem[f'{elem_key}_type']
        # TODO: 'he', 'she', 'they' always checks for a PERSON
        if elem_type == 'INCLUSIVE':                  # E.g., 'we', 'us'
            # Find singular or plural person nouns (any gender) in last_nouns
            nouns.update(_check_last_nouns(last_nouns, None, None, True))
            nouns.add(('Narrator', f'{narr_gender}SINGPERSON', ':Narrator'))
        # Process the various pronouns
        elif elem_text.lower() in ('they', 'them'):
            # Give preference to persons (any gender) in last_nouns
            noun_list = _check_last_nouns(last_nouns, None, None, True)
            if noun_list:
                nouns.update(noun_list)
            else:
                # Check for non-persons
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
            # Not a pronoun
            found = False
            for noun_text, noun_type, noun_iri in last_nouns:   # See if a subj/obj occurred in previous sentence
                if elem_text == noun_text:
                    found = True
                    nouns.add((noun_text, noun_type, noun_iri))
                    break
            if not found:
                if 'preps' in elem.keys():    # Get the full text for the noun
                    elem_text = _get_noun_preposition_text(elem, elem_text)
                iri = f":{elem_text.replace(' ', '_')}"
                if ('PERSON' in elem_type or elem_type.endswith('GPE') or
                        elem_type.endswith('ORG') or elem_type.endswith('NORP')):
                    match_iri, match_type = check_specific_match(elem_text, elem_type)
                    if match_iri:
                        iri = match_iri
                else:
                    # Some kind of thing or event that could be repeated
                    iri = f'{iri}_{str(uuid.uuid4())[:13]}'   # Adjust the subject IRI to be unique
                nouns.add((elem_text, elem_type, iri))
    if nouns:
        return list(nouns)
    else:
        return []


def check_specific_match(noun: str, noun_type: str) -> (str, str):
    """
    Checks if the concept/Person/Location/... is already defined in the DNA Country or domain-specific
    ontology modules. These are the only ontologies where a specific person/location/... would be defined.

    :param noun: String holding the text to be matched
    :param noun_type: String holding the noun type (PERSON/GPE/LOC/...) from spacy's NER
    :returns: A tuple consisting of the matched IRI and its type (if a match is found) or two empty strings
    """
    if noun_type.endswith('GPE') and noun in names_to_geo_dict.keys():
        return f'geo:{names_to_geo_dict[noun]}', ':Country'
    if noun_type.endswith('PERSON') or noun_type.endswith('GPE') or noun_type.endswith('LOC') \
            or noun_type.endswith('ORG') or noun_type.endswith('EVENT'):
        match_details = query_database('select', query_specific_noun.replace('keyword', noun), domain_database)
        if match_details:
            return match_details[0]['iri']['value'].replace(dna_prefix, ':'), match_details[0]['type']['value']
    return empty_string, empty_string


# Functions internal to the module
def _check_criteria(last_nouns: list, looking_for_singular: Union[bool, None],
                    looking_for_female: Union[bool, None], looking_for_person: bool, is_exact: bool) -> list:
    """
    Checks the values of the nouns in last_nouns for matches of the specified gender/number
    criteria.

    :param last_nouns: The list/array of tuples defining the text, type and IRI of the nouns
                       from the last sentence(s) that were analyzed
    :param looking_for_singular: Boolean indicating that a singular noun is needed from last_nouns
    :param looking_for_female: Boolean indicating that a female gender noun is needed from last_nouns
    :param looking_for_person: Boolean indicating that a Person is needed from last_nouns (if True)
    :param is_exact: Boolean indicating that the gender and number MUST match when the looking_for
                     parameters are not None
    :returns: A list/array of tuples of subjects/objects (text, type and IRI) from last_nouns that fit
              the criteria defined by the parameters
    """
    poss_nouns = []
    for text, ent_type, iri in last_nouns:
        # Check number
        if looking_for_singular is None or not is_exact:
            found_number = True
        else:
            if (looking_for_singular and 'SING' in ent_type) or (not looking_for_singular and 'PLURAL' in ent_type):
                found_number = True
            else:
                found_number = False
        # Check gender
        if looking_for_female is None or not is_exact:
            found_gender = True
        else:
            if (looking_for_female and 'FEMALE' in ent_type) or (not looking_for_female and 'MALE' in ent_type):
                found_gender = True
            else:
                found_gender = False
        # Check if a PERSON
        if looking_for_person and 'PERSON' in ent_type:
            found_person = True
        else:
            found_person = False
        # Check all criteria
        if found_gender and found_number and found_person:
            poss_nouns.append((text, ent_type, iri))
    return poss_nouns


def _check_last_nouns(last_nouns: list, looking_for_singular: Union[bool, None],
                      looking_for_female: Union[bool, None], looking_for_person: Union[bool, None]):
    """
    Determine if any nouns in the last_nouns array meet the criteria defined by the input parameters.
    This function first looks for exact matches of the criteria and then allows matching if no value
    for gender, number and personhood are given (e.g., 'inexact').

    :param last_nouns: The list/array of tuples defining the text, type and IRI of the nouns
                       from the last sentence(s) that were analyzed
    :param looking_for_singular: Boolean indicating that a singular noun is needed from last_nouns
    :param looking_for_female: Boolean indicating that a female gender noun is needed from last_nouns
    :param looking_for_person: Boolean indicating that a Person is needed from last_nouns
    :returns: None
    """
    possible_nouns = _check_criteria(last_nouns, looking_for_singular, looking_for_female,
                                     looking_for_person, True)        # Exact
    if not possible_nouns:
        # No exact matches found, so try again more broadly
        possible_nouns = _check_criteria(last_nouns, looking_for_singular, looking_for_female,
                                         looking_for_person, False)   # Inexact
    if possible_nouns:
        if looking_for_singular:
            # Singular result - take the most recent which is the last entry in possible_nouns
            return [possible_nouns[-1]]
        else:
            return possible_nouns
    else:
        return []


def _get_noun_preposition_text(dictionary: dict, text: str) -> str:
    """
    Get prepositional details for a noun.

    :param dictionary: Dictionary holding the details to be added
    :param text: Input noun text
    :returns: The updated noun text or the original text if no change is warranted
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
