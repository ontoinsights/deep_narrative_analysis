# Processing to display a window to select a narrative for display as a timeline, which in turn
# can show a detailed event graph (for the events in the timeline for a specific month and year)
# Uses the functions in details_narrative_timeline to display narrative metadata and an event timeline

import PySimpleGUI as sg

from database import query_database
from details_narrative_timeline import display_metadata, display_timeline
from utilities import capture_error, dark_blue, encoded_logo

query_narratives = 'prefix : <urn:ontoinsights:dna:> SELECT ?name ?narrator WHERE ' \
                   '{ ?narr a :Narrative ; rdfs:label ?name ; :has_author ?narrator }'

query_events_in_range = 'prefix : <urn:ontoinsights:dna:> SELECT distinct ?event ?label ?year ?month ?day ' \
                        'FROM <urn:narr_graph> FROM <tag:stardog:api:context:default> WHERE ' \
                        '{ ?event a ?type ; rdfs:label ?label ; :sentence_offset ?offset . ' \
                        '?type rdfs:subClassOf* :EventAndState . ' \
                        '{ { ?event :has_time ?time } UNION { ?event :has_beginning ?time } UNION ' \
                        '{ ?event :has_earliest_beginning ?time } UNION { ?event :has_end ?time } UNION ' \
                        '{ ?event :has_latest_end ?time } } ?time :year ?year . ' \
                        'FILTER(?year >= beginning_year) . FILTER(?year <= ending_year) . ' \
                        'OPTIONAL { ?time :month_of_year ?month . OPTIONAL { ?time :day_of_month ?day } } } ' \
                        'ORDER BY ?year ?month ?day ?offset '

query_events = 'prefix : <urn:ontoinsights:dna:> SELECT distinct ?event ?label ?year ?month ?day ' \
               'FROM <urn:narr_graph> FROM <tag:stardog:api:context:default> WHERE ' \
               '{ ?event a ?type ; rdfs:label ?label ; :sentence_offset ?offset . ' \
               '?type rdfs:subClassOf* :EventAndState . ' \
               '{ { ?event :has_time ?time } UNION { ?event :has_beginning ?time } UNION ' \
               '{ ?event :has_earliest_beginning ?time } UNION { ?event :has_end ?time } UNION ' \
               '{ ?event :has_latest_end ?time } } ?time :year ?year . ' \
               'OPTIONAL { ?time :month_of_year ?month . OPTIONAL { ?time :day_of_month ?day } } } ' \
               'ORDER BY ?year ?month ?day ?offset'


