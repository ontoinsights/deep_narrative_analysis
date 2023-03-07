# Functions to determine the ontology mapping of words and create their corresponding turtle
# Called by create_narrative_turtle.py

import os
import pickle

from dna.create_specific_turtle import create_type_turtle, create_verb_norp_ttl
from dna.database import query_class
from dna.nlp import get_head_word
from dna.queries import query_event, query_example, query_noun
from dna.query_ontology import check_subclass, check_emotion_loc_movement, get_norp_emotion_or_lob, \
    query_exact_and_approx_match
from dna.query_sources import check_wordnet, get_wikipedia_classification, get_wikipedia_description
from dna.utilities_and_language_specific import aux_be_lemmas, dna_dir, dna_prefix, empty_string, \
    event_and_state_class, lemma_do, ner_dict, objects_string, owl_thing2, preps_string, prep_with, space

resources_dir = os.path.join(dna_dir, 'resources/')
# Pickle files holding nouns/verbs with multiple inheritance and/or multiple mapping choices
# TODO: Correct for language-specific mappings
# TODO: Include in the ontology definitions directly
multi_file = os.path.join(resources_dir, 'nouns-multiple-en.pickle')
with open(multi_file, 'rb') as inFile:
    nouns_multi_dict = pickle.load(inFile)
multi_file = os.path.join(resources_dir, 'verbs-multiple-en.pickle')
with open(multi_file, 'rb') as inFile:
    verbs_multi_dict = pickle.load(inFile)


