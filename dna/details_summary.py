# Processing to display various graphs/charts concerning the characteristics of the narrators
# and their stories, or related to nouns/verbs which are not 'known'/understood by the ontology

import logging
import matplotlib.pyplot as plt
import PySimpleGUI as sg
from wordcloud import WordCloud, STOPWORDS

from database import query_database
from details_summary_counts import display_dates_events, display_locations, get_y_x_values, output_words_in_csv
from utilities import empty_string, resources_root, capture_error, encoded_logo
from utilities_matplotlib import draw_figure, display_horiz_histogram

query_countries = 'prefix : <urn:ontoinsights:dna:> SELECT distinct ?s ?country WHERE ' \
                  '{ ?narr a :Narrative ; :has_author ?narrator . ?event a :Birth ; :has_actor ?narrator ; ' \
                  ':has_location/:country_name ?country . { ?narrator a :Person . ' \
                  'FILTER NOT EXISTS { ?unifying1 a :UnifyingCollection ; :has_member ?narrator } . ' \
                  'BIND (?narrator as ?s) } UNION { ?unifying2 a :UnifyingCollection ; :has_member ?narrator . ' \
                  'BIND (?unifying2 as ?s) } }'

query_genders = 'prefix : <urn:ontoinsights:dna:> SELECT distinct ?s ?gender WHERE ' \
                '{ VALUES ?gender { :Female :Male :Agender :Bigender } . ' \
                '?narr a :Narrative ; :has_author ?narrator . ?narrator :has_agent_aspect ?gender . ' \
                '{ ?narrator a :Person . ' \
                'FILTER NOT EXISTS { ?unifying1 a :UnifyingCollection ; :has_member ?narrator } . ' \
                'BIND (?narrator as ?s) } UNION { ?unifying2 a :UnifyingCollection ; :has_member ?narrator . ' \
                'BIND (?unifying2 as ?s) } }'

query_narrative_text = 'prefix : <urn:ontoinsights:dna:> SELECT ?narr_text WHERE ' \
                       '{ ?narr a :Narrative ; :text ?narr_text . }'

query_number_narrators = 'prefix : <urn:ontoinsights:dna:> SELECT (COUNT(distinct ?s) as ?cnt) WHERE ' \
                         '{ ?narr a :Narrative ; :has_author ?narrator . { { ?narrator a :Person . ' \
                         'FILTER NOT EXISTS { ?unifying a :UnifyingCollection ; :has_member ?narrator } . ' \
                         'BIND(?narrator as ?s) } UNION { ?unifying a :UnifyingCollection ; :has_member ' \
                         '?narrator . BIND(?unifying as ?s) } } }'

query_years = 'prefix : <urn:ontoinsights:dna:> SELECT distinct ?s ?year WHERE ' \
              '{ ?narr a :Narrative ; :has_author ?narrator . ?event a :Birth ; :has_actor ?narrator ; ' \
              ':has_time/:year ?year . { ?narrator a :Person . ' \
              'FILTER NOT EXISTS { ?unifying1 a :UnifyingCollection ; :has_member ?narrator } . ' \
              'BIND (?narrator as ?s) } UNION { ?unifying2 a :UnifyingCollection ; :has_member ?narrator . ' \
              'BIND (?unifying2 as ?s) } }'


