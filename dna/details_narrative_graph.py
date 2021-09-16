# Processing to create a window to display an event graph for the selected narrative
# (a narrative or the domain events are selected in details_narrative.py)
# Called by details_narrative.py

import logging
import matplotlib.pyplot as plt
import networkx as nx
import PySimpleGUI as sg

from database import query_database
from utilities import empty_string, capture_error, encoded_logo
from utilities_matplotlib import draw_figure_with_toolbar


query_graph_individuals = 'prefix : <urn:ontoinsights:dna:> SELECT distinct ?pred ?obj ?obj_label ?e_type ' \
                          '?a_type ?t_type ?r_type FROM <urn:narr_graph> FROM <tag:stardog:api:context:default> ' \
                          'WHERE { VALUES ?pred { rdf:type rdfs:label :has_agent :has_holder :has_active_agent ' \
                          ':has_affected_agent :has_location :has_origin :has_destination :has_time :has_end ' \
                          ':has_beginning :has_topic :has_component :cause :enable :prevent } <uri> ?pred ?obj . ' \
                          'OPTIONAL { ?obj a ?obj_type ; rdfs:label ?obj_label .' \
                          'OPTIONAL { { ?obj_type rdfs:subClassOf* :EventAndState . BIND("Event" as ?e_type) } ' \
                          'UNION { { { ?obj_type rdfs:subClassOf* :Agent } UNION { ?obj_type rdfs:subClassOf* ' \
                          ':Location } } BIND("Agent" as ?a_type) } ' \
                          'UNION { ?obj_type rdfs:subClassOf* :Time . BIND("Time" as ?t_type) } ' \
                          'UNION { ?obj_type rdfs:subClassOf* :Resource . BIND("Resource" as ?r_type) } } } }'

year_list = list(range(1933, 1946))  # TODO: Check if dates in range?


