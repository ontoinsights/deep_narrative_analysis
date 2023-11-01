import pytest
from dna.create_narrative_turtle import create_graph
from dna.nlp import parse_narrative

sents1 = \
    'Liz Cheney’s loss marks a remarkable fall for a political family that has loomed large in ' \
    'Republican politics in the sparsely populated state for more than four decades. Her father is former ' \
    'Vice President Dick Cheney, who was elected to the House in 1978, where he served for a decade.'
sents2 = \
    'Liz Cheney’s loss was expected, even by herself. In fact, she said, "I hope that I served my constituency well."'
sents3 = \
    'U.S. Rep. Liz Cheney conceded defeat Tuesday in the Republican primary in Wyoming, ' \
    'an outcome that was a priority for former President Donald Trump as he urged GOP voters ' \
    'to reject one of his most prominent critics on Capitol Hill. ' \
    'Harriet Hageman, a water and natural-resources attorney who was endorsed by the former president, ' \
    'won 66.3% of the vote to Ms. Cheney’s 28.9%, with 95% of all votes counted. ' \
    '“No House seat, no office in this land is more important than the principles we swore to ' \
    'protect,” Ms. Cheney said in her concession speech. She also claimed that Trump is promoting ' \
    'an insidious lie about the recent FBI raid of his Mar-a-Lago residence, which will provoke ' \
    'violence and threats of violence.'


