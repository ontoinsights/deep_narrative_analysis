# Handles querying the idiom details and returning information on special processing
# Called by create_event_turtle and nlp_sentence_dictionary.py (latter is a minor usage)

import logging
import os
import pickle

from lark import Lark, Tree
from lark import exceptions as lark_exceptions

from nlp import get_head_word
from query_ontology_specific_classes import get_norp_emotion_or_lob
from utilities import dna_prefix, empty_string, event_and_state_class, objects_string, owl_thing2, preps_string, \
    resources_root, space

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
        dsl = []
        word_dicts = verb_dict[key_term]   # Acomp or object details are an array
        for word_dict in word_dicts:
            word_text = word_dict[word_dict_term]
            word_ttl = _determine_norp_emotion_or_lob(get_head_word(word_text)[0])
            if word_ttl:
                dsl.append(word_ttl)
                continue
            if space in word_text:
                for word in word_text.split(space):    # Try looking up the individual words
                    word_ttl = _determine_norp_emotion_or_lob(word)
                    if word_ttl:
                        dsl.append(word_ttl)
                        break
        if dsl:
            return dsl
        # TODO: Default processing for some text similar to 'She is tall' (e.g., not an emotion, ethnicity, ...)
        if objects_string in verb_keys:
            return ['subj > :EnvironmentAndCondition ; :has_topic dobj ; :has_holder subj']
    return ['subj > :EnvironmentAndCondition ; :has_holder subj']


def get_class_names(tree: Tree) -> str:
    """
    Get one or more class names from an idiom rule.

    :param tree: The class_names tree
    :returns: A string holding the class names, separated by commas
    """
    class_names = []
    for i in range(0, len(tree.children)):
        class_names.append(f':{tree.children[i].children[0].children[0].value}')
    return ', '.join(class_names)


def get_needed_text(tree: Tree) -> str:
    """
    Get the text identified as required (for the rule to apply) from an idiom rule.

    :param tree: The rule tree
    :returns: String with the text that should be present in the sentence, for the rule to apply
    """
    needed_text = ''
    for j in range(0, len(tree.children)):
        needed_text += tree.children[j].value + ' '
        if needed_text:
            needed_text = needed_text.strip()
    return needed_text


