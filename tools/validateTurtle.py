import argparse


def check_event(event: dict):
    """
    Make sure the incoming event has the following predicates [:sentence_offset, a] and least one other predicate
    :param event: A dictionary representing an individual event.  The keys are the predicates.
    :return: True if the event criteria is met, otherwise return false
    """
    okay = True
    if 'a' in event and ':sentence_offset' in event:
        if len(event.keys()) < 3:
            okay = False
    else:
        okay = False
    return okay


def check_for_missing_predicates(expected_e, missing_preds, a_identity):
    """
    Capture any expected predicates that were not specified for the event
    :param expected_e: The expected event (where all found predicates have been removed)
    :param missing_preds: Array for capturing the missing predications
    :param a_identity: the identity for the event that is being validated
    :return: None
    """
    captured = []
    for pred in expected_e:
        missing_preds.append(f'{a_identity} expected predicate {pred} got NULL')
        captured.append(pred)
    for pred in captured:
        del expected_e[pred]
        

def check_values(in_value, expected_value) -> bool:
    """
    Check if the expected_value in contained within the in_value.  
    :param in_value: The value to be checked
    :param expected_value: The expected string
    :return: True if the conditions are met, otherwise, False
    """
    j = in_value.find(expected_value)
    if j < 0:
        # check for weird extra \s
        if in_value.find("\\'s") > 0:
            s = in_value.replace("\\'s", "'s")
            j = s.find(expected_value)
    return j >= 0


def create_init_in_temp_file(file: str):
    """
    Create the expected init data structure in a temp file for the given turtle file.
    Then one, can cut and paste the contents of the temp file into init_expected for this turtle file.
    
    Then in the future the contents of a newly generated version of this turtle file can be validated to match
    what was assumed to be expected.
    :param file: The name of the turtle file with no extension
    """
    events = read_in_objects(file)
    new_file = file + '_temp.txt'
    file_out = open(new_file, "a")
    file_out.write('        init = {')
    first = True

    sorted_by_offest = sort_events(events)

    for offset in sorted_by_offest:
        if first:
            file_out.write(f'"{offset}": [\n')
        else:
            file_out.write(f'             ], \n        "{offset}": [\n')
        for event in sorted_by_offest[offset]:
            file_out.write('               {\n')
            for s in event:
                file_out.write(f'                "{s}": "{event[s]}", \n')
            file_out.write('               },\n')
            first = False
    file_out.write('              ] \n')
    file_out.write('        } \n')
    file_out.close()


def find_matching_event(offset: set, event_type: str, expected: dict) -> dict:
    """
    Find and return the dictionary for the validation event corresponding to the sentence offset and event type
    :param offset: The expected sentence offset
    :param event_type: The expected event_type (i.e. the 'a' value)
    :param expected: The dictionary containing all of the validation events
    :return: The dictionary for the validation event or None
    """
    matches = []
    events = expected[offset]

    for i in range(len(events)):
        if events[i]['a'] == event_type:
            matches.append(i)

    if len(matches) > 1:
        print("EXPECTED HAS MULTIPLE EVENTS OF SAME TYPE")

    if len(matches) > 0:
        match = events[matches[0]]
        events.pop(matches[0])
        return match
    else:
        return None


