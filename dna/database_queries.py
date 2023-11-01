# Various SPARQL queries used in DNA processing

construct_kg = 'prefix : <urn:ontoinsights:dna:> prefix dc: <http://purl.org/dc/terms/> ' \
               'CONSTRUCT {?s ?p ?o} WHERE { GRAPH ?graph {?s ?p ?o} } ORDER BY ?s ?p ?o'

count_triples = 'prefix : <urn:ontoinsights:dna:> SELECT (COUNT(*) as ?cnt) WHERE { GRAPH ?g {?s ?p ?o} }'

delete_db_metadata = 'prefix : <urn:ontoinsights:dna:> prefix dc: <http://purl.org/dc/terms/> ' \
                     'DELETE {?db a :Database ; dc:created ?created} WHERE {?db a :Database ; dc:created ?created}'

delete_entity = 'prefix : <urn:ontoinsights:dna:> DELETE {?s ?p ?o} WHERE {?s ?p ?o}'

delete_narrative = 'prefix : <urn:ontoinsights:dna:> ' \
                   'DELETE {:narr_id ?graph_p ?graph_o . :Narrative_narr_id ?narr_p ?narr_o} ' \
                   'WHERE {:narr_id ?graph_p ?graph_o . :Narrative_narr_id ?narr_p ?narr_o}'

query_dbs = 'prefix : <urn:ontoinsights:dna:> prefix dc: <http://purl.org/dc/terms/> ' \
            'SELECT * WHERE {?db a :Database ; dc:created ?created}'

query_graphs = 'prefix : <urn:ontoinsights:dna:> prefix dc: <http://purl.org/dc/terms/> ' \
               'SELECT * WHERE {?graph a :InformationGraph ; dc:created ?created}'

query_narratives = \
    'prefix : <urn:ontoinsights:dna:> prefix dc: <http://purl.org/dc/terms/> SELECT * WHERE { ' \
    '?graph a :InformationGraph ; dc:created ?created ; :number_triples ?numbTriples ; :encodes ?narrative . ' \
    '?narrative :source ?source ; :external_link ?url ; dc:title ?title ; :number_characters ?length . ' \
    'OPTIONAL {?narrative dc:created ?published} }'

update_narrative = \
    'prefix : <urn:ontoinsights:dna:> prefix dc: <http://purl.org/dc/terms/> ' \
    'DELETE {?s dc:created ?created ; :number_triples ?numbTriples} WHERE {' \
    '?s a :InformationGraph ; dc:created ?created ; :number_triples ?numbTriples}'
