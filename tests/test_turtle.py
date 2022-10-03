from dna.create_narrative_turtle import create_graph
from dna.nlp import parse_narrative

sent_simple = 'U.S. Rep. Liz Cheney conceded defeat Tuesday in the Republican primary in Wyoming'
sent_xcomp1 = 'Harry tried to give up the prize.'
sent_xcomp2 = "Trump urged GOP voters to reject one of his most prominent critics."
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


def test_sent_simple():
    sent_dicts, quotations, quotations_dict = parse_narrative(sent_simple)
    success, graph_ttl = create_graph(sent_dicts, '', True, False)
    assert success
    print(graph_ttl)
    ttl_str = str(graph_ttl)
    assert '"Elizabeth Lynne Cheney"' in ttl_str        # Person alt name
    assert ':Liz_Cheney :gender "Female"' in ttl_str    # Gender capture
    assert '"Equality State"' in ttl_str                # WY alt name
    assert 'geo:6252001 :has_component :Wyoming' in ttl_str    # WY located in US
    assert ':PiT_DayTuesday a :PointInTime ; rdfs:label "Tuesday"' in ttl_str    # Time capture
    # Following are shown in the output pasted below
    assert ':has_topic :the_Republican_primary_' in ttl_str
    assert ':has_topic :defeat_' in ttl_str
    assert ':has_active_agent :Liz_Cheney' in ttl_str
    assert 'a :SurrenderAndYielding' in ttl_str         # Mapping for conceded
    assert 'a :Failure' in ttl_str                      # Mapping for defeat
    assert 'a :Election' in ttl_str                     # Mapping for primary
    assert ':has_time' in ttl_str
    assert ':has_location' not in ttl_str               # Wyoming is related to the primary, not Cheney
    # Output:
    # :Chunk_d632b84f-d377 a :Chunk ; :offset 1 .
    # :Chunk_d632b84f-d377 :text "U.S. Rep. Liz Cheney conceded defeat Tuesday in the Republican primary in Wyoming" .
    # :Event_c3a3b76b-a335 :has_time :PiT_DayTuesday .
    # :defeat_9c84560d-2d50 a :Failure . :defeat_9c84560d-2d50 rdfs:label "defeat" .
    # :the_Republican_primary_3103cf50-6289 a :Election .
    # :the_Republican_primary_3103cf50-6289 rdfs:label "the Republican primary" .
    # :Event_c3a3b76b-a335 :has_topic :the_Republican_primary_3103cf50-6289 .
    # :Event_c3a3b76b-a335 a :SurrenderAndYielding . :Event_c3a3b76b-a335 :has_active_agent :Liz_Cheney .
    # :Event_c3a3b76b-a335 :has_topic :defeat_9c84560d-2d50 .
    # :Event_c3a3b76b-a335 rdfs:label "Cheney conceded defeat in the Republican primary" .
    # :Event_c3a3b76b-a335 :has_time :PiT_DayTuesday .


def test_sent_xcomp1():
    sent_dicts, quotations, quotations_dict = parse_narrative(sent_xcomp1)
    success, graph_ttl = create_graph(sent_dicts, '', True, False)
    assert success
    print(graph_ttl)
    ttl_str = str(graph_ttl)
    assert '"Harry"' in ttl_str                  # Person alt name
    assert ':Harry :gender "Male"' in ttl_str    # Gender capture
    # Following are shown in the output pasted below
    assert ':has_topic :the_prize_' in ttl_str
    assert ':has_active_agent :Harry' in ttl_str
    assert 'a :Attempt' in ttl_str                      # Mapping for tried
    assert 'a :SurrenderAndYielding' in ttl_str         # Mapping for give up
    assert ':has_time' not in ttl_str
    assert ':has_location' not in ttl_str
    # Output:
    # :Chunk_6eeea672-9d51 a :Chunk ; :offset 1 .
    # :Chunk_6eeea672-9d51 :text "Harry tried to give up the prize" .
    # :the_prize_a8ace05f-2908 a :RewardAndCompensation .
    # :the_prize_a8ace05f-2908 rdfs:label "the prize" .
    # :Event_656905bc-0770 a :Attempt .
    # :Event_656905bc-0770 a :SurrenderAndYielding .
    # :Event_656905bc-0770 :has_active_agent :Harry .
    # :Event_656905bc-0770 :has_topic :the_prize_a8ace05f-2908 .
    # :Event_656905bc-0770 rdfs:label "Harry try to give up the prize" .


