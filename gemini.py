import os
from openai import OpenAI

# 第一步：获取 Gemini API Key
# 请访问 https://ai.google.dev/gemini-api/docs/api-key 获取免费 API Key
# 推荐通过环境变量设置，以避免硬编码
os.environ["GEMINI_API_KEY"] = "AIzaSyATMdBobaJnW3Mx-Vib0i7CeJZD9eTEIPw"  # 替换为您的实际 Key，或直接使用环境变量

# 初始化 OpenAI 客户端（指向 Gemini 的兼容端点）
client = OpenAI(
    api_key=os.environ["GEMINI_API_KEY"],
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# 示例：调用聊天完成 API
response = client.chat.completions.create(
    model="gemini-3-flash-preview",  # 可选模型：gemini-1.5-flash、gemini-1.5-pro 等（查看最新模型列表：https://ai.google.dev/gemini-api/docs/models）
    messages=[
        {"role": "system", "content": "你是一个有帮助的助手。"},
        {"role": "user", "content": "请用中文解释量子计算的基本原理。"}
    ],
    temperature=0.7,
    max_tokens=500
)

# 输出响应
print("Gemini 响应：")
print(response.choices[0].message.content)

# 可选：流式输出示例
# print("\n--- 流式输出示例 ---")
# stream_response = client.chat.completions.create(
#     model="gemini-1.5-flash",
#     messages=[{"role": "user", "content": "讲一个简短的笑话。"}],
#     stream=True
# )

# for chunk in stream_response:
#     if chunk.choices[0].delta.content:
#         print(chunk.choices[0].delta.content, end="", flush=True)
# print("\n")