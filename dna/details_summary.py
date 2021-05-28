import csv
import logging
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import PySimpleGUI as sg
from wordcloud import WordCloud, STOPWORDS

from database import query_database
from encoded_images import encoded_logo
from nlp import get_nouns_verbs
from utilities import resources_root, update_dictionary_count

query_number_narrators = 'prefix : <urn:ontoinsights:dna:> SELECT (COUNT(distinct ?s) as ?cnt) WHERE ' \
                         '{ ?narr a :Narrative ; :subject ?narrator . { { ?narrator a :Person . ' \
                         'FILTER NOT EXISTS { ?unifying a :UnifyingCollection ; :has_member ?narrator } . ' \
                         'BIND(?narrator as ?s) } UNION { ?unifying a :UnifyingCollection ; :has_member ?narrator . ' \
                         'BIND(?unifying as ?s) } } }'

query_narrative_text = 'prefix : <urn:ontoinsights:dna:> SELECT ?narr_text WHERE ' \
                       '{ ?narr a :Narrative ; :text ?narr_text . }'

query_genders = 'prefix : <urn:ontoinsights:dna:> SELECT distinct ?s ?gender WHERE ' \
                '{ VALUES ?gender { :Female :Male :Agender :Bigender } . ' \
                '?narr a :Narrative ; :subject ?narrator . ?narrator :has_characteristic ?gender . ' \
                '{ ?narrator a :Person . ' \
                'FILTER NOT EXISTS { ?unifying1 a :UnifyingCollection ; :has_member ?narrator } . ' \
                'BIND (?narrator as ?s) } UNION { ?unifying2 a :UnifyingCollection ; :has_member ?narrator . ' \
                'BIND (?unifying2 as ?s) } }'

query_years = 'prefix : <urn:ontoinsights:dna:> SELECT distinct ?s ?year WHERE ' \
              '{ ?narr a :Narrative ; :subject ?narrator . ?event a :Birth ; :has_actor ?narrator ; ' \
              ':has_time/:year ?year . { ?narrator a :Person . ' \
              'FILTER NOT EXISTS { ?unifying1 a :UnifyingCollection ; :has_member ?narrator } . ' \
              'BIND (?narrator as ?s) } UNION { ?unifying2 a :UnifyingCollection ; :has_member ?narrator . ' \
              'BIND (?unifying2 as ?s) } }'

query_countries = 'prefix : <urn:ontoinsights:dna:> SELECT distinct ?s ?country WHERE ' \
                  '{ ?narr a :Narrative ; :subject ?narrator . ?event a :Birth ; :has_actor ?narrator ; ' \
                  ':has_location/:country_name ?country . { ?narrator a :Person . ' \
                  'FILTER NOT EXISTS { ?unifying1 a :UnifyingCollection ; :has_member ?narrator } . ' \
                  'BIND (?narrator as ?s) } UNION { ?unifying2 a :UnifyingCollection ; :has_member ?narrator . ' \
                  'BIND (?unifying2 as ?s) } }'


