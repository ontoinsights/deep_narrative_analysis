# Processing to split sentences if sub-clauses have both a subject and verb
# Needs the nlp Language model from nlp.py passed as a parameter into the main function, split_clauses
# Called by nlp.py

import copy
import logging

from spacy.language import Language
from spacy.tokens import Span, Token

from utilities import cause_connectors, effect_connectors


def get_chunks(verb: Token, connector: list, chunk_sentence: Span, is_conj: bool) -> list:
    """
    Given a conjunctive verb, a connector token relating that verb to the root verb
    (such as 'and', 'but', ...) and the sentence that contains these tokens, determine if
    the sentence can be separated into clauses. Also separate sentences that are two clauses
    split by a semi-colon.

    :param verb: The token of the conjunctive verb
    :param connector: Tokens of the connectors between the root and conjunctive verbs
                      (if is_conj is true) or adverb modifiers of the conjunctive verb
                      (if is_conj is false)
    :param chunk_sentence: A Span representing the parsed sentence
    :param is_conj: A boolean indicating whether the connector is related to terms such as
                    'and', 'but', 'or' or is related to an adverbial clause
    :return: A list of the text of the clauses of the sentence (split if indicated by the
             logic below) or just the original sentence returned
    """
    logging.info(f'Getting the clauses in {chunk_sentence.text}')
    chunks = []
    # Is there a subject of the other clause's verb? That is required to split the sentence
    # An 'expl' is the word, 'there'
    subj2 = [subj for subj in verb.children if ('subj' in subj.dep_ or subj.dep_ == 'expl')]
    if len(subj2):
        # Yes ... Separate clauses
        # Get the tokens in sentence related to the 'other' verb's subtree
        seen = [ww for ww in verb.subtree if ww.pos_ != 'PUNCT']
        seen_chunk = ' '.join([ww.text for ww in seen]).strip() + '.'
        unseen = [ww for ww in chunk_sentence if ww not in seen and ww.pos_ != 'PUNCT']
        unseen_chunk = ' '.join([ww.text for ww in unseen]).strip() + '.'
        for conn in connector:
            if is_conj:
                # Remove the connector words (to prevent cycles and sentences such as 'Mary biked to the market and.')
                unseen_chunk = unseen_chunk.replace(f' {conn.text} ', ' ').replace(f' {conn.text}.', '.')
            else:
                # Remove the connector words (to prevent cycles) but NOT if there is a single auxiliary verb
                # If so, then the advmod is needed
                # For example, 'my daughter is home' (is = auxiliary verb, home = adverbial modifier)
                if not any([ww for ww in seen if ww.pos_ == 'AUX']) or any([ww for ww in seen if ww.pos_ == 'VERB']):
                    seen_chunk = _remove_startswith(seen_chunk, conn.text)
                    seen_chunk = seen_chunk.replace(f' {conn.text} ', ' ').replace(f' {conn.text}.', '.')
                if not any([ww for ww in unseen if ww.pos_ == 'AUX']) or any(
                        [ww for ww in unseen if ww.pos_ == 'VERB']):
                    unseen_chunk = _remove_startswith(unseen_chunk, conn.text)
        # Store the seen and unseen clauses as separate sentences
        chunks.append(unseen_chunk)
        chunks.append(seen_chunk)
    if len(chunks) > 0:
        return chunks
    else:
        return [chunk_sentence.text]


