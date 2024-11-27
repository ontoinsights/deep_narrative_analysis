# Main application processing

from datetime import datetime
from flask import Flask, Request, Response, jsonify, request
import json
import logging

from dna.app_functions import check_query_parameter, parse_narrative_query_binding, process_background, \
    process_new_narrative, background_str, detail, error_str, narrative_id, repository, sentences, \
    Metadata, MetadataResults, BackgroundAndNarrativeResults
from dna.database import add_remove_data, clear_data, construct_graph, query_database
from dna.database_queries import construct_kg, count_triples, delete_entity, delete_narrative, \
    delete_repo_metadata, query_background, query_narratives, query_repos, query_repo_graphs, update_narrative
# from dna.query_news import get_article_text, get_matching_articles
from dna.utilities_and_language_specific import dna_prefix, empty_string, meta_graph

logging.basicConfig(level=logging.INFO, filename='dna.log',
                    format='%(funcName)s - %(levelname)s - %(asctime)s - %(message)s')

background_names: str = "backgroundNames"
not_defined: str = 'not defined'

# Main
app = Flask(__name__)
# TODO: (Future) Deal with concurrency, caching, etc. for production; Move to Nginx and WSGI protocol


@app.route('/dna/v1')
def index():
    return \
        '<h1>Deep Narrative Analysis APIs V1.2</h1> ' \
        '<div>DNA APIs to ingest and analyze narratives and news articles. <br /><br />' \
        'For detailed information about the APIs, see the ' \
        '<a href="https://ontoinsights.github.io/dna-swagger/">Swagger/YAML documentation</a>.'


# TODO: Pending resolution of subscription issues
# @app.route('/dna/v1/news', methods=['GET'])
# def news():
#    if request.method == 'GET':
#        values, scode = check_query_parameter('news', False, request)
#        if scode == 400:
#            return jsonify(dict(values)), scode
#        news_details = {x: dict(values)[x] for x in ('topic', 'fromDate', 'toDate')}
#        articles = get_matching_articles(news_details)   # Array of article metadata dictionaries
#        news_details['articleCount'] = len(articles)
#        news_details['articles'] = articles
#       return jsonify(news_details), 200
#    return jsonify({error_str: '/news API only supports GET requests'}), 405


@app.route('/dna/v1/repositories', methods=['GET', 'POST', 'DELETE'])
def repositories():
    if request.method == 'POST':
        # Get repository name query parameter
        values, scode = check_query_parameter(repository, False, request)
        if scode in (400, 404, 409):
            return jsonify(dict(values)), scode
        repo = dict(values)[repository]
        logging.info(f'Creating repository, {repo}')
        # Add details to meta_graph
        created_at = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        triples = f'@prefix : <{dna_prefix}> . @prefix dc: <http://purl.org/dc/terms/> . ' \
                  f':{repo} a :Database ; dc:created "{created_at}"^^xsd:dateTime .'
        triples_msg = add_remove_data('add', triples, empty_string)   # Add triples to dna db, default graph
        if not triples_msg:     # Successful
            return jsonify({'created': repo}), 201
        else:
            return jsonify({error_str: triples_msg}), 500
    elif request.method == 'DELETE':
        # Get repository name query parameter
        values, scode = check_query_parameter(repository, True, request)
        if scode in (400, 404):
            return jsonify(dict(values)), scode
        repo = dict(values)[repository]
        logging.info(f'Deleting repository, {repo}')
        # Delete metadata for the repository in dna db's default graph
        query_database('update', delete_repo_metadata.replace('?repo', f':{repo}'))
        # Delete all the named graphs for the repository
        graph_bindings = query_database('select', query_repo_graphs.replace('?repo', repo))
        if graph_bindings and 'exception' in graph_bindings[0]:
            return jsonify({error_str: graph_bindings[0]}), 500
        for binding in graph_bindings:
            # Delete the graph
            clear_data(repo, binding['g']['value'].split(f'{repo}_')[1])
        return jsonify({'deleted': repo}), 200
    elif request.method == 'GET':
        logging.info(f'Repository list')
        repo_bindings = query_database('select', query_repos)
        if repo_bindings and 'exception' in repo_bindings[0]:
            return jsonify({error_str: repo_bindings[0]}), 500
        repo_list = []
        for binding in repo_bindings:
            repo_list.append({repository: binding['repo']['value'].replace(dna_prefix, ''),
                              'created': binding['created']['value']})
        return jsonify(repo_list), 200
    return jsonify({error_str: '/repositories API only supports GET, POST and DELETE requests'}), 405


