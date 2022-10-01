# Functions to process/modify sentence/verb labels
# Called by create_narrative_turtle.py

from dna.utilities import empty_string


def create_verb_label(labels: list, subj_tuples: list, obj_tuples: list, prep_tuples: list, negated: bool) -> str:
    """
    Creates a text summary of the sentence.

    :param labels: An array of label details - verb_label, xcomp_labels (another list), prt_label,
                   using_label, aux_label
    :param subj_tuples: An array of tuples consisting of the verb's subjects' text, type, mappings and IRI
    :param obj_tuples: An array of tuples consisting of the verb's objects' text, type, mappings and IRI
    :param prep_tuples: An array of tuples consisting of the verb's prepositions' text, and its objects'
                        text, type, mappings and IRI
    :param negated: Boolean indicating that the verb is negated
    :return: A string holding the sentence summary, which becomes the event label
    """
    subj_labels = [subj_text for subj_text, subj_type, subj_mappings, subj_iri in subj_tuples if True]
    obj_labels = [obj_text for obj_text, obj_type, subj_mappings, obj_iri in obj_tuples if True]
    verb_text = f'{labels[4]} {labels[0]}' if labels[4] else labels[0]   # Label with aux verb or the default label
    xcomp_text = empty_string
    for xcomp_label in labels[1]:
        if xcomp_text:
            xcomp_text += f', {xcomp_label}'
        else:
            xcomp_text = xcomp_label
    verb_text = xcomp_text if xcomp_text else verb_text
    if labels[2]:
        prt_label = labels[2]
        # Replace the prt root verb with the verb + prt
        for text in verb_text.split(' '):
            if prt_label.startswith(text):
                verb_text = verb_text.replace(text, prt_label)
                break
    if not subj_labels:
        event_label = f'{", ".join(obj_labels)} {verb_text}'
    elif not obj_labels:
        event_label = f'{", ".join(subj_labels)} {verb_text}'
    else:
        event_label = f'{", ".join(subj_labels)} {verb_text} {", ".join(obj_labels)}'
    for prep_text, obj_text, obj_type, obj_mappings, obj_iri in prep_tuples:
        if not prep_text or not obj_text:
            continue
        if prep_text != 'after' and not (obj_type.endswith('GPE') or obj_type.endswith('LOC')
                                         or obj_type.endswith('FAC')):
            # "after xxx" designates a time which may not be part of the main subject/verb and likely confusing
            event_label += f' {prep_text} {obj_text}'
    if labels[3]:
        event_label += labels[3]
    if negated:
        return f'Negated: {event_label}'
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


def get_xcomp_labels(chunk_dict: dict) -> list:
    """
    Creates an array of strings representing how verb labels need to be modified due to
    the presence of an xcomp.

    :param chunk_dict: The dictionary for the chunk
    :return: An array of labels that add xcomp details
    """
    xcomp_labels = []
    if 'verb_processing' in chunk_dict:
        verb_procs = chunk_dict['verb_processing']
        for proc in verb_procs:
            if proc.startswith('xcomp'):
                verbs = proc.split(', ')
                xcomp_labels.append(f'{verbs[0].split("> ")[1]} to {verbs[1]}')
    return xcomp_labels
