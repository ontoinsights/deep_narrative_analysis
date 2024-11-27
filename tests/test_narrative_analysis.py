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
    assert 1 in narr_dict['goal_numbers']
    assert 'topic' in narr_dict
    assert 'summary' in narr_dict
    assert 'reader_reactions' in narr_dict
    assert narr_dict['reader_reactions'][0]['perspective'] in ('conservative', 'liberal', 'neutral')
    assert 'validity_views' in narr_dict
    assert narr_dict['validity_views'][0]['perspective'] in ('conservative', 'liberal', 'neutral')
    assert 'sentiment' in narr_dict
    # The returned results (in narr_dict) are:
    #  {'goal_numbers': ['1', '2'],
    #  'topics': ['U.S. peacemaking policy', 'Israel-Palestine conflict', 'Hamas', "Iran's influence",
    #      'Middle East geopolitics'],
    #  'summary': "The article is a personal narrative from a professional with 35 years of experience in U.S.
    #      peacemaking policy, focusing on the Israel-Palestine conflict. The author argues that peace between Israel
    #      and the Palestinians is unattainable as long as Hamas remains in control of Gaza. The piece highlights the
    #      threat posed by Hamas and Hezbollah, both backed by Iran, to Israel's existence. The author suggests that
    #      these groups aim to make Israel unlivable, aligning with Iran's long-term strategy against Israel.",
    #  'reader_reactions': [
    #      {'perspective': 'conservative', 'reaction': 'Supportive, as the article aligns with a strong
    #          stance against Hamas and highlights security concerns for Israel.'},
    #      {'perspective': 'liberal', 'reaction': 'Mixed, as some may agree with the security concerns but also
    #          worry about the humanitarian impact on Gazan civilians.'},
    #      {'perspective': 'neutral', 'reaction': 'Informative, providing a perspective on the complexities of the
    #          Israel-Palestine conflict and regional geopolitics.'}],
    #  'validity_views': [
    #      {'perspective': 'conservative', 'validity': 5},
    #      {'perspective': 'liberal', 'validity': 3},
    #      {'perspective': 'neutral', 'validity': 4}],
    #  'sentiment': 'negative',
    #  'sentiment_explanation': "The sentiment is negative due to the focus on the ongoing conflict, the threat to
    #      Israel's existence, and the bleak outlook for peace as long as Hamas remains in power."}


def test_narrative_turtle():
    sentence_classes, quotation_classes = parse_narrative(narr_text)
    graph_results = create_graph(sentence_classes, quotation_classes, 5, 'foo')
    add_remove_data('add', ' '.join(graph_results.turtle), 'foo', '123')   # Add to dna db's foo_123 graph
    narr_meta = Metadata('I Might Have Once Favored a Cease-Fire With Hamas, but Not Now', '2023-10-27',
                         'New York Times', 'https://www.nytimes.com/2023/10/27/opinion/hamas-war-gaza-israel.html', 2)
    metadata_results = get_metadata_ttl('foo', '123', narr_text, narr_meta, 10, 2)
    ttl_str = str(metadata_results.turtle)
    assert ':text ' in ttl_str
    assert ':topic ' in ttl_str and ':summary ' in ttl_str
    assert ':narrative_goal "analyze' in ttl_str
    assert ':interpretation_conservative' in ttl_str
    assert ':ranking_conservative' in ttl_str
    assert ':sentiment "negative' in ttl_str
    assert ':sentiment_explanation' in ttl_str
    # Output Turtle:
    # :123 a :InformationGraph ; dc:created "2024-11-13T12:07:27"^^xsd:dateTime ;
    # :number_triples 218 ; :encodes :Narrative_123 .
    # :Narrative_123 a :Narrative ; dc:created "2023-10-27"^^xsd:dateTime ;
    # :number_sentences 10 ; :number_ingested 2 ; :source "New York Times" ;
    #     dc:title "I Might Have Once Favored a Cease-Fire With Hamas, but Not Now" ;
    #     :external_link "https://www.nytimes.com/2023/10/27/opinion/hamas-war-gaza-israel.html" .
    # :Narrative_123 :text "For 35 years, I’ve devoted my professional life to U.S. peacemaking policy ..." .
    # :Narrative_123 :narrative_goal "advocate" .
    # :Narrative_123 :narrative_goal "analyze" .
    # :Narrative_123 :topic "U.S. peacemaking policy" .
    # :Narrative_123 :topic "Israel-Palestine conflict" .
    # :Narrative_123 :topic "Hamas" .
    # :Narrative_123 :topic "Iran\'s influence" .
    # :Narrative_123 :topic "Middle East geopolitics" .
    # :Narrative_123 :summary "The article is a personal narrative from a professional with 35 years of experience in U.S.
    #     peacemaking policy, focusing on the Israel-Palestine conflict. The author argues that peace between Israel
    #     and the Palestinians is unattainable as long as Hamas remains in control of Gaza. The piece highlights the
    #     threat posed by Hamas and Hezbollah, both backed by Iran, to Israel's existence. The author suggests that
    #     these groups aim to make Israel unlivable, aligning with Iran's long-term strategy against Israel." .
    # :Narrative_123 :interpretation_conservative "Supportive, as the article aligns with a strong
    #    stance against Hamas and highlights security concerns for Israel." .
    # :Narrative_123 :interpretation_liberal "Mixed, as some may agree with the security concerns but also
    #    worry about the humanitarian impact on Gazan civilians." .
    # :Narrative_123 :interpretation_neutral "Informative, providing a perspective on the complexities of the
    #    Israel-Palestine conflict and regional geopolitics." .
    # :Narrative_123 :ranking_conservative 5 .
    # :Narrative_123 :ranking_liberal 3 .
    # :Narrative_123 :ranking_neutral 4 .
    # :Narrative_123 :sentiment "negative" .
    # :Narrative_123 :sentiment_explanation "The sentiment is negative due to the focus on the ongoing conflict, the
    #     threat of violence, and the bleak outlook for peace as long as Hamas remains in power." .
