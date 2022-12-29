from dna.nlp import parse_narrative

sent_no_quotations = \
    'U.S. Rep. Liz Cheney conceded defeat Tuesday in the Republican primary in Wyoming, ' \
    'an outcome that was a priority for former President Donald Trump as he urged GOP voters ' \
    'to reject one of his most prominent critics on Capitol Hill.'
sent_percent = \
    'Harriet Hageman, a water and natural-resources attorney who was endorsed by the former president, ' \
    'won 66.3% of the vote to Ms. Cheney’s 28.9%, with 95% of all votes counted.'
sent_quotation = \
    '“No House seat, no office in this land is more important than the principles we swore to ' \
    'protect,” Ms. Cheney said in her concession speech.'
sent_dative = 'John gave Susan a raise of $3.20.'
sent_if = "If my child wants a dog, then she needs to be responsible. I will not take care of it."
sent_members_of = \
    'Cheney said her opposition to former President Donald Trump was rooted in “the principles” that ' \
    'members of congress are sworn to protect and that she “well understood the potential political ' \
    'consequences” of opposing Trump.'
sent_passive = 'Jane was loved by John.'
sent_compound_aux = 'I am having coffee with breakfast.'
sent_compound_xcomp1 = 'Sue attempted and failed to win the race.'
sent_compound_xcomp2 = 'Sue failed to finish or to win the race.'
sent_compound_xcomp_prt = 'Sue failed to give up her prize.'
sent_compound_prep_prep = 'George went along with the plan that Mary outlined.'
sent_loc_time = 'George lived in Detroit in 1980.'


def test_sent_no_quotations():
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(sent_no_quotations)
    assert not quotations and not quotations_dict
    assert len(sent_dicts) == 1
    first_dict = sent_dicts[0]
    assert first_dict['LOCS'] == ['U.S.+GPE', 'Wyoming+GPE'] and first_dict['AGENTS'] == \
           ['Liz Cheney+PERSON', 'Republican+NORP', 'Donald Trump+PERSON', 'GOP+ORG', 'Capitol Hill+ORG'] \
           and first_dict['TIMES'] == ['Tuesday']
    assert len(first_dict['chunks']) == 2
    assert first_dict['chunks'][0]['verbs'][0]['verb_lemma'] == 'reject'
    assert first_dict['chunks'][0]['verbs'][1]['verb_lemma'] == 'urge'
    assert first_dict['chunks'][1]['verbs'][0]['verb_lemma'] == 'concede'
    assert first_dict['chunks'][0]['verb_processing'] == ['xcomp > urge/urged, reject']
    assert 'verb_processing' not in first_dict['chunks'][1]
    first_dict_chunk1_verb = first_dict['chunks'][1]['verbs'][0]
    assert first_dict_chunk1_verb['preps'][0]['prep_details'][0]['preps'][0]['prep_details'][0]['detail_type'] == \
           'SINGGPE'


def test_sent_percent():
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(sent_percent)
    assert len(sent_dicts) == 1
    first_dict = sent_dicts[0]
    assert 'LOCS' not in first_dict and first_dict['AGENTS'] == ['Harriet Hageman+PERSON', 'Cheney+PERSON']
    assert len(first_dict['chunks']) == 2
    # First chunk is about 95% of the vote counted
    assert first_dict['chunks'][1]['verbs'][0]['verb_lemma'] == 'win'
    assert first_dict['chunks'][1]['verbs'][0]['objects'][0]['object_text'] == '66.3% of vote'
    assert len(first_dict['chunks'][1]['verbs'][0]['objects'][0]['preps']) == 1
    assert len(first_dict['chunks'][1]['verbs'][0]['preps']) == 1
    assert first_dict['chunks'][1]['verbs'][0]['preps'][0]['prep_text'] == 'to'
    assert first_dict['chunks'][1]['verbs'][0]['preps'][0]['prep_details'][0]['detail_text'] == 'Cheney/poss/ 28.9%'


def test_sent_quotation():
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(sent_quotation)
    assert len(sent_dicts) == 1
    assert len(quotations) == 1 and len(quotations_dict) == 1
    first_dict = sent_dicts[0]
    assert len(first_dict['chunks']) == 2
    assert first_dict['chunks'][0]['chunk_text'] == 'Quotation0'
    second_chunk = first_dict['chunks'][1]
    assert second_chunk['chunk_text'] == 'Ms. Cheney said in her concession speech'
    assert len(second_chunk['verbs']) == 1
    assert len(second_chunk['verbs'][0]['preps']) == 1


def test_sent_dative():
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(sent_dative)
    assert len(sent_dicts) == 1
    assert len(sent_dicts[0]['AGENTS']) == 2
    assert sent_dicts[0]['chunks'][0]['verbs'][0]['objects'][0]['object_text'] == 'Susan'
    assert sent_dicts[0]['chunks'][0]['verbs'][0]['objects'][1]['object_text'] == 'raise of $ 3.20'
    str0 = str(sent_dicts[0])
    assert '$3.20' in str0 and 'MONEY' in str0


