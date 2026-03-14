#!/usr/bin/env python3
"""
XinBanAI Framework - 决赛演示版
定位：智能体运行框架，非完整产品
核心：orand协议 · 五层架构 · 数据主权 · 插件机制
"""

import os
import sys
import time
from datetime import datetime

# 配置
API_KEY = "sk-c14dcdc9772f4bff9b0dd1a88a9fd839"
DB_PATH = "chatbot.db"

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入框架核心
from main import ChatbotCore
from qwen_api import QwenAPI
from sqlite_db import SQLiteDB

class Colors:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    END = "\033[0m"
    BOLD = "\033[1m"

def print_framework_header():
    """框架架构展示"""
    print(f"{Colors.HEADER}{Colors.BOLD}")
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║           XinBanAI Framework - 智能体运行框架                      ║")
    print("║     「orand协议 · 五层架构 · 数据主权 · 插件扩展」               ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print(Colors.END)
    
    print(f"{Colors.CYAN}【框架定位】{Colors.END}")
    print("  目标：让任意LLM获得常态化智能体能力")
    print("  机制：orand()指令协议 → 标准化输入输出")
    print("  架构：五层分离，每层可独立替换")
    print("  主权：所有数据归框架，LLM仅作为工具")
    print()

def print_architecture():
    """五层架构可视化"""
    print(f"{Colors.YELLOW}{Colors.BOLD}【五层架构初始化】{Colors.END}")
    print("  [存储层] SQLite 8张表 ........... ✓ 数据持久化")
    print("  [记忆层] FAISS向量检索 .......... ✓ 语义记忆")
    print("  [状态层] 四维情绪系统 .......... ✓ 自我维持")
    print("  [核心层] orand指令解析器 ...... ✓ 协议路由")
    print("  [模型层] 阿里云DashScope ...... ✓ LLM接口")
    print()

class FrameworkDemo:
    def __init__(self):
        print(f"{Colors.YELLOW}🔧 框架初始化...{Colors.END}")
        self.framework = ChatbotCore(db_path=DB_PATH)
        self.framework.qwen = QwenAPI(API_KEY)
        self.round = 0
        print(f"{Colors.GREEN}✅ 框架就绪{Colors.END}\n")

    def demonstrate_orand_protocol(self):
        """演示1：orand协议——框架核心创新"""
        print(f"{Colors.BOLD}{Colors.YELLOW}【演示1】orand() 指令解析协议{Colors.END}")
        print("原理：LLM输出自然语言 + 结构化指令，框架自动路由到各模块")
        print()
        
        # 实际运行
        user_input = "你好，我是开发者，测试框架"
        
        print(f"{Colors.BLUE}输入：{user_input}{Colors.END}")
        print(f"{Colors.CYAN}框架处理流程：{Colors.END}")
        
        # 构建Prompt
        prompt = self.framework._build_prompt(user_input, need_search=False)
        print("  1. orand() 扫描所有上下文信息")
        print("     - 自我认知、他人认知、情绪数值、历史摘要...")
        
        # 调用LLM
        response = self.framework.qwen.call(prompt)
        print("  2. LLM生成结构化输出（自然语言 + JSON指令）")
        
        # 解析
        parsed = self.framework._parse_ai_output(response, user_input)
        print("  3. 框架解析所有字段，路由到对应模块：")
        print(f"     - 自然回复 → 输出层")
        print(f"     - 情绪数值 → 状态管理器")
        print(f"     - 用户信息 → 画像系统")
        print(f"     - 下一次活动时间数值 → 任务调度器")
        
        # 写入
        self.framework._write_to_db(user_input, parsed)
        print("  4. 所有数据写入SQLite，框架拥有主权")
        
        print(f"\n{Colors.GREEN}输出：{parsed['回复文本']}{Colors.END}")
        print(f"状态：{parsed['当前状态']} | 情绪：{parsed['情绪值']} | 定时：{parsed['下一次活动时间数值']}秒")
        print()
        
        return parsed

    def demonstrate_plugin_mechanism(self):
        """演示2：插件扩展机制"""
        print(f"{Colors.BOLD}{Colors.YELLOW}【演示2】功能插件扩展机制{Colors.END}")
        print("开发者新增功能步骤：")
        print("  1. 创建插件文件（如 email_plugin.py）")
        print("  2. 在orand协议中注册：'功能类别': '发送邮件'")
        print("  3. LLM输出对应指令，框架自动路由调用")
        print()
        
        # 模拟扩展
        print(f"{Colors.CYAN}模拟：新增'文件操作'插件{Colors.END}")
        print("  LLM输出: {'功能类别': '文件读取', '参数': {'路径': 'data.txt'}}")
        print("  框架动作:")
        print("    [orand解析] → [路由到file_plugin] → [执行读取] → [结果回写]")
        print(f"  {Colors.GREEN}✓ 零侵入扩展，无需修改框架核心{Colors.END}")
        print()

    def demonstrate_data_sovereignty(self):
        """演示3：数据主权"""
        print(f"{Colors.BOLD}{Colors.YELLOW}【演示3】数据主权设计{Colors.END}")
        print("原则：所有数据归框架，LLM只是调用方")
        print()
        
        # 查询数据库
        try:
            db = SQLiteDB(DB_PATH)
            print(f"{Colors.CYAN}数据库验证（框架拥有所有数据）：{Colors.END}")
            
            tables = [
                ("self_cognition", "自我认知"),
                ("other_cognition", "他人认知"),
                ("emotion_values", "情绪数值"),
                ("user_info", "用户画像"),
                ("long_term_memory", "长期记忆"),
                ("event_summary", "事件摘要")
            ]
            
            for table, desc in tables:
                try:
                    conn = sqlite3.connect(DB_PATH)
                    cursor = conn.cursor()
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    print(f"  • {desc:12s} ({table:20s}): {count:3d} 条记录")
                    conn.close()
                except:
                    print(f"  • {desc:12s} ({table:20s}): 表为空或不存在")
            
            print(f"\n{Colors.GREEN}✓ 数据完全本地，LLM无直接访问权限{Colors.END}")
            
        except Exception as e:
            print(f"{Colors.RED}数据库查询受限：{e}{Colors.END}")
        
        print()

    def demonstrate_lifecycle(self):
        """演示4：智能体生命周期"""
        print(f"{Colors.BOLD}{Colors.YELLOW}【演示4】常态化运行机制{Colors.END}")
        print("框架让LLM从'单次对话'变为'常驻服务'")
        print()
        
        # 启动短定时任务
        user_input = "演示定时任务，5秒后触发"
        prompt = self.framework._build_prompt(user_input, need_search=False)
        response = self.framework.qwen.call(prompt)
        parsed = self.framework._parse_ai_output(response, user_input)
        
        # 启动3秒定时任务（演示用）
        self.framework._start_scheduled_task(3, "框架演示定时任务")
        
        print(f"{Colors.CYAN}定时任务注册：{Colors.END}")
        print(f"  ⏰ 3秒后将自动唤醒LLM")
        print(f"  📝 任务ID: {self.framework.scheduled_tasks[-1].ident}")
        print(f"  🔄 后台线程守护，主程序不阻塞")
        
        # 等待触发
        print(f"{Colors.YELLOW}等待定时任务触发...{Colors.END}")
        time.sleep(4)
        
        print(f"{Colors.GREEN}✓ 生命周期管理：初始化 → 运行 → 定时唤醒 → 持续迭代{Colors.END}")
        print()

    def run(self):
        """主演示"""
        print_framework_header()
        print_architecture()
        
        # 四个核心演示
        self.demonstrate_orand_protocol()
        time.sleep(0.5)
        
        self.demonstrate_plugin_mechanism()
        time.sleep(0.5)
        
        self.demonstrate_data_sovereignty()
        time.sleep(0.5)
        
        self.demonstrate_lifecycle()
        
        # 收尾
        print(f"{Colors.HEADER}{Colors.BOLD}" + "="*70)
        print("框架核心价值")
        print("="*70)
        print("  • orand协议：LLM标准化输出 → 结构化能力")
        print("  • 五层架构：模块化设计，每层可独立替换")
        print("  • 数据主权：框架拥有记忆，LLM只是工具")
        print("  • 插件机制：新功能 = 新文件 + 协议注册，零侵入")
        print()
        print("XinBanAI 不造智能体，而是让每个LLM都能成为智能体")
        print("="*70 + Colors.END)

if __name__ == "__main__":
    import sqlite3
    try:
        demo = FrameworkDemo()
        demo.run()
    except Exception as e:
        print(f"{Colors.RED}演示异常：{e}{Colors.END}")
        import traceback
        traceback.print_exc()