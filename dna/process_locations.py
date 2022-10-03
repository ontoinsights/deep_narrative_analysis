# Processing related to locations including adding geonames turtle details
# Called from create_narrative_turtle.py

from dna.create_noun_turtle import create_geonames_ttl, create_noun_ttl
from dna.utilities import empty_string, names_to_geo_dict, space


def check_if_loc_is_known(loc_text: str, alet_dict: dict) -> (list, str):
    """
    Determines if the location is already known/defined in either the geo-names country list or if
    it has been already processed.

    :param loc_text: Input location string
    :param alet_dict: A dictionary holding the agents, locations, events & times encountered in
             the full narrative - For co-reference resolution (it may be updated by this function);
             Keys = 'agents', 'locs', 'events', 'times' and Values (for 'locs') = array of arrays
             with index 0 holding an array of strings associated with the location, index 1
             storing the location's entity type, index 2 storing the class mappings, and index 3
             defining the location's IRI
    :return: A tuple holding an array of class mappings and a string specifying the location IRI,
             or a tuple of empty strings
    """
    if loc_text in names_to_geo_dict:     # Location is a country name\
        return [':Country'], f'geo:{names_to_geo_dict[loc_text]}'
    if 'locs' not in alet_dict:
        return [], empty_string
    known_locs = alet_dict['locs']
    for known_loc in known_locs:
        if loc_text in known_loc[0]:                    # Strings match
            return known_loc[2], known_loc[3]           # NER maps to a known/processed location, with an IRI
    return [], empty_string


def get_location_iri_and_ttl(loc_text: str, alet_dict: dict, from_ner: bool,
                             ext_sources: bool) -> (list, list, str, list):
    """
    Get a location IRI based on the input string and if appropriate, add the Turtle explaining/
    defining that location.

    :param loc_text: Input location string
    :param alet_dict: A dictionary holding the agents, locations, events & times encountered in
             the full narrative - For co-reference resolution (it may be updated by this function);
             Keys = 'agents', 'locs', 'events', 'times' and Values (for 'locs') = array of arrays
             with index 0 holding an array of strings associated with the location, index 1
             storing the location's entity type, index 2 storing the class mappings, and index 3
             defining the location's IRI
    :param from_ner: Boolean indicating whether the location has been identified by spaCy as
                     a named entity
    :param ext_sources: Boolean indicating whether additional information on the location should
                        be retrieved from GeoNames (recommended)
    :return: A tuple holding 1) an array of alternate names for the location, 2) an array with the
             location's class mappings, 3) a string with the loc's IRI and 4) a list of Turtle
             statements defining the location (if the location is not already 'known'/processed,
             the alet_dict is updated)
    """
    loc_ttl = []
    new_loc_arrays = []
    if loc_text.lower().startswith('the '):
        loc_text = loc_text.replace('the ', empty_string).replace('The ', empty_string)
    loc_maps, loc_iri = check_if_loc_is_known(loc_text, alet_dict)
    if loc_iri:
        return [], loc_maps, loc_iri, []   # Don't care about alt names and have no Turtle
    loc_iri = f':{loc_text.replace(space,"_")}'.replace('.', empty_string)
    if from_ner:
        # Know that this is identified as a LOC, GPE, ...; See if there is more info
        if ext_sources:
            geo_ttl, geonames_map, alt_names = create_geonames_ttl(loc_iri, loc_text)
            # Class map from geonames is a string
            loc_maps = [geonames_map]
            loc_ttl.extend(geo_ttl)
        else:
            alt_names = [loc_text.strip()]
            loc_maps = [':Location']
            loc_ttl.append(f'{loc_iri} a :Location ; rdfs:label "{loc_text}" .')  # TODO: Improve class mapping
        new_loc_arrays.append([alt_names, 'LOC', loc_maps, loc_iri])
    else:     # From chunk parse
        # Determine if the location includes a proper noun (begins with capital letter)
        split_locs = loc_text.split(space)
        proper_noun = empty_string
        for word in split_locs:      # Want to get locations such as 'Warsaw ghetto'
            if word.isupper():
                proper_noun += word + space
        if proper_noun:
            proper_noun = proper_noun.strip()
            proper_noun_map, proper_noun_iri = check_if_loc_is_known(proper_noun, alet_dict)
            if proper_noun_iri and proper_noun != loc_text:
                # Location has more text than just the proper noun - likely that it describes a part of a location
                loc_ttl.append(f'{proper_noun_iri} :has_component {loc_iri} .')
        loc_maps, loc_turtle = create_noun_ttl(loc_iri, loc_text, 'LOC', False, ext_sources)
        alt_names = [loc_text.strip()]
        loc_ttl.extend(loc_turtle)
        new_loc_arrays.append([alt_names, 'LOC', loc_maps, loc_iri])
    # Record location text in alet_dict so that the details are not added again
    if new_loc_arrays:
        known_locs = alet_dict['locs'] if 'locs' in alet_dict else []
        known_locs.extend(new_loc_arrays)
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
             with index 0 holding an array of strings associated with the location, index 1
             storing the location's entity type, index 2 storing the class mappings, and index 3
             defining the location's IRI
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
                new_locs.append(f'{orig_locs[offset]}, {orig_locs[offset + 1]}')
                offset += 2
            else:
                new_locs.append(orig_locs[offset])
                offset += 1
        new_locs.append(orig_locs[offset])
    else:
        new_locs.append(orig_locs[0])
    new_locs_dict = dict()
    for new_loc in new_locs:
        new_locs_dict[new_loc] = check_if_loc_is_known(new_loc, alet_dict)
    for new_loc, loc_details in new_locs_dict.items():
        loc_maps, loc_iri = loc_details
        if not loc_iri:
            # Need to define the Turtle for a new location
            alt_names, loc_maps, loc_iri, loc_turtle = get_location_iri_and_ttl(new_loc, alet_dict, True, use_sources)
            locs_turtle.extend(loc_turtle)
        last_nouns.append((new_loc, 'LOC', loc_maps, loc_iri))
        loc_iris.append(loc_iri)
    return loc_iris, locs_turtle
