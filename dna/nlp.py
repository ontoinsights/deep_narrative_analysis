# Entry points for all spaCy processing and creation of the KG from the text parse
# Includes functions for head words, named entities, relative time, etc.
# Key function: parse_narratives
# Where a narrative's sentences are parsed into dictionary elements with the following form:
#    'text': 'narrative_text', 'sentence_offset': #,
#    'AGENTS': ['agent1', 'agent2', ...], 'LOCS': ['location1', ...],
#    'TIMES': ['dates_or_times1', ...], 'EVENTS': ['event1', ...],
#    'chunks': [chunk1, chunk2, ...]
# Note that 'punct': '?' may also be included above
# Where each chunk is a dictionary with the form:
#    'chunk_text': 'chunk_text', 'verb_processing': 'xcomp_or_prt_details',
#    'verbs': [{'verb_text': 'verb_text', 'verb_lemma': 'verb_lemma', 'tense': 'tense_such_as_Past',
#               'subject_text': 'subject_text', 'subject_type': 'type_such_as_SINGNOUN',
#               'objects': [{'object_text': 'verb_object_text', 'object_type': 'type_eg_NOUN'}]
#               'preps': [{'prep_text': 'preposition_text',
#                          'prep_details': [{'detail_text': 'preposition_object', 'detail_type': 'type_eg_SINGGPE'}]}]
# There may be more than 1 verb when there is a root verb + an xcomp
# Sentence dictionaries are evaluated to produce the narrative's Turtle output
#    (parse_narratives -> create_narrative_turtle's create_graph)

import logging
import re
import spacy
from spacy.language import Language
from spacy.matcher import DependencyMatcher
from spacy.tokens import Doc
from spacy.tokenizer import Tokenizer
from spacy.lang.char_classes import ALPHA, ALPHA_LOWER, ALPHA_UPPER, CONCAT_QUOTES, LIST_ELLIPSES, LIST_ICONS
from spacy.util import compile_infix_regex
from word2number import w2n

from dna.nlp_patterns import member_name_pattern, name_member_pattern, members_names_pattern, names_members_pattern, \
    member_verb_name_pattern, members_verb_names_pattern, name_verb_member_pattern, names_verb_members_pattern
from dna.nlp_sentence_dictionary import extract_chunk_details
from dna.nlp_split_sentences import split_clauses
from dna.utilities_and_language_specific import add_to_dictionary_values, empty_string, ner_types, \
    replacement_words, space


# noinspection PyArgumentList
def custom_tokenizer(nlp_lang: Language):   # Code duplicated in test environment
    infixes = (
        LIST_ELLIPSES
        + LIST_ICONS
        + [
            r"(?<=[0-9])[+\-\*^](?=[0-9-])",
            r"(?<=[{al}{q}])\.(?=[{au}{q}])".format(
                al=ALPHA_LOWER, au=ALPHA_UPPER, q=CONCAT_QUOTES
            ),
            r"(?<=[{a}]),(?=[{a}])".format(a=ALPHA),
            # r"(?<=[{a}])(?:{h})(?=[{a}])".format(a=ALPHA, h=HYPHENS),   # Remove separation of words
            r"(?<=[{a}0-9])[:<>=/](?=[{a}])".format(a=ALPHA),
        ]
    )
    infix_re = compile_infix_regex(infixes)
    # Note that lint'ing may indicate that prefix_search, ... are unexpected arguments - They are valid
    return Tokenizer(nlp_lang.vocab, prefix_search=nlp.tokenizer.prefix_search,
                     suffix_search=nlp.tokenizer.suffix_search, infix_finditer=infix_re.finditer,
                     token_match=nlp.tokenizer.token_match, rules=nlp.Defaults.tokenizer_exceptions)


nlp = spacy.load('en_core_web_trf')
nlp.tokenizer = custom_tokenizer(nlp)
nlp.add_pipe('sentencizer')

