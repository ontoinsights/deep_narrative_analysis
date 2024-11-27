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
from dna.process_entities import agent_classes, check_if_noun_is_known, process_ner_entities
from dna.query_openai import access_api, coref_prompt, event_categories, events_prompt, \
    noun_categories, noun_categories_prompt, rhetorical_devices, sentence_prompt, situations_prompt
from dna.sentence_classes import Sentence, Quotation, Entity
from dna.utilities_and_language_specific import empty_string, honorifics, literal, modals, ner_dict, ttl_prefixes

agent_classes_without_plant = [element for element in agent_classes if ':Plant' not in element]

location_business = (':Location', ':GeopoliticalEntity', ':LineOfBusiness')

measurement = (':Assessment', ':Measurement')

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

# TODO: (Future)
# semantic_roles = ("affiliation", "agent", "patient", "content", "theme", "experiencer", "instrument", "cause",
#                  "location", "time", "goal", "source", "state", "subject", "purpose", "recipient",
#                  "measure", "attribute")
#
#semantic_role_mapping = {"affiliation": ":affiliated_with", "agent": ":has_active_entity",
                         # "attribute": ":has_aspect", "beneficiary": ":has_affected_entity",
                         # "cause": ":has_cause", "content": ":has_topic", "co-agent": ":has_active_entity",
                         # "co-patient": ":has_affected_entity", "experiencer": ":has_affected_entity",
                         # "goal": ":has_destination",      # only for locations; goal of person -> has_affected_entity
                         # "instrument": ":has_instrument", "location": ":has_location",
                         # "measure": ":has_quantification", "patient": ":has_affected_entity",
                         # "purpose": ":has_goal", "recipient": ":has_recipient",   # for locations -> has_destination
                         # "source": ":has_origin", "state": ":has_aspect", "subject": ":has_context",
                         # "theme": ":has_topic", "time": ":has_time"}


def _deal_with_nouns(event_iri: str, event_classes: list, noun_texts: list, short_texts: list,
                     situation_nouns: list, nouns_dict: dict) -> list:
    """
    Get the class details and appropriate predicates for nouns related to a situation.

    :param event_iri: The IRI identifying the situation
    :param noun_texts: An array holding the 'active', 'passive' and 'topic' noun texts (where each
                       text ends with either "_active", "_passive" or "_topic" as appropriate)
    :param short_texts: An array holding the noun descriptions (entries are ordered
                        by the texts in noun_texts)
    :param situation_nouns: See query_openai's noun_categories_result for the key, "text_nouns"
    :param event_classes: An array holding the DNA classes that categorize the situation
    :param nouns_dict: A dictionary holding the nouns/named entities encountered in the narrative;
             The dictionary keys are the text for the noun, and its values are a tuple consisting
             of the spaCy entity type and the noun's IRI. An IRI value may be associated with
             more than 1 text.
    :return: An array holding the Turtle for the situation's associated nouns
    """
    nouns_ttl = []
    for index, noun_text in enumerate(noun_texts):
        phrase = noun_text.rsplit('_', 1)[0]
        noun_details = [phrase , noun_text.rsplit('_', 1)[1]]
        full_spacy_type, noun_iri = check_if_noun_is_known(phrase, empty_string, nouns_dict)
        noun_class = 'owl:Thing'
        if full_spacy_type and noun_iri:
            for key, value in ner_dict.items():
                if key in full_spacy_type:
                   noun_class = value
                   break
        if not noun_iri:
            noun_iri, noun_class, noun_ttl = _get_noun_details(noun_details, short_texts[index], event_classes,
                                                               situation_nouns[index]['phrase_information'], nouns_dict)
            if noun_ttl:           # Turtle for a new noun
                nouns_ttl.extend(noun_ttl)
        # Determine the predicate relating the noun to the event
        predicate = _get_predicate(noun_details, noun_class, event_classes)
        if predicate:
            nouns_ttl.append(f'{event_iri} {predicate} {noun_iri} .')
    return nouns_ttl


def _get_event_class(category: int, correctness: int) -> (str, int):
    """
    Determine the event/condition DNA class name for the situation category returned by OpenAI.

    :param category: The event/condition category number.
    :param correctness: The correctness of the semantic mapping to the category number, as
                        estimated by OpenAI.
    :return: The DNA class name corresponding to the category number and the mapping correctness
    """
    event_class_name = ':EventAndState'
    if 0 < category < len(event_categories) + 1:      # A valid category #
        if category < 68:                             # Every category except EventAndState/other
            event_class_name = event_categories[category - 1]
        else:
            correctness = 0
    return event_class_name, correctness


