# Functions used by the app.py processing to validate query parameters and
# begin the process of creating the Turtle definitions (process_new_narrative)

import json
import logging
from dataclasses import dataclass

import uuid
from datetime import datetime
from flask import Request, Response, jsonify

from dna.create_narrative_turtle import create_graph, nouns_preload
from dna.database import add_remove_data, check_server_status, query_database
from dna.database_queries import count_triples, query_narratives, query_repos
from dna.nlp import parse_narrative
from dna.process_entities import process_ner_entities
from dna.query_openai import access_api, narrative_goals, narrative_summary_prompt
from dna.sentence_classes import Entity
from dna.utilities_and_language_specific import dna_prefix, empty_string, literal, meta_graph, ttl_prefixes

background_str: str = 'background'
detail: str = 'detail'
error_str: str = 'error'
narrative_id: str = 'narrativeId'
repository: str = 'repository'
sentences: str = 'sentences'

background_type_mapping = {
    "law": "LAW",
    "organization": "ORG",
    "person": "PERSON",
    "place": "LOC",
    "thing": "PRODUCT",
    "norp": "NORP"
}

@dataclass
class BackgroundAndNarrativeResults:
    """
    Dataclass holding the results of the process_background and process_new_narrative functions
    """
    resp_dict: dict           # Dictionary with the details for the background data or narrative
                              #   (for return in the REST response)
    error_msg: str            # Error message if an error occurred or an empty string
    http_status: int          # The HTTP status code (for return in the REST response)

@dataclass
class Metadata:
    """
    Dataclass holding metadata details for a narrative/article
    """
    title: str                    # Narrative/article title
    published: str                # Date/time published
    source: str                   # Source (such as 'CNN', free-form)
    url: str                      # Online location
    number_to_ingest: int         # Number of sentences to ingest

@dataclass
class MetadataResults:
    """
    Dataclass holding the results of the get_metadata_ttl function
    """
    success: bool               # Success boolean
    turtle: list                # List of Turtle statements defining the metadata
    created: str                # String indicated the date/time that the metadata RDF was created
    number_triples: int         # Count of the number of triples in the narrative graph


# Future
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
    :return: True if the database or graph exists, False otherwise
    """
    if graph:
        bindings = query_database('select', query_narratives.replace('?named', f':{repo}_default')
                                  .replace('?graph', f':{graph}'))
    else:
        bindings = query_database('select', query_repos.replace('?repo', f':{repo}'))
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
    'topic' is not blank. (4) If the check_param == 'background', check for 'repository' and 'name'
    query parameters. There is no need to check that the name is actually found in the repository since
    it will be removed. (5) If the check_param == 'sentences', validate that this is a positive integer.

    :param check_param: String indicating the argument name ('repository', 'narrativeId',
                        'background', 'news', 'sentences')
    :param should_exist: If true, indicates that the entity SHOULD exist
    :param req: Flask Request
    :return: If an error is encountered, a Flask JSON Response (a dictionary for conversion to JSON) and
             status code are returned; If the argument is found and valid, its value is returned as a dictionary
             (for consistency) and the integer, 200
    """
    args_dict = req.args.to_dict()
    if check_param in (repository, narrative_id, background_str):
        if not check_server_status():
            return {error_str: f'Database server must be active at the address in the environment variable, '
                               f'STARDOG_ENDPOINT'}, 404
    elif check_param == sentences:
        if sentences not in args_dict:
            return {sentences: 10}, 200
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
    if check_param in (repository, narrative_id, background_str):
        if repository not in args_dict:
            return {error_str: 'missing',
                    detail: 'The argument parameter, repository, is required'}, 400
        repo = args_dict[repository]
        repo_exists = _entity_exists(repo)
        if not repo_exists and ((check_param == repository and should_exist) or
                                check_param in (narrative_id, background_str)):
            return {error_str: f'Repository with the name, {repo}, was not found'}, 404
        if check_param == repository:
            if not should_exist and repo_exists:
                return {error_str: f'Repository with the name, {repo}, already exists'}, 409
            return {repository: repo}, 200
        # Check for narrativeId
        if check_param == narrative_id:
            if narrative_id not in args_dict:
                return {error_str: 'missing',
                        detail: 'The argument parameter, narrativeId, is required'}, 400
            narr = args_dict[narrative_id]
            narr_exists = _entity_exists(repo, narr)
            if should_exist and not narr_exists:
                return {error_str: f'Narrative with the id, {narr}, was not found in {repo}'}, 404
            elif not should_exist and repo_exists:
                return {error_str: f'Narrative with the id, {narr}, already exists in {repo}'}, 409
            return {repository: repo, narrative_id: narr}, 200
        # Check for narrativeId
        if check_param == background_str:
            if 'name' not in args_dict:
                return {error_str: 'missing',
                        detail: 'The argument parameter, name, is required'}, 400
            return {repository: repo, 'name': args_dict['name']}, 200
    return dict(), 200


