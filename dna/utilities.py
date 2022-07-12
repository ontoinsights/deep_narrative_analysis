# Various string constants, images and small, utility methods used across different DNA modules

# import base64
import os

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dna_root = os.path.join(base_dir, 'dna')

image_file_logo = os.path.join(resources_root, 'DNA2.png')

# with open(image_file_logo, "rb") as im_file:
#    encoded_logo = base64.b64encode(im_file.read())

empty_string = ''
space = ' '
new_line = '\n'
double_new_line = '\n\n'
subjects_string = 'subjects'
objects_string = 'objects'
verbs_string = 'verbs'
preps_string = 'preps'

dna_prefix = 'urn:ontoinsights:dna:'
owl_thing = 'http://www.w3.org/2002/07/owl#Thing'
owl_thing2 = 'owl:Thing'
event_and_state_class = ':EventAndState'

ontologies_database = 'ontologies'

gender_dict = {'A': ':Agender', 'B': ':Bigender',
               'F': ':Female', 'M': ':Male'}

family_members = {'mother': 'FEMALE', 'father': 'MALE', 'sister': 'FEMALE', 'brother': 'MALE',
                  'aunt': 'FEMALE', 'uncle': 'MALE', 'grandmother': 'FEMALE', 'grandfather': 'MALE',
                  'parent': empty_string, 'sibling': empty_string, 'cousin': empty_string,
                  'grandparent': empty_string, 'relative': empty_string}

months = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
          'August', 'September', 'October', 'November', 'December']

processed_prepositions = ('about', 'after', 'as', 'at', 'before', 'during', 'in', 'inside', 'into',
                          'for', 'from', 'near', 'of', 'on', 'outside', 'to', 'with', 'without')

# Words that introduce a 'causal' clause, where the main clause is the effect
cause_connectors = ['when', 'because', 'since', 'as']
# Words that introduce a 'causal' effect in the main clause, where the other clause is the cause
effect_connectors = ['so', 'therefore', 'consequently']
# If - then only is cause-effect when the tenses of the main and other clause are the same
cause_effect_pairs = [('if', 'then')]
# Prepositions that introduce a cause in the form of a noun phrase
cause_prepositions = ['because of', 'due to', 'as a result [of]', 'as a consequence [of]', 'my means of']
# Prepositions that introduce an effect in the form of a noun phrase
effect_prepositions = ['in order to']


def add_to_dictionary_values(dictionary: dict, key: str, value, value_type):
    """
    Add the value (cast using the value_type parameter) for the specified key in the dictionary,
    if that key exists, or create a new dictionary entry for the key (where the value is a list).

    :param dictionary: The dictionary to be updated
    :param key: String holding the dictionary key
    :param value: The value to be added to the current list of values of the dictionary entry, or
                  a new list is created with the value
    :param value_type: The type of the value
    :return None (Dictionary is updated)
    """
    values = []
    if key in dictionary.keys():
        values = dictionary[key]
    values.append(value_type(value))
    dictionary[key] = values


def add_unique_to_array(new_array: list, array: list):
    """
    Adds any unique elements from new_array to array.

    :param new_array: An array of elements
    :param array: The array to be updated with any 'new'/unique elements
    :return None (array is updated)
    """
    for new_elem in new_array:
        if new_elem not in array:      # Element is NOT in the array
            array.append(new_elem)     # So, add it
