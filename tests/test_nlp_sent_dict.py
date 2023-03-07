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
sent_acomp_prep = 'John is tired of running.'
sent_compound_acomp = 'Mary is lonely and sad.'
sent_compound_objs = 'John loves lonely Mary and active Sue.'
sent_compound_aux = 'I am having coffee with breakfast.'
sent_compound_xcomp1 = 'Sue attempted and failed to win the race.'
sent_compound_xcomp2 = 'Sue failed to finish or to win the race.'
sent_compound_xcomp_prt = 'Sue failed to give up her prize.'
sent_compound_prt_prep = 'George went along with the plan that Mary outlined.'
sent_acomp_xcomp = "John is unable to stomach lies."
sent_acomp_xcomp2 = "John is unable to stomach lies or witness violence."
sent_compound_attr = 'Jane is an attorney or an active Republican.'
sent_compound_attr_acomp_xcomp = 'Jane is an attorney and is unable to stomach lies or handle stress.'
sent_loc_time = 'George lived in Detroit in 1980.'
sent_aux_obj_prep = 'Ms. Cheney was the last House Republican to face a primary.'


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
    # Output:
    # [{'offset': 1,
    #   'text': 'U.S. Rep. Liz Cheney conceded defeat Tuesday in the Republican primary in Wyoming, an outcome
    #            that was a priority for former President Donald Trump as he urged GOP voters to reject one of his
    #            most prominent critics on Capitol Hill.',
    #   'LOCS': ['U.S.+GPE', 'Wyoming+GPE'],
    #   'AGENTS': ['Liz Cheney+PERSON', 'Republican+NORP', 'Donald Trump+PERSON', 'GOP+ORG', 'Capitol Hill+ORG'],
    #   'TIMES': ['Tuesday'],
    #   'chunks': [{'chunk_text': 'he urged GOP voters to reject one of his most prominent critics on Capitol Hill',
    #           'verb_processing': ['xcomp > urge/urged, reject'],
    #           'subjects': [{'subject_text': 'he', 'subject_lemma': 'he', 'subject_type': 'MALESINGPERSON'}],
    #           'verbs': [{'verb_text': 'reject', 'verb_lemma': 'reject', 'tense': 'Pres',
    #                     'objects': [{'object_text': 'one of critics', 'object_lemma': 'one',
    #                          'object_type': 'CARDINAL', 'preps': [{'prep_text': 'of',
    #                               'prep_details': [{'detail_text': 'his/poss/ prominent critics on Hill',
    #                                   'detail_type': 'PLURALNOUN'}]}]}]},
    #               {'verb_text': 'urged', 'verb_lemma': 'urge', 'tense': 'Past',
    #                     'objects': [{'object_text': 'GOP voters', 'object_lemma': 'voter',
    #                            'object_type': 'PLURALNOUN'}]}]},
    #      {'chunk_text': 'U.S. Rep. Liz Cheney conceded defeat Tuesday in the Republican primary in Wyoming ,
    #                     an outcome that was a priority for former President Donald Trump',
    #           'subjects': [{'subject_text': 'Rep. Liz Cheney', 'subject_lemma': 'Cheney',
    #                'subject_type': 'FEMALESINGPERSON'}],
    #           'verbs': [{'verb_text': 'conceded', 'verb_lemma': 'concede', 'tense': 'Past',
    #                 'objects': [{'object_text': 'defeat', 'object_lemma': 'defeat', 'object_type': 'SINGNOUN'}],
    #                        'preps': [{'prep_text': 'in',
    #                               'prep_details': [{'detail_text': 'Republican primary in Wyoming',
    #                                     'detail_lemma': 'primary', 'detail_type': 'SINGNOUN',
    #                                     'preps': [{'prep_text': 'in',
    #                                           'prep_details': [{'detail_text': 'Wyoming',
    #                                                             'detail_type': 'SINGGPE'}]}]}]}]}]}]}]


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
    # Output:
    # [{'offset': 1,
    #   'text': 'Harriet Hageman, a water and natural-resources attorney who was endorsed by the former president,
    #            won 66.3% of the vote to Ms. Cheney’s 28.9%, with 95% of all votes counted.',
    #   'AGENTS': ['Harriet Hageman+PERSON', 'Cheney+PERSON'],
    #   'chunks': [{'chunk_text': '95 % of all votes counted',
    #           'subjects': [{'subject_text': '95% of votes', 'subject_lemma': '%', 'subject_type': 'SINGPERCENT',
    #                'preps': [{'prep_text': 'of', 'prep_details': [{'detail_text': 'votes',
    #                                                                'detail_type': 'PLURALNOUN'}]}]}],
    #           'verbs': [{'verb_text': 'counted', 'verb_lemma': 'count', 'tense': 'Past'}]},
    #      {'chunk_text': 'Harriet Hageman , a water and natural-resources attorney who was endorsed by
    #                      the former president , won 66.3 % of the vote to Ms. Cheney ’s 28.9 %',
    #           'subjects': [{'subject_text': 'Harriet Hageman , attorney', 'subject_lemma': 'Hageman',
    #                 'subject_type': 'FEMALESINGPERSON'}],
    #           'verbs': [{'verb_text': 'won', 'verb_lemma': 'win', 'tense': 'Past',
    #                  'objects': [{'object_text': '66.3% of vote', 'object_lemma': '%', 'object_type': 'SINGPERCENT',
    #                         'preps': [{'prep_text': 'of',
    #                              'prep_details': [{'detail_text': 'vote', 'detail_type': 'SINGNOUN'}]}]}],
    #                                    'preps': [{'prep_text': 'to',
    #                                         'prep_details': [{'detail_text': 'Cheney/poss/ 28.9%',
    #                                                 'detail_lemma': '%', 'detail_type': 'SINGPERCENT'}]}]}]}]}]


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
    # Output:
    # [{'offset': 1, 'text': 'Quotation0 Ms. Cheney said in her concession speech.',
    #   'AGENTS': ['Cheney+PERSON'],
    #   'chunks': [{'chunk_text': 'Quotation0', 'verb_processing': []},
    #       {'chunk_text': 'Ms. Cheney said in her concession speech',
    #             'subjects': [{'subject_text': 'Ms. Cheney', 'subject_lemma': 'Cheney',
    #                  'subject_type': 'FEMALESINGPERSON'}],
    #             'verbs': [{'verb_text': 'said', 'verb_lemma': 'say', 'tense': 'Past',
    #                   'preps': [{'prep_text': 'in',
    #                         'prep_details': [{'detail_text': 'her/poss/ concession speech',
    #                                           'detail_lemma': 'speech', 'detail_type': 'SINGNOUN'}]}]}]}]}]


