# 使用自定义数据集训练模型

本章介绍如果使用自定义数据集(Alpaca格式)训练模型。如果你不清楚Alpaca格式，点击这里[查看教程](../data_structure/README.md)。

- [使用自定义数据集训练模型](#使用自定义数据集训练模型)
  - [1. 准备自定义数据集:](#1-准备自定义数据集)
  - [2. 将数据集放到LLaMA-Factory/data目录下:](#2-将数据集放到llama-factorydata目录下)
  - [3. 修改dataset\_info.json文件:](#3-修改dataset_infojson文件)
  - [4. 正式训练模型:](#4-正式训练模型)


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

只有将数据集放到 `LLaMA-Factory/data` 目录下，项目才能检索到。例如笔者使用的 `nurse_patient_data.json` 最终路径为:

```log
LLaMA-Factory/data/nurse_patient_data.json
```


## 3. 修改dataset_info.json文件:

`dataset_info.json` 包含了项目所有可用的数据集，如果想要使用自定义数据集，必须在 `dataset_info.json` 添加自己的数据集描述。

`dataset_info.json` 文件位置为:

```log
LLaMA-Factory/data/dataset_info.json
```

以笔者使用的 `nurse_patient_data.json` 为例，修改方式如下:

```json
{
  "identity": {
    "file_name": "identity.json"
  },
  "nurse_patient_data": {
    "file_name": "nurse_patient_data.json"  // 这里!关注这里!
  },
  "alpaca_en_demo": {
    "file_name": "alpaca_en_demo.json"
  },
  "alpaca_zh_demo": {
    "file_name": "alpaca_zh_demo.json"
  }
}
```

## 4. 正式训练模型:

其他操作都与 [easy_to_train_model](../easy_to_train_model/README.md) 中的操作相似，请自行查阅。