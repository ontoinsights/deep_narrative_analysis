import pytest
from dna.create_narrative_turtle import create_graph
from dna.nlp import parse_narrative

text_multiple_acomp = 'Jane is averse to broccoli and kale.'
text_multiple_verbs = 'Sue is an attorney but still lies.'
text_aux_pobj = 'John got rid of the debris.'
text_idiom_npadvmod = 'John looked the other way when it came to Mary.'
text_idiom_amod = "John turned a blind eye to Mary's infidelity."
text_advmod = 'Harry put the broken vase back together.'
text_complex_verb = 'The store went out of business on Tuesday.'
text_acomp_xcomp = 'Jane is unable to stomach lies.'
text_neg_acomp_xcomp = 'Jane is not able to stomach lies.'
text_non_person_subject = "John's hopes were dashed."
text_first_person = 'I was not ready to leave.'
text_pobj_semantics = 'The robber escaped with the aid of the local police.'
text_multiple_subjects = 'Jane and John had a serious difference of opinion.'
text_multiple_xcomp = 'John liked to ski and to swim.'
text_location_hierarchy = "Switzerland's mountains are magnificent."
text_weather = "Hurricane Otis severely damaged Acapulco, Mexico."
text_coref = 'Anna saw Heidi cut the roses, but she did not recognize that it was Heidi who cut the roses.'

# Note that it is unlikely that all tests will complete successfully since event semantics can be
# interpreted/reported in multiple ways
# 80% of tests should pass


def test_multiple_acomp():
    sent_dicts, quotations, quotations_dict = parse_narrative(text_multiple_acomp)
    success, index, graph_ttl = create_graph(quotations_dict, sent_dicts)
    ttl_str = str(graph_ttl)
    assert 'a :EmotionalResponse ; :text "averse' in ttl_str
    assert ':has_active_entity :Jane' in ttl_str
    assert ':has_topic [ :text "broccoli" ; a :Plant' in ttl_str
    assert ':has_topic [ :text "kale" ; a :Plant' in ttl_str
    # Output Turtle:
    # :Sentence_22e7c782-7b93 a :Sentence ; :offset 1 .
    # :Sentence_22e7c782-7b93 :text "Jane is averse to broccoli and kale." .
    # :Jane a :Person .
    # :Jane rdfs:label "Jane" .
    # :Jane rdfs:comment "Needs disambiguation; See the web site, https://en.wikipedia.org/wiki/Jane" .
    # :Jane :gender "female" .
    # :Sentence_22e7c782-7b93 :mentions :Jane .
    # :Sentence_22e7c782-7b93 :sentence_person 3 ; :sentiment "negative".
    # :Sentence_22e7c782-7b93 :voice "active" ; :tense "present" ; :summary "Jane dislikes broccoli, kale." .
    # :Sentence_22e7c782-7b93 :grade_level 3 .
    # :Sentence_22e7c782-7b93 :has_semantic :Event_6563f64a-344e .
    # :Event_6563f64a-344e a :EmotionalResponse ; :text "averse" .
    # :Event_6563f64a-344e :has_active_entity :Jane .
    # :Event_6563f64a-344e :has_topic [ :text "broccoli" ; a :Plant ] .
    # :Event_6563f64a-344e :has_topic [ :text "kale" ; a :Plant ] .


