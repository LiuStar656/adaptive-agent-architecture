# 🤖 XinBanAI V1 - Adaptive AI Runtime Framework
A local intelligent dialogue system built on the Alibaba Cloud Bailian Qwen large model, featuring advanced capabilities such as emotional cognition, long-term memory, and scheduled task triggering.

> **⚠️ Important Notice**: The local inference model (Qwen2.5-7B) is currently in an **experimental adaptation phase**. The cloud API version is recommended for a stable experience. See [LOCAL_INFERENCE.md](LOCAL_INFERENCE.md) for details.

---

## ✨ Core Features

- **🧠 Emotional Cognition System**: Four-dimensional emotional metrics (energy / mood / focus / empathy), with automatic switching between five states (awake / drowsy / napping / resting / asleep)
- **💾 Long-Term Memory Management**: SQLite persistent storage + FAISS vector search, supporting semantic association and historical recall
- **⏰ Intelligent Scheduled Tasks**: AI-driven autonomous delayed task scheduling, configurable from 180 seconds to 8 hours
- **🔄 Incremental Cognitive Adaptation**: Dynamic construction of user profiles and AI self-cognition, continuous learning without repetition
- **🛡️ Graceful Degradation**: Automatic fallback to SQLite search when FAISS is unavailable, ensuring service continuity
- **🔒 Fully Local Data**: All data stored locally, no cloud communication, ensuring privacy and security
- **🚀 Dual-Mode Deployment**: Supports cloud API (recommended) and local inference (experimental) modes

---

## 🧠 Design Philosophy
XinBanAI is not built as a "static chatbot"—it is designed as an **adaptive runtime system** that mimics the information reading and writing logic of the human brain.
- **Intelligence depends on context length, not parameter size**
- Memory is not just storage, but **continuous cognitive growth**
- The system maintains autonomy while remaining highly controllable
- All data stays local, with privacy as a foundational design principle
- **Mutual respect and love** are the core of all interactions—we prioritize emotional connection over mechanical response

We pursue a balance between **controllable stability** and **uncontrollable autonomy**, making the AI feel both consistent and alive, while centering all interactions on respect and genuine care.

## 🎯 Usage Philosophy
- **For daily interaction**: Lightweight, stable, and emotionally responsive, built on mutual respect
- **For long-term companionship**: Builds persistent memory and personality over time, rooted in genuine care and love
- **For development**: Highly extensible architecture for secondary development, with openness and collaboration
- **For privacy-sensitive scenarios**: Fully local deployment with no cloud dependency, protecting user trust

The goal is not to create a tool that "answers questions," but a **self-evolving digital companion** that truly understands you—one that interacts with you with respect, empathy, and unconditional positive regard.

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────┐
│         User Interaction Layer (CLI Input)        │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│      Function Layer (ChatbotCore Core Business Logic) │
│  - Prompt Construction                          │
│  - AI Invocation Scheduling                     │
│  - Command Parsing                              │
│  - Scheduled Task Management                   │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│       Reading Layer (DataReader Data Integration)   │
│  - Database Reading                          │
│  - State Calculation                         │
│  - Vector Search                             │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│   Module Layer (Independent Functional Modules)      │
│  ┌─────────┬──────────┬────────┬──────┐  │
│  │SQLiteDB │EventSumm │FAISS   │QwenAPI│  │
│  │Database │Event Summ│Vector  │LLM API│  │
│  └─────────┴──────────┴────────┴──────┘  │
└─────────────────────────────────────────┘
```

### Layer Responsibilities

| Layer | Component | Responsibilities |
|-------|-----------|------------------|
| **User Interaction Layer** | CLI | Receives user input and displays dialogue results |
| **Function Layer** | [`ChatbotCore`](main.py#L119) | Controls dialogue flow, parses commands, and schedules tasks |
| **Reading Layer** | [`DataReader`](main.py#L13) | Unified data query interface, state calculation, and search coordination |
| **Module Layer** | [`SQLiteDB`](sqlite_db.py), [`FAISSSearch`](faiss_search.py), [`QwenAPI`](qwen_api.py) | Encapsulates independent functions with low coupling and high cohesion |

---

## 🚀 Quick Start

### Requirements

- **Python Version**: 3.8+
- **Memory Requirements**:
  - Cloud API Mode: ≥ 8GB (16GB recommended)
  - Local Inference Mode: ≥ 16GB (32GB recommended; see [LOCAL_INFERENCE.md](LOCAL_INFERENCE.md))
- **Operating System**: Windows / Linux / macOS
- **Disk Space**:
  - Cloud API Mode: At least 1GB
  - Local Inference Mode: At least 10GB (model file ~4.3GB)

### Installation

#### 1. Create Virtual Environment

```bash
# Windows (PowerShell)
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

