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
    import threading
    # 设置请求头
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    # 预检 Range 支持
    head = requests.head(url, headers=headers)
    accept_ranges = head.headers.get('Accept-Ranges', '').lower()
    total_size = int(head.headers.get('content-length', 0))

    # 获取文件名
    filename = get_filename_from_response(url, head)

    # 确定保存路径
    if save_path is None:
        save_path = filename
    elif os.path.isdir(save_path):
        save_path = os.path.join(save_path, filename)

    # 创建目录（如果不存在）
    os.makedirs(os.path.dirname(save_path) if os.path.dirname(save_path) else '.', exist_ok=True)

    def single_thread():
        response = requests.get(url, headers=headers, stream=True)
        response.raise_for_status()
        with open(save_path, 'wb') as file, tqdm(
            desc=f"{filename} (单线程下载)",
            total=total_size,
            unit='B',
            unit_scale=True,
            unit_divisor=1024,
            bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]'
        ) as progress_bar:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    file.write(chunk)
                    progress_bar.update(len(chunk))
        print(f"✓ 下载完成: {save_path}")
        return save_path

    def multi_thread():
        num_threads = min(8, max(2, os.cpu_count() or 4))
        part_size = total_size // num_threads
        results = [b''] * num_threads
        locks = [threading.Lock() for _ in range(num_threads)]
        downloaded_sizes = [0] * num_threads

        # 创建总进度条
        progress_bar = tqdm(
            desc=f"{filename} (多线程下载)",
            total=total_size,
            unit='B',
            unit_scale=True,
            unit_divisor=1024,
            bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]'
        )

        def download_part(i, start, end):
            range_header = {'Range': f'bytes={start}-{end}', **headers}
            r = requests.get(url, headers=range_header, stream=True)
            r.raise_for_status()
            data = b''
            for chunk in r.iter_content(chunk_size=chunk_size):
                if chunk:
                    data += chunk
                    with locks[i]:
                        downloaded_sizes[i] += len(chunk)
                        # 更新总进度条
                        progress_bar.update(len(chunk))
            results[i] = data

        threads = []
        for i in range(num_threads):
            start = i * part_size
            end = total_size - 1 if i == num_threads - 1 else (start + part_size - 1)
            t = threading.Thread(target=download_part, args=(i, start, end))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
        with open(save_path, 'wb') as f:
            for part in results:
                f.write(part)
        progress_bar.close()
        print(f"✓ 多线程下载完成: {save_path}")
        return save_path

    # 优先尝试多线程
    if accept_ranges == 'bytes' and total_size > 0:
        try:
            return multi_thread()
        except Exception as e:
            print(f"[多线程下载失败，自动回退单线程] {e}")
            return single_thread()
    else:
        return single_thread()

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