def test_sent_dative():
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(sent_dative)
    assert len(sent_dicts) == 1
    assert len(sent_dicts[0]['AGENTS']) == 2
    assert sent_dicts[0]['chunks'][0]['verbs'][0]['objects'][0]['object_text'] == 'Susan'
    assert sent_dicts[0]['chunks'][0]['verbs'][0]['objects'][1]['object_text'] == 'raise of $ 3.20'
    str0 = str(sent_dicts[0])
    assert '$3.20' in str0 and 'MONEY' in str0
    # Output:
    # [{'offset': 1, 'text': 'John gave Susan a raise of $3.20.', 'AGENTS': ['John+PERSON', 'Susan+PERSON'],
    #   'chunks': [{'chunk_text': 'John gave Susan a raise of $3.20',
    #       'subjects': [{'subject_text': 'John', 'subject_lemma': 'John', 'subject_type': 'MALESINGPERSON'}],
    #       'verbs': [{'verb_text': 'gave', 'verb_lemma': 'give', 'tense': 'Past',
    #           'objects': [{'object_text': 'Susan', 'object_lemma': 'Susan', 'object_type': 'FEMALESINGPERSON'},
    #                  {'object_text': 'raise of $ 3.20', 'object_lemma': 'raise', 'object_type': 'SINGNOUN',
    #                         'preps': [{'prep_text': 'of',
    #                                    'prep_details': [{'detail_text': '$3.20', 'detail_type': 'MONEY'}]}]}]}]}]}]


def test_sent_if():
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(sent_if)
    assert len(sent_dicts) == 2
    assert not quotations and not quotations_dict
    first_dict = sent_dicts[0]
    assert len(first_dict['chunks']) == 2
    assert first_dict['chunks'][0]['chunk_text'] == 'my child wants a dog$&if'
    # Output:
    # [{'offset': 1, 'text': 'If my child wants a dog, then she needs to be responsible.',
    #   'chunks': [{'chunk_text': 'my child wants a dog$&if',
    #            'subjects': [{'subject_text': 'my/poss/ child', 'subject_lemma': 'child', 'subject_type': 'SINGNOUN'}],
    #            'verbs': [{'verb_text': 'wants', 'verb_lemma': 'want', 'tense': 'Pres',
    #                  'objects': [{'object_text': 'dog$&if', 'object_lemma': 'dog$&if', 'object_type': 'SINGNOUN'}]}]},
    #       {'chunk_text': 'then she needs to be responsible', 'verb_processing': ['xcomp > need/needs, be'],
    #            'subjects': [{'subject_text': 'she', 'subject_lemma': 'she', 'subject_type': 'FEMALESINGPERSON'}],
    #            'verbs': [{'verb_text': 'be', 'verb_lemma': 'be', 'tense': 'Pres',
    #                  'acomp': [{'detail_text': 'responsible', 'detail_lemma': 'responsible', 'detail_type': 'ADJ'}]},
    #               {'verb_text': 'needs', 'verb_lemma': 'need', 'tense': 'Pres'}]}]},
    #  {'offset': 2, 'text': 'I will not take care of it.',
    #   'chunks': [{'chunk_text': 'I will not take care of it',
    #       'subjects': [{'subject_text': 'I', 'subject_lemma': 'I', 'subject_type': 'SINGPERSON'}],
    #       'verbs': [{'verb_text': 'take', 'verb_lemma': 'take', 'tense': 'Fut', 'verb_aux': 'will', 'negation': True,
    #             'objects': [{'object_text': 'care', 'object_lemma': 'care', 'object_type': 'SINGNOUN'}],
    #             'preps': [{'prep_text': 'of', 'prep_details': [{'detail_text': 'it', 'detail_lemma': 'it',
    #                                                             'detail_type': 'SINGNOUN'}]}]}]}]}]


