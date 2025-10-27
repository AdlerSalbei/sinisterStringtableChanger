from pathlib import Path

string path = Path("\StarCitizen\LIVE\data\")

if path.is_dir():
    print("Folder exists!")
else:
    print("Folder does not exist.")