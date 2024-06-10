import flask
from service import utils
import sqlite3
import model.main as model_analyse
import io


def register(app: flask.Flask, data_db: sqlite3.Connection):
    @app.route('/api/superior/text', methods=['POST'])
    def text_superior():
        text = flask.request.form['text']
        result = model_analyse.superiorText(text)
        if result < 0.5:
            sentiment = '消极'
        elif result > 0.5:
            sentiment = '积极'
        else:
            sentiment = '中立'

        response_data = {
            'probability': result,
            'sentiment': sentiment
        }
        return utils.Resp(200, response_data, 'analyse successfully').to_json()

