import pytest
from dna.create_narrative_turtle import create_graph
from dna.nlp import parse_narrative

text_clauses1 = 'While Mary exercised, John practiced guitar.'
text_clauses2 = 'George went along with the plan that Mary outlined.'
text_aux_only = 'Joe is an attorney.'
text_complex = \
    'Rep. Liz Cheney R-WY compared herself to former President Abraham Lincoln during her concession ' \
    'speech shortly after her loss to Trump-backed Republican challenger Harriet Hageman.'
text_coref = 'Joe broke his foot. He went to the doctor.'
text_xcomp = 'Mary enjoyed being with her grandfather.'
text_modal = 'Mary can visit her grandfather on Tuesdays.'
text_acomp = 'The connector is compatible with the computer.'
text_pobj = 'The connector is in compliance with the specs.'
text_acomp_pcomp = 'I got tired of running.'
text_acomp_xcomp = 'Jane is unable to tolerate smoking.'
text_idiom1 = 'George put one over on Harry.'
text_idiom2 = 'The store shut its doors.'
text_idiom3 = 'Wear and tear on the bridge caused its collapse.'
text_idiom4 = 'John stabbed Harry in the back.'
text_idiom5 = 'John was accused of breaking and entering.'
text_negation = 'Jane has no liking for broccoli.'
text_multiple_acomp1 = 'Jane is averse to broccoli and kale.'
text_multiple_acomp2 = 'Sue is an attorney and is unable to tolerate lies.'
text_auxpass = 'John got rid of the debris.'
text_npadvmod = 'John looked the other way when it came to Mary.'
text_amod_idiom = "John turned a blind eye to Mary's infidelity."
text_advmod = 'Harry put the broken vase back together.'
text_complex_verb = 'The store went out of business on Tuesday.'
text_neg_acomp_xcomp = 'Jane is unable to stomach lies.'
text_non_person_subject1 = "John's hopes were dashed."
text_non_person_subject2 = "John's dashed hopes were alive once again."
text_first_person = 'I was not ready to leave.'
text_modal_negated = 'The drill would not be ready on time.'
text_recipient = 'I bought this gift for my friend.'
text_pobj_semantics = 'The robber escaped with the aid of the local police.'
text_negated_dobj = 'Jane paid no attention to the mouse.'
text_multiple_subjects = 'Jane and John had a serious difference of opinion.'
text_multiple_xcomp = 'John liked to ski and to swim.'
text_location_hierarchy = 'Switzerland\'s mountains are magnificent.'
text_weather = "Hurricane Otis severely damaged Acapulco."


def test_clauses1():
    sent_dicts, quotations, quotations_dict = parse_narrative(text_clauses1)
    success, graph_ttl = create_graph(quotations_dict, sent_dicts)
    ttl_str = str(graph_ttl)
    # Following are shown in the output pasted below
    assert ':has_active_entity :Mary' in ttl_str and ':has_active_entity :John' in ttl_str
    assert ':has_instrument' in ttl_str
    assert ':text "guitar"' in ttl_str
    assert 'a :MusicalInstrument' in ttl_str
    assert ':text "exercised"' in ttl_str and 'a :BodilyAct' in ttl_str
    assert ':text "practiced"' in ttl_str
    assert 'a :ArtAndEntertainmentEvent' in ttl_str or 'a :Attempt' in ttl_str   # For "practiced"
    # Output Turtle:
    # :Sentence_dec17fd3-166b a :Sentence ; :offset 1 .
    # :Sentence_dec17fd3-166b :text "While Mary exercised, John practiced guitar." .
    # :Mary a :Person .
    # :Mary rdfs:label "Mary" .
    # :Mary :gender "female" .
    # :John a :Person .
    # :John rdfs:label "John" .
    # :John :gender "male" .
    # :Sentence_dec17fd3-166b :mentions :Mary .
    # :Sentence_dec17fd3-166b :mentions :John .
    # :Sentence_dec17fd3-166b :sentence_person 3 ; :sentiment "neutral".
    # :Sentence_dec17fd3-166b :voice "active" ; :tense "past" ; :summary "Mary exercised, John practiced guitar" .
    # :Sentence_dec17fd3-166b :grade_level 2 .
    # :Sentence_dec17fd3-166b :has_semantic :Event_625d4632-f165 .
    # :Event_625d4632-f165 :text "exercised" ; a :BodilyAct .
    # :Event_625d4632-f165 :has_active_entity :Mary .
    # :Sentence_dec17fd3-166b :has_semantic :Event_ecb026db-806e .
    # :Event_ecb026db-806e :text "practiced" ; a :Attempt .
    # :Event_ecb026db-806e :has_active_entity :John .
    # :Event_ecb026db-806e :has_instrument [ :text "guitar" ; a :MusicalInstrument ] .']


