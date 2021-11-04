from dna.database import add_remove_data, create_delete_database
from dna.create_metadata_turtle import create_metadata_turtle

from test_dictionaries import metadata_dict1, metadata_dict2
from test_utilities import query_for_triples

test_metadata = 'test-meta'


def test_delete_create_database():
    # Init
    create_delete_database('delete', test_metadata)
    create_delete_database('create', test_metadata)


def test_first_person_metadata():
    # Tests metadata for the first episodic narrative for Erika Eckstut,
    # in Echoes of Memory, Vol 1 ("Teach Love, Not Hate")
    with open(f'resources/Expected-{metadata_dict2["Source"]}', 'r') as revised:
        narrative = revised.read()
    # Get the metadata and compare with what is expected
    gender, family_dict, turtle_list = create_metadata_turtle(narrative.replace('"', "'"), metadata_dict2)
    assert gender == 'FEMALE'
    title = metadata_dict2["Title"]
    add_remove_data('add', ' '.join(turtle_list), test_metadata, f'urn:{title}')
    assert query_for_triples(title, f"resources/{title}_Metadata.csv", test_metadata)


def test_third_person_metadata():
    # Tests metadata for the first timeline narrative for Erika Eckstut, in Echoes of Memory, Vol 1
    with open(f'resources/Expected-{metadata_dict1["Source"]}', 'r') as revised:
        narrative = revised.read()
    # Get the metadata and compare with what is expected
    gender, family_dict, turtle_list = create_metadata_turtle(narrative.replace('"', "'"), metadata_dict1)
    assert gender == 'FEMALE'
    title = metadata_dict1["Title"]
    add_remove_data('add', ' '.join(turtle_list), test_metadata, f'urn:{title}')
    assert query_for_triples(title, f"resources/{title}_Metadata.csv", test_metadata)


def test_narrator_unification():
    # Tests whether narrators are correctly unified based on the domain criteria
    # In this case, the criteria is the narrator's/subject's name
    # TODO
    return
