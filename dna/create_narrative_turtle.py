# Processing to create the Turtle rendering of the sentences in a narrative
# The sentences are defined by their sentence dictionaries, which have the form:
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

import logging
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import re
import uuid

from dna.create_specific_turtle import cleanup_turtle
from dna.process_agents import get_name_permutations, get_sentence_agents
from dna.process_locations import get_sentence_locations
from dna.process_times import get_sentence_times
from dna.process_verbs import process_verb
from dna.utilities_and_language_specific import empty_string, family_members, \
    ttl_prefixes, underscore

sid = SentimentIntensityAnalyzer()


def _add_mentions_to_sentence(sentence_iri: str, mention_iris: list, sentence_ttl_list: list):
    """
    Add mentions of agents/persons, locations and events to the sentence.

    :param sentence_iri: A string identifying the sentence
    :param mention_iris: A list of either agent/person, location or event IRIs associated with
                         named entities in the sentence
    :return: None
    """
    for mention_iri in mention_iris:
        sentence_ttl_list.append(f'{sentence_iri} :mentions {mention_iri} .')
    return


def _get_text_sentiment(text: str, negated: bool, emotion: str) -> float:
    """
    Get chunk polarity.
    TODO: Verify that emotion and sentiment are taken into account.

    :param text: The chunk to be analyzed.
    :param negated: Boolean indicating that the verb is negated (if true)
    :param emotion: String = 'positive' or 'negative' (characterizing the emotion), 'emotion'
                    if it can be either positive or negative, or an empty string if not an
                    emotion/mood
    :return: The polarity (-1 for negative, 1 for positive) of the sentence
    """
    # TODO: Resolve PolyGlot loading on Mac - Issues with ICU
    text_scores = sid.polarity_scores(text)
    return text_scores['compound']
    # if (emotion == 'negative' and not negated and sentiment > 0) or \
    #        (emotion == 'negative' and negated and sentiment < 0) or \
    #        (emotion == 'positive' and not negated and sentiment < 0) or \
    #        (emotion == 'positive' and negated and sentiment > 0):
    #    # Should probably reverse the sentiment
    #    return sentiment * -1
    # else:
    #    return sentiment
    # return 0.0


def _process_chunk(chunk_dict: dict, chunk_iri: str, offset: int, alet_dict: dict, loc_time_iris: list,
                   last_nouns: list, last_events: list, ext_sources: bool, is_bio: bool) -> list:
    """
    Generate the Turtle for each chunk in a sentence, from the chunk's dictionary definition.

    :param chunk_dict: The dictionary for the chunk
    :param chunk_iri: The IRI identifier for the chunk
    :param offset: Integer indicating the ordering of the chunk within the sentence
    :param alet_dict: A dictionary holding the agents, locations, events & times encountered in
             the full narrative - For co-reference resolution (it may be updated by this function);
             Keys = 'agents', 'locs', 'events', 'times' and Values vary by the key
    :param loc_time_iris: An array holding the last processed location (index 0) and time (index 1)
    :param last_nouns: An array of noun texts, type, class mapping and IRI from the current paragraph
    :param last_events: An array of verb texts, class mapping and IRI from the current paragraph
    :param ext_sources: A boolean indicating that data from GeoNames, Wikidata, etc. should be
                        added to the parse results if available
    :param is_bio: A boolean indicating that the text is biographical/autobiographical
    :return: An array of Turtle statements defining the chunk's knowledge graph
    """
    # TODO: Deal with '$&', special mark, in text
    chunk_text = chunk_dict['chunk_text']
    chunk_ttl_list = [f'{chunk_iri} a :Chunk ; :offset {offset} .',
                      f'{chunk_iri} :text "{chunk_text}" .',
                      f'{chunk_iri} :sentiment {_get_text_sentiment(chunk_text, empty_string, empty_string)} .']
    if chunk_text.startswith('Quotation'):
        return chunk_ttl_list
    new_ttl_list = process_verb(chunk_iri, chunk_dict, alet_dict, loc_time_iris, last_nouns,
                                last_events, ext_sources, is_bio)
    if new_ttl_list:
        chunk_ttl_list.extend(new_ttl_list)
        return chunk_ttl_list
    return []


def _process_family(family_dict: dict) -> list:
    """
    Process the entries in family_dict and create entries to add to the alet_dictionary as
    new 'agents'.

    :return: An array of arrays with index 0 holding an array of labels associated with the agent (variations
             on their name), index 1 storing the agent's entity type and index 2 storing the agent's IRI
    """
    unique_names = []
    for name1 in family_dict.keys():
        found = False
        for name2 in family_dict.keys():
            if name1 != name2 and name1 in name2 and name2.startswith(name1):    # Part of name overlaps
                unique_names.append(name2)        # Save the longer name
                found = True
                break
        if found:
            continue
        unique_names.append(name1)                # Longer name or no overlap - so save name1
    agents_list = []
    for unique_name in unique_names:
        family_role = family_dict[unique_name]
        role_gender = family_members[family_role]
        alt_names = get_name_permutations(unique_name)
        alt_names.append(family_role)
        agents_list.append((alt_names, f'{role_gender}SINGPERSON' if role_gender else 'SINGPERSON',
                            re.sub(r'[^:a-zA-Z0-9_]', underscore, f':{unique_name}_{family_role}').replace('__', '_')))
    return agents_list


