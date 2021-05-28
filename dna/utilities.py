import logging
import os
import PySimpleGUI as sg

from encoded_images import encoded_logo

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
resources_root = os.path.join(BASE_DIR, 'dna/resources/')

dna_prefix = 'urn:ontoinsights:dna:'

gender_dict = {'A': ':Agender', 'B': 'Bigender',
               'F': ':Female', 'M': ':Male'}

months = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
          'August', 'September', 'October', 'November', 'December']

with open('../dna/resources/country_names.txt', 'r') as names_file:
    countries = names_file.read().split('\n')


def add_to_dictionary_values(dictionary: dict, key: str, value):
    """
    Add the value for the specified key in the dictionary or create a dictionary entry for that key
    (where the value is a list).

    :param dictionary: The dictionary to be updated
    :param key: String holding the dictionary key
    :param value: The value to be added to the current list of values of the dictionary entry, or
                  a new list is created with the value
    :return: None
    """
    values = []
    if key in dictionary.keys():
        values = dictionary[key]
    values.append(value)
    dictionary[key] = values
    return


def capture_error(message: str, notify: bool):
    """
    Both log and popup the error message.

    :param message: The text to be logged/displayed
    :param notify: Boolean indicating that the text, 'Please notify a system administrator.'
                   should be added
    :return: None
    """
    logging.error(message)
    if notify:
        sg.popup_error(f'{message} \nPlease notify a system administrator.',
                       font=('Arial', 14), button_color='dark blue', icon=encoded_logo)
    else:
        sg.popup_error(message, font=('Arial', 14), button_color='dark blue', icon=encoded_logo)


def update_dictionary_count(dictionary: dict, key: str):
    """
    Add 1 to the specified dictionary key or create a dictionary entry for that key.

    :param dictionary: The dictionary to be updated
    :param key: String holding the dictionary key
    :return: None
    """
    if key in dictionary.keys():
        dictionary[key] = dictionary[key] + 1
    else:
        dictionary[key] = 1
    return
