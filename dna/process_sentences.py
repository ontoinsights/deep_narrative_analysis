# Processing of Sentence instances using OpenAI

import copy
import logging
import re
import uuid
from dataclasses import dataclass
from typing import Union
from unidecode import unidecode

from dna.database import add_remove_data
from dna.nlp import get_entities
from dna.process_entities import agent_classes, check_if_noun_is_known, create_time_iri, process_ner_entities
from dna.query_openai import access_api, noun_categories_prompt, rhetorical_devices, sentence_prompt, situation_prompt
from dna.sentence_classes import Sentence, Quotation, Entity
from dna.utilities_and_language_specific import empty_string, honorifics, literal, modals, ner_dict, ttl_prefixes

agent_classes_without_plant = [element for element in agent_classes if ':Plant' not in element]

location_business = (':BuildingAndDwelling', ':BuildingAndDwelling, :Collection', ':Location',
                     ':Location, :Collection', ':GeopoliticalEntity', ':GeopoliticalEntity, :Collection',
                     ':LineOfBusiness', ':LineOfBusiness, :Collection')

modal_mapping = {'can': ':ReadinessAndAbility',                      # Ex: I can swim.
                 'can-future': ':OpportunityAndPossibility',         # Ex: I can visit tomorrow.
                 'could': ':ReadinessAndAbility',                    # Ex: I could skate when I was younger.
                 'could-future': ':OpportunityAndPossibility',       # Ex: It could rain tomorrow.
                 'have to': ':RequirementAndDependence',             # Ex: You have to leave.
                 'may': ':OpportunityAndPossibility',                # Ex: It may rain.
                 'might': ':OpportunityAndPossibility',              # Ex: It might rain.
                 'must': ':RequirementAndDependence',                # Ex: I must leave.
                 'ought to': ':AdviceAndRecommendation',             # Ex: You ought to leave.
                 'shall': ':RequirementAndDependence',               # Ex: You shall go to the store.
                 'should': ':AdviceAndRecommendation',               # Ex: They should go to the store.
                 'would': ':OpportunityAndPossibility'}              # Ex: I would take the train if possible.

specific_mapping_dict = {'person': ':Person', 'geopolitical entity': ':GeopoliticalEntity',
                         'location': ':Location', 'occupation': ':LineOfBusiness'}
specific_spacy_dict = {'person': 'PERSON', 'geopolitical entity': 'LOC',
                       'location': 'LOC', 'occupation': ''}

# TODO: Add "effect"
semantic_roles = ("affiliation", "agent", "patient", "content", "theme", "experiencer", "instrument", "cause",
                  "location", "time", "goal", "source", "state", "subject", "purpose", "recipient",
                  "measure", "attribute")
semantic_role_mapping = {"affiliation": ":affiliated_with", "agent": ":has_active_entity",
                         "attribute": ":has_aspect", "beneficiary": ":has_affected_entity",
                         "cause": ":has_cause", "content": ":has_topic", "co-agent": ":has_active_entity",
                         "co-patient": ":has_affected_entity", "experiencer": ":has_affected_entity",
                         "goal": ":has_destination",      # only for locations; goal of person -> has_affected_entity
                         "instrument": ":has_instrument", "location": ":has_location",
                         "measure": ":has_quantification", "patient": ":has_affected_entity",
                         "purpose": ":has_goal", "recipient": ":has_recipient",   # for locations -> has_destination
                         "source": ":has_origin", "state": ":has_aspect", "subject": ":has_context",
                         "theme": ":has_topic", "time": ":has_time"}

@dataclass
class EventsAndNouns:
    """
    Dataclass holding the categories of events/states and nouns from the DNA ontology, and strings holding their
    numbered definitions for use in OpenAI calls
    """
    events: list                 # An array of event/state DNA classes
    numbered_events: str         # A string holding each DNA class description, numbered starting from 1
    nouns: list                  # An array of event/state + noun DNA classes
    numbered_nouns: str          # A string holding each DNA class description, numbered starting from 1


