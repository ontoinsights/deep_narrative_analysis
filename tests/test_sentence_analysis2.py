import pytest
from dna.create_narrative_turtle import create_graph
from dna.nlp import parse_narrative

text_multiple_verbs = 'Sue is an attorney but still lies.'
text_aux_pobj = 'John got rid of the debris.'
text_idiom_amod = "John turned a blind eye to Mary's infidelity."
text_advmod = 'Harry put the broken vase back together.'
text_complex_verb = 'The store went out of business on Tuesday.'
text_neg_acomp_xcomp = 'Jane is not able to stomach lies.'
text_non_person_subject = "John's hopes were dashed."
text_first_person = 'I was not ready to leave.'
text_pobj_semantics = 'The robber escaped with the aid of the local police.'
text_multiple_subjects = 'Jane and John had a serious difference of opinion.'
text_multiple_xcomp = 'John liked to ski and to swim.'
text_location_hierarchy = "Switzerland's mountains are magnificent."
text_weather = "Hurricane Otis severely damaged Acapulco."
text_coref = 'Anna saw Heidi cut the roses, but she did not recognize that it was Heidi who cut the roses.'
text_quotation = 'Jane said, "I want to work for NVIDIA."'

repo = 'foo'

# Note that it is unlikely that all tests will complete successfully since event semantics can be
# interpreted/reported in multiple ways
# 80% of tests should pass


def test_multiple_verbs():
    sentence_instances, quotation_instances, quoted_strings = parse_narrative(text_multiple_verbs)
    success, index, graph_ttl = create_graph(sentence_instances, quotation_instances, 3, repo)
    ttl_str = str(graph_ttl)
    assert 'ad hominem' in ttl_str or 'juxtaposition' in ttl_str
    assert ':has_active_entity :Sue' in ttl_str
    if 'a :EnvironmentAndCondition' in ttl_str:    # is
        assert 'a :LineOfBusiness ; :text "an attorney' in ttl_str
    else:
        assert 'a :KnowledgeAndSkill ; :text "an attorney' in ttl_str
    assert ':has_described_entity :Sue' in ttl_str
    assert 'a :DeceptionAndDishonesty ; :text "lies' in ttl_str
    assert ':has_active_entity :Sue' in ttl_str
    # Output Turtle:
    # :Sentence_5f51a0ce-ed8a a :Sentence ; :offset 1 .
    # :Sentence_5f51a0ce-ed8a :text "Sue is an attorney but still lies." .
    # :Sue :text "Sue" .
    # :Sue a :Person, :Correction .
    # :Sue rdfs:label "Sue" .
    # :Sue :gender "female" .
    # :Sentence_5f51a0ce-ed8a :mentions :Sue .
    # :Sentence_5f51a0ce-ed8a :summary "Attorney Sue engages in dishonest behavior." .
    # :Sentence_5f51a0ce-ed8a :sentiment "negative" .
    # :Sentence_5f51a0ce-ed8a :grade_level 5 .
    # :Sentence_5f51a0ce-ed8a :rhetorical_device "ad hominem" .
    # :Sentence_5f51a0ce-ed8a :rhetorical_device_ad_hominem "The phrase \'but still lies\' directly attacks the
    #     character of Sue, implying dishonesty despite her professional status as an attorney." .
    # :Sentence_5f51a0ce-ed8a :rhetorical_device "juxtaposition" .
    # :Sentence_5f51a0ce-ed8a :rhetorical_device_juxtaposition "The sentence places the contrasting ideas of being
    #     an attorney, typically associated with integrity and truthfulness, alongside lying, which is generally
    #     viewed negatively." .
    # :Sentence_5f51a0ce-ed8a :has_semantic :Event_35a96649-03c7 .
    # :Event_35a96649-03c7 a :EnvironmentAndCondition ; :text "is" .
    # :Event_35a96649-03c7 :has_described_entity :Sue .
    # :Noun_45f85bf4-81a5 a :LineOfBusiness ; :text "an attorney" ; rdfs:label "an attorney" .
    # :Event_35a96649-03c7 :has_aspect :Noun_45f85bf4-81a5 .
    # :Sentence_5f51a0ce-ed8a :has_semantic :Event_6dfe8ad7-dfa8 .
    # :Event_6dfe8ad7-dfa8 a :DeceptionAndDishonesty ; :text "lies" .
    # :Event_6dfe8ad7-dfa8 :has_active_entity :Sue .


