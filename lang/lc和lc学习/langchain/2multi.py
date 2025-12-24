from langchain_openai import ChatOpenAI

# 初始化模型
chat_model = ChatOpenAI(
    api_key="AIzaSyDWIExbwSN6Y6nWtPkxlGPEkejd9KHWVgQ",
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    model="gemini-3-flash-preview",
)

from langchain_core.runnables import RunnableLambda
from langchain_core.prompts import ChatPromptTemplate

# 1. 定义路由判断函数（判断问题类型）
def route_question(inputs):
    question = inputs["input"]
    # 简单规则判断（实际可用模型优化判断逻辑）
    if any(keyword in question.lower() for keyword in ["编程", "代码", "python"]):
        print("tech_chain被调用")
        return "tech_chain"  # 技术问题链
    elif any(keyword in question.lower() for keyword in ["天气", "温度", "下雨"]):
        print("weather_chain被调用")
        return "weather_chain"  # 天气问题链
    else:
        print("general_chain被调用")
        return "general_chain"  # 通用问题链

# 2. 定义各分支链
# 技术链
tech_prompt = ChatPromptTemplate.from_template("用专业术语回答技术问题：{input}")
tech_chain = tech_prompt | chat_model

# 天气链（模拟调用工具）
def weather_tool(inputs):
    return f"查询到{inputs['input']}：25℃，晴"
weather_chain = RunnableLambda(weather_tool)

# 通用链
general_prompt = ChatPromptTemplate.from_template("用简洁语言回答：{input}")
general_chain = general_prompt | chat_model

# 3. 定义路由映射（链名称→链实例）
route_map = {
    "tech_chain": tech_chain,
    "weather_chain": weather_chain,
    "general_chain": general_chain
}

# 4. 构建路由链
def router_chain(inputs):
    route_key = route_question(inputs)
    selected_chain = route_map[route_key]
    return selected_chain.invoke(inputs)

# 测试路由链
print("技术问题回答：", router_chain({"input": "Python如何实现多线程？"}).content)
print("天气问题回答：", router_chain({"input": "北京天气"}))
print("通用问题回答：", router_chain({"input": "推荐一部科幻电影"}).content)
