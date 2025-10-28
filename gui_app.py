import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from config import GOOGLE_SHEET_LINK, AVAILABLE_LANGS, STRINGTABLE_FOLDER
from google_sheet import read_google_sheet
from file_handler import process_ini_file, backup_existing_file
from star_citizen import find_star_citizen_install_path

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sinister Inc. Stringtable Changer")
        self.geometry("500x300")
        self.resizable(False, False)

        tk.Label(self, text="Sprache wählen:").pack(pady=5)
        self.lang_var = tk.StringVar(value="de")
        ttk.Combobox(self, textvariable=self.lang_var, values=AVAILABLE_LANGS).pack()

        tk.Label(self, text="Star Citizen LIVE-Verzeichnis:").pack(pady=5)
        self.path_entry = tk.Entry(self, width=50)
        self.path_entry.pack()
        tk.Button(self, text="Durchsuchen", command=self.browse_path).pack(pady=5)

        self.status = tk.Text(self, height=10, width=60, state="disabled")
        self.status.pack(pady=5)

        tk.Button(self, text="global.ini erstellen", command=self.run).pack(pady=10)

    def browse_path(self):
        path = filedialog.askdirectory(title="Star Citizen LIVE-Verzeichnis wählen")
        if path:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, path)

    def log(self, message):
        self.status.configure(state="normal")
        self.status.insert(tk.END, message + "\n")
        self.status.configure(state="disabled")
        self.status.see(tk.END)

    def run(self):
        self.log("Lade Google Sheet ...")
        data = read_google_sheet(GOOGLE_SHEET_LINK)
        if not data:
            return
        self.log(f"→ {len(data)} Einträge geladen.")

        language = self.lang_var.get()
        input_file = os.path.join(STRINGTABLE_FOLDER, f"{language}.ini")
        if not os.path.exists(input_file):
            messagebox.showerror("Fehler", f"Datei nicht gefunden: {input_file}")
            return

        path = self.path_entry.get() or find_star_citizen_install_path()
        if not path or not os.path.exists(path):
            messagebox.showerror("Fehler", f"Ungültiger Pfad: {path}")
            return

        output_file = os.path.join(path, "global.ini")
        backup = backup_existing_file(output_file)
        if backup:
            self.log(f"Backup erstellt unter: {backup}")

        self.log(f"Bearbeite Sprachdatei ({language}.ini) ...")
        process_ini_file(data, input_file, output_file)
        self.log(f"global.ini erfolgreich erstellt:\n{output_file}")
        messagebox.showinfo("Fertig", f"global.ini erfolgreich erstellt:\n{output_file}")
