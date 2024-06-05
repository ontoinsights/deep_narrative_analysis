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
text_mention = 'The FBI raided the house.'

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
    assert 'a :BodilyAct' in ttl_str and ':text "exercised' in ttl_str
    assert ':ArtAndEntertainmentEvent' in ttl_str or ':KnowledgeAndSkill' in ttl_str    # Or both
    assert ':text "practiced' in ttl_str
    assert ':has_active_entity :John' in ttl_str
    assert 'a :MusicalInstrument ; :text "guitar' in ttl_str
    # Output Turtle:
    # ::Sentence_6d13d6dc-dfcd a :Sentence ; :offset 1 .
    # :Sentence_6d13d6dc-dfcd :text "While Mary exercised, John practiced guitar." .
    # :Mary :text "Mary" .
    # :Mary a :Person, :Correction .
    # :Mary rdfs:label "Mary" .
    # :Mary :gender "female" .
    # :John :text "John" .
    # :John a :Person, :Correction .
    # :John rdfs:label "John" .
    # :John :gender "male" .
    # :Sentence_6d13d6dc-dfcd :mentions :Mary .
    # :Sentence_6d13d6dc-dfcd :mentions :John .
    # :Sentence_6d13d6dc-dfcd :summary "Mary exercised, John practiced guitar." .
    # :Sentence_6d13d6dc-dfcd :sentiment "neutral" .
    # :Sentence_6d13d6dc-dfcd :grade_level 3 .
    # :Sentence_6d13d6dc-dfcd :has_semantic :Event_96741104-a719 .
    # :Event_96741104-a719 a :BodilyAct, :EventAndState ; :text "exercised" .
    # :Event_96741104-a719 :has_active_entity :Mary .
    # :Sentence_6d13d6dc-dfcd :has_semantic :Event_a5afddc0-2b9f .
    # :Event_a5afddc0-2b9f a :ArtAndEntertainmentEvent, :KnowledgeAndSkill ; :text "practiced guitar" .
    # :Event_a5afddc0-2b9f :has_active_entity :John .
    # :Noun_97b9cc32-46d4 a :MusicalInstrument ; :text "guitar" ; rdfs:label "guitar" .
    # :Event_a5afddc0-2b9f :has_instrument :Noun_97b9cc32-46d4 .


def test_clauses2():
    sentence_instances, quotation_instances, quoted_strings = parse_narrative(text_clauses2)
    success, index, graph_ttl = create_graph(sentence_instances, quotation_instances, 5, repo)
    ttl_str = str(graph_ttl)
    assert ':negated true' not in ttl_str
    assert ':has_active_entity :George' in ttl_str
    assert 'a :Process' in ttl_str
    assert ':text "plan' in ttl_str or ':text "the plan' in ttl_str
    assert ':Agreement' in ttl_str
    assert ':text "went along with' in ttl_str
    assert 'a :Cognition ; :text "outlined' in ttl_str
    assert ':has_topic :Noun'
    # Output Turtle:
    # :Sentence_27ad3074-19d2 a :Sentence ; :offset 1 .
    # :Sentence_27ad3074-19d2 :text "George went along with the plan that Mary outlined." .
    # :Sentence_27ad3074-19d2 :mentions :George .
    # :Sentence_27ad3074-19d2 :mentions :Mary .
    # :Sentence_27ad3074-19d2 :summary "George agreed to Mary\'s outlined plan." .
    # :Sentence_27ad3074-19d2 :sentiment "neutral" .
    # :Sentence_27ad3074-19d2 :grade_level 3 .
    # :Sentence_27ad3074-19d2 :has_semantic :Event_1b596db5-1789 .
    # :Event_1b596db5-1789 a :Agreement ; :text "went along with" .
    # :Event_1b596db5-1789 :has_active_entity :George .
    # :Noun_2d3b06ec-813e a :Process ; :text "the plan" ; rdfs:label "the plan" .
    # :Event_1b596db5-1789 :has_topic :Noun_2d3b06ec-813e .
    # :Sentence_27ad3074-19d2 :has_semantic :Event_e2423a3f-b3b2 .
    # :Event_e2423a3f-b3b2 a :Cognition ; :text "outlined" .
    # :Event_e2423a3f-b3b2 :has_active_entity :Mary .
    # :Event_e2423a3f-b3b2 :has_topic :Noun_2d3b06ec-813e .


