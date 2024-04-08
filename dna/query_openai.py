# Query for details using OpenAI

import json
import logging
import os

from openai import OpenAI
# from tenacity import *

from dna.utilities_and_language_specific import add_to_dictionary_values

openai_api_key = os.environ.get('OPENAI_API_KEY')
model_engine = "gpt-4-1106-preview"   # gpt-4 or gpt-4-1106-preview
client = OpenAI()

any_boolean = 'true/false'
same_opposite = 'same/opposite'
interpretation_views = 'conservative, liberal or neutral'
modal_text = '"can", "could", "have to", "may", "might", "must", "ought to", "shall", "should" and "would"'
person = 'using the numbers 1, 2, 3'
semantic_labels = '"agent", "dative", "experiencer", "instrument", "location", "measure", ' \
                  '"patient", "source" or "theme"'
sentiment = 'positive, negative or neutral'
tense = 'past, present, future'

# JSON formats
consistency_format = '{"consistent": "bool"}'

coref_format = '{"updated_text": "string"}'

name_check_probability = '{"probability": "int"}'

narr_format = '{"goal_numbers": ["int"], ' \
               '"summary": "string", ' \
               '"rhetorical_devices": [{"device_number": "int", "evidence": "string"}], ' \
               '"interpreted_text": [{"perspective": "string", "interpretation": "string"}], ' \
               '"ranking_by_perspective": [{"perspective": "string", "ranking": "int"}]}'

quote_format1 = '{"sentiment": "string", ' \
                '"grade_level": "int", ' \
                '"summary": "string"}'

sent_format1 = '{"person": "int", ' \
                '"sentiment": "string", ' \
                '"tense": "string", ' \
                '"modal_text": "string", ' \
                '"grade_level": "int", ' \
                '"summary": "string"}'

sent_format2 = '{"rhetorical_devices": [{"device_number": "int", "evidence": "string"}]}'

quote_format3 = '{"semantics": [{' \
                 '"trigger_text": "string", ' \
                 '"justification": "string", ' \
                 '"category_number": "int", ' \
                 '"same_or_opposite": "string"}'

sent_format3 = '{"semantics": [{' \
                '"trigger_text": "string", ' \
                '"justification": "string", ' \
                '"category_number": "int", ' \
                '"same_or_opposite": "string", ' \
                '"nouns": [{"semantic_role": "string", "text": "string", "singular": "boolean", ' \
                '"noun_type": "int", "semantic_category": "int"}]}]}'

speaker_format = '{"speaker": "string"}'

# Ontology details
categories = [':AchievementAndAccomplishment', ':AcquisitionPossessionAndTransfer', ':Affiliation',
              ':AggressiveCriminalOrHostileAct', ':Agreement', ':AgricultureApicultureAndAquacultureEvent',
              ':ArrestAndImprisonment', ':ArtAndEntertainmentEvent', ':Attempt', ':Attendance', ':Avoidance',
              ':Birth', ':BodilyAct', ':Change', ':Cognition', ':Commemoration', ':CommunicationAndSpeechAct',
              ':Continuation', ':Death', ':DeceptionAndDishonesty', ':DelayAndWait', ':DemonstrationStrikeAndRally',
              ':DisagreementAndDispute', ':DiscriminationAndPrejudice', ':DistributionAndSupply',
              ':DivorceAndSeparation', ':EconomyAndFinanceRelated', ':EducationRelated', ':EmotionalResponse',
              ':End', ':EnvironmentAndCondition', ':EnvironmentalOrEcologicalEvent', ':HealthAndDiseaseRelated',
              ':ImpactAndContact', ':InclusionAttachmentAndUnification', ':IssuingAndPublishing',
              ':KnowledgeAndSkill', ':LegalEvent', ':Marriage', ':Measurement', ':MeetingAndEncounter', ':Mistake',
              ':MovementTravelAndTransportation', ':PoliticalEvent', ':Process',
              ':ProductionManufactureAndCreation', ':Punishment', ':ReadinessAndAbility', ':ReligionRelated',
              ':RemovalAndRestriction', ':ReturnRecoveryAndRelease', ':RewardAndCompensation', ':RiskTaking',
              ':Searching', ':SensoryPerception', ':Separation', ':SpaceEvent', ':StartAndBeginning', ':Storage',
              ':Substitution', ':TechnologyRelated', ':UtilizationAndConsumption', ':War', ':WinAndLoss',
              ':Causation', ':EventAndState']

