from dna.create_narrative_turtle import nouns_preload
from dna.process_entities import check_if_noun_is_known
from dna.query_openai import access_api, coref_prompt

sent1 = 'U.S. Rep. Liz Cheney conceded defeat Tuesday in the Republican primary in Wyoming, ' \
        'an outcome that was a priority for former President Donald Trump as he urged GOP voters ' \
        'to reject one of his most prominent critics on Capitol Hill.'
sent2 = 'She then compared herself to Abraham Lincoln, who saved the nation during our Civil War.'
sent3 = 'Harriet Hageman won the primary.'
sent4 = 'She did not lose.'
sent5 = 'Anna saw Heidi cut the roses, but she did not recognize that it was Heidi who cut the roses.'
sent6 = 'Anna saw that Heidi was cutting the roses but she did not recognize that it was Heidi who cut the roses.'


def test_sent1():
    coref_dict = access_api(coref_prompt.replace('{sentences}', sent1))
    updated_text = coref_dict['updated_sentences']
    assert 'Donald Trump urged GOP voters' in updated_text[0]


def test_sent1_sent2():
    coref_dict = access_api(coref_prompt.replace('{sentences}', f'{sent1} {sent2}'))
    updated_text = coref_dict['updated_sentences']
    print(updated_text)
    assert 'Liz Cheney then compared Liz Cheney' in updated_text[1]


def test_sent1_to_sent4():
    coref_dict = access_api(coref_prompt.replace('{sentences}', f'{sent1} {sent2} {sent3} {sent4}'))
    updated_text = coref_dict['updated_sentences']
    assert 'Harriet Hageman did not lose' in updated_text[3]


def test_sent5():
    coref_dict = access_api(coref_prompt.replace('{sentences}', sent5))
    updated_text = coref_dict['updated_sentences']
    assert 'Anna did not recognize' in updated_text[0]


def test_sent6():
    coref_dict = access_api(coref_prompt.replace('{sentences}', sent6))
    updated_text = coref_dict['updated_sentences']
    assert 'Anna did not recognize' in updated_text[0]
