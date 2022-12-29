# Functions to determine the ontology mapping of words and create their corresponding turtle
# Called by create_narrative_turtle.py

import os
import pickle

from dna.create_specific_turtle import create_environment_ttl
from dna.database import query_class
from dna.nlp import get_head_word
from dna.queries import query_event, query_example, query_noun
from dna.query_ontology import check_subclass, check_emotion_loc_movement, get_norp_emotion_or_lob, \
    query_exact_and_approx_match
from dna.query_sources import check_wordnet
from dna.utilities_and_language_specific import aux_lemmas, dna_dir, dna_prefix, empty_string, \
    event_and_state_class, ner_dict, objects_string, owl_thing2, preps_string, space

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
    if not is_verb:
        if text in nouns_multi_dict:
            return nouns_multi_dict[text]
        if space in text:
            text_words = text.split()
            check_text = f'{text_words[-2]} {text_words[-1]}'   # Checking for adj+noun such as 'red tape'
            if check_text in nouns_multi_dict:
                return nouns_multi_dict[check_text]
    return []


def _determine_ontology_verb_be(verb_dict: dict, sent_subjects: list, event_iri: str, turtle: list) -> list:
    """
    Handle semantic variations of the verb, 'be', such as 'being', 'become', 'am', ...

    :param verb_dict: The verb details from the sentence dictionary
    :param sent_subjects: Array of tuples that are the subject text, type, mappings and IRI
    :param event_iri: String holding the IRI of the Event being described/processed
    :param turtle: A list of the Turtle statements/declarations currently defined for the sentence
                   (it may be updated)
    :return: An array holding the class mappings for the verb_text
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
            new_ttl = determine_norp_emotion_or_lob(get_head_word(word_text)[0], sent_subjects, event_iri)
            if new_ttl:
                turtle.extend(new_ttl)
        return empty_string
    else:
        return [event_and_state_class]   # Last resort with no acomp or object detail


def _determine_ontology_verb_do(verb_dict: dict) -> list:
    """
    Determine the appropriate mapping of the lemma, 'do' (assumes a semantic
    of performing some task or activity).

    :param verb_dict: The verb details from the sentence dictionary
    :return: An array of class mappings for the verb_text or an empty list indicating that the
             semantics are already captured in the turtle
    # TODO: Handle "I did the dishes" (where the object indicates what is done)
    """
    return [event_and_state_class]


def _determine_ontology_verb_have(verb_dict: dict) -> list:
    """
    Determine the appropriate mapping of the lemma, 'have' (assumes a semantic of possession).

    :param verb_dict: The verb details from the sentence dictionary
    :return: An array of class mappings for the verb_text or an empty list indicating that the
             semantics are already captured in the turtle
    # TODO: Handle "I had a bath" (an activity)
    """
    return [':Possession']


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
            do_mapping = _determine_ontology_verb_do(verb_dict)[0]
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


def determine_norp_emotion_or_lob(word: str, subjs: list, event_iri: str = empty_string) -> list:
    """
    Return the details for a Person's identification as a member of an organization (NORP), as having
    an emotion or having a line of business (LoB) or political ideology.

    :param word: String that identified the NORP, emotion, ideology or LoB
    :param subjs: Array of tuples that are the subject text, type, mappings and IRI
    :param event_iri: String holding the IRI of the Event being described/processed
    :return: Appropriate Turtle statement given the input parameters
    """
    word_type, word_class = get_norp_emotion_or_lob(word)
    if not word_type:
        return []
    if word_type in ('Ethnicity', 'ReligiousBelief', 'PoliticalIdeology'):
        ttl_stmt = f'subj :has_agent_aspect {word_class} ; :agent_aspect "{word}" .'
    elif word_type == 'LineOfBusiness':
        ttl_stmt = f'subj :has_line_of_business {word_class} ; :line_of_business "{word}" .'
    elif word_type == 'EmotionalResponse':
        return create_environment_ttl(word, word_class, subjs, event_iri)
    else:
        return create_environment_ttl(word, ':EnvironmentAndCondition', subjs, event_iri)
    new_ttl = [f'{event_iri} a :EnvironmentAndCondition ; :has_topic {word_class} .']
    for subj_text, subj_type, subj_mappings, subj_iri in subjs:
        new_ttl.append(ttl_stmt.replace('subj ', f'{subj_iri} '))
        new_ttl.append(f'{event_iri} :has_holder {subj_iri}. ')
        new_ttl.append(f'{event_iri} rdfs:label "Describes that {subj_text} has an aspect of {word}" .')
    return new_ttl


def get_agent_or_loc_class(text_type: str) -> str:
    """
    Returns a class mapping for an Agent or Location based on its type.

    :param text_type: String holding the noun type (such as 'FEMALESINGPERSON')
    :return: The DNA class mapping
    """
    base_type = text_type.replace('PLURAL', empty_string).replace('SING', empty_string).\
        replace('FEMALE', empty_string).replace('MALE', empty_string)
    class_map = ner_dict[base_type]
    if 'PLURAL' in text_type:
        class_map += '+:Collection'
    return class_map


def get_event_state_mapping(verb_text: str, verb_dict: dict, subjs: list,
                            objs: list, event_iri: str, curr_turtle: list) -> list:
    """
    Determine the appropriate event(s)/state(s) in the DNA ontology, that match the semantics of
    the verb.

    :param verb_text: The verb lemma
    :param verb_dict: The verb details from the sentence dictionary
    :param subjs: Array of tuples that are the subject text, type, mappings and IRI
    :param objs: Array of tuples that are the object text, type, mappings and IRI
    :param event_iri: String holding the IRI of the Event being described/processed
    :param curr_turtle: A list of the Turtle statements/declarations currently defined for the sentence
                        (it may be updated)
    :return: An array of class mappings for the verb_text or an empty list indicating that the
             semantics are already captured in the turtle
    """
    if verb_text in aux_lemmas:
        return _determine_ontology_verb_be(verb_dict, subjs, event_iri, curr_turtle)
    elif verb_text in ('do', 'doing'):
        return _determine_ontology_verb_do(verb_dict)
    elif verb_text in ('have', 'having'):
        return _determine_ontology_verb_have(verb_dict)
    if space in verb_text:    # Indicates a verb + prt
        verb_classes = get_mapping_detail(verb_text, verb_dict, subjs)
        if verb_classes != [event_and_state_class]:
            return verb_classes
    # Check for verb + preposition mappings
    if preps_string in verb_dict:
        for prep in verb_dict[preps_string]:
            revised_text = f'{verb_text} {prep["prep_text"]}'
            verb_classes = get_mapping_detail(revised_text, verb_dict, subjs)
            if verb_classes != [event_and_state_class]:
                return verb_classes
    # Check for verb + object mappings
    if objs:
        for obj_text, obj_type, obj_maps, obj_iri in objs:
            verb_classes = get_mapping_detail(f'{verb_text} {get_head_word(obj_text)[0]}', verb_dict, [])
            if verb_classes != [event_and_state_class]:
                return verb_classes
    # Not found, check for the verb alone
    return get_mapping_detail(verb_text, verb_dict, subjs)


def get_mapping_detail(text: str, verb_dict: dict, subjects: list) -> list:
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
    ontol_class = owl_thing2
    if not verb_classes:     # No multiple class mappings
        if space in text:     # verb + prt or verb + prep or event proper noun (such as 'World War II')
            if text.istitle():     # Proper noun
                for text_word in text.split():
                    ontol_class = query_exact_and_approx_match(text_word.lower(), empty_string, True)
                    if ontol_class != owl_thing2:
                        return [ontol_class]
            else:
                ontol_class = query_exact_and_approx_match(text, empty_string, True)    # Check the ontology for match
                if ontol_class != owl_thing2:
                    return check_emotion_loc_movement([ontol_class], 'movement')
        else:
            ontol_class = query_exact_and_approx_match(text.lower(), query_event, True)
        if ontol_class != owl_thing2:
            return check_emotion_loc_movement([ontol_class], 'movement')
        ontol_class = query_class(text.lower(), query_example)                  # Check the example text
        if ontol_class != owl_thing2:
            return check_emotion_loc_movement([ontol_class], 'movement')
    else:
        return check_emotion_loc_movement(verb_classes, 'movement')
    return [event_and_state_class]


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
            ontol_class = query_exact_and_approx_match(head_word, query_noun, False)  # Move to checking the ontology
            if ontol_class == owl_thing2:
                ontol_class = query_exact_and_approx_match(lemma, query_noun, False)
            if ontol_class != owl_thing2:
                noun_classes = [ontol_class]
        elif iteration == 4:
            ontol_class = query_class(head_word, query_example)   # Check inclusion of text in dna:example string
            if ontol_class == owl_thing2:
                ontol_class = query_exact_and_approx_match(lemma, query_example, False)
            if ontol_class != owl_thing2:
                noun_classes = [ontol_class]
        elif iteration == 5:
            head_word = check_wordnet(noun_text)    # Get head word from the definition of the top synset in WordNet
            # Future: Also check thesaurus synonyms?
            if head_word:
                noun_classes, noun_ttl = _revise_noun_mapping(_check_dicts(head_word, False), noun_iri)
            if not noun_classes:
                ontol_class = query_exact_and_approx_match(head_word, query_noun, False)
                if ontol_class != owl_thing2:
                    noun_classes = [ontol_class]
        else:
            break   # Exit - no mapping
    if noun_classes and noun_classes[0] is not None:
        return check_emotion_loc_movement(noun_classes, 'location'), noun_ttl
    return [owl_thing2], noun_ttl
