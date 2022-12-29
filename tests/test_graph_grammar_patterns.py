from dna.create_narrative_turtle import create_graph
from dna.nlp import parse_narrative

text1 = 'While Mary exercised, John practiced guitar.'            # clauses
text2 = 'George went along with the plan that Mary outlined.'     # clauses, multiple possibilities + verb, prt, prep
text3 = 'Rep. Liz Cheney R-WY compared herself to former President Abraham Lincoln during her concession speech ' \
        'shortly after her loss to Trump-backed Republican challenger Harriet Hageman.'    # bug
text4 = 'Mary enjoyed being with her grandfather.'                # verb, xcomp, prep
text5 = 'Mary can be with her grandfather on Tuesdays.'           # possibility
text6 = 'I got tired of running.'                                 # verb, acomp, prep, pcomp
text7 = 'Jane is unable to tolerate smoking.'                     # verb, acomp, xcomp, obj
text8 = 'George put one over on Harry.'                           # verb, card obj, prt, prep
text9 = 'Jane has no liking for broccoli.'                        # verb, neg obj
text10 = 'The connector is compatible with the computer.'         # verb, acomp
text11 = 'Jane is averse to broccoli.'                            # verb, acomp
text12 = 'Sue is partial to pumpkin pie.'                         # verb, acomp
text13 = 'Sue got hold of a bargain.'                             # verb, obj, prep
text14 = 'John got rid of the debris.'                            # verb, auxpass, prep
text15 = 'John looked the other way when it came to Mary.'        # verb, npadvmod, amod
text16 = "John turned a blind eye to Mary's infidelity."          # verb, obj, amod
text17 = 'Harry put the broken vase back together.'               # verb, advmod, advmod
text18 = 'Mary took care of the problem.'                         # multiple possibilities
text19 = 'The connector is in compliance with the specs.'         # verb, prep + pobj, prep
text20 = 'The store went out of business on Tuesday.'             # verb, prep + prep
text21 = 'The store shut its doors.'                              # verb, plural obj
text22 = 'Jane is unable to stomach lies.'                        # verb, acomp, xcomp
text23 = "John's hopes were dashed."                              # bug
text24 = "John's dashed hopes were alive once again."             # bug, adjective + noun
text25 = 'Wear and tear on the bridge caused its collapse.'       # and, cause
text26 = 'I was not ready to leave.'                              # verb, neg + acomp
text27 = 'The drill would not be ready on time.'                  # bug
text28 = 'The CEO put up a smoke screen to distract the press.'   # verb, prt, obj + compound
text29 = 'John stabbed Harry in the back.'                        # verb, prep + pobj
text30 = 'My peace of mind was in danger.'                        # noun + prep + noun
text31 = 'She holds her sister in esteem.'                        # verb, prep + noun
text32 = 'I bought this gift for my friend.'                      # for => has_recipient
text33 = 'The robber escaped with the aid of the local police.'   # bug
text34 = 'Jane paid no attention to the mouse.'                   # verb, neg + noun
# TODO: EnvAndCondition always has_holder
# TODO: NORP adjective for noun => affiliation
# TODO: Loc adjective for noun => has_component
# TODO: Possessive => context


