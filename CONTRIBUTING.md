# 🤝 XinBanAI V1 贡献指南

感谢您对本项目的关注！我们欢迎各种形式的贡献，包括代码提交、问题反馈、文档改进等。

---

## 📋 目录

- [行为准则](#行为准则)
- [贡献方式](#贡献方式)
- [开发环境设置](#开发环境设置)
- [代码规范](#代码规范)
- [提交流程](#提交流程)
- [代码审查](#代码审查)

---

## 🌟 行为准则

请遵循以下原则：

1. **尊重他人**：友善交流，避免人身攻击
2. **开放包容**：欢迎不同背景的贡献者
3. **专业严谨**：保持代码质量和文档准确性
4. **协作共赢**：积极沟通，共同解决问题

---

## 🎯 贡献方式

### 1. 提交 Bug 报告

如果您发现程序中的错误，请在 GitHub Issues 中创建新的 Issue，并提供以下信息：

- **标题**：简明扼要地描述问题
- **环境信息**：操作系统、Python 版本、依赖版本
- **复现步骤**：详细描述如何重现该问题
- **错误日志**：`logs/context.log` 中的完整错误信息
- **预期行为**：说明您期望的结果

### 2. 功能建议

欢迎提出新功能建议！请说明：

- 功能描述和使用场景
- 为什么需要这个功能
- 可能的实现方案（可选）

### 3. 文档改进

您可以：

- 修正错别字或语法错误
- 补充缺失的说明
- 添加使用示例
- 翻译为其他语言

### 4. 代码贡献

#### 修复 Bug

1. 在 Issues 中找到相关 Bug
2. 分析问题原因
3. 编写修复代码
4. 添加测试用例（如适用）
5. 提交 Pull Request

#### 开发新功能

1. 先在 Issue 中讨论新功能的必要性
2. 获得认可后开始开发
3. 按照代码规范编写代码
4. 更新相关文档
5. 提交 Pull Request

---

## 🛠️ 开发环境设置

### 1. Fork 项目

在 GitHub 上点击"Fork"按钮，将项目复制到您的账号下。

### 2. 克隆到本地

```bash
git clone https://github.com/yourusername/xinbanai5.0.git
cd xinbanai5.0
```

### 3. 配置上游仓库

```bash
git remote add upstream https://github.com/original-owner/xinbanai5.0.git
git fetch upstream
```

### 4. 创建虚拟环境

```bash
# Windows
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

### 5. 安装开发依赖

```bash
pip install -r requirements.txt
pip install pytest black flake8  # 开发和测试工具
```

### 6. 创建特性分支

```bash
git checkout -b feature/your-feature-name
```

---

## 📝 代码规范

### Python 代码风格

遵循 PEP 8 规范：

```python
# ✅ 好的命名
user_name = "张三"
def get_user_info():
    pass

# ❌ 避免的命名
UserName = "张三"  # 应使用蛇形命名
def getUserInfo():  # 应使用蛇形命名
    pass
```

### 注释要求

``python
def calculate_emotion_score(values):
    """
    计算情绪分数（0-100）
    
    Args:
        values (dict): 包含四项指标数值的字典
        
    Returns:
        float: 计算后的情绪分数
        
    Example:
        >>> calculate_emotion_score({'energy': 80, 'emotion': 90})
        85.0
    """
    pass
```

### 错误处理

``python
# ✅ 推荐：明确的异常处理
try:
    result = db.query(sql)
except sqlite3.Error as e:
    logger.error(f"数据库查询失败：{e}")
    raise

# ❌ 避免：捕获所有异常
try:
    result = db.query(sql)
except:
    print("出错了")
```

### 导入顺序

```python
# 标准库
import os
import sys
from datetime import datetime

# 第三方库
import numpy as np
from openai import OpenAI

# 本地模块
from prompt_config import PROMPT_TEMPLATE
from sqlite_db import SQLiteDB
```

---

## 🚀 提交流程

### 1. 编写代码

确保代码：
- 功能正常
- 符合代码规范
- 添加了必要的注释
- 更新了相关文档

### 2. 运行测试

```bash
# 运行单元测试（如果有）
pytest

# 检查代码格式
black --check .

# 检查代码风格
flake8
```

### 3. 提交更改

```bash
# 添加文件
git add path/to/changed/file.py

# 提交代码（使用清晰的提交信息）
git commit -m "feat: 添加语意检索双模机制

- 实现 FAISS 向量检索
- 支持优雅降级到 SQLite 检索
- 添加相关单元测试"

# 推送到远程仓库
git push origin feature/your-feature-name
```

### 4. 创建 Pull Request

1. 访问您的 Fork 仓库
2. 点击"Compare & pull request"
3. 填写 PR 描述：
   - 修改目的
   - 主要变更
   - 测试结果
   - 关联的 Issue（如 `Fixes #123`）

4. 提交 PR

---

## 🔍 代码审查

### 审查标准

维护者将从以下方面审查您的代码：

- ✅ **功能性**：代码是否按预期工作
- ✅ **可读性**：代码是否清晰易懂
- ✅ **性能**：是否存在性能问题
- ✅ **安全性**：是否存在安全隐患
- ✅ **兼容性**：是否与现有代码兼容
- ✅ **测试覆盖**：是否包含足够的测试

### 常见审查意见

- "请添加更详细的注释"
- "建议使用更高效的算法"
- "需要补充单元测试"
- "请遵循 PEP 8 规范"
- "考虑边界情况"

### 回应审查

- 积极回应审查意见
- 及时修改代码
- 如有疑问，礼貌讨论
- 完成所有修改后，请求重新审查

---

## 📦 发布流程

### 版本号规范

遵循语义化版本（Semantic Versioning）：

- **MAJOR.MINOR.PATCH** (例如：5.0.1)
- MAJOR: 不兼容的 API 变更
- MINOR: 向后兼容的功能增加
- PATCH: 向后兼容的问题修复

### 发布清单

发布新版本前，请确认：

- [ ] 所有测试通过
- [ ] 文档已更新
- [ ] CHANGELOG.md 已更新
- [ ] 版本号已更新
- [ ] 依赖项已检查
- [ ] 性能测试通过

---

## 🎓 学习资源

### Python 编程

- [PEP 8 风格指南](https://peps.python.org/pep-0008/)
- [Python 官方文档](https://docs.python.org/zh-cn/3/)
- [流畅的 Python](https://book.douban.com/subject/27592247/)

### Git 使用

- [Git 官方文档](https://git-scm.com/book/zh/v2)
- [GitHub 流](https://docs.github.com/zh/get-started/quickstart/github-flow)

### 开源贡献

- [第一次贡献开源项目](https://opensource.guide/zh-hans/how-to-contribute/)
- [Pull Request 礼仪](https://github.blog/2015-01-21-how-to-write-the-perfect-pull-request/)

---

## 🏆 致谢贡献者

感谢所有为本项目做出贡献的开发者！

<!-- 这里会显示贡献者列表 -->
[![Contributors](https://contrib.rocks/image?repo=yourusername/xinbanai5.0)](https://github.com/yourusername/xinbanai5.0/graphs/contributors)

---

## 📧 联系方式

如有任何问题，请通过以下方式联系：

- **GitHub Issues**: 技术问题首选
- **Discussion**: 一般性问题讨论
- **Email**: （如有公开）

---

<div align="center">

**再次感谢您的贡献！**

Made with ❤️ by XinBanAI Team

</div>
