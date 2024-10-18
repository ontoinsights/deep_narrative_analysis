import pytest
from dna.create_narrative_turtle import create_graph
from dna.nlp import parse_narrative

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
    assert ':CommunicationAndSpeechAct' in ttl_str and ':text "claimed' in ttl_str
    assert ':has_active_entity :Liz_Cheney' in ttl_str
    assert ':has_topic [ a :Clause' in ttl_str or ':has_topic :Donald_Trump' in ttl_str
    assert ':DeceptionAndDishonesty' in ttl_str and ':text "lie' in ttl_str
    assert ':has_active_entity :Donald_Trump' in ttl_str                 # Trump is promoting the lie
    assert ':LawEnforcement' in ttl_str and (':text "recent FBI raid' in ttl_str or ':text "FBI raid' in ttl_str)
    assert ':has_context :Noun' in ttl_str
    # Output Turtle:
    # :Sentence_35bdd3bd-fedc a :Sentence ; :offset 1 .
    # :Sentence_35bdd3bd-fedc :text "Liz Cheney claimed that Trump is promoting an insidious lie about the recent
    #     FBI raid of his Mar-a-Lago residence." .
    # :Sentence_35bdd3bd-fedc :mentions :Liz_Cheney .
    # :Sentence_35bdd3bd-fedc :mentions :Trump .
    # :Sentence_35bdd3bd-fedc :mentions :FBI .
    # :Sentence_35bdd3bd-fedc :mentions :Mar_a_Lago .
    # :Sentence_35bdd3bd-fedc :grade_level 10 .
    # :Sentence_35bdd3bd-fedc :rhetorical_device "loaded language" .
    # :Sentence_35bdd3bd-fedc :rhetorical_device_loaded_language "The phrase \'insidious lie\' uses loaded language
    #     to invoke negative emotions and judgments." .
    # :Sentence_35bdd3bd-fedc :summary "Liz Cheney claimed that Trump is promoting an insidious lie about the recent
    #     FBI raid." .
    # :Sentence_35bdd3bd-fedc :has_semantic :Event_6cc9e635-3d3d .
    # :Event_6cc9e635-3d3d :text "claimed" .
    # :Event_6cc9e635-3d3d a :CommunicationAndSpeechAct ; :confidence-CommunicationAndSpeechAct 95 .
    # :Event_6cc9e635-3d3d :has_active_entity :Liz_Cheney .
    # :Event_6cc9e635-3d3d :has_topic :Donald_Trump .
    # :Noun_9b48af77-6423 a :DeceptionAndDishonesty ; :text "lie" ; :confidence 100 .
    # :Event_6cc9e635-3d3d :has_topic :Noun_9b48af77-6423 .
    # :Sentence_35bdd3bd-fedc :has_semantic :Event_8fb30641-595b .
    # :Event_8fb30641-595b :text "is promoting" .
    # :Event_8fb30641-595b a :DeceptionAndDishonesty ; :confidence-DeceptionAndDishonesty 90 .
    # :Event_8fb30641-595b :has_active_entity :Donald_Trump .
    # :Event_8fb30641-595b :text "lie" .
    # :Noun_393a8a7e-89af a :LawEnforcement ; :text "recent FBI raid" ; :confidence 85 .
    # :Event_8fb30641-595b :has_context :Noun_393a8a7e-89af .