def test_sent_members_of():
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(sent_members_of)
    assert len(sent_dicts) == 1
    first_dict = sent_dicts[0]
    assert len(first_dict['chunks']) == 4
    assert first_dict['chunks'][1]['verb_processing'][0] == 'xcomp > swear/sworn, protect'
    assert 'congress+ORG' in first_dict['AGENTS']
    # Output:
    # [{'offset': 1,
    #   'text': 'Cheney said her opposition to former President Donald Trump was rooted in the principles that members
    #            of congress are sworn to protect and that she well understood the potential political consequences
    #            of opposing Trump.',
    #   'AGENTS': ['Cheney+PERSON', 'Donald Trump+PERSON', 'congress+ORG', 'Trump+PERSON'],
    #   'chunks': [{'chunk_text': 'Cheney said',
    #               'subjects': [{'subject_text': 'Cheney', 'subject_lemma': 'Cheney', 'subject_type': 'SINGPERSON'}],
    #               'verbs': [{'verb_text': 'said', 'verb_lemma': 'say', 'tense': 'Past'}]},
    #       {'chunk_text': 'members of congress are sworn to protect the principles',
    #               'verb_processing': ['xcomp > swear/sworn, protect'],
    #               'objects': [{'object_text': 'members of congress', 'object_lemma': 'member',
    #                      'object_type': 'PLURALNOUN',
    #                      'preps': [{'prep_text': 'of',
    #                                 'prep_details': [{'detail_text': 'congress', 'detail_type': 'SINGORG'}]}]}],
    #               'verbs': [{'verb_text': 'protect', 'verb_lemma': 'protect', 'tense': 'Pres',
    #                              'objects': [{'object_text': 'principles', 'object_lemma': 'principle',
    #                                     'object_type': 'PLURALNOUN'}]},
    #                    {'verb_text': 'sworn', 'verb_lemma': 'swear', 'tense': 'Past'}]},
    #       {'chunk_text': 'her opposition to former President Donald Trump was rooted in the principles',
    #            'objects': [{'object_text': 'her/poss/ opposition to Trump', 'object_lemma': 'opposition',
    #                       'object_type': 'SINGNOUN',
    #                       'preps': [{'prep_text': 'to',
    #                                  'prep_details': [{'detail_text': 'President Donald Trump',
    #                                        'detail_type': 'MALESINGPERSON'}]}]}],
    #            'verbs': [{'verb_text': 'rooted', 'verb_lemma': 'root', 'tense': 'Past',
    #                       'preps': [{'prep_text': 'in',
    #                                  'prep_details': [{'detail_text': 'principles',
    #                                        'detail_lemma': 'principle', 'detail_type': 'PLURALNOUN'}]}]}]},
    #       {'chunk_text': 'she well understood the potential political consequences of opposing Trump',
    #            'subjects': [{'subject_text': 'she', 'subject_lemma': 'she', 'subject_type': 'FEMALESINGPERSON'}],
    #            'verbs': [{'verb_text': 'understood', 'verb_lemma': 'understand', 'tense': 'Past',
    #                  'objects': [{'object_text': 'potential political consequences of opposing',
    #                               'object_lemma': 'consequence', 'object_type': 'PLURALNOUN'}]}]}]}]


def test_sent_passive():
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(sent_passive)
    assert len(sent_dicts) == 1
    assert not quotations and not quotations_dict
    first_dict = sent_dicts[0]
    assert len(first_dict['chunks']) == 1
    assert 'objects' in first_dict['chunks'][0] and 'subjects' in first_dict['chunks'][0]
    assert first_dict['chunks'][0]['objects'][0]['object_text'] == 'Jane'
    assert first_dict['chunks'][0]['subjects'][0]['subject_text'] == 'John'
    # Output:
    # [{'offset': 1, 'text': 'Jane was loved by John.', 'AGENTS': ['Jane+PERSON', 'John+PERSON'],
    #   'chunks': [{'chunk_text': 'Jane was loved by John',
    #        'objects': [{'object_text': 'Jane', 'object_lemma': 'Jane', 'object_type': 'FEMALESINGPERSON'}],
    #        'subjects': [{'subject_text': 'John', 'subject_lemma': 'John', 'subject_type': 'MALESINGPERSON'}],
    #        'verbs': [{'verb_text': 'loved', 'verb_lemma': 'love', 'tense': 'Past'}]}]}]


def test_sent_acomp_prep():
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(sent_acomp_prep)
    assert len(sent_dicts) == 1
    first_chunk = sent_dicts[0]['chunks'][0]
    assert 'objects' not in first_chunk
    assert 'acomp' in first_chunk['verbs'][0]
    assert first_chunk['verbs'][0]['acomp'][0]['detail_text'] == 'tired'
    assert first_chunk['verbs'][0]['acomp'][0]['detail_type'] == 'ADJ'
    assert first_chunk['verbs'][0]['acomp'][0]['full_text'] == 'tired of running'
    # Output:
    # [{'offset': 1, 'text': 'John is tired of running.', 'AGENTS': ['John+PERSON'],
    #   'chunks': [{'chunk_text': 'John is tired of running',
    #        'subjects': [{'subject_text': 'John', 'subject_lemma': 'John', 'subject_type': 'MALESINGPERSON'}],
    #        'verbs': [{'verb_text': 'is', 'verb_lemma': 'be', 'tense': 'Pres',
    #             'acomp': [{'detail_text': 'tired', 'detail_lemma': 'tired', 'detail_type': 'ADJ',
    #                        'full_text': 'tired of running'}]}]}]}]


