# 🧠 本地推理模型适配指南

## ⚠️ 重要提示

**本地推理功能目前处于实验性适配阶段，推荐使用云端 API 版本（Qwen API）以获得稳定体验。**

如果您希望尝试本地部署大语言模型，请仔细阅读以下说明。

---

## 📋 当前状态

### ✅ 已实现功能（XinBanAI V1）
- Qwen2.5-7B-4bit 量化模型支持（GGUF 格式）
- llama-cpp-python 推理引擎集成
- CPU 模式运行（无需 GPU）
- 基础对话功能正常

### 🔧 适配中功能
- 性能优化（当前生成速度 1.7-3.2 tokens/秒）【目标版本 v5.1】
- 内存管理优化
- Prompt 格式兼容性测试
- 长上下文窗口支持

### ❌ 已知限制
- 首次加载时间较长（约 30-60 秒）
- 生成速度受 CPU 性能影响较大
- 某些复杂推理任务可能不如云端 API 准确
- 不支持流式输出（正在开发中）【计划在 v5.1 版本解决】

---

## 🛠️ 安装步骤

### 1. 环境要求

- **操作系统**: Windows 10/11, Linux, macOS
- **Python 版本**: 3.8 - 3.11
- **内存要求**: 
  - 最低：16GB RAM
  - 推荐：32GB RAM（i9 第 12 代或同级 CPU 可高效运行）
- **磁盘空间**: 至少 10GB 可用空间

### 2. 下载模型文件

从 Hugging Face 或 ModelScope 下载量化后的 GGUF 格式模型：

```bash
# 推荐模型：Qwen2.5-7B-Instruct-Q4_K_M.gguf（约 4.3GB）
# 下载地址：
# - Hugging Face: https://huggingface.co/Qwen/Qwen2.5-7B-Instruct-GGUF
# - ModelScope: https://modelscope.cn/models/qwen/Qwen2.5-7B-Instruct-GGUF
```

将下载的模型文件放入项目目录：

```
xinbanai5.0/
├── models/
│   └── qwen2.5-7b-instruct-q4_k_m.gguf
```

### 3. 安装依赖

#### Windows 用户

```bash
# 创建虚拟环境
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1

# 升级 pip
python -m pip install --upgrade pip

# 安装 llama-cpp-python（需要编译环境）
pip install llama-cpp-python requests tqdm

# 如果编译失败，使用预编译 wheel
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu
```

#### Linux/Mac 用户

```bash
# 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate

# 升级 pip
pip install --upgrade pip

# 安装系统依赖（Ubuntu/Debian）
sudo apt-get install build-essential

# 安装 llama-cpp-python
pip install llama-cpp-python requests tqdm

# Mac (Apple Silicon) 可使用 Metal 加速
CMAKE_ARGS="-DLLAMA_METAL=on" pip install llama-cpp-python
```

### 4. 验证安装

运行测试脚本：

```bash
python local_qwen_model.py
```

如果看到类似输出，说明安装成功：

```
✅ 模型加载成功
输入测试问题：你好
AI 回复：你好！有什么我可以帮助你的吗？
```

---

## 🚀 使用方法

### 方式一：使用本地模型启动器

```bash
python local_qwen_model.py
```

### 方式二：在主程序中切换

编辑 `main.py` 或创建新的启动脚本：

```python
from local_qwen_model import LocalQwenModel

# 初始化本地模型
llm = LocalQwenModel(
    model_path="models/qwen2.5-7b-instruct-q4_k_m.gguf",
    n_ctx=2048,        # 上下文窗口
    n_threads=8        # CPU 线程数
)

# 调用模型
response = llm.generate("你好，请介绍一下自己")
print(response)
```

### 方式三：通过 API 接口（开发中）

```python
from flask import Flask, request, jsonify
from local_qwen_model import LocalQwenModel

app = Flask(__name__)
llm = LocalQwenModel(model_path="models/qwen2.5-7b-instruct-q4_k_m.gguf")

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    prompt = data.get('prompt', '')
    response = llm.generate(prompt)
    return jsonify({'response': response})
```

---

## ⚙️ 配置选项

在 `local_qwen_model.py` 中调整参数：

