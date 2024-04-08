import pytest
from dna.create_narrative_turtle import create_graph
from dna.nlp import parse_narrative

text_clauses1 = 'While Mary exercised, John practiced guitar.'
text_clauses2 = 'George went along with the plan that Mary outlined.'
text_aux_only = 'Joe is an attorney.'
text_affiliation = 'Joe is a member of the Mayberry Book Club.'
text_complex1 = \
    'Rep. Liz Cheney R-WY compared herself to former President Abraham Lincoln during her concession ' \
    'speech shortly after her loss to Trump-backed Republican challenger Harriet Hageman.'
text_complex2 = \
    'Harriet Hageman, a water and natural-resources attorney who was endorsed by the former president, won ' \
    '66.3% of the vote to Ms. Cheney’s 28.9%, with 95% of all votes counted.'
text_coref = 'Joe broke his foot. He went to the doctor.'
text_xcomp = 'Mary enjoyed being with her grandfather.'
text_modal = 'Mary can visit her grandfather on Tuesday.'
text_modal_neg = 'Mary will not visit her grandfather next Tuesday.'
text_acomp = 'Mary is very beautiful.'
text_pobj = 'The connector is in compliance with the specifications.'
text_acomp_pcomp = 'Peter got tired of running.'
text_acomp_xcomp = 'Jane is unable to tolerate smoking.'
text_idiom = 'Wear and tear on the bridge caused its collapse.'
text_idiom_full_pass = 'John was accused by George of breaking and entering.'
text_idiom_trunc_pass = 'John was accused of breaking and entering.'
text_negation_emotional = 'Jane has no liking for broccoli.'
text_negation = 'Jane did not stab John.'


# Note that it is unlikely that all tests will complete successfully since event semantics can be
# interpreted/reported in multiple ways
# 80%+ of tests should pass


def test_clauses1():
    sent_dicts, quotations, quotations_dict = parse_narrative(text_clauses1)
    success, index, graph_ttl = create_graph(quotations_dict, sent_dicts)
    ttl_str = str(graph_ttl)
    assert ':negated true' not in ttl_str
    assert ':has_active_entity :Mary' in ttl_str
    assert ':has_instrument [ :text "guitar" ; a :MusicalInstrument' in ttl_str
    assert 'a :BodilyAct ; :text "exercised' in ttl_str
    assert 'a :ArtAndEntertainmentEvent ; :text "practiced' in ttl_str \
           or 'a :KnowledgeAndSkill ; :text "practiced' in ttl_str
    if 'a :KnowledgeAndSkill' in ttl_str:
        assert ':has_described_entity :John' in ttl_str
    else:
        assert ':has_active_entity :John' in ttl_str
    # Output Turtle:
    # :Sentence_858a0e52-8ff0 a :Sentence ; :offset 1 .
    # :Sentence_858a0e52-8ff0 :text "While Mary exercised, John practiced guitar." .
    # :Mary a :Person .
    # :Mary rdfs:label "Mary" .
    # :Mary rdfs:comment "Needs disambiguation; See the web site, https://en.wikipedia.org/wiki/Mary" .
    # :Mary :gender "female" .
    # :John a :Person .
    # :John rdfs:label "John" .
    # :John rdfs:comment "Needs disambiguation; See the web site, https://en.wikipedia.org/wiki/John" .
    # :John :gender "male" .
    # :Sentence_858a0e52-8ff0 :mentions :Mary .
    # :Sentence_858a0e52-8ff0 :mentions :John .
    # :Sentence_858a0e52-8ff0 :sentence_person 3 ; :sentiment "neutral".
    # :Sentence_858a0e52-8ff0 :tense "past" ; :summary "Mary exercised, John played guitar." .
    # :Sentence_858a0e52-8ff0 :grade_level 3 .
    # :Sentence_858a0e52-8ff0 :has_semantic  :Event_b74e75c2-d432 .
    # :Event_b74e75c2-d432 a :BodilyAct ; :text "exercised" .
    # :Sentence_858a0e52-8ff0 :has_semantic  :Event_7307a6f8-f0cb .
    # :Event_7307a6f8-f0cb a :ArtAndEntertainmentEvent ; :text "practiced guitar" .
    # :Sentence_858a0e52-8ff0 :has_semantic {:summary true} :Event_bcf26d1e-77c4 .
    # :Event_bcf26d1e-77c4 a :BodilyAct ; :text "exercised" .
    # :Event_bcf26d1e-77c4 :has_active_entity :Mary .
    # :Sentence_858a0e52-8ff0 :has_semantic {:summary true} :Event_51a384e0-6aed .    # Summary true
    # :Event_51a384e0-6aed a :ArtAndEntertainmentEvent ; :text "played guitar" .
    # :Event_51a384e0-6aed :has_active_entity :John .
    # :Event_51a384e0-6aed :has_instrument [ :text "guitar" ; a :MusicalInstrument ] .


