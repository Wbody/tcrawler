#!/usr/bin/python
# -*-coding：gbk-*-

import requests
import json
from bs4 import BeautifulSoup
import os
import time
from common.RandomHeaders import randomHeaders
from common.RandomProxy import randomProxy


class Grep:
    soup = {}
    selects = []
    sense = '访问验证'
    grepMap = {}
    timesleep = 1

    def divGroup(self, list, mod_num, mod_index):
        slen = len(list)
        nlist = []
        for i in range(0, slen):
            if i % mod_num == mod_index:
                nlist.append(list[i])
        return nlist

    def setTimesleep(self, timesleep):
        self.timesleep = timesleep
        return self

    def setSelects(self, selects):
        self.selects = selects
        return self

    def html(self, url, dev=False, autoHeader=True, autoProxy=True, proxies={}, header={}, isPrintUrl=True,
             isProxyPrint=True):
        time.sleep(self.timesleep)
        if isPrintUrl:
            print(url)
        isError = False
        if autoHeader:
            header = randomHeaders()
        if autoProxy:
            proxies = randomProxy(isProxyPrint)
        try:
            requst = requests.get(url, headers=header, proxies=proxies, timeout=5)
            html_doc = requst.text
            self.soup = BeautifulSoup(html_doc, 'lxml')
            if dev == True:
                print(self.soup.prettify())
        except(requests.exceptions.ProxyError, requests.exceptions.ConnectTimeout):
            print('failed!')
            isError = True
        return self.retry(url, dev, autoProxy, isError)

    def retry(self, url, dev, autoProxy, isError=False):
        if isError:
            return self.html(url, dev, autoProxy)
        if self.sense in self.soup.text:
            print("重试==》")
            return self.html(url, dev, autoProxy)
        return True

    def active(self, isGrepOne=False):
        if self.sense in self.soup.text:
            print("==>" + self.sense)
            return False
        if (len(self.selects) == 0) and (not isGrepOne):
            print(self.soup.prettify())
            print("==>未找到有效节点")
            return False
        return True

    def grepOne(self, conf):
        obj = {}
        if not self.active(True):
            return obj
        for index in conf:
            select = index
            item = select["select"]
            dic = select["dic"]
            robj = self.getObject(item, dic)
            obj = {**obj, **robj}
        return obj

    def getObject(self, item, dic):
        obj = {}
        if not self.active():
            return obj
        for key in dic:
            attr = dic[key]
            grepname = attr["grepname"]
            if (attr['isAttr'] == True):
                value = item.get(key)
            elif (attr['isText'] == True):
                value = item.text
            else:
                print("==>暂不支持其他属性")
            if value.strip() != "":
                obj[grepname] = value
        return obj

    def grep(self, dic, filename="", isSavefile=True):
        result = []
        if not self.active():
            return result
        ls = []
        for item in self.selects:
            obj = self.getObject(item, dic)
            ls.append(obj)
        result = ls
        if isSavefile:
            self.save(ls, filename)
        return result

    def save(self, ls, filename):
        curr_dir = os.path.dirname(os.path.realpath(__file__))
        path = curr_dir + os.sep + filename
        file = open(path, mode='w+', encoding="utf-8")
        txt = json.dumps(ls, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ': '))
        file.write(txt)
        file.flush()
        file.close()