def test_multiple_verbs():
    sent_dicts, quotations, quotations_dict = parse_narrative(text_multiple_verbs)
    success, index, graph_ttl = create_graph(quotations_dict, sent_dicts)
    ttl_str = str(graph_ttl)
    assert 'pathos' in ttl_str or 'ad hominem' in ttl_str
    assert ':has_active_entity :Sue' in ttl_str
    if 'a :EnvironmentAndCondition' in ttl_str:    # is
        assert ':has_described_entity :Sue' in ttl_str
        assert ':text "attorney' in ttl_str or ':text "is an attorney' in ttl_str
    else:
        assert 'a :KnowledgeAndSkill ; :text "attorney' in ttl_str
        assert ':has_described_entity :Sue' in ttl_str
    assert 'a :DeceptionAndDishonesty ; :text "lies' in ttl_str
    assert ':has_active_entity :Sue' in ttl_str
    # Output Turtle:
    # :Sentence_3539b873-5144 a :Sentence ; :offset 1 .
    # :Sentence_3539b873-5144 :text "Sue is an attorney but still lies." .
    # :Sue a :Person .
    # :Sue rdfs:label "Sue" .
    # :Sue rdfs:comment "Needs disambiguation; See the web site, https://en.wikipedia.org/wiki/Sue" .
    # :Sue :gender "female" .
    # :Sentence_3539b873-5144 :mentions :Sue .
    # :Sentence_3539b873-5144 :sentence_person 3 ; :sentiment "negative".
    # :Sentence_3539b873-5144 :voice "active" ; :tense "present" ; :summary "Attorney Sue lies." .
    # :Sentence_3539b873-5144 :grade_level 6 .
    # :Sentence_3539b873-5144 :rhetorical_device {:evidence "The use of the word \'lies\' can be seen as a form
    #        of invective, as it is an angry or insulting accusation."}  "invective" .
    # :Sentence_3539b873-5144 :rhetorical_device {:evidence "The statement may appeal to the emotion of distrust
    #        or disappointment, as it contrasts the expectation of honesty associated with a professional like an
    #        attorney with the negative behavior of lying."}  "pathos" .
    # :Sentence_3539b873-5144 :has_semantic :Event_e3bf5ea9-824e .
    # :Event_e3bf5ea9-824e a :KnowledgeAndSkill ; :text "attorney" .
    # :Event_e3bf5ea9-824e :has_active_entity :Sue .
    # :Sentence_3539b873-5144 :has_semantic :Event_3c034bd0-4c08 .
    # :Event_3c034bd0-4c08 a :DeceptionAndDishonesty ; :text "lies" .
    # :Event_3c034bd0-4c08 :has_active_entity :Sue .


def test_aux_pobj():
    sent_dicts, quotations, quotations_dict = parse_narrative(text_aux_pobj)
    success, index, graph_ttl = create_graph(quotations_dict, sent_dicts)
    ttl_str = str(graph_ttl)
    assert 'a :RemovalAndRestriction ; :text "got rid of' in ttl_str
    assert ':has_active_entity :Joe' in ttl_str
    assert ':has_affected_entity [ :text "debris" ; a :WasteAndResidue' in ttl_str
    # Output Turtle:
    # :Sentence_f76fd9c9-da7b a :Sentence ; :offset 1 .
    # :Sentence_f76fd9c9-da7b :text "John got rid of the debris." .
    # :John a :Person .
    # :John rdfs:label "John" .
    # :John rdfs:comment "Needs disambiguation; See the web site, https://en.wikipedia.org/wiki/John" .
    # :John :gender "male" .
    # :Sentence_f76fd9c9-da7b :mentions :John .
    # :Sentence_f76fd9c9-da7b :sentence_person 3 ; :sentiment "neutral".
    # :Sentence_f76fd9c9-da7b :voice "active" ; :tense "past" ; :summary "John cleared debris." .
    # :Sentence_f76fd9c9-da7b :grade_level 3 .
    # :Sentence_f76fd9c9-da7b :has_semantic :Event_a1646e3f-804b .
    # :Event_a1646e3f-804b a :RemovalAndRestriction ; :text "got rid of" .
    # :Event_a1646e3f-804b :has_active_entity :John .  # TODO: Reports passive voice => has_affected_entity :John
    # :Event_a1646e3f-804b :has_affected_entity [ :text "debris" ; a :WasteAndResidue ] .


def test_idiom_npadvmod():
    sent_dicts, quotations, quotations_dict = parse_narrative(text_idiom_npadvmod)
    success, index, graph_ttl = create_graph(quotations_dict, sent_dicts)
    ttl_str = str(graph_ttl)
    assert 'a :Avoidance ; :text "looked the other way' in ttl_str
    assert ':has_active_entity :John' in ttl_str
    assert ':has_topic :Mary' in ttl_str
    # Output Turtle:
    # :Sentence_de1d8fe5-d9a4 a :Sentence ; :offset 1 .
    # :Sentence_de1d8fe5-d9a4 :text "John looked the other way when it came to Mary." .
    # :John a :Person .
    # :John rdfs:label "John" .
    # :John rdfs:comment "Needs disambiguation; See the web site, https://en.wikipedia.org/wiki/John" .
    # :John :gender "male" .
    # :Mary a :Person .
    # :Mary rdfs:label "Mary" .
    # :Mary rdfs:comment "Needs disambiguation; See the web site, https://en.wikipedia.org/wiki/Mary" .
    # :Mary :gender "female" .
    # :Sentence_de1d8fe5-d9a4 :mentions :John .
    # :Sentence_de1d8fe5-d9a4 :mentions :Mary .
    # :Sentence_de1d8fe5-d9a4 :sentence_person 3 ; :sentiment "neutral".
    # :Sentence_de1d8fe5-d9a4 :voice "active" ; :tense "past" ; :summary "John ignored Mary\'s issue." .
    # :Sentence_de1d8fe5-d9a4 :grade_level 5 .
    # :Sentence_de1d8fe5-d9a4 :has_semantic :Event_f029ddde-e0e2 .
    # :Event_f029ddde-e0e2 a :Avoidance ; :text "looked the other way" .
    # :Event_f029ddde-e0e2 :has_active_entity :John .
    # :Event_f029ddde-e0e2 :has_topic :Mary .