def get_noun_idiom(noun: str, noun_phrase: str, noun_type: str, sentence: str, noun_iri: str) -> list:
    """
    Specific semantics have been defined for several nouns - as specified by fixes to the knowledge
    graph. This method looks up the input noun in the nouns dictionary and retrieves the
    semantics.

    :param noun: String holding the noun text
    :param noun_phrase: String specifying the complete noun phrase from the original narrative sentence
    :param noun_type: String holding the type of the noun (e.g., 'FEMALESINGPERSON' or 'PLURALNOUN')
    :param sentence: The full text of the sentence (needed for checking for idioms)
    :param noun_iri: String identifying the IRI/URL/individual associated with the noun_text
    :returns: Returns an array of strings defining the Turtle for the noun/noun_phrase
    """
    process_ttl = []
    if noun in noun_idiom_dict.keys():
        processing = [noun_idiom_dict[noun]]
        if processing:
            noun_dict = {'text': noun_phrase, 'type': noun_type}
            idiom_ttl = process_idiom_detail(processing, sentence, noun_dict, [])
            for line in idiom_ttl:
                process_ttl.append(f'{noun_iri} a {line} .')
            process_ttl.append(f'{noun_iri} rdfs:label "{noun_phrase}" .')
            if noun_type.startswith('NEG'):
                process_ttl.append(f'{noun_iri} :negation true .')
    else:
        if space in noun:
            head_noun = get_head_word(noun)
            process_ttl = get_noun_idiom(head_noun, noun, noun_type, sentence, noun_iri)
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
    if tree.data == 'class_names':                  # Example: ":Possession"
        result = get_class_names(tree)
        if 'type' in term_dict.keys() and 'PLURAL' in term_dict['type'] and ':Collection' not in result:
            # Processing is a reference to 1+ noun or verb classes
            result += ', :Collection'
    elif tree.data == 'complex_rule':
        for paren_rule in tree.children:           # There can be 1 or more parenthesized rules
            # Each paren_rule has 1 child (children[0]) = 'rule' and then that has 1 child with the specific rule type
            result = parse_idiom(paren_rule.children[0].children[0], sentence, term_dict, preps)
            if result:                             # First non-empty result should be chosen
                break
    elif tree.data == 'noun_rule':
        # Example: "secretary": ":Person . affiliation Secretary Organization"
        result = owl_thing2    # Default
        increment = 0
        needed_text = empty_string
        affiliation_details = []
        lob_detail = empty_string
        if tree.children[0].data == 'text':  # May have text to check for
            increment = 1
            needed_text = get_needed_text(tree.children[0])
        if not needed_text or needed_text in sentence:  # For the rule to be valid, needed_text must be in the sentence
            noun_classes = get_class_names(tree.children[increment])
            if (needed_text and len(tree.children) == 3) or (not needed_text and len(tree.children) == 2):
                if tree.children[increment + 1].data == "affiliation_statement":
                    affiliation_details.append(tree.children[increment + 1].children[0].children[0].value)
                    affiliation_details.append(tree.children[increment + 1].children[1].children[0].value)
                else:  # lob_statement
                    lob_detail = tree.children[increment + 1].children[0].children[0].value
            result = noun_classes
        if result:
            if affiliation_details:
                result += f' . noun_iri{affiliation_details[0]}Affiliation a :Affiliation ; ' \
                          f':affiliated_agent noun_iri ; ' \
                          f':affiliated_with noun_iri{affiliation_details[1]}'
            if lob_detail:
                result += f'; :has_line_of_business :{lob_detail}'
    elif tree.data == 'verb_rule':        # Example: "Agent dobj > :CaringForDependents ; :has_affected_agent dobj"
        result = event_and_state_class
        objects = []
        verbs = empty_string
        other_verb = empty_string
        property_details = []
        property_refs = []
        for j in range(0, len(tree.children)):
            child = tree.children[j]
            if child.data == 'text':  # May have text to check for
                need_text = get_needed_text(child)
                if need_text not in sentence:  # For the rule to be valid, need_text must be in the sentence
                    break
            elif child.data == 'obj_detail':
                obj_text = ''
                for k in range(0, len(child.children)):
                    if child.children[k].data == 'entity_type':
                        obj_text = child.children[k].children[0].data + ' '
                    else:
                        obj_text += child.children[k].children[0].data
                objects.append(obj_text)
            elif child.data == 'class_names':
                verbs = get_class_names(child)
            elif child.data == 'property_detail':
                property_details.append(
                    f'; :{child.children[0].children[0].children[0].value} {child.children[1].children[0].data}')
            elif child.data == 'property_ref':
                property_refs.append(
                    f'; :{child.children[0].children[0].children[0].value} '
                    f':{child.children[1].children[0].children[0].value}')
            elif child.data == 'other_verb':
                other_verb = f'dobj {child.children[0].value}'
        if verbs:    # Might have broken out of the above loop, since the need_text was not in the sentence
            # Need to at least have verbs to continue
            # Check if the rule references dobj/pobj, then there are 'objects'/'preps' lists in the term dictionary
            ok_to_continue = True
            for obj in objects:
                if not (('dobj' in obj and objects_string in term_dict) or
                        ('pobj' in obj and preps_string in term_dict)):
                    ok_to_continue = False
            if ok_to_continue:                # Requirements are met
                if other_verb:     # Another verb; Example: "dobj > :Attempt, dobj verb"
                    if ':Ignore' in verbs:
                        result = 'dobj(verb)'
                    else:
                        result = f'{verbs}, dobj(verb)'
                else:
                    result = verbs
                obj_dict = dict()
                for obj in objects:
                    if obj == 'dobj':
                        obj_dict['dobj'] = obj
                    elif ' dobj' in obj:
                        obj_dict['dobj'] = f'dobj({obj.split(space)[0].title()})'
                    if obj == 'pobj':
                        obj_dict['pobj'] = obj
                    elif ' pobj' in obj:
                        obj_dict['pobj'] = f'pobj({obj.split(space)[0].title()})'
                for prop_detail in property_details:    # Example from above: ":has_affected_agent dobj"
                    if 'dobj' in prop_detail:
                        result += prop_detail.replace('dobj', obj_dict['dobj'])
                    if 'pobj' in prop_detail:
                        result += prop_detail.replace('pobj', obj_dict['pobj'])
                for prop_detail in property_details:    # Example from above: ":has_affected_agent dobj"
                    if 'dobj' in prop_detail:
                        result += prop_detail.replace('dobj', obj_dict['dobj'])
                for prop_ref in property_refs:    # Example ":has_topic :PoliticalEnvironment"
                    result += prop_ref
    elif tree.data == 'verb_subject_rule':
        # Example: "subj > :EnvironmentAndConditionLineOfBusiness ; :has_topic :Judiciary ;
        #    :has_holder subj ; :word_detail 'attorney'"
        result = get_class_names(tree.children[0])
        for i in range(1, len(tree.children)):
            if tree.children[i].data == 'topic':
                if tree.children[i].children[0].data == 'dobj':
                    result += '; :has_topic dobj '
                else:
                    result += f'; :has_topic :{tree.children[i].children[0].children[0].children[0].value} '
            elif tree.children[i].data == 'word_detail':
                result += f"; :word_detail '{tree.children[i].children[0].value}' "
            elif tree.children[i].data == 'holder':
                result += f'; :has_holder {tree.children[i].children[0].value} '
        result = result.strip()
    elif tree.data == 'verb_preposition_rule':
        # Example: "prep_for (Agent pobj > :CaringForDependent ; :has_affected_agent pobj)"
        prep_tree, complex_rule = tree.children
        preposition = prep_tree.value
        prep_found = False
        if preps_string in term_dict:
            for prep in term_dict[preps_string]:
                if prep['prep_text'].lower() == preposition:
                    prep_found = True
                    break
        if prep_found:        # Preposition must be found in the sentence to continue
            result = parse_idiom(complex_rule, sentence, term_dict, preps)
            result = result.replace('pobj', f'pobj(prep_{preposition})')
        else:
            result = event_and_state_class
    elif tree.data == 'verb_xcomp_rule':          # Example: "xcomp > attempt, attack"
        if len(tree.children) == 2:
            verb1 = tree.children[0].value
            verb2 = tree.children[1].value
        else:
            verb1 = f'{tree.children[0].value} {tree.children[1].value}'
            verb2 = tree.children[2].value
        result = f'xcomp({verb1}, {verb2})'
    return result


