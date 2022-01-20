# Processing to split sentences if sub-clauses have both a subject and verb
# Needs the nlp Language model from nlp.py passed as a parameter into the main function, split_clauses
# Called by nlp.py

from typing import Union

from spacy.language import Language
from spacy.tokens import Span, Token

from utilities import cause_connectors, effect_connectors


def get_chunks(verb: Token, connector: Union[Token, None], chunk_sentence: Span, processing_type: str) -> list:
    """
    Given a conjunctive or clausal verb, an optional connector token relating that verb to the root
    verb (such as 'and', 'but', ...) and the sentence that contains these tokens, determine if
    the sentence can be separated into clauses. The sentence is separated if the clause has its own
    subject and verb.

    :param verb: The token of the conjunctive or clausal verb
    :param connector: Token of the connector between the root and conjunctive or clausal verb,
                      or None (which may occur if this is a clausal complement - e.g., "He said
                      Joe is ill.")
    :param chunk_sentence: A Span representing the parsed sentence
    :param processing_type: A string indicating whether this is for a conjunctive verb ('conj'),
                            adverbial clause verb ('advcl') or a clausal complement ('comp')

    :returns: A list of the text of the clauses of the sentence (split if indicated by the
             logic below) or just the original sentence returned
    """
    chunks = []
    # Is there a subject of the other clause's verb? That is required to split the sentence
    # A subject is identified in a dependency parse as an 'nsubj', 'nsubjpass' or 'expl' (e.g., the word 'there')
    subj2 = [subj for subj in verb.children if ('subj' in subj.dep_ or subj.dep_ == 'expl')]
    if len(subj2):
        # Yes ... Separate clauses
        # Get the tokens in sentence related to the 'other' verb's subtree
        seen = [ww for ww in verb.subtree if ww.pos_ != 'PUNCT']
        seen_chunk = ' '.join([ww.text for ww in seen]).strip() + '.'
        unseen = [ww for ww in chunk_sentence if ww not in seen and ww.pos_ != 'PUNCT']
        unseen_chunk = ' '.join([ww.text for ww in unseen]).strip() + '.'
        if connector:
            if processing_type == 'conj':
                # Remove the connector words (to prevent cycles and sentences such as 'Mary biked to the market and.')
                # The connector is always associated with the 'unseen' chunk
                unseen_chunk = unseen_chunk.replace(f' {connector.text} ', ' ').replace(f' {connector.text}.', '.')
                # Store the unseen and seen clauses in that order
                chunks.extend(_store_chunks_in_order(seen_chunk, unseen_chunk, False))
            else:
                # Remove the connector word (to prevent cycles)
                # It may be in either the seen or unseen chunks
                seen_chunk = _remove_startswith(seen_chunk, connector.text)
                seen_chunk = seen_chunk.replace(f' {connector.text} ', ' ').replace(f' {connector.text}.', '.')
                unseen_chunk = _remove_startswith(unseen_chunk, connector.text)
                unseen_chunk = unseen_chunk.replace(f' {connector.text} ', ' ').replace(f' {connector.text}.', '.')
                if processing_type == 'advcl':
                    if connector.text.lower() in cause_connectors:
                        chunks.extend(_store_chunks_in_order(seen_chunk, unseen_chunk, True))  # Store the clauses
                    elif connector.text.lower() in effect_connectors:
                        chunks.extend(_store_chunks_in_order(seen_chunk, unseen_chunk, False))  # Store the clauses
                else:
                    chunks.extend(_store_chunks_in_order(seen_chunk, unseen_chunk, False))  # Store the clauses
        else:
            chunks.extend(_store_chunks_in_order(seen_chunk, unseen_chunk, False))  # Store the clauses
    if len(chunks) > 0:
        return chunks
    else:
        return [chunk_sentence.text]


def split_clauses(sent_text: str, nlp: Language) -> list:
    """
    Perform splitting of sentences first by splitting by coordinating conjunctions (calling the function,
    split_by_conjunctions), second splitting by adverbial clauses and then by clausal complements. Lastly,
    check for conjunctions within the adverbial or complement clauses.

    :param sent_text: The sentence to be split (as a string)
    :param nlp: A spaCy Language model
    :returns: A list of new sentences (text only) created from the splits
    """
    new_sents = _split_by_conjunctions(sent_text, nlp)
    split_sents = []
    for sent in new_sents:
        # Split by advcl IF these have their own subject/verb
        # Example: 'When I went to the store, I met George.' ('when ...' is an adverbial clause)
        adv_sents = _split_advcl_clauses(sent, nlp)
        # Split by ccomp IF these hae their own subject/verb
        # Example: 'He said Joe is ill.' (a clausal complement)
        for adv_sent in adv_sents:
            comp_sents = _split_complement_clauses(adv_sent, nlp)
            for comp_sent in comp_sents:
                split_sents.extend(_split_by_conjunctions(comp_sent, nlp))
    return split_sents


