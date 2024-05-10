# Functions used by the app.py processing to validate query parameters and
# begin the process of creating the Turtle definitions (process_new_narrative)

import json
import logging
from rdflib import Literal
import uuid
from datetime import datetime
from flask import Request, Response, jsonify

from dna.create_narrative_turtle import create_graph
from dna.database import add_remove_data, check_server_status, query_database
from dna.database_queries import count_triples, query_narratives, query_repos
from dna.sentence_element_classes import Metadata
from dna.nlp import parse_narrative
from dna.query_openai import access_api, narrative_goals, narrative_summary_prompt, rhetorical_devices
from dna.utilities_and_language_specific import dna_prefix, empty_string, meta_graph, ttl_prefixes

detail: str = 'detail'
error_str: str = 'error'
narrative_id: str = 'narrativeId'
repository: str = 'repository'
sentences: str = 'sentences'


def _check_from_to_date(date_value: str) -> bool:
    """
    Check that the date query parameters ('from' and 'to') are defined and have the format,
    YYYY-mm-dd.

    :param date_value: String holding either the 'from' or 'to' date value from the API
    :return: Boolean indicating if the date has a valid format
    """
    ymd = date_value.split('-')
    if len(ymd) != 3 or len(ymd[0]) != 4:  # Not y-m-d or 4 digit year
        return False
    if any([not ymd[i].isdigit() for i in range(0, 3)]):
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


def check_query_parameter(check_param: str, should_exist: bool, req: Request) -> (dict, int):
    """
    Check that the specified query parameter is defined. (1) If the check_param == 'repository', check
    that a query parameter for 'repository' is defined. A Stardog database at the address specified in
    the environment variable, STARDOG_ENDPOINT, is used. The repository should exist or not
    (depending on the should_exist parameter). (2) If the check_param == 'narrativeId', check for 'repository'
    and 'narrativeId' query parameters. Then, check that a graph with the narrativeId exists (or not) in the
    specified repository (depending on the should_exist parameter) in that database. (3) If the check_param ==
    'news', validate that the contents of 'from' and 'to' are of the form, YYYY-mm-dd. Also verify that
    'topic' is not blank. (4) If the check_param == 'sentences', validate that this is a positive integer.

    :param check_param: String indicating the argument name ('repository', 'narrativeId', 'news', 'sentences')
    :param should_exist: If true, indicates that the entity SHOULD exist
    :param req: Flask Request
    :return: If an error is encountered, a Flask JSON Response (a dictionary for conversion to JSON) and
             status code are returned; If the argument is found and valid, its value is returned as a dictionary
             (for consistency) and the integer, 200
    """
    args_dict = req.args.to_dict()
    if check_param in (repository, narrative_id):
        if not check_server_status():
            return {error_str: f'Database server must be active at the address in the environment variable, '
                               f'STARDOG_ENDPOINT'}, 404
    elif check_param == sentences:
        if sentences not in args_dict:
            return {sentences: 100}, 200
        else:
            if not args_dict[sentences].isdigit() or int(args_dict[sentences]) < 2:
                return {error_str: f'Number of sentences to ingest must be an integer, greater than 1.'}, 400
            return {sentences: int(args_dict[sentences])}, 200
    # Not processing 'news' pending resolution of subscription issues
    # elif check_param == 'news':
    #    if 'topic' not in args_dict or not args_dict['topic'] or 'fromDate' not in args_dict \
    #            or 'toDate' not in args_dict:
    #        return {error_str: 'invalid',
    #                detail: f'The query parameters, topic, fromDate and toDate, must all be specified'}, 400
    #    if not _check_from_to_date(args_dict['fromDate']) or not _check_from_to_date(args_dict['toDate']):
    #        return {error_str: 'invalid',
    #                detail: f'The query parameters, fromDate and toDate, must use recent/valid dates formatted as '
    #                        f'YYYY-mm-dd'}, 400
    #    result_dict = dict()
    #    result_dict['topic'] = args_dict['topic']
    #    result_dict['fromDate'] = args_dict['fromDate']
    #    result_dict['toDate'] = args_dict['toDate']
    #   return result_dict, 200
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


