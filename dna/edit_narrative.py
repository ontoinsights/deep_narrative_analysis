# Processing to display a window to edit the predicate and/or object of a triple

import csv
import logging
import PySimpleGUI as sg

from database import query_database
from details_narrative import get_narratives
from utilities import empty_string, new_line, resources_root, capture_error, encoded_logo

query_events = 'prefix : <urn:ontoinsights:dna:> SELECT distinct ?event ?pred ?obj ' \
               'FROM <urn:narr_graph> WHERE ' \
               '{ ?event a ?type ; :sentiment ?sent ; :sentence_offset ?offset ; ?pred ?obj } ' \
               'ORDER BY ?offset ?pred ?obj'

query_nouns = 'prefix : <urn:ontoinsights:dna:> SELECT distinct ?noun ?pred ?obj ' \
              'FROM NAMED <urn:narr_graph> FROM <tag:stardog:api:context:default> WHERE ' \
              '{ { { graph <urn:narr_graph> { ?noun a ?type ; ?pred ?obj } } ' \
              '{ { ?type rdfs:subClassOf* :Agent } UNION { ?type rdfs:subClassOf* :Location } ' \
              'UNION { ?type rdfs:subClassOf* :Time } UNION { ?type rdfs:subClassOf* :Resource } } } ' \
              'UNION { graph <urn:narr_graph> { ?noun a owl:Thing ; ?pred ?obj } } } ' \
              'ORDER BY ?noun ?pred ?obj'


def display_edit_table(title: str, data_list: list, store_name: str):
    """
    Display a PySimpleGUI window with a table of nouns/concepts, events or both from a narrative.

    :param title: String holding the window title
    :param data_list: Array of lists holding 1) either a noun/concept or event URI, 2) a predicate
                      for that noun/event individual, 3) the object of the predicate
    :param store_name: String holding the database/store details when saving changes
    :returns: None
    """
    cols_list = ['Identifier', 'Predicate', 'Object/Value', 'Delete']
    # TODO: Add ability to create new triples
    # Define the window layout
    layout = [[sg.Text("Select a specific row/column for editing and enter its row number below. A "
                       "pop-up window will be displayed where edits can be made",
                       font=('Arial', 16))],
              [sg.Text("Alternately, you can output the table to a CSV file, make changes there and upload "
                       "the modified file to persist the changes.",
                       font=('Arial', 16))],
              [sg.Text("To remove a triple, enter 'True' as the value for 'Delete'.",
                       font=('Arial', 16))],
              [sg.Text()],
              [sg.Text('Row number to update:', font=('Arial', 16)),
               sg.InputText(text_color='black', background_color='#ede8e8',
                            font=('Arial', 16), key='row_number')],
              [sg.Text("OR, output the table to a CSV file with the name:", font=('Arial', 16)),
               sg.InputText(text_color='black', background_color='#ede8e8',
                            font=('Arial', 16), key='csv_file'),
              [sg.Text("Note that the file is created in the dna/resources directory.", font=('Arial', 16))],
               sg.Text(".csv", font=('Arial', 16))],
              [sg.Text("Click 'OK' to obtain the window to edit the row, or to output the CSV file.",
                       font=('Arial', 16)),
               sg.Button('OK', button_color='dark blue', font=('Arial', 14), size=(5, 1))],
              [sg.Text()],
              [sg.Column(layout=[[sg.Table(key='edit-table', values=data_list, headings=cols_list,
                                           auto_size_columns=True, display_row_numbers=True,
                                           justification='left', num_rows=20, max_col_width=35,
                                           alternating_row_color='lightyellow',
                                           enable_events=True, bind_return_key=True,
                                           font=('Arial', 14))]], pad=(0, 0))],
              [sg.Text()],
              [sg.Text("Press 'Save' to update the backing store with ALL the changes since the beginning of "
                       "this edit session, or since the last 'Save' in this session", font=('Arial', 16))],
              [sg.Text("Press 'Reset' to return ALL rows/columns to their original values (as they were at "
                       "the beginning of this edit session or since the last 'Save'.", font=('Arial', 16))],
              [sg.Text("Press 'End' (or close the window) to exit. If the window is exited, all "
                       "pending changes will be lost.", font=('Arial', 16))],
              [sg.Button('Save', button_color='dark blue', font=('Arial', 14), size=(5, 1)),
               sg.Button('Reset', button_color='red', font=('Arial', 14), size=(5, 1)),
               sg.Button('End', button_color='dark blue', font=('Arial', 14), size=(5, 1))],
              [sg.Text()]]

    # Create the GUI Window
    window_table = sg.Window(title, layout, icon=encoded_logo, resizable=True).Finalize()
    window_table['row_number'].Widget.config(insertbackground='black')
    window_table['csv_file'].Widget.config(insertbackground='black')

    # Loop to process window triples
    items_changed = set()
    window_table.find_element("edit-table").update(values=data_list)
    while True:
        edit_events, values = window_table.read()
        if edit_events in (sg.WIN_CLOSED, 'End'):
            # If user closes window or clicks 'End'
            break
        if edit_events == 'Reset':
            # Make no changes to Stardog; Reset the window
            window_table.close()
            display_narratives_for_edit(store_name)
            return
        if edit_events == 'Save':
            # TODO: Write items_changed to Stardog; Reset the window with the new changes
            # TODO: Changes update the idioms dictionaries
            window_table.close()
            display_narratives_for_edit(store_name)
            return
        if edit_events == 'OK':
            if values['row_number'] and values['csv_file']:
                sg.popup_error('Both a row number and a CSV output file cannot be specified. '
                               'Remove the text in one of the fields.', font=('Arial', 14),
                               button_color='dark blue', icon=encoded_logo)
            else:
                if values['row_number']:
                    row_number = int(values['row_number'])
                    # Expand the list element
                    [subj, pred, obj, del_flag] = data_list[row_number]
                    new_pred, new_obj, new_del = display_row_for_edit(subj, pred, obj, del_flag)
                    if (new_pred == pred) and (new_obj == obj) and (del_flag == new_del):
                        continue   # No changes
                    items_changed.add(subj)
                    data_list[row_number] = [subj, new_pred, new_obj, new_del]
                    window_table.find_element("edit-table").update(values=data_list)
                if values['csv_file']:
                    with open(f"{resources_root}{values['csv_file']}.csv", 'w', newline=new_line) as csv_file:
                        table_writer = csv.writer(csv_file, delimiter=',')
                        table_writer.writerow(['Identifier', 'Predicate', 'Value'])
                        for data_row in data_list:
                            table_writer.writerow(data_row)

    # Done
    window_table.close()
    return


