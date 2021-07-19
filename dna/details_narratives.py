import logging
import matplotlib.pyplot as plt
import networkx as nx
import PySimpleGUI as sg

from encoded_images import encoded_logo
from database import query_database
from utilities import capture_error, draw_figure

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

    :param store_name: The database/data store name
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
                    _display_timeline(narrative_name, store_name)

    # Done
    window_narrative_list.close()
    return


def get_timeline_data(narrative_name: str, store_name: str) -> list:
    """
    Get all events in the knowledge graph (in the specified store/db) for the specified narrative title.

    :param narrative_name: String holding the narrative title/label
    :param store_name: String holding the database/store name from which the knowledge graph will be retrieved
    :return: An array of event dictionaries, in relative time order
    """
    # TODO
    return []


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


def _display_timeline(narrative_name: str, store_name: str):
    """
    Displays a timeline of the narrative events using NetworkX

    :param narrative_name: The name/label of the narrative
    :param store_name: The database/store that holds the narrative's knowledge graph
    :return: None (Timeline is displayed)
    """
    logging.info(f'Displaying narrative timeline for {narrative_name}')
    event_dicts = get_timeline_data(narrative_name, store_name)
    # TODO: Display pos/neg events on y axis and relative time on the x-axis
    fig, ax = plt.subplots(figsize=(10, 7))
    dig = nx.DiGraph()
    dig.add_nodes_from(["a", "b", "c", "d", "e", "f", "g", "h", "x"])
    dig.add_edges_from([("a", "b"), ("b", "c"), ("c", "d"), ("d", "e"), ("e", "f"), ("f", "g"), ("g", "h"), ("h", "x")])
    nx.draw(dig, with_labels=True)
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
