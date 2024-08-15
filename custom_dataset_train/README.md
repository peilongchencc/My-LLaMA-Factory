# 使用自定义数据集训练模型

本章介绍如果使用自定义数据集(Alpaca格式)训练模型。如果你不清楚Alpaca格式，点击这里[查看教程](../data_structure/README.md)。

- [使用自定义数据集训练模型](#使用自定义数据集训练模型)
  - [1. 准备自定义数据集:](#1-准备自定义数据集)
  - [2. 将数据集放到LLaMA-Factory/data目录下:](#2-将数据集放到llama-factorydata目录下)
  - [3. 修改dataset\_info.json文件:](#3-修改dataset_infojson文件)
  - [4. 参数、数据集设置:](#4-参数数据集设置)
  - [5. 训练模型:](#5-训练模型)
  - [6. 模型评估:](#6-模型评估)
  - [7. 新模型测试:](#7-新模型测试)
  - [8. 模型导出:](#8-模型导出)


## 1. 准备自定义数据集:

数据集可参考当前项目文件的data模块:

[训练集](..data/nurse_patient_data_train.json)。

[测试集](..data/nurse_patient_data_test.json)。

> [!CAUTION]
> llama-factory需要自己划分数据集，"split" 参数是用来定位 HF 或 魔搭 中已划分好的数据集的。

例如llama-factory中 `data/dataset_info.json` 的下列内容:

```json
{
  "adgen_train": {
    "hf_hub_url": "HasturOfficial/adgen",
    "ms_hub_url": "AI-ModelScope/adgen",
    "split": "train",
    "columns": {
      "prompt": "content",
      "response": "summary"
    }
  },
  "adgen_eval": {
    "hf_hub_url": "HasturOfficial/adgen",
    "ms_hub_url": "AI-ModelScope/adgen",
    "split": "validation",
    "columns": {
      "prompt": "content",
      "response": "summary"
    }
  }
}
```

![](../docs/adgen数据集结构.png)


## 2. 将数据集放到LLaMA-Factory/data目录下:

只有将数据集放到 `LLaMA-Factory/data` 目录下，项目才能检索到。例如笔者使用的数据最终路径为:

```log
LLaMA-Factory/data/nurse_patient_data_train.json
LLaMA-Factory/data/nurse_patient_data_test.json
```


## 3. 修改dataset_info.json文件:

`dataset_info.json` 包含了项目所有可用的数据集，如果想要使用自定义数据集，必须在 `dataset_info.json` 添加自己的数据集描述。

`dataset_info.json` 文件位置为:

```log
LLaMA-Factory/data/dataset_info.json
```

以笔者使用的数据为例，修改方式如下:

```json
{
  "identity": {
    "file_name": "identity.json"
  },
  "nurse_patient_data_train": {
    "file_name": "nurse_patient_data_train.json"  // 这里!关注这里!
  },
  "nurse_patient_data_test": {
    "file_name": "nurse_patient_data_test.json"  // 这里!关注这里!
  },
  "alpaca_en_demo": {
    "file_name": "alpaca_en_demo.json"
  },
  "alpaca_zh_demo": {
    "file_name": "alpaca_zh_demo.json"
  }
}
```


## 4. 参数、数据集设置:

![](../docs/参数_数据集设置.png)


## 5. 训练模型:

点击开始，系统会自动下载模型。当显示进度条，loss逐渐变化时，模型即开始训练，效果如下图:

![](../docs/glm4训练示例.png)

如果Loss没有收敛或降低到1以下，可以选择继续训练模型。


## 6. 模型评估:

![](../docs/模型评估.png)


## 7. 新模型测试:

![](../docs/新模型测试.png)

输入内容测试下效果:

![](../docs/新模型测试_2.png)


## 8. 模型导出:

![](../docs/模型导出_完整.png)
