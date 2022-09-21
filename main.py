import pandas as pd
import requests
from bs4 import BeautifulSoup
import json
import math
import re
import concurrent.futures
from functools import partial


session = requests.Session()
session.headers.update({
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.134 Safari/537.36 Edg/103.0.1264.77',
    'x-olx-team-key': '5XzjuCgmYE7qMlYpsLZbTvm98ik4CS4a',
})


def crawler(query_, pages_):
    ads = []
    request = session.get(f'https://sp.olx.com.br/regiao-de-bauru-e-marilia?o={pages_}&q={query_}')
    html = BeautifulSoup(request.text, 'html.parser')
    if pages_ == 0:
        script_ = html.find('script', attrs={'id': 'initial-data'})
        json_html_ = script_['data-json']
        json_ = json.loads(json_html_)
        total_of_pages = math.ceil(json_['listingProps']['totalOfAds']/50)

    name_n_link = html.find_all('a', attrs={'data-lurker-detail': 'list_id'})
    price = html.find_all('span', attrs={'aria-label': re.compile('^Preço')})
    if name_n_link:
        for i, (n, p) in enumerate(zip(name_n_link, price)):
            ads.append([n['title'], n['href'], p.text])
    else:
        return 'Nenhum anúncio com as palavras-chave localizado'
    try:
        return total_of_pages
    except NameError:
        return ads


query = 'iphone'
filtro = 'iphone'.lower().split()
pages = crawler(query, 0)

with concurrent.futures.ThreadPoolExecutor() as executor:
    results = executor.map(partial(crawler, query), range(1, pages+1))

tabela = []
margem1 = 1300
margem2 = 2100

for i in results:
    for j in i:
        try:
            if margem1 < int(j[2][3:].translate({ord('.'): None})) < margem2 and set(filtro) <= set(j[0].lower().split()):
                tabela.append(j)
        except ValueError:
            ...
df = pd.DataFrame(tabela, columns=['Titulo', 'Link', 'Preco'])
df.to_excel('teste.xlsx')