def display_statistics(store_name: str):
    """
    Display a window with buttons to show various graphs and charts, and/or output files with the
    top xx 'unknown to the ontology' nouns and verbs.

    :param store_name: The database/data store name
    :return: None (Window is displayed)
    """
    logging.info(f'Displaying summary statistics for {store_name}')
    # Setup the PySimpleGUI window
    sg.theme('Material2')
    layout = [[sg.Text("Click one or more of the buttons to display various summary statistics.",
                       font=('Arial', 16))],
              [sg.Text("To exit, press 'End' or close the window.",
                       font=('Arial', 16))],
              [sg.Text()],
              [sg.Text("Narrator Characteristics:", font=('Arial', 16))],
              [sg.Button('Gender Details', font=('Arial', 14), button_color='dark blue', size=(20, 1),
                         pad=((25, 0), 3))],
              [sg.Button('Birth Year Details', font=('Arial', 14), button_color='dark blue', size=(20, 1),
                         pad=((25, 0), 3))],
              [sg.Button('Birth Country Details', font=('Arial', 14), button_color='dark blue', size=(20, 1),
                         pad=((25, 0), 3))],
              [sg.Text()],
              [sg.Text("Narrative Information:", font=('Arial', 16))],
              [sg.Button('Locations Mentioned', font=('Arial', 14), button_color='blue', size=(24, 1),
                         pad=((25, 0), 3))],
              [sg.Button('Years and Events Mentioned', font=('Arial', 14), button_color='blue', size=(24, 1),
                         pad=((25, 0), 3))],
              [sg.Text()],
              [sg.Text("Frequent Words:", font=('Arial', 16))],
              [sg.Button('Word Cloud', font=('Arial', 14), button_color='blue', size=(24, 1),
                         pad=((25, 0), 3)),
               sg.Text('Number of words:', font=('Arial', 16)),
               sg.InputText(text_color='black', background_color='#ede8e8', size=(5, 1),
                            font=('Arial', 16), key='words_in_cloud', do_not_clear=True)],
              [sg.Button('Output "Unknown" Nouns/Verbs', font=('Arial', 14), button_color='blue', size=(24, 1),
                         pad=((25, 0), 3)),
               sg.Text('Number of nouns:', font=('Arial', 16)),
               sg.InputText(text_color='black', background_color='#ede8e8', size=(5, 1),
                            font=('Arial', 16), key='nouns_in_csv', do_not_clear=True),
               sg.Text('Number of verbs:', font=('Arial', 16)),
               sg.InputText(text_color='black', background_color='#ede8e8', size=(5, 1),
                            font=('Arial', 16), key='verbs_in_csv', do_not_clear=True)],
              [sg.Text("Directory:", font=('Arial', 16), pad=((125, 0), 3)),
               sg.FolderBrowse(target='directory_name', button_color='dark blue'),
               sg.InputText(text_color='black', background_color='#ede8e8',
                            font=('Arial', 16), key='directory_name', do_not_clear=True)],
              [sg.Text("The files, 'Nouns.csv' and 'Verbs.csv', will be written to the specified directory.",
                       font=('Arial', 16))],
              [sg.Text("This processing takes SEVERAL MINUTES if a large number of narratives are analyzed.",
                       font=('Arial', 16))],
              [sg.Text()],
              [sg.Button('End', button_color='dark blue', size=(5, 1), font=('Arial', 14))]]

    # Create the GUI Window
    try:
        number_narrators_results = query_database('select', query_number_narrators, store_name)
        if number_narrators_results:
            number_narrators = int(number_narrators_results[0]['cnt']['value'])
        else:
            sg.popup_error(f'No narrators are defined in {store_name}. '
                           f'Gender and birth details cannot be displayed.',
                           font=('Arial', 14), button_color='dark blue', icon=encoded_logo)
            number_narrators = 0
        narrative_text_results = query_database('select', query_narrative_text, store_name)
        if narrative_text_results:
            narratives = empty_string
            for binding in narrative_text_results:
                narratives += f" {binding['narr_text']['value']}"
        else:
            sg.popup_error(f'No narrators are defined in {store_name}. '
                           f'Summary graphs, charts and word frequencies cannot be generated.',
                           font=('Arial', 14), button_color='dark blue', icon=encoded_logo)
            narratives = empty_string
    except Exception as e:
        capture_error(f'Exception getting initial narrative details from {store_name}: {str(e)}', True)
        return
    window_stats_list = sg.Window('Display Summary Statistics', layout, icon=encoded_logo).Finalize()
    window_stats_list.find_element('directory_name', True).Update(resources_root[0:len(resources_root) - 1])
    window_stats_list.find_element('words_in_cloud', True).Update(50)
    window_stats_list.find_element('nouns_in_csv', True).Update(50)
    window_stats_list.find_element('verbs_in_csv', True).Update(50)

    # Event Loop to process window "events"
    while True:
        event_stats_list, values = window_stats_list.read()
        if event_stats_list in (sg.WIN_CLOSED, 'End'):
            # If user closes window or clicks 'End'
            break
        elif event_stats_list == 'Gender Details':
            if number_narrators:
                logging.info(f'Displaying gender statistics for {store_name}')
                y_values, x_values = get_y_x_values(number_narrators, 'gender', query_genders, store_name)
                display_horiz_histogram(y_values, x_values, 'Number of Narrators/Subjects', 'Narrator Genders')
            else:
                sg.popup_error(f'No narrators are defined in {store_name}. '
                               f'The gender histogram cannot be displayed.',
                               font=('Arial', 14), button_color='dark blue', icon=encoded_logo)
        elif event_stats_list == 'Birth Year Details':
            if number_narrators:
                logging.info(f'Displaying birth year statistics for {store_name}')
                y_values, x_values = get_y_x_values(number_narrators, 'year', query_years, store_name)
                display_horiz_histogram(y_values, x_values, 'Number of Narrators/Subjects Born in Year',
                                        'Narrator Birth Years')
            else:
                sg.popup_error(f'No narrators are defined in {store_name}. '
                               f'The birth histograms cannot be displayed.',
                               font=('Arial', 14), button_color='dark blue', icon=encoded_logo)
        elif event_stats_list == 'Birth Country Details':
            if number_narrators:
                logging.info(f'Displaying birth country statistics for {store_name}')
                y_values, x_values = get_y_x_values(number_narrators, 'country', query_countries, store_name)
                display_horiz_histogram(y_values, x_values, 'Number of Narrators/Subjects Born in Country',
                                        'Narrator Birth Countries')
            else:
                sg.popup_error(f'No narrators are defined in {store_name}. '
                               f'The birth histograms cannot be displayed.',
                               font=('Arial', 14), button_color='dark blue', icon=encoded_logo)
        elif event_stats_list == 'Locations Mentioned':
            if not narratives:
                sg.popup_error(f'No narrators are defined in {store_name}. '
                               f'A list of locations cannot be extracted.',
                               font=('Arial', 14), button_color='dark blue', icon=encoded_logo)
                continue
            display_locations(narratives)
        elif event_stats_list == 'Years and Events Mentioned':
            if not narratives:
                sg.popup_error(f'No narrators are defined in {store_name}. '
                               f'A list of years and events cannot be extracted.',
                               font=('Arial', 14), button_color='dark blue', icon=encoded_logo)
                continue
            display_dates_events(narratives)
        elif event_stats_list == 'Word Cloud':
            if not values['words_in_cloud']:
                sg.popup_error('A word count MUST be specified to configure the word cloud output. '
                               'Please provide a value.', font=('Arial', 14), button_color='dark blue',
                               icon=encoded_logo)
                continue
            if not narratives:
                sg.popup_error(f'No narrators are defined in {store_name}. '
                               f'The word cloud cannot be displayed.',
                               font=('Arial', 14), button_color='dark blue', icon=encoded_logo)
                continue
            _display_word_cloud(narratives, int(values['words_in_cloud']))
        elif event_stats_list == 'Output Top "Unknown" Nouns and Verbs':
            if not values['directory_name'] and not values['nouns_in_csv'] and not values['verbs_in_csv']:
                sg.popup_error('A directory name and noun/verb word counts MUST be specified to save '
                               'the unknown words and their frequency counts. Please provide all of these values.',
                               font=('Arial', 14), button_color='dark blue', icon=encoded_logo)
                continue
            if not narratives:
                sg.popup_error(f'No narratives were found in {store_name}. '
                               f'The word frequencies cannot be output.',
                               font=('Arial', 14), button_color='dark blue', icon=encoded_logo)
                continue
            logging.info(f'Outputting nouns/verbs for {store_name}')
            output_words_in_csv(narratives, int(values['nouns_in_csv']), int(values['verbs_in_csv']),
                                values['directory_name'])

    # Done
    window_stats_list.close()
    return


# Functions internal to the module
def _display_word_cloud(narratives: str, words_in_cloud: int):
    """
    Display a Word Cloud based on the texts of the narratives.

    :param narratives: String consisting of all the narratives' texts
    :param words_in_cloud: Integer value indicating the number of words to be displayed
    :return: None (Word cloud is displayed)
    """
    logging.info('Displaying word cloud')
    # Size the WordCloud plot
    plt.rcdefaults()
    fig, ax = plt.subplots()
    # Set stop-words (words to ignore)
    stopwords = set(STOPWORDS)
    stopwords.update(['will', 'per', 'us', 'said', 'even',
                      'one', 'two', 'first', 'second'])
    # Create WordCloud of top xx words in all documents
    wordcloud = WordCloud(stopwords=stopwords, max_font_size=50, max_words=words_in_cloud,
                          background_color='white').generate(narratives)
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    # Display in a window
    layout = [[sg.Canvas(key="-CANVAS-")]]
    window_cloud = sg.Window("Word Cloud Based on Narratives' Texts", layout,
                             icon=encoded_logo, element_justification='center').Finalize()
    draw_figure(window_cloud["-CANVAS-"].TKCanvas, fig)
    window_cloud.read()
    return
