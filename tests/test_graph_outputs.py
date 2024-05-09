import pytest
from dna.create_narrative_turtle import create_graph
from dna.nlp import parse_narrative

sentences = \
    'U.S. Rep. Liz Cheney conceded defeat Tuesday in the Republican primary in Wyoming, ' \
    'an outcome that was a priority for former President Donald Trump. ' \
    'Harriet Hageman, a water and natural-resources attorney who was endorsed by the former president, ' \
    'won 66.3% of the vote to Ms. Cheney’s 28.9%, with 95% of all votes counted. ' \
    '“No House seat, no office in this land is more important than the principles we swore to ' \
    'protect,” Ms. Cheney said in her concession speech. She also claimed that Trump is promoting ' \
    'an insidious lie about the recent FBI raid of his Mar-a-Lago residence.'


def test_sentences1():
    sentence_list, quotation_list, quoted_strings = parse_narrative(sentences)
    success, index, graph_ttl = create_graph(sentence_list, quotation_list)
    ttl_str = str(graph_ttl)
    assert index == 3
    assert ':Win' in ttl_str
    assert ':Loss' in ttl_str
    assert ':Affiliation' in ttl_str                                         # Trump endorsement of Hageman
    assert ':has_active_entity :Harriet_Hageman' in ttl_str
    assert ':has_active_entity :Liz_Cheney' in ttl_str
    assert ':has_active_entity :Donald_Trump' in ttl_str
    assert ':Measurement' in ttl_str and ':has_quantification' in ttl_str    # percentages
    assert ':CommunicationAndSpeechAct' in ttl_str
    assert ':DeceptionAndDishonesty' in ttl_str                              # "insidious lie"
    assert 'pathos' in ttl_str
    assert 'exceptionalism' in ttl_str or 'hyperbole' in ttl_str
    assert 'loaded language' in ttl_str
    assert ':Mar_a_Lago a :PhysicalLocation' in ttl_str
    # Output:
    # :Sentence_c2076a43-a925 a :Sentence ; :offset 1 .
    # :Sentence_c2076a43-a925 :text "U.S. Rep. Liz Cheney conceded defeat Tuesday in the Republican primary in
    #     Wyoming, an outcome that was a priority for former President Donald Trump." .
    # :Liz_Cheney :text "Liz Cheney" .
    # :Liz_Cheney a :Person .
    # :Liz_Cheney rdfs:label "Elizabeth Lynne Cheney", "Elizabeth Lynne Cheney Perry", "Elizabeth Lynne Perry",
    #     "Liz Cheney", "Elizabeth Cheney", "Liz", "Cheney" .
    # :Liz_Cheney rdfs:comment "From Wikipedia (wikibase_item: Q5362573): \'Elizabeth Lynne Cheney is an American
    #     attorney and politician. She represented Wyoming\'s at-large congressional district in the U.S. House of
    #     Representatives from 2017 to 2023 ...\'" .
    # :Liz_Cheney :external_link "https://en.wikipedia.org/wiki/Liz_Cheney" .
    # :Liz_Cheney :external_identifier {:identifier_source "Wikidata"} "Q5362573" .
    # :Liz_Cheney :gender "female" .
    # :Cheneys a :Person, :Collection ; rdfs:label "Cheneys" ; :role "family" .
    # :Republican :text "Republican" .
    # :Republican rdfs:label "The Republicans", "GOP", "Grand Old Party", "Republicans",
    #     "Republican Party (United States)", "United States Republican Party", "US Republican Party",
    #     "Republican Party", "Republican" .
    # :Republican a :PoliticalIdeology .
    # :Republican rdfs:comment "From Wikipedia (wikibase_item: Q29468): \'The Republican Party, also known as the GOP,
    #     is one of the two major contemporary political parties in the United States.
    #     It emerged as the main political rival of the Democratic Party in the mid-1850s.\'" .
    # :Republican :external_link "https://en.wikipedia.org/wiki/Republican_Party_(United_States)" .
    # :Republican :external_identifier {:identifier_source "Wikidata"} "Q29468" .
    # :Wyoming :text "Wyoming" .
    # :Wyoming a :PopulatedPlace, :AdministrativeDivision .
    # :Wyoming rdfs:label "WY", "Wyoming" .
    # :Wyoming rdfs:comment "From Wikipedia (wikibase_item: Q1214): \'Wyoming is a landlocked state in the Mountain
    #     West subregion of the Western United States. It borders Montana to the north and northwest, South Dakota
    #     and Nebraska to the east, Idaho to the west, Utah to the southwest, and Colorado to the south. ...\'" .\
    # :Wyoming :external_link "https://en.wikipedia.org/wiki/Wyoming" .
    # :Wyoming :external_identifier {:identifier_source "Wikidata"} "Q1214" .
    # :Wyoming :admin_level 1 .
    # :Wyoming :country_name "United States" .
    # geo:6252001 :has_component :Wyoming .
    # :Wyoming a :GeopoliticalEntity .
    # :Wyoming rdfs:label "WY", "Wyoming" .
    # :Donald_Trump :text "Donald Trump" .
    # :Donald_Trump a :Person .
    # :Donald_Trump rdfs:label "Donald Trump", "@realDonaldTrump", "David Dennison", "DJT", "Donald J Trump",
    #     "Donald J. Trump", "Individual 1", "Mr Trump", "POTUS 45", "President Donald J Trump",
    #     "President Donald J. Trump", "President Donald John Trump", "President Donald Trump", "President Trump",
    #     "The Donald", "John Miller", "Trump", "John Barron", "Donald John Trump", "Inmate No. P01135809",
    #     "Prisoner P01135809", "inmate P01135809", "Inmate P01135809", "The Former Guy", "P01135809", "Donald" .
    # :Donald_Trump rdfs:comment "From Wikipedia (wikibase_item: Q22686): \'Donald John Trump is an American
    #     politician, media personality, and businessman who served as the 45th president of the United States
    #     from 2017 to 2021.\'" .
    # :Donald_Trump :external_link "https://en.wikipedia.org/wiki/Donald_Trump" .
    # :Donald_Trump :external_identifier {:identifier_source "Wikidata"} "Q22686" .
    # :Donald_Trump :gender "male" .
    # :Trumps a :Person, :Collection ; rdfs:label "Trumps" ; :role "family" .
    # :Sentence_c2076a43-a925 :mentions geo:6252001 .
    # :Sentence_c2076a43-a925 :mentions :Liz_Cheney .
    # :Sentence_c2076a43-a925 :mentions :Republican .
    # :Sentence_c2076a43-a925 :mentions :Wyoming .
    # :Sentence_c2076a43-a925 :mentions :Donald_Trump .
    # :Sentence_c2076a43-a925 :summary "Liz Cheney loses Wyoming Republican primary." .
    # :Sentence_c2076a43-a925 :sentiment "negative" .
    # :Sentence_c2076a43-a925 :grade_level 8 .
    # :Sentence_c2076a43-a925 :has_semantic :Event_a7116883-02b0 .
    # :Event_a7116883-02b0 a :Loss ; :text "conceded defeat" .
    # :Event_a7116883-02b0 :has_active_entity :Liz_Cheney .
    # :Noun_a42edb91-d0cd a :End ; :text "defeat" ; rdfs:label "defeat" .
    # :Event_a7116883-02b0 :has_topic :Noun_a42edb91-d0cd .
    # :Event_a7116883-02b0 :has_time [ :text "Tuesday" ; a :Time ] .
    # :Event_a7116883-02b0 :has_location :Wyoming .
    # :Sentence_c2076a43-a925 :has_semantic :Event_06bf9c10-c756 .
    # :Event_06bf9c10-c756 a :EnvironmentAndCondition ; :text "was a priority" .
    # :Noun_fad7a583-eca9 a :Change ; :text "outcome" ; rdfs:label "an outcome" .
    # :Event_06bf9c10-c756 :has_topic :Noun_fad7a583-eca9 .
    # :Event_06bf9c10-c756 :has_topic [ :text "a priority" ; a :Clause ] .
    # :Event_06bf9c10-c756 :has_described_entity :Donald_Trump .
    # :Sentence_1847ec13-7004 a :Sentence ; :offset 2 .
    # :Sentence_1847ec13-7004 :text "Harriet Hageman, a water and natural-resources attorney who was endorsed by the
    #     former president, won 66.3% of the vote to Ms. Cheney’s 28.9%, with 95% of all votes counted." .
    # :Harriet_Hageman :text "Harriet Hageman" .
    # :Harriet_Hageman a :Person .
    # :Harriet_Hageman rdfs:label "Harriet M. Hageman", "Harriet Hageman", "Harriet", "Hageman" .
    # :Harriet_Hageman rdfs:comment "From Wikipedia (wikibase_item: Q110815967): \'Harriet Maxine Hageman is an
    #     American politician and attorney serving as the U.S. representative for Wyoming\'s at-large congressional
    #     district since 2023. She is a member of the Republican Party.\'" .
    # :Harriet_Hageman :external_link "https://en.wikipedia.org/wiki/Harriet_Hageman" .
    # :Harriet_Hageman :external_identifier {:identifier_source "Wikidata"} "Q110815967" .
    # :Harriet_Hageman :gender "female" .
    # :Hagemans a :Person, :Collection ; rdfs:label "Hagemans" ; :role "family" .
    # :Sentence_1847ec13-7004 :mentions :Harriet_Hageman .
    # :Sentence_1847ec13-7004 :mentions :Liz_Cheney .
    # :Sentence_1847ec13-7004 :summary "Harriet Hageman wins with 66.3% of the vote." .
    # :Sentence_1847ec13-7004 :sentiment "positive" .
    # :Sentence_1847ec13-7004 :grade_level 8 .
    # :Sentence_1847ec13-7004 :rhetorical_device {:evidence "won 66.3% of the vote to Ms. Cheney’s 28.9%, with 95%
    #     of all votes counted"}  "logos" .
    # :Sentence_1847ec13-7004 :has_semantic :Event_232d482c-0498 .
    # :Event_232d482c-0498 a :Affiliation ; :text "was endorsed" .
    # :Event_232d482c-0498 :affiliated_with :Harriet_Hageman .
    # :Noun_35be419c-95b5 a :Affiliation ; :text "president" ; rdfs:label "by the former president" .
    # :Event_232d482c-0498 :has_active_entity :Noun_35be419c-95b5 .
    # :Sentence_1847ec13-7004 :has_semantic :Event_b07eae0a-d41a .
    # :Event_b07eae0a-d41a a :Affiliation ; :text "was endorsed" .
    # :Event_b07eae0a-d41a :affiliated_with :Harriet_Hageman .
    # :Event_b07eae0a-d41a :has_active_entity :Noun_35be419c-95b5 .
    # :Sentence_1847ec13-7004 :has_semantic :Event_5e9efb21-4b7f .
    # :Event_5e9efb21-4b7f a :Win ; :text "won 66.3% of the vote" .
    # :Event_5e9efb21-4b7f :has_active_entity :Harriet_Hageman .
    # :Noun_0c6d981c-aa35 a :Measurement ; :text "66.3% of the vote" ; rdfs:label "66.3% of the vote" .
    # :Event_5e9efb21-4b7f :has_quantification :Noun_0c6d981c-aa35 .
    # :Noun_9391d248-adfb a :Person ; :text "Ms. Cheney" ; rdfs:label "to Ms. Cheney’s 28.9%" .
    # :Event_5e9efb21-4b7f :has_affected_entity :Noun_9391d248-adfb .
    # :Sentence_1847ec13-7004 :has_semantic :Event_9fd73291-2b7d .
    # :Event_9fd73291-2b7d a :Measurement ; :text "with 95% of all votes counted" .
    # :Noun_1af420b5-84e7 a :Measurement ; :text "votes" ; rdfs:label "95% of all votes" .
    # :Event_9fd73291-2b7d :has_quantification :Noun_1af420b5-84e7 .
    # :Sentence_8c5b4125-90ea a :Sentence ; :offset 3 .
    # :Sentence_8c5b4125-90ea :text "[Quotation0] Ms. Cheney said in her concession speech." .
    # :Sentence_8c5b4125-90ea :mentions :Liz_Cheney .
    # :Sentence_8c5b4125-90ea :has_component :Quotation0 .
    # :Sentence_8c5b4125-90ea :summary "Cheney delivers concession speech." .
    # :Sentence_8c5b4125-90ea :sentiment "neutral" .
    # :Sentence_8c5b4125-90ea :grade_level 8 .
    # :Sentence_8c5b4125-90ea :has_semantic :Event_acc372b1-53fe .
    # :Event_acc372b1-53fe a :CommunicationAndSpeechAct ; :text "said" .
    # :Event_acc372b1-53fe :has_active_entity :Liz_Cheney .
    # :Noun_a62d906e-768c a :CommunicationAndSpeechAct ; :text "concession speech" ; rdfs:label "in
    #     her concession speech" .
    # :Event_acc372b1-53fe :has_location :Noun_a62d906e-768c .
    # :Sentence_cc337306-9bdc a :Sentence ; :offset 4 .
    # :Sentence_cc337306-9bdc :text "She also claimed that Trump is promoting an insidious lie about
    #     the recent FBI raid of his Mar-a-Lago residence." .
    # :FBI :text "FBI" .
    # :FBI a :OrganizationalEntity .
    # :FBI rdfs:label "FBI", "F.B.I.", "Federal Bureau of Investigation" .
    # :FBI rdfs:comment "From Wikipedia (wikibase_item: Q8333): \'The Federal Bureau of Investigation (FBI) is
    #    the domestic intelligence and security service of the United States and its principal federal law
    #    enforcement agency. ...\'" .
    # :FBI :external_link "https://en.wikipedia.org/wiki/Federal_Bureau_of_Investigation" .
    # :FBI :external_identifier {:identifier_source "Wikidata"} "Q8333" .
    # :Sentence_bd1c68b9-6545 :mentions :FBI .
    # :Mar_a_Lago :text "Mar-a-Lago" .
    # :Mar_a_Lago a :PhysicalLocation .
    # :Mar_a_Lago rdfs:label "Mar-a-Lago", "Mar-A-Lago Building" .
    # :Mar_a_Lago rdfs:comment "From Wikipedia (wikibase_item: Q1262898): \'Mar-a-Lago is a resort and National
    #     Historic Landmark in Palm Beach, Florida. Since 1985, it has been owned by former U.S. president
    #     Donald Trump, who resides on the premises.\'" .
    # :Mar_a_Lago :external_link "https://en.wikipedia.org/wiki/Mar-a-Lago" .
    # :Mar_a_Lago :external_identifier {:identifier_source "Wikidata"} "Q1262898" .
    # :Mar_a_Lago :country_name "United States" .
    # geo:6252001 :has_component :Mar_a_Lago .
    # :Mar_a_Lago a :Location, :AnthropogenicFeature .
    # :Mar_a_Lago rdfs:label "Mar-a-Lago", "Mar-A-Lago Building" .
    # :Sentence_cc337306-9bdc :mentions :Donald_Trump .
    # :Sentence_cc337306-9bdc :mentions :FBI .
    # :Sentence_cc337306-9bdc :mentions :Mar_a_Lago .
    # :Sentence_cc337306-9bdc :summary "Claims Trump spreads false narrative about FBI raid." .
    # :Sentence_cc337306-9bdc :sentiment "negative" .
    # :Sentence_cc337306-9bdc :grade_level 8 .
    # :Sentence_cc337306-9bdc :rhetorical_device {:evidence "The use of the word \'insidious\' is an example of
    #     loaded language, as it carries strong negative connotations that invoke emotions and judgments about the
    #     nature of the lie."}  "loaded language" .
    # :Sentence_cc337306-9bdc :has_semantic :Event_c68ea6c5-1718 .
    # :Event_c68ea6c5-1718 a :CommunicationAndSpeechAct ; :text "claimed" .
    # :Event_c68ea6c5-1718 :has_active_entity :Liz_Cheney .
    # :Event_c68ea6c5-1718 :has_topic [ :text "that Trump is promoting an insidious lie about the recent FBI
    #     raid of Trump\'s Mar-a-Lago residence" ; a :Clause ] .
    # :Sentence_cc337306-9bdc :has_semantic :Event_b20c80c5-fa94 .
    # :Event_b20c80c5-fa94 a :DeceptionAndDishonesty ; :text "is promoting" .
    # :Event_b20c80c5-fa94 :has_active_entity :Donald_Trump .
    # :Noun_3de8ae10-0a24 a :CommunicationAndSpeechAct ; :text "lie" ; rdfs:label "an insidious lie" .
    # :Event_b20c80c5-fa94 :has_topic :Noun_3de8ae10-0a24 .
    # :Event_b20c80c5-fa94 :has_location :Mar_a_Lago .
    # :Quotation_e0947ef0-892f a :Quote ; :text "No House seat, no office in this land is more important than
    #     the principles we swore to protect," .
    # :Quotation_e0947ef0-892f :mentions :House_of_Representatives .
    # :Quotation_e0947ef0-892f :attributed_to :Liz_Cheney .
    # :Quotation_e0947ef0-892f :summary "No position surpasses sworn principles in importance." .
    # :Quotation_e0947ef0-892f :sentiment "positive" .
    # :Quotation_e0947ef0-892f :grade_level 8 .
    # :Quotation_e0947ef0-892f :rhetorical_device {:evidence "The phrase \'no House seat, no office in this land
    #     is more important than the principles we swore to protect\' suggests that the principles mentioned are unique,
    #     extraordinary, or exemplary compared to any political position."}  "exceptionalism" .
    # :Quotation_e0947ef0-892f :rhetorical_device {:evidence "The emphasis on the importance of principles over
    #     any political office appeals to the emotions of duty and integrity."}  "pathos" .'


def test_sentences2():
    sent_dicts, quotations, quotations_dict = parse_narrative(sentences)
    success, index, graph_ttl = create_graph(quotations_dict, sent_dicts, 2)
    assert index == 2
