# Query for details using OpenAI
# Constants, prompts (titled xxx_prompt) and JSON formats (titled xxx_result)

import json
import logging
import os

from openai import OpenAI
# from tenacity import *

from dna.utilities_and_language_specific import add_to_dictionary_values

openai_api_key = os.environ.get('OPENAI_API_KEY')
model_engine = "gpt-4-turbo"
client = OpenAI()

any_boolean = 'true/false'
same_opposite = 'same/opposite'
interpretation_views = 'conservative, liberal or neutral'
semantic_role_text = 'agent, patient, theme, experiencer, instrument, cause, content, beneficiary, ' \
                     'location, time, goal, source, recipient, measure'
sentiment = 'positive, negative or neutral'
tense = 'past, present or future'

# JSON formats
consistency_result = '{"consistent": "bool"}'

coref_result = '{"updated_text": "string"}'

narrative_summary_result = '{"goal_numbers": ["int"], ' \
                           '"summary": "string", ' \
                           '"rhetorical_devices": [{"device_number": "int", "evidence": "string"}], ' \
                           '"interpreted_text": [{"perspective": "string", "interpretation": "string"}], ' \
                           '"ranking_by_perspective": [{"perspective": "string", "ranking": "int"}]}'

sentence_summary_result = '{"sentiment": "string", ' \
                          '"grade_level": "int", ' \
                          '"summary": "string"}'

sentence_devices_result = '{"rhetorical_devices": [{"device_number": "int", "evidence": "string"}]}'

verbs_and_associateds_result = '{"verbs": [' \
                               '"verb_text": "string", ' \
                               '"full_verb_phrase": "string", ' \
                               '"associateds": ["text": "string", "semantic_roles": ["string"]]]}'

semantics_result = '{"verbs": [{' \
                   '"verb_phrase_text": "string", ' \
                   '"tense": "string", ' \
                   '"topics": ["topic_number": "int", "topic_negated": "boolean"]]}'

noun_result = '{"noun_phrase": "string", ' \
               '"selected_text": "string", ' \
               '"singular": "boolean", ' \
               '"type": "int",' \
               '"negated": "boolean"}]}'

noun_category_result = '{"category_number": "int"}'

attribution_result = '{"speaker": "string"}'

# Ontology details / event and state classes
categories = [':AchievementAndAccomplishment', ':AcquisitionPossessionAndTransfer', ':Affiliation',
              ':AggressiveCriminalOrHostileAct', ':Agreement', ':AgricultureApicultureAndAquacultureEvent',
              ':ArrestAndImprisonment', ':ArtAndEntertainmentEvent', ':Attempt', ':Attendance', ':Avoidance',
              ':Birth', ':BodilyAct', ':Change', ':Cognition', ':Commemoration', ':CommunicationAndSpeechAct',
              ':Continuation', ':Death', ':DeceptionAndDishonesty', ':DelayAndWait', ':DemonstrationStrikeAndRally',
              ':DisagreementAndDispute', ':DiscriminationAndPrejudice', ':DistributionSupplyAndStorage',
              ':DivorceAndSeparation', ':EconomyAndFinanceRelated', ':EducationRelated', ':EmotionalResponse', ':End',
              ':EnvironmentAndCondition', ':EnvironmentalOrEcologicalEvent', ':HealthAndDiseaseRelated',
              ':ImpactAndContact', ':InclusionAttachmentAndUnification', ':IssuingAndPublishing',
              ':KnowledgeAndSkill', ':LegalEvent', ':Marriage', ':Measurement', ':MeetingAndEncounter', ':Mistake',
              ':MovementTravelAndTransportation', ':OpenMindednessAndTolerance', ':PoliticalEvent', ':Process',
              ':ProductionManufactureAndCreation', ':Punishment', ':ReadinessAndAbility', ':ReligionRelated',
              ':RemovalAndRestriction', ':ReturnRecoveryAndRelease', ':RewardAndCompensation', ':RiskTaking',
              ':Searching', ':SensoryPerception', ':Separation', ':SpaceEvent', ':StartAndBeginning', ':Substitution',
              ':TechnologyRelated', ':UtilizationAndConsumption', ':Win', ':Loss', ':Causation', ':EventAndState']
