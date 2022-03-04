# Functions to clean up the Turtle (before storage in Stardog)
# Called by create_event_turtle.py

import logging
import uuid

from idiom_processing import get_verb_processing, process_idiom_detail
from nlp import get_head_noun
from query_ontology_and_sources import get_event_state_class
from utilities import empty_string, objects_string, preps_string


def create_verb_label(labels: list, subj_dict: dict, obj_dict: dict, prepositions: list) -> str:
    """
    Creates a summary of the parts of the sentence that were used in defining the Turtle output.

    :param labels: An array of label details
    :param subj_dict: A dictionary of the verb subjects' text (keys) and associated URIs (values)
    :param obj_dict: A dictionary of the verb objects' text (keys) and associated URIs (values)
    :param prepositions: An array of tuples consisting of the preposition's text, and its object text and type
    :returns: A string holding the verb label
    """
    xcomp_text = labels[1]
    using_text = labels[2]
    if subj_dict:
        subj_labels = subj_dict.keys()
    else:
        subj_labels = []
    if obj_dict:
        obj_labels = obj_dict.keys()
    else:
        obj_labels = []
    if labels[3]:
        verb_text = f'{labels[3]} {labels[0]}'
    else:
        verb_text = labels[0]
    if not subj_labels:
        event_label = f'{", ".join(obj_labels)} {xcomp_text}' if xcomp_text else \
            f'{", ".join(obj_labels)} {verb_text}'
    elif not obj_labels:
        event_label = f'{", ".join(subj_labels)} {xcomp_text}' if xcomp_text else \
            f'{", ".join(subj_labels)} {verb_text}'
    else:
        event_label = f'{", ".join(subj_labels)} {xcomp_text} {", ".join(obj_labels)}' \
            if xcomp_text else f'{", ".join(subj_labels)} {verb_text} {", ".join(obj_labels)}'
    for prep in prepositions:
        prep_text, obj_text, obj_type = prep
        if not prep_text:
            continue
        event_label += f' {prep_text} {obj_text}'
    if using_text:
        event_label += using_text
    return event_label


def handle_environment_cleanup(ttl_list: list, obj_dict: dict) -> list:
    """
    Removes the unused object references from the Turtle results when EnvironmentAndCondition which
    are created due to the special processing for the verb, be.

    @param ttl_list: An array of Turtle statements from the processing of the verb, be
    @param obj_dict: A dictionary of object texts and their corresponding IRIs for the verb, be
    @return: The revised list of Turtle statements
    """
    revised_ttl = []
    for turtle in ttl_list:
        keep_ttl = True
        for key, value in obj_dict.items():
            if turtle.startswith(value):
                keep_ttl = False
                break
        if keep_ttl:
            revised_ttl.append(turtle)
    return revised_ttl


