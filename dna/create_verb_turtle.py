# Functions to clean up the Turtle (before storage in Stardog)
# Called by create_narrative_turtle.py

import uuid

from dna.coreference_resolution import check_nouns
from dna.create_specific_turtle import create_type_turtle
from dna.query_ontology import check_subclass
from dna.utilities_and_language_specific import add_unique_to_array, dna_prefix, empty_string, objects_string, \
    prep_to_predicate_for_locs

has_location = ':has_location'


def add_subj_obj_to_ttl(event_iri: str, subjs: list, objs: list, ttl_list: list):
    """
    Given the details related to the subjects/objects of a sentence, capture the
    corresponding Turtle that relates the concepts to a chunk's verb (identified by
    the event_iri).

    :param event_iri: An IRI identifying the verb event
    :param subjs: Array of tuples that are the subject nouns' text, type, mappings and IRI
    :param objs: Array of tuples that are the object nouns' text, type, mappings and IRI
    :param ttl_list: An array of Turtle statements capturing the semantics of the chunk
    :return: None (ttl_list is updated)
    """
    ttl_str = str(ttl_list)
    for subj_text, subj_type, subj_mappings, subj_iri in subjs:
        if ':Affiliation' in ttl_str:
            ttl_list.append(f'{event_iri} :affiliated_agent {subj_iri} .')
        else:
            ttl_list.append(f'{event_iri} :has_active_agent {subj_iri} .')
    for obj_text, obj_type, obj_mappings, obj_iri in objs:
        is_agent = False
        if 'PERSON' in obj_type or obj_type.endswith('GPE') or obj_type.endswith('ORG') \
                or obj_type.endswith('NORP'):
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
            if ':Affiliation' in ttl_str:
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
    # TODO: Get full prepositional text ('with aid of the local police chief')
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
    # TODO: Relationships for an Agent are different from associations for other "things"; Is more needed?
    new_loc_iri = empty_string
    if 'PERSON' in prep_obj_type or 'Agent' in prep_obj_classes or 'ORG' in prep_obj_type:
        if prep_text == 'from':
            prep_turtle.append(f'{event_iri} :has_provider {prep_obj_iri} .')
        elif prep_text == 'to':
            prep_turtle.append(f'{event_iri} :has_recipient {prep_obj_iri} .')
        elif prep_text in ('for', 'about'):
            prep_turtle.append(f'{event_iri} :has_affected_agent {prep_obj_iri} .')
        elif prep_text == 'with':
            prep_turtle.append(f'{event_iri} :has_active_agent {prep_obj_iri} .')
    else:
        if prep_text == 'with':
            prep_turtle.append(f'{event_iri} :has_instrument {prep_obj_iri} .')
        elif prep_text in prep_to_predicate_for_locs and \
                (prep_obj_type.endswith('LOC') or prep_obj_type.endswith('GPE') or prep_obj_type.endswith('FAC')):
            if prep_text in ('at', 'in', 'near', 'outside', 'to'):
                new_loc_iri = prep_obj_iri
            prep_turtle.append(f'{event_iri} {prep_to_predicate_for_locs[prep_text]} {prep_obj_iri} .')
        elif prep_text in ('about', 'from', 'in', 'of', 'to'):
            prep_turtle.append(f'{event_iri} :has_topic {prep_obj_iri} .')
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
    if is_bio and 'has_location' not in ttl_str and 'has_destination' not in ttl_str:
        # No location - so add one
        if loc_iri:
            turtle.append(f'{event_iri} :has_location {loc_iri} .')
        else:
            turtle.append(f'{event_iri} :has_location {loc_time_iris[0]} .')
    return


