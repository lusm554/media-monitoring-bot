from .base_scraper import NewsBaseScraper
from .article import Article
import concurrent.futures
import feedparser
import datetime
import time
import logging

logger = logging.getLogger(__name__)

class RssFeed:
  '''
  Представление rss канала.
  Описывает характеристики rss канала - название источника, ссылка, название канала, если есть.
  '''
  def __init__(self, publisher_name, url, feed_name=None):
    self.publisher_name = publisher_name
    self.url = url
    self.feed_name = feed_name
  
  def __repr__(self):
    cls_name = self.__class__.__name__
    args = ', '.join(f'{k}={v!r}' for k,v in self.__dict__.items())
    return f'{cls_name}({args})'

class CfaRssNewsScraper(NewsBaseScraper):
  '''
  Парсер новоей ЦФА из Rss каналов.
  Парсит список новостных источников.
  '''
  def __init__(self, *args, **kwargs):
    '''
    Определяет список rss каналов для парсинга.
    '''
    super().__init__(*args, **kwargs)
    if self.error == 'ignore':
      logger.warning(f'Error handler set to {self.error!r}')
    self.RSS_FEEDS = (
      RssFeed(publisher_name='РИА Новости', url='https://ria.ru/export/rss2/archive/index.xml'),
      RssFeed(publisher_name='Рамблер', url='https://news.rambler.ru/rss/'),
      RssFeed(publisher_name='РБК', url='https://rssexport.rbc.ru/rbcnews/news/30/full.rss'),
      RssFeed(publisher_name='Новости Mail.ru', url='https://news.mail.ru/rss/90/'),
      RssFeed(publisher_name='Регнум', url='https://regnum.ru/rss'),
      RssFeed(publisher_name='ТАСС', url='https://tass.ru/rss/v2.xml'),
      RssFeed(publisher_name='Интерфакс', url='https://www.interfax.ru/rss.asp'),
      RssFeed(publisher_name='RT на русском', url='https://russian.rt.com/rss'),
      RssFeed(publisher_name='Известия', url='https://iz.ru/xml/rss/all.xml'),
      RssFeed(publisher_name='Российская газета', url='https://rg.ru/xml/index.xml'),
      RssFeed(publisher_name='Коммерсантъ', url='https://www.kommersant.ru/RSS/news.xml'),
      RssFeed(publisher_name='Ведомости', feed_name='Все новости', url='https://www.vedomosti.ru/rss/news.xml'),
      RssFeed(publisher_name='Ведомости', feed_name='Все материалы', url='https://www.vedomosti.ru/rss/articles.xml'),
      RssFeed(publisher_name='lenta.ru', url='https://lenta.ru/rss'),
      RssFeed(publisher_name='Московский Комсомолец', feed_name='Все материалы', url='https://www.mk.ru/rss/news/index.xml'),
      RssFeed(publisher_name='Московский Комсомолец', feed_name='Новостная лента', url='https://www.mk.ru/rss/news/index.xml'),
      RssFeed(publisher_name='Газета.ru', url='https://www.gazeta.ru/export/rss/social_more.xml'),
      RssFeed(publisher_name='RT', url='https://russian.rt.com/rss'),
      RssFeed(publisher_name='Финмаркет', url='http://www.finmarket.ru/rss/mainnews.asp'),
      RssFeed(publisher_name='Росбалт', url='https://www.rosbalt.ru/feed/'),
      RssFeed(publisher_name='Прайм', feed_name='Основной поток', url='https://1prime.ru/export/rss2/index.xml'),
      RssFeed(publisher_name='Прайм', feed_name='Финансы', url='https://1prime.ru/export/rss2/finance/index.xml'),
      RssFeed(publisher_name='Прайм', feed_name='Экономика', url='https://1prime.ru/export/rss2/state_regulation/index.xml'),
      RssFeed(publisher_name='Bits.media', url='https://bits.media/rss2/'),
      RssFeed(publisher_name='Indicator', url='https://indicator.ru/exports/rss'),
      RssFeed(publisher_name='Финам', feed_name='Новости компаний', url='https://www.finam.ru/analysis/conews/rsspoint/'),
      RssFeed(publisher_name='Финам', feed_name='Новости мировых рынков', url='https://www.finam.ru/international/advanced/rsspoint/'),
      RssFeed(publisher_name='Comnews', url='https://www.comnews.ru/rss'),
      RssFeed(publisher_name='tadviser.ru', url='https://www.tadviser.ru/xml/tadviser.xml'),
    )

  def feed_fetcher(self, url):
    '''
    Запрашивает новости rss канала в формате библиотеки feedparser.
    '''
    feed_data = feedparser.parse(url)
    return feed_data

  def feed_parser(self, feed_data, article_publisher_name='Не определен'):
    '''
    Парсит ответ формата библиотеки feedparser в экземпляры класса Article.
    '''
    articles = list()
    for entry in feed_data.entries:
      article_title = entry.get('title', '')      
      if not ('цфа' in article_title.lower() or 'цифровые финансовые активы' in article_title.lower()):
        continue
      article_url = entry.get('link')
      article_publish_time = entry.get('published_parsed')
      article = Article(
        title=article_title,
        url=article_url,
        publish_time=datetime.datetime.fromtimestamp(time.mktime(article_publish_time)).astimezone(self.timezone),
        publisher_name=article_publisher_name,
        scraper='rss',
      )
      articles.append(article)
    return articles

  def fetch_and_parse(self, period):
    '''
    Формирует набор тасков запроса и парсинга на каждый канал.
    Фильтрует по параметру period.
    '''
    logger.info(f'Fetching {len(self.RSS_FEEDS)} channels')
    result_cfa_articles = list()
    try:
      with concurrent.futures.ThreadPoolExecutor() as executor:
        logger.debug(f'{executor._max_workers=}')
        process_feed_jobs = {
          executor.submit(
            lambda feed: self.feed_parser(
              feed_data=self.feed_fetcher(feed.url),
              article_publisher_name=feed.publisher_name
            ),
            feed
          ): feed
          for feed in self.RSS_FEEDS
        }
        for done_job in concurrent.futures.as_completed(process_feed_jobs):
          cfa_articles = done_job.result()
          result_cfa_articles.extend(cfa_articles)
      news_start_time = datetime.datetime.now(tz=self.timezone) - period
      result_cfa_articles = [
        article
        for article in result_cfa_articles
        if article.publish_time >= news_start_time
      ]
      logger.info(f'Found {len(result_cfa_articles)} articles for {period}')
      # extract news
      result_cfa_articles = self.add_news_body_to_article(result_cfa_articles)
      return result_cfa_articles
    except Exception as error:
      if self.error == 'raise':
        raise error
      logger.error(error)
      return result_cfa_articles
