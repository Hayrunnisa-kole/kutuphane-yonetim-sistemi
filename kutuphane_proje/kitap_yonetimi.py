import tkinter as tk
from tkinter import ttk, messagebox
import db


def kitap_yonetimi_ac():
    pencere = tk.Toplevel()
    pencere.title("Kitap Yönetimi")
    pencere.geometry("950x550")

    kolonlar = (
        "KitapID",
        "KitapAdi",
        "Yazar",
        "Kategori",
        "BasimYili",
        "ToplamAdet",
        "MevcutAdet"
    )

    tablo = ttk.Treeview(pencere, columns=kolonlar, show="headings")

    tablo.heading("KitapID", text="ID")
    tablo.heading("KitapAdi", text="Kitap Adı")
    tablo.heading("Yazar", text="Yazar")
    tablo.heading("Kategori", text="Kategori")
    tablo.heading("BasimYili", text="Basım Yılı")
    tablo.heading("ToplamAdet", text="Toplam")
    tablo.heading("MevcutAdet", text="Mevcut")

    tablo_frame = tk.Frame(pencere)
    tablo_frame.pack(fill=tk.BOTH, expand=True)

    tablo.pack(fill=tk.BOTH, expand=True)

    def kitaplari_yukle(filtre=""):
        for row in tablo.get_children():
            tablo.delete(row)

        conn = db.get_connection()
        cursor = conn.cursor(buffered=True)

        if filtre:
            cursor.execute("""
                SELECT KitapID, KitapAdi, Yazar, Kategori,
                       BasimYili, ToplamAdet, MevcutAdet
                FROM KITAP
                WHERE KitapAdi LIKE %s OR Yazar LIKE %s
            """, (f"%{filtre}%", f"%{filtre}%"))
        else:
            cursor.execute("""
                SELECT KitapID, KitapAdi, Yazar, Kategori,
                       BasimYili, ToplamAdet, MevcutAdet
                FROM KITAP
            """)

        for kitap in cursor.fetchall():
            tablo.insert("", tk.END, values=kitap)

        conn.close()

    kitaplari_yukle()

    arama = tk.Frame(pencere)
    arama.pack(pady=5)

    tk.Label(arama, text="Ara (Kitap Adı / Yazar):").pack(side=tk.LEFT)
    entry_ara = tk.Entry(arama)
    entry_ara.pack(side=tk.LEFT, padx=5)

    tk.Button(
        arama,
        text="Ara",
        command=lambda: kitaplari_yukle(entry_ara.get())
    ).pack(side=tk.LEFT)


    form = tk.Frame(pencere)
    form.pack(pady=10)
    tk.Label(form, text="Kitap Adı").grid(row=0, column=0)
    entry_kitapadi = tk.Entry(form, width=30)
    entry_kitapadi.grid(row=0, column=1)

    tk.Label(form, text="Yazar").grid(row=1, column=0)
    entry_yazar = tk.Entry(form)
    entry_yazar.grid(row=1, column=1)

    tk.Label(form, text="Kategori").grid(row=2, column=0)
    entry_kategori = tk.Entry(form)
    entry_kategori.grid(row=2, column=1)

    tk.Label(form, text="Basım Yılı").grid(row=3, column=0)
    entry_basimyili = tk.Entry(form)
    entry_basimyili.grid(row=3, column=1)

    tk.Label(form, text="Toplam Adet").grid(row=4, column=0)
    entry_toplam = tk.Entry(form)
    entry_toplam.grid(row=4, column=1)

    secili_kitap_id = None

    def tablo_sec(event):
        nonlocal secili_kitap_id
        secilen = tablo.focus()
        if not secilen:
            return

        veri = tablo.item(secilen)["values"]
        secili_kitap_id = veri[0]

        entry_kitapadi.delete(0, tk.END)
        entry_kitapadi.insert(0, veri[1])

        entry_yazar.delete(0, tk.END)
        entry_yazar.insert(0, veri[2])

        entry_kategori.delete(0, tk.END)
        entry_kategori.insert(0, veri[3])

        entry_basimyili.delete(0, tk.END)
        entry_basimyili.insert(0, veri[4])

        entry_toplam.delete(0, tk.END)
        entry_toplam.insert(0, veri[5])

    tablo.bind("<<TreeviewSelect>>", tablo_sec)

    def kitap_ekle():
        if not entry_kitapadi.get() or not entry_yazar.get():
            messagebox.showwarning("Uyarı", "Zorunlu alanlar boş")
            return

        conn = db.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO KITAP
            (KitapAdi, Yazar, Kategori, BasimYili, ToplamAdet, MevcutAdet)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            entry_kitapadi.get(),
            entry_yazar.get(),
            entry_kategori.get(),
            entry_basimyili.get(),
            entry_toplam.get(),
            entry_toplam.get()  
        ))

        conn.commit()
        conn.close()

        kitaplari_yukle()
        messagebox.showinfo("Başarılı", "Kitap eklendi")

    def kitap_guncelle():
        if not secili_kitap_id:
            messagebox.showwarning("Uyarı", "Kitap seçin")
            return

        conn = db.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE KITAP
            SET KitapAdi=%s, Yazar=%s, Kategori=%s,
                BasimYili=%s, ToplamAdet=%s
            WHERE KitapID=%s
        """, (
            entry_kitapadi.get(),
            entry_yazar.get(),
            entry_kategori.get(),
            entry_basimyili.get(),
            entry_toplam.get(),
            secili_kitap_id
        ))

        conn.commit()
        conn.close()

        kitaplari_yukle()
        messagebox.showinfo("Başarılı", "Kitap güncellendi")

    def kitap_sil():
        if not secili_kitap_id:
            messagebox.showwarning("Uyarı", "Kitap seçin")
            return

        conn = db.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*) FROM ODUNC
            WHERE KitapID=%s AND TeslimTarihi IS NULL
        """, (secili_kitap_id,))
        aktif = cursor.fetchone()[0]

        if aktif > 0:
            conn.close()
            messagebox.showerror(
                "Engellendi",
                "Kitap aktif ödünçte, silinemez"
            )
            return

        cursor.execute(
            "DELETE FROM KITAP WHERE KitapID=%s",
            (secili_kitap_id,)
        )

        conn.commit()
        conn.close()

        kitaplari_yukle()
        messagebox.showinfo("Başarılı", "Kitap silindi")

    butonlar = tk.Frame(pencere)
    butonlar.pack(pady=10)

    tk.Button(butonlar, text="Ekle", width=15, command=kitap_ekle)\
        .grid(row=0, column=0, padx=5)

    tk.Button(butonlar, text="Güncelle", width=15, command=kitap_guncelle)\
        .grid(row=0, column=1, padx=5)

    tk.Button(butonlar, text="Sil", width=15, command=kitap_sil)\
        .grid(row=0, column=2, padx=5)