#### 2. Install Dependencies

```bash
# Cloud API Mode (Recommended)
pip install --upgrade pip
pip install -r requirements.txt

# Local Inference Mode (Experimental, extra installation required)
pip install llama-cpp-python requests tqdm
# See detailed installation guide in LOCAL_INFERENCE.md
```

#### 3. Configure API Key
Get your Alibaba Cloud Bailian API Key at: https://dashscope.console.aliyun.com/

---

## 📖 Usage

### Launch the Dialogue System

#### Method 1: Cloud API Mode (Recommended)

```bash
python main.py
```

**First Run Notes**:
- Enter your Alibaba Cloud DashScope API Key
- The system automatically initializes the database and vector index
- Start interactive conversation

#### Method 2: Local Inference Mode (Experimental)

```bash
# 1. Ensure the model file is downloaded to the models/ directory
# 2. Run the local model launcher
python local_qwen_model.py

# Or use integrated version (under development)
python main_local.py
```

⚠️ **Notes**:
- Local inference is in the adaptation phase; performance may be unstable
- First load takes 30–60 seconds
- Generation speed ~1.7–3.2 tokens/sec (depending on CPU performance)
- See [LOCAL_INFERENCE.md](LOCAL_INFERENCE.md)

### Basic Dialogue Example

```
Please enter your text (type 'exit' to quit): I'm in a good mood today

【Base Prompt (No Retrieval)】:
---
### Core Syntax Definition...
(Full prompt structure in prompt_config.py)
---

【Raw AI Output (With Retrieval Instructions)】:
{
  "natural_response": "natural_response[Great! I'm happy to hear you're in a good mood～]",
  "mood": "mood[pleasant]",
  "thought": "thought[Hope this good mood lasts]",
  ...
}

【Structured Output】:
Response: Great! I'm happy to hear you're in a good mood～
Current Feeling_Mood: pleasant
Current Feeling_Thought: Hope this good mood lasts
Energy: 85.0
Mood: 90.0
...

✅ All data written to database, scheduled task started!
```

### Database Visualization

```bash
python db_viewer.py
```
Visit http://localhost:5000 to view and export database contents.

---

## 📁 Project Structure

```
xinbanai5.0/
├── main.py                  # Main entry (full version)
├── prompt_config.py         # Prompt template configuration
├── sqlite_db.py             # Database layer (8 tables)
├── qwen_api.py              # Alibaba Cloud Bailian API wrapper
├── faiss_search.py          # FAISS vector search
├── event_summary.py         # Event summary management
├── db_viewer.py             # Database visualizer
├── cli_demo.py              # CLI demo
├── local_qwen_model.py      # Local inference model (experimental)
│
├── requirements.txt         # Python dependencies
├── LICENSE                  # MIT License
├── .gitignore               # Git ignore rules
├── README.md                # Project documentation
├── QUICKSTART.md            # Quick start guide
├── LOCAL_INFERENCE.md       # Local inference guide
│
├── chatbot.db               # SQLite database (generated at runtime)
├── faiss_index.bin          # FAISS index (generated at runtime)
├── text_list.npy            # Text list cache (generated at runtime)
└── logs/                    # Log directory (generated at runtime)
    └── context.log
```

