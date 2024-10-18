# Query for details using OpenAI
# Constants, prompts (titled xxx_prompt) and JSON formats (titled xxx_result)

import json
import logging
import os

from openai import OpenAI
# from tenacity import *

openai_api_key = os.environ.get('OPENAI_API_KEY')
model_engine = "gpt-4o"
client = OpenAI()

any_boolean = 'true/false'
interpretation_views = 'conservative, liberal or neutral'
pronoun_text = 'I, we, they, them, he, she, it, myself, ourselves, themselves, herself, himself or itself'
semantic_role_text = 'affiliation, agent, patient, theme, content, experiencer, instrument, location, time, goal, ' \
                     'cause, source, state, subject, purpose, recipient, measure, or attribute'
sentiment = 'positive, negative or neutral'
tense = 'past, present or future'

# JSON formats
attribution_result = '{"speaker": "string"}'

consistency_result = '{"consistent": "bool"}'

coref_result = '{"updated_sentences": ["string"]}'

events_result = '{"sentences": [{' \
                '"sentence_number": "int", ' \
                '"verbs": [{"trigger_text": "string", ' \
                '"category_number": "int", "category_same_or_opposite": "string", "correctness": "int"}]}]}'

noun_categories_result = '{"sentence_nouns": [{' \
                          '"verb_text": "string", ' \
                          '"noun_information": [{' \
                          '"trigger_text": "string", "is_plural": "bool", "semantic_role": "string", ' \
                          '"category_number": "int", "category_same_or_opposite": "string", "correctness": "int"}]}]}'

noun_events_result = '{"category_number": "int", ' \
                      '"category_same_or_opposite": "string", ' \
                      '"category_correctness": "int"}'

narrative_summary_result = '{"goal_numbers": ["int"], ' \
                           '"summary": "string", ' \
                           '"interpreted_text": [{"perspective": "string", "interpretation": "string"}], ' \
                           '"ranking_by_perspective": [{"perspective": "string", "ranking": "int"}]' \
                           '"sentiment": "string", "sentiment_explanation": "string"}'

sentence_result = '{"grade_level": "int", ' \
                  '"summary": "string", ' \
                  '"rhetorical_devices": [{"device_number": "int", "explanation": "string"}]}'

# Ontology details / event and state classes
event_categories = [
    ':AchievementAndAccomplishment', ':AcquisitionPossessionAndTransfer', ':Affiliation',
    ':AggressiveCriminalOrHostileAct', ':Agreement', ':AgricultureApicultureAndAquacultureEvent',
    ':LawEnforcement', ':ArtAndEntertainmentEvent', ':Assessment', ':Attempt', ':Attendance', ':Avoidance',
    ':Birth', ':BodilyAct', ':Change', ':Cognition', ':Commemoration', ':CommunicationAndSpeechAct',
    ':Continuation', ':Death', ':DeceptionAndDishonesty', ':DelayAndWait', ':DemonstrationStrikeAndRally',
    ':DisagreementAndDispute', ':DiscriminationAndPrejudice', ':DistributionSupplyAndStorage',
    ':DivorceAndSeparation', ':EconomyAndFinanceRelated', ':EducationRelated', ':EmotionalResponse', ':End',
    ':EnvironmentAndCondition', ':EnvironmentalOrEcologicalEvent', ':HealthAndDiseaseRelated',
    ':ImpactAndContact', ':InclusionAttachmentAndUnification', ':IssuingAndPublishing',
    ':LegalEvent', ':Marriage', ':Measurement', ':MeetingAndEncounter', ':Mistake',
    ':MovementTravelAndTransportation', ':OpenMindednessAndTolerance', ':PoliticalEvent', ':Process',
    ':ProductionManufactureAndCreation', ':Punishment', ':ReadinessAndAbility', ':ReligionRelated',
    ':RemovalAndRestriction', ':Residence', ':ReturnRecoveryAndRelease', ':RewardAndCompensation',
    ':RiskTaking', ':Searching', ':SensoryPerception', ':Separation', ':SpaceEvent', ':StartAndBeginning',
    ':Substitution', ':TechnologyRelated', ':UtilizationAndConsumption', ':Win', ':Loss',
    ':AidAndAssistance', ':Causation', ':EventAndState']
