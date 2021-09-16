# Processing to create the sentence dictionary, which has the form:
#    'text': 'narrative_text', 'LOCS': ['location'], 'TIMES': ['date_or_time'],
#    'subjects': [{'subject_text': 'subject_text', 'subject_type': 'type_such_as_SINGNOUN'},
#                 {'subject_text': 'Narrator', 'subject_type': 'example_FEMALESINGPERSON'}],
#    'verbs': [{'verb_text': 'verb_text', 'verb_lemma': 'verb_lemma', 'tense': 'tense_such_as_Past',
#               'preps': [{'prep_text': 'preposition_text',
#                          'prep_details': [{'prep_text': 'preposition_object', 'prep_type': 'type_eg_SINGGPE'}]}],
#                          # Preposition object may also have a preposition - for ex, 'with the aid of the police'
#                          # If so, following the 'prep_type' entry would be another 'preps' element
#                          'objects': [{'object_text': 'verb_object_text', 'object_type': 'type_eg_NOUN'}]}]}]}]}]}
# Called by nlp.py

import logging

from spacy.language import Language
from spacy.tokens import Doc, Token

from idiom_processing import get_verb_idiom
from nlp_sentence_tokens import add_token_details
from utilities import objects_string, subjects_string, verbs_string, add_to_dictionary_values, processed_prepositions


def extract_dictionary_details(sentence: str, sentence_dicts: list, nlp: Language, gender: str, family_dict: dict):
    """
    Extract the subject, verb, object details from a sentence and store these in a dictionary for
    further processing (and rendering in Turtle).

    :param sentence: The sentence to be processed
    :param sentence_dicts: An array of dictionaries holding the subject/verb/object details of each sentence
    :param nlp: A spaCy Language model
    :param gender: Either an empty string or one of the values, AGENDER, BIGENDER, FEMALE or MALE -
                   indicating the gender of the narrator
    :param family_dict: A dictionary containing the names of family members and their relationship
                        to the narrator/subject
    :return None (the sentence_dicts array is updated)
    """
    logging.info(f'Creating sentence dictionary for {sentence}')
    # Store details for each sentence, starting from the ROOT verb
    sentence_dict = dict()
    sentence_dict['text'] = sentence
    if sentence == "New line":     # Track ending of paragraphs
        sentence_dicts.append(sentence_dict)
        return
    nlp_sent = nlp(sentence)
    get_named_entities_in_sentence(nlp_sent, sentence_dict)
    for token in nlp_sent:
        if token.dep_ == 'ROOT':
            process_verb(token, sentence_dict, nlp, gender, family_dict)
    sentence_dicts.append(sentence_dict)
    return


def get_named_entities_in_sentence(nlp_sentence: Doc, sentence_dict: dict):
    """
    Get the GPE, LOC (location), EVENT, DATE and TIME entities from the input sentence.

    :param nlp_sentence: The sentence (a spaCy Doc)
    :param sentence_dict: A dictionary that is updated with time-related details
    :return: None (sentence_dict is updated with the text of the named entities, where the
             key is either 'LOCS' or 'TIMES')
    """
    for ent in nlp_sentence.ents:
        if ent.label_ in ('GPE', 'LOC', 'FAC'):
            add_to_dictionary_values(sentence_dict, 'LOCS', ent.text, str)
        if ent.label_ in ('EVENT', 'DATE', 'TIME'):
            add_to_dictionary_values(sentence_dict, 'TIMES', ent.text, str)
    return


