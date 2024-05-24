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
        assert ':has_described_entity :Sue' in ttl_str
        assert 'a :LineOfBusiness ; :text "attorney' in ttl_str
    else:
        assert 'a :KnowledgeAndSkill ; :text "attorney' in ttl_str
        assert ':has_described_entity :Sue' in ttl_str
    assert 'a :DeceptionAndDishonesty ; :text "lies' in ttl_str
    assert ':has_active_entity :Sue' in ttl_str
    # Output Turtle:
    # :Sentence_18463183-7d1b a :Sentence ; :offset 1 .
    # :Sentence_18463183-7d1b :text "Sue is an attorney but still lies." .
    # :Sue :text "Sue" .
    # :Sue a :Person .
    # :Sue rdfs:label "Sue" .
    # :Sue :gender "female" .
    # :Sentence_18463183-7d1b :mentions :Sue .
    # :Sentence_18463183-7d1b :summary "Attorney Sue still engages in dishonesty." .
    # :Sentence_18463183-7d1b :sentiment "negative" .
    # :Sentence_18463183-7d1b :grade_level 5 .
    # :Sentence_18463183-7d1b :rhetorical_device {:evidence "The phrase \'but still lies\' directly attacks
    #     the character of Sue, implying dishonesty despite her professional status as an attorney."}  "ad hominem" .
    # :Sentence_18463183-7d1b :rhetorical_device {:evidence "The sentence places the contrasting ideas of being
    #     an attorney, typically associated with integrity, against the act of lying."}  "juxtaposition" .
    # :Sentence_18463183-7d1b :has_semantic :Event_aa7974e3-d7d6 .
    # :Event_aa7974e3-d7d6 a :EnvironmentAndCondition ; :text "is" .
    # :Event_aa7974e3-d7d6 :has_described_entity :Sue .
    # :Noun_61c08455-e3fe a :LineOfBusiness ; :text "attorney" ; rdfs:label "an attorney" .
    # :Event_aa7974e3-d7d6 :has_aspect :Noun_61c08455-e3fe .
    # :Sentence_18463183-7d1b :has_semantic :Event_334319a1-0165 .
    # :Event_334319a1-0165 a :DeceptionAndDishonesty ; :text "lies" .
    # :Event_334319a1-0165 :has_active_entity :Sue .


def test_aux_pobj():
    sentence_instances, quotation_instances, quoted_strings = parse_narrative(text_aux_pobj)
    success, index, graph_ttl = create_graph(sentence_instances, quotation_instances, 3, repo)
    ttl_str = str(graph_ttl)
    assert 'a :RemovalAndRestriction ; :text "got rid of' in ttl_str
    assert ':has_active_entity :John' in ttl_str
    assert ':has_topic :Noun' in ttl_str or ':has_affected_entity :Noun' in ttl_str
    # Output Turtle:
    # :Sentence_3ff0776d-57c8 a :Sentence ; :offset 1 .
    # :Sentence_3ff0776d-57c8 :text "John got rid of the debris." .
    # :John :text "John" .
    # :John a :Person .
    # :John rdfs:label "John" .
    # :John :gender "male" .
    # :Sentence_3ff0776d-57c8 :mentions :John .
    # :Sentence_3ff0776d-57c8 :summary "John eliminated the debris." .
    # :Sentence_3ff0776d-57c8 :sentiment "neutral" .
    # :Sentence_3ff0776d-57c8 :grade_level 3 .
    # :Sentence_3ff0776d-57c8 :has_semantic :Event_3360728c-bd1f .
    # :Event_3360728c-bd1f a :RemovalAndRestriction ; :text "got rid of" .
    # :Event_3360728c-bd1f :has_active_entity :John .
    # :Noun_8e77f08d-de2c a :WasteAndResidue ; :text "debris" ; rdfs:label "rid of the debris" .
    # :Event_3360728c-bd1f :has_topic :Noun_8e77f08d-de2c .
    # :Sentence_3ff0776d-57c8 :has_semantic :Event_f6adaa5d-8849 .
    # :Event_f6adaa5d-8849 a :RemovalAndRestriction ; :text "got rid of" .
    # :Event_f6adaa5d-8849 :has_active_entity :John .
    # :Event_f6adaa5d-8849 :has_topic :Noun_8e77f08d-de2c .


