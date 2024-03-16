# Processing to create the Turtle rendering of the sentences in a narrative
# Where a narrative's sentences are parsed into dictionary elements with the following form:
#    'text': 'narrative_text', 'offset': #, 'punct': '?|!',
#    'entities': ['text+ent_label1', 'text+ent_label2', ...]
# And the text is analyzed using OpenAI

import logging
import openai
import os
import re
from typing import List
import uuid

from dna.process_entities import get_name_permutations
from dna.process_sentences import get_sentence_details
from dna.query_openai import access_api, coref_prompt
from dna.utilities_and_language_specific import empty_string, personal_pronouns, space, ttl_prefixes, underscore


def create_graph(quote_dict: dict, sentence_dicts: list) -> (bool, list):
    """
    Using the sentence dictionaries generated by the nlp functions, create the Turtle
    rendering of the events.

    :param quote_dict: An array of quotation dictionaries (key = 'Quotation#' which is referenced
                      in a chunk, and value = full quotation text and the probable speaker)
                      extracted from the original text
    :param sentence_dicts: An array of sentence dictionaries for a narrative
    :return: A tuple consisting of a boolean indicating success (if true) or failure, and a
             list of the Turtle statements encoding the narrative (if successful)
    """
    logging.info(f'Creating narrative Turtle')
    graph_ttl_list = ttl_prefixes[:]
    # A dictionary holding the named entities encountered in the text - For reuse of the IRIs
    # Keys = the texts and Values are a tuple of the entity text and IRI
    nouns_dictionary = dict()
    for index in range(0, len(sentence_dicts)):
        sentence_text = sentence_dicts[index]['text']
        sentence_iri = f':Sentence_{str(uuid.uuid4())[:13]}'
        sentence_ttl_list = [f'{sentence_iri} a :Sentence ; :offset {sentence_dicts[index]["offset"]} .',
                             f'{sentence_iri} :text "{sentence_text}" .']
        # Capture whether the sentence is a question or exclamation; Future: Handle ! and ?
        if 'punct' in sentence_dicts[index]:
            if sentence_dicts[index]['punct'] == '?':
                sentence_ttl_list.append(f'{sentence_iri} a :Inquiry .')
            elif sentence_dicts[index]['punct'] == '!':
                sentence_ttl_list.append(f'{sentence_iri} a :ExpressiveAndExclamation .')
        named_entities = []
        if 'entities' in sentence_dicts[index]:
            named_entities = sentence_dicts[index]['entities']
        # Get a version of the sentence with co-references resolved, if needed
        need_coref = False
        for pers_pronoun in personal_pronouns:
            if f'{pers_pronoun} ' in sentence_text.lower() or f'{pers_pronoun}.' in sentence_text:
                need_coref = True
                break
        if need_coref:
            # TODO: Can this be improved? Too much previous text distorts pronomial de-referencing
            if index == 0:
                preceding_sentences = empty_string
            elif index == 1:
                preceding_sentences = sentence_dicts[0]['text']
            else:
                preceding_sentences = sentence_dicts[index - 2]['text'] + space + sentence_dicts[index - 1]['text']
            try:
                coref_dict = access_api(coref_prompt.replace('{sentences}', preceding_sentences)
                                        .replace("{sent_text}", sentence_text))
                updated_text = coref_dict['updated_text']
            except Exception:
                logging.error(f'Exception in getting coreference details for the text, {sentence_text}')
                continue
        else:
            updated_text = sentence_text
        # Get all the sentence details using OpenAI prompting
        try:
            get_sentence_details(sentence_iri, sentence_text, updated_text, sentence_ttl_list,
                                 empty_string, False, named_entities, nouns_dictionary)
            graph_ttl_list.extend(sentence_ttl_list)
        except Exception as e:   # Triples not added for sentence
            logging.error(f'Exception ({str(e)}) in getting sentence details for the text, {sentence_text}')
            continue
    # Add the quotation sentence details to the Turtle
    for quote_iri, quote_tuple in quote_dict.items():
        quote_text, attribution, entities = quote_tuple
        quote_ttl_list = [f'{quote_iri} a :Quote ; :text "{quote_text}" .']
        try:
            get_sentence_details(f'{quote_iri}', quote_text, quote_text, quote_ttl_list, attribution,
                                 True, entities, nouns_dictionary)
            graph_ttl_list.extend(quote_ttl_list)
        except Exception as e:    # Triples not added for quote
            logging.error(f'Exception ({str(e)}) in getting quote details for the text, {quote_text}')
            continue
    return True, graph_ttl_list
