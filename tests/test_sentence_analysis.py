import pytest
from dna.create_narrative_turtle import create_graph
from dna.nlp import parse_narrative

text_clauses1 = 'While Mary exercised, John practiced guitar.'
text_clauses2 = 'George went along with the plan that Mary outlined.'
text_aux_only = 'Joe is an attorney.'
text_affiliation = 'Joe is a member of the Mayberry Book Club.'
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

# Note that it is unlikely that all tests will complete successfully since event semantics can be
# interpreted/reported in multiple ways
# 75% of tests should pass


def test_clauses1():
    sent_dicts, quotations, quotations_dict = parse_narrative(text_clauses1)
    success, graph_ttl = create_graph(quotations_dict, sent_dicts)
    # Following are shown in the output pasted below
    assert ':has_active_entity :Mary' in ttl_str and ':has_active_entity :John' in ttl_str
    assert ':has_instrument' in ttl_str
    assert ':text "guitar' in ttl_str
    assert 'a :MusicalInstrument' in ttl_str
    assert ':text "exercised' in ttl_str and 'a :BodilyAct' in ttl_str
    assert ':text "practiced' in ttl_str
    assert 'a :ArtAndEntertainmentEvent' in ttl_str or 'a :Attempt' in ttl_str   # practiced
    # Output Turtle:
    # :Sentence_c567e3dc-fd80 a :Sentence ; :offset 1 .
    # :Sentence_c567e3dc-fd80 :text "While Mary exercised, John practiced guitar." .
    # :Mary a :Person .
    # :Mary rdfs:label "Mary" .
    # :Mary rdfs:comment "Needs disambiguation; See the web site, https://en.wikipedia.org/wiki/Mary" .
    # :Mary :gender "female" .
    # :John a :Person .
    # :John rdfs:label "John" .
    # :John rdfs:comment "Needs disambiguation; See the web site, https://en.wikipedia.org/wiki/John" .
    # :John :gender "male" .
    # :Sentence_c567e3dc-fd80 :mentions :Mary .
    # :Sentence_c567e3dc-fd80 :mentions :John .
    # :Sentence_c567e3dc-fd80 :sentence_person 3 ; :sentiment "neutral".
    # :Sentence_c567e3dc-fd80 :voice "active" ; :tense "past" ; :summary "Mary exercised, John played guitar." .
    # :Sentence_c567e3dc-fd80 :grade_level 3 .
    # :Sentence_c567e3dc-fd80 :has_semantic :Event_882740d1-d136 .
    # :Event_882740d1-d136 a :BodilyAct ; :text "exercised" .
    # :Event_882740d1-d136 :has_active_entity :Mary .
    # :Sentence_c567e3dc-fd80 :has_semantic :Event_5693c8a2-c003 .
    # :Event_5693c8a2-c003 a :ArtAndEntertainmentEvent ; :text "practiced guitar" .   # Could also be :Attempt
    # :Event_5693c8a2-c003 :has_active_entity :John .
    # :Event_5693c8a2-c003 :has_instrument [ :text "guitar" ; a :MusicalInstrument ] .