event_category_texts = [
    'achieving or accomplishing something',  # 1
    'acquisition such as by purchase or sale, finding or stealing something, seizure, transfer of possession',  # 2
    'affiliation or close association of a person or thing with another entity, or membership of a person in a group',
    'hostile or criminal act such as an attack, purposeful destruction such as looting, intimidation, betrayal, '
    'murder, abduction, etc.',  # 4
    'agreement, consensus and compliance/accordance',  #
    'an agricultural, apiculture, viniculture and aquacultural act such as planting seeds, bottling wine, or '
    'harvesting honey',  # 6
    'a police/law enforcement activity such as arrest, incarceration, capture, detention, imprisonment',  # 7
    'performing or playing in an artistic, entertainment or sporting event such as playing golf, '
    'singing in a musical performance, acting in a movie, etc.',  # 8
    'an assessment, estimation, prioritization, evaluation, etc.',  # 9
    'attempting something',  # 10
    'attendance of an artistic, entertainment or sporting event',  # 11
    'avoidance such as bans, boycotts, escape, ignoring something/someone, prevention, concealment',  # 12
    'birth of a living being',  # 13
    'bodily act such as movement, eating, drinking, grooming, sleeping',  # 14
    'change such as increase, decrease or physical change such as melting, bending and vaporization',  # 15
    'any type of thinking, focusing, reading, characterizing/comparing, deciding, planning, etc.',  # 16
    'any commemorative or celebratory activity such as celebrating "Independence Day" or a birthday',  # 17
    'a communication or speech act such as stating, explaining or detailing something, permitting/refusing, '
    'questioning, responding, etc.',  # 18
    'continuation',  # 19
    'death of a living being which is NOT murder, homicide or suicide',  # 20
    'an act of deception, of concealing or misrepresenting the truth, or of being fraudulent or dishonest',  # 21
    'delay, postponement or need to wait for something or someone',  # 22
    'a protest, demonstration, rally or strike',  # 23
    'disagreement, disapproval, dispute, controversy or violation of agreement',  # 24
    'discrimination, prejudice, or any act that is intolerant, unjust, unfair, inappropriate',  # 25
    'any type of goods distribution, supply or storage',  # 26
    'divorce or separation of a couple in a relationship',  # 27
    'related to economic or financial matters and conditions such as being in recession, going bankrupt, etc.',  # 28
    'related to educational events such as attending school, graduating, practicing or drilling, etc.',  # 29
    'any type of emotion or emotional response',  # 30
    'end or completion of something or the obtaining of a result/outcome',  # 31
    'description of a characteristic or attribute of a person, place, event, or thing such as its physical '
    'appearance, population, role, occupation, etc',  # 32
    'any type of environmental or ecological event such as a natural disaster, weather event, or other natural '
    'phenomenon or emergency',  # 33
    'related to health and disease such as contracting a disease, addiction, physical injury, frailty, '
    'allergic reactions, vaccinations, sterility',  # 34
    'impact, contact and collision',  # 35
    'inclusion, unification, alignment and attachment such as adding to a list and assembling something',  # 36
    'issuing and publishing information such as a publishing a newspaper, or releasing a document such as a '
    'press briefing',  # 37
    'any legal or judicial event such as testifying or arguing at a trial, reaching a verdict, selecting a jury, '
    'or handing down or appealing a judicial ruling',  # 38
    'marriage',  # 39
    'an act or reporting of a measurement, count or scientific unit/value',  # 40
    'meeting and encounter such as a seminar or conference, spending time with or visiting someone',  # 41
    'error or mistake',  # 42
    'any type of movement, travel or transportation such as entering/leaving a port, loading a truck, and '
    'making incremental changes such as pouring liquid into a container',  # 43
    'open-mindedness or tolerance',  # 44
    'any political event or occurrence such as an election, referendum, coup, transfer of power, and political '
    'campaign',  # 45
    'a natural or goal-directed process (including plans and strategies) involving several related or '
    'interdependent events and conditions',  # 46
    'any type of production, manufacture and creation event such as designing, building or producing a product',  # 47
    'punishment',  # 48
    'readiness, preparation and ability',  # 49
    'any religious event or activity such as church services, observance of Ramadan, praying, meditation, etc.',  # 50
    'removal or restriction of something, including blockage of movement, access, flow or personal activities',  # 51
    'an act of restoring or releasing something or someone to their original owner/location/condition, or '
    'granting freedom or parole to someone or something',  # 52
    'act of living or residing in a location',  # 53
    'reward, compensation, award and prize',  # 54
    'risk taking including gambling',  # 55
    'search, research and investigation',  # 56
    'any type of sensory perception such as pain, hunger, exhaustion and other sensations',  # 57
    'separation of two or more things by cutting, pulling apart, etc.',  # 58
    'any type of space event such as a meteor shower, sun spots, eclipse, or rocket or satellite launch',  # 59
    'start or beginning of something',  # 60
    'substitution, imitation or counterfeiting of something or someone',  # 61
    'any event or activity related to science and technology, or involving computers and scientific '
    'devices/instruments',  # 62
    'utilization and consumption',  # 63
    'win and victory',  # 64
    'loss and defeat',  # 65
    'aid, assistance and cooperative effort',  # 66
    'causation, cause and effect',  # 67
    'other']  # 68
