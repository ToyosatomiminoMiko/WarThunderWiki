# -*- coding:UTF-8 -*-

import requests
from lxml import etree
from bs4 import BeautifulSoup

"""
文件说明:

header:
    'Last-Modified'是获取的服务器反馈的页面更新时间,
    'If-Modified-Since'是设置上次的'Last-Modified',
    若'If-Modified-Since'和本次的'Last-Modified'相同,
    则返回的status_code为304,不相同为200.


"""


w = """

1.首次运行;
2.非首次运行;
->
"""

headers0 = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/56.0.2924.87 Safari/537.36'}

url0 = 'https://wiki.warthunder.com/M256_(120_mm)'


def main_request(url, headers):
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


def write(s):  # 源码写入函数
    with open('M256/data.txt', 'w+', encoding="utf-8") as f:
        f.writelines(s)
        print("已下载html源码")


def read_html(headers, url):  # 非首次使用函数
    with open('M256/data.txt', 'r', encoding="utf-8") as f:
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


def main():
    k = input(w)
    if k == "1":
        ls = main_request(url0, headers0)  # 主请求信息表
        name = ls[1]  # 提取对象
        info_d = {url0: header_time(name)}
        print(f'If-Modified-Since:{info_d}')
        write([str(info_d), "\n", ls[0]])  # 写入源码
    elif k == "2":
        read_html(headers0, url0)


if __name__ == '__main__':
    main()