def handle_event_state_idiosyncrasies(event_state_turtle: str, sentence: str, subj_dict: dict,
                                      obj_dict: dict, prep_dicts: list, obj_tuples: list,
                                      prep_tuples: list) -> str:
    """
    Handles subj (identified by the text, ':word_detail'), dobj/pobj and xcomp references in a
    parsed idiom rule. These could be resolved in the idiom processing but are not since
    1) there is no difference (or efficiencies to be had) in the code and 2) the processing involves
    calling the get_event_state_class function, which would result in a circular reference from the
    idiom_processing module.

    At this time, subj and xcomp processing does not involve any object references.

    :param event_state_turtle: The Turtle statement resulting from processing an idiom rule
    :param sentence: The sentence text
    :param subj_dict: A dictionary consisting of the verb's subjects' texts as keys and
                      their associated IRIs as values
    :param obj_dict: A dictionary consisting of the verb's objects' texts as keys and their
                     associated IRIs as values
    :param prep_dicts: An array of dictionaries of the verb's prepositional details, which have
                       the preposition text as the key and the object text and type as the value
    :param obj_tuples: An array of tuples consisting of the verb's objects text and type
    :param prep_tuples: An array of tuples consisting of the preposition's text, and its object text,
                        type and URI
    :returns: The updated Turtle statement if 'word_detail', 'dobj', 'pobj' or 'xcomp' text was present in the
             input event_state_turtle
    """
    if 'EnvironmentAndCondition' in event_state_turtle:  # Indicates that a subj_rule was parsed
        subj_uris = []
        for subj_text, subj_uri in subj_dict.items():
            subj_uris.append(subj_uri)
        uri_str = ', '.join(subj_uris)
        if 'subj :Ethnicity' in event_state_turtle:
            event_state_turtle = f'{event_state_turtle.split("; :word_detail")[0]}.'
            return event_state_turtle.replace(':Ethnicity', ':has_agent_aspect').replace('subj', uri_str)
        elif 'subj :PoliticalIdeology' in event_state_turtle:
            event_state_turtle = f'{event_state_turtle.split("; :word_detail")[0]}.'
            return event_state_turtle.replace(':PoliticalIdeology', ':has_political_ideology'). \
                replace('subj', uri_str)
        elif 'subj :LineOfBusiness' in event_state_turtle:
            event_state_turtle = event_state_turtle.replace(':LineOfBusiness', ':has_line_of_business'). \
                replace(':word_detail', ':line_of_business').replace('subj', uri_str)
            return f'{event_state_turtle} .'
        else:
            event_state_turtle = event_state_turtle.split(" subj")[0]
            return f'{event_state_turtle} {uri_str} .'
    if 'xcomp' in event_state_turtle:
        if ', ' in event_state_turtle:
            verb1_text = event_state_turtle.split('(')[1].split(', ')[0]
            verb2_text = event_state_turtle.split(', ')[1].split(')')[0]
        else:
            verb1_text = event_state_turtle.split('(')[1].split(')')[0]
            verb2_text = empty_string
        verb1_class = get_event_state_class(verb1_text)  # Get the Event/State class for the text
        if verb2_text:
            # Check for idiom (already handled the idiom for the first verb)
            # This second verb is the xcomp and has not yet been handled by the idiom processing
            xcomp_verb_dict = dict()
            xcomp_verb_dict['verb_lemma'] = verb2_text
            xcomp_verb_dict[preps_string] = prep_dicts
            verb2_processing = get_verb_processing(xcomp_verb_dict)
            if verb2_processing:
                # TODO: Is it sufficient to take the first result?
                verb2_class = process_idiom_detail(verb2_processing, sentence, xcomp_verb_dict, prep_tuples)[0]
            else:
                verb2_class = get_event_state_class(verb2_text)  # Get the Event/State class for the text
        else:
            # Only have the single verb (due to Ignore), return it
            return f'{event_state_turtle.split("(")[0]}({verb1_class}) .'
        return f'{event_state_turtle.split("(")[0]}({verb1_class}, {verb2_class}) .'
    if 'dobj' in event_state_turtle:
        # Appears as dobj(agent), dobj(location), dobj(verb) or dobj (mutually exclusive)
        obj_uris = []
        for obj_text, obj_type in obj_tuples:
            if 'dobj(verb)' in event_state_turtle:
                # Get the class name for the dobj
                if ' ' in obj_text:
                    obj_text = get_head_noun(obj_text)[0]
                obj_uris.append(get_event_state_class(obj_text))
            elif 'dobj(agent)' not in event_state_turtle and 'dobj(location)' not in event_state_turtle and \
                    'dobj(verb)' not in event_state_turtle:
                obj_uris.append(obj_dict[obj_text])
            elif _verify_uri_requirements(event_state_turtle, obj_type):
                obj_uris.append(obj_dict[obj_text])
        if obj_uris:
            uri_str = ', '.join(obj_uris)
            event_state_turtle = event_state_turtle.replace('dobj(verb)', uri_str).replace('dobj(agent)', uri_str). \
                replace('dobj(location)', uri_str).replace('dobj', uri_str)
        else:
            logging.warning(f'Dobj in processed idiom but not found in sentence, {sentence}')
    if 'pobj' in event_state_turtle:
        # Appears as pobj(agent), pobj(location), pobj(prep_xxx), pobj(prep_xxx)(agent | location)
        # or pobj (mutually exclusive)
        obj_uris = []
        if '(prep_' in event_state_turtle:
            prep_of_interest = event_state_turtle.split('(prep_')[1].split(')')[0]
            # Processing specific to a single preposition
            for preposition, obj_text, obj_type, obj_uri in prep_tuples:
                if preposition == prep_of_interest:
                    if f'pobj(prep_{prep_of_interest})(agent)' not in event_state_turtle and \
                            f'pobj(prep_{prep_of_interest})(location)' not in event_state_turtle:
                        obj_uris.append(obj_uri)
                    elif _verify_uri_requirements(event_state_turtle, obj_type):
                        obj_uris.append(obj_uri)
        else:
            prep_of_interest = ''
            for preposition, obj_text, obj_type, obj_uri in prep_tuples:
                if '(agent)' not in event_state_turtle and '(location)' not in event_state_turtle:
                    obj_uris.append(obj_uri)
                elif _verify_uri_requirements(event_state_turtle, obj_type):
                    obj_uris.append(obj_uri)
        if obj_uris:
            uri_str = ', '.join(obj_uris)
            event_state_turtle = event_state_turtle.replace(f'pobj(prep_{prep_of_interest})(agent)', uri_str). \
                replace(f'pobj(prep_{prep_of_interest})(location)', uri_str). \
                replace(f'pobj(prep_{prep_of_interest})', uri_str). \
                replace('pobj(agent)', uri_str).replace('pobj(location)', uri_str).replace('pobj', uri_str)
        else:
            logging.warning(f'Pobj in processed idiom but not found in sentence, {sentence_text}')
    if event_state_turtle[-1] != '.':
        event_state_turtle += ' .'
    return event_state_turtle


