"""
Description: 切分数据集
Notes: 
"""
import json
import random

# 读取 JSON 文件中的数据
with open('nurse_patient_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 打乱数据
random.shuffle(data)

# 计算验证集大小
val_size = int(len(data) * 0.1)

# 切分数据集
val_data = data[:val_size]
train_data = data[val_size:]

# 输出结果
print("训练集大小:", len(train_data))
print("验证集大小:", len(val_data))

# 保存到新的 JSON 文件
with open('train_data.json', 'w', encoding='utf-8') as f_train:
    json.dump(train_data, f_train, ensure_ascii=False, indent=4)

with open('val_data.json', 'w', encoding='utf-8') as f_val:
    json.dump(val_data, f_val, ensure_ascii=False, indent=4)