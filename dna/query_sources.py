# Query for details from GeoNames, Wikidata and Wikipedia
# Called from get_ontology_mapping.py

import datetime
import logging
import os
import re
import time
from dataclasses import dataclass

import requests
from typing import Union
import xml.etree.ElementTree as etree

# TODO: (Future) Modify code to 'replace' the language tag when the query is executed, vs hardcoding
from dna.query_openai import access_api, wikipedia_prompt
from dna.utilities_and_language_specific import empty_string, language_tag, space, underscore

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

@dataclass
class DescriptionDetails:
    """
    Dataclass holding the results of the get_wikipedia_description function
    """
    wiki_desc: str        # String holding the Wikipedia description of the entity
    wiki_url: str         # String holding the URL of the web page from Wikipedia
    wikidata_id: str      # String holding the Wikidata identifier
    labels: list          # Array of labels/alternate names for the entity
    # TODO: Add gender

@dataclass
class EventDetails:
    """
    Dataclass holding the results of the get_event_details_from_wikidata function
    """
    wiki_desc: str        # String holding the Wikipedia description of the event
    wiki_url: str         # String holding the URL of the web page from Wikipedia
    wikidata_id: str      # String holding the Wikidata identifier
    start_time: str       # String identifying the start time of the event or the empty string
    end_time: str         # String identifying the end time of the event or the empty string
    labels: list          # Array of labels/alternate names for the event

@dataclass
class GeoNamesDetails:
    """
    Dataclass holding the results of the get_geonames_location function
    """
    location_class: str     # Location's DNA class mapping
    country: str            # Country name or empty string
    admin_level: int        # Administrative level (or 0 if the admin level is not applicable)
    alt_names: list         # Array of alternative names
    wiki_link: str          # Wikipedia page link or empty string


def _call_wikipedia(noun_text: str) -> dict:
    """
    Queries the REST API of Wikipedia for information about a specific concept/noun.

    :param noun_text: String holding the noun/concept text
    :return: Dictionary holding the details returned from Wikipedia
    """
    try:
        resp = requests.get(f'https://en.wikipedia.org/api/rest_v1/page/summary/{noun_text}')
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


def _get_wikidata_delay(date: str) -> int:
    """
    If too many Wikidata requests are made, then a 'retry after' time limit is set. This method
    calculates the time limit.

    :param date: A string with the 'retry after' time
    :return: An integer indicating how many seconds to delay
    """
    try:
        datetime_obj = datetime.datetime.strptime(date, '%a, %d %b %Y %H:%M:%S GMT')
        timeout = int((datetime_obj - datetime.datetime.now()).total_seconds())
    except ValueError:
        timeout = int(date)
    return timeout


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
        response = requests.get(request)
    except requests.exceptions.ConnectTimeout:
        logging.error(f'GeoNames timeout: Query={request}')
        return None
    except requests.exceptions.RequestException as e:
        logging.error(f'GeoNames query error: Query={request} and Exception={str(e)}')
        return None
    orig_root = etree.fromstring(response.content)
    toponym_name = _get_xml_value('./geoname/toponymName', orig_root)
    ascii_name = _get_xml_value('./geoname/asciiName', orig_root)
    if toponym_name.lower() == loc_str.lower() or loc_str.lower().startswith(toponym_name.lower()):
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


def _get_wikidata_labels(wikidata_id: str, retry: bool = True) -> list:
    """
    Get the labels (labels and alt_names) for a Wikidata item.

    :param wikidata_id: String holding the Q ID of the Wikidata item
    :param retry: Boolean indicating that the request be retried on an exception
    :return: An array of strings that are the rdfs:label and skos:alt_names of the item
    """
    if not wikidata_id:
        return []
    labels = []
    query_labels = query_wikidata_labels.replace('?item', f'wd:{wikidata_id}').replace(' ', '%20')
    resp_json = _make_wikidata_query(f'https://query.wikidata.org/sparql?format=json&query={query_labels}')
    if resp_json and 'results' in resp_json and 'bindings' in resp_json['results']:
        for result in resp_json['results']['bindings']:
            label = result['label']['value'].replace('"', "'")
            labels.append(label)
    return labels


def _get_wikidata_time(query: str, is_start: bool, retry: bool = True) -> str:
    """
    Send the query, query_wikidata_time, to WDQS asking for the start and end times of an
    event identified by text (in the mwapi search parameters).

    :param query: The query to be sent with the wikidata ID already in the string
    :param is_start: Boolean indicating that the start time is requested (if true); Otherwise,
                     the end time is requested
    :param retry: Boolean indicating that the request be retried on an exception
    :return: A string holding the start or end time if defined; Otherwise, an empty string
    """
    time_query = (query.replace('timeProp', 'P580').replace(' ', '%20') if is_start
                  else query.replace('timeProp', 'P582').replace(' ', '%20'))
    resp_json = _make_wikidata_query(f'https://query.wikidata.org/sparql?format=json&query={time_query}')
    if resp_json and 'results' in resp_json and 'bindings' in resp_json['results'] and \
                len(resp_json['results']['bindings']) > 0:
            return resp_json['results']['bindings'][0]['time']['value']
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