spacy_stopwords = nlp.Defaults.stop_words
spacy_stopwords.clear()

matcher = DependencyMatcher(nlp.vocab)
matcher.add("member_name", [member_name_pattern])
matcher.add("name_member", [name_member_pattern])
matcher.add("member_verb_name", [member_verb_name_pattern])
matcher.add("name_verb_member", [name_verb_member_pattern])
matcher.add("members_names", [members_names_pattern])
matcher.add("names_members", [names_members_pattern])
matcher.add("members_verb_names", [members_verb_names_pattern])
matcher.add("names_verb_members", [names_verb_members_pattern])


def _add_named_entities_to_dict(nlp_sentence: Doc, sentence_dict: dict):
    """
    Get the GPE, LOC or FAC (location), EVENT, PERSON, NORP or ORG (agent), DATE and TIME entities
    from the input sentence.

    :param nlp_sentence: The sentence (a spaCy Doc)
    :param sentence_dict: A dictionary that is updated with time-, location- and/or event-related details
    :return: None (sentence_dict is updated with the text of the named entities, where the
             key is either 'LOCS' or 'TIMES')
    """
    for ent in nlp_sentence.ents:
        ent_text = ent.text
        if ent.label_ in ('PERSON', 'ORG', 'NORP'):
            ent_doc = nlp(ent.text)
            ent_names = []
            for token in ent_doc:
                if token.pos_ == 'PROPN':    # Remove any possessive cases and only keep the proper noun
                    ent_names.append(token.text)
            if ent_names:
                ent_text = space.join(ent_names)
        if ent.label_ in ('GPE', 'LOC', 'FAC'):
            add_to_dictionary_values(sentence_dict, 'LOCS', f'{ent_text}+{ent.label_}', str)
        elif ent.label_ in ('PERSON', 'ORG', 'NORP'):
            add_to_dictionary_values(sentence_dict, 'AGENTS', f'{ent_text}+{ent.label_}', str)
        elif ent.label_ in ('DATE', 'TIME'):
            add_to_dictionary_values(sentence_dict, 'TIMES', f'{ent_text}', str)
        elif ent.label_ == 'EVENT':
            add_to_dictionary_values(sentence_dict, 'EVENTS', f'{ent_text}', str)


def _record_family_member(role: str, name: str, family_dict: dict):
    """
    Record a proper name associated with a family role (brother, sister, ...).

    :param role: String holding the family member role
    :param name: String holding the name of the Person (1+ proper nouns)
    :param family_dict: A dictionary keyed by names with values = their family relationship/role;
                        The dictionary is updated if new family members are found
    :return: N/A (family_dict may be updated)
    """
    found = False
    if name in family_dict:
        found = True
        if role != family_dict[name]:
            logging.error(f'Found proper name ({name}) associated with multiple roles, '
                          f'{role} and {family_dict[name]}.')
    else:
        for family_name in family_dict.keys():
            if name in family_name or family_name in name:    # May only have the first or last names
                found = True
                if role != family_dict[family_name]:
                    logging.error(f'Found related names, {name} and {family_name}, associated with '
                                  f'multiple roles, {role} and {family_dict[family_name]}.')
                break
    if not found:
        family_dict[name] = role
    return


def _remove_quotation_marks(text: str) -> str:
    """
    Removes quotation marks and brackets from a sentence (where brackets usually designate an inserted
    word).

    :param text: The original text
    :return: The updated text with the quotes and brackets removed
    """
    text_doc = nlp(text)
    updated_text = empty_string
    for token in text_doc:
        if (token.pos_ == 'PUNCT' and token.text in ('.', '?', '-')) or \
                (token.pos_ == 'PART' and token.dep_ == 'case'):
            updated_text += token.text
        elif token.pos_ != 'PUNCT':
            updated_text += f' {token.text}'
    return updated_text.replace('\u005b', empty_string).replace('\u005d', empty_string).replace('  ', ' ').strip()


