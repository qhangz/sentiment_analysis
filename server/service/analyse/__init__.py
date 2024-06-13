import flask
from service import utils
import sqlite3
import model.main as model_analyse
import io


def register(app: flask.Flask, data_db: sqlite3.Connection):
    @app.route('/api/analyse/visualize', methods=['POST'])
    def get_visualize():
        url = flask.request.form['url']
        segmentRangeTop, img_bytes = model_analyse.getBinVisualize_(url)

        # Prepare response data
        response_data = {
            'segmentRangeTop': segmentRangeTop,
            # 'barrage_data': time_barrage.to_dict()  # Convert DataFrame to dictionary
        }

        # Return image as response
        return flask.send_file(
            io.BytesIO(img_bytes),
            mimetype='image/png',  # Set MIME type to PNG
            as_attachment=False,
            download_name='result_image.png'
        )
        # # Convert image bytes to base64 string
        # img_base64 = utils.convert_bytes_to_base64(img_bytes)
        #
        # # Prepare response data
        # response_data = {
        #     'segmentRangeTop': segmentRangeTop,
        #     'img_base64': img_base64,
        #     'barrage_data': time_barrage.to_dict()  # Convert DataFrame to dictionary
        # }
        #
        # # Return response
        # return flask.jsonify(response_data)
        # return utils.Resp(200, None, 'test successfully').to_json()

    @app.route('/api/analyse/sentiment', methods=['POST'])
    def sentiment_analyse():
        url = flask.request.form['url']
        img_bytes = model_analyse.sentimentTrend_(url)

        # Return image as response
        return flask.send_file(
            io.BytesIO(img_bytes),
            mimetype='image/png',  # Set MIME type to PNG
            as_attachment=True,
            download_name='result_image.png'
        )

    @app.route('/api/analyse/wordcloud', methods=['POST'])
    def wordcloud():
        url = flask.request.form['url']
        img_bytes = model_analyse.generateWordCloud_(url)

        # Return image as response
        return flask.send_file(
            io.BytesIO(img_bytes),
            mimetype='image/png',  # Set MIME type to PNG
            as_attachment=True,
            download_name='result_image.png'
        )

    @app.route('/api/analyse/text', methods=['POST'])
    def text_analyse():
        text = flask.request.form['text']
        result = model_analyse.analyseText(text)
        if result < 0.5:
            sentiment = '消极'
        elif result > 0.5:
            sentiment = '积极'
        else:
            sentiment = '中立'

        # Prepare response data
        response_data = {
            'probability': result,
            'sentiment': sentiment
        }
        return utils.Resp(200, response_data, 'analyse successfully').to_json()

    @app.route('/api/analyse/toptext', methods=['POST'])
    def top10_text():
        url = flask.request.form['url']
        top_text = model_analyse.topTextBarrage_(url,15,10)
        return utils.Resp(200, top_text, 'analyse successfully').to_json()

    @app.route('/api/analyse/piechart', methods=['POST'])
    def pie_chart():
        url = flask.request.form['url']
        positive_num, negative_num,neutral_num = model_analyse.pieChartData(url)

        response_data= {
            'positive_num': positive_num,
            'negative_num': negative_num,
            'neutral_num': neutral_num,
        }
        return utils.Resp(200, response_data, 'analyse successfully').to_json()
