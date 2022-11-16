# Processing of verbs
# Called by create_narrative_turtle.py

import logging
# from textblob import TextBlob
import uuid

from dna.coreference_resolution import check_nouns
from dna.create_labels import create_verb_label, get_prt_label, get_xcomp_labels
from dna.create_noun_turtle import create_using_details
from dna.create_specific_turtle import create_type_turtle
from dna.create_verb_turtle import add_subj_obj_to_ttl, create_ttl_for_prep_detail, handle_locations, \
    handle_xcomp_processing
from dna.get_ontology_mapping import get_event_state_mapping
from dna.nlp import get_named_entities_in_string
from dna.process_times import process_chunk_time
from dna.query_ontology import check_emotion_loc_movement
from dna.utilities_and_language_specific import add_unique_to_array, aux_verb_dict, empty_string, subjects_string, \
    objects_string, preps_string


# TODO: Is last_events complete? Check nouns + verbs.


def _check_verb_person_mappings(mappings: list, objs: list) -> list:
    """
    If mappings have an alternative with a class mapping of verb + Person, then check the verb's objects.
    If they are a Person, choose that mapping over the others.

    :param mappings: A list of strings holding possible alternative ontology mappings for the verb
    :param objs: Array of tuples that are the noun text, type, mappings and IRI for the sentence's objects
    :return: The evaluated mappings (which may be modified)
    """
    if len(mappings) == 1:
        return mappings     # No alternatives
    new_mappings = []
    for mapping in mappings:
        if '+' in mapping and (':Person' in mapping or ':NegPerson' in mapping):
            for obj in objs:
                text, noun_type, noun_mappings, iri = obj
                if 'PERSON' in noun_type:
                    if ':Person' in mapping:
                        return [mapping.replace('urn:ontoinsights:dna:Person', empty_string).
                                replace(':Person', empty_string).replace('+', empty_string)]
                    else:
                        continue
            # No Person, so don't save that mapping
            continue
        else:
            new_mappings.append(mapping)
    return new_mappings


def _get_preposition_tuples(prep_dict: dict) -> list:
    """
    Extracts the details from the preposition dictionary of a verb.

    :param prep_dict: A dictionary holding the details for a single preposition for a verb.
                      For example, "{'prep_text': 'with', 'prep_details': [{'detail_text': 'other children',
                      'detail_type': 'PLURALNOUN'}]}"
    :return: An array holding tuples consisting of the preposition text, and the preposition's object
             text and type
    """
    prep_details = []
    if 'prep_details' in prep_dict:
        for prep_detail in prep_dict['prep_details']:
            if 'detail_text' in prep_detail:
                prep_detail_type = prep_detail['detail_type']   # If there is _text, there will also be _type
                if prep_detail_type.endswith('DATE') or prep_detail_type.endswith('TIME') or  \
                        prep_detail_type.endswith('EVENT'):
                    # Time-related - so, this is already handled => ignore
                    continue
                prep_details.append((prep_dict['prep_text'].lower(), prep_detail['detail_text'], prep_detail_type))
    return prep_details


def _get_xcomp_root_objects(xcomp_dict: dict, chunk_dict: dict) -> list:
    """
    Extract the texts of any nouns that are objects of the root verb.

    :param xcomp_dict: A dictionary with keys = root verb and the xcomp verb and values = 'root' for
                       the root verb or the verb_processing string for the xcomp
    :param chunk_dict: Dictionary holding the chunk details
    :return: An array of strings of the nouns that are objects of the root verb of the xcomp
    """
    chunk_objects = []
    if xcomp_dict:
        for verb, processing in xcomp_dict.items():
            if processing == 'root':
                # Get the root verb details
                for chunk_verb in chunk_dict['verbs']:
                    lemma = chunk_verb['verb_lemma']
                    if lemma == verb:
                        if objects_string in chunk_verb:    # Get the objects that are specific to the verb
                            add_unique_to_array(check_nouns(chunk_verb, objects_string, dict(), [],
                                                [], [], False), chunk_objects)
                            # TODO: Also get prepositional objects?
    if chunk_objects:
        root_texts = []
        for chunk_object in chunk_objects:
            obj_text, obj_type, obj_map, obj_iri = chunk_object
            root_texts.append(obj_text)
        return root_texts
    return []


