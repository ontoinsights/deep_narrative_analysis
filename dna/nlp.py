# Entry points for all spaCy processing:
# 1) Pattern matching (in get_birth_family_details)
# 2) Noun/verb details (in get_nouns_verbs)
# 3) Processing for phrases in the form, 'a'|'the'|# 'years'|'months'|'days'|... 'earlier'|'later'|'prior'|...
#    (in get_time_details)
# 4) Parses the sentences from a narrative into dictionary elements with the following form:
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
#    (in parse_narrative)

import logging
import spacy

from nltk.corpus import wordnet as wn
from spacy.matcher import DependencyMatcher
from textblob import TextBlob
from word2number import w2n


from nlp_patterns import born_date_pattern, born_place_pattern, family_member_name_pattern
from nlp_sentence_dictionary import extract_dictionary_details
from nlp_split_sentences import split_clauses
from utilities import empty_string, new_line, update_dictionary_count

nlp = spacy.load('en_core_web_trf')
nlp.add_pipe('sentencizer')
matcher = DependencyMatcher(nlp.vocab)

spacy_stopwords = nlp.Defaults.stop_words
spacy_stopwords.clear()

matcher.add("born_date", [born_date_pattern])
matcher.add("born_place", [born_place_pattern])
matcher.add("family_member_name", [family_member_name_pattern])

ner_dict = {'PERSON': ':Person',
            'NORP': ':Organization',
            'ORG': ':Organization',
            'GPE': ':GeopoliticalEntity',
            'LOC': ':GeopoliticalEntity',
            'EVENT': ':EventAndState'}
ner_types = list(ner_dict.keys())

# Replace multi-word phrases or non-standard terms acting as conjunctions and prepositions
# (or using prepositions) with single words
replacement_words = {
    'as well as': 'and',
    'circa': 'in',
    'in addition to': 'and',
    'since': 'for',   # Assumes that clauses such as 'since [noun] [verb]' have already been split out
    'next to': 'near',
    'on behalf of': 'for',
    'prior to': 'before',
    'subsequent to': 'after'
}


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
    doc = nlp(narrative.replace('\n', ''))
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
            family_dict[doc[token_ids[1]].text] = doc[token_ids[0]].text   # Key = proper name, Value = relationship
    # Verify that dates actually have a year
    found_year = any([value for value in born_on_date if (value.isnumeric() and int(value) > 1000)])
    if not found_year:
        born_on_date = set()
    return list(born_on_date), list(born_in_place), family_dict


def get_synonym(text: str) -> list:
    """
    Get the synonyms/lemma of the input text.

    :param text: String to be lemmatized
    :return An array holding the synonyms/lemmas of the input text
    """
    words = []
    syns = wn.synsets(text)
    for syn in syns:
        text = str(syn)
        words.append(text[text.index("'") + 1:text.index('.')])
    return words


def get_named_entity_in_string(text: str) -> (str, str):
    """
    Returns information on any Named Entity that are Agents (people, organizations, geopolitical
    entities, ...) or Events in the input text.

    :param text: The text to be parsed
    :return Two strings - the first is the named entity's text and the second string is its
            type mapped to the DNA Agent sub-classing hierarchy or to :EventAndState; If the input text
            does not contain any Named Entities, then two empty strings are returned
    """
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ in ner_types:
            return ent.text, ner_dict[ent.label_]
    return empty_string, empty_string


def get_noun(text: str, get_first_occurrence: bool) -> str:
    """
    Creates a spacy Doc from the input text and returns the first (or last) noun found.

    :param text: The text to parse
    :param get_first_occurrence: Boolean indicating that the first noun is returned (if True);
                                 otherwise, the last noun is returned
    :return: The first or last (depending on whether the first variable is True or False) noun
             in the input text, or an empty string if no noun is found
    """
    doc = nlp(text)
    word = empty_string
    for token in doc:
        if token.pos_ in ('NOUN', 'PROPN'):
            if token.dep_ == 'compound':
                continue
            word = token.text
            if get_first_occurrence:
                break
    return word


