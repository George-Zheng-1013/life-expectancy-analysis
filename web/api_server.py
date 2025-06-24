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

# 字段名映射
FIELD_MAPPING = {
    'Country': '国家',
    'Year': '年份', 
    'Life_expectancy': '预期寿命',
    'Adult_mortality': '成人死亡率',
    'Infant_deaths': '婴儿死亡数',
    'Alcohol_consumption': '酒精消费',
    'Under_five_deaths': '五岁以下死亡数',
    'Hepatitis_B': '乙肝疫苗接种率',
    'Measles': '麻疹病例数',
    'BMI': 'BMI指数',
    'Polio': '脊髓灰质炎疫苗接种率',
    'Diphtheria': '白喉疫苗接种率',
    'Incidents_HIV': 'HIV/AIDS死亡率',
    'GDP_per_capita': 'GDP人均',
    'Population_mln': '人口数量(百万)',
    'Thinness_ten_nineteen_years': '10-19岁消瘦率',
    'Thinness_five_nine_years': '5-9岁消瘦率',
    'Schooling': '受教育年限',
    'Economy_status_Developed': '发达国家',
    'Economy_status_Developing': '发展中国家',
    'Status': '发展状态_数值'
}

REVERSE_FIELD_MAPPING = {v: k for k, v in FIELD_MAPPING.items()}

@app.route('/api/data', methods=['GET'])#检查路径对不对
def get_data():
    conn = get_conn()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM life_expectancy")
        raw_data = cursor.fetchall()
        # 将中文字段名转换为英文字段名以匹配前端
        data = []
        for row in raw_data:
            new_row = {}
            for chinese_key, english_key in REVERSE_FIELD_MAPPING.items():
                if chinese_key in row:
                    new_row[english_key] = row[chinese_key]
            # 保留从数据库中获取的原始ID
            if 'id' in row:
                new_row['id'] = row['id']
            data.append(new_row)
    conn.close()
    return jsonify(data)

@app.route('/api/record/<int:record_id>', methods=['GET'])
def get_record(record_id):
    conn = get_conn()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM life_expectancy WHERE id=%s", (record_id,))
        raw_data = cursor.fetchone()
        if raw_data:
            # 将中文字段名转换为英文字段名
            data = {}
            for chinese_key, english_key in REVERSE_FIELD_MAPPING.items():
                if chinese_key in raw_data:
                    data[english_key] = raw_data[chinese_key]
            data['id'] = record_id
        else:
            data = None
    conn.close()
    return jsonify(data)

@app.route('/api/record', methods=['POST'])
def add_record():
    record = request.json
    # 将英文字段名转换为中文字段名
    chinese_record = {}
    for english_key, value in record.items():
        if english_key in FIELD_MAPPING:
            chinese_record[FIELD_MAPPING[english_key]] = value
    
    conn = get_conn()
    with conn.cursor() as cursor:
        keys = ','.join([f"`{k}`" for k in chinese_record.keys()])
        values = ','.join(['%s'] * len(chinese_record))
        sql = f"INSERT INTO life_expectancy ({keys}) VALUES ({values})"
        cursor.execute(sql, tuple(chinese_record.values()))
        conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

@app.route('/api/record/<int:record_id>', methods=['PUT'])
def update_record(record_id):
    record = request.json
    # 将英文字段名转换为中文字段名
    chinese_record = {}
    for english_key, value in record.items():
        if english_key in FIELD_MAPPING:
            chinese_record[FIELD_MAPPING[english_key]] = value
    
    conn = get_conn()
    with conn.cursor() as cursor:
        set_clause = ','.join([f"`{k}`=%s" for k in chinese_record.keys()])
        sql = f"UPDATE life_expectancy SET {set_clause} WHERE id=%s"
        cursor.execute(sql, tuple(chinese_record.values()) + (record_id,))
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