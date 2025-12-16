import requests
import os
import tarfile
import json

# 配置
API_KEY = os.getenv("MINIMAX_API_KEY") 
# 如果 env 没加载到，尝试手动读取
if not API_KEY:
    try:
        with open('.env', 'r', encoding='utf-8') as f:
            for line in f:
                if 'MINIMAX_API_KEY' in line:
                    API_KEY = line.split('=')[1].strip()
                    break
    except:
        pass

if not API_KEY:
    print("Error: API Key not found")
    exit(1)

HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
FILE_ID = 345056797478986

def download_and_extract():
    print(f"1. 请求文件元数据 (File ID: {FILE_ID})...")
    retrieve_url = "https://api.minimaxi.com/v1/files/retrieve"
    
    try:
        # 获取下载链接
        res = requests.get(retrieve_url, headers=HEADERS, params={"file_id": FILE_ID})
        res_data = res.json()
        
        # 检查是否成功
        if res_data.get('base_resp', {}).get('status_code') != 0:
            print(f"API 错误: {res_data}")
            return

        download_url = res_data.get('file', {}).get('download_url')
        if not download_url:
            print("未在响应中找到 download_url")
            print(res_data)
            return
            
        print("2. 获取到真实下载链接，开始下载 .tar 包...")
        
        # 下载 tar 包
        tar_filename = f"{FILE_ID}.tar"
        with requests.get(download_url, stream=True) as r:
            r.raise_for_status()
            with open(tar_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print(f"   已保存临时文件: {tar_filename}")

        # 解压
        print("3. 正在提取 MP3 文件...")
        final_mp3_name = "制胜v8.mp3"
        mp3_extracted = False

        try:
            with tarfile.open(tar_filename, "r") as tar:
                # 遍历压缩包内容，只找 MP3
                for member in tar.getmembers():
                    if member.name.lower().endswith('.mp3'):
                        print(f"   找到音频: {member.name}")
                        tar.extract(member, path=".") # 解压到当前目录
                        
                        # 重命名
                        if os.path.exists(final_mp3_name):
                            os.remove(final_mp3_name)
                        os.rename(member.name, final_mp3_name)
                        print(f"   已重命名为: {final_mp3_name}")
                        mp3_extracted = True
                        break # 假设只要第一个 mp3
            
            if not mp3_extracted:
                print("   警告: 压缩包内未找到 .mp3 文件")

        except Exception as e:
            print(f"   解压/重命名出错: {e}")

        # 清理
        try:
            os.remove(tar_filename)
            print("   已删除临时 .tar 文件")
        except:
            pass

        if mp3_extracted:
            print(f"\n全部完成！您的文件: {final_mp3_name}")

    except Exception as e:
        print(f"发生异常: {e}")

if __name__ == "__main__":
    download_and_extract()