def _replace_words(sentence: str) -> str:
    """
    Replace specific phrases/terms with simpler ones - such as replacing 'as well as' with the word, 'and'.

    :param sentence: The sentence whose text should be updated
    :return: The updated sentence
    """
    for key, value in replacement_words.items():
        if key in sentence:
            sentence = sentence.replace(key, value)
        if key.title() in sentence:   # Check for capitalized 'key' words
            sentence = sentence.replace(key.title(), value.title())
    return sentence


def get_family_details(doc: Doc) -> dict:
    """
    Use spaCy rules-based matching to get the proper names of family members from a narrative.

    :param doc: spaCy Document holding the narrative
    :returns: A dictionary keyed by names with values = their family relationship/role
    """
    # TODO: Logic insufficient if multiple families are discussed in a single text
    logging.info('Getting family data from narrative')
    family_dict = dict()
    matches = matcher(doc)
    for match_id, token_ids in matches:          # Indicates which pattern is matched and the specific tokens
        string_id = nlp.vocab.strings[match_id]  # Get string id for the matched pattern
        if string_id in ('member_name', 'name_member'):
            role = doc[token_ids[0]].text
            name_tokens = doc[token_ids[1]].subtree
        elif string_id in ('members_names', 'names_members'):
            role = doc[token_ids[0]].text[:-1]
            name_tokens = doc[token_ids[1]].subtree
        elif string_id in ('member_verb_name', 'name_verb_member'):
            role = doc[token_ids[1]].text
            name_tokens = doc[token_ids[2]].subtree
        else:
            role = doc[token_ids[1]].text[:-1]
            name_tokens = doc[token_ids[2]].subtree
        names = []
        preceding_punct = True
        for name_token in name_tokens:
            if name_token.text == ',' or name_token.text == 'and':
                preceding_punct = True
            if name_token.pos_ == 'PROPN':
                if preceding_punct:
                    preceding_punct = False
                    names.append(f'new{name_token.text}')
                else:
                    names.append(name_token.text)
        new_name = empty_string
        for name in names:
            if name.startswith('new'):
                if new_name:
                    # Record the current 'new' name
                    _record_family_member(role, new_name, family_dict)
                # Reset the 'new' name
                new_name = name.replace('new', empty_string)
                continue
            else:
                # Append the subsequent names (for ex, "Mary Jo Smith") to the new_name
                new_name += space + name
        # Capture the last 'new' name
        _record_family_member(role, new_name, family_dict)
    return family_dict


def get_head_word(text: str) -> (str, str):
    """
    Creates a spacy Doc from the input text and returns the lemma and text of the 'head'/root noun/verb.
    If the root is a noun and a proper name, this function assembles the full name.

    :param text: The text to parse
    :return: The lemma of the root word in the input text and its actual text (for ex, a plural); If
             the root is a noun and a proper name, this function assembles the full name and returns it
             as the lemma and text
    """
    doc = nlp(text)
    for token in doc:
        if token.dep_ == 'ROOT':
            if token.pos_ == 'PROPN':
                complete_names = [ch.text for ch in token.children if ch.dep_ == 'compound']
                complete_name = f'{space.join(complete_names)} {token.text}'.strip()
                if token.text != complete_name:
                    return complete_name, complete_name
            return token.lemma_, token.text
    return empty_string, empty_string


def get_named_entities_in_string(text: str) -> list:
    """
    Returns information on any Named Entities in the text.

    :param text: The text to be parsed
    :return: An array of tuples holding the entity text and type.
    """
    doc = nlp(text)
    named_entities = []
    for ent in doc.ents:
        if ent.label_ in ner_types:
            ent_doc = nlp(ent.text)
            ent_texts = []
            for token in ent_doc:
                if token.dep_ != 'case':
                    ent_texts.append(token.text)
                else:
                    ent_texts.append('/poss/')
            if ent_texts:
                ent_text = space.join(ent_texts)
                named_entities.append((ent_text, ent.label_))
    return named_entities