def test_idiom_amod():
    sentence_instances, quotation_instances, quoted_strings = parse_narrative(text_idiom_amod)
    success, index, graph_ttl = create_graph(sentence_instances, quotation_instances, 3, repo)
    ttl_str = str(graph_ttl)
    assert 'metaphor' in ttl_str
    assert ':Avoidance' in ttl_str and ':text "turned a blind eye' in ttl_str
    assert ':has_active_entity :John' in ttl_str
    assert ':DeceptionAndDishonesty' in ttl_str or ':has_topic [ :text "to Mary' in ttl_str    # infidelity
    # Output Turtle:
    # :Sentence_a1fc3fbe-508a a :Sentence ; :offset 1 .
    # :Sentence_a1fc3fbe-508a :text "John turned a blind eye to Mary\'s infidelity." .
    # :John :text "John" .
    # :John a :Person .
    # :John rdfs:label "John" .
    # :John :gender "male" .
    # :Mary :text "Mary" .
    # :Mary a :Person .
    # :Mary rdfs:label "Mary" .
    # :Mary :gender "female" .
    # :Sentence_a1fc3fbe-508a :mentions :John .
    # :Sentence_a1fc3fbe-508a :mentions :Mary .
    # :Sentence_a1fc3fbe-508a :summary "John ignored Mary\'s unfaithfulness." .
    # :Sentence_a1fc3fbe-508a :sentiment "negative" .
    # :Sentence_a1fc3fbe-508a :grade_level 5 .
    # :Sentence_a1fc3fbe-508a :rhetorical_device {:evidence "The phrase \'turned a blind eye\' is a metaphor for
    #     intentionally ignoring something."}  "metaphor" .
    # :Sentence_a1fc3fbe-508a :has_semantic :Event_7086ef57-bf96 .
    # TODO: DeceptionAndDishonesty should be separate event
    # :Event_7086ef57-bf96 a :Avoidance, :DeceptionAndDishonesty ; :text "turned a blind eye" .
    # :Event_7086ef57-bf96 :has_active_entity :John .
    # :Event_7086ef57-bf96 :has_topic [ :text "to Mary\'s infidelity" ; a :Clause ] .


def test_advmod():
    sentence_instances, quotation_instances, quoted_strings = parse_narrative(text_advmod)
    success, index, graph_ttl = create_graph(sentence_instances, quotation_instances, 3, repo)
    ttl_str = str(graph_ttl)
    assert 'a :ReturnRecoveryAndRelease ; :text "put back together' in ttl_str or \
           ' a :ProductionManufactureAndCreation ; :text "put back together' in ttl_str
    assert ':has_active_entity :Harry' in ttl_str
    assert ' a :Resource ; :text "vase' in ttl_str
    assert ':has_topic :Noun' in ttl_str
    # Output Turtle:
    # :Sentence_72e13208-88db a :Sentence ; :offset 1 .
    # :Sentence_72e13208-88db :text "Harry put the broken vase back together." .
    # :Harry :text "Harry" .
    # :Harry a :Person .
    # :Harry rdfs:label "Harry" .
    # :Harry :gender "male" .
    # :Sentence_72e13208-88db :mentions :Harry .
    # :Sentence_72e13208-88db :summary "Harry repaired the broken vase." .
    # :Sentence_72e13208-88db :sentiment "positive" .
    # :Sentence_72e13208-88db :grade_level 3 .
    # :Sentence_72e13208-88db :has_semantic :Event_0146fcd0-b4ff .
    # :Event_0146fcd0-b4ff a :ReturnRecoveryAndRelease ; :text "put back together" .
    # :Event_0146fcd0-b4ff :has_active_entity :Harry .
    # :Noun_d36d13fc-1c34 a :Resource ; :text "vase" ; rdfs:label "the broken vase" .
    # :Event_0146fcd0-b4ff :has_topic :Noun_d36d13fc-1c34 .