def test_sent_compound_acomp():
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(sent_compound_acomp)
    assert len(sent_dicts) == 1
    first_dict = sent_dicts[0]
    assert len(first_dict['chunks']) == 1
    first_chunk = first_dict['chunks'][0]
    assert 'objects' not in first_chunk
    assert 'acomp_cc' in first_chunk['verbs'][0]
    assert len(first_chunk['verbs'][0]['acomp']) == 2
    assert first_chunk['verbs'][0]['acomp'][0]['detail_text'] == 'sad'
    assert first_chunk['verbs'][0]['acomp'][1]['detail_text'] == 'lonely'
    # Output:
    # [{'offset': 1, 'text': 'Mary is lonely and sad.', 'AGENTS': ['Mary+PERSON'],
    #   'chunks': [{'chunk_text': 'Mary is lonely and sad',
    #        'subjects': [{'subject_text': 'Mary', 'subject_lemma': 'Mary', 'subject_type': 'FEMALESINGPERSON'}],
    #        'verbs': [{'verb_text': 'is', 'verb_lemma': 'be', 'tense': 'Pres', 'acomp_cc': 'and',
    #        'acomp': [{'detail_text': 'sad', 'detail_lemma': 'sad', 'detail_type': 'ADJ'},
    #                  {'detail_text': 'lonely', 'detail_lemma': 'lonely', 'detail_type': 'ADJ'}]}]}]}]


def test_sent_compound_objs():
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(sent_compound_objs)
    assert len(sent_dicts) == 1
    assert not quotations and not quotations_dict
    first_dict = sent_dicts[0]
    assert len(first_dict['chunks']) == 1
    assert len(first_dict['chunks'][0]['verbs']) == 1
    assert 'objects' in first_dict['chunks'][0]['verbs'][0] and 'objects_cc' in first_dict['chunks'][0]['verbs'][0]
    assert len(first_dict['chunks'][0]['verbs'][0]['objects']) == 2
    object_texts = []
    for obj in first_dict['chunks'][0]['verbs'][0]['objects']:
        object_texts.append(obj['object_text'])
    assert 'lonely Mary' in object_texts and 'active Sue' in object_texts
    # Output:
    # [{'offset': 1, 'text': 'John loves lonely Mary and active Sue.',
    #   'AGENTS': ['John+PERSON', 'Mary+PERSON', 'Sue+PERSON'],
    #   'chunks': [{'chunk_text': 'John loves lonely Mary and active Sue',
    #        'subjects': [{'subject_text': 'John', 'subject_lemma': 'John', 'subject_type': 'MALESINGPERSON'}],
    #        'verbs': [{'verb_text': 'loves', 'verb_lemma': 'love', 'tense': 'Pres', 'objects_cc': 'and',
    #            'objects': [{'object_text': 'active Sue', 'object_lemma': 'Sue', 'object_type': 'FEMALESINGPERSON'},
    #                 {'object_text': 'lonely Mary', 'object_lemma': 'Mary', 'object_type': 'FEMALESINGPERSON'}]}]}]}]


def test_sent_compound_aux():
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(sent_compound_aux)
    first_dict = sent_dicts[0]
    assert len(first_dict['chunks'][0]['verbs']) == 1
    first_verb = first_dict['chunks'][0]['verbs'][0]
    assert first_verb['objects'][0]['object_text'] == 'coffee'
    assert first_verb['preps'][0]['prep_text'] == 'with'
    # Output:
    # [{'offset': 1, 'text': 'I am having coffee with breakfast.',
    #   'chunks': [{'chunk_text': 'I am having coffee with breakfast',
    #         'subjects': [{'subject_text': 'I', 'subject_lemma': 'I', 'subject_type': 'SINGPERSON'}],
    #         'verbs': [{'verb_text': 'having', 'verb_lemma': 'have', 'tense': 'Pres',
    #               'objects': [{'object_text': 'coffee', 'object_lemma': 'coffee', 'object_type': 'SINGNOUN'}],
    #               'preps': [{'prep_text': 'with', 'prep_details': [{'detail_text': 'breakfast',
    #                          'detail_lemma': 'breakfast', 'detail_type': 'SINGNOUN'}]}]}]}]}]


