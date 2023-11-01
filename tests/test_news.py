import pytest
from datetime import datetime, timedelta
from dna.query_news import get_article_text, get_matching_articles


def test_articles_retrieval():
    # Search that is likely to always have results
    yesterday = datetime.now() - timedelta(1)
    match_details = {
        'topic': 'Trump',
        'fromDate': datetime.strftime(yesterday, '%Y-%m-%d'),
        'toDate': datetime.strftime(yesterday, '%Y-%m-%d')
    }
    articles = get_matching_articles(match_details)
    assert len(articles) > 0
    assert articles[0]['title']
    assert articles[0]['published']
    assert articles[0]['source']
    assert articles[0]['url']
    assert articles[0]['length'] > 0
    return


def test_article_text():
    text = get_article_text('https://apnews.com/article/israel-palestinians-gaza-hamas-'
                            'war-781b3c63af4ae6e51c313a68f314e66d')
    assert text.startswith('RAFAH, Gaza Strip (AP) — Truckloads of aid idled at Egypt’s border with Gaza as')
    assert 'Israel is ready to operate on two fronts' in text
    return