def init_expected_events(init_id: str) -> dict:
    """
    Initialize the expected events for the given turtle file
    :param init_id: the turtle file being verified
    :return: dictionary containing the expected events for a given turtle file
    """
    init = {}
    if init_id == 'Erika-Oct20':
        init = {"1": [
            {
                ":text": "Narrator was born on June 12, 1928, in Znojmo, a town in the Moravian region of "
                         "Czechoslovakia with a Jewish community dating back to the thirteenth century.",
                ":sentence_offset": "1",
                "a": "<urn:ontoinsights:dna:Birth>",
                ":has_time": ":PiTJune_1928",
                ":has_location": ":Znojmo",
                ":has_affected_agent": ":Narrator",
                "rdfs:label": "Narrator born in Znojmo",
                ":sentiment": "0.0",
            },
        ],
            "2": [
                {
                    ":text": "Her father was a respected attorney and an ardent Zionist who hoped to emigrate with "
                             "his family to Palestine.",
                    ":sentence_offset": "2",
                    "a": ":EnvironmentAndCondition",
                    ":has_topic": ":LineOfBusiness",
                    ":has_time": ":PiTJune_1928",
                    ":has_active_agent": ":father",
                    ":has_location": ":Znojmo",
                    "rdfs:label": "father was respected attorney, ardent Zionist",
                    ":sentiment": "0.0",
                },
            ],
            "3": [
                {
                    ":text": "In 1931, family moved to Stanesti, a town in the Romanian province of Bukovina, "
                             "where Narrator\'s paternal grandparents lived.",
                    ":sentence_offset": "3",
                    "a": "<urn:ontoinsights:dna:MovementTravelAndTransportation>",
                    ":has_time": ":PiT1931",
                    ":has_origin": ":Znojmo",
                    ":has_destination": ":Stanesti",
                    ":has_active_agent": ":family",
                    "rdfs:label": "family moved to Stanesti",
                    ":sentiment": "0.0",
                },
            ],
            "5": [
                {
                    ":text": "In Stanesti, Narrator attended the public school and the Hebrew school, which her father "
                             "had helped found.",
                    ":sentence_offset": "5",
                    "a": "<urn:ontoinsights:dna:EducationalEvent>",
                    ":has_time": ":PiT1931",
                    ":has_location": ":Stanesti",
                    ":has_active_agent": ":Narrator",
                    ":has_topic": ":Hebrew_school_",
                    "rdfs:label": "Narrator attended public school, Hebrew school in Stanesti",
                    ":sentiment": "0.0",
                },
            ],
            "6": [
                {
                    ":text": "She loved to play with her sister Beatrice and the other children in the town and "
                             "enjoyed being with her grandfather.",
                    ":sentence_offset": "6",
                    "a": ":MeetingAndEncounter",
                    ":has_time": ":PiT1931",
                    ":has_active_agent": ":Narrator",
                    ":has_location": ":Stanesti",
                    "rdfs:label": "Narrator being with grandfather",
                    ":sentiment": "0.35833333333333334",
                },
                {
                    ":text": "She loved to play with her sister Beatrice and the other children in the town and "
                             "enjoyed being with her grandfather.",
                    ":sentence_offset": "6",
                    ":has_topic": ":Event_",
                    "a": "<urn:ontoinsights:dna:Love>",
                    ":has_time": ":PiT1931",
                    ":has_active_agent": ":Narrator",
                    ":has_location": ":Stanesti",
                    "rdfs:label": "Narrator loved to play",
                    ":sentiment": "0.35833333333333334",
                },
                {
                    ":text": "She loved to play with her sister Beatrice and the other children in the town and "
                             "enjoyed being with her grandfather.",
                    ":sentence_offset": "6",
                    "a": "<urn:ontoinsights:dna:RecreationEvent>",
                    ":has_time": ":PiT1931",
                    ":has_active_agent": ":Narrator",
                    ":has_location": ":Stanesti",
                    "rdfs:label": "Narrator play with other children with sister",
                    ":sentiment": "0.35833333333333334",
                },
            ],
            "8": [
                {
                    ":text": "In 1937, however, members of the fascist Iron Guard tried to remove Narrator\'s father "
                             "from his position as the chief civil official in Stanesti.",
                    ":sentence_offset": "8",
                    ":has_topic": ":Event_",
                    "a": "<urn:ontoinsights:dna:Attempt>",
                    ":has_time": ":PiT1937",
                    ":has_active_agent": ":members_of_fascist_Iron_Guard_",
                    ":has_affected_agent": ":father",
                    ":has_location": ":Stanesti",
                    "rdfs:label": "members of fascist Iron Guard tried to remove father",
                    ":sentiment": "0.0",
                },
                {
                    ":text": "In 1937, however, members of the fascist Iron Guard tried to remove Narrator\'s father "
                             "from his position as the chief civil official in Stanesti.",
                    ":sentence_offset": "8",
                    "a": "<urn:ontoinsights:dna:RemovalAndRestriction>",
                    ":has_time": ":PiT1937",
                    ":has_topic": ":position_",
                    ":has_active_agent": ":members_of_fascist_Iron_Guard_",
                    ":has_affected_agent": ":father",
                    ":has_location": ":Stanesti",
                    "rdfs:label": "members of fascist Iron Guard remove father from position",
                    ":sentiment": "0.0",
                },
            ],
            "9": [
                {
                    ":text": "Eventually a court cleared him of the fabricated charges.",
                    ":sentence_offset": "9",
                    "a": "<urn:ontoinsights:dna:RemovalAndRestriction>",
                    ":has_time": ":PiT1937",
                    ":has_topic": ":fabricated_charges_",
                    ":has_active_agent": ":court_",
                    ":has_affected_agent": ":father",
                    ":has_location": ":Stanesti",
                    "rdfs:label": "court cleared father of fabricated charges",
                    ":sentiment": "0.0",
                },
            ],
            "10": [
                {
                    ":text": "he was restored to his post.",
                    ":sentence_offset": "10",
                    "a": "<urn:ontoinsights:dna:ReturnRecoveryAndRelease>",
                    ":has_time": ":PiT1937",
                    ":has_topic": ":post_",
                    ":has_affected_agent": ":father",
                    ":has_location": ":Stanesti",
                    "rdfs:label": "father restored to post",
                    ":sentiment": "0.0",
                },
            ],
            "12": [
                {
                    ":text": "In 1940, the Soviet Union occupied Bukovina.",
                    ":sentence_offset": "12",
                    "a": "<urn:ontoinsights:dna:InvasionAndOccupation>",
                    ":has_time": ":PiT1940",
                    ":has_active_agent": ":Soviet_Union",
                    ":has_affected_agent": ":Bukovina",
                    ":has_location": ":Stanesti",
                    "rdfs:label": "Soviet Union occupied Bukovina",
                    ":sentiment": "0.0",
                },
            ],
            "13": [
                {
                    ":text": "A year later the Soviets were driven from Stanesti.",
                    ":sentence_offset": "13",
                    "a": "<urn:ontoinsights:dna:MovementTravelAndTransportation>",
                    ":has_time": ":PiT1941",
                    ":has_origin": ":Stanesti",
                    ":has_active_agent": ":Soviets_",
                    "rdfs:label": "Soviets driven from Stanesti",
                    ":sentiment": "0.0",
                },
            ],
            "14": [
                {
                    ":text": "Romania joined Nazi Germany in the war against the Soviet Union.",
                    ":sentence_offset": "14",
                    "a": "<urn:ontoinsights:dna:Affiliation>",
                    ":has_time": ":PiT1941",
                    ":affiliated_agent": ":Romania",
                    ":affiliated_with": "<urn:ontoinsights:dna:NaziGermany>",
                    ":has_location": ":Stanesti",
                    "rdfs:label": "Romania joined Nazi Germany in war",
                    ":sentiment": "0.0",
                },
            ],
            "15": [
                {
                    ":text": "Mobs then carried out bloody attacks on the town\'s Jews.",
                    ":sentence_offset": "15",
                    "a": ":AttackDamageAndAssault",
                    ":has_time": ":PiT1941",
                    ":has_active_agent": ":Mobs_",
                    ":has_location": ":Stanesti",
                    "rdfs:label": "Mobs carried bloody attacks on Jews",
                    ":has_affected_agent": ":towns_Jews_",
                    ":sentiment": "-0.8",
                },
            ],
            "16": [
                {
                    ":text": "During the violence, Narrator and her family fled to Czernowitz with the aid of the "
                             "local police chief.",
                    ":sentence_offset": "16",
                    "a": "<urn:ontoinsights:dna:EscapeAndEvasion>",
                    ":has_time": ":PiT1941",
                    ":has_destination": ":Czernowitz",
                    ":has_instrument": ":aid_",
                    ":has_active_agent": ":Narrator",
                    "rdfs:label": "family, Narrator fled during violence to Czernowitz with aid",
                    ":sentiment": "0.0",
                },
            ],
            "17": [
                {
                    ":text": "In fall of 1941, family were forced to settle in the Czernowitz ghetto, where living "
                             "conditions were poor and they were subject to deportation to Transnistria.",
                    ":sentence_offset": "17",
                    ":has_topic": ":Event_",
                    "a": "<urn:ontoinsights:dna:CoercionAndIntimidation>",
                    ":has_time": ":PiT1941",
                    ":has_affected_agent": ":family",
                    ":has_location": ":Czernowitz",
                    "rdfs:label": "family forced to settle",
                    ":sentiment": "-0.2888888888888889",
                },
                {
                    ":text": "In fall of 1941, family were forced to settle in the Czernowitz ghetto, where living "
                             "conditions were poor and they were subject to deportation to Transnistria.",
                    ":sentence_offset": "17",
                    "a": "<urn:ontoinsights:dna:Resettlement>",
                    ":has_time": ":PiT1941",
                    ":has_location": ":Czernowitz_ghetto",
                    "rdfs:label": "settle in Czernowitz ghetto",
                    ":has_active_agent": ":family",
                    ":sentiment": "-0.2888888888888889",
                },
            ],
            "18": [
                {
                    ":text": "In 1943, Narrator and Beatrice escaped from the ghetto using false papers that "
                             "their father had obtained.",
                    ":sentence_offset": "18",
                    "a": "<urn:ontoinsights:dna:EscapeAndEvasion>",
                    ":has_time": ":PiT1943",
                    ":has_instrument": ":false_papers_",
                    ":has_origin": ":ghetto_",
                    ":has_active_agent": ":Narrator",
                    "rdfs:label": "sister, Narrator escaped from ghetto",
                    ":sentiment": "-0.4000000000000001",
                },
            ],
            "19": [
                {
                    ":text": "After escaping to the Soviet Union Narrator and Beatrice returned to Czechoslovakia "
                             "after World War II.",
                    ":sentence_offset": "19",
                    "a": "<urn:ontoinsights:dna:ReturnRecoveryAndRelease>",
                    ":has_earliest_beginning": ":PiTSeptember_1945",
                    ":has_destination": "geo:3057568",
                    ":has_active_agent": ":Narrator",
                    "rdfs:label": "sister, Narrator returned after escaping to Czechoslovakia",
                    ":sentiment": "0.0",
                },
            ],
            "20": [
                {
                    ":text": "where they were eventually reunited with their parents",
                    ":sentence_offset": "20",
                    "a": ":InclusionAttachmentAndUnification",
                    ":has_earliest_beginning": ":PiTSeptember_1945",
                    ":has_affected_agent": ":parents",
                    ":has_location": "geo:3057568",
                    "rdfs:label": "sister, Narrator reunited with parents",
                    ":sentiment": "0.0",
                },
            ],
            "23": [
                {
                    ":text": "Narrator married an officer in the Czech army and raised two children.",
                    ":sentence_offset": "23",
                    "a": ":CaringForDependents",
                    ":has_topic": ":two_children_",
                    ":has_earliest_beginning": ":PiTSeptember_1945",
                    ":has_active_agent": ":Narrator",
                    ":has_affected_agent": ":two_children_",
                    ":has_location": "geo:3057568",
                    "rdfs:label": "Narrator raised two children",
                    ":sentiment": "0.25",
                },
                {
                    ":text": "Narrator married an officer in the Czech army and raised two children.",
                    ":sentence_offset": "23",
                    "a": ":Marriage",
                    ":has_active_agent": ":officer_in_Czech_army_",
                    ":has_earliest_beginning": ":PiTSeptember_1945",
                    ":has_location": "geo:3057568",
                    "rdfs:label": "Narrator married officer in Czech army",
                    ":sentiment": "0.25",
                },
            ],
            "24": [
                {
                    ":text": "After many years of hard effort and her mother and sister\'s appeals to Soviet leader "
                             "Nikita Khrushchev, she was permitted to emigrate from Czechoslovakia to the United "
                             "States in 1960, three years after the death of her husband.",
                    ":sentence_offset": "24",
                    ":has_topic": ":Event_",
                    "a": "<urn:ontoinsights:dna:Permission>",
                    ":has_time": ":PiT1960",
                    ":has_affected_agent": ":Narrator",
                    ":has_location": "geo:3057568",
                    "rdfs:label": "Narrator permitted to emigrate after sister after appeals after mother",
                    ":sentiment": "0.10416666666666666",
                },
                {
                    ":text": "After many years of hard effort and her mother and sister\'s appeals to Soviet leader "
                             "Nikita Khrushchev, she was permitted to emigrate from Czechoslovakia to the United "
                             "States in 1960, three years after the death of her husband.",
                    ":sentence_offset": "24",
                    "a": "<urn:ontoinsights:dna:MovementTravelAndTransportation>",
                    ":has_time": ":PiT1960",
                    ":has_origin": "geo:3057568",
                    ":has_destination": "geo:6252001",
                    "rdfs:label": "emigrate from Czechoslovakia to United States",
                    ":has_active_agent": ":Narrator",
                    ":sentiment": "0.10416666666666666",
                },
            ],
            "25": [
                {
                    ":text": "Once in the United States, Narrator became a supervisor of a pathology lab.",
                    ":sentence_offset": "25",
                    "a": ":EnvironmentAndCondition",
                    ":has_time": ":PiT1960",
                    ":has_active_agent": ":Narrator",
                    ":has_topic": ":supervisor_of_pathology_lab_",
                    ":has_location": "geo:3057568",
                    "rdfs:label": "Narrator became supervisor of pathology lab",
                    ":sentiment": "0.0",
                },
            ]
        }
    return init


