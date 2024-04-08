import pytest
import os
from database import datetime

from dna.database import add_remove_data, clear_data, construct_graph, query_database
from dna.database_queries import construct_kg, delete_repo_metadata, query_repo_graphs
from dna.utilities_and_language_specific import dna_prefix, empty_string

test_repo = 'test-repo'
test_graph = 'testGraph'
full_test_graph = f'<{dna_prefix}{test_repo}_{test_graph}>'
triples = ':testS :testP :testO ; rdfs:label "text" .'
class_triples = '@prefix dna: <urn:ontoinsights:dna:> :testS a dna:EventAndState ; rdfs:label "text" .'
query = 'select (count(*) as ?cnt) where { GRAPH ?g {?s ?p ?o} }'
graph_query = query.replace('?g', full_test_graph)

# Get environment variables
sd_conn_details = {'endpoint': os.environ.get('STARDOG_ENDPOINT'),
                   'username': os.getenv('STARDOG_USER'),
                   'password': os.environ.get('STARDOG_PASSWORD')}


def test_remove_last_tests():
    # Delete metadata for the repository in dna db's default graph
    query_database('update', delete_repo_metadata.replace('?repo', f':{test_repo}'), empty_string)
    # Delete all the named graphs for the repository
    graph_bindings = query_database('select', query_repo_graphs.replace('?repo', test_repo), empty_string)
    if graph_bindings and 'exception' not in graph_bindings[0]:
        for binding in graph_bindings:
            # Delete the graph
            clear_data(repo, binding['g']['value'].split(f'{repo}_')[1])


def test_create_repo():
    # Delete metadata for the repository in dna db's default graph
    query_database('update', delete_repo_metadata.replace('?repo', f':{test_repo}'), empty_string)
    created_at = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    repo_triples = f'@prefix : <{dna_prefix}> . @prefix dc: <http://purl.org/dc/terms/> . ' \
                   f':{test_repo} a :Database ; dc:created "{created_at}"^^xsd:dateTime .'
    triples_msg = add_remove_data('add', repo_triples, empty_string)   # Add triples to dna db, default graph
    assert not triples_msg


def test_add_data():
    org_results = query_database('select', graph_query, test_repo)
    print(org_results)
    org_cnt = int(org_results[0]['cnt']['value'])
    add_remove_data('add', triples, test_repo, test_graph)
    new_results = query_database('select', graph_query, test_repo)
    new_cnt = int(new_results[0]['cnt']['value'])
    assert new_cnt - org_cnt == 2


def test_construct():
    success, turtle = construct_graph(construct_kg.replace('?g', f':{test_repo}_{test_graph}'), test_repo)
    assert success
    print(turtle)
    assert len(turtle) == 2
    triples_str = str(turtle)
    assert 'testS' in triples_str
    assert 'testP' in triples_str
    assert 'testO' in triples_str
    assert '"text"' in triples_str


def test_remove_data():
    org_results = query_database('select', graph_query, test_repo)
    print(org_results)
    org_cnt = int(org_results[0]['cnt']['value'])
    add_remove_data('remove', triples, test_repo, test_graph)
    new_results = query_database('select', graph_query, test_repo)
    new_cnt = int(new_results[0]['cnt']['value'])
    assert new_cnt - org_cnt == -2


def test_clear_data_from_graph():
    add_remove_data('add', triples, test_repo, test_graph)
    org_results = query_database('select', graph_query, test_repo)
    org_cnt = int(org_results[0]['cnt']['value'])
    assert org_cnt == 2
    clear_data(test_repo, test_graph)
    new_results = query_database('select', graph_query, test_repo)
    new_cnt = int(new_results[0]['cnt']['value'])
    assert new_cnt == 0


def test_delete_repo():
    # Delete metadata for the repository in dna db's default graph
    query_database('update', delete_repo_metadata.replace('?repo', f':{test_repo}'), test_repo)
    # Delete all the named graphs for the repository
    graph_bindings = query_database('select', query_repo_graphs.replace('?repo', test_repo), test_repo)
    assert not graph_bindings
    for binding in graph_bindings:
        assert test_repo in binding['g']['value']
        # Delete the graph
        clear_data(repo, binding['g']['value'].split(f'{repo}_')[1])
    # Validate deletion of all the named graphs for the repository
    graph_bindings = query_database('select', query_repo_graphs.replace('?repo', test_repo), test_repo)
    assert not graph_bindings


def test_remove_tests():
    # Delete metadata for the repository in dna db's default graph
    query_database('update', delete_repo_metadata.replace('?repo', f':{test_repo}'), empty_string)
    # Delete all the named graphs for the repository
    graph_bindings = query_database('select', query_repo_graphs.replace('?repo', test_repo), empty_string)
    if graph_bindings and 'exception' not in graph_bindings[0]:
        for binding in graph_bindings:
            # Delete the graph
            clear_data(repo, binding['g']['value'].split(f'{repo}_')[1])