# Functions internal to the module
def _remove_startswith(chunk: str, connector: str) -> str:
    """
    Returns first string with the second string removed from its start.

    :param chunk: String to be updated
    :param connector: String to be removed from the beginning of the chunk
    :returns: Updated 'chunk' string
    """
    if chunk.startswith(f'{connector} '):
        chunk = chunk[len(connector) + 1:]
    elif chunk.startswith(f' {connector} '):
        chunk = chunk[len(connector) + 2:]
    return chunk


def _split_advcl_clauses(sentence: str, nlp: Language) -> list:
    """
    Split the adverbial clauses of a sentence into separate sentences, if the clauses have their
    own subject and verb.

    :param sentence The sentence which is analyzed
    :returns: An array of simpler sentence(s) (note that only the text of the sentences is
             returned, not the spacy tokens) or the original sentence if there is no advcl verb
             or if the verb is not one of the cause_ or effect_connectors
    """
    sent_span = next(nlp(sentence).sents)    # There should only be 1 sentence for each function call
    advcl_verbs = [child for child in sent_span.root.children if child.dep_ == 'advcl']
    for advcl_verb in advcl_verbs:
        connectors = [conn for conn in advcl_verb.children if conn.dep_ in ('advmod', 'mark')]
        # Process the verb and the first connector (there should only be 1)
        if connectors:
            chunks = get_chunks(advcl_verb, connectors[0], sent_span, 'advcl')
            return chunks
    return [sentence]


def _split_by_conjunctions(sentence: str, nlp: Language) -> list:
    """
    Split the clauses of a sentence into separate sentences, if they are connected by a coordinating
    conjunction (for, and, but, or, nor, yet, so). For example,"Mary and John walked to the store." would
    NOT be split, but "Mary biked to the market and John walked to the store." should be split.

    :param sentence The sentence which is analyzed
    :returns: An array of simpler sentence(s) (note that only the text of the sentences is
             returned, not the spacy tokens) or the original sentence if there are no
             conjunctive verbs
    """
    sent_span = next(nlp(sentence).sents)    # There should only be 1 sentence for each function call
    new_sents = []
    conj_verbs = [child for child in sent_span.root.children if child.dep_ == 'conj']
    connectors = [conn for conn in sent_span.root.children if conn.dep_ == 'cc']
    if conj_verbs and len(conj_verbs) == len(connectors):
        # Process the first 'chunk' and then return - Subsequent iterations will process the complete text
        chunks = get_chunks(conj_verbs[0], connectors[0], sent_span, 'conj')
        if len(chunks) > 1:
            for chunk in chunks:
                new_sents.extend(_split_by_conjunctions(chunk, nlp))
        else:
            return [chunks[0]]
    else:
        return [sentence]
    return new_sents


def _split_complement_clauses(sentence: str, nlp: Language) -> list:
    """
    Split the clausal complements of a sentence into separate sentences, if the clauses have their
    own subject and verb.

    :param sentence The sentence which is analyzed
    :returns: An array of simpler sentence(s) (note that only the text of the sentences is
             returned, not the spacy tokens) or the original sentence if there is no ccomp verb
    """
    sent_span = next(nlp(sentence).sents)    # There should only be 1 sentence for each function call
    comp_verbs = [child for child in sent_span.root.children if child.dep_ == 'ccomp']
    for comp_verb in comp_verbs:
        connectors = [conn for conn in comp_verb.children if conn.dep_ in ('advmod', 'mark')]
        # Process the verb and the first connector (there may not be any)
        if connectors:
            chunks = get_chunks(comp_verb, connectors[0], sent_span, 'comp')
        else:
            chunks = get_chunks(comp_verb, None, sent_span, 'comp')
        return chunks
    else:
        return [sentence]


def _store_chunks_in_order(seen: str, unseen: str, seen_first: bool) -> list:
    """
    Save two strings (a 'seen' and an 'unseen' string) in an array where the 'seen' string is
    the first element if the seen_first parameter is True.

    :param seen: The 'seen' string
    :param unseen: The 'unseen' string
    :returns: An array where either the seen or unseen strings are the first/second element
             depending on the value of the seen_first parameter.
    """
    if seen_first:
        return [seen, unseen]
    else:
        return [unseen, seen]
