# Entry points for all spaCy processing
#    where a narrative's sentences are parsed into an array of Sentence Class instances
#    (parse_narratives outputs passed to create_narrative_turtle's create_graph by
#    process_new_narrative in app_functions.py)

import logging
import re
import spacy
from spacy.tokens import Doc
from spacy.tokenizer import Tokenizer

from dna.query_openai import access_api, attribution_prompt
from dna.sentence_classes import Entity, Sentence, Quotation, Punctuation
from dna.utilities_and_language_specific import empty_string, ner_types, space

nlp = spacy.load('en_core_web_trf')

spacy_stopwords = nlp.Defaults.stop_words
spacy_stopwords.clear()


def _get_punctuations(sentence_text: str) -> list:
    """
    Determine if '?' or '!' is found in the sentence.

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


def _get_sentence_entities(sentence_doc):
    """
    Processing to find the 'named entities' in a sentence.

    :param sentence_doc: NLP parse of the sentence from spaCy
    :return: List of named entities (except for TIME, which is handled separately in the Turtle processing)
    """
    entities = []
    for ent in sentence_doc.ents:
        # Ignoring 'TIME'
        if ent.label_ in ner_types and ent.label_ != 'TIME':    # Using strings for now to aid in debug
            entities.append(Entity(ent.text, ent.label_))
    return entities


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
    updated_text = re.sub(r'(Quotation[0-9]+])\.', r'\1', updated_text)
    return updated_text.replace('  ', space).replace('\n ', space).strip()


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


def get_head_word(text: str) -> str:
    """
    Creates a spacy Doc from the input text and returns the text of the 'head'/root noun/verb.
    If the root is a noun and a proper name, this function assembles the full name.

    :param text: The text to parse
    :return: The text of the head/root; If the root is a noun and a proper name, this function
             assembles the full name and returns that as the text
    """
    doc = nlp(text)
    for token in doc:
        if token.dep_ == 'ROOT':
            if token.pos_ == 'PROPN':
                complete_names = [ch.text for ch in token.children if ch.dep_ == 'compound']
                complete_name = f'{space.join(complete_names)} {token.text}'.strip()
                if token.text != complete_name:
                    return complete_name
            return token.text
    # TODO: If the head word is connected via a conjunction to another noun/verb, then that text should added
    return empty_string


def parse_narrative(narr_text: str) -> (list, list, list):
    """
    Creates a spacy Doc from the narrative text, splitting it into sentences and separating out
    quotations. Each sentence is an instance of the Sentence Class and is returned in sentence_list
    (the first array in the returned tuple). Each quotation (with a subject and verb) is separated
    from the narrative text and separately saved in quotation_list (returned as the second array).
    Lastly, a list of all quoted strings in the text is returned as the third array.

    :param narr_text: The narrative text
    :return: A tuple consisting of three arrays - Sentence classes, Quotation classes and all quoted
             strings
    """
    narrative = narr_text.replace('\n', space).replace("  ", space)
    updated_narr, quotation_instance_list, quoted_strings_list = resolve_quotations(narrative)
    doc = nlp(updated_narr)
    sentence_instance_list = []
    sentence_offset = 0
    for sentence in doc.sents:
        sentence_offset += 1
        sentence_text = _update_token_separation(sentence.text.strip())
        # Determine if special punctuation is present (question and exclamation marks for now)
        # TODO: Other punctuation?
        punctuations = _get_punctuations(sentence_text)
        # Short sentences are mainly for reader effect and result in parsing problems - capture but ignore processing
        if len(sentence_text) < 3 or not any(c.isalnum() for c in sentence_text):
            # No NER or verb processing
            sentence_instance_list.append(Sentence(sentence_text, sentence_offset, [], punctuations, []))
            continue
        sentence_doc = nlp(sentence_text)
        # Get root and clausal verbs
        verb_list = [wd.text for wd in list(sentence_doc) if (wd.pos_ == 'VERB' or
                                                              (wd.pos_ == 'AUX' and wd.dep_ != 'aux'))]
        sentence_instance_list.append(Sentence(sentence_text, sentence_offset, _get_sentence_entities(sentence_doc),
                                               punctuations, verb_list))
    return sentence_instance_list, quotation_instance_list, quoted_strings_list


def resolve_quotations(narr: str) -> (str, list, list):
    """
    Process the quotations in the text - capture them and clean the text.

    :param narr: The original narrative text
    :return: A tuple with (1) a string holding the updated narrative text (cleaning the text and removing
             any quotations with a subj+verb, replacing the quote with the text 'Quotation#'), (2) a list
             of Quotation Class instances (removed from the updated narrative text, (1)) and (3) a list
             of all quoted strings in the text
    """
    # Determine what format is used to indicate a quotation (", right/left quotes, ...) and extract
    #     all quoted text
    quotations_list = [[], [], []]    # Array of arrays of the strings within different types of quotation marks
    # TODO: What about single quote (apostrophe)? Assume that they are used for only for possessives
    # TODO: Other quotation patterns?
    quotations_list[0] = re.findall(r"\u0022(.*?)\u0022", narr)        # Within double quotes
    quotations_list[1] = re.findall(r"\u2018(.*?)\u2019", narr)        # Within left/right single quotes
    quotations_list[2] = re.findall(r"\u201c(.*?)\u201d", narr)        # Within left/right double quotes
    lengths = [len(quotations_list[0]), len(quotations_list[1]), len(quotations_list[2])]
    if len([gt for gt in lengths if gt > 0]) > 0:   # Are there any quotes in the text? (any length > 0?)
        # Yes, but may have quotes within quotes
        # Assume that the quotation mark type with the largest count is the method for quoting
        index_max = max(range(len(lengths)), key=lengths.__getitem__)
        quotations = quotations_list[int(index_max)]   # List of quotations to be processed
    else:    # No left/right or double quotes
        return narr.replace('  ', space).replace('\n ', space).strip(), [], []
    # Create array of all quoted strings and another of all quotations that are sentences with subjs/objs
    # Also, update the narrative to remove quotation marks and all quotations that are sentences with subjs/objs
    index = 0
    quotation_instance_list = []       # Array of instances of the Quotation class
    quoted_string_list = []            # Array of all quoted strings
    updated_narr = narr                # Remove quotations from sentences due to influencing overall sentence sentiment
    for quoted_string in quotations:           # Process the individual quotations
        quote_doc = nlp(quoted_string)
        quote_verbs = [wd for wd in list(quote_doc) if wd.pos_ in ('VERB', 'AUX')]  # Root verb may be AUX
        verb_and_subj = False
        for quote_verb in quote_verbs:   # If any verb has a subject, then remove quoted text
            if any([wd for wd in quote_verb.children if 'subj' in wd.dep_]):
                verb_and_subj = True
                break
        if verb_and_subj:                # Have a subject+verb
            # Remove quote from narrative and replace with 'Quotation#'
            updated_narr = updated_narr.replace(quoted_string, f'[Quotation{index}]').strip()
            quotation_instance_list.append(
                Quotation(quoted_string, index, _get_sentence_entities(
                    nlp(quoted_string.replace('[', empty_string).replace(']', empty_string))),
                          _get_punctuations(quoted_string), [wd.text for wd in quote_verbs],
                          _get_quotation_attribution(narr, quoted_string)))
            index += 1
            # In the above, note that spacy may have issues with finding named entities if the names are
            #      enclosed by brackets
        # Always add the quote to the full list
        quoted_string_list.append(quoted_string)
    return _remove_tokens(updated_narr), quotation_instance_list, quoted_string_list