def test_clauses2():
    sent_dicts, quotations, quotations_dict = parse_narrative(text_clauses2)
    success, graph_ttl = create_graph(quotations_dict, sent_dicts)
    ttl_str = str(graph_ttl)
    # Following are shown in the output pasted below
    assert ':has_active_entity :Mary' in ttl_str and ':has_active_entity :George' in ttl_str
    assert ':has_topic [ :text "plan' in ttl_str
    assert ':text "went along with' in ttl_str and ':text "outlined"' in ttl_str
    assert 'a :Agreement' in ttl_str           # went along with
    assert 'a :Cognition' in ttl_str           # outlined
    assert ':text "plan" ; a :Process' in ttl_str
    # Output Turtle:
    # :Sentence_7dac42b4-9147 a :Sentence ; :offset 1 .
    # :Sentence_7dac42b4-9147 :text "George went along with the plan that Mary outlined." .
    # :George a :Person .
    # :George rdfs:label "George" .
    # :George rdfs:comment "Needs disambiguation; See the web site, https://en.wikipedia.org/wiki/George" .
    # :George :gender "male" .
    # :Mary a :Person .
    # :Mary rdfs:label "Mary" .
    # :Mary rdfs:comment "Needs disambiguation; See the web site, https://en.wikipedia.org/wiki/Mary" .
    # :Mary :gender "female" .
    # :Sentence_7dac42b4-9147 :mentions :George .
    # :Sentence_7dac42b4-9147 :mentions :Mary .
    # :Sentence_7dac42b4-9147 :sentence_person 3 ; :sentiment "neutral".
    # :Sentence_7dac42b4-9147 :voice "active" ; :tense "past" ; :summary "George followed Mary\'s plan." .
    # :Sentence_7dac42b4-9147 :grade_level 5 .
    # :Sentence_7dac42b4-9147 :has_semantic :Event_26888f2f-a3d0 .
    # :Event_26888f2f-a3d0 a :Agreement ; :text "went along with" .
    # :Event_26888f2f-a3d0 :has_active_entity :George .
    # :Event_26888f2f-a3d0 :has_topic [:text "plan" ; a :Process] .
    # :Sentence_7dac42b4-9147 :has_semantic :Event_9becfcb5-705c .
    # :Event_9becfcb5-705c a :Cognition ; :text "outlined" .
    # :Event_9becfcb5-705c :has_active_entity :Mary .
    # :Event_9becfcb5-705c :has_topic [:text "plan" ; a :Process] .


def test_aux_only():
    sent_dicts, quotations, quotations_dict = parse_narrative(text_aux_only)
    success, graph_ttl = create_graph(quotations_dict, sent_dicts)
    ttl_str = str(graph_ttl)
    # Following are shown in the output pasted below
    assert 'a :EnvironmentAndCondition' in ttl_str     # is
    assert ':has_described_entity :Joe' in ttl_str
    assert ':has_aspect [ :text "attorney' in ttl_str
    assert 'a :LineOfBusiness' in ttl_str              # attorney
    # Output Turtle:
    # :Sentence_5c116489-da1c a :Sentence ; :offset 1 .
    # :Sentence_5c116489-da1c :text "Joe is an attorney." .
    # :Joe a :Person .
    # :Joe rdfs:label "Joe" .
    # :Joe rdfs:comment "Needs disambiguation; See the web site, https://en.wikipedia.org/wiki/Joe" .
    # :Joe :gender "male" .
    # :Sentence_5c116489-da1c :mentions :Joe .
    # :Sentence_5c116489-da1c :sentence_person 3 ; :sentiment "neutral".
    # :Sentence_5c116489-da1c :voice "active" ; :tense "present" ; :summary "Joe is a lawyer" .
    # :Sentence_5c116489-da1c :grade_level 5 .
    # :Sentence_5c116489-da1c :has_semantic :Event_0dba1899-2ab9 .
    # :Event_0dba1899-2ab9 a :EnvironmentAndCondition ; :text "Joe is an attorney." .
    # :Event_0dba1899-2ab9 :has_described_entity :Joe .
    # :Event_0dba1899-2ab9 :has_aspect [:text "attorney" ; a :LineOfBusiness] .']


def test_affiliation():
    sent_dicts, quotations, quotations_dict = parse_narrative(text_affiliation)
    success, graph_ttl = create_graph(quotations_dict, sent_dicts)
    ttl_str = str(graph_ttl)
    assert 'a :Affiliation' in ttl_str
    assert ':has_active_entity :Joe' in ttl_str
    assert ':has_affected_entity :the_Mayberry' in ttl_str
    # Output Turtle:
    # :Sentence_2bbce40c-56e7 a :Sentence ; :offset 1 .
    # :Sentence_2bbce40c-56e7 :text "Joe is a member of the Mayberry Book Club." .
    # :Joe a :Person .
    # :Joe rdfs:label "Joe" .
    # :Joe rdfs:comment "Needs disambiguation; See the web site, https://en.wikipedia.org/wiki/Joe" .
    # :Joe :gender "male" .
    # :the_Mayberry_Book_Club a :Organization .
    # :the_Mayberry_Book_Club rdfs:label "the Mayberry Book Club" .
    # :Sentence_2bbce40c-56e7 :mentions :Joe .
    # :Sentence_2bbce40c-56e7 :mentions :the_Mayberry_Book_Club .
    # :Sentence_2bbce40c-56e7 :sentence_person 3 ; :sentiment "neutral".
    # :Sentence_2bbce40c-56e7 :voice "active" ; :tense "present" ; :summary "Joe joins book club" .
    # :Sentence_2bbce40c-56e7 :grade_level 3 .
    # :Sentence_2bbce40c-56e7 :has_semantic :Event_f7fa1139-8022 .
    # :Event_f7fa1139-8022 a :Affiliation ; :text "member" .
    # :Event_f7fa1139-8022 :has_active_entity :Joe .
    # :Event_f7fa1139-8022 :has_affected_entity :the_Mayberry_Book_Club .


