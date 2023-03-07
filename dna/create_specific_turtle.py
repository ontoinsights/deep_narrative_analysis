# Functions to clean up the Turtle (before storage in Stardog)
# Called by create_narrative_turtle.py

from rdflib import Graph as RDFGraph
import uuid

from dna.database import query_class, query_database
from dna.queries import query_if_subclass
from dna.query_ontology import get_norp_emotion_or_lob
from dna.query_sources import get_wikipedia_classification
from dna.utilities_and_language_specific import dna_prefix, empty_string, ontologies_database, ttl_prefixes


def _process_class_mapping(class_map: str, indiv_iri: str, is_alt_coll: bool) -> (list, str):
    """
    Create the Turtle assigning a DNA class type (rdf:type) to an individual based on the class mapping
    string. The individual is identified by the indiv_iri. The details in the class mapping may require
    special handling - such as when a noun map indicates both a Person and an Event (which indicates that
    the Person should be associated with an event of that type). For example, a 'civil servant' is
    defined as 'urn:ontoinsights:dna:Person+urn:ontoinsights:dna:GovernmentAndPoliticsBusiness'.

    Note that the association of context is only output when the mapping is for a noun that is the
    object of the sentence.

    :param class_map: A possible type definition for an individual
    :param indiv_iri: A string/IRI identifying the individual
    :param is_alt_coll: Boolean indicating that this processing is related to a collection of
                        alternative mappings (an AlternativeCollection)
    :return: A tuple consisting of two entries - 1) a list of strings holding the Turtle representation
             and 2) a possibly revised class_map string
    """
    type_turtle = []
    revised_map = class_map
    if 'dna:Person+' in class_map:
        for detail in class_map.split('+'):  # Class names that define the type, '+' = multiple inheritance
            if ':Person' in detail or ':Collection' in detail:
                continue
            if ':enum:Female' in detail:
                type_turtle.append(f'{indiv_iri} :has_gender :enum:Female .')
                revised_map = revised_map.replace(f'+{dna_prefix}enum:Female', empty_string)
                continue
            elif ':enum:Male' in detail:
                type_turtle.append(f'{indiv_iri} :has_gender :enum:Male .')
                revised_map = revised_map.replace(f'+{dna_prefix}enum:Male', empty_string)
                continue
            revised_detail = detail.replace(dna_prefix, ":")
            # TODO: Handle rdfs:comment contexts or aspects
            if '-or-' in detail:
                revised_map = revised_map.replace(f'+{detail}', empty_string).replace(detail, empty_string)
                revised_detail = revised_detail.replace('-or-', ' or ')
                type_turtle.append(f'{indiv_iri} rdfs:comment "Business and/or Event contexts, {revised_detail}" .')
                continue
            if query_database('select', query_if_subclass.replace('urnClass', detail)
                              .replace('searchClass', 'Interval'), ontologies_database):
                # Check Interval (such as 'OldAge')
                revised_map = revised_map.replace(f'+{detail}', empty_string).replace(detail, empty_string)
                if is_alt_coll:
                    type_turtle.append(f'{indiv_iri} rdfs:comment "Agent aspect, {revised_detail} .')
                else:
                    type_turtle.append(f'{indiv_iri} :has_agent_aspect {revised_detail} .')
                continue
            if query_database('select', query_if_subclass.replace('urnClass', detail)
                              .replace('searchClass', 'LineOfBusiness'), ontologies_database):
                revised_map = revised_map.replace(f'+{detail}', empty_string).replace(detail, empty_string)
                if is_alt_coll:
                    type_turtle.append(f'{indiv_iri} rdfs:comment "LineOfBusiness context, {revised_detail}" .')
                else:
                    type_turtle.append(f'{indiv_iri} :has_line_of_business {revised_detail} .')
                continue
            if query_database('select', query_if_subclass.replace('urnClass', detail)
                              .replace('searchClass', 'EventAndState'), ontologies_database):
                revised_map = revised_map.replace(f'+{detail}', empty_string).replace(detail, empty_string)
                type_turtle.append(f'{indiv_iri} rdfs:comment "EventAndState context, {revised_detail}" .')
                continue
    if is_alt_coll:
        type_turtle.append(f'{indiv_iri} :has_member {revised_map.replace("+", ", ").replace(dna_prefix, ":")} .')
    else:
        type_turtle.append(f'{indiv_iri} a {revised_map.replace("+", ", ").replace(dna_prefix, ":")} .')
    return type_turtle, revised_map


