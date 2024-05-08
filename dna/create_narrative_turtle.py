# Processing to create the Turtle rendering of the sentences in a narrative
#    where a narrative's sentences are parsed (by spaCy) into an array of Sentence instances
#    and the text is analyzed using OpenAI

import logging
import openai
import os
import re
from rdflib import Literal
from typing import List

from dna.process_entities import get_name_permutations
from dna.process_sentences import get_sentence_details
from dna.query_openai import access_api, coref_prompt
from dna.sentence_classes import Sentence, Quotation, Punctuation
from dna.utilities_and_language_specific import empty_string, personal_pronouns, space, ttl_prefixes, underscore


def _temp_preload() -> dict:
    temp_dict = dict()
    for text in ("House of Representatives", "House", "U.S. House of Representatives", "HOR",
                 "House of Representatives of the United States", "house.gov", "U.S. House",
                 "United States Congress House", "US HOR", "US House of Representatives", "USHOR",
                 "United States House of Representatives"):
        temp_dict[text] = ('ORG', ':House_of_Representatives')
    return temp_dict


def create_graph(sentence_instance_list: list, quotation_instance_list: list,
                 number_sentences: int = 10) -> (bool, list):
    """
    Using the instances of the Sentence Class defining each sentence in the narrative/article,
    create the Turtle rendering of the details.

    :param sentence_instance_list: An array of Sentence Class instances extracted from a narrative
    :param quotation_instance_list: An array of Quotation Class instances extracted from the original text
    :param number_sentences: An integer indicating the number of sentences to ingest (a number
                             greater than 1; by default up to 10 sentences are ingested)
    :return: A tuple consisting of a boolean indicating success (if true) or failure, an integer
             indicating the number of sentences processed, and a list of the Turtle statements
             encoding the narrative (if successful)
    """
    logging.info(f'Creating narrative Turtle')
    graph_ttl_list = ttl_prefixes[:]
    # A dictionary holding the named entities encountered in the text - For reuse of the IRIs
    #    due to co-reference/multiple reference
    # Keys = the texts and Values are a tuple of the entity text and IRI
    # TODO: Preload :Corrections from the ontology into nouns_dictionary AND the graph Turtle
    nouns_dictionary = _temp_preload()
    index = 0
    for index in range(0, len(sentence_instance_list)):
        if (index + 1) > number_sentences:    # Stop at the requested number of sentences (to be ingested)
            break
        sentence_iri = sentence_instance_list[index].iri
        sentence_text = sentence_instance_list[index].text
        sentence_ttl_list = [f'{sentence_iri} a :Sentence ; :offset {sentence_instance_list[index].offset} .',
                             f'{sentence_iri} :text {Literal(sentence_text).n3()} .']
        # Capture whether the sentence is a question or exclamation; Future: Handle ! and ?
        for punctuation in sentence_instance_list[index].punctuations:
            if punctuation == Punctuation.QUESTION:
                sentence_ttl_list.append(f'{sentence_iri} a :Inquiry .')
            elif punctuation == Punctuation.EXCLAMATION:
                sentence_ttl_list.append(f'{sentence_iri} a :ExpressiveAndExclamation .')
        # Get a version of the sentence with co-references resolved, if needed
        if any([(sentence_text.startswith(f'{pers_pronoun} '.title()) or f' {pers_pronoun} ' in sentence_text or
                 f'{pers_pronoun}.' in sentence_text) for pers_pronoun in personal_pronouns]):
            # TODO: Can this be improved? 2 previous sentences, but too much previous text distorts de-referencing
            preceding_sentences = empty_string
            if index == 1:
                preceding_sentences = sentence_instance_list[0].text
            elif index > 1:
                preceding_sentences = sentence_instance_list[index - 2].text + space + \
                                      sentence_instance_list[index - 1].text
            try:
                coref_dict = access_api(coref_prompt.replace('{sentences}', preceding_sentences)
                                        .replace("{sent_text}", sentence_text))
                if coref_dict['updated_text'] not in ('error', 'string'):
                    updated_text = coref_dict['updated_text']
                else:
                    updated_text = sentence_text
            except Exception:
                logging.error(f'Exception in getting coreference details for the text, {sentence_text}')
                continue
        else:
            updated_text = sentence_text
        # Get all the sentence details using OpenAI prompting
        try:
            get_sentence_details(sentence_instance_list[index], updated_text, sentence_ttl_list,
                                 False, nouns_dictionary)
            graph_ttl_list.extend(sentence_ttl_list)
        except Exception as e:   # Triples not added for sentence
            logging.error(f'Exception ({str(e)}) in getting sentence details for the text, {sentence_text}')
            continue
    # Add the quotation sentence details to the Turtle
    # Quotation analysis is not limited by the number of sentences to ingest
    for quotation in quotation_instance_list:
        quote_iri = quotation.iri
        quote_text = quotation.text
        quote_ttl_list = [f'{quote_iri} a :Quote ; :text {Literal(quote_text).n3()} .']
        try:
            get_sentence_details(quotation, quote_text, quote_ttl_list, True, nouns_dictionary)
            graph_ttl_list.extend(quote_ttl_list)
        except Exception as e:    # Triples not added for quote
            logging.error(f'Exception ({str(e)}) in getting quote details for the text, {quote_text}')
            continue
    return True, index, graph_ttl_list
