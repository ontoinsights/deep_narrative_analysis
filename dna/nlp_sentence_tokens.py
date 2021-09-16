# Processing to create the individual token dictionaries within a sentence dictionary
# Called by nlp_sentence_dictionary.py

import logging

from spacy.tokens import Token

from utilities import empty_string, space, objects_string, family_members, \
    add_to_dictionary_values, processed_prepositions

family_roles = []
for key in family_members.keys():
    family_roles.append(key)
family_roles_plurals = []
for fam_role in family_roles:
    family_roles_plurals.append(f'{fam_role}s')

unwanted_tokens = [
    'DET',    # determiner
    'INTJ',   # interjection
    'PUNCT',  # punctuation
    'SYM',    # symbol
    'X',      # other
]


def add_token_details(token: Token, dictionary: dict, token_key: str, narr_gender: str, family_dict: dict):
    """
    Expand/clarify the token text, get the token's entity type (or define one if blank), and
    add the token details to the specified dictionary key.

    :param token: Token from spacy parse
    :param dictionary: Dictionary that the token details should be added to
    :param token_key: Dictionary key where the details are added
    :param narr_gender: Either an empty string or one of the values, AGENDER, BIGENDER, FEMALE or
                        MALE - indicating the gender of the narrator
    :param family_dict: A dictionary containing the names of family members and their
                        relationship to the narrator/subject
    :return: None (Specified dictionary is updated)
    """
    logging.info(f'Processing the token, {token.text}, for key, {token_key}, of type, {token.ent_type_}')
    ent = token.text
    ent_type = token.ent_type_
    # Handle proper nouns and pronouns
    if 'Prop' in token.morph.get('NounType'):      # Proper noun
        if ent == 'Narrator':
            gender = narr_gender
            if gender:
                ent_type = f'{gender}SINGPERSON'
        elif ent_type.endswith('GPE') or ent_type.endswith('LOC') or ent_type.endswith('ORG') \
                or ent_type.endswith('NORP'):
            ent, ent_type = _process_noun(token, ent_type)
            ent_type = f'SING{ent_type}'
        else:
            ent, gender, ent_type = _check_family(ent, family_dict)
            if ent_type == 'NOUN':    # Proper noun that is not a Person or identified as GPE, ORG, ...
                ent, ent_type = _process_noun(token, ent_type)   # Get the full entity text at least
            if 'Plur' in token.morph.get('Number'):
                ent_type = f'{gender}PLURAL{ent_type}' if gender else f'PLURAL{ent_type}'
            elif 'Sing' in token.morph.get('Number'):
                ent_type = f'{gender}SING{ent_type}' if gender else f'SING{ent_type}'
            else:
                ent_type = f'{gender}{ent_type}' if gender else ent_type
    elif 'Prs' in token.morph.get('PronType'):    # Personal pronoun
        if '1' in token.morph.get('Person'):
            if 'Plur' in token.morph.get('Number'):
                ent_type = 'INCLUSIVE'
            else:
                ent = 'Narrator'
                ent_type = f'{narr_gender}SINGPERSON'
        elif '2' in token.morph.get('Person'):
            ent_type = 'AUDIENCE'
        elif '3' in token.morph.get('Person'):
            gender = empty_string
            ent_type = 'NOUN'
            if 'Fem' in token.morph.get('Gender'):
                gender = 'FEMALE'
            elif 'Masc' in token.morph.get('Gender'):
                gender = 'MALE'
            if 'Plur' in token.morph.get('Number'):
                ent_type = f'{gender}PLURAL{ent_type}' if gender else f'PLURAL{ent_type}'
            elif 'Sing' in token.morph.get('Number'):
                ent_type = f'{gender}SING{ent_type}' if gender else f'SING{ent_type}'
            else:
                ent_type = f'{gender}{ent_type}' if gender else ent_type
    # Handle references to family members ('brother', 'sister', ...)
    elif ent.lower() in family_roles:
        gender = family_members[ent.lower()]
        ent_type = f'{gender}SINGPERSON' if gender else f'SINGPERSON'
    elif ent.lower() in family_roles_plurals:
        gender = family_members[ent[0:-1].lower()]
        ent_type = f'{gender}PLURALPERSON' if gender else f'PLURALPERSON'
    elif 'verb' in token_key:
        ent = token.text
        ent_type = 'VERB'
    else:
        ent, ent_type = _process_noun(token, ent_type)

    # Set up the entity's dictionary and add basic details
    ent_dict = dict()
    # Lists of dictionaries have plural names while individual dictionary keys should not
    ent_base_key = 'prep'
    if 'verb' in token_key:
        ent_base_key = 'verb'
    elif 'object' in token_key:
        ent_base_key = 'object'
    elif 'subject' in token_key:
        ent_base_key = 'subject'
    ent_dict[f'{ent_base_key}_text'] = ent
    if 'verb' in token_key:
        ent_dict[f'verb_lemma'] = token.lemma_
    else:
        ent_dict[f'{ent_base_key}_type'] = ent_type

    # Process specific children (conjunctions and prepositions)
    for child in token.children:
        if ent_type == 'VERB' and ('obj' in child.dep_ or 'attr' in child.dep_):
            if 'advcl' in token_key:
                # Object/attr is part of the adverbial clause, so it adds to the current ent_dict
                add_token_details(child, ent_dict, objects_string, narr_gender, family_dict)
            else:
                add_token_details(child, dictionary, objects_string, narr_gender, family_dict)
        # TODO: Note a "cc" of "or" or "nor" (alternatives vs conjunctions)
        elif 'conj' == child.dep_:
            add_token_details(child, dictionary, token_key, narr_gender, family_dict)
        elif 'prep' in child.dep_:
            if child.text.lower() not in processed_prepositions:
                continue
            prep_dict = dict()
            # Lists of dictionaries have plural names while individual dictionary keys should not
            prep_dict['prep_text'] = child.text
            for prep_child in child.children:
                if 'obj' in prep_child.dep_ or 'attr' in prep_child.dep_:
                    # Object/attr is part of the prepositional clause, so it adds to the current prep_dict
                    _process_prep_object(prep_child, prep_dict,
                                         (token_key[0:-1] if token_key.endswith("s") else token_key))
            add_to_dictionary_values(ent_dict, 'preps', prep_dict, dict)
    add_to_dictionary_values(dictionary, token_key, ent_dict, dict)
    return


