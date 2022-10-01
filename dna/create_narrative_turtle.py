# Processing to create the Turtle rendering of the sentences in a narrative
# The sentences are defined by their sentence dictionaries, which have the form:
#    'text': 'narrative_text', 'sentence_offset': #,
#    'PERSONS': ['person1', 'person2', ...], 'LOCS': ['location1', ...],
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

import logging
from textblob import TextBlob
import uuid

from dna.process_locations import get_sentence_locations
from dna.process_persons import get_sentence_persons
from dna.process_times import get_sentence_times
from dna.process_verbs import process_verb
from dna.utilities import empty_string

ttl_prefixes = ['@prefix : <urn:ontoinsights:dna:> .', '@prefix dna: <urn:ontoinsights:dna:> .',
                '@prefix dc: <http://purl.org/dc/terms/> .', '@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .']

# Date processing is handled differently/separately
# TODO: Other interpretations + near, on, over, of, without, ...
#    (https://www.oxfordlearnersdictionaries.com/us/definition/english/xxx)
prep_to_predicate_for_locs = {'about': ':has_topic',
                              'at': ':has_location',
                              'from': ':has_origin',
                              'to': ':has_destination',
                              'in': ':has_location'}


def _get_text_sentiment(text: str) -> float:
    """
    Use TextBlob to get sentence polarity/sentiment, and then adjust it based on

    :param text: The sentence to be analyzed.
    # :param negated: Boolean indicating that the verb is negated (if true)
    # :param emotion: String = 'positive' or 'negative' (characterizing the emotion), 'emotion'
    #                if it can be either positive or negative, or an empty string if not an
    #                emotion/mood
    :return: The polarity (-1 for negative, 1 for positive) of the sentence
    """
    blob = TextBlob(text)
    # TextBlob's sentiment is a namedtuple = (polarity, subjectivity)
    # The polarity score is a float within the range [-1.0, 1.0] - negative to positive
    # The subjectivity is a float within the range [0.0, 1.0] - 0.0 = very objective and 1.0 = very subjective
    return blob.sentiment.polarity
    # TODO: Test sentiment if negated verb, and negative emotion
    # if (emotion == 'negative' and not negated and sentiment > 0) or \
    #        (emotion == 'negative' and negated and sentiment < 0) or \
    #        (emotion == 'positive' and not negated and sentiment < 0) or \
    #        (emotion == 'positive' and negated and sentiment > 0):
    #    # Should probably reverse the sentiment
    #    return sentiment * -1
    # else:
    #    return sentiment


def _process_chunk(chunk_dict: dict, chunk_iri: str, offset: int, plet_dict: dict, loc_time_iris: list,
                   last_nouns: list, last_events: list, ext_sources: bool, timeline_poss: bool) -> list:
    """
    Generate the Turtle for each chunk in a sentence, from the chunk's dictionary definition.

    :param chunk_dict: The dictionary for the chunk
    :param chunk_iri: The IRI identifier for the chunk
    :param offset: Integer indicating the ordering of the chunk within the sentence
    :param plet_dict: A dictionary holding the persons, locations, events & times encountered in
             the full narrative - For co-reference resolution (it may be updated by this function);
             Keys = 'persons', 'locs', 'events', 'times' and Values vary by the key
    :param loc_time_iris: An array holding the last processed time (index 0) and location (index 1)
    :param last_nouns: An array of noun texts, type, class mapping and IRI from the current paragraph
    :param last_events: An array of verb texts, class mapping and IRI from the current paragraph
    :param ext_sources: A boolean indicating that data from GeoNames, Wikidata, etc. should be
                        added to the parse results if available
    :param timeline_poss: A boolean indicating that the narrative could have a timeline - for
                          example, this would likely be true for biographies/autobiographies but
                          not for news articles
    :return: An array of Turtle statements defining the chunk's knowledge graph
    """
    chunk_text = chunk_dict['chunk_text']
    chunk_ttl_list = [f'{chunk_iri} a :Chunk ; :offset {offset} .',
                      f'{chunk_iri} :text "{chunk_text}" .']
    if chunk_text.startswith('Quotation'):
        return chunk_ttl_list
    event_iri, new_ttl_list = process_verb(chunk_dict, plet_dict, loc_time_iris, last_nouns, last_events,
                                           ext_sources, timeline_poss)
    if event_iri:
        chunk_ttl_list.extend(new_ttl_list)
        return chunk_ttl_list
    return []


