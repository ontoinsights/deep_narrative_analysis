# Processes one or more narratives as described in a CSV file
# Displays one of two windows to load new narratives from a CSV or to load narratives already ingested
# If new narratives are ingested (a):
# 1) The text is loaded and simplified/cleaned
# 2) Narrative text and metadata are saved to the specified database/store name
# 3) spaCy's parse_narrative is called to do the spaCy parsing and create a dictionary of the sentence details
# 4) create_event_turtle is called to turn the dictionary into Turtle
# 5) The Turtle from (4) is loaded to a named graph identified by the narrative metadata's title
# 6) A check for multiple narrator names (due to aliases/maiden and married names/etc.) is performed and
#    if found, the metadata for these multiple narrators is combined

import csv
import logging
import os
import PySimpleGUI as sg
import subprocess
import sys
import traceback

from create_event_turtle import create_event_turtle
from create_metadata_turtle import create_metadata_turtle
from database import get_databases, add_remove_data, create_delete_database, query_database
from load_text_processing import clean_text, simplify_text
from nlp import parse_narrative
from utilities import empty_string, resources_root, capture_error, encoded_logo

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

# TODO: Remove stranded triples
remove_stranded_triples = 'prefix : <urn:ontoinsights:dna:> ' \
                          'DELETE { graph <urn:Erika_Eckstut> { ?inst ?p ?o } } WHERE ' \
                          '{ { graph <urn:narr_graph> { ?inst a ?type ; ?p ?o . ' \
                          'FILTER NOT EXISTS { ?inst2 ?pred ?inst } } } ' \
                          'FILTER NOT EXISTS { { graph <tag:stardog:api:context:default> { ' \
                          '?type rdfs:subClassOf* :EventAndState } } } FILTER(!(CONTAINS(str(?type), "Idiom"))) }'


def ingest_narratives() -> (str, int):   # pragma: no cover
    """
    Allow the user to select a CSV file for processing and to then select an existing
    database/store (or define a new store name) to which the described narratives are added.

    @return: String indicating the data store to which narratives were added
             Integer indicating the number of narratives added
    """
    store_list = get_databases()

    # Define the PySimpleGUI window
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
    window_csv['csv_file'].Widget.config(insertbackground='black')
    window_csv['store_name'].Widget.config(insertbackground='black')

    # Loop to process window "events"
    while True:
        event_csv, values = window_csv.read()
        if event_csv in (sg.WIN_CLOSED, 'End'):
            # If user closes window or clicks 'End'
            selected_store = empty_string
            count = 0
            break
        if event_csv == 'store_list' and len(values['store_list']) == 1:
            window_csv.find_element('store_name', True).Update(values['store_list'][0])
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


def select_store() -> str:    # pragma: no cover
    """
    Display a list of all database/store names and allow selection of one.

    @return: Either an empty string or the name of the selected data store
    """
    store_list = get_databases()
    if not store_list:
        sg.popup_ok('No stores are currently available.', font=('Arial', 14),
                    button_color='dark blue', icon=encoded_logo)
        return empty_string

    # Define the PySimpleGUI window
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

    # Loop to process window "events"
    while True:
        event_store_list, values = window_store_list.read()
        if event_store_list in (sg.WIN_CLOSED, 'End'):
            # If user closes window or clicks 'End'
            selected_store = empty_string
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


# Functions internal to the module, but accessible to testing
def process_csv(csv_file: str, store_name: str, store_list: list) -> int:  # pragma: no cover
    """
    Input the specified CSV file and process the narratives defined in it.
    The format of the CSV MUST be:
       Source,Title,Person,Type,Given,Given2,Surname,Maiden,Maiden2,Gender,Start,End,Remove,Header,Footer

    @param csv_file: CSV file name
    @param store_name: Database/data store name
    @param store_list: List of the existing dbs -
                       Need to determine if a db name is new or existing
    @return: Count of the number of narratives ingested
    """
    logging.info(f'Processing the CSV, {csv_file}')
    count = 0
    db_exception = empty_string
    if store_name not in store_list:
        db_exception = create_delete_database('create', store_name)
    if db_exception:
        capture_error(f'Error creating or deleting {store_name}: {db_exception}', True)
        return 0
    try:
        with open(csv_file, newline=empty_string) as meta_file:
            narr_dict = csv.DictReader(meta_file)
            # Process each narrative based on the metadata:
            # Source,Title,Person,Type,Given,Given2,Surname,Maiden,Maiden2,Gender,Start,End,Header,Footer
            for narr_meta in narr_dict:
                if 'Title' not in narr_meta.keys() or 'Given' not in narr_meta.keys():
                    capture_error('Expected columns not found in the CSV file. Processing stopped.', False)
                title = narr_meta['Title']
                if narr_meta['Type'] != 'T':    # TODO: Only process life timelines for now
                    continue
                # TODO: Remove
                print(f'Title: {title}')
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
                    # TODO: If the text is multi-page, the first line of all pages but the first is lost
                    in_file = f'{resources_root}{title}.txt'
                    subprocess.run(['../tools/pdftotext', '-f', narr_meta['Start'], '-l', narr_meta['End'],
                                    '-simple', f'{resources_root}{source}', in_file])
                else:
                    in_file = f'{resources_root}{source}'
                with open(in_file, 'r', encoding='utf8', errors='ignore') as narr_in:
                    if source.endswith('.pdf'):
                        text = clean_text(narr_in.read(), narr_meta)
                    else:
                        text = narr_in.read()
                    narrative = simplify_text(text, narr_meta)
                    # Get the narrator's gender (if possible), a list of family members mentioned
                    # (and their proper names, if possible) and the narrative + metadata Turtle
                    gender, family_dict, turtle_list = \
                        create_metadata_turtle(narrative.replace('"', "'"), narr_meta)
                    # Add the triples to the data store, default graph
                    try:
                        add_remove_data('add', ' '.join(turtle_list), store_name)
                    except Exception as e:
                        capture_error(
                            f'Exception adding ({narr_meta["Title"]}) metadata to store: {str(e)}', True)
                    sentence_dicts = parse_narrative(narrative, gender, family_dict)
                    print(sentence_dicts)
                    event_turtle_list = create_event_turtle(gender, sentence_dicts)
                    print(event_turtle_list)
                    # Add the triples to the data store, to a named graph with name = metadata title
                    try:
                        add_remove_data('add', ' '.join(event_turtle_list), store_name,
                                        f'urn:{title}')

                    except Exception as e:
                        capture_error(
                            f'Exception adding ({narr_meta["Title"]}) events to store: {str(e)}', True)
                if source.endswith('.pdf'):
                    # Cleanup - Delete the text file created by pdftotext
                    os.remove(in_file)
                count += 1
        # Determine if any narrators/subjects (different names) are really the same
        logging.info('Checking for unification of narrators')
        unified_triples = unify_narrators(store_name)
        if unified_triples:
            # Add the triples to the data store
            add_remove_data('add', ' '.join(unified_triples), store_name)
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        capture_error(f'Exception ingesting narratives: {str(e)}', True)
    return count


def unify_narrators(store_name: str) -> list:
    """
    Determine if any of the narrators should be 'unified' (are the same person but have
    different names).

    @param store_name: The database/data store name
    @return: List holding strings of the new triples to add
    """
    new_triples = []
    results = query_database('select', query_for_unification, store_name)
    for result in results:
        narr1 = result['narr1']['value']
        narr2 = result['narr2']['value']
        unify1 = result['unify1']['value'] if 'unify1' in result.keys() else empty_string
        unify2 = result['unify2']['value'] if 'unify2' in result.keys() else empty_string
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
    return new_triples
