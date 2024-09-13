# Query for details using OpenAI
# Constants, prompts (titled xxx_prompt) and JSON formats (titled xxx_result)

import json
import logging
import os

from openai import OpenAI
# from tenacity import *

openai_api_key = os.environ.get('OPENAI_API_KEY')
model_engine = "gpt-4o-2024-08-06"
client = OpenAI()

any_boolean = 'true/false'
interpretation_views = 'conservative, liberal or neutral'
pronoun_text = 'they, them, he, she, it, myself, ourselves, themselves, herself, himself and itself'
semantic_role_text = 'affiliation, agent, patient, theme, content, experiencer, instrument, location, time, goal, ' \
                     'cause, source, state, subject, recipient, measure, or attribute'
sentiment = 'positive, negative or neutral'
tense = 'past, present or future'

# JSON formats
attribution_result = '{"speaker": "string"}'

consistency_result = '{"consistent": "bool"}'

coref_result = '{"updated_sentences": ["string"]}'

events_result = '{"sentences": [{' \
                '"sentence_number": "int", ' \
                '"summary": "string", ' \
                '"verbs": [{"trigger_text": "string", ' \
                '"category_number": "int", "category_same_or_opposite": "string", "correctness": "int"}]}]}'

noun_categories_result = '{"sentence_nouns": [{' \
                          '"verb_text": "string", ' \
                          '"noun_information": [{' \
                          '"trigger_text": "string", "semantic_role": "string", ' \
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

chatgpt = 'Perform as ChatGPT, a large language model trained by OpenAI, based on the GPT-4 architecture. In ' \
          'addition, the user has provided information on how you should respond. The user details are: '

# Quotation prompt
attribution_prompt = \
    f'{chatgpt} You are a linguist and NLP expert, analyzing quotations from news articles. Here is the ' + \
    'text of a news article (ending with the string "**" which should be ignored): {narr_text} ** ' \
    'Here is a quotation contained in the article (ending with the string "**" which should be ignored): ' \
    '{quote_text} ** For the quotation, find it in the news article, and indicate the name of the person who ' \
    'spoke/communicated it. If the speaker is identified using a pronoun, analyze the text to dereference it. ' + \
    f'Return the response as a JSON object with keys and values as defined by {attribution_result}.'

# Co-reference related prompting
coref_prompt = \
    f'{chatgpt} You are a linguist and NLP expert, analyzing text. Here are sentences from an ' + \
    'article. The complete set of sentence texts end with the string "**", which should ignored. ' \
    '{sentences} ** Examine each sentence. If the sentence contains one or more of these pronouns, ' + \
    f'{pronoun_text}, update each pronoun to replace it with its specific noun reference. Double check to ' \
    f'make sure that ALL of the pronouns are updated. Return each updated sentence (or return the original ' \
    f'sentence if not updated) in the "updated_sentences" array in the JSON format, {coref_result}.'

# Event and noun details prompts
events_prompt = \
    f'{chatgpt} You are an event linguistics researcher interested in events and conditions reported in news ' + \
    'articles, blogs and personal narratives. Here are a numbered set of sentences from an article. The complete ' \
    'set of sentence texts end with the string "**", which should ignored. {numbered_sentences_texts} ** ' \
    'For each sentence, return the number associated with the sentence, the main verb, verbs in ' \
    'subordinate clauses, and a short summary of the sentence of 12 words or less. If ' \
    '"[Quotation##]" or "[Partial##]" occurs in the sentence, those strings represent quoted text which ' \
    'has been removed. Analyze the sentence assuming the "[Quotation##]" and "[Partial##]" strings ' \
    'do not affect any semantics. For each main or subordinate clause verb, return its ' \
    'specific trigger word(s) including any modals and negation. If any of the verbs are idioms, legal ' \
    'terms or legalese, return the complete idiom/legalese/legal terms as the trigger text. ' \
    'Make sure to expand any verb contractions. Map the verb semantics to one of the following event/state ' + \
    f'categories: {event_categories_text} When mapping to the category, make sure to examine the verb in the ' + \
    'context of the sentence and examine ALL the possible categories before selecting the ' \
    'most relevant one. When returning the event/state category, return its number from the list above.' \
    'Also, indicate if the semantic of the event/state category is the "same" as (or is the "opposite" of) the ' \
    'semantic of the full verb (always considering whether the verb is negated). Once complete, assign an estimate ' \
    'from 0-100 for the correctness of the mapping, where 0 indicates that it is incorrect. If no categories ' \
    'are appropriate, return the number 68 ("other"). If the verb is ONLY the lemma, "be" or "become", ' \
    'return its semantic as the number 32. ' + \
    f'Return the information as a JSON object with keys and values defined by {events_result}.'