def test_sent_xcomp2():
    sent_dicts, quotations, quotations_dict = parse_narrative(sent_xcomp2)
    print(sent_dicts)
    success, graph_ttl = create_graph(sent_dicts, '', True, False)
    assert success
    print(graph_ttl)
    ttl_str = str(graph_ttl)
    assert '"Trump"' in ttl_str
    # Following are shown in the output pasted below
    assert '"GOP voters"' in ttl_str
    assert ':RequestAndAppeal' in ttl_str                # Mapping for urging
    assert ':RefusalAndRejection' in ttl_str             # Mapping for reject
    assert ':has_active_agent :GOP_voters_' in ttl_str   # voters reject
    assert ':has_active_agent :Trump' in ttl_str            # Trump urged
    assert ':has_affected_agent :GOP_voters_' in ttl_str     # voters were urged
    assert ':has_topic :one_of_prominent_critics_' in ttl_str    # topic of urging
    assert 'a :OpportunityAndPossibility' in ttl_str             # urging does not mean that the xcomp event happens
    # Output:
    # :Chunk_d681083f-0a64 a :Chunk ; :offset 1 .
    # :Chunk_d681083f-0a64 :text "Trump urged GOP voters to reject one of his most prominent critics" .
    # :Event_6e2faeac-d027 a :RequestAndAppeal .     # Trump urging
    # :Event_6e2faeac-d027 :has_topic :Event_776f909c-078c .   # Topic of urging
    # TODO: label should include obj
    # :Event_6e2faeac-d027 rdfs:label "Trump urge to reject one of prominent critics" .
    # :GOP_voters_2035c60d-f214 :has_context :Election .
    # :GOP_voters_2035c60d-f214 a :Person, :Collection .
    # :GOP_voters_2035c60d-f214 rdfs:label "GOP voters" .
    # :Event_6e2faeac-d027 :has_active_agent :Trump .
    # :Event_6e2faeac-d027 :has_affected_agent :GOP_voters_2035c60d-f214 .
    # TODO: resolve mapping via 'critic' vs the cardinal number, one
    # :one_of_prominent_critics_58623e7d-2721 a owl:Thing .
    # :one_of_prominent_critics_58623e7d-2721 rdfs:label "one of prominent critics" .
    # :Event_6e2faeac-d027 rdfs:label "one of prominent critics" .
    # :Event_776f909c-078c a :RefusalAndRejection .    # voter to reject
    # :Event_776f909c-078c :has_active_agent :GOP_voters_2035c60d-f214 .
    # :Event_776f909c-078c :has_topic :one_of_prominent_critics_58623e7d-2721 .
    # :Event_776f909c-078c rdfs:label "Trump urge to reject one of prominent critics" .
    # :Event_776f909c-078c a: OpportunityAndPossibility .


def test_sent_xcomp3():
    sent_dicts, quotations, quotations_dict = parse_narrative(sent_xcomp3)
    success, graph_ttl = create_graph(sent_dicts, '', True, False)
    assert success
    print(graph_ttl)
    ttl_str = str(graph_ttl)
    assert '"Trump"' in ttl_str
    # Following are shown in the output pasted below
    assert ':has_time :PiT_DayTuesday' in ttl_str
    # Wyoming is the location of the primary, not necessarily where Cheney delivered her speech
    assert ':has_location' not in ttl_str
    assert '"GOP voters"' in ttl_str
    assert ':RequestAndAppeal' in ttl_str                # Mapping for urging
    assert ':RefusalAndRejection' in ttl_str             # Mapping for reject
    assert ':has_active_agent :GOP_voters_' in ttl_str   # voters reject
    assert ':has_active_agent :Donald_Trump' in ttl_str            # Trump urged
    assert ':has_affected_agent :GOP_voters_' in ttl_str     # voters were urged
    assert ':has_topic :one_of_prominent_critics_' in ttl_str    # topic of urging
    assert 'a :OpportunityAndPossibility' in ttl_str             # urging does not mean that the xcomp event happens
    assert ':the_Republican_primary_' in ttl_str and 'a :Election' in ttl_str
    assert 'a :SurrenderAndYielding' in ttl_str           # Cheney conceded
    assert 'a :Failure' in ttl_str                        # defeat
    assert ':has_topic :defeat_'                          # topic of concession
    assert ':has_topic :the_Republican_primary'           # topic of concession
    # Output as above plus:
    # :Chunk_6adcf1f5-5e2d a :Chunk ; :offset 2 .
    # :Chunk_6adcf1f5-5e2d :text "U.S. Rep. Liz Cheney conceded defeat Tuesday in the Republican primary in
    #                             Wyoming an outcome that was a priority for former President Donald Trump" .
    # :Event_5d321b25-a5e5 :has_time :PiT_DayTuesday .
    # :defeat_b2f3d9ff-4521 a :Failure .
    # :defeat_b2f3d9ff-4521 rdfs:label "defeat" .
    # :the_Republican_primary_00433669-f54d a :Election .
    # TODO: Capture 'in Wyoming' related to the primary
    # :the_Republican_primary_00433669-f54d rdfs:label "the Republican primary" .
    # :Event_5d321b25-a5e5 :has_topic :the_Republican_primary_00433669-f54d .
    # :Event_5d321b25-a5e5 a :SurrenderAndYielding .
    # :Event_5d321b25-a5e5 :has_active_agent :Liz_Cheney .
    # :Event_5d321b25-a5e5 :has_topic :defeat_b2f3d9ff-4521 .
    # :Event_5d321b25-a5e5 rdfs:label "Cheney conceded defeat in the Republican primary" .


