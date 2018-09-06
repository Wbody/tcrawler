#!/usr/bin/python
# -*-coding：gbk-*-

import random
import demjson


def randomProxy():
    file = open("ip.json")
    jsontext = file.read()
    file.close()
    ip_pool = demjson.decode(jsontext)
    ip = ip_pool[random.randrange(0, len(ip_pool))]
    proxy_ip = "{proxy}://{ip}:{port}"
    proxy_ip = proxy_ip.format(proxy=ip["proxy"], ip=ip["ip"], port=ip["port"])
    proxies = {ip["proxy"]: proxy_ip}
    print(proxies)
    return proxies


