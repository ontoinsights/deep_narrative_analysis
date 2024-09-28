# Processing of Sentence instances using OpenAI

import copy
import logging
import re
import uuid
from dataclasses import dataclass
from rdflib import Literal
from typing import Union
from unidecode import unidecode

from dna.database import add_remove_data
from dna.nlp import get_entities
from dna.process_entities import agent_classes, check_if_noun_is_known, process_ner_entities
from dna.query_openai import (access_api, coref_prompt, event_categories, events_prompt,
                              noun_categories, noun_categories_prompt, rhetorical_devices, sentence_prompt)
from dna.sentence_classes import Sentence, Quotation, Entity
from dna.utilities_and_language_specific import empty_string, honorifics, modals, ner_dict, ttl_prefixes

agent_classes_without_plant = [element for element in agent_classes if ':Plant' not in element]

location_business = (':Location', ':GeopoliticalEntity', ':LineOfBusiness')

measurement = (':Assessment', ':Measurement')

modal_mapping = {'can-present': ':ReadinessAndAbility',              # Ex: I can swim.
                 'can-not-present': ':OpportunityAndPossibility',    # Ex: I can visit tomorrow.
                 'could-past': ':ReadinessAndAbility',               # Ex: I could skate when I was younger.
                 'could-not-past': ':OpportunityAndPossibility',     # Ex: It could rain tomorrow.
                 'have to': ':AdviceAndRecommendation',              # Ex: You have to leave.
                 'may': ':OpportunityAndPossibility',                # Ex: It may rain.
                 'might': ':OpportunityAndPossibility',              # Ex: It might rain.
                 'must': ':RequirementAndDependence',                # Ex: I must leave.
                 'ought to': ':AdviceAndRecommendation',             # Ex: You ought to leave.
                 'shall': ':RequirementAndDependence',               # Ex: You shall go to the store.
                 'should': ':AdviceAndRecommendation',               # Ex: They should go to the store.
                 'would': ':OpportunityAndPossibility'}              # Ex: I would take the train if possible.

# TODO: (Future) co-agent, co-patient
semantic_roles = ("affiliation", "agent", "patient", "content", "theme", "experiencer", "instrument", "cause",
                  "location", "time", "goal", "source", "state", "subject", "recipient", "measure", "attribute")

semantic_role_mapping = {"affiliation": ":affiliated_with",
                         "agent": ":has_active_entity",
                         "attribute": ":has_aspect",
                         "beneficiary": ":has_affected_entity",
                         "cause": ":has_cause",
                         "content": ":has_context",
                         # "co-agent": ":has_active_entity",
                         # "co-patient": ":has_affected_entity",
                         "experiencer": ":has_active_entity",
                         "goal": ":has_destination",        # only for locations; goal of person -> has_affected_entity
                         "instrument": ":has_instrument",
                         "location": ":has_location",
                         "measure": ":has_quantification",
                         "patient": ":has_affected_entity",
                         "recipient": ":has_recipient",     # for locations -> has_destination
                         "source": ":has_origin",
                         "state": ":has_aspect",
                         "subject": ":has_context",
                         "theme": ":has_topic",
                         "time": ":has_time"}

@dataclass
class VerbDetails:
    category: int
    same_opposite: str
    correctness: int
    iri: str


