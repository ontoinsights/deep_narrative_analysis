# Main application processing

import logging
import PySimpleGUI as sg

from database import query_database
from details_narrative import display_narratives
from details_similarities import display_similarities
from details_summary import display_statistics
from edit_narrative import display_narratives_for_edit
from help import display_popup_help
from hypotheses import display_hypotheses
from load import select_store, ingest_narratives
from evaluate_hypothesis import evaluate_hypothesis
from utilities import dark_blue, empty_string, capture_error, encoded_logo, encoded_question

logging.basicConfig(level=logging.INFO, filename='dna.log',
                    format='%(funcName)s - %(levelname)s - %(asctime)s - %(message)s')

query_number_narratives = 'prefix : <urn:ontoinsights:dna:> SELECT (COUNT(distinct ?narr) as ?cnt) ' \
                          'WHERE { ?narr a :Narrative } '


# Main
if __name__ == '__main__':
    # Application is a minimal GUI that exercises narrative ingest and NLP/NLU components
    logging.info('Opened DNA GUI')

    # Create the PySimpleGUI window
    sg.theme('Material2')
    layout = [[sg.Image(r'resources/DNA2.png'),
               sg.Text('Deep Narrative Analysis', font=('Arial', 24, 'bold'))],
              [sg.Text()],
              [sg.Text('Minimal GUI to demo ingest and natural language understanding (NLU)',
                       font=('Arial', 20, 'bold'))],
              [sg.Text()],
              [sg.Text("Load Narratives:", font=('Arial', 16))],
              [sg.Button('From Existing Store', font=('Arial', 14), button_color=dark_blue,
                         size=(22, 1), pad=((25, 0), 3)),
               sg.Button(empty_string, image_data=encoded_question,
                         button_color=(sg.theme_background_color(), sg.theme_background_color()),
                         border_width=0, key='existing_question', pad=(1, 1))],
              [sg.Button('New, From CSV Metadata', font=('Arial', 14), button_color=dark_blue,
                         size=(22, 1), pad=((25, 0), 3)),
               sg.Button(empty_string, image_data=encoded_question,
                         button_color=(sg.theme_background_color(), sg.theme_background_color()),
                         border_width=0, key='csv_question', pad=(1, 1))],
              [sg.Text('No narratives/store currently selected', size=(70, 1),
                       key='text-selected', font=('Arial', 14))],
              [sg.Text()],
              [sg.Text('One or more narratives MUST be loaded in order to select any buttons below.',
                       font=('Arial', 16))],
              [sg.Text()],
              [sg.Text("Edit Narrative Details:", font=('Arial', 16))],
              [sg.Button('Edit Narrative', font=('Arial', 14), button_color='blue', size=(20, 1),
                         pad=((25, 0), 3)),
               sg.Button(empty_string, image_data=encoded_question,
                         button_color=(sg.theme_background_color(), sg.theme_background_color()),
                         border_width=0, key='edit_question', pad=(1, 1))],
              [sg.Text()],
              [sg.Text("Display Narrative Details:", font=('Arial', 16))],
              [sg.Button('Summary Statistics', font=('Arial', 14), button_color='blue', size=(20, 1),
                         pad=((25, 0), 3)),
               sg.Button(empty_string, image_data=encoded_question,
                         button_color=(sg.theme_background_color(), sg.theme_background_color()),
                         border_width=0, key='stats_question', pad=(1, 1))],
              [sg.Button('Narrative Timeline', font=('Arial', 14), button_color='blue',
                         size=(20, 1), pad=((25, 0), 3)),
               sg.Button(empty_string, image_data=encoded_question,
                         button_color=(sg.theme_background_color(), sg.theme_background_color()),
                         border_width=0, key='timeline_question', pad=(1, 1))],
              [sg.Button('Narrative Similarities', font=('Arial', 14), button_color='blue',
                         size=(20, 1), pad=((25, 0), 3)),
               sg.Button(empty_string, image_data=encoded_question,
                         button_color=(sg.theme_background_color(), sg.theme_background_color()),
                         border_width=0, key='similarities_question', pad=(1, 1))],
              [sg.Text()],
              [sg.Text("Run Analysis:", font=('Arial', 16))],
              [sg.Button('Hypothesis Search/Edit', font=('Arial', 14), button_color='blue',
                         size=(24, 1), pad=((25, 0), 3)),
               sg.Button(empty_string, image_data=encoded_question,
                         button_color=(sg.theme_background_color(), sg.theme_background_color()),
                         border_width=0, key='hypothesis_question', pad=(1, 1))],
              [sg.Button('Hypothesis Test', font=('Arial', 14), button_color='blue',
                         size=(24, 1), pad=((25, 0), 3)),
               sg.Button(empty_string, image_data=encoded_question,
                         button_color=(sg.theme_background_color(), sg.theme_background_color()),
                         border_width=0, key='test_question', pad=(1, 1))],
              [sg.Text()],
              [sg.Button('End', button_color=dark_blue, size=(5, 1), font=('Arial', 14))]]

    # Create the GUI Window
    store_name = empty_string
    window = sg.Window('Deep Narrative Analysis', layout, icon=encoded_logo).Finalize()

    # Loop to process window "events"
    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, 'End'):
            # If user closes window or clicks 'End'
            break
        # Help for various buttons
        elif event in ('existing_question', 'csv_question', 'edit_question', 'similarities_question',
                       'timeline_question', 'stats_question', 'hypothesis_question', 'test_question'):
            display_popup_help(event)
        # New windows to process narratives
        # TODO: Remove reference to the domain timeline (from the next 2 events) if not applicable
        elif event == 'From Existing Store':
            store_name = select_store()
            if store_name:
                count_results = query_database('select', query_number_narratives, store_name)
                if count_results:
                    count = int(count_results[0]['cnt']['value'])
                    window['text-selected'].\
                        update(f'The data store, {store_name}, holds {count-1} narratives and the domain timeline.')
                else:
                    capture_error('The query for narrative count failed.', True)
        elif event == 'New, From CSV Metadata':
            store_name, count = ingest_narratives()
            if store_name:
                window['text-selected'].\
                    update(f'{count} narratives and the domain timeline were added '
                           f'to the data store, {store_name}')
        elif event == 'Summary Statistics':
            if not store_name:
                sg.popup_error("A narrative store must be loaded before selecting 'Summary Statistics'.",
                               font=('Arial', 14), button_color=dark_blue, icon=encoded_logo)
            else:
                display_statistics(store_name)
        elif event == 'Narrative Timeline':
            if not store_name:
                sg.popup_error("A narrative store must be loaded before selecting 'Narrative Timeline'.",
                               font=('Arial', 14), button_color=dark_blue, icon=encoded_logo)
            else:
                display_narratives(store_name)
        elif event == 'Narrative Similarities':
            if not store_name:
                sg.popup_error("A narrative store must be loaded before selecting 'Narrative Similarities'.",
                               font=('Arial', 14), button_color=dark_blue, icon=encoded_logo)
            else:
                display_similarities(store_name)
        elif event == 'Edit Narrative':
            display_narratives_for_edit(store_name)
        elif event == 'Hypothesis Search/Edit':
            display_hypotheses(store_name)
        elif event == 'Hypothesis Test':
            evaluate_hypothesis(store_name)

    # Done
    window.close()
