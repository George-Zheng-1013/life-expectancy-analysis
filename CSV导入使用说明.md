# CSV导入功能使用说明

## 功能概述
CSV导入功能允许用户批量导入预期寿命数据到数据库中，支持新增和更新记录。系统已修复和优化，提供完整的错误处理和详细的导入反馈。

## 最新修复内容
- ✅ 修复了CSV文件读取的编码问题（支持UTF-8、GBK、Latin-1）
- ✅ 优化了数据字段映射和空值处理
- ✅ 增强了错误处理和错误信息反馈
- ✅ 添加了导入统计和详细结果显示
- ✅ 创建了示例CSV文件供下载使用
- ✅ 完善了API测试功能

## 支持的CSV格式

### 必需字段
CSV文件必须包含以下列（英文字段名）：
- `Country`: 国家名称
- `Year`: 年份（数字）
- `Life_expectancy`: 预期寿命（数字）

### 可选字段
以下字段可选，但建议包含以获得更完整的数据分析：
- `Adult_mortality`: 成人死亡率
- `Infant_deaths`: 婴儿死亡数
- `Alcohol_consumption`: 酒精消费
- `Under_five_deaths`: 五岁以下死亡数
- `Hepatitis_B`: 乙肝疫苗接种率
- `Measles`: 麻疹病例数
- `BMI`: BMI指数
- `Polio`: 脊髓灰质炎疫苗接种率
- `Diphtheria`: 白喉疫苗接种率
- `Incidents_HIV`: HIV/AIDS死亡率
- `GDP_per_capita`: GDP人均
- `Population_mln`: 人口数量(百万)
- `Thinness_ten_nineteen_years`: 10-19岁消瘦率
- `Thinness_five_nine_years`: 5-9岁消瘦率
- `Schooling`: 受教育年限
- `Economy_status_Developed`: 发达国家标志（0或1）
- `Economy_status_Developing`: 发展中国家标志（0或1）

## 使用步骤

### 1. 准备CSV文件
- 确保文件编码为UTF-8或GBK
- 第一行必须是字段名（表头）
- 数据从第二行开始
- 文件大小不超过10MB

### 2. 导入数据
1. 打开系统web界面
2. 点击"数据库管理"标签
3. 在"批量导入数据"区域选择CSV文件
4. 点击"上传并导入"按钮
5. 等待导入完成

### 3. 查看结果
- 导入成功后会显示导入统计信息
- 系统会自动刷新数据显示
- 可在"数据视图"标签中查看导入的数据

## 示例CSV文件格式

```csv
Country,Year,Life_expectancy,Adult_mortality,GDP_per_capita,Economy_status_Developed,Economy_status_Developing
TestCountry1,2020,75.5,150.2,15000,0,1
TestCountry2,2020,80.2,120.5,25000,1,0
TestCountry3,2021,77.8,135.7,18000,0,1
```

## 注意事项

1. **重复数据处理**: 如果导入的数据与已有数据的国家和年份相同，系统会自动更新现有记录
2. **数据验证**: 系统会自动跳过缺少必需字段的行
3. **错误处理**: 如果某行数据有问题，系统会跳过该行并继续处理其他行
4. **编码支持**: 系统会自动尝试UTF-8和GBK编码来读取文件

## 常见问题

### Q: 导入失败怎么办？
A: 检查CSV文件格式，确保包含必需字段，文件编码正确。

### Q: 部分数据导入失败？
A: 系统会显示成功导入的行数，失败的行会被跳过。检查数据格式是否正确。

### Q: 如何下载示例文件？
A: 在导入界面点击"下载CSV格式示例文件"链接。

## 技术支持
如果遇到问题，请检查：
1. 数据库连接是否正常
2. Flask服务器是否运行在端口5000
3. CSV文件格式是否符合要求
