import logging
import PySimpleGUI as sg

from encoded_images import encoded_logo, encoded_question
from help import display_popup_help
from analyses import display_hypotheses, test_hypothesis
from details import display_narratives, display_similarities
from details_summary import display_statistics
from load import select_store, ingest_narratives
from database import query_database

logging.basicConfig(level=logging.INFO, filename='dna.log',
                    format='%(funcName)s - %(levelname)s - %(asctime)s - %(message)s')

query_number_narratives = 'prefix : <urn:ontoinsights:dna:> SELECT (COUNT(distinct ?narr) as ?cnt) ' \
                          'WHERE { ?narr a :Narrative } '


# Main
if __name__ == '__main__':
    logging.info('Opened DNA GUI')

    # Setup the PySimpleGUI window
    sg.theme('Material2')
    layout = [[sg.Image(r'resources/DNA2.png'),
               sg.Text('Deep Narrative Analysis', font=('Arial', 24, 'bold'))],
              [sg.Text()],
              [sg.Text("Load Narratives:", font=('Arial', 16))],
              [sg.Button('From Existing Store', font=('Arial', 14), button_color='dark blue',
                         size=(22, 1), pad=((25, 0), 3)),
               sg.Button('', image_data=encoded_question,
                         button_color=(sg.theme_background_color(), sg.theme_background_color()),
                         border_width=0, key='existing_question', pad=(1, 1))],
              [sg.Button('New, From CSV Metadata', font=('Arial', 14), button_color='dark blue',
                         size=(22, 1), pad=((25, 0), 3)),
               sg.Button('', image_data=encoded_question,
                         button_color=(sg.theme_background_color(), sg.theme_background_color()),
                         border_width=0, key='csv_question', pad=(1, 1))],
              [sg.Text('No narratives/store currently selected', size=(70, 1),
                       key='text-selected', font=('Arial', 14))],
              [sg.Text()],
              [sg.Text("Display Narrative Details:", font=('Arial', 16))],
              [sg.Button('Summary Statistics', font=('Arial', 14), button_color='blue', size=(20, 1),
                         pad=((25, 0), 3)),
               sg.Button('', image_data=encoded_question,
                         button_color=(sg.theme_background_color(), sg.theme_background_color()),
                         border_width=0, key='stats_question', pad=(1, 1))],
              [sg.Button('Narrative Search/Display', font=('Arial', 14), button_color='blue',
                         size=(20, 1), pad=((25, 0), 3)),
               sg.Button('', image_data=encoded_question,
                         button_color=(sg.theme_background_color(), sg.theme_background_color()),
                         border_width=0, key='search_question', pad=(1, 1))],
              [sg.Button('Narrative Similarities', font=('Arial', 14), button_color='blue',
                         size=(20, 1), pad=((25, 0), 3)),
               sg.Button('', image_data=encoded_question,
                         button_color=(sg.theme_background_color(), sg.theme_background_color()),
                         border_width=0, key='similarities_question', pad=(1, 1))],
              [sg.Text()],
              [sg.Text("Run Analysis:", font=('Arial', 16))],
              [sg.Button('Hypothesis Search/Edit', font=('Arial', 14), button_color='blue',
                         size=(24, 1), pad=((25, 0), 3)),
               sg.Button('', image_data=encoded_question,
                         button_color=(sg.theme_background_color(), sg.theme_background_color()),
                         border_width=0, key='hypothesis_question', pad=(1, 1))],
              [sg.Button('Hypothesis Test', font=('Arial', 14), button_color='blue',
                         size=(24, 1), pad=((25, 0), 3)),
               sg.Button('', image_data=encoded_question,
                         button_color=(sg.theme_background_color(), sg.theme_background_color()),
                         border_width=0, key='test_question', pad=(1, 1))],
              [sg.Text()],
              [sg.Button('End', button_color='dark blue', size=(5, 1), font=('Arial', 14))]]

    # Create the GUI Window
    store_name = ''
    window = sg.Window('Deep Narrative Analysis', layout, icon=encoded_logo).Finalize()

    # Event Loop to process window "events"
    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, 'End'):
            # If user closes window or clicks 'End'
            break
        # Help for various buttons
        elif event in ('existing_question', 'csv_question', 'similarities_question',
                       'search_question', 'stats_question', 'hypothesis_question', 'test_question'):
            display_popup_help(event)
        # New windows to process narratives
        elif event == 'From Existing Store':
            store_name = select_store()
            if store_name:
                success, count_results = query_database('select', query_number_narratives, store_name)
                if success and 'results' in count_results.keys() and 'bindings' in count_results['results'].keys():
                    count = int(count_results['results']['bindings'][0]['cnt']['value'])
                    window['text-selected'].\
                        update(f'The data store, {store_name}, holds {count} narratives.')
                else:
                    sg.popup_error('The query for narrative count failed. Please contact a system administrator.',
                                   font=('Arial', 14), button_color='dark blue', icon=encoded_logo)
        elif event == 'New, From CSV Metadata':
            store_name, count = ingest_narratives()
            if store_name:
                window['text-selected'].\
                    update(f'{count} narratives were added to the data store, {store_name}')
        elif event == 'Summary Statistics':
            if not store_name:
                sg.popup_error("A narrative store must be loaded before selecting 'Summary Statistics'.",
                               font=('Arial', 14), button_color='dark blue', icon=encoded_logo)
            else:
                display_statistics(store_name)
        elif event == 'Narrative Search/Display':
            if not store_name:
                sg.popup_error("A narrative store must be loaded before selecting 'Narrative Search'.",
                               font=('Arial', 14), button_color='dark blue', icon=encoded_logo)
            else:
                display_narratives()
        elif event == 'Narrative Similarities':
            if not store_name:
                sg.popup_error("A narrative store must be loaded before selecting 'Narrative Similarities'.",
                               font=('Arial', 14), button_color='dark blue', icon=encoded_logo)
            else:
                display_similarities()
        elif event == 'Hypothesis Search/Edit':
            display_hypotheses()
        elif event == 'Hypothesis Test':
            test_hypothesis()

    # Done
    window.close()
