import csv
import logging
import os
import PySimpleGUI as sg
import requests
import subprocess

from SPARQLWrapper import SPARQLWrapper, JSON

from database import get_databases, add_remove_data, create_delete_database, query_database
from encoded_images import encoded_logo
from nlp import get_birth_family_details, parse_narrative
from utilities import EMPTY_STRING, SPACE, NEW_LINE, DOUBLE_NEW_LINE, \
    resources_root, gender_dict, months, countries, capture_error

get_id_url = 'https://en.wikipedia.org/w/api.php?action=query&prop=pageprops&titles=sub_title&format=json'

merge_delete = 'prefix : <urn:ontoinsights:dna:> DELETE { <unify2> ?p ?o } ' \
               'WHERE { <unify2> ?p ?o }'

merge_insert = 'prefix : <urn:ontoinsights:dna:> INSERT { <unify1> :has_member ?member } ' \
               'WHERE { <unify2> :has_member ?member }'

query_for_unification = 'prefix : <urn:ontoinsights:dna:> ' \
                        'SELECT ?narr1 ?unify1 ?narr2 ?unify2 WHERE {' \
                        '?narr1 a :Person ; rdfs:label ?label . ' \
                        '?narr2 a :Person ; rdfs:label ?label . ' \
                        'FILTER (str(?narr1) < str(?narr2)) . ' \
                        'OPTIONAL {?unify1 a :UnifyingCollection ; :has_member ?narr1 } ' \
                        'OPTIONAL {?unify2 a :UnifyingCollection ; :has_member ?narr2 } }'

sparql_wikidata = SPARQLWrapper(
    "https://query.wikidata.org/sparql",
    agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) '
          'Chrome/50.0.2661.102 Safari/537.36')

wikidata_query = 'SELECT ?country WHERE { wd:wikidata_id wdt:P17/rdfs:label ?country }'


def select_store() -> str:
    """
    Display a list of all database/store names and allow selection of one.

    :return: Either an empty string or the name of the selected data store
    """
    logging.info('Top-level select store processing')
    store_list = get_databases()
    if not store_list:
        sg.popup_ok('No stores are currently available.', font=('Arial', 14),
                    button_color='dark blue', icon=encoded_logo)
        return EMPTY_STRING

    # Setup the PySimpleGUI window
    sg.theme('Material2')
    layout = [[sg.Text("Select a store name and then press 'OK'.", font=('Arial', 16))],
              [sg.Text("To exit without making a selection, press 'End' or close the window.",
                       font=('Arial', 16))],
              [sg.Listbox(store_list, size=(30, 10), key='store_list', font=('Arial', 14),
                          background_color='#fafafa', highlight_background_color='light grey',
                          highlight_text_color='black', text_color='black')],
              [sg.Text()],
              [sg.Button('OK', button_color='dark blue', font=('Arial', 14), size=(5, 1)),
               sg.Button('End', button_color='dark blue', font=('Arial', 14), size=(5, 1))]]

    # Create the GUI Window
    window_store_list = sg.Window('Select Narrative Store', layout, icon=encoded_logo).Finalize()

    # Event Loop to process window "events"
    while True:
        event_store_list, values = window_store_list.read()
        if event_store_list in (sg.WIN_CLOSED, 'End'):
            # If user closes window or clicks 'End'
            selected_store = EMPTY_STRING
            break
        if event_store_list == 'OK':
            if len(values['store_list']) != 1:
                sg.popup_error('Either no store is selected, or more than one store is selected.',
                               font=('Arial', 14), button_color='dark blue', icon=encoded_logo)
            else:
                selected_store = values['store_list'][0]
                break

    # Done
    window_store_list.close()
    return selected_store


