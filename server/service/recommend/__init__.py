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
    def recommend_vedio():
        url = flask.request.form['url']
        # result = model_analyse.recommendVideo(url)
        top_text = model_analyse.topTextBarrage_(url,15,20)
        response_data = {
            'toptext': top_text
        }
        return utils.Resp(200, response_data, 'analyse successfully').to_json()