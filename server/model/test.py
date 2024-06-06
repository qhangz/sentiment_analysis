import main
import jieba.analyse
import pandas as pd
import re
import os
import requests
import warnings
import jieba
import jieba.analyse
import numpy as np
import pandas as pd
from PIL import Image
from sa import SnowNLP
from bs4 import BeautifulSoup
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import io
import sa.sentiment as sen
# 设置库中的参数
warnings.filterwarnings('ignore')
plt.rcParams['font.size'] = 13
plt.rcParams['font.sans-serif'] = 'Arial'


def getXML_url_(url):
    '''
    根据B站的视频链接获取弹幕对应的XML文件的链接。

    Parameters
    ----------
    url : str
        B站的视频链接。
        例：'https://www.bilibili.com/video/BV1wq4y1s7S5/?spm_id_from=333.337.search-card.all.click&vd_source=1d24f52164a3ed510e0b7386c010cc2e'。

    Returns
    -------
    xml_url : str
        视频链接对应的XML文件的链接。

    '''
    # print('begin get xml')
    # 通过url中的BV，得到cid值
    bv = re.findall(r'(BV.{10})', url)[0]
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleW\
               ebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'}

    response = requests.get('https://www.bilibili.com/video/' + bv,
                            headers=headers)
    content = response.text
    # print(cid)
    cid = re.findall(r'"cid":(\d+),', content)[0]

    xml_url = f'https://comment.bilibili.com/{cid}.xml'
    # print('finish xml url')
    return xml_url


def getBarrageTime_(url, type_='Video'):
    '''
    根据弹幕对应的XML文件的链接获取指定的时间类型的时间和弹幕。

    Parameters
    ----------
    url : str
        弹幕对应的XML文件的链接。
        例：'https://comment.bilibili.com/375203456.xml'。

    type_ : str, optional
        用于指定获取时间的类型。可选值为 'Video' 和 'Real'。
        默认值为 'Video'，表示获取视频中的时间。
        'Real' 表示获取实际中的时间。

    Raises
    ------
    TypeError
        若输入的type_参数不是 'Video' 或 'Real'，则会生成该错误。

    Returns
    -------
    time_barrage : pandas.DataFrame
        返回一个DataFrame，包含指定时间类型的时间和弹幕。

    '''

    # 获取并解析xml文件
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleW\
               ebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'}

    response = requests.get(url, headers=headers)
    response.encoding = response.apparent_encoding
    xml = response.text

    soup = BeautifulSoup(xml, 'xml')
    content_all = soup.find_all(name='d')

    # 获取弹幕的时间和内容，并分别存储到对应的列表中
    timeList = []
    textList = []

    for comment in content_all:
        data = comment.attrs['p']
        if type_ == 'Video':
            time = float(data.split(',')[0])
            text = comment.text
        elif type_ == 'Real':
            timeStamp = data.split(',')[4]
            time = pd.to_datetime(timeStamp, unit='s')
            text = comment.text
        else:
            raise TypeError('This method is not defined.')
        # text = comment.text

        timeList.append(time)
        textList.append(text)

    time_barrage = pd.DataFrame({'time': timeList,
                                 'danmu': textList})
    return time_barrage

def bin_visualize(times, segment=15):
    num_segment = int(np.ceil(times.max() / segment))
    segmentDict = {}
    for i in range(num_segment):
        if i == 0:
            start = 0
            end = segment
            segment_range = f'{start}-{end}'
            segmentDict[segment_range] = 0
        else:
            start = segment * i + 1
            end = segment * (i + 1)
            segment_range = f'{start}-{end}'
            segmentDict[segment_range] = 0

    # 获得每个时间间隔中的弹幕数量
    for segment_range in segmentDict.keys():
        start_key = segment_range.split('-')[0]
        end_key = segment_range.split('-')[1]
        for time in times:
            if int(start_key) <= round(time) <= int(end_key):
                segmentDict[segment_range] = segmentDict[segment_range] + 1

    df_segmentdict = pd.DataFrame(segmentDict.items(),
                                  columns=['segment', 'num'])
    num_top_two = df_segmentdict['num'].nlargest(2)
    segmentRangeTop = df_segmentdict.loc[df_segmentdict['num'].idxmax(), 'segment']

    return segmentRangeTop


def getBinVisualize(url, segment=15):
    xml_url = getXML_url_(url)
    time_barrage = getBarrageTime_(xml_url)
    segmentRangeTop = bin_visualize(time_barrage['time'], segment)
    return time_barrage, segmentRangeTop

def analyseText(text):
    # print('当前路径：', os.getcwd())
    # route=os.getcwd()
    sen.load('./sentiment.marshal')
    return sen.classify(text)

if __name__ == '__main__':
    url='https://www.bilibili.com/video/BV1BK411L7DJ/?vd_source=2c028219bde53dd725fd2b228dc2d5df'
    segment = 15
    time_barrage, segmentRangeTop = getBinVisualize(url, segment)
    sentence = '\n'.join(time_barrage['danmu'])
    print('sentence:',sentence)
    allowPOS = ('n', 'nr', 'ns', 'nz', 'v', 'vd', 'vn', 'a', 'q')
    jieba.analyse.set_stop_words('./stopwords.txt')
    keyTop_10 = jieba.analyse.textrank(sentence,
                                       topK=10,
                                       withWeight=True,
                                       allowPOS=allowPOS)
    # print('keyTop_10:',keyTop_10)
    keyTop_df = pd.DataFrame(keyTop_10,
                             columns=['key', 'value of textrank'])

    # print('keyTop_df:',keyTop_df)
    # Convert DataFrame to a list of dictionaries
    keyTop_list = keyTop_df.to_dict(orient='records')
    # print('keyTop_list:',keyTop_list)
    # Remove backslashes from keys
    for item in keyTop_list:
        item['key'] = item['key'].replace('\\', '')
    # print('list',keyTop_list)

    # 为keyTop_list添加probability的值，通过调用analyseText函数
    for item in keyTop_list:
        item['probability'] = analyseText(item['key'])
        if item['probability'] < 0.5:
            item['sentiment'] = '消极'
        elif item['probability'] > 0.5:
            item['sentiment'] = '积极'
        else:
            item['sentiment'] = '中立'

    print('result',keyTop_list)
    # 将keyTop_list转换为DataFrame
    # keyTop_df = pd.DataFrame(keyTop_list)
    # print(keyTop_df)
