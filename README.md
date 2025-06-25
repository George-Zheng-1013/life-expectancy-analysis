# 预期寿命数据分析与可视化系统

本项目基于世界卫生组织（WHO）公开数据，集成了数据清洗、特征工程、数据库管理、API 服务和交互式网页可视化，旨在探索全球健康与经济指标对预期寿命的影响。

## 目录结构

```
analysis/      # Jupyter 数据分析与特征工程
dataset/       # 数据集（原始、中文、填充、转换后）
sql/           # SQL 脚本与数据分析脚本
web/           # Flask API 后端与前端可视化页面
```

## 主要功能

- **数据分析与预处理**：使用 Jupyter Notebook 进行数据加载、清洗、特征处理与重构。
- **数据库管理**：MySQL 存储清洗后的数据，支持增删改查和批量导入。
- **API 服务**：基于 Flask 提供数据接口，支持数据查询、拟合分析、批量导入等。
- **交互式前端**：基于 HTML+JS（Chart.js、Leaflet）实现数据表格、特征相关性分析、散点图拟合、世界地图分布可视化等功能。

## 快速开始

### 1. 环境准备

- Python 3.8+
- MySQL 数据库
- 推荐使用虚拟环境

安装依赖：

```sh
pip install -r requirements.txt
```

### 2. 数据库初始化

1. 创建数据库 `life_expectancy_dataset`
2. 执行 [sql/change_primary_key.sql](sql/change_primary_key.sql) 初始化表结构

### 3. 数据处理与导入

在 `analysis/` 目录下运行 Jupyter Notebook，完成数据清洗与特征工程，生成最终数据集。
或直接运行：

```sh
python sql/data_analysis.py
```

### 4. 启动后端服务

进入 `web/` 目录，运行：

```sh
python api_server.py
```

默认监听端口为 5000。

### 5. 启动前端页面

直接用浏览器打开 [web/web.html](web/web.html) 或 [web/world_map.html](web/world_map.html)。

## 主要文件说明

- `analysis/数据加载.ipynb`、`数据清洗及特征处理.ipynb`、`数据重构.ipynb`：数据探索与处理
- `sql/data_analysis.py`：数据清洗与入库自动化脚本
- `web/api_server.py`：Flask API 服务
- `web/web.html`：主数据分析与管理页面
- `web/world_map.html`：世界地图分布可视化页面

## 主要依赖

- Flask、Flask-CORS
- pymysql
- pandas、numpy、scikit-learn
- Chart.js、Leaflet.js

## 特色功能

- 多维特征与预期寿命相关性热力图
- 随机森林拟合与可视化
- 世界地图分布与统计
- 数据库增删改查与批量导入

## 致谢

数据来源：  
- WHO 官方数据：[Life Expectancy Data](https://www.who.int/data/gho/data/themes/mortality-and-global-health-estimates/ghe-life-expectancy-and-healthy-life-expectancy)  
- Kaggle 数据集：lashagoch/life-expectancy-who-updated  
  获取方式：
  ```python
  import kagglehub

  # Download latest version
  path = kagglehub.dataset_download("lashagoch/life-expectancy-who-updated")
  print("Path to dataset files:", path)
  ```