def test_text1():
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(text1)
    success, graph_ttl = create_graph(sent_dicts, family_dict, '', False, False)
    ttl_str = str(graph_ttl)
    # Following are shown in the output pasted below
    assert ':has_active_agent :Mary' in ttl_str and ':has_active_agent :John' in ttl_str
    assert ':has_topic :guitar_' in ttl_str
    assert ':has_topic :guitar_' in ttl_str
    assert 'a :MusicalInstrument' in ttl_str
    assert 'a :BodyMovement, :HealthAndDiseaseRelated' in ttl_str      # Exercised
    assert 'a :LearningAndEducation' in ttl_str
    # Output:
    # :Chunk_9b821aee-5e44 a :Chunk ; :offset 1 .
    # :Chunk_9b821aee-5e44 :text "Mary exercised" .
    # :Chunk_9b821aee-5e44 :describes :Event_099a1378-81ba .
    # :Event_099a1378-81ba a :BodyMovement, :HealthAndDiseaseRelated .
    # :Event_099a1378-81ba :has_active_agent :Mary .
    # :Event_099a1378-81ba rdfs:label "Mary exercised" .
    # :Chunk_3071bb08-3279 a :Chunk ; :offset 2 .
    # :Chunk_3071bb08-3279 :text "John practiced guitar" .
    # :Chunk_3071bb08-3279 :describes :Event_cb52a553-e0c2 .
    # :guitar_e801b432_8ec6 a :MusicalInstrument .
    # :guitar_e801b432_8ec6 rdfs:label "guitar" .
    # :Event_cb52a553-e0c2 a :LearningAndEducation .
    # :Event_cb52a553-e0c2 :has_active_agent :John .
    # :Event_cb52a553-e0c2 :has_topic :guitar_e801b432_8ec6 .
    # :Event_cb52a553-e0c2 rdfs:label "John practiced guitar" .


def test_text2():
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(text2)
    success, graph_ttl = create_graph(sent_dicts, family_dict, '', False, False)
    ttl_str = str(graph_ttl)
    # Following are shown in the output pasted below
    assert ':has_active_agent :Mary' in ttl_str and ':has_active_agent :George' in ttl_str
    assert ':has_topic :plan_' in ttl_str
    assert ttl_str.count(':has_topic :plan_') == 2
    assert 'a :Agreement' in ttl_str                  # Go along with
    assert 'a :AssertionAndDeclaration' in ttl_str    # Outline
    # Output:
    # :Chunk_1393cbd6-7367 a :Chunk ; :offset 1 .
    # :Chunk_1393cbd6-7367 :text "Mary outlined the plan" .
    # :plan_0cfadb73_6603 a :IntentionAndGoal .
    # :plan_0cfadb73_6603 rdfs:label "plan" .
    # :Event_639a8db0-abd5 a :AssertionAndDeclaration .
    # :Event_639a8db0-abd5 :has_active_agent :Mary .
    # :Event_639a8db0-abd5 :has_topic :plan_0cfadb73_6603 .
    # :Event_639a8db0-abd5 rdfs:label "Mary outlined plan" .
    # :Chunk_1393cbd6-7367 :describes :Event_639a8db0-abd5 .
    # :Sentence_d90d21a9-fa47 :has_component :Chunk_10542a5e-2636 .
    # :Chunk_10542a5e-2636 a :Chunk ; :offset 2 .
    # :Chunk_10542a5e-2636 :text "George went along with the plan" .
    # :Event_6ec1af2c-c72e a :Agreement .
    # :Event_6ec1af2c-c72e :has_active_agent :George .
    # :Event_6ec1af2c-c72e :has_topic :plan_0cfadb73_6603 .
    # :Event_6ec1af2c-c72e rdfs:label "George went along with plan" .
    # :Chunk_10542a5e-2636 :describes :Event_6ec1af2c-c72e .


