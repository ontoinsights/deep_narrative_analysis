import pytest
from dna.create_narrative_turtle import create_graph
from dna.nlp import parse_narrative

text_clauses1 = 'While Mary exercised, John practiced guitar.'
text_clauses2 = 'George went along with the plan that Mary outlined.'
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
text_acomp_xcomp = 'Jane is unable to tolerate smoking.'
text_idiom = 'Wear and tear on the bridge caused its collapse.'
text_idiom_full_pass = 'John was accused by George of breaking and entering.'
text_idiom_trunc_pass = 'John was accused of breaking and entering.'
text_negation_emotion = 'Jane has no liking for broccoli.'
text_negation = 'Jane did not stab John.'
text_wikipedia = 'The FBI raided the house.'

repo = "foo"

# Note that it is unlikely that all tests will complete successfully since event semantics can be
# interpreted/reported in multiple ways
# 80%+ of tests should pass


def test_clauses1():
    sentence_instances, quotation_instances, quoted_strings = parse_narrative(text_clauses1)
    success, index, graph_ttl = create_graph(sentence_instances, quotation_instances, 5, repo)
    ttl_str = str(graph_ttl)
    assert ':negated true' not in ttl_str
    assert ':has_active_entity :Mary' in ttl_str
    assert 'a :BodilyAct ; :text "exercised' in ttl_str
    assert 'a :ArtAndEntertainmentEvent ; :text "practiced' in ttl_str \
           or 'a :KnowledgeAndSkill ; :text "practiced' in ttl_str
    if 'a :ArtAndEntertainmentEvent' in ttl_str:
        assert ':has_active_entity :John' in ttl_str
    else:
        assert ':has_described_entity :John' in ttl_str
    assert 'a :MusicalInstrument ; :text "guitar' in ttl_str
    # Output Turtle:
    # :Sentence_83f4627b-68b7 a :Sentence ; :offset 1 .
    # :Sentence_83f4627b-68b7 :text "While Mary exercised, John practiced guitar." .
    # :Mary :text "Mary" .
    # :Mary a :Person .
    # :Mary rdfs:label "Mary" .
    # :Mary :gender "female" .
    # :John :text "John" .
    # :John a :Person .
    # :John rdfs:label "John" .
    # :John :gender "male" .
    # :Sentence_83f4627b-68b7 :mentions :Mary .
    # :Sentence_83f4627b-68b7 :mentions :John .
    # :Sentence_83f4627b-68b7 :summary "Mary exercised, John practiced guitar." .
    # :Sentence_83f4627b-68b7 :sentiment "neutral" .
    # :Sentence_83f4627b-68b7 :grade_level 3 .
    # :Sentence_83f4627b-68b7 :has_semantic :Event_53b5b210-5500 .
    # :Event_53b5b210-5500 a :BodilyAct ; :text "exercised" .
    # :Event_53b5b210-5500 :has_active_entity :Mary .
    # :Sentence_83f4627b-68b7 :has_semantic :Event_34ddb5db-8335 .
    # :Event_34ddb5db-8335 a :KnowledgeAndSkill ; :text "practiced" .
    # :Event_34ddb5db-8335 :has_described_entity :John .
    # :Event_34ddb5db-8335 :has_active_entity :John .
    # :Noun_7edc415b-3b59 a :MusicalInstrument ; :text "guitar" ; rdfs:label "guitar" .
    # :Event_34ddb5db-8335 :has_instrument :Noun_7edc415b-3b59 .


def test_clauses2():
    sentence_instances, quotation_instances, quoted_strings = parse_narrative(text_clauses2)
    success, index, graph_ttl = create_graph(sentence_instances, quotation_instances, 5, repo)
    ttl_str = str(graph_ttl)
    assert ':negated true' not in ttl_str
    assert ':has_active_entity :Mary' in ttl_str and ':has_active_entity :George' in ttl_str
    assert 'a :Process ; :text "plan' in ttl_str
    assert ':Agreement' in ttl_str
    assert ':text "went along with' in ttl_str
    assert ':Process' in ttl_str
    assert ':text "outlined' in ttl_str and ':text "plan' in ttl_str
    assert ':has_topic :Noun'
    # Output Turtle:
    # :Sentence_47dd00f7-c71c a :Sentence ; :offset 1 .
    # :Sentence_47dd00f7-c71c :text "George went along with the plan that Mary outlined." .
    # :George :text "George" .
    # :George a :Person .
    # :George rdfs:label "George" .
    # :George :gender "male" .
    # :Mary :text "Mary" .
    # :Mary a :Person .
    # :Mary rdfs:label "Mary" .
    # :Mary :gender "female" .
    # :Sentence_47dd00f7-c71c :mentions :George .
    # :Sentence_47dd00f7-c71c :mentions :Mary .
    # :Sentence_47dd00f7-c71c :summary "George agreed to follow Mary\'s outlined plan." .
    # :Sentence_47dd00f7-c71c :sentiment "neutral" .
    # :Sentence_47dd00f7-c71c :grade_level 5 .
    # :Sentence_47dd00f7-c71c :has_semantic :Event_b7855987-fc75 .
    # :Event_b7855987-fc75 a :Agreement ; :text "went along with" .
    # :Event_b7855987-fc75 :has_active_entity :George .
    # :Noun_63a6284c-142c a :Process ; :text "plan" ; rdfs:label "the plan that Mary outlined" .
    # :Event_b7855987-fc75 :has_topic :Noun_63a6284c-142c .
    # :Sentence_47dd00f7-c71c :has_semantic :Event_5d676c65-a0ea .
    # :Event_5d676c65-a0ea a :Cognition ; :text "outlined" .
    # :Event_5d676c65-a0ea :has_active_entity :Mary .
    # :Event_5d676c65-a0ea :has_topic :Noun_63a6284c-142c .


