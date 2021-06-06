
from datetime import datetime
import logging
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.dates as mdates
import PySimpleGUI as sg

from encoded_images import encoded_logo
from database import query_database
from nlp import parse_narrative
from utilities import SPACE, add_to_dictionary_values, capture_error, draw_figure

query_narratives = 'prefix : <urn:ontoinsights:dna:> SELECT ?name ?narrator WHERE ' \
                   '{ ?narr a :Narrative ; rdfs:label ?name ; :subject ?narrator . }'

query_narrative_text = 'prefix : <urn:ontoinsights:dna:> SELECT ?text WHERE ' \
                       '{ ?narr a :Narrative ; rdfs:label "narrative_name" ; :text ?text . }'

query_metadata1 = 'prefix : <urn:ontoinsights:dna:> SELECT ?name WHERE ' \
                  '{ ?narrator rdfs:label ?name }'

query_metadata2 = 'prefix : <urn:ontoinsights:dna:> SELECT ?year ?country WHERE ' \
                  '{ ?birthEvent a :Birth ; :has_actor ?narrator . ' \
                  'OPTIONAL { ?birthEvent :has_time/:year ?year } ' \
                  'OPTIONAL { ?birthEvent :has_location/:country_name ?country } }'

query_metadata3 = 'prefix : <urn:ontoinsights:dna:> SELECT ?aspect WHERE ' \
                  '{ ?narrator :has_agent_aspect ?aspect }'


def display_narratives(store_name):
    """
    Display a list of all narratives in the specified store and allow selection of one.

    :param store_name The database/data store name
    :return: None (Narrative timeline is displayed)
    """
    logging.info('Narrative selection')
    # Create the GUI Window
    narrative_dict = dict()
    try:
        success, narrative_names = query_database('select', query_narratives, store_name)
        if success and 'results' in narrative_names.keys() and \
                'bindings' in narrative_names['results'].keys():
            for binding in narrative_names['results']['bindings']:
                narrative_dict[binding['name']['value']] = binding['narrator']['value'].split(':')[-1]
        else:
            sg.popup_error(f'No narratives are defined in {store_name}. '
                           f'Narrative timelines cannot be displayed.',
                           font=('Arial', 14), button_color='dark blue', icon=encoded_logo)
    except Exception as e:
        capture_error(f'Exception getting narrative names from {store_name}: {str(e)}', True)
        return
    if not len(narrative_dict):
        sg.popup_ok('No narratives were found in the store. '
                    'Please ingest one or more using the "Load Narratives" button.', font=('Arial', 14),
                    button_color='dark blue', icon=encoded_logo)
        return
    else:
        narrative_list = list(narrative_dict.keys())

    # Setup the PySimpleGUI window
    sg.theme('Material2')
    layout = [[sg.Text("Select a narrative and then press 'OK'.", font=('Arial', 16))],
              [sg.Text("To exit without making a selection, press 'End' or close the window.",
                       font=('Arial', 16))],
              [sg.Listbox(narrative_list, size=(30, 10), key='narrative_list', font=('Arial', 14),
                          background_color='#fafafa', highlight_background_color='light grey',
                          highlight_text_color='black', text_color='black')],
              [sg.Text()],
              [sg.Button('OK', button_color='dark blue', font=('Arial', 14), size=(5, 1)),
               sg.Button('End', button_color='dark blue', font=('Arial', 14), size=(5, 1))]]

    # Create the GUI Window
    window_narrative_list = sg.Window('Select Narrative', layout, icon=encoded_logo).Finalize()

    # Event Loop to process window "events"
    while True:
        event_narrative_list, values = window_narrative_list.read()
        if event_narrative_list in (sg.WIN_CLOSED, 'End'):
            # If user closes window or clicks 'End'
            break
        if event_narrative_list == 'OK':
            if len(values['narrative_list']) != 1:
                sg.popup_error('Either no narrative was selected, or more than one was selected.',
                               font=('Arial', 14), button_color='dark blue', icon=encoded_logo)
            else:
                narrative_name = values['narrative_list'][0]
                narrative_text = ''
                try:
                    success1, narrative_text_results = query_database(
                        'select', query_narrative_text.replace('narrative_name', narrative_name),
                        store_name)
                    if success1 and 'results' in narrative_text_results.keys() and \
                            'bindings' in narrative_text_results['results'].keys():
                        narrative_text = narrative_text_results['results']['bindings'][0]['text']['value']
                    else:
                        sg.popup_error(f'Error retrieving the text for the narrative, {narrative_name}, '
                                       f'from {store_name}. The narrative details cannot be displayed.',
                                       font=('Arial', 14), button_color='dark blue', icon=encoded_logo)
                except Exception as e:
                    capture_error(f'Exception getting narrative text for {narrative_name} '
                                  f'from {store_name}: {str(e)}', True)
                    return
                if narrative_text:
                    _display_metadata(narrative_name, narrative_dict[narrative_name],
                                      narrative_text, store_name)
                    _display_timeline(narrative_name, narrative_text)

    # Done
    window_narrative_list.close()
    return


