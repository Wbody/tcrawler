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
        Grep().save(city_list, ".." + os.sep + "out1" + os.sep + "city_" + str(mod_index) + ".json")

        for city in city_list:
            flag = os.path.exists("./out1/" + city["name"] + ".json")
            if not flag:
                try:
                    self.getXiaoQu(city["href"], city["name"])
                except OSError:
                    continue

    def getXiaoQuDetail(self, url, obj):
        grep = Grep().setTimesleep(self.timesleep)
        arr = url.split("community")
        header = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Host": url.replace("https://", "").split("/")[0],
            "Referer": arr[0] + "community/props/sale" + arr[1],
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:62.0) Gecko/20100101 Firefox/62.0"
        }
        grep.html(url, autoHeader=False, header=header, isPrintUrl=False, isProxyPrint=False)

        try:
            image = grep.soup.select_one("#j-switch-basic img:nth-of-type(1)").get("src")
            obj["bigimage"] = image
            decription = grep.soup.select_one(".comm-brief-mod.j-ext-infos > p:nth-of-type(1)")
            obj["decription"] = ""
            if decription is not None:
                obj["decription"] = decription.text

            info = grep.soup.select("dl.basic-parms-mod")[0]
            lx = info.select_one("dt:nth-of-type(1)").text + info.select_one("dd:nth-of-type(1)").text
            areas = info.select_one("dt:nth-of-type(3)").text + info.select_one("dd:nth-of-type(3)").text
            sums = info.select_one("dt:nth-of-type(4)").text + info.select_one("dd:nth-of-type(4)").text
            years = info.select_one("dt:nth-of-type(5)").text + info.select_one("dd:nth-of-type(5)").text
            lh = info.select_one("dt:nth-of-type(8)").text + info.select_one("dd:nth-of-type(8)").text
            kfs = info.select_one("dt:nth-of-type(9)").text + info.select_one("dd:nth-of-type(9)").text
            wygs = info.select_one("dt:nth-of-type(10)").text + info.select_one("dd:nth-of-type(10)").text
            obj["params"] = lx + ";" + areas + ";" + sums + ";" + years + ";" + lh + ";" + kfs + ";" + wygs + ";"
        except:
            print(obj)

    def getXiaoQu(self, url, name, index=1, ls=[]):
        isHasNext = False
        flag = os.path.exists("." + os.sep + "out1" + os.sep + name + "-" + str(index) + ".json")
        if not flag:
            rurl = url + "/community/p" + str(index) + "?from=navigation"
            grep = Grep().setTimesleep(self.timesleep)
            header = {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Host": url.replace("https://", ""),
                "Referer": url + "?from=navigation",
                "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:62.0) Gecko/20100101 Firefox/62.0"
            }
            grep.html(rurl, autoHeader=False, header=header)
            selects = grep.soup.select(".li-itemmod")
            check = grep.soup.select_one(".aNxt")
            isHasNext = check
            onePage = []

            for select in selects:
                obj = {}
                image = select.select_one("img").get("src")
                xiaoqu = select.select_one(".li-info h3 a")
                rname = xiaoqu.text
                info = select.select_one(".date").text.strip()
                href = xiaoqu.get("href")
                location = select.select_one(".bot-tag > a:nth-of-type(1)").get("href")
                params = location.split("#")[1]
                res = parse.parse_qs(params)
                lng = res["l1"][0]
                lat = res["l2"][0]
                obj = {"img": image, "href": href, "name": rname, "lng": lng, "lat": lat, "info": info}
                self.getXiaoQuDetail(href, obj)
                # self.geo(obj)
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
