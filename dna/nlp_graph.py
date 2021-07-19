import logging

from spacy.language import Language
from spacy.tokens import Doc, Token

from utilities import EMPTY_STRING, SPACE, add_to_dictionary_values

dna_stopwords = ['a', 'an', 'just', 'quite', 'really', 'the', 'very']


def extract_graph_details(sentence: Doc, sentence_dicts: list, nlp: Language):
    """
    Extract the subject, verb, object details from a sentence and store these in a dictionary.

    :param sentence The sentence to be processed (it is defined as a spaCy Doc due to previous processing)
    :param sentence_dicts An array of dictionaries holding the subject/verb/object details of each sentence
    :param nlp A spaCy Language model
    :return None (the sentence_dicts array is updated)
    """
    logging.info(f'Creating sentence dictionary for {sentence.text}')
    # Store graph details for each sentence, starting from the ROOT verb
    sentence_dict = dict()
    nlp_sent = nlp(sentence.text)
    get_named_entities(nlp_sent, sentence_dict)
    for token in nlp_sent:
        if token.dep_ == 'ROOT':
            process_verb(token, sentence_dict, nlp)
    sentence_dicts.append(sentence_dict)


def get_named_entities(nlp_sentence: Doc, sentence_dict: dict):
    """
    Get the FAC (facility), ORG (organization), GPE, LOC (location), EVENT,
    DATE and TIME entities from the input sentence.

    :param nlp_sentence: The sentence (a spaCy Doc)
    :param sentence_dict: A dictionary that is updated with time-related details
    :return: None (the sentence_dict is updated with the text of the named entities, where the
             key is the entity type)
    """
    for ent in nlp_sentence.ents:
        if ent.label_ in ['FAC', 'ORG', 'GPE', 'LOC', 'EVENT', 'DATE', 'TIME']:
            add_to_dictionary_values(sentence_dict, ent.label_, ent.text, str)
    return


def process_verb(token: Token, dictionary: dict, nlp: Language):
    """
    When processing a token (that is a verb), capture its details. Note that all processing
    of a narrative is based on the sentences and their ROOT verbs.

    :param token: Verb token from spacy parse
    :param dictionary: Dictionary that the token details should be added to
    :param nlp: A spaCy Language model
    :return: None (Specified dictionary is updated)
    """
    logging.info(f'Processing the verb, {token.text}')
    ent = token.text
    verb_dict = dict()
    verb_dict['verb_text'] = ent
    verb_dict['verb_lemma'] = token.lemma_
    tense = token.morph.get('Tense')
    if not tense:
        verb_dict['tense'] = 'Pres'
    else:
        verb_dict['tense'] = tense[0]
    for child in token.children:
        if 'acomp' == child.dep_:          # Adjectival phrase that complements the verb
            _add_token_details(child, dictionary, 'complements')
        elif 'advcl' == child.dep_:        # Adverbial clause of the verb
            _add_token_details(child, verb_dict, 'verb_advcl')
        elif 'agent' == child.dep_:          # Agent of a passive verb, introduced by the word, 'by'
            for child2 in child.children:
                if 'pobj' == child2.dep_:    # The real subject is the object of the preposition, 'by'
                    _add_token_details(child2, dictionary, 'subjects')
        elif 'aux' == child.dep_:
            # Care about the tense of the primary auxiliaries (be, do, have)
            # But not using those auxiliaries for semantics
            if 'will' == child.text:
                verb_dict['tense'] = 'Fut'
            elif child.lemma_ in ['be', 'do', 'have']:
                child_tense = child.morph.get('Tense')
                if verb_dict['tense'] == 'Pres' and child_tense and child_tense == 'Past':
                    verb_dict['tense'] = 'Past'
            # TODO: What to do with the modals ('would', 'should') and verbs such as "enjoyed" in "enjoyed being"?
        elif 'conj' == child.dep_:   # Another verb related via a coordinating conjunction
            process_verb(child, dictionary, nlp)
        # TODO: Handle subjects that are themselves clauses (csubj and csubjpass)
        elif 'neg' == child.dep_:   # Verb is negated
            verb_dict['negation'] = True
        elif 'nsubj' == child.dep_:   # Subject of the verb
            _add_token_details(child, dictionary, 'subjects')
        elif 'nsubjpass' == child.dep_:   # Subject of a passive verb -> Which means that it is an object
            _add_token_details(child, dictionary, 'objects')
        elif 'obj' in child.dep_ or 'attr' in child.dep_:  # Object or attribute of the verb
            _add_token_details(child, verb_dict, 'objects')
        elif 'prep' in child.dep_:    # Preposition associated with the verb
            # TODO: Handle pcomp (where the preposition's object is itself a clause)
            prep_dict = dict()
            prep_dict['prep_text'] = child.text
            for prep_dep in child.children:
                _add_token_details(prep_dep, prep_dict, 'prep_details')
            add_to_dictionary_values(verb_dict, 'preps', prep_dict, dict)
        elif 'xcomp' == child.dep_:  # Clausal complement of the verb
            _add_token_details(child, verb_dict, 'verb_xcomp')
    add_to_dictionary_values(dictionary, 'verbs', verb_dict, dict)
    return