def test_aux_only():
    sentence_instances, quotation_instances, quoted_strings = parse_narrative(text_aux_only)
    success, index, graph_ttl = create_graph(sentence_instances, quotation_instances, 5, repo)
    ttl_str = str(graph_ttl)
    assert ':negated true' not in ttl_str
    assert 'a :EnvironmentAndCondition' in ttl_str     # is
    assert ':has_described_entity :Joe' in ttl_str
    assert ':has_aspect' in ttl_str
    assert 'a :LineOfBusiness ; :text "attorney' in ttl_str or 'a :LineOfBusiness ; :text "an attorney' in ttl_str
    # Output Turtle:
    # ::Sentence_eaf17a08-9ee9 a :Sentence ; :offset 1 .
    # :Sentence_eaf17a08-9ee9 :text "Joe is an attorney." .
    # :Sentence_eaf17a08-9ee9 :mentions :Joe .
    # :Sentence_eaf17a08-9ee9 :summary "Joe holds the profession of an attorney." .
    # :Sentence_eaf17a08-9ee9 :sentiment "neutral" .
    # :Sentence_eaf17a08-9ee9 :grade_level 3 .
    # :Sentence_eaf17a08-9ee9 :has_semantic :Event_2a94b8dd-8a31 .
    # :Event_2a94b8dd-8a31 a :EnvironmentAndCondition ; :text "is" .
    # :Event_2a94b8dd-8a31 :has_described_entity :Joe .
    # :Noun_0bbdd69d-568d a :LineOfBusiness ; :text "an attorney" ; rdfs:label "an attorney" .
    # :Event_2a94b8dd-8a31 :has_aspect :Noun_0bbdd69d-568d .


def test_affiliation():
    sentence_instances, quotation_instances, quoted_strings = parse_narrative(text_affiliation)
    success, index, graph_ttl = create_graph(sentence_instances, quotation_instances, 5, repo)
    ttl_str = str(graph_ttl)
    assert ':negated true' not in ttl_str
    assert 'a :Affiliation' in ttl_str
    assert ':has_active_entity :Joe' in ttl_str
    assert ':affiliated_with :Mayberry_' in ttl_str
    # Output Turtle:
    # :Sentence_880c5584-dfca a :Sentence ; :offset 1 .
    # :Sentence_880c5584-dfca :text "Joe is a member of the Mayberry Book Club." .
    # :Sentence_880c5584-dfca :mentions :Joe .
    # :Sentence_880c5584-dfca :mentions :Mayberry_Book_Club .
    # :Sentence_880c5584-dfca :summary "Joe belongs to Mayberry Book Club." .
    # :Sentence_880c5584-dfca :sentiment "neutral" .
    # :Sentence_880c5584-dfca :grade_level 3 .
    # :Sentence_880c5584-dfca :has_semantic :Event_514d1e8a-413f .
    # :Event_514d1e8a-413f a :Affiliation ; :text "is a member of" .
    # :Event_514d1e8a-413f :has_active_entity :Joe .
    # :Event_514d1e8a-413f :affiliated_with :Mayberry_Book_Club .'


