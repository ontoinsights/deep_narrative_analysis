# Processing to split sentences if sub-clauses have both a subject and verb
# Needs the nlp Language model from nlp.py passed as a parameter into the main function, split_clauses

import re
from spacy.language import Language
from spacy.tokens import Span, Token
from typing import Union

from dna.utilities import later_connectors, empty_string, space

relative_clause_words = ['who', 'whose', 'whom', 'which', 'that', 'where', 'when', 'why']
conjunction_words = ['for', 'and', 'nor', 'but', 'or', 'yet', 'so']
special_marks = ['if', 'because', 'since']


def _chunk_quotations(text_str: str) -> list:
    """
    Given a sentence text that includes 'Quotation#', chunk that text into individual clauses for
    each Quotation reference and any remaining text.

    :param text_str: The text that contains at least one 'Quotation#' reference
    :return: A list of the text chunks, splitting each 'Quotation#' reference into its own chunk
             and including each intervening text as a chunk
    """
    quotation_refs = re.findall(r'Quotation[0-9]+', text_str)   # Really only care about the first ref
    chunks = []
    quote_index = text_str.index(quotation_refs[0])
    if quote_index > 0:
        chunk_text = text_str[0:quote_index].strip()
        chunks.append(chunk_text[0:-1] if chunk_text.endswith('.') else chunk_text)
        text_str = text_str[quote_index:]
    chunks.append(quotation_refs[0])
    text_str = text_str.replace(quotation_refs[0], empty_string)
    if not text_str or text_str == space:
        return chunks
    text_str = text_str.strip()
    if 'Quotation' not in text_str:
        chunks.append(text_str)
        return chunks
    chunks.extend(_chunk_quotations(text_str))   # Recursively deal with the rest of the sentence
    return chunks


def _get_chunks(verb: Token, connector: Union[Token, None], chunk_sentence: Span, processing_type: str,
                subjs: Union[list, None]) -> list:
    """
    Given (1) a conjunctive or clausal phrase for a verb, (2) an optional connector token relating the
    phrase to the verb (such as 'and', 'but', ...) and (3) the sentence that contains these tokens, determine
    if the sentence can be separated into clauses. The sentence is separated if the clause has its own
    subject and verb.

    Note that this algorithm (seen/unseen_chunk) is taken from the StackOverflow response at
    https://stackoverflow.com/questions/65227103/clause-extraction-long-sentence-segmentation-in-python.

    :param verb: The token of the verb with the conjunctive or clausal phrase
    :param connector: Token of the connector between the root and conjunctive or clausal verb,
                      or None (which may occur if this is a clausal complement - e.g., "He said
                      Joe is ill.")
    :param chunk_sentence: A Span representing the parsed sentence
    :param processing_type: A string indicating whether this is for a conjunctive verb ('conj'),
                            adverbial clause verb ('advcl'), clausal complement ('comp') or
                            relative clause ('relcl')
    :param subjs: An array holding the tokens of any subjects or expletives (it is only needed when
                  processing conjunctions
    :return: A list of the text of the clauses of the sentence (split if indicated by the
             logic below) or just the original sentence returned
    """
    if subjs is None:
        subjs = []
    chunks = []
    subj_texts = []
    # Does the other clause's verb have a subject ('nsubj'/'nsubjpass'/'expl' (e.g., 'there')) in the dep parse?
    subj2 = [subj for subj in verb.children if ('subj' in subj.dep_ or subj.dep_ == 'expl') and
             ((subj.pos_ == 'PRON' and subj.morph.get('PronType') != ['Dem']) or subj.pos_ != 'PRON')]
    if not subj2 and (processing_type in ('conj', 'advcl')):
        # Attach the root verb's subject(s) to the other verb
        for subj in subjs:
            for subtree in subj.subtree:
                subj_texts.append(subtree.text)
    if len(subj2) or subj_texts:
        # Yes ... Separate clauses
        # Get the tokens in sentence related to the 'other' verb's subtree
        seen = [ww for ww in verb.subtree if (
                (ww.pos_ == 'PUNCT' and ww.lemma_ == '?') or
                not ((ww.dep_ == 'dobj' and ww.pos_ == 'PRON') or ww.pos_ == 'PUNCT'))]
        seen_chunk = ' '.join([ww.text for ww in seen]).strip()
        seen_chunk = seen_chunk.replace(' .', empty_string) if seen_chunk.endswith(' .') else seen_chunk
        unseen = [ww for ww in chunk_sentence if ww not in seen and
                  ((ww.pos_ == 'PUNCT' and ww.lemma_ == '?') or ww.pos_ != 'PUNCT')]
        unseen_chunk = ' '.join([ww.text for ww in unseen]).strip()
        unseen_chunk = unseen_chunk.replace(' .', empty_string) if unseen_chunk.endswith(' .') else unseen_chunk
        if connector:
            seen_chunk = _remove_connector_text(seen_chunk, connector.text)
            unseen_chunk = _remove_connector_text(unseen_chunk, connector.text)
            if processing_type == 'conj':
                # Store the unseen and seen clauses in that order
                chunks.extend(
                    _store_chunks_in_order(unseen_chunk,
                                           f"{' '.join(subj_texts)} {seen_chunk}" if subj_texts else seen_chunk))
            elif processing_type == 'advcl':
                if connector.text.lower() in later_connectors:   # Store unseen_chunk first
                    if 'eventually' in unseen_chunk.lower() or 'afterwards' in unseen_chunk.lower() or \
                            'finally' in unseen_chunk.lower():    # Keywords override ordering
                        chunks.extend(
                            _store_chunks_in_order(
                                f"{' '.join(subj_texts)} {seen_chunk}" if subj_texts else seen_chunk, unseen_chunk))
                    else:
                        chunks.extend(
                            _store_chunks_in_order(
                                unseen_chunk, f"{' '.join(subj_texts)} {seen_chunk}" if subj_texts else seen_chunk))
                else:     # Store seen_chunk first
                    if connector.text.lower() in special_marks:
                        seen_chunk += f'$&{connector.text.lower()}'
                    chunks.extend(
                        _store_chunks_in_order(
                            f"{' '.join(subj_texts)} {seen_chunk}" if subj_texts else seen_chunk, unseen_chunk))
        else:
            chunks.extend(
                _store_chunks_in_order(
                    unseen_chunk, f"{' '.join(subj_texts)} {seen_chunk}" if subj_texts else seen_chunk))
    if len(chunks) > 0:
        return chunks
    else:
        return [chunk_sentence.text[0:-1] if chunk_sentence.text.endswith('.') else chunk_sentence.text]


