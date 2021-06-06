import csv
import logging
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import numpy as np
import PySimpleGUI as sg
from wordcloud import WordCloud, STOPWORDS

from database import query_database
from encoded_images import encoded_logo
from nlp import get_nouns_verbs
from utilities import EMPTY_STRING, NEW_LINE, \
    resources_root, capture_error, draw_figure, update_dictionary_count

query_countries = 'prefix : <urn:ontoinsights:dna:> SELECT distinct ?s ?country WHERE ' \
                  '{ ?narr a :Narrative ; :subject ?narrator . ?event a :Birth ; :has_actor ?narrator ; ' \
                  ':has_location/:country_name ?country . { ?narrator a :Person . ' \
                  'FILTER NOT EXISTS { ?unifying1 a :UnifyingCollection ; :has_member ?narrator } . ' \
                  'BIND (?narrator as ?s) } UNION { ?unifying2 a :UnifyingCollection ; :has_member ?narrator . ' \
                  'BIND (?unifying2 as ?s) } }'

query_genders = 'prefix : <urn:ontoinsights:dna:> SELECT distinct ?s ?gender WHERE ' \
                '{ VALUES ?gender { :Female :Male :Agender :Bigender } . ' \
                '?narr a :Narrative ; :subject ?narrator . ?narrator :has_agent_aspect ?gender . ' \
                '{ ?narrator a :Person . ' \
                'FILTER NOT EXISTS { ?unifying1 a :UnifyingCollection ; :has_member ?narrator } . ' \
                'BIND (?narrator as ?s) } UNION { ?unifying2 a :UnifyingCollection ; :has_member ?narrator . ' \
                'BIND (?unifying2 as ?s) } }'

query_narrative_text = 'prefix : <urn:ontoinsights:dna:> SELECT ?narr_text WHERE ' \
                       '{ ?narr a :Narrative ; :text ?narr_text . }'

query_number_narrators = 'prefix : <urn:ontoinsights:dna:> SELECT (COUNT(distinct ?s) as ?cnt) WHERE ' \
                         '{ ?narr a :Narrative ; :subject ?narrator . { { ?narrator a :Person . ' \
                         'FILTER NOT EXISTS { ?unifying a :UnifyingCollection ; :has_member ?narrator } . ' \
                         'BIND(?narrator as ?s) } UNION { ?unifying a :UnifyingCollection ; :has_member ?narrator . ' \
                         'BIND(?unifying as ?s) } } }'

