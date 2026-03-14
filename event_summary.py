from sqlite_db import SQLiteDB
from datetime import datetime
import pytz

class EventSummary:
    def __init__(self, db_path="chatbot.db", timezone="Asia/Shanghai"):
        self.db = SQLiteDB(db_path)  # 调用数据库层
        self.timezone = pytz.timezone(timezone)  # 统一时区

    def get_history_summary(self, limit=3):
        """
        读取最近N条事件摘要，拼接成「历史摘要」文本
        :param limit: 读取最近的条数，默认3条
        :return: 拼接后的摘要文本（空数据返回空字符串）
        """
        try:
            # 从数据库读取所有事件摘要（含vector、create_time）
            all_summary = self.db.read_event_summary_all()  # 返回格式：[(summary, vector, create_time), ...]
            
            # 过滤无效数据 + 按时间排序（确保最新的在前）
            valid_summary = []
            for s, v, t in all_summary:
                # 过滤空摘要/空时间
                if not (s and s.strip() and t and t.strip()):
                    continue
                # 时间格式校验（兼容不同格式）
                try:
                    # 解析时间字符串为datetime对象（用于排序）
                    summary_time = datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
                    valid_summary.append((s.strip(), summary_time))
                except ValueError:
                    # 时间格式错误则跳过该条
                    continue
            
            # 按时间降序排序（最新的在前）
            valid_summary.sort(key=lambda x: x[1], reverse=True)
            
            # 取最近limit条并拼接
            recent_summary = valid_summary[:limit]
            history_summary = []
            for s, t in recent_summary:
                # 格式化时间（统一展示格式）
                time_str = t.strftime("%Y-%m-%d %H:%M:%S")
                history_summary.append(f"{time_str}：{s}")
            
            # 无数据返回空字符串，有数据则用分号分隔
            return "; ".join(history_summary) if history_summary else ""
        
        except Exception as e:
            # 捕获所有异常，返回空字符串避免程序崩溃
            print(f"⚠️ 读取事件摘要异常：{e}")
            return ""

    def add_summary(self, summary_text):
        """
        快捷添加事件摘要到数据库（封装db层逻辑）
        :param summary_text: 要添加的摘要文本
        """
        if not summary_text or not summary_text.strip():
            print("⚠️ 空摘要文本，跳过添加")
            return
        try:
            # 调用db层写入摘要（vector传None，由db层处理）
            self.db.write_event_summary(summary_text, vector=None)
            print(f"✅ 事件摘要已添加：{summary_text[:50]}...")
        except Exception as e:
            print(f"⚠️ 添加事件摘要失败：{e}")