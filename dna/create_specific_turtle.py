# Functions to clean up the Turtle (before storage in Stardog)
# Called by create_narrative_turtle.py

import uuid

from dna.database import query_class
from dna.queries import query_subclass
from dna.utilities import dna_prefix, empty_string


def _process_class_mapping(class_map: str, indiv_iri: str, process_verb: bool) -> list:
    """
    Create the Turtle assigning an individual a type (rdf:type) based on the class mapping string. The
    individual is identified by the indiv_iri. The details in the class mapping may require special
    handling - such as when a noun map indicates both a Person and an Event (which indicates that
    the Person should be associated with an event of that type).

    :param class_map: A possible type definition for an individual
    :param indiv_iri: A string/IRI identifying the individual
    :param process_verb: Boolean indicating that this processing is for a verb mapping
    :return: A list of strings holding the Turtle type declaration
    """
    type_turtle = []
    if not process_verb and '+' in class_map and \
            ('dna:Person+' in class_map or 'dna:OrganizationalEntity' in class_map):
        for detail in class_map.split('+'):    # Class names that define the type, '+' indicates multiple inheritance
            if query_class(detail, query_lob_or_event.replace('check', 'LineOfBusiness')):
                class_map = class_map.replace(f'+{detail}', empty_string)
                class_map = class_map.replace(detail, empty_string)
                type_turtle.append(
                   f'{indiv_iri} :has_line_of_business {detail.replace(dna_prefix, ":")} .')
            elif query_class(detail, query_lob_or_event.replace('check', 'EventAndState')):
                class_map = class_map.replace(f'+{detail}', empty_string)
                class_map = class_map.replace(detail, empty_string)
                match_iri = f':PersonEvent_{str(uuid.uuid4())[:13]}'
                type_turtle.append(
                        f'{match_iri} a {detail.replace(dna_prefix, ":")} ; '
                        f':has_actor {indiv_iri} .')
    type_turtle.append(f'{indiv_iri} a {class_map.replace("+", ", ")} .')
    return type_turtle


def create_basic_environment_ttl(subjs: list) -> list:
    """
    Create the Turtle for an :EnvironmentAndCondition where the subject(s) are the 'holder's of
    that condition.

    :param subjs: Array of tuples that are the subjects' texts, mappings, types and IRIs
    :return: An array holding the Turtle statements describing the condition
    """
    event_iri = f':{general_type}_{str(uuid.uuid4())[:13]}'
    condition_turtle = [f'{event_iri} a :EnvironmentAndCondition .']
    for subj in subjs:
        subj_text, subj_type, subj_mappings, subj_iri = subj
        condition_turtle.append(f'{event_iri} :has_holder {subj_iri} .')
    return condition_turtle


def create_environment_ttl(text: str, specific_class: str, general_type: str, subjects: list) -> list:
    """
    Return the Turtle for a Person identified as a member of an organization (NORP), as having
    an emotion or as involved in a line of business (LoB).

    :param text: Specific text from the sentence that was used for the identification
    :param specific_class: The most specific class in the DNA ontology to which the text was mapped
    :param general_type: String = either 'EmotionalResponse'|'Ethnicity'|'ReligiousBelief'|
                         'LineOfBusiness'|'PoliticalIdeology'
    :param subjects: Array of tuples that are the subjects' texts, mappings, types and IRIs
    :return: Appropriate Turtle statement given the input parameters
    """
    event_iri = f':{general_type}_{str(uuid.uuid4())[:13]}'
    if general_type == 'EmotionalResponse':
        new_ttl = [f'{event_iri} a {specific_class} ; rdfs:label "{text}" .']
    else:
        new_ttl = [f'{event_iri} a :EnvironmentAndCondition ; :has_topic :{general_type} ; ' 
                   f'rdfs:label "The {general_type} of the holder - {text}." .']
    for subj_text, subj_type, subj_mappings, subj_iri in subjects:
        new_ttl.append(f'{event_iri} :has_holder {subj_iri} .')
        if general_type == 'LineOfBusiness':
            new_ttl.append(f'{subj_iri} :has_line_of_business {specific_class} ; :line_of_business "{text}" .')
        if general_type == 'PoliticalIdeology':
            new_ttl.append(f'{subj_iri} :has_political_ideology {specific_class} ; :political_ideology "{text}" .')
        if general_type == 'ReligiousBelief':
            new_ttl.append(f'{subj_iri} :has_agent_aspect {specific_class} ; :religion "{text}" .')
        if general_type == 'Ethnicity':
            new_ttl.append(f'{subj_iri} :has_agent_aspect {specific_class} ; :ethnicity "{text}" .')
    return new_ttl


