import tkinter as tk
from tkinter import ttk, messagebox
import db


def odunc_verme_ac(giris_yapan_id):
    pencere = tk.Toplevel()
    pencere.title("Ödünç Verme")
    pencere.geometry("1000x600")


    ust_frame = tk.Frame(pencere)
    ust_frame.pack(fill=tk.BOTH, expand=True)

    alt_frame = tk.Frame(pencere)
    alt_frame.pack(fill=tk.X)


    uye_frame = tk.LabelFrame(ust_frame, text="Üyeler")
    uye_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

    uye_tablo = ttk.Treeview(
        uye_frame,
        columns=("UyeID", "Ad", "Soyad"),
        show="headings"
    )
    uye_tablo.heading("UyeID", text="ID")
    uye_tablo.heading("Ad", text="Ad")
    uye_tablo.heading("Soyad", text="Soyad")
    uye_tablo.pack(fill=tk.BOTH, expand=True)


    kitap_frame = tk.LabelFrame(ust_frame, text="Kitaplar")
    kitap_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

    kitap_tablo = ttk.Treeview(
        kitap_frame,
        columns=("KitapID", "KitapAdi", "MevcutAdet"),
        show="headings"
    )
    kitap_tablo.heading("KitapID", text="ID")
    kitap_tablo.heading("KitapAdi", text="Kitap Adı")
    kitap_tablo.heading("MevcutAdet", text="Stok")
    kitap_tablo.pack(fill=tk.BOTH, expand=True)


    def uyeleri_yukle():
        for r in uye_tablo.get_children():
            uye_tablo.delete(r)

        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT UyeID, Ad, Soyad FROM UYE")

        for row in cursor.fetchall():
            uye_tablo.insert("", tk.END, values=row)

        conn.close()

    def kitaplari_yukle():
        for r in kitap_tablo.get_children():
            kitap_tablo.delete(r)

        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT KitapID, KitapAdi, MevcutAdet FROM KITAP"
        )

        for row in cursor.fetchall():
            kitap_tablo.insert("", tk.END, values=row)

        conn.close()

    uyeleri_yukle()
    kitaplari_yukle()


    secili_uye_id = None
    secili_kitap_id = None

    def uye_sec(event):
        nonlocal secili_uye_id
        secilen = uye_tablo.focus()
        if secilen:
            secili_uye_id = uye_tablo.item(secilen)["values"][0]

    def kitap_sec(event):
        nonlocal secili_kitap_id
        secilen = kitap_tablo.focus()
        if secilen:
            secili_kitap_id = kitap_tablo.item(secilen)["values"][0]

    uye_tablo.bind("<<TreeviewSelect>>", uye_sec)
    kitap_tablo.bind("<<TreeviewSelect>>", kitap_sec)


    def odunc_ver():
        if not secili_uye_id or not secili_kitap_id:
            messagebox.showwarning(
                "Uyarı",
                "Üye ve kitap seçmelisiniz"
            )
            return

        conn = db.get_connection()
        cursor = conn.cursor()

        try:
            cursor.callproc(
                "sp_YeniOduncVer",
                (secili_uye_id, secili_kitap_id, giris_yapan_id)
            )
            conn.commit()

            messagebox.showinfo(
                "Başarılı",
                "Ödünç verme işlemi tamamlandı"
            )

            kitaplari_yukle()

        except Exception as e:
            messagebox.showerror("Hata", str(e))

        finally:
            conn.close()

    tk.Button(
        alt_frame,
        text="Ödünç Ver",
        width=30,
        height=2,
        command=odunc_ver
    ).pack(pady=10)