def parse_continue(line: str, extra: dict):
    """
    There was a ; vs a . for the turtle.  So get the next predicate and object
    :param line: the string containing the ; and what follows
    :param extra: a dictionary containing the extra predicates for the subject
    :return: None
    """
    pi = line.find(' ')
    pre = line[0:pi].strip().replace('"', '')
    obj = parse_out_object(line[pi:], extra)
    extra[pre] = obj


def parse_line(line: str) -> (str, str, str, dict):
    """
    Parse the line of turtle for the subject, predicate, object.  Some lines have multiple predicates --- those extras
    are retruned in the dictionary (whose keys are the predicates)
    :param line: The line to be parsed
    :return: subject, predicate, object, and a dictionary for extra predicates
    """
    extra = {}
    si = line.find(' ')
    sub = line[0:si].strip().replace('"', '')
    pi = line.find(' ', si+1)
    pre = line[si:pi].strip().replace('"', '')
    obj = parse_out_object(line[pi:], extra)

    return sub, pre, obj, extra


def parse_out_object(line, extra) -> str:
    """
    Parse out the object from the line and check if there are mulitple predicates specified on this line.
    :param line: The line to be parsed starting with the first characters of the object
    :param extra: dictionary containing any extras already found for this subject
    :return: the object
    """
    oi = line.rfind(';')
    if oi < 0:
        oi = line.rfind('.')
    else:
        parse_continue(line[oi+1:].strip(), extra)
    if oi > 0:
        obj = line[0:oi].strip().replace('"', '')
    else:
        obj = line.replace('"', '')

    if obj.rfind('-') > 0:
        x = obj.rfind('_')
        if x > 0:
            uuid = obj[x:]
            if len(uuid) == 14:
                obj = obj[0:x+1]
    return obj


