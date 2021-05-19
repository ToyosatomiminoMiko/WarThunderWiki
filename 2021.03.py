# -*- coding:UTF-8 -*-

import requests
from lxml import etree
from bs4 import BeautifulSoup
import re
# import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import time
from sqlalchemy import create_engine

"""
说明:

有关header:
'Last-Modified'是获取服务器的页面"最后修改"时间.
当'If-Modified-Since'被设置成上次的'Last-Modified'时,
若'If-Modified-Since'和'Last-Modified'相同,则返回的status_code为304,不相同为200. 
因此,无需每一次提交请求,从HTML源码中提取的数据在第一次请求时就会保存在本地SQL,被同时保存下来的还有'Last-Modified',
用作下一次提交请求时放进header的'If-Modified-Since'中用于检查页面修改情况.
"""

# 解决保存图像是负号'-'显示为方块的问题,或者转换负号为字符串 csdn:qq_40195360
mpl.rcParams['font.sans-serif'] = ['KaiTi']
mpl.rcParams['font.serif'] = ['KaiTi']
mpl.rcParams['axes.unicode_minus'] = False

urls = {'M256': 'https://wiki.warthunder.com/M256_(120_mm)',
        'ZPT98': 'https://wiki.warthunder.com/ZPT98_(125_mm)',
        '2A46M_1': 'https://wiki.warthunder.com/2A46M-1_(125_mm)',
        # '2A46M_1':'https://wiki.warthunder.com/2A46M-5_(125_mm)',  # 无数据
        'OTO_Breda_120_44': 'https://wiki.warthunder.com/OTO_Breda_120/44_(120_mm)',
        'GIAT_CN120_26_F1': 'https://wiki.warthunder.com/GIAT_CN120-26_F1_(120_mm)',
        'Rh120_L_44': 'https://wiki.warthunder.com/Rh120_L/44_(120_mm)'}
# ['M256','ZPT98','2A46M_1','2A46M_1','OTO_Breda_120_44','GIAT_CN120_26_F1','Rh120_L_44']

w = """
WarThunder_Wikipedia_WebSpider:
0.帮助;
1.首次运行(提交请求获取数据并保存至MySQL);
2.读取本地MySQL数据并绘图;
3.非首次运行(从MySQL读取数据并检查页面是否更新);
┏━━━输入:
"""

headers0 = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/56.0.2924.87 Safari/537.36'}

engine = create_engine('mysql+pymysql://root:admini@localhost:3306/warthunderwiki')


def sleep(s):  # 等待时间
    time.sleep(s)


def main_request(url, headers):  # 第一次请求html源码及header,并提取出数据
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
    data0 = soup.find_all("table")  # 筛选table
    # 还原html
    tags0 = list(data0)[0]  # 筛选出第一个table标签
    tags = []
    for tag in tags0:  # 将soup内所有标签还原为str
        tags.append(str(tag))
    data = ''.join(tags)  # 重新构造html
    # 再格式化
    soup = BeautifulSoup(data, 'html.parser')  # 再创建soup
    data = soup.find_all("td")  # 筛选td
    # 索引数据
    mm_data = data  # [0:4 * 8]  # 穿深数据

    # 提取数据
    d0 = []
    for i in range(int(len(mm_data) / 8)):
        data_name = re.sub(r'<td>|</td>|\s', '', str(data[i * 8]))  # key:删除标签和空字符(炮弹名称)
        info_s = list(data[i * 8 + 1:i * 8 + 8])
        info_s1 = [i, data_name]  # 炮弹数据列表
        for inf in info_s:
            inf = re.sub(r'<td>|</td>|\s', '', str(inf))  # value:删除标签和空字符(炮弹类型及数据)
            if inf.isdigit():
                inf = int(inf)  # 数字转换为int类型
            info_s1.append(inf)  # 创建列表
        d0.append(info_s1)
    # 构建DataFrame
    df = pd.DataFrame(d0, columns=['index', 'name', 'type', 10, 100, 500, 1000, 1500, 2000])  # 列名和值的定义
    print(df)
    return [df, z]  # 返回DataFrame和headers


def read_html_line1(headers, url, engine0):  # 非首次使用从MySQL读取上回时间の函数
    sql_cmd = f"SELECT * FROM last_modified_s"
    df = pd.read_sql(sql=sql_cmd, con=engine0)  # 读取MySQL
    d=dict(zip(list(df['name']), list(df['Last-Modified'])))  # 构建映射
    headers['If-Modified-Since'] = d[url]  # 读取的上次更新时间
    z = requests.get(urls[url], headers=headers)  # 重新提交请求
    i = z.status_code  # int
    print(f'响应:{i}')
    if i == 304:  # 判断网页是否有更新
        print(f"{url}:网页未更新!")
    else:
        print(f"{url}:页面已更新,可以更新本地文件!")


def cannon_plot(df1):  # 读取本地MySQL并绘图
    df1.plot(kind='line', marker="+")
    plt.xlabel(u'距离(单位:m)', fontsize=14)  # 设置x轴
    plt.ylabel(u'穿深(单位:mm)', fontsize=14)  # 设置y轴
    plt.show()


def read_cannon_mysql(engine0, name):  # 读取数据库火炮信息
    df = pd.read_sql_query(f'select * from {name};', engine0)
    return df


def read_time_mysql(engine0, i):  # 读出mysql时间数据
    sql_cmd = f"SELECT * FROM {i}"
    df = pd.read_sql(sql=sql_cmd, con=engine0)
    return df


def save_data_sql(data, name):  # 保存火炮或时间数据到mysql
    data.to_sql(name.lower(), engine, index=False, if_exists='replace')
    print("数据已保存至MySQL!")


def read_lm_headers(ls, url0):  # 从主请求返回的列表中提取"Last-Modified(最后修改)"
    name = ls[1]  # 提取对象
    last_modified = name.headers['Last-Modified']  # 获取更新时间
    return [url0, f'{last_modified}']


def main():  # 主函数
    print(w, end="")
    k = input("┗━")
    if k == "1":
        time_s = {}
        i = 1
        for url0 in urls:
            ls = main_request(urls[url0], headers0)  # 主请求信息表
            time_s[i] = read_lm_headers(ls, url0)  # 创建时间DataFrame
            print(ls[0])  # 输出火炮数据DataFrame
            save_data_sql(ls[0], url0)  # 保存火炮数据到MySQL
            sleep(0)
            i += 1
        # print(f'Last-Modified(最后修改):{time_s}')
        data_df = pd.DataFrame(time_s, index=['name', 'Last-Modified'])  # 列名和值的定义
        data_df = pd.DataFrame(data_df.values.T, index=data_df.columns, columns=data_df.index)
        print(data_df)
        save_data_sql(data_df, 'Last_Modified_s')
        main()

    elif k == "2":
        print(urls)
        i = input("输入需要查询的火炮数据:")
        df = read_cannon_mysql(engine, i)  # 读取数据
        df = pd.DataFrame(df.values.T, index=df.columns, columns=df['name'])
        df = df.drop(['index', 'type', 'name'], axis=0)
        print(df)
        cannon_plot(df)  # 读取数据绘图
        main()

    elif k == "3":  # 读取MySQL中的时间# 查看页面是否更新
        for url in urls:
            read_html_line1(headers0, url, engine)

        main()

    elif k == "0":
        s = """
        帮助:
        1.提交请求获取数据并保存至MySQL
        保存的数据将包含:
        火炮炮弹数据,页面最后修改时间
        """
        print(s)

    else:
        print("输入错误!")

        main()


if __name__ == '__main__':
    main()
