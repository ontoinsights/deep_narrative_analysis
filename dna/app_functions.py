# Functions used by the app.py processing to validate query parameters and
# create the Turtle declarations

import json
import logging
from typing import Union
import uuid
from datetime import datetime
from flask import Request, Response, jsonify

from dna.create_narrative_turtle import create_graph
from dna.database import add_remove_data, check_server_status, query_database
from dna.database_queries import count_triples, query_narratives, query_repos
from dna.nlp import parse_narrative
from dna.query_openai import access_api, narrative_goals, narr_prompt, rhetorical_devices
from dna.utilities_and_language_specific import dna_prefix, empty_string, meta_graph, ttl_prefixes

detail: str = 'detail'
error_str: str = 'error'
narrative_id: str = 'narrativeId'
repository: str = 'repository'


def _check_from_to_date(date_value: str) -> bool:
    """
    Check that the date query parameters ('from' and 'to') are defined and have the format,
    YYYY-mm-dd.

    :param date_value: String holding either the 'from' or 'to' date value from the API
    :return: Boolean indicating if the date has a valid format
    """
    ymd = date_value.split('-')
    if len(ymd) != 3:
        return False
    if len(ymd[0]) != 4:
        return False
    for i in range(0, 3):
        if not ymd[i].isdigit():
            return False
    if not (1900 < int(ymd[0]) < 2100) or not (0 < int(ymd[1]) < 13) or not (0 < int(ymd[2]) < 32):
        return False
    return True


def _entity_exists(repo: str, graph: str = empty_string) -> bool:
    """
    Validate that the repository exists (if no graph id is provided), or that the specified graph exists
    for the database.

    :param repo: The repository nae
    :param graph: String identifying the narrative/narrative graph
    :return: True if the database or graph exists for the specified server, False otherwise
    """
    if graph:
        bindings = query_database('select', query_narratives.replace('?named', f':{repo}_default')
                                  .replace('?graph', f':{graph}'), repo)
    else:
        bindings = query_database('select', query_repos.replace('?repo', f':{repo}'), empty_string)
    if bindings:
        return True
    return False


def check_query_parameter(check_param: str, should_exist: bool, req: Request) -> (Union[dict, str, bool], int):
    """
    Check that the specified query parameter is defined. (1) If the check_param == 'repository', check
    that a query parameter for 'repository' is defined. A Stardog database at the address specified in
    the environment variable, STARDOG_ENDPOINT, is used. The repository should exist or not
    (depending on the should_exist parameter). (2) If the check_param == 'narrativeId', check for 'repository'
    and 'narrativeId' query parameters. Then, check that a graph with the narrativeId exists or not in the
    specified repository (depending on the should_exist parameter) in that database. (3) If the check_param ==
    'news', validate that the contents of 'from' and 'to' are of the form, YYYY-mm-dd. Also verify that
    'topic' is not blank.

    :param check_param: String indicating the argument name ('repository', 'narrativeId', 'news')
    :param should_exist: If true, indicates that the entity SHOULD exist
    :param req: Flask Request
    :return: If an error is encountered, a Flask JSON Response and status code are returned; If the
             argument is found and valid, its value (a string or boolean) is returned and the integer, 200
    """
    args_dict = req.args.to_dict()
    if check_param in (repository, narrative_id):
        if not check_server_status():
            return {error_str: f'Database server at the address in the environment variable, STARDOG_ENDPOINT'}, 404
    elif check_param == 'news':
        if 'topic' not in args_dict or not args_dict['topic'] or 'fromDate' not in args_dict \
                or 'toDate' not in args_dict:
            return {error_str: 'invalid',
                    detail: f'The query parameters, topic, fromDate and toDate, must all be specified'}, 400
        if not _check_from_to_date(args_dict['fromDate']) or not _check_from_to_date(args_dict['toDate']):
            return {error_str: 'invalid',
                    detail: f'The query parameters, fromDate and toDate, must use recent/valid dates '
                            f'written as YYYY-mm-dd'}, 400
        result_dict = dict()
        result_dict['topic'] = args_dict['topic']
        result_dict['fromDate'] = args_dict['fromDate']
        result_dict['toDate'] = args_dict['toDate']
        return result_dict, 200
    # Checking for repository and/or narrativeId
    if check_param in (repository, narrative_id):
        if repository not in args_dict:
            return {error_str: 'missing',
                    detail: 'The argument parameter, repository, is required'}, 400
        repo = args_dict[repository]
        repo_exists = _entity_exists(repo)
        if ((check_param == repository and should_exist) or check_param == narrative_id) and not repo_exists:
            return {error_str: f'Repository with the name, {repo}, was not found'}, 404
        if check_param == repository:
            if not should_exist and repo_exists:
                return {error_str: f'Repository with the name, {repo}, already exists'}, \
                    409
            return {repository: repo}, 200
        # Check for narrativeId
        if check_param == narrative_id:
            if narrative_id not in args_dict:
                return {error_str: 'missing',
                        detail: 'The argument parameter, narrativeId, is required'}, 400
            narr = args_dict[narrative_id]
            narr_exists = _entity_exists(repo, narr)
            if should_exist and not narr_exists:
                return {error_str:
                        f'Narrative with the id, {narr}, was not found in {repo}'}, \
                    404
            elif not should_exist and repo_exists:
                return {error_str:
                        f'Narrative with the id, {narr}, already exists in {repo}'}, \
                    409
            return {repository: repo, narrative_id: narr}, 200
    return dict(), 200


