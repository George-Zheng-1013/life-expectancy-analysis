#用于设置联合主键为国家和年份
ALTER TABLE life_expectancy MODIFY COLUMN `国家` VARCHAR(100) NOT NULL;
ALTER TABLE life_expectancy ADD PRIMARY KEY (`国家`, `年份`);