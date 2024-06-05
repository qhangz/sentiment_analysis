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
            as_attachment=True,
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

        # Prepare response data
        response_data = {
            'probability': result,
        }
        return utils.Resp(200, response_data, 'register successfully').to_json()