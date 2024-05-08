# Processing of Sentence instances using OpenAI

import logging
import re
import uuid
from rdflib import Literal
from typing import Union

from dna.nlp import nlp
from dna.sentence_element_classes import Associated, Event
from dna.process_entities import agent_classes, check_if_noun_is_known, process_ner_entities
from dna.query_openai import access_api, categories, noun_categories, rhetorical_devices, noun_prompt,\
    noun_category_prompt, sentence_summary_prompt, sentence_devices_prompt, verbs_and_associateds_prompt, \
    semantics_prompt
from dna.sentence_classes import Sentence, Quotation, Entity
from dna.utilities_and_language_specific import empty_string, ner_dict

future_true = '{:future true}'
negated_true = '{:negated true}'

semantic_roles = ("agent", "patient", "theme", "experiencer", "instrument", "cause", "content", "beneficiary",
                  "location", "time", "goal", "source", "recipient", "measure")

semantic_role_mapping = {"agent": ":has_active_entity",
                         "beneficiary": ":has_affected_entity",
                         "cause": ":has_cause",
                         "content": ":has_aspect",
                         "experiencer": ":has_active_entity",
                         "goal": ":has_destination",   # only for locations; goal of person -> has_affected_entity
                         "instrument": ":has_instrument",
                         "location": ":has_location",
                         "measure": ":has_quantification",
                         "patient": ":has_affected_entity",
                         "recipient": ":has_affected_entity",
                         "source": ":has_origin",
                         "theme": ":has_topic",    # affected_entity if an Agent
                         "time": ":has_time"}

env_and_condition = ':EnvironmentAndCondition'
knowledge = ':KnowledgeAndSkill'


def _get_associated_predicate(semantic_role: str, class_name: str):
    if semantic_role == 'patient' and class_name not in agent_classes:
        return ':has_topic'
    elif semantic_role == 'goal' and class_name in agent_classes:
        return ':has_affected_entity'
    elif semantic_role in semantic_roles:
        return semantic_role_mapping[semantic_role]
    return empty_string