def test_clauses2():
    sent_dicts, quotations, quotations_dict = parse_narrative(text_clauses2)
    success, index, graph_ttl = create_graph(quotations_dict, sent_dicts)
    ttl_str = str(graph_ttl)
    assert ':negated true' not in ttl_str
    assert ':has_active_entity :Mary' in ttl_str and ':has_active_entity :George' in ttl_str
    assert ':has_topic [ :text "plan" ; a :Process' in ttl_str or \
           ':has_topic [ :text "the plan" ; a :Process' in ttl_str
    assert 'a :Cognition ; :text "went along with' in ttl_str or \
           'a :Agreement ; :text "went along with' in ttl_str
    assert 'a :Cognition ; :text "outlined"' in ttl_str
    # Output Turtle:
    # :Sentence_50f45db1-81bc :mentions :George .
    # :Sentence_50f45db1-81bc :mentions :Mary .
    # :Sentence_50f45db1-81bc :sentence_person 3 ; :sentiment "neutral".
    # :Sentence_50f45db1-81bc :tense "past" ; :summary "George agreed to Mary\'s plan." .
    # :Sentence_50f45db1-81bc :grade_level 5 .
    # :Sentence_50f45db1-81bc :has_semantic  :Event_9be1583c-86d9 .
    # :Event_9be1583c-86d9 a :Agreement ; :text "went along with" .
    # :Sentence_50f45db1-81bc :has_semantic  :Event_cf47ca81-6af0 .
    # :Event_cf47ca81-6af0 a :Process ; :text "plan" .
    # :Sentence_50f45db1-81bc :has_semantic {:summary true} :Event_2eda9dcb-0cda .
    # :Event_2eda9dcb-0cda a :Agreement ; :text "agreed" .
    # :Event_2eda9dcb-0cda :has_active_entity :George .
    # :Event_2eda9dcb-0cda :has_topic :Mary .


def test_aux_only():
    sent_dicts, quotations, quotations_dict = parse_narrative(text_aux_only)
    success, index, graph_ttl = create_graph(quotations_dict, sent_dicts)
    ttl_str = str(graph_ttl)
    assert ':negated true' not in ttl_str
    if 'a :EnvironmentAndCondition' in ttl_str:    # is
        assert ':has_described_entity :Joe' in ttl_str
        assert ':text "attorney' in ttl_str or ':text "is an attorney' in ttl_str
    else:
        assert 'a :KnowledgeAndSkill ; :text "attorney' in ttl_str
        assert ':has_active_entity :Joe' in ttl_str
    # Output Turtle:
    # :Sentence_887a008f-a570 a :Sentence ; :offset 1 .
    # :Sentence_887a008f-a570 :text "Joe is an attorney." .
    # :Joe a :Person .
    # :Joe rdfs:label "Joe" .
    # :Joe rdfs:comment "Needs disambiguation; See the web site, https://en.wikipedia.org/wiki/Joe" .
    # :Joe :gender "male" .
    # :Sentence_887a008f-a570 :mentions :Joe .
    # :Sentence_887a008f-a570 :sentence_person 3 ; :sentiment "neutral".
    # :Sentence_887a008f-a570 :tense "present" ; :summary "Joe is a lawyer." .
    # :Sentence_887a008f-a570 :grade_level 5 .
    # :Sentence_887a008f-a570 :has_semantic :Event_11e7ab8e-f08b .
    # :Event_11e7ab8e-f08b a :EnvironmentAndCondition ; :text "is" .
    # :Event_11e7ab8e-f08b :has_described_entity :Joe .
    # :Event_11e7ab8e-f08b :has_aspect [ :text "attorney" ; a :LineOfBusiness ] .


def test_affiliation():
    sent_dicts, quotations, quotations_dict = parse_narrative(text_affiliation)
    success, index, graph_ttl = create_graph(quotations_dict, sent_dicts)
    ttl_str = str(graph_ttl)
    assert ':negated true' not in ttl_str
    assert 'a :Affiliation ; :text "member' in ttl_str
    assert 'Mayberry_Book_Club a :Organization' in ttl_str
    assert ':has_active_entity :Joe' in ttl_str
    assert ':affiliated_with :Mayberry_' in ttl_str
    # Output Turtle:
    # :Sentence_1c616dc4-e972 a :Sentence ; :offset 1 .
    # :Sentence_1c616dc4-e972 :text "Joe is a member of the Mayberry Book Club." .
    # :Joe a :Person .
    # :Joe rdfs:label "Joe" .
    # :Joe rdfs:comment "Needs disambiguation; See the web site, https://en.wikipedia.org/wiki/Joe" .
    # :Joe :gender "male" .
    # :the_Mayberry_Book_Club a :Organization .
    # :the_Mayberry_Book_Club rdfs:label "the Mayberry Book Club" .
    # :Sentence_1c616dc4-e972 :mentions :Joe .
    # :Sentence_1c616dc4-e972 :mentions :the_Mayberry_Book_Club .
    # :Sentence_1c616dc4-e972 :sentence_person 3 ; :sentiment "neutral".
    # :Sentence_1c616dc4-e972 :tense "present" ; :summary "Joe joins book club" .
    # :Sentence_1c616dc4-e972 :grade_level 5 .
    # :Sentence_1c616dc4-e972 :has_semantic :Event_1fa8a915-7f01 .
    # :Event_1fa8a915-7f01 a :Affiliation ; :text "member" .
    # :Event_1fa8a915-7f01 :has_active_entity :Joe .
    # :Event_1fa8a915-7f01 :affiliated_with :the_Mayberry_Book_Club .
    # :Sentence_1c616dc4-e972 :has_semantic :Event_e93216f2-60a9 .
    # :Event_e93216f2-60a9 a :EnvironmentAndCondition ; :text "is" .
    # :Event_e93216f2-60a9 :has_described_entity :Joe .