def handle_xcomp_processing(root_text: str, root_map: list, chunk_dict: dict, alet_dict: dict,
                            last_nouns: list, last_events: list, turtle: list, event_iri: str,
                            ext_sources: bool) -> list:
    """
    Handles xcomp processing for a sentence, which requires adjusting the subject/object,
    and more.

    :param root_text: The text of the root verb
    :param root_map: An array holding the mapping of the root verb to the DNA ontology
    :param chunk_dict: A dictionary holding details about the chunk
    :param alet_dict: A dictionary holding the agents, locations, events & times encountered in
             the narrative to-date - For co-reference resolution (it may be updated by this function);
             Keys = 'agents', 'locs', 'events', 'times' and Values that vary for the different keys
    :param last_nouns: An array of noun texts, type, class mapping and IRI from the current paragraph
    :param last_events: A list/array of tuples defining an event DNA class mapping and IRI, found in the
                        current paragraph
    :param turtle: The current Turtle definition for the sentence (which may be updated)
    :param event_iri: The xcomp event's IRI
    :param ext_sources: A boolean indicating that data from GeoNames, Wikidata, etc. should be
                        added to the parse results if available
    :return: An array of Turtle statements intended to replace the existing verb Turtle
    """
    # If root verb has a DNA mapping of Attempt or Continuation, End, ..., then can do simple multiple inheritance
    if root_map[0] in (':Attempt', ':Continuation', ':StartAndBeginning', ':End', ':Success', ':Failure'):
        turtle.append(f'{event_iri} a {root_map[0]} .')
        return turtle
    # Otherwise, create new event IRI for the scoping event/root verb (e.g., "permitted to leave")
    new_iri = f':Event_{str(uuid.uuid4())[:13]}'
    # And create the Turtle
    new_ttl = create_type_turtle(root_map, new_iri, True, root_text)
    new_ttl.append(f'{new_iri} :has_topic {event_iri} .')
    root_objects = []    # Account for the objects of the root verb
    for verb in chunk_dict['verbs']:
        if verb['verb_lemma'] == root_text and objects_string in verb:
            add_unique_to_array(check_nouns(verb, objects_string, alet_dict, last_nouns,
                                            last_events, new_ttl, ext_sources), root_objects)
            # TODO: Also process prepositions for the root verb (this is only processing the xcomp verb)
            add_subj_obj_to_ttl(new_iri, [], root_objects, new_ttl)
    # Use the existing the Turtle to add the details for the new scoping event and to correct the xcomp event
    turtle_text = str(turtle)
    has_affected = True if ':has_affected_agent' in turtle_text else False
    for turtle_stmt in turtle:
        # Deal with subjects, objects:
        # - If 'affected_agent', the root verb is passive and its subj becomes the 'active_agent' of the xcomp verb
        # - If the root verb has its own objects, these become the 'active_agent's of the xcomp verb
        # - If there is no 'affected_agent' and no root objects, the subject of the xcomp and root verbs are the same
        if ':describes' in turtle_stmt:    # Chunk also describes the root verb/event
            new_ttl.append(turtle_stmt)
            new_ttl.append(f'{turtle_stmt.split(" :describes")[0]} :describes {new_iri} .')
        elif ':has_affected_agent' in turtle_stmt:
            new_ttl.append(f'{new_iri} :has_{turtle_stmt.split("has_")[1]}')
            new_ttl.append(turtle_stmt.replace('affected_agent', 'active_agent'))
        elif ':has_active_agent' in turtle_stmt:
            new_ttl.append(f'{new_iri} :has_{turtle_stmt.split(":has_")[1]}')
            if root_objects:
                # Add root objects as subjects for the xcomp verb/event
                for root_text, root_type, root_mappings, root_iri in root_objects:
                    new_ttl.append(f'{event_iri} :has_active_agent {root_iri} .')
            else:
                new_ttl.append(turtle_stmt)
        elif ':has_agent' in turtle_stmt:
            new_ttl.append(turtle_stmt)
            new_ttl.append(f'{new_iri} :has_{turtle_stmt.split(":has_")[1]}')
        # Deal with time - the root and xcomp verbs may have same time or the root verb precedes the xcomp
        #    For ex, "she loved to play" (same relative time) vs. "she was permitted to leave"
        #    (permitted before leaving, leaving may not happen)
        elif ':has_latest_end' in turtle_stmt:
            time_iri = turtle_stmt.split(':has_latest_end ')[1].split(' .')[0]
            new_ttl.append(f'{new_iri} :has_latest_end {time_iri} .')
            new_ttl.append(turtle_stmt if not has_affected else new_ttl.append(f'{event_iri} :has_time {time_iri} .'))
        elif ':has_earliest_beginning' in turtle_stmt:
            new_ttl.append(turtle_stmt)
            new_ttl.append(f'{new_iri} :has_{turtle_stmt.split(":has_")[1]}')
        elif ':has_time ' in turtle_stmt:
            new_ttl.append(turtle_stmt)
            new_ttl.append(f'{new_iri} :has_{turtle_stmt.split(":has_")[1]}')
        # Deal with location
        elif has_location in turtle_stmt:
            new_ttl.append(turtle_stmt)
            new_ttl.append(f'{new_iri} :has_{turtle_stmt.split(":has_")[1]}')
        elif ':has_origin ' in turtle_stmt:
            new_ttl.append(turtle_stmt)
            new_ttl.append(f'{new_iri} {has_location} {turtle_stmt.split(":has_origin")[1]}')
        # Deal with label and a few more properties for the scoping event
        elif ':text ' in turtle_stmt:
            new_ttl.append(turtle_stmt)
            new_ttl.append(f'{new_iri} :text {turtle_stmt.split(":text ")[1]}')
        elif 'rdfs:label ' in turtle_stmt and turtle_stmt.startswith(':Event'):
            new_ttl.append(turtle_stmt)
            new_ttl.append(f'{new_iri} rdfs:label {turtle_stmt.split("rdfs:label ")[1]}')
        elif ':sentiment ' in turtle_stmt:
            new_ttl.append(f'{new_iri} :sentiment {turtle_stmt.split(":sentiment ")[1]}')
        else:
            new_ttl.append(turtle_stmt)     # For everything else, there is no change to the Turtle
    # The xcomp event may not occur (e.g., 'she was asked to leave' - but she might not leave)
    new_ttl.append(f'{event_iri} a :OpportunityAndPossibility .')
    return new_ttl
