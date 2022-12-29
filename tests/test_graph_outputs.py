from dna.create_narrative_turtle import create_graph
from dna.nlp import parse_narrative

sent_simple = 'U.S. Rep. Liz Cheney conceded defeat Tuesday in the Republican primary in Wyoming'
sent_xcomp1 = 'Harry tried to give up the prize.'
sent_xcomp2 = 'On Tuesday, in Wyoming, Trump urged GOP voters to reject one of his most prominent critics.'
sent_xcomp2a = 'Trump urged Republican voters to reject his critics.'
sent_xcomp3 = 'U.S. Rep. Liz Cheney conceded defeat Tuesday in the Republican primary in Wyoming, ' \
        'an outcome that was a priority for former President Donald Trump as he urged GOP voters ' \
        'to reject one of his most prominent critics on Capitol Hill.'
sent_aux_only = 'Liz Cheney is a neoconservative.'
sent_aux_and_verb = 'Liz Cheney was defeated Tuesday by Harriet Hageman.'
sent_possessive_and_aux = \
    'Liz Cheney’s loss marks a remarkable fall for a political family that has loomed large in ' \
    'Republican politics in the sparsely populated state for more than four decades. Her father is former ' \
    'Vice President Dick Cheney, who was elected to the House in 1978, where he served for a decade.'
sents = 'U.S. Rep. Liz Cheney conceded defeat Tuesday in the Republican primary in Wyoming, ' \
        'an outcome that was a priority for former President Donald Trump as he urged GOP voters ' \
        'to reject one of his most prominent critics on Capitol Hill.\n\n' \
        'Harriet Hageman, a water and natural-resources attorney who was endorsed by the former president, ' \
        'won 66.3% of the vote to Ms. Cheney’s 28.9%, with 95% of all votes counted.\n\n ' \
        '“No House seat, no office in this land is more important than the principles we swore to ' \
        'protect,” Ms. Cheney said in her concession speech. She also claimed that Trump is promoting ' \
        'an insidious lie about the recent FBI raid of his Mar-a-Lago residence, which will provoke ' \
        'violence and threats of violence.'
bug1 = 'While Mary exercised, John practiced guitar.'
bug2 = 'George went along with the plan that Mary outlined.'
bug3 = 'Rep. Liz Cheney R-WY compared herself to former President Abraham Lincoln during her concession speech ' \
       'shortly after her loss to Trump-backed Republican challenger Harriet Hageman.'
bug4 = 'Mary enjoyed being with her grandfather.'
bug5 = 'Mary can be with her grandfather on Tuesdays.'


def test_sent_simple():
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(sent_simple)
    success, graph_ttl = create_graph(sent_dicts, family_dict, '', True, False)
    assert success
    ttl_str = str(graph_ttl)
    assert '"Elizabeth Lynne Cheney"' in ttl_str        # Person alt name
    assert ':Liz_Cheney :gender "Female"' in ttl_str    # Gender capture
    assert '"WY"' in ttl_str                            # Abbreviation for location
    assert 'geo:6252001 :has_component :Wyoming' in ttl_str    # Wyoming located in US
    assert ':PiT_DayTuesday a :PointInTime ; rdfs:label "Tuesday"' in ttl_str    # Time capture
    # Following are shown in the output pasted below
    assert ':has_topic :republican_primary_' in ttl_str
    assert ':has_topic :defeat_' in ttl_str
    assert ':has_active_agent :Liz_Cheney' in ttl_str
    assert 'a :SurrenderAndYielding' in ttl_str         # Mapping for conceded
    assert 'a :Failure' in ttl_str                      # Mapping for defeat
    assert 'a :Election' in ttl_str                     # Mapping for primary
    assert ':has_time :PiT_DayTuesday' in ttl_str
    assert ':has_location' not in ttl_str
    assert 'Republican primary in Wyoming in Republican primary in Wyoming' not in ttl_str
    # Output:
    # :Chunk_be193c95-826d a :Chunk ; :offset 1 .
    # :Chunk_be193c95-826d :text "U.S. Rep. Liz Cheney conceded defeat Tuesday in the Republican primary in Wyoming" .
    # :Event_b6162062-7ad6 :has_time :PiT_DayTuesday .
    # :defeat_5629d0d1_b706 a :Failure .
    # :defeat_5629d0d1_b706 rdfs:label "defeat" .
    # :republican_primary_in_wyoming_e8f8c661_f274 a :Election .
    # :republican_primary_in_wyoming_e8f8c661_f274 rdfs:label "Republican primary in Wyoming" .
    # :Event_b6162062-7ad6 :has_topic :republican_primary_in_wyoming_e8f8c661_f274 .
    # :Event_b6162062-7ad6 a :SurrenderAndYielding .
    # :Event_b6162062-7ad6 :has_active_agent :Liz_Cheney .
    # :Event_b6162062-7ad6 :has_topic :defeat_5629d0d1_b706 .
    # :Event_b6162062-7ad6 rdfs:label "Liz Cheney conceded defeat, in Republican primary in Wyoming" .
    # :Chunk_be193c95-826d :describes :Event_b6162062-7ad6 .'