def get_metadata_ttl(repo: str, narr_id: str, narr: str, metadata: Metadata,
                     number_sentences: int, number_ingested: int) -> (bool, list, str, int):
    """
    Add the meta-data triples for a narrative to the specified database of the server.

    :param repo: The repository name
    :param narr_id: String identifying the narrative/narrative graph
    :param narr: String holding the text of the narrative
    :param metadata: Instance of the Metadata Class holding the narrative/article details -
                     title, date published, source/publisher, url and number of sentences to ingest
    :param number_sentences: Integer holding the number of sentences in the narrative/article
    :param number_ingested: Integer holding the actual number of sentences ingested (<= number requested)
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
                   f':Narrative_{narr_id} a :Narrative ; dc:created "{metadata.published}"^^xsd:dateTime ; ',
                   f':number_sentences "{number_sentences}" ; :number_ingested "{number_ingested}" ; '
                   f':source "{metadata.source}" ; dc:title "{metadata.title}" ; :external_link "{metadata.url}" .',
                   f':Narrative_{narr_id} :text {Literal(narr).n3()} .'])
    goal_dict = access_api(narrative_summary_prompt.replace("{narr_text}", narr))
    summary = goal_dict['summary']
    turtle.append(f':Narrative_{narr_id} :summary "{summary}" .')
    for goal in goal_dict['goal_numbers']:
        turtle.append(f':Narrative_{narr_id} :narrative_goal "{narrative_goals[goal - 1]}" .')
    for device_detail in goal_dict['rhetorical_devices']:
        device_numb = int(device_detail['device_number'])
        # TODO: Pending pystardog fix; predicate = ':rhetorical_device {:evidence "' + device_detail['evidence'] + '"}'
        predicate = f':rhetorical_device_{rhetorical_devices[device_numb - 1].replace(" ", "_")}'
        turtle.append(f':Narrative_{narr_id} :rhetorical_device "{rhetorical_devices[device_numb - 1]}" .')
        evidence = device_detail['evidence']
        turtle.append(f':Narrative_{narr_id} {predicate} "{evidence}" .')
    for interpreted_text in goal_dict['interpreted_text']:
        perspective = interpreted_text['perspective']
        interpretation = interpreted_text['interpretation']
        # TODO: Pending pystardog fix; edge = f':interpretation {:view "' + {perspective} + '"}'
        predicate = f':interpretation_{perspective}'
        turtle.append(f':Narrative_{narr_id} {predicate} "{interpretation}" .')
    return True, turtle, created_at, numb_triples


def parse_narrative_query_binding(binding_set: dict) -> dict:
    """
    Returns a dictionary holding the DNA result encoding of a narrative's metadata.

    :param binding_set: A binding set from the query results for 'query_narratives'
    :return: The dictionary with the encoding of the data from the binding set
    """
    return {narrative_id: binding_set['narrative']['value'].split(':Narrative_')[-1],
            'processed': binding_set['created']['value'],
            'numberOfTriples': binding_set['numbTriples']['value'],
            'numberOfSentences': binding_set['sents']['value'],
            'numberIngested': binding_set['ingested']['value'],
            'narrativeMetadata': {'title': binding_set['title']['value'],
                                  'published': binding_set['published']['value'],
                                  'source': binding_set['source']['value'],
                                  'url': binding_set['url']['value']}}


def process_new_narrative(metadata: Metadata, narr: str, repo: str) -> (dict, str, int):
    """
    Performs the sentence and quotation extractions and analysis, adding a narrative to
    the database with the specified name and address.

    :param metadata: Instance of the Metadata Class holding the narrative/article details -
                     title, date published, source/publisher, url and number of sentences to ingest
    :param narr: String holding the narrative text
    :param repo: String holding the repository name for the narrative graph
    :return: A tuple consisting of a dictionary with the details for the narrative added to the
             database (for return in the REST response), an error message if an error occurred or
             an empty string, and an integer holding the HTTP status code
    """
    graph_uuid = str(uuid.uuid4())[:8]   # IRI of the named graph for the narrative, and the narrative itself
    logging.info(f'Ingesting {metadata.title} to {repo}')
    sentence_instance_list, quotation_instance_list, quoted_strings_list = parse_narrative(narr)
    success, actual_sentences, graph_ttl = create_graph(sentence_instance_list, quotation_instance_list,
                                                        metadata.number_to_ingest)
    if not success:
        return dict(), f'Error creating the graph for {metadata.title}', 500
    logging.info('Loading knowledge graph')
    msg = add_remove_data('add', ' '.join(graph_ttl), repo, graph_uuid)   # Add to dna db's repo_graphUUID graph
    if msg:
        logging.info(graph_ttl)
        return dict(), f'Error loading the narrative graph {graph_uuid}: {msg}', 500
    # Process the metadata and add all quote strings to the meta-db
    logging.info("Loading metadata")
    success, meta_ttl, created, numb_triples = get_metadata_ttl(repo, graph_uuid, narr, metadata,
                                                                len(sentence_instance_list), actual_sentences)
    if not success:
        return dict(), f'Error creating the metadata for {metadata.title}', 500
    for quoted_string in quoted_strings_list:
        meta_ttl.append(f':{graph_uuid} :text_quote {Literal(quoted_string).n3()} .')
    msg = add_remove_data('add', ' '.join(meta_ttl), repo)   # Add to dna db's repo graph
    if msg:
        logging.info(meta_ttl)
        return dict(), f'Error adding metadata for {metadata.title}: {msg}', 500
    # All is successful
    resp_dict = {repository: repo,
                 'narrativeDetails': {
                     narrative_id: graph_uuid, 'processed': created, 'numberOfTriples': numb_triples,
                     'numberOfSentences': len(sentence_instance_list), 'numberIngested': actual_sentences,
                     'narrativeMetadata': {'title': metadata.title, 'published': metadata.published,
                                           'source': metadata.source, 'url': metadata.url}}}
    return resp_dict, empty_string, 201