def test_complex1():
    sent_dicts, quotations, quotations_dict = parse_narrative(text_complex1)
    success, index, graph_ttl = create_graph(quotations_dict, sent_dicts)
    ttl_str = str(graph_ttl)
    assert ':negated true' not in ttl_str
    assert ':Harriet_Hageman' in ttl_str and ':Liz_Cheney' in ttl_str and ':Abraham_Lincoln' in ttl_str
    assert 'a :CommunicationAndSpeechAct' in ttl_str         # concession speech
    assert 'a :Cognition ; :text "compared' in ttl_str
    assert ':has_active_entity :Liz_Cheney' in ttl_str       # Cheney compared herself
    assert ':has_topic :Abraham_Lincoln' in ttl_str          # to Lincoln
    assert ' a :WinAndLoss ; :text "loss' in ttl_str
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
    # :Sentence_249204c5-4e80 :tense "past" ; :summary "Cheney compares herself to Lincoln, concedes." .
    # :Sentence_249204c5-4e80 :grade_level 8 .
    # :Sentence_249204c5-4e80 :rhetorical_device {:evidence "Rep. Liz Cheney compared herself to former President
    #       Abraham Lincoln, which is an allusion to a historical figure known for his leadership and integrity."}
    #       "allusion" .
    # :Sentence_249204c5-4e80 :rhetorical_device {:evidence "The reference to former President Abraham Lincoln
    #       invokes ethos by drawing on the authority and respect associated with Lincoln."}  "ethos" .
    # :Sentence_249204c5-4e80 :rhetorical_device {:evidence "Comparing herself to Abraham Lincoln serves as a
    #       metaphor, likening her situation or qualities to those of Lincoln."}  "metaphor" .
    # :Sentence_249204c5-4e80 :has_semantic :Event_4d51eb8e-a256 .
    # :Event_4d51eb8e-a256 a :Cognition ; :text "compared" .
    # :Event_4d51eb8e-a256 :has_active_entity :Liz_Cheney .
    # :Event_4d51eb8e-a256 :has_topic :Abraham_Lincoln .
    # :Sentence_249204c5-4e80 :has_semantic :Event_2abe3914-56c8 .
    # :Event_2abe3914-56c8 a :ArtAndEntertainmentEvent ;
    #       :text "concession speech" .   # TODO: Invalid classification as art and entertainment
    # :Event_2abe3914-56c8 :has_topic [ :text "concession speech" ; a :Ceremony ] .
    # :Sentence_249204c5-4e80 :has_semantic :Event_da71ebeb-7364 .
    # :Event_da71ebeb-7364 a :WinAndLoss ; :text "loss" .    # TODO: Need to be able to distinguish win/loss
    # :Event_da71ebeb-7364 :has_active_entity :Liz_Cheney .
    # :Sentence_249204c5-4e80 :has_semantic :Event_e0d06c89-cc0e .
    # :Event_e0d06c89-cc0e a :CommunicationAndSpeechAct ; :text "concedes" .
    # :Event_e0d06c89-cc0e :has_active_entity :Liz_Cheney .
    # TODO: What about Harriet Hageman's win?


def test_complex2():
    sent_dicts, quotations, quotations_dict = parse_narrative(text_complex2)
    success, index, graph_ttl = create_graph(quotations_dict, sent_dicts)
    ttl_str = str(graph_ttl)
    assert ':has_quantification' in ttl_str
    assert ':WinAndLoss ; :text "won' in ttl_str
    assert ':has_active_entity :Harriet_Hageman' in ttl_str
    assert ':Affiliation ; :text "endorsed' in ttl_str or ':CommunicationAndSpeechAct ; :text "endorsed' in ttl_str
    # "former president" likely associated as 'agent'/active_entity in an Affiliation or as the "source"
    # As a speech act, "former president" is the speaker/active_entity
    assert ':affiliated_with [ :text "former president' in ttl_str \
           or ':has_active_entity [ :text "former president' in ttl_str
    # Output Turtle:
    # :Sentence_af12d044-14eb a :Sentence ; :offset 1 .
    # :Sentence_af12d044-14eb :text "Harriet Hageman, a water and natural-resources attorney who was endorsed by
    #     the former president, won 66.3% of the vote to Ms. Cheney’s 28.9%, with 95% of all votes counted." .
    # :Harriet_Hageman a :Person .
    # :Harriet_Hageman rdfs:label "Harriet M. Hageman", "Harriet Hageman", "Harriet", "Hageman" .
    # :Harriet_Hageman rdfs:comment "From Wikipedia (wikibase_item: Q110815967): \'Harriet Maxine Hageman is an
    #     American politician and attorney serving as the U.S. representative for Wyoming\'s at-large congressional
    #     district since 2023. She is a member of the Republican Party.\'" .
    # :Harriet_Hageman :external_link "https://en.wikipedia.org/wiki/Harriet_Hageman" .
    # :Harriet_Hageman :gender "female" .
    # :Hagemans a :Person, :Collection ; rdfs:label "Hagemans" ; :role "family" .
    # :Cheney a :Person .
    # :Cheney rdfs:label "Cheney" .
    # :Cheney rdfs:comment "Needs disambiguation; See the web site, https://en.wikipedia.org/wiki/Cheney" .
    # :Sentence_af12d044-14eb :mentions :Harriet_Hageman .
    # :Sentence_af12d044-14eb :mentions :Cheney .
    # :Sentence_af12d044-14eb :sentence_person 3 ; :sentiment "positive".
    # :Sentence_af12d044-14eb :tense "past" ; :summary "Hageman wins, Cheney loses." .
    # :Sentence_af12d044-14eb :grade_level 8 .
    # :Sentence_af12d044-14eb :rhetorical_device {:evidence "won 66.3% of the vote to Ms. Cheney’s 28.9%, with
    #     95% of all votes counted"}  "logos" .
    # :Sentence_af12d044-14eb :has_semantic  :Event_cda68878-72e2 .
    # :Event_cda68878-72e2 a :WinAndLoss ; :text "won" .
    # :Event_cda68878-72e2 :has_active_entity :Harriet_Hageman .
    # :Event_cda68878-72e2 :has_quantification [ :text "66.3% of the vote" ; a :Measurement ] .
    # :Sentence_af12d044-14eb :has_semantic  :Event_73dec298-35bb .
    # :Event_73dec298-35bb a :Affiliation ; :text "endorsed" .
    # :Event_73dec298-35bb :affiliated_with [ :text "the former president" ; a :Person ] .
    # :Event_73dec298-35bb :affiliated_with :Harriet_Hageman .
    # :Sentence_af12d044-14eb :has_semantic  :Event_9c30429e-b194 .
    # :Event_9c30429e-b194 a :Measurement ; :text "votes counted" .
    # :Event_9c30429e-b194 :has_quantification [ :text "95% of all votes" ; a :Measurement ] .


