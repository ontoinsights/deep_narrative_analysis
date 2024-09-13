# Entry points for all spaCy processing
#    where a narrative's sentences are parsed into an array of Sentence Class instances
#    (parse_narratives outputs passed to create_narrative_turtle's create_graph by
#    process_new_narrative in app_functions.py)

import logging
import re
from dataclasses import dataclass

import spacy
from spacy.tokens import Doc
from spacy.tokenizer import Tokenizer

from dna.query_openai import access_api, attribution_prompt
from dna.sentence_classes import Entity, Sentence, Quotation, Punctuation
from dna.utilities_and_language_specific import empty_string, modals, ner_types, space

nlp = spacy.load('en_core_web_trf')

spacy_stopwords = nlp.Defaults.stop_words
spacy_stopwords.clear()

quotation_mark_dict = {"\u0022": "\u0022",     # Holding the corresponding left/right quotation marks
                       "\u2018": "\u2019",     # Where the key is the left-hand mark
                       "\u201c": "\u201d"}
left_quotation_marks = list(quotation_mark_dict.keys())

modals_without_space = [modal[:-1] for modal in modals]

@dataclass
class ParseResults:
    """
    Dataclass holding the results of the parse_narrative function
    """
    sentence_classes: list       # Array of Sentence class instances
    quotation_classes: list      # Array of Quotation class instances
    partial_quotes: list         # Array of strings of partial quotations (without subject/verb)

@dataclass
class QuotationResults:
    """
    Dataclass holding the results of the _resolve_quotations function
    """
    # Updated narrative text (cleaning the text, removing quotations with a subj+verb, replacing the quote
    # with the text '[Quotation#]', and removing partial quotes, replacing the quote with the text, '[Partial#])
    updated_text: str
    left_quotation: str          # Left quotation mark to delineate quotes
    quotation_classes: list      # List of Quotation Class instances (removed from the updated_text)
    quoted_texts: list           # List of quoted texts that do not have a subject/verb


def _get_original_text(sent_text: str, quotation_instances: list, partial_quotations: list, left_quote: str) -> str:
    """
    Reassemble the original text to maintain/use it plus support the removal of the quoted text.

    :param sent_text: The updated sentence text
    :param quotation_instances: A list of Quotation instance classes for the entire narrative/article
    :param partial_quotations: A list of quoted text that is only a few words long
    :param left_quote: String holding the left quotation mark used in the article/narrative
    :return: The original sentence text with the quotes restored to it
    """
    if '[Quotation' not in sent_text and '[Partial' not in sent_text:
        return sent_text
    updated_text = sent_text
    if '[Quotation' in sent_text:
        quotations = re.findall(r'\[Quotation[0-9]+]', sent_text)
        for quotation in quotations:
            quote_index = int(quotation.split("[Quotation")[1].split(']')[0])
            quote_text = quotation_instances[quote_index].text
            updated_text = \
                updated_text.replace(quotation, f'{left_quote}{quote_text}{quotation_mark_dict[left_quote]}')
    if '[Partial' in sent_text:
        partials = re.findall(r'\[Partial[0-9]+]', sent_text)
        for partial in partials:
            partial_index = int(partial.split("[Partial")[1].split(']')[0])
            partial_text = partial_quotations[partial_index].split(': ')[1]
            updated_text = updated_text.replace(partial, partial_text)
    return updated_text


# Future
def _get_punctuations(sentence_text: str) -> list:
    """
    FUTURE: Determine if '?' or '!' is found in the sentence.

    :param sentence_text: String holding the sentence text
    :return: Array of Punctuation Enum values found in the sentence
    """
    punctuations = []
    if '?' in sentence_text:
        punctuations.append(Punctuation.QUESTION)
    if '!' in sentence_text:
        punctuations.append(Punctuation.EXCLAMATION)
    return punctuations


