import os
from tkinter import filedialog

def find_star_citizen_install_path():
    possible_paths = [
        r"C:\Program Files\Roberts Space Industries\StarCitizen\LIVE",
        r"C:\Program Files (x86)\Roberts Space Industries\StarCitizen\LIVE",
        os.path.expandvars(r"%ProgramFiles%\Roberts Space Industries\StarCitizen\LIVE"),
        os.path.expandvars(r"%ProgramFiles(x86)%\Roberts Space Industries\StarCitizen\LIVE"),
    ]
    for path in possible_paths:
        if os.path.exists(path):
            return path
    return filedialog.askdirectory(title="Star Citizen LIVE-Verzeichnis wählen")
