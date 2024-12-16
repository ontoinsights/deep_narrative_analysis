# Query for details using OpenAI
# Constants, prompts (titled xxx_prompt) and JSON formats (titled xxx_result)

import json
import logging
import os

from openai import OpenAI
from dna.prompting_ontology_details import base_event_category_texts
from dna.utilities_and_language_specific import modals
# from tenacity import *

openai_api_key = os.environ.get('OPENAI_API_KEY')
model_engine = "gpt-4o"
client = OpenAI()

any_boolean = 'true/false'
interpretation_views = 'conservative, liberal or neutral'
modal_text = '", "'.join(modals)
pronoun_text = 'I, we, they, them, he, she, it, myself, ourselves, themselves, herself, himself or itself'
semantic_role_text = 'affiliation, agent, patient, theme, content, experiencer, instrument, location, time, goal, ' \
                     'cause, source, state, subject, purpose, recipient, measure, or attribute'
sentiment = 'positive, negative or neutral'
tense = 'past, present or future'

# Ontology details / noun, event and state classes defined in query_ontology_extensions.py
narrative_actors = ['hero', 'mentor', 'villain', 'innocent', 'lover', 'victim', 'rebel', 'caregiver',
                    'everyman', 'outcast', 'supporter', 'trickster', 'creator', 'ruler']
narrative_actor_texts = \
    '1. Actor overcomes challenges/obstacles to achieve a goal ' \
    '2. Actor provides knowledge, guidance and insight, or is an expert ' \
    '3. Actor is cast as a villain, criminal or corrupt ' \
    '4. Actor is pure-hearted and embodies goodness, hope or naivety ' \
    '5. Actor is driven by passion, devotion or love ' \
    '6. Actor suffers due to injustice, disaster, crime, etc.' \
    '7. Actor challenges authority, norms, the status quo or expectations ' \
    '8. Actor is a caregiver, providing emotional or physical support to others ' \
    '9. Actor represents the average/ordinary person ' \
    '10. Actor is marginalized/misunderstood ' \
    '11. Actor is loyal and resourceful, and supports a person or cause ' \
    '12. Actor uses wit, cunning or subversive actions to disrupt/question norms or introduce chaos ' \
    '13. Actor innovates and shapes the future ' \
    '14. Actor is a leader, ruler or decision-maker'
# TODO: Investigate assigning actor types within articles/narratives

narrative_flows = ['narrative/episodic', 'chronological', 'comparative', 'thematic/multifaceted', 'analytical',
                   'argumentative', 'causal', 'fragmented', 'speculative/forward-looking', 'historical context',
                   'cyclical', 'spiral', 'summarized', 'inverted pyramid', 'question-answer']
narrative_flow_texts = \
    '1. Presents interconnected stories/episodes, building toward a central theme and/or its resolution ' \
    '2. Follows a linear sequence of events, emphasizing decisive outcomes ' \
    '3. Contrasts multiple perspectives, events, people or outcomes to highlight similarities and differences ' \
    '4. Explores different aspects of a broader central subject, rather than being organized according to a ' \
    'timeline ' \
    '5. Focuses on explaining how and why, often incorporating data, detailed context and expert opinions ' \
    '6. Builds a case step-by-step and presenting evidence, counterarguments and rebuttals in order to persuade a ' \
    'reader ' \
    '7. Highlights cause-effect relationships; can be sequential but focuses on mechanisms, using logic and evidence ' \
    '8. Presents events outside of chronological order, emphasizing significant moments and events, or describing ' \
    'a journey of discovery ' \
    '9. Opens with a question, hypothesis, set of events or problem, and discusses potential/actual solutions or ' \
    'future implications ' \
    '10. Links current events to past occurrences, providing context and perspective ' \
    '11. Ends the article by returning to the opening idea or quote ' \
    '12. Begins with a broad overview and then narrows down to specific details, returning to the main topic ' \
    'several times to deepen understanding ' \
    '13. Compresses details to high-level points, focusing on key takeaways without deep analysis ' \
    '14. Starts with most critical information and progressively provides less essential details ' \
    '15. Presents a series of questions followed by answers to address reader inquiries'

