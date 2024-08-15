"""
Description: 使用Gradio创建网页实现与用户交互。(流式输出)
Notes: 
代码来源于GLM4官方，没搞懂其中 `parse_text` 函数的作用。笔者尝试注释 `parse_text` 函数中所有代码，gradio依旧可以正常解析。
"""
import os
from pathlib import Path  # 用于处理文件和目录路径
from threading import Thread  # 用于多线程操作
from typing import Union  # 用于类型注解，允许多种类型
import gradio as gr  # Gradio是一个用于快速搭建Web界面的库
import torch
from transformers import (  # Transformers库，用于加载和使用预训练的语言模型
    AutoModelForCausalLM,
    AutoTokenizer,
    PreTrainedModel,
    PreTrainedTokenizer,
    PreTrainedTokenizerFast,
    StoppingCriteria,
    StoppingCriteriaList,
    TextIteratorStreamer
)

# 定义模型和分词器的路径，可以通过环境变量指定，或使用默认路径
MODEL_PATH = "/data/LLaMA-Factory-main/my_glm4_9b_chat"  # 模型路径，硬编码指定
TOKENIZER_PATH = os.environ.get("TOKENIZER_PATH", MODEL_PATH)  # 分词器路径，默认为模型路径

# 将路径字符串解析为Path对象，并解析用户目录和相对路径，返回绝对路径
def _resolve_path(path: Union[str, Path]) -> Path:
    return Path(path).expanduser().resolve()

# 加载模型和分词器
# 参数：
# - model_dir: 模型所在目录的路径
# - trust_remote_code: 是否信任远程加载的代码（默认为True）
# 返回值：
# - tuple[PreTrainedModel, PreTrainedTokenizer]: 返回加载的模型和分词器(均为整体的模型，非适配器+基座模型形式)
def load_model_and_tokenizer(
        model_dir: Union[str, Path], trust_remote_code: bool = True
) -> tuple[PreTrainedModel, PreTrainedTokenizer]:
    model_dir = _resolve_path(model_dir)  # 将路径解析为绝对路径
    # 加载普通CausalLM模型(非加载适配器方式)
    model = AutoModelForCausalLM.from_pretrained(
        model_dir, trust_remote_code=trust_remote_code, device_map='auto'
    )
    tokenizer_dir = model_dir  # 分词器路径与模型路径一致
    # 加载对应的分词器，use_fast=False 表示不使用快速分词器（某些模型不兼容）
    tokenizer = AutoTokenizer.from_pretrained(
        tokenizer_dir, trust_remote_code=trust_remote_code, use_fast=False
    )
    return model, tokenizer  # 返回加载的模型和分词器

# 加载指定路径的模型和分词器
model, tokenizer = load_model_and_tokenizer(MODEL_PATH, trust_remote_code=True)

# 自定义停止条件类，用于控制生成文本的停止条件
class StopOnTokens(StoppingCriteria):
    # 当生成的序列包含指定的结束标记时停止生成
    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor, **kwargs) -> bool:
        stop_ids = model.config.eos_token_id  # 获取模型的结束标记（end-of-sequence）ID
        for stop_id in stop_ids:
            if input_ids[0][-1] == stop_id:  # 如果生成的最后一个token是结束标记，则停止生成
                return True
        return False  # 否则继续生成

# 预测函数，根据历史记录和用户输入生成新的回复
# 参数：
# - history: 聊天历史记录
# - prompt: 系统提示（用于指定对话的上下文）
# - max_length: 生成的最大文本长度
# - top_p: top-p采样值，用于控制生成多样性
# - temperature: 温度值，用于控制生成的随机性
# 返回值：
# - 生成的回复（通过生成器逐步返回）
def predict(history, prompt, max_length, top_p, temperature):
    stop = StopOnTokens()  # 使用自定义的停止条件
    messages = []  # 存储对话消息的列表
    if prompt:  # 如果提供了prompt，将其作为系统消息添加到消息列表中
        messages.append({"role": "system", "content": prompt})
    for idx, (user_msg, model_msg) in enumerate(history):
        if prompt and idx == 0:  # 如果有prompt，跳过第一条历史记录
            continue
        if idx == len(history) - 1 and not model_msg:  # 如果是最后一条历史记录且模型尚未回复
            messages.append({"role": "user", "content": user_msg})  # 将用户消息添加到消息列表中
            break
        if user_msg:  # 如果存在用户消息，将其添加到消息列表中
            messages.append({"role": "user", "content": user_msg})
        if model_msg:  # 如果存在模型回复，将其添加到消息列表中
            messages.append({"role": "assistant", "content": model_msg})

    # 使用分词器将消息列表转换为模型输入格式
    model_inputs = tokenizer.apply_chat_template(messages,
                                                 add_generation_prompt=True,  # 添加生成提示
                                                 tokenize=True,  # 进行分词
                                                 return_tensors="pt"  # 返回PyTorch张量
                                                 ).to(next(model.parameters()).device)  # 将输入移动到模型所在设备
    # 创建流式生成器，控制生成过程中的输出行为
    streamer = TextIteratorStreamer(tokenizer, timeout=60, skip_prompt=True, skip_special_tokens=True)
    # 设置生成参数
    generate_kwargs = {
        "input_ids": model_inputs,  # 输入张量
        "streamer": streamer,  # 使用流式生成器
        "max_new_tokens": max_length,  # 最大生成长度
        "do_sample": True,  # 使用采样生成而不是贪婪搜索
        "top_p": top_p,  # top-p采样值
        "temperature": temperature,  # 控制生成的随机性
        "stopping_criteria": StoppingCriteriaList([stop]),  # 设置停止条件
        "repetition_penalty": 1.2,  # 惩罚重复生成，降低重复生成的可能性
        "eos_token_id": model.config.eos_token_id,  # 生成结束标记ID，控制生成结束
    }
    # 创建一个新线程，运行生成文本的任务，避免阻塞主线程
    t = Thread(target=model.generate, kwargs=generate_kwargs)
    t.start()  # 启动线程，开始生成
    for new_token in streamer:  # 使用流式生成器逐个获取生成的token
        if new_token:  # 如果生成了新的token
            history[-1][1] += new_token  # 将token添加到历史记录中最后一条回复的内容中
        yield history  # 逐步返回更新后的历史记录（生成器方式）

