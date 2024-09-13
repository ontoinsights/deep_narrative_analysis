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
text_acomp_pcomp = 'Peter got tired of running.'
text_neg_acomp_pcomp = 'Peter never tires of running.'
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
    parse_results = parse_narrative(text_clauses1)
    graph_results = create_graph(parse_results.sentence_classes, parse_results.quotation_classes,
                                 parse_results.partial_quotes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':has_active_entity :Mary' in ttl_str
    assert ':has_active_entity :John' in ttl_str
    assert 'a :BodilyAct' in ttl_str and ':text "exercised' in ttl_str
    assert (':ArtAndEntertainmentEvent' in ttl_str or ':EducationRelated' in ttl_str) and ':text "practiced' in ttl_str
    assert 'a :MusicalInstrument ; :text "guitar' in ttl_str
    assert ':has_instrument :Noun' in ttl_str or ':has_context :Noun' in ttl_str
    # Output Turtle:
    # :Sentence_5897d614-07c0 a :Sentence ; :offset 1 .
    # :Sentence_5897d614-07c0 :text "While Mary exercised, John practiced guitar." .
    # :Sentence_5897d614-07c0 :mentions :Mary .
    # :Sentence_5897d614-07c0 :mentions :John .
    # :Sentence_5897d614-07c0 :grade_level 5 .
    # :Sentence_5897d614-07c0 :summary "Mary exercised while John practiced guitar." .
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
    parse_results = parse_narrative(text_clauses2)
    graph_results = create_graph(parse_results.sentence_classes, parse_results.quotation_classes,
                                 parse_results.partial_quotes, 5, repo)
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
    # :Sentence_78b356ac-9a45 :summary "George agreed with Mary\'s outlined plan." .
    # :Sentence_78b356ac-9a45 :has_semantic :Event_9fc158b5-353c .
    # :Event_9fc158b5-353c :text "agreed" .
    # :Event_9fc158b5-353c a :Agreement ; :confidence-Agreement 100 .
    # :Event_9fc158b5-353c :has_active_entity :George .
    # :Noun_12ccd540-84da a :Process ; :text "plan" ; :confidence 90 .
    # :Event_9fc158b5-353c :has_context :Noun_12ccd540-84da .
    # :Sentence_78b356ac-9a45 :has_semantic :Event_44fd0030-bdd5 .
    # :Event_44fd0030-bdd5 :text "outlined" .
    # :Event_44fd0030-bdd5 a :CommunicationAndSpeechAct ; :confidence-CommunicationAndSpeechAct 90 .
    # :Event_44fd0030-bdd5 :has_active_entity :Mary .
    # :Event_44fd0030-bdd5 :has_topic :Noun_12ccd540-84da .


def test_aux_only():
    parse_results = parse_narrative(text_aux_only)
    graph_results = create_graph(parse_results.sentence_classes, parse_results.quotation_classes,
                                 parse_results.partial_quotes, 5, repo)
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
    # :Sentence_7b634962-247f :summary "Joe works as an attorney." .
    # :Sentence_7b634962-247f :has_semantic :Event_770b98fd-32ee .
    # :Event_770b98fd-32ee :text "is" .
    # :Event_770b98fd-32ee a :EnvironmentAndCondition ; :confidence-EnvironmentAndCondition 100 .
    # :Event_770b98fd-32ee :has_context :Joe .      # Whose/what condition is described
    # :Noun_c98bfda5-73d9 a :LineOfBusiness ; :text "attorney" ; :confidence 100 .
    # :Event_770b98fd-32ee :has_aspect :Noun_c98bfda5-73d9 .


def test_affiliation():
    parse_results = parse_narrative(text_affiliation)
    graph_results = create_graph(parse_results.sentence_classes, parse_results.quotation_classes,
                                 parse_results.partial_quotes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':Affiliation' in ttl_str
    assert ':has_active_entity :Joe' in ttl_str or ':has_context :Joe' in ttl_str or ':affiliated_with :Joe' in ttl_str
    assert ':affiliated_with :Mayberry_' in ttl_str
    # Output Turtle:
    # :Sentence_4d5aabcf-5a7f a :Sentence ; :offset 1 .
    # :Sentence_4d5aabcf-5a7f :text "Joe is a member of the Mayberry Book Club." .
    # :Sentence_4d5aabcf-5a7f :mentions :Joe .
    # :Sentence_4d5aabcf-5a7f :mentions :Mayberry_Book_Club .
    # :Sentence_4d5aabcf-5a7f :grade_level 3 .
    # :Sentence_4d5aabcf-5a7f :summary "Joe is a Mayberry Book Club member." .
    # :Sentence_4d5aabcf-5a7f :has_semantic :Event_7a846a70-5b93 .
    # :Event_7a846a70-5b93 :text "is" .
    # :Event_7a846a70-5b93 a :Affiliation ; :confidence-Affiliation 95 .
    # :Event_7a846a70-5b93 :affiliated_with :Joe .
    # :Event_7a846a70-5b93 :affiliated_with :Mayberry_Book_Club .


def test_complex1():
    parse_results = parse_narrative(text_complex1)
    graph_results = create_graph(parse_results.sentence_classes, parse_results.quotation_classes,
                                 parse_results.partial_quotes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':mentions :Liz_Cheney' in ttl_str and ':mentions :Harriet_Hageman' in ttl_str
    assert ':mentions :Abraham_Lincoln' in ttl_str
    assert ':mentions :Donald_Trump' in ttl_str
    assert 'allusion' in ttl_str
    assert ':Cognition' in ttl_str and ':text "compared' in ttl_str
    assert ':has_active_entity :Liz_Cheney' in ttl_str        # Cheney compared herself
    assert ':has_topic :Abraham_Lincoln' in ttl_str           # to Lincoln
    assert ':Loss' in ttl_str and ':text "loss' in ttl_str    # Cheney loss to Hageman
    assert ':has_cause :Harriet_Hageman' in ttl_str
    # Output:
    # :Sentence_b876e7b0-0e7c a :Sentence ; :offset 1 .
    # :Sentence_b876e7b0-0e7c :text "Rep. Liz Cheney R-WY compared herself to former President Abraham Lincoln during
    #     her concession speech shortly after her loss to Trump-backed Republican challenger Harriet Hageman." .
    # :Sentence_b876e7b0-0e7c :mentions :Liz_Cheney .
    # :Sentence_b876e7b0-0e7c :mentions :Wyoming .
    # :Sentence_b876e7b0-0e7c :mentions :Abraham_Lincoln .
    # :Sentence_b876e7b0-0e7c :mentions :Donald_Trump .
    # :Sentence_b876e7b0-0e7c :mentions :Republican .
    # :Sentence_b876e7b0-0e7c :mentions :Harriet_Hageman .
    # :Sentence_b876e7b0-0e7c :grade_level 10 .
    # :Sentence_b876e7b0-0e7c :rhetorical_device "allusion" .
    # :Sentence_b876e7b0-0e7c :rhetorical_device_allusion "The sentence contains an allusion, as it references former
    #     President Abraham Lincoln, a historical figure with symbolic meaning, to draw a comparison with Rep.
    #     Liz Cheney." .
    # :Sentence_b876e7b0-0e7c :summary "Liz Cheney compared herself to Abraham Lincoln after her loss." .
    # :Sentence_b876e7b0-0e7c :has_semantic :Event_19302aa5-6b9d .
    # :Event_19302aa5-6b9d :text "compared" .
    # :Event_19302aa5-6b9d a :Cognition ; :confidence-Cognition 95 .
    # :Event_19302aa5-6b9d :has_active_entity :Liz_Cheney .
    # :Event_19302aa5-6b9d :has_topic :Liz_Cheney .
    # :Event_19302aa5-6b9d :has_topic :Abraham_Lincoln .
    # :Sentence_b876e7b0-0e7c :has_semantic :Event_e3bb4b13-02af .
    # :Event_e3bb4b13-02af :text "loss" .
    # :Event_e3bb4b13-02af a :Loss ; :confidence-Loss 100 .
    # :Event_e3bb4b13-02af :has_active_entity :Liz_Cheney .
    # :Event_e3bb4b13-02af :has_cause :Harriet_Hageman .


def test_complex2():
    parse_results = parse_narrative(text_complex2)
    graph_results = create_graph(parse_results.sentence_classes, parse_results.quotation_classes,
                                 parse_results.partial_quotes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert 'logos'
    assert 'a :Win' in ttl_str and ':text "won' in ttl_str
    assert ':has_active_entity :Harriet_Hageman' in ttl_str
    assert ':Measurement' in ttl_str and (':text "66.3%' in ttl_str or ':text "counted' in ttl_str or
                                          ':text "vote' in ttl_str)
    if ':text "66.3%' in ttl_str:
        assert ':has_quantification :Noun' in ttl_str
    assert (':Affiliation' in ttl_str or ':PoliticalEvent' in ttl_str) and (':text "was endorsed' in ttl_str
                                                                            or ':text "endorsed' in ttl_str)
    assert ':text "president' in ttl_str or ':text "former president' in ttl_str
    assert ':has_active_entity :Noun' in ttl_str
    assert ':affiliated_with :Harriet_Hageman' in ttl_str or ':has_recipient :Harriet_Hageman' in ttl_str
    # Output Turtle:
    # :Sentence_e7b09bb5-756c a :Sentence ; :offset 1 .
    # :Sentence_e7b09bb5-756c :text "Harriet Hageman, a water and natural-resources attorney who was endorsed by the
    #     former president, won 66.3% of the vote to Ms. Cheney’s 28.9%, with 95% of all votes counted." .
    # :Sentence_e7b09bb5-756c :mentions :Harriet_Hageman .
    # :Sentence_e7b09bb5-756c :mentions :Liz_Cheney .
    # :Sentence_e7b09bb5-756c :grade_level 10 .
    # :Sentence_e7b09bb5-756c :rhetorical_device "logos" .
    # :Sentence_e7b09bb5-756c :rhetorical_device_logos "The sentence uses statistics and numbers to convey the
    #     election results, specifically the percentages of votes won by Harriet Hageman and Ms. Cheney, as well as
    #     the percentage of votes counted." .
    # :Sentence_e7b09bb5-756c :summary "Harriet Hageman won against Ms. Cheney in the election." .
    # :Sentence_e7b09bb5-756c :has_semantic :Event_f05dec0e-baa4 .
    # :Event_f05dec0e-baa4 :text "won" .
    # :Event_f05dec0e-baa4 a :Win ; :confidence-Win 100 .
    # :Event_f05dec0e-baa4 :has_active_entity :Harriet_Hageman .
    # :Noun_b75ffb11-4f6c a :Measurement ; :text "66.3%" ; :confidence 100 .
    # :Event_f05dec0e-baa4 :has_quantification :Noun_b75ffb11-4f6c .
    # :Noun_b38cb0a0-f4af a :PoliticalEvent ; :text "vote" ; :confidence 100 .
    # :Event_f05dec0e-baa4 :has_topic :Noun_b38cb0a0-f4af .
    # :Sentence_e7b09bb5-756c :has_semantic :Event_d40d7ab4-d183 .
    # :Event_d40d7ab4-d183 :text "endorsed" .
    # :Event_d40d7ab4-d183 a :PoliticalEvent ; :confidence-PoliticalEvent 90 .
    # :Noun_eea12f59-4059 a :Person ; :text "former president" ; :confidence 100 .
    # :Event_d40d7ab4-d183 :has_active_entity :Noun_eea12f59-4059 .
    # :Event_d40d7ab4-d183 :has_recipient :Harriet_Hageman .
    # :Sentence_e7b09bb5-756c :has_semantic :Event_430b21d8-3e73 .
    # :Event_430b21d8-3e73 :text "counted" .
    # :Event_430b21d8-3e73 a :Measurement ; :confidence-Measurement 95 .
    # :Event_430b21d8-3e73 :text "votes" .


def test_coref():
    parse_results = parse_narrative(text_coref)
    graph_results = create_graph(parse_results.sentence_classes, parse_results.quotation_classes,
                                 parse_results.partial_quotes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':HealthAndDiseaseRelated' in ttl_str and ':text "broke' in ttl_str
    assert ':MovementTravelAndTransportation' in ttl_str and ':text "went' in ttl_str
    assert ':ComponentPart' in ttl_str and (':text "foot' in ttl_str or 'foot"' in ttl_str)
    assert ':has_context :Noun' in ttl_str or ':has_topic :Noun' in ttl_str       # Broke his foot
    assert ':has_active_entity :Joe' in ttl_str
    assert 'a :LineOfBusiness' in ttl_str and \
           (':has_destination :Noun' in ttl_str or ':has_location :Noun' in ttl_str) and ':text "doctor' in ttl_str
    # Output Turtle:
    # :Sentence_949d9ef6-e837 a :Sentence ; :offset 1 .
    # :Sentence_949d9ef6-e837 :text "Joe broke his foot." .
    # :Sentence_949d9ef6-e837 :mentions :Joe .
    # :Sentence_949d9ef6-e837 :grade_level 3 .
    # :Sentence_4cfcb6f7-77f6 a :Sentence ; :offset 2 .
    # :Sentence_4cfcb6f7-77f6 :text "He went to the doctor." .
    # :Sentence_4cfcb6f7-77f6 :grade_level 1 .
    # :Sentence_949d9ef6-e837 :summary "Joe injured his foot." .
    # :Sentence_949d9ef6-e837 :has_semantic :Event_64b2c214-c719 .
    # :Event_64b2c214-c719 :text "broke" .
    # :Event_64b2c214-c719 a :HealthAndDiseaseRelated ; :confidence-HealthAndDiseaseRelated 95 .
    # :Event_64b2c214-c719 :has_active_entity :Joe .
    # :Noun_2227bc20-3b58 a :ComponentPart ; :text "Joe\'s foot" ; :confidence 100 .
    # :Event_64b2c214-c719 :has_context :Noun_2227bc20-3b58 .
    # :Sentence_4cfcb6f7-77f6 :summary "Joe visited a doctor." .
    # :Sentence_4cfcb6f7-77f6 :has_semantic :Event_51748ba3-e4c6 .
    # :Event_51748ba3-e4c6 :text "went" .
    # :Event_51748ba3-e4c6 a :MovementTravelAndTransportation ; :confidence-MovementTravelAndTransportation 90 .
    # :Event_51748ba3-e4c6 :has_active_entity :Joe .
    # :Noun_849795f5-e169 a :LineOfBusiness ; :text "doctor" ; :confidence 90 .
    # :Event_51748ba3-e4c6 :has_destination :Noun_849795f5-e169 .


def test_xcomp():
    parse_results = parse_narrative(text_xcomp)
    graph_results = create_graph(parse_results.sentence_classes, parse_results.quotation_classes,
                                 parse_results.partial_quotes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':EmotionalResponse' in ttl_str and ':text "enjoyed' in ttl_str
    assert ':has_active_entity :Mary' in ttl_str
    assert ':Person' in ttl_str and (':text "grandfather' in ttl_str or 'grandfather"' in ttl_str)
    assert ':has_context :Noun' in ttl_str or ':affiliated_with :Noun' in ttl_str or \
           ':has_affected_entity :Noun' in ttl_str
    assert ':text "being' in ttl_str
    assert ':EnvironmentAndCondition' in ttl_str or ':MeetingAndEncounter' in ttl_str
    # Output:
    # :Sentence_fda11d2b-27ff a :Sentence ; :offset 1 .
    # :Sentence_fda11d2b-27ff :text "Mary enjoyed being with her grandfather." .
    # :Sentence_fda11d2b-27ff :mentions :Mary .
    # :Sentence_fda11d2b-27ff :grade_level 3 .
    # :Sentence_fda11d2b-27ff :summary "Mary enjoyed spending time with her grandfather." .
    # :Sentence_fda11d2b-27ff :has_semantic :Event_44ad7685-7ddb .
    # :Event_44ad7685-7ddb :text "enjoyed" .
    # :Event_44ad7685-7ddb a :EmotionalResponse ; :confidence-EmotionalResponse 95 .
    # :Event_44ad7685-7ddb :has_active_entity :Mary .
    # :Noun_d6a451f6-f850 a :Person ; :text "grandfather" ; :confidence 100 .
    # :Event_44ad7685-7ddb a :Affiliation .
    # :Event_44ad7685-7ddb :affiliated_with :Noun_d6a451f6-f850 .
    # :Event_44ad7685-7ddb :has_topic :Event_a2aa6c99-7b35 .
    # :Sentence_fda11d2b-27ff :has_semantic :Event_a2aa6c99-7b35 .
    # :Event_a2aa6c99-7b35 :text "being" .
    # :Event_a2aa6c99-7b35 a :MeetingAndEncounter ; :confidence-MeetingAndEncounter 90 .
    # :Event_a2aa6c99-7b35 :has_active_entity :Mary .
    # :Event_a2aa6c99-7b35 a :Affiliation .
    # :Event_a2aa6c99-7b35 :affiliated_with :Noun_d6a451f6-f850 .


def test_modal():
    parse_results = parse_narrative(text_modal)
    graph_results = create_graph(parse_results.sentence_classes, parse_results.quotation_classes,
                                 parse_results.partial_quotes, 5, repo)
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
    parse_results = parse_narrative(text_modal_neg)
    graph_results = create_graph(parse_results.sentence_classes, parse_results.quotation_classes,
                                 parse_results.partial_quotes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':Avoidance' in ttl_str and ':negated true' not in ttl_str
    assert ':future true' in ttl_str
    assert ':has_active_entity :Mary' in ttl_str
    assert ':Person' in ttl_str and (':text "grandfather' in ttl_str or 'grandfather"' in ttl_str)
    assert ':has_affected_entity :Noun' in ttl_str
    assert ':has_time [ a :Time ; :text "next Tuesday' in ttl_str
    # Output Turtle:
    # :Sentence_9747b06d-1ed9 a :Sentence ; :offset 1 .
    # :Sentence_9747b06d-1ed9 :text "Mary will not visit her grandfather next Tuesday." .
    # :Sentence_9747b06d-1ed9 :mentions :Mary .
    # :Sentence_9747b06d-1ed9 :grade_level 4 .
    # :Sentence_9747b06d-1ed9 :summary "Mary will not visit her grandfather next Tuesday." .
    # :Sentence_9747b06d-1ed9 :has_semantic :Event_fbcce835-7bc9 .
    # :Event_fbcce835-7bc9 :text "will not visit" .
    # :Event_fbcce835-7bc9 a :Avoidance ; :confidence-Avoidance 95 .
    # :Event_fbcce835-7bc9 :future true .
    # :Event_fbcce835-7bc9 :has_active_entity :Mary .
    # :Noun_04fb962a-2893 a :Person ; :text "Mary\'s grandfather" ; :confidence 100 .
    # :Event_fbcce835-7bc9 :has_affected_entity :Noun_04fb962a-2893 .
    # :Event_fbcce835-7bc9 :has_time [ a :Time ; :text "next Tuesday" ] .


def test_acomp():
    parse_results = parse_narrative(text_acomp)
    graph_results = create_graph(parse_results.sentence_classes, parse_results.quotation_classes,
                                 parse_results.partial_quotes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert 'a :EnvironmentAndCondition' in ttl_str and ':text "is' in ttl_str
    assert ':has_context :Mary' in ttl_str
    # Intermittently includes ':text "beautiful' and ':has_aspect :Noun' in ttl_str
    # Output Turtle:
    # :Sentence_56db981f-4899 a :Sentence ; :offset 1 .
    # :Sentence_56db981f-4899 :text "Mary is very beautiful." .
    # :Sentence_56db981f-4899 :mentions :Mary .
    # :Sentence_56db981f-4899 :grade_level 2 .
    # :Sentence_56db981f-4899 :summary "Mary is described as very beautiful." .
    # :Sentence_56db981f-4899 :has_semantic :Event_d1daeb17-ab96 .
    # :Event_d1daeb17-ab96 :text "is" .
    # :Event_d1daeb17-ab96 a :EnvironmentAndCondition ; :confidence-EnvironmentAndCondition 100 .
    # :Event_d1daeb17-ab96 :has_context :Mary .


def test_acomp_pcomp():
    parse_results = parse_narrative(text_acomp_pcomp)
    graph_results = create_graph(parse_results.sentence_classes, parse_results.quotation_classes,
                                 parse_results.partial_quotes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':text "got tired' in ttl_str
    assert ':SensoryPerception' in ttl_str
    assert ':has_active_entity :Peter' in ttl_str
    assert 'a :BodilyAct' in ttl_str and ':text "running' in ttl_str
    assert ':has_topic :Event' in ttl_str    # tired of running
    # Output Turtle:
    # :Sentence_c363cb50-14e0 a :Sentence ; :offset 1 .
    # :Sentence_c363cb50-14e0 :text "Peter got tired of running." .
    # :Sentence_c363cb50-14e0 :mentions :Peter .
    # :Sentence_c363cb50-14e0 :grade_level 3 .
    # :Sentence_c363cb50-14e0 :summary "Peter stopped running due to fatigue." .
    # :Sentence_c363cb50-14e0 :has_semantic :Event_b148d04c-0479 .
    # :Event_b148d04c-0479 :text "got tired" .
    # :Event_b148d04c-0479 a :SensoryPerception ; :confidence-SensoryPerception 95 .
    # :Event_b148d04c-0479 :has_active_entity :Peter .
    # :Event_b148d04c-0479 :has_topic :Event_2a7ac249-1475 .
    # :Sentence_c363cb50-14e0 :has_semantic :Event_2a7ac249-1475 .
    # :Event_2a7ac249-1475 :text "running" .
    # :Event_2a7ac249-1475 a :BodilyAct ; :confidence-BodilyAct 90 .
    # :Event_2a7ac249-1475 :has_active_entity :Peter .


def test_neg_acomp_pcomp():
    parse_results = parse_narrative(text_neg_acomp_pcomp)
    graph_results = create_graph(parse_results.sentence_classes, parse_results.quotation_classes,
                                 parse_results.partial_quotes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':text "never tires' in ttl_str
    assert ':SensoryPerception' in ttl_str
    # assert ':negated true' in ttl_str   # TODO: Never gets the sensation? Is this correct?
    assert ':BodilyAct' in ttl_str and ':text "running' in ttl_str
    assert ':has_active_entity :Peter' in ttl_str
    # Output Turtle:
    # :Sentence_fd160b2e-7b6d a :Sentence ; :offset 1 .
    # :Sentence_fd160b2e-7b6d :text "Peter never tires of running." .
    # :Sentence_fd160b2e-7b6d :mentions :Peter .
    # :Sentence_fd160b2e-7b6d :grade_level 4 .
    # :Sentence_fd160b2e-7b6d :summary "Peter enjoys running without getting tired." .
    # :Sentence_fd160b2e-7b6d :has_semantic :Event_127c103d-e147 .
    # :Event_127c103d-e147 :text "tires" .
    # :Event_127c103d-e147 a :SensoryPerception ; :confidence-SensoryPerception 90 .
    # :Event_127c103d-e147 :negated true .
    # :Event_127c103d-e147 :has_active_entity :Peter .
    # :Event_127c103d-e147 :has_topic :Event_8ea71fe8-7b3f .
    # :Sentence_fd160b2e-7b6d :has_semantic :Event_8ea71fe8-7b3f .
    # :Event_8ea71fe8-7b3f :text "running" .
    # :Event_8ea71fe8-7b3f a :BodilyAct ; :confidence-BodilyAct 100 .
    # :Event_8ea71fe8-7b3f :has_active_entity :Peter .


def test_acomp_xcomp():
    parse_results = parse_narrative(text_acomp_xcomp)
    graph_results = create_graph(parse_results.sentence_classes, parse_results.quotation_classes,
                                 parse_results.partial_quotes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':Avoidance' in ttl_str or (':OpenMindednessAndTolerance' in ttl_str and ':negated true' in ttl_str)
    assert 'a :HealthAndDiseaseRelated ; :text "smoking' in ttl_str or 'a :BodilyAct ; :text "smoking' in ttl_str
    assert ':has_active_entity :Jane' in ttl_str
    assert ':has_topic :Noun' in ttl_str
    # Output Turtle:
    # :Sentence_b121c0ba-ad5a a :Sentence ; :offset 1 .
    # :Sentence_b121c0ba-ad5a :text "Jane is unable to tolerate smoking." .
    # :Sentence_b121c0ba-ad5a :mentions :Jane .
    # :Sentence_b121c0ba-ad5a :grade_level 5 .
    # :Sentence_b121c0ba-ad5a :summary "Jane cannot tolerate smoking." .
    # :Sentence_b121c0ba-ad5a :has_semantic :Event_e04ff606-3c48 .
    # :Event_e04ff606-3c48 :text "is unable to tolerate" .
    # :Event_e04ff606-3c48 a :OpenMindednessAndTolerance ; :confidence-OpenMindednessAndTolerance 90 .
    # :Event_e04ff606-3c48 :negated true .
    # :Event_e04ff606-3c48 :has_active_entity :Jane .
    # :Noun_f0bd5be4-7ddf a :HealthAndDiseaseRelated ; :text "smoking" ; :confidence 90 .
    # :Event_e04ff606-3c48 :has_topic :Noun_f0bd5be4-7ddf .


def test_idiom():
    parse_results = parse_narrative(text_idiom)
    graph_results = create_graph(parse_results.sentence_classes, parse_results.quotation_classes,
                                 parse_results.partial_quotes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':Causation' in ttl_str and ':text "caused' in ttl_str
    assert ':Change ; :text "Wear and tear' in ttl_str or ':TroubleAndProblem ; :text "Wear and tear' in ttl_str
    assert ':has_cause :Noun' in ttl_str
    assert ':Location' in ttl_str and ':text "bridge' in ttl_str
    assert ':has_location :Noun' in ttl_str
    # Cause of collapse or cause is about the bridge
    assert (':End' in ttl_str or ':Change' in ttl_str) and ':text "collapse' in ttl_str
    assert ':has_context' in ttl_str or ':has_topic' in ttl_str      # bridge's collapse
    # Output Turtle:
    # :Sentence_3e666bbe-c2c1 a :Sentence ; :offset 1 .
    # :Sentence_3e666bbe-c2c1 :text "Wear and tear on the bridge caused its collapse." .
    # :Sentence_3e666bbe-c2c1 :grade_level 8 .
    # :Sentence_3e666bbe-c2c1 :summary "Bridge collapsed due to wear and tear." .
    # :Sentence_3e666bbe-c2c1 :has_semantic :Event_a057e700-0991 .
    # :Event_a057e700-0991 :text "caused" .
    # :Event_a057e700-0991 a :Causation ; :confidence-Causation 95 .
    # :Noun_76e1a8fd-9ede a :TroubleAndProblem ; :text "Wear and tear" ; :confidence 90 .
    # :Event_a057e700-0991 :has_cause :Noun_76e1a8fd-9ede .
    # :Noun_9a783023-e41f a :Location ; :text "bridge" ; :confidence 95 .
    # :Event_a057e700-0991 :has_location :Noun_9a783023-e41f .
    # :Event_a057e700-0991 :has_topic :Event_b89150ae-246a .
    # :Sentence_3e666bbe-c2c1 :has_semantic :Event_b89150ae-246a .
    # :Event_b89150ae-246a :text "collapse" .
    # :Event_b89150ae-246a a :End ; :confidence-End 90 .
    # :Event_b89150ae-246a :has_topic :Noun_9a783023-e41f .


def test_idiom_full_pass():
    parse_results = parse_narrative(text_idiom_full_pass)
    graph_results = create_graph(parse_results.sentence_classes, parse_results.quotation_classes,
                                 parse_results.partial_quotes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':text "accused' in ttl_str or ':text "was accused' in ttl_str
    assert ':CommunicationAndSpeechAct' in ttl_str or ':LegalEvent' in ttl_str
    assert ':has_affected_entity :John' in ttl_str
    assert ':has_active_entity :George' in ttl_str
    assert ':has_topic :Event' in ttl_str
    assert ':AggressiveCriminalOrHostileAct' in ttl_str and ':text "breaking and entering' in ttl_str
    assert ':has_active_entity :John' in ttl_str
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
    parse_results = parse_narrative(text_idiom_trunc_pass)
    graph_results = create_graph(parse_results.sentence_classes, parse_results.quotation_classes,
                                 parse_results.partial_quotes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':text "was accused' in ttl_str
    assert ':CommunicationAndSpeechAct' in ttl_str or ':LegalEvent' in ttl_str
    assert ':has_topic :Event' in ttl_str
    assert ':AggressiveCriminalOrHostileAct' in ttl_str and ':text "breaking and entering' in ttl_str
    assert ':has_affected_entity :John' in ttl_str
    assert ':has_active_entity :John' in ttl_str
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
    parse_results = parse_narrative(text_negation_emotion)
    graph_results = create_graph(parse_results.sentence_classes, parse_results.quotation_classes,
                                 parse_results.partial_quotes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':text "has no liking' in ttl_str
    assert ':EmotionalResponse' in ttl_str and ':negated true' not in ttl_str
    assert ':has_active_entity :Jane' in ttl_str
    assert ':Plant ; :text "broccoli' in ttl_str
    assert ':has_topic :Noun' in ttl_str
    # Output Turtle:
    # :Sentence_9dc61b51-f292 a :Sentence ; :offset 1 .
    # :Sentence_9dc61b51-f292 :text "Jane has no liking for broccoli." .
    # :Sentence_9dc61b51-f292 :mentions :Jane .
    # :Sentence_9dc61b51-f292 :grade_level 3 .
    # :Sentence_9dc61b51-f292 :summary "Jane dislikes broccoli." .
    # :Sentence_9dc61b51-f292 :has_semantic :Event_10e42ffd-5ec9 .
    # :Event_10e42ffd-5ec9 :text "has no liking" .
    # :Event_10e42ffd-5ec9 a :EmotionalResponse ; :confidence-EmotionalResponse 95 .
    # :Event_10e42ffd-5ec9 :has_active_entity :Jane .
    # :Noun_9bcfec49-8672 a :Plant ; :text "broccoli" ; :confidence 100 .
    # :Event_10e42ffd-5ec9 :has_topic :Noun_9bcfec49-8672 .


def test_negation():
    parse_results = parse_narrative(text_negation)
    graph_results = create_graph(parse_results.sentence_classes, parse_results.quotation_classes,
                                 parse_results.partial_quotes, 5, repo)
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
    parse_results = parse_narrative(text_mention)
    graph_results = create_graph(parse_results.sentence_classes, parse_results.quotation_classes,
                                 parse_results.partial_quotes, 5, repo)
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
