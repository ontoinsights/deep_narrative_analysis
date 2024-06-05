# Processing of Sentence instances using OpenAI

import copy
import logging
import re
import uuid
from rdflib import Literal
from typing import Union
from unidecode import unidecode

from dna.database import add_remove_data
from dna.nlp import nlp, get_head_word
from dna.sentence_element_classes import Associated, Event
from dna.process_entities import agent_classes, check_if_noun_is_known, process_ner_entities
from dna.query_openai import access_api, categories, coref_prompt, noun_categories, rhetorical_devices, noun_prompt,\
    noun_category_prompt, sentence_summary_prompt, sentence_devices_prompt, verbs_and_associateds_prompt, \
    semantics_prompt
from dna.sentence_classes import Sentence, Quotation, Entity
from dna.utilities_and_language_specific import empty_string, ner_dict, processed_prepositions, ttl_prefixes

future_true = '{:future true}'
negated_true = '{:negated true}'

semantic_roles = ("agent", "patient", "co-patient", "theme", "experiencer", "instrument", "cause", "content",
                  "beneficiary", "location", "time", "goal", "source", "state", "recipient", "measure")

semantic_role_mapping = {"agent": ":has_active_entity",
                         "beneficiary": ":has_affected_entity",
                         "cause": ":has_cause",
                         "content": ":has_aspect",
                         "co-patient": ":has_affected_entity",
                         "experiencer": ":has_active_entity",
                         "goal": ":has_destination",        # only for locations; goal of person -> has_affected_entity
                         "instrument": ":has_instrument",
                         "location": ":has_location",
                         "measure": ":has_quantification",
                         "patient": ":has_affected_entity",
                         "recipient": ":has_affected_entity",
                         "source": ":has_origin",
                         "state": ":has_quantification",    # TODO: Assess value/correctness
                         "subject": ":has_theme",
                         "theme": ":has_topic",             # affected_entity if an Agent
                         "time": ":has_time"}

env_and_condition = ':EnvironmentAndCondition'
knowledge = ':KnowledgeAndSkill'


def _get_associated_predicate(semantic_role: str, class_name: str):
    if semantic_role in ('patient', 'co-patient') and class_name not in agent_classes:
        return ':has_topic'
    elif semantic_role == 'goal':
        if class_name in agent_classes:
            return ':has_affected_entity'
        elif ':Location' not in class_name:
            return ':has_topic'
    elif semantic_role in semantic_roles:
        return semantic_role_mapping[semantic_role]
    return empty_string


