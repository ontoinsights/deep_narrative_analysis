import logging
import PySimpleGUI as sg

from database import query_database
from encoded_images import encoded_logo
from utilities import capture_error

query_narrative_text = 'prefix : <urn:ontoinsights:dna:> SELECT ?narr_text WHERE ' \
                       '{ ?narr a :Narrative ; :text ?narr_text . }'


def display_similarities(store_name: str):
    """
    Display a window to show 'similar' narratives.

    :param store_name: The database/data store name holding the narratives
    :return: TBD
    """
    logging.info(f'Displaying similarities in {store_name}')
    # Setup the PySimpleGUI window
    sg.theme('Material2')
    layout = [[sg.Text("Not yet implemented.",
                       font=('Arial', 16))],
              [sg.Text("To exit, press 'End' or close the window.",
                       font=('Arial', 16))]]

    # Create the GUI Window
    try:
        success, narrative_results = query_database('select', query_narrative_text, store_name)
        number_narratives = 0
        if 'results' in narrative_results.keys() and \
                'bindings' in narrative_results['results'].keys():
            number_narratives = len(narrative_results['results']['bindings'])
        if not number_narratives:
            sg.popup_error(f'No narrators are defined in {store_name}. '
                           f'Similarities graph cannot be displayed.',
                           font=('Arial', 14), button_color='dark blue', icon=encoded_logo)
    except Exception as e:
        capture_error(f'Exception getting narratives for similarity analysis from {store_name}: {str(e)}',
                      True)
        return
    window_similarities_list = sg.Window('Narrative Similarities', layout, icon=encoded_logo).Finalize()

    # Event Loop to process window "events"
    while True:
        event_similarities_list, values = window_similarities_list.read()
        if event_similarities_list in (sg.WIN_CLOSED, 'End'):
            # If user closes window or clicks 'End'
            break
        # TODO

    # Done
    window_similarities_list.close()
    return
