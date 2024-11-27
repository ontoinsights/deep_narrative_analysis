import pytest
from dna.create_narrative_turtle import create_graph
from dna.nlp import parse_narrative

sentences1 = \
    'U.S. Rep. Liz Cheney conceded defeat Tuesday in the Republican primary in Wyoming, ' \
    'an outcome that was a priority for former President Donald Trump. ' \
    'Harriet Hageman, a water and natural-resources attorney who was endorsed by the former president, ' \
    'won 66.3% of the vote to Ms. Cheney’s 28.9%, with 95% of all votes counted. ' \
    '“No House seat, no office in this land is more important than the principles we swore to ' \
    'protect,” Ms. Cheney said in her concession speech. She also claimed that Trump is promoting ' \
    'an insidious lie about the recent FBI raid of his Mar-a-Lago residence.'

repo = 'foo'

# On Nov 21, execution time for test_sentences1 was 53sec 844ms


def test_sentences1():
    sentence_classes, quotation_classes = parse_narrative(sentences1)
    graph_results = create_graph(sentence_classes, quotation_classes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert graph_results.number_processed == 4                         # 4 sentences
    assert 'logos' in ttl_str                                          # Percentages
    assert 'pathos' in ttl_str or 'exceptionalism' in ttl_str          # Principles we swore to protect
    assert 'loaded language' in ttl_str                                # Insidious lie
    assert ':Loss' in ttl_str                                          # conceded defeat
    assert ':has_active_entity :Liz_Cheney' in ttl_str
    assert ':Assessment' in ttl_str                                    # priority for Trump
    assert ':Win' in ttl_str                                           # won
    assert ':has_active_entity :Harriet_Hageman' in ttl_str
    assert ':Affiliation' in ttl_str                                   # endorsed
    assert ':has_active_entity :Donald_Trump' in ttl_str and ':affiliated_with :Harriet_Hageman' in ttl_str
    assert ':CommunicationAndSpeechAct' in ttl_str
    assert ':DeceptionAndDishonesty' in ttl_str                        # lie
    assert ':LawEnforcement ; :text "FBI raid' in ttl_str
    # Output Turtle:
    # :Sentence_0fed755c-b571 a :Sentence ; :offset 1 .
    # :Sentence_0fed755c-b571 :text "U.S. Rep. Liz Cheney conceded defeat Tuesday in the Republican primary in Wyoming,
    #     an outcome that was a priority for former President Donald Trump." .
    # :Sentence_0fed755c-b571 :mentions geo:6252001 .
    # :Sentence_0fed755c-b571 :mentions :Liz_Cheney .
    # :Sentence_0fed755c-b571 :mentions :Republican .
    # :Sentence_0fed755c-b571 :mentions :Wyoming .
    # :Sentence_0fed755c-b571 :mentions :Donald_Trump .
    # :Sentence_0fed755c-b571 :grade_level 10 .
    # :Sentence_cd98fa70-8dbb a :Sentence ; :offset 2 .
    # :Sentence_cd98fa70-8dbb :text "Harriet Hageman, a water and natural-resources attorney who was endorsed by the
    #     former president, won 66.3% of the vote to Ms. Cheney’s 28.9%, with 95% of all votes counted." .
    # :Sentence_cd98fa70-8dbb :mentions :Harriet_Hageman .
    # :Sentence_cd98fa70-8dbb :mentions :Liz_Cheney .
    # :Sentence_cd98fa70-8dbb :grade_level 10 .
    # :Sentence_cd98fa70-8dbb :rhetorical_device "logos" .
    # :Sentence_cd98fa70-8dbb :rhetorical_device_logos "The sentence uses statistics and numbers, such as \'66.3%\',
    #     \'28.9%\', and \'95%\', to convey information about the election results, which is an example of logos." .
    # :Sentence_80a74b61-c738 a :Sentence ; :offset 3 .
    # :Sentence_80a74b61-c738 :text "“No House seat, no office in this land is more important than the principles we
    #     swore to protect,” Ms. Cheney said in her concession speech." .
    # :Sentence_80a74b61-c738 :mentions :House .
    # :Sentence_80a74b61-c738 :mentions :Liz_Cheney .
    # :Sentence_80a74b61-c738 :grade_level 10 .
    # :Sentence_80a74b61-c738 :rhetorical_device "exceptionalism" .
    # :Sentence_80a74b61-c738 :rhetorical_device_exceptionalism "The sentence uses language that indicates the
    #     principles are unique and of utmost importance, suggesting exceptionalism." .
    # :Sentence_a255f9b4-bc31 a :Sentence ; :offset 4 .
    # :Sentence_a255f9b4-bc31 :text "She also claimed that Trump is promoting an insidious lie about the recent FBI
    #     raid of his Mar-a-Lago residence." .
    # :Sentence_a255f9b4-bc31 :mentions :Donald_Trump .
    # :Sentence_a255f9b4-bc31 :mentions :FBI .
    # :Sentence_a255f9b4-bc31 :mentions :Mar_a_Lago .
    # :Sentence_a255f9b4-bc31 :grade_level 10 .
    # :Sentence_a255f9b4-bc31 :rhetorical_device "loaded language" .
    # :Sentence_a255f9b4-bc31 :rhetorical_device_loaded_language "The phrase \'insidious lie\' uses loaded language
    #     with strong connotations that invoke emotions and judgments about the nature of the lie being described." .
    # :Sentence_0fed755c-b571 :has_semantic :Event_fdccf9c6-1e14 .
    # :Event_fdccf9c6-1e14 rdfs:label "Liz Cheney conceding defeat" .
    # :Event_fdccf9c6-1e14 a :Loss ; :confidence-Loss 100 .
    # :Event_fdccf9c6-1e14 a :CommunicationAndSpeechAct ; :confidence-CommunicationAndSpeechAct 90 .
    # :Event_fdccf9c6-1e14 :has_active_entity :Liz_Cheney .
    # :Sentence_0fed755c-b571 :has_semantic :Event_ff71167b-885a .
    # :Event_ff71167b-885a rdfs:label "Outcome being a priority for Donald Trump" .
    # :Event_ff71167b-885a a :Assessment ; :confidence-Assessment 90 .
    # :Event_ff71167b-885a :has_active_entity :Donald_Trump .
    # :Noun_908ee3fe-d177 a :End ; :text "Outcome" ; rdfs:label "Outcome; Republican primary result" ;
    #     :confidence 100 .
    # :Event_ff71167b-885a :has_topic :Noun_908ee3fe-d177 .
    # :Sentence_cd98fa70-8dbb :has_semantic :Event_6114b362-f2c2 .
    # :Event_6114b362-f2c2 rdfs:label "Harriet Hageman winning 66.3% of the vote" .
    # :Event_6114b362-f2c2 a :AchievementAndAccomplishment ; :confidence-AchievementAndAccomplishment 90 .
    # :Event_6114b362-f2c2 a :Win ; :confidence-Win 100 .
    # :Event_6114b362-f2c2 :has_active_entity :Harriet_Hageman .
    # :Sentence_cd98fa70-8dbb :has_semantic :Event_7d572af6-d38c .
    # :Event_7d572af6-d38c rdfs:label "Donald Trump endorsing Harriet Hageman" .
    # :Event_7d572af6-d38c a :CommunicationAndSpeechAct ; :confidence-CommunicationAndSpeechAct 100 .
    # :Event_7d572af6-d38c a :Affiliation ; :confidence-Affiliation 90 .
    # :Event_7d572af6-d38c :has_active_entity :Donald_Trump .
    # :Event_7d572af6-d38c :affiliated_with :Harriet_Hageman .
    # :Sentence_80a74b61-c738 :has_semantic :Event_5d682725-63a6 .
    # :Event_5d682725-63a6 rdfs:label "Liz Cheney saying no office is more important than principles" .
    # :Event_5d682725-63a6 a :CommunicationAndSpeechAct ; :confidence-CommunicationAndSpeechAct 100 .
    # :Event_5d682725-63a6 a :Assessment ; :confidence-Assessment 90 .
    # :Event_5d682725-63a6 :has_active_entity :Liz_Cheney .
    # :Sentence_a255f9b4-bc31 :has_semantic :Event_ab397df3-c137 .
    # :Event_ab397df3-c137 rdfs:label "Liz Cheney claiming Donald Trump is promoting a lie" .
    # :Event_ab397df3-c137 a :CommunicationAndSpeechAct ; :confidence-CommunicationAndSpeechAct 100 .
    # :Event_ab397df3-c137 a :DeceptionAndDishonesty ; :confidence-DeceptionAndDishonesty 100 .
    # :Event_ab397df3-c137 :has_active_entity :Liz_Cheney .
    # :Sentence_a255f9b4-bc31 :has_semantic :Event_6a2fb89d-062a .
    # :Event_6a2fb89d-062a rdfs:label "Donald Trump promoting an insidious lie" .
    # :Event_6a2fb89d-062a a :CommunicationAndSpeechAct ; :confidence-CommunicationAndSpeechAct 100 .
    # :Event_6a2fb89d-062a a :DeceptionAndDishonesty ; :confidence-DeceptionAndDishonesty 100 .
    # :Event_6a2fb89d-062a :has_active_entity :Donald_Trump .
    # :Noun_604f9102-a387 a :DeceptionAndDishonesty ; :text "Insidious lie" ; rdfs:label "Insidious lie; false
    #     information" ; :confidence 100 .
    # :Event_6a2fb89d-062a :has_topic :Noun_604f9102-a387 .
    # :Sentence_a255f9b4-bc31 :has_semantic :Event_0c3b548d-628b .
    # :Event_0c3b548d-628b rdfs:label "FBI raiding Mar-a-Lago residence" .
    # :Event_0c3b548d-628b a :LawEnforcement ; :confidence-LawEnforcement 100 .
    # :Event_0c3b548d-628b :has_active_entity :FBI .
    # :Noun_ae5d1b2e-c60d a :Location ; :text "Mar-a-Lago residence" ; rdfs:label "Mar-a-Lago residence; Donald
    #     Trump\'s property" ; :confidence 100 .
    # :Event_0c3b548d-628b :has_topic :Noun_ae5d1b2e-c60d .
    # :Quotation_eb148071-62c7 a :Quote ; :text "No House seat, no office in this land is more important than the
    #     principles we swore to protect," .
    # :Quotation_eb148071-62c7 :attributed_to :Liz_Cheney .
    # :Quotation_eb148071-62c7 :grade_level 10 .
    # :Quotation_eb148071-62c7 :rhetorical_device "exceptionalism" .
    # :Quotation_eb148071-62c7 :rhetorical_device_exceptionalism "The sentence uses language that indicates the
    #     principles are unique and exemplary, suggesting that no office or seat is more important than these
    #     principles, which is a form of exceptionalism." .