def display_statistics(store_name: str):
    """
    Display a window with buttons to show various graphs and charts, and/or output files with the
    top xx nouns and verbs.

    :param store_name: The database/data store name
    :return: None
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
              [sg.Button('Locations Mentioned', font=('Arial', 14), button_color='blue', size=(20, 1),
                         pad=((25, 0), 3))],
              [sg.Button('Times Mentioned', font=('Arial', 14), button_color='blue', size=(20, 1),
                         pad=((25, 0), 3))],
              [sg.Text()],
              [sg.Text("Frequent Words:", font=('Arial', 16))],
              [sg.Button('Word Cloud', font=('Arial', 14), button_color='blue', size=(24, 1),
                         pad=((25, 0), 3)),
               sg.Text('Number of words:', font=('Arial', 16)),
               sg.InputText(text_color='black', background_color='#ede8e8', size=(5, 1),
                            font=('Arial', 16), key='words_in_cloud', do_not_clear=True)],
              [sg.Button('Output Top Nouns and Verbs', font=('Arial', 14), button_color='blue', size=(24, 1),
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
        success, number_narrators_results = query_database('select', query_number_narrators, store_name)
        if 'results' in number_narrators_results.keys() and \
                'bindings' in number_narrators_results['results'].keys():
            number_narrators = int(number_narrators_results['results']['bindings'][0]['cnt']['value'])
        else:
            logging.error(f'No narrators are defined in {store_name}. '
                          f'Gender and birth histograms cannot be displayed.')
            number_narrators = 0
        success, narrative_text_results = query_database('select', query_narrative_text, store_name)
        if 'results' in narrative_text_results.keys() \
                and 'bindings' in narrative_text_results['results'].keys():
            narratives = ''
            for binding in narrative_text_results['results']['bindings']:
                narratives += ' ' + binding['narr_text']['value']
        else:
            logging.error(f'No narratives were found in {store_name}. '
                          f'Word cloud and frequency output cannot be generated.')
            narratives = ''
    except Exception as e:
        logging.error(f'Exception getting initial narrative details from {store_name}: {str(e)}')
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
                sg.popup_error(f'No narrators are defined in {store_name}. The gender histogram cannot be displayed.',
                               font=('Arial', 14), button_color='dark blue', icon=encoded_logo)
        elif event_stats_list == 'Birth Year Details':
            if number_narrators:
                logging.info(f'Displaying birth year statistics for {store_name}')
                y_values, x_values = get_y_x_values(number_narrators, 'year', query_years, store_name)
                _display_horiz_histogram(y_values, x_values, 'Number of Narrators/Subjects Born in Year',
                                         'Narrator Birth Years')
            else:
                sg.popup_error(f'No narrators are defined in {store_name}. The birth histograms cannot be displayed.',
                               font=('Arial', 14), button_color='dark blue', icon=encoded_logo)
        elif event_stats_list == 'Birth Country Details':
            if number_narrators:
                logging.info(f'Displaying birth country statistics for {store_name}')
                y_values, x_values = get_y_x_values(number_narrators, 'country', query_countries, store_name)
                _display_horiz_histogram(y_values, x_values, 'Number of Narrators/Subjects Born in Country',
                                         'Narrator Birth Countries')
            else:
                sg.popup_error(f'No narrators are defined in {store_name}. The birth histograms cannot be displayed.',
                               font=('Arial', 14), button_color='dark blue', icon=encoded_logo)
        elif event_stats_list == 'Word Cloud':
            if not values['words_in_cloud']:
                sg.popup_error('A word count MUST be specified to configure the word cloud output. '
                               'Please provide a value.', font=('Arial', 14), button_color='dark blue',
                               icon=encoded_logo)
                continue
            if not narratives:
                sg.popup_error(f'No narratives were found in {store_name}. The word cloud cannot be displayed.',
                               font=('Arial', 14), button_color='dark blue', icon=encoded_logo)
                continue
            _display_word_cloud(narratives, int(values['words_in_cloud']))
        elif event_stats_list == 'Output Top Nouns and Verbs':
            if not values['directory_name'] and not values['nouns_in_csv'] and not values['verbs_in_csv']:
                sg.popup_error('A directory name and noun/verb word counts MUST be specified to save the frequency '
                               'counts. Please provide all of these values.', font=('Arial', 14),
                               button_color='dark blue', icon=encoded_logo)
                continue
            if not narratives:
                sg.popup_error(f'No narratives were found in {store_name}. The word frequencies cannot be output.',
                               font=('Arial', 14), button_color='dark blue', icon=encoded_logo)
                continue
            logging.info(f'Outputting nouns/verbs for {store_name}')
            _output_words_in_csv(narratives, int(values['nouns_in_csv']), int(values['verbs_in_csv']),
                                 values['directory_name'])

    # Done
    window_stats_list.close()
    return


def display_narratives():
    return


def display_similarities():
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
    :return: None
    """
    logging.info('Displaying histogram')
    # Setup the histogram
    plt.rcdefaults()
    fig, ax = plt.subplots()
    y_pos = np.arange(len(y_values))
    ax.barh(y_pos, x_values, align='center')
    ax.set_yticks(y_pos)
    ax.set_yticklabels(y_values)
    ax.invert_yaxis()  # labels read top-to-bottom
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_xlabel(x_label)
    # Display in a window
    layout = [[sg.Canvas(key="-CANVAS-")]]
    window_histogram = sg.Window(title, layout, icon=encoded_logo, element_justification='center').Finalize()
    _draw_figure(window_histogram["-CANVAS-"].TKCanvas, fig)
    # Non-blocking window
    window_histogram.read(timeout=0)


def _display_word_cloud(narratives: str, words_in_cloud: int):
    """
    Display a Word Cloud based on the texts of the narratives.

    :param narratives: String consisting of all the narratives' texts
    :param words_in_cloud: Integer value indicating the number of words to be displayed
    :return: None
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
    _draw_figure(window_cloud["-CANVAS-"].TKCanvas, fig)
    # Non-blocking window
    window_cloud.read(timeout=0)


def _draw_figure(canvas, figure):
    """
    Routine to draw a matplotlib image on a tkinter canvas

    :param canvas: The 'canvas' object in PySimpleGUI
    :param figure: The matplotlib figure to be drawn
    :return: The tkinter canvas which will contain the figure
    """
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side="top", fill="both", expand=1)
    return figure_canvas_agg


def _output_words_in_csv(narratives: str, nouns_in_csv: int, verbs_in_csv: int, directory_name: str):
    """
    Output the top xx nouns and verbs in the narratives' texts to the files, <directory_name>/Nouns.csv
    and <directory_name>/Verbs.csv. The nouns, verbs and a count of their occurrences is returned.

    :param narratives: String consisting of all the narratives' texts
    :param nouns_in_csv: Integer value indicating the number of nouns to be output
    :param verbs_in_csv: Integer value indicating the number of verbs to be output
    :param directory_name: String indicating the base file name to which the nouns, verbs and
                           their frequencies are output
    :return: None
    """
    sorted_nouns, sorted_verbs = get_nouns_verbs(narratives)
    with open(f'{directory_name}/Nouns.csv', 'w', newline='\n') as noun_file:
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
