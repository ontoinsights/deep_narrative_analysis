import json
import pytest
from datetime import datetime, timedelta
from dna.app import app
from dna.app_functions import get_metadata_ttl


@pytest.fixture()
def test_app():
    app.config.update({"TESTING": True})
    yield app


@pytest.fixture()
def client():
    return app.test_client()


def test_foo_repository(client):
    client.post('/dna/v1/repositories', query_string={'repository': 'foo'})


def test_ingest(client):
    with open('resources/ceasefire_fox.txt', 'r') as fox:
        article = fox.read()
    req_data = json.dumps(
        {"title": "Ceasefire Fox",
         "published": "2024-03-25T00:00:00",
         "source": "Fox News",
         "url": "https://www.fox.com/news/2024/3/25/xyz",
         "text": article})
    resp = client.post('/dna/v1/repositories/narratives', content_type='application/json',
                       query_string={'repository': 'foo', 'sentences': 5}, data=req_data)
    assert resp.status_code == 201
    json_data = resp.get_json()
    assert 'narrativeDetails' in json_data
    narr_details = json_data['narrativeDetails']
    assert 'narrativeId' in narr_details
    assert 'processed' in narr_details
    # assert narr_details['numberIngested'] == 5   # TODO: Full processing only up to the requested # of sentences (5)
    assert narr_details['numberOfSentences'] > 10
    assert narr_details['numberOfTriples'] > 100
    narr_meta = narr_details['narrativeMetadata']
    assert narr_meta['published'] == '2024-03-25T00:00:00'
    assert narr_meta['source'] == 'Fox News'
    assert narr_meta['title'] == 'Ceasefire Fox'
    assert narr_meta['url'] == 'https://www.fox.com/news/2024/3/25/xyz'


def test_repositories_cleanup(client):
    resp = client.delete('/dna/v1/repositories', query_string={'repository': 'foo'})
    assert resp.status_code == 200
    json_data = resp.get_json()
    assert json_data['deleted'] == 'foo'
