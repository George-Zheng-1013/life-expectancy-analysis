#在集成终端中运行python api_server.py后开启flask后端服务
from flask import Flask, request, jsonify, send_file
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

# 字段名映射：英文字段名 -> 中文字段名（数据库中的字段名）
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
    'Status': '发展状态_数值'
}

REVERSE_FIELD_MAPPING = {v: k for k, v in FIELD_MAPPING.items()}

@app.route('/api/data', methods=['GET'])
def get_data():
    conn = get_conn()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM life_expectancy")
        raw_data = cursor.fetchall()
        # 将中文字段名转换为英文字段名返回给前端
        data = []
        for row in raw_data:
            english_row = {}
            for chinese_key, value in row.items():
                # 寻找对应的英文字段名
                english_key = None
                for eng_key, chi_key in FIELD_MAPPING.items():
                    if chi_key == chinese_key:
                        english_key = eng_key
                        break
                if english_key:
                    # 特殊处理Status字段，将数值转换为文本
                    if english_key == 'Status' and value is not None:
                        english_row[english_key] = 'Developed' if value == 1 else 'Developing'
                        # 为了兼容前端，同时设置Economy_status字段
                        english_row['Economy_status_Developed'] = 1 if value == 1 else 0
                        english_row['Economy_status_Developing'] = 1 if value == 0 else 0
                    else:
                        english_row[english_key] = value
                else:
                    # 如果没有找到映射，保持原字段名（比如id字段）
                    english_row[chinese_key] = value
            data.append(english_row)
    conn.close()
    return jsonify(data)

@app.route('/api/record/<int:record_id>', methods=['GET'])
def get_record(record_id):
    conn = get_conn()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM life_expectancy WHERE id=%s", (record_id,))
        raw_data = cursor.fetchone()
        if raw_data:
            # 将中文字段名转换为英文字段名返回给前端
            english_row = {}
            for chinese_key, value in raw_data.items():
                # 寻找对应的英文字段名
                english_key = None
                for eng_key, chi_key in FIELD_MAPPING.items():
                    if chi_key == chinese_key:
                        english_key = eng_key
                        break
                if english_key:
                    # 特殊处理Status字段，将数值转换为文本
                    if english_key == 'Status' and value is not None:
                        english_row[english_key] = 'Developed' if value == 1 else 'Developing'
                        # 为了兼容前端，同时设置Economy_status字段
                        english_row['Economy_status_Developed'] = 1 if value == 1 else 0
                        english_row['Economy_status_Developing'] = 1 if value == 0 else 0
                    else:
                        english_row[english_key] = value
                else:
                    # 如果没有找到映射，保持原字段名
                    english_row[chinese_key] = value
            data = english_row
        else:
            data = None
    conn.close()
    return jsonify(data)

@app.route('/api/record', methods=['POST'])
def add_record():
    try:
        record = request.json
        if not record:
            return jsonify({'status': 'error', 'error': '请求数据为空'}), 400
            
        # 将英文字段名转换为中文字段名（数据库字段是中文的）
        chinese_record = {}
        for english_key, value in record.items():
            if english_key in FIELD_MAPPING:
                chinese_field = FIELD_MAPPING[english_key]
                # 处理空值
                if value == '' or value is None:
                    chinese_record[chinese_field] = None
                else:
                    # 特殊处理Status字段
                    if english_key == 'Status':
                        if isinstance(value, str):
                            chinese_record[chinese_field] = 1 if value.lower() == 'developed' else 0
                        else:
                            chinese_record[chinese_field] = value
                    else:
                        chinese_record[chinese_field] = value
        
        # 确保必需字段存在
        if '国家' not in chinese_record or '年份' not in chinese_record:
            return jsonify({'status': 'error', 'error': '缺少必需字段：国家或年份'}), 400
        
        conn = get_conn()
        with conn.cursor() as cursor:
            keys = ','.join([f"`{k}`" for k in chinese_record.keys()])
            values = ','.join(['%s'] * len(chinese_record))
            sql = f"INSERT INTO life_expectancy ({keys}) VALUES ({values})"
            print(f"执行SQL: {sql}")
            print(f"数据: {tuple(chinese_record.values())}")
            cursor.execute(sql, tuple(chinese_record.values()))
            conn.commit()
        conn.close()
        return jsonify({'status': 'success', 'message': '记录添加成功'})
    except Exception as e:
        print(f"添加记录错误: {e}")
        return jsonify({'status': 'error', 'error': f'添加记录失败: {str(e)}'}), 500

