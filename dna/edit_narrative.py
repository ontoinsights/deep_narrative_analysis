# Processing to display a window to select a narrative for edit, and then to show a table of
# the sentences from the narrative and their parses

import logging
import PySimpleGUI as sg

from database import query_database
from details_narrative import get_narratives
from utilities import capture_error, encoded_logo

query_events_in_range = 'prefix : <urn:ontoinsights:dna:> SELECT distinct ?event ?label ?year ?month ?day ' \
                        'FROM <urn:narr_graph> FROM <tag:stardog:api:context:default> WHERE ' \
                        '{ ?event a ?type ; rdfs:label ?label . ?type rdfs:subClassOf+ :EventAndState . ' \
                        '{ { ?event :has_time ?time } UNION { ?event :has_beginning ?time } } ' \
                        '?time :year ?year . FILTER(?year >= beginning_year) . FILTER(?year <= ending_year) . ' \
                        'OPTIONAL { ?time :month_of_year ?month . OPTIONAL { ?time :day_of_month ?day } } } ' \
                        'ORDER BY ?year ?month ?day '

query_events = 'prefix : <urn:ontoinsights:dna:> SELECT distinct ?event ?label ?year ?month ?day ' \
               'FROM <urn:narr_graph> FROM <tag:stardog:api:context:default> WHERE ' \
               '{ ?event a ?type ; rdfs:label ?label . ?type rdfs:subClassOf+ :EventAndState . ' \
               '{ { ?event :has_time ?time } UNION { ?event :has_beginning ?time } } ' \
               '?time :year ?year . ' \
               'OPTIONAL { ?time :month_of_year ?month . OPTIONAL { ?time :day_of_month ?day } } } ' \
               'ORDER BY ?year ?month ?day'


def display_narratives(store_name: str):
    """
    Display a list of all narratives in the specified store (without the domain timeline, if one is defined)
    and allow selection of one. Then, display the parse details for the selected narrative.

    :param store_name: The database/data store name
    :return: None (Narrative timeline is displayed)
    """
    logging.info('Narrative selection for edit')
    # Get the list of narratives
    narrative_dict = get_narratives(store_name)
    if 'urn:Domain_Events' in narrative_dict.keys():
        del narrative_dict['urn:Domain_Events']
    if len(narrative_dict) == 0:
        sg.popup_ok(f'No narratives were found in {store_name}. '
                    f'Please select a different store or ingest one or more using the "Load Narratives" button.',
                    font=('Arial', 14), button_color='dark blue', icon=encoded_logo)
        return
    else:
        narrative_list = [narr.replace('_', '') for narr in narrative_dict.keys()]

    # Setup the PySimpleGUI window
    sg.theme('Material2')
    layout = [[sg.Text("Select a narrative.", font=('Arial', 16))],
              [sg.Text(f"Press 'OK' to edit the narrative, or press 'End' (or close the window) to exit.",
                       font=('Arial', 16))],
              [sg.Listbox(narrative_list, size=(30, 10), key='narrative_list', font=('Arial', 14),
                          background_color='#fafafa', highlight_background_color='light grey',
                          highlight_text_color='black', text_color='black')],
              [sg.Text()],
              [sg.Button('OK', button_color='dark blue', font=('Arial', 14), size=(5, 1)),
               sg.Button('End', button_color='dark blue', font=('Arial', 14), size=(5, 1))]]

    # Create the GUI Window
    window_edit = sg.Window('Select Narrative for Edit', layout, icon=encoded_logo).Finalize()

    # Loop to process window "events"
    while True:
        edit_events, values = window_edit.read()
        if edit_events in (sg.WIN_CLOSED, 'End'):
            # If user closes window or clicks 'End'
            break
        if edit_events == 'OK':
            if len(values['narrative_list']) != 1:
                sg.popup_error('Either nothing was selected, or more than one selection was made.',
                               font=('Arial', 14), button_color='dark blue', icon=encoded_logo)
            else:
                narrative_name = values['narrative_list'][0]
                # Get events for the selected narrative
                try:
                    events_list = query_database(
                        'select', query_events.replace('narr_graph', narrative_name.replace(' ', '_')), store_name)
                    if not events_list:
                        sg.popup_error(f'No events are defined for the narrative, {narrative_name}. '
                                       f'There is nothing to edit.',
                                       font=('Arial', 14), button_color='dark blue', icon=encoded_logo)
                except Exception as e:
                    capture_error(
                        f'Exception getting events for {narrative_name} in the {store_name}: {str(e)}', True)
                    return
                # Display table of events
                display_table(narrative_name, events_list, store_name)

    # Done
    window_edit.close()
    return
