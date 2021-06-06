from dna.database import create_delete_database, query_database
from dna.load import add_narr_data_to_store, clean_text, simplify_text
from dna.utilities import dna_prefix

test_dna = 'test-dna-12345'


def test_create_database():
    # Tests database.py's create_delete_database
    # Will fail if the db already exists, but only need existence
    create_delete_database('create', test_dna)


def test_get_locations():
    # Validates that a list of location names from a set of narratives is complete and correct
    # TODO
    return


def test_get_unknown_words():
    # Tests that the top xx nouns and verbs that are semantically 'unknown' (not accounted for
    # in the ontology) are complete and correct
    # TODO
    return


def test_get_y_x_values():
    # Validates that the gender, birth year and birth country values that are displayed in a
    # histogram are correct
    # TODO
    return


def test_get_years_and_events():
    # Validates that a list of years and event names from a set of narratives is complete and correct
    # TODO
    return


# def test_delete_database():
    # Tests database.py's create_delete_database
    # create_delete_database('delete', test_dna)
    # (Not deleted but maintained for after test review and use in other tests;
    # Duplicate processing should not add new triples)
