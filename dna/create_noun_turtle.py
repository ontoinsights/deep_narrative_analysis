# Functions to clean up the Turtle (before storage in Stardog)
# Called by create_narrative_turtle.py

import uuid

from dna.create_specific_turtle import create_type_turtle
from dna.get_ontology_mapping import get_noun_mapping
from dna.nlp import get_named_entities_in_string
from dna.query_ontology import get_norp_emotion_or_lob
from dna.query_sources import get_geonames_location, get_wikipedia_description
from dna.utilities import days, empty_string, months, names_to_geo_dict, space

person = ':Person'
person_collection = ':Person, :Collection'
explicit_plural = ('group', 'people')
part_of_group = ('member', 'group', 'citizen', 'people', 'affiliate', 'representative', 'associate', 'comrade')


def _check_presence_of_words(text: str, words: tuple) -> bool:
    """
    Determines if one of the 'words' in the input tuple is found in the 'text' string. Returns
    True if so.

    :param text: The string to be checked
    :param words: A tuple holding words to be searched for
    :return: True if one of the 'words' is found in the 'text; False otherwise
    """
    for word in words:
        if word in text:
            return True
    return False


def create_affiliation_ttl(noun_iri: str, noun_text: str, affiliated_text: str, affiliated_type: str) -> list:
    """
    Creates the Turtle for an Affiliation.

    :param noun_iri: String holding the entity/IRI to be affiliated
    :param noun_text: String holding the sentence text for the entity
    :param affiliated_text: String specifying the entity (organization, group, etc.) to which the
                            noun is affiliated
    :param affiliated_type: String specifying the class type of the entity
    :return: An array of strings holding the Turtle representation of the Affiliation
    """
    affiliated_iri = f':{affiliated_text.replace(" ", "_")}'
    affiliation_iri = f'{noun_iri}{affiliated_text.replace(" ", "_")}Affiliation'
    noun_str = f"'{noun_text}'"
    ttl = [f'{affiliation_iri} a :Affiliation ; :affiliated_with {affiliated_iri} ; :affiliated_agent {noun_iri} .',
           f'{affiliation_iri} rdfs:label "Relationship based on the text, {noun_str}" .',
           f'{affiliated_iri} a {affiliated_type} ; rdfs:label "{affiliated_text}" .']
    wikipedia_desc = get_wikipedia_description(affiliated_text)
    if wikipedia_desc:
        ttl.append(f'{affiliated_iri} :definition "{wikipedia_desc}" .')
    return ttl


def create_agent_ttl(agent_iri: str, alt_names: list, agent_type: str, agent_class: str,
                     description: str) -> list:
    """
    Create the Turtle for a named entity that is identified as an Agent/Person.

    :param agent_iri: String holding the IRI to be assigned to the Agent
    :param alt_names: An array of strings of alternative names
    :param agent_type: The entity type for the Agent (for ex, FEMALESINGPERSON)
    :param agent_class: The mapping of the entity type to the DNA ontology
    :param description: A description of the person from Wikipedia, if available; Otherwise,
                        an empty string
    :return: A tuple holding the agent_class and an array of its Turtle declaration
    """
    labels = '", "'.join(alt_names)
    agent_ttl = [f'{agent_iri} a {agent_class} .',
                 f'{agent_iri} rdfs:label "{labels}" .']
    if description:
        agent_ttl.append(f'{agent_iri} :description "{description}" .')
    if 'FEMALE' in agent_type:
        agent_ttl.append(f'{agent_iri} :gender "Female" .')
    elif 'MALE' in agent_type:
        agent_ttl.append(f'{agent_iri} :gender "Male" .')
    return agent_ttl