def test_idiom_amod():
    sent_dicts, quotations, quotations_dict = parse_narrative(text_idiom_amod)
    success, index, graph_ttl = create_graph(quotations_dict, sent_dicts)
    ttl_str = str(graph_ttl)
    assert 'metaphor' in ttl_str
    assert 'a :Avoidance ; :text "turned a blind eye' in ttl_str
    assert ':has_active_entity :John' in ttl_str
    assert ':has_topic [ :text "Mary' in ttl_str or ':has_topic :Mary' in ttl_str
    # Output Turtle:
    # :Sentence_a1621d46-6ed8 a :Sentence ; :offset 1 .
    # :Sentence_a1621d46-6ed8 :text "John turned a blind eye to Mary\'s infidelity." .
    # :John a :Person .
    # :John rdfs:label "John" .
    # :John rdfs:comment "Needs disambiguation; See the web site, https://en.wikipedia.org/wiki/John" .
    # :John :gender "male" .
    # :Mary a :Person .
    # :Mary rdfs:label "Mary" .
    # :Mary rdfs:comment "Needs disambiguation; See the web site, https://en.wikipedia.org/wiki/Mary" .
    # :Mary :gender "female" .
    # :Sentence_a1621d46-6ed8 :mentions :John .
    # :Sentence_a1621d46-6ed8 :mentions :Mary .
    # :Sentence_a1621d46-6ed8 :sentence_person 3 ; :sentiment "negative".
    # :Sentence_a1621d46-6ed8 :voice "active" ; :tense "past" ; :summary "John ignored Mary\'s cheating." .
    # :Sentence_a1621d46-6ed8 :grade_level 7 .
    # :Sentence_a1621d46-6ed8 :rhetorical_device {:evidence "The phrase \'turned a blind eye\' is a metaphor for
    #      intentionally ignoring something, comparing the act of ignoring to the physical act of closing or
    #      turning one\'s eye away."}  "metaphor" .
    # :Sentence_a1621d46-6ed8 :has_semantic :Event_24b36d0e-4fff .
    # :Event_24b36d0e-4fff  a :Avoidance ; :text "turned a blind eye" .
    # :Event_24b36d0e-4fff :has_active_entity :John .
    # :Event_24b36d0e-4fff :has_topic :Mary .    # TODO: or Mary's infidelity


def test_advmod():
    sent_dicts, quotations, quotations_dict = parse_narrative(text_advmod)
    success, index, graph_ttl = create_graph(quotations_dict, sent_dicts)
    ttl_str = str(graph_ttl)
    assert 'a :ReturnRecoveryAndRelease ; :text "put back together' in ttl_str
    assert ':has_active_entity :Harry' in ttl_str
    assert ':has_topic [ :text "vase' in ttl_str or ':has_affected_entity [ :text "vase' in ttl_str
    # Output Turtle:
    # :Sentence_49ef0e5a-d031 a :Sentence ; :offset 1 .
    # :Sentence_49ef0e5a-d031 :text "Harry put the broken vase back together." .
    # :Harry a :Person .
    # :Harry rdfs:label "Harry" .
    # :Harry rdfs:comment "Needs disambiguation; See the web site, https://en.wikipedia.org/wiki/Harry" .
    # :Harry :gender "male" .
    # :Sentence_49ef0e5a-d031 :mentions :Harry .
    # :Sentence_49ef0e5a-d031 :sentence_person 3 ; :sentiment "positive".
    # :Sentence_49ef0e5a-d031 :voice "active" ; :tense "past" ; :summary "Harry repaired a vase." .
    # :Sentence_49ef0e5a-d031 :grade_level 3 .
    # :Sentence_49ef0e5a-d031 :has_semantic  :Event_186674f8-4a61 .
    # :Event_186674f8-4a61 a :ReturnRecoveryAndRelease ; :text "put back together" .
    # :Event_186674f8-4a61 :has_active_entity :Harry .
    # :Event_186674f8-4a61 :has_topic [ :text "vase" ; a :ComponentPart ] .  # TODO: Not 'component part'


