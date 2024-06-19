import flask
from service import utils
import sqlite3
import io
from openai import OpenAI
import model.main as model_analyse
from transformers import AutoTokenizer, AutoModel
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


def chatGLM(messages):
    tokenizer = AutoTokenizer.from_pretrained("model/chatglm", trust_remote_code=True)
    # model = AutoModel.from_pretrained("model/chatglm", trust_remote_code=True, device='cuda')
    model = AutoModel.from_pretrained("model/chatglm", trust_remote_code=True, ignore_mismatched_sizes=True)
    model = model.eval()
    response, history = model.chat(tokenizer, messages, history=[])
    print(response)
    return response


def register(app: flask.Flask, data_db: sqlite3.Connection):
    @app.route('/api/gpt/analyse', methods=['POST'])
    def analyse():
        text = flask.request.form['text']
        text += '。这句话是积极的还是消极的?'
        messages = [{'role': 'user', 'content': text}, ]
        result = gpt_35_api(messages)

        # 如果result中包含"积极"或"消极"，则提取出来
        if '积极' in result:
            sentiment = 'positive'
            model_analyse.gptSuperiorText(text,sentiment)
        elif '消极' in result:
            sentiment = 'negative'
            model_analyse.gptSuperiorText(text,sentiment)

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

    @app.route('/api/glm/chat', methods=['POST'])
    def chatglm():
        text = flask.request.form['text']
        response=chatGLM(text)
        response_data = {
            'response': response,
        }
        return utils.Resp(200, response_data, 'chat successfully').to_json()