def test_complex_verb():
    sentence_instances, quotation_instances, quoted_strings = parse_narrative(text_complex_verb)
    success, index, graph_ttl = create_graph(sentence_instances, quotation_instances, 3, repo)
    ttl_str = str(graph_ttl)
    assert 'a :End ; :text "went out of business' in ttl_str
    assert ':has_active_entity :Noun' in ttl_str
    assert ' :has_time [ :text "on Tuesday' in ttl_str
    assert 'a :LineOfBusiness ; :text "store' in ttl_str
    # Output Turtle:
    # :Sentence_b5a73ea9-6b27 a :Sentence ; :offset 1 .
    # :Sentence_b5a73ea9-6b27 :text "The store went out of business on Tuesday." .
    # :Sentence_b5a73ea9-6b27 :summary "Store ceased operations on Tuesday." .
    # :Sentence_b5a73ea9-6b27 :sentiment "negative" .
    # :Sentence_b5a73ea9-6b27 :grade_level 5 .
    # :Sentence_b5a73ea9-6b27 :has_semantic :Event_378242d7-9f44 .
    # :Event_378242d7-9f44 a :End ; :text "went out of business" .
    # :Noun_817cee91-b787 a :LineOfBusiness ; :text "store" ; rdfs:label "The store" .
    # :Event_378242d7-9f44 :has_active_entity :Noun_817cee91-b787 .
    # :Event_378242d7-9f44 :has_time [ :text "on Tuesday" ; a :Time ] .


def test_neg_acomp_xcomp():
    sentence_instances, quotation_instances, quoted_strings = parse_narrative(text_neg_acomp_xcomp)
    success, index, graph_ttl = create_graph(sentence_instances, quotation_instances, 3, repo)
    ttl_str = str(graph_ttl)
    assert 'a {:negated true} :ReadinessAndAbility ; :text "is not able' in ttl_str
    assert 'a {:negated true} :EmotionalResponse ; :text "stomach' in ttl_str    # negative emotion
    assert ':has_active_entity :Jane' in ttl_str
    assert ':CommunicationAndSpeechAct ; :text "lies' in ttl_str or \
           ':DeceptionAndDishonesty ; :text "lies' in ttl_str
    assert ':has_topic :Noun' in ttl_str
    # Output Turtle:
    # :Sentence_f1102501-ffbc a :Sentence ; :offset 1 .
    # :Sentence_f1102501-ffbc :text "Jane is not able to stomach lies." .
    # :Jane :text "Jane" .
    # :Jane a :Person .
    # :Jane rdfs:label "Jane" .
    # :Jane :gender "female" .
    # :Sentence_f1102501-ffbc :mentions :Jane .
    # :Sentence_f1102501-ffbc :summary "Jane cannot tolerate dishonesty." .
    # :Sentence_f1102501-ffbc :sentiment "negative" .
    # :Sentence_f1102501-ffbc :grade_level 5 .
    # :Sentence_f1102501-ffbc :rhetorical_device {:evidence "The phrase \'not able to stomach\' uses loaded
    #     language to express strong aversion, invoking a visceral reaction to the concept of lies."}
    #     "loaded language" .
    # :Sentence_f1102501-ffbc :has_semantic :Event_9e53b791-20ed .
    # :Event_9e53b791-20ed a {:negated true} :ReadinessAndAbility ; :text "is not able to" .
    # :Event_9e53b791-20ed :has_active_entity :Jane .
    # :Event_9e53b791-20ed :has_topic [ :text "stomach lies" ; a :Clause ] .
    # :Sentence_f1102501-ffbc :has_semantic :Event_f8851efe-26fd .
    # :Event_f8851efe-26fd a {:negated true} :EmotionalResponse ; :text "stomach" .    # negative emotion
    # :Event_f8851efe-26fd :has_active_entity :Jane .
    # :Noun_faf59d0f-5f5f a :CommunicationAndSpeechAct ; :text "lies" ; rdfs:label "lies" .
    # :Event_f8851efe-26fd :has_topic :Noun_faf59d0f-5f5f .


