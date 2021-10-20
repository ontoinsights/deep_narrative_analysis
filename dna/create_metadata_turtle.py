# Processing to create the narrative metadata Turtle

import logging

from nlp import get_birth_family_details
from query_ontology_and_sources import get_geonames_location
from utilities import empty_string, space, family_members, gender_dict, months, countries


def create_metadata_turtle(narrative: str, narr_metadata: dict) -> (str, dict, list):
    """
    Create Turtle capturing the narrative text and metadata information.

    :param narrative: String consisting of the full narrative text
    :param narr_metadata: Dictionary of metadata information - Keys are:
                          Source,Title,Person,Type,Given,Surname,Maiden,Gender,Start,End,Remove,Header,Footer
    :return: 3 items: 1) String identifying the gender of the narrator if known (or an empty string otherwise;
             gender is one of AGENDER, BIGENDER, FEMALE or MALE), 2) a dictionary containing the family member
             roles mentioned in the narrative and the members' proper names (if provided), and 3) a list of
             Turtle statements to add to the database with the narrative and metadata information
    """
    # Construct the narrator's/subject's identifier
    if narr_metadata['Maiden'] and narr_metadata['Surname']:
        narrator = f'{narr_metadata["Given"]} {narr_metadata["Maiden"]} {narr_metadata["Surname"]}'
    elif narr_metadata['Surname']:
        narrator = f'{narr_metadata["Given"]} {narr_metadata["Surname"]}'
    else:
        narrator = f'{narr_metadata["Given"]}'
    # Create the reference to the doc in the db store
    title = narr_metadata["Title"]
    title_text = title.replace('_', ' ')
    iri_narrator = narrator.replace(space, empty_string)
    # Create triples describing the narrative and narrator/subject
    triples_list = [f'@prefix : <urn:ontoinsights:dna:> .',
                    f':{title} a :Narrative ; rdfs:label "{title_text}" ; '
                    f':text "{narrative}" ; :has_author :{iri_narrator} .',
                    f':{iri_narrator} a :Person ; rdfs:label "{get_narrator_names(narr_metadata)}" .']
    gender = narr_metadata['Gender']
    if gender and gender != 'U':
        gender = gender_dict[gender]
        triples_list.append(f':{iri_narrator} :has_agent_aspect {gender} .')
    # Get additional information - the subject's birth date, place and the names of family members
    new_triples, family_dict = get_birth_family_turtle(narrative, narr_metadata['Given'], iri_narrator)
    if new_triples:
        triples_list.extend(new_triples)
    return gender[1:].upper(), family_dict, triples_list


