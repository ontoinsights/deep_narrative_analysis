from dna.load_text_processing import clean_text, simplify_text
from test_dictionaries import metadata_dict1, metadata_dict2


def test_first_person_text():
    # Tests text simplification for the first episodic narrative for Erika Eckstut,
    # in Echoes of Memory, Vol 1 ("Teach Love, Not Hate")
    with open(f'resources/{metadata_dict2["Source"]}', 'r') as orig:
        # Get text as would be extracted by pdftotext
        orig_text = orig.read()
    # Perform processing steps to "simplify" the text
    narrative = simplify_text(orig_text, metadata_dict2)
    # Compare the narrative text with what is expected
    with open(f'resources/Expected-{metadata_dict2["Source"]}', 'r') as revised:
        assert narrative == revised.read()


def test_third_person_text():
    # Tests text processing for the first timeline narrative for Erika Eckstut, in Echoes of Memory, Vol 1
    with open(f'resources/{metadata_dict1["Source"]}', 'r') as orig:
        # Get text as would be extracted by pdftotext
        orig_text = orig.read()
    # Perform processing steps to clean the text and "simplify" it
    text = clean_text(orig_text, metadata_dict1)
    narrative = simplify_text(text, metadata_dict1)
    # Compare the narrative text with what is expected
    with open(f'resources/Expected-{metadata_dict1["Source"]}', 'r') as revised:
        assert narrative == revised.read()