def test_non_person_subject():
    sentence_instances, quotation_instances, quoted_strings = parse_narrative(text_non_person_subject)
    success, index, graph_ttl = create_graph(sentence_instances, quotation_instances, 3, repo)
    ttl_str = str(graph_ttl)
    assert '{:negated true} :EmotionalResponse ; :text "were dashed' in ttl_str
    assert ':has_topic :John' in ttl_str or ':has_topic :Noun' in ttl_str
    if ':has_topic :Noun' in ttl_str:
        assert 'a :EmotionalResponse ; :text "hopes' in ttl_str     # TODO: Ideally, distinguish John from his hopes
    # Output Turtle:
    # :Sentence_2f9ab1aa-663a a :Sentence ; :offset 1 .
    # :Sentence_2f9ab1aa-663a :text "John\'s hopes were dashed." .
    # :John :text "John" .
    # :John a :Person .
    # :John rdfs:label "John" .
    # :John :gender "male" .
    # :Sentence_2f9ab1aa-663a :mentions :John .
    # :Sentence_2f9ab1aa-663a :summary "John\'s hopes were destroyed." .
    # :Sentence_2f9ab1aa-663a :sentiment "negative" .
    # :Sentence_2f9ab1aa-663a :grade_level 3 .
    # :Sentence_2f9ab1aa-663a :has_semantic :Event_bf7728a7-efc5 .
    # :Event_bf7728a7-efc5 a {:negated true} :EmotionalResponse ; :text "were dashed" .
    # :Event_bf7728a7-efc5 :has_topic :John .
    # :Sentence_2f9ab1aa-663a :has_semantic :Event_c344a84d-b203 .
    # :Event_c344a84d-b203 a {:negated true} :EmotionalResponse ; :text "were dashed" .
    # :Event_c344a84d-b203 :has_topic :John .


def test_first_person():
    sentence_instances, quotation_instances, quoted_strings = parse_narrative(text_first_person)
    success, index, graph_ttl = create_graph(sentence_instances, quotation_instances, 3, repo)
    ttl_str = str(graph_ttl)
    assert ':sentiment "negative' in ttl_str
    assert '{:negated true} :ReadinessAndAbility ; :text "was not ready' in ttl_str
    assert ':negated true' in ttl_str
    assert 'a :Person ; :text "I' in ttl_str
    assert ':has_active_entity :Noun' in ttl_str
    assert 'a :MovementTravelAndTransportation ; :text "to leave' in ttl_str
    assert ':has_semantic {:future true} :Event' in ttl_str or ':has_semantic :Event' in ttl_str
    # Output Turtle:
    # :Sentence_0806ce9b-eb3d a :Sentence ; :offset 1 .
    # :Sentence_0806ce9b-eb3d :text "I was not ready to leave." .
    # :Sentence_0806ce9b-eb3d :summary "Reluctance to depart expressed." .
    # :Sentence_0806ce9b-eb3d :sentiment "negative" .
    # :Sentence_0806ce9b-eb3d :grade_level 3 .
    # :Sentence_0806ce9b-eb3d :has_semantic :Event_ea1357a3-cd00 .
    # :Event_ea1357a3-cd00 a {:negated true} :ReadinessAndAbility ; :text "was not ready" .
    # :Noun_40089061-f9e0 a :Person ; :text "I" ; rdfs:label "I" .
    # :Event_ea1357a3-cd00 :has_active_entity :Noun_40089061-f9e0 .
    # :Sentence_0806ce9b-eb3d :has_semantic {:future true} :Event_7c6604c4-0a6d .
    # :Event_7c6604c4-0a6d a :MovementTravelAndTransportation ; :text "to leave" .
    # :Event_7c6604c4-0a6d :has_active_entity :Noun_40089061-f9e0 .