def get_metadata_ttl(repo: str, narr_id: str, narr: str, metadata: Metadata,
                     number_sentences: int, number_ingested: int) -> MetadataResults:
    """
    Add the meta-data triples for a narrative to the specified database.

    :param repo: The repository name
    :param narr_id: String identifying the narrative/narrative graph
    :param narr: String holding the text of the narrative
    :param metadata: Instance of the Metadata Class holding the narrative/article details -
                     title, date published, source/publisher, url and number of sentences to ingest
    :param number_sentences: Integer holding the number of sentences in the narrative/article
    :param number_ingested: Integer holding the actual number of sentences ingested (<= number requested)
    :return: The MetadataResults dataclass
    """
    created_at = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    numb_triples_results = query_database('select', count_triples.replace('?g', f':{repo}_{narr_id}'))
    if len(numb_triples_results) > 0:
        numb_triples = int(numb_triples_results[0]['cnt']['value'])
    else:
        return MetadataResults(False, [], empty_string, 0)
    turtle = ttl_prefixes[:]
    turtle.extend([f':{narr_id} a :InformationGraph ; dc:created "{created_at}"^^xsd:dateTime ; ',
                   f':number_triples {numb_triples} ; :encodes :Narrative_{narr_id} .',
                   f':Narrative_{narr_id} a :Narrative ; dc:created "{metadata.published}"^^xsd:dateTime ; ',
                   f':number_sentences {number_sentences} ; :number_ingested {number_ingested} ; '
                   f':source "{metadata.source}" ; dc:title {literal(metadata.title)} ; '
                   f':external_link "{metadata.url}" .',
                   f':Narrative_{narr_id} :text {literal(narr)} .'])
    summary_dict = access_api(narrative_summary_prompt.replace("{narr_text}", narr))
    for goal in summary_dict['goal_numbers']:
        turtle.append(f':Narrative_{narr_id} :narrative_goal "{narrative_goals[int(goal) - 1]}" .')
    for topic in summary_dict['topics']:
        turtle.append(f':Narrative_{narr_id} :topic {literal(topic)} .')
    turtle.append(f':Narrative_{narr_id} :summary {literal(summary_dict["summary"])} .')
    for reaction in summary_dict['reader_reactions']:
        perspective = reaction['perspective']
        # TODO: Pending pystardog fix; edge = f':interpretation {:segment_label "' + {perspective} + '"}'
        predicate = f':interpretation_{perspective}'
        turtle.append(f':Narrative_{narr_id} {predicate} {literal(reaction["reaction"])} .')
    for validity in summary_dict['validity_views']:
        perspective = validity['perspective']
        # TODO: Pending pystardog fix; edge = f':ranking {:segment_label "' + {perspective} + '"}'
        predicate = f':ranking_{perspective}'
        turtle.append(f':Narrative_{narr_id} {predicate} {validity["validity"]} .')
    if 'sentiment' in summary_dict:
        sentiment = summary_dict['sentiment']
        turtle.append(f':Narrative_{narr_id} :sentiment "{sentiment}" .')
        turtle.append(f':Narrative_{narr_id} :sentiment_explanation '
                      f'{literal(summary_dict["sentiment_explanation"])} .')
    return MetadataResults(True, turtle, created_at, numb_triples)


def parse_narrative_query_binding(binding_set: dict) -> dict:
    """
    Returns a dictionary holding the DNA result encoding of a narrative's metadata.

    :param binding_set: A binding set from the query results for 'query_narratives'
    :return: The dictionary with the encoding of the data from the binding set
    """
    return {narrative_id: binding_set['narrative']['value'].split(':Narrative_')[-1],
            'processed': binding_set['created']['value'],
            'numberOfTriples': int(binding_set['numbTriples']['value']),
            'numberOfSentences': int(binding_set['sents']['value']),
            'numberIngested': int(binding_set['ingested']['value']),
            'narrativeMetadata': {'title': binding_set['title']['value'],
                                  'published': binding_set['published']['value'],
                                  'source': binding_set['source']['value'],
                                  'url': binding_set['url']['value']}}


