import pytest
from dna.create_narrative_turtle import create_graph
from dna.nlp import parse_narrative

text_multiple_entities = 'Liz Cheney claimed that Trump is promoting an insidious lie about the recent ' \
                         'FBI raid of his Mar-a-Lago residence.'
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
text_rule = "You shall not kill."

repo = 'foo'

# Note that it is unlikely that all tests will complete successfully since event semantics can be
# interpreted/reported in multiple ways
# 80%+ of the tests should pass


def test_multiple_entities():
    parse_results = parse_narrative(text_multiple_entities)
    graph_results = create_graph(parse_results.sentence_classes, parse_results.quotation_classes,
                                 parse_results.partial_quotes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert 'loaded language' in ttl_str
    assert ':CommunicationAndSpeechAct' in ttl_str and ':text "claimed' in ttl_str
    assert ':DeceptionAndDishonesty' in ttl_str and ':text "insidious lie' in ttl_str
    assert ':has_active_entity :Liz_Cheney' in ttl_str
    assert ':has_topic :Noun' in ttl_str or ':has_topic :Donald_Trump'   # Topic is Trump's lie
    assert ':has_active_entity :Donald_Trump' in ttl_str                 # Trump is promoting the lie
    assert ':LawEnforcement ; :text "FBI raid' in ttl_str
    assert ':Location' in ttl_str and 'residence"' in ttl_str and ':has_location :Noun' in ttl_str
    # Output Turtle:
    # :Sentence_b1e82338-85a1 a :Sentence ; :offset 1 .
    # :Sentence_b1e82338-85a1 :text "Liz Cheney claimed that Trump is promoting an insidious lie about the recent
    #     FBI raid of his Mar-a-Lago residence." .
    # :Sentence_b1e82338-85a1 :mentions :Liz_Cheney .
    # :Sentence_b1e82338-85a1 :mentions :Donald_Trump .
    # :Sentence_b1e82338-85a1 :mentions :FBI .
    # :Sentence_b1e82338-85a1 :mentions :Mar_a_Lago .
    # :Sentence_b1e82338-85a1 :grade_level 10 .
    # :Sentence_b1e82338-85a1 :rhetorical_device "loaded language" .
    # :Sentence_b1e82338-85a1 :rhetorical_device_loaded_language "The phrase \'insidious lie\' uses loaded
    #     language with strong connotations that invoke emotions and judgments about the nature of the lie
    #     being described." .
    # :Sentence_b1e82338-85a1 :summary "Cheney accuses Trump of lying about FBI raid." .
    # :Sentence_b1e82338-85a1 :has_semantic :Event_bce136ec-b0bf .
    # :Event_bce136ec-b0bf :text "claimed" .
    # :Event_bce136ec-b0bf a :CommunicationAndSpeechAct ; :confidence-CommunicationAndSpeechAct 95 .
    # :Event_bce136ec-b0bf :has_active_entity :Liz_Cheney .
    # :Event_bce136ec-b0bf :has_topic :Donald_Trump .
    # :Noun_945b5314-931e a :DeceptionAndDishonesty ; :text "insidious lie" ; :confidence 95 .
    # :Event_bce136ec-b0bf :has_context :Noun_945b5314-931e .
    # :Sentence_b1e82338-85a1 :has_semantic :Event_9c0e0946-dff6 .
    # :Event_9c0e0946-dff6 :text "is promoting" .
    # :Event_9c0e0946-dff6 a :DeceptionAndDishonesty ; :confidence-DeceptionAndDishonesty 90 .
    # :Event_9c0e0946-dff6 :has_active_entity :Donald_Trump .
    # :Event_9c0e0946-dff6 :text "insidious lie" .
    # :Noun_7ae48ef0-e718 a :LawEnforcement ; :text "FBI raid" ; :confidence 90 .
    # :Event_9c0e0946-dff6 :has_context :Noun_7ae48ef0-e718 .
    # :Noun_645486aa-c7a0 a :Location ; :text "Mar-a-Lago residence" ; :confidence 100 .
    # :Event_9c0e0946-dff6 :has_location :Noun_645486aa-c7a0 .


def test_multiple_verbs():
    parse_results = parse_narrative(text_multiple_verbs)
    graph_results = create_graph(parse_results.sentence_classes, parse_results.quotation_classes,
                                 parse_results.partial_quotes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert 'ad hominem' in ttl_str or 'loaded language' in ttl_str
    assert ':EnvironmentAndCondition' in ttl_str and ':text "is' in ttl_str
    assert ':LineOfBusiness ; :text "attorney' in ttl_str and ':has_aspect :Noun' in ttl_str
    assert ':has_context :Sue' in ttl_str
    assert ':text "lies' in ttl_str and ':DeceptionAndDishonesty' in ttl_str
    assert ':has_active_entity :Sue' in ttl_str
    # Output Turtle:
    # :Sentence_cc657637-9320 a :Sentence ; :offset 1 .
    # :Sentence_cc657637-9320 :text "Sue is an attorney but still lies." .
    # :Sentence_cc657637-9320 :mentions :Sue .
    # :Sentence_cc657637-9320 :grade_level 8 .
    # :Sentence_cc657637-9320 :rhetorical_device "loaded language" .
    # :Sentence_cc657637-9320 :rhetorical_device_loaded_language "The word \'lies\' is loaded language with
    #     strong connotations, invoking emotions and judgments about Sue\'s character." .
    # :Sentence_cc657637-9320 :summary "Sue is an attorney but lies." .
    # :Sentence_cc657637-9320 :has_semantic :Event_847b69db-ea21 .
    # :Event_847b69db-ea21 :text "is" .
    # :Event_847b69db-ea21 a :EnvironmentAndCondition ; :confidence-EnvironmentAndCondition 100 .
    # :Event_847b69db-ea21 :has_context :Sue .
    # :Noun_13c99ece-ebdb a :LineOfBusiness ; :text "attorney" ; :confidence 100 .
    # :Event_847b69db-ea21 :has_aspect :Noun_13c99ece-ebdb .
    # :Sentence_cc657637-9320 :has_semantic :Event_04e9a04c-9e05 .
    # :Event_04e9a04c-9e05 :text "lies" .
    # :Event_04e9a04c-9e05 a :DeceptionAndDishonesty ; :confidence-DeceptionAndDishonesty 100 .
    # :Event_04e9a04c-9e05 :has_active_entity :Sue .


def test_aux_pobj():
    parse_results = parse_narrative(text_aux_pobj)
    graph_results = create_graph(parse_results.sentence_classes, parse_results.quotation_classes,
                                 parse_results.partial_quotes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':text "got rid of' in ttl_str
    assert ':RemovalAndRestriction' in ttl_str
    assert ':has_active_entity :John' in ttl_str
    assert ':WasteAndResidue ; :text "debris' in ttl_str
    assert ':has_topic :Noun' in ttl_str or ':has_context :Noun' in ttl_str
    # Output Turtle:
    # :Sentence_1bb569f1-eac0 a :Sentence ; :offset 1 .
    # :Sentence_1bb569f1-eac0 :text "John got rid of the debris." .
    # :Sentence_1bb569f1-eac0 :mentions :John .
    # :Sentence_1bb569f1-eac0 :grade_level 3 .
    # :Sentence_1bb569f1-eac0 :summary "John removed the debris." .
    # :Sentence_1bb569f1-eac0 :has_semantic :Event_1d2f24d0-f211 .
    # :Event_1d2f24d0-f211 :text "got rid of" .
    # :Event_1d2f24d0-f211 a :RemovalAndRestriction ; :confidence-RemovalAndRestriction 100 .
    # :Event_1d2f24d0-f211 :has_active_entity :John .
    # :Noun_feae0a3a-2b80 a :WasteAndResidue ; :text "debris" ; :confidence 100 .
    # :Event_1d2f24d0-f211 :has_topic :Noun_feae0a3a-2b80 .


def test_idiom_amod():
    parse_results = parse_narrative(text_idiom_amod)
    graph_results = create_graph(parse_results.sentence_classes, parse_results.quotation_classes,
                                 parse_results.partial_quotes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':Avoidance' in ttl_str and ':text "turned a blind eye' in ttl_str
    assert ':has_active_entity :John' in ttl_str
    assert ':DeceptionAndDishonesty' in ttl_str and 'infidelity"' in ttl_str
    assert ':has_topic :Noun' in ttl_str               # infidelity
    # Output Turtle:
    # ::Sentence_be459a70-e76e a :Sentence ; :offset 1 .
    # :Sentence_be459a70-e76e :text "John turned a blind eye to Mary\'s infidelity." .
    # :Sentence_be459a70-e76e :mentions :John .
    # :Sentence_be459a70-e76e :mentions :Mary .
    # :Sentence_be459a70-e76e :grade_level 8 .
    # :Sentence_be459a70-e76e :rhetorical_device "allusion" .
    # :Sentence_be459a70-e76e :rhetorical_device_allusion "The phrase \'turned a blind eye\' is an allusion to the
    #     historical anecdote about Admiral Horatio Nelson, who allegedly used his blind eye to look through his
    #     telescope and claim he did not see a signal to withdraw during a battle. This allusion implies ignoring
    #     something intentionally." .
    # :Sentence_be459a70-e76e :summary "John ignored Mary\'s infidelity." .
    # :Sentence_be459a70-e76e :has_semantic :Event_55d40242-6506 .
    # :Event_55d40242-6506 :text "turned a blind eye to" .
    # :Event_55d40242-6506 a :Avoidance ; :confidence-Avoidance 95 .
    # :Event_55d40242-6506 :has_active_entity :John .
    # :Noun_269325e4-dc81 a :DeceptionAndDishonesty ; :text "Mary\'s infidelity" ; :confidence 95 .
    # :Event_55d40242-6506 :has_topic :Noun_269325e4-dc81 .


def test_advmod():
    parse_results = parse_narrative(text_advmod)
    graph_results = create_graph(parse_results.sentence_classes, parse_results.quotation_classes,
                                 parse_results.partial_quotes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':ReturnRecoveryAndRelease' in ttl_str or ':ProductionManufactureAndCreation' in ttl_str
    assert ':text "put back together' in ttl_str
    assert ':has_active_entity :Harry' in ttl_str
    assert ' :Resource ; :text "vase' in ttl_str
    assert ':has_topic :Noun' in ttl_str or ':has_context :Noun' in ttl_str
    # Output Turtle:
    # :Sentence_fca17a82-c47b a :Sentence ; :offset 1 .
    # :Sentence_fca17a82-c47b :text "Harry put the broken vase back together." .
    # :Harry :text "Harry" .
    # :Harry a :Person, :Correction .
    # :Harry rdfs:label "Harry" .
    # :Harry :gender "male" .
    # :Sentence_fca17a82-c47b :mentions :Harry .
    # :Sentence_fca17a82-c47b :grade_level 3 .
    # :Sentence_fca17a82-c47b :summary "Harry repaired the broken vase." .
    # :Sentence_fca17a82-c47b :has_semantic :Event_b78645f5-cd62 .
    # :Event_b78645f5-cd62 :text "put back together" .
    # :Event_b78645f5-cd62 a :ReturnRecoveryAndRelease ; :confidence-ReturnRecoveryAndRelease 90 .
    # :Event_b78645f5-cd62 :has_active_entity :Harry .
    # :Noun_f2b7db33-7a54 a :Resource ; :text "vase" ; :confidence 100 .
    # :Event_b78645f5-cd62 :has_topic :Noun_f2b7db33-7a54 .


def test_complex_verb():
    parse_results = parse_narrative(text_complex_verb)
    graph_results = create_graph(parse_results.sentence_classes, parse_results.quotation_classes,
                                 parse_results.partial_quotes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert (':End' in ttl_str or ':EconomyAndFinanceRelated' in ttl_str) or ':text "went out of business' in ttl_str
    assert (':LineOfBusiness' in ttl_str or ':Location' in ttl_str) or ':text "store' in ttl_str
    assert ':has_context :Noun' in ttl_str
    assert ':has_time [ a :Time ; :text "Tuesday' in ttl_str
    # Output Turtle:
    # :Sentence_bac165b6-9159 a :Sentence ; :offset 1 .
    # :Sentence_bac165b6-9159 :text "The store went out of business on Tuesday." .
    # :Sentence_bac165b6-9159 :grade_level 5 .
    # :Sentence_bac165b6-9159 :summary "The store closed on Tuesday." .
    # :Sentence_bac165b6-9159 :has_semantic :Event_a35a9458-94f1 .
    # :Event_a35a9458-94f1 :text "went out of business" .
    # :Event_a35a9458-94f1 a :EconomyAndFinanceRelated ; :confidence-EconomyAndFinanceRelated 95 .
    # :Noun_dc2a9a9f-c8bf a :LineOfBusiness ; :text "store" ; :confidence 90 .
    # :Event_a35a9458-94f1 :has_context :Noun_dc2a9a9f-c8bf .
    # :Event_a35a9458-94f1 :has_time [ a :Time ; :text "Tuesday" ] .


def test_neg_acomp_xcomp():
    parse_results = parse_narrative(text_neg_acomp_xcomp)
    graph_results = create_graph(parse_results.sentence_classes, parse_results.quotation_classes,
                                 parse_results.partial_quotes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert (':EmotionalResponse' in ttl_str or ':Avoidance' in ttl_str) and ':text "is not able to stomach' in ttl_str
    assert ':has_active_entity :Jane' in ttl_str
    assert ':DeceptionAndDishonesty ; :text "lies' in ttl_str
    assert ':has_topic :Noun' in ttl_str
    # Output Turtle:
    # :Sentence_7210bef0-1651 a :Sentence ; :offset 1 .
    # :Sentence_7210bef0-1651 :text "Jane is not able to stomach lies." .
    # :Sentence_7210bef0-1651 :mentions :Jane .
    # :Sentence_7210bef0-1651 :grade_level 6 .
    # :Sentence_7210bef0-1651 :rhetorical_device "loaded language" .
    # :Sentence_7210bef0-1651 :rhetorical_device_loaded_language "The phrase \'not able to stomach lies\' uses loaded
    #     language. The word \'stomach\' in this context has strong connotations, suggesting a visceral, emotional
    #     reaction to lies, which invokes judgment and emotion." .
    # :Sentence_7210bef0-1651 :summary "Jane cannot tolerate dishonesty." .
    # :Sentence_7210bef0-1651 :has_semantic :Event_9578c939-edb7 .
    # :Event_9578c939-edb7 :text "is not able to stomach" .
    # :Event_9578c939-edb7 a :Avoidance ; :confidence-Avoidance 95 .
    # :Event_9578c939-edb7 :has_active_entity :Jane .
    # :Noun_36f43ba2-3280 a :DeceptionAndDishonesty ; :text "lies" ; :confidence 100 .
    # :Event_9578c939-edb7 :has_topic :Noun_36f43ba2-3280 .


def test_non_person_subject():
    parse_results = parse_narrative(text_non_person_subject)
    graph_results = create_graph(parse_results.sentence_classes, parse_results.quotation_classes,
                                 parse_results.partial_quotes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':Loss' in ttl_str and ':text "were dashed' in ttl_str
    assert ':EmotionalResponse' in ttl_str and 'hopes"' in ttl_str
    assert ':has_context :Noun' in ttl_str
    # Output Turtle:
    # :Sentence_5a10adaf-16aa a :Sentence ; :offset 1 .
    # :Sentence_5a10adaf-16aa :text "John\'s hopes were dashed." .
    # :Sentence_5a10adaf-16aa :mentions :John .
    # :Sentence_5a10adaf-16aa :grade_level 5 .
    # :Sentence_5a10adaf-16aa :summary "John\'s hopes were not realized." .
    # :Sentence_5a10adaf-16aa :has_semantic :Event_d7490511-be86 .
    # :Event_d7490511-be86 :text "were dashed" .
    # :Event_d7490511-be86 a :Loss ; :confidence-Loss 95 .
    # :Noun_278caf70-996a a :EmotionalResponse ; :text "John\'s hopes" ; :confidence 90 .
    # :Event_d7490511-be86 :has_context :Noun_278caf70-996a .


def test_first_person():
    parse_results = parse_narrative(text_first_person)
    graph_results = create_graph(parse_results.sentence_classes, parse_results.quotation_classes,
                                 parse_results.partial_quotes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':text "was not ready' in ttl_str
    assert ':ReadinessAndAbility' in ttl_str and ':negated true' in ttl_str
    assert 'a :Person ; :text "I' in ttl_str
    assert ':has_active_entity :Noun' in ttl_str
    assert ':MovementTravelAndTransportation' in ttl_str and ':text "to leave' in ttl_str
    # Output Turtle:
    # :Sentence_4e75ee76-8da9 a :Sentence ; :offset 1 .
    # :Sentence_4e75ee76-8da9 :text "I was not ready to leave." .
    # :Sentence_4e75ee76-8da9 :grade_level 4 .
    # :Sentence_4e75ee76-8da9 :summary "The speaker was not ready to leave." .
    # :Sentence_4e75ee76-8da9 :has_semantic :Event_7bb63287-1a47 .
    # :Event_7bb63287-1a47 :text "was not ready" .
    # :Event_7bb63287-1a47 a :ReadinessAndAbility ; :confidence-ReadinessAndAbility 90 .
    # :Event_7bb63287-1a47 :negated true .
    # :Noun_37c654ea-a6ad a :Person ; :text "I" ; :confidence 99 .
    # :Event_7bb63287-1a47 :has_active_entity :Noun_37c654ea-a6ad .
    # :Sentence_4e75ee76-8da9 :has_semantic :Event_e0a79b05-bc8d .
    # :Event_e0a79b05-bc8d :text "to leave" .
    # :Event_e0a79b05-bc8d a :MovementTravelAndTransportation ; :confidence-MovementTravelAndTransportation 95 .
    # :Event_e0a79b05-bc8d :has_active_entity :Noun_37c654ea-a6ad .


def test_pobj_semantics():
    parse_results = parse_narrative(text_pobj_semantics)
    graph_results = create_graph(parse_results.sentence_classes, parse_results.quotation_classes,
                                 parse_results.partial_quotes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':Avoidance' in ttl_str     # escape
    assert 'a :Person ; :text "robber' in ttl_str
    assert ':has_active_entity :Noun' in ttl_str
    assert ':has_topic :Event' in ttl_str
    assert ':AidAndAssistance' in ttl_str and ':text "with the aid' in ttl_str
    assert 'a :GovernmentalEntity ; :text "local police' in ttl_str
    assert ':has_instrument :Noun' in ttl_str
    # Output Turtle:
    # :Sentence_4b621f12-26d3 a :Sentence ; :offset 1 .
    # :Sentence_4b621f12-26d3 :text "The robber escaped with the aid of the local police." .
    # :Sentence_4b621f12-26d3 :grade_level 8 .
    # :Sentence_4b621f12-26d3 :summary "Robber escaped with police aid." .
    # :Sentence_4b621f12-26d3 :has_semantic :Event_effd59d4-d759 .
    # :Event_effd59d4-d759 :text "escaped" .
    # :Event_effd59d4-d759 a :Avoidance ; :confidence-Avoidance 95 .
    # :Noun_ebe7d9f2-ba7e a :Person ; :text "robber" ; :confidence 100 .
    # :Event_effd59d4-d759 :has_active_entity :Noun_ebe7d9f2-ba7e .
    # :Event_effd59d4-d759 :has_topic :Event_6225e2db-fafc .
    # :Sentence_4b621f12-26d3 :has_semantic :Event_6225e2db-fafc .
    # :Event_6225e2db-fafc :text "with the aid of" .
    # :Event_6225e2db-fafc a :AidAndAssistance ; :confidence-AidAndAssistance 90 .
    # :Noun_a3cacaab-c60c a :GovernmentalEntity ; :text "local police" ; :confidence 100 .
    # :Event_6225e2db-fafc :has_instrument :Noun_a3cacaab-c60c .


def test_multiple_subjects():
    parse_results = parse_narrative(text_multiple_subjects)
    graph_results = create_graph(parse_results.sentence_classes, parse_results.quotation_classes,
                                 parse_results.partial_quotes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':DisagreementAndDispute' in ttl_str
    assert ':text "had a serious difference' in ttl_str
    assert ':has_active_entity :John' in ttl_str
    assert ':has_active_entity :Jane' in ttl_str
    # Output Turtle:
    # :Sentence_0810d0b3-8439 a :Sentence ; :offset 1 .
    # :Sentence_0810d0b3-8439 :text "Jane and John had a serious difference of opinion." .
    # :Sentence_0810d0b3-8439 :mentions :Jane .
    # :Sentence_0810d0b3-8439 :mentions :John .
    # :Sentence_0810d0b3-8439 :grade_level 6 .
    # :Sentence_0810d0b3-8439 :summary "Jane and John disagreed seriously." .
    # :Sentence_0810d0b3-8439 :has_semantic :Event_2eecb11d-b946 .
    # :Event_2eecb11d-b946 :text "had a serious difference of opinion" .
    # :Event_2eecb11d-b946 a :DisagreementAndDispute ; :confidence-DisagreementAndDispute 95 .
    # :Event_2eecb11d-b946 :has_active_entity :Jane .
    # :Event_2eecb11d-b946 :has_active_entity :John .


def test_multiple_xcomp():
    parse_results = parse_narrative(text_multiple_xcomp)
    graph_results = create_graph(parse_results.sentence_classes, parse_results.quotation_classes,
                                 parse_results.partial_quotes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert (':ArtAndEntertainmentEvent' in ttl_str or ':BodilyAct' in ttl_str) and \
           ':text "to ski' in ttl_str and ':text "to swim' in ttl_str
    assert ':EmotionalResponse' in ttl_str and ':text "liked' in ttl_str
    assert ':has_active_entity :John' in ttl_str
    # Output Turtle:
    # :Sentence_93b8056c-a76e a :Sentence ; :offset 1 .
    # :Sentence_93b8056c-a76e :text "John liked to ski and to swim." .
    # :Sentence_93b8056c-a76e :mentions :John .
    # :Sentence_93b8056c-a76e :grade_level 3 .
    # :Sentence_93b8056c-a76e :summary "John enjoys skiing and swimming." .
    # :Sentence_93b8056c-a76e :has_semantic :Event_2dad2608-5aff .
    # :Event_2dad2608-5aff :text "liked" .
    # :Event_2dad2608-5aff a :EmotionalResponse ; :confidence-EmotionalResponse 95 .
    # :Event_2dad2608-5aff :has_active_entity :John .
    # :Event_2dad2608-5aff :has_topic :Event_bfc4329f-85d3 .
    # :Sentence_93b8056c-a76e :has_semantic :Event_bfc4329f-85d3 .
    # :Event_bfc4329f-85d3 :text "to ski" .
    # :Event_bfc4329f-85d3 a :ArtAndEntertainmentEvent ; :confidence-ArtAndEntertainmentEvent 90 .
    # :Sentence_93b8056c-a76e :has_semantic :Event_697312c6-ec1f .
    # :Event_697312c6-ec1f :text "to swim" .
    # :Event_697312c6-ec1f a :ArtAndEntertainmentEvent ; :confidence-ArtAndEntertainmentEvent 90 .


def test_location_hierarchy():
    parse_results = parse_narrative(text_location_hierarchy)
    graph_results = create_graph(parse_results.sentence_classes, parse_results.quotation_classes,
                                 parse_results.partial_quotes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':mentions geo:2658434' in ttl_str        # Switzerland
    assert 'imagery' in ttl_str or 'exceptionalism' in ttl_str
    assert ':EnvironmentAndCondition' in ttl_str
    assert ':Location' in ttl_str and  'mountains"' in ttl_str
    assert ':has_context :Noun' in ttl_str
    # Output Turtle:
    # :Sentence_6bdab26a-3b7b a :Sentence ; :offset 1 .
    # :Sentence_6bdab26a-3b7b :text "Switzerland\'s mountains are magnificent." .
    # :Sentence_6bdab26a-3b7b :mentions geo:2658434 .
    # :Sentence_6bdab26a-3b7b :grade_level 5 .
    # :Sentence_6bdab26a-3b7b :rhetorical_device "exceptionalism" .
    # :Sentence_6bdab26a-3b7b :rhetorical_device_exceptionalism "The sentence uses language that indicates
    #     Switzerland\'s mountains are \'magnificent\', suggesting they are unique or exemplary." .
    # :Sentence_6bdab26a-3b7b :rhetorical_device "imagery" .
    # :Sentence_6bdab26a-3b7b :rhetorical_device_imagery "The word \'magnificent\' is a descriptive term that
    #     paints a vivid picture and emotionally engages the reader by highlighting the beauty of the mountains." .
    # :Sentence_6bdab26a-3b7b :summary "Switzerland\'s mountains are magnificent." .
    # :Sentence_6bdab26a-3b7b :has_semantic :Event_cb43954b-3b79 .
    # :Event_cb43954b-3b79 :text "are" .
    # :Event_cb43954b-3b79 a :EnvironmentAndCondition ; :confidence-EnvironmentAndCondition 100 .
    # :Noun_14af17b7-298d a :Location ; :text "Switzerland\'s mountains" ; :confidence 95 .
    # :Event_cb43954b-3b79 :has_context :Noun_14af17b7-298d .


def test_weather():
    parse_results = parse_narrative(text_weather)
    graph_results = create_graph(parse_results.sentence_classes, parse_results.quotation_classes,
                                 parse_results.partial_quotes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':mentions :Hurricane_Otis' in ttl_str and ':mentions :Acapulco' in ttl_str
    assert ':EnvironmentalOrEcologicalEvent' in ttl_str
    assert ':has_described_entity :Hurricane_Otis' in ttl_str or ':has_topic :Hurricane_Otis' in ttl_str or \
           ':has_context :Hurricane_Otis' in ttl_str
    assert ':has_location :Acapulco' in ttl_str
    # Output Turtle:
    # :Sentence_cc1b4df6-2961 a :Sentence ; :offset 1 .
    # :Sentence_cc1b4df6-2961 :text "Hurricane Otis severely damaged Acapulco." .
    # :Hurricane_Otis :text "Hurricane Otis" .      # Example of data pulled from Wikipedia/Wikidata
    # :Hurricane_Otis a :EnvironmentalOrEcologicalEvent .
    # :Hurricane_Otis rdfs:label "Otis", "Hurricane Otis" .
    # :Hurricane_Otis rdfs:comment "From Wikipedia (wikibase_item: Q123178445): \'Hurricane Otis was a compact but very
    #     powerful tropical cyclone which made a devastating landfall in October 2023 near Acapulco as a Category 5
    #     hurricane...\'" .
    # :Hurricane_Otis :external_link "https://en.wikipedia.org/wiki/Hurricane_Otis" .
    # :Hurricane_Otis :external_identifier "Q123178445" .
    # :Hurricane_Otis :has_beginning :PiT_2023-10-22T00:00:00Z .
    # :Acapulco :text "Acapulco" .
    # :Acapulco a :PopulatedPlace .
    # :Acapulco rdfs:label "Acapulco de Juárez", "Acapulco", "Acapulco de Juarez" .
    # :Acapulco rdfs:comment "From Wikipedia (wikibase_item: Q81398): \'Acapulco de Ju?rez, commonly called Acapulco,
    #     is a city and major seaport in the state of Guerrero on the Pacific Coast of Mexico, 380 kilometres (240 mi)
    #     south of Mexico City...\'" .
    # :Acapulco :external_link "https://en.wikipedia.org/wiki/Acapulco" .
    # :Acapulco :external_identifier "Q81398" .
    # :Acapulco :country_name "Mexico" .
    # geo:3996063 :has_component :Acapulco .
    # :Acapulco a :Location, :Correction .
    # :Acapulco rdfs:label "Acapulco de Juárez", "Acapulco", "Acapulco de Juarez", "Acapulco de julio", "Acapulco, Guerrero" .
    # :Sentence_cc1b4df6-2961 :mentions :Hurricane_Otis .
    # :Sentence_cc1b4df6-2961 :mentions :Acapulco .
    # :Sentence_cc1b4df6-2961 :grade_level 6 .
    # :Sentence_cc1b4df6-2961 :summary "Hurricane Otis damaged Acapulco severely." .
    # :Sentence_cc1b4df6-2961 :has_semantic :Event_280da0bb-77e6 .
    # :Event_280da0bb-77e6 :text "damaged" .
    # :Event_280da0bb-77e6 a :EnvironmentalOrEcologicalEvent ; :confidence-EnvironmentalOrEcologicalEvent 95 .
    # :Event_280da0bb-77e6 :has_context :Hurricane_Otis .
    # :Event_280da0bb-77e6 :has_location :Acapulco .


def test_coref():
    parse_results = parse_narrative(text_coref)
    graph_results = create_graph(parse_results.sentence_classes, parse_results.quotation_classes,
                                 parse_results.partial_quotes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':SensoryPerception' in ttl_str and ':text "saw' in ttl_str
    assert ':has_active_entity :Anna' in ttl_str
    assert (':Separation' in ttl_str or ':AgricultureApicultureAndAquacultureEvent' in ttl_str) \
           and ':text "cut' in ttl_str
    assert 'a :Plant ; :text "roses' in ttl_str
    assert ':has_active_entity :Heidi' in ttl_str
    assert ':has_topic :Noun' in ttl_str             # Heidi cutting roses
    # TODO: "Not recognizing" is cognition but should it be negated?
    assert (':Cognition' in ttl_str or ':Avoidance' in ttl_str) and ':text "did not recognize' in ttl_str
    assert ':has_affected_entity :Heidi' in ttl_str or ':has_topic :Heidi' in ttl_str
    # Output Turtle:
    # :Sentence_be409247-c4e6 a :Sentence ; :offset 1 .
    # :Sentence_be409247-c4e6 :text "Anna saw Heidi cut the roses, but she did not recognize that it was Heidi
    #     who cut the roses." .
    # :Sentence_be409247-c4e6 :mentions :Anna .
    # :Sentence_be409247-c4e6 :mentions :Heidi .
    # :Sentence_be409247-c4e6 :mentions :Heidi .
    # :Sentence_be409247-c4e6 :grade_level 8 .
    # :Sentence_be409247-c4e6 :summary "Anna saw Heidi cut roses but did not recognize her." .
    # :Sentence_be409247-c4e6 :has_semantic :Event_302ef14c-ef05 .
    # :Event_302ef14c-ef05 :text "saw" .
    # :Event_302ef14c-ef05 a :SensoryPerception ; :confidence-SensoryPerception 90 .
    # :Event_302ef14c-ef05 :has_active_entity :Anna .
    # :Event_302ef14c-ef05 :has_active_entity :Heidi .
    # :Noun_0cc5dc5a-b093 a :Plant ; :text "roses" ; :confidence 100 .
    # :Event_302ef14c-ef05 :has_topic :Noun_0cc5dc5a-b093 .
    # :Sentence_be409247-c4e6 :has_semantic :Event_58492ab1-bea8 .
    # :Event_58492ab1-bea8 :text "cut" .
    # :Event_58492ab1-bea8 a :Separation ; :confidence-Separation 95 .
    # :Event_58492ab1-bea8 :has_active_entity :Heidi .
    # :Event_58492ab1-bea8 :has_context :Noun_0cc5dc5a-b093 .
    # :Sentence_be409247-c4e6 :has_semantic :Event_80de11fb-1475 .
    # :Event_80de11fb-1475 :text "did not recognize" .
    # :Event_80de11fb-1475 a :Avoidance ; :confidence-Avoidance 85 .
    # :Event_80de11fb-1475 :has_active_entity :Anna .
    # :Event_80de11fb-1475 :has_topic :Heidi .


def test_quotation():
    parse_results = parse_narrative(text_quotation)
    graph_results = create_graph(parse_results.sentence_classes, parse_results.quotation_classes,
                                 parse_results.partial_quotes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':mentions :NVIDIA' in ttl_str
    assert ':CommunicationAndSpeechAct' in ttl_str and ':text "said' in ttl_str
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


def test_rule():
    parse_results = parse_narrative(text_rule)
    graph_results = create_graph(parse_results.sentence_classes, parse_results.quotation_classes,
                                 parse_results.partial_quotes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':AggressiveCriminalOrHostileAct' in ttl_str and ':RequirementAndDependence' in ttl_str
    assert  'a :Person ; :text "you' in ttl_str
    assert ':has_active_entity :Noun' in ttl_str
    # Output Turtle:
    # :Sentence_01a67e68-6268 a :Sentence ; :offset 1 .
    # :Sentence_01a67e68-6268 :text "You shall not kill." .
    # :Sentence_01a67e68-6268 :grade_level 3 .
    # :Sentence_01a67e68-6268 :summary "Prohibition against killing." .
    # :Sentence_01a67e68-6268 :has_semantic :Event_8565acf3-5ec3 .
    # :Event_8565acf3-5ec3 :text "shall not kill" .
    # TODO: "shall not" is the requirement; can we distinguish "shall", "not kill"?
    # :Event_8565acf3-5ec3 a :AggressiveCriminalOrHostileAct ; :confidence-AggressiveCriminalOrHostileAct 100 .
    # :Event_8565acf3-5ec3 a :RequirementAndDependence ; :confidence-RequirementAndDependence 95 .
    # :Noun_29ecfb6f-6cf3 a :Person ; :text "you" ; :confidence 100 .
    # :Event_8565acf3-5ec3 :has_active_entity :Noun_29ecfb6f-6cf3 .