def test_sent_xcomp1():
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(sent_xcomp1)
    success, graph_ttl = create_graph(sent_dicts, family_dict, '', True, False)
    ttl_str = str(graph_ttl)
    print(ttl_str)
    assert '"Harry"' in ttl_str                  # Person alt name
    assert ':Harry :gender "Male"' in ttl_str    # Gender capture
    # Following are shown in the output pasted below
    assert ':has_topic :prize_' in ttl_str
    assert ':has_active_agent :Harry' in ttl_str
    assert 'a :Attempt' in ttl_str                      # Mapping for tried
    assert 'a :SurrenderAndYielding' in ttl_str         # Mapping for give up
    assert ':has_time' not in ttl_str
    assert ':has_location' not in ttl_str
    assert 'Harry tried to give up the prize' in ttl_str
    # Output:
    # :Chunk_6eeea672-9d51 a :Chunk ; :offset 1 .
    # :Chunk_6eeea672-9d51 :text "Harry tried to give up the prize" .
    # :Chunk_6eeea672-9d51 :describes :Event_656905bc-0770 .
    # :prize_a8ace05f-2908 a :RewardAndCompensation .
    # :prize_a8ace05f-2908 rdfs:label "prize" .
    # :Event_656905bc-0770 a :Attempt .
    # :Event_656905bc-0770 a :SurrenderAndYielding .
    # :Event_656905bc-0770 :has_active_agent :Harry .
    # :Event_656905bc-0770 :has_topic :prize_a8ace05f-2908 .
    # :Event_656905bc-0770 rdfs:label "Harry tried to give up the prize" .


