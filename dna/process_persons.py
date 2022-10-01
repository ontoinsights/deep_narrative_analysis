# Processing related to PERSONS
# Called from create_narrative_turtle.py

import requests

from dna.create_noun_turtle import create_person_ttl
from dna.queries import query_wikidata_alt_names
from dna.query_sources import get_wikipedia_description
from dna.utilities import check_name_gender, empty_string, space


def _get_person_iri_and_ttl(person_text: str, plet_dict: dict, use_sources: bool) -> (list, str, str, list):
    """
    Handle person names identified by spaCy's NER, stored in the sentence dictionary with the
    key, 'PERSONS'.

    :param person_text: Text identifying the person
    :param plet_dict: A dictionary holding the persons, locations, events & times encountered in
             the full narrative - For co-reference resolution (it may be updated by this function);
             Keys = 'persons', 'locs', 'events', 'times', Values (for 'persons') = array of arrays
             with index 0 holding an array of labels associated with the person (variations on their
             name), index 1 storing the person's entity type and index 2 storing the person's IRI
    :param person_turtle: An array of Turtle statements defining named persons in the current chunk
    :param use_sources: Boolean indicating whether additional information on a person should
                        be retrieved from Wikidata (recommended)
    :return: A tuple holding 1) an array of alternate names for the person, 2) a string with the
             person's entity type, 3) IRI and 4) a list of Turtle statements defining the person
             (if the person is not already 'known'/processed, the plet_dict is updated)
    """
    person_type, person_iri = check_if_person_is_known(person_text, plet_dict)
    if person_iri:
        return person_type, person_iri, []
    person_iri = f':{person_text.replace(space,"_")}'
    alt_names = []
    wiki_details = empty_string
    if use_sources:
        wiki_details = get_wikipedia_description(person_text.replace(space, '_'))
        if wiki_details:
            if 'See the web site' not in wiki_details:
                wikidata_id = wiki_details.split('wikibase_item: ')[1].split(')')[0]
                query_alt_names = query_wikidata_alt_names.replace('?item', f'wd:{wikidata_id}')
                response = requests.get(f'https://query.wikidata.org/sparql?format=json&query={query_alt_names}').json()
                if 'results' in response and 'bindings' in response['results']:
                    results = response['results']['bindings']
                    for result in results:
                        alt_names.append(result['altLabel']['value'])
    split_names = person_text.split(space)
    if split_names[-1] not in alt_names:    # Get first and last names, if possible
        alt_names.append(split_names[-1])
    if person_text not in alt_names:
        alt_names.append(person_text)
    known_persons = plet_dict['persons'] if 'persons' in plet_dict else []
    person_type = check_name_gender(person_text)
    known_persons.append([alt_names, person_type, person_iri])
    plet_dict['persons'] = known_persons
    return person_type, person_iri, create_person_ttl(person_iri, alt_names, person_type, wiki_details)


def check_if_person_is_known(person_text: str, plet_dict: dict) -> (str, str):
    """
    Determines if the person is already processed and identified in the plet_dict.

    :param person_text: Input string identifying the person
    :param plet_dict: A dictionary holding the persons, locations, events & times encountered in
             the full narrative - For co-reference resolution (it may be updated by this function);
             Keys = 'persons', 'locs', 'events', 'times' and Values (for 'persons') = array of arrays
             with index 0 holding an array of labels associated with the person (variations on their
             name), index 1 storing the person's entity type and index 2 storing the person's IRI
    :return: A tuple holding the entity type and IRI of the person, or two empty strings
    """
    if 'persons' not in plet_dict:
        return empty_string, empty_string
    known_persons = plet_dict['persons']
    for known_person in known_persons:
        if person_text in known_person[0]:              # Strings match
            return known_person[1], known_person[2]     # NER maps to a known/processed location, with type and IRI
    return empty_string, empty_string


def get_sentence_persons(sent_dict: dict, plet_dict: dict, last_nouns: list, use_sources: bool) -> list:
    """
    Handle person names identified by spaCy's NER, stored in the sentence dictionary with the
    key, 'PERSONS'.

    :param sent_dict: The sentence dictionary
    :param plet_dict: A dictionary holding the persons, locations, events & times encountered in
             the full narrative - For co-reference resolution (it may be updated by this function);
             Keys = 'persons', 'locs', 'events', 'times', Values (for 'persons') = array of arrays
             with index 0 holding an array of labels associated with the person (variations on their
             name), index 1 storing the person's entity type and index 2 storing the person's IRI
    :param last_nouns: An array of tuples = noun texts, type, class mapping and IRI
                       from the current paragraph
    :param use_sources: Boolean indicating whether additional information on a person should
                        be retrieved from Wikidata (recommended)
    :return: An array of Turtle statements defining new persons identified in the sentence
             (also the plet_dict may be updated)
    """
    persons_turtle = []
    new_persons = sent_dict['PERSONS']
    new_persons_dict = dict()
    for new_person in new_persons:
        new_persons_dict[new_person] = check_if_person_is_known(new_person, plet_dict)
    for new_person, person_details in new_persons_dict.items():
        person_type, person_iri = person_details
        if not person_iri:
            # Need to define the Turtle for a new person
            person_type, person_iri, person_ttl = _get_person_iri_and_ttl(new_person, plet_dict, use_sources)
            persons_turtle.extend(person_ttl)
            last_nouns.append((new_person, person_type, [':Person'], person_iri))
        else:
            # Still need to update last_nouns
            last_nouns.append((new_person, person_type, [':Person'], person_iri))
    return persons_turtle
