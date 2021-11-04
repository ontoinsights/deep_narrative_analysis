import codecs
import csv

from dna.database import query_database
from dna.load_text_processing import clean_text, simplify_text

triple_query = 'prefix : <urn:ontoinsights:dna:> prefix geo: <urn:ontoinsights:geonames:> ' \
               'SELECT ?subj FROM <urn:graph> WHERE { spo BIND("urn:xyz" as ?subj) }'

event_query = 'prefix : <urn:ontoinsights:dna:> prefix geo: <urn:ontoinsights:geonames:> ' \
              'SELECT ?event FROM <urn:graph> WHERE { ' \
              '?event a evt_type ; :text "txt" ; :sentence_offset sent_off ; OPTIONAL ' \
              'rdfs:label "lbl" . FILTERS }'


def get_simplified_text(metadata_dict: dict) -> str:
    # Get narrative text
    with open(f'resources/{metadata_dict["Source"]}', 'r') as orig:
        # Get text as would be extracted by pdftotext
        orig_text = orig.read()
    # Perform processing steps to clean the text and "simplify" it
    if metadata_dict['Clean'] == 'Y':   # Cleaning is for PDF docs
        text = clean_text(orig_text, metadata_dict)
    else:
        text = orig_text
    return simplify_text(text, metadata_dict)


def query_for_triples(graph: str, file_name: str, test_db: str) -> bool:
    # Open the file (whose name is constructed using the 'file_name' input parameter) and
    # query the named graph (constructed using the 'graph' input parameter)
    # in the database (defined by the 'test_db' parameter);
    # Returns True if all indicated triples are found in the db, or False otherwise
    with codecs.open(file_name, encoding='utf-8-sig') as csv_file:
        triples = csv.reader(csv_file, delimiter=',', quotechar='"')
        missing_triple = False
        for row in triples:
            expected, s, p, o = row
            if expected == 'fail':
                continue
            if s and o:
                if s == 'subject':   # Skip column headings
                    continue
                spo_str = update_spo(s, p, o)
                query_str = triple_query.replace('graph', graph).replace('spo', spo_str).replace('xxx', '')
                results = query_database('select', query_str, test_db)
                if not results:
                    missing_triple = True
                    print(f'Missing: {s}, {p}, {o}')
        if missing_triple:
            return False
        else:
            return True


def query_for_events(graph: str,  file_name: str, test_db: str) -> bool:
    # Open the file (whose name is constructed using the 'file_name' input parameter) and
    # query the named graph (again constructed using the 'graph' input parameter)
    # in the database (defined by the 'test_db' parameter);
    # Returns True if all indicated triples are found in the db, or False otherwise
    with codecs.open(file_name, encoding='utf-8-sig') as csv_file:
        triples = csv.reader(csv_file, delimiter=',', quotechar='"')
        missing_event = False
        for row in triples:
            testing, expected, txt, lbl, sent_off, evt_type, evt_time, evt_begin, evt_end, evt_earliest, \
                evt_latest, evt_agent, evt_active, evt_affected, evt_provider, evt_recipient, evt_holder, \
                evt_location, evt_origin, evt_destination, evt_instrument, evt_resource, \
                evt_topic, evt_component, evt_member, evt_sentiment = row
            if testing == 'testing' or expected == 'fail':   # Skip column headings
                continue
            if txt:
                query_str = event_query.replace('graph', graph).replace('evt_type', evt_type).\
                    replace('txt', txt).replace('lbl', lbl).replace('sent_off', sent_off)
                if evt_time:
                    query_str = query_str.replace('OPTIONAL', f":has_time {evt_time} ; OPTIONAL")
                if evt_begin:
                    query_str = query_str.replace('OPTIONAL', f":has_beginning {evt_begin} ; OPTIONAL")
                if evt_end:
                    query_str = query_str.replace('OPTIONAL', f":has_end {evt_end} ; OPTIONAL")
                if evt_earliest:
                    query_str = query_str.replace('OPTIONAL', f":has_earliest_beginning {evt_earliest} ; OPTIONAL")
                if evt_latest:
                    query_str = query_str.replace('OPTIONAL', f":has_latest_end {evt_latest} ; OPTIONAL")
                if evt_agent:
                    query_str = update_query_clause(query_str, ':has_agent', evt_agent)
                if evt_active:
                    query_str = update_query_clause(query_str, ':has_active_agent', evt_active)
                if evt_affected:
                    query_str = update_query_clause(query_str, ':has_affected_agent', evt_affected)
                if evt_provider:
                    query_str = update_query_clause(query_str, ':has_provider', evt_provider)
                if evt_recipient:
                    query_str = update_query_clause(query_str, ':has_recipient', evt_recipient)
                if evt_holder:
                    query_str = update_query_clause(query_str, ':has_holder', evt_holder)
                if evt_location:
                    query_str = update_query_clause(query_str, ':has_location', evt_location)
                if evt_origin:
                    query_str = update_query_clause(query_str, ':has_origin', evt_origin)
                if evt_destination:
                    query_str = update_query_clause(query_str, ':has_destination', evt_destination)
                if evt_instrument:
                    query_str = update_query_clause(query_str, ':has_instrument', evt_instrument)
                if evt_resource:
                    query_str = update_query_clause(query_str, ':has_resource', evt_resource)
                if evt_topic:
                    query_str = update_query_clause(query_str, ':has_topic', evt_topic)
                if evt_component:
                    query_str = update_query_clause(query_str, ':has_component', evt_component)
                if evt_member:
                    query_str = update_query_clause(query_str, ':has_member', evt_member)
                if evt_sentiment:
                    query_str = query_str.replace('OPTIONAL', f':sentiment ?sentiment ; OPTIONAL')
                query_str = query_str.replace('graph', graph).replace('OPTIONAL ', '').\
                    replace('FILTERS', '').replace('xxx', '')
                results = query_database('select', query_str, test_db)
                if not results:
                    missing_event = True
                    print(f'Missing for query: {query_str}')
        if missing_event:
            return False
        else:
            return True


def update_query_clause(query: str, pred: str, obj: str) -> str:
    """

    """
    if 'xxx' in obj:
        return query.replace('OPTIONAL', f'{pred} ?{pred[1:]}_obj ; OPTIONAL').\
            replace('FILTERS', f'FILTER(CONTAINS(str(?{pred[1:]}_obj), "{obj}")) . FILTERS')
    else:
        return query.replace('OPTIONAL', f'{pred} {obj} ; OPTIONAL')


def update_spo(subj: str, pred: str, obj: str) -> str:
    """

    """
    query_str = f'{subj} {pred} ?o'
    if 'xxx' in subj:
        if 'Affiliation' in subj:
            # Format of the instance IRI is ':<id-agent>_xxx<id-affiliated-with>Affiliation'
            subjs = subj.split('xxx')
            query_str = f'?s {pred} ?o . FILTER(CONTAINS(str(?s), "{subjs[0]}")) . ' \
                        f'FILTER(CONTAINS(str(?s), "{subjs[1]}")) .'
        else:
            query_str = f'?s {pred} ?o . FILTER(CONTAINS(str(?s), "{subj}")) .'
    if 'xxx' in obj:
        return f'{query_str} FILTER(CONTAINS(str(?o), "{obj}")) .'
    # Place quotation marks around strings
    if not obj.isnumeric():
        if not obj.startswith(':') and not obj.startswith('geo:'):
            obj = f'"{obj}"'
    return query_str.replace('?o', obj)
