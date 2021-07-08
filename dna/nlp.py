import copy
import logging
import spacy
from spacy.matcher import DependencyMatcher
from spacy.tokens import Span, Token

from utilities import EMPTY_STRING, SPACE, NEW_LINE, add_to_dictionary_values, update_dictionary_count

nlp = spacy.load('en_core_web_trf')
nlp.add_pipe('sentencizer')
matcher = DependencyMatcher(nlp.vocab)

pronouns = ['she', 'her', 'herself', 'he', 'him', 'himself',
            'they', 'them', 'themselves', 'you', 'yourself', 'yourselves',
            'we',  'us', 'ourselves']
dna_stopwords = ['a', 'an', 'just', 'quite', 'really', 'the', 'very']
spacy_stopwords = nlp.Defaults.stop_words
spacy_stopwords.clear()

unwanted_tokens = (
    'ADV',    # adverb
    'PART',   # particle
    'DET',    # determiner
    'INTJ',   # interjection
    'SCONJ',  # subordinating conjunction
    'PUNCT',  # punctuation
    'SYM',    # symbol
    'X',      # other
)

# "born ... on ... in ..."
born_date_pattern = [
  # anchor token: born
  {
    'RIGHT_ID': 'born1',
    'RIGHT_ATTRS': {'ORTH': 'born'}
  },
  # subject should be 'I'
  {
    'LEFT_ID': 'born1',
    'REL_OP': '>',
    'RIGHT_ID': 'I_born1',
    'RIGHT_ATTRS': {'ORTH': 'I'}
  },
  # date follows "born"
  {
    'LEFT_ID': 'born1',
    'REL_OP': '>>',
    'RIGHT_ID': 'born_date',
    'RIGHT_ATTRS': {'ENT_TYPE': 'DATE'}
  }
]

born_place_pattern = [
  # anchor token: born
  {
    'RIGHT_ID': 'born2',
    'RIGHT_ATTRS': {'ORTH': 'born'}
  },
  # subject should be 'I'
  {
    'LEFT_ID': 'born2',
    'REL_OP': '>',
    'RIGHT_ID': 'I_born2',
    'RIGHT_ATTRS': {'ORTH': 'I'}
  },
  # place follows "born"
  {
    'LEFT_ID': 'born2',
    'REL_OP': '>>',
    'RIGHT_ID': 'born_place',
    'RIGHT_ATTRS': {'ENT_TYPE': {'IN': ['GPE', 'LOC']}}
  }
]

family_member_name_pattern = [
  # anchor token: family relation
  {
    'RIGHT_ID': 'family_member',
    'RIGHT_ATTRS': {'ORTH': {'IN': ['sister', 'brother', 'mother', 'father', 'cousin',
                                    'grandmother', 'grandfather', 'aunt', 'uncle']}}
  },
  # subject should be 'I'
  {
    'LEFT_ID': 'family_member',
    'REL_OP': '>',
    'RIGHT_ID': 'proper_name',
    'RIGHT_ATTRS': {'DEP': 'appos', 'POS': 'PROPN'}
  }
]