categories_text = 'The semantic topic categories are: ' \
    '1. achieving or accomplishing something' \
    '2. acquisition such as by purchase or sale, finding or stealing something, seizure, transfer of possession ' \
    '3. affiliation or close association of a person or thing with another entity, or membership of a ' \
    'person in a group ' \
    '4. hostile or criminal act such as an attack, purposeful destruction such as looting, ' \
    'intimidation, betrayal, murder, abduction, etc. ' \
    '5. agreement, consensus and compliance/accordance ' \
    '6. an agricultural, apiculture, viniculture and aquacultural act such as planting seeds, bottling wine, or' \
    'harvesting honey ' \
    '7. a police/law enforcement activity such as arrest, incarceration, capture, detention, imprisonment ' \
    '8. performing or playing in an art, entertainment or sporting event such as a playing in a football game, ' \
    'singing in a musical performance, acting in a movie, etc. ' \
    '9. attempting something ' \
    '10. attendance at an art, entertainment or sporting event ' \
    '11. avoidance such as bans, boycotts, escape, ignoring something/someone, prevention, concealment ' \
    '12. birth of a living being ' \
    '13. bodily act such as movement, eating, drinking, grooming, sleeping ' \
    '14. change such as increase, decrease or physical change such as melting, bending and vaporization ' \
    '15. any type of thinking, focusing, reading, characterizing/comparing, deciding, planning, etc. ' \
    '16. any commemorative or celebratory activity such as celebrating "Independence Day" or a birthday ' \
    '17. a communication or speech act such as stating a fact or position, permitting/refusing, questioning, ' \
    'responding, etc. ' \
    '18. continuation ' \
    '19. death of a living being (if murder or homicide, ALSO report topic category 4) ' \
    '20. an act of deception, of concealing or misrepresenting the truth, or of being fraudulent or dishonest ' \
    '21. delay, postponement or need to wait for something or someone' \
    '22. a protest, demonstration, rally or strike ' \
    '23. disagreement, disapproval, dispute, controversy or violation of agreement ' \
    '24. discrimination, prejudice, or any act that is intolerant, unjust, unfair or inappropriate, ' \
    'especially if motivated by ethnicity, age, disability, etc. ' \
    '25. any type of goods distribution, supply or storage ' \
    '26. divorce or separation of a couple in a relationship ' \
    '27. related to economic or financial matters and conditions such as being in recession, going bankrupt, etc. ' \
    '28. related to educational events such as attending school, graduating, practicing or drilling, etc. ' \
    '29. any type of emotion or emotional response ' \
    '30. end or completion of something ' \
    '31. description of a characteristic or an attribute of a person, place, event, or thing such as its physical ' \
    'appearance, population, role, occupation, etc. ' \
    '32. any type of environmental or ecological event such as a natural disaster, weather event, or other natural ' \
    'phenomenon or emergency ' \
    '33. related to health and disease such as contracting a disease, addiction, physical injury, frailty, ' \
    'allergic reactions, vaccinations, sterility ' \
    '34. impact, contact and collision ' \
    '35. inclusion, unification, alignment and attachment such as adding to a list and assembling something ' \
    '36. issuing and publishing information such as a publishing a newspaper, or releasing a document such as a ' \
    'press briefing ' \
    '37. having or using knowledge or skills which may be indicated by a job, hobby, schooling or practice ' \
    '38. any legal or judicial event such as testifying or arguing at a trial, reaching a verdict, selecting a ' \
    'jury, or handing down or appealing a judicial ruling ' \
    '39. marriage ' \
    '40. an act of measurement, counting, assessing or defining significance/importance ' \
    '41. meeting and encounter such as a seminar or conference, spending time with or visiting someone ' \
    '42. error or mistake ' \
    '43. any type of movement, travel or transportation such as entering/leaving a port, loading a truck, and ' \
    'making incremental changes such as pouring liquid into a container ' \
    '44. open-mindedness or tolerance ' \
    '45. any political event or occurrence such as an election, referendum, coup, transfer of power, and ' \
    'political campaign ' \
    '46. a natural or goal-directed process (including plans and strategies) involving several related or ' \
    'interdependent events and conditions, progressing along a timeline ' \
    '47. any type of production, manufacture and creation event such as designing, building or producing ' \
    'a product or creative work ' \
    '48. punishment ' \
    '49. readiness, preparation and ability ' \
    '50. any religious event or activity such as church services, observance of Ramadan, praying, meditation, etc. ' \
    '51. removal or restriction of something, including blockage of movement, access, flow or personal activities ' \
    '52. an act of restoring or releasing something or someone to their original owner/location/condition, or ' \
    'granting freedom or parole to someone or something ' \
    '53. reward, compensation, award and prize ' \
    '54. risk taking including gambling ' \
    '55. search, research and investigation ' \
    '56. any type of sensory perception such as pain, hunger, exhaustion and other sensations ' \
    '57. separation of two or more things by cutting, pulling apart, etc. ' \
    '58. any type of space event such as a meteor shower, sun spots, eclipse, or rocket or satellite launch ' \
    '59. start or beginning of something ' \
    '60. substitution, imitation or counterfeiting of something or someone ' \
    '61. any event or activity related to science and technology, or involving computers and ' \
    'scientific devices/instruments ' \
    '62. utilization and consumption ' \
    '63. win and victory ' \
    '64. loss and defeat ' \
    '65. causation, cause and effect ' \
    '66. other'

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