def test_coref():
    sent_dicts, quotations, quotations_dict = parse_narrative(text_coref)
    success, index, graph_ttl = create_graph(quotations_dict, sent_dicts)
    ttl_str = str(graph_ttl)
    assert ':negated true' not in ttl_str
    assert 'a :HealthAndDiseaseRelated ; :text "broke' in ttl_str or \
           'a :BodilyAct ; :text "broke' in ttl_str or 'a :Mistake ; :text "broke' in ttl_str
    assert 'a :HealthAndDiseaseRelated ; :text "went to the doctor' in ttl_str
    assert ':has_affected_entity [ :text "foot" ; a :ComponentPart' in ttl_str or \
           ':has_topic [ :text "foot" ; a :ComponentPart' in ttl_str
    assert ':has_active_entity :Joe' in ttl_str
    assert ':has_location [ :text "doctor" ; a :LineOfBusiness' in ttl_str
    # Output Turtle:
    # :Sentence_429cfd0a-bed9 a :Sentence ; :offset 1 .
    # :Sentence_429cfd0a-bed9 :text "Joe broke his foot." .
    # :Joe a :Person .
    # :Joe rdfs:label "Joe" .
    # :Joe rdfs:comment "Needs disambiguation; See the web site, https://en.wikipedia.org/wiki/Joe" .
    # :Joe :gender "male" .
    # :Sentence_429cfd0a-bed9 :mentions :Joe .
    # :Sentence_429cfd0a-bed9 :sentence_person 3 ; :sentiment "negative".
    # :Sentence_429cfd0a-bed9 :tense "past" ; :summary "Joe injured his foot." .
    # :Sentence_429cfd0a-bed9 :grade_level 3 .
    # :Sentence_429cfd0a-bed9 :has_semantic :Event_1b9bc308-07cf .
    # :Event_1b9bc308-07cf a :Change ; :text "broke" .
    # :Event_1b9bc308-07cf :has_active_entity :Joe .
    # :Event_1b9bc308-07cf :has_topic [ :text "foot" ; a :ComponentPart ] .
    # :Sentence_429cfd0a-bed9 :has_semantic :Event_90e94e4a-a5ef .
    # :Event_90e94e4a-a5ef a :HealthAndDiseaseRelated ; :text "broke" .   # TODO: Ideally classified as Health
    # :Event_90e94e4a-a5ef :has_active_entity :Joe .
    # :Event_90e94e4a-a5ef :has_topic [ :text "foot" ; a :ComponentPart ] .
    # :Sentence_317205fe-e3a3 a :Sentence ; :offset 2 .
    # :Sentence_317205fe-e3a3 :text "He went to the doctor." .
    # :Sentence_317205fe-e3a3 :sentence_person 3 ; :sentiment "neutral".
    # :Sentence_317205fe-e3a3 :tense "past" ; :summary "Visited the doctor." .
    # :Sentence_317205fe-e3a3 :grade_level 3 .
    # :Sentence_317205fe-e3a3 :has_semantic :Event_eafcf2d1-b971 .
    # :Event_eafcf2d1-b971 a :HealthAndDiseaseRelated ; :text "went to the doctor" .
    # :Event_eafcf2d1-b971 :has_active_entity :Joe .
    # :Event_eafcf2d1-b971 :has_location [ :text "doctor" ; a :LineOfBusiness ] .
    # :Sentence_317205fe-e3a3 :has_semantic :Event_47f98fab-dfc8 .
    # :Event_47f98fab-dfc8 a :MeetingAndEncounter ; :text "Visited" .
    # :Event_47f98fab-dfc8 :has_location [ :text "doctor" ; a :LineOfBusiness ] .


