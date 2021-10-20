# Query ontology class details
# To avoid passing a store name parameter, the ontology files are pre-loaded into an 'ontologies' database
# Called by create_event_turtle.py

from database import query_ontology
from utilities import empty_string, owl_thing

domain_query_norp_emotion_or_enum = \
    'prefix : <urn:ontoinsights:dna:> SELECT ?class ?prob WHERE { ' \
    'SERVICE <db://domain-database> { ?class rdfs:subClassOf* ?domain_class_type . ' \
    '{ { ?class :noun_synonym ?nsyn . FILTER(?nsyn = "keyword") . BIND(100 as ?prob) } UNION ' \
    '{ ?class rdfs:label ?label . FILTER(?label = "keyword") . BIND(85 as ?prob) } UNION ' \
    '{ ?class :noun_synonym ?nsyn . FILTER(CONTAINS(?nsyn, "keyword")) . BIND(90 as ?prob) } UNION ' \
    '{ ?class rdfs:label ?label . FILTER(CONTAINS(?label, "keyword")) . BIND(85 as ?prob) } UNION ' \
    '{ ?class :definition ?defn . FILTER(CONTAINS(lcase(?defn), " keyword ")) . BIND(80 as ?prob) } UNION ' \
    '{ ?class :definition ?defn . FILTER(CONTAINS(lcase(?defn), "keyword")) . BIND(75 as ?prob) } } } ' \
    'SERVICE <db://ontologies-database> { ?domain_class_type rdfs:subClassOf* :class_type } ' \
    '} ORDER BY DESC(?prob)'

query_norp_emotion_or_enum = \
    'prefix : <urn:ontoinsights:dna:> SELECT ?class ?prob WHERE ' \
    '{ ?class rdfs:subClassOf+ :class_type . ' \
    '{ { ?class :noun_synonym ?nsyn . FILTER(?nsyn = "keyword") . BIND(100 as ?prob) } UNION ' \
    '{ ?class rdfs:label ?label . FILTER(?label = "keyword") . BIND(85 as ?prob) } UNION ' \
    '{ ?class :noun_synonym ?nsyn . FILTER(CONTAINS(?nsyn, "keyword")) . BIND(90 as ?prob) } UNION ' \
    '{ ?class rdfs:label ?label . FILTER(CONTAINS(?label, "keyword")) . BIND(85 as ?prob) } UNION ' \
    '{ ?class :definition ?defn . FILTER(CONTAINS(lcase(?defn), " keyword ")) . BIND(80 as ?prob) } UNION ' \
    '{ ?class :definition ?defn . FILTER(CONTAINS(lcase(?defn), "keyword")) . BIND(75 as ?prob) } } ' \
    '} ORDER BY DESC(?prob)'


def get_norp_emotion_or_enum(noun_text: str) -> (str, str):
    """
    Check if the input text is a kind of ethnicity, religion, line of work or political ideology.

    :param noun_text: String holding the text to be categorized.
    :return A tuple consisting of a string indicating either 'Ethnicity', 'ReligiousBelief',
            'LineOfBusiness' or 'PoliticalIdeology', and the specific subclass
    """
    for class_type in ('Ethnicity', 'ReligiousBelief', 'LineOfBusiness', 'PoliticalIdeology'):
        result = query_ontology(
            noun_text, query_norp_emotion_or_enum.replace('class_type', class_type),
            domain_query_norp_emotion_or_enum.replace('class_type', class_type))
        if result != owl_thing:
            return class_type, result
    return empty_string, empty_string