@app.route('/api/record', methods=['PUT'])
def update_record():
    try:
        record = request.json
        if not record:
            return jsonify({'status': 'error', 'error': '请求数据为空'}), 400
            
        country = record.get('Country')
        year = record.get('Year')
        if not country or year is None:
            return jsonify({'status': 'error', 'error': '缺少国家或年份'}), 400

        # 将英文字段名转换为中文字段名，排除主键字段
        chinese_record = {}
        for english_key, value in record.items():
            if english_key in FIELD_MAPPING and english_key not in ['Country', 'Year']:
                chinese_field = FIELD_MAPPING[english_key]
                # 处理空值
                if value == '' or value is None:
                    chinese_record[chinese_field] = None
                else:
                    # 特殊处理Status字段
                    if english_key == 'Status':
                        if isinstance(value, str):
                            chinese_record[chinese_field] = 1 if value.lower() == 'developed' else 0
                        else:
                            chinese_record[chinese_field] = value
                    else:
                        chinese_record[chinese_field] = value

        if not chinese_record:
            return jsonify({'status': 'error', 'error': '没有可更新的字段'}), 400

        conn = get_conn()
        with conn.cursor() as cursor:
            # 检查记录是否存在
            cursor.execute("SELECT COUNT(*) as count FROM life_expectancy WHERE `国家`=%s AND `年份`=%s", (country, year))
            result = cursor.fetchone()
            if result['count'] == 0:
                conn.close()
                return jsonify({'status': 'error', 'error': '未找到要更新的记录'}), 404
            
            # 执行更新
            set_clause = ','.join([f"`{k}`=%s" for k in chinese_record.keys()])
            sql = f"UPDATE life_expectancy SET {set_clause} WHERE `国家`=%s AND `年份`=%s"
            print(f"执行SQL: {sql}")
            print(f"数据: {tuple(chinese_record.values()) + (country, year)}")
            cursor.execute(sql, tuple(chinese_record.values()) + (country, year))
            
            if cursor.rowcount == 0:
                conn.close()
                return jsonify({'status': 'error', 'error': '更新失败，未找到匹配的记录'}), 404
                
            conn.commit()
        conn.close()
        return jsonify({'status': 'success', 'message': '记录更新成功'})
    except Exception as e:
        print(f"更新记录错误: {e}")
        return jsonify({'status': 'error', 'error': f'更新记录失败: {str(e)}'}), 500

