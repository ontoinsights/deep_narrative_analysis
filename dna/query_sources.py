# Query for details from GeoNames, Wikidata and Wikipedia
# Called from get_ontology_mapping.py

import logging
import os
import re
import requests
from typing import Union
import xml.etree.ElementTree as etree

# Future: Modify code to 'replace' the language tag when the query is executed, vs at 'compile' time (as it is now)
from dna.query_openai import access_api, wikipedia_prompt
from dna.utilities_and_language_specific import concept_map, empty_string, language_tag, space, underscore

country_qualifier = 'United_States'   # TODO: Move to environment variable

geonamesUser = os.environ.get('GEONAMES_ID')

geocodes_mapping = {'H': ':WaterFeature',
                    'L': ':DesignatedArea',
                    'R': ':TransportationFeature',
                    'S': ':PhysicalLocation',
                    'T': ':GeographicFeature',
                    'U': ':WaterFeature',
                    'V': ':GeographicFeature'}

# Future
query_wikidata_instance_of = \
    'SELECT DISTINCT ?instanceOf WHERE {?item wd:P31 ?instanceOf}'

language_filter = f'FILTER(lang(?label) = "{language_tag[1:]}")'
query_wikidata_labels = \
    'SELECT DISTINCT ?label WHERE {{?item rdfs:label ?label . ' + language_filter + ' } UNION ' \
    '{?item skos:altLabel ?label . ' + language_filter + ' }}'

query_wikidata_time = 'SELECT DISTINCT ?time WHERE {?item wdt:timeProp ?time}'


def _call_wikipedia(noun_text: str) -> dict:
    """
    Queries the REST API of Wikipedia for information about a specific concept/noun.

    :param noun_text: String holding the noun/concept text
    :return: Dictionary holding the details returned from Wikipedia
    """
    try:
        resp = requests.get(f'https://en.wikipedia.org/api/rest_v1/page/summary/{noun_text}', timeout=10)
    except requests.exceptions.ConnectTimeout:
        logging.error(f'Wikipedia description timeout: Noun={noun_text}')
        return dict()
    except requests.exceptions.RequestException as e:
        logging.error(f'Wikipedia description query exception for noun: {noun_text}. Exception: {str(e)}')
        return dict()
    wiki_dict = resp.json()
    if 'title' in wiki_dict and 'not found' in wiki_dict['title'].lower():
        return dict()
    return wiki_dict


def _get_geonames_alt_names(root: etree.Element) -> (list, str):
    """
    Retrieve all alternativeName elements (there is almost always more than 1) having the specified language(s)
    in the XML tree. And, return the Wikipedia link for the entity, if available.

    :param root: The root element of the XML tree
    :return: A tuple consisting of an array holding the string values of the alternative names
             or an empty array (if not defined), and a string holding the Wikipedia link for
             additional details
    """
    names = set()
    link = empty_string
    elems = root.findall('./geoname/alternateName[@lang]')
    for elem in elems:
        lang = elem.get('lang')
        # access = True if ('isPreferredName' in elem.attrib or 'isShortName' in elem.attrib) else False
        if lang == 'en':
            names.add(elem.text)
        if lang == 'link' and 'en.wikipedia' in elem.text:
            link = elem.text
    return list(names), link


def _get_geonames_response(request: str, loc_str: str) -> Union[etree.Element, None]:
    """
    Send and process a query to the GeoNames API.

    :param request: A string holding the query request.
    :param loc_str: A string holding the text identifying the location.
    :return: The GeoNames response
    """
    try:
        response = requests.get(request, timeout=10)
    except requests.exceptions.ConnectTimeout:
        logging.error(f'GeoNames timeout: Query={request}')
        return None
    except requests.exceptions.RequestException as e:
        logging.error(f'GeoNames query error: Query={request} and Exception={str(e)}')
        return None
    orig_root = etree.fromstring(response.content)
    toponym_name = _get_xml_value('./geoname/toponymName', orig_root)
    ascii_name = _get_xml_value('./geoname/asciiName', orig_root)
    if toponym_name.lower() == loc_str.lower():
        return orig_root
    # Try again, forcing a match of fcode = ADM1 - for ex, New York returns New York City, not the state
    if 'fcode=' not in request:
        request += '&fcode=ADM1'
        root = _get_geonames_response(request, loc_str)
        if root:
            return root
    # Relax the match to the toponym or ascii name containing the location string
    if loc_str.lower() in toponym_name.lower() or loc_str.lower() in ascii_name.lower():
        return orig_root
    return None


