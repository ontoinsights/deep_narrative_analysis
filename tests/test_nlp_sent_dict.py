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
text_multiple_complete_quotes = \
    '“No House seat, no office in this land is more important than the principles we swore to ' \
    'protect,” Ms. Cheney said in her concession speech. “Our nation is barreling once again toward ' \
    'crisis, lawlessness and violence. No American should support election deniers.”'
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


def test_sent_no_quotations():
    sentence_classes, quotation_classes = parse_narrative(sent_no_quotations)
    assert not quotation_classes
    assert len(sentence_classes) == 1
    assert sentence_classes[0].text == sent_no_quotations
    sentence0 = sentence_classes[0]
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
    sentence_classes, quotation_classes = parse_narrative(sent_percent)
    assert len(sentence_classes) == 1
    sentence0 = sentence_classes[0]
    entities = sentence0.entities
    assert len(entities) == 2
    assert entities[0].text == 'Harriet Hageman' and entities[0].ner_type == 'PERSON'
    assert entities[1].text == 'Cheney' and entities[1].ner_type == 'PERSON'
    assert '3%' in sentence0.text and '5%' in sentence0.text


def test_sent_quotation1():
    sentence_classes, quotation_classes = parse_narrative(sent_quotation1)
    assert len(sentence_classes) == 1
    assert sentence_classes[0].text.startswith('In fact, she said')
    assert len(quotation_classes) == 1
    quotation0 = quotation_classes[0]
    assert quotation0.text == 'I lost'
    assert quotation0.attribution == 'she'
    assert not quotation0.entities


def test_sent_quotation2():
    sentence_classes, quotation_classes = parse_narrative(sent_quotation2)
    assert len(sentence_classes) == 1
    assert sentence_classes[0].text.endswith('Ms. Cheney said in her concession speech.')
    assert len(quotation_classes) == 1
    quotation0 = quotation_classes[0]
    assert quotation0.text.startswith('No House seat')
    assert quotation0.attribution == 'Ms. Cheney'


def test_sent_dative():
    sentence_classes, quotation_classes = parse_narrative(sent_dative)
    assert len(sentence_classes) == 1
    assert len(sentence_classes[0].entities) == 2


def test_sent_multiple_sentences():
    sentence_classes, quotation_classes = parse_narrative(sent_multiple_sentences)
    assert len(sentence_classes) == 2
    assert sentence_classes[1].text == 'I will not take care of it.'
    assert not quotation_classes


def test_sent_multiple_quotations():
    sentence_classes, quotation_classes = parse_narrative(sent_multiple_quotations)
    assert len(sentence_classes) == 2
    assert sentence_classes[1].text.startswith('She echoed')
    assert len(quotation_classes) == 2
    assert quotation_classes[0].text == 'well understood the potential political consequences'
    assert quotation_classes[0].attribution == 'Cheney'
    assert quotation_classes[1].text == 'I lost'
    assert quotation_classes[1].attribution == 'Cheney'


def test_multiple_complete_quotes():
    sentence_classes, quotation_classes = parse_narrative(text_multiple_complete_quotes)
    assert len(sentence_classes) == 3
    assert len(quotation_classes) == 2
    assert sentence_classes[0].text.endswith('Ms. Cheney said in her concession speech.')
    assert sentence_classes[0].text.startswith(
        '“No House seat, no office in this land is more important than the principles we swore to protect')
    assert sentence_classes[1].text.startswith('“Our nation is barreling')
    assert quotation_classes[0].attribution == 'Ms. Cheney'
    assert quotation_classes[0].text == \
        'No House seat, no office in this land is more important than the principles we swore to protect,'
    assert quotation_classes[1].text == \
        'Our nation is barreling once again toward crisis, lawlessness and violence. No American should ' \
        'support election deniers.'
    assert quotation_classes[1].attribution == 'Ms. Cheney'


def test_complete_and_partial_quotes():
    sentence_classes, quotation_classes = parse_narrative(text_complete_and_partial_quotes)
    assert len(sentence_classes) == 3
    assert len(quotation_classes) == 2
    assert sentence_classes[0].text.endswith('Mr. Trump posted on Truth Social.')
    assert sentence_classes[2].text.startswith('Trump reacted with')
    entities = []
    for sentence in sentence_classes:
        entities.extend([entity.text for entity in sentence.entities])
    assert 'Trump' in entities and 'Truth Social' in entities and 'America' in entities
    assert 'the Unselect Committee' in entities and 'Cheney' in entities
    assert quotation_classes[0].text == \
        'This is a wonderful result for America, and a complete rebuke of the Unselect Committee of ' \
        'political Hacks and Thugs,'
    assert quotation_classes[1].text == \
        'Now [Cheney] can finally disappear into the depths of political oblivion where, I am sure, ' \
        'she will be much happier than she is right now.'
    assert quotation_classes[0].attribution == 'Mr. Trump'
    assert quotation_classes[1].attribution == 'Mr. Trump'


def test_multiple_possible_speakers():
    sentence_classes, quotation_classes = parse_narrative(text_multiple_possible_speakers)
    assert len(sentence_classes) == 2
    assert len(quotation_classes) == 1
    assert sentence_classes[0].text.startswith("That was evident in Ms. Cheney's paraphrase")
    assert sentence_classes[0].text.endswith('bends toward justice and freedom.')
    assert sentence_classes[0].entities[0].text == 'Cheney'
    assert sentence_classes[0].entities[1].text == 'Martin Luther King Jr.'
    assert sentence_classes[1].entities[0].text == 'the Civil War'
    assert quotation_classes[0].text == \
           'It has been said that the long arc of history bends toward justice and freedom. That’s true, but only ' \
           'if we make it bend'
    assert quotation_classes[0].attribution == 'Ms. Cheney'
