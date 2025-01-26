# Event, condition and entity extensions for OpenAI classification tasks

# Base event and state classes
event_categories = [
    ':AchievementAndAccomplishment', ':AcquisitionPossessionAndTransfer', ':Affiliation', ':Agreement',
    ':AgricultureApicultureAndAquacultureEvent', ':AidAndAssistance', ':AppointmentAndNomination',  #7
    ':ArtAndEntertainmentEvent', ':AssessmentMeasurement',  ':Attempt', ':AttributeAndCharacteristic',
    ':Avoidance', ':Birth', ':BodilyAct', ':Causation', ':Cognition', ':Commemoration',  # 17
    ':CommunicationAndSpeechAct', ':Continuation',  ':CorruptionAndFraud', ':CourtOrderAndRuling',
    ':CrimeAndHostileConflict', ':DamageAndDifficulty', ':Death', ':DeceptionAndDishonesty', ':Decrease',
    ':DelayAndWait', ':DemonstrationStrikeAndRally', ':Diplomacy',  # 29
    ':DisagreementAndDispute', ':DiscriminationAndPrejudice', ':DistributionSupplyAndStorage',
    ':DivorceAndSeparation', ':EconomyAndFinanceRelated', ':EducationRelated', ':EmotionalResponse',   # 36
    ':End', ':EnvironmentalIssue', ':HealthAndDiseaseRelated', ':ImpactAndContact',
    ':InclusionAttachmentAndUnification', ':Increase', ':InternationalRelations', ':IssuingAndPublishing',   # 44
    ':LawEnforcement', ':LawRelated', ':LivingCondition', ':Marriage', ':Measurement', ':MeetingAndEncounter',
    ':Mistake', ':MovementTravelAndTransportation', ':OpenMindednessAndTolerance', ':PhysicalChange',    # 54
    ':PoliticsRelated', ':Polling', ':ProductionManufactureAndCreation', ':Punishment', ':ReadinessAndAbility',
    ':ReligionRelated', ':Relocation', ':RemovalAndRestriction', ':Residence', ':ReturnRecoveryAndRelease',   # 64
    ':RewardAndCompensation', ':RiskTaking', ':Scandal', ':ScienceAndTechnologyRelated', ':Search',
    ':SensoryPerception', ':Separation', ':SpaceEvent', ':StartAndBeginning', ':Substitution', ':Terrorism',
    ':UtilizationAndConsumption', ':Win', ':Loss', ':EventAndState']    # 79
