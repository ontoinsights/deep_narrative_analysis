from dna.database import create_delete_database, query_database
from dna.load import add_narr_data_to_store, clean_text, simplify_text
from dna.utilities import dna_prefix

test_dna = 'test-dna-12345'


def test_create_database():
    # Tests database.py's create_delete_database
    # Will fail if the db already exists, but only need existence
    create_delete_database('create', test_dna)


def test_get_birth_family_triples():
    # Tests if the appropriate (metadata) triples are extracted from the narrative text
    # TODO
    return


def test_parse_narrative():
    # Tests the parsing of a narrative - that the correct triples are created and stored in the db
    # This basically tests most of the functions in the module
    # TODO
    return


def test_sentence_split():
    # Validates that sentence splitting is working correctly
    # TODO
    return


# def test_delete_database():
    # Tests database.py's create_delete_database
    # create_delete_database('delete', test_dna)
    # (Not deleted but maintained for after test review and use in other tests;
    # Duplicate processing should not add new triples)

# No need to test get_nouns_verbs since that is executed as part of details_summaries' test_get_unknown_words
