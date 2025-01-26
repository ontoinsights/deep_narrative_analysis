import pytest
from dna.create_narrative_turtle import create_graph
from dna.nlp import parse_narrative

# Latest execution, Jan 26: test_acomp_xcomp failed to identify "smoking"

text_clauses1 = 'While Mary exercised, Jack practiced guitar.'
text_clauses2 = 'George agreed with the plan that Mary outlined.'
text_aux_only = 'Jack is an attorney.'
text_affiliation = 'Jack is a member of the Mayberry Book Club.'
text_complex1 = \
    'Rep. Liz Cheney R-WY compared herself to former President Abraham Lincoln during her concession ' \
    'speech shortly after her loss to Trump-backed Republican challenger Harriet Hageman.'
text_complex2 = \
    'Harriet Hageman, a water and natural-resources attorney who was endorsed by the former president, won ' \
    '66.3% of the vote to Ms. Cheney’s 28.9%, with 95% of all votes counted.'
text_coref = 'Jack broke his foot. He went to the doctor.'
text_xcomp = 'Mary enjoyed being with her grandfather.'
text_modal = 'Mary can visit her grandfather on Tuesday.'
text_modal_neg = 'Mary will not visit her grandfather next Tuesday.'
text_acomp = 'Mary is very beautiful.'
text_acomp_pcomp1 = 'Peter got tired of running.'
text_acomp_pcomp2 = 'Peter never tires of running.'
text_acomp_xcomp = 'Jane is unable to tolerate smoking.'
text_idiom = 'Wear and tear on the bridge caused its collapse.'
text_idiom_full_pass = 'Jack was accused by George of breaking and entering.'
text_idiom_trunc_pass = 'Jack was accused of breaking and entering.'
text_negative_emotion = 'Jane has no liking for broccoli.'
text_negation = 'Jane did not stab Jack.'
text_mention = 'The FBI raided the house.'
text_hyphenation = \
    'Joe Biden and Kamala Harris were running on the Democratic ticket in 2024. The Biden-Harris campaign ' \
    'suffered serious setbacks. Nancy Smith-Evans reported on this. Smith-Evans is a friend of Harris.'

repo = "foo"

# Note that it is unlikely that all tests will complete successfully since event semantics can be
# interpreted/reported in multiple ways
# 80%+ of the tests should pass

