from datetime import datetime, timedelta
import pytz
import re
import threading  # 新增：定时任务线程
import time       # 新增：时间相关工具
# 导入各独立模块
from prompt_config import PROMPT_TEMPLATE, get_fallback_response  # 提示词层
from sqlite_db import SQLiteDB             # 数据库层（读取/写入）
from event_summary import EventSummary     # 事件摘要拼接
from qwen_api import QwenAPI               # 大模型调用
from faiss_search import FAISSSearch        # 秒加载向量检索
import os
import sys
import logging
import os

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)


logging.basicConfig(
    level=logging.DEBUG,  # 可设为 INFO/WARNING 控制输出量
    format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "context.log"), encoding="utf-8"),
        logging.StreamHandler()  # 同时输出到控制台
    ]
)
logging.getLogger("openai._base_client").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)

# 获取 logger
logger = logging.getLogger("ChatbotContext")

# ====================== 读取层（整合所有读取功能） ======================
class DataReader:
    def __init__(self, db_path="chatbot.db"):
        self.db = SQLiteDB(db_path)
        self.event_summary = EventSummary(db_path)
        self.faiss_search = FAISSSearch()  # 秒加载向量
        self.timezone = pytz.timezone("Asia/Shanghai")

    def read_all_data(self, user_input, need_search=False):
        """读取所有需要的信息（供Prompt拼接），仅当need_search=True时执行检索"""
        try:
            # 1. 数据库读取
            self_cognition = self.db.read_self_cognition()
            other_cognition = self.db.read_other_cognition()
            recent_feelings = self.db.read_recent_feelings()
            energy, emotion, focus, empathy = self.db.read_recent_emotion_values()
            last_input_time = self.db.read_last_input_time()
            user_info = self.db.read_user_info()  # 读取用户信息
            self_info = self.db.read_self_info()  # 读取自我信息
            
            # 2. 系统信息
            current_dt = datetime.now(self.timezone)
            current_date = current_dt.strftime("%Y-%m-%d")
            current_time = current_dt.strftime("%H:%M:%S")
            last_input_str = last_input_time if last_input_time else ""
            
            # 3. 当前状态计算
            current_state = self._calculate_state(last_input_time)
            
            # 4. 最近情绪描述
            recent_emotion_desc = f"精力值{energy}，情绪值{emotion}，整体状态{current_state}"
            
            # 5. 事件摘要（历史摘要）
            history_summary = self.event_summary.get_history_summary(limit=3)
            
            # 6. FAISS语意检索（仅当AI要求检索时执行）
            faiss_str = ""
            if need_search:
                faiss_top5 = self.faiss_search.search(user_input, top_k=5)
                faiss_str = "; ".join(faiss_top5) if faiss_top5 else ""

            return {
                "self_cognition": self_cognition,
                "other_cognition": other_cognition,
                "recent_feelings": recent_feelings,
                "user_input": user_input,
                "current_date": current_date,
                "current_time": current_time,
                "current_state": current_state,
                "recent_emotion_desc": recent_emotion_desc,
                "energy_val": energy,
                "emotion_val": emotion,
                "focus_val": focus,
                "empathy_val": empathy,
                "last_input_time": last_input_str,
                "history_summary": history_summary,
                "faiss_top5": faiss_str,
                "user_info": user_info,
                "self_info": self_info
            }
        except Exception as e:
            print(f"⚠️ 数据读取警告：{e}")
            # 返回兜底数据
            return {
                "self_cognition": "",
                "other_cognition": "",
                "recent_feelings": "",
                "user_input": user_input,
                "current_date": datetime.now(self.timezone).strftime("%Y-%m-%d"),
                "current_time": datetime.now(self.timezone).strftime("%H:%M:%S"),
                "current_state": "清醒",
                "recent_emotion_desc": "",
                "energy_val": 0.0,
                "emotion_val": 0.0,
                "focus_val": 0.0,
                "empathy_val": 0.0,
                "last_input_time": "",
                "history_summary": "",
                "faiss_top5": "",
                "user_info": "",
                "self_info": ""
            }

    def _calculate_state(self, last_input_time):
        """根据活动间隔计算状态：清醒/打盹/小憩/午休/睡眠"""
        if not last_input_time:
            return "清醒"
        try:
            last_time = datetime.strptime(last_input_time, "%Y-%m-%d %H:%M:%S")
            current_time = datetime.now(self.timezone).replace(tzinfo=None)
            interval = (current_time - last_time).total_seconds()
            # 状态规则
            if interval < 300:      # <5分钟
                return "清醒"
            elif 300 <= interval < 1800:  # 5-30分钟
                return "打盹"
            elif 1800 <= interval < 3600: # 30-60分钟
                return "小憩"
            elif 3600 <= interval < 7200: # 1-2小时
                return "午休"
            else:                   # >2小时
                return "睡眠"
        except Exception as e:
            print(f"⚠️ 状态计算异常：{e}")
            return "清醒"