def test_aux_only():
    sentence_instances, quotation_instances, quoted_strings = parse_narrative(text_aux_only)
    success, index, graph_ttl = create_graph(sentence_instances, quotation_instances, 5, repo)
    ttl_str = str(graph_ttl)
    assert ':negated true' not in ttl_str
    assert 'a :EnvironmentAndCondition' in ttl_str     # is
    assert ':has_described_entity :Joe' in ttl_str
    assert ':has_aspect' in ttl_str and 'a :LineOfBusiness ; :text "attorney' in ttl_str
    # Output Turtle:
    # :Sentence_08134e71-b105 a :Sentence ; :offset 1 .
    # :Sentence_08134e71-b105 :text "Joe is an attorney." .
    # :Joe :text "Joe" .
    # :Joe a :Person .
    # :Joe rdfs:label "Joe" .
    # :Joe :gender "male" .
    # :Sentence_08134e71-b105 :mentions :Joe .
    # :Sentence_08134e71-b105 :summary "Joe holds the profession of an attorney." .
    # :Sentence_08134e71-b105 :sentiment "neutral" .
    # :Sentence_08134e71-b105 :grade_level 3 .
    # :Sentence_08134e71-b105 :has_semantic :Event_fcd2ee35-61fc .
    # :Event_fcd2ee35-61fc a :EnvironmentAndCondition ; :text "is" .
    # :Event_fcd2ee35-61fc :has_described_entity :Joe .
    # :Noun_1d28969e-2e76 a :LineOfBusiness ; :text "attorney" ; rdfs:label "an attorney" .
    # :Event_fcd2ee35-61fc :has_aspect :Noun_1d28969e-2e76 .


def test_affiliation():
    sentence_instances, quotation_instances, quoted_strings = parse_narrative(text_affiliation)
    success, index, graph_ttl = create_graph(sentence_instances, quotation_instances, 5, repo)
    ttl_str = str(graph_ttl)
    print(ttl_str)
    assert ':negated true' not in ttl_str
    assert 'a :Affiliation' in ttl_str
    assert 'Mayberry_Book_Club a :OrganizationalEntity' in ttl_str
    assert ':has_active_entity :Joe' in ttl_str
    assert ':affiliated_with :Mayberry_' in ttl_str    # TODO: Error - OpenAI may classify Mayberry as the location
    # Output Turtle:
    # :Sentence_8534dde4-336e a :Sentence ; :offset 1 .
    # :Sentence_8534dde4-336e :text "Joe is a member of the Mayberry Book Club." .
    # :Joe :text "Joe" .
    # :Joe a :Person .
    # :Joe rdfs:label "Joe" .
    # :Joe :gender "male" .
    # :Mayberry_Book_Club :text "Mayberry Book Club" .
    # :Mayberry_Book_Club a :OrganizationalEntity .
    # :Mayberry_Book_Club rdfs:label "Mayberry Book Club" .
    # :Sentence_8534dde4-336e :mentions :Joe .
    # :Sentence_8534dde4-336e :mentions :Mayberry_Book_Club .
    # :Sentence_8534dde4-336e :summary "Joe belongs to Mayberry Book Club." .
    # :Sentence_8534dde4-336e :sentiment "neutral" .
    # :Sentence_8534dde4-336e :grade_level 3 .
    # :Sentence_8534dde4-336e :has_semantic :Event_6597c681-6606 .
    # :Event_6597c681-6606 a :Affiliation ; :text "is" .
    # :Event_6597c681-6606 :has_active_entity :Joe .
    # :Event_6597c681-6606 :affiliated_with :Mayberry_Book_Club .