def test_text3():
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(text3)
    success, graph_ttl = create_graph(sent_dicts, family_dict, '', False, False)
    ttl_str = str(graph_ttl)
    assert ':Harriet_Hageman' in ttl_str and ':Liz_Cheney' in ttl_str and ':Abraham_Lincoln' in ttl_str
    # Following are shown in the output pasted below
    assert ':during :concession_speech_' in ttl_str
    assert 'a :CommunicationAndSpeechAct' in ttl_str        # Concession speech
    assert 'a :AssessmentAndCharacterization' in ttl_str    # Compared
    assert ':has_active_agent :Liz_Cheney' in ttl_str and ':has_affected_agent :Liz_Cheney' in ttl_str
    assert ':has_topic :Abraham_Lincoln' in ttl_str
    # Output:
    # :Chunk_e147526b-5c3f :text "Rep. Liz Cheney R-WY compared herself to former President Abraham Lincoln during
    #                             her concession speech shortly after her loss to Trump-backed Republican challenger
    #                             Harriet Hageman" .
    # :Event_ca7f6893-08fb :has_topic :Abraham_Lincoln .
    # :concession_speech_shortly_after_loss_790b8704_435d a :CommunicationAndSpeechAct .
    # :concession_speech_shortly_after_loss_790b8704_435d rdfs:label "concession speech shortly after loss" .
    # :Event_ca7f6893-08fb :during :concession_speech_shortly_after_loss_790b8704_435d .
    # :Event_ca7f6893-08fb a :AssessmentAndCharacterization .
    # :Event_ca7f6893-08fb :has_active_agent :Liz_Cheney .
    # :Event_ca7f6893-08fb :has_affected_agent :Liz_Cheney .
    # :Event_ca7f6893-08fb rdfs:label "Liz Cheney compared Liz Cheney to President Abraham Lincoln during her
    #                                  concession speech shortly after her loss" .
    # :Chunk_e147526b-5c3f :describes :Event_ca7f6893-08fb .


def test_text4():
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(text4)
    success, graph_ttl = create_graph(sent_dicts, family_dict, '', False, False)
    ttl_str = str(graph_ttl)
    print(ttl_str)
    assert False
    # TODO: Define assertions


def test_text5():
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(text5)
    success, graph_ttl = create_graph(sent_dicts, family_dict, '', False, False)
    ttl_str = str(graph_ttl)
    print(ttl_str)
    # TODO: Define assertions


def test_text6():
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(text6)
    success, graph_ttl = create_graph(sent_dicts, family_dict, '', False, False)
    ttl_str = str(graph_ttl)
    print(ttl_str)
    # TODO: Define assertions


def test_text7():
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(text7)
    success, graph_ttl = create_graph(sent_dicts, family_dict, '', False, False)
    ttl_str = str(graph_ttl)
    print(ttl_str)
    # TODO: Define assertions


def test_text8():
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(text8)
    success, graph_ttl = create_graph(sent_dicts, family_dict, '', False, False)
    ttl_str = str(graph_ttl)
    print(ttl_str)
    # TODO: Define assertions


def test_text9():
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(text9)
    success, graph_ttl = create_graph(sent_dicts, family_dict, '', False, False)
    ttl_str = str(graph_ttl)
    print(ttl_str)
    # TODO: Define assertions


def test_text10():
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(text10)
    success, graph_ttl = create_graph(sent_dicts, family_dict, '', False, False)
    ttl_str = str(graph_ttl)
    print(ttl_str)
    # TODO: Define assertions


def test_text11():
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(text11)
    success, graph_ttl = create_graph(sent_dicts, family_dict, '', False, False)
    ttl_str = str(graph_ttl)
    print(ttl_str)
    # TODO: Define assertions


def test_text12():
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(text12)
    success, graph_ttl = create_graph(sent_dicts, family_dict, '', False, False)
    ttl_str = str(graph_ttl)
    print(ttl_str)
    # TODO: Define assertions


def test_text13():
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(text13)
    success, graph_ttl = create_graph(sent_dicts, family_dict, '', False, False)
    ttl_str = str(graph_ttl)
    print(ttl_str)
    # TODO: Define assertions


def test_text14():
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(text14)
    success, graph_ttl = create_graph(sent_dicts, family_dict, '', False, False)
    ttl_str = str(graph_ttl)
    print(ttl_str)
    # TODO: Define assertions


def test_text15():
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(text15)
    success, graph_ttl = create_graph(sent_dicts, family_dict, '', False, False)
    ttl_str = str(graph_ttl)
    print(ttl_str)
    # TODO: Define assertions


def test_text16():
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(text16)
    success, graph_ttl = create_graph(sent_dicts, family_dict, '', False, False)
    ttl_str = str(graph_ttl)
    print(ttl_str)
    # TODO: Define assertions


