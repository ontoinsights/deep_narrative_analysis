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
    assert ':Liz_Cheney :has_gender :enum:Female' in ttl_str    # Gender capture
    assert '"WY"' in ttl_str                            # Abbreviation for location
    assert 'geo:6252001 :has_component :Wyoming' in ttl_str    # Wyoming located in US
    assert ':PiT_DayTuesday a :PointInTime ; rdfs:label "Tuesday"' in ttl_str    # Time capture
    # Following are shown in the output pasted below
    assert ':has_topic :republican_primary_' in ttl_str
    assert ':has_topic :defeat_' in ttl_str
    assert ':has_active_agent :Liz_Cheney' in ttl_str
    assert 'a :AlternativeCollection' in ttl_str        # Mapping for conceded
    assert ':has_member :Acknowledgment' in ttl_str     # Alternatives
    assert ':has_member :SurrenderAndYielding' in ttl_str
    assert 'a :Failure' in ttl_str                      # Mapping for defeat
    assert 'a :Election' in ttl_str                     # Mapping for primary
    assert ':has_time :PiT_DayTuesday' in ttl_str
    assert ':has_location' not in ttl_str
    assert 'Republican primary in Wyoming in Republican primary in Wyoming' not in ttl_str
    # Output:
    # :Chunk_d4915475-dec3 a :Chunk ; :offset 1 .
    # :Chunk_d4915475-dec3 :text "U.S. Rep. Liz Cheney conceded defeat Tuesday in the Republican primary in Wyoming" .
    # :Event_c769ace5-f169 :has_time :PiT_DayTuesday .
    # :defeat_8805550c_4151 a :Failure .
    # :defeat_8805550c_4151 rdfs:label "defeat" .
    # :republican_primary_in_wyoming_c5df03f5_174d a :Election .
    # :republican_primary_in_wyoming_c5df03f5_174d rdfs:label "Republican primary in Wyoming" .
    # :Event_c769ace5-f169 :has_topic :republican_primary_in_wyoming_c5df03f5_174d .
    # :Event_c769ace5-f169 a :AlternativeCollection ; :text "concede" .
    # :Event_c769ace5-f169 :has_member :Acknowledgment .
    # :Event_c769ace5-f169 :has_member :SurrenderAndYielding .
    # :Event_c769ace5-f169 :has_active_agent :Liz_Cheney .
    # :Event_c769ace5-f169 :has_topic :defeat_8805550c_4151 .
    # :Event_c769ace5-f169 rdfs:label "Liz Cheney conceded defeat, in Republican primary in Wyoming" .
    # :Chunk_d4915475-dec3 :describes :Event_c769ace5-f169 .


def test_sent_xcomp1():
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(sent_xcomp1)
    success, graph_ttl = create_graph(sent_dicts, family_dict, '', True, False)
    ttl_str = str(graph_ttl)
    assert '"Harry"' in ttl_str                  # Person alt name
    assert ':Harry :has_gender :enum:Male' in ttl_str    # Gender capture
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
    # :Chunk_4a3b3672-ee2b a :Chunk ; :offset 1 .
    # :Chunk_4a3b3672-ee2b :text "On Tuesday, in Wyoming, Trump urged GOP voters to reject one of his most
    #                             prominent critics" .
    # :Event_76108e4e-ae21 :has_topic :Event_e89813bd-d1dc .
    # :Event_76108e4e-ae21 :has_time :PiT_DayTuesday .
    # :gop_voters_f2f9424c_f9af rdfs:comment "EventAndState context, :Election" .
    # :gop_voters_f2f9424c_f9af a :Person, :Collection .
    # :gop_voters_f2f9424c_f9af_GOP_Affiliation a :Affiliation ; :affiliated_with :GOP ;
    #      :affiliated_agent :gop_voters_f2f9424c_f9af .
    # :gop_voters_f2f9424c_f9af_GOP_Affiliation rdfs:label "Relationship based on the text, \'GOP voters\'" .
    # :gop_voters_f2f9424c_f9af a :Person, :Collection .     TODO: Repeated type definition
    # :gop_voters_f2f9424c_f9af rdfs:label "GOP voters" .
    # :prominent_critics_b9273179_0395 rdfs:comment "EventAndState context, :AssertionAndDeclaration" .
    # :prominent_critics_b9273179_0395 a :Person .
    # :prominent_critics_b9273179_0395 a :Person .           TODO: Repeated type definition
    # :prominent_critics_b9273179_0395 rdfs:label "one of critics" .
    # :Event_e89813bd-d1dc a :RefusalAndRejection .
    # :Event_e89813bd-d1dc :has_active_agent :gop_voters_f2f9424c_f9af .
    # :Event_e89813bd-d1dc :has_affected_agent :prominent_critics_b9273179_0395 .
    # :Event_e89813bd-d1dc rdfs:label "GOP voters reject one of critics" .
    # :Chunk_4a3b3672-ee2b :describes :Event_e89813bd-d1dc .
    # :Event_76108e4e-ae21 :has_location :Wyoming .
    # :Event_76108e4e-ae21 a :RequestAndAppeal .
    # :Event_76108e4e-ae21 :has_active_agent :Trump .
    # :Event_76108e4e-ae21 :has_affected_agent :gop_voters_f2f9424c_f9af .
    # :Event_76108e4e-ae21 rdfs:label "Trump urged GOP voters" .
    # :Chunk_4a3b3672-ee2b :describes :Event_76108e4e-ae21 .
    # :Event_e89813bd-d1dc a :OpportunityAndPossibility .