def test_sents1():
    sent_dicts, quotations, quotations_dict = parse_narrative(sents1)
    success, graph_ttl = create_graph(quotations_dict, sent_dicts)
    assert success
    ttl_str = str(graph_ttl)
    assert '"Elizabeth Lynne Cheney"' in ttl_str        # Person alt name
    assert ':gender "female"' in ttl_str                # Gender capture
    # Following are shown in the output pasted below
    assert ':has_topic [ :text "Liz Cheney’s loss" ; a :WinAndLoss' in ttl_str
    assert ':has_location [ :text "the sparsely populated state"' in ttl_str
    assert ':has_active_agent :Dick_Cheney' not in ttl_str       # TODO, bug
    assert 'a :End' in ttl_str                          # Mapping for 'marks'
    assert 'a :EnvironmentAndCondition' in ttl_str      # Mapping for 'is'
    assert ':has_quantification' in ttl_str
    # Output:
    # :Sentence_ae97cf32-b3b5 a :Sentence ; :offset 1 .
    # :Sentence_ae97cf32-b3b5 :text "Liz Cheney’s loss marks a remarkable fall for a political family that has
    #       loomed large in Republican politics in the sparsely populated state for more than four decades." .
    # :Cheneys a :Person, :Collection ; rdfs:label "Cheneys" ; :role "family" .
    # :Liz_Cheney a :Person ; :gender "female" .
    # :Liz_Cheney rdfs:label "Elizabeth Lynne Cheney", "Elizabeth Lynne Cheney Perry", "Elizabeth Lynne Perry",
    #       "Liz Cheney", "Elizabeth Cheney", "Liz", "Cheney" .
    # :Liz_Cheney rdfs:comment "From Wikipedia (wikibase_item: Q5362573): \'Elizabeth Lynne Cheney is an American
    #       attorney and politician. ... As of March 2023, she is a professor of practice at the University of
    #       Virginia Center for Politics.\'" .
    # :Liz_Cheney :external_link "https://en.wikipedia.org/wiki/Liz_Cheney" .
    # :Republican a :Person ; rdfs:label "Republican" .
    # :Republican rdfs:comment "Needs disambiguation; See the web site, https://en.wikipedia.org/wiki/Republican" .
    # :Sentence_ae97cf32-b3b5 :mentions :Liz_Cheney .
    # :Sentence_ae97cf32-b3b5 :mentions :Republican .
    # :Sentence_ae97cf32-b3b5 :sentence_person 3 ; :sentiment "negative".
    # :Sentence_ae97cf32-b3b5 :voice "active" ; :tense "past" ;
    #       :summary "Cheney\'s political family\'s influence in Republican politics declines." .
    # :Sentence_ae97cf32-b3b5 :grade_level 12 .
    # :Sentence_ae97cf32-b3b5 :rhetorical_device {:evidence "Reference to authority figures, in this case, the
    #       political family of Liz Cheney, is used to justify the statement about their significant influence
    #       in Republican politics."}  "ethos" .
    # :Sentence_ae97cf32-b3b5 :rhetorical_device {:evidence "The phrase \'has loomed large in Republican politics
    #         in the sparsely populated state for more than four decades\' invokes nostalgia by referring to the
    #         long-standing influence of the Cheney family."}  "nostalgia" .
    # :Sentence_ae97cf32-b3b5 :rhetorical_device {:evidence "The phrase \'Liz Cheney’s loss marks a remarkable fall\'
    #       appeals to emotions such as empathy or sympathy for the political family."}  "pathos" .
    # :Sentence_ae97cf32-b3b5 :has_semantic :Event_c32095fd-b4bd .
    # :Event_c32095fd-b4bd :text "marks" ; a :End .
    # :Event_c32095fd-b4bd :has_topic [ :text "Liz Cheney’s loss" ; a :WinAndLoss ] .
    # :Event_c32095fd-b4bd :has_active_entity [ :text "a political family" ; a :Person, :Collection ] .
    # :Sentence_ae97cf32-b3b5 :has_semantic :Event_573957d9-23eb .
    # :Event_573957d9-23eb :text "loomed" ; a :MovementTravelAndTransportation .    ** Incorrect classification
    # :Event_573957d9-23eb :has_affected_entity [ :text "Republican politics" ; a :PoliticalGroup ] .
    # :Event_573957d9-23eb :has_location [ :text "the sparsely populated state" ; a :Location ] .
    # :Sentence_dd1d93df-e259 a :Sentence ; :offset 2 .
    # :Sentence_dd1d93df-e259 :text "Her father is former Vice President Dick Cheney, who was elected to the
    #       House in 1978, where he served for a decade." .
    # :Dick_Cheney a :Person .     ** Missing gender
    # :Dick_Cheney rdfs:label "Richard Cheney", "Richard Bruce \'Dick\' Cheney", "Richard Bruce Cheney",
    #       "Dick Cheney", "Dick", "Cheney" .
    # :Dick_Cheney rdfs:comment "From Wikipedia (wikibase_item: Q48259): \'Richard Bruce Cheney is an American
    #       politician and businessman who served as the 46th vice president of the United States ... \'" .
    # :Dick_Cheney :external_link "https://en.wikipedia.org/wiki/Dick_Cheney" .
    # :House a :Organization .
    # :House rdfs:label "House" .     # Correctly identified inconsistency with Wikipedia match of wording
    # :PiT_Yr1978 a :PointInTime ; rdfs:label "1978" .
    # :Sentence_dd1d93df-e259 :mentions :Dick_Cheney .
    # :Sentence_dd1d93df-e259 :mentions :House .
    # :Sentence_dd1d93df-e259 :mentions :1978 .
    # :Sentence_dd1d93df-e259 :sentence_person 3 ; :sentiment "neutral".
    # :Sentence_dd1d93df-e259 :voice "active" ; :tense "past" ;
    #       :summary "Dick Cheney served in the House for a decade." .
    # :Sentence_dd1d93df-e259 :grade_level 10 .
    # :Sentence_dd1d93df-e259 :rhetorical_device {:evidence "The sentence refers to Dick Cheney, a figure of
    #       authority in the political field, to justify the statement about the Cheney family\'s political
    #       influence."}  "ethos" .
    # :Sentence_dd1d93df-e259 :rhetorical_device {:evidence "The sentence refers to a specific time period
    #       (more than four decades) and specific events (Dick Cheney\'s election to the House in 1978 and his
    #       decade-long service) to engage the reader."}  "kairos" .
    # :Sentence_dd1d93df-e259 :has_semantic :Event_c3487e39-a602 .
    # :Event_c3487e39-a602 :text "is" ; a :EnvironmentAndCondition .
    # :Event_c3487e39-a602 :has_described_entity [ :text "Her father" ; a :Person ] .
    # *** Missing match to :Dick_Cheney
    # :Event_c3487e39-a602 :has_described_entity [ :text "former Vice President Dick Cheney" ; a :Person ] .
    # :Sentence_dd1d93df-e259 :has_semantic :Event_ea31a2d5-fb8d .
    # :Event_ea31a2d5-fb8d :text "was elected" ; a :PoliticalEvent .
    # :Event_ea31a2d5-fb8d :has_active_entity [ :text "former Vice President Dick Cheney" ; a :Person ] .
    # :Event_ea31a2d5-fb8d :has_affected_entity [ :text "the House" ; a :GovernmentalEntity ] .
    # :Sentence_dd1d93df-e259 :has_semantic :Event_5ef35e72-bf0e .
    # :Event_5ef35e72-bf0e :text "served" ; a :UtilizationAndConsumption .      ** Incorrect classification
    # :Event_5ef35e72-bf0e :has_active_entity [ :text "former Vice President Dick Cheney" ; a :Person ] .
    # :Event_5ef35e72-bf0e :has_quantification [ :text "a decade" ; a owl:Thing ] .


