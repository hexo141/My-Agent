import mimetypes
from tqdm import tqdm
import requests
import os
from urllib.parse import urlparse


def download_file(url, save_path=None, chunk_size=8192):
    """
    使用tqdm显示下载进度条
    
    Args:
        url: 文件URL
        save_path: 保存路径
        chunk_size: 分块大小
    
    Returns:
        保存的文件路径
    """
    # 设置请求头
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    # 发送请求
    response = requests.get(url, headers=headers, stream=True)
    response.raise_for_status()
    
    # 获取文件大小
    total_size = int(response.headers.get('content-length', 0))
    
    # 获取文件名
    filename = get_filename_from_response(url, response)
    
    # 确定保存路径
    if save_path is None:
        save_path = filename
    elif os.path.isdir(save_path):
        save_path = os.path.join(save_path, filename)
    
    # 创建目录（如果不存在）
    os.makedirs(os.path.dirname(save_path) if os.path.dirname(save_path) else '.', exist_ok=True)
    
    # 使用tqdm显示进度条
    with open(save_path, 'wb') as file, tqdm(
        desc=filename,
        total=total_size,
        unit='B',
        unit_scale=True,
        unit_divisor=1024,
    ) as progress_bar:
        for chunk in response.iter_content(chunk_size=chunk_size):
            if chunk:
                file.write(chunk)
                progress_bar.update(len(chunk))
    
    print(f"✓ 下载完成: {save_path}")
    return save_path

def get_filename_from_response(url, response):
    """
    从响应头或URL中获取文件名
    """
    # 从Content-Disposition头获取文件名
    content_disposition = response.headers.get('Content-Disposition', '')
    if 'filename=' in content_disposition:
        filename = content_disposition.split('filename=')[1].strip('"\'')
        if filename:
            return filename
    
    # 从URL路径获取文件名
    parsed_url = urlparse(url)
    filename = os.path.basename(parsed_url.path)
    if filename and filename != '/':
        return filename
    
    # 根据Content-Type生成文件名
    content_type = response.headers.get('Content-Type', '').split(';')[0]
    extension = mimetypes.guess_extension(content_type) or '.bin'
    return f"downloaded_file{extension}"