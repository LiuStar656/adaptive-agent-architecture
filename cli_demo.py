import os
import sys
import time
import pytz
from datetime import datetime

# ===================== 核心配置 =====================
ALIYUN_API_KEY = "sk-xxx"
DB_PATH = "chatbot.db"

# ===================== 导入核心模块 =====================
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from main import ChatbotCore
from qwen_api import QwenAPI

# ===================== 彩色输出 =====================
class Color:
    os.system("")
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    PURPLE = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[0m"
    BOLD = "\033[1m"

def clear_screen():
    os.system('cls')

def print_top_banner():
    """顶部常驻横幅（每次清屏后重绘）"""
    print(f"{Color.BOLD}{Color.CYAN}" + "="*80)
    print(f"{Color.BOLD}{Color.PURPLE}          🚀 AI智能对话系统 - 比赛演示版 (云API稳定模式)")
    print(f"{Color.BOLD}{Color.BLUE}          🎯 核心能力：人格动态注入 + 记忆读写 + 用户画像 + 定时任务 + 向量检索")
    print(f"{Color.BOLD}{Color.YELLOW}          📌 数据库：{DB_PATH} | 时区：Asia/Shanghai")
    print(f"{Color.BOLD}{Color.CYAN}" + "="*80 + Color.WHITE)

def print_loading():
    for _ in range(2):
        sys.stdout.write(f"\r{Color.YELLOW}🤖 AI内核正在处理...{'.'*_}{Color.WHITE}")
        sys.stdout.flush()
        time.sleep(0.2)
    sys.stdout.write("\r" + " " * 40 + "\r")

# ===================== DemoRunner 重构 =====================
class DemoRunner:
    def __init__(self):
        try:
            self.chatbot = ChatbotCore(db_path=DB_PATH)
            self.chatbot.qwen = QwenAPI(ALIYUN_API_KEY)
            self.chat_history = []
        except Exception as e:
            print(f"{Color.RED}❌ 内核初始化失败：{str(e)}{Color.WHITE}")
            sys.exit(1)

    def handle_user_input(self, user_input):
        if user_input.lower() == "exit":
            return "exit"
        if user_input.lower() == "history":
            self._show_history()
            return None
        if not user_input:
            return None

        try:
            print_loading()
            
            # ========== 复用 main 的核心流程（静默执行） ==========
            base_prompt = self.chatbot._build_prompt(user_input, need_search=False)
            ai_raw_output = self.chatbot.qwen.call(base_prompt)
            need_search, search_content = self.chatbot._parse_search_instruction(ai_raw_output)

            final_ai_output = ai_raw_output
            if need_search:
                search_prompt = self.chatbot._build_prompt(search_content or user_input, need_search=True)
                final_ai_output = self.chatbot.qwen.call(search_prompt)

            ai_parsed = self.chatbot._parse_ai_output(final_ai_output, user_input)
            self.chatbot._write_to_db(user_input, ai_parsed)
            
            if ai_parsed.get("事件摘要", "").strip():
                self.chatbot.faiss.add_text(ai_parsed["事件摘要"])
                
            self.chatbot._start_scheduled_task(
                delay_seconds=ai_parsed.get("下一次活动时间数值", 180),
                last_user_input=user_input
            )

            # 记录历史
            self.chat_history.append({
                "time": datetime.now(pytz.timezone("Asia/Shanghai")).strftime("%Y-%m-%d %H:%M:%S"),
                "user": user_input,
                "ai_reply": ai_parsed.get("回复文本", ""),
                "emotion": ai_parsed.get("情绪值", 0),
                "next_task": ai_parsed.get("下一次活动时间数值", 0)
            })

            return ai_parsed
        except Exception as e:
            print(f"{Color.RED}❌ 处理失败：{str(e)}{Color.WHITE}")
            return None

    def _show_history(self):
        clear_screen()
        print_top_banner()
        print(f"\n{Color.PURPLE}{Color.BOLD}📜 对话记忆（共{len(self.chat_history)}条）：{Color.WHITE}")
        if not self.chat_history:
            print(f"{Color.RED}暂无记录{Color.WHITE}")
        else:
            for i, item in enumerate(self.chat_history[-5:], 1):
                print(f"\n{i}. {Color.BLUE}{item['time']}{Color.WHITE}")
                print(f"   👤 {item['user']}")
                print(f"   🤖 {item['ai_reply'][:60]}...")
        input(f"\n{Color.GREEN}按回车返回主界面...{Color.WHITE}")

    def run(self):
        # 初始横幅
        clear_screen()
        print_top_banner()
        print(f"\n{Color.PURPLE}📢 操作说明：输入对话 | history 查看记忆 | exit 退出{Color.WHITE}")

        while True:
            user_input = input(f"\n{Color.BLUE}👤 用户 > {Color.WHITE}").strip()
            
            result = self.handle_user_input(user_input)
            
            if result == "exit":
                clear_screen()
                print_top_banner()
                print(f"\n{Color.YELLOW}🔄 等待后台任务完成...{Color.WHITE}")
                for task in self.chatbot.scheduled_tasks:
                    if task.is_alive():
                        task.join(timeout=5)
                print(f"\n{Color.GREEN}👋 演示结束！数据已持久化至 {DB_PATH}{Color.WHITE}")
                break
            elif result is None:
                continue
            else:
                # ====== 关键：清屏 + 顶部横幅 + 最新状态 ======
                clear_screen()
                print_top_banner()
                
                # 安全获取字段（防 KeyError）
                reply = result.get("回复文本", "（无回复）")
                thought = result.get("当前想法", "暂无想法")
                status = result.get("当前状态", "未知")
                energy = result.get("精力值", 0)
                emotion = result.get("情绪值", 0)
                focus = result.get("专注值", 0)
                resonance = result.get("共鸣值", 0)
                summary = result.get("事件摘要", "无摘要")
                next_time = result.get("下一次活动时间数值", 0)

                print(f"\n{Color.BLUE}👤 用户：{user_input}{Color.WHITE}\n")
                print(f"{Color.GREEN}{Color.BOLD}🤖 星语：{Color.WHITE}{reply}\n")
                
                print(f"{Color.PURPLE}{Color.BOLD}💭 当前内核状态：{Color.WHITE}")
                print(f"   • 情绪四维：精力={energy} | 情绪={emotion} | 专注={focus} | 共鸣={resonance}")
                print(f"   • 人格状态：{status}")
                print(f"   • 当前想法：{thought}")
                print(f"   • 事件摘要：{summary[:80]}{'...' if len(summary) > 80 else ''}")
                
                if next_time > 0:
                    print(f"\n{Color.YELLOW}⏳ 已安排定时任务：{next_time}秒后主动互动{Color.WHITE}")
                
                print(f"\n{Color.CYAN}💡 提示：输入 'history' 查看记忆 | 'exit' 退出{Color.WHITE}")

# ===================== 程序入口 =====================
if __name__ == "__main__":
    if ALIYUN_API_KEY == "你的阿里云DashScope API Key":
        print(f"{Color.RED}❌ 请先填写API Key！{Color.WHITE}")
        sys.exit(1)
    
    try:
        runner = DemoRunner()
        runner.run()
    except KeyboardInterrupt:
        clear_screen()
        print_top_banner()
        print(f"\n{Color.GREEN}👋 演示被中断，感谢观看！{Color.WHITE}")
    except Exception as e:
        clear_screen()
        print_top_banner()
        print(f"\n{Color.RED}❌ 异常：{str(e)}{Color.WHITE}")