def test_aux_pobj():
    sentence_instances, quotation_instances, quoted_strings = parse_narrative(text_aux_pobj)
    success, index, graph_ttl = create_graph(sentence_instances, quotation_instances, 3, repo)
    ttl_str = str(graph_ttl)
    assert 'a :RemovalAndRestriction ; :text "got rid of' in ttl_str
    assert ':has_active_entity :John' in ttl_str
    assert ':has_topic :Noun' in ttl_str
    assert ':WasteAndResidue ; :text "the debris' in ttl_str
    # Output Turtle:
    # :Sentence_b9976227-fef5 a :Sentence ; :offset 1 .
    # :Sentence_b9976227-fef5 :text "John got rid of the debris." .
    # :Sentence_b9976227-fef5 :mentions :John .
    # :Sentence_b9976227-fef5 :summary "John disposed of the debris." .
    # :Sentence_b9976227-fef5 :sentiment "neutral" .
    # :Sentence_b9976227-fef5 :grade_level 3 .
    # :Sentence_b9976227-fef5 :has_semantic :Event_7c641d0d-0057 .
    # :Event_7c641d0d-0057 a :RemovalAndRestriction ; :text "got rid of" .
    # :Event_7c641d0d-0057 :has_active_entity :John .
    # :Noun_2e95fa04-5f4c a :WasteAndResidue ; :text "the debris" ; rdfs:label "the debris" .
    # :Event_7c641d0d-0057 :has_topic :Noun_2e95fa04-5f4c .


def test_idiom_amod():
    sentence_instances, quotation_instances, quoted_strings = parse_narrative(text_idiom_amod)
    success, index, graph_ttl = create_graph(sentence_instances, quotation_instances, 3, repo)
    ttl_str = str(graph_ttl)
    assert 'metaphor' in ttl_str
    assert ':Avoidance' in ttl_str and ':DeceptionAndDishonesty' in ttl_str
    assert ':text "turned a blind eye' in ttl_str
    assert ':has_active_entity :John' in ttl_str
    assert ':has_topic :Noun' in ttl_str        # infidelity
    # Output Turtle:
    # :Sentence_2d6b0a42-de2c a :Sentence ; :offset 1 .
    # :Sentence_2d6b0a42-de2c :text "John turned a blind eye to Mary\'s infidelity." .
    # :Sentence_2d6b0a42-de2c :mentions :John .
    # :Sentence_2d6b0a42-de2c :mentions :Mary .
    # :Sentence_2d6b0a42-de2c :summary "John ignored Mary\'s unfaithfulness." .
    # :Sentence_2d6b0a42-de2c :sentiment "negative" .
    # :Sentence_2d6b0a42-de2c :grade_level 5 .
    # :Sentence_2d6b0a42-de2c :rhetorical_device "metaphor" .
    # :Sentence_2d6b0a42-de2c :rhetorical_device_metaphor "The phrase \'turned a blind eye\' is a metaphor for
    #     intentionally ignoring something." .
    # :Sentence_2d6b0a42-de2c :has_semantic :Event_8010aabf-00f7 .
    # :Event_8010aabf-00f7 a :Avoidance, :DeceptionAndDishonesty ; :text "turned a blind eye" .
    # :Event_8010aabf-00f7 :has_active_entity :John .
    # TODO: Idiom is not component part; Nor is it an instrument
    # :Noun_afbf7b60-c5a9 a :ComponentPart ; :text "a blind eye" ; rdfs:label "a blind eye" .
    # :Event_8010aabf-00f7 :has_instrument :Noun_afbf7b60-c5a9 .
    # :Noun_95e9ec8b-61d5 a :DeceptionAndDishonesty ; :text "to Mary\'s infidelity" ;
    #     rdfs:label "to Mary\'s infidelity" .
    # :Event_8010aabf-00f7 :has_topic :Noun_95e9ec8b-61d5 .


