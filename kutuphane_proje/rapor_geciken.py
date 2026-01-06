import tkinter as tk
from tkinter import ttk
import db


def rapor_geciken_ac():
    pencere = tk.Toplevel()
    pencere.title("Geciken Kitaplar Raporu")
    pencere.geometry("900x500")

    kolonlar = (
        "Uye",
        "Kitap",
        "OduncTarihi",
        "SonTeslimTarihi",
        "GecikmeGunu"
    )

    tablo = ttk.Treeview(
        pencere,
        columns=kolonlar,
        show="headings"
    )

    for col in kolonlar:
        tablo.heading(col, text=col)

    tablo.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def raporu_getir():
        for r in tablo.get_children():
            tablo.delete(r)

        conn = db.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                CONCAT(u.Ad, ' ', u.Soyad),
                k.KitapAdi,
                o.OduncTarihi,
                o.SonTeslimTarihi,
                DATEDIFF(CURDATE(), o.SonTeslimTarihi)
            FROM ODUNC o
            JOIN UYE u ON o.UyeID = u.UyeID
            JOIN KITAP k ON o.KitapID = k.KitapID
            WHERE o.TeslimTarihi IS NULL
              AND o.SonTeslimTarihi < CURDATE()
            ORDER BY 5 DESC
        """)

        for row in cursor.fetchall():
            tablo.insert("", tk.END, values=row)

        conn.close()

    raporu_getir()