narrative_goals = ['advocate', 'analyze', 'describe-set', 'describe-single', 'entertain',
                   'establish-authority', 'inspire', 'investigate', 'relate-life-story']
narrative_goal_texts = \
    '1. Promote or advocate for a cause, person or thing ' \
    '2. Analyze an issue, event or trend in-depth, by breaking it down ' \
    '3. Describe/chronicle how a set of events, trends and conditions evolve over time ' \
    '4. Describe/focus on a single event, trend or condition ' \
    '5. Entertain using humor and engaging content ' \
    '6. Establish authority by citing facts, statistics and quotes from experts ' \
    '7. Inspire and motivate through uplifting stories, news, etc. ' \
    '8. Uncover truths or corruption through detailed research ' \
    '9. Relate a personal narrative or life story'

narrative_plotlines = ['conflict and resolution', 'rise and fall', 'overcoming the monster/heroic acts',
                       'rags to riches', 'scandal and accountability', 'quest', 'personal transformation',
                       'justice and revenge']
narrative_plotline_texts = \
    '1. Reporting on conflicts (political, social, legal or military) and how they unfold/are resolved ' \
    '2. Reporting on rise and fall (or fall and rise), focusing on ambition and consequences ' \
    '3. Focusing on good vs. evil and/or survival, courage and resilience ' \
    '4. Documenting a rise from obscurity or hardness to greatness, wealth or happiness ' \
    '5. Investigating or exposing misconduct, corruption or ethical breaches, and/or seeking truth and transparency ' \
    '6. Achieving significant goal(s) despite problems and obstacles along the way ' \
    '7. Undergoing personal transformation ' \
    '8. Seeking justice or vengeance for wrongs done to someone'

narrative_subjects = ['crime and law', 'economy and business', 'education', 'entertainment', 'environment and ecology',
                      'health', 'human interest', 'lifestyle', 'politics and international', 'science and technology',
                      'sports']
narrative_subject_texts = \
    '1. Dealing with crime and criminal activities, legal cases, the justice system, organized crime, cybercrime, ' \
    'police brutality, police reform, fraud, embezzlement, prisons, and the correctional system ' \
    '2. Dealing with financial markets, corporations and small businesses, earnings, mergers/acquisitions, ' \
    'trade, tariffs, jobs, economic trends, the stock market, employment/unemployment, consumer behavior, ' \
    'spending, taxation, real estate, cryptocurrency, and blockchain ' \
    '3. Dealing with education, schools, universities, learning, teaching and teachers, testing, and college ' \
    'admissions ' \
    '4. Dealing with movies, TV, music, celebrities, cultural events, awards, books, gaming and performing arts ' \
    '5. Dealing with weather, climate change, conservation, sustainability, deforestation, energy sources, ' \
    'pollution, wildlife protection, green technology, carbon emissions, waste management and environmental ' \
    'activism ' \
    '6. Dealing with medicines, pharmacology, diseases, symptoms, medical treatments, epidemics/pandemics, ' \
    'mental health, fitness, nutrition and diet, vaccines and public health ' \
    '7. Focusing on personal stories that inspire, amuse or emotionally connect ' \
    '8. Dealing with travel and travel destinations, food and drink, the fashion industry, personal style, ' \
    'home decor, interior design, hobbies, relationships and the family, aging, retirement and human interest ' \
    '9. Dealing with national and international politics - elections, campaigns, transfer of power, ' \
    'international conflict and war, diplomacy, terrorism, refugees and displaced persons, international aid and ' \
    'organizations (such as the UN and NATO), governance, political figures, partisanship, political polarization, ' \
    'polling, political appointments/nominations, and political activism ' \
    '10. Dealing with space exploration, scientific discoveries, biotechnology, genetics, scientific debates, ' \
    'artificial intelligence, machine learning, cybersecurity, hardware, software, the tech industry, social ' \
    'media, and quantum computing ' \
    '11. Dealing with sports leagues, tournaments, athletes, college sports, sports injuries, player transfers ' \
    'and trades, and sport fans'

