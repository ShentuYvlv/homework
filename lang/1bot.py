from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_openai import ChatOpenAI
from openai import OpenAI

# 初始化模型
chat_model = ChatOpenAI(
    api_key="AIzaSyATMdBobaJnW3Mx-Vib0i7CeJZD9eTEIPw",
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    model="gemini-3-flash-preview"
)

# 定义提示词模板
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是友好的聊天助手，根据历史对话回答。历史：{chat_history}"),
    ("user", "{input}")
])

# 基础链
base_chain = prompt | chat_model

# 多会话历史存储
session_histories = {}
def get_session_history(session_id: str) -> InMemoryChatMessageHistory:
    if session_id not in session_histories:
        session_histories[session_id] = InMemoryChatMessageHistory()
    return session_histories[session_id]

# 带记忆的链
chain = RunnableWithMessageHistory(
    base_chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history",
)

# 交互循环
session_id = input("请输入会话ID：")
config = {"configurable": {"session_id": session_id}}

print("开始聊天（输入'quit'退出，'clear'清空记忆）：")
while True:
    user_input = input("你：")
    if user_input.lower() == "quit":
        break
    if user_input.lower() == "clear":
        get_session_history(session_id).clear()
        print("机器人：记忆已清空")
        continue
    response = chain.invoke({"input": user_input}, config=config)
    print(f"机器人：{response.content}")