def create_graph(sentence_dicts: list, family_dict: dict, published: str, use_sources: bool = False,
                 is_bio: bool = False) -> (bool, list):
    """
    Using the sentence dictionaries generated by the nlp functions, create the Turtle
    rendering of the events.

    :param sentence_dicts: An array of sentence dictionaries for a narrative
    :param family_dict: A dictionary holding proper nouns and the relationship that they have to
                        the subject/narrator; This is only used when is_bio is True
    :param published: A string indicating the date that the article was published, if provided
                      (otherwise, the empty string)
    :param use_sources: A boolean indicating that data from GeoNames, Wikidata, etc. should be
                        added to the parse results if available
    :param is_bio: A boolean indicating that the text is biographical/autobiographical
    :return: A tuple consisting of a boolean indicating success (if true) or failure, and a
              list of the Turtle statements encoding the narrative (if successful)
    """
    logging.info(f'Creating narrative Turtle')
    graph_ttl_list = []
    graph_ttl_list.extend(ttl_prefixes)
    # A dictionary holding the agents, locations, events & times encountered in the text - For co-reference resolution
    #  Keys = 'agents', 'locs', 'events', 'times' and Values vary by key type
    alet_dictionary = dict()
    if is_bio and family_dict:
        family_details = _process_family(family_dict)
        if family_details:
            alet_dictionary['agents'] = family_details
            for fam_detail in family_details:
                alt_names, ent_type, fam_iri = fam_detail
                label_names = '", "'.join(alt_names)
                graph_ttl_list.append(f'{fam_iri} a :Person ; rdfs:label "{label_names}" .')
                gender = 'Female' if 'FEMALE' in ent_type else ('Male' if 'MALE' in ent_type else empty_string)
                if gender:
                    graph_ttl_list.append(f'{fam_iri} :gender "{gender}" .')
    last_nouns = []   # Array of tuples of noun texts, types, class mappings and IRIs; Paragraph boundaries highlighted
    last_events = []   # Array of tuples of class mappings and IRIs; Paragraph boundaries highlighted
    # An array with index 0 = last location mentioned, index 1 = last time mentioned
    loc_time_iris = [empty_string, empty_string]
    for sent_dict in sentence_dicts:
        if 'punct' in sent_dict and sent_dict['punct'] == '?':
            continue     # TODO: Handle questions
        sentence_text = sent_dict['text']
        if sentence_text == 'New line':     # Future: What if last_nouns and last_events arrays become too large?
            last_nouns.append(('new_line', empty_string, empty_string, empty_string))
            last_events.append(('new_line', empty_string))
            continue
        sentence_iri = f':Sentence_{str(uuid.uuid4())[:13]}'
        sent_text = sent_dict['text']
        sentence_ttl_list = [f'{sentence_iri} a :Sentence ; :offset {sent_dict["offset"]} .',
                             f'{sentence_iri} :text "{sent_text}" .']
        # Handle location, time and agent info
        if 'LOCS' in sent_dict:
            loc_iris, locs_ttl = get_sentence_locations(sent_dict, alet_dictionary, last_nouns, use_sources)
            _add_mentions_to_sentence(sentence_iri, loc_iris, sentence_ttl_list)
            sentence_ttl_list.extend(locs_ttl)
        if 'TIMES' in sent_dict or 'EVENTS' in sent_dict:
            event_iris, time_ttl = get_sentence_times(sent_dict, published, alet_dictionary, last_nouns, use_sources)
            _add_mentions_to_sentence(sentence_iri, event_iris, sentence_ttl_list)
            sentence_ttl_list.extend(time_ttl)
        # Handle AGENTS
        if 'AGENTS' in sent_dict:
            agent_iris, agents_ttl = get_sentence_agents(sent_dict, alet_dictionary, last_nouns, use_sources)
            _add_mentions_to_sentence(sentence_iri, agent_iris, sentence_ttl_list)
            sentence_ttl_list.extend(agents_ttl)
        # Handle each sentence's chunks, in order
        chunk_offset = 1
        for chunk in sent_dict['chunks']:
            chunk_iri = f':Chunk_{str(uuid.uuid4())[:13]}'
            sentence_ttl_list.append(f'{sentence_iri} :has_component {chunk_iri} .')
            sentence_ttl_list.extend(
                _process_chunk(chunk, chunk_iri, chunk_offset, alet_dictionary, loc_time_iris,
                               last_nouns, last_events, use_sources, is_bio))
            chunk_offset += 1
        # Clean up unused subject IRIs (e.g., where the subject never occurs as an object) and save the Turtle
        graph_ttl_list.extend(cleanup_turtle(sentence_ttl_list))
    return True, graph_ttl_list