def _make_wikidata_query(query: str, retry: bool = True) -> Union[dict, None]:
    """
    Processes a query to the Wikidata query service.

    :param query: String holding the query.
    :param retry: Boolean indicating that the request be retried on an exception or 'too many requests' error
    :return: Either the query results or None if the request was not successful
    """
    try:
        resp = requests.get(query)
    except requests.exceptions.ConnectTimeout:
        logging.error(f'Wikidata timeout: Query={query}')
        return None
    except requests.exceptions.RequestException as e:
        if retry:
            return _make_wikidata_query(query, retry=False)
        else:
            return None
    if resp.status_code == 200:
        if resp.json()['results']['bindings']:
            return resp.json()
        else:
            return None
    if resp.status_code == 429:     # Too many requests
        timeout = _get_wikidata_delay(resp.headers['retry-after'])
        logging.info(f'Wikidata timeout: {timeout} seconds')
        time.sleep(timeout)
        return _make_wikidata_query(query)
    return None


def get_event_details_from_wikidata(event_text: str) -> EventDetails:
    """
    Get the start and end times and alternate names of an event, if it is known to Wikidata.

    :param event_text: Text defining the event
    :return: An instance of the EventDetails dataclass
    """
    start_time = empty_string
    end_time = empty_string
    description_details = get_wikipedia_description(event_text, ':Event')
    if description_details.wiki_desc and 'See the web site' not in description_details.wiki_desc:
        time_query = query_wikidata_time.replace('?item', f'wd:{description_details.wikidata_id}')
        start_time = _get_wikidata_time(time_query, True)
        end_time = _get_wikidata_time(time_query, False)
    return EventDetails(description_details.wiki_desc, description_details.wiki_url,
                        description_details.wikidata_id, start_time, end_time, description_details.labels)


def get_geonames_location(loc_text: str) -> GeoNamesDetails:
    """
    Get the type of location from its text as well as its country and administrative level (if relevant).

    :param loc_text: Location text
    :return: An instance of the GeoNamesDetails dataclass
    """
    # TODO: Add sleep to meet geonames timing requirements
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
        return GeoNamesDetails(empty_string, empty_string, 0, [], empty_string)
    country = _get_xml_value('./geoname/countryName', root)
    feature = _get_xml_value('./geoname/fcl', root)
    fcode = _get_xml_value('./geoname/fcode', root)
    ascii_name = _get_xml_value('./geoname/asciiName', root)
    alt_names, wiki_link = _get_geonames_alt_names(root)
    if not country and not feature:
        return GeoNamesDetails(empty_string, empty_string, 0, [], empty_string)
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
        admin_level = admin_levels[0] if admin_levels else 1
    elif feature in ('H', 'L', 'R', 'S', 'T', 'U', 'V'):
        class_type = geocodes_mapping[feature]
    return GeoNamesDetails(class_type, country, admin_level, alt_names, wiki_link)


def get_wikipedia_description(noun: str, noun_class: str, explicit_link: str = empty_string) -> DescriptionDetails:
    """
    Get the first paragraph of the Wikipedia web page for the specified organization, group, ...
    and a link to display the full page.

    :param noun: String holding the concept name
    :param noun_class: DNA class name corresponding to the concept
    :param explicit_link: A link retrieved from another source (such as GeoNames) to a Wikipedia
                          entry for the noun
    :return: An instance of the DescriptionDetails dataclass
    """
    wikipedia_dict = _get_wikipedia_description(noun.replace(space, '_'), noun_class, explicit_link)
    if not wikipedia_dict:
        return DescriptionDetails(empty_string, empty_string, empty_string, [])
    if 'type' in wikipedia_dict and wikipedia_dict['type'] == 'disambiguation':
        return DescriptionDetails(
            f'Needs disambiguation; See the web site, https://en.wikipedia.org/wiki/{noun.replace(space, "_")}',
            empty_string, empty_string, [])
    desktop_url = empty_string if 'content_urls' not in wikipedia_dict else \
        wikipedia_dict['content_urls']['desktop']['page']
    wikidata_id = empty_string if 'wikibase_item' not in wikipedia_dict else wikipedia_dict['wikibase_item']
    extract = empty_string
    if 'extract' in wikipedia_dict:
        extract_text = wikipedia_dict['extract'].replace('"', "'").replace('\xa0', space).replace('\n', space).\
            encode('ASCII', errors='replace').decode('utf-8')
        wiki_text = f"'{extract_text}'"
        extract = f'From Wikipedia (wikibase_item: {wikidata_id}): {wiki_text}'
    return DescriptionDetails(extract, desktop_url, wikidata_id, _get_wikidata_labels(wikidata_id))