def print_validation_errors(errors: list, header: str, okay_in: bool) -> bool:
    """
    Check if any error where captured for the type of error (specified by the header).  If there were errors then print
    the header and the errors
    :param errors: A list of captured errors
    :param header: The type of errors that are in the list
    :param okay_in:  Running indication if there were any errors
    :return: False: if errors > 0 or if okay_in was False,  Otherwise, returns True
    """
    okay = okay_in
    if len(errors) > 0:
        okay = False
        print()
        print(f'{header}:')
        for e in errors:
            print(e)
    return okay


def read_in_objects(file: str) -> dict:
    """
    Create an dictionary for the event objects defined in the specified turtle file
    :param file: turtle file without the .ttl extension
    :return: A dictionary of event objects
    """
    ttl_file = file + '.ttl'
    ttl_in = open(ttl_file, 'r')
    events = {}
    # read in the lines and then process them
    lines = ttl_in.readlines()
    for line in lines:
        # only care about event objects at this time
        if line.find(":Event_") == 0:
            # parse the line into it's subject, predicate, object, and if there was more on the line it is in extra
            sub, pre, obj, extra = parse_line(line)
            # check if we already have this event (i.e. more predicates for an existing event) or if it is a new one
            if sub in events:
                event = events[sub]
            else:
                event = {}
                events[sub] = event
            # create a key for the predicate and save the object
            event[pre] = obj
            # if there were extra predicates on the same line --- save those as well
            for pred in extra:
                event[pred] = extra[pred]
    ttl_in.close()
    return events


