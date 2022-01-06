# TODO: Summary of processing

import logging
import PySimpleGUI as sg

from database import query_database
from utilities import capture_error, encoded_logo

query_hypotheses = 'prefix : <urn:ontoinsights:dna:> SELECT distinct ?hypo ?label WHERE ' \
                   '{ ?hypo a :Script ; rdfs:label ?label }'

query_number_narratives = 'prefix : <urn:ontoinsights:dna:> SELECT (COUNT(?narr) as ?cnt) WHERE ' \
                       '{ ?narr a :Narrative . }'


def evaluate_hypothesis(store_name: str):
    """
    Display a window to show currently defined hypotheses, and allow selection and test
    of one of them.

    @param store_name: The database/data store name holding the hypotheses and narratives
    @return: TBD
    """
    logging.info(f'Test hypothesis in {store_name}')
    # Define the PySimpleGUI window
    sg.theme('Material2')
    layout = [[sg.Text("Not yet implemented.",
                       font=('Arial', 16))],
              [sg.Text("To exit, press 'End' or close the window.",
                       font=('Arial', 16))],
              [sg.Text()],
              [sg.Button('End', button_color='dark blue', size=(5, 1), font=('Arial', 14))]]

    # Create the GUI Window
    try:
        hypotheses_results = query_database('select', query_hypotheses, store_name)
        number_hypotheses = 0
        number_narratives = 0
        if hypotheses_results:
            number_hypotheses = len(hypotheses_results)
        narratives_results = query_database('select', query_number_narratives, store_name)
        if narratives_results:
            number_narratives = int(narratives_results[0]['cnt']['value'])
        error_msg = ''
        if not number_hypotheses:
            error_msg = 'No hypotheses'
            if not number_narratives:
                error_msg = 'and no narratives'
        else:
            if not number_narratives:
                error_msg = 'No narratives'
        if error_msg:
            error_msg += f' are defined in {store_name}.'
            sg.popup_error(error_msg, font=('Arial', 14), button_color='dark blue', icon=encoded_logo)
    except Exception as e:
        capture_error(f'Exception getting hypotheses details from {store_name}: {str(e)}', True)
        return
    window_test_list = sg.Window('Test Hypothesis', layout, icon=encoded_logo).Finalize()

    # Event Loop to process window "events"
    while True:
        event_test_list, values = window_test_list.read()
        if event_test_list in (sg.WIN_CLOSED, 'End'):
            # If user closes window or clicks 'End'
            break
        # TODO: Test hypothesis

    # Done
    window_test_list.close()
    return