# having or using knowledge or skills which may be indicated by a job, hobby, schooling, practice = :KnowledgeAndSkill
event_categories_text = " ".join([f'{index}. {text}' for index, text in enumerate(event_category_texts, start=1)])

narrative_goals = ['advocate', 'analyze', 'describe-set', 'describe-current', 'entertain',
                   'establish-authority', 'inspire', 'life-story']
narrative_goals_text = 'The narrative goal categories are: ' \
    '1. Promote or advocate for a cause, person or thing ' \
    '2. Analyze an issue, event or trend in-depth, by breaking it down ' \
    '3. Describe/chronicle how a set of events, trends and conditions evolve over time ' \
    '4. Describe/report a current event, trend or condition ' \
    '5. Entertain using humor and engaging content ' \
    '6. Establish authority by citing facts, statistics and quotes from experts ' \
    '7. Inspire and motivate through uplifting stories, news, etc. ' \
    '8. Relate a personal narrative or life story ' \

noun_categories = event_categories[:-1]    # Not including other
noun_categories.extend([
    ':Animal', ':Ceremony', ':ComponentPart', ':EthnicGroup', ':FreedomAndSupportForHumanRights',
    ':GovernmentalEntity', ':InformationSource', ':LaborRelated', ':LawAndPolicy', ':LineOfBusiness',
    ':Location', ':MachineAndTool', ':MusicalInstrument', ':OrganizationalEntity', ':Person',
    ':Person, :Collection', ':PharmaceuticalAndMedicinal', ':Plant', ':PoliticalGroup', ':Product',
    ':ReligiousGroup', ':ScienceAndTechnology', ':SubstanceAndRawMaterial', ':TroubleAndProblem',
    ':WeaponAndAmmunition', ':War', ':WasteAndResidue', ':Resource', 'owl:Thing'])
