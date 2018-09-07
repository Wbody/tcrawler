#!/usr/bin/python
# -*-coding：gbk-*-

import requests
import json
from bs4 import BeautifulSoup
import lxml

from common.RandomHeaders import randomHeaders
from common.RandomProxy import randomProxy


def getCity():
    # 设置随机请求头
    header = randomHeaders()
    proxies = randomProxy()
    url = 'https://m.anjuke.com/cityList/'
    result = []
    try:
        requst = requests.get(url, headers=header, proxies=proxies, timeout=5)
        html_doc = requst.text
        soup = BeautifulSoup(html_doc, 'lxml')
        div = soup.select(".cl-c-list")[2]
        div = div.find_all("a")
        list = []
        for a in div:
            href = a.get("href")
            if href.strip() != "":
                name = a.text
                obj = {"href": href, "name": name}
                list.append(obj)
        result = list
        if len(list) > 0:
            try:
                path = "city.json"
                file = open(path, mode='w')
                txt = json.dumps(list, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ': '))
                file.write(txt)
                file.flush()
                file.close()

            except():
                print('failed!')
    except(requests.exceptions.ProxyError, requests.exceptions.ConnectTimeout):
        print('failed!')
    return result
