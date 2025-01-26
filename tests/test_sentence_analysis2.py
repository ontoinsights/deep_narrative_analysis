import pytest
from dna.create_narrative_turtle import create_graph
from dna.nlp import parse_narrative

# Latest execution, Jan 25: All tests passed

text_possessive = "Joe's foot hit the table."
text_communication = 'Liz Cheney claimed that Donald Trump is promoting an insidious lie about the recent ' \
                     'FBI raid of his Mar-a-Lago residence.'
text_multiple_verbs = 'Sue is an attorney but still lies.'
text_aux_pobj = 'Jack got rid of the debris.'
text_idiom_amod = "Jack turned a blind eye to Mary's infidelity."
text_complex_verb = 'The store went out of business on Tuesday.'
text_non_person_subject = "Jack's hopes were dashed."
text_first_person = 'I was not ready to leave.'
text_pobj_semantics = 'The robber escaped with the aid of the local police.'
text_multiple_subjects = 'Jane and Jack had a serious difference of opinion.'
text_multiple_xcomp = 'Jack liked to ski and to swim.'
text_location_hierarchy = "Switzerland's mountains are magnificent."
text_weather = "Hurricane Otis severely damaged Acapulco."
text_coref = 'Anna saw Heidi cut the roses, but she did not recognize that it was Heidi who cut the roses.'
text_quotation = 'Jane said, "I want to work for NVIDIA. My interview is tomorrow."'
text_rule = "You shall not kill."
text_causation = "Yesterday Holly was running a marathon when she twisted her ankle. Jack had pushed her."

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
    assert ':LawEnforcement, :Collection ; :text "recent FBI raid' in ttl_str and ':has_topic :Noun' in ttl_str
    assert ':Location ; :text "Donald Trump' in ttl_str and (':has_location :Noun' in ttl_str or
                                                             ':has_context :Noun' in ttl_str)
    # Output Turtle:
    # :Narrative_foo :has_component :Sentence_6944282a-f994 .
    # :Sentence_6944282a-f994 a :Sentence ; :offset 1 .
    # :Sentence_6944282a-f994 :text "Liz Cheney claimed that Donald Trump is promoting an insidious lie about the
    #     recent FBI raid of his Mar-a-Lago residence." .
    # :Sentence_6944282a-f994 :mentions :Liz_Cheney .
    # :Sentence_6944282a-f994 :mentions :Donald_Trump .
    # :Sentence_6944282a-f994 :mentions :FBI .
    # :Sentence_6944282a-f994 :mentions :Mar_a_Lago .
    # :Sentence_6944282a-f994 :grade_level 10 .
    # :Sentence_6944282a-f994 :rhetorical_device "loaded language" .
    # :Sentence_6944282a-f994 :rhetorical_device_loaded_language "The phrase \'insidious lie\' uses loaded language
    #     with strong connotations that invoke emotions and judgments about the nature of the lie being described." .
    # :Narrative_foo :describes :NarrativeEvent_bfc529c7-0e39 .
    # :NarrativeEvent_bfc529c7-0e39 a :NarrativeEvent ; :offset 0 .
    # :NarrativeEvent_bfc529c7-0e39 :text "Liz Cheney claimed that Donald Trump is promoting an insidious lie about the
    #     recent FBI raid of his Mar-a-Lago residence." .
    # :NarrativeEvent_bfc529c7-0e39 :has_semantic :Event_51cfc393-30b1 .
    # :NarrativeEvent_bfc529c7-0e39 :has_first :Event_51cfc393-30b1 .
    # :Event_51cfc393-30b1 :text "Liz Cheney claimed." .
    # :Event_51cfc393-30b1 a :CommunicationAndSpeechAct ; :confidence-CommunicationAndSpeechAct 100 .
    # :Event_51cfc393-30b1 :has_active_entity :Liz_Cheney .
    # :NarrativeEvent_bfc529c7-0e39 :has_semantic :Event_78499d1e-69b9 .
    # :Event_51cfc393-30b1 :has_next :Event_78499d1e-69b9 .
    # :Event_78499d1e-69b9 :text "Donald Trump is promoting an insidious lie." .
    # :Event_78499d1e-69b9 a :DeceptionAndDishonesty ; :confidence-DeceptionAndDishonesty 100 .
    # :Event_78499d1e-69b9 :has_active_entity :Donald_Trump .
    # :Noun_4e6aba57-a25f a :DeceptionAndDishonesty ; :text "insidious lie" ; :confidence 95 .
    # :Event_78499d1e-69b9 :has_topic :Noun_4e6aba57-a25f .
    # :NarrativeEvent_bfc529c7-0e39 :has_semantic :Event_b381d5e4-5015 .
    # :Event_78499d1e-69b9 :has_next :Event_b381d5e4-5015 .
    # :Event_b381d5e4-5015 :text "The insidious lie is about the recent FBI raid of Donald Trump\'s Mar-a-Lago
    #     residence." .
    # :Event_b381d5e4-5015 a :CommunicationAndSpeechAct ; :confidence-CommunicationAndSpeechAct 90 .
    # :Event_b381d5e4-5015 :has_topic :Noun_4e6aba57-a25f .
    # :Noun_efcdbb33-0fdf a :LawEnforcement, :Collection ; :text "recent FBI raid" ; :confidence 95 .
    # :Event_b381d5e4-5015 :has_topic :Noun_efcdbb33-0fdf .
    # :Noun_e2df6cdb-57f0 a :Location ; :text "Donald Trump\'s Mar-a-Lago residence" ; :confidence 95 .
    # :Noun_e2df6cdb-57f0 :clarifying_reference :Donald_Trump .
    # :Noun_e2df6cdb-57f0 :clarifying_text "Donald Trump\'s" .
    # :Event_b381d5e4-5015 :has_location :Noun_e2df6cdb-57f0 .


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
    assert ':has_active_entity :Jack' in ttl_str
    assert ':WasteAndResidue' in ttl_str and ':text "debris' in ttl_str
    assert ':has_topic :Noun' in ttl_str or ':has_affected_entity :Noun' in ttl_str
    # Output Turtle:
    # :Narrative_foo :has_component :Sentence_58d2eb3c-f5dc .
    # :Sentence_58d2eb3c-f5dc a :Sentence ; :offset 1 .
    # :Sentence_58d2eb3c-f5dc :text "Jack got rid of the debris." .
    # :Jack :text "Jack" .
    # :Jack a :Person, :Correction .
    # :Jack rdfs:label "Jack" .
    # :Jack :gender "male" .
    # :Sentence_58d2eb3c-f5dc :mentions :Jack .
    # :Sentence_58d2eb3c-f5dc :grade_level 3 .
    # :Narrative_foo :describes :NarrativeEvent_438e8a91-f942 .
    # :NarrativeEvent_438e8a91-f942 a :NarrativeEvent ; :offset 0 .
    # :NarrativeEvent_438e8a91-f942 :text "Jack got rid of the debris." .
    # :NarrativeEvent_438e8a91-f942 :has_semantic :Event_4d97d89c-7bad .
    # :NarrativeEvent_438e8a91-f942 :has_first :Event_4d97d89c-7bad .
    # :Event_4d97d89c-7bad :text "Jack got rid of the debris." .
    # :Event_4d97d89c-7bad a :RemovalAndRestriction ; :confidence-RemovalAndRestriction 100 .
    # :Event_4d97d89c-7bad :has_active_entity :Jack .
    # :Noun_ba0765e6-05e3 a :WasteAndResidue, :Collection ; :text "debris" ; :confidence 100 .
    # :Event_4d97d89c-7bad :has_affected_entity :Noun_ba0765e6-05e3 .