noun_category_texts = event_category_texts[:-1]
noun_category_texts.extend([
    'animal',   # 68
    'ceremony',  # 69
    'part of a living thing such as a the leg of a person or animal or leaf of a plant',  # 70
    'related to ethnicity or an ethnic group',   # 71
    'fundamental rights such as life, liberty, freedom of speech, etc.',  # 72
    'a governmental body, organization, sub-organization, government-funded law-enforcement or military group, '
    'etc., but NOT a specific person, role/position or political event',  # 73
    'any entity that holds text, data/numbers, video, visual or audible content, etc. including documents, '
    'books, news articles, databases, spreadsheets, computer files or web pages',  # 74
    'related to labor such as employment/unemployment, the labor market, labor relations, retirement and unions',  # 75
    'a specific law, policy, legislation and legal decision (NOT including any legal occupations)',  # 76
    'occupation or business',  # 77
    'place or location including buildings, roads, bodies of water, etc.',   # 78
    'machine, tool or device',  # 79
    'musical instrument',  # 80
    'any non-governmental organization, sub-organization, club, social group, etc.',  # 81
    'person',  # 82
    'group of people such as a family or people at a party or in the park that are NOT named governmental, '
    'business, social or organizational entities',  # 83
    'pharmaceutical or medicinal entity',  # 84
    'plant',  # 85
    'set of persons with a common political ideology',  # 86
    'product or service which is bought, sold or traded',  # 87
    'related to religion, a religious group or a religious practice',  # 88
    'any of the sciences such as biomedical science, computer science, mathematics, natural science, '
    'social science, standards, engineering, etc.',  # 89
    'any chemical substance, raw material or natural material',  # 90
    'a situation which is undesirable and potentially harmful, a trouble or problem',  # 91
    'weapon or ammunition',  # 92
    'armed conflict, war, insurgency or armed clash',  # 93
    'waste or residue',  # 94
    'a non-living, man-made thing or part thereof',  # 95
    'other'])   # 96
noun_categories_text = " ".join([f'{index}. {text}' for index, text in enumerate(noun_category_texts, start=1)])

rhetorical_devices = ['ad baculum', 'ad hominem', 'ad populum', 'allusion', 'exceptionalism', 'expletive',
                      'hyperbole', 'imagery', 'invective', 'loaded language', 'logos', 'paralipsis', 'pathos']
rhetorical_devices_text = 'The rhetorical device categories are: ' \
    '1. An appeal to force or a threat of force in order to compel a conclusion (ad baculum)' \
    '2. Use of wording that verbally demeans or attacks a person (ad hominem) ' \
    '3. Reference to general or popular knowledge such as "the most popular xyz" or "everyone says xyz" (ad populum) ' \
    '4. Reference to an historical/literary person, place or thing that has symbolic meaning (allusion) ' \
    '5. Use of language that indicates that a particular entity is somehow unique, extraordinary or ' \
    'exemplary (exceptionalism)' \
    '6. Use of emphasis words, such as "in fact", "of course", "clearly" or "certainly" (expletive) ' \
    '7. Use of exaggerated wording (hyperbole) ' \
    '8. Use of imagery and descriptive phrases that paint a vivid picture that emotionally engages a reader (imagery)' \
    '9. Use of ridicule, or angry or insulting language (invective) ' \
    '10. Use of "loaded language" such as words like "double-dealing", with strong connotations which invoke ' \
    'emotions and judgments' \
    '11. Use of statistics and numbers (logos) ' \
    '12. Indicating that little or nothing is said about a subject in order to bring attention to it, ' \
    'such as saying "I will not mention their many crimes" (paralipsis)' \
    '13. Wording that appeals to emotion such as fear or empathy (pathos) '

