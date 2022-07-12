# Main application processing

import argparse
from argparse import ArgumentParser, Namespace
import logging

from database import query_database
from display_details import display_timeline, display_visualization, display_word_cloud
from nlp import ingest_narratives
from utilities import dna_root

logging.basicConfig(level=logging.INFO, filename='dna.log',
                    format='%(funcName)s - %(levelname)s - %(asctime)s - %(message)s')

ingest_dir = "/dna/resources/ingest"
graph_query = "SELECT DISTINCT ?g WHERE { GRAPH ?g { ?s ?p ?o } }"


def check_arguments(arg_details: Namespace) -> bool:
    """
    Verifies that only 1 action is requested - either ingest narratives, list current narratives
    already ingested, edit a narrative, display a timeline or display a word cloud.

    :param arg_details: Argparse's Namespace with the argument details
    :return: True if only 1 action is requested, False otherwise
    """
    count = 0
    if arg_details.ingest:
        count += 1
    if arg_details.list:
        count += 1
    if arg_details.narr_edit:
        count += 1
    if arg_details.narr_graph:
        count += 1
    if arg_details.narr_timeline:
        count += 1
    if arg_details.narr_wordcloud:
        count += 1
    if count == 1:
        return True
    else:
        return False


def define_arguments(parser: ArgumentParser):
    """
    Specifies the arguments of the DNA CLI.

    :param parser: Argparse's ArgumentParser handling the CLI
    :return: None
    """
    parser.add_argument(
        '-d', dest='database', action='store', nargs="?",
        help='(optional) database name holding narrative parses (default: narratives)')
    parser.add_argument(
        '-e', dest='narr_edit', action='store', nargs=1,
        help='edit the specified narrative from the database')
    parser.add_argument(
        '-i', dest='ingest', action='store', nargs=1,
        help='ingest .txt narratives to the database, from the directory, dna/resources/ingest')
    parser.add_argument(
        '-g', dest='narr_graph', action='store', nargs=1,
        help='open Stardog to create graph visualization of the specified narrative')
    parser.add_argument(
        '-l', dest='list', action='store_true',
        help='show list of narratives stored in the database')
    parser.add_argument(
        '-t', dest='narr_timeline', action='store', nargs=1,
        help='display timeline for the specified narrative from the database')
    parser.add_argument(
        '-w', dest='narr_wordcloud', action='store', nargs=1,
        help='display 75 element word cloud for "all" or the specified narrative from the database')


# Main
if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(
        description='Interface to ingest and analyze narratives. '
                    'Specify a database using the -d option (or the default, "narratives", will be used). '
                    'You must also select one of the instructions: -i, -l, -e, -t or -w.')
    define_arguments(arg_parser)
    args = arg_parser.parse_args()
    if not check_arguments(args):
        print("*** Invalid number of arguments. Please see the usage information below. ***")
        arg_parser.print_help()
    else:
        # Process the command
        if args.database:
            db = args.database
        else:
            db = 'narratives'
        if args.ingest:
            logging.info(f'Ingest from {ingest_dir} to {db}')
            print(f'Ingested {ingest_narratives(ingest_dir, db)} narrative(s)')
        if args.list:
            logging.info(f'Narrative list for {db}')
            print(f'Narratives in the database, {db}:')
            narratives = query_database('select', graph_query, db)
            for binding in narratives:
                print(f"  {binding['g']['value'][4:]}")
        if args.narr_graph:
            narr_detail = args.narr_graph[0]
            logging.info(f'Visualize {narr_detail} from {db}')
            display_visualization(narr_detail, db)
        if args.narr_wordcloud:
            narr_detail = args.narr_wordcloud[0]
            logging.info(f'Word cloud for {narr_detail} in {db}')
            display_word_cloud(narr_detail, db)
        if args.narr_edit:
            narr_detail = args.narr_edit[0]
            logging.info(f'Edit {narr_detail} in {db}')
            edit_narrative(narr_detail, db)
        if args.narr_timeline:
            narr_detail = args.narr_timeline[0]
            logging.info(f'Timeline for {narr_detail} from {db}')
            display_timeline(narr_detail, db)