def process_background(entities: list, repo: str) -> BackgroundAndNarrativeResults:
    """
    Performs the sentence and quotation extractions and analysis, adding a narrative to
    the database with the specified name and address.

    :param entities: Array of dictionaries holding an entity's name, type (person, location, ...)
                     and an optional Wikidata Q-id
    :param repo: String holding the repository name for which the entities are background data
    :return: The BackgroundAndNarrativeResults dataclass
    """
    background_turtle = ttl_prefixes[:]
    nouns_dict = nouns_preload(repo)
    # Change the input entities to instances of the Entity class
    entity_classes = []
    invalid_names = []
    processed_names = []
    for entity in entities:
        if entity['type'].lower() in ('law', 'norp', 'organization', 'person', 'place', 'thing'):
            entity_type = background_type_mapping[entity['type'].lower()]
            entity_type = f'PLURAL{entity_type}' if 'isCollection' in entity and entity['isCollection'] \
                else entity_type
            entity_class = Entity(entity['name'], entity_type)
            entity_classes.append(entity_class)
            processed_names.append(entity)
        else:
            invalid_names.append(entity)
    entity_iris, entities_ttl = process_ner_entities(empty_string, entity_classes, nouns_dict)
    # Adjust the Turtle to indicate that these are ":Background" entities
    background_turtle.extend(entities_ttl)
    background_ttl = ' '.join(background_turtle)
    background_ttl = background_ttl.replace(':Correction', ':Background, :Correction')
    msg = add_remove_data('add', background_ttl, repo)
    if msg:
        logging.error(f'Error loading the background Turtle, {background_turtle}')
        return BackgroundResults(0, [], f'Error loading background data to {repo}: {msg}', 500)
    # Add is successful
    resp_dict = {repository: repo,
                 'processedNames': processed_names,
                 'skippedNames': invalid_names}
    return BackgroundAndNarrativeResults(resp_dict, empty_string, 201)


def process_new_narrative(metadata: Metadata, narr: str, repo: str) -> BackgroundAndNarrativeResults:
    """
    Performs the sentence and quotation extractions and analysis, adding a narrative to
    the database with the specified name and address.

    :param metadata: Instance of the Metadata Class holding the narrative/article details -
                     title, date published, source/publisher, url and number of sentences to ingest
    :param narr: String holding the narrative text
    :param repo: String holding the repository name for the narrative graph
    :return: The BackgroundAndNarrativeResults dataclass
    """
    graph_uuid = str(uuid.uuid4())[:8]   # IRI of the named graph for the narrative, and the narrative itself
    logging.info(f'Ingesting {metadata.title} to {repo}')
    sentence_classes, quotation_classes = parse_narrative(narr)
    graph_results = create_graph(sentence_classes, quotation_classes, metadata.number_to_ingest, repo)
    if not graph_results.success:
        return BackgroundAndNarrativeResults(dict(), f'Error creating the graph for {metadata.title}', 500)
    logging.info('Loading knowledge graph')
    msg = add_remove_data('add', ' '.join(graph_results.turtle), repo, graph_uuid)   # Add to dna's repo_graphUUID graph
    if msg:
        logging.error(f'Error loading the narrative graph, {graph_results.turtle}')
        return BackgroundAndNarrativeResults(dict(), f'Error loading the narrative graph {graph_uuid}: {msg}', 500)
    # Process the metadata
    logging.info('Loading metadata')
    metadata_results = get_metadata_ttl(repo, graph_uuid, narr, metadata,
                                        len(sentence_classes), graph_results.number_processed)
    if not metadata_results.success:
        return BackgroundAndNarrativeResults(dict(), f'Error creating the metadata for {metadata.title}', 500)
    msg = add_remove_data('add', ' '.join(metadata_results.turtle), repo)   # Add to dna db's repo graph
    if msg:
        return BackgroundAndNarrativeResults(dict(), f'Error adding metadata for {metadata.title}: {msg}', 500)
    # All is successful
    resp_dict = {repository: repo,
                 'narrativeDetails': {
                     narrative_id: graph_uuid, 'processed': metadata_results.created,
                     'numberOfTriples': metadata_results.number_triples,
                     'numberOfSentences': len(sentence_classes),
                     'numberIngested': graph_results.number_processed,
                     'narrativeMetadata': {'title': metadata.title, 'published': metadata.published,
                                           'source': metadata.source, 'url': metadata.url}}}
    return BackgroundAndNarrativeResults(resp_dict, empty_string, 201)