def test_complex_verb():
    sent_dicts, quotations, quotations_dict = parse_narrative(text_complex_verb)
    success, index, graph_ttl = create_graph(quotations_dict, sent_dicts)
    ttl_str = str(graph_ttl)
    assert 'a :End ; :text "went out of business' in ttl_str
    assert ':has_active_entity [ :text "store" ; a :OrganizationalEntity' in ttl_str or \
           ':has_active_entity [ :text "store" ; a :Location' in ttl_str or \
           ':has_topic [ :text "store" ; a :OrganizationalEntity' in ttl_str or \
           ':has_topic [ :text "store" ; a :Location' in ttl_str
    # Output Turtle:
    # :Sentence_7adde9e0-d3ba a :Sentence ; :offset 1 .
    # :Sentence_7adde9e0-d3ba :text "The store went out of business on Tuesday." .
    # :PiT_DayTuesday a :PointInTime ; rdfs:label "Tuesday" .
    # :Sentence_7adde9e0-d3ba :mentions :Tuesday .
    # :Sentence_7adde9e0-d3ba :sentence_person 3 ; :sentiment "negative".
    # :Sentence_7adde9e0-d3ba :voice "active" ; :tense "past" ; :summary "Store closed on Tuesday." .
    # :Sentence_7adde9e0-d3ba :grade_level 5 .
    # :Sentence_7adde9e0-d3ba :has_semantic :Event_59a0d632-e62e .
    # :Event_59a0d632-e62e a :End ; :text "went out of business" .
    # :Event_59a0d632-e62e :has_active_entity [ :text "The store" ; a :OrganizationalEntity ] .
    # :Event_59a0d632-e62e a :EnvironmentAndCondition ; :text "on Tuesday" .


def test_acomp_xcomp():
    sent_dicts, quotations, quotations_dict = parse_narrative(text_acomp_xcomp)
    success, index, graph_ttl = create_graph(quotations_dict, sent_dicts)
    ttl_str = str(graph_ttl)
    assert 'pathos' in ttl_str
    assert ':tense "present"' in ttl_str
    assert 'a :EmotionalResponse ; :text "unable to stomach' in ttl_str
    assert ':has_active_entity :Jane' in ttl_str
    assert ':has_topic [ :text "lies' in ttl_str
    # Output Turtle:
    # :Sentence_dc46c5ac-3851 a :Sentence ; :offset 1 .
    # :Sentence_dc46c5ac-3851 :text "Jane is unable to stomach lies." .
    # :Jane a :Person .
    # :Jane rdfs:label "Jane" .
    # :Jane rdfs:comment "Needs disambiguation; See the web site, https://en.wikipedia.org/wiki/Jane" .
    # :Jane :gender "female" .
    # :Sentence_dc46c5ac-3851 :mentions :Jane .
    # :Sentence_dc46c5ac-3851 :sentence_person 3 ; :sentiment "negative".
    # :Sentence_dc46c5ac-3851 :voice "active" ; :tense "present" ; :summary "Jane hates lies" .
    # :Sentence_dc46c5ac-3851 :grade_level 5 .
    # :Sentence_dc46c5ac-3851 :rhetorical_device {:evidence "The phrase \'unable to stomach\' appeals to emotion
    #      by evoking a sense of strong aversion or disgust."}  "pathos" .
    # :Sentence_dc46c5ac-3851 :has_semantic :Event_35bd27fe-960e .
    # :Event_35bd27fe-960e a :EmotionalResponse ; :text "unable to stomach" .
    # :Event_35bd27fe-960e :has_active_entity :Jane .
    # :Event_35bd27fe-960e :has_topic [ :text "lies" ; a :AggressiveCriminalOrHostileAct ] .


def test_neg_acomp_xcomp():
    sent_dicts, quotations, quotations_dict = parse_narrative(text_neg_acomp_xcomp)
    success, index, graph_ttl = create_graph(quotations_dict, sent_dicts)
    ttl_str = str(graph_ttl)
    assert 'pathos' in ttl_str
    assert ':tense "present"' in ttl_str
    assert 'a :EmotionalResponse ; :text "unable to stomach' in ttl_str
    assert ':has_active_entity :Jane' in ttl_str
    assert ':has_topic [ :text "lies' in ttl_str
    # Output Turtle:
    # :Sentence_fd1933a8-390c a :Sentence ; :offset 1 .
    # :Sentence_fd1933a8-390c :text "Jane is not able to stomach lies." .
    # :Jane a :Person .
    # :Jane rdfs:label "Jane" .
    # :Jane rdfs:comment "Needs disambiguation; See the web site, https://en.wikipedia.org/wiki/Jane" .
    # :Jane :gender "female" .
    # :Sentence_fd1933a8-390c :mentions :Jane .
    # :Sentence_fd1933a8-390c :sentence_person 3 ; :sentiment "negative".
    # :Sentence_fd1933a8-390c :voice "active" ; :tense "present" ; :summary "Jane dislikes lies" .
    # :Sentence_fd1933a8-390c :grade_level 5 .
    # :Sentence_fd1933a8-390c :rhetorical_device {:evidence "The phrase \'not able to stomach\' appeals to the
    #      emotion of disgust or intolerance towards dishonesty."}  "pathos" .
    # :Sentence_fd1933a8-390c :has_semantic {:negated true} :Event_07f8c237-dbc0 .
    # :Event_07f8c237-dbc0 a :EmotionalResponse ; :text "able to stomach" .
    # :Event_07f8c237-dbc0 :has_active_entity :Jane .
    # :Event_07f8c237-dbc0 :has_topic [ :text "lies" ; a :AggressiveCriminalOrHostileAct ] .