def test_pobj_semantics():
    sentence_instances, quotation_instances, quoted_strings = parse_narrative(text_pobj_semantics)
    success, index, graph_ttl = create_graph(sentence_instances, quotation_instances, 3, repo)
    ttl_str = str(graph_ttl)
    assert 'a :Avoidance ; :text "escaped' in ttl_str
    assert '{:negated true} :ArrestAndImprisonment ; :text "escaped' in ttl_str
    assert 'a :Person ; :text "robber' in ttl_str
    assert ':has_active_entity :Noun' in ttl_str
    assert 'a :GovernmentalEntity ; :text "police' in ttl_str
    assert ':has_instrument :Noun' in ttl_str
    # Output Turtle:
    # :Sentence_36cf8f2b-0af2 a :Sentence ; :offset 1 .
    # :Sentence_36cf8f2b-0af2 :text "The robber escaped with the aid of the local police." .
    # :Sentence_36cf8f2b-0af2 :summary "Robber escapes with local police assistance." .
    # :Sentence_36cf8f2b-0af2 :sentiment "negative" .
    # :Sentence_36cf8f2b-0af2 :grade_level 5 .
    # :Sentence_36cf8f2b-0af2 :rhetorical_device {:evidence "The phrase \'the aid of the local police\' uses
    #     loaded language, implying that the police were complicit in the crime, which invokes strong emotional
    #     reactions and judgments."}  "loaded language" .
    # :Sentence_36cf8f2b-0af2 :has_semantic :Event_ddaee614-5364 .
    # :Event_ddaee614-5364 a :Avoidance ; :text "escaped" .
    # :Event_ddaee614-5364 a {:negated true} :ArrestAndImprisonment ; :text "escaped" .
    # :Noun_cbeb3e81-cb11 a :Person ; :text "robber" ; rdfs:label "The robber" .
    # :Event_ddaee614-5364 :has_active_entity :Noun_cbeb3e81-cb11 .
    # :Noun_13ee0ca5-45ee a :GovernmentalEntity ; :text "police" ; rdfs:label "with the aid of the local police" .
    # :Event_ddaee614-5364 :has_instrument :Noun_13ee0ca5-45ee


def test_multiple_subjects():
    sentence_instances, quotation_instances, quoted_strings = parse_narrative(text_multiple_subjects)
    success, index, graph_ttl = create_graph(sentence_instances, quotation_instances, 3, repo)
    ttl_str = str(graph_ttl)
    assert ':DisagreementAndDispute' in ttl_str
    assert 'a :Person, :Collection ; :text "Jane and John' in ttl_str
    assert ':has_active_entity :Noun' in ttl_str
    # Output Turtle:
    # :Sentence_784cf881-355b a :Sentence ; :offset 1 .
    # :Sentence_784cf881-355b :text "Jane and John had a serious difference of opinion." .
    # :Jane :text "Jane" .
    # :Jane a :Person .
    # :Jane rdfs:label "Jane" .
    # :Jane :gender "female" .
    # :John :text "John" .
    # :John a :Person .
    # :John rdfs:label "John" .
    # :John :gender "male" .
    # :Sentence_784cf881-355b :mentions :Jane .
    # :Sentence_784cf881-355b :mentions :John .
    # :Sentence_784cf881-355b :summary "Jane and John disagreed seriously." .
    # :Sentence_784cf881-355b :sentiment "negative" .
    # :Sentence_784cf881-355b :grade_level 3 .
    # :Sentence_784cf881-355b :has_semantic :Event_e3d7666d-cc31 .
    # :Event_e3d7666d-cc31 a :DisagreementAndDispute ; :text "had" .
    # :Noun_1a81ecf3-4e9c a :Person, :Collection ; :text "Jane and John" ; rdfs:label "Jane and John" .
    # :Event_e3d7666d-cc31 :has_active_entity :Noun_1a81ecf3-4e9c .
    # :Noun_9af3af20-b2fc a :TroubleAndProblem ; :text "difference of opinion" ;
    #     rdfs:label "a serious difference of opinion" .
    # :Event_e3d7666d-cc31 :has_topic :Noun_9af3af20-b2fc .


def test_multiple_xcomp():
    sentence_instances, quotation_instances, quoted_strings = parse_narrative(text_multiple_xcomp)
    success, index, graph_ttl = create_graph(sentence_instances, quotation_instances, 3, repo)
    ttl_str = str(graph_ttl)
    assert (':BodilyAct' in ttl_str or ':ArtAndEntertainmentEvent' in ttl_str) and ':EmotionalResponse' in ttl_str
    assert ':has_active_entity :John' in ttl_str
    # Output Turtle:
    # :Sentence_dbb3cf1d-304e a :Sentence ; :offset 1 .
    # :Sentence_dbb3cf1d-304e :text "John liked to ski and to swim." .
    # :John :text "John" .
    # :John a :Person .
    # :John rdfs:label "John" .
    # :John :gender "male" .
    # :Sentence_dbb3cf1d-304e :mentions :John .
    # :Sentence_dbb3cf1d-304e :summary "John enjoys skiing and swimming." .
    # :Sentence_dbb3cf1d-304e :sentiment "positive" .
    # :Sentence_dbb3cf1d-304e :grade_level 3 .
    # :Sentence_dbb3cf1d-304e :has_semantic :Event_618f4446-a314 .
    # :Event_618f4446-a314 a :BodilyAct, :EmotionalResponse ; :text "liked to ski and to swim" .
    # :Event_618f4446-a314 :has_active_entity :John .
    # :Sentence_dbb3cf1d-304e :has_semantic :Event_343e5d45-956d .
    # :Event_343e5d45-956d a :BodilyAct ; :text "to ski" .
    # :Event_343e5d45-956d :has_active_entity :John .
    # :Sentence_dbb3cf1d-304e :has_semantic :Event_199d71fa-2713 .
    # :Event_199d71fa-2713 a :BodilyAct ; :text "to swim" .
    # :Event_199d71fa-2713 :has_active_entity :John .


