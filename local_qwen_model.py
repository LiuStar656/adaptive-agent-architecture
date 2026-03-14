# local_qwen_model.py （GPU 优化版）

import os
from llama_cpp import Llama
import json
import re
from prompt_config import get_fallback_response

def load_local_qwen2(model_path):
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"模型文件不存在: {model_path}")
    
    print("🚀 正在加载 Qwen2-7B 到 GPU（目标显存 ≤1GB）...")
    
    llm = Llama(
        model_path=model_path,
        n_ctx=2048,           # 提升上下文，避免截断（原1024不够）
        n_threads=1,          # 减少 CPU 线程（GPU 主导）
        n_threads_batch=1,
        n_batch=512,
        n_gpu_layers=35,      # ← 关键！Qwen2-7B 约36层，尽量全卸载到GPU
        use_mlock=False,
        offload_kqv=True,     # KQV 张量也上 GPU
        low_vram=True,        # ← 关键！启用低显存模式（控制在1GB内）
        flash_attn=True,      # 如果支持，启用更快注意力
        verbose=False
    )
    print("✅ 模型加载完成！GPU 将主导推理。")
    return llm


class LocalQwenModel:
    def __init__(self, model_path):
        self.model = load_local_qwen2(model_path)

    def call(self, prompt):
        messages = [
            {"role": "system", "content": "你必须严格按照指定 JSON 格式回复，不要包含任何额外文本、注释或 Markdown。"},
            {"role": "user", "content": prompt}
        ]

        try:
            response = self.model.create_chat_completion(
                messages=messages,
                max_tokens=512,       # 减少生成长度，加快速度
                temperature=0.7,
                top_p=0.9,
                repeat_penalty=1.1,
                stop=["</s>", "```", "or and("]  # 防止重复输出模板
            )

            raw_content = response["choices"][0]["message"]["content"].strip()
            if not raw_content:
                raise ValueError("空回复")

            # === JSON 解析（同前）===
            try:
                return json.loads(raw_content)
            except json.JSONDecodeError:
                clean_content = re.sub(r"```(?:json)?", "", raw_content)
                match = re.search(r"\{.*\}", clean_content, re.DOTALL)
                if match:
                    return json.loads(match.group(0))
                else:
                    raise ValueError("无法提取 JSON")

        except Exception as e:
            print(f"⚠️ 推理失败: {e}")
            user_input = "你好"
            if '输入文本（input）：' in prompt:
                user_input = prompt.split('输入文本（input）：')[1].split('\n')[0]
            return get_fallback_response(user_input)