import pytest
from dna.create_narrative_turtle import create_graph
from dna.nlp import parse_narrative

sentences = \
    'U.S. Rep. Liz Cheney conceded defeat Tuesday in the Republican primary in Wyoming, ' \
    'an outcome that was a priority for former President Donald Trump. ' \
    'Harriet Hageman, a water and natural-resources attorney who was endorsed by the former president, ' \
    'won 66.3% of the vote to Ms. Cheney’s 28.9%, with 95% of all votes counted. ' \
    '“No House seat, no office in this land is more important than the principles we swore to ' \
    'protect,” Ms. Cheney said in her concession speech. She also claimed that Trump is promoting ' \
    'an insidious lie about the recent FBI raid of his Mar-a-Lago residence.'


def test_sentences1():
    sent_dicts, quotations, quotations_dict = parse_narrative(sentences)
    success, index, graph_ttl = create_graph(quotations_dict, sent_dicts)
    ttl_str = str(graph_ttl)
    assert index == 3
    assert 'a :WinAndLoss ; :text "conceded defeat' in ttl_str
    assert 'a :WinAndLoss ; :text "won' in ttl_str
    assert ':has_active_entity :Harriet_Hageman' in ttl_str and ':has_active_entity :Liz_Cheney' in ttl_str
    assert ':has_active_entity :Donald_Trump' in ttl_str
    assert 'a :Measurement ; :text "votes counted' in ttl_str
    assert 'a :DeceptionAndDishonesty ; :text "insidious lie' in ttl_str
    assert 'a :Affiliation ; :text "endorsed' in ttl_str
    assert ':has_active_entity [ :text "former president' in ttl_str or \
           ':has_active_entity [ :text "the former president' in ttl_str
    assert ':affiliated_with :Harriet_Hageman' in ttl_str
    assert 'a :ArrestAndImprisonment ; :text "FBI raid' in ttl_str
    assert ':has_active_entity :FBI' in ttl_str and ':has_location :Mar_a_Lago' in ttl_str
    # Output:
    # :Sentence_ec25ae8c-c2e5 a :Sentence ; :offset 1 .                ** Sentence 1
    # :Sentence_ec25ae8c-c2e5 :text "U.S. Rep. Liz Cheney conceded defeat Tuesday in the Republican primary in
    #    Wyoming, an outcome that was a priority for former President Donald Trump." .
    # :Liz_Cheney a :Person .
    # :Liz_Cheney rdfs:label "Elizabeth Lynne Cheney", "Elizabeth Lynne Cheney Perry", "Elizabeth Lynne Perry", ...
    # :Cheneys a :Person, :Collection ; rdfs:label "Cheneys" ; :role "family" .
    # :PiT_DayTuesday a :PointInTime ; rdfs:label "Tuesday" .
    # :Republican a :Person ; rdfs:label "Republican" .
    # :Republican rdfs:comment "Needs disambiguation; See the web site, https://en.wikipedia.org/wiki/Republican" .
    # :Wyoming a :PopulatedPlace, :AdministrativeDivision .
    # :Wyoming rdfs:label "WY", "Wyoming" .
    # :Wyoming rdfs:comment "From Wikipedia (wikibase_item: Q1214): \'Wyoming is a state in the Mountain West ...
    # :Wyoming :admin_level 1 .
    # :Wyoming :country_name "United States" .
    # geo:6252001 :has_component :Wyoming .
    # :Donald_Trump a :Person .
    # :Donald_Trump rdfs:label "Donald Trump", "@realDonaldTrump", "David Dennison", "DJT", "Donald J Trump", ...
    # :Trumps a :Person, :Collection ; rdfs:label "Trumps" ; :role "family" .
    # :Sentence_ec25ae8c-c2e5 :mentions geo:6252001 .
    # :Sentence_ec25ae8c-c2e5 :mentions :Liz_Cheney .
    # :Sentence_ec25ae8c-c2e5 :mentions :Tuesday .
    # :Sentence_ec25ae8c-c2e5 :mentions :Republican .
    # :Sentence_ec25ae8c-c2e5 :mentions :Wyoming .
    # :Sentence_ec25ae8c-c2e5 :mentions :Donald_Trump .
    # :Sentence_ec25ae8c-c2e5 :sentence_person 3 ; :sentiment "negative".
    # :Sentence_ec25ae8c-c2e5 :tense "past" ; :summary "Cheney loses Wyoming GOP primary." .
    # :Sentence_ec25ae8c-c2e5 :grade_level 8 .
    # :Sentence_ec25ae8c-c2e5 :rhetorical_device {:evidence "Reference to authority figures, such as \'U.S.
    #     Rep. Liz Cheney\' and \'former President Donald Trump\', is used to lend credibility to the statement."}
    #     "ethos" .
    # :Sentence_ec25ae8c-c2e5 :rhetorical_device {:evidence "The mention of \'Tuesday\' and \'the Republican primary
    #     in Wyoming\' invokes the specific time and event of the political defeat."}  "kairos" .
    # :Sentence_ec25ae8c-c2e5 :rhetorical_device {:evidence "The phrase \'conceded defeat\' may evoke feelings
    #     of empathy or disappointment among supporters or followers."}  "pathos" .
    # :Sentence_ec25ae8c-c2e5 :has_semantic  :Event_0e884cfe-2ed3 .
    # :Event_0e884cfe-2ed3 a :WinAndLoss ; :text "conceded defeat" .
    # :Event_0e884cfe-2ed3 :has_active_entity :Liz_Cheney .
    # :Sentence_ec25ae8c-c2e5 :has_semantic  :Event_a85a8833-fb7c .
    # :Event_a85a8833-fb7c a :PoliticalEvent ; :text "Republican primary" .
    # :Event_a85a8833-fb7c :has_topic :Republican .
    # :Sentence_ec25ae8c-c2e5 :has_semantic  :Event_2a9f7177-5728 .
    # :Event_2a9f7177-5728 a :Process ; :text "priority for former President Donald Trump" .
    # :Event_2a9f7177-5728 :has_affected_entity :Donald_Trump .      # Also see active_entity
    # :Sentence_c8032cc8-1ad5 a :Sentence ; :offset 2 .                ** Sentence 2
    # :Sentence_c8032cc8-1ad5 :text "Harriet Hageman, a water and natural-resources attorney who was endorsed by
    #    the former president, won 66.3% of the vote to Ms. Cheney’s 28.9%, with 95% of all votes counted." .
    # :Harriet_Hageman a :Person .
    # :Harriet_Hageman rdfs:label "Harriet M. Hageman", "Harriet Hageman", "Harriet", "Hageman" ...
    # :Hagemans a :Person, :Collection ; rdfs:label "Hagemans" ; :role "family" .
    # :Sentence_c8032cc8-1ad5 :mentions :Harriet_Hageman .
    # :Sentence_c8032cc8-1ad5 :mentions :Liz_Cheney .
    # :Sentence_c8032cc8-1ad5 :sentence_person 3 ; :sentiment "positive".
    # :Sentence_c8032cc8-1ad5 :tense "past" ; :summary "Hageman wins, Cheney loses in vote." .
    # :Sentence_c8032cc8-1ad5 :grade_level 8 .
    # :Sentence_c8032cc8-1ad5 :rhetorical_device {:evidence "won 66.3% of the vote to Ms. Cheney’s 28.9%,
    #    with 95% of all votes counted"}  "logos" .
    # :Sentence_c8032cc8-1ad5 :has_semantic  :Event_c449ac20-0231 .
    # :Event_c449ac20-0231 a :WinAndLoss ; :text "won" .
    # :Event_c449ac20-0231 :has_active_entity :Harriet_Hageman .
    # :Event_c449ac20-0231 :has_reported_value [ :text "66.3% of the vote" ; a :Measurement ] .
    # :Sentence_c8032cc8-1ad5 :has_semantic  :Event_92e92dc3-650d .
    # :Event_92e92dc3-650d a :Affiliation ; :text "endorsed" .
    # :Event_92e92dc3-650d :has_active_entity [ :text "former president" ; a :Person ] .
    # :Event_92e92dc3-650d :affiliated_with :Harriet_Hageman .
    # :Sentence_c8032cc8-1ad5 :has_semantic  :Event_25f7bfbc-9b47 .
    # :Event_25f7bfbc-9b47 a :Measurement ; :text "votes counted" .
    # :Event_25f7bfbc-9b47 :has_reported_value [ :text "95% of all votes" ; a :Measurement ] .
    # :Sentence_da74bced-0673 a :Sentence ; :offset 3 .                ** Sentence 3
    # :Sentence_da74bced-0673 :text "[Quotation0] Ms. Cheney said in her concession speech." .
    # :Sentence_da74bced-0673 :mentions :Liz_Cheney .
    # :Sentence_da74bced-0673 :has_component :Quotation0 .
    # :Quotation0 a :Quote ; :text "No House seat, no office in this land is more important than the
    #    principles we swore to protect," .
    # :House a :Organization .
    # :House rdfs:label "House" .
    # :Quotation0 :mentions :House .
    # :Quotation0 :attributed_to :Liz_Cheney .
    # :Quotation0 :sentiment "positive" ; :summary "Principles over positions" .
    # :Quotation0 :grade_level 8 .
    # :Quotation0 :rhetorical_device {:evidence "The quotation expresses a moral principle about the importance
    #    of principles over positions of power."}  "aphorism" .
    # :Quotation0 :rhetorical_device {:evidence "The statement uses logical reasoning to prioritize principles
    #    over any office or House seat."}  "logos" .
    # :Quotation0 :rhetorical_device {:evidence "The statement appeals to the emotion of duty and integrity,
    #    suggesting an emotional response to the idea of upholding principles."}  "pathos" .
    # :Quotation0 :has_semantic  :Event_0eacac07-be20 .
    # :Event_0eacac07-be20 a :Agreement ; :text "principles we swore to protect" .
    # :Quotation0 :has_semantic  :Event_175e1ca8-664e .
    # :Event_175e1ca8-664e a :EnvironmentAndCondition ; :text "No House seat, no office in this land is
    #    more important" .
    # :Quotation0 :has_semantic  :Event_10fa43e9-1cdb .
    # :Event_10fa43e9-1cdb a :Affiliation ; :text "No House seat, no office in this land" .
    # :Sentence_8dc79531-8fc1 a :Sentence ; :offset 4 .                ** Sentence 4
    # :Sentence_8dc79531-8fc1 :text "She also claimed that Trump is promoting an insidious lie about the recent
    #    FBI raid of his Mar-a-Lago residence." .
    # :FBI a :Organization .
    # :FBI rdfs:label "FBI", "F.B.I.", "Federal Bureau of Investigation" .
    # :FBI rdfs:comment "From Wikipedia (wikibase_item: Q8333): \'The Federal Bureau of Investigation (FBI) ...
    # :Mar_a_Lago a :PhysicalLocation .
    # :Mar_a_Lago rdfs:label "Mar-a-Lago", "Mar-A-Lago Building" .
    # :Mar_a_Lago rdfs:comment "From Wikipedia (wikibase_item: Q1262898): \'Mar-a-Lago is a resort and National ...
    # :Mar_a_Lago :country_name "United States" .
    # geo:6252001 :has_component :Mar_a_Lago .
    # :Sentence_8dc79531-8fc1 :mentions :Donald_Trump .
    # :Sentence_8dc79531-8fc1 :mentions :FBI .
    # :Sentence_8dc79531-8fc1 :mentions :Mar_a_Lago .
    # :Sentence_8dc79531-8fc1 :sentence_person 3 ; :sentiment "negative".
    # :Sentence_8dc79531-8fc1 :tense "present" ; :summary "Trump accused of spreading FBI raid lie." .
    # :Sentence_8dc79531-8fc1 :grade_level 8 .
    # :Sentence_8dc79531-8fc1 :rhetorical_device {:evidence "The word \'insidious\' suggests an exaggerated
    #    sense of malice or deceit."}  "hyperbole" .
    # :Sentence_8dc79531-8fc1 :rhetorical_device {:evidence "The phrase \'insidious lie\' is designed to evoke
    #    an emotional response, suggesting manipulation or harm."}  "pathos" .
    # :Sentence_8dc79531-8fc1 :rhetorical_device {:evidence "The term \'insidious\' is loaded language,
    #    carrying strong negative connotations."}  "loaded language" .
    # :Sentence_8dc79531-8fc1 :has_semantic  :Event_e656dc27-db67 .
    # :Event_e656dc27-db67 a :CommunicationAndSpeechAct ; :text "claimed" .
    # :Event_e656dc27-db67 :has_active_entity :Liz_Cheney .
    # :Sentence_8dc79531-8fc1 :has_semantic  :Event_85453299-dbbe .
    # :Event_85453299-dbbe a :CommunicationAndSpeechAct ; :text "promoting" .
    # :Event_85453299-dbbe :has_active_entity :Donald_Trump .
    # :Sentence_8dc79531-8fc1 :has_semantic  :Event_d4e94fb4-7293 .
    # :Event_d4e94fb4-7293 a :DeceptionAndDishonesty ; :text "insidious lie" .
    # :Event_d4e94fb4-7293 :has_topic [ :text "insidious lie" ; a :DeceptionAndDishonesty ] .
    # :Sentence_8dc79531-8fc1 :has_semantic  :Event_2b9e96b2-5bfb .
    # :Event_2b9e96b2-5bfb a :ArrestAndImprisonment ; :text "FBI raid" .
    # :Event_2b9e96b2-5bfb :has_active_entity :FBI .
    # :Event_2b9e96b2-5bfb :has_location :Mar_a_Lago .


def test_sentences2():
    sent_dicts, quotations, quotations_dict = parse_narrative(sentences)
    success, index, graph_ttl = create_graph(quotations_dict, sent_dicts, 2)
    ttl_str = str(graph_ttl)
    assert index == 2
