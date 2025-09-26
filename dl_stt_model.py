from bs4 import BeautifulSoup
import requests
import os
search_lists = lambda key, lists: [item for item in (lists if isinstance(lists[0], str) else [item for lst in lists for item in lst]) if key in str(item)]
import pathlib
import requests
import os
import dl_file
import unzip
import tomlkit

with open("config.toml", "r", encoding="utf-8") as f:
    toml_config = tomlkit.load(f)

stt_model_path = pathlib.Path("Model") / "stt" 
if not os.path.exists(stt_model_path):
    stt_model_path.mkdir(parents=True,exist_ok=True)


def get_stt_model_list():
    print("[-] Getting STT model list...")
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
        save_path = dl_file.download_file(model["url"], "Model/stt/")
        if os.path.exists(save_path):
            extract_to = pathlib.Path("Model") / "stt"
            if unzip.unzip(save_path, extract_to):
                if input("Do you want to delete the zip file? (y/n): ").lower() == 'y':
                    os.remove(save_path)
                print("是否设置为默认stt模型？(y/n): ")
                if input("Set as the default STT model?(y/n): ").lower() == 'y':
                    toml_config["record"]["DEFAULT_SPT_MODEL_PATH"] = str(extract_to / os.path.splitext(os.path.basename(save_path))[0])
                    
                    with open("config.toml", "w", encoding="utf-8") as f:
                        tomlkit.dump(toml_config, f)
                    
                    print(f"已将 {extract_to / os.path.splitext(os.path.basename(save_path))[0]} 设为默认STT模型。")
                    print("[-] Done.")
        break