def test_non_person_subject():
    sent_dicts, quotations, quotations_dict = parse_narrative(text_non_person_subject)
    success, index, graph_ttl = create_graph(quotations_dict, sent_dicts)
    ttl_str = str(graph_ttl)
    assert 'pathos' in ttl_str or 'imagery' in ttl_str
    assert ':tense "past' in ttl_str
    assert ' a :EmotionalResponse' in ttl_str     # hopes
    assert ' a :End' in ttl_str                   # dashed
    assert ':has_affected_entity :John' in ttl_str
    # Output Turtle:
    # :Sentence_648a27fc-ef20 a :Sentence ; :offset 1 .
    # :Sentence_648a27fc-ef20 :text "John\'s hopes were dashed." .
    # :John a :Person .
    # :John rdfs:label "John" .
    # :John rdfs:comment "Needs disambiguation; See the web site, https://en.wikipedia.org/wiki/John" .
    # :John :gender "male" .
    # :Sentence_648a27fc-ef20 :mentions :John .
    # :Sentence_648a27fc-ef20 :sentence_person 3 ; :sentiment "negative".
    # :Sentence_648a27fc-ef20 :voice "passive" ; :tense "past" ; :summary "John\'s hopes were destroyed." .
    # :Sentence_648a27fc-ef20 :grade_level 5 .
    # :Sentence_648a27fc-ef20 :rhetorical_device {:evidence "The phrase \'hopes were dashed\' appeals to the
    #      emotion of disappointment or loss."}  "pathos" .
    # :Sentence_648a27fc-ef20 :has_semantic :Event_df3d3390-d6bf .
    # :Event_df3d3390-d6bf a :EmotionalResponse ; :text "hopes" .
    # :Sentence_648a27fc-ef20 :has_semantic :Event_c2ccb42c-c372 .
    # :Event_c2ccb42c-c372 a :End ; :text "dashed" .
    # :Event_c2ccb42c-c372 :has_affected_entity :John .


def test_first_person():
    sent_dicts, quotations, quotations_dict = parse_narrative(text_first_person)
    success, index, graph_ttl = create_graph(quotations_dict, sent_dicts)
    ttl_str = str(graph_ttl)
    assert ':sentence_person 1 ; :sentiment "negative' in ttl_str
    assert ':tense "past' in ttl_str
    assert ':negated true' in ttl_str
    assert 'a :ReadinessAndAbility' in ttl_str
    assert ':has_active_entity [ :text "I" ; a :Person' in ttl_str
    # Output Turtle:
    # :Sentence_be21a070-f25f a :Sentence ; :offset 1 .
    # :Sentence_be21a070-f25f :text "I was not ready to leave." .
    # :Sentence_be21a070-f25f :sentence_person 1 ; :sentiment "negative".
    # :Sentence_be21a070-f25f :voice "active" ; :tense "past" ; :summary "Unwillingness to leave." .
    # :Sentence_be21a070-f25f :grade_level 3 .
    # :Sentence_be21a070-f25f :has_semantic {:negated true} :Event_b1a11e0d-0a0a .
    # :Event_b1a11e0d-0a0a a :ReadinessAndAbility ; :text "ready to leave" .
    # :Event_b1a11e0d-0a0a :has_active_entity [ :text "I" ; a :Person ] .