# More complete list of rhetorical devices
# rhetorical_devices = ['ad baculum', 'ad hominem', 'ad populum', 'allusion', 'antanagoge', 'aphorism',
#                      'ethos', 'exceptionalism', 'expletive', 'hyperbole', 'imagery', 'invective', 'irony',
#                      'juxtaposition', 'kairos', 'litote', 'loaded language', 'logos', 'metaphor',
#                      'nostalgia', 'paralipsis', 'pathos', 'pleonasm', 'repetition', 'rhetorical question']
# rhetorical_devices_text = 'The rhetorical device categories are: ' \
#    '1. An appeal to force or a threat of force in order to compel a conclusion (ad baculum)' \
#    '2. Use of wording that verbally demeans or attacks a person (ad hominem) ' \
#    '3. Reference to general or popular knowledge such as "the most popular xyz" or "everyone says xyz" ' \
#    (ad populum) ' \
#    '4. Reference to an historical/literary person, place or thing that has symbolic meaning such as ' \
#    'saying that "sleeping late is my Achilles heel" where "Achilles heel" is the reference (allusion) ' \
#    '5. Balancing negative wording with positive (antanagoge) ' \
#    '6. Expressing a truth or moral principle such as "a stitch in time saves nine" (aphorism) ' \
#    '7. Reference to authority figures and/or to people in occupations that should have knowledge ' \
#    '(such as doctors or professors) in order to justify a statement (ethos) ' \
#    '8. Use of language that indicates that a particular entity is somehow unique, extraordinary or ' \
#    'exemplary (exceptionalism)' \
#    '9. Use of emphasis words, such as "in fact", "of course", "clearly" or "certainly" (expletive) ' \
#    '10. Use of exaggerated wording (hyperbole) ' \
#    '11. Use of imagery and descriptive phrases that paint a vivid picture that emotionally engages a reader ' \
#    '12. Use of ridicule, or angry or insulting language (invective) ' \
#    '13. Use of irony or satire ' \
#    '14. Placing contrasting ideas or situations side by side (juxtaposition)' \
#    '15. Reference invoking feelings/remembrances of specific day, time, event or season such as ' \
#    'discussing the Civil War in order to engage a reader (kairos) ' \
#    '16. Use of double negative (litote) ' \
#    '17. Use of "loaded language" such as words like "double-dealing", with strong connotations which invoke ' \
#    'emotions and judgments' \
#    '18. Use of logical reasoning terms, statistics and numbers (logos) ' \
#    '19. Use of analogy, metaphor and simile to compare one thing with another of a different kind, or to ' \
#    'compare an abstract thing with a concrete entity (such as peace being described as a dove) ' \
#    '20. Use of wording that invokes nostalgia ' \
#    '21. Indicating that little or nothing is said about a subject in order to bring attention to it, ' \
#    'such as saying "I will not mention their many crimes" (paralipsis)' \
#    '22. Wording that appeals to emotion such as fear or empathy (pathos) ' \
#    '23. Use of superfluous or redundant language such as referring to a "burning fire" (pleonasm) ' \
#    '24. Repeating words, phrases or sentences for emphasis ' \
#    '25. Asking rhetorical questions '

chatgpt1 = \
    'Task: You are ChatGPT, a large language model trained by OpenAI using the GPT-4 architecture, with expertise ' \
    'in linguistics and natural language processing (NLP). Your objective is to'

chatgpt2 = \
    'Task: You are ChatGPT, a large language model trained by OpenAI using the GPT-4 architecture, specializing in ' \
    'event linguistics research. Your objective is to'

chatgpt3 = \
    'Task: You are ChatGPT, a large language model trained by OpenAI using the GPT-4 architecture, specializing in ' \
    'political and historical events. Your objective is to'

chatgpt4 = \
    'Task: You are ChatGPT, a large language model trained by OpenAI using the GPT-4 architecture, with expertise ' \
    'as a political/historical observer. Your objective is to'

# Quotation prompt
attribution_prompt = \
    f'<{chatgpt1} identify the speaker of a quotation from a news article.> ' \
    '<Instructions: 1. Input Formats: a) You are provided with the text of a news article, which ends with the ' \
    'string "**" (this should be ignored). b) A specific quotation from the article is also provided, ' \
    'ending with the string "**" (this should also be ignored). ' \
    '2: Attribution Identification: Your task is to identify the speaker of the quotation by analyzing ' \
    'the context of the news article. If the speaker is referred to using a pronoun, resolve the pronoun by ' \
    'examining the surrounding text to determine its referent. ' \
    '3. Attribution Considerations: a) Ensure you return the name of the person who made the statement, not the ' \
    'individual or entity to whom it was communicated. b) If a direct name is not given, accurately infer the ' \
    'speaker based on the article’s context.> ' \
    '<Inputs: 1. News article: {narr_text} ** 2. Quotation: {quote_text} **> ' + \
    f'<Output: Return the response as a JSON object in the format: {attribution_result}>'

