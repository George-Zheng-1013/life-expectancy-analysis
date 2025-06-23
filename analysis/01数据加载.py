# %% [markdown]
# 数据加载

# %%
import numpy as np
import pandas as pd

# %%
df= pd.read_csv('..\dataset\Life Expectancy Data.csv')
#打印列索引
print(df.columns)
#列索引改成中文
df.columns = ['国家', '年份', '发展状态', '预期寿命', '成人死亡率', '婴儿死亡数', 
              '酒精消费', '医疗支出百分比', '乙肝疫苗接种率', '麻疹病例数', 'BMI指数', 
              '五岁以下死亡数', '脊髓灰质炎疫苗接种率', '总医疗支出', '白喉疫苗接种率', 
              'HIV/AIDS死亡率', 'GDP', '人口数量', '1-19岁消瘦率', '5-9岁消瘦率', 
              '收入构成资源', '受教育年限']
df.head()

# %%
df.info()

# %%
df.isnull().sum()

# %%
df.to_csv('..\dataset\Life_Expectancy_Data_Chinese.csv', index=False, encoding='utf-8-sig')


