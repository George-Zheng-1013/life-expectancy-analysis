# %%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# %%
df=pd.read_csv('..\dataset\Life_Expectancy_Data_Transformed_Final.csv')

# %%
df.head()

# %%
columns = [col for col in df.columns if col != '预期寿命']

plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

# 设置图形大小
plt.figure(figsize=(20, 30))  # 调整图形大小，使图片更大

# 遍历每个特征列并绘制散点图
for i, col in enumerate(columns, 1):
    plt.subplot(len(columns) // 2 + 1, 2, i)  # 每行显示2个子图
    sns.scatterplot(x=df[col], y=df['预期寿命'])
    plt.title(f'{col} vs Life Expectancy', fontsize=14)  # 调整标题字体大小
    plt.xlabel(col, fontsize=12)  # 调整标签字体大小
    plt.ylabel('Life Expectancy', fontsize=12)

plt.tight_layout()
plt.show()

# %%
# 计算每个特征与目标变量的相关系数
for column in df.columns:
    if column != '预期寿命' and column!= '国家':
        correlation = df[column].corr(df['预期寿命'])
        print(f'Correlation between {column} and 预期寿命: {correlation:.2f}')

# %%
# 热力图
columns = [col for col in df.columns if col != '预期寿命' and col != '国家']

plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

# 设置图形大小
plt.figure(figsize=(12, 10))  # 调整图形大小，使热力图更清晰

# 绘制热力图
sns.heatmap(df[columns + ['预期寿命']].corr(), annot=True, cmap='coolwarm', fmt='.2f')
plt.title('Feature Correlation Heatmap', fontsize=16)  # 设置标题字体大小
plt.show()

# %%
from sklearn.ensemble import RandomForestRegressor

X = df.drop(columns=['预期寿命','国家'])
y = df['预期寿命']

model = RandomForestRegressor()
model.fit(X, y)

importance = model.feature_importances_
for col, imp in zip(X.columns, importance):
    print(f"{col}: {imp}")


