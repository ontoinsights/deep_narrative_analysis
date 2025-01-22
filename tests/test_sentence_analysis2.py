import pytest
from dna.create_narrative_turtle import create_graph
from dna.nlp import parse_narrative

# Latest execution, Dec 15: test_neg_acomp_xcomp failed; 1 of 17

text_possessive = "Joe's foot hit the table."
text_communication = 'Liz Cheney claimed that Trump is promoting an insidious lie about the recent ' \
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


def test_possessive():
    sentence_classes, quotation_classes = parse_narrative(text_possessive)
    graph_results = create_graph(sentence_classes, quotation_classes, text_possessive,
                                 ':Narrative_foo', [],5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':ImpactAndContact' in ttl_str
    assert (':has_active_entity :Noun' in ttl_str and ':clarifying_reference :Joe' in ttl_str) or \
           ':has_active_entity :Joe' in ttl_str
    assert ':ComponentPart' in ttl_str and (':text "Joe' in ttl_str or ':text "foot' in ttl_str)
    assert ':Resource ; :text "table' in ttl_str
    assert ':has_affected_entity :Noun' in ttl_str
    # Output Turtle:
    # :Narrative_foo :has_component :Sentence_82a391ff-25b1 .
    # :Sentence_82a391ff-25b1 a :Sentence ; :offset 1 .
    # :Sentence_82a391ff-25b1 :text "Joe\'s foot hit the table." .
    # :Sentence_82a391ff-25b1 :mentions :Joe .
    # :Sentence_82a391ff-25b1 :grade_level 3 .
    # :Narrative_foo :describes :NarrativeEvent_bb2d1f80-eee7 .
    # :NarrativeEvent_bb2d1f80-eee7 a :NarrativeEvent ; :offset 0 .
    # :NarrativeEvent_bb2d1f80-eee7 :text "Joe\'s foot hit the table." .
    # :NarrativeEvent_bb2d1f80-eee7 :has_semantic :Event_902a787d-262c .
    # :NarrativeEvent_bb2d1f80-eee7 :has_first :Event_902a787d-262c .
    # :Event_902a787d-262c :text "Joe\'s foot hit the table." .
    # :Event_902a787d-262c a :ImpactAndContact ; :confidence-ImpactAndContact 100 .
    # :Event_902a787d-262c a :BodilyAct ; :confidence-BodilyAct 80 .
    # :Noun_dd3f79bf-55d8 a :ComponentPart ; :text "Joe\'s foot" ; :confidence 100 .
    # :Noun_dd3f79bf-55d8 :clarifying_text "Joe\'s" .
    # :Event_902a787d-262c :has_active_entity :Noun_dd3f79bf-55d8 .
    # :Noun_54a21a08-ea20 a :Resource ; :text "table" ; :confidence 100 .
    # :Event_902a787d-262c :has_affected_entity :Noun_54a21a08-ea20 .


def test_communication():
    sentence_classes, quotation_classes = parse_narrative(text_communication)
    graph_results = create_graph(sentence_classes, quotation_classes, text_communication, ':Narrative_foo',
                                 ['politics and international'], 5, repo)
    ttl_str = str(graph_results.turtle)
    assert 'loaded language' in ttl_str
    assert ':CommunicationAndSpeechAct' in ttl_str           # claimed
    assert ':has_active_entity :Liz_Cheney' in ttl_str
    assert ':DeceptionAndDishonesty' in ttl_str              # promoting lie
    assert ':has_active_entity :Donald_Trump' in ttl_str
    assert ':LawEnforcement' in ttl_str
    assert ':has_location :Mar_a_Lago' in ttl_str
    assert ':has_topic :FBI' in ttl_str or ':has_context :FBI' in ttl_str
    # Output Turtle:
    # :Narrative_foo :has_component :Sentence_124bae5f-6ffb .
    # :Sentence_124bae5f-6ffb a :Sentence ; :offset 1 .
    # :Sentence_124bae5f-6ffb :text "Liz Cheney claimed that Trump is promoting an insidious lie about the recent FBI
    #     raid of his Mar-a-Lago residence." .
    # :Sentence_124bae5f-6ffb :mentions :Liz_Cheney .
    # :Sentence_124bae5f-6ffb :mentions :Donald_Trump .
    # :Sentence_124bae5f-6ffb :mentions :FBI .
    # :Sentence_124bae5f-6ffb :mentions :Mar_a_Lago .
    # :Sentence_124bae5f-6ffb :grade_level 10 .
    # :Sentence_124bae5f-6ffb :rhetorical_device "loaded language" .
    # :Sentence_124bae5f-6ffb :rhetorical_device_loaded_language "The phrase \'insidious lie\' uses loaded language
    #     with strong negative connotations, invoking emotions and judgments about the nature of the lie." .
    # :Narrative_foo :describes :NarrativeEvent_779d4993-835c .
    # :NarrativeEvent_779d4993-835c a :NarrativeEvent ; :offset 0 .
    # :NarrativeEvent_779d4993-835c :text "Liz Cheney claimed that Trump is promoting an insidious lie about the
    #     recent FBI raid of his Mar-a-Lago residence." .
    # :NarrativeEvent_779d4993-835c :has_semantic :Event_ccd90e94-e941 .
    # :NarrativeEvent_779d4993-835c :has_first :Event_ccd90e94-e941 .
    # :Event_ccd90e94-e941 :text "Liz Cheney claimed." .
    # :Event_ccd90e94-e941 a :CommunicationAndSpeechAct ; :confidence-CommunicationAndSpeechAct 95 .
    # :Event_ccd90e94-e941 :has_active_entity :Liz_Cheney .
    # :NarrativeEvent_779d4993-835c :has_semantic :Event_817567a2-5c35 .
    # :Event_ccd90e94-e941 :has_next :Event_817567a2-5c35 .
    # :Event_817567a2-5c35 :text "Trump is promoting an insidious lie." .
    # :Event_817567a2-5c35 a :DeceptionAndDishonesty ; :confidence-DeceptionAndDishonesty 90 .
    # :Event_817567a2-5c35 a :DisagreementAndDispute ; :confidence-DisagreementAndDispute 80 .
    # :Event_817567a2-5c35 :has_active_entity :Donald_Trump .
    # :Noun_a638936d-c5a3 a :DeceptionAndDishonesty ; :text "insidious lie" ; :confidence 90 .
    # :Event_817567a2-5c35 :has_topic :Noun_a638936d-c5a3 .
    # :NarrativeEvent_779d4993-835c :has_semantic :Event_08ccd98f-8529 .
    # :Event_817567a2-5c35 :has_next :Event_08ccd98f-8529 .
    # :Event_08ccd98f-8529 :text "The insidious lie is about the recent FBI raid of Trump\'s Mar-a-Lago residence." .
    # :Event_08ccd98f-8529 a :AssessmentMeasurement ; :confidence-AssessmentMeasurement 85 .
    # :Event_08ccd98f-8529 a :LawEnforcement ; :confidence-LawEnforcement 80 .
    # :Event_08ccd98f-8529 :has_context :Noun_a638936d-c5a3 .
    # :Event_08ccd98f-8529 :has_context :FBI .
    # :Mar_a_Lago :clarifying_reference :Donald_Trump .
    # :Mar_a_Lago :clarifying_text "Trump\'s" .
    # :Event_08ccd98f-8529 :has_context :Mar_a_Lago .


def test_multiple_verbs():
    sentence_classes, quotation_classes = parse_narrative(text_multiple_verbs)
    graph_results = create_graph(sentence_classes, quotation_classes, text_multiple_verbs,
                                 ':Narrative_foo', [],5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':AttributeAndCharacteristic' in ttl_str
    assert ':has_context :Sue' in ttl_str
    assert ':LineOfBusiness ; :text "attorney' in ttl_str and \
           (':has_aspect :Noun' in ttl_str or ':has_context :Noun' in ttl_str)
    assert ':DeceptionAndDishonesty' in ttl_str
    assert ':has_active_entity :Sue' in ttl_str
    # Output Turtle:
    # :Narrative_foo :has_component :Sentence_c403f334-89bd .
    # :Sentence_c403f334-89bd a :Sentence ; :offset 1 .
    # :Sentence_c403f334-89bd :text "Sue is an attorney but still lies." .
    # :Sentence_c403f334-89bd :mentions :Sue .
    # :Sentence_c403f334-89bd :grade_level 8 .
    # :Sentence_c403f334-89bd :rhetorical_device "loaded language" .
    # :Sentence_c403f334-89bd :rhetorical_device_loaded_language "The word \'lies\' is loaded language with strong
    #     negative connotations, invoking emotions and judgments about Sue\'s character." .
    # :Narrative_foo :describes :NarrativeEvent_b03ba533-56b0 .
    # :NarrativeEvent_b03ba533-56b0 a :NarrativeEvent ; :offset 0 .
    # :NarrativeEvent_b03ba533-56b0 :text "Sue is an attorney." .
    # :NarrativeEvent_b03ba533-56b0 :has_semantic :Event_f875ea5c-fe7d .
    # :NarrativeEvent_b03ba533-56b0 :has_first :Event_f875ea5c-fe7d .
    # :Event_f875ea5c-fe7d :text "Sue is an attorney." .
    # :Event_f875ea5c-fe7d a :AttributeAndCharacteristic ; :confidence-AttributeAndCharacteristic 100 .
    # :Event_f875ea5c-fe7d :has_context :Sue .
    # :Noun_afe4bd24-3dee a :LineOfBusiness ; :text "attorney" ; :confidence 95 .
    # :Event_f875ea5c-fe7d :has_aspect :Noun_afe4bd24-3dee .
    # :Narrative_foo :describes :NarrativeEvent_33d186c9-39dd .
    # :NarrativeEvent_33d186c9-39dd a :NarrativeEvent ; :offset 1 .
    # :NarrativeEvent_33d186c9-39dd :text "Sue lies." .
    # :NarrativeEvent_33d186c9-39dd :has_semantic :Event_4a4bb6e5-a588 .
    # :NarrativeEvent_33d186c9-39dd :has_first :Event_4a4bb6e5-a588 .
    # :Event_4a4bb6e5-a588 :text "Sue lies." .
    # :Event_4a4bb6e5-a588 a :DeceptionAndDishonesty ; :confidence-DeceptionAndDishonesty 100 .
    # :Event_4a4bb6e5-a588 a :CommunicationAndSpeechAct ; :confidence-CommunicationAndSpeechAct 80 .
    # :Event_4a4bb6e5-a588 :has_active_entity :Sue .


def test_aux_pobj():
    sentence_classes, quotation_classes = parse_narrative(text_aux_pobj)
    graph_results = create_graph(sentence_classes, quotation_classes, text_aux_pobj,
                                 ':Narrative_foo', [], 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':RemovalAndRestriction' in ttl_str
    assert ':has_active_entity :John' in ttl_str
    assert ':WasteAndResidue' in ttl_str and ':text "debris' in ttl_str
    assert ':has_topic :Noun' in ttl_str or ':has_affected_entity :Noun' in ttl_str
    # Output Turtle:
    # :Narrative_foo :has_component :Sentence_0f6bcadf-d47f .
    # :Sentence_0f6bcadf-d47f a :Sentence ; :offset 1 .
    # :Sentence_0f6bcadf-d47f :text "John got rid of the debris." .
    # :Sentence_0f6bcadf-d47f :mentions :John .
    # :Sentence_0f6bcadf-d47f :grade_level 3 .
    # :Narrative_foo :describes :NarrativeEvent_a7597602-1cda .
    # :NarrativeEvent_a7597602-1cda a :NarrativeEvent ; :offset 0 .
    # :NarrativeEvent_a7597602-1cda :text "John got rid of the debris." .
    # :NarrativeEvent_a7597602-1cda :has_semantic :Event_b427a878-e554 .
    # :NarrativeEvent_a7597602-1cda :has_first :Event_b427a878-e554 .
    # :Event_b427a878-e554 :text "John removed the debris." .
    # :Event_b427a878-e554 a :RemovalAndRestriction ; :confidence-RemovalAndRestriction 95 .
    # :Event_b427a878-e554 a :End ; :confidence-End 85 .
    # :Event_b427a878-e554 :has_active_entity :John .
    # :Noun_da005dcf-182d a :WasteAndResidue ; :text "debris" ; :confidence 100 .
    # :Event_b427a878-e554 :has_affected_entity :Noun_da005dcf-182d .


def test_idiom_amod():
    sentence_classes, quotation_classes = parse_narrative(text_idiom_amod)
    graph_results = create_graph(sentence_classes, quotation_classes, text_idiom_amod,
                                 ':Narrative_foo', [],5, repo)
    ttl_str = str(graph_results.turtle)
    assert "allusion" in ttl_str
    assert ':Avoidance' in ttl_str
    assert ':has_active_entity :John' in ttl_str
    assert ':DeceptionAndDishonesty' in ttl_str
    assert ':has_topic :Noun' in ttl_str
    assert ':clarifying_text "Mary' in ttl_str
    # Output Turtle:
    # :Narrative_foo :has_component :Sentence_0af83723-ce2a .
    # :Sentence_0af83723-ce2a a :Sentence ; :offset 1 .
    # :Sentence_0af83723-ce2a :text "John turned a blind eye to Mary\'s infidelity." .
    # :Sentence_0af83723-ce2a :mentions :John .
    # :Sentence_0af83723-ce2a :mentions :Mary .
    # :Sentence_0af83723-ce2a :grade_level 8 .
    # :Sentence_0af83723-ce2a :rhetorical_device "allusion" .
    # :Sentence_0af83723-ce2a :rhetorical_device_allusion "The phrase \'turned a blind eye\' is an allusion to the
    #     historical anecdote about Admiral Horatio Nelson, who purportedly used his blind eye to look through a
    #     telescope and claim he did not see a signal to withdraw, thus ignoring orders." .
    # :Narrative_foo :describes :NarrativeEvent_91dc9b07-75e3 .
    # :NarrativeEvent_91dc9b07-75e3 a :NarrativeEvent ; :offset 0 .
    # :NarrativeEvent_91dc9b07-75e3 :text "John ignored Mary\'s infidelity." .
    # :NarrativeEvent_91dc9b07-75e3 :has_semantic :Event_d708ab1a-b538 .
    # :NarrativeEvent_91dc9b07-75e3 :has_first :Event_d708ab1a-b538 .
    # :Event_d708ab1a-b538 :text "John ignored Mary\'s infidelity." .
    # :Event_d708ab1a-b538 a :Avoidance ; :confidence-Avoidance 90 .
    # TODO: EmotionalResponse may be a consequence but is not indicated in the situation
    # :Event_d708ab1a-b538 a :EmotionalResponse ; :confidence-EmotionalResponse 80 .
    # :Event_d708ab1a-b538 :negated-EmotionalResponse true .    # TODO: Likely indicates a negative emotion
    # :Event_d708ab1a-b538 :has_active_entity :John .
    # :Noun_07d34898-64af a :DeceptionAndDishonesty ; :text "Mary\'s infidelity" ; :confidence 90 .
    # :Noun_07d34898-64af :clarifying_reference :Mary .
    # :Noun_07d34898-64af :clarifying_text "Mary\'s" .
    # :Event_d708ab1a-b538 :has_topic :Noun_07d34898-64af .


def test_complex_verb():
    sentence_classes, quotation_classes = parse_narrative(text_complex_verb)
    graph_results = create_graph(sentence_classes, quotation_classes, text_complex_verb,
                                 ':Narrative_foo', [], 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':End' in ttl_str or ':EconomyAndFinanceRelated' in ttl_str
    assert ':OrganizationalEntity' in ttl_str or ':Location' in ttl_str      # store
    assert ':has_active_entity :Noun' in ttl_str
    assert ':has_time :PiT_DayTuesday' in ttl_str
    # Output Turtle:
    # :Narrative_foo :has_component :Sentence_df8aee8c-a948 .
    # :Sentence_df8aee8c-a948 a :Sentence ; :offset 1 .
    # :Sentence_df8aee8c-a948 :text "The store went out of business on Tuesday." .
    # :Sentence_df8aee8c-a948 :grade_level 5 .
    # :Narrative_foo :describes :NarrativeEvent_89e94b0a-00eb .
    # :NarrativeEvent_89e94b0a-00eb a :NarrativeEvent ; :offset 0 .
    # :NarrativeEvent_89e94b0a-00eb :text "The store went out of business on Tuesday." .
    # :NarrativeEvent_89e94b0a-00eb :has_semantic :Event_1974a288-0969 .
    # :NarrativeEvent_89e94b0a-00eb :has_first :Event_1974a288-0969 .
    # :Event_1974a288-0969 :text "The store went out of business on Tuesday." .
    # :Event_1974a288-0969 a :End ; :confidence-End 95 .
    # :Event_1974a288-0969 a :EconomyAndFinanceRelated ; :confidence-EconomyAndFinanceRelated 90 .
    # :Noun_bc02da9b-cfc0 a :OrganizationalEntity ; :text "store" ; :confidence 90 .
    # :Event_1974a288-0969 :has_active_entity :Noun_bc02da9b-cfc0 .
    # :PiT_DayTuesday a :Time ; :text "Tuesday" .
    # :Event_1974a288-0969 :has_time :PiT_DayTuesday .


def test_neg_acomp_xcomp():
    sentence_classes, quotation_classes = parse_narrative(text_neg_acomp_xcomp)
    graph_results = create_graph(sentence_classes, quotation_classes, text_neg_acomp_xcomp,
                                 ':Narrative_foo', [], 5, repo)
    ttl_str = str(graph_results.turtle)
    print(ttl_str)
    assert ':Avoidance' in ttl_str
    assert (':ReadinessAndAbility' in ttl_str and ':negated-ReadinessAndAbility' in ttl_str) or \
           (':EmotionalResponse' in ttl_str and ':negated-EmotionalResponse' in ttl_str)
    assert ':has_active_entity :Jane' in ttl_str
    assert ':DeceptionAndDishonesty' in ttl_str
    assert ':has_topic :Noun' in ttl_str
    # Output Turtle:
    # :Narrative_foo :has_component :Sentence_0d631212-8f37 .
    # :Sentence_0d631212-8f37 a :Sentence ; :offset 1 .
    # :Sentence_0d631212-8f37 :text "Jane is not able to stomach lies." .
    # :Sentence_0d631212-8f37 :mentions :Jane .
    # :Sentence_0d631212-8f37 :grade_level 6 .
    # :Narrative_foo :describes :NarrativeEvent_e537a442-8262 .
    # :NarrativeEvent_e537a442-8262 a :NarrativeEvent ; :offset 0 .
    # :NarrativeEvent_e537a442-8262 :text "Jane is not able to stomach lies." .
    # :NarrativeEvent_e537a442-8262 :has_semantic :Event_94aadca1-a00a .
    # :NarrativeEvent_e537a442-8262 :has_first :Event_94aadca1-a00a .
    # :Event_94aadca1-a00a :text "Jane is not able to stomach lies." .
    # :Event_94aadca1-a00a a :Avoidance ; :confidence-Avoidance 90 .
    # TODO: EmotionalResponse may be a consequence but is not indicated in the situation
    # :Event_94aadca1-a00a a :EmotionalResponse ; :confidence-EmotionalResponse 80 .
    # :Event_94aadca1-a00a :negated-EmotionalResponse true .
    # :Event_94aadca1-a00a :has_active_entity :Jane .
    # TODO: Missing the topic, "lies"

def test_non_person_subject():
    sentence_classes, quotation_classes = parse_narrative(text_non_person_subject)
    graph_results = create_graph(sentence_classes, quotation_classes, text_non_person_subject,
                                 ':Narrative_foo', [], 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':Loss' in ttl_str
    assert ':EmotionalResponse' in ttl_str or ':Cognition' in ttl_str
    assert ':has_active_entity :John' in ttl_str or ':has_topic :John' in ttl_str
    # Output Turtle:
    # :Narrative_foo :has_component :Sentence_260350b4-976f .
    # :Sentence_260350b4-976f a :Sentence ; :offset 1 .
    # :Sentence_260350b4-976f :text "John\'s hopes were dashed." .
    # :Sentence_260350b4-976f :mentions :John .
    # :Sentence_260350b4-976f :grade_level 5 .
    # :Narrative_foo :describes :NarrativeEvent_bda47afb-990f .
    # :NarrativeEvent_bda47afb-990f a :NarrativeEvent ; :offset 0 .
    # :NarrativeEvent_bda47afb-990f :text "John\'s hopes were dashed." .
    # :NarrativeEvent_bda47afb-990f :has_semantic :Event_ad815027-226c .
    # :NarrativeEvent_bda47afb-990f :has_first :Event_ad815027-226c .
    # :Event_ad815027-226c :text "John\'s hopes were dashed." .
    # :Event_ad815027-226c a :Loss ; :confidence-Loss 100 .
    # :Event_ad815027-226c a :EmotionalResponse ; :confidence-EmotionalResponse 80 .
    # :Event_ad815027-226c :has_active_entity :John .


def test_first_person():
    sentence_classes, quotation_classes = parse_narrative(text_first_person)
    graph_results = create_graph(sentence_classes, quotation_classes, text_first_person,
                                 ':Narrative_foo', [], 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':ReadinessAndAbility' in ttl_str and ':negated-ReadinessAndAbility' in ttl_str
    assert ':MovementTravelAndTransportation' in ttl_str
    assert ':Person ; :text "I' in ttl_str or ':Person ; :text "narrator' in ttl_str
    assert ':has_active_entity :Noun' in ttl_str
    # Output Turtle:
    # :Narrative_foo :has_component :Sentence_170c7974-e023 .
    # :Sentence_170c7974-e023 a :Sentence ; :offset 1 .
    # :Sentence_170c7974-e023 :text "I was not ready to leave." .
    # :Sentence_170c7974-e023 :grade_level 4 .
    # :Narrative_foo :describes :NarrativeEvent_65e67c5e-74b3 .
    # :NarrativeEvent_65e67c5e-74b3 a :NarrativeEvent ; :offset 0 .
    # :NarrativeEvent_65e67c5e-74b3 :text "The narrator was not ready to leave." .
    # :NarrativeEvent_65e67c5e-74b3 :has_semantic :Event_daff53da-327e .
    # :NarrativeEvent_65e67c5e-74b3 :has_first :Event_daff53da-327e .
    # :Event_daff53da-327e :text "The narrator was not ready." .
    # :Event_daff53da-327e a :ReadinessAndAbility ; :confidence-ReadinessAndAbility 90 .
    # :Event_daff53da-327e :negated-ReadinessAndAbility true .
    # :Noun_213dbf69-5a05 a :Person ; :text "narrator" ; :confidence 95 .
    # :Event_daff53da-327e :has_active_entity :Noun_213dbf69-5a05 .
    # :NarrativeEvent_65e67c5e-74b3 :has_semantic :Event_e630af45-1c65 .
    # :Event_daff53da-327e :has_next :Event_e630af45-1c65 .
    # :Event_e630af45-1c65 :text "The narrator was not ready to leave." .
    # :Event_e630af45-1c65 a :MovementTravelAndTransportation ; :confidence-MovementTravelAndTransportation 85 .
    # :Event_e630af45-1c65 :negated-MovementTravelAndTransportation true .
    # :Event_e630af45-1c65 a :ReadinessAndAbility ; :confidence-ReadinessAndAbility 90 .
    # :Event_e630af45-1c65 :negated-ReadinessAndAbility true .
    # :Event_e630af45-1c65 :has_active_entity :Noun_213dbf69-5a05 .


def test_pobj_semantics():
    sentence_classes, quotation_classes = parse_narrative(text_pobj_semantics)
    graph_results = create_graph(sentence_classes, quotation_classes, text_pobj_semantics,
                                 ':Narrative_foo', [], 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':Avoidance' in ttl_str     # escape
    assert ':Person ; :text "robber' in ttl_str
    assert ':has_active_entity :Noun' in ttl_str
    assert ':AidAndAssistance' in ttl_str
    assert 'a :PoliceForce' in ttl_str and ':text "local police' in ttl_str
    assert ':has_affected_entity :Noun' in ttl_str    # robber who is assisted
    # Output Turtle:
    # :Narrative_foo :has_component :Sentence_fad758aa-3e36 .
    # :Sentence_fad758aa-3e36 a :Sentence ; :offset 1 .
    # :Sentence_fad758aa-3e36 :text "The robber escaped with the aid of the local police." .
    # :Sentence_fad758aa-3e36 :grade_level 8 .
    # :Narrative_foo :describes :NarrativeEvent_6d3eef1b-6071 .
    # :NarrativeEvent_6d3eef1b-6071 a :NarrativeEvent ; :offset 0 .
    # :NarrativeEvent_6d3eef1b-6071 :text "The robber escaped with the aid of the local police." .
    # :NarrativeEvent_6d3eef1b-6071 :has_semantic :Event_43d6869c-221a .
    # :NarrativeEvent_6d3eef1b-6071 :has_first :Event_43d6869c-221a .
    # :Event_43d6869c-221a :text "The robber escaped." .
    # :Event_43d6869c-221a a :Avoidance ; :confidence-Avoidance 100 .
    # :Event_43d6869c-221a a :MovementTravelAndTransportation ; :confidence-MovementTravelAndTransportation 80 .
    # :Noun_e4a5f404-7807 a :Person ; :text "robber" ; :confidence 95 .
    # :Event_43d6869c-221a :has_active_entity :Noun_e4a5f404-7807 .
    # :NarrativeEvent_6d3eef1b-6071 :has_semantic :Event_dbdf2775-1f2a .
    # :Event_43d6869c-221a :has_next :Event_dbdf2775-1f2a .
    # :Event_dbdf2775-1f2a :text "The local police aided the robber." .
    # :Event_dbdf2775-1f2a a :AidAndAssistance ; :confidence-AidAndAssistance 100 .
    # :Event_dbdf2775-1f2a a :CrimeAndHostileConflict ; :confidence-CrimeAndHostileConflict 70 .
    # :Event_dbdf2775-1f2a :negated-CrimeAndHostileConflict true .
    # :Noun_9eea92e6-81f2 a :PoliceForce, :Collection ; :text "local police" ; :confidence 100 .
    # :Event_dbdf2775-1f2a :has_active_entity :Noun_9eea92e6-81f2 .
    # :Event_dbdf2775-1f2a :has_affected_entity :Noun_e4a5f404-7807 .


def test_multiple_subjects():
    sentence_classes, quotation_classes = parse_narrative(text_multiple_subjects)
    graph_results = create_graph(sentence_classes, quotation_classes, text_multiple_subjects,
                                 ':Narrative_foo', [], 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':DisagreementAndDispute' in ttl_str
    assert ':has_active_entity :Jane' in ttl_str
    assert ':has_active_entity :John' in ttl_str
    # Output Turtle:
    # :Narrative_foo :has_component :Sentence_c6adb28b-2f38 .
    # :Sentence_c6adb28b-2f38 a :Sentence ; :offset 1 .
    # :Sentence_c6adb28b-2f38 :text "Jane and John had a serious difference of opinion." .
    # :Sentence_c6adb28b-2f38 :mentions :Jane .
    # :Sentence_c6adb28b-2f38 :mentions :John .
    # :Sentence_c6adb28b-2f38 :grade_level 6 .
    # :Narrative_foo :describes :NarrativeEvent_01f478e8-8aed .
    # :NarrativeEvent_01f478e8-8aed a :NarrativeEvent ; :offset 0 .
    # :NarrativeEvent_01f478e8-8aed :text "Jane and John had a serious difference of opinion." .
    # :NarrativeEvent_01f478e8-8aed :has_semantic :Event_daf442ec-2f83 .
    # :NarrativeEvent_01f478e8-8aed :has_first :Event_daf442ec-2f83 .
    # :Event_daf442ec-2f83 :text "Jane had a serious difference of opinion with John." .
    # :Event_daf442ec-2f83 a :DisagreementAndDispute ; :confidence-DisagreementAndDispute 100 .
    # :Event_daf442ec-2f83 a :Agreement ; :confidence-Agreement 80 .
    # :Event_daf442ec-2f83 :negated-Agreement true .
    # :Event_daf442ec-2f83 :has_active_entity :Jane .
    # :Event_daf442ec-2f83 :has_affected_entity :John .
    # :NarrativeEvent_01f478e8-8aed :has_semantic :Event_b2ee0d65-9429 .
    # :Event_daf442ec-2f83 :has_next :Event_b2ee0d65-9429 .
    # :Event_b2ee0d65-9429 :text "John had a serious difference of opinion with Jane." .
    # :Event_b2ee0d65-9429 a :DisagreementAndDispute ; :confidence-DisagreementAndDispute 100 .
    # :Event_b2ee0d65-9429 a :Agreement ; :confidence-Agreement 80 .
    # :Event_b2ee0d65-9429 :negated-Agreement true .
    # :Event_b2ee0d65-9429 :has_active_entity :John .
    # :Event_b2ee0d65-9429 :has_affected_entity :Jane .


def test_multiple_xcomp():
    sentence_classes, quotation_classes = parse_narrative(text_multiple_xcomp)
    graph_results = create_graph(sentence_classes, quotation_classes, text_multiple_xcomp,
                                 ':Narrative_foo', [], 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':EmotionalResponse' in ttl_str
    assert ':BodilyAct' in ttl_str
    assert ':has_active_entity :John' in ttl_str
    # Output Turtle:
    # :Narrative_foo :has_component :Sentence_9f2f428f-8d7a .
    # :Sentence_9f2f428f-8d7a a :Sentence ; :offset 1 .
    # :Sentence_9f2f428f-8d7a :text "John liked to ski and to swim." .
    # :Sentence_9f2f428f-8d7a :mentions :John .
    # :Sentence_9f2f428f-8d7a :grade_level 3 .
    # :Narrative_foo :describes :NarrativeEvent_ac7ea6ab-f348 .
    # :NarrativeEvent_ac7ea6ab-f348 a :NarrativeEvent ; :offset 0 .
    # :NarrativeEvent_ac7ea6ab-f348 :text "John liked to ski." .
    # :NarrativeEvent_ac7ea6ab-f348 :has_semantic :Event_1bda1beb-086f .
    # :NarrativeEvent_ac7ea6ab-f348 :has_first :Event_1bda1beb-086f .
    # :Event_1bda1beb-086f :text "John liked skiing." .
    # :Event_1bda1beb-086f a :EmotionalResponse ; :confidence-EmotionalResponse 100 .
    # :Event_1bda1beb-086f a :BodilyAct ; :confidence-BodilyAct 80 .
    # :Event_1bda1beb-086f :has_active_entity :John .
    # :Noun_7db1f5a9-1387 a :BodilyAct, :Collection ; :text "skiing" ; :confidence 90 .
    # :Event_1bda1beb-086f :has_topic :Noun_7db1f5a9-1387 .
    # :Narrative_foo :describes :NarrativeEvent_c12354d4-25fc .
    # :NarrativeEvent_c12354d4-25fc a :NarrativeEvent ; :offset 1 .
    # :NarrativeEvent_c12354d4-25fc :text "John liked to swim." .
    # :NarrativeEvent_c12354d4-25fc :has_semantic :Event_6be4bcbe-3e51 .
    # :NarrativeEvent_c12354d4-25fc :has_first :Event_6be4bcbe-3e51 .
    # :Event_6be4bcbe-3e51 :text "John liked swimming." .
    # :Event_6be4bcbe-3e51 a :EmotionalResponse ; :confidence-EmotionalResponse 90 .
    # :Event_6be4bcbe-3e51 a :BodilyAct ; :confidence-BodilyAct 80 .
    # :Event_6be4bcbe-3e51 :has_active_entity :John .
    # :Noun_9099c638-3251 a :BodilyAct, :Collection ; :text "swimming" ; :confidence 100 .
    # :Event_6be4bcbe-3e51 :has_topic :Noun_9099c638-3251 .


def test_location_hierarchy():
    sentence_classes, quotation_classes = parse_narrative(text_location_hierarchy)
    graph_results = create_graph(sentence_classes, quotation_classes, text_location_hierarchy,
                                 ':Narrative_foo', [], 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':mentions geo:2658434' in ttl_str        # Switzerland
    assert 'imagery' in ttl_str or 'exceptionalism' in ttl_str
    assert ':AttributeAndCharacteristic' in ttl_str
    assert ':Location' in ttl_str and (':text "mountains' in ttl_str or ':text "Switzerland' in ttl_str)
    assert ':has_context :Noun' in ttl_str or ':has_topic :Noun' in ttl_str
    # Output Turtle:
    # :Narrative_foo :has_component :Sentence_68f0d108-f242 .
    # :Sentence_68f0d108-f242 a :Sentence ; :offset 1 .
    # :Sentence_68f0d108-f242 :text "Switzerland\'s mountains are magnificent." .
    # :Sentence_68f0d108-f242 :mentions geo:2658434 .
    # :Sentence_68f0d108-f242 :grade_level 5 .
    # :Sentence_68f0d108-f242 :rhetorical_device "imagery" .
    # :Sentence_68f0d108-f242 :rhetorical_device_imagery "The sentence uses imagery by describing Switzerland\'s
    #     mountains as \'magnificent,\' which paints a vivid picture and emotionally engages the reader." .
    # :Narrative_foo :describes :NarrativeEvent_5ff44e7e-a572 .
    # :NarrativeEvent_5ff44e7e-a572 a :NarrativeEvent ; :offset 0 .
    # :NarrativeEvent_5ff44e7e-a572 :text "Switzerland\'s mountains are described as magnificent." .
    # :NarrativeEvent_5ff44e7e-a572 :has_semantic :Event_c75dc8bd-51af .
    # :NarrativeEvent_5ff44e7e-a572 :has_first :Event_c75dc8bd-51af .
    # :Event_c75dc8bd-51af :text "Switzerland\'s mountains are described as magnificent." .
    # :Event_c75dc8bd-51af a :AttributeAndCharacteristic ; :confidence-AttributeAndCharacteristic 100 .
    # :Event_c75dc8bd-51af a :CommunicationAndSpeechAct ; :confidence-CommunicationAndSpeechAct 90 .
    # :Noun_a2f694c2-cfd9 a :Location, :Collection ; :text "Switzerland\'s mountains" ; :confidence 95 .
    # :Noun_a2f694c2-cfd9 :clarifying_text "Switzerland\'s" .
    # :Event_c75dc8bd-51af :has_context :Noun_a2f694c2-cfd9 .


def test_weather():
    sentence_classes, quotation_classes = parse_narrative(text_weather)
    graph_results = create_graph(sentence_classes, quotation_classes, text_weather,
                                 ':Narrative_foo', [], 5, repo)
    ttl_str = str(graph_results.turtle)
    print(ttl_str)
    assert ':mentions :Hurricane_Otis' in ttl_str and ':mentions :Acapulco' in ttl_str
    assert ':EnvironmentalIssue' in ttl_str or ':DamageAndDifficulty' in ttl_str
    assert ':has_active_entity :Hurricane_Otis' in ttl_str
    assert ':has_affected_entity :Acapulco' in ttl_str
    # Output Turtle:
    # :Narrative_foo :has_component :Sentence_fbc53a36-fb27 .
    # :Sentence_fbc53a36-fb27 a :Sentence ; :offset 1 .
    # :Sentence_fbc53a36-fb27 :text "Hurricane Otis severely damaged Acapulco." .
    # :Hurricane_Otis :text "Hurricane Otis" .          # Example of background data from Wikidata and GeoNames
    # :Hurricane_Otis a :EnvironmentalIssue .
    # :Hurricane_Otis rdfs:label "Hurricane Otis", "Otis" .
    # :Hurricane_Otis rdfs:comment "From Wikipedia (wikibase_item: Q123178445): \'Hurricane Otis was a compact but
    #     very powerful tropical cyclone which made a devastating landfall in October 2023 near Acapulco as a
    #     Category 5 hurricane. Otis was the first Pacific hurricane to make landfall at Category 5 intensity and
    #     surpassed Hurricane Patricia as the strongest landfalling Pacific hurricane on record. The resulting damage
    #     made Otis the costliest tropical cyclone to strike Mexico on record. The fifteenth tropical storm,
    #     tenth hurricane, eighth major hurricane, and second Category 5 hurricane of the 2023 Pacific hurricane
    #     season, Otis originated from a disturbance several hundred miles south of the Gulf of Tehuantepec.
    #     Initially forecast to stay offshore and to only be a weak tropical storm at peak intensity, Otis instead
    #     underwent explosive intensification to reach peak winds of 165 mph (270 km/h) and weakened only slightly
    #     before making landfall as a powerful Category 5 hurricane. Once inland, the hurricane quickly weakened
    #     before dissipating the following day.\'" .
    # :Hurricane_Otis :external_link "https://en.wikipedia.org/wiki/Hurricane_Otis" .
    # :Hurricane_Otis :external_identifier "Q123178445" .
    # :Hurricane_Otis :has_beginning :PiT_2023-10-22T00:00:00Z .
    # :Hurricane_Otis :has_end :PiT_2023-10-25T00:00:00Z .
    # :Acapulco :text "Acapulco" .
    # :Acapulco a :OrganizationalEntity, :Correction .
    # :Acapulco rdfs:label "Acapulco", "Acapulco de julio", "Acapulco de Juarez", "Acapulco, Guerrero",
    #     "Acapulco de Juárez" .
    # :Acapulco rdfs:comment "From Wikipedia (wikibase_item: Q81398): \'Acapulco de Ju?rez, commonly called Acapulco,
    #     is a city and major seaport in the state of Guerrero on the Pacific Coast of Mexico, 380 kilometres (240 mi)
    #     south of Mexico City. Located on a deep, semicircular bay, Acapulco has been a port since the early colonial
    #     period of Mexico\'s history. It is a port of call for shipping and cruise lines running between Panama and
    #     San Francisco, California, United States. The city of Acapulco is the largest in the state, far larger than
    #     the state capital Chilpancingo. Acapulco is also Mexico\'s largest beach and balneario resort city. Acapulco
    #     de Ju?rez, Guerrero is the municipal seat of the municipality of Acapulco, Guerrero.\'" .
    # :Acapulco :external_link "https://en.wikipedia.org/wiki/Acapulco" .
    # :Acapulco :external_identifier "Q81398" .
    # :Sentence_fbc53a36-fb27 :mentions :Hurricane_Otis .
    # :Sentence_fbc53a36-fb27 :mentions :Acapulco .
    # :Sentence_fbc53a36-fb27 :grade_level 6 .
    # :Narrative_foo :describes :NarrativeEvent_64c2ccf0-f199 .
    # :NarrativeEvent_64c2ccf0-f199 a :NarrativeEvent ; :offset 0 .
    # :NarrativeEvent_64c2ccf0-f199 :text "Hurricane Otis severely damaged Acapulco." .
    # :NarrativeEvent_64c2ccf0-f199 :has_semantic :Event_2086fccb-ea95 .
    # :NarrativeEvent_64c2ccf0-f199 :has_first :Event_2086fccb-ea95 .
    # :Event_2086fccb-ea95 :text "Hurricane Otis damaged Acapulco." .
    # :Event_2086fccb-ea95 a :EnvironmentalIssue ; :confidence-EnvironmentalIssue 100 .
    # :Event_2086fccb-ea95 a :DamageAndDifficulty ; :confidence-DamageAndDifficulty 90 .
    # :Event_2086fccb-ea95 :has_active_entity :Hurricane_Otis .
    # :Event_2086fccb-ea95 :has_affected_entity :Acapulco .


def test_coref():
    sentence_classes, quotation_classes = parse_narrative(text_coref)
    graph_results = create_graph(sentence_classes, quotation_classes, text_coref,
                                 ':Narrative_foo', [], 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':SensoryPerception' in ttl_str                        # saw
    assert ':has_active_entity :Anna' in ttl_str
    assert ':Separation' in ttl_str or ':AgricultureApicultureAndAquacultureEvent' in ttl_str or \
        ':BodilyAct' in ttl_str      # cutting
    assert ':has_active_entity :Heidi' in ttl_str
    assert ':Plant, :Collection ; :text "roses' in ttl_str
    assert ':has_affected_entity :Noun' in ttl_str or ':has_topic :Noun' in ttl_str
    assert ':Cognition' in ttl_str and ':Mistake' in ttl_str       # not recognize
    # Output Turtle:
    # :Narrative_foo :has_component :Sentence_4dcf4c0a-18ef .
    # :Sentence_4dcf4c0a-18ef a :Sentence ; :offset 1 .
    # :Sentence_4dcf4c0a-18ef :text "Anna saw Heidi cut the roses, but she did not recognize that it was Heidi
    #     who cut the roses." .
    # :Sentence_4dcf4c0a-18ef :mentions :Anna .
    # :Sentence_4dcf4c0a-18ef :mentions :Heidi .
    # :Sentence_4dcf4c0a-18ef :grade_level 8 .
    # :Narrative_foo :describes :NarrativeEvent_b6bce0ce-1639 .
    # :NarrativeEvent_b6bce0ce-1639 a :NarrativeEvent ; :offset 0 .
    # :NarrativeEvent_b6bce0ce-1639 :text "Anna saw someone cut the roses." .
    # :NarrativeEvent_b6bce0ce-1639 :has_semantic :Event_463a7036-0d30 .
    # :NarrativeEvent_b6bce0ce-1639 :has_first :Event_463a7036-0d30 .
    # :Event_463a7036-0d30 :text "Anna saw someone." .
    # :Event_463a7036-0d30 a :SensoryPerception ; :confidence-SensoryPerception 90 .
    # :Event_463a7036-0d30 a :Search ; :confidence-Search 70 .    # Low probability
    # :Event_463a7036-0d30 :has_active_entity :Anna .
    # :NarrativeEvent_b6bce0ce-1639 :has_semantic :Event_bcf98b2f-e427 .
    # :Event_463a7036-0d30 :has_next :Event_bcf98b2f-e427 .
    # :Event_bcf98b2f-e427 :text "Someone cut the roses." .
    # :Event_bcf98b2f-e427 a :Separation ; :confidence-Separation 95 .
    # :Event_bcf98b2f-e427 a :CrimeAndHostileConflict ; :confidence-CrimeAndHostileConflict 60 .   # Low probability
    # :Noun_8af9c405-3585 a :Plant, :Collection ; :text "roses" ; :confidence 95 .
    # :Event_bcf98b2f-e427 :has_affected_entity :Noun_8af9c405-3585 .
    # :Narrative_foo :describes :NarrativeEvent_fe654f30-e726 .
    # :NarrativeEvent_fe654f30-e726 a :NarrativeEvent ; :offset 1 .
    # :NarrativeEvent_fe654f30-e726 :text "Anna did not recognize that it was Heidi who cut the roses." .
    # :NarrativeEvent_fe654f30-e726 :has_semantic :Event_1660a1f6-0fc2 .
    # :NarrativeEvent_fe654f30-e726 :has_first :Event_1660a1f6-0fc2 .
    # :Event_1660a1f6-0fc2 :text "Anna did not recognize." .
    # :Event_1660a1f6-0fc2 a :Mistake ; :confidence-Mistake 90 .
    # :Event_1660a1f6-0fc2 a :Cognition ; :confidence-Cognition 80 .
    # :Event_1660a1f6-0fc2 :has_active_entity :Anna .
    # :NarrativeEvent_fe654f30-e726 :has_semantic :Event_a0a8aee7-70b8 .
    # :Event_1660a1f6-0fc2 :has_next :Event_a0a8aee7-70b8 .
    # :Event_a0a8aee7-70b8 :text "Heidi cut the roses." .
    # :Event_a0a8aee7-70b8 a :Separation ; :confidence-Separation 85 .
    # :Event_a0a8aee7-70b8 a :BodilyAct ; :confidence-BodilyAct 75 .
    # :Event_a0a8aee7-70b8 :has_active_entity :Heidi .
    # :Event_a0a8aee7-70b8 :has_affected_entity :Noun_8af9c405-3585


def test_quotation():
    sentence_classes, quotation_classes = parse_narrative(text_quotation)
    graph_results = create_graph(sentence_classes, quotation_classes, text_quotation,
                                 ':Narrative_foo', [], 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':mentions :NVIDIA' in ttl_str
    assert ':CommunicationAndSpeechAct' in ttl_str
    assert ':Attempt' in ttl_str and ':Affiliation' in ttl_str
    assert ':has_active_entity :Jane' in ttl_str
    assert ':has_topic :NVIDIA' in ttl_str or ':affiliated_with :NVIDIA' in ttl_str or \
        ':has_affected_entity :NVIDIA' in ttl_str
    assert ':future true' in ttl_str
    assert ':MeetingAndEncounter' in ttl_str       # interview
    assert 'a :Quote ; :text "I want to work for NVIDIA. My interview is tomorrow' in ttl_str
    assert ':attributed_to :Jane' in ttl_str
    # Output Turtle:
    # :Narrative_foo :has_component :Sentence_5575dcb4-4951 .
    # :Sentence_5575dcb4-4951 a :Sentence ; :offset 1 .
    # :Sentence_5575dcb4-4951 :text "Jane said, \'I want to work for NVIDIA." .
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
    # :Sentence_5575dcb4-4951 :mentions :Jane .
    # :Sentence_5575dcb4-4951 :mentions :NVIDIA .
    # :Sentence_5575dcb4-4951 :grade_level 5 .
    # :Narrative_foo :has_component :Sentence_ed92fc32-37e2 .
    # :Sentence_ed92fc32-37e2 a :Sentence ; :offset 2 .
    # :Sentence_ed92fc32-37e2 :text "My interview is tomorrow.\'" .
    # :Sentence_ed92fc32-37e2 :grade_level 3 .
    # :Narrative_foo :describes :NarrativeEvent_56ffe6b5-6ca6 .
    # :NarrativeEvent_56ffe6b5-6ca6 a :NarrativeEvent ; :offset 0 .
    # :NarrativeEvent_56ffe6b5-6ca6 :text "Jane expressed a desire to work for NVIDIA." .
    # :NarrativeEvent_56ffe6b5-6ca6 :has_semantic :Event_9c3333c5-b491 .
    # :NarrativeEvent_56ffe6b5-6ca6 :has_first :Event_9c3333c5-b491 .
    # :Event_9c3333c5-b491 :text "Jane expressed a desire." .
    # :Event_9c3333c5-b491 a :EmotionalResponse ; :confidence-EmotionalResponse 90 .
    # :Event_9c3333c5-b491 a :CommunicationAndSpeechAct ; :confidence-CommunicationAndSpeechAct 80 .
    # :Event_9c3333c5-b491 :has_active_entity :Jane .
    # :NarrativeEvent_56ffe6b5-6ca6 :has_semantic :Event_feca9834-4b18 .
    # :Event_9c3333c5-b491 :has_next :Event_feca9834-4b18 .
    # :Event_feca9834-4b18 :text "Jane wants to work for NVIDIA." .
    # :Event_feca9834-4b18 a :Affiliation ; :confidence-Affiliation 85 .
    # :Event_feca9834-4b18 a :Attempt ; :confidence-Attempt 75 .
    # :Event_feca9834-4b18 :has_context :Jane .
    # :Event_feca9834-4b18 :affiliated_with :NVIDIA .
    # :Narrative_foo :describes :NarrativeEvent_c969f067-8374 .
    # :NarrativeEvent_c969f067-8374 a :NarrativeEvent ; :offset 1 .
    # :NarrativeEvent_c969f067-8374 :text "Jane has an interview scheduled for tomorrow." .
    # :NarrativeEvent_c969f067-8374 :has_semantic :Event_1244975c-eb34 .
    # :NarrativeEvent_c969f067-8374 :has_first :Event_1244975c-eb34 .
    # :Event_1244975c-eb34 :text "Jane has an interview scheduled." .
    # :Event_1244975c-eb34 :future true .
    # :Event_1244975c-eb34 a :MeetingAndEncounter ; :confidence-MeetingAndEncounter 90 .
    # :Event_1244975c-eb34 a :ReadinessAndAbility ; :confidence-ReadinessAndAbility 80 .
    # :Event_1244975c-eb34 :has_active_entity :Jane .
    # :Noun_58e35483-df3d a :CommunicationAndSpeechAct ; :text "interview" ; :confidence 90 .
    # :Event_1244975c-eb34 :has_topic :Noun_58e35483-df3d .
    # :Quotation_65a72f4e-a60d a :Quote ; :text "I want to work for NVIDIA. My interview is tomorrow." .
    # :Quotation_65a72f4e-a60d :attributed_to :Jane .
    # :Quotation_65a72f4e-a60d :grade_level 5 .


def test_rule():
    sentence_classes, quotation_classes = parse_narrative(text_rule)
    graph_results = create_graph(sentence_classes, quotation_classes, text_rule,
                                 ':Narrative_foo', [], 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':CommunicationAndSpeechAct' in ttl_str
    assert ':LawAndPolicy' in ttl_str and ':has_topic' in ttl_str
    # Output Turtle:
    # :Narrative_foo :has_component :Sentence_86a20450-1c2d .
    # :Sentence_86a20450-1c2d a :Sentence ; :offset 1 .
    # :Sentence_86a20450-1c2d :text "You shall not kill." .
    # :Sentence_86a20450-1c2d :grade_level 5 .
    # :Narrative_foo :describes :NarrativeEvent_d5367f99-cc09 .
    # :NarrativeEvent_d5367f99-cc09 a :NarrativeEvent ; :offset 0 .
    # :NarrativeEvent_d5367f99-cc09 :text "The narrative discusses the commandment \'You shall not kill.\'" .
    # :NarrativeEvent_d5367f99-cc09 :has_semantic :Event_8a8d688c-bb46 .
    # :NarrativeEvent_d5367f99-cc09 :has_first :Event_8a8d688c-bb46 .
    # :Event_8a8d688c-bb46 :text "The narrative discusses the commandment \'You shall not kill.\'" .
    # :Event_8a8d688c-bb46 a :CommunicationAndSpeechAct ; :confidence-CommunicationAndSpeechAct 90 .
    # :Noun_8ecb94ed-dcad a :CommunicationAndSpeechAct ; :text "narrative" ; :confidence 85 .
    # :Event_8a8d688c-bb46 :has_active_entity :Noun_8ecb94ed-dcad .
    # :Noun_601e1e8e-ea05 a :LawAndPolicy ; :text "commandment" ; :confidence 90 .
    # :Event_8a8d688c-bb46 :has_topic :Noun_601e1e8e-ea05 .
    # TODO: Need to include the specific 'commandment'


def test_causation():
    sentence_classes, quotation_classes = parse_narrative(text_causation)
    graph_results = create_graph(sentence_classes, quotation_classes, text_causation,
                                 ':Narrative_foo', [], 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':BodilyAct' in ttl_str or ':ArtAndEntertainmentEvent' in ttl_str or \
           ':MovementTravelAndTransportation' in ttl_str
    assert ':has_active_entity :Holly' in ttl_str
    assert ':HealthAndDiseaseRelated' in ttl_str
    assert ':ComponentPart ; :text "ankle' in ttl_str     # TODO: Error, missing
    assert ':has_affected_entity :Noun' in ttl_str                  # twisted ankle
    assert ':ImpactAndContact' in ttl_str
    assert ':has_active_entity :David' in ttl_str
    assert ':has_affected_entity :Holly' in ttl_str
    # Output Turtle:
    # :Narrative_foo :has_component :Sentence_51ce7447-72ea .
    # :Sentence_51ce7447-72ea a :Sentence ; :offset 1 .
    # :Sentence_51ce7447-72ea :text "Yesterday Holly was running a marathon when she twisted her ankle." .
    # :Sentence_51ce7447-72ea :mentions :Holly .
    # :Sentence_51ce7447-72ea :grade_level 6 .
    # :Narrative_foo :has_component :Sentence_2eeb97b2-05a1 .
    # :Sentence_2eeb97b2-05a1 a :Sentence ; :offset 2 .
    # :Sentence_2eeb97b2-05a1 :text "David had pushed her." .
    # :Sentence_2eeb97b2-05a1 :mentions :David .
    # :Sentence_2eeb97b2-05a1 :grade_level 3 .
    # :Narrative_foo :describes :NarrativeEvent_65100627-228d .
    # :NarrativeEvent_65100627-228d a :NarrativeEvent ; :offset 0 .
    # :NarrativeEvent_65100627-228d :text "Holly was running a marathon." .
    # :NarrativeEvent_65100627-228d :has_semantic :Event_6df242ff-b746 .
    # :NarrativeEvent_65100627-228d :has_first :Event_6df242ff-b746 .
    # :Event_6df242ff-b746 :text "Holly was running a marathon." .
    # :Event_6df242ff-b746 a :ArtAndEntertainmentEvent ; :confidence-ArtAndEntertainmentEvent 95 .
    # :Event_6df242ff-b746 a :MovementTravelAndTransportation ; :confidence-MovementTravelAndTransportation 85 .
    # :Event_6df242ff-b746 :has_active_entity :Holly .
    # :Noun_9f4cac16-ac6d a :ArtAndEntertainmentEvent ; :text "marathon" ; :confidence 90 .
    # :Event_6df242ff-b746 :has_topic :Noun_9f4cac16-ac6d .
    # :Narrative_foo :describes :NarrativeEvent_72fe03c3-edd5 .
    # :NarrativeEvent_72fe03c3-edd5 a :NarrativeEvent ; :offset 1 .
    # :NarrativeEvent_72fe03c3-edd5 :text "Holly twisted her ankle." .
    # :NarrativeEvent_72fe03c3-edd5 :has_semantic :Event_7837fb0b-8863 .
    # :NarrativeEvent_72fe03c3-edd5 :has_first :Event_7837fb0b-8863 .
    # :Event_7837fb0b-8863 :text "Holly twisted her ankle." .
    # :Event_7837fb0b-8863 a :HealthAndDiseaseRelated ; :confidence-HealthAndDiseaseRelated 100 .
    # :Event_7837fb0b-8863 a :SensoryPerception ; :confidence-SensoryPerception 90 .
    # :Event_7837fb0b-8863 :has_active_entity :Holly .
    # :Noun_5c3f1a6a-f433 a :ComponentPart ; :text "ankle" ; :confidence 100 .
    # :Event_7837fb0b-8863 :has_affected_entity :Noun_5c3f1a6a-f433 .
    # :Narrative_foo :describes :NarrativeEvent_933ca9bc-31d9 .
    # :NarrativeEvent_933ca9bc-31d9 a :NarrativeEvent ; :offset 2 .
    # :NarrativeEvent_933ca9bc-31d9 :text "David had pushed Holly." .
    # :NarrativeEvent_933ca9bc-31d9 :has_semantic :Event_1db4649a-ca88 .
    # :NarrativeEvent_933ca9bc-31d9 :has_first :Event_1db4649a-ca88 .
    # :Event_1db4649a-ca88 :text "David pushed Holly." .
    # :Event_1db4649a-ca88 a :CrimeAndHostileConflict ; :confidence-CrimeAndHostileConflict 90 .
    # :Event_1db4649a-ca88 a :ImpactAndContact ; :confidence-ImpactAndContact 80 .
    # :Event_1db4649a-ca88 :has_active_entity :David .
    # :Event_1db4649a-ca88 :has_affected_entity :Holly .