def get_metadata_ttl(repo: str, narr_id: str, narr: str, narr_details: list) -> (bool, list, str, int):
    """
    Add the meta-data triples for a narrative to the specified database of the server.

    :param repo: The repository name
    :param narr_id: String identifying the narrative/narrative graph
    :param narr: String holding the text of the narrative
    :param narr_details: Array holding the details related to the original text -
                         The order of the entries are title, date published,
                         source/publisher, url and length of text
    :return: A tuple holding a success boolean (T/F), a list of Turtle statements defining
             the metadata, a string indicated the date/time created and a count of the number
             of triples in the narrative graph
    """
    created_at = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    numb_triples_results = query_database('select', count_triples.replace('?g', f':{repo}_{narr_id}'), repo)
    if len(numb_triples_results) > 0:
        numb_triples = numb_triples_results[0]['cnt']['value']
    else:
        return False, [], empty_string, 0
    turtle = ttl_prefixes[:]
    turtle.extend([f':{narr_id} a :InformationGraph ; dc:created "{created_at}"^^xsd:dateTime ; ',
                   f':number_triples {numb_triples} ; :encodes :Narrative_{narr_id} .',
                   f':Narrative_{narr_id} a :Narrative ; '
                   f':source "{narr_details[2]}" ; :external_link "{narr_details[3]}" ; '
                   f'dc:title "{narr_details[0]}" ; :number_characters {narr_details[4]} .',
                   f':Narrative_{narr_id} :text "{narr}" .'])
    if narr_details[1] != 'not defined':
        turtle.append(f':Narrative_{narr_id} dc:created "{narr_details[1]}"^^xsd:dateTime .')
    goal_dict = access_api(narr_prompt.replace("{narr_text}", narr))
    summary = goal_dict['summary']
    turtle.append(f':Narrative_{narr_id} :summary "{summary}" .')
    for goal in goal_dict['goal_numbers']:
        turtle.append(f':Narrative_{narr_id} :narrative_goal "{narrative_goals[goal - 1]}" .')
    for device_detail in goal_dict['rhetorical_devices']:
        device_numb = device_detail['device_number']
        predicate = ':rhetorical_device {:evidence "' + device_detail['evidence'] + '"} '
        turtle.append(f':Narrative_{narr_id} {predicate} "{rhetorical_devices[device_numb - 1]}" .')
    for key in goal_dict:
        if 'interpretation' in key:
            interpretation_strs = key.split('_interpretation')
            edge = '{:view "' + interpretation_strs[0] + '"}'
            turtle.append(f':Narrative_{narr_id} :interpretation {edge} "{goal_dict[key]}" .')
    return True, turtle, created_at, numb_triples