def _process_aux_verb(verb_dict: dict, chunk_text: str) -> list:
    """
    Determines the mapping of the auxiliary verb to the DNA ontology, including whether the
    verb indicates an emotion, mood or modal - which affects the overall sentiment of the sentence.

    :param verb_dict: The dictionary for the verb
    :param chunk_text: Text of the sentence
    :return: A list holding the possible class names implied by the aux verb (which could be an
             empty list if the aux can be ignored)
    """
    if 'verb_aux' in verb_dict:
        inclusive = chunk_text.startswith('I ') or chunk_text.startswith('We ') or chunk_text.startswith('we ') or \
                    " I " in chunk_text or " we " in chunk_text
        aux_label = verb_dict['verb_aux']
        if aux_label in aux_verb_dict:
            aux_mapping = aux_verb_dict[aux_label]
            if ',' in aux_mapping:
                auxs = aux_mapping.split(',')
                class_mapping = [auxs[0] if inclusive else auxs[1]]
            else:
                class_mapping = [aux_mapping]
            return class_mapping
        else:
            if aux_label in ('be', 'do', 'have', 'become'):      # Main verb defines the event/state
                return []     # No change to that verb
            # Determine if the aux verb is an emotion/mood by getting the Event/State class for the text
            keep_aux, class_mapping = get_event_state_mapping(aux_label, dict(), [], [], 'iri', [])
            if not keep_aux:
                return []
            return check_emotion_loc_movement(class_mapping, 'emotion')


def _process_subjs_objs(chunk_dict: dict, alet_dict: dict, last_nouns: list, last_events: list,
                        subj_obj_str: str, ext_sources: bool) -> (list, list):
    """
    Given the details of a chunk, capture the concepts of its top-level subjects or objects
    (depending on the value of the subj_obj_str), and return the noun details and Turtle statements.

    :param chunk_dict: The sentence/chunk dictionary from the spaCy parse
    :param alet_dict: A dictionary holding the agents, locations, events & times encountered in
             the narrative to-date - For co-reference resolution (it may be updated by this function);
             Keys = 'agents', 'locs', 'events', 'times' and Values that vary for the different keys
    :param last_nouns: An array of noun texts, type, class mapping and IRI from the current paragraph
    :param last_events: A list/array of tuples defining an event DNA class mapping and IRI, found in the
                        current paragraph
    :param subj_obj_str: String = either 'subjects' or 'objects'
    :param ext_sources: A boolean indicating that data from GeoNames, Wikidata, etc. should be
                        added to the parse results if available
    :return: A tuple consisting of two arrays - the first holding tuples (nouns' text, type,
             class mappings and IRI) related to either the subject or object nouns, and the
             second holding their defining Turtle statements.
    """
    noun_tuples = []
    noun_ttl = []
    if subj_obj_str in chunk_dict:
        # Get the relevant nouns (text, type, mappings and IRI) and resolve co-references
        noun_tuples = check_nouns(chunk_dict, subj_obj_str, alet_dict, last_nouns,
                                  last_events, noun_ttl, ext_sources)
    return noun_tuples, noun_ttl


def _process_xcomp_prt(chunk_dict: dict) -> (dict, dict, bool):
    """
    Extract any 'verb_processing' details for the chunk.

    :param chunk_dict: The dictionary from the spaCy parse for the chunk
    :return: A tuple consisting of a dictionary holding xcomp processing details, a dictionary
             holding prt processing details and a boolean indicating that subjects and objects
             are switched (which is done for passive verbs)
    """
    # xcomp - for ex, 'she loved to play with her sister' => 'love' is root, 'play' is xcomp
    # These verbs are both found in the same chunk_dict['verbs'] array
    xcomp_dict = dict()
    # prt - for ex, 'she gave up the prize' => 'give' is root, 'up' is prt
    prt_dict = dict()
    if 'verb_processing' in chunk_dict:
        for processing in chunk_dict['verb_processing']:
            if 'xcomp' in processing:    # For example, 'xcomp > love, play'
                xcomp_dict[processing.split(', ')[1]] = processing
                xcomp_dict[processing.split('> ')[1].split(',')[0]] = 'root'
            elif 'prt' in processing:    # For example, 'prt > give, up'
                prt_dict[processing.split('prt > ')[1].split(' ')[0]] = processing
    return xcomp_dict, prt_dict, \
        True if (subjects_string not in chunk_dict and objects_string in chunk_dict) else False