noun_categories = [':Animal', ':Ceremony', ':Change', ':CommunicationAndSpeechAct', ':ComponentPart',
                   ':Culture', ':ElectricityAndPower', ':End', ':EthnicGroup', ':FreedomAndSupportForHumanRights',
                   ':GovernmentalEntity', ':HealthAndDiseaseRelated', ':InformationSource', ':LaborRelated',
                   ':LawAndPolicy', ':LineOfBusiness', ':Location', ':MachineAndTool', ':Measurement',
                   ':MusicalInstrument', ':OrganizationalEntity', ':Person', ':Person, :Collection',
                   ':PharmaceuticalAndMedicinal', ':Plant', ':PoliticalGroup', ':Product', ':ReligiousGroup',
                   ':ScienceAndTechnology', ':StartAndBeginning', ':SubstanceAndRawMaterial', ':TroubleAndProblem',
                   ':WeaponAndAmmunition', ':War', ':WasteAndResidue', ':Resource', 'owl:Thing']
# TODO: Should all event categories be included?
noun_categories_text = 'The noun types are: ' \
    '1. animal ' \
    '2. ceremony ' \
    '3. change, whether positively or negatively ' \
    '4. verbal or written communication including speeches ' \
    '5. part of a living thing such as a the leg of a person or animal or leaf of a plant ' \
    '6. related to the customs, practices, values, principles and traditions of a particular society ' \
    '7. electricity and power-related ' \
    '8. finish or end ' \
    '9. related to ethnicity and ethnic groups ' \
    '10. fundamental rights such as life, liberty, freedom of speech, etc. ' \
    '11. a governmental body, organization, sub-organization, government-funded law-enforcement or military group, ' \
    'etc., but NOT a specific person or role/position ' \
    '12. disease, illness and their symptoms ' \
    '13. any entity that holds text, data/numbers, video, visual or audible content, etc. including documents, ' \
    'books, news articles, databases, spreadsheets, computer files or web pages ' \
    '14. related to labor such as employment/unemployment, the labor market, labor relations, retirement and unions ' \
    '(if a union, also report noun type 20)' \
    '15. a specific law, policy, legislation and legal decision (NOT including any legal occupations) ' \
    '16. occupation or business ' \
    '17. place or location including buildings, roads, bodies of water, etc. ' \
    '18. machine, tool or instrument ' \
    '19. quantity, assessment or measurement including demographics ' \
    '20. musical instrument ' \
    '21. any non-governmental organization, sub-organization, club, social group, etc. ' \
    '22. person ' \
    '23. group of people such as a family or people at a party or in the park that are NOT named governmental, ' \
    'business, social or organizational entities ' \
    '24. pharmaceutical or medicinal entity ' \
    '25. plant ' \
    '26. political group ' \
    '27. product or service which is bought, sold or traded ' \
    '28. related to religion, religious groups or religious practices ' \
    '29. any of the sciences such as biomedical science, computer science, mathematics, natural science, ' \
    'social science, standards, engineering, etc. ' \
    '30. beginning or start ' \
    '31. any chemical substance, raw material or natural material ' \
    '32. a situation which is undesirable and potentially harmful, a trouble or problem ' \
    '33. weapon or ammunition ' \
    '34. armed conflict, war, insurgency or armed clash ' \
    '35. waste or residue ' \
    '36. a non-living, man-made thing or part thereof' \
    '37. other'