def test_advmod():
    sentence_instances, quotation_instances, quoted_strings = parse_narrative(text_advmod)
    success, index, graph_ttl = create_graph(sentence_instances, quotation_instances, 3, repo)
    ttl_str = str(graph_ttl)
    assert 'a :ReturnRecoveryAndRelease ; :text "put back together' in ttl_str or \
           ' a :ProductionManufactureAndCreation ; :text "put back together' in ttl_str
    assert ':has_active_entity :Harry' in ttl_str
    assert ' a :Resource ; :text "the broken vase' in ttl_str
    assert ':has_topic :Noun' in ttl_str
    # Output Turtle:
    # :Sentence_c44d56ae-8cce a :Sentence ; :offset 1 .
    # :Sentence_c44d56ae-8cce :text "Harry put the broken vase back together." .
    # :Harry :text "Harry" .
    # :Harry a :Person, :Correction .
    # :Harry rdfs:label "Harry" .
    # :Harry :gender "male" .
    # :Sentence_c44d56ae-8cce :mentions :Harry .
    # :Sentence_c44d56ae-8cce :summary "Harry repaired the broken vase." .
    # :Sentence_c44d56ae-8cce :sentiment "neutral" .
    # :Sentence_c44d56ae-8cce :grade_level 3 .
    # :Sentence_c44d56ae-8cce :has_semantic :Event_124f4043-72ea .
    # :Event_124f4043-72ea a :ReturnRecoveryAndRelease ; :text "put back together" .
    # :Event_124f4043-72ea :has_active_entity :Harry .
    # :Noun_6f253254-d954 a :Resource ; :text "the broken vase" ; rdfs:label "the broken vase" .
    # :Event_124f4043-72ea :has_topic :Noun_6f253254-d954 .


def test_complex_verb():
    sentence_instances, quotation_instances, quoted_strings = parse_narrative(text_complex_verb)
    success, index, graph_ttl = create_graph(sentence_instances, quotation_instances, 3, repo)
    ttl_str = str(graph_ttl)
    assert ':End' in ttl_str and ':EconomyAndFinanceRelated' in ttl_str
    assert ':text "went out of business' in ttl_str
    assert ':has_active_entity :Noun' in ttl_str
    assert ':has_time [ :text "on Tuesday' in ttl_str
    assert 'a :LineOfBusiness' in ttl_str or 'a :Location' in ttl_str
    assert ':text "store' in ttl_str or ':text "The store' in ttl_str
    # Output Turtle:
    # :Sentence_88927ad9-d45a a :Sentence ; :offset 1 .
    # :Sentence_88927ad9-d45a :text "The store went out of business on Tuesday." .
    # :Sentence_88927ad9-d45a :summary "Store ceased operations on Tuesday." .
    # :Sentence_88927ad9-d45a :sentiment "negative" .
    # :Sentence_88927ad9-d45a :grade_level 3 .
    # :Sentence_88927ad9-d45a :has_semantic :Event_0862453c-b8d6 .
    # :Event_0862453c-b8d6 a :EconomyAndFinanceRelated, :End ; :text "went out of business" .
    # :Noun_4362d1bf-2d6c a :Location ; :text "The store" ; rdfs:label "The store" .
    # :Event_0862453c-b8d6 :has_active_entity :Noun_4362d1bf-2d6c .
    # :Event_0862453c-b8d6 :has_time [ :text "on Tuesday" ; a :Time ] .


