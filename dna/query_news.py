# Query for details using newsAPI

import json
import logging
import os
import requests

from bs4 import BeautifulSoup

from dna.utilities_and_language_specific import add_to_dictionary_values, empty_string, space

news_key = os.environ.get('NEWS_API_KEY')
newsapi_url = 'https://newsapi.org/v2/everything?'\
    'q={topic}&from={from}&to={to}&searchIn=title,description&'\
    'page={page}&sources={sources}&sortBy=popularity&language=en&apiKey={news_key}'

# Sources limited to 20 at a time
sources1 = 'abc-news,al-jazeera-english,associated-press,axios,bbc-news,bloomberg,breitbart-news,'\
           'business-insider,cbc-news,cbs-news,cnn,fox-news,google-news,independent,msnbc,national-review,'\
           'nbc-news,newsweek'
sources2 = 'politico,reuters,the-american-conservative,the-globe-and-mail,the-hill,the-hindu,'\
           'the-huffington-post,the-irish-times,the-jerusalem-post,the-times-of-india,the-wall-street-journal,'\
           'the-washington-post,the-washington-times,time,usa-today'

excluded_urls = ['/video', '/live', '/tv', 'bbc.co.uk/programmes']

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/50.0.2661.102 Safari/537.36'}

extraction_details = {
    'abcnews.go.': ['article', 'p'],
    '.afr.': ['article', 'p'],
    '.aljazeera.': ['div&class&wysiwyg--all-content', 'p'],
    'apnews.com': ['div&class&RichTextStoryBody', 'p'],
    '.bbc.': ['', 'p&class&ssrcss-1q0x1qg-Paragraph'],
    '.bloomberg.': [],       # ['div&class&body-content', 'p'],
    '.breitbart.': ['div&class&entry-content', 'p', 'p&class&rmoreabt'],
    '.businessinsider.': ['schemaorg', 'articleBody'],
    '.cbc.ca': ['div&class&story', 'p'],
    '.cbsnews.': ['schemaorg', 'articleBody'],
    '.ctvnews.': ['div&class&c-text', 'p'],
    '.cnn.': ['schemaorg', 'articleBody'],
    'economictimes.indiatimes.': ['', 'article'],
    '.foxnews.': ['schemaorg', 'articleBody'],
    '.france24.': [],        # ['', '<p><span>'],
    '.ft.': [],              # ['div&class&article__content-body', 'p'],
    'globalnews.ca': ['article', 'p'],
    '.hindustantimes.': [],  # ['div&class&storyDetails', 'p'],
    '.independent.': ['div&class&sc-cvxyxr-6', 'p'],
    '.indiatoday.': ['main&class&main__content', 'p'],
    'irishtimes.': ['article&class&article-body-wrapper', 'p'],
    '.jpost.': ['schemaorg', 'articleBody'],
    '.moneycontrol.': ['schemaorg', 'articleBody'],
    '.nbcnews.': ['schemaorg', 'articleBody'],
    '.ndtv.': ['div&itemprop&articleBody', 'p'],
    '.newsweek.': ['schemaorg', 'articleBody'],
    'nypost.': ['', 'p'],
    '.nytimes.': [],         # ['', 'p&class&css-at9mc1'],
    '.politico.': ['', 'p&class&story-text__paragraph'],
    '.reuters.': ['', 'p&data-testid&*paragraph-'],
    '.rt.': ['div&class&article__text', 'p', 'div&class&article__share article__share_bottom'],
    '.thedailybeast.': ['article&class&Body hpCCr', 'p', 'p&class'],
    '.theglobeandmail.': ['', 'p&class&c-article-body__text'],
    '.theguardian.': ['div&class&article-body-commercial-selector', 'p&class&dcr-94xsh'],
    'thehill.': ['article', 'p'],
    'timesofindia.indiatimes': ['schemaorg', 'articleBody'],
    '.usatoday.': ['article', 'p'],
    '.vnexpress.': ['div&class&fck_detail', 'p'],
    '.washingtonpost.': ['schemaorg', 'hasPart/cssSelector=".article-body"/value'],
    '.washingtontimes.': ['div&class&storyareawrapper', 'p'],
    '.wsj.': []
}


def _check_excluded(url) -> bool:
    """
    Determine if the URL contains text such as 'video' or 'tv', indicating that it likely contains
    little relevant text, or if its text can't be parsed by (is not accounted for by) BeautifulSoup
    processing. If so, return True to signal that further processing should not be done. Otherwise,
    return False.

    :param url: String holding the URL
    :return: False if the URL could reasonably contain narrative text that could be retrieved;
             Otherwise, True indicating that the URL should be excluded from further processing
    """
    for exclude_url in excluded_urls:
        if exclude_url in url:
            return True
    for key in extraction_details:
        if key in url:
            return False
    return True