@app.route('/api/record', methods=['DELETE'])
def delete_record():
    try:
        data = request.json
        if not data:
            return jsonify({'status': 'error', 'error': '请求数据为空'}), 400
            
        country = data.get('Country')
        year = data.get('Year')
        if not country or year is None:
            return jsonify({'status': 'error', 'error': '缺少国家或年份'}), 400

        conn = get_conn()
        with conn.cursor() as cursor:
            # 先检查记录是否存在
            cursor.execute("SELECT COUNT(*) as count FROM life_expectancy WHERE `国家`=%s AND `年份`=%s", (country, year))
            result = cursor.fetchone()
            if result['count'] == 0:
                conn.close()
                return jsonify({'status': 'error', 'error': '未找到要删除的记录'}), 404
            
            # 执行删除
            sql = "DELETE FROM life_expectancy WHERE `国家`=%s AND `年份`=%s"
            print(f"执行SQL: {sql}")
            print(f"数据: ({country}, {year})")
            cursor.execute(sql, (country, year))
            
            if cursor.rowcount == 0:
                conn.close()
                return jsonify({'status': 'error', 'error': '删除失败，未找到匹配的记录'}), 404
                
            conn.commit()
        conn.close()
        return jsonify({'status': 'success', 'message': '记录删除成功'})
    except Exception as e:
        print(f"删除记录错误: {e}")
        return jsonify({'status': 'error', 'error': f'删除记录失败: {str(e)}'}), 500

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
        # 尝试不同编码读取CSV文件
        try:
            df = pd.read_csv(file, encoding='utf-8')
        except UnicodeDecodeError:
            file.seek(0)
            try:
                df = pd.read_csv(file, encoding='gbk')
            except UnicodeDecodeError:
                file.seek(0)
                df = pd.read_csv(file, encoding='latin-1')
    except Exception as e:
        return jsonify({'status': 'fail', 'error': f'文件读取错误: {str(e)}'}), 400
    
    if df.empty:
        return jsonify({'status': 'fail', 'error': 'CSV文件为空'}), 400
    
    try:
        conn = get_conn()
        cursor = conn.cursor()
        
        # 统计导入信息
        total_rows = len(df)
        successful_rows = 0
        errors = []
        
        for index, row in df.iterrows():
            try:
                # 将英文字段名转换为中文字段名以匹配数据库
                chinese_row = {}
                
                # 处理基本字段
                for english_key, value in row.items():
                    if english_key in FIELD_MAPPING:
                        # 处理空值
                        if pd.isna(value) or (isinstance(value, str) and value.strip() == ''):
                            chinese_row[FIELD_MAPPING[english_key]] = None
                        else:
                            chinese_row[FIELD_MAPPING[english_key]] = value
                
                # 特殊处理Status字段 - 转换为数值
                if 'Economy_status_Developed' in row and 'Economy_status_Developing' in row:
                    if pd.notna(row['Economy_status_Developed']) and row['Economy_status_Developed'] == 1:
                        chinese_row[FIELD_MAPPING['Status']] = 1  # 发达国家用1表示
                    elif pd.notna(row['Economy_status_Developing']) and row['Economy_status_Developing'] == 1:
                        chinese_row[FIELD_MAPPING['Status']] = 0  # 发展中国家用0表示
                elif 'Status' in row and pd.notna(row['Status']):
                    # 如果Status是文本，转换为数值
                    status_value = str(row['Status']).strip().lower()
                    if status_value == 'developed':
                        chinese_row[FIELD_MAPPING['Status']] = 1
                    elif status_value == 'developing':
                        chinese_row[FIELD_MAPPING['Status']] = 0
                    else:
                        # 尝试直接作为数值处理
                        try:
                            chinese_row[FIELD_MAPPING['Status']] = float(row['Status'])
                        except (ValueError, TypeError):
                            chinese_row[FIELD_MAPPING['Status']] = 0  # 默认为发展中国家
                
                # 检查必需字段
                if '国家' not in chinese_row or '年份' not in chinese_row:
                    errors.append(f"第{index+2}行：缺少必需字段 Country 或 Year")
                    continue
                
                if chinese_row['国家'] is None or chinese_row['年份'] is None:
                    errors.append(f"第{index+2}行：Country 或 Year 字段为空")
                    continue
                
                # 构建插入语句，遇到主键冲突则更新
                if chinese_row:
                    keys = ','.join([f"`{k}`" for k in chinese_row.keys()])
                    placeholders = ','.join(['%s'] * len(chinese_row))
                    
                    # 构建更新子句，排除主键字段
                    update_fields = [k for k in chinese_row.keys() if k not in ['国家', '年份']]
                    if update_fields:
                        update_clause = ','.join([f"`{k}`=VALUES(`{k}`)" for k in update_fields])
                        sql = f'''
                        INSERT INTO life_expectancy ({keys})
                        VALUES ({placeholders})
                        ON DUPLICATE KEY UPDATE {update_clause}
                        '''
                    else:
                        sql = f'''
                        INSERT IGNORE INTO life_expectancy ({keys})
                        VALUES ({placeholders})
                        '''
                    
                    cursor.execute(sql, tuple(chinese_row.values()))
                    successful_rows += 1
                    
            except Exception as row_error:
                error_msg = f"第{index+2}行处理失败: {str(row_error)}"
                errors.append(error_msg)
                print(error_msg)
                continue
        
        conn.commit()
        cursor.close()
        conn.close()
        
        # 构建返回消息
        message = f'成功导入 {successful_rows}/{total_rows} 条记录'
        if errors:
            # 限制错误信息数量避免响应过大
            error_summary = errors[:5]  # 只显示前5个错误
            if len(errors) > 5:
                error_summary.append(f"...以及其他 {len(errors)-5} 个错误")
            message += f'，{len(errors)} 条记录导入失败'
        
        return jsonify({
            'status': 'success', 
            'message': message,
            'details': {
                'total': total_rows,
                'successful': successful_rows,
                'failed': len(errors),
                'errors': errors[:10] if errors else []  # 最多返回10个错误详情
            }
        })
        
    except Exception as e:
        print(f"CSV导入错误: {e}")
        return jsonify({'status': 'fail', 'error': f'数据库操作失败: {str(e)}'}), 500

@app.route('/api/sample_csv', methods=['GET'])
def download_sample_csv():
    """下载示例CSV文件"""
    try:
        sample_file_path = os.path.join(os.path.dirname(__file__), 'sample_data.csv')
        if os.path.exists(sample_file_path):
            return send_file(sample_file_path, 
                           as_attachment=True, 
                           download_name='life_expectancy_sample.csv',
                           mimetype='text/csv')
        else:
            return jsonify({'error': '示例文件不存在'}), 404
    except Exception as e:
        return jsonify({'error': f'下载失败: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)