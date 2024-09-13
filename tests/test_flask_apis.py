import json
import pytest
from datetime import datetime, timedelta
from dna.app import app

narrative_ids = []
triples = []
kg_times = []
number_databases = []


@pytest.fixture()
def test_app():
    app.config.update({"TESTING": True})
    yield app


@pytest.fixture()
def client():
    return app.test_client()


def test_remove_last_tests(client):
    client.delete('/dna/v1/repositories', query_string={'repository': 'foo'})
    client.delete('/dna/v1/repositories', query_string={'repository': 'bar'})


# Get initial number of repositories/databases in meta-dna
def test_repositories_get0(client):
    resp = client.get('/dna/v1/repositories')
    assert resp.status_code == 200
    json_data = resp.get_json()
    number_databases.append(len(json_data))


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
    assert json_data['error'] == 'missing'
    assert json_data['detail'] == 'The argument parameter, repository, is required'


def test_repositories_post_dup(client):
    resp = client.post('/dna/v1/repositories', query_string={'repository': 'foo'})
    assert resp.status_code == 409
    json_data = resp.get_json()
    assert 'Repository with the name' in json_data['error']


def test_repositories_get1(client):
    resp = client.get('/dna/v1/repositories')
    assert resp.status_code == 200
    json_data = resp.get_json()
    assert len(json_data) == number_databases[0] + 2
    dbs = []
    for jd in json_data:
        dbs.append(jd['repository'])
    assert 'foo' in dbs and 'bar' in dbs
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
    assert json_data['error'] == 'missing'
    assert json_data['detail'] == 'The argument parameter, repository, is required'


def test_repositories_delete_nonexistent(client):
    resp = client.delete('/dna/v1/repositories', query_string={'repository': 'foobar'})
    assert resp.status_code == 404
    json_data = resp.get_json()
    assert 'Repository with the name' in json_data['error']


def test_repositories_get2(client):
    resp = client.get('/dna/v1/repositories')
    assert resp.status_code == 200
    json_data = resp.get_json()
    assert len(json_data) == number_databases[0] + 1
    dbs = []
    for jd in json_data:
        dbs.append(jd['repository'])
    assert 'foo' in dbs


# dna/v1/repositories/narratives
def test_narratives_post_ok1(client):
    article_text = "John is a musician. When Mary goes to the grocery store, John practices guitar."
    req_data = json.dumps({
        "title": "A narrative title",
        "published": "2022-07-14T17:32:28Z",
        "source": "Wall Street Journal",
        "url": "http://some-site.com/narrative",
        "text": article_text
    })
    resp = client.post('/dna/v1/repositories/narratives', content_type='application/json',
                       query_string={'repository': 'foo'}, data=req_data)
    assert resp.status_code == 201
    json_data = resp.get_json()['narrativeDetails']
    # Will validate encoding in other tests
    assert 'narrativeId' in json_data
    assert 'processed' in json_data
    assert 'numberOfTriples' in json_data
    assert 'narrativeMetadata' in json_data
    assert 'published' in json_data['narrativeMetadata']
    assert 'source' in json_data['narrativeMetadata']
    assert 'title' in json_data['narrativeMetadata']
    narrative_ids.append(json_data['narrativeId'])


def test_narratives_post_ok2(client):
    req_data = json.dumps({
        "title": "Another Title",
        "published": "2022-07-14T17:32:28Z",
        "source": "internal",
        "text": "George lived in Detroit in 1980. He moved to Atlanta in 1990."
    })
    resp = client.post('/dna/v1/repositories/narratives', content_type='application/json',
                       query_string={'repository': 'foo'}, data=req_data)
    assert resp.status_code == 201
    json_data = resp.get_json()['narrativeDetails']
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
    assert 'source' in json_data['narratives'][0]['narrativeMetadata']
    assert 'source' in json_data['narratives'][1]['narrativeMetadata']
    narr_publishers = [json_data['narratives'][0]['narrativeMetadata']['source'],
                       json_data['narratives'][1]['narrativeMetadata']['source']]
    assert 'internal' in narr_publishers and 'Wall Street Journal' in narr_publishers


