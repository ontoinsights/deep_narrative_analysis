from dna.database import create_delete_database, query_database
from dna.load import add_narr_data_to_store, clean_text, simplify_text
from dna.utilities import dna_prefix

test_dna = 'test-dna-12345'

metadata_dict1 = {'Source': 'LastingMemory.txt', 'Title': 'LastingMemory', 'Person': '1',
                  'Given': 'Erika', 'Given2': '', 'Surname': 'Eckstut', 'Maiden': 'Neuman', 'Maiden2': '',
                  'Gender': 'F', 'Start': '15', 'End': '15', 'Remove': '4',
                  'Header': 'HOLOCAUST; MEMORIAL; MUSEUM', 'Footer': 'ECHOES; OF; MEMORY'}

metadata_dict2 = {'Source': 'TeachLove.txt', 'Title': 'TeachLove', 'Person': '1',
                  'Given': 'Erika', 'Given2': '', 'Surname': 'Eckstut', 'Maiden': 'Neuman', 'Maiden2': '',
                  'Gender': 'F', 'Start': '13', 'End': '14', 'Remove': '4',
                  'Header': 'HOLOCAUST; MEMORIAL; MUSEUM', 'Footer': 'ECHOES; OF; MEMORY'}

metadata_dict3 = {'Source': 'Erika.txt', 'Title': 'Erika', 'Person': '3',
                  'Given': 'Erika', 'Given2': '', 'Surname': 'Eckstut', 'Maiden': 'Neuman', 'Maiden2': '',
                  'Gender': 'F', 'Start': '12', 'End': '12', 'Remove': '1',
                  'Header': 'HOLOCAUST; MEMORIAL; MUSEUM', 'Footer': 'ECHOES; OF; MEMORY'}

text_query = 'prefix : <urn:ontoinsights:dna:> SELECT ?text WHERE { ' \
             '?narr a :Narrative . FILTER(CONTAINS(str(?narr), "title")) . ?narr :text ?text }'

metadata_query1 = 'prefix : <urn:ontoinsights:dna:> SELECT ?narr WHERE { ' \
                  '?narr a :Narrative ; :subject ?narrator }'

metadata_query2 = 'prefix : <urn:ontoinsights:dna:> SELECT ?narrator WHERE { ' \
                  '?narrator a :Person ; rdfs:label "Erika Neuman Eckstut" ; :has_agent_aspect :Female }'

metadata_query3 = 'prefix : <urn:ontoinsights:dna:> SELECT ?year ?country WHERE { ' \
                  '?birth a :Birth ; :has_time/:year ?year ; :has_location/:country_name ?country}'


def test_create_database():
    # Tests database.py's create_delete_database
    # Will fail if the db already exists, but only need existence
    create_delete_database('create', test_dna)


def test_csv_input_first_person_single_page_pdftotext_result():
    _test_csv_processing(metadata_dict1)


def test_csv_input_first_person_multi_page_pdftotext_result():
    _test_csv_processing(metadata_dict2)


def test_csv_processing_third_person_pdftotext_result():
    _test_csv_processing(metadata_dict3)


def test_check_narrator_metadata():
    # Checks that the narrative data created in add_narr_data_to_store (in the
    # _test_csv_processing) is correct
    # Also tests database.py's query_database
    success1, query_results1 = query_database('select', metadata_query1, test_dna)
    assert success1
    count_narratives = 0
    for binding in query_results1['results']['bindings']:
        if binding['narr']['value'] in (f'{dna_prefix}{metadata_dict1["Title"]}',
                                        f'{dna_prefix}{metadata_dict2["Title"]}',
                                        f'{dna_prefix}{metadata_dict3["Title"]}'):
            count_narratives += 1
    assert count_narratives == 3
    success2, query_results2 = query_database('select', metadata_query2, test_dna)
    assert success2
    assert query_results2['results']['bindings'][0]['narrator']['value'] == \
           f'{dna_prefix}ErikaNeumanEckstut'
    success3, query_results3 = query_database('select', metadata_query3, test_dna)
    assert success3
    assert query_results3['results']['bindings'][0]['year']['value'] == '1928'
    assert query_results3['results']['bindings'][0]['country']['value'] == 'Czechoslovakia'


def test_narrator_unification():
    # Tests whether narrators are correctly unified based on the domain criteria
    # In this case, the criteria is the narrator's/subject's name
    # TODO
    return


def test_page_cleanup_with_footer_in_sentence():
    # Tests ingest of a narrative where a pdf page break is in the middle of a sentence
    # _test_csv_processing(metadata_dict3)
    # TODO
    return


def test_wikidata_access():
    # Validates that the logic to get country information from wikidata is working correctly
    # TODO - check multiples including multipe countries returned
    return


# def test_delete_database():
    # Tests database.py's create_delete_database
    # create_delete_database('delete', test_dna)
    # (Not deleted but maintained for after test review and use in other tests;
    # Duplicate processing should not add new triples)


# Repeated code
def _test_csv_processing(metadata_dict: dict):
    # Tests narrative clean up and addition to the store, which are parts of the process_csv function
    # Specific functions tested: clean_text, simplify_text and add_narr_data_to_store
    # Also tests database.py's query_database
    with open(f'resources/{metadata_dict["Source"]}', 'r') as orig:
        # Get text as would be extracted by pdftotext
        orig_text = orig.read()
    # Perform processing steps to clean it, create metadata and store the results in the db
    text = clean_text(orig_text, metadata_dict)
    narrative = simplify_text(text, metadata_dict)
    add_narr_data_to_store(narrative.replace('"', "'"), metadata_dict, test_dna)
    # Get back the stored text
    success, query_results = query_database(
        'select', text_query.replace('title', metadata_dict['Title']), test_dna)
    assert success
    # Compare the stored results with what is expected
    with open(f'resources/Expected-{metadata_dict["Source"]}', 'r') as revised:
        rev_text = revised.read()
    # Is the text stored in the db as expected?
    assert query_results['results']['bindings'][0]['text']['value'] == rev_text
