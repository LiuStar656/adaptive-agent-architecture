# 🤖 XinBanAI V1 - 自适应AI运行框架

基于阿里云百炼 Qwen 大模型的本地智能对话系统，具备情感认知、长期记忆、定时任务触发等高级功能。

> **⚠️ 重要提示**：本地推理模型（Qwen2.5-7B）功能目前处于**实验性适配阶段**，推荐使用云端 API 版本以获得稳定体验。详见 [LOCAL_INFERENCE.md](LOCAL_INFERENCE.md).

---

## ✨ 核心特性

- **🧠 情感认知系统**：四维情绪指标（精力/情绪/专注/共鸣），五种状态自动切换（清醒/打盹/小憩/午休/睡眠）
- **💾 长期记忆管理**：SQLite 持久化存储 + FAISS 向量检索，支持语意关联和历史召回
- **⏰ 智能定时任务**：基于 AI 自主决策的延迟任务调度，支持 180 秒~8 小时灵活配置
- **🔄 增量认知适应**：动态构建用户画像和 AI 自我认知，持续学习不重复
- **🛡️ 优雅降级机制**：FAISS 不可用时自动切换 SQLite 检索，保证服务连续性
- **🔒 数据完全本地**：所有数据存储于本地，无云端通信，隐私安全
- **🚀 双模部署**：支持云端 API（推荐）和本地推理（实验性）两种模式

---

## 🏗️ 系统架构

```
┌─────────────────────────────────────────┐
│         用户交互层 (CLI 输入)             │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│      功能层 (ChatbotCore 核心业务逻辑)    │
│  - Prompt 拼接                           │
│  - AI 调用调度                            │
│  - 指令解析                              │
│  - 定时任务管理                          │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│       读取层 (DataReader 数据整合)        │
│  - 数据库读取                            │
│  - 状态计算                              │
│  - 向量检索                              │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│   模块层 (独立功能模块)                   │
│  ┌─────────┬──────────┬────────┬──────┐ │
│  │SQLiteDB │EventSumm │FAISS   │QwenAPI│ │
│  │数据库   │事件摘要  │向量检索│大模型 │ │
│  └─────────┴──────────┴────────┴──────┘ │
└─────────────────────────────────────────┘
```

### 分层职责

