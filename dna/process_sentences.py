# Processing of sentences using OpenAI

import logging
import re
import uuid
from PassivePySrc import PassivePy
from rdflib import Literal

from dna.process_entities import agent_classes, check_if_noun_is_known, get_sentence_entities
from dna.query_openai import access_api, categories, noun_categories, quote_prompt1, quote_prompt2, quote_prompt3, \
    rhetorical_devices, sent_prompt1, sent_prompt2, sent_prompt3, speaker_prompt
from dna.utilities_and_language_specific import empty_string, personal_pronouns, plural_pronouns

modal_mapping = {'can-present': ':ReadinessAndAbility',              # Ex: I can swim.
                 'can-not-present': ':OpportunityAndPossibility',    # Ex: I can visit tomorrow.
                 'could-past': ':ReadinessAndAbility',               # Ex: I could skate when I was younger.
                 'could-not-past': ':OpportunityAndPossibility',     # Ex: It could rain tomorrow.
                 'have to': ':AdviceAndRecommendation',              # Ex: You have to leave.
                 'may': ':OpportunityAndPossibility',                # Ex: It may rain.
                 'might': ':OpportunityAndPossibility',              # Ex: It might rain.
                 'must': ':RequirementAndDependence',                # Ex: I must leave.
                 'ought to': ':AdviceAndRecommendation',             # Ex: You ought to leave.
                 'shall-second': ':RequirementAndDependence',        # Ex: You shall go to the store.
                 'shall-not-second': ':IntentionAndGoal',            # Ex: They shall go to the store.
                 'should': ':AdviceAndRecommendation',               # Ex: They should go to the store.
                 'would': ':OpportunityAndPossibility'}              # Ex: I would take the train if possible.

semantic_roles = ("agent", "dative", "experiencer", "force", "instrument",
                  "location", "measure", "patient", "theme")

semantic_role_mapping = {"agent": ":has_active_entity",
                         "dative": ":has_affected_entity",
                         "experiencer": ":has_active_entity",
                         "instrument": ":has_instrument",
                         "location": ":has_location",
                         "measure": ":has_quantification",
                         "patient": ":has_affected_entity",
                         "source": ":has_source",    # TODO: Refine for location, has_origin
                         "theme": ":has_topic"}

passivepy = PassivePy.PassivePyAnalyzer(spacy_model="en_core_web_trf")


def _get_passive_verbs(sentence_text: str) -> list:
    """
    LLM indicates the correct voice ONLY for active and (usually) full_passive. So, using the PassivePy
    library instead to get the text/trigger words of all passive verbs.

    :param sentence_text: String holding the sentence text
    :return: Array of the text of all passive verbs
    """
    # TODO: Track both full and truncated? ChatGPT seems to return correct 'fully' passive Agent information
    passive_result = passivepy.match_text(sentence_text, full_passive=False, truncated_passive=True)
    return passive_result.all_passives    # Given the parameters above, only returning truncated passives


def _sentence_semantics_processing(sentence_dict: dict, sentence_iri: str, sentence_text: str, nouns_dict: dict,
                                   is_summary: bool, curr_turtle: list):
    """
    Logic to process the dictionary resulting from an OpenAI call using sent_prompt3. The current Turtle
    for the sentence is passed in and is updated.

    :param sentence_dict: Dictionary with the format defined by sent_format3 in query_openai.py
    :param sentence_iri: String holding the identifier for the sentence being analyzed
    :param sentence_text: String holding the text of the sentence being analyzed
    :param nouns_dict: A dictionary holding the nouns/named entities encountered in the narrative;
             The dictionary keys are the text for the noun, and its values are a tuple consisting
             of the spaCy entity type and the noun's IRI. An IRI value may be associated with
             more than 1 text. Note that this parameter is only used when processing quotations
             (in order to get the IRI of the speaker).
    :param is_summary: Boolean indicating if this is a summary of the full text from an article/narrative
    :param curr_turtle: Array holding the assembled Turtle statements for the sentence
    :return: None
    """
    if sentence_dict:
        for semantic in sentence_dict['semantics']:
            if 0 < semantic['category_number'] < len(categories) + 1:
                event_semantics = categories[semantic['category_number'] - 1]
            else:
                logging.error(f'Invalid semantic category ({semantic["category_number"]}) for {sentence_text}')
                event_semantics = ':EventAndState'
            trigger_text = semantic['trigger_text']
            if semantic['same_or_opposite'] == 'opposite' and \
                    (event_semantics != ':EmotionalResponse' or
                     (event_semantics == ':EmotionalResponse' and 'not' in sentence_text and
                      'not' not in trigger_text)):
                edges = '{:negated true ; :summary true}' if is_summary else '{:negated true}'
            else:
                edges = '{:summary true}' if is_summary else ''
            event_iri = f':Event_{str(uuid.uuid4())[:13]}'
            curr_turtle.append(f'{sentence_iri} :has_semantic {edges} {event_iri} .')
            curr_turtle.append(f'{event_iri} a {event_semantics} ; :text {Literal(trigger_text).n3()} .')
            if 'nouns' in semantic:     # Not returned for quotations
                passive_verbs = _get_passive_verbs(sentence_text)
                for noun in semantic['nouns']:
                    noun_text = noun['text']
                    entity_type, noun_iri = check_if_noun_is_known(noun_text, empty_string, nouns_dict)
                    _update_turtle(noun, noun_iri, event_semantics, event_iri, trigger_text, passive_verbs, curr_turtle)
    return


