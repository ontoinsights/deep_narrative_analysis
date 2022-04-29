# Functions to clean up the Turtle (before storage in Stardog)
# Called by create_event_turtle.py

import logging
import os
import pickle
import uuid

from database import query_database
from idiom_processing import get_verb_processing, process_idiom_detail
from nlp import get_head_word
from query_ontology_and_sources import get_event_state_class, get_noun_ttl
from utilities import empty_string, ontologies_database, preps_string, resources_root, space

dobj_verb = 'dobj(verb)'
has_location = ':has_location'

query_permission = 'prefix : <urn:ontoinsights:dna:> SELECT ?permission WHERE { ' \
                   'className rdfs:subClassOf* :Permission . BIND("true" as ?permission) } '

verb_xcomp_file = os.path.join(resources_root, 'verb-xcomp-idioms.pickle')
with open(verb_xcomp_file, 'rb') as inFile:
    verb_xcomp_dict = pickle.load(inFile)


def create_using_details(verb_dict: dict, event_iri: str, sent_text: str, turtle: list,
                         last_nouns: list, processed_locs: dict) -> str:
    """
    Special case processing if the word, 'using', is in the sentence.
    
    :param verb_dict: The dictionary entry for the verb in the current sentence
    :param event_iri: String holding the IRI identifier of the verb/event
    :param sent_text: The full text of the sentence (needed for checking for idioms)
    :param turtle: An array of the current Turtle for the sentence
    :param last_nouns: A list of all noun text, type and IRI tuples that have been defined
                       (also used for co-reference resolution)
    :param processed_locs: A dictionary of location texts (keys) and their IRI (values) of
                           all locations already processed
    :returns: A string holding additional label text, if the word 'using' is in the sentence;
              Otherwise, returns an empty_string 
    """
    # Special case for the word, 'using'
    using_label = empty_string
    if 'verb_advcl' in verb_dict.keys():
        advcl_text = str(verb_dict['verb_advcl'])
        if "'verb_lemma': 'use'" in advcl_text:
            inst_text = advcl_text.split("object_text': '")[1]
            inst_text2 = inst_text[:inst_text.index("',")]
            inst_type = advcl_text.split("object_type': '")[1]
            inst_type2 = inst_type[:inst_type.index("'}")]
            inst_iri = f':{inst_text2.replace(" ", "_")}_{str(uuid.uuid4())[:13]}'
            turtle.append(f'{event_iri} :has_instrument {inst_iri} .')
            inst_ttl = get_noun_ttl(inst_iri, inst_text2, inst_type2, sent_text, last_nouns, processed_locs)
            if inst_ttl:
                turtle.extend(inst_ttl)
            using_label = f' using {inst_text2}'
    return using_label


def create_verb_label(labels: list, subj_tuples: list, obj_tuples: list, prep_tuples: list, negated: bool) -> str:
    """
    Creates a text summary of the sentence.

    :param labels: An array of label details - verb_label, xcomp_label, using_label, aux_label
    :param subj_tuples: An array of tuples consisting of the verb's subjects' text, type and IRI
    :param obj_tuples: An array of tuples consisting of the verb's objects' text, type and IRI
    :param prep_tuples: An array of tuples consisting of the verb's prepositions' text, and its objects'
                        text, type and IRI
    :param negated: Boolean indicating that the verb is negated
    :returns: A string holding the sentence summary, which becomes the event label
    """
    subj_labels = []
    if subj_tuples:
        for subj_text, subj_type, subj_iri in subj_tuples:
            subj_labels.append(subj_text)
    obj_labels = []
    if obj_tuples:
        for obj_text, obj_type, obj_iri in obj_tuples:
            obj_labels.append(obj_text)
    if labels[3]:           # aux_label
        verb_text = f'{labels[3]} {labels[0]}'
    else:
        verb_text = labels[0]
    xcomp_text = labels[1]
    if not subj_labels:
        event_label = f'{", ".join(obj_labels)} {xcomp_text}' if xcomp_text else \
            f'{", ".join(obj_labels)} {verb_text}'
    elif not obj_labels:
        event_label = f'{", ".join(subj_labels)} {xcomp_text}' if xcomp_text else \
            f'{", ".join(subj_labels)} {verb_text}'
    else:
        event_label = f'{", ".join(subj_labels)} {xcomp_text} {", ".join(obj_labels)}' \
            if xcomp_text else f'{", ".join(subj_labels)} {verb_text} {", ".join(obj_labels)}'
    for prep_text, obj_text, obj_type, obj_iri in prep_tuples:
        if not prep_text or not obj_text:
            continue
        if prep_text != 'after' and not (obj_type.endswith('GPE') or obj_type.endswith('LOC')
                                         or obj_type.endswith('FAC')):
            # "after xxx" designates a time which may not be part of the main subject/verb and likely confusing
            event_label += f' {prep_text} {obj_text}'
    if labels[2]:
        event_label += labels[2]
    if negated:
        return f'Negated: {event_label}'
    return event_label