def _get_wikidata_labels(wikidata_id: str) -> list:
    """
    Get the labels (labels and alt_names) for a Wikidata item.

    :param wikidata_id: String holding the Q ID of the Wikidata item
    :return: An array of strings that are the rdfs:label and skos:alt_names of the item
    """
    if not wikidata_id:
        return []
    labels = []
    query_labels = query_wikidata_labels.replace('?item', f'wd:{wikidata_id}')
    try:
        response = requests.get(
            f'https://query.wikidata.org/sparql?format=json&query={query_labels}', timeout=10).json()
    except requests.exceptions.ConnectTimeout:
        logging.error(f'Wikidata labels timeout: Query={query_labels}')
        return labels
    except requests.exceptions.RequestException as e:
        request = f'https://query.wikidata.org/sparql?format=json&query={query_labels}'
        logging.error(f'Wikidata labels query error: Query={request} and Exception={str(e)}')
        return labels
    if 'results' in response and 'bindings' in response['results']:
        results = response['results']['bindings']
        for result in results:
            label = result['label']['value'].replace('"', "'")
            labels.append(label)
    return labels


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
    try:
        response = requests.get(f'https://query.wikidata.org/sparql?format=json&query={query}', timeout=10).json()
    except requests.exceptions.ConnectTimeout:
        logging.error(f'Wikidata time timeout: Query={query}')
        return empty_string
    except requests.exceptions.RequestException as e:
        request = f'https://query.wikidata.org/sparql?format=json&query={query}'
        logging.error(f'Wikidata time query error: Query={request} and Exception={str(e)}')
        return empty_string
    results = []
    if 'results' in response and 'bindings' in response['results']:
        results = response['results']['bindings']
    if len(results) > 0:
        return results[0]['time']['value']
    else:
        return empty_string


def _get_wikipedia_description(noun_text: str, noun_class: str, explicit_link: str) -> dict:
    """
    Wikipedia call to get page summary information for a concept. If information is not retrieved
    due to the need to disambiguate or due to the return of non-relevant information, the request is
    retried with the addition of the country name.

    :param noun_text: String holding the concept text (with spaces replaced by underscores)
    :param noun_class: DNA class name corresponding to the concept
    :param explicit_link: A link to a Wikipedia article provided by another source
    :return: A dictionary with the Wikipedia information returned from the request
    """
    wiki_dict = dict()
    if explicit_link:       # Order of processing - explicit link, country-qualified noun text, unmodified noun text
        wiki_dict = _call_wikipedia(explicit_link.split('/')[-1])
    if not wiki_dict:
        noun_text = noun_text.replace(' ', underscore)
        wiki_dict = _call_wikipedia(f'{country_qualifier}_{noun_text}')
        if not wiki_dict:
            wiki_dict = _call_wikipedia(noun_text)
    # Check if the wikipedia text/extract matches the DNA class semantic
    if wiki_dict and 'extract' in wiki_dict and 'See the web site' not in wiki_dict['extract']:
        # Remove a second class name and the beginning ':' from noun_class and then split the upper camel case
        #    text into individual words
        concept = space.join(re.findall(r'[A-Z](?:[a-z]+|[A-Z]*(?=[A-Z]|$))', noun_class.split(',')[0][1:]))
        wikipedia_dict = access_api(
            wikipedia_prompt.replace("{text_type}", concept).replace("{wiki_def}", wiki_dict['extract']))
        if type(wikipedia_dict['consistent']) is bool and wikipedia_dict['consistent']:
            return wiki_dict    # Consistent - return the result
    return dict()


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


def get_event_details_from_wikidata(event_text: str) -> (str, str, str, str, list):
    """
    Get the start and end times and alternate names of an event, if it is known to Wikidata.

    :param event_text: Text defining the event
    :return: A tuple consisting of strings holding the Wikipedia description of the event, the
             URL of the web page from Wikipedia, the Wikidata identifier for the event,
             strings identifying the start and end times,
             and an array of labels/alternate names
    """
    logging.info(f'Getting Wikidata event details for {event_text}')
    start_time = empty_string
    end_time = empty_string
    wiki_details, wiki_url, wikidata_id, labels = get_wikipedia_description(event_text, ':Event')
    if wiki_details and 'See the web site' not in wiki_details:
        time_query = query_wikidata_time.replace('?item', f'wd:{wikidata_id}')
        start_time = _get_wikidata_time(time_query, True)
        end_time = _get_wikidata_time(time_query, False)
    return wiki_details, wiki_url, wikidata_id, start_time, end_time, labels


