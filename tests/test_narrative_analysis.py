import pytest

from dna.app_functions import get_metadata_ttl, Metadata
from dna.create_narrative_turtle import create_graph
from dna.database import add_remove_data
from dna.nlp import parse_narrative
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


def test_narrative_dict_results():
    narr_dict = access_api(narrative_summary_prompt.replace("{narr_text}", narr_text))
    goals = narr_dict['goal_numbers']
    goal_texts = []
    for goal in goals:
        goal_texts.append(narrative_goals[goal - 1])
    assert 'analyze' in goal_texts    # Goal number 2
    assert 'summary' in narr_dict
    assert 'interpreted_text' in narr_dict
    assert narr_dict['interpreted_text'][0]['perspective'] in ('conservative', 'liberal', 'neutral')
    assert 'ranking_by_perspective' in narr_dict
    assert narr_dict['ranking_by_perspective'][0]['perspective'] in ('conservative', 'liberal', 'neutral')
    # The returned results (in narr_dict) are:
    #  {'goal_numbers': [2, 8],
    #   'summary': "The article is a personal narrative from a U.S. peacemaking policy expert who has shifted their
    #          stance on the Israel-Palestine conflict. The author argues that peace is unattainable as long as Hamas
    #          remains in control of Gaza, citing the group's persistent threat to Israel and its backing by Iran.
    #          The narrative emphasizes the existential threat perceived by Israelis and the need to dismantle Hamas
    #          to achieve lasting peace.",
    #   'interpreted_text': [
    #      {'perspective': 'conservative', 'interpretation': "Conservatives are likely to interpret the article
    #            positively, as it aligns with a strong stance against Hamas and supports Israel's right to defend
    #            itself. The emphasis on the existential threat to Israel and the need to dismantle Hamas resonates
    #            with conservative views on national security and counterterrorism."},
    #      {'perspective': 'liberal', 'interpretation': 'Liberals may have a mixed reaction to the article. While
    #            some may appreciate the call for peace and the acknowledgment of the complex dynamics in the region,
    #            others might be concerned about the implications of advocating for the dismantling of Hamas,
    #            potentially leading to further violence and humanitarian issues in Gaza.'},
    #      {'perspective': 'neutral', 'interpretation': 'Neutral readers are likely to see the article as a
    #            well-reasoned analysis from an experienced professional. They may appreciate the detailed explanation
    #            of the threats posed by Hamas and the broader geopolitical context, while also recognizing the
    #            challenges in achieving a peaceful resolution.'}],
    #   'ranking_by_perspective': [
    #      {'perspective': 'conservative', 'ranking': 5},
    #      {'perspective': 'liberal', 'ranking': 3},
    #      {'perspective': 'neutral', 'ranking': 4}],
    #   'sentiment': 'negative',
    #   'sentiment_explanation': 'The sentiment of the article is negative because it focuses on the ongoing
    #        conflict, the threats posed by Hamas, and the bleak prospects for peace as long as Hamas remains in
    #        power. The narrative underscores the dire situation and the perceived existential threat to Israel,
    #        contributing to an overall negative tone.'}


def test_narrative_turtle():
    narrative_results = parse_narrative(narr_text)
    graph_results = create_graph(narrative_results.sentence_classes, narrative_results.quotation_classes,
                                 narrative_results.partial_quotes, 2, 'foo')
    add_remove_data('add', ' '.join(graph_results.turtle), 'foo', '123')   # Add to dna db's foo_123 graph
    narr_meta = Metadata('I Might Have Once Favored a Cease-Fire With Hamas, but Not Now', '2023-10-27',
                         'New York Times', 'https://www.nytimes.com/2023/10/27/opinion/hamas-war-gaza-israel.html', 2)
    metadata_results = get_metadata_ttl('foo', '123', narr_text, narr_meta, 10, 2)
    ttl_str = str(metadata_results.turtle)
    assert ':narrative_goal "analyze' in ttl_str
    assert ':interpretation_conservative' in ttl_str
    assert ':ranking_conservative' in ttl_str
    assert ':sentiment "negative' in ttl_str
    assert ':sentiment_explanation' in ttl_str
    # Output Turtle:
    # :123 a :InformationGraph ; dc:created "2024-08-29T21:47:14"^^xsd:dateTime ;
    # :number_triples 161 ; :encodes :Narrative_123 .
    # :Narrative_123 a :Narrative ; dc:created "2023-10-27"^^xsd:dateTime ;
    # :number_sentences 10 ; :number_ingested 2 ; :source "New York Times" ;
    #     dc:title "I Might Have Once Favored a Cease-Fire With Hamas, but Not Now" ;
    #     :external_link "https://www.nytimes.com/2023/10/27/opinion/hamas-war-gaza-israel.html" .
    # :Narrative_123 :text "For 35 years, I’ve devoted my professional life to U.S. peacemaking policy and conflict
    #     resolution and planning — whether in the former Soviet Union, a reunified Germany or postwar Iraq. But
    #     nothing has preoccupied me like finding a peaceful and lasting solution between Israel and the Palestinians.
    #     In the past, I might have favored a cease-fire with Hamas during a conflict with Israel. But today it is
    #     clear to me that peace is not going to be possible now or in the future as long as Hamas remains intact
    #     and in control of Gaza. ..." .
    # :Narrative_123 :summary "The article is a personal narrative from a professional with 35 years of experience
    #     in U.S. peacemaking policy and conflict resolution. The author argues that a peaceful and lasting solution
    #     between Israel and the Palestinians is unattainable as long as Hamas remains in control of Gaza. The author
    #     believes that Hamas\'s power and ability to threaten Israel must end, as their continued existence poses a
    #     significant threat to Israel\'s survival. The article also touches on the broader geopolitical context,
    #     including the roles of Hezbollah and Iran." .
    # :Narrative_123 :narrative_goal "analyze" .
    # :Narrative_123 :narrative_goal "life-story" .
    # :Narrative_123 :interpretation_conservative "Conservatives are likely to interpret the article positively,
    #     as it aligns with their typically strong support for Israel and their stance against militant groups like
    #     Hamas. The emphasis on the necessity of dismantling Hamas to ensure Israel\'s security resonates with
    #     conservative views on national security and counterterrorism." .
    # :Narrative_123 :interpretation_liberal "Liberals might have a mixed interpretation of the article. While some
    #     may agree with the need for peace and security for Israel, others might be concerned about the implications
    #     for Palestinian civilians and the potential for increased violence. The focus on military solutions rather
    #     than diplomatic efforts could be seen as problematic by those who advocate for a more balanced approach to
    #     the Israeli-Palestinian conflict." .
    # :Narrative_123 :interpretation_neutral "Neutral readers are likely to see the article as a well-informed
    #     analysis from an experienced professional. They may appreciate the detailed context provided about the
    #     geopolitical situation and the challenges of achieving peace. However, they might also recognize the
    #     complexity of the issue and the potential biases in the author\'s perspective." .
    # :Narrative_123 :ranking_conservative 5 .
    # :Narrative_123 :ranking_liberal 3 .
    # :Narrative_123 :ranking_neutral 4 .
    # :Narrative_123 :sentiment "negative" .
    # :Narrative_123 :sentiment_explanation "The sentiment of the article is negative because it focuses on the ongoing
    #     conflict, the threats posed by Hamas, and the bleak prospects for peace as long as Hamas remains in power.
    #     The narrative underscores the dire situation and the perceived existential threat to Israel, contributing
    #     to an overall negative tone." .
