# Main application processing

from datetime import datetime
from flask import Flask, Request, Response, jsonify, request
import json
import logging
from typing import Union
import uuid

from dna.create_narrative_turtle import create_graph
from dna.create_specific_turtle import create_metadata_ttl, create_quotations_ttl
from dna.database import add_remove_data, clear_data, construct_database, create_delete_database, query_database
from dna.nlp import parse_narrative
from dna.queries import construct_kg, count_triples, delete_entity, query_narratives, query_dbs, update_narrative
from dna.utilities_and_language_specific import dna_prefix, empty_string, ttl_prefixes

logging.basicConfig(level=logging.INFO, filename='dna.log',
                    format='%(funcName)s - %(levelname)s - %(asctime)s - %(message)s')

detail = 'detail'
error_str = 'error'
ext_sources = 'extSources'
meta_db = 'meta-dna'
narrative_id = 'narrativeId'
not_defined = 'not defined'
repository = 'repository'
is_biography = 'isBiography'


def _check_query_parameter(check_param: str, should_exist: bool, req: Request) -> (Union[dict, str, bool], int):
    """
    Check that the specified query parameter is defined. (1) If the parameter == 'repository',
    check that a query parameter for 'repository' is defined and that a Stardog database with the
    specified name exists or not (depending on the should_exist parameter). (2) If the parameter ==
    'narrativeId', check for both 'repository' and 'narrativeId' query parameters, that a Stardog
    database exists with the specified repository name, and that a graph with the narrativeId exists
    or not (depending on the should_exist parameter) in that database. (3) If the parameter ==
    'extSources' or 'isBiography', check whether a query parameter with that string is defined
    and that its value is either 'true' or 'false'.

    :param check_param: String indicating the argument name ('repository', 'narrativeId',
                        'extSources' or 'isBiography')
    :param should_exist: If true, indicates that the entity SHOULD exist
    :param req: Flask Request
    :return: If an error is encountered, a Flask JSON Response and status code are returned; If the
             argument is found and valid, its value (a string or boolean) is returned and the integer, 200
    """
    args_dict = req.args.to_dict()
    if check_param in (ext_sources, is_biography):
        # Checking for optional, boolean value
        if check_param in args_dict:
            arg_value = args_dict[check_param]
            if arg_value == 'true':
                return True, 200
            elif arg_value == 'false':
                return False, 200
            else:
                return {error_str: 'invalid',
                        detail: f'The argument parameter, {check_param}, must be =true or =false'}, 400
        else:
            return False, 200
    # Checking for repository or repository and narrativeId
    if repository not in args_dict:
        return {error_str: 'missing',
                detail: 'The argument parameter, repository, is required'}, 400
    repo = args_dict[repository]
    repo_exists = _entity_exists(repo)
    if ((check_param == repository and should_exist) or check_param == narrative_id) and not repo_exists:
        return {error_str: f'Repository with the name, {repo}, was not found'}, 404
    if check_param == repository:
        if not should_exist and repo_exists:
            return {error_str: f'Repository with the name, {repo}, already exists'}, 409
        else:
            return {repository: repo}, 200
    # Check for narrativeId
    if narrative_id not in args_dict:
        return {error_str: 'missing',
                detail: 'The argument parameter, narrativeId, is required'}, 400
    narr = args_dict[narrative_id]
    narr_exists = _entity_exists(repo, narr)
    if should_exist and not narr_exists:
        return {error_str: f'Narrative with the id, {narr}, was not found in {repo}'}, 404
    elif not should_exist and repo_exists:
        return {error_str: f'Narrative with the id, {narr}, already exists in {repo}'}, 409
    else:
        return {repository: repo, narrative_id: narr}, 200


def _delete_data(db: str, graph: str = empty_string) -> (Response, int):
    """
    Delete either an entire database (if a graph name is not defined) or the specified
    graph in the database.

    :param db: Database to be deleted or where the narrative graph is found
    :param graph: String identifying the narrative/narrative graph
    :return: Flask JSON response and status code
    """
    if graph:
        failure = clear_data(db, f'urn:ontoinsights:dna:{graph}')    # Empty string is returned if successful
    else:
        msg = create_delete_database('delete', db)
        failure = False if 'deleted at' in msg else True
    if not failure:
        if graph:
            query_database('update', delete_entity.replace('?s', f':{graph}'), db)
            del_results = query_database('update', delete_entity.replace('?s', f':Narrative_{graph}'), db)
        else:
            del_results = query_database('update', delete_entity.replace('?s', f':{db}'), meta_db)
        if del_results[0] == 'successful':
            if graph:
                resp_dict = {'repository': db, 'deleted': graph}
            else:
                resp_dict = {'deleted': db}
            return jsonify(resp_dict), 200
        else:
            return jsonify({error_str: del_results[0]}), 500
    else:
        return jsonify({error_str: failure}), 500


