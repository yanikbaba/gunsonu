# personnel_view.py — Minimal Tkinter table for B2: Person | Toplam | Adet | Son Tarih
import tkinter as tk
import pathlib, importlib

db_model = importlib.import_module("db_model")
adapter  = importlib.import_module("gunsonu_test_adapter")

DB_FILE = str((pathlib.Path.cwd() / "gunsonu.sqlite").resolve())
YM = "2025-10"

def ensure_db():
    adapter.init_db(pathlib.Path(DB_FILE))
    db_model.ensure_schema(DB_FILE)

def reload_table():
    ensure_db()
    rows = db_model.personnel_advances_summary_b2(DB_FILE, ym=YM)
    for w in table.get_children():
        table.delete(w)
    for person, total, cnt, last in rows:
        table.insert("", "end", values=(person, f"{total:.2f}", cnt, last))

def main():
    ensure_db()
    root = tk.Tk()
    root.title("Personel Avans (B2)")

    from tkinter import ttk
    global table
    table = ttk.Treeview(root, columns=("person","total","count","last"), show="headings", height=12)
    table.heading("person", text="Person")
    table.heading("total", text="Toplam Avans")
    table.heading("count", text="Adet")
    table.heading("last",  text="Son Tarih")
    table.pack(fill="both", expand=True, padx=10, pady=10)

    btn = tk.Button(root, text="Yenile (2025-10)", command=reload_table)
    btn.pack(pady=(0,10))

    reload_table()
    root.mainloop()

if __name__ == "__main__":
    main()