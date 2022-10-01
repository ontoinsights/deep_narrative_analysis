import json
import pytest
from dna.app import app

narrative_ids = []
triples = []
kg_times = []


@pytest.fixture()
def test_app():
    app.config.update({"TESTING": True})
    yield app


@pytest.fixture()
def client():
    return app.test_client()


# dna/v1/repositories
def test_repositories_post_ok1(client):
    resp = client.post('/dna/v1/repositories', query_string={'repository': 'foo'})
    assert resp.status_code == 201
    json_data = resp.get_json()
    assert json_data['created'] == 'foo'


def test_repositories_post_ok2(client):
    resp = client.post('/dna/v1/repositories', query_string={'repository': 'bar'})
    assert resp.status_code == 201
    json_data = resp.get_json()
    assert json_data['created'] == 'bar'


def test_repositories_post_missing_repo(client):
    resp = client.post('/dna/v1/repositories')
    assert resp.status_code == 400
    json_data = resp.get_json()
    assert json_data['missing'][0] == 'repository'


def test_repositories_post_dup(client):
    resp = client.post('/dna/v1/repositories', query_string={'repository': 'foo'})
    assert resp.status_code == 409
    json_data = resp.get_json()
    assert 'Repository with the name' in json_data['error']


def test_repositories_get1(client):
    resp = client.get('/dna/v1/repositories')
    assert resp.status_code == 200
    json_data = resp.get_json()
    assert len(json_data) == 2
    dbs = [json_data[0]['repository'], json_data[1]['repository']]
    assert 'urn:ontoinsights:dna:foo' in dbs and 'urn:ontoinsights:dna:bar' in dbs
    assert 'created' in json_data[0] and 'created' in json_data[1]


def test_repositories_delete(client):
    resp = client.delete('/dna/v1/repositories', query_string={'repository': 'bar'})
    assert resp.status_code == 200
    json_data = resp.get_json()
    assert json_data['deleted'] == 'bar'


def test_repositories_delete_missing_param(client):
    resp = client.delete('/dna/v1/repositories')
    assert resp.status_code == 400
    json_data = resp.get_json()
    assert json_data['missing'][0] == 'repository'


def test_repositories_delete_nonexistent(client):
    resp = client.delete('/dna/v1/repositories', query_string={'repository': 'foobar'})
    assert resp.status_code == 404
    json_data = resp.get_json()
    assert 'Repository with the name' in json_data['error']


def test_repositories_get2(client):
    resp = client.get('/dna/v1/repositories')
    assert resp.status_code == 200
    json_data = resp.get_json()
    assert len(json_data) == 1
    assert json_data[0]['repository'] == 'urn:ontoinsights:dna:foo'


# dna/v1/repositories/narratives
def test_narratives_post_ok1(client):
    req_data = json.dumps({
        "narrativeMetadata": {
            "author": "John Smith",
            "published": "2022-07-14T17:32:28Z",
            "publisher": "Wall Street Journal",
            "source": "Identifier_such_as_URL",
            "title": "John's Title"},
        "narrative": "When Mary went to the grocery store, John practiced guitar."
    })
    resp = client.post('/dna/v1/repositories/narratives', content_type='application/json',
                       query_string={'repository': 'foo'}, data=req_data)
    assert resp.status_code == 201
    json_data = resp.get_json()
    # Will validate encoding in other tests
    assert 'narrativeId' in json_data
    assert 'processed' in json_data
    assert 'numberOfTriples' in json_data
    assert 'narrativeMetadata' in json_data
    assert 'author' in json_data['narrativeMetadata']
    assert 'published' in json_data['narrativeMetadata']
    assert 'publisher' in json_data['narrativeMetadata']
    assert 'source' in json_data['narrativeMetadata']
    assert 'title' in json_data['narrativeMetadata']
    narrative_ids.append(json_data['narrativeId'])


def test_narratives_post_ok2(client):
    req_data = json.dumps({
        "narrativeMetadata": {
            "author": "Jane Doe",
            "published": "2022-07-14T17:32:28Z",
            "publisher": "New York Times",
            "source": "Identifier_such_as_URL",
            "title": "Jane's Title"},
        "narrative": "George lived in Detroit in 1980. He moved to Atlanta in 1990."
    })
    resp = client.post('/dna/v1/repositories/narratives', content_type='application/json',
                       query_string={'repository': 'foo'}, data=req_data)
    assert resp.status_code == 201
    json_data = resp.get_json()
    assert 'narrativeId' in json_data
    narrative_ids.append(json_data['narrativeId'])


def test_narratives_get1(client):
    resp = client.get('/dna/v1/repositories/narratives', query_string={'repository': 'foo'})
    assert resp.status_code == 200
    json_data = resp.get_json()
    assert 'repository' in json_data
    assert json_data['repository'] == 'foo'
    assert 'narratives' in json_data
    assert len(json_data['narratives']) == 2
    assert 'publisher' in json_data['narratives'][0]['narrativeMetadata']
    assert 'publisher' in json_data['narratives'][1]['narrativeMetadata']
    narr_publishers = [json_data['narratives'][0]['narrativeMetadata']['publisher'],
                       json_data['narratives'][1]['narrativeMetadata']['publisher']]
    assert 'New York Times' in narr_publishers and 'Wall Street Journal' in narr_publishers


def test_narratives_post_missing_all(client):
    resp = client.post('/dna/v1/repositories/narratives')
    assert resp.status_code == 400
    json_data = resp.get_json()
    assert json_data['missing'][0] == 'repository'


