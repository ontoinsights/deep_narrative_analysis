# Processing to create the individual token dictionaries within a sentence dictionary
# Called by nlp_sentence_dictionary.py

from spacy.tokens import Token

from dna.utilities import add_to_dictionary_values, check_name_gender, empty_string, family_members, \
    objects_string, processed_prepositions, space

family_roles = [key for key in family_members.keys() if True]

unwanted_tokens = [
    'INTJ',   # interjection
    'X',      # other
]
# Want 'PUNCT' and 'SYM' to address statements such as "66.3% of the vote"


def _handle_noun(noun_token: Token) -> (str, str):
    """
    When processing a token (in add_token_details) that is a noun, first handle the special
    cases of a proper noun, pronoun, family member role, etc. Lastly, check a general noun.

    :param noun_token: Token of the noun
    :return: Two strings, the noun text and type
    """
    noun_text = ' '.join([ww.text for ww in noun_token.subtree])
    # Handle proper nouns and pronouns
    if 'PROPN' in noun_token.pos_:      # Proper noun
        return _process_proper_noun(noun_token)
    elif 'Prs' in noun_token.morph.get('PronType'):    # Personal pronoun
        return _process_personal_pronoun(noun_token)
    # Handle references to family members ('brother', 'sister', ...)
    elif noun_text.lower() in family_roles:
        noun_text_lower = noun_text.lower()
        gender = family_members[noun_text_lower]
        if gender:
            return full_noun_text, f'{gender}SINGPERSON' if gender else f'SINGPERSON'
        else:
            gender = family_members[noun_text_lower[0:-1]]   # Check if plural family members were referenced
            return full_noun_text, f'{gender}PLURALPERSON' if gender else f'PLURALPERSON'
    elif noun_text.lower() in ('family', 'families'):
        return full_noun_text, 'PLURALPERSON'
    else:
        return _process_noun(noun_token)


def _process_noun(token: Token) -> (str, str):
    """
    When processing a token (in add_token_details) that is a noun, capture its number, gender, etc.

    :param token: Token of the noun
    :return: Two strings, the entity text and type
    """
    # Retrieve the full text with adjectives, etc.
    ent = space.join(t.text for t in token.children if (t.dep_ in ('amod', 'compound', 'det', 'nummod', 'nmod')
                     and t.pos_ not in unwanted_tokens))
    symbols = [t.text for t in token.children if t.pos_ == 'SYM']
    if ent:
        ent = f'{ent}{space}{token.text}'
    else:
        ent = token.text
    ent_type = token.ent_type_ if token.ent_type_ else 'NOUN'
    # Include plurality in ent_type
    if 'Plur' in token.morph.get('Number'):
        ent_type = f'PLURAL{ent_type}'
    elif 'Sing' in token.morph.get('Number'):
        ent_type = f'SING{ent_type}'
    gender = empty_string
    if 'Fem' in token.morph.get('Gender'):
        gender = 'FEMALE'
    elif 'Masc' in token.morph.get('Gender'):
        gender = 'MALE'
    ent_type = f'{gender}{ent_type}' if gender else ent_type
    # Account for a determiner of 'no' - i.e., nothing (for ex, 'no information was found')
    if any([tc for tc in token.children if tc.dep_ == 'det' and tc.text == 'no']):
        ent_type = f'NEG{ent_type}'
    if 'PERCENT' in ent_type or 'MONEY' in ent_type:
        ent = ent.replace(' %', '%')
        for sym in symbols:    # TODO: Assumes that there is only 1 occurrence of the symbol
            if ent[ent.index(sym) + 2].isdigit():
                ent = ent.replace(f'{sym} ', sym)
            elif ent[ent.index(sym) - 2].isdigit():
                ent = ent.replace(f' {sym}', sym)
    else:
        ent.replace('.', empty_string)
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
    prep_ent, prep_ent_type = _handle_noun(token)
    prep_ent_detail = dict()
    prep_ent_detail['detail_text'] = prep_ent
    prep_ent_detail['detail_type'] = prep_ent_type
    # Recursively call if there are more objects, related by conjunction
    for child in token.children:
        if 'conj' == child.dep_:
            _process_prep_object(child, dictionary, prep_key)
    add_to_dictionary_values(dictionary, 'prep_details', prep_ent_detail, dict)