@app.route('/dna/v1/repositories/background', methods=['GET', 'POST', 'DELETE'])
def background():
    if request.method == 'POST':
        # Get repository name query parameter
        values, scode = check_query_parameter(repository, True, request)
        if scode in (400, 404, 409):
            return jsonify(dict(values)), scode
        repo = dict(values)[repository]
        # Process the request body
        if not request.data:
            return jsonify(
                {error_str: 'missing',
                 detail: 'A request body MUST be defined when issuing a /background POST.'}), 400
        background_data = json.loads(request.data)
        # TODO: Allow definition of membership in collections
        if 'backgroundNames' not in background_data:
            return jsonify(
                {error_str: 'missing',
                 detail: 'The "backgroundNames" array MUST be specified in the request body '
                         'of a /background POST.'}), 400
        if not background_data[background_names]:
            return jsonify(
                {error_str: 'missing',
                 detail: 'At least one name MUST be specified in the "backgroundNames" property '
                         'in the request body of a /background POST.'}), 400
        logging.info(f'Posting background {background_data}')
        background_results = process_background(background_data[background_names], repo)
        if background_results.http_status != 201:
            return jsonify({error_str: background_results.error_msg}), background_results.http_status
        return jsonify(background_results.resp_dict), 201
    elif request.method == 'DELETE':
        # Get entity name and repository query parameters
        values, scode = check_query_parameter(background_str, True, request)
        if scode in (400, 404, 409):
            return jsonify(dict(values)), scode
        repo = dict(values)[repository]
        entity_name = dict(values)['name']
        logging.info(f'Deleting background entity, {entity_name}, in {repo}')
        # Delete the entity data in the dna db repository_default graph
        query_database('update', delete_entity.replace('?named', f':{repo}_default')
                       .replace('?text_name', entity_name))
        return jsonify({'repository': repo, 'deleted': entity_name}), 200
    elif request.method == 'GET':
        logging.info(f'Background list for {repository}')
        # Get repository name query parameter
        values, scode = check_query_parameter(repository, True, request)
        if scode in (400, 404, 409):
            return jsonify(dict(values)), scode
        repo = dict(values)[repository]
        query_text = query_background.replace('?named', f':{repo}_default')
        background_bindings = query_database('select', query_text)
        if background_bindings and 'exception' in background_bindings[0]:    # In the text
            return jsonify({error_str: background_bindings[0]}), 500
        background_list = []
        for binding in background_bindings:
            entity = {'name': binding['name'],
                      'type': binding['type']}
            if 'plural' in binding:
                entity['isCollection'] = 'true'
            background_list.append(entity)
        return jsonify({repository: repo, background_names: background_list}), 200
    return jsonify({error_str: '/repositories/background API only supports GET, POST and DELETE requests'}), 405


@app.route('/dna/v1/repositories/narratives', methods=['GET', 'POST', 'DELETE'])
def narratives():
    if request.method == 'POST':
        # Get repository name query parameter
        values, scode = check_query_parameter(repository, True, request)
        if scode in (400, 404, 409):
            return jsonify(dict(values)), scode
        repo = dict(values)[repository]
        # Get number of sentences to ingest
        values, scode = check_query_parameter(sentences, False, request)
        number_sentences = int(dict(values)[sentences])
        # Process the request body
        if not request.data:
            return jsonify(
                {error_str: 'missing',
                 detail: 'A request body MUST be defined when issuing a /narratives POST.'}), 400
        narr_data = json.loads(request.data)
        if 'title' not in narr_data or 'source' not in narr_data or 'text' not in narr_data:
            return jsonify(
                {error_str: 'missing',
                 detail: 'A "title", "source" and "text" MUST be specified in the request body '
                         'of a /narratives POST.'}), 400
        logging.info(f'Posting narrative {type(narr_data)} {narr_data["title"]} {narr_data["source"]}')
        metadata = Metadata(narr_data['title'], narr_data['published'] if 'published' in narr_data else not_defined,
                            narr_data['source'], narr_data['url'] if 'url' in narr_data else not_defined,
                            number_sentences)
        narrative_results = process_new_narrative(metadata, narr_data['text'], repo)
        if narrative_results.http_status != 201:
            return jsonify({error_str: narrative_results.error_msg}), narrative_results.http_status
        return jsonify(narrative_results.resp_dict), 201
    elif request.method == 'DELETE':
        # Get repository name and narrative id query parameters
        values, scode = check_query_parameter(narrative_id, True, request)
        if scode in (400, 404, 409):
            return jsonify(dict(values)), scode
        repo = dict(values)[repository]
        narr_id = dict(values)[narrative_id]
        logging.info(f'Deleting narrative, {narr_id}, in {repo}')
        # Delete the metadata for the narrative in the dna db repository_default graph
        query_database('update', delete_narrative.replace('?named', f':{repo}_default')
                       .replace('narr_id', narr_id))
        # Delete the narrative graph
        clear_data(repo, narr_id)
        return jsonify({'repository': repo, 'deleted': narr_id}), 200
    elif request.method == 'GET':
        # Get repository name query parameter
        values, scode = check_query_parameter(repository, True, request)
        if scode in (400, 404, 409):
            return jsonify(dict(values)), scode
        repo = dict(values)[repository]
        logging.info(f'Narrative list for {repo}')
        query_text = query_narratives.replace('?named', f':{repo}_default')
        narrative_bindings = query_database('select', query_text)
        if narrative_bindings and 'exception' in narrative_bindings[0]:
            return jsonify({error_str: narrative_bindings[0]}), 500
        narr_list = []
        for binding in narrative_bindings:
            narr_list.append(parse_narrative_query_binding(binding))
        return jsonify({repository: repo, 'narratives': narr_list}), 200
    return jsonify({error_str: '/repositories/narratives API only supports GET, POST and DELETE requests'}), 405