def handle_environment_cleanup(ttl_list: list, obj_tuples: list) -> list:
    """
    Removes the unused object references from the Turtle results when EnvironmentAndCondition statements
    are created due to the special processing for the verb, be.

    :param ttl_list: An array of Turtle statements from the processing of the verb, be
    :param obj_tuples: An array of object texts, types and their corresponding IRIs for the verb, be
    :returns: The revised list of Turtle statements
    """
    revised_ttl = []
    for turtle in ttl_list:
        keep_ttl = True
        for obj_text, obj_type, obj_iri in obj_tuples:
            if turtle.startswith(obj_iri):
                keep_ttl = False
                break
        if keep_ttl:
            revised_ttl.append(turtle)
    return revised_ttl


def handle_event_state_idiosyncrasies(event_state_turtle: str, sentence: str, verb_dict: dict, subj_tuples: list,
                                      obj_tuples: list, prep_tuples: list) -> str:
    """
    Handles subj (identified by the text, ':word_detail'), dobj/pobj and xcomp references in a
    parsed idiom rule. These could be resolved in the idiom processing but are not since
    1) there is no difference (or efficiencies to be had) in the code and 2) the processing involves
    calling the get_event_state_class function, which would result in a circular reference from the
    idiom_processing module.

    At this time, subj and xcomp processing does not involve any object references.

    :param event_state_turtle: The Turtle statement resulting from processing an idiom rule
    :param sentence: The sentence text
    :param verb_dict: The verb details from the sentence dictionary
    :param subj_tuples: An array of tuples consisting of the verb's subjects' text, type and IRI
    :param obj_tuples: An array of tuples consisting of the verb's objects' text, type and IRI
    :param prep_tuples: An array of tuples consisting of the verb's prepositions' text, and its objects'
                        text, type and IRI
    :returns: The updated Turtle statement if 'word_detail', 'dobj', 'pobj' or 'xcomp' text was present in the
             input event_state_turtle
    """
    if 'EnvironmentAndCondition' in event_state_turtle:  # Indicates that a subj_rule was parsed
        subj_iris = []
        for subj_text, subj_type, subj_iri in subj_tuples:
            subj_iris.append(subj_iri)
        iri_str = ', '.join(subj_iris)
        event_state_turtle = _clean_environment_condition(event_state_turtle, obj_tuples, iri_str)
    if 'xcomp' in event_state_turtle:    # Appears as ':Event_xyz a xcomp(root_verb_text, xcomp_verb_text)'
        # Should always have 2 verbs, the root and the xcomp
        verb1_text = event_state_turtle.split('(')[1].split(', ')[0]
        verb2_text = event_state_turtle.split(', ')[1].split(')')[0]
        # Determine if the first verb has an idiom defined
        if verb1_text in verb_xcomp_dict.keys():
            verb1_class = verb_xcomp_dict[verb1_text]
        else:
            verb1_class = get_event_state_class(verb1_text)  # Get the Event/State class for the text
        # Check for second verb having an idiom (already handled the idiom for the first verb)
        xcomp_verb_dict = dict()
        xcomp_verb_dict['verb_lemma'] = verb2_text
        if preps_string in verb_dict.keys():
            xcomp_verb_dict[preps_string] = verb_dict[preps_string]
        verb2_processing = get_verb_processing(xcomp_verb_dict)
        if verb2_processing:
            # TODO: Is it sufficient to take the first result?
            verb2_class = process_idiom_detail(verb2_processing, sentence, xcomp_verb_dict, prep_tuples)[0]
            verb2_class = handle_event_state_idiosyncrasies(verb2_class, sentence, verb_dict, subj_tuples,
                                                            obj_tuples, prep_tuples)
        else:
            verb2_class = get_event_state_class(verb2_text)  # Get the Event/State class for the text
        return f'{event_state_turtle.split("(")[0]}({verb1_class}, {verb2_class}) .'
    if 'dobj' in event_state_turtle:
        # Appears as dobj(Agent), dobj(Location), dobj(verb) or dobj (mutually exclusive)
        obj_iris = []
        for obj_text, obj_type, obj_iri in obj_tuples:
            if dobj_verb in event_state_turtle:
                # Get the class name for the dobj
                if space in obj_text:
                    obj_text = get_head_word(obj_text)[0]
                obj_iris.append(get_event_state_class(obj_text))
            elif 'dobj(Agent)' not in event_state_turtle and 'dobj(Location)' not in event_state_turtle and \
                    dobj_verb not in event_state_turtle:
                obj_iris.append(obj_iri)
            elif _verify_iri_requirements(event_state_turtle, obj_type):
                obj_iris.append(obj_iri)
        if obj_iris:
            iri_str = ', '.join(obj_iris)
            event_state_turtle = event_state_turtle.replace(dobj_verb, iri_str).replace('dobj(Agent)', iri_str). \
                replace('dobj(Location)', iri_str).replace('dobj', iri_str)
        else:
            logging.warning(f'Dobj in processed idiom but not found in sentence, {sentence}')
    if 'pobj' in event_state_turtle:
        # Appears as pobj(Agent), pobj(Location), pobj(prep_xxx), pobj(prep_xxx)(Agent | Location)
        # or pobj (mutually exclusive)
        obj_iris = []
        if '(prep_' in event_state_turtle:
            prep_of_interest = event_state_turtle.split('(prep_')[1].split(')')[0]
            # Processing specific to a single preposition
            for preposition, obj_text, obj_type, obj_iri in prep_tuples:
                if preposition == prep_of_interest and \
                        (f'pobj(prep_{prep_of_interest})(Agent)' not in event_state_turtle and
                         f'pobj(prep_{prep_of_interest})(Location)' not in event_state_turtle) or \
                        _verify_iri_requirements(event_state_turtle, obj_type):
                    obj_iris.append(obj_iri)
        else:
            prep_of_interest = ''
            for preposition, obj_text, obj_type, obj_iri in prep_tuples:
                if ('(Agent)' not in event_state_turtle and '(Location)' not in event_state_turtle) or \
                        _verify_iri_requirements(event_state_turtle, obj_type):
                    obj_iris.append(obj_iri)
        if obj_iris:
            iri_str = ', '.join(obj_iris)
            event_state_turtle = event_state_turtle.replace(f'pobj(prep_{prep_of_interest})(Agent)', iri_str). \
                replace(f'pobj(prep_{prep_of_interest})(Location)', iri_str). \
                replace(f'pobj(prep_{prep_of_interest})', iri_str). \
                replace('pobj(Agent)', iri_str).replace('pobj(Location)', iri_str).replace('pobj', iri_str)
        else:
            logging.warning(f'Pobj in processed idiom but not found in sentence, {sentence}')
    if event_state_turtle[-1] != '.':
        event_state_turtle += ' .'
    return event_state_turtle


