import os
import json
from typing import Any

from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

# 1. 定义工具函数
def calculate(expression: str) -> str:
    try:
        import ast

        node = ast.parse(expression, mode="eval")

        def eval_node(n: ast.AST) -> Any:
            if isinstance(n, ast.Expression):
                return eval_node(n.body)
            if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)):
                return n.value
            if isinstance(n, ast.UnaryOp) and isinstance(n.op, (ast.UAdd, ast.USub)):
                v = eval_node(n.operand)
                return +v if isinstance(n.op, ast.UAdd) else -v
            if isinstance(n, ast.BinOp) and isinstance(
                n.op,
                (
                    ast.Add,
                    ast.Sub,
                    ast.Mult,
                    ast.Div,
                    ast.FloorDiv,
                    ast.Mod,
                    ast.Pow,
                ),
            ):
                left = eval_node(n.left)
                right = eval_node(n.right)
                if isinstance(n.op, ast.Add):
                    return left + right
                if isinstance(n.op, ast.Sub):
                    return left - right
                if isinstance(n.op, ast.Mult):
                    return left * right
                if isinstance(n.op, ast.Div):
                    return left / right
                if isinstance(n.op, ast.FloorDiv):
                    return left // right
                if isinstance(n.op, ast.Mod):
                    return left % right
                if isinstance(n.op, ast.Pow):
                    return left**right
            raise ValueError("unsupported expression")

        return str(eval_node(node))
    except Exception:
        return "计算失败，请检查表达式格式"

def search(query: str) -> str:
    mock_data = {
        "今天日期": "2025年8月18日",
        "Python最新版本": "Python 3.13",
        "LangChain最新版本": "LangChain 0.3.0"
    }
    return mock_data.get(query, f"未找到'{query}'的信息")

# 2. 初始化工具、模型
tools = [
    Tool(name="Calculator", func=calculate, description="数学计算时使用"),
    Tool(name="Search", func=search, description="查询实时/未知信息时使用")
]

chat_model = ChatOpenAI(
    api_key="AIzaSyATMdBobaJnW3Mx-Vib0i7CeJZD9eTEIPw",
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    model="gemini-3-flash-preview",
)

TOOLS_BY_NAME = {t.name: t for t in tools}

SYSTEM_PROMPT = """你是带记忆的工具助手。
可用工具：
- Calculator：数学计算
- Search：查询信息（本地 mock）

当且仅当你需要调用工具时，输出严格 JSON（不要额外文字）：
{"tool":"Calculator","input":"2+2"}
或
{"tool":"Search","input":"今天日期"}

我会把工具返回值作为一条新消息发给你，你再用自然语言给出最终答案。"""


def _maybe_parse_tool_call(text: str) -> dict[str, str] | None:
    if not isinstance(text, str):
        return None
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    try:
        obj = json.loads(text[start : end + 1])
    except Exception:
        return None
    if not isinstance(obj, dict):
        return None
    tool = obj.get("tool")
    tool_input = obj.get("input")
    if not isinstance(tool, str) or not isinstance(tool_input, str):
        return None
    return {"tool": tool, "input": tool_input}


history_store: dict[str, InMemoryChatMessageHistory] = {}


def get_history(session_id: str) -> InMemoryChatMessageHistory:
    if session_id not in history_store:
        history_store[session_id] = InMemoryChatMessageHistory()
    return history_store[session_id]


def run_turn(session_id: str, user_input: str, max_steps: int = 3) -> str:
    history = get_history(session_id)
    history.add_message(HumanMessage(content=user_input))

    for _ in range(max_steps):
        messages = [SystemMessage(content=SYSTEM_PROMPT), *history.messages]
        ai: AIMessage = chat_model.invoke(messages)
        history.add_message(ai)

        tool_call = _maybe_parse_tool_call(ai.content)
        if not tool_call:
            return str(ai.content)

        tool_name = tool_call["tool"]
        tool_input = tool_call["input"]
        tool = TOOLS_BY_NAME.get(tool_name)
        if not tool:
            history.add_message(
                HumanMessage(content=f"工具调用失败：未知工具 {tool_name!r}。请直接回答或改用可用工具。")
            )
            continue

        try:
            tool_output = tool.func(tool_input)
        except Exception as e:
            tool_output = f"工具执行异常：{type(e).__name__}: {e}"

        history.add_message(HumanMessage(content=f"工具 {tool_name} 返回：{tool_output}"))

    return "执行步数超限，请换一种问法或减少连续工具调用。"

# 4. 交互测试
session_id = "test"
print("智能助手（输入'quit'退出，'clear'清空记忆）：")
while True:
    user_input = input("你：")
    if user_input.lower() == "quit":
        break
    if user_input.lower() == "clear":
        get_history(session_id).clear()
        print("助手：记忆已清空")
        continue

    print(f"助手：{run_turn(session_id, user_input)}")
