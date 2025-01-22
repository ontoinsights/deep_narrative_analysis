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

# TODO: Move from hardcoding country and language
from dna.utilities_and_language_specific import add_unique_to_array, country_qualifier, empty_string, \
    language_tags, space, underscore

geonames_user = os.environ.get('GEONAMES_ID')
geocodes_mapping = {'H': ':WaterFeature',
                    'L': ':DesignatedArea',
                    'R': ':TransportationFeature',
                    'S': ':PhysicalLocation',
                    'T': ':GeographicFeature',
                    'U': ':WaterFeature',
                    'V': ':GeographicFeature'}
geonames_url = 'http://api.geonames.org/search?'

wikibase_bearer = os.environ.get('WDATA_BEARER')
wikibase_headers = {'Content-Type': 'application/json',
                    'Authorization': f'Bearer {wikibase_bearer}'}
wikipedia_summary_url = 'https://en.wikipedia.org/api/rest_v1/page/summary/'
# Mapping of spaCy NER types to Wikidata Q-ids
qid_mapping = {'PERSON': 'Q5, Q214339, Q4164871, Q12737077, Q28640',  # human, role, position, occupation, profession
               'NORP': 'Q231002, Q41710, Q7210356, '                  # nationality, ethnic grp, political org,
                       'Q12909644, Q111252415, Q13414953',            #  + pol ideology, religious grp, rel denomination
               'ORG': 'Q43229, Q106668099, Q131085629',               # organization, corporate body, collective agent
               'GPE': 'Q16562419, Q1063239, Q3455524',                # political entity, polity, administrative region
               'LOC': 'Q17334923, Q123349660',                        # physical location, geo-locatable entity
               'FAC': ':Q27096235',                                   # artificial geographic entity (non-natural)
               'EVENT': 'Q1190554, Q3505845, Q483247',                # occurrence, state, phenomenon
               'DATE': 'Q26907166',                                   # temporal entity
               'LAW': 'Q7748, Q1151067,Q1156854',                     # law, rule, policy
               'PRODUCT': 'Q2424752',                                 # product
               'WORK_OF_ART': 'Q838948, Q2342494'}                    # work of art, collectible
wikidata_rest_url = 'https://www.wikidata.org/w/rest.php/wikibase/v1/entities/items/'

wdqs_url = 'https://query.wikidata.org/sparql?format=json&query='
wdqs_instance_of = \
    'SELECT ?instanceOf WHERE { ?item wdt:P31 ?instanceOf . ?instanceOf wdt:P279* wd:poss_super }'
wdqs_event_time = \
    'SELECT ?type ?startTime ?endTime WHERE { ?item wdt:P31 ?type .' \
    'OPTIONAL { ?item wdt:P580 ?startTime } OPTIONAL { ?item wdt:P582 ?endTime } }'

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


def _call_geonames(request: str, loc_str: str) -> Union[etree.Element, None]:
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
    try:
        orig_root = etree.fromstring(response.content)
    except Exception as e:
        logging.error(f'etree.fromstring Exception={str(e)} for response, {response.content}')
        return None
    toponym_name = _get_xml_value('./geoname/toponymName', orig_root)
    ascii_name = _get_xml_value('./geoname/asciiName', orig_root)
    if toponym_name.lower() == loc_str.lower() or loc_str.lower().startswith(toponym_name.lower()):
        return orig_root
    # Try again, forcing a match of fcode = ADM1 - for ex, New York returns New York City, not the state
    if 'fcode=' not in request:
        request += '&fcode=ADM1'
        root = _call_geonames(request, loc_str)
        if root:
            return root
    # Relax the match to the toponym or ascii name containing the location string
    if loc_str.lower() in toponym_name.lower() or loc_str.lower() in ascii_name.lower():
        return orig_root
    return None