# Co-reference related prompting
coref_prompt = \
    f'<{chatgpt1} resolve co-references in sentences from a news article by replacing pronouns with their ' + \
    'appropriate noun references.> ' \
    '<Instructions: 1. Input Format: You are provided with the text of a news article. ' \
    'The article ends with the string "**", which should be ignored. ' \
    f'2. Co-Reference Resolution: For each sentence in the article: a) Identify any occurrence of the pronouns: ' \
    f'{pronoun_text}. b) Replace each pronoun with the appropriate noun or noun phrase it refers to, based ' \
    f'on the context of the sentence or the article. ' + \
    '3. Co-Reference Considerations: a) Ensure that all pronouns in the sentences are updated to their correct ' \
    'noun references. b) If a sentence contains none of the listed pronouns, return it as-is without modification.> ' \
    '<Input: {sentences} **> ' + \
    f'<Output: Return the response as a JSON object in the format: {coref_result} Each updated sentence should ' \
    f'replace the pronouns with their noun or noun phrase reference. If no changes are required for a sentence, ' \
    f'return the original sentence.>'

# Event and noun details prompts
events_prompt = \
    f'<{chatgpt2} analyze events and conditions described in sentences from news articles, blogs, or personal ' + \
    'narratives.> ' \
    '<Instructions: 1. Input Formats: a) You are provided with a set of numbered sentences from ' \
    'the article. After all sentences are provided, the string "**" indicates the end and should be ignored. b) ' \
    'A numbered list of event/state categories is also provided. ' \
    '2. Verb Identification: For each sentence: ' \
    'a) Identify the main verb and any verbs in subordinate clauses. b) Return the trigger word(s) for each verb, ' \
    'including any modals, negation, and open clausal complements (xcomps). c) If the sentence contains ' \
    'infinitive verbs, treat them as subordinate verbs. d) For verbs that are idioms, legal terms, ' \
    'or legalese, return the entire phrase as the trigger text. e) Expand any verb contractions in the trigger text ' \
    '(e.g., "didn’t" becomes "did not"). ' \
    '3. Verb Semantic Mapping: For each identified verb: a) Map each verb’s ' \
    'meaning to one of the numbered event/state categories provided in the input. Carefully consider the context ' \
    'of the sentence and review all possible categories before selecting the most relevant category. b) Indicate ' \
    'whether the selected event/state category matches the meaning of the verb ("same") or is the opposite ' \
    '("opposite"), accounting for negation in the sentence. c) Assign a correctness score (0-100) to each ' \
    'verb-to-category mapping, where 0 indicates incorrect mapping and 100 indicates high accuracy. ' \
    'd) If no appropriate category is available, assign category 68 ("other"). e) For verbs based solely ' \
    'on the lemmas "be" or "become", assign category 32 ("description").> ' \
    '<Inputs: 1. Numbered sentences {numbered_sentences_texts} ** ' + \
    f'2. Event/state categories: {event_categories_text}> ' \
    f'<Output: Return the results as a JSON object using the following structure: {events_result}>'

