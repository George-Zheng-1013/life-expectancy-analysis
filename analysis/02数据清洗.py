# %%
import numpy as np
import pandas as pd

# %%
df=pd.read_csv('../dataset/Life_Expectancy_Data_Chinese.csv')
df.head()

# %%
df.isnull().sum()

# %% [markdown]
# 使用spsspro网站-缺失值处理-k近邻填充

# %%
df_filled=pd.read_csv("D:\HP\Downloads\版本1_缺失值处理_Life_Expectancy_Data_Chinese_副本1.csv")
df_filled.isnull().sum()

# %%
df_filled.to_csv("..\dataset\Life_Expectancy_Data_Filled.csv", index=False)

# %%
df_filled.duplicated().sum()

# %%
#对每个特征值绘制箱型图
import matplotlib.pyplot as plt
import seaborn as sns

# 设置中文字体显示
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

# 获取数值型列
def draw_boxplots(df):

    numeric_columns = df_filled.select_dtypes(include=[np.number]).columns.tolist()

    # 计算子图数量和布局
    n_cols = 3  # 每行3个图
    n_rows = (len(numeric_columns) + n_cols - 1) // n_cols

    # 创建子图
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(18, 6*n_rows))
    fig.suptitle('各特征值箱型图分析', fontsize=16, y=0.98)

    # 将axes转换为一维数组，便于遍历
    if n_rows == 1:
        axes = [axes] if n_cols == 1 else axes
    else:
        axes = axes.flatten()

    # 为每个数值型特征绘制箱型图
    for i, column in enumerate(numeric_columns):
        sns.boxplot(y=df_filled[column], ax=axes[i])
        axes[i].set_title(f'{column}箱型图')
        axes[i].set_ylabel(column)
        
        # 添加统计信息
        q1 = df_filled[column].quantile(0.25)
        q3 = df_filled[column].quantile(0.75)
        median = df_filled[column].median()
        iqr = q3 - q1
        outliers_count = len(df_filled[(df_filled[column] < q1 - 1.5*iqr) | 
                                    (df_filled[column] > q3 + 1.5*iqr)])
        
        axes[i].text(0.02, 0.98, f'异常值数量: {outliers_count}', 
                    transform=axes[i].transAxes, verticalalignment='top',
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    # 隐藏多余的子图
    for i in range(len(numeric_columns), len(axes)):
        axes[i].set_visible(False)

    plt.tight_layout()
    plt.show()

    # 打印每个特征的异常值统计
    print("各特征异常值统计:")
    print("-" * 50)
    for column in numeric_columns:
        q1 = df_filled[column].quantile(0.25)
        q3 = df_filled[column].quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        outliers = df_filled[(df_filled[column] < lower_bound) | 
                            (df_filled[column] > upper_bound)]
        
        print(f"{column}: {len(outliers)}个异常值 ({len(outliers)/len(df_filled)*100:.2f}%)")

# %%
draw_boxplots(df_filled)

# %%
#使用盖帽法处理异常值
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
for column in numeric_columns:
    df_filled = cap_outliers(df_filled, column)

draw_boxplots(df_filled)

# %%
print(df_filled.columns)

# %%
df_transformed = df_filled.copy()

# %%
#one-hot编码处理分类变量
import pandas as pd
import numpy as np

# 识别分类变量
categorical_columns = df_transformed.select_dtypes(include=['object']).columns.tolist()
print(f"分类变量列: {categorical_columns}")

# 查看每个分类变量的唯一值
print("\n各分类变量的唯一值:")
print("-" * 40)
for col in categorical_columns:
    unique_values = df_transformed[col].unique()
    print(f"{col}: {unique_values} (共{len(unique_values)}个类别)")
    print()

# %%
df_transformed.head()

# %%
status_map = {'Developing': 0, 'Developed': 1}

# 将分类变量转换为数值
df_transformed['发展状态_数值'] = df_transformed['发展状态'].map(status_map)
df_transformed.drop(columns=['发展状态'], inplace=True)  # 删除原始分类列
# 查看结果
print("转换后的前5行:")
print(df_transformed.head())

# 查看唯一值确认转换成功
print("\n发展状态_数值的唯一值:", df_transformed['发展状态_数值'].unique())

# 保存转换后的数据集
df_transformed.to_csv("..\dataset\Life_Expectancy_Data_Transformed_Final.csv", index=False)


