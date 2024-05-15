import pytest

from dna.app_functions import get_metadata_ttl
from dna.query_openai import access_api, narrative_goals, narrative_summary_prompt

# From NYT Editorial, https://www.nytimes.com/2023/10/27/opinion/hamas-war-gaza-israel.html
narr_text = \
    'For 35 years, I’ve devoted my professional life to U.S. peacemaking policy and conflict resolution and planning ' \
    '— whether in the former Soviet Union, a reunified Germany or postwar Iraq. But nothing has preoccupied me like ' \
    'finding a peaceful and lasting solution between Israel and the Palestinians. In the past, I might have favored ' \
    'a cease-fire with Hamas during a conflict with Israel. But today it is clear to me that peace is not going to ' \
    'be possible now or in the future as long as Hamas remains intact and in control of Gaza. Hamas’s power and ' \
    'ability to threaten Israel — and subject Gazan civilians to ever more rounds of violence — must end. After ' \
    'Oct. 7, there are many Israelis who believe their survival as a state is at stake. That may sound like an ' \
    'exaggeration, but to them, it’s not. If Hamas persists as a military force and is still running Gaza after ' \
    'this war is over, it will attack Israel again. And whether or not Hezbollah opens a true second front from ' \
    'Lebanon during this conflict, it, too, will attack Israel in the future. The aim of these groups, both of ' \
    'which are backed by Iran, is to make Israel unlivable and drive Israelis to leave: While Iran has denied ' \
    'involvement in the Hamas attack, Ali Khamenei, Iran’s supreme leader, has long talked about Israel not ' \
    'surviving for another 25 years, and his strategy has been to use these militant proxies to achieve that goal.'


def test_narrative_results():
    narr_dict = access_api(narrative_summary_prompt.replace("{narr_text}", narr_text))
    goals = narr_dict['goal_numbers']
    print(narr_dict)
    goal_texts = []
    for goal in goals:
        goal_texts.append(narrative_goals[goal - 1])
    assert 'advocate' in goal_texts    # Goal #1
    assert 'summary' in narr_dict
    assert 'rhetorical_devices' in narr_dict
    assert int(narr_dict['rhetorical_devices'][0]['device_number']) in (7, 22)
    assert 'interpreted_text' in narr_dict
    assert narr_dict['interpreted_text'][0]['perspective'] in ('conservative', 'liberal', 'neutral')
    assert 'ranking_by_perspective' in narr_dict
    assert narr_dict['ranking_by_perspective'][0]['perspective'] in ('conservative', 'liberal', 'neutral')
    # The returned results (in goal_dict) are:
    #  'goal_numbers': [1, 2],      # advocate/analyze
    #      Have also seen 1 and 6, advocate/establish authority
    #  'summary': "The narrative is from a U.S. peacemaking policy and conflict resolution professional who
    #      has worked on various international conflicts. The focus is on the Israeli-Palestinian conflict,
    #      specifically the role of Hamas in Gaza. The author argues that peace is unattainable as long as
    #      Hamas, which is backed by Iran, remains in power and poses a threat to Israel. The narrative
    #      suggests that for Israelis, the existence of their state is at risk, and that the ultimate goal
    #      of Hamas and Hezbollah is to make Israel unlivable.",
    #   'rhetorical_devices': [
    #      {'device_number': 7, 'evidence': 'The author establishes authority by discussing their 35 years
    #          of experience in U.S. peacemaking and conflict resolution.'},    # ethos
    #      {'device_number': 22, 'evidence': 'The narrative appeals to emotions by discussing the existential
    #          threat to Israel and the impact of ongoing conflict on civilians.'}]    # pathos
    #   'interpreted_text': [
    #      {'perspective': 'conservative', 'interpretation': "Conservatives might view the narrative favorably
    #          as it emphasizes security concerns and the need for decisive action against Hamas, aligning with
    #          a strong national defense ideology."},
    #      {'perspective': 'liberal', 'interpretation': "Liberals might be critical of the narrative for its hardline
    #          stance against Hamas without discussing potential diplomatic solutions or the humanitarian impact
    #          of military actions."},
    #      {'perspective': 'neutral', 'interpretation': "A neutral observer might see the narrative as a pragmatic
    #          examination of the challenges in achieving peace between Israel and the Palestinians, recognizing the
    #          complexities of the situation."}],
    #    'relevance_by_perspective': [
    #      {'perspective': 'conservative', 'ranking': 4},
    #      {'perspective': 'liberal', 'ranking': 2},
    #      {'perspective': 'neutral', 'ranking': 3}]
    # }


def test_narrative_turtle():
    success, ttl_str, created, number = get_metadata_ttl('foo', '123', narr_text, [], 10, 10)
    assert ':narrative_goal "advocate' in ttl_str
    assert ':rhetorical_device "ethos' in ttl_str
    assert ':rhetorical_device_ethos' in ttl_str    # Holding the evidence for assigning the 'ethos' device
    assert ':interpretation_conservative' in ttl_str
    assert ':ranking_conservative' in ttl_str
    # Output Turtle:
    # :Narrative_123 :summary "The narrative is from a U.S. peacemaking policy and conflict resolution professional who
    #     has worked on various international conflicts. The focus is on the Israeli-Palestinian conflict,
    #     specifically the role of Hamas in Gaza. The author argues that peace is unattainable as long as
    #     Hamas, which is backed by Iran, remains in power and poses a threat to Israel. The narrative
    #     suggests that for Israelis, the existence of their state is at risk, and that the ultimate goal
    #     of Hamas and Hezbollah is to make Israel unlivable." .
    # :Narrative_123 :narrative_goal "advocate" .
    # :Narrative_123 :narrative_goal "analyze" .
    # :Narrative_123 :rhetorical_device "ethos" .
    # :Narrative_123 :rhetorical_device_ethos "The author establishes authority by discussing their 35 years
    #     of experience in U.S. peacemaking and conflict resolution." .
    # :Narrative_123 :rhetorical_device "pathos" .
    # :Narrative_123 :rhetorical_device_pathos "The narrative appeals to emotions by discussing the existential
    #     threat to Israel and the impact of ongoing conflict on civilians." .
    # :Narrative_123 :interpretation_conservative "Conservatives might view the narrative favorably as it emphasizes
    #     security concerns and the need for decisive action against Hamas, aligning with a strong national
    #     defense ideology." .
    # :Narrative_123 :interpretation_liberal "Liberals might be critical of the narrative for its hardline stance
    #     against Hamas without discussing potential diplomatic solutions or the humanitarian impact of
    #     military actions." .
    # :Narrative_123 :interpretation_neutral "A neutral observer might see the narrative as a pragmatic examination
    #     of the challenges in achieving peace between Israel and the Palestinians, recognizing the complexities \
    #     of the situation." .
    # :Narrative_123 :ranking_conservative 4 .
    # :Narrative_123 :ranking_liberal 2 .
    # :Narrative_123 :ranking_neutral 3 .
