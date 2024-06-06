import flask
from service import utils
import sqlite3
import io
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


def gpt_35_api_stream(messages: list):
    """为提供的对话消息创建新的回答 (流式传输)

    Args:
        messages (list): 完整的对话消息
    """
    stream = client.chat.completions.create(
        model='gpt-3.5-turbo',
        messages=messages,
        stream=True,
    )
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            # print(chunk.choices[0].delta.content, end="")
            return chunk.choices[0].delta.content
    return None


def register(app: flask.Flask, data_db: sqlite3.Connection):
    @app.route('/api/gpt/analyse', methods=['POST'])
    def analyse():
        text = flask.request.form['text']
        text += '。这句话是积极的还是消极的?'
        messages = [{'role': 'user', 'content': text}, ]
        result = gpt_35_api(messages)

        response_data = {
            'result': result,
            # 'text':text
        }
        return utils.Resp(200, response_data, 'analyse successfully').to_json()

    @app.route('/api/gpt/chat', methods=['POST'])
    def chat():
        text = flask.request.form['text']
        messages = [{'role': 'user', 'content': text}, ]
        result = gpt_35_api(messages)

        response_data = {
            'result': result,
        }
        return utils.Resp(200, response_data, 'chat successfully').to_json()