def sort_events(events) -> dict:
    """
    The incoming events are in a dictionary whos keys are the actually event uuids.  The uuids may not be the same uuid
    between turtle file generations.  So the validation wants to key off the sentence offset instead.  This routine 
    creates the data structure that is returned by init_expected_events()
    :param events: A dictionary containing the events that are defined by the turtle file whose keys are the event uuid
    :return: A dictionary containing the events that are defined by the turtle file whose keys are the sentence offsets
    """
    by_offset = {}
    for e in events:
        if check_event(events[e]):
            if events[e][':sentence_offset'] not in by_offset:
                by_offset[events[e][':sentence_offset']] = []
            by_offset[events[e][':sentence_offset']].append(events[e])
    return by_offset


def verify_turtle_against_expected(file: str):
    """
    This assumes that init_expected_events has been updated to contain the events that are expected for the turtle file.
    If so, it then verifies that the specified turtle file has the expected events, predicates, and values.
    It prints out to the screen all errors that are detected --- or SUCCESSFULLY
    :param file: The turtle file to be validated (with out the .ttl extension)
    :return: None
    """
    
    # Initialize the varies kinds of errors that will be captured
    missing_offset = []
    missing_event = []
    unknown_offset = []
    unmatched_event = []
    extra_preds = []
    mismatches_values = []
    missing_preds = []
    missing_events = []
    
    # Initialized the dictionary contained the expected events (keys are :sentence_offset)
    expected = init_expected_events(file)
    if len(expected) == 0:
        print(f'CAN NOT VERIFY --- NO VALIDATION SPECIFIED for {file}')
        return()
    
    # Create a dictionary of events defined in the turtle file (keys are the event uuids)
    actual = read_in_objects(file)

    # For every event in turtle file --- validate it against the expected events
    for e in actual:
        a_event = actual[e]
        if ':sentence_offset' not in a_event:
            missing_offset.append(str(e))
        elif 'a' not in a_event:
            missing_event.append(str(e))
        elif a_event[':sentence_offset'] not in expected:
            unknown_offset.append(f'offset of {a_event[":sentence_offset"]} was specified for {str(e)}')
        else:
            expected_e = find_matching_event(a_event[':sentence_offset'], a_event['a'], expected)
            if expected_e is None:
                unmatched_event.append(f'for sentence offset {a_event[":sentence_offset"]} event {a_event["a"]} '
                                       f'was not found in validation')
            else:
                # Found the matching event validation, now validate the predicates and their values
                a_identity = f'offset {a_event[":sentence_offset"]} event {str(e)} '
                for pred in a_event:
                    if pred not in expected_e:
                        extra_preds.append(f'{a_identity} - no validation for predicate {pred}')
                    else:
                        if not check_values(a_event[pred], expected_e[pred]):
                            mismatches_values.append(f'{a_identity} predicate {pred} expected: {expected_e[pred]} got '
                                                     f'{a_event[pred]}')
                        del expected_e[pred]
                # Capture all expected predicates that were missing from the event under test
                check_for_missing_predicates(expected_e, missing_preds, a_identity)
 
    # Capture all expected events that were missing from the turtle file under test
    for offset in expected:
        for event in expected[offset]:
            missing_events.append(f'Expected sentence offset {offset} event {event["a"]} got NULL')

    # Print out the results
    print("VALIDATION COMPLETED: ")
    okay = print_validation_errors(missing_offset, 'There was no sentence offset specified for event(s)', True)
    okay = print_validation_errors(missing_event, 'There was no event type specified for event(s)', okay)
    okay = print_validation_errors(unknown_offset, 'Validation does not contain sentence offset(s)', okay)
    okay = print_validation_errors(unmatched_event,
                                   'Validation does not contain the specified event type for sentence offset',
                                   okay)
    okay = print_validation_errors(extra_preds, 'Validation does not include the following predicates', okay)
    okay = print_validation_errors(mismatches_values, 'Values do not match', okay)
    okay = print_validation_errors(missing_preds, 'Validation expected these predicates', okay)
    okay = print_validation_errors(missing_events, 'Validation expected these events', okay)
    if okay:
        print("SUCCESSFULLY")


def run_main():
    """
    The first time --- you need to create the data structure to validate against.  To do this:
        1) Run the program with the create cmd
            python3 validateTurtle create Erika-Oct20
        2) Cut and paste the contents of the temp file into init_expected_events
            (i.e. Erika-Oct20_temp.txt).  This file can then be deleted.
    From then on.  When a new version of the turtle file has been create, then you can run the validate cmd to
    insure that the events have remained the same.
        1) Run the program with the validate cmd
            python3 validateTurtle validate Erika-Oct20
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(dest='cmd', type=str,
                        help='cmd = create , validate')
    parser.add_argument(dest='file', type=str,
                        help='name of the turtle file (without an extension')
    args = parser.parse_args()

    cmd = args.cmd.lower()
    filename = args.file

    if cmd == 'create':
        create_init_in_temp_file(filename)
    elif cmd == 'validate':
        verify_turtle_against_expected(filename)
    else:
        print("Please try again, create or run are valid command")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    run_main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