def process_verb(chunk_iri: str, chunk_dict: dict, alet_dict: dict, loc_time_iris: list, last_nouns: list,
                 last_events: list, ext_sources: bool, is_bio: bool) -> (str, list):
    """
    Generate the Turtle for the root event/verb of a chunk, based on the details in the verb's
    dictionary.

    :param chunk_iri: String IRI identifying the current chunk
    :param chunk_dict: The sentence/chunk dictionary from the spaCy parse
    :param alet_dict: A dictionary holding the agents, locations, events & times encountered in
             the narrative to-date - For co-reference resolution (it may be updated by this function);
             Keys = 'agents', 'locs', 'events', 'times' and Values that vary for the different keys
    :param loc_time_iris: An array holding the last processed location (index 0) and time (index 1)
    :param last_nouns: An array of noun texts, type, class mapping and IRI from the current paragraph
    :param last_events: A list/array of tuples defining an event DNA class mapping and IRI, found in the
                        current paragraph
    :param ext_sources: A boolean indicating that data from GeoNames, Wikidata, etc. should be
                        added to the parse results if available
    :param is_bio: A boolean indicating that the text is biographical/autobiographical
    :return: A list of Turtle statements defining the event(s) in the chunk
    """
    chunk_text = chunk_dict['chunk_text']
    logging.info(f'Processing chunk, {chunk_text}')
    ttl_list = []
    event_iri = f':Event_{str(uuid.uuid4())[:13]}'
    named_entities = get_named_entities_in_string(chunk_text)
    # Determine chunk time
    new_time = process_chunk_time(chunk_text, named_entities, event_iri, loc_time_iris[1], alet_dict,
                                  is_bio, ttl_list)
    loc_time_iris[1] = new_time if new_time else loc_time_iris[1]
    # Get subjects and objects
    init_subjects, subj_ttl = _process_subjs_objs(chunk_dict, alet_dict, last_nouns,
                                                  last_events, subjects_string, ext_sources)
    ttl_list.extend(subj_ttl)    # Subject Turtle is always added
    init_objects, obj_ttl = _process_subjs_objs(chunk_dict, alet_dict, last_nouns,
                                                last_events, objects_string, ext_sources)
    # Note that obj_ttl may not be added if an auxiliary verb is the main/root verb (for ex, 'John is an attorney')
    xcomp_dict, prt_dict, switch_subj_obj = _process_xcomp_prt(chunk_dict)
    if xcomp_dict and switch_subj_obj:    # Passive root verb => 'subjects' are defined as the chunk's objects
        subjects = init_objects           # Only switch for xcomp and if the switch_ variable is true
        objects = init_subjects
    else:
        subjects = init_subjects
        objects = init_objects
    root_objects = _get_xcomp_root_objects(xcomp_dict, chunk_dict)    # Need this detail for the label
    root_text = empty_string
    xcomp_root_mappings = []
    for verb in chunk_dict['verbs']:
        if objects_string in verb:    # Get the objects that are specific to the verb
            add_unique_to_array(check_nouns(verb, objects_string, alet_dict, last_nouns,
                                            last_events, ttl_list, ext_sources), objects)
        lemma = verb['verb_lemma']
        # Get and process the prepositions and their objects
        prepositions = []        # List of tuples (preposition text, and object text, type, class mappings and IRI)
        prep_ttl = []            # Turtle related to prepositional objects
        loc_iri = empty_string
        if preps_string in verb:
            for prep_dict in verb[preps_string]:
                # An array of tuples of the prep & object text/type/mapping(s) to the DNA ontology
                prep_details = _get_preposition_tuples(prep_dict)
                # Get IRI and add Turtle for the objects (if new)
                for prep_detail in prep_details:
                    prep_turtle, prep_loc_iri = \
                        create_ttl_for_prep_detail(prep_detail, prepositions, event_iri, alet_dict,
                                                   last_nouns, last_events, objects, ext_sources)
                    prep_ttl.extend(prep_turtle)
                    loc_iri = prep_loc_iri if prep_loc_iri else loc_iri
        ttl_list.extend(prep_ttl)
        event_state_mappings = []
        # First deal with the auxiliary verbs
        aux_mappings = _process_aux_verb(verb, chunk_text)
        if aux_mappings:
            # Future: Code assumes that there is only 1 mapping for an aux verb and no xcomp; Is this valid?
            aux_map = aux_mappings[0]
            if 'Emotion' in aux_map:
                xcomp_dict[lemma] = f'xcomp > {verb["verb_aux"]}, {lemma}'
            else:
                ttl_list.append(f'{event_iri} a {aux_map.replace("+", ", ")} .')
        # Second deal with prt verbs
        if 'verb_processing' in chunk_dict and prt_dict and lemma in prt_dict:
            event_state_mappings = \
                get_event_state_mapping(prt_dict[lemma].split('prt > ')[1], verb, subjects, objects,
                                        event_iri, ttl_list)
        # Third deal with the root and xcomp verbs
        if 'verb_processing' in chunk_dict and xcomp_dict and lemma in xcomp_dict \
                and xcomp_dict[lemma].startswith('xcomp'):
            if not event_state_mappings:     # Might have a mapping if the lemma is part of prt processing
                event_state_mappings = get_event_state_mapping(lemma, verb, subjects, objects, event_iri, ttl_list)
            root_text = xcomp_dict[lemma].split('xcomp > ')[1].split(',')[0]
            xcomp_root_mappings = get_event_state_mapping(root_text, verb, subjects, objects, event_iri, ttl_list)
        # Lastly deal with other verbs
        if 'verb_processing' not in chunk_dict:
            event_state_mappings = get_event_state_mapping(lemma, verb, subjects, objects, event_iri, ttl_list)
        if not event_state_mappings:
            ttl_list.append(f'{chunk_iri} :describes {event_iri} .')
            handle_locations(ttl_list, loc_iri, loc_time_iris, event_iri, is_bio)  # May need to add location
            # Skip remainder of processing the xcomp root verb and for EnvAndCondition
            continue
        if len(event_state_mappings) > 1:
            # Logic to possibly select one mapping when there are alternatives
            event_state_mappings = _check_verb_person_mappings(event_state_mappings, objects)
        ttl_list.extend(create_type_turtle(event_state_mappings, event_iri, True, lemma))
        # May need to add origin to movement or a location overall for the event
        handle_locations(ttl_list, loc_iri, loc_time_iris, event_iri, is_bio)
        # Include the objects' ttl which was skipped above; It is referenced in the 'add_subj_obj_to_ttl' processing
        ttl_list.extend(obj_ttl)
        add_subj_obj_to_ttl(event_iri, subjects, objects, ttl_list)
        # Gather all the details that create a sentence label and deal with negation
        labels = [verb['verb_text'], get_xcomp_labels(chunk_dict, root_objects), get_prt_label(chunk_dict),
                  create_using_details(verb, event_iri, ttl_list),
                  verb['verb_aux'] if 'verb_aux' in verb else empty_string]
        if 'negation' in verb:
            ttl_list.append(f'{event_iri} :negation true .')
        label = create_verb_label(labels, subjects, objects, prepositions, True if 'negation' in verb else False)
        ttl_list.append(f'{event_iri} rdfs:label "{label.strip()}" .')
        ttl_list.append(f'{chunk_iri} :describes {event_iri} .')
        # TODO: Update last_events
        if xcomp_dict and lemma in xcomp_dict and xcomp_root_mappings:
            # Adjust the current array of Turtle statements taking the xcomp root verb into account
            return handle_xcomp_processing(root_text, xcomp_root_mappings, chunk_dict, alet_dict,
                                           last_nouns, last_events, ttl_list, event_iri, ext_sources)
    return ttl_list