def _deal_with_nouns(event_iri: str, event_classes: list, sit_nouns_dict: dict, noun_roles_dict: dict,
                     events_and_nouns: EventsAndNouns, nouns_dict: dict) -> list:
    """
    Get the class details and appropriate predicates for nouns related to an event/situation.

    :param event_iri: The IRI identifying the event within the situation
    :param event_classes: An array holding the DNA classes that categorize the event
    :param sit_nouns_dict: Dictionary holding the results of the nouns_prompt (based on the
                           noun_categories_result format)
    :param events_and_nouns: An instance of the EventsAndNouns class
    :param noun_roles_dict: Dictionary whose keys are the noun phrases, and whose values are their
                            semantic role
    :param nouns_dict: A dictionary holding the nouns/named entities encountered in the narrative;
             The dictionary keys are the text for the noun, and its values are a tuple consisting
             of the spaCy entity type and the noun's IRI. An IRI value may be associated with
             more than 1 text.
    :return: An array holding the Turtle for the event's associated nouns
    """
    nouns_ttl = []
    for noun_details in sit_nouns_dict['noun_phrases']:
        phrase = noun_details['text']
        noun_context = noun_details['clarifying_text']
        noun_text = phrase if not noun_context else phrase.replace(noun_context, empty_string)
        # Sometimes OpenAI returns the correct phrase text but with additional adjectives, modifiers
        if phrase not in noun_roles_dict:
            revised = phrase.split(' ')
            if len(revised) > 1:
                new_phrase = ' '.join(revised[1:])
                if new_phrase not in noun_roles_dict:
                    continue
                else:
                    phrase = new_phrase
            else:
                continue
        if noun_roles_dict[phrase] == 'time':
            # TODO: Time IRIs need better resolution; e.g., every mention of "Tuesday" is not the same day
            time_iri = create_time_iri(empty_string, phrase, False)
            nouns_ttl.extend([f'{time_iri} a :Time ; :text {literal(phrase)} .',
                              f'{event_iri} :has_time {time_iri} .'])
            continue
        full_spacy_type, noun_iri = check_if_noun_is_known(noun_text, empty_string, nouns_dict)
        noun_class = 'owl:Thing'
        if full_spacy_type and noun_iri:
            for key, value in ner_dict.items():
                if key in full_spacy_type:
                   noun_class = value
                   break
        if not noun_iri:
            noun_iri, noun_class, noun_ttl = \
                _get_noun_details(noun_details, event_classes, events_and_nouns, nouns_dict)
            if not noun_iri:
                continue
            if noun_ttl:           # Turtle for a new noun
                nouns_ttl.extend(noun_ttl)
        # Process the clarifying text - TODO: Refine
        # Does the text refer to an existing concept?
        if noun_context:
            clarifying_type, clarifying_iri = check_if_noun_is_known(noun_context, empty_string, nouns_dict)
            if clarifying_iri:
                if any(':Affiliation' in event_class for event_class in event_classes) or ':Affiliation' in noun_class:
                    nouns_ttl.append(f'{noun_iri} :affiliated_with {clarifying_iri} .')
                else:
                    nouns_ttl.append(f'{noun_iri} :clarifying_reference {clarifying_iri} .')
            nouns_ttl.append(f'{noun_iri} :clarifying_text {literal(noun_context)} .')
        # Determine the predicate relating the noun to the event
        predicate = _get_predicate(noun_details, noun_class, noun_roles_dict, event_classes)
        if predicate:
            nouns_ttl.append(f'{event_iri} {predicate} {noun_iri} .')
    return nouns_ttl


