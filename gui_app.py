import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from config import GOOGLE_SHEET_LINK, AVAILABLE_LANGS, STRINGTABLE_FOLDER
from google_sheet import read_google_sheet
from file_handler import process_ini_file, backup_existing_file, move_global_ini_and_set_language
from star_citizen import find_star_citizen_install_path


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sinister Inc. Stringtable Changer")
        self.geometry("500x350")
        self.resizable(False, False)

        # === Dark mode colors ===
        bg = "#1e1e1e"
        fg = "#ffffff"
        accent = "#3a3a3a"
        highlight = "#0078d7"

        self.configure(bg=bg)

        # Style configuration for ttk widgets
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(
            "TLabel",
            background=bg,
            foreground=fg,
        )
        style.configure(
            "TButton",
            background=accent,
            foreground=fg,
            borderwidth=0,
            focuscolor=accent,
            padding=6,
        )
        style.map(
            "TButton",
            background=[("active", highlight)],
            foreground=[("active", "#ffffff")],
        )
        style.configure(
            "TCombobox",
            fieldbackground=accent,
            background=accent,
            foreground=fg,
            arrowcolor=fg,
        )
        style.map("TCombobox",
                  fieldbackground=[("readonly", accent)],
                  selectbackground=[("readonly", accent)],
                  selectforeground=[("readonly", fg)])

        # === Widgets ===
        ttk.Label(self, text="Sprache wählen:").pack(pady=5)
        self.lang_var = tk.StringVar(value="en")
        ttk.Combobox(
            self, textvariable=self.lang_var, values=AVAILABLE_LANGS, state="readonly"
        ).pack()

        ttk.Label(self, text="Star Citizen LIVE-Verzeichnis:").pack(pady=5)
        path_frame = tk.Frame(self, bg=bg)
        path_frame.pack(pady=2)
        self.path_entry = tk.Entry(path_frame, width=40, bg=accent, fg=fg, insertbackground=fg, relief="flat")
        self.path_entry.pack(side="left", padx=(0, 5))
        ttk.Button(path_frame, text="Durchsuchen", command=self.browse_path).pack(side="left")

        self.status = tk.Text(
            self,
            height=10,
            width=60,
            state="disabled",
            bg=accent,
            fg=fg,
            insertbackground=fg,
            relief="flat",
            highlightthickness=1,
            highlightbackground=highlight,
        )
        self.status.pack(pady=10)

        ttk.Button(self, text="Stringtable erstellen", command=self.run).pack(pady=5)

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

        language = self.lang_var.get()  # e.g., "de"
        input_file = os.path.join(STRINGTABLE_FOLDER, f"{language}.ini")
        if not os.path.exists(input_file):
            messagebox.showerror("Fehler", f"Datei nicht gefunden: {input_file}")
            return

        path = self.path_entry.get() or find_star_citizen_install_path()
        if not path or not os.path.exists(path):
            messagebox.showerror("Fehler", f"Ungültiger Pfad: {path}")
            return

        # 1️⃣ Backup existing global.ini
        output_file = os.path.join(path, "global.ini")
        backup = backup_existing_file(output_file)
        if backup:
            self.log(f"Backup erstellt unter: {backup}")

        # 2️⃣ Process INI file (add suffixes)
        process_ini_file(data, input_file, output_file)
        self.log(f"global.ini erfolgreich erstellt:\n{output_file}")

        # 3️⃣ Move to localization folder & update user.cfg
        move_global_ini_and_set_language(output_file, path, language)