def test_clauses2():
    sent_dicts, quotations, quotations_dict = parse_narrative(text_clauses2)
    success, graph_ttl = create_graph(quotations_dict, sent_dicts)
    ttl_str = str(graph_ttl)
    # Following are shown in the output pasted below
    assert ':has_active_entity :Mary' in ttl_str and ':has_active_entity :George' in ttl_str
    assert ':has_topic [ :text "plan' in ttl_str
    assert ttl_str.count(':has_topic [ :text "plan') == 2
    assert ':text "went along"' in ttl_str and ':text "outlined"' in ttl_str
    assert 'a :Agreement' in ttl_str                    # went along with
    assert 'a :CommunicationAndSpeechAct' in ttl_str    # outlined
    assert ':text "plan" ; a :Process' in ttl_str
    # Output Turtle:
    # :Sentence_07fae146-3b85 a :Sentence ; :offset 1 .
    # :Sentence_07fae146-3b85 :text "George went along with the plan that Mary outlined." .
    # :George a :Person .
    # :George rdfs:label "George" .
    # :George :gender "male" .
    # :Mary a :Person .
    # :Mary rdfs:label "Mary" .
    # :Mary :gender "female" .
    # :Sentence_07fae146-3b85 :mentions :George .
    # :Sentence_07fae146-3b85 :mentions :Mary .
    # :Sentence_07fae146-3b85 :sentence_person 3 ; :sentiment "neutral".
    # :Sentence_07fae146-3b85 :voice "active" ; :tense "past" ; :summary "George agreed to Mary\'s plan." .
    # :Sentence_07fae146-3b85 :grade_level 5 .
    # :Sentence_07fae146-3b85 :has_semantic :Event_c8e33c62-56d6 .
    # :Event_c8e33c62-56d6 :text "went along" ; a :Agreement .
    # :Event_c8e33c62-56d6 :has_active_entity :George .
    # :Event_c8e33c62-56d6 :has_topic [ :text "plan" ; a :Process ] .
    # :Sentence_07fae146-3b85 :has_semantic :Event_021bef23-c06c .
    # :Event_021bef23-c06c :text "outlined" ; a :CommunicationAndSpeechAct .
    # :Event_021bef23-c06c :has_active_entity :Mary .
    # :Event_021bef23-c06c :has_topic [ :text "plan" ; a :Process ] .


def test_aux_only():
    sent_dicts, quotations, quotations_dict = parse_narrative(text_aux_only)
    success, graph_ttl = create_graph(quotations_dict, sent_dicts)
    ttl_str = str(graph_ttl)
    # Following are shown in the output pasted below
    assert ':has_described_entity :Joe' in ttl_str
    assert ':has_described_entity [ :text "a conservative"' in ttl_str
    assert 'a :EnvironmentAndCondition' in ttl_str     # is
    # Output Turtle:
    # :Sentence_63faf270-ae1d a :Sentence ; :offset 1 .
    # :Sentence_63faf270-ae1d :text "Joe is a conservative." .
    # :Joe a :Person .
    # :Joe rdfs:label "Joe" .
    # :Joe :gender "male" .
    # :Sentence_63faf270-ae1d :mentions :Joe .
    # :Sentence_63faf270-ae1d :sentence_person 3 ; :sentiment "neutral".
    # :Sentence_63faf270-ae1d :voice "active" ; :tense "present" ; :summary "Joe is a conservative." .
    # :Sentence_63faf270-ae1d :grade_level 5 .
    # :Sentence_63faf270-ae1d :has_semantic :Event_529d775e-64e8 .
    # :Event_529d775e-64e8 :text "is" ; a :EnvironmentAndCondition .
    # :Event_529d775e-64e8 :has_described_entity :Joe .
    # :Event_529d775e-64e8 :has_described_entity [ :text "a conservative" ; a :PoliticalGroup ] .']