def test_pobj_semantics():
    sent_dicts, quotations, quotations_dict = parse_narrative(text_pobj_semantics)
    success, index, graph_ttl = create_graph(quotations_dict, sent_dicts)
    ttl_str = str(graph_ttl)
    assert "ethos" in ttl_str
    assert 'a :Avoidance ; :text "escaped' in ttl_str
    assert ':has_active_entity [ :text "robber" ; a :Person' in ttl_str
    assert 'a :Affiliation' in ttl_str
    assert 'a :AggressiveCriminalOrHostileAct' in ttl_str
    assert ' :affiliated_with [ :text "local police' in ttl_str or \
        ':has_active_entity [ :text "local police' in ttl_str
    # Output Turtle:
    # :Sentence_094d9010-e069 a :Sentence ; :offset 1 .
    # :Sentence_094d9010-e069 :text "The robber escaped with the aid of the local police." .
    # :Sentence_094d9010-e069 :sentence_person 3 ; :sentiment "negative".
    # :Sentence_094d9010-e069 :voice "active" ; :tense "past" ; :summary "Robber fled with police help" .
    # :Sentence_094d9010-e069 :grade_level 5 .
    # :Sentence_094d9010-e069 :rhetorical_device {:evidence "Reference to authority figures (local police)
    #       to justify a statement."}  "ethos" .
    # :Sentence_094d9010-e069 :rhetorical_device {:evidence "Use of \'loaded language\' implying collusion or
    #       incompetence on the part of the police."}  "loaded language" .
    # :Sentence_094d9010-e069 :has_semantic  :Event_4c433bb0-e23e .
    # :Event_4c433bb0-e23e a :Avoidance ; :text "escaped" .
    # :Event_4c433bb0-e23e :has_active_entity [ :text "robber" ; a :Person ] .
    # :Sentence_094d9010-e069 :has_semantic  :Event_81fcdf08-22aa .
    # :Event_81fcdf08-22aa a :Affiliation ; :text "aid" .
    # :Event_81fcdf08-22aa :has_described_entity [ :text "aid" ; a :Affiliation ] .
    # :Event_81fcdf08-22aa :has_active_entity [ :text "local police" ; a :GovernmentalEntity ] .
    # :Sentence_094d9010-e069 :has_semantic  :Event_0286bb74-d855 .
    # :Event_0286bb74-d855 a :AggressiveCriminalOrHostileAct ; :text "robber" .
    # :Event_0286bb74-d855 :has_active_entity [ :text "robber" ; a :Person ] .


def test_multiple_subjects():
    sent_dicts, quotations, quotations_dict = parse_narrative(text_multiple_subjects)
    success, index, graph_ttl = create_graph(quotations_dict, sent_dicts)
    ttl_str = str(graph_ttl)
    assert 'a :DisagreementAndDispute ; :text "difference of opinion' in ttl_str
    assert ':has_active_entity :Jane' in ttl_str
    assert ':has_active_entity :John' in ttl_str
    # Output Turtle:
    # :Sentence_e432930f-45eb a :Sentence ; :offset 1 .
    # :Sentence_e432930f-45eb :text "Jane and John had a serious difference of opinion." .
    # :Jane a :Person .
    # :Jane rdfs:label "Jane" .
    # :Jane rdfs:comment "Needs disambiguation; See the web site, https://en.wikipedia.org/wiki/Jane" .
    # :Jane :gender "female" .
    # :John a :Person .
    # :John rdfs:label "John" .
    # :John rdfs:comment "Needs disambiguation; See the web site, https://en.wikipedia.org/wiki/John" .
    # :John :gender "male" .
    # :Sentence_e432930f-45eb :mentions :Jane .
    # :Sentence_e432930f-45eb :mentions :John .
    # :Sentence_e432930f-45eb :sentence_person 3 ; :sentiment "negative".
    # :Sentence_e432930f-45eb :voice "active" ; :tense "past" ; :summary "Jane, John disagreed seriously." .
    # :Sentence_e432930f-45eb :grade_level 5 .
    # :Sentence_e432930f-45eb :has_semantic  :Event_547f30e5-c59a .
    # :Event_547f30e5-c59a a :DisagreementAndDispute ; :text "difference of opinion" .
    # :Event_547f30e5-c59a :has_active_entity :Jane .
    # :Event_547f30e5-c59a :has_active_entity :John .


