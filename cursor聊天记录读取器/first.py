import sqlite3
import json
from datetime import datetime, timedelta
import os
from collections import defaultdict

def format_timestamp(timestamp):
    """格式化时间戳"""
    try:
        if len(str(timestamp)) > 10:
            timestamp = timestamp / 1000
        return datetime.fromtimestamp(timestamp)
    except:
        return None

def identify_role(obj):
    """识别消息角色"""
    # 根据内容特征判断是用户还是AI
    text = obj.get('text', '').strip()
    if not text:
        return 'unknown'
    
    # AI回复通常包含代码块或特定格式
    if '```' in text or 'Here' in text or 'Let' in text:
        return 'assistant'
    # 用户消息通常更简短或包含问题
    else:
        return 'user'

def read_cursor_chat():
    try:
        db_path = r"C:\Users\24657\AppData\Roaming\Cursor\User\globalStorage\stata.vscdb"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        conversations = []
        for table in ['ItemTable', 'cursorDiskKV']:
            cursor.execute(f"SELECT key, value FROM {table}")
            rows = cursor.fetchall()
            conversations.extend(rows)
        
        # 用于存储按主题分组的消息
        chat_topics = defaultdict(list)
        
        # 获取3天前的时间戳
        one_days_ago = datetime.now() - timedelta(days=3)

        def extract_messages(obj, parent_key='', timestamp=None, topic=None):
            if isinstance(obj, dict):
                # 获取当前对象的时间戳
                current_timestamp = None
                for time_key in ['timestamp', 'messageTime', 'time', 'createdAt', 'created_at']:
                    if time_key in obj:
                        current_timestamp = obj[time_key]
                        break
                
                # 如果没有找到时间戳，使用父级时间戳
                if current_timestamp is None:
                    current_timestamp = timestamp

                # 获取主题信息
                current_topic = obj.get('topic', 
                                      obj.get('title',
                                      obj.get('name', topic)))

                # 检查是否有messages数组
                if 'messages' in obj and isinstance(obj['messages'], list):
                    for msg in obj['messages']:
                        if isinstance(msg, dict):
                            try:
                                msg_time = msg.get('timestamp', current_timestamp)
                                formatted_time = format_timestamp(msg_time)
                                if formatted_time and formatted_time >= three_days_ago:
                                    role = msg.get('role', identify_role(msg))
                                    text = msg.get('text', '').strip()
                                    if text:
                                        message = {
                                            'time': formatted_time,
                                            'role': role,
                                            'content': text,
                                            'topic': current_topic or '未分类对话'
                                        }
                                        chat_topics[message['topic']].append(message)
                            except Exception as e:
                                continue

                # 处理常规的text字段
                if 'text' in obj and obj['text']:
                    formatted_time = format_timestamp(current_timestamp)
                    if formatted_time and formatted_time >= one_days_ago:
                        role = obj.get('role', identify_role(obj))
                        message = {
                            'time': formatted_time,
                            'role': role,
                            'content': str(obj['text']).strip(),
                            'topic': current_topic or '未分类对话'
                        }
                        chat_topics[message['topic']].append(message)

                # 递归处理其他字段
                for k, v in obj.items():
                    if isinstance(v, (dict, list)) and k != 'messages':  # 避免重复处理messages
                        try:
                            extract_messages(v, k, current_topic, current_timestamp)
                        except Exception:
                            pass
            
            elif isinstance(obj, list):
                for item in obj:
                    extract_messages(item, parent_key, timestamp, topic)

        # 提取消息
        for key, value in conversations:
            try:
                if isinstance(value, str):
                    data = json.loads(value)
                    extract_messages(data)
            except json.JSONDecodeError:
                continue
            except Exception as e:
                print(f"处理记录时出错: {str(e)}")
                continue

        # 创建输出目录和文件
        output_dir = "cursor_chat_exports"
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f'cursor_chat_history_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md')

        # TODO: 请实现以下功能
        # 1. 将chat_topics中的消息按时间排序
        # 2. 将排序后的消息写入到output_file文件中
        # 3. 文件格式要求：
        #    - 每个主题作为一级标题（# 主题名）
        #    - 每条消息包含时间和角色作为二级标题（## 时间 - 角色）
        #    - 消息内容直接写在二级标题下方
        #    - 每条消息之间用"---"分隔
        # 4. 注意处理可能出现的异常情况
        
        # 在此处编写代码
        # ...

    except sqlite3.Error as e:
        print(f"数据库错误: {e}")
    except Exception as e:
        print(f"程序执行出错: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    read_cursor_chat()

