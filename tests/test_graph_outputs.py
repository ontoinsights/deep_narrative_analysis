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


def test_sentences1():
    parse_results = parse_narrative(sentences1)
    graph_results = create_graph(parse_results.sentence_classes, parse_results.quotation_classes,
                                 parse_results.partial_quotes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert graph_results.number_sentences == 4       # 4 sentence
    assert ':Loss' in ttl_str and ':text "conceded' in ttl_str and ':text "defeat' in ttl_str
    assert ':has_active_entity :Liz_Cheney' in ttl_str
    assert ':PoliticalEvent ; :text "Republican primary' in ttl_str and ':has_context :Noun' in ttl_str
    assert ':has_location :Wyoming' in ttl_str
    assert ':End ; :text "outcome' in ttl_str
    assert ':Assessment ; :text "priority' in ttl_str and ':has_quantification :Noun' in ttl_str
    assert ':Win' in ttl_str and ':text "won' in ttl_str
    assert ':has_active_entity :Harriet_Hageman' in ttl_str
    assert ':Measurement' in ttl_str and (':text "66.3%' in ttl_str or ':text "counted' in ttl_str or
                                          ':text "vote' in ttl_str)
    assert ':Affiliation' in ttl_str and (':text "was endorsed' in ttl_str or ':text "endorsed' in ttl_str)
    assert ':affiliated_with :Harriet_Hageman' in ttl_str
    assert ':Person ; :text "former ' in ttl_str and ':has_active_entity :Noun' in ttl_str
    assert ':CommunicationAndSpeechAct' in ttl_str and ':text "said' in ttl_str and ':text "claimed' in ttl_str
    assert ':DeceptionAndDishonesty' in ttl_str and ':text "insidious lie' in ttl_str and \
           (':has_topic :Noun' in ttl_str or ':has_context :Noun' in ttl_str)
    assert ':text "is promoting' in ttl_str
    assert ':has_active_entity :Donald_Trump' in ttl_str
    assert ':LawEnforcement' in ttl_str and  (':text "raid' in ttl_str or 'FBI raid' in ttl_str)
    assert ':has_location :Noun' in ttl_str
    assert 'logos' in ttl_str                                          # Percentages
    assert 'pathos' in ttl_str or 'exceptionalism' in ttl_str          # Principles we swore to protect
    assert 'loaded language' in ttl_str                                # Insidious lie
    # Output Turtle:
    # :Sentence_12bd76ab-06fe a :Sentence ; :offset 1 .
    # :Sentence_12bd76ab-06fe :text "U.S. Rep. Liz Cheney conceded defeat Tuesday in the Republican primary in
    #     Wyoming, an outcome that was a priority for former President Donald Trump." .
    # :Sentence_12bd76ab-06fe :mentions geo:6252001 .
    # :Sentence_12bd76ab-06fe :mentions :Liz_Cheney .
    # :Sentence_12bd76ab-06fe :mentions :Republican .
    # :Sentence_12bd76ab-06fe :mentions :Wyoming .
    # :Sentence_12bd76ab-06fe :mentions :Donald_Trump .
    # :Sentence_12bd76ab-06fe :grade_level 10 .
    # :Sentence_f77b6bb7-5e28 a :Sentence ; :offset 2 .
    # :Sentence_f77b6bb7-5e28 :text "Harriet Hageman, a water and natural-resources attorney who was endorsed by the
    #     former president, won 66.3% of the vote to Ms. Cheney’s 28.9%, with 95% of all votes counted." .
    # :Sentence_f77b6bb7-5e28 :mentions :Harriet_Hageman .
    # :Sentence_f77b6bb7-5e28 :mentions :Liz_Cheney .
    # :Sentence_f77b6bb7-5e28 :grade_level 10 .
    # :Sentence_f77b6bb7-5e28 :rhetorical_device "logos" .
    # :Sentence_f77b6bb7-5e28 :rhetorical_device_logos "The sentence uses statistics and numbers to convey the
    #     election results, specifically the percentages of votes won by Harriet Hageman and Ms. Cheney, as well as
    #     the percentage of votes counted." .
    # :Sentence_6ce57152-27e7 a :Sentence ; :offset 3 .
    # :Sentence_6ce57152-27e7 :text "“No House seat, no office in this land is more important than the principles we
    #     swore to protect,” Ms. Cheney said in her concession speech." .
    # :Sentence_6ce57152-27e7 :has_component :Quotation0 .
    # :Sentence_6ce57152-27e7 :mentions :House .
    # :Sentence_6ce57152-27e7 :mentions :Liz_Cheney .
    # :Sentence_6ce57152-27e7 :grade_level 10 .
    # :Sentence_6ce57152-27e7 :rhetorical_device "exceptionalism" .
    # :Sentence_6ce57152-27e7 :rhetorical_device_exceptionalism "The phrase \'No House seat, no office in this land
    #     is more important\' suggests that the principles are unique and of utmost importance, indicating a sense
    #     of exceptionalism." .
    # :Sentence_1e0eefaa-2a25 a :Sentence ; :offset 4 .
    # :Sentence_1e0eefaa-2a25 :text "She also claimed that Trump is promoting an insidious lie about the recent FBI
    #     raid of his Mar-a-Lago residence." .
    # :Sentence_1e0eefaa-2a25 :mentions :Donald_Trump .
    # :Sentence_1e0eefaa-2a25 :mentions :FBI .
    # :Sentence_1e0eefaa-2a25 :mentions :Mar_a_Lago .
    # :Sentence_1e0eefaa-2a25 :grade_level 10 .
    # :Sentence_1e0eefaa-2a25 :rhetorical_device "loaded language" .
    # :Sentence_1e0eefaa-2a25 :rhetorical_device_loaded_language "The phrase \'insidious lie\' uses loaded language
    #     with strong connotations that invoke emotions and judgments about the nature of the lie." .
    # **** Sentence semantics ****
    # :Sentence_12bd76ab-06fe :summary "Liz Cheney conceded defeat in Wyoming Republican primary." .
    # :Sentence_12bd76ab-06fe :has_semantic :Event_3267344e-5c1e .
    # :Event_3267344e-5c1e :text "conceded" .
    # :Event_3267344e-5c1e a :Loss ; :confidence-Loss 100 .
    # :Event_3267344e-5c1e :has_active_entity :Liz_Cheney .
    # :Event_3267344e-5c1e :text "defeat" .
    # :Event_3267344e-5c1e :has_time [ a :Time ; :text "Tuesday" ] .
    # :Noun_c60cee00-4680 a :PoliticalEvent ; :text "Republican primary" ; :confidence 90 .
    # :Event_3267344e-5c1e :has_context :Noun_c60cee00-4680 .
    # :Event_3267344e-5c1e :has_location :Wyoming .
    # :Sentence_12bd76ab-06fe :has_semantic :Event_64fbd340-2f0b .
    # :Event_64fbd340-2f0b :text "was" .
    # :Event_64fbd340-2f0b a :EnvironmentAndCondition ; :confidence-EnvironmentAndCondition 100 .
    # :Noun_abad90fc-08ed a :End ; :text "outcome" ; :confidence 100 .
    # :Event_64fbd340-2f0b :has_context :Noun_abad90fc-08ed .
    # :Noun_ef94f581-1e55 a :Assessment ; :text "priority" ; :confidence 100 .
    # :Event_64fbd340-2f0b :has_quantification :Noun_ef94f581-1e55 .
    # :Event_64fbd340-2f0b :has_context :Donald_Trump .
    # :Sentence_f77b6bb7-5e28 :summary "Harriet Hageman won Wyoming primary with Trump\'s endorsement." .
    # :Sentence_f77b6bb7-5e28 :has_semantic :Event_27a9f563-2658 .
    # :Event_27a9f563-2658 :text "won" .
    # :Event_27a9f563-2658 a :Win ; :confidence-Win 100 .
    # :Event_27a9f563-2658 :has_active_entity :Harriet_Hageman .
    # :Noun_ff01c9fb-4030 a :Measurement ; :text "66.3% of the vote" ; :confidence 90 .
    # :Event_27a9f563-2658 :has_quantification :Noun_ff01c9fb-4030 .
    # :Sentence_f77b6bb7-5e28 :has_semantic :Event_137118b7-13e2 .
    # :Event_137118b7-13e2 :text "was endorsed" .
    # :Event_137118b7-13e2 a :Affiliation ; :confidence-Affiliation 100 .
    # :Event_137118b7-13e2 :affiliated_with :Harriet_Hageman .
    # :Noun_e83ad3e4-ab3b a :Person ; :text "former President Donald Trump" ; :confidence 100 .
    # :Event_137118b7-13e2 :has_active_entity :Noun_e83ad3e4-ab3b .
    # :Sentence_6ce57152-27e7 :summary "Cheney made a concession speech." .
    # :Sentence_6ce57152-27e7 :has_semantic :Event_83bfcdd8-7c40 .
    # :Event_83bfcdd8-7c40 :text "said" .
    # :Event_83bfcdd8-7c40 a :CommunicationAndSpeechAct ; :confidence-CommunicationAndSpeechAct 100 .
    # :Event_83bfcdd8-7c40 :has_active_entity :Liz_Cheney .
    # :Noun_18e4076e-01e4 a :InformationSource ; :text "concession speech" ; :confidence 90 .
    # :Event_83bfcdd8-7c40 :has_context :Noun_18e4076e-01e4 .
    # :Sentence_1e0eefaa-2a25 :summary "Cheney claimed Trump promotes lie about Mar-a-Lago raid." .
    # :Sentence_1e0eefaa-2a25 :has_semantic :Event_2c79be45-d419 .
    # :Event_2c79be45-d419 :text "claimed" .
    # :Event_2c79be45-d419 a :CommunicationAndSpeechAct ; :confidence-CommunicationAndSpeechAct 100 .
    # :Event_2c79be45-d419 :has_active_entity :Liz_Cheney .
    # :Noun_4b469d2d-57c4 a :DeceptionAndDishonesty ; :text "insidious lie" ; :confidence 95 .
    # :Event_2c79be45-d419 :has_context :Noun_4b469d2d-57c4 .
    # :Sentence_1e0eefaa-2a25 :has_semantic :Event_16b28f72-7c5e .
    # :Event_16b28f72-7c5e :text "is promoting" .
    # :Event_16b28f72-7c5e a :DeceptionAndDishonesty ; :confidence-DeceptionAndDishonesty 100 .
    # :Event_16b28f72-7c5e :has_active_entity :Donald_Trump .
    # :Event_16b28f72-7c5e :text "insidious lie" .
    # :Noun_06a2682d-b7dd a :LawEnforcement ; :text "FBI raid" ; :confidence 90 .
    # :Event_16b28f72-7c5e :has_context :Noun_06a2682d-b7dd .
    # :Noun_58615f69-3256 a :Location ; :text "Mar-a-Lago residence" ; :confidence 100 .
    # :Event_16b28f72-7c5e :has_location :Noun_58615f69-3256 .
    # :Quotation0 a :Quote ; :text "No House seat, no office in this land is more important than the principles we
    #     swore to protect," .
    # :Quotation0 :attributed_to :Liz_Cheney .
    # :Quotation0 :grade_level 10 .
    # :Quotation0 :rhetorical_device "exceptionalism" .
    # :Quotation0 :rhetorical_device_exceptionalism "The phrase \'no office in this land is more important\' suggests
    #     that the principles are unique and exemplary, indicating exceptionalism." .