def test_multiple_xcomp():
    sent_dicts, quotations, quotations_dict = parse_narrative(text_multiple_xcomp)
    success, index, graph_ttl = create_graph(quotations_dict, sent_dicts)
    ttl_str = str(graph_ttl)
    assert ':has_active_entity :John' in ttl_str
    assert ' a :ArtAndEntertainmentEvent ; :text "ski' in ttl_str
    assert ' a :ArtAndEntertainmentEvent ; :text "swim' in ttl_str
    # Output Turtle:
    # :Sentence_e26947af-5429 a :Sentence ; :offset 1 .
    # :Sentence_e26947af-5429 :text "John liked to ski and to swim." .
    # :John a :Person .
    # :John rdfs:label "John" .
    # :John rdfs:comment "Needs disambiguation; See the web site, https://en.wikipedia.org/wiki/John" .
    # :John :gender "male" .
    # :Sentence_e26947af-5429 :mentions :John .
    # :Sentence_e26947af-5429 :sentence_person 3 ; :sentiment "positive".
    # :Sentence_e26947af-5429 :voice "active" ; :tense "past" ; :summary "John enjoyed skiing and swimming." .
    # :Sentence_e26947af-5429 :grade_level 3 .
    # :Sentence_e26947af-5429 :has_semantic  :Event_d9339f60-dbe6 .
    # :Event_d9339f60-dbe6 a :ArtAndEntertainmentEvent ; :text "ski" .
    # :Event_d9339f60-dbe6 :has_active_entity :John .
    # :Sentence_e26947af-5429 :has_semantic  :Event_1b288d3d-081f .
    # :Event_1b288d3d-081f a :ArtAndEntertainmentEvent ; :text "swim" .
    # :Event_1b288d3d-081f :has_active_entity :John .


def test_location_hierarchy():
    sent_dicts, quotations, quotations_dict = parse_narrative(text_location_hierarchy)
    success, index, graph_ttl = create_graph(quotations_dict, sent_dicts)
    ttl_str = str(graph_ttl)
    assert ':mentions geo:2658434' in ttl_str     # Switzerland
    assert 'imagery' in ttl_str
    assert 'a :EnvironmentAndCondition' in ttl_str
    assert ':has_location [ :text "Switzerland' in ttl_str
    # Output Turtle:
    # :Sentence_50121e94-0b6f a :Sentence ; :offset 1 .
    # :Sentence_50121e94-0b6f :text "Switzerland\'s mountains are magnificent." .
    # :Sentence_50121e94-0b6f :mentions geo:2658434 .
    # :Sentence_50121e94-0b6f :sentence_person 3 ; :sentiment "positive".
    # :Sentence_50121e94-0b6f :voice "active" ; :tense "present" ; :summary "Swiss mountains are stunning." .
    # :Sentence_50121e94-0b6f :grade_level 5 .
    # :Sentence_50121e94-0b6f :rhetorical_device {:evidence "The word \'magnificent\' is used to paint a vivid
    #       picture that emotionally engages the reader, evoking the grandeur and beauty of Switzerland\'s
    #       mountains."}  "imagery" .
    # :Sentence_50121e94-0b6f :has_semantic  :Event_9ff8f1d6-44f5 .
    # :Event_9ff8f1d6-44f5 a :EnvironmentAndCondition ; :text "magnificent" .
    # :Event_9ff8f1d6-44f5 :has_location [ :text "Switzerland\'s mountains" ; a :Location ] .


