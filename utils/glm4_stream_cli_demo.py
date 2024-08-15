"""
本脚本通过 transformers后端 为 glm-4-9b-chat 模型创建了一个命令行界面（CLI）演示，允许用户通过命令行与模型进行交互。

使用方法：
- 运行当前脚本以启动CLI演示。
- 通过输入问题并接收回答与模型互动。

注意：本脚本包含了一个将markdown转换为纯文本的功能修改，以确保CLI界面能够正确显示格式化文本。

如果使用闪存注意力机制（flash attention），请安装flash-attn库，并在加载模型时添加参数 `attn_implementation="flash_attention_2"`。
"""
import torch
from threading import Thread
from transformers import AutoTokenizer, StoppingCriteria, StoppingCriteriaList, TextIteratorStreamer, AutoModel

# MODEL_PATH = os.environ.get('MODEL_PATH', 'THUDM/glm-4-9b-chat')
# 使用自定义的模型路径
MODEL_PATH = "/data/LLaMA-Factory-main/my_glm4_9b_chat"

# 初始化分词器，用于将输入文本转换为模型可以理解的格式
tokenizer = AutoTokenizer.from_pretrained(
    MODEL_PATH,
    trust_remote_code=True,             # 允许远程代码执行，用于加载模型和分词器
    encode_special_tokens=True          # 编码特殊标记，如开始和结束标记
)

# 加载预训练模型，并设置为评估模式（eval），不启用梯度计算
model = AutoModel.from_pretrained(
    MODEL_PATH,
    trust_remote_code=True,
    # attn_implementation="flash_attention_2", # 使用闪存注意力机制（提高速度和效率）
    # torch_dtype=torch.bfloat16, # 使用 flash-attn 时必须使用 bfloat16 或 float16 精度
    device_map="auto"                    # 自动选择设备（如 GPU 或 CPU）
).eval()

# 自定义停止条件类，用于判断何时停止生成
class StopOnTokens(StoppingCriteria):
    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor, **kwargs) -> bool:
        stop_ids = model.config.eos_token_id  # 获取模型的结束标记（EOS token）的 ID
        for stop_id in stop_ids:
            if input_ids[0][-1] == stop_id:   # 如果生成的最后一个标记是结束标记，则停止生成
                return True
        return False  # 否则继续生成

if __name__ == "__main__":
    history = []  # 保存对话历史，格式为[[用户输入, 模型回复], ...]
    max_length = 8192  # 模型生成的最大标记数
    top_p = 0.8  # 控制生成时选择概率最高的标记的阈值（多样性）
    temperature = 0.6  # 控制生成的随机性，值越低，生成的文本越确定
    stop = StopOnTokens()  # 实例化自定义的停止条件

    # 输出欢迎信息
    print("欢迎使用 GLM-4-9B 命令行聊天界面。请在下方输入您的消息。")
    
    while True:
        user_input = input("\nYou: ")  # 获取用户输入
        if user_input.lower() in ["exit", "quit"]:  # 如果输入 "exit" 或 "quit"，则退出循环
            break
        history.append([user_input, ""])  # 将用户输入添加到历史记录中

        # 准备消息列表，将历史对话转换为模型输入格式
        messages = []
        for idx, (user_msg, model_msg) in enumerate(history):
            if idx == len(history) - 1 and not model_msg:  # 对当前的用户输入创建消息
                messages.append({"role": "user", "content": user_msg})
                break
            if user_msg:
                messages.append({"role": "user", "content": user_msg})  # 添加用户的消息
            if model_msg:
                messages.append({"role": "assistant", "content": model_msg})  # 添加模型的回复

        # 将消息列表应用聊天模板并进行标记化
        model_inputs = tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,  # 添加生成提示符
            tokenize=True,               # 对输入进行标记化处理
            return_tensors="pt"          # 返回 PyTorch 张量
        ).to(model.device)  # 将输入移动到模型所在的设备上

        # 初始化流式生成器，用于实时输出生成的文本
        streamer = TextIteratorStreamer(
            tokenizer=tokenizer,
            timeout=60,                # 超时时间，单位为秒
            skip_prompt=True,          # 跳过输出提示符
            skip_special_tokens=True   # 跳过特殊标记，如 EOS
        )

        # 配置生成参数
        generate_kwargs = {
            "input_ids": model_inputs,
            "streamer": streamer,      # 使用流式生成器实时输出
            "max_new_tokens": max_length,  # 生成的最大标记数
            "do_sample": True,         # 启用采样（随机性）
            "top_p": top_p,            # 使用 nucleus 采样策略
            "temperature": temperature, # 控制生成的多样性
            "stopping_criteria": StoppingCriteriaList([stop]),  # 自定义停止条件
            "repetition_penalty": 1.2,  # 惩罚重复的标记，避免模型循环生成
            "eos_token_id": model.config.eos_token_id,  # 结束标记
        }

        # 启动生成线程，避免阻塞主线程
        t = Thread(target=model.generate, kwargs=generate_kwargs)
        t.start()

        print("GLM-4:", end="", flush=True)  # 实时输出生成结果
        for new_token in streamer:
            if new_token:
                print(new_token, end="", flush=True)  # 打印生成的标记
                history[-1][1] += new_token  # 将新生成的标记添加到对话历史中

        history[-1][1] = history[-1][1].strip()  # 移除生成结果的首尾空白字符