def test_complex():
    sent_dicts, quotations, quotations_dict = parse_narrative(text_complex)
    success, graph_ttl = create_graph(quotations_dict, sent_dicts)
    ttl_str = str(graph_ttl)
    assert ':Harriet_Hageman' in ttl_str and ':Liz_Cheney' in ttl_str and ':Abraham_Lincoln' in ttl_str
    # Following are shown in the output pasted below
    assert 'a :CommunicationAndSpeechAct' in ttl_str         # concession speech
    assert 'a :Cognition' in ttl_str                         # compared
    assert ':has_active_entity :Liz_Cheney' in ttl_str       # Cheney compared herself
    assert ':has_topic :Abraham_Lincoln' in ttl_str          #    to Lincoln
    assert ':has_active_entity :Harriet_Hageman' in ttl_str  # Hageman won
    # Output:
    # :Sentence_249204c5-4e80 a :Sentence ; :offset 1 .
    # :Sentence_249204c5-4e80 :text "Rep. Liz Cheney R-WY compared herself to former President Abraham Lincoln
    #      during her concession speech shortly after her loss to Trump-backed Republican challenger Harriet Hageman." .
    # :Cheneys a :Person, :Collection ; rdfs:label "Cheneys" ; :role "family" .
    # :Liz_Cheney a :Person .
    # :Liz_Cheney rdfs:label "Elizabeth Lynne Cheney", "Elizabeth Lynne Cheney Perry", "Elizabeth Lynne Perry",
    #      "Liz Cheney", "Elizabeth Cheney", "Liz", "Cheney" .
    # :Liz_Cheney rdfs:comment "From Wikipedia (wikibase_item: Q5362573): \'Elizabeth Lynne Cheney is an American
    #      attorney and politician. ... As of March 2023, she is a professor of practice at the University of
    #      Virginia Center for Politics.\'" .
    # :Liz_Cheney :external_link "https://en.wikipedia.org/wiki/Liz_Cheney" .
    # :Liz_Cheney :gender "female" .
    # :WY a :PopulatedPlace, :AdministrativeDivision .
    # :WY rdfs:label "Wyoming", "WY" .
    # :WY rdfs:comment "From Wikipedia (wikibase_item: Q1214): \'Wyoming is a state in the Mountain West
    #       subregion of the Western United States. ...\'" .
    # :WY :external_link "https://en.wikipedia.org/wiki/Wyoming" .
    # :WY :admin_level 1 .
    # :WY :country_name "United States" .
    # geo:6252001 :has_component :WY .
    # :Lincolns a :Person, :Collection ; rdfs:label "Lincolns" ; :role "family" .
    # :Abraham_Lincoln a :Person .
    # :Abraham_Lincoln rdfs:label "Lincoln", "Honest Abe", "A. Lincoln", "Abe Lincoln", "President Lincoln",
    #       "Uncle Abe", "Abraham Lincoln", "Abraham" .
    # :Abraham_Lincoln rdfs:comment "From Wikipedia (wikibase_item: Q91): \'Abraham Lincoln was an American lawyer,
    #       politician, and statesman who served as the 16th president of the United States from 1861 until his
    #       assassination in 1865. ...\'" .
    # :Abraham_Lincoln :external_link "https://en.wikipedia.org/wiki/Abraham_Lincoln" .
    # :Abraham_Lincoln :gender "male" .
    # :Trump a :Person .
    # :Trump rdfs:label "Trump" .
    # :Trump rdfs:comment "Needs disambiguation; See the web site, https://en.wikipedia.org/wiki/Trump" .
    # :Republican a :Person ; rdfs:label "Republican" .
    # :Republican rdfs:comment "Needs disambiguation; See the web site, https://en.wikipedia.org/wiki/Republican" .
    # :Hagemans a :Person, :Collection ; rdfs:label "Hagemans" ; :role "family" .
    # :Harriet_Hageman a :Person .
    # :Harriet_Hageman rdfs:label "Harriet M. Hageman", "Harriet Hageman", "Harriet", "Hageman" .
    # :Harriet_Hageman rdfs:comment "From Wikipedia (wikibase_item: Q110815967): \'Harriet Maxine Hageman is an
    #       American politician and attorney serving as the U.S. representative for Wyoming\'s at-large
    #       congressional district since 2023. She is a member of the Republican Party.\'" .
    # :Harriet_Hageman :external_link "https://en.wikipedia.org/wiki/Harriet_Hageman" .
    # :Harriet_Hageman :gender "female" .
    # :Sentence_249204c5-4e80 :mentions :Liz_Cheney .
    # :Sentence_249204c5-4e80 :mentions :WY .
    # :Sentence_249204c5-4e80 :mentions :Abraham_Lincoln .
    # :Sentence_249204c5-4e80 :mentions :Trump .
    # :Sentence_249204c5-4e80 :mentions :Republican .
    # :Sentence_249204c5-4e80 :mentions :Harriet_Hageman .
    # :Sentence_249204c5-4e80 :sentence_person 3 ; :sentiment "negative".
    # :Sentence_249204c5-4e80 :voice "active" ; :tense "past" ;
    #       :summary "Cheney compares herself to Lincoln in defeat." .
    # :Sentence_249204c5-4e80 :grade_level 8 .
    # :Sentence_249204c5-4e80 :rhetorical_device {:evidence "Rep. Liz Cheney compared herself to former President
    #       Abraham Lincoln, which is an allusion to a historical figure known for his leadership and integrity."}
    #       "allusion" .
    # :Sentence_249204c5-4e80 :rhetorical_device {:evidence "The reference to former President Abraham Lincoln
    #       invokes ethos by drawing on the authority and respect associated with Lincoln."}  "ethos" .
    # :Sentence_249204c5-4e80 :rhetorical_device {:evidence "Comparing herself to Abraham Lincoln serves as a
    #       metaphor, likening her situation or qualities to those of Lincoln."}  "metaphor" .
    # :Sentence_249204c5-4e80 :has_semantic :Event_48caed53-cba5 .
    # :Event_48caed53-cba5 a :Cognition ; :text "compared" .
    # :Event_48caed53-cba5 :has_active_entity :Liz_Cheney .
    # :Event_48caed53-cba5 :has_topic :Abraham_Lincoln .
    # :Sentence_249204c5-4e80 :has_semantic :Event_b715c899-94f6 .
    # :Event_b715c899-94f6 a :CommunicationAndSpeechAct ; :text "concession speech" .
    # :Event_b715c899-94f6 :has_topic [:text "concession speech" ; a :End] .
    # :Sentence_249204c5-4e80 :has_semantic :Event_20f6fa57-7aed .
    # :Event_20f6fa57-7aed a :WinAndLoss ; :text "loss" .
    # :Event_20f6fa57-7aed :has_topic [:text "her loss" ; a :Person] .
    # :Event_20f6fa57-7aed :has_active_entity :Harriet_Hageman .    # Winner's perspective taken