def _get_noun_details(noun_details: list, short_text: str, event_classes: list, situation_noun_details: dict,
                      nouns_dict: dict) -> (str, str, list):
    """
    Define the Turtle for a noun associated with a situation (event/condition). Return the noun iri,
    and new Turtle.

    :param noun_details: Array holding the noun_text and the string, "active", "passive" or "topic"
    :param short_text: String holding the description for the noun
    :param event_classes: An array holding the DNA classes that categorize the situation
    :param situation_noun_details: See query_openai's noun_categories_result for the key, "text_nouns", and
                               then "noun_information"
    :param nouns_dict: A dictionary holding the nouns/named entities encountered in the narrative;
             The dictionary keys are the text for the noun, and its values are a tuple consisting
             of the spaCy entity type and the noun's IRI. An IRI value may be associated with
             more than 1 text.
    :return: A tuple consisting a string with the noun's assigned IRI, a string with its DNA class,
             and an array with any new Turtle
    """
    new_turtle = []
    noun_text = noun_details[0]
    noun_iri = f':Noun_{str(uuid.uuid4())[:13]}'
    correctness = situation_noun_details['correctness']
    same_or_opposite = situation_noun_details['category_same_or_opposite']
    if noun_text in ('I', 'We', 'we', 'me', 'us', 'you'):
        # TODO: (Future) Assumes that every 'I' is the same person; Is this valid?
        noun_class = ':Person'
        if noun_text.lower in ('we', 'us'):
            noun_class += ', :Collection'
        nouns_dict[noun_text] = ('PERSON', noun_iri)
        correctness = 99
        same_or_opposite = 'same'
    else:
        # Add to the nouns_dictionary
        nouns_dict[noun_text.replace('.', empty_string)] = empty_string, noun_iri
        # Add to the Turtle
        noun_class = 'owl:Thing'
        category = situation_noun_details['category_number']
        if 0 < category < len(noun_categories) + 1:      # A valid category #
            if category < 98:                             # Every category except Thing/other
                noun_class = noun_categories[category - 1]
            else:
                if ':EnvironmentAndCondition' in event_classes:
                    noun_class = ':EnvironmentAndCondition'
                    correctness = 80
                else:
                    correctness = 0
        else:
            logging.info(f'Invalid noun category ({category}) for {noun_text} for description {short_text}')
        if situation_noun_details['singular_plural_not_noun'] == 'plural noun':
            noun_class += ', :Collection'
    new_turtle.append(f'{noun_iri} a {noun_class} ; :text {literal(noun_text)} ; '
                      f'rdfs:label {literal(short_text)} ; :confidence {correctness} .')
    if same_or_opposite == 'opposite':
        new_turtle.append(f'{noun_iri} :negated true .')
    return noun_iri, noun_class, new_turtle


def _get_noun_texts(nouns_detail: list, noun_type: str, noun_texts: list, short_texts: list):
    """
    Update the arrays holding an active, passive or topic noun tex, its short description and
    the noun phrase (for mapping) for a situation in the query_openai's situations_result.

    :param nouns_detail: An array of active, passive or topic nouns for a situation
    :param noun_type: String holding either "active", "passive" or "topic" as appropriate
    :param noun_texts: An array holding the 'active', 'passive' or 'topic' noun texts
    :param short_texts: An array holding the 'active', 'passive' or 'topic' noun descriptions
                        (entries are ordered by the texts in noun_texts)
    :return: N/A (the noun_texts and short_texts are updated)
    """
    for noun in nouns_detail:
        if noun['text'] == "Unknown":
            return
        noun_texts.append(f'{noun["text"]}_{noun_type}')
        short_texts.append(f'{noun["text"]}; {noun["description"]}')
    return


def _get_predicate(noun_details: list, noun_class_name: str, event_classes: list) -> str:
    """
    Get the DNA property/predicate appropriate for the situation and its associated entity.

    :param noun_detail: Array holding the noun text in the first entry and whether
                        "active"/"passive"/"topic" in the second
    :param noun_class_name: String holding the DNA class mapping for the entity
    :param event_classes: An array holding the DNA classes that categorize the situation
    :return: A string holding the predicate associating the entity to the situation
    """
    if noun_details[1] == 'active':
        if ':EnvironmentAndCondition' in event_classes:
            return ':has_context'
        else:
            return ':has_active_entity'
    if ':Affiliation' in event_classes:
        return ':affiliated_with'
    if noun_details[1] == 'topic':
        if ':EnvironmentAndCondition' in event_classes:
            return ':has_aspect'
        else:
            return ':has_topic'
    if ':EnvironmentAndCondition' in event_classes:
        if ':LineOfBusiness' in noun_class_name or ':EthnicGroup' in noun_class_name or \
                ':PoliticalGroup' in noun_class_name or ':ReligiousGroup' in noun_class_name:
            return ':has_aspect'
    if noun_class_name in agent_classes and not any(class_name in event_classes for class_name in
           (':Attempt', ':EmotionalResponse', ':SensoryPerception', ':CommunicationAndSpeechAct')):
        return ':has_affected_entity'
    if noun_class_name in location_business:
        return ':has_location'
    if any(class_name in event_classes for class_name in
           (':Attempt', ':EmotionalResponse', ':SensoryPerception', ':CommunicationAndSpeechAct')) and \
           not noun_class_name in agent_classes_without_plant:
        return ':has_topic'
    if noun_class_name not in agent_classes:
        return ':has_topic'
    return ':has_affected_entity'


