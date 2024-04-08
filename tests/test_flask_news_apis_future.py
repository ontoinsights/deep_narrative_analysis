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
    assert 'published' in article0
    assert 'source' in article0
    assert 'title' in article0
    assert 'url' in article0


# Post articles using search criteria that are likely to have results
# def test_news_post(client):
#    yesterday = datetime.now() - timedelta(1)
#    resp = client.post('/dna/v1/news',
#                       query_string={'repository': 'foo', 'topic': 'Trump', 'numberToIngest': 1,
#                                     'fromDate': datetime.strftime(yesterday, '%Y-%m-%d'),
#                                     'toDate': datetime.strftime(yesterday, '%Y-%m-%d')})
#    assert resp.status_code == 200
#    json_data = resp.get_json()     TODO: Validate


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
