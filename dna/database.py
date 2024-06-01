# Stardog database processing:
#   1) create/delete databases
#   2) remove all data from a database or graph
#   3) add/remove specific data from a database
#   4) query or update a database
#   5) 'construct' the triples in a graph

from datetime import datetime
import logging
import os
from rdflib import Graph, Namespace
import stardog
from stardog import Connection

from dna.utilities_and_language_specific import dna_db, dna_prefix, empty_string, owl_thing

rdf_graph = Graph()
text_turtle = 'text/turtle'
DNA = Namespace('urn:ontoinsights:dna:')
OWL = Namespace('http://www.w3.org/2002/07/owl')
RDF = Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
RDFS = Namespace('http://www.w3.org/2000/01/rdf-schema#')

# Get environment variables
sd_conn_details = {'endpoint': os.environ.get('STARDOG_ENDPOINT'),
                   'username': os.getenv('STARDOG_USER'),
                   'password': os.environ.get('STARDOG_PASSWORD')}

full_owl_thing = 'http://www.w3.org/2002/07/owl#Thing'


def add_remove_data(op_type: str, triples: str, repo: str, graph: str = empty_string) -> str:
    """
    Add or remove triples to/from Stardog for narratives to be stored in the specified "repository"

    :param op_type: A string = 'add' or 'remove'
    :param triples: A string with the triples to be inserted/removed
    :param repo: The repository name
    :param graph: An optional ID indicating that triples for a specific narrative are added to the repository
    :return: An empty string if successful, or the error details if not
    """
    if op_type != 'add' and op_type != 'remove':
        return "Invalid op_type"
    try:
        ar_conn: Connection = stardog.Connection(dna_db, **sd_conn_details)
        ar_conn.begin()
        if op_type == 'add':
            # Add to the database
            if not repo:
                ar_conn.add(stardog.content.Raw(triples.encode('utf-8'), text_turtle))
            elif graph:
                ar_conn.add(stardog.content.Raw(triples.encode('utf-8'), text_turtle),
                            graph_uri=f'{dna_prefix}{repo}_{graph}')
            else:
                ar_conn.add(stardog.content.Raw(triples.encode('utf-8'), text_turtle),
                            graph_uri=f'{dna_prefix}{repo}_default')
        else:
            # Remove from the database
            if not repo:
                ar_conn.remove(stardog.content.Raw(triples.encode('utf-8'), text_turtle))
            elif graph:
                ar_conn.remove(stardog.content.Raw(triples.encode('utf-8'), text_turtle),
                               graph_uri=f'{dna_prefix}{repo}_{graph}')
            else:
                ar_conn.remove(stardog.content.Raw(triples.encode('utf-8'), text_turtle),
                               graph_uri=f'{dna_prefix}{repo}_default')
        ar_conn.commit()
        return empty_string
    except Exception as add_rem_err:
        curr_error = f'Database ({op_type}) exception: {str(add_rem_err)}'
        logging.error(curr_error)
        return curr_error


def check_server_status() -> bool:
    """
    Validate that the server at the dna_db address is functional.

    :return: Boolean indicating that it is functional (True) or not (False)
    """
    try:
        admin = stardog.Admin(**sd_conn_details)
        return admin.alive()
    except Exception as stat_err:
        curr_error = f'Database server exception: {str(stat_err)}'
        logging.error(curr_error)
        return False


def clear_data(repo: str, graph: str = empty_string) -> str:
    """
    Clear all triples from a graph or for the complete repository

    :param repo: The repository name
    :param graph: An optional ID indicating that triples in a specific graph are cleared
    :return: An empty string if successful, or the error details if not
    """
    try:
        clear_conn = stardog.Connection(dna_db, **sd_conn_details)
        clear_conn.begin()
        if graph:
            clear_conn.clear(f'{dna_prefix}{repo}_{graph}')
        else:
            clear_conn.clear(f'{dna_prefix}{repo}_default')
        clear_conn.commit()
        return empty_string
    except Exception as clear_err:
        if graph:
            curr_error = f'Clear exception for narrative {graph} in repository {repo}: {str(clear_err)}'
        else:
            curr_error = f'Clear exception for repository {repo}: {str(clear_err)}'
        logging.error(curr_error)


def construct_graph(construct: str, repo: str) -> (bool, list):
    """
    Process a CONSTRUCT query

    :param construct: The text of the CONSTRUCT query
    :param repo: The repository to be queried
    :return: A tuple holding a boolean indicating success (if true) or failure and an array
              with the Turtle results of the CONSTRUCT query or an error message
    """
    try:
        const_conn = stardog.Connection(dna_db, **sd_conn_details)
        construct_results = const_conn.graph(construct, content_type='text/turtle')
        turtle_details = rdf_graph.parse(format='text/turtle', data=construct_results)
        turtle_details.bind('dna', DNA)
        turtle_details.bind('owl', OWL)
        turtle_details.bind('rdf', RDF)
        turtle_details.bind('rdfs', RDFS)
        turtle_stmts = []
        for stmt in turtle_details:
            subj, pred, obj = stmt
            turtle_stmts.append(f'{subj.n3(turtle_details.namespace_manager)} '
                                f'{pred.n3(turtle_details.namespace_manager)} '
                                f'{obj.n3(turtle_details.namespace_manager)} .\n')
        turtle_stmts.sort()
        final_turtle = ['@prefix : <urn:ontoinsights:dna:> .\n', '\n']
        final_turtle.extend(turtle_stmts)
        return True, final_turtle
    except Exception as const_err:
        curr_error = f'Narrative graph ({narr_id}) construct for repository ({repo}) exception: {str(const_err)}'
        logging.error(curr_error)
        return False, [str(const_err)]


# Future: Multiple separate database repositories are not currently supported
def create_delete_database(op_type: str, database: str) -> str:
    """
    Create or delete a database. In order to use Stardog Cloud's Free tier, all
    repositories/databases are collapsed to 1.    Future: Allow for separate repositories.

    :param op_type: A string = 'create' or 'delete'
    :param database: The database name
    :return: Empty string if successful or the details of an exception
    """
    if op_type != 'create' and op_type != 'delete':
        return empty_string
    try:
        admin = stardog.Admin(**sd_conn_details)
        if op_type == 'create':
            # Create database
            admin.new_database(database,
                               {'search.enabled': True, 'edge.properties': True, 'reasoning': True,
                                'reasoning.punning.enabled': True, 'query.timeout': '5m'})
        else:
            # Delete database
            database_obj = admin.database(database)
            database_obj.drop()
        now = datetime.now()
        return f'Database, {database}, {op_type}d at {now.strftime("%Y-%m-%dT%H:%M:%S")}'
    except Exception as cd_err:
        curr_error = f'Database ({op_type}) exception: {str(cd_err)}'
        logging.error(curr_error)
        return curr_error


def query_database(query_type: str, query: str) -> list:
    """
    Process a SELECT or UPDATE query

    :param query_type: A string = 'select' or 'update'
    :param query: The text of a SPARQL query
    :return: The bindings array from the query results
    """
    if query_type != 'select' and query_type != 'update':
        logging.error(f'Invalid query_type {query_type} for query_db')
        return []
    try:
        query_conn = stardog.Connection(dna_db, **sd_conn_details)
        if query_type == 'select':
            # Select query, which will return results, if successful
            query_results = query_conn.select(query, content_type='application/sparql-results+json')
            if 'results' in query_results and 'bindings' in query_results['results']:
                return query_results['results']['bindings']
            else:
                return []
        else:
            # Update query; No results (either success or failure)
            query_conn.update(query)
            return ['successful']
    except Exception as query_err:
        curr_error = f'Query exception for {query}: {str(query_err)}'
        logging.error(curr_error)
        return [curr_error]
