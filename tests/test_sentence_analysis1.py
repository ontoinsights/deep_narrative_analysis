import pytest
from dna.create_narrative_turtle import create_graph
from dna.nlp import parse_narrative

text_clauses1 = 'While Mary exercised, John practiced guitar.'
text_clauses2 = 'George agreed with the plan that Mary outlined.'
text_aux_only = 'Joe is an attorney.'
text_affiliation = 'Joe is a member of the Mayberry Book Club.'
text_complex1 = \
    'Rep. Liz Cheney R-WY compared herself to former President Abraham Lincoln during her concession ' \
    'speech shortly after her loss to Trump-backed Republican challenger Harriet Hageman.'
text_complex2 = \
    'Harriet Hageman, a water and natural-resources attorney who was endorsed by the former president, won ' \
    '66.3% of the vote to Ms. Cheney’s 28.9%, with 95% of all votes counted.'
text_coref = 'Joe broke his foot. He went to the doctor.'
text_xcomp = 'Mary enjoyed being with her grandfather.'
text_modal = 'Mary can visit her grandfather on Tuesday.'
text_modal_neg = 'Mary will not visit her grandfather next Tuesday.'
text_acomp = 'Mary is very beautiful.'
text_acomp_pcomp1 = 'Peter got tired of running.'
text_acomp_pcomp2 = 'Peter never tires of running.'
text_acomp_xcomp = 'Jane is unable to tolerate smoking.'
text_idiom = 'Wear and tear on the bridge caused its collapse.'
text_idiom_full_pass = 'John was accused by George of breaking and entering.'
text_idiom_trunc_pass = 'John was accused of breaking and entering.'
text_negation_emotion = 'Jane has no liking for broccoli.'
text_negation = 'Jane did not stab John.'
text_mention = 'The FBI raided the house.'

repo = "foo"

# Note that it is unlikely that all tests will complete successfully since event semantics can be
# interpreted/reported in multiple ways
# 80%+ of the tests should pass