def test_clauses1():
    sentence_classes, quotation_classes = parse_narrative(text_clauses1)
    graph_results = create_graph(sentence_classes, quotation_classes, text_clauses1,
                                 ':Narrative_foo', [], 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':has_active_entity :Mary' in ttl_str
    assert ':has_active_entity :Jack' in ttl_str
    assert ':BodilyAct' in ttl_str                          # exercise
    assert ':ArtAndEntertainmentEvent' in ttl_str or ':EducationRelated' in ttl_str       # practice
    assert ':EducationRelated' in ttl_str
    assert ':MusicalInstrument ; :text "guitar' in ttl_str and ':has_topic :Noun' in ttl_str
    # Output Turtle:
    # :Narrative_foo :has_component :Sentence_32e1de15-8321 .
    # :Sentence_32e1de15-8321 a :Sentence ; :offset 1 .
    # :Sentence_32e1de15-8321 :text "While Mary exercised, Jack practiced guitar." .
    # :Sentence_32e1de15-8321 :mentions :Mary .
    # :Sentence_32e1de15-8321 :mentions :Jack .
    # :Sentence_32e1de15-8321 :grade_level 5 .
    # :Narrative_foo :describes :NarrativeEvent_c852f9f6-dfc5 .
    # :NarrativeEvent_c852f9f6-dfc5 a :NarrativeEvent ; :offset 0 .
    # :NarrativeEvent_c852f9f6-dfc5 :text "Mary exercised." .
    # :NarrativeEvent_c852f9f6-dfc5 :has_semantic :Event_8ef71edf-f656 .
    # :NarrativeEvent_c852f9f6-dfc5 :has_first :Event_8ef71edf-f656 .
    # :Event_8ef71edf-f656 :text "Mary exercised." .
    # :Event_8ef71edf-f656 a :BodilyAct ; :confidence-BodilyAct 100 .
    # :Event_8ef71edf-f656 :has_active_entity :Mary .
    # :Narrative_foo :describes :NarrativeEvent_904574fe-a15d .
    # :NarrativeEvent_904574fe-a15d a :NarrativeEvent ; :offset 1 .
    # :NarrativeEvent_904574fe-a15d :text "Jack practiced guitar." .
    # :NarrativeEvent_904574fe-a15d :has_semantic :Event_f813886d-789e .
    # :NarrativeEvent_904574fe-a15d :has_first :Event_f813886d-789e .
    # :Event_f813886d-789e :text "Jack practiced guitar." .
    # :Event_f813886d-789e a :ArtAndEntertainmentEvent ; :confidence-ArtAndEntertainmentEvent 90 .
    # :Event_f813886d-789e a :EducationRelated ; :confidence-EducationRelated 85 .
    # :Event_f813886d-789e :has_active_entity :Jack .
    # :Noun_c7a0f4bf-c238 a :MusicalInstrument ; :text "guitar" ; :confidence 100 .
    # :Event_f813886d-789e :has_topic :Noun_c7a0f4bf-c238 .


def test_clauses2():
    sentence_classes, quotation_classes = parse_narrative(text_clauses2)
    graph_results = create_graph(sentence_classes, quotation_classes, text_clauses2,
                                 ':Narrative_foo', [],5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':has_active_entity :George' in ttl_str
    assert ':Agreement' in ttl_str
    assert ':Process ; :text "the plan' in ttl_str or ':Process ; :text "plan' in ttl_str
    assert ':has_topic :Noun'
    assert ':CommunicationAndSpeechAct' in ttl_str or ':Cognition' in ttl_str    # outlined
    assert ':has_active_entity :Mary' in ttl_str
    # Output Turtle:
    # :Narrative_foo :has_component :Sentence_c97d8635-e66b .
    # :Sentence_c97d8635-e66b a :Sentence ; :offset 1 .
    # :Sentence_c97d8635-e66b :text "George agreed with the plan that Mary outlined." .
    # :Sentence_c97d8635-e66b :mentions :George .
    # :Sentence_c97d8635-e66b :mentions :Mary .
    # :Sentence_c97d8635-e66b :grade_level 6 .
    # :Narrative_foo :describes :NarrativeEvent_98efca10-f06f .
    # :NarrativeEvent_98efca10-f06f a :NarrativeEvent ; :offset 0 .
    # :NarrativeEvent_98efca10-f06f :text "George agreed with the plan that Mary outlined." .
    # :NarrativeEvent_98efca10-f06f :has_semantic :Event_dbef3f9a-b3a2 .
    # :NarrativeEvent_98efca10-f06f :has_first :Event_dbef3f9a-b3a2 .
    # :Event_dbef3f9a-b3a2 :text "George agreed with the plan." .
    # :Event_dbef3f9a-b3a2 a :Agreement ; :confidence-Agreement 95 .
    # :Event_dbef3f9a-b3a2 a :CommunicationAndSpeechAct ; :confidence-CommunicationAndSpeechAct 85 .
    # :Event_dbef3f9a-b3a2 :has_active_entity :George .
    # :Noun_fa77bb31-9eda a :Process ; :text "plan" ; :confidence 90 .
    # :Event_dbef3f9a-b3a2 :has_topic :Noun_fa77bb31-9eda .
    # :NarrativeEvent_98efca10-f06f :has_semantic :Event_17a49802-5073 .
    # :Event_dbef3f9a-b3a2 :has_next :Event_17a49802-5073 .
    # :Event_17a49802-5073 :text "Mary outlined the plan." .
    # :Event_17a49802-5073 a :CommunicationAndSpeechAct ; :confidence-CommunicationAndSpeechAct 90 .
    # :Event_17a49802-5073 a :Cognition ; :confidence-Cognition 80 .
    # :Event_17a49802-5073 :has_active_entity :Mary .
    # :Event_17a49802-5073 :has_topic :Noun_fa77bb31-9eda .


def test_aux_only():
    sentence_classes, quotation_classes = parse_narrative(text_aux_only)
    graph_results = create_graph(sentence_classes, quotation_classes, text_aux_only,
                                 ':Narrative_foo', [],5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':AttributeAndCharacteristic' in ttl_str             # is
    assert ':has_context :Jack' in ttl_str
    assert ':LineOfBusiness ; :text "attorney' in ttl_str    # attorney
    assert ':has_aspect :Noun' in ttl_str
    # Output Turtle:
    # :Narrative_foo :has_component :Sentence_e66413e5-71b2 .
    # :Sentence_e66413e5-71b2 a :Sentence ; :offset 1 .
    # :Sentence_e66413e5-71b2 :text "Jack is an attorney." .
    # :Sentence_e66413e5-71b2 :mentions :Jack .
    # :Sentence_e66413e5-71b2 :grade_level 3 .
    # :Narrative_foo :describes :NarrativeEvent_14acf00e-0d3e .
    # :NarrativeEvent_14acf00e-0d3e a :NarrativeEvent ; :offset 0 .
    # :NarrativeEvent_14acf00e-0d3e :text "Jack is an attorney." .
    # :NarrativeEvent_14acf00e-0d3e :has_semantic :Event_ad7e4896-364d .
    # :NarrativeEvent_14acf00e-0d3e :has_first :Event_ad7e4896-364d .
    # :Event_ad7e4896-364d :text "Jack is an attorney." .
    # :Event_ad7e4896-364d a :AttributeAndCharacteristic ; :confidence-AttributeAndCharacteristic 100 .
    # :Event_ad7e4896-364d :has_context :Jack .
    # :Noun_afd3bdfd-e82d a :LineOfBusiness ; :text "attorney" ; :confidence 95 .
    # :Event_ad7e4896-364d :has_aspect :Noun_afd3bdfd-e82d .


def test_affiliation():
    sentence_classes, quotation_classes = parse_narrative(text_affiliation)
    graph_results = create_graph(sentence_classes, quotation_classes, text_affiliation,
                                 ':Narrative_foo', [],5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':Affiliation' in ttl_str
    assert ':has_context :Jack' in ttl_str
    assert ':affiliated_with :Mayberry_' in ttl_str
    # Output Turtle:
    # :Narrative_foo :has_component :Sentence_0678465c-ac20 .
    # :Sentence_0678465c-ac20 a :Sentence ; :offset 1 .
    # :Sentence_0678465c-ac20 :text "Jack is a member of the Mayberry Book Club." .
    # :Sentence_0678465c-ac20 :mentions :Jack .
    # :Sentence_0678465c-ac20 :mentions :Mayberry_Book_Club .
    # :Sentence_0678465c-ac20 :grade_level 3 .
    # :Narrative_foo :describes :NarrativeEvent_5dc3c653-1812 .
    # :NarrativeEvent_5dc3c653-1812 a :NarrativeEvent ; :offset 0 .
    # :NarrativeEvent_5dc3c653-1812 :text "Jack is a member of the Mayberry Book Club." .
    # :NarrativeEvent_5dc3c653-1812 :has_semantic :Event_1a907f11-72d3 .
    # :NarrativeEvent_5dc3c653-1812 :has_first :Event_1a907f11-72d3 .
    # :Event_1a907f11-72d3 :text "Jack is a member of the Mayberry Book Club." .
    # :Event_1a907f11-72d3 a :Affiliation ; :confidence-Affiliation 100 .
    # :Event_1a907f11-72d3 a :AttributeAndCharacteristic ; :confidence-AttributeAndCharacteristic 90 .
    # :Event_1a907f11-72d3 :has_context :Jack .
    # :Event_1a907f11-72d3 :affiliated_with :Mayberry_Book_Club .


def test_complex1():
    sentence_classes, quotation_classes = parse_narrative(text_complex1)
    graph_results = create_graph(sentence_classes, quotation_classes, text_complex1, ':Narrative_foo',
                                 ['politics and international'], 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':mentions :Liz_Cheney' in ttl_str and ':mentions :Harriet_Hageman' in ttl_str \
        and ':mentions :Abraham_Lincoln' in ttl_str
    assert ':mentions :Trump' in ttl_str or ':mentions :Donald_Trump' in ttl_str   # Depending on previous ingests
    assert 'allusion' in ttl_str
    assert ':Cognition' in ttl_str                                       # compared
    assert ':has_active_entity :Liz_Cheney' in ttl_str
    assert ':has_affected_entity :Abraham_Lincoln' in ttl_str or ':has_topic :Abraham_Lincoln' in ttl_str
    assert ':CommunicationAndSpeechAct' in ttl_str                       # in concession speech
    assert ':Loss' in ttl_str
    assert ':has_affected_entity :Harriet_Hageman' in ttl_str            # Cheney lost to Hageman
    assert ':Affiliation' in ttl_str
    assert ':has_context :Harriet_Hageman' in ttl_str or ':affiliated_with :Harriet_Hageman' in ttl_str
    assert ':affiliated_with :Donald_Trump' in ttl_str or ':has_context :Donald_Trump' in ttl_str or \
           ':affiliated_with :Trump' in ttl_str or ':has_context :Trump' in ttl_str
    # Output Turtle:
    # :Narrative_foo :has_component :Sentence_653f77c1-caf2 .
    # :Sentence_653f77c1-caf2 a :Sentence ; :offset 1 .
    # :Sentence_653f77c1-caf2 :text "Rep. Liz Cheney R-WY compared herself to former President Abraham Lincoln during
    #     her concession speech shortly after her loss to Trump-backed Republican challenger Harriet Hageman." .
    # :Sentence_653f77c1-caf2 :mentions :Liz_Cheney .
    # :Sentence_653f77c1-caf2 :mentions :WY .
    # :Sentence_653f77c1-caf2 :mentions :Abraham_Lincoln .
    # :Sentence_653f77c1-caf2 :mentions :Trump .
    # :Sentence_653f77c1-caf2 :mentions :Republican .
    # :Sentence_653f77c1-caf2 :mentions :Harriet_Hageman .
    # :Sentence_653f77c1-caf2 :grade_level 10 .
    # :Sentence_653f77c1-caf2 :rhetorical_device "allusion" .
    # :Sentence_653f77c1-caf2 :rhetorical_device_allusion "The sentence uses an allusion by comparing Rep. Liz Cheney
    #     to former President Abraham Lincoln, a historical figure with symbolic meaning." .
    # :Narrative_foo :describes :NarrativeEvent_59a2b8ac-1f09 .
    # :NarrativeEvent_59a2b8ac-1f09 a :NarrativeEvent ; :offset 0 .
    # :NarrativeEvent_59a2b8ac-1f09 :text "Rep. Liz Cheney compared herself to former President Abraham Lincoln during
    #     her concession speech." .
    # :NarrativeEvent_59a2b8ac-1f09 :has_semantic :Event_726a822b-d2b5 .
    # :NarrativeEvent_59a2b8ac-1f09 :has_first :Event_726a822b-d2b5 .
    # :Event_726a822b-d2b5 :text "Rep. Liz Cheney compared Rep. Liz Cheney to former President Abraham Lincoln." .
    # :Event_726a822b-d2b5 a :Cognition ; :confidence-Cognition 90 .
    # :Event_726a822b-d2b5 :has_active_entity :Liz_Cheney .
    # :Event_726a822b-d2b5 :has_topic :Abraham_Lincoln .
    # :NarrativeEvent_59a2b8ac-1f09 :has_semantic :Event_4cc43336-6dc3 .
    # :Event_726a822b-d2b5 :has_next :Event_4cc43336-6dc3 .
    # :Event_4cc43336-6dc3 :text "Rep. Liz Cheney made a concession speech." .
    # :Event_4cc43336-6dc3 a :CommunicationAndSpeechAct ; :confidence-CommunicationAndSpeechAct 95 .
    # :Event_4cc43336-6dc3 :has_active_entity :Liz_Cheney .
    # :Narrative_foo :describes :NarrativeEvent_41d7615c-8c6b .
    # :NarrativeEvent_41d7615c-8c6b a :NarrativeEvent ; :offset 1 .
    # :NarrativeEvent_41d7615c-8c6b :text "Rep. Liz Cheney delivered her concession speech shortly after her loss to
    #     Trump-backed Republican challenger Harriet Hageman." .
    # :NarrativeEvent_41d7615c-8c6b :has_semantic :Event_dc29ffb3-3fcc .
    # :NarrativeEvent_41d7615c-8c6b :has_first :Event_dc29ffb3-3fcc .
    # :Event_dc29ffb3-3fcc :text "Liz Cheney delivered a concession speech." .
    # :Event_dc29ffb3-3fcc a :CommunicationAndSpeechAct ; :confidence-CommunicationAndSpeechAct 100 .
    # :Event_dc29ffb3-3fcc :has_active_entity :Liz_Cheney .
    # :Noun_83b18b5d-bbd9 a :CommunicationAndSpeechAct ; :text "concession speech" ; :confidence 95 .
    # :Event_dc29ffb3-3fcc :has_topic :Noun_83b18b5d-bbd9 .
    # :NarrativeEvent_41d7615c-8c6b :has_semantic :Event_c7ab5adf-fd84 .
    # :Event_dc29ffb3-3fcc :has_next :Event_c7ab5adf-fd84 .
    # :Event_c7ab5adf-fd84 :text "Liz Cheney lost to Harriet Hageman." .
    # :Event_c7ab5adf-fd84 a :Loss ; :confidence-Loss 100 .
    # :Event_c7ab5adf-fd84 :has_active_entity :Liz_Cheney .
    # :Event_c7ab5adf-fd84 :has_affected_entity :Harriet_Hageman .
    # :NarrativeEvent_41d7615c-8c6b :has_semantic :Event_5ec7514a-74fb .
    # :Event_c7ab5adf-fd84 :has_next :Event_5ec7514a-74fb .
    # :Event_5ec7514a-74fb :text "Harriet Hageman was backed by Trump." .
    # :Event_5ec7514a-74fb a :Affiliation ; :confidence-Affiliation 100 .
    # :Event_5ec7514a-74fb :has_context :Harriet_Hageman .
    # :Event_5ec7514a-74fb :has_context :Trump .


def test_complex2():
    sentence_classes, quotation_classes = parse_narrative(text_complex2)
    graph_results = create_graph(sentence_classes, quotation_classes, text_complex2, ':Narrative_foo',
                                 ['politics and international'], 5, repo)
    ttl_str = str(graph_results.turtle)
    assert 'logos' in ttl_str
    assert ':Win' in ttl_str
    assert ':has_active_entity :Harriet_Hageman' in ttl_str
    assert (':Loss' in ttl_str and ':has_active_entity :Liz_Cheney' in ttl_str) or \
           (':Measurement' in ttl_str and ':has_context :Liz_Cheney' in ttl_str)     # percentage of vote
    # Output Turtle:
    # :Narrative_foo :has_component :Sentence_70e8d14c-390a .
    # :Sentence_70e8d14c-390a a :Sentence ; :offset 1 .
    # :Sentence_70e8d14c-390a :text "Harriet Hageman, a water and natural-resources attorney who was endorsed by the
    #     former president, won 66.3% of the vote to Ms. Cheney’s 28.9%, with 95% of all votes counted." .
    # :Sentence_70e8d14c-390a :mentions :Harriet_Hageman .
    # :Sentence_70e8d14c-390a :mentions :Liz_Cheney .
    # :Sentence_70e8d14c-390a :grade_level 10 .
    # :Sentence_70e8d14c-390a :rhetorical_device "logos" .
    # :Sentence_70e8d14c-390a :rhetorical_device_logos "The sentence uses statistics and numbers, such as \'66.3%\',
    #     \'28.9%\', and \'95%\', to convey the election results, which is an appeal to logic and reason (logos)." .
    # :Narrative_foo :describes :NarrativeEvent_225af1e9-e340 .
    # :NarrativeEvent_225af1e9-e340 a :NarrativeEvent ; :offset 0 .
    # :NarrativeEvent_225af1e9-e340 :text "Harriet Hageman, a water and natural-resources attorney endorsed by the
    #     former president, won 66.3% of the vote." .
    # :NarrativeEvent_225af1e9-e340 :has_semantic :Event_379586be-46f3 .
    # :NarrativeEvent_225af1e9-e340 :has_first :Event_379586be-46f3 .
    # :Event_379586be-46f3 :text "Harriet Hageman is a water and natural-resources attorney." .
    # :Event_379586be-46f3 a :AttributeAndCharacteristic ; :confidence-AttributeAndCharacteristic 100 .
    # :Event_379586be-46f3 :has_context :Harriet_Hageman .
    # :Noun_d446e479-373d a :LineOfBusiness ; :text "water and natural-resources attorney" ; :confidence 95 .
    # :Event_379586be-46f3 :has_aspect :Noun_d446e479-373d .
    # :NarrativeEvent_225af1e9-e340 :has_semantic :Event_d7bb0b9e-3fd9 .
    # :Event_379586be-46f3 :has_next :Event_d7bb0b9e-3fd9 .
    # :Event_d7bb0b9e-3fd9 :text "Harriet Hageman was endorsed by the former president." .
    # :Event_d7bb0b9e-3fd9 a :Affiliation ; :confidence-Affiliation 100 .
    # :Event_d7bb0b9e-3fd9 :affiliated_with :Harriet_Hageman .
    # :Noun_bd0f821f-3c84 a :LineOfBusiness, :Collection ; :text "former president" ; :confidence 95 .
    # :Event_d7bb0b9e-3fd9 :has_context :Noun_bd0f821f-3c84 .
    # :NarrativeEvent_225af1e9-e340 :has_semantic :Event_3fb1492e-f1ad .
    # :Event_d7bb0b9e-3fd9 :has_next :Event_3fb1492e-f1ad .
    # :Event_3fb1492e-f1ad :text "Harriet Hageman won 66.3% of the vote." .
    # :Event_3fb1492e-f1ad a :Win ; :confidence-Win 100 .
    # :Event_3fb1492e-f1ad :has_active_entity :Harriet_Hageman .
    # :Narrative_foo :describes :NarrativeEvent_8b59e658-8942 .
    # :NarrativeEvent_8b59e658-8942 a :NarrativeEvent ; :offset 1 .
    # :NarrativeEvent_8b59e658-8942 :text "Ms. Cheney received 28.9% of the vote." .
    # :NarrativeEvent_8b59e658-8942 :has_semantic :Event_c2b876be-350b .
    # :NarrativeEvent_8b59e658-8942 :has_first :Event_c2b876be-350b .
    # :Event_c2b876be-350b :text "Ms. Cheney received 28.9% of the vote." .
    # :Event_c2b876be-350b a :Loss ; :confidence-Loss 100 .
    # :Event_c2b876be-350b :has_active_entity :Liz_Cheney .
    # :Narrative_foo :describes :NarrativeEvent_c2a70bd8-eabc .
    # :NarrativeEvent_c2a70bd8-eabc a :NarrativeEvent ; :offset 2 .
    # :NarrativeEvent_c2a70bd8-eabc :text "95% of all votes were counted." .
    # :NarrativeEvent_c2a70bd8-eabc :has_semantic :Event_6fc4933c-a0c4 .
    # :NarrativeEvent_c2a70bd8-eabc :has_first :Event_6fc4933c-a0c4 .
    # :Event_6fc4933c-a0c4 :text "All votes were counted." .
    # :Event_6fc4933c-a0c4 a :Measurement ; :confidence-Measurement 100 .
    # :Noun_8e945e07-7501 a :PoliticsRelated, :Collection ; :text "votes" ; :confidence 90 .
    # :Event_6fc4933c-a0c4 :has_context :Noun_8e945e07-7501 .
    # :NarrativeEvent_c2a70bd8-eabc :has_semantic :Event_7f533477-439b .
    # :Event_6fc4933c-a0c4 :has_next :Event_7f533477-439b .
    # :Event_7f533477-439b :text "The count of votes was 95%." .
    # :Event_7f533477-439b a :Measurement ; :confidence-Measurement 100 .
    # :Noun_ae0fce5c-aa5d a :Measurement ; :text "count" ; :confidence 90 .
    # :Event_7f533477-439b :has_context :Noun_ae0fce5c-aa5d .
    # :Event_7f533477-439b :has_context :Noun_8e945e07-7501 .


def test_coref():
    sentence_classes, quotation_classes = parse_narrative(text_coref)
    graph_results = create_graph(sentence_classes, quotation_classes, text_coref,
                                 ':Narrative_foo',[],5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':HealthAndDiseaseRelated' in ttl_str
    assert ':has_active_entity :Jack' in ttl_str
    assert ':ComponentPart ; :text "foot' in ttl_str               # Jack's foot
    assert ':has_affected_entity :Noun' in ttl_str
    assert ':MovementTravelAndTransportation' in ttl_str
    assert ':LineOfBusiness ; :text "doctor' in ttl_str and ':has_destination :Noun' in ttl_str
    # Output Turtle:
    # :Narrative_foo :has_component :Sentence_f3d61fe7-cc26 .
    # :Sentence_f3d61fe7-cc26 a :Sentence ; :offset 1 .
    # :Sentence_f3d61fe7-cc26 :text "Jack broke his foot." .
    # :Sentence_f3d61fe7-cc26 :mentions :Jack .
    # :Sentence_f3d61fe7-cc26 :grade_level 3 .
    # :Narrative_foo :has_component :Sentence_f008e240-c814 .
    # :Sentence_f008e240-c814 a :Sentence ; :offset 2 .
    # :Sentence_f008e240-c814 :text "He went to the doctor." .
    # :Sentence_f008e240-c814 :grade_level 3 .
    # :Narrative_foo :describes :NarrativeEvent_bb29b3c6-9349 .
    # :NarrativeEvent_bb29b3c6-9349 a :NarrativeEvent ; :offset 0 .
    # :NarrativeEvent_bb29b3c6-9349 :text "Jack broke his foot." .
    # :NarrativeEvent_bb29b3c6-9349 :has_semantic :Event_dbcbc507-4b14 .
    # :NarrativeEvent_bb29b3c6-9349 :has_first :Event_dbcbc507-4b14 .
    # :Event_dbcbc507-4b14 :text "Jack broke his foot." .
    # :Event_dbcbc507-4b14 a :HealthAndDiseaseRelated ; :confidence-HealthAndDiseaseRelated 100 .
    # :Event_dbcbc507-4b14 a :DamageAndDifficulty ; :confidence-DamageAndDifficulty 80 .
    # :Event_dbcbc507-4b14 :has_active_entity :Jack .
    # :Noun_7a516752-0042 a :ComponentPart ; :text "foot" ; :confidence 100 .
    # :Event_dbcbc507-4b14 :has_affected_entity :Noun_7a516752-0042 .
    # :Narrative_foo :describes :NarrativeEvent_53273428-668e .
    # :NarrativeEvent_53273428-668e a :NarrativeEvent ; :offset 1 .
    # :NarrativeEvent_53273428-668e :text "Jack went to the doctor." .
    # :NarrativeEvent_53273428-668e :has_semantic :Event_9a0d7ec2-c6cd .
    # :NarrativeEvent_53273428-668e :has_first :Event_9a0d7ec2-c6cd .
    # :Event_9a0d7ec2-c6cd :text "Jack went to the doctor." .
    # :Event_9a0d7ec2-c6cd a :MovementTravelAndTransportation ; :confidence-MovementTravelAndTransportation 90 .
    # :Event_9a0d7ec2-c6cd a :HealthAndDiseaseRelated ; :confidence-HealthAndDiseaseRelated 80 .
    # :Event_9a0d7ec2-c6cd :has_active_entity :Jack .
    # :Noun_885af8f1-e951 a :LineOfBusiness ; :text "doctor" ; :confidence 95 .
    # :Event_9a0d7ec2-c6cd :has_destination :Noun_885af8f1-e951 .


def test_xcomp():
    sentence_classes, quotation_classes = parse_narrative(text_xcomp)
    graph_results = create_graph(sentence_classes, quotation_classes, text_xcomp,
                                 ':Narrative_foo', [],5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':EmotionalResponse' in ttl_str          # enjoyed
    assert ':MeetingAndEncounter' in ttl_str        # being with
    assert ':has_active_entity :Mary' in ttl_str
    assert ':Person' in ttl_str and (':text "grandfather' in ttl_str or ':text "her grandfather' in ttl_str)
    assert ':has_affected_entity :Noun' in ttl_str or ':has_topic :Noun' in ttl_str
    # Output:
    # :Narrative_foo :has_component :Sentence_69d195fa-4280 .
    # :Sentence_69d195fa-4280 a :Sentence ; :offset 1 .
    # :Sentence_69d195fa-4280 :text "Mary enjoyed being with her grandfather." .
    # :Sentence_69d195fa-4280 :mentions :Mary .
    # :Sentence_69d195fa-4280 :grade_level 3 .
    # :Narrative_foo :describes :NarrativeEvent_7d3d3764-d183 .
    # :NarrativeEvent_7d3d3764-d183 a :NarrativeEvent ; :offset 0 .
    # :NarrativeEvent_7d3d3764-d183 :text "Mary enjoyed being with her grandfather." .
    # :NarrativeEvent_7d3d3764-d183 :has_semantic :Event_678988b4-2206 .
    # :NarrativeEvent_7d3d3764-d183 :has_first :Event_678988b4-2206 .
    # :Event_678988b4-2206 :text "Mary enjoyed being with her grandfather." .
    # :Event_678988b4-2206 a :EmotionalResponse ; :confidence-EmotionalResponse 95 .
    # :Event_678988b4-2206 a :MeetingAndEncounter ; :confidence-MeetingAndEncounter 90 .
    # :Event_678988b4-2206 :has_active_entity :Mary .
    # :Noun_b11994c4-93c8 a :Person ; :text "her grandfather" ; :confidence 95 .
    # :Event_678988b4-2206 :has_topic :Noun_b11994c4-93c8 .


def test_modal():
    sentence_classes, quotation_classes = parse_narrative(text_modal)
    graph_results = create_graph(sentence_classes, quotation_classes, text_modal,
                                 ':Narrative_foo', [], 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':ReadinessAndAbility' in ttl_str
    assert ':MeetingAndEncounter' in ttl_str
    assert ':has_active_entity :Mary' in ttl_str
    assert ':Person' in ttl_str and (':text "grandfather' in ttl_str or ':text "her grandfather' in ttl_str)
    assert ':has_affected_entity :Noun' in ttl_str
    assert 'a :Time ; :text "Tuesday' in ttl_str and ':has_time' in ttl_str
    # Output Turtle:
    # :Narrative_foo :has_component :Sentence_f4b91c72-fb96 .
    # :Sentence_f4b91c72-fb96 a :Sentence ; :offset 1 .
    # :Sentence_f4b91c72-fb96 :text "Mary can visit her grandfather on Tuesday." .
    # :Sentence_f4b91c72-fb96 :mentions :Mary .
    # :Sentence_f4b91c72-fb96 :grade_level 3 .
    # :Narrative_foo :describes :NarrativeEvent_5fabc313-e1b5 .
    # :NarrativeEvent_5fabc313-e1b5 a :NarrativeEvent ; :offset 0 .
    # :NarrativeEvent_5fabc313-e1b5 :text "Mary can visit her grandfather on Tuesday." .
    # :NarrativeEvent_5fabc313-e1b5 :has_semantic :Event_d143c720-5ae0 .
    # :NarrativeEvent_5fabc313-e1b5 :has_first :Event_d143c720-5ae0 .
    # :Event_d143c720-5ae0 :text "Mary can visit her grandfather." .
    # Note that ReadinessAndAbility occurs twice - it is added via modal processing in case this is missed by OpenAI
    # :Event_d143c720-5ae0 a :ReadinessAndAbility ; :confidence-ReadinessAndAbility 95 .
    # :Event_d143c720-5ae0 a :MeetingAndEncounter ; :confidence-MeetingAndEncounter 100 .
    # :Event_d143c720-5ae0 a :ReadinessAndAbility ; :confidence-ReadinessAndAbility 90 .
    # :Event_d143c720-5ae0 :has_active_entity :Mary .
    # :Noun_721ef2e9-4115 a :Person ; :text "her grandfather" ; :confidence 95 .
    # :Event_d143c720-5ae0 :has_affected_entity :Noun_721ef2e9-4115 .
    # :NarrativeEvent_5fabc313-e1b5 :has_semantic :Event_e469b701-eb45 .
    # :Event_d143c720-5ae0 :has_next :Event_e469b701-eb45 .
    # :Event_e469b701-eb45 :text "The visit can happen on Tuesday." .
    # :Event_e469b701-eb45 a :ReadinessAndAbility ; :confidence-ReadinessAndAbility 95 .
    # :Event_e469b701-eb45 a :MeetingAndEncounter ; :confidence-MeetingAndEncounter 100 .
    # :Event_e469b701-eb45 a :ReadinessAndAbility ; :confidence-ReadinessAndAbility 90 .
    # :PiT_DayTuesday a :Time ; :text "Tuesday" .
    # :Event_e469b701-eb45 :has_time :PiT_DayTuesday .


def test_modal_neg():
    sentence_classes, quotation_classes = parse_narrative(text_modal_neg)
    graph_results = create_graph(sentence_classes, quotation_classes, text_modal_neg,
                                 ':Narrative_foo', [],5, repo)
    ttl_str = str(graph_results.turtle)
    assert (':MeetingAndEncounter' in ttl_str and ':negated-MeetingAndEncounter' in ttl_str) or \
        ':Avoidance' in ttl_str
    assert ':future true' in ttl_str
    assert ':has_active_entity :Mary' in ttl_str
    assert ':Person' in ttl_str and (':text "grandfather' in ttl_str or ':text "her grandfather' in ttl_str)
    assert ':has_affected_entity :Noun' in ttl_str
    assert ('a :Time ; :text "next Tuesday' in ttl_str or 'a :Time ; :text "Tuesday' in ttl_str) \
           and ':has_time' in ttl_str
    # Output Turtle:
    # :Narrative_foo :has_component :Sentence_28a58d7e-8021 .
    # :Sentence_28a58d7e-8021 a :Sentence ; :offset 1 .
    # :Sentence_28a58d7e-8021 :text "Mary will not visit her grandfather next Tuesday." .
    # :Sentence_28a58d7e-8021 :mentions :Mary .
    # :Sentence_28a58d7e-8021 :grade_level 5 .
    # :Narrative_foo :describes :NarrativeEvent_939504b7-61ab .
    # :NarrativeEvent_939504b7-61ab a :NarrativeEvent ; :offset 0
    # :NarrativeEvent_939504b7-61ab :text "Mary will not visit her grandfather next Tuesday." .
    # :NarrativeEvent_939504b7-61ab :has_semantic :Event_573ce468-ccc0 .
    # :NarrativeEvent_939504b7-61ab :has_first :Event_573ce468-ccc0 .
    # :Event_573ce468-ccc0 :text "Mary will not visit her grandfather next Tuesday." .
    # :Event_573ce468-ccc0 :future true .
    # :Event_573ce468-ccc0 a :Avoidance ; :confidence-Avoidance 90 .
    # :Event_573ce468-ccc0 a :MeetingAndEncounter ; :confidence-MeetingAndEncounter 85 .
    # :Event_573ce468-ccc0 :negated-MeetingAndEncounter true .
    # :Event_573ce468-ccc0 :has_active_entity :Mary .
    # :Noun_330de6de-a5b9 a :Person ; :text "her grandfather" ; :confidence 95 .
    # :Noun_330de6de-a5b9 :clarifying_text "her" .
    # :Event_573ce468-ccc0 :has_affected_entity :Noun_330de6de-a5b9 .
    # :PiT_DayTuesday a :Time ; :text "next Tuesday" .
    # :Event_573ce468-ccc0 :has_time :PiT_DayTuesday .   # TODO: Better time identification


def test_acomp():
    sentence_classes, quotation_classes = parse_narrative(text_acomp)
    graph_results = create_graph(sentence_classes, quotation_classes, text_acomp,
                                 ':Narrative_foo', [],5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':AttributeAndCharacteristic' in ttl_str
    assert ':has_context :Mary' in ttl_str
    # Output Turtle:
    # :Narrative_foo :has_component :Sentence_33ccea05-6e72 .
    # :Sentence_33ccea05-6e72 a :Sentence ; :offset 1 .
    # :Sentence_33ccea05-6e72 :text "Mary is very beautiful." .
    # :Sentence_33ccea05-6e72 :mentions :Mary .
    # :Sentence_33ccea05-6e72 :grade_level 3 .
    # :Sentence_33ccea05-6e72 :rhetorical_device "exceptionalism" .
    # :Sentence_33ccea05-6e72 :rhetorical_device_exceptionalism "The sentence uses language that indicates Mary is
    #     somehow unique or exemplary by stating she is \'very beautiful\', which can be seen as a form of
    #     exceptionalism." .
    # :Narrative_foo :describes :NarrativeEvent_f008756e-695b .
    # :NarrativeEvent_f008756e-695b a :NarrativeEvent ; :offset 0 .
    # :NarrativeEvent_f008756e-695b :text "Mary is described as very beautiful." .
    # :NarrativeEvent_f008756e-695b :has_semantic :Event_7336b8ff-4b9f .
    # :NarrativeEvent_f008756e-695b :has_first :Event_7336b8ff-4b9f .
    # :Event_7336b8ff-4b9f :text "Mary is described as very beautiful." .
    # :Event_7336b8ff-4b9f a :AttributeAndCharacteristic ; :confidence-AttributeAndCharacteristic 100 .
    # :Event_7336b8ff-4b9f a :AssessmentMeasurement ; :confidence-AssessmentMeasurement 80 .
    # :Event_7336b8ff-4b9f :has_context :Mary .


def test_acomp_pcomp1():
    sentence_classes, quotation_classes = parse_narrative(text_acomp_pcomp1)
    graph_results = create_graph(sentence_classes, quotation_classes, text_acomp_pcomp1,
                                 ':Narrative_foo', [],5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':EmotionalResponse' in ttl_str or ':SensoryPerception' in ttl_str
    assert ':BodilyAct' in ttl_str or ':MovementTravelAndTransportation' in ttl_str
    assert ':has_active_entity :Peter' in ttl_str
    # Output Turtle:
    # ::Narrative_foo :has_component :Sentence_60323636-2170 .
    # :Sentence_60323636-2170 a :Sentence ; :offset 1 .
    # :Sentence_60323636-2170 :text "Peter got tired of running." .
    # :Sentence_60323636-2170 :mentions :Peter .
    # :Sentence_60323636-2170 :grade_level 3 .
    # :Narrative_foo :describes :NarrativeEvent_8c067f47-16c6 .
    # :NarrativeEvent_8c067f47-16c6 a :NarrativeEvent ; :offset 0 .
    # :NarrativeEvent_8c067f47-16c6 :text "Peter got tired of running." .
    # :NarrativeEvent_8c067f47-16c6 :has_semantic :Event_552d59a1-308d .
    # :NarrativeEvent_8c067f47-16c6 :has_first :Event_552d59a1-308d .
    # :Event_552d59a1-308d :text "Peter got tired." .
    # :Event_552d59a1-308d a :SensoryPerception ; :confidence-SensoryPerception 100 .
    # :Event_552d59a1-308d a :DamageAndDifficulty ; :confidence-DamageAndDifficulty 80 .
    # :Event_552d59a1-308d :has_active_entity :Peter .
    # :NarrativeEvent_8c067f47-16c6 :has_semantic :Event_05319d07-a001 .
    # :Event_552d59a1-308d :has_next :Event_05319d07-a001 .
    # :Event_05319d07-a001 :text "Peter was running." .
    # :Event_05319d07-a001 a :BodilyAct ; :confidence-BodilyAct 100 .
    # :Event_05319d07-a001 a :MovementTravelAndTransportation ; :confidence-MovementTravelAndTransportation 90 .
    # :Event_05319d07-a001 :has_active_entity :Peter .


def test_acomp_pcomp2():
    sentence_classes, quotation_classes = parse_narrative(text_acomp_pcomp2)
    graph_results = create_graph(sentence_classes, quotation_classes, text_acomp_pcomp2,
                                 ':Narrative_foo', [],5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':Continuation' in ttl_str or ':SensoryPerception' in ttl_str
    assert ':BodilyAct' in ttl_str
    assert ':has_active_entity :Peter' in ttl_str
    # Output Turtle:
    # :Narrative_foo :has_component :Sentence_7f2657ab-8d6a .
    # :Sentence_7f2657ab-8d6a a :Sentence ; :offset 1 .
    # :Sentence_7f2657ab-8d6a :text "Peter never tires of running." .
    # :Sentence_7f2657ab-8d6a :mentions :Peter .
    # :Sentence_7f2657ab-8d6a :grade_level 5 .
    # :Narrative_foo :describes :NarrativeEvent_0fcef351-7ddc .
    # :NarrativeEvent_0fcef351-7ddc a :NarrativeEvent ; :offset 0 .
    # :NarrativeEvent_0fcef351-7ddc :text "Peter never tires of running." .
    # :NarrativeEvent_0fcef351-7ddc :has_semantic :Event_e2f45580-675a .
    # :NarrativeEvent_0fcef351-7ddc :has_first :Event_e2f45580-675a .
    # :Event_e2f45580-675a :text "Peter never tires." .
    # :Event_e2f45580-675a a :SensoryPerception ; :confidence-SensoryPerception 90 .
    # :Event_e2f45580-675a :negated-SensoryPerception true .     # TODO: Should not be negated
    # :Event_e2f45580-675a :has_active_entity :Peter .
    # :NarrativeEvent_0fcef351-7ddc :has_semantic :Event_16e29499-c873 .
    # :Event_e2f45580-675a :has_next :Event_16e29499-c873 .
    # :Event_16e29499-c873 :text "Peter runs." .
    # :Event_16e29499-c873 a :BodilyAct ; :confidence-BodilyAct 100 .
    # :Event_16e29499-c873 :has_active_entity :Peter .


def test_acomp_xcomp():
    sentence_classes, quotation_classes = parse_narrative(text_acomp_xcomp)
    graph_results = create_graph(sentence_classes, quotation_classes, text_acomp_xcomp,
                                 ':Narrative_foo', [],5, repo)
    ttl_str = str(graph_results.turtle)
    assert (':OpenMindednessAndTolerance' in ttl_str and ':negated-OpenMindednessAndTolerance' in ttl_str) or \
        ':Avoidance' in ttl_str
    assert ':HealthAndDiseaseRelated' in ttl_str or ':BodilyAct' in ttl_str
    assert ':text "smoking' in ttl_str
    assert ':has_active_entity :Jane' in ttl_str
    assert ':has_topic :Noun' in ttl_str
    # Output Turtle::Narrative_foo :has_component :Sentence_a1a7af1b-016b .
    # :Narrative_foo :has_component :Sentence_30254bd1-3b98 .
    # :Sentence_30254bd1-3b98 a :Sentence ; :offset 1 .
    # :Sentence_30254bd1-3b98 :text "Jane is unable to tolerate smoking." .
    # :Sentence_30254bd1-3b98 :mentions :Jane .
    # :Sentence_30254bd1-3b98 :grade_level 6 .
    # :Narrative_foo :describes :NarrativeEvent_28315c4a-c398 .
    # :NarrativeEvent_28315c4a-c398 a :NarrativeEvent ; :offset 0 .
    # :NarrativeEvent_28315c4a-c398 :text "Jane is unable to tolerate smoking." .
    # :NarrativeEvent_28315c4a-c398 :has_semantic :Event_32e9a747-686f .
    # :NarrativeEvent_28315c4a-c398 :has_first :Event_32e9a747-686f .
    # :Event_32e9a747-686f :text "Jane is unable to tolerate smoking." .
    # :Event_32e9a747-686f a :OpenMindednessAndTolerance ; :confidence-OpenMindednessAndTolerance 90 .
    # :Event_32e9a747-686f :negated-OpenMindednessAndTolerance true .
    # :Event_32e9a747-686f :has_active_entity :Jane .
    # :Noun_7ec26863-e941 a :BodilyAct, :Collection ; :text "smoking" ; :confidence 95 .
    # :Event_32e9a747-686f :has_topic :Noun_7ec26863-e941 .

def test_idiom():
    sentence_classes, quotation_classes = parse_narrative(text_idiom)
    graph_results = create_graph(sentence_classes, quotation_classes, text_idiom,
                                 ':Narrative_foo', [], 5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':Causation' in ttl_str and ':has_cause :Noun' in ttl_str
    assert ':Change' in ttl_str or ':DamageAndDifficulty' in ttl_str
    assert ':text "wear and tear' in ttl_str
    assert ':Location ; :text "bridge' in ttl_str
    assert ':has_location :Noun' in ttl_str
    # Output Turtle:
    # :Narrative_foo :has_component :Sentence_52da79a3-528b .
    # :Sentence_52da79a3-528b a :Sentence ; :offset 1 .
    # :Sentence_52da79a3-528b :text "Wear and tear on the bridge caused its collapse." .
    # :Sentence_52da79a3-528b :grade_level 8 .
    # :Narrative_foo :describes :NarrativeEvent_b3a30f66-cc8f .
    # :NarrativeEvent_b3a30f66-cc8f a :NarrativeEvent ; :offset 0 .
    # :NarrativeEvent_b3a30f66-cc8f :text "Wear and tear on the bridge caused its collapse." .
    # :NarrativeEvent_b3a30f66-cc8f :has_semantic :Event_603cd452-ec3f .
    # :NarrativeEvent_b3a30f66-cc8f :has_first :Event_603cd452-ec3f .
    # :Event_603cd452-ec3f :text "Wear and tear caused the collapse of the bridge." .
    # :Event_603cd452-ec3f a :Causation ; :confidence-Causation 100 .
    # :Event_603cd452-ec3f a :DamageAndDifficulty ; :confidence-DamageAndDifficulty 90 .
    # :Noun_1550924a-f06e a :DamageAndDifficulty, :Collection ; :text "wear and tear" ; :confidence 90 .
    # :Event_603cd452-ec3f :has_cause :Noun_1550924a-f06e .
    # :Noun_2b932658-23d1 a :DamageAndDifficulty ; :text "collapse" ; :confidence 85 .
    # :Event_603cd452-ec3f :has_topic :Noun_2b932658-23d1 .
    # :Noun_7dd17259-eac0 a :Location ; :text "bridge" ; :confidence 95 .
    # :Event_603cd452-ec3f :has_location :Noun_7dd17259-eac0 .


def test_idiom_full_pass():
    sentence_classes, quotation_classes = parse_narrative(text_idiom_full_pass)
    graph_results = create_graph(sentence_classes, quotation_classes, text_idiom_full_pass,
                                 ':Narrative_foo', [],5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':CommunicationAndSpeechAct' in ttl_str
    assert ':has_affected_entity :Jack' in ttl_str
    assert ':has_active_entity :George' in ttl_str
    assert ':CrimeAndHostileConflict' in ttl_str         # breaking and entering
    assert ':has_active_entity :Jack' in ttl_str or ':has_topic :Noun' in ttl_str
    # Output Turtle:
    # :Narrative_foo :has_component :Sentence_c499bf9d-445d .
    # :Sentence_c499bf9d-445d a :Sentence ; :offset 1 .
    # :Sentence_c499bf9d-445d :text "Jack was accused by George of breaking and entering." .
    # :Sentence_c499bf9d-445d :mentions :Jack .
    # :Sentence_c499bf9d-445d :mentions :George .
    # :Sentence_c499bf9d-445d :grade_level 8 .
    # :Sentence_c499bf9d-445d :rhetorical_device "rhetorical question or accusation" .
    # :Sentence_c499bf9d-445d :rhetorical_device_rhetorical_question_or_accusation "The sentence contains an implicit accusation, as George is accusing Jack of breaking and entering." .
    # :Narrative_foo :describes :NarrativeEvent_07c20641-df41 .
    # :NarrativeEvent_07c20641-df41 a :NarrativeEvent ; :offset 0 .
    # :NarrativeEvent_07c20641-df41 :text "Jack was accused by George of breaking and entering." .
    # :NarrativeEvent_07c20641-df41 :has_semantic :Event_67d77dbd-d6cf .
    # :NarrativeEvent_07c20641-df41 :has_first :Event_67d77dbd-d6cf .
    # :Event_67d77dbd-d6cf :text "George accused Jack of breaking and entering." .
    # :Event_67d77dbd-d6cf a :CommunicationAndSpeechAct ; :confidence-CommunicationAndSpeechAct 100 .
    # :Event_67d77dbd-d6cf :has_active_entity :George .
    # :Event_67d77dbd-d6cf :has_affected_entity :Jack .
    # :Noun_7ed4b630-5656 a :CrimeAndHostileConflict, :Collection ; :text "breaking and entering" ; :confidence 95 .
    # :Event_67d77dbd-d6cf :has_topic :Noun_7ed4b630-5656 .


def test_idiom_trunc_pass():
    sentence_classes, quotation_classes = parse_narrative(text_idiom_trunc_pass)
    graph_results = create_graph(sentence_classes, quotation_classes, text_idiom_trunc_pass,
                                 ':Narrative_foo', [],5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':CommunicationAndSpeechAct' in ttl_str
    assert ':has_affected_entity :Jack' in ttl_str
    assert ':CrimeAndHostileConflict' in ttl_str
    assert ':has_active_entity :Jack' in ttl_str or ':has_topic :Noun' in ttl_str
    # Output Turtle:
    # :Narrative_foo :has_component :Sentence_7b72e3d0-ba25 .
    # :Sentence_7b72e3d0-ba25 a :Sentence ; :offset 1 .
    # :Sentence_7b72e3d0-ba25 :text "Jack was accused of breaking and entering." .
    # :Sentence_7b72e3d0-ba25 :mentions :Jack .
    # :Sentence_7b72e3d0-ba25 :grade_level 8 .
    # :Narrative_foo :describes :NarrativeEvent_a434e975-d875 .
    # :NarrativeEvent_a434e975-d875 a :NarrativeEvent ; :offset 0 .
    # :NarrativeEvent_a434e975-d875 :text "Jack was accused of breaking and entering." .
    # :NarrativeEvent_a434e975-d875 :has_semantic :Event_6c32150c-082b .
    # :NarrativeEvent_a434e975-d875 :has_first :Event_6c32150c-082b .
    # :Event_6c32150c-082b :text "Someone accused Jack of breaking and entering." .
    # :Event_6c32150c-082b a :CommunicationAndSpeechAct ; :confidence-CommunicationAndSpeechAct 100 .
    # :Event_6c32150c-082b a :CrimeAndHostileConflict ; :confidence-CrimeAndHostileConflict 90 .
    # :Event_6c32150c-082b :has_affected_entity :Jack .
    # :Noun_e760c66e-0e2f a :CrimeAndHostileConflict, :Collection ; :text "breaking and entering" ; :confidence 95 .
    # :Event_6c32150c-082b :has_topic :Noun_e760c66e-0e2f .


def test_negation_emotion():
    sentence_classes, quotation_classes = parse_narrative(text_negative_emotion)
    graph_results = create_graph(sentence_classes, quotation_classes, text_negative_emotion,
                                 ':Narrative_foo', [],5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':EmotionalResponse' in ttl_str
    assert ':has_active_entity :Jane' in ttl_str
    assert ':Plant ; :text "broccoli' in ttl_str
    assert ':has_topic :Noun' in ttl_str
    # Output Turtle:
    # :Narrative_foo :has_component :Sentence_ec4e9da3-6ce4 .
    # :Sentence_ec4e9da3-6ce4 a :Sentence ; :offset 1 .
    # :Sentence_ec4e9da3-6ce4 :text "Jane has no liking for broccoli." .
    # :Sentence_ec4e9da3-6ce4 :mentions :Jane .
    # :Sentence_ec4e9da3-6ce4 :grade_level 4 .
    # :Narrative_foo :describes :NarrativeEvent_e97f2fce-12dc .
    # :NarrativeEvent_e97f2fce-12dc a :NarrativeEvent ; :offset 0 .
    # :NarrativeEvent_e97f2fce-12dc :text "Jane has no liking for broccoli." .
    # :NarrativeEvent_e97f2fce-12dc :has_semantic :Event_bf6c8588-0a98 .
    # :NarrativeEvent_e97f2fce-12dc :has_first :Event_bf6c8588-0a98 .
    # :Event_bf6c8588-0a98 :text "Jane dislikes broccoli." .
    # :Event_bf6c8588-0a98 a :EmotionalResponse ; :confidence-EmotionalResponse 100 .
    # :Event_bf6c8588-0a98 :has_active_entity :Jane .
    # :Noun_a7d1e2fd-3ddf a :Plant ; :text "broccoli" ; :confidence 100 .
    # :Event_bf6c8588-0a98 :has_topic :Noun_a7d1e2fd-3ddf .


def test_negation():
    sentence_classes, quotation_classes = parse_narrative(text_negation)
    graph_results = create_graph(sentence_classes, quotation_classes, text_negation,
                                 ':Narrative_foo', [],5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':CrimeAndHostileConflict' in ttl_str and ':negated-CrimeAndHostileConflict' in ttl_str
    assert ':has_active_entity :Jane' in ttl_str
    assert ':has_affected_entity :Jack' in ttl_str
    # Output Turtle:
    # :Narrative_foo :has_component :Sentence_2ed4d0a0-9054 .
    # :Sentence_2ed4d0a0-9054 a :Sentence ; :offset 1 .
    # :Sentence_2ed4d0a0-9054 :text "Jane did not stab Jack." .
    # :Sentence_2ed4d0a0-9054 :mentions :Jane .
    # :Sentence_2ed4d0a0-9054 :mentions :Jack .
    # :Sentence_2ed4d0a0-9054 :grade_level 4 .
    # :Narrative_foo :describes :NarrativeEvent_edc2a122-3bb2 .
    # :NarrativeEvent_edc2a122-3bb2 a :NarrativeEvent ; :offset 0 .
    # :NarrativeEvent_edc2a122-3bb2 :text "Jane did not stab Jack." .
    # :NarrativeEvent_edc2a122-3bb2 :has_semantic :Event_f4a6b449-b341 .
    # :NarrativeEvent_edc2a122-3bb2 :has_first :Event_f4a6b449-b341 .
    # :Event_f4a6b449-b341 :text "Jane did not stab Jack." .
    # :Event_f4a6b449-b341 a :CrimeAndHostileConflict ; :confidence-CrimeAndHostileConflict 100 .
    # :Event_f4a6b449-b341 :negated-CrimeAndHostileConflict true .
    # :Event_f4a6b449-b341 :has_active_entity :Jane .
    # :Event_f4a6b449-b341 :has_affected_entity :Jack .


def test_mention():
    sentence_classes, quotation_classes = parse_narrative(text_mention)
    graph_results = create_graph(sentence_classes, quotation_classes, text_mention,
                                 ':Narrative_foo', [],5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':mentions :FBI' in ttl_str
    assert ':LawEnforcement' in ttl_str
    assert ':has_active_entity :FBI' in ttl_str
    assert (':BuildingAndDwelling' in ttl_str or ':Location' in ttl_str) and ':text "house' in ttl_str
    assert ':has_location :Noun' in ttl_str
    # Output Turtle:
    # :Narrative_foo :has_component :Sentence_598c5f53-9600 .
    # :Sentence_598c5f53-9600 a :Sentence ; :offset 1 .
    # :Sentence_598c5f53-9600 :text "The FBI raided the house." .
    # :Sentence_598c5f53-9600 :mentions :FBI .
    # :Sentence_598c5f53-9600 :grade_level 6 .
    # :Narrative_foo :describes :NarrativeEvent_d15c1773-d77c .
    # :NarrativeEvent_d15c1773-d77c a :NarrativeEvent ; :offset 0 .
    # :NarrativeEvent_d15c1773-d77c :text "The FBI raided the house." .
    # :NarrativeEvent_d15c1773-d77c :has_semantic :Event_4d9a6577-a5be .
    # :NarrativeEvent_d15c1773-d77c :has_first :Event_4d9a6577-a5be .
    # :Event_4d9a6577-a5be :text "The FBI raided the house." .
    # :Event_4d9a6577-a5be a :AcquisitionPossessionAndTransfer ; :confidence-AcquisitionPossessionAndTransfer 90 .
    # :Event_4d9a6577-a5be a :LawEnforcement ; :confidence-LawEnforcement 95 .
    # :Event_4d9a6577-a5be :has_active_entity :FBI .
    # :Noun_e92c4d98-a64a a :Location ; :text "house" ; :confidence 95 .
    # :Event_4d9a6577-a5be :has_location :Noun_e92c4d98-a64a .


def test_hyphenation():
    sentence_classes, quotation_classes = parse_narrative(text_hyphenation)
    graph_results = create_graph(sentence_classes, quotation_classes, text_hyphenation,
                                 ':Narrative_foo', [],5, repo)
    ttl_str = str(graph_results.turtle)
    assert (':mentions :Joe_Biden' in ttl_str or ':mentions :Biden' in ttl_str) and \
        ':mentions :Kamala_Harris' in ttl_str and ':mentions :Nancy_Smith_Evans' in ttl_str
    assert ':mentions :Biden-Harris' not in ttl_str
    assert ':Process, :Collection ; :text "Biden-Harris campaign' in ttl_str or \
        ':PoliticsRelated, :Collection ; :text "Biden-Harris campaign' in ttl_str
    assert ':DamageAndDifficulty, :Collection ; :text "setbacks"' in ttl_str or \
        ':Loss, :Collection ; :text "setbacks"' in ttl_str or ':DelayAndWait, :Collection ; :text "setbacks' in ttl_str
    assert ':has_topic :Noun' in ttl_str and ':has_context :Noun' in ttl_str
    assert ':affiliated_with :Kamala_Harris' in ttl_str
    # Output Turtle:
    # :Narrative_foo :has_component :Sentence_91aa2be1-9aca .
    # :Sentence_91aa2be1-9aca a :Sentence ; :offset 1 .
    # :Sentence_91aa2be1-9aca :text "Joe Biden and Kamala Harris were running on the Democratic ticket in 2024." .
    # :Sentence_91aa2be1-9aca :mentions :Joe_Biden .
    # :Sentence_91aa2be1-9aca :mentions :Kamala_Harris .
    # :Sentence_91aa2be1-9aca :mentions :Democratic .
    # :Sentence_91aa2be1-9aca :grade_level 8 .
    # :Narrative_foo :has_component :Sentence_563d1074-36b8 .
    # :Sentence_563d1074-36b8 a :Sentence ; :offset 2 .
    # :Sentence_563d1074-36b8 :text "The Biden-Harris campaign suffered serious setbacks." .
    # :Sentence_563d1074-36b8 :mentions :Joe_Biden .
    # :Sentence_563d1074-36b8 :mentions :Kamala_Harris .
    # :Sentence_563d1074-36b8 :grade_level 8 .
    # :Narrative_foo :has_component :Sentence_143955db-dc61 .
    # :Sentence_143955db-dc61 a :Sentence ; :offset 3 .
    # :Sentence_143955db-dc61 :text "Nancy Smith-Evans reported on this." .
    # :Sentence_143955db-dc61 :mentions :Nancy_Smith_Evans .
    # :Sentence_143955db-dc61 :grade_level 5 .
    # :Narrative_foo :has_component :Sentence_da809b0c-283a .
    # :Sentence_da809b0c-283a a :Sentence ; :offset 4 .
    # :Sentence_da809b0c-283a :text "Smith-Evans is a friend of Harris." .
    # :Sentence_da809b0c-283a :mentions :Nancy_Smith_Evans .
    # :Sentence_da809b0c-283a :mentions :Kamala_Harris .
    # :Sentence_da809b0c-283a :grade_level 3 .
    # :Narrative_foo :describes :NarrativeEvent_5d2e9163-d477 .
    # :NarrativeEvent_5d2e9163-d477 a :NarrativeEvent ; :offset 0 .
    # :NarrativeEvent_5d2e9163-d477 :text "Joe Biden and Kamala Harris were running on the Democratic ticket in 2024." .
    # :NarrativeEvent_5d2e9163-d477 :has_semantic :Event_6642569e-db2b .
    # :NarrativeEvent_5d2e9163-d477 :has_first :Event_6642569e-db2b .
    # :Event_6642569e-db2b :text "Joe Biden was running on the Democratic ticket in 2024." .
    # :Event_6642569e-db2b a :PoliticsRelated ; :confidence-PoliticsRelated 100 .
    # :Event_6642569e-db2b :has_active_entity :Joe_Biden .
    # :Noun_ae85ee2f-d96c a :PoliticalGroup, :Collection ; :text "Democratic ticket" ; :confidence 90 .
    # :Event_6642569e-db2b :has_topic :Noun_ae85ee2f-d96c .
    # :PiT_Yr2024 a :Time ; :text "2024" .
    # :Event_6642569e-db2b :has_time :PiT_Yr2024 .
    # :NarrativeEvent_5d2e9163-d477 :has_semantic :Event_8602a310-9949 .
    # :Event_6642569e-db2b :has_next :Event_8602a310-9949 .
    # :Event_8602a310-9949 :text "Kamala Harris was running on the Democratic ticket in 2024." .
    # :Event_8602a310-9949 a :PoliticsRelated ; :confidence-PoliticsRelated 100 .
    # :Event_8602a310-9949 :has_active_entity :Kamala_Harris .
    # :Event_8602a310-9949 :has_topic :Noun_ae85ee2f-d96c .
    # :PiT_Yr2024 a :Time ; :text "2024" .
    # :Event_8602a310-9949 :has_time :PiT_Yr2024 .
    # :Narrative_foo :describes :NarrativeEvent_ac0f3844-321d .
    # :NarrativeEvent_ac0f3844-321d a :NarrativeEvent ; :offset 1 .
    # :NarrativeEvent_ac0f3844-321d :text "The Biden-Harris campaign suffered serious setbacks." .
    # :NarrativeEvent_ac0f3844-321d :has_semantic :Event_1abca758-903b .
    # :NarrativeEvent_ac0f3844-321d :has_first :Event_1abca758-903b .
    # :Event_1abca758-903b :text "The Biden-Harris campaign suffered setbacks." .
    # :Event_1abca758-903b a :Loss ; :confidence-Loss 100 .
    # TODO: Biden-Harris as clarifying text
    # :Noun_482fd955-9b53 a :Process, :Collection ; :text "Biden-Harris campaign" ; :confidence 90 .
    # :Event_1abca758-903b :has_active_entity :Noun_482fd955-9b53 .
    # :Noun_9ae9c0ed-f3a6 a :Loss, :Collection ; :text "setbacks" ; :confidence 85 .
    # :Event_1abca758-903b :has_affected_entity :Noun_9ae9c0ed-f3a6 .
    # :NarrativeEvent_ac0f3844-321d :has_semantic :Event_8cfd3af9-dff4 .
    # :Event_1abca758-903b :has_next :Event_8cfd3af9-dff4 .
    # :Event_8cfd3af9-dff4 :text "The setbacks were serious." .
    # :Event_8cfd3af9-dff4 a :AttributeAndCharacteristic ; :confidence-AttributeAndCharacteristic 100 .
    # :Event_8cfd3af9-dff4 :has_context :Noun_9ae9c0ed-f3a6 .
    # :Narrative_foo :describes :NarrativeEvent_e4c7cc2c-06b2 .
    # :NarrativeEvent_e4c7cc2c-06b2 a :NarrativeEvent ; :offset 2 .
    # :NarrativeEvent_e4c7cc2c-06b2 :text "Nancy Smith-Evans reported on the setbacks." .
    # :NarrativeEvent_e4c7cc2c-06b2 :has_semantic :Event_27840569-fbc0 .
    # :NarrativeEvent_e4c7cc2c-06b2 :has_first :Event_27840569-fbc0 .
    # :Event_27840569-fbc0 :text "Nancy Smith-Evans reported on the setbacks." .
    # :Event_27840569-fbc0 a :CommunicationAndSpeechAct ; :confidence-CommunicationAndSpeechAct 100 .
    # :Event_27840569-fbc0 :has_active_entity :Nancy_Smith_Evans .
    # :Event_27840569-fbc0 :has_topic :Noun_9ae9c0ed-f3a6 .
    # :Narrative_foo :describes :NarrativeEvent_172970d5-199f .
    # :NarrativeEvent_172970d5-199f a :NarrativeEvent ; :offset 3 .
    # :NarrativeEvent_172970d5-199f :text "Nancy Smith-Evans is a friend of Kamala Harris." .
    # :NarrativeEvent_172970d5-199f :has_semantic :Event_8206fe32-5695 .
    # :NarrativeEvent_172970d5-199f :has_first :Event_8206fe32-5695 .
    # :Event_8206fe32-5695 :text "Nancy Smith-Evans is a friend of Kamala Harris." .
    # :Event_8206fe32-5695 a :Affiliation ; :confidence-Affiliation 100 .
    # :Event_8206fe32-5695 :has_context :Nancy_Smith_Evans .
    # :Noun_1bde0d91-3d1e a :Person ; :text "friend" ; :confidence 95 .
    # :Event_8206fe32-5695 :affiliated_with :Noun_1bde0d91-3d1e .
    # :Event_8206fe32-5695 :affiliated_with :Kamala_Harris .
