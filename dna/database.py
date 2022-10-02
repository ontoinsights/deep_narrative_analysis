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

from dna.utilities import base_dir, empty_string, ontologies_database, owl_thing, owl_thing2

rdf_graph = Graph()

ontologies_dir = os.path.join(base_dir, 'ontologies/')
text_turtle = 'text/turtle'

# Get environment variables
sd_conn_details = {'endpoint': os.environ.get('STARDOG_ENDPOINT'),
                   'username': os.getenv('STARDOG_USER'),
                   'password': os.environ.get('STARDOG_PASSWORD')}


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
        conn = stardog.Connection(database, **sd_conn_details)
        conn.begin()
        if op_type == 'add':
            # Add to the database
            if graph:
                conn.add(stardog.content.Raw(triples.encode('utf-8'), text_turtle), graph_uri=graph)
            else:
                conn.add(stardog.content.Raw(triples.encode('utf-8'), text_turtle))
        else:
            # Remove from the database
            if graph:
                conn.remove(stardog.content.Raw(triples.encode('urf-8'), text_turtle), graph_uri=graph)
            else:
                conn.remove(stardog.content.Raw(triples.encode('utf-8'), text_turtle))
        conn.commit()
        return empty_string
    except Exception as e:
        error = f'Database ({op_type}) exception: {str(e)}'
        logging.error(error)
        return error


def clear_data(database: str, graph: str = empty_string) -> str:
    """
    Clear all triples from a graph or the complete database

    :param database: The database name
    :param graph: An optional named graph which to clear
    :return: An empty string if successful, or the error details if not
    """
    try:
        conn = stardog.Connection(database, **sd_conn_details)
        conn.begin()
        if graph:
            conn.clear(graph)
        else:
            conn.clear()
        conn.commit()
        return empty_string
    except Exception as e:
        if graph:
            error = f'Database clear exception for graph {graph} in {database}: {str(e)}'
        else:
            error = f'Database clear exception for database {database}: {str(e)}'
        logging.error(error)


def construct_database(construct: str, database: str) -> (bool, list):
    """
    Process a CONSTRUCT query

    :param construct: The text of the CONSTRUCT query
    :param database: The database (name) to be queried
    :return: A tuple holding a boolean indicating success (if true) or failure and an array
              with the Turtle results of the CONSTRUCT query or an error message
    """
    try:
        conn = stardog.Connection(database, **sd_conn_details)
        construct_results = conn.graph(construct, content_type='text/turtle')
        turtle_details = rdf_graph.parse(format='text/turtle', data=construct_results)
        final_turtle = []
        for stmt in turtle_details:
            subj, pred, obj = stmt
            final_turtle.append(f'{subj.n3()} {pred.n3()} {obj.n3()} .\n')
        return True, final_turtle
    except Exception as e:
        error = f'Database ({database}) construct exception: {str(e)}'
        logging.error(error)
        return False, [str(e)]


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
    except Exception as e:
        error = f'Database ({op_type}) exception: {str(e)}'
        logging.error(error)
        return error


def query_class(text: str, query: str) -> str:
    """
    Attempts to match the input text to verb/noun_synonyms, labels and definitions in the ontology,
    and returns the highest probability class name as the result.

    :param text: Text to match
    :param query: String holding the query to execute
    :return: The highest probability class name returned by the query
    """
    if text == owl_thing2:
        return owl_thing2
    results = query_database('select', query.replace('keyword', text), ontologies_database)
    if results:
        result = results[0]  # Return the first result (assumes that the query is ordered by descending probability)
        class_name = result['class']['value']
        if class_name != owl_thing:
            return f':{class_name.split(":")[-1]}'
        else:
            return owl_thing2
    return owl_thing2   # No results/no match


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
        conn = stardog.Connection(database, **sd_conn_details)
        if query_type == 'select':
            # Select query, which will return results, if successful
            query_results = conn.select(query, content_type='application/sparql-results+json')
            if 'results' in query_results and 'bindings' in query_results['results']:
                return query_results['results']['bindings']
            else:
                return []
        else:
            # Update query; No results (either success or failure)
            conn.update(query)
            return ['successful']
    except Exception as e:
        error = f'Database ({database}) query exception for {query}: {str(e)}'
        logging.error(error)
        return [error]
