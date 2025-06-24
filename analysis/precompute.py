# 预计算所有特征与预期寿命的拟合曲线
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import json
import os

def precompute_all_fits():
    print("开始预计算所有特征与预期寿命的拟合曲线...")
    
    # 中文到英文字段名映射
    chinese_to_english = {
        '年份': 'Year',
        '预期寿命': 'Life_expectancy', 
        '成人死亡率': 'Adult_mortality',
        '婴儿死亡数': 'Infant_deaths',
        '酒精消费': 'Alcohol_consumption',
        '五岁以下死亡数': 'Under_five_deaths',
        '乙肝疫苗接种率': 'Hepatitis_B',
        '麻疹病例数': 'Measles',
        'BMI指数': 'BMI',
        '脊髓灰质炎疫苗接种率': 'Polio',
        '白喉疫苗接种率': 'Diphtheria',
        'HIV/AIDS死亡率': 'Incidents_HIV',
        'GDP人均': 'GDP_per_capita',
        '人口数量(百万)': 'Population_mln',
        '10-19岁消瘦率': 'Thinness_ten_nineteen_years',
        '5-9岁消瘦率': 'Thinness_five_nine_years',
        '受教育年限': 'Schooling',
        '发展状态_数值': 'Status'
    }
    
    # 读取CSV文件
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'dataset', 'Life_Expectancy_Data_Transformed_Final.csv')
    
    if not os.path.exists(csv_path):
        print(f"错误：找不到CSV文件 {csv_path}")
        return None
    
    print(f"正在读取CSV文件: {csv_path}")
    df = pd.read_csv(csv_path)
    
    print(f"CSV数据加载成功！")
    print(f"数据总量: {len(df)} 行")
    print(f"数据列: {list(df.columns)}")
    
    # 获取数值型特征列（排除非数值列）
    numeric_features = []
    for col in df.columns:
        if col not in ['国家', '年份', '预期寿命']:
            # 检查是否为数值列
            if df[col].dtype in ['int64', 'float64'] or pd.api.types.is_numeric_dtype(df[col]):
                numeric_features.append(col)
    
    print(f"可用于拟合的数值特征: {numeric_features}")
    print(f"总共 {len(numeric_features)} 个特征")
    
    # 预计算所有特征与预期寿命的拟合结果
    fit_results = {}
    
    for i, feature in enumerate(numeric_features):
        try:
            print(f"正在处理特征 {i+1}/{len(numeric_features)}: {feature}")
            
            # 准备数据，使用中文列名
            df_fit = df[[feature, '预期寿命']].copy()
            df_fit = df_fit.dropna()
            
            if len(df_fit) < 10:  # 需要足够的数据点
                print(f"  跳过 {feature}: 有效数据不足 ({len(df_fit)} 行)")
                continue
            
            X = df_fit[[feature]].values
            y = df_fit['预期寿命'].values
            
            # 训练随机森林模型
            regression = RandomForestRegressor(n_estimators=20, random_state=42, n_jobs=-1)
            regression.fit(X, y)
            
            # 生成拟合曲线点
            x_range = np.linspace(X.min(), X.max(), 100).reshape(-1, 1)
            y_pred = regression.predict(x_range)
            
            line_points = [{"x": float(x_val), "y": float(y_val)} for x_val, y_val in zip(x_range.flatten(), y_pred)]
            
            # 使用英文字段名作为键，以便前端访问
            english_feature = chinese_to_english.get(feature, feature)
            fit_results[english_feature] = {
                'line_points': line_points,
                'data_count': len(df_fit),
                'x_range': [float(X.min()), float(X.max())],
                'y_range': [float(y_pred.min()), float(y_pred.max())]
            }
            
            print(f"  完成 {feature} -> {english_feature}: {len(df_fit)} 个数据点, 拟合曲线 {len(line_points)} 个点")
            
        except Exception as e:
            print(f"  错误处理 {feature}: {e}")
            continue
    
    # 保存结果到web目录下的JSON文件
    output_file = os.path.join(os.path.dirname(__file__), '..', 'web', 'precomputed_fits.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(fit_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n预计算完成！")
    print(f"成功处理 {len(fit_results)} 个特征")
    print(f"结果已保存到: {output_file}")
    print(f"文件大小: {os.path.getsize(output_file) / 1024:.1f} KB")
    
    # 显示处理结果摘要
    print("\n处理结果摘要:")
    for english_feature, data in fit_results.items():
        print(f"  {english_feature}: {data['data_count']} 个数据点")
    
    return fit_results

if __name__ == '__main__':
    precompute_all_fits()