def handle_xcomp_cleanup(turtle: list, event_uri: str, verb_dict: dict, subj_dict: dict,
                         narr_gender: str, last_nouns: list) -> (list, list):
    """
    Handles xcomp cleanup processing for a sentence, which requires adjusting the subject/object,
    and much more.

    :param turtle: The current Turtle definition for the sentence
    :param event_uri: The xcomp event's URI
    :param verb_dict: A dictionary containing the verb details from the NLP parse
    :param subj_dict: A dictionary containing the text of all sentence subjects and their IRIs
    :param narr_gender: Either an empty string or one of the values, AGENDER, BIGENDER, FEMALE or MALE -
                        indicating the gender of the narrator
    :param last_nouns: A list of all noun text and type tuples that is used for co-reference resolution
                       (it is updated with new nouns from the verb prepositions)
    :returns: An array of the revised Turtle statements and any new object details
    """
    if 'xcomp(:Attempt, ' in str(turtle):
        new_turtle = []
        for turtle_stmt in turtle:
            if 'xcomp(:Attempt, ' in turtle_stmt:
                new_turtle.append(turtle_stmt.replace('xcomp(', empty_string).replace(')', empty_string))
            else:
                new_turtle.append(turtle_stmt)
        return new_turtle, []
    # Create new event URI for the scoping event (e.g., "loved to play" - have the event for play,
    #   but need the event for love)
    new_uri = f':Event_{str(uuid.uuid4())[:13]}'
    new_turtle = [f'{new_uri} :has_topic {event_uri}.']
    objects = []
    found_subject = False
    for turtle_stmt in turtle:
        if turtle_stmt.startswith(':Event'):
            if ' a ' in turtle_stmt:
                verb1_class = turtle_stmt.split('(')[1].split(',')[0].strip()
                verb2_class = turtle_stmt.split(', ')[1].split(')')[0].strip()
                new_turtle.append(f'{new_uri} a {verb1_class} .')
                new_turtle.append(f'{event_uri} a {verb2_class} .')
                continue
            elif ':has_latest_end ' in turtle_stmt:
                time_uri = turtle_stmt.split(':has_latest_end ')[1]
                new_turtle.append(f'{event_uri} :has_time {time_uri}')
                new_turtle.append(f'{new_uri} :has_latest_end {time_uri}')
                continue
            new_turtle.append(turtle_stmt)
            if ':text ' in turtle_stmt:
                new_turtle.append(f'{new_uri} :text {turtle_stmt.split(":text ")[1]}')
            elif 'rdfs:label ' in turtle_stmt:
                new_turtle.append(f'{new_uri} rdfs:label {turtle_stmt.split("rdfs:label ")[1]}')
            elif ':has_location' in turtle_stmt:
                new_turtle.append(f'{new_uri} :has_location {turtle_stmt.split(":has_location ")[1]}')
            elif ':has_earliest_beginning ' in turtle_stmt:
                new_turtle.append(f'{new_uri} :has_earliest_beginning '
                                  f'{turtle_stmt.split(":has_earliest_beginning ")[1]}')
            elif ':has_time ' in turtle_stmt:
                new_turtle.append(f'{new_uri} :has_time {turtle_stmt.split(":has_time ")[1]}')
            elif ':has_active_agent ' in turtle_stmt:
                found_subject = True
            elif ':has_origin ' in turtle_stmt:
                new_turtle.append(f'{new_uri} :has_location {turtle_stmt.split(":has_origin ")[1]}')
            elif ':sentiment ' in turtle_stmt:
                new_turtle.append(f'{new_uri} :sentiment {turtle_stmt.split(":sentiment ")[1]}')
    for subj_text, subj_uri in subj_dict.items():
        new_turtle.append(f'{new_uri} :has_active_agent {subj_uri} .')
    if not found_subject and objects_string in verb_dict.keys():
        # Need to add subject/object to the events since the root verb was passive
        # (e.g, "the family was forced to move")
        # Check previous and current sentence nouns
        add_unique_to_array(check_nouns(narr_gender, verb_dict, objects_string, last_nouns), objects)
        obj_dict = _process_subjects_and_objects(objects, sentence_text, new_turtle)
        for obj_text, obj_uri in obj_dict.items():
            new_turtle.append(f'{event_uri} :has_active_agent {obj_uri}')
            new_turtle.append(f'{new_uri} :has_affected_agent {obj_uri}')
    return new_turtle, objects


# Functions internal to the module
def _verify_uri_requirements(event_state_turtle: str, noun_type: str) -> bool:
    """
    Verifies if a noun type meets the requirements of a dobj or pobj reference in a parsed idiom rule.

    :param event_state_turtle: The Turtle statement resulting from processing an idiom rule
    :param obj_type: The type of the object/noun as defined by the spaCy parse
    :returns: A boolean indicating that
    """
    if '(agent)' in event_state_turtle and \
            ('PERSON' in noun_type or 'ORG' in noun_type or 'NORP' in noun_type or 'GPE' in noun_type):
        return True
    elif '(location)' in event_state_turtle and \
            ('GPE' in noun_type or 'LOC' in noun_type or 'FAC' in noun_type):
        return True
    return False