def _update_turtle(noun: dict, noun_iri: str, event_semantics: str, event_iri: str, trigger_text: str,
                   passive_verbs: list, curr_turtle: list):
    """
    Logic to create the appropriate predicate for the noun relationships to the sentence's
    verb/semantic, as well as adding details for a truncated passive.

    :param noun: Dictionary holding the noun details associated with the event_semantics
    :param noun_iri: An IRI for the noun, if the noun is a proper noun/already known (otherwise,
                     is an empty string)
    :param event_semantics: DNA class type of the EventAndState described in the sentence, to
                            which the noun is associated
    :param event_iri: String holding the IRI of the current event
    :param trigger_text: String holding the trigger word for the event/state
    :param passive_verbs: Array of the text of all passive verbs in the original sentence
    :param curr_turtle: Array holding the assembled Turtle statements for the sentence
    :return: N/A
    """
    # Determine if the trigger is a passive verb
    voice = "active"
    for verb in passive_verbs.loc[0]:
        if trigger_text in verb or verb in trigger_text:
            voice = "passive"
            break
    noun_text = noun['text']
    semantic_role = noun['semantic_role']
    if 0 < noun['noun_type'] < len(noun_categories) + 1:
        noun_category = noun_categories[noun['noun_type'] - 1]
    else:
        logging.error(f'Invalid noun type ({noun["noun_type"]}) for {noun_text}')
        noun_category = 'owl:Thing'
    if (noun['singular'] == 'false' or noun_text in plural_pronouns) and \
            ':Collection' not in noun_category:
        noun_category += ', :Collection'
    if 0 < noun['semantic_category'] < len(categories) + 1:
        event_category = categories[noun['semantic_category'] - 1]
    else:
        if noun['semantic_category'] != 0:
            logging.error(f'Invalid noun semantic category ({noun["semantic_category"]}) for {noun_text}')
        event_category = empty_string
    triple_object = noun_iri if noun_iri else f'[ :text {Literal(noun_text).n3()} ; ' \
                                              f'a {event_category if event_category else noun_category} ]'
    # TODO: Mapping rules; more needed?
    if noun_category == ':Measurement':
        curr_turtle.append(f'{event_iri} :has_quantification {triple_object} .')
    elif noun_category in (':LineOfBusiness', ':EthnicGroup', ':PoliticalGroup', ':ReligiousGroup') and \
            event_semantics in (':EnvironmentAndCondition', ':KnowledgeAndSkill'):
        curr_turtle.append(f'{event_iri} :has_aspect {triple_object} .')
    elif noun_category == ':LineOfBusiness' and \
            event_semantics not in (':EnvironmentAndCondition', ':KnowledgeAndSkill'):
        curr_turtle.append(f'{event_iri} :has_location {triple_object} .')
    elif event_semantics in (':EnvironmentAndCondition', ':KnowledgeAndSkill') and \
            ((semantic_role in ('agent', 'experiencer') or noun_category in agent_classes) or
             (semantic_role == 'theme' and noun_category in agent_classes)):
        curr_turtle.append(f'{event_iri} :has_described_entity {triple_object} .')
    elif event_semantics == ':Affiliation':
        if semantic_role == 'agent':
            curr_turtle.append(f'{event_iri} :has_active_entity {triple_object} .')
        elif noun_category in agent_classes:
            curr_turtle.append(f'{event_iri} :affiliated_with {triple_object} .')
        else:
            curr_turtle.append(f'{event_iri} :has_described_entity {triple_object} .')
    elif semantic_role in semantic_roles:
        if event_category and semantic_role == 'theme' and noun_category in agent_classes:
            curr_turtle.append(f'{event_iri} :has_affected_entity {triple_object} .')
        elif semantic_role == 'patient' and noun_category not in agent_classes:
            curr_turtle.append(f'{event_iri} :has_topic {triple_object} .')
        elif voice == 'passive':
            curr_turtle.append(f'{event_iri} :has_affected_entity {triple_object} .')
        else:
            curr_turtle.append(f'{event_iri} {semantic_role_mapping[semantic_role]} {triple_object} .')
    return