def handle_xcomp_cleanup(turtle: list, event_iri: str, subj_tuples: list, is_xcomp_subjects: bool) -> list:
    """
    Handles xcomp cleanup processing for a sentence, which requires adjusting the subject/object,
    and much more.

    :param turtle: The current Turtle definition for the sentence
    :param event_iri: The xcomp event's IRI
    :param subj_tuples: An array containing the sentence/event's subjects' text, type and IRI
    :param is_xcomp_subjects: Boolean indicating that the subjects come from the root verb,
                              which is passive
    :returns: An array of the revised Turtle statements and any new object details
    """
    # Attempt or Ignore as the first verb means that a scoping root event is not needed
    if 'xcomp(:Attempt, ' in str(turtle) or 'xcomp(:Ignore, ' in str(turtle):
        new_turtle = []
        for turtle_stmt in turtle:
            if 'xcomp(:Attempt, ' in turtle_stmt:
                new_turtle.append(turtle_stmt.replace('xcomp(', empty_string).replace(')', empty_string))
            elif 'xcomp(:Ignore, ' in turtle_stmt:
                new_turtle.append(turtle_stmt.replace('xcomp(:Ignore, ', empty_string).replace(')', empty_string))
            else:
                new_turtle.append(turtle_stmt)
        return new_turtle
    # It may happen that a location is added and then refined (in idiom processing of the xcomp verb)
    #    to has_origin/destination. If so, the original :has_location predicate should be removed.
    turtle_str = str(turtle)
    ignore_has_location = False
    if has_location in turtle_str and (':has_origin' in turtle_str or ':has_destination' in turtle_str):
        ignore_has_location = True
    # Create new event IRI for the scoping event (e.g., "loved to play" - have the event for play,
    #   but need the event for love)
    new_iri = f':Event_{str(uuid.uuid4())[:13]}'
    new_turtle = [f'{new_iri} :has_topic {event_iri}.']
    # Get the type of ROOT event
    scope_permission = False
    for turtle_stmt in turtle:
        if ' a xcomp' in turtle_stmt:
            verb1_class = turtle_stmt.split('(')[1].split(',')[0].strip()
            if query_database('select', query_permission.replace('className', verb1_class), ontologies_database):
                scope_permission = True
                # TODO: Not permitted, negates the event - Either RefusalAndRejection or negated Permission
            break
    # Update the Turtle and add the new scoping event
    for turtle_stmt in turtle:
        if turtle_stmt.startswith(':Event'):
            if ' a xcomp' in turtle_stmt:
                verb1_class = turtle_stmt.split('(')[1].split(',')[0].strip()
                verb2_class = turtle_stmt.split(', ')[1].split(')')[0].strip()
                if verb2_class.endswith(' .'):
                    # Would happen if the second verb was also an idiom
                    verb2_class = verb2_class[:-2]
                new_turtle.append(f'{new_iri} a {verb1_class} .')
                new_turtle.append(f'{event_iri} a {verb2_class} .')
                continue
            elif ':has_latest_end ' in turtle_stmt:
                time_iri = turtle_stmt.split(':has_latest_end ')[1]
                if scope_permission:
                    new_turtle.append(f'{new_iri} :before {event_iri} .')
                    new_turtle.append(f'{event_iri} :has_time {time_iri}')
                    new_turtle.append(f'{new_iri} :has_latest_end {time_iri}')
                else:
                    new_turtle.append(turtle_stmt)
                    new_turtle.append(f'{new_iri} :has_latest_end {time_iri}')
                continue
            elif ':has_earliest_beginning ' in turtle_stmt:
                time_iri = turtle_stmt.split(':has_earliest_beginning ')[1]
                if scope_permission:
                    new_turtle.append(f'{new_iri} :before {event_iri} .')
                new_turtle.append(turtle_stmt)
                new_turtle.append(f'{new_iri} :has_earliest_beginning {time_iri}')
                continue
            elif ':has_time ' in turtle_stmt:
                time_iri = turtle_stmt.split(':has_time ')[1]
                if scope_permission:
                    new_turtle.append(f'{new_iri} :before {event_iri} .')
                    new_turtle.append(f'{event_iri} :has_earliest_beginning {time_iri}')
                    new_turtle.append(f'{new_iri} :has_time {time_iri}')
                else:
                    new_turtle.append(turtle_stmt)
                    new_turtle.append(f'{new_iri} :has_time {time_iri}')
                continue
            elif has_location in turtle_stmt and ignore_has_location:
                continue
            new_turtle.append(turtle_stmt)
            if ':text ' in turtle_stmt:
                new_turtle.append(f'{new_iri} :text {turtle_stmt.split(":text ")[1]}')
            elif 'rdfs:label ' in turtle_stmt:
                new_turtle.append(f'{new_iri} rdfs:label {turtle_stmt.split("rdfs:label ")[1]}')
            elif ':has_active_agent ' in turtle_stmt:
                if is_xcomp_subjects:
                    new_turtle.append(f'{new_iri} :has_affected_agent {turtle_stmt.split(":has_active_agent ")[1]}')
            elif has_location in turtle_stmt:
                new_turtle.append(f'{new_iri} {has_location} {turtle_stmt.split(":has_location ")[1]}')
            elif ':has_origin ' in turtle_stmt:
                new_turtle.append(f'{new_iri} {has_location} {turtle_stmt.split(":has_origin ")[1]}')
            elif ':sentiment ' in turtle_stmt:
                new_turtle.append(f'{new_iri} :sentiment {turtle_stmt.split(":sentiment ")[1]}')
        else:
            new_turtle.append(turtle_stmt)
    if not is_xcomp_subjects:
        for subj_text, subj_type, subj_iri in subj_tuples:
            new_turtle.append(f'{new_iri} :has_active_agent {subj_iri} .')
    return new_turtle