def test_sent_xcomp2():
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(sent_xcomp2)
    success, graph_ttl = create_graph(sent_dicts, family_dict, '', True, False)
    assert success
    ttl_str = str(graph_ttl)
    assert '"Trump"' in ttl_str
    # Following are shown in the output pasted below
    assert '"GOP voters"' in ttl_str
    assert ':RequestAndAppeal' in ttl_str                # Mapping for urging
    assert ':RefusalAndRejection' in ttl_str             # Mapping for reject
    assert ':has_topic :Event_' in ttl_str               # Topic of the urging (another event = rejection)
    assert ':has_active_agent :gop_voters_' in ttl_str   # Voters reject
    assert ':has_active_agent :Trump' in ttl_str             # Trump urged
    assert ':has_affected_agent :gop_voters_' in ttl_str     # Voters were urged
    assert 'a :OpportunityAndPossibility' in ttl_str         # Urging does not mean that the 'topic' event happens
    assert 'Trump urged GOP voters' in ttl_str           # Verify labels
    assert 'GOP voters reject one' in ttl_str
    assert 'a :Affiliation' in ttl_str                   # Affiliation of the voters to the GOP
    assert ':affiliated_agent :gop_voters' in ttl_str and ':affiliated_with :GOP' in ttl_str
    # Output:
    # :Chunk_22755898-623d a :Chunk ; :offset 1 .
    # :Chunk_22755898-623d :text "On Tuesday, in Wyoming, Trump urged GOP voters to reject one of his
    #                             most prominent critics" .
    # :Event_c966d908-db52 :has_topic :Event_f90d9252-65bd .
    # :Event_c966d908-db52 :has_time :PiT_DayTuesday .
    # :gop_voters_0685e457_e868 :has_context :Election .
    # :gop_voters_0685e457_e868_GOP_Affiliation a :Affiliation ; :affiliated_with :GOP ;
    #                                           :affiliated_agent :gop_voters_0685e457_e868 .
    # :gop_voters_0685e457_e868_GOP_Affiliation rdfs:label "Relationship based on the text, \'GOP voters\'" .
    # :gop_voters_0685e457_e868 a :Person, :Collection .
    # :gop_voters_0685e457_e868 rdfs:label "GOP voters" .
    # :prominent_critics_84802128_b8c2 :has_context :Complaint .
    # :prominent_critics_84802128_b8c2 a :Person .
    # :prominent_critics_84802128_b8c2 rdfs:label "one of critics" .
    # :Event_f90d9252-65bd a :RefusalAndRejection .
    # :Event_f90d9252-65bd :has_active_agent :gop_voters_0685e457_e868 .
    # :Event_f90d9252-65bd :has_affected_agent :prominent_critics_84802128_b8c2 .
    # :Event_f90d9252-65bd rdfs:label "GOP voters reject one of critics" .
    # :Chunk_22755898-623d :describes :Event_f90d9252-65bd .
    # :Event_c966d908-db52 :has_location :Wyoming .
    # :Event_c966d908-db52 a :RequestAndAppeal .
    # :Event_c966d908-db52 :has_active_agent :Trump .
    # :Event_c966d908-db52 :has_affected_agent :gop_voters_0685e457_e868 .
    # :Event_c966d908-db52 rdfs:label "Trump urged GOP voters" .
    # :Chunk_22755898-623d :describes :Event_c966d908-db52 .
    # :Event_f90d9252-65bd a :OpportunityAndPossibility .


def test_sent_xcomp2a():
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(sent_xcomp2a)
    success, graph_ttl = create_graph(sent_dicts, family_dict, '', True, False)
    assert success
    ttl_str = str(graph_ttl)
    print(ttl_str)
    # Following are shown in the output pasted below
    assert '"Republican voters"' in ttl_str
    assert ':RequestAndAppeal' in ttl_str                # Mapping for urging
    assert ':RefusalAndRejection' in ttl_str             # Mapping for reject
    assert ':has_topic :Event_' in ttl_str               # Topic of the urging (another event = rejection)
    assert ':has_active_agent :republican_voters_' in ttl_str   # Voters reject
    assert ':has_active_agent :Trump' in ttl_str             # Trump urged
    assert ':has_affected_agent :republican_voters_' in ttl_str     # Voters were urged
    # TODO: Republican is captured as amod only, not compound; Check adj modifiers for affiliation
    assert 'a :Affiliation' not in ttl_str
    # assert ':affiliated_agent :republican_voters' in ttl_str and ':affiliated_with :Republican' in ttl_str
    # Output similar to above