categories_text = 'The semantic topic categories are: ' \
    '1. achieving or accomplishing something' \
    '2. acquisition such as by purchase or sale, finding or stealing something, seizure or transfer of possession ' \
    '3. affiliation or close association of a person or thing with another entity, or membership of a ' \
    'person in a group ' \
    '4. aggressive, hostile or criminal act such as an attack, purposeful destruction such as looting, ' \
    'intimidation, betrayal, murder, abduction, etc. ' \
    '5. agreement such as consensus and signing a contract, approval of a course of action, or compliance/accordance ' \
    '6. an agricultural, apiculture, viniculture and aquacultural act such as planting seeds, bottling wine, or' \
    'harvesting honey ' \
    '7. arrest, incarceration, capture, detention, imprisonment or police/law enforcement activity ' \
    '8. performing or playing in an art, entertainment or sporting event such as a playing in a football game, ' \
    'singing in a musical performance, acting in a movie, etc. ' \
    '9. attempt ' \
    '10. attendance at an event AND the semantic category of the event should also be specified ' \
    '11. avoidance such as bans, boycotts, escape, ignoring something, prevention and concealment ' \
    '12. birth of a living being ' \
    '13. bodily act such as movement, eating, drinking, grooming and sleeping ' \
    '14. change such as increase, decrease or physical change such as melting, bending and vaporization ' \
    '15. any type of thinking, focusing, reading, assessing, characterizing, comparing, making a decision, ' \
    'planning, and remembering ' \
    '16. commemorative event such as celebrating "Independence Day" or "Juneteenth", or celebrating a birthday ' \
    '17. any type of communication and speech act such as asking or responding to a question, making a ' \
    'recommendation, denying something, granting or refusing permission, etc. ' \
    '18. continuation ' \
    '19. death of a living being (if murder or homicide, ALSO report semantic category 4) ' \
    '20. an act of deceiving, of concealing or misrepresenting the truth, or of being fraudulent or dishonest ' \
    '21. delay, postponement or need to wait for something or someone' \
    '22. a protest, demonstration, rally or strike ' \
    '23. disagreement, disapproval, dispute, controversy or violation of agreement ' \
    '24. discriminative or prejudicial act, or any act that is intolerant, unjust, unfair or inappropriate, ' \
    'especially when motivated by ethnicity, age, sexual orientation, disability, etc. ' \
    '25. distribution or supply of something ' \
    '26. divorce or separation of a couple in a relationship ' \
    '27. related to economic or financial matters and conditions such as being in recession, going bankrupt, etc. ' \
    '28. related to educational events such as attending school, graduating, practicing or drilling, etc. ' \
    '29. any type of emotion or emotional response ' \
    '30. end of something ' \
    '31. description of a characteristic or an attribute of a person, place, event, or thing such as its physical ' \
    'appearance, weight, population, role or occupation, etc. ' \
    '32. any type of environmental or ecological event such as a natural disaster, weather event, or other natural ' \
    'phenomenon or emergency ' \
    '33. related to health and disease such as contracting a disease, addiction, physical injury, frailty, ' \
    'allergic reactions, vaccinations and sterility ' \
    '34. impact, contact and collision ' \
    '35. inclusion, unification, alignment and attachment such as adding to a list and assembling something ' \
    '36. issuing and publishing information such as a publishing a newspaper, or releasing a document such as a ' \
    'press briefing ' \
    '37. having or using knowledge or skills which may be indicated by a job, hobby, schooling or practice ' \
    '38. any legal or judicial event such as testifying or arguing at a trial, reaching a verdict, selecting a ' \
    'jury, or handing down or appealing a judicial ruling ' \
    '39. marriage ' \
    '40. measurement, measuring and reported assessment, count, percentages, etc. ' \
    '41. meeting and encounter such as a seminar or conference, spending time with or visiting someone ' \
    '42. accident, error or mistake ' \
    '43. any type of movement, travel or transportation such as entering/leaving a port, loading a truck, and ' \
    'making incremental changes such as pouring liquid into a container ' \
    '44. any political event or occurrence such as an election, referendum, coup, transfer of power, and ' \
    'political campaign ' \
    '45. a natural or goal-directed process (including plans and strategies) which is a set of ' \
    'interrelated/interdependent events and conditions, ' \
    'that progress along a timeline such as a plan, script, the aging process or climate change' \
    '46. any type of production, manufacture and creation event such as designing, building or producing ' \
    'a product or creative work ' \
    '47. punishment ' \
    '48. readiness, preparation and ability ' \
    '49. related to religion and religious events and activities such as church services, observance of Ramadan ' \
    'or Lent, daily prayers or meditation, etc. ' \
    '50. removal or restriction of something, including blockage of movement, access, flow or personal activities ' \
    '51. an act of restoring or releasing something or someone to their original owner/location/condition, or ' \
    'granting freedom or parole to someone or something ' \
    '52. reward, compensation, award and prize ' \
    '53. risk taking including gambling ' \
    '54. search, research and investigation ' \
    '55. any type of sensory perception such as pain, hunger, exhaustion and other sensations ' \
    '56. separation (but NOT divorce) ' \
    '57. any type of space event such as a meteor shower, sun spots, eclipse, or rocket or satellite launch ' \
    '58. start or beginning of something ' \
    '59. any type of storage event such as stockpiling, hoarding or refrigerating something ' \
    '60. substitution, imitation or counterfeiting of something or someone ' \
    '61. related to science and technology, and activities involving computers and scientific devices/instruments ' \
    '62. utilization and consumption ' \
    '63. war or sustained armed conflict between two or more entities ' \
    '64. win or loss ' \
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