rhetorical_devices = ['ad baculum', 'ad hominem', 'ad populum', 'allusion', 'antanagoge', 'aphorism',
                      'ethos', 'exceptionalism', 'expletive', 'hyperbole', 'imagery', 'invective', 'irony',
                      'juxtaposition', 'kairos', 'litote', 'loaded language', 'logos', 'metaphor',
                      'nostalgia', 'paralipsis', 'pathos', 'pleonasm', 'repetition', 'rhetorical question']
rhetorical_devices_text = 'The rhetorical device categories are: ' \
    '1. An appeal to force or a threat of force in order to compel a conclusion (ad baculum)' \
    '2. Use of wording that verbally demeans or attacks a person (ad hominem) ' \
    '3. Reference to general or popular knowledge such as "the most popular xyz" or "everyone says xyz" (ad populum) ' \
    '4. Reference to an historical/literary person, place or thing that has symbolic meaning such as ' \
    'saying that "sleeping late is my Achilles heel" where "Achilles heel" is the reference (allusion) ' \
    '5. Balancing negative wording with positive (antanagoge) ' \
    '6. Expressing a truth or moral principle such as "a stitch in time saves nine" (aphorism) ' \
    '7. Reference to authority figures and/or to people in occupations that should have knowledge ' \
    '(such as doctors or professors) in order to justify a statement (ethos) ' \
    '8. Use of language that indicates that a particular entity is somehow unique, extraordinary or ' \
    'exemplary (exceptionalism)' \
    '9. Use of emphasis words, such as "in fact", "of course", "clearly" or "certainly" (expletive) ' \
    '10. Use of exaggerated wording (hyperbole) ' \
    '11. Use of imagery and descriptive phrases that paint a vivid picture that emotionally engages a reader ' \
    '12. Use of ridicule, or angry or insulting language (invective) ' \
    '13. Use of irony or satire ' \
    '14. Placing contrasting ideas or situations side by side (juxtaposition)' \
    '15. Reference invoking feelings/remembrances of specific day, time, event or season such as ' \
    'discussing the Civil War in order to engage a reader (kairos) ' \
    '16. Use of double negative (litote) ' \
    '17. Use of "loaded language" such as words like "double-dealing", with strong connotations which invoke ' \
    'emotions and judgments' \
    '18. Use of logical reasoning terms, statistics and numbers (logos) ' \
    '19. Use of analogy, metaphor and simile to compare one thing with another of a different kind, or to ' \
    'compare an abstract thing with a concrete entity (such as peace being described as a dove) ' \
    '20. Use of wording that invokes nostalgia ' \
    '21. Indicating that little or nothing is said about a subject in order to bring attention to it, ' \
    'such as saying "I will not mention their many crimes" (paralipsis)' \
    '22. Wording that appeals to emotion such as fear or empathy (pathos) ' \
    '23. Use of superfluous or redundant language such as referring to a "burning fire" (pleonasm) ' \
    '24. Repeating words, phrases or sentences for emphasis ' \
    '25. Asking rhetorical questions '

