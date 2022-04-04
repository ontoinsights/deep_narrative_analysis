# Processing to create the sentence dictionary, which has the form:
#    'text': 'narrative_text',
#    'LOCS': ['location1', ...], 'TIMES': ['dates_or_times1', ...], 'EVENTS': ['event1', ...],
#    'subjects': [{'subject_text': 'subject_text', 'subject_type': 'type_such_as_SINGNOUN'},
#                 {'subject_text': 'Narrator', 'subject_type': 'example_FEMALESINGPERSON'}],
#    'verbs': [{'verb_text': 'verb_text', 'verb_lemma': 'verb_lemma', 'tense': 'tense_such_as_Past',
#               'preps': [{'prep_text': 'preposition_text',
#                          'prep_details': [{'detail_text': 'preposition_object', 'detail_type': 'type_eg_SINGGPE'}]}],
#                          # Preposition object may also have a preposition - for ex, 'with the aid of the police'
#                          # If so, following the 'detail_type' entry would be another 'preps' element
#                          'objects': [{'object_text': 'verb_object_text', 'object_type': 'type_eg_NOUN'}]}]}]}]}]}
# Called by nlp.py

import logging
import os
import pickle

from spacy.language import Language
from spacy.tokens import Doc, Token

from nlp_sentence_tokens import add_token_details
from utilities import objects_string, resources_root, subjects_string, add_to_dictionary_values, processed_prepositions

verb_prt_file = os.path.join(resources_root, 'verb-prt-idioms.pickle')
with open(verb_prt_file, 'rb') as inFile:
    verb_prt_dict = pickle.load(inFile)

verb_xcomp_file = os.path.join(resources_root, 'verb-xcomp-idioms.pickle')
with open(verb_xcomp_file, 'rb') as inFile:
    verb_xcomp_dict = pickle.load(inFile)


def extract_dictionary_details(sentence: str, sentence_dicts: list, nlp: Language, gender: str,
                               family_dict: dict, sentence_offset: int):
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
    :param sentence_offset: Integer indicating the order of the sentence in the overall narrative
    :returns: None (the sentence_dicts array is updated)
    """
    logging.info(f'Creating sentence dictionary for {sentence}')
    # Store details for each sentence, starting from the ROOT verb
    sentence_dict = dict()
    sentence_dict['text'] = sentence
    sentence_dict['offset'] = sentence_offset
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
    :param sentence_dict: A dictionary that is updated with time-, location- and/or event-related details
    :returns: None (sentence_dict is updated with the text of the named entities, where the
             key is either 'LOCS' or 'TIMES')
    """
    for ent in nlp_sentence.ents:
        if ent.label_ in ('GPE', 'LOC', 'FAC'):
            add_to_dictionary_values(sentence_dict, 'LOCS', ent.text, str)
        elif ent.label_ in ('DATE', 'TIME'):
            add_to_dictionary_values(sentence_dict, 'TIMES', ent.text, str)
        elif ent.label_ == 'EVENT':
            add_to_dictionary_values(sentence_dict, 'EVENTS', ent.text, str)
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
    :returns: None (Specified dictionary is updated)
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
        if child.dep_ == 'xcomp':   # Clausal complement - e.g., 'he attempted robbing the bank' (xcomp = robbing)
            if token.lemma_ in verb_xcomp_dict.keys():
                first_verb = verb_xcomp_dict[token.lemma_].split(' > :')[1].split(' ')[0].lower()
            else:
                first_verb = token.lemma_
            verb_dict['verb_processing'] = f'xcomp > :{first_verb}, {child.lemma_}'
            process_verb(child, dictionary, nlp, gender, family_dict)
        elif 'prt' in child.dep_:     # Phrasal verb particle - e.g., 'he gave up the jewels' (up = prt)
            verb_dict['verb_text'] = f'{ent} {child.text}'
            # Check for a substitution in the verb_idioms dictionary
            check_text = f'{token.lemma_} {child.text}'
            if check_text in verb_prt_dict.keys():
                verb_dict['verb_processing'] = verb_prt_dict[check_text]
            else:
                # verb + prt was not found in the dictionary - log this for manual addition
                logging.warning(f'Verb Prt not found, {token.lemma_} {child.text}')
        elif child.dep_ in ('acomp', 'advcl', 'ccomp'):    # Various complements of the verb
            add_token_details(child, verb_dict, f'verb_{child.dep_}', gender, family_dict)
        elif 'agent' == child.dep_:          # Agent of a passive verb, introduced by the word, 'by'
            for child2 in child.children:
                if 'pobj' == child2.dep_:    # The real subject is the object of the preposition, 'by'
                    add_token_details(child2, dictionary, subjects_string, gender, family_dict)
        elif 'aux' == child.dep_:
            # Care about modals, tense of the primary auxiliaries (be, do, have), and semantics of mood
            if 'will' == child.text:
                # TODO: Is it ok to ignore other modals ('could/would/should', 'shall/must/may', 'can', 'might')?
                verb_dict['tense'] = 'Fut'
            elif child.lemma_ in ('be', 'do', 'have'):
                child_tense = child.morph.get('Tense')
                if verb_dict['tense'] == 'Pres' and child_tense and child_tense == 'Past':
                    verb_dict['tense'] = 'Past'
            else:
                # Aux is likely expressing mood, such as "enjoyed/hated being with"
                verb_dict['verb_aux'] = child.text
        elif 'conj' == child.dep_:   # Another verb related via a coordinating conjunction
            process_verb(child, dictionary, nlp, gender, family_dict)
        elif 'neg' == child.dep_:   # Verb is negated
            verb_dict['negation'] = True
        elif 'nsubj' == child.dep_:   # Subject of the verb
            add_token_details(child, dictionary, subjects_string, gender, family_dict)
        elif 'nsubjpass' == child.dep_:   # Subject of a passive verb -> Which means that it is an object
            # TODO: Problem if > one verb is used, connected by a conjunction; Obj needs to be associated with both
            add_token_details(child, verb_dict, objects_string, gender, family_dict)
        # TODO: Handle subjects that are themselves clauses (csubj and csubjpass)
        elif 'obj' in child.dep_ or 'attr' in child.dep_:  # Object or attribute of the verb
            add_token_details(child, verb_dict, objects_string, gender, family_dict)
        elif 'prep' in child.dep_:    # Preposition associated with the verb
            # Only concerned with certain prepositions and their semantics
            if child.text.lower() not in processed_prepositions:
                continue
            # TODO: Handle pcomp (where the preposition's object is itself a clause)
            prep_dict = dict()
            prep_dict['prep_text'] = child.text
            for prep_dep in child.children:
                add_token_details(prep_dep, prep_dict, 'prep_details', gender, family_dict)
            add_to_dictionary_values(verb_dict, 'preps', prep_dict, dict)
    add_to_dictionary_values(dictionary, 'verbs', verb_dict, dict)
    return
