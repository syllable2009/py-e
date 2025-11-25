
import json

json_str = '''{}'''
# 1. 解析 JSON 字符串,json字符串需要转义
data = json.loads(json_str)

# 2. 提取 FOLOCATION 列表
locations = data["result"]["FOLOCATION"]

# 3. 构建 {code: description} 字典
code_to_desc = {item["code"]: item["description"] for item in locations}

# 4. 输出结果
for idx, (key, value) in enumerate(code_to_desc.items(), start=1):
    print(f"{idx}. {key}={value}")