def test_weather():
    sent_dicts, quotations, quotations_dict = parse_narrative(text_weather)
    success, index, graph_ttl = create_graph(quotations_dict, sent_dicts)
    ttl_str = str(graph_ttl)
    assert ':mentions :Hurricane_Otis' in ttl_str and ':mentions :Acapulco' in ttl_str
    assert ':mentions geo:3996063' in ttl_str      # Mexico
    assert ':has_active_entity :Hurricane_Otis' in ttl_str
    assert ':has_location :Acapulco' in ttl_str
    assert 'a :EnvironmentalOrEcologicalEvent' in ttl_str
    # Output Turtle:
    # :Sentence_9ee6137b-0532 a :Sentence ; :offset 1 .
    # :Sentence_9ee6137b-0532 :text "Hurricane Otis severely damaged Acapulco, Mexico." .
    # :Hurricane_Otis a :EventAndState .
    # :Hurricane_Otis rdfs:label "Otis", "Hurricane Otis" .
    # :Hurricane_Otis rdfs:comment "From Wikipedia (wikibase_item: Q123178445): \'Hurricane Otis was a compact but
    #     very powerful tropical cyclone which made a devastating landfall in October 2023 near Acapulco as a
    #     Category 5 hurricane. ...\'" .
    # :Hurricane_Otis :external_link "https://en.wikipedia.org/wiki/Hurricane_Otis" .
    # :Acapulco a :PopulatedPlace .
    # :Acapulco rdfs:label "Acapulco de Juárez", "Acapulco", "Acapulco de Juarez" .
    # :Acapulco rdfs:comment "From Wikipedia (wikibase_item: Q81398): \'Acapulco de Ju?rez, commonly called
    #      Acapulco, Guerrero, is a city and major seaport in the state of Guerrero on the Pacific Coast of Mexico,
    #      380 kilometres (240 mi) south of Mexico City. ...\'" .
    # :Acapulco :external_link "https://en.wikipedia.org/wiki/Acapulco" .
    # :Acapulco :country_name "Mexico" .
    # geo:3996063 :has_component :Acapulco .
    # :Sentence_9ee6137b-0532 :mentions :Hurricane_Otis .
    # :Sentence_9ee6137b-0532 :mentions :Acapulco .
    # :Sentence_9ee6137b-0532 :mentions geo:3996063 .
    # :Sentence_9ee6137b-0532 :sentence_person 3 ; :sentiment "negative".
    # :Sentence_9ee6137b-0532 :tense "past" ; :summary "Hurricane Otis damaged Acapulco" .
    # :Sentence_9ee6137b-0532 :grade_level 5 .
    # :Sentence_9ee6137b-0532 :has_semantic  :Event_15696b04-e060 .
    # :Event_15696b04-e060 a :AggressiveCriminalOrHostileAct ; :text "damaged" .    # TODO: Not criminal or hostile
    # :Event_15696b04-e060 :has_active_entity :Hurricane_Otis .
    # :Event_15696b04-e060 :has_topic :Acapulco .
    # :Event_15696b04-e060 :has_location geo:3996063 .
    # :Sentence_9ee6137b-0532 :has_semantic  :Event_eda32e66-7a2c .
    # :Event_eda32e66-7a2c a :EnvironmentalOrEcologicalEvent ; :text "Hurricane" .
    # :Event_eda32e66-7a2c :has_active_entity :Hurricane_Otis .
    # :Event_eda32e66-7a2c :has_location :Acapulco .
    # :Sentence_9ee6137b-0532 :has_semantic  :Event_6afa457c-7916 .
    # :Event_6afa457c-7916 a :Change ; :text "severely" .
    # :Event_6afa457c-7916 :has_quantification [ :text "severely" ; a :Measurement ] .
    # :Event_6afa457c-7916 :has_topic :Acapulco .


def test_coref():
    sent_dicts, quotations, quotations_dict = parse_narrative(text_coref)
    success, index, graph_ttl = create_graph(quotations_dict, sent_dicts)
    ttl_str = str(graph_ttl)
    assert "repetition" in ttl_str
    assert 'a :Change ; :text "cut' in ttl_str
    assert ':has_active_entity :Heidi' in ttl_str
    assert ':negated true' in ttl_str
    assert 'a :Cognition ; :text "did not recognize' in ttl_str
    assert ':has_active_entity :Anna' in ttl_str
    assert ':has_topic :Heidi' in ttl_str
    # Output Turtle:
    # :Sentence_1d397b83-f452 a :Sentence ; :offset 1 .
    # :Sentence_1d397b83-f452 :text "Anna saw Heidi cut the roses, but she did not recognize that it was
    #          Heidi who cut the roses." .
    # :Anna a :Person .
    # :Anna rdfs:label "Anna" .
    # :Anna rdfs:comment "Needs disambiguation; See the web site, https://en.wikipedia.org/wiki/Anna" .
    # :Anna :gender "female" .
    # :Heidi a :Person .
    # :Heidi rdfs:label "Heidi" .
    # :Heidi :gender "female" .
    # :Sentence_1d397b83-f452 :mentions :Anna .
    # :Sentence_1d397b83-f452 :mentions :Heidi .
    # :Sentence_1d397b83-f452 :mentions :Heidi .
    # :Sentence_1d397b83-f452 :sentence_person 3 ; :sentiment "neutral".
    # :Sentence_1d397b83-f452 :voice "active" ; :tense "past" ; :summary "Anna didn\'t recognize Heidi cutting roses." .
    # :Sentence_1d397b83-f452 :grade_level 5 .
    # :Sentence_1d397b83-f452 :rhetorical_device {:evidence "The repetition of the phrase \'cut the roses\' for
    #      emphasis."}  "repetition" .
    # :Sentence_1d397b83-f452 :has_semantic  :Event_3d091a8b-7d17 .
    # :Event_3d091a8b-7d17 a :Change ; :text "cut" .
    # :Event_3d091a8b-7d17 :has_active_entity :Heidi .
    # :Event_3d091a8b-7d17 :has_affected_entity [ :text "roses" ; a :Plant ] .
    # :Sentence_1d397b83-f452 :has_semantic {:negated true} :Event_bb5710f3-8382 .
    # :Event_bb5710f3-8382 a :Cognition ; :text "did not recognize" .
    # :Event_bb5710f3-8382 :has_active_entity :Anna .
    # :Event_bb5710f3-8382 :has_topic :Heidi .
