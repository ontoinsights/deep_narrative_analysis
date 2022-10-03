# Various string constants and pre-defined dictionaries and arrays
# Also includes small, utility methods used across different DNA modules

# import base64
import os
import pickle

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dna_dir = os.path.join(base_dir, 'dna')
resources_dir = os.path.join(dna_dir, 'resources/')

# with open(image_file_logo, "rb") as im_file:
#    encoded_logo = base64.b64encode(im_file.read())

empty_string = ''
space = ' '
subjects_string = 'subjects'
objects_string = 'objects'
verbs_string = 'verbs'
preps_string = 'preps'

dna_prefix = 'urn:ontoinsights:dna:'
owl_thing = 'http://www.w3.org/2002/07/owl#Thing'
owl_thing2 = 'owl:Thing'
event_and_state_class = ':EventAndState'

ontologies_database = 'ontologies'

family_members = {'mother': 'FEMALE', 'father': 'MALE', 'sister': 'FEMALE', 'brother': 'MALE',
                  'aunt': 'FEMALE', 'uncle': 'MALE', 'grandmother': 'FEMALE', 'grandfather': 'MALE',
                  'parent': empty_string, 'sibling': empty_string, 'cousin': empty_string,
                  'grandparent': empty_string, 'relative': empty_string}

months = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
          'August', 'September', 'October', 'November', 'December']

days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

processed_prepositions = ('about', 'after', 'as', 'at', 'before', 'during', 'in', 'inside', 'into',
                          'for', 'from', 'near', 'of', 'on', 'outside', 'to', 'with', 'without')

prep_to_predicate_for_locs = {'about': ':has_topic',
                              'at': ':has_location',
                              'from': ':has_origin',
                              'to': ':has_destination',
                              'in': ':has_location'}

# Words that introduce a temporal relation, where the main clause is the following event
earlier_connectors = ['when', 'because', 'since', 'as', 'while', 'before', 'as long as', 'until', 'til', 'where',
                      'given', 'given that', 'wherever', 'whenever', 'anywhere', 'everywhere', 'if']
# Words that introduce a temporal relation with the main clause, where the main clause is the earlier event
later_connectors = ['after', 'so', 'so that', 'therefore', 'consequently', 'though', 'than', 'in order to',
                    'in order that', 'although', 'that']
# If - then only is cause-effect when the tenses of the main and other clause are the same
cause_effect_pairs = [('if', 'then')]
# Prepositions that introduce a cause in the form of a noun phrase
cause_prepositions = ['because of', 'due to', 'as a result [of]', 'as a consequence [of]', 'by means of']
# Prepositions that introduce an effect in the form of a noun phrase
effect_prepositions = ['in order to']

ttl_prefixes = ['@prefix : <urn:ontoinsights:dna:> .', '@prefix dna: <urn:ontoinsights:dna:> .',
                '@prefix geo: <urn:ontoinsights:geonames:> .', '@prefix dc: <http://purl.org/dc/terms/> .',
                '@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .']

# A dictionary where the keys are country names and the values are the GeoNames country codes
geocodes_file = os.path.join(f'{dna_dir}/resources', 'countries_mapped_to_geo_codes.pickle')
with open(geocodes_file, 'rb') as inFile:
    names_to_geo_dict = pickle.load(inFile)

# Reused from https://github.com/explosion/coreferee/blob/master/coreferee/lang/common/data/female_names.dat (MIT lic)
fnames_file = os.path.join(resources_dir, 'female_names.txt')
with open(fnames_file, 'r') as fnames:
    fnames_content = fnames.read()
female_names = fnames_content.split('\n')
# Reused from https://github.com/explosion/coreferee/blob/master/coreferee/lang/common/data/male_names.dat (MIT lic)
mnames_file = os.path.join(resources_dir, 'male_names.txt')
with open(mnames_file, 'r') as mnames:
    mnames_content = mnames.read()
male_names = mnames_content.split('\n')


def add_to_dictionary_values(dictionary: dict, key: str, value, value_type):
    """
    Add the value (cast using the value_type parameter) for the specified key in the dictionary,
    if that key exists, or create a new dictionary entry for the key (where the value is a list).

    :param dictionary: The dictionary to be updated
    :param key: String holding the dictionary key
    :param value: The value to be added to the current list of values of the dictionary entry, or
                  a new list is created with the value
    :param value_type: The type of the value
    :return: None (Dictionary is updated)
    """
    values = []
    if key in dictionary:
        values = dictionary[key]
    values.append(value_type(value))
    dictionary[key] = values


def add_unique_to_array(new_array: list, array: list):
    """
    Adds any unique elements from new_array to array.

    :param new_array: An array of elements
    :param array: The array to be updated with any 'new'/unique elements
    :return: None (array is updated)
    """
    for new_elem in new_array:
        if new_elem not in array:      # Element is NOT in the array
            array.append(new_elem)     # So, add it


def check_name_gender(name_str: str) -> str:
    """
    Determines if a reference is to male/female name. Returns a type of either <FEMALE/MALE>SINGPERSON
    (if the gender can be determined) or 'SINGPERSON'.

    :param name_str: The string representing the noun or proper name
    :return: A tuple of 2 strings representing the entity's text and type (with gender if known)
    """
    gender = empty_string
    if space in name_str:
        names = name_str.split(space)
    else:
        names = [name_str]
    for name in names:
        gender = 'FEMALE' if name in female_names else ('MALE' if name in male_names else empty_string)
        if gender:
            break
    return f'{gender}SINGPERSON' if gender else 'SINGNOUN'
