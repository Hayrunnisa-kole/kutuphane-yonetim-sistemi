import tkinter as tk
from tkinter import ttk, messagebox 
import db


def ceza_goruntuleme_ac():
    pencere = tk.Toplevel()
    pencere.title("Ceza Görüntüleme")
    pencere.geometry("950x500")

    ust_frame = tk.Frame(pencere)
    ust_frame.pack(fill=tk.X, padx=10, pady=5)

    tk.Label(ust_frame, text="Üye:").pack(side=tk.LEFT)

    combo_uye = ttk.Combobox(ust_frame, width=30)
    combo_uye.pack(side=tk.LEFT, padx=5)

    kolonlar = (
        "CezaID",
        "Uye",
        "Kitap",
        "CezaTarihi",
        "Tutar"
    )

    tablo = ttk.Treeview(
        pencere,
        columns=kolonlar,
        show="headings"
    )

    for col in kolonlar:
        tablo.heading(col, text=col)

    tablo.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def uyeleri_yukle():
        try:
            conn = db.get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT UyeID, CONCAT(Ad,' ',Soyad)
                FROM UYE
            """)

            uyeler = cursor.fetchall()
            combo_uye["values"] = [
                f"{u[0]} - {u[1]}" for u in uyeler
            ]
        except Exception as e:
            messagebox.showerror("Hata", f"Üyeler yüklenirken hata: {e}")
        finally:
            if 'conn' in locals() and conn.is_connected():
                conn.close()

    uyeleri_yukle()

    def cezalar_yukle():
        for r in tablo.get_children():
            tablo.delete(r)

        secilen_uye_metni = combo_uye.get()
        if not secilen_uye_metni:
            messagebox.showwarning("Uyarı", "Lütfen önce listeden bir üye seçiniz!")
            return

        try:
            uye_id = secilen_uye_metni.split(" - ")[0]

            conn = db.get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT 
                    c.CezaID,
                    CONCAT(u.Ad,' ',u.Soyad) as AdSoyad,
                    k.KitapAdi,
                    c.CezaTarihi,
                    c.Tutar
                FROM CEZA c
                JOIN ODUNC o ON c.OduncID = o.OduncID
                JOIN UYE u ON o.UyeID = u.UyeID
                JOIN KITAP k ON o.KitapID = k.KitapID
                WHERE u.UyeID = %s
            """, (uye_id,))

            sonuclar = cursor.fetchall()
            
            if not sonuclar:
                messagebox.showinfo("Bilgi", "Bu üyeye ait kayıtlı ceza bulunamadı.")
            else:
                for row in sonuclar:
                    tablo.insert("", tk.END, values=row)

        except Exception as e:
            messagebox.showerror("Hata Oluştu", str(e))
        finally:
            if 'conn' in locals() and conn.is_connected():
                conn.close()

    tk.Button(
        ust_frame,
        text="Cezaları Göster",
        command=cezalar_yukle
    ).pack(side=tk.LEFT, padx=10)