event_category_texts = [
    'achieving or accomplishing something, but NOT winning or ending',  # 1
    'acquisition such as by purchase or sale, finding or stealing something, seizure, transfer of possession',
    'affiliation or close association of a person or thing with another entity, or membership of a person in a group',
    'agreement, consensus and compliance/accordance',
    'an agricultural, apiculture, viniculture and aquacultural act such as planting seeds, bottling wine, or '
    'harvesting honey',
    'aid, assistance and cooperative effort',
    'an act of proposing/appointing/nominating an Agent for a task or position',    # 7
    'performing, playing in or attending an artistic, entertainment or sporting event such as playing golf, '
    'singing in a musical performance, acting in a movie, etc.',
    'making an assessment, estimation, prioritization, evaluation, prediction, etc.',
    'attempting something',
    'description of a characteristic or attribute of a person, place, event, or thing such as its physical '
    'appearance, population, role, occupation, etc.',
    'avoidance, bans, boycotts, escape, prevention, concealment, etc.',
    'birth of a living being',
    'bodily act such as movement, eating, drinking, grooming, sleeping',
    'causation, cause and effect',
    'any type of thinking, focusing, reading, characterizing/comparing, deciding, planning, etc.',
    'any commemorative or celebratory activity such as celebrating "Independence Day" or a birthday',   # 17
    'a communication or speech act such as stating, explaining or detailing something, permitting/refusing, '
    'questioning, accusing, responding, etc.',
    'continuation',
    'any abuse of a position of power or trust, or other deceptions for personal gain including bribery, extortion, '
    'embezzlement and misuse of information',
    'a decision by a judicial body on a legal case or motion in a case, and/or a judicial order for an entity to '
    'do or not do something',
    'hostile or criminal act carried out by an person or group/organization, such as an armed attack, purposeful '
    'destruction such as looting, intimidation, betrayal, murder, abduction, etc.',
    'a condition/situation involving damage or dealing with ongoing problems being experienced by a person, '
    'organization, community, etc., EXCLUDING scandals, controversies and actions that led to the '
    'damaged/problematic state',
    'death of a living being, ONLY by natural causes',
    'an act of deception, of concealing or misrepresenting the truth, or of being fraudulent or dishonest,',
    'decrease, decline and reduction, EXCLUDING physical change',
    'delay, postponement or need to wait for something or someone',
    'a protest, demonstration, rally or strike',
    'an activity aimed at influencing the decisions and behaviors of foreign entities through dialogue, '
    'negotiation, and other peaceful measures, avoiding war or violence',  # 29
    'disagreement, disapproval, dispute, controversy or violation of agreement',
    'discrimination, prejudice, bias, or any act of inequity or unfairness',
    'any type of goods distribution, supply or storage',
    'divorce or separation of a couple in a relationship',
    'related to economic or financial matters and conditions such as being in recession, going bankrupt, etc.',
    'related to any educational events such as attending school, graduating, practicing or drilling, etc.',
    'any type of emotion or emotional response',   # 36
    'end or completion of something or the obtaining of a result/outcome',
    'any type of environmental or ecological issue or event such as a natural disaster, weather event, climate '
    'change, etc.',
    'related to health and disease events such as contracting a disease, addiction, physical injury, frailty, '
    'allergic reactions, vaccinations, sterility, etc., but NOT specific diseases, viruses or symptoms',
    'impact, contact and collision between two physical entities that are not environmental/weather/ecologically '
    'related',
    'inclusion, unification, alignment and attachment such as adding to a list and assembling something',
    'increase, escalation, expansion and surge, EXCLUDING physical change',
    'the condition/state of global affairs and the political, economic, social, and cultural interactions between '
    'countries, international organizations, NGOs and other global entities, dealing with how the entities '
    'cooperate, compete, and influence one another',
    'issuing and publishing information such as a publishing a newspaper, or releasing a document such as a '
    'press briefing',    # 44
    'a police/law enforcement activity such as arrest, incarceration, capture, detention, imprisonment',
    'any legal or judicial event such as testifying at a trial, reaching a verdict, selecting a jury, '
    'or appealing a judicial ruling, EXCLUDING the judicial decision, law enforcement actions and legal occupations '
    'such as judges',
    'any existing circumstance, situation or state affecting the life, welfare and relations of human beings '
    'in a location or community, such as access to food, water, housing and safe living conditions, EXCLUDING '
    'residence and time',
    'marriage',
    'an act or reporting of a measurement, count, scientific unit/value, statistic, etc.',
    'meeting and encounter such as a seminar or conference, spending time with or visiting someone',
    'error or mistake',
    'any type of movement, travel or transportation such as entering/leaving a port, loading a truck, and '
    'making incremental changes such as pouring liquid into a container, EXCLUDING relocation/the act of changing '
    'residences',
    'open-mindedness or tolerance',
    'physical change such as melting, bending and vaporization',    # 54
    'any political event or occurrence such as an election, referendum, coup, transfer of power, and political '
    'campaign',
    'an act of inquiry in order to obtain the opinion and thoughts of a set of people',
    'any type of production, manufacture and creation event such as designing, building or producing a product',
    'punishment',
    'readiness, preparation and ability',
    'any religious event or activity such as church services, observance of Ramadan, praying, meditation, etc.',
    'the act of changing residences whether voluntarily or not; non-voluntary relocations may mandated by evacuation/' 
    'government order, living conditions or by physical coercion, EXCLUDING describing a current residence',
    'removal or restriction of something, including blockage of movement, access, flow or personal activities',
    'living or residing in a location, EXCLUDING moving to a new location/relocating',
    'an act of restoring or releasing something or someone to their original owner/location/condition, or '
    'granting freedom or parole to someone or something',    # 64
    'reward, compensation, award and prize',
    'risk taking including gambling',
    'the outcome/consequence of a disgraceful or inappropriate action that damages reputation and public image',
    'any event or activity related to using or discovering new scientific/technical knowledge, and/or involving '
    'computers and scientific devices/instruments',
    'search, research and investigation',
    'any type of sensory perception such as pain, hunger, exhaustion and other sensations',
    'separation of two or more things by cutting, pulling apart, etc.',
    'any type of space event such as a meteor shower, sun spots, eclipse, or rocket or satellite launch',
    'start or beginning of something',
    'substitution, imitation or counterfeiting of something or someone',
    'use of violence or the threat of violence to achieve a political, religious, ideological, or social goal, and '
    'to instill fear',
    'utilization and consumption',
    'win and victory',
    'loss and defeat',
    'other']   # 79
base_event_category_texts = " ".join([f'{index}. {text}' for index, text in enumerate(event_category_texts, start=1)])

# 'related to labor such as employment/unemployment, the labor market, labor relations, retirement and unions',  # 74

noun_categories = [
    ':Animal', ':ArmedForce', ':Prison', ':BuildingAndDwelling', ':OrganizationalEntity', ':Ceremony',
    ':ComponentPart', ':Currency', ':DamageAndDifficulty', ':DiagnosticTest', ':DiseaseAndInfection',   # +11
    ':EthnicGroup', ':ExecutiveAndLegislativeGroup', ':FreedomAndSupportForHumanRights', ':GeopoliticalEntity',
    ':GovernmentalEntity', ':InformationSource', ':JudicialGroup', ':LawAndPolicy', ':LegalInstrument',
    ':LineOfBusiness', ':Location',  ':MachineAndTool', ':MedicalTest', ':MusicalInstrument',    # +25
    ':OrganizationalEntity', ':ParamilitaryAndRebelGroup', ':Person', ':Person, :Collection',
    ':PharmaceuticalAndMedicinal', ':Plant', ':PoliceForce', ':PoliticalGroup', ':Process', ':Product',   # +35
    ':ReligiousGroup', ':SubstanceAndRawMaterial', ':Symptom', ':TherapyAndMedicalCare', ':Vaccine', ':Vehicle',
    ':WeaponAndAmmunition', ':War', ':WasteAndResidue', ':Resource', 'owl:Thing']   # +46