def test_neg_acomp_xcomp():
    sentence_instances, quotation_instances, quoted_strings = parse_narrative(text_neg_acomp_xcomp)
    success, index, graph_ttl = create_graph(sentence_instances, quotation_instances, 3, repo)
    ttl_str = str(graph_ttl)
    assert 'a :EmotionalResponse ; :negated true ; :text "is not able to stomach' in ttl_str
    assert ':has_active_entity :Jane' in ttl_str
    assert ':DeceptionAndDishonesty ; :text "lies' in ttl_str
    assert ':has_topic :Noun' in ttl_str
    # Output Turtle:
    # :Sentence_4ec04c7b-5acd a :Sentence ; :offset 1 .
    # :Sentence_4ec04c7b-5acd :text "Jane is not able to stomach lies." .
    # :Sentence_4ec04c7b-5acd :mentions :Jane .
    # :Sentence_4ec04c7b-5acd :summary "Jane cannot tolerate dishonesty." .
    # :Sentence_4ec04c7b-5acd :sentiment "negative" .
    # :Sentence_4ec04c7b-5acd :grade_level 5 .
    # :Sentence_4ec04c7b-5acd :has_semantic :Event_c4bc61c8-5843 .
    # :Event_c4bc61c8-5843 a :EmotionalResponse ; :negated true ; :text "is not able to stomach" .
    # :Event_c4bc61c8-5843 :has_active_entity :Jane .
    # :Noun_5c775a0c-44fc a :DeceptionAndDishonesty ; :text "lies" ; rdfs:label "lies" .
    # :Event_c4bc61c8-5843 :has_topic :Noun_5c775a0c-44fc .


def test_non_person_subject():
    sentence_instances, quotation_instances, quoted_strings = parse_narrative(text_non_person_subject)
    success, index, graph_ttl = create_graph(sentence_instances, quotation_instances, 3, repo)
    ttl_str = str(graph_ttl)
    print(ttl_str)
    assert 'a :Loss ; :text "were dashed' in ttl_str or \
           'a :EmotionalResponse ; :negated true ; :text "were dashed' in ttl_str
    assert ':has_topic :Noun' in ttl_str
    assert 'hopes"' in ttl_str
    # Output Turtle:
    # :Sentence_4b414c77-ccf6 a :Sentence ; :offset 1 .
    # :Sentence_4b414c77-ccf6 :text "John\'s hopes were dashed." .
    # :Sentence_4b414c77-ccf6 :mentions :John .
    # :Sentence_4b414c77-ccf6 :summary "John\'s expectations were completely thwarted." .
    # :Sentence_4b414c77-ccf6 :sentiment "negative" .
    # :Sentence_4b414c77-ccf6 :grade_level 3 .
    # :Sentence_4b414c77-ccf6 :has_semantic :Event_c5c1de46-2ff9 .
    # :Event_c5c1de46-2ff9 a :EmotionalResponse ; :negated true ; :text "were dashed" .
    # TODO: Hopes = EmotionalResponse; Dashed = Loss
    # :Noun_1494229d-9162 a :AchievementAndAccomplishment ; :text "John\'s hopes" ; rdfs:label "John\'s hopes" .
    # :Event_c5c1de46-2ff9 :has_topic :Noun_1494229d-9162 .


def test_first_person():
    sentence_instances, quotation_instances, quoted_strings = parse_narrative(text_first_person)
    success, index, graph_ttl = create_graph(sentence_instances, quotation_instances, 3, repo)
    ttl_str = str(graph_ttl)
    assert ':sentiment "negative' in ttl_str
    assert 'a :ReadinessAndAbility ; :negated true ; :text "was not ready' in ttl_str
    assert 'a :Person ; :text "I' in ttl_str
    assert ':has_active_entity :Noun' in ttl_str
    assert 'a :MovementTravelAndTransportation ; :text "to leave' in ttl_str
    # Output Turtle:
    # :Sentence_256879da-fc1c a :Sentence ; :offset 1 .
    # :Sentence_256879da-fc1c :text "I was not ready to leave." .
    # :Sentence_256879da-fc1c :summary "Individual was unprepared for departure." .
    # :Sentence_256879da-fc1c :sentiment "negative" .
    # :Sentence_256879da-fc1c :grade_level 3 .
    # :Sentence_256879da-fc1c :has_semantic :Event_ee6dcb8f-8f29 .
    # :Event_ee6dcb8f-8f29 a :ReadinessAndAbility ; :negated true ; :text "was not ready" .
    # :Noun_0f788fd6-074e a :Person ; :text "I" ; rdfs:label "I" .
    # :Event_ee6dcb8f-8f29 :has_active_entity :Noun_0f788fd6-074e .
    # :Sentence_256879da-fc1c :has_semantic :Event_f1d5e19a-cca3 .
    # :Event_f1d5e19a-cca3 a :MovementTravelAndTransportation ; :text "to leave" .
    # :Event_f1d5e19a-cca3 :has_active_entity :Noun_0f788fd6-074e .'