def display_graph(narrative_name: str, events_bindings: dict, store_name: str, event_date: str):
    """
    Displays a graph of the narrative events using NetworkX.

    :param narrative_name: The name/label of the narrative
    :param events_bindings: The binding results for the query, query_timeline_events, for the
                            specified narrative
    :param store_name: The database/store that holds the narrative's knowledge graph
    :param event_date: A string in YYYY-mm format indicating which events (events with times in that
                       month) should be shown in the graph
    :return: None (graph is displayed)
    """
    logging.info(f'Displaying narrative graph for {narrative_name}')
    # Get the details (predicates and objects) for each event individual
    node_set = set()
    edges = []
    edge_label_dict = dict()
    for binding in events_bindings:
        event_uri = binding['event']['value']
        event_name = event_uri.split(':')[-1]
        event_time = binding['year']['value']
        if 'month' in binding.keys():
            month = binding['month']['value']
            if len(month) == 1:
                month = f'0{month}'
            event_time = f'{event_time}-{month}'
        else:
            event_time = f'{event_time}-01'
        if event_time != event_date:
            continue
        event_tuples = get_event_data(narrative_name, store_name, event_uri)
        for event_tuple in event_tuples:
            if len(event_tuple) == 4:
                pred, obj, obj_label, obj_type = event_tuple
            else:
                pred, obj = event_tuple
                if ':dna:' in obj:
                    obj_label = obj.split(':')[-1]
                    obj_type = 'Class'
                else:
                    obj_label = obj
                    obj_type = empty_string
            if '#' in pred:
                pred_name = pred.split('#')[-1]
            else:
                pred_name = pred.split(':')[-1]
            if obj_type:
                if obj_type == 'Event':
                    obj_node_name = f'evt{obj_label}'
                elif obj_type == 'Class':
                    obj_node_name = f'cls{obj_label}'
                else:
                    obj_node_name = f'uri{obj_label}'
            else:
                obj_node_name = obj_label
            edges.append((event_name, obj_label))
            edge_label_dict[(event_name, obj_label)] = pred_name
            node_set.add(f'evt{event_name}')
            node_set.add(obj_node_name)

    # Associate the color red with 'bad' Events/States and green with 'good' ones
    # Associate the color white with class types, blue with other URIs and orange with strings/literals
    nodes = []
    node_colors = []
    node_sizes = []
    for node in node_set:
        if node.startswith('evt'):
            nodes.append(node[3:])
            node_colors.append('red')
            node_sizes.append(500)
        elif node.startswith('cls'):
            nodes.append(node[3:])
            node_colors.append('purple')
            node_sizes.append(200)
        elif node.startswith('uri'):
            nodes.append(node[3:])
            node_colors.append('blue')
            node_sizes.append(350)
        else:
            nodes.append(node)
            node_colors.append('orange')
            node_sizes.append(100)

    fig, ax = plt.subplots(figsize=(12, 8))
    dpi = fig.get_dpi()
    fig.set_size_inches(808 * 2 / float(dpi), 808 / float(dpi))
    dig = nx.DiGraph()
    dig.add_nodes_from(nodes)
    dig.add_edges_from(edges)
    pos = nx.spiral_layout(dig, scale=2)
    nx.draw(dig, pos, edge_color='black', width=1, linewidths=1, node_size=node_sizes,
            node_color=node_colors, alpha=0.5, with_labels=True)
    nx.draw_networkx_edge_labels(dig, pos, edge_labels=edge_label_dict, font_color='red')
    plt.tight_layout(pad=0.05, h_pad=0.05, w_pad=0.05)
    plt.show()

    # Display in a window with matplotlib interactive controls
    layout = [[sg.Text('Controls:', font=('Arial', 14)),
               sg.Canvas(key='controls_cv')],
              [sg.Text('Legend:', font=('Arial', 14))],
              [sg.Text('Red', font=('Arial', 14), text_color='red'),
               sg.Text(' - Negative Events/States, ', font=('Arial', 14)),
               sg.Text('Green', font=('Arial', 14), text_color='green'),
               sg.Text('- Positive Events/States,', font=('Arial', 14))],
              [sg.Text('Purple', font=('Arial', 14), text_color='purple'),
               sg.Text(' - Class Types, ', font=('Arial', 14)),
               sg.Text('Blue', font=('Arial', 14), text_color='blue'),
               sg.Text('- Agents/Locations/Times/Resources, ',  font=('Arial', 14)),
               sg.Text('Orange', font=('Arial', 14), text_color='orange'),
               sg.Text('- Literals', font=('Arial', 14))],
              [sg.Column(layout=[[sg.Canvas(key='fig_cv', size=(800 * 2, 800))]], pad=(0, 0))]]
    graph_window = sg.Window('Graph', layout, icon=encoded_logo, element_justification='center').Finalize()
    draw_figure_with_toolbar(graph_window['fig_cv'].TKCanvas, fig,
                             graph_window['controls_cv'].TKCanvas)
    graph_window.Maximize()
    while True:
        event, values = graph_window.read()
        if event == sg.WIN_CLOSED:
            break
    graph_window.close()
    return


def get_event_data(narrative_name: str, store_name: str, event_uri: str) -> list:
    """
    Get details (predicates and objects) for an event.

    :param narrative_name: String holding the narrative title/label
    :param store_name: String holding the database/store name from which the event data is retrieved
    :param event_uri: The URI of the event in the database/data store
    :return: An array of tuples of (predicate value, object value, object type) for the event individual
    """
    results = []
    try:
        query_str = query_graph_individuals.replace('uri', event_uri).\
            replace('narr_graph', narrative_name.replace(' ', '_'))
        event_details = query_database('select', query_str, store_name)
        if not event_details:
            capture_error(f'No event triples were returned for the uri, {event_uri}, in '
                          f'the narrative, {narrative_name}, in the database, {store_name}.', True)
    except Exception as e:
        capture_error(
            f'Exception getting event details for {event_uri} for the narrative, {narrative_name}, '
            f'in the database, {store_name}: {str(e)}', True)
        return []
    for binding in event_details:
        obj_type = empty_string
        if 'e_type' in binding:
            obj_type = "Event"
        elif 'a_type' in binding:
            obj_type = "Agent"
        elif 't_type' in binding:
            obj_type = "Time"
        elif 'r_type' in binding:
            obj_type = "Resource"
        if obj_type:
            results.append((binding['pred']['value'], binding['obj']['value'],
                            binding['obj_label']['value'], obj_type))
        else:
            results.append((binding['pred']['value'], binding['obj']['value']))
    return results