---

## 🧩 Core Modules

### 1. Main Program ([`main.py`](main.py))

**Core Classes**:

- **`DataReader`**: Data reading layer
  - Reads self-cognition, other-cognition, recent feelings, and emotion values
  - Computes current state (awake / drowsy / napping / resting / asleep)
  - Performs FAISS semantic search (on demand)

- **`ChatbotCore`**: Core business logic
  - `_build_prompt()`: Assembles prompts
  - `_parse_search_instruction()`: Parses search instructions
  - `_parse_ai_output()`: Parses structured JSON output
  - `_write_to_db()`: Writes to database
  - `_start_scheduled_task()`: Starts scheduled tasks

### 2. Prompt Configuration ([`prompt_config.py`](prompt_config.py))

**Key Components**:

- **`PROMPT_TEMPLATE`**: Structured prompt template
  - Contains 13 functional fields (self-cognition, other-cognition, emotion values, etc.)
  - Uses `or and()` conditional output logic blocks

- **`QWEN_STRUCTURED_PROMPT_SUFFIX`**: JSON formatting constraint
  - Forces standardized JSON output
  - Incremental update principle (only new/changed content)

### 3. Database Layer ([`sqlite_db.py`](sqlite_db.py))

**8 Major Tables**:

| Table Name | Purpose | Key Fields |
|------------|---------|------------|
| `self_cognition` | Self-cognition | content, update_time |
| `other_cognition` | Other-cognition | content, update_time |
| `feelings` | Mood & thoughts | mood, thought, create_time |
| `emotion_values` | Emotional metrics | energy, emotion, focus, empathy |
| `long_term_memory` | Long-term memory | user_input, ai_response, role |
| `event_summary` | Event summaries | summary, vector(BLOB) |
| `user_info` | User info | key, value (UPSERT) |
| `self_info` | Self info | key, value (UPSERT) |

**Features**:
- ✅ Automatic schema migration (`_check_and_add_columns()`)
- ✅ Vector serialization (Pickle)
- ✅ Incremental updates (UPSERT)

### 4. LLM API ([`qwen_api.py`](qwen_api.py))

**Tech Stack**:
- OpenAI Python SDK (compatible mode)
- Alibaba Cloud Bailian endpoint: `https://dashscope.aliyuncs.com/compatible-mode/v1`
- Default model: `qwen3-max`

**Methods**:
- `call(prompt)`: Non-streaming, returns structured JSON
- `stream_call(prompt)`: Streaming (with thinking process, for debugging)

### 5. Vector Search ([`faiss_search.py`](faiss_search.py))

**Performance**:
- ⚡ Sub-second loading (local index)
- ⚡ Millisecond search (in-memory)
- ⚡ 384-dimensional IndexFlatL2

**Optimizations**:
- Local hash vectorization (no external model dependencies)
- Incremental saving (disk write <10ms on add)
- Graceful degradation (empty list on failure)

---

## 📊 Database Design

### ER Diagram Overview

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
│  (Coordinates read/write across all tables)    │
└────────┬──────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────┐
│  long_term_memory  │  feelings                   │
├────────────────────┼─────────────────────────────┤
│ user_input         │ mood                        │
│ ai_response        │ thought                     │
│ role               │ create_time                 │
│ create_time        │                             │
└────────────────────┴─────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────┐
│  event_summary       │  emotion_values           │
├──────────────────────┼───────────────────────────┤
│ summary              │ energy/emotion/focus...   │
│ vector (BLOB)        │ create_time               │
│ create_time          │                           │
└──────────────────────┴───────────────────────────┘
```

---

## 🎯 Feature Details

### 1. Dual-Mode Semantic Search

**Workflow**:
```
graph LR
    A[User Input] --> B[Initial AI Response]
    B --> C{Contains<br/>semantic search instruction?}
    C -->|Yes| D[FAISS Top-5 Search]
    C -->|No| E[Direct Output]
    D --> F[Second AI Call]
    F --> G[Final Response]
