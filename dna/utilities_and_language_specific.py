# Various string and language-specific constants, pre-defined dictionaries and arrays
# Also includes small, utility methods used across different DNA modules

# import base64
import os
import pickle

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dna_dir = os.path.join(base_dir, 'dna')
resources_dir = os.path.join(dna_dir, 'resources/')

language_tag = '@en'

empty_string: str = ''
space: str = ' '
subjects_string: str = 'subjects'
objects_string: str = 'objects'
preps_string: str = 'preps'
verbs_string: str = 'verbs'
underscore: str = '_'

dna_prefix: str = 'urn:ontoinsights:dna:'
meta_db: str = 'meta-dna'
owl_thing: str = 'owl:Thing'
event_and_state_class: str = ':EventAndState'

ontologies_database: str = 'ontologies'

concept_map = {'political': ':PoliticalIdeology',
               'ideology': ':PoliticalIdeology',
               'religio': ':ReligiousBelief',
               'ethnic': ':Ethnicity',
               'nationality': 'Ethnicity'}

# Future: Move texts to separate file for maintenance/extension by users
# Times
days = ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')
months = ('January', 'February', 'March', 'April', 'May', 'June', 'July',
          'August', 'September', 'October', 'November', 'December')

# People
explicit_plural = ('group', 'people')

family_members = {'mother': 'FEMALE', 'father': 'MALE', 'sister': 'FEMALE', 'brother': 'MALE',
                  'aunt': 'FEMALE', 'uncle': 'MALE', 'grandmother': 'FEMALE', 'grandfather': 'MALE',
                  'grandparent': empty_string, 'parent': empty_string, 'sibling': empty_string,
                  'cousin': empty_string, 'relative': empty_string}
plural_family_members = ('mothers', 'fathers', 'sisters', 'brothers', 'aunts', 'uncles',
                         'grandmothers', 'grandfathers', 'grandparents', 'parents', 'siblings',
                         'cousins', 'relatives')
family_text = ('family', 'families')

female_titles = ['Miss', 'Ms', 'Mrs']
male_titles = ['Mr']

# spaCy NER type mapping
ner_dict = {'PERSON': ':Person',
            'NORP': ':Person, :Collection',
            'ORG': ':Organization',
            'GPE': ':GeopoliticalEntity',
            'LOC': ':Location',
            'FAC': ':Location, :AnthropogenicFeature',
            'EVENT': ':EventAndState',
            'DATE': ':PointInTime',
            'LAW': ':LawAndPolicy',
            'PRODUCT': ':Resource',
            'WORK_OF_ART': ':ArtAndCollectible'}
ner_types = list(ner_dict.keys())

ttl_prefixes = ['@prefix : <urn:ontoinsights:dna:> .', '@prefix dna: <urn:ontoinsights:dna:> .',
                '@prefix geo: <urn:ontoinsights:geonames:> .', '@prefix dc: <http://purl.org/dc/terms/> .',
                '@prefix owl: <http://www.w3.org/2002/07/owl#> .',
                '@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .',
                '@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .',
                '@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .']

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

# Future + other prepositions, clause identifiers and marks?
personal_pronouns = ('I', 'we', 'us', 'they', 'them', 'he', 'she', 'it', 'myself', 'ourselves', 'themselves',
                     'herself', 'himself', 'itself')
plural_pronouns = ('we', 'us', 'they', 'them', 'ourselves', 'themselves')
possessive_pronouns = ('my', 'our', 'his', 'her', 'their', 'its')
indefinite_pronouns = {'all': 'plural', 'both': 'plural', 'few': 'plural', 'many': 'plural', 'most': 'plural',
                       'none': 'zero', 'some': 'plural'}
processed_prepositions = ('about', 'after', 'along', 'at', 'before', 'during', 'in', 'inside', 'into',
                          'for', 'from', 'near', 'of', 'on', 'out', 'outside', 'to', 'with')
relative_clause_words = ('who', 'whose', 'whom', 'which', 'that', 'where', 'when', 'why')
conjunction_words = ('and', 'nor', 'but', 'or', 'yet')
special_marks = {
    'reason': ('as', 'because', 'due to', 'for', 'given', 'given that', 'since', 'so'),
    'possibility': ('if', 'in case', 'lest', 'provided that', 'unless'),
    'purpose': ('in order that', 'in order to', 'so that')
}


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
        names = name_str.split()
    else:
        names = [name_str]
    for name in names:
        gender = 'FEMALE' if name in female_names else ('MALE' if name in male_names else empty_string)
        if gender:
            break
    return f'{gender}SINGPERSON' if gender else 'SINGPERSON'
