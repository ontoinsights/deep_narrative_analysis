# Various SPARQL queries used in DNA processing

# TODO: Modify code to 'replace' the language tag when the query is executed, vs at 'compile' time (as it is now)
from dna.utilities_and_language_specific import language_tag

construct_kg = 'prefix : <urn:ontoinsights:dna:> prefix dc: <http://purl.org/dc/terms/> ' \
               'CONSTRUCT {?s ?p ?o} WHERE { GRAPH :graph_uuid {?s ?p ?o} } ORDER BY ?s ?p ?o'

count_triples = 'prefix : <urn:ontoinsights:dna:> SELECT (COUNT(*) as ?cnt) WHERE { GRAPH ?g {?s ?p ?o}}'

delete_entity = 'prefix : <urn:ontoinsights:dna:> DELETE {?s ?p ?o} WHERE {?s ?p ?o}'

query_dbs = 'prefix : <urn:ontoinsights:dna:> prefix dc: <http://purl.org/dc/terms/> ' \
            'SELECT * WHERE {?db a :Database ; dc:created ?created}'

query_agent_or_location = 'prefix : <urn:ontoinsights:dna:> SELECT ?result WHERE { ' \
                          '{{keyword rdfs:subClassOf+ :Agent . BIND(":Agent" as ?result)} UNION ' \
                          '{keyword rdfs:subClassOf+ :Location . BIND(":Location" as ?result)}} }'

query_emotion = 'prefix : <urn:ontoinsights:dna:> SELECT ?overall ?result WHERE { ' \
                'keyword rdfs:subClassOf+ :EmotionalResponse . BIND("EmotionalResponse" as ?overall) . ' \
                '{{keyword rdfs:subClassOf+ :PositiveEmotion . BIND("PositiveEmotion" as ?result)} UNION ' \
                '{keyword rdfs:subClassOf+ :NegativeEmotion . BIND("NegativeEmotion" as ?result)}} }'

query_event = 'prefix : <urn:ontoinsights:dna:> SELECT ?class ?prob WHERE { ' \
              '?class rdfs:subClassOf+ :EventAndState . ' \
              '{ { ?class :verb_synonym ?vsyn . FILTER(CONTAINS(?vsyn, "keyword")) . BIND(100 as ?prob) } UNION ' \
              '{ ?class :noun_synonym ?nsyn . FILTER(CONTAINS(?nsyn, "keyword")) . BIND(95 as ?prob) } UNION ' \
              '{ ?class :example ?ex . FILTER(CONTAINS(?ex, "keyword")) . BIND(80 as ?prob) } UNION ' \
              '{ ?class :verb_synonym ?vsyn . FILTER(CONTAINS("keyword", ?vsyn)) . BIND(65 as ?prob) } UNION ' \
              '{ ?class :noun_synonym ?nsyn . FILTER(CONTAINS("keyword", ?nsyn)) . BIND(60 as ?prob) } } ' \
              '} ORDER BY DESC(?prob)'

query_example = 'prefix : <urn:ontoinsights:dna:> SELECT ?class WHERE { ' \
                '?class rdfs:subClassOf+ :EventAndState ; :example ?ex . FILTER(CONTAINS(?ex, "keyword")) . ' \
                'FILTER NOT EXISTS { ?class rdfs:subClassOf+ :LineOfBusiness } ' \
                'FILTER NOT EXISTS { ?class rdfs:subClassOf+ :Ethnicity } ' \
                'FILTER NOT EXISTS { ?class rdfs:subClassOf+ :Enumeration } }'

query_if_subclass = 'prefix : <urn:ontoinsights:dna:> SELECT ?result WHERE { ' \
                    '<urnClass> rdfs:subClassOf+ :searchClass . BIND("true" as ?result) }'

query_match = 'prefix : <urn:ontoinsights:dna:> SELECT ?class ?prob WHERE { ?class a owl:Class . ' \
              '{ { ?class :verb_synonym ?vsyn . FILTER(?vsyn = "keyword"' + language_tag + \
              ') . BIND(verb_prob as ?prob) } UNION { ?class :noun_synonym ?nsyn . FILTER(?nsyn = "keyword"' + \
              language_tag + ') . BIND(noun_prob as ?prob) } } } ORDER BY DESC(?prob)'

query_match_noun = 'prefix : <urn:ontoinsights:dna:> SELECT ?inst ?type WHERE { ' \
              '?inst a ?type ; :noun_synonym ?nsyn . FILTER(?nsyn = "keyword"' + language_tag + ') } LIMIT 1'

query_match_noun_nsyns = 'prefix : <urn:ontoinsights:dna:> SELECT distinct ?nsyn WHERE { ' \
              '?inst a ?type ; :noun_synonym ?nsyn . FILTER(lang(?nsyn) = "' + language_tag[1:] + '") }'