# 构建Gradio用户界面
with gr.Blocks() as demo:
    # 显示页面标题
    gr.HTML("""<h1 align="center">GLM-4-9B-Chat Gradio Simple Chat Demo</h1>""")
    chatbot = gr.Chatbot()  # 创建聊天机器人组件

    with gr.Row():  # 在页面中创建一行布局
        with gr.Column(scale=3):  # 定义一个占3/5宽度的列用于用户输入
            with gr.Column(scale=12):  # 在列中嵌套一个全宽度的列，用于文本框
                # 创建一个多行文本框，用于用户输入，隐藏标签，不使用容器
                user_input = gr.Textbox(show_label=False, placeholder="Input...", lines=10, container=False)
            with gr.Column(min_width=32, scale=1):  # 定义一个用于按钮的窄列
                submitBtn = gr.Button("Submit")  # 创建提交按钮
        with gr.Column(scale=1):  # 定义一个占1/5宽度的列用于设置prompt
            # 创建一个多行文本框，用于设置系统提示信息
            prompt_input = gr.Textbox(show_label=False, placeholder="Prompt", lines=10, container=False)
            pBtn = gr.Button("Set Prompt")  # 创建设置prompt按钮
        with gr.Column(scale=1):  # 定义另一个占1/5宽度的列用于其他设置
            emptyBtn = gr.Button("Clear History")  # 创建清空历史记录按钮
            # 创建滑块，用于设置生成文本的最大长度
            max_length = gr.Slider(0, 32768, value=8192, step=1.0, label="Maximum length", interactive=True)
            # 创建滑块，用于设置top-p采样值
            top_p = gr.Slider(0, 1, value=0.8, step=0.01, label="Top P", interactive=True)
            # 创建滑块，用于设置生成文本的温度值
            temperature = gr.Slider(0.01, 1, value=0.6, step=0.01, label="Temperature", interactive=True)

    # 定义用户提交输入后的处理函数
    # 参数：
    # - query: 用户输入的文本
    # - history: 聊天的历史记录
    # 返回值：
    # - 清空的输入框（返回空字符串）和更新的历史记录
    def user(query, history):
        return "", history + [[query, ""]]

    # 定义设置prompt的处理函数
    # 参数：
    # - prompt_text: 用户输入的prompt文本
    # 返回值：
    # - 更新后的聊天记录，显示成功设置prompt的消息
    def set_prompt(prompt_text):
        return [[prompt_text, "成功设置prompt"]]

    # 将设置prompt按钮的点击事件与set_prompt函数绑定
    pBtn.click(set_prompt, inputs=[prompt_input], outputs=chatbot)

    # 将提交按钮的点击事件与user函数和predict函数绑定
    submitBtn.click(user, [user_input, chatbot], [user_input, chatbot], queue=False).then(
        predict, [chatbot, prompt_input, max_length, top_p, temperature], chatbot
    )

    # 将清空历史记录按钮的点击事件绑定到重置聊天记录的函数
    emptyBtn.click(lambda: (None, None), None, [chatbot, prompt_input], queue=False)

# 启动Gradio应用，并在指定地址和端口上运行
demo.queue()  # 启用请求队列，确保多个请求顺序处理
demo.launch(server_name="0.0.0.0", server_port=8000, inbrowser=True, share=True)  # 启动Web应用