import logging
import PySimpleGUI as sg

from database import query_database
from encoded_images import encoded_logo
from utilities import capture_error

query_hypotheses = 'prefix : <urn:ontoinsights:dna:> SELECT distinct ?hypo ?label WHERE ' \
                   '{ ?hypo a :Script ; rdfs:label ?label }'


def display_hypotheses(store_name: str):
    """
    Display a window to show currently defined hypotheses, and allow selection of one
    for display and possibly edit, or permit definition of a new hypothesis.

    :param store_name: The database/data store name holding the hypotheses
    :return: TBD
    """
    logging.info(f'Displaying hypotheses in {store_name}')
    # Setup the PySimpleGUI window
    sg.theme('Material2')
    layout = [[sg.Text("Not yet implemented.",
                       font=('Arial', 16))],
              [sg.Text("To exit, press 'End' or close the window.",
                       font=('Arial', 16))],
              [sg.Text()],
              [sg.Button('End', button_color='dark blue', size=(5, 1), font=('Arial', 14))]]

    # Get the data for the window
    try:
        success, hypotheses_results = query_database('select', query_hypotheses, store_name)
        number_hypotheses = 0
        if success and 'results' in hypotheses_results.keys() and \
                'bindings' in hypotheses_results['results'].keys():
            number_hypotheses = len(hypotheses_results['results']['bindings'])
    except Exception as e:
        capture_error(f'Exception getting hypotheses details from {store_name}: {str(e)}', True)
        return
    window_hypotheses_list = sg.Window('Display Hypotheses', layout, icon=encoded_logo).Finalize()

    # Event Loop to process window "events"
    while True:
        event_hypotheses_list, values = window_hypotheses_list.read()
        if event_hypotheses_list in (sg.WIN_CLOSED, 'End'):
            # If user closes window or clicks 'End'
            break

    # Done
    window_hypotheses_list.close()
    return