def _get_noun_details(noun_details: dict, event_classes: list, events_and_nouns: EventsAndNouns,
                      nouns_dict: dict) -> (str, str, list):
    """
    Define the Turtle for a noun associated with a situation/event/condition. Return the noun iri,
    DNA class semantics, and new Turtle.

    :param noun_details: See query_openai's noun_categories_result for a single list entry for
                         the key, "noun_phrases"
    :param short_text: String holding the description for the noun
    :param event_classes: An array holding the DNA classes that categorize the situation
    :param events_and_nouns: An instance of the EventsAndNouns class
    :param nouns_dict: A dictionary holding the nouns/named entities encountered in the narrative;
             The dictionary keys are the text for the noun, and its values are a tuple consisting
             of the spaCy entity type and the noun's IRI. An IRI value may be associated with
             more than 1 text.
    :return: A tuple consisting a string with the noun's assigned IRI, a string with its DNA class,
             and an array with any new Turtle
    """
    new_turtle = []
    noun_text = noun_details['text']
    noun_iri = f':Noun_{str(uuid.uuid4())[:13]}'
    noun_class = 'owl:Thing'
    correctness = 95
    same_or_opposite = 'same'
    if noun_details['specific_representation'] in specific_mapping_dict:
        if noun_text.lower().startswith('narrator'):
            noun_class = ':Person' if noun_text.lower() == 'narrator' else ':Person, :Collection'
            nouns_dict[noun_text] = ('PLURALPERSON', noun_iri)      # Add to the nouns_dictionary
        else:
            noun_class = specific_mapping_dict[noun_details['specific_representation']]
            nouns_dict[noun_text.replace('.', empty_string)] = \
                (specific_spacy_dict[noun_details['specific_representation']], noun_iri)
    else:
        if noun_text in ('I', 'We', 'we', 'me', 'us', 'You', 'you'):
            # TODO: (Future) Assumes that every 'I' is the same person; Is this valid?
            noun_class = ':Person'
            if noun_text.lower in ('we', 'us'):
                noun_class += ', :Collection'
            nouns_dict[noun_text] = ('PERSON', noun_iri)      # Add to the nouns_dictionary
        else:
            nouns_dict[noun_text.replace('.', empty_string)] = empty_string, noun_iri    # Add to the nouns_dictionary
            category = noun_details['category_number']
            correctness = noun_details['correctness']
            if 0 < category < len(events_and_nouns.nouns) + 1:      # A valid category #
                noun_class = events_and_nouns.nouns[category - 1]
            else:
                logging.info(f'Invalid noun category ({category}) for {noun_text}')
            if noun_class == 'owl:Thing' and ':EnvironmentAndCondition' in event_classes:
                noun_class = ':EnvironmentAndCondition'
                correctness = 80
            if noun_class == 'owl:Thing':
                correctness = 0
            same_or_opposite = noun_details['same_or_opposite']
    if not noun_details['singular'] and ':Collection' not in noun_class:
        noun_class += ', :Collection'
    new_turtle.append(f'{noun_iri} a {noun_class} ; :text {literal(noun_text)} ; :confidence {correctness} .')
    if same_or_opposite == 'opposite':
        new_turtle.append(f'{noun_iri} :negated true .')
    return noun_iri, noun_class, new_turtle


def _get_predicate(noun_details: dict, noun_class_name: str, noun_roles_dict: dict, event_classes: list) -> str:
    """
    Get the DNA property/predicate appropriate for the situation/event and its associated entity,
    based on the entity's semantic role.

    :param noun_details: See query_openai's noun_categories_result for a single list entry for
                         the key, "noun_phrases"
    :param noun_class_name: String holding the DNA class mapping for the entity
    :param noun_roles_dict: Dictionary whose keys are the noun phrases, and whose values are their
                            semantic role
    :param event_classes: An array holding the DNA classes that categorize the situation
    :return: A string holding the predicate associating the entity to the situation/event
    """
    noun_text = noun_details['text']
    if noun_text not in noun_roles_dict:
        revised = noun_text.split(' ')
        if len(revised) > 1:
            new_text = ' '.join(revised[1:])
            if new_text not in noun_roles_dict:
                return empty_string
            else:
                noun_text = new_text
    sem_role_lower = noun_roles_dict[noun_text].lower()
    if (any(':Measurement' in event_class for event_class in event_classes) or
        any(':AssessmentMeasurement' in event_class for event_class in event_classes) or
            ':Measurement' in noun_class_name or ':AssessmentMeasurement' in noun_class_name):
        if any(c.isdigit() for c in noun_text):
            return ':has_quantification'
        else:
            return ':has_context'
    if any(':AttributeAndCharacteristic' in event_class for event_class in event_classes):
        if ':LineOfBusiness' in noun_class_name or ':EthnicGroup' in noun_class_name or \
                ':PoliticalGroup' in noun_class_name or ':ReligiousGroup' in noun_class_name:
            return ':has_aspect'
        elif sem_role_lower in ('agent', 'experiencer'):
            return ':has_context'
    if any(':Affiliation' in event_class for event_class in event_classes):
        return ':has_context' if sem_role_lower in ('agent', 'experiencer', 'subject') else ':affiliated_with'
    if ':Affiliation' == noun_class_name:
        # TODO: Determine which entity is affiliated with another; Define new Affiliation Event and associate the nouns
        return ':has_context'
    if any(':MovementTravelAndTransportation' in event_class for event_class in event_classes) and \
            sem_role_lower == 'theme' and noun_class_name in location_business:
        return ':has_destination'
    if (any(':EmotionalResponse' in event_class for event_class in event_classes) or
        any(':SensoryPerception' in event_class for event_class in event_classes) or
        any(':AttributeAndCharacteristic' in event_class for event_class in event_classes) or
        any(':Cognition' in event_class for event_class in event_classes)) \
            and sem_role_lower == 'experiencer':
        return ':has_active_entity'
    if sem_role_lower == 'location' and noun_class_name not in location_business:
        return ':has_context'
    if sem_role_lower == 'source' and noun_class_name in agent_classes:
        return ':has_source'
    if sem_role_lower == 'recipient' and noun_class_name in location_business:
        return ':has_destination'
    if sem_role_lower in 'patient' and noun_class_name in location_business:
        return ':has_location'
    if sem_role_lower == 'experiencer' and noun_class_name not in agent_classes_without_plant:
        return ':has_context'
    if sem_role_lower == 'experiencer' and not any(value == 'agent' for key, value in noun_roles_dict.items()):
        return ':has_active_entity'
    if sem_role_lower == 'goal':
        if noun_class_name in agent_classes_without_plant:
            return ':has_affected_entity'
        elif noun_class_name not in location_business:
            return ':has_context'
    if sem_role_lower in semantic_roles:
        return semantic_role_mapping[sem_role_lower]
    else:
        logging.info(f'Unknown semantic role: {sem_role_lower} for text: {noun_text}')
        return empty_string