def test_pobj_semantics():
    sentence_instances, quotation_instances, quoted_strings = parse_narrative(text_pobj_semantics)
    success, index, graph_ttl = create_graph(sentence_instances, quotation_instances, 3, repo)
    ttl_str = str(graph_ttl)
    assert ':Avoidance' in ttl_str or ':AggressiveCriminalOrHostileAct' in ttl_str     # escape
    assert 'a :Person ; :text "The robber' in ttl_str
    assert ':has_active_entity :Noun' in ttl_str
    assert 'a :AidAndAssistance ; :text "the aid of the local police' in ttl_str
    assert ':has_instrument :Noun' in ttl_str
    # Output Turtle:
    # :Sentence_4a8274ff-3854 a :Sentence ; :offset 1 .
    # :Sentence_4a8274ff-3854 :text "The robber escaped with the aid of the local police." .
    # :Sentence_4a8274ff-3854 :summary "Robber escaped with assistance from local police." .
    # :Sentence_4a8274ff-3854 :sentiment "negative" .
    # :Sentence_4a8274ff-3854 :grade_level 5 .
    # :Sentence_4a8274ff-3854 :rhetorical_device "hyperbole" .
    # :Sentence_4a8274ff-3854 :rhetorical_device_hyperbole "The phrase \'with the aid of the local police\'
    #     suggests an exaggerated scenario where police, who are typically expected to prevent such crimes, are
    #     instead helping a robber, which is an unlikely and exaggerated situation." .
    # :Sentence_4a8274ff-3854 :has_semantic :Event_4b8d2566-524f .
    # :Event_4b8d2566-524f a :AggressiveCriminalOrHostileAct, :Causation ;
    #     :text "escaped with the aid of the local police" .
    # :Noun_bc4e012e-20a4 a :Person ; :text "The robber" ; rdfs:label "The robber" .
    # :Event_4b8d2566-524f :has_active_entity :Noun_bc4e012e-20a4 .
    # :Noun_1432e54f-96aa a :AidAndAssistance ; :text "the aid of the local police" ;
    #     rdfs:label "the aid of the local police" .
    # :Event_4b8d2566-524f :has_instrument :Noun_1432e54f-96aa .


def test_multiple_subjects():
    sentence_instances, quotation_instances, quoted_strings = parse_narrative(text_multiple_subjects)
    success, index, graph_ttl = create_graph(sentence_instances, quotation_instances, 3, repo)
    ttl_str = str(graph_ttl)
    assert ':DisagreementAndDispute' in ttl_str
    assert 'a :Person, :Collection ; :text "Jane and John' in ttl_str
    assert ':has_active_entity :Noun' in ttl_str
    # Output Turtle:
    # :Sentence_a903fc4c-13a6 a :Sentence ; :offset 1 .
    # :Sentence_a903fc4c-13a6 :text "Jane and John had a serious difference of opinion." .
    # :Sentence_a903fc4c-13a6 :mentions :Jane .
    # :Sentence_a903fc4c-13a6 :mentions :John .
    # :Sentence_a903fc4c-13a6 :summary "Jane and John disagreed seriously." .
    # :Sentence_a903fc4c-13a6 :sentiment "negative" .
    # :Sentence_a903fc4c-13a6 :grade_level 5 .
    # :Sentence_a903fc4c-13a6 :has_semantic :Event_eb8c2376-2bad .
    # :Event_eb8c2376-2bad a :DisagreementAndDispute ; :text "had" .
    # :Noun_dea13795-fa11 a :Person, :Collection ; :text "Jane and John" ; rdfs:label "Jane and John" .
    # :Event_eb8c2376-2bad :has_active_entity :Noun_dea13795-fa11 .
    # :Noun_1ae60ea7-e790 a :Change ; :text "a serious difference of opinion" ;
    #     rdfs:label "a serious difference of opinion" .     # TODO: Should be :DisagreementAndDispute
    # :Event_eb8c2376-2bad :has_topic :Noun_1ae60ea7-e790 .


