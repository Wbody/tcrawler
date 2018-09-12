#!/usr/bin/python
# -*-coding：gbk-*-

import random
import demjson
import os


def randomProxy(isPrint=True):
    curr_dir = os.path.dirname(os.path.realpath(__file__))
    file = open(curr_dir + os.sep + ".." + os.sep + "conf" + os.sep + "ip.json")
    jsontext = file.read()
    file.close()
    ip_pool = demjson.decode(jsontext)
    ip = ip_pool[random.randrange(0, len(ip_pool))]
    proxy_ip = "{proxy}://{ip}:{port}"
    proxy = "http"
    proxy_ip = proxy_ip.format(proxy=proxy, ip=ip["ip"], port=ip["port"])
    proxies = {proxy: proxy_ip}
    if isPrint:
        print(proxies)
    return proxies