# Functions internal to the module
def _clean_environment_condition(turtle: str, object_tuples: list, iri: str) -> str:
    """
    Updates the Turtle for a subject/EnvironmentAndCondition statement.

    :param turtle: The original Turtle from idiom processing
    :param object_tuples: An array of tuples consisting of the verb's objects' text, type and IRI
    :param iri: The IRI identifying the subject/holder of the environment/condition
    :returns: The updated Turtle statement
    """
    topic = 'owl:Thing'
    word = 'unknown'
    if 'has_topic ' in turtle:
        if ' dobj' not in turtle:
            topic = turtle.split('has_topic ')[1].split(space)[0]
        elif ' dobj' in turtle and not object_tuples:    # Possible for a verb to have no objects, just adverbs
            turtle = turtle.replace(':has_topic dobj ; ', empty_string)   # So, remove the triple
    if 'word_detail' in turtle:
        word = turtle.split('word_detail ')[1].split(space)[0]
    if 'LineOfBusiness' in turtle:
        turtle = f'{turtle.replace("LineOfBusiness", empty_string).replace(":word_detail", "rdfs:label")} . ' \
                 f'subj :has_line_of_business {topic} ; :line_of_business {word} .'
    elif 'PoliticalIdeology' in turtle:
        turtle = f'{turtle.replace("PoliticalIdeology", empty_string).replace(":word_detail", "rdfs:label")} . ' \
                 f'subj :has_agent_aspect {topic} .'
    elif 'Ethnicity' in turtle:
        turtle = f'{turtle.replace("Ethnicity", empty_string).replace(":word_detail", "rdfs:label")} . ' \
                 f'subj :has_agent_aspect {topic} .'
    return turtle.replace('subj', iri).replace("'", '"')


def _verify_iri_requirements(event_state_turtle: str, noun_type: str) -> bool:
    """
    Verifies if a noun type meets the requirements of a dobj or pobj reference in a parsed idiom rule.

    :param event_state_turtle: The Turtle statement resulting from processing an idiom rule
    :param noun_type: The type of the object/noun as defined by the spaCy parse
    :returns: A boolean indicating that
    """
    if ('(Agent)' in event_state_turtle and
            (noun_type.endswith('PERSON') or noun_type.endswith('ORG') or noun_type.endswith('NORP') or
             noun_type.endswith('GPE'))) or \
            ('(Location)' in event_state_turtle and
             (noun_type.endswith('GPE') or noun_type.endswith('LOC') or noun_type.endswith('FAC'))):
        return True
    # TODO: May have a NOUN but its definition could indicate an agent or location / Does using WordNet address this?
    return False
