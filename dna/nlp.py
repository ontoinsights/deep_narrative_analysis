# Entry points for all spaCy processing
# Where a narrative's sentences are parsed into dictionary elements with the following form:
#    'text': 'narrative_text', 'offset': #, 'punct': '?|!',
#    'entities': ['text+ent_label1', 'text+ent_label2', ...]
# Sentence dictionaries are then evaluated to produce the narrative's Turtle output
#    (parse_narratives -> create_narrative_turtle's create_graph)

import logging
import re
import spacy
from spacy.language import Language
from spacy.matcher import DependencyMatcher
from spacy.tokens import Doc
from spacy.tokenizer import Tokenizer
from spacy.lang.char_classes import ALPHA, ALPHA_LOWER, ALPHA_UPPER, CONCAT_QUOTES, LIST_ELLIPSES, LIST_ICONS
from spacy.util import compile_infix_regex
from word2number import w2n

from dna.query_openai import access_api, speaker_prompt
from dna.utilities_and_language_specific import add_to_dictionary_values, empty_string, space

nlp = spacy.load('en_core_web_trf')

spacy_stopwords = nlp.Defaults.stop_words
spacy_stopwords.clear()


def _remove_quotation_marks(text: str) -> str:
    """
    Removes quotation marks and some punctuation from a sentence.

    :param text: The original text
    :return: The updated text with the quotes and some punctuation removed
    """
    text_doc = nlp(text)
    updated_text = empty_string
    for token in text_doc:
        if token.text in ('[', ']') or (token.pos_ == 'PUNCT' and token.text in ('.', '?', '-', '!', ',')) or \
                (token.pos_ == 'PART' and token.dep_ == 'case'):
            updated_text += token.text
        elif token.pos_ != 'PUNCT':
            updated_text += f' {token.text}'
    # Some cleanup
    updated_text = re.sub(r'(\[) ', r'\1', updated_text)
    updated_text = re.sub(r'(\S)(\[Quotation)', r'\1 \2', updated_text)
    updated_text = re.sub(r'(Quotation[0-9]+])\.', r'\1', updated_text)
    return updated_text.replace('  ', space).replace('\n ', space).strip()


def parse_narrative(narr_text: str) -> (list, list, dict):
    """
    Creates a spacy Doc from the narrative text, splitting it into sentences and separating out
    quotations. Each of the sentences is described using a dictionary format, which is added to an array,
    and returned. In addition, quotations from the narrative are extracted.

    :param narr_text: The narrative text
    :return: A tuple consisting of an array of dictionaries holding the details of each sentence,
             an array of the texts of any quotations (texts between any types of quotation marks),
             and a dictionary of quotations that have a subject and verb (whose keys are the text,
             "Quotation#" and whose values are a tuple of the text and likely 'speaker')
    """
    narrative = narr_text.replace('\n', space).replace("  ", space)
    updated_narr, quotations, quotations_dict = resolve_quotations(narrative)
    doc = nlp(updated_narr)
    sentence_dicts = []
    sentence_offset = 0
    for sentence in doc.sents:
        prelim_text = sentence.text.strip()
        if len(prelim_text) < 3 or not any(c.isalnum() for c in prelim_text):
            continue
        sent_dict = dict()
        sentence_offset += 1
        sent_dict['offset'] = sentence_offset
        # Reset spacy's separation of tokens
        sent_text = re.sub(r'([0-9]) %', r'\1%', prelim_text)
        sent_text = re.sub(r' (]) ', r'\1', sent_text)
        # Need to execute re.sub twice since a string of hyphens may be defined (e.g., xxx- xxx- xxx)
        sent_text = re.sub(r'([a-zA-Z])- ([a-zA-Z])', r'\1-\2', sent_text)
        sent_text = re.sub(r'([a-zA-Z])- ([a-zA-Z])', r'\1-\2', sent_text)
        # TODO: Other quotation patterns?
        sent_dict['text'] = sent_text
        if '?' in sent_text:
            sent_dict['punct'] = '?'
        elif '!' in sent_text:
            sent_dict['punct'] = '!'
        sent_doc = nlp(sent_text)
        for ent in sent_doc.ents:
            ent_text = ent.text
            # Ignoring 'TIME'
            if ent.label_ in ('DATE', 'EVENT', 'FAC', 'GPE', 'LAW', 'LOC', 'NORP', 'ORG', 'PERSON',
                              'PRODUCT', 'WORK_OF_ART'):
                add_to_dictionary_values(sent_dict, 'entities', f'{ent_text}+{ent.label_}', str)
        sentence_dicts.append(sent_dict)
    return sentence_dicts, quotations, quotations_dict


