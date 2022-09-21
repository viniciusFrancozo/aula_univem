import requests
from bs4 import BeautifulSoup
import json
import math
import re
import pandas as pd
import concurrent.futures
from functools import partial


class Bot:
    def __init__(self, headers=None):
        self.session = requests.Session()
        if headers is None:
            headers = {
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.134 Safari/537.36 Edg/103.0.1264.77',
                'x-olx-team-key': '5XzjuCgmYE7qMlYpsLZbTvm98ik4CS4a',
            }
        self.session.headers.update(headers)

    def __crawler_olx(self, query, pages=0):
        ads = []

        request = self.session.get(f'https://sp.olx.com.br/regiao-de-bauru-e-marilia?o={pages}&q={query}')
        html = BeautifulSoup(request.text, 'html.parser')
        if pages == 0:
            script = html.find('script', attrs={'id': 'initial-data'})
            json_html = script['data-json']
            json_ = json.loads(json_html)
            total_of_pages = math.ceil(json_['listingProps']['totalOfAds'] / 50)

        name_n_link = html.find_all('a', attrs={'data-lurker-detail': 'list_id'})
        price = html.find_all('span', attrs={'aria-label': re.compile('^Preço')})
        if name_n_link:
            for (n, p) in zip(name_n_link, price):
                ads.append([n['title'], n['href'], p.text])
        else:
            return 'Nenhum anúncio com as palavras-chave localizado'
        try:
            return total_of_pages
        except NameError:
            return ads

    def get_ads_olx(self, query, valor_minimo=0, valor_maximo=0, filtro=None):
        if filtro is None:
            filtro = []
        tabela = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = executor.map(partial(self.__crawler_olx, query), range(1, self.__crawler_olx(query)))
        for i in results:
            for j in i:
                try:
                    if valor_maximo > 0:
                        if valor_minimo < int(j[2][3:].translate({ord('.'): None})) < valor_maximo and set(filtro) <= set(j[0].lower().split()) if len(filtro) > 0 else True:
                            tabela.append(j)
                    else:
                        if valor_minimo < int(j[2][3:].translate({ord('.'): None})) and set(filtro) <= set(j[0].lower().split()) if filtro != '' else True:
                            tabela.append(j)
                except ValueError:
                    ...
        pd.DataFrame(tabela, columns=['Titulo', 'Link', 'Preco']).to_excel('teste.xlsx')


bot = Bot()
query_ = 'iphone x'
filtro_ = 'iphone'.lower().split()
bot.get_ads_olx(query_)

