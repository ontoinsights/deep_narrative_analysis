# Functions to clean up the Turtle (before storage in Stardog)
# Called by create_narrative_turtle.py

import uuid

from dna.coreference_resolution import check_nouns
from dna.query_ontology import check_subclass
from dna.utilities_and_language_specific import add_unique_to_array, dna_prefix, empty_string, objects_string, \
    prep_to_predicate, prep_to_predicate_mod

has_location = ':has_location'


def _process_prep_predicate(prep_text: str, event_iri: str, prep_obj_iri: str, is_agent: bool,
                            is_loc: bool, is_time: bool, prep_turtle: list) -> str:
    """
    Using the details in the prep_to_predicate dictionary, create a tuple for the verb/event/state
    where the preposition defines the predicate and the object is referenced as its subject or object.

    :param prep_text: String holding the preposition
    :param event_iri: The IRI for the verb/event
    :param prep_obj_iri: The IRI for the prepositional object
    :param is_agent: Boolean indicating whether the prepositional object is a type of :Agent
    :param is_loc: Boolean indicating whether the prepositional object is a type of :Location
    :param is_time: Boolean indicating whether the prepositional object is a type of :Time
    :param prep_turtle: The current Turtle for the verb/event/state
    :return: The mapping of the preposition to a DNA property
    """
    if prep_text not in prep_to_predicate:
        return empty_string
    prep_mapping = prep_to_predicate[prep_text]
    if '|' not in prep_mapping:     # A single mapping for the preposition
        if prep_mapping.startswith('obj+'):     # Object and event roles as subj/obj are reversed
            predicate = prep_mapping.replace('obj+', empty_string)
            prep_turtle.append(f'{prep_obj_iri} {predicate} {event_iri} .')
            return predicate
        else:
            prep_turtle.append(f'{event_iri} {prep_mapping} {prep_obj_iri} .')
            return prep_mapping
    prep_clauses = prep_mapping.split('|')    # Break into alternatives
    prep_default = empty_string
    for prep_clause in prep_clauses:
        if '=>' not in prep_clause:
            prep_default = prep_clause    # Save the default if no other alternatives match
        else:
            predicate = empty_string
            if ':Agent' in prep_clause and is_agent:
                predicate = prep_clause.replace('=>:Agent', empty_string)
            elif ':Location' in prep_clause and is_loc:
                predicate = prep_clause.replace('=>:Location', empty_string)
            elif ':Time' in prep_clause and is_time:
                predicate = prep_clause.replace('=>:Time', empty_string)
            if predicate:
                prep_turtle.append(f'{event_iri} {predicate} {prep_obj_iri} .')
                return predicate
    if prep_default:                     # No alternatives match, so use default
        prep_turtle.append(f'{event_iri} {prep_default} {prep_obj_iri} .')
        return prep_default
    return empty_string


def add_subj_obj_to_ttl(event_iri: str, subjs: list, objs: list, xcomp_root_processing: bool, ttl_list: list):
    """
    Given the details related to the subjects/objects of a sentence, capture the
    corresponding Turtle that relates the concepts to a chunk's verb (identified by
    the event_iri).

    :param event_iri: An IRI identifying the verb event
    :param subjs: Array of tuples that are the subject nouns' text, type, mappings and IRI
    :param objs: Array of tuples that are the object nouns' text, type, mappings and IRI
    :param xcomp_root_processing: Boolean (if true) indicating that this invocation is related to processing
                 the root verb of a root-xcomp pair
    :param ttl_list: An array of Turtle statements capturing the semantics of the chunk
    :return: None (ttl_list is updated)
    """
    ttl_str = str(ttl_list)
    for subj_text, subj_type, subj_mappings, subj_iri in subjs:
        if ':Affiliation' in ttl_str and ':affiliated_agent' not in ttl_str:
            ttl_list.append(f'{event_iri} :affiliated_agent {subj_iri} .')
        else:
            ttl_list.append(f'{event_iri} :has_active_agent {subj_iri} .')
    for obj_text, obj_type, obj_mappings, obj_iri in objs:
        if not xcomp_root_processing and f' {obj_iri}' in ttl_str:   # Check that the obj is not already in the ttl
            continue
        is_agent = False
        if 'PERSON' in obj_type or obj_type.endswith('GPE') or obj_type.endswith('ORG') \
                or obj_type.endswith('NORP') or any(['Person' in obj_map for obj_map in obj_mappings]):
            is_agent = True
        if not is_agent:     # May not have a type, so have to check the class mappings
            for obj_map in obj_mappings:
                if ',' not in obj_map and ('Agent' in obj_map or
                                           check_subclass(f'{dna_prefix}{obj_map[1:]}', 'Agent')):
                    is_agent = True
                    break
                # Deal with a comma separated list of classes (multiple inheritance)
                indiv_classes = obj_map.split(', ')
                for indiv_class in indiv_classes:
                    if check_subclass(f'{dna_prefix}{indiv_class[1:]}', 'Agent'):
                        is_agent = True
                        break
                if is_agent:
                    break
        if is_agent:
            if ':Affiliation' in ttl_str and ':affiliated_with' not in ttl_str:
                ttl_list.append(f'{event_iri} :affiliated_with {obj_iri} .')
            else:
                ttl_list.append(f'{event_iri} :has_affected_agent {obj_iri} .')
        else:
            ttl_list.append(f'{event_iri} :has_topic {obj_iri} .')
    return


