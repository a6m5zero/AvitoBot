from bs4 import BeautifulSoup
import requests
import re
import datetime

# URL = 'https://m.avito.ru/moskva?metro=1'

def connect_url(url):
    headers_mobile = { 'User-Agent' : 'Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B137 Safari/601.1'}
    try:
        page = requests.get(url, headers=headers_mobile)
    except:
        return 0
    print(page.status_code)
    if page.status_code != 200:
        return 0
    else:
        return page


def parse_page(page):
    soup = BeautifulSoup(page.text, "html.parser")
    # links =[a['href'] for a in soup.findAll('a', href = True)]
    links = []
    for a in soup.findAll('div', attrs={"data-marker":re.compile("item-wrapper")}):
        link = a.find('a', attrs={"data-marker":re.compile("item/link")})
        date = a.find('div', attrs={"data-marker":re.compile("item/datetime")})

        now = datetime.datetime.now()
        date_m = date.get_text()
        date_m = date_m[date_m.index(',')+2:]
        date_hour = int(date_m[:date_m.index(':')])
        date_minute = int(date_m[date_m.index(':')+1:])

        if (now.minute - date_minute) > 5:
            continue
        elif 'Сегодня' not in date.get_text():
            continue
        elif now.hour != date_hour:
            continue
        else:
            links.append('https://avito.ru%s' %link['href'])
    return links

    