def test_xcomp():
    sent_dicts, quotations, quotations_dict = parse_narrative(text_xcomp)
    success, index, graph_ttl = create_graph(quotations_dict, sent_dicts)
    ttl_str = str(graph_ttl)
    assert ':negated true' not in ttl_str
    assert ':has_active_entity :Mary' in ttl_str
    assert ':has_topic [ :text "grandfather' in ttl_str or \
           ':affiliated_with [ :text "grandfather' in ttl_str
    assert 'a :EmotionalResponse ; :text "enjoyed' in ttl_str
    assert ':sentiment "positive' in ttl_str
    # Output:
    # :Sentence_02e0d40d-d198 a :Sentence ; :offset 1 .
    # :Sentence_02e0d40d-d198 :text "Mary enjoyed being with her grandfather." .
    # :Mary a :Person .
    # :Mary rdfs:label "Mary" .
    # :Mary rdfs:comment "Needs disambiguation; See the web site, https://en.wikipedia.org/wiki/Mary" .
    # :Mary :gender "female" .
    # :Sentence_02e0d40d-d198 :mentions :Mary .
    # :Sentence_02e0d40d-d198 :sentence_person 3 ; :sentiment "positive".
    # :Sentence_02e0d40d-d198 :tense "past" ; :summary "Mary enjoyed grandfather\'s company." .
    # :Sentence_02e0d40d-d198 :grade_level 3 .
    # :Sentence_02e0d40d-d198 :has_semantic :Event_002eaf0f-61e0 .
    # :Event_002eaf0f-61e0 a :EmotionalResponse ; :text "enjoyed" .
    # :Event_002eaf0f-61e0 :has_active_entity :Mary .
    # :Event_002eaf0f-61e0 :has_topic [ :text "grandfather" ; a :Person ] .
    # :Sentence_02e0d40d-d198 :has_semantic :Event_061913da-c9d3 .
    # :Event_061913da-c9d3 a :Affiliation ; :text "being with" .
    # :Event_061913da-c9d3 :has_active_entity :Mary .
    # :Event_061913da-c9d3 :affiliated_with [ :text "grandfather" ; a :Person ] .


def test_modal():
    sent_dicts, quotations, quotations_dict = parse_narrative(text_modal)
    success, index, graph_ttl = create_graph(quotations_dict, sent_dicts)
    ttl_str = str(graph_ttl)
    assert ':negated true' not in ttl_str
    assert ':has_active_entity :Mary' in ttl_str
    assert ':has_affected_entity [ :text "grandfather' in ttl_str or ':has_topic [ :text "grandfather' in ttl_str
    assert ':has_semantic :OpportunityAndPossibility' in ttl_str       # can
    assert 'a :MeetingAndEncounter' in ttl_str                         # visit
    assert ':mentions :Tuesday' in ttl_str
    # Output Turtle:
    # :Sentence_34dffb9f-9fd1 a :Sentence ; :offset 1 .
    # :Sentence_34dffb9f-9fd1 :text "Mary can visit her grandfather on Tuesday." .
    # :Mary a :Person .
    # :Mary rdfs:label "Mary" .
    # :Mary rdfs:comment "Needs disambiguation; See the web site, https://en.wikipedia.org/wiki/Mary" .
    # :Mary :gender "female" .
    # :PiT_DayTuesday a :PointInTime ; rdfs:label "Tuesday" .
    # :Sentence_34dffb9f-9fd1 :mentions :Mary .
    # :Sentence_34dffb9f-9fd1 :mentions :Tuesday .
    # :Sentence_34dffb9f-9fd1 :sentence_person 3 ; :sentiment "neutral".
    # :Sentence_34dffb9f-9fd1 :tense "future" ; :summary "Mary visits grandfather Tuesday" .
    # :Sentence_34dffb9f-9fd1 :grade_level 3 .
    # :Sentence_34dffb9f-9fd1 :has_semantic :OpportunityAndPossibility .
    # :Sentence_34dffb9f-9fd1 :has_semantic :Event_97ab8996-057d .
    # :Event_97ab8996-057d a :MeetingAndEncounter ; :text "can visit" .
    # :Event_97ab8996-057d :has_active_entity :Mary .
    # :Event_97ab8996-057d :has_affected_entity [ :text "grandfather" ; a :Person ] .


def test_modal_neg():
    sent_dicts, quotations, quotations_dict = parse_narrative(text_modal_neg)
    success, index, graph_ttl = create_graph(quotations_dict, sent_dicts)
    ttl_str = str(graph_ttl)
    assert ':has_active_entity :Mary' in ttl_str
    assert ':has_affected_entity [ :text "grandfather' in ttl_str or ':has_topic [ :text "grandfather' in ttl_str \
           or ':has_affected_entity [ :text "Mary' in ttl_str or ':has_topic [ :text "Mary' in ttl_str
    if ':negated true' in ttl_str:
        assert 'a :MeetingAndEncounter' in ttl_str
    else:
        assert 'a :Avoidance ; :text "will not visit' in ttl_str
    # Output Turtle:
    # :Sentence_5d836047-184b a :Sentence ; :offset 1 .
    # :Sentence_5d836047-184b :text "Mary will not visit her grandfather next Tuesday." .
    # :Mary a :Person .
    # :Mary rdfs:label "Mary" .
    # :Mary rdfs:comment "Needs disambiguation; See the web site, https://en.wikipedia.org/wiki/Mary" .
    # :Mary :gender "female" .
    # :PiT_DayTuesday a :PointInTime ; rdfs:label "next Tuesday" .
    # :Sentence_5d836047-184b :mentions :Mary .
    # :Sentence_5d836047-184b :mentions :next_Tuesday .
    # :Sentence_5d836047-184b :sentence_person 3 ; :sentiment "negative".
    # :Sentence_5d836047-184b :tense "future" ; :summary "Mary won't visit grandfather Tuesday" .
    # :Sentence_5d836047-184b :grade_level 3 .
    # :Sentence_5d836047-184b :has_semantic :Event_7b7c8cd9-89ef .
    # :Event_7b7c8cd9-89ef a :Avoidance ; :text "will not visit" .
    # :Event_7b7c8cd9-89ef :has_active_entity :Mary .
    # :Event_7b7c8cd9-89ef :has_topic [ :text "grandfather" ; a :Person ] .


