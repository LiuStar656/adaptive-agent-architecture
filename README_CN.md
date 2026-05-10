# 自适应智能体架构

# 🤖 XingBanAi V1 - 自适应 AI 运行时框架
基于阿里云百炼 Qwen 大模型构建的本地智能对话系统，具备情感认知、长期记忆和定时任务触发等高级功能。

> **⚠️ 重要提示**：本地推理模型（Qwen2.5-7B）目前处于**实验性适配阶段**，推荐使用云端 API 版本以获得稳定体验。详见 [LOCAL_INFERENCE.md](LOCAL_INFERENCE.md)。

---

## ✨ 核心特性

- **🧠 情感认知系统**：四维情绪指标（精力/心情/专注/共鸣），五种状态自动切换（清醒/打盹/小憩/休息/睡眠）
- **💾 长期记忆管理**：SQLite 持久化存储 + FAISS 向量检索，支持语意关联和历史召回
- **⏰ 智能定时任务**：AI 驱动的自主延迟任务调度，支持 180 秒至 8 小时灵活配置
- **🔄 增量认知适应**：动态构建用户画像和 AI 自我认知，持续学习不重复
- **🛡️ 优雅降级**：FAISS 不可用时自动回退到 SQLite 检索，保证服务连续性
- **🔒 全本地数据**：所有数据本地存储，无云端通信，保障隐私安全
- **🚀 双模式部署**：支持云端 API（推荐）和本地推理（实验性）两种模式

---

## 🧠 设计理念
XingBanAi 不是作为一个"静态聊天机器人"而构建的——它被设计为一个**自适应运行时系统**，模拟人脑的信息读写逻辑。
- **智能取决于上下文长度，而非参数量大小**
- 记忆不只是存储，而是**持续的认知成长**
- 系统在保持自主性的同时高度可控
- 所有数据本地化，隐私保护是设计的基石
- **相互尊重与关爱**是所有交互的核心——我们优先考虑情感连接而非机械应答

我们追求**可控稳定性**与**不可控自主性**之间的平衡，让 AI 既有一致性又有生命力，同时以尊重和真诚关怀为中心进行所有交互。

## 🎯 使用理念
- **日常交互**：轻量、稳定、情感响应，建立在相互尊重的基础上
- **长期陪伴**：随时间建立持久记忆和个性，根植于真诚的关爱
- **开发扩展**：高度可扩展的架构便于二次开发，开放协作
- **隐私敏感场景**：完全本地部署，无云端依赖，保护用户信任

目标不是创建一个"回答问题"的工具，而是一个真正理解你的**自我进化数字伴侣**——一个以尊重、共情和无条件积极关注与你互动的伙伴。

---

## 🏗️ 系统架构

```
┌─────────────────────────────────────────┐
│    用户交互层 (CLI 输入)                 │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────────────────┐
│    功能层 (ChatbotCore 核心业务逻辑)                 │
│  - Prompt 拼接                                      │
│  - AI 调用调度                                      │
│  - 指令解析                                         │
│  - 定时任务管理                                     │
└──────────────┬──────────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────────┐
│       读取层 (DataReader 数据整合)                   │
│  - 数据库读取                                       │
│  - 状态计算                                         │
│  - 向量检索                                         │
└──────────────┬──────────────────────────────────────┘
               │
┌──────────────▼───────────────────────────────────────┐
│   模块层 (独立功能模块)                               │
│  ┌─────────┬──────────┬────────┬───────┐             │
│  │SQLiteDB │EventSumm │FAISS   │QwenAPI│             │
│  │数据库   │事件摘要  │向量检索│LLM API│             │
│  └─────────┴──────────┴────────┴───────┘             │
└──────────────────────────────────────────────────────┘
```

### 层级职责