def _sentence_semantics_processing(sentence_or_quotation: Union[Sentence, Quotation],
                                   updated_text: str, nouns_dict: dict, curr_turtle: list):
    """
    Logic to process the semantics of a sentence or quotation in a narrative/article. The current Turtle
    for the sentence is passed in and is updated.

    :param sentence_or_quotation: An instance of either the Sentence or Quotation Class
    :param updated_text: String holding the summary of a sentence or the original sentence text
    :param nouns_dict: A dictionary holding the nouns/named entities encountered in the narrative;
             The dictionary keys are the text for the noun, and its values are a tuple consisting
             of the spaCy entity type and the noun's IRI. An IRI value may be associated with
             more than 1 text.
    :param curr_turtle: Array holding the assembled Turtle statements for the current sentence
    :return: None (curr_turtle is updated)
    """
    sentence_iri = sentence_or_quotation.iri
    # Get the complete verb text and associated nouns and clauses
    verb_dict = access_api(
        verbs_and_associateds_prompt.replace('{sent_text}', updated_text.replace('[', '').replace(']', '')))
    #                      .replace('{verb_texts}', '", "'.join(sentence_or_quotation.verbs)))
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
            curr_turtle.append(f'{sentence_iri} :has_semantic {event_iri} .')
            curr_turtle.append(f'{sentence_iri} :future true .')
        else:
            curr_turtle.append(f'{sentence_iri} :has_semantic {event_iri} .')
        if event.class_names:
            # TODO: Other invalid combinations?
            if ':ArrestAndImprisonment' in event.class_names and ':AggressiveCriminalOrHostileAct' in event.class_names:
                event.class_names.remove(':AggressiveCriminalOrHostileAct')
            curr_turtle.append(f'{event_iri} a {", ".join(event.class_names)} ; :text {Literal(full_phrase).n3()} .')
        if event.negated_class_names:
            for negated_name in event.negated_class_names:
                curr_turtle.append(f'{event_iri} a {negated_name} ; :negated true ; '
                                   f':text {Literal(full_phrase).n3()} .')
        # Deal with the associated nouns and clauses
        for associated in associateds:
            assoc_text = associated['text']
            # Determine noun/clause semantics
            for semantic_role in associated['semantic_roles']:
                sem_role_lower = semantic_role.lower()
                if 'Quotation' in assoc_text:
                    for quote_topic in re.findall(r'Quotation[0-9]+', assoc_text):
                        curr_turtle.append(f'{event_iri} :has_topic :{quote_topic} .')
                    continue
                if sem_role_lower == 'content' and \
                        31 not in verb_semantic_dict['topics']:  # Not a simple env/condition verb
                    curr_turtle.append(f'{event_iri} :has_topic [ :text {Literal(assoc_text).n3()} ; a :Clause ] .')
                    continue
                if sem_role_lower == 'time':
                    # TODO: Time as NER
                    # check_text = unidecode(assoc_text.replace('.', empty_string))
                    # entity_type, noun_iri = check_if_noun_is_known(check_text, 'TIME', nouns_dict)
                    # if noun_iri:
                    #    curr_turtle.append(f'{event_iri} :has_time {noun_iri} .')
                    # else:
                    curr_turtle.append(f'{event_iri} :has_time [ :text {Literal(assoc_text).n3()} ; a :Time ] .')
                    continue
                # Deal with a preposition as the first word of the associated text
                if assoc_text.lower().split()[0] in processed_prepositions:
                    prep_text = ' '.join(assoc_text.split()[1:])
                else:
                    prep_text = assoc_text
                if ' and ' in prep_text or ' or ' in prep_text:
                    # TODO: Deal with multiple nouns in subjects and objects (conjunction or disjunction) and negations
                    head_text = prep_text    # TODO: Improve get_head_word to address this
                else:
                    head_text = get_head_word(prep_text)
                entity_type, noun_iri = check_if_noun_is_known(unidecode(head_text.replace('.', empty_string)),
                                                               empty_string, nouns_dict)
                if noun_iri:    # Already have the noun and its semantics captured; Set up for semantic role processing
                    noun_class_name = 'owl:Thing'
                    for ner_key in ner_dict.keys():
                        if ner_key in entity_type:
                            noun_class_name = ner_dict[ner_key]     # Should be able to override owl:Thing
                            break
                    # TODO: Add correct details for singular/plural and negated
                    assoc = Associated(assoc_text, noun_class_name, sem_role_lower, True, False, noun_iri)
                elif head_text in ("I", "we", "we"):    # OpenAI does not identify I/we as people
                    noun_class_name = ':Person'
                    singular = True
                    if head_text.lower() == 'we':
                        singular = False
                        noun_class_name += ', :Collection'
                    # TODO: Add correct details for negated
                    new_iri = f':Noun_{str(uuid.uuid4())[:13]}'
                    # TODO: Assumes that every 'I' is the same person; Is this valid?
                    nouns_dict[head_text] = empty_string, new_iri
                    curr_turtle.append(f'{new_iri} a {noun_class_name} ; :text {Literal(head_text).n3()} ; '
                                       f'rdfs:label {Literal(head_text).n3()} .')
                    assoc = Associated(assoc_text, noun_class_name, sem_role_lower, singular, False, new_iri)
                else:
                    noun_dict = access_api(noun_prompt.replace('{sent_text}', updated_text)
                                           .replace('{noun_text}', head_text))
                    noun_type = noun_dict['type']
                    noun_class_name = 'owl:Thing'
                    if 0 < noun_type < len(noun_categories) + 1:
                        noun_class_name = noun_categories[noun_type - 1]
                    else:
                        logging.error(f'Invalid noun type ({noun["type"]}) for {assoc_text}')
                    if noun_class_name == 'owl:Thing':  # Check if the noun is an event or state
                        noun_event_dict = access_api(noun_category_prompt.replace('{sent_text}', updated_text)
                                                     .replace('{noun_text}', head_text))
                        if 'category_number' in noun_event_dict and \
                                (0 < noun_event_dict['category_number'] < len(categories)):
                            noun_class_name = categories[noun_event_dict['category_number'] - 1]
                    # Add to the nouns_dictionary
                    new_iri = f':Noun_{str(uuid.uuid4())[:13]}'
                    nouns_dict[head_text.replace('.', empty_string)] = empty_string, new_iri
                    nouns_dict[assoc_text] = empty_string, new_iri
                    curr_turtle.append(f'{new_iri} a {noun_class_name} ; :text {Literal(assoc_text).n3()} ; '
                                       f'rdfs:label {Literal(assoc_text).n3()} .')
                    # Create an instance of the Associated class to hold the details
                    assoc = Associated(assoc_text, noun_class_name, sem_role_lower, noun_dict['singular'],
                                       noun_dict['negated'], new_iri)
                _update_turtle(assoc, event, nouns_dict, curr_turtle)
    return


