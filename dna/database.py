# Stardog database processing:
# 1) create/delete databases
# 2) add/remove data from a database
# 3) list databases
# 4) query or update a database

import logging
import os
import stardog

from utilities import dna_prefix, empty_string, ontologies_database, owl_thing, owl_thing2, resources_root

# Get environment variables
stardog_user = os.getenv('STARDOG_USER')
stardog_password = os.environ.get('STARDOG_PASSWORD')
stardog_endpoint = os.environ.get('STARDOG_ENDPOINT')

query_match = 'prefix : <urn:ontoinsights:dna:> SELECT ?class WHERE { ' \
              '{ ?class :verb_synonym ?vsyn . FILTER(?vsyn = "keyword") } UNION ' \
              '{ ?class :noun_synonym ?nsyn . FILTER(?nsyn = "keyword") } UNION ' \
              '{ ?class rdfs:label ?label . FILTER(lcase(?label) = "keyword") } }'

text_turtle = 'text/turtle'


def add_remove_data(op_type: str, triples: str, database: str, graph: str = empty_string) -> bool:
    """
    Add or remove data to/from the database/store

    :param op_type: A string = 'add' or 'remove'
    :param triples: A string with the triples to be inserted/removed
    :param database: The database name
    :param graph: An optional named graph in which to insert/remove the triples
    :returns: True if successful; False otherwise
    """
    logging.info(f'Data {"added to" if op_type == "add" else "removed from"} {database}'
                 f'{" and graph, " if graph else ""}{graph}')
    if op_type != 'add' and op_type != 'remove':
        capture_error(f'Invalid op_type {op_type} for add_remove_graph', True)
        return False
    try:
        conn = stardog.Connection(database, **sd_conn_details)
        conn.begin()
        if op_type == 'add':
            # Add to the database
            if graph:
                conn.add(stardog.content.Raw(triples, text_turtle), graph_uri=graph)
            else:
                conn.add(stardog.content.Raw(triples, text_turtle))
        else:
            # Remove from the database
            if graph:
                conn.remove(stardog.content.Raw(triples, text_turtle), graph_uri=graph)
            else:
                conn.remove(stardog.content.Raw(triples, text_turtle))
        conn.commit()
        return True
    except Exception as e:
        capture_error(f'Database ({op_type}) exception: {str(e)}', True)
        return False


def create_delete_database(op_type: str, database: str) -> str:
    """
    Create or delete a database. If created, add the DNA ontologies.

    :param op_type: A string = 'create' or 'delete'
    :param database: The database name
    :returns: Empty string if successful or the details of an exception
    """
    logging.info(f'Database {database} being {op_type}d')
    if op_type != 'create' and op_type != 'delete':
        capture_error(f'Invalid op_type {op_type} for create_delete_db', True)
        return empty_string
    try:
        admin = stardog.Admin(**sd_conn_details)
        if op_type == 'create':
            # Create database
            admin.new_database(database,
                               {'search.enabled': True, 'edge.properties': True, 'reasoning': True,
                                'reasoning.punning.enabled': True, 'query.timeout': '5m'})
            # Load ontologies to the newly created database
            conn = stardog.Connection(database, **sd_conn_details)
            conn.begin()
            _load_directory_to_database(ontol_path, conn)
            # TODO: Remove if not applicable for the domain
            _load_directory_to_database(f'{ontol_path}domain-specific/', conn)
            conn.commit()
        else:
            # Delete database
            database_obj = admin.database(database)
            database_obj.drop()
        return empty_string
    except Exception as e:
        return f'Database ({op_type}) exception: {str(e)}'


def get_databases() -> list:
    """
    Return a list of all the databases/stores of narratives

    :returns: List of database/store names
    """
    try:
        admin = stardog.Admin(**sd_conn_details)
        databases = admin.databases()
        db_names = []
    except Exception as e:
        capture_error(f'Exception getting list of stores: {str(e)}', True)
        return []
    for database in databases:
        db_name = database.name
        if db_name != 'ontologies' and 'domain-' not in db_name and 'test-' not in db_name:
            db_names.append(database.name)
    return db_names


def query_class(text: str, query: str) -> str:
    """
    Attempts to match the input text to verb/noun_synonyms, labels and definitions in the ontology,
    and returns the highest probability class name as the result. Note that this method requires
    the SPARQL query to SELECT a ?class variable.

    :param text: Text to match
    :param query: String holding the query to execute
    :returns: The highest probability class name returned by the query
    """
    results = query_database('select', query.replace('keyword', text), ontologies_database)
    if results:
        result = results[0]  # Return the first result (assumes that the query is ordered by descending probability)
        class_name = result['class']['value']
        if class_name != owl_thing:
            return class_name.split(':')[-1]
        else:
            return owl_thing2
    return owl_thing2   # No results/no match


def query_database(query_type: str, query: str, database: str) -> list:
    """
    Process a SELECT or UPDATE query

    :param query_type: A string = 'select' or 'update'
    :param query: The text of a SPARQL query
    :param database: The database (name) to be queried
    :returns: The bindings array from the query results
    """
    logging.info(f'Querying database, {database}, using {query_type}, with query, {query}')
    if query_type != 'select' and query_type != 'update':
        capture_error(f'Invalid query_type {query_type} for query_db', True)
        return []
    try:
        conn = stardog.Connection(database, **sd_conn_details)
        if query_type == 'select':
            # Select query, which will return results, if successful
            query_results = conn.select(query, content_type='application/sparql-results+json')
            if 'results' in query_results.keys() and 'bindings' in query_results['results'].keys():
                return query_results['results']['bindings']
            else:
                return []
        else:
            # Update query; No results (either success or failure)
            conn.update(query)
            return ['successful']
    except Exception as e:
        capture_error(f'Database ({database}) query exception for {query}: {str(e)}', True)
        return []


def query_exact_and_approx_match(text: str, query_str: str) -> str:
    """
    Executes a query_match and then approximate match (identified by the query string) for the
    text. An "approximate" match is written using FILTER CONTAINS.

    :param text: Text to match
    :param query_str: String holding the "approximate" query to execute
    :returns: The highest probability class name returned by the query
    """
    class_name = query_class(text, query_match)   # Query exact match
    if class_name != owl_thing:
        return class_name.split(':')[-1]
    # Avoid false matches if the word is < 5 characters (for ex, 'end' or 'old' is in many strings)
    if len(text) < 5:
        return owl_thing2
    class_name = query_class(text, query_str)      # Query approximate match
    # Avoid false matches if the matched class is < 5 characters (for ex, ':End' might be returned for 'friend')
    if class_name != owl_thing and len(class_name.split(':')[-1]) > 5:
        return class_name.split(':')[-1]
    else:
        return owl_thing2


# Internal functions
def _load_directory_to_database(directory_name, conn):
    """
    Loads the DNA ontology files to a new database/data store.

    :param directory_name: String holding the directory name
    :param conn: The connection to the Stardog DB for the database
    :returns: None
    """
    try:
        list_files = os.listdir(directory_name)
        for file in list_files:
            if file.endswith('.ttl'):
                conn.add(stardog.content.File(f'{directory_name}{file}'))
    except Exception as e:
        capture_error(f'Exception loading ontologies from {directory_name}: {str(e)}', True)