def _get_quotation_attribution(complete_text: str, quotation: str) -> str:
    """
    Processing to find the speaker of a quotation.

    :param complete_text: String holding the full narrative
    :param quotation: String holding the specific quotation
    :return: String holding the 'speaker' of the quote as determined by OpenAI
             or an empty string if a speaker could not be determined
    """
    # Get attribution for the quote
    speaker_dict = access_api(attribution_prompt.replace("{narr_text}", complete_text)
                              .replace("{quote_text}", quotation))
    if 'speaker' in speaker_dict and speaker_dict['speaker'] not in ('error', 'string'):
        return speaker_dict['speaker']
    return empty_string


def _remove_tokens(text: str) -> str:
    """
    Removes quotation marks and some punctuation from a sentence.

    :param text: The original text
    :return: The updated text with the quotes and some punctuation removed
    """
    text_doc = nlp(text)
    updated_text = empty_string
    for token in text_doc:
        # Keep certain marks classified as "punctuation"
        if token.text in ('[', ']', '.', '?', '-', '!', ',') or (token.pos_ == 'PART' and token.dep_ == 'case'):
            updated_text += token.text
        elif token.pos_ != 'PUNCT':
            updated_text += f' {token.text}'
    # Some cleanup
    updated_text = re.sub(r'(\[) ', r'\1', updated_text)
    updated_text = re.sub(r'(\S)(\[Quotation)', r'\1 \2', updated_text)
    updated_text = re.sub(r'(\S)(\[Partial)', r'\1 \2', updated_text)
    updated_text = re.sub(r'(Quotation[0-9]+])\.', r'\1', updated_text)
    updated_text = re.sub(r'(Partial[0-9]+])\.', r'\1', updated_text)
    return updated_text.replace('  ', space).replace('\n ', space).strip()


def _resolve_quotations(narr: str) -> QuotationResults:
    """
    Process the quotations in the text - capture them and return a version of the
    article/narrative with the quotation texts removed.

    :param narr: The original narrative text
    :return: An instance of the dataclass, QuotationResults
    """
    # Determine what format is used to indicate a quotation (", right/left quotes, ...) and extract
    #     all quoted text
    quotations_list = [[], [], []]    # Array of arrays of the strings within different types of quotation marks
    # TODO: (Future) What about single quote (apostrophe)? Assume that they are used for only for possessives
    # TODO: (Future) Other quotation patterns?
    quotations_list[0] = re.findall(r"\u0022(.*?)\u0022", narr)        # Within double quotes
    quotations_list[1] = re.findall(r"\u2018(.*?)\u2019", narr)        # Within left/right single quotes
    quotations_list[2] = re.findall(r"\u201c(.*?)\u201d", narr)        # Within left/right double quotes
    lengths = [len(quotations_list[0]), len(quotations_list[1]), len(quotations_list[2])]
    if len([gt for gt in lengths if gt > 0]) > 0:   # Are there any quotes in the text? (any length > 0?)
        # Yes, but may have quotes within quotes
        # Assume that the quotation mark type with the largest count is the method for quoting
        index_max = max(range(len(lengths)), key=lengths.__getitem__)
        left_quotation = left_quotation_marks[index_max]
        quotes = quotations_list[int(index_max)]   # List of quotations to be processed
    else:    # No left/right or double quotes
        return QuotationResults(narr.replace('  ', space).replace('\n ', space).strip(), empty_string,
                                [], [])
    # Create array of all quoted strings and another of all quotations that are sentences with subjs/objs
    # Also, update the narrative to remove quotation marks and all quotations that are sentences with subjs/objs
    full_quote_index = 0
    partial_quote_index = 0
    quotation_instance_list = []        # Array of instances of the Quotation class
    partial_quote_list = []             # Array of all quoted strings that do not have subject/object
    updated_narr = narr                 # Remove quotations from sentences since they could cross sentence boundaries
    for quote in quotes:    # Process the individual quotations
        quote_doc = nlp(quote)
        quote_verbs = [wd for wd in list(quote_doc) if wd.pos_ in ('VERB', 'AUX')]  # Root verb may be AUX
        verb_and_subj = False
        for quote_verb in quote_verbs:   # If any verb has a subject, then remove quoted text
            if any([wd for wd in quote_verb.children if 'subj' in wd.dep_]):
                verb_and_subj = True
                break
        if verb_and_subj:                # Have a subject+verb
            # Remove quote from narrative and replace with 'Quotation#'
            updated_narr = updated_narr.replace(quote, f'[Quotation{full_quote_index}]').strip()
            quotation_instance_list.append(
                Quotation(quote, full_quote_index,
                          get_entities(quote.replace('[', empty_string).replace(']', empty_string)),
                          _get_quotation_attribution(narr, quote)))
            full_quote_index += 1
        else:
            # Add the quote to the partial quotation list
            updated_narr = updated_narr.replace(quote, f'[Partial{partial_quote_index}]').strip()
            partial_quote_list.append(f'Partial{partial_quote_index}: {quote}')
            partial_quote_index += 1
    return QuotationResults(_remove_tokens(updated_narr), left_quotation, quotation_instance_list, partial_quote_list)


