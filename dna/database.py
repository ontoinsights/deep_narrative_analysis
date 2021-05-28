import configparser as cp
import logging
import os
import stardog

from utilities import resources_root, capture_error

# Get details from the dna.config file, stored in the resources directory
# And set the connection details
config = cp.RawConfigParser()
config.read(f'{resources_root}dna.config')
sd_conn_details = {
    'endpoint': config.get('StardogConfig', 'endpoint'),
    'username': config.get('StardogConfig', 'username'),
    'password': config.get('StardogConfig', 'password')}
# And set path to directory where ontologies stored
ontol_path = config.get('OntologiesConfig', 'ontolPath')
if not ontol_path.endswith('/'):
    ontol_path = f'{ontol_path}/'


def add_remove_data(op_type: str, triples: str, database: str, graph: str = '') -> bool:
    """
    Add or remove data to/from the database/store

    :param op_type: A string = 'add' or 'remove'
    :param triples: A string with the triples to be inserted/removed
    :param database: The database name
    :param graph: An optional named graph in which to insert/remove the triples
    :return: True if successful; False otherwise
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
                conn.add(stardog.content.Raw(triples, 'text/turtle'), graph_uri=graph)
            else:
                conn.add(stardog.content.Raw(triples, 'text/turtle'))
        else:
            # Remove from the database
            if graph:
                conn.remove(stardog.content.Raw(triples, 'text/turtle'), graph_uri=graph)
            else:
                conn.remove(stardog.content.Raw(triples, 'text/turtle'))
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
    :return: Empty string if successful or the details of an exception
    """
    logging.info(f'Database {database} being {op_type}d')
    if op_type != 'create' and op_type != 'delete':
        capture_error(f'Invalid op_type {op_type} for create_delete_db', True)
        return ''
    try:
        admin = stardog.Admin(**sd_conn_details)
        if op_type == 'create':
            # Create database
            admin.new_database(database,
                               {'search.enabled': True, 'edge.properties': True, 'reasoning': True,
                                'reasoning.punning.enabled': True, 'query.timeout': '20m'})
            # Load ontologies to the newly created database
            conn = stardog.Connection(database, **sd_conn_details)
            conn.begin()
            logging.info(f'Loading DNA ontologies to {database}')
            _load_directory_to_database(ontol_path, conn)
            _load_directory_to_database(f'{ontol_path}domain-context/', conn)
            conn.commit()
        else:
            # Delete database
            database_obj = admin.database(database)
            database_obj.drop()
        return ''
    except Exception as e:
        return f'Database ({op_type}) exception: {str(e)}'


def get_databases() -> list:
    """
    Return a list of all the databases/stores of narratives

    :return: List of database/store names
    """
    logging.info('Getting a list of all databases')
    try:
        admin = stardog.Admin(**sd_conn_details)
        databases = admin.databases()
        db_names = list()
    except Exception as e:
        capture_error(f'Exception getting list of stores: {str(e)}', True)
        return []
    for database in databases:
        db_names.append(database.name)
    return db_names


def query_database(query_type: str, query: str, database: str) -> (bool, dict):
    """
    Process a SELECT or UPDATE query

    :param query_type: A string = 'select' or 'update'
    :param query: The text of a SPARQL query
    :param database: The database (name) to be queried
    :return: True if successful; False otherwise
             Query results (if the query_type is 'select'); An empty dictionary otherwise
    """
    logging.info(f'Querying database, {database}, using {query_type}, with query, {query}')
    if query_type != 'select' and query_type != 'update':
        capture_error(f'Invalid query_type {query_type} for query_db', True)
        return False, dict()
    try:
        conn = stardog.Connection(database, **sd_conn_details)
        if query_type == 'select':
            # Select query, which will return results, if successful
            query_results = conn.select(query, content_type='application/sparql-results+json')
            if query_results['results']['bindings']:
                return True, query_results
            else:
                return True, dict()
        else:
            # Update query; No results (either success or failure)
            conn.update(query)
            return True, dict()
    except Exception as e:
        capture_error(f'Database ({database}) query exception for {query}: {str(e)}', True)
        return False, dict()


# Functions internal to the module
def _load_directory_to_database(directory_name, conn):
    """
    Loads the DNA files to a new database/data store.

    :param directory_name: String holding the directory name
    :param conn: The connection to the Stardog DB for the database
    :return: None
    """
    try:
        list_files = os.listdir(directory_name)
        for file in list_files:
            if file.endswith('.ttl'):
                conn.add(stardog.content.File(f'{directory_name}{file}'))
    except Exception as e:
        capture_error(f'Exception loading ontologies from {directory_name}: {str(e)}', True)