def test_clauses1():
    sentence_classes, quotation_classes = parse_narrative(text_clauses1)
    graph_results = create_graph(sentence_classes, quotation_classes,5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':has_active_entity :Mary' in ttl_str
    assert ':has_active_entity :John' in ttl_str
    assert 'a :BodilyAct' in ttl_str and ':text "exercised' in ttl_str
    assert (':ArtAndEntertainmentEvent' in ttl_str or ':EducationRelated' in ttl_str) and ':text "practiced' in ttl_str
    assert 'a :MusicalInstrument ; :text "guitar' in ttl_str
    assert ':has_instrument :Noun' in ttl_str or ':has_topic :Noun' in ttl_str
    # Output Turtle:
    # :Sentence_5897d614-07c0 a :Sentence ; :offset 1 .
    # :Sentence_5897d614-07c0 :text "While Mary exercised, John practiced guitar." .
    # :Sentence_5897d614-07c0 :mentions :Mary .
    # :Sentence_5897d614-07c0 :mentions :John .
    # :Sentence_5897d614-07c0 :grade_level 5 .
    # :Sentence_5897d614-07c0 :summary "While Mary exercised, John practiced guitar." .
    # :Sentence_5897d614-07c0 :has_semantic :Event_bc32a5a8-810d .
    # :Event_bc32a5a8-810d :text "exercised" .
    # :Event_bc32a5a8-810d a :BodilyAct ; :confidence-BodilyAct 100 .
    # :Event_bc32a5a8-810d :has_active_entity :Mary .
    # :Sentence_5897d614-07c0 :has_semantic :Event_53dee84c-4cd7 .
    # :Event_53dee84c-4cd7 :text "practiced" .
    # :Event_53dee84c-4cd7 a :ArtAndEntertainmentEvent ; :confidence-ArtAndEntertainmentEvent 100 .
    # :Event_53dee84c-4cd7 :has_active_entity :John .
    # :Noun_9d221bf3-385f a :MusicalInstrument ; :text "guitar" ; :confidence 100 .
    # :Event_53dee84c-4cd7 :has_instrument :Noun_9d221bf3-385f .


def test_clauses2():
    sentence_classes, quotation_classes = parse_narrative(text_clauses2)
    graph_results = create_graph(sentence_classes, quotation_classes,5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':has_active_entity :George' in ttl_str
    assert ':Agreement' in ttl_str and ':text "agreed' in ttl_str
    assert ':Process ; :text "plan' in ttl_str or ':Cognition ; :text "plan' in ttl_str
    assert ':CommunicationAndSpeechAct' in ttl_str and ':text "outlined' in ttl_str
    assert ':has_active_entity :Mary' in ttl_str
    assert ':has_topic :Noun'
    # Output Turtle:
    # :Sentence_78b356ac-9a45 a :Sentence ; :offset 1 .
    # :Sentence_78b356ac-9a45 :text "George agreed with the plan that Mary outlined." .
    # :Sentence_78b356ac-9a45 :mentions :George .
    # :Sentence_78b356ac-9a45 :mentions :Mary .
    # :Sentence_78b356ac-9a45 :grade_level 8 .
    # :Sentence_78b356ac-9a45 :summary "George agreed with the plan that Mary outlined." .
    # :Sentence_78b356ac-9a45 :has_semantic :Event_9fc158b5-353c .
    # :Event_9fc158b5-353c :text "agreed" .
    # :Event_9fc158b5-353c a :Agreement ; :confidence-Agreement 100 .
    # :Event_9fc158b5-353c :has_active_entity :George .
    # :Noun_12ccd540-84da a :Process ; :text "plan" ; :confidence 90 .
    # :Event_9fc158b5-353c :has_topic :Noun_12ccd540-84da .
    # :Sentence_78b356ac-9a45 :has_semantic :Event_44fd0030-bdd5 .
    # :Event_44fd0030-bdd5 :text "outlined" .
    # :Event_44fd0030-bdd5 a :CommunicationAndSpeechAct ; :confidence-CommunicationAndSpeechAct 90 .
    # :Event_44fd0030-bdd5 :has_active_entity :Mary .
    # :Event_44fd0030-bdd5 :has_topic :Noun_12ccd540-84da .


def test_aux_only():
    sentence_classes, quotation_classes = parse_narrative(text_aux_only)
    graph_results = create_graph(sentence_classes, quotation_classes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert 'a :EnvironmentAndCondition' in ttl_str     # is
    assert ':has_context :Joe' in ttl_str
    assert 'a :LineOfBusiness ; :text "attorney' in ttl_str
    assert ':has_aspect :Noun' in ttl_str
    # Output Turtle:
    # :Sentence_7b634962-247f a :Sentence ; :offset 1 .
    # :Sentence_7b634962-247f :text "Joe is an attorney." .
    # :Sentence_7b634962-247f :mentions :Joe .
    # :Sentence_7b634962-247f :grade_level 3 .
    # :Sentence_7b634962-247f :summary "Joe is an attorney." .
    # :Sentence_7b634962-247f :has_semantic :Event_770b98fd-32ee .
    # :Event_770b98fd-32ee :text "is" .
    # :Event_770b98fd-32ee a :EnvironmentAndCondition ; :confidence-EnvironmentAndCondition 100 .
    # :Event_770b98fd-32ee :has_context :Joe .      # Whose/what condition is described
    # :Noun_c98bfda5-73d9 a :LineOfBusiness ; :text "attorney" ; :confidence 100 .
    # :Event_770b98fd-32ee :has_aspect :Noun_c98bfda5-73d9 .


def test_affiliation():
    sentence_classes, quotation_classes = parse_narrative(text_affiliation)
    graph_results = create_graph(sentence_classes, quotation_classes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':Affiliation' in ttl_str
    assert ':has_active_entity :Joe' in ttl_str or ':has_context :Joe' in ttl_str or ':affiliated_with :Joe' in ttl_str
    assert ':affiliated_with :Mayberry_' in ttl_str
    # Output Turtle:
    # :Sentence_e6100aed-85f9 a :Sentence ; :offset 1 .
    # :Sentence_e6100aed-85f9 :text "Joe is a member of the Mayberry Book Club." .
    # :Sentence_e6100aed-85f9 :mentions :Joe .
    # :Sentence_e6100aed-85f9 :mentions :Mayberry_Book_Club .
    # :Sentence_e6100aed-85f9 :grade_level 3 .
    # :Sentence_e6100aed-85f9 :summary "Joe is a member of the Mayberry Book Club." .
    # :Sentence_e6100aed-85f9 :has_semantic :Event_90e4eb86-4e0e .
    # :Event_90e4eb86-4e0e :text "is" .
    # :Event_90e4eb86-4e0e a :EnvironmentAndCondition ; :confidence-EnvironmentAndCondition 100 .
    # :Event_90e4eb86-4e0e :has_context :Joe .
    # :Event_90e4eb86-4e0e a :Affiliation .
    # :Event_90e4eb86-4e0e :affiliated_with :Mayberry_Book_Club .


def test_complex1():
    sentence_classes, quotation_classes = parse_narrative(text_complex1)
    graph_results = create_graph(sentence_classes, quotation_classes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':mentions :Liz_Cheney' in ttl_str and ':mentions :Harriet_Hageman' in ttl_str
    assert ':mentions :Abraham_Lincoln' in ttl_str
    assert ':mentions :Donald_Trump' in ttl_str
    assert 'allusion' in ttl_str
    assert ':Cognition' in ttl_str and ':text "compared' in ttl_str
    assert ':has_active_entity :Liz_Cheney' in ttl_str        # Cheney compared herself
    assert ':has_topic :Abraham_Lincoln' in ttl_str           # to Lincoln
    assert ':Loss' in ttl_str
    assert ':has_affected_entity :Harriet_Hageman' in ttl_str
    # Output:
    # :Sentence_9f1f0bd3-a44e a :Sentence ; :offset 1 .
    # :Sentence_9f1f0bd3-a44e :text "Rep. Liz Cheney R-WY compared herself to former President Abraham Lincoln during
    #     her concession speech shortly after her loss to Trump-backed Republican challenger Harriet Hageman." .
    # :Sentence_9f1f0bd3-a44e :mentions :Liz_Cheney .
    # :Sentence_9f1f0bd3-a44e :mentions :WY .
    # :Sentence_9f1f0bd3-a44e :mentions :Abraham_Lincoln .
    # :Sentence_9f1f0bd3-a44e :mentions :Trump .
    # :Sentence_9f1f0bd3-a44e :mentions :Republican .
    # :Sentence_9f1f0bd3-a44e :mentions :Harriet_Hageman .
    # :Sentence_9f1f0bd3-a44e :grade_level 10 .
    # :Sentence_9f1f0bd3-a44e :rhetorical_device "allusion" .
    # :Sentence_9f1f0bd3-a44e :rhetorical_device_allusion "The sentence uses an allusion by referencing Abraham
    #     Lincoln, a historical figure with symbolic meaning." .
    # :Sentence_9f1f0bd3-a44e :summary "Liz Cheney compared herself to Abraham Lincoln after losing to
    #     Harriet Hageman." .
    # :Sentence_9f1f0bd3-a44e :has_semantic :Event_a7818f24-9134 .
    # :Event_a7818f24-9134 :text "compared" .
    # :Event_a7818f24-9134 a :Cognition ; :confidence-Cognition 100 .
    # :Event_a7818f24-9134 :has_active_entity :Liz_Cheney .
    # :Event_a7818f24-9134 :has_topic :Liz_Cheney .
    # :Event_a7818f24-9134 :has_topic :Abraham_Lincoln .
    # :Sentence_9f1f0bd3-a44e :has_semantic :Event_eaaf8883-3a21 .
    # :Event_eaaf8883-3a21 :text "losing" .
    # :Event_eaaf8883-3a21 a :Loss ; :confidence-Loss 100 .
    # :Event_eaaf8883-3a21 :has_active_entity :Liz_Cheney .
    # :Event_eaaf8883-3a21 :has_affected_entity :Harriet_Hageman .


def test_complex2():
    sentence_classes, quotation_classes = parse_narrative(text_complex2)
    graph_results = create_graph(sentence_classes, quotation_classes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert 'logos'
    assert 'a :Win' in ttl_str and ':text "won' in ttl_str
    assert ':has_active_entity :Harriet_Hageman' in ttl_str
    assert ':Measurement' in ttl_str and (':text "66.3%' in ttl_str or ':text "counted' in ttl_str or
                                          ':text "vote' in ttl_str)
    if ':text "66.3%' in ttl_str:
        assert ':has_quantification :Noun' in ttl_str
    if ':text "vote' in ttl_str:
        assert ':has_context :Noun' in ttl_str
    # Output Turtle:
    # :Sentence_d072e763-ec45 a :Sentence ; :offset 1 .
    # :Sentence_d072e763-ec45 :text "Harriet Hageman, a water and natural-resources attorney who was endorsed by the
    #     former president, won 66.3% of the vote to Ms. Cheney’s 28.9%, with 95% of all votes counted." .
    # :Sentence_d072e763-ec45 :mentions :Harriet_Hageman .
    # :Sentence_d072e763-ec45 :mentions :Liz_Cheney .
    # :Sentence_d072e763-ec45 :grade_level 10 .
    # :Sentence_d072e763-ec45 :rhetorical_device "logos" .
    # :Sentence_d072e763-ec45 :rhetorical_device_logos "The use of specific percentages and vote counts is an
    #     example of logos." .
    # :Sentence_d072e763-ec45 :summary "Harriet Hageman won 66.3% of the vote to Cheney’s 28.9%." .
    # :Sentence_d072e763-ec45 :has_semantic :Event_7f38acc5-1f56 .
    # :Event_7f38acc5-1f56 :text "won" .
    # :Event_7f38acc5-1f56 a :Win ; :confidence-Win 100 .
    # :Event_7f38acc5-1f56 :has_active_entity :Harriet_Hageman .
    # :Noun_21322a43-6c37 a :Measurement ; :text "vote" ; :confidence 90 .
    # :Event_7f38acc5-1f56 :has_context :Noun_21322a43-6c37 .


def test_coref():
    sentence_classes, quotation_classes = parse_narrative(text_coref)
    graph_results = create_graph(sentence_classes, quotation_classes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':HealthAndDiseaseRelated' in ttl_str and ':text "broke' in ttl_str
    assert ':MovementTravelAndTransportation' in ttl_str and ':text "went' in ttl_str
    assert ':has_active_entity :Joe' in ttl_str
    assert ':ComponentPart' in ttl_str and ':text "foot' in ttl_str
    assert ':has_affected_entity :Noun' in ttl_str or ':has_topic :Noun' in ttl_str       # Broke his foot
    assert ':text "doctor' in ttl_str
    if 'a :LineOfBusiness' in ttl_str:
        assert ':has_destination :Noun' in ttl_str or ':has_location :Noun' in ttl_str
    if 'a :Person' in ttl_str:
        assert ':has_affected_entity :Noun' in ttl_str
    # Output Turtle:
    # :Sentence_6086e8fc-72c5 a :Sentence ; :offset 1 .
    # :Sentence_6086e8fc-72c5 :text "Joe broke his foot." .
    # :Sentence_6086e8fc-72c5 :mentions :Joe .
    # :Sentence_6086e8fc-72c5 :grade_level 3 .
    # :Sentence_6086e8fc-72c5 :summary "Joe broke his foot." .
    # :Sentence_d75bffd9-7eb1 a :Sentence ; :offset 2 .
    # :Sentence_d75bffd9-7eb1 :text "He went to the doctor." .
    # :Sentence_d75bffd9-7eb1 :grade_level 1 .
    # :Sentence_d75bffd9-7eb1 :summary "He went to the doctor." .
    # :Sentence_6086e8fc-72c5 :has_semantic :Event_46846a59-cdd2 .
    # :Event_46846a59-cdd2 :text "broke" .
    # :Event_46846a59-cdd2 a :HealthAndDiseaseRelated ; :confidence-HealthAndDiseaseRelated 100 .
    # :Noun_a09defce-bd6d a :ComponentPart ; :text "foot" ; :confidence 100 .
    # :Event_46846a59-cdd2 :has_affected_entity :Noun_a09defce-bd6d .
    # :Event_46846a59-cdd2 :has_active_entity :Joe .
    # :Sentence_d75bffd9-7eb1 :has_semantic :Event_1280a5de-e437 .
    # :Event_1280a5de-e437 :text "went" .
    # :Event_1280a5de-e437 a :MovementTravelAndTransportation ; :confidence-MovementTravelAndTransportation 100 .
    # :Event_1280a5de-e437 :has_active_entity :Joe .
    # :Noun_afd8f45e-96c2 a :Person ; :text "doctor" ; :confidence 100 .
    # :Event_1280a5de-e437 :has_affected_entity :Noun_afd8f45e-96c2 .


def test_xcomp():
    sentence_classes, quotation_classes = parse_narrative(text_xcomp)
    graph_results = create_graph(sentence_classes, quotation_classes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':EmotionalResponse' in ttl_str and ':text "enjoyed' in ttl_str
    assert ':has_active_entity :Mary' in ttl_str
    assert ':Person' in ttl_str and ':text "grandfather' in ttl_str
    assert (':Affiliation' in ttl_str or ':affiliated_with :Noun' in ttl_str) or \
        ':has_topic :Noun' in ttl_str
    assert ':text "being' in ttl_str
    assert ':EnvironmentAndCondition' in ttl_str or ':MeetingAndEncounter' in ttl_str
    # Output:
    # :Sentence_29b2644d-48fc a :Sentence ; :offset 1 .
    # :Sentence_29b2644d-48fc :text "Mary enjoyed being with her grandfather." .
    # :Sentence_29b2644d-48fc :mentions :Mary .
    # :Sentence_29b2644d-48fc :grade_level 3 .
    # :Sentence_29b2644d-48fc :summary "Mary enjoyed being with her grandfather." .
    # :Sentence_29b2644d-48fc :has_semantic :Event_dc5c7691-a9cc .
    # :Event_dc5c7691-a9cc :text "enjoyed" .
    # :Event_dc5c7691-a9cc a :EmotionalResponse ; :confidence-EmotionalResponse 95 .
    # :Event_dc5c7691-a9cc :has_active_entity :Mary .
    # :Noun_10adc0d3-af55 a :Person ; :text "grandfather" ; :confidence 100 .
    # :Event_dc5c7691-a9cc a :Affiliation .
    # :Event_dc5c7691-a9cc :affiliated_with :Noun_10adc0d3-af55 .
    # :Event_dc5c7691-a9cc :has_topic :Event_1e1d8d28-0053 .
    # :Sentence_29b2644d-48fc :has_semantic :Event_1e1d8d28-0053 .
    # :Event_1e1d8d28-0053 :text "being" .
    # :Event_1e1d8d28-0053 a :EnvironmentAndCondition ; :confidence-EnvironmentAndCondition 90 .
    # :Event_1e1d8d28-0053 :has_context :Mary .
    # :Event_1e1d8d28-0053 a :Affiliation .
    # :Event_1e1d8d28-0053 :affiliated_with :Noun_10adc0d3-af55 .


def test_modal():
    sentence_classes, quotation_classes = parse_narrative(text_modal)
    graph_results = create_graph(sentence_classes, quotation_classes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':ReadinessAndAbility' in ttl_str and ':MeetingAndEncounter' in ttl_str
    assert ':text "can visit' in ttl_str
    assert ':has_active_entity :Mary' in ttl_str
    assert ':Person' in ttl_str and (':text "grandfather' in ttl_str or 'grandfather"' in ttl_str)
    assert ':has_affected_entity :Noun' in ttl_str
    assert ':has_time [ a :Time ; :text "Tuesday' in ttl_str
    # Output Turtle:
    # :Sentence_5abb4f3b-be60 a :Sentence ; :offset 1 .
    # :Sentence_5abb4f3b-be60 :text "Mary can visit her grandfather on Tuesday." .
    # :Sentence_5abb4f3b-be60 :mentions :Mary .
    # :Sentence_5abb4f3b-be60 :grade_level 3 .
    # :Sentence_5abb4f3b-be60 :summary "Mary can visit her grandfather on Tuesday." .
    # :Sentence_5abb4f3b-be60 :has_semantic :Event_2c309fd6-04f8 .
    # :Event_2c309fd6-04f8 :text "can visit" .
    # :Event_2c309fd6-04f8 a :MeetingAndEncounter ; :confidence-MeetingAndEncounter 95 .
    # :Event_2c309fd6-04f8 a :ReadinessAndAbility ; :confidence-ReadinessAndAbility 95 .
    # :Event_2c309fd6-04f8 :has_active_entity :Mary .
    # :Noun_9157cf80-a903 a :Person ; :text "grandfather" ; :confidence 100 .
    # :Event_2c309fd6-04f8 :has_affected_entity :Noun_9157cf80-a903 .
    # :Event_2c309fd6-04f8 :has_time [ a :Time ; :text "Tuesday" ] .


def test_modal_neg():
    sentence_classes, quotation_classes = parse_narrative(text_modal_neg)
    graph_results = create_graph(sentence_classes, quotation_classes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert (':Avoidance' in ttl_str and ':negated true' not in ttl_str) or \
        (':MeetingAndEncounter' in ttl_str and ':negated true' in ttl_str)
    assert ':future true' in ttl_str
    assert ':has_active_entity :Mary' in ttl_str
    assert ':Person' in ttl_str and ':text "grandfather' in ttl_str
    assert ':has_affected_entity :Noun' in ttl_str
    assert ':has_time [ a :Time' in ttl_str
    # Output Turtle:
    # :Sentence_9747b06d-1ed9 a :Sentence ; :offset 1 .
    # :Sentence_9747b06d-1ed9 :text "Mary will not visit her grandfather next Tuesday." .
    # :Sentence_9747b06d-1ed9 :mentions :Mary .
    # :Sentence_9747b06d-1ed9 :grade_level 4 .
    # :Sentence_9747b06d-1ed9 :summary "Mary will not visit her grandfather next Tuesday." .
    # :Sentence_9747b06d-1ed9 :has_semantic :Event_fbcce835-7bc9 .
    # :Event_fbcce835-7bc9 :text "will not visit" .
    # :Event_fbcce835-7bc9 a :MeetingAndEncounter ; :confidence-Avoidance 95 .
    # :Event_fbcce835-7bc9 :negated true .
    # :Event_fbcce835-7bc9 :future true .
    # :Event_fbcce835-7bc9 :has_active_entity :Mary .
    # :Noun_04fb962a-2893 a :Person ; :text "Mary\'s grandfather" ; :confidence 100 .
    # :Event_fbcce835-7bc9 :has_affected_entity :Noun_04fb962a-2893 .
    # :Event_fbcce835-7bc9 :has_time [ a :Time ; :text "Tuesday" ] .


def test_acomp():
    sentence_classes, quotation_classes = parse_narrative(text_acomp)
    graph_results = create_graph(sentence_classes, quotation_classes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert 'a :EnvironmentAndCondition' in ttl_str and ':text "is' in ttl_str
    assert ':has_context :Mary' in ttl_str
    # Output Turtle:
    # :Sentence_56db981f-4899 a :Sentence ; :offset 1 .
    # :Sentence_56db981f-4899 :text "Mary is very beautiful." .
    # :Sentence_56db981f-4899 :mentions :Mary .
    # :Sentence_56db981f-4899 :grade_level 2 .
    # :Sentence_56db981f-4899 :summary "Mary is very beautiful." .
    # :Sentence_56db981f-4899 :has_semantic :Event_d1daeb17-ab96 .
    # :Event_d1daeb17-ab96 :text "is" .
    # :Event_d1daeb17-ab96 a :EnvironmentAndCondition ; :confidence-EnvironmentAndCondition 100 .
    # :Event_d1daeb17-ab96 :has_context :Mary .


def test_acomp_pcomp1():
    sentence_classes, quotation_classes = parse_narrative(text_acomp_pcomp1)
    graph_results = create_graph(sentence_classes, quotation_classes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':text "got tired' in ttl_str
    assert ':SensoryPerception' in ttl_str
    assert ':has_active_entity :Peter' in ttl_str
    assert 'a :BodilyAct' in ttl_str and ':text "running' in ttl_str
    assert ':has_topic :Event' in ttl_str    # tired of running
    # Output Turtle:
    # :Sentence_2e28e054-3322 a :Sentence ; :offset 1 .
    # :Sentence_2e28e054-3322 :text "Peter got tired of running." .
    # :Sentence_2e28e054-3322 :mentions :Peter .
    # :Sentence_2e28e054-3322 :grade_level 3 .
    # :Sentence_2e28e054-3322 :summary "Peter got tired of running." .
    # :Sentence_2e28e054-3322 :has_semantic :Event_f87fdd91-7bdf .
    # :Event_f87fdd91-7bdf :text "got tired of" .
    # :Event_f87fdd91-7bdf a :SensoryPerception ; :confidence-SensoryPerception 90 .
    # :Event_f87fdd91-7bdf :has_active_entity :Peter .
    # :Event_f87fdd91-7bdf :has_topic :Event_65eda48c-227a .
    # :Sentence_2e28e054-3322 :has_semantic :Event_65eda48c-227a .
    # :Event_65eda48c-227a :text "running" .
    # :Event_65eda48c-227a a :BodilyAct ; :confidence-BodilyAct 85 .
    # :Event_65eda48c-227a :has_active_entity :Peter .


def test_acomp_pcomp2():
    sentence_classes, quotation_classes = parse_narrative(text_acomp_pcomp2)
    graph_results = create_graph(sentence_classes, quotation_classes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':text "never tires' in ttl_str
    assert ':BodilyAct' in ttl_str and ':text "running' in ttl_str
    assert ':has_active_entity :Peter' in ttl_str
    # Output Turtle:
    # :Sentence_6a574216-cd4e a :Sentence ; :offset 1 .
    # :Sentence_6a574216-cd4e :text "Peter never tires of running." .
    # :Sentence_6a574216-cd4e :mentions :Peter .
    # :Sentence_6a574216-cd4e :grade_level 4 .
    # :Sentence_6a574216-cd4e :summary "Peter never tires of running." .
    # :Sentence_6a574216-cd4e :has_semantic :Event_e41729ab-9c4a .
    # :Event_e41729ab-9c4a :text "tires" .
    # :Event_e41729ab-9c4a a :SensoryPerception ; :confidence-SensoryPerception 100 .
    # :Event_e41729ab-9c4a :negated true .
    # :Event_e41729ab-9c4a :has_active_entity :Peter .
    # :Event_e41729ab-9c4a :has_topic :Event_5a8acb55-dcae .
    # :Sentence_6a574216-cd4e :has_semantic :Event_5a8acb55-dcae .
    # :Event_5a8acb55-dcae :text "running" .
    # :Event_5a8acb55-dcae a :BodilyAct ; :confidence-BodilyAct 100 .
    # :Event_5a8acb55-dcae :has_active_entity :Peter .


def test_acomp_xcomp():
    sentence_classes, quotation_classes = parse_narrative(text_acomp_xcomp)
    graph_results = create_graph(sentence_classes, quotation_classes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':Avoidance' in ttl_str or (':OpenMindednessAndTolerance' in ttl_str and ':negated true' in ttl_str)
    assert 'a :HealthAndDiseaseRelated ; :text "smoking' in ttl_str or 'a :BodilyAct ; :text "smoking' in ttl_str
    assert ':has_active_entity :Jane' in ttl_str
    assert ':has_topic :Noun' in ttl_str
    # Output Turtle:
    # :Sentence_c1b4ffe9-4ac2 a :Sentence ; :offset 1 .
    # :Sentence_c1b4ffe9-4ac2 :text "Jane is unable to tolerate smoking." .
    # :Sentence_c1b4ffe9-4ac2 :mentions :Jane .
    # :Sentence_c1b4ffe9-4ac2 :grade_level 5 .
    # :Sentence_c1b4ffe9-4ac2 :summary "Jane is unable to tolerate smoking." .
    # :Sentence_c1b4ffe9-4ac2 :has_semantic :Event_f676cf58-5290 .
    # :Event_f676cf58-5290 :text "is unable to tolerate" .
    # :Event_f676cf58-5290 a :OpenMindednessAndTolerance ; :confidence-OpenMindednessAndTolerance 90 .
    # :Event_f676cf58-5290 :negated true .
    # :Event_f676cf58-5290 :has_active_entity :Jane .
    # :Noun_77cb253c-1433 a :HealthAndDiseaseRelated ; :text "smoking" ; :confidence 90 .
    # :Event_f676cf58-5290 :has_topic :Noun_77cb253c-1433 .


def test_idiom():
    sentence_classes, quotation_classes = parse_narrative(text_idiom)
    graph_results = create_graph(sentence_classes, quotation_classes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':Causation' in ttl_str and ':text "caused' in ttl_str
    assert ':text "wear and tear' in ttl_str and (':Change' in ttl_str or ':TroubleAndProblem' in ttl_str)
    assert ':has_cause :Noun' in ttl_str
    assert ':Location' in ttl_str and ':text "bridge' in ttl_str
    assert ':has_location :Noun' in ttl_str
    # Cause of collapse or cause is about the bridge
    assert (':End' in ttl_str or ':Change' in ttl_str) and ':text "collapse' in ttl_str
    assert ':has_context' in ttl_str or ':has_topic' in ttl_str      # bridge's collapse
    # Output Turtle:
    # :Sentence_2550be83-76c7 a :Sentence ; :offset 1 .
    # :Sentence_2550be83-76c7 :text "Wear and tear on the bridge caused its collapse." .
    # :Sentence_2550be83-76c7 :grade_level 6 .
    # :Sentence_2550be83-76c7 :summary "Wear and tear on the bridge caused its collapse." .
    # :Sentence_2550be83-76c7 :has_semantic :Event_83fcb59b-8b3c .
    # :Event_83fcb59b-8b3c :text "caused" .
    # :Event_83fcb59b-8b3c a :Causation ; :confidence-Causation 100 .
    # :Noun_de922952-3b63 a :TroubleAndProblem, :Collection ; :text "wear and tear" ; :confidence 100 .
    # :Event_83fcb59b-8b3c :has_cause :Noun_de922952-3b63 .
    # :Noun_bdf645e6-617c a :Location ; :text "bridge" ; :confidence 100 .
    # :Event_83fcb59b-8b3c :has_location :Noun_bdf645e6-617c .
    # :Event_83fcb59b-8b3c :has_topic :Event_3ee56bf9-0b8a .
    # :Sentence_2550be83-76c7 :has_semantic :Event_3ee56bf9-0b8a .
    # :Event_3ee56bf9-0b8a :text "collapse" .
    # :Event_3ee56bf9-0b8a a :End ; :confidence-End 100 .
    # :Event_3ee56bf9-0b8a :has_topic :Noun_bdf645e6-617c .


def test_idiom_full_pass():
    sentence_classes, quotation_classes = parse_narrative(text_idiom_full_pass)
    graph_results = create_graph(sentence_classes, quotation_classes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':text "accused' in ttl_str or ':text "was accused' in ttl_str
    assert ':CommunicationAndSpeechAct' in ttl_str or ':LegalEvent' in ttl_str
    assert ':has_affected_entity :John' in ttl_str
    assert ':has_active_entity :George' in ttl_str
    assert ':has_topic :Event' in ttl_str
    assert ':AggressiveCriminalOrHostileAct' in ttl_str and ':text "breaking and entering' in ttl_str
    # Output Turtle:
    # :Sentence_b8904b67-a373 a :Sentence ; :offset 1 .
    # :Sentence_b8904b67-a373 :text "John was accused by George of breaking and entering." .
    # :Sentence_b8904b67-a373 :mentions :John .
    # :Sentence_b8904b67-a373 :mentions :George .
    # :Sentence_b8904b67-a373 :grade_level 8 .
    # :Sentence_b8904b67-a373 :summary "John accused by George of breaking and entering." .
    # :Sentence_b8904b67-a373 :has_semantic :Event_54346c9b-3fd0 .
    # :Event_54346c9b-3fd0 :text "was accused" .
    # :Event_54346c9b-3fd0 a :LegalEvent ; :confidence-LegalEvent 90 .
    # :Event_54346c9b-3fd0 :has_affected_entity :John .
    # :Event_54346c9b-3fd0 :has_active_entity :George .
    # :Event_54346c9b-3fd0 :has_topic :Event_a4b330ab-95e0 .
    # :Sentence_b8904b67-a373 :has_semantic :Event_a4b330ab-95e0 .
    # :Event_a4b330ab-95e0 :text "breaking and entering" .
    # :Event_a4b330ab-95e0 a :AggressiveCriminalOrHostileAct ; :confidence-AggressiveCriminalOrHostileAct 95 .
    # :Event_a4b330ab-95e0 :has_active_entity :John .


def test_idiom_trunc_pass():
    sentence_classes, quotation_classes = parse_narrative(text_idiom_trunc_pass)
    graph_results = create_graph(sentence_classes, quotation_classes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':text "was accused' in ttl_str
    assert ':CommunicationAndSpeechAct' in ttl_str or ':LegalEvent' in ttl_str
    assert ':has_topic :Event' in ttl_str
    assert ':AggressiveCriminalOrHostileAct' in ttl_str and ':text "breaking and entering' in ttl_str
    assert ':has_affected_entity :John' in ttl_str
    # Output Turtle:
    # :Sentence_d5d68bde-508d a :Sentence ; :offset 1 .
    # :Sentence_d5d68bde-508d :text "John was accused of breaking and entering." .
    # :Sentence_d5d68bde-508d :mentions :John .
    # :Sentence_d5d68bde-508d :grade_level 6 .
    # :Sentence_d5d68bde-508d :summary "John was accused of breaking and entering." .
    # :Sentence_d5d68bde-508d :has_semantic :Event_c0a68fa6-0ace .
    # :Event_c0a68fa6-0ace :text "was accused" .
    # :Event_c0a68fa6-0ace a :LegalEvent ; :confidence-LegalEvent 100 .
    # :Event_c0a68fa6-0ace :has_affected_entity :John .
    # :Event_c0a68fa6-0ace :has_topic :Event_b10414d9-ddba .
    # :Sentence_d5d68bde-508d :has_semantic :Event_b10414d9-ddba .
    # :Event_b10414d9-ddba :text "breaking and entering" .
    # :Event_b10414d9-ddba a :AggressiveCriminalOrHostileAct ; :confidence-AggressiveCriminalOrHostileAct 100 .
    # :Event_b10414d9-ddba :has_active_entity :John .


def test_negation_emotion():
    sentence_classes, quotation_classes = parse_narrative(text_negation_emotion)
    graph_results = create_graph(sentence_classes, quotation_classes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':text "has no liking' in ttl_str
    assert ':EmotionalResponse' in ttl_str and ':negated true' in ttl_str
    assert ':has_active_entity :Jane' in ttl_str
    assert ':Plant ; :text "broccoli' in ttl_str
    assert ':has_topic :Noun' in ttl_str
    # Output Turtle:
    # :Sentence_871800de-2dd7 a :Sentence ; :offset 1 .
    # :Sentence_871800de-2dd7 :text "Jane has no liking for broccoli." .
    # :Sentence_871800de-2dd7 :mentions :Jane .
    # :Sentence_871800de-2dd7 :grade_level 3 .
    # :Sentence_871800de-2dd7 :summary "Jane has no liking for broccoli." .
    # :Sentence_871800de-2dd7 :has_semantic :Event_74d66284-e7fe .
    # :Event_74d66284-e7fe :text "has no liking" .
    # :Event_74d66284-e7fe a :EmotionalResponse ; :confidence-EmotionalResponse 90 .
    # :Event_74d66284-e7fe :negated true .
    # :Event_74d66284-e7fe :has_active_entity :Jane .
    # :Noun_3eae795b-b1e0 a :Plant ; :text "broccoli" ; :confidence 100 .
    # :Event_74d66284-e7fe :has_topic :Noun_3eae795b-b1e0 .


def test_negation():
    sentence_classes, quotation_classes = parse_narrative(text_negation)
    graph_results = create_graph(sentence_classes, quotation_classes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':text "did not stab' in ttl_str
    assert 'a :AggressiveCriminalOrHostileAct' in ttl_str and ':negated true' in ttl_str
    assert ':has_active_entity :Jane' in ttl_str
    assert ':has_affected_entity :John' in ttl_str
    # Output Turtle:
    # :Sentence_5ca94658-7224 a :Sentence ; :offset 1 .
    # :Sentence_5ca94658-7224 :text "Jane did not stab John." .
    # :Sentence_5ca94658-7224 :mentions :Jane .
    # :Sentence_5ca94658-7224 :mentions :John .
    # :Sentence_5ca94658-7224 :grade_level 3 .
    # :Sentence_5ca94658-7224 :summary "Jane did not stab John." .
    # :Sentence_5ca94658-7224 :has_semantic :Event_4f515433-7032 .
    # :Event_4f515433-7032 :text "did not stab" .
    # :Event_4f515433-7032 a :AggressiveCriminalOrHostileAct ; :confidence-AggressiveCriminalOrHostileAct 100 .
    # :Event_4f515433-7032 :negated true .
    # :Event_4f515433-7032 :has_active_entity :Jane .
    # :Event_4f515433-7032 :has_affected_entity :John .


def test_mention():
    sentence_classes, quotation_classes = parse_narrative(text_mention)
    graph_results = create_graph(sentence_classes, quotation_classes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':mentions :FBI' in ttl_str
    assert ':text "raided' in ttl_str
    assert 'a :LawEnforcement' in ttl_str
    assert ':has_active_entity :FBI' in ttl_str
    assert 'a :Location ; :text "house' in ttl_str
    assert ':has_location :Noun' in ttl_str
    # Output Turtle:
    # :Sentence_b8e19cec-aac6 a :Sentence ; :offset 1 .
    # :Sentence_b8e19cec-aac6 :text "The FBI raided the house." .
    # :Sentence_b8e19cec-aac6 :mentions :FBI .
    # :Sentence_b8e19cec-aac6 :grade_level 6 .
    # :Sentence_b8e19cec-aac6 :summary "The FBI raided the house." .
    # :Sentence_b8e19cec-aac6 :has_semantic :Event_fa327a78-8bce .
    # :Event_fa327a78-8bce :text "raided" .
    # :Event_fa327a78-8bce a :LawEnforcement ; :confidence-LawEnforcement 100 .
    # :Event_fa327a78-8bce :has_active_entity :FBI .
    # :Noun_e98802c7-d82f a :Location ; :text "house" ; :confidence 100 .
    # :Event_fa327a78-8bce :has_location :Noun_e98802c7-d82f .