def test_sent_xcomp3():
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(sent_xcomp3)
    success, graph_ttl = create_graph(sent_dicts, family_dict, '', True, False)
    assert success
    ttl_str = str(graph_ttl)
    print(ttl_str)
    assert '"Trump"' in ttl_str
    # Following are shown in the output pasted below
    assert ':has_time :PiT_DayTuesday' in ttl_str
    assert ':has_location' not in ttl_str
    assert '"GOP voters"' in ttl_str
    assert ':RequestAndAppeal' in ttl_str                # Mapping for urging
    assert ':RefusalAndRejection' in ttl_str             # Mapping for reject
    assert ':has_active_agent :gop_voters_' in ttl_str   # Voters reject
    assert ':has_active_agent :Donald_Trump' in ttl_str            # Trump urged
    assert ':has_affected_agent :gop_voters_' in ttl_str           # Voters were urged
    assert ':has_topic :Event_' in ttl_str    # Topic of urging
    assert 'a :OpportunityAndPossibility' in ttl_str             # Urging does not mean that the xcomp event happens
    assert ':republican_primary_' in ttl_str and 'a :Election' in ttl_str
    assert 'a :SurrenderAndYielding' in ttl_str           # Cheney conceded
    assert 'a :Failure' in ttl_str                        # Defeat
    assert ':has_topic :defeat_'                          # Topic of concession
    assert ':has_topic :republican_primary_'              # Topic of concession
    # Output as for xcomp1 and xcomp2 combined


def test_sent_aux_only():
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(sent_aux_only)
    success, graph_ttl = create_graph(sent_dicts, family_dict, '', True, False)
    assert success
    ttl_str = str(graph_ttl)
    print(ttl_str)
    assert 'a :EnvironmentAndCondition ; :has_topic :Conservatism' in ttl_str
    assert ':has_holder :Liz_Cheney' in ttl_str
    assert ':Liz_Cheney :has_agent_aspect :Conservatism ; :agent_aspect "neoconservative"' in ttl_str
    assert 'rdfs:label "Describes that Liz Cheney has an aspect of neoconservative"' in ttl_str
    assert ':neoconservative_' not in ttl_str      # Is unused since the mapping is to an EnvAndCondition
    # Output:
    # :Chunk_4a58c6bc-abd2 a :Chunk ; :offset 1 .
    # :Chunk_4a58c6bc-abd2 :text "Liz Cheney is a neoconservative" .
    # :Chunk_4a58c6bc-abd2 :sentiment 0.0 .
    # :Chunk_4a58c6bc-abd2 :describes :Event_84a7d9d1-2d6f .
    # :Event_84a7d9d1-2d6f a :EnvironmentAndCondition ; :has_topic :Conservatism .
    # :Liz_Cheney :has_agent_aspect :Conservatism ; :agent_aspect "neoconservative" .
    # :Event_84a7d9d1-2d6f :has_holder :Liz_Cheney.
    # :Event_84a7d9d1-2d6f rdfs:label "Describes that Liz Cheney has an aspect of neoconservative" .


def test_sent_aux_and_verb():
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(sent_aux_and_verb)
    success, graph_ttl = create_graph(sent_dicts, family_dict, '', True, False)
    assert success
    ttl_str = str(graph_ttl)
    print(ttl_str)
    assert ':Harriet_Hageman :gender "Female"' in ttl_str    # Gender capture
    assert ':Liz_Cheney :gender "Female"' in ttl_str         # Gender capture
    # Following are shown in the output pasted below
    assert 'a :Success' in ttl_str                                 # Mapping for 'was defeated', reversing subj/obj
    assert ':has_active_agent :Harriet_Hageman' in ttl_str
    assert ':has_affected_agent :Liz_Cheney' in ttl_str
    assert ':has_time' in ttl_str
    assert ':has_location' not in ttl_str
    # Output:
    # Chunk_b894a019-1af7 a :Chunk ; :offset 1 .
    # :Chunk_b894a019-1af7 :text "Liz Cheney was defeated Tuesday by Harriet Hageman" .
    # :Event_3ce85fd5-19cd :has_time :PiT_DayTuesday .
    # :Event_3ce85fd5-19cd a :Success .
    # :Event_3ce85fd5-19cd :has_active_agent :Harriet_Hageman .
    # :Event_3ce85fd5-19cd :has_affected_agent :Liz_Cheney .
    # :Event_3ce85fd5-19cd rdfs:label "Harriet Hageman defeated Liz Cheney" .
    # :Chunk_b894a019-1af7 :describes :Event_3ce85fd5-19cd .