query_narratives = \
    'prefix : <urn:ontoinsights:dna:> prefix dc: <http://purl.org/dc/terms/> SELECT * WHERE { ' \
    '?graph a :KnowledgeGraph ; dc:created ?created ; :number_triples ?numbTriples ; :encodes ?narrative . ' \
    '?narrative dc:creator ?author ; dc:publisher ?publisher; dc:source ?source ; dc:title ?title . ' \
    'OPTIONAL {?narrative dc:created ?narrCreated} BIND(str(?graph) as ?narrId)}'

query_norp_emotion_or_lob = \
    'prefix : <urn:ontoinsights:dna:> SELECT ?class ?prob WHERE { ' \
    '?class rdfs:subClassOf* :class_type . ' \
    '{ { ?class :noun_synonym ?nsyn . FILTER(?nsyn = "keyword"' + language_tag + ') . BIND(100 as ?prob) } UNION ' \
    '{ ?class :noun_synonym ?nsyn . FILTER(CONTAINS(?nsyn, "keyword")) . BIND(90 as ?prob) } UNION ' \
    '{ ?class :noun_synonym ?nsyn . FILTER(CONTAINS("keyword", ?nsyn)) . BIND(80 as ?prob) } UNION ' \
    '{ ?class :definition ?defn . FILTER(CONTAINS(lcase(?defn), " keyword ")) . BIND(70 as ?prob) } UNION ' \
    '{ ?class :definition ?defn . FILTER(CONTAINS(lcase(?defn), "keyword")) . BIND(65 as ?prob) } } ' \
    '} ORDER BY DESC(?prob)'

query_noun = 'prefix : <urn:ontoinsights:dna:> SELECT ?class ?prob WHERE ' \
             '{ ?class a owl:Class { ' \
             '{ ?class :noun_synonym ?nsyn . FILTER(CONTAINS("keyword", ?nsyn)) . BIND(100 as ?prob) } UNION ' \
             '{ ?class :verb_synonym ?vsyn . FILTER(CONTAINS("keyword", ?vsyn)) . BIND(99 as ?prob) } UNION ' \
             '{ ?class :noun_synonym ?nsyn . FILTER(CONTAINS(?nsyn, "keyword")) . BIND(95 as ?prob) } UNION ' \
             '{ ?class :verb_synonym ?vsyn . FILTER(CONTAINS(?vsyn, "keyword")) . BIND(94 as ?prob) } UNION ' \
             '{ ?class :example ?ex . FILTER(CONTAINS(?ex, "keyword")) . BIND(80 as ?prob) } } ' \
             'FILTER NOT EXISTS { ?class rdfs:subClassOf+ :LineOfBusiness } ' \
             'FILTER NOT EXISTS { ?class rdfs:subClassOf+ :Ethnicity } ' \
             'FILTER NOT EXISTS { ?class rdfs:subClassOf+ :Enumeration } } ORDER BY DESC(?prob)'

query_specific_noun = \
    'prefix : <urn:ontoinsights:dna:> SELECT ?iri ?type ?prob WHERE ' \
    '{ ?iri a ?type . ?type rdfs:subClassOf+ class_type . ' \
    '{ { ?iri :noun_synonym ?nsyn . FILTER(?nsyn = "keyword"' + language_tag + ') . BIND(100 as ?prob) } UNION ' \
    '{ ?iri :verb_synonym ?vsyn . FILTER(?vsyn = "keyword"' + language_tag + ') . BIND(99 as ?prob) } UNION ' \
    '{ ?iri :noun_synonym ?nsyn . FILTER(CONTAINS("keyword", ?nsyn)) . BIND(90 as ?prob) } UNION ' \
    '{ ?iri :verb_synonym ?vsyn . FILTER(CONTAINS("keyword", ?vsyn)) . BIND(89 as ?prob) } UNION ' \
    '{ ?iri :noun_synonym ?nsyn . FILTER(CONTAINS(?nsyn, "keyword")) . BIND(80 as ?prob) } UNION ' \
    '{ ?iri :verb_synonym ?vsyn . FILTER(CONTAINS(?vsyn, "keyword")) . BIND(79 as ?prob) } } } ' \
    'ORDER BY DESC(?prob)'

query_subclass = 'prefix : <urn:ontoinsights:dna:> SELECT ?class WHERE { ' \
              '<keyword> rdfs:subClassOf+ :searchClass . BIND("keyword" as ?class) }'

query_wikidata_instance_of = \
    'SELECT DISTINCT ?instanceOf WHERE {?item wd:P31 ?instanceOf}'

language_filter = f'FILTER(lang(?label) = "{language_tag[1:]}")'
query_wikidata_labels = \
    'SELECT DISTINCT ?label WHERE {{?item rdfs:label ?label . ' + language_filter + ' } UNION ' \
    '{?item skos:altLabel ?label . ' + language_filter + ' } }'

query_wikidata_time = 'SELECT DISTINCT ?time WHERE {?item wdt:timeProp ?time}'

update_narrative = \
    'prefix : <urn:ontoinsights:dna:> prefix dc: <http://purl.org/dc/terms/> ' \
    'DELETE {?s dc:created ?created ; :number_triples ?numbTriples} WHERE {' \
    '?s a :KnowledgeGraph ; dc:created ?created ; :number_triples ?numbTriples }'