def get_nouns_verbs(sentences: str) -> (dict, dict):
    """
    Parses all the sentences in the input parameter to return counts of each distinct
    noun and verb.

    :param sentences: String with the text of one or more sentences
    :return: Two dictionaries of the counts of the noun/verb lemmas where the noun
             dictionary is returned first
    """
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


def get_proper_nouns(text: str) -> str:
    """
    Extract a string consisting of the proper nouns in a text string. For example, "New York City ghetto"
    would return "New York City".

    :param text: The text string to be parsed
    :return A string of the proper nouns
    """
    phrase = nlp(text)
    proper_nouns = []
    for token in phrase:
        noun_type = token.morph.get('NounType')
        if noun_type and noun_type[0] == 'Prop':   # Have a proper noun
            proper_nouns.append(token.text)
    if proper_nouns:
        return ' '.join(proper_nouns)
    else:
        return empty_string


def get_sentence_sentiment(sentence: str) -> float:
    """
    Use TextBlob to get sentence polarity/sentiment.

    :param sentence: The sentence to be analyzed.
    :return The polarity (-1 for negative, 1 for positive) of the sentence
    """
    blob = TextBlob(sentence)
    # TextBlob's sentiment property returns a namedtuple of the form, (polarity, subjectivity).
    # The polarity score is a float within the range [-1.0, 1.0] - negative to positive.
    # The subjectivity is a float within the range [0.0, 1.0] - 0.0 = very objective and 1.0 = very subjective.
    return blob.sentiment.polarity


def get_time_details(phrase: str) -> (int, str):
    """
    For a phrase (such as 'a year later'), get the time increment and number of increments.

    :param phrase: String to be processed
    :return A tuple of the number of increments and the increment length (for example, 'year')
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
                number = w2n.word_to_num(token.lemma_)
        elif token.dep_ == 'npadvmod':
            increment = token.text
    return number, increment


def parse_narrative(narr_text: str, gender: str, family_dict: dict) -> list:
    """
    Creates a spacy Doc from the input text, splits sentences by conjunctions into clauses with
    their own subjects/verbs, and then parses each of the resulting sentences to create a
    dictionary holding the subject/verb/object/preposition/... details. Each of the sentence
    dictionaries are added to an array, which is returned.

    :param narr_text: The narrative text
    :param gender: Either an empty string or one of the values, AGENDER, BIGENDER, FEMALE or
                   MALE - indicating the gender of the narrator
    :param family_dict: A dictionary containing the names of family members and their
                        relationship to the narrator/subject
    :return: An array of dictionaries holding the details of each sentence (after splitting)
    """
    doc = nlp(narr_text)
    split_sentences = []
    sentence_dicts = []
    # Split sentences by conjunctions
    for sentence in doc.sents:
        if sentence.text.startswith(new_line):
            # When using a text editor on the narrative, the new line may be part of the 'next' line of text
            split_sentences.append(nlp("New line"))
            sent_text = sentence.text.replace(new_line, '')
            if not sent_text:
                continue
        else:
            sent_text = sentence.text
        # Change conjunctions into new sentences
        for sent in split_clauses(sent_text, nlp):
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
    sentence_offset = 1
    for sentence in split_sentences:
        revised = _replace_words(sentence.text)
        extract_dictionary_details(revised, sentence_dicts, nlp, gender, family_dict, sentence_offset)
        sentence_offset += 1
    return sentence_dicts


# Functions internal to the module
def _replace_words(sentence: str) -> str:
    """
    Replace specific phrases/terms with simpler ones - such as replacing 'as well as' with the word, 'and'.

    :param sentence: The sentence whose text should be updated
    :return The updated sentence
    """
    for key, value in replacement_words.items():
        if key in sentence:
            sentence = sentence.replace(key, value)
        if key.title() in sentence:
            sentence = sentence.replace(key.title(), value.title())
    return sentence