def test_complex1():
    sentence_instances, quotation_instances, quoted_strings = parse_narrative(text_complex1)
    success, index, graph_ttl = create_graph(sentence_instances, quotation_instances, 5, repo)
    ttl_str = str(graph_ttl)
    assert ':negated true' not in ttl_str
    assert ':Harriet_Hageman' in ttl_str and ':Liz_Cheney' in ttl_str and ':Abraham_Lincoln' in ttl_str
    assert ':Cognition' in ttl_str or ':CommunicationAndSpeechAct' in ttl_str     # compared (or synonymous word)
    assert ':has_active_entity :Liz_Cheney' in ttl_str                            # Cheney compared herself
    assert ':has_affected_entity :Liz_Cheney' in ttl_str or ':has_topic :Liz_Cheney' in ttl_str
    assert ':has_topic :Abraham_Lincoln' in ttl_str or ':has_affected_entity :Abraham_Lincoln' in ttl_str  # to Lincoln
    # Output:
    # :Sentence_57b5ad0c-21b2 a :Sentence ; :offset 1 .
    # :Sentence_57b5ad0c-21b2 :text "Rep. Liz Cheney R-WY compared herself to former President Abraham Lincoln
    #     during her concession speech shortly after her loss to Trump-backed Republican challenger Harriet Hageman." .
    # :Republican :text "Republican" .
    # :Republican rdfs:label "Republicans", "GOP", "Grand Old Party", "Republicans", "Republican Party
    #     (United States)", "United States Republican Party", "US Republican Party", "Republican Party", "Republican" .
    # :Republican a :PoliticalIdeology, :Correction .
    # :Republican rdfs:comment "From Wikipedia (wikibase_item: Q29468): \'The Republican Party, also known as the
    #     GOP, is one of the two major contemporary political parties in the United States...\'" .
    # :Republican :external_link "https://en.wikipedia.org/wiki/Republican_Party_(United_States)" .
    # :Republican :external_identifier "Q29468" .
    # :Sentence_57b5ad0c-21b2 :mentions :Liz_Cheney .
    # :Sentence_57b5ad0c-21b2 :mentions :Wyoming .
    # :Sentence_57b5ad0c-21b2 :mentions :Abraham_Lincoln .
    # :Sentence_57b5ad0c-21b2 :mentions :Donald_Trump .
    # :Sentence_57b5ad0c-21b2 :mentions :Republican .
    # :Sentence_57b5ad0c-21b2 :mentions :Harriet_Hageman .
    # :Sentence_57b5ad0c-21b2 :summary "Cheney likens herself to Lincoln in concession speech." .
    # :Sentence_57b5ad0c-21b2 :sentiment "neutral" .
    # :Sentence_57b5ad0c-21b2 :grade_level 8 .
    # :Sentence_57b5ad0c-21b2 :rhetorical_device "allusion" .
    # :Sentence_57b5ad0c-21b2 :rhetorical_device_allusion "Rep. Liz Cheney compared herself to former
    #     President Abraham Lincoln" .
    # :Sentence_57b5ad0c-21b2 :rhetorical_device "metaphor" .
    # :Sentence_57b5ad0c-21b2 :rhetorical_device_metaphor "compared herself to former President Abraham Lincoln" .
    # :Sentence_57b5ad0c-21b2 :has_semantic :Event_357e342e-0210 .
    # :Event_357e342e-0210 a :Cognition, :CommunicationAndSpeechAct ;
    #     :text "likens" .   # TODO: Resolve to wording in original sentence
    # :Event_357e342e-0210 :has_active_entity :Liz_Cheney .
    # :Event_357e342e-0210 :has_topic :Liz_Cheney .
    # :Event_357e342e-0210 :has_affected_entity :Abraham_Lincoln .


def test_complex2():
    sentence_instances, quotation_instances, quoted_strings = parse_narrative(text_complex2)
    success, index, graph_ttl = create_graph(sentence_instances, quotation_instances, 5, repo)
    ttl_str = str(graph_ttl)
    assert ':has_quantification :Noun' in ttl_str
    assert ':Measurement' in ttl_str
    assert ':Win' in ttl_str
    assert ':has_active_entity :Harriet_Hageman' in ttl_str
    assert ':has_active_entity :Liz_Cheney' in ttl_str
    # TODO: Simplifying to the summary resulted in losing information (Trump endorsement)
    # Output Turtle:
    # :Sentence_31136131-0ea2 a :Sentence ; :offset 1 .
    # :Sentence_31136131-0ea2 :text "Harriet Hageman, a water and natural-resources attorney who was endorsed by the
    #     former president, won 66.3% of the vote to Ms. Cheney’s 28.9%, with 95% of all votes counted." .
    # :Sentence_31136131-0ea2 :mentions :Harriet_Hageman .
    # :Sentence_31136131-0ea2 :mentions :Liz_Cheney .
    # :Sentence_31136131-0ea2 :summary "Harriet Hageman wins 66.3% of vote, Cheney gets 28.9%." .
    # :Sentence_31136131-0ea2 :sentiment "neutral" .
    # :Sentence_31136131-0ea2 :grade_level 8 .
    # :Sentence_31136131-0ea2 :rhetorical_device "logos" .
    # :Sentence_31136131-0ea2 :rhetorical_device_logos "won 66.3% of the vote to Ms. Cheney’s 28.9%, with 95% of
    #     all votes counted" .
    # :Sentence_31136131-0ea2 :has_semantic :Event_32cb3dc5-fd25 .
    # :Event_32cb3dc5-fd25 a :Win ; :text "wins" .
    # :Event_32cb3dc5-fd25 :has_active_entity :Harriet_Hageman .
    # :Noun_9ba90238-38e8 a :Measurement ; :text "66.3% of vote" ; rdfs:label "66.3% of vote" .
    # :Event_32cb3dc5-fd25 :has_quantification :Noun_9ba90238-38e8 .
    # :Sentence_31136131-0ea2 :has_semantic :Event_d61a9d9f-94a4 .
    # :Event_d61a9d9f-94a4 a :AcquisitionPossessionAndTransfer ; :text "gets" .
    # :Event_d61a9d9f-94a4 :has_active_entity :Liz_Cheney .
    # :Event_d61a9d9f-94a4 :has_quantification :Noun_9ba90238-38e8 .


