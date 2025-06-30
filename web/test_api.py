#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试API服务器的CRUD功能
确保数据库操作正常工作
"""

import requests
import json
import tempfile
import os

BASE_URL = 'http://localhost:5000'

def test_get_data():
    """测试获取所有数据"""
    print("测试获取数据...")
    response = requests.get(f'{BASE_URL}/api/data')
    if response.status_code == 200:
        data = response.json()
        print(f"✓ 成功获取 {len(data)} 条记录")
        if len(data) > 0:
            print(f"  示例记录: {data[0]['Country']} - {data[0]['Year']}")
        return True
    else:
        print(f"✗ 获取数据失败: {response.status_code}")
        return False

def test_add_record():
    """测试添加记录"""
    print("\n测试添加记录...")
    test_record = {
        'Country': 'TestCountry',
        'Year': 2020,
        'Life_expectancy': 75.5,
        'Adult_mortality': 100,
        'Infant_deaths': 5,
        'Alcohol_consumption': 5.5,
        'Under_five_deaths': 6,
        'Hepatitis_B': 95,
        'Measles': 10,
        'BMI': 25.5,
        'Polio': 95,
        'Diphtheria': 95,
        'Incidents_HIV': 0.1,
        'GDP_per_capita': 10000,
        'Population_mln': 10.5,
        'Thinness_ten_nineteen_years': 5.5,
        'Thinness_five_nine_years': 5.5,
        'Schooling': 12.5,
        'Economy_status_Developed': 0,
        'Economy_status_Developing': 1,
        'Status': 'Developing'
    }
    
    response = requests.post(
        f'{BASE_URL}/api/record',
        headers={'Content-Type': 'application/json'},
        data=json.dumps(test_record)
    )
    
    if response.status_code == 200:
        result = response.json()
        if result['status'] == 'success':
            print(f"✓ 成功添加测试记录: {test_record['Country']} - {test_record['Year']}")
            return True
        else:
            print(f"✗ 添加记录失败: {result.get('error', '未知错误')}")
            return False
    else:
        print(f"✗ 添加记录请求失败: {response.status_code}")
        return False

def test_update_record():
    """测试更新记录"""
    print("\n测试更新记录...")
    update_data = {
        'Country': 'TestCountry',
        'Year': 2020,
        'Life_expectancy': 80.0,  # 更新预期寿命
        'GDP_per_capita': 12000   # 更新GDP
    }
    
    response = requests.put(
        f'{BASE_URL}/api/record',
        headers={'Content-Type': 'application/json'},
        data=json.dumps(update_data)
    )
    
    if response.status_code == 200:
        result = response.json()
        if result['status'] == 'success':
            print(f"✓ 成功更新测试记录: {update_data['Country']} - {update_data['Year']}")
            return True
        else:
            print(f"✗ 更新记录失败: {result.get('error', '未知错误')}")
            return False
    else:
        print(f"✗ 更新记录请求失败: {response.status_code}")
        return False

def test_delete_record():
    """测试删除记录"""
    print("\n测试删除记录...")
    delete_data = {
        'Country': 'TestCountry',
        'Year': 2020
    }
    
    response = requests.delete(
        f'{BASE_URL}/api/record',
        headers={'Content-Type': 'application/json'},
        data=json.dumps(delete_data)
    )
    
    if response.status_code == 200:
        result = response.json()
        if result['status'] == 'success':
            print(f"✓ 成功删除测试记录: {delete_data['Country']} - {delete_data['Year']}")
            return True
        else:
            print(f"✗ 删除记录失败: {result.get('error', '未知错误')}")
            return False
    else:
        print(f"✗ 删除记录请求失败: {response.status_code}")
        return False

def test_csv_import():
    """测试CSV导入功能"""
    print("\n测试CSV导入功能...")
    
    # 创建测试CSV数据
    test_csv_content = """Country,Year,Life_expectancy,Adult_mortality,Infant_deaths,Alcohol_consumption,Under_five_deaths,Hepatitis_B,Measles,BMI,Polio,Diphtheria,Incidents_HIV,GDP_per_capita,Population_mln,Thinness_ten_nineteen_years,Thinness_five_nine_years,Schooling,Economy_status_Developed,Economy_status_Developing,Status
TestCountry1,2021,75.5,100,5,5.5,6,95,10,25.5,95,95,0.1,10000,10.5,5.5,5.5,12.5,0,1,Developing
TestCountry2,2021,80.2,80,3,6.5,4,97,5,27.1,97,97,0.05,15000,8.2,4.1,4.2,14.2,1,0,Developed"""
    
    # 将CSV数据写入临时文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as temp_file:
        temp_file.write(test_csv_content)
        temp_csv_path = temp_file.name
    
    try:
        # 准备上传文件
        with open(temp_csv_path, 'rb') as csv_file:
            files = {'file': ('test_data.csv', csv_file, 'text/csv')}
            
            response = requests.post(
                f'{BASE_URL}/api/import_csv',
                files=files
            )
        
        if response.status_code == 200:
            result = response.json()
            if result['status'] == 'success':
                print(f"✓ CSV导入成功: {result['message']}")
                if 'details' in result:
                    details = result['details']
                    print(f"  详情: 总计{details['total']}行，成功{details['successful']}行，失败{details['failed']}行")
                    if details['errors']:
                        print(f"  错误: {details['errors'][:3]}")  # 只显示前3个错误
                return True
            else:
                print(f"✗ CSV导入失败: {result.get('error', '未知错误')}")
                return False
        else:
            print(f"✗ CSV导入请求失败: {response.status_code}")
            try:
                error_info = response.json()
                print(f"  错误详情: {error_info}")
            except:
                print(f"  响应内容: {response.text}")
            return False
    
    except Exception as e:
        print(f"✗ CSV导入异常: {e}")
        return False
    
    finally:
        # 清理临时文件
        try:
            os.unlink(temp_csv_path)
        except:
            pass

def test_sample_csv_download():
    """测试示例CSV文件下载"""
    print("\n测试示例CSV文件下载...")
    
    try:
        response = requests.get(f'{BASE_URL}/api/sample_csv')
        
        if response.status_code == 200:
            # 检查是否是CSV内容
            content = response.text
            if 'Country,Year' in content:
                print("✓ 示例CSV文件下载成功")
                print(f"  文件大小: {len(content)} 字符")
                print(f"  前100字符: {content[:100]}...")
                return True
            else:
                print("✗ 下载的文件不是有效的CSV格式")
                return False
        else:
            print(f"✗ 示例CSV文件下载失败: {response.status_code}")
            return False
    
    except Exception as e:
        print(f"✗ 示例CSV文件下载异常: {e}")
        return False

def main():
    """运行所有测试"""
    print("开始测试API服务器功能...")
    print("="*50)
    
    tests = [
        test_get_data,
        test_sample_csv_download,
        test_csv_import,
        test_add_record,
        test_update_record,
        test_delete_record
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ 测试异常: {e}")
            failed += 1
    
    print("\n" + "="*50)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    
    if failed == 0:
        print("🎉 所有测试通过！数据库CRUD功能和CSV导入功能正常工作。")
    else:
        print("⚠️  部分测试失败，请检查API服务器和数据库连接。")

if __name__ == '__main__':
    main()