def test_narratives_post_missing_all(client):
    resp = client.post('/dna/v1/repositories/narratives')
    assert resp.status_code == 400
    json_data = resp.get_json()
    assert json_data['error'] == 'missing'
    assert 'repository' in json_data['detail']


def test_narratives_post_missing_repo(client):
    req_data = json.dumps({
        "published": "2022-07-14T17:32:28Z",
        "source": "internal",
        "title": "Jane's Title",
        "text": "George lived in Detroit in 1980. He moved to Atlanta in 1990."
    })
    resp = client.post('/dna/v1/repositories/narratives', content_type='application/json', data=req_data)
    assert resp.status_code == 400
    json_data = resp.get_json()
    assert json_data['error'] == 'missing'
    assert 'repository' in json_data['detail']


def test_narratives_post_missing_narr(client):
    resp = client.post('/dna/v1/repositories/narratives', query_string={'repository': 'foo'})
    assert resp.status_code == 400
    json_data = resp.get_json()
    assert json_data['error'] == 'missing'
    assert 'request body' in json_data['detail']


def test_narratives_post_invalid_repo(client):
    req_data = json.dumps({
        "published": "2022-07-14T17:32:28Z",
        "source": "internal",
        "title": "Jane's Title",
        "text": "George lived in Detroit in 1980. He moved to Atlanta in 1990."
    })
    resp = client.post('/dna/v1/repositories/narratives', query_string={'repository': 'foobar'},
                       content_type='application/json', data=req_data)
    assert resp.status_code == 404
    json_data = resp.get_json()
    assert 'Repository with the name' in json_data['error']


def test_narratives_post_no_text(client):
    req_data = json.dumps({
        "published": "2022-07-14T17:32:28Z",
        "source": "internal",
        "title": "Jane's Title"
    })
    resp = client.post('/dna/v1/repositories/narratives', query_string={'repository': 'foo'},
                       content_type='application/json', data=req_data)
    assert resp.status_code == 400
    json_data = resp.get_json()
    assert json_data['error'] == 'missing'
    assert 'A "title"' in json_data['detail']


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
    assert json_data['error'] == 'missing'
    assert 'repository' in json_data['detail']


def test_narratives_delete_missing_repo(client):
    resp = client.delete('/dna/v1/repositories/narratives',
                         query_string={'narrativeId': narrative_ids[0]})
    assert resp.status_code == 400
    json_data = resp.get_json()
    assert json_data['error'] == 'missing'
    assert 'repository' in json_data['detail']


def test_narratives_delete_missing_narr(client):
    resp = client.delete('/dna/v1/repositories/narratives', query_string={'repository': 'foo'})
    assert resp.status_code == 400
    json_data = resp.get_json()
    assert json_data['error'] == 'missing'
    assert 'narrativeId' in json_data['detail']


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


def test_end_to_end(client):
    req_data = json.dumps(
        {'title': 'UN Security Council demands immediate Gaza ceasefire as US abstains',
         'published': '2024-03-25T00:00:00',
         'source': 'Al Jazeera',
         'url': 'https://www.aljazeera.com/news/2024/3/25/un-security-council-adopts-resolution',
         'text': 'The United Nations Security Council (UNSC) demands an immediate ceasefire between Israel and the '
                 'Palestinian group Hamas in the Gaza Strip and the release of all hostages as the United States '
                 'abstains from the vote.\n\nThe remaining 14 council members voted in favour of the resolution, '
                 'which was proposed by the 10 elected members of the council. There was a round of applause in the '
                 'council chamber after the vote on Monday.\n\nThe resolution calls for an immediate ceasefire for '
                 'the Muslim fasting month of Ramadan, which ends in two weeks, and also demands the release of all '
                 'hostages seized in the Hamas-led attack on southern Israel on October 7.'})
    resp = client.post('/dna/v1/repositories/narratives', content_type='application/json',
                       query_string={'repository': 'foo'},
                       data=req_data)
    assert resp.status_code == 201
    json_data = resp.get_json()
    assert 'repository' in json_data
    assert 'narrativeDetails' in json_data


def test_repositories_cleanup(client):
    resp = client.delete('/dna/v1/repositories', query_string={'repository': 'foo'})
    assert resp.status_code == 200
    json_data = resp.get_json()
    assert json_data['deleted'] == 'foo'