def test_coref():
    sentence_instances, quotation_instances, quoted_strings = parse_narrative(text_coref)
    success, index, graph_ttl = create_graph(sentence_instances, quotation_instances, 5, repo)
    ttl_str = str(graph_ttl)
    assert ':negated true' not in ttl_str
    assert 'a :HealthAndDiseaseRelated ; :text "broke' in ttl_str
    assert ':HealthAndDiseaseRelated' in ttl_str or ':MovementTravelAndTransportation' in ttl_str
    assert ':text "went' in ttl_str
    assert 'a :ComponentPart ; :text "foot' in ttl_str or 'a :ComponentPart ; :text "his foot' in ttl_str
    assert ':has_affected_entity :Noun' in ttl_str or ':has_topic :Noun' in ttl_str     # foot
    assert ':has_active_entity :Joe' in ttl_str
    assert 'a :Person' in ttl_str or 'a :LineOfBusiness' in ttl_str                     # doctor
    assert ':has_destination :Noun'                                                     # to the doctor
    # Output Turtle:
    # :Sentence_08cd7717-1bcb a :Sentence ; :offset 1 .
    # :Sentence_08cd7717-1bcb :text "Joe broke his foot." .
    # :Sentence_08cd7717-1bcb :mentions :Joe .
    # :Sentence_08cd7717-1bcb :summary "Joe sustained a foot injury." .
    # :Sentence_08cd7717-1bcb :sentiment "negative" .
    # :Sentence_08cd7717-1bcb :grade_level 3 .
    # :Sentence_08cd7717-1bcb :has_semantic :Event_8b1c428c-69b8 .
    # :Event_8b1c428c-69b8 a :HealthAndDiseaseRelated ; :text "broke" .
    # :Event_8b1c428c-69b8 :has_active_entity :Joe .
    # :Noun_10e62f92-9776 a :ComponentPart ; :text "his foot" ; rdfs:label "his foot" .
    # :Event_8b1c428c-69b8 :has_topic :Noun_10e62f92-9776 .
    # :Sentence_547db83d-f298 a :Sentence ; :offset 2 .
    # :Sentence_547db83d-f298 :text "He went to the doctor." .
    # :Sentence_547db83d-f298 :summary "Joe visited the doctor." .
    # :Sentence_547db83d-f298 :sentiment "neutral" .
    # :Sentence_547db83d-f298 :grade_level 3 .
    # :Sentence_547db83d-f298 :has_semantic :Event_aeed5556-562d .
    # :Event_aeed5556-562d a :MovementTravelAndTransportation, :HealthAndDiseaseRelated ; :text "went" .
    # :Event_aeed5556-562d :has_active_entity :Joe .
    # :Noun_05a08849-f5a4 a :LineOfBusiness ; :text "to the doctor" ; rdfs:label "to the doctor" .
    # :Event_aeed5556-562d :has_destination :Noun_05a08849-f5a4 .


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
    # :Sentence_faed5162-6863 a :Sentence ; :offset 1 .
    # :Sentence_faed5162-6863 :text "Mary enjoyed being with her grandfather." .
    # :Sentence_faed5162-6863 :mentions :Mary .
    # :Sentence_faed5162-6863 :summary "Mary enjoyed grandfather\'s company." .
    # :Sentence_faed5162-6863 :sentiment "positive" .
    # :Sentence_faed5162-6863 :grade_level 2 .
    # :Sentence_faed5162-6863 :has_semantic :Event_e8f8c122-43a1 .
    # :Event_e8f8c122-43a1 a :EmotionalResponse ; :text "enjoyed" .
    # :Event_e8f8c122-43a1 :has_active_entity :Mary .
    # :Event_e8f8c122-43a1 :has_topic [ :text "being with her grandfather" ; a :Clause ] .
    # :Sentence_faed5162-6863 :has_semantic :Event_7d7a988c-2a9c .
    # :Event_7d7a988c-2a9c a :MeetingAndEncounter ; :text "being with" .
    # :Noun_b902f7cd-d7c5 a :Person ; :text "her grandfather" ; rdfs:label "her grandfather" .
    # :Event_7d7a988c-2a9c :has_affected_entity :Noun_b902f7cd-d7c5 .


