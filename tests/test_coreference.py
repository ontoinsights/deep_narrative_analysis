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
    coref_dict = access_api(coref_prompt.replace('{sentences}', '').replace("{sent_text}", sent1))
    updated_text = coref_dict['updated_text']
    assert 'Donald Trump urged GOP voters' in updated_text


def test_sent1_sent2():
    coref_dict = access_api(coref_prompt.replace('{sentences}', sent1).replace("{sent_text}", sent2))
    updated_text = coref_dict['updated_text']
    assert 'Liz Cheney then compared Liz Cheney' in updated_text


def test_sent2_sent3_sent4():
    coref_dict = access_api(coref_prompt.replace('{sentences}', f'{sent2} {sent3}')
                            .replace("{sent_text}", sent4))
    updated_text = coref_dict['updated_text']
    assert 'Harriet Hageman did not lose' in updated_text


def test_sent5():
    coref_dict = access_api(coref_prompt.replace('{sentences}', '').replace("{sent_text}", sent5))
    updated_text = coref_dict['updated_text']
    assert 'Anna did not recognize' in updated_text


def test_sent6():
    coref_dict = access_api(coref_prompt.replace('{sentences}', '').replace("{sent_text}", sent6))
    updated_text = coref_dict['updated_text']
    assert 'Anna did not recognize' in updated_text