def _process_personal_pronoun(token: Token) -> (str, str):
    """
    When processing a token that is a personal pronoun, return the text that identifies
    the person and their 'type' (gender + single/plural + PERSON).

    :param token: Token of the personal pronoun
    :return: A tuple holding the text that identifies the person and their 'type'
            (gender + single/plural + PERSON).
    """
    entity = token.text
    entity_type = token.ent_type_
    if '1' in token.morph.get('Person'):
        entity_type = 'PERSON'
    if '2' in token.morph.get('Person'):
        entity_type = 'AUDIENCE'
    elif '3' in token.morph.get('Person'):
        if token.text.lower() == 'it':
            entity_type = 'NOUN'
        else:
            entity_type = 'PERSON'
    # Include gender and plurality in ent_type
    if 'Plur' in token.morph.get('Number'):
        entity_type = f'PLURAL{entity_type}'
    elif 'Sing' in token.morph.get('Number'):
        entity_type = f'SING{entity_type}'
    if 'Fem' in token.morph.get('Gender'):
        entity_type = f'FEMALE{entity_type}'
    elif 'Masc' in token.morph.get('Gender'):
        entity_type = f'MALE{entity_type}'
    return entity, entity_type


def _process_proper_noun(token: Token) -> (str, str):
    """
    When processing a token that is a proper noun, return the text of the noun and its
    'type' (gender + single/plural + PERSON).

    :param token: Token of the proper noun
    :return: A tuple holding the text of the noun and its 'type' (gender + single/plural + PERSON/
             GPE/LOC/EVENT/...).
    """
    entity = token.text
    entity_type = token.ent_type_
    if entity_type.endswith('DATE') or entity_type.endswith('TIME'):
        return entity, entity_type
    if entity_type.endswith('GPE') or entity_type.endswith('LOC') or entity_type.endswith('ORG') \
            or entity_type.endswith('NORP') or entity_type.endswith('EVENT') or entity_type.endswith('NOUN'):
        return _process_noun(token)
    return entity, check_name_gender(entity)


def _setup_entity_dictionary(ent_text: str, ent_type: str, ent_key: str, verb_lemma: str = None) -> dict:
    """
    Set up a dictionary to hold the entity's/token's details.

    :param ent_text: Full token string - For verbs, = lemma; For nouns, compound words
                     and modifiers added
    :param ent_type: The type of the entity - For example, SINGPERSON or NOUN
    :param ent_key: Dictionary key where the details are added
    :param verb_lemma: The lemma if the entity is a verb
    :return: A dictionary holding the entity's/token's initial dictionary definition
    """
    ent_dict = dict()
    # Lists of dictionaries have plural names while individual dictionary keys should not
    ent_base_key = 'detail'
    if 'verb' in ent_key:
        ent_base_key = 'verb'
    elif 'object' in ent_key:
        ent_base_key = 'object'
    elif 'subject' in ent_key:
        ent_base_key = 'subject'
    ent_dict[f'{ent_base_key}_text'] = ent_text
    if 'verb' in ent_key:
        ent_dict['verb_lemma'] = verb_lemma
    else:
        ent_dict[f'{ent_base_key}_type'] = ent_type
    return ent_dict


def add_token_details(token: Token, dictionary: dict, token_key: str):
    """
    Expand/clarify the token text, get the token's entity type (or define one if blank), and
    add the token details to the specified dictionary key.

    :param token: Token from spacy parse
    :param dictionary: Dictionary that the token details should be added to
    :param token_key: Dictionary key where the details are added
    :return: None (Input dictionary is updated)
    """
    ent = token.text
    if ent in ('.', ','):   # Erroneous parse sometimes returns punctuation
        return
    if 'verb' in token_key:
        ent = token.lemma_
        ent_type = 'VERB'
    else:
        ent, ent_type = _handle_noun(token)
    # Set up the entity's dictionary and add basic details
    ent_dict = _setup_entity_dictionary(ent, ent_type, token_key, token.lemma_)
    # Process specific children (conjunctions and prepositions)
    for child in token.children:
        if ent_type == 'VERB' and ('obj' in child.dep_ or 'attr' in child.dep_):
            # if 'advcl' in token_key or 'xcomp' in token_key:
            # Object/attr is part of the adverbial clause, so it adds to the current ent_dict
            # add_token_details(child, ent_dict, objects_string)
            # else:
            add_token_details(child, ent_dict, objects_string)
        elif 'conj' == child.dep_:
            # TODO: A "cc" of "or" or "nor" => :alternative true Collection (currently, assumes 'cc' = 'and')
            add_token_details(child, dictionary, token_key)
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
                    # TODO: Add processing for pcomp
                    # Only add to the dictionary if the object or attr is processed
                    add_to_dictionary_values(ent_dict, 'preps', prep_dict, dict)
    add_to_dictionary_values(dictionary, token_key, ent_dict, dict)