def test_modal():
    sentence_instances, quotation_instances, quoted_strings = parse_narrative(text_modal)
    success, index, graph_ttl = create_graph(sentence_instances, quotation_instances, 5, repo)
    ttl_str = str(graph_ttl)
    assert ':has_active_entity :Mary' in ttl_str
    if ':future true' in ttl_str:
        assert ':OpportunityAndPossibility' in ttl_str
    else:
        assert ':ReadinessAndAbility' in ttl_str
    assert ':MeetingAndEncounter' in ttl_str                  # visit
    assert 'a :Person ; :text "grandfather' in ttl_str or 'a :Person ; :text "her grandfather' in ttl_str
    assert ':has_affected_entity :Noun' in ttl_str
    assert ':has_time [ :text "on Tuesday' in ttl_str
    # Output Turtle:
    # :Sentence_5993049b-c42a a :Sentence ; :offset 1 .
    # :Sentence_5993049b-c42a :text "Mary can visit her grandfather on Tuesday." .
    # :Sentence_5993049b-c42a :mentions :Mary .
    # :Sentence_5993049b-c42a :summary "Mary schedules visit to grandfather on Tuesday." .
    # :Sentence_5993049b-c42a :sentiment "positive" .
    # :Sentence_5993049b-c42a :grade_level 2 .
    # :Sentence_5993049b-c42a :has_semantic :Event_2e2224a4-9777 .
    # :Event_2e2224a4-9777 a :MeetingAndEncounter, :ReadinessAndAbility ; :text "can visit" .
    # :Event_2e2224a4-9777 :has_active_entity :Mary .
    # :Noun_4d4704cf-06c4 a :Person ; :text "her grandfather" ; rdfs:label "her grandfather" .
    # :Event_2e2224a4-9777 :has_affected_entity :Noun_4d4704cf-06c4 .
    # :Event_2e2224a4-9777 :has_time [ :text "on Tuesday" ; a :Time ] .


def test_modal_neg():
    sentence_instances, quotation_instances, quoted_strings = parse_narrative(text_modal_neg)
    success, index, graph_ttl = create_graph(sentence_instances, quotation_instances, 5, repo)
    ttl_str = str(graph_ttl)
    assert ':has_active_entity :Mary' in ttl_str
    assert 'a :Person ; :text "grandfather' in ttl_str or 'a :Person ; :text "her grandfather' in ttl_str
    assert ':has_affected_entity :Noun' in ttl_str
    assert ':MeetingAndEncounter ; :negated true; ; :text "will not visit' in ttl_str
    assert ':future true' in ttl_str
    # Output Turtle:
    # :Sentence_f182c364-dc70 a :Sentence ; :offset 1 .
    # :Sentence_f182c364-dc70 :text "Mary will not visit her grandfather next Tuesday." .
    # :Sentence_f182c364-dc70 :mentions :Mary .
    # :Sentence_f182c364-dc70 :summary "Mary cancels next Tuesday\'s visit to her grandfather." .
    # :Sentence_f182c364-dc70 :sentiment "negative" .
    # :Sentence_f182c364-dc70 :grade_level 3 .
    # :Sentence_f182c364-dc70 :has_semantic :Event_cae1e574-a7fb .
    # :Sentence_f182c364-dc70 :future true .
    # :Event_cae1e574-a7fb a :MeetingAndEncounter ; :negated true ; :text "will not visit" .
    # :Event_cae1e574-a7fb :has_active_entity :Mary .
    # :Noun_6cdb5cd6-fdf2 a :Person ; :text "her grandfather" ; rdfs:label "her grandfather" .
    # :Event_cae1e574-a7fb :has_affected_entity :Noun_6cdb5cd6-fdf2 .
    # :Event_cae1e574-a7fb :has_time [ :text "next Tuesday" ; a :Time ] .


def test_acomp():
    sentence_instances, quotation_instances, quoted_strings = parse_narrative(text_acomp)
    success, index, graph_ttl = create_graph(sentence_instances, quotation_instances, 5, repo)
    ttl_str = str(graph_ttl)
    assert 'a :EnvironmentAndCondition ;  :text "is very beautiful' in ttl_str
    assert ':has_described_entity :Mary' in ttl_str
    # Output Turtle:
    # :Sentence_69d87345-c1ac a :Sentence ; :offset 1 .
    # :Sentence_69d87345-c1ac :text "Mary is very beautiful." .
    # :Sentence_69d87345-c1ac :mentions :Mary .
    # :Sentence_69d87345-c1ac :summary "Article describes Mary\'s beauty." .
    # :Sentence_69d87345-c1ac :sentiment "positive" .
    # :Sentence_69d87345-c1ac :grade_level 1 .
    # :Sentence_69d87345-c1ac :has_semantic :Event_55042065-84ea .
    # :Event_55042065-84ea a :EnvironmentAndCondition ; :text "is very beautiful" .
    # :Event_55042065-84ea :has_described_entity :Mary .


