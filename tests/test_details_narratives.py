from dna.database import create_delete_database, query_database
from dna.load import add_narr_data_to_store, clean_text, simplify_text
from dna.utilities import dna_prefix

test_dna = 'test-dna-12345'


def test_create_database():
    # Tests database.py's create_delete_database
    # Will fail if the db already exists, but only need existence
    create_delete_database('create', test_dna)


def test_get_timeline_data():
    # Validates that the results of extracting events from a narrative are complete and correct
    # TODO
    return


# def test_delete_database():
    # Tests database.py's create_delete_database
    # create_delete_database('delete', test_dna)
    # (Not deleted but maintained for after test review and use in other tests;
    # Duplicate processing should not add new triples)