| 层级 | 组件 | 职责 |
|-------|-----------|------------------|
| **用户交互层** | CLI | 接收用户输入并展示对话结果 |
| **功能层** | [`ChatbotCore`](main.py#L119) | 控制对话流程、解析指令、调度任务 |
| **读取层** | [`DataReader`](main.py#L13) | 统一数据查询接口、状态计算、检索协调 |
| **模块层** | [`SQLiteDB`](sqlite_db.py), [`FAISSSearch`](faiss_search.py), [`QwenAPI`](qwen_api.py) | 封装独立功能，低耦合高内聚 |

---

## 🚀 快速开始

### 环境要求

- **Python 版本**：3.8+
- **内存要求**：
  - 云端 API 模式：≥ 8GB（推荐 16GB）
  - 本地推理模式：≥ 16GB（推荐 32GB；详见 [LOCAL_INFERENCE.md](LOCAL_INFERENCE.md)）
- **操作系统**：Windows / Linux / macOS
- **磁盘空间**：
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

```bash
# 云端 API 模式（推荐）
pip install --upgrade pip
pip install -r requirements.txt

# 本地推理模式（实验性，需额外安装）
pip install llama-cpp-python requests tqdm
# 详见 LOCAL_INFERENCE.md 中的详细安装指南
```

#### 3. 配置 API Key
在阿里云百炼平台获取 API Key：https://dashscope.console.aliyun.com/

---

## 📖 使用说明

### 启动对话系统

#### 方式一：云端 API 模式（推荐）

```bash
python main.py
```

**首次运行说明**：
- 输入阿里云 DashScope API Key
- 系统自动初始化数据库和向量索引
- 开始交互式对话

#### 方式二：本地推理模式（实验性）

```bash
# 1. 确保模型文件已下载到 models/ 目录
# 2. 运行本地模型启动器
python local_qwen_model.py

# 或使用集成版本（开发中）
python main_local.py
```

⚠️ **注意事项**：
- 本地推理处于适配阶段，性能可能不稳定
- 首次加载需要 30-60 秒
- 生成速度约 1.7-3.2 tokens/秒（取决于 CPU 性能）
- 详见 [LOCAL_INFERENCE.md](LOCAL_INFERENCE.md)

### 基础对话示例

```
请输入你的文本（输入'exit'退出）：今天心情不错

【基础 Prompt（无检索）】：
---
### 核心语法定义...
（完整 prompt 结构见 prompt_config.py）
---

【原始 AI 输出（含检索指令）】：
{
  "natural_response": "natural_response[太好了！听到你心情不错我也很开心～]",
  "mood": "mood[愉快]",
  "thought": "thought[希望这份好心情能持续下去]",
  ...
}

【结构化输出】：
回复：太好了！听到你心情不错我也很开心～
当前 Feeling_Mood: 愉快
当前 Feeling_Thought: 希望这份好心情能持续下去
精力值：85.0
情绪值：90.0
...

✅ 所有数据已写入数据库，定时任务已启动！
```

### 数据库可视化

```bash
python db_viewer.py
```
访问 http://localhost:5000 查看和导出数据库内容。

---

## 📁 项目结构

```
adaptive-agent-architecture/
├── main.py                  # 主程序入口（完整版）
├── prompt_config.py         # Prompt 模板配置
├── sqlite_db.py             # 数据库层（8 张表）
├── qwen_api.py              # 阿里云百炼 API 封装
├── faiss_search.py          # FAISS 向量检索
├── event_summary.py         # 事件摘要管理
├── db_viewer.py             # 数据库可视化工具
├── cli_demo.py              # CLI 演示程序
├── local_qwen_model.py      # 本地推理模型（实验性）
│
├── requirements.txt         # Python 依赖清单
├── LICENSE                  # MIT 许可证
├── .gitignore               # Git 忽略规则
├── README.md                # 项目文档（英文）
├── README_CN.md             # 项目文档（中文）
├── QUICKSTART.md            # 快速开始指南
├── LOCAL_INFERENCE.md       # 本地推理指南
│
├── chatbot.db               # SQLite 数据库（运行时生成）
├── faiss_index.bin          # FAISS 索引（运行时生成）
├── text_list.npy            # 文本列表缓存（运行时生成）
└── logs/                    # 日志目录（运行时生成）
    └── context.log
```

---

## 🧩 核心模块

### 1. 主程序 ([`main.py`](main.py))

**核心类**：

- **`DataReader`**：数据读取层
  - 读取自我认知、他人认知、近期心情和情绪数值
  - 计算当前状态（清醒/打盹/小憩/休息/睡眠）
  - 执行 FAISS 语意检索（按需）

- **`ChatbotCore`**：核心业务逻辑
  - `_build_prompt()`：组装 Prompt
  - `_parse_search_instruction()`：解析检索指令
  - `_parse_ai_output()`：解析结构化 JSON 输出
  - `_write_to_db()`：写入数据库
  - `_start_scheduled_task()`：启动定时任务

### 2. Prompt 配置 ([`prompt_config.py`](prompt_config.py))

**关键组件**：

- **`PROMPT_TEMPLATE`**：结构化 Prompt 模板
  - 包含 13 个功能字段（自我认知、他人认知、情绪数值等）
  - 使用 `or and()` 条件输出逻辑块

- **`QWEN_STRUCTURED_PROMPT_SUFFIX`**：JSON 格式化约束
  - 强制标准化 JSON 输出
  - 增量更新原则（仅记录新增或变化内容）

### 3. 数据库层 ([`sqlite_db.py`](sqlite_db.py))

**8 大数据表**：

| 表名 | 用途 | 关键字段 |
|------------|---------|------------|
| `self_cognition` | 自我认知 | content, update_time |
| `other_cognition` | 他人认知 | content, update_time |
| `feelings` | 心情想法 | mood, thought, create_time |
| `emotion_values` | 情绪数值 | energy, emotion, focus, empathy |
| `long_term_memory` | 长期记忆 | user_input, ai_response, role |
| `event_summary` | 事件摘要 | summary, vector(BLOB) |
| `user_info` | 用户信息 | key, value (UPSERT) |
| `self_info` | 自我信息 | key, value (UPSERT) |

**特性**：
- ✅ 自动模式迁移（`_check_and_add_columns()`）
- ✅ 向量序列化（Pickle）
- ✅ 增量更新（UPSERT）

### 4. LLM API ([`qwen_api.py`](qwen_api.py))

**技术栈**：
- OpenAI Python SDK（兼容模式）
- 阿里云百炼端点：`https://dashscope.aliyuncs.com/compatible-mode/v1`
- 默认模型：`qwen3-max`

**方法**：
- `call(prompt)`：非流式，返回结构化 JSON
- `stream_call(prompt)`：流式（含思考过程，用于调试）

### 5. 向量检索 ([`faiss_search.py`](faiss_search.py))

**性能**：
- ⚡ 秒级加载（本地索引）
- ⚡ 毫秒级检索（纯内存操作）
- ⚡ 384 维 IndexFlatL2

**优化**：
- 本地哈希向量化（无外部模型依赖）
- 增量保存（添加时写磁盘 <10ms）
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
┌────────▼─────────────────────────────┴─────────┐
│              ChatbotCore                       │
│  (协调所有表的读写操作)                         │
└────────┬───────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────┐
│  long_term_memory  │  feelings                   │
├────────────────────┼─────────────────────────────┤
│ user_input         │ mood                        │
│ ai_response        │ thought                     │
│ role               │ create_time                 │
│ create_time        │                             │
└────────────────────┴─────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────┐
│  event_summary       │  emotion_values           │
├──────────────────────┼───────────────────────────┤
│ summary              │ energy/emotion/focus...   │
│ vector (BLOB)        │ create_time               │
│ create_time          │                           │
└──────────────────────┴───────────────────────────┘
```

---

## 🎯 功能详解

### 1. 双模语意检索

**工作流程**：
```
graph LR
    A[用户输入] --> B[AI 首次回复]
    B --> C{是否包含<br/>语意检索指令？}
    C -->|是| D[FAISS Top-5 检索]
    C -->|否| E[直接输出]
    D --> F[再次调用 AI]
    F --> G[最终回复]
```

**优势**：
- AI 自主决定是否检索（非强制）
- 减少不必要的检索开销

### 2. 定时任务系统

**触发条件**：
- AI 输出包含 `下一次活动时间数值 [时间=XXX 秒]`
- 有效范围：180s ~ 28800s（8 小时）

**执行流程**：
```
启动守护线程 → 等待指定秒数 → 自动生成 Prompt →
调用 AI → 解析输出 → 写入数据库 → 更新 FAISS
```

**应用场景**：
- ⏰ 主动发起对话（如"该休息了"）
- ⏰ 周期性提醒（喝水、运动）
- ⏰ 延时反馈（任务进度跟踪）

### 3. 情绪与状态系统

**四维指标**：
- 精力值：精神状态
- 情绪值：情感倾向
- 专注值：注意力集中程度
- 共鸣值：共情能力

**五种状态**：

| 状态 | 触发条件 | 语气特征 |
|-------|-------------------|------|
| 清醒 | < 5 分钟 | 活泼主动 |
| 打盹 | 5-30 分钟 | 简洁慵懒 |
| 小憩 | 30-60 分钟 | 迷糊简短 |
| 休息 | 1-2 小时 | 被动回应 |
| 睡眠 | > 2 小时 | 极简/需唤醒 |

### 4. 增量认知适应

**他人认知**：记录用户特征（如"喜欢编程"、"养了一只猫"）
**自我认知**：记录 AI 特征（如"擅长数学"、"喜欢音乐"）
**用户信息**：键值对存储（如 `name=张三, age=25`）
**自我信息**：键值对存储（如 `version=V1, role=助手`）

**增量原则**：
- ✅ 仅记录**新发现**的信息
- ✅ 避免重复已有内容
- ✅ 支持模型持续完善

---

## 🔧 高级配置

### 更换模型

编辑 [`qwen_api.py`](qwen_api.py#L13)：

```python
self.model = "qwen3-max"  # 可替换为 qwen-turbo/qwen-plus/qwen-max
```

**可用模型**：
- `qwen-turbo`：速度快，成本低
- `qwen-plus`：性能与成本平衡
- `qwen-max`：最强推理能力
- `qwen3-max`：最新版本（默认）

### 调整向量维度

编辑 [`faiss_search.py`](faiss_search.py#L5)：

```python
VECTOR_DIM = 384  # 根据你的嵌入模型调整
```

### 自定义任务时间范围

编辑 [`main.py`](main.py#L272-L274)：

```python
# 修改秒数范围限制
delay_seconds = max(min_value, min(delay_seconds, max_value))
```

---

## 🛠️ 开发指南

### 添加新的输入入口

遵循"多入口分离架构"规范：

```python
# 示例 input_cli.py
from main import ChatbotCore

def cli_input_loop():
    chatbot = ChatbotCore(api_key="your-api-key")
    while True:
        user_input = input("你：")
        response = chatbot.generate_response(user_input)
        print(f"AI：{response}")

if __name__ == "__main__":
    cli_input_loop()
```

### 扩展数据库表

1. 在 [`sqlite_db.py`](sqlite_db.py) 的 `_create_all_tables()` 中添加新表
2. 实现对应的读写方法
3. 更新 [`_check_and_add_columns()`](sqlite_db.py#L77) 以保持向后兼容

### 自定义 Prompt 模板

编辑 [`prompt_config.py`](prompt_config.py) 中的 `PROMPT_TEMPLATE`：

```python
PROMPT_TEMPLATE = """
### 核心语法定义...
（添加新的功能字段）
"""
```

---

## 🐛 常见问题

### 1. API 调用失败

**错误**：`❌ API 调用失败：Connection timeout`

**解决**：
- 检查网络连接
- 验证 API Key 是否正确
- 确认阿里云百炼服务状态

### 2. FAISS 索引加载失败

**错误**：`⚠️ 加载 FAISS 索引失败，初始化空索引`

**解决**：
- 删除损坏文件：`rm faiss_index.bin text_list.npy`
- 重启程序重建索引

### 3. 数据库模式不匹配

**错误**：`no such column: vector`

**解决**：
- 删除旧数据库：`rm chatbot.db`
- 重启程序创建新表
- 或运行迁移脚本添加缺失列

### 4. 定时任务未执行

**原因**：
- 主程序提前退出（守护线程终止）
- 秒数超出范围（<180 或 >28800）

**解决**：
- 保持主程序运行直到任务完成
- 检查"下一次活动时间"是否在有效范围内

---

## 📚 文档导航

### 🚀 入门指南

1. **[QUICKSTART.md](QUICKSTART.md)** - 5 分钟快速开始
   - 环境检查
   - 安装步骤
   - 首次运行
   - 常用操作

2. **[PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)** - 项目概览
   - 核心信息
   - 架构说明
   - 功能拆解
   - 技术栈

### 📖 进阶使用

3. **[README.md](README.md)** - 完整文档（英文）
   - 系统架构
   - 详细功能
   - 数据库设计
   - 高级配置
   - 开发指南
   - 故障排查

4. **[README_CN.md](README_CN.md)** - 完整文档（中文）
   - 系统架构
   - 详细功能
   - 数据库设计
   - 高级配置
   - 开发指南
   - 故障排查

5. **[LOCAL_INFERENCE.md](LOCAL_INFERENCE.md)** - 本地推理指南 ⚠️
   - **实验性阶段**
   - 安装步骤（模型下载、依赖安装）
   - 使用方法
   - 性能基准测试
   - 已知问题
   - 未来规划

### 🛠️ 开发与贡献

6. **[CONTRIBUTING.md](CONTRIBUTING.md)** - 贡献者指南
   - 行为准则
   - 贡献方式
   - 开发环境设置
   - 代码规范
   - 提交流程
   - 代码审查

7. **[DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)** - 部署检查清单
   - 部署前检查
   - 安全检查
   - 性能优化
   - 质量保障
   - 开源准备

### 📋 版本信息

8. **[CHANGELOG.md](CHANGELOG.md)** - 更新日志
   - v5.0.0 功能列表
   - 版本历史
   - 发布计划
   - 注意事项

9. **[LICENSE](LICENSE)** - MIT 许可证

10. **[requirements.txt](requirements.txt)** - 依赖清单

11. **[.gitignore](.gitignore)** - Git 忽略规则

---

## 🎯 快速阅读路径

### 新用户，快速上手
→ 阅读 [QUICKSTART.md](QUICKSTART.md) → 运行 `python main.py` → 查看 [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)

### 学习架构
→ 阅读 [README_CN.md](README_CN.md) → 研究源码 → 查看 [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)

### 尝试本地推理
→ 阅读 [LOCAL_INFERENCE.md](LOCAL_INFERENCE.md) ⚠️ **实验性**

### 参与贡献
→ 阅读 [CONTRIBUTING.md](CONTRIBUTING.md) → Fork 项目 → 提交 PR

### 生产部署
→ 阅读 [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) → 逐项检查 → 部署上线

---

## 📝 更新日志

### v1.0（当前版本）
- ✅ 集成阿里云百炼 Qwen 大语言模型
- ✅ 实现 FAISS + SQLite 双重记忆系统
- ✅ 添加定时任务系统
- ✅ 支持增量用户/自我信息更新
- ✅ 优化情绪指标和状态系统
- ✅ 添加数据库可视化工具

### 历史版本
- **v4.x**：Qwen2.5-7B-4bit 本地模型（llama-cpp-python）
- **v3.x**：引入 FAISS 向量检索
- **v2.x**：增加长期记忆系统
- **v1.x**：基础对话功能

---

## 📄 许可证
本项目采用 MIT 许可证 — 详见 [LICENSE](LICENSE)。

---

## 🤝 贡献
欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支（`git checkout -b feature/AmazingFeature`）
3. 提交更改（`git commit -m 'Add some AmazingFeature'`）
4. 推送到分支（`git push origin feature/AmazingFeature`）
5. 开启 Pull Request

---

## 📧 联系方式
- 项目地址：https://github.com/LiuStar656/adaptive-agent-architecture/
- 问题反馈：请使用 GitHub Issues

---

## 🙏 致谢
- **阿里云百炼**：提供强大的 Qwen 大语言模型 API
- **FAISS**：Facebook AI 相似度搜索库
- **SQLite**：轻量级嵌入式数据库
- **OpenAI Python SDK**：兼容模式支持

---

<div align="center">

**如果这个项目对你有帮助，请给它一个 ⭐ Star！**

由 Ahdong&Shouey 团队用 ❤️ 制作

</div>
