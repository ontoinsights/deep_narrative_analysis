from dna.coreference_resolution import check_nouns
from dna.process_locations import get_sentence_locations
from dna.process_persons import get_sentence_persons
from dna.process_times import get_sentence_times
from dna.nlp import parse_narrative

sent1 = 'U.S. Rep. Liz Cheney conceded defeat Tuesday in the Republican primary in Wyoming, ' \
        'an outcome that was a priority for former President Donald Trump as he urged GOP voters ' \
        'to reject one of his most prominent critics on Capitol Hill.'
sent2 = 'She then compared herself to Abraham Lincoln, who saved the nation during our Civil War.'
sent3 = 'They might be presidents.'
paragraphs = 'Harriet Hageman won the primary.' + '\n\n' + \
             'Liz Cheney compared herself to Abraham Lincoln. Cheney lost.'

plet_dictionary = dict()
last_nouns = []
last_events = []


def test_sent1_plet():
    sent_dicts, quotations, quotations_dict = parse_narrative(sent1)
    sent_dict = sent_dicts[0]
    get_sentence_locations(sent_dict, plet_dictionary, last_nouns, True)
    get_sentence_times(sent_dict, '', plet_dictionary, last_nouns, True)
    get_sentence_persons(sent_dict, plet_dictionary, last_nouns, True)
    assert plet_dictionary['events'] == []
    assert len(plet_dictionary['locs']) == 1   # Because the country is already known to DNA
    assert len(plet_dictionary['locs'][0][0]) > 2  # Need to have obtained the alt names for Wyoming
    assert len(plet_dictionary['persons']) == 2
    assert plet_dictionary['persons'][0][2] == ':Liz_Cheney'
    assert plet_dictionary['persons'][1][2] == ':Donald_Trump'
    assert ('U.S.', 'LOC', [':Country'], 'geo:6252001') in last_nouns
    assert ('Wyoming', 'LOC', [':PopulatedPlace+:AdministrativeDivision'], ':Wyoming') in last_nouns
    assert ('Liz Cheney', 'FEMALESINGPERSON', [':Person'], ':Liz_Cheney') in last_nouns
    assert ('Donald Trump', 'MALESINGPERSON', [':Person'], ':Donald_Trump') in last_nouns


def test_sent2_plet():
    sent_dicts, quotations, quotations_dict = parse_narrative(sent2)
    turtle = []
    sent_dict = sent_dicts[0]
    get_sentence_times(sent_dict, '', plet_dictionary, last_nouns, True)
    get_sentence_persons(sent_dict, plet_dictionary, last_nouns, True)
    # No dates since there are many 'Civil Wars' - get a Wikipedia disambiguation page
    assert plet_dictionary['events'] == [[['Civil War'], [':War'], ':Event_Civil_War', '', '']]
    assert len(plet_dictionary['locs']) == 1    # From above
    assert len(plet_dictionary['persons']) == 3
    assert plet_dictionary['persons'][0][2] == ':Liz_Cheney'
    assert plet_dictionary['persons'][1][2] == ':Donald_Trump'
    assert plet_dictionary['persons'][2][2] == ':Abraham_Lincoln'
    assert ('Civil War', 'EVENT', [':War'], ':Event_Civil_War') in last_nouns
    match1 = check_nouns(sent_dict['chunks'][1], 'subjects', plet_dictionary, last_nouns, last_events, turtle, True)
    assert len(match1) == 1
    assert match1[0] == ('Liz Cheney', 'FEMALESINGPERSON', [':Person'], ':Liz_Cheney')
    match2 = check_nouns(sent_dict['chunks'][1]['verbs'][0], 'objects', plet_dictionary,
                         last_nouns, last_events, turtle, True)
    assert match2[0] == ('Liz Cheney', 'FEMALESINGPERSON', [':Person'], ':Liz_Cheney')


def test_sent3_plet():
    sent_dicts, quotations, quotations_dict = parse_narrative(sent3)
    turtle = []
    sent_dict = sent_dicts[0]
    match1 = check_nouns(sent_dict['chunks'][0], 'subjects', plet_dictionary, last_nouns, last_events, turtle, True)
    assert len(match1) == 3


def test_paragraphs():
    plet_dictionary = dict()
    last_nouns = []
    last_events = []
    turtle = []
    sent_dicts, quotations, quotations_dict = parse_narrative(paragraphs)
    get_sentence_persons(sent_dicts[0], plet_dictionary, last_nouns, True)
    get_sentence_persons(sent_dicts[2], plet_dictionary, last_nouns, True)
    get_sentence_persons(sent_dicts[3], plet_dictionary, last_nouns, True)
    sent_dict = sent_dicts[2]
    assert len(plet_dictionary['persons']) == 3
    assert plet_dictionary['persons'][0][2] == ':Harriet_Hageman'
    assert plet_dictionary['persons'][1][2] == ':Liz_Cheney'
    assert plet_dictionary['persons'][2][2] == ':Abraham_Lincoln'
    match1 = check_nouns(sent_dicts[2]['chunks'][0]['verbs'][0], 'objects', plet_dictionary, last_nouns,
                         last_events, turtle, True)
    assert match1[0] == ('Cheney', 'FEMALESINGPERSON', [':Person'], ':Liz_Cheney')


def test_sent1_no_ext():
    plet_dictionary = dict()
    last_nouns = []
    last_events = []
    sent_dicts, quotations, quotations_dict = parse_narrative(sent1)
    sent_dict = sent_dicts[0]
    get_sentence_locations(sent_dict, plet_dictionary, last_nouns, False)
    get_sentence_times(sent_dict, '', plet_dictionary, last_nouns, False)
    get_sentence_persons(sent_dict, plet_dictionary, last_nouns, False)
    assert plet_dictionary['events'] == []
    assert len(plet_dictionary['locs']) == 1   # Because the country is already known to DNA
    assert len(plet_dictionary['locs'][0][0]) == 1  # No alt names without ext source check
    assert len(plet_dictionary['persons']) == 2
    assert plet_dictionary['persons'][0][2] == ':Liz_Cheney'
    assert plet_dictionary['persons'][1][2] == ':Donald_Trump'
    assert ('U.S.', 'LOC', [':Country'], 'geo:6252001') in last_nouns
    assert ('Wyoming', 'LOC', [':Location'], ':Wyoming') in last_nouns
    assert ('Liz Cheney', 'FEMALESINGPERSON', [':Person'], ':Liz_Cheney') in last_nouns
    assert ('Donald Trump', 'MALESINGPERSON', [':Person'], ':Donald_Trump') in last_nouns
