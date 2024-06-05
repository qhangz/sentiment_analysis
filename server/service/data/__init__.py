import sqlite3
import os
from flask import Flask
import base64

app = Flask(__name__)

DATABASE = 'data.db'

def create_database():
    try:
        # 检查数据库文件是否存在
        if not os.path.exists(DATABASE):
            db = sqlite3.connect(DATABASE)
            print("Opened database successfully")
            # 从 schema.sql 文件中读取 SQL 命令并执行
            with app.open_resource('schema.sql', mode='r') as f:
                db.cursor().executescript(f.read())
            print("Table created successfully")

            db.close()
        else:
            print("Database file already exists, skipping creation")
    except Exception as e:
        print("Error:",e)

if __name__ == '__main__':
    create_database()