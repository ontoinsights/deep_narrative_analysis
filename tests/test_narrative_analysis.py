import pytest

from dna.app_functions import get_metadata_ttl, Metadata
from dna.create_narrative_turtle import create_graph
from dna.database import add_remove_data
from dna.nlp import parse_narrative

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


def test_narrative_turtle():
    sentence_classes, quotation_classes = parse_narrative(narr_text)
    graph_results = create_graph(sentence_classes, quotation_classes, narr_text, ':Narrative_123',
                                 ['politics and international'], 100, 'foo')
    add_remove_data('add', ' '.join(graph_results.turtle), 'foo', '123')   # Add to dna db's foo_123 graph
    narr_meta = Metadata('I Might Have Once Favored a Cease-Fire With Hamas, but Not Now', '2023-10-27',
                         'New York Times', 'https://www.nytimes.com/2023/10/27/opinion/hamas-war-gaza-israel.html', 10)
    metadata_results = get_metadata_ttl('foo', '123', narr_text, narr_meta, 10)
    ttl_str = str(metadata_results.turtle)
    print(ttl_str)
    assert ':text ' in ttl_str
    assert ':topic ' in ttl_str and ':summary ' in ttl_str
    assert ':narrative_goal "analyze' in ttl_str
    assert ':interpretation_conservative' in ttl_str
    assert ':sentiment "negative' in ttl_str
    assert ':sentiment_explanation' in ttl_str
    # Output Turtle:
    # Full article processing in ~ 2 minutes
    # :123 a :InformationGraph ; dc:created "2024-12-13T19:13:02"^^xsd:dateTime ;
    #   :number_triples 238 ; :encodes :Narrative_123 .
    # :Narrative_123 a :Narrative ; dc:created "2023-10-27"^^xsd:dateTime ;
    #   :number_sentences 10 ; :source "New York Times" ;
    #   dc:title "I Might Have Once Favored a Cease-Fire With Hamas, but Not Now" ;
    #   :external_link "https://www.nytimes.com/2023/10/27/opinion/hamas-war-gaza-israel.html" .
    # :Narrative_123 :text "For 35 years, I’ve devoted my professional life to U.S. peacemaking policy ..." .
    # :Narrative_123 :subject_area "politics and international" .
    # :Narrative_123 :subject_area "crime and law" .
    # :Narrative_123 :narrative_goal "analyze" .
    # :Narrative_123 :narrative_goal "establish-authority" .
    # :Narrative_123 :information_flow "analytical" .
    # :Narrative_123 :information_flow "causal" .
    # :Narrative_123 :narrative_plotline "conflict and resolution" .
    # :Narrative_123 :narrative_plotline "overcoming the monster/heroic acts" .
    # :Narrative_123 :topic "Israel-Palestine conflict" .
    # :Narrative_123 :topic "Hamas" .
    # :Narrative_123 :topic "Iran\'s influence" .
    # :Narrative_123 :topic "Middle East peace process" .
    # :Narrative_123 :topic "Gaza" .
    # :Narrative_123 :summary "The article discusses the author\'s perspective on the Israel-Palestine conflict,
    #     emphasizing the need for a lasting peace solution that involves dismantling Hamas\'s power in Gaza.
    #     The author argues that as long as Hamas remains a military force, peace will be unattainable, and Israel\'s
    #     survival is at risk. The article also highlights the role of Iran in supporting militant groups like Hamas
    #     and Hezbollah, which aim to destabilize Israel." .
    # :Narrative_123 :interpretation_conservative "Conservatives may agree with the article\'s stance on the necessity
    #     of dismantling Hamas to ensure Israel\'s security." .
    # :Narrative_123 :interpretation_liberal "Liberals might be concerned about the implications for Palestinian
    #     civilians and the broader peace process." .
    # :Narrative_123 :interpretation_neutral "Neutral readers may appreciate the analysis of the complex geopolitical
    #     dynamics in the region." .
    # :Narrative_123 :sentiment "negative" .
    # :Narrative_123 :sentiment_explanation "The sentiment is negative due to the focus on ongoing conflict,
    #     threats to Israel\'s existence, and the challenges in achieving peace." .
