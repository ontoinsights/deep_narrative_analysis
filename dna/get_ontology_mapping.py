# Functions to determine the ontology mapping of words and create their corresponding turtle
# Called by create_narrative_turtle.py

import os
import pickle

from dna.create_specific_turtle import create_basic_environment_ttl, create_environment_ttl
from dna.database import query_class
from dna.nlp import get_head_word
from dna.queries import query_event, query_event_example, query_noun
from dna.query_ontology import check_subclass, check_emotion_loc_movement, get_norp_emotion_or_lob, \
    query_exact_and_approx_match
from dna.query_sources import check_wordnet
from dna.utilities import dna_dir, dna_prefix, empty_string, event_and_state_class, objects_string, \
    owl_thing2, preps_string, space

resources_dir = os.path.join(dna_dir, 'resources/')
# Pickle files holding nouns/verbs with multiple inheritance and/or multiple mapping choices
# TODO: Include in ontology directly
multi_file = os.path.join(resources_dir, 'nouns-multiple.pickle')
with open(multi_file, 'rb') as inFile:
    nouns_multi_dict = pickle.load(inFile)
multi_file = os.path.join(resources_dir, 'verbs-multiple.pickle')
with open(multi_file, 'rb') as inFile:
    verbs_multi_dict = pickle.load(inFile)


def _check_dicts(text: str, is_verb: bool) -> list:
    """
    Get the ontology mapping details for a concept from the multiple inheritance dictionaries
    (nouns/verbs_multi_dict) and if not found, query the ontology.

    :param text: String holding the text to be mapped
    :param is_verb: Boolean indicating that the text represents a verb
    :return: A list of strings representing possible mappings
    """
    if is_verb and text in verbs_multi_dict:
        return verbs_multi_dict[text]
    if not is_verb and text in nouns_multi_dict:
        return nouns_multi_dict[text]
    return []


def _revise_noun_mapping(curr_classes: list, noun_iri: str) -> (list, list):
    """
    Update the class mappings if they reference (using a '+') a LineOfBusiness, a stage
    in a Person's life, gender or an Event (such as DishonestyAndDeception or Love).

    :param curr_classes: A list of strings mapping the DNA ontology classes for a noun
    :param noun_iri: An IRI identifying the noun
    :return: A tuple holding an array of the updated curr_classes and new Turtle to be
             added for the noun
    """
    updated_classes = []
    new_ttl = []
    for curr_class in curr_classes:
        if '+' not in curr_class:
            # TODO: Any other types?
            updated_classes.append(curr_class)
            continue
        if not (':Person' in curr_class or ':OrganizationalEntity' in curr_class
                or ':BuildingAndDwelling' in curr_class):
            updated_classes.append(curr_class)
            continue
        classes = curr_class.split('+')
        multi_classes = []
        for cls in classes:
            specific_class = cls.split(':dna:')[1]
            remove_class = False
            # Check for text, Male or Female
            if specific_class in ('Female', 'Male'):
                new_ttl.append(f'{noun_iri} :gender "{specific_class}" .')
                remove_class = True
            # Check Interval (such as 'OldAge')
            elif check_subclass(cls, 'Interval'):
                new_ttl.append(f'{noun_iri} :has_time :{specific_class} .')
                remove_class = True
            # Check LineOfBusiness
            elif check_subclass(cls, 'LineOfBusiness'):
                new_ttl.append(f'{noun_iri} :has_line_of_business :{specific_class} .')
                remove_class = True
            # Check EventAndState
            elif check_subclass(cls, 'EventAndState'):
                new_ttl.append(f'{noun_iri} :has_context :{specific_class} .')
                remove_class = True
            if not remove_class:
                multi_classes.append(cls)
        if multi_classes:
            updated_classes.append('+'.join(multi_classes))
    return updated_classes, new_ttl