def test_sents2():
    sent_dicts, quotations, quotations_dict = parse_narrative(sents2)
    success, graph_ttl = create_graph(quotations_dict, sent_dicts)
    ttl_str = str(graph_ttl)
    assert '"Elizabeth Cheney"' in ttl_str               # Person alt name
    assert ':gender "female"' in ttl_str                 # Gender capture
    # Following are shown in the output pasted below
    assert ':has_active_entity :Liz_Cheney' in ttl_str
    assert ':has_affected_entity :Liz_Cheney' in ttl_str
    assert 'a :WinAndLoss' in ttl_str                   # loss
    assert 'a :Cognition' in ttl_str                    # expected
    assert ':has_component :Quotation0' in ttl_str
    assert ':Quotation0 a :Quote' in ttl_str
    assert ':voice "active' in ttl_str and ':voice "passive' in ttl_str
    assert ':has_time' not in ttl_str
    assert ':has_location' not in ttl_str
    # Output Turtle:
    # :Sentence_dcec0566-ac2a a :Sentence ; :offset 1 .
    # :Sentence_dcec0566-ac2a :text "Liz Cheney’s loss was expected, even by herself." .
    # :Cheneys a :Person, :Collection ; rdfs:label "Cheneys" ; :role "family" .
    # :Liz_Cheney a :Person .
    # :Liz_Cheney rdfs:label "Elizabeth Lynne Cheney", "Elizabeth Lynne Cheney Perry", "Elizabeth Lynne Perry",
    #      "Liz Cheney", "Elizabeth Cheney", "Liz", "Cheney" .
    # :Liz_Cheney rdfs:comment "From Wikipedia (wikibase_item: Q5362573): \'Elizabeth Lynne Cheney is an American
    #      attorney and politician. ... As of March 2023, she is a professor of practice at the University
    #      of Virginia Center for Politics.\'" .
    # :Liz_Cheney :external_link "https://en.wikipedia.org/wiki/Liz_Cheney" .
    # :Liz_Cheney :gender "female" .
    # :Sentence_dcec0566-ac2a :mentions :Liz_Cheney .
    # :Sentence_dcec0566-ac2a :sentence_person 3 ; :sentiment "negative".
    # :Sentence_dcec0566-ac2a :voice "passive" ; :tense "past" ; :summary "Liz Cheney expected her own loss." .
    # :Sentence_dcec0566-ac2a :grade_level 8 .
    # :Sentence_dcec0566-ac2a :has_semantic :Event_872c2177-7bae .
    # :Event_872c2177-7bae :text "Liz Cheney’s loss" ; a :WinAndLoss .
    # :Event_872c2177-7bae :has_active_entity :Liz_Cheney .
    # :Event_872c2177-7bae :has_topic [ :text "loss" ; a :WinAndLoss ] .
    # :Sentence_dcec0566-ac2a :has_semantic :Event_75bf4c31-a155 .
    # :Event_75bf4c31-a155 :text "was expected" ; a :Cognition .
    # :Event_75bf4c31-a155 :has_affected_entity :Liz_Cheney .
    # :Sentence_45c258b9-75f9 a :Sentence ; :offset 2 .
    # :Sentence_45c258b9-75f9 :text "In fact, she said,[ Quotation0]" .
    # :Sentence_45c258b9-75f9 :has_component :Quotation0 .
    # :Sentence_45c258b9-75f9 :sentence_person 3 ; :sentiment "neutral".
    # :Sentence_45c258b9-75f9 :voice "active" ; :tense "past" ; :summary "She stated a fact" .
    # :Sentence_45c258b9-75f9 :grade_level 5 .
    # :Sentence_45c258b9-75f9 :rhetorical_device {:evidence "The phrase \'In fact\' is used to emphasize
    #      the statement that follows."}  "expletive" .
    # :Sentence_45c258b9-75f9 :has_semantic :Event_aeeac23a-0a08 .
    # :Event_aeeac23a-0a08 :text "she said" ; a :CommunicationAndSpeechAct .
    # :Event_aeeac23a-0a08 :has_active_entity [ :text "she" ; a :Person ] .
    # :Quotation0 a :Quote ; :text "I expected to lose." .
    # :Quotation0 :attributed_to :Liz_Cheney .
    # :Quotation0 :sentiment "negative" ; :summary "Speaker anticipated defeat" .
    # :Quotation0 :grade_level 2 .
    # :Quotation0 :has_semantic :Event_520a39cd-dd5d .
    # :Event_520a39cd-dd5d :text "expected to lose" ; a :WinAndLoss .