def get_time_details(phrase: str) -> (int, str):
    """
    For a phrase (such as 'a year later'), get the time increment and number of increments.

    :param phrase: String to be processed
    :return: A tuple of the number of increments and the increment length (for example, 'year');
             If the phrase does not represent a time, then 0 is returned for the int and the original
             phrase is returned in the str
    """
    number = 0
    increment = ''
    nlp_date = nlp(phrase)
    for token in nlp_date:
        if token.dep_ == 'det':    # Assumes 'a' or 'the' means 1
            number = 1
        elif token.dep_ == 'nummod':
            if token.text.isnumeric():
                number = int(token.text)
            else:
                # noinspection PyBroadException
                try:
                    number = w2n.word_to_num(token.lemma_)
                except Exception:
                    number = 0
        elif token.dep_ == 'npadvmod':
            increment = token.text
    return number, increment


def parse_narrative(narr_text: str) -> (list, list, dict):
    """
    Creates a spacy Doc from the entire narrative text, then splits sentences into clauses with
    their own subjects/verbs, and parses each of the resulting sentences to create a dictionary
    holding the subject/verb/object/preposition/... details. Each of the sentence dictionaries are
    added to an array, which is returned.

    :param narr_text: The narrative text
    :return: A tuple consisting of an array of dictionaries holding the details of each sentence
             (after splitting), an array of the texts of any quotations (texts between any types of
             quotation marks), and a dictionary of quotations that have a subject and verb (and
             will be removed from the final narrative)
    """
    revised_narr = _replace_words(narr_text)
    updated_narr, quotations, quotations_dict = resolve_quotations(revised_narr)
    # \n\n indicates a new paragraph
    updated_narr = updated_narr.replace('\n\n', " New line. ").replace('\n', empty_string)
    doc = nlp(updated_narr)
    sentence_dicts = []
    sentence_offset = 0
    for sentence in doc.sents:
        sent_dict = dict()
        sentence_offset += 1
        sent_dict['offset'] = sentence_offset
        sent_text = sentence.text
        if sent_text in ('New line.' or 'New line'):
            sent_dict['text'] = "New line"
            sentence_dicts.append(sent_dict)
            continue
        new_line_at_end = False
        if 'New line' in sent_text:
            # Sentence is more than just a 'new line' - for ex, 'She claimed that Quotation0 New line'
            if sentence.text.startswith('New line.') or sentence.text.startswith('New line'):
                sent_dict['text'] = 'New line'
                sentence_dicts.append(sent_dict)
                sent_dict = dict()    # Create a new dictionary for the remainder of the text
                sentence_offset += 1
                sent_dict['offset'] = sentence_offset
            elif sentence.text.endswith('New line.') or sentence.text.endswith('New line'):
                new_line_at_end = True
            sent_text = sent_text.replace('New line.', empty_string).replace('New line', empty_string).strip()
        sent_dict['text'] = sent_text
        if '?' in sent_text:
            sent_dict['punct'] = '?'
        _add_named_entities_to_dict(nlp(sent_text), sent_dict)
        # Split sentences into chunks based on quotations and whether they have their own verb
        chunk_dicts = []
        for chunk in split_clauses(sent_text, nlp):
            # Clean up a chunk if it begins or ends with a 'mark' (which may happen with quotations)
            nlp_chunk = nlp(chunk)
            marks = [child for child in nlp_chunk if child.dep_ == 'mark']
            for mark in marks:
                mark_text = mark.text
                if chunk.startswith(mark_text):
                    chunk = chunk[len(mark_text) + 1:].strip()
                elif chunk.endswith(mark_text):
                    chunk = chunk[0:(len(mark_text) * -1)].strip()
            # Get the details of each chunk
            chunk_dict = dict()
            chunk_dict['chunk_text'] = chunk
            chunk_dict['verb_processing'] = []
            if chunk.startswith('Quotation'):
                chunk_dicts.append(chunk_dict)
            else:
                chunk_dicts.append(extract_chunk_details(chunk, chunk_dict, nlp))
        sent_dict['chunks'] = chunk_dicts
        sentence_dicts.append(sent_dict)
        if new_line_at_end:
            sent_dict = dict()   # Create a new dictionary to capture the 'new line'
            sentence_offset += 1
            sent_dict['offset'] = sentence_offset
            sent_dict['text'] = 'New line'
            sentence_dicts.append(sent_dict)
    return sentence_dicts, quotations, quotations_dict, get_family_details(doc)


def resolve_quotations(narr: str) -> (str, list, dict):
    """
    Process the quotations in the text - capture them and remove quotation marks.

    :param narr: The original narrative text
    :return: A tuple with (1) the updated narrative text (removing quotation marks and removing any quotations
             with a subj+verb, replacing the quote with the text 'Quotation#'), (2) a list of quotations
             (separating out individual sentences) and (3) a dictionary of the quotations that were removed
             from the narrative (with the keys, 'Quotation#')
    """
    quot_dict = dict()
    quot_dict[0] = re.findall(r"\u0022(.*?)\u0022", narr)   # Double quotes
    quot_dict[1] = re.findall(r"\u2018(.*?)\u2019", narr)   # Left and right single quotes
    quot_dict[2] = re.findall(r"\u201c(.*?)\u201d", narr)   # Left and right double quotes
    lengths = [len(quot_dict[0]), len(quot_dict[1]), len(quot_dict[2])]
    if len([gt for gt in lengths if gt > 0]) > 0:   # Are there any quotes in the text?
        # Yes, but may have quotes within quotes
        # Assume that the quotation type with the largest number of quotations is the main choice for quoting
        index_max = max(range(len(lengths)), key=lengths.__getitem__)
        quotations = quot_dict[int(index_max)]
    else:    # No quotes, just return
        return narr, [], dict()
    new_quotes = []    # Updated list of quotations
    for quote in quotations:
        quote_doc = nlp(quote)
        if len(list(quote_doc.sents)) > 1:   # Break a multi-sentence quote into its individual sentences
            for sent in list(quote_doc.sents):
                new_quotes.append(sent.text[:-1] if sent.text.endswith(',') else sent.text)
        else:
            new_quotes.append(quote[:-1] if quote.endswith(',') else quote)
    updated_narr = _remove_quotation_marks(narr)     # Clean the narrative to remove quotation marks
    # Create quotations dictionary and update narrative to remove quotations that are sentences (have subjs + verbs)
    index = 0
    quotation_dict = dict()
    final_quotes = []
    for quote in new_quotes:   # Process the individual sentences
        quote_doc = nlp(quote)
        quote_verbs = [wd for wd in list(quote_doc) if wd.pos_ in ('VERB', 'AUX')]
        quote_subjs = []
        if quote_verbs:
            for quote_verb in quote_verbs:
                quote_subjs = [wd for wd in quote_verb.children if 'subj' in wd.dep_]
                if quote_subjs:
                    break
        if quote_verbs and quote_subjs:
            # Remove quote from narrative and replace with 'Quotation#'
            # Address fact that a quotation may include other quotations within it
            updated_quote = _remove_quotation_marks(quote)
            updated_narr = updated_narr.replace(updated_quote, f' Quotation{index}')
            quotation_dict[f'Quotation{index}'] = quote[:-1] if quote.endswith('.') else quote
            final_quotes.append(quote[:-1] if quote.endswith('.') else quote)
            index += 1
        else:
            # Phrases should not end with periods
            final_quotes.append(quote[:-1] if quote.endswith('.') else quote)
    return updated_narr.replace('  ', space).replace('\n ', '\n').replace(' \n', '\n').strip(), \
        final_quotes, quotation_dict