def _revise_verb_mapping(curr_classes: list, verb_dict: dict, subjs: list) -> list:
    """
    Update the class mappings if they contain the string, '+do', or reference any of the
    classes, dna:Continuation, dna:StartAndBeginning, dna:End, dna:Success or dna:Failure,
    without multiple inheritance.

    :param curr_classes: A list of strings mapping the DNA ontology classes for the verb_text
    :param verb_dict: The verb details from the sentence dictionary
    :param subjs: An array of tuples of the subject nouns' texts, types, DNA class mappings and IRIs
    :return: Updated curr_classes
    """
    updated_classes = []
    for curr_class in curr_classes:
        if '+do' in curr_class:
            do_mapping = determine_ontology_verb_do(verb_dict)[0]
            new_class = curr_class.replace('+do', empty_string)
            if new_class:
                new_class += f'+{do_mapping}'
            else:
                new_class = do_mapping
            updated_classes.append(new_class)
        elif curr_class in (f'{dna_prefix}Continuation', f'{dna_prefix}StartAndBeginning', f'{dna_prefix}End',
                            f'{dna_prefix}Success', f'{dna_prefix}Failure'):
            # Define the Event from the subject
            updated_classes.append(curr_class)
            for subj in subjs:
                subj_text, subj_type, subj_iri = subj
                # TODO: What if the subject is imprecise - e.g., this happened?
                noun_mapping, noun_ttl = get_noun_mapping(subj_text, empty_string)
                updated_classes.extend(noun_mapping)
        else:
            updated_classes.append(curr_class)
    return updated_classes


def _determine_norp_emotion_or_lob(word: str, subjs: list) -> list:
    """
    Return the details for a Person's identification as a member of an organization (NORP), as having
    an emotion or having a line of business (LoB).

    :param word: String that identified the NORP, emotion or LoB
    :param subjs: Array of tuples that are the subject text, type, mappings and IRI
    :return: Appropriate Turtle statement given the input parameters
    """
    word_type, word_class = get_norp_emotion_or_lob(word)
    if not word_type:
        return []
    return create_environment_ttl(word, word_class.replace(dna_prefix, empty_string), word_type, subjs)


def determine_ontology_verb_be(verb_dict: dict, sent_subjects: list, turtle: list) -> list:
    """
    Handle semantic variations of the verb, 'be', such as 'being', 'become', 'am', ...

    :param verb_dict: The verb details from the sentence dictionary
    :param sent_subjects: Array of tuples that are the subject text, type, mappings and IRI
    :param turtle: A list of the Turtle statements/declarations currently defined for the sentence
                   (it may be updated)
    :return: An array of class mappings for the verb_text or an empty list indicating that the
             semantics are already captured in the turtle
    """
    verb_str = str(verb_dict)
    if "'prep_text': 'with'" in verb_str:
        prep_str = verb_str.split("'prep_text': 'with'")[1].split(']')[0]  # Get all the text for 'with'
        if 'PERSON' in prep_str:
            return [':MeetingAndEncounter']
        else:
            return [':Affiliation']
    if 'verb_acomp' in verb_dict or objects_string in verb_dict:
        if 'verb_acomp' in verb_dict:
            key_term = 'verb_acomp'
            word_dict_term = 'verb_text'
        else:
            key_term = objects_string
            word_dict_term = 'object_text'
        # Special processing for am/is/was/... + adjectival complement or a direct object
        # For example, "I am Slavic/angry" => be as the verb lemma + Slavic/angry as the acomp
        # For example, "My father was an attorney" => be as the verb lemma + attorney as the object
        word_dicts = verb_dict[key_term]   # Acomp or object details are an array
        for word_dict in word_dicts:
            word_text = word_dict[word_dict_term]
            new_ttl = _determine_norp_emotion_or_lob(get_head_word(word_text)[0], sent_subjects)
            if not new_ttl and space in word_text:
                for word in word_text.split(space):    # Try looking up the individual words
                    new_ttl = _determine_norp_emotion_or_lob(word, sent_subjects)
                    if new_ttl:
                        break
            # TODO: Handle text similar to 'She is tall' (e.g., not an emotion, ...), or 'The killer is Mary'
            if new_ttl:    # Truthy indicates that the word_dict was processed
                turtle.extend(new_ttl)
            # else:
                # return create_basic_environment_ttl(sent_subjects)    # TODO: Improve and use objects
    # else:
        # return create_basic_environment_ttl(sent_subjects)            # TODO: Improve
    return []   # Everything addressed by new Turtle


