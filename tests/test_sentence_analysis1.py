import pytest
from dna.create_narrative_turtle import create_graph
from dna.nlp import parse_narrative

# Latest execution, Dec 15: No failures

text_clauses1 = 'While Mary exercised, John practiced guitar.'
text_clauses2 = 'George agreed with the plan that Mary outlined.'
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
text_acomp_pcomp1 = 'Peter got tired of running.'
text_acomp_pcomp2 = 'Peter never tires of running.'
text_acomp_xcomp = 'Jane is unable to tolerate smoking.'
text_idiom = 'Wear and tear on the bridge caused its collapse.'
text_idiom_full_pass = 'John was accused by George of breaking and entering.'
text_idiom_trunc_pass = 'John was accused of breaking and entering.'
text_negative_emotion = 'Jane has no liking for broccoli.'
text_negation = 'Jane did not stab John.'
text_mention = 'The FBI raided the house.'

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
    assert ':has_active_entity :John' in ttl_str
    assert ':BodilyAct' in ttl_str                          # exercise
    assert ':ArtAndEntertainmentEvent' in ttl_str or ':EducationRelated' in ttl_str       # practice
    assert ':EducationRelated' in ttl_str
    assert ':MusicalInstrument ; :text "guitar' in ttl_str and ':has_topic :Noun' in ttl_str
    # Output Turtle:
    # :Narrative_foo :has_component :Sentence_32e1de15-8321 .
    # :Sentence_32e1de15-8321 a :Sentence ; :offset 1 .
    # :Sentence_32e1de15-8321 :text "While Mary exercised, John practiced guitar." .
    # :Sentence_32e1de15-8321 :mentions :Mary .
    # :Sentence_32e1de15-8321 :mentions :John .
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
    # :NarrativeEvent_904574fe-a15d :text "John practiced guitar." .
    # :NarrativeEvent_904574fe-a15d :has_semantic :Event_f813886d-789e .
    # :NarrativeEvent_904574fe-a15d :has_first :Event_f813886d-789e .
    # :Event_f813886d-789e :text "John practiced guitar." .
    # :Event_f813886d-789e a :ArtAndEntertainmentEvent ; :confidence-ArtAndEntertainmentEvent 90 .
    # :Event_f813886d-789e a :EducationRelated ; :confidence-EducationRelated 85 .
    # :Event_f813886d-789e :has_active_entity :John .
    # :Noun_c7a0f4bf-c238 a :MusicalInstrument ; :text "guitar" ; :confidence 100 .
    # :Event_f813886d-789e :has_topic :Noun_c7a0f4bf-c238 .