```python
n_ctx = 2048          # 上下文窗口大小（最大 4096）
n_threads = os.cpu_count()  # CPU 线程数
n_gpu_layers = 0      # GPU 层数（0=纯 CPU，>0=GPU 加速）
n_batch = 512         # 批处理大小
```

### 性能调优建议

| 配置 | 低配电脑 | 高配电脑 |
|------|----------|----------|
| n_ctx | 1024 | 4096 |
| n_threads | 4 | 16 |
| n_batch | 256 | 1024 |

---

## 🐛 常见问题

### 1. 安装失败：`llama-cpp-python` 编译错误

**解决方案：**

```bash
# Windows：使用预编译版本
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu

# 或先安装 Visual Studio Build Tools
# https://visualstudio.microsoft.com/zh-hans/visual-cpp-build-tools/

# Linux：安装编译工具链
sudo apt-get install build-essential cmake

# Mac：安装 Xcode Command Line Tools
xcode-select --install
```

### 2. 模型加载失败：`Segmentation fault`

**可能原因：**
- 模型文件损坏
- 内存不足

**解决方案：**
- 重新下载模型文件并校验 MD5
- 关闭其他占用内存的程序
- 减少 `n_ctx` 参数值

### 3. 生成速度过慢（<1 token/秒）

**优化方案：**
- 增加 `n_threads` 到 CPU 核心数的 80%
- 减少 `n_ctx` 到 1024 或 512
- 考虑使用更小的模型（如 Qwen-1.8B）

### 4. 输出乱码或格式错误

**解决方案：**
- 检查 Prompt 格式是否符合 Qwen2.5 规范
- 确保使用正确的 tokenizer
- 更新 llama-cpp-python 到最新版本

---

## 📊 性能基准测试

### 测试环境
- CPU: Intel i9-12900K (16 核 24 线程)
- 内存：32GB DDR4
- 模型：Qwen2.5-7B-4bit (Q4_K_M)

### 测试结果

| 指标 | 数值 |
|------|------|
| 模型加载时间 | ~45 秒 |
| 首 Token 延迟 | ~3 秒 |
| 平均生成速度 | 2.5 tokens/秒 |
| 内存占用 | ~8GB |
| CPU 占用率 | 100%（满载） |

### 不同硬件对比

| 硬件配置 | 生成速度 | 推荐度 |
|----------|----------|--------|
| i9-12900K + 32GB | 2.5 t/s | ⭐⭐⭐⭐ |
| i7-10700K + 16GB | 1.8 t/s | ⭐⭐⭐ |
| Ryzen 7 5800X + 32GB | 2.2 t/s | ⭐⭐⭐⭐ |
| M1 Pro + 16GB | 3.5 t/s | ⭐⭐⭐⭐⭐ |

---

## 🔮 未来计划

### 短期目标（V1.1）
- [ ] 支持流式输出
- [ ] 优化首次加载速度
- [ ] 添加 GPU 加速支持（CUDA/Metal）
- [ ] 改进 Prompt 格式兼容性

### 中期目标（V1.2）
- [ ] 支持更多量化格式（Q3_K_S, Q5_K_M）
- [ ] 多模型热切换
- [ ] 模型自动下载和更新
- [ ] 性能监控和日志系统

### 长期愿景
- [ ] 支持 70B+ 超大模型
- [ ] 分布式推理
- [ ] 混合精度推理
- [ ] 边缘设备部署（手机/平板）

---

## 📚 参考资料

- [llama-cpp-python 官方文档](https://github.com/abetlen/llama-cpp-python)
- [Qwen2.5 官方文档](https://qwen.readthedocs.io/)
- [GGUF 格式说明](https://github.com/ggerganov/ggml/blob/master/docs/gguf.md)
- [阿里云百炼平台](https://help.aliyun.com/zh/dashscope/)

---

## 🆘 获取帮助

如果遇到无法解决的问题：

1. **查看日志文件**: `logs/context.log`
2. **提交 Issue**: GitHub 仓库 Issues 区
3. **社区讨论**: 项目 Discussion 区

---

<div align="center">

**⚠️ 再次提醒：本地推理仍处于适配阶段，生产环境建议使用云端 API**

Made with ❤️ by XinBanAI Team

</div>