def create_graph(sentence_dicts: list, published: str, use_sources: bool = False,
                 timeline_poss: bool = False) -> (bool, list):
    """
    Using the sentence dictionaries generated by the nlp functions, create the Turtle
    rendering of the events.

    :param sentence_dicts: An array of sentence dictionaries for a narrative
    :param published: A string indicating the date that the article was published, if provided
                      (otherwise, the empty string)
    :param use_sources: A boolean indicating that data from GeoNames, Wikidata, etc. should be
                        added to the parse results if available
    :param timeline_poss: A boolean indicating that the narrative could have a timeline - for
                          example, this would likely be true for biographies/autobiographies but
                          not for news articles
    :return: A tuple consisting of a boolean indicating success (if true) or failure, and a
              list of the Turtle statements encoding the narrative (if successful)
    """
    logging.info(f'Creating narrative Turtle')
    # A dictionary holding the persons, locations, events & times encountered in the text - For co-reference resolution
    #  Keys = 'persons', 'locs', 'events', 'times' and Values vary by key type
    plet_dictionary = dict()
    last_nouns = []    # Array of tuples of noun texts, types, class mappings and IRIs, reset at paragraph boundaries
    last_events = []   # Array of tuples of verb texts, class mappings and IRIs, reset at paragraph boundaries
    graph_ttl_list = []
    graph_ttl_list.extend(ttl_prefixes)
    for sent_dict in sentence_dicts:
        if 'punct' in sent_dict and sent_dict['punct'] == '?':
            continue     # TODO: Handle questions
        sentence_text = sent_dict['text']
        if sentence_text == 'New line':
            last_nouns = []         # Reset the nouns being co-referenced by paragraph boundaries
            last_events = []
            continue
        sentence_iri = f':Sentence_{str(uuid.uuid4())[:13]}'
        sent_text = sent_dict['text']
        sentence_ttl_list = [f'{sentence_iri} a :Sentence ; :offset {sent_dict["offset"]} .',
                             f'{sentence_iri} :text "{sent_text}" .']
        # Handle location, time and person info
        if 'LOCS' in sent_dict:
            locs_ttl = get_sentence_locations(sent_dict, plet_dictionary, last_nouns, use_sources)
            sentence_ttl_list.extend(locs_ttl)
        if 'TIMES' in sent_dict or 'EVENTS' in sent_dict:
            dates_ttl = get_sentence_times(sent_dict, published, plet_dictionary, last_nouns, use_sources)
            sentence_ttl_list.extend(dates_ttl)
        # Handle PERSONS
        if 'PERSONS' in sent_dict:
            persons_ttl = get_sentence_persons(sent_dict, plet_dictionary, last_nouns, use_sources)
            sentence_ttl_list.extend(persons_ttl)
        # Handle each sentence's chunks, in order
        chunk_offset = 1
        # An array with index 0 = last time mentioned, index 1 = last location mentioned
        loc_time_iris = [empty_string, empty_string]
        for chunk in sent_dict['chunks']:
            chunk_iri = f':Chunk_{str(uuid.uuid4())[:13]}'
            sentence_ttl_list.append(f'{sentence_iri} :has_component {chunk_iri} .')
            sentence_ttl_list.extend(
                _process_chunk(chunk, chunk_iri, chunk_offset, plet_dictionary, loc_time_iris,
                               last_nouns, last_events, use_sources, timeline_poss))
            chunk_offset += 1
        graph_ttl_list.extend(sentence_ttl_list)
    return True, graph_ttl_list
