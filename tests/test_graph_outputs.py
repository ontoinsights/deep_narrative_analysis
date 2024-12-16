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
    graph_results = create_graph(sentence_classes, quotation_classes, sentences1, ':Narrative_foo',
                                 ['politics and international'], 10, repo)
    ttl_str = str(graph_results.turtle)
    print(ttl_str)
    assert graph_results.number_processed == 4                         # 4 sentences
    assert 'logos' in ttl_str                                          # Percentages
    assert 'pathos' in ttl_str or 'exceptionalism' in ttl_str          # Principles we swore to protect
    assert 'loaded language' in ttl_str                                # Insidious lie
    assert ':Loss' in ttl_str                                          # conceded defeat
    assert ':has_active_entity :Liz_Cheney' in ttl_str
    assert ':AssessmentMeasurement' in ttl_str                         # priority for Trump
    assert ':Win' in ttl_str                                           # won
    assert ':has_active_entity :Harriet_Hageman' in ttl_str
    assert ':CommunicationAndSpeechAct' in ttl_str
    assert ':DeceptionAndDishonesty' in ttl_str                        # lie
    assert ':has_active_entity :Donald_Trump' in ttl_str
    assert ':LawEnforcement' in ttl_str
    # Output Turtle:
    # :Narrative_foo :has_component :Sentence_88229efa-e469 .
    # :Sentence_88229efa-e469 a :Sentence ; :offset 1 .
    # :Sentence_88229efa-e469 :text "U.S. Rep. Liz Cheney conceded defeat Tuesday in the Republican primary in
    #     Wyoming, an outcome that was a priority for former President Donald Trump." .
    # :Sentence_88229efa-e469 :mentions geo:6252001 .
    # :Sentence_88229efa-e469 :mentions :Liz_Cheney .
    # :Sentence_88229efa-e469 :mentions :Republican .
    # :Sentence_88229efa-e469 :mentions :Wyoming .
    # :Sentence_88229efa-e469 :mentions :Donald_Trump .
    # :Sentence_88229efa-e469 :grade_level 10 .
    # :Narrative_foo :has_component :Sentence_eada33e3-66d3 .
    # :Sentence_eada33e3-66d3 a :Sentence ; :offset 2 .
    # :Sentence_eada33e3-66d3 :text "Harriet Hageman, a water and natural-resources attorney who was endorsed by the
    #     former president, won 66.3% of the vote to Ms. Cheney’s 28.9%, with 95% of all votes counted." .
    # :Sentence_eada33e3-66d3 :mentions :Harriet_Hageman .
    # :Sentence_eada33e3-66d3 :mentions :Liz_Cheney .
    # :Sentence_eada33e3-66d3 :grade_level 10 .
    # :Sentence_eada33e3-66d3 :rhetorical_device "logos" .
    # :Sentence_eada33e3-66d3 :rhetorical_device_logos "The sentence uses statistics and numbers, such as \'66.3%\',
    #     \'28.9%\', and \'95%\', to convey information about the election results, which is an example of logos." .
    # :Narrative_foo :has_component :Sentence_e2db5daa-bce9 .
    # :Sentence_e2db5daa-bce9 a :Sentence ; :offset 3 .
    # :Sentence_e2db5daa-bce9 :text "“No House seat, no office in this land is more important than the principles we
    #     swore to protect,” Ms. Cheney said in her concession speech." .
    # :Sentence_e2db5daa-bce9 :mentions :House .
    # :Sentence_e2db5daa-bce9 :mentions :Liz_Cheney .
    # :Sentence_e2db5daa-bce9 :grade_level 10 .
    # :Sentence_e2db5daa-bce9 :rhetorical_device "exceptionalism" .
    # :Sentence_e2db5daa-bce9 :rhetorical_device_exceptionalism "The phrase \'no office in this land is more important
    #     than the principles we swore to protect\' suggests that the principles are unique and of utmost importance,
    #     indicating exceptionalism." .
    # :Narrative_foo :has_component :Sentence_4f831a4f-55e6 .
    # :Sentence_4f831a4f-55e6 a :Sentence ; :offset 4 .
    # :Sentence_4f831a4f-55e6 :text "She also claimed that Trump is promoting an insidious lie about the recent
    #     FBI raid of his Mar-a-Lago residence." .
    # :Sentence_4f831a4f-55e6 :mentions :Donald_Trump .
    # :Sentence_4f831a4f-55e6 :mentions :FBI .
    # :Sentence_4f831a4f-55e6 :mentions :Mar_a_Lago .
    # :Sentence_4f831a4f-55e6 :grade_level 10 .
    # :Sentence_4f831a4f-55e6 :rhetorical_device "loaded language" .
    # :Sentence_4f831a4f-55e6 :rhetorical_device_loaded_language "The phrase \'insidious lie\' uses loaded language
    #     with strong negative connotations to invoke emotions and judgments about the nature of the lie." .
    # :Narrative_foo :describes :NarrativeEvent_98703f56-82a7 .
    # :NarrativeEvent_98703f56-82a7 a :NarrativeEvent ; :offset 0 .
    # :NarrativeEvent_98703f56-82a7 :text "U.S. Rep. Liz Cheney conceded defeat in the Republican primary in Wyoming." .
    # :NarrativeEvent_98703f56-82a7 :has_semantic :Event_ff301d79-c0c5 .
    # :NarrativeEvent_98703f56-82a7 :has_first :Event_ff301d79-c0c5 .
    # :Event_ff301d79-c0c5 :text "Liz Cheney conceded defeat." .
    # :Event_ff301d79-c0c5 a :Loss ; :confidence-Loss 100 .
    # :Event_ff301d79-c0c5 a :CommunicationAndSpeechAct ; :confidence-CommunicationAndSpeechAct 90 .
    # :Event_ff301d79-c0c5 :has_active_entity :Liz_Cheney .
    # :NarrativeEvent_98703f56-82a7 :has_semantic :Event_a3cf5470-5062 .
    # :Event_ff301d79-c0c5 :has_next :Event_a3cf5470-5062 .
    # :Event_a3cf5470-5062 :text "The defeat was in the Republican primary." .
    # :Event_a3cf5470-5062 a :PoliticsRelated ; :confidence-PoliticsRelated 95 .
    # :Event_a3cf5470-5062 a :Loss ; :confidence-Loss 85 .
    # :Noun_3eacb301-2ad6 a :Loss ; :text "defeat" ; :confidence 100 .
    # :Event_a3cf5470-5062 :has_topic :Noun_3eacb301-2ad6 .
    # :Event_a3cf5470-5062 :has_context :Republican .
    # :NarrativeEvent_98703f56-82a7 :has_semantic :Event_9431d32a-6203 .
    # :Event_a3cf5470-5062 :has_next :Event_9431d32a-6203 .
    # :Event_9431d32a-6203 :text "The Republican primary was in Wyoming." .
    # :Event_9431d32a-6203 a :PoliticsRelated ; :confidence-PoliticsRelated 90 .
    # :Event_9431d32a-6203 a :AssessmentMeasurement ; :confidence-AssessmentMeasurement 80 .
    # :Event_9431d32a-6203 :has_topic :Republican .
    # :Event_9431d32a-6203 :has_location :Wyoming .
    # :Narrative_foo :describes :NarrativeEvent_750eb84e-786c .
    # :NarrativeEvent_750eb84e-786c a :NarrativeEvent ; :offset 1 .
    # :NarrativeEvent_750eb84e-786c :text "The outcome of the primary was a priority for former President
    #     Donald Trump." .
    # :NarrativeEvent_750eb84e-786c :has_semantic :Event_0180592e-4d6d .
    # :NarrativeEvent_750eb84e-786c :has_first :Event_0180592e-4d6d .
    # :Event_0180592e-4d6d :text "The outcome of the primary was a priority." .
    # :Event_0180592e-4d6d a :AssessmentMeasurement ; :confidence-AssessmentMeasurement 90 .
    # :Event_0180592e-4d6d a :End ; :confidence-End 80 .
    # :Noun_f7092777-a659 a :End ; :text "outcome" ; :confidence 90 .
    # :Event_0180592e-4d6d :has_context :Noun_f7092777-a659 .
    # :Noun_2dd3cf8d-d801 a owl:Thing ; :text "primary" ; :confidence 0 .     # TODO: Correct owl:Thing
    # :Event_0180592e-4d6d :has_context :Noun_2dd3cf8d-d801 .
    # :NarrativeEvent_750eb84e-786c :has_semantic :Event_1f89b12a-8aea .
    # :Event_0180592e-4d6d :has_next :Event_1f89b12a-8aea .
    # :Event_1f89b12a-8aea :text "The outcome of the primary was a priority for Donald Trump." .
    # :Event_1f89b12a-8aea a :AssessmentMeasurement ; :confidence-AssessmentMeasurement 90 .
    # :Event_1f89b12a-8aea a :Affiliation ; :confidence-Affiliation 70 .
    # :Event_1f89b12a-8aea :has_context :Noun_f7092777-a659 .
    # :Event_1f89b12a-8aea :has_context :Noun_2dd3cf8d-d801 .
    # :Event_1f89b12a-8aea :has_context :Donald_Trump .
    # :Narrative_foo :describes :NarrativeEvent_3f043ddf-a6af .
    # :NarrativeEvent_3f043ddf-a6af a :NarrativeEvent ; :offset 2 .
    # :NarrativeEvent_3f043ddf-a6af :text "Harriet Hageman, endorsed by the former president, won 66.3% of the vote
    #     to Liz Cheney’s 28.9%, with 95% of all votes counted." .
    # :NarrativeEvent_3f043ddf-a6af :has_semantic :Event_beb95aae-5049 .
    # :NarrativeEvent_3f043ddf-a6af :has_first :Event_beb95aae-5049 .
    # :Event_beb95aae-5049 :text "Harriet Hageman won 66.3% of the vote." .
    # :Event_beb95aae-5049 a :Win ; :confidence-Win 100 .
    # :Event_beb95aae-5049 a :PoliticsRelated ; :confidence-PoliticsRelated 90 .
    # :Event_beb95aae-5049 :has_active_entity :Harriet_Hageman .
    # :Noun_1516903c-80ca a :Measurement, :Collection ; :text "66.3% of the vote" ; :confidence 90 .
    # :Event_beb95aae-5049 :has_quantification :Noun_1516903c-80ca .
    # :NarrativeEvent_3f043ddf-a6af :has_semantic :Event_f941fe8c-7ad8 .
    # :Event_beb95aae-5049 :has_next :Event_f941fe8c-7ad8 .
    # :Event_f941fe8c-7ad8 :text "Liz Cheney received 28.9% of the vote." .
    # :Event_f941fe8c-7ad8 a :Loss ; :confidence-Loss 100 .
    # :Event_f941fe8c-7ad8 a :PoliticsRelated ; :confidence-PoliticsRelated 90 .
    # :Event_f941fe8c-7ad8 :has_active_entity :Liz_Cheney .
    # :NarrativeEvent_3f043ddf-a6af :has_semantic :Event_4bb44807-ea77 .
    # :Event_f941fe8c-7ad8 :has_next :Event_4bb44807-ea77 .
    # :Event_4bb44807-ea77 :text "95% of all votes were counted." .
    # :Event_4bb44807-ea77 a :Measurement ; :confidence-Measurement 100 .
    # :Event_4bb44807-ea77 a :PoliticsRelated ; :confidence-PoliticsRelated 80 .
    # :Noun_ed982029-7a6c a :Polling, :Collection ; :text "95% of all votes" ; :confidence 85 .
    # :Event_4bb44807-ea77 :has_quantification :Noun_ed982029-7a6c .
    # :Narrative_foo :describes :NarrativeEvent_6d36406d-18be .
    # :NarrativeEvent_6d36406d-18be a :NarrativeEvent ; :offset 3 .
    # :NarrativeEvent_6d36406d-18be :text "Liz Cheney stated in her concession speech that no House seat or office
    #     is more important than the principles sworn to protect." .
    # :NarrativeEvent_6d36406d-18be :has_semantic :Event_911e2eea-f2d1 .
    # :NarrativeEvent_6d36406d-18be :has_first :Event_911e2eea-f2d1 .
    # :Event_911e2eea-f2d1 :text "Liz Cheney stated something in her concession speech." .
    # :Event_911e2eea-f2d1 a :CommunicationAndSpeechAct ; :confidence-CommunicationAndSpeechAct 100 .
    # :Event_911e2eea-f2d1 a :PoliticsRelated ; :confidence-PoliticsRelated 80 .
    # :Event_911e2eea-f2d1 :has_active_entity :Liz_Cheney .
    # :Noun_ffe142c9-a890 a :CommunicationAndSpeechAct ; :text "concession speech" ; :confidence 95 .
    # :Event_911e2eea-f2d1 :has_context :Noun_ffe142c9-a890 .
    # :NarrativeEvent_6d36406d-18be :has_semantic :Event_f5e35edf-409d .
    # :Event_911e2eea-f2d1 :has_next :Event_f5e35edf-409d .
    # :Event_f5e35edf-409d :text "Liz Cheney stated that no House seat or office is more important than the
    #     principles sworn to protect." .
    # :Event_f5e35edf-409d a :CommunicationAndSpeechAct ; :confidence-CommunicationAndSpeechAct 100 .
    # :Event_f5e35edf-409d a :Cognition ; :confidence-Cognition 70 .
    # :Event_f5e35edf-409d :has_active_entity :Liz_Cheney .
    # :Event_f5e35edf-409d :has_topic :House .
    # :Noun_6a885f65-5950 a :Resource ; :text "office" ; :confidence 80 .
    # :Event_f5e35edf-409d :has_topic :Noun_6a885f65-5950 .
    # :Noun_c645cbed-dd91 a :FreedomAndSupportForHumanRights, :Collection ; :text "principles" ; :confidence 85 .
    # :Event_f5e35edf-409d :has_topic :Noun_c645cbed-dd91 .
    # :Narrative_foo :describes :NarrativeEvent_6398c5f4-0146 .
    # :NarrativeEvent_6398c5f4-0146 a :NarrativeEvent ; :offset 4 .
    # :NarrativeEvent_6398c5f4-0146 :text "Liz Cheney claimed that Trump is promoting an insidious lie about the
    #     recent FBI raid of his Mar-a-Lago residence." .
    # :NarrativeEvent_6398c5f4-0146 :has_semantic :Event_9bb5a09f-c2dc .
    # :NarrativeEvent_6398c5f4-0146 :has_first :Event_9bb5a09f-c2dc .
    # :Event_9bb5a09f-c2dc :text "Liz Cheney claimed." .
    # :Event_9bb5a09f-c2dc a :CommunicationAndSpeechAct ; :confidence-CommunicationAndSpeechAct 100 .
    # :Event_9bb5a09f-c2dc a :AssessmentMeasurement ; :confidence-AssessmentMeasurement 80 .
    # :Event_9bb5a09f-c2dc :has_active_entity :Liz_Cheney .
    # :NarrativeEvent_6398c5f4-0146 :has_semantic :Event_71b65d3a-9666 .
    # :Event_9bb5a09f-c2dc :has_next :Event_71b65d3a-9666 .
    # :Event_71b65d3a-9666 :text "Trump is promoting an insidious lie." .
    # :Event_71b65d3a-9666 a :DeceptionAndDishonesty ; :confidence-DeceptionAndDishonesty 100 .
    # :Event_71b65d3a-9666 a :CorruptionAndFraud ; :confidence-CorruptionAndFraud 90 .
    # :Event_71b65d3a-9666 :has_active_entity :Donald_Trump .
    # :Noun_cf38478d-cff5 a :DeceptionAndDishonesty ; :text "insidious lie" ; :confidence 90 .
    # :Event_71b65d3a-9666 :has_topic :Noun_cf38478d-cff5 .
    # :NarrativeEvent_6398c5f4-0146 :has_semantic :Event_4ee598de-6569 .
    # :Event_71b65d3a-9666 :has_next :Event_4ee598de-6569 .
    # :Event_4ee598de-6569 :text "The insidious lie is about the recent FBI raid of Trump\'s Mar-a-Lago residence." .
    # :Event_4ee598de-6569 a :AssessmentMeasurement ; :confidence-AssessmentMeasurement 90 .
    # :Event_4ee598de-6569 a :LawEnforcement ; :confidence-LawEnforcement 85 .
    # :Event_4ee598de-6569 :has_context :Noun_cf38478d-cff5 .
    # :Event_4ee598de-6569 :has_context :FBI .
    # :Mar_a_Lago :clarifying_reference :Donald_Trump .
    # :Mar_a_Lago :clarifying_text "Trump\'s" .
    # :Event_4ee598de-6569 :has_context :Mar_a_Lago .
    # :Quotation_c962b0be-53df a :Quote ; :text "No House seat, no office in this land is more important than the
    #     principles we swore to protect," .
    # :Quotation_c962b0be-53df :attributed_to :Liz_Cheney .
    # :Quotation_c962b0be-53df :grade_level 10 .
    # :Quotation_c962b0be-53df :rhetorical_device "exceptionalism" .
    # :Quotation_c962b0be-53df :rhetorical_device_exceptionalism "The sentence uses exceptionalism by implying
    #     that the principles sworn to protect are of utmost importance, suggesting they are unique and exemplary
    #     compared to any House seat or office." .
