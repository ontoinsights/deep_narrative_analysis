import spacy
from spacy.language import Language
from spacy.tokenizer import Tokenizer
from spacy.lang.char_classes import ALPHA, ALPHA_LOWER, ALPHA_UPPER, CONCAT_QUOTES, LIST_ELLIPSES, LIST_ICONS
from spacy.util import compile_infix_regex
from dna.nlp_split_sentences import split_clauses


# noinspection PyArgumentList
def custom_tokenizer(nlp_lang: Language):
    infixes = (
        LIST_ELLIPSES
        + LIST_ICONS
        + [
            r"(?<=[0-9])[+\-\*^](?=[0-9-])",
            r"(?<=[{al}{q}])\.(?=[{au}{q}])".format(
                al=ALPHA_LOWER, au=ALPHA_UPPER, q=CONCAT_QUOTES
            ),
            r"(?<=[{a}]),(?=[{a}])".format(a=ALPHA),
            # r"(?<=[{a}])(?:{h})(?=[{a}])".format(a=ALPHA, h=HYPHENS),   # Remove separation of words
            r"(?<=[{a}0-9])[:<>=/](?=[{a}])".format(a=ALPHA),
        ]
    )
    infix_re = compile_infix_regex(infixes)
    return Tokenizer(nlp_lang.vocab, prefix_search=nlp.tokenizer.prefix_search,
                     suffix_search=nlp.tokenizer.suffix_search, infix_finditer=infix_re.finditer,
                     token_match=nlp.tokenizer.token_match, rules=nlp.Defaults.tokenizer_exceptions)


nlp = spacy.load('en_core_web_trf')
nlp.tokenizer = custom_tokenizer(nlp)
nlp.add_pipe('sentencizer')

simple_subj_verb = 'Mary went to the store.'
simple_multi_subj_verb = 'Mary and John went to the store.'
simple_subj_verb_multi_obj = 'Mary went to the store and library.'
compound_percent = \
    'Harriet Hageman, a water and natural-resources attorney who was endorsed by the former president, ' \
    'won 66.3% of the vote to Ms. Cheney’s 28.9%, with 95% of all votes counted.'
compound_subj_multi_verb = 'Mary went to the store and took the bus home.'
compound_pass_subj_multi_verb = 'Mary was hit by a bus and went to the hospital.'
compound_multi_subj_multi_verb1 = 'Mary and John went to the store and took the bus home.'
compound_multi_subj_multi_verb2 = 'Mary and the injured John went to the store and took the bus home.'
compound_multi_subj_multi_verb3 = 'The injured Mary and the healthy John went to the store and took the bus home.'
compound_multi_subj_multi_verb_conj = 'Mary went to the store and John practiced guitar.'
compound_multi_subj_multi_verb_semi = 'Mary went to the store; John practiced guitar.'
compound_while_clause = 'While Mary reads comics, John reads the newspaper.'
compound_three_clauses = 'While Mary reads comics, John reads the newspaper, but Bob only looks at his phone.'
compound_relcl = 'I saw the book which you bought.'
compound_advcl = 'Mary bought a dress while studying in Thailand.'
compound_advcl_conj = 'Mary bought a dress while studying and traveling in Thailand.'
compound_advcl_because = 'Because Mary was lonely, John bought her flowers.'
compound_relcl_advcl = 'John mopped the floor with the dress Mary bought while studying in Thailand.'
compound_relcl_advcl_conj = \
    'John mopped the floor with the dress Mary bought while studying and traveling in Thailand.'
compound_news_text1 = \
    'U.S. Rep. Liz Cheney conceded defeat Tuesday in the Republican primary in Wyoming, an outcome that was a ' \
    'priority for former President Donald Trump.'
compound_news_text2 = \
    'U.S. Rep. Liz Cheney conceded defeat Tuesday in the Republican primary in Wyoming, an outcome that was a ' \
    'priority for former President Donald Trump as he urged GOP voters to reject one of his most prominent ' \
    'critics on Capitol Hill.'
compound_advcl_relcl_conj = 'Cheney said her opposition to former President Donald Trump was rooted in the ' \
                            'principles that members of congress are sworn to protect and that she well understood ' \
                            'the potential political consequences of opposing Trump.'