chatgpt = 'Perform as ChatGPT, a large language model trained by OpenAI, based on the GPT-4 architecture. In ' \
          'addition, the user has provided information on how you should respond. The user details are: '

# Co-reference related prompting - Future
coref_prompt = \
    f'{chatgpt} You are a linguist and NLP expert, analyzing text. Here are 0-2 preceding ' + \
    'sentences (ending with the string "**" which should be ignored): {sentences} ** Here is the next sentence ' \
    '(also ending with the string "**" which is ignored): {sent_text} ** Resolve ALL personal and possessive ' \
    'pronouns found in the previous sentence. Update each of the personal pronouns with their specific noun ' + \
    f'references. Return the updated sentence using the JSON format, {coref_result}.'

# Narrative-level prompting
narrative_summary_prompt = \
    f'{chatgpt} You are a political observer analyzing news articles. Here is the text ' + \
    'of a narrative or article (ending with the string "**" which should be ignored): {narr_text} **' + \
    f'Here is a numbered list of the possible goals of the narrative. {narrative_goals_text} ' \
    f'Here is a numbered list of the possible rhetorical devices that may be used in the narrative. ' \
    f'{rhetorical_devices_text} ' + \
    'Indicate the numbers of the 2 most likely narrative goals. Indicate the numbers of the rhetorical' \
    'devices used, and explain why those devices were returned. Also, summarize the narrative, and explain ' + \
    f'how it would be interpreted from each of the following perspectives: {interpretation_views}. Rank the ' \
    f'text from 1-5 as to how positively it would be received for each perspective. The rank of 1 is very ' \
    f'negatively, and the rank of 5 is very positively. Return the response as a JSON object with keys and ' \
    f'values as defined by {narrative_summary_result}.'

noun_prompt = \
    f'{chatgpt} You are a linguist and NLP expert. Here is a sentence (ending with the string "**" which should ' + \
    'be ignored): {sent_text} ** Here is a noun or noun phrase from that sentence, "{noun_text}", and its ' \
    'semantic role, {semantic_role}. Select a subset of the noun phrase text that corresponds to the semantic role. ' \
    'If the noun phrase is a single word, set the selected text to that word. Otherwise, prefer the selection ' + \
    f'of text that is a full proper noun. Return all the components of a proper noun (e.g., the first, middle and ' \
    f'last names of a person), but please remove adjectives, possessives, honorifics, titles, etc. from it. ' \
    f'For the selected text, indicate whether it is singular ({any_boolean}), whether it is negated ({any_boolean}) ' \
    f'and its noun type. {noun_categories_text} Return the selected text, and the number of the noun type that ' \
    f'corresponds to its meaning and its semantic role. If no noun types are appropriate, return the number 37 ' \
    f'("other"). Return the response as a JSON object with keys and values as defined by {noun_result}.'

noun_category_prompt = \
    f'{chatgpt} You are a linguist and NLP expert. Here is a sentence (ending with the string "**" which should ' + \
    'be ignored): {sent_text} ** Here is a noun from that sentence, "{noun_text}". For the noun, ' + \
    f'return the number of the semantic topic category that best corresponds to its meaning. {categories_text} ' \
    f'If none of the categories are appropriate, return the number 66 ("other"). Return the response as a JSON ' \
    f'object with keys and values as defined by {noun_category_result}.'

# Sentence-level prompting
sentence_summary_prompt = \
    f'{chatgpt} You are a linguist and NLP expert, analyzing the text from narratives and news articles. ' + \
    'Here is the text of a sentence from an article that should be analyzed. The text ends with the string ' \
    '"**" which should be ignored. {sent_text} ** For the sentence, indicate its sentiment ' + \
    f'({sentiment}) and summarize it in a sentence of 10 words or less. Do not use personal or possessive pronouns ' \
    f'in the summary sentence, but references to nouns and proper nouns. Indicate the grade level that is ' \
    f'expected of a reader to understand the sentence semantics. Return the response as a JSON object ' \
    f'with keys and values as defined by {sentence_summary_result}.'

