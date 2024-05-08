import pytest
from dna.sentence_classes import Quotation, Entity
from dna.nlp import resolve_quotations

text_no_quotes = 'U.S. Rep. Liz Cheney conceded defeat Tuesday in the Republican primary in Wyoming, ' \
                 'an outcome that was a priority for former President Donald Trump.'
text_single_complete_quote = \
    '“No House seat, no office in this land is more important than the principles we swore to ' \
    'protect,” Ms. Cheney said in her concession speech.'
text_multiple_complete_quotes = \
    '“No House seat, no office in this land is more important than the principles we swore to ' \
    'protect,” Ms. Cheney said in her concession speech. “Our nation is barreling once again toward ' \
    'crisis, lawlessness and violence. No American should support election deniers.”'
text_coreference = 'U.S. Rep. Liz Cheney conceded defeat Tuesday in the Republican primary in Wyoming. ' \
                   'She said, "I lost."'
text_only_partial_quotes = \
    'After comparing herself to Lincoln, Cheney focused on the January 6 Capitol Riots and ' \
    'claimed that “America will never be the same” if Americans do not “hold those ' \
    'responsible to account.”'
text_complete_and_partial_quotes = \
    '“This is a wonderful result for America, and a complete rebuke of the Unselect Committee of ' \
    'political Hacks and Thugs,” Mr. Trump posted on Truth Social. “Now [Cheney] can finally ' \
    'disappear into the depths of political oblivion where, I am sure, she will be much happier ' \
    'than she is right now.” Trump reacted with “pure delight” over Ms. Cheney\'s loss.'
text_multiple_possible_speakers = \
    'That was evident in Ms. Cheney\'s paraphrase of a quote popularized by the Rev. Dr. Martin Luther King Jr. — ' \
    '“It has been said that the long arc of history bends toward justice and freedom. That’s true, but ' \
    'only if we make it bend” — and even more so a few minutes later, when she turned her attention to ' \
    'the Civil War.'


def test_no_quotes():
    updated_text, quotation_instance_list, quoted_strings = resolve_quotations(text_no_quotes)
    assert updated_text == text_no_quotes
    assert not quotation_instance_list and not quoted_strings


def test_single_complete_quote():
    updated_text, quotation_instance_list, quoted_strings = resolve_quotations(text_single_complete_quote)
    assert updated_text == '[Quotation0] Ms. Cheney said in her concession speech.'
    assert len(quoted_strings) == 1
    assert len(quotation_instance_list) == 1
    quotation0 = quotation_instance_list[0]
    assert quotation0.text == 'No House seat, no office in this land is more important than the principles ' \
                              'we swore to protect,'
    assert quoted_strings == ['No House seat, no office in this land is more important than the principles ' \
                              'we swore to protect,']
    assert quotation0.attribution == 'Ms. Cheney'
    assert quotation0.entities[0].text == 'House'
    assert quotation0.entities[0].ner_type == 'ORG'
    # Note that Cheney's name is not in the quotation, so it is not reported as an entity


def test_multiple_complete_quotes():
    updated_text, quotation_instance_list, quoted_strings = resolve_quotations(text_multiple_complete_quotes)
    assert updated_text == '[Quotation0] Ms. Cheney said in her concession speech. [Quotation1]'
    assert quoted_strings == [
        'No House seat, no office in this land is more important than the principles we swore to protect,',
        'Our nation is barreling once again toward crisis, lawlessness and violence. '
        'No American should support election deniers.']
    assert len(quotation_instance_list) == 2
    quotation0 = quotation_instance_list[0]
    assert quotation0.text == 'No House seat, no office in this land is more important than the ' \
                              'principles we swore to protect,'
    assert quotation0.attribution == 'Ms. Cheney'
    quotation1 = quotation_instance_list[1]
    assert quotation1.text == 'Our nation is barreling once again toward crisis, lawlessness and violence. ' \
                              'No American should support election deniers.'
    assert quotation1.attribution == 'Ms. Cheney'
    assert quotation1.entities[0].text == 'American'
    assert quotation1.entities[0].ner_type == 'NORP'


def test_coreference():
    updated_text, quotation_instance_list, quoted_strings = resolve_quotations(text_coreference)
    assert updated_text == 'U.S. Rep. Liz Cheney conceded defeat Tuesday in the Republican primary in Wyoming. ' \
                           'She said, [Quotation0]'
    assert quoted_strings == ['I lost.']
    assert len(quotation_instance_list) == 1
    quotation0 = quotation_instance_list[0]
    assert quotation0.text == 'I lost.'
    assert quotation0.attribution == 'Liz Cheney'
    assert quotation0.entities == []    # Note that the pronoun ('I') would not be returned as a named entity


def test_only_partial_quotes():
    updated_text, quotation_instance_list, quoted_strings = resolve_quotations(text_only_partial_quotes)
    assert updated_text == \
        'After comparing herself to Lincoln, Cheney focused on the January 6 Capitol Riots and claimed that ' \
        '[Quotation0] if Americans do not hold those responsible to account.'
    assert len(quoted_strings) == 2
    assert quoted_strings[1] == 'hold those responsible to account.'
    assert len(quotation_instance_list) == 1
    quotation0 = quotation_instance_list[0]
    assert quotation0.text == 'America will never be the same'
    assert quotation0.attribution == 'Cheney'
    assert quotation0.entities[0].text == 'America'
    assert quotation0.entities[0].ner_type == 'GPE'


def test_complete_and_partial_quotes():
    updated_text, quotation_instance_list, quoted_strings = resolve_quotations(text_complete_and_partial_quotes)
    assert updated_text == '[Quotation0] Mr. Trump posted on Truth Social. [Quotation1] ' \
                           'Trump reacted with pure delight over Ms. Cheney\'s loss.'
    assert quoted_strings == [
        'This is a wonderful result for America, and a complete rebuke of the Unselect Committee of ' \
        'political Hacks and Thugs,',
        'Now [Cheney] can finally disappear into the depths of political oblivion where, I am sure, ' \
        'she will be much happier than she is right now.',
        'pure delight']
    assert len(quotation_instance_list) == 2
    quotation0 = quotation_instance_list[0]
    assert quotation0.text == \
           'This is a wonderful result for America, and a complete rebuke of the Unselect Committee of ' \
           'political Hacks and Thugs,'
    assert quotation0.attribution == 'Mr. Trump'
    assert quotation0.entities[0].text == 'America'
    assert quotation0.entities[1].text == 'the Unselect Committee'
    # Hacks and/or Thugs may also be reported
    assert quotation_instance_list[1].text == \
           'Now [Cheney] can finally disappear into the depths of political oblivion where, I am sure, ' \
           'she will be much happier than she is right now.'
    assert quotation_instance_list[1].entities[0].text == 'Cheney'


def test_multiple_possible_speakers():
    updated_text, quotation_instance_list, quoted_strings = resolve_quotations(text_multiple_possible_speakers)
    assert updated_text == "That was evident in Ms. Cheney's paraphrase of a quote popularized by the Rev. " \
                           "Dr. Martin Luther King Jr. [Quotation0] and even more so a few minutes later, when " \
                           "she turned her attention to the Civil War."
    assert len(quoted_strings) == 1
    assert len(quotation_instance_list) == 1
    assert quotation_instance_list[0].text == \
           'It has been said that the long arc of history bends toward justice and freedom. That’s true, but only ' \
           'if we make it bend'
    assert quotation_instance_list[0].attribution == 'Ms. Cheney'
    assert quotation_instance_list[0].entities == []
