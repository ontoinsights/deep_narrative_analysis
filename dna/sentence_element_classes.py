# Narrative details class structure

import logging
import uuid
from enum import Enum

from dna.query_openai import categories
from dna.utilities_and_language_specific import empty_string, ner_dict, plural_pronouns

modals = ("can ", "could ", "have to ", "may ", "might ", "must ", "ought to ", "shall ", "should ", "would ")
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


def _get_class_details(topics: list, tense: str, verb_text: str, sentence_text: str) -> list:
    """
    Get the DNA class names that are the semantics of the verb phrase

    :param topics: Integers representing the DNA class names (selected by OpenAI) and a boolean
                   indicating that the class is negated
    :param tense: Tense of the verb phrase
    :param verb_text: String holding the verb phrase text
    :param sentence_text: String holding the full sentence text (in case of errors)
    :return: Array of DNA class names applicable to the verb phrase
    """
    class_names = []
    negated_class_names = []
    # TODO: Other special cases?
    env_condition = False
    econ_env = False
    if len(topics) > 1:
        for topic in topics:
            topic_number = topic['topic_number']
            if topic_number == 31:
                env_condition = True
            if topic_number == 32:
                econ_env = True
    for topic in topics:
        if env_condition:
            continue   # Ignore EnvironmentAndCondition (31) which is often returned by OpenAI unless is only topic
        if topic['topic_number'] == 4 and econ_env:
            continue   # Economic/environmental disaster != AggressiveCriminalOrHostileAct
        if 0 < topic['topic_number'] < len(categories) + 1:       # A valid topic #
            class_name = categories[topic['topic_number'] - 1]
        else:
            logging.error(f'Invalid semantic category ({topic}) for {verb_text} in "{sentence_text}"')
        if class_name:
            if topic['topic_negated']:
                negated_class_names.append(class_name)
            else:
                class_names.append(class_name)
    for modal in modals:
        if modal in verb_text.lower():
            modal_key = modal[:-1]
            # Some modifications based on tense
            if modal == 'can ':
                modal_key = 'can-present' if tense == 'present' else 'can-not-present'
            elif modal == 'could ':
                modal_key = 'could-past' if tense == 'past' else 'could-not-past'
            class_names.append(modal_mapping[modal_key])
    if not class_names and not negated_class_names:
        return [':EventAndState'], []
    return class_names, negated_class_names


class Associated:
    """
    Class holding noun phrase and clause details related to a verb in a sentence
    """
    trigger_text: str = empty_string     # Specific text of the noun or clausal phrase related to the sem role
    full_text: str = empty_string        # Full text of the associated entity
    class_name: str = empty_string       # Array of DNA class names that reflect the text
    semantic_role: str = empty_string    # Semantic role of the trigger_text
    negated: bool = False
    iri: str = empty_string              # IRI for the instance

    def __init__(self, trigger_text: str, full_text: str, class_name: str, semantic_role: str, singular: bool,
                 negated: bool, iri: str):
        self.trigger_text = trigger_text
        self.full_text = full_text
        # TODO: Handle OpenAI singular/plural determination errors for complex text phrases
        #  if (not singular or text in plural_pronouns) and ':Collection' not in class_name:
        #     class_name += ', :Collection'
        self.class_name = class_name
        self.semantic_role = semantic_role
        self.negated = True if negated else False
        self.iri = iri


class Event:
    """
    Class holding event/state details (verb and associated noun/clause) for a narrative/article
    """
    text: str = empty_string               # Text of a full verb phrase
    class_names: list = []                 # Array of DNA class names that reflect the verb phrase semantics
    negated_class_names: list = []
    future: bool = False
    iri: str = empty_string                # Event IRI (in resulting Turtle)

    def __init__(self, verb_dict: dict, verb_semantic_dict: dict, sentence_text: str):
        full_phrase = verb_dict['full_verb_phrase']
        self.text = full_phrase
        # Get the DNA class names that are the semantics of the verb phrase
        self.class_names, self.negated_class_names = \
            _get_class_details(verb_semantic_dict['topics'], verb_semantic_dict['tense'], full_phrase, sentence_text)
        self.future = True if verb_semantic_dict['tense'] == 'future' else False
        self.iri = f':Event_{str(uuid.uuid4())[:13]}'


class Metadata:
    """
    Class holding metadata details for a narrative/article
    """
    title: str = empty_string            # Narrative/article title
    published: str = empty_string        # Date/time published
    source: str = empty_string           # Source (such as 'CNN', free-form)
    url: str = empty_string              # Online location
    number_to_ingest: int = 1            # Number of sentences to ingest

    def __init__(self, title: str, published: str, source: str, url: str, number_to_ingest: int):
        self.title = title
        self.published = published
        self.source = source
        self.url = url
        self.number_to_ingest = number_to_ingest
