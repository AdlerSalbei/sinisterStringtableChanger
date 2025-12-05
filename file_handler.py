import os
import shutil
from config import BACKUP_FOLDER, STRINGTABLE_FOLDER

LANGUAGE_MAP = {
    "en": "english",
    "de": "german_(germany)"
}

def get_suffix(value):
    try:
        num = int(float(value))
    except (ValueError, TypeError):
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
    """
    Reads an INI file, adds suffixes based on mapping, and writes to output.
    Uses utf-8-sig encoding for Star Citizen compatibility.
    """
    # Read with utf-8-sig to handle BOM if present
    with open(input_path, "r", encoding="utf-8-sig") as f:
        lines = f.readlines()
    
    modified_lines = []
    for line in lines:
        if "=" in line:
            key, value = line.strip().split("=", 1)
            key = key.strip()
            value = value.strip()
            
            # Check if key exists in mapping
            key_lower = key.lower()
            if key_lower in mapping:
                suffix = get_suffix(mapping[key_lower])
                # Only add suffix if it doesn't already exist
                if suffix and not value.endswith((" EHD", " HD", " ND", " ZD")):
                    value += suffix
                line = f"{key}={value}\n"
        modified_lines.append(line)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # CRITICAL: Write with utf-8-sig (adds BOM) for Star Citizen
    with open(output_path, "w", encoding="utf-8-sig") as f:
        f.writelines(modified_lines)

def move_global_ini_and_set_language(global_ini_path, star_citizen_path, lang_code):
    """
    Moves global.ini to the correct localization folder and updates user.cfg.
    """
    if lang_code not in LANGUAGE_MAP:
        raise ValueError(f"Unknown language code: {lang_code}")
    
    folder_name = LANGUAGE_MAP[lang_code]
    
    # Ensure we're working with the LIVE path
    live_path = star_citizen_path.rstrip("\\/")
    if os.path.basename(live_path).lower() != "live":
        live_path = os.path.join(live_path, "LIVE")
    
    # Target localization folder
    target_folder = os.path.join(live_path, "data", "Localization", folder_name)
    os.makedirs(target_folder, exist_ok=True)
    
    dest_ini_path = os.path.join(target_folder, "global.ini")
    
    # Copy with proper encoding (utf-8-sig)
    with open(global_ini_path, "r", encoding="utf-8-sig") as f:
        content = f.read()
    with open(dest_ini_path, "w", encoding="utf-8-sig") as f:
        f.write(content)
    
    print(f"global.ini copied to: {dest_ini_path}")
    
    # Update user.cfg
    user_cfg_path = os.path.join(live_path, "user.cfg")
    
    if not os.path.exists(user_cfg_path):
        with open(user_cfg_path, "w", encoding="utf-8-sig") as f:
            f.write(f"g_language = {folder_name}\n")
        print(f"user.cfg created with language: {folder_name}")
        return
    
    # Read existing user.cfg
    with open(user_cfg_path, "r", encoding="utf-8-sig") as f:
        lines = f.readlines()
    
    # Update or add g_language line
    found = False
    for i, line in enumerate(lines):
        if line.strip().lower().startswith("g_language"):
            lines[i] = f"g_language = {folder_name}\n"
            found = True
            break
    
    if not found:
        lines.append(f"g_language = {folder_name}\n")
    
    # Write back with utf-8-sig
    with open(user_cfg_path, "w", encoding="utf-8-sig") as f:
        f.writelines(lines)
    
    print(f"user.cfg updated with language: {folder_name}")