def test_complex1():
    sentence_instances, quotation_instances, quoted_strings = parse_narrative(text_complex1)
    success, index, graph_ttl = create_graph(sentence_instances, quotation_instances, 5, repo)
    ttl_str = str(graph_ttl)
    assert ':negated true' not in ttl_str
    assert ':Harriet_Hageman' in ttl_str and ':Liz_Cheney' in ttl_str and ':Abraham_Lincoln' in ttl_str
    assert ':Cognition' in ttl_str or ':CommunicationAndSpeechAct' in ttl_str
    assert ':text "compared' in ttl_str
    assert ':has_active_entity :Liz_Cheney' in ttl_str       # Cheney compared herself
    # Sometimes present
    # assert ':has_affected_entity :Liz_Cheney' in ttl_str or ':has_topic :Liz_Cheney' in ttl_str
    assert ':has_topic :Abraham_Lincoln' in ttl_str          # to Lincoln
    # TODO: Cheney's loss/Harriet Hageman's win
    # assert ' a :Loss ; :text "loss' in ttl_str
    # Output:
    # :Sentence_11e530cd-6b38 a :Sentence ; :offset 1 .
    # :Sentence_11e530cd-6b38 :text "Rep. Liz Cheney R-WY compared herself to former President Abraham Lincoln
    #     during her concession speech shortly after her loss to Trump-backed Republican challenger Harriet Hageman." .
    # :Liz_Cheney :text "Liz Cheney" .
    # :Liz_Cheney a :Person .
    # ...
    # :Sentence_11e530cd-6b38 :mentions :Liz_Cheney .
    # :Sentence_11e530cd-6b38 :mentions :WY .
    # :Sentence_11e530cd-6b38 :mentions :Abraham_Lincoln .
    # :Sentence_11e530cd-6b38 :mentions :Trump .
    # :Sentence_11e530cd-6b38 :mentions :Republican .
    # :Sentence_11e530cd-6b38 :mentions :Harriet_Hageman .
    # :Sentence_11e530cd-6b38 :summary "Cheney compares herself to Lincoln in concession speech." .
    # :Sentence_11e530cd-6b38 :sentiment "neutral" .
    # :Sentence_11e530cd-6b38 :grade_level 8 .
    # :Sentence_11e530cd-6b38 :rhetorical_device {:evidence "Rep. Liz Cheney compared herself to former
    #     President Abraham Lincoln."}  "allusion" .
    # :Sentence_11e530cd-6b38 :rhetorical_device {:evidence "Rep. Liz Cheney compared herself to former
    #     President Abraham Lincoln."}  "metaphor" .
    # :Sentence_11e530cd-6b38 :has_semantic :Event_486e43cd-8e31 .
    # :Event_486e43cd-8e31 a :Cognition, :CommunicationAndSpeechAct ; :text "compared" .
    # :Event_486e43cd-8e31 :has_active_entity :Liz_Cheney .
    # :Event_486e43cd-8e31 :has_topic :Liz_Cheney .
    # :Event_486e43cd-8e31 :has_topic :Abraham_Lincoln .
    # :Sentence_11e530cd-6b38 :has_semantic :Event_cc6bfe0b-1096 .
    # :Event_cc6bfe0b-1096 a :Affiliation ; :text "Trump-backed" .
    # :Event_cc6bfe0b-1096 :has_active_entity :Trump .
    # :Event_cc6bfe0b-1096 :affiliated_with :Harriet_Hageman .


def test_complex2():
    sentence_instances, quotation_instances, quoted_strings = parse_narrative(text_complex2)
    success, index, graph_ttl = create_graph(sentence_instances, quotation_instances, 5, repo)
    ttl_str = str(graph_ttl)
    assert ':has_quantification' in ttl_str
    assert ':Measurement' in ttl_str
    assert ':Win ; :text "won' in ttl_str
    assert ':has_active_entity :Harriet_Hageman' in ttl_str
    assert ':has_active_entity :Noun' in ttl_str    # former president
    assert ':Affiliation ; :text "was endorsed' in ttl_str
    # Output Turtle:
    # :Sentence_4f2b64f0-73dc a :Sentence ; :offset 1 .
    # :Sentence_4f2b64f0-73dc :text "Harriet Hageman, a water and natural-resources attorney who was endorsed by
    #     the former president, won 66.3% of the vote to Ms. Cheney’s 28.9%, with 95% of all votes counted." .
    # :Harriet_Hageman :text "Harriet Hageman" .
    # :Harriet_Hageman a :Person .
    # ...
    # :Sentence_4f2b64f0-73dc :mentions :Harriet_Hageman .
    # :Sentence_4f2b64f0-73dc :mentions :Cheney .
    # :Sentence_4f2b64f0-73dc :summary "Harriet Hageman wins with 66.3% against Cheney\'s 28.9%." .
    # :Sentence_4f2b64f0-73dc :sentiment "neutral" .
    # :Sentence_4f2b64f0-73dc :grade_level 8 .
    # :Sentence_4f2b64f0-73dc :rhetorical_device {:evidence "Use of specific percentages and statistical data
    #     (\'won 66.3% of the vote to Ms. Cheney’s 28.9%, with 95% of all votes counted\') to support the
    #     statement about the election results."}  "logos" .
    # :Sentence_4f2b64f0-73dc :has_semantic :Event_8f69d8fd-a109 .
    # :Event_8f69d8fd-a109 a :Affiliation ; :text "was endorsed" .
    # :Event_8f69d8fd-a109 :affiliated_with :Harriet_Hageman .
    # :Noun_10ff6036-241d a :Person ; :text "president" ; rdfs:label "by the former president" .
    # :Event_8f69d8fd-a109 :has_active_entity :Noun_10ff6036-241d .
    # :Sentence_4f2b64f0-73dc :has_semantic :Event_8dea8aae-cdfd .
    # :Event_8dea8aae-cdfd a :Affiliation ; :text "was endorsed" .
    # :Event_8dea8aae-cdfd :affiliated_with :Harriet_Hageman .
    # :Event_8dea8aae-cdfd :has_active_entity :Noun_10ff6036-241d .
    # :Sentence_4f2b64f0-73dc :has_semantic :Event_18c3aadf-278a .
    # :Event_18c3aadf-278a a :Win ; :text "won 66.3% of the vote" .
    # :Event_18c3aadf-278a :has_active_entity :Harriet_Hageman .
    # :Noun_34a271fe-b500 a :Measurement ; :text "66.3%" ; rdfs:label "66.3% of the vote" .
    # :Event_18c3aadf-278a :has_quantification :Noun_34a271fe-b500 .
    # :Event_18c3aadf-278a :has_affected_entity :Cheney .
    # :Sentence_4f2b64f0-73dc :has_semantic :Event_020c1ab4-1c83 .
    # :Event_020c1ab4-1c83 a :End ; :text "with 95% of all votes counted" .
    # :Noun_b33c3f5b-3009 a :InformationSource ; :text "votes" ; rdfs:label "95% of all votes" .
    # :Event_020c1ab4-1c83 :has_topic :Noun_b33c3f5b-3009 .


def test_coref():
    sentence_instances, quotation_instances, quoted_strings = parse_narrative(text_coref)
    success, index, graph_ttl = create_graph(sentence_instances, quotation_instances, 5, repo)
    ttl_str = str(graph_ttl)
    assert ':negated true' not in ttl_str
    assert 'a :HealthAndDiseaseRelated ; :text "broke' in ttl_str
    assert ':HealthAndDiseaseRelated ; :text "went' in ttl_str or \
           ':MovementTravelAndTransportation; :text "went' in ttl_str
    assert 'a :ComponentPart ; :text "foot' in ttl_str
    assert ':has_affected_entity :Noun' in ttl_str or ':has_topic :Noun' in ttl_str     # foot
    assert ':has_active_entity :Joe' in ttl_str
    assert 'a :Person ; :text "doctor' in ttl_str or 'a :LineOfBusiness ; :text "doctor' in ttl_str
    assert ':has_affected_entity :Noun' in ttl_str or ':has_destination :Noun'          # to the doctor
    # Output Turtle:
    # :Sentence_55d9fec0-3e14 a :Sentence ; :offset 1 .
    # :Sentence_55d9fec0-3e14 :text "Joe broke his foot." .
    # :Joe :text "Joe" .
    # :Joe a :Person .
    # :Joe rdfs:label "Joe" .
    # :Joe :gender "male" .
    # :Sentence_55d9fec0-3e14 :mentions :Joe .
    # :Sentence_55d9fec0-3e14 :summary "Joe sustained a foot injury." .
    # :Sentence_55d9fec0-3e14 :sentiment "negative" .
    # :Sentence_55d9fec0-3e14 :grade_level 3 .
    # :Sentence_55d9fec0-3e14 :has_semantic :Event_1193a858-2cd3 .
    # :Event_1193a858-2cd3 a :HealthAndDiseaseRelated ; :text "broke" .
    # :Event_1193a858-2cd3 :has_active_entity :Joe .
    # :Noun_497602fb-c9c8 a :ComponentPart ; :text "foot" ; rdfs:label "his foot" .
    # :Event_1193a858-2cd3 :has_topic :Noun_497602fb-c9c8 .
    # :Sentence_941efddc-9e92 a :Sentence ; :offset 2 .
    # :Sentence_941efddc-9e92 :text "He went to the doctor." .
    # :Sentence_941efddc-9e92 :summary "Visit to the doctor occurred." .
    # :Sentence_941efddc-9e92 :sentiment "neutral" .
    # :Sentence_941efddc-9e92 :grade_level 3 .
    # :Sentence_941efddc-9e92 :has_semantic :Event_35b46cd7-9320 .
    # :Event_35b46cd7-9320 a :HealthAndDiseaseRelated ; :text "went to the doctor" .
    # :Event_35b46cd7-9320 :has_active_entity :Joe .
    # :Noun_c13beaa4-d9ea a :Person ; :text "doctor" ; rdfs:label "to the doctor" .
    # :Event_35b46cd7-9320 :has_affected_entity :Noun_c13beaa4-d9ea .


def test_xcomp():
    sentence_instances, quotation_instances, quoted_strings = parse_narrative(text_xcomp)
    success, index, graph_ttl = create_graph(sentence_instances, quotation_instances, 5, repo)
    ttl_str = str(graph_ttl)
    assert ':negated true' not in ttl_str
    assert ':has_active_entity :Mary' in ttl_str
    assert ':has_location :Noun' in ttl_str or ':has_affected_entity :Noun' in ttl_str    # being with grandfather
    assert ':EmotionalResponse' in ttl_str
    assert ':sentiment "positive' in ttl_str
    # Output:
    # :Sentence_3712805e-705d a :Sentence ; :offset 1 .
    # :Sentence_3712805e-705d :text "Mary enjoyed being with her grandfather." .
    # :Mary :text "Mary" .
    # :Mary a :Person .
    # :Mary rdfs:label "Mary" .
    # :Mary :gender "female" .
    # :Sentence_3712805e-705d :mentions :Mary .
    # :Sentence_3712805e-705d :summary "Mary enjoyed grandfather\'s company." .
    # :Sentence_3712805e-705d :sentiment "positive" .
    # :Sentence_3712805e-705d :grade_level 1 .
    # :Sentence_3712805e-705d :has_semantic :Event_7c17f84e-ebfc .
    # :Event_7c17f84e-ebfc a :EmotionalResponse, :MeetingAndEncounter ; :text "enjoyed being" .
    # :Event_7c17f84e-ebfc :has_active_entity :Mary .
    # :Noun_e16db766-5518 a :Person ; :text "grandfather" ; rdfs:label "with her grandfather" .
    # :Event_7c17f84e-ebfc :has_location :Noun_e16db766-5518 .    # TODO: "With" as location but class type = Person


def test_modal():
    sentence_instances, quotation_instances, quoted_strings = parse_narrative(text_modal)
    success, index, graph_ttl = create_graph(sentence_instances, quotation_instances, 5, repo)
    ttl_str = str(graph_ttl)
    assert ':negated true' not in ttl_str
    assert ':has_active_entity :Mary' in ttl_str
    if ':future true' in ttl_str:
        assert ':OpportunityAndPossibility' in ttl_str
    else:
        assert ':ReadinessAndAbility' in ttl_str
    assert ':MeetingAndEncounter' in ttl_str                  # visit
    assert 'a :Person ; :text "grandfather' in ttl_str
    assert ':has_affected_entity :Noun' in ttl_str
    assert ':has_time [ :text "on Tuesday' in ttl_str
    # Output Turtle:
    # :Sentence_05091962-fe02 a :Sentence ; :offset 1 .
    # :Sentence_05091962-fe02 :text "Mary can visit her grandfather on Tuesday." .
    # :Mary :text "Mary" .
    # :Mary a :Person .
    # :Mary rdfs:label "Mary" .
    # :Mary :gender "female" .
    # :Sentence_05091962-fe02 :mentions :Mary .
    # :Sentence_05091962-fe02 :summary "Mary schedules visit to grandfather on Tuesday." .
    # :Sentence_05091962-fe02 :sentiment "positive" .
    # :Sentence_05091962-fe02 :grade_level 3 .
    # :Sentence_05091962-fe02 :has_semantic {:future true} :Event_9aaa6f8d-d6a9 .
    # :Event_9aaa6f8d-d6a9 a :MeetingAndEncounter, :OpportunityAndPossibility ; :text "can visit" .
    # :Event_9aaa6f8d-d6a9 :has_active_entity :Mary .
    # :Noun_9cdb5186-8761 a :Person ; :text "grandfather" ; rdfs:label "her grandfather" .
    # :Event_9aaa6f8d-d6a9 :has_affected_entity :Noun_9cdb5186-8761 .
    # :Event_9aaa6f8d-d6a9 :has_time [ :text "on Tuesday" ; a :Time ] .


def test_modal_neg():
    sentence_instances, quotation_instances, quoted_strings = parse_narrative(text_modal_neg)
    success, index, graph_ttl = create_graph(sentence_instances, quotation_instances, 5, repo)
    ttl_str = str(graph_ttl)
    assert ':has_active_entity :Mary' in ttl_str
    assert 'a :Person ; :text "grandfather' in ttl_str
    assert ':has_affected_entity :Noun' in ttl_str
    assert 'a {:negated true} :MeetingAndEncounter ; :text "will not visit' in ttl_str
    assert '{:future true}' in ttl_str
    # Output Turtle:
    # :Sentence_50dad4a4-c0b7 a :Sentence ; :offset 1 .
    # :Sentence_50dad4a4-c0b7 :text "Mary will not visit her grandfather next Tuesday." .
    # :Mary :text "Mary" .
    # :Mary a :Person .
    # :Mary rdfs:label "Mary" .
    # :Mary :gender "female" .
    # :Sentence_50dad4a4-c0b7 :mentions :Mary .
    # :Sentence_50dad4a4-c0b7 :summary "Mary cancels visit to grandfather next Tuesday." .
    # :Sentence_50dad4a4-c0b7 :sentiment "negative" .
    # :Sentence_50dad4a4-c0b7 :grade_level 3 .
    # :Sentence_50dad4a4-c0b7 :has_semantic {:future true} :Event_0533c4bf-671b .
    # :Event_0533c4bf-671b a {:negated true} :MeetingAndEncounter ; :text "will not visit" .
    # :Event_0533c4bf-671b :has_active_entity :Mary .
    # :Noun_40ca5bfa-a33e a :Person ; :text "grandfather" ; rdfs:label "her grandfather" .
    # :Event_0533c4bf-671b :has_affected_entity :Noun_40ca5bfa-a33e .
    # :Event_0533c4bf-671b :has_time [ :text "next Tuesday" ; a :Time ] .


def test_acomp():
    sentence_instances, quotation_instances, quoted_strings = parse_narrative(text_acomp)
    success, index, graph_ttl = create_graph(sentence_instances, quotation_instances, 5, repo)
    ttl_str = str(graph_ttl)
    assert 'a :EnvironmentAndCondition' in ttl_str
    assert ':has_described_entity :Mary' in ttl_str
    # Output Turtle:
    # :Sentence_64e496cd-4194 a :Sentence ; :offset 1 .
    # :Sentence_64e496cd-4194 :text "Mary is very beautiful." .
    # :Mary :text "Mary" .
    # :Mary a :Person .
    # :Mary rdfs:label "Mary" .
    # :Mary :gender "female" .
    # :Sentence_64e496cd-4194 :mentions :Mary .
    # :Sentence_64e496cd-4194 :summary "Mary possesses great beauty." .
    # :Sentence_64e496cd-4194 :sentiment "positive" .
    # :Sentence_64e496cd-4194 :grade_level 1 .
    # :Sentence_64e496cd-4194 :has_semantic :Event_c36bce92-0d98 .
    # :Event_c36bce92-0d98 a :EnvironmentAndCondition ; :text "is very beautiful" .
    # :Event_c36bce92-0d98 :has_described_entity :Mary .


def test_acomp_pcomp():
    sentence_instances, quotation_instances, quoted_strings = parse_narrative(text_acomp_pcomp)
    success, index, graph_ttl = create_graph(sentence_instances, quotation_instances, 5, repo)
    ttl_str = str(graph_ttl)
    assert ':negated true' not in ttl_str
    assert ':EmotionalResponse' in ttl_str
    assert ':BodilyAct' in ttl_str        # running
    assert ':has_active_entity :Peter' in ttl_str
    # Output Turtle:
    # :Sentence_7e04ffe3-ed71 a :Sentence ; :offset 1 .
    # :Sentence_7e04ffe3-ed71 :text "Peter got tired of running." .
    # :Peter :text "Peter" .
    # :Peter a :Person .
    # :Peter rdfs:label "Peter" .
    # :Peter :gender "male" .
    # :Sentence_7e04ffe3-ed71 :mentions :Peter .
    # :Sentence_7e04ffe3-ed71 :summary "Peter became exhausted from running." .
    # :Sentence_7e04ffe3-ed71 :sentiment "negative" .
    # :Sentence_7e04ffe3-ed71 :grade_level 3 .
    # :Sentence_7e04ffe3-ed71 :has_semantic :Event_b4bcaa70-2cde .
    # :Event_b4bcaa70-2cde a :EmotionalResponse, :SensoryPerception ; :text "got tired of running" .
    # :Event_b4bcaa70-2cde :has_active_entity :Peter .


def test_acomp_xcomp():
    sentence_instances, quotation_instances, quoted_strings = parse_narrative(text_acomp_xcomp)
    success, index, graph_ttl = create_graph(sentence_instances, quotation_instances, 5, repo)
    ttl_str = str(graph_ttl)
    assert ':negated true' in ttl_str
    assert 'a {:negated true} :OpenMindednessAndTolerance ; :text "is unable to tolerate' in ttl_str
    assert 'a :HealthAndDiseaseRelated ; :text "smoking' in ttl_str     # TODO: BodilyAct would be more correct
    assert ':has_active_entity :Jane' in ttl_str
    assert ':has_topic :Noun' in ttl_str
    # Output Turtle:
    # :Sentence_7fd3fefe-5f07 a :Sentence ; :offset 1 .
    # :Sentence_7fd3fefe-5f07 :text "Jane is unable to tolerate smoking." .
    # :Jane :text "Jane" .
    # :Jane a :Person .
    # :Jane rdfs:label "Jane" .
    # :Jane :gender "female" .
    # :Sentence_7fd3fefe-5f07 :mentions :Jane .
    # :Sentence_7fd3fefe-5f07 :summary "Jane cannot tolerate smoking." .
    # :Sentence_7fd3fefe-5f07 :sentiment "negative" .
    # :Sentence_7fd3fefe-5f07 :grade_level 3 .
    # :Sentence_7fd3fefe-5f07 :has_semantic :Event_3ac1780f-0b14 .
    # :Event_3ac1780f-0b14 a {:negated true} :OpenMindednessAndTolerance ; :text "is unable to tolerate" .
    # :Event_3ac1780f-0b14 :has_active_entity :Jane .
    # :Noun_b2cbefc0-b5dc a :HealthAndDiseaseRelated ; :text "smoking" ; rdfs:label "smoking" .
    # :Event_3ac1780f-0b14 :has_topic :Noun_b2cbefc0-b5dc .
    # :Sentence_7fd3fefe-5f07 :has_semantic :Event_6bbfe9b8-885b .
    # :Event_6bbfe9b8-885b a {:negated true} :OpenMindednessAndTolerance ; :text "unable to tolerate" .
    # :Event_6bbfe9b8-885b :has_active_entity :Jane .
    # :Event_6bbfe9b8-885b :has_topic :Noun_b2cbefc0-b5dc .


def test_idiom():
    sentence_instances, quotation_instances, quoted_strings = parse_narrative(text_idiom)
    success, index, graph_ttl = create_graph(sentence_instances, quotation_instances, 5, repo)
    ttl_str = str(graph_ttl)
    assert ':negated true' not in ttl_str
    assert 'a :TroubleAndProblem ; :text "Wear and tear' in ttl_str
    assert 'a :Causation ; :text "caused' in ttl_str
    assert 'a :Change ; :text "collapse' in ttl_str or 'a :End ; :text "collapse' in ttl_str
    # TODO: Ideally have 'bridge' as location
    # Output Turtle:
    # :Sentence_12e33323-03ba a :Sentence ; :offset 1 .
    # :Sentence_12e33323-03ba :text "Wear and tear on the bridge caused its collapse." .
    # :Sentence_12e33323-03ba :summary "Bridge collapse due to wear and tear." .
    # :Sentence_12e33323-03ba :sentiment "negative" .
    # :Sentence_12e33323-03ba :grade_level 5 .
    # :Sentence_12e33323-03ba :has_semantic :Event_64ef91ef-744c .
    # :Event_64ef91ef-744c a :Causation ; :text "caused" .
    # :Noun_1035e85a-9e84 a :TroubleAndProblem ; :text "Wear and tear" ; rdfs:label "Wear and tear on the bridge" .
    # :Event_64ef91ef-744c :has_cause :Noun_1035e85a-9e84 .
    # :Noun_9175ef1f-8c0a a :Change ; :text "collapse" ; rdfs:label "its collapse" .
    # :Event_64ef91ef-744c :has_topic :Noun_9175ef1f-8c0a .'


def test_idiom_full_pass():
    sentence_instances, quotation_instances, quoted_strings = parse_narrative(text_idiom_full_pass)
    success, index, graph_ttl = create_graph(sentence_instances, quotation_instances, 5, repo)
    ttl_str = str(graph_ttl)
    assert ':negated true' not in ttl_str
    assert 'a :CommunicationAndSpeechAct' in ttl_str     # accused
    assert ':has_affected_entity :John' in ttl_str
    assert ':has_active_entity :George' in ttl_str
    assert ':AggressiveCriminalOrHostileAct ; :text "breaking' in ttl_str   # TODO: Ideally, the full idiom
    # Output Turtle:
    # :Sentence_f9e9ef85-bf5d a :Sentence ; :offset 1 .
    # :Sentence_f9e9ef85-bf5d :text "John was accused by George of breaking and entering." .
    # :John :text "John" .
    # :John a :Person .
    # :John rdfs:label "John" .
    # :John :gender "male" .
    # :George :text "George" .
    # :George a :Person .
    # :George rdfs:label "George" .
    # :George :gender "male" .
    # :Sentence_f9e9ef85-bf5d :mentions :John .
    # :Sentence_f9e9ef85-bf5d :mentions :George .
    # :Sentence_f9e9ef85-bf5d :summary "George accused John of illegal entry." .
    # :Sentence_f9e9ef85-bf5d :sentiment "negative" .
    # :Sentence_f9e9ef85-bf5d :grade_level 5 .
    # :Sentence_f9e9ef85-bf5d :has_semantic :Event_2201c00e-ecc4 .
    # :Event_2201c00e-ecc4 a :CommunicationAndSpeechAct ; :text "was accused" .
    # :Event_2201c00e-ecc4 :has_affected_entity :John .
    # :Event_2201c00e-ecc4 :has_active_entity :George .
    # :Sentence_f9e9ef85-bf5d :has_semantic :Event_c36a4c8b-c582 .
    # :Event_c36a4c8b-c582 a :CommunicationAndSpeechAct ; :text "was accused" .
    # :Event_c36a4c8b-c582 :has_affected_entity :John .
    # :Event_c36a4c8b-c582 :has_active_entity :George .
    # :Event_c36a4c8b-c582 :has_topic [ :text "of breaking and entering" ; a :Clause ] .
    # :Sentence_f9e9ef85-bf5d :has_semantic :Event_9f6988e2-cead .
    # :Event_9f6988e2-cead a :AggressiveCriminalOrHostileAct ; :text "breaking and entering" .
    # :Noun_09d49ca0-65cf a :TroubleAndProblem ; :text "breaking and entering" ; rdfs:label "of breaking and entering" .
    # :Event_9f6988e2-cead :has_topic :Noun_09d49ca0-65cf .
    # :Sentence_f9e9ef85-bf5d :has_semantic :Event_9498fc43-7d9d .
    # :Event_9498fc43-7d9d a :AggressiveCriminalOrHostileAct ; :text "breaking and entering" .
    # :Event_9498fc43-7d9d :has_topic :Noun_09d49ca0-65cf .


def test_idiom_trunc_pass():
    sentence_instances, quotation_instances, quoted_strings = parse_narrative(text_idiom_trunc_pass)
    success, index, graph_ttl = create_graph(sentence_instances, quotation_instances, 5, repo)
    ttl_str = str(graph_ttl)
    assert ':negated true' not in ttl_str
    assert 'a :CommunicationAndSpeechAct' in ttl_str or 'a :AggressiveCriminalOrHostileAct' in ttl_str     # accused
    assert ':has_affected_entity :John' in ttl_str          # TODO: Sometimes incorrectly reported as 'active' entity
    assert ':AggressiveCriminalOrHostileAct' in ttl_str     # breaking and entering
    # Output Turtle:
    # :Sentence_8a1c96fc-4ad2 a :Sentence ; :offset 1 .
    # :Sentence_8a1c96fc-4ad2 :text "John was accused of breaking and entering." .
    # :John :text "John" .
    # :John a :Person .
    # :John rdfs:label "John" .
    # :John :gender "male" .
    # :Sentence_8a1c96fc-4ad2 :mentions :John .
    # :Sentence_8a1c96fc-4ad2 :summary "John accused of breaking and entering." .
    # :Sentence_8a1c96fc-4ad2 :sentiment "negative" .
    # :Sentence_8a1c96fc-4ad2 :grade_level 5 .
    # :Sentence_8a1c96fc-4ad2 :has_semantic :Event_39c963fc-2d7e .
    # :Event_39c963fc-2d7e a :AggressiveCriminalOrHostileAct ; :text "was accused" .
    # :Event_39c963fc-2d7e :has_affected_entity :John .
    # :Sentence_8a1c96fc-4ad2 :has_semantic :Event_b1f37df1-c410 .
    # :Event_b1f37df1-c410 a :AggressiveCriminalOrHostileAct ; :text "was accused" .
    # :Event_b1f37df1-c410 :has_affected_entity :John .
    # :Event_b1f37df1-c410 :has_topic [ :text "of breaking and entering" ; a :Clause ] .
    # :Sentence_8a1c96fc-4ad2 :has_semantic :Event_a55a60e2-e42f .
    # :Event_a55a60e2-e42f a :AggressiveCriminalOrHostileAct ; :text "breaking and entering" .
    # :Event_a55a60e2-e42f :has_active_entity :John .
    # :Sentence_8a1c96fc-4ad2 :has_semantic :Event_562e99d8-ac30 .
    # :Event_562e99d8-ac30 a :AggressiveCriminalOrHostileAct ; :text "breaking and entering" .
    # :Event_562e99d8-ac30 :has_active_entity :John .