def _entity_exists(db: str, graph: str = empty_string) -> bool:
    """
    Validate that the database exists, if no graph id is provided, or that the specified
    graph exists in the database.

    :param db: Database to be validated or where the narrative graph is found
    :param graph: String identifying the narrative/narrative graph
    :return: True if the database or graph exists, False otherwise
    """
    if graph:
        bindings = query_database('select', query_narratives.replace('?graph', f':{graph}'), db)
    else:
        bindings = query_database('select', query_dbs.replace('?db', f':{db}'), meta_db)
    if bindings:
        return True
    else:
        return False


def _handle_narrative_metadata(db: str, narr_id: str, narr: str, narr_details: list) -> (Response, int):
    """
    Add the meta-data triples for a narrative to the specified database. In the future, this metadata
    may be retrieved from a news service or web scraping.

    :param db: Database where the meta-data and narrative graph are found
    :param narr_id: String identifying the narrative/narrative graph
    :param narr: String holding the text of the narrative
    :param narr_details: Array holding the details related to the original text -
                         The order of the entries are author, date published, publisher, source and title
    :return: Flask JSON response and status code
    """
    created_at = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    numb_triples_results = query_database(
        'select', count_triples.replace('?g', f':{narr_id}'), db)
    numb_triples = 0
    if len(numb_triples_results) > 0:
        numb_triples = numb_triples_results[0]['cnt']['value']
    meta_ttl = create_metadata_ttl(narr_id, narr, created_at, numb_triples, narr_details)
    meta_msg = add_remove_data('add', ' '.join(meta_ttl), db)
    if not meta_msg:
        resp_dict = {repository: db,
                     narrative_id: narr_id,
                     'processed': created_at,
                     'numberOfTriples': numb_triples,
                     'narrativeMetadata': {'author': narr_details[0],
                                           'published': narr_details[1],
                                           'publisher': narr_details[2],
                                           'source': narr_details[3],
                                           'title': narr_details[4]}}
        return jsonify(resp_dict), 201
    else:
        return jsonify({error_str: f'Error adding narrative metadata {narr_id}: {meta_msg}'}), 500


def _parse_narrative_query_binding(binding_set: dict) -> dict:
    """
    Returns a dictionary holding the DNA result encoding of a narrative's metadata.

    :param binding_set: A binding set from the query results for 'query_narratives'
    :return: The dictionary with the encoding of the data from the binding set
    """
    return {narrative_id: binding_set['narrId']['value'].split(':')[-1],
            'processed': binding_set['created']['value'],
            'numberOfTriples': binding_set['numbTriples']['value'],
            'narrativeMetadata': {'author': binding_set['author']['value'],
                                  'published': binding_set['created']['value'],
                                  'publisher': binding_set['publisher']['value'],
                                  'source': binding_set['source']['value'],
                                  'title': binding_set['title']['value']}}


# Main
app = Flask(__name__)
# Future: Deal with concurrency, caching, etc. for production; Move to Nginx and WSGI protocol


@app.route('/dna/v1')
def index():
    return \
        '<h1>Deep Narrative Analysis APIs V1.0.5</h1> ' \
        '<div>DNA APIs to ingest and manage repositories and the narratives within them. <br /><br />' \
        'For detailed information about the APIs, see the ' \
        '<a href="https://ontoinsights.github.io/dna-swagger/">Swagger/YAML documentation</a>.'


@app.route('/dna/v1/repositories', methods=['GET', 'POST', 'DELETE'])
def repositories():
    if request.method == 'POST':
        # Get repository name query parameter
        value, scode = _check_query_parameter(repository, False, request)
        if scode in (400, 409):
            return jsonify(dict(value)), scode
        repo = dict(value)[repository]
        logging.info(f'Creating database, {repo}')
        create_msg = create_delete_database('create', repo)
        if 'created at' in create_msg:
            # Add details to meta-db
            created_at = create_msg.split('created at ')[1]
            triples = f'@prefix : <urn:ontoinsights:dna:> . @prefix dc: <http://purl.org/dc/terms/> . ' \
                      f':{repo} a :Database ; dc:created "{created_at}"^^xsd:dateTime .'
            triples_msg = add_remove_data('add', triples, meta_db)
            if not triples_msg:     # Successful
                return jsonify({'created': repo}), 201
            else:
                return jsonify({error_str: triples_msg}), 500
        else:
            return jsonify({error_str: create_msg}), 500
    elif request.method == 'DELETE':
        # Get repository name query parameter
        value, scode = _check_query_parameter(repository, True, request)
        if scode in (400, 404):
            return jsonify(dict(value)), scode
        repo = dict(value)[repository]
        logging.info(f'Deleting database, {repo}')
        return _delete_data(repo)
    elif request.method == 'GET':
        # Get repository name query parameter
        logging.info(f'Database list')
        db_bindings = query_database('select', query_dbs, meta_db)
        if db_bindings and 'exception' in db_bindings[0]:
            return jsonify({error_str: db_bindings[0]}), 500
        db_list = []
        if len(db_bindings) > 0:
            for binding in db_bindings:
                db_dict = {repository: binding['db']['value'].replace(dna_prefix, ''),
                           'created': binding['created']['value']}
                db_list.append(db_dict)
        return jsonify(db_list), 200
    else:
        return jsonify({error_str: '/repositories API only supports GET, POST and DELETE requests'}), 405