def test_sent_compound_xcomp1():
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(sent_compound_xcomp1)
    assert len(sent_dicts) == 1
    first_dict = sent_dicts[0]
    assert first_dict['chunks'][1]['verb_processing'] == ['xcomp > fail/failed, win']
    # Output:
    # [{'offset': 1, 'text': 'Sue attempted and failed to win the race.', 'AGENTS': ['Sue+PERSON'],
    #   'chunks': [{'chunk_text': 'Sue attempted',
    #           'subjects': [{'subject_text': 'Sue', 'subject_lemma': 'Sue', 'subject_type': 'FEMALESINGPERSON'}],
    #           'verbs': [{'verb_text': 'attempted', 'verb_lemma': 'attempt', 'tense': 'Past'}]},
    #      {'chunk_text': 'Sue failed to win the race', 'verb_processing': ['xcomp > fail/failed, win'],
    #           'subjects': [{'subject_text': 'Sue', 'subject_lemma': 'Sue', 'subject_type': 'FEMALESINGPERSON'}],
    #           'verbs': [{'verb_text': 'win', 'verb_lemma': 'win', 'tense': 'Pres',
    #                    'objects': [{'object_text': 'race', 'object_lemma': 'race', 'object_type': 'SINGNOUN'}]},
    #               {'verb_text': 'failed', 'verb_lemma': 'fail', 'tense': 'Past'}]}]}]


def test_sent_compound_xcomp2():
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(sent_compound_xcomp2)
    assert len(sent_dicts) == 1
    first_dict = sent_dicts[0]
    assert 'xcomp > fail/failed, win' in first_dict['chunks'][0]['verb_processing']
    assert 'xcomp > fail/failed, finish' in first_dict['chunks'][0]['verb_processing']
    assert first_dict['chunks'][0]['verb_cc'] == 'or'
    assert len(first_dict['chunks'][0]['verbs']) == 3
    # Output:
    # [{'offset': 1, 'text': 'Sue failed to finish or to win the race.', 'AGENTS': ['Sue+PERSON'],
    #   'chunks': [{'chunk_text': 'Sue failed to finish or to win the race',
    #        'verb_processing': ['xcomp > fail/failed, finish', 'xcomp > fail/failed, win'],
    #        'subjects': [{'subject_text': 'Sue', 'subject_lemma': 'Sue', 'subject_type': 'FEMALESINGPERSON'}],
    #        'verbs': [{'verb_text': 'finish', 'verb_lemma': 'finish', 'tense': 'Pres'},
    #             {'verb_text': 'win', 'verb_lemma': 'win', 'tense': 'Pres',
    #                   'objects': [{'object_text': 'race', 'object_lemma': 'race', 'object_type': 'SINGNOUN'}]},
    #             {'verb_text': 'failed', 'verb_lemma': 'fail', 'tense': 'Past'}], 'verb_cc': 'or'}]}]


def test_sent_compound_xcomp_prt():
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(sent_compound_xcomp_prt)
    assert len(sent_dicts) == 1
    first_dict = sent_dicts[0]
    assert len(first_dict['chunks'][0]['verb_processing']) == 2
    assert 'xcomp > fail/failed, give' in first_dict['chunks'][0]['verb_processing']
    assert 'prt > give up' in first_dict['chunks'][0]['verb_processing']
    # Output:
    # [{'offset': 1, 'text': 'Sue failed to give up her prize.', 'AGENTS': ['Sue+PERSON'],
    #   'chunks': [{'chunk_text': 'Sue failed to give up her prize',
    #        'verb_processing': ['xcomp > fail/failed, give', 'prt > give up'],
    #        'subjects': [{'subject_text': 'Sue', 'subject_lemma': 'Sue', 'subject_type': 'FEMALESINGPERSON'}],
    #        'verbs': [{'verb_text': 'give', 'verb_lemma': 'give', 'tense': 'Pres',
    #              'objects': [{'object_text': 'her/poss/ prize', 'object_lemma': 'prize', 'object_type': 'SINGNOUN'}]},
    #           {'verb_text': 'failed', 'verb_lemma': 'fail', 'tense': 'Past'}]}]}]


def test_sent_compound_prt_prep():
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(sent_compound_prt_prep)
    assert len(sent_dicts[0]['chunks']) == 2
    first_dict = sent_dicts[0]
    assert 'preps' not in first_dict['chunks'][0]['verbs'][0]
    assert 'objects' in first_dict['chunks'][0]['verbs'][0]
    assert 'preps' in first_dict['chunks'][1]['verbs'][0]
    assert 'verb_processing' in first_dict['chunks'][1]
    assert first_dict['chunks'][1]['verbs'][0]['preps'][0]['prep_text'] == 'with'
    assert first_dict['chunks'][1]['verbs'][0]['preps'][0]['prep_details'][0]['detail_text'] == 'plan'
    # Output:
    # [{'offset': 1, 'text': 'George went along with the plan that Mary outlined.',
    #   'AGENTS': ['George+PERSON', 'Mary+PERSON'],
    #   'chunks': [{'chunk_text': 'Mary outlined the plan',
    #         'subjects': [{'subject_text': 'Mary', 'subject_lemma': 'Mary', 'subject_type': 'FEMALESINGPERSON'}],
    #         'verbs': [{'verb_text': 'outlined', 'verb_lemma': 'outline', 'tense': 'Past',
    #             'objects': [{'object_text': 'plan', 'object_lemma': 'plan', 'object_type': 'SINGNOUN'}]}]},
    #     {'chunk_text': 'George went along with the plan', 'verb_processing': ['prt > go along'],
    #         'subjects': [{'subject_text': 'George', 'subject_lemma': 'George', 'subject_type': 'MALESINGPERSON'}],
    #         'verbs': [{'verb_text': 'went', 'verb_lemma': 'go', 'tense': 'Past',
    #             'preps': [{'prep_text': 'with', 'prep_details': [{'detail_text': 'plan',
    #                        'detail_type': 'SINGNOUN'}]}]}]}]}]