def _check_dicts(text: str, is_verb: bool) -> list:
    """
    Get the ontology mapping details for a concept from the multiple inheritance dictionaries
    (nouns/verbs_multi_dict).

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
            if len(text_words) > 2:
                check_text = f'{text_words[-2]} {text_words[-1]}'   # Checking for adj+noun such as 'red tape'
                if check_text in nouns_multi_dict:
                    return nouns_multi_dict[check_text]
    return []


def _determine_ontology_verb_be(verb_dict: dict, sent_subjects: list, event_iri: str, turtle: list,
                                ext_sources: bool) -> list:
    """
    Handle semantic variations of the verb, 'be', such as 'being', 'become', 'am', ...

    :param verb_dict: The verb details from the sentence dictionary
    :param sent_subjects: Array of tuples that are the subject text, type, mappings and IRI
    :param event_iri: String holding the IRI of the Event being described/processed
    :param turtle: A list of the Turtle statements/declarations currently defined for the sentence
                   (it may be updated)
    :param ext_sources: A boolean indicating that data from GeoNames, Wikidata, etc. should be
                        added to the parse results if available
    :return: An array holding the class mappings for the verb_text
    """
    verb_str = str(verb_dict)
    if f"'prep_text': '{prep_with}'" in verb_str:
        prep_str = verb_str.split(f"'prep_text': '{prep_with}'")[1].split(']')[0]  # Get all the text for 'with'
        if 'PERSON' in prep_str:
            return [':MeetingAndEncounter']
        elif 'NORP' in prep_str:
            return [':Affiliation']
        else:
            return [event_and_state_class]     # TODO: Improve resolution
    new_ttl = []
    if 'acomp' in verb_dict:
        # Special processing for am/is/was/... + adjectival complement
        # For example, "I am Slavic/angry" => be as the verb lemma + Slavic/angry as the acomp
        word_dicts = verb_dict['acomp']  # Acomp details are an array
        for word_dict in word_dicts:
            if 'full_text' in word_dict:
                entity_text = f'{verb_dict["verb_lemma"]} {word_dict["full_text"]}'
            else:
                entity_text = f'{verb_dict["verb_lemma"]} {word_dict["detail_text"]}'
            mappings = get_event_mapping_detail(f'be {word_dict["detail_text"]}', dict(), [], True)
            if mappings:
                map_turtle, revised_map = create_type_turtle(mappings, event_iri, entity_text)
                new_ttl.extend(map_turtle)
                new_ttl.append(f'{event_iri} :has_holder subj .')
            else:
                new_ttl.extend(create_verb_norp_ttl(word_dict['detail_lemma'], entity_text,
                                                    word_dict['detail_type'], event_iri, ext_sources))
    if objects_string in verb_dict:
        # Special processing for am/is/was/... + direct object
        # For example, "My father was an attorney" => be as the verb lemma + attorney as the object
        word_dicts = verb_dict[objects_string]   # Object details are an array
        for word_dict in word_dicts:
            new_ttl.extend(create_verb_norp_ttl(word_dict['object_lemma'], word_dict['object_text'],
                                                word_dict['object_type'], event_iri, ext_sources))
    if new_ttl:
        final_ttl = []
        for triple in new_ttl:
            if 'subj ' in triple:
                for sent_subject in sent_subjects:
                    final_ttl.append(triple.replace('subj ', f'{sent_subject[3]} '))
            else:
                final_ttl.append(triple)
        turtle.extend(final_ttl)
        return []
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


def _get_noun_mapping_detail(text: str, noun_iri: str, is_plural: bool) -> (list, list):
    """
    Get the ontology mapping details for a concept from the multiple inheritance dictionaries
    (nouns/verbs_multi_dict) and if not found, query the ontology.

    :param text: String holding the text to be mapped
    :param noun_iri: A string identifying the noun (if only the class mapping is important, then
                     the IRI is empty)
    :param is_plural: Boolean indicating that the noun is plural (is a :Collection)
    :return: A tuple with a list of strings representing possible mappings for the noun's text (or an array
             = ['owl:Thing']) and details of any new Turtle for the noun
    """
    # First check the multi-inheritance dicts
    noun_classes = _check_dicts(text, False)
    noun_ttl = []
    if noun_iri and noun_classes:
        if is_plural:
            new_classes = []
            for noun_class in noun_classes:
                new_classes.append(f'{noun_class}+{dna_prefix}Collection')
            noun_classes = new_classes[:]
        noun_ttl, noun_classes = create_type_turtle(noun_classes, noun_iri, text)
    if not noun_classes:
        ontol_class = query_exact_and_approx_match(text, query_noun, False)  # Move to checking the ontology
        if ontol_class == owl_thing2:
            ontol_class = query_class(text, query_example)   # Check inclusion of text in dna:example string
        if ontol_class != owl_thing2:
            if is_plural:
                noun_classes = [f'{ontol_class}+{dna_prefix}Collection']
            else:
                noun_classes = [ontol_class]
    if noun_classes and noun_classes[0] is not None and noun_classes[0] != owl_thing2:
        return check_emotion_loc_movement(noun_classes, 'location'), noun_ttl
    return [owl_thing2], noun_ttl


def _revise_verb_mapping(curr_classes: list, verb_dict: dict, subjs: list) -> list:
    """
    Update the class mappings if they reference any of the classes, dna:Continuation, dna:StartAndBeginning,
    dna:End, dna:Success or dna:Failure, without multiple inheritance.

    :param curr_classes: A list of strings mapping the DNA ontology classes for the verb_text
    :param verb_dict: The verb details from the sentence dictionary
    :param subjs: An array of tuples of the subject nouns' texts, types, DNA class mappings and IRIs
    :return: Updated curr_classes
    """
    updated_classes = []
    for curr_class in curr_classes:
        if curr_class in (f'{dna_prefix}Continuation', f'{dna_prefix}StartAndBeginning', f'{dna_prefix}End',
                          f'{dna_prefix}Success', f'{dna_prefix}Failure'):
            # Define the Event from the subject
            updated_classes.append(curr_class)
            for subj in subjs:
                subj_text, subj_type, subj_classes, subj_iri = subj
                # TODO: What if the subject is imprecise - e.g., this happened?
                noun_mapping, noun_ttl = get_noun_mapping(subj_text, subj_iri,
                                                          True if 'PLURAL' in subj_type else False)
                updated_classes.extend(noun_mapping)
        else:
            updated_classes.append(curr_class)
    return updated_classes


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


def get_event_mapping_detail(text: str, verb_dict: dict, subjects: list, is_verb: bool) -> list:
    """
    Get the ontology mapping details for a concept from the multiple inheritance dictionaries
    (nouns/verbs_multi_dict) and if not found, query the ontology.

    :param text: String holding the text to be mapped
    :param verb_dict: Dictionary holding the parse details of the verb
    :param subjects: An array of subject text, type, mappings and IRI details
    :param is_verb: Boolean indicating that the processing is for verb text
    :return: A list of strings representing possible mappings for the verb's text, or an array
             = [':EventAndState']
    """
    if is_verb:
        if verb_dict:
            verb_classes = _revise_verb_mapping(_check_dicts(text, True), verb_dict, subjects)
        else:
            verb_classes = _check_dicts(text, True)
    else:
        verb_classes = []
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


def get_event_state_mapping(verb_text: str, verb_dict: dict, subjs: list,  objs: list,
                            event_iri: str, curr_turtle: list, ext_sources: bool) -> list:
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
    :param ext_sources: A boolean indicating that data from GeoNames, Wikidata, etc. should be
                        added to the parse results if available
    :return: An array of class mappings for the verb_text or an empty list indicating that the
             semantics are already captured in the turtle
    """
    if verb_text in aux_be_lemmas:
        return _determine_ontology_verb_be(verb_dict, subjs, event_iri, curr_turtle, ext_sources)
    elif verb_text == lemma_do:
        return _determine_ontology_verb_do(verb_dict)
    # TODO: elif verb_text in ('have', 'having'):   Other than Possession, ex: I am having a bath
    if space in verb_text:    # Indicates a verb + prt
        verb_classes = get_event_mapping_detail(verb_text, verb_dict, subjs, True)
        if verb_classes != [event_and_state_class]:
            return verb_classes
    # Check for verb + preposition mappings
    if preps_string in verb_dict:
        for prep in verb_dict[preps_string]:
            revised_text = f'{verb_text} {prep["prep_text"]}'
            verb_classes = get_event_mapping_detail(revised_text, verb_dict, subjs, True)
            if verb_classes != [event_and_state_class]:
                return verb_classes
    # Check for verb + object mappings
    if objs:
        for obj_text, obj_type, obj_maps, obj_iri in objs:
            verb_classes = get_event_mapping_detail(f'{verb_text} {get_head_word(obj_text)[0]}', verb_dict, [], True)
            if verb_classes != [event_and_state_class]:
                return verb_classes
    # TODO: Check for other verb combinations
    # Not found, check for the verb alone
    return get_event_mapping_detail(verb_text, verb_dict, subjs, True)