def test_sent_aux_only():
    sent_dicts, quotations, quotations_dict = parse_narrative(sent_aux_only)
    success, graph_ttl = create_graph(sent_dicts, '', True, False)
    assert success
    ttl_str = str(graph_ttl)
    assert 'a :EnvironmentAndCondition ; :has_topic :PoliticalIdeology' in ttl_str
    assert ':has_holder :Liz_Cheney' in ttl_str
    assert ':Liz_Cheney :has_political_ideology ' in ttl_str
    assert ':Liz_Cheney :has_political_ideology' in ttl_str
    # Output:
    # :Chunk_4bdd239b-6437 a :Chunk ; :offset 1 .
    # :Chunk_4bdd239b-6437 :text "Liz Cheney is a neoconservative" .
    # :PoliticalIdeology_3879e65d-4b9b a :EnvironmentAndCondition ; :has_topic :PoliticalIdeology ;
    #       rdfs:label "The PoliticalIdeology of the holder - neoconservative." .
    # :PoliticalIdeology_3879e65d-4b9b :has_holder :Liz_Cheney .
    # :Liz_Cheney :has_political_ideology :Conservatism ; :Liz_Cheney :has_political_ideology .
    # TODO: Remove unused objects related to neoconservative
    # :a_neoconservative_2a84ca2d-24c3 a owl:Thing .
    # :a_neoconservative_2a84ca2d-24c3 rdfs:label "a neoconservative" .


def test_sent_aux_and_verb():
    sent_dicts, quotations, quotations_dict = parse_narrative(sent_aux_and_verb)
    success, graph_ttl = create_graph(sent_dicts, '', True, False)
    assert success
    print(graph_ttl)
    ttl_str = str(graph_ttl)
    assert ':Harriet_Hageman :gender "Female"' in ttl_str    # Gender capture
    assert ':Liz_Cheney :gender "Female"' in ttl_str    # Gender capture
    # Following are shown in the output pasted below
    assert 'a :Failure' in ttl_str                                 # Mapping for defeated
    assert ':has_active_agent :Harriet_Hageman' in ttl_str
    assert ':has_affected_agent :Liz_Cheney' in ttl_str
    assert ':has_time' in ttl_str
    assert ':has_location' not in ttl_str
    # Output:
    # :Chunk_4b33e220-9ac1 a :Chunk ; :offset 1 .
    # :Chunk_4b33e220-9ac1 :text "Liz Cheney was defeated Tuesday by Harriet Hageman" .
    # :Event_b3057af2-3500 :has_time :PiT_DayTuesday .
    # :Event_b3057af2-3500 a :Failure .
    # :Event_b3057af2-3500 :has_active_agent :Harriet_Hageman .
    # :Event_b3057af2-3500 :has_affected_agent :Liz_Cheney .
    # :Event_b3057af2-3500 rdfs:label "Hageman defeated Cheney" .


def test_sent_possessive_and_aux():
    sent_dicts, quotations, quotations_dict = parse_narrative(sent_possessive_and_aux)
    success, graph_ttl = create_graph(sent_dicts, '', True, False)
    assert success
    ttl_str = str(graph_ttl)
    # TODO: Add assertion details


def test_paragraphs():
    sent_dicts, quotations, quotations_dict = parse_narrative(sents)
    success, graph_ttl = create_graph(sent_dicts, '', False, False)
    assert success   # Want to make sure that there are no exceptions


def test_short_news_turtle():
    for title in ('LC-FarRight', 'LC-Right', 'LC-Center', 'LC-Left'):
        with open(f'resources/{title}.txt', 'r') as narr:
            narrative = narr.read()
            sent_dicts, quotations, quotations_dict = parse_narrative(narrative)
            success, turtle = create_graph(sent_dicts, '', True, False)
            print(title)
            print(turtle)
            assert success
    # TODO: More detailed review/asserts


def test_news_turtle():
    for title in ('LizCheney-FarRight', 'LizCheney-Right', 'LizCheney-Center', 'LizCheney-Left'):
        with open(f'resources/{title}.txt', 'r') as narr:
            narrative = narr.read()
            sent_dicts, quotations, quotations_dict = parse_narrative(narrative)
            success, turtle = create_graph(sent_dicts, '', False, False)
            print(title)
            print(turtle)
            assert success
    # TODO: More detailed review/asserts


def test_narrative_turtle():
    with open(f'resources/ErikaEckstut.txt', 'r') as narr:
        narrative = narr.read()
    sent_dicts, quotations, quotations_dict = parse_narrative(narrative)
    success, turtle = create_graph(sent_dicts, '', True, True)   # Timeline possible True
    print(turtle)
    assert success
    # TODO: More detailed review/asserts; Esp need to test timeline
