import os
import shutil
import subprocess
import tempfile
import time
from markitdown import MarkItDown

# 尝试导入 win32com，用于处理 .doc
try:
    import win32com.client as win32
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False

SOFFICE_BIN = shutil.which("soffice") or shutil.which("libreoffice")
HAS_SOFFICE = SOFFICE_BIN is not None

if not HAS_WIN32 and not HAS_SOFFICE:
    print("[!] 未检测到 .doc 转换器。Windows 请安装 pywin32；macOS/Linux 请安装 LibreOffice 后重试。")

# --- 配置 ---
SOURCE_DIR = "."       # 当前目录
OUTPUT_DIR = "coze"    # 输出目录名称
# 支持的格式
SUPPORTED_EXTS = {'.doc'} # 注意：.doc 单独处理

def get_unique_output_path(output_dir, file_name_no_ext):
    """防止文件名冲突"""
    target_name = f"{file_name_no_ext}.md"
    target_path = os.path.join(output_dir, target_name)
    counter = 1
    while os.path.exists(target_path):
        target_name = f"{file_name_no_ext}_{counter}.md"
        target_path = os.path.join(output_dir, target_name)
        counter += 1
    return target_path, target_name

def doc_to_docx(doc_path):
    """
    使用 Word COM 接口将 .doc 转为 .docx 临时文件
    返回临时文件的绝对路径，如果失败返回 None
    """
    if not HAS_WIN32 and not HAS_SOFFICE:
        return None

    if HAS_SOFFICE and not HAS_WIN32:
        abs_doc_path = os.path.abspath(doc_path)
        temp_dir = tempfile.mkdtemp(prefix="doc_convert_")
        try:
            cmd = [
                SOFFICE_BIN,
                "--headless",
                "--convert-to",
                "docx",
                "--outdir",
                temp_dir,
                abs_doc_path,
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            output_name = os.path.splitext(os.path.basename(abs_doc_path))[0] + ".docx"
            temp_docx_path = os.path.join(temp_dir, output_name)

            if result.returncode != 0 or not os.path.exists(temp_docx_path):
                stderr = (result.stderr or "").strip()
                print(f"\n    [LibreOffice转换错误] {stderr or '未知错误'}")
                return None

            return temp_docx_path
        except Exception as e:
            print(f"\n    [LibreOffice转换错误] {e}")
            return None

    word = None
    try:
        # 必须使用绝对路径
        abs_doc_path = os.path.abspath(doc_path)
        temp_docx_path = abs_doc_path + "x" # 简单地加个x后缀作为临时文件名
        
        # 启动 Word (后台运行)
        word = win32.gencache.EnsureDispatch('Word.Application')
        word.Visible = False
        
        # 打开 .doc
        doc = word.Documents.Open(abs_doc_path)
        # 另存为 .docx (16 代表 wdFormatXMLDocument)
        doc.SaveAs2(temp_docx_path, FileFormat=16)
        doc.Close()
        
        return temp_docx_path
    except Exception as e:
        print(f"\n    [Word转换错误] {e}")
        return None
    finally:
        # 这里不退出 word app，因为频繁开关太慢。
        # 脚本结束后系统会自动清理，或者手动关闭进程。
        pass

def main():
    md = MarkItDown()
    
    output_root = os.path.join(SOURCE_DIR, OUTPUT_DIR)
    if not os.path.exists(output_root):
        os.makedirs(output_root)
    
    print(f"[*] 输出目录: {os.path.abspath(output_root)}")
    print(f"[*] 开始处理 (含 .doc 兼容模式)...")
    print("-" * 50)

    success_count = 0
    fail_count = 0

    for root, dirs, files in os.walk(SOURCE_DIR):
        if OUTPUT_DIR in root.split(os.sep):
            continue

        for file in files:
            ext = os.path.splitext(file)[1].lower()
            src_path = os.path.join(root, file)
            file_name_no_ext = os.path.splitext(file)[0]
            
            # --- 分支 1: 处理旧版 .doc ---
            if ext == '.doc':
                print(f"处理: {file} (旧版格式) ...", end="", flush=True)
                
                # 1. 转为 docx
                temp_docx = doc_to_docx(src_path)
                
                if temp_docx and os.path.exists(temp_docx):
                    try:
                        # 2. 转换 temp docx -> md
                        result = md.convert(temp_docx)
                        output_path, final_name = get_unique_output_path(output_root, file_name_no_ext)
                        
                        source_info = f"> 来源文件: {src_path} (由 .doc 转换)\n\n"
                        with open(output_path, "w", encoding="utf-8") as f:
                            f.write(source_info + result.text_content)
                        
                        print(f" -> {final_name} [成功]")
                        success_count += 1
                        
                        # 3. 删除临时文件
                        os.remove(temp_docx)
                        temp_dir = os.path.dirname(temp_docx)
                        if os.path.basename(temp_dir).startswith("doc_convert_"):
                            try:
                                os.rmdir(temp_dir)
                            except OSError:
                                pass
                        
                    except Exception as e:
                        print(f" [失败] {e}")
                        fail_count += 1
                else:
                    print(" [跳过] (.doc 转 .docx 失败)")
                    fail_count += 1

            # --- 分支 2: 处理常规支持格式 ---
            elif ext in SUPPORTED_EXTS:
                output_path, final_name = get_unique_output_path(output_root, file_name_no_ext)
                print(f"处理: {file} -> {final_name}", end="", flush=True)

                try:
                    result = md.convert(src_path)
                    if result.text_content:
                        source_info = f"> 来源文件: {src_path}\n\n"
                        with open(output_path, "w", encoding="utf-8") as f:
                            f.write(source_info + result.text_content)
                        print(" [成功]")
                        success_count += 1
                    else:
                        print(" [跳过] (内容为空)")
                except Exception as e:
                    print(f" [失败] {e}")
                    fail_count += 1

    print("-" * 50)
    print(f"[*] 处理完成。成功: {success_count}, 失败: {fail_count}")

    # 尝试关闭 Word 进程 (如果被开启过)
    try:
        if HAS_WIN32:
            w = win32.Dispatch("Word.Application")
            w.Quit()
    except:
        pass

if __name__ == "__main__":
    main()
