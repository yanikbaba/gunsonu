# backup_manager_view.py — Minimal GUI for snapshot list/restore/delete (E4)
import tkinter as tk
from tkinter import ttk, messagebox
import pathlib, importlib

db_model = importlib.import_module("db_model")
adapter  = importlib.import_module("gunsonu_test_adapter")
bm       = importlib.import_module("backup_manager")

DB_FILE = str((pathlib.Path.cwd() / "gunsonu.sqlite").resolve())

def ensure_db():
    adapter.init_db(pathlib.Path(DB_FILE))
    db_model.ensure_schema(DB_FILE)

def refresh_table():
    ensure_db()
    for w in table.get_children():
        table.delete(w)
    rows = bm.list_snapshots(pathlib.Path(DB_FILE))
    for name, size in rows:
        table.insert("", "end", values=(name, size))

def take_snapshot():
    ensure_db()
    snap = bm.create_snapshot(pathlib.Path(DB_FILE))
    messagebox.showinfo("Snapshot", f"Snapshot alındı:\n{snap}")
    refresh_table()

def restore_selected():
    ensure_db()
    sel = table.selection()
    if not sel:
        # recover latest
        ok = bm.recover_snapshot(pathlib.Path(DB_FILE), None)
    else:
        name = table.item(sel[0], "values")[0]
        ok = bm.recover_snapshot(pathlib.Path(DB_FILE), name)
    if ok:
        messagebox.showinfo("Geri Yükleme", "Snapshot geri yüklendi.")
    else:
        messagebox.showwarning("Geri Yükleme", "Snapshot bulunamadı.")
    refresh_table()

def delete_selected():
    sel = table.selection()
    if not sel:
        messagebox.showwarning("Sil", "Lütfen bir snapshot seçin.")
        return
    name = table.item(sel[0], "values")[0]
    if messagebox.askyesno("Sil", f"{name} dosyasını silmek istiyor musunuz?"):
        bm.delete_snapshot(pathlib.Path(DB_FILE), name)
        refresh_table()

def main():
    ensure_db()
    root = tk.Tk()
    root.title("Backup Manager — GunSonu")

    frm = ttk.Frame(root, padding=12)
    frm.pack(fill="both", expand=True)

    global table
    table = ttk.Treeview(frm, columns=("name","size"), show="headings", height=12)
    table.heading("name", text="Dosya Adı")
    table.heading("size", text="Boyut (bayt)")
    table.column("name", width=360, anchor="w")
    table.column("size", width=120, anchor="e")
    table.grid(row=0, column=0, columnspan=3, sticky="nsew", pady=(0,8))

    ttk.Button(frm, text="Snapshot Al", command=take_snapshot).grid(row=1, column=0, sticky="w", padx=(0,8))
    ttk.Button(frm, text="Geri Yükle (Seçili/Yeni)", command=restore_selected).grid(row=1, column=1, sticky="w", padx=(0,8))
    ttk.Button(frm, text="Sil (Seçili)", command=delete_selected).grid(row=1, column=2, sticky="w")

    frm.columnconfigure(0, weight=1)
    frm.columnconfigure(1, weight=0)
    frm.columnconfigure(2, weight=0)
    frm.rowconfigure(0, weight=1)

    refresh_table()
    root.mainloop()

if __name__ == "__main__":
    main()