rhetorical_devices = ['ad baculum', 'ad hominem', 'ad populum', 'allusion', 'exceptionalism', 'expletive',
                      'imagery', 'invective', 'loaded language', 'logos', 'paralipsis', 'pathos',
                      'rhetorical question or accusation']
rhetorical_device_texts = 'The rhetorical device categories are: ' \
    '1. An appeal to force or a threat of force in order to compel a conclusion (ad baculum)' \
    '2. Use of wording that verbally demeans or attacks a person (ad hominem) ' \
    '3. Reference to general or popular knowledge such as "the most popular xyz" or "everyone says xyz" (ad populum) ' \
    '4. Reference to an historical/literary person, place or thing that has symbolic meaning (allusion) ' \
    '5. Use of language that indicates that a particular entity is somehow unique, extraordinary or ' \
    'exemplary (exceptionalism)' \
    '6. Use of emphasis words, such as "in fact", "of course", "clearly" or "certainly" (expletive) ' \
    '7. Use of imagery and descriptive phrases that paint a vivid picture that emotionally engages a reader (imagery)' \
    '8. Use of ridicule, or angry or insulting language (invective) ' \
    '9. Use of "loaded language" such as words like "double-dealing", with strong connotations which invoke ' \
    'emotions and judgments' \
    '10. Use of statistics and numbers (logos) ' \
    '11. Indicating that little or nothing is said about a subject in order to bring attention to it, ' \
    'such as saying "I will not mention their many crimes" (paralipsis)' \
    '12. Wording that appeals to emotion such as fear or empathy (pathos)' \
    '13. Asking rhetorical questions or making an explicit or implicit accusation'

# More complete list of rhetorical devices
# rhetorical_devices = ['ad baculum', 'ad hominem', 'ad populum', 'allusion', 'antanagoge', 'aphorism',
#                      'ethos', 'exceptionalism', 'expletive', 'hyperbole', 'imagery', 'invective', 'irony',
#                      'juxtaposition', 'kairos', 'litote', 'loaded language', 'logos', 'metaphor',
#                      'nostalgia', 'paralipsis', 'pathos', 'pleonasm', 'repetition', 'rhetorical question']
# rhetorical_device_texts = 'The rhetorical device categories are: ' \
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

# JSON response formats
attribution_result = '{"speaker": "string"}'

chronology_result = '{"events_situations": ["string"]}'

consistency_result = '{"consistent": bool}'

coref_result = '{"updated_sentences": ["string"]}'

noun_categories_result = '{"noun_phrases": [{' \
                          '"text": "string", "clarifying_text": "string", ' \
                          '"singular": bool, ' \
                          '"specific_representation": "string", ' \
                          '"category_number": int, "same_or_opposite": "string", "correctness": int}]}'

noun_events_result = '{"category_number": int, ' \
                      '"category_same_or_opposite": "string", ' \
                      '"category_correctness": int}'

narrative_classification_result = '{"subject_areas": [int], ' \
                                  '"goal_numbers": [int], "information_flows": [int], "plotlines": [int], ' \
                                  '"topics": ["string"], ' \
                                  '"summary": "string", ' \
                                  '"reader_reactions": [{"perspective": "string", "reaction": "string"}], ' \
                                  '"sentiment": "string", "sentiment_explanation": "string"}'

sentence_result = '{"grade_level": int, ' \
                  '"rhetorical_devices": [{"device_number": int, "explanation": "string"}]}'

situation_result = '{"simpler_sentences": [{' \
                   '"text": "string", "future": bool, "modal": "string", ' \
                   '"semantics": [{ ' \
                   '"category_number": int, "same_or_opposite": "string", "correctness": int}], ' \
                   '"nouns": [{ ' \
                   '"noun_text": "string", "semantic_role": "string"}]}]}'

# Prompt details
chatgpt1 = \
    'Task: You are ChatGPT, a large language model trained by OpenAI using the GPT-4 architecture, with expertise ' \
    'in linguistics and natural language processing (NLP). Your objective is to'

