import json
import os
import pathlib
import re
import shutil
from typing import TYPE_CHECKING

from ...extras.packages import is_gradio_available
from ..common import DEFAULT_DATA_DIR, load_dataset_info, DATA_CONFIG

if is_gradio_available():
    import gradio as gr

if TYPE_CHECKING:
    from gradio.components import Component

    from ..engine import Engine
    

def upload_json(file, dataset_name):
    target_dir = DEFAULT_DATA_DIR

    try:
        if not dataset_name:
            return "请指定数据集的名字。"

        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', dataset_name):
            return "数据集名称只能包含英文、数字、下划线，并且不能以数字开头。"
        
        if not is_valid_name(dataset_name):
            return "数据集名称已存在。"
        
        is_valid_dataset, msg = is_valid_json(file.name)
        if not is_valid_dataset:
            return msg

        target_path = os.path.join(target_dir, dataset_name+".json")
        shutil.move(file.name, target_path)
        update_dataset_info(DEFAULT_DATA_DIR)
        return f"文件已成功上传到 {target_path}"
    except Exception as e:
        return f"文件上传失败: {str(e)}"
    

def is_valid_name(name: str) -> bool:
    dataset_info = load_dataset_info(DEFAULT_DATA_DIR)
    datasets = [k for k, v in dataset_info.items() if v.get("ranking", False) == False] # not paired dataset
    return name not in datasets


def is_valid_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if not isinstance(data, list):
            return False, "JSON 文件内容必须是一个列表。"

        for element in data:
            if not isinstance(element, dict):
                return False, "列表中的每个元素必须是一个字典。"
            if not all(key in element for key in ["instruction", "output"]):
                return False, "每个字典必须包含 'instruction' 和 'output' 字段。"

        return True, "JSON 文件内容验证通过。"
    except Exception as e:
        return False, f"JSON 文件内容验证失败: {str(e)}"
    
    
def update_dataset_info(dataset_dir, dataset_name, dataset_file_path):
    dataset_info = load_dataset_info(dataset_dir=dataset_dir)
    
    dataset_info[dataset_name] = {
        "file_name": pathlib.Path(dataset_file_path).name,
    }
    
    with open(os.path.join(dataset_dir, DATA_CONFIG), 'w', encoding='utf-8') as f:
        json.dump(dataset_info, f, indent=4, ensure_ascii=False)

    
def create_upload_tab(engine: 'Engine'):
    with gr.Row():
        file = gr.File(label="文件", file_types=[".json"])
        dataset_name = gr.Textbox(label="数据集名称", placeholder="请输入数据集名称（仅支持英文字母、下划线、数字）")
        upload_btn = gr.Button("上传")
        output = gr.Textbox(readonly=True)
        
        upload_btn.click(upload_json, [file, dataset_name], outputs=output)