def get_sentence_details(sent_iri: str, sent_text: str, updated_text: str, ttl_list: list, attribution: str,
                         for_quote: bool, entities: list, nouns_dict: dict):
    """
    Retrieve sentence (or quotation) details using the OpenAI API and create the sentence
    (or quotation) level Turtle.

    :param sent_iri: The IRI identifying the current sentence
    :param sent_text: String holding the text of up to the 3 last sentences
    :param updated_text: String holding the sentence text if anaphora (co-references) are de-referenced;
                        Otherwise is the original sent_text
    :param ttl_list: The current Turtle definition where the new declarations will be stored
    :param attribution: String identifying the person who stated/communicate a quotation (is empty
                        for normal sentences)
    :param for_quote: Boolean indicating that the processing is for a quotation (if True)
    :param entities: An array of named entities found in the sentence, if any
    :param nouns_dict: A dictionary holding the nouns/named entities encountered in the narrative;
             The dictionary keys are the text for the noun, and its values are a tuple consisting
             of the spaCy entity type and the noun's IRI. An IRI value may be associated with
             more than 1 text. Note that this parameter is only used when processing quotations
             (in order to get the IRI of the speaker).
    :return: N/A (ttl_list is updated with the details from OpenAI)
    """
    # Handle named entities
    if entities:
        entity_iris, entity_ttl = get_sentence_entities(sent_text, entities, nouns_dict)
        ttl_list.extend(entity_ttl)
        for entity_iri in entity_iris:
            ttl_list.append(f'{sent_iri} :mentions {entity_iri} .')
    # Capture a quotation's attribution and whether it is formatted as a question or exclamation
    if for_quote:
        if attribution:
            attrib_type, attrib_iri = check_if_noun_is_known(attribution, 'PERSON', nouns_dict)
            if attrib_iri:
                ttl_list.append(f'{sent_iri} :attributed_to {attrib_iri} .')
        # Also check for punctuation, since this is stored in the quoted text
        if '?' in sent_text:
            ttl_list.append(f'{sent_iri} a :Inquiry .')
        elif '!' in sent_text:
            ttl_list.append(f'{sent_iri} a :ExpressiveAndExclamation .')
    else:
        # Not a quotation but one may be referenced in sentence
        quote_texts = re.findall(r'Quotation[0-9]+', sent_text)
        for quote_text in quote_texts:
            ttl_list.append(f'{sent_iri} :has_component :{quote_text} .')
    # Processing the first prompt for details such as sentence person, sentiment, tense, ...
    summary = empty_string
    if for_quote:
        quote_dict = access_api(quote_prompt1.replace("{quote_text}", sent_text))   # Note different prompts
        if quote_dict:   # Might not get reply from OpenAI
            sentiment = quote_dict['sentiment']
            summary = quote_dict['summary']
            ttl_list.extend([f'{sent_iri} :sentiment "{sentiment}" ; :summary "{summary}" .',
                             f'{sent_iri} :grade_level {quote_dict["grade_level"]} .'])
    else:
        sent_dict = access_api(sent_prompt1.replace("{sent_text}", sent_text))
        if sent_dict:   # Might not get reply from OpenAI
            sentiment = sent_dict['sentiment']
            tense = sent_dict['tense']
            summary = sent_dict['summary']
            ttl_list.extend([f'{sent_iri} :sentence_person {sent_dict["person"]} ; :sentiment "{sentiment}".',
                             f'{sent_iri} :tense "{tense}" ; :summary "{summary}" .',
                             f'{sent_iri} :grade_level {sent_dict["grade_level"]} .'])
            if sent_dict['modal_text'].lower() != "none":
                modal_text = sent_dict['modal_text']
                if modal_text not in modal_mapping:
                    if modal_text == 'can':
                        modal_text = 'can-present' if tense == 'present' else 'can-not-present'
                    elif modal_text == 'could':
                        modal_text = 'could-past' if tense == 'past' else 'could-not-past'
                    elif modal_text == 'shall':
                        modal_text = 'shall-second' if voice == 2 else 'shall-not-second'
                    else:
                        modal_text = empty_string
                if modal_text:
                    ttl_list.append(f'{sent_iri} :has_semantic {modal_mapping[modal_text]} .')
    # Processing the second prompt for rhetorical devices
    if for_quote:
        sent_dict = access_api(quote_prompt2.replace("{sent_text}", sent_text))   # Note different prompts
    else:
        sent_dict = access_api(sent_prompt2.replace("{sent_text}", sent_text))
    if sent_dict:   # Might not get reply from OpenAI or there are no rhetorical devices
        if 'rhetorical_devices' in sent_dict and len(sent_dict['rhetorical_devices']) > 0:
            for device_detail in sent_dict['rhetorical_devices']:
                device_numb = int(device_detail['device_number'])
                if 0 < device_numb < len(rhetorical_devices) + 1:
                    predicate = ':rhetorical_device {:evidence "' + device_detail['evidence'] + '"} '
                    ttl_list.append(f'{sent_iri} {predicate} "{rhetorical_devices[device_numb - 1]}" .')
                else:
                    logging.error(f'Invalid rhetorical device ({device_numb}) for sentence, {sent_text}')
                    continue
    # Processing the events and states, and related nouns
    if for_quote:
        _sentence_semantics_processing(access_api(quote_prompt3.replace("{sent_text}", sent_text)),
                                       sent_iri, sent_text, nouns_dict, False, ttl_list)
    else:
        _sentence_semantics_processing(access_api(sent_prompt3.replace("{sent_text}", updated_text)),
                                       sent_iri, updated_text, nouns_dict, False, ttl_list)
        # _sentence_semantics_processing(access_api(sent_prompt3.replace("{sent_text}", summary)),
        #                               sent_iri, summary, nouns_dict, True, ttl_list)
    return