def test_coref():
    sent_dicts, quotations, quotations_dict = parse_narrative(text_coref)
    success, graph_ttl = create_graph(quotations_dict, sent_dicts)
    ttl_str = str(graph_ttl)
    print(ttl_str)
    # Output Turtle:   TODO


def test_xcomp():
    sent_dicts, quotations, quotations_dict = parse_narrative(text_xcomp)
    success, graph_ttl = create_graph(quotations_dict, sent_dicts)
    ttl_str = str(graph_ttl)
    assert ':has_affected_agent :Mary' in ttl_str and ':has_topic [:text "grandfather' in ttl_str
    assert 'a :EmotionalResponse' in ttl_str
    assert ':sentiment "positive' in ttl_str
    # Output:
    # :Sentence_8bf2537b-c7cd a :Sentence ; :offset 1 .
    # :Sentence_8bf2537b-c7cd :text "Mary enjoyed being with her grandfather." .
    # :Mary a :Person .
    # :Mary rdfs:label "Mary" .
    # :Mary rdfs:comment "Needs disambiguation; See the web site, https://en.wikipedia.org/wiki/Mary" .
    # :Mary :gender "female" .
    # :Sentence_8bf2537b-c7cd :mentions :Mary .
    # :Sentence_8bf2537b-c7cd :sentence_person 3 ; :sentiment "positive".
    # :Sentence_8bf2537b-c7cd :voice "active" ; :tense "past" ; :summary "Mary enjoyed grandfather\'s company." .
    # :Sentence_8bf2537b-c7cd :grade_level 3 .
    # :Sentence_8bf2537b-c7cd :has_semantic :Event_48cb18ed-3652 .
    # :Event_48cb18ed-3652 a :EmotionalResponse ; :text "enjoyed" .
    # :Event_48cb18ed-3652 :has_affected_entity :Mary .
    # :Event_48cb18ed-3652 :has_topic [:text "grandfather" ; a :Person] .