# ====================== 功能层（核心业务逻辑 + 定时任务） ======================
class ChatbotCore:
    def __init__(self, db_path="chatbot.db"):
        self.reader = DataReader(db_path)  # 读取层
        self.qwen = None       # 大模型调用
        self.db = SQLiteDB(db_path)        # 数据库写入
        self.faiss = FAISSSearch()         # 秒加载向量
        self.scheduled_tasks = []          # 新增：存储定时任务线程，便于管理

    def _parse_search_instruction(self, ai_raw_output):
        """
        解析AI输出，判断是否包含「语意检索」指令
        现在直接读取 '语意检索' 字段的值，非空即触发
        """
        try:
            # 直接获取字段值
            retrieval_content = ai_raw_output.get("语意检索", "")
            if isinstance(retrieval_content, str) and retrieval_content.strip() != "":
                return True, retrieval_content.strip()
        except Exception as e:
            print(f"⚠️ 解析语意检索指令异常：{e}")
        return False, ""
    def _parse_info_instruction(self, info_str, prefix):
        """解析用户信息/自我信息指令，返回键值对列表"""
        if not info_str or not prefix:
            return []
        # 清理前缀
        clean_str = info_str.replace(f"{prefix}[", "").replace("]", "").strip()
        if not clean_str:
            return []
        # 拆分多个键值对
        kv_pairs = clean_str.split("，")
        result = []
        for pair in kv_pairs:
            if "=" in pair:
                k, v = pair.split("=", 1)
                k = k.strip()
                v = v.strip()
                if k and v:
                    result.append((k, v))
        return result

    def _build_prompt(self, user_input, need_search=False):
        """拼接 Prompt（提示词层 + 读取层数据）"""
        data = self.reader.read_all_data(user_input, need_search)
        # === 使用 logging 记录上下文 ===
        context_log = (
            f"👤 用户输入: {data.get('user_input', '')}\n"
            f"🕒 时间: {data.get('current_date', '')} {data.get('current_time', '')}\n"
            f"💤 当前状态: {data.get('current_state', '')}\n"
            f"📊 情绪数值: 精力={data.get('energy_val', 0)}, 情绪={data.get('emotion_val', 0)}, "
            f"专注={data.get('focus_val', 0)}, 共鸣={data.get('empathy_val', 0)}\n"
            f"💭 最近感受: {data.get('recent_feelings', '（无）')}\n"
            f"🤖 自我认知: {data.get('self_cognition', '（无）')}\n"
            f"👥 他人认知: {data.get('other_cognition', '（无）')}\n"
            f"📅 最后交互: {data.get('last_input_time', '（首次对话）')}\n"
            f"📚 历史摘要: {data.get('history_summary', '（无）')}\n"
            f"🧾 用户信息: {data.get('user_info', '（无）')}\n"
            f"🔖 自我信息: {data.get('self_info', '（无）')}"
        )
        if data.get("faiss_top5"):
            context_log += f"\n🔍 检索结果: {data['faiss_top5']}"
        
        logger.debug("🧠 AI 决策上下文（输入日志）\n" + context_log)
        # === 日志记录结束 ===




        if not need_search:
        # 替换为模糊提示，引导AI主动请求检索
            data["history_summary"] = "【长期记忆已存储，需通过语意检索功能激活具体内容】"
        prompt = PROMPT_TEMPLATE.format(**data)
        if data["faiss_top5"]:
            prompt += f"\n10. 语意检索结果：{data['faiss_top5']}"
        return prompt

    def _parse_ai_output(self, ai_output, user_input=None):
        """解析大模型结构化输出（优化下一次活动时间数值解析）"""
        if not ai_output:
            return get_fallback_response(user_input)
        
        # 清理字段冗余字符的工具函数
        def clean_field(text, prefix):
            if not text:
                return ""
            return text.replace(f"{prefix}[", "").replace("]", "").strip() or ""

        # 清理情绪数字段
        emotion_str = clean_field(ai_output.get("情绪数值", ""), "情绪数值").replace(" ", "").rstrip("，")
        def extract_num(key):
            match = re.search(rf"{key}=([-+]?\d+\.?\d*)", emotion_str)
            return float(match.group(1)) if match else 0.0

        # 解析用户信息/自我信息
        user_info_str = clean_field(ai_output.get("用户信息", ""), "用户信息")
        self_info_str = clean_field(ai_output.get("自我信息", ""), "自我信息")
        user_info_kv = self._parse_info_instruction(user_info_str, "用户信息")
        self_info_kv = self._parse_info_instruction(self_info_str, "自我信息")

        # 核心：解析下一次活动时间数值（严格校验格式和范围）
        try:
            # 提取数值并清理格式
            next_activity_str = clean_field(ai_output.get("下一次活动时间数值", ""), "下一次活动时间数值")
            # 正则提取纯数字（兼容"时间=300"或仅"300"）
            num_match = re.search(r"\d+", next_activity_str)
            next_activity = int(num_match.group()) if num_match else 180
            # 限制数值范围（180秒 ~ 8小时=28800秒）
            next_activity = max(180, min(next_activity, 28800))
        except Exception as e:
            print(f"⚠️ 解析下一次活动时间数值失败：{e}，使用默认值180秒")
            next_activity = 180

        # 提取核心字段
        try:
            return {
                "回复文本": clean_field(ai_output.get("自然回复", ""), "自然回复"),
                "当前感受_心情": clean_field(ai_output.get("心情", ""), "心情"),
                "当前感受_想法": clean_field(ai_output.get("想法", ""), "想法"),
                "事件摘要": ai_output.get("事件摘要", "").strip() or "",
                "精力值": extract_num("精力值"),
                "情绪值": extract_num("情绪值"),
                "专注值": extract_num("专注值"),
                "共鸣值": extract_num("共鸣值"),
                "功能调用": "",
                "下一次活动时间数值": next_activity,  # 仅存储纯数字（秒）
                "当前状态": clean_field(ai_output.get("当前状态", ""), "当前状态"),
                "自我认知": clean_field(ai_output.get("自我认知", ""), "自我认知"),
                "他人认知": clean_field(ai_output.get("他人认知", ""), "他人认知"),
                "用户信息": user_info_kv,
                "自我信息": self_info_kv
            }
        except Exception as e:
            print(f"⚠️ 解析大模型输出警告：{e}")
            fallback = get_fallback_response(user_input)
            # 确保兜底值符合范围
            fallback["下一次活动时间数值"] = 300
            return fallback

    def _execute_scheduled_task(self, delay_seconds, last_user_input):
        """新增：定时任务执行逻辑（到时间后激活的操作）"""
        try:
            # 1. 等待指定秒数
            time.sleep(delay_seconds)
            
            # 2. 记录任务执行日志
            current_time = datetime.now(pytz.timezone("Asia/Shanghai")).strftime("%Y-%m-%d %H:%M:%S")
            print(f"\n=====================")
            print(f"⏰ 定时任务触发 | 时间：{current_time}")
            print(f"🔍 触发延迟：{delay_seconds}秒 | 关联用户输入：{last_user_input}")
            print(f"=====================")

            # 3. 核心业务逻辑（可根据需求自定义）
            # 示例1：生成定时回复Prompt并调用AI
            task_prompt = self._build_prompt(
                user_input=f"定时任务：基于历史对话「{last_user_input}」主动发起互动",
                need_search=True  # 执行语意检索
            )
            ai_output = self.qwen.call(task_prompt)
            ai_parsed = self._parse_ai_output(ai_output, f"定时任务：{last_user_input}")
            
            # 4. 输出定时任务结果
            print(f"\n📝 定时任务AI回复：{ai_parsed['回复文本']}")
            print(f"😊 定时任务心情：{ai_parsed['当前感受_心情']}")
            print(f"💡 定时任务想法：{ai_parsed['当前感受_想法']}")
            
            # 5. 写入数据库（保持数据一致性）
            self._write_to_db(f"定时任务：{last_user_input}", ai_parsed)
            
            # 6. 更新向量库
            if ai_parsed["事件摘要"].strip() != "":
                self.faiss.add_text(ai_parsed["事件摘要"])
                
            print(f"✅ 定时任务执行完成，数据已写入数据库")

        except Exception as e:
            print(f"❌ 定时任务执行失败：{e}")

    def _start_scheduled_task(self, delay_seconds, last_user_input):
        """新增：启动定时任务（后台线程，不阻塞主对话）"""
        # 校验秒数范围
        delay_seconds = max(180, min(delay_seconds, 28800))
        
        # 创建守护线程（主程序退出时自动终止）
        task_thread = threading.Thread(
            target=self._execute_scheduled_task,
            args=(delay_seconds, last_user_input),
            daemon=True
        )
        
        # 启动线程并记录
        task_thread.start()
        self.scheduled_tasks.append(task_thread)
        print(f"\n⏳ 已启动定时任务：{delay_seconds}秒后触发（线程ID：{task_thread.ident}）")

    def _write_to_db(self, user_input, ai_parsed):
        """将解析后的结果写入对应数据库"""
        try:
            # 1. 原有写入逻辑
            self.db.write_long_term_memory(user_input, str(ai_parsed), "user")
            if ai_parsed["当前感受_心情"] and ai_parsed["当前感受_想法"]:
                self.db.write_feelings(ai_parsed["当前感受_心情"], ai_parsed["当前感受_想法"])
            self.db.write_emotion_values(ai_parsed["精力值"], 
                                         ai_parsed["情绪值"], 
                                         ai_parsed["专注值"], 
                                         ai_parsed["共鸣值"]
                                         )
            if ai_parsed["事件摘要"]:
                self.db.write_event_summary(ai_parsed["事件摘要"], None)
        
            if ai_parsed["自我认知"].strip():
                self.db.write_self_cognition(ai_parsed["自我认知"])
            
            if ai_parsed["他人认知"].strip():
                self.db.write_other_cognition(ai_parsed["他人认知"])
            # 2. 写入用户信息
            for k, v in ai_parsed["用户信息"]:
                self.db.write_user_info(k, v)
            
            # 3. 写入自我信息
            for k, v in ai_parsed["自我信息"]:
                self.db.write_self_info(k, v)
                
        except Exception as e:
            print(f"⚠️ 数据库写入警告：{e}")

    def run(self):
        """主程序入口：接收输入→拼接Prompt→调用模型→解析指令→检索→输出→写入数据库→启动定时任务"""
        print("=== 智能对话机器人（含定时任务版）===")
        print("📌 支持基于「下一次活动时间数值」的周期激活功能")
        print("📌 定时任务会在后台执行，不影响正常对话\n")
        
        while True:
            try:
                # 1. 接收用户输入
                user_input = input("\n请输入你的文本（输入'exit'退出）：")
                if user_input.lower() == "exit":
                    print("\n🔄 等待所有后台定时任务完成...")
                    # 等待所有非守护线程完成（可选）
                    for task in self.scheduled_tasks:
                        if task.is_alive():
                            task.join(timeout=5)
                    print("程序结束！")
                    break

                # 第一步：拼接基础Prompt（不执行检索）
                base_prompt = self._build_prompt(user_input, need_search=False)
                print("\n【基础Prompt（未检索）】：")
                print("-" * 80)
                print(base_prompt)
                print("-" * 80)

                # 第二步：调用大模型，获取AI的指令（是否需要检索）
                ai_raw_output = self.qwen.call(base_prompt)
                print("\n【AI原始输出（含检索指令）】：")
                print(ai_raw_output)

                # 第三步：解析AI的检索指令
                need_search, search_content = self._parse_search_instruction(ai_raw_output)
                print(f"\n【检索指令解析】：AI{'要求' if need_search else '未要求'}检索，检索内容：{search_content}")

                # 第四步：如果AI要求检索，重新拼接带检索结果的Prompt并再次调用
                final_ai_output = ai_raw_output
                if need_search:
                    search_prompt = self._build_prompt(search_content or user_input, need_search=True)
                    print("\n【带检索结果的Prompt】：")
                    print("-" * 80)
                    print(search_prompt)
                    print("-" * 80)
                    final_ai_output = self.qwen.call(search_prompt)
                    print("\n【AI最终输出（含检索结果）】：")
                    print(final_ai_output)

                # 第五步：解析结构化输出
                ai_parsed = self._parse_ai_output(final_ai_output, user_input)
                print("\n【结构化输出】：")
                for key, value in ai_parsed.items():
                    if key == "下一次活动时间数值":
                        print(f"{key}：{value} 秒")  # 明确标注单位
                    else:
                        print(f"{key}：{value}")

                # 第六步：写入对应数据库
                self._write_to_db(user_input, ai_parsed)
                
                # 第七步：添加事件摘要到向量库
                if ai_parsed["事件摘要"].strip() != "":
                    self.faiss.add_text(ai_parsed["事件摘要"])
                
                # 第八步：启动定时任务（核心新增逻辑）
                self._start_scheduled_task(
                    delay_seconds=ai_parsed["下一次活动时间数值"],
                    last_user_input=user_input
                )
                
                print("\n✅ 所有数据已写入数据库，定时任务已启动！")
                
            except Exception as e:
                print(f"❌ 单次对话错误：{e}")
                print("⚠️ 程序已恢复，可继续输入...")

# ====================== 程序启动 ======================
if __name__ == "__main__":
    print("请选择模型后端：")
    print("1. 云端 API（阿里云 DashScope）")
    print("2. 本地模型（llama.cpp + GGUF）")
    choice = input("请输入 1 或 2：").strip()

    if choice == "1":
        api_key = input("请输入阿里云API Key：")
        from qwen_api import QwenAPI
        chatbot = ChatbotCore()  # ← 不传 api_key
        chatbot.qwen = QwenAPI(api_key)  # ← 手动赋值
    elif choice == "2":
        MODEL_PATH = r"F:\xinbanai5.0\备份\models\qwen2-7b-instruct-q4_k_m.gguf"
        if not os.path.exists(MODEL_PATH):
            print(f"❌ 本地模型未找到：{MODEL_PATH}")
            sys.exit(1)
        from local_qwen_model import LocalQwenModel
        chatbot = ChatbotCore()  # ← 不传 api_key
        chatbot.qwen = LocalQwenModel(MODEL_PATH)  # ← 手动赋值
    else:
        print("无效选择，退出程序")
        sys.exit(1)

    chatbot.run()