# Main application processing

from datetime import datetime
from flask import Flask, Request, Response, jsonify, request
import json
import logging
import uuid

from dna.create_narrative_turtle import create_graph
from dna.create_specific_turtle import create_metadata_ttl, create_quotations_ttl
from dna.database import add_remove_data, clear_data, construct_database, create_delete_database, query_database
from dna.nlp import parse_narrative
from dna.queries import construct_kg, count_triples, delete_entity, query_narratives, query_dbs, update_narrative
from dna.utilities import dna_prefix, empty_string

logging.basicConfig(level=logging.INFO, filename='dna.log',
                    format='%(funcName)s - %(levelname)s - %(asctime)s - %(message)s')

error_str = 'error'
meta_db = "meta-dna"
narrative_id = 'narrativeId'
not_defined = "not defined"
repository = 'repository'


def _check_query_parameters(check_narr_id: bool, req: Request, should_exist: list) -> (Response, int):
    """
    Check that the specified query parameters are defined, and if defined and = 'repository'
    or 'narrativeId', check that the specified entity exists.

    :param check_narr_id: Boolean indicating that the arguments should include a narrativeId
    :param req: Flask Request
    :param should_exist: A list holding the names of the entities ('repository' and/or 'narrativeId')
                         that should exist
    :return: Flask JSON response and status code
    """
    # Get repository query parameter (always needed)
    args_dict = req.args.to_dict()
    resp = []
    if repository not in args_dict:    # Always retrieve the repo name
        resp.append(repository)
    # Get narrativeId query parameter (if requested)
    if check_narr_id and narrative_id not in args_dict:
        resp.append(narrative_id)
    if resp:
        return {'missing': resp}, 400
    repo = args_dict[repository]
    repo_exists = _entity_exists(repo)
    if repository in should_exist and not repo_exists:
        return {error_str: f'Repository with the name, {repo}, was not found'}, 404
    elif repository not in should_exist and repo_exists:
        return {error_str: f'Repository with the name, {repo}, already exists'}, 409
    if check_narr_id:
        narr_id = args_dict[narrative_id]
        narr_exists = _entity_exists(repo, narr_id)
        if narrative_id in should_exist and not narr_exists:
            return {error_str: f'Narrative with the id, {narr_id}, was not found in {repo}'}, 404
        elif narrative_id not in should_exist and narr_exists:
            return {error_str: f'Narrative with id, {narr_id}, already exists in {repo}'}, 409
        else:
            return args_dict, 200
    else:
        return args_dict, 200


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
    Add the meta-data triples for a narrative to the specified database.

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
# TODO: Deal with concurrency, caching, etc. for production; Move to Nginx and WSGI protocol


@app.route('/dna/v1')
def index():
    return \
        '<h1>Deep Narrative Analysis APIs V1.0.3</h1> ' \
        '<div>DNA APIs to ingest and manage repositories and the narratives within them. <br /><br />' \
        'For detailed information about the APIs, see the ' \
        '<a href="https://ontoinsights.github.io/dna-swagger/">Swagger/YAML documentation</a>.'


@app.route('/dna/v1/repositories', methods=['GET', 'POST', 'DELETE'])
def repositories():
    if request.method == 'POST':
        # Get repository name query parameter
        args_dict, scode = _check_query_parameters(False, request, [])
        if scode in (400, 409):
            return jsonify(args_dict), scode
        repo = args_dict[repository]
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
        args_dict, scode = _check_query_parameters(False, request, [repository])
        if scode in (400, 404):
            return jsonify(args_dict), scode
        repo = request.args.to_dict()[repository]
        logging.info(f'Deleting database, {repo}')
        return _delete_data(repo)
    elif request.method == 'GET':
        # Get repository name query parameter
        logging.info(f'Database list')
        db_bindings = query_database('select', query_dbs, meta_db)
        if 'exception' in db_bindings[0]:
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
        args_dict, scode = _check_query_parameters(False, request, [repository])
        if scode in (400, 404, 409):
            return jsonify(args_dict), scode
        repo = args_dict[repository]
        use_sources = True if 'extSources' in args_dict and args_dict['extSources'] == 'true' else False
        timeline_poss = True if 'timelinePossible' in args_dict and args_dict['timelinePossible'] == 'true' else False
        # TODO: Check if extSources or timelinePossible only true or false
        # Get text from request body
        if not request.data:
            return jsonify({'missing': ['narrativeText']}), 400
        narr_data = json.loads(request.data)
        if 'narrative' not in narr_data:
            return jsonify({'missing': ['narrativeText']}), 400
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
        sentence_dicts, quotations, quotations_dict = parse_narrative(narr)
        success, graph_ttl = create_graph(sentence_dicts, narr_details[1], use_sources, timeline_poss)
        if success:
            # Add the triples to the data store, to a named graph with name = dna:graph_uuid
            graph_uuid = str(uuid.uuid4())[:8]
            msg = add_remove_data('add', ' '.join(graph_ttl), repo, f'urn:ontoinsights:dna:{graph_uuid}')
            if not msg:
                # Successful, so process the quotations and add them to the graph
                quotation_ttl = create_quotations_ttl(graph_uuid, quotations, quotations_dict)
                msg = add_remove_data('add', ' '.join(quotation_ttl), repo, f'urn:ontoinsights:dna:{graph_uuid}')
                if not msg:
                    # And add meta-data to the default graph in the database
                    return _handle_narrative_metadata(repo, graph_uuid, narr, narr_details)
            if msg:
                return jsonify({error_str: f'Error adding narrative knowledge graph {graph_uuid}: {msg}'}), 500
        else:
            return jsonify({error_str: f'Error parsing the sentence dictionaries for {title}'}), 500
    elif request.method == 'DELETE':
        # Get repository name and narrative id query parameters
        args_dict, scode = _check_query_parameters(True, request, [repository, narrative_id])
        if scode in (400, 404, 409):
            return jsonify(args_dict), scode
        repo = args_dict[repository]
        narr_id = args_dict[narrative_id]
        logging.info(f'Deleting narrative, {narr_id}, in {repo}')
        return _delete_data(repo, narr_id)
    elif request.method == 'GET':
        # Get repository name query parameter
        args_dict, scode = _check_query_parameters(False, request, [repository])
        if scode in (400, 404, 409):
            return jsonify(args_dict), scode
        repo = args_dict[repository]
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
        args_dict, scode = _check_query_parameters(True, request, [repository, narrative_id])
        if scode in (400, 404, 409):
            return jsonify(args_dict), scode
        repo = args_dict[repository]
        narr_id = args_dict[narrative_id]
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
        args_dict, scode = _check_query_parameters(True, request, [repository, narrative_id])
        if scode in (400, 404, 409):
            return jsonify(args_dict), scode
        repo = args_dict[repository]
        narr_id = args_dict[narrative_id]
        # Get triples from request body
        req_data = json.loads(request.data)
        if 'triples' not in req_data:
            return jsonify({'missing': ['narrativeTriples']}), 400
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
