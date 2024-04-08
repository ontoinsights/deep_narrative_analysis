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
    with open('resources/fl_abortion_fox.txt', 'r') as fox:
        article = fox.read()
    req_data = json.dumps(
        {"title": "FL abortion Fox",
         "published": "2024-03-25T00:00:00",
         "source": "Fox News",
         "url": "https://www.fox.com/news/2024/3/25/xyz",
         "text": article})
    resp = client.post('/dna/v1/repositories/narratives', content_type='application/json',
                       query_string={'repository': 'foo', 'sentences': 10}, data=req_data)
    print(resp.status_code)
    print(resp.get_json())


def test_repositories_cleanup(client):
    resp = client.delete('/dna/v1/repositories', query_string={'repository': 'foo'})
    assert resp.status_code == 200
    json_data = resp.get_json()
    assert json_data['deleted'] == 'foo'
