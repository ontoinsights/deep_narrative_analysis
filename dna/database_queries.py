# Various SPARQL queries used in DNA processing

from dna.utilities_and_language_specific import dna_prefix

construct_kg = 'prefix : <urn:ontoinsights:dna:> prefix dc: <http://purl.org/dc/terms/> ' \
               'CONSTRUCT {?s ?p ?o} WHERE {graph ?named {?s ?p ?o}}'

count_triples = 'prefix : <urn:ontoinsights:dna:> SELECT (COUNT(*) as ?cnt) WHERE { GRAPH ?g {?s ?p ?o} }'

delete_entity = 'prefix : <urn:ontoinsights:dna:> WITH ?named ' \
                'DELETE {?s ?p ?o} WHERE {?s a :Background ; :text "?text_name" ; ?p ?o}'

delete_narrative = 'prefix : <urn:ontoinsights:dna:> WITH ?named ' \
                   'DELETE {:narr_id ?graph_p ?graph_o . :Narrative_narr_id ?narr_p ?narr_o} ' \
                   'WHERE {:narr_id ?graph_p ?graph_o . :Narrative_narr_id ?narr_p ?narr_o}'

delete_repo_metadata = 'prefix : <urn:ontoinsights:dna:> prefix dc: <http://purl.org/dc/terms/> ' \
                       'DELETE {?repo a :Database ; dc:created ?created} ' \
                       'WHERE {?repo a :Database ; dc:created ?created}'

query_background = 'prefix : <urn:ontoinsights:dna:> SELECT ?name ?type ?plural WHERE { GRAPH ?named { ' \
                   '?s a :Background; :text ?name . OPTIONAL {?s a :Collection. BIND(true as ?plural)} ' \
                   '{{?s a :Person . BIND("person" as ?type)} UNION {?s a :Resource . BIND("thing" as ?type)} ' \
                   'UNION {?s a :OrganizationalEntity . BIND("organization" as ?type)} UNION ' \
                   '{{{?s a :GeoPoliticalEntity} UNION {?s a :Location}}. BIND("place" as ?type)} UNION ' \
                   '{?s a :LawAndPolicy . BIND("law" as ?type)}} }}'

query_corrections = \
    'prefix : <urn:ontoinsights:dna:> SELECT * WHERE { GRAPH ?named {?s a :Correction; a ?type ; rdfs:label ?label}}'

query_manual_corrections = \
    'prefix : <urn:ontoinsights:dna:> SELECT * WHERE {?s a :Correction; a ?type ; rdfs:label ?label}'

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
