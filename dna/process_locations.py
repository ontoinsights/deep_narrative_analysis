# Processing related to locations including adding geonames turtle details
# Called from create_narrative_turtle.py

import re

from dna.create_noun_turtle import create_geonames_ttl
from dna.get_ontology_mapping import get_agent_or_loc_class
from dna.utilities_and_language_specific import empty_string, names_to_geo_dict, underscore


def _check_if_loc_is_known(loc_text: str, loc_type: str, alet_dict: dict) -> (list, str):
    """
    Determines if the location is already known/defined in either the geo-names country list or if
    it has been already processed (and is therefore in the alet dictionary).

    :param loc_text: Input location string
    :param loc_type: String identifying NER type for the text, as defined by spaCy
    :param alet_dict: A dictionary holding the agents, locations, events & times encountered in
             the full narrative - For co-reference resolution (it may be updated by this function);
             Keys = 'agents', 'locs', 'events', 'times' and Values (for 'locs') = array of arrays
             with index 0 holding an array of strings/alt names associated with the location, index 1
             storing the class mappings, and index 2 defining the location's IRI
    :return: A tuple holding an array of class mappings and a string specifying the location IRI,
             or a tuple of the location class mappings and an empty string
    """
    if loc_text in names_to_geo_dict:     # Location is a country name
        return [':Country'], f'geo:{names_to_geo_dict[loc_text]}'
    class_map = get_agent_or_loc_class(loc_type)
    if 'locs' not in alet_dict:
        return [class_map], empty_string
    known_locs = alet_dict['locs']
    for known_loc in known_locs:
        if loc_text in known_loc[0]:                    # Strings match
            return known_loc[1], known_loc[2]           # NER maps to a known/processed location, with an IRI
    return [class_map], empty_string


def _get_location_iri_and_ttl(loc_text: str, loc_maps: list, alet_dict: dict,
                              ext_sources: bool) -> (list, list, str, list):
    """
    Get a location IRI based on the input string and if appropriate, add the Turtle explaining/
    defining that location.

    :param loc_text: Input location string
    :param loc_maps: Array holding the ontology mapping for the NER type from spaCy
    :param alet_dict: A dictionary holding the agents, locations, events & times encountered in
             the full narrative - For co-reference resolution (it may be updated by this function);
             Keys = 'agents', 'locs', 'events', 'times' and Values (for 'locs') = array of arrays
             with index 0 holding an array of strings/alt names associated with the location, index 1
             storing the class mappings, and index 2 defining the location's IRI
    :param ext_sources: Boolean indicating whether additional information on the location should
                        be retrieved from GeoNames (recommended)
    :return: A tuple holding 1) an array of alternate names for the location, 2) an array with the
             location's class mappings, 3) a string with the loc's IRI and 4) a list of Turtle
             statements defining the location (if the location is not already 'known'/processed,
             the alet_dict is updated)
    """
    loc_ttl = []
    loc_iri = re.sub(r'[^:a-zA-Z0-9_]', underscore, f':{loc_text}').replace('__', '_')
    # Know that this is identified as a LOC, GPE, ...; See if there is more info
    if ext_sources:
        geo_ttl, geonames_map, alt_names = create_geonames_ttl(loc_iri, loc_text)
        # Class map from geonames is a string
        loc_maps = [geonames_map]
        loc_ttl.extend(geo_ttl)
    else:
        alt_names = [loc_text.strip()]
        loc_ttl.append(f'{loc_iri} a {loc_maps[0]} ; rdfs:label "{loc_text}" .')    # Only have 1 mapping from NER
    # Record location text in alet_dict so that the details are not added again
    known_locs = alet_dict['locs'] if 'locs' in alet_dict else []
    known_locs.append([alt_names, loc_maps, loc_iri])
    alet_dict['locs'] = known_locs
    return alt_names, loc_maps, loc_iri, loc_ttl


def get_sentence_locations(sentence_dictionary: dict, alet_dict: dict, last_nouns: list,
                           use_sources: bool) -> (list, list):
    """
    Handle locations identified by spaCy's NER, stored in the sentence dictionary with the
    key, 'LOCS'. If there is only 1 location specified, it is returned as "the" location
    for the events of this sentence.

    :param sentence_dictionary: The sentence dictionary
    :param alet_dict: A dictionary holding the agents, locations, events & times encountered in
             the full narrative - For co-reference resolution (it may be updated by this function);
             Keys = 'agents', 'locs', 'events', 'times' and Values (for 'locs') = array of arrays
             with index 0 holding an array of strings/alt names associated with the location, index 1
             storing the class mappings, and index 2 defining the location's IRI
    :param last_nouns: An array of tuples = noun texts, type, class mapping and IRI
                       from the current paragraph
    :param use_sources: Boolean indicating whether additional information on the location should
                        be retrieved from GeoNames (recommended)
    :return: A tuple consisting of two arrays: (1) the IRIs of the locations identified in the sentence,
             and 2) Turtle statements defining them  (also the alet_dict may be updated)
    """
    locs_turtle = []
    orig_locs = sentence_dictionary['LOCS']
    # Handle location words occurring together - for ex, 'Paris, Texas' - which are returned as 2 separate entities
    new_locs = []
    loc_iris = []
    if len(orig_locs) > 1:
        sent_str = sentence_dictionary['text']
        offset = 0
        while offset < (len(orig_locs) - 1):
            if f'{orig_locs[offset]}, {orig_locs[offset + 1]}' in sent_str:
                new_locs.append(f'{orig_locs[offset].split("+")[0]}, {orig_locs[offset + 1].split("+")[0]}'
                                f'+{orig_locs[offset].split("+")[1]}')
                offset += 2
            else:
                new_locs.append(orig_locs[offset])
                offset += 1
        new_locs.append(orig_locs[offset])
    else:
        new_locs.append(orig_locs[0])
    new_locs_dict = dict()
    for new_loc in new_locs:
        loc_split = new_loc.split('+')
        new_locs_dict[loc_split[0]] = _check_if_loc_is_known(loc_split[0], loc_split[1], alet_dict)
    for new_loc, loc_details in new_locs_dict.items():
        loc_maps, loc_iri = loc_details
        if not loc_iri:
            # Need to define the Turtle for a new location - Have only the NER mapping for the loc_type from above
            alt_names, loc_maps, loc_iri, loc_turtle = \
                _get_location_iri_and_ttl(new_loc, loc_maps, alet_dict, use_sources)
            locs_turtle.extend(loc_turtle)
        last_nouns.append((new_loc, 'LOC', loc_maps, loc_iri))
        loc_iris.append(loc_iri)
    return loc_iris, locs_turtle
