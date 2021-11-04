from dna.database import add_remove_data, create_delete_database
from dna.create_event_turtle import create_event_turtle
from dna.create_metadata_turtle import create_metadata_turtle
from dna.nlp import parse_narrative

from test_dictionaries import metadata_dict1, metadata_dict2
from test_utilities import query_for_events, query_for_triples

test_events = 'test-events'


def test_delete_create_database():
    # Init
    create_delete_database('delete', test_events)
    create_delete_database('create', test_events)


def test_first_person_events():
    # Tests the events extracted from the first episodic narrative for Erika Eckstut,
    # in Echoes of Memory, Vol 1 ("Teach Love, Not Hate")
    # TODO
    title = metadata_dict2["Title"]
    assert title


def test_first_person_triples():
    # Tests the triples related to events extracted from the first episodic narrative for Erika Eckstut,
    # in Echoes of Memory, Vol 1 ("Teach Love, Not Hate")
    # TODO
    title = metadata_dict2["Title"]
    assert title


def test_third_person_events():
    # Tests the events extracted for the first timeline narrative for Erika Eckstut, in Echoes of Memory, Vol 1
    title = metadata_dict1["Title"]
    with open(f'resources/Expected-{metadata_dict1["Source"]}', 'r') as revised:
        narrative = revised.read()
    gender, family_dict, turtle_list = create_metadata_turtle(narrative, metadata_dict1)
    sentence_dicts = parse_narrative(narrative, gender, family_dict)
    event_turtle_list = create_event_turtle(gender, sentence_dicts)
    add_remove_data('add', ' '.join(event_turtle_list), test_events, f'urn:{title}')
    assert query_for_events(title, f"resources/{title}_Events.csv", test_events)


def test_third_person_triples():
    # Tests the triples related to events extracted for the first timeline narrative for Erika Eckstut,
    # in Echoes of Memory, Vol 1
    title = metadata_dict1["Title"]
    with open(f'resources/Expected-{metadata_dict1["Source"]}', 'r') as revised:
        narrative = revised.read()
    gender, family_dict, turtle_list = create_metadata_turtle(narrative, metadata_dict1)
    sentence_dicts = parse_narrative(narrative, gender, family_dict)
    event_turtle_list = create_event_turtle(gender, sentence_dicts)
    add_remove_data('add', ' '.join(event_turtle_list), test_events, f'urn:{title}')
    assert query_for_triples(title, f"resources/{title}_Triples.csv", test_events)
