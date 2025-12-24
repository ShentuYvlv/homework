import os
import time
import requests
from typing import Dict, List, Any, TypedDict
from langgraph.graph import StateGraph
 
# Ollama 配置
OLLAMA_API_BASE = "http://localhost:11434/api"
DEFAULT_MODEL = "llama3"
 
# LangSmith 配置
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "your_langsmith_api_key"
os.environ["LANGCHAIN_PROJECT"] = "课程创建-LangGraph"
 
# Ollama API 调用函数
def generate_with_ollama(prompt, model=DEFAULT_MODEL, temperature=0.7, max_tokens=2000):
    """使用 Ollama API 生成内容"""
    try:
        response = requests.post(
            f"{OLLAMA_API_BASE}/generate",
            json={
                "model": model,
                "prompt": prompt,
                "temperature": temperature,
                "stream": False
            }
        )
 
        if response.status_code == 200:
            result = response.json()
            return result.get("response", "")
        else:
            print(f"Ollama API 返回错误状态码: {response.status_code}")
            return f"API调用失败，状态码: {response.status_code}"
    except Exception as e:
        print(f"调用 Ollama API 出错: {e}")
        return f"内容生成失败，请检查 Ollama 服务。错误: {e}"
 
# 课程结构定义
course_structure = {
    "课程名称": "Python数据分析与可视化",
    "章节": [
        {
            "章节名称": "Python数据分析基础",
            "简介": "介绍Python在数据分析中的基本应用。",
            "学习目标": ["理解数据分析的基本概念", "掌握Python数据处理基础语法"]
        },
        {
            "章节名称": "数据可视化入门",
            "简介": "学习常用数据可视化方法与工具。",
            "学习目标": ["了解数据可视化的意义", "掌握常见可视化库的使用"]
        }
    ]
}
 
# 提示词模板
prompt_templates = {
    "概念理解": """
    你是一位教育专家，正在为《{course_name}》课程的《{chapter_name}》章节创建概念理解学习材料。
    章节介绍: {chapter_intro}
    学习目标: {chapter_goals}
    请创建一份全面的概念理解材料，包含核心概念定义、背景知识、相关概念联系等。
    输出格式使用 Markdown，确保标题层级正确，内容应该全部使用中文。
    """,
 
    # 其他模板省略...
}
 
# 1. 章节生成节点
def chapter_generator(state: Dict[str, Any]) -> Dict[str, Any]:
    """生成课程章节"""
    # 简化版：直接使用预定义的章节
    chapters = course_structure["章节"]
    return {"章节列表": chapters}
 
# 2. 学习对象生成节点
def learning_object_generator(state: Dict[str, Any]) -> Dict[str, Any]:
    """为每个章节生成学习对象"""
    chapters = state["章节列表"]
    learning_objects = []
 
    for chapter in chapters:
        chapter_name = chapter["章节名称"]
 
        # 创建基础学习对象
        chapter_objects = {
            "章节名称": chapter_name,
            "学习对象": [
                {"类型": "概念理解", "内容": f"本节介绍{chapter_name}的核心概念，帮助学习者建立基础认知。"},
                {"类型": "实践应用", "内容": f"通过实际案例演示{chapter_name}的应用方法，提升实战能力。"},
                {"类型": "知识评估", "内容": f"包含与{chapter_name}相关的自测题，帮助学习者检验学习效果。"}
            ]
        }
 
        learning_objects.append(chapter_objects)
 
    return {"章节学习对象": learning_objects}
 