def test_acomp_pcomp():
    sentence_instances, quotation_instances, quoted_strings = parse_narrative(text_acomp_pcomp)
    success, index, graph_ttl = create_graph(sentence_instances, quotation_instances, 5, repo)
    ttl_str = str(graph_ttl)
    assert ':negated true' not in ttl_str
    assert ':EmotionalResponse ; :text "got tired of' in ttl_str
    assert ':BodilyAct ; :text "running' in ttl_str
    assert ':has_active_entity :Peter' in ttl_str
    # Output Turtle:
    # :Sentence_d16c167e-43a2 a :Sentence ; :offset 1 .
    # :Sentence_d16c167e-43a2 :text "Peter got tired of running." .
    # :Sentence_d16c167e-43a2 :mentions :Peter .
    # :Sentence_d16c167e-43a2 :summary "Peter became exhausted from running." .
    # :Sentence_d16c167e-43a2 :sentiment "negative" .
    # :Sentence_d16c167e-43a2 :grade_level 2 .
    # :Sentence_d16c167e-43a2 :has_semantic :Event_a7f57a6d-c4b2 .
    # :Event_a7f57a6d-c4b2 a :EmotionalResponse ; :text "got tired of" .
    # :Event_a7f57a6d-c4b2 :has_active_entity :Peter .
    # :Sentence_d16c167e-43a2 :has_semantic :Event_d06368a7-b0c2 .
    # :Event_d06368a7-b0c2 a :EmotionalResponse ; :text "got tired of" .
    # :Noun_0850b9b0-d90e a :BodilyAct ; :text "running" ; rdfs:label "running" .
    # :Event_d06368a7-b0c2 :has_cause :Noun_0850b9b0-d90e .


def test_acomp_xcomp():
    sentence_instances, quotation_instances, quoted_strings = parse_narrative(text_acomp_xcomp)
    success, index, graph_ttl = create_graph(sentence_instances, quotation_instances, 5, repo)
    ttl_str = str(graph_ttl)
    assert 'a :Avoidance ; :negated true ; :text "is unable to tolerate' in ttl_str or \
           'a :OpenMindednessAndTolerance ; :negated true ; :text "is unable to tolerate' in ttl_str
    assert 'a :HealthAndDiseaseRelated ; :text "smoking' in ttl_str     # TODO: BodilyAct would be more correct
    assert ':has_active_entity :Jane' in ttl_str
    assert ':has_topic :Noun' in ttl_str
    # Output Turtle:
    # :Sentence_ddba6ad0-240d a :Sentence ; :offset 1 .
    # :Sentence_ddba6ad0-240d :text "Jane is unable to tolerate smoking." .
    # :Sentence_ddba6ad0-240d :mentions :Jane .
    # :Sentence_ddba6ad0-240d :summary "Jane cannot tolerate smoking." .
    # :Sentence_ddba6ad0-240d :sentiment "negative" .
    # :Sentence_ddba6ad0-240d :grade_level 3 .
    # :Sentence_ddba6ad0-240d :has_semantic :Event_8644a5ee-52e3 .
    # :Event_8644a5ee-52e3 a :Avoidance ; :negated true ; :text "is unable to tolerate" .
    # :Event_8644a5ee-52e3 :has_active_entity :Jane .
    # :Noun_f3a453bb-bd2f a :HealthAndDiseaseRelated ; :text "smoking" ; rdfs:label "smoking" .
    # :Event_8644a5ee-52e3 :has_topic :Noun_f3a453bb-bd2f .


def test_idiom():
    sentence_instances, quotation_instances, quoted_strings = parse_narrative(text_idiom)
    success, index, graph_ttl = create_graph(sentence_instances, quotation_instances, 5, repo)
    ttl_str = str(graph_ttl)
    assert 'a :TroubleAndProblem ; :text "Wear and tear' in ttl_str or 'a :Process ; :text "Wear and tear' in ttl_str
    assert 'a :Causation ; :text "caused' in ttl_str
    assert 'a :Change ; :text "its collapse' in ttl_str or 'a :End ; :text "its collapse' in ttl_str
    # TODO: Ideally have 'bridge' as location
    # Output Turtle:
    # :Sentence_5de5f3ef-6084 a :Sentence ; :offset 1 .
    # :Sentence_5de5f3ef-6084 :text "Wear and tear on the bridge caused its collapse." .
    # :Sentence_5de5f3ef-6084 :summary "Bridge collapse due to wear and tear." .
    # :Sentence_5de5f3ef-6084 :sentiment "negative" .
    # :Sentence_5de5f3ef-6084 :grade_level 5 .
    # :Sentence_5de5f3ef-6084 :has_semantic :Event_8b64cb9c-b233 .
    # :Event_8b64cb9c-b233 a :Causation ; :text "caused" .
    # TODO: Should not be owl:Thing but :Process or :TroubleAndProblem
    # :Noun_61ff7c55-294b a owl:Thing ; :text "Wear and tear on the bridge" ; rdfs:label "Wear and tear on the bridge" .
    # :Event_8b64cb9c-b233 :has_cause :Noun_61ff7c55-294b .
    # :Noun_52b284c2-3963 a :End ; :text "its collapse" ; rdfs:label "its collapse" .
    # :Event_8b64cb9c-b233 :has_topic :Noun_52b284c2-3963 .