```

**Advantages**:
- AI autonomously decides whether to search (not forced)
- Reduces unnecessary search overhead

### 2. Scheduled Task System

**Trigger Condition**:
- AI output includes `next_activity_time [time=XXX seconds]`
- Valid range: 180s ~ 28800s (8 hours)

**Execution Flow**:
```
Start daemon thread → Wait specified seconds → Auto-generate Prompt →
Call AI → Parse output → Write to DB → Update FAISS
```

**Use Cases**:
- ⏰ Proactive dialogue (e.g., "Time to rest")
- ⏰ Periodic reminders (drink water, exercise)
- ⏰ Delayed feedback (task progress tracking)

### 3. Emotion & State System

**Four-Dimensional Metrics**:
- Energy: Mental state
- Mood: Emotional tendency
- Focus: Attention level
- Empathy: Compassion capability

**Five States**:

| State | Trigger Condition | Tone |
|-------|-------------------|------|
| Awake | < 5 minutes | Active & lively |
| Drowsy | 5–30 minutes | Brief & lazy |
| Napping | 30–60 minutes | Sleepy & concise |
| Resting | 1–2 hours | Passive response |
| Asleep | > 2 hours | Minimal / wake-only |

### 4. Incremental Cognitive Adaptation

**Other-Cognition**: Records user traits (e.g., "likes coding", "has a cat")
**Self-Cognition**: Records AI traits (e.g., "good at math", "likes music")
**User Info**: Key-value storage (e.g., `name=Zhang San, age=25`)
**Self Info**: Key-value storage (e.g., `version=V1, role=Assistant`)

**Incremental Principles**:
- ✅ Only records **newly discovered** information
- ✅ Avoids duplicate existing content
- ✅ Supports continuous model refinement

---

## 🔧 Advanced Configuration

### Change Model

Edit [`qwen_api.py`](qwen_api.py#L13):

```python
self.model = "qwen3-max"  # Replace with qwen-turbo/qwen-plus/qwen-max
```

**Available Models**:
- `qwen-turbo`: Fast, low cost
- `qwen-plus`: Balanced performance & cost
- `qwen-max`: Strongest reasoning
- `qwen3-max`: Latest (default)

### Adjust Vector Dimension

Edit [`faiss_search.py`](faiss_search.py#L5):

```python
VECTOR_DIM = 384  # Adjust to your embedding model
```

### Customize Task Time Range

Edit [`main.py`](main.py#L272-L274):

```python
# Modify second range limits
delay_seconds = max(min_value, min(delay_seconds, max_value))
```

---

## 🛠️ Development Guide

### Add New Input Entry

Follow the "multi-entry separation architecture" spec:

```python
# Example input_cli.py
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

### Extend Database Tables