def test_text17():
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(text17)
    success, graph_ttl = create_graph(sent_dicts, family_dict, '', False, False)
    ttl_str = str(graph_ttl)
    print(ttl_str)
    # TODO: Define assertions


def test_text18():
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(text18)
    success, graph_ttl = create_graph(sent_dicts, family_dict, '', False, False)
    ttl_str = str(graph_ttl)
    print(ttl_str)
    # TODO: Define assertions


def test_text19():
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(text19)
    success, graph_ttl = create_graph(sent_dicts, family_dict, '', False, False)
    ttl_str = str(graph_ttl)
    print(ttl_str)
    # TODO: Define assertions


def test_text20():
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(text20)
    success, graph_ttl = create_graph(sent_dicts, family_dict, '', False, False)
    ttl_str = str(graph_ttl)
    print(ttl_str)
    # TODO: Define assertions


def test_text21():
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(text21)
    success, graph_ttl = create_graph(sent_dicts, family_dict, '', False, False)
    ttl_str = str(graph_ttl)
    print(ttl_str)
    # TODO: Define assertions


def test_text22():
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(text22)
    success, graph_ttl = create_graph(sent_dicts, family_dict, '', False, False)
    ttl_str = str(graph_ttl)
    print(ttl_str)
    # TODO: Define assertions


def test_text23():
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(text23)
    success, graph_ttl = create_graph(sent_dicts, family_dict, '', False, False)
    ttl_str = str(graph_ttl)
    print(ttl_str)
    # TODO: Define assertions


def test_text24():
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(text24)
    success, graph_ttl = create_graph(sent_dicts, family_dict, '', False, False)
    ttl_str = str(graph_ttl)
    print(ttl_str)
    # TODO: Define assertions


def test_text25():
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(text25)
    success, graph_ttl = create_graph(sent_dicts, family_dict, '', False, False)
    ttl_str = str(graph_ttl)
    print(ttl_str)
    # TODO: Define assertions


def test_text26():
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(text26)
    success, graph_ttl = create_graph(sent_dicts, family_dict, '', False, False)
    ttl_str = str(graph_ttl)
    print(ttl_str)
    # TODO: Define assertions


def test_text27():
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(text27)
    success, graph_ttl = create_graph(sent_dicts, family_dict, '', False, False)
    ttl_str = str(graph_ttl)
    print(ttl_str)
    # TODO: Define assertions


def test_text28():
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(text28)
    success, graph_ttl = create_graph(sent_dicts, family_dict, '', False, False)
    ttl_str = str(graph_ttl)
    print(ttl_str)
    # TODO: Define assertions


def test_text29():
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(text29)
    success, graph_ttl = create_graph(sent_dicts, family_dict, '', False, False)
    ttl_str = str(graph_ttl)
    print(ttl_str)
    # TODO: Define assertions


def test_text30():
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(text30)
    success, graph_ttl = create_graph(sent_dicts, family_dict, '', False, False)
    ttl_str = str(graph_ttl)
    print(ttl_str)
    # TODO: Define assertions


def test_text31():
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(text31)
    success, graph_ttl = create_graph(sent_dicts, family_dict, '', False, False)
    ttl_str = str(graph_ttl)
    print(ttl_str)
    # TODO: Define assertions


def test_text32():
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(text32)
    success, graph_ttl = create_graph(sent_dicts, family_dict, '', False, False)
    ttl_str = str(graph_ttl)
    print(ttl_str)
    # TODO: Define assertions


def test_text33():
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(text33)
    success, graph_ttl = create_graph(sent_dicts, family_dict, '', False, False)
    ttl_str = str(graph_ttl)
    print(ttl_str)
    # TODO: Define assertions


def test_text34():
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(text34)
    success, graph_ttl = create_graph(sent_dicts, family_dict, '', False, False)
    ttl_str = str(graph_ttl)
    print(ttl_str)
    # TODO: Define assertions
