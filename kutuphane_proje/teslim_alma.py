import tkinter as tk
from tkinter import ttk, messagebox
import db
from datetime import date



def teslim_alma_ac():
    pencere = tk.Toplevel()
    pencere.title("Kitap Teslim Alma")
    pencere.geometry("900x500")

    kolonlar = (
        "OduncID",
        "Uye",
        "Kitap",
        "OduncTarihi",
        "SonTeslimTarihi"
    )

    tablo = ttk.Treeview(
        pencere,
        columns=kolonlar,
        show="headings"
    )

    tablo.heading("OduncID", text="ID")
    tablo.heading("Uye", text="Üye")
    tablo.heading("Kitap", text="Kitap")
    tablo.heading("OduncTarihi", text="Ödünç Tarihi")
    tablo.heading("SonTeslimTarihi", text="Son Teslim")

    tablo.column("OduncID", width=60)
    tablo.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)


    def aktif_oduncleri_yukle():
        for r in tablo.get_children():
            tablo.delete(r)

        conn = db.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT 
                o.OduncID,
                CONCAT(u.Ad, ' ', u.Soyad),
                k.KitapAdi,
                o.OduncTarihi,
                o.SonTeslimTarihi
            FROM ODUNC o
            JOIN UYE u ON o.UyeID = u.UyeID
            JOIN KITAP k ON o.KitapID = k.KitapID
            WHERE o.TeslimTarihi IS NULL
        """)

        for row in cursor.fetchall():
            tablo.insert("", tk.END, values=row)

        conn.close()

    aktif_oduncleri_yukle()


    def teslim_al():
        secilen = tablo.focus()
        if not secilen:
            messagebox.showwarning(
                "Uyarı",
                "Teslim alınacak ödünç seçin"
            )
            return

        odunc_id = tablo.item(secilen)["values"][0]

        conn = db.get_connection()
        cursor = conn.cursor()

        try:
            cursor.callproc(
                "sp_KitapTeslimAl",
                (odunc_id,date.today())
            )
            conn.commit()

            messagebox.showinfo(
                "Başarılı",
                "Kitap teslim alındı"
            )

            aktif_oduncleri_yukle()

        except Exception as e:
            messagebox.showerror("Hata", str(e))

        finally:
            conn.close()


    tk.Button(
        pencere,
        text="Teslim Al",
        width=25,
        height=2,
        command=teslim_al
    ).pack(pady=10)
