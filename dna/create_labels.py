# Functions to process/modify sentence/verb labels
# Called by create_narrative_turtle.py

from dna.utilities_and_language_specific import empty_string, prep_after, space


def create_verb_label(labels: list, subj_tuples: list, obj_tuples: list, prep_tuples: list, negated: bool) -> str:
    """
    Creates a text summary of the sentence.

    :param labels: An array of label details - verb_label, prt_label and aux_label
    :param subj_tuples: An array of tuples consisting of the verb's subjects' text, type, mappings and IRI
    :param obj_tuples: An array of tuples consisting of the verb's objects' text, type, mappings and IRI
    :param prep_tuples: An array of tuples consisting of the verb's prepositions' text, and its objects'
                        text, type, mappings and IRI
    :param negated: Boolean indicating that the verb is negated
    :return: A string holding the sentence summary, which becomes the event label
    """
    subj_labels = [subj_text for subj_text, subj_type, subj_mappings, subj_iri in subj_tuples if True]
    obj_labels = [obj_text for obj_text, obj_type, subj_mappings, obj_iri in obj_tuples if True]
    verb_text = f'{labels[2]} {labels[0]}' if labels[2] else labels[0]   # Label with aux verb or the default label
    if labels[1]:
        prt_label = labels[1]
        # Replace the prt root verb with the verb + prt
        for text in verb_text.split():
            if prt_label.startswith(text):
                verb_text = verb_text.replace(text, prt_label)
                break
    if not obj_labels and subj_labels:
        event_label = f'{", ".join(subj_labels)} {verb_text}'
    elif not subj_labels and obj_labels:
        event_label = f'{", ".join(obj_labels)} {verb_text}'
    else:
        event_label = f'{", ".join(subj_labels)} {verb_text} {", ".join(obj_labels)}'
    for prep_text, obj_text, obj_type, obj_mappings, obj_iri in prep_tuples:
        if not prep_text or not obj_text:
            continue
        if prep_text != prep_after and not (obj_type.endswith('GPE') or obj_type.endswith('LOC')
                                            or obj_type.endswith('FAC')):
            # "after xxx" designates a time which may not be part of the main subject/verb and likely confusing
            if obj_text in event_label:
                event_label = event_label.replace(f'{obj_text}', empty_string).replace('  ', space).strip()
            event_label += f' {prep_text} {obj_text}'
    if negated:
        return f'Negated: {event_label}'
    event_label = event_label.replace(' , ', space).replace('  ', space).replace('/poss/', empty_string)
    return event_label


def get_prt_label(chunk_dict: dict) -> str:
    """
    Creates a string representing how verb labels need to be modified due to the presence
    of a prt.

    :param chunk_dict: The dictionary for the chunk
    :return: A label string that includes the prt
    """
    if 'verb_processing' in chunk_dict:
        verb_procs = chunk_dict['verb_processing']
        for proc in verb_procs:
            if proc.startswith('prt'):
                return proc.split('prt > ')[1]
    return empty_string
