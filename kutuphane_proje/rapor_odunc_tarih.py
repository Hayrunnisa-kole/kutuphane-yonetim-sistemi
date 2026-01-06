import tkinter as tk
from tkinter import ttk, messagebox
import db


def rapor_odunc_tarih_ac():
    pencere = tk.Toplevel()
    pencere.title("Tarih Aralığına Göre Ödünç Raporu")
    pencere.geometry("900x500")


    ust = tk.Frame(pencere)
    ust.pack(pady=10)

    tk.Label(ust, text="Başlangıç Tarihi (YYYY-MM-DD):").grid(row=0, column=0)
    entry_bas = tk.Entry(ust)
    entry_bas.grid(row=0, column=1, padx=5)

    tk.Label(ust, text="Bitiş Tarihi (YYYY-MM-DD):").grid(row=0, column=2)
    entry_bit = tk.Entry(ust)
    entry_bit.grid(row=0, column=3, padx=5)


    kolonlar = ("Uye", "Kitap", "OduncTarihi", "TeslimTarihi", "Durum")
    tablo = ttk.Treeview(pencere, columns=kolonlar, show="headings")

    for col in kolonlar:
        tablo.heading(col, text=col)

    tablo.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)


    def raporu_getir():
        if not entry_bas.get() or not entry_bit.get():
            messagebox.showwarning("Uyarı", "Tarihleri giriniz")
            return

        for r in tablo.get_children():
            tablo.delete(r)

        conn = db.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                CONCAT(u.Ad, ' ', u.Soyad),
                k.KitapAdi,
                o.OduncTarihi,
                o.TeslimTarihi,
                CASE
                    WHEN o.TeslimTarihi IS NULL THEN 'Teslim Edilmedi'
                    ELSE 'Teslim Edildi'
                END
            FROM ODUNC o
            JOIN UYE u ON o.UyeID = u.UyeID
            JOIN KITAP k ON o.KitapID = k.KitapID
            WHERE o.OduncTarihi BETWEEN %s AND %s
            ORDER BY o.OduncTarihi
        """, (entry_bas.get(), entry_bit.get()))

        for row in cursor.fetchall():
            tablo.insert("", tk.END, values=row)

        conn.close()

    tk.Button(
        ust,
        text="Raporu Getir",
        command=raporu_getir
    ).grid(row=0, column=4, padx=10)