@app.route('/dna/v1/repositories/narratives', methods=['GET', 'POST', 'DELETE'])
def narratives():
    if request.method == 'POST':
        # Get repository name query parameter
        value, scode = _check_query_parameter(repository, True, request)
        if scode in (400, 404, 409):
            return jsonify(dict(value)), scode
        repo = dict(value)[repository]
        value, scode = _check_query_parameter(ext_sources, False, request)
        if scode == 400:
            return jsonify(dict(value)), 400
        use_sources = value
        value, scode = _check_query_parameter(is_biography, False, request)
        if scode == 400:
            return jsonify(dict(value)), 400
        is_bio = value
        # Get text from request body
        if not request.data:
            return jsonify(
                {error_str: 'missing',
                 detail: 'A request body MUST be defined when issuing a /narratives POST.'}), 400
        narr_data = json.loads(request.data)
        if 'narrative' not in narr_data:
            return jsonify(
                {error_str: 'missing',
                 detail: 'A narrative element MUST be present in the request body of a /narratives POST.'}), 400
        if 'narrativeMetadata' not in narr_data:
            title = 'No title provided'
            narr_details = [not_defined, not_defined, not_defined, not_defined, title]
        else:
            narr_meta = narr_data['narrativeMetadata']
            title = narr_meta['title'] if 'title' in narr_meta else not_defined
            narr_details = [narr_meta['author'] if 'author' in narr_meta else not_defined,
                            narr_meta['published'] if 'published' in narr_meta else not_defined,
                            narr_meta['publisher'] if 'publisher' in narr_meta else not_defined,
                            narr_meta['source'] if 'source' in narr_meta else not_defined,
                            title]
        # Future: Do we care if a narrative with this or similar metadata already exists?
        narr = narr_data['narrative']
        logging.info(f'Ingesting {title} to {repo}')
        sentence_dicts, quotations, quotations_dict, family_dict = parse_narrative(narr)
        success, graph_ttl = create_graph(sentence_dicts, family_dict, narr_details[1], use_sources, is_bio)
        logging.info('Loading knowledge graph')
        if success:
            # Add the triples to the data store, to a named graph with name = dna:graph_uuid
            graph_uuid = str(uuid.uuid4())[:8]
            msg = add_remove_data('add', ' '.join(graph_ttl), repo, f'urn:ontoinsights:dna:{graph_uuid}')
            if not msg:
                # Successful, so process the quotations and add them to the default/meta-data graph and
                #    specific narrative graph
                logging.info("Loading quotations")
                quotation_ttl = ttl_prefixes[:]
                create_quotations_ttl(graph_uuid, quotations, quotations_dict, quotation_ttl, True)
                msg = add_remove_data('add', ' '.join(quotation_ttl), repo)
                if msg:
                    return jsonify({error_str: f'Error adding quotations to the repository {repo}: {msg}'}), 500
                create_quotations_ttl(graph_uuid, quotations, quotations_dict, quotation_ttl, False)
                msg = add_remove_data('add', ' '.join(quotation_ttl), repo, f'urn:ontoinsights:dna:{graph_uuid}')
                if msg:
                    return jsonify({error_str: f'Error adding quotations to narrative graph {graph_uuid}: {msg}'}), 500
                # Add meta-data to the default graph in the database
                logging.info("Loading metadata")
                return _handle_narrative_metadata(repo, graph_uuid, narr, narr_details)
            if msg:
                return jsonify({error_str: f'Error adding narrative graph {graph_uuid}: {msg}'}), 500
        else:
            return jsonify({error_str: f'Error parsing the sentence dictionaries for {title}'}), 500
    elif request.method == 'DELETE':
        # Get repository name and narrative id query parameters
        value, scode = _check_query_parameter(narrative_id, True, request)
        if scode in (400, 404, 409):
            return jsonify(dict(value)), scode
        repo = dict(value)[repository]
        narr_id = dict(value)[narrative_id]
        logging.info(f'Deleting narrative, {narr_id}, in {repo}')
        return _delete_data(repo, narr_id)
    elif request.method == 'GET':
        # Get repository name query parameter
        value, scode = _check_query_parameter(repository, True, request)
        if scode in (400, 404, 409):
            return jsonify(dict(value)), scode
        repo = dict(value)[repository]
        logging.info(f'Narrative list for {repo}')
        narrative_bindings = query_database('select', query_narratives, repo)
        if narrative_bindings and 'exception' in narrative_bindings[0]:
            return jsonify({error_str: narrative_bindings[0]}), 500
        narr_list = []
        if len(narrative_bindings) > 0:
            for binding in narrative_bindings:
                narr_list.append(_parse_narrative_query_binding(binding))
        return jsonify({repository: repo, 'narratives': narr_list}), 200
    else:
        return jsonify({error_str: '/repositories/narratives API only supports GET, POST and DELETE requests'}), 405


