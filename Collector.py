#!/usr/bin/python
# -*-coding：gbk-*-

import json
from helper.Grep import Grep
from urllib import parse


def getCity():
    grep = Grep()
    url = 'https://www.anjuke.com/sy-city.html'
    dic = {"href": {"isAttr": True, "grepname": "href"}, "text": {"isAttr": False, "isText": True, "grepname": "name"}}
    grep.html(url)
    selects = grep.soup.select(".city_list a")
    return grep.setSelects(selects).grep(dic, "city.json")


def collector():
    cityList = []
    try:
        file = open("./helper/city.json", mode='r')
        cityList = json.loads(file.read())
    except (OSError):
        cityList = getCity()
    for city in cityList:
        getXiaoQu(city["href"], city["name"], 1, [])


def getXiaoQu(url, name, index, ls):
    rurl = url + "/community/p" + str(index) + "?from=navigation"
    grep = Grep()
    header = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Host": url.replace("https://", ""),
        "Referer": url + "?from=navigation",
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:62.0) Gecko/20100101 Firefox/62.0"
    }
    grep.html(rurl, autoHeader=False, header=header)
    selects = grep.soup.select(".li-itemmod")
    check = grep.soup.select_one(".aNxt")
    isHasNext = check.has_attr("href")

    ls = []
    for select in selects:
        obj = {}
        image = select.select_one("img").get("src")
        xiaoqu = select.select_one(".li-info h3 a")
        name = xiaoqu.text
        href = xiaoqu.get("href")
        location = select.select_one(".bot-tag > a:nth-of-type(1)").get("href")
        params = location.split("#")[1]
        res = parse.parse_qs(params)
        lng = res["l1"][0]
        lat = res["l2"][0]
        obj = {"img": image, "href": href, "name": name, "lng": lng, "lat": lat}
        print(obj)
        ls.append(obj)

    if isHasNext:
        index = index + 1
        getXiaoQu(url, name, index, ls)
    else:
        grep.save(ls, name + ".json")
        return ls


collector()