1. Add new tables in `_create_all_tables()` in [`sqlite_db.py`](sqlite_db.py)
2. Implement corresponding read/write methods
3. Update [`_check_and_add_columns()`](sqlite_db.py#L77) for backward compatibility

### Customize Prompt Template

Edit `PROMPT_TEMPLATE` in [`prompt_config.py`](prompt_config.py):

```python
PROMPT_TEMPLATE = """
### Core Syntax Definition...
(Add new functional fields)
"""
```

---

## 🐛 Troubleshooting

### 1. API Call Failure

**Error**: `❌ API call failed: Connection timeout`

**Fix**:
- Check network
- Verify API Key
- Confirm Alibaba Cloud Bailian service status

### 2. FAISS Index Load Failure

**Error**: `⚠️ Failed to load FAISS index, initializing empty index`

**Fix**:
- Delete corrupted files: `rm faiss_index.bin text_list.npy`
- Restart to rebuild index

### 3. Database Schema Mismatch

**Error**: `no such column: vector`

**Fix**:
- Delete old DB: `rm chatbot.db`
- Restart to create new tables
- Or run migration script to add missing columns

### 4. Scheduled Task Not Executed

**Causes**:
- Main program exited early (daemon terminated)
- Seconds out of range (<180 or >28800)

**Fix**:
- Keep main program running until task completes
- Check that "next activity time" is within valid range

---

## 📚 Documentation Navigation

### 🚀 Getting Started

1. **[QUICKSTART.md](QUICKSTART.md)** - 5-Minute Quick Start
   - Environment check
   - Installation
   - First run
   - Common operations

2. **[PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)** - Project Overview
   - Core info
   - Architecture
   - Feature breakdown
   - Tech stack

### 📖 Advanced Usage

3. **[README.md](README.md)** - Full Documentation
   - Architecture
   - Detailed features
   - Database design
   - Advanced config
   - Development
   - Troubleshooting

4. **[LOCAL_INFERENCE.md](LOCAL_INFERENCE.md)** - Local Inference Guide ⚠️
   - **Experimental phase**
   - Installation (model download, dependencies)
   - Usage
   - Performance benchmarks
   - Issues
   - Roadmap

### 🛠️ Development & Contribution

5. **[CONTRIBUTING.md](CONTRIBUTING.md)** - Contributor Guide
   - Code of conduct
   - Contribution methods
   - Dev setup
   - Style guide
   - Commit flow
   - Code review

6. **[DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)** - Deployment Checklist
   - Pre-deployment checks
   - Security
   - Performance
   - Quality assurance
   - Open-source prep

### 📋 Version Info

7. **[CHANGELOG.md](CHANGELOG.md)** - Changelog
   - v5.0.0 features
   - Version history
   - Release plan
   - Notes

8. **[LICENSE](LICENSE)** - MIT License

9. **[requirements.txt](requirements.txt)** - Dependencies

10. **[.gitignore](.gitignore)** - Git ignore rules

---

## 🎯 Quick Reading Paths

### New User, Quick Start
→ Read [QUICKSTART.md](QUICKSTART.md) → Run `python main.py` → View [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)

### Learn Architecture
→ Read [README.md](README.md) → Study source → View [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)

### Try Local Inference
→ Read [LOCAL_INFERENCE.md](LOCAL_INFERENCE.md) ⚠️ **Experimental**

### Contribute
→ Read [CONTRIBUTING.md](CONTRIBUTING.md) → Fork → Submit PR

### Production Deploy
→ Read [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) → Verify → Deploy

---

## 📝 Changelog

### v1.0 (Current)
- ✅ Integrated Alibaba Cloud Bailian Qwen LLM
- ✅ Implemented FAISS + SQLite dual memory
- ✅ Added scheduled task system
- ✅ Supported incremental user/self info updates
- ✅ Optimized emotion metrics and state system
- ✅ Added database visualizer

### Previous Versions
- **v4.x**: Qwen2.5-7B-4bit local model (llama-cpp-python)
- **v3.x**: FAISS vector search introduced
- **v2.x**: Long-term memory system added
- **v1.x**: Basic dialogue

---

## 📄 License
This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.

---

## 🤝 Contributing
Issues and Pull Requests are welcome!

1. Fork this repo
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

## 📧 Contact
- Project: https://github.com/LiuStar656/adaptive-agent-architecture/
- Issues: Please use GitHub Issues

---

## 🙏 Acknowledgments
- **Alibaba Cloud Bailian**: Powerful Qwen LLM API
- **FAISS**: Facebook AI Similarity Search library
- **SQLite**: Lightweight embedded database
- **OpenAI Python SDK**: Compatible mode support

---

<div align="center">

**If this project helps you, please give it a ⭐ Star!**

Made with ❤️ by the AdongAndSouYi Team

</div>
```
### 总结
- 保留了原有所有技术内容，仅新增理念板块，不影响技术文档的完整性；
- 「相互尊重与爱」的核心理念自然融入设计/使用哲学，而非生硬堆砌；
- 位置醒目，符合开源项目README的阅读习惯，能让用户快速感知项目的核心价值观。