def get_geonames_location(loc_text: str) -> (str, str, int, list, str):
    """
    Get the type of location from its text as well as its country and administrative level (if relevant).

    :param loc_text: Location text
    :return: A tuple holding the location's class mapping (for geonames, it is always a single string),
             country name (or an empty string or None), an administrative level (if 0, then admin level
             is not applicable) or GeoNames ID (for a Country), a list of alternate names and a link
             to a Wikipedia page for the location
    """
    logging.info(f'Getting geonames details for {loc_text}')
    # Future: May need to add sleep to meet geonames timing requirements
    name_startswith = False
    if ',' in loc_text:   # Different query parameters are defined based on ',' or space in the location text
        request = f'http://api.geonames.org/search?q={loc_text.lower().replace(space, "+").replace(",", "+")}' \
                  f'&style=full&maxRows=1&username={geonamesUser}'
    elif space in loc_text:
        request = f'http://api.geonames.org/search?q={loc_text.lower().replace(space, "+")}' \
                  f'&name_equals={loc_text.lower().replace(space, "+")}&style=full&maxRows=1&username={geonamesUser}'
    else:
        name_startswith = True
        request = f'http://api.geonames.org/search?q={loc_text.lower()}&name_startsWith={loc_text.lower()}' \
                  f'&style=full&maxRows=1&username={geonamesUser}'
    root = _get_geonames_response(request, loc_text)
    if root is None:
        if name_startswith:
            # Try less restrictive search
            request = f'http://api.geonames.org/search?q={loc_text.lower()}' \
                      f'&style=full&maxRows=1&username={geonamesUser}'
            root = _get_geonames_response(request, loc_text)
    if root is None:
        return empty_string, empty_string, 0, [], empty_string
    country = _get_xml_value('./geoname/countryName', root)
    feature = _get_xml_value('./geoname/fcl', root)
    fcode = _get_xml_value('./geoname/fcode', root)
    ascii_name = _get_xml_value('./geoname/asciiName', root)
    alt_names, wiki_link = _get_geonames_alt_names(root)
    if not country and not feature:
        return empty_string, empty_string, 0, [], empty_string
    # Process the alternate names
    if loc_text not in alt_names:
        alt_names.append(loc_text)
    if ascii_name not in alt_names:
        alt_names.append(ascii_name)
    # Process the rest of the GeoNames info
    admin_level = 0
    class_type = ':PopulatedPlace'
    if feature == 'A':     # Administrative area
        if fcode.startswith('ADM'):
            class_type += ', :AdministrativeDivision'
            # Get administrative level
            if any([i for i in fcode if i.isdigit()]):
                admin_level = [int(i) for i in fcode if i.isdigit()][0]
        elif fcode.startswith('PCL'):  # Some kind of political entity, assuming for now that it is a country
            class_type = ":Country"
            country = empty_string
        elif fcode.startswith('L') or fcode.startswith('Z'):
            # Leased area usually for military installations or a zone, such as a demilitarized zone
            class_type = ':DesignatedArea'
    elif feature == 'P' and fcode.startswith('PPLA'):  # PopulatedPlace that is an administrative division
        class_type += ', :AdministrativeDivision'
        # Get administrative level
        admin_levels = [int(i) for i in fcode if i.isdigit()]
        if admin_levels:
            admin_level = admin_levels[0]
        else:
            admin_level = 1
    elif feature in ('H', 'L', 'R', 'S', 'T', 'U', 'V'):
        class_type = geocodes_mapping[feature]
    return class_type, country, admin_level, alt_names, wiki_link


def get_wikipedia_description(noun: str, noun_class: str, explicit_link: str = empty_string) -> (str, str, str, list):
    """
    Get the first paragraph of the Wikipedia web page for the specified organization, group, ...
    and a link to display the full page.

    :param noun: String holding the concept name
    :param noun_class: DNA class name corresponding to the concept
    :param explicit_link: A link retrieved from another source (such as GeoNames) to a Wikipedia
                          entry for the noun
    :return: A tuple holding three strings - (1) the first paragraph of the Wikipedia page
             (if found and not ambiguous), (2) a link to the full Wikipedia article,
             (3) the Wikibase/Wikidata identifier, or 3 empty strings; and (4) a list
             of text labels
    """
    logging.info(f'Getting wikipedia details for {noun}')
    wikipedia_dict = _get_wikipedia_description(noun.replace(space, '_'), noun_class, explicit_link)
    if not wikipedia_dict:
        return empty_string, empty_string, empty_string, []
    if 'type' in wikipedia_dict and wikipedia_dict['type'] == 'disambiguation':
        return f'Needs disambiguation; See the web site, https://en.wikipedia.org/wiki/{noun.replace(space, "_")}', \
            empty_string, empty_string, []
    desktop_url = empty_string if 'content_urls' not in wikipedia_dict else \
        wikipedia_dict['content_urls']['desktop']['page']
    wikidata_id = empty_string if 'wikibase_item' not in wikipedia_dict else wikipedia_dict['wikibase_item']
    extract = empty_string
    if 'extract' in wikipedia_dict:
        extract_text = wikipedia_dict['extract'].replace('"', "'").replace('\xa0', space).replace('\n', space).\
            encode('ASCII', errors='replace').decode('utf-8')
        wiki_text = f"'{extract_text}'"
        extract = f'From Wikipedia (wikibase_item: {wikidata_id}): {wiki_text}'
    return extract, desktop_url, wikidata_id, _get_wikidata_labels(wikidata_id)