def _remove_connector_text(chunk_text: str, connector_text: str) -> str:
    """
    Returns first string with the second string removed from its start or end.

    :param chunk_text: String to be updated
    :param connector_text: String to be removed from the beginning or end of the chunk
    :return: Updated 'chunk' string
    """
    if chunk_text.startswith(f'{connector_text} ') or chunk_text.startswith(f'{connector_text.title()} '):
        chunk_text = chunk_text[len(connector_text) + 1:]
    elif chunk_text.startswith(f' {connector_text} '):
        chunk_text = chunk_text[len(connector_text) + 2:]
    elif chunk_text.endswith(f' {connector_text} '):
        chunk_text = chunk_text[0:(len(connector_text) + 2) * -1]
    elif chunk_text.endswith(f' {connector_text}'):
        chunk_text = chunk_text[0:(len(connector_text) + 1) * -1]
    return chunk_text


def _split_advcl_clauses(sentence: str, nlp: Language) -> list:
    """
    Split the adverbial clauses of a sentence into separate sentences, if the clauses have their
    own subject and verb.

    :param sentence: The sentence which is analyzed
    :param nlp: A spacy Language model
    :return: An array of simpler sentence(s) (note that only the text of the sentences is
             returned, not the spacy tokens) or the original sentence if there is no advcl verb
             or if the connector is not one of the cause_ or effect_connectors
    """
    sent_span = next(nlp(sentence).sents)    # There should only be 1 sentence for each function call
    subjs = [child for child in sent_span.root.children if 'subj' in child.dep_]
    advcl_verbs = [child for child in sent_span.root.children if child.dep_ == 'advcl']
    new_chunks = []
    for advcl_verb in advcl_verbs:
        connectors = [conn for conn in advcl_verb.children if conn.dep_ in ('advmod', 'mark')]
        # Process the verb and the first connector (there should only be 1, but there may be 0)
        if connectors:
            chunks = _get_chunks(advcl_verb, connectors[0], sent_span, 'advcl', subjs)
        else:
            chunks = _get_chunks(advcl_verb, None, sent_span, 'advcl', subjs)
        revised_chunks = []
        if connectors:
            # Remove the connector from the middle of the text of the sentence
            revised_chunks.extend([chunk.replace(f' {connectors[0]} ', space) for chunk in chunks])
        else:
            revised_chunks = chunks
        new_chunks.extend(revised_chunks)
    return new_chunks if new_chunks else [sentence]