def _update_token_separation(sentence_text: str) -> str:
    """
    Reset spacy's separation of tokens

    :param sentence_text: The current text of the sentence
    :return: Updated sentence text
    """
    #
    updated_text = re.sub(r'([0-9]) %', r'\1%', sentence_text)
    updated_text = re.sub(r' (]) ', r'\1', updated_text)
    # Need to execute re.sub twice since a string of hyphens may be defined (e.g., xxx- xxx- xxx)
    updated_text = re.sub(r'([a-zA-Z])- ([a-zA-Z])', r'\1-\2', updated_text)
    return re.sub(r'([a-zA-Z])- ([a-zA-Z])', r'\1-\2', updated_text)


def get_entities(text: str) -> list:
    """
    Processing to find the 'named entities' in a sentence.

    :param text: String holding the sentence text
    :return: List of named entities (except for TIME, which is handled separately in the Turtle processing)
    """
    doc = nlp(text)
    entities = []
    for ent in doc.ents:
        # Ignoring 'TIME'
        if ent.label_ in ner_types and ent.label_ != 'TIME':    # Using strings for now to aid in debug
            entities.append(Entity(ent.text, ent.label_))
    return entities


def parse_narrative(narr_text: str) -> ParseResults:
    """
    Creates a spacy Doc from the narrative text, splitting it into sentences and separating out
    quotations. Each sentence is an instance of the Sentence Class. Each quotation (with a subject and verb) is
    separated from the narrative text and separately saved as a Quotation instance. Also, partial quotes
    (typically a few words) are returned.

    :param narr_text: The narrative text
    :return: An instance of the ParseResults dataclass
    """
    narrative = narr_text.replace('\n', space).replace("  ", space)
    quotation_results = _resolve_quotations(narrative)
    doc = nlp(quotation_results.updated_text)
    sentence_instance_list = []
    sentence_offset = 0
    for sentence in doc.sents:
        sentence_offset += 1
        sentence_text = _update_token_separation(sentence.text.strip())
        original_text = _get_original_text(sentence_text, quotation_results.quotation_classes,
                                           quotation_results.quoted_texts, quotation_results.left_quotation)
        # Determine if special punctuation is present (question and exclamation marks for now); Other punctuation?
        # punctuations = _get_punctuations(sentence_text)
        # Short sentences are mainly for reader effect and result in parsing problems - capture but ignore processing
        if len(sentence_text) < 3 or not any(c.isalnum() for c in sentence_text):
            # No NER or verb processing
            sentence_instance_list.append(Sentence(sentence_text, original_text, sentence_offset, []))
            continue
        sentence_instance_list.append(
            Sentence(sentence_text, original_text, sentence_offset, get_entities(sentence_text)))
    return ParseResults(sentence_instance_list, quotation_results.quotation_classes, quotation_results.quoted_texts)
