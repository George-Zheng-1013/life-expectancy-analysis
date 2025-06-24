#在集成终端中运行python api_server.py后开启flask后端服务
from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql

app = Flask(__name__)
CORS(app)  # 允许跨域

def get_conn():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='123456',
        database='life_expectancy_dataset',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route('/api/data', methods=['GET'])#检查路径对不对
def get_data():
    conn = get_conn()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM life_expectancy")
        data = cursor.fetchall()
    conn.close()
    return jsonify(data)

@app.route('/api/record/<int:record_id>', methods=['GET'])
def get_record(record_id):
    conn = get_conn()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM life_expectancy WHERE id=%s", (record_id,))
        data = cursor.fetchone()
    conn.close()
    return jsonify(data)

@app.route('/api/record', methods=['POST'])
def add_record():
    record = request.json
    conn = get_conn()
    with conn.cursor() as cursor:
        keys = ','.join(record.keys())
        values = ','.join(['%s'] * len(record))
        sql = f"INSERT INTO life_expectancy ({keys}) VALUES ({values})"
        cursor.execute(sql, tuple(record.values()))
        conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

@app.route('/api/record/<int:record_id>', methods=['PUT'])
def update_record(record_id):
    record = request.json
    conn = get_conn()
    with conn.cursor() as cursor:
        set_clause = ','.join([f"{k}=%s" for k in record.keys()])
        sql = f"UPDATE life_expectancy SET {set_clause} WHERE id=%s"
        cursor.execute(sql, tuple(record.values()) + (record_id,))
        conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

@app.route('/api/record/<int:record_id>', methods=['DELETE'])
def delete_record(record_id):
    conn = get_conn()
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM life_expectancy WHERE id=%s", (record_id,))
        conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(port=5000, debug=True)