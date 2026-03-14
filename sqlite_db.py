import sqlite3
import pickle  # 用于向量序列化/反序列化
from datetime import datetime
import pytz

class SQLiteDB:
    def __init__(self, db_path="chatbot.db", timezone="Asia/Shanghai"):
        self.db_path = db_path
        self.timezone = pytz.timezone(timezone)
        self._create_all_tables()  # 首次运行创建所有表
        self._check_and_add_columns()  # 检查并添加缺失字段

    def _create_all_tables(self):
        """创建8个数据库表（新增user_info/self_info）"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 1. 自我认知数据库
        cursor.execute('''CREATE TABLE IF NOT EXISTS self_cognition
                          (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                           content TEXT, 
                           update_time TIMESTAMP)''')
        
        # 2. 长期记忆数据库（按时间+角色存储）
        cursor.execute('''CREATE TABLE IF NOT EXISTS long_term_memory
                          (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                           user_input TEXT, 
                           ai_response TEXT, 
                           role TEXT, 
                           create_time TIMESTAMP)''')
        
        # 3. 他人认知数据库
        cursor.execute('''CREATE TABLE IF NOT EXISTS other_cognition
                          (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                           content TEXT, 
                           update_time TIMESTAMP)''')
        
        # 4. 感受数据库
        cursor.execute('''CREATE TABLE IF NOT EXISTS feelings
                          (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                           mood TEXT, 
                           thought TEXT, 
                           create_time TIMESTAMP)''')
        
        # 5. 情绪数值数据库
        cursor.execute('''CREATE TABLE IF NOT EXISTS emotion_values
                          (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                           energy REAL, 
                           emotion REAL, 
                           focus REAL, 
                           empathy REAL, 
                           create_time TIMESTAMP)''')
        
        # 6. 事件摘要数据库
        cursor.execute('''CREATE TABLE IF NOT EXISTS event_summary
                          (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                           summary TEXT, 
                           vector BLOB,
                           create_time TIMESTAMP)''')
        
        # 7. 新增：用户信息表
        cursor.execute('''CREATE TABLE IF NOT EXISTS user_info
                          (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                           key TEXT UNIQUE,  
                           value TEXT,      
                           update_time TIMESTAMP)''')
        
        # 8. 新增：自我信息表
        cursor.execute('''CREATE TABLE IF NOT EXISTS self_info
                          (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                           key TEXT UNIQUE,  
                           value TEXT,       
                           update_time TIMESTAMP)''')
        
        conn.commit()
        conn.close()

    def _check_and_add_columns(self):
        """检查并添加缺失的字段（兼容旧数据库）"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 检查event_summary表是否有vector字段
        cursor.execute("PRAGMA table_info(event_summary)")
        columns = [col[1] for col in cursor.fetchall()]
        if "vector" not in columns:
            cursor.execute("ALTER TABLE event_summary ADD COLUMN vector BLOB")
            print("✅ 已为event_summary表添加vector字段")

        conn.commit()
        conn.close()

    # -------------------------- 原有读取方法（保持不变） --------------------------
    def read_self_cognition(self):
        """读取最新自我认知（保留历史，只用最新）"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT content FROM self_cognition ORDER BY update_time DESC LIMIT 1")
        res = cursor.fetchone()
        conn.close()
        return res[0] if res else ""
    def read_other_cognition(self):
        """读取最新他人认知（保留历史，只用最新）"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT content FROM other_cognition ORDER BY update_time DESC LIMIT 1")
        res = cursor.fetchone()
        conn.close()
        return res[0] if res else ""

    def read_recent_feelings(self, limit=3):
        """读取最近N条感受（心情+想法）"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT mood, thought FROM feelings ORDER BY create_time DESC LIMIT ?", (limit,))
        res = cursor.fetchall()
        conn.close()
        return "; ".join([f"心情：{m}，想法：{t}" for m, t in res]) if res else ""

    def read_recent_emotion_values(self):
        """读取最新情绪数值"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT energy, emotion, focus, empathy FROM emotion_values ORDER BY create_time DESC LIMIT 1")
        res = cursor.fetchone()
        conn.close()
        return res if res else (0.0, 0.0, 0.0, 0.0)

    def read_last_input_time(self):
        """读取最近一次用户输入时间（用于计算状态）"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT create_time FROM long_term_memory ORDER BY create_time DESC LIMIT 1")
        res = cursor.fetchone()
        conn.close()
        return res[0] if res else None

    def read_event_summary_all(self):
        """读取所有事件摘要（含向量）供FAISS调用"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT summary, vector, create_time FROM event_summary ORDER BY create_time DESC")
        res = cursor.fetchall()
        conn.close()
        # 反序列化向量（pickle转numpy数组）
        result = []
        for s, v, t in res:
            vector = None
            if v:
                try:
                    vector = pickle.loads(v)
                except:
                    vector = None
            result.append((s, vector, t))
        return result

    # -------------------------- 新增：用户信息读写方法 --------------------------
    def read_user_info(self):
        """读取所有用户信息，拼接为键值对字符串"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT key, value FROM user_info ORDER BY update_time DESC")
        res = cursor.fetchall()
        conn.close()
        if not res:
            return ""
        return "; ".join([f"{k}：{v}" for k, v in res])

    def write_user_info(self, key, value):
        """写入/更新用户信息（键存在则更新，不存在则新增）"""
        if not key.strip() or value is None:
            return
        current_time = datetime.now(self.timezone).strftime("%Y-%m-%d %H:%M:%S")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            # 先检查键是否存在
            cursor.execute("SELECT id FROM user_info WHERE key = ?", (key.strip(),))
            if cursor.fetchone():
                # 更新现有记录
                cursor.execute(
                    "UPDATE user_info SET value = ?, update_time = ? WHERE key = ?",
                    (value.strip(), current_time, key.strip())
                )
            else:
                # 新增记录
                cursor.execute(
                    "INSERT INTO user_info (key, value, update_time) VALUES (?, ?, ?)",
                    (key.strip(), value.strip(), current_time)
                )
            conn.commit()
        except Exception as e:
            print(f"⚠️ 写入用户信息失败：{e}")
            conn.rollback()
        finally:
            conn.close()

    # -------------------------- 新增：自我信息读写方法 --------------------------
    def read_self_info(self):
        """读取所有自我信息，拼接为键值对字符串"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT key, value FROM self_info ORDER BY update_time DESC")
        res = cursor.fetchall()
        conn.close()
        if not res:
            return ""
        return "; ".join([f"{k}：{v}" for k, v in res])

    def write_self_info(self, key, value):
        """写入/更新自我信息（键存在则更新，不存在则新增）"""
        if not key.strip() or value is None:
            return
        current_time = datetime.now(self.timezone).strftime("%Y-%m-%d %H:%M:%S")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            # 先检查键是否存在
            cursor.execute("SELECT id FROM self_info WHERE key = ?", (key.strip(),))
            if cursor.fetchone():
                # 更新现有记录
                cursor.execute(
                    "UPDATE self_info SET value = ?, update_time = ? WHERE key = ?",
                    (value.strip(), current_time, key.strip())
                )
            else:
                # 新增记录
                cursor.execute(
                    "INSERT INTO self_info (key, value, update_time) VALUES (?, ?, ?)",
                    (key.strip(), value.strip(), current_time)
                )
            conn.commit()
        except Exception as e:
            print(f"⚠️ 写入自我信息失败：{e}")
            conn.rollback()
        finally:
            conn.close()

    # -------------------------- 原有写入方法（保持不变） --------------------------
    def write_long_term_memory(self, user_input, ai_response, role="user"):
        """写入长期记忆数据库"""
        current_time = datetime.now(self.timezone).strftime("%Y-%m-%d %H:%M:%S")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO long_term_memory (user_input, ai_response, role, create_time) VALUES (?, ?, ?, ?)",
            (user_input, ai_response, role, current_time)
        )
        conn.commit()
        conn.close()

    def write_feelings(self, mood, thought):
        """写入感受数据库"""
        current_time = datetime.now(self.timezone).strftime("%Y-%m-%d %H:%M:%S")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO feelings (mood, thought, create_time) VALUES (?, ?, ?)",
            (mood, thought, current_time)
        )
        conn.commit()
        conn.close()

    def write_emotion_values(self, energy, emotion, focus, empathy):
        """写入情绪数值数据库"""
        current_time = datetime.now(self.timezone).strftime("%Y-%m-%d %H:%M:%S")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO emotion_values (energy, emotion, focus, empathy, create_time) VALUES (?, ?, ?, ?, ?)",
            (energy, emotion, focus, empathy, current_time)
        )
        conn.commit()
        conn.close()

    def write_event_summary(self, summary, vector=None):
        """写入事件摘要数据库（含本地向量）"""
        if not summary.strip():
            return
        current_time = datetime.now(self.timezone).strftime("%Y-%m-%d %H:%M:%S")
        # 序列化向量（numpy数组转pickle二进制）
        vector_blob = None
        if vector is not None:
            try:
                vector_blob = pickle.dumps(vector)
            except Exception as e:
                print(f"⚠️ 向量序列化失败：{e}")
                vector_blob = None
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO event_summary (summary, vector, create_time) VALUES (?, ?, ?)",
                (summary, vector_blob, current_time)
            )
            conn.commit()
        except Exception as e:
            print(f"⚠️ 写入事件摘要失败：{e}")
            conn.rollback()
        finally:
            conn.close()

    def write_self_cognition(self, content):
        if not content.strip(): 
            return
        current_time = datetime.now(self.timezone).strftime("%Y-%m-%d %H:%M:%S")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            # 直接插入 AI 生成的完整认知（不拼接！）
            cursor.execute(
                "INSERT INTO self_cognition (content, update_time) VALUES (?, ?)",
                (content.strip(), current_time)
            )
            conn.commit()
        except Exception as e:
            print(f"⚠️ 写入自我认知失败：{e}")
            conn.rollback()
        finally:
            conn.close()

    def write_other_cognition(self, content):
        """写入他人认知：保存AI生成的完整新认知（追加新记录）"""
        if not content.strip():
            return
        current_time = datetime.now(self.timezone).strftime("%Y-%m-%d %H:%M:%S")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
        # 直接插入新记录（内容已是AI融合后的完整认知）
            cursor.execute(
                "INSERT INTO other_cognition (content, update_time) VALUES (?, ?)",
                (content.strip(), current_time)
            )
            conn.commit()
        except Exception as e:
            print(f"⚠️ 写入他人认知失败：{e}")
            conn.rollback()
        finally:
            conn.close()