def _update_turtle(assoc: Associated, event: Event, nouns_dict: dict, curr_turtle: list):
    """
    Logic to create the appropriate predicate for the noun relationships to the sentence's
    verb/semantic, as well as adding details for a truncated passive.

    :param assoc: Instance of an Associated Class for the event/verb
    :param event: Instance of an Event Class
    :param nouns_dict: A dictionary holding the nouns/named entities encountered in the narrative;
             The dictionary keys are the text for the noun, and its values are a tuple consisting of the
             spaCy entity type and the noun's IRI. An IRI value may be associated with more than 1 text.
    :param curr_turtle: Array holding the assembled Turtle statements for the current sentence
    :return: N/A (curr_turtle is updated)
    """
    class_name = assoc.class_name
    event_iri = event.iri
    semantic_role = assoc.semantic_role.lower()
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
        elif semantic_role.lower() in ('agent', 'experiencer') and knowledge in event_classes:
            curr_turtle.append(f'{event_iri} :has_active_entity {reference_iri} .')
        elif (semantic_role.lower() in ('agent', 'experiencer') and knowledge not in event_classes) or \
                class_name in agent_classes:
            curr_turtle.append(f'{event_iri} :has_described_entity {reference_iri} .')
        else:
            predicate = _get_associated_predicate(semantic_role, class_name)
            if not predicate:
                logging.error(f'Unknown semantic role: {semantic_role} in text: {assoc.text}')
            else:
                curr_turtle.append(f'{event_iri} {predicate} {reference_iri} .')
    # elif ':LineOfBusiness' in class_name:
    #     curr_turtle.append(f'{event_iri} :has_location {reference_iri} .')
    elif ':Affiliation' in event_classes:
        if reference_iri != assoc.iri and class_name in agent_classes:
            # Is a specific proper noun referenced in the text?
            for ent in nlp(assoc.text).ents:
                # The entity should already have been processed in the sentence
                # TODO: What if there are 2+ proper nouns?
                check_text = unidecode(ent.text.replace('.', empty_string))
                entity_type, noun_iri = check_if_noun_is_known(check_text, empty_string, nouns_dict)
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
            logging.error(f'Unknown semantic role: {semantic_role} in text: {assoc.text}')
        else:
            curr_turtle.append(f'{event_iri} {predicate} {reference_iri} .')
    return