| 层级 | 组件 | 职责 |
|------|------|------|
| **用户交互层** | CLI | 接收用户输入，展示对话结果 |
| **功能层** | [`ChatbotCore`](main.py#L119) | 对话流程控制、指令解析、定时任务调度 |
| **读取层** | [`DataReader`](main.py#L13) | 统一数据查询接口、状态计算、检索协调 |
| **模块层** | [`SQLiteDB`](sqlite_db.py)、[`FAISSSearch`](faiss_search.py)、[`QwenAPI`](qwen_api.py) | 独立功能封装，低耦合高内聚 |

---

## 🚀 快速开始

### 环境要求

- **Python 版本**: 3.8+
- **内存要求**: 
  - 云端 API 模式：≥ 8GB（推荐 16GB）
  - 本地推理模式：≥ 16GB（推荐 32GB，详见 [LOCAL_INFERENCE.md](LOCAL_INFERENCE.md)）
- **操作系统**: Windows / Linux / macOS
- **磁盘空间**: 
  - 云端 API 模式：至少 1GB
  - 本地推理模式：至少 10GB（模型文件约 4.3GB）

### 安装步骤

#### 1. 创建虚拟环境

```bash
# Windows (PowerShell)
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

#### 2. 安装依赖

```
# 云端 API 模式（推荐）
pip install --upgrade pip
pip install -r requirements.txt

# 本地推理模式（实验性，需要额外安装）
pip install llama-cpp-python requests tqdm
# 详见 LOCAL_INFERENCE.md 中的详细安装指南
```

#### 3. 配置 API Key

获取阿里云百炼平台 API Key：https://dashscope.console.aliyun.com/

---

## 📖 使用说明

### 启动对话系统

#### 方式一：云端 API 模式（推荐）

```bash
python main.py
```

**首次运行提示：**
- 输入阿里云 DashScope API Key
- 系统将自动初始化数据库和向量索引
- 开始交互式对话

#### 方式二：本地推理模式（实验性）

```bash
# 1. 确保已下载模型文件到 models/ 目录
# 2. 运行本地模型启动器
python local_qwen_model.py

# 或使用集成版本（开发中）
python main_local.py
```

⚠️ **注意事项**：
- 本地推理功能处于适配阶段，性能可能不稳定
- 首次加载需要 30-60 秒
- 生成速度约 1.7-3.2 tokens/秒（取决于 CPU 性能）
- 详见 [LOCAL_INFERENCE.md](LOCAL_INFERENCE.md)

### 基本对话示例

```
请输入你的文本（输入'exit'退出）：今天心情不错

【基础 Prompt（未检索）】：
---
### 核心语法定义...
（完整 Prompt 结构见 prompt_config.py）
---

【AI 原始输出（含检索指令）】：
{
  "自然回复": "自然回复[太好了！听到你心情不错我也很开心～]",
  "心情": "心情[愉快]",
  "想法": "想法[希望这种好心情能持续下去]",
  ...
}

【结构化输出】：
回复文本：太好了！听到你心情不错我也很开心～
当前感受_心情：愉快
当前感受_想法：希望这种好心情能持续下去
精力值：85.0 秒
情绪值：90.0 秒
...

✅ 所有数据已写入数据库，定时任务已启动！
```

### 数据库可视化查看

```bash
python db_viewer.py
```

访问 http://localhost:5000 查看和导出数据库内容。

---

## 📁 项目结构

```
xinbanai5.0/
├── main.py                  # 主程序入口（完整版）
├── prompt_config.py         # 提示词模板配置
├── sqlite_db.py             # 数据库层（8 张表）
├── qwen_api.py              # 阿里云百炼 API 封装
├── faiss_search.py          # FAISS 向量检索
├── event_summary.py         # 事件摘要管理
├── db_viewer.py             # 数据库可视化查看器
├── cli_demo.py              # 命令行演示程序
├── local_qwen_model.py      # 本地推理模型（实验性）
│
├── requirements.txt         # Python 依赖清单
├── LICENSE                  # MIT 开源许可证
├── .gitignore               # Git 忽略文件配置
├── README.md                # 项目说明文档
├── QUICKSTART.md            # 快速开始指南
├── LOCAL_INFERENCE.md       # 本地推理适配指南
│
├── chatbot.db               # SQLite 数据库（运行时生成）
├── faiss_index.bin          # FAISS 向量索引（运行时生成）
├── text_list.npy            # 文本列表缓存（运行时生成）
└── logs/                    # 日志目录（运行时生成）
    └── context.log
```

---

## 🧩 核心模块说明

### 1. 主程序 ([`main.py`](main.py))

**核心类：**

- **`DataReader`**：数据读取层
  - 读取自我认知、他人认知、最近感受、情绪数值
  - 计算当前状态（清醒/打盹/小憩/午休/睡眠）
  - 执行 FAISS 语意检索（按需）

- **`ChatbotCore`**：核心业务逻辑
  - `_build_prompt()`：拼接 Prompt
  - `_parse_search_instruction()`：解析检索指令
  - `_parse_ai_output()`：解析结构化 JSON 输出
  - `_write_to_db()`：写入数据库
  - `_start_scheduled_task()`：启动定时任务

### 2. 提示词配置 ([`prompt_config.py`](prompt_config.py))

**关键组件：**

- **`PROMPT_TEMPLATE`**：结构化提示词模板
  - 包含 13 个功能字段（自我认知、他人认知、情绪数值等）
  - 使用 `or and()` 条件输出逻辑框

- **`QWEN_STRUCTURED_PROMPT_SUFFIX`**：JSON 格式化约束
  - 强制 AI 返回标准 JSON 格式
  - 增量更新原则（仅填写新增/变化内容）

### 3. 数据库层 ([`sqlite_db.py`](sqlite_db.py))

**8 大数据表：**

| 表名 | 用途 | 关键字段 |
|------|------|----------|
| `self_cognition` | 自我认知 | content, update_time |
| `other_cognition` | 他人认知 | content, update_time |
| `feelings` | 心情想法 | mood, thought, create_time |
| `emotion_values` | 情绪数值 | energy, emotion, focus, empathy |
| `long_term_memory` | 长期记忆 | user_input, ai_response, role |
| `event_summary` | 事件摘要 | summary, vector(BLOB) |
| `user_info` | 用户信息 | key, value (UPSERT) |
| `self_info` | 自我信息 | key, value (UPSERT) |

**特性：**
- ✅ 自动模式迁移（`_check_and_add_columns()`）
- ✅ 向量序列化存储（Pickle）
- ✅ 增量更新机制（UPSERT）

### 4. 大模型 API ([`qwen_api.py`](qwen_api.py))

**技术栈：**
- OpenAI Python SDK（兼容模式）
- 阿里云百炼平台：`https://dashscope.aliyuncs.com/compatible-mode/v1`
- 默认模型：`qwen3-max`

**方法：**
- `call(prompt)`：非流式调用，返回结构化 JSON
- `stream_call(prompt)`：流式调用（带思考过程，调试用）

### 5. 向量检索 ([`faiss_search.py`](faiss_search.py))

**性能指标：**
- ⚡ 秒级加载（读取本地索引文件）
- ⚡ 毫秒级检索（纯内存操作）
- ⚡ 384 维 IndexFlatL2 索引

**优化策略：**
- 本地哈希生成向量（无外部模型依赖）
- 增量保存（仅添加时写磁盘 <10ms）
- 优雅降级（失败时返回空列表）

---

## 📊 数据库设计

### ER 图概览

```
┌─────────────────────┐       ┌─────────────────────┐
│  self_cognition     │       │  other_cognition    │
├─────────────────────┤       ├─────────────────────┤
│ id (PK)             │       │ id (PK)             │
│ content             │       │ content             │
│ update_time         │       │ update_time         │
└─────────────────────┘       └─────────────────────┘
         ▲                             ▲
         │                             │
┌────────▼─────────────────────────────┴────────┐
│              ChatbotCore                       │
│  （协调所有数据表的读写操作）                  │
└────────┬──────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────┐
│  long_term_memory  │  feelings                 │
├────────────────────┼───────────────────────────┤
│ user_input         │ mood                      │
│ ai_response        │ thought                   │
│ role               │ create_time               │
│ create_time        │                           │
└────────────────────┴───────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────┐
│  event_summary       │  emotion_values         │
├──────────────────────┼─────────────────────────┤
│ summary              │ energy/emotion/focus... │
│ vector (BLOB)        │ create_time             │
│ create_time          │                         │
└──────────────────────┴─────────────────────────┘
```

---

## 🎯 特色功能详解

### 1. 语意检索双模机制

**工作流程：**
```
graph LR
    A[用户输入] --> B[AI 首次回复]
    B --> C{是否包含<br/>语意检索指令？}
    C -->|是 | D[FAISS 检索 Top5]
    C -->|否 | E[直接输出]
    D --> F[再次调用 AI]
    F --> G[最终回复]
```

**优势：**
- AI 自主决策是否需要检索（非强制）
- 减少不必要的检索开销

### 2. 定时任务系统

**触发条件：**
- AI 输出包含 `下一次活动时间数值 [时间=XXX 秒]`
- 范围限制：180 秒 ~ 28800 秒（8 小时）

**执行流程：**
```
启动守护线程 → 等待指定秒数 → 自动生成 Prompt → 
调用 AI → 解析输出 → 写入数据库 → 更新 FAISS
```

**应用场景：**
- ⏰ 主动发起对话（如"该休息了"）
- ⏰ 周期性提醒（喝水、运动）
- ⏰ 延时反馈（任务进度跟踪）

### 3. 情绪与状态系统

**四维情绪指标：**
- 精力值（Energy）：反映精神状态
- 情绪值（Emotion）：反映情感倾向
- 专注值（Focus）：反映注意力集中程度
- 共鸣值（Empathy）：反映共情能力

**五种状态：**

| 状态 | 触发条件 | 语气特征 |
|------|----------|----------|
| 清醒 | < 5 分钟 | 活泼主动 |
| 打盹 | 5-30 分钟 | 简洁慵懒 |
| 小憩 | 30-60 分钟 | 迷糊简短 |
| 午休 | 1-2 小时 | 被动回应 |
| 睡眠 | > 2 小时 | 极简/唤醒 |

### 4. 增量认知适应

**他人认知**：记录用户特点（如"喜欢编程"、"养了一只猫"）  
**自我认知**：记录 AI 自身特点（如"擅长数学"、"喜欢音乐"）  
**用户信息**：键值对存储（如 `name=张三，age=25`）  
**自我信息**：键值对存储（如 `version=V1，role=助手`）

**增量原则：**
- ✅ 仅记录本次对话**新发现**的信息
- ✅ 避免重复记录历史已存在的内容
- ✅ 支持后续对话持续完善认知模型

---

## 🔧 高级配置

### 修改模型

编辑 [`qwen_api.py`](qwen_api.py#L13)：

```python
self.model = "qwen3-max"  # 可替换为qwen-turbo/qwen-plus/qwen-max 等
```

**可用模型列表：**
- `qwen-turbo`：速度快，成本低
- `qwen-plus`：平衡性能和成本
- `qwen-max`：最强推理能力
- `qwen3-max`：最新版本（默认）

### 调整向量维度

编辑 [`faiss_search.py`](faiss_search.py#L5)：

```python
VECTOR_DIM = 384  # 根据使用的向量化模型调整
```

### 自定义定时任务范围

编辑 [`main.py`](main.py#L272-L274)：

```python
# 修改秒数范围限制
delay_seconds = max(最小值，min(delay_seconds, 最大值))
```

---

## 🛠️ 开发指南

### 添加新的输入入口

参考 Memory 中的"多入口分离架构"规范：

```python
# input_cli.py 示例
from main import ChatbotCore

def cli_input_loop():
    chatbot = ChatbotCore(api_key="your-api-key")
    while True:
        user_input = input("You: ")
        response = chatbot.generate_response(user_input)
        print(f"AI: {response}")

if __name__ == "__main__":
    cli_input_loop()
```

### 扩展数据库表

1. 在 [`sqlite_db.py`](sqlite_db.py) 的 `_create_all_tables()` 中添加新表
2. 编写对应的读写方法
3. 更新 [`_check_and_add_columns()`](sqlite_db.py#L77) 以支持向后兼容

### 自定义 Prompt 模板

编辑 [`prompt_config.py`](prompt_config.py) 的 `PROMPT_TEMPLATE`：

```python
PROMPT_TEMPLATE = """
### 核心语法定义...
（添加新的功能字段）
"""
```

---

## 🐛 常见问题

### 1. API 调用失败

**错误信息：** `❌ API调用失败：Connection timeout`

**解决方案：**
- 检查网络连接
- 验证 API Key 是否正确
- 确认阿里云百炼服务状态

### 2. FAISS 索引加载失败

**错误信息：** `⚠️ 加载 FAISS 索引失败，初始化空索引`

**解决方案：**
- 删除损坏的索引文件：`rm faiss_index.bin text_list.npy`
- 重启程序自动重建索引

### 3. 数据库模式不匹配

**错误信息：** `no such column: vector`

**解决方案：**
- 删除旧数据库：`rm chatbot.db`
- 重启程序自动创建新表
- 或运行迁移脚本添加缺失字段

### 4. 定时任务未执行

**可能原因：**
- 主程序提前退出（守护线程被终止）
- 秒数超出范围（<180 或 >28800）

**解决方案：**
- 确保主程序运行至定时任务完成
- 检查 AI 输出的"下一次活动时间数值"是否在有效范围

---

## 📚 文档导航

为了帮助您快速了解和使用本项目，我们准备了完整的文档体系：

### 🚀 新手入门

1. **[QUICKSTART.md](QUICKSTART.md)** - 5 分钟快速开始指南
   - 环境检查
   - 安装步骤
   - 首次运行
   - 常用操作

2. **[PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)** - 项目概览
   - 核心信息速查
   - 架构说明
   - 功能详解
   - 技术栈介绍

### 📖 深入使用

3. **[README.md](README.md)** - 完整项目说明
   - 系统架构
   - 详细功能
   - 数据库设计
   - 高级配置
   - 开发指南
   - 常见问题

4. **[LOCAL_INFERENCE.md](LOCAL_INFERENCE.md)** - 本地推理适配指南 ⚠️
   - **重要提示：本地推理处于实验性阶段**
   - 安装步骤（模型下载、依赖安装）
   - 使用方法
   - 性能基准测试
   - 常见问题
   - 未来计划

### 🛠️ 开发与贡献

5. **[CONTRIBUTING.md](CONTRIBUTING.md)** - 贡献者指南
   - 行为准则
   - 贡献方式
   - 开发环境设置
   - 代码规范
   - 提交流程
   - 代码审查

6. **[DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)** - 部署检查清单
   - 部署前检查
   - 安全检查
   - 性能优化
   - 质量保障
   - 开源准备

### 📋 版本信息

7. **[CHANGELOG.md](CHANGELOG.md)** - 更新日志
   - v5.0.0 新增功能
   - 历史版本记录
   - 发布计划
   - 版本说明

8. **[LICENSE](LICENSE)** - MIT 开源许可证

9. **[requirements.txt](requirements.txt)** - Python 依赖清单

10. **[.gitignore](.gitignore)** - Git 忽略配置

---

## 🎯 快速选择阅读路径

### 我是新手，想快速上手

→ 阅读 [QUICKSTART.md](QUICKSTART.md) → 运行 `python main.py` → 查看 [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)

### 我想深入了解系统架构

→ 阅读 [README.md](README.md) → 研究源代码 → 查看 [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)

### 我想尝试本地推理模型

→ 阅读 [LOCAL_INFERENCE.md](LOCAL_INFERENCE.md) ⚠️ **注意：实验性功能**

### 我想为项目做贡献

→ 阅读 [CONTRIBUTING.md](CONTRIBUTING.md) → Fork 项目 → 提交 PR

### 我要部署到生产环境

→ 阅读 [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) → 逐项检查 → 部署上线

## 📝 更新日志

### v1.0 (当前版本)
- ✅ 集成阿里云百炼 Qwen 大模型
- ✅ 实现 FAISS 向量检索 + SQLite 双模记忆
- ✅ 新增定时任务调度系统
- ✅ 支持用户信息和自我信息增量更新
- ✅ 优化情绪数值和状态系统
- ✅ 添加数据库可视化查看器

### 历史版本
- **v4.x**：基于 Qwen2.5-7B-4bit 本地模型（llama-cpp-python）
- **v3.x**：引入 FAISS 向量检索
- **v2.x**：增加长期记忆系统
- **v1.x**：基础对话功能

---

## 📄 许可证

本项目采用 MIT 许可证，详见 [LICENSE](LICENSE) 文件。

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📧 联系方式

- 项目地址：https://github.com/LiuStar656/adaptive-agent-architecture/
- 问题反馈：请通过 GitHub Issues 提交

---

## 🙏 致谢

- **阿里云百炼**：提供强大的 Qwen 大模型 API
- **FAISS**：Facebook AI Similarity Search 向量检索库
- **SQLite**：轻量级嵌入式数据库
- **OpenAI Python SDK**：兼容模式对接支持

---

<div align="center">

**如果这个项目对你有帮助，请给一个 ⭐ Star！**

Made with ❤️ by XinBanAI Team

</div>