def get_sentence_details(sentence_or_quotation: Union[Sentence, Quotation], ttl_list: list,
                         sentence_type: str, nouns_dict: dict, repo: str):
    """
    Retrieve sentence or quotation details (such as rhetorical devices and quotation attribution)
    using the OpenAI API and create the Turtle representation of this information.

    :param sentence_or_quotation: An instance of either the Sentence or Quotation Class
    :param ttl_list: The current Turtle definition where the new declarations will be stored
    :param sentence_type: String indicating that the processing is for a 'sentence' or ('complete'),
             a 'quote'
    :param nouns_dict: A dictionary holding the nouns/named entities encountered in the narrative;
             The dictionary keys are the text for the noun, and its values are a tuple consisting
             of the spaCy entity type and the noun's IRI. An IRI value may be associated with
             more than 1 text.
    :param repo: String holding the repository name for the narrative graph
    :return: N/A (the ttl_list is updated with the details from OpenAI)
    """
    sentence_iri = sentence_or_quotation.iri
    sentence_text = sentence_or_quotation.text
    # Get named entities for a sentence, including its quotations
    entity_iris = []
    entity_ttls = []
    if sentence_or_quotation.entities:
        # Deal with hyphenated names (e.g., 'Biden-Harris campaign')
        new_entities = []
        for entity in sentence_or_quotation.entities:
            if '-' in entity.text:
                # TODO: Improve - names must be previously encountered as background information or full names in text
                if entity.text in nouns_dict:    # Check first for an exact match of a hyphenated name
                    new_entities.append(entity)
                # Not previously encountered
                split_names = entity.text.split('-')
                # Are ALL the split names encountered?
                encountered = all(split_name in nouns_dict.keys() for split_name in split_names)
                if encountered:
                    new_entities.extend(
                        [Entity(split_name, entity.ner_type, []) for split_name in split_names])
                else:
                    new_entities.append(entity)
            else:
                new_entities.append(entity)
        new_iris, new_ttl = process_ner_entities(sentence_text, new_entities, nouns_dict)
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
                        ttl_list.append(f'{sentence_iri} {predicate} {literal(device_detail["explanation"])} .')
                    else:
                        logging.error(f'Invalid rhetorical device ({device_numb}) for sentence, {sentence_text}')
                        continue
    return