def get_sentence_details(sentence_or_quotation: Union[Sentence, Quotation], updated_text: str, ttl_list: list,
                         sentence_type: str, nouns_dict: dict, quotation_list: list, repo: str):
    """
    Retrieve sentence (or quotation) details using the OpenAI API and create the sentence
    (or quotation) level Turtle.

    :param sentence_or_quotation: An instance of either the Sentence or Quotation Class
    :param updated_text: String holding the sentence/quotation text if anaphora (co-references) are
                         de-referenced; Otherwise is the original sentence/quotation text
    :param ttl_list: The current Turtle definition where the new declarations will be stored
    :param sentence_type: String indicating that the processing is for a complete sentence ('complete'),
                          to record mentions ('mentions') or for a quotation ('quote')
    :param nouns_dict: A dictionary holding the nouns/named entities encountered in the narrative;
             The dictionary keys are the text for the noun, and its values are a tuple consisting
             of the spaCy entity type and the noun's IRI. An IRI value may be associated with
             more than 1 text.
    :param quotation_list: An array of Quotation instances in case any are referenced in the sentence
    :param repo: String holding the repository name for the narrative graph
    :return: N/A (ttl_list is updated with the details from OpenAI)
    """
    sentence_iri = sentence_or_quotation.iri
    sentence_text = sentence_or_quotation.text
    # Get named entities for a sentence, including its quotations
    entity_iris = []
    entity_ttls = []
    named = False
    if '[Quotation' in sentence_text:   # Processing Quotation NEs
        quote_indices = []
        for quotation in re.findall(r'Quotation[0-9]+', sentence_text):
            ttl_list.append(f'{sentence_iri} :has_component :{quotation} .')
            quote_indices.append(quotation.split('Quotation')[1])
        if quote_indices:
            for i in range(0, len(quote_indices)):
                if quotation_list[int(quote_indices[i])].entities:
                    named = True
                    new_iris, new_ttl = \
                        process_ner_entities(quotation_list[int(quote_indices[i])].text,
                                             quotation_list[int(quote_indices[i])].entities, nouns_dict)
                    entity_iris.extend(new_iris)
                    entity_ttls.extend(new_ttl)
    if sentence_or_quotation.entities and sentence_type != 'quote':    # Already processed entities for a quotation
        if sentence_or_quotation.entities:   # Processing Sentence NEs
            named = True
            new_iris, new_ttl = \
                process_ner_entities(sentence_text, sentence_or_quotation.entities, nouns_dict)
            entity_iris.extend(new_iris)
            entity_ttls.extend(new_ttl)
    if named:
        if entity_ttls:
            ttl_list.extend(entity_ttls)
            logging.info('Loading NER Turtle')
            ner_ttl = ttl_prefixes[:]
            ner_ttl.extend(entity_ttls)
            # Add new entities to the repo's default graph
            msg = add_remove_data('add', ' '.join(ner_ttl), repo)
            if msg:
                logging.info('Error adding new entity: ', ner_ttl)
        for entity_iri in entity_iris:
            ttl_list.append(f'{sentence_iri} :mentions {entity_iri} .')
    # Capture a quotation's attribution
    if sentence_type == 'quote' and sentence_or_quotation.attribution:
        attrib_text = sentence_or_quotation.attribution
        for ent in nlp(sentence_or_quotation.attribution).ents:
            if ent.label_ == 'PERSON':
                attrib_text = ent.text
                break
        attrib_type, attrib_iri = check_if_noun_is_known(unidecode(attrib_text.replace('.', empty_string)),
                                                         'PERSON', nouns_dict)
        if attrib_iri:
            ttl_list.append(f'{sentence_iri} :attributed_to {attrib_iri} .')
    # Processing the summary prompt for details such as sentiment, summary and grade level
    sent_dict = access_api(sentence_summary_prompt.replace("{sent_text}", updated_text))
    if sent_dict:   # Might not get reply from OpenAI
        if sent_dict['summary'] not in ('error', 'string'):
            summary = sent_dict['summary']
            ttl_list.append(f'{sentence_iri} :summary "{summary}" .')
            if len(updated_text.split()) > 10:
                coref_dict = access_api(coref_prompt.replace('{sentences}', empty_string)
                                        .replace("{sent_text}", summary))
                if coref_dict['updated_text'] not in ('error', 'string'):
                    eval_text = coref_dict['updated_text']
                else:
                    eval_text = summary
            else:
                eval_text = updated_text
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
                        device_numb = int(device_detail['device_number'])
                        # TODO: Pending pystardog fix;
                        #       predicate = ':rhetorical_device {:evidence "' + device_detail['evidence'] + '"}'
                        predicate = f':rhetorical_device_{rhetorical_devices[device_numb - 1].replace(" ", "_")}'
                        ttl_list.append(f'{sentence_iri} :rhetorical_device "{rhetorical_devices[device_numb - 1]}" .')
                        evidence = device_detail['evidence']
                        ttl_list.append(f'{sentence_iri} {predicate} "{evidence}" .')
                    else:
                        logging.error(f'Invalid rhetorical device ({device_numb}) for sentence, {sentence_text}')
                        continue
    # Processing the events and states, and related nouns
    if sentence_type == 'complete':
        _sentence_semantics_processing(sentence_or_quotation, eval_text, nouns_dict, ttl_list)
    return