def test_location_hierarchy():
    sentence_instances, quotation_instances, quoted_strings = parse_narrative(text_location_hierarchy)
    success, index, graph_ttl = create_graph(sentence_instances, quotation_instances, 3, repo)
    ttl_str = str(graph_ttl)
    assert ':mentions geo:2658434' in ttl_str     # Switzerland
    assert 'imagery' in ttl_str or 'exceptionalism' in ttl_str
    assert 'a :EnvironmentAndCondition' in ttl_str
    assert ':has_topic geo:2658434' in ttl_str     # TODO: Resolve to Switzerland's mountatins, not just Switzerland
    # Output Turtle:
    # :Sentence_933251b1-8a73 a :Sentence ; :offset 1 .
    # :Sentence_933251b1-8a73 :text "Switzerland\'s mountains are magnificent." .
    # :Sentence_933251b1-8a73 :mentions geo:2658434 .
    # :Sentence_933251b1-8a73 :summary "Switzerland\'s mountains described as magnificent." .
    # :Sentence_933251b1-8a73 :sentiment "positive" .
    # :Sentence_933251b1-8a73 :grade_level 3 .
    # :Sentence_933251b1-8a73 :rhetorical_device {:evidence "The word \'magnificent\' indicates that Switzerland\'s
    #     mountains are described as extraordinary or exemplary."}  "exceptionalism" .
    # :Sentence_933251b1-8a73 :has_semantic :Event_2f7cde2c-10c1 .
    # :Event_2f7cde2c-10c1 a :EnvironmentAndCondition ; :text "are magnificent" .
    # :Event_2f7cde2c-10c1 :has_topic geo:2658434 .


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
    # :Sentence_bc8c28e2-e412 a :Sentence ; :offset 1 .
    # :Sentence_bc8c28e2-e412 :text "Hurricane Otis severely damaged Acapulco." .
    # :Hurricane_Otis :text "Hurricane Otis" .
    # :Hurricane_Otis a :EnvironmentalOrEcologicalEvent .
    # :Hurricane_Otis rdfs:label "Otis", "Hurricane Otis" .
    # :Hurricane_Otis rdfs:comment "From Wikipedia (wikibase_item: Q123178445): \'Hurricane Otis was a compact but
    #     very powerful tropical cyclone which made a devastating landfall in October 2023 near Acapulco as a
    #     Category 5 hurricane. ...\'" .
    # :Hurricane_Otis :external_link "https://en.wikipedia.org/wiki/Hurricane_Otis" .
    # :Hurricane_Otis :external_identifier {:identifier_source "Wikidata"} "Q123178445" .
    # :Acapulco :text "Acapulco" .
    # :Acapulco a :PopulatedPlace .
    # :Acapulco rdfs:label "Acapulco de Juárez", "Acapulco", "Acapulco de Juarez" .
    # :Acapulco rdfs:comment "From Wikipedia (wikibase_item: Q81398): \'Acapulco de Ju?rez, commonly called
    #     Acapulco, Guerrero, is a city and major seaport in the state of Guerrero on the Pacific Coast of Mexico,
    #     380 kilometres (240 mi) south of Mexico City. ... \'" .
    # :Acapulco :external_link "https://en.wikipedia.org/wiki/Acapulco" .
    # :Acapulco :external_identifier {:identifier_source "Wikidata"} "Q81398" .
    # :Acapulco :country_name "Mexico" .
    # geo:3996063 :has_component :Acapulco .
    # :Acapulco a :OrganizationalEntity .
    # :Acapulco rdfs:label "Acapulco de Juárez", "Acapulco", "Acapulco de Juarez" .
    # :Sentence_bc8c28e2-e412 :mentions :Hurricane_Otis .
    # :Sentence_bc8c28e2-e412 :mentions :Acapulco .
    # :Sentence_bc8c28e2-e412 :summary "Hurricane Otis severely damaged Acapulco." .
    # :Sentence_bc8c28e2-e412 :sentiment "negative" .
    # :Sentence_bc8c28e2-e412 :grade_level 5 .
    # :Sentence_bc8c28e2-e412 :has_semantic :Event_9d967437-7f6f .
    # :Event_9d967437-7f6f a :EnvironmentalOrEcologicalEvent ; :text "severely damaged" .
    # :Event_9d967437-7f6f :has_active_entity :Hurricane_Otis .
    # :Event_9d967437-7f6f :has_cause :Hurricane_Otis .
    # :Event_9d967437-7f6f :has_affected_entity :Acapulco .
    # :Event_9d967437-7f6f :has_location :Acapulco .


