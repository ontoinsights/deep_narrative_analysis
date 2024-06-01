# Various SPARQL queries used in DNA processing

from dna.utilities_and_language_specific import dna_prefix

construct_kg = 'prefix : <urn:ontoinsights:dna:> prefix dc: <http://purl.org/dc/terms/> ' \
               'CONSTRUCT {?s ?p ?o} FROM ?named WHERE {?s ?p ?o} ORDER BY ?s'

count_triples = 'prefix : <urn:ontoinsights:dna:> SELECT (COUNT(*) as ?cnt) WHERE { GRAPH ?g {?s ?p ?o} }'

delete_repo_metadata = 'prefix : <urn:ontoinsights:dna:> prefix dc: <http://purl.org/dc/terms/> ' \
                       'DELETE {?repo a :Database ; dc:created ?created} ' \
                       'WHERE {?repo a :Database ; dc:created ?created}'

delete_narrative = 'prefix : <urn:ontoinsights:dna:> WITH ?named ' \
                   'DELETE {:narr_id ?graph_p ?graph_o . :Narrative_narr_id ?narr_p ?narr_o} ' \
                   'WHERE {:narr_id ?graph_p ?graph_o . :Narrative_narr_id ?narr_p ?narr_o}'

query_corrections = \
    'prefix : <urn:ontoinsights:dna:> SELECT * WHERE { GRAPH ?named {?s a :Correction; a ?type; rdfs:label ?label}}'

query_manual_corrections = \
    'prefix : <urn:ontoinsights:dna:> SELECT * WHERE {?s a :Correction; a ?type; rdfs:label ?label}'

query_narratives = \
    'prefix : <urn:ontoinsights:dna:> prefix dc: <http://purl.org/dc/terms/> SELECT * WHERE { GRAPH ?named { ' \
    '?graph a :InformationGraph ; dc:created ?created ; :number_triples ?numbTriples ; :encodes ?narrative . ' \
    '?narrative :source ?source ; dc:title ?title ; :number_sentences ?sents ; :number_ingested ?ingested ; ' \
    'dc:created ?published ; :external_link ?url } }'

query_repos = 'prefix : <urn:ontoinsights:dna:> prefix dc: <http://purl.org/dc/terms/> ' \
              'SELECT * WHERE {?repo a :Database ; dc:created ?created}'

query_repo_graphs = 'prefix : <urn:ontoinsights:dna:> prefix dc: <http://purl.org/dc/terms/> ' \
                   'SELECT distinct ?g WHERE { GRAPH ?g {?s ?p ?o} FILTER (CONTAINS(str(?g), "?repo")) }'

update_narrative = \
    'prefix : <urn:ontoinsights:dna:> prefix dc: <http://purl.org/dc/terms/> WITH ?g ' \
    'DELETE {?s :number_triples ?numbTriples} WHERE {' \
    '?s a :InformationGraph ; :number_triples ?numbTriples}'
