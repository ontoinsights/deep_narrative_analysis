from dna.app_functions import process_background, BackgroundAndNarrativeResults

name1 = {"name": "Eric Adams", "type": "person"}
name2 = {"name": "Las Vegas, CA", "type": "location"}
name3 = {"name": "New York City, NY", "type": "place"}
name4 = {"name": "NY politicians", "type": "person", "isCollection": True}
name5 = {"name": "House", "type": "organization", "isCollection": False}


def test_post():
    background_results = process_background([name1, name2, name3, name4, name5], 'foo')
    assert background_results.http_status == 201
    response = background_results.resp_dict
    assert response['repository'] == 'foo'
    assert len(response['processedNames']) == 4
    assert len(response['skippedNames']) == 1     # Las Vegas, CA
