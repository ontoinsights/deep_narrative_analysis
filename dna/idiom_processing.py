# Handles querying the idiom details and returning information on special processing
# Called by create_event_turtle and nlp_sentence_dictionary.py (latter is a minor usage)

import logging
import os
import pickle

from lark import Lark, Tree
from lark import exceptions as lark_exceptions
from query_ontology_specific_classes import get_norp_emotion_or_lob
from utilities import empty_string, objects_string, preps_string, resources_root

lark_file = os.path.join(resources_root, 'lark.txt')
with open(lark_file, 'r') as inFile:
    lark_details = inFile.read()
idiom_dsl = Lark(lark_details)

noun_idioms_file = os.path.join(resources_root, 'noun-idioms.pickle')
with open(noun_idioms_file, 'rb') as inFile:
    noun_idiom_dict = pickle.load(inFile)

verb_idioms_file = os.path.join(resources_root, 'verb-idioms.pickle')
with open(verb_idioms_file, 'rb') as inFile:
    verb_idiom_dict = pickle.load(inFile)

verb_prep_file = os.path.join(resources_root, 'verb-prep-idioms.pickle')
with open(verb_prep_file, 'rb') as inFile:
    verb_prep_idiom_dict = pickle.load(inFile)


def determine_processing_be(verb_dict: dict) -> list:
    """
    Handle semantic variations of the verb, 'be', such as 'being', 'become', 'am', ...

    :param verb_dict: The dictionary for the verb, 'be' (with prepositions, objects, adverbs, ...)
    :returns: An array of strings with rules on how to render the semantics
    """
    verb_keys = list(verb_dict.keys())
    verb_str = str(verb_dict)
    dsl = []
    if "'prep_text': 'with'" in verb_str:
        prep_str = verb_str.split("'prep_text': 'with'")[1].split(']')[0]  # Get all the text for 'with'
        if 'PERSON' in prep_str:
            return [':MeetingAndEncounter']
        else:
            return [':Affiliation']
    if 'verb_acomp' in verb_keys or objects_string in verb_keys:
        word_dict_term = 'object_text'
        if 'verb_acomp' in verb_keys:
            key_term = 'verb_acomp'
            word_dict_term = 'verb_text'
        else:
            key_term = objects_string
        # Special processing for am/is/was/... + adjectival complement or a direct object
        # For example, "I am Slavic/angry" => be as the verb lemma + Slavic/angry as the acomp
        # For example, "My father was an attorney" => be as the verb lemma + attorney as the object
        word_dicts = verb_dict[key_term]   # Acomp or object details are an array
        for word_dict in word_dicts:
            word_text = word_dict[word_dict_term]
            words = word_text.split(' ')
            for word in words:
                word_type, word_class = get_norp_emotion_or_lob(word)
                if word_type:
                    word_class = word_class.replace('urn:ontoinsights:dna:', empty_string)
                    dsl.append(f"subj > :EnvironmentAndCondition{word_type} ; :has_topic :{word_class} ; "
                               f":word_detail '{word}'")
        # TODO: "am 'tired of'": "prep_of (pobj > :AngerAndAnnoyance ; :has_topic pobj)" or 'am tired': :Exhaustion
    # TODO: "no go" or "no way" > :Impossibility :has_topic"
    if not dsl:
        return [':EventAndState']
    return dsl


def get_noun_idiom(noun: str, noun_phrase: str, noun_type: str, sentence: str, noun_uri: str) -> list:
    """
    Specific semantics have been defined for several nouns - as specified by fixes to the knowledge
    graph. This method looks up the input noun in the nouns dictionary and retrieves the
    semantics.

    :param noun: String holding the noun text
    :param noun_phrase: String specifying the complete noun phrase from the original narrative sentence
    :param noun_type: String holding the type of the noun (e.g., 'FEMALESINGPERSON' or 'PLURALNOUN')
    :param sentence: The full text of the sentence (needed for checking for idioms)
    :param noun_uri: String identifying the URI/URL/individual associated with the noun_text
    :returns: Returns an array of strings defining the Turtle for the noun/noun_phrase
    """
    process_ttl = []
    if noun in noun_idiom_dict.keys():
        processing = [noun_idiom_dict[noun]]
        if processing:
            noun_dict = {'text': noun, 'type': noun_type}
            idiom_ttl = process_idiom_detail(processing, sentence, noun_dict, [])
            for line in idiom_ttl:
                process_ttl.append(f'{noun_uri} a {line} .')
            process_ttl.append(f'{noun_uri} rdfs:label "{noun_phrase}" .')
            if noun_type.startswith('NEG'):
                process_ttl.append(f'{noun_uri} :negation true .')
    return process_ttl


