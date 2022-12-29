# Query for ontology class details
# To avoid passing a store name parameter, the ontology files are preloaded into an 'ontologies' database
# Called by create_narrative_turtle.py and create_specific_turtle.py

from dna.database import query_class, query_database
from dna.queries import query_emotion, query_match, query_norp_emotion_or_lob, query_subclass
from dna.utilities_and_language_specific import dna_prefix, empty_string, ontologies_database, owl_thing2


def _check_emotion(class_name: str) -> str:
    """
    Determines if the class_name is a positive or negative emotion, or not an emotion.
    If an emotion, then either ":PositiveEmotion', ':NegativeEmotion' or ':EmotionalResponse' will
    be returned.

    :param class_name: A string holding a class name
    :return: A string = :PositiveEmotion, :NegativeEmotion, :EmotionalResponse or an empty string
    """
    emotion_results = query_database('select', query_emotion.replace('keyword', class_name), ontologies_database)
    for emotion_result in emotion_results:
        if 'result' in emotion_result:
            return emotion_result['result']['value']
        if 'overall' in emotion_result:
            return emotion_result['overall']['value']
    return empty_string


def check_emotion_loc_movement(class_mappings: list, check: str) -> list:
    """
    Check if any of the classes in the class_mappings array are a subclass of :EmotionalResponse,
    :MovementTravelAndTransportation or :Location (depending on the value of the check input
    parameter). If so, add the appropriate type to the class_mapping entry. This simplifies checking
    later (when making decisions about predicates and other Turtle statements to add).

    :param class_mappings: An array of mappings to DNA ontology classes
    :param check: String = 'movement', 'location' or 'emotion'
    :return: An updated class_mapping if :EmotionalResponse (or its subclasses, :PositiveEmotion
             and :NegativeEmotion), :MovementTravelAndTransportation or :Location should be
             added to an entry
    """
    if check == 'movement':
        query_str = query_subclass.replace('searchClass', 'MovementTravelAndTransportation')
    elif check == 'location':
        query_str = query_subclass.replace('searchClass', 'Location')
    else:
        query_str = query_emotion
    updated_mappings = []
    for entry in class_mappings:
        if not entry or entry == owl_thing2:
            continue
        if (check == 'movement' and 'MovementTravelAndTransportation' in entry) or \
                (check == 'location' and 'Location' in entry) or (check == 'emotion' and 'Emotion' in entry):
            updated_mappings.append(entry.replace(dna_prefix, ':'))
            continue
        found = empty_string
        if "+" in entry:    # '+' indicates multiple inheritance
            indiv_classes = entry.split('+')
            for indiv in indiv_classes:
                if check == 'emotion':
                    found = _check_emotion(indiv)
                else:
                    result = query_class(indiv, query_str)
                    if result != owl_thing2:
                        found = 'moveOrLoc'
                if found:
                    break
        else:
            if check == 'emotion':
                found = _check_emotion(entry)
            else:
                result = query_class(entry, query_str)
                if result != owl_thing2:
                    found = 'moveOrLoc'
        entry = entry.replace(dna_prefix, ':')
        if check == 'movement':
            updated_mappings.append(
                f'{entry}+:MovementTravelAndTransportation' if found else entry)
        elif check == 'location':
            updated_mappings.append(f'{entry}+:Location' if found else entry)
        else:
            updated_mappings.append(f'{entry}+:{found}' if found else entry)
    return updated_mappings


def check_subclass(class_name: str, check_superclass: str) -> bool:
    """
    Check if the class_name is a subclass of the specified type.

    :param class_name: String holding the class name
    :param check_superclass: String indicating the superclass
    :return: Boolean indicating whether the class is a subclass of the specified superclass
    """
    result = query_class(class_name, query_subclass.replace('searchClass', check_superclass))
    if result != owl_thing2:
        return True
    return False


def get_norp_emotion_or_lob(noun_text: str) -> (str, str):
    """
    Check if the input text is a kind of emotion, ethnicity, religion, line of work or political ideology.

    :param noun_text: String holding the text to be categorized.
    :return: A tuple consisting of a string indicating either 'EmotionalResponse', 'Ethnicity',
             'ReligiousBelief', 'LineOfBusiness' or 'PoliticalIdeology', and the specific subclass
    """
    for class_type in ('EmotionalResponse', 'Ethnicity', 'ReligiousBelief', 'LineOfBusiness', 'PoliticalIdeology'):
        result = query_class(noun_text, query_norp_emotion_or_lob.replace('class_type', class_type))
        if result != owl_thing2:
            return class_type, result.replace(dna_prefix, ':')
    return empty_string, empty_string


def query_exact_and_approx_match(text: str, query_str: str, is_verb: bool) -> str:
    """
    Executes a query_match and then approximate match (identified by the query string) for the
    text. An "approximate" match is written using FILTER CONTAINS.

    :param text: Text to match
    :param query_str: String holding the "approximate" query to execute; If empty, then only an exact
                      match is performed
    :param is_verb: Boolean indicating if this is a check for a noun or verb
    :return: The highest probability class name returned by the query
    """
    if is_verb:
        exact_query = query_match.replace('verb_prob', '100').replace('noun_prob', '90')
    else:
        exact_query = query_match.replace('verb_prob', '90').replace('noun_prob', '100')
    class_name = query_class(text, exact_query)   # Query exact match
    if class_name != owl_thing2:
        return f':{class_name.split(":")[-1]}'
    # Avoid false matches if the word is < 5 characters (for ex, 'end' or 'old' is in many strings)
    if len(text) < 5:
        return owl_thing2
    if query_str:
        class_name = query_class(text, query_str)      # Query approximate match
        # Avoid false matches if the matched class is < 5 characters (for ex, ':End' might be returned for 'friend')
        if class_name != owl_thing2 and len(class_name.split(':')[-1]) > 5:
            return f':{class_name.split(":")[-1]}'
    return owl_thing2
