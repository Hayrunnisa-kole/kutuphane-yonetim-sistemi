import tkinter as tk
from odunc_verme import odunc_verme_ac
from kitap_yonetimi import kitap_yonetimi_ac
from uye_yonetimi import uye_yonetimi_ac
from teslim_alma import teslim_alma_ac
from ceza_goruntuleme import ceza_goruntuleme_ac
from rapor_menu import rapor_menu_ac
from dinamik_kitap_raporu import dinamik_kitap_raporu_ac


def ana_menu_ac(giris_yapan_id, giris_yapan_ad, giris_yapan_rol):
    pencere = tk.Tk()
    pencere.title("Ana Menü")
    pencere.geometry("400x500")
    pencere.resizable(False, False)

    tk.Label(
        pencere,
        text=f"Hoş geldiniz, {giris_yapan_ad} ({giris_yapan_rol})",
        font=("Arial", 12, "bold")
    ).pack(pady=20)


    tk.Button(
        pencere,
        text="Üye Yönetimi",
        width=25,
        command=uye_yonetimi_ac
    ).pack(pady=5)

    tk.Button(
        pencere,
        text="Kitap Yönetimi",
        width=25,
        command=kitap_yonetimi_ac
    ).pack(pady=5)

    tk.Button(
        pencere,
        text="Ödünç Verme",
        width=25,
        command=lambda: odunc_verme_ac(giris_yapan_id)
    ).pack(pady=5)

    tk.Button(
        pencere,
        text="Kitap Teslim Alma",
        width=25,
        command=teslim_alma_ac
    ).pack(pady=5)

    tk.Button(
        pencere,
        text="Ceza Görüntüleme",
        width=25,
        command=ceza_goruntuleme_ac
    ).pack(pady=5)


    if giris_yapan_rol == "Admin":
        tk.Button(
            pencere,
            text="📑 Raporlar",
            width=25,
            height=2,
            command=rapor_menu_ac
        ).pack(pady=5)

        tk.Button(
            pencere,
            text="Dinamik Sorgu Ekranı",
            width=25,
            height=2,
            command=dinamik_kitap_raporu_ac
        ).pack(pady=8)


    tk.Button(
        pencere,
        text="Çıkış",
        width=25,
        command=pencere.destroy
    ).pack(pady=20)

    pencere.mainloop()
