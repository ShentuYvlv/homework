from modelscope import snapshot_download

# 指定下载目录为当前目录下的 models 文件夹
model_dir = snapshot_download('Xorbits/bge-m3', cache_dir='./models')

print(f"模型已下载到: {model_dir}")