def _split_by_conjunctions(sentence: str, nlp: Language) -> list:
    """
    Split the clauses of a sentence into separate sentences, if the verbs are connected by a coordinating
    conjunction (for, and, but, or, nor, yet, so). For example,"Mary and John walked to the store." would
    NOT be split, but "Mary biked to the market and John walked to the store." should be split.

    :param sentence: The sentence which is analyzed
    :param nlp: A spacy Language model
    :return: An array of simpler sentence(s) (note that only the text of the sentences is
             returned, not the spacy tokens) or the original sentence if there are no
             conjunctive verbs
    """
    sent_span = next(nlp(sentence).sents)    # There should only be 1 sentence for each function call
    new_sents = []
    conj_verbs = [child for child in sent_span.root.children if child.dep_ == 'conj']
    connectors = [conn for conn in sent_span.root.children if conn.dep_ == 'cc']
    if conj_verbs and len(conj_verbs) == len(connectors):
        subjects = [child for child in sent_span.root.children if 'subj' in child.dep_]
        expls = [child for child in sent_span.root.children if child.dep_ == 'expl']
        if expls:
            subjects.extend(expls)
        # Process the first 'chunk' and then return - Subsequent iterations will process the complete text
        chunks = _get_chunks(conj_verbs[0], connectors[0], sent_span, 'conj', subjects)
        if len(chunks) > 1:
            for chunk in chunks:
                new_sents.extend(_split_by_conjunctions(chunk, nlp))
            return new_sents
        else:
            return [chunks[0]]
    else:
        return [sentence[0:-1] if sentence.endswith('.') else sentence]


def _split_complement_clauses(sentence: str, nlp: Language) -> list:
    """
    Split the clausal complements of a sentence into separate sentences, if the clauses have their
    own subject and verb.

    :param sentence: The sentence which is analyzed
    :param nlp: A spacy Language model
    :return: An array of simpler sentence(s) (note that only the text of the sentences is
             returned, not the spacy tokens) or the original sentence if there is no ccomp verb
    """
    sent_span = next(nlp(sentence).sents)    # There should only be 1 sentence for each function call
    comp_verbs = [child for child in sent_span.root.children if child.dep_ == 'ccomp']
    for comp_verb in comp_verbs:
        connectors = [conn for conn in comp_verb.children if conn.dep_ in ('advmod', 'mark')]
        # Process the verb and the first connector (there may not be any)
        if connectors:
            return _get_chunks(comp_verb, connectors[0], sent_span, 'comp', None)
        else:
            return _get_chunks(comp_verb, None, sent_span, 'comp', None)
    return [sentence]


def _split_relcl_clauses(clause: str, nlp: Language) -> list:
    """
    Split the relative clauses of a sentence into separate sentences, if the clauses have their
    own subject and verb.

    :param clause: The sentence which is analyzed
    :param nlp: A spacy Language model
    :return: An array of simpler sentence(s) (note that only the text of the sentences is
             returned, not the spacy tokens) or the original sentence if there is no relcl verb
    """
    clause_span = next(nlp(clause).sents)    # There should only be 1 sentence for each function call
    new_clauses = []
    relcl_dict = dict()
    for token in clause_span:
        if 'subj' in token.dep_ or 'obj' in token.dep_:
            relcls = [child for child in token.children if child.dep_ == 'relcl' and child.pos_ in ('VERB', 'AUX')]
            if relcls:
                relcl_dict[token] = relcls
    for noun_token, relcls in relcl_dict.items():
        for relcl in relcls:
            noun_details = [ww.text for ww in noun_token.subtree]
            noun_text = ' '.join(noun_details)
            seen = [ww for ww in relcl.subtree]
            seen_chunk = ' '.join([ww.text for ww in seen])
            unseen = [ww for ww in clause_span if ww not in seen and
                      ((ww.pos_ == 'PUNCT' and ww.lemma_ == '?') or ww.pos_ != 'PUNCT')]
            unseen_chunk = ' '.join([ww.text for ww in unseen])
            # Need to remove the relcl subtree from the noun's subtree
            noun_text = noun_text.replace(seen_chunk, empty_string).strip()
            # Relcl may have a relative pronoun or adverb (e.g., 'which Mary bought', 'Arizona where Cheney lost' -
            #   which and where are the relative pronoun and adverb, respectively) that should be removed
            # Also need to add the relcl noun text back into the seen chunk (the relcl subtree)
            relcl_objs = [ww for ww in relcl.subtree if ww.dep_ == 'dobj' and ww.text in relative_clause_words]
            relcl_subjs = [ww for ww in relcl.subtree if 'subj' in ww.dep_ and ww.text in relative_clause_words]
            if relcl_subjs:
                seen_chunk = noun_text + space + seen_chunk.replace(f'{relcl_subjs[0].text}', empty_string).strip()
            elif relcl_objs:
                seen_chunk = seen_chunk.replace(f'{relcl_objs[0].text}', empty_string).strip() + space + noun_text
            else:
                seen_chunk = seen_chunk.strip() + space + noun_text
            # Does the 'seen' chunk (the relcl) have an advcl?
            adv_clauses = _split_advcl_clauses(seen_chunk, nlp)
            split_adv_clauses = []
            for adv_sent in adv_clauses:  # Do the advcls have conjunctions?
                comp_clauses = _split_complement_clauses(adv_sent, nlp)
                for comp_clause in comp_clauses:
                    split_adv_clauses.extend(_split_by_conjunctions(comp_clause, nlp))
            # Reassemble all the sentences
            new_clauses.extend(split_adv_clauses)
            new_clauses.append(unseen_chunk)
    return new_clauses if new_clauses else [clause]


