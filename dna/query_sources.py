# Query for details from external sources
# Called from get_ontology_mapping.py

import logging
import os
import requests
from typing import Union
import xml.etree.ElementTree as etree
from nltk.corpus import wordnet as wn

from dna.nlp import get_head_word
from dna.queries import query_wikidata_alt_names, query_wikidata_time
from dna.utilities import empty_string, space

geonamesUser = os.environ.get('GEONAMES_ID')

geocodes_mapping = {'H': ':WaterFeature',
                    'L': ':DesignatedArea',
                    'R': ':TransportationFeature',
                    'S': ':PhysicalLocation',
                    'T': ':GeographicFeature',
                    'U': ':WaterFeature',
                    'V': ':GeographicFeature'}


def _get_wikidata_time(query: str, is_start: bool) -> str:
    """
    Send the query, query_wikidata_time, to WDQS asking for the start and end times of an
    event identified by text (in the mwapi search parameters).

    :param query: The query to be sent with the wikidata ID already in the string
    :param is_start: Boolean indicating that the start time is requested (if true); Otherwise,
                     the end time is requested
    :return: A string holding the start or end time if defined; Otherwise, an empty string
    """
    if is_start:
        query = query.replace('propTime', 'P580')
    else:
        query = query.replace('propTime', 'P582')
    response = requests.get(f'https://query.wikidata.org/sparql?format=json&query={query}').json()
    results = []
    if 'results' in response and 'bindings' in response['results']:
        results = response['results']['bindings']
    if len(results) > 0:
        return results[0]['time']['value']
    else:
        return empty_string


def _get_xml_value(xpath: str, root: etree.Element) -> str:
    """
    Use the input xpath string to access specific elements in an XML tree.

    :param xpath: String identifying the path to the element to be retrieved
    :param root: The root element of the XML tree
    :return: String representing the value of the specified element or an empty string
             (if not defined)
    """
    elems = root.findall(xpath)
    if elems:
        return elems[0].text
    else:
        return empty_string


def _get_geonames_response(request: str, loc_str: str) -> Union[etree.Element, None]:
    """
    Send and process a query to the GeoNames API.

    :param request: A string holding the query request.
    :param loc_str: A string holding the text identifying the location.
    :return: The GeoNames response
    """
    response = requests.get(request)
    root = etree.fromstring(response.content)
    toponym_name = _get_xml_value('./geoname/toponymName', root)
    if toponym_name.lower() == loc_str.lower():
        return root
    # Try again, forcing a match of fcode = ADM1 - for ex, New York returns New York City, not the state
    if 'fcode=' in request:
        return None
    request += '&fcode=ADM1'
    return _get_geonames_response(request, loc_str)


def check_wordnet(word: str) -> str:
    """
    Check the most common wordnet definition (the first one) for an unmapped term.

    :param word: The term to be mapped
    :return: String holding the head word from the definition of the first synset for the term, or
             an empty string
    """
    if space in word:
        single_word = get_head_word(word)[0]
    else:
        single_word = word
    synsets = wn.synsets(single_word, pos=wn.NOUN)
    if synsets:
        return get_head_word(synsets[0].definition())[0]
    else:
        return empty_string


def get_event_details_from_wikidata(event_text: str) -> (str, str, str, list):
    """
    Get the start and end times and alternate names of an event, if it is known to Wikidata.

    :param event_text: Text defining the event
    :return: A tuple consisting of strings holding the Wikipedia description of the event,
             strings identifying the start and end times and an array of alternate names
    """
    logging.info(f'Getting Wikidata event details for {event_text}')
    start_time = empty_string
    end_time = empty_string
    alt_names = []
    wiki_details = get_wikipedia_description(event_text.replace(space, '_'))
    if wiki_details:
        if 'See the web site' not in wiki_details:
            wikidata_id = wiki_details.split('wikibase_item: ')[1].split(')')[0]
            query_alt_names = query_wikidata_alt_names.replace('?item', f'wd:{wikidata_id}')
            response = requests.get(f'https://query.wikidata.org/sparql?format=json&query='
                                    f'{query_alt_names}').json()
            if 'results' in response and 'bindings' in response['results']:
                results = response['results']['bindings']
                for result in results:
                    alt_names.append(result['altLabel']['value'].replace('"', "'"))
            time_query = query_wikidata_time.replace('?item', f'wd:{wikidata_id}')
            start_time = _get_wikidata_time(time_query, True)
            end_time = _get_wikidata_time(time_query, False)
    return wiki_details, start_time, end_time, alt_names