def test_multiple_verbs():
    sentence_classes, quotation_classes = parse_narrative(text_multiple_verbs)
    graph_results = create_graph(sentence_classes, quotation_classes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':EnvironmentAndCondition' in ttl_str and ':text "is' in ttl_str
    assert ':LineOfBusiness ; :text "attorney' in ttl_str and ':has_aspect :Noun' in ttl_str
    assert ':has_context :Sue' in ttl_str
    assert ':text "lies' in ttl_str and ':DeceptionAndDishonesty' in ttl_str
    assert ':has_active_entity :Sue' in ttl_str
    # Output Turtle:
    # :Sentence_cc657637-9320 a :Sentence ; :offset 1 .
    # :Sentence_cc657637-9320 :text "Sue is an attorney but still lies." .
    # :Sentence_cc657637-9320 :mentions :Sue .
    # :Sentence_cc657637-9320 :grade_level 6 .
    # :Sentence_cc657637-9320 :summary "Sue is an attorney but still lies." .
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
    sentence_classes, quotation_classes = parse_narrative(text_aux_pobj)
    graph_results = create_graph(sentence_classes, quotation_classes, 5, repo)
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
    # :Sentence_1bb569f1-eac0 :summary "John got rid of the debris." .
    # :Sentence_1bb569f1-eac0 :has_semantic :Event_1d2f24d0-f211 .
    # :Event_1d2f24d0-f211 :text "got rid of" .
    # :Event_1d2f24d0-f211 a :RemovalAndRestriction ; :confidence-RemovalAndRestriction 100 .
    # :Event_1d2f24d0-f211 :has_active_entity :John .
    # :Noun_feae0a3a-2b80 a :WasteAndResidue ; :text "debris" ; :confidence 100 .
    # :Event_1d2f24d0-f211 :has_topic :Noun_feae0a3a-2b80 .


def test_idiom_amod():
    sentence_classes, quotation_classes = parse_narrative(text_idiom_amod)
    graph_results = create_graph(sentence_classes, quotation_classes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':Avoidance' in ttl_str and ':text "turned a blind eye' in ttl_str
    assert ':has_active_entity :John' in ttl_str
    assert ':DeceptionAndDishonesty' in ttl_str and ':text "infidelity' in ttl_str    # Mary's infidelity
    assert ':has_topic :Mary' in ttl_str and ':has_topic :Noun' in ttl_str
    # Output Turtle:
    # :Sentence_9a844dae-aa10 a :Sentence ; :offset 1 .
    # :Sentence_9a844dae-aa10 :text "John turned a blind eye to Mary\'s infidelity." .
    # :Sentence_9a844dae-aa10 :mentions :John .
    # :Sentence_9a844dae-aa10 :mentions :Mary .
    # :Sentence_9a844dae-aa10 :grade_level 8 .
    # :Sentence_9a844dae-aa10 :rhetorical_device "allusion" .
    # :Sentence_9a844dae-aa10 :rhetorical_device_allusion "The phrase \'turned a blind eye\' is an allusion to
    #     the historical anecdote of Admiral Horatio Nelson, who purportedly used his blind eye to look through his
    #     telescope and ignore signals to withdraw from battle, symbolizing willful ignorance." .
    # :Sentence_9a844dae-aa10 :summary "John turned a blind eye to Mary\'s infidelity." .
    # :Sentence_9a844dae-aa10 :has_semantic :Event_21fd2349-2ca1 .
    # :Event_21fd2349-2ca1 :text "turned a blind eye" .
    # :Event_21fd2349-2ca1 a :Avoidance ; :confidence-Avoidance 100 .
    # :Event_21fd2349-2ca1 :has_active_entity :John .
    # :Event_21fd2349-2ca1 :has_topic :Mary .
    # :Noun_56f507bc-a4c7 a :DeceptionAndDishonesty ; :text "infidelity" ; :confidence 100 .
    # :Event_21fd2349-2ca1 :has_topic :Noun_56f507bc-a4c7 .


def test_complex_verb():
    sentence_classes, quotation_classes = parse_narrative(text_complex_verb)
    graph_results = create_graph(sentence_classes, quotation_classes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert (':End' in ttl_str or ':EconomyAndFinanceRelated' in ttl_str) and ':text "went out of business' in ttl_str
    assert (':LineOfBusiness' in ttl_str or ':Location' in ttl_str) or ':text "store' in ttl_str
    assert ':has_context :Noun' in ttl_str
    assert ':has_time [ a :Time ; :text "Tuesday' in ttl_str
    # Output Turtle:
    # :Sentence_bac165b6-9159 a :Sentence ; :offset 1 .
    # :Sentence_bac165b6-9159 :text "The store went out of business on Tuesday." .
    # :Sentence_bac165b6-9159 :grade_level 5 .
    # :Sentence_bac165b6-9159 :summary "The store went out of business on Tuesday." .
    # :Sentence_bac165b6-9159 :has_semantic :Event_a35a9458-94f1 .
    # :Event_a35a9458-94f1 :text "went out of business" .
    # :Event_a35a9458-94f1 a :EconomyAndFinanceRelated ; :confidence-EconomyAndFinanceRelated 95 .
    # :Noun_dc2a9a9f-c8bf a :LineOfBusiness ; :text "store" ; :confidence 90 .
    # :Event_a35a9458-94f1 :has_context :Noun_dc2a9a9f-c8bf .
    # :Event_a35a9458-94f1 :has_time [ a :Time ; :text "Tuesday" ] .


def test_neg_acomp_xcomp():
    sentence_classes, quotation_classes = parse_narrative(text_neg_acomp_xcomp)
    graph_results = create_graph(sentence_classes, quotation_classes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':text "is not able to stomach' in ttl_str
    assert (':ReadinessAndAbility' in ttl_str and ':negated true' in ttl_str) or \
        (':Avoidance' in ttl_str and ':negated true' not in ttl_str)
    assert ':has_active_entity :Jane' in ttl_str
    assert ':DeceptionAndDishonesty ; :text "lies' in ttl_str
    assert ':has_topic :Noun' in ttl_str
    # Output Turtle:
    # :Sentence_b5c75a8a-5251 a :Sentence ; :offset 1 .
    # :Sentence_b5c75a8a-5251 :text "Jane is not able to stomach lies." .
    # :Sentence_b5c75a8a-5251 :mentions :Jane .
    # :Sentence_b5c75a8a-5251 :grade_level 5 .
    # :Sentence_b5c75a8a-5251 :rhetorical_device "loaded language" .
    # :Sentence_b5c75a8a-5251 :rhetorical_device_loaded_language "The phrase \'stomach lies\' uses loaded language
    #     with strong connotations against dishonesty." .
    # :Sentence_b5c75a8a-5251 :summary "Jane is not able to stomach lies." .
    # :Sentence_b5c75a8a-5251 :has_semantic :Event_a3ca4e03-9ccf .
    # :Event_a3ca4e03-9ccf :text "is not able to stomach" .
    # :Event_a3ca4e03-9ccf a :ReadinessAndAbility ; :confidence-Avoidance 90 .
    # :Event_a3ca4e03-9ccf :negated true .
    # :Event_a3ca4e03-9ccf :has_active_entity :Jane .
    # :Noun_52ece0a2-0228 a :DeceptionAndDishonesty ; :text "lies" ; :confidence 100 .
    # :Event_a3ca4e03-9ccf :has_topic :Noun_52ece0a2-0228


def test_non_person_subject():
    sentence_classes, quotation_classes = parse_narrative(text_non_person_subject)
    graph_results = create_graph(sentence_classes, quotation_classes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':Loss' in ttl_str and ':text "were dashed' in ttl_str
    assert (':EmotionalResponse' in ttl_str or ':Cognition' in ttl_str) and ':text "hopes' in ttl_str   # John's hopes
    assert ':has_affected_entity :Noun' in ttl_str
    # Output Turtle:
    # :Sentence_934924a9-856b a :Sentence ; :offset 1 .
    # :Sentence_934924a9-856b :text "John\'s hopes were dashed." .
    # :Sentence_934924a9-856b :mentions :John .
    # :Sentence_934924a9-856b :grade_level 5 .
    # :Sentence_934924a9-856b :summary "John\'s hopes were dashed." .
    # :Sentence_934924a9-856b :has_semantic :Event_873c5614-9aeb .
    # :Event_873c5614-9aeb :text "were dashed" .
    # :Event_873c5614-9aeb a :Loss ; :confidence-Loss 100 .
    # :Noun_67c7028c-c268 a :EmotionalResponse, :Collection ; :text "hopes" ; :confidence 100 .
    # :Event_873c5614-9aeb :has_affected_entity :Noun_67c7028c-c268 .


def test_first_person():
    sentence_classes, quotation_classes = parse_narrative(text_first_person)
    graph_results = create_graph(sentence_classes, quotation_classes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':text "was not ready' in ttl_str
    assert ':ReadinessAndAbility' in ttl_str and ':negated true' in ttl_str
    assert 'a :Person ; :text "I' in ttl_str
    assert ':has_active_entity :Noun' in ttl_str
    assert ':MovementTravelAndTransportation' in ttl_str and (':text "leave' in ttl_str or ':text "to leave' in ttl_str)
    # Output Turtle:
    # :Sentence_564e8d0d-f7d9 a :Sentence ; :offset 1 .
    # :Sentence_564e8d0d-f7d9 :text "I was not ready to leave." .
    # :Sentence_564e8d0d-f7d9 :grade_level 3 .
    # :Sentence_564e8d0d-f7d9 :summary "I was not ready to leave." .
    # :Sentence_564e8d0d-f7d9 :has_semantic :Event_fa5842b7-532e .
    # :Event_fa5842b7-532e :text "was not ready to leave" .
    # :Event_fa5842b7-532e a :ReadinessAndAbility ; :confidence-ReadinessAndAbility 90 .
    # :Event_fa5842b7-532e :negated true .
    # :Noun_d80147ec-82a0 a :Person ; :text "I" ; :confidence 99 .
    # :Event_fa5842b7-532e :has_active_entity :Noun_d80147ec-82a0 .
    # :Sentence_564e8d0d-f7d9 :has_semantic :Event_f46d80c6-7029 .
    # :Event_f46d80c6-7029 :text "to leave" .
    # :Event_f46d80c6-7029 a :MovementTravelAndTransportation ; :confidence-MovementTravelAndTransportation 95 .
    # :Event_f46d80c6-7029 :has_active_entity :Noun_d80147ec-82a0 .


def test_pobj_semantics():
    sentence_classes, quotation_classes = parse_narrative(text_pobj_semantics)
    graph_results = create_graph(sentence_classes, quotation_classes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':Avoidance' in ttl_str     # escape
    assert 'a :Person ; :text "robber' in ttl_str
    assert ':has_active_entity :Noun' in ttl_str
    assert ':has_topic :Event' in ttl_str
    assert ':AidAndAssistance' in ttl_str and ':text "aid' in ttl_str
    assert 'a :GovernmentalEntity ; :text "police' in ttl_str
    assert ':has_instrument :Noun' in ttl_str or ':has_source :Noun' in ttl_str
    # Output Turtle:
    # :Sentence_2b6af84d-cda1 a :Sentence ; :offset 1 .
    # :Sentence_2b6af84d-cda1 :text "The robber escaped with the aid of the local police." .
    # :Sentence_2b6af84d-cda1 :grade_level 8 .
    # :Sentence_2b6af84d-cda1 :summary "The robber escaped with the aid of the local police." .
    # :Sentence_2b6af84d-cda1 :has_semantic :Event_87d2d7fe-1660 .
    # :Event_87d2d7fe-1660 :text "escaped" .
    # :Event_87d2d7fe-1660 a :Avoidance ; :confidence-Avoidance 95 .
    # :Noun_5fd60e71-062f a :Person ; :text "robber" ; :confidence 100 .
    # :Event_87d2d7fe-1660 :has_active_entity :Noun_5fd60e71-062f .
    # :Event_87d2d7fe-1660 :has_topic :Event_67333bd1-09ff .
    # :Sentence_2b6af84d-cda1 :has_semantic :Event_67333bd1-09ff .
    # :Event_67333bd1-09ff :text "aid" .
    # :Event_67333bd1-09ff a :AidAndAssistance ; :confidence-AidAndAssistance 100 .
    # :Noun_226c5a1e-876a a :GovernmentalEntity ; :text "police" ; :confidence 100 .
    # :Event_67333bd1-09ff :has_instrument :Noun_226c5a1e-876a .


def test_multiple_subjects():
    sentence_classes, quotation_classes = parse_narrative(text_multiple_subjects)
    graph_results = create_graph(sentence_classes, quotation_classes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':DisagreementAndDispute' in ttl_str and ':text "difference' in ttl_str
    assert ':has_affected_entity :John' in ttl_str
    assert ':has_affected_entity :Jane' in ttl_str
    assert ':Cognition ; :text "opinion' in ttl_str and ':has_topic :Noun' in ttl_str
    # Output Turtle:
    # :Sentence_ed5fb665-6c99 a :Sentence ; :offset 1 .
    # :Sentence_ed5fb665-6c99 :text "Jane and John had a serious difference of opinion." .
    # :Sentence_ed5fb665-6c99 :mentions :Jane .
    # :Sentence_ed5fb665-6c99 :mentions :John .
    # :Sentence_ed5fb665-6c99 :grade_level 5 .
    # :Sentence_ed5fb665-6c99 :summary "Jane and John had a serious difference of opinion." .
    # :Sentence_ed5fb665-6c99 :has_semantic :Event_9c20c28f-43ea .
    # :Event_9c20c28f-43ea :text "had" .
    # :Event_9c20c28f-43ea a :DisagreementAndDispute ; :confidence-DisagreementAndDispute 100 .
    # :Event_9c20c28f-43ea :has_affected_entity :Jane .
    # :Event_9c20c28f-43ea :has_affected_entity :John .
    # :Event_9c20c28f-43ea :text "difference" .
    # :Noun_b816e128-8903 a :Cognition ; :text "opinion" ; :confidence 100 .
    # :Event_9c20c28f-43ea :has_topic :Noun_b816e128-8903 .


def test_multiple_xcomp():
    sentence_classes, quotation_classes = parse_narrative(text_multiple_xcomp)
    graph_results = create_graph(sentence_classes, quotation_classes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert (':ArtAndEntertainmentEvent' in ttl_str or ':BodilyAct' in ttl_str) and \
           ':text "to ski' in ttl_str and ':text "to swim' in ttl_str
    assert ':EmotionalResponse' in ttl_str and ':text "liked' in ttl_str
    assert ':has_active_entity :John' in ttl_str
    # Output Turtle:
    # :Sentence_56d338d7-47dd a :Sentence ; :offset 1 .
    # :Sentence_56d338d7-47dd :text "John liked to ski and to swim." .
    # :Sentence_56d338d7-47dd :mentions :John .
    # :Sentence_56d338d7-47dd :grade_level 3 .
    # :Sentence_56d338d7-47dd :summary "John liked to ski and to swim." .
    # :Sentence_56d338d7-47dd :has_semantic :Event_f3dcf42c-3190 .
    # :Event_f3dcf42c-3190 :text "liked" .
    # :Event_f3dcf42c-3190 a :EmotionalResponse ; :confidence-EmotionalResponse 90 .
    # :Event_f3dcf42c-3190 :has_active_entity :John .
    # :Event_f3dcf42c-3190 :has_topic :Event_62d28444-ce84 .
    # :Sentence_56d338d7-47dd :has_semantic :Event_62d28444-ce84 .
    # :Event_62d28444-ce84 :text "to ski" .
    # :Event_62d28444-ce84 a :ArtAndEntertainmentEvent ; :confidence-ArtAndEntertainmentEvent 85 .
    # :Event_62d28444-ce84 :has_active_entity :John .
    # :Sentence_56d338d7-47dd :has_semantic :Event_709834b7-d38a .
    # :Event_709834b7-d38a :text "to swim" .
    # :Event_709834b7-d38a a :ArtAndEntertainmentEvent ; :confidence-ArtAndEntertainmentEvent 85 .
    # :Event_709834b7-d38a :has_active_entity :John .
    # TODO: "to swim" event is also a topic of "liked"


def test_location_hierarchy():
    sentence_classes, quotation_classes = parse_narrative(text_location_hierarchy)
    graph_results = create_graph(sentence_classes, quotation_classes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':mentions geo:2658434' in ttl_str        # Switzerland
    assert 'imagery' in ttl_str or 'exceptionalism' in ttl_str
    assert ':EnvironmentAndCondition' in ttl_str
    assert ':Location' in ttl_str and ':text "mountains' in ttl_str
    assert ':has_context :Noun' in ttl_str
    # Output Turtle:
    # :Sentence_4022a793-6140 a :Sentence ; :offset 1 .
    # :Sentence_4022a793-6140 :text "Switzerland\'s mountains are magnificent." .
    # :Sentence_4022a793-6140 :mentions geo:2658434 .
    # :Sentence_4022a793-6140 :grade_level 5 .
    # :Sentence_4022a793-6140 :rhetorical_device "exceptionalism" .
    # :Sentence_4022a793-6140 :rhetorical_device_exceptionalism "The word \'magnificent\' indicates that the
    #     mountains are unique or exemplary." .
    # :Sentence_4022a793-6140 :rhetorical_device "imagery" .
    # :Sentence_4022a793-6140 :rhetorical_device_imagery "The word \'magnificent\' paints a vivid picture that
    #     emotionally engages the reader." .
    # :Sentence_4022a793-6140 :summary "Switzerland\'s mountains are magnificent." .
    # :Sentence_4022a793-6140 :has_semantic :Event_bd7f552d-dcf4 .
    # :Event_bd7f552d-dcf4 :text "are" .
    # :Event_bd7f552d-dcf4 a :EnvironmentAndCondition ; :confidence-EnvironmentAndCondition 100 .
    # :Noun_b9f54de6-0c99 a :Location ; :text "mountains" ; :confidence 95 .
    # :Event_bd7f552d-dcf4 :has_context :Noun_b9f54de6-0c99 .


def test_weather():
    sentence_classes, quotation_classes = parse_narrative(text_weather)
    graph_results = create_graph(sentence_classes, quotation_classes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':mentions :Hurricane_Otis' in ttl_str and ':mentions :Acapulco' in ttl_str
    assert ':EnvironmentalOrEcologicalEvent' in ttl_str
    assert ':has_active_entity :Hurricane_Otis' in ttl_str
    assert ':has_location :Acapulco' in ttl_str
    # Output Turtle:
    # :Sentence_2e706399-449a a :Sentence ; :offset 1 .
    # :Sentence_2e706399-449a :text "Hurricane Otis severely damaged Acapulco." .
    # :Sentence_2e706399-449a :mentions :Hurricane_Otis .
    # :Sentence_2e706399-449a :mentions :Acapulco .
    # :Sentence_2e706399-449a :grade_level 5 .
    # :Sentence_2e706399-449a :summary "Hurricane Otis severely damaged Acapulco." .
    # :Sentence_2e706399-449a :has_semantic :Event_d75b4af2-aa59 .
    # :Event_d75b4af2-aa59 :text "damaged" .
    # :Event_d75b4af2-aa59 a :EnvironmentalOrEcologicalEvent ; :confidence-EnvironmentalOrEcologicalEvent 100 .
    # :Event_d75b4af2-aa59 :has_active_entity :Hurricane_Otis .
    # :Event_d75b4af2-aa59 :has_location :Acapulco .


def test_coref():
    sentence_classes, quotation_classes = parse_narrative(text_coref)
    graph_results = create_graph(sentence_classes, quotation_classes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':SensoryPerception' in ttl_str and ':text "saw' in ttl_str
    assert ':has_active_entity :Anna' in ttl_str
    assert ':has_topic :Heidi' in ttl_str
    assert (':Separation' in ttl_str or ':AgricultureApicultureAndAquacultureEvent' in ttl_str) \
           and ':text "cut' in ttl_str
    assert 'a :Plant, :Collection ; :text "roses' in ttl_str
    assert ':has_active_entity :Heidi' in ttl_str
    assert ':has_affected_entity :Noun' in ttl_str
    assert (':Cognition' in ttl_str and ':negated true' in ttl_str) or \
        (':Avoidance' in ttl_str and ':negated true' not in ttl_str)
    # Output Turtle:
    # :Sentence_9184c762-3537 a :Sentence ; :offset 1 .
    # :Sentence_9184c762-3537 :text "Anna saw Heidi cut the roses, but she did not recognize that it was Heidi
    #     who cut the roses." .
    # :Sentence_9184c762-3537 :mentions :Anna .
    # :Sentence_9184c762-3537 :mentions :Heidi .
    # :Sentence_9184c762-3537 :mentions :Heidi .
    # :Sentence_9184c762-3537 :grade_level 8 .
    # :Sentence_9184c762-3537 :summary "Anna saw Heidi cut roses but didn\'t recognize her." .
    # :Sentence_9184c762-3537 :has_semantic :Event_b979a648-235a .
    # :Event_b979a648-235a :text "saw" .
    # :Event_b979a648-235a a :SensoryPerception ; :confidence-SensoryPerception 100 .
    # :Event_b979a648-235a :has_active_entity :Anna .
    # :Event_b979a648-235a :has_topic :Heidi .
    # :Noun_54d1b67d-4968 a :Plant, :Collection ; :text "roses" ; :confidence 100 .
    # :Event_b979a648-235a :has_topic :Noun_54d1b67d-4968 .
    # :Sentence_9184c762-3537 :has_semantic :Event_03923fe5-e722 .
    # :Event_03923fe5-e722 :text "cut" .
    # :Event_03923fe5-e722 a :Separation ; :confidence-Separation 100 .
    # :Event_03923fe5-e722 :has_active_entity :Heidi .
    # :Event_03923fe5-e722 :has_affected_entity :Noun_54d1b67d-4968 .
    # :Sentence_9184c762-3537 :has_semantic :Event_d99ed67c-964a .
    # :Event_d99ed67c-964a :text "did not recognize" .
    # :Event_d99ed67c-964a a :Avoidance ; :confidence-Avoidance 100 .
    # :Event_d99ed67c-964a :has_affected_entity :Anna .
    # :Event_d99ed67c-964a :has_topic :Heidi .


def test_quotation():
    sentence_classes, quotation_classes = parse_narrative(text_quotation)
    graph_results = create_graph(sentence_classes, quotation_classes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':mentions :NVIDIA' in ttl_str
    assert ':CommunicationAndSpeechAct' in ttl_str and ':text "said' in ttl_str
    assert ':has_active_entity :Jane' in ttl_str
    assert ':has_topic :Jane' in ttl_str
    assert ':EmotionalResponse' in ttl_str or ':Attempt' in ttl_str     # "want"
    assert ':has_affected_entity :NVIDIA' in ttl_str
    if ':Attempt' in ttl_str:
        assert ':has_context :Jane' in ttl_str
    assert ':MeetingAndEncounter ; :text "interview' in ttl_str
    # TODO: Missing meeting details
    assert 'a :Quote ; :text "I want to work for NVIDIA. My interview is tomorrow' in ttl_str
    assert ':attributed_to :Jane' in ttl_str
    # Output Turtle:
    # :Sentence_5d5f5d34-bea6 a :Sentence ; :offset 1 .
    # :Sentence_5d5f5d34-bea6 :text "Jane said, \'I want to work for NVIDIA." .
    # :Sentence_5d5f5d34-bea6 :mentions :Jane .
    # :Sentence_5d5f5d34-bea6 :mentions :NVIDIA .
    # :Sentence_5d5f5d34-bea6 :grade_level 5 .
    # :Sentence_5d5f5d34-bea6 :summary "Jane said, \'I want to work for NVIDIA." .
    # :Sentence_00a36550-fe73 a :Sentence ; :offset 2 .
    # :Sentence_00a36550-fe73 :text "My interview is tomorrow.\'" .
    # :Sentence_00a36550-fe73 :grade_level 3 .
    # :Sentence_00a36550-fe73 :summary "My interview is tomorrow.\'" .
    # :Sentence_5d5f5d34-bea6 :has_semantic :Event_455ee09e-98be .
    # :Event_455ee09e-98be :text "said" .
    # :Event_455ee09e-98be a :CommunicationAndSpeechAct ; :confidence-CommunicationAndSpeechAct 100 .
    # :Event_455ee09e-98be :has_active_entity :Jane .
    # :Event_455ee09e-98be :has_topic :Jane .
    # :Sentence_5d5f5d34-bea6 :has_semantic :Event_54925bd2-98d3 .
    # :Event_54925bd2-98d3 :text "want to work" .
    # :Event_54925bd2-98d3 a :Attempt ; :confidence-Attempt 100 .
    # :Event_54925bd2-98d3 :has_context :Jane .
    # :Event_54925bd2-98d3 :has_affected_entity :NVIDIA .
    # :Sentence_5d5f5d34-bea6 :has_semantic :Event_a5cc3e1c-0a99 .
    # :Event_a5cc3e1c-0a99 :text "is" .
    # :Event_a5cc3e1c-0a99 a :EnvironmentAndCondition ; :confidence-EnvironmentAndCondition 100 .
    # :Noun_3f65599f-d00c a :MeetingAndEncounter ; :text "interview" ; :confidence 100 .
    # :Event_a5cc3e1c-0a99 :has_context :Noun_3f65599f-d00c .
    # :Event_a5cc3e1c-0a99 :has_time [ a :Time ; :text "tomorrow" ] .
    # :Quotation_a1debc8e-3894 a :Quote ; :text "I want to work for NVIDIA. My interview is tomorrow." .
    # :Quotation_a1debc8e-3894 :attributed_to :Jane .
    # :Quotation_a1debc8e-3894 :grade_level 5 .
    # :Quotation_a1debc8e-3894 :summary "I want to work for NVIDIA. My interview is tomorrow." .


def test_rule():
    sentence_classes, quotation_classes = parse_narrative(text_rule)
    graph_results = create_graph(sentence_classes, quotation_classes, 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':AggressiveCriminalOrHostileAct' in ttl_str and ':negated true' in ttl_str
    assert ':RequirementAndDependence' in ttl_str
    assert  'a :Person ; :text "you' in ttl_str
    assert ':has_active_entity :Noun' in ttl_str
    # Output Turtle:
    # ::Sentence_0fb7d521-f0d3 a :Sentence ; :offset 1 .
    # :Sentence_0fb7d521-f0d3 :text "You shall not kill." .
    # :Sentence_0fb7d521-f0d3 :grade_level 5 .
    # :Sentence_0fb7d521-f0d3 :summary "You shall not kill." .
    # :Sentence_0fb7d521-f0d3 :has_semantic :Event_92d5c2b7-e38a .
    # :Event_92d5c2b7-e38a :text "shall not kill" .
    # :Event_92d5c2b7-e38a a :AggressiveCriminalOrHostileAct ; :confidence-AggressiveCriminalOrHostileAct 95 .
    # :Event_92d5c2b7-e38a :negated true .    # TODO: Better distinguish that negation is related to killing
    # :Event_92d5c2b7-e38a a :RequirementAndDependence ; :confidence-RequirementAndDependence 95 .
    # :Noun_965fe865-6331 a :Person ; :text "you" ; :confidence 100 .
    # :Event_92d5c2b7-e38a :has_active_entity :Noun_965fe865-6331 .


def test_causation():
    sentence_classes, quotation_classes = parse_narrative(text_causation)
    graph_results = create_graph(sentence_classes, quotation_classes, 5, repo)
    ttl_str = str(graph_results.turtle)
    print(ttl_str)
    assert ':HealthAndDiseaseRelated' in ttl_str and ':text "twisted' in ttl_str
    assert ':has_active_entity :Holly' in ttl_str
    assert ':ComponentPart ; :text "ankle' in ttl_str
    assert ':has_affected_entity :Noun' in ttl_str    # twisted ankle
    assert (':ArtAndEntertainmentEvent' in ttl_str or ':BodilyAct' in ttl_str) and ':text "was running' in ttl_str
    assert (':AggressiveCriminalOrHostileAct' in ttl_str or ':ImpactAndContact' in ttl_str) and \
        ':text "had pushed' in ttl_str
    assert ':has_active_entity :David' in ttl_str
    assert ':has_affected_entity :Holly' in ttl_str
    # Output Turtle:
    # :Sentence_b31fbee6-9d20 a :Sentence ; :offset 1 .
    # :Sentence_b31fbee6-9d20 :text "Yesterday Holly was running a marathon when she twisted her ankle." .
    # :Sentence_b31fbee6-9d20 :mentions :Holly .
    # :Sentence_b31fbee6-9d20 :grade_level 6 .
    # :Sentence_b31fbee6-9d20 :summary "Yesterday Holly was running a marathon when she twisted her ankle." .
    # :Sentence_71076128-157f a :Sentence ; :offset 2 .
    # :Sentence_71076128-157f :text "David had pushed her." .
    # :Sentence_71076128-157f :mentions :David .
    # :Sentence_71076128-157f :grade_level 3 .
    # :Sentence_71076128-157f :summary "David had pushed her." .
    # :Sentence_b31fbee6-9d20 :has_semantic :Event_0dc70a2c-86fe .
    # :Event_0dc70a2c-86fe :text "was running" .
    # :Event_0dc70a2c-86fe a :ArtAndEntertainmentEvent ; :confidence-ArtAndEntertainmentEvent 100 .
    # :Event_0dc70a2c-86fe :has_active_entity :Holly .
    # :Event_0dc70a2c-86fe :text "marathon" .
    # :Sentence_b31fbee6-9d20 :has_semantic :Event_32910745-8a07 .
    # :Event_32910745-8a07 :text "twisted" .
    # :Event_32910745-8a07 a :HealthAndDiseaseRelated ; :confidence-HealthAndDiseaseRelated 100 .
    # :Event_32910745-8a07 :has_active_entity :Holly .
    # :Noun_f168157d-1658 a :ComponentPart ; :text "ankle" ; :confidence 100 .
    # :Event_32910745-8a07 :has_affected_entity :Noun_f168157d-1658 .
    # :Sentence_71076128-157f :has_semantic :Event_b1043278-6006 .
    # :Event_b1043278-6006 :text "had pushed" .
    # :Event_b1043278-6006 a :ImpactAndContact ; :confidence-ImpactAndContact 100 .
    # :Event_b1043278-6006 :has_active_entity :David .
    # :Event_b1043278-6006 :has_affected_entity :Holly .
    # TODO: Causation across sentences
