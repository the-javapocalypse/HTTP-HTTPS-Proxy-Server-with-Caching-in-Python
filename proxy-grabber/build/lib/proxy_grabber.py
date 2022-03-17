# -*- coding: utf8 -*-
import time
import random
from multiprocessing import Pool
import requests
from bs4 import BeautifulSoup


class ProxyGrabber:
    def __init__(self, useragents_file=None):
        self.user_ip = self.get_ip()
        if useragents_file is not None:
            self.useragents = open(useragents_file).read().split('\n')

        self.proxy_list = []
        self.checked_proxies = []
        self.proxy_countries = []

    def add_proxies(self, proxies):
        self.proxy_list += proxies

    def get_useragent(self):
        return random.choice(self.useragents)

    def get_proxy_list(self):
        return self.proxy_list

    def get_checked_proxies(self):
        return self.checked_proxies

    def get_proxy(self):
        return random.choice(self.checked_proxies)

    def get_ip(self, proxies={}):
        return requests.get(url='http://ip-api.com/json', proxies=proxies).json()['query']

    def load(self, filename='./data/proxy-list.txt'):
        self.load_proxies(filename)

    def load_proxies(self, filename='./data/proxy-list.txt'):
        file = open(filename, 'r')
        proxies = file.readlines()
        file.close()
        for proxy in proxies:
            self.proxy_list.append(proxy.rstrip())

    def save(self, filename='./data/proxy-list.txt'):
        self.save_proxies(filename)

    def set_countries(self, countries):
        self.proxy_countries = countries

    def save_proxies(self, filename='./data/proxy-list.txt'):
        file = open(filename, 'w')
        for proxy in self.checked_proxies:
            file.write(proxy[7:] + '\n')
        file.close()

    def check_proxy(self, proxy):
        proxy = 'http://' + proxy
        time.sleep(1)
        try:
            result = requests.get('http://ip-api.com/json', proxies={'http': proxy}, timeout=2)
            if result.status_code == 200:
                try:
                    if result.json()['status'] == 'success' and result.json()['query'] != self.user_ip:
                        if self.proxy_countries != [] and result.json()['countryCode'] in self.proxy_countries:
                            return proxy
                except IndexError:
                    return False
            else:
                return False
        except requests.exceptions.ConnectionError:
            return False
        except requests.exceptions.ReadTimeout:
            return False
        except requests.exceptions.ChunkedEncodingError:
            return False
        except requests.exceptions.TooManyRedirects:
            return False

    def grab_proxies(self, proxy_limit=None):
        proxy_list = []
        proxy_sources = [
            self._get_clarketm_list,
            self._get_ipadress_proxy,
            self._get_proxyscale_proxy,
            self._get_freeproxylist_proxy,
        ]

        for parse_source in proxy_sources:
            proxy_list += parse_source()
            if proxy_limit is not None and len(proxy_list) > proxy_limit:
                self.proxy_list = list(set(self.proxy_list + proxy_list))
                return self.proxy_list

        self.proxy_list = list(set(self.proxy_list + proxy_list))
        return self.proxy_list

    def check_proxies(self):
        with Pool(20) as p:
            proxy_list = p.map(self.check_proxy, self.proxy_list)
        checked_proxy_list = []

        for elem in proxy_list:
            if elem:
                checked_proxy_list.append(elem)

        self.checked_proxies = checked_proxy_list

    def _get_ipadress_proxy(self):
        target_url = 'https://www.ip-adress.com/proxy-list'
        result = requests.get(target_url)
        soup = BeautifulSoup(result.text, "lxml")
        pars_result = soup.find('tbody').find_all('tr')
        proxy_list = []
        for elem in pars_result:
            elem = elem.get_text().split()[:2]
            if elem[1] != 'transparent':
                proxy_list.append(elem[0])
        return proxy_list

    def _get_proxyscale_proxy(self):
        url = 'http://free.proxy-sale.com/?pg=&port[]=http&type[]=an&type[]=el'
        result = requests.get(url)
        soup = BeautifulSoup(result.text, "lxml")
        export_url = soup.find(class_='ico-export-tre').a['href']
        ip_list = requests.get('http://free.proxy-sale.com/' + export_url).text.split('\r\n')
        return ip_list[:-1]

    def _generate_urls(self, pages_count, target_url_bp, target_url_ep):
        urls = []
        for i in range(pages_count):
            target_url = target_url_bp + str(i + 1) + target_url_ep
            urls.append(target_url)
        return urls

    def _parse(self, target_url):
        time.sleep(random.uniform(0.5, 2))
        result = requests.get(target_url)
        soup = BeautifulSoup(result.text, "lxml")
        ports = []
        ip_port = []
        for elem in soup.find('tbody').find_all('img'):
            if 'imgport' in elem.get('src'):
                ports.append(str(elem)[28:str(elem).index('"/>')])

        proxy_list = []
        for elem in soup.find('tbody').find_all('tr'):
            proxy_list.append(elem.get_text().split()[0])

        for i in range(len(ports)):
            ip_port.append(proxy_list[i] + ':' + ports[i])
        return ip_port

    def _get_freeproxylist_proxy(self):
        result = []
        result += self._get_proxy_list('https://us-proxy.org/')
        result += self._get_proxy_list('https://free-proxy-list.net/')
        return result

    def _get_proxy_list(self, url):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "lxml")
        result = soup.find('table',
                           id='proxylisttable').find('tbody').find_all('tr')
        proxy_list = []
        for elem in result:
            elem = str(elem)[8:-10].split('</td')
            if elem[4][5:] != 'transparent':
                proxy = elem[0] + ':' + elem[1][5:]
                proxy_list.append(proxy)
        return proxy_list

    def _get_clarketm_list(self):
        response = requests.get(
            'https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list.txt')
        proxies = response.text.split('\n')
        proxy_list = []
        for i in range(4, len(proxies) - 2):
            proxy_list.append(proxies[i].split(' ')[0])
        return proxy_list