def test_modal():
    sent_dicts, quotations, quotations_dict = parse_narrative(text_modal)
    success, graph_ttl = create_graph(quotations_dict, sent_dicts)
    ttl_str = str(graph_ttl)
    assert ':has_active_agent :Mary' in ttl_str and ':has_topic [:text "grandfather' in ttl_str
    assert 'a :ReadinessAndAbility' in ttl_str       # can
    assert 'a :MeetingAndEncounter' in ttl_str       # visit
    assert ':mentions :PiT_DayTuesday' in ttl_str
    # Output Turtle:
    # :Sentence_e04a69c5-a84c a :Sentence ; :offset 1 .
    # :Sentence_e04a69c5-a84c :text "Mary can visit her grandfather on Tuesdays." .
    # :Mary a :Person .
    # :Mary rdfs:label "Mary" .
    # :Mary rdfs:comment "Needs disambiguation; See the web site, https://en.wikipedia.org/wiki/Mary" .
    # :Mary :gender "female" .
    # :PiT_DayTuesday a :PointInTime ; rdfs:label "Tuesdays" .
    # :Sentence_e04a69c5-a84c :mentions :Mary .
    # :Sentence_e04a69c5-a84c :mentions :Tuesdays .
    # :Sentence_e04a69c5-a84c :sentence_person 3 ; :sentiment "neutral".
    # :Sentence_e04a69c5-a84c :voice "active" ; :tense "present" ; :summary "Mary visits grandfather Tuesdays" .
    # :Sentence_e04a69c5-a84c :grade_level 3 .
    # :Sentence_e04a69c5-a84c :has_semantic :ReadinessAndAbility .     # can
    # :Sentence_e04a69c5-a84c :has_semantic :Event_a7c39915-4230 .
    # :Event_a7c39915-4230 a :MeetingAndEncounter ; :text "visit" .
    # :Event_a7c39915-4230 :has_active_entity :Mary .
    # :Event_a7c39915-4230 :has_topic [:text "grandfather" ; a :Person] .
    # :Sentence_e04a69c5-a84c :has_semantic :Event_a069150f-5d23 .
    # :Event_a069150f-5d23 a :Continuation ; :text "Tuesdays" .        # TODO: Repeating sequence, 'on Tuesdays'


def test_acomp():
    sent_dicts, quotations, quotations_dict = parse_narrative(text_acomp)
    success, graph_ttl = create_graph(quotations_dict, sent_dicts)
    ttl_str = str(graph_ttl)
    print(ttl_str)
    assert ':has_active_agent :Mary' in ttl_str and ':has_active_agent :grandfather' in ttl_str
    assert 'a :OpportunityAndPossibility' in ttl_str      # 'can'
    assert 'a :MeetingAndEncounter' in ttl_str
    # Output Turtle:   TODO