noun_categories_prompt = \
    f'<{chatgpt2} analyze verbs and their associated nouns from a sentence in a news article, blog, or personal ' + \
    'narrative.> ' \
    '<Instructions: 1. Input Formats: a) You are given a sentence ending with a list of its verbs of interest ' + \
    'in parentheses. b) A numbered list of semantic categories is also provided. ' \
    '2. Verb-Noun Analysis: For each verb of interest, locate the verb in the sentence and identify all nouns ' + \
    f'associated with it that play one of the following semantic roles: {semantic_role_text}. Use the following ' + \
    'instructions to determine the noun and its semantic role: a) Consider whether the sentence is in the active ' \
    'or passive voice when assigning the semantic role. b) If the verb is an infinitive (lacking its own subject), ' \
    'always return the subject noun associated with the verb on which the infinitive depends, as one of the nouns ' + \
    f'for the infinitive. c) If the noun is one of the pronouns, {pronoun_text}, resolve it to an explicit entity ' + \
    'by examining the surrounding text to determine its referent. Return the referent as one of the nouns for the ' \
    'verb. ' \
    '3. Noun Detailed Analysis: Return the following information about each noun from the "Verb-Noun Analysis": ' \
    'a) Indicate whether the noun is singular or plural. b) Map the noun semantics to one of the numbered ' \
    'categories proved in the inputs, following the considerations in "Noun Semantic Mappings". c) Return the ' \
    'trigger word(s) of the noun (without articles, possessive nouns, pronouns, or conjunctions) following the ' \
    'considerations in "Noun Trigger Text Considerations". ' \
    '4. Noun Semantic Mappings: For each noun category mapping: a) Return the category number from list provided as ' \
    'an input. b) To choose the correct category, first determine whether the noun represents a person, location, ' \
    'thing, event, or condition/state. Then, examine all categories before selecting the most appropriate one. ' \
    'c) Avoid assigning the same semantic category to the noun as the verb or its semantic role in the sentence. ' \
    'For example, for the sentence, “x caused y,” do not map “x” to the semantic of causation (number 67). ' \
    'd) Always map nouns referring to people to category 82, regardless of their role. For example, a "musician" ' \
    'is mapped to the semantic of a person (category 82), not to an "art or entertainment event" (category 8). e) ' \
    'Indicate whether the selected noun category matches the semantic meaning of the noun ("same") or is the ' \
    'opposite ("opposite"). Make sure to consider any negation in the sentence. f) Assign a correctness score ' \
    '(0-100) for the accuracy of the category mapping, where 0 indicates incorrectness. ' \
    '5. Noun Trigger Text Considerations: a) If the noun is an idiom, legal term, or legalese, return the full ' \
    'phrase as the trigger. b) If the noun refers to a person, only return their first and last name, or just ' \
    'the last name (if no first name is provided) as the trigger. Do not return honorifics (e.g., Mr., ' \
    'Mrs.), titles, or other designations.> ' \
    '<Inputs: 1. Sentence with verbs in parentheses at the end: {sentence_text} ' + \
    f'2. Semantic categories: {noun_categories_text}> ' \
    f'<Output: Return the results as a JSON object using the following structure: {noun_categories_result}>'

# Process EVENT entity
noun_events_prompt = \
    f'<{chatgpt3} map a specific event in history, referenced in a news article, to an event/state category.> ' + \
    '<Instructions: 1. Input Format: a) You are given a sentence ending with the string "**" which should be ' \
    'ignored. b) A list of proper nouns, found in the sentence and referencing historical/political events, are ' \
    'also provided. The list of nouns also ends with the string "**" which is also ignored. c) A numbered list ' \
    'of event/state categories is also provided. ' \
    '2. Semantic Category Mapping: Map the event semantics to one of the categories provided in the inputs. ' \
    '3. Semantic Mapping Considerations: a) Make sure to examine ALL the possible categories before selecting ' \
    'the most relevant one. b) When returning the event category, return its number from the categories list. ' \
    'c) Indicate if the semantic of the event category is the "same" as (or is the "opposite" of) the semantic of ' \
    'the event. d) Assign an estimate from 0-100 for the correctness of the mapping, where 0 indicates ' \
    'that it is incorrect. e) If no categories are appropriate, return the number 68 ("other").> ' \
    '<Inputs: 1. Sentence text: {sentence_text} ** 2. Event proper nouns: {noun_texts} ** ' + \
    f'3. Semantic categories: {event_categories_text}> ' \
    f'<Output: Return the results as a JSON object using the following structure: {noun_events_result}>'

