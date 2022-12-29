# Processing related to AGENTS
# Called from create_narrative_turtle.py

import re
import uuid

from dna.create_noun_turtle import create_agent_ttl, create_norp_ttl
from dna.database import query_database
from dna.get_ontology_mapping import get_agent_or_loc_class
from dna.queries import query_match_noun
from dna.query_sources import get_wikidata_labels, get_wikipedia_description
from dna.utilities_and_language_specific import check_name_gender, empty_string, ontologies_database, \
    dna_prefix, underscore


def _check_agent_relevance(agent_text: str, sent_dict: dict) -> bool:
    """
    Determine if the text identified by spaCy NER is actually an Agent. Adjectives may be
    identified - for example, 'Jewish' in a sentence with the words 'Jewish settlement'.
    These are not agents.

    :param agent_text: Text identifying the agent
    :param sent_dict: The sentence dictionary
    :return: A boolean indicating that the text is an Agent (if true) or not (if false)
    """
    chunks = sent_dict['chunks']
    for chunk in chunks:
        chunk_str = str(chunk)
        indexes = []
        if chunk_str.find("'subjects'") > 0:
            indexes.append(chunk_str.index("'subjects'"))
        if chunk_str.find("'objects'") > 0:
            indexes.append(chunk_str.index("'objects'"))
        indexes.append(chunk_str.index("'verb"))    # Always have 'verb' key in a chunk; May have 'verb_processing'
        details_after_text = min(indexes)           # Get the details directly following the 'chunk_text' entry
        chunk_str = chunk_str[details_after_text:]
        agent_words = agent_text.split()
        for agent_word in agent_words:
            if agent_word in chunk_str:
                return True
    return False


def _check_if_agent_is_known(agent_text: str, agent_type: str, alet_dict: dict) -> (str, str):
    """
    Determines if the agent is already processed and identified in the alet_dict.

    :param agent_text: Input string identifying the agent
    :param agent_type: String identifying NER type for the text, as defined by spaCy
    :param alet_dict: A dictionary holding the agents, locations, events & times encountered in
             the full narrative - For co-reference resolution (it may be updated by this function);
             Keys = 'agents', 'locs', 'events', 'times' and Values (for 'agents') = array of arrays
             with index 0 holding an array of labels associated with the agent (variations on their
             name), index 1 storing the agent's entity type and index 2 storing the agent's IRI
    :return: A tuple holding the entity type and IRI of the agent, or two empty strings
    """
    if 'agents' not in alet_dict:
        return agent_type, empty_string
    known_agents = alet_dict['agents']
    for known_agent in known_agents:
        if agent_text in known_agent[0]:              # Strings match
            return known_agent[1], known_agent[2]     # NER maps to a known/processed agent, with type and IRI
    return agent_type, empty_string


def _get_agent_iri_and_ttl(agent_text: str, agent_type: str, alet_dict: dict,
                           use_sources: bool) -> (str, str, str, list):
    """
    Handle agent names identified by spaCy's NER, stored in the sentence dictionary with the
    key, 'AGENTS'.

    :param agent_text: Text identifying the agent
    :param agent_type: String holding the NER type identified by spaCy
    :param alet_dict: A dictionary holding the agents, locations, events & times encountered in
             the full narrative - For co-reference resolution (it may be updated by this function);
             Keys = 'agents', 'locs', 'events', 'times', Values (for 'agents') = array of arrays
             with index 0 holding an array of labels associated with the agent (variations on their
             name), index 1 storing the agent's entity type and index 2 storing the agent's IRI
    :param use_sources: Boolean indicating whether additional information on an agent should
                        be retrieved from Wikidata (recommended)
    :return: A tuple holding 1-3 strings with the agent's entity type, DNA class mapping and IRI,
             and 4) a list of Turtle statements defining the agent (also, the alet_dict is updated)
    """
    agent_iri = re.sub(r'[^:a-zA-Z0-9_]', underscore, f':{agent_text}').replace('__', '_')
    labels = []
    family_names = []
    wiki_details = empty_string
    wiki_url = empty_string
    if use_sources:
        wiki_details, wiki_url = get_wikipedia_description(agent_text.replace(' ', underscore))
        if wiki_details and 'See the web site' not in wiki_details:
            labels = get_wikidata_labels(wiki_details.split('wikibase_item: ')[1].split(')')[0])
    # Update alet_dict
    known_agents = alet_dict['agents'] if 'agents' in alet_dict else []
    if 'PERSON' in agent_type:
        family_names = _update_agent_names(agent_text, labels)
        agent_type = check_name_gender(agent_text)
    known_agents.append([labels, agent_type, agent_iri])
    for fam_name in family_names:
        known_agents.append([[fam_name], 'PLURALPERSON', f':{fam_name}'])
    alet_dict['agents'] = known_agents
    agent_class = get_agent_or_loc_class(agent_type)
    if agent_type.endswith('NORP'):
        agent_iri = f'{agent_iri}_{str(uuid.uuid4())[:13]}'
        return agent_type, agent_class, agent_iri, \
            create_norp_ttl(agent_text, agent_type, agent_iri, wiki_details, wiki_url, labels)
    return agent_type, agent_class, agent_iri, \
        create_agent_ttl(agent_iri, labels, agent_type, agent_class, wiki_details, wiki_url, family_names)


