# 导入类库
import re
import os
import requests
import warnings
import jieba
import jieba.analyse
import numpy as np
import pandas as pd
from PIL import Image
from model.sa import SnowNLP
from bs4 import BeautifulSoup
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import io
import model.sa.sentiment as sen
import model.sa.sentiment as supesen

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

    # 通过url中的BV，得到cid值
    bv = re.findall(r'(BV.{10})', url)[0]
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleW\
               ebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'}

    response = requests.get('https://www.bilibili.com/video/' + bv,
                            headers=headers)
    content = response.text

    cid = re.findall(r'"cid":(\d+),', content)[0]

    xml_url = f'https://comment.bilibili.com/{cid}.xml'
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


# get visualize image
def bin_visualize_(times, segment=15):
    '''
    可视化分箱后的数据。

    Parameters
    ----------
    times : pandas.Series
        弹幕对应的视频中的时间。

    segment : int, optional
        分箱的时间间隔，默认值为15。

    Returns
    -------
    segmentRangeTop : str
        弹幕时间间隔中出现次数最多的时间间隔。

    img_bytes : bytes
        图像的字节数据。
    '''

    # 根据设置的时间间隔，得到间隔的数量，并生成每个间隔对应的时间
    # times_list = times.tolist()

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

    # 可视化
    plt.figure(figsize=(15, 8))
    plt.plot(df_segmentdict['segment'], df_segmentdict['num'], marker='o')
    plt.xticks(np.arange(num_segment), np.arange(1, num_segment + 1))
    plt.xlabel(f'Segments (The length of one segment is {segment})',
               labelpad=10, size=15)
    plt.ylabel('Number', labelpad=10, size=15)
    plt.title('Number of each segment', pad=13, size=18)
    for i, value in zip(num_top_two.index, num_top_two):
        plt.text(i, value + 3, value, ha='center', va='bottom',
                 fontdict={'size': 13})

    # Save the plot to bytes buffer
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png')
    img_buffer.seek(0)
    img_bytes = img_buffer.read()
    img_buffer.close()

    return segmentRangeTop, img_bytes


def getBinVisualize_(url, segment=15):
    '''
    根据给出的B站的视频链接获取可视化后的图片。

    Parameters
    ----------
    url : str
        B站的视频链接。
        例：'https://www.bilibili.com/video/BV1wq4y1s7S5/?spm_id_from=333.337.search-card.all.click&vd_source=1d24f52164a3ed510e0b7386c010cc2e'。

    segment : int, optional
        分箱的时间间隔，默认值为15。

    Returns
    -------
    time_barrage : pandas.DataFrame
        返回一个DataFrame，包含指定时间类型的时间和弹幕。

    segmentRangeTop : str
        弹幕时间间隔中出现次数最多的时间间隔。

    img_bytes : bytes
        图像的字节数据。
    '''

    xml_url = getXML_url_(url)
    time_barrage = getBarrageTime_(xml_url)
    segmentRangeTop, img_bytes = bin_visualize_(time_barrage['time'], segment)

    return segmentRangeTop, img_bytes


# get sentiment analyse image

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


def sentiment_analyse_(url, segment=15):
    '''
    使用snownlp库对弹幕进行情感分析，并获取情感得分和标签。

    Parameters
    ----------
    url : str
        B站的视频链接。

    segment : int, optional
        分箱的时间间隔，默认值为15。

    Returns
    -------
    sa_df : pandas.DataFrame
        包含弹幕情感得分和对应标签的DataFrame。
    '''

    time_barrage, segmentRangeTop = getBinVisualize(url, segment)
    barrage = list(time_barrage['danmu'])

    # 采用snownlp库获取情感得分，并根据得分进行标签的划分
    scoreList = []
    tagList = []
    sa_df = pd.DataFrame()

    for comment in barrage:
        tag = ''
        sentiments_score = SnowNLP(comment).sentiments
        if sentiments_score < 0.5:
            tag = 'negative'
        elif sentiments_score > 0.5:
            tag = 'positive'
        else:
            tag = 'neutral'
        scoreList.append(round(sentiments_score))
        tagList.append(tag)

    sa_df['score'] = scoreList
    sa_df['tag'] = tagList
    return sa_df