def determine_ontology_verb_do(verb_dict: dict) -> list:
    """
    Determine the appropriate mapping of the lemma, 'do' (assumes a semantic
    of performing some task or activity).

    :param verb_dict: The verb details from the sentence dictionary
    :return: An array of class mappings for the verb_text or an empty list indicating that the
             semantics are already captured in the turtle
    # TODO: Handle "I did the dishes" (where the object indicates what is done)
    """
    return [event_and_state_class]


def determine_ontology_verb_have(verb_dict: dict) -> list:
    """
    Determine the appropriate mapping of the lemma, 'have' (assumes a semantic of possession).

    :param verb_dict: The verb details from the sentence dictionary
    :return: An array of class mappings for the verb_text or an empty list indicating that the
             semantics are already captured in the turtle
    # TODO: Handle "I had a bath" (an activity)
    """
    return [':Possession']


def get_agent_class(text_type: str) -> str:
    """
    Returns a class mapping for an Agent based on its type.

    :param text_type: String holding the noun type (such as 'FEMALESINGPERSON')
    :return: The DNA class mapping
    """
    class_map = ':Person' if 'PERSON' in text_type else \
        ('OrganizationalEntity' if text_type.endswith('ORG') or text_type.endswith('NORP') else
         ('GeopoliticalEntity' if text_type.endswith('GPE') else
          ('Location' if text_type.endswith('LOC') or text_type.endswith('FAC') else
           ('EventAndState' if text_type.endswith('EVENT') else ':Agent'))))
    if 'PLUR' in text_type:
        class_map += '+:Collection'
    return class_map


def get_event_state_mapping(verb_text: str, verb_dict: dict, subjs: list,
                            objs: list, curr_turtle: list) -> list:
    """
    Determine the appropriate event(s)/state(s) in the DNA ontology, that match the semantics of
    the verb.

    :param verb_text: The verb lemma
    :param verb_dict: The verb details from the sentence dictionary
    :param subjs: Array of tuples that are the subject text, type, mappings and IRI
    :param objs: Array of tuples that are the object text, type, mappings and IRI
    :param curr_turtle: A list of the Turtle statements/declarations currently defined for the sentence
                        (it may be updated)
    :return: An array of class mappings for the verb_text or an empty list indicating that the
             semantics are already captured in the turtle
    """
    if verb_text in ('be', 'being', 'become', 'becoming'):
        return determine_ontology_verb_be(verb_dict, subjs, curr_turtle)
    elif verb_text in ('do', 'doing'):
        return determine_ontology_verb_do(verb_dict)
    elif verb_text in ('have', 'having'):
        return determine_ontology_verb_have(verb_dict)
    if space in verb_text:    # Indicates a verb + prt
        verb_classes = get_verb_mapping(verb_text, verb_dict, subjs)
        if verb_classes != [event_and_state_class]:
            return verb_classes
    # Check for verb + preposition mappings
    if preps_string in verb_dict:
        for prep in verb_dict[preps_string]:
            revised_text = f'{verb_text} {prep["prep_text"]}'
            verb_classes = get_verb_mapping(revised_text, verb_dict, subjs)
            if verb_classes != [event_and_state_class]:
                return verb_classes
    # Check for verb + object mappings
    if objs:
        for obj_text, obj_type, obj_maps, obj_iri in objs:
            revised_text = f'{verb_text} {obj_text}'
            verb_classes = get_verb_mapping(revised_text, verb_dict, [])
            if verb_classes != [event_and_state_class]:
                return verb_classes
    # Not found, check for the verb alone
    return get_verb_mapping(verb_text, verb_dict, subjs)