noun_categories = [':Animal', ':War', ':Ceremony', ':ComponentPart', ':ComponentPart',
                   ':Culture', ':ElectricityAndPower', ':EthnicGroup', ':FreedomAndSupportForHumanRights',
                   ':GovernmentalEntity', ':HealthAndDiseaseRelated', ':InformationSource', ':LaborRelated',
                   ':LawAndPolicy', ':LineOfBusiness', ':Location', ':MachineAndTool', ':Measurement',
                   ':MusicalInstrument', ':OrganizationalEntity', ':Person', ':Person, :Collection',
                   ':PharmaceuticalAndMedicinal', ':Plant', ':PoliticalGroup', ':Product',
                   ':ReligiousGroup', ':ScienceAndTechnology', ':SubstanceAndRawMaterial', ':WeaponAndAmmunition',
                   ':WasteAndResidue', 'owl:Thing']

noun_categories_text = 'The noun types are: ' \
    '1. animal ' \
    '2. armed conflict, war, insurgency or armed clash ' \
    '3. ceremony ' \
    '4. part of a living thing such as a the leg of a person or animal or leaf of a plant ' \
    '5. part of a non-living thing such as a wheel on a car or valve in an engine ' \
    '6. related to the customs, practices, traditions and behaviors of a particular society ' \
    '7. electricity and power-related ' \
    '8. related to ethnicity and ethnic groups ' \
    '9. fundamental rights such as life, liberty, freedom of speech, etc. ' \
    '10. government or government-funded entity ' \
    '11. disease, illness and their symptoms ' \
    '12. any entity that holds text, data/numbers, video, visual or audible content, etc. including documents, ' \
    'books, news articles, databases, spreadsheets, computer files or web pages ' \
    '13. related to labor such as employment/unemployment, the labor market, labor relations, retirement and unions ' \
    '(if a union, also report noun type 20)' \
    '14. a specific law, policy, legislation and legal decision (NOT including any legal occupations) ' \
    '15. occupation or business ' \
    '16. place or location including buildings, roads, bodies of water, etc. ' \
    '17. machine, tool or instrument ' \
    '18. quantity, assessment or measurement including demographics ' \
    '19. musical instrument ' \
    '20. organization, sub-organization, club, social group, etc. ' \
    '21. person ' \
    '22. group of people such as a family or people at a party or in the park that are NOT named governmental, ' \
    'business, social or organizational entities ' \
    '23. pharmaceutical or medicinal entity ' \
    '24. plant ' \
    '25. political group ' \
    '26. product or service which is bought, sold or traded ' \
    '27. related to religion, religious groups or religious practices ' \
    '28. any of the sciences such as biomedical science, computer science, mathematics, natural science, ' \
    'social science, standards, engineering, etc. ' \
    '29. any chemical substance, raw material or natural material ' \
    '30. weapon or ammunition ' \
    '31. waste or residue ' \
    '32. other'

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

