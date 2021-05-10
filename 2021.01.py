# -*- coding:UTF-8 -*-

import requests
from lxml import etree
from bs4 import BeautifulSoup
import re
import numpy as np
import pandas as pd

"""
文件说明:

header:
    'Last-Modified'是获取服务器反馈的页面更新时间,
    'If-Modified-Since'被设置成上次的'Last-Modified',
    若'If-Modified-Since'和'Last-Modified'相同,
    则返回的status_code为304,不相同为200.
    
因此,无需每一次提交请求,HTML源码在第一次请求时就会保存在本地,
被同时保存下来的还有'Last-Modified',
用作下一次提交请求时放进header的'If-Modified-Since'中,

"""

w = """
WarThunder_Wikipedia_WebSpider:
1.首次运行;
2.非首次运行;
3.读取本地html并解析数据;
->
"""

headers0 = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/56.0.2924.87 Safari/537.36'}

url0 = 'https://wiki.warthunder.com/M256_(120_mm)'

path_M256 = 'cannon/M256.txt'


def main_request(url, headers):  # 第一次请求html源码及header
    z = requests.get(url, headers=headers)
    html = z.content.decode('utf-8')  # 设置编码

    # 解析
    html = etree.HTML(html, parser=etree.HTMLParser(encoding='utf-8'))
    # 修正html
    result = etree.tostring(html, encoding='utf-8', pretty_print=True, method='html')
    # 转换为字符串
    html = result.decode('utf-8')

    # 格式化
    soup = BeautifulSoup(html, 'html.parser')  # 创建soup
    html = soup.prettify()  # 格式化html
    return [html, z]  # 返回已格式化的html源码


def header_time(name0):
    last_modified = name0.headers['Last-Modified']  # 获取更新时间
    ft = f'{last_modified}'
    return ft


def write(s, path):  # 源码写入函数
    with open(path, 'w+', encoding="utf-8") as f:
        f.writelines(s)
        print("已下载html源码")


def read_html_line1(headers, url, path):  # 非首次使用读取上回时间の函数
    with open(path, 'r', encoding="utf-8") as f:
        hd = eval(f.readline())
    headers['If-Modified-Since'] = hd[url]  # 读取的上次更新时间
    print(headers)
    z = requests.get(url, headers=headers)  # 重新提交请求
    i = z.status_code  # int
    print(i)
    if i == 304:  # 判断网页是否有更新
        print("网页未更新")
        main()
    else:
        print("页已更新,可以更新本地文件")
        main()


def read_html_all(path, ):  # 非首次使用读取上回html源码の函数
    with open(path, 'r', encoding="utf-8") as html_local:  # 读取文件
        html_ls = html_local.readlines()[1:]
    return ''.join(html_ls)


def parsing_html(html):  # 解析本地HTML
    soup = BeautifulSoup(html, 'html.parser')  # 创建soup
    data = soup.find_all("td")
    # 索引数据
    mm_data = data[0:4 * 8]  # 穿深数据
    # info_data = data[4 * 8:4 * 8 + 40]

    # 提取数据
    d0 = {}
    for i in range(int(len(mm_data) / 8)):
        data_name = re.sub(r'<td>|</td>|\s', '', str(data[i * 8]))  # 删除标签和空字符
        info_s = list(data[i * 8 + 1:i * 8 + 8])
        info_s1 = []
        for inf in info_s:
            inf = re.sub(r'<td>|</td>|\s', '', str(inf))  # 删除标签和空字符
            info_s1.append(inf)
        d0[data_name] = info_s1  # 创建字典

    # 构建DataFrame
    df = pd.DataFrame(d0, index=['type', '10m', '100m', '500m', '1000m', '1500m', '2000m'])  # 列名和值的定义
    return df


def main():
    k = input(w)
    if k == "1":
        ls = main_request(url0, headers0)  # 主请求信息表
        name = ls[1]  # 提取对象
        info_d = {url0: header_time(name)}
        print(f'If-Modified-Since:{info_d}')
        write([str(info_d), "\n", ls[0]], path_M256)  # 写入源码
    elif k == "2":
        read_html_line1(headers0, url0, path_M256)  # 查看页面是否更新
    elif k == "3":
        local_html = read_html_all(path_M256)
        print(parsing_html(local_html))  # 输出解析出的数据
    else:
        print("输入错误")
        main()


if __name__ == '__main__':
    main()