@app.route('/dna/v1/repositories/narratives/graphs', methods=['GET', 'PUT'])
def graphs():
    if request.method == 'GET':
        # Get repository name and narrative id query parameters
        values, scode = check_query_parameter(narrative_id, True, request)
        if scode in (400, 404, 409):
            return jsonify(dict(values)), scode
        repo = dict(values)[repository]
        narr_id = dict(values)[narrative_id]
        logging.info(f'Get KG for narrative {narr_id} for {repo}')
        # Get the triples from dna db's graph, :repo_narrId
        # TODO: Error in construct with edge properties in pystardog; Currently edge properties removed
        success, turtle = construct_graph(construct_kg.replace('?named', f':{repo}_{narr_id}'))
        if success:
            # Get narrative metadata
            metadata_dict = parse_narrative_query_binding(
                query_database('select', query_narratives.replace('?named', f':{repo}_default')
                               .replace('?graph', f':{narr_id}'))[0])
            return jsonify({repository: repo, 'narrativeDetails': metadata_dict, 'triples': turtle}), 200
        return jsonify({error_str: f'Error getting narrative knowledge graph {narr_id}: {turtle[0]}'}), 500
    elif request.method == 'PUT':
        # Get repository name and narrative id query parameters
        values, scode = check_query_parameter(narrative_id, True, request)
        if scode in (400, 404, 409):
            return jsonify(dict(values)), scode
        repo = dict(values)[repository]
        narr_id = dict(values)[narrative_id]
        # Get triples from request body
        if not request.data:
            return jsonify({error_str: 'missing',
                            detail: 'A request body MUST be defined when issuing a /graphs POST.'}), 400
        req_data = json.loads(request.data)
        if 'triples' not in req_data:
            return jsonify(
                {error_str: 'missing',
                 detail: 'A triples element MUST be present in the request body of a /graphs POST.'}), 400
        logging.info(f'Updating narrative, {narr_id}, in {repo}')
        # Add triples to dna db's graph, :repo_test_narrId
        test_msg = add_remove_data('add', ' '.join(req_data['triples']), repo, f'test_{narr_id}')
        if not test_msg:     # Successful
            # Delete the test and 'real' narrative graph and recreate the latter
            clear_data(repo, f'test_{narr_id}')
            clear_msg = clear_data(repo, narr_id)
            if clear_msg:
                error = f'Could not remove the triples from the original narrative graph ({narr_id}) in {repo}'
                return jsonify({error_str: error}), 500
            # Add triples to dna db's graph, :repo_narrId
            msg = add_remove_data('add', ' '.join(req_data['triples']), repo, narr_id)
            if not msg:     # Successfully added data to the narr_id narrative graph
                # Update the narrative metadata (delete/insert original and new KG created and number of triples)
                query_database('update', update_narrative.replace('?g', f':{repo}_default')
                               .replace('?s', f':{narr_id}'))
                modified_at = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
                numb_triples_results = query_database('select', count_triples.replace('?g', f':{repo}_{narr_id}'))
                numb_triples = 0
                if len(numb_triples_results) > 0:
                    numb_triples = int(numb_triples_results[0]['cnt']['value'])
                new_meta_ttl = [
                    f'@prefix : <{dna_prefix}> . @prefix dc: <http://purl.org/dc/terms/> .',
                    f':{narr_id} dc:modified "{modified_at}"^^xsd:dateTime ; :number_triples {numb_triples} .']
                add_msg = add_remove_data('add', ' '.join(new_meta_ttl), repo)   # Add narr metadata to :repo_default
                if not add_msg:    # Successful
                    return jsonify({repository: repo, narrative_id: narr_id, 'processed': modified_at,
                                    'numberOfTriples': numb_triples}), 200
                error = f'Error updating narrative ({narr_id}) metadata from {repo}'
                return jsonify({error_str: error}), 500
        error = f'Invalid triples; {test_msg}'
        return jsonify({error_str: error}), 500
    return jsonify({error_str: '/repositories/narratives/graphs API only supports GET and PUT requests'}), 405


if __name__ == '__main__':
    app.run()
