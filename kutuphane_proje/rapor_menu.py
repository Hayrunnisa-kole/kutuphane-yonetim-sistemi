import tkinter as tk

from rapor_odunc_tarih import rapor_odunc_tarih_ac
from rapor_geciken import rapor_geciken_ac
from rapor_en_cok_odunc import rapor_en_cok_odunc_ac


def rapor_menu_ac():
    pencere = tk.Toplevel()
    pencere.title("Raporlar")
    pencere.geometry("400x300")

    tk.Label(
        pencere,
        text="RAPORLAR",
        font=("Arial", 16, "bold")
    ).pack(pady=15)

    tk.Button(
        pencere,
        text="📅 Tarih Aralığına Göre Ödünç Raporu",
        width=40,
        height=2,
        command=rapor_odunc_tarih_ac
    ).pack(pady=5)

    tk.Button(
        pencere,
        text="⏰ Geciken Kitaplar Raporu",
        width=40,
        height=2,
        command=rapor_geciken_ac
    ).pack(pady=5)

    tk.Button(
        pencere,
        text="📊 En Çok Ödünç Alınan Kitaplar",
        width=40,
        height=2,
        command=rapor_en_cok_odunc_ac
    ).pack(pady=5)