def get_sentence_details(sentence_or_quotation: Union[Sentence, Quotation], ttl_list: list, sentence_type: str,
                         nouns_dict: dict, repo: str):
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
    :return: N/A (the ttl_list is updated with the details from OpenAI)
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
        # summary = sentence_text
        # if 'summary' in sent_dict and sent_dict['summary']:
        #     summary = sent_dict['summary']
        # ttl_list.append(f'{sentence_iri} :summary {literal(summary)} .')
    # return summary
    return


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
    sentence_situations_dict = access_api(situations_prompt.
                                          replace('{numbered_sentences_texts}', ' '.join(sentence_texts)))
    # Process the sentences and their situations one by one; OpenAI has issues with too many sentences
    for sentence_detail in sentence_situations_dict['sentences']:
        index = int(sentence_detail['sentence_number'])
        sent_text = updated_sentences[index - 1]
        # Assemble the Turtle for the sentence
        sent_iri = sentence_iris[index - 1]
        # Get the situation details
        for situation in sentence_detail['ordered_situations']:
            trigger_text = situation["summary"]
            event_iri = f':Event_{str(uuid.uuid4())[:13]}'
            semantics_ttl.append(f'{sent_iri} :has_semantic {event_iri} .')
            semantics_ttl.append(f'{event_iri} rdfs:label {literal(trigger_text)} .')
            if situation['future']:
                semantics_ttl.append(f'{event_iri} :future true .')
            if situation['modal'] in modals:
                modal_text = situation['modal']
                if situation['future'] and situation['modal'] in ('can', 'could'):
                    modal_text += '-future'
                semantics_ttl.append(f'{event_iri} a {modal_mapping[modal_text]} ; '
                                     f':confidence-{modal_mapping[modal_text][1:]} 95 .')
            situation_events_dict = access_api(events_prompt.
                                               replace('{situation_text}', f'{situation["summary"]}; {sent_text}'))
            noun_texts = []
            short_texts = []
            _get_noun_texts(situation["actives"], 'active', noun_texts, short_texts)
            _get_noun_texts(situation["passives"], 'passive', noun_texts, short_texts)
            _get_noun_texts(situation["topics"], 'topic', noun_texts, short_texts)
            noun_phrases = [short_text.split(';')[0] for short_text in short_texts]
            situation_nouns_dict = access_api(noun_categories_prompt.
                                              replace('{noun_texts}', ' ** '.join(noun_phrases)))
            # Get noun categories
            noun_category_numbers = []
            for noun_dict in situation_nouns_dict['text_phrases']:
                noun_category_numbers.append(noun_dict['phrase_information']['category_number'])
            event_classes = []
            situation_events = []
            for key, value in situation_events_dict.items():      # "mappings" and "infinitive_mappings" lists
                situation_events.extend(value)
            for index, event_state in enumerate(situation_events):
                category = event_state['category_number']
                if category in noun_category_numbers and len(situation_events) > 1:
                    continue
                correctness = event_state['correctness']
                event_class_name = ':EventAndState'
                if 0 < category < len(event_categories) + 1:      # A valid category #
                    if category < 68:                             # Every category except EventAndState/other
                        event_class_name = event_categories[category - 1]
                    else:
                        correctness = 0
                else:
                    logging.info(f'Invalid event category ({category}) for {trigger_text}')
                if index != 0 and event_class_name == ':EnvironmentAndCondition':   # Ignore this type if not the first
                    continue
                event_classes.append(event_class_name)
                semantics_ttl.append(
                    f'{event_iri} a {event_class_name} ; :confidence-{event_class_name[1:]} {correctness} .')
                    # TODO: Pending pystardog fix: Change line above to using RDF star property
                if event_state['category_same_or_opposite'] == "opposite":
                    semantics_ttl.append(f'{event_iri} :negated-{event_class_name[1:]} true .')
                elif situation['modal'] in modals and 'not' in sent_text:
                    semantics_ttl.append(f'{event_iri} :negated-{event_class_name[1:]} true .')
            # Assemble the Turtle for the nouns
            noun_ttl = _deal_with_nouns(event_iri, event_classes, noun_texts, short_texts,
                                        situation_nouns_dict['text_phrases'], nouns_dict)
            semantics_ttl.extend(noun_ttl)
    return semantics_ttl
