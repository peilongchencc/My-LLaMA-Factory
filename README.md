# My-LLaMA-Factory

LLaMA-Factory使用经验记录。

- [My-LLaMA-Factory](#my-llama-factory)
  - [文件简介:](#文件简介)
  - [鸣谢:](#鸣谢)

## 文件简介:

| 文件夹名称   | 作用           | 备注                |
|--------------|----------------|---------------------|
| data          | 数据集示例     |     |
| data_structure          | 数据集格式解释     | 仅介绍Alpaca格式    |
| easy_to_use          | 直接加载模型进行测试，体验LLaMA-Factory的使用     | Colab方式    |
| easy_to_train_model          | 使用项目本身数据集训练模型     | Colab方式    |
| custom_dataset_train          | 使用自定义数据集训练模型     | 服务器启动UI方式    |

utils文件夹下文件解释:

| 文件名称   | 作用           | 备注                |
|--------------|----------------|---------------------|
| split_dataset.py          | 切分数据集     | 用于Alpaca格式    |
| update_self_awareness.py          | 更新模型自我认知数据集     | 注意修改文件中的模型名称、作者名称    |
| update_self_awareness.py          | 更新模型自我认知数据集     | 注意修改文件中的模型名称、作者名称    |
| glm4_stream_cli_demo.py          | transformers 后端以命令行进行模型推理     | 流式输出    |
| glm4_stream_web_demo.py          | transformers 后端以web界面进行模型推理     | 流式输出    |


## 鸣谢:

感谢 [hiyouga](https://github.com/hiyouga) 的贡献，才能有 [**LLaMA-Factory**](https://github.com/hiyouga/LLaMA-Factory) 这么方便的工具。<br>