def test_sent_xcomp2a():
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(sent_xcomp2a)
    success, graph_ttl = create_graph(sent_dicts, family_dict, '', True, False)
    assert success
    ttl_str = str(graph_ttl)
    # Following are shown in the output pasted below
    assert '"Republican voters"' in ttl_str
    assert ':RequestAndAppeal' in ttl_str                # Mapping for urging
    assert ':RefusalAndRejection' in ttl_str             # Mapping for reject
    assert ':has_topic :Event_' in ttl_str               # Topic of the urging (another event = rejection)
    assert ':has_active_agent :republican_voters_' in ttl_str       # Voters reject
    assert ':has_active_agent :Trump' in ttl_str                    # Trump urged
    assert ':has_affected_agent :republican_voters_' in ttl_str     # Voters were urged
    # TODO: Republican is captured as amod only, not a compound noun (spacy bug); Check adj modifiers for affiliation
    assert 'a :Affiliation' not in ttl_str
    # assert ':affiliated_agent :republican_voters' in ttl_str and ':affiliated_with :Republican' in ttl_str
    # Output similar to above


def test_sent_xcomp3():
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(sent_xcomp3)
    success, graph_ttl = create_graph(sent_dicts, family_dict, '', True, False)
    assert success
    ttl_str = str(graph_ttl)
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
    assert 'a :AlternativeCollection' in ttl_str                 # Mapping for conceded
    assert ':has_member :Acknowledgment' in ttl_str              # Alternatives
    assert ':has_member :SurrenderAndYielding' in ttl_str
    assert 'a :Failure' in ttl_str                        # Defeat
    assert ':has_topic :defeat_'                          # Topic of concession
    assert ':has_topic :republican_primary_'              # Topic of concession
    # Output as for xcomp1 and xcomp2 combined


def test_sent_aux_only():
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(sent_aux_only)
    success, graph_ttl = create_graph(sent_dicts, family_dict, '', True, False)
    assert success
    ttl_str = str(graph_ttl)
    assert ':Liz_Cheney :has_agent_aspect :PoliticalIdeology ; :agent_aspect "neoconservative"' in ttl_str
    assert ':neoconservative_' not in ttl_str      # Is unused since the mapping is to an agent aspect
    # Output:
    # :Chunk_e1ae1402-d86c a :Chunk ; :offset 1 .
    # :Chunk_e1ae1402-d86c :text "Liz Cheney is a neoconservative" .
    # :Liz_Cheney :has_agent_aspect :PoliticalIdeology ; :agent_aspect "neoconservative" .


def test_sent_aux_and_verb():
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(sent_aux_and_verb)
    success, graph_ttl = create_graph(sent_dicts, family_dict, '', True, False)
    assert success
    ttl_str = str(graph_ttl)
    assert ':Harriet_Hageman :has_gender :enum:Female' in ttl_str    # Gender capture
    assert ':Liz_Cheney :has_gender :enum:Female' in ttl_str         # Gender capture
    # Following are shown in the output pasted below
    assert 'a :Success' in ttl_str                           # Mapping for 'was defeated', reversing subj/obj
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