def cleanup_unused_turtle(turtle: list) -> list:
    """
    Use rdflib to examine the Turtle statements, to determine if any IRIs that are triple subjects
    are included, but are never referenced as objects. They are removed since they might be confusing
    to a user reviewing a knowledge graph.

    :param turtle: An array of the Turtle statements for a sentence/chunk
    :return: The Turtle with any triples with a subject IRI that is not referenced as an object removed
    """
    complete_turtle = ttl_prefixes[:]
    complete_turtle.extend(turtle)
    rdf_graph = RDFGraph()
    graph = rdf_graph.parse(data=' '.join(complete_turtle), format='text/turtle')
    unused_iris = []
    subjects = [subj for subj in graph.subjects(unique=True) if subj.startswith('urn:')]
    objects = [obj for obj in graph.objects(unique=True) if obj.startswith('urn:')]
    for subj in subjects:
        if subj not in objects:
            unused_iris.append(subj)
    # Also check if a LoB, ideology, religion is referenced as an agent aspect AND as an object
    new_turtle = []
    if unused_iris:
        # The Sentence reference is always 'unused'
        if not (len(unused_iris) == 1 and ':Sentence' in str(unused_iris[0])):
            new_turtle = []
            for ttl in turtle:
                found_unused = False
                for unused in unused_iris:
                    if ':Sentence_' in unused or '_Affiliation' in unused:
                        continue
                    if ttl.startswith(f':{str(unused.split(":")[-1])} '):
                        found_unused = True
                        continue
                if not found_unused:
                    new_turtle.append(ttl)
    if new_turtle:
        return new_turtle
    else:
        return turtle


def create_environment_ttl(text: str, specific_class: str, subjects: list, event_iri: str) -> list:
    """
    Return the Turtle for a Person identified as a member of an organization (NORP), as having
    an emotion or as involved in a line of business (LoB).

    :param text: Specific text from the sentence that was used for the identification
    :param specific_class: The most specific class in the DNA ontology to which the text was mapped
    :param subjects: Array of tuples that are the subjects' texts, mappings, types and IRIs
    :param event_iri: String holding the IRI of the Event being described/processed
    :return: Appropriate Turtle statement given the input parameters
    """
    new_ttl = [f'{event_iri} a {specific_class} ; rdfs:label "{text}" .']
    for subj_text, subj_type, subj_mappings, subj_iri in subjects:
        new_ttl.append(f'{event_iri} :has_holder {subj_iri} .')
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
    narr_text = narr_text.replace('"', "'")
    turtle = [f'@prefix : <urn:ontoinsights:dna:> .', '@prefix dc: <http://purl.org/dc/terms/> .',
              f':{graph_id} a :KnowledgeGraph ; dc:created "{created_at}"^^xsd:dateTime ; '
              f':number_triples {number_triples} ; :encodes :Narrative_{graph_id} .',
              f':Narrative_{graph_id} a :Narrative ; dc:creator "{narr_details[0]}" ; '
              f'dc:publisher "{narr_details[2]}" ; dc:source "{narr_details[3]}" ; '
              f'dc:title "{narr_details[4]}" .',
              f':Narrative_{graph_id} :text "{narr_text}" .']
    if narr_details[1] != 'not defined':
        turtle.append(f':Narrative_{graph_id} dc:created "{narr_details[1]}"^^xsd:dateTime .')
    return turtle