def _call_wdqs(query: str, retry: bool = True) -> Union[dict, None]:
    """
    Processes a query to the Wikidata query service.

    :param query: String holding the query.
    :param retry: Boolean indicating that the request be retried on an exception or 'too many requests' error
    :return: Either the query results or None if the request was not successful
    """
    try:
        response = requests.get(f'{wdqs_url}{query.replace(" ", "%20")}')
    except requests.exceptions.ConnectTimeout:
        logging.error(f'Wikidata timeout: Query={query}')
        return None
    except requests.exceptions.RequestException as e:
        if retry:
            return _call_wdqs(query, retry=False)
        else:
            return None
    if response.status_code == 200:
        if response.json()['results']['bindings']:
            return response.json()
        else:
            return None
    if response.status_code == 429:     # Too many requests
        timeout = _get_wikidata_delay(response.headers['retry-after'])
        logging.info(f'Wikidata timeout: {timeout} seconds')
        time.sleep(timeout)
        return _call_wdqs(query)
    return None


def _call_wikidata_rest(path_parameters: str) -> Union[str, list]:
    """
    Queries the Wikidata REST API with the given path parameters. This method assumes that either a
    single string or an array of strings is returned (which is true for labels and alias requests
    with a language tag).

    :param path_parameters: String holding the path parameters
    :return: The Wikidata REST API result as defined
    """
    try:
        response = requests.get(f'{wikidata_rest_url}{path_parameters}', headers=wikibase_headers)
    except requests.exceptions as e:
        logging.error(f'Wikidata REST exception for parameters: {path_parameters}. Exception: {str(e)}')
        return empty_string
    if response.status_code == 200:
        return response.json()
    return empty_string


def _call_wikipedia(noun_text: str) -> dict:
    """
    Queries the REST API of Wikipedia for information about a specific concept/noun.

    :param noun_text: String holding the noun/concept text
    :return: Dictionary holding the details returned from Wikipedia
    """
    try:
        response = requests.get(f'{wikipedia_summary_url}{noun_text}')
    except requests.exceptions.ConnectTimeout:
        logging.error(f'Wikipedia description timeout: Noun={noun_text}')
        return dict()
    except requests.exceptions.RequestException as e:
        logging.error(f'Wikipedia description query exception for noun: {noun_text}. Exception: {str(e)}')
        return dict()
    wiki_dict = response.json()
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


def _get_wikidata_labels(wikidata_id: str, retry: bool = True) -> list:
    """
    Get the labels (labels and aliases) for a Wikidata item using the Wikidata REST API.

    :param wikidata_id: String holding the Q ID of the Wikidata item
    :param retry: Boolean indicating that the request be retried on an exception
    :return: An array of strings that are the rdfs:label and skos:alt_names of the item
    """
    if not wikidata_id:
        return []
    labels = []
    for tag in language_tags:
        label = _call_wikidata_rest(f'{wikidata_id}/labels/{tag}')
        if label:
            add_unique_to_array([label], labels)
        aliases = _call_wikidata_rest(f'{wikidata_id}/aliases/{tag}')
        if aliases:
            add_unique_to_array(aliases, labels)
    return labels


def _get_wikidata_time(query: str, retry: bool = True) -> (str, str):
    """
    Send the query, wdqs_wikidata_time, to WDQS asking for the start and end times of an
    event identified by text (in the mwapi search parameters).

    :param query: The query to be sent with the wikidata ID already in the string
    :param retry: Boolean indicating that the request be retried on an exception
    :return: A tuple with strings holding the start and/or end times if defined; Otherwise, empty strings
    """
    resp_json = _call_wdqs(query)
    start_time = end_time = empty_string
    if resp_json and 'results' in resp_json and 'bindings' in resp_json['results'] and \
                len(resp_json['results']['bindings']) > 0:
            binding = resp_json['results']['bindings'][0]
            if 'startTime' in binding:
                start_time = binding['startTime']['value']
            if 'endTime' in binding:
                end_time = binding['endTime']['value']
    return start_time, end_time