def get_geonames_location(loc_text: str) -> (str, str, int, list):
    """
    Get the type of location from its text as well as its country and administrative level (if relevant).

    :param loc_text: Location text
    :return: A tuple holding the location's class mapping (for geonames, it is always a single string),
             country name (or an empty string or None), an administrative level (if 0, then admin level
             is not applicable) or GeoNames ID (for a Country), and a list of alternate names
             (or just [loc_text] is returned)
    """
    logging.info(f'Getting geonames details for {loc_text}')
    # Future: May need to add sleep to meet geonames timing requirements
    if ',' in loc_text:
        request = f'http://api.geonames.org/search?q={loc_text.lower().replace(space, "+")}' \
                  f'&style=full&maxRows=1&username={geonamesUser}'
    elif space in loc_text:
        request = f'http://api.geonames.org/search?q={loc_text.lower().replace(space, "+")}' \
                  f'&name_equals={loc_text.lower().replace(space, "+")}&style=full&maxRows=1&username={geonamesUser}'
    else:
        request = f'http://api.geonames.org/search?q={loc_text.lower()}&name_startsWith={loc_text.lower()}' \
                  f'&style=full&maxRows=1&username={geonamesUser}'
    root = _get_geonames_response(request, loc_text)
    if root is None:
        return empty_string, empty_string, 0, []
    country = _get_xml_value('./geoname/countryName', root)
    feature = _get_xml_value('./geoname/fcl', root)
    fcode = _get_xml_value('./geoname/fcode', root)
    ascii_name = _get_xml_value('./geoname/asciiName', root)
    alt_str = _get_xml_value('./geoname/alternateNames', root)
    if not country and not feature:
        return empty_string, empty_string, 0, []
    admin_level = 0
    class_type = ':PopulatedPlace'
    if feature == 'A':     # Administrative area
        if fcode.startswith('ADM'):
            class_type += '+:AdministrativeDivision'
            # Get administrative level
            if any([i for i in fcode if i.isdigit()]):
                admin_level = [int(i) for i in fcode if i.isdigit()][0]
        elif fcode.startswith('PCL'):  # Some kind of political entity, assuming for now that it is a country
            class_type = ":Country"
            country = empty_string
        elif fcode.startswith('L') or fcode.startswith('Z'):
            # Leased area usually for military installations or a zone, such as a demilitarized zone
            return empty_string, empty_string, admin_level
    elif feature == 'P' and fcode.startswith('PPLA'):  # PopulatedPlace that is an administrative division
        class_type += '+:AdministrativeDivision'
        # Get administrative level
        admin_levels = [int(i) for i in fcode if i.isdigit()]
        if admin_levels:
            admin_level = admin_levels[0]
        else:
            admin_level = 1
    elif feature in ('H', 'L', 'R', 'S', 'T', 'U', 'V'):
        class_type = geocodes_mapping[feature]
    # Process the alternate names
    alt_names = []
    anames = alt_str.split(',')
    for aname in anames:
        if aname.isascii():
            if "'" not in aname or "'s" in aname or "' " in aname:
                alt_names.append(aname)
    if ascii_name not in alt_names:
        alt_names.append(ascii_name)
    return class_type, country, admin_level, alt_names


def get_wikipedia_description(noun: str) -> str:
    """
    Get the first paragraph of the Wikipedia web page for the specified organization, group, ...

    :param noun: String holding the organization/group name
    :return: String that is the first paragraph of the Wikipedia page (if the org/group is found),
             information on a disambiguation page or an empty string
    """
    logging.info(f'Getting wikipedia details for {noun}')
    noun_underscore = noun.replace(space, '_')
    resp = requests.get(f'https://en.wikipedia.org/api/rest_v1/page/summary/{noun_underscore}')
    wikipedia = resp.json()
    if 'type' in wikipedia and wikipedia['type'] == 'disambiguation':
        return f'Needs disambiguation; See the web site, https://en.wikipedia.org/wiki/{noun_underscore}'
    if 'extract' in wikipedia:
        extract_text = wikipedia['extract'].replace('"', "'").replace('\xa0', space).replace('\n', space).\
            encode('ASCII', errors='replace').decode('utf-8')
        wiki_text = f"'{extract_text}'"
        return f'From Wikipedia (wikibase_item: {wikipedia["wikibase_item"]}): {wiki_text}'
    return empty_string