def test_acomp():
    sent_dicts, quotations, quotations_dict = parse_narrative(text_acomp)
    success, index, graph_ttl = create_graph(quotations_dict, sent_dicts)
    ttl_str = str(graph_ttl)
    print(ttl_str)
    assert ':negated true' not in ttl_str
    assert 'a :EnvironmentAndCondition' in ttl_str
    assert ':has_described_entity :Mary' in ttl_str
    # Output Turtle:
    # :Sentence_5eb9aaef-2589 a :Sentence ; :offset 1 .
    # :Sentence_5eb9aaef-2589 :text "Mary is very beautiful." .
    # :Mary a :Person .
    # :Mary rdfs:label "Mary" .
    # :Mary rdfs:comment "Needs disambiguation; See the web site, https://en.wikipedia.org/wiki/Mary" .
    # :Mary :gender "female" .
    # :Sentence_5eb9aaef-2589 :mentions :Mary .
    # :Sentence_5eb9aaef-2589 :sentence_person 3 ; :sentiment "positive".
    # :Sentence_5eb9aaef-2589 :tense "present" ; :summary "Mary is beautiful" .
    # :Sentence_5eb9aaef-2589 :grade_level 3 .
    # :Sentence_5eb9aaef-2589 :has_semantic  :Event_34d3a18a-81b8 .
    # :Event_34d3a18a-81b8 a :EnvironmentAndCondition ; :text "beautiful" .
    # :Event_34d3a18a-81b8 :has_described_entity :Mary .


def test_pobj():
    sent_dicts, quotations, quotations_dict = parse_narrative(text_pobj)
    success, index, graph_ttl = create_graph(quotations_dict, sent_dicts)
    ttl_str = str(graph_ttl)
    assert ':negated true' not in ttl_str
    assert 'a :Agreement' in ttl_str
    assert ':has_topic [ :text "connector' in ttl_str or ':has_topic [ :text "The connector' in ttl_str
    assert 'connector" ; a :ComponentPart' in ttl_str or 'connector" ; a :MachineAndTool' in ttl_str
    assert ':has_topic [ :text "specifications" ; a :InformationSource' in ttl_str \
           or 'a :EnvironmentAndCondition ; :text "specifications' in ttl_str
    # Output Turtle:
    # :Sentence_6f25ccc0-6bef a :Sentence ; :offset 1 .
    # :Sentence_6f25ccc0-6bef :text "The connector is in compliance with the specifications." .
    # :Sentence_6f25ccc0-6bef :sentence_person 3 ; :sentiment "neutral".
    # :Sentence_6f25ccc0-6bef :tense "present" ; :summary "Connector meets specifications." .
    # :Sentence_6f25ccc0-6bef :grade_level 8 .
    # :Sentence_6f25ccc0-6bef :has_semantic :Event_27dbdb9a-a1ef .
    # :Event_27dbdb9a-a1ef a :Agreement ; :text "in compliance with" .
    # :Event_27dbdb9a-a1ef :has_topic [ :text "connector" ; a :MachineAndTool ] .
    # :Event_27dbdb9a-a1ef :has_topic [ :text "specifications" ; a :InformationSource ]  .


def test_acomp_pcomp():
    sent_dicts, quotations, quotations_dict = parse_narrative(text_acomp_pcomp)
    success, index, graph_ttl = create_graph(quotations_dict, sent_dicts)
    ttl_str = str(graph_ttl)
    assert ':negated true' not in ttl_str
    assert 'a :BodilyAct ; :text "got tired' in ttl_str or \
           'a :SensoryPerception ; :text "got tired' in ttl_str or 'a :Change ; :text "got tired' in ttl_str
    assert 'a :BodilyAct ; :text "running' in ttl_str \
           or ':has_topic [ :text "running" ; a :MovementTravelAndTransportation' in ttl_str \
           or ':has_topic [ :text "running" ; a :BodilyAct' in ttl_str
    # Output Turtle:
    # :Sentence_678b7c90-6579 a :Sentence ; :offset 1 .
    # :Sentence_678b7c90-6579 :text "Peter got tired of running." .
    # :Peter a :Person .
    # :Peter rdfs:label "Peter" .
    # :Peter rdfs:comment "Needs disambiguation; See the web site, https://en.wikipedia.org/wiki/Peter" .
    # :Peter :gender "male" .
    # :Sentence_678b7c90-6579 :mentions :Peter .
    # :Sentence_678b7c90-6579 :sentence_person 3 ; :sentiment "negative".
    # :Sentence_678b7c90-6579 :tense "past" ; :summary "Peter exhausted from running." .
    # :Sentence_678b7c90-6579 :grade_level 3 .
    # :Sentence_678b7c90-6579 :has_semantic :Event_619c7a31-5faf .
    # :Event_619c7a31-5faf a :SensoryPerception ; :text "got tired" .
    # :Event_619c7a31-5faf :has_active_entity :Peter .
    # :Sentence_678b7c90-6579 :has_semantic :Event_d9c5d2e0-e9de .
    # :Event_d9c5d2e0-e9de a :BodilyAct ; :text "running" .
    # :Event_d9c5d2e0-e9de :has_topic [ :text "running" ; a :MovementTravelAndTransportation ] .


