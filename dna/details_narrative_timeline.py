# Processing to create 2 windows - 1) metadata details and 2) an event timeline for the
# selected narrative (a narrative or the domain events are selected in details_narrative.py)
# Called by details_narrative.py
# Uses the functions in details_narrative_graph to display a graph of events for a particular month and year

import logging
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import PySimpleGUI as sg

from datetime import datetime
from database import query_database
from details_narrative_graph import display_graph
from utilities import empty_string, add_to_dictionary_values, capture_error, encoded_logo
from utilities_matplotlib import draw_figure_with_toolbar

query_narrative_text = 'prefix : <urn:ontoinsights:dna:> SELECT ?text WHERE ' \
                       '{ ?narr a :Narrative ; rdfs:label "narrative_name" ; :text ?text . }'

query_metadata1 = 'prefix : <urn:ontoinsights:dna:> SELECT ?name WHERE ' \
                  '{ ?narrator rdfs:label ?name }'

query_metadata2 = 'prefix : <urn:ontoinsights:dna:> SELECT ?year ?country WHERE ' \
                  '{ ?birthEvent a :Birth ; :has_affected_agent ?narrator . ' \
                  'OPTIONAL { ?birthEvent :has_time/:year ?year } ' \
                  'OPTIONAL { ?birthEvent :has_location/:country_name ?country } }'

query_metadata3 = 'prefix : <urn:ontoinsights:dna:> SELECT ?aspect WHERE ' \
                  '{ ?narrator :has_agent_aspect ?aspect }'


def display_metadata(narrative_name: str, narrator: str, store_name: str):
    """
    Display the metadata for a narrator (such as gender and birth year) and the narrative text.

    :param narrative_name: The narrative title
    :param narrator: The URI with the narrator's metadata
    :param store_name: The database/store to be queried for data
    :return None
    """
    logging.info(f'Displaying metadata and text for {narrative_name}')
    narrator_names = []
    metadata_dict = dict()
    try:
        narrative_text_results = query_database(
            'select', query_narrative_text.replace('narrative_name', narrative_name), store_name)
        if narrative_text_results:
            narrative_text = narrative_text_results[0]['text']['value']
        else:
            narrative_text = 'Error retrieving the narrative text. It cannot be displayed.'
        metadata1_results = query_database(
            'select', query_metadata1.replace("?narrator", f':{narrator}'), store_name)
        for binding in metadata1_results:
            narrator_names.append(binding['name']['value'])
        metadata2_results = query_database(
            'select', query_metadata2.replace("?narrator", f':{narrator}'), store_name)
        if metadata2_results:
            for binding in metadata2_results:
                # There should only be one result / one set of metadata for the narrator
                metadata_dict['country'] = binding['country']['value'] if 'country' in binding.keys() else 'Unknown'
                metadata_dict['year'] = binding['year']['value'] if 'year' in binding.keys() else 'Unknown'
        else:
            metadata_dict['country'] = 'Unknown'
            metadata_dict['year'] = 'Unknown'
        metadata3_results = query_database(
            'select', query_metadata3.replace("?narrator", f':{narrator}'), store_name)
        if metadata3_results:
            gender = empty_string
            for binding in metadata3_results:
                aspect = binding['aspect']['value'].split(':')[-1]
                if aspect in ('Agender', 'Bigender', 'Female', 'Male'):
                    gender = aspect
            if gender:
                metadata_dict['gender'] = gender
            else:
                metadata_dict['gender'] = 'Unknown'
        else:
            metadata_dict['gender'] = 'Unknown'
        if not (metadata1_results or metadata2_results or metadata3_results):
            sg.popup_error(f'Limited or no metadata was found for the narrator, {narrator.split(":")[-1]}. '
                           f'The narrative text will be displayed, if available.',
                           font=('Arial', 14), button_color='dark blue', icon=encoded_logo)
    except Exception as e:
        capture_error(f'Exception getting narrator details from {store_name}: {str(e)}', True)
        return

    # Setup the PySimpleGUI window
    sg.theme('Material2')
    layout = [[sg.Text("Narrative Title:", font=('Arial', 16)),
               sg.Text(narrative_name, font=('Arial', 16))],
              [sg.Text()],
              [sg.Text("Narrator:", font=('Arial', 16)),
               sg.Text(', '.join(narrator_names), font=('Arial', 16))],
              [sg.Text()],
              [sg.Text("Narrator Gender:", font=('Arial', 16)),
               sg.Text(metadata_dict['gender'], font=('Arial', 16))],
              [sg.Text("Narrator Birth Country:", font=('Arial', 16)),
               sg.Text(metadata_dict['country'], font=('Arial', 16))],
              [sg.Text("Narrator Birth Year:", font=('Arial', 16)),
               sg.Text(metadata_dict['year'], font=('Arial', 16))],
              [sg.Text()],
              [sg.Text("Text:", font=('Arial', 16))],
              [sg.Multiline(key='narr_text', font=('Arial', 14), size=(75, 30), auto_refresh=True,
                            autoscroll=True, background_color='#fafafa', text_color='black', write_only=True)],
              [sg.Text()],
              [sg.Text("To exit, close the window.", font=('Arial', 16))]]
    window_metadata_list = sg.Window(f'Metadata for {narrative_name}', layout, icon=encoded_logo).Finalize()
    window_metadata_list.find_element('narr_text', True).Update(narrative_text)
    window_metadata_list.find_element('narr_text', True).Widget.configure()
    # Non-blocking window
    window_metadata_list.read(timeout=0)
    return


