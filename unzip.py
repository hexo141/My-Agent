import zipfile
import os
import pathlib

def unzip(zip_file_path, extract_to_path):
    """
    解压包含子文件夹的ZIP文件
    
    Args:
        zip_file_path: ZIP文件路径
        extract_to_path: 解压目标路径
    """
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        file_list = zip_ref.namelist()
        print(f"开始解压 {len(file_list)} 个项目到 {extract_to_path}...")
        
        for i, file in enumerate(file_list, 1):
            # 构建完整的目标路径
            target_path = pathlib.Path(extract_to_path) / file
            
            if file.endswith('/'):  # 目录条目
                os.makedirs(target_path, exist_ok=True)
                print(f"[{i}/{len(file_list)}] mkdir: {file}")
            else:  # 文件条目
                # 确保父目录存在
                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                # 解压到指定目录
                zip_ref.extract(file, extract_to_path)
                print(f"[{i}/{len(file_list)}] unzip: {file}")
        
        print("[✓] Success！")
        return True
