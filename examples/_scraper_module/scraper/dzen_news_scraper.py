from .base_scraper import NewsBaseScraper
from .article import Article
from bs4 import BeautifulSoup, SoupStrainer
import requests
import datetime
import logging

logger = logging.getLogger(__name__)

class CfaDzenNewsScraper(NewsBaseScraper):
  '''
  Парсер новоей ЦФА из Дзена.
  '''
  def __init__(self):
    '''
    Устанавливает параметры HTTP запроса к Дзену.
    '''
    self.DZEN_URL = 'https://dzen.ru/news/search'
    self.COOKIES = {
      'KIykI': '1',
      'HgGedof': '1',
      'zen_sso_checked': '1',
      'yandex_login': '',
      'sso_status': 'sso.passport.yandex.ru:synchronized',
    }
    self.HEADERS = {
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
      'Accept-Language': 'en-US,en;q=0.9',
      'Connection': 'keep-alive',
      'Referer': 'https://sso.dzen.ru/',
      'Sec-Fetch-Dest': 'document',
      'Sec-Fetch-Mode': 'navigate',
      'Sec-Fetch-Site': 'same-site',
      'Upgrade-Insecure-Requests': '1',
      'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
      'sec-ch-ua': '"Not)A;Brand";v="24", "Chromium";v="116"',
      'sec-ch-ua-mobile': '?0',
      'sec-ch-ua-platform': '"macOS"',
    }

  def page_fetcher(self, for_period, content_type):
    '''
    Запрашивает HTML или json страницу новостей по теме 'ЦФА' из Дзенa.
    Запрос передается с фильтром на период новостей.
    '''
    current_time = datetime.datetime.now()
    #current_time = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    #news_start_time = current_time - datetime.timedelta(hours=24)
    news_start_time_ms = int((current_time - datetime.timedelta(hours=24)).timestamp()) * 1000
    news_end_time_ms = int(current_time.timestamp()) * 1000
    for page_num in range(10):
      params = dict(
        issue_tld='ru', # region
        text=f'ЦФА date:{current_time.strftime("%Y%m%d")}..{current_time.strftime("%Y%m%d")}', # text request, only current date
        filter_date=f'{news_start_time_ms},{news_end_time_ms}', # for period more than 24 hours
        flat=1, # flag for no aggregation by article theme
        p=page_num,
        sortby='date', # news sort key
      )
      if content_type == self.DZEN_JSON_PARSER:
        params['ajax'] = 1 # flag for json response
      response = requests.get(
        url=self.DZEN_URL,
        headers=self.HEADERS,
        cookies=self.COOKIES,
        params=params,
      )
      logger.info(f'Fetched dzen {response.url}')
      logger.info(f'Fetched status {response.status_code}')
      logger.info(f'Fetched in {response.elapsed.total_seconds()} seconds')
      assert response.status_code == 200
      if content_type == self.DZEN_JSON_PARSER:
        page_data = response.json()
      else:
        page_data = response.text
      yield page_data 
      time.sleep(.1)

  def html_page_parser(self, html):
    '''
    Парсит статьи из HTML страницы новостей Дзенa.
    Формирует объект статьи в формате Article.
    '''
    logger.info(f'Parsing html page with size {len(html)} bytes')
    only_tags_with_role_main = SoupStrainer(role='main')
    soup = BeautifulSoup(html, 'lxml', parse_only=only_tags_with_role_main)
    articles_from_page = soup.find_all('article')
    articles_parsed = []
    for page_article in articles_from_page:
      _article_link = page_article.find('a')
      article_href = _article_link.get('href')
      article_title = _article_link.find('span').get_text()
      article_source_name = page_article.find(attrs={'class': 'mg-snippet-source-info__agency-name'}).get_text()
      article_publish_time = page_article.find(attrs={'class': 'mg-snippet-source-info__time'}).get_text()
      article = Article(
        title=article_title,
        url=article_href,
        publish_time=article_publish_time,
        publisher_name=article_source_name,
        scraper='dzen',
      )
      articles_parsed.append(article)
    logger.info(f'Found {len(articles_parsed)} articles')
    return articles_parsed 

  def json_page_parser(self, json):
    json = json['data']
    articles = list()
    for story in json.get('stories', []):
      for doc in story.get('docs', []):
        article_url = doc.get('url')
        article_title = ''.join(x.get('text') for x in doc.get('title'))
        article_source_name = doc.get('sourceName')
        article_publish_time = doc.get('time')
        article = Article(
          title=article_title,
          url=article_url,
          publish_time=article_publish_time,
          publisher_name=article_source_name,
          scraper='dzen',
        )
        articles.append(article)
    return articles
  def fetch_and_parse(self, period):
    '''
    Основная функция класса, запрашивает HTML новостей Дзена и парсит их в общий формат данных.
    '''
    dzen_html_page = self.fetch_page()
    dzen_articles = self.parse_page(dzen_html_page)
    for art in dzen_articles:
      print(art)
      print()