def ingest_narratives() -> (str, int):
    """
    Allow the user to select a CSV file for processing and to then select an existing
    database/store (or define a new store name) to which the described narratives are added.

    :return: String indicating the data store to which narratives were added
             Integer indicating the number of narratives added
    """
    logging.info('Ingesting narratives')
    store_list = get_databases()

    # Setup the PySimpleGUI window
    sg.theme('Material2')
    layout = [[sg.Text("Select CSV file:", font=('Arial', 16)),
               sg.FileBrowse(target='csv_file', button_color='dark blue'),
               sg.InputText(text_color='black', background_color='#ede8e8',
                            font=('Arial', 16), key='csv_file', do_not_clear=True)],
              [sg.Text()],
              [sg.Text('Choose a store from the following list:',  font=('Arial', 16))],
              [sg.Listbox(store_list, size=(30, 10), key='store_list', font=('Arial', 14),
                          background_color='#fafafa', highlight_background_color='light grey',
                          highlight_text_color='black', text_color='black', enable_events=True)],
              [sg.Text()],
              [sg.Text("OR enter a store name:", font=('Arial', 16)),
               sg.InputText(text_color='black', background_color='#ede8e8',
                            font=('Arial', 16), key='store_name', do_not_clear=True)],
              [sg.Text('If the store name does not exist, it will be created.', font=('Arial', 16))],
              [sg.Text()],
              [sg.Text("Note that ingest may take SEVERAL MINUTES to complete. Please be patient.",
                       font=('Arial', 16))],
              [sg.Text("This window will close when the ingest is complete.", font=('Arial', 16))],
              [sg.Text()],
              [sg.Text("To exit without making a selection, press 'End' or close the window.",
                       font=('Arial', 16))],
              [sg.Text()],
              [sg.Button('OK', button_color='dark blue', font=('Arial', 14), size=(5, 1)),
               sg.Button('End', button_color='dark blue', font=('Arial', 14), size=(5, 1))]]

    # Create the GUI Window
    window_csv = sg.Window('Select CSV File and Store', layout, icon=encoded_logo).Finalize()

    # Event Loop to process window "events"
    while True:
        event_csv, values = window_csv.read()
        if event_csv in (sg.WIN_CLOSED, 'End'):
            # If user closes window or clicks 'End'
            selected_store = EMPTY_STRING
            count = 0
            break
        if event_csv == 'store_list' and len(values['store_list']) == 1:
            window_csv.FindElement('store_name').Update(values['store_list'][0])
        if event_csv == 'OK':
            if not values['csv_file'] or not values['store_name']:
                sg.popup_error('Both a CSV file and data store must be specified.',
                               font=('Arial', 14), button_color='dark blue', icon=encoded_logo)
            else:
                selected_csv = values['csv_file'].strip()
                selected_store = values['store_name'].strip()
                count = process_csv(selected_csv, selected_store, store_list)
                break

    # Done
    window_csv.close()
    return selected_store, count


