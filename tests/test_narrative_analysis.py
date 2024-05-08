import pytest
from dna.query_openai import access_api, narrative_goals, narr_prompt

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
    narr_dict = access_api(narr_prompt.replace("{narr_text}", narr_text))
    goals = narr_dict['goal_numbers']
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
    #      {'perspective': 'conservative', 'interpretation': "Conservatives might view the narrative as a
    #          validation of security concerns regarding Israel and the threat posed by Hamas and Hezbollah.
    #          They may agree with the author's assessment that dismantling Hamas is necessary for peace."},
    #      {'perspective': 'liberal', 'interpretation': "Liberals might be critical of the narrative's hardline
    #          stance against Hamas and may advocate for a more nuanced approach to resolving the conflict that
    #          includes addressing the humanitarian situation in Gaza."},
    #      {'perspective': 'neutral', 'interpretation': "A neutral observer might consider the narrative as one
    #          perspective on the complex Israeli-Palestinian conflict, recognizing the author's expertise
    #          while also understanding that the situation has multiple dimensions and viewpoints."}],
    #    'ranking_by_perspective': [
    #      {'perspective': 'conservative', 'ranking': 4},
    #      {'perspective': 'liberal', 'ranking': 2},
    #      {'perspective': 'neutral', 'ranking': 3}]
    # }