# Narrative-level prompting
narrative_summary_prompt = \
    f'<{chatgpt4} describe and summarize a news article.> ' + \
    '<Instructions: 1. Input Format: a) You are given the text of an article, ending with the string "**" which ' \
    'is ignored. b) A numbered list of goals of the article is also provided. ' \
    '2. Article Analysis: a) Indicate the numbers of the 2 most likely goals of the article. b) Summarize the ' \
    'article. c) Explain how the article could be interpreted from each of the following perspectives: ' + \
    f'{interpretation_views}, and rank the text from 1-5 as to how positively it would be received by readers of ' + \
    'each perspective. Note that the rank of 1 is very negatively, and the rank of 5 is very positively. d) ' \
    'Indicate the sentiment of the article ("positive", "negative" or "neutral"), and explain why that sentiment ' \
    'was selected.> ' \
    '<Inputs: 1. Narrative: {narr_text} ** ' + \
    f'2. Goals: {narrative_goals_text}> ' \
    f'<Output: Return the results as a JSON object using the following structure: {narrative_summary_result}>'

# Sentence-level prompting
sentence_prompt = \
    f'<{chatgpt1} analyze a sentence from a narrative or news article.> ' + \
    '<Instructions: 1. Input Format: a) You are given the text of a sentence from an article, where ' \
    'the sentence ends with the string "**" which is ignored. b) A numbered list of rhetorical devices that ' \
    'may be used in the sentence, is also provided. ' \
    '2. Sentence Analysis: a) Indicate the grade level that is expected of a reader to understand the ' \
    'sentence semantics. b) Provide the numbers of the various rhetorical devices used in the sentence, and ' \
    'explain why they are identified. If there are no rhetorical devices used, return an empty array for ' \
    'the "rhetorical_devices" JSON key, specified in the Output. c) Create a summary of the sentence using 15 ' \
    'words or less, ONLY if the input sentence has more than 10 words. If the input sentence is 10 words or ' \
    'less, do not return a summary. When creating a summary, do not use figurative language or idioms, and ' \
    'resolve all co-references.> ' \
    '<Inputs: 1. Sentence text: {sent_text} ** ' + \
    f'2. Rhetorical devices: {rhetorical_devices_text}> ' \
    f'<Output: Return the results as a JSON object using the following structure: {sentence_result}>'

# Validating Wikipedia result
wikipedia_prompt = \
    'Task: You are ChatGPT, a large language model trained by OpenAI using the GPT-4 architecture, with expertise ' \
    'in research. Your objective is to determine if a noun described by the Input text is correctly categorized ' \
    'as a type of  "{text_type}".> ' \
    'Instructions: 1. Input Format: You will receive a description of a noun, followed by the string "**", ' \
    'which should be ignored. ' \
    '2. Text Analysis: Analyze the provided description to determine if the described entity qualifies as ' \
    'a type of "{text_type}".> ' \
    '<Input: {wiki_def} **> ' + \
    f'<Output: Return the results as a JSON object using the following structure: {consistency_result} Note ' + \
    'that "consistent" should be true if the noun is categorized correctly as a "{text_type}" and false otherwise.>'


# @retry(stop=stop_after_delay(20) | stop_after_attempt(2), wait=(wait_fixed(3) + wait_random(0, 2)))
def access_api(content: str) -> dict:
    """
    Surrounding the calls to the OpenAI API with retry logic.

    :param content: String holding the content of the completion request
    :return: The 'content' response from the API as a Python dictionary
    """
    try:
        response = client.chat.completions.create(
            model=model_engine,
            messages=[
                {"role": "user", "content": content}
            ],
            response_format={"type": "json_object"},
            temperature=0.05,
            top_p=0.1
        )
        if "finish_reason='stop'" not in str(response):
            logging.error(f'Non-stop finish response, {str(response)}, for content, {content}')
            return dict()
    except Exception as e:
        logging.error(f'OpenAI exception for content, {content}: {str(e)}')
        return dict()
    try:
        resp_dict = json.loads(response.choices[0].message.content.replace('\n', ' '))
    except Exception as e:
        logging.error(f'Invalid JSON content ({str(e)}): {response.choices[0].message.content}')
        return dict()
    return resp_dict