def _get_wikipedia_description(noun_text: str, ner_type: str, explicit_link: str) -> dict:
    """
    Wikipedia call to get page summary information for a concept. If information is not retrieved
    due to the need to disambiguate, nothing is returned. If the entity returned is not an instance of
    an appropriate Q-id in Wikidata, again, nothing is returned.

    :param noun_text: String holding the concept text (with spaces replaced by underscores)
    :param ner_type: Entity type defined by spaCy
    :param explicit_link: A link to a Wikipedia article provided by another source
    :return: A dictionary with the Wikipedia information returned from the request
    """
    wiki_dict = dict()
    if explicit_link:       # Order of processing - explicit link, country-qualified noun text, unmodified noun text
        wiki_dict = _call_wikipedia(explicit_link.split('/')[-1])
    if not wiki_dict:
        noun_text = noun_text.replace(' ', underscore)
        wiki_dict = _call_wikipedia(f'{country_qualifier}_{noun_text}')   # TODO: (Future) Refine context
        if not wiki_dict:
            wiki_dict = _call_wikipedia(noun_text)
    # Check if the wikipedia text/extract matches the DNA class semantic
    if wiki_dict and 'type' in wiki_dict and wiki_dict['type'] != 'disambiguation':
        # TODO: (Future) Examine disambiguated entities for possible match
        if 'wikibase_item' not in wiki_dict:
            return dict()
        qid = wiki_dict['wikibase_item']
        if ner_type in qid_mapping:
            for possible_superclass in qid_mapping[ner_type].split(', '):
                class_query = wdqs_instance_of.replace('?item', f'wd:{qid}').\
                    replace('poss_super', possible_superclass)
                resp_json = _call_wdqs(class_query)
                if resp_json and 'results' in resp_json and 'bindings' in resp_json['results'] and \
                        len(resp_json['results']['bindings']) > 0:
                    return wiki_dict
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


def get_event_details_from_wikidata(event_text: str) -> EventDetails:
    """
    Get the start and end times and alternate names of an event, if it is known to Wikidata.

    :param event_text: Text defining the event
    :return: An instance of the EventDetails dataclass
    """
    start_time = end_time = empty_string
    description_details = get_wikipedia_description(event_text, 'EVENT')
    if description_details.wikidata_id:
        time_query = wdqs_event_time.replace('?item', f'wd:{description_details.wikidata_id}')
        start_time, end_time = _get_wikidata_time(time_query, True)
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
        request = f'{geonames_url}q={loc_text.lower().replace(space, "+").replace(",", "+")}' \
                  f'&style=full&maxRows=1&username={geonames_user}'
    elif space in loc_text:
        request = f'{geonames_url}q={loc_text.lower().replace(space, "+")}&name_equals=' \
                  f'{loc_text.lower().replace(space, "+")}&style=full&maxRows=1&username={geonames_user}'
    else:
        name_startswith = True
        request = f'{geonames_url}q={loc_text.lower()}&name_startsWith={loc_text.lower()}' \
                  f'&style=full&maxRows=1&username={geonames_user}'
    root = _call_geonames(request, loc_text)
    if root is None:
        if name_startswith:
            # Try less restrictive search
            request = f'{geonames_url}q={loc_text.lower()}&style=full&maxRows=1&username={geonames_user}'
            root = _call_geonames(request, loc_text)
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


def get_wikipedia_description(noun: str, ner_type: str, explicit_link: str = empty_string) -> DescriptionDetails:
    """
    Get the first paragraph of the Wikipedia web page for the specified organization, group, ...
    and a link to display the full page.

    :param noun: String holding the concept name
    :param ner_type: Entity type defined by spaCy
    :param explicit_link: A link retrieved from another source (such as GeoNames) to a Wikipedia
                          entry for the noun
    :return: An instance of the DescriptionDetails dataclass
    """
    wikipedia_dict = _get_wikipedia_description(noun.replace(space, '_'), ner_type, explicit_link)
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
