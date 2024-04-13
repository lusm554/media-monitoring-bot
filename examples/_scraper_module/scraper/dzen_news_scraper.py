from .base_scraper import NewsBaseScraper
from .article import Article
from bs4 import BeautifulSoup, SoupStrainer
import requests
import datetime
import logging

logger = logging.getLogger(__name__)

class CfaDzenNewsScraper(NewsBaseScraper):
  def __init__(self):
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

  def fetch_page(self):
    current_time = datetime.datetime.now()
    news_start_time_ms = int( (current_time - datetime.timedelta(hours=24)).timestamp() ) * 1000
    news_end_time_ms = int(current_time.timestamp()) * 1000
    params = dict(
      issue_tld='ru', # region
      text=f'ЦФА date:{current_time.strftime("%Y%m%d")}', # text request, only current date
      filter_date=f'{news_end_time_ms}', # time period in unix seconds since 1970 # only current date
      #filter_date=f'{news_start_time_ms},{news_end_time_ms}', # time period in unix seconds since 1970 # only current date
      flat=f'1', # flag for no aggregation by article theme
    )
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
    html = response.text
    return html
  
  def fetch_and_parse(self, period):
    dzen_html_page = self.fetch_page()