def get_verb_processing(verb_dict: dict) -> list:
    """
    Specific semantics have been defined for idiomatic text, where the text has meaning different
    from the individual words (such as 'fish around' meaning 'search'). This method looks up verb +
    acomp or xcomp combinations in the verb-idioms dictionary and retrieves the
    semantics.

    :param verb_dict: Dictionary holding the verb details
    :returns: If special processing is found, return the details (there may be more than 1 match,
             so an array is returned)
    """
    lemma = verb_dict['verb_lemma']
    if lemma in ('be', 'being', 'become', 'becoming'):
        return determine_processing_be(verb_dict)
    processing = []
    if preps_string in verb_dict.keys():
        for prep in verb_dict[preps_string]:
            preposition = prep['prep_text']
            looking_for = f'{lemma} {preposition}'
            if looking_for in verb_prep_idiom_dict.keys():
                processing.append(verb_prep_idiom_dict[looking_for])
    if lemma in verb_idiom_dict.keys():
        processing.append(verb_idiom_dict[lemma])
    return processing


def parse_idiom(tree: Tree, sentence: str, term_dict: dict, preps: list) -> str:
    """
    Interprets the DSL of the idiom rules to determine if the idiom applies to the sentence, and
    if so, to define the resulting Turtle.

    :param tree: A Lark parse tree of a verb/noun idiom rule
    :param sentence: String holding the complete sentence text
    :param term_dict: Either a noun or a verb dictionary
    :param preps: For a verb idiom, an array holding tuples consisting of the preposition text, and its
                  object text and type; For a noun idiom, the array is empty
    :returns: Either a string holding the Turtle for a processed idiom or an empty string (the string
             starts with the class name and may include Event/State properties)
    """
    result = empty_string
    if tree.data == 'class_name':                  # Example: ":Possession"
        class_name = tree.children[0].value        # There is only 1 word/class name/child
        if 'type' in term_dict.keys() and 'PLURAL' in term_dict['type']:
            # Processing is a reference to 1+ noun or verb classes
            result = f':{class_name}, :Collection'
        else:
            result = f':{class_name}'
    elif tree.data == 'complex_rule':
        for paren_rule in tree.children:           # There can be 1 or more parenthesized rules
            result = parse_idiom(paren_rule.children[0].children[0], sentence, term_dict, preps)
            if result:                             # First non-empty result should be chosen
                break
    elif tree.data == 'keyword_rule':
        # Example: "'back' & dobj > :ReturnRecoveryAndRelease ; :has_topic dobj"
        if len(tree.children) == 4:                # property_tree is optional
            text_tree, objects_tree, class_tree, property_tree = tree.children
        else:
            text_tree, objects_tree, class_tree = tree.children
            property_tree = None
        keyword = empty_string
        for text in text_tree.children:
            keyword += f'{text.value} '
        keyword = keyword[:-1]
        if keyword in sentence:             # For the rule to be valid, the 'keyword' must be in the sentence
            class_name = class_tree.children[0].value
            obj_type = empty_string
            if objects_tree:
                obj_type = objects_tree.children[0].data
            # If the rule references a dobj, then there must be an 'objects' list in the term dictionary
            # If the rule references a pobj, then there must be an 'preps' list in the term dictionary
            if (obj_type == 'dobj' and objects_string in term_dict) or \
                    (obj_type == 'pobj' and preps_string in term_dict):
                result = f':{class_name}'
                if property_tree:           # Example from above: ":has_topic dobj"
                    result += parse_property_text(property_tree)
    elif tree.data == 'obj_rule':        # Example: "Agent dobj > :CaringForDependents ; :has_affected_agent dobj"
        entity_tree = tree.children[0]   # Have to get the children values by specific array reference
        obj1_tree = tree.children[1]
        obj2_tree = tree.children[2]
        class_tree = tree.children[3]
        prop_or_verbs = []
        if len(tree.children) > 4:       # Since there are optional "property or verb" clauses
            for i in range(4, len(tree.children)):
                prop_or_verbs.append(tree.children[i])
        entity_type = empty_string         # There may be a requirement for either an 'agent' or 'location' object
        if entity_tree:
            entity_type = entity_tree.children[0].data
        # If the rule references a dobj, then there must be an 'objects' list in the term dictionary
        # If the rule references a pobj, then there must be an 'preps' list in the term dictionary
        # This needs to hold for both obj1 and (optional) obj2 (if specified)
        ok_to_continue = False
        obj1_type = obj1_tree.children[0].data
        if (obj1_type == 'dobj' and objects_string in term_dict) or \
                (obj1_type == 'pobj' and preps_string in term_dict):
            if obj2_tree:
                obj2_type = obj2_tree.children[0].data
                if (obj2_type == 'dobj' and objects_string in term_dict) or \
                        (obj2_type == 'pobj' and preps_string in term_dict):
                    ok_to_continue = True
            else:
                ok_to_continue = True
        if ok_to_continue:                # Requirements are met
            class_name = class_tree.children[0].value
            result = f':{class_name}'
            for prop_or_verb in prop_or_verbs:
                if prop_or_verb.children[0].data == 'property_text':
                    # Example from above: ":has_affected_agent dobj"
                    result += parse_property_text(prop_or_verb.children[0])
                    if entity_type and obj1_type in result:
                        result = result.replace(obj1_type, f'{obj1_type}({entity_type})')
                else:   # Another verb; Example: "dobj > :Attempt, dobj verb"
                    obj_type, text = prop_or_verb.children[0].children   # Should be a dobj reference
                    if obj_type.data == 'dobj':
                        if 'Ignore' in result:
                            result = 'dobj(verb)'
                        else:
                            result += ', dobj(verb)'
                    else:
                        logging.warning(f'Unexpected obj ref in idiom: {tree}')
    elif tree.data == 'subj_rule':
        class_tree, topic_tree, word_tree = tree.children
        class_name = class_tree.children[0].value.replace('EnvironmentAndCondition', empty_string)
        topic_name = topic_tree.children[0].children[0].value
        word = word_tree.children[0].children[0].value
        result = f':EnvironmentAndCondition ; :has_topic :{topic_name} ; :has_holder subj . ' \
                 f'subj :{class_name} :{topic_name} ; :word_detail "{word}"'
    elif tree.data == 'preposition_rule':
        # Example: "prep_for (Agent pobj > :CaringForDependent ; :has_affected_agent pobj)"
        prep_tree, complex_rule = tree.children
        preposition = prep_tree.value
        prep_found = False
        if preps_string in term_dict:
            for prep in term_dict[preps_string]:
                if prep['prep_text'].lower() == preposition:
                    prep_found = True
                    break
        if prep_found:                                  # Preposition must be found in the sentence to continue
            result = parse_idiom(complex_rule, sentence, term_dict, preps)
            result = result.replace('pobj', f'pobj(prep_{preposition})')
    elif tree.data == 'xcomp_rule':                              # Example: "xcomp > :attempt, attack"
        verb1_tree, verb2_tree = tree.children
        verb1 = verb1_tree.children[0].value                     # Example from above: "attempt"
        verb2 = verb2_tree.value                                 # Example from above: "attack"
        if verb1.lower() != "ignore":
            result = f'xcomp({verb1}, {verb2})'
        else:
            result = f'xcomp({verb2})'
    return result