def _deal_with_sem_roles(event_iri: str, verb_details: dict, sentence_noun_dict: dict, event_class: str,
                         nouns_dict: dict) -> list:
    """
    Get the class details and appropriate relationship/predicate for nouns related to an
    event or state via a variety of semantic roles.

    :param event_iri: The IRI identifying the event
    :param verb_details: Dictionary with key = verb text and value = VerbDetails dataclass
    :param sentence_noun_dict: See query_openai's noun_categories_result for the key, "sentence_nouns"
    :param event_classes: A string identifying the DNA class name applicable to the event/state
    :param nouns_dict: A dictionary holding the nouns/named entities encountered in the narrative;
             The dictionary keys are the text for the noun, and its values are a tuple consisting
             of the spaCy entity type and the noun's IRI. An IRI value may be associated with
             more than 1 text.
    :return: An array holding the Turtle for the event's associated nouns
    """
    roles_ttl = []
    for noun_detail in sentence_noun_dict['noun_information']:
        noun_text = noun_detail['trigger_text']
        if '[Quotation' in noun_text or '[Partial' in noun_text:
            roles_ttl.append(f'{event_iri} :has_topic :{noun_text[1:-1]} .')
            continue
        for honorific in honorifics:
            noun_text = noun_text.replace(honorific, '')
        role = noun_detail['semantic_role']
        if role == 'content' and len(noun_text.split()) > 3:
            roles_ttl.append(f'{event_iri} :has_topic [ a :Clause ; :text {Literal(noun_text).n3()} ] .')
            continue
        if role == 'time':     # TODO: Time as NER
            roles_ttl.append(f'{event_iri} :has_time [ a :Time ; :text {Literal(noun_text).n3()} ] .')
            continue
        correctness = noun_detail['correctness']
        category = noun_detail['category_number']
        noun_class_name = 'owl:Thing'
        if 0 < category < len(noun_categories) + 1:
            noun_class_name = noun_categories[category - 1]
        else:
            logging.error(f'Invalid noun type ({category}) for {noun_text}')
        if noun_text in verb_details:
            noun_iri = verb_details[noun_text].iri
            noun_ttl = []
        else:
            noun_iri, noun_ttl = _get_noun_details(noun_text, noun_class_name, correctness, nouns_dict)
        if noun_iri == event_iri:
            continue
        if event_class == noun_class_name and noun_iri.startswith(':Noun'):
            roles_ttl.append(f'{event_iri} :text {Literal(noun_text).n3()} .')
            continue
        if noun_ttl:           # Turtle for a new noun
            roles_ttl.extend(noun_ttl)
        # Determine the predicate relating the noun to the event
        predicate = _get_predicate(noun_text, noun_class_name, role, event_class)
        if predicate:
            if predicate == ':affiliated_with' and event_class != ':Affiliation':
                roles_ttl.append(f'{event_iri} a :Affiliation .')
            roles_ttl.append(f'{event_iri} {predicate} {noun_iri} .')
    return roles_ttl


def _get_noun_details(noun_text: str, noun_class: str, correctness: int, nouns_dict: dict) -> (str, list):
    """
    Determine/define the entities associated with an event/condition. Return their iri,
    and any new Turtle.

    :param noun_text: String holding the noun text
    :param noun_class: String holding DNA class name that defines the semantics of the noun
    :param nouns_dict: A dictionary holding the nouns/named entities encountered in the narrative;
             The dictionary keys are the text for the noun, and its values are a tuple consisting
             of the spaCy entity type and the noun's IRI. An IRI value may be associated with
             more than 1 text.
    :return: A tuple consisting of the noun's assigned IRI, and any new Turtle for it
    """
    spacy_type, noun_iri = check_if_noun_is_known(noun_text, noun_class, nouns_dict)
    if noun_iri:
        return noun_iri, []
    new_turtle = []
    noun_iri = f':Noun_{str(uuid.uuid4())[:13]}'
    if noun_text in ('I', 'We', 'we', 'me', 'us'):
        # TODO: (Future) Assumes that every 'I' is the same person; Is this valid?
        noun_class = ':Person'
        if noun_text.lower in ('we', 'us'):
            noun_class += ', :Collection'
        nouns_dict[noun_text] = ('PERSON', noun_iri)
        new_turtle.append(f'{noun_iri} a {noun_class} ; :text {Literal(noun_text).n3()} ; :confidence 99 .')
    else:
        # Add to the nouns_dictionary
        nouns_dict[noun_text.replace('.', empty_string)] = empty_string, noun_iri
        # Add to the turtle
        new_turtle.append(f'{noun_iri} a {noun_class} ; :text {Literal(noun_text).n3()} ; :confidence {correctness} .')
    return noun_iri, new_turtle


