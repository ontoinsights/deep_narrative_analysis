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
    goal_dict = access_api(narr_prompt.replace("{narr_text}", narr_text))
    goals = goal_dict['goal_numbers']
    goal_texts = []
    for goal in goals:
        goal_texts.append(narrative_goals[goal - 1])
    assert 'analyze' in goal_texts and 'describe-current' in goal_texts
    assert 'conservative_interpretation' in goal_dict
    assert 'liberal_interpretation' in goal_dict
    assert 'neutral_interpretation' in goal_dict
    return
    # The returned results (in goal_dict) are:
    #  'goal_numbers': [1, 2],      # advocate and analyze
    #  'summary': "The author, a professional in U.S. peacemaking policy and conflict resolution, argues that
    #      peace between Israel and the Palestinians will not be possible as long as Hamas remains in control of
    #      Gaza. The author believes that Hamas's power and ability to threaten Israel must end, and that if
    #      Hamas persists as a military force, it will attack Israel again. The author also mentions the
    #      threat of Hezbollah and Iran's involvement.",
    #   'rhetorical_devices': [
    #      {'device_number': 5, 'evidence': 'The author refers to his professional experience in U.S. peacemaking
    #             policy and conflict resolution.'},     # ethos
    #      {'device_number': 16, 'evidence': "The author uses wording that appeals to fear, such as 'Israel's
    #             survival as a state is at stake' and 'Hamas will attack Israel again'."}],     # pathos
    #   'interpreted_text': [
    #      {'perspective': 'conservative', 'interpretation': "A conservative reader might agree with the
    #           author's argument that Hamas poses a significant threat to Israel and that peace will not be
    #           possible as long as Hamas remains in control of Gaza. They might also appreciate the author's
    #           emphasis on the need for strong action against Hamas."},
    #      {'perspective': 'liberal', 'interpretation': "A liberal reader might question the author's assertion
    #           that peace is impossible as long as Hamas is in control of Gaza, and might argue for a more
    #           nuanced approach to the conflict. They might also be concerned about the potential for
    #           escalation if Hamas's power is forcibly ended."},
    #      {'perspective': 'neutral', 'interpretation': "A neutral reader would note the author's argument
    #           and the reasons given for it, but might also seek out other perspectives to gain a more balanced
    #           understanding of the situation."}]}
