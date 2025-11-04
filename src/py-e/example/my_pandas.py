import pandas as pd

# 新建并保存 Excel
data = {
    "ID": [1, 2, 3, 4],
    "Name": ["Alice", "Bob", "Charlie", "Diana"],
    "Department": ["HR", "IT", "Finance", "IT"],
    "Salary": [5000, 7000, 6000, 7500]
}
df = pd.DataFrame(data)
filename = "/Users/jiaxiaopeng/employees_pandas.xlsx"
df.to_excel(filename, index=False)
print(f"✅ 使用 pandas 创建了 {filename}")

# 读取 Excel
df_read = pd.read_excel(filename)

# 搜索：Name 包含 'a'（不区分大小写）
result1 = df_read[df_read["Name"].str.contains("a", case=False, na=False)]
print("\n🔍 Name 包含 'a' 的员工:")
print(result1)

# 搜索：Department 为 IT
result2 = df_read[df_read["Department"] == "IT"]
print("\n🔍 IT 部门员工:")
print(result2)