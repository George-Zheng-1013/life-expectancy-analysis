import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
from sklearn.ensemble import RandomForestRegressor

# 1. 数据加载和初步清洗
def load_and_clean_data():
    # 读取CSV文件
    df = pd.read_csv('Life Expectancy Data.csv', encoding='utf-8')
    
    # 去除所有列名和内容的首尾空格
    df.columns = df.columns.str.strip()
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    
    # 列名改为中文
    df.columns = ['国家', '年份', '发展状态', '预期寿命', '成人死亡率', '婴儿死亡数', 
                  '酒精消费', '医疗支出百分比', '乙肝疫苗接种率', '麻疹病例数', 'BMI指数', 
                  '五岁以下死亡数', '脊髓灰质炎疫苗接种率', '总医疗支出', '白喉疫苗接种率', 
                  'HIV/AIDS死亡率', 'GDP', '人口数量', '1-19岁消瘦率', '5-9岁消瘦率', 
                  '收入构成资源', '受教育年限']
    
    # 保存中文版本数据
    df.to_csv('Life_Expectancy_Data_Chinese.csv', index=False, encoding='utf-8-sig')
    
    return df

# 2. 缺失值处理
def handle_missing_values(df):
    # 使用spsspro网站-缺失值处理-k近邻填充
    # 这里模拟处理过程，实际应用中可能需要使用sklearn的KNNImputer
    df_filled = df.copy()
    
    # 对数值列进行填充
    numeric_columns = df_filled.select_dtypes(include=[np.number]).columns.tolist()
    for col in numeric_columns:
        df_filled[col] = df_filled[col].fillna(df_filled[col].median())
    
    # 对分类列进行填充
    categorical_columns = df_filled.select_dtypes(include=['object']).columns.tolist()
    for col in categorical_columns:
        df_filled[col] = df_filled[col].fillna(df_filled[col].mode()[0])
    
    # 保存填充后的数据
    df_filled.to_csv("Life_Expectancy_Data_Filled.csv", index=False)
    
    return df_filled

# 3. 异常值处理
def handle_outliers(df):
    # 使用盖帽法处理异常值
    def cap_outliers(df, column):
        q1 = df[column].quantile(0.25)
        q3 = df[column].quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        # 使用盖帽法处理异常值
        df[column] = np.where(df[column] < lower_bound, lower_bound, df[column])
        df[column] = np.where(df[column] > upper_bound, upper_bound, df[column])
        
        return df
    
    # 对所有数值型列应用盖帽法
    numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
    for column in numeric_columns:
        df = cap_outliers(df, column)
    
    return df

# 4. 特征工程
def feature_engineering(df):
    # one-hot编码处理分类变量
    status_map = {'Developing': 0, 'Developed': 1}
    
    # 将分类变量转换为数值
    df['发展状态_数值'] = df['发展状态'].map(status_map)
    df.drop(columns=['发展状态'], inplace=True)  # 删除原始分类列
    
    # 保存转换后的数据集
    df.to_csv("Life_Expectancy_Data_Transformed_Final.csv", index=False)
    
    return df

# 5. 数据分析和可视化
def analyze_data(df):
    # 设置中文字体显示
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    
    # 绘制各特征与预期寿命的散点图
    columns = [col for col in df.columns if col != '预期寿命' and col != '国家']
    plt.figure(figsize=(20, 30))
    
    for i, col in enumerate(columns, 1):
        plt.subplot(len(columns) // 2 + 1, 2, i)
        sns.scatterplot(x=df[col], y=df['预期寿命'])
        plt.title(f'{col} vs 预期寿命', fontsize=14)
        plt.xlabel(col, fontsize=12)
        plt.ylabel('预期寿命', fontsize=12)
    
    plt.tight_layout()
    plt.show()
    
    # 计算相关系数
    print("\n各特征与预期寿命的相关系数:")
    for column in df.columns:
        if column != '预期寿命' and column != '国家':
            correlation = df[column].corr(df['预期寿命'])
            print(f'{column} 与 预期寿命 的相关系数: {correlation:.2f}')
    
    # 绘制热力图
    plt.figure(figsize=(12, 10))
    sns.heatmap(df[columns + ['预期寿命']].corr(), annot=True, cmap='coolwarm', fmt='.2f')
    plt.title('特征相关性热力图', fontsize=16)
    plt.show()
    
    # 随机森林特征重要性分析
    X = df.drop(columns=['预期寿命', '国家'])
    y = df['预期寿命']
    
    model = RandomForestRegressor()
    model.fit(X, y)
    
    importance = model.feature_importances_
    print("\n随机森林特征重要性:")
    for col, imp in zip(X.columns, importance):
        print(f"{col}: {imp:.4f}")

# 主函数
def main():
    # 1. 加载和清洗数据
    df = load_and_clean_data()
    
    # 2. 处理缺失值
    df_filled = handle_missing_values(df)
    
    # 3. 处理异常值
    df_cleaned = handle_outliers(df_filled)
    
    # 4. 特征工程
    df_transformed = feature_engineering(df_cleaned)
    
    # 5. 数据分析
    analyze_data(df_transformed)
    
    # 6. 导入数据库
    engine = create_engine('mysql+pymysql://root:123456@localhost:3306/life_expectancy_dataset')
    df_transformed.to_sql('life_expectancy', con=engine, index=False, if_exists='replace')
    print("\n数据已清洗并导入数据库！")

if __name__ == "__main__":
    main()