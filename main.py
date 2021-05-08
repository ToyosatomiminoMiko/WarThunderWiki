#!usr/bin/env python3
# -*- coding:UTF-8 -*-

import numpy as np
import pandas as pd
import requests

from lxml import etree
import re
from bs4 import BeautifulSoup

# ctrl+F Xpath查找器
"""
说明:
爬取M256滑膛炮
 M256 Rh 120mm L/44
"""

# 请求信息
url = "https://wiki.warthunder.com/M256_(120_mm)"
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36 Edg/89.0.774.77"
headers = {"User-Agent": user_agent}

# 请求
r = requests.get(url, headers=headers)
html = r.content.decode('utf-8')

# 解析
html = etree.HTML(html, parser=etree.HTMLParser(encoding='utf-8'))
# 修正html
result = etree.tostring(html, encoding='utf-8', pretty_print=True, method='html')
# 转换为字符串
html = result.decode('utf-8')
# Xpath有毒
# l=html.xpath("//*[@id=\"mw-content-text\"]/div[2]/table[1]/tbody/tr/td/text()")
# print(l)

# 格式化
soup = BeautifulSoup(html, 'html.parser')
html = soup.prettify()
data = soup.find_all("td")
# 索引数据
mm_data = data[0:4 * 8]
info_data = data[4 * 8:4 * 8 + 40]

d0 = {}
for i in range(int(len(mm_data) / 8)):
    data_name = re.sub(r'<td>|</td>', '', str(data[i * 8]))
    info_s=list(data[i * 8 + 1:i * 8 + 8])
    info_s1=[]
    for inf in info_s:
        inf = re.sub(r'<td>|</td>|\s', '', str(inf))
        info_s1.append(inf)
    d0[data_name] = info_s1

#print(d0)

# 定义列
df = pd.DataFrame(d0, index=['type', '10m', '100m', '500m', '1000m', '1500m', '2000m'])  # 列名和值的定义
print(df)
# print(mm_data, info_data, sep="\n")
"""
print(html)
# re
fd = r'\d+'
datalist = list(re.findall(fd, html))
print(datalist)
"""