# Functions internal to the module, but accessible to testing
def add_narr_data_to_store(narrative: str, narr_metadata: dict, store_name: str):
    """
    Add narrative text and meta information to generate summary statistics and for later use
    in analyses.

    :param narrative: String consisting of the full narrative text
    :param narr_metadata: Dictionary of metadata information - Keys are:
                          Source,Title,Person,Given,Surname,Maiden,Gender,Start,End,Remove,Header,Footer
    :param store_name: The database/data store name
    :return: None (Specified database/store is updated with the narrative text and metadata,
             translated into RDF)
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
    iri_narrator = narrator.replace(SPACE, EMPTY_STRING)
    # Create triples describing the narrative and narrator/subject
    triples_list = list()
    triples_list.append(f'@prefix : <urn:ontoinsights:dna:> .')
    triples_list.append(f':{title} a :Narrative ; rdfs:label "{title}" ; '
                        f':text "{narrative}" ; :subject :{iri_narrator} .')
    triples_list.append(f':{iri_narrator} a :Person ; rdfs:label "{get_narrator_names(narr_metadata)}" .')
    if narr_metadata['Gender'] != 'U':
        triples_list.append(f':{iri_narrator} :has_agent_aspect {gender_dict[narr_metadata["Gender"]]} .')
    # Get additional information - the subject's birth date and place
    new_triples = get_birth_family_triples(narrative, narr_metadata['Given'], iri_narrator)
    if new_triples:
        triples_list.extend(new_triples)
    # Add the triples to the data store
    try:
        add_remove_data('add', ' '.join(triples_list), store_name)
    except Exception as e:
        capture_error(f'Exception adding narrative ({narr_metadata["Title"]}) triples to store: {str(e)}', True)


def clean_text(narrative: str, narr_metadata: dict) -> str:
    """
    Clean narrative text by:
      * Removing extraneous beginning white-space
      * Combining lines into paragraphs
      * Having 2 CR/LFs between paragraphs
      * Removing headers/footers (if they exist)

    :param narrative: String holding the text to be processed
    :param narr_metadata: Dictionary of metadata information - Keys are: Source,Title,Person,
                          Given,Given2,Surname,Maiden,Maiden2,Gender,Start,End,Remove,Header,Footer
    :return: Updated narrative text
    """
    new_text = EMPTY_STRING
    # Remove the first x line(s) from the text
    lines = narrative.split(NEW_LINE)[int(narr_metadata['Remove']):]
    ending_period_quote = False
    for line in lines:
        if not line:
            if ending_period_quote:
                new_text += DOUBLE_NEW_LINE         # 2 CR/LFs between paragraphs
                ending_period_quote = False
            # Else, just ignore the line assuming that it is a blank line between text and footer/header
        else:
            # Remove header/footer lines (if any are defined)
            if _check_header_footer_match(line, narr_metadata['Header'].split(';')):
                continue               # Skip line
            if _check_header_footer_match(line, narr_metadata['Footer'].split(';')):
                continue               # Skip line
            # Remove white space at beginning/ending of lines, and have 1 white space between words
            new_text += line.strip()
            # Remove dash at the end of a line (assume that it is a hyphenated word) and don't add space
            # TODO: Is a dash at the end always due to a hyphenated word?
            if new_text.endswith('-'):
                new_text = new_text[:-1]
            else:
                end_char = new_text[-1]
                if end_char in ['.', "'", '"']:
                    ending_period_quote = True
                new_text += ' '
    # Clean up final lines of text due to <NP> and other artifacts
    new_text = new_text.replace(' \n\n \n\n', ' \n').replace(' \n\n ', ' \n')
    return new_text


def create_narrative_graph(narrative: str, title: str, store_name: str):
    # TODO: Create KG of events using the sentences array
    sentences = parse_narrative(narrative)
    return


def get_birth_family_triples(narrative: str, given_name: str, iri_narrator: str) -> list:
    """
    Process the narrative text to see if there is information about where and when
    the narrator/subject was born, and if proper names can be associated with family
    members.

    :param narrative: String holding the narrative text
    :param given_name: String holding the narrator's/subject's name (to avoid including that name
                       as a location)
    :param iri_narrator: String holding the IRI defined for the narrator/subject
    :return: List holding strings of the new triples to add
    """
    logging.info('Getting birth details')
    new_triples = list()
    birth_date, birth_place, family_dict = get_birth_family_details(narrative)
    logging.info(f'birth date: {birth_date}')
    logging.info(f'birth place: {birth_place}')
    if birth_date or birth_place:
        # Create birth event
        new_triples.append(f':{iri_narrator}Birth a :Birth ; :has_actor :{iri_narrator} .')
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
            found_country = EMPTY_STRING
            labels = list()
            for value in birth_place:
                if value == given_name:
                    continue
                if value in countries:
                    found_country = value
                else:
                    labels.append(value)
            label_text = ', '.join(labels)
            if not found_country and labels:
                # TODO: What if the first country (most likely country) is not correct?
                # Should this return nothing?
                found_country = get_wikidata_country(labels[0])
            if found_country:
                label_text += f', {found_country}'
                new_triples.append(f':{iri_narrator}BirthPlace :country_name "{found_country}" .')
            new_triples.append(f':{iri_narrator}Birth :has_location :{iri_narrator}BirthPlace . '
                               f':{iri_narrator}BirthPlace a :PopulatedPlace ; rdfs:label "{label_text}" .')
        if len(family_dict):
            new_triples.append(f':{iri_narrator}Family a :Family ; :has_member :{iri_narrator} .')
            for key, value in family_dict.items():
                new_triples.append(f':{iri_narrator}Family :has_member :{iri_narrator}{key}{value} . '
                                   f':{iri_narrator}{key}{value} rdfs:label "{key}", "{value}" .')
    return new_triples


def get_narrator_names(narr_metadata: dict) -> str:
    """
    Create a list of names for the narrator/subject based on the metadata ... for example,
    given-maiden, given-maiden2, given-maiden-surname, given-maiden2-surname, given-surname,
    given2-maiden, given2-maiden2, given2-maiden-surname, given2-maiden2-surname, given2-surname

    :param narr_metadata: Dictionary of metadata information - Keys are: Source,Title,Person,
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


