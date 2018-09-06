#!/usr/bin/python
# -*-coding：gbk-*-

import json
from helper.CitysList import getCity

def collector():
    cityList = []
    try:
        file = open("city.json", mode='r')
        cityList = json.loads(file.read())
    except (OSError):
        cityList = getCity()
    print(cityList)

collector()