def resolve_quotations(narr: str) -> (str, list, dict):
    """
    Process the quotations in the text - capture them and remove quotation marks.

    :param narr: The original narrative text
    :return: A tuple with (1) the updated narrative text (removing quotation marks and removing any quotations
             with a subj+verb, replacing the quote with the text 'Quotation#'), (2) a list of quotations
             (separating out individual sentences) and (3) a dictionary of the quotations that were removed
             from the narrative (with the keys, 'Quotation#', and values = tuples of the quote text and
             likely 'speaker')
    """
    quot_dict = dict()
    # TODO: What about single quote (apostrophe)? But, that should be used for possessives
    quot_dict[0] = re.findall(r"\u0022(.*?)\u0022", narr)   # Double quotes
    quot_dict[1] = re.findall(r"\u2018(.*?)\u2019", narr)   # Left and right single quotes
    quot_dict[2] = re.findall(r"\u201c(.*?)\u201d", narr)   # Left and right double quotes
    lengths = [len(quot_dict[0]), len(quot_dict[1]), len(quot_dict[2])]
    if len([gt for gt in lengths if gt > 0]) > 0:   # Are there any quotes in the text?
        # Yes, but may have quotes within quotes
        # Assume that the quotation mark type with the largest number of quotations is the main choice for quoting
        index_max = max(range(len(lengths)), key=lengths.__getitem__)
        quotations = quot_dict[int(index_max)]
    else:    # No left/right or double quotes
        return narr.replace('  ', space).replace('\n ', space).strip(), [], dict()
    # Create quotations dictionary and update narrative to remove quotations that are sentences with subjs/verbs
    index = 0
    quotation_dict = dict()
    final_quotes = []
    updated_narr = narr   # Want to remove quotations from sentences to not influence their overall sentiment
    for quote in quotations:   # Process the individual quotations
        quote_doc = nlp(quote)
        quote_verbs = [wd for wd in list(quote_doc) if wd.pos_ in ('VERB', 'AUX')]
        quote_subjs = []
        if quote_verbs:
            for quote_verb in quote_verbs:
                quote_subjs = [wd for wd in quote_verb.children if 'subj' in wd.dep_]
                if quote_subjs:
                    break
        if quote_verbs and quote_subjs:
            # Remove quote from narrative and replace with 'Quotation#'
            updated_narr = updated_narr.replace(quote, f'[Quotation{index}]')
            quotation_dict[f':Quotation{index}'] = quote
            index += 1
        final_quotes.append(quote)
    updated_narr = updated_narr.replace('"', space).strip()
    # Add speaker attribution and Named Entities list to the quotations
    if len(quotation_dict) > 0:
        for quote_numb, quote_text in quotation_dict.items():
            # Get named entities mentioned
            # spacy 3.7.4 has issues with finding named entities if the names are enclosed by brackets
            quote_doc = nlp(quote_text.replace('[', empty_string).replace(']', empty_string))
            entities = []
            for ent in quote_doc.ents:
                ent_text = ent.text
                # Ignoring 'TIME'
                if ent.label_ in ('DATE', 'EVENT', 'FAC', 'GPE', 'LAW', 'LOC', 'NORP', 'ORG', 'PERSON',
                                  'PRODUCT', 'WORK_OF_ART'):
                    entities.append(f'{ent_text}+{ent.label_}')
            # Get attribution for the quote
            speaker_dict = access_api(speaker_prompt.replace("{narr_text}", narr).replace("{quote_text}", quote_text))
            if 'speaker' in speaker_dict:
                attribution = speaker_dict['speaker']
                quotation_dict[quote_numb] = (quote_text, attribution, entities)
            else:
                quotation_dict[quote_numb] = (quote_text, empty_string, entities)
    return _remove_quotation_marks(updated_narr), final_quotes, quotation_dict
