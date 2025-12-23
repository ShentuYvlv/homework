import os
from markitdown import MarkItDown

# --- 配置 ---
SOURCE_DIR = "."       # 当前目录
OUTPUT_DIR = "coze"    # 输出目录名称
# 支持的格式
SUPPORTED_EXTS = {'.docx', '.doc', '.pdf', '.pptx', '.txt'}

def get_unique_output_path(output_dir, file_name_no_ext):
    """
    解决文件名冲突：
    如果 output.md 已存在，则返回 output_1.md, output_2.md，以此类推。
    """
    target_name = f"{file_name_no_ext}.md"
    target_path = os.path.join(output_dir, target_name)
    
    counter = 1
    while os.path.exists(target_path):
        target_name = f"{file_name_no_ext}_{counter}.md"
        target_path = os.path.join(output_dir, target_name)
        counter += 1
    
    return target_path, target_name

def main():
    # 1. 准备环境
    md = MarkItDown()
    
    output_root = os.path.join(SOURCE_DIR, OUTPUT_DIR)
    if not os.path.exists(output_root):
        os.makedirs(output_root)
    
    print(f"[*] 输出目录: {os.path.abspath(output_root)}")
    print(f"[*] 开始全量扁平化转换...")
    print("-" * 50)

    success_count = 0
    fail_count = 0

    # 2. 遍历所有目录
    for root, dirs, files in os.walk(SOURCE_DIR):
        # 跳过输出目录自己
        if OUTPUT_DIR in root.split(os.sep):
            continue

        for file in files:
            ext = os.path.splitext(file)[1].lower()
            
            if ext in SUPPORTED_EXTS:
                src_path = os.path.join(root, file)
                file_name_no_ext = os.path.splitext(file)[0]
                
                # 获取不重复的输出路径
                output_path, final_name = get_unique_output_path(output_root, file_name_no_ext)
                
                print(f"处理: {file} -> {final_name}", end="", flush=True)

                try:
                    # 转换
                    result = md.convert(src_path)
                    
                    if result.text_content:
                        # 建议在Markdown开头加上原始文件路径，方便做Agent时溯源
                        source_info = f"> 来源文件: {os.path.join(root, file)}\n\n"
                        
                        with open(output_path, "w", encoding="utf-8") as f:
                            f.write(source_info + result.text_content)
                            
                        print(" [成功]")
                        success_count += 1
                    else:
                        print(" [跳过] (内容为空)")

                except Exception as e:
                    print(f" [失败]")
                    print(f"    └─ 错误: {e}")
                    fail_count += 1

    print("-" * 50)
    print(f"[*] 全部完成。")
    print(f"    成功: {success_count}")
    print(f"    失败: {fail_count}")
    print(f"    所有Markdown文件均已存放于: {OUTPUT_DIR} 目录下")

if __name__ == "__main__":
    main()