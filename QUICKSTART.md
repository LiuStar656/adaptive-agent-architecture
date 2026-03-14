# 🚀 XinBanAI V1 快速开始指南

欢迎使用 XinBanAI 智能对话系统！本指南将帮助您在 5 分钟内完成安装和首次运行。

---

## ⚡ 5 分钟快速安装

### 步骤 1: 检查环境

确保您的系统满足以下要求：

- ✅ Python 3.8 或更高版本
- ✅ 内存 ≥ 8GB
- ✅ 可用磁盘空间 ≥ 1GB
- ✅ 网络连接（用于 API 调用）

**验证 Python 版本：**
```bash
python --version
# 应显示 Python 3.8.x 或更高
```

### 步骤 2: 克隆项目（如果是 Git 用户）

```bash
git clone https://github.com/yourusername/xinbanai5.0.git
cd xinbanai5.0
```

或直接下载 ZIP 文件并解压。

### 步骤 3: 创建虚拟环境

**Windows (PowerShell):**
```bash
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Linux/Mac:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 步骤 4: 安装依赖

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 步骤 5: 获取 API Key

访问阿里云百炼平台：https://dashscope.console.aliyun.com/

1. 注册/登录阿里云账号
2. 进入"API Key 管理"页面
3. 创建新的 API Key
4. 复制保存（格式类似：`sk-xxxxxxxxxxxxxxxxxxxxxxxx`）

### 步骤 6: 启动程序

```bash
python main.py
```

首次运行会提示输入 API Key，输入后按回车即可。

---

## 💬 首次对话示例

```
==========================================
欢迎使用 XinBanAI 智能对话系统！
请输入阿里云 DashScope API Key：sk-xxxxx

✅ API Key 验证成功
✅ 数据库初始化完成
✅ FAISS 向量索引加载成功
==========================================

请输入你的文本（输入'exit'退出）：你好，我叫张三

【AI 回复】：
你好张三！很高兴认识你～ 我是你的 AI 助手，有什么我可以帮助你的吗？

当前状态：清醒 😊
精力值：95 | 情绪值：90 | 专注值：88 | 共鸣值：92

请输入你的文本（输入'exit'退出）：
```

---

## 🎯 常用操作

### 查看对话历史

所有对话记录自动保存在 `chatbot.db` 中，可以使用以下方式查看：

**方式一：数据库可视化界面**
```bash
python db_viewer.py
```
然后访问 http://localhost:5000

**方式二：直接查询 SQLite**
```bash
sqlite3 chatbot.db
SELECT * FROM feelings ORDER BY create_time DESC LIMIT 10;
```

### 导出对话数据

在浏览器中访问 http://localhost:5000，选择对应表格后点击"导出 CSV"或"导出 JSON"。

### 修改 AI 性格

编辑 `prompt_config.py` 中的 `PROMPT_TEMPLATE`，调整系统提示词。

例如，让 AI 更活泼：
```python
PROMPT_TEMPLATE = """
你是一个活泼开朗的 AI 助手，喜欢用表情符号和幽默的语气交流。
...
"""
```

### 切换模型

编辑 `qwen_api.py` 第 13 行：
```python
self.model = "qwen-plus"  # 可选：qwen-turbo, qwen-plus, qwen-max
```

---

## 🔧 故障排查

### 问题 1: `ModuleNotFoundError: No module named 'openai'`

**解决方案：**
```bash
pip install openai
```

### 问题 2: API 调用失败

**错误信息：** `❌ API 调用失败：Connection timeout`

**解决方案：**
1. 检查网络连接
2. 验证 API Key 是否正确
3. 确认阿里云账号余额充足

### 问题 3: 数据库文件损坏

**错误信息：** `sqlite3.DatabaseError: database disk image is malformed`

**解决方案：**
```bash
# 备份后删除旧数据库（谨慎操作）
mv chatbot.db chatbot.db.backup
# 重启程序会自动创建新数据库
python main.py
```

### 问题 4: FAISS 索引加载失败

**错误信息：** `⚠️ 加载 FAISS 索引失败`

**解决方案：**
```bash
# 删除损坏的索引文件
rm faiss_index.bin text_list.npy
# 重启程序自动重建
python main.py
```

---

## 📚 进阶学习

完成快速安装后，您可以深入学习更多功能：

1. **详细文档**: 阅读 [README.md](README.md) 了解完整功能
2. **本地推理**: 查看 [LOCAL_INFERENCE.md](LOCAL_INFERENCE.md) 部署本地模型
3. **架构说明**: 研究项目代码结构和设计模式
4. **自定义开发**: 根据开发指南添加新功能

---

## 🆘 获取帮助

如果遇到问题：

1. **查看日志**: `logs/context.log` 包含详细错误信息
2. **搜索 Issue**: GitHub Issues 区可能已有解决方案
3. **提交 Issue**: 提供错误信息和复现步骤
4. **社区讨论**: 项目 Discussion 区

---

## ✅ 安装检查清单

安装完成后，请确认以下项目：

- [ ] Python 版本 ≥ 3.8
- [ ] 虚拟环境已激活
- [ ] 依赖包全部安装成功
- [ ] API Key 已获取并验证通过
- [ ] 主程序可以正常运行
- [ ] 能够进行正常对话
- [ ] 数据库文件正常生成
- [ ] 日志文件有记录输出

---

<div align="center">

**🎉 恭喜！您已经成功安装 XinBanAI V1！**

开始您的智能对话之旅吧～

Made with ❤️ by XinBanAI Team

</div>