def create_metadata_ttl(graph_id: str, narr_text: str, created_at: str,
                        number_triples: int, narr_details: list) -> list:
    """
    Return the metadata Turtle for an ingested or updated narrative.

    :param graph_id: The ID of the graph where the narrative is stored
    :param narr_text: The complete narrative text
    :param created_at: The time that the graph was created or updated
    :param number_triples: Number of triples in the graph
    :param narr_details: The metadata for the narrative - an array of strings indicating the
                         author, publication date, publisher, source and title of the narrative
    :return: An array of Turtle statements
    """
    turtle = [f'@prefix : <urn:ontoinsights:dna:> . @prefix dc: <http://purl.org/dc/terms/> . ',
              f':{graph_id} a :KnowledgeGraph ; dc:created "{created_at}"^^xsd:dateTime ; '
              f':number_triples {number_triples} ; :encodes :Narrative_{graph_id} .',
              f':Narrative_{graph_id} a :Narrative ; dc:creator "{narr_details[0]}" ; '
              f'dc:publisher "{narr_details[2]}" ; dc:source "{narr_details[3]}" ; '
              f'dc:title "{narr_details[4]}" .',
              f':Narrative_{graph_id} :text "{narr_text}" .']
    if narr_details[1] != 'not defined':
        turtle.append(f':Narrative_{graph_id} dc:created "{narr_details[1]}"^^xsd:dateTime .')
    return turtle


def create_quotations_ttl(graph_id: str, quotations: list, quot_dict: dict) -> list:
    """
    Return the Turtle related to the quotations in a text.

    :param graph_id: The ID of the graph where the narrative is stored
    :param quotations: An array of quotations extracted from the original text
    :param quot_dict: An array of quotation dictionaries (key = 'Quotation#' which is referenced
                      in a chunk, and value = full quotation text) extracted from the original text
    :return: An array of Turtle statements
    """
    quote_ttl = []
    narr_iri = f':Narrative_{graph_id}'
    for quotation in quotations:
        quote_ttl.append(f'{narr_iri} :text_quote "{quotation}" .')
    for quote_numb, text in quot_dict.items():
        quote_ttl.append(f':{quote_numb} :text "{text}" .')
    return quote_ttl


def create_type_turtle(class_mappings: list, subj_iri: str, is_verb: bool, noun_text: str) -> list:
    """
    Create the Turtle assigning an individual a type (rdf:type). The individual is identified by the
    subj_iri and the type(s) are identified by the class_mappings. Due to a word having multiple
    possible meanings (which may be disambiguated in future code drops), a list of possible
    class types are provided as input.

    :param class_mappings: A list of possible types for an individual
    :param subj_iri: A string/IRI identifying the individual
    :param is_verb: Boolean indicating that this processing is for a verb mapping
    :param noun_text: A string holding the original text for a noun
    :return: A list of strings holding the Turtle representation
    """
    if len(class_mappings) > 1:
        ttl_list = [f'{subj_iri} a :AlternativeCollection ; :text "{noun_text}" .']
        for class_map in class_mappings:
            ttl_list.extend(_process_class_mapping(class_map, subj_iri, is_verb))
        return ttl_list
    else:
        return _process_class_mapping(class_mappings[0], subj_iri, is_verb)
