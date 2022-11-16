from dna.coreference_resolution import check_nouns
from dna.process_locations import get_sentence_locations
from dna.process_agents import get_sentence_agents
from dna.process_times import get_sentence_times
from dna.nlp import parse_narrative

sent1 = 'U.S. Rep. Liz Cheney conceded defeat Tuesday in the Republican primary in Wyoming, ' \
        'an outcome that was a priority for former President Donald Trump as he urged GOP voters ' \
        'to reject one of his most prominent critics on Capitol Hill.'
sent2 = 'She then compared herself to Abraham Lincoln, who saved the nation during our Civil War.'
sent3 = 'They might be presidents.'
paragraphs = 'Harriet Hageman won the primary.' + '\n\n' + \
             'Liz Cheney compared herself to Abraham Lincoln. Cheney lost.'
family_members = 'Mary loved to play with her brothers, Ralph and Carter.'

alet_dictionary = dict()
last_nouns = []
last_events = []


def reset():
    alet_dictionary.clear()
    last_nouns.clear()
    last_events.clear()


def test_sent1_alet():
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(sent1)
    sent_dict = sent_dicts[0]
    reset()
    get_sentence_locations(sent_dict, alet_dictionary, last_nouns, True)
    get_sentence_times(sent_dict, '', alet_dictionary, last_nouns, True)
    get_sentence_agents(sent_dict, alet_dictionary, last_nouns, True)
    assert alet_dictionary['events'] == []
    assert len(alet_dictionary['locs']) == 1   # Because the country is already known to DNA
    assert len(alet_dictionary['locs'][0][0]) == 2
    assert len(alet_dictionary['agents']) == 6
    agent_iris = []
    for agent in alet_dictionary['agents']:
        agent_iris.append(agent[2])
    assert ':Liz_Cheney' in agent_iris and ':Donald_Trump' in agent_iris
    assert ':Cheneys' in agent_iris and ':Trumps' in agent_iris   # The families
    assert ':GOP' in agent_iris and ':Capitol_Hill' in agent_iris
    assert ('U.S.', 'LOC', [':Country'], 'geo:6252001') in last_nouns
    assert ('Wyoming', 'LOC', [':PopulatedPlace+:AdministrativeDivision'], ':Wyoming') in last_nouns
    assert ('Liz Cheney', 'FEMALESINGPERSON', [':Person'], ':Liz_Cheney') in last_nouns
    assert ('Donald Trump', 'MALESINGPERSON', [':Person'], ':Donald_Trump') in last_nouns


def test_sent2_alet():
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(sent2)
    turtle = []
    sent_dict = sent_dicts[0]
    get_sentence_times(sent_dict, '', alet_dictionary, last_nouns, True)
    get_sentence_agents(sent_dict, alet_dictionary, last_nouns, True)
    # No dates since there are many 'Civil Wars' - get a Wikipedia disambiguation page
    assert alet_dictionary['events'] == [[['Civil War'], [':War'], ':Event_Civil_War', '', '']]
    assert len(alet_dictionary['locs']) == 1    # From above
    assert len(alet_dictionary['agents']) == 8
    agent_iris = []
    for agent in alet_dictionary['agents']:
        agent_iris.append(agent[2])
    assert ':Liz_Cheney' in agent_iris and ':Donald_Trump' in agent_iris
    assert ':Abraham_Lincoln' in agent_iris
    assert ':Cheneys' in agent_iris and ':Trumps' in agent_iris and ':Lincolns' in agent_iris    # The families
    assert ('Civil War', 'EVENT', [':War'], ':Event_Civil_War') in last_nouns
    match1 = check_nouns(sent_dict['chunks'][1], 'subjects', alet_dictionary, last_nouns, last_events, turtle, True)
    assert len(match1) == 1
    assert match1[0] == ('Liz Cheney', 'FEMALESINGPERSON', [':Person'], ':Liz_Cheney')
    match2 = check_nouns(sent_dict['chunks'][1]['verbs'][0], 'objects', alet_dictionary,
                         last_nouns, last_events, turtle, True)
    assert match2[0] == ('Liz Cheney', 'FEMALESINGPERSON', [':Person'], ':Liz_Cheney')


def test_sent3_alet():
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(sent3)
    turtle = []
    sent_dict = sent_dicts[0]
    match1 = check_nouns(sent_dict['chunks'][0], 'subjects', alet_dictionary, last_nouns, last_events, turtle, True)
    assert len(match1) == 3


def test_paragraphs():
    reset()
    turtle = []
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(paragraphs)
    get_sentence_agents(sent_dicts[0], alet_dictionary, last_nouns, True)
    get_sentence_agents(sent_dicts[2], alet_dictionary, last_nouns, True)
    get_sentence_agents(sent_dicts[3], alet_dictionary, last_nouns, True)
    assert len(alet_dictionary['agents']) == 6
    agent_iris = []
    for agent in alet_dictionary['agents']:
        agent_iris.append(agent[2])
    assert ':Liz_Cheney' in agent_iris and ':Harriet_Hageman' in agent_iris and ':Abraham_Lincoln' in agent_iris
    match1 = check_nouns(sent_dicts[2]['chunks'][0]['verbs'][0], 'objects', alet_dictionary, last_nouns,
                         last_events, turtle, True)
    assert match1[0] == ('Cheney', 'FEMALESINGPERSON', [':Person'], ':Liz_Cheney')


def test_sent1_no_ext():
    reset()
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(sent1)
    sent_dict = sent_dicts[0]
    get_sentence_locations(sent_dict, alet_dictionary, last_nouns, False)
    get_sentence_times(sent_dict, '', alet_dictionary, last_nouns, False)
    get_sentence_agents(sent_dict, alet_dictionary, last_nouns, False)
    assert len(family_dict) == 0
    assert alet_dictionary['events'] == []
    assert len(alet_dictionary['locs']) == 1   # Because the country is already known to DNA
    assert len(alet_dictionary['locs'][0][0]) == 1  # No alt names without ext source check
    assert len(alet_dictionary['agents']) == 6
    agent_iris = []
    for agent in alet_dictionary['agents']:
        agent_iris.append(agent[2])
    assert ':Liz_Cheney' in agent_iris and ':Donald_Trump' in agent_iris
    assert ('U.S.', 'LOC', [':Country'], 'geo:6252001') in last_nouns
    assert ('Wyoming', 'LOC', [':GeopoliticalEntity'], ':Wyoming') in last_nouns
    assert ('Liz Cheney', 'FEMALESINGPERSON', [':Person'], ':Liz_Cheney') in last_nouns
    assert ('Donald Trump', 'MALESINGPERSON', [':Person'], ':Donald_Trump') in last_nouns


def test_family_members():
    reset()
    sent_dicts, quotations, quotations_dict, family_dict = parse_narrative(family_members)
    sent_dict = sent_dicts[0]
    get_sentence_agents(sent_dict, alet_dictionary, last_nouns, False)
    assert len(alet_dictionary['agents']) == 3
    agent_iris = []
    for agent in alet_dictionary['agents']:
        agent_iris.append(agent[2])
    assert ':Mary' in agent_iris and ':Ralph' in agent_iris and ':Carter' in agent_iris
    assert ('Mary', 'FEMALESINGPERSON', [':Person'], ':Mary') in last_nouns
    assert ('Ralph', 'MALESINGPERSON', [':Person'], ':Ralph') in last_nouns
    assert 'Ralph' in family_dict and 'Carter' in family_dict
    assert family_dict['Ralph'] == 'brother'
    assert family_dict['Carter'] == 'brother'