chatgpt2 = \
    'Task: You are ChatGPT, a large language model trained by OpenAI using the GPT-4 architecture, specializing in ' \
    'event linguistics research. Your objective is to'

# Quotation attribution prompt
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

# Co-reference related prompting - Not currently used
# TODO: Remove?
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

# Noun details prompts
noun_categories_prompt = \
    f'<{chatgpt2} analyze a set of nouns.> ' + \
    '<Instructions: 1. Input Formats: a) You are provided with one or more noun phrases. Each phrase is followed ' \
    'by the string ** which should be ignored. b) A numbered list of semantic categories is also provided. ' \
    '2. Phrase Analysis: Return ALL phrases, maintaining the order of the phrases in the JSON response "noun_' \
    'phrases" array. For each phrase, return the following information: a) Indicate whether the phrase is singular ' \
    'or not. b) Determine if the phrase represents one of the following: "person", "geopolitical entity", "location" ' \
    '(other than a geopolitical entity), or "occupation", indicate this in the JSON response as the value ' \
    'for "specific_representation". c) Map the semantics of the phrase to one of the numbered ' \
    'categories provided in the inputs, following the instructions in "Phrase Semantic Mappings". d) If the phrase ' \
    'involves a possessive, clarifying adjective or preposition, return that text as the value for the JSON key, ' \
    '"clarifying_text". If there is no clarifying text, then return an empty string. ' \
    '3. Phrase Semantic Mappings: a) When choosing the mapping, examine all categories before selecting the most ' \
    'appropriate one. Review all possible categories before selecting the most relevant. {subject_area_text} ' \
    'b) Make sure to consider each category and what it EXCLUDES. c) Double check the mapping to validate that ' \
    'it is the most appropriate. d) When returning the event category, return its number from the categories list. ' \
    'e) Indicate whether the category matches the meaning of the phrase ("same") or is the "opposite". ' \
    'f) Assign a correctness score (0-100) to indicate confidence in the mapping, where 0 indicates low confidence. ' \
    'g) If the phrase is some kind of personal activity, such as exercising or washing, map it to ' \
    'the category, "bodily activity". h) If the phrase is an idiom, legal term, or legalese, make sure ' \
    'to use its idiomatic meaning in the mapping. i) Always map noun phrases referring to people to "person", ' \
    'regardless of their role. For example, a "musician" is mapped to the semantic of "person", not to ' \
    'an "art or entertainment event". j) If no appropriate category is available, assign {other_number} ("other").> ' \
    '<Inputs: 1. Short texts: {noun_phrases} ** 2. Semantic categories: {noun_texts}> ' + \
    f'<Output: Return the results as a JSON object using the following structure: {noun_categories_result}>'

noun_events_prompt = \
    '<Task: You are ChatGPT, a large language model trained by OpenAI using the GPT-4 architecture, specializing in ' \
    'political and historical events. Your objective is to map a specific event in history, referenced in a news ' \
    'article, to an event/state category.> ' + \
    '<Instructions: 1. Input Formats: a) You are given a sentence ending with the string "**" which should be ' \
    'ignored. b) A list of proper nouns, found in the sentence and referencing historical/political events, are ' \
    'also provided. The list of nouns also ends with the string "**" which is also ignored. c) A numbered list ' \
    'of event/state categories is also provided. ' \
    '2. Semantic Category Mapping: Map the event semantics to one of the categories provided in the inputs. ' \
    '3. Semantic Mapping Considerations: a) Make sure to examine ALL the possible categories before selecting ' \
    'the most relevant one. Review all possible categories before selecting the most relevant. ' \
    'b) Make sure to consider each category and what it EXCLUDES. c) Double check the mapping to validate that ' \
    'it is the most appropriate. d) When returning the event category, return its number from the categories list. ' \
    'e) Indicate if the semantic of the event category is the "same" as (or is the "opposite" of) the semantic of ' \
    'the event. f) Assign an estimate from 0-100 for the correctness of the mapping, where 0 indicates ' \
    'that it is incorrect. g) If no categories are appropriate, return the number 79 ("other").> ' \
    '<Inputs: 1. Sentence text: {sentence_text} ** 2. Event proper nouns: {noun_texts} ** ' + \
    f'3. Semantic categories: {base_event_category_texts}> ' \
    f'<Output: Return the results as a JSON object using the following structure: {noun_events_result}>'