noun_category_texts = [
    'animal',    # +1 added to last event class index
    'a government-funded military group/armed force',
    'prison, area or facility/building in which people are legally or illegally detained, EXCLUDING the act of '
    'detention/imprisonment',
    'building, dwelling or factory, EXCLUDING a prison',
    'business, commercial venture',
    'ceremony',
    'part of a living thing such as a the leg of a person or animal or leaf of a plant',
    'currency, money',
    'the condition of being damaged/suboptimal/in difficulty or having challenges, but NOT the act or cause of '
    'the damage/challenge',
    'a medical test that aids in determining disease and medical conditions, and in monitoring treatment (such as a '
    'laboratory, genetic or imaging test or biopsy)',
    'any disease, infection, virus, etc.',        # +11
    'related to ethnicity or an ethnic group',
    'a legislative body responsible for governance of a region and its people',
    'fundamental rights such as life, liberty, freedom of speech, etc.',
    'a country, state or province, or governing/administrative region, EXCLUDING governmental organizations, '
    'military/police groups and judicial groups',
    'a governmental organization or sub-organization EXCLUDING military/police groups, judicial groups and'
    'legislatures, and EXCLUDING a specific person, role/position and political event',
    'any entity that holds text, data/numbers, video, visual or audible content, etc. including documents, '
    'books, news articles, databases, spreadsheets, computer files or web pages',
    'any court/judicial body responsible for interpreting laws, and applying them to individual cases, EXCLUDING '
    'a specific person, role/position and judicial event',
    'a specific law, policy, legislation and legal decision, EXCLUDING legal occupation and judicial bodies',
    'occupation or line of business',
    'any formally/legally executed document that expresses an action, process, or contractual duty, obligation or '
    'right, such as birth/marriage certificates, licenses, wills, notarizations, etc.',
    'any location or element of the landscape (such as roads, bridges, dams), EXCLUDING buildings and facilities, '
    'prisons/detention areas, and geopolitical entities',
    'machine, tool or device',
    'any medical test that helps detect, diagnose, or monitor a medical condition',
    'musical instrument',     # +25
    'any non-governmental organization, sub-organization, business, club, social group, etc., EXCLUDING '
    'paramilitary/rebel and religious groups',
    'a non-governmental group of people who are armed and fighting a military force or to change a government',
    'person, EXCLUDING a reference to a body part',
    'group of people such as a family or people at a party or in the park that are NOT named governmental, military, '
    'business, social or other organizational entities',
    'pharmaceutical or medicinal entity, EXCLUDING vaccines',
    'plant',
    'police force',
    'set of persons with a common political ideology or a political party, EXCLUDING the activities, campaigns, '
    'etc. in which the persons or party are involved',
    'a natural or goal-directed process (including campaigns, plans and strategies) involving several related or '
    'interdependent events and conditions',
    'a named product or service which is bought, sold or traded, EXCLUDING locations where something is bought',  # +35
    'religious group',
    'any chemical substance, raw material or natural material',
    'a symptom of a disease or illness such as coughing or heartburn',
    'any medical therapy, treatment or care such as wound care, radiation/chemo-therapy, transfusion, '
    'palliative care, etc.',
    'vaccine',
    'vehicle',
    'weapon or ammunition',
    'war',
    'trash, residue, refuse, litter, junk, detritus, scrap material, dregs, sewage, etc., EXCLUDING activities '
    'related to waste management',
    'any physical, man-made thing or part thereof that can be used, harvested, mined or made/manufactured, ' 
    'EXCLUDING buildings and infrastructure, devices, musical or scientific instruments, pharmaceutical/medical '
    'items and vehicles',
    'other']   # +46

# Politics and International, additional classes
political_event_categories = [':Campaign', ':ConferenceAndConvention', ':PartisanPolarization', ':Treaty', ':Voting']
political_event_category_texts = [
    'an advertising or political campaign',
    'a large meeting, especially of members of a political party or who are involved in a profession',
    'a condition represented by conflict between two or more political parties where there is no middle ground, '
    'and situations are win/lose versus compromise; often, the "other" party is viewed as an enemy',
    'a formally negotiated and approved agreement between countries',
    'voting, balloting, registering or recording a vote,']
political_event_category_replacements = {
    'agreement, consensus and compliance/accordance':
        'agreement, consensus and compliance/accordance, EXCLUDING treaties'
}

# TODO: Crime and Law, Economy, Education, Entertainment, Environment and Ecology, Health,
#       Lifestyle, Science and Technology, Sports


