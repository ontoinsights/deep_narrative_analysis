import logging

# Words that introduce a 'causal' clause, where the main clause is the effect
cause_connectors = ['when', 'because', 'since', 'as']
# Words that introduce a 'causal' effect in the main clause, where the other clause is the cause
effect_connectors = ['so', 'therefore ', 'consequently ']
# If - then only is cause-effect when the tenses of the main and other clause are the same
cause_effect_pairs = [('if', 'then')]
# Prepositions that introduce a cause in the form of a noun phrase
cause_prepositions = ['because of', 'due to', 'as a result [of]', 'as a consequence [of]']
# Prepositions that introduce an effect in the form of a noun phrase
effect_prepositions = ['in order to']


def create_narrative_graph(sentence_dicts: list, title: str, store_name: str):
    """

    """
    logging.info(f'Create graph for {title} in {store_name}')
    # TODO
    for sent_dict in sentence_dicts:
        print(sent_dict)
    # current_date = ''
    # current_loc = ''
    # subjects = []
    # for subject_dict in sent_dict['subjects']:
    #     subject_text = subject_dict['subject_text']
    #     if 'subject_preps' in subject_dict.keys():
    #         for subject_prep_dict in subject_dict['subject_preps']:
    #             subject_text += f" {subject_prep_dict['subject_prep_text']}"
    #             for subject_prep_obj_dict in subject_prep_dict['subject_prep_objects']:
    #                 subject_text += f" {subject_prep_obj_dict['subject_prep_object']}"
    #     subjects.append(subject_text)
    # for verb_dict in sent_dict['verbs']:
    #     verb_text = verb_dict['verb_text']
    #     if 'preps' in verb_dict.keys():
    #         for prep_dict in verb_dict['preps']:
    #             prep_text = prep_dict['prep_text']
    #             count = 0
    #             for prep_detail_dict in prep_dict['prep_details']:
    #                 prep_type = prep_detail_dict['prep_detail_type']
    #                 if prep_text.lower() in ('in', 'on') and prep_type == 'DATE':
    #                     current_date = prep_detail_dict['prep_detail_text']
    #                 elif prep_text.lower() == 'after' and prep_type == 'EVENT' \
    #                         and prep_detail_dict['prep_detail_text'] == 'World War II':
    #                     # TODO: Look up event date and signal 'After' that date
    #                     current_date = '1945'
    #                 elif prep_text.lower() in ('in', 'to', 'from') and \
    #                         (prep_type in ('GPE', 'LOC') or 'ghetto' in prep_detail_dict['prep_detail_text']):
    #                     current_loc = prep_detail_dict['prep_detail_text']
    #                 else:
    #                     count += 1
    #                     if prep_text.lower() in verb_text:
    #                         space = SPACE
    #                         if count > 1:
    #                             space = ', '
    #                         verb_text += space + prep_detail_dict['prep_detail_text']
    #                     else:
    #                         verb_text += f" {prep_text.lower()} {prep_detail_dict['prep_detail_text']}"
    #                 # TODO with aid of
    #     if 'verb_aux' in verb_dict.keys():
    #         for verb_aux_dict in verb_dict['verb_aux']:
    #             verb_text = verb_aux_dict['verb_aux_text'] + ' ' + verb_text
    #             # TODO: 'verb_aux_preps' in verb_aux_dict.keys() ?
    #     if 'verb_xcomp' in verb_dict.keys():
    #         for verb_xcomp_dict in verb_dict['verb_xcomp']:
    #             verb_text += ' ' + verb_xcomp_dict['verb_xcomp_text']
    #             if 'verb_xcomp_preps' in verb_xcomp_dict.keys():
    #                 prep_objects = []
    #                 for prep_dict in verb_xcomp_dict['verb_xcomp_preps']:
    #                     prep_text = prep_dict['verb_xcomp_prep_text']
    #                     verb_text += ' ' + prep_text
    #                     if 'verb_xcomp_prep_objects' in prep_dict.keys():
    #                         for prep_object_dict in prep_dict['verb_xcomp_prep_objects']:
    #                             prep_object = prep_object_dict['verb_xcomp_prep_object']
    #                             prep_type = prep_object_dict['verb_xcomp_prep_object_type']
    #                             if prep_text.lower() in ('in', 'on') and prep_type == 'DATE':
    #                                 current_date = prep_object
    #                             elif prep_text.lower() == 'after' and prep_type == 'EVENT' \
    #                                     and prep_object == 'World War II':
    #                                 # TODO Look up event date and signal 'After' that date
    #                                 current_date = '1945'
    #                             elif prep_text.lower() in ('in', 'to', 'from') and \
    #                                     (prep_type in ('GPE', 'LOC') or 'ghetto' in prep_object):
    #                                 current_loc = prep_object
    #                             else:
    #                                 prep_objects.append(prep_object)
    #                 if prep_objects:
    #                     verb_text += ' ' + ', '.join(prep_objects)
    #     objects = []
    #     if 'objects' in verb_dict.keys():
    #         for object_dict in verb_dict['objects']:
    #             object_text = object_dict['object_text']
    #             if 'object_preps' in object_dict.keys():
    #                 for prep_dict in object_dict['object_preps']:
    #                     object_text += ' ' + prep_dict['object_prep_text']
    #                     for prep_detail in prep_dict['object_prep_objects']:
    #                         object_text += ' ' + prep_detail['object_prep_object']
    #             objects.append(object_text)
    #     if current_date:
    #         date_texts = current_date.split(' ')
    #         for date_text in date_texts:
    #             if date_text.isnumeric() and int(date_text) > 1000:
    #                 orig_dates.add(date_text)
    #             key_date = date_text
    #     text = f'Loc: {current_loc}\n'
    #     if not (len(subjects) == 1 and subjects[0] == 'I'):
    #         text += ', '.join(subjects) + ' ' + verb_text
    #     else:
    #         text += verb_text
    #     if objects:
    #         text += ' ' + ', '.join(objects)
    #     final_text = text + '\n'
    #     add_to_dictionary_values(date_text_dict, key_date, final_text, str)
    # return key_date, current_loc
    return