def parse_narrative_query_binding(binding_set: dict) -> dict:
    """
    Returns a dictionary holding the DNA result encoding of a narrative's metadata.

    :param binding_set: A binding set from the query results for 'query_narratives'
    :return: The dictionary with the encoding of the data from the binding set
    """
    return {narrative_id: binding_set['narrative']['value'].split(':')[-1],
            'processed': binding_set['created']['value'],
            'numberOfTriples': binding_set['numbTriples']['value'],
            'narrativeMetadata': {'title': binding_set['title']['value'],
                                  'published': binding_set['published']['value'],
                                  'source': binding_set['source']['value'],
                                  'url': binding_set['url']['value'],
                                  'length': binding_set['length']['value']}}


def process_new_narrative(metadata: list, narr_text: str, repo: str) -> (dict, str, int):
    """
    Performs the sentence and quotation extractions and analysis, adding a narrative to
    the database with the specified name and address.

    :param metadata: Array holding the details related to the original text - The order of the entries
                     are title, date published, source/publisher, url and length of text
    :param narr_text: String holding the narrative text
    :param repo: String holding the repository name for the narrative graph
    :return: A tuple consisting of a dictionary with the details for the narrative added
             to the database, an error message if an error occurred or an empty string, and an
             integer holding the HTTP status code
    """
    # Future: Do we care if a narrative with this or similar metadata already exists?
    # TODO: Check that the text is not similar since the same article could be picked up by different publishers
    # Process first 1000 characters   TODO: Are 1000 chars enough?
    if int(metadata[4]) > 1000:
        length = 1250
        narr = narr_text[:1000]
        # End on a '.' vs potentially a partial sentence (ideally end on '. ')
        # TODO: Some publishers do not have spaces after periods if on paragraph boundary, in schema.org/articleBody
        narr = narr[0:(narr.rindex('.') + 1)]
    else:
        length = metadata[4]
        narr = narr_text
    graph_uuid = str(uuid.uuid4())[:8]   # IRI of the named graph for the narrative, and the narrative itself
    title = metadata[0]
    logging.info(f'Ingesting {title} to {repo}')
    sentence_dicts, quotations, quotations_dict = parse_narrative(narr)
    success, graph_ttl = create_graph(quotations_dict, sentence_dicts)
    if not success:
        return dict(), f'Error creating the graph for {title}', 500
    logging.info('Loading knowledge graph')
    msg = add_remove_data('add', ' '.join(graph_ttl), repo, graph_uuid)   # Add to dna db's repo_graphUUID graph
    if msg:
        return dict(), f'Error loading the narrative graph {graph_uuid}: {msg}', 500
    # Process the metadata and add individual quotes to the meta-db
    logging.info("Loading metadata")
    success, meta_ttl, created, numb_triples = get_metadata_ttl(repo, graph_uuid, narr, metadata)
    if not success:
        return dict(), f'Error creating the metadata for {title}', 500
    for quotation in quotations:
        meta_ttl.append(f':{graph_uuid} :text_quote "{quotation}" .')
    msg = add_remove_data('add', ' '.join(meta_ttl), repo)   # Add to dna db's repo graph
    if msg:
        return dict(), f'Error adding metadata for {title}: {msg}', 500
    # All is successful
    resp_dict = {repository: repo,
                 'narrativeDetails': {
                     narrative_id: graph_uuid, 'processed': created, 'numberOfTriples': numb_triples,
                     'narrativeMetadata': {'title': title, 'published': metadata[1],
                                           'source': metadata[2], 'url': metadata[3],
                                           'length': length}}}
    return resp_dict, empty_string, 201