def test_multiple_xcomp():
    sentence_instances, quotation_instances, quoted_strings = parse_narrative(text_multiple_xcomp)
    success, index, graph_ttl = create_graph(sentence_instances, quotation_instances, 3, repo)
    ttl_str = str(graph_ttl)
    assert ':ArtAndEntertainmentEvent' in ttl_str
    assert ':BodilyAct' in ttl_str
    assert ':has_active_entity :John' in ttl_str
    # Output Turtle:
    # :Sentence_41ad12a0-b8af a :Sentence ; :offset 1 .
    # :Sentence_41ad12a0-b8af :text "John liked to ski and to swim." .
    # :Sentence_41ad12a0-b8af :mentions :John .
    # :Sentence_41ad12a0-b8af :summary "John enjoys skiing and swimming." .
    # :Sentence_41ad12a0-b8af :sentiment "positive" .
    # :Sentence_41ad12a0-b8af :grade_level 3 .
    # :Sentence_41ad12a0-b8af :has_semantic :Event_64c5325e-c491 .
    # :Event_64c5325e-c491 a :ArtAndEntertainmentEvent, :BodilyAct ; :text "liked to ski and to swim" .
    # :Event_64c5325e-c491 :has_active_entity :John .
    # :Event_64c5325e-c491 :has_active_entity :John .
    # :Noun_7528b04c-dff6 a :ArtAndEntertainmentEvent ; :text "to ski" ; rdfs:label "to ski" .
    # :Event_64c5325e-c491 :has_topic :Noun_7528b04c-dff6 .
    # :Noun_256f3abf-cd3f a :ArtAndEntertainmentEvent ; :text "to swim" ; rdfs:label "to swim" .
    # :Event_64c5325e-c491 :has_topic :Noun_256f3abf-cd3f .


def test_location_hierarchy():
    sentence_instances, quotation_instances, quoted_strings = parse_narrative(text_location_hierarchy)
    success, index, graph_ttl = create_graph(sentence_instances, quotation_instances, 3, repo)
    ttl_str = str(graph_ttl)
    assert ':mentions geo:2658434' in ttl_str        # Switzerland
    assert 'a :EnvironmentAndCondition' in ttl_str
    assert 'a :Location ; :text "Switzerland' in ttl_str
    assert ':has_topic :Noun' in ttl_str
    # Output Turtle:
    # :Sentence_3b7c91fd-8120 a :Sentence ; :offset 1 .
    # :Sentence_3b7c91fd-8120 :text "Switzerland\'s mountains are magnificent." .
    # :Sentence_3b7c91fd-8120 :mentions geo:2658434 .
    # :Sentence_3b7c91fd-8120 :summary "Switzerland\'s mountains described as magnificent." .
    # :Sentence_3b7c91fd-8120 :sentiment "positive" .
    # :Sentence_3b7c91fd-8120 :grade_level 3 .
    # :Sentence_3b7c91fd-8120 :has_semantic :Event_dfcfe767-3501 .
    # :Event_dfcfe767-3501 a :EnvironmentAndCondition ; :text "are magnificent" .
    # :Noun_ecae7c6b-9b2c a :Location ; :text "Switzerland\'s mountains" ; rdfs:label "Switzerland\'s mountains" .
    # :Event_dfcfe767-3501 :has_topic :Noun_ecae7c6b-9b2c .