def _update_agent_names(agent_text: str, alt_names: list) -> list:
    """
    Create the possible permutations of an agent's name.

    :param agent_text: Text specifying the agent's name
    :param alt_names: An array of possible alternative names for the agent
    :return: An array of possible family names (if the agent_name includes a space) and
             the alt_names array may be updated
    """
    no_paren = agent_text.replace('(', empty_string).replace(')', empty_string)
    split_names = no_paren.split()
    for name in split_names:
        if name not in alt_names:
            alt_names.append(name)
    perm_list = []
    family_names = []
    if len(split_names) > 1:
        for i in range(1, len(split_names)):
            family_names.append(f'{split_names[i]}s')
        perm_list = get_name_permutations(no_paren)
    for name in perm_list:
        if name not in alt_names:
            alt_names.append(name)
    if agent_text not in alt_names:
        alt_names.append(agent_text)
    if no_paren not in alt_names:
        alt_names.append(no_paren)
    return family_names


def get_name_permutations(name: str) -> list:
    """
    Get the combinations of first and maiden/last names.

    :param name: A string holding a Person's full name
    :return: A list of strings combining the first and second, first and third, ... names
    """
    poss_names = []
    names = name.split()
    for i in range(1, len(names)):
        poss_names.append(f'{names[0]} {names[i]}')
    return poss_names


def get_sentence_agents(sent_dict: dict, alet_dict: dict, last_nouns: list, use_sources: bool) -> (list, list):
    """
    Handle agent names identified by spaCy's NER, stored in the sentence dictionary with the
    key, 'AGENTS'.

    :param sent_dict: The sentence dictionary
    :param alet_dict: A dictionary holding the agents, locations, events & times encountered in
             the full narrative - For co-reference resolution (it may be updated by this function);
             Keys = 'agents', 'locs', 'events', 'times', Values (for 'agents') = array of arrays
             with index 0 holding an array of labels associated with the agent (variations on their
             name), index 1 storing the agent's entity type and index 2 storing the agent's IRI
    :param last_nouns: An array of tuples = noun texts, type, class mapping and IRI
                       from the current paragraph
    :param use_sources: Boolean indicating whether additional information on an agent should
                        be retrieved from Wikidata (recommended)
    :return: A tuple consisting of two arrays: (1) the IRIs of the agents identified in the sentence,
             and 2) Turtle statements defining them  (also the alet_dict may be updated)
    """
    agents_turtle = []
    new_agents = sent_dict['AGENTS']
    new_agents_dict = dict()
    agent_iris = []
    for new_agent in new_agents:
        agent_split = new_agent.split('+')
        # Ignore NORP in sentence AGENT analysis (will be addressed at the level of the verb, if needed)
        if agent_split[1] != 'NORP':
            new_agents_dict[agent_split[0]] = _check_if_agent_is_known(agent_split[0], agent_split[1], alet_dict)
    for new_agent, agent_details in new_agents_dict.items():
        agent_type, agent_iri = agent_details
        if not agent_iri:
            # Need to define the Turtle for a new agent
            # Is the Agent already defined in the ontology?
            insts = query_database('select', query_match_noun.replace('keyword', new_agent), ontologies_database)
            if insts:
                inst_result = insts[0]
                agent_class = inst_result['class']['value']
                agent_iri = inst_result['inst']['value'].replace(dna_prefix, ':')
            else:
                agent_type, agent_class, agent_iri, agent_ttl = \
                    _get_agent_iri_and_ttl(new_agent, agent_type, alet_dict, use_sources)
                agents_turtle.extend(agent_ttl)
        else:
            agent_class = get_agent_or_loc_class(agent_type)
        last_nouns.append((new_agent, agent_type, [agent_class], agent_iri))
        agent_iris.append(agent_iri)
    return agent_iris, agents_turtle