compound_relcl_who = 'She then compared herself to Lincoln who saved the nation during our Civil War.'
quotation_text1 = 'Quotation0 Cheney said.'
quotation_text2 = 'Quotation0 Cheney said. Quotation1 Quotation2 Cheney was saddened.'
quotation_and_removed = \
    'After comparing herself to Lincoln Cheney focused on the January 6 Capitol Riots and claimed that ' \
    'Quotation0 if Americans do not hold those responsible to account.'
location_dashes = \
    'She also claimed that Trump is promoting an insidious lie about the recent FBI raid of his ' \
    'Mar-a-Lago residence which will provoke violence and threats of violence.'
compound_conn_and_preposition = 'George went along with the plan that Mary outlined.'


def test_simple_subj_verb():
    new_sents = split_clauses(simple_subj_verb, nlp)
    assert new_sents[0] == simple_subj_verb[0:-1]


def test_simple_multi_subj_verb():
    new_sents = split_clauses(simple_multi_subj_verb, nlp)
    assert new_sents[0] == simple_multi_subj_verb[0:-1]


def test_simple_subj_verb_multi_obj():
    new_sents = split_clauses(simple_subj_verb_multi_obj, nlp)
    assert new_sents[0] == simple_subj_verb_multi_obj[0:-1]


def test_compound_percent():
    new_sents = split_clauses(compound_percent, nlp)
    assert new_sents[0] == '95 % of all votes counted'
    assert new_sents[1] == 'Harriet Hageman , a water and natural-resources attorney who was endorsed by ' \
                           'the former president , won 66.3 % of the vote to Ms. Cheney ’s 28.9 %'


def test_compound_subj_multi_verb():
    new_sents = split_clauses(compound_subj_multi_verb, nlp)
    assert new_sents[0] == 'Mary went to the store'
    assert new_sents[1] == 'Mary took the bus home'


def test_compound_pass_subj_multi_verb():
    new_sents = split_clauses(compound_pass_subj_multi_verb, nlp)
    assert new_sents[0] == 'Mary was hit by a bus'
    assert new_sents[1] == 'Mary went to the hospital'


def test_compound_multi_subj_multi_verb1():
    new_sents = split_clauses(compound_multi_subj_multi_verb1, nlp)
    assert new_sents[0] == 'Mary and John went to the store'
    assert new_sents[1] == 'Mary and John took the bus home'


def test_compound_multi_subj_multi_verb2():
    new_sents = split_clauses(compound_multi_subj_multi_verb2, nlp)
    assert new_sents[0] == 'Mary and the injured John went to the store'
    assert new_sents[1] == 'Mary and the injured John took the bus home'


def test_compound_multi_subj_multi_verb3():
    new_sents = split_clauses(compound_multi_subj_multi_verb3, nlp)
    assert new_sents[0] == 'The injured Mary and the healthy John went to the store'
    assert new_sents[1] == 'The injured Mary and the healthy John took the bus home'


def test_compound_multi_subj_multi_verb_conj():
    new_sents = split_clauses(compound_multi_subj_multi_verb_conj, nlp)
    assert new_sents[0] == 'Mary went to the store'
    assert new_sents[1] == 'John practiced guitar'


def test_compound_multi_subj_multi_verb_semi():
    new_sents = split_clauses(compound_multi_subj_multi_verb_semi, nlp)
    assert 'Mary went to the store' in new_sents and 'John practiced guitar' in new_sents


def test_compound_while_clause():
    new_sents = split_clauses(compound_while_clause, nlp)
    assert new_sents[0] == "Mary reads comics"
    assert new_sents[1] == "John reads the newspaper"


def test_compound_three_clauses():
    new_sents = split_clauses(compound_three_clauses, nlp)
    assert new_sents[0] == "Mary reads comics"
    assert new_sents[1] == "John reads the newspaper"
    assert new_sents[2] == "Bob only looks at his phone"


def test_compound_relcl():
    new_sents = split_clauses(compound_relcl, nlp)
    assert new_sents[0] == "you bought the book"
    assert new_sents[1] == "I saw the book"


def test_compound_advcl():
    new_sents = split_clauses(compound_advcl, nlp)
    assert new_sents[0] == "Mary studying in Thailand"
    assert new_sents[1] == "Mary bought a dress"