def _get_predicate(noun_str: str, noun_class_name: str, role: str, event_class: str) -> str:
    """
    Get the DNA property/predicate appropriate for the event and its associated entity.

    :param noun_str: String holding the text of the associated entity
    :param noun_class_name: String holding the DNA class mapping for the entity
    :param role: String holding the semantic role of the noun, as defined by OpenAI
    :param event_class: A string holding the DNA class name(s) defining the semantics of the event/state
    :return: A string holding the predicate associating the entity to the event/state
    """
    sem_role_lower = role.lower()
    if event_class in measurement:
       return ':has_quantification' if any(c.isdigit() for c in noun_str) else ':has_context'
    if noun_class_name in measurement:
       return ':has_quantification'
    if ':EnvironmentAndCondition' == event_class:
        if ':LineOfBusiness' in noun_class_name or ':EthnicGroup' in noun_class_name or \
                ':PoliticalGroup' in noun_class_name or ':ReligiousGroup' in noun_class_name:
            return ':has_aspect'
        elif sem_role_lower in ('agent', 'experiencer') and noun_class_name in agent_classes:
            return ':has_context'
    if ':Affiliation' == event_class:
        return ':has_active_entity' if sem_role_lower == 'agent' else ':affiliated_with'
    if ':MovementTravelAndTransportation' == event_class and sem_role_lower == 'theme' and \
            noun_class_name in location_business:
        return ':has_destination'
    if sem_role_lower == 'location' and noun_class_name not in location_business:
        return ':has_context'
    if sem_role_lower == 'source' and noun_class_name in agent_classes:
        return ':has_source'
    if sem_role_lower == 'recipient' and noun_class_name in location_business:
        return ':has_recipient'
    if sem_role_lower in 'patient' and noun_class_name in location_business:
        return ':has_location'
    if sem_role_lower in 'patient' and noun_class_name not in agent_classes_without_plant:
        return ':has_context'
    if sem_role_lower in ('agent', 'experiencer') and noun_class_name not in agent_classes_without_plant:
        return ':has_context'
    if sem_role_lower == 'goal':
        if noun_class_name in agent_classes_without_plant:
            return ':has_affected_entity'
        elif noun_class_name not in location_business:
            return ':has_context'
    if sem_role_lower in semantic_roles:
        return semantic_role_mapping[sem_role_lower]
    else:
        logging.info(f'Unknown semantic role: {sem_role_lower} in text: {noun_str}')
        return empty_string


def get_sentence_details(sentence_or_quotation: Union[Sentence, Quotation], ttl_list: list, sentence_type: str,
                         nouns_dict: dict, repo: str) -> list:
    """
    Retrieve sentence or quotation details (such as the summary or rhetorical devices)
    using the OpenAI API and create the Turtle representation of this information. Return the
    sentence or quotation summary as the result.

    :param sentence_or_quotation: An instance of either the Sentence or Quotation Class
    :param ttl_list: The current Turtle definition where the new declarations will be stored
    :param sentence_type: String indicating that the processing is for a 'sentence' or ('complete'),
             a 'quote'
    :param nouns_dict: A dictionary holding the nouns/named entities encountered in the narrative;
             The dictionary keys are the text for the noun, and its values are a tuple consisting
             of the spaCy entity type and the noun's IRI. An IRI value may be associated with
             more than 1 text.
    :param repo: String holding the repository name for the narrative graph
    :return: The sentence's summary (and ttl_list is updated with the details from OpenAI)
    """
    sentence_iri = sentence_or_quotation.iri
    sentence_text = sentence_or_quotation.text
    # Get named entities for a sentence, including its quotations
    entity_iris = []
    entity_ttls = []
    if sentence_or_quotation.entities:
        new_iris, new_ttl = process_ner_entities(sentence_text, sentence_or_quotation.entities, nouns_dict)
        entity_iris.extend(new_iris)
        entity_ttls.extend(new_ttl)
    if entity_ttls:
        ttl_list.extend(entity_ttls)
        ner_ttl = ttl_prefixes[:]
        ner_ttl.extend(entity_ttls)
        # Add new entities to the repo's default graph
        msg = add_remove_data('add', ' '.join(ner_ttl), repo)
        if msg:
            logging.error('Error adding new entity: ', ner_ttl)
    for entity_iri in entity_iris:
        ttl_list.append(f'{sentence_iri} :mentions {entity_iri} .')
    # Capture a quotation's attribution
    if sentence_type == 'quote' and sentence_or_quotation.attribution:
        attrib_text = sentence_or_quotation.attribution
        for ent in get_entities(attrib_text):
            if ent.ner_type == 'PERSON':
                attrib_text = ent.text
                break
        attrib_type, attrib_iri = check_if_noun_is_known(unidecode(attrib_text.replace('.', empty_string)),
                                                         'PERSON', nouns_dict)
        if attrib_iri:
            ttl_list.append(f'{sentence_iri} :attributed_to {attrib_iri} .')
    # Process the sentence-level prompt
    summary = empty_string
    sent_dict = access_api(sentence_prompt.replace("{sent_text}", sentence_text))   # Deref
    if sent_dict:   # Might not get reply from OpenAI
        if type(sent_dict['grade_level']) is int:
            ttl_list.append(f'{sentence_iri} :grade_level {sent_dict["grade_level"]} .')
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
                        explanation = device_detail['explanation']
                        ttl_list.append(f'{sentence_iri} {predicate} "{explanation}" .')
                    else:
                        logging.error(f'Invalid rhetorical device ({device_numb}) for sentence, {sentence_text}')
                        continue
        if 'summary' in sent_dict:
            ttl_list.append(f'{sentence_iri} :summary {Literal(sent_dict["summary"]).n3()} .')
            summary = sent_dict['summary']
    return summary


