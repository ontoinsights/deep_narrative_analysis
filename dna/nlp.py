import copy
import logging
import spacy
from spacy.matcher import DependencyMatcher
from spacy.tokens import Span, Token

from nlp_graph import extract_graph_details
from nlp_patterns import born_date_pattern, born_place_pattern, family_member_name_pattern
from utilities import NEW_LINE, update_dictionary_count

nlp = spacy.load('en_core_web_trf')
nlp.add_pipe('sentencizer')
matcher = DependencyMatcher(nlp.vocab)

spacy_stopwords = nlp.Defaults.stop_words
spacy_stopwords.clear()

matcher.add("born_date", [born_date_pattern])
matcher.add("born_place", [born_place_pattern])
matcher.add("family_member_name", [family_member_name_pattern])

# Words that introduce a 'causal' clause, where the main clause is the effect
cause_connectors = ['when', 'because', 'since', 'as']
# Words that introduce a 'causal' effect in the main clause, where the other clause is the cause
effect_connectors = ['so', 'therefore ', 'consequently ']


def get_birth_family_details(narrative: str) -> (list, list, dict):
    """
    Use spaCy Dependency Parsing and rules-based matching to get the birth date and place details,
    and family member names from a narrative.

    :param narrative: String holding the narrative
    :return: Two lists where the first contains the tokens related to date and the second
             contains the tokens related to location, and a dictionary containing the names
             of family members and their relationship to the narrator/subject
    """
    logging.info('Getting birth and family data from narrative')
    # Analyze the text using spaCy and get matches to the 'born' and 'member' rules
    doc = nlp(narrative[:1000])
    matches = matcher(doc)
    # Get born on and born in details from the matches
    born_on_date = set()
    born_in_place = set()
    family_dict = dict()
    # Each token_id corresponds to one pattern dict
    for match in matches:
        match_id, token_ids = match   # Indicates which pattern is matched and the specific tokens
        # Get the string representation
        string_id = nlp.vocab.strings[match_id]
        if string_id == 'born_date':
            born_on_date.add(doc[token_ids[2]].text)
        elif string_id == 'born_place':
            born_in_place.add(doc[token_ids[2]].text)
        elif string_id == 'family_member_name':
            family_dict[doc[token_ids[0]].text] = doc[token_ids[1]].text
    # Verify that dates actually have a year
    found_year = any([value for value in born_on_date if (value.isnumeric() and int(value) > 1000)])
    if not found_year:
        born_on_date = set()
    return list(born_on_date), list(born_in_place), family_dict


def get_nouns_verbs(sentences: str) -> (dict, dict):
    """
    Parses all the sentences in the input parameter to return counts of each distinct
    nouns and verbs.

    :param sentences: String with the text of one or more sentences
    :return: Two dictionaries of the counts of the noun/verb lemmas
             The noun dictionary is returned first
    """
    logging.info('Getting the nouns and verbs from a set of narratives')
    noun_dict = dict()
    verb_dict = dict()
    doc = nlp(sentences)
    for sentence in doc.sents:
        for token in sentence:
            if token.pos_ in ('NOUN', 'PROPN'):
                update_dictionary_count(noun_dict, token.lemma_.lower())
            if token.pos_ == 'VERB':
                update_dictionary_count(verb_dict, token.lemma_.lower())
    sorted_nouns = dict(sorted(noun_dict.items(), key=lambda item: item[1], reverse=True))
    sorted_verbs = dict(sorted(verb_dict.items(), key=lambda item: item[1], reverse=True))
    return sorted_nouns, sorted_verbs


def parse_narrative(narr_text: str) -> list:
    """
    Creates a spacy Doc from the input text, splits sentences by conjunctions into clauses with
    their own subjects/verbs, and then parses each of the resulting sentences to create a
    dictionary holding the subject/verb/preposition/... details. Each of the sentence
    dictionaries are added to an array, which is returned.

    :param narr_text: The narrative text
    :return: An array of dictionaries holding the details of each sentence (after splitting)
    """
    doc = nlp(narr_text)
    split_sentences = []
    sentence_dicts = []
    # Split sentences by conjunctions
    for sentence in doc.sents:
        if sentence.text.startswith(NEW_LINE):
            continue
        # Change conjunctions into new sentences
        for sent in split_clauses(sentence):
            sent_nlp = nlp(sent)
            # Determine the spans of individual nouns and noun chunks
            spans = list(sent_nlp.ents) + list(sent_nlp.noun_chunks)
            spans = spacy.util.filter_spans(spans)
            # Reset the sentence parse to maintain chunks
            with sent_nlp.retokenize() as retokenizer:
                [retokenizer.merge(span, attrs={'tag': span.root.tag,
                                                'dep': span.root.dep}) for span in spans]
            # Store new sentence details
            split_sentences.append(sent_nlp)
    # Get the details of each sentence
    for sentence in split_sentences:
        extract_graph_details(sentence, sentence_dicts, nlp)
    return sentence_dicts


# Functions internal to the module, but accessible to testing
def check_subject_in_clause(cls_sentence: Span) -> (list, list):
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


def get_chunks(verb: Token, connector: list, chunk_sentence: Span, is_conj: bool) -> list:
    """
    Given a conjunctive verb, a connector token relating that verb to the root verb
    (such as 'and', 'but', ...) and the sentence that contains these tokens, determine if
    the sentence can be separated into clauses. Also separate semi-colon-ed sentences
    into two.

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
        seen_first = False
        for conn in connector:
            if is_conj:
                # Remove the connector words (to prevent cycles and sentences such as 'Mary biked to the market and')
                unseen_chunk = unseen_chunk.replace(f' {conn.text} ', ' ').replace(f' {conn.text}.', '.')
            else:
                # Connector in the seen words; Should seen words be first because they are a
                # cause related to an effect?
                if not seen_first and conn.text in seen_chunk and conn.text in cause_connectors:
                    seen_first = True
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
        if seen_first:
            chunks.append(seen_chunk)
            chunks.append(unseen_chunk)
        else:
            chunks.append(unseen_chunk)
            chunks.append(seen_chunk)
    if len(chunks) > 0:
        return chunks
    else:
        return [chunk_sentence.text]


def split_clauses(sentence: Span) -> list:
    """
    Perform splitting of sentences first by splitting by coordinating conjunctions (calling the function,
    split_by_conjunctions) and second by adverbial clauses and clausal complements.

    :param sentence: The sentence/Span to be split
    :return: A list of new sentences/Spans created from the split
    """
    orig_sents = [sentence.text]
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
            # TODO: Deal with 'or', 'nor' as the splitting word below (e.g., as an alternative)
            for chunk_sent in nlp(orig_sent).sents:
                # nlp(orig_sent) creates a new Document to allow .sents processing of ROOT verbs
                intermed_sents, splitting_word = _split_by_conjunctions(chunk_sent)
                # Now check resulting sentences to further split by adverbial clauses and clausal complements
                # Only split if there is a subject for a related verb
                # Example: 'When I went to the store, I met George.' ('when ...' is an adverbial modifier)
                for intermed_sent in intermed_sents:
                    for chunk_sent2 in nlp(intermed_sent).sents:
                        # nlp(intermed_sent) 're-tokenizes' in order to create a new Document, as above
                        clausal_verbs, connectors = check_subject_in_clause(chunk_sent2)
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
    :return: An array of simpler sentence(s) to be parsed and the text of the connecting token
             (note that only the text of the sentences is returned, not the spacy tokens)
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