def create_named_event_ttl(event_iri: str, alt_names: list, event_classes: list, description: str,
                           start_time_iri: str, end_time_iri: str) -> list:
    """
    Return the Turtle related to a named event.

    :param event_iri: The IRI created for the event
    :param alt_names: An array of strings which represent alternate names for the event
    :param event_classes: An array with mappings of the event to the DNA ontology
    :param description: A description of the event from Wikipedia, if available; Otherwise,
                        an empty string
    :param start_time_iri: The IRI created for the starting time of the event
    :param end_time_iri: The IRI created for the ending time of the event
    :return: An array of Turtle statements
    """
    labels = '", "'.join(alt_names)
    event_ttl = [f'{event_iri} a {", ".join(event_classes)} .',
                 f'{event_iri} rdfs:label "{labels}" .']
    if description:
        event_ttl.append(f'{event_iri} :description "{description}" .')
    if start_time_iri:
        event_ttl.append(f'{event_iri} :has_beginning {start_time_iri} .')
    if end_time_iri:
        event_ttl.append(f'{event_iri} :has_end {end_time_iri} .')
    return event_ttl


def create_geonames_ttl(loc_iri: str, loc_text: str) -> (list, str, list):
    """
    Create the Turtle for a location that is a location described by GeoNames.

    :param loc_iri: String holding the IRI to be assigned to the location
    :param loc_text: The location text
    :return: A tuple holding an array that are the individual Turtle statements describing
              the location (if available; otherwise, an empty array), the location's class mapping
              (there is only 1), and an array of alternate names for the location (if available;
              otherwise, an array with the loc_text)
    """
    geonames_ttl = []
    class_type, country, admin_level, alt_names = get_geonames_location(loc_text)
    if class_type:
        geonames_ttl.extend(create_type_turtle([class_type], loc_iri, False, loc_text))
        names_text = '", "'.join(alt_names)
        geonames_ttl.append(f'{loc_iri} rdfs:label "{names_text}" .')
        wiki_desc = get_wikipedia_description(loc_text)
        if wiki_desc:
            geonames_ttl.append(f'{loc_iri} :description "{wiki_desc}" .')
        if admin_level > 0:
            geonames_ttl.append(f'{loc_iri} :admin_level {str(admin_level)} .')
        if country and country != "None":
            geonames_ttl.append(f'{loc_iri} :country_name "{country}" .')
            if country in names_to_geo_dict:
                geonames_ttl.append(f'geo:{names_to_geo_dict[country]} :has_component {loc_iri} .')
    return geonames_ttl, class_type, alt_names


def create_norp_ttl(noun_text: str, noun_type: str, noun_iri: str) -> (list, list):
    """
    Definition of the Turtle for a Person, Group or Organization that was identified by spaCy as a
    'NORP' (nationality, religion, political party, ...).

    :param noun_text: String holding the noun text
    :param noun_type: String holding the type of the noun (e.g., 'FEMALESINGPERSON' or 'PLURALNOUN')
    :param noun_iri: String identifying the noun concept as an IRI
    :return: A tuple holding the type of noun (e.g., Person or OrganizationalEntity) and an array of
             the defining Turtle (if appropriate)
    """
    # Check if ethnic group, religious group, ... that is already defined in the DNA ontology
    norp_type, norp_class = get_norp_emotion_or_lob(noun_text)
    wikipedia_desc = empty_string
    retrieved_desc = False
    if not norp_class or norp_type == 'EmotionalResponse' \
            or norp_type == 'LineOfBusiness':   # Should not be LOB or emotion
        # Check if a type of ethnic, religious or political group by checking the Wikipedia description
        wikipedia_desc = get_wikipedia_description(noun_text)
        retrieved_desc = True
        if wikipedia_desc:
            wikipedia_lower = wikipedia_desc.lower()
            if 'political' in wikipedia_lower or 'religio' in wikipedia_lower or 'ethnic' in wikipedia_lower:
                words = wikipedia_desc.split(space)
                for word in words:
                    if not word.istitle():   # Word is likely capitalized, so ignore lower cased words
                        continue
                    norp_type, norp_class = get_norp_emotion_or_lob(word)
                    if norp_class and norp_type != 'EmotionalResponse' and norp_type != 'LineOfBusiness':
                        break
    # Did not find match of the word or any details from its definition
    if not norp_class or norp_type == 'EmotionalResponse' or norp_type == 'LineOfBusiness':
        type_str = ':OrganizationalEntity'
        if 'PLURAL' in noun_type:
            type_str += ':, :Collection'
        norp_ttl = [f'{noun_iri} a {type_str} ; rdfs:label "{noun_text}" .']
        if not retrieved_desc:
            wikipedia_desc = get_wikipedia_description(noun_text)
        if wikipedia_desc:
            norp_ttl.append(f'{noun_iri} :description "{wikipedia_desc}" .')
    else:
        type_str = person
        if 'PLURAL' in noun_type:
            type_str = person_collection
        norp_ttl = [f'{noun_iri} a {type_str} ; rdfs:label "{noun_text}" .']
        if norp_type == 'ReligiousBelief' or norp_type == 'Ethnicity':
            norp_ttl.append(f'{noun_iri} :has_agent_aspect <{norp_class}> .')
        elif norp_type == 'PoliticalIdeology':
            norp_ttl.append(f'{noun_iri} :has_political_ideology <{norp_class}> .')
    if noun_type.startswith('NEG'):
        norp_ttl.append(f'{noun_iri} :negation true .')
    return [type_str], norp_ttl


