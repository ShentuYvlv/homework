import os
import re

def list_txt_files(directory):
    return [f for f in os.listdir(directory) if f.endswith('.txt')]

def process_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 1. Remove all *
        content = content.replace('*', '')
        
        # 2. Remove content in () including parentheses
        # Handles both English () and Chinese （）
        # Using non-greedy matching .*? to handle multiple occurrences on one line
        # Using flags=re.DOTALL so it can match content spanning multiple lines if needed, 
        # though strictly speaking this can be risky if parens are unbalanced. 
        # I will remove re.DOTALL to be safer for typical text processing unless specified. 
        
        content = re.sub(r'\(.*\)', '', content)
        content = re.sub(r'（.*?）', '', content)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"已处理: {filepath}")
    except Exception as e:
        print(f"处理文件 {filepath} 时出错: {e}")

def main():
    current_dir = os.getcwd()
    txt_files = list_txt_files(current_dir)
    
    if not txt_files:
        print("当前目录下没有找到 .txt 文件。")
        return

    print("找到以下 .txt 文件:")
    for idx, filename in enumerate(txt_files, 1):
        print(f"{idx}. {filename}")

    selection = input("\n请输入要处理的文件编号（用空格分隔）: ")
    
    try:
        indices = [int(x) - 1 for x in selection.split()]
    except ValueError:
        print("输入无效，请输入用空格分隔的数字。")
        return

    selected_files = []
    for idx in indices:
        if 0 <= idx < len(txt_files):
            selected_files.append(txt_files[idx])
        else:
            print(f"警告: 编号 {idx + 1} 超出范围，已忽略。")

    if not selected_files:
        print("没有选择有效的文件。")
        return

    print("\n开始处理文件...")
    for filename in selected_files:
        process_file(os.path.join(current_dir, filename))
    print("处理完成。")

if __name__ == "__main__":
    main()