def test_sents3():
    sent_dicts, quotations, quotations_dict = parse_narrative(sents3)
    success, graph_ttl = create_graph(quotations_dict, sent_dicts)
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
    # :Sentence_0139e4a2-94d0 a :Sentence ; :offset 1 .
    # :Sentence_0139e4a2-94d0 :text "U.S. Rep. Liz Cheney conceded defeat Tuesday in the Republican primary
    #      in Wyoming, an outcome that was a priority for former President Donald Trump as he urged GOP voters
    #      to reject one of his most prominent critics on Capitol Hill." .
    # :Cheneys a :Person, :Collection ; rdfs:label "Cheneys" ; :role "family" .
    # :Liz_Cheney a :Person .
    # :Liz_Cheney rdfs:label "Elizabeth Lynne Cheney", "Elizabeth Lynne Cheney Perry", ...
    # :Liz_Cheney rdfs:comment "From Wikipedia (wikibase_item: Q5362573): \'Elizabeth Lynne Cheney ...\'" .
    # :Liz_Cheney :external_link "https://en.wikipedia.org/wiki/Liz_Cheney" .
    # :Liz_Cheney :gender "female" .
    # :PiT_DayTuesday a :PointInTime ; rdfs:label "Tuesday" .
    # :Republican a :Person ; rdfs:label "Republican" .
    # :Republican rdfs:comment "Needs disambiguation; See the web site, https://en.wikipedia.org/wiki/Republican" .
    # :Wyoming a :PopulatedPlace, :AdministrativeDivision .
    # :Wyoming rdfs:label "Wyoming", "WY" .
    # :Wyoming rdfs:comment "From Wikipedia (wikibase_item: Q1214): \'Wyoming ...\'" .
    # :Wyoming :external_link "https://en.wikipedia.org/wiki/Wyoming" .
    # :Wyoming :admin_level 1 .
    # :Wyoming :country_name "United States" .
    # geo:6252001 :has_component :Wyoming .
    # :Trumps a :Person, :Collection ; rdfs:label "Trumps" ; :role "family" .
    # :Donald_Trump a :Person .
    # :Donald_Trump rdfs:label "@realDonaldTrump", "David Dennison", "DJT", "Donald J Trump", "Donald J. Trump",
    #      "Individual 1", "Mr Trump", "POTUS 45", "President Donald J Trump", "President Donald J. Trump",
    #      "President Donald John Trump", "President Donald Trump", "President Trump", "The Donald", "John Miller",
    #      "Trump", "45", "John Barron", "Donald John Trump", "Donald Trump", "Inmate No. P01135809",
    #      "Prisoner P01135809", "inmate P01135809", "Inmate P01135809", "The Former Guy", "Donald" .
    # :Donald_Trump rdfs:comment "From Wikipedia (wikibase_item: Q22686): \'Donald John Trump ... \'" .
    # :Donald_Trump :external_link "https://en.wikipedia.org/wiki/Donald_Trump" .
    # :Donald_Trump :gender "male" .
    # :GOP a :Organization .
    # :GOP rdfs:label "Republican Party", "The Republicans", "GOP", "Grand Old Party", "Republicans",
    #      "Republican Party (United States)", "United States Republican Party", "US Republican Party" .
    # :GOP rdfs:comment "From Wikipedia (wikibase_item: Q29468): \'The Republican Party, also known as the GOP, ...\'" .
    # :GOP :external_link "https://en.wikipedia.org/wiki/Republican_Party_(United_States)" .
    # :Capitol_Hill a :Organization .
    # :Capitol_Hill rdfs:label "Capitol Hill", "Capitol Hill Historic District", "Capitol Hill, DC" .
    # :Capitol_Hill rdfs:comment "From Wikipedia (wikibase_item: Q2305815): \'Capitol Hill is the largest historic
    #      residential neighborhood in Washington, D.C., stretching easterly in front of the United States Capitol
    #      along wide avenues. It is one of the oldest residential neighborhoods in Washington, D.C., ...
    #      The name is also frequently used as a metonym for the United States Congress.\'" .
    # :Capitol_Hill :external_link "https://en.wikipedia.org/wiki/Capitol_Hill" .
    # :Sentence_0139e4a2-94d0 :mentions geo:6252001 .
    # :Sentence_0139e4a2-94d0 :mentions :Liz_Cheney .
    # :Sentence_0139e4a2-94d0 :mentions :Tuesday .
    # :Sentence_0139e4a2-94d0 :mentions :Republican .
    # :Sentence_0139e4a2-94d0 :mentions :Wyoming .
    # :Sentence_0139e4a2-94d0 :mentions :Donald_Trump .
    # :Sentence_0139e4a2-94d0 :mentions :GOP .
    # :Sentence_0139e4a2-94d0 :mentions :Capitol_Hill .
    # :Sentence_0139e4a2-94d0 :sentence_person 3 ; :sentiment "negative".
    # :Sentence_0139e4a2-94d0 :voice "active" ; :tense "past" ; :summary "Cheney loses Wyoming primary, Trump\'s
    #      priority achieved." .
    # :Sentence_0139e4a2-94d0 :grade_level 12 .
    # :Sentence_0139e4a2-94d0 :rhetorical_device {:evidence "The text refers to authority figures such as U.S. Rep.
    #      Liz Cheney and former President Donald Trump."}  "ethos" .
    # :Sentence_0139e4a2-94d0 :rhetorical_device {:evidence "The text refers to a specific event, the Republican
    #      primary in Wyoming, to engage the reader."}  "kairos" .
    # :Sentence_0139e4a2-94d0 :rhetorical_device {:evidence "The text uses wording that appeals to emotions
    #      such as the defeat of Liz Cheney and the victory being a priority for Donald Trump."}  "pathos" .
    # :Sentence_0139e4a2-94d0 :has_semantic :Event_099aad21-e7f0 .
    # :Event_099aad21-e7f0 :text "conceded defeat" ; a :End .
    # :Event_099aad21-e7f0 :has_active_entity :Liz_Cheney .
    # :Event_099aad21-e7f0 :has_location :Republican .      *** Incorrect location
    # :Sentence_0139e4a2-94d0 :has_semantic :Event_5aefa0a0-e5fa .
    # :Event_5aefa0a0-e5fa :text "was a priority for former President Donald Trump" ; a :Cognition .
    # :Event_5aefa0a0-e5fa :has_active_entity :Donald_Trump .
    # :Sentence_0139e4a2-94d0 :has_semantic :Event_65ff7dfa-3b47 .
    # :Event_65ff7dfa-3b47 :text "urged GOP voters to reject" ; a :CommunicationAndSpeechAct .
    # :Event_65ff7dfa-3b47 :has_affected_entity :GOP .     ** Missing Trump as active entity
    # :Event_65ff7dfa-3b47 :has_affected_entity :Capitol_Hill .
    # :Sentence_e2370b23-e1ac a :Sentence ; :offset 2 .
    # :Sentence_e2370b23-e1ac :text "Harriet Hageman, a water and natural-resources attorney ...\'" .
    # :Hagemans a :Person, :Collection ; rdfs:label "Hagemans" ; :role "family" .
    # :Harriet_Hageman a :Person .
    # :Harriet_Hageman rdfs:label "Harriet M. Hageman", "Harriet Hageman", "Harriet", "Hageman" .
    # :Harriet_Hageman rdfs:comment "From Wikipedia (wikibase_item: Q110815967): \'Harriet Maxine Hageman ...
    #      She is a member of the Republican Party.\'" .
    # :Harriet_Hageman :external_link "https://en.wikipedia.org/wiki/Harriet_Hageman" .
    # :Harriet_Hageman :gender "female" .
    # :Sentence_e2370b23-e1ac :mentions :Harriet_Hageman .
    # :Sentence_e2370b23-e1ac :mentions :Cheneys .
    # :Sentence_e2370b23-e1ac :sentence_person 3 ; :sentiment "positive".
    # :Sentence_e2370b23-e1ac :voice "active" ; :tense "past" ;
    #      :summary "Hageman, endorsed by ex-president, won 66.3% of vote." .
    # :Sentence_e2370b23-e1ac :grade_level 12 .
    # :Sentence_e2370b23-e1ac :rhetorical_device {:evidence "The sentence refers to the endorsement of Harriet
    #      Hageman by the former president, which is an appeal to authority."}  "ethos" .
    # :Sentence_e2370b23-e1ac :rhetorical_device {:evidence "The sentence uses specific percentages and
    #      numbers to provide a logical and factual basis for the claim that Harriet Hageman won the vote."}  "logos" .
    # :Sentence_e2370b23-e1ac :has_semantic :Event_82b423ca-0522 .
    # :Event_82b423ca-0522 :text "won 66.3% of the vote" ; a :WinAndLoss .
    # :Event_82b423ca-0522 :has_active_entity :Harriet_Hageman .
    # :Event_82b423ca-0522 :has_topic [ :text "vote" ; a :PoliticalEvent ] .
    # :Sentence_e2370b23-e1ac :has_semantic :Event_93a03566-3dbf .
    # :Event_93a03566-3dbf :text "endorsed by the former president" ; a :CommunicationAndSpeechAct .
    # :Event_93a03566-3dbf :has_active_entity [ :text "former president" ; a :Person ] .    ** Sophisticated co-ref
    # :Sentence_e2370b23-e1ac :has_semantic :Event_61104e66-613b .
    # :Event_61104e66-613b :text "a water and natural-resources attorney" ; a :EnvironmentAndCondition .
    # :Event_61104e66-613b :has_aspect [ :text "water and natural-resources attorney" ; a :LineOfBusiness ] .
    #       ** Should reference :Harriet_Hageman, sophisticated co-ref
    # :Sentence_18a7470f-76e8 a :Sentence ; :offset 3 .
    # :Sentence_18a7470f-76e8 :text "[ Quotation0] Ms. Cheney said in her concession speech." .
    # :Sentence_18a7470f-76e8 :mentions :Liz_Cheney .
    # :Sentence_18a7470f-76e8 :has_component :Quotation0 .
    # :Sentence_18a7470f-76e8 :sentence_person 3 ; :sentiment "neutral".
    # :Sentence_18a7470f-76e8 :voice "active" ; :tense "past" ; :summary "Ms. Cheney spoke in her concession speech." .
    # :Sentence_18a7470f-76e8 :grade_level 8 .
    # :Sentence_18a7470f-76e8 :has_semantic :Event_156f725b-552f .
    # :Event_156f725b-552f :text "said" ; a :CommunicationAndSpeechAct .
    # :Event_156f725b-552f :has_active_entity :Liz_Cheney .
    # :Event_156f725b-552f :has_topic [ :text "her concession speech" ; a :End ] .
    # :Sentence_76ad1ccd-7c9f a :Sentence ; :offset 4 .
    # :Sentence_76ad1ccd-7c9f :text "She also claimed that Trump is promoting an insidious lie about the recent FBI
    #      raid of his Mar-a-Lago residence, which will provoke violence and threats of violence." .
    # :FBI a :Organization .
    # :FBI rdfs:label "FBI", "F.B.I.", "Federal Bureau of Investigation" .
    # :FBI rdfs:comment "From Wikipedia (wikibase_item: Q8333): \'The Federal Bureau of Investigation (FBI) ...'\" .
    # :FBI :external_link "https://en.wikipedia.org/wiki/Federal_Bureau_of_Investigation" .
    # :Mar_a_Lago a :PhysicalLocation .
    # :Mar_a_Lago rdfs:label "Mar-a-Lago", "Mar-A-Lago Building" .
    # :Mar_a_Lago rdfs:comment "From Wikipedia (wikibase_item: Q1262898): \'Mar-a-Lago is a resort and National
    #      Historic Landmark in Palm Beach, Florida, owned since 1985 by Donald Trump.\'" .
    # :Mar_a_Lago :external_link "https://en.wikipedia.org/wiki/Mar-a-Lago" .
    # :Mar_a_Lago :country_name "United States" .
    # geo:6252001 :has_component :Mar_a_Lago .
    # :Sentence_76ad1ccd-7c9f :mentions :Donald_Trump .
    # :Sentence_76ad1ccd-7c9f :mentions :FBI .
    # :Sentence_76ad1ccd-7c9f :mentions :Mar_a_Lago .
    # :Sentence_76ad1ccd-7c9f :sentence_person 3 ; :sentiment "negative".
    # :Sentence_76ad1ccd-7c9f :voice "active" ; :tense "present" ;
    #      :summary "Cheney claims Trump\'s lie will provoke violence." .
    # :Sentence_76ad1ccd-7c9f :grade_level 12 .
    # :Sentence_76ad1ccd-7c9f :has_semantic :OpportunityAndPossibility .
    # :Sentence_76ad1ccd-7c9f :rhetorical_device {:evidence "The sentence refers to Trump, a figure of authority,
    #      to justify the statement."}  "ethos" .
    # :Sentence_76ad1ccd-7c9f :rhetorical_device {:evidence "The phrase \'insidious lie\' is an exaggeration,
    #      implying that the lie is not just a lie, but one with harmful effects."}  "hyperbole" .
    # :Sentence_76ad1ccd-7c9f :rhetorical_device {:evidence "The sentence appeals to fear by suggesting
    #      that the lie will provoke violence and threats of violence."}  "pathos" .
    # :Sentence_76ad1ccd-7c9f :rhetorical_device {:evidence "The term \'insidious lie\' is a loaded language,
    #      invoking strong negative emotions and judgments about Trump\'s actions."}  "loaded language" .
    # :Sentence_76ad1ccd-7c9f :has_semantic :Event_f2671ba5-f119 .
    # :Event_f2671ba5-f119 :text "claimed" ; a :CommunicationAndSpeechAct .
    # :Event_f2671ba5-f119 :has_active_entity [ :text "She" ; a :Person ] .    ** Needs co-ref resolved
    # :Event_f2671ba5-f119 :has_affected_entity :Donald_Trump .
    # :Sentence_76ad1ccd-7c9f :has_semantic :Event_17973818-81b2 .
    # :Event_17973818-81b2 :text "promoting an insidious lie" ; a :AggressiveCriminalOrHostileAct .
    # :Event_17973818-81b2 :has_active_entity :Donald_Trump .
    # :Event_17973818-81b2 :has_topic [ :text "insidious lie" ; a :CommunicationAndSpeechAct ] .
    # :Sentence_76ad1ccd-7c9f :has_semantic :Event_314c2e8e-32c5 .
    # :Event_314c2e8e-32c5 :text "provoke violence and threats of violence" ; a :AggressiveCriminalOrHostileAct .
    # :Event_314c2e8e-32c5 :has_topic [ :text "violence and threats of violence" ; a :AggressiveCriminalOrHostileAct ] .
    # :Quotation0 a :Quote ; :text "No House seat, no office in this land is more important than the
    #      principles we swore to protect," .
    # :House a :Organization .
    # :House rdfs:label "house", "accommodation", "living house", "House" .     ** Consistency check failed
    # :House rdfs:comment "From Wikipedia (wikibase_item: Q3947): \'A house is a single-unit residential ...\'" .
    # :Quotation0 :mentions :House .
    # :Quotation0 :attributed_to :Liz_Cheney .
    # :Quotation0 :sentiment "positive" ; :summary "Principles more important than any office" .
    # :Quotation0 :grade_level 8 .
    # :Quotation0 :rhetorical_device {:evidence "The speaker refers to the authority of the principles that they
    #      swore to protect, which is an appeal to ethos."}  "ethos" .
    # :Quotation0 :rhetorical_device {:evidence "The speaker uses wording that appeals to the emotion of the reader,
    #      emphasizing the importance of principles over any office or House seat, which is an appeal to pathos."}
    #      "pathos" .
    # :Quotation0 :rhetorical_device {:evidence "The speaker repeats the word \'no\' for emphasis."}  "repetition" .
    # :Quotation0 :has_semantic :Event_b7169256-b3b6 .
    # :Event_b7169256-b3b6 :text "No House seat, no office in this land is more important than the principles we
    #      swore to protect" ; a :CommunicationAndSpeechAct .
    # :Event_b7169256-b3b6 :has_affected_entity [ :text "House seat" ; a :GovernmentalEntity ] .
    # :Event_b7169256-b3b6 :has_affected_entity [ :text "office" ; a :Location ] .    ** Incorrect classification
    # :Event_b7169256-b3b6 :has_topic [ :text "principles" ; a :EventAndState ] .
    # :Quotation0 :has_semantic :Event_022f150f-d18c .
    # :Event_022f150f-d18c :text "we swore to protect" ; a :CaptureAndSeizure .      ** Incorrect classification
    # :Event_022f150f-d18c :has_active_entity [ :text "we" ; a :Person, :Collection ] .