def situation_semantics_processing(situations: list, events_and_nouns: EventsAndNouns, narr_id: str,
                                   subject_areas: list, nouns_dict: dict) -> list:
    """
    Logic to process the semantics of the main event/situation sentences from a narrative/article.

    :param situations: An array of the main events/situations described in a narrative/article as
                      defined by OpenAI
    :param events_and_nouns: An instance of the EventsAndNouns class
    :param narr_id: IRI identifying the narrative
    :param subject_areas: A list of the subject areas of the narrative, as defined by OpenAI
    :param nouns_dict: A dictionary holding the nouns/named entities encountered in the narrative;
             The dictionary keys are the text for the noun, and its values are a tuple consisting
             of the spaCy entity type and the noun's IRI. An IRI value may be associated with
             more than 1 text.
    :return: Array holding the assembled Turtle statements for the situation semantics
    """
    semantics_ttl = []
    # Create the prompt for the situation text with the event categories
    sit_prompt = (situation_prompt.replace('{events_text}', events_and_nouns.numbered_events).
                  replace('{other_number}', str(len(events_and_nouns.events))).
                  replace('{description_number}',
                          str(events_and_nouns.events.index(":AttributeAndCharacteristic") - 1)))
    nouns_prompt = (noun_categories_prompt.replace('{noun_texts}', events_and_nouns.numbered_nouns).
                    replace('{other_number}', str(len(events_and_nouns.nouns))))
    if len(subject_areas) > 0:
        if len(subject_areas) == 1:
            area_sentence = f'The subject area is "{subject_areas[0]}".'
        else:
            area_text = '", "'.join(subject_areas)
            area_sentence = f'The subject areas are "{area_text}".'
        subject_area_text = f'When mapping semantics, make sure to carefully consider the specific focus and ' \
                            f'context of the subject area. {area_sentence}'
    else:
        subject_area_text = empty_string
    sit_prompt = sit_prompt.replace('{subject_area_text}', subject_area_text)
    nouns_prompt = nouns_prompt.replace('{subject_area_text}', subject_area_text)
    # Process the situations one by one; OpenAI has issues with analyzing too many sentences
    for index, situation in enumerate(situations):
        # Assemble the Turtle for the sentence
        sit_iri = f':NarrativeEvent_{str(uuid.uuid4())[:13]}'
        # Get the situation details
        semantics_ttl.extend([f'{narr_id} :describes {sit_iri} .',
                              f'{sit_iri} a :NarrativeEvent ; :offset {index} .',
                              f'{sit_iri} :text {literal(situation)} .'])
        situation_dict = access_api(sit_prompt.replace('{sit_text}', situation))
        prev_event = empty_string
        for sentence in situation_dict['simpler_sentences']:
            event_iri = f':Event_{str(uuid.uuid4())[:13]}'
            sent_text = sentence["text"]
            if sent_text.endswith(' something.'):
                sent_text = sent_text.replace(' something', empty_string)
            if not prev_event:
                semantics_ttl.extend([f'{sit_iri} :has_semantic {event_iri} .',
                                      f'{sit_iri} :has_first {event_iri} .',
                                      f'{event_iri} :text {literal(sent_text)} .'])

            else:
                semantics_ttl.extend([f'{sit_iri} :has_semantic {event_iri} .',
                                      f'{prev_event} :has_next {event_iri} .',
                                      f'{event_iri} :text {literal(sent_text)} .'])
            prev_event = event_iri
            if sentence['future_tense']:
                semantics_ttl.append(f'{event_iri} :future true .')
            if sentence['modal'] in modals:
                modal_text = sentence['modal']
                if sentence['future_tense'] and modal_text in ('can', 'could'):
                    modal_text += '-future'
                semantics_ttl.append(f'{event_iri} a {modal_mapping[modal_text]} ; '
                                     f':confidence-{modal_mapping[modal_text][1:]} 95 .')
            event_classes = []
            for sem_index, event_state in enumerate(sentence['semantics']):
                category = event_state['category_number']
                event_class_name = ':EventAndState'
                if 0 < category < len(events_and_nouns.events) + 1:      # A valid category #
                    event_class_name = events_and_nouns.events[category - 1]
                else:
                    logging.info(f'Invalid event category ({category}) for {situation}')
                if sem_index != 0 and (event_class_name in (':Avoidance', ':EventAndState') or
                        (event_class_name == ':Affiliation' and
                        any(':AttributeAndCharacteristic' in event_class for event_class in event_classes)) or
                        (event_class_name == ':AssessmentMeasurement' and
                        any(':CommunicationAndSpeechAct' in event_class for event_class in event_classes))):
                    continue   # TODO: Need better algorithm to ignore (currently, ignoring these types if not first)
                if event_state["correctness"] > 80:
                    event_classes.append(event_class_name)
                semantics_ttl.append(
                    f'{event_iri} a {event_class_name} ; :confidence-{event_class_name[1:]} '
                    f'{event_state["correctness"]} .')
                    # TODO: Pending pystardog fix: Change line above to using RDF star property
                if event_state["same_or_opposite"] == 'opposite':
                    semantics_ttl.append(f'{event_iri} :negated-{event_class_name[1:]} true .')
            noun_roles_dict = dict()
            for noun in sentence['nouns']:
                noun_roles_dict[noun['noun_text']] = noun['semantic_role']
            # Get noun categories and details, and assemble the Turtle for the nouns
            situation_nouns_dict = access_api(nouns_prompt.
                                              replace('{noun_phrases}', " ** ".join(noun_roles_dict.keys())))
            noun_ttl = _deal_with_nouns(event_iri, event_classes, situation_nouns_dict, noun_roles_dict,
                                        events_and_nouns, nouns_dict)
            semantics_ttl.extend(noun_ttl)
    return semantics_ttl
