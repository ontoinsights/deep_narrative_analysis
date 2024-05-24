# Main application processing

from datetime import datetime
from flask import Flask, Request, Response, jsonify, request
import json
import logging

from dna.app_functions import check_query_parameter, parse_narrative_query_binding, process_new_narrative, \
    detail, error_str, narrative_id, repository, sentences
from dna.database import add_remove_data, clear_data, construct_graph, query_database
from dna.database_queries import construct_kg, count_triples, delete_narrative, delete_repo_metadata, \
    query_narratives, query_repos, query_repo_graphs, update_narrative
from dna.sentence_element_classes import Metadata
# from dna.query_news import get_article_text, get_matching_articles
from dna.utilities_and_language_specific import dna_prefix, empty_string, meta_graph

logging.basicConfig(level=logging.INFO, filename='dna.log',
                    format='%(funcName)s - %(levelname)s - %(asctime)s - %(message)s')

not_defined: str = 'not defined'

# Main
app = Flask(__name__)
# Future: Deal with concurrency, caching, etc. for production; Move to Nginx and WSGI protocol


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
        query_database('update', delete_repo_metadata.replace('?repo', f':{repo}'), empty_string)
        # Delete all the named graphs for the repository
        graph_bindings = query_database('select', query_repo_graphs.replace('?repo', repo), empty_string)
        if graph_bindings and 'exception' in graph_bindings[0]:
            return jsonify({error_str: graph_bindings[0]}), 500
        for binding in graph_bindings:
            # Delete the graph
            clear_data(repo, binding['g']['value'].split(f'{repo}_')[1])
        return jsonify({'deleted': repo}), 200
    elif request.method == 'GET':
        logging.info(f'Repository list')
        repo_bindings = query_database('select', query_repos, empty_string)
        if repo_bindings and 'exception' in repo_bindings[0]:
            return jsonify({error_str: repo_bindings[0]}), 500
        repo_list = []
        for binding in repo_bindings:
            repo_list.append({repository: binding['repo']['value'].replace(dna_prefix, ''),
                              'created': binding['created']['value']})
        return jsonify(repo_list), 200
    return jsonify({error_str: '/repositories API only supports GET, POST and DELETE requests'}), 405


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
        number_sentences = dict(values)[sentences]
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
        logging.info(f'narr_data {type(narr_data)} {narr_data}')
        metadata = Metadata(narr_data['title'], narr_data['published'] if 'published' in narr_data else not_defined,
                            narr_data['source'], narr_data['url'] if 'url' in narr_data else not_defined,
                            number_sentences)
        resp_dict, resp_str, status_code = process_new_narrative(metadata, narr_data['text'], repo)
        if status_code != 201:
            return jsonify({error_str: resp_str}), status_code
        return jsonify(resp_dict), 201
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
                       .replace('narr_id', narr_id), repo)
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
        narrative_bindings = query_database('select', query_text, repo)
        if narrative_bindings and 'exception' in narrative_bindings[0]:
            return jsonify({error_str: narrative_bindings[0]}), 500
        narr_list = []
        if len(narrative_bindings) > 0:
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
        success, turtle = construct_graph(construct_kg.replace('?named', f':{repo}_{narr_id}'), repo)
        if success:
            # Get narrative metadata
            metadata_dict = parse_narrative_query_binding(
                query_database('select', query_narratives.replace('?named', f':{repo}_default')
                               .replace('?graph', f':{narr_id}'), repo)[0])
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
                               .replace('?s', f':{narr_id}'), repo)
                modified_at = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
                numb_triples_results = query_database('select', count_triples.replace('?g', f':{repo}_{narr_id}'), repo)
                numb_triples = 0
                if len(numb_triples_results) > 0:
                    numb_triples = numb_triples_results[0]['cnt']['value']
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