def test_weather():
    sentence_instances, quotation_instances, quoted_strings = parse_narrative(text_weather)
    success, index, graph_ttl = create_graph(sentence_instances, quotation_instances, 3, repo)
    ttl_str = str(graph_ttl)
    assert ':mentions :Hurricane_Otis' in ttl_str and ':mentions :Acapulco' in ttl_str
    assert ':has_active_entity :Hurricane_Otis' in ttl_str
    assert ':has_location :Acapulco' in ttl_str
    assert 'a :EnvironmentalOrEcologicalEvent' in ttl_str
    assert ':has_affected_entity :Acapulco' in ttl_str
    # Output Turtle:
    # :Sentence_1422e97c-1843 a :Sentence ; :offset 1 .
    # :Sentence_1422e97c-1843 :text "Hurricane Otis severely damaged Acapulco." .
    # :Hurricane_Otis :text "Hurricane Otis" .
    # :Hurricane_Otis a :EnvironmentalOrEcologicalEvent .
    # :Hurricane_Otis rdfs:label "Otis", "Hurricane Otis" .
    # :Hurricane_Otis rdfs:comment "From Wikipedia (wikibase_item: Q123178445): \'Hurricane Otis was a compact
    #     but very powerful tropical cyclone which made a devastating landfall in October 2023 near Acapulco
    #     as a Category 5 hurricane...\'" .
    # :Hurricane_Otis :external_link "https://en.wikipedia.org/wiki/Hurricane_Otis" .
    # :Hurricane_Otis :external_identifier "Q123178445" .
    # :Acapulco :text "Acapulco" .
    # :Acapulco a :OrganizationalEntity, :Correction .
    # :Acapulco rdfs:label "Acapulco de Juarez", "Acapulco de Juárez", "Acapulco de julio", "Acapulco, Guerrero",
    #     "Acapulco" .
    # :Acapulco rdfs:comment "From Wikipedia (wikibase_item: Q81398): \'Acapulco de Ju?rez, commonly called
    #     Acapulco, Guerrero, is a city and major seaport in the state of Guerrero on the Pacific Coast of Mexico,
    #     380 kilometres (240 mi) south of Mexico City....\'" .
    # :Acapulco :external_link "https://en.wikipedia.org/wiki/Acapulco" .
    # :Acapulco :external_identifier "Q81398" .
    # :Sentence_1422e97c-1843 :mentions :Hurricane_Otis .
    # :Sentence_1422e97c-1843 :mentions :Acapulco .
    # :Sentence_1422e97c-1843 :summary "Hurricane Otis severely damaged Acapulco." .
    # :Sentence_1422e97c-1843 :sentiment "negative" .
    # :Sentence_1422e97c-1843 :grade_level 5 .
    # :Sentence_1422e97c-1843 :has_semantic :Event_a3e3982a-0d31 .
    # :Event_a3e3982a-0d31 a :EnvironmentalOrEcologicalEvent ; :text "severely damaged" .
    # :Event_a3e3982a-0d31 :has_active_entity :Hurricane_Otis .
    # :Event_a3e3982a-0d31 :has_cause :Hurricane_Otis .
    # :Event_a3e3982a-0d31 :has_affected_entity :Acapulco .
    # :Event_a3e3982a-0d31 :has_location :Acapulco .