def get_timeline_data(sent_dict: dict, key_date: str, orig_dates: set, current_loc: str,
                      date_text_dict: dict) -> (str, str):
    """
    Temporary function to assemble timeline data. Will ultimately create RDF triples of events
    and be moved to another module
    """
    # TODO: Code is complicated and not optimized
    # TODO: Retrieve from DB after ingest adds KG
    current_date = ''
    subjects = []
    for subject_dict in sent_dict['subjects']:
        subject_text = subject_dict['subject_text']
        if 'subject_preps' in subject_dict.keys():
            for subject_prep_dict in subject_dict['subject_preps']:
                subject_text += f" {subject_prep_dict['subject_prep_text']}"
                for subject_prep_obj_dict in subject_prep_dict['subject_prep_objects']:
                    subject_text += f" {subject_prep_obj_dict['subject_prep_object']}"
        subjects.append(subject_text)
    for verb_dict in sent_dict['verbs']:
        verb_text = verb_dict['verb_text']
        if 'preps' in verb_dict.keys():
            for prep_dict in verb_dict['preps']:
                prep_text = prep_dict['prep_text']
                count = 0
                for prep_detail_dict in prep_dict['prep_details']:
                    prep_type = prep_detail_dict['prep_detail_type']
                    if prep_text.lower() in ('in', 'on') and prep_type == 'DATE':
                        current_date = prep_detail_dict['prep_detail_text']
                    elif prep_text.lower() == 'after' and prep_type == 'EVENT' \
                            and prep_detail_dict['prep_detail_text'] == 'World War II':
                        # TODO: Look up event date and signal 'After' that date
                        current_date = '1945'
                    elif prep_text.lower() in ('in', 'to', 'from') and \
                            (prep_type in ('GPE', 'LOC') or 'ghetto' in prep_detail_dict['prep_detail_text']):
                        current_loc = prep_detail_dict['prep_detail_text']
                    else:
                        count += 1
                        if prep_text.lower() in verb_text:
                            space = SPACE
                            if count > 1:
                                space = ', '
                            verb_text += space + prep_detail_dict['prep_detail_text']
                        else:
                            verb_text += f" {prep_text.lower()} {prep_detail_dict['prep_detail_text']}"
                    # TODO with aid of
        if 'verb_aux' in verb_dict.keys():
            for verb_aux_dict in verb_dict['verb_aux']:
                verb_text = verb_aux_dict['verb_aux_text'] + ' ' + verb_text
                # TODO: 'verb_aux_preps' in verb_aux_dict.keys() ?
        if 'verb_xcomp' in verb_dict.keys():
            for verb_xcomp_dict in verb_dict['verb_xcomp']:
                verb_text += ' ' + verb_xcomp_dict['verb_xcomp_text']
                if 'verb_xcomp_preps' in verb_xcomp_dict.keys():
                    prep_objects = []
                    for prep_dict in verb_xcomp_dict['verb_xcomp_preps']:
                        prep_text = prep_dict['verb_xcomp_prep_text']
                        verb_text += ' ' + prep_text
                        if 'verb_xcomp_prep_objects' in prep_dict.keys():
                            for prep_object_dict in prep_dict['verb_xcomp_prep_objects']:
                                prep_object = prep_object_dict['verb_xcomp_prep_object']
                                prep_type = prep_object_dict['verb_xcomp_prep_object_type']
                                if prep_text.lower() in ('in', 'on') and prep_type == 'DATE':
                                    current_date = prep_object
                                elif prep_text.lower() == 'after' and prep_type == 'EVENT' \
                                        and prep_object == 'World War II':
                                    # TODO Look up event date and signal 'After' that date
                                    current_date = '1945'
                                elif prep_text.lower() in ('in', 'to', 'from') and \
                                        (prep_type in ('GPE', 'LOC') or 'ghetto' in prep_object):
                                    current_loc = prep_object
                                else:
                                    prep_objects.append(prep_object)
                    if prep_objects:
                        verb_text += ' ' + ', '.join(prep_objects)
        objects = []
        if 'objects' in verb_dict.keys():
            for object_dict in verb_dict['objects']:
                object_text = object_dict['object_text']
                if 'object_preps' in object_dict.keys():
                    for prep_dict in object_dict['object_preps']:
                        object_text += ' ' + prep_dict['object_prep_text']
                        for prep_detail in prep_dict['object_prep_objects']:
                            object_text += ' ' + prep_detail['object_prep_object']
                objects.append(object_text)
        if current_date:
            date_texts = current_date.split(' ')
            for date_text in date_texts:
                if date_text.isnumeric() and int(date_text) > 1000:
                    orig_dates.add(date_text)
                key_date = date_text
        text = f'Loc: {current_loc}\n'
        if not (len(subjects) == 1 and subjects[0] == 'I'):
            text += ', '.join(subjects) + ' ' + verb_text
        else:
            text += verb_text
        if objects:
            text += ' ' + ', '.join(objects)
        final_text = text + '\n'
        add_to_dictionary_values(date_text_dict, key_date, final_text, str)
    return key_date, current_loc