def sentence_semantics_processing(sentences: dict, nouns_dict: dict) -> list:
    """
    Logic to process the semantics (main verb and nouns) of the sentences from a narrative/article.

    :param sentences: A dictionary whose keys are the sentence_iris and whose values are the
                      sentence text
    :param nouns_dict: A dictionary holding the nouns/named entities encountered in the narrative;
             The dictionary keys are the text for the noun, and its values are a tuple consisting
             of the spaCy entity type and the noun's IRI. An IRI value may be associated with
             more than 1 text.
    :return: Array holding the assembled Turtle statements for the sentence semantics
    """
    semantics_ttl = []
    # Collect all the sentence texts in a string
    sentence_iris = []
    sentence_texts_without_index = []
    # Resolve coreferences
    for key, value in sentences.items():
        sentence_iris.append(key)
        sentence_texts_without_index.append(value)
    coref_dict = access_api(coref_prompt.replace('{sentences}', ' '.join(sentence_texts_without_index)))
    updated_sentences = coref_dict['updated_sentences']
    # Create array with indices and the sentences with co-references resolved
    sentence_texts = []
    index = 1
    for sentence in updated_sentences:
        sentence_texts.append(f'{str(index)}. {sentence}')
        index += 1
    sentence_events_dict = access_api(events_prompt.replace('{numbered_sentences_texts}', ' '.join(sentence_texts)))
    # Process the sentences and their verbs one by one; OpenAI has issues with too many sentences
    processed_iris = []
    for sentence_event in sentence_events_dict['sentences']:
        index = int(sentence_event['sentence_number'])
        # Assemble the Turtle for the sentence
        sent_iri = sentence_iris[index - 1]
        # Assemble the sentence with the verbs in parentheses at the end
        verb_details = dict()    # Dictionary with key = verb text and value = VerbDetails dataclass
        verb_texts = []          # List of the verbs' trigger texts
        verb_numbers = []        # Array of verbs' DNA class mappings
        for event_state in sentence_event['verbs']:
            trigger_text = event_state["trigger_text"]
            if event_state["category_number"] in verb_numbers and trigger_text.lower().startswith('to ') and \
                    any([trigger_text in verb_text for verb_text in verb_texts]):
                continue    # An infinitive that is already included
            verb_texts.append(event_state["trigger_text"])
            verb_numbers.append(event_state["category_number"])
            verb_details[f'{event_state["trigger_text"]}'] = \
                VerbDetails(event_state['category_number'], event_state['category_same_or_opposite'],
                            event_state['correctness'], f':Event_{str(uuid.uuid4())[:13]}')
        verb_texts_string = '", "'.join(verb_texts)
        sent_with_verbs_text = f'{updated_sentences[index - 1]} ("{verb_texts_string}") '
        noun_categories_dict = access_api(noun_categories_prompt.
                                          replace('{sentence_text}', sent_with_verbs_text))
        sentence_nouns = noun_categories_dict['sentence_nouns']     # See query_openai's noun_categories_result
        # Assemble the Turtle for the verbs/events/states, along with the verbs' related concepts/nouns
        prev_event = empty_string
        for noun_details in sentence_nouns:
            trigger_text = noun_details['verb_text']
            verb_details_key = empty_string
            if trigger_text in verb_texts:
                verb_details_key = trigger_text
            elif len(trigger_text) > 3:
                for key in verb_details.keys():
                    if trigger_text in key:      # TODO: Needs further testing
                        verb_details_key = key
                        break
            if not verb_details_key:
                logging.error(f'OpenAI returned unrequested verb text, {trigger_text}, for the sentence, '
                              f'{updated_sentences[index - 1]}')
                continue
            event_iri = verb_details[verb_details_key].iri
            if prev_event:              # Need a topic for the previous event
                semantics_ttl.append(f'{prev_event} :has_topic {event_iri} .')
            if event_iri in processed_iris:
                semantics_ttl.append(f'{event_iri} :text {Literal(trigger_text).n3()} .')
                break
            else:
                processed_iris.append(event_iri)
            semantics_ttl.append(f'{sent_iri} :has_semantic {event_iri} .')
            semantics_ttl.append(f'{event_iri} :text {Literal(verb_details_key).n3()} .')
            category = int(verb_details[verb_details_key].category)
            correctness = int(verb_details[verb_details_key].correctness)
            event_class_name = ':EventAndState'
            if 0 < category < len(event_categories) + 1:      # A valid category #
                if category < 68:                             # Every category except EventAndState/other
                    event_class_name = event_categories[category - 1]
                else:
                    correctness = 0
                semantics_ttl.append(
                    f'{event_iri} a {event_class_name} ; :confidence-{event_class_name[1:]} {correctness} .')
                # TODO: Pending pystardog fix: Change line above to using RDF star property
                if verb_details[verb_details_key].same_opposite == "opposite":
                    semantics_ttl.append(f'{event_iri} :negated true .')
            else:
                logging.info(f'Invalid event category ({category}) for {trigger_text} for sentence index {index}')
            future = False
            if ' will ' in trigger_text or trigger_text.startswith('will '):
                semantics_ttl.append(f'{event_iri} :future true . ')
                future = True
            for modal in modals:
                if f' {modal}' in trigger_text or trigger_text.startswith(modal):
                    modal_key = modal[:-1]
                    # Some modifications based on tense
                    if modal == 'can ':
                        modal_key = 'can-present' if not future else 'can-not-present'
                    elif modal == 'could ':
                        modal_key = 'could-past' if not future else 'could-not-past'
                    semantics_ttl.append(f'{event_iri} a {modal_mapping[modal_key]} ; '
                                         f':confidence-{modal_mapping[modal_key][1:]} 95 .')
            # Assemble the Turtle for the verbs'/events'/states/ nouns and their semantic roles
            noun_ttl = _deal_with_sem_roles(event_iri, verb_details, noun_details, event_class_name, nouns_dict)
            semantics_ttl.extend(noun_ttl)
            ttl_txt = str(noun_ttl)
            prev_event = empty_string
            # TODO: Other classes?
            if event_class_name in (':Avoidance', ':EmotionalResponse', ':SensoryPerception',
                                    ':CommunicationAndSpeechAct', ':Causation', ':LegalEvent') \
                    and not (':has_context' in ttl_txt or ':has_aspect' in ttl_txt or ':has_topic' in ttl_txt):
                prev_event = event_iri
    return semantics_ttl