matcher.add("born_date", [born_date_pattern])
matcher.add("born_place", [born_place_pattern])
matcher.add("family_member_name", [family_member_name_pattern])


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
    noun and verb.

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
    Creates a spacy Doc from the input text and parses each of the sentences creating a
    dictionary holding the subject/verb/preposition/... details. Each of the sentence
    dictionaries are added to an array, which is returned.

    :param narr_text The narrative text
    :return An array of sentence dictionaries
    """
    doc = nlp(narr_text)
    sentences = []
    for sentence in doc.sents:
        if sentence.text.startswith(NEW_LINE):
            continue
        # Change conjunctions into new sentences
        for sent in split_by_conjunctions(sentence):
            nlp_sent = nlp(sent)
            # Determine the spans of individual nouns and noun chunks
            spans = list(nlp_sent.ents) + list(nlp_sent.noun_chunks)
            spans = spacy.util.filter_spans(spans)
            # Reset the sentence parse to maintain chunks
            with nlp_sent.retokenize() as retokenizer:
                [retokenizer.merge(span, attrs={'tag': span.root.tag,
                                                'dep': span.root.dep}) for span in spans]
            # Store info starting from the ROOT verb
            sentence_dict = dict()
            for token in nlp_sent:
                if token.dep_ == 'ROOT':
                    _process_verb(token, sentence_dict)
            sentences.append(sentence_dict)
    return sentences


def split_by_conjunctions(sentence: Span) -> list:
    """
    Split the clauses of a sentence into separate sentences, if warranted. For example,
    "Mary and John walked to the store." would not be split, but "Mary biked to the market
    and John walked to the store." would be split.

    :param sentence The sentence which is analyzed.
    :return: An array of simpler sentence(s) to be parsed. Only the text of the sentences
             is returned, not the spacy tokens.
    """
    logging.info(f'Splitting the sentence, {sentence.text}')
    orig_sents = [sentence.text]
    # Iterate until the sentences cannot be further decomposed/split
    while True:
        new_sents = []
        # Go through each sentence in the array
        for orig_sent in orig_sents:
            # Need to re-tokenize in order to get new root verbs and children
            chunk_doc = nlp(orig_sent)
            # There should only be 1 sentence in each 'chunk_doc'
            # For loop below turns the Doc sentence into a Span, allowing use of .root to get main verb
            intermed_sents = []
            for chunk_sent in chunk_doc.sents:
                if '; ' in chunk_sent.text:
                    sent_text = chunk_sent.text
                    semicolon_index = sent_text.index('; ')
                    new_sents = [f'{sent_text[:semicolon_index]}.', f'{sent_text[semicolon_index + 2:]}.']
                    break
                # First split by words such as 'and', 'but', 'or', ...
                conj_verb = [child for child in chunk_sent.root.children if child.dep_ == 'conj']
                connector = [conn for conn in chunk_sent.root.children if conn.dep_ == 'cc']
                if len(conj_verb) > 0:
                    for chunk in _get_chunks(conj_verb[0], connector, chunk_sent, True):
                        intermed_sents.append(chunk)
                else:
                    intermed_sents = [orig_sent]
                # Now check resulting sentences to further split by adverbial clauses and clausal complements
                # Only split if there is a subject-verb pair in the clause
                # Example: 'I went to the store where I met George.' ('where ...' is an adverbial clause)
                for intermed_sent in intermed_sents:
                    chunk_doc2 = nlp(intermed_sent)
                    for chunk_sent2 in chunk_doc2.sents:
                        advcl_verb = [child for child in chunk_sent2.root.children if child.dep_ == 'advcl']
                        if len(advcl_verb) > 0:
                            connector = [conn for conn in advcl_verb[0].children if conn.dep_ == 'advmod']
                        else:
                            connector = []
                        # Need to have both a clause and a connector/modifier for this logic
                        if len(advcl_verb) > 0 and len(connector) > 0:
                            for chunk in _get_chunks(advcl_verb[0], connector, chunk_sent2, False):
                                new_sents.append(chunk)
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
def _add_token_details(token: Token, dictionary: dict, key: str):
    """
    Simplify the token text, get the token's entity type (or define one if blank), and
    add the token details to the specified dictionary key.

    :param token Token from spacy parse
    :param dictionary Dictionary that the token details should be added to
    :param key Dictionary key where the details are added
    :return None (Specified dictionary is updated)
    """
    logging.info(f'Processing the token, {token.text}, for key, {key}, of type, {token.ent_type_}')
    ent_type = token.ent_type_
    if token.text == 'I':
        ent = 'I'
        ent_type = 'NARRATOR'
    elif token.text.lower() == 'you':
        ent = 'You'
        ent_type = 'AUDIENCE'
    elif 'verb' in key:
        ent = token.text
        ent_type = 'VERB'
    elif token.text.lower() in pronouns:
        ent = token.text
        ent_type = 'PERSON'
    else:
        # Simplify the entity text for nouns
        ent = SPACE.join(str(t.text) for t in nlp(token.text)
                         if (t.pos_ not in unwanted_tokens and t.text.lower() not in dna_stopwords))
        if ent_type == EMPTY_STRING:
            ent_type = 'NOUN'

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
        elif 'conj' in child.dep_:
            _add_token_details(child, dictionary, key)
        elif 'prep' in child.dep_:
            prep_dict = dict()
            # Lists of dictionaries have plural names while individual dictionary keys should not
            prep_dict[f'{key[0:-1] if key.endswith("s") else key}_prep_text'] = child.text
            for prep_child in child.children:
                if 'obj' in prep_child.dep_ or 'attr' in prep_child.dep_:
                    # Object/attr is part of the prepositional clause, so it adds to the current prep_dict
                    _process_prep_object(prep_child, prep_dict, (key[0:-1] if key.endswith("s") else key))
                    # Are there multiple objects (i.e., a conjunction)?
                    # TODO: Only gets 1 other conjunctive; Get others
                    for child_squared in prep_child.children:
                        if 'conj' == child_squared.dep_:
                            _process_prep_object(
                                child_squared, prep_dict, (key[0:-1] if key.endswith("s") else key))
            add_to_dictionary_values(ent_dict, f'{key[0:-1] if key.endswith("s") else key}_preps', prep_dict, dict)
    add_to_dictionary_values(dictionary, key, ent_dict, dict)
    return


def _get_chunks(verb: Token, connector: list, sentence: Span, is_conj: bool) -> list:
    """
    Given a conjunctive verb, a connector token relating that verb to the root verb
    (such as 'and', 'but', ...) and the sentence that contains these tokens, determine if
    the sentence can be separated into clauses. Also separate semi-colon-ed sentences
    into two.

    :param verb The token of the conjunctive verb
    :param connector Tokens of the connectors between the root and conjunctive verbs
                     (if is_conj is true) or adverb modifiers of the conjunctive verb
                     (if is_conj is false)
    :param sentence A Span representing the parsed sentence
    :param is_conj A boolean indicating whether the connector is related to terms such as
                   'and', 'but', 'or' or is related to an adverbial clause
    :return: A list of the text of the clauses of the sentence (split if indicated by the
             logic below) or just the original sentence returned
    """
    logging.info(f'Getting the clauses in {sentence.text}')
    chunks = []
    seen = set()
    # Is there a subject of the conjunctive verb?
    subj2 = [subj for subj in verb.children if 'subj' in subj.dep_]
    if len(subj2) == 1:
        # Yes ... Separate clauses
        # Get the tokens in sentence related to the conjunctive verb's subtree
        words = [ww for ww in verb.subtree if ww.pos_ != 'PUNCT']
        for word in words:
            seen.add(word)
        seen_chunk = SPACE.join([ww.text for ww in words])
        # Get the remaining tokens in the sentence
        unseen = [ww for ww in sentence if ww not in seen and ww.pos_ != 'PUNCT']
        unseen_chunk = SPACE.join([ww.text for ww in unseen])
        # Remove the connector words (to prevent sentences such as 'Mary biked to the market and')
        if is_conj:
            for conn in connector:
                unseen_chunk = unseen_chunk.replace(f' {conn.text}', EMPTY_STRING)
        else:
            for conn in connector:
                seen_chunk = seen_chunk.replace(f' {conn.text}', EMPTY_STRING)
                seen_chunk = seen_chunk.replace(conn.text, EMPTY_STRING)
        # Store the seen and unseen clauses as separate sentences
        chunks.append(unseen_chunk.strip() + '.')
        chunks.append(seen_chunk.strip() + '.')
    if len(chunks) > 0:
        return chunks
    else:
        return [sentence.text]


def _process_prep_object(token, dictionary, key):
    """
    When processing a token (in add_token_details), capture prepositions and their objects.

    :param token Token of the preposition
    :param dictionary Dictionary that the token details should be added to
    :param key Dictionary key where the details are added
    :return None (Specified dictionary is updated)
    """
    logging.info(f'Processing the preposition, {token.text}')
    prep_ent = SPACE.join(str(t.text) for t in nlp(token.text)
                          if (t.pos_ not in unwanted_tokens and not t.is_stop))
    prep_ent_type = token.ent_type_
    if prep_ent_type == EMPTY_STRING:
        prep_ent_type = 'NOUN'
    prep_ent_detail = dict()
    prep_ent_detail[f'{key[0:-1] if key.endswith("s") else key}_prep_object'] = prep_ent
    prep_ent_detail[f'{key[0:-1] if key.endswith("s") else key}_prep_object_type'] = prep_ent_type
    add_to_dictionary_values(dictionary, f'{key}_prep_objects', prep_ent_detail, dict)
    return


def _process_verb(token, dictionary):
    """
    When processing a token (that is a verb), capture its details. Note that all processing
    of a narrative is based on the sentences and their ROOT verbs.

    :param token Verb token from spacy parse
    :param dictionary Dictionary that the token details should be added to
    :return None (Specified dictionary is updated)
    """
    logging.info(f'Processing the verb, {token.text}')
    ent = token.text
    verb_dict = dict()
    verb_dict['verb_text'] = ent
    verb_dict['verb_lemma'] = token.lemma_
    for child in token.children:
        if 'aux' == child.dep_:     # Auxiliary clause of the verb
            _add_token_details(child, verb_dict, 'verb_aux')
        if 'advcl' == child.dep_:   # Adverbial clause of the verb
            _add_token_details(child, verb_dict, 'verb_advcl')
        elif 'xcomp' == child.dep_:  # Clausal complement of the verb
            _add_token_details(child, verb_dict, 'verb_xcomp')
        elif 'conj' == child.dep_:   # Another verb related via a coordinating conjunction
            _process_verb(child, dictionary)
        elif 'subj' in child.dep_:   # Subject of the verb
            _add_token_details(child, dictionary, 'subjects')
        elif 'obj' in child.dep_ or 'attr' in child.dep_:  # Object or attribute of the verb
            _add_token_details(child, verb_dict, 'objects')
        elif 'prep' in child.dep_:    # Preposition associated with the verb
            prep_dict = dict()
            prep_dict['prep_text'] = child.text
            for prep_dep in child.children:
                _add_token_details(prep_dep, prep_dict, 'prep_details')
            add_to_dictionary_values(verb_dict, 'preps', prep_dict, dict)
    add_to_dictionary_values(dictionary, 'verbs', verb_dict, dict)
    return
