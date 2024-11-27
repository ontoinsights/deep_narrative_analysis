import pytest
from dna.create_narrative_turtle import create_graph
from dna.nlp import parse_narrative

# Latest execution: test_acomp_xcomp failed; 1 of 20 tests

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
text_negative_emotion = 'Jane has no liking for broccoli.'
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
    assert ':BodilyAct' in ttl_str                          # exercise
    assert ':ArtAndEntertainmentEvent' in ttl_str           # practice
    assert ':EducationRelated' in ttl_str
    # Output Turtle:
    # :Sentence_f6cd8563-fe66 a :Sentence ; :offset 1 .
    # :Sentence_f6cd8563-fe66 :text "While Mary exercised, John practiced guitar." .
    # :Sentence_f6cd8563-fe66 :mentions :Mary .
    # :Sentence_f6cd8563-fe66 :mentions :John .
    # :Sentence_f6cd8563-fe66 :grade_level 5 .
    # :Sentence_f6cd8563-fe66 :has_semantic :Event_fedeb84b-4d40 .
    # :Event_fedeb84b-4d40 rdfs:label "Mary exercising" .
    # :Event_fedeb84b-4d40 a :BodilyAct ; :confidence-BodilyAct 100 .
    # :Event_fedeb84b-4d40 a :ArtAndEntertainmentEvent ; :confidence-ArtAndEntertainmentEvent 90 .
    # :Event_fedeb84b-4d40 :has_active_entity :Mary .
    # :Sentence_f6cd8563-fe66 :has_semantic :Event_2ff30880-654a .
    # :Event_2ff30880-654a rdfs:label "John practicing guitar" .
    # :Event_2ff30880-654a a :ArtAndEntertainmentEvent ; :confidence-ArtAndEntertainmentEvent 100 .
    # :Event_2ff30880-654a a :EducationRelated ; :confidence-EducationRelated 90 .
    # :Event_2ff30880-654a :has_active_entity :John .


