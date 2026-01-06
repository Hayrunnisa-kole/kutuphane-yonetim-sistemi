import tkinter as tk
from tkinter import ttk, messagebox
import db


def uye_yonetimi_ac():
    pencere = tk.Toplevel()
    pencere.title("Üye Yönetimi")
    pencere.geometry("900x550")


    kolonlar = ("UyeID", "Ad", "Soyad", "Telefon", "Email", "Borc")
    tablo = ttk.Treeview(pencere, columns=kolonlar, show="headings")

    tablo.heading("UyeID", text="ID")
    tablo.heading("Ad", text="Ad")
    tablo.heading("Soyad", text="Soyad")
    tablo.heading("Telefon", text="Telefon")
    tablo.heading("Email", text="Email")
    tablo.heading("Borc", text="Toplam Borç")

    tablo.column("UyeID", width=60)
    tablo.pack(fill=tk.BOTH, expand=True, pady=10)

    def uyeleri_yukle(filtre=""):
        for r in tablo.get_children():
            tablo.delete(r)

        conn = db.get_connection()
        cursor = conn.cursor()

        if filtre:
            cursor.execute("""
                SELECT UyeID, Ad, Soyad, Telefon, Email, ToplamBorc
                FROM UYE
                WHERE Ad LIKE %s OR Soyad LIKE %s OR Email LIKE %s
            """, (f"%{filtre}%", f"%{filtre}%", f"%{filtre}%"))
        else:
            cursor.execute("""
                SELECT UyeID, Ad, Soyad, Telefon, Email, ToplamBorc
                FROM UYE
            """)

        for row in cursor.fetchall():
            tablo.insert("", tk.END, values=row)

        conn.close()

    uyeleri_yukle()


    arama_frame = tk.Frame(pencere)
    arama_frame.pack(pady=5)

    tk.Label(arama_frame, text="Ara (Ad / Soyad / Email):").pack(side=tk.LEFT)
    entry_ara = tk.Entry(arama_frame)
    entry_ara.pack(side=tk.LEFT, padx=5)

    tk.Button(
        arama_frame,
        text="Ara",
        command=lambda: uyeleri_yukle(entry_ara.get())
    ).pack(side=tk.LEFT)

    form = tk.Frame(pencere)
    form.pack(pady=10)

    tk.Label(form, text="Ad").grid(row=0, column=0)
    entry_ad = tk.Entry(form)
    entry_ad.grid(row=0, column=1)

    tk.Label(form, text="Soyad").grid(row=1, column=0)
    entry_soyad = tk.Entry(form)
    entry_soyad.grid(row=1, column=1)

    tk.Label(form, text="Telefon").grid(row=2, column=0)
    entry_tel = tk.Entry(form)
    entry_tel.grid(row=2, column=1)

    tk.Label(form, text="Email").grid(row=3, column=0)
    entry_email = tk.Entry(form)
    entry_email.grid(row=3, column=1)

    secili_uye_id = None

    def tablo_sec(event):
        nonlocal secili_uye_id
        secilen = tablo.focus()
        if not secilen:
            return

        veri = tablo.item(secilen)["values"]
        secili_uye_id = veri[0]

        entry_ad.delete(0, tk.END)
        entry_ad.insert(0, veri[1])

        entry_soyad.delete(0, tk.END)
        entry_soyad.insert(0, veri[2])

        entry_tel.delete(0, tk.END)
        entry_tel.insert(0, veri[3])

        entry_email.delete(0, tk.END)
        entry_email.insert(0, veri[4])

    tablo.bind("<<TreeviewSelect>>", tablo_sec)


    def uye_ekle():
        if not entry_ad.get() or not entry_soyad.get() or not entry_email.get():
            messagebox.showwarning("Uyarı", "Ad, Soyad ve Email zorunludur")
            return

        conn = db.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO UYE (Ad, Soyad, Telefon, Email)
            VALUES (%s, %s, %s, %s)
        """, (
            entry_ad.get(),
            entry_soyad.get(),
            entry_tel.get(),
            entry_email.get()
        ))

        conn.commit()
        conn.close()

        uyeleri_yukle()
        messagebox.showinfo("Başarılı", "Üye eklendi")

    def uye_guncelle():
        if not secili_uye_id:
            messagebox.showwarning("Uyarı", "Güncellenecek üye seçin")
            return

        conn = db.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE UYE
            SET Ad=%s, Soyad=%s, Telefon=%s, Email=%s
            WHERE UyeID=%s
        """, (
            entry_ad.get(),
            entry_soyad.get(),
            entry_tel.get(),
            entry_email.get(),
            secili_uye_id
        ))

        conn.commit()
        conn.close()

        uyeleri_yukle()
        messagebox.showinfo("Başarılı", "Üye güncellendi")

    def uye_ozet_goster():
        if not secili_uye_id:
            messagebox.showwarning("Uyarı", "Lütfen özetini görmek istediğiniz üyeyi seçin.")
            return

        conn = db.get_connection()
        cursor = conn.cursor()

        try:
            cursor.callproc("sp_UyeOzetRaporu", (secili_uye_id,))
            
            for result in cursor.stored_results():
                row = result.fetchone()
                if row:
                    mesaj = (
                        f"👤 Üye: {row[0]}\n\n"
                        f"📚 Okuduğu/Elindeki Kitap: {row[1]}\n"
                        f"⚠️ Teslimi Geciken: {row[2]}\n"
                        f"💰 Toplam Borç: {row[3]} TL"
                    )
                    messagebox.showinfo("Üye Durum Raporu", mesaj)
                else:
                    messagebox.showerror("Hata", "Üye bilgisi alınamadı.")

        except Exception as e:
            messagebox.showerror("Hata", str(e))
        finally:
            conn.close()


    def uye_sil():
        secilen = tablo.focus()
        if not secilen:
            messagebox.showwarning("Uyarı", "Bir üye seçin")
            return

        uye_id = tablo.item(secilen)["values"][0]

        conn = db.get_connection()
        cursor = conn.cursor()


        cursor.execute("""
            SELECT COUNT(*)
            FROM ODUNC
            WHERE UyeID = %s
            AND TeslimTarihi IS NULL
        """, (uye_id,))

        if cursor.fetchone()[0] > 0:
            conn.close()
            messagebox.showerror(
                "Silme Engellendi",
                "Bu üyenin aktif ödünç aldığı kitaplar var."
            )
            return


        cursor.execute("""
            DELETE FROM ODUNC
            WHERE UyeID = %s
            AND TeslimTarihi IS NOT NULL
        """, (uye_id,))

        cursor.execute("""
            DELETE FROM UYE
            WHERE UyeID = %s
        """, (uye_id,))

        conn.commit()
        conn.close()

        uyeleri_yukle()
        messagebox.showinfo("Başarılı", "Üye tamamen silindi")

    butonlar = tk.Frame(pencere)
    butonlar.pack(pady=10)

    tk.Button(butonlar, text="Ekle", width=15, command=uye_ekle)\
        .grid(row=0, column=0, padx=5)

    tk.Button(butonlar, text="Güncelle", width=15, command=uye_guncelle)\
        .grid(row=0, column=1, padx=5)
    
    tk.Button(butonlar, text="Durum Özeti", width=15, command=uye_ozet_goster)\
        .grid(row=0, column=3, padx=5)

    tk.Button(butonlar, text="Sil", width=15, command=uye_sil)\
        .grid(row=0, column=2, padx=5)
