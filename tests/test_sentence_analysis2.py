import pytest
from dna.create_narrative_turtle import create_graph
from dna.nlp import parse_narrative

# Latest execution: test_causation failed; 1 of 17

text_multiple_entities = 'Liz Cheney claimed that Trump is promoting an insidious lie about the recent ' \
                         'FBI raid of his Mar-a-Lago residence.'
text_multiple_verbs = 'Sue is an attorney but still lies.'
text_aux_pobj = 'John got rid of the debris.'
text_idiom_amod = "John turned a blind eye to Mary's infidelity."
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
text_quotation = 'Jane said, "I want to work for NVIDIA. My interview is tomorrow."'
text_rule = "You shall not kill."
text_causation = "Yesterday Holly was running a marathon when she twisted her ankle. David had pushed her."

repo = 'foo'

# Note that it is unlikely that all tests will complete successfully since event semantics can be
# interpreted/reported in multiple ways
# 80%+ of the tests should pass


def test_multiple_entities():
    sentence_classes, quotation_classes = parse_narrative(text_multiple_entities)
    graph_results = create_graph(sentence_classes, quotation_classes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert 'loaded language' in ttl_str
    assert ':CommunicationAndSpeechAct' in ttl_str           # claimed
    assert ':has_active_entity :Liz_Cheney' in ttl_str
    assert ':has_topic :Donald_Trump'
    assert ':DeceptionAndDishonesty' in ttl_str              # promoting lie
    assert ':has_active_entity :Donald_Trump' in ttl_str
    assert ':LawEnforcement' in ttl_str                      # FBI raid
    assert ':has_location :Noun' in ttl_str or ':has_topic :Noun' in ttl_str    # Trump's residence or raid as topic
    # Output Turtle:
    # :Sentence_04223321-01a5 a :Sentence ; :offset 1 .
    # :Sentence_04223321-01a5 :text "Liz Cheney claimed that Trump is promoting an insidious lie about the recent FBI
    #     raid of his Mar-a-Lago residence." .
    # :Sentence_04223321-01a5 :mentions :Liz_Cheney .
    # :Sentence_04223321-01a5 :mentions :Donald_Trump .
    # :Sentence_04223321-01a5 :mentions :FBI .
    # :Sentence_04223321-01a5 :mentions :Mar_a_Lago .
    # :Sentence_04223321-01a5 :grade_level 10 .
    # :Sentence_04223321-01a5 :rhetorical_device "loaded language" .
    # :Sentence_04223321-01a5 :rhetorical_device_loaded_language "The phrase \'insidious lie\' uses loaded language
    #     with strong connotations that invoke emotions and judgments about the nature of the lie being described." .
    # :Sentence_04223321-01a5 :has_semantic :Event_45dac516-9387 .
    # :Event_45dac516-9387 rdfs:label "Claiming that Trump is promoting an insidious lie" .
    # :Event_45dac516-9387 a :CommunicationAndSpeechAct ; :confidence-CommunicationAndSpeechAct 100 .
    # :Event_45dac516-9387 a :DeceptionAndDishonesty ; :confidence-DeceptionAndDishonesty 100 .
    # :Event_45dac516-9387 :has_active_entity :Liz_Cheney .
    # :Event_45dac516-9387 :has_topic :Donald_Trump .
    # :Noun_744fd4fa-271d a :DeceptionAndDishonesty ; :text "an insidious lie" ; rdfs:label "an insidious lie;
    #     false statement" ; :confidence 100 .
    # :Event_45dac516-9387 :has_topic :Noun_744fd4fa-271d .
    # :Sentence_04223321-01a5 :has_semantic :Event_16181199-e39f .
    # :Event_16181199-e39f rdfs:label "Promoting an insidious lie about the recent FBI raid" .
    # :Event_16181199-e39f a :CommunicationAndSpeechAct ; :confidence-CommunicationAndSpeechAct 100 .
    # :Event_16181199-e39f a :DeceptionAndDishonesty ; :confidence-DeceptionAndDishonesty 100 .
    # :Event_16181199-e39f :has_active_entity :Donald_Trump .
    # :Noun_aa70aee6-ec59 a :LawEnforcement ; :text "the recent FBI raid of Trump\'s Mar-a-Lago residence" ;
    #     rdfs:label "the recent FBI raid of Trump\'s Mar-a-Lago residence; law enforcement action" ; :confidence 100 .
    # :Event_16181199-e39f :has_topic :Noun_aa70aee6-ec59 .


def test_multiple_verbs():
    sentence_classes, quotation_classes = parse_narrative(text_multiple_verbs)
    graph_results = create_graph(sentence_classes, quotation_classes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':EnvironmentAndCondition' in ttl_str
    assert ':has_context :Sue' in ttl_str
    assert ':LineOfBusiness ; :text "attorney' in ttl_str and ':has_aspect :Noun' in ttl_str
    assert ':DeceptionAndDishonesty' in ttl_str
    assert ':has_active_entity :Sue' in ttl_str
    # Output Turtle:
    # :Sentence_c1bdf749-a2de a :Sentence ; :offset 1 .
    # :Sentence_c1bdf749-a2de :text "Sue is an attorney but still lies." .
    # :Sentence_c1bdf749-a2de :mentions :Sue .
    # :Sentence_c1bdf749-a2de :grade_level 8 .
    # :Sentence_c1bdf749-a2de :rhetorical_device "ad hominem" .
    # :Sentence_c1bdf749-a2de :rhetorical_device_ad_hominem "The sentence uses ad hominem by implying that Sue,
    #     despite being an attorney, lies, which verbally demeans her character." .
    # :Sentence_c1bdf749-a2de :has_semantic :Event_5052a9c6-2b32 .
    # :Event_5052a9c6-2b32 rdfs:label "Sue being an attorney" .
    # :Event_5052a9c6-2b32 a :EnvironmentAndCondition ; :confidence-EnvironmentAndCondition 100 .
    # :Event_5052a9c6-2b32 :has_context :Sue .
    # :Noun_d4744908-b7dd a :LineOfBusiness ; :text "attorney" ; rdfs:label "attorney; profession" ; :confidence 100 .
    # :Event_5052a9c6-2b32 :has_aspect :Noun_d4744908-b7dd .
    # :Sentence_c1bdf749-a2de :has_semantic :Event_1c90da10-302d .
    # :Event_1c90da10-302d rdfs:label "Sue lying" .
    # :Event_1c90da10-302d a :DeceptionAndDishonesty ; :confidence-DeceptionAndDishonesty 100 .
    # :Event_1c90da10-302d :has_active_entity :Sue .


def test_aux_pobj():
    sentence_classes, quotation_classes = parse_narrative(text_aux_pobj)
    graph_results = create_graph(sentence_classes, quotation_classes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':RemovalAndRestriction' in ttl_str
    assert ':has_active_entity :John' in ttl_str
    assert ':WasteAndResidue ; :text "debris' in ttl_str
    assert ':has_topic :Noun' in ttl_str
    # Output Turtle:
    # :Sentence_08f5bc0d-b908 a :Sentence ; :offset 1 .
    # :Sentence_08f5bc0d-b908 :text "John got rid of the debris." .
    # :Sentence_08f5bc0d-b908 :mentions :John .
    # :Sentence_08f5bc0d-b908 :grade_level 3 .
    # :Sentence_08f5bc0d-b908 :has_semantic :Event_6bb9d997-7064 .
    # :Event_6bb9d997-7064 rdfs:label "John getting rid of the debris" .
    # :Event_6bb9d997-7064 a :RemovalAndRestriction ; :confidence-RemovalAndRestriction 100 .
    # :Event_6bb9d997-7064 :has_active_entity :John .
    # :Noun_5ffec85f-9371 a :WasteAndResidue ; :text "debris" ; rdfs:label "debris; material being removed" ;
    #     :confidence 100 .
    # :Event_6bb9d997-7064 :has_topic :Noun_5ffec85f-9371 .


def test_idiom_amod():
    sentence_classes, quotation_classes = parse_narrative(text_idiom_amod)
    graph_results = create_graph(sentence_classes, quotation_classes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert "allusion" in ttl_str
    assert ':Avoidance' in ttl_str
    assert ':has_active_entity :John' in ttl_str
    assert ':DeceptionAndDishonesty' in ttl_str
    assert ':has_topic :Noun' in ttl_str
    # Output Turtle:
    # :Sentence_99ed5243-bcae a :Sentence ; :offset 1 .
    # :Sentence_99ed5243-bcae :text "John turned a blind eye to Mary\'s infidelity." .
    # :Sentence_99ed5243-bcae :mentions :John .
    # :Sentence_99ed5243-bcae :mentions :Mary .
    # :Sentence_99ed5243-bcae :grade_level 8 .
    # :Sentence_99ed5243-bcae :rhetorical_device "allusion" .
    # :Sentence_99ed5243-bcae :rhetorical_device_allusion "The phrase \'turned a blind eye\' is an allusion to the
    #     historical anecdote about Admiral Horatio Nelson, who purportedly used his blind eye to look through his
    #     telescope and ignore signals to withdraw from battle. This allusion is used to convey the idea of
    #     deliberately ignoring something." .
    # :Sentence_99ed5243-bcae :has_semantic :Event_39a657c6-f611 .
    # :Event_39a657c6-f611 rdfs:label "Turning a blind eye to infidelity" .
    # :Event_39a657c6-f611 a :Avoidance ; :confidence-Avoidance 100 .
    # :Event_39a657c6-f611 :has_active_entity :John .
    # :Noun_51c4c2aa-d444 a :DeceptionAndDishonesty ; :text "Mary\'s infidelity" ; rdfs:label "Mary\'s infidelity;
    #     act of being unfaithful" ; :confidence 100 .
    # :Event_39a657c6-f611 :has_topic :Noun_51c4c2aa-d444 .
    # TODO: Report that Mary was the one who was not faithful


def test_complex_verb():
    sentence_classes, quotation_classes = parse_narrative(text_complex_verb)
    graph_results = create_graph(sentence_classes, quotation_classes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':End' in ttl_str or ':EconomyAndFinanceRelated' in ttl_str
    assert ':LineOfBusiness' in ttl_str or ':Location' in ttl_str      # store
    assert ':has_active_entity :Noun' in ttl_str
    # Output Turtle:
    # :Sentence_30758f68-7889 a :Sentence ; :offset 1 .
    # :Sentence_30758f68-7889 :text "The store went out of business on Tuesday." .
    # :Sentence_30758f68-7889 :grade_level 5 .
    # :Sentence_30758f68-7889 :has_semantic :Event_d7e93388-10f5 .
    # :Event_d7e93388-10f5 rdfs:label "The store going out of business" .
    # :Event_d7e93388-10f5 a :EconomyAndFinanceRelated ; :confidence-EconomyAndFinanceRelated 100 .
    # :Event_d7e93388-10f5 a :End ; :confidence-End 100 .
    # :Noun_af46b522-37c1 a :Location ; :text "The store" ; rdfs:label "The store; retail business" ; :confidence 100 .
    # :Event_d7e93388-10f5 :has_active_entity :Noun_af46b522-37c1 .


def test_neg_acomp_xcomp():
    sentence_classes, quotation_classes = parse_narrative(text_neg_acomp_xcomp)
    graph_results = create_graph(sentence_classes, quotation_classes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':Avoidance' in ttl_str
    assert ':ReadinessAndAbility' in ttl_str and ':negated-ReadinessAndAbility' in ttl_str
    assert ':has_active_entity :Jane' in ttl_str
    assert ':DeceptionAndDishonesty' in ttl_str
    assert ':has_topic :Noun' in ttl_str
    # Output Turtle:
    # :Sentence_20dedf06-3728 a :Sentence ; :offset 1 .
    # :Sentence_20dedf06-3728 :text "Jane is not able to stomach lies." .
    # :Sentence_20dedf06-3728 :mentions :Jane .
    # :Sentence_20dedf06-3728 :grade_level 6 .
    # :Sentence_20dedf06-3728 :has_semantic :Event_809482ed-f92b .
    # :Event_809482ed-f92b rdfs:label "Jane\'s inability to stomach lies" .
    # :Event_809482ed-f92b a :Avoidance ; :confidence-Avoidance 100 .
    # :Event_809482ed-f92b a :EmotionalResponse ; :confidence-EmotionalResponse 80 .
    # :Event_809482ed-f92b a :ReadinessAndAbility ; :confidence-ReadinessAndAbility 90 .
    # :Event_809482ed-f92b :negated-ReadinessAndAbility true .
    # :Event_809482ed-f92b :has_active_entity :Jane .
    # :Noun_a4a35293-8c59 a :DeceptionAndDishonesty ; :text "lies" ; rdfs:label "lies; false statements" ;
    #     :confidence 100 .
    # :Event_809482ed-f92b :has_topic :Noun_a4a35293-8c59 .

def test_non_person_subject():
    sentence_classes, quotation_classes = parse_narrative(text_non_person_subject)
    graph_results = create_graph(sentence_classes, quotation_classes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':Loss' in ttl_str
    assert ':EmotionalResponse' in ttl_str or ':Cognition' in ttl_str
    assert ':has_affected_entity :John' in ttl_str or ':has_topic :John' in ttl_str
    assert ':text "hopes' in ttl_str and ':has_topic :Noun' in ttl_str
    # Output Turtle:
    # :Sentence_a6c578b7-2bb1 a :Sentence ; :offset 1 .
    # :Sentence_a6c578b7-2bb1 :text "John\'s hopes were dashed." .
    # :Sentence_a6c578b7-2bb1 :mentions :John .
    # :Sentence_a6c578b7-2bb1 :grade_level 6 .
    # :Sentence_a6c578b7-2bb1 :has_semantic :Event_4b3ac46d-f737 .
    # :Event_4b3ac46d-f737 rdfs:label "John\'s hopes being dashed" .
    # :Event_4b3ac46d-f737 a :Loss ; :confidence-Loss 100 .
    # :Event_4b3ac46d-f737 a :EmotionalResponse ; :confidence-EmotionalResponse 80 .
    # :Noun_1ce2671e-f161 a :EmotionalResponse, :Collection ; :text "hopes" ; rdfs:label "hopes; John\'s aspirations" ;
    #     :confidence 90 .
    # :Event_4b3ac46d-f737 :has_topic :Noun_1ce2671e-f161 .
    # :Event_4b3ac46d-f737 :has_topic :John .      # TODO: Distinguish John as context or active
    # TODO: Better test possessives


def test_first_person():
    sentence_classes, quotation_classes = parse_narrative(text_first_person)
    graph_results = create_graph(sentence_classes, quotation_classes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':ReadinessAndAbility' in ttl_str and ':negated-ReadinessAndAbility' in ttl_str
    assert ':MovementTravelAndTransportation' in ttl_str
    assert ':Person ; :text "I' in ttl_str
    assert ':has_active_entity :Noun' in ttl_str
    # Output Turtle:
    # :Sentence_ab6948ed-5ef8 a :Sentence ; :offset 1 .
    # :Sentence_ab6948ed-5ef8 :text "I was not ready to leave." .
    # :Sentence_ab6948ed-5ef8 :grade_level 4 .
    # :Sentence_ab6948ed-5ef8 :has_semantic :Event_41371a86-c6fd .
    # :Event_41371a86-c6fd rdfs:label "Not being ready to leave" .
    # :Event_41371a86-c6fd a :ReadinessAndAbility ; :confidence-ReadinessAndAbility 100 .
    # :Event_41371a86-c6fd :negated-ReadinessAndAbility true .
    # :Event_41371a86-c6fd a :MovementTravelAndTransportation ; :confidence-MovementTravelAndTransportation 100 .
    # :Noun_d05e43d1-bbac a :Person ; :text "I" ; rdfs:label "I; the speaker" ; :confidence 99 .
    # :Event_41371a86-c6fd :has_active_entity :Noun_d05e43d1-bbac .


def test_pobj_semantics():
    sentence_classes, quotation_classes = parse_narrative(text_pobj_semantics)
    graph_results = create_graph(sentence_classes, quotation_classes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':Avoidance' in ttl_str     # escape
    assert ':Person ; :text "robber' in ttl_str
    assert ':has_active_entity :Noun' in ttl_str
    assert ':AidAndAssistance' in ttl_str
    assert ':has_topic :Noun' in ttl_str
    # Output Turtle:
    # :Sentence_f519d7a3-02a8 a :Sentence ; :offset 1 .
    # :Sentence_f519d7a3-02a8 :text "The robber escaped with the aid of the local police." .
    # :Sentence_f519d7a3-02a8 :grade_level 8 .
    # :Sentence_f519d7a3-02a8 :has_semantic :Event_b9920f44-6ecd .
    # :Event_b9920f44-6ecd rdfs:label "Escaping with the aid" .
    # :Event_b9920f44-6ecd a :Avoidance ; :confidence-Avoidance 100 .
    # :Noun_e7d99c25-be1f a :Person ; :text "robber" ; rdfs:label "robber; person committing theft" ; :confidence 100 .
    # :Event_b9920f44-6ecd :has_active_entity :Noun_e7d99c25-be1f .
    # :Noun_126c33ee-1843 a :AidAndAssistance ; :text "aid of the local police" ; rdfs:label "aid of the local
    #     police; assistance from law enforcement" ; :confidence 100 .
    # :Event_b9920f44-6ecd :has_topic :Noun_126c33ee-1843 .


def test_multiple_subjects():
    sentence_classes, quotation_classes = parse_narrative(text_multiple_subjects)
    graph_results = create_graph(sentence_classes, quotation_classes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':DisagreementAndDispute' in ttl_str
    assert ':has_active_entity :Jane' in ttl_str
    assert ':has_active_entity :John' in ttl_str
    # Output Turtle:
    # :Sentence_aeca6eda-673d a :Sentence ; :offset 1 .
    # :Sentence_aeca6eda-673d :text "Jane and John had a serious difference of opinion." .
    # :Sentence_aeca6eda-673d :mentions :Jane .
    # :Sentence_aeca6eda-673d :mentions :John .
    # :Sentence_aeca6eda-673d :grade_level 6 .
    # :Sentence_aeca6eda-673d :has_semantic :Event_009fbe06-2a35 .
    # :Event_009fbe06-2a35 rdfs:label "Having a serious difference of opinion" .
    # :Event_009fbe06-2a35 a :DisagreementAndDispute ; :confidence-DisagreementAndDispute 100 .
    # :Event_009fbe06-2a35 :has_active_entity :Jane .
    # :Event_009fbe06-2a35 :has_active_entity :John .


def test_multiple_xcomp():
    sentence_classes, quotation_classes = parse_narrative(text_multiple_xcomp)
    graph_results = create_graph(sentence_classes, quotation_classes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':EmotionalResponse' in ttl_str
    assert ':has_active_entity :John' in ttl_str
    assert ':BodilyAct ; :text "ski' in ttl_str
    assert ':BodilyAct ; :text "swim' in ttl_str
    assert ':has_topic :Noun' in ttl_str
    # Output Turtle:
    # :Sentence_4e071533-c700 a :Sentence ; :offset 1 .
    # :Sentence_4e071533-c700 :text "John liked to ski and to swim." .
    # :Sentence_4e071533-c700 :mentions :John .
    # :Sentence_4e071533-c700 :grade_level 3 .
    # :Sentence_4e071533-c700 :has_semantic :Event_3351c988-f8fe .
    # :Event_3351c988-f8fe rdfs:label "John liking to ski" .
    # :Event_3351c988-f8fe a :EmotionalResponse ; :confidence-EmotionalResponse 90 .
    # :Event_3351c988-f8fe :has_active_entity :John .
    # :Noun_7e684990-2a40 a :BodilyAct ; :text "ski" ; rdfs:label "ski; activity" ; :confidence 80 .
    # :Event_3351c988-f8fe :has_topic :Noun_7e684990-2a40 .
    # :Sentence_4e071533-c700 :has_semantic :Event_9cb490b7-50c3 .
    # :Event_9cb490b7-50c3 rdfs:label "John liking to swim" .
    # :Event_9cb490b7-50c3 a :EmotionalResponse ; :confidence-EmotionalResponse 90 .
    # :Event_9cb490b7-50c3 a :EmotionalResponse ; :confidence-EmotionalResponse 90 .
    # :Event_9cb490b7-50c3 :has_active_entity :John .
    # :Noun_cbdf55b9-651d a :BodilyAct ; :text "swim" ; rdfs:label "swim; activity" ; :confidence 100 .
    # :Event_9cb490b7-50c3 :has_topic :Noun_cbdf55b9-651d .


def test_location_hierarchy():
    sentence_classes, quotation_classes = parse_narrative(text_location_hierarchy)
    graph_results = create_graph(sentence_classes, quotation_classes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':mentions geo:2658434' in ttl_str        # Switzerland
    assert 'imagery' in ttl_str or 'exceptionalism' in ttl_str
    assert ':EnvironmentAndCondition' in ttl_str
    assert ':Location' in ttl_str and (':text "mountains' in ttl_str or ':text "Switzerland' in ttl_str)
    assert ':has_context :Noun' in ttl_str
    # Output Turtle:
    # :Sentence_d531cf03-d640 a :Sentence ; :offset 1 .
    # :Sentence_d531cf03-d640 :text "Switzerland\'s mountains are magnificent." .
    # :Sentence_d531cf03-d640 :mentions geo:2658434 .
    # :Sentence_d531cf03-d640 :grade_level 5 .
    # :Sentence_d531cf03-d640 :rhetorical_device "imagery" .
    # :Sentence_d531cf03-d640 :rhetorical_device_imagery "The sentence uses imagery by describing Switzerland\'s
    #     mountains as \'magnificent\', which paints a vivid picture and emotionally engages the reader." .
    # :Sentence_d531cf03-d640 :has_semantic :Event_d0df0f23-375f .
    # :Event_d0df0f23-375f rdfs:label "Switzerland\'s mountains being magnificent" .
    # :Event_d0df0f23-375f a :EnvironmentAndCondition ; :confidence-EnvironmentAndCondition 100 .
    # :Noun_301fa568-bb74 a :Location, :Collection ; :text "Switzerland\'s mountains" ; rdfs:label "Switzerland\'s
    #     mountains; Mountain range in Switzerland" ; :confidence 100 .
    # :Event_d0df0f23-375f :has_context :Noun_301fa568-bb74 .


def test_weather():
    sentence_classes, quotation_classes = parse_narrative(text_weather)
    graph_results = create_graph(sentence_classes, quotation_classes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':mentions :Hurricane_Otis' in ttl_str and ':mentions :Acapulco' in ttl_str
    assert ':EnvironmentalOrEcologicalEvent' in ttl_str or ':Change' in ttl_str
    assert ':has_active_entity :Hurricane_Otis' in ttl_str
    assert ':has_affected_entity :Acapulco' in ttl_str
    # Output Turtle:
    # :Sentence_b8076e9b-8a11 a :Sentence ; :offset 1 .
    # :Sentence_b8076e9b-8a11 :text "Hurricane Otis severely damaged Acapulco." .
    # :Sentence_b8076e9b-8a11 :mentions :Hurricane_Otis .
    # :Sentence_b8076e9b-8a11 :mentions :Acapulco .
    # :Sentence_b8076e9b-8a11 :grade_level 6 .
    # :Sentence_b8076e9b-8a11 :has_semantic :Event_49a583cb-0f7d .
    # :Event_49a583cb-0f7d rdfs:label "Hurricane Otis damaging Acapulco" .
    # :Event_49a583cb-0f7d a :Change ; :confidence-Change 80 .
    # :Event_49a583cb-0f7d :has_active_entity :Hurricane_Otis .
    # :Event_49a583cb-0f7d :has_affected_entity :Acapulco .


def test_coref():
    sentence_classes, quotation_classes = parse_narrative(text_coref)
    graph_results = create_graph(sentence_classes, quotation_classes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':SensoryPerception' in ttl_str                        # saw
    assert ':has_active_entity :Anna' in ttl_str
    assert ':Separation' in ttl_str or ':AgricultureApicultureAndAquacultureEvent' in ttl_str     # cutting
    assert ':has_active_entity :Heidi' in ttl_str
    assert ':Plant, :Collection ; :text "roses' in ttl_str
    assert ':has_affected_entity :Noun' in ttl_str or ':has_topic :Noun' in ttl_str
    assert ':Cognition' in ttl_str and ':Mistake' in ttl_str       # not recognize
    assert ':has_topic :Heidi' in ttl_str
    # Output Turtle:
    # :Sentence_4d33bf80-9677 a :Sentence ; :offset 1 .
    # :Sentence_4d33bf80-9677 :text "Anna saw Heidi cut the roses, but she did not recognize that it was Heidi who
    #     cut the roses." .
    # :Sentence_4d33bf80-9677 :mentions :Anna .
    # :Sentence_4d33bf80-9677 :mentions :Heidi .
    # :Sentence_4d33bf80-9677 :mentions :Heidi .
    # :Sentence_4d33bf80-9677 :grade_level 8 .
    # :Sentence_4d33bf80-9677 :has_semantic :Event_949373fc-415d .
    # :Event_949373fc-415d rdfs:label "Heidi cutting the roses" .
    # :Event_949373fc-415d a :Separation ; :confidence-Separation 100 .
    # :Event_949373fc-415d a :ProductionManufactureAndCreation ; :confidence-ProductionManufactureAndCreation 80 .
    # :Event_949373fc-415d :has_active_entity :Heidi .
    # :Noun_d22f9bde-218f a :Plant, :Collection ; :text "roses" ; rdfs:label "roses; flowers being cut" ;
    #     :confidence 100 .
    # :Event_949373fc-415d :has_topic :Noun_d22f9bde-218f .
    # :Sentence_4d33bf80-9677 :has_semantic :Event_53f06569-b0ec .
    # :Event_53f06569-b0ec rdfs:label "Anna seeing Heidi cut the roses" .
    # :Event_53f06569-b0ec a :SensoryPerception ; :confidence-SensoryPerception 100 .
    # :Event_53f06569-b0ec :has_active_entity :Anna .
    # :Noun_76bec105-4e40 a :BodilyAct ; :text "Heidi cutting the roses" ; rdfs:label "Heidi cutting the roses;
    #     event observed" ; :confidence 80 .
    # :Event_53f06569-b0ec :has_topic :Noun_76bec105-4e40 .
    # :Sentence_4d33bf80-9677 :has_semantic :Event_de724692-a236 .
    # :Event_de724692-a236 rdfs:label "Anna not recognizing Heidi" .
    # :Event_de724692-a236 a :Cognition ; :confidence-Cognition 90 .
    # :Event_de724692-a236 a :Mistake ; :confidence-Mistake 80 .
    # :Event_de724692-a236 :has_active_entity :Anna .
    # :Event_de724692-a236 :has_topic :Heidi .


def test_quotation():
    sentence_classes, quotation_classes = parse_narrative(text_quotation)
    graph_results = create_graph(sentence_classes, quotation_classes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':mentions :NVIDIA' in ttl_str
    # said and want
    assert ':Attempt' in ttl_str and (':CommunicationAndSpeechAct' in ttl_str or ':Affiliation' in ttl_str)
    assert ':has_active_entity :Jane' in ttl_str
    assert ':has_topic :NVIDIA' in ttl_str or ':affiliated_with :NVIDIA' in ttl_str
    assert ':future true' in ttl_str
    assert ':MeetingAndEncounter' in ttl_str       # interview
    assert 'a :Quote ; :text "I want to work for NVIDIA. My interview is tomorrow' in ttl_str
    assert ':attributed_to :Jane' in ttl_str
    # Output Turtle:
    # :Sentence_a2d6d972-0754 a :Sentence ; :offset 1 .
    # :Sentence_a2d6d972-0754 :text "Jane said, \'I want to work for NVIDIA." .
    # :NVIDIA :text "NVIDIA" .        # Example showing info retrieved from Wikidata
    # :NVIDIA a :OrganizationalEntity, :Correction .
    # :NVIDIA rdfs:label "Nvidia", "NVDA", "Nvidia Corp.", "Nvidia Corporation", "NVIDIA" .
    # :NVIDIA rdfs:comment "From Wikipedia (wikibase_item: Q182477): \'Nvidia Corporation is an American multinational
    #     corporation and technology company headquartered in Santa Clara, California, and incorporated in Delaware.
    #     It is a software and fabless company which designs and supplies graphics processing units (GPUs), application
    #     programming interfaces (APIs) for data science and high-performance computing, as well as system on a chip
    #     units (SoCs) for the mobile computing and automotive market. Nvidia is also a dominant supplier of
    #     artificial intelligence (AI) hardware and software.\'" .
    # :NVIDIA :external_link "https://en.wikipedia.org/wiki/Nvidia" .
    # :NVIDIA :external_identifier "Q182477" .
    # :Sentence_a2d6d972-0754 :mentions :Jane .
    # :Sentence_a2d6d972-0754 :mentions :NVIDIA .
    # :Sentence_a2d6d972-0754 :grade_level 5 .
    # :Sentence_d0a7456c-6b43 a :Sentence ; :offset 2 .
    # :Sentence_d0a7456c-6b43 :text "My interview is tomorrow.\'" .
    # :Sentence_d0a7456c-6b43 :grade_level 3 .
    # :Sentence_a2d6d972-0754 :has_semantic :Event_c455991f-0a38 .
    # :Event_c455991f-0a38 rdfs:label "Jane wanting to work for NVIDIA" .
    # :Event_c455991f-0a38 :future true .
    # :Event_c455991f-0a38 a :Affiliation ; :confidence-Affiliation 80 .
    # :Event_c455991f-0a38 a :Attempt ; :confidence-Attempt 90 .
    # :Event_c455991f-0a38 :has_active_entity :Jane .
    # :Event_c455991f-0a38 :affiliated_with :NVIDIA .
    # :Sentence_a2d6d972-0754 :has_semantic :Event_2753a2b7-9a24 .
    # :Event_2753a2b7-9a24 rdfs:label "Jane\'s interview being tomorrow" .
    # :Event_2753a2b7-9a24 :future true .
    # :Event_2753a2b7-9a24 a :MeetingAndEncounter ; :confidence-MeetingAndEncounter 90 .
    # :Noun_bc6de132-c25c a :CommunicationAndSpeechAct ; :text "Jane\'s interview" ; rdfs:label "Jane\'s interview;
    #     scheduled meeting" ; :confidence 90 .
    # :Event_2753a2b7-9a24 :has_topic :Noun_bc6de132-c25c .
    # :Quotation_21850031-c3bd a :Quote ; :text "I want to work for NVIDIA. My interview is tomorrow." .
    # :Quotation_21850031-c3bd :attributed_to :Jane .
    # :Quotation_21850031-c3bd :grade_level 5 .


def test_rule():
    sentence_classes, quotation_classes = parse_narrative(text_rule)
    graph_results = create_graph(sentence_classes, quotation_classes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':AggressiveCriminalOrHostileAct' in ttl_str and ':negated-AggressiveCriminalOrHostileAct' in ttl_str
    assert ':RequirementAndDependence' in ttl_str
    # Output Turtle:
    # :Sentence_7f34cee7-9537 a :Sentence ; :offset 1 .
    # :Sentence_7f34cee7-9537 :text "You shall not kill." .
    # :Sentence_7f34cee7-9537 :grade_level 5 .
    # :Sentence_7f34cee7-9537 :has_semantic :Event_7a3e2350-bd2c .
    # :Event_7a3e2350-bd2c rdfs:label "Killing" .
    # :Event_7a3e2350-bd2c :future true .
    # :Event_7a3e2350-bd2c a :RequirementAndDependence ; :confidence-RequirementAndDependence 95 .
    # :Event_7a3e2350-bd2c a :AggressiveCriminalOrHostileAct ; :confidence-AggressiveCriminalOrHostileAct 100 .
    # :Event_7a3e2350-bd2c :negated-AggressiveCriminalOrHostileAct true .


def test_causation():
    sentence_classes, quotation_classes = parse_narrative(text_causation)
    graph_results = create_graph(sentence_classes, quotation_classes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':BodilyAct' in ttl_str or ':ArtAndEntertainmentEvent' in ttl_str
    assert ':has_active_entity :Holly' in ttl_str
    assert ':HealthAndDiseaseRelated' in ttl_str
    assert ':ComponentPart ; :text "ankle' in ttl_str     # TODO: Error, missing
    assert ':has_topic :Noun' in ttl_str                  # twisted ankle
    assert ':ImpactAndContact' in ttl_str
    assert ':has_active_entity :David' in ttl_str
    assert ':has_affected_entity :Holly' in ttl_str
    # Output Turtle:
    # :Sentence_1d290d69-c8d4 a :Sentence ; :offset 1 .
    # :Sentence_1d290d69-c8d4 :text "Yesterday Holly was running a marathon when she twisted her ankle." .
    # :Sentence_1d290d69-c8d4 :mentions :Holly .
    # :Sentence_1d290d69-c8d4 :grade_level 6 .
    # :Sentence_a4ccdbaf-e889 a :Sentence ; :offset 2 .
    # :Sentence_a4ccdbaf-e889 :text "David had pushed her." .
    # :Sentence_a4ccdbaf-e889 :mentions :David .
    # :Sentence_a4ccdbaf-e889 :grade_level 3 .
    # :Sentence_1d290d69-c8d4 :has_semantic :Event_88bb2ddd-0401 .
    # :Event_88bb2ddd-0401 rdfs:label "Holly running a marathon" .
    # :Event_88bb2ddd-0401 a :ArtAndEntertainmentEvent ; :confidence-ArtAndEntertainmentEvent 100 .
    # :Event_88bb2ddd-0401 a :BodilyAct ; :confidence-BodilyAct 90 .
    # :Event_88bb2ddd-0401 a :ArtAndEntertainmentEvent ; :confidence-ArtAndEntertainmentEvent 100 .
    # :Event_88bb2ddd-0401 :has_active_entity :Holly .
    # :Sentence_1d290d69-c8d4 :has_semantic :Event_7d092b63-66e1 .
    # :Event_7d092b63-66e1 rdfs:label "Holly twisting her ankle" .
    # :Event_7d092b63-66e1 a :HealthAndDiseaseRelated ; :confidence-HealthAndDiseaseRelated 100 .
    # :Event_7d092b63-66e1 a :Change ; :confidence-Change 80 .
    # :Event_7d092b63-66e1 :has_active_entity :Holly .
    # :Sentence_a4ccdbaf-e889 :has_semantic :Event_0a512edd-dbd5 .
    # :Event_0a512edd-dbd5 rdfs:label "David pushing Holly" .
    # :Event_0a512edd-dbd5 a :ImpactAndContact ; :confidence-ImpactAndContact 100 .
    # :Event_0a512edd-dbd5 a :BodilyAct ; :confidence-BodilyAct 90 .
    # :Event_0a512edd-dbd5 :has_active_entity :David .
    # :Event_0a512edd-dbd5 :has_affected_entity :Holly .