# 3. 内容增强节点
def content_enhancer(state: Dict[str, Any]) -> Dict[str, Any]:
    """使用 Ollama 生成详细内容"""
    print("开始内容增强...")
 
    chapter_list = state["章节列表"]
    learning_objects_list = state.get("章节学习对象", [])
 
    # 创建映射以便后续查找
    learning_objects_map = {}
    for lo in learning_objects_list:
        chapter_name = lo.get("章节名称", "")
        if chapter_name:
            learning_objects_map[chapter_name] = lo.get("学习对象", [])
 
    # 存储增强后的章节内容
    enhanced_chapters = []
 
    # 处理每个章节
    for chapter in chapter_list:
        try:
            # 提取章节信息
            chapter_name = chapter["章节名称"]
            chapter_intro = chapter.get("简介", "无介绍")
 
            # 处理学习目标
            chapter_goals = chapter.get("学习目标", [])
            if isinstance(chapter_goals, list):
                chapter_goals = "\n".join([f"- {goal}" for goal in chapter_goals])
 
            # 创建增强章节对象
            enhanced_chapter = {
                "章节名称": chapter_name,
                "章节介绍": chapter_intro,
                "学习目标": chapter_goals,
                "学习对象": []
            }
 
            # 获取学习对象类型
            learning_objects = []
            if chapter_name in learning_objects_map:
                chapter_objects = learning_objects_map[chapter_name]
                learning_objects = [obj["类型"] for obj in chapter_objects]
 
            # 如果没有定义学习对象，使用默认列表
            if not learning_objects:
                learning_objects = ["概念理解", "实践应用", "知识评估"]
 
            # 为每个学习对象生成内容
            for obj_type in learning_objects:
                # 创建提示词
                prompt = prompt_templates.get(obj_type, "").format(
                    course_name=course_structure["课程名称"],
                    chapter_name=chapter_name,
                    chapter_intro=chapter_intro,
                    chapter_goals=chapter_goals
                )
 
                # 使用 Ollama 生成内容
                enhanced_content = generate_with_ollama(prompt)
 
                # 添加到章节对象
                enhanced_chapter["学习对象"].append({
                    "类型": obj_type,
                    "内容": enhanced_content
                })
 
            # 添加到增强章节列表
            enhanced_chapters.append(enhanced_chapter)
 
        except Exception as e:
            print(f"处理章节时发生错误: {e}")
 
    # 更新状态
    updated_state = state.copy()
    updated_state["章节增强内容"] = enhanced_chapters
 
    return updated_state
 
# 4. Markdown 写入节点
def markdown_writer(state: Dict[str, Any]) -> Dict[str, Any]:
    """保存章节与学习对象到本地 Markdown 文件"""
    course_name = course_structure["课程名称"]
    enhanced_chapters = state.get("章节增强内容", [])
 
    # 创建输出目录
    output_dir = f"course_langgraph"
    os.makedirs(output_dir, exist_ok=True)
 
    # 创建索引文件
    index_path = os.path.join(output_dir, "课程索引.md")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(f"# {course_name}\n\n")
        f.write("## 课程章节\n\n")
 
        for chapter in enhanced_chapters:
            chapter_name = chapter["章节名称"]
            chapter_intro = chapter["章节介绍"]
            chapter_goals = chapter["学习目标"]
 
            # 写入章节信息
            f.write(f"### {chapter_name}\n\n")
            f.write(f"{chapter_intro}\n\n")
            f.write("**学习目标**:\n")
            if isinstance(chapter_goals, list):
                for goal in chapter_goals:
                    f.write(f"- {goal}\n")
            else:
                f.write(f"{chapter_goals}\n")
 
            # 创建章节目录
            chapter_dir = os.path.join(output_dir, chapter_name)
            os.makedirs(chapter_dir, exist_ok=True)
 
            # 添加学习对象链接
            f.write("\n**学习内容**:\n")
 
            # 写入每个学习对象
            for obj in chapter["学习对象"]:
                obj_type = obj["类型"]
                obj_content = obj["内容"]
 
                # 写入文件链接
                obj_filename = f"{obj_type}.md"
                obj_path = os.path.join(chapter_dir, obj_filename) 
                f.write(f"- [{obj_type}](./{chapter_name}/{obj_filename})\n")
 
                # 创建学习对象文件
                with open(obj_path, "w", encoding="utf-8") as obj_file:
                    obj_file.write(f"# {chapter_name} - {obj_type}\n\n")
                    obj_file.write(obj_content)
 
            f.write("\n")
 
    return state
 
# 创建工作流图
builder = StateGraph(Dict[str, Any])
 
# 添加节点
builder.add_node("章节生成", chapter_generator)
builder.add_node("学习对象生成", learning_object_generator)
builder.add_node("内容增强", content_enhancer)
builder.add_node("Markdown写入", markdown_writer)
 
# 设置起点
builder.set_entry_point("章节生成")
 
# 添加边（连接节点）
builder.add_edge("章节生成", "学习对象生成")
builder.add_edge("学习对象生成", "内容增强")
builder.add_edge("内容增强", "Markdown写入")
 
# 编译图
workflow = builder.compile(debug=True)
 
# 执行工作流
if __name__ == "__main__":
    # 初始状态为空
    state = {}
 
    # 添加运行标识
    run_id = f"run_{int(time.time())}"
 
    print(f"开始执行课程生成流程，运行ID: {run_id}")
    print(f"可在 LangSmith 查看详细执行记录: https://smith.langchain.com/projects/课程创建-LangGraph")
 
    # 执行工作流
    result = workflow.invoke(state)
 
    print(f"执行完成! 课程内容已生成。")