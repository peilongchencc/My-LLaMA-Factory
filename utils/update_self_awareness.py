"""
Description: 更新模型自我认知数据集
Notes: 
"""
import json

# NAME = "Llama-Chinese"  # 定义常量NAME，表示模型名称
# AUTHOR = "LLaMA Factory"  # 定义常量AUTHOR，表示作者名称

NAME = "My-Llama-Chinese"  # 定义常量NAME，表示模型名称
AUTHOR = "peilongchencc"  # 定义常量AUTHOR，表示作者名称

# 打开并读取data/identity.json文件，文件编码为utf-8
with open("data/identity.json", "r", encoding="utf-8") as f:
  dataset = json.load(f)  # 将文件内容加载为JSON对象

# 遍历JSON对象中的每个样本
for sample in dataset:
  # 替换样本中的占位符{{name}}和{{author}}为实际的NAME和AUTHOR值
  sample["output"] = sample["output"].replace("{{"+ "name" + "}}", NAME).replace("{{"+ "author" + "}}", AUTHOR)

# 将修改后的数据重新写回data/identity.json文件，确保文件格式美观且不转义非ASCII字符
with open("data/identity.json", "w", encoding="utf-8") as f:
  json.dump(dataset, f, indent=2, ensure_ascii=False)