def test_sent_acomp_xcomp():
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(sent_acomp_xcomp)
    first_dict = sent_dicts[0]
    assert 'verb_processing' not in first_dict['chunks'][0]
    assert len(first_dict['chunks'][0]['verbs']) == 1
    first_verb = first_dict['chunks'][0]['verbs'][0]   # is
    assert first_verb['verb_text'] == 'is'
    assert len(first_verb['acomp']) == 1
    first_acomp = first_verb['acomp'][0]
    assert first_acomp['detail_text'] == 'unable'
    assert first_acomp['full_text'] == 'unable to stomach lies'
    # Output:
    # [{'offset': 1, 'text': 'John is unable to stomach lies.', 'AGENTS': ['John+PERSON'],
    #   'chunks': [{'chunk_text': 'John is unable to stomach lies',
    #        'subjects': [{'subject_text': 'John', 'subject_lemma': 'John', 'subject_type': 'MALESINGPERSON'}],
    #        'verbs': [{'verb_text': 'is', 'verb_lemma': 'be', 'tense': 'Pres',
    #         'acomp': [{'detail_text': 'unable', 'detail_lemma': 'unable', 'detail_type': 'ADJ',
    #                    'full_text': 'unable to stomach lies'}]}]}]}]
    # TODO: Further extract xcomp detail


def test_sent_acomp_xcomp2():
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(sent_acomp_xcomp2)
    first_dict = sent_dicts[0]
    assert 'verb_processing' not in first_dict['chunks'][0]
    assert len(first_dict['chunks'][0]['verbs']) == 1
    first_verb = first_dict['chunks'][0]['verbs'][0]    # is unable
    assert first_verb['verb_text'] == 'is'
    assert 'acomp' in first_verb
    assert first_verb['acomp'][0]['detail_text'] == 'unable'
    assert first_verb['acomp'][0]['full_text'] == 'unable to stomach lies or witness violence'
    # Output:
    # [{'offset': 1, 'text': 'John is unable to stomach lies or witness violence.', 'AGENTS': ['John+PERSON'],
    #   'chunks': [{'chunk_text': 'John is unable to stomach lies or witness violence',
    #       'subjects': [{'subject_text': 'John', 'subject_lemma': 'John', 'subject_type': 'MALESINGPERSON'}],
    #       'verbs': [{'verb_text': 'is', 'verb_lemma': 'be', 'tense': 'Pres',
    #              'acomp': [{'detail_text': 'unable', 'detail_lemma': 'unable', 'detail_type': 'ADJ',
    #                         'full_text': 'unable to stomach lies or witness violence'}]}]}]}]
    # TODO: Further extract xcomp details, conjunction, ...


def test_sent_compound_attr():
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(sent_compound_attr)
    first_dict = sent_dicts[0]
    assert 'objects' in first_dict['chunks'][0]['verbs'][0] and 'objects_cc' in first_dict['chunks'][0]['verbs'][0]
    assert first_dict['chunks'][0]['verbs'][0]['objects_cc'] == 'or'
    assert len(first_dict['chunks'][0]['verbs'][0]['objects']) == 2
    object_texts = []
    for obj in first_dict['chunks'][0]['verbs'][0]['objects']:
        object_texts.append(obj['object_text'])
    assert 'active Republican' in object_texts and 'attorney' in object_texts
    # Output:
    # [{'offset': 1, 'text': 'Jane is an attorney or a Republican.', 'AGENTS': ['Jane+PERSON', 'Republican+NORP'],
    #   'chunks': [{'chunk_text': 'Jane is an attorney or a Republican',
    #        'subjects': [{'subject_text': 'Jane', 'subject_lemma': 'Jane', 'subject_type': 'FEMALESINGPERSON'}],
    #        'verbs': [{'verb_text': 'is', 'verb_lemma': 'be', 'tense': 'Pres', 'objects_cc': 'or',
    #             'objects': [{'object_text': 'active Republican', 'object_lemma': 'Republican',
    #                          'object_type': 'SINGNORP'},
    #                     {'object_text': 'attorney', 'object_lemma': 'attorney', 'object_type': 'SINGNOUN'}]}]}]}]