def parse_property_text(property_tree: Tree) -> str:
    """
    Interprets the DSL of the idiom rules to determine if the idiom applies to the sentence, and
    if so, to define the resulting Turtle. This function should only be relevant for verb idioms.

    :param property_tree: A Lark parse tree of a property_text clause of an idiom rule
    :returns: A string holding the predicate and object type portion of a Turtle statement
    """
    prop_names, prop_obj_type = property_tree.children
    prop_name = ':'
    for pname in prop_names.children:
        # Have to assemble the property name from its component words
        # And put it back together with underscores
        prop_name += f'{pname.value}_'
    prop_name = prop_name[:-1]
    prop_type = prop_obj_type.children[0].data
    return f' ; {prop_name} {prop_type}'


def process_idiom_detail(processing: list, sentence_text: str, term_dict: dict, preps: list) -> list:
    """
    Iterate through the processing strings attempting to match to the conditions. If a match is found,
    translate the processing string into an ontology class and additional Turtle statements, which
    may require the term_dictionary to get info such as the sentence object, preposition object, ...

    An example of a processing string is 'prep_to (Location pobj > :MovementTravelAndTransportation ;
    :has_destination obj_uri) | (pobj > :ReturnRecoveryAndRelease ; :has_topic obj_uri)' which states
    that if a preposition of 'to' is associated with the verb, and the object of the preposition is
    a type of Location, then the event/state is :MovementTravelAndTransportation with the Location
    being the destination. Or, if the object of the preposition is NOT a Location, then the event/state
    is :ReturnRecoveryAndRelease and the object is the entity returned (identified as the topic).

    :param processing: An array of strings holding the possible processing 'rules'/idioms
    :param sentence_text: String holding the complete sentence text
    :param term_dict: Either a noun or a verb dictionary
    :param preps: For a verb idiom, an array holding tuples consisting of the preposition text, and its
                  object text and type; For a noun idiom, the array is empty
    :returns: An array of strings holding the  individual Turtle statements given the matched idiom
              (note that only the subj_rule will return multiple strings)
    """
    logging.info(f'Processing the idiom string, {processing}, for the sentence, {sentence_text}')
    # Process all the individual strings, looking for a match
    # Once a match is found, we are finished since the processing rules should be ordered from specific to default
    result = []
    for process_str in processing:
        if 'EnvironmentAndCondition' not in process_str and result:
            # There may be multiple EnvironmentAndCondition clauses (due to multiple objects)
            # Each needs to be processed
            # But for the other idioms, the first match is assumed to be the best and final
            break
        try:
            process_parse = idiom_dsl.parse(process_str)
        except lark_exceptions.UnexpectedCharacters:
            logging.error(f'Unexpected characters in idiom string')
            continue
        # Tree is start (1 only, children[0]) -> rule (1 only, children[0]) -> specific type of rule
        result.append(parse_idiom(process_parse.children[0].children[0], sentence_text, term_dict, preps))
    if result:
        return result
    elif 'verb_text' in term_dict.keys():
        return [':EventAndState']
    else:
        return ['owl:Thing']
