import pytest
from dna.nlp import parse_narrative

sent_no_quotations = \
    'U.S. Rep. Liz Cheney conceded defeat Tuesday in the Republican primary in Wyoming, ' \
    'an outcome that was a priority for former President Donald Trump as he urged GOP voters ' \
    'to reject one of his most prominent critics on Capitol Hill.'
sent_percent = \
    'Harriet Hageman, a water and natural-resources attorney who was endorsed by the former president, ' \
    'won 66.3% of the vote to Ms. Cheney’s 28.9%, with 95% of all votes counted.'
sent_quotation1 = 'In fact, she said, "I lost".'
sent_quotation2 = \
    '“No House seat, no office in this land is more important than the principles we swore to ' \
    'protect,” Ms. Cheney said in her concession speech.'
sent_dative = 'John gave Susan a raise of $3.20.'
sent_multiple_sentences = "If my child wants a dog, then she needs to be responsible. I will not take care of it."
sent_multiple_quotations = \
    'Cheney said her opposition to former President Donald Trump was rooted in “the principles” that ' \
    'members of congress are sworn to protect and that she “well understood the potential political ' \
    'consequences” of opposing Trump. She echoed, “I lost”.'


def test_sent_no_quotations():
    sent_dicts, quotations, quotations_dict = parse_narrative(sent_no_quotations)
    assert not quotations and not quotations_dict
    assert len(sent_dicts) == 1
    first_dict = sent_dicts[0]
    entities = first_dict['entities']
    assert len(entities) == 8
    assert 'U.S.+GPE' in entities and 'Wyoming+GPE' in entities
    assert 'Liz Cheney+PERSON' in entities and 'Donald Trump+PERSON' in entities
    assert 'Tuesday+DATE' in entities
    assert 'Republican+NORP' in entities and 'GOP+ORG' in entities and 'Capitol Hill+ORG' in entities
    # Output, sentence dictionaries:
    # [{'offset': 1,
    #   'text': 'U.S. Rep. Liz Cheney conceded defeat Tuesday in the Republican primary in Wyoming,
    #           an outcome that was a priority for former President Donald Trump as he urged GOP voters to
    #           reject one of his most prominent critics on Capitol Hill.',
    #   'entities': ['U.S.+GPE', 'Liz Cheney+PERSON', 'Tuesday+DATE', 'Republican+NORP', 'Wyoming+GPE',
    #                'Donald Trump+PERSON', 'GOP+ORG', 'Capitol Hill+ORG']
    # }]


def test_sent_percent():
    sent_dicts, quotations, quotations_dict = parse_narrative(sent_percent)
    assert len(sent_dicts) == 1
    first_dict = sent_dicts[0]
    assert first_dict['entities'] == ['Harriet Hageman+PERSON', 'Cheney+PERSON']
    assert '3%' in first_dict['text'] and '5%' in first_dict['text']
    # Output, sentence_dictionaries:
    # [{'offset': 1,
    #   'text': 'Harriet Hageman, a water and natural-resources attorney who was endorsed by the former
    #            president, won 66.3% of the vote to Ms. Cheney’s 28.9%, with 95% of all votes counted.',
    #   'entities': ['Harriet Hageman+PERSON', 'Cheney+PERSON']
    # }]


def test_sent_quotation1():
    sent_dicts, quotations, quotations_dict = parse_narrative(sent_quotation1)
    assert len(sent_dicts) == 1
    assert len(quotations) == 1 and len(quotations_dict) == 1
    quote_text, speaker, entities = quotations_dict[':Quotation0']
    assert quote_text == 'I lost'
    assert speaker == 'she'
    assert not entities
    # Output, sentence dictionaries:
    # [{'offset': 1,
    #   'text': 'In fact, she said, [Quotation0]'
    # }]
    # Output, quotations array:
    # ['I lost']
    # Output, quotations dictionary:
    # {':Quotation0': ('I lost', 'she', [])}


def test_sent_quotation2():
    sent_dicts, quotations, quotations_dict = parse_narrative(sent_quotation2)
    assert len(sent_dicts) == 1
    assert len(quotations) == 1 and len(quotations_dict) == 1
    quote_text, speaker, entities = quotations_dict[':Quotation0']
    assert quote_text.startswith('No House seat')
    assert speaker == 'Ms. Cheney'
    assert entities[0] == 'House+ORG'
    # Output, sentence dictionaries:
    # [{'offset': 1,
    #   'text': '[Quotation0] Ms. Cheney said in her concession speech.',
    #   'entities': ['Cheney+PERSON']
    # }]
    # Output, quotations array:
    # ['No House seat, no office in this land is more important than the principles we swore to protect,']
    # Output, quotations dictionary:
    # {':Quotation0':      # Returns complete quotation, the speaker and any entities mentioned in the quote
    #     ('No House seat, no office in this land is more important than the principles we swore to protect,',
    #      'Ms. Cheney', ['House+ORG'])
    # }


def test_sent_dative():
    sent_dicts, quotations, quotations_dict = parse_narrative(sent_dative)
    assert len(sent_dicts) == 1
    assert len(sent_dicts[0]['entities']) == 2
    # Output:
    # [{'offset': 1,
    #   'text': 'John gave Susan a raise of $3.20.',
    #   'entities': ['John+PERSON', 'Susan+PERSON']
    # }]


def test_sent_multiple_sentences():
    sent_dicts, quotations, quotations_dict = parse_narrative(sent_multiple_sentences)
    assert len(sent_dicts) == 2
    assert not quotations and not quotations_dict
    # Output:
    # [{'offset': 1,
    #   'text': 'If my child wants a dog, then she needs to be responsible.'},
    #  {'offset': 2, 'text': 'I will not take care of it.'}
    # ]


def test_sent_multiple_quotations():
    sent_dicts, quotations, quotations_dict = parse_narrative(sent_multiple_quotations)
    assert len(sent_dicts) == 2
    assert sent_dicts[1]['text'] == 'She echoed, [Quotation0]'
    assert len(quotations) == 3
    assert quotations[0] == 'the principles'
    assert len(quotations_dict) == 1
    assert quotations_dict[':Quotation0'][1] == 'Cheney'
    # Output, sentence dictionaries:
    # [{'offset': 1,
    #   'text': 'Cheney said her opposition to former President Donald Trump was rooted in the principles
    #            that members of congress are sworn to protect and that she well understood the potential
    #            political consequences of opposing Trump.',
    #   'entities': ['Cheney+PERSON', 'Donald Trump+PERSON', 'congress+ORG', 'Trump+PERSON']},
    #  {'offset': 2, 'text': 'She echoed, [Quotation0]'}
    # ]
    # Output, quotations array:
    # ['the principles', 'well understood the potential political consequences', 'I lost']
    # Output, quotations dictionary:
    # {':Quotation0': ('I lost', 'Cheney', [])}