def test_acomp_xcomp():
    sent_dicts, quotations, quotations_dict = parse_narrative(text_acomp_xcomp)
    success, index, graph_ttl = create_graph(quotations_dict, sent_dicts)
    ttl_str = str(graph_ttl)
    assert ':negated true' not in ttl_str
    assert 'a :EmotionalResponse ; :text "unable to tolerate' in ttl_str \
        or 'a :Avoidance ; :text "unable to tolerate'
    assert ':has_active_entity :Jane' in ttl_str
    assert ':has_topic [ :text "smoking' in ttl_str
    # Output Turtle:
    # :Sentence_17860020-6180 a :Sentence ; :offset 1 .
    # :Sentence_17860020-6180 :text "Jane is unable to tolerate smoking." .
    # :Jane a :Person .
    # :Jane rdfs:label "Jane" .
    # :Jane rdfs:comment "Needs disambiguation; See the web site, https://en.wikipedia.org/wiki/Jane" .
    # :Jane :gender "female" .
    # :Sentence_17860020-6180 :mentions :Jane .
    # :Sentence_17860020-6180 :sentence_person 3 ; :sentiment "negative".
    # :Sentence_17860020-6180 :tense "present" ; :summary "Jane dislikes smoking" .
    # :Sentence_17860020-6180 :grade_level 5 .
    # :Sentence_17860020-6180 :has_semantic :Event_9c45d231-befe .
    # :Event_9c45d231-befe a :Avoidance ; :text "unable to tolerate" .
    # :Event_9c45d231-befe :has_active_entity :Jane .
    # :Event_9c45d231-befe :has_topic [ :text "smoking" ; a :Avoidance ] .']   # TODO: Versus BodilyAct


def test_idiom():
    sent_dicts, quotations, quotations_dict = parse_narrative(text_idiom)
    success, index, graph_ttl = create_graph(quotations_dict, sent_dicts)
    ttl_str = str(graph_ttl)
    assert ':negated true' not in ttl_str
    assert 'a :Change ; :text "Wear and tear' in ttl_str
    assert 'a :End ; :text "collapse' in ttl_str or 'a :CauseAndEffect ; :text "caused' in ttl_str
    assert ':has_affected_entity [ :text "bridge" ; a :Location' in ttl_str or \
           ':has_topic [ :text "bridge" ; a :Location' in ttl_str
    # Output Turtle:
    # :Sentence_4044df4a-68ae a :Sentence ; :offset 1 .
    # :Sentence_4044df4a-68ae :text "Wear and tear on the bridge caused its collapse." .
    # :Sentence_4044df4a-68ae :sentence_person 3 ; :sentiment "negative".
    # :Sentence_4044df4a-68ae :tense "past" ; :summary "Bridge collapsed due to wear and tear." .
    # :Sentence_4044df4a-68ae :grade_level 5 .
    # :Sentence_4044df4a-68ae :has_semantic :Event_becd306f-9b79 .
    # :Event_becd306f-9b79 a :Change ; :text "Wear and tear" .
    # :Event_becd306f-9b79 :has_affected_entity [ :text "bridge" ; a :Location ] .
    # :Sentence_4044df4a-68ae :has_semantic :Event_0a45c608-698b .
    # :Event_0a45c608-698b a :End ; :text "collapse" .
    # :Event_0a45c608-698b :has_topic [ :text "bridge" ; a :Location ] .


def test_idiom_full_pass():
    sent_dicts, quotations, quotations_dict = parse_narrative(text_idiom_full_pass)
    success, index, graph_ttl = create_graph(quotations_dict, sent_dicts)
    ttl_str = str(graph_ttl)
    assert ':negated true' not in ttl_str
    assert 'a :CommunicationAndSpeechAct ; :text "accused' in ttl_str or \
           'a :LegalEvent ; :text "accused' in ttl_str
    assert ':has_affected_entity :John' in ttl_str
    assert ':has_active_entity :George' in ttl_str
    assert ':AggressiveCriminalOrHostileAct ; :text "breaking and entering' in ttl_str
    # Output Turtle:
    # :Sentence_173da7da-4eb4 a :Sentence ; :offset 1 .
    # :Sentence_173da7da-4eb4 :text "John was accused by George of breaking and entering." .
    # :John a :Person .
    # :John rdfs:label "John" .
    # :John rdfs:comment "Needs disambiguation; See the web site, https://en.wikipedia.org/wiki/John" .
    # :John :gender "male" .
    # :George a :Person .
    # :George rdfs:label "George" .
    # :George rdfs:comment "Needs disambiguation; See the web site, https://en.wikipedia.org/wiki/George" .
    # :George :gender "male" .
    # :Sentence_173da7da-4eb4 :mentions :John .
    # :Sentence_173da7da-4eb4 :mentions :George .
    # :Sentence_173da7da-4eb4 :sentence_person 3 ; :sentiment "negative".
    # :Sentence_173da7da-4eb4 :tense "past" ; :summary "John accused by George" .
    # :Sentence_173da7da-4eb4 :grade_level 6 .
    # :Sentence_173da7da-4eb4 :has_semantic :Event_60a4e77f-2eab .
    # :Event_60a4e77f-2eab a :CommunicationAndSpeechAct ; :text "accused" .
    # :Event_60a4e77f-2eab :has_affected_entity :John .
    # :Event_60a4e77f-2eab :has_active_entity :George .
    # :Sentence_173da7da-4eb4 :has_semantic :Event_e6c5fe70-381b .
    # :Event_e6c5fe70-381b a :AggressiveCriminalOrHostileAct ; :text "breaking and entering" .
    # :Event_e6c5fe70-381b :has_active_entity :John .


