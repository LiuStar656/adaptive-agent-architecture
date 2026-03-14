from openai import OpenAI
import os
import json
# 导入prompt_config中的配置和工具函数
from prompt_config import get_qwen_structured_prompt, get_fallback_response

class QwenAPI:
    def __init__(self, api_key):
        # 初始化OpenAI兼容客户端（对接阿里云百炼）
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        self.model = "qwen3-max-2026-01-23"  # 可替换为qwen-turbo/qwen-plus等

    # 移除原有的_get_structured_prompt方法，改用prompt_config中的工具函数
    def call(self, prompt):
        """调用阿里云百炼（OpenAI兼容模式），返回结构化JSON"""
        # 从prompt_config获取完整结构化提示词
        full_prompt = get_qwen_structured_prompt(prompt)
        
        try:
            # 非流式调用（适配原有程序逻辑，如需流式可调整）
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": full_prompt}],
                temperature=0.7,
                top_p=0.8,
                # 禁用思考过程（避免干扰JSON格式），如需保留可打开
                # extra_body={"enable_thinking": True},
            )
            
            # 提取回复内容
            raw_content = completion.choices[0].message.content.strip()
            if not raw_content:
                raise ValueError("AI返回空内容")
            
            # 解析JSON
            try:
                return json.loads(raw_content)
            except json.JSONDecodeError:
                print(f"⚠️ 返回非标准JSON，尝试清理格式：{raw_content[:100]}...")
                # 清理多余内容（如思考过程、换行、多余空格）
                clean_content = raw_content.strip() \
                    .replace("```json", "") \
                    .replace("```", "") \
                    .replace("\n", "") \
                    .strip()
                # 再次尝试解析
                try:
                    return json.loads(clean_content)
                except json.JSONDecodeError:
                    print(f"❌ 清理后仍无法解析JSON：{clean_content[:100]}...")
                    # 触发兜底回复
                    raise ValueError("JSON解析失败")
                    
        except Exception as e:
            print(f"❌ API调用失败：{str(e)}")
            # 提取用户输入（兼容原有逻辑）
            user_input = prompt.split('输入文本（input）：')[1].split('\n')[0] if '输入文本（input）：' in prompt else "你好"
            # 从prompt_config获取兜底回复
            return get_fallback_response(user_input)

    # 可选：流式调用（带思考过程，用于单独测试）
    def stream_call(self, prompt):
        """流式调用（带思考过程），仅用于测试"""
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                extra_body={"enable_thinking": True},
                stream=True
            )
            is_answering = False
            print("\n" + "=" * 20 + "思考过程" + "=" * 20)
            for chunk in completion:
                delta = chunk.choices[0].delta
                if hasattr(delta, "reasoning_content") and delta.reasoning_content is not None:
                    if not is_answering:
                        print(delta.reasoning_content, end="", flush=True)
                if hasattr(delta, "content") and delta.content:
                    if not is_answering:
                        print("\n" + "=" * 20 + "完整回复" + "=" * 20)
                        is_answering = True
                    print(delta.content, end="", flush=True)
        except Exception as e:
            print(f"❌ 流式调用失败：{e}")

# 测试代码（单独运行此文件验证）
if __name__ == "__main__":
    api_key = input("请输入阿里云DashScope API Key：")
    qwen = QwenAPI(api_key)
    # 测试流式调用（带思考过程）
    qwen.stream_call("你是谁？请用结构化JSON回答")