def test_idiom_amod():
    sentence_classes, quotation_classes = parse_narrative(text_idiom_amod)
    graph_results = create_graph(sentence_classes, quotation_classes, text_idiom_amod,
                                 ':Narrative_foo', [],5, repo)
    ttl_str = str(graph_results.turtle)
    assert "allusion" in ttl_str
    assert ':Avoidance' in ttl_str
    assert ':has_active_entity :Jack' in ttl_str
    assert ':DeceptionAndDishonesty' in ttl_str
    assert ':has_topic :Noun' in ttl_str
    assert ':clarifying_text "Mary' in ttl_str
    # Output Turtle:
    # :Narrative_foo :has_component :Sentence_3d409906-8700 .
    # :Sentence_3d409906-8700 a :Sentence ; :offset 1 .
    # :Sentence_3d409906-8700 :text "Jack turned a blind eye to Mary\'s infidelity." .
    # :Sentence_3d409906-8700 :mentions :Jack .
    # :Sentence_3d409906-8700 :mentions :Mary .
    # :Sentence_3d409906-8700 :grade_level 8 .
    # :Sentence_3d409906-8700 :rhetorical_device "allusion" .
    # :Sentence_3d409906-8700 :rhetorical_device_allusion "The phrase \'turned a blind eye\' is an allusion to the
    #     historical anecdote about Admiral Horatio Nelson, who purportedly used his blind eye to look through a
    #     telescope and claim he did not see a signal to withdraw, symbolizing willful ignorance." .
    # :Narrative_foo :describes :NarrativeEvent_4e38b40f-3323 .
    # :NarrativeEvent_4e38b40f-3323 a :NarrativeEvent ; :offset 0 .
    # :NarrativeEvent_4e38b40f-3323 :text "Jack ignored Mary\'s infidelity." .
    # :NarrativeEvent_4e38b40f-3323 :has_semantic :Event_13751bad-920c .
    # :NarrativeEvent_4e38b40f-3323 :has_first :Event_13751bad-920c .
    # :Event_13751bad-920c :text "Jack ignored Mary\'s infidelity." .
    # :Event_13751bad-920c a :Avoidance ; :confidence-Avoidance 90 .
    # :Event_13751bad-920c :has_active_entity :Jack .
    # :Noun_db390172-6dd8 a :DeceptionAndDishonesty ; :text "Mary\'s infidelity" ; :confidence 90 .
    # :Noun_db390172-6dd8 :clarifying_reference :Mary .
    # :Noun_db390172-6dd8 :clarifying_text "Mary\'s" .
    # :Event_13751bad-920c :has_topic :Noun_db390172-6dd8 .


