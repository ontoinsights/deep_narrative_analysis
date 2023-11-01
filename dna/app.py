# Main application processing

from datetime import datetime
from flask import Flask, Request, Response, jsonify, request
import json
import logging
import uuid

from dna.app_functions import check_query_parameter, delete_data, parse_narrative_query_binding, process_new_narrative
from dna.database import add_remove_data, clear_data, construct_database, create_delete_database, query_database
from dna.database_queries import construct_kg, count_triples, delete_db_metadata, delete_narrative, query_dbs, \
    query_narratives, update_narrative
from dna.query_news import get_article_text, get_matching_articles
from dna.utilities_and_language_specific import dna_prefix, empty_string, meta_db

logging.basicConfig(level=logging.INFO, filename='dna.log',
                    format='%(funcName)s - %(levelname)s - %(asctime)s - %(message)s')

detail: str = 'detail'
error_str: str = 'error'
narrative_id: str = 'narrativeId'
not_defined: str = 'not defined'
repository: str = 'repository'

# Main
app = Flask(__name__)
# Future: Deal with concurrency, caching, etc. for production; Move to Nginx and WSGI protocol


@app.route('/dna/v1')
def index():
    return \
        '<h1>Deep Narrative Analysis APIs V1.2</h1> ' \
        '<div>DNA APIs to acquire news, and ingest and manage narratives and news articles. <br /><br />' \
        'For detailed information about the APIs, see the ' \
        '<a href="https://ontoinsights.github.io/dna-swagger/">Swagger/YAML documentation</a>.'


@app.route('/dna/v1/news', methods=['GET', 'POST'])
def news():
    if request.method == 'POST' or request.method == 'GET':
        values, scode = check_query_parameter('news', False, request)
        if scode == 400:
            return jsonify(dict(values)), scode
        news_details = {x: dict(values)[x] for x in ('topic', 'fromDate', 'toDate')}
        repo = empty_string
        if request.method == 'POST':
            # Get repository name query parameter
            values, scode = check_query_parameter(repository, True, request)
            if scode in (400, 404, 409):
                return jsonify(dict(values)), scode
            repo = dict(values)[repository]
            news_details['repository'] = repo
            number_to_ingest = 0
            if 'number' in dict(values):
                number_str = dict(values)['number_to_ingest']
                if number_str.isdigit():
                    number_to_ingest = int(number_str)
                else:
                    return jsonify(
                        {error_str: 'invalid',
                         detail: f'The query parameter, number_to_ingest, must be an integer'}), 400
        articles = get_matching_articles(news_details)   # Array of article metadata dictionaries
        if request.method == 'POST':
            article_number = 0
            failed_retrievals = []
            for article in articles:
                article_text = get_article_text(article['url'])
                if article_text:
                    metadata = [article['title'], article['published'], article['source'], article['url'],
                                article['length']]
                    resp_dict, resp_str, status_code = process_new_narrative(metadata, article_text, repo)
                    if resp_str:
                        failed_retrievals.append(article)
                else:
                    failed_retrievals.append(article)
                article_number += 1
                if number_to_ingest > 0 and article_number == number_ingested:
                    break
            news_details['articles'] = articles
            news_details['failed_articles'] = failed_retrievals
            return jsonify(news_details), 200
        elif request.method == 'GET':
            news_details['articleCount'] = len(articles)
            news_details['articles'] = articles
            return jsonify(news_details), 200
    return jsonify({error_str: '/news API only supports GET and POST requests'}), 405


@app.route('/dna/v1/repositories', methods=['GET', 'POST', 'DELETE'])
def repositories():
    if request.method == 'POST':
        # Get repository name query parameter
        values, scode = check_query_parameter(repository, False, request)
        if scode in (400, 404, 409):
            return jsonify(dict(values)), scode
        repo = dict(values)[repository]
        logging.info(f'Creating database, {repo}')
        create_msg = create_delete_database('create', repo)
        if 'created at' in create_msg:
            # Add details to meta_db
            created_at = create_msg.split('created at ')[1]
            triples = f'@prefix : <{dna_prefix}> . @prefix dc: <http://purl.org/dc/terms/> . ' \
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
        values, scode = check_query_parameter(repository, True, request)
        if scode in (400, 404):
            return jsonify(dict(values)), scode
        repo = dict(values)[repository]
        logging.info(f'Deleting database, {repo}')
        # Delete metadata for the repository in meta_db
        query_database('update', delete_db_metadata.replace('?db', f':{repo}'), meta_db)
        return delete_data(repo)    # Delete the repository
    elif request.method == 'GET':
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
    return jsonify({error_str: '/repositories API only supports GET, POST and DELETE requests'}), 405


@app.route('/dna/v1/repositories/narratives', methods=['GET', 'POST', 'DELETE'])
def narratives():
    if request.method == 'POST':
        # Get repository name query parameter
        values, scode = check_query_parameter(repository, True, request)
        if scode in (400, 404, 409):
            return jsonify(dict(values)), scode
        repo = dict(values)[repository]
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
            narr_details = [title, not_defined, not_defined, not_defined]
        else:
            narr_meta = narr_data['narrativeMetadata']
            title = narr_meta['title'] if 'title' in narr_meta else not_defined
            narr_details = [title,
                            narr_meta['published'] if 'published' in narr_meta else not_defined,
                            narr_meta['source'] if 'source' in narr_meta else not_defined,
                            narr_meta['url'] if 'url' in narr_meta else not_defined,
                            narr_meta['length'] if 'length' in narr_meta else not_defined]
        resp_dict, resp_str, status_code = process_new_narrative(narr_details, narr_data['narrative'], repo)
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
        # Delete the metadata for the narrative in the repository's default graph
        query_database('update', delete_narrative.replace('narr_id', narr_id), repo)
        return delete_data(repo, narr_id)    # Delete the narrative
    elif request.method == 'GET':
        # Get repository name query parameter
        values, scode = check_query_parameter(repository, True, request)
        if scode in (400, 404, 409):
            return jsonify(dict(values)), scode
        repo = dict(values)[repository]
        logging.info(f'Narrative list for {repo}')
        narrative_bindings = query_database('select', query_narratives, repo)
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
        success, turtle = construct_database(construct_kg.replace('?graph', f':{narr_id}'), repo)
        if success:
            # Get narrative metadata
            metadata_dict = parse_narrative_query_binding(
                query_database('select', query_narratives.replace('?graph', f':{narr_id}'), repo)[0])
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
        test_msg = add_remove_data('add', ' '.join(req_data['triples']), repo, f'{dna_prefix}test_{narr_id}')
        if not test_msg:     # Successful
            # Delete the test and 'real' narrative graph and recreate the latter
            clear_data(repo, f'{dna_prefix}test_{narr_id}')
            clear_msg = clear_data(repo, f'{dna_prefix}{narr_id}')
            if clear_msg:
                error = f'Could not remove the triples from the original narrative graph ({narr_id}) in {repo}'
                return jsonify({error_str: error}), 500
            msg = add_remove_data('add', ' '.join(req_data['triples']), repo, f'{dna_prefix}{narr_id}')
            if not msg:     # Successfully added data to the narr_id narrative graph
                # Update the narrative metadata (delete/insert original and new KG created and number of triples)
                query_database('update', update_narrative.replace('?s', f':{narr_id}'), repo)
                created_at = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
                numb_triples_results = query_database('select', count_triples.replace('?g', f':{narr_id}'), repo)
                numb_triples = 0
                if len(numb_triples_results) > 0:
                    numb_triples = numb_triples_results[0]['cnt']['value']
                new_meta_ttl = [
                    f'@prefix : <{dna_prefix}> . @prefix dc: <http://purl.org/dc/terms/> .',
                    f':{narr_id} dc:created "{created_at}"^^xsd:dateTime ; :number_triples {numb_triples} .']
                add_msg = add_remove_data('add', ' '.join(new_meta_ttl), repo)
                if not add_msg:    # Successful
                    return jsonify({repository: repo, narrative_id: narr_id, 'processed': created_at,
                                    'numberOfTriples': numb_triples}), 200
                error = f'Error updating narrative ({narr_id}) metadata from {repo}'
                return jsonify({error_str: error}), 500
        error = f'Invalid triples; {test_msg}'
        return jsonify({error_str: error}), 500
    return jsonify({error_str: '/repositories/narratives/graphs API only supports GET and PUT requests'}), 405


if __name__ == '__main__':
    app.run()