def get_noun_mapping(noun_text: str, noun_iri: str, is_plural: bool) -> (list, list):
    """
    Processing to determine the mapping of a noun. Noun-preposition-noun or noun-conjunction-noun combinations,
    and word, ontology and definition matches are all examined.

    :param noun_text: String holding the noun text
    :param noun_iri: A string identifying the noun (if only the class mapping is important, then
                     the IRI is empty)
    :param is_plural: Boolean indicating that the noun is plural (is a :Collection)
    :return: A tuple holding a list of strings of the DNA ontology classes for the noun_text or an array
             = [owl:Thing], and an array of new Turtle statements related to the noun
    """
    if not noun_text:
        return [owl_thing2], []
    # First check for the full noun text
    noun_classes, noun_ttl = _get_noun_mapping_detail(noun_text, noun_iri, is_plural)
    lemma, head_word = get_head_word(noun_text)   # Returns the lemma of the head word and the word itself
    if not noun_text.startswith(head_word) and f' {head_word}' not in noun_text:
        # For ex, '95% of vote' - % is the head word, but not preceded by space
        noun_text = noun_text.replace(head_word, f' {head_word}')
    if (not noun_classes or noun_classes == [owl_thing2]) and space not in head_word:
        # Space associated with proper and/or compound nouns
        noun_texts = noun_text.split()
        head_word_index = noun_texts.index(head_word)
        # Check preceding word + noun
        if head_word_index > 0 and len(noun_texts) > 2:
            check_text = f'{noun_texts[head_word_index - 1]} {noun_texts[head_word_index]}'
            noun_classes, noun_ttl = _get_noun_mapping_detail(check_text, noun_iri, is_plural)
            if (not noun_classes or noun_classes == [owl_thing2]) and head_word_index + 2 < len(noun_texts):
                # Check for 3-gram phrases, such as 'difference of opinion'
                check_text = f'{noun_texts[head_word_index]} {noun_texts[head_word_index + 1]} ' \
                             f'{noun_texts[head_word_index + 2]}'
                noun_classes, noun_ttl = _get_noun_mapping_detail(check_text, noun_iri, is_plural)
    iteration = 0
    while not noun_classes or noun_classes == [owl_thing2]:
        iteration += 1
        if iteration == 1:
            # Check head word
            noun_classes, noun_ttl = _get_noun_mapping_detail(head_word, noun_iri, is_plural)
        elif iteration == 2:
            # Check lemma
            noun_classes, noun_ttl = _get_noun_mapping_detail(lemma, noun_iri, is_plural)
        elif iteration == 3:
            head_word = check_wordnet(lemma)    # Get head word from the definition of the top synset in WordNet
            if head_word:
                noun_classes, noun_ttl = _get_noun_mapping_detail(noun_text, noun_iri, is_plural)
        else:
            break   # Exit - no mapping
    if noun_classes[0] != owl_thing2:
        return noun_classes, noun_ttl
    return [owl_thing2], noun_ttl