def test_complex_verb():
    sentence_classes, quotation_classes = parse_narrative(text_complex_verb)
    graph_results = create_graph(sentence_classes, quotation_classes, text_complex_verb,
                                 ':Narrative_foo', [], 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':End' in ttl_str or ':EconomyAndFinanceRelated' in ttl_str
    assert ':OrganizationalEntity' in ttl_str or ':Location' in ttl_str      # store
    assert ':has_active_entity :Noun' in ttl_str
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

def test_non_person_subject():
    sentence_classes, quotation_classes = parse_narrative(text_non_person_subject)
    graph_results = create_graph(sentence_classes, quotation_classes, text_non_person_subject,
                                 ':Narrative_foo', [], 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':Loss' in ttl_str
    assert ':has_active_entity :Jack' in ttl_str or ':has_topic :Jack' in ttl_str
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
    # :Event_ad815027-226c :has_active_entity :John .
    # TODO: Capture the concept of "hopes"


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
    assert ':has_active_entity :Jack' in ttl_str
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
    assert ':has_active_entity :Jack' in ttl_str
    # Output Turtle:
    # :Narrative_foo :has_component :Sentence_01f54ead-0eb4 .
    # :Sentence_01f54ead-0eb4 a :Sentence ; :offset 1 .
    # :Sentence_01f54ead-0eb4 :text "Jack liked to ski and to swim." .
    # :Sentence_01f54ead-0eb4 :mentions :Jack .
    # :Sentence_01f54ead-0eb4 :grade_level 3 .
    # :Narrative_foo :describes :NarrativeEvent_75e222d0-b6f2 .
    # :NarrativeEvent_75e222d0-b6f2 a :NarrativeEvent ; :offset 0 .
    # :NarrativeEvent_75e222d0-b6f2 :text "Jack liked to ski." .
    # :NarrativeEvent_75e222d0-b6f2 :has_semantic :Event_3915a064-eff8 .
    # :NarrativeEvent_75e222d0-b6f2 :has_first :Event_3915a064-eff8 .
    # :Event_3915a064-eff8 :text "Jack liked skiing." .
    # :Event_3915a064-eff8 a :EmotionalResponse ; :confidence-EmotionalResponse 100 .
    # :Event_3915a064-eff8 :has_active_entity :Jack .
    # :Noun_b5359ce5-b9f0 a :BodilyAct, :Collection ; :text "skiing" ; :confidence 90 .
    # :Event_3915a064-eff8 :has_topic :Noun_b5359ce5-b9f0 .
    # :NarrativeEvent_75e222d0-b6f2 :has_semantic :Event_02df2d34-6022 .
    # :Event_3915a064-eff8 :has_next :Event_02df2d34-6022 .
    # :Event_02df2d34-6022 :text "Jack liked to ski." .
    # :Event_02df2d34-6022 a :BodilyAct ; :confidence-BodilyAct 100 .
    # :Event_02df2d34-6022 :has_active_entity :Jack .
    # :Event_02df2d34-6022 :has_topic :Noun_b5359ce5-b9f0 .
    # :Narrative_foo :describes :NarrativeEvent_2465feb5-9a16 .
    # :NarrativeEvent_2465feb5-9a16 a :NarrativeEvent ; :offset 1 .
    # :NarrativeEvent_2465feb5-9a16 :text "Jack liked to swim." .
    # :NarrativeEvent_2465feb5-9a16 :has_semantic :Event_baf28753-75c5 .
    # :NarrativeEvent_2465feb5-9a16 :has_first :Event_baf28753-75c5 .
    # :Event_baf28753-75c5 :text "Jack liked swimming." .
    # :Event_baf28753-75c5 a :EmotionalResponse ; :confidence-EmotionalResponse 100 .
    # :Event_baf28753-75c5 :has_active_entity :Jack .
    # :Noun_49145ee1-ab88 a :BodilyAct, :Collection ; :text "swimming" ; :confidence 95 .
    # :Event_baf28753-75c5 :has_topic :Noun_49145ee1-ab88 .
    # :NarrativeEvent_2465feb5-9a16 :has_semantic :Event_f572e4fa-7187 .
    # :Event_baf28753-75c5 :has_next :Event_f572e4fa-7187 .
    # :Event_f572e4fa-7187 :text "Jack liked to swim." .
    # :Event_f572e4fa-7187 a :BodilyAct ; :confidence-BodilyAct 100 .
    # :Event_f572e4fa-7187 :has_active_entity :Jack .
    # :Event_f572e4fa-7187 :has_topic :Noun_49145ee1-ab88 .


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
    assert ':Plant, :Collection ; :text "roses' in ttl_str
    assert ':has_affected_entity :Noun' in ttl_str or ':has_topic :Noun' in ttl_str
    assert ':Cognition' in ttl_str or ':Mistake' in ttl_str       # not recognize
    assert ':has_active_entity :Heidi' in ttl_str                 # Heidi cut the roses
    # Output Turtle:
    # :Narrative_foo :has_component :Sentence_611aa3be-ac7c .
    # :Sentence_611aa3be-ac7c a :Sentence ; :offset 1 .
    # :Sentence_611aa3be-ac7c :text "Anna saw Heidi cut the roses, but she did not recognize that it was Heidi
    #     who cut the roses." .
    # :Sentence_611aa3be-ac7c :mentions :Anna .
    # :Sentence_611aa3be-ac7c :mentions :Heidi .
    # :Sentence_611aa3be-ac7c :mentions :Heidi .
    # :Sentence_611aa3be-ac7c :grade_level 8 .
    # :Narrative_foo :describes :NarrativeEvent_c2ef2f1b-4be4 .
    # :NarrativeEvent_c2ef2f1b-4be4 a :NarrativeEvent ; :offset 0 .
    # :NarrativeEvent_c2ef2f1b-4be4 :text "Anna saw someone cut the roses." .
    # :NarrativeEvent_c2ef2f1b-4be4 :has_semantic :Event_dea34436-8cd1 .
    # :NarrativeEvent_c2ef2f1b-4be4 :has_first :Event_dea34436-8cd1 .
    # :Event_dea34436-8cd1 :text "Anna saw someone." .
    # :Event_dea34436-8cd1 a :SensoryPerception ; :confidence-SensoryPerception 90 .
    # :Event_dea34436-8cd1 :has_active_entity :Anna .
    # :NarrativeEvent_c2ef2f1b-4be4 :has_semantic :Event_4c025669-6d37 .
    # :Event_dea34436-8cd1 :has_next :Event_4c025669-6d37 .
    # :Event_4c025669-6d37 :text "Someone cut the roses." .
    # :Event_4c025669-6d37 a :Separation ; :confidence-Separation 95 .
    # :Noun_a0912836-e5fb a :Person ; :text "someone" ; :confidence 95 .
    # :Event_4c025669-6d37 :has_active_entity :Noun_a0912836-e5fb .
    # :Noun_f4c8a2be-c0e0 a :Plant, :Collection ; :text "roses" ; :confidence 100 .
    # :Event_4c025669-6d37 :has_affected_entity :Noun_f4c8a2be-c0e0 .
    # :Narrative_foo :describes :NarrativeEvent_bbfac540-4248 .
    # :NarrativeEvent_bbfac540-4248 a :NarrativeEvent ; :offset 1 .
    # :NarrativeEvent_bbfac540-4248 :text "Anna did not recognize that it was Heidi who cut the roses." .
    # :NarrativeEvent_bbfac540-4248 :has_semantic :Event_41b4848c-d424 .
    # :NarrativeEvent_bbfac540-4248 :has_first :Event_41b4848c-d424 .
    # :Event_41b4848c-d424 :text "Anna did not recognize." .
    # :Event_41b4848c-d424 a :Mistake ; :confidence-Mistake 90 .
    # :Event_41b4848c-d424 :has_active_entity :Anna .
    # :NarrativeEvent_bbfac540-4248 :has_semantic :Event_f29f2914-bef6 .
    # :Event_41b4848c-d424 :has_next :Event_f29f2914-bef6 .
    # :Event_f29f2914-bef6 :text "Heidi cut the roses." .
    # :Event_f29f2914-bef6 a :Separation ; :confidence-Separation 95 .
    # :Event_f29f2914-bef6 :has_active_entity :Heidi .
    # :Event_f29f2914-bef6 :has_affected_entity :Noun_f4c8a2be-c0e0 .


def test_quotation():
    sentence_classes, quotation_classes = parse_narrative(text_quotation)
    graph_results = create_graph(sentence_classes, quotation_classes, text_quotation,
                                 ':Narrative_foo', [], 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':mentions :NVIDIA' in ttl_str
    assert ':EmotionalResponse' in ttl_str or ':CommunicationAndSpeechAct' in ttl_str    # expressed desire
    assert ':has_active_entity :Jane' in ttl_str
    assert ':Affiliation' in ttl_str
    assert ':has_topic :NVIDIA' in ttl_str or ':affiliated_with :NVIDIA' in ttl_str
    assert ':MeetingAndEncounter' in ttl_str       # interview
    assert 'a :Quote ; :text "I want to work for NVIDIA. My interview is tomorrow' in ttl_str
    assert ':attributed_to :Jane' in ttl_str
    # Output Turtle:
    # :Narrative_foo :has_component :Sentence_2ee30a44-4d6d .
    # :Sentence_2ee30a44-4d6d a :Sentence ; :offset 1 .
    # :Sentence_2ee30a44-4d6d :text "Jane said, \'I want to work for NVIDIA." .
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
    # :Sentence_2ee30a44-4d6d :mentions :Jane .
    # :Sentence_2ee30a44-4d6d :mentions :NVIDIA .
    # :Sentence_2ee30a44-4d6d :grade_level 5 .
    # :Narrative_foo :has_component :Sentence_9e8051a8-b2ec .
    # :Sentence_9e8051a8-b2ec a :Sentence ; :offset 2 .
    # :Sentence_9e8051a8-b2ec :text "My interview is tomorrow.\'" .
    # :Sentence_9e8051a8-b2ec :grade_level 3 .
    # :Narrative_foo :describes :NarrativeEvent_6c67c62e-8f79 .
    # :NarrativeEvent_6c67c62e-8f79 a :NarrativeEvent ; :offset 0 .
    # :NarrativeEvent_6c67c62e-8f79 :text "Jane expressed a desire to work for NVIDIA." .
    # :NarrativeEvent_6c67c62e-8f79 :has_semantic :Event_e562a3c8-183c .
    # :NarrativeEvent_6c67c62e-8f79 :has_first :Event_e562a3c8-183c .
    # :Event_e562a3c8-183c :text "Jane expressed a desire." .
    # :Event_e562a3c8-183c a :EmotionalResponse ; :confidence-EmotionalResponse 100 .
    # :Event_e562a3c8-183c :has_active_entity :Jane .
    # :Noun_970846a9-f801 a :EmotionalResponse ; :text "desire" ; :confidence 90 .
    # :Event_e562a3c8-183c :has_topic :Noun_970846a9-f801 .
    # :NarrativeEvent_6c67c62e-8f79 :has_semantic :Event_60a65678-8058 .
    # :Event_e562a3c8-183c :has_next :Event_60a65678-8058 .
    # :Event_60a65678-8058 :text "Jane wants to work for NVIDIA." .
    # :Event_60a65678-8058 a :Affiliation ; :confidence-Affiliation 100 .
    # :Event_60a65678-8058 :has_context :Jane .
    # :Event_60a65678-8058 :affiliated_with :NVIDIA .
    # :Narrative_foo :describes :NarrativeEvent_a48edc1e-0c76 .
    # :NarrativeEvent_a48edc1e-0c76 a :NarrativeEvent ; :offset 1 .
    # :NarrativeEvent_a48edc1e-0c76 :text "Jane has an interview scheduled for tomorrow." .
    # :NarrativeEvent_a48edc1e-0c76 :has_semantic :Event_d2d78023-e492 .
    # :NarrativeEvent_a48edc1e-0c76 :has_first :Event_d2d78023-e492 .
    # :Event_d2d78023-e492 :text "Jane has an interview." .
    # :Event_d2d78023-e492 a :MeetingAndEncounter ; :confidence-MeetingAndEncounter 90 .
    # :Event_d2d78023-e492 :has_active_entity :Jane .
    # :NarrativeEvent_a48edc1e-0c76 :has_semantic :Event_5cbfb50e-506a .
    # :Event_d2d78023-e492 :has_next :Event_5cbfb50e-506a .
    # :Event_5cbfb50e-506a :text "The interview is scheduled for tomorrow." .
    # :Event_5cbfb50e-506a a :DelayAndWait ; :confidence-DelayAndWait 85 .
    # :Noun_6d9356b0-9cd3 a :CommunicationAndSpeechAct ; :text "interview" ; :confidence 90 .
    # :Event_5cbfb50e-506a :has_topic :Noun_6d9356b0-9cd3 .
    # :Quotation_ab98047c-4e3d a :Quote ; :text "I want to work for NVIDIA. My interview is tomorrow." .
    # :Quotation_ab98047c-4e3d :attributed_to :Jane .
    # :Quotation_ab98047c-4e3d :grade_level 5 .


def test_rule():
    sentence_classes, quotation_classes = parse_narrative(text_rule)
    graph_results = create_graph(sentence_classes, quotation_classes, text_rule,
                                 ':Narrative_foo', [], 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':CommunicationAndSpeechAct' in ttl_str
    assert ':LawAndPolicy' in ttl_str and ':has_topic' in ttl_str
    assert ':Avoidance' in ttl_str and ':CrimeAndHostileConflict' in ttl_str and ':text "killing' in ttl_str
    # Output Turtle:
    # :Narrative_foo :has_component :Sentence_33b525a1-fa20 .
    # :Sentence_33b525a1-fa20 a :Sentence ; :offset 1 .
    # :Sentence_33b525a1-fa20 :text "You shall not kill." .
    # :Sentence_33b525a1-fa20 :grade_level 5 .
    # :Narrative_foo :describes :NarrativeEvent_fab01388-9b06 .
    # :NarrativeEvent_fab01388-9b06 a :NarrativeEvent ; :offset 0 .
    # :NarrativeEvent_fab01388-9b06 :text "A commandment is given that prohibits killing." .
    # :NarrativeEvent_fab01388-9b06 :has_semantic :Event_0b2d7a86-278c .
    # :NarrativeEvent_fab01388-9b06 :has_first :Event_0b2d7a86-278c .
    # :Event_0b2d7a86-278c :text "A commandment is given." .
    # :Event_0b2d7a86-278c a :CommunicationAndSpeechAct ; :confidence-CommunicationAndSpeechAct 90 .
    # :Noun_2beea8d6-dfb2 a :LawAndPolicy ; :text "commandment" ; :confidence 90 .
    # :Event_0b2d7a86-278c :has_topic :Noun_2beea8d6-dfb2 .
    # :NarrativeEvent_fab01388-9b06 :has_semantic :Event_4194a828-fc4f .
    # :Event_bd1bb433-d78b :has_next :Event_4194a828-fc4f .
    # :Event_4194a828-fc4f :text "The commandment prohibits killing." .
    # :Event_4194a828-fc4f a :Avoidance ; :confidence-Avoidance 95 .
    # :Event_4194a828-fc4f :has_active_entity :Noun_2beea8d6-dfb2 .
    # :Noun_096b0e05-5f64 a :CrimeAndHostileConflict, :Collection ; :text "killing" ; :confidence 95 .
    # :Event_4194a828-fc4f :has_topic :Noun_096b0e05-5f64 .


def test_causation():
    sentence_classes, quotation_classes = parse_narrative(text_causation)
    graph_results = create_graph(sentence_classes, quotation_classes, text_causation,
                                 ':Narrative_foo', [], 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':BodilyAct' in ttl_str or ':ArtAndEntertainmentEvent' in ttl_str or \
           ':MovementTravelAndTransportation' in ttl_str
    assert ':has_active_entity :Holly' in ttl_str
    assert ':HealthAndDiseaseRelated' in ttl_str
    assert ':ComponentPart ; :text "ankle' in ttl_str
    assert ':has_affected_entity :Noun' in ttl_str                  # twisted ankle
    assert ':ImpactAndContact' in ttl_str
    assert ':has_active_entity :Jack' in ttl_str
    assert ':has_affected_entity :Holly' in ttl_str
    # Output Turtle:
    # :Narrative_foo :has_component :Sentence_c85c21d4-409f .
    # :Sentence_c85c21d4-409f a :Sentence ; :offset 1 .
    # :Sentence_c85c21d4-409f :text "Yesterday Holly was running a marathon when she twisted her ankle." .
    # :Sentence_c85c21d4-409f :mentions :Holly .
    # :Sentence_c85c21d4-409f :grade_level 6 .
    # :Narrative_foo :has_component :Sentence_9f3267ac-3363 .
    # :Sentence_9f3267ac-3363 a :Sentence ; :offset 2 .
    # :Sentence_9f3267ac-3363 :text "Jack had pushed her." .
    # :Sentence_9f3267ac-3363 :mentions :Jack .
    # :Sentence_9f3267ac-3363 :grade_level 3 .
    # :Narrative_foo :describes :NarrativeEvent_8189eea4-c8be .
    # :NarrativeEvent_8189eea4-c8be a :NarrativeEvent ; :offset 0 .
    # :NarrativeEvent_8189eea4-c8be :text "Holly was running a marathon." .
    # :NarrativeEvent_8189eea4-c8be :has_semantic :Event_e4aaaf65-f138 .
    # :NarrativeEvent_8189eea4-c8be :has_first :Event_e4aaaf65-f138 .
    # :Event_e4aaaf65-f138 :text "Holly was running." .
    # :Event_e4aaaf65-f138 a :BodilyAct ; :confidence-BodilyAct 100 .
    # :Event_e4aaaf65-f138 :has_active_entity :Holly .
    # :NarrativeEvent_8189eea4-c8be :has_semantic :Event_06e45d0e-4068 .
    # :Event_e4aaaf65-f138 :has_next :Event_06e45d0e-4068 .
    # :Event_06e45d0e-4068 :text "Holly was running a marathon." .
    # :Event_06e45d0e-4068 a :ArtAndEntertainmentEvent ; :confidence-ArtAndEntertainmentEvent 100 .
    # :Event_06e45d0e-4068 :has_active_entity :Holly .
    # :Noun_e6c05f13-7d47 a :ArtAndEntertainmentEvent ; :text "marathon" ; :confidence 90 .
    # :Event_06e45d0e-4068 :has_topic :Noun_e6c05f13-7d47 .
    # :Narrative_foo :describes :NarrativeEvent_e551fdca-4f61 .
    # :NarrativeEvent_e551fdca-4f61 a :NarrativeEvent ; :offset 1 .
    # :NarrativeEvent_e551fdca-4f61 :text "Holly twisted her ankle." .
    # :NarrativeEvent_e551fdca-4f61 :has_semantic :Event_8a577875-b17d .
    # :NarrativeEvent_e551fdca-4f61 :has_first :Event_8a577875-b17d .
    # :Event_8a577875-b17d :text "Holly twisted her ankle." .
    # :Event_8a577875-b17d a :HealthAndDiseaseRelated ; :confidence-HealthAndDiseaseRelated 100 .
    # :Event_8a577875-b17d :has_active_entity :Holly .
    # :Noun_ca55d40c-aabd a :ComponentPart ; :text "ankle" ; :confidence 100 .
    # :Event_8a577875-b17d :has_affected_entity :Noun_ca55d40c-aabd .
    # :Narrative_foo :describes :NarrativeEvent_ebe4572c-47d4 .
    # :NarrativeEvent_ebe4572c-47d4 a :NarrativeEvent ; :offset 2 .
    # :NarrativeEvent_ebe4572c-47d4 :text "Jack had pushed Holly." .
    # :NarrativeEvent_ebe4572c-47d4 :has_semantic :Event_80935f75-0d35 .
    # :NarrativeEvent_ebe4572c-47d4 :has_first :Event_80935f75-0d35 .
    # :Event_80935f75-0d35 :text "Jack pushed Holly." .
    # :Event_80935f75-0d35 a :ImpactAndContact ; :confidence-ImpactAndContact 100 .
    # :Event_80935f75-0d35 :has_active_entity :Jack .
    # :Event_80935f75-0d35 :has_affected_entity :Holly .