def create_ttl_for_prep_detail(prep_detail: tuple, prepositions: list, event_iri: str, alet_dict: dict,
                               last_nouns: list, last_events: list, objects: list, ext_sources: bool) -> (list, str):
    """
    Parse the details for a verb's prepositions and create the corresponding Turtle. Note that
    dates/times are not handled in this code, but for the sentence overall.

    :param prep_detail: The text of the object of a preposition
    :param prepositions: An array of tuples holding the preposition text, object text, object type,
                         object class mappings, and object IRI
    :param event_iri: The IRI for the verb/event
    :param alet_dict: A dictionary holding the agents, locations, events & times encountered in
             the narrative to-date - For co-reference resolution (it may be updated by this function);
             Keys = 'agents', 'locs', 'events', 'times' and Values that vary for the different keys
    :param last_nouns: An array of noun texts, type, class mapping and IRI from the current paragraph
    :param last_events: A list of all event types and their IRIs from the current paragraph
    :param objects: An array of the direct objects of the chunk, to which the prepositional objects
                    are added; The array is a list of tuples holding an array of tuples of the
                    noun's texts, types, mappings and IRIs
    :param ext_sources: Boolean indicating whether additional information on a noun should
                        be retrieved from Wikidata (recommended)
    :return: An array holding the Turtle statements describing the preposition object (and the
             prepositions array is updated); Also if the prepositional object is location-related,
             and the preposition indicates that a new location is discussed, that location's IRI is
             returned (also, the objects array is updated)
    """
    prep_turtle = []
    prep_text, prep_obj_text, prep_obj_type = prep_detail
    prep_mapping = check_nouns(
        {'objects': [{'object_text': prep_obj_text, 'object_type': prep_obj_type}]}, 'objects',
        alet_dict, last_nouns, last_events, prep_turtle, ext_sources)
    # Should only be 1 tuple in prep_details array where 2nd value is the updated obj type, 3rd value is
    #    an array of class mappings and the 4th value is the IRI
    prep_obj_type = prep_mapping[0][1]
    prep_obj_classes = prep_mapping[0][2]
    prep_obj_iri = prep_mapping[0][3]
    objects.append((prep_obj_text, prep_obj_type, prep_obj_classes, prep_obj_iri))
    prepositions.append((prep_text, prep_obj_text, prep_obj_type, prep_obj_classes, prep_obj_iri))
    new_loc_iri = empty_string
    is_agent = True if 'PERSON' in prep_obj_type or 'Agent' in prep_obj_classes or 'ORG' in prep_obj_type else False
    is_loc = True if prep_obj_type.endswith('LOC') or prep_obj_type.endswith('GPE') or prep_obj_type.endswith('FAC') \
        else False
    is_time = False    # TODO: is_time
    prep_predicate = _process_prep_predicate(prep_text, event_iri, prep_obj_iri, is_agent, is_loc,
                                             is_time, prep_turtle)
    if is_loc and (prep_predicate == ':has_location' or prep_predicate == ':has_destination'):
        new_loc_iri = prep_obj_iri
    return prep_turtle, new_loc_iri


def handle_locations(turtle: list, loc_iri: str, loc_time_iris: list, event_iri: str, is_bio: bool):
    """
    Add an origin location for a Movement event (if possible and one is not already defined) and
    determine if an Event/State should have a location.

    :param turtle: The current Turtle definition for the sentence
    :param loc_iri: A string holding a new location for the current event
    :param loc_time_iris: An array holding the last processed location (index 0) and time (index 1)
    :param event_iri: A string holding the IRI identifier for the sentence's verb/event
    :param is_bio: A boolean indicating that the text is biographical/autobiographical, and so
                   may consistently define/use location references
    :return: N/A (the turtle and loc_time_iris arrays may be updated)
    """
    ttl_str = str(turtle)
    # Get the origin for a MovementTravelAndTransportation event
    # Origin is the location defined by the preposition 'from' OR the last location from processed_locs
    if ':Movement' in ttl_str and 'has_origin' not in ttl_str:
        if loc_time_iris[0]:
            turtle.append(f'{event_iri} :has_origin {loc_time_iris[0]} .')
    loc_time_iris[0] = loc_iri if loc_iri else loc_time_iris[0]     # Reset with the 'new' last known loc if available
    if is_bio and has_location not in ttl_str and 'has_destination' not in ttl_str:
        # No location - so add one
        if loc_iri:
            turtle.append(f'{event_iri} {has_location} {loc_iri} .')
        else:
            turtle.append(f'{event_iri} {has_location} {loc_time_iris[0]} .')
    return


