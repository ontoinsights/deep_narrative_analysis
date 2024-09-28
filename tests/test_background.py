from dna.app_functions import process_background, BackgroundAndNarrativeResults

name1 = {"name": "Eric Adams", "type": "person"}
name2 = {"name": "Las Vegas, CA", "type": "location"}
name3 = {"name": "New York City, NY", "type": "place"}
name4 = {"name": "NY politicians", "type": "person", "isCollection": True}


def test_post():
    background_results = process_background([name1, name2, name3, name4], 'foo')
    assert background_results.http_status == 201
    response = background_results.resp_dict
    assert response['repository'] == 'debate'
    assert len(response['processedNames']) == 3
    assert len(response['skippedNames']) == 1
