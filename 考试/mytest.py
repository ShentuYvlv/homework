import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
# ==========================================
# 任务 1：问题与目标
# ==========================================
# 目标：分析2030年自动化概率对薪资价值的影响，并对比不同学历等级的职业发展。


# 1. 读取数据 (通常中文CSV用gbk或utf-8编码)
try:
    df = pd.read_csv('mydata.csv')
except UnicodeDecodeError:
    df = pd.read_csv('mydata.csv', encoding='gbk')

# 2. 生成计算字段 calcol 
# 【修改点】：使用正确的列名 Automation_Probability_2030
# 含义：扣除自动化概率后的“折算薪资”
df['calcol'] = df['Average_Salary'] * (1 - df['Automation_Probability_2030'])

print(">>> 2完成，calcol字段已生成。")
print(df[['Job_Title', 'calcol']].head(3)) # 打印预览一下

# 1. 处理时间列：将“Years_Experience”分箱
bins = [0, 5, 15, 100]
labels = ['早期(0-5年)', '中期(5-15年)', '资深(15年以上)']
df['Career_Stage'] = pd.cut(df['Years_Experience'], bins=bins, labels=labels)

# 2. 交叉统计
# 【修改点】：使用正确的列名 Education_Level
pivot_res = pd.pivot_table(
    df, 
    index='Education_Level',    # 行：学历等级 (注意这里改成了 Education_Level)
    columns='Career_Stage',     # 列：职业阶段
    values='Average_Salary',    # 值：平均薪资
    aggfunc='mean'              # 统计方式：求均值
)

print("\n>>> 3：交叉列联统计结果")
print(pivot_res)

mean_val = df['Average_Salary'].mean()

high_salary = df[df['Average_Salary'] > mean_val]

top_5_result = high_salary.sort_values(by='Average_Salary', ascending=False).head(5)

print(f"\n>>> 4：薪资均值线为 {mean_val:.2f}")
print(">>> 前5行数据：")

cols_to_show = ['Job_Title', 'Average_Salary', 'Years_Experience', 'Education_Level', 'Automation_Probability_2030', 'calcol']
print(top_5_result[cols_to_show])



# 任务 2 (绘图篇)：绘制堆积条形图

plt.rcParams['font.sans-serif'] = ['SimHei'] 
plt.rcParams['axes.unicode_minus'] = False 

plot_data = df.groupby(['Education_Level', 'Career_Stage'])['Average_Salary'].mean().unstack()

ax = plot_data.plot(kind='bar', stacked=True, figsize=(10, 6), colormap='viridis')

plt.title('不同学历在各职业阶段的平均薪资堆积图', fontsize=16) # 图标题
plt.xlabel('学历等级 (Education Level)', fontsize=12)          # X轴标签
plt.ylabel('平均薪资 (Average Salary)', fontsize=12)           # Y轴标签

plt.legend(title='职业阶段 (时间跨度)', bbox_to_anchor=(1.05, 1), loc='upper left')

plt.xticks(rotation=0) 

plt.tight_layout() # 自动调整布局防止被遮挡
plt.show()

print(">>> 任务2图表已绘制，请查看弹出的窗口。")


# ==========================================
# 任务 4：聚类分析与最终报告
# ==========================================
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import seaborn as sns

features = ['Average_Salary', 'Automation_Probability_2030', 'AI_Exposure_Index']
data_for_clustering = df[features].dropna() # 去除空值

scaler = StandardScaler()
scaled_data = scaler.fit_transform(data_for_clustering)

kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
df['Cluster'] = kmeans.fit_predict(scaled_data)

plt.figure(figsize=(10, 6))
# 绘制散点图：X轴为自动化概率，Y轴为薪资，颜色为聚类结果
sns.scatterplot(
    data=df, 
    x='Automation_Probability_2030', 
    y='Average_Salary', 
    hue='Cluster', 
    palette='viridis', 
    s=100, 
    alpha=0.8
)

plt.title('岗位聚类分析：薪资 vs 自动化风险', fontsize=16)
plt.xlabel('2030年自动化概率 (Automation Probability)', fontsize=12)
plt.ylabel('平均薪资 (Average Salary)', fontsize=12)
plt.axvline(x=0.5, color='r', linestyle='--', alpha=0.5) # 添加一条0.5概率的分割线
plt.legend(title='聚类类别')
plt.grid(True, alpha=0.3)
plt.show()
