# Various string and language-specific constants, pre-defined dictionaries and arrays
# Also includes small, utility methods used across different DNA modules

# import base64
import os
import pickle

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dna_dir = os.path.join(base_dir, 'dna')
resources_dir = os.path.join(dna_dir, 'resources/')

language_tag = '@en'

# with open(image_file_logo, "rb") as im_file:
#    encoded_logo = base64.b64encode(im_file.read())

empty_string = ''
space = ' '
subjects_string = 'subjects'
objects_string = 'objects'
preps_string = 'preps'
verbs_string = 'verbs'
underscore = '_'

dna_prefix = 'urn:ontoinsights:dna:'
owl_thing = 'http://www.w3.org/2002/07/owl#Thing'
owl_thing2 = 'owl:Thing'
event_and_state_class = ':EventAndState'

ontologies_database = 'ontologies'

concept_map = {'political': ':PoliticalIdeology',
               'ideology': ':PoliticalIdeology',
               'religio': ':ReligiousBelief',
               'ethnic': ':Ethnicity',
               'nationality': 'Ethnicity',
               'emotion': ':EmotionalResponse'}

# TODO: Move texts to separate file for maintenance/extension by users
# Times
days = ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')
months = ('January', 'February', 'March', 'April', 'May', 'June', 'July',
          'August', 'September', 'October', 'November', 'December')
# TODO: Other incremental times?
incremental_time_keywords = ('ago', 'earlier', 'later', 'next', 'previous', 'prior', 'following')

# People
explicit_plural = ('group', 'people')

family_members = {'mother': 'FEMALE', 'father': 'MALE', 'sister': 'FEMALE', 'brother': 'MALE',
                  'aunt': 'FEMALE', 'uncle': 'MALE', 'grandmother': 'FEMALE', 'grandfather': 'MALE',
                  'parent': empty_string, 'sibling': empty_string, 'cousin': empty_string,
                  'grandparent': empty_string, 'relative': empty_string}
plural_family_members = ('mothers', 'fathers', 'sisters', 'brothers', 'aunts', 'uncles',
                         'grandmothers', 'grandfathers', 'grandparents', 'parents', 'siblings',
                         'cousins', 'relatives')
family_text = ('family', 'families')

# Pronouns
personal_pronouns = ('I', 'we', 'us', 'they', 'them', 'he', 'she', 'it', 'myself', 'ourselves', 'themselves',
                     'herself', 'himself', 'itself', 'my', 'our', 'their', 'her', 'his')
indefinite_pronouns = {'all': 'plural', 'both': 'plural', 'few': 'plural', 'many': 'plural', 'most': 'plural',
                       'none': 'zero', 'some': 'plural'}

# Verbs
aux_lemmas = ('be', 'become', 'do', 'have')
aux_be_lemmas = ('be', 'become')
lemma_be = 'be'
lemma_do = 'do'
aux_verb_dict = {'can': ':OpportunityAndPossibility',
                 'could': ':OpportunityAndPossibility',
                 'may': ':OpportunityAndPossibility',
                 'might': ':OpportunityAndPossibility',
                 'must': ':CommandAndDemand',
                 'should': ':OpportunityAndPossibility,dna:AdviceAndRecommendation',
                 'will': ':IntentionAndGoal,dna:CommandAndDemand',
                 'would': ':OpportunityAndPossibility'}

# Prepositions
# TODO: Other prepositions? Out? Without?
processed_prepositions = ('about', 'after', 'along', 'at', 'before', 'during', 'in', 'inside', 'into',
                          'for', 'from', 'near', 'of', 'on', 'outside', 'to', 'with')
prep_to_predicate = {'about': ':has_topic',
                     'after': 'obj+:before',     # 'obj+' indicates the prep object is the subject of the triple
                     'along': ':has_active_agent=>:Agent',      # No default
                     'at': ':has_location|:has_time=>:Time',    # Default + alternatives separated by '|'
                     'before': ':before',
                     'during': ':during',
                     'in': ':has_topic|:has_location=>:Location',
                     'inside': ':has_location',
                     'into': ':has_location',
                     'for': ':has_topic|:has_time=>:Time|has_affected_agent=>:Agent',
                     'from': ':has_origin|:has_earliest_beginning=>:Time|:has_provider=>:Agent|'
                             'ProductionManufactureAndCreation=>:has_component',
                     'near': ':has_location',
                     'of': 'obj+:has_component',
                     'on': ':has_location',
                     'outside': ':has_location',
                     'to': ':has_topic|:has_recipient=>:Agent|:has_destination=>:Location|:has_latest_end=>:Time',
                     'with': ':has_topic|:has_instrument=>:Resource|:has_location=>:Location|:has_active_agent=>:Agent'}
prep_after = 'after'
prep_with = 'with'
# Indicates the prepositional mapping which should be changed (as the dictionary key),
#   and the value uses the format, event_state_class=>original_predicate>new_predicate
prep_to_predicate_mod = {'to': ':AssessmentAndCharacterization=>:has_recipient>:has_topic'}

# Replace multi-word phrases or non-standard terms acting as conjunctions or prepositions with single word terms
replacement_words = {
    'as well as': 'and',
    'circa': 'in',
    'in addition to': 'and',
    'since': 'for',   # Assumes that clauses such as 'since [noun] [verb]' have already been split out
    'next to': 'near',
    'on behalf of': 'for',
    'prior to': 'before',
    'subsequent to': 'after'
}

relative_clause_words = ('who', 'whose', 'whom', 'which', 'that', 'where', 'when', 'why')
conjunction_words = ('for', 'and', 'nor', 'but', 'or', 'yet', 'so')
special_marks = ('if', 'because', 'since')

# Words that introduce a temporal relation, where the main clause is the following event
earlier_connectors = ('when', 'because', 'since', 'as', 'while', 'before', 'as long as', 'until', 'til', 'where',
                      'given', 'given that', 'wherever', 'whenever', 'anywhere', 'everywhere', 'if')
# Words that introduce a temporal relation with the main clause, where the main clause is the earlier event
later_connectors = ('after', 'so', 'so that', 'therefore', 'consequently', 'though', 'than', 'in order to',
                    'in order that', 'although', 'that')
# If - then only is cause-effect when the tenses of the main and other clause are the same
cause_effect_pairs = [('if', 'then')]
# Prepositions that introduce a cause in the form of a noun phrase
cause_prepositions = ('because of', 'due to', 'as a result [of]', 'as a consequence [of]', 'by means of')
# Prepositions that introduce an effect in the form of a noun phrase
effect_prepositions = ['in order to']

# spaCy NER type mapping
ner_dict = {'PERSON': ':Person',
            'NORP': ':Person',
            'ORG': ':Organization',
            'GPE': ':GeopoliticalEntity',
            'LOC': ':Location',
            'FAC': ':AnthropogenicFeature',
            'EVENT': ':EventAndState'}
ner_types = list(ner_dict.keys())
ner_types.append('DATE')

female_titles = ['Miss', 'Ms', 'Mrs']
male_titles = ['Mr']

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