def test_coref():
    sentence_instances, quotation_instances, quoted_strings = parse_narrative(text_coref)
    success, index, graph_ttl = create_graph(sentence_instances, quotation_instances, 3, repo)
    ttl_str = str(graph_ttl)
    assert 'a :AgricultureApicultureAndAquacultureEvent' in ttl_str     # cutting roses
    assert ':has_active_entity :Heidi' in ttl_str
    assert 'a :Plant ; :text "roses' in ttl_str
    assert 'a :Cognition ; :text "saw' in ttl_str or 'a :SensoryPerception ; :text "saw' in ttl_str
    assert ':has_active_entity :Anna' in ttl_str     # seeing
    assert ':has_topic :Noun' in ttl_str             # Heidi cutting roses
    assert 'a :Cognition ; :negated true ; :text "did not recognize' in ttl_str
    assert ':has_topic :Heidi' in ttl_str
    # Output Turtle:
    # :Sentence_7602fa71-cefe a :Sentence ; :offset 1 .
    # :Sentence_7602fa71-cefe :text "Anna saw Heidi cut the roses, but she did not recognize that it was Heidi
    #     who cut the roses." .
    # :Sentence_7602fa71-cefe :mentions :Anna .
    # :Sentence_7602fa71-cefe :mentions :Heidi .
    # :Sentence_7602fa71-cefe :mentions :Heidi .
    # :Sentence_7602fa71-cefe :summary "Anna observed Heidi cutting roses but did not recognize Heidi." .
    # :Sentence_7602fa71-cefe :sentiment "neutral" .
    # :Sentence_7602fa71-cefe :grade_level 5 .
    # :Sentence_7602fa71-cefe :has_semantic :Event_a1245eec-41bc .
    # :Event_a1245eec-41bc a :Searching ; :text "observed" .      # TODO: Should be :SensoryPerception or :Cognition
    # :Event_a1245eec-41bc :has_active_entity :Anna .
    # :Noun_9c8487ce-9da3 a :AgricultureApicultureAndAquacultureEvent ; :text "Heidi cutting roses" ;
    #     rdfs:label "Heidi cutting roses" .
    # :Event_a1245eec-41bc :has_topic :Noun_9c8487ce-9da3 .
    # :Sentence_7602fa71-cefe :has_semantic :Event_27f7b518-d261 .
    # :Event_27f7b518-d261 a :BodilyAct ; :text "cutting" .
    # :Event_27f7b518-d261 :has_active_entity :Heidi .
    # :Noun_719b3ffb-5478 a :Plant ; :text "roses" ; rdfs:label "roses" .
    # :Event_27f7b518-d261 :has_affected_entity :Noun_719b3ffb-5478 .
    # :Sentence_7602fa71-cefe :has_semantic :Event_8307597d-0eca .
    # TODO: Should be :Cognition, not :CommunicationAndSpeechAct
    # :Event_8307597d-0eca a :CommunicationAndSpeechAct ; :negated true ; :text "did not recognize" .
    # :Event_8307597d-0eca :has_active_entity :Anna .
    # :Event_8307597d-0eca :has_topic :Heidi .


def test_quotation():
    sentence_instances, quotation_instances, quoted_strings = parse_narrative(text_quotation)
    success, index, graph_ttl = create_graph(sentence_instances, quotation_instances, 3, repo)
    ttl_str = str(graph_ttl)
    print(ttl_str)
    assert 'a :CommunicationAndSpeechAct ; :text "said' in ttl_str
    assert ':has_active_entity :Jane' in ttl_str
    assert ':has_topic :Quotation0' in ttl_str
    assert ':Quotation0 :attributed_to :Jane' in ttl_str
    # Output Turtle:
    # :Sentence_96e29b8a-5449 a :Sentence ; :offset 1 .
    # :Sentence_96e29b8a-5449 :text "Jane said, [Quotation0]" .
    # :Sentence_96e29b8a-5449 :has_component :Quotation0 .
    # :Sentence_96e29b8a-5449 :mentions :NVIDIA .
    # :Sentence_96e29b8a-5449 :mentions :Jane .
    # :Sentence_96e29b8a-5449 :summary "Jane spoke, content unspecified." .
    # :Sentence_96e29b8a-5449 :sentiment "neutral" .
    # :Sentence_96e29b8a-5449 :grade_level 4 .
    # :Sentence_96e29b8a-5449 :has_semantic :Event_f9f4204d-3381 .
    # :Event_f9f4204d-3381 a :CommunicationAndSpeechAct ; :text "said" .
    # :Event_f9f4204d-3381 :has_active_entity :Jane .
    # :Event_f9f4204d-3381 :has_topic :Quotation0 .
    # :Quotation0 a :Quote ; :text "I want to work for NVIDIA." .
    # :Quotation0 :attributed_to :Jane .
    # :Quotation0 :summary "Individual expresses desire to work for NVIDIA." .
    # :Quotation0 :sentiment "positive" .
    # :Quotation0 :grade_level 5 .