# Co-reference related prompting - Future
coref_prompt = 'You are a linguist and NLP expert, analyzing text. Here are a series of zero to three preceding ' \
    'sentences (ending with the string "**" which should be ignored): {sentences} ** Here is the next sentence ' \
    '(also ending with the string "**" which is ignored): {sent_text} ** Resolve ALL personal pronouns found in ' \
    'the "next sentence". Update each of the personal pronouns with their specific noun references. Return the ' + \
    f'updated sentence using the JSON format, {coref_format}.'

# Validation prompting
name_check_prompt = 'You are a student researching whether two individuals described in text could be the same ' \
    'entities. The two texts that you are asked about are: 1. {noun1_text} and 2. {noun2_text}. Estimate the ' \
    'probability (an integer from 0-100) that the entities could be the same by removing honorifics from the first ' \
    'name, and checking plurality of the names. Return the response as a JSON object with keys and values ' + \
    f'as defined by {name_check_probability}. '

# Narrative-level prompting
narr_prompt = f'You are a political observer analyzing news articles. ' \
    'Here is the text of a narrative or article (ending with the string "**" which should be ignored): ' \
    '{narr_text} **' + \
    f'Here is a numbered list of the possible goals of the narrative. {narrative_goals_text} ' \
    f'Here is a numbered list of the possible rhetorical devices that may be used in the narrative. ' \
    f'{rhetorical_devices_text} ' + \
    'Indicate the numbers of the 2 most likely narrative goals. Indicate the numbers of the rhetorical' \
    'devices used, and explain why those devices were returned. Also, summarize the narrative, and explain ' + \
    f'how it would be interpreted from each of the following perspectives: {interpretation_views}. Rank the ' \
    f'text from 1-5 for each perspective. Return the response as a JSON object with keys and values as ' \
    f'defined by {narr_format}.'

# Sentence-level prompting
quote_prompt1 = \
    'You are a linguist and NLP expert, analyzing quotations from news articles. ' \
    'Here is the text of a quotation from an article (ending with the string "**" which should be ignored): ' \
    '{quote_text} ** ' + \
    f'For the text, indicate its sentiment ({sentiment}) and create a summary in 8 words or less. ' \
    f'Indicate the grade level that is expected of a reader to understand its semantics. ' + \
    f'Return the response as a JSON object with keys and values as defined by {quote_format1}.'

sent_prompt1 = \
    'You are a linguist and NLP expert, analyzing the text from narratives and news articles. ' \
    'Here is the text of a sentence from an article that should be analyzed. The text ends with the string ' \
    '"**" which should be ignored. {sent_text} ** ' + \
    f'For the sentence, indicate if it is in the first, second or third person ({person}), its sentiment ' \
    f'({sentiment}), and its tense ({tense}). Create a summary of the sentence in 8 words or less. Indicate' \
    f'the grade level that is expected of a reader to understand the sentence semantics. Lastly, consider ' \
    f'the modal auxiliary verbs: {modal_text}. If one of these modal verbs is used in the sentence, return its ' \
    f'text. If one of the listed modal verbs is not found, return the string, "none". ' \
    f'Return the response as a JSON object with keys and values as defined by {sent_format1}.'

quote_prompt2 = \
    'You are a linguist and NLP expert, analyzing quotations from news articles. ' \
    'Here is a numbered list of the possible types of rhetorical devices that may be used in a quotation. ' + \
    f'{rhetorical_devices_text} ' + \
    'Here is the text of a quotation from an article (ending with the string "**" which should be ignored): ' \
    '{sent_text} ** ' + \
    f'Provide the numbers associated with any rhetorical devices found in the quotation and explain why they are' \
    f'identified. Return the results as a JSON object with keys and values defined by {sent_format2} IF there are ' \
    f'no rhetorical devices used in the text, return an empty array for the "rhetorical_devices" JSON key.'

