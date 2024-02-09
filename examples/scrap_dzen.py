import requests

def get_html():
  cookies = {
    'KIykI': '1',
    'HgGedof': '1',
    'zen_sso_checked': '1',
    'yandex_login': '',
    'sso_status': 'sso.passport.yandex.ru:synchronized',
  }

  headers = {
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

  params = {
    'issue_tld': 'ru',
    'text': 'ЦФА',
    'filter_date': '1706821200000,1706907600000',
    'flat': '1',
  }

  res = requests.get('https://dzen.ru/news/search', params=params, headers=headers, cookies=cookies)
  print('status code', res.status_code)
  #print(res.history)
  print('req url', res.url)
  print()
  html = res.text
  return html

def parse_dzen(html):
  from bs4 import BeautifulSoup, SoupStrainer
  only_tags_with_role_main = SoupStrainer(role='main')
  soup = BeautifulSoup(html, 'lxml', parse_only=only_tags_with_role_main)
  links = soup.find_all('article')
  for l in links:
    title_a = l.find('a')
    print(title_a.prettify())
    href = title_a.get('href')
    title = title_a.find('span').get_text()
    print(href)
    print(title)
    print()

html = get_html()
res = parse_dzen(html)
#print(res)