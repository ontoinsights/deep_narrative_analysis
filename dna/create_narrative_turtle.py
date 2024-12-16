# Processing to create the Turtle rendering of the sentences in a narrative
#    where a narrative's sentences are parsed (by spaCy) into an array of Sentence instances
#    and the text is analyzed using OpenAI

import logging
from dataclasses import dataclass

import openai
import os
import re
import traceback
from typing import List

from dna.database import query_database
from dna.database_queries import query_corrections, query_manual_corrections
from dna.process_sentences import EventsAndNouns, get_sentence_details, situation_semantics_processing
from dna.prompting_ontology_details import event_categories, political_event_categories, event_category_texts, \
    political_event_category_texts, political_event_category_replacements, noun_categories, noun_category_texts
from dna.sentence_classes import Sentence, Punctuation
from dna.utilities_and_language_specific import empty_string, literal, ner_dict, personal_pronouns, space, \
    ttl_prefixes, underscore
from dna.query_openai import access_api, narrative_chronology_prompt


@dataclass
class GraphResults:
    """
    Dataclass holding the results of the create_graph function
    """
    success: bool              # Success boolean
    number_processed: int      # Integer indicating the number of sentences processed
    turtle: list               # List of the Turtle statements encoding the narrative (if successful)


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
            if key == 'NORP':
                for class_type in (':Ethnicity', ':ReligiousGroup', ':PoliticalGroup',
                                   ':PoliticalIdeology', ':ReligiousBelief', ':GroupOfAgents'):
                    if class_type == f':{entity_type}':
                        entity_ner = class_type
                        break
            elif value == f':{entity_type}':   # TODO: (Future) Address class hierarchies such as GovEntity->OrgEntity
                entity_ner = key
                break
        if not entity_ner:
            continue
        nouns_dictionary[binding_set['label']['value']] = entity_ner, entity_iri
    return


def create_graph(sentence_instance_list: list, quotation_instance_list: list, narr: str, narr_id: str,
                 subject_areas: list, number_sentences: int, repo: str) -> GraphResults:
    """
    Based on the sentences and quotations, create the Turtle rendering of the details.

    :param sentence_instance_list: An array of Sentence Class instances extracted from a narrative
    :param quotation_instance_list: An array of Quotation Class instances extracted from a narrative
    :param narr: The text of the narrative to be analyzed
    :param narr_id: The IRI identifying the narrative
    :param subject_areas: A list of the subject areas of the narrative, as defined by OpenAI
    :param number_sentences: An integer indicating the number of sentences to fully ingest (a number
            greater than 1; by default up to 10 sentences are ingested)
    :param repo: String holding the repository name for the narrative graph
    :return: Instance of the GraphResults dataclass
    """
    logging.info(f'Creating narrative Turtle')
    graph_ttl_list = ttl_prefixes[:]
    # A dictionary holding the named entities encountered in the text - For reuse of the IRIs
    #    due to co-reference/multiple reference
    # Keys = the texts and Values = entity's spaCy NER type and its IRI
    nouns_dictionary = nouns_preload(repo)
    for index, sentence_instance in enumerate(sentence_instance_list):
        sentence_iri = sentence_instance.iri
        original_text = sentence_instance.text
        sentence_ttl_list = [f'{narr_id} :has_component {sentence_iri} .',
                             f'{sentence_iri} a :Sentence ; :offset {sentence_instance.offset} .',
                             f'{sentence_iri} :text {literal(original_text)} .']
        # TODO: (Future) Should DNA Capture whether the sentence is a question or exclamation?
        # for punctuation in sentence_instance_list[index].punctuations:
        #     if punctuation == Punctuation.QUESTION:
        #         sentence_ttl_list.append(f'{sentence_iri} a :Inquiry .')
        #     elif punctuation == Punctuation.EXCLAMATION:
        #         sentence_ttl_list.append(f'{sentence_iri} a :ExpressiveAndExclamation .')
        try:
            get_sentence_details(sentence_instance, sentence_ttl_list,'sentence', nouns_dictionary, repo)
            graph_ttl_list.extend(sentence_ttl_list)
        except Exception as e:
            logging.error(f'Exception ({str(e)}) in getting sentence details for the text, {original_text}')
            print(traceback.format_exc())
            continue
        # if index < number_sentences:    # TODO: Full processing only up to the requested number of sentences
    # Get the events/situations from the narrative
    chronology_dict = access_api(narrative_chronology_prompt.replace("{narr_text}", narr))
    if 'events_situations' in chronology_dict:
        # Get the event categories given the article's subject_areas
        # TODO: Generalize for all subject areas
        events = event_categories[:]
        event_texts = event_category_texts
        if 'political and international' in subject_areas:
            events = event_categories[:-1] + political_event_categories + [':EventAndState']
            event_texts = event_category_texts[:-1] + political_event_category_texts + ['other']
            for key, value in political_event_category_replacements:
                event_texts = event_texts.replace(key, value)
        # And add the noun information and get numbered lists
        nouns = events[:-1] + noun_categories
        noun_texts = event_texts[:-1] + noun_category_texts
        numbered_events = " ".join([f'{index}. {text}' for index, text in enumerate(event_texts, start=1)])
        numbered_nouns = " ".join([f'{index}. {text}' for index, text in enumerate(noun_texts, start=1)])
        events_and_nouns = EventsAndNouns(events, numbered_events, nouns, numbered_nouns)
        try:
            semantics_ttl = \
                situation_semantics_processing(chronology_dict['events_situations'], events_and_nouns,
                                               narr_id, subject_areas, nouns_dictionary)
            graph_ttl_list.extend(semantics_ttl)
        except Exception as e:
            logging.error(f'Exception ({str(e)}) in getting sentence semantics for the text')
            print(traceback.format_exc())
    logging.info(f'Narrative Turtle created')
    # Add the quotation details to the Turtle
    for quote in quotation_instance_list:
        quote_ttl_list = [f'{quote.iri} a :Quote ; :text {literal(quote.text)} .']
        try:
            get_sentence_details(quote, quote_ttl_list, 'quote', nouns_dictionary, repo)
            graph_ttl_list.extend(quote_ttl_list)
        except Exception as e:    # Triples not added for quote
            logging.error(f'Exception ({str(e)}) in getting quote details for the text, {quotation.text}')
            print(traceback.format_exc())
            continue
    return GraphResults(True, len(sentence_instance_list), graph_ttl_list)


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