def _store_chunks_in_order(chunk1: str, chunk2: str) -> list:
    """
    Save two strings in an array where chunk1 is first. Also, this method removes any
    ending periods.

    :param chunk1: The first string
    :param chunk2: The second string
    :return: An array consisting of the two strings
    """
    return [chunk1[0:-1] if chunk1.endswith('.') else chunk1, chunk2[0:-1] if chunk2.endswith('.') else chunk2]


def split_clauses(sent_text: str, nlp: Language) -> list:
    """
    Perform splitting of sentences by (1) finding the root verb, (2) working from its conjunctions (conj),
    clausal complements (ccomp) and adverbial clauses (advcl), (3) iterating through/splitting these clauses
    if they include a subject/object and verb,and (4) checking the final clauses if their subject/object
    contains a relative clause with a subject and verb.

    :param sent_text: The sentence to be split (as a string)
    :param nlp: A spaCy Language model
    :return: A list of new sentences (text only) created from the splits
    """
    initial_sents = []
    if 'Quotation' in sent_text:
        initial_sents.extend(_chunk_quotations(sent_text))
    else:
        initial_sents.append(sent_text)
    final_with_conn_words = []
    for initial_sent in initial_sents:
        if initial_sent.startswith('Quotation'):
            final_with_conn_words.append(initial_sent)
            continue
        new_sents = _split_by_conjunctions(initial_sent, nlp)
        split_sents = []
        # Split by advcl IF these have their own subject/verb
        # Example: 'When I went to the store, I met George.' ('when ...' is an adverbial clause)
        for sent in new_sents:
            adv_sents = _split_advcl_clauses(sent, nlp)
            # Split by ccomp IF these have their own subject/verb
            # Example: 'He said Joe is ill.' ('Joe is ill' is a clausal complement)
            for adv_sent in adv_sents:
                comp_sents = _split_complement_clauses(adv_sent, nlp)
                for comp_sent in comp_sents:
                    split_sents.extend(_split_by_conjunctions(comp_sent, nlp))
        # Check relcl
        split_sents2 = []
        for sent in split_sents:
            split_sents2.extend(_split_relcl_clauses(sent, nlp))
        # Check for advcls that are not directly associated with the root verb but still have a subject/object and verb
        for sent in split_sents2:
            sent_span = next(nlp(sent).sents)
            advcl_verbs = []
            for token in sent_span:
                advcl_verbs.extend([child for child in token.children if child.dep_ == 'advcl'])
            new_chunks = []
            for advcl_verb in advcl_verbs:   # There are some advcls remaining that are not associated w/ the root verb
                connectors = [conn for conn in advcl_verb.children if conn.dep_ in ('advmod', 'mark')]
                # Process the verb and the first connector (there should only be 1)
                if connectors:
                    connector = connectors[0]
                    chunks = _get_chunks(advcl_verb, connector, sent_span, 'advcl', None)
                    revised_chunks = []
                    for chunk in chunks:
                        # Remove the connector from the middle of the text of the sentence
                        revised_chunks.append(chunk.replace(f' {connector} ', space))
                    new_chunks.extend(revised_chunks)
            final_with_conn_words.extend(new_chunks if new_chunks else [sent])
    # Chunks may still have beginning or trailing 'mark' words (such as 'that' in 'she claimed that')
    final_chunks = []
    for clause in final_with_conn_words:
        # Relative and connector words may be present at the beginning or end of the clauses, and should be removed
        # TODO: Is the ordering (relcl to conj) correct? Should it be recursive?
        for word in relative_clause_words:
            clause = _remove_connector_text(clause, word)
        for word in conjunction_words:
            clause = _remove_connector_text(clause, word)
        # May still have "special mark"s that need to be addressed in the semantics
        for word in special_marks:
            revised_clause = _remove_connector_text(clause, word)
            if clause != revised_clause:
                clause = f'{revised_clause}$&{word}'
        final_chunks.append(clause)
    return final_chunks
