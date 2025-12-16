import sqlite3
import json
from datetime import datetime
import os
import glob
from collections import defaultdict

def format_timestamp(timestamp):
    """尝试解析各种格式的时间戳"""
    if not timestamp: return None
    try:
        ts = float(timestamp)
        # 毫秒转秒
        if ts > 10000000000: ts = ts / 1000
        # 简单的合法性校验 (2020年-2030年)
        if 1577836800 <= ts <= 1893456000:
            return datetime.fromtimestamp(ts)
    except:
        pass
    return None

def is_ai_content(text):
    """通过内容特征判断是否为AI"""
    if not text: return False
    # AI 经常回复代码块，或者很长的解释
    if "```" in text: return True
    if len(text) > 200 and ("Here is" in text or "To fix this" in text or "建议" in text): return True
    return False

def extract_chats_from_db(db_path, chat_topics, seen_hashes):
    """从单个数据库文件中提取对话"""
    conn = None
    count = 0
    try:
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        cursor = conn.cursor()
        
        # 获取所有表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        raw_data = []
        for table in ['cursorDiskKV', 'ItemTable']:
            if table in tables:
                try:
                    cursor.execute(f"SELECT value FROM {table}")
                    raw_data.extend(cursor.fetchall())
                except: pass

        # --- 核心递归逻辑 ---
        def recursive_search(obj, topic="未命名会话", parent_time=None):
            nonlocal count
            
            # 1. 如果是列表，遍历元素
            if isinstance(obj, list):
                for item in obj:
                    recursive_search(item, topic, parent_time)
                return

            # 2. 如果是字典，进行深度解析
            if isinstance(obj, dict):
                # A. 尝试获取时间 (如果没有，就继承父级时间)
                current_time = parent_time
                for k in ['timestamp', 'createdAt', 'time', 'date', 'lastModified']:
                    if k in obj:
                        t = format_timestamp(obj[k])
                        if t: current_time = t; break
                
                # B. 尝试获取主题
                if 'name' in obj and isinstance(obj['name'], str): topic = obj['name']
                if 'header' in obj and isinstance(obj['header'], str): topic = obj['header']

                # C. 提取内容 (这是最关键的修改)
                content = None
                role = 'unknown'

                # --- 适配 Cursor 多种数据结构 ---

                # 情况 1: Composer 的 Bubbles 结构 (常见于 Ctrl+I)
                if 'bubbles' in obj and isinstance(obj['bubbles'], list):
                    # 这是一个容器，递归进去
                    recursive_search(obj['bubbles'], topic, current_time)
                    return

                # 情况 2: 标准消息结构 (含 text/markdown)
                # 很多 AI 回复存在 'markdown' 字段里，而不是 'text'
                if 'markdown' in obj and isinstance(obj['markdown'], str):
                    content = obj['markdown']
                    role = 'assistant' # markdown 通常是 AI
                elif 'text' in obj and isinstance(obj['text'], str):
                    content = obj['text']
                    # 尝试判断角色
                    if obj.get('type') == 1 or obj.get('role') == 'user': role = 'user'
                    elif obj.get('type') == 2 or obj.get('role') == 'assistant': role = 'assistant'
                    elif is_ai_content(content): role = 'assistant'
                    else: role = 'user' # 默认归为 User

                # 情况 3: 只有 code 字段
                elif 'code' in obj and isinstance(obj['code'], str):
                    content = f"```\n{obj['code']}\n```"
                    role = 'assistant' if is_ai_content(content) else 'user'

                # --- 保存提取结果 ---
                if content and isinstance(content, str) and len(content.strip()) > 1:
                    # 过滤掉一些 JSON 垃圾数据
                    if not content.strip().startswith('{'):
                        sig = f"{content[:50]}" # 弱去重
                        if sig not in seen_hashes:
                            seen_hashes.add(sig)
                            
                            chat_topics[topic].append({
                                'time': current_time,
                                'role': role,
                                'content': content,
                                'source_db': os.path.basename(os.path.dirname(db_path))
                            })
                            count += 1

                # D. 继续递归子字典
                for k, v in obj.items():
                    if isinstance(v, (dict, list)):
                        recursive_search(v, topic, current_time)

        # 处理每一条原始数据
        for row in raw_data:
            val = row[0]
            try:
                if isinstance(val, bytes): val = val.decode('utf-8', errors='ignore')
                if val.startswith('{') or val.startswith('['):
                    json_obj = json.loads(val)
                    recursive_search(json_obj)
            except:
                continue
                    
    except Exception:
        pass
    finally:
        if conn: conn.close()
    return count

def main():
    # 1. 扫描路径
    appdata = os.getenv('APPDATA')
    cursor_user_dir = os.path.join(appdata, "Cursor", "User")
    
    paths = []
    # 包含 Global
    g_db = os.path.join(cursor_user_dir, "globalStorage", "state.vscdb")
    if os.path.exists(g_db): paths.append(g_db)
    # 包含 Workspaces
    ws_dir = os.path.join(cursor_user_dir, "workspaceStorage")
    if os.path.exists(ws_dir):
        paths.extend(glob.glob(os.path.join(ws_dir, "*", "state.vscdb")))

    print(f"开始扫描 {len(paths)} 个数据库...")
    
    chat_topics = defaultdict(list)
    seen_hashes = set()
    total = 0

    for i, db in enumerate(paths):
        print(f"[{i+1}/{len(paths)}] 扫描中: {os.path.basename(os.path.dirname(db))} ...")
        total += extract_chats_from_db(db, chat_topics, seen_hashes)

    # 2. 导出
    output_dir = "cursor_chat_exports"
    os.makedirs(output_dir, exist_ok=True)
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f'cursor_chat_history_{timestamp_str}.md')

    print(f"\n扫描完成! 共找到 {total} 条消息。")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Cursor Chat History Export (Fixed AI)\n")
        f.write(f"导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        # 排序
        sorted_topics = sorted(chat_topics.items(), 
                             key=lambda x: max((m['time'] for m in x[1] if m['time']), default=datetime.min), 
                             reverse=True)

        for topic, messages in sorted_topics:
            if not messages: continue
            
            f.write(f"# {topic}\n\n")
            
            # 按时间排序 (把 None 的放最后)
            messages.sort(key=lambda x: x['time'] if x['time'] else datetime.max)
            
            for msg in messages:
                t_str = msg['time'].strftime('%Y-%m-%d %H:%M:%S') if msg['time'] else "未知时间"
                
                # 图标逻辑
                role = msg['role']
                if role == 'assistant':
                    icon, name = "🤖", "AI"
                else:
                    icon, name = "👤", "User"
                
                f.write(f"## {icon} {t_str} - {name}\n\n")
                f.write(f"{msg['content']}\n\n")
                f.write("---\n\n")

    print(f"导出成功: {os.path.abspath(output_file)}")

if __name__ == "__main__":
    main()