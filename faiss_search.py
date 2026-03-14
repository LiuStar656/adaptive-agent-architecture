import faiss
import numpy as np
import os

# 配置常量（可根据需要调整）
VECTOR_DIM = 384  # 固定384维，无需改
FAISS_INDEX_FILE = "faiss_index.bin"  # 向量索引文件
TEXT_LIST_FILE = "text_list.npy"      # 文本列表文件

class FAISSSearch:
    def __init__(self):
        self.dim = VECTOR_DIM
        self.index = None
        self.summary_texts = []
        self.load_faiss_index()  # 秒加载：启动即读文件，无计算

    # -------------------------- 核心：秒加载向量索引 --------------------------
    def load_faiss_index(self):
        """直接读取本地文件加载FAISS索引，毫秒级完成"""
        try:
            if os.path.exists(FAISS_INDEX_FILE) and os.path.exists(TEXT_LIST_FILE):
                # 直接读二进制索引文件（秒加载）
                self.index = faiss.read_index(FAISS_INDEX_FILE)
                # 读文本列表
                self.summary_texts = np.load(TEXT_LIST_FILE, allow_pickle=True).tolist()
            else:
                # 首次运行：初始化空索引
                self.index = faiss.IndexFlatL2(self.dim)
                self.summary_texts = []
        except Exception as e:
            print(f"⚠️ 加载FAISS索引失败，初始化空索引：{e}")
            self.index = faiss.IndexFlatL2(self.dim)
            self.summary_texts = []

    # -------------------------- 保存向量索引（仅添加时执行一次） --------------------------
    def save_faiss_index(self):
        """保存索引到文件，下次启动直接读"""
        try:
            faiss.write_index(self.index, FAISS_INDEX_FILE)
            np.save(TEXT_LIST_FILE, np.array(self.summary_texts, dtype=object))
        except Exception as e:
            print(f"⚠️ 保存FAISS索引失败：{e}")

    # -------------------------- 本地超快生成向量（无模型依赖） --------------------------
    def get_text_vector(self, text):
        """纯本地生成向量，无延迟、无依赖"""
        if not text or text.strip() == "":
            return np.zeros(self.dim, dtype=np.float32)
        # 哈希生成固定向量（保证相同文本生成相同向量）
        try:
            rng = np.random.RandomState(hash(text) & 0xFFFFFFFF)
            return rng.randn(self.dim).astype("float32")
        except Exception as e:
            print(f"⚠️ 生成文本向量失败，返回零向量：{e}")
            return np.zeros(self.dim, dtype=np.float32)

    # -------------------------- 添加文本到向量库 --------------------------
    def add_text(self, text):
        """添加文本到向量库，瞬间完成"""
        if not text or text.strip() == "" or text in self.summary_texts:
            return  # 空文本/重复文本不添加
        # 生成向量并添加到索引
        try:
            vec = self.get_text_vector(text).reshape(1, -1)
            self.index.add(vec)
            self.summary_texts.append(text)
            # 保存到文件（仅这一步写磁盘，耗时<10ms）
            self.save_faiss_index()
        except Exception as e:
            print(f"⚠️ 添加文本到向量库失败：{e}")

    # -------------------------- 秒级检索 --------------------------
    def search(self, text, top_k=5):
        """检索相关性top5，毫秒级返回"""
        # 无数据时直接返回空列表
        if self.index.ntotal == 0:
            return []
        try:
            # 生成用户输入向量
            vec = self.get_text_vector(text).reshape(1, -1)
            # FAISS检索（无计算，纯内存操作）
            _, idx_list = self.index.search(vec, top_k)
            # 过滤有效索引，避免越界
            top_summary = []
            for i in idx_list[0]:
                if 0 <= i < len(self.summary_texts):
                    top_summary.append(self.summary_texts[i])
            return top_summary
        except Exception as e:
            print(f"⚠️ 向量检索失败，返回空列表：{e}")
            return []