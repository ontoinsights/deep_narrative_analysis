# Processing to create the sentence dictionary:
#    'text': 'narrative_text', 'sentence_offset': #,
#    'AGENTS': ['agent1', 'agent2', ...], 'LOCS': ['location1', ...],
#    'TIMES': ['dates_or_times1', ...], 'EVENTS': ['event1', ...],
#    'chunks': [chunk1, chunk2, ...]
# Note that 'punct': '?' may also be included above
# Where each chunk is a dictionary with the form:
#    'chunk_text': 'chunk_text',
#    'verbs': [{'verb_text': 'verb_text', 'verb_lemma': 'verb_lemma', 'tense': 'tense_such_as_Past',
#               'subject_text': 'subject_text', 'subject_type': 'type_such_as_SINGNOUN',
#               'objects': [{'object_text': 'verb_object_text', 'object_type': 'type_eg_NOUN'}]
#               'preps': [{'prep_text': 'preposition_text',
#                          'prep_details': [{'detail_text': 'preposition_object', 'detail_type': 'type_eg_SINGGPE'}]}]
# There may be more than 1 verb when there is a root verb + an xcomp
# Called by nlp.py, Main function: extract_sentence details

import logging
from spacy.language import Language
from spacy.tokens import Token

from dna.nlp_sentence_tokens import add_token_details
from dna.utilities import objects_string, subjects_string, add_to_dictionary_values, processed_prepositions


def _adjust_xcomp_prt(processing: list) -> list:
    """
    Clean up the verb_processing text if there are both prt and xcomp details. If there is only a
    single 'xcomp' or 'prt', then just remove the final '$'. If both, correct either the first or
    second verb of the 'xcomp' details for one of the verbs (the one matching the prt verb) to h
    ave it reference the full 'prt' text (verb + prt).

    :param processing: Array holding the xcomp and prt details
    :return: List holding the final xcomp/prt details
    """
    xcomp_tuples = []
    prts = []
    for detail in processing:
        if 'xcomp' in detail:
            xcomp_tuples.append((detail.split('> ')[1].split(', ')[0], detail.split(', ')[1]))
        elif 'prt' in detail:
            prts.append(detail.split('> ')[1])
    if xcomp_tuples and prts:
        new_xcomps = []
        for verb1, verb2 in xcomp_tuples:
            for prt in prts:
                if prt.startswith(verb1):
                    verb1 = prt
                    break
                elif prt.startswith(verb2):
                    verb2 = prt
                    break
            new_xcomps.append(f'xcomp > {verb1}, {verb2}')
        return new_xcomps
    elif xcomp_tuples:
        return [f'xcomp > {verb1}, {verb2}' for verb1, verb2 in xcomp_tuples]
    elif prts:
        return [f'prt > {prt}' for prt in prts]


def _process_aux(aux_token: Token, verb_dictionary: dict):
    """
    When processing a token that is an auxiliary, such as a modal or a primary auxiliary
    (be, do, have), get the details.

    :param aux_token: Token holding the spaCy details about the auxiliary
    :param verb_dictionary: Dictionary holding all the details about the verb/sentence
                            being processed
    :return: None (the verb_dictionary is updated)
    """
    if aux_token.lemma_ == 'to':
        return
    elif aux_token.lemma_ in ('be', 'do', 'have'):
        child_tense = aux_token.morph.get('Tense')
        if verb_dictionary['tense'] == 'Pres' and child_tense and child_tense == 'Past':
            verb_dictionary['tense'] = 'Past'
    else:
        if aux_token.lemma_ == 'will':
            verb_dictionary['tense'] = 'Fut'
        # Aux is expressing mood (ex: enjoyed/hated being with), possibility (could, may, might, should),
        # intent (would, will), ability (can/cannot), suggestion (should) or necessity/obligation (must),
        # or is asking permission (can, may, could) or requesting (would, will, can, could)
        verb_dictionary['verb_aux'] = aux_token.text


def extract_chunk_details(chunk: str, chunk_dict: dict, nlp: Language) -> dict:
    """
    Extract the subject, verb, object details from a sentence and store these in a dictionary for
    further processing (and rendering in Turtle).

    :param chunk: The sentence/chunk to be processed
    :param chunk_dict: The dictionary holding the chunk details
    :param nlp: A spaCy Language model
    :return: Returns the updated chunk_dict
    """
    logging.info(f'Creating chunk dictionary for {chunk}')
    nlp_chunk = nlp(chunk)
    # There should only be 1 root verb, because the text was already split
    process_verb([chunk.root for chunk in nlp_chunk.sents][0], chunk_dict, nlp)
    return chunk_dict


