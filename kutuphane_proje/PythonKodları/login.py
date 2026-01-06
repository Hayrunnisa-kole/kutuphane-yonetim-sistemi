import tkinter as tk
from tkinter import messagebox
import db
from menu import ana_menu_ac


def login_ekrani():
    pencere = tk.Tk()
    pencere.title("Giriş")
    pencere.geometry("300x220")
    pencere.resizable(False, False)

    tk.Label(pencere, text="Kullanıcı Adı").pack(pady=5)
    entry_kadi = tk.Entry(pencere)
    entry_kadi.pack()

    tk.Label(pencere, text="Şifre").pack(pady=5)
    entry_sifre = tk.Entry(pencere, show="*")
    entry_sifre.pack()

    def giris_yap():
        kullanici_adi = entry_kadi.get()
        sifre = entry_sifre.get()

        if not kullanici_adi or not sifre:
            messagebox.showwarning(
                "Uyarı",
                "Kullanıcı adı ve şifre giriniz"
            )
            return

        conn = db.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
         SELECT KullaniciID, KullaniciAdi, Rol
         FROM KULLANICI
         WHERE KullaniciAdi = %s AND Sifre = %s
        """, (kullanici_adi, sifre))

        sonuc = cursor.fetchone()
        conn.close()

        if sonuc:
            giris_yapan_id = sonuc[0]  
            giris_yapan_ad = sonuc[1]
            giris_yapan_rol = sonuc[2]

            pencere.destroy()
            ana_menu_ac(giris_yapan_id, giris_yapan_ad, giris_yapan_rol)
        else:
            messagebox.showerror(
                "Hata",
                "Kullanıcı adı veya şifre yanlış"
            )

    tk.Button(
        pencere,
        text="Giriş",
        width=15,
        command=giris_yap
    ).pack(pady=15)

    pencere.mainloop()


if __name__ == "__main__":
    login_ekrani()