def display_narratives(store_name: str):
    """
    Display a list of all narratives in the specified store (plus the domain timeline, if applicable)
    and allow selection of one. Also allow a year range to be defined for events to display. If no year
    range is specified, then all events are displayed.

    :param store_name: The database/data store name
    :returns: None (Narrative timeline is displayed)
    """
    # Get the list of narratives
    narrative_dict = get_narratives(store_name)
    if len(narrative_dict):
        narrative_list = [narr.replace('_', '') for narr in narrative_dict.keys()]
    else:
        return

    # Define the PySimpleGUI window
    sg.theme('Material2')
    # TODO: Remove the window's reference to the domain timeline if not relevant for a use case
    layout = [[sg.Text("Select a narrative or 'Domain Events'.", font=('Arial', 16))],
              [sg.Text(f"Press 'OK' to display the narrative or domain timeline, or press "
                       f"'End' (or close the window) to exit.",
                       font=('Arial', 16))],
              [sg.Listbox(narrative_list, size=(30, 10), key='narrative_list', font=('Arial', 14),
                          background_color='#fafafa', highlight_background_color='light grey',
                          highlight_text_color='black', text_color='black')],
              [sg.Text(f"If there is overlapping text, restrict the timeline to specific years.",
                       font=('Arial', 16))],
              [sg.Text("Beginning year:", font=('Arial', 16)),
               sg.InputText(text_color='black', background_color='#ede8e8', size=(8, 1),
                            font=('Arial', 16), key='begin_year', do_not_clear=True)],
              [sg.Text("Ending year:   ", font=('Arial', 16)),
               sg.InputText(text_color='black', background_color='#ede8e8', size=(8, 1),
                            font=('Arial', 16), key='end_year', do_not_clear=True)],
              [sg.Text()],
              [sg.Button('OK', button_color=dark_blue, font=('Arial', 14), size=(5, 1)),
               sg.Button('End', button_color=dark_blue, font=('Arial', 14), size=(5, 1))]]

    # Create the GUI Window
    window_narrative_list = sg.Window('Select Narrative or Domain Timeline', layout, icon=encoded_logo).Finalize()
    window_narrative_list['begin_year'].Widget.config(insertbackground='black')
    window_narrative_list['end_year'].Widget.config(insertbackground='black')

    # Loop to process window "events"
    while True:
        event_narrative_list, values = window_narrative_list.read()
        if event_narrative_list in (sg.WIN_CLOSED, 'End'):
            # If user closes window or clicks 'End'
            break
        if event_narrative_list == 'OK':
            ok_to_continue = True
            if len(values['narrative_list']) != 1:
                ok_to_continue = False
                sg.popup_error('Either nothing was selected, or more than one selection was made.',
                               font=('Arial', 14), button_color=dark_blue, icon=encoded_logo)
            begin_year = values['begin_year']
            end_year = values['end_year']
            if (begin_year and not end_year) or (end_year and not begin_year) or \
                    (begin_year and end_year and int(begin_year) > int(end_year)):
                ok_to_continue = False
                sg.popup_error('If a year range is specified, select both a beginning and ending year, '
                               'and ensure that the beginning year is <= the ending year.',
                               font=('Arial', 14), button_color=dark_blue, icon=encoded_logo)
            if ok_to_continue:
                narrative_name = values['narrative_list'][0]
                if narrative_name != 'Domain Events':
                    # Display narrator metadata and story text
                    display_metadata(narrative_name, narrative_dict[narrative_name], store_name)
                # Get list of events, sorted by time
                try:
                    if begin_year:
                        query = query_events_in_range.\
                            replace('narr_graph', narrative_name.replace(' ', '_')).\
                            replace('beginning_year', begin_year).\
                            replace('ending_year', end_year)
                        events_list = query_database('select', query, store_name)
                    else:
                        events_list = query_database(
                            'select',
                            query_events.replace('narr_graph', narrative_name.replace(' ', '_')),
                            store_name)
                    if not events_list:
                        sg.popup_error(f'No events are defined for the narrative, {narrative_name}. '
                                       f'Narrative timeline and graph cannot be displayed.',
                                       font=('Arial', 14), button_color=dark_blue, icon=encoded_logo)
                except Exception as e:
                    capture_error(
                        f'Exception getting events for {narrative_name} in the {store_name}: {str(e)}', True)
                    return
                # Display timeline
                display_timeline(narrative_name, events_list, store_name)
                break

    # Done
    window_narrative_list.close()


def get_narratives(store_name: str) -> dict:
    """
    Query the specified database for ingested narratives.

    :param store_name: The database/data store name
    :returns: A dictionary with keys = narrative title and values = narrator name
    """
    narrative_dict = dict()
    try:
        narrative_names = query_database('select', query_narratives, store_name)
        if narrative_names:
            for binding in narrative_names:
                narrative_dict[binding['name']['value']] = binding['narrator']['value'].split(':')[-1]
    except Exception as e:
        capture_error(f'Exception getting narrative names from {store_name}: {str(e)}', True)
        return dict()
    if not len(narrative_dict):
        sg.popup_ok(f'No narratives were found in {store_name}. '
                    f'Please select a different store or ingest one or more using the "Load Narratives" button.',
                    font=('Arial', 14), button_color=dark_blue, icon=encoded_logo)
    return narrative_dict