def process_idiom_detail(processing: list, sentence_text: str, term_dict: dict, preps: list) -> list:
    """
    Iterate through the processing strings attempting to match to the conditions. If a match is found,
    translate the processing string into an ontology class and additional Turtle statements, which
    may require the term_dictionary to get info such as the sentence object, preposition object, ...

    An example of a processing string is 'prep_to (Location pobj > :MovementTravelAndTransportation ;
    :has_destination obj_iri) | (pobj > :ReturnRecoveryAndRelease ; :has_topic obj_iri)' which states
    that if a preposition of 'to' is associated with the verb, and the object of the preposition is
    a type of Location, then the event/state is :MovementTravelAndTransportation with the Location
    being the destination. Or, if the object of the preposition is NOT a Location, then the event/state
    is :ReturnRecoveryAndRelease and the object is the entity returned (identified as the topic).

    :param processing: An array of strings holding the possible processing 'rules'/idioms
    :param sentence_text: String holding the complete sentence text
    :param term_dict: Either a noun or a verb dictionary
    :param preps: For a verb idiom, an array holding tuples consisting of the preposition text, and its
                  object text, type and IRI; For a noun idiom, the array is empty
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
        # Tree starts with 1 child (children[0]) -> a single rule (again, children[0]) -> specific type of rule
        result.append(parse_idiom(process_parse.children[0].children[0], sentence_text, term_dict, preps))
    if result:
        return result
    elif 'verb_text' in term_dict.keys():
        return [':EventAndState']
    else:
        return ['owl:Thing']


# Functions internal to the module
def _determine_norp_emotion_or_lob(word: str) -> str:
    """
    Return the details for a Person's identification as a member of an organization (NORP), as having
    an emotion or having a line of business (LoB).

    :param word: String that could identify the NORP, emotion or LoB
    :returns: Appropriate Turtle statement for the 'environment or condition'
    """
    word_type, word_class = get_norp_emotion_or_lob(word)
    if word_type:
        word_class = word_class.replace(dna_prefix, empty_string)
        return f"subj > :EnvironmentAndCondition{word_type} ; :has_topic :{word_class} ; " \
               f":has_holder subj ; :word_detail '{word}'"
    return empty_string