def display_timeline(narrative_name: str, events_bindings: dict, store_name: str):
    """
    Displays a timeline of the narrative or domain events using a matplotlib stem plot.

    :param narrative_name: The name/label of the narrative
    :param events_bindings: The binding results for the query, query_timeline_events, for the
                            specified narrative
    :param store_name: The database/store to be queried for data
    :return: None (timeline is displayed)
    """
    logging.info(f'Displaying narrative timeline for {narrative_name}')
    event_dict = dict()
    for binding in events_bindings:
        if 'month' in binding.keys():
            dict_key = f'{binding["year"]["value"]}-{binding["month"]["value"]}'
        else:
            dict_key = f'{binding["year"]["value"]}-01'
        add_to_dictionary_values(event_dict, dict_key, binding['label']['value'], str)

    dates = []
    texts = []
    for key, value in event_dict.items():
        dates.append(key)
        texts.append('\n'.join(value))
    # For matplotlib timeline, need datetime formatting
    plot_dates = [datetime.strptime(d, "%Y-%m") for d in dates]
    # Create a stem plot with some variation in levels as to distinguish close-by events.
    # Add markers on the baseline with dates
    # For each event, add a text label via annotate, which is offset from the tip of the event line
    levels = np.tile([-10, 10, -6, 6, -2, 2, -8, 8, -4, 4, -1, 1, -9, 9, -5, 5],
                     int(np.ceil(len(plot_dates) / 6)))[:len(plot_dates)]
    # Create figure and plot a stem plot with the dates
    fig, ax = plt.subplots(figsize=(12, 8))
    dpi = fig.get_dpi()
    fig.set_size_inches(808 * 2 / float(dpi), 808 / float(dpi))
    ax.set(title=narrative_name)
    ax.vlines(plot_dates, 0, levels, color="tab:red")  # The vertical stems
    ax.plot(plot_dates, np.zeros_like(plot_dates), "-o",
            color="k", markerfacecolor="w")  # Baseline and markers on it
    # Annotate lines
    for d, l, r in zip(plot_dates, levels, texts):
        ax.annotate(r, xy=(d, l),
                    xytext=(-2, np.sign(l) * 3), textcoords="offset points",
                    horizontalalignment="right",
                    verticalalignment="bottom" if l > 0 else "top", fontsize='x-small')
    # Format x-axis with yearly intervals
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right", fontsize='small')
    # Remove y axis and spines
    ax.yaxis.set_visible(False)
    ax.spines[["left", "top", "right"]].set_visible(False)
    ax.margins(y=0.1)
    plt.tight_layout(pad=0.05, h_pad=0.05, w_pad=0.05)
    plt.show()

    # Display in a window with matplotlib interactive controls
    # TODO: Add checkboxes to limit relationships that are displayed?
    layout = [[sg.Text('Display Event Network for Date (YYYY-mm): ', font=('Arial', 14)),
               sg.InputText(text_color='black', background_color='#ede8e8', size=(10, 1),
                            font=('Arial', 14), key='event_date', do_not_clear=True),
               sg.Button('Graph', button_color='dark blue', font=('Arial', 14), size=(6, 1))],
              [sg.Text('Controls:', font=('Arial', 14)),
               sg.Canvas(key='controls_cv')],
              [sg.Column(layout=[[sg.Canvas(key='fig_cv', size=(800 * 2, 800))]], pad=(0, 0))]]
    window_timeline = sg.Window('Timeline', layout, icon=encoded_logo, element_justification='center',
                                resizable=True).Finalize()
    window_timeline['event_date'].Widget.config(insertbackground='black')
    draw_figure_with_toolbar(window_timeline['fig_cv'].TKCanvas, fig,
                             window_timeline['controls_cv'].TKCanvas)
    window_timeline.Maximize()
    while True:
        event, values = window_timeline.read()
        if event == 'Graph':
            display_graph(narrative_name, events_bindings, store_name, values['event_date'])
        if event == sg.WIN_CLOSED:
            break
    window_timeline.close()
    return
