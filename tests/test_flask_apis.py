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
        "narrativeMetadata": {
            "title": "A narrative title",
            "published": "2022-07-14T17:32:28Z",
            "source": "Wall Street Journal",
            "url": "http://some-site.com/narrative",
            "length": len(article_text)},
        "narrative": article_text
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
        "narrativeMetadata": {
            "title": "Another Title",
            "published": "2022-07-14T17:32:28Z",
            "source": "New York Times",
            "url": "http://nyt.com/article",
            "length": len("George lived in Detroit in 1980. He moved to Atlanta in 1990.")},
        "narrative": "George lived in Detroit in 1980. He moved to Atlanta in 1990."
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
    assert 'New York Times' in narr_publishers and 'Wall Street Journal' in narr_publishers


def test_narratives_post_missing_all(client):
    resp = client.post('/dna/v1/repositories/narratives')
    assert resp.status_code == 400
    json_data = resp.get_json()
    assert json_data['error'] == 'missing'
    assert 'repository' in json_data['detail']


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


# Get articles using search criteria that are likely to have results
def test_news_get(client):
    yesterday = datetime.now() - timedelta(1)
    resp = client.get('/dna/v1/news', query_string={'topic': 'Trump',
                                                    'fromDate': datetime.strftime(yesterday, '%Y-%m-%d'),
                                                    'toDate': datetime.strftime(yesterday, '%Y-%m-%d')})
    assert resp.status_code == 200
    json_data = resp.get_json()
    assert 'articleCount' in json_data and json_data['articleCount'] > 1
    assert 'articles' in json_data
    article0 = json_data['articles'][0]
    assert 'length' in article0
    assert 'published' in article0
    assert 'source' in article0
    assert 'title' in article0
    assert 'url' in article0


# Post articles using search criteria that are likely to have results
# def test_news_post(client):
#     yesterday = datetime.now() - timedelta(1)
#     resp = client.post('/dna/v1/news',
#                        query_string={'repository': 'foo', 'topic': 'Trump', 'numberToIngest': 1,
#                                      'fromDate': datetime.strftime(yesterday, '%Y-%m-%d'),
#                                      'toDate': datetime.strftime(yesterday, '%Y-%m-%d')})
#     assert resp.status_code == 200
#     json_data = resp.get_json()
    # TODO: Validate


# Get articles using incorrect parameters
def test_news_get_incorrect_parameters(client):
    resp = client.get('/dna/v1/news', query_string={'topic': 'Trump', 'from': '1899-01-01', 'to': '1899-01-01'})
    assert resp.status_code == 400
    json_data = resp.get_json()
    assert 'error' in json_data and json_data['error'] == 'invalid'
    assert json_data['detail'] == 'The query parameters, topic, fromDate and toDate, must all be specified'


# Get articles using invalid from/to
def test_news_get_invalid_dates(client):
    resp = client.get('/dna/v1/news', query_string={'topic': 'Trump', 'fromDate': '1899-01-01', 'toDate': '1899-01-01'})
    assert resp.status_code == 400
    json_data = resp.get_json()
    assert 'error' in json_data and json_data['error'] == 'invalid'
    assert json_data['detail'] == 'The query parameters, fromDate and toDate, must use recent/valid dates ' \
                                  'written as YYYY-mm-dd'


def test_news_post_no_repo(client):
    yesterday = datetime.now() - timedelta(1)
    resp = client.post('/dna/v1/news', query_string={'topic': 'Trump',
                                                     'fromDate': datetime.strftime(yesterday, '%Y-%m-%d'),
                                                     'toDate': datetime.strftime(yesterday, '%Y-%m-%d')})
    assert resp.status_code == 400
    json_data = resp.get_json()
    assert 'error' in json_data and json_data['error'] == 'missing'
    assert json_data['detail'] == 'The argument parameter, repository, is required'


def test_repositories_cleanup(client):
    resp = client.delete('/dna/v1/repositories', query_string={'repository': 'foo'})
    assert resp.status_code == 200
    json_data = resp.get_json()
    assert json_data['deleted'] == 'foo'
