import logging
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import PySimpleGUI as sg

from encoded_images import encoded_logo

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
resources_root = os.path.join(BASE_DIR, 'dna/resources/')

EMPTY_STRING = ''
SPACE = ' '
NEW_LINE = '\n'
DOUBLE_NEW_LINE = '\n\n'

dna_prefix = 'urn:ontoinsights:dna:'

gender_dict = {'A': ':Agender', 'B': 'Bigender',
               'F': ':Female', 'M': ':Male'}

months = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
          'August', 'September', 'October', 'November', 'December']

with open('../dna/resources/country_names.txt', 'r') as names_file:
    countries = names_file.read().split('\n')


def add_to_dictionary_values(dictionary: dict, key: str, value, value_type):
    """
    Add the value (cast using the value_type parameter) for the specified key in the dictionary
    if that key exists, or create a new dictionary entry for the key (where the value is a list).

    :param dictionary: The dictionary to be updated
    :param key: String holding the dictionary key
    :param value: The value to be added to the current list of values of the dictionary entry, or
                  a new list is created with the value
    :param value_type: The type of the value
    :return: None (Dictionary is updated)
    """
    values = []
    if key in dictionary.keys():
        values = dictionary[key]
    values.append(value_type(value))
    dictionary[key] = values
    return


def capture_error(message: str, notify: bool):
    """
    Both log and popup the error message.

    :param message: The text to be logged/displayed
    :param notify: Boolean indicating that the text, 'Please notify a system administrator.'
                   should be added
    :return: None (Message is logged and displayed)
    """
    logging.error(message)
    if notify:
        sg.popup_error(f'{message} \nPlease notify a system administrator.',
                       font=('Arial', 14), button_color='dark blue', icon=encoded_logo)
    else:
        sg.popup_error(message, font=('Arial', 14), button_color='dark blue', icon=encoded_logo)


def draw_figure(canvas, figure):
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


def update_dictionary_count(dictionary: dict, key: str):
    """
    Add 1 to the specified dictionary key or create a dictionary entry for that key.

    :param dictionary: The dictionary to be updated
    :param key: String holding the dictionary key
    :return: None (Dictionary is updated)
    """
    if key in dictionary.keys():
        dictionary[key] = dictionary[key] + 1
    else:
        dictionary[key] = 1
    return