def test_sent_compound_attr_acomp_xcomp():
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(sent_compound_attr_acomp_xcomp)
    first_dict = sent_dicts[0]
    assert len(first_dict['chunks']) == 2
    assert first_dict['chunks'][0]['verbs'][0]['verb_text'] == 'is'
    assert first_dict['chunks'][0]['verbs'][0]['objects'][0]['object_text'] == 'attorney'
    assert len(first_dict['chunks'][1]['verbs']) == 1
    assert 'acomp' in first_dict['chunks'][1]['verbs'][0]
    # Output:
    # [{'offset': 1, 'text': 'Jane is an attorney and is unable to stomach lies or handle stress.',
    #   'AGENTS': ['Jane+PERSON'],
    #   'chunks': [{'chunk_text': 'Jane is an attorney',
    #           'subjects': [{'subject_text': 'Jane', 'subject_lemma': 'Jane', 'subject_type': 'FEMALESINGPERSON'}],
    #           'verbs': [{'verb_text': 'is', 'verb_lemma': 'be', 'tense': 'Pres',
    #               'objects': [{'object_text': 'attorney', 'object_lemma': 'attorney', 'object_type': 'SINGNOUN'}]}]},
    #      {'chunk_text': 'Jane is unable to stomach lies or handle stress',
    #            'subjects': [{'subject_text': 'Jane', 'subject_lemma': 'Jane', 'subject_type': 'FEMALESINGPERSON'}],
    #            'verbs': [{'verb_text': 'is', 'verb_lemma': 'be', 'tense': 'Pres',
    #                    'acomp': [{'detail_text': 'unable', 'detail_lemma': 'unable', 'detail_type': 'ADJ',
    #                               'full_text': 'unable to stomach lies or handle stress'}]}]}]}]
    # TODO: Capture additional acomp text details


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
    # Output:
    # [{'offset': 1, 'text': 'George lived in Detroit in 1980.', 'AGENTS': ['George+PERSON'],
    #   'LOCS': ['Detroit+GPE'], 'TIMES': ['1980'],
    #   'chunks': [{'chunk_text': 'George lived in Detroit in 1980',
    #        'subjects': [{'subject_text': 'George', 'subject_lemma': 'George', 'subject_type': 'MALESINGPERSON'}],
    #        'verbs': [{'verb_text': 'lived', 'verb_lemma': 'live', 'tense': 'Past',
    #              'preps': [{'prep_text': 'in',
    #                         'prep_details': [{'detail_text': 'Detroit', 'detail_lemma': 'Detroit',
    #                                       'detail_type': 'SINGGPE'}]},
    #                        {'prep_text': 'in',
    #                         'prep_details': [{'detail_text': '1980', 'detail_lemma': '1980',
    #                                           'detail_type': 'DATE'}]}]}]}]}]


def test_sent_aux_obj_prep():
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(sent_aux_obj_prep)
    print(sent_dicts)
    assert len(sent_dicts[0]['chunks']) == 1
    first_dict = sent_dicts[0]
    assert 'preps' not in first_dict['chunks'][0]['verbs'][0]
    assert 'Cheney+PERSON' in first_dict['AGENTS']
    assert 'House+ORG' in first_dict['AGENTS']
    assert 'Republican+NORP' in first_dict['AGENTS']
    assert first_dict['chunks'][0]['verbs'][0]['objects'][0]['object_text'] == 'last House Republican'
    # Output:
    # [{'offset': 1, 'text': 'Ms. Cheney was the last House Republican to face a primary.',
    #  'AGENTS': ['Cheney+PERSON', 'House+ORG', 'Republican+NORP'],
    #  'chunks': [{'chunk_text': 'Ms. Cheney was the last House Republican to face a primary',
    #       'subjects': [{'subject_text': 'Ms. Cheney', 'subject_lemma': 'Cheney', 'subject_type': 'FEMALESINGPERSON'}],
    #       'verbs': [{'verb_text': 'was', 'verb_lemma': 'be', 'tense': 'Past',
    #            'objects': [{'object_text': 'last House Republican', 'object_lemma': 'Republican',
    #                         'object_type': 'SINGNORP'}]}]}]}]


