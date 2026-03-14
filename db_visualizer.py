#!/usr/bin/env python3
"""
XinBanAI Framework - 数据库可视化工具 (tkinter版)
Python自带，展示完整记忆，表头与数据严格对齐
"""

import sqlite3
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import os

DB_PATH = "chatbot.db"

class DBViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("XinBanAI Framework - 完整数据主权中心")
        self.root.geometry("1100x800")
        self.root.configure(bg='#1a1a2e')
        
        # 数据库连接
        self.conn = sqlite3.connect(DB_PATH)
        
        # 标题
        title = tk.Label(root, text="🏛️ XinBanAI 完整数据主权中心", 
                        font=("Microsoft YaHei", 20, "bold"),
                        bg='#1a1a2e', fg='#00d4ff')
        title.pack(pady=10)
        
        subtitle = tk.Label(root, text="完整展示所有记忆，表头与数据严格对齐，证明框架数据主权",
                           font=("Microsoft YaHei", 12),
                           bg='#1a1a2e', fg='#888888')
        subtitle.pack()
        
        # 主框架
        main_frame = tk.Frame(root, bg='#1a1a2e')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 左侧：表列表
        left_frame = tk.Frame(main_frame, bg='#16213e', bd=2, relief=tk.RIDGE)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        tk.Label(left_frame, text="数据表", font=("Microsoft YaHei", 12, "bold"),
                bg='#16213e', fg='#00d4ff').pack(pady=10)
        
        self.tables = [
            ("emotion_values", "📊 情绪数值"),
            ("self_cognition", "🧠 自我认知"),
            ("other_cognition", "👤 他人认知"),
            ("user_info", "🔖 用户画像"),
            ("feelings", "💭 感受记录"),
            ("long_term_memory", "💾 长期记忆"),
            ("event_summary", "📝 事件摘要"),
            ("self_info", "🤖 自我信息")
        ]
        
        for table, label in self.tables:
            btn = tk.Button(left_frame, text=label, 
                          font=("Microsoft YaHei", 10),
                          bg='#0f3460', fg='white',
                          activebackground='#e94560',
                          command=lambda t=table: self.show_table(t))
            btn.pack(fill=tk.X, padx=10, pady=2)
        
        # 右侧：数据展示（使用grid确保对齐）
        right_frame = tk.Frame(main_frame, bg='#16213e', bd=2, relief=tk.RIDGE)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        
        # 表名标签
        self.table_label = tk.Label(right_frame, text="选择左侧表查看完整数据",
                                   font=("Microsoft YaHei", 14, "bold"),
                                   bg='#16213e', fg='#e94560')
        self.table_label.pack(pady=10)
        
        # 统计信息
        self.stats_label = tk.Label(right_frame, text="",
                                   font=("Microsoft YaHei", 10),
                                   bg='#16213e', fg='#00d4ff')
        self.stats_label.pack()
        
        # Canvas容器
        canvas_frame = tk.Frame(right_frame, bg='#16213e')
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 滚动条
        v_scroll = tk.Scrollbar(canvas_frame, orient=tk.VERTICAL)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.canvas = tk.Canvas(canvas_frame, bg='#0f3460', 
                               yscrollcommand=v_scroll.set,
                               highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        v_scroll.config(command=self.canvas.yview)
        
        # 内部Frame放置数据（使用grid）
        self.data_frame = tk.Frame(self.canvas, bg='#0f3460')
        self.canvas.create_window((0, 0), window=self.data_frame, anchor='nw')
        
        # 绑定滚动
        self.data_frame.bind("<Configure>", self.on_frame_configure)
        
        # 底部：数据主权声明
        bottom = tk.Frame(root, bg='#16213e', bd=2, relief=tk.RIDGE)
        bottom.pack(fill=tk.X, padx=20, pady=10)
        
        principles = ["🛡️ 框架拥有所有记忆", "🔒 数据完全本地", 
                     "🚫 LLM仅作为工具", "☁️ 零云端依赖"]
        for i, p in enumerate(principles):
            tk.Label(bottom, text=p, font=("Microsoft YaHei", 10, "bold"),
                    bg='#16213e', fg='#00d4ff').pack(side=tk.LEFT, padx=20, pady=10)
        
        # 刷新按钮
        tk.Button(bottom, text="🔄 刷新数据", command=self.refresh,
                 font=("Microsoft YaHei", 10, "bold"),
                 bg='#e94560', fg='white').pack(side=tk.RIGHT, padx=20, pady=5)
        
        # 状态栏
        self.status = tk.Label(root, text=f"数据库: {DB_PATH} | 就绪",
                              font=("Microsoft YaHei", 9),
                              bg='#1a1a2e', fg='#666666')
        self.status.pack(side=tk.BOTTOM, fill=tk.X, padx=20)
        
        # 默认显示情绪数值
        self.show_table("emotion_values")
    
    def on_frame_configure(self, event=None):
        """配置Canvas滚动区域"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        # 设置Canvas宽度为data_frame宽度
        self.canvas.configure(width=self.data_frame.winfo_width())
    
    def show_table(self, table_name):
        """显示指定表的完整数据，表头与数据严格对齐"""
        try:
            cursor = self.conn.cursor()
            
            # 获取列名
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [col[1] for col in cursor.fetchall()]
            
            # 获取完整数据
            cursor.execute(f"SELECT * FROM {table_name} ORDER BY id")
            rows = cursor.fetchall()
            
            # 清空旧数据
            for widget in self.data_frame.winfo_children():
                widget.destroy()
            
            # 配置grid权重
            for i in range(len(columns)):
                self.data_frame.columnconfigure(i, weight=1, minsize=150)
            
            # 表头（使用grid，固定行0）
            for col_idx, col_name in enumerate(columns):
                header = tk.Label(self.data_frame, 
                                text=str(col_name),
                                font=("Consolas", 10, "bold"),
                                bg='#16213e', fg='#00d4ff',
                                anchor='w', padx=5, pady=5,
                                wraplength=150)
                header.grid(row=0, column=col_idx, sticky='ew', padx=2, pady=2)
            
            # 分隔线（行1）
            sep_frame = tk.Frame(self.data_frame, bg='#e94560', height=2)
            sep_frame.grid(row=1, column=0, columnspan=len(columns), sticky='ew', padx=5, pady=5)
            
            # 数据行（从行2开始）
            for row_idx, row_data in enumerate(rows, start=2):
                for col_idx, cell in enumerate(row_data):
                    cell_str = str(cell) if cell is not None else "NULL"
                    
                    # 使用Message实现自动换行，但宽度固定
                    cell_label = tk.Message(self.data_frame,
                                          text=cell_str,
                                          font=("Consolas", 9),
                                          bg='#0f3460', fg='white',
                                          width=140,  # 固定宽度，自动换行
                                          anchor='nw',
                                          padx=5, pady=3)
                    cell_label.grid(row=row_idx, column=col_idx, 
                                  sticky='nsew', padx=2, pady=1)
            
            # 更新标签
            display_name = dict(self.tables).get(table_name, table_name)
            self.table_label.config(text=f"{display_name} ({table_name})")
            self.stats_label.config(text=f"完整展示 {len(rows)} 条记录 | 表头与数据严格对齐")
            
            # 状态栏
            self.status.config(text=f"数据库: {DB_PATH} | 共 {len(rows)} 条 | 更新: {datetime.now().strftime('%H:%M:%S')}")
            
            # 刷新布局
            self.data_frame.update_idletasks()
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            self.canvas.configure(width=self.data_frame.winfo_width())
            
        except Exception as e:
            messagebox.showerror("错误", f"无法读取表 {table_name}: {str(e)}")
    
    def refresh(self):
        """刷新数据"""
        current = self.table_label.cget("text").split()[0]
        for table, label in self.tables:
            if label in current:
                self.show_table(table)
                break
    
    def on_closing(self):
        """关闭时清理"""
        self.conn.close()
        self.root.destroy()

def main():
    if not os.path.exists(DB_PATH):
        print(f"❌ 数据库不存在：{DB_PATH}")
        print("请先运行框架生成数据")
        return
    
    root = tk.Tk()
    app = DBViewer(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()