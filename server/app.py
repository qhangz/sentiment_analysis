from flask import Flask
import flask_cors
import sqlite3
import os
from service.data import create_database
import service.analyse


app = Flask(__name__)
# CORS
flask_cors.CORS(app,supports_credentials=True)

# 保存原始的工作目录
original_dir = os.getcwd()
# 切换到 ./service/data 文件夹下
os.chdir('./service/data')
# 调用创建数据库的函数
create_database()
# 恢复到原始的工作目录
os.chdir(original_dir)

data_db = sqlite3.connect('./service/data/data.db', check_same_thread=False)
# 设置为可多线程访问
data_db.isolation_level = None

# 服务注册
service.analyse.register(app, data_db)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"




if __name__ == '__main__':
    app.run()