def get_noun_mapping(noun_text: str, noun_iri: str) -> (list, list):
    """
    Processing to determine the mapping of a noun. Word matches, ontology matches, definition matches
    are all examined.

    :param noun_text: String holding the noun text
    :param noun_iri: A string identifying the noun (if only the class mapping is important, then
                     the IRI is empty)
    :return: A tuple holding a list of strings of the DNA ontology classes for the noun_text or an array
             = [owl:Thing], and an array of new Turtle statements related to the noun
    """
    # First check for the 'full' noun text
    if not noun_text:
        return [owl_thing2], []
    noun_classes, noun_ttl = _revise_noun_mapping(_check_dicts(noun_text, False), noun_iri)
    iteration = 0
    lemma = empty_string
    head_word = empty_string
    while not noun_classes:
        iteration += 1
        if iteration == 1:
            # Try the head word
            lemma, head_word = get_head_word(noun_text)   # Returns the lemma of the head word and the word itself
            # Check the head word as specified in the text
            noun_classes, noun_ttl = _revise_noun_mapping(_check_dicts(head_word, False), noun_iri)
        elif iteration == 2:     # Check the head word's lemma
            noun_classes, noun_ttl = _revise_noun_mapping(_check_dicts(lemma, False), noun_iri)
        elif iteration == 3:
            ontol_class = query_exact_and_approx_match(noun_text, query_noun)  # Move to checking the ontology
            if ontol_class == owl_thing2:
                ontol_class = query_exact_and_approx_match(head_word, query_noun)
                if ontol_class != owl_thing2:
                    noun_classes = [ontol_class]
        elif iteration == 4:
            ontol_class = query_class(noun_text, query_event_example)   # Check inclusion of text in dna:example string
            if ontol_class == owl_thing2:
                ontol_class = query_exact_and_approx_match(head_word, query_event_example)
                if ontol_class != owl_thing2:
                    noun_classes = [ontol_class]
        elif iteration == 5:
            head_word = check_wordnet(noun_text)    # Get head word from the definition of the top synset in WordNet
            # Future: Also check thesaurus synonyms?
            if head_word:
                noun_classes, noun_ttl = _revise_noun_mapping(_check_dicts(head_word, False), noun_iri)
            if not noun_classes:
                ontol_class = query_exact_and_approx_match(head_word, query_noun)  # Move to checking the ontology
                if ontol_class != owl_thing2:
                    noun_classes = [ontol_class]
        else:
            break   # Exit - no mapping
    if noun_classes and noun_classes[0] is not None:
        return check_emotion_loc_movement(noun_classes, 'location'), noun_ttl
    return [owl_thing2], noun_ttl


def get_verb_mapping(text: str, verb_dict: dict, subjects: list) -> list:
    """
    Get the ontology mapping details for a concept from the multiple inheritance dictionaries
    (nouns/verbs_multi_dict) and if not found, query the ontology.

    :param text: String holding the text to be mapped
    :param verb_dict: Dictionary holding the parse details of the verb
    :param subjects: An array of subject text, type, mappings and IRI details
    :return: A list of strings representing possible mappings for the verb's text, or an array
             = [':EventAndState']
    """
    verb_classes = _revise_verb_mapping(_check_dicts(text, True), verb_dict, subjects)
    if not verb_classes:     # No multiple class mappings
        if space in text:     # verb + prt or verb + prep or event proper noun (such as 'World War II')
            if text.istitle():     # Proper noun
                for text_word in text.split(space):
                    ontol_class = query_exact_and_approx_match(text_word.lower(), empty_string)
                    if ontol_class != owl_thing2:
                        return [ontol_class]
            else:
                ontol_class = query_exact_and_approx_match(text, empty_string)    # Check the ontology for exact match
                if ontol_class != owl_thing2:
                    return check_emotion_loc_movement([ontol_class], 'movement')
        else:
            ontol_class = query_exact_and_approx_match(text.lower(), query_event)     # Check the ontology
        if ontol_class != owl_thing2:
            return check_emotion_loc_movement([ontol_class], 'movement')
        ontol_class = query_class(text.lower(), query_event_example)                  # Check the example text
        if ontol_class != owl_thing2:
            return check_emotion_loc_movement([ontol_class], 'movement')
    else:
        return check_emotion_loc_movement(verb_classes, 'movement')
    return [event_and_state_class]
