import os
import shutil

from config import BACKUP_FOLDER, STRINGTABLE_FOLDER  # where your generated global.ini lives

# Mapping of language code to folder name and CVAR line
LANGUAGE_MAP = {
    "zh_cn": "chinese_(simplified)",
    "zh_tw": "chinese_(traditional)",
    "en": "english",
    "fr": "french_(france)",
    "de": "german_(germany)",
    "it": "italian_(italy)",
    "ja": "japanese_(japan)",
    "ko": "korean_(south_korea)",
    "pl": "polish_(poland)",
    "pt_br": "portuguese_(brazil)",
    "es_latam": "spanish_(latin_america)",
    "es_es": "spanish_(spain)",
}

def get_suffix(value):
    try:
        num = int(float(value.strip()))
    except (ValueError, AttributeError):
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
    with open(input_path, "r", encoding="utf-8-sig") as f:
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
    with open(output_path, "w", encoding="utf-8-sig") as f:
        f.writelines(modified_lines)

def move_global_ini_and_set_language(global_ini_path, star_citizen_path, lang_code):
    """
    Moves global.ini to the correct folder and updates user.cfg,
    replacing the g_language line if it exists.
    """
    if lang_code not in LANGUAGE_MAP:
        raise ValueError(f"Unknown language code: {lang_code}")
    
    folder_name = LANGUAGE_MAP[lang_code]
    
    live_path = star_citizen_path.rstrip("\\/")
    if os.path.basename(live_path).lower() != "live":
        live_path = os.path.join(live_path, "LIVE")
    
    target_folder = os.path.join(live_path, "data", "Localization", folder_name)
    os.makedirs(target_folder, exist_ok=True)
    
    dest_ini_path = os.path.join(target_folder, "global.ini")
    
    # ÄNDERN: Datei mit utf-8-sig lesen und schreiben
    with open(global_ini_path, "r", encoding="utf-8-sig") as f:
        content = f.read()
    with open(dest_ini_path, "w", encoding="utf-8-sig") as f:
        f.write(content)
    
    print(f"global.ini copied to: {dest_ini_path}")
    
    user_cfg_path = os.path.join(live_path, "user.cfg")
    
    if not os.path.exists(user_cfg_path):
        # ÄNDERN: utf-8-sig auch für user.cfg
        with open(user_cfg_path, "w", encoding="utf-8-sig") as f:
            f.write(f"g_language = {folder_name}\n")
        print(f"user.cfg created with language: {folder_name}")
        return
    
    # ÄNDERN: utf-8-sig beim Lesen
    with open(user_cfg_path, "r", encoding="utf-8-sig") as f:
        lines = f.readlines()
    
    found = False
    for i, line in enumerate(lines):
        if line.strip().lower().startswith("g_language"):
            lines[i] = f"g_language = {folder_name}\n"
            found = True
            break
    
    if not found:
        lines.append(f"g_language = {folder_name}\n")
    
    # ÄNDERN: utf-8-sig beim Schreiben
    with open(user_cfg_path, "w", encoding="utf-8-sig") as f:
        f.writelines(lines)
    
    print(f"user.cfg updated with language: {folder_name}")
