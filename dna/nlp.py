# Entry points for all spaCy processing and creation of the KG from the text parse
# Includes functions for getting family details, head words, sentiment, named entities, relative time, etc.
# Key functions: ingest_narratives -> parse_narratives
#  Where a narrative's sentences are parsed into dictionary elements with the following form:
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
#    (ingest_narrative -> parse_narrative)
# Sentence dictionaries are evaluated to produce the KG Turtle output
#    (ingest_narrative -> create_narrative_turtle's create_turtle)

from os import listdir
from os.path import isfile, join
import spacy
from spacy.matcher import DependencyMatcher
from textblob import TextBlob
from word2number import w2n

from create_narrative_turtle import create_turtle
from nlp_sentence_dictionary import extract_dictionary_details
from nlp_split_sentences import split_clauses
from utilities import empty_string, new_line

nlp = spacy.load('en_core_web_trf')
nlp.add_pipe('sentencizer')
matcher = DependencyMatcher(nlp.vocab)

spacy_stopwords = nlp.Defaults.stop_words
spacy_stopwords.clear()

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


def get_family_details(narrative: str) -> dict:
    """
    Use spaCy Dependency Parsing and rules-based matching to get family member names from a narrative.

    :param narrative: String holding the narrative
    :returns: A dictionary containing the proper names of family members (the keys) and their
              relationships (values)
    """
    # Analyze the text using spaCy and get matches to 'member' rule
    doc = nlp(narrative.replace('\n', ''))
    matches = matcher(doc)
    family_dict = dict()
    # Each token_id corresponds to one pattern dict
    for match in matches:
        match_id, token_ids = match   # Indicates which pattern is matched and the specific tokens
        string_id = nlp.vocab.strings[match_id]   # Get the string representation; There is only 1 right now
        if string_id == 'family_member_name':
            family_dict[doc[token_ids[1]].text] = doc[token_ids[0]].text   # Key = proper name, Value = relationship
    return family_dict


def get_head_word(text: str) -> (str, str):
    """
    Creates a spacy Doc from the input text and returns the lemma and text of the 'head'/root noun/verb.

    :param text: The text to parse
    :returns: The lemma of the root word in the input text and its actual text
    """
    # TODO: Use more efficient way to get the lemma if there is only a single word in the text
    doc = nlp(text)
    for token in doc:
        if token.dep_ == 'ROOT':
            return token.lemma_, token.text


def get_named_entity_in_string(text: str) -> (str, str):
    """
    Returns information on any Named Entities that are Agents (people, organizations, geopolitical
    entities, ...) or Events in the input text.

    :param text: The text to be parsed
    :returns: Two strings - the first is the named entity's text and the second string is its
             type mapped to the DNA Agent sub-classing hierarchy or to :EventAndState; If the input text
             does not contain any Named Entities, then two empty strings are returned
    """
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ in ner_types:
            return ent.text, ner_dict[ent.label_]
    return empty_string, empty_string


def get_sentence_sentiment(sentence: str) -> float:
    """
    Use TextBlob to get sentence polarity/sentiment.

    :param sentence: The sentence to be analyzed.
    :returns: The polarity (-1 for negative, 1 for positive) of the sentence
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
    :returns: A tuple of the number of increments and the increment length (for example, 'year')
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


def ingest_narratives(narr_dir: str, database: str) -> int:
    """
    Ingest each of the .txt files in the narr_dir directory, parse the text into Turtle
    and load the results to the specified database.

    :param narr_dir: Directory holding the text narratives
    :param database: Database to which the resulting KG triples are loaded
    :returns: Integer indicating the number of narratives added
    """
    # Get narrative texts
    count = 0
    try:
        in_files = [f for f in listdir(f'{dna_root}{narr_dir}') if f.endswith('.txt') and
                    isfile(join(f'{dna_root}{narr_dir}', f))]
        for infile in in_files:
            with open(f'{dna_root}{narr_dir}{infile}', 'r', encoding='utf8', errors='ignore') as narr_in:
                text = narr_in.read()
            title = infile.split('.txt')[0]
            sentence_dicts = parse_narrative(text)
            event_turtle_list = create_event_turtle(sentence_dicts)
            # Add the triples to the data store, to a named graph with name = graph_name
            add_remove_data('add', ' '.join(event_turtle_list), database, f'urn:{title}')
            count += 1
    except Exception as e:
        print(f'Exception ingesting narratives: {str(e)}', True)
        traceback.print_exc(file=sys.stdout)
    return count


def parse_narrative(narr_text: str) -> list:
    """
    Creates a spacy Doc from the entire narrative text, then splits sentences by conjunctions into clauses
    with their own subjects/verbs, and parses each of the resulting sentences to create a dictionary
    holding the subject/verb/object/preposition/... details. Each of the sentence dictionaries are added
    to an array, which is returned.

    :param narr_text: The narrative text
    :returns: An array of dictionaries holding the details of each sentence (after splitting)
    """
    family_dict = get_family_details(narr_text)
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
        revised = replace_words(sentence.text)
        extract_dictionary_details(revised, sentence_dicts, nlp, family_dict, sentence_offset)
        sentence_offset += 1
    return sentence_dicts


def replace_words(sentence: str) -> str:
    """
    Replace specific phrases/terms with simpler ones - such as replacing 'as well as' with the word, 'and'.

    :param sentence: The sentence whose text should be updated
    :returns: The updated sentence
    """
    for key, value in replacement_words.items():
        if key in sentence:
            sentence = sentence.replace(key, value)
        if key.title() in sentence:
            sentence = sentence.replace(key.title(), value.title())
    return sentence