def get_birth_family_turtle(narrative: str, given_name: str, iri_narrator: str) -> (list, dict):
    """
    Process the narrative text to see if there is information about where and when
    the narrator/subject was born, and if proper names can be associated with family
    members. If so, generate Turtle to capture this info.

    :param narrative: String holding the narrative text
    :param given_name: String holding the narrator's/subject's name (to avoid including that name
                       as a location)
    :param iri_narrator: String holding the IRI defined for the narrator/subject
    :return: List holding strings of the new triples to add and a dictionary containing the names
             of family members and their relationship to the narrator/subject
    """
    logging.info('Getting birth details')
    new_triples = []
    family_dict = dict()
    # Set up default family dictionary with the roles mentioned in the narrative
    for fam_rel in family_members.keys():
        if fam_rel in narrative:
            family_dict[fam_rel] = fam_rel
    # Replace any family dictionary values if a proper name is found; Also get birth details
    # This info is obtained using spaCy's pattern matching (in the nlp module)
    birth_date, birth_place, revised_family_dict = get_birth_family_details(narrative)
    for rev_fam, value in revised_family_dict.items():
        family_dict[rev_fam] = value
    logging.info(f'birth date: {birth_date}')
    logging.info(f'birth place: {birth_place}')
    logging.info(f'family: {family_dict}')
    if birth_date or birth_place:
        # Create birth event Turtle
        new_triples.append(f':{iri_narrator}Birth a :Birth ; :has_affected_agent :{iri_narrator} .')
        if birth_date:
            new_triples.append(f':{iri_narrator}Birth :has_time :{iri_narrator}BirthTime .')
            new_triples.append(f':{iri_narrator}BirthTime a :PointInTime .')
            for value in birth_date:
                if value in months:
                    new_triples.append(f':{iri_narrator}BirthTime :month_of_year {months.index(value) + 1} .')
                if value.isnumeric():
                    if int(value) < 32:
                        new_triples.append(f':{iri_narrator}BirthTime :day_of_month {value} .')
                    elif int(value) > 1000:
                        new_triples.append(f':{iri_narrator}BirthTime :year {value} .')
        if birth_place:
            found_country = empty_string
            labels = []
            for value in birth_place:
                if value == given_name:
                    continue
                if value in countries:
                    found_country = value
                else:
                    labels.append(value)
            label_text = ', '.join(labels)
            if not found_country and labels:
                # TODO: What if the first country (most likely country) is not correct? Or the country is not found?
                loc_type, found_country, admin_level = get_geonames_location(labels[0])  # Only need country
            if found_country:
                label_text += f', {found_country}'
                new_triples.append(f':{iri_narrator}BirthPlace :country_name "{found_country}" .')
            new_triples.append(f':{iri_narrator}Birth :has_location :{iri_narrator}BirthPlace . '
                               f':{iri_narrator}BirthPlace a :PopulatedPlace ; rdfs:label "{label_text}" .')
        # Create family Turtle
        if len(family_dict):
            new_triples.append(f':{iri_narrator}Family a :Family ; :has_member :{iri_narrator} .')
            for key, value in family_dict.items():
                if key == value:
                    new_triples.append(f':{iri_narrator}Family :has_member :{iri_narrator}{key} . '
                                       f':{iri_narrator}{key} rdfs:label "{key}" .')
                else:
                    new_triples.append(f':{iri_narrator}Family :has_member :{iri_narrator}{key}{value} . '
                                       f':{iri_narrator}{key}{value} rdfs:label "{key}", "{value}" .')
    return new_triples, family_dict


def get_narrator_names(narr_metadata: dict) -> str:
    """
    Create a list of names for the narrator/subject based on the metadata ... for example,
    given-maiden, given-maiden2, given-maiden-surname, given-maiden2-surname, given-surname,
    given2-maiden, given2-maiden2, given2-maiden-surname, given2-maiden2-surname, given2-surname

    :param narr_metadata: Dictionary of metadata information - Keys are: Source,Title,Person,Type,
                          Given,Given2,Surname,Maiden,Maiden2,Gender,Start,End,Remove,Header,Footer
    :return: String holding names ('labels') for the narrator/subject, separated appropriately
             for inclusion as a comma-separated set of strings
    """
    given = narr_metadata['Given']  # Will always be present
    given2 = narr_metadata['Given2']
    maiden = narr_metadata['Maiden']
    maiden2 = narr_metadata['Maiden2']
    surname = narr_metadata['Surname']
    names = set()
    if surname:
        names.add(f'{given} {surname}')
        if maiden:
            names.add(f'{given} {maiden}')
            names.add(f'{given} {maiden} {surname}')
        if maiden2:
            names.add(f'{given} {maiden2}')
            names.add(f'{given} {maiden2} {surname}')
        if given2:
            names.add(f'{given2} {surname}')
            if maiden:
                names.add(f'{given2} {maiden}')
                names.add(f'{given2} {maiden} {surname}')
            if maiden2:
                names.add(f'{given2} {maiden2}')
                names.add(f'{given2} {maiden2} {surname}')
    else:
        names.add(f'{given}')
        if given2:
            names.add(f'{given2}')
    return '", "'.join(list(names))
