from bs4 import BeautifulSoup
import requests
import re
from tqdm import tqdm
search_lists = lambda key, lists: [item for item in (lists if isinstance(lists[0], str) else [item for lst in lists for item in lst]) if key in str(item)]

import requests
import os
from urllib.parse import urlparse
import mimetypes

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
def get_stt_model_list():
    rp = requests.get("https://alphacephei.com/vosk/models")
    rp.encoding = "utf-8"

    # 创建BeautifulSoup对象
    soup = BeautifulSoup(rp.text, 'html.parser')

    # 查找包含模型信息的表格
    tables = soup.find_all('table', class_='table table-bordered')

    # 存储所有模型信息
    models_data = []

    # 处理第一个表格（主要模型表格）
    if len(tables) > 0:
        main_table = tables[0]
        rows = main_table.find_all('tr')
        
        current_category = ""
        
        for row in rows:
            # 检查是否是分类标题行
            header_cells = row.find_all('th')
            if header_cells and len(header_cells) >= 5:
                # 这是表头，跳过
                continue
                
            cells = row.find_all('td')
            
            if len(cells) == 5:
                # 这是正常的模型行
                model_name = cells[0].get_text(strip=True)
                model_link = cells[0].find('a')
                model_url = model_link['href'] if model_link else ""
                
                size = cells[1].get_text(strip=True)
                wer_speed = cells[2].get_text(strip=True)
                notes = cells[3].get_text(strip=True)
                license = cells[4].get_text(strip=True)
                
                models_data.append({
                    'category': current_category,
                    'name': model_name,
                    'url': model_url,
                    'size': size,
                    'wer_speed': wer_speed,
                    'notes': notes,
                    'license': license
                })
            elif len(cells) == 1:
                # 这可能是分类标题
                category_text = cells[0].get_text(strip=True)
                if category_text and not category_text.startswith(' '):
                    current_category = category_text

    # 处理第二个表格（标点模型表格）
    if len(tables) > 1:
        punctuation_table = tables[1]
        rows = punctuation_table.find_all('tr')
        
        current_category = ""
        
        for row in rows:
            cells = row.find_all('td')
            
            if len(cells) == 3:
                # 正常的标点模型行
                model_name = cells[0].get_text(strip=True)
                model_link = cells[0].find('a')
                model_url = model_link['href'] if model_link else ""
                
                size = cells[1].get_text(strip=True)
                license = cells[2].get_text(strip=True)
                
                models_data.append({
                    'category': f"Punctuation - {current_category}",
                    'name': model_name,
                    'url': model_url,
                    'size': size,
                    'wer_speed': "",
                    'notes': "Punctuation and case restoration model",
                    'license': license
                })
            elif len(cells) == 1:
                # 分类标题
                category_text = cells[0].get_text(strip=True)
                if category_text and not category_text.startswith(' '):
                    current_category = category_text

    # for model in models_data:
    #     if model['category'] != current_cat:
    #         current_cat = model['category']
    #         print(f"\n{current_cat}")
    #         print("-" * 60)
        
    #     print(f"模型名称: {model['name']}")
    #     if model['url']:
    #         print(f"下载链接: {model['url']}")
    #     print(f"大小: {model['size']}")
    #     if model['wer_speed']:
    #         print(f"词错率/速度: {model['wer_speed']}")
    #     print(f"说明: {model['notes']}")
    #     print(f"许可证: {model['license']}")
    #     print()

    # # 统计信息
    # categories = set([model['category'] for model in models_data if model['category']])
    # total_models = len(models_data)

    # print("=" * 80)
    # print(f"总计: {total_models} 个模型")
    # print(f"分类数量: {len(categories)}")
    # print("分类列表:", ", ".join(categories))
    return models_data
models_data = get_stt_model_list()
model_name_list = []
for model in models_data:
    if len(model["url"]) == 0:
        continue
    # print(f"[{num}]: {model['name']}")
    model_name_list.append(model['name'])
print("请输入你想使用的语音输入语(如: cn, en): ")
s_key = input("Please enter the voice input language you want to use (e.g., cn, en) :")
s_list = search_lists(s_key, model_name_list)
num = 0
for i in s_list:
    print(f"[{num}]: {i}")
    num += 1
s_l = s_list[int(input(f"Please select a model (0-{num - 1})："))]
for model in models_data:
    if len(model["url"]) == 0:
        continue
    # print(f"[{num}]: {model['name']}")
    if model["name"] == s_l:
        print(f"[url]: {model["url"]}")
        download_file(model["url"], "Model/stt/")
        break