# Narrative-level prompting
narrative_chronology_prompt = \
    f'<{chatgpt2} capture the situations discussed in a news article, blog, or personal narrative.> ' + \
    '<Instructions: 1. Input Format: You are provided with an article. ' \
    '2. Event/Situation Identification: Prepare a list of the events/situations from the article in the order ' \
    'in which they are discussed. Return the events/situations as complete sentences avoiding all use of ' \
    'personal pronouns.> ' \
    '<Inputs: 1. Narrative: {narr_text}> ' + \
    f'<Output: Return the results as a JSON object using the following structure: {chronology_result}>'

narrative_classification_prompt = \
    '<Task: You are ChatGPT, a large language model trained by OpenAI using the GPT-4 architecture, with expertise ' \
    'as a news analyst. Your objective is to categorize, describe and summarize a news article.> ' \
    '<Instructions: 1. Input Formats: a) You are given the text of an article, ending with the string "**" which ' \
    'is ignored. b) A numbered list of possible subject areas is also provided, also ending with the string "**" ' \
    'which is ignored. c) A numbered list of possible goals of the article is provided, ending with the string "**" ' \
    'which is ignored. d) A numbered list of article information "flows" describing how an article presents its ' \
    'information, ending with the string "**" which is ignored. e) A numbered list of archetypal story themes/' \
    'plotlines tied to human experiences and desires. ' \
    '2. Article Analysis: a) Indicate the number of the two most likely subject areas of the article. ' \
    'b) Indicate the numbers of the 2 most likely goals of the article. c) Indicate the numbers of the two most ' \
    'likely "flows" that the article uses. d) Indicate the numbers of up to 2 plotlines that can be observed ' \
    'in the article. e) Provide a list of the main topics discussed in the article. ' \
    'f) Summarize the article. g) Indicate the probable reaction of readers from each ' + \
    f'of the following perspectives: {interpretation_views}. h) Indicate the sentiment of the article ' \
    '("positive", "negative" or "neutral"), and explain why that sentiment was selected.> ' \
    '<Inputs: 1. Narrative: {narr_text} ** ' + \
    f'2. Subject areas: {narrative_subject_texts} ** 3. Goals: {narrative_goal_texts} ** ' \
    f'4. Information flows: {narrative_flow_texts} ** 5. Plotlines: {narrative_plotline_texts} > ' \
    f'<Output: Return the results as a JSON object using the following structure: {narrative_classification_result}>'

# Sentence-level prompting
sentence_prompt = \
    f'<Task: You are ChatGPT, a large language model trained by OpenAI using the GPT-4 architecture, with expertise ' \
    'in linguistics and natural language processing (NLP). Your objective is to analyze a sentence from a narrative ' \
    'or news article.> ' + \
    '<Instructions: 1. Input Formats: a) You are given the text of a sentence from an article, where ' \
    'the sentence ends with the string "**" which is ignored. b) A numbered list of rhetorical devices that ' \
    'may be used in the sentence, is also provided. ' \
    '2. Sentence Analysis: a) Indicate the grade level that is expected of a reader to understand the ' \
    'sentence semantics. b) Provide the numbers of the various rhetorical devices used in the sentence, and ' \
    'explain why they are identified. If there are no rhetorical devices used, return an empty array for ' \
    'the "rhetorical_devices" JSON key, specified in the Output. > ' \
    '<Inputs: 1. Sentence text: {sent_text} ** ' + \
    f'2. Rhetorical devices: {rhetorical_device_texts}> ' \
    f'<Output: Return the results as a JSON object using the following structure: {sentence_result}>'
# Sentence analysis - c) Create a summary of the sentence using 15 ' \
#     'words or less, ONLY if the input sentence has more than 10 words. If the input sentence is 10 words or ' \
#     'less, do not return a summary. When creating a summary, do not use figurative language or idioms, and ' \
#     'resolve all co-references.> ' \