def sentimentTrend_(url, segment=15):
    '''
    可视化情感趋势图。

    Parameters
    ----------
    url : str
        B站的视频链接。

    segment : int, optional
        分箱的时间间隔，默认值为15。

    Returns
    -------
    img_bytes : bytes
        图像的字节数据。
    '''

    time_barrage, segmentRangeTop = getBinVisualize(url, segment)

    # 添加类型检查和转换
    # if not isinstance(time_barrage['time'], (float, int)):
    #     time_barrage['time'] = time_barrage['time'].astype(float)

    sa_df = sentiment_analyse_(url)
    st_df = pd.concat([time_barrage['time'], sa_df], axis=1)

    times = st_df['time']
    num_segment = int(np.ceil(times.max() / segment))

    segmentList = []
    for i in range(num_segment):
        if i == 0:
            start = 0
            end = segment
            segment_range = f'{start}-{end}'
            segmentList.append(segment_range)
        else:
            start = segment * i + 1
            end = segment * (i + 1)
            segment_range = f'{start}-{end}'
            segmentList.append(segment_range)

    tagNum_df = pd.DataFrame(columns=['positive', 'neutral', 'negative'])
    for segment_range in segmentList:
        start = segment_range.split('-')[0]
        end = segment_range.split('-')[1]
        select_df = st_df[(int(start) <= st_df['time']) &
                          (st_df['time'] <= int(end))]
        tag_num = pd.DataFrame(select_df['tag'].value_counts()).T
        tagNum_df = pd.concat([tagNum_df, tag_num])
    tagNum_df = tagNum_df.fillna(0)
    tagNum_df['segment_range'] = segmentList

    # 可视化
    plt.figure(figsize=(15, 8))
    plt.plot(tagNum_df['segment_range'].astype('str'),
             tagNum_df['positive'],
             label='positive')
    plt.plot(tagNum_df['segment_range'].astype('str'),
             tagNum_df['neutral'],
             label='neutral')
    plt.plot(tagNum_df['segment_range'].astype('str'),
             tagNum_df['negative'],
             label='negative')
    plt.xticks(np.arange(num_segment), np.arange(1, num_segment + 1))
    plt.xlabel(f'Segments (The length of one segment is {segment})',
               labelpad=10, size=15)
    plt.ylabel('Number', labelpad=10, size=15)
    plt.title('Sentiment Trend Chart', pad=13, size=18)
    plt.legend()

    # Save the plot to bytes buffer
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png')
    img_buffer.seek(0)
    img_bytes = img_buffer.read()
    img_buffer.close()

    return img_bytes


# get wordcloud image
def countWordFrequency_(url, segment=15):
    '''
    使用jieba库进行分词，并统计词频。

    Parameters
    ----------
    url : str
        B站的视频链接。

    segment : int, optional
        分箱的时间间隔，默认值为15。

    Returns
    -------
    wordsFrequency_df : pandas.DataFrame
        包含词语及其对应词频的DataFrame。

    '''

    time_barrage, segmentRangeTop = getBinVisualize(url, segment)
    barrage = list(time_barrage['danmu'])

    # 加载停用词
    with open('./model/stopwords.txt', 'r', encoding='utf-8') as f:
        stopwords = f.read()

    wordsDict = {}
    for text in barrage:
        tempText = jieba.cut(text)
        for word in tempText:
            if (word not in stopwords) and (not word.isdigit()) and \
                    (not word.islower()) and (not word.isupper()):
                if word in wordsDict.keys():
                    wordsDict[word] += 1
                else:
                    wordsDict[word] = 1
            else:
                pass
    wordsFrequency_df = pd.DataFrame(wordsDict.items(),
                                     columns=['word', 'frequency'])
    return wordsFrequency_df


def generateWordCloud_(url, segment=15, mask=False, maskpath=None):
    '''
    根据词频生成词云图。

    Parameters
    ----------
    url : str
        B站的视频链接。

    segment : int, optional
        分箱的时间间隔，默认值为15。

    mask : bool, optional
        用于指定是否采用自定义背景图片。可选值为 False 和 True。
        默认值为 False，表示不采用自定义背景图片。
        如果为 True，则采用自定义背景图片。

    maskpath : str, optional
        采用的词云图的背景图片的路径。仅在 mask 参数为 True 时有效。

    savepath : str, optional
        图片保存的路径。

    Returns
    -------
    img_bytes : bytes
        图像的字节数据。
    '''

    wordsFrequency_df = countWordFrequency_(url, segment)

    # 判断采用自定义图片作为背景时，存储路径是否为None
    if mask:
        if maskpath is None:
            maskpath = os.getcwd()
        bgPicture = np.array(Image.open(maskpath))
    else:
        bgPicture = None

    fontpath = './model/fonts/微软雅黑.ttf'

    # 可视化
    wc = WordCloud(background_color='white',
                   max_words=2000,
                   mask=bgPicture,
                   font_path=fontpath,
                   width=1000,
                   height=600)
    wfDict = wordsFrequency_df.set_index(['word'])['frequency'].to_dict()
    wc.generate_from_frequencies(wfDict)

    # Save the plot to bytes buffer
    img_buffer = io.BytesIO()
    wc.to_image().save(img_buffer, format='PNG')
    img_buffer.seek(0)
    img_bytes = img_buffer.read()
    img_buffer.close()

    return img_bytes


