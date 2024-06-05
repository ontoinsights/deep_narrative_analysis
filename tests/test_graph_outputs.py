import pytest
from dna.create_narrative_turtle import create_graph
from dna.nlp import parse_narrative

sentences1 = \
    'U.S. Rep. Liz Cheney conceded defeat Tuesday in the Republican primary in Wyoming, ' \
    'an outcome that was a priority for former President Donald Trump. ' \
    'Harriet Hageman, a water and natural-resources attorney who was endorsed by the former president, ' \
    'won 66.3% of the vote to Ms. Cheney’s 28.9%, with 95% of all votes counted. ' \
    '“No House seat, no office in this land is more important than the principles we swore to ' \
    'protect,” Ms. Cheney said in her concession speech. She also claimed that Trump is promoting ' \
    'an insidious lie about the recent FBI raid of his Mar-a-Lago residence.'

repo = 'foo'


def test_sentences1():
    sentence_list, quotation_list, quoted_strings = parse_narrative(sentences1)
    success, index, graph_ttl = create_graph(sentence_list, quotation_list, 5, repo)
    ttl_str = str(graph_ttl)
    assert index == 4       # 4 sentences
    assert ':Win' in ttl_str
    assert ':Loss' in ttl_str
    assert ':has_active_entity :Harriet_Hageman' in ttl_str
    assert ':has_active_entity :Liz_Cheney' in ttl_str
    assert ':has_active_entity :Donald_Trump' in ttl_str
    assert ':Measurement' in ttl_str and ':has_quantification' in ttl_str    # percentages
    assert ':CommunicationAndSpeechAct' in ttl_str
    assert ':DeceptionAndDishonesty' in ttl_str                              # "insidious lie"
    assert 'pathos' in ttl_str
    assert 'exceptionalism' in ttl_str or 'hyperbole' in ttl_str
    assert 'loaded language' in ttl_str
    # Output with RDF* properties:
    # :Sentence_d13ce0a5-2095 a :Sentence ; :offset 1 .
    # :Sentence_d13ce0a5-2095 :text "U.S. Rep. Liz Cheney conceded defeat Tuesday in the Republican primary
    #     in Wyoming, an outcome that was a priority for former President Donald Trump." .
    # :Republican :text "Republican" .
    # :Republican rdfs:label "Republican Party", "Republicans", "GOP", "Grand Old Party", "Republicans",
    #     "Republican Party (United States)", "United States Republican Party", "US Republican Party", "Republican" .
    # :Republican a :PoliticalIdeology, :Correction .
    # :Republican rdfs:comment "From Wikipedia (wikibase_item: Q29468): \'The Republican Party, also known as the
    #     GOP, is one of the two major contemporary political parties in the United States...\'" .
    # :Republican :external_link "https://en.wikipedia.org/wiki/Republican_Party_(United_States)" .
    # :Republican :external_identifier "Q29468" .
    # :Sentence_d13ce0a5-2095 :mentions geo:6252001 .
    # :Sentence_d13ce0a5-2095 :mentions :Liz_Cheney .
    # :Sentence_d13ce0a5-2095 :mentions :Republican .
    # :Sentence_d13ce0a5-2095 :mentions :Wyoming .
    # :Sentence_d13ce0a5-2095 :mentions :Donald_Trump .
    # :Sentence_d13ce0a5-2095 :summary "Liz Cheney loses Wyoming Republican primary." .
    # :Sentence_d13ce0a5-2095 :sentiment "negative" .
    # :Sentence_d13ce0a5-2095 :grade_level 8 .
    # :Sentence_d13ce0a5-2095 :rhetorical_device "kairos" .
    # :Sentence_d13ce0a5-2095 :rhetorical_device_kairos "The reference to \'Tuesday\' in the sentence invokes a
    #     specific day, which is used to mark the timing of the event, thereby engaging the reader by placing the
    #     event in a temporal context." .
    # :Sentence_d13ce0a5-2095 :has_semantic :Event_615634a3-b095 .
    # :Event_615634a3-b095 a :Loss ; :text "loses" .
    # :Event_615634a3-b095 :has_active_entity :Liz_Cheney .
    # :Noun_3a75311b-05b4 a :PoliticalEvent ; :text "Wyoming Republican primary" ; rdfs:label
    #     "Wyoming Republican primary" .
    # :Event_615634a3-b095 :has_topic :Noun_3a75311b-05b4 .
    # :Sentence_5dc6ceb6-c794 a :Sentence ; :offset 2 .
    # :Sentence_5dc6ceb6-c794 :text "Harriet Hageman, a water and natural-resources attorney who was endorsed by the
    #     former president, won 66.3% of the vote to Ms. Cheney’s 28.9%, with 95% of all votes counted." .
    # :Sentence_5dc6ceb6-c794 :mentions :Harriet_Hageman .
    # :Sentence_5dc6ceb6-c794 :mentions :Liz_Cheney .
    # :Sentence_5dc6ceb6-c794 :summary "Harriet Hageman wins with 66.3% of the vote." .
    # :Sentence_5dc6ceb6-c794 :sentiment "neutral" .
    # :Sentence_5dc6ceb6-c794 :grade_level 8 .
    # :Sentence_5dc6ceb6-c794 :rhetorical_device "logos" .
    # :Sentence_5dc6ceb6-c794 :rhetorical_device_logos "Use of specific percentages and the phrase \'with 95% of all
    #     votes counted\' provides statistical evidence to support the statement about the election results." .
    # :Sentence_5dc6ceb6-c794 :has_semantic :Event_7d72b265-49cb .
    # :Event_7d72b265-49cb a :Win ; :text "wins" .
    # :Event_7d72b265-49cb :has_active_entity :Harriet_Hageman .
    # :Noun_cb458936-1132 a :Measurement ; :text "66.3% of the vote" ; rdfs:label "66.3% of the vote" .
    # :Event_7d72b265-49cb :has_quantification :Noun_cb458936-1132 .
    # :Sentence_c8d9c156-f2bb a :Sentence ; :offset 3 .
    # :Sentence_c8d9c156-f2bb :text "[Quotation0] Ms. Cheney said in her concession speech." .
    # :Sentence_c8d9c156-f2bb :has_component :Quotation0 .
    # :Sentence_c8d9c156-f2bb :mentions :House .
    # :Sentence_c8d9c156-f2bb :mentions :Liz_Cheney .
    # :Sentence_c8d9c156-f2bb :summary "Cheney delivers concession speech." .
    # :Sentence_c8d9c156-f2bb :sentiment "neutral" .
    # :Sentence_c8d9c156-f2bb :grade_level 8 .
    # :Sentence_c8d9c156-f2bb :has_semantic :Event_a293a811-db36 .
    # :Event_a293a811-db36 a :CommunicationAndSpeechAct ; :text "delivers" .
    # :Event_a293a811-db36 :has_active_entity :Liz_Cheney .
    # :Event_a293a811-db36 :has_topic [ :text "concession speech" ; a :Clause ] .
    # :Sentence_0793bc9f-f0e8 a :Sentence ; :offset 4 .
    # :Sentence_0793bc9f-f0e8 :text "She also claimed that Trump is promoting an insidious lie about the recent
    #     FBI raid of his Mar-a-Lago residence." .
    # :Sentence_0793bc9f-f0e8 :mentions :Donald_Trump .
    # :Sentence_0793bc9f-f0e8 :mentions :FBI .
    # :Sentence_0793bc9f-f0e8 :mentions :Mar_a_Lago .
    # :Sentence_0793bc9f-f0e8 :summary "Cheney accuses Trump of spreading falsehoods about FBI raid." .
    # :Sentence_0793bc9f-f0e8 :sentiment "negative" .
    # :Sentence_0793bc9f-f0e8 :grade_level 8 .
    # :Sentence_0793bc9f-f0e8 :rhetorical_device "hyperbole" .
    # :Sentence_0793bc9f-f0e8 :rhetorical_device_hyperbole "The word \'insidious\' is an exaggerated term that
    #     intensifies the nature of the lie being promoted." .
    # :Sentence_0793bc9f-f0e8 :rhetorical_device "loaded language" .
    # :Sentence_0793bc9f-f0e8 :rhetorical_device_loaded_language "The use of \'insidious\' is a loaded
    #     language, implying a deceitful, harmful quality to the lie about the FBI raid." .
    # :Sentence_0793bc9f-f0e8 :has_semantic :Event_3c10cd3a-d80d .
    # :Event_3c10cd3a-d80d a :CommunicationAndSpeechAct ; :text "accuses" .
    # :Event_3c10cd3a-d80d :has_active_entity :Liz_Cheney .
    # :Event_3c10cd3a-d80d :has_affected_entity :Donald_Trump .
    # :Event_3c10cd3a-d80d :has_topic [ :text "of spreading falsehoods about FBI raid" ; a :Clause ] .
    # :Sentence_0793bc9f-f0e8 :has_semantic :Event_9d9942e0-6798 .
    # :Event_9d9942e0-6798 a :DeceptionAndDishonesty ; :text "spreading falsehoods about FBI raid" .
    # :Event_9d9942e0-6798 :has_active_entity :Donald_Trump .
    # :Noun_b81e8c7a-c4df a :CommunicationAndSpeechAct ; :text "falsehoods" ; rdfs:label "falsehoods" .
    # :Event_9d9942e0-6798 :has_topic :Noun_b81e8c7a-c4df .
    # :Noun_88f3fb29-9ce8 a :Affiliation ; :text "about FBI raid" ; rdfs:label "about FBI raid" .
    # :Event_9d9942e0-6798 :has_location :Noun_88f3fb29-9ce8 .
    # :Quotation1 a :Quote ; :text "No House seat, no office in this land is more important than the
    #     principles we swore to protect," .
    # :Quotation1 :attributed_to :Liz_Cheney .
    # :Quotation1 :summary "No position surpasses sworn principles in importance." .
    # :Quotation1 :sentiment "positive" .
    # :Quotation1 :grade_level 8 .
    # :Quotation1 :rhetorical_device "exceptionalism" .
    # :Quotation1 :rhetorical_device_exceptionalism "The phrase \'no House seat, no office in this land is more
    #     important than the principles we swore to protect\' uses language that indicates the principles are
    #     unique, extraordinary, or exemplary compared to any office or House seat." .
    # :Quotation1 :rhetorical_device "pathos" .
    # :Quotation1 :rhetorical_device_pathos "The statement appeals to the emotion of duty or honor by emphasizing the
    #     importance of the principles over any political position." .


# def test_sentences2():
#    sent_dicts, quotations, quotations_dict = parse_narrative(sentences)
#    success, index, graph_ttl = create_graph(quotations_dict, sent_dicts, 2)
#    assert index == 2