def _find_element(soup, start: str) -> list:
    """
    Return the value(s) of the HTML element specified by the 'start' input parameter.

    :param soup: The BeautifulSoup output being analyzed (which may be a subset of the entire webpage)
    :param start: The HTML element being searched for
    :return: The values of the specified HTML element (tag/attribute)
    """
    if '||' in start:
        starts = start.split('||')
        elements = []
        for alt_start in starts:
            elements.extend(find_element(soup, alt_start))
            return elements
    else:
        if '&' in start:
            strings = start.split('&')
            tag = strings[0]
            attrib_name = strings[1]
            name = strings[2]
            return soup.find(tag, {attrib_name: name})
        else:
            return soup.find(start)


def _process_extraction(soup, value) -> str:
    """
    Given that HTML details are returned for a URL, process them using BeautifulSoup and the relevant
    HTML tags and attribute value details specified in the extraction_details dictionary.

    :param soup: The BeautifulSoup output for the URL
    :param value: The HTML processing details found in extraction_details
    :return: The text of the narrative extracted from the soup using the value details
    """
    if len(value) == 0:
        return empty_string
    start = value[0]
    text_at = value[1]
    # stop = empty_string
    # if len(value) == 3:   Future: Use stop details, ignored for now
    #     stop = value[2]
    if start == 'schemaorg':
        return _process_json(soup)
    elif start == empty_string:
        element_detail = soup
    else:
        element_detail = _find_element(soup, start)
    article_text = empty_string
    if element_detail:
        if text_at.startswith('<'):
            text_elements = text_at.split('>')
            first_element = text_elements[0][1:]
            second_element = text_elements[1][1:]
            first_elements = element_detail.find_all(first_element)
            for first in first_elements:
                first_child = str(first.select_one(":nth-child(1)"))
                if first_child.startswith(f'<{second_element}'):
                    new_text = first.text.strip()
                    if new_text and len(new_text) > 75:
                        article_text += new_text + space
                else:
                    continue
        else:
            if '&' in text_at:
                strings = text_at.split('&')
                tag = strings[0]
                attrib_name = strings[1]
                name = strings[2]
                art_texts = element_detail.find_all(tag, {attrib_name: name})
            else:
                art_texts = element_detail.find_all(text_at)
            for art_text in art_texts:
                new_text = art_text.text.strip()
                if new_text:
                    article_text += new_text + space
    return article_text


def _process_html(url: str) -> str:
    """
    Return the narrative text found at the specified URL, if any.

    :param url: String holding the URL where the narrative text should be found
    :return: The extracted text or an empty string
    """
    text = ''
    try:
        web_page = requests.get(url, headers=headers, timeout=10)
    except requests.exceptions.ConnectTimeout:
        logging.error(f'News text timeout for url, {url}')
        return empty_string
    except requests.exceptions.RequestException as e:
        logging.error(f'News text error for url, {url}, Exception={str(e)}')
        return empty_string
    if web_page.status_code == 200:
        soup = BeautifulSoup(web_page.text, 'html.parser')
        for key, value in extraction_details.items():
            if key in url:
                if len(value) > 0:
                    text = _process_extraction(soup, value)
                break
    return text


def _process_json(soup) -> str:
    """
    Return the narrative text for websites that use Schema.org to capture their article text.

    :param soup: The BeautifulSoup output for the URL
    :return: String holding the article text
    """
    json_texts = soup.find_all('script', type='application/ld+json')
    for json_text in json_texts:
        json_string = str(json_text)
        try:
            json_detail = json.loads(json_string[json_string.index('>') + 1:json_string.index('</script')].strip())
            if 'articleBody' in json_detail:
                return json_detail['articleBody']
            elif 'hasPart' in json_detail and 'cssSelector' in json_detail['hasPart'] and \
                    '.article-body' == json_detail['hasPart']['cssSelector']:
                return json_detail['hasPart']['value']
        except Exception as e:
            # Usually occurs because line feeds/carriage returns in articleBody are invalid
            # TODO: Improve error handling
            if '"articleBody":' in json_string:
                index_body = json_string.index('"articleBody":') + 14
                return json_string[json_string.index('"', index_body) + 1:json_string.index('",', index_body + 25)]
            logging.warning(f'Exception in JSON-LD handling for text, {json_text}, Exception={str(e)}')
    return empty_string


def get_articles(dictionary: dict, request: str, source_list: str, page_number: int):
    """
    Use the News API to retrieve articles with the specified topic, published within the
    indicated date range.

    :param dictionary: Dictionary storing the articles' details
    :param request: The query parameters specifying the topic and from/to dates
    :param source_list: A list of publications to query
    :param page_number: The page number of results if there are more than 200 results
    :return: N/A (the dictionary is updated)
    """
    request = request.replace('{sources}', source_list).replace('{page}', str(page_number))
    try:
        resp = requests.get(request, timeout=10)
    except requests.exceptions.ConnectTimeout:
        logging.error(f'NewsAPI timeout: Query={request}')
        return
    except requests.exceptions.RequestException as e:
        logging.error(f'NewsAPI query error: Query={request} and Exception={str(e)}')
        return
    if resp.status_code == 200:
        json_response = resp.json()
        number_results = json_response['totalResults']
        if number_results > 0:
            list_articles = json_response['articles']
            for article in list_articles:
                if article['title'] == '[Removed]' or ' [+' not in article['content']:
                    continue
                add_to_dictionary_values(dictionary, 'titles', article['title'], str)
                add_to_dictionary_values(dictionary, 'dates', article['publishedAt'], str)
                add_to_dictionary_values(dictionary, 'sources', article['source']['name'], str)
                add_to_dictionary_values(dictionary, 'urls',
                                         article['url'].replace('https://consent.google.com/ml?continue=', ''), str)
                contents = article['content'].split(' [+')   # For ex, "content text ... [+xxx chars]"
                length_content = len(contents[0]) + int(contents[1].split(' chars')[0])
                add_to_dictionary_values(dictionary, 'lengths', length_content, int)
        if page_number == 1:
            logging.info(f'Found {number_results} articles for the request {request}')
            if number_results > 100:
                number_pages = int(number_results/100)
                if number_results % 100 > 0:
                    number_pages += 1
                for i in range(2, number_pages+1):
                    get_articles(dictionary, request, source_list, i)
    else:
        logging.error(f'Failed to retrieve news articles for {request}, response code {resp.status_code}')


def get_article_text(url: str) -> str:
    """
    Using the article URL details, get the text and return it.

    :param url: String holding the web address of the article
    :return: String holding the narrative retrieved from the online site.
    """
    if 'removed.com' in url or _check_excluded(url):
        return empty_string
    elif url.startswith('https://news.google.com/'):
        interim_soup = BeautifulSoup(requests.get(url).text, 'html.parser')
        # Future: FinancialTimes url ref not in og:url but = www.ft.com/content/id,
        #   where id in <script> LD, trackingData->pageDescription->rootContentId
        new_url = interim_soup.find_all('meta', {'property': 'og:url'})
        if len(new_url) == 1:
            url = new_url[0]['content']
            if '404' in url or _check_excluded(url):
                return empty_string
        else:
            return empty_string
    narr_text = _process_html(url)
    if len(narr_text) > 500:
        return narr_text
    else:
        return empty_string


def get_matching_articles(match_details: dict) -> list:
    """
    Retrieve and process the requested news articles.

    :param match_details: The input parameters from the REST call - topic and article dates
    :return: A list of articles' metadata which match the details (metadata includes title, date, source
             url and length)
    """
    # Get the articles and capture their metadata
    curr_request = newsapi_url.replace('{topic}', match_details['topic']).replace('{news_key}', news_key) \
        .replace('{from}', match_details['fromDate']).replace('{to}', match_details['toDate'])
    article_dict = {
        'titles': [], 'dates': [], 'sources': [], 'urls': [], 'lengths': []
    }
    get_articles(article_dict, curr_request, sources1, 1)
    get_articles(article_dict, curr_request, sources2, 1)
    # Remove duplicate titles if in Google News and another source
    remove_indices = []
    for i in range(0, len(article_dict['titles'])):
        excluded = False
        for exclude_url in excluded_urls:
            if exclude_url in article_dict['urls'][i]:
                remove_indices.append(i)
                excluded = True
                break
        if not excluded and article_dict['sources'][i] == 'Google News':
            gn_sd_title = article_dict['titles'][i][:30]
            index = 0
            for title in article_dict['titles']:
                if title.startswith(gn_sd_title) and index != i:
                    remove_indices.append(i)
                index += 1
    logging.info(f'Removing {len(remove_indices)} articles as duplicate or excluded')
    # Reset the results to remove the indicated indices
    articles = []
    for i in range(0, len(article_dict['titles'])):
        if i in remove_indices:
            continue
        art_detail = dict()
        art_detail['title'] = article_dict['titles'][i]
        art_detail['published'] = article_dict['dates'][i]
        art_detail['source'] = article_dict['sources'][i]
        art_detail['url'] = article_dict['urls'][i]
        art_detail['length'] = article_dict['lengths'][i]
        articles.append(art_detail)
    return articles