# Situation prompt
# TODO: More consistency in the noun extraction and semantic roles is needed
situation_prompt = \
    f'<{chatgpt2} capture the semantics of a situation discussed in a news article, blog, or personal ' \
    'narrative.> ' + \
    '<Instructions: 1. Input Format: You are provided with the text (a complex sentence) that describes ' \
    'the situation. The sentence is followed by the string "**" which should be ignored. 2. A numbered list ' \
    'of event semantic categories are also provided. ' \
    '2. Situation Simplification: Break the complex sentence into simpler noun-verb or noun-verb-object sentences. ' \
    'Validate that all aspects of the sentence are captured in the set of simple sentences. Do NOT create a ' \
    'simpler sentence just to capture time-related information, but include the time in the appropriate previous ' \
    'sentence. Make sure to capture the semantics of infinitive verbs as a separate, simple sentence. ' \
    'For each of the simpler sentences: a) Do NOT use any pronouns in the simpler sentences. Resolve ' \
    'pronouns to their specific references, and return the resolved text. b) Indicate if the simpler sentence is ' + \
    f'future tense or is about an event in the future. c) List any modal verbs ("{modal_text}") that apply to the ' \
    f'simpler sentence. d) Classify the semantics of the sentence using the considerations in "Semantic ' \
    f'Considerations". e) Provide the text of nouns that have a semantic role of {semantic_role_text}. When ' \
    'providing the noun phrases and its semantic roles, follow the considerations in "Noun Text/Role ' \
    'Considerations". ' \
    '3. Semantic Considerations: a) Map each simpler sentence semantic to two of the numbered event/state ' \
    'categories provided in the input. Review all possible categories before selecting the two most relevant ones. ' \
    '{subject_area_text} b) Make sure to consider each category and what it EXCLUDES. c) If the semantic involves ' \
    'an idiom, legal term, or legalese, make sure to use its idiomatic meaning in the mapping. ' \
    'd) Indicate whether the selected event/state category matches the meaning of the situation ("same") or ' \
    'is the "opposite", accounting for negation in the sentence. ' \
    'e) Assign a correctness score (0-100) to each category mapping, where 0 indicates low ' \
    'confidence. f) For sentences with verbs based solely on the lemmas "be" or "become", assign category ' \
    '{description_number} ("description"). g) If no appropriate category is available, assign category ' \
    '{other_number} ("other"). ' \
    '4. Noun Text/Role Considerations: a) Make sure to consider whether the sentence is in the active or ' \
    'passive voice when assigning the semantic role. b) Do NOT return nouns that are attributive nouns or noun ' \
    'adjuncts. c) Do NOT return articles in the text. d) Modify the text that is returned if the noun is a person ' \
    'and includes their proper name. ONLY return the person’s first and/or last names and validate that there are ' \
    'no adjectives, honorifics, titles, etc. e) Make sure to distinguish the semantics of communication, sensory ' \
    'perception, emotion, attempt or indication of causation, from what is communicated, perceived, felt, attempted ' \
    'or caused. Do NOT return the semantic of what is communicated, perceived, felt, attempted or caused. The ' \
    'latter should be returned as a noun phrase with the "semantic role" of "theme". f) If the sentence describes ' \
    'a characteristic, attribute or role of an entity, such as a physical appearance, occupation, demographic, etc., ' \
    'return that characteristic/attribute/role with the semantic role of "theme" and return the described entity ' \
    'with the semantic role of "experiencer". g) Make sure to correctly define the semantic role when dealing with ' \
    'winning/losing. Specifically, if the sentence is concerned with a loss, the loser should have the semantic role ' \
    'of "agent", and the winner should have the role of "patient". If the sentence is concerned with a win, the ' \
    'winner has the role of "agent", and the loser has the role of "patient".> ' \
    '<Input: 1. Sentence: {sit_text} ** 2. Event Semantic Categories: {events_text} >' + \
    f'<Output: Return the results as a JSON object using the following structure: {situation_result}>'


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