def test_clauses2():
    sentence_classes, quotation_classes = parse_narrative(text_clauses2)
    graph_results = create_graph(sentence_classes, quotation_classes, text_clauses2,
                                 ':Narrative_foo', [],5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':has_active_entity :George' in ttl_str
    assert ':Agreement' in ttl_str
    assert ':Process ; :text "plan' in ttl_str
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
    assert ':has_context :Joe' in ttl_str
    assert ':LineOfBusiness ; :text "attorney' in ttl_str    # attorney
    assert ':has_aspect :Noun' in ttl_str
    # Output Turtle:
    # :Narrative_foo :has_component :Sentence_e66413e5-71b2 .
    # :Sentence_e66413e5-71b2 a :Sentence ; :offset 1 .
    # :Sentence_e66413e5-71b2 :text "Joe is an attorney." .
    # :Sentence_e66413e5-71b2 :mentions :Joe .
    # :Sentence_e66413e5-71b2 :grade_level 3 .
    # :Narrative_foo :describes :NarrativeEvent_14acf00e-0d3e .
    # :NarrativeEvent_14acf00e-0d3e a :NarrativeEvent ; :offset 0 .
    # :NarrativeEvent_14acf00e-0d3e :text "Joe is an attorney." .
    # :NarrativeEvent_14acf00e-0d3e :has_semantic :Event_ad7e4896-364d .
    # :NarrativeEvent_14acf00e-0d3e :has_first :Event_ad7e4896-364d .
    # :Event_ad7e4896-364d :text "Joe is an attorney." .
    # :Event_ad7e4896-364d a :AttributeAndCharacteristic ; :confidence-AttributeAndCharacteristic 100 .
    # :Event_ad7e4896-364d :has_context :Joe .
    # :Noun_afd3bdfd-e82d a :LineOfBusiness ; :text "attorney" ; :confidence 95 .
    # :Event_ad7e4896-364d :has_aspect :Noun_afd3bdfd-e82d .


def test_affiliation():
    sentence_classes, quotation_classes = parse_narrative(text_affiliation)
    graph_results = create_graph(sentence_classes, quotation_classes, text_affiliation,
                                 ':Narrative_foo', [],5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':Affiliation' in ttl_str
    assert ':has_context :Joe' in ttl_str
    assert ':affiliated_with :Mayberry_' in ttl_str
    # Output Turtle:
    # :Narrative_foo :has_component :Sentence_0678465c-ac20 .
    # :Sentence_0678465c-ac20 a :Sentence ; :offset 1 .
    # :Sentence_0678465c-ac20 :text "Joe is a member of the Mayberry Book Club." .
    # :Sentence_0678465c-ac20 :mentions :Joe .
    # :Sentence_0678465c-ac20 :mentions :Mayberry_Book_Club .
    # :Sentence_0678465c-ac20 :grade_level 3 .
    # :Narrative_foo :describes :NarrativeEvent_5dc3c653-1812 .
    # :NarrativeEvent_5dc3c653-1812 a :NarrativeEvent ; :offset 0 .
    # :NarrativeEvent_5dc3c653-1812 :text "Joe is a member of the Mayberry Book Club." .
    # :NarrativeEvent_5dc3c653-1812 :has_semantic :Event_1a907f11-72d3 .
    # :NarrativeEvent_5dc3c653-1812 :has_first :Event_1a907f11-72d3 .
    # :Event_1a907f11-72d3 :text "Joe is a member of the Mayberry Book Club." .
    # :Event_1a907f11-72d3 a :Affiliation ; :confidence-Affiliation 100 .
    # :Event_1a907f11-72d3 a :AttributeAndCharacteristic ; :confidence-AttributeAndCharacteristic 90 .
    # :Event_1a907f11-72d3 :has_context :Joe .
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
    # TODO: Endorsement should be captured
    # assert ':affiliated_with :Harriet_Hageman' in ttl_str
    # assert ':has_active_agent :Donald_Trump' in ttl_str or ':has_context :Donald_Trump' in ttl_str or \
    #        ':has_active_agent :Trump' in ttl_str or ':has_context :Trump' in ttl_str
    #
    # Output Turtle:
    # :Narrative_foo :has_component :Sentence_11b1a7d7-7156 .
    # :Sentence_11b1a7d7-7156 a :Sentence ; :offset 1 .
    # :Sentence_11b1a7d7-7156 :text "Rep. Liz Cheney R-WY compared herself to former President Abraham Lincoln during
    #     her concession speech shortly after her loss to Trump-backed Republican challenger Harriet Hageman." .
    # :Sentence_11b1a7d7-7156 :mentions :Liz_Cheney .
    # :Sentence_11b1a7d7-7156 :mentions :Wyoming .
    # :Sentence_11b1a7d7-7156 :mentions :Abraham_Lincoln .
    # :Sentence_11b1a7d7-7156 :mentions :Donald_Trump .
    # :Sentence_11b1a7d7-7156 :mentions :Republican .
    # :Sentence_11b1a7d7-7156 :mentions :Harriet_Hageman .
    # :Sentence_11b1a7d7-7156 :grade_level 10 .
    # :Sentence_11b1a7d7-7156 :rhetorical_device "allusion" .
    # :Sentence_11b1a7d7-7156 :rhetorical_device_allusion "The sentence contains an allusion, as it references former
    #     President Abraham Lincoln, a historical figure with symbolic meaning." .
    # :Narrative_foo :describes :NarrativeEvent_c5835ccd-d4e4 .
    # :NarrativeEvent_c5835ccd-d4e4 a :NarrativeEvent ; :offset 0 .
    # :NarrativeEvent_c5835ccd-d4e4 :text "Rep. Liz Cheney compared herself to former President Abraham Lincoln
    #     during her concession speech." .
    # :NarrativeEvent_c5835ccd-d4e4 :has_semantic :Event_1e1b9393-7c9b .
    # :NarrativeEvent_c5835ccd-d4e4 :has_first :Event_1e1b9393-7c9b .
    # :Event_1e1b9393-7c9b :text "Rep. Liz Cheney compared Rep. Liz Cheney to former President Abraham Lincoln." .
    # :Event_1e1b9393-7c9b a :Cognition ; :confidence-Cognition 90 .
    # :Event_1e1b9393-7c9b a :AttributeAndCharacteristic ; :confidence-AttributeAndCharacteristic 85 .
    # :Event_1e1b9393-7c9b :has_context :Liz_Cheney .
    # :Event_1e1b9393-7c9b :has_topic :Abraham_Lincoln .
    # :NarrativeEvent_c5835ccd-d4e4 :has_semantic :Event_593c8db1-401d .
    # :Event_1e1b9393-7c9b :has_next :Event_593c8db1-401d .
    # :Event_593c8db1-401d :text "Rep. Liz Cheney made a concession speech." .
    # :Event_593c8db1-401d a :CommunicationAndSpeechAct ; :confidence-CommunicationAndSpeechAct 95 .
    # :Event_593c8db1-401d a :Loss ; :confidence-Loss 90 .
    # :Event_593c8db1-401d :has_active_entity :Liz_Cheney .
    # :Narrative_foo :describes :NarrativeEvent_282ca46a-da76 .
    # NarrativeEvent_282ca46a-da76 a :NarrativeEvent ; :offset 1 .
    # :NarrativeEvent_282ca46a-da76 :text "Rep. Liz Cheney delivered her concession speech shortly after her loss to
    #     Trump-backed Republican challenger Harriet Hageman." .
    # :NarrativeEvent_282ca46a-da76 :has_semantic :Event_14ead286-5eb2 .
    # :NarrativeEvent_282ca46a-da76 :has_first :Event_14ead286-5eb2 .
    # :Event_14ead286-5eb2 :text "Rep. Liz Cheney delivered her concession speech." .
    # :Event_14ead286-5eb2 a :CommunicationAndSpeechAct ; :confidence-CommunicationAndSpeechAct 95 .
    # :Event_14ead286-5eb2 a :PoliticsRelated ; :confidence-PoliticsRelated 85 .
    # :Event_14ead286-5eb2 :has_active_entity :Liz_Cheney .
    # :Noun_33db6723-d66c a :CommunicationAndSpeechAct, :Collection ; :text "concession speech" ; :confidence 95 .
    # :Event_14ead286-5eb2 :has_topic :Noun_33db6723-d66c .
    # :NarrativeEvent_282ca46a-da76 :has_semantic :Event_05eaeb7f-3660 .
    # :Event_14ead286-5eb2 :has_next :Event_05eaeb7f-3660 .
    # :Event_05eaeb7f-3660 :text "Rep. Liz Cheney lost to Trump-backed Republican challenger Harriet Hageman." .
    # :Event_05eaeb7f-3660 a :Loss ; :confidence-Loss 100 .
    # :Event_05eaeb7f-3660 a :PoliticsRelated ; :confidence-PoliticsRelated 90 .
    # :Event_05eaeb7f-3660 :has_active_entity :Liz_Cheney .
    # :Event_05eaeb7f-3660 :has_affected_entity :Harriet_Hageman .


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
    assert ':Measurement' in ttl_str and ':has_quantification :Noun' in ttl_str      # percentages and/or votes counted
    # Output Turtle:
    # :Narrative_foo :has_component :Sentence_2ed32b16-eb50 .
    # :Sentence_2ed32b16-eb50 a :Sentence ; :offset 1 .
    # :Sentence_2ed32b16-eb50 :text "Harriet Hageman, a water and natural-resources attorney who was endorsed by the
    #     former president, won 66.3% of the vote to Ms. Cheney’s 28.9%, with 95% of all votes counted." .
    # :Sentence_2ed32b16-eb50 :mentions :Harriet_Hageman .
    # :Sentence_2ed32b16-eb50 :mentions :Liz_Cheney .
    # :Sentence_2ed32b16-eb50 :grade_level 10 .
    # :Sentence_2ed32b16-eb50 :rhetorical_device "logos" .
    # :Sentence_2ed32b16-eb50 :rhetorical_device_logos "The sentence uses statistics and numbers, such as \'66.3%\',
    #     \'28.9%\', and \'95%\', to convey the election results, which is an appeal to logic and reason (logos)." .
    # :Narrative_foo :describes :NarrativeEvent_20ec1e7e-536d .
    # :NarrativeEvent_20ec1e7e-536d a :NarrativeEvent ; :offset 0 .
    # :NarrativeEvent_20ec1e7e-536d :text "Harriet Hageman, a water and natural-resources attorney endorsed by the
    #     former president, won 66.3% of the vote." .
    # :NarrativeEvent_20ec1e7e-536d :has_semantic :Event_a05b052c-17f0 .
    # :NarrativeEvent_20ec1e7e-536d :has_first :Event_a05b052c-17f0 .
    # :Event_a05b052c-17f0 :text "Harriet Hageman is a water and natural-resources attorney." .
    # :Event_a05b052c-17f0 a :AttributeAndCharacteristic ; :confidence-AttributeAndCharacteristic 100 .
    # :Event_a05b052c-17f0 :has_context :Harriet_Hageman .
    # :Noun_29e89602-0f28 a :LineOfBusiness ; :text "water and natural-resources attorney" ; :confidence 95 .
    # :Event_a05b052c-17f0 :has_aspect :Noun_29e89602-0f28 .
    # :NarrativeEvent_20ec1e7e-536d :has_semantic :Event_9607bd36-e54f .
    # :Event_a05b052c-17f0 :has_next :Event_9607bd36-e54f .
    # :Event_9607bd36-e54f :text "The former president endorsed Harriet Hageman." .
    # :Event_9607bd36-e54f a :Affiliation ; :confidence-Affiliation 90 .
    # :Event_9607bd36-e54f a :CommunicationAndSpeechAct ; :confidence-CommunicationAndSpeechAct 85 .
    # :Noun_9b241cb2-6629 a :LineOfBusiness ; :text "former president" ; :confidence 95 .
    # :Event_9607bd36-e54f :has_context :Noun_9b241cb2-6629 .
    # :Event_9607bd36-e54f :affiliated_with :Harriet_Hageman .
    # :NarrativeEvent_20ec1e7e-536d :has_semantic :Event_6f1a51bc-b527 .
    # :Event_9607bd36-e54f :has_next :Event_6f1a51bc-b527 .
    # :Event_6f1a51bc-b527 :text "Harriet Hageman won 66.3% of the vote." .
    # :Event_6f1a51bc-b527 a :Win ; :confidence-Win 100 .
    # :Event_6f1a51bc-b527 a :PoliticsRelated ; :confidence-PoliticsRelated 95 .
    # :Event_6f1a51bc-b527 :has_active_entity :Harriet_Hageman .
    # :Noun_ae3ac77f-d130 a :Measurement, :Collection ; :text "66.3% of the vote" ; :confidence 90 .
    # :Noun_ae3ac77f-d130 :clarifying_reference :Noun_ae3ac77f-d130 .
    # :Noun_ae3ac77f-d130 :clarifying_text "of the vote" .
    # :Event_6f1a51bc-b527 :has_quantification :Noun_ae3ac77f-d130 .
    # :Narrative_foo :describes :NarrativeEvent_fdb0c998-5355 .
    # :NarrativeEvent_fdb0c998-5355 a :NarrativeEvent ; :offset 1 .
    # :NarrativeEvent_fdb0c998-5355 :text "Ms. Cheney received 28.9% of the vote." .
    # :NarrativeEvent_fdb0c998-5355 :has_semantic :Event_430f3481-4f17 .
    # :NarrativeEvent_fdb0c998-5355 :has_first :Event_430f3481-4f17 .
    # :Event_430f3481-4f17 :text "Ms. Cheney received 28.9% of the vote." .
    # :Event_430f3481-4f17 a :Measurement ; :confidence-Measurement 90 .
    # :Event_430f3481-4f17 a :Loss ; :confidence-Loss 85 .
    # :Event_430f3481-4f17 :has_context :Liz_Cheney .
    # :Narrative_foo :describes :NarrativeEvent_5bb965a1-2d00 .
    # :NarrativeEvent_5bb965a1-2d00 a :NarrativeEvent ; :offset 2 .
    # :NarrativeEvent_5bb965a1-2d00 :text "95% of all votes were counted." .
    # :NarrativeEvent_5bb965a1-2d00 :has_semantic :Event_2a173b79-0b96 .
    # :NarrativeEvent_5bb965a1-2d00 :has_first :Event_2a173b79-0b96 .
    # :Event_2a173b79-0b96 :text "95% of all votes were counted." .
    # :Event_2a173b79-0b96 a :Measurement ; :confidence-Measurement 95 .
    # :Event_2a173b79-0b96 a :PoliticsRelated ; :confidence-PoliticsRelated 85 .
    # :Noun_ca096f7b-401e a :PoliticsRelated, :Collection ; :text "votes" ; :confidence 90 .
    # :Event_2a173b79-0b96 :has_context :Noun_ca096f7b-401e .


def test_coref():
    sentence_classes, quotation_classes = parse_narrative(text_coref)
    graph_results = create_graph(sentence_classes, quotation_classes, text_coref,
                                 ':Narrative_foo',[],5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':HealthAndDiseaseRelated' in ttl_str
    assert ':has_active_entity :Joe' in ttl_str
    assert ':ComponentPart ; :text "foot' in ttl_str               # Joe's foot
    assert ':has_affected_entity :Noun' in ttl_str
    assert ':MovementTravelAndTransportation' in ttl_str
    assert ':LineOfBusiness ; :text "doctor' in ttl_str and ':has_destination :Noun' in ttl_str
    # Output Turtle:
    # :Narrative_foo :has_component :Sentence_f3d61fe7-cc26 .
    # :Sentence_f3d61fe7-cc26 a :Sentence ; :offset 1 .
    # :Sentence_f3d61fe7-cc26 :text "Joe broke his foot." .
    # :Sentence_f3d61fe7-cc26 :mentions :Joe .
    # :Sentence_f3d61fe7-cc26 :grade_level 3 .
    # :Narrative_foo :has_component :Sentence_f008e240-c814 .
    # :Sentence_f008e240-c814 a :Sentence ; :offset 2 .
    # :Sentence_f008e240-c814 :text "He went to the doctor." .
    # :Sentence_f008e240-c814 :grade_level 3 .
    # :Narrative_foo :describes :NarrativeEvent_bb29b3c6-9349 .
    # :NarrativeEvent_bb29b3c6-9349 a :NarrativeEvent ; :offset 0 .
    # :NarrativeEvent_bb29b3c6-9349 :text "Joe broke his foot." .
    # :NarrativeEvent_bb29b3c6-9349 :has_semantic :Event_dbcbc507-4b14 .
    # :NarrativeEvent_bb29b3c6-9349 :has_first :Event_dbcbc507-4b14 .
    # :Event_dbcbc507-4b14 :text "Joe broke his foot." .
    # :Event_dbcbc507-4b14 a :HealthAndDiseaseRelated ; :confidence-HealthAndDiseaseRelated 100 .
    # :Event_dbcbc507-4b14 a :DamageAndDifficulty ; :confidence-DamageAndDifficulty 80 .
    # :Event_dbcbc507-4b14 :has_active_entity :Joe .
    # :Noun_7a516752-0042 a :ComponentPart ; :text "foot" ; :confidence 100 .
    # :Event_dbcbc507-4b14 :has_affected_entity :Noun_7a516752-0042 .
    # :Narrative_foo :describes :NarrativeEvent_53273428-668e .
    # :NarrativeEvent_53273428-668e a :NarrativeEvent ; :offset 1 .
    # :NarrativeEvent_53273428-668e :text "Joe went to the doctor." .
    # :NarrativeEvent_53273428-668e :has_semantic :Event_9a0d7ec2-c6cd .
    # :NarrativeEvent_53273428-668e :has_first :Event_9a0d7ec2-c6cd .
    # :Event_9a0d7ec2-c6cd :text "Joe went to the doctor." .
    # :Event_9a0d7ec2-c6cd a :MovementTravelAndTransportation ; :confidence-MovementTravelAndTransportation 90 .
    # :Event_9a0d7ec2-c6cd a :HealthAndDiseaseRelated ; :confidence-HealthAndDiseaseRelated 80 .
    # :Event_9a0d7ec2-c6cd :has_active_entity :Joe .
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
    assert ':OpportunityAndPossibility' in ttl_str or ':ReadinessAndAbility' in ttl_str
    assert ':MeetingAndEncounter' in ttl_str
    assert ':has_active_entity :Mary' in ttl_str
    assert ':Person' in ttl_str and (':text "grandfather' in ttl_str or ':text "her grandfather' in ttl_str)
    assert ':has_affected_entity :Noun' in ttl_str
    assert ':future true' in ttl_str
    assert 'a :Time ; :text "Tuesday' in ttl_str and ':has_time' in ttl_str
    # Output Turtle:
    # :Narrative_foo :has_component :Sentence_409b7891-89fd .
    # :Sentence_409b7891-89fd a :Sentence ; :offset 1 .
    # :Sentence_409b7891-89fd :text "Mary can visit her grandfather on Tuesday." .
    # :Sentence_409b7891-89fd :mentions :Mary .
    # :Sentence_409b7891-89fd :grade_level 3 .
    # :Narrative_foo :describes :NarrativeEvent_36bd593f-dd94 .
    # :NarrativeEvent_36bd593f-dd94 a :NarrativeEvent ; :offset 0 .
    # :NarrativeEvent_36bd593f-dd94 :text "Mary can visit her grandfather on Tuesday." .
    # :NarrativeEvent_36bd593f-dd94 :has_semantic :Event_b862684c-8212 .
    # :NarrativeEvent_36bd593f-dd94 :has_first :Event_b862684c-8212 .
    # :Event_b862684c-8212 :text "Mary can visit her grandfather." .
    # :Event_b862684c-8212 :future true .
    # :Event_b862684c-8212 a :OpportunityAndPossibility ; :confidence-OpportunityAndPossibility 95 .
    # :Event_b862684c-8212 a :MeetingAndEncounter ; :confidence-MeetingAndEncounter 90 .
    # :Event_b862684c-8212 a :ReadinessAndAbility ; :confidence-ReadinessAndAbility 80 .
    # :Event_b862684c-8212 :has_active_entity :Mary .
    # :Noun_6d607e0a-48a0 a :Person ; :text "her grandfather" ; :confidence 95 .
    # :Noun_6d607e0a-48a0 :clarifying_text "her" .
    # :Event_b862684c-8212 :has_affected_entity :Noun_6d607e0a-48a0 .
    # :NarrativeEvent_36bd593f-dd94 :has_semantic :Event_87dce681-9e54 .
    # :Event_b862684c-8212 :has_next :Event_87dce681-9e54 .
    # :Event_87dce681-9e54 :text "The visit is on Tuesday." .
    # :Event_87dce681-9e54 :future true .
    # :Event_87dce681-9e54 a :EventAndState ; :confidence-EventAndState 70 .
    # :PiT_DayTuesday a :Time ; :text "Tuesday" .
    # :Event_87dce681-9e54 :has_time :PiT_DayTuesday .


def test_modal_neg():
    sentence_classes, quotation_classes = parse_narrative(text_modal_neg)
    graph_results = create_graph(sentence_classes, quotation_classes, text_modal_neg,
                                 ':Narrative_foo', [],5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':MeetingAndEncounter' in ttl_str and ':negated-MeetingAndEncounter' in ttl_str
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
    assert ':BodilyAct' in ttl_str and ':MovementTravelAndTransportation' in ttl_str
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
    assert ':Continuation' in ttl_str or (':SensoryPerception' in ttl_str and ':negated-SensoryPerception' in ttl_str)
    assert ':BodilyAct' in ttl_str
    assert ':has_active_entity :Peter' in ttl_str
    # Output Turtle:
    # :Narrative_foo :has_component :Sentence_e9b71481-5958 .
    # :Sentence_e9b71481-5958 a :Sentence ; :offset 1 .
    # :Sentence_e9b71481-5958 :text "Peter never tires of running." .
    # :Sentence_e9b71481-5958 :mentions :Peter .
    # :Sentence_e9b71481-5958 :grade_level 4 .
    # :Narrative_foo :describes :NarrativeEvent_1f71b8dc-3990 .
    #  :NarrativeEvent_1f71b8dc-3990 a :NarrativeEvent ; :offset 0 .
    # :NarrativeEvent_1f71b8dc-3990 :text "Peter never tires of running." .
    # :NarrativeEvent_1f71b8dc-3990 :has_semantic :Event_57ac10dc-242a .
    # :NarrativeEvent_1f71b8dc-3990 :has_first :Event_57ac10dc-242a .
    # :Event_57ac10dc-242a :text "Peter never tires." .
    # :Event_57ac10dc-242a a :SensoryPerception ; :confidence-SensoryPerception 90 .
    # :Event_57ac10dc-242a :negated-SensoryPerception true .
    # :Event_57ac10dc-242a a :Continuation ; :confidence-Continuation 85 .
    # :Event_57ac10dc-242a :has_active_entity :Peter .
    # :NarrativeEvent_1f71b8dc-3990 :has_semantic :Event_6df54a29-0db1 .
    # :Event_57ac10dc-242a :has_next :Event_6df54a29-0db1 .
    # :Event_6df54a29-0db1 :text "Peter runs." .
    # :Event_6df54a29-0db1 a :BodilyAct ; :confidence-BodilyAct 95 .
    # :Event_6df54a29-0db1 a :Continuation ; :confidence-Continuation 80 .
    # :Event_6df54a29-0db1 :has_active_entity :Peter .
    # TODO: Improve semantic mappings and distinctions; Confusing


def test_acomp_xcomp():
    sentence_classes, quotation_classes = parse_narrative(text_acomp_xcomp)
    graph_results = create_graph(sentence_classes, quotation_classes, text_acomp_xcomp,
                                 ':Narrative_foo', [],5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':OpenMindednessAndTolerance' in ttl_str and ':negated-OpenMindednessAndTolerance' in ttl_str
    assert ':HealthAndDiseaseRelated' in ttl_str or ':BodilyAct' in ttl_str
    assert ':text "smoking' in ttl_str
    assert ':has_active_entity :Jane' in ttl_str
    assert ':has_topic :Noun' in ttl_str
    # Output Turtle::Narrative_foo :has_component :Sentence_a1a7af1b-016b .
    # :Sentence_a1a7af1b-016b a :Sentence ; :offset 1 .
    # :Sentence_a1a7af1b-016b :text "Jane is unable to tolerate smoking." .
    # :Sentence_a1a7af1b-016b :mentions :Jane .
    # :Sentence_a1a7af1b-016b :grade_level 5 .
    # :Narrative_foo :describes :NarrativeEvent_b8b60d1f-b99a .
    #  :NarrativeEvent_b8b60d1f-b99a a :NarrativeEvent ; :offset 0 .
    # :NarrativeEvent_b8b60d1f-b99a :text "Jane is unable to tolerate smoking." .
    # :NarrativeEvent_b8b60d1f-b99a :has_semantic :Event_f1613392-e8f8 .
    # :NarrativeEvent_b8b60d1f-b99a :has_first :Event_f1613392-e8f8 .
    # :Event_f1613392-e8f8 :text "Jane is unable to tolerate smoking." .
    # :Event_f1613392-e8f8 a :Avoidance ; :confidence-Avoidance 90 .     # TODO: Consequence but not stated
    # :Event_f1613392-e8f8 a :OpenMindednessAndTolerance ; :confidence-OpenMindednessAndTolerance 85 .
    # :Event_f1613392-e8f8 :negated-OpenMindednessAndTolerance true .
    # :Event_f1613392-e8f8 :has_active_entity :Jane .
    # :Noun_84aa1a70-3a10 a :BodilyAct, :Collection ; :text "smoking" ; :confidence 90 .
    # :Event_f1613392-e8f8 :has_topic :Noun_84aa1a70-3a10 .


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
    assert ':has_affected_entity :John' in ttl_str
    assert ':has_active_entity :George' in ttl_str
    assert ':CrimeAndHostileConflict' in ttl_str         # breaking and entering
    assert ':has_active_entity :John' in ttl_str or ':has_topic :Noun' in ttl_str
    # Output Turtle:
    # :Narrative_foo :has_component :Sentence_7cc80505-e1a3 .
    # :Sentence_7cc80505-e1a3 a :Sentence ; :offset 1 .
    # :Sentence_7cc80505-e1a3 :text "John was accused by George of breaking and entering." .
    # :Sentence_7cc80505-e1a3 :mentions :John .
    # :Sentence_7cc80505-e1a3 :mentions :George .
    # :Sentence_7cc80505-e1a3 :grade_level 8 .
    # :Narrative_foo :describes :NarrativeEvent_755bf490-13c0 .
    # :NarrativeEvent_755bf490-13c0 a :NarrativeEvent ; :offset 0 .
    # :NarrativeEvent_755bf490-13c0 :text "John was accused by George of breaking and entering." .
    # :NarrativeEvent_755bf490-13c0 :has_semantic :Event_e8cfd689-fc86 .
    # :NarrativeEvent_755bf490-13c0 :has_first :Event_e8cfd689-fc86 .
    # :Event_e8cfd689-fc86 :text "George accused John of breaking and entering." .
    # :Event_e8cfd689-fc86 a :CommunicationAndSpeechAct ; :confidence-CommunicationAndSpeechAct 95 .
    # TODO: Error: George is not the actor of the breaking and entering
    # :Event_e8cfd689-fc86 a :CrimeAndHostileConflict ; :confidence-CrimeAndHostileConflict 90 .
    # :Event_e8cfd689-fc86 :has_active_entity :George .
    # :Event_e8cfd689-fc86 :has_affected_entity :John .
    # :Noun_9cdc372b-20b0 a :CrimeAndHostileConflict, :Collection ; :text "breaking and entering" ; :confidence 95 .
    # :Event_e8cfd689-fc86 :has_topic :Noun_9cdc372b-20b0 .


def test_idiom_trunc_pass():
    sentence_classes, quotation_classes = parse_narrative(text_idiom_trunc_pass)
    graph_results = create_graph(sentence_classes, quotation_classes, text_idiom_trunc_pass,
                                 ':Narrative_foo', [],5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':CommunicationAndSpeechAct' in ttl_str
    assert ':has_affected_entity :John' in ttl_str
    assert ':CrimeAndHostileConflict' in ttl_str and ':text "breaking and entering' in ttl_str
    assert ':has_topic :Noun' in ttl_str
    # Output Turtle:
    # :Narrative_foo :has_component :Sentence_457718bc-3f79 .
    # :Sentence_457718bc-3f79 a :Sentence ; :offset 1 .
    # :Sentence_457718bc-3f79 :text "John was accused of breaking and entering." .
    # :Sentence_457718bc-3f79 :mentions :John .
    # :Sentence_457718bc-3f79 :grade_level 8 .
    # :Narrative_foo :describes :NarrativeEvent_d1a8d626-9cc9 .
    # :NarrativeEvent_d1a8d626-9cc9 a :NarrativeEvent ; :offset 0 .
    # :NarrativeEvent_d1a8d626-9cc9 :text "John was accused of breaking and entering." .
    # :NarrativeEvent_d1a8d626-9cc9 :has_semantic :Event_7066e88b-6de8 .
    # :NarrativeEvent_d1a8d626-9cc9 :has_first :Event_7066e88b-6de8 .
    # :Event_7066e88b-6de8 :text "Someone accused John of breaking and entering." .
    # :Event_7066e88b-6de8 a :CommunicationAndSpeechAct ; :confidence-CommunicationAndSpeechAct 90 .
    # :Event_7066e88b-6de8 a :CrimeAndHostileConflict ; :confidence-CrimeAndHostileConflict 85 .
    # :Event_7066e88b-6de8 :has_affected_entity :John .
    # :Noun_0114051e-d5d1 a :CrimeAndHostileConflict, :Collection ; :text "breaking and entering" ; :confidence 95 .
    # :Event_7066e88b-6de8 :has_topic :Noun_0114051e-d5d1 .


def test_negation_emotion():
    sentence_classes, quotation_classes = parse_narrative(text_negative_emotion)
    graph_results = create_graph(sentence_classes, quotation_classes, text_negative_emotion,
                                 ':Narrative_foo', [],5, repo)
    ttl_str = str(graph_results.turtle)
    assert ':EmotionalResponse' in ttl_str and \
           (':DisagreementAndDispute' in ttl_str or ':negated-EmotionalResponse' in ttl_str)
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
    # :Event_bf6c8588-0a98 a :DisagreementAndDispute ; :confidence-DisagreementAndDispute 80 .
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
    assert ':has_affected_entity :John' in ttl_str
    # Output Turtle:
    # :Narrative_foo :has_component :Sentence_2ed4d0a0-9054 .
    # :Sentence_2ed4d0a0-9054 a :Sentence ; :offset 1 .
    # :Sentence_2ed4d0a0-9054 :text "Jane did not stab John." .
    # :Sentence_2ed4d0a0-9054 :mentions :Jane .
    # :Sentence_2ed4d0a0-9054 :mentions :John .
    # :Sentence_2ed4d0a0-9054 :grade_level 4 .
    # :Narrative_foo :describes :NarrativeEvent_edc2a122-3bb2 .
    # :NarrativeEvent_edc2a122-3bb2 a :NarrativeEvent ; :offset 0 .
    # :NarrativeEvent_edc2a122-3bb2 :text "Jane did not stab John." .
    # :NarrativeEvent_edc2a122-3bb2 :has_semantic :Event_f4a6b449-b341 .
    # :NarrativeEvent_edc2a122-3bb2 :has_first :Event_f4a6b449-b341 .
    # :Event_f4a6b449-b341 :text "Jane did not stab John." .
    # :Event_f4a6b449-b341 a :CrimeAndHostileConflict ; :confidence-CrimeAndHostileConflict 100 .
    # :Event_f4a6b449-b341 :negated-CrimeAndHostileConflict true .
    # :Event_f4a6b449-b341 :has_active_entity :Jane .
    # :Event_f4a6b449-b341 :has_affected_entity :John .


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
