import spacy
from spacy.matcher import DependencyMatcher

from utilities import months, add_to_dictionary_values, update_dictionary_count

nlp = spacy.load('en_core_web_trf')
nlp.add_pipe('sentencizer')
matcher = DependencyMatcher(nlp.vocab)

# "born ... on ... in ..."
born_date_pattern = [
  # anchor token: born
  {
    'RIGHT_ID': 'born1',
    'RIGHT_ATTRS': {'ORTH': 'born'}
  },
  # subject should be 'I'
  {
    'LEFT_ID': 'born1',
    'REL_OP': '>',
    'RIGHT_ID': 'I_born1',
    'RIGHT_ATTRS': {'ORTH': 'I'}
  },
  # date follows "born"
  {
    'LEFT_ID': 'born1',
    'REL_OP': '>>',
    'RIGHT_ID': 'born_date',
    'RIGHT_ATTRS': {'ENT_TYPE': 'DATE'}
  }
]

born_place_pattern = [
  # anchor token: born
  {
    'RIGHT_ID': 'born2',
    'RIGHT_ATTRS': {'ORTH': 'born'}
  },
  # subject should be 'I'
  {
    'LEFT_ID': 'born2',
    'REL_OP': '>',
    'RIGHT_ID': 'I_born2',
    'RIGHT_ATTRS': {'ORTH': 'I'}
  },
  # place follows "born"
  {
    'LEFT_ID': 'born2',
    'REL_OP': '>>',
    'RIGHT_ID': 'born_place',
    'RIGHT_ATTRS': {'ENT_TYPE': 'GPE'}
  }
]

matcher.add("born_date", [born_date_pattern])
matcher.add("born_place", [born_place_pattern])


def get_birth_details(narrative: str) -> (list, list):
    """
    Use spaCy Dependency Parsing to get the birth date and place details.

    :param narrative:
    :return:
    """
    # Analyze the text using spaCy and get matches to the 'born' rule
    doc = nlp(narrative[:1000])
    matches = matcher(doc)
    # Get born on and born in details from the matches
    born_on_date = set()
    born_in_place = set()
    # Each token_id corresponds to one pattern dict
    for match in matches:
        match_id, token_ids = match   # Indicates which pattern is matched and the specific tokens
        # Get the string representation
        string_id = nlp.vocab.strings[match_id]
        for i in range(len(token_ids)):
            if string_id == 'born_date' and born_date_pattern[i]["RIGHT_ID"] == 'born_date':
                born_on_date.add(doc[token_ids[i]].text)
            if string_id == 'born_place' and born_place_pattern[i]['RIGHT_ID'] == 'born_place':
                born_in_place.add(doc[token_ids[i]].text)
    # Verify that dates actually have a year
    found_year = False
    for value in born_on_date:
        if value.isnumeric() and int(value) > 1000:
            found_year = True
    if not found_year:
        born_on_date = set()
    return list(born_on_date), list(born_in_place)


def parse_narrative(narrative: str) -> list:
    """
    Parse a narrative text into sentences and detail if each sentence contains a date, and
    its nouns, verbs and objects.

    :param narrative:
    :return: A list of sentence dictionaries where the dictionary keys are:
             month, day, year, subject, verb and object
    """
    sentences = []
    doc = nlp(narrative)
    for sentence in doc.sents:
        sentence_dict = dict()
        for token in sentence:
            if token.ent_type_ == 'DATE':
                date_text = token.text
                if date_text in months:
                    sentence_dict['month'] = date_text
                if date_text.isnumeric():
                    if int(date_text) < 32:
                        sentence_dict['day'] = int(date_text)
                    else:
                        sentence_dict['year'] = int(date_text)
            elif token.dep_ == 'ROOT':
                sentence_dict['verb'] = token.text
                sentence_dict['verb_lemma'] = token.lemma_
                for child in token.children:
                    if 'subj' in child.dep_:
                        add_to_dictionary_values(sentence_dict, 'subject', child.text)
                    elif 'obj' in child.dep_ or 'attr' in child.dep_:
                        add_to_dictionary_values(sentence_dict, 'object', child.text)
                    elif 'prep' in child.dep_:
                        add_to_dictionary_values(sentence_dict, 'prep', child.text)
        sentences.append(sentence_dict)
    return sentences


def get_nouns_verbs(sentences: str) -> (dict, dict):
    """
    Parses all the sentences in the input parameter.

    :param sentences: String with the text of one or more sentences
    :return: Two dictionaries of the counts of the noun/verb lemmas
             The noun dictionary is returned first
    """
    noun_dict = dict()
    verb_dict = dict()
    doc = nlp(sentences)
    for sentence in doc.sents:
        for token in sentence:
            if token.pos_ in ('NOUN', 'PROPN'):
                update_dictionary_count(noun_dict, token.lemma_)
            if token.pos_ == 'VERB':
                update_dictionary_count(verb_dict, token.lemma_)
    sorted_nouns = dict(sorted(noun_dict.items(), key=lambda item: item[1], reverse=True))
    sorted_verbs = dict(sorted(verb_dict.items(), key=lambda item: item[1], reverse=True))
    return sorted_nouns, sorted_verbs
