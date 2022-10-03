# Processing related to AGENTS
# Called from create_narrative_turtle.py

import requests

from dna.create_noun_turtle import create_agent_ttl
from dna.get_ontology_mapping import get_agent_class
from dna.queries import query_wikidata_alt_names
from dna.query_sources import get_wikipedia_description
from dna.utilities import check_name_gender, empty_string, space


def _get_agent_iri_and_ttl(agent_text: str, alet_dict: dict, use_sources: bool) -> (str, str, str, list):
    """
    Handle agent names identified by spaCy's NER, stored in the sentence dictionary with the
    key, 'AGENTS'.

    :param agent_text: Text identifying the agent
    :param alet_dict: A dictionary holding the agents, locations, events & times encountered in
             the full narrative - For co-reference resolution (it may be updated by this function);
             Keys = 'agents', 'locs', 'events', 'times', Values (for 'agents') = array of arrays
             with index 0 holding an array of labels associated with the agent (variations on their
             name), index 1 storing the agent's entity type and index 2 storing the agent's IRI
    :param use_sources: Boolean indicating whether additional information on a agent should
                        be retrieved from Wikidata (recommended)
    :return: A tuple holding 1-3) strings with the agent's entity type, DNA class mapping and IRI,
             and 4) a list of Turtle statements defining the agent (also, if the agent is not
             already 'known'/processed, the alet_dict is updated)
    """
    agent_type, agent_iri = check_if_agent_is_known(agent_text, alet_dict)
    if agent_iri:
        return agent_type, get_agent_class(agent_type), agent_iri, []
    agent_iri = f':{agent_text.replace(space,"_")}'.replace('.', empty_string).replace("'s", empty_string)
    alt_names = []
    wiki_details = empty_string
    if use_sources:
        wiki_details = get_wikipedia_description(agent_text.replace(space, '_'))
        if wiki_details:
            if 'See the web site' not in wiki_details:
                wikidata_id = wiki_details.split('wikibase_item: ')[1].split(')')[0]
                query_alt_names = query_wikidata_alt_names.replace('?item', f'wd:{wikidata_id}')
                response = requests.get(
                    f'https://query.wikidata.org/sparql?format=json&query={query_alt_names}').json()
                if 'results' in response and 'bindings' in response['results']:
                    results = response['results']['bindings']
                    for result in results:
                        alt_names.append(result['altLabel']['value'].replace('"', "'"))
    split_names = agent_text.split(space)
    if split_names[-1] not in alt_names:    # Get first and last names, if possible
        alt_names.append(split_names[-1])
    if agent_text not in alt_names:
        alt_names.append(agent_text)
    known_agents = alet_dict['agents'] if 'agents' in alet_dict else []
    agent_type = check_name_gender(agent_text)
    known_agents.append([alt_names, agent_type, agent_iri])
    alet_dict['agents'] = known_agents
    agent_class = get_agent_class(agent_type)
    return agent_type, agent_class, agent_iri, \
           create_agent_ttl(agent_iri, alt_names, agent_type, agent_class, wiki_details)


def check_if_agent_is_known(agent_text: str, alet_dict: dict) -> (str, str):
    """
    Determines if the agent is already processed and identified in the alet_dict.

    :param agent_text: Input string identifying the agent
    :param alet_dict: A dictionary holding the agents, locations, events & times encountered in
             the full narrative - For co-reference resolution (it may be updated by this function);
             Keys = 'agents', 'locs', 'events', 'times' and Values (for 'agents') = array of arrays
             with index 0 holding an array of labels associated with the agent (variations on their
             name), index 1 storing the agent's entity type and index 2 storing the agent's IRI
    :return: A tuple holding the entity type and IRI of the agent, or two empty strings
    """
    if 'agents' not in alet_dict:
        return empty_string, empty_string
    known_agents = alet_dict['agents']
    for known_agent in known_agents:
        if agent_text in known_agent[0]:              # Strings match
            return known_agent[1], known_agent[2]     # NER maps to a known/processed location, with type and IRI
    return empty_string, empty_string


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
    :param use_sources: Boolean indicating whether additional information on a agent should
                        be retrieved from Wikidata (recommended)
    :return: A tuple consisting of two arrays: (1) the IRIs of the agents identified in the sentence,
             and 2) Turtle statements defining them  (also the alet_dict may be updated)
    """
    agents_turtle = []
    new_agents = sent_dict['AGENTS']
    new_agents_dict = dict()
    agent_iris = []
    for new_agent in new_agents:
        new_agents_dict[new_agent] = check_if_agent_is_known(new_agent, alet_dict)
    for new_agent, agent_details in new_agents_dict.items():
        agent_type, agent_iri = agent_details
        if not agent_iri:
            # Need to define the Turtle for a new agent
            agent_type, agent_class, agent_iri, agent_ttl = _get_agent_iri_and_ttl(new_agent, alet_dict, use_sources)
            agents_turtle.extend(agent_ttl)
        else:
            agent_class = get_agent_class(agent_type)
        last_nouns.append((new_agent, agent_type, [agent_class], agent_iri))
        agent_iris.append(agent_iri)
    return agent_iris, agents_turtle
