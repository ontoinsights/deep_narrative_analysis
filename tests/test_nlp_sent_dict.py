import pytest
from dna.sentence_classes import Sentence, Quotation
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
    sentence_instances, quotation_instances, quoted_strings = parse_narrative(sent_no_quotations)
    assert not quotation_instances and not quoted_strings
    assert len(sentence_instances) == 1
    assert sentence_instances[0].text == sent_no_quotations
    sentence0 = sentence_instances[0]
    entities = sentence0.entities
    assert len(entities) == 8
    assert entities[0].text == 'U.S.' and entities[0].ner_type == 'GPE'
    assert entities[1].text == 'Liz Cheney' and entities[1].ner_type == 'PERSON'
    assert entities[2].text == 'Tuesday' and entities[2].ner_type == 'DATE'
    assert entities[3].text == 'Republican' and entities[3].ner_type == 'NORP'
    assert entities[4].text == 'Wyoming' and entities[4].ner_type == 'GPE'
    assert entities[5].text == 'Donald Trump' and entities[5].ner_type == 'PERSON'
    assert entities[6].text == 'GOP' and entities[6].ner_type == 'ORG'
    assert entities[7].text == 'Capitol Hill' and entities[7].ner_type == 'ORG'


def test_sent_percent():
    sentence_instances, quotation_instances, quoted_strings = parse_narrative(sent_percent)
    assert len(sentence_instances) == 1
    sentence0 = sentence_instances[0]
    entities = sentence0.entities
    assert len(entities) == 2
    assert entities[0].text == 'Harriet Hageman' and entities[0].ner_type == 'PERSON'
    assert entities[1].text == 'Cheney' and entities[1].ner_type == 'PERSON'
    assert '3%' in sentence0.text and '5%' in sentence0.text


def test_sent_quotation1():
    sentence_instances, quotation_instances, quoted_strings = parse_narrative(sent_quotation1)
    assert len(sentence_instances) == 1
    assert sentence_instances[0].text == 'In fact, she said, [Quotation0]'
    assert len(quoted_strings) == 1 and len(quotation_instances) == 1
    quotation0 = quotation_instances[0]
    assert quotation0.text == 'I lost'
    assert quotation0.attribution == 'she'
    assert not quotation0.entities


def test_sent_quotation2():
    sentence_instances, quotation_instances, quoted_strings = parse_narrative(sent_quotation2)
    assert len(sentence_instances) == 1
    assert sentence_instances[0].text == '[Quotation0] Ms. Cheney said in her concession speech.'
    assert len(quoted_strings) == 1 and len(quotation_instances) == 1
    quotation0 = quotation_instances[0]
    assert quotation0.text.startswith('No House seat')
    assert quotation0.attribution == 'Ms. Cheney'
    assert quotation0.entities[0].text == 'House'
    assert quotation0.entities[0].ner_type == 'ORG'


def test_sent_dative():
    sentence_instances, quotation_instances, quoted_strings = parse_narrative(sent_dative)
    assert len(sentence_instances) == 1
    assert len(sentence_instances[0].entities) == 2


def test_sent_multiple_sentences():
    sentence_instances, quotation_instances, quoted_strings = parse_narrative(sent_multiple_sentences)
    assert len(sentence_instances) == 2
    assert sentence_instances[1].text == 'I will not take care of it.'
    assert not quotation_instances and not quoted_strings


def test_sent_multiple_quotations():
    sentence_instances, quotation_instances, quoted_strings = parse_narrative(sent_multiple_quotations)
    assert len(sentence_instances) == 2
    assert sentence_instances[0].text == \
           'Cheney said her opposition to former President Donald Trump was rooted in the principles that members ' \
           'of congress are sworn to protect and that she [Quotation0] of opposing Trump.'
    assert sentence_instances[1].text == 'She echoed, [Quotation1]'
    assert len(quoted_strings) == 3
    assert quoted_strings[0] == 'the principles'
    assert quoted_strings[1] == 'well understood the potential political consequences'
    assert quoted_strings[2] == 'I lost'
    assert len(quotation_instances) == 2
    # spaCy errors can result in the 2nd quote being a sentence
    assert quotation_instances[0].text == 'well understood the potential political consequences'
    assert quotation_instances[0].attribution == 'Cheney'
    assert quotation_instances[1].text == 'I lost'
    assert quotation_instances[1].attribution == 'Cheney'