# Functions internal to the module
def _add_token_details(token: Token, dictionary: dict, key: str):
    """
    Simplify the token text, get the token's entity type (or define one if blank), and
    add the token details to the specified dictionary key.

    :param token: Token from spacy parse
    :param dictionary: Dictionary that the token details should be added to
    :param key: Dictionary key where the details are added
    :return: None (Specified dictionary is updated)
    """
    logging.info(f'Processing the token, {token.text}, for key, {key}, of type, {token.ent_type_}')
    ent_type = token.ent_type_
    long_text = ''
    # Handle pronouns
    if 'Prs' in token.morph.get('PronType'):
        ent = token.text
        if '1' in token.morph.get('Person'):
            if 'Plur' in token.morph.get('Number'):
                ent_type = 'INCLUSIVE'
            else:
                ent_type = 'NARRATOR'
        elif '2' in token.morph.get('Person'):
            ent_type = 'AUDIENCE'
        elif '3' in token.morph.get('Person'):
            if 'Plur' in token.morph.get('Number'):
                ent_type = 'GROUP'
            else:
                ent_type = 'PERSON'
    elif 'verb' in key:
        ent = token.text
        ent_type = 'VERB'
    else:
        # Retrieve the text for nouns (including adjectives and compound nouns)
        ent = SPACE.join(t.text for t in token.children if t.dep_ in ['amod', 'compound']) + SPACE + token.text
        if ent_type == EMPTY_STRING:
            ent_type = 'NOUN'
        # Account for a determiner of 'no' - i.e., nothing (for ex, 'no information  was found')
        # TODO: Make use of NEG
        if any([tc for tc in token.children if tc.dep_ == 'det' and tc.text == 'no']):
            ent_type = 'NEG ' + ent_type

    # Set up the entity's dictionary and add basic details
    ent_dict = dict()
    # Lists of dictionaries have plural names while individual dictionary keys should not
    ent_dict[f'{key[0:-1] if key.endswith("s") else key}_text'] = ent
    if 'verb' in key:
        ent_dict[f'{key}_lemma'] = token.lemma_
    else:
        ent_dict[f'{key[0:-1] if key.endswith("s") else key}_type'] = ent_type

    # Process specific children (conjunctions and prepositions)
    for child in token.children:
        if ent_type == 'VERB' and ('obj' in child.dep_ or 'attr' in child.dep_):
            if 'advcl' in key:
                # Object/attr is part of the adverbial clause, so it adds to the current ent_dict
                _add_token_details(child, ent_dict, 'objects')
            else:
                _add_token_details(child, dictionary, 'objects')
        # TODO: Make use of a "cc" of "or" or "nor"
        elif 'conj' == child.dep_:
            _add_token_details(child, dictionary, key)
        elif 'prep' in child.dep_:
            prep_dict = dict()
            # Lists of dictionaries have plural names while individual dictionary keys should not
            prep_dict[f'{key[0:-1] if key.endswith("s") else key}_prep_text'] = child.text
            for prep_child in child.children:
                if 'obj' in prep_child.dep_ or 'attr' in prep_child.dep_:
                    # Object/attr is part of the prepositional clause, so it adds to the current prep_dict
                    _process_prep_object(prep_child, prep_dict, (key[0:-1] if key.endswith("s") else key))
            add_to_dictionary_values(ent_dict, f'{key[0:-1] if key.endswith("s") else key}_preps', prep_dict, dict)
    add_to_dictionary_values(dictionary, key, ent_dict, dict)


def _process_prep_object(token: Token, dictionary: dict, key: str):
    """
    When processing a token (in add_token_details), capture prepositions and their objects.

    :param token: Token of the preposition
    :param dictionary: Dictionary that the token details should be added to
    :param key: Dictionary key where the details are added
    :return: None (Specified dictionary is updated)
    """
    # Retrieve the text for nouns (including adjectives and compound nouns)
    prep_ent = SPACE.join(t.text for t in token.children if t.dep_ in ['amod', 'compound']) + SPACE + token.text
    prep_ent_type = token.ent_type_
    if prep_ent_type == EMPTY_STRING:
        prep_ent_type = 'NOUN'
    prep_ent_detail = dict()
    prep_ent_detail[f'{key[0:-1] if key.endswith("s") else key}_prep_object'] = prep_ent
    prep_ent_detail[f'{key[0:-1] if key.endswith("s") else key}_prep_object_type'] = prep_ent_type
    # Recursively call if there are more objects, related by conjunction
    for child in token.children:
        if 'conj' == child.dep_:
            _process_prep_object(child, dictionary, key)
    add_to_dictionary_values(dictionary, f'{key}_prep_objects', prep_ent_detail, dict)
    return