def create_quotations_ttl(graph_id: str, quotations: list, quot_dict: dict,
                          quotations_ttl: list, for_default_graph: bool) -> list:
    """
    Return the Turtle related to the quotations in a text - for the data to be added to
    the meta_dna database (if for_meta_dna is True) or adding the detailed 'Quotation#'
    text for the knowledge graph (if for_meta_dna is False).

    :param graph_id: The ID of the graph where the narrative is stored
    :param quotations: An array of quotations extracted from the original text
    :param quot_dict: An array of quotation dictionaries (key = 'Quotation#' which is referenced
                      in a chunk, and value = full quotation text) extracted from the original text
    :param quotations_ttl: The current list of Turtle statements related to the quotations
    :param for_default_graph: A boolean indicating whether this processing is for the default/
                              meta-data graph of the repository
    :return: An array of Turtle statements
    """
    # TODO: Quotation summary
    narr_iri = f':Narrative_{graph_id}'
    if for_default_graph:
        for quotation in quotations:
            quotations_ttl.append(f'{narr_iri} :text_quote "{quotation}" .')
    else:
        for quote_numb, text in quot_dict.items():
            quotations_ttl.append(f':{quote_numb} :text "{text}" .')
    return quotations_ttl


def create_type_turtle(class_mappings: list, subj_iri: str, entity_text: str) -> (list, list):
    """
    Create the Turtle assigning a DNA class type (rdf:type) to an individual. The individual is identified
    by the subj_iri and the type(s) are identified by the class_mappings. Due to a word having multiple
    possible meanings (which may be disambiguated in future code drops), a list of possible
    class types are provided as input.

    :param class_mappings: A list of possible types for an individual
    :param subj_iri: A string/IRI identifying the individual
    :param entity_text: A string holding the original text for the entity (noun or verb)
    :return: A tuple consisting of two arrays - 1) a list of strings holding the Turtle representation
             and 2) a possibly revised class_mappings array
    """
    if not class_mappings:
        return [], []
    revised_mappings = []
    is_alt_coll = False
    if len(class_mappings) > 1:
        is_alt_coll = True
        ttl_list = [f'{subj_iri} a :AlternativeCollection ; :text "{entity_text}" .']
    else:
        ttl_list = []
    for class_map in class_mappings:
        new_ttl, new_map = _process_class_mapping(class_map, subj_iri, is_alt_coll)
        revised_mappings.append(new_map)
        ttl_list.extend(new_ttl)
    return ttl_list, revised_mappings


def create_verb_norp_ttl(text_lemma: str, full_text: str, text_type: str, event_iri: str, ext_sources: bool) -> list:
    """
    Definition of the Turtle for sentence with the verb, "be", and an acomp or direct object - for
    example, "I am angry."

    :param text_lemma: String holding the acomp or direct object's lemma
    :param full_text: String holding the acomp or direct object's full text
    :param text_type: String holding the type of the text (e.g., 'PERSON', 'ADJ', 'PLURALNOUN', ...)
    :param event_iri: A string identifying the sentence verb's IRI
    :param ext_sources: Boolean indicating if external data sources, such as Wikipedia, can be used
    :return: An array defining the Turtle for the event
    """
    norp_ttl = []
    negated = True if text_type.startswith('NEG') else False
    norp_type, norp_class = get_norp_emotion_or_lob(text_lemma)
    if not norp_type and ext_sources:
        norp_type = get_wikipedia_classification(text_lemma)
        norp_class = norp_type
    if norp_type == ':LineOfBusiness':
        if not negated:   # If negated, then only know that the subject is NOT involved in a LoB; TODO: Handle
            norp_ttl.append(f'subj :has_line_of_business {norp_class} ; :line_of_business "{full_text}" .')
    elif norp_type == ':EmotionalResponse' or not norp_type:
        norp_ttl.append(f'{event_iri} a :AttributeAndCharacteristic .')
        if negated:
            norp_ttl.append(f'{event_iri} :negation true .')
        norp_ttl.append(f'{event_iri} :has_holder subj .')
        norp_ttl.append(f'{event_iri} rdfs:label "Holder described as {full_text}" .')
    else:
        if not negated:   # If negated, then only know that the subject does NOT have a certain aspect; TODO: Handle
            norp_ttl.append(f'subj :has_agent_aspect {norp_class} ; :agent_aspect "{full_text}" .')
    return norp_ttl