def get_wikidata_country(location: str) -> str:
    """
    Get the country for a GPE entity name

    :param location: String holding the GPE name
    :return: String holding the country name if it can be obtained from wikidata;
             An empty string otherwise
    """
    logging.info(f'Getting country info for {location}')
    # Get the wikidata id
    id_url = get_id_url.replace('sub_title', location)
    resp = requests.get(id_url)
    resp_dict = resp.json()
    for page in resp_dict['query']['pages']:
        if page != '-1' and 'pageprops' in resp_dict['query']['pages'][page].keys():
            wikidata_id = resp_dict['query']['pages'][page]['pageprops']['wikibase_item']
            # Get the country
            new_query = wikidata_query.replace('wikidata_id', wikidata_id)
            sparql_wikidata.setQuery(new_query)
            sparql_wikidata.setReturnFormat(JSON)
            results = sparql_wikidata.query().convert()
            for result in results["results"]["bindings"]:
                country = result["country"]["value"]
                if country in countries:
                    return country
    return EMPTY_STRING


def process_csv(csv_file: str, store_name: str, store_list: list) -> int:
    """
    Input the specified CSV file and process the narratives defined in it.
    The format of the CSV MUST be:
       Source,Title,Person,Given,Given2,Surname,Maiden,Maiden2,Gender,Start,End,Remove,Header,Footer

    :param csv_file: CSV file name
    :param store_name: Database/data store name
    :param store_list: List of the existing dbs -
                       Need to determine if a db name is new or existing
    :return: Count of the number of narratives ingested
    """
    logging.info(f'Processing the CSV, {csv_file}')
    count = 0
    db_exception = EMPTY_STRING
    if store_name not in store_list:
        db_exception = create_delete_database('create', store_name)
    if db_exception:
        capture_error(f'Error creating or deleting {store_name}: {db_exception}', True)
        return 0

    try:
        with open(csv_file, newline=EMPTY_STRING) as meta_file:
            narr_dict = csv.DictReader(meta_file)
            # Process each narrative based on the metadata:
            # Source,Title,Person,Given,Given2,Surname,Maiden,Maiden2,Gender,Start,End,Header,Footer
            for narr_meta in narr_dict:
                if 'Title' not in narr_meta.keys() or 'Given' not in narr_meta.keys():
                    capture_error('Expected columns not found in the CSV file. Processing stopped.', False)
                title = narr_meta['Title']
                logging.info(f'Ingesting the document, {title}')
                source = narr_meta['Source']
                # Must have at least the Source, Title, Person and Gender values defined
                if not source or not title or not narr_meta['Person'] \
                        or not narr_meta['Gender']:
                    sg.popup_error(f'For any source, the Source, Title, Person and Gender details MUST be '
                                   f'provided. This is not true for the CSV record with source file, '
                                   f'{source}, and narrative title, {title}. That record is skipped.',
                                   font=('Arial', 14), button_color='dark blue', icon=encoded_logo)
                    continue
                if source.endswith('.pdf'):
                    # Capture each narrative text from the metadata details in the CSV
                    if not narr_meta['Start'] and not narr_meta['End']:
                        sg.popup_error(f'For PDF source files, the Start and End page details MUST be '
                                       f'provided. This is not true for the CSV record with source file, '
                                       f'{source}, and narrative title, {title}. That record is skipped.',
                                       font=('Arial', 14), button_color='dark blue', icon=encoded_logo)
                        continue
                    in_file = f'{resources_root}{title}'
                    subprocess.run(['../tools/pdftotext', '-f', narr_meta['Start'], '-l', narr_meta['End'],
                                    '-simple', f'{resources_root}{source}', in_file])
                else:
                    in_file = f'{resources_root}{source}'
                with open(in_file, 'r', encoding='utf8', errors='ignore') as narr_in:
                    text = clean_text(narr_in.read(), narr_meta)
                    narrative = simplify_text(text, narr_meta)
                    add_narr_data_to_store(narrative.replace('"', "'"), narr_meta, store_name)
                    # create_narrative_graph(narrative, title, store_name)
                if source.endswith('.pdf'):
                    # Cleanup - Delete the text file created by pdftotext
                    os.remove(in_file)
                count += 1
        # Determine if any narrators/subjects (different names) are really the same
        logging.info('Checking if any unification can be performed')
        unified_triples = unify_narrators(store_name)
        if unified_triples:
            # Add the triples to the data store
            add_remove_data('add', ' '.join(unified_triples), store_name)
    except Exception as e:
        capture_error(f'Exception ingesting narratives: {str(e)}', True)
    return count


