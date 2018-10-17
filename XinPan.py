#!/usr/bin/python
# -*-coding：gbk-*-

import json
from json import JSONDecodeError

from helper.Grep import Grep
from urllib import parse
import os
import sys
from functools import reduce
import requests


class anjuke():
    timesleep = 1

    def __init__(self, timesleep):
        self.timesleep = timesleep

    def geo(self, obj):
        url = "http://api.map.baidu.com/geocoder/v2/?location=" + obj["lng"] + "," + obj[
            "lat"] + "&output=json&pois=1&ak=rhRhulWg5FGAh83v7fkHxhc4j2779L8d"
        requst = requests.get(url)
        try:
            jsonObj = json.loads(requst.text)
            if jsonObj["status"] == 0:
                address = jsonObj["result"]["formatted_address"]
                province = jsonObj["result"]["addressComponent"]["province"]
                city = jsonObj["result"]["addressComponent"]["city"]
                district = jsonObj["result"]["addressComponent"]["district"]
                obj["address"] = address
                obj["province"] = province
                obj["city"] = city
                poi = jsonObj["result"]["pois"][0]["addr"]
                obj["poi"] = poi
                obj["district"] = district
        except(IndexError, JSONDecodeError):
            print("poi不存在")

    def getCity(self):
        grep = Grep().setTimesleep(self.timesleep)
        url = 'https://www.anjuke.com/sy-city.html'
        dic = {"href": {"isAttr": True, "grepname": "href"},
               "text": {"isAttr": False, "isText": True, "grepname": "name"}}
        grep.html(url)
        selects = grep.soup.select(".city_list a")
        return grep.setSelects(selects).grep(dic, "city.json")

    def collector(self, mod_num=1, mod_index=0):
        try:
            file = open("./conf/city.json", mode='rb')
            city_list = json.loads(file.read())
        except IOError:
            city_list = self.getCity()

        city_list = Grep().divGroup(city_list, mod_num, mod_index)
        Grep().save(city_list, ".." + os.sep + "out2" + os.sep + "city_" + str(mod_index) + ".json")

        for city in city_list:
            flag = os.path.exists("./out2/" + city["name"] + ".json")
            if not flag:
                try:
                    self.getXiaoQu(city["href"], city["name"])
                except OSError:
                    continue

    def getLouPanUrl(self, url):
        grep = Grep().setTimesleep(self.timesleep)
        header = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Host": url.replace("https://", ""),
            "Referer": "https://www.anjuke.com/sy-city.html",
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:62.0) Gecko/20100101 Firefox/62.0"
        }
        grep.html(url, autoHeader=False, header=header)
        select = grep.soup.select_one(".L_tabsnew .div_xinfang a:nth-of-type(1)")
        if select:
            return select.get("href")
        else:
            return ""

    def getXiaoQu(self, url, name, index=1, ls=[]):
        url = self.getLouPanUrl(url)
        if not url:
            return
        isHasNext = False
        flag = os.path.exists("." + os.sep + "out2" + os.sep + name + "-" + str(index) + ".json")
        if not flag:
            rurl = url + "all/p" + str(index) + "/?from=navigation"
            grep = Grep().setTimesleep(self.timesleep)
            header = {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Host": url.replace("https://", ""),
                "Referer": url + "?from=navigation",
                "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:62.0) Gecko/20100101 Firefox/62.0"
            }
            grep.html(rurl, autoHeader=False, header=header)
            selects = grep.soup.select(".item-mod")
            check = grep.soup.select_one(".aNxt")
            isHasNext = check
            onePage = []

            for select in selects:
                obj = {}
                image = select.select_one("img").get("src")
                xiaoqu = select.select_one(".infos .lp-name")
                rname = xiaoqu.text
                href = xiaoqu.get("href")

                info = select.select_one(".huxing").text.strip()
                status = select.select(".status-icon")
                params = ""
                for s in status:
                    params + s.text.strip() + ";"

                tag = select.select(".tag")
                for s in tag:
                    params + s.text.strip() + ";"

                obj = {"img": image, "href": href, "name": rname, "info": info, "params": params}
                onePage.append(obj)
                print(obj)
                ls.append(obj)
            grep.save(onePage, ".." + os.sep + "out1" + os.sep + name + "-" + str(index) + ".json")

        if isHasNext:
            index = index + 1
            self.getXiaoQu(url, name, index, ls)


def str2float(s):
    def fn(x, y):
        return x * 10 + y

    n = s.index('.')
    s1 = list(map(int, [x for x in s[:n]]))
    s2 = list(map(int, [x for x in s[n + 1:]]))
    return reduce(fn, s1) + reduce(fn, s2) / (10 ** len(s2))


if __name__ == '__main__':
    anjuke(str2float(sys.argv[1])).collector(int(sys.argv[2]), int(sys.argv[3]))