def test_sent_if():
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(sent_if)
    assert len(sent_dicts) == 2
    assert not quotations and not quotations_dict
    first_dict = sent_dicts[0]
    assert len(first_dict['chunks']) == 2
    assert first_dict['chunks'][0]['chunk_text'] == 'my child wants a dog$&if'


def test_sent_members_of():
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(sent_members_of)
    assert len(sent_dicts) == 1
    first_dict = sent_dicts[0]
    assert len(first_dict['chunks']) == 4
    assert first_dict['chunks'][1]['verb_processing'][0] == 'xcomp > swear/sworn, protect'
    assert 'congress+ORG' in first_dict['AGENTS']


def test_sent_passive():
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(sent_passive)
    assert len(sent_dicts) == 1
    assert not quotations and not quotations_dict
    first_dict = sent_dicts[0]
    assert len(first_dict['chunks']) == 1
    assert 'objects' in first_dict['chunks'][0] and 'subjects' in first_dict['chunks'][0]


def test_sent_compound_aux():
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(sent_compound_aux)
    assert not quotations and not quotations_dict
    first_dict = sent_dicts[0]
    assert len(first_dict['chunks'][0]['verbs']) == 1


def test_sent_compound_xcomp1():
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(sent_compound_xcomp1)
    assert len(sent_dicts) == 1
    first_dict = sent_dicts[0]
    assert first_dict['chunks'][1]['verb_processing'] == ['xcomp > fail/failed, win']


def test_sent_compound_xcomp2():
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(sent_compound_xcomp2)
    assert len(sent_dicts) == 1
    first_dict = sent_dicts[0]
    assert 'xcomp > fail/failed, win' in first_dict['chunks'][0]['verb_processing']
    assert 'xcomp > fail/failed, finish' in first_dict['chunks'][0]['verb_processing']
    assert first_dict['chunks'][0]['verb_cc'] == 'or'


def test_sent_compound_xcomp_prt():
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(sent_compound_xcomp_prt)
    assert len(sent_dicts) == 1
    first_dict = sent_dicts[0]
    assert len(first_dict['chunks'][0]['verb_processing']) == 2
    assert 'xcomp > fail/failed, give' in first_dict['chunks'][0]['verb_processing']
    assert 'prt > give up' in first_dict['chunks'][0]['verb_processing']


def test_sent_compound_prep_prep():
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(sent_compound_prep_prep)
    assert len(sent_dicts[0]['chunks']) == 2
    first_dict = sent_dicts[0]
    assert len(first_dict['chunks'][1]['verbs'][0]['preps']) == 1
    assert first_dict['chunks'][1]['verbs'][0]['preps'][0]['prep_text'] == 'along with'
    assert first_dict['chunks'][1]['verbs'][0]['preps'][0]['prep_details'][0]['detail_text'] == 'plan'


def test_sent_loc_time():
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(sent_loc_time)
    assert len(sent_dicts[0]['chunks']) == 1
    first_dict = sent_dicts[0]
    assert len(first_dict['chunks'][0]['verbs'][0]['preps']) == 2
    assert 'George+PERSON' in first_dict['AGENTS'][0]
    assert 'Detroit+GPE' in first_dict['LOCS'][0]
    assert '1980' in first_dict['TIMES'][0]
    assert first_dict['chunks'][0]['verbs'][0]['preps'][0]['prep_details'][0]['detail_text'] == 'Detroit'
    assert first_dict['chunks'][0]['verbs'][0]['preps'][1]['prep_details'][0]['detail_text'] == '1980'


def test_multi_sentence_parse():
    sent_dicts, quotations, quotations_dict, family_dict = \
        parse_narrative(sent_no_quotations + '\n\n' + sent_percent + '\n\n' + sent_quotation)
    assert quotations[0] == \
           'No House seat, no office in this land is more important than the principles we swore to protect'
    assert len(sent_dicts) == 5
    assert 'New line' in sent_dicts[1]['text'] and 'New line' in sent_dicts[3]['text']
    assert 'Quotation' in sent_dicts[4]['chunks'][0]['chunk_text']
    assert sent_dicts[4]['chunks'][1]['verbs'][0]['verb_lemma'] == 'say'


def test_parse_news():
    with open(f'resources/LizCheney-FarRight.txt', 'r') as narr:
        narrative = narr.read()
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(narrative)
    assert len(quotations_dict) == 21
    assert len(quotations) > len(quotations_dict)


def test_parse_narrative():
    with open(f'resources/ErikaEckstut.txt', 'r') as narr:
        narrative = narr.read()
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(narrative)
    assert len(quotations_dict) == 0    # No quotations
    assert len(sent_dicts) == 21        # 21 sentences overall
    assert len(family_dict) == 1
    assert 'Beatrice' in family_dict
    assert 'sister' == family_dict['Beatrice']