def simplify_text(narrative: str, narr_metadata: dict) -> str:
    """
    Update the text to change 3rd person instances of full name, given name + maiden name and
    given name + surname to 'I', and to change instances of 'the {maiden_name}s' and 'the {surname}s'
    to 'my family'. This is done to try to minimize co-reference problems.

    :param narrative: String holding the text to be processed
    :param narr_metadata: Dictionary of metadata information - Keys are: Source,Title,Person,
                          Given,Given2,Surname,Maiden,Maiden2,Gender,Start,End,Remove,Header,Footer
    :return: Updated narrative text
    """
    new_text = narrative
    # If third person, update name, 'she/he' to be 'I' and 'her/him' to be 'my'
    if narr_metadata['Person'] == '3':
        # Given name must be defined
        new_text = _replace_third_person(new_text, narr_metadata['Given'], narr_metadata)
        if narr_metadata['Given2']:
            new_text = _replace_third_person(new_text, narr_metadata['Given2'], narr_metadata)
        # TODO: Evaluate if the substitutions below cause other co-reference errors
        if narr_metadata['Gender'] == 'F':
            new_text = new_text.replace(' she ', ' I ')
            new_text = new_text.replace(' She ', ' I ')
            new_text = new_text.replace(' her ', ' my ')
            new_text = new_text.replace(' Her ', ' My ')
        elif narr_metadata['Gender'] == 'M':
            new_text = new_text.replace(' he ', ' I ')
            new_text = new_text.replace(' He ', ' I ')
            new_text = new_text.replace(' his ', ' my')
            new_text = new_text.replace(' His ', ' My')
    # Update occurrences of maiden name or surname to be 'my family'
    if narr_metadata['Maiden']:
        maiden_name = narr_metadata['Maiden']
        new_text = new_text.replace(f"the {maiden_name}s", 'my family')
        new_text = new_text.replace(f"The {maiden_name}s", 'My family')
    if narr_metadata['Maiden2']:
        maiden_name = narr_metadata['Maiden2']
        new_text = new_text.replace(f"the {maiden_name}s", 'my family')
        new_text = new_text.replace(f"The {maiden_name}s", 'My family')
    if narr_metadata['Surname']:
        surname = narr_metadata['Surname']
        new_text = new_text.replace(f"the {surname}s", 'my family')
        new_text = new_text.replace(f"The {surname}s", 'My family')
    return new_text