def test_multi_sentence_parse():
    sent_dicts, quotations, quotations_dict, family_dict = \
        parse_narrative(sent_no_quotations + '\n\n' + sent_percent + '\n\n' + sent_quotation)
    assert quotations[0] == \
           'No House seat, no office in this land is more important than the principles we swore to protect'
    assert len(sent_dicts) == 5
    assert 'New line' in sent_dicts[1]['text'] and 'New line' in sent_dicts[3]['text']
    assert 'Quotation' in sent_dicts[4]['chunks'][0]['chunk_text']
    assert sent_dicts[4]['chunks'][1]['verbs'][0]['verb_lemma'] == 'say'
    # Output:
    # [{'offset': 1,
    #   'text': 'U.S. Rep. Liz Cheney conceded defeat Tuesday in the Republican primary in Wyoming an outcome
    #           that was a priority for former President Donald Trump as he urged GOP voters to reject one of his
    #           most prominent critics on Capitol Hill.',
    #   'LOCS': ['U.S.+GPE', 'Wyoming+GPE', 'Capitol Hill+LOC'],
    #   'AGENTS': ['Liz Cheney+PERSON', 'Republican+NORP', 'Donald Trump+PERSON', 'GOP+ORG'],
    #   'TIMES': ['Tuesday'],
    #   'chunks': [{'chunk_text': 'he urged GOP voters to reject one of his most prominent critics on Capitol Hill',
    #                   'verb_processing': ['xcomp > urge/urged, reject'],
    #                   'subjects': [{'subject_text': 'he', 'subject_lemma': 'he', 'subject_type': 'MALESINGPERSON'}],
    #                   'verbs': [{'verb_text': 'reject', 'verb_lemma': 'reject', 'tense': 'Pres',
    #                              'objects': [{'object_text': 'one of critics', 'object_lemma': 'one',
    #                                 'object_type': 'CARDINAL',
    #                                 'preps': [{'prep_text': 'of',
    #                                       'prep_details': [{'detail_text': 'his/poss/ prominent critics on Hill',
    #                                                         'detail_type': 'PLURALNOUN'}]}]}]},
    #                        {'verb_text': 'urged', 'verb_lemma': 'urge', 'tense': 'Past',
    #                               'objects': [{'object_text': 'GOP voters', 'object_lemma': 'voter',
    #                                  'object_type': 'PLURALNOUN'}]}]},
    #          {'chunk_text': 'U.S. Rep. Liz Cheney conceded defeat Tuesday in the Republican primary in Wyoming
    #                          an outcome that was a priority for former President Donald Trump',
    #                  'subjects': [{'subject_text': 'Rep. Liz Cheney', 'subject_lemma': 'Cheney',
    #                                'subject_type': 'FEMALESINGPERSON'}],
    #                  'verbs': [{'verb_text': 'conceded', 'verb_lemma': 'concede', 'tense': 'Past',
    #                       'objects': [{'object_text': 'defeat', 'object_lemma': 'defeat', 'object_type': 'SINGNOUN'}],
    #                       'preps': [{'prep_text': 'in',
    #                             'prep_details': [{'detail_text': 'Republican primary in Wyoming',
    #                                    'detail_lemma': 'primary', 'detail_type': 'SINGNOUN',
    #                                    'preps': [{'prep_text': 'in',
    #                                             'prep_details': [{'detail_text': 'Wyoming',
    #                                                               'detail_type': 'SINGGPE'}]}]}]}]}]}]},
    #  {'offset': 2, 'text': 'New line'},
    #  {'offset': 3,
    #   'text': 'Harriet Hageman a water and natural-resources attorney who was endorsed by the former president
    #            won 66.3 % of the vote to Ms. Cheney’s 28.9 % , with 95 % of all votes counted.',
    #   'AGENTS': ['Harriet Hageman+PERSON', 'Cheney+PERSON'],
    #   'chunks': [{'chunk_text': '95 % of all votes counted',
    #               'subjects': [{'subject_text': '95% of votes', 'subject_lemma': '%', 'subject_type': 'SINGPERCENT',
    #                   'preps': [{'prep_text': 'of', 'prep_details': [{'detail_text': 'votes',
    #                              'detail_type': 'PLURALNOUN'}]}]}],
    #               'verbs': [{'verb_text': 'counted', 'verb_lemma': 'count', 'tense': 'Past'}]},
    #       {'chunk_text': 'Harriet Hageman a water and natural-resources attorney who was endorsed by the
    #                       former president won 66.3 % of the vote to Ms. Cheney ’s 28.9 %',
    #               'subjects': [{'subject_text': 'Harriet Hageman attorney', 'subject_lemma': 'Hageman',
    #                             'subject_type': 'FEMALESINGPERSON'}],
    #               'verbs': [{'verb_text': 'won', 'verb_lemma': 'win', 'tense': 'Past',
    #                      'objects': [{'object_text': '66.3% of vote', 'object_lemma': '%',
    #                             'object_type': 'SINGPERCENT',
    #                             'preps': [{'prep_text': 'of', 'prep_details': [{'detail_text': 'vote',
    #                                       'detail_type': 'SINGNOUN'}]}]}],
    #                       'preps': [{'prep_text': 'to',
    #                             'prep_details': [{'detail_text': 'Cheney/poss/ 28.9%', 'detail_lemma': '%',
    #                                               'detail_type': 'SINGPERCENT'}]}]}]}]},
    #  {'offset': 4, 'text': 'New line'},
    #  {'offset': 5, 'text': 'Quotation0 Ms. Cheney said in her concession speech.', 'AGENTS': ['Cheney+PERSON'],
    #   'chunks': [{'chunk_text': 'Quotation0', 'verb_processing': []},
    #          {'chunk_text': 'Ms. Cheney said in her concession speech',
    #                'subjects': [{'subject_text': 'Ms. Cheney', 'subject_lemma': 'Cheney',
    #                              'subject_type': 'FEMALESINGPERSON'}],
    #                'verbs': [{'verb_text': 'said', 'verb_lemma': 'say', 'tense': 'Past',
    #                     'preps': [{'prep_text': 'in',
    #                          'prep_details': [{'detail_text': 'her/poss/ concession speech',
    #                                            'detail_lemma': 'speech', 'detail_type': 'SINGNOUN'}]}]}]}]}]
    # TODO: Additional assertions matching output above


def test_parse_news():
    with open(f'resources/LizCheney-FarRight.txt', 'r') as narr:
        narrative = narr.read()
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(narrative)
    assert len(quotations_dict) == 21
    assert len(quotations) > len(quotations_dict)
    # TODO: Assertions


def test_parse_narrative():
    with open(f'resources/ErikaEckstut.txt', 'r') as narr:
        narrative = narr.read()
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(narrative)
    assert len(quotations_dict) == 0    # No quotations
    assert len(sent_dicts) == 21        # 21 sentences overall
    assert len(family_dict) == 1
    assert 'Beatrice' in family_dict
    assert 'sister' == family_dict['Beatrice']
    # TODO: Assertions