def handle_xcomp_processing(xcomp_iri: str, root_iri: str, xcomp_dict: dict, xcomp_incorporates_root: bool,
                            turtle: list) -> list:
    """
    Cleans up the Turtle for a chunk with a root-xcomp pair.

    :param xcomp_iri: String holding the IRI of the xcomp verb
    :param root_iri: String holding the IRI of the root verb
    :param xcomp_dict: A dictionary with keys = root verb and the xcomp verb and values = 'root' for
                       the root verb or the verb_processing string for the xcomp
    :param xcomp_incorporates_root: A boolean indicating that the semantics of the root verb were collapsed
                                    into the xcomp verb (via multiple inheritance)
    :param turtle: An array of the current Turtle statements for a chunk
    :return: An array of updated Turtle statements
    """
    new_ttl = []
    if xcomp_incorporates_root:
        # Only need to fix the label to incorporate the root verb
        for turtle_stmt in turtle:
            if 'rdfs:label' in turtle_stmt:
                updated = False
                label = turtle_stmt.split('rdfs:label "')[1].split('" .')[0]
                for verb, processing in xcomp_dict.items():
                    if 'xcomp >' in processing and verb in label:
                        root_text = processing.split('/')[1].split(',')[0]
                        if f' {verb} ' not in label:
                            label = label.replace(verb, f'{root_text} to {verb} / {verb}')   # TODO: Non-English, 'to'
                        else:
                            label = label.replace(verb, f'{root_text} to {verb}')
                        new_ttl.append(f'{xcomp_iri} rdfs:label "{label}" .')
                        updated = True
                        break
                if not updated:
                    new_ttl.append(turtle_stmt)
            else:
                new_ttl.append(turtle_stmt)
        return new_ttl
    new_ttl = [f'{root_iri} :has_topic {xcomp_iri} .']
    # Correct the time and location in the existing Turtle - Details apply to the root verb and not the xcomp
    for turtle_stmt in turtle:
        if ':has_latest_end' in turtle_stmt or ':has_earliest_beginning' in turtle_stmt or ':has_time' in turtle_stmt:
            new_ttl.append(f'{root_iri} :has_{turtle_stmt.split(":has_")[1]}')
        elif has_location in turtle_stmt:
            new_ttl.append(f'{root_iri} :has_{turtle_stmt.split(":has_")[1]}')
        else:
            new_ttl.append(turtle_stmt)
    # Also, the xcomp event may not occur (e.g., 'she was asked to leave' - but she might not leave)
    new_ttl.append(f'{xcomp_iri} a :OpportunityAndPossibility .')
    return new_ttl


def revise_prep_turtle(ttl_list: list, indiv_mappings: list, prepositions: list, indiv_iri: str, dict_changes: dict):
    """
    Uses the dictionary, prep_to_predicate_mod (in the utilities and language_specific module),
    to adjust a prepositional predicate if the event/state class mapping meets the criteria specified
    in the dictionary.

    The dictionary format uses the prepositional text as the key, and the value is defined as a string
    using the syntax, event_state_class=>original_predicate>new_predicate.

    :param ttl_list: An array of the current Turtle for the chunk/event/state
    :param indiv_mappings: A list of possible types for the event/state
    :param prepositions: An array of tuples holding the preposition text, object text, object type,
                         object class mappings, and object IRI
    :param indiv_iri: A string/IRI identifying the event/state
    :param dict_changes: A dictionary where the key is the subject and original predicate and the value is
                         the revised subject and new predicate - indicating how the ttl_list should be
                         updated
    :return: N/A (dict_changes may be updated)
    """
    for preposition, rev_mapping in prep_to_predicate_mod.items():
        trigger_class = rev_mapping.split('=>')[0]
        orig_predicate = rev_mapping.split('=>')[1].split('>')[0]
        new_predicate = rev_mapping.split('=>')[1].split('>')[1]
        if not any([trigger_class == indiv_map for indiv_map in indiv_mappings]):
            continue
        if not any([prep_tuple[0] == preposition for prep_tuple in prepositions]):
            continue
        if f'{indiv_iri} {orig_predicate} ' not in str(ttl_list):
            continue
        # All the criteria of the prep_to_predicate_mod dictionary are met
        dict_changes[f'{indiv_iri} {orig_predicate} '] = f'{indiv_iri} {new_predicate} '
    return
