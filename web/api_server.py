#在集成终端中运行python api_server.py后开启flask后端服务
from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import json
import os

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

@app.route('/api/record', methods=['PUT'])
def update_record():
    record = request.json
    country = record.get('Country')
    year = record.get('Year')
    if not country or year is None:
        return jsonify({'status': 'error', 'error': '缺少国家或年份'}), 400

    chinese_record = {}
    for english_key, value in record.items():
        if english_key in FIELD_MAPPING and english_key not in ['Country', 'Year']:
            chinese_record[FIELD_MAPPING[english_key]] = value

    conn = get_conn()
    with conn.cursor() as cursor:
        set_clause = ','.join([f"`{k}`=%s" for k in chinese_record.keys()])
        sql = f"UPDATE life_expectancy SET {set_clause} WHERE `国家`=%s AND `年份`=%s"
        cursor.execute(sql, tuple(chinese_record.values()) + (country, year))
        conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

@app.route('/api/record', methods=['DELETE'])
def delete_record():
    data = request.json
    country = data.get('Country')
    year = data.get('Year')
    if not country or year is None:
        return jsonify({'status': 'error', 'error': '缺少国家或年份'}), 400

    conn = get_conn()
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM life_expectancy WHERE `国家`=%s AND `年份`=%s", (country, year))
        conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

@app.route('/api/fit', methods=['POST'])
def fit_data():
    try:
        body = request.json
        x_var = body.get('xVar')
        y_var = body.get('yVar')

        if not x_var or not y_var:
            return jsonify({"error": "Missing xVar or yVar"}), 400

        # 只支持与预期寿命的拟合
        if y_var != 'Life_expectancy':
            return jsonify({"error": "Only support fitting with Life_expectancy"}), 400        # 读取预计算的拟合结果
        fits_file = os.path.join(os.path.dirname(__file__), 'precomputed_fits.json')
        
        if not os.path.exists(fits_file):
            return jsonify({"error": "Precomputed fits not found. Please run precompute_fits.py first."}), 500

        with open(fits_file, 'r', encoding='utf-8') as f:
            all_fits = json.load(f)

        if x_var not in all_fits:
            return jsonify({"error": f"No precomputed fit found for {x_var}"}), 404

        # 返回拟合曲线的点数据，前端期望的是数组格式
        return jsonify(all_fits[x_var]['line_points'])

    except Exception as e:
        print(f"Error during fitting: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/import_csv', methods=['POST'])
def import_csv():
    if 'file' not in request.files:
        return jsonify({'status': 'fail', 'error': '未收到文件'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'status': 'fail', 'error': '未选择文件'}), 400
    try:
        try:
            df = pd.read_csv(file, encoding='utf-8')
        except UnicodeDecodeError:
            file.seek(0)
            df = pd.read_csv(file, encoding='gbk')
    except Exception as e:
        return jsonify({'status': 'fail', 'error': f'文件编码错误: {str(e)}'}), 400
    try:
        # 这里假设你的表名为 life_expectancy，主键为 Country+Year
        conn = pymysql.connect(host='localhost', user='root', password='你的密码', db='你的数据库', charset='utf8mb4')
        cursor = conn.cursor()
        for _, row in df.iterrows():
            # 构建插入语句，遇到主键冲突则更新
            sql = '''
            INSERT INTO life_expectancy (Country, Year, Life_expectancy, Adult_mortality, Infant_deaths, Alcohol_consumption, Under_five_deaths, Hepatitis_B, Measles, BMI, Polio, Diphtheria, Incidents_HIV, GDP_per_capita, Population_mln, Thinness_ten_nineteen_years, Thinness_five_nine_years, Schooling, Economy_status_Developed, Economy_status_Developing)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                Life_expectancy=VALUES(Life_expectancy),
                Adult_mortality=VALUES(Adult_mortality),
                Infant_deaths=VALUES(Infant_deaths),
                Alcohol_consumption=VALUES(Alcohol_consumption),
                Under_five_deaths=VALUES(Under_five_deaths),
                Hepatitis_B=VALUES(Hepatitis_B),
                Measles=VALUES(Measles),
                BMI=VALUES(BMI),
                Polio=VALUES(Polio),
                Diphtheria=VALUES(Diphtheria),
                Incidents_HIV=VALUES(Incidents_HIV),
                GDP_per_capita=VALUES(GDP_per_capita),
                Population_mln=VALUES(Population_mln),
                Thinness_ten_nineteen_years=VALUES(Thinness_ten_nineteen_years),
                Thinness_five_nine_years=VALUES(Thinness_five_nine_years),
                Schooling=VALUES(Schooling),
                Economy_status_Developed=VALUES(Economy_status_Developed),
                Economy_status_Developing=VALUES(Economy_status_Developing)
            '''
            values = tuple(row.get(col, None) for col in [
                'Country', 'Year', 'Life_expectancy', 'Adult_mortality', 'Infant_deaths', 'Alcohol_consumption',
                'Under_five_deaths', 'Hepatitis_B', 'Measles', 'BMI', 'Polio', 'Diphtheria', 'Incidents_HIV',
                'GDP_per_capita', 'Population_mln', 'Thinness_ten_nineteen_years', 'Thinness_five_nine_years',
                'Schooling', 'Economy_status_Developed', 'Economy_status_Developing'
            ])
            cursor.execute(sql, values)
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'fail', 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)