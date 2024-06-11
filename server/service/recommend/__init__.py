import flask
from service import utils
import sqlite3
import model.main as model_analyse
from openai import OpenAI

client = OpenAI(
    # defaults to os.environ.get("OPENAI_API_KEY")
    api_key="sk-esV4Eck7DXaxMBMINwZmm06DaBqmxgzkeOp9pNzgaz3f74SR",
    base_url="https://api.chatanywhere.tech/v1"
)

# 非流式响应
def gpt_35_api(messages: list):
    """为提供的对话消息创建新的回答

    Args:
        messages (list): 完整的对话消息
    """
    completion = client.chat.completions.create(model="gpt-3.5-turbo", messages=messages)
    # print(completion.choices[0].message.content)
    return completion.choices[0].message.content




def register(app: flask.Flask, data_db: sqlite3.Connection):
    @app.route('/api/recommend/video', methods=['POST'])
    def recommend_video():
        url = flask.request.form['url']
        # result = model_analyse.recommendVideo(url)
        top_text = model_analyse.topTextBarrage(url,15,10)
        # 循环遍历将top_text中的key，将key组合成一句话，用逗号隔开
        top_text_str = ''
        for item in top_text:
            top_text_str += item['key'] + ','
        top_text_str = top_text_str[:-1]

        question='推荐一些关于“'+top_text_str+'”的bilibili视频，给出视频的链接。'
        result = gpt_35_api([{'role': 'user', 'content': question}, ])




        response_data = {
            # 'toptext': top_text,
            # 'top_text_str': top_text_str,
            # 'question': question,
            'result': result,
        }
        return utils.Resp(200, response_data, 'recommend successfully').to_json()