def process_verb(token: Token, dictionary: dict, nlp: Language):
    """
    When processing a token (that is a verb), capture its details. Note that all processing
    of a narrative is based on the sentences/chunks and their ROOT verbs.

    :param token: Verb token from spacy parse
    :param dictionary: Dictionary that the token details should be added to
    :param nlp: A spaCy Language model
    :return: None (Specified dictionary is updated)
    """
    logging.info(f'Processing the verb, {token.text}')
    verb_dict = dict()
    verb_dict['verb_text'] = token.text
    verb_dict['verb_lemma'] = token.lemma_
    tense = token.morph.get('Tense')
    verb_dict['tense'] = tense[0] if tense else 'Pres'
    # Processing is based on dependency parsing
    # Dependency tokens are defined at https://downloads.cs.stanford.edu/nlp/software/dependencies_manual.pdf
    for child in token.children:
        if child.dep_ == 'xcomp':   # Clausal complement - e.g., 'he attempted robbing the bank' (xcomp = robbing)
            # For the above, xcomp > attempt, rob
            add_to_dictionary_values(dictionary, 'verb_processing', f'xcomp > {token.lemma_}, {child.lemma_}', str)
            process_verb(child, dictionary, nlp)
            for child_child in child.children:
                if child_child.dep_ == 'conj':
                    # Conjunction of xcomps ('Sue failed to win the race or to finish.') handled as
                    #     3 verbs with multiple xcomp processing details
                    add_to_dictionary_values(dictionary, 'verb_processing',
                                             f'xcomp > {token.lemma_}, {child_child.text}', str)
                    process_verb(child_child, dictionary, nlp)
        elif 'prt' in child.dep_:   # Phrasal verb particle - e.g., 'he gave up the jewels' (up = prt)
            # For the above, prt > give up
            add_to_dictionary_values(dictionary, 'verb_processing', f'prt > {token.lemma_} {child.text}', str)
        elif child.dep_ in ('acomp', 'advcl', 'ccomp'):    # Various complements of the verb
            add_token_details(child, verb_dict, f'verb_{child.dep_}')
        elif 'agent' == child.dep_:          # Agent of a passive verb, introduced by the word, 'by'
            for child2 in child.children:
                if 'pobj' == child2.dep_:    # The real subject is the object of the preposition, 'by'
                    add_token_details(child2, dictionary, subjects_string)
        elif 'aux' == child.dep_:
            # Care about modals, tense of the primary auxiliaries (be, do, have), and semantics of mood
            _process_aux(child, verb_dict)
        elif 'neg' == child.dep_:   # Verb is negated
            verb_dict['negation'] = True
        elif 'nsubj' == child.dep_:   # Subject of the verb
            add_token_details(child, dictionary, subjects_string)
        elif 'nsubjpass' == child.dep_:   # Subject of a passive verb -> Which means that it is an object
            add_token_details(child, dictionary, objects_string)
        # TODO: Handle subjects that are themselves clauses (csubj and csubjpass)
        elif 'obj' in child.dep_ or child.dep_ in ('attr', 'dative'):  # Object or attribute of the verb
            add_token_details(child, verb_dict, objects_string)
        elif 'prep' in child.dep_:    # Preposition associated with the verb
            # Only concerned with certain prepositions and their semantics
            if child.text.lower() not in processed_prepositions:
                continue
            prep_dict = dict()
            prep_dict['prep_text'] = child.text
            for prep_dep in child.children:
                add_token_details(prep_dep, prep_dict, 'prep_details')
            add_to_dictionary_values(verb_dict, 'preps', prep_dict, dict)
    # Need to adjust the processing if there are prt and xcomp children
    if 'verb_processing' in dictionary and not dictionary['verb_processing']:
        # dictionary['verb_processing'] = _adjust_xcomp_prt(dictionary['verb_processing'])
        del dictionary['verb_processing']
    add_to_dictionary_values(dictionary, 'verbs', verb_dict, dict)