def test_coref():
    sentence_instances, quotation_instances, quoted_strings = parse_narrative(text_coref)
    success, index, graph_ttl = create_graph(sentence_instances, quotation_instances, 3, repo)
    ttl_str = str(graph_ttl)
    assert 'a :Change ; :text "cut' in ttl_str or 'a :Separation ; :text "cut' in ttl_str or \
           'a :AgricultureApicultureAndAquacultureEvent ; :text "cut' in ttl_str
    assert 'a :Cognition ; :text "saw' in ttl_str or 'a :SensoryPerception ; :text "saw' in ttl_str
    assert ':has_active_entity :Heidi' in ttl_str    # cutting
    assert 'a {:negated true} :Cognition ; :text "did not recognize' in ttl_str
    assert ':has_active_entity :Anna' in ttl_str     # seeing
    assert ':has_topic [ :text' in ttl_str
    # Output Turtle:
    # :Sentence_4d9867bf-6138 a :Sentence ; :offset 1 .
    # :Sentence_4d9867bf-6138 :text "Anna saw Heidi cut the roses, but she did not recognize that it was
    #     Heidi who cut the roses." .
    # :Anna :text "Anna" .
    # :Anna a :Person .
    # :Anna rdfs:label "Anna" .
    # :Anna :gender "female" .
    # :Heidi :text "Heidi" .
    # :Heidi a :Person .
    # :Heidi rdfs:label "Heidi" .
    # :Heidi :gender "female" .
    # :Sentence_4d9867bf-6138 :mentions :Anna .
    # :Sentence_4d9867bf-6138 :mentions :Heidi .
    # :Sentence_4d9867bf-6138 :mentions :Heidi .
    # :Sentence_4d9867bf-6138 :summary "Anna saw Heidi cutting roses, failed to recognize Heidi." .
    # :Sentence_4d9867bf-6138 :sentiment "neutral" .
    # :Sentence_4d9867bf-6138 :grade_level 5 .
    # :Sentence_4d9867bf-6138 :has_semantic :Event_330cfe46-b750 .
    # :Event_330cfe46-b750 a :Cognition ; :text "saw" .
    # :Event_330cfe46-b750 :has_active_entity :Anna .
    # :Event_330cfe46-b750 :has_topic [ :text "Heidi cut the roses" ; a :Clause ] .
    # :Sentence_4d9867bf-6138 :has_semantic :Event_c8451944-0940 .
    # :Event_c8451944-0940 a :AgricultureApicultureAndAquacultureEvent ; :text "cut the roses" .
    # :Event_c8451944-0940 :has_active_entity :Heidi .
    # :Noun_3ba541e5-0d24 a :Plant ; :text "roses" ; rdfs:label "the roses" .
    # :Event_c8451944-0940 :has_affected_entity :Noun_3ba541e5-0d24 .
    # :Sentence_4d9867bf-6138 :has_semantic :Event_e8c7aee4-2d6c .
    # :Event_e8c7aee4-2d6c a {:negated true} :Cognition ; :text "did not recognize" .
    # :Event_e8c7aee4-2d6c :has_active_entity :Anna .
    # :Event_e8c7aee4-2d6c :has_topic [ :text "that it was Heidi who cut the roses" ; a :Clause ] .
    # :Sentence_4d9867bf-6138 :has_semantic :Event_020cbca4-f8b0 .
    # :Event_020cbca4-f8b0 a :EnvironmentAndCondition ; :text "was" .
    # :Noun_f2a28752-752d a :Cognition ; :text "it" ; rdfs:label "it" .     # TODO: Not relevant
    # :Event_020cbca4-f8b0 :has_topic :Noun_f2a28752-752d .
    # :Event_020cbca4-f8b0 :has_described_entity :Heidi .
    # :Sentence_4d9867bf-6138 :has_semantic :Event_d342e8a1-dbff .
    # :Event_d342e8a1-dbff a :AgricultureApicultureAndAquacultureEvent ; :text "cut the roses" .
    # :Event_d342e8a1-dbff :has_active_entity :Heidi .
    # :Event_d342e8a1-dbff :has_topic :Noun_3ba541e5-0d24 .


