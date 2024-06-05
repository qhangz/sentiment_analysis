# server

## run serve
flask --app appName run
or
flask run (if appName = app.py)

## venv
```shell
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
venv\Scripts\activate

# 退出虚拟环境
deactivate

# 安装依赖
pip install -r requirements.txt

```

## sqlite3
```sh
# enter db
sqlite3 demo.db

# show tables
.table

# other (select,update,delete,insert)
select * from users;

# quit
.quit

# descript table
pargma table_info(tableName)
```