def _sentence_semantics_processing(sentence_or_quotation: Union[Sentence, Quotation],
                                   updated_text: str, nouns_dict: dict, curr_turtle: list):
    """
    Logic to process the semantics of a sentence or quotation in a narrative/article. The current Turtle
    for the sentence is passed in and is updated.

    :param sentence_or_quotation: An instance of either the Sentence or Quotation Class
    :param updated_text: String holding the sentence text if anaphora (co-references) are de-referenced
             or holding a summary of a quote; Otherwise is the original sentence_text
    :param nouns_dict: A dictionary holding the nouns/named entities encountered in the narrative;
             The dictionary keys are the text for the noun, and its values are a tuple consisting
             of the spaCy entity type and the noun's IRI. An IRI value may be associated with
             more than 1 text.
    :param curr_turtle: Array holding the assembled Turtle statements for the current sentence
    :return: None (curr_turtle is updated)
    """
    sentence_iri = sentence_or_quotation.iri
    sentence_nouns_dict = dict(nouns_dict)
    # Get the complete verb text and associated nouns and clauses
    verb_dict = access_api(verbs_and_associateds_prompt.replace('{sent_text}', updated_text)
                           .replace('{verb_texts}', '", "'.join(sentence_or_quotation.verbs)))
    verb_phrases = list(set([verb['full_verb_phrase'] for verb in verb_dict['verbs']]))
    # Get the semantic topics for the verbs
    semantics_dict = access_api(semantics_prompt.replace('{sent_text}', updated_text)
                                .replace('{verb_phrases}', '", "'.join(verb_phrases)))
    for verb in verb_dict['verbs']:
        full_phrase = verb['full_verb_phrase']
        associateds = [] if 'associateds' not in verb else verb['associateds']
        verb_semantic_dict = dict()    # Will eventually hold the semantic topic results specific to the verb phrase
        # Match the semantic topic results with the verb
        for verb_semantic in semantics_dict['verbs']:
            if verb_semantic['verb_phrase_text'] == full_phrase:
                verb_semantic_dict = verb_semantic
                break
        if not verb_semantic_dict:    # Mismatch in OpenAI results; Verb phrase lost; Skip
            continue
        # Create an instance of the Event class to hold all the details
        event = Event(verb, verb_semantic_dict, updated_text)
        # Create the Turtle for the verb phrase and its semantics
        event_iri = event.iri
        if event.future:
            curr_turtle.append(f'{sentence_iri} :has_semantic {future_true} {event_iri} .')
        else:
            curr_turtle.append(f'{sentence_iri} :has_semantic {event_iri} .')
        if event.class_names:
            curr_turtle.append(f'{event_iri} a {", ".join(event.class_names)} ; :text {Literal(full_phrase).n3()} .')
        if event.negated_class_names:
            curr_turtle.append(f'{event_iri} a {negated_true} {", ".join(event.negated_class_names)} ; '
                               f':text {Literal(full_phrase).n3()} .')
        # Deal with the associated nouns and clauses
        for associated in associateds:
            # TODO: Deal with multiple nouns in subjects and objects (conjunction or disjunction) and negations
            assoc_text = associated['text']
            # Determine noun/clause semantics and trigger text
            for semantic_role in associated['semantic_roles']:
                sem_role_lower = semantic_role.lower()
                if sem_role_lower == 'content' and \
                        31 not in verb_semantic_dict['topics']:  # Not a simple env/condition verb
                    curr_turtle.append(f'{event_iri} :has_topic [ :text {Literal(assoc_text).n3()} ; a :Clause ] .')
                    continue
                elif sem_role_lower == 'time':
                    # TODO: Time as NER
                    # entity_type, noun_iri = check_if_noun_is_known(assoc_text, empty_string, nouns_dict)
                    # if noun_iri:
                    #    curr_turtle.append(f'{event_iri} :has_time {noun_iri} .')
                    # else:
                    curr_turtle.append(f'{event_iri} :has_time [ :text {Literal(assoc_text).n3()} ; a :Time ] .')
                    continue
                noun_dict = access_api(noun_prompt.replace('{sent_text}', updated_text)
                                       .replace('{noun_text}', assoc_text).replace('{semantic_role}', sem_role_lower))
                # Just using the shorter of the text or the trigger words, the noun might be found
                # TODO: Deal with other nouns than just the trigger text
                noun_text = noun_dict['selected_text'] if len(noun_dict['selected_text']) <= len(assoc_text) \
                    else assoc_text
                entity_type, noun_iri = check_if_noun_is_known(noun_text, empty_string, sentence_nouns_dict)
                if noun_iri:    # Already have the noun and its semantics captured; Set up for further processing
                    noun_class_name = 'owl:Thing'
                    for ner_key in ner_dict.keys():
                        if ner_key in entity_type:
                            noun_class_name = ner_dict[ner_key]     # Should always be able to override owl:Thing
                            break
                    assoc = Associated(noun_text, assoc_text, noun_class_name, sem_role_lower,
                                       True if 'PLURAL' not in entity_type else False, noun_dict['negated'], noun_iri)
                else:
                    noun_type = noun_dict['type']
                    noun_class_name = 'owl:Thing'
                    if 0 < noun_type < len(noun_categories) + 1:
                        noun_class_name = noun_categories[noun_type - 1]
                    else:
                        logging.error(f'Invalid noun type ({noun["type"]}) for {assoc_text}')
                    if noun_class_name == 'owl:Thing':  # Check if the noun is "I", "we" or an event or state
                        if noun_text in ("I", "we", "we"):    # OpenAI does not identify I/we as people
                            noun_class_name = ':Person'
                            if noun_text.lower() == 'we':
                                noun_text += ', :Collection'
                        else:
                            noun_event_dict = access_api(noun_category_prompt.replace('{sent_text}', updated_text)
                                                        .replace('{noun_text}', assoc_text))
                            if 'category_number' in noun_event_dict and (0 < noun_event_dict['category_number']
                                                                        < len(categories)):
                                noun_class_name = categories[noun_event_dict['category_number'] - 1]
                    # Create an instance of the Associated class to hold the details
                    assoc = Associated(noun_text, assoc_text, noun_class_name, sem_role_lower, noun_dict['singular'],
                                       noun_dict['negated'], empty_string)
                _update_turtle(assoc, event, sentence_nouns_dict, curr_turtle)
    return


def _update_turtle(assoc: Associated, event: Event, sentence_nouns_dict: dict, curr_turtle: list):
    """
    Logic to create the appropriate predicate for the noun relationships to the sentence's
    verb/semantic, as well as adding details for a truncated passive.

    :param assoc: Instance of an Associated Class for the event/verb
    :param event: Instance of an Event Class
    :param nouns_dict: A dictionary holding the nouns/named entities encountered in the narrative;
             The dictionary keys are the text for the noun, and its values are a tuple consisting
             of the spaCy entity type and the noun's IRI. An IRI value may be associated with
             more than 1 text.
    :param curr_turtle: Array holding the assembled Turtle statements for the current sentence
    :return: N/A (curr_turtle is updated)
    """
    class_name = assoc.class_name
    event_iri = event.iri
    semantic_role = assoc.semantic_role.lower()
    # TODO: How is negated handled for a noun? Edge property?
    if not assoc.iri:
        reference_iri = f':Noun_{str(uuid.uuid4())[:13]}'
        curr_turtle.append(f'{reference_iri} a {class_name} ; :text {Literal(assoc.trigger_text).n3()} ; '
                           f'rdfs:label {Literal(assoc.full_text).n3()} .')
        sentence_nouns_dict[assoc.trigger_text] = empty_string, reference_iri
    else:
        reference_iri = assoc.iri
    # TODO: Other mapping rules?
    # TODO: Match text with "content" role to another event?
    event_classes = list(event.class_names)
    event_classes.extend(event.negated_class_names)
    if len(event_classes) == 1 and ':Measurement' in event_classes:
        curr_turtle.append(f'{event_iri} :has_quantification {reference_iri} .')
    elif len(event_classes) == 1 and (env_and_condition in event_classes or knowledge in event_classes):
        if ':LineOfBusiness' in class_name or ':EthnicGroup' in class_name or \
                ':PoliticalGroup' in class_name or ':ReligiousGroup' in class_name:
            curr_turtle.append(f'{event_iri} :has_aspect {reference_iri} .')
        elif semantic_role.lower() in ('agent', 'experiencer') or class_name in agent_classes:
            curr_turtle.append(f'{event_iri} :has_described_entity {reference_iri} .')
        else:
            predicate = _get_associated_predicate(semantic_role, class_name)
            if not predicate:
                logging.error(f'Unknown semantic role: {noun_role} in text: {assoc.text}')
            else:
                curr_turtle.append(f'{event_iri} {predicate} {reference_iri} .')
    # elif ':LineOfBusiness' in class_name:
    #     curr_turtle.append(f'{event_iri} :has_location {reference_iri} .')
    elif ':Affiliation' in event_classes:
        if reference_iri != assoc.iri and class_name in agent_classes:
            # Is a specific proper noun referenced in the text?
            for ent in nlp(assoc.trigger_text).ents:
                # The entity should already have been processed in the sentence
                # TODO: What if there are 2+ proper nouns?
                entity_type, noun_iri = check_if_noun_is_known(ent.text, empty_string, nouns_dict)
                reference_iri = noun_iri if noun_iri else reference_iri
        if semantic_role == 'agent':
            curr_turtle.append(f'{event_iri} :has_active_entity {reference_iri} .')
        elif class_name in agent_classes:
            curr_turtle.append(f'{event_iri} :affiliated_with {reference_iri} .')
        else:
            curr_turtle.append(f'{event_iri} :has_described_entity {reference_iri} .')
    else:
        predicate = _get_associated_predicate(semantic_role, class_name)
        if not predicate:
            logging.error(f'Unknown semantic role: {noun_role} in text: {assoc.text}')
        else:
            curr_turtle.append(f'{event_iri} {predicate} {reference_iri} .')
    return


def get_sentence_details(sentence_or_quotation: Union[Sentence, Quotation], updated_text: str, ttl_list: list,
                         for_quote: bool, nouns_dict: dict):
    """
    Retrieve sentence (or quotation) details using the OpenAI API and create the sentence
    (or quotation) level Turtle.

    :param sentence_or_quotation: An instance of either the Sentence or Quotation Class
    :param updated_text: String holding the sentence/quotation text if anaphora (co-references) are de-referenced;
                         Otherwise is the original sent_text
    :param ttl_list: The current Turtle definition where the new declarations will be stored
    :param for_quote: Boolean indicating that the processing is for a quotation (if True)
    :param nouns_dict: A dictionary holding the nouns/named entities encountered in the narrative;
             The dictionary keys are the text for the noun, and its values are a tuple consisting
             of the spaCy entity type and the noun's IRI. An IRI value may be associated with
             more than 1 text.
    :return: N/A (ttl_list is updated with the details from OpenAI)
    """
    sentence_iri = sentence_or_quotation.iri
    sentence_text = sentence_or_quotation.text
    # Handle named entities
    if sentence_or_quotation.entities:
        entity_iris, entity_ttl = process_ner_entities(sentence_text, sentence_or_quotation.entities, nouns_dict)
        ttl_list.extend(entity_ttl)
        for entity_iri in entity_iris:
            ttl_list.append(f'{sentence_iri} :mentions {entity_iri} .')
    # Capture a quotation's attribution
    if for_quote and sentence_or_quotation.attribution:
        attrib_type, attrib_iri = check_if_noun_is_known(sentence_or_quotation.attribution, 'PERSON', nouns_dict)
        if attrib_iri:
            ttl_list.append(f'{sentence_iri} :attributed_to {attrib_iri} .')
    elif not for_quote:     # Not a quotation but one may be referenced in sentence
        for quote_text in re.findall(r'Quotation[0-9]+', sentence_text):
            ttl_list.append(f'{sentence_iri} :has_component :{quote_text} .')
    # Processing the summary prompt for details such as sentiment, summary and grade level
    sent_dict = access_api(sentence_summary_prompt.replace("{sent_text}", sentence_text))
    summary = empty_string
    if sent_dict:   # Might not get reply from OpenAI
        if sent_dict['summary'] not in ('error', 'string'):
            summary = sent_dict['summary']
            ttl_list.append(f'{sentence_iri} :summary "{summary}" .')
        if sent_dict['sentiment'] in ('positive', 'negative', 'neutral'):
            sentiment = sent_dict['sentiment']
            ttl_list.append(f'{sentence_iri} :sentiment "{sentiment}" .')
        if type(sent_dict['grade_level']) is int:
            ttl_list.append(f'{sentence_iri} :grade_level {sent_dict["grade_level"]} .')
    # Processing for rhetorical devices
    sent_dict = access_api(sentence_devices_prompt.replace("{sent_text}", sentence_text))
    if sent_dict:   # Might not get reply from OpenAI or there are no rhetorical devices
        if 'rhetorical_devices' in sent_dict and len(sent_dict['rhetorical_devices']) > 0:
            for device_detail in sent_dict['rhetorical_devices']:
                if type(device_detail['device_number']) is int or device_detail['device_number'].isdigit():
                    device_numb = int(device_detail['device_number'])
                    if 0 < device_numb < len(rhetorical_devices) + 1:
                        predicate = ':rhetorical_device {:evidence "' + device_detail['evidence'] + '"} '
                        ttl_list.append(f'{sentence_iri} {predicate} "{rhetorical_devices[device_numb - 1]}" .')
                    else:
                        logging.error(f'Invalid rhetorical device ({device_numb}) for sentence, {sentence_text}')
                        continue
    # Processing the events and states, and related nouns - Details of quotations are NOT analyzed
    if not for_quote:
        _sentence_semantics_processing(sentence_or_quotation, updated_text, nouns_dict, ttl_list)
    return