def analyseText(text):
    # print('当前路径：', os.getcwd())
    # route=os.getcwd()
    sen.load('./model/sentiment.marshal')

    return sen.classify(text)


def topTextBarrage_(url, segment=15, topKey=10):
    '''
    获取全文弹幕中权重最高的前十个关键词及其对应的TextRank算法数值。

    Parameters
    ----------
    url : str
        B站的视频链接。
        例：'https://www.bilibili.com/video/BV1wq4y1s7S5/?spm_id_from=333.337.search-card.all.click&vd_source=1d24f52164a3ed510e0b7386c010cc2e'。

    segment : int, optional
        分箱的时间间隔，默认值为15。

    Returns
    -------
    keyTop_json : str
        包含权重最高的前十个关键词及其对应的TextRank算法数值的JSON字符串。

    使用 jieba.analyse.textrank 函数对拼接后的弹幕文本进行关键词提取。这里使用了停用词表，并限制了词性（只考虑名词、动词、形容词等）。
    提取前 10 个权重最高的关键词及其对应的权重值。
    '''

    time_barrage, segmentRangeTop = getBinVisualize(url, segment)
    sentence = '\n'.join(time_barrage['danmu'])

    allowPOS = ('n', 'nr', 'ns', 'nz', 'v', 'vd', 'vn', 'a', 'q')
    jieba.analyse.set_stop_words('./model/stopwords.txt')
    keyTop_10 = jieba.analyse.textrank(sentence,
                                       topK=topKey,
                                       withWeight=True,
                                       allowPOS=allowPOS)
    keyTop_df = pd.DataFrame(keyTop_10,
                             columns=['key', 'textrank'])

    # Convert DataFrame to a list of dictionaries
    keyTop_list = keyTop_df.to_dict(orient='records')

    # Remove backslashes from keys
    for item in keyTop_list:
        item['key'] = item['key'].replace('\\', '')

    for item in keyTop_list:
        item['probability'] = analyseText(item['key'])
        if item['probability'] < 0.5:
            item['sentiment'] = '消极'
        elif item['probability'] > 0.5:
            item['sentiment'] = '积极'
        else:
            item['sentiment'] = '中立'

    return keyTop_list


def superiorText(text):
    supesen.load('./model/superior.marshal')
    analyseResult = supesen.classify(text)
    if analyseResult < 0.5:
        supesen.add_training_negdata(text)
    elif analyseResult > 0.5:
        supesen.add_training_posdata(text)
    supesen.save('./model/superior.marshal')
    return analyseResult


def topTextBarrage(url, segment=15, topKey=10):
    '''
    获取全文弹幕中权重最高的前十个关键词及其对应的TextRank算法数值。

    Parameters
    ----------
    url : str
        B站的视频链接。
        例：'https://www.bilibili.com/video/BV1wq4y1s7S5/?spm_id_from=333.337.search-card.all.click&vd_source=1d24f52164a3ed510e0b7386c010cc2e'。

    segment : int, optional
        分箱的时间间隔，默认值为15。

    Returns
    -------
    keyTop_json : str
        包含权重最高的前十个关键词及其对应的TextRank算法数值的JSON字符串。

    '''

    time_barrage, segmentRangeTop = getBinVisualize(url, segment)
    sentence = '\n'.join(time_barrage['danmu'])

    allowPOS = ('n', 'nr', 'ns', 'nz', 'v', 'vd', 'vn', 'a', 'q')
    jieba.analyse.set_stop_words('./model/stopwords.txt')
    keyTop_10 = jieba.analyse.textrank(sentence,
                                       topK=topKey,
                                       withWeight=True,
                                       allowPOS=allowPOS)
    keyTop_df = pd.DataFrame(keyTop_10,columns=['key', 'textrank'])

    # Convert DataFrame to a list of dictionaries
    keyTop_list = keyTop_df.to_dict(orient='records')

    # Remove backslashes from keys
    for item in keyTop_list:
        item['key'] = item['key'].replace('\\', '')

    return keyTop_list


def pieChartData(url,segment=15):
    sa_df = sentiment_analyse_(url)
    positive_num = len(sa_df[sa_df['tag'] == 'positive'])
    negative_num = len(sa_df[sa_df['tag'] == 'negative'])
    neutral_num = len(sa_df[sa_df['tag'] == 'neutral'])

    return positive_num,negative_num,neutral_num