def test_clauses2():
    sentence_classes, quotation_classes = parse_narrative(text_clauses2)
    graph_results = create_graph(sentence_classes, quotation_classes,5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':has_active_entity :George' in ttl_str
    assert ':Agreement' in ttl_str
    assert ':Process' in ttl_str and (':text "plan' in ttl_str or ':text "the plan' in ttl_str)
    assert ':CommunicationAndSpeechAct' in ttl_str or ':Cognition' in ttl_str    # outlined
    assert ':has_active_entity :Mary' in ttl_str
    assert ':has_topic :Noun'
    # Output Turtle:
    # :Sentence_ed0f4bad-f18f a :Sentence ; :offset 1 .
    # :Sentence_ed0f4bad-f18f :text "George agreed with the plan that Mary outlined." .
    # :Sentence_ed0f4bad-f18f :mentions :George .
    # :Sentence_ed0f4bad-f18f :mentions :Mary .
    # :Sentence_ed0f4bad-f18f :grade_level 6 .
    # :Sentence_ed0f4bad-f18f :has_semantic :Event_ec388f15-5f55 .
    # :Event_ec388f15-5f55 rdfs:label "Mary outlining a plan" .
    # :Event_ec388f15-5f55 a :CommunicationAndSpeechAct ; :confidence-CommunicationAndSpeechAct 100 .
    # :Event_ec388f15-5f55 a :Cognition ; :confidence-Cognition 90 .
    # :Event_ec388f15-5f55 :has_active_entity :Mary .
    # :Noun_13d06776-627c a :Process ; :text "plan" ; rdfs:label "plan; subject of outlining" ; :confidence 90 .
    # :Event_ec388f15-5f55 :has_topic :Noun_13d06776-627c .
    # :Sentence_ed0f4bad-f18f :has_semantic :Event_1cf4ca08-eff6 .
    # :Event_1cf4ca08-eff6 rdfs:label "George agreeing with the plan" .
    # :Event_1cf4ca08-eff6 a :Agreement ; :confidence-Agreement 100 .
    # :Event_1cf4ca08-eff6 :has_active_entity :George .
    # :Event_1cf4ca08-eff6 :has_topic :Noun_13d06776-627c .


def test_aux_only():
    sentence_classes, quotation_classes = parse_narrative(text_aux_only)
    graph_results = create_graph(sentence_classes, quotation_classes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':EnvironmentAndCondition' in ttl_str             # is
    assert ':has_context :Joe' in ttl_str
    assert ':LineOfBusiness ; :text "attorney' in ttl_str    # attorney
    assert ':has_aspect :Noun' in ttl_str
    # Output Turtle:
    # :Sentence_b0470a9b-f3a6 a :Sentence ; :offset 1 .
    # :Sentence_b0470a9b-f3a6 :text "Joe is an attorney." .
    # :Sentence_b0470a9b-f3a6 :mentions :Joe .
    # :Sentence_b0470a9b-f3a6 :grade_level 3 .
    # :Sentence_b0470a9b-f3a6 :has_semantic :Event_b390b12a-7b40 .
    # :Event_b390b12a-7b40 rdfs:label "Joe being an attorney" .
    # :Event_b390b12a-7b40 a :EnvironmentAndCondition ; :confidence-EnvironmentAndCondition 100 .
    # :Event_b390b12a-7b40 :has_context :Joe .
    # :Noun_73fc57b1-47d9 a :LineOfBusiness ; :text "attorney" ; rdfs:label "attorney; occupation" ; :confidence 100 .
    # :Event_b390b12a-7b40 :has_aspect :Noun_73fc57b1-47d9 .


def test_affiliation():
    sentence_classes, quotation_classes = parse_narrative(text_affiliation)
    graph_results = create_graph(sentence_classes, quotation_classes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':Affiliation' in ttl_str
    assert ':has_active_entity :Joe' in ttl_str
    assert ':has_topic :Mayberry_' in ttl_str or ':affiliated_with :Mayberry_' in ttl_str
    # Output Turtle:
    # :Sentence_5b97cd0b-9518 a :Sentence ; :offset 1 .
    # :Sentence_5b97cd0b-9518 :text "Joe is a member of the Mayberry Book Club." .
    # :Sentence_5b97cd0b-9518 :mentions :Joe .
    # :Sentence_5b97cd0b-9518 :mentions :Mayberry_Book_Club .
    # :Sentence_5b97cd0b-9518 :grade_level 4 .
    # :Sentence_5b97cd0b-9518 :has_semantic :Event_699edde2-9ff8 .
    # :Event_699edde2-9ff8 rdfs:label "Joe being a member of the Mayberry Book Club" .
    # :Event_699edde2-9ff8 :has_active_entity :Joe .
    # :Noun_c4964096-52aa a :Affiliation ; :text "member" ; rdfs:label "member; role" ; :confidence 100 .
    # :Event_699edde2-9ff8 :has_topic :Noun_c4964096-52aa .
    # :Event_699edde2-9ff8 :has_topic :Mayberry_Book_Club .


def test_complex1():
    sentence_classes, quotation_classes = parse_narrative(text_complex1)
    graph_results = create_graph(sentence_classes, quotation_classes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':mentions :Liz_Cheney' in ttl_str and ':mentions :Harriet_Hageman' in ttl_str \
        and ':mentions :Abraham_Lincoln' in ttl_str
    assert ':mentions :Trump' in ttl_str or ':mentions :Donald_Trump' in ttl_str   # Depending on previous ingests
    assert 'allusion' in ttl_str
    assert ':Cognition' in ttl_str                                       # compared
    assert ':has_active_entity :Liz_Cheney' in ttl_str
    assert ':has_affected_entity :Abraham_Lincoln' in ttl_str or ':has_topic :Abraham_Lincoln' in ttl_str
    assert ':CommunicationAndSpeechAct' in ttl_str                       # in concession speech
    assert ':Loss' in ttl_str
    assert ':has_affected_entity :Harriet_Hageman' in ttl_str                      # Cheney lost to Hageman
    # Output:
    # :Sentence_4b5e904e-3bde a :Sentence ; :offset 1 .
    # :Sentence_4b5e904e-3bde :text "Rep. Liz Cheney R-WY compared herself to former President Abraham Lincoln during
    #     her concession speech shortly after her loss to Trump-backed Republican challenger Harriet Hageman." .
    # :Sentence_4b5e904e-3bde :mentions :Liz_Cheney .
    # :Sentence_4b5e904e-3bde :mentions :Wyoming .
    # :Sentence_4b5e904e-3bde :mentions :Abraham_Lincoln .
    # :Sentence_4b5e904e-3bde :mentions :Donald_Trump .
    # :Sentence_4b5e904e-3bde :mentions :Republican .
    # :Sentence_4b5e904e-3bde :mentions :Harriet_Hageman .
    # :Sentence_4b5e904e-3bde :grade_level 10 .
    # :Sentence_4b5e904e-3bde :rhetorical_device "allusion" .
    # :Sentence_4b5e904e-3bde :rhetorical_device_allusion "The sentence uses an allusion by comparing Rep. Liz Cheney
    #     to former President Abraham Lincoln, a historical figure with symbolic meaning." .
    # :Sentence_4b5e904e-3bde :has_semantic :Event_96fe357d-6f99 .
    # :Event_96fe357d-6f99 rdfs:label "Liz Cheney\'s loss to Harriet Hageman" .
    # :Event_96fe357d-6f99 a :Loss ; :confidence-Loss 100 .
    # :Event_96fe357d-6f99 :has_active_entity :Liz_Cheney .
    # :Event_96fe357d-6f99 :has_affected_entity :Harriet_Hageman .
    # :Sentence_4b5e904e-3bde :has_semantic :Event_36ebe278-0ed2 .
    # :Event_36ebe278-0ed2 rdfs:label "Liz Cheney\'s concession speech" .
    # :Event_36ebe278-0ed2 a :CommunicationAndSpeechAct ; :confidence-CommunicationAndSpeechAct 100 .
    # :Event_36ebe278-0ed2 a :Loss ; :confidence-Loss 100 .
    # :Event_36ebe278-0ed2 :has_active_entity :Liz_Cheney .
    # :Sentence_4b5e904e-3bde :has_semantic :Event_6bc83e0e-597e .
    # :Event_6bc83e0e-597e rdfs:label "Comparing Liz Cheney to Abraham Lincoln" .
    # :Event_6bc83e0e-597e a :Cognition ; :confidence-Cognition 100 .
    # :Event_6bc83e0e-597e a :CommunicationAndSpeechAct ; :confidence-CommunicationAndSpeechAct 100 .
    # :Event_6bc83e0e-597e :has_active_entity :Liz_Cheney .
    # :Event_6bc83e0e-597e :has_affected_entity :Abraham_Lincoln .


def test_complex2():
    sentence_classes, quotation_classes = parse_narrative(text_complex2)
    graph_results = create_graph(sentence_classes, quotation_classes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert 'logos'
    assert ':Win' in ttl_str
    assert ':has_active_entity :Harriet_Hageman' in ttl_str
    assert ':Loss' in ttl_str
    assert ':has_active_entity :Liz_Cheney' in ttl_str
    assert ':Measurement' in ttl_str                     # percentages and/or votes counted
    assert ':has_topic :Noun' in ttl_str
    # Output Turtle:
    # :Sentence_66054fda-08ee a :Sentence ; :offset 1 .
    # :Sentence_66054fda-08ee :text "Harriet Hageman, a water and natural-resources attorney who was endorsed by the
    #     former president, won 66.3% of the vote to Ms. Cheney’s 28.9%, with 95% of all votes counted." .
    # :Sentence_66054fda-08ee :mentions :Harriet_Hageman .
    # :Sentence_66054fda-08ee :mentions :Liz_Cheney .
    # :Sentence_66054fda-08ee :grade_level 10 .
    # :Sentence_66054fda-08ee :rhetorical_device "logos" .
    # :Sentence_66054fda-08ee :rhetorical_device_logos "The sentence uses statistics and numbers, such as \'66.3%\',
    #     \'28.9%\', and \'95%\', to convey information about the election results, which is an example of logos." .
    # :Sentence_66054fda-08ee :has_semantic :Event_ecd9c290-6650 .
    # :Event_ecd9c290-6650 rdfs:label "Harriet Hageman winning 66.3% of the vote" .
    # :Event_ecd9c290-6650 a :Win ; :confidence-Win 100 .
    # :Event_ecd9c290-6650 :has_active_entity :Harriet_Hageman .
    # :Sentence_66054fda-08ee :has_semantic :Event_0a649eed-ff7a .
    # :Event_0a649eed-ff7a rdfs:label "Ms. Cheney receiving 28.9% of the vote" .
    # :Event_0a649eed-ff7a a :Loss ; :confidence-Loss 100 .
    # :Event_0a649eed-ff7a :has_active_entity :Liz_Cheney .
    # :Sentence_66054fda-08ee :has_semantic :Event_9c48fb82-0750 .
    # :Event_9c48fb82-0750 rdfs:label "95% of all votes being counted" .
    # :Event_9c48fb82-0750 a :End ; :confidence-Measurement 90 .
    # :Noun_a1b6be0f-33fc a :Measurement ; :text "95% of all votes" ; rdfs:label "95% of all votes; election results" ;
    #     :confidence 0 .
    # :Event_9c48fb82-0750 :has_topic :Noun_a1b6be0f-33fc .


def test_coref():
    sentence_classes, quotation_classes = parse_narrative(text_coref)
    graph_results = create_graph(sentence_classes, quotation_classes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':HealthAndDiseaseRelated' in ttl_str
    assert ':has_active_entity :Joe' in ttl_str
    assert ':ComponentPart ; :text "Joe' in ttl_str       # Joe's foot
    assert ':has_topic :Noun' in ttl_str                  # Broken foot
    assert ':MovementTravelAndTransportation' in ttl_str
    # doctor
    assert (':LineOfBusiness' in ttl_str and (':has_location :Noun' in ttl_str or ':has_topic :Noun' in ttl_str)) or \
           (':Person' in ttl_str and (':has_affected_entity :Noun' in ttl_str or ':has_topic :Noun' in ttl_str))
    # TODO: Better refine predicate for "doctor"
    # Output Turtle:
    # :Sentence_448f2281-5df0 a :Sentence ; :offset 1 .
    # :Sentence_448f2281-5df0 :text "Joe broke his foot." .
    # :Sentence_448f2281-5df0 :mentions :Joe .
    # :Sentence_448f2281-5df0 :grade_level 3 .
    # :Sentence_f54c4d82-97e9 a :Sentence ; :offset 2 .
    # :Sentence_f54c4d82-97e9 :text "He went to the doctor." .
    # :Sentence_f54c4d82-97e9 :grade_level 3 .
    # :Sentence_448f2281-5df0 :has_semantic :Event_5c0f8704-3df9 .
    # :Event_5c0f8704-3df9 rdfs:label "Joe breaking Joe\'s foot" .
    # :Event_5c0f8704-3df9 a :HealthAndDiseaseRelated ; :confidence-HealthAndDiseaseRelated 100 .
    # :Event_5c0f8704-3df9 a :Change ; :confidence-Change 80 .
    # :Event_5c0f8704-3df9 :has_active_entity :Joe .
    # :Noun_f793fffe-ef44 a :ComponentPart ; :text "Joe\'s foot" ; rdfs:label "Joe\'s foot; body part broken" ;
    #     :confidence 100 .
    # :Event_5c0f8704-3df9 :has_topic :Noun_f793fffe-ef44 .
    # :Sentence_f54c4d82-97e9 :has_semantic :Event_e135abb9-780b .
    # :Event_e135abb9-780b rdfs:label "Joe going to the doctor" .
    # :Event_e135abb9-780b a :HealthAndDiseaseRelated ; :confidence-HealthAndDiseaseRelated 90 .
    # :Event_e135abb9-780b a :MovementTravelAndTransportation ; :confidence-MovementTravelAndTransportation 100 .
    # :Event_e135abb9-780b :has_active_entity :Joe .
    # :Noun_fd35f2a9-8424 a :Person ; :text "the doctor" ; rdfs:label "the doctor; medical professional visited" ;
    #     :confidence 100 .
    # :Event_e135abb9-780b :has_affected_entity :Noun_fd35f2a9-8424 .


def test_xcomp():
    sentence_classes, quotation_classes = parse_narrative(text_xcomp)
    graph_results = create_graph(sentence_classes, quotation_classes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':EmotionalResponse' in ttl_str          # enjoyed
    assert ':MeetingAndEncounter' in ttl_str        # being with
    assert ':has_active_entity :Mary' in ttl_str
    assert ':Person' in ttl_str and (':text "Mary' in ttl_str or ':text "grandfather' in ttl_str)
    assert ':has_affected_entity :Noun' in ttl_str or ':has_topic :Noun' in ttl_str
    # Output:
    # :Sentence_83ec55b3-891c a :Sentence ; :offset 1 .
    # :Sentence_83ec55b3-891c :text "Mary enjoyed being with her grandfather." .
    # :Sentence_83ec55b3-891c :mentions :Mary .
    # :Sentence_83ec55b3-891c :grade_level 3 .
    # :Sentence_83ec55b3-891c :has_semantic :Event_b23a83a8-5608 .
    # :Event_b23a83a8-5608 rdfs:label "Mary enjoying being with her grandfather" .
    # :Event_b23a83a8-5608 a :EmotionalResponse ; :confidence-EmotionalResponse 100 .
    # :Event_b23a83a8-5608 a :MeetingAndEncounter ; :confidence-MeetingAndEncounter 90 .
    # :Event_b23a83a8-5608 :has_active_entity :Mary .
    # :Noun_96d3d62e-0b99 a :Person ; :text "Mary\'s grandfather" ; rdfs:label "Mary\'s grandfather; person being
    #     with Mary" ; :confidence 100 .
    # :Event_b23a83a8-5608 :has_affected_entity :Noun_96d3d62e-0b99 .


def test_modal():
    sentence_classes, quotation_classes = parse_narrative(text_modal)
    graph_results = create_graph(sentence_classes, quotation_classes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':OpportunityAndPossibility' in ttl_str and ':MeetingAndEncounter' in ttl_str
    assert ':has_active_entity :Mary' in ttl_str
    assert ':Person' in ttl_str and (':text "Mary' in ttl_str or ':text "grandfather' in ttl_str)
    assert ':has_affected_entity :Noun' in ttl_str
    # Output Turtle:
    # :Sentence_e9dee8cc-9175 a :Sentence ; :offset 1 .
    # :Sentence_e9dee8cc-9175 :text "Mary can visit her grandfather on Tuesday." .
    # :Sentence_e9dee8cc-9175 :mentions :Mary .
    # :Sentence_e9dee8cc-9175 :grade_level 3 .
    # :Sentence_e9dee8cc-9175 :has_semantic :Event_5e1e917a-cf57 .
    # :Event_5e1e917a-cf57 rdfs:label "Mary visiting her grandfather" .
    # :Event_5e1e917a-cf57 :future true .
    # :Event_5e1e917a-cf57 a :OpportunityAndPossibility ; :confidence-OpportunityAndPossibility 95 .
    # :Event_5e1e917a-cf57 a :MeetingAndEncounter ; :confidence-MeetingAndEncounter 100 .
    # :Event_5e1e917a-cf57 :has_active_entity :Mary .
    # :Noun_346c9749-6b04 a :Person ; :text "Mary\'s grandfather" ; rdfs:label "Mary\'s grandfather; person being
    #     visited" ; :confidence 100 .
    # :Event_5e1e917a-cf57 :has_affected_entity :Noun_346c9749-6b04 .


def test_modal_neg():
    sentence_classes, quotation_classes = parse_narrative(text_modal_neg)
    graph_results = create_graph(sentence_classes, quotation_classes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':MeetingAndEncounter' in ttl_str and ':negated-MeetingAndEncounter' in ttl_str
    assert ':future true' in ttl_str
    assert ':has_active_entity :Mary' in ttl_str
    assert ':Person' in ttl_str and (':text "grandfather' in ttl_str or ':text "Mary' in ttl_str)
    assert ':has_affected_entity :Noun' in ttl_str or ':has_topic :Noun' in ttl_str
    # Output Turtle:
    # :Sentence_5266682f-354c a :Sentence ; :offset 1 .
    # :Sentence_5266682f-354c :text "Mary will not visit her grandfather next Tuesday." .
    # :Sentence_5266682f-354c :mentions :Mary .
    # :Sentence_5266682f-354c :grade_level 5 .
    # :Sentence_5266682f-354c :has_semantic :Event_95ed0d82-4272 .
    # :Event_95ed0d82-4272 rdfs:label "Mary not visiting Mary\'s grandfather" .
    # :Event_95ed0d82-4272 :future true .
    # :Event_95ed0d82-4272 a :Avoidance ; :confidence-Avoidance 100 .
    # :Event_95ed0d82-4272 a :MeetingAndEncounter ; :confidence-MeetingAndEncounter 100 .
    # :Event_95ed0d82-4272 :negated-MeetingAndEncounter true .
    # :Event_95ed0d82-4272 :has_active_entity :Mary .
    # :Noun_4e500c9f-f22e a :Person ; :text "Mary\'s grandfather" ; rdfs:label "Mary\'s grandfather; person not
    #     being visited" ; :confidence 100 .
    # :Event_95ed0d82-4272 :has_affected_entity :Noun_4e500c9f-f22e .


def test_acomp():
    sentence_classes, quotation_classes = parse_narrative(text_acomp)
    graph_results = create_graph(sentence_classes, quotation_classes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':EnvironmentAndCondition' in ttl_str
    assert ':has_context :Mary' in ttl_str
    assert ':has_aspect' in ttl_str
    # Output Turtle:
    # :Sentence_2a139dfb-fb56 a :Sentence ; :offset 1 .
    # :Sentence_2a139dfb-fb56 :text "Mary is very beautiful." .
    # :Sentence_2a139dfb-fb56 :mentions :Mary .
    # :Sentence_2a139dfb-fb56 :grade_level 3 .
    # :Sentence_2a139dfb-fb56 :has_semantic :Event_8f62ec25-6beb .
    # :Event_8f62ec25-6beb rdfs:label "Being very beautiful" .
    # :Event_8f62ec25-6beb a :EnvironmentAndCondition ; :confidence-EnvironmentAndCondition 100 .
    # :Event_8f62ec25-6beb :has_context :Mary .
    # :Noun_a10660cd-abfe a :EnvironmentAndCondition ; :text "beautiful" ; rdfs:label "beautiful; physical
    #     appearance" ; :confidence 100 .
    # :Event_8f62ec25-6beb :has_aspect :Noun_a10660cd-abfe .


def test_acomp_pcomp1():
    sentence_classes, quotation_classes = parse_narrative(text_acomp_pcomp1)
    graph_results = create_graph(sentence_classes, quotation_classes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':SensoryPerception' in ttl_str
    assert ':has_active_entity :Peter' in ttl_str
    assert ':BodilyAct' in ttl_str
    # Output Turtle:
    # :Sentence_3bea8579-2a17 a :Sentence ; :offset 1 .
    # :Sentence_3bea8579-2a17 :text "Peter got tired of running." .
    # :Sentence_3bea8579-2a17 :mentions :Peter .
    # :Sentence_3bea8579-2a17 :grade_level 3 .
    # :Sentence_3bea8579-2a17 :has_semantic :Event_96ef225a-b48b .
    # :Event_96ef225a-b48b rdfs:label "Peter getting tired" .
    # :Event_96ef225a-b48b a :SensoryPerception ; :confidence-SensoryPerception 100 .
    # :Event_96ef225a-b48b :has_active_entity :Peter .
    # :Sentence_3bea8579-2a17 :has_semantic :Event_7e48ec12-ef6a .
    # :Event_7e48ec12-ef6a rdfs:label "running" .
    # :Event_7e48ec12-ef6a a :BodilyAct ; :confidence-BodilyAct 100 .
    # :Event_7e48ec12-ef6a a :MovementTravelAndTransportation ; :confidence-MovementTravelAndTransportation 90 .
    # :Event_7e48ec12-ef6a :has_active_entity :Peter .


def test_acomp_pcomp2():
    sentence_classes, quotation_classes = parse_narrative(text_acomp_pcomp2)
    graph_results = create_graph(sentence_classes, quotation_classes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':BodilyAct' in ttl_str and ':Continuation' in ttl_str
    assert ':has_active_entity :Peter' in ttl_str
    # Output Turtle:
    # :Sentence_22cd7346-fb57 a :Sentence ; :offset 1 .
    # :Sentence_22cd7346-fb57 :text "Peter never tires of running." .
    # :Sentence_22cd7346-fb57 :mentions :Peter .
    # :Sentence_22cd7346-fb57 :grade_level 5 .
    # :Sentence_22cd7346-fb57 :has_semantic :Event_60ce83cc-2d90 .
    # :Event_60ce83cc-2d90 rdfs:label "Peter never tiring of running" .
    # :Event_60ce83cc-2d90 a :Continuation ; :confidence-Continuation 100 .
    # :Event_60ce83cc-2d90 a :BodilyAct ; :confidence-BodilyAct 90 .     # running
    # :Event_60ce83cc-2d90 :has_active_entity :Peter .


def test_acomp_xcomp():
    sentence_classes, quotation_classes = parse_narrative(text_acomp_xcomp)
    graph_results = create_graph(sentence_classes, quotation_classes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':OpenMindednessAndTolerance' in ttl_str and ':negated-OpenMindednessAndTolerance' in ttl_str
    assert ':HealthAndDiseaseRelated ; :text "smoking' in ttl_str or ':BodilyAct ; :text "smoking' in ttl_str
    assert ':has_active_entity :Jane' in ttl_str
    assert ':has_topic :Noun' in ttl_str
    # Output Turtle:
    # :Sentence_2aefd6c8-b2a7 a :Sentence ; :offset 1 .
    # :Sentence_2aefd6c8-b2a7 :text "Jane is unable to tolerate smoking." .
    # :Sentence_2aefd6c8-b2a7 :mentions :Jane .
    # :Sentence_2aefd6c8-b2a7 :grade_level 6 .
    # :Sentence_2aefd6c8-b2a7 :has_semantic :Event_f9bb350e-ed12 .
    # :Event_f9bb350e-ed12 rdfs:label "Jane\'s inability to tolerate smoking" .
    # :Event_f9bb350e-ed12 a :OpenMindednessAndTolerance ; :confidence-OpenMindednessAndTolerance 100 .
    # :Event_f9bb350e-ed12 :negated-OpenMindednessAndTolerance true .
    # :Event_f9bb350e-ed12 a :ReadinessAndAbility ; :confidence-ReadinessAndAbility 100 .
    # :Event_f9bb350e-ed12 :negated-ReadinessAndAbility true .
    # :Event_f9bb350e-ed12 :has_active_entity :Jane .
    # :Noun_6e6e2e87-c93d a owl:Thing ; :text "smoking" ; rdfs:label "smoking; activity not tolerated" ;
    #     :confidence 80 .     # TODO: Error, smoking is not associated with health or bodily act
    # :Event_f9bb350e-ed12 :has_topic :Noun_6e6e2e87-c93d .


def test_idiom():
    sentence_classes, quotation_classes = parse_narrative(text_idiom)
    graph_results = create_graph(sentence_classes, quotation_classes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':Causation' in ttl_str
    assert ':Change' in ttl_str or ':TroubleAndProblem' in ttl_str     # wear and tear
    assert ':Location' in ttl_str and (':text "bridge' in ttl_str or ':text "the bridge' in ttl_str)
    assert ':has_location :Noun' in ttl_str or ':has_active_entity :Noun' in ttl_str      # bridge collapse
    # Output Turtle:
    # :Sentence_e24b2ae6-1750 a :Sentence ; :offset 1 .
    # :Sentence_e24b2ae6-1750 :text "Wear and tear on the bridge caused its collapse." .
    # :Sentence_e24b2ae6-1750 :grade_level 8 .
    # :Sentence_e24b2ae6-1750 :has_semantic :Event_45275f7b-473d .
    # :Event_45275f7b-473d rdfs:label "Wear and tear on the bridge" .
    # :Event_45275f7b-473d a :Change ; :confidence-Change 90 .
    # :Event_45275f7b-473d a :Causation ; :confidence-Causation 100 .
    # :Noun_f0b13d75-f374 a :Location ; :text "the bridge" ; rdfs:label "the bridge; structure experiencing wear
    #     and tear" ; :confidence 100 .
    # :Event_45275f7b-473d :has_location :Noun_f0b13d75-f374 .
    # :Sentence_e24b2ae6-1750 :has_semantic :Event_63930d05-48f1 .
    # :Event_63930d05-48f1 rdfs:label "the bridge\'s collapse" .
    # :Event_63930d05-48f1 a :Change ; :confidence-Change 90 .
    # :Event_63930d05-48f1 a :Causation ; :confidence-Causation 100 .
    # :Event_63930d05-48f1 :has_topic :Noun_f0b13d75-f374 .


def test_idiom_full_pass():
    sentence_classes, quotation_classes = parse_narrative(text_idiom_full_pass)
    graph_results = create_graph(sentence_classes, quotation_classes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':CommunicationAndSpeechAct' in ttl_str or ':LegalEvent' in ttl_str
    assert ':has_affected_entity :John' in ttl_str
    assert ':has_active_entity :George' in ttl_str
    assert ':AggressiveCriminalOrHostileAct' in ttl_str         # breaking and entering
    # Output Turtle:
    # :Sentence_3d98bd66-9689 a :Sentence ; :offset 1 .
    # :Sentence_3d98bd66-9689 :text "John was accused by George of breaking and entering." .
    # :Sentence_3d98bd66-9689 :mentions :John .
    # :Sentence_3d98bd66-9689 :mentions :George .
    # :Sentence_3d98bd66-9689 :grade_level 8 .
    # :Sentence_3d98bd66-9689 :rhetorical_device "rhetorical question or accusation" .
    # :Sentence_3d98bd66-9689 :rhetorical_device_rhetorical_question_or_accusation "The sentence makes an implicit
    #     accusation by stating that John was accused by George of breaking and entering." .
    # :Sentence_3d98bd66-9689 :has_semantic :Event_a33bf9df-06d6 .
    # :Event_a33bf9df-06d6 rdfs:label "Accusing John of breaking and entering" .
    # :Event_a33bf9df-06d6 a :CommunicationAndSpeechAct ; :confidence-CommunicationAndSpeechAct 100 .
    # :Event_a33bf9df-06d6 a :CommunicationAndSpeechAct ; :confidence-CommunicationAndSpeechAct 100 .
    # :Event_a33bf9df-06d6 :has_active_entity :George .
    # :Event_a33bf9df-06d6 :has_affected_entity :John .
    # :Noun_c1f09d2f-7af8 a :AggressiveCriminalOrHostileAct ; :text "breaking and entering" ; rdfs:label
    #     "breaking and entering; alleged crime" ; :confidence 100 .
    # :Event_a33bf9df-06d6 :has_topic :Noun_c1f09d2f-7af8 .


def test_idiom_trunc_pass():
    sentence_classes, quotation_classes = parse_narrative(text_idiom_trunc_pass)
    graph_results = create_graph(sentence_classes, quotation_classes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':CommunicationAndSpeechAct' in ttl_str or ':LegalEvent' in ttl_str
    assert ':has_affected_entity :John' in ttl_str
    assert ':AggressiveCriminalOrHostileAct' in ttl_str      # breaking and entering
    assert ':has_topic :Noun' in ttl_str
    # Output Turtle:
    # :Sentence_3e722046-502d a :Sentence ; :offset 1 .
    # :Sentence_3e722046-502d :text "John was accused of breaking and entering." .
    # :Sentence_3e722046-502d :mentions :John .
    # :Sentence_3e722046-502d :grade_level 8 .
    # :Sentence_3e722046-502d :has_semantic :Event_8b343899-0e34 .
    # :Event_8b343899-0e34 rdfs:label "Accusing John of breaking and entering" .
    # :Event_8b343899-0e34 a :CommunicationAndSpeechAct ; :confidence-CommunicationAndSpeechAct 100 .
    # :Event_8b343899-0e34 a :LegalEvent ; :confidence-LegalEvent 90 .
    # :Event_8b343899-0e34 :has_affected_entity :John .
    # :Noun_6dc7d267-4051 a :AggressiveCriminalOrHostileAct ; :text "breaking and entering" ; rdfs:label
    #     "breaking and entering; Criminal act" ; :confidence 100 .
    # :Event_8b343899-0e34 :has_topic :Noun_6dc7d267-4051 .


def test_negation_emotion():
    sentence_classes, quotation_classes = parse_narrative(text_negative_emotion)
    graph_results = create_graph(sentence_classes, quotation_classes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':EmotionalResponse' in ttl_str and (':DisagreementAndDispute' in ttl_str or
                                                ':negated-EmotionalResponse' in ttl_str)
    assert ':has_active_entity :Jane' in ttl_str
    assert ':Plant ; :text "broccoli' in ttl_str
    assert ':has_topic :Noun' in ttl_str
    # Output Turtle:
    # :Sentence_60face3d-b9ff a :Sentence ; :offset 1 .
    # :Sentence_60face3d-b9ff :text "Jane has no liking for broccoli." .
    # :Sentence_60face3d-b9ff :mentions :Jane .
    # :Sentence_60face3d-b9ff :grade_level 4 .
    # :Sentence_60face3d-b9ff :has_semantic :Event_a37247f8-31f4 .
    # :Event_a37247f8-31f4 rdfs:label "Jane\'s dislike of broccoli" .
    # :Event_a37247f8-31f4 a :DisagreementAndDispute ; :confidence-DisagreementAndDispute 100 .
    # :Event_a37247f8-31f4 a :EmotionalResponse ; :confidence-EmotionalResponse 100 .
    # :Event_a37247f8-31f4 :has_active_entity :Jane .
    # :Noun_ceca326d-8ea6 a :Plant ; :text "broccoli" ; rdfs:label "broccoli; vegetable" ; :confidence 100 .
    # :Event_a37247f8-31f4 :has_topic :Noun_ceca326d-8ea6 .


def test_negation():
    sentence_classes, quotation_classes = parse_narrative(text_negation)
    graph_results = create_graph(sentence_classes, quotation_classes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':AggressiveCriminalOrHostileAct' in ttl_str and ':negated-AggressiveCriminalOrHostileAct' in ttl_str
    assert ':has_active_entity :Jane' in ttl_str
    assert ':has_affected_entity :John' in ttl_str
    # Output Turtle:
    # :Sentence_e2f75d0d-6bb2 a :Sentence ; :offset 1 .
    # :Sentence_e2f75d0d-6bb2 :text "Jane did not stab John." .
    # :Sentence_e2f75d0d-6bb2 :mentions :Jane .
    # :Sentence_e2f75d0d-6bb2 :mentions :John .
    # :Sentence_e2f75d0d-6bb2 :grade_level 5 .
    # :Sentence_e2f75d0d-6bb2 :has_semantic :Event_b2e8b986-777d .
    # :Event_b2e8b986-777d rdfs:label "Jane not stabbing John" .
    # :Event_b2e8b986-777d a :AggressiveCriminalOrHostileAct ; :confidence-AggressiveCriminalOrHostileAct 100 .
    # :Event_b2e8b986-777d :negated-AggressiveCriminalOrHostileAct true .
    # :Event_b2e8b986-777d :has_active_entity :Jane .
    # :Event_b2e8b986-777d :has_affected_entity :John .


def test_mention():
    sentence_classes, quotation_classes = parse_narrative(text_mention)
    graph_results = create_graph(sentence_classes, quotation_classes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':mentions :FBI' in ttl_str
    assert ':LawEnforcement' in ttl_str
    assert ':has_active_entity :FBI' in ttl_str
    assert ':Location ; :text "house' in ttl_str
    assert ':has_location :Noun' in ttl_str
    # Output Turtle:
    # :Sentence_07943b8d-ed40 a :Sentence ; :offset 1 .
    # :Sentence_07943b8d-ed40 :text "The FBI raided the house." .
    # :Sentence_07943b8d-ed40 :mentions :FBI .
    # :Sentence_07943b8d-ed40 :grade_level 6 .
    # :Sentence_07943b8d-ed40 :has_semantic :Event_893b0067-b901 .
    # :Event_893b0067-b901 rdfs:label "Raiding the house" .
    # :Event_893b0067-b901 a :AcquisitionPossessionAndTransfer ; :confidence-AcquisitionPossessionAndTransfer 90 .
    # :Event_893b0067-b901 a :LawEnforcement ; :confidence-LawEnforcement 100 .
    # :Event_893b0067-b901 :has_active_entity :FBI .
    # :Noun_4763dc6f-0759 a :Location ; :text "house" ; rdfs:label "house; residential building" ; :confidence 100 .
    # :Event_893b0067-b901 :has_location :Noun_4763dc6f-0759 .