def create_noun_ttl(noun_iri: str, noun_text: str, noun_type: str, is_subj: bool,
                    ext_sources: bool) -> (list, list):
    """
    Create the Turtle for a noun, given all the input information. And, if a new concept
    is found, update the last_nouns array and return its Turtle statement.

    :param noun_iri: String identifying the IRI/URL/individual associated with the noun_text
    :param noun_text: String specifying the noun text from the original narrative sentence
    :param noun_type: String holding the type of the noun (e.g., 'FEMALESINGPERSON' or 'PLURALNOUN')
    :param is_subj: Boolean indicating that the noun is the subject of a sentence
    :param ext_sources: A boolean indicating that data from GeoNames, Wikidata, etc. should be
                        added to the parse results if available
    :return: A tuple holding two arrays - 1) class mappings and 2) the Turtle of the noun semantics
    """
    # Process nouns based on their (mutually exclusive) entity type from spaCy
    class_name = empty_string
    if 'PERSON' in noun_type:
        class_name = person
    if noun_type.endswith('GPE'):
        class_name = ':GeopoliticalEntity+:Location'
    # Nationalities, religious or political groups
    if noun_type.endswith('NORP'):
        return create_norp_ttl(noun_text, noun_type, noun_iri)
    if noun_type.endswith('ORG'):
        class_name = ':Organization'
    if noun_type.endswith('LOC'):
        class_name = ':Location'
    if not class_name and _check_presence_of_words(noun_text, part_of_group):
        # Could be a reference to 'members OF'/'people IN'/... an org, group, ...
        class_name = person_collection if 'PLURAL' in noun_type or \
                                          _check_presence_of_words(noun_text, explicit_plural) else person
        # Check if an org, group, ... is mentioned
        for prep in ('of', 'in', 'from', 'with'):
            found_prep = (True if noun_text.lower().startswith(f'{prep} ') else False) or \
                         (True if f' {prep} ' in noun_text.lower() else False)
            if found_prep:
                # TODO: Handle general group reference (ex: 'soldiers in the Soviet army')
                agent_text, agent_type = get_named_entities_in_string(noun_text)
                if agent_text:  # Found a named entity that is an affiliated agent
                    new_ttl = create_affiliation_ttl(noun_iri, noun_text, agent_text, agent_type)
                    new_ttl.append(f'{noun_iri} a {class_name} ; rdfs:label "{noun_text}" .')
                    return new_ttl    # Return 2
    noun_ttl = []
    if not class_name:
        noun_mapping, noun_ttl = get_noun_mapping(noun_text, noun_iri)
        init_mappings = noun_mapping
    else:
        init_mappings = [class_name]
    class_mappings = []
    if 'PLURAL' in noun_type:
        for init_map in init_mappings:
            class_mappings.append(f'{init_map}, :Collection')
    else:
        class_mappings = init_mappings
    # Optimizations
    if len(class_mappings) > 1 and is_subj:
        # Future: For subjects, preference to Person type, defaulting to the first definition; Is this valid?
        person_map = [mapping for mapping in class_mappings if 'Person' in mapping]
        if len(person_map) > 0:
            class_mappings = person_map if len(person_map) == 1 else [person_map[0]]
    noun_ttl.extend(create_type_turtle(class_mappings, noun_iri, False, noun_text))
    noun_ttl.append(f'{noun_iri} rdfs:label "{noun_text}" .')
    if noun_type.startswith('NEG'):
        noun_ttl.append(f'{noun_iri} :negation true .')
    # Future: Update logic if more than Countries and Continents are defined in the core DNA ontologies
    wikipedia_desc = empty_string
    if not noun_iri.startswith('geo:') and ext_sources and (noun_type.endswith('GPE') or noun_type.endswith('ORG')):
        wikipedia_desc = get_wikipedia_description(noun_text)
    if wikipedia_desc:
        noun_ttl.append(f'{noun_iri} :description "{wikipedia_desc}" .')
    return class_mappings, noun_ttl