def test_quotation():
    sentence_instances, quotation_instances, quoted_strings = parse_narrative(text_quotation)
    success, index, graph_ttl = create_graph(sentence_instances, quotation_instances, 3, repo)
    ttl_str = str(graph_ttl)
    print(ttl_str)
    assert 'a :Change ; :text "cut' in ttl_str or 'a :Separation ; :text "cut' in ttl_str or \
           'a :AgricultureApicultureAndAquacultureEvent ; :text "cut' in ttl_str
    assert 'a :Cognition ; :text "saw' in ttl_str or 'a :SensoryPerception ; :text "saw' in ttl_str
    assert ':has_active_entity :Heidi' in ttl_str    # cutting
    assert 'a {:negated true} :Cognition ; :text "did not recognize' in ttl_str
    assert ':has_active_entity :Anna' in ttl_str     # seeing
    assert ':has_topic [ :text' in ttl_str
    # Output Turtle:
    # :Sentence_49559f87-0517 a :Sentence ; :offset 1 .
    # :Sentence_49559f87-0517 :text "Jane said, [Quotation0]" .
    # :Sentence_49559f87-0517 :has_component :Quotation0 .
    # :NVIDIA :text "NVIDIA" .
    # :NVIDIA a :OrganizationalEntity, :Correction .
    # :NVIDIA rdfs:label "Nvidia Corp.", "Nvidia Corporation", "Nvidia", "NVIDIA" .
    # :NVIDIA rdfs:comment "From Wikipedia (wikibase_item: Q182477): \'Nvidia Corporation is an American multinational
    #     corporation and technology company headquartered in Santa Clara, California, and incorporated in Delaware.
    #     It is a software and fabless company which designs and supplies graphics processing units (GPUs), ...\'" .
    # :NVIDIA :external_link "https://en.wikipedia.org/wiki/Nvidia" .
    # :NVIDIA :external_identifier "Q182477" .
    # :Jane :text "Jane" .
    # :Jane a :Person, :Correction .
    # :Jane rdfs:label "Jane" .
    # :Jane :gender "female" .
    # :Sentence_49559f87-0517 :mentions :NVIDIA .
    # :Sentence_49559f87-0517 :mentions :Jane .
    # :Sentence_49559f87-0517 :summary "Jane communicates content of Quotation0." .
    # :Sentence_49559f87-0517 :sentiment "neutral" .
    # :Sentence_49559f87-0517 :grade_level 4 .
    # :Sentence_49559f87-0517 :has_semantic :Event_b4ac0364-01db .
    # :Event_b4ac0364-01db a :CommunicationAndSpeechAct ; :text "said" .
    # :Event_b4ac0364-01db :has_active_entity :Jane .
    # :Event_b4ac0364-01db :has_topic :Quotation0 .
    # :Quotation1 a :Quote ; :text "I want to work for NVIDIA." .
    # :Quotation1 :attributed_to :Jane .
    # :Quotation1 :summary "Desire to work for NVIDIA expressed." .
    # :Quotation1 :sentiment "positive" .
    # :Quotation1 :grade_level 5 .