def test_sent_possessive_and_aux():
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(sent_possessive_and_aux)
    success, graph_ttl = create_graph(sent_dicts, family_dict, '', True, False)
    ttl_str = str(graph_ttl)
    print(ttl_str)
    # TODO: Add assertion details
    # :Chunk_baa5049a-e42c a :Chunk ; :offset 1 .
    # :Chunk_baa5049a-e42c :text "a political family has loomed large in Republican politics in the
    #                             sparsely populated state for more than four decades" .
    # :Chunk_baa5049a-e42c :sentiment -0.2732 .
    # :Event_01d9bcf4-14cb :has_time :PiT_more_than_four_decades .
    # :political_family_27dc3bb4_f1cb a :Person, :Collection .
    # :political_family_27dc3bb4_f1cb rdfs:label "political family" .
    # :republican_politics_d757f9df_1b6c a :PoliticalIdeology, :Collection .
    # :republican_politics_d757f9df_1b6c rdfs:label "Republican politics" .
    # :Event_01d9bcf4-14cb :has_topic :republican_politics_d757f9df_1b6c .
    # :sparsely_populated_state_86c1aefd_4bf3 a :AdministrativeDivision .
    # :sparsely_populated_state_86c1aefd_4bf3 rdfs:label "sparsely populated state" .
    # :Event_01d9bcf4-14cb :has_topic :sparsely_populated_state_86c1aefd_4bf3 .
    # :Event_01d9bcf4-14cb a :EventAndState .   TODO: loomed
    # :Event_01d9bcf4-14cb :has_active_agent :political_family_27dc3bb4_f1cb .
    # :Event_01d9bcf4-14cb :has_topic :republican_politics_d757f9df_1b6c .
    # :Event_01d9bcf4-14cb :has_affected_agent :sparsely_populated_state_86c1aefd_4bf3 .
    # :Event_01d9bcf4-14cb rdfs:label "political family loomed in Republican politics in sparsely populated state" .
    # :Chunk_949a2de1-4f5f a :Chunk ; :offset 2 .
    # :Chunk_949a2de1-4f5f :text "Liz Cheney ’s loss marks a remarkable fall for a political family" .
    # :Chunk_949a2de1-4f5f :sentiment 0.3182 .
    # :liz_cheney_s_loss_332e1e23_047d a :Failure .
    # :liz_cheney_s_loss_332e1e23_047d rdfs:label "Liz Cheney ’s loss" .
    # :remarkable_fall_for_political_family_e5532b36_b81c a :AlternativeCollection ;
    #     :text "remarkable fall for political family" .
    # :remarkable_fall_for_political_family_e5532b36_b81c :has_member :Autumn .
    # :remarkable_fall_for_political_family_e5532b36_b81c :has_member :Decrease .
    # :remarkable_fall_for_political_family_e5532b36_b81c rdfs:label "remarkable fall for political family" .
    # :Event_84d6734b-ce16 a :Ceremony .   TODO: marks
    # :Event_84d6734b-ce16 :has_active_agent :liz_cheney_s_loss_332e1e23_047d .    TODO: Not active agent; loss is obj
    # :Event_84d6734b-ce16 :has_topic :remarkable_fall_for_political_family_e5532b36_b81c .
    # :Event_84d6734b-ce16 rdfs:label "Liz Cheney ’s loss marks remarkable fall for political family" .
    # Second sentence
    # :PiT_Yr1978 a :PointInTime ; rdfs:label "1978" .
    # :PiT_Yr1978 :year 1978 .
    # :PiT_a_decade a :PointInTime ; rdfs:label "a decade" .
    # :Sentence_a945dd26-b8ce :mentions :Dick_Cheney .
    # :Sentence_a945dd26-b8ce :mentions :House .
    # :Dick_Cheney a :Person .
    # :Dick_Cheney rdfs:label "Richard Cheney", "Richard Bruce \'Dick\' Cheney", "Richard Bruce Cheney",
    #                         "Dick Cheney", "Dick", "Cheney" .
    # :Dick_Cheney :description "From Wikipedia (wikibase_item: Q48259): \'Richard Bruce Cheney is an
    #       American politician and businessman who served as the 46th vice president of the United States
    #       from 2001 to 2009 under President George W. Bush. He is currently the oldest living former U.S.
    #       'vice president, following the death of Walter Mondale in 2021.\'" .
    # :House a :Organization .
    # :House rdfs:label "living house", "accommodation", "house" .    TODO: Labels do not match ORG; Needs metonymy
    # :House :description "From Wikipedia (wikibase_item: Q3947): \'A house is a single-unit ..." .
    # :Chunk_3e5f988d-b910 a :Chunk ; :offset 1 .
    # :Chunk_3e5f988d-b910 :text "he served for a decade the House" .
    # :Chunk_3e5f988d-b910 :sentiment 0.0 .
    # :Event_836882af-0b3b :has_time :PiT_a_decade .
    # :Event_836882af-0b3b a :EmploymentAndRelatedEvent .   TODO: Can define a topic/affiliation related to the House?
    # :Event_836882af-0b3b :has_active_agent :Dick_Cheney .
    # :Event_836882af-0b3b rdfs:label "Dick Cheney served" .
    # :Chunk_f24fbe29-e210 a :Chunk ; :offset 2 .
    # :Chunk_f24fbe29-e210 :text "Her father is former Vice President Dick Cheney , who was elected to
    #                             the House in 1978" .
    # :Chunk_f24fbe29-e210 :sentiment -0.5106 .
    # :Event_09ec227f-31da :has_time :PiT_Yr1978 .
    # TODO: Election event