@app.route('/dna/v1/repositories/narratives/graphs', methods=['GET', 'PUT'])
def graphs():
    if request.method == 'GET':
        # Get repository name and narrative id query parameters
        value, scode = _check_query_parameter(narrative_id, True, request)
        if scode in (400, 404, 409):
            return jsonify(dict(value)), scode
        repo = dict(value)[repository]
        narr_id = dict(value)[narrative_id]
        logging.info(f'Get KG for narrative {narr_id} for {repo}')
        success, turtle = construct_database(construct_kg.replace('graph_uuid', narr_id), repo)
        if success:
            # Get narrative metadata
            metadata_dict = _parse_narrative_query_binding(
                query_database('select', query_narratives.replace('?graph', f':{narr_id}'), repo)[0])
            return jsonify({repository: repo, 'narrativeDetails': metadata_dict, 'triples': turtle}), 200
        else:
            return jsonify({error_str: f'Error getting narrative knowledge graph {narr_id}: {turtle[0]}'}), 500
    elif request.method == 'PUT':
        # Get repository name and narrative id query parameters
        value, scode = _check_query_parameter(narrative_id, True, request)
        if scode in (400, 404, 409):
            return jsonify(dict(value)), scode
        repo = dict(value)[repository]
        narr_id = dict(value)[narrative_id]
        # Get triples from request body
        if not request.data:
            return jsonify(
                {error_str: 'missing',
                 detail: 'A request body MUST be defined when issuing a /graphs POST.'}), 400
        req_data = json.loads(request.data)
        if 'triples' not in req_data:
            return jsonify(
                {error_str: 'missing',
                 detail: 'A triples element MUST be present in the request body of a /graphs POST.'}), 400
        logging.info(f'Updating narrative, {narr_id}, in {repo}')
        test_msg = add_remove_data('add', ' '.join(req_data['triples']), repo, f'urn:ontoinsights:dna:test_{narr_id}')
        if not test_msg:     # Successful
            # Delete the test and 'real' narrative graph and recreate the latter
            clear_data(repo, f'urn:ontoinsights:dna:test_{narr_id}')
            clear_msg = clear_data(repo, f'urn:ontoinsights:dna:{narr_id}')
            if clear_msg:
                error = f'Could not remove the triples from the original narrative graph ({narr_id}) in {repo}'
                return jsonify({error_str: error}), 500
            msg = add_remove_data('add', ' '.join(req_data['triples']), repo, f'urn:ontoinsights:dna:{narr_id}')
            if not msg:     # Successfully added data to the narr_id narrative graph
                # Update the narrative meta-data (delete/insert original and new KG created and number of triples)
                query_database('update', update_narrative.replace('?s', f':{narr_id}'), repo)
                created_at = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
                numb_triples_results = query_database('select', count_triples.replace('?g', f':{narr_id}'), repo)
                numb_triples = 0
                if len(numb_triples_results) > 0:
                    numb_triples = numb_triples_results[0]['cnt']['value']
                new_meta_ttl = [
                    f'@prefix : <urn:ontoinsights:dna:> . @prefix dc: <http://purl.org/dc/terms/> .',
                    f':{narr_id} dc:created "{created_at}"^^xsd:dateTime ; :number_triples {numb_triples} .']
                add_msg = add_remove_data('add', ' '.join(new_meta_ttl), repo)
                if not add_msg:    # Successful
                    return jsonify({repository: repo, narrative_id: narr_id, 'processed': created_at,
                                    'numberOfTriples': numb_triples}), 200
                else:
                    error = f'Error updating narrative ({narr_id}) meta-data from {repo}'
                    return jsonify({error_str: error}), 500
        else:
            error = f'Invalid triples; {test_msg}'
            return jsonify({error_str: error}), 500
    else:
        return jsonify({error_str: '/repositories/narratives/graphs API only supports GET and PUT requests'}), 405


if __name__ == '__main__':
    app.run()