# Functions internal to the module
def _check_family(entity: str, family_dict: dict) -> (str, str, str):
    """
    Determines if a reference is to a family member and returns the member's relationship,
    gender and type (= PERSON if a family member or NOUN otherwise).

    :param entity: The string representing the noun or possessive
    :param family_dict: A dictionary containing the names of family members and their
                        relationship to the narrator/subject
    :return 3 strings representing the entity's relationship (if a family member), gender
            and type (= PERSON if a family member or NOUN otherwise)
    """
    gender = empty_string
    ent_type = 'NOUN'
    if entity in family_dict.keys():
        entity = family_dict[entity]
    if entity in family_roles:
        gender = family_members[entity]
        ent_type = 'PERSON'
    return entity, gender, ent_type


def _process_noun(token: Token, ent_type: str) -> (str, str):
    """
    When processing a token (in add_token_details) that is a noun, capture its number, gender, etc.

    :param token: Token of the noun
    :param ent_type: Input ent_type (which may be empty)
    :return: Two strings, the entity text and type
    """
    # Retrieve the full text with adjectives, etc.
    token_text = token.text.lower()
    ent = space.join(t.text for t in token.children if
                     (t.dep_ in ('amod', 'nummod', 'compound') and t.pos_ not in unwanted_tokens))
    if ent:
        ent = f'{ent}{space}{token.text}'
    else:
        ent = token.text
    # Get gender
    gender = empty_string
    if token_text in family_roles:
        gender = family_members[token_text]
        ent_type = 'PERSON'
    else:
        if 'Fem' in token.morph.get('Gender'):
            gender = 'FEMALE'
        elif 'Masc' in token.morph.get('Gender'):
            gender = 'MALE'
    if ent_type == empty_string:
        ent_type = 'NOUN'
    # Get number/plurality
    if 'Plur' in token.morph.get('Number'):
        ent_type = f'{gender}PLURAL{ent_type}' if gender else f'PLURAL{ent_type}'
    elif 'Sing' in token.morph.get('Number'):
        ent_type = f'{gender}SING{ent_type}' if gender else f'SING{ent_type}'
    else:
        ent_type = f'{gender}{ent_type}' if gender else ent_type
    # Account for a determiner of 'no' - i.e., nothing (for ex, 'no information  was found')
    if any([tc for tc in token.children if tc.dep_ == 'det' and tc.text == 'no']):
        ent_type = f'NEG{ent_type}'
    return ent, ent_type


def _process_prep_object(token: Token, dictionary: dict, prep_key: str):
    """
    When processing a token (in add_token_details or recursively here), capture prepositions
    and their objects.

    :param token: Token of the preposition
    :param dictionary: Dictionary that the token details should be added to
    :param prep_key: Dictionary key where the details are added
    :return: None (Specified dictionary is updated)
    """
    # Retrieve the text for nouns (including adjectives and compound nouns)
    prep_ent = space.join(t.text for t in token.children if
                          (t.dep_ in ('amod', 'compound') and t.pos_ not in unwanted_tokens))
    if prep_ent:
        prep_ent = f'{prep_ent}{space}{token.text}'
    else:
        prep_ent = token.text
    prep_ent_type = token.ent_type_
    if prep_ent_type == empty_string:
        prep_ent_type = 'NOUN'
    # Account for a determiner of 'no' - i.e., nothing (for ex, 'no information  was found')
    if any([tc for tc in token.children if tc.dep_ == 'det' and tc.text == 'no']):
        prep_ent_type = f'NEG{prep_ent_type}'
    if 'Plur' in token.morph.get('Number'):
        prep_ent_type = f'PLURAL{prep_ent_type}'
    prep_ent_detail = dict()
    prep_ent_detail['object_text'] = prep_ent
    prep_ent_detail['object_type'] = prep_ent_type
    # Recursively call if there are more objects, related by conjunction
    for child in token.children:
        if 'conj' == child.dep_:
            _process_prep_object(child, dictionary, prep_key)
    add_to_dictionary_values(dictionary, objects_string, prep_ent_detail, dict)
    return