def process_verb(token: Token, dictionary: dict, nlp: Language, gender: str, family_dict: dict):
    """
    When processing a token (that is a verb), capture its details. Note that all processing
    of a narrative is based on the sentences and their ROOT verbs.

    :param token: Verb token from spacy parse
    :param dictionary: Dictionary that the token details should be added to
    :param nlp: A spaCy Language model
    :param gender: Either an empty string or one of the values, AGENDER, BIGENDER, FEMALE or
                   MALE - indicating the gender of the narrator
    :param family_dict: A dictionary containing the names of family members and their
                        relationship to the narrator/subject
    :return: None (Specified dictionary is updated)
    """
    logging.info(f'Processing the verb, {token.text}')
    ent = token.text
    verb_dict = dict()
    verb_dict['verb_text'] = ent
    verb_dict['verb_lemma'] = token.lemma_
    tense = token.morph.get('Tense')
    verb_dict['tense'] = tense[0] if tense else 'Pres'
    # Processing is based on dependency parsing
    # Dependency tokens are defined at https://downloads.cs.stanford.edu/nlp/software/dependencies_manual.pdf
    for child in token.children:
        if 'acomp' == child.dep_:          # Adjectival phrase that complements the verb
            add_token_details(child, dictionary, 'verb_acomp', gender, family_dict)
        elif 'advmod' == child.dep_:        # Adverbial modifier
            # Only care about before/after and earlier/later (for now)
            add_token_details(child, verb_dict, 'verb_advmod', gender, family_dict)
        elif 'advcl' == child.dep_:        # Adverbial clause of the verb
            add_token_details(child, verb_dict, 'verb_advcl', gender, family_dict)
        elif 'agent' == child.dep_:          # Agent of a passive verb, introduced by the word, 'by'
            for child2 in child.children:
                if 'pobj' == child2.dep_:    # The real subject is the object of the preposition, 'by'
                    add_token_details(child2, dictionary, subjects_string, gender, family_dict)
        elif 'aux' == child.dep_:
            # Care about the tense of the primary auxiliaries (be, do, have)
            # TODO: Semantics of aux such as "enjoyed being with" vs "hated being with"
            if 'will' == child.text:
                verb_dict['tense'] = 'Fut'
            elif child.lemma_ in ('be', 'do', 'have'):
                child_tense = child.morph.get('Tense')
                if verb_dict['tense'] == 'Pres' and child_tense and child_tense == 'Past':
                    verb_dict['tense'] = 'Past'
            # TODO: What to do with the modals ('would', 'should')?
        elif 'conj' == child.dep_:   # Another verb related via a coordinating conjunction
            process_verb(child, dictionary, nlp, gender, family_dict)
        # TODO: Handle subjects that are themselves clauses (csubj and csubjpass)
        elif 'neg' == child.dep_:   # Verb is negated
            verb_dict['negation'] = True
        elif 'nsubj' == child.dep_:   # Subject of the verb
            add_token_details(child, dictionary, subjects_string, gender, family_dict)
        elif 'nsubjpass' == child.dep_:   # Subject of a passive verb -> Which means that it is an object
            # TODO: What if more than one verb is used, connected by a conjunction?
            add_token_details(child, verb_dict, objects_string, gender, family_dict)
        elif 'obj' in child.dep_ or 'attr' in child.dep_:  # Object or attribute of the verb
            add_token_details(child, verb_dict, objects_string, gender, family_dict)
        elif 'prt' in child.dep_:     # Phrasal verb particle
            # Check for a substitution in the verb_idioms dictionary
            idiom, processing = get_verb_idiom(token.lemma_, child.text.lower())
            if idiom:
                verb_dict['verb_lemma'] = idiom
                verb_dict['verb_processing'] = processing
            else:
                # Idiom was not found in the dictionary - log this for manual addition
                logging.warning(f'Verb idiom not found, {token.lemma_} {child.text}')
        elif 'prep' in child.dep_:    # Preposition associated with the verb
            if child.text.lower() not in processed_prepositions:
                continue
            # TODO: Handle pcomp (where the preposition's object is itself a clause)
            # Check if there is processing defined for this verb/prep combination
            idiom, processing = get_verb_idiom(token.lemma_, child.text.lower())
            if idiom:
                verb_dict['verb_lemma'] = idiom
                verb_dict['verb_processing'] = processing
            else:
                prep_dict = dict()
                prep_dict['prep_text'] = child.text
                for prep_dep in child.children:
                    add_token_details(prep_dep, prep_dict, 'prep_details', gender, family_dict)
                add_to_dictionary_values(verb_dict, 'preps', prep_dict, dict)
        elif 'xcomp' == child.dep_:  # Clausal complement of the verb
            add_token_details(child, verb_dict, 'verb_xcomp', gender, family_dict)
    add_to_dictionary_values(dictionary, verbs_string, verb_dict, dict)
    return