def test_idiom_full_pass():
    sentence_instances, quotation_instances, quoted_strings = parse_narrative(text_idiom_full_pass)
    success, index, graph_ttl = create_graph(sentence_instances, quotation_instances, 5, repo)
    ttl_str = str(graph_ttl)
    assert ':negated true' not in ttl_str
    assert 'a :CommunicationAndSpeechAct' in ttl_str     # accused
    assert ':has_affected_entity :John' in ttl_str
    assert ':has_active_entity :George' in ttl_str
    assert ':AggressiveCriminalOrHostileAct ; :text "breaking and entering' in ttl_str
    assert ':has_active_entity :John' in ttl_str
    # Output Turtle:
    # :Sentence_b13a2230-7d18 a :Sentence ; :offset 1 .
    # :Sentence_b13a2230-7d18 :text "John was accused by George of breaking and entering." .
    # :Sentence_b13a2230-7d18 :mentions :John .
    # :Sentence_b13a2230-7d18 :mentions :George .
    # :Sentence_b13a2230-7d18 :summary "George accused John of breaking and entering." .
    # :Sentence_b13a2230-7d18 :sentiment "negative" .
    # :Sentence_b13a2230-7d18 :grade_level 5 .
    # :Sentence_b13a2230-7d18 :has_semantic :Event_644417a4-8ffa .
    # :Event_644417a4-8ffa a :CommunicationAndSpeechAct ; :text "was accused" .
    # :Event_644417a4-8ffa :has_affected_entity :John .
    # :Event_644417a4-8ffa :has_active_entity :George .
    # :Event_644417a4-8ffa :has_topic [ :text "of breaking and entering" ; a :Clause ] .
    # :Sentence_b13a2230-7d18 :has_semantic :Event_26c89c2d-9498 .
    # :Event_26c89c2d-9498 a :AggressiveCriminalOrHostileAct ; :text "breaking and entering" .
    # :Event_26c89c2d-9498 :has_active_entity :John .
    # :Sentence_b13a2230-7d18 :has_semantic :Event_10c0e5ef-a29d .
    # :Event_10c0e5ef-a29d a :AggressiveCriminalOrHostileAct ; :text "breaking and entering" .
    # :Event_10c0e5ef-a29d :has_active_entity :John .


def test_idiom_trunc_pass():
    sentence_instances, quotation_instances, quoted_strings = parse_narrative(text_idiom_trunc_pass)
    success, index, graph_ttl = create_graph(sentence_instances, quotation_instances, 5, repo)
    ttl_str = str(graph_ttl)
    assert ':CommunicationAndSpeechAct' in ttl_str
    assert ':AggressiveCriminalOrHostileAct' in ttl_str
    assert ':has_affected_entity :John' in ttl_str
    # Output Turtle:
    # :Sentence_ee17ca47-a5be a :Sentence ; :offset 1 .
    # :Sentence_ee17ca47-a5be :text "John was accused of breaking and entering." .
    # :Sentence_ee17ca47-a5be :mentions :John .
    # :Sentence_ee17ca47-a5be :summary "John was accused of illegal entry." .
    # :Sentence_ee17ca47-a5be :sentiment "negative" .
    # :Sentence_ee17ca47-a5be :grade_level 5 .
    # :Sentence_ee17ca47-a5be :has_semantic :Event_4ce51bce-5e32 .
    # :Event_4ce51bce-5e32 a :AggressiveCriminalOrHostileAct, :CommunicationAndSpeechAct ; :text "was accused of" .
    # :Event_4ce51bce-5e32 :has_affected_entity :John .
    # TODO: :End is incorrect; Should be :AggressiveCriminalOrHostileAct
    # :Noun_0f0aaa06-e0dd a :End ; :text "breaking and entering" ; rdfs:label "breaking and entering" .
    # :Event_4ce51bce-5e32 :has_topic :Noun_0f0aaa06-e0dd .