query_years = 'prefix : <urn:ontoinsights:dna:> SELECT distinct ?s ?year WHERE ' \
              '{ ?narr a :Narrative ; :subject ?narrator . ?event a :Birth ; :has_actor ?narrator ; ' \
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
        success1, number_narrators_results = query_database('select', query_number_narrators, store_name)
        if success1 and 'results' in number_narrators_results.keys() and \
                'bindings' in number_narrators_results['results'].keys():
            number_narrators = int(number_narrators_results['results']['bindings'][0]['cnt']['value'])
        else:
            sg.popup_error(f'No narrators are defined in {store_name}. '
                           f'Gender and birth details cannot be displayed.',
                           font=('Arial', 14), button_color='dark blue', icon=encoded_logo)
            number_narrators = 0
        success2, narrative_text_results = query_database('select', query_narrative_text, store_name)
        if success2 and 'results' in narrative_text_results.keys() \
                and 'bindings' in narrative_text_results['results'].keys():
            narratives = EMPTY_STRING
            for binding in narrative_text_results['results']['bindings']:
                narratives += f" {binding['narr_text']['value']}"
        else:
            sg.popup_error(f'No narrators are defined in {store_name}. '
                           f'Summary graphs, charts and word frequencies cannot be generated.',
                           font=('Arial', 14), button_color='dark blue', icon=encoded_logo)
            narratives = EMPTY_STRING
    except Exception as e:
        capture_error(f'Exception getting initial narrative details from {store_name}: {str(e)}', True)
        return
    window_stats_list = sg.Window('Display Summary Statistics', layout, icon=encoded_logo).Finalize()
    window_stats_list.FindElement('directory_name').Update(resources_root[0:len(resources_root) - 1])
    window_stats_list.FindElement('words_in_cloud').Update(50)
    window_stats_list.FindElement('nouns_in_csv').Update(50)
    window_stats_list.FindElement('verbs_in_csv').Update(50)

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
                _display_horiz_histogram(y_values, x_values, 'Number of Narrators/Subjects', 'Narrator Genders')
            else:
                sg.popup_error(f'No narrators are defined in {store_name}. '
                               f'The gender histogram cannot be displayed.',
                               font=('Arial', 14), button_color='dark blue', icon=encoded_logo)
        elif event_stats_list == 'Birth Year Details':
            if number_narrators:
                logging.info(f'Displaying birth year statistics for {store_name}')
                y_values, x_values = get_y_x_values(number_narrators, 'year', query_years, store_name)
                _display_horiz_histogram(y_values, x_values, 'Number of Narrators/Subjects Born in Year',
                                         'Narrator Birth Years')
            else:
                sg.popup_error(f'No narrators are defined in {store_name}. '
                               f'The birth histograms cannot be displayed.',
                               font=('Arial', 14), button_color='dark blue', icon=encoded_logo)
        elif event_stats_list == 'Birth Country Details':
            if number_narrators:
                logging.info(f'Displaying birth country statistics for {store_name}')
                y_values, x_values = get_y_x_values(number_narrators, 'country', query_countries, store_name)
                _display_horiz_histogram(y_values, x_values, 'Number of Narrators/Subjects Born in Country',
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
            _display_locations(narratives)
        elif event_stats_list == 'Years and Events Mentioned':
            if not narratives:
                sg.popup_error(f'No narrators are defined in {store_name}. '
                               f'A list of years and events cannot be extracted.',
                               font=('Arial', 14), button_color='dark blue', icon=encoded_logo)
                continue
            _display_years_events(narratives)
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
            _output_words_in_csv(narratives, int(values['nouns_in_csv']), int(values['verbs_in_csv']),
                                 values['directory_name'])

    # Done
    window_stats_list.close()
    return


# Functions internal to the module, but accessible to testing
def get_y_x_values(number_narrators: int, variable: str, query: str, store_name: str) -> (tuple, tuple):
    """
    Get the count of narrators by gender, birth country and birth year. Also provide counts where
    this info is not known.

    :param number_narrators: Total number of narrators
    :param variable: String indicating the name of the returned SPARQL query variable - either
                     'gender', 'year' or 'country'
    :param query: String holding the query to run to get the count
    :param store_name: String holding the database/data store name with the narratives and narrator details
    :return: Two tuples of integers - for the y and x axes of a horizontal bar chart
             The y axis is the list of genders, birth countries and birth years,
             and the x axis is the number of narrators
    """
    dictionary = dict()
    # Get count
    success, count_results = query_database('select', query, store_name)
    if success:
        if 'results' in count_results.keys() and 'bindings' in count_results['results'].keys():
            for binding in count_results['results']['bindings']:
                # Manipulate the key value in case it is an IRI
                update_dictionary_count(dictionary, str(binding[variable]['value']).split(':')[-1])
    # Make sure that all narrators are addressed
    total_count = 0
    y_list = []
    for key in dictionary.keys():
        total_count += dictionary[key]
        y_list.append(key)
    if total_count != number_narrators:
        dictionary['Unknown'] = number_narrators - total_count
        y_list.append('Unknown')
    # Sort the results and create the returned tuples
    y_values = sorted(y_list)
    x_values = []
    for y_value in y_values:
        x_values.append(dictionary[y_value])
    return tuple(y_values), tuple(x_values)


# Functions internal to the module
def _display_horiz_histogram(y_values: tuple, x_values: tuple, x_label: str, title: str):
    """
    Display a horizontal bar chart/histogram using matplotlib.

    :param y_values: The y-axis (horizontal) values
    :param x_values: The x-axis (vertical) values
    :param x_label: The labels on the x-axis (MUST correspond to the order of the values)
    :param title: The title of the histogram chart
    :return: None (Histogram is displayed)
    """
    logging.info('Displaying histogram')
    # Setup the histogram
    plt.rcdefaults()
    fig, ax = plt.subplots()
    y_pos = np.arange(len(y_values))
    ax.barh(y_pos, x_values, align='edge')
    ax.set_yticks(y_pos)
    ax.set_yticklabels(y_values)
    ax.invert_yaxis()  # labels read top-to-bottom
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_xlabel(x_label)
    plt.tight_layout(pad=2.0)
    # Display in a window
    layout = [[sg.Canvas(key="-CANVAS-")]]
    window_histogram = sg.Window(title, layout, icon=encoded_logo, element_justification='center',
                                 finalize=True)
    draw_figure(window_histogram["-CANVAS-"].TKCanvas, fig)
    # Non-blocking window
    window_histogram.read(timeout=0)


def _display_locations(narratives: str):
    """
    Display a table of locations and counts of their occurrences in the narratives.

    :param narratives: String consisting of all the narratives' texts
    :return: None (Table of locations and counts is displayed)
    """
    logging.info(f'Displaying locations in narratives')
    # Setup the PySimpleGUI window
    sg.theme('Material2')
    layout = [[sg.Text("Not yet implemented.",
                       font=('Arial', 16))],
              [sg.Text("To exit, press 'End' or close the window.",
                       font=('Arial', 16))],
              [sg.Text()],
              [sg.Button('End', button_color='dark blue', size=(5, 1), font=('Arial', 14))]]

    # Get the data for the window
    # TODO
    # try:
    #     success, hypotheses_results = query_database('select', query_hypotheses, store_name)
    #     number_hypotheses = 0
    #     if success and 'results' in hypotheses_results.keys() and \
    #             'bindings' in hypotheses_results['results'].keys():
    #         number_hypotheses = len(hypotheses_results['results']['bindings'])
    # except Exception as e:
    #     capture_error(f'Exception getting hypotheses details from {store_name}: {str(e)}', True)
    #     return
    window_locations = sg.Window('Display Locations Mentioned in Narratives',
                                 layout, icon=encoded_logo).Finalize()

    # Event Loop to process window "events"
    while True:
        event_locations, values = window_locations.read()
        if event_locations in (sg.WIN_CLOSED, 'End'):
            # If user closes window or clicks 'End'
            break

    # Done
    window_locations.close()
    return


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
    # Non-blocking window
    window_cloud.read(timeout=0)


def _display_years_events(narratives: str):
    """
    Display a table of years and counts of their occurrences in the narratives.

    :param narratives: String consisting of all the narratives' texts
    :return: None (Table of locations and counts is displayed)
    """
    logging.info(f'Displaying years and events in narratives')
    # Setup the PySimpleGUI window
    sg.theme('Material2')
    layout = [[sg.Text("Not yet implemented.",
                       font=('Arial', 16))],
              [sg.Text("To exit, press 'End' or close the window.",
                       font=('Arial', 16))],
              [sg.Text()],
              [sg.Button('End', button_color='dark blue', size=(5, 1), font=('Arial', 14))]]

    # Get the data for the window
    # TODO
    # try:
    #     success, hypotheses_results = query_database('select', query_hypotheses, store_name)
    #     number_hypotheses = 0
    #     if success and 'results' in hypotheses_results.keys() and \
    #             'bindings' in hypotheses_results['results'].keys():
    #         number_hypotheses = len(hypotheses_results['results']['bindings'])
    # except Exception as e:
    #     capture_error(f'Exception getting hypotheses details from {store_name}: {str(e)}', True)
    #     return
    window_years_events = sg.Window('Display Locations Mentioned in Narratives',
                                    layout, icon=encoded_logo).Finalize()

    # Event Loop to process window "events"
    while True:
        event_years_events, values = window_years_events.read()
        if event_years_events in (sg.WIN_CLOSED, 'End'):
            # If user closes window or clicks 'End'
            break

    # Done
    window_years_events.close()
    return


def _output_words_in_csv(narratives: str, nouns_in_csv: int, verbs_in_csv: int, directory_name: str):
    """
    Output the top xx 'unknown to the ontology' nouns and verbs in the narratives' texts
    to the files, <directory_name>/Nouns.csv and <directory_name>/Verbs.csv.
    The nouns, verbs and a count of their occurrences is returned.

    :param narratives: String consisting of all the narratives' texts
    :param nouns_in_csv: Integer value indicating the number of nouns to be output
    :param verbs_in_csv: Integer value indicating the number of verbs to be output
    :param directory_name: String indicating the base file name to which the nouns, verbs and
                           their frequencies are output
    :return: None (.csv files are generated)
    """
    sorted_nouns, sorted_verbs = get_nouns_verbs(narratives)
    # TODO: Make words lower case
    with open(f'{directory_name}/Nouns.csv', 'w', newline=NEW_LINE) as noun_file:
        noun_writer = csv.writer(noun_file, delimiter=',')
        noun_writer.writerow(['Noun', 'Count'])
        count = 0
        for key, value in sorted_nouns.items():
            if count < nouns_in_csv:
                count += 1
                noun_writer.writerow([key, value])
            else:
                break
    with open(f'{directory_name}/Verbs.csv', 'w') as verb_file:
        verb_writer = csv.writer(verb_file, delimiter=',')
        verb_writer.writerow(['Verb', 'Count'])
        count = 0
        for key, value in sorted_verbs.items():
            if count < verbs_in_csv:
                count += 1
                verb_writer.writerow([key, value])
            else:
                break
    return