def display_narratives_for_edit(store_name: str):
    """
    Display a list of all narratives in the specified store (without the domain timeline, if one is defined)
    and allow selection of one. Then, display the subj-pred-obj details for individuals (nouns and events)
    that are discussed within it.

    :param store_name: The database/data store name
    :returns: None (Narrative timeline is displayed)
    """
    logging.info('Narrative selection for edit')
    # Get the list of narratives
    narrative_dict = get_narratives(store_name)
    if 'Domain Events' in narrative_dict.keys():
        del narrative_dict['Domain Events']
    if len(narrative_dict) == 0:
        sg.popup_ok(f'No narratives were found in {store_name}. '
                    f'Please select a different store or ingest one or more using the "Load Narratives" button.',
                    font=('Arial', 14), button_color='dark blue', icon=encoded_logo)
        return
    else:
        narrative_list = [narr.replace('_', '') for narr in narrative_dict.keys()]

    # Define the PySimpleGUI window
    sg.theme('Material2')
    layout = [[sg.Text("Select a narrative and either choose to edit nouns or events.", font=('Arial', 16))],
              [sg.Text("Press 'OK' to edit the narrative, or press 'End' (or close the window) to exit.",
                       font=('Arial', 16))],
              [sg.Listbox(narrative_list, size=(30, 10), key='narrative_list', font=('Arial', 14),
                          background_color='#fafafa', highlight_background_color='light grey',
                          highlight_text_color='black', text_color='black')],
              [sg.Text()],
              [sg.Text("Please select 'Edit  Nouns, 'Edit Events' or both via the checkboxes below.",
                       font=('Arial', 16))],
              [sg.Checkbox('Edit Nouns', default=False, key='edit-nouns', font=('Arial', 16)),
               sg.Checkbox('Edit Events', default=True, key='edit-events', font=('Arial', 16))],
              [sg.Text()],
              [sg.Button('OK', button_color='dark blue', font=('Arial', 14), size=(5, 1)),
               sg.Button('End', button_color='dark blue', font=('Arial', 14), size=(5, 1))]]

    # Create the GUI Window
    window_edit = sg.Window('Select Narrative for Edit', layout, icon=encoded_logo).Finalize()

    # Loop to process window "events"
    while True:
        edit_events, values = window_edit.read()
        if edit_events in (sg.WIN_CLOSED, 'End'):
            # If user closes window or clicks 'End'
            break
        if edit_events == 'OK':
            if len(values['narrative_list']) != 1:
                sg.popup_error('Either no narrative was selected, or more than one selection was made.',
                               font=('Arial', 14), button_color='dark blue', icon=encoded_logo)
            else:
                narrative_name = values['narrative_list'][0]
                edit_nouns = True if values['edit-nouns'] else False
                edit_events = True if values['edit-events'] else False

                # Get nouns and/or events for the selected narrative
                data_list = []
                event_bindings = []
                noun_bindings = []
                try:
                    if edit_events:
                        event_bindings = query_database(
                            'select', query_events.replace('narr_graph', narrative_name.replace(' ', '_')),
                            store_name)
                        if not event_bindings:
                            sg.popup_error(f'No events are defined for the narrative, {narrative_name}. '
                                           f'There is nothing to edit.',
                                           font=('Arial', 14), button_color='dark blue', icon=encoded_logo)
                    if edit_nouns:
                        noun_bindings = query_database(
                            'select', query_nouns.replace('narr_graph', narrative_name.replace(' ', '_')), store_name)
                        if not noun_bindings:
                            sg.popup_error(f'No concepts/nouns are defined for the narrative, {narrative_name}. '
                                           f'There is nothing to edit.',
                                           font=('Arial', 14), button_color='dark blue', icon=encoded_logo)
                except Exception as e:
                    capture_error(
                        f'Exception getting events for {narrative_name} in the {store_name}: {str(e)}', True)
                    return
                # Get all the tuples together in an array with array elements = subj, pred, obj
                if event_bindings:
                    for event_bind in event_bindings:
                        data_list.append(list((event_bind['event']['value'], event_bind['pred']['value'],
                                              event_bind['obj']['value'], False)))
                    display_edit_table('Edit Nouns/Concepts', data_list, store_name)
                if noun_bindings:
                    for noun_bind in noun_bindings:
                        data_list.append(list((noun_bind['noun']['value'], noun_bind['pred']['value'],
                                               noun_bind['obj']['value'], False)))
                        # Sort data_list by subj, pred, obj
                    data_sorted = sorted(data_list, key=lambda i: [i[0], i[1], i[2]])
                    display_edit_table('Edit Nouns/Concepts', data_sorted, store_name)
                break

    # Done
    window_edit.close()
    return


