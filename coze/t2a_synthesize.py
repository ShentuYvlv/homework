import os
import time
import json
import requests
import tarfile
import shutil

# Simple .env parser
def load_env():
    env_path = '.env'
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

load_env()

API_KEY = os.getenv("MINIMAX_API_KEY")
BASE_URL = "https://api.minimaxi.com"

if not API_KEY:
    print("错误: 未在 .env 文件中找到 MINIMAX_API_KEY")
    exit(1)

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def list_txt_files():
    files = [f for f in os.listdir('.') if f.endswith('.txt')]
    return files

def create_task(text):
    url = f"{BASE_URL}/v1/t2a_async_v2"
    payload = {
        "model": "speech-2.6-hd",
        "text": text,
        "voice_setting": {
            "voice_id": "ttv-voice-2025071421385025-SZcZBSgw",
            "speed": 1.05,
            "vol": 1,
            "pitch": 0
        },
        "audio_setting": {
            "format": "mp3",
            "audio_sample_rate": 32000,
            "bitrate": 128000
        }
    }
    
    try:
        response = requests.post(url, headers=HEADERS, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"创建任务失败: {e}")
        if response is not None:
             print(f"响应内容: {response.text}")
        return None

def query_task(task_id):
    url = f"{BASE_URL}/v1/query/t2a_async_query_v2"
    params = {"task_id": task_id}
    
    try:
        response = requests.get(url, headers=HEADERS, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"查询任务失败: {e}")
        return None

def download_and_extract(file_id, output_filename):
    print(f"开始下载流程 (File ID: {file_id})...")
    retrieve_url = f"{BASE_URL}/v1/files/retrieve"
    
    try:
        # 1. 获取下载链接
        res = requests.get(retrieve_url, headers=HEADERS, params={"file_id": file_id})
        res_data = res.json()
        
        if res_data.get('base_resp', {}).get('status_code') != 0:
            print(f"下载失败 (API Error): {res_data}")
            return False

        download_url = res_data.get('file', {}).get('download_url')
        if not download_url:
            print("下载失败: 未找到 download_url")
            return False
            
        print("正在下载压缩包...")
        
        # 2. 下载 tar 包
        tar_filename = f"{file_id}.tar"
        with requests.get(download_url, stream=True) as r:
            r.raise_for_status()
            with open(tar_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        
        # 3. 提取 MP3
        print("正在解压并提取音频...")
        mp3_extracted = False
        
        try:
            with tarfile.open(tar_filename, "r") as tar:
                # 寻找第一个 mp3 文件
                for member in tar.getmembers():
                    if member.name.lower().endswith('.mp3'):
                        # 直接提取文件流写入目标文件，避免创建文件夹结构
                        f_in = tar.extractfile(member)
                        with open(output_filename, 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)
                        print(f"提取成功: {output_filename}")
                        mp3_extracted = True
                        break
            
            if not mp3_extracted:
                print("错误: 压缩包内未找到 .mp3 文件")
        except Exception as e:
            print(f"解压失败: {e}")
            return False
        finally:
            # 清理临时 tar 文件
            if os.path.exists(tar_filename):
                os.remove(tar_filename)

        return mp3_extracted

    except Exception as e:
        print(f"下载流程异常: {e}")
        return False

def main():
    txt_files = list_txt_files()
    if not txt_files:
        print("当前目录下没有 .txt 文件")
        return

    print("找到以下文件:")
    for i, f in enumerate(txt_files):
        print(f"{i+1}. {f}")

    choice = input("\n请选择要合成的文件编号 (例如 1): ")
    try:
        index = int(choice) - 1
        if index < 0 or index >= len(txt_files):
            print("无效的选择")
            return
        filename = txt_files[index]
    except ValueError:
        print("输入无效")
        return

    print(f"\n读取文件: {filename}")
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            text = f.read()
    except Exception as e:
        print(f"读取文件失败: {e}")
        return

    if not text.strip():
        print("文件内容为空")
        return

    print(f"文本长度: {len(text)} 字符")
    
    confirm = input("确认开始合成? (y/n): ")
    if confirm.lower() != 'y':
        print("已取消")
        return

    print("正在提交任务...")
    result = create_task(text)
    
    if not result or result.get('base_resp', {}).get('status_code') != 0:
        print("任务提交失败")
        if result:
            print(result)
        return

    task_id = result['task_id']
    print(f"任务提交成功! Task ID: {task_id}")
    
    print("正在等待生成 (MiniMax 异步生成可能需要几分钟)...")
    start_time = time.time()
    
    while True:
        status_res = query_task(task_id)
        if not status_res:
            time.sleep(5)
            continue
            
        status = status_res.get('status')
        
        elapsed = int(time.time() - start_time)
        print(f"\r状态: {status} [已耗时: {elapsed}s]", end="")
        
        # 修正: 使用 lower() 忽略大小写
        if status and status.lower() == 'success':
            print("\n生成成功! 开始处理下载...")
            file_id = status_res.get('file_id')
            if file_id:
                output_file = os.path.splitext(filename)[0] + ".mp3"
                if download_and_extract(file_id, output_file):
                    print(f"\n=========\n全部完成! 音频文件已保存为: {output_file}\n=========")
                else:
                    print("\n下载或解压过程出错")
            else:
                print("API 未返回 file_id")
            break
        elif status and status.lower() == 'failed':
            print("\n生成失败")
            print(status_res)
            break
        elif status and status.lower() == 'expired':
            print("\n任务已过期")
            break
            
        time.sleep(3)

if __name__ == "__main__":
    main()