# Processing to create the individual token dictionaries within a sentence dictionary
# Called by nlp_sentence_dictionary.py

from spacy.tokens import Token

from dna.utilities_and_language_specific import add_to_dictionary_values, check_name_gender, empty_string, \
    family_members, family_text, objects_string, processed_prepositions, space

family_roles = [key for key in family_members.keys()]

unwanted_tokens = ('INTJ',   # interjection
                   'X')      # other
# Want 'PUNCT' for semantic evaluation and 'SYM' to address statements such as "66.3% of the vote"


def _handle_noun(noun_token: Token) -> (str, str):
    """
    When processing a token (in add_token_details) that is a noun, first handle the special
    cases of a proper noun, pronoun, family member role, etc. Lastly, process a general noun.

    :param noun_token: Token of the noun
    :return: Two strings, the noun text and type
    """
    # Get text with adjectives and first level of preposition only
    noun_text = noun_token.text
    noun_texts = [noun_text]
    for child_token in noun_token.children:
        if child_token.dep_ == 'prep':
            noun_texts.append(child_token.text)
            for child2 in child_token.children:
                if child2.pos_ not in unwanted_tokens and child2.dep_ != 'prep' and child2.text != '.' and \
                        ((child2.dep_ == 'det' and child2.text == 'no') or child2.dep_ != 'det'):
                    if child2.dep_ == 'poss':
                        noun_texts.append(f'{child2.text}/poss/')
                    else:
                        for child3 in child2.children:
                            if child3.pos_ == 'SYM':
                                noun_texts.append(child3.text)
                        noun_texts.append(child2.text)
        else:
            if child_token.pos_ not in unwanted_tokens and child_token.text != '.' and \
                    ((child_token.dep_ == 'det' and child_token.text == 'no') or child_token.dep_ != 'det'):
                if child_token.dep_ == 'poss':
                    noun_texts.append(f'{child_token.text}/poss/')
                else:
                    noun_texts.append(child_token.text)
    noun_texts_in_order = []
    for token in noun_token.subtree:
        if token.text in noun_texts:
            noun_texts_in_order.append(token.text)
        elif f'{token.text}/poss/' in noun_texts:
            noun_texts_in_order.append(f'{token.text}/poss/')
    full_noun_text = space.join(noun_texts_in_order)
    # Handle proper nouns and pronouns
    if 'PROPN' in noun_token.pos_:      # Proper noun
        return _process_proper_noun(noun_token, full_noun_text)
    elif 'Prs' in noun_token.morph.get('PronType'):    # Personal pronoun
        return _process_personal_pronoun(noun_token)
    # Handle references to family members ('brother', 'sister', ...) or 'family'
    elif noun_text.lower() in family_roles:
        gender = family_members[noun_text.lower()]
        return full_noun_text, f'{gender}SINGPERSON' if gender else f'SINGPERSON'
    elif noun_text.lower()[0:-1] in family_roles:  # Check if plural family members were referenced
        gender = family_members[noun_text.lower()[0:-1]]   # Check if plural family members were referenced
        return full_noun_text, f'{gender}PLURALPERSON' if gender else f'PLURALPERSON'
    elif noun_text.lower() in family_text:
        return full_noun_text, 'PLURALPERSON'
    else:
        return _process_noun(noun_token, full_noun_text)


def _process_noun(token: Token, full_text: str) -> (str, str):
    """
    When processing a token that is a general noun, capture its number, gender, etc.

    :param token: Token of the noun
    :param full_text: Full text of the noun, with adjectives, prepositions, ...
    :return: Two strings, the entity text and type
    """
    symbols = [t.text for t in token.children if t.pos_ == 'SYM']
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
    if 'PERCENT' in ent_type or 'MONEY' in ent_type:    # Clean up spaces introduced by the parse
        full_text = full_text.replace(' %', '%')
        for sym in symbols:
            if full_text[full_text.index(sym) + 2].isdigit():
                full_text = full_text.replace(f'{sym} ', sym)
            elif full_text[full_text.index(sym) - 2].isdigit():
                full_text = full_text.replace(f' {sym}', sym)
    return full_text, ent_type


def _process_prep_object(token: Token, dictionary: dict, prep_key: str):
    """
    When processing a token that is a preposition, capture its object details.

    :param token: Token of the preposition
    :param dictionary: Dictionary that the token details should be added to
    :param prep_key: Dictionary key where the details are added
    :return: None (Specified dictionary is updated)
    """
    # Retrieve the text for nouns (including adjectives and compound nouns)
    prep_ent, prep_ent_type = _handle_noun(token)
    prep_ent_detail = dict()
    prep_ent_detail['detail_text'] = prep_ent.split('$&')[0]
    prep_ent_detail['detail_type'] = prep_ent_type
    # Recursively call if there are more objects, related by conjunction
    for child in token.children:
        if 'cc' == child.dep_:
            dictionary[f'{prep_key}_cc'] = child.text
        elif 'conj' == child.dep_:
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


def _process_proper_noun(token: Token, full_text: str) -> (str, str):
    """
    When processing a token that is a proper noun, return the text of the noun and its
    'type' (gender + single/plural + PERSON).

    :param token: Token of the proper noun
    :param full_text: Full text of the noun, with adjectives, prepositions, ...
    :return: A tuple holding the text of the noun and its 'type' (gender + single/plural + PERSON/
             GPE/LOC/EVENT/...).
    """
    entity_type = token.ent_type_
    if entity_type.endswith('DATE') or entity_type.endswith('TIME'):
        return full_text, entity_type
    if entity_type.endswith('GPE') or entity_type.endswith('LOC') or entity_type.endswith('FAC') \
            or entity_type.endswith('ORG') or entity_type.endswith('NORP') or entity_type.endswith('EVENT') \
            or entity_type.endswith('NOUN'):
        return _process_noun(token, full_text)
    return full_text, check_name_gender(full_text)


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
    ent = token.text.split('$&')[0]
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
            add_token_details(child, dictionary, token_key)
        elif 'cc' == child.dep_:
            dictionary[f'{token_key}_cc'] = child.text
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
                    add_to_dictionary_values(ent_dict, 'preps', prep_dict, dict)
    add_to_dictionary_values(dictionary, token_key, ent_dict, dict)