def display_row_for_edit(subj: str, pred: str, obj: str, del_flag: bool) -> (str, str, bool):
    """
    :param subj: String holding the subject of a triple
    :param pred: String holding the predicate of a triple
    :param obj: String holding the object of a triple
    :param del_flag: Boolean indicating that the triple should be removed from the store
    :returns: A tuple consisting of the window's predicate and object strings
    """
    # Determine the height of the 'Object' text
    if len(obj) > 2000:
        obj_size = 25
    elif len(obj) > 1000:
        obj_size = 15
    else:
        obj_size = 5

    # Create the window
    sg.theme('Material2')
    layout = [[sg.Text("To edit, simply update the text fields inline (the Identifier cannot be updated).",
                       font=('Arial', 16))],
              [sg.Text("To retain the changes, press 'OK'. Otherwise, press 'End' or close the window.",
                       font=('Arial', 16))],
              [sg.Text()],
              [sg.Text('Identifier: ', font=('Arial', 14))],
              [sg.Text(subj, font=('Arial', 14))],
              [sg.Text()],
              [sg.Text('Predicate: ', font=('Arial', 14))],
              # TODO: Should this be a drop-down?
              [sg.InputText(default_text=pred, text_color='black', background_color='#ede8e8',
                            font=('Arial', 16), key='pred_text', do_not_clear=True)],
              [sg.Text()],
              [sg.Text('Object: ', font=('Arial', 14))],
              [sg.Multiline(obj, key='obj_text', font=('Arial', 16), size=(70, obj_size),
                            auto_refresh=True, autoscroll=True, background_color='#ede8e8',
                            text_color='black')],
              [sg.Checkbox('Delete triple: ', key='delete', font=('Arial', 14), default=del_flag)],
              [sg.Text()],
              [sg.Button('OK', button_color='dark blue', font=('Arial', 14), size=(5, 1)),
               sg.Button('End', button_color='dark blue', font=('Arial', 14), size=(5, 1))]]

    # Create the GUI Window
    window_triples = sg.Window('Edit Triple', layout, icon=encoded_logo).Finalize()
    window_triples['pred_text'].Widget.config(insertbackground='black')
    window_triples['obj_text'].Widget.config(insertbackground='black')

    # Loop to process window "events"
    while True:
        triple_events, values = window_triples.read(timeout=0)
        if triple_events in (sg.WIN_CLOSED, 'End'):
            # If user closes window or clicks 'End'
            break
        if triple_events == 'OK':
            new_pred = values['pred_text']
            new_obj = values['obj_text']
            new_del = values['delete']
            window_triples.close()
            return new_pred, new_obj, new_del

    # Cleanup
    window_triples.close()
    return empty_string, empty_string, False
