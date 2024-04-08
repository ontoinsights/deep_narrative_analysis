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
    req_data = \
        {'title': 'UN Security Council demands immediate Gaza ceasefire as US abstains',
         'published': '2024-03-25T00:00:00',
         'source': 'Al Jazeera',
         'url': 'https://www.aljazeera.com/news/2024/3/25/un-security-council-adopts-resolution',
         'text': 'The United Nations Security Council (UNSC) demands an immediate ceasefire between Israel and the Palestinian group Hamas in the Gaza Strip and the release of all hostages as the United States abstains from the vote.\n\nThe remaining 14 council members voted in favour of the resolution, which was proposed by the 10 elected members of the council. There was a round of applause in the council chamber after the vote on Monday.\n\nThe resolution calls for an immediate ceasefire for the Muslim fasting month of Ramadan, which ends in two weeks, and also demands the release of all hostages seized in the Hamas-led attack on southern Israel on October 7.\n\n“The bloodbath has continued for far too long,” said Amar Bendjama, the ambassador from Algeria, the Arab bloc’s current Security Council member and a sponsor of the resolution. “Finally, the Security Council is shouldering its responsibility.”\n\nThe US had repeatedly blocked Security Council resolutions that put pressure on Israel but has increasingly shown frustration with its ally as civilian casualties mount and the UN warns of impending famine in Gaza.\n\nSpeaking after the vote, US Ambassador Linda Thomas-Greenfield blamed Hamas for the delay in passing a ceasefire resolution.\n\n“We did not agree with everything with the resolution,” which she said was the reason why the US abstained.\n\n“Certain key edits were ignored, including our request to add a condemnation of Hamas,” Thomas-Greenfield said. She stressed that the release of Israeli captives would lead to an increase in humanitarian aid supplies going into the besieged coastal enclave.\n\nThe White House said the final resolution did not have language the US considers essential and its abstention does not represent a shift in policy.\n\nBut Israeli Prime Minister Benjamin Netanyahu’s office said the US failure to veto the resolution is a “clear retreat” from its previous position and would hurt war efforts against Hamas as well as efforts to release Israeli captives held in Gaza.\n\nHis office also said Netanyahu will not be sending a high-level delegation to Washington, DC, in light of the new US position.\n\nUS President Joe Biden had requested to meet Israeli officials to discuss Israeli plans for a ground invasion of Rafah in southern Gaza, where more than 1 million displaced Palestinians are sheltering.\n\nWhite House spokesperson John Kirby said the US was “disappointed” by Netanyahu’s decision.\n\n“We’re very disappointed that they won’t be coming to Washington, DC, to allow us to have a fulsome conversation with them about viable alternatives to them going in on the ground in Rafah,” Kirby told reporters.\n\nHe said senior US officials would still meet for separate talks with Israeli Defence Minister Yoav Gallant, who is currently in Washington, on issues including the captives, humanitarian aid and protecting civilians in Rafah.\n\nLast week, Netanyahu promised to defy US appeals and expand Israel’s military campaign to Rafah even without its ally’s support.\n\nAl Jazeera’s diplomatic editor James Bays said the vote is still a “very, very significant” development.\n\n“After almost six months, … the vote, almost unanimous,” has demanded a lasting and immediate ceasefire in Gaza.\n\n“The US has used its veto three times,” Bays said. “This time, the US let this pass.”\n\n“Resolutions of the Security Council are international law. They are always seen as binding on all the member states of the United Nations,” he added.\n\nUN Secretary-General Antonio Guterres said in a post on X that the resolution “must be implemented”, adding that “failure would be unforgivable”.\n\nThe vote came amid international calls to bring the nearly six-month-long conflict to an end as Israeli forces pummel Gaza and humanitarian conditions in the besieged strip reach critical levels.\n\nMore than 90 percent of Gaza’s 2.3 million residents have been displaced, and conditions under Israeli siege and bombardment have pushed Gaza to the brink of famine, the UN said.\n\nMore than 32,000 Palestinians have been killed in the Israeli assault since October 7, mostly women and children, according to Palestinian health authorities.\n\nIsrael began its military offensive in Gaza after Hamas led an attack on southern Israel on October 7, killing at least 1,139 people, mostly civilians, and seizing about 250 others as hostages, according to Israeli tallies.\n\nPalestinian leaders welcomed the adoption of the resolution, saying it was a step in the right direction.\n\n“This must be a turning point,” Palestinian Ambassador Riyad Mansour told the UNSC, holding back tears. “This must signal the end of this assault, of atrocities against our people.”\n\nIn a statement, the Palestinian Ministry of Foreign Affairs called on UNSC member states to fulfill their legal responsibilities to implement the resolution immediately.\n\nThe ministry also stressed the importance of intensifying efforts to achieve a permanent ceasefire that extends beyond Ramadan, secure the entry of aid, work on the release Palestinian prisoners held in Israeli jails and prevent forced displacement of Palestinians.\n\nHamas welcomed the resolution and said in a statement it “affirms readiness to engage in immediate prisoner swaps on both sides”.\n\nFrance called for more work on securing a permanent ceasefire between Israel and Hamas.\n\n“This crisis is not over. Our council will have to remain mobilised and immediately get back to work. After Ramadan, which ends in two weeks, it will have to establish a permanent ceasefire,” French Ambassador Nicolas de Riviere said.\n\nThe latest vote was held after Russia and China vetoed a US-sponsored resolution on Friday that would have supported “an immediate and sustained ceasefire”.\n\nRussian Ambassador Vasily Alekseyevich Nebenzya said his country hopes Monday’s resolution will be used in the “interests of peace” rather than advancing the “inhumane Israeli operation against Palestinians”.\n\n“It is of fundamental importance that the UN Security Council, for the first time, is demanding the parties observe an immediate ceasefire, even if it is limited to the month of Ramadan,” he said. “Unfortunately, what happens after that ends remains unclear.”\n\nRussia tried to push for the use of the word “permanent” in regards to the ceasefire. It had complained that dropping the word could allow Israel “to resume its military operation in the Gaza Strip at any moment” after Ramadan, which ends on April 9.\n\n“We are disappointed that it did not make it through,” Nebenzya said.\n'}
    resp = client.post('v1/repositories/narratives', content_type='application/json',
                       query_string={'repository': 'foo'},
                       data=req_data)


def test_repositories_cleanup(client):
    resp = client.delete('/dna/v1/repositories', query_string={'repository': 'foo'})
    assert resp.status_code == 200
    json_data = resp.get_json()
    assert json_data['deleted'] == 'foo'