noun_categories_prompt = \
    f'{chatgpt} You are an event linguistics researcher interested in the concepts related to verbs reported in ' + \
    'the sentences of a news article, blog or personal narrative. Here is a sentence (ending with ** which should ' \
    'be ignored): {sentence_text}. In parentheses at the end are the main verb and verbs in subordinate clauses ' \
    'from the sentence. For each verb recorded in the parentheses, return its full text and find it in the ' + \
    f'sentence. Determine the nouns associated with the verbs that have a semantic role of {semantic_role_text}. ' + \
    'When determining the semantic role, consider whether the sentence is in the active or passive voice. ' \
    'Return the trigger word(s) of the nouns, and their semantic roles. Do not return articles (such as "the") in ' \
    'the trigger words. If any of the nouns are idioms, legal terms or legalese, return the complete idiom/legalese/' \
    'legal term as the trigger text. Note that the trigger text for the name of a person should consist only of the ' \
    'first and last names (if a first name is available) or only the last name. Honorifics (such as "Mr.", "Mrs.", ' \
    '"Ms."), titles, designations and other qualifiers should NOT be returned. Map the semantics of the nouns to ' + \
    f'the categories described in the following numbered list: {noun_categories_text} ' + \
    'To perform the mapping, first determine whether the noun is a person, location, thing, event or ' \
    'condition/state. Then make sure to examine ALL the possible categories before selecting the most relevant one. ' \
    'Generally, the noun semantics should NOT map to the same semantics as the verb or the semantic role of the ' \
    'noun. For example, for a declaration of "x caused y", x should not be mapped to the ' \
    'category of "causation" (number 67). Assign a more relevant category. Also, always map a person in any role ' \
    'or relationship as number 82 (person). For example, a "musician" is NOT an art or entertainment event (number ' \
    '8), but is a person (number 82). When returning the category, return its number from the list. ' \
    'If no category is appropriate, return the number 96 ("other"). Indicate if the semantic ' \
    'of the category is the "same" as (or is the "opposite" of) the semantic of the noun. Also, assign an ' \
    'estimate from 0-100 for the correctness of the mapping, where 0 indicates that it is incorrect.' \
    'If "[Quotation##]" or "[Partial##]" occurs in the sentence, those strings represent quoted text which has ' \
    'been removed. If "[Quotation##]" or "[Partial##]" is returned as a related noun, return its text as the ' \
    'root word, and assume that it has the semantic role of "theme". ' + \
    f'Return the information as a JSON object with keys and values defined by {noun_categories_result}.'

# Process EVENT entity
noun_events_prompt = \
    f'{chatgpt} You are a linguist and NLP expert. Here is a sentence (ending with the string "**" which should be ' + \
    'ignored): {sent_text} ** Here are a proper noun found in the sentence, "{noun_texts}", which describes a ' \
    'specific event in history. Map the noun semantics to one of the following event/state categories. ' + \
    f'{event_categories_text} ' + \
    'When mapping to an event category, make sure to examine ALL the possible categories before selecting ' \
    'the most relevant one. When returning the event category, return its number from the list above. Also, ' \
    'indicate if the semantic of the event category is the "same" as (or is the "opposite" of) the semantic of the ' \
    'noun. Once complete, assign an estimate from 0-100 for the correctness of the mapping, where 0 indicates ' \
    'that it is incorrect. If no categories are appropriate, return the number 68 ("other"). ' + \
    f'Return the response as a JSON object with keys and values as defined by {noun_events_result}.'

# Narrative-level prompting
narrative_summary_prompt = \
    f'{chatgpt} You are a political observer analyzing news articles. Here is the text ' + \
    'of a narrative or article (ending with the string "**" which should be ignored): {narr_text} **' + \
    f'Here is a numbered list of the possible goals of the narrative. {narrative_goals_text} ' \
    f'Indicate the numbers of the 2 most likely narrative goals. Also, summarize the article, and explain ' + \
    f'how it would be interpreted from each of the following perspectives: {interpretation_views}. Rank the ' \
    f'text from 1-5 as to how positively it would be received by readers of each perspective. The rank of 1 is ' \
    f'very negatively, and the rank of 5 is very positively. Lastly, indicate the article sentiment ("positive", ' \
    f'"negative" or "neutral"), and explain why that sentiment was selected. Return the response as a JSON object ' \
    f'with keys and values as defined by {narrative_summary_result}.'

# Sentence-level prompting
sentence_prompt = \
    f'{chatgpt} You are a linguist and NLP expert, analyzing the text from narratives and news articles. ' + \
    'Here is the text of a sentence from an article. The text ends with the string "**" which should be ignored. ' \
    '{sent_text} ** Indicate the grade level that is expected of a reader to understand the sentence semantics. ' \
    'Also, here is a numbered list of the types of rhetorical devices that may be used in the sentence. ' + \
    f'{rhetorical_devices_text} Provide the numbers associated with the devices found in the sentence and ' \
    f'explain why they are identified. If there are no rhetorical devices used, return an empty array for ' \
    f'the "rhetorical_devices" JSON key. Return the response as a JSON object with ' \
    f'keys and values defined by {sentence_result}.'


# Validating Wikipedia result
wikipedia_prompt = \
    f'{chatgpt} You are a student researching a proper noun and are given its text and information ' + \
    'that the noun is a type of "{text_type}". You retrieved a possible definition for the ' \
    'noun from Wikipedia. That definition is given by the following text, ending with the string "**" ' \
    'which should be ignored. {wiki_def} **. Evaluate if the definition is ' \
    'consistent with the noun type, and return the response as a JSON object with keys and ' + \
    f'values as defined by {consistency_result}.'


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