def test_idiom_trunc_pass():
    sent_dicts, quotations, quotations_dict = parse_narrative(text_idiom_trunc_pass)
    success, index, graph_ttl = create_graph(quotations_dict, sent_dicts)
    ttl_str = str(graph_ttl)
    assert ':negated true' not in ttl_str
    assert 'a :CommunicationAndSpeechAct' in ttl_str or ':LegalEvent' in ttl_str   # accused
    assert ':has_affected_entity :John' in ttl_str
    assert ':AggressiveCriminalOrHostileAct' in ttl_str     # breaking and entering
    # Output Turtle:
    # :Sentence_4506adb1-abdc a :Sentence ; :offset 1 .
    # :Sentence_4506adb1-abdc :text "John was accused of breaking and entering." .
    # :John a :Person .
    # :John rdfs:label "John" .
    # :John rdfs:comment "Needs disambiguation; See the web site, https://en.wikipedia.org/wiki/John" .
    # :John :gender "male" .
    # :Sentence_4506adb1-abdc :mentions :John .
    # :Sentence_4506adb1-abdc :sentence_person 3 ; :sentiment "negative".
    # :Sentence_4506adb1-abdc :tense "past" ; :summary "John accused of crime" .
    # :Sentence_4506adb1-abdc :grade_level 5 .
    # :Sentence_4506adb1-abdc :has_semantic :Event_193676ae-0154 .
    # :Event_193676ae-0154 a :AggressiveCriminalOrHostileAct ; :text "accused of breaking and entering" .
    # :Event_193676ae-0154 :has_affected_entity :John .
    # :Sentence_4506adb1-abdc :has_semantic :Event_2d4f9813-c5cc .
    # :Event_2d4f9813-c5cc a :CommunicationAndSpeechAct ; :text "was accused" .
    # :Event_2d4f9813-c5cc :has_affected_entity :John .


def test_negation_emotional():
    sent_dicts, quotations, quotations_dict = parse_narrative(text_negation_emotional)
    success, index, graph_ttl = create_graph(quotations_dict, sent_dicts)
    ttl_str = str(graph_ttl)
    assert ':negated true' not in ttl_str
    assert 'a :EmotionalResponse' in ttl_str
    assert ':has_active_entity :Jane' in ttl_str
    assert ':has_topic [ :text "broccoli" ; a :Plant' in ttl_str
    # Output Turtle:
    # :Sentence_44a2e93d-972a a :Sentence ; :offset 1 .
    # :Sentence_44a2e93d-972a :text "Jane has no liking for broccoli." .
    # :Jane a :Person .
    # :Jane rdfs:label "Jane" .
    # :Jane rdfs:comment "Needs disambiguation; See the web site, https://en.wikipedia.org/wiki/Jane" .
    # :Jane :gender "female" .
    # :Sentence_44a2e93d-972a :mentions :Jane .
    # :Sentence_44a2e93d-972a :sentence_person 3 ; :sentiment "negative".
    # :Sentence_44a2e93d-972a :tense "present" ; :summary "Jane dislikes broccoli." .
    # :Sentence_44a2e93d-972a :grade_level 3 .
    # :Sentence_44a2e93d-972a :has_semantic :Event_b5986efb-c6df .
    # :Event_b5986efb-c6df a :EmotionalResponse ; :text "no liking" .
    # :Event_b5986efb-c6df :has_active_entity :Jane .
    # :Event_b5986efb-c6df :has_topic [ :text "broccoli" ; a :Plant ] .


def test_negation():
    sent_dicts, quotations, quotations_dict = parse_narrative(text_negation)
    success, index, graph_ttl = create_graph(quotations_dict, sent_dicts)
    ttl_str = str(graph_ttl)
    if ':negated true' in ttl_str:
        assert 'a :AggressiveCriminalOrHostileAct '    # 'not stab' where stab = AggressiveCriminalOrHostileAct
    assert ':has_active_entity :Jane' in ttl_str
    assert ':has_affected_entity :John' in ttl_str
    # Output Turtle:
    # :Sentence_19f96950-bbe8 a :Sentence ; :offset 1 .
    # :Sentence_19f96950-bbe8 :text "Jane did not stab John." .
    # :Jane a :Person .
    # :Jane rdfs:label "Jane" .
    # :Jane rdfs:comment "Needs disambiguation; See the web site, https://en.wikipedia.org/wiki/Jane" .
    # :Jane :gender "female" .
    # :John a :Person .
    # :John rdfs:label "John" .
    # :John rdfs:comment "Needs disambiguation; See the web site, https://en.wikipedia.org/wiki/John" .
    # :John :gender "male" .
    # :Sentence_19f96950-bbe8 :mentions :Jane .
    # :Sentence_19f96950-bbe8 :mentions :John .
    # :Sentence_19f96950-bbe8 :sentence_person 3 ; :sentiment "negative".
    # :Sentence_19f96950-bbe8 :tense "past" ; :summary "Jane didn\'t stab John" .
    # :Sentence_19f96950-bbe8 :grade_level 5 .
    # :Sentence_19f96950-bbe8 :has_semantic :Event_b766ec92-cbaf .
    # :Event_b766ec92-cbaf a :AggressiveCriminalOrHostileAct ; :text "did not stab" .
    # :Event_b766ec92-cbaf :has_active_entity :Jane .
    # :Event_b766ec92-cbaf :has_affected_entity :John .
