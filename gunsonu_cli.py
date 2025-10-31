# app.py — Tkinter GUI (E2+E5): Z Raporu giriş + Excel/PDF export + snapshot
import tkinter as tk
from tkinter import messagebox
import pathlib, importlib

exporter = importlib.import_module("exporter")
pdf_exporter = importlib.import_module("pdf_exporter")
db_model = importlib.import_module("db_model")
adapter = importlib.import_module("gunsonu_test_adapter")

APP_TITLE = "GunSonu — powered by Çözüm Bilgisayar"
YM = "2025-10"
DB_FILE = str((pathlib.Path.cwd() / "gunsonu.sqlite").resolve())

def ensure_db():
    adapter.init_db(pathlib.Path(DB_FILE))
    db_model.ensure_schema(DB_FILE)

def action_export():
    try:
        ensure_db()
        out_dir = adapter.default_db_dir()
        out_path = out_dir / "rapor.xlsx"
        exporter.export_all(DB_FILE, str(out_path), ym=YM)
        messagebox.showinfo("Excel", f"Excel oluşturuldu:\n{out_path}")
        status.set(f"Excel OK → {out_path}")
    except Exception as e:
        messagebox.showerror("Hata", f"Excel dışa aktarılamadı:\n{e}")
        status.set(f"Hata (excel): {e}")

def action_export_pdf():
    try:
        ensure_db()
        out_dir = adapter.default_db_dir()
        out_path = out_dir / "rapor.pdf"
        pdf_exporter.export_pdf(DB_FILE, str(out_path), ym=YM)
        messagebox.showinfo("PDF", f"PDF oluşturuldu:\n{out_path}")
        status.set(f"PDF OK → {out_path}")
    except Exception as e:
        messagebox.showerror("Hata", f"PDF dışa aktarılamadı:\n{e}")
        status.set(f"Hata (pdf): {e}")

def action_snapshot():
    try:
        ensure_db()
        snap = adapter.create_snapshot(pathlib.Path(DB_FILE))
        messagebox.showinfo("Snapshot", f"Snapshot alındı:\n{snap}")
        status.set(f"Snapshot OK → {snap}")
    except Exception as e:
        messagebox.showerror("Hata", f"Snapshot alınamadı:\n{e}")
        status.set(f"Hata (snapshot): {e}")

def action_recover():
    try:
        ensure_db()
        ok = adapter.recover_last_snapshot(pathlib.Path(DB_FILE))
        if ok:
            messagebox.showinfo("Geri Yükleme", "Son snapshot başarıyla geri yüklendi.")
            status.set("Recover OK")
        else:
            messagebox.showwarning("Geri Yükleme", "Snapshot bulunamadı.")
            status.set("Recover: snapshot yok")
    except Exception as e:
        messagebox.showerror("Hata", f"Geri yükleme başarısız:\n{e}")
        status.set(f"Hata (recover): {e}")

def action_save_z():
    try:
        ensure_db()
        date = ent_date.get().strip()
        cash = float(ent_cash.get().strip() or 0)
        pos  = float(ent_pos.get().strip() or 0)
        qr   = 1 if var_qr.get() else 0
        db_model.upsert_z_report(DB_FILE, date=date, cash_total=cash, pos_total=pos, qr_included=qr)
        messagebox.showinfo("Z Raporu", f"Kayıt edildi: {date} (Kasa={cash}, POS={pos}, QR={qr})")
        status.set(f"Z Raporu OK → {date}")
    except Exception as e:
        messagebox.showerror("Hata", f"Z Raporu kaydedilemedi:\n{e}")
        status.set(f"Hata (z): {e}")

def main():
    ensure_db()
    root = tk.Tk()
    root.title(APP_TITLE)

    frm = tk.Frame(root, padx=12, pady=12)
    frm.pack(fill="both")

    tk.Label(frm, text=APP_TITLE, font=("Segoe UI", 12, "bold")).grid(row=0, column=0, columnspan=8, sticky="w", pady=(0,10))

    # Z Raporu giriş alanları
    tk.Label(frm, text="Tarih (YYYY-MM-DD)").grid(row=1, column=0, sticky="w")
    global ent_date, ent_cash, ent_pos, var_qr, status
    ent_date = tk.Entry(frm, width=12); ent_date.insert(0, f"{YM}-01"); ent_date.grid(row=1, column=1, padx=(4,12))
    tk.Label(frm, text="Kasa").grid(row=1, column=2, sticky="w")
    ent_cash = tk.Entry(frm, width=10); ent_cash.insert(0, "0"); ent_cash.grid(row=1, column=3, padx=(4,12))
    tk.Label(frm, text="POS").grid(row=1, column=4, sticky="w")
    ent_pos = tk.Entry(frm, width=10); ent_pos.insert(0, "0"); ent_pos.grid(row=1, column=5, padx=(4,12))
    var_qr = tk.BooleanVar(value=True); tk.Checkbutton(frm, text="QR Dahil", variable=var_qr).grid(row=1, column=6, padx=(8,0))

    # Buttons
    tk.Button(frm, text="Z Raporu Kaydet", command=action_save_z).grid(row=2, column=0, padx=4, pady=8, sticky="w")
    tk.Button(frm, text=f"Excel'e Dışa Aktar ({YM})", command=action_export).grid(row=2, column=1, padx=4, pady=8, sticky="w")
    tk.Button(frm, text=f"PDF'e Dışa Aktar ({YM})", command=action_export_pdf).grid(row=2, column=2, padx=4, pady=8, sticky="w")
    tk.Button(frm, text="Snapshot Al", command=action_snapshot).grid(row=2, column=3, padx=4, pady=8, sticky="w")
    tk.Button(frm, text="Son Snapshot'tan Geri Yükle", command=action_recover).grid(row=2, column=4, padx=4, pady=8, sticky="w")

    status = tk.StringVar(value="Hazır")
    tk.Label(frm, textvariable=status, anchor="w").grid(row=3, column=0, columnspan=8, sticky="ew")

    root.mainloop()

if __name__ == "__main__":
    main()