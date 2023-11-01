# Stardog database processing:
#   1) create/delete databases
#   2) remove all data from a database or graph
#   3) add/remove specific data from a database
#   4) query or update a database
#   5) 'construct' the triples in a graph

from datetime import datetime
import logging
import os
from rdflib import Graph
import stardog
from stardog import Connection

from dna.utilities_and_language_specific import empty_string, ontologies_database, owl_thing

rdf_graph = Graph()
text_turtle = 'text/turtle'

# Get environment variables
sd_conn_details = {'endpoint': os.environ.get('STARDOG_ENDPOINT'),
                   'username': os.getenv('STARDOG_USER'),
                   'password': os.environ.get('STARDOG_PASSWORD')}

full_owl_thing = 'http://www.w3.org/2002/07/owl#Thing'


def add_remove_data(op_type: str, triples: str, database: str, graph: str = empty_string) -> str:
    """
    Add or remove data to/from the database/store

    :param op_type: A string = 'add' or 'remove'
    :param triples: A string with the triples to be inserted/removed
    :param database: The database name
    :param graph: An optional named graph in which to insert/remove the triples
    :return: An empty string if successful, or the error details if not
    """
    if op_type != 'add' and op_type != 'remove':
        return "Invalid op_type"
    try:
        ar_conn: Connection = stardog.Connection(database, **sd_conn_details)
        ar_conn.begin()
        if op_type == 'add':
            # Add to the database
            if graph:
                ar_conn.add(stardog.content.Raw(triples.encode('utf-8'), text_turtle), graph_uri=graph)
            else:
                ar_conn.add(stardog.content.Raw(triples.encode('utf-8'), text_turtle))
        else:
            # Remove from the database
            if graph:
                ar_conn.remove(stardog.content.Raw(triples.encode('utf-8'), text_turtle), graph_uri=graph)
            else:
                ar_conn.remove(stardog.content.Raw(triples.encode('utf-8'), text_turtle))
        ar_conn.commit()
        return empty_string
    except Exception as add_rem_err:
        curr_error = f'Database ({op_type}) exception: {str(add_rem_err)}'
        logging.error(curr_error)
        return curr_error


def check_server_status() -> bool:
    """
    Validate that the server at the specified address is functional.

    :return: Boolean indicating that it is functional (True) or not (False)
    """
    try:
        admin = stardog.Admin(**sd_conn_details)
        return admin.alive()
    except Exception as stat_err:
        curr_error = f'Database server exception: {str(stat_err)}'
        logging.error(curr_error)
        return False


def clear_data(database: str, graph: str = empty_string) -> str:
    """
    Clear all triples from a graph or the complete database

    :param database: The database name
    :param graph: An optional named graph which to clear
    :return: An empty string if successful, or the error details if not
    """
    try:
        clear_conn = stardog.Connection(database, **sd_conn_details)
        clear_conn.begin()
        if graph:
            clear_conn.clear(graph)
        else:
            clear_conn.clear()
        clear_conn.commit()
        return empty_string
    except Exception as clear_err:
        if graph:
            curr_error = f'Database clear exception for graph {graph} in {database}: {str(clear_err)}'
        else:
            curr_error = f'Database clear exception for database {database}: {str(clear_err)}'
        logging.error(curr_error)


def construct_database(construct: str, database: str) -> (bool, list):
    """
    Process a CONSTRUCT query

    :param construct: The text of the CONSTRUCT query
    :param database: The database (name) to be queried
    :return: A tuple holding a boolean indicating success (if true) or failure and an array
              with the Turtle results of the CONSTRUCT query or an error message
    """
    try:
        const_conn = stardog.Connection(database, **sd_conn_details)
        construct_results = const_conn.graph(construct, content_type='text/turtle')
        turtle_details = rdf_graph.parse(format='text/turtle', data=construct_results)
        final_turtle = []
        for stmt in turtle_details:
            subj, pred, obj = stmt
            final_turtle.append(f'{subj.n3()} {pred.n3()} {obj.n3()} .\n')
        return True, final_turtle
    except Exception as const_err:
        curr_error = f'Database ({database}) construct exception: {str(const_err)}'
        logging.error(curr_error)
        return False, [str(const_err)]


def create_delete_database(op_type: str, database: str) -> str:
    """
    Create or delete a database. If created, add the DNA ontologies.

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


def query_database(query_type: str, query: str, database: str) -> list:
    """
    Process a SELECT or UPDATE query

    :param query_type: A string = 'select' or 'update'
    :param query: The text of a SPARQL query
    :param database: The database (name) to be queried
    :return: The bindings array from the query results
    """
    if query_type != 'select' and query_type != 'update':
        logging.error(f'Invalid query_type {query_type} for query_db')
        return []
    try:
        query_conn = stardog.Connection(database, **sd_conn_details)
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
        curr_error = f'Database ({database}) query exception for {query}: {str(query_err)}'
        logging.error(curr_error)
        return [curr_error]