def test_complex():
    sent_dicts, quotations, quotations_dict = parse_narrative(text_complex)
    success, graph_ttl = create_graph(quotations_dict, sent_dicts)
    ttl_str = str(graph_ttl)
    assert ':Harriet_Hageman' in ttl_str and ':Liz_Cheney' in ttl_str and ':Abraham_Lincoln' in ttl_str
    # Following are shown in the output pasted below
    assert ':during :concession_speech_' in ttl_str
    assert 'a :CommunicationAndSpeechAct' in ttl_str        # Concession speech
    assert 'a :AssessmentAndCharacterization' in ttl_str    # Compared
    assert ':has_active_agent :Liz_Cheney' in ttl_str and ':has_affected_agent :Liz_Cheney' in ttl_str
    assert ':has_topic :Abraham_Lincoln' in ttl_str
    # Output:
    # :Sentence_a1c01322-742e a :Sentence ; :offset 1 .
    # :Sentence_a1c01322-742e :text "Rep. Liz Cheney R-WY compared herself to former President Abraham Lincoln
    #        during her concession speech shortly after her loss to Trump-backed Republican challenger
    #        Harriet Hageman." .
    # :Cheneys a :Person, :Collection ; rdfs:label "Cheneys" ; :role "family" .
    # :Liz_Cheney a :Person ; :gender "female" .
    # :Liz_Cheney rdfs:label "Elizabeth Lynne Cheney", "Elizabeth Lynne Cheney Perry", "Elizabeth Lynne Perry",
    #        "Liz Cheney", "Elizabeth Cheney", "Liz", "Cheney" .
    # :Liz_Cheney rdfs:comment "From Wikipedia (wikibase_item: Q5362573): \'Elizabeth Lynne Cheney is an American
    #        attorney and politician. ... As of March 2023, she is a professor of practice at the University of
    #        Virginia Center for Politics.\'" ." .
    # :Liz_Cheney :external_link "https://en.wikipedia.org/wiki/Liz_Cheney" .
    # :WY a :PopulatedPlace, :AdministrativeDivision .
    # :WY rdfs:label "WY", "Wyoming" .
    # :WY rdfs:comment "From Wikipedia (wikibase_item: Q1214): \'...\'" .
    # :WY :external_link "https://en.wikipedia.org/wiki/Wyoming" .
    # :WY :admin_level 1 ; :country_name "United States" .
    # geo:6252001 :has_component :WY .
    # :Lincolns a :Person, :Collection ; rdfs:label "Lincolns" ; :role "family" .
    # :Abraham_Lincoln a :Person ; :gender "male" .
    # :Abraham_Lincoln rdfs:label "Lincoln", "Honest Abe", "A. Lincoln", "Abe Lincoln", "President Lincoln",
    #         "Uncle Abe", "Abraham Lincoln", "Abraham" .
    # :Abraham_Lincoln rdfs:comment "From Wikipedia (wikibase_item: Q91): \'...\'" .
    # :Abraham_Lincoln :external_link "https://en.wikipedia.org/wiki/Abraham_Lincoln" .
    # :Trump a :Person ; rdfs:label "Trump" .
    # :Trump rdfs:comment "Needs disambiguation; See the web site, https://en.wikipedia.org/wiki/Trump" .
    # :Republican a :Person ; rdfs:label "Republican" .
    # :Republican rdfs:comment "Needs disambiguation; See the web site, https://en.wikipedia.org/wiki/Republican" .
    # :Hagemans a :Person, :Collection ; rdfs:label "Hagemans" ; :role "family" .
    # :Harriet_Hageman a :Person ; :gender "female" .
    # :Harriet_Hageman rdfs:label "Harriet M. Hageman", "Harriet Hageman", "Harriet", "Hageman" .
    # :Harriet_Hageman rdfs:comment "From Wikipedia (wikibase_item: Q110815967): \'
    #          Harriet Maxine Hageman (born October 18, 1962) is an American politician and attorney serving as
    #          the U.S. representative for Wyoming's at-large congressional district since 2023. She is a member
    #          of the Republican Party.\'" .
    # :Harriet_Hageman :external_link "https://en.wikipedia.org/wiki/Harriet_Hageman" .
    # :Sentence_a1c01322-742e :mentions :Liz_Cheney .
    # :Sentence_a1c01322-742e :mentions :WY .
    # :Sentence_a1c01322-742e :mentions :Abraham_Lincoln .
    # :Sentence_a1c01322-742e :mentions :Trump .
    # :Sentence_a1c01322-742e :mentions :Republican .
    # :Sentence_a1c01322-742e :mentions :Harriet_Hageman .
    # :Sentence_a1c01322-742e :sentence_person 3 ; :sentiment "neutral".
    # :Sentence_a1c01322-742e :voice "active" ; :tense "past" ;
    #        :summary "Cheney compared herself to Lincoln after election loss." .
    # :Sentence_a1c01322-742e :grade_level 12 .
    # :Sentence_a1c01322-742e :rhetorical_device {:evidence "The speaker, Liz Cheney, refers to Abraham Lincoln,
    #        a historical figure, to symbolize her own political stance and situation."}  "allusion" .
    # :Sentence_a1c01322-742e :rhetorical_device {:evidence "The speaker refers to Abraham Lincoln, an authority
    #        figure in American history, to justify her own political stance and actions."}  "ethos" .
    # :Sentence_a1c01322-742e :rhetorical_device {:evidence "The speaker invokes the remembrance of
    #        Abraham Lincoln, a significant figure in American history, to engage the audience."}  "kairos" .
    # :Sentence_a1c01322-742e :has_semantic :Event_88476522-bace .
    # :Event_88476522-bace :text "compared" ; a :Cognition .
    # :Event_88476522-bace :has_active_entity [ :text "Rep. Liz Cheney R-WY" ; a :Person ] .
    # :Event_88476522-bace :has_affected_entity [ :text "former President Abraham Lincoln" ; a :Person ] .
    # :Sentence_a1c01322-742e :has_semantic :Event_aca91327-5bf1 .
    # :Event_aca91327-5bf1 :text "loss" ; a :WinAndLoss .
    # :Event_aca91327-5bf1 :has_affected_entity [ :text "Rep. Liz Cheney R-WY" ; a :Person ] .
    # :Event_aca91327-5bf1 :has_active_entity [ :text "Trump-backed Republican challenger Harriet Hageman" ;
    #        a :Person ] .']


