# 命令分析

本章介绍为什么在安装了 LLaMA Factory 后，用户可以在终端操作使用 `llamafactory-cli` 命令。

- [命令分析](#命令分析)
  - [`llamafactory-cli` 命令可以使用的原因:](#llamafactory-cli-命令可以使用的原因)
    - [`entry_points` 的作用:](#entry_points-的作用)
      - [`setup.py` 文件中的 `entry_points`:](#setuppy-文件中的-entry_points)
  - [执行`pip install -e .`后具体发生了什么:](#执行pip-install--e-后具体发生了什么)
  - [指令执行逻辑:](#指令执行逻辑)
  - [`llamafactory/cli.py`文件注释版(可选):](#llamafactoryclipy文件注释版可选)
    - [关键组件:](#关键组件)
  - [举例-终端运行`llamafactory-cli help`:](#举例-终端运行llamafactory-cli-help)
  - [附录: sys.argv 用法解释](#附录-sysargv-用法解释)


## `llamafactory-cli` 命令可以使用的原因:

### `entry_points` 的作用:

在 Python 项目中，`setup.py` 文件（或 `pyproject.toml` 文件）通常用于定义如何安装和配置这个包。`entry_points` 是 `setup.py` 文件中的一个配置选项，它允许你定义命令行工具，这些工具在安装后可以直接从终端调用。

#### `setup.py` 文件中的 `entry_points`:

```python
entry_points={
    'console_scripts': [
        'llamafactory-cli=llamafactory.cli:main',
    ],
},
```

这里的 `console_scripts` 是一类 `entry_points`，用于定义终端命令。每个终端命令通过 `'命令名=模块路径:函数名'` 的形式定义。

> [!CAUTION]
> 模块路径使用`.`，采用的是python模块导入的标准表示法，即 `import llamafactory.cli`。
> 寻找指定模块中的制定对象(函数)时固定要用冒号进行分隔。


## 执行`pip install -e .`后具体发生了什么:

当使用 `pip install -e .` 命令时，`setup.py` 文件中定义的命令行工具会被安装到系统的 PATH 中，使得可以直接在终端中使用。

具体来说，下列代码会自动生成一个 **可执行文件** 。这是 `pip` 处理 `console_scripts` 时的标准行为:

```python
entry_points={
    'console_scripts': [
        'llamafactory-cli=llamafactory.cli:main',
    ],
},
```

生成的结果可以通过 `which` 指令查看，例如:

```bash
# Linux系统可用
which llamafactory-cli
```

终端效果:

```log
(myenv) root@ubuntu22:/data/LLaMA-Factory-main# which llamafactory-cli
/home/vipuser/miniconda3/envs/myenv/bin/llamafactory-cli
```

🔥看着是不是和 **python解释器** 很像？我们再打印一下python解释器的路径看一下:

```log
(myenv) root@ubuntu22:/data/LLaMA-Factory-main# which llamafactory-cli
/home/vipuser/miniconda3/envs/myenv/bin/llamafactory-cli

(myenv) root@ubuntu22:/data/LLaMA-Factory-main# which python
/home/vipuser/miniconda3/envs/myenv/bin/python
```

看出来了吧，这其实就是一个 **python解释器**，只是还有一些额外功能。例如:

- 导入 `llamafactory.cli` 模块
- 执行 `main()` 函数


## 指令执行逻辑:

当你在终端输入 `llamafactory-cli` 时：

1. **系统搜索路径**：系统会检查所有在 `PATH` 环境变量中的目录，寻找名为 `llamafactory-cli` 的可执行文件。

2. **执行可执行文件**：找到后，系统会执行该文件。该文件内部实际上是调用 Python 解释器，运行相应的模块和函数，即 `llamafactory.cli:main`。找到 `llamafactory/cli.py` 文件，并执行里面的 `main()` 函数。

3. **运行代码**：`main()` 函数会根据输入的参数决定要执行的具体逻辑。


## `llamafactory/cli.py`文件注释版(可选):

读者可以简单看一下 `llamafactory/cli.py` 文件中的代码逻辑，方便理解之后的内容。

```python
import os  # 导入操作系统相关的模块
import random  # 导入生成随机数的模块
import subprocess  # 导入执行子进程的模块
import sys  # 导入与Python解释器交互的模块
from enum import Enum, unique  # 从enum模块导入Enum类和unique装饰器

# 导入LLaMA Factory项目中的其他模块和函数
from . import launcher  # 导入launcher模块
from .api.app import run_api  # 导入run_api函数，用于启动API服务器
from .chat.chat_model import run_chat  # 导入run_chat函数，用于启动聊天模型
from .eval.evaluator import run_eval  # 导入run_eval函数，用于评估模型
from .extras.env import VERSION, print_env  # 导入版本信息和打印环境信息的函数
from .extras.logging import get_logger  # 导入日志记录器
from .extras.misc import get_device_count  # 导入获取设备数量的函数
from .train.tuner import export_model, run_exp  # 导入模型导出和实验运行的函数
from .webui.interface import run_web_demo, run_web_ui  # 导入启动Web演示和Web UI的函数

# 定义命令行使用帮助信息
USAGE = (
    "-" * 70  # 输出70个字符长度的横线
    + "\n"
    + "| Usage:                                                             |\n"
    + "|   llamafactory-cli api -h: launch an OpenAI-style API server       |\n"  # 启动类似OpenAI风格的API服务器
    + "|   llamafactory-cli chat -h: launch a chat interface in CLI         |\n"  # 启动命令行聊天界面
    + "|   llamafactory-cli eval -h: evaluate models                        |\n"  # 评估模型
    + "|   llamafactory-cli export -h: merge LoRA adapters and export model |\n"  # 合并LoRA适配器并导出模型
    + "|   llamafactory-cli train -h: train models                          |\n"  # 训练模型
    + "|   llamafactory-cli webchat -h: launch a chat interface in Web UI   |\n"  # 启动Web聊天界面
    + "|   llamafactory-cli webui: launch LlamaBoard                        |\n"  # 启动LlamaBoard Web界面
    + "|   llamafactory-cli version: show version info                      |\n"  # 显示版本信息
    + "-" * 70  # 输出70个字符长度的横线
)

# 定义欢迎信息，包含版本号和项目页面链接
WELCOME = (
    "-" * 58
    + "\n"
    + "| Welcome to LLaMA Factory, version {}".format(VERSION)  # 显示当前版本号
    + " " * (21 - len(VERSION))
    + "|\n|"
    + " " * 56
    + "|\n"
    + "| Project page: https://github.com/hiyouga/LLaMA-Factory |\n"  # 显示项目页面链接
    + "-" * 58
)

# 获取日志记录器实例
logger = get_logger(__name__)

# 定义命令枚举类，包含各种可能的命令
@unique  # 使用unique装饰器确保枚举值唯一
class Command(str, Enum):
    API = "api"  # 启动API服务器
    CHAT = "chat"  # 启动聊天界面
    ENV = "env"  # 打印环境信息
    EVAL = "eval"  # 评估模型
    EXPORT = "export"  # 导出模型
    TRAIN = "train"  # 训练模型
    WEBDEMO = "webchat"  # 启动Web聊天界面
    WEBUI = "webui"  # 启动Web UI
    VER = "version"  # 显示版本信息
    HELP = "help"  # 显示帮助信息

# 定义主函数，解析并执行命令行输入
def main():
    # 从命令行参数中获取命令，如果没有参数，则默认为HELP命令
    command = sys.argv.pop(1) if len(sys.argv) != 1 else Command.HELP
    # 根据命令执行对应的功能
    if command == Command.API:
        run_api()  # 启动API服务器
    elif command == Command.CHAT:
        run_chat()  # 启动聊天界面
    elif command == Command.ENV:
        print_env()  # 打印环境信息
    elif command == Command.EVAL:
        run_eval()  # 评估模型
    elif command == Command.EXPORT:
        export_model()  # 导出模型
    elif command == Command.TRAIN:
        # 检查是否需要强制使用torchrun进行分布式训练
        force_torchrun = os.environ.get("FORCE_TORCHRUN", "0").lower() in ["true", "1"]
        # 如果需要使用torchrun或设备数量大于1，则进行分布式训练
        if force_torchrun or get_device_count() > 1:
            # 获取分布式训练所需的主节点地址和端口
            master_addr = os.environ.get("MASTER_ADDR", "127.0.0.1")
            master_port = os.environ.get("MASTER_PORT", str(random.randint(20001, 29999)))
            logger.info("Initializing distributed tasks at: {}:{}".format(master_addr, master_port))
            # 使用torchrun启动分布式训练任务
            process = subprocess.run(
                (
                    "torchrun --nnodes {nnodes} --node_rank {node_rank} --nproc_per_node {nproc_per_node} "
                    "--master_addr {master_addr} --master_port {master_port} {file_name} {args}"
                ).format(
                    nnodes=os.environ.get("NNODES", "1"),  # 获取节点数量
                    node_rank=os.environ.get("RANK", "0"),  # 获取节点排名
                    nproc_per_node=os.environ.get("NPROC_PER_NODE", str(get_device_count())),  # 获取每个节点的进程数量
                    master_addr=master_addr,  # 使用的主节点地址
                    master_port=master_port,  # 使用的主节点端口
                    file_name=launcher.__file__,  # 启动的文件名
                    args=" ".join(sys.argv[1:]),  # 传递给torchrun的额外参数
                ),
                shell=True,  # 在shell中运行命令
            )
            sys.exit(process.returncode)  # 退出并返回子进程的退出状态
        else:
            run_exp()  # 启动单节点训练
    elif command == Command.WEBDEMO:
        run_web_demo()  # 启动Web演示界面
    elif command == Command.WEBUI:
        run_web_ui()  # 启动Web UI界面
    elif command == Command.VER:
        print(WELCOME)  # 显示欢迎信息和版本号
    elif command == Command.HELP:
        print(USAGE)  # 显示使用帮助信息
    else:
        raise NotImplementedError("Unknown command: {}".format(command))  # 抛出未实现的命令错误
```

从 `llamafactory/cli.py` 文件的代码可以看出，`llamafactory-cli` 命令行工具的主要逻辑就是解析用户输入的命令，并根据不同的命令调用相应的函数来执行具体的任务。

下面是一些关键点的解释:

### 关键组件:

1. **命令枚举 (`Command` Enum)**:
    
    - `Command` 是一个枚举类，定义了所有可以通过 `llamafactory-cli` 使用的命令，包括 `api`、`chat`、`eval`、`export`、`train`、`webchat`、`webui` 等。

2. **`main` 函数**:
    
    - `main` 函数是命令行工具的入口点，负责解析用户输入的命令并根据相应的命令执行对应的功能。
    
    - `sys.argv.pop(1)` 获取命令行中的第一个参数作为命令，如果没有输入命令则默认使用 `Command.HELP`（即帮助信息）。
    
    - 根据解析出的命令，`main` 函数会调用不同的函数，例如 `run_api()` 启动 API 服务器，`run_web_ui()` 启动 `webui` 界面等。

3. **命令的实现**:

    - 每个命令背后都有对应的函数，比如:

        - `Command.WEBUI` 对应 `run_web_ui()`，启动 Web 界面。

        - `Command.TRAIN` 对应 `run_exp()` 或 `torchrun` 分布式训练任务。

        - `Command.VER` 显示欢迎信息。

    - 如果你想查看每个子命令具体做了什么，可以深入到这些子命令所对应的函数（如 `run_web_ui()`）的实现文件中去。


## 举例-终端运行`llamafactory-cli help`:

讲了那么多，现在为代码添加一下 `print`，验证下前面讲的内容。读者可以按照以下方式修改 `llamafactory/cli.py` 中的代码:

```python
# llamafactory/cli.py

# 其他代码省略

def main():
    print(f"sys.argv为:{sys.argv}")
    pop_value = sys.argv.pop(1)
    print(f"sys.argv.pop(1)为:{pop_value}，类型:{type(pop_value)}")
    
    command = sys.argv.pop(1) if len(sys.argv) != 1 else Command.HELP
    # 其他代码省略
```

当终端运行`llamafactory-cli help`时:

```log
(myenv) root@ubuntu22:/data/LLaMA-Factory-main# llamafactory-cli help
sys.argv为:['/home/vipuser/miniconda3/envs/myenv/bin/llamafactory-cli', 'help']
sys.argv.pop(1)为:help，类型:<class 'str'>
----------------------------------------------------------------------
| Usage:                                                             |
|   llamafactory-cli api -h: launch an OpenAI-style API server       |
|   llamafactory-cli chat -h: launch a chat interface in CLI         |
|   llamafactory-cli eval -h: evaluate models                        |
|   llamafactory-cli export -h: merge LoRA adapters and export model |
|   llamafactory-cli train -h: train models                          |
|   llamafactory-cli webchat -h: launch a chat interface in Web UI   |
|   llamafactory-cli webui: launch LlamaBoard                        |
|   llamafactory-cli version: show version info                      |
----------------------------------------------------------------------
(myenv) root@ubuntu22:/data/LLaMA-Factory-main# 
```

从代码中可以看出，触发了下列逻辑:

```python
# 其他代码省略
    elif command == Command.HELP:
        print(USAGE)  # 显示使用帮助信息
# 其他代码省略
```


## 附录: sys.argv 用法解释

`sys.argv` 是一个包含命令行参数的列表，其中：

- `sys.argv[0]` 是脚本的名称或命令名（如 `llamafactory-cli`）。

- `sys.argv[1]` 及之后的元素是传递给脚本的参数。

`sys.argv.pop(1)` 的作用是从命令行参数列表 `sys.argv` 中移除并返回索引为 `1` 的元素。

例如你在终端输入下列指令(这个命令是笔者虚构的):

```bash
llamafactory-cli webui --port 8080
```

则 `sys.argv` 列表的内容如下：

```python
sys.argv = ['llamafactory-cli', 'webui', '--port', '8080']
```

调用 `sys.argv.pop(1)` 后，`sys.argv` 发生以下变化：

- **返回值**：`'webui'`（因为这是索引为 `1` 的元素）

- **修改后的 `sys.argv` 列表**：

```python
sys.argv = ['llamafactory-cli', '--port', '8080']
```