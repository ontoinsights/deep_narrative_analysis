# Processing to create the Turtle rendering of the sentences in a narrative
#    where a narrative's sentences are parsed (by spaCy) into an array of Sentence instances
#    and the text is analyzed using OpenAI

import logging
import openai
import os
import re
from rdflib import Literal
from typing import List

from dna.database import query_database
from dna.database_queries import query_corrections, query_manual_corrections
from dna.process_entities import get_name_permutations
from dna.process_sentences import get_sentence_details
from dna.query_openai import access_api, coref_prompt
from dna.sentence_classes import Sentence, Quotation, Punctuation
from dna.utilities_and_language_specific import empty_string, ner_dict, personal_pronouns, space, \
    ttl_prefixes, underscore


def _update_nouns(bindings: list, nouns_dictionary: dict):
    """
    Iterate through the query bindings and add the results to the nouns_dictionary.

    :param bindings: An array of query result bindings
    :param nouns_dictionary: A dictionary holding the details of any named entities that could be
             encountered in a narrative - For reuse of the IRI due to co-reference/multiple reference;
             Keys are the possible texts for the entity and their value is a tuple that is the spaCy
             NER type and its IRI
    :return: None (nouns_dictionary is updated)
    """
    for binding_set in bindings:
        entity_iri = f":{binding_set['s']['value'].split(':')[-1]}"
        entity_type = f"{binding_set['type']['value'].split(':')[-1]}"
        if entity_type == 'Correction':
            continue
        entity_ner = empty_string
        for key, value in ner_dict.items():
            if value == f':{entity_type}':     # TODO: Include the class hierarchy in eval (eg, GovEntity -> OrgEntity)
                entity_ner = key
                break
        if not entity_ner:
            continue
        nouns_dictionary[binding_set['label']['value']] = entity_ner, entity_iri
    return


def create_graph(sentence_instance_list: list, quotation_instance_list: list,
                 number_sentences: int, repo: str) -> (bool, list):
    """
    Using the instances of the Sentence Class defining each sentence in the narrative/article,
    create the Turtle rendering of the details.

    :param sentence_instance_list: An array of Sentence Class instances extracted from a narrative
    :param quotation_instance_list: An array of Quotation Class instances extracted from the original text
    :param number_sentences: An integer indicating the number of sentences to ingest (a number
                             greater than 1; by default up to 10 sentences are ingested)
    :param repo: String holding the repository name for the narrative graph
    :return: A tuple consisting of a boolean indicating success (if true) or failure, an integer
             indicating the number of sentences processed, and a list of the Turtle statements
             encoding the narrative (if successful)
    """
    logging.info(f'Creating narrative Turtle')
    graph_ttl_list = ttl_prefixes[:]
    # A dictionary holding the named entities encountered in the text - For reuse of the IRIs
    #    due to co-reference/multiple reference
    # Keys = the texts and Values = entity's spaCy NER type and its IRI
    nouns_dictionary = nouns_preload(repo)
    index = 0
    for index in range(0, len(sentence_instance_list)):
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
        updated_text = sentence_text
        sentence_type = 'mentions'
        if not (index + 1 > number_sentences):    # Detailed processing only up to the requested number of sentences
            sentence_type = 'complete'
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
                except Exception:
                    logging.error(f'Exception in getting coreference details for the text, {sentence_text}')
                    continue
        # Get the sentence details using OpenAI prompting
        try:
            get_sentence_details(sentence_instance_list[index], updated_text, sentence_ttl_list,
                                 sentence_type, nouns_dictionary, quotation_instance_list, repo)
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
            get_sentence_details(quotation, quote_text, quote_ttl_list, 'quote', nouns_dictionary, [], repo)
            graph_ttl_list.extend(quote_ttl_list)
        except Exception as e:    # Triples not added for quote
            logging.error(f'Exception ({str(e)}) in getting quote details for the text, {quote_text}')
            continue
    return True, index, graph_ttl_list


def nouns_preload(repo: str) -> dict:
    """
    Preload the nouns_dictionary with any named entities that are 'Corrections' (created manually or
    having been encountered in parsing previous narratives into the repository).

    :param repo: String holding the repository name for the narrative graph
    :return: A dictionary holding the details of any named entities that could be encountered in a
             narrative - For reuse of the IRI due to co-reference/multiple reference; Keys are the possible
             texts for the entity and their value is a tuple that is the spaCy NER type and its IRI
    """
    nouns_dict = dict()
    # Manually created corrections are stored in the default db graph
    corr_bindings = query_database('select', query_manual_corrections)
    _update_nouns(corr_bindings, nouns_dict)
    # Corrections recorded by previous parses in the repository's default graph
    corr_bindings = query_database('select', query_corrections.replace('?named', f':{repo}_default'))
    _update_nouns(corr_bindings, nouns_dict)
    return nouns_dict