def unify_narrators(store_name: str) -> list:
    """
    Determine if any of the narrators should be 'unified' (are the same person but have
    different names).

    :param store_name: The database/data store name
    :return: List holding strings of the new triples to add
    """
    new_triples = list()
    success, results = query_database('select', query_for_unification, store_name)
    if success and results:
        for result in results['results']['bindings']:
            narr1 = result['narr1']['value']
            narr2 = result['narr2']['value']
            if 'unify1' in result.keys():
                unify1 = result['unify1']['value']
            else:
                unify1 = EMPTY_STRING
            if 'unify2' in result.keys():
                unify2 = result['unify2']['value']
            else:
                unify2 = EMPTY_STRING
            if not unify1 and not unify2:
                # Create new UnifyingCollection
                iri_collection = f'{narr1}{narr2.split("urn:ontoinsights:dna:")[-1]}'
                new_triples.append(f'@prefix : <urn:ontoinsights:dna:> . '
                                   f'<{iri_collection}> a :UnifyingCollection ; :has_member <{narr1}>, <{narr2}> .')
            elif unify1 and unify2 and unify1 != unify2:
                # Move unify2 members to unify1 via SPARQL UPDATE and delete unify2
                query_database('update', merge_insert.replace('unify1', unify1).replace('unify2', unify2), store_name)
                query_database('update', merge_delete.replace('unify2', unify2), store_name)
            elif unify1 and not unify2:
                # Add narr2 to unify1
                new_triples.append(f'@prefix : <urn:ontoinsights:dna:> . <{unify1}> :has_member <{narr2}> .')
            elif unify2 and not unify1:
                # Add narr1` to unify2
                new_triples.append(f'@prefix : <urn:ontoinsights:dna:> . <{unify2}> :has_member <{narr1}> .')
    else:
        logging.info('Failure querying for unification details')
    return new_triples


# Functions private to the module
def _check_header_footer_match(line: str, terms: list) -> bool:
    """
    Check the line of text if it includes all occurrences of the specified terms.

    :param line: String holding the line of text
    :param terms: Terms whose presence in the line are validated
    :return: True if all the specified terms are in the line (or if there are no terms defined)
             False otherwise
    """
    if len(terms) == 0:
        return False
    term_count = 0
    for term in terms:
        if term in line:
            term_count += 1
    if term_count == len(terms):
        return True
    else:
        return False


def _replace_third_person(narrative: str, given_name: str, narr_metadata: dict) -> str:
    """
    Update the text to change 3rd person instances of full name, given name + maiden name and
    given name + surname to 'I', and the possessive form to 'my'.

    :param narrative: String holding the narrative text
    :param given_name: The narrator's given name
    :param narr_metadata: Dictionary of metadata information - Keys are: Source,Title,Person,
                          Given,Given2,Surname,Maiden,Maiden2,Gender,Start,End,Remove,Header,Footer
    :return: String with the updated text
    """
    new_text = narrative
    maiden_name = narr_metadata['Maiden']
    maiden2_name = narr_metadata['Maiden2']
    surname = narr_metadata['Surname']
    new_text = new_text.replace(f"{given_name}'s ", 'my ')
    if maiden_name and surname:
        new_text = new_text.replace(f"{given_name} ({maiden_name}) {surname}'s ", 'my ')
        new_text = new_text.replace(f"{given_name} {maiden_name} {surname}'s ", 'my ')
        new_text = new_text.replace(f"{given_name} ({maiden_name}) {surname} ", 'I ')
        new_text = new_text.replace(f"{given_name} {maiden_name} {surname} ", 'I ')
    if maiden2_name and surname:
        new_text = new_text.replace(f"{given_name} ({maiden2_name}) {surname}'s ", 'my ')
        new_text = new_text.replace(f"{given_name} {maiden2_name} {surname}'s ", 'my ')
    if surname and not maiden_name and not maiden2_name:
        new_text = new_text.replace(f"{given_name} {surname}'s ", ' my ')
        new_text = new_text.replace(f"{given_name} {surname} ", 'I ')
    new_text = new_text.replace(f"{given_name} ", 'I ')
    return new_text