def test_paragraphs():
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(sents)
    success, graph_ttl = create_graph(sent_dicts, family_dict, '', False, False)
    assert success   # Want to make sure that there are no exceptions
    ttl_str = str(graph_ttl)
    print(ttl_str)
    # TODO: Add assertion details
    # Output:


def test_news_far_right_turtle():
    with open(f'resources/LizCheney-FarRight.txt', 'r') as narr:
        narrative = narr.read()
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(narrative)
    success, turtle = create_graph(sent_dicts, family_dict, '', True, False)
    print(turtle)
    # TODO: More detailed review/asserts
    # Output:


def test_news_right_turtle():
    with open(f'resources/LizCheney-Right.txt', 'r') as narr:
        narrative = narr.read()
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(narrative)
    success, turtle = create_graph(sent_dicts, family_dict, '', True, False)
    print(turtle)
    # TODO: More detailed review/asserts
    # Output:


def test_news_center_turtle():
    with open(f'resources/LizCheney-Center.txt', 'r') as narr:
        narrative = narr.read()
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(narrative)
    success, turtle = create_graph(sent_dicts, family_dict, '', True, False)
    print(turtle)
    # TODO: More detailed review/asserts
    # Output:


def test_news_left_turtle():
    with open(f'resources/LizCheney-Left.txt', 'r') as narr:
        narrative = narr.read()
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(narrative)
    success, turtle = create_graph(sent_dicts, family_dict, '', True, False)
    print(turtle)
    # TODO: More detailed review/asserts
    # Output:


def test_narrative_turtle():
    with open(f'resources/ErikaEckstut.txt', 'r') as narr:
        narrative = narr.read()
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(narrative)
    print(sent_dicts)
    success, turtle = create_graph(sent_dicts, family_dict, '', True, True)   # Ext sources + Is biography True
    print(turtle)
    # TODO: More detailed review/asserts; Esp need to test isBiography
    # Output:
