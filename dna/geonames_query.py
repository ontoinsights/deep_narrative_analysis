# Query location details using GeoNames API
# Called by create_event_turtle and create_metadata_turtle.py

import configparser as cp
import logging
import os
import pickle
import requests
import xml.etree.ElementTree as etree

from utilities import base_dir, empty_string, resources_root

config = cp.RawConfigParser()
config.read(f'{resources_root}dna.config')
# Set geoname user id
geonamesUser = config.get('GeoNamesConfig', 'geonamesUser')

geocodes_file = os.path.join(base_dir, 'dna/resources/country_names_mapped_to_geo_codes.pickle')
with open(geocodes_file, 'rb') as inFile:
    names_to_geo_dict = pickle.load(inFile)


def get_location_details(last_loc: str, country_only: bool) -> (str, str, int):
    """
    Get the type of location from its text as well as its country and administrative level (if relevant).

    :param last_loc: Location text
    :param country_only: Boolean indicating that only the country name is needed
    :return A tuple holding the location's class type, country name (or an empty string or None),
            and an administrative level (if 0, then admin level is not applicable) or GeoNames ID
            (for a Country)
    """
    logging.info(f'Getting location details for {last_loc}')
    # TODO: Add sleep to meet geonames timing requirements?
    if last_loc in names_to_geo_dict.keys():
        return ':Country', last_loc, names_to_geo_dict[last_loc]
    response = requests.get(
        f'http://api.geonames.org/search?q={last_loc.lower().replace(" ", "+")}&maxRows=1&username={geonamesUser}')
    root = etree.fromstring(response.content)
    country = _get_xml_value('./geoname/countryName', root)
    if country_only:
        return empty_string, country, 0
    feature = _get_xml_value('./geoname/fcl', root)
    fcode = _get_xml_value('./geoname/fcode', root)
    # Defaults
    admin_level = 0
    class_type = ":PopulatedPlace"
    if feature == 'A':     # Administrative area
        if fcode.startswith('ADM'):
            class_type += ', :AdministrativeDivision'
            # Get administrative level
            if any([i for i in fcode if i.isdigit()]):
                admin_level = [int(i) for i in fcode if i.isdigit()][0]
        elif fcode.startswith('PCL'):  # Some kind of political entity, assuming for now that it is a country
            class_type = ":Country"
        elif fcode.startswith('L') or fcode.startswith('Z'):
            # Leased area usually for military installations or a zone, such as a demilitarized zone
            return empty_string, empty_string, admin_level
    elif feature == 'P':   # Populated Place
        if fcode.startswith('PPLA'):
            class_type += ', :AdministrativeDivision'
            # Get administrative level
            admin_levels = [int(i) for i in fcode if i.isdigit()]
            if admin_levels:
                admin_level = admin_levels[0]
            else:
                admin_level = 1
    return class_type, country, admin_level


# Functions internal to the module
def _get_xml_value(xpath: str, root: etree.Element) -> str:
    """
    Uses an xpath string to access specific elements in an XML tree.

    :param xpath: String identifying the path to the element to be retrieved
    :param root: The root element of the XML tree
    :return String representing the value of the specified element or an empty string
            (if not defined)
    """
    elems = root.findall(xpath)
    if elems:
        return elems[0].text
    else:
        return empty_string