sent_prompt2 = 'You are a linguist and NLP expert, analyzing the text from narratives and news articles. ' \
    'Here is a numbered list of the possible types of rhetorical devices that may be used in the text of ' + \
    f'a sentence from the narrative or article. {rhetorical_devices_text} ' + \
    'Here is the text of a specific sentence to be analyzed. The text ends with the string "**" which should be ' \
    'ignored. {sent_text} ** ' + \
    f'Provide the numbers associated with any rhetorical devices found in the sentence and explain why they are ' \
    f'identified. Return the results as a JSON object with keys and values defined by {sent_format2} IF there are ' \
    f'no rhetorical devices used in the text, return an empty array for the "rhetorical_devices" JSON key.'

statement_of_the_form = 'If the analyzed text is a statement of the form, "<noun> was/is/will be <something>", then ' \
    'the verb should be reported using the category number 31 (a description).'

# TODO: Should more categories be reported? 2 are reported now (Also applies to sent_prompt3)
quote_prompt3 = 'You are a linguist and NLP expert, analyzing quotations from news articles. Here ' \
    'is a numbered list of categories of the possible semantic topics that may be discussed in a quotation. ' + \
    f'{categories_text} Here is the text of a specific quotation from an article (ending with the string "**" ' + \
    'which should be ignored): {sent_text} ** For the quotation, indicate the numbers of at most ' + \
    f'three semantic topics found in the quotation, the specific words that triggered the categorization, and the ' \
    f'justification for the selection. {statement_of_the_form} Only return three topics if they are significant to ' \
    f'the semantics of the quote. If none of the semantic categories apply, return the number 66 ("other"). ' \
    f'If the quotation includes a negation, compare the trigger words to the semantic topic and indicate ' \
    f'if their meanings are the same or opposite ({same_opposite}). Return the response as a JSON object with ' \
    f'keys and values as defined by {quote_format3}.'

sent_prompt3 = 'You are a linguist and NLP expert, analyzing the text of narratives and news articles. ' \
    'Here is a numbered list of categories of the possible semantic topics that may be discussed in the text. ' + \
    f'{categories_text} Here is the text of a sentence from a narrative or article to be analyzed. The text ends ' + \
    'with the string "**" which should be ignored. {sent_text} ** For the sentence, indicate the numbers of at ' + \
    f'most three semantic topics found in the text, the specific words that triggered the categorization, and the ' \
    f'justification for the selection. {statement_of_the_form} Only return three topics if they are significant to ' \
    f'the semantics of the sentence. If none of the semantic categories apply, return the number 66 ("other"). ' \
    f'If the sentence includes a negation, compare the trigger words to the semantic topic and indicate if ' \
    f'their meanings are the same or opposite ({same_opposite}). For each topic, determine the nouns that ' \
    f'are associated with it via one of these semantic role labels: {semantic_labels}. For an associated ' \
    f'noun, return its role label and text string, whether it is singular ({any_boolean}), and its noun type. ' \
    f'{noun_categories_text} Return the number of the noun type that best corresponds to the meaning of ' \
    f'the noun. If the type is number 32 ("other"), attempt to match the meaning to a semantic category. If the ' \
    f'noun type number is not 32, return 0 for the semantic category. Return the response as a JSON object with ' \
    f'keys and values as defined by {sent_format3}.'

speaker_prompt = 'You are a linguist and NLP expert, analyzing quotations from news articles. ' \
    'Here is the text of a news article (ending with the string "**" which should be ignored): {narr_text} ** ' \
    'Here is a quotation contained in the article (ending with the string "**" which should be ignored): ' \
    '{quote_text} ** For the quotation, find it in the news article, and indicate the name of the person who ' \
    'spoke/communicated it. If the speaker is identified using a pronoun, analyze the text to dereference it. ' + \
    f'Return the response as a JSON object with keys and values as defined by {speaker_format}.'

wikipedia_prompt = 'You are a student researching a proper noun and are given its text and information ' \
    'that the noun is a type of "{text_type}". You retrieved a possible definition for the ' \
    'noun from Wikipedia. That definition is given by the following text, ending with the string "**" ' \
    'which should be ignored. {wiki_def} **. Evaluate if the definition is ' \
    'consistent with the noun type, and return the response as a JSON object with keys and ' + \
    f'values as defined by {consistency_format}.'


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
            temperature=0.2,
            top_p=0.15
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