def test_narratives_post_missing_repo(client):
    req_data = json.dumps({
        "narrativeMetadata": {
            "author": "Jane Doe",
            "published": "2022-07-14T17:32:28Z",
            "publisher": "New York Times",
            "source": "Identifier_such_as_URL",
            "title": "Jane's Title"},
        "narrative": "George lived in Detroit in 1980. He moved to Atlanta in 1990."
    })
    resp = client.post('/dna/v1/repositories/narratives', content_type='application/json', data=req_data)
    assert resp.status_code == 400
    json_data = resp.get_json()
    assert json_data['missing'][0] == 'repository'


def test_narratives_post_missing_narr(client):
    resp = client.post('/dna/v1/repositories/narratives', query_string={'repository': 'foo'})
    assert resp.status_code == 400
    json_data = resp.get_json()
    assert json_data['missing'][0] == 'narrativeText'


def test_narratives_post_invalid_sources(client):
    resp = client.post('/dna/v1/repositories/narratives', query_string={'repository': 'foo', 'extSources': 123})
    assert resp.status_code == 500
    json_data = resp.get_json()
    assert 'extSources and/or timelinePossible must be set' in json_data['error']


def test_narratives_post_invalid_timeline(client):
    resp = client.post('/dna/v1/repositories/narratives', query_string={'repository': 'foo', 'timelinePossible': 123})
    assert resp.status_code == 500
    json_data = resp.get_json()
    assert 'extSources and/or timelinePossible must be set' in json_data['error']


def test_narratives_post_invalid_repo(client):
    req_data = json.dumps({
        "narrativeMetadata": {
            "author": "Jane Doe",
            "published": "2022-07-14T17:32:28Z",
            "publisher": "New York Times",
            "source": "Identifier_such_as_URL",
            "title": "Jane's Title"},
        "narrative": "George lived in Detroit in 1980. He moved to Atlanta in 1990."
    })
    resp = client.post('/dna/v1/repositories/narratives', query_string={'repository': 'foobar'},
                       content_type='application/json', data=req_data)
    assert resp.status_code == 404
    json_data = resp.get_json()
    assert 'Repository with the name' in json_data['error']


def test_narratives_delete(client):
    resp = client.delete('/dna/v1/repositories/narratives',
                         query_string={'repository': 'foo', 'narrativeId': narrative_ids[1]})
    assert resp.status_code == 200
    json_data = resp.get_json()
    assert json_data['repository'] == 'foo'
    assert json_data['deleted'] == narrative_ids[1]


def test_narratives_delete_missing_all(client):
    resp = client.delete('/dna/v1/repositories/narratives')
    assert resp.status_code == 400
    json_data = resp.get_json()
    missing = json_data['missing']
    assert 'repository' in missing and 'narrativeId' in missing


def test_narratives_delete_missing_repo(client):
    resp = client.delete('/dna/v1/repositories/narratives',
                         query_string={'narrativeId': narrative_ids[0]})
    assert resp.status_code == 400
    json_data = resp.get_json()
    assert json_data['missing'][0] == 'repository'


def test_narratives_delete_missing_narr(client):
    resp = client.delete('/dna/v1/repositories/narratives', query_string={'repository': 'foo'})
    assert resp.status_code == 400
    json_data = resp.get_json()
    assert json_data['missing'][0] == 'narrativeId'


def test_narratives_delete_nonexistent_repo(client):
    resp = client.delete('/dna/v1/repositories/narratives',
                         query_string={'repository': 'foobar', 'narrativeId': narrative_ids[0]})
    assert resp.status_code == 404
    json_data = resp.get_json()
    assert 'Repository with the name' in json_data['error']


def test_narratives_delete_nonexistent_narr(client):
    resp = client.delete('/dna/v1/repositories/narratives',
                         query_string={'repository': 'foo', 'narrativeId': '123'})
    assert resp.status_code == 404
    json_data = resp.get_json()
    assert 'Narrative with the id' in json_data['error']


def test_narratives_get2(client):
    resp = client.get('/dna/v1/repositories/narratives', query_string={'repository': 'foo'})
    assert resp.status_code == 200
    json_data = resp.get_json()
    assert 'narratives' in json_data
    assert len(json_data['narratives']) == 1


# dna/v1/repositories/narratives/graphs
def test_graphs_get(client):
    resp = client.get('/dna/v1/repositories/narratives/graphs',
                      query_string={'repository': 'foo', 'narrativeId': narrative_ids[0]})
    assert resp.status_code == 200
    json_data = resp.get_json()
    assert 'repository' in json_data
    assert 'narrativeDetails' in json_data
    kg_times.append(json_data['narrativeDetails']['processed'])
    assert 'triples' in json_data
    triples.extend(json_data['triples'])
    assert len(triples) > 1


def test_graphs_put(client):
    req_data = json.dumps({'triples': triples})
    resp = client.put('/dna/v1/repositories/narratives/graphs', content_type='application/json',
                      query_string={'repository': 'foo', 'narrativeId': narrative_ids[0]},
                      data=req_data)
    assert resp.status_code == 200
    json_data = resp.get_json()
    assert 'repository' in json_data
    assert 'processed' in json_data
    assert json_data['processed'] != kg_times[0]
    assert 'numberOfTriples' in json_data


def test_graphs_put_bad_triples(client):
    req_data = json.dumps({'triples': ['subject rdfs:label "bar" .']})
    resp = client.put('/dna/v1/repositories/narratives/graphs', content_type='application/json',
                      query_string={'repository': 'foo', 'narrativeId': narrative_ids[0]},
                      data=req_data)
    assert resp.status_code == 500
    json_data = resp.get_json()
    assert 'error' in json_data
    assert "Invalid triples" in json_data['error']


def test_repositories_cleanup(client):
    resp = client.delete('/dna/v1/repositories', query_string={'repository': 'foo'})
    assert resp.status_code == 200
    json_data = resp.get_json()
    assert json_data['deleted'] == 'foo'
