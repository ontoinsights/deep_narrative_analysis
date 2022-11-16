from dna.database import add_remove_data, clear_data, construct_database, create_delete_database, \
    query_class, query_database
from dna.get_ontology_mapping import query_exact_and_approx_match
from dna.queries import construct_kg, query_event, query_noun

test_db = 'test-dna-db'
full_test_graph = 'urn:ontoinsights:dna:testGraph'
test_graph = 'testGraph'
triples = ':testS :testP :testO ; rdfs:label "text" .'
class_triples = '@prefix dna: <urn:ontoinsights:dna:> :testS a dna:EventAndState ; rdfs:label "text" .'
query = 'select (count(*) as ?cnt) where {?s ?p ?o}'
graph_query = query.replace('where', f'from <{full_test_graph}> where')


def test_create_database():
    create_delete_database('delete', test_db)
    result = create_delete_database('create', test_db)
    assert f'Database, {test_db}, created' in result


def test_add_data():
    org_results = query_database('select', query, test_db)
    org_cnt = int(org_results[0]['cnt']['value'])
    add_remove_data('add', triples, test_db)
    new_results = query_database('select', query, test_db)
    new_cnt = int(new_results[0]['cnt']['value'])
    assert new_cnt - org_cnt == 2


def test_remove_data():
    org_results = query_database('select', query, test_db)
    org_cnt = int(org_results[0]['cnt']['value'])
    add_remove_data('remove', triples, test_db)
    new_results = query_database('select', query, test_db)
    new_cnt = int(new_results[0]['cnt']['value'])
    assert new_cnt - org_cnt == -2


def test_add_data_to_graph():
    msg = add_remove_data('add', triples, test_db, full_test_graph)
    if not msg:
        results = query_database('select', graph_query, test_db)
        new_cnt = int(results[0]['cnt']['value'])
        assert new_cnt == 2
    else:
        assert False


def test_construct():
    success, turtle = construct_database(construct_kg.replace(':graph_uuid', f'<{full_test_graph}>'), test_db)
    assert success
    assert len(turtle) == 2
    triples_str = str(turtle)
    assert 'testS' in triples_str
    assert 'testP' in triples_str
    assert 'testO' in triples_str
    assert '"text"' in triples_str


def test_remove_data_from_graph():
    add_remove_data('remove', triples, test_db, full_test_graph)
    results = query_database('select', graph_query, test_db)
    new_cnt = int(results[0]['cnt']['value'])
    assert new_cnt == 0


def test_clear_data_from_graph():
    add_remove_data('add', triples, test_db, full_test_graph)
    org_results = query_database('select', graph_query, test_db)
    org_cnt = int(org_results[0]['cnt']['value'])
    assert org_cnt == 2
    clear_data(test_db, full_test_graph)
    new_results = query_database('select', graph_query, test_db)
    new_cnt = int(new_results[0]['cnt']['value'])
    assert new_cnt == 0


def test_query_class():
    result = query_class('permit', query_event)
    assert 'Permission' in result


def test_query_exact_and_approx_match():
    result = query_exact_and_approx_match('raw material', query_noun)
    assert 'RawMaterial' in result


def test_delete_database():
    result = create_delete_database('delete', test_db)
    assert f'Database, {test_db}, deleted' in result
