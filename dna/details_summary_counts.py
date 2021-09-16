# Processing to retrieve counts of the characteristics of the narrators or their stories,
# or related to nouns/verbs which are not 'known'/understood by the ontology
# Called by details_summary.py

import csv
import logging
import PySimpleGUI as sg

from database import query_database
from nlp import get_nouns_verbs
from utilities import new_line, encoded_logo, update_dictionary_count


def display_dates_events(narratives: str):
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
    # TODO: Get dates and events in narratives
    # try:
    #     hypotheses_results = query_database('select', query_hypotheses, store_name)
    #     number_hypotheses = 0
    #     if hypotheses_results:
    #         number_hypotheses = len(hypotheses_results)
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


def display_locations(narratives: str):
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
    # TODO: Get locations in narratives
    # try:
    #     hypotheses_results = query_database('select', query_hypotheses, store_name)
    #     number_hypotheses = 0
    #     if hypotheses_results:
    #         number_hypotheses = len(hypotheses_results)
    # except Exception as e:
    #     capture_error(f'Exception getting hypotheses details from {store_name}: {str(e)}', True)
    #     return
    window_locations = sg.Window('Display Locations Mentioned in Narratives',
                                 layout, icon=encoded_logo).Finalize()

    # Loop to process window "events"
    while True:
        event_locations, values = window_locations.read()
        if event_locations in (sg.WIN_CLOSED, 'End'):
            # If user closes window or clicks 'End'
            break

    # Done
    window_locations.close()
    return


def get_y_x_values(number_narrators: int, variable: str, query: str, store_name: str) -> (tuple, tuple):
    """
    Get the count of narrators by gender, birth country and birth year. Also provide counts where
    this info is not known.

    :param number_narrators: Total number of narrators
    :param variable: String indicating the name of the returned SPARQL query variable - either
                     'gender', 'year' or 'country'
    :param query: String holding the query to run to get the count
    :param store_name: String holding the database/data store name with the narratives and narrator details
    :return: Two tuples of integers - for the y and x axes of a horizontal bar chart ...
             The y axis is the list of genders, birth countries and birth years,
             and the x axis is the number of narrators
    """
    dictionary = dict()
    # Get count
    count_results = query_database('select', query, store_name)
    for binding in count_results:
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


def output_words_in_csv(narratives: str, nouns_in_csv: int, verbs_in_csv: int, directory_name: str):
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
    # TODO: Only report words with 'unknown' semantics
    with open(f'{directory_name}/Nouns.csv', 'w', newline=new_line) as noun_file:
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
