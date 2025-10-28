import os
import shutil

from config import BACKUP_FOLDER, STRINGTABLE_FOLDER

def get_suffix(value):
    try:
        num = int(value)
    except ValueError:
        return ""
    return {50: " EHD", 25: " HD", 1: " ND", 0: " ZD"}.get(num, "")

def backup_existing_file(file_path):
    if not os.path.exists(file_path):
        return None
    os.makedirs(BACKUP_FOLDER, exist_ok=True)
    backup_name = f"global_backup_{len(os.listdir(BACKUP_FOLDER)) + 1}.ini"
    backup_path = os.path.join(BACKUP_FOLDER, backup_name)
    shutil.copy2(file_path, backup_path)
    return backup_path

def process_ini_file(mapping, input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    modified_lines = []
    for line in lines:
        if "=" in line:
            key, value = line.strip().split("=", 1)
            key = key.strip()
            value = value.strip()
            if key in mapping:
                suffix = get_suffix(mapping[key])
                if suffix and not value.endswith((" EHD"," HD"," ND"," ZD")):
                    value += suffix
                line = f"{key}={value}\n"
        modified_lines.append(line)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.writelines(modified_lines)
