from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words

s = """
ВТБ прогнозирует объем рынка ЦФА по итогам года около 400 млрд рублей

По итогам 2024 года объем рынка цифровых финансовых активов (ЦФА) в России приблизится к 400 млрд рублей. Об этом в рамках ВЭФ-2024 в эфире телеканала РБК ТВ заявил член правления ВТБ Виталий Сергейчук.

«Объем рынка ЦФА в 2024 году уже превысил 200 млрд руб. и может достигнуть 400 млрд руб. Этот рынок активно развивается, его доходность уже сейчас зачастую превышает доходность по сопоставимым биржевым инструментам. Поэтому мы видим большой потенциал роста спроса на данный продукт со стороны инвесторов», – рассказал Виталий Сергейчук.

Он также отметил, что для более активного развития рынка ЦФА необходима автоматизация сделок. «Сейчас ограничен инструментарий, доступный физическим лицам. Как только мы переведем форму или возможность инвестирования в ЦФА в привычный для людей интерфейс – приложения брокерские и банковские в телефоне – будет гораздо больше спрос и всплеск интереса со стороны розничного инвестора к данному продукту», – отметил спикер.

Напомним, что в этом году ВТБ первым в России предложил частным инвесторам цифровые финансовые активы, привязанные к стоимости физического квадратного метра в строящемся жилом комплексе hideOUT. Этот инструмент радикально снизил для розничных инвесторов порог входа на рынок инвестиций в премиальную недвижимость. Доходность и защита капитала инвесторов аналогичны приобретению физического метра жилья в этом ЖК.
"""

def get_russian_stopwords():
  with open('nlp/russian_stop_words.txt', 'rt') as f:
    data = f.read()
  return frozenset(w.rstrip() for w in data.splitlines() if w)

def summarizer(text):
  LANGUAGE = "russian"
  SENTENCES_COUNT = 3
  parser = PlaintextParser.from_string(text, Tokenizer(LANGUAGE))
  summarizer = Summarizer(Stemmer(LANGUAGE))
  summarizer.stop_words = get_russian_stopwords()
  summirized = '\n'.join(str(sen) for sen in summarizer(parser.document, SENTENCES_COUNT))
  return summirized

import sys; sys.path.insert(0, '.')
import scraper_lib

articles = scraper_lib.CfaAllNewsScraper(error='raise').fetch_and_parse(scraper_lib.Periods.LAST_24_HOURS)
for a in articles:
  print('*'*10, 'BODY', '*'*10)
  print(a.body_text)
  print()
  print('*'*10, 'SUM', '*'*10)
  print(summarizer(a.body_text))
  print('*'*10, 'END', '*'*10)
  print()
  print()
  print()


