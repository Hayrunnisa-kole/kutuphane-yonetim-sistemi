import tkinter as tk
from tkinter import ttk, messagebox
import db


def rapor_en_cok_odunc_ac():
    pencere = tk.Toplevel()
    pencere.title("En Çok Ödünç Alınan Kitaplar")
    pencere.geometry("700x500")

    ust = tk.Frame(pencere)
    ust.pack(pady=10)

    tk.Label(ust, text="Başlangıç Tarihi (YYYY-AA-GG):").grid(row=0, column=0)
    entry_baslangic = tk.Entry(ust)
    entry_baslangic.grid(row=0, column=1)

    tk.Label(ust, text="Bitiş Tarihi (YYYY-AA-GG):").grid(row=1, column=0)
    entry_bitis = tk.Entry(ust)
    entry_bitis.grid(row=1, column=1)

    kolonlar = ("KitapAdi", "OduncSayisi")

    tablo = ttk.Treeview(
        pencere,
        columns=kolonlar,
        show="headings"
    )

    tablo.heading("KitapAdi", text="Kitap Adı")
    tablo.heading("OduncSayisi", text="Ödünç Sayısı")

    tablo.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def raporu_getir():
        bas = entry_baslangic.get()
        bit = entry_bitis.get()

        if not bas or not bit:
            messagebox.showwarning(
                "Uyarı",
                "Tarih aralığı giriniz"
            )
            return

        for r in tablo.get_children():
            tablo.delete(r)

        conn = db.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                k.KitapAdi,
                COUNT(o.OduncID)
            FROM ODUNC o
            JOIN KITAP k ON o.KitapID = k.KitapID
            WHERE o.OduncTarihi BETWEEN %s AND %s
            GROUP BY k.KitapID, k.KitapAdi
            ORDER BY 2 DESC
        """, (bas, bit))

        for row in cursor.fetchall():
            tablo.insert("", tk.END, values=row)

        conn.close()

    tk.Button(
        pencere,
        text="Raporu Getir",
        width=25,
        command=raporu_getir
    ).pack(pady=5)