def test_negation_emotion():
    sentence_instances, quotation_instances, quoted_strings = parse_narrative(text_negation_emotion)
    success, index, graph_ttl = create_graph(sentence_instances, quotation_instances, 5, repo)
    ttl_str = str(graph_ttl)
    assert 'a :EmotionalResponse ; :negated true ; :text "has no liking for' in ttl_str
    assert ':has_active_entity :Jane' in ttl_str
    assert 'a :Plant ; :text "broccoli' in ttl_str
    assert ':has_topic :Noun' in ttl_str
    # Output Turtle:
    # :Sentence_9c8d2031-2aef a :Sentence ; :offset 1 .
    # :Sentence_9c8d2031-2aef :text "Jane has no liking for broccoli." .
    # :Sentence_9c8d2031-2aef :mentions :Jane .
    # :Sentence_9c8d2031-2aef :summary "Jane dislikes broccoli." .
    # :Sentence_9c8d2031-2aef :sentiment "negative" .
    # :Sentence_9c8d2031-2aef :grade_level 3 .
    # :Sentence_9c8d2031-2aef :has_semantic :Event_adad3cec-a656 .
    # :Event_adad3cec-a656 a :EmotionalResponse ; :negated true ; :text "has no liking for" .
    # :Event_adad3cec-a656 :has_active_entity :Jane .
    # :Noun_f27929b1-b38b a :Affiliation ; :text "liking" ; rdfs:label "liking" .   # TODO: Incorrect
    # :Event_adad3cec-a656 :has_topic :Noun_f27929b1-b38b .
    # :Noun_7251dea1-69e8 a :Plant ; :text "broccoli" ; rdfs:label "broccoli" .
    # :Event_adad3cec-a656 :has_topic :Noun_7251dea1-69e8 .


def test_negation():
    sentence_instances, quotation_instances, quoted_strings = parse_narrative(text_negation)
    success, index, graph_ttl = create_graph(sentence_instances, quotation_instances, 5, repo)
    ttl_str = str(graph_ttl)
    assert 'a :AggressiveCriminalOrHostileAct ; :negated true ; :text "did not stab' in ttl_str
    assert ':has_active_entity :Jane' in ttl_str
    assert ':has_affected_entity :John' in ttl_str
    # Output Turtle:
    # :Sentence_5a0e8be0-a034 a :Sentence ; :offset 1 .
    # :Sentence_5a0e8be0-a034 :text "Jane did not stab John." .
    # :Sentence_5a0e8be0-a034 :mentions :Jane .
    # :Sentence_5a0e8be0-a034 :mentions :John .
    # :Sentence_5a0e8be0-a034 :summary "Jane did not commit violence against John." .
    # :Sentence_5a0e8be0-a034 :sentiment "neutral" .
    # :Sentence_5a0e8be0-a034 :grade_level 3 .
    # :Sentence_5a0e8be0-a034 :has_semantic :Event_33ef992e-7413 .
    # :Event_33ef992e-7413 a :AggressiveCriminalOrHostileAct ; :negated true ; :text "did not stab" .
    # :Event_33ef992e-7413 :has_active_entity :Jane .
    # :Event_33ef992e-7413 :has_affected_entity :John .


def test_mention():
    sentence_instances, quotation_instances, quoted_strings = parse_narrative(text_mention)
    success, index, graph_ttl = create_graph(sentence_instances, quotation_instances, 5, repo)
    ttl_str = str(graph_ttl)
    assert ':mentions :FBI' in ttl_str
    assert 'a :ArrestAndImprisonment' in ttl_str      # raided
    assert ':has_active_entity :FBI' in ttl_str
    assert ':has_location :Noun' in ttl_str
    assert 'a :Location ; :text "the house' in ttl_str
    # Output Turtle:
    # :Sentence_7d91eb70-e511 a :Sentence ; :offset 1 .
    # :Sentence_7d91eb70-e511 :text "The FBI raided the house." .
    # :Sentence_7d91eb70-e511 :mentions :FBI .
    # :Sentence_7d91eb70-e511 :summary "FBI conducted raid on a house." .
    # :Sentence_7d91eb70-e511 :sentiment "negative" .
    # :Sentence_7d91eb70-e511 :grade_level 5 .
    # :Sentence_7d91eb70-e511 :has_semantic :Event_49be8ecd-43ae .
    # :Event_49be8ecd-43ae a :ArrestAndImprisonment ; :text "raided" .
    # :Event_49be8ecd-43ae :has_active_entity :FBI .
    # :Noun_5161a236-ec48 a :Location ; :text "the house" ; rdfs:label "the house" .
    # :Event_49be8ecd-43ae :has_location :Noun_5161a236-ec48 .