sentence_devices_prompt = \
    f'{chatgpt} You are a linguist and NLP expert, analyzing the text from narratives and news articles. ' \
    f'Here is a numbered list of the possible types of rhetorical devices that may be used in the text of ' \
    f'a sentence from the narrative or article. {rhetorical_devices_text} Here is the text of a specific sentence ' + \
    'to be analyzed. The text ends with the string "**" which should be ignored. {sent_text} ** ' + \
    f'Provide the numbers associated with any rhetorical devices found in the sentence and explain why they are ' \
    f'identified. Return the results as a JSON object with keys and values defined by {sentence_devices_result} ' \
    f'IF there are no rhetorical devices used in the text, return an empty array for the "rhetorical_devices" JSON key.'

verbs_and_associateds_prompt = \
    f'{chatgpt} You are a linguist and NLP expert. Here is a sentence (ending with the string "**" which should ' + \
    'be ignored): {sent_text} ** Here are the root and clausal verbs in the sentence: "{verb_texts}". For ' \
    'each verb, find it in the sentence and return its text, as well as the full verb phrase with modals, adverbial ' \
    'modifiers, negation, etc. Also return the full text of all associated subjects, objects, prepositional clauses, ' \
    'etc. If the verb or associated entities are considered idioms, return the complete idiom as the verb or ' \
    'associated clause. Indicate the semantic roles of each associated subject, object, etc. There may be more ' + \
    f'than one role. Only return these specific semantic roles: {semantic_role_text}. Make sure to consider whether ' \
    f'the sentence is in the active or passive voice when assigning the roles. Do not assign a role of "content" if ' \
    f'the associated subject, object, etc. does not include a verb. If there is no verb, try to assign a more ' \
    f'specific semantic role. Return the information as a JSON object with keys and values defined by ' \
    f'{verbs_and_associateds_result}.'

# TODO: Should more categories be reported? 2 are reported now
semantics_prompt = \
    f'{chatgpt} You are a linguist and NLP expert. Here is a numbered list of semantic topic categories ' \
    f'capturing the meanings of the phrases in a sentence. {categories_text} Here is a sentence (ending with ' + \
    'the string "**" which should be ignored): {sent_text} ** Here are specific root and clausal verb phrases ' \
    'from the sentence which should be evaluated: "{verb_phrases}". Indicate the tense of each verb phrase ' + \
    f'({tense}). Select up to two semantic topics that reflect the meaning of each verb phrase. If the ' \
    f'verb phrase contains an idiom, assign its topic based on the meaning of the idiom. Also indicate ' \
    f'whether the topic is negated ({any_boolean}) in the sentence. If a verb phrase is only based on the ' \
    f'root lemma "be" (such as "<noun> was/is/will be <something>"), then the semantic topic should be ' \
    f'reported using the number 31 (a description). If none of the topics are applicable, return the number ' \
    f'66 ("other"). Return the response as a JSON object with keys and values as defined by {semantics_result}.'

# Quotation prompt
attribution_prompt = \
    f'{chatgpt} You are a linguist and NLP expert, analyzing quotations from news articles. Here is the ' + \
    'text of a news article (ending with the string "**" which should be ignored): {narr_text} ** ' \
    'Here is a quotation contained in the article (ending with the string "**" which should be ignored): ' \
    '{quote_text} ** For the quotation, find it in the news article, and indicate the name of the person who ' \
    'spoke/communicated it. If the speaker is identified using a pronoun, analyze the text to dereference it. ' + \
    f'Return the response as a JSON object with keys and values as defined by {attribution_result}.'

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
    except Exception:
        logging.error(f'Invalid JSON content: {response.choices[0].message.content}')
        return dict()
    return resp_dict