def test_compound_advcl_conj():
    new_sents = split_clauses(compound_advcl_conj, nlp)
    assert new_sents[0] == "Mary studying"
    assert new_sents[1] == "Mary traveling in Thailand"
    assert new_sents[2] == "Mary bought a dress"


def test_compound_advcl_because():
    new_sents = split_clauses(compound_advcl_because, nlp)
    assert new_sents[0] == "Mary was lonely$&because"
    assert new_sents[1] == "John bought her flowers"


def test_compound_relcl_advcl():
    new_sents = split_clauses(compound_relcl_advcl, nlp)
    assert new_sents[0] == "Mary studying in Thailand"
    assert new_sents[1] == "Mary bought the dress"
    assert new_sents[2] == "John mopped the floor with the dress"


def test_compound_relcl_advcl_conj():
    new_sents = split_clauses(compound_relcl_advcl_conj, nlp)
    assert new_sents[0] == "Mary studying"
    assert new_sents[1] == "Mary traveling in Thailand"
    assert new_sents[2] == "Mary bought the dress"
    assert new_sents[3] == "John mopped the floor with the dress"


def test_compound_news_text1():
    new_sents = split_clauses(compound_news_text1, nlp)
    assert new_sents[0] == "U.S. Rep. Liz Cheney conceded defeat Tuesday in the Republican primary in Wyoming, an " \
                           "outcome that was a priority for former President Donald Trump"


def test_compound_news_text2():
    new_sents = split_clauses(compound_news_text2, nlp)
    assert new_sents[0] == "he urged GOP voters to reject one of his most prominent critics on Capitol Hill"
    assert new_sents[1] == "U.S. Rep. Liz Cheney conceded defeat Tuesday in the Republican primary in Wyoming " \
                           ", an outcome that was a priority for former President Donald Trump"


def test_compound_advcl_relcl_conj():
    new_sents = split_clauses(compound_advcl_relcl_conj, nlp)
    assert "Cheney said" in new_sents
    assert "members of congress are sworn to protect the principles" in new_sents
    assert "her opposition to former President Donald Trump was rooted in the principles" in new_sents
    assert "she well understood the potential political consequences of opposing Trump" in new_sents


def test_compound_relcl_who():
    new_sents = split_clauses(compound_relcl_who, nlp)
    assert "Lincoln saved the nation during our Civil War" in new_sents
    assert "She then compared herself to Lincoln" in new_sents


def test_quotation1():
    new_sents = split_clauses(quotation_text1, nlp)
    assert new_sents[0] == "Quotation0"
    assert new_sents[1] == "Cheney said"


def test_quotation2():
    new_sents = split_clauses(quotation_text2, nlp)
    assert new_sents[0] == "Quotation0"
    assert new_sents[1] == "Cheney said"
    assert new_sents[2] == "Quotation1"
    assert new_sents[3] == "Quotation2"
    assert new_sents[4] == "Cheney was saddened"


def test_quotation_and_removed():
    new_sents = split_clauses(quotation_and_removed, nlp)
    assert new_sents[0] == "After comparing herself to Lincoln Cheney focused on the January 6 Capitol Riots"
    assert new_sents[3] == "Americans do not hold those responsible to account$&if"
    assert new_sents[1] == "Cheney claimed"
    assert new_sents[2] == "Quotation0"


def test_location_dashes():
    new_sents = split_clauses(location_dashes, nlp)
    assert new_sents[0] == \
           'the recent FBI raid of his Mar-a-Lago residence will provoke violence and threats of violence'
    assert new_sents[1] == 'She also claimed that Trump is promoting an insidious lie about the recent FBI ' \
                           'raid of his Mar-a-Lago residence'
    # Likely interpretation by a human but not certain; Not associated by spacy
    # assert new_sents[0] == 'an insidious lie about the recent FBI raid of his ' \
    #                        'Mar-a-Lago residence will provoke violence and threats of violence'


def test_compound_conn_and_preposition():
    new_sents = split_clauses(compound_conn_and_preposition, nlp)
    assert new_sents[0] == 'Mary outlined the plan'
    assert new_sents[1] == 'George went along with the plan'