def test_coref():
    sent_dicts, quotations, quotations_dict = parse_narrative(text_coref)
    success, graph_ttl = create_graph(quotations_dict, sent_dicts)
    ttl_str = str(graph_ttl)
    assert ':has_active_agent :Mary' in ttl_str and ':has_active_agent :grandfather' in ttl_str
    assert 'a :DelightAndHappiness' in ttl_str and 'a :MeetingAndEncounter' in ttl_str
    # Output:


def test_text4():
    sent_dicts, quotations, quotations_dict = parse_narrative(text4)
    success, graph_ttl = create_graph(quotations_dict, sent_dicts)
    ttl_str = str(graph_ttl)
    assert ':has_active_agent :Mary' in ttl_str and ':has_active_agent :grandfather' in ttl_str
    assert 'a :DelightAndHappiness' in ttl_str and 'a :MeetingAndEncounter' in ttl_str
    # Output:
    # :Chunk_e9e14a01-40dd :text "Mary enjoyed being with her grandfather" .
    # :grandfather_0db0f775_6d96 :gender "Male" .
    # :grandfather_0db0f775_6d96 a :Person .
    # :grandfather_0db0f775_6d96 rdfs:label "grandfather" .
    # :Event_ecf200ec-83d4 :has_active_agent :grandfather_0db0f775_6d96 .
    # :Event_ecf200ec-83d4 a :MeetingAndEncounter .
    # :Event_ecf200ec-83d4 a :DelightAndHappiness .
    # :Event_ecf200ec-83d4 :has_active_agent :Mary .
    # :Event_ecf200ec-83d4 rdfs:label "Mary enjoyed to be / being with her grandfather" .
    # :Chunk_e9e14a01-40dd :describes :Event_ecf200ec-83d4 .


def test_text5():
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(text5)
    success, graph_ttl = create_graph(quotations_dict, sent_dicts, family_dict)
    ttl_str = str(graph_ttl)
    assert ':has_active_agent :Mary' in ttl_str and ':has_active_agent :grandfather' in ttl_str
    assert 'a :OpportunityAndPossibility' in ttl_str      # 'can'
    assert 'a :MeetingAndEncounter' in ttl_str
    # Output:
    # :Event_df51d93b-f5d5 :has_time :PiT_DayTuesday .
    # TODO: Repeating sequence, 'on Tuesdays'
    # :grandfather_8e115e79_d60f :gender "Male" .
    # :grandfather_8e115e79_d60f a :Person .
    # :grandfather_8e115e79_d60f rdfs:label "grandfather" .
    # :Event_df51d93b-f5d5 :has_active_agent :grandfather_8e115e79_d60f .
    # :Event_df51d93b-f5d5 a dna:OpportunityAndPossibility .
    # :Event_df51d93b-f5d5 a :MeetingAndEncounter .
    # :Event_df51d93b-f5d5 :has_active_agent :Mary .
    # :Event_df51d93b-f5d5 rdfs:label "Mary can be with her grandfather" .
    # :Chunk_e9f09b9c-ac86 :describes :Event_df51d93b-f5d5 .