def test_negation_emotion():
    sentence_instances, quotation_instances, quoted_strings = parse_narrative(text_negation_emotion)
    success, index, graph_ttl = create_graph(sentence_instances, quotation_instances, 5, repo)
    ttl_str = str(graph_ttl)
    assert ':EmotionalResponse' in ttl_str    # May be negated since it is a negative response
    assert ':has_active_entity :Jane' in ttl_str
    assert 'a :Plant ; :text "broccoli' in ttl_str
    assert ':has_topic :Noun' in ttl_str
    # Output Turtle:
    # :Sentence_d32853a0-8ef5 a :Sentence ; :offset 1 .
    # :Sentence_d32853a0-8ef5 :text "Jane has no liking for broccoli." .
    # :Jane :text "Jane" .
    # :Jane a :Person .
    # :Jane rdfs:label "Jane" .
    # :Jane :gender "female" .
    # :Sentence_d32853a0-8ef5 :mentions :Jane .
    # :Sentence_d32853a0-8ef5 :summary "Jane dislikes broccoli." .
    # :Sentence_d32853a0-8ef5 :sentiment "negative" .
    # :Sentence_d32853a0-8ef5 :grade_level 3 .
    # :Sentence_d32853a0-8ef5 :has_semantic :Event_2b281e77-e21b .
    # :Event_2b281e77-e21b a {:negated true} :EmotionalResponse ; :text "has no liking for" .
    # :Event_2b281e77-e21b :has_active_entity :Jane .
    # :Noun_6c49fac3-dbb1 a :Plant ; :text "broccoli" ; rdfs:label "no liking for broccoli" .
    # :Event_2b281e77-e21b :has_topic :Noun_6c49fac3-dbb1 .


def test_negation():
    sentence_instances, quotation_instances, quoted_strings = parse_narrative(text_negation)
    success, index, graph_ttl = create_graph(sentence_instances, quotation_instances, 5, repo)
    ttl_str = str(graph_ttl)
    assert 'a {:negated true} :AggressiveCriminalOrHostileAct' in ttl_str    # did not stab
    assert ':has_active_entity :Jane' in ttl_str
    assert ':has_affected_entity :John' in ttl_str
    # Output Turtle:
    # :Sentence_63bd45fb-aa1b a :Sentence ; :offset 1 .
    # :Sentence_63bd45fb-aa1b :text "Jane did not stab John." .
    # :Jane :text "Jane" .
    # :Jane a :Person .
    # :Jane rdfs:label "Jane" .
    # :Jane :gender "female" .
    # :John :text "John" .
    # :John a :Person .
    # :John rdfs:label "John" .
    # :John :gender "male" .
    # :Sentence_63bd45fb-aa1b :mentions :Jane .
    # :Sentence_63bd45fb-aa1b :mentions :John .
    # :Sentence_63bd45fb-aa1b :summary "Jane did not stab John." .
    # :Sentence_63bd45fb-aa1b :sentiment "neutral" .
    # :Sentence_63bd45fb-aa1b :grade_level 3 .
    # :Sentence_63bd45fb-aa1b :has_semantic :Event_931e5fdf-be34 .
    # :Event_931e5fdf-be34 a {:negated true} :AggressiveCriminalOrHostileAct ; :text "did not stab" .
    # :Event_931e5fdf-be34 :has_active_entity :Jane .
    # :Event_931e5fdf-be34 :has_affected_entity :John .


def test_wikipedia():
    sentence_instances, quotation_instances, quoted_strings = parse_narrative(text_wikipedia)
    success, index, graph_ttl = create_graph(sentence_instances, quotation_instances, 5, repo)
    ttl_str = str(graph_ttl)
    assert ':identifier_source "Wikidata"' in ttl_str
    assert ':ArrestAndImprisonment' in ttl_str      # raid
    assert ':has_active_entity :FBI' in ttl_str
    assert ':has_location :Noun' in ttl_str
    # Output Turtle:
    # :Sentence_bd1c68b9-6545 a :Sentence ; :offset 1 .
    # :Sentence_bd1c68b9-6545 :text "The FBI raided the house." .
    # :FBI :text "FBI" .
    # :FBI a :OrganizationalEntity .
    # :FBI rdfs:label "FBI", "F.B.I.", "Federal Bureau of Investigation" .
    # :FBI rdfs:comment "From Wikipedia (wikibase_item: Q8333): \'The Federal Bureau of Investigation (FBI) is the
    #     domestic intelligence and security service of the United States and its principal federal law enforcement
    #     agency. An agency of the United States Department of Justice, the FBI is also a member of the U.S.
    #     Intelligence Community and reports to both the Attorney General and the Director of National Intelligence.
    #     A leading U.S. counterterrorism, counterintelligence, and criminal investigative organization, the FBI
    #     has jurisdiction over violations of more than 200 categories of federal crimes.\'" .
    # :FBI :external_link "https://en.wikipedia.org/wiki/Federal_Bureau_of_Investigation" .
    # :FBI :external_identifier {:identifier_source "Wikidata"} "Q8333" .
    # :Sentence_bd1c68b9-6545 :mentions :FBI .
    # :Sentence_bd1c68b9-6545 :summary "FBI conducted raid on a house." .
    # :Sentence_bd1c68b9-6545 :sentiment "negative" .
    # :Sentence_bd1c68b9-6545 :grade_level 5 .
    # :Sentence_bd1c68b9-6545 :has_semantic :Event_b59f6e1e-fa55 .
    # :Event_b59f6e1e-fa55 a :ArrestAndImprisonment, :AggressiveCriminalOrHostileAct ; :text "raided" .
    # :Event_b59f6e1e-fa55 :has_active_entity :FBI .
    # :Noun_aaff033e-18e4 a :Location ; :text "house" ; rdfs:label "the house" .
    # :Event_b59f6e1e-fa55 :has_location :Noun_aaff033e-18e4 .