def split_clauses(sent_text: str, nlp: Language) -> list:
    """
    Perform splitting of sentences first by splitting by coordinating conjunctions (calling the function,
    split_by_conjunctions) and second by adverbial clauses and clausal complements.

    :param sent_text: The sentence to be split (as a string)
    :param nlp: A spaCy Language model
    :return: A list of new sentences/Spans created from the split
    """
    orig_sents = [sent_text]
    # Iterate until the sentences cannot be further decomposed/split
    while True:
        new_sents = []
        # Go through each sentence in the array
        for orig_sent in orig_sents:
            # Semi-colons automatically split sentences
            if '; ' in orig_sent:
                semicolon_index = orig_sent.index('; ')
                new_sents = [f'{orig_sent[:semicolon_index]}.', f'{orig_sent[semicolon_index + 2:]}.']
                break
            # First split by words such as 'and', 'but', 'or', ... related to the 'root' verb
            for chunk_sent in nlp(orig_sent).sents:
                # nlp(orig_sent) creates a new Document to allow .sents processing of ROOT verbs
                # TODO: Capture 'or', 'nor' as the splitting word (e.g., as an alternative)
                intermed_sents, splitting_word = _split_by_conjunctions(chunk_sent)
                # Split by advcl and xcomp IF these have their own subject/verb
                # Example: 'When I went to the store, I met George.' ('when ...' is an adverbial clause)
                for intermed_sent in intermed_sents:
                    for chunk_sent2 in nlp(intermed_sent).sents:
                        # nlp(intermed_sent) 're-tokenizes' in order to create a new Document, as above
                        clausal_verbs, connectors = _check_subject_in_clause(chunk_sent2)
                        # Need to have both a clause and a connector/modifier for this logic
                        if len(clausal_verbs) > 0:
                            new_sents.extend(get_chunks(clausal_verbs[0], connectors, chunk_sent2, False))
                        else:
                            new_sents.append(intermed_sent)
        # Check if the processing has resulted in new sentence clauses
        if len(orig_sents) == len(new_sents):
            # If not, break out of the while loop
            break
        else:
            # New clauses, so keep processing
            orig_sents = copy.deepcopy(new_sents)
    return new_sents


# Functions internal to the module
def _check_subject_in_clause(cls_sentence: Span) -> (list, list):
    """
    Return a list of the verb and connector tokens in a sentence/Span IF the sentence
    has dependent clauses with their own subject and verb (and a few other conditions are
    met as documented below).

    :param cls_sentence: The sentence/Span to be analyzed
    :return: Two lists - the first with the independent verbs and the second with any connectors
    """
    # Returns a list of the verb and connector tokens
    # Check for adverbial clauses, which will have the advmod in the clause
    clausal_verbs = [child for child in cls_sentence.root.children if child.dep_ == 'advcl']
    connectors = []
    keep_separate_clauses = False
    if len(clausal_verbs) > 0:
        connectors = [conn for conn in clausal_verbs[0].children if conn.dep_ in ('advmod', 'mark')]
        # Only keep the verbs and connectors under certain circumstances
        for conn in connectors:
            if conn.text.lower() in cause_connectors:
                keep_separate_clauses = True
    if not keep_separate_clauses:
        connectors = []
    # Also check for clausal complement, where we want the advmod (or mark) in the original/root verb clause
    new_verbs = [child for child in cls_sentence.root.children if child.dep_ == 'ccomp']
    if new_verbs:
        new_connectors = [conn for conn in cls_sentence.root.children if conn.dep_ in ('advmod', 'mark')]
        if new_connectors:
            keep_separate_clauses = False
            for new_conn in new_connectors:
                if new_conn.text.lower() in effect_connectors:
                    keep_separate_clauses = True
            if keep_separate_clauses:
                clausal_verbs.extend(new_verbs)
                connectors.extend(new_connectors)
    return clausal_verbs, connectors


def _remove_startswith(chunk: str, connector: str) -> str:
    """
    Returns first string with the second string removed from its start.

    :param chunk: String to be updated
    :param connector: String to be removed from the beginning of the chunk
    :return: Updated 'chunk' string
    """
    if chunk.startswith(f'{connector} '):
        chunk = chunk[len(connector) + 1:]
    elif chunk.startswith(f' {connector} '):
        chunk = chunk[len(connector) + 2:]
    return chunk


def _split_by_conjunctions(conj_sentence: Span) -> (list, str):
    """
    Split the clauses of a sentence into separate sentences, if they are connected by a coordinating
    conjunction (for, and, but, or, nor, yet, so). For example,"Mary and John walked to the store." would
    NOT be split, but "Mary biked to the market and John walked to the store." should be split.

    :param conj_sentence The sentence which is analyzed
    :return: An array of simpler sentence(s) (note that only the text of the sentences is
             returned, not the spacy tokens) and the coordinating conjunction. The latter is
             needed to process or/nor alternatives.
    """
    logging.info(f'Splitting the sentence, {conj_sentence.text}')
    conj_sents = []
    conj_verb = [child for child in conj_sentence.root.children if child.dep_ == 'conj']
    connectors = [conn for conn in conj_sentence.root.children if conn.dep_ == 'cc']
    if len(conj_verb) > 0:
        for chunk in get_chunks(conj_verb[0], connectors, conj_sentence, True):
            conj_sents.append(str(chunk))
    else:
        conj_sents = [conj_sentence.text]
    return conj_sents, ('' if not connectors else connectors[0].text)