# Functions internal to the module
def _display_metadata(narrative_name: str, narrator: str, narrative_text: str, store_name: str):
    """

    """
    logging.info(f'Displaying metadata and text for {narrative_name}')
    narrator_names = []
    metadata_dict = dict()
    try:
        success1, metadata1_results = query_database(
            'select', query_metadata1.replace("?narrator", f':{narrator}'), store_name)
        if success1 and 'results' in metadata1_results.keys() and \
                'bindings' in metadata1_results['results'].keys():
            for binding in metadata1_results['results']['bindings']:
                narrator_names.append(binding['name']['value'])
        success2, metadata2_results = query_database(
            'select', query_metadata2.replace("?narrator", f':{narrator}'), store_name)
        if success2 and 'results' in metadata2_results.keys() and \
                'bindings' in metadata1_results['results'].keys():
            if len(metadata2_results['results']['bindings']):
                for binding in metadata2_results['results']['bindings']:
                    # There should only be one result / one set of metadata for the narrator
                    if 'country' in binding.keys():
                        metadata_dict['country'] = binding['country']['value']
                    else:
                        metadata_dict['country'] = 'Unknown'
                    if 'year' in binding.keys():
                        metadata_dict['year'] = binding['year']['value']
                    else:
                        metadata_dict['year'] = 'Unknown'
            else:
                metadata_dict['country'] = 'Unknown'
                metadata_dict['year'] = 'Unknown'
        success3, metadata3_results = query_database(
            'select', query_metadata3.replace("?narrator", f':{narrator}'), store_name)
        if success3 and 'results' in metadata3_results.keys() and \
                'bindings' in metadata1_results['results'].keys():
            if len(metadata3_results['results']['bindings']):
                gender = ''
                for binding in metadata3_results['results']['bindings']:
                    aspect = binding['aspect']['value'].split(':')[-1]
                    if aspect in ('Agender', 'Bigender', 'Female', 'Male'):
                        gender = aspect
                if gender:
                    metadata_dict['gender'] = gender
                else:
                    metadata_dict['gender'] = 'Unknown'
            else:
                metadata_dict['country'] = 'Unknown'
                metadata_dict['year'] = 'Unknown'
        if not (success1 or success2 or success3):
            sg.popup_error(f'Limited or no metadata was found for the narrator, {narrator.split(":")[-1]}. '
                           f'At a minimum, the narrative text will be displayed.',
                           font=('Arial', 14), button_color='dark blue', icon=encoded_logo)
    except Exception as e:
        capture_error(f'Exception getting narrator details from {store_name}: {str(e)}', True)
        return

    # Setup the PySimpleGUI window
    sg.theme('Material2')
    layout = [[sg.Text("Narrative Title:", font=('Arial', 16)),
               sg.Text(narrative_name, font=('Arial', 16))],
              [sg.Text()],
              [sg.Text("Narrator Names:", font=('Arial', 16)),
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
    # window_metadata_list['narr_text'].TKOut.output.config(wrap='word')
    window_metadata_list.FindElement('narr_text').Update(narrative_text)
    window_metadata_list.FindElement('narr_text').Widget.configure()

    window_metadata_list.read(timeout=0)
    return


def _display_timeline(narrative_name: str, narrative_text: str):
    """
    Displays a timeline of the narrative events.

    :param narrative_name The name/label of the narrative
    :param narrative_text The narrative text (which will not be needed when the event graph is created
                          in load.py)
    :return None (Timeline is displayed)
    """
    logging.info(f'Displaying narrative timeline for {narrative_name}')
    # TODO: Move following processing to load.py and change to retrieving from DB
    sentences = parse_narrative(narrative_text)
    key_date = ''
    current_loc = ''
    orig_dates = set()
    date_text_dict = dict()
    for sent_dict in sentences:
        key_date, current_loc = \
            get_timeline_data(sent_dict, key_date, orig_dates, current_loc, date_text_dict)
    # TODO: What if there are no dates?
    # Sort the dates and simplify the text
    orig_dates = sorted(orig_dates)
    names = []
    for orig_date in orig_dates:
        date_text = ''
        loc_text = date_text_dict[orig_date][0].split('Loc: ')[1].split('\n')[0]
        for text in date_text_dict[orig_date]:
            text = text.replace(f'Loc: {loc_text}\n', '')
            date_text += text
        names.append(f'Loc: {loc_text}\n{date_text}')
    # For matplotlib timeline, need datetime formatting
    dates = [datetime.strptime(d, "%Y") for d in orig_dates]
    # Create a stem plot with some variation in levels as to distinguish close-by events.
    # Add markers on the baseline for visual emphasis
    # For each event, add a text label via annotate, which is offset in units of points from the tip of the event line
    levels = np.tile([-5, 5, -3, 3, -1, 1],
                     int(np.ceil(len(dates) / 6)))[:len(dates)]
    # Create figure and plot a stem plot with the date
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.set(title="Narrative Timeline")
    ax.vlines(dates, 0, levels, color="tab:red")  # The vertical stems
    ax.plot(dates, np.zeros_like(dates), "-o",
            color="k", markerfacecolor="w")       # Baseline and markers on it
    # Annotate lines
    for d, l, r in zip(dates, levels, names):
        ax.annotate(r, xy=(d, l),
                    xytext=(-2, np.sign(l) * 3), textcoords="offset points",
                    horizontalalignment="right",
                    verticalalignment="bottom" if l > 0 else "top", fontsize='x-small')
    # Format x-axis with yearly intervals
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right", fontsize='small')
    # Remove y axis and spines
    ax.yaxis.set_visible(False)
    ax.spines[["left", "top", "right"]].set_visible(False)
    ax.margins(y=0.1)
    plt.tight_layout()
    # Display in a window
    layout = [[sg.Canvas(key="-CANVAS-")]]
    window_timeline = sg.Window("Narrative Timeline", layout,
                                icon=encoded_logo, element_justification='center').Finalize()
    draw_figure(window_timeline["-CANVAS-"].TKCanvas, fig)
    window_timeline.Maximize()
    # Non-blocking window
    window_timeline.read(timeout=0)
    return