def create_time_ttl(time_text: str, time_iri: str) -> list:
    """
    Return the Turtle related to a point in time.

    :param time_text: The text defining the time
    :param time_iri: The IRI created for the time
    :return: An array of Turtle statements
    """
    time_ttl = [f'{time_iri} a :PointInTime ; rdfs:label "{time_text}" .']
    if '_Yr' in time_iri:
        time_ttl.append(f'{time_iri} :year {time_iri.split("_Yr")[1].split("_")[0]} .')
    if '_Mo' in time_iri:
        time_ttl.append(f'{time_iri} :month_of_year '
                        f'{str(months.index(time_iri.split("_Mo")[1].split("_")[0]) + 1)} .')
    if '_Day' in time_iri:
        day = time_iri.split("_Day")[1]
        if day in days:
            time_ttl.append(f'{time_iri} :day_of_week {days.index(day) + 1} .')
        else:
            time_ttl.append(f'{time_iri} :day_of_month {day} .')
    return time_ttl


def create_using_details(verb_dict: dict, event_iri: str, turtle: list) -> str:
    """
    Special case processing if the word, 'using', is in the sentence (e.g., 'he cut the bread
    using a knife').

    :param verb_dict: The dictionary entry for the verb in the current sentence
    :param event_iri: String holding the IRI identifier of the verb/event
    :param turtle: An array of the current Turtle for the sentence
    :return: A string holding additional label text, if the word 'using' is in the sentence;
              Otherwise, returns an empty_string
    """
    # Special case for the word, 'using'
    using_label = empty_string
    if 'verb_advcl' in verb_dict:
        advcl_text = str(verb_dict['verb_advcl'])
        if "'verb_lemma': 'use'" in advcl_text:
            inst_text = advcl_text.split("object_text': '")[1]
            inst_text2 = inst_text[:inst_text.index("',")]
            inst_type = advcl_text.split("object_type': '")[1]
            inst_type2 = inst_type[:inst_type.index("'}")]
            inst_iri = f':{inst_text2.replace(" ", "_")}_{str(uuid.uuid4())[:13]}'
            turtle.append(f'{event_iri} :has_instrument {inst_iri} .')
            # TODO: Need to check previous nouns and use external sources for instruments?
            inst_mappings, inst_ttl = create_noun_ttl(inst_iri, inst_text2, inst_type2, False, False)
            if inst_ttl:
                turtle.extend(inst_ttl)
            using_label = f' using {inst_text2}'
    return using_label
