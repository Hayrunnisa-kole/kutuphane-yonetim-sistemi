import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import db
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas



def dinamik_kitap_raporu_ac():
    pencere = tk.Toplevel()
    pencere.title("Dinamik Kitap Raporu")
    pencere.geometry("1000x600")

    filtre = tk.LabelFrame(pencere, text="Filtreler")
    filtre.pack(fill=tk.X, padx=10, pady=10)

    tk.Label(filtre, text="Kitap Adı").grid(row=0, column=0)
    entry_kitapadi = tk.Entry(filtre)
    entry_kitapadi.grid(row=0, column=1)

    tk.Label(filtre, text="Yazar").grid(row=0, column=2)
    entry_yazar = tk.Entry(filtre)
    entry_yazar.grid(row=0, column=3)

    tk.Label(filtre, text="Kategori").grid(row=1, column=0)
    combo_kategori = ttk.Combobox(
        filtre,
        values=["", "Roman", "Bilim", "Tarih", "Edebiyat"]
    )
    combo_kategori.grid(row=1, column=1)

    tk.Label(filtre, text="Basım Yılı Min").grid(row=1, column=2)
    entry_min = tk.Entry(filtre)
    entry_min.grid(row=1, column=3)

    tk.Label(filtre, text="Basım Yılı Max").grid(row=1, column=4)
    entry_max = tk.Entry(filtre)
    entry_max.grid(row=1, column=5)

    mevcut_var = tk.IntVar()
    tk.Checkbutton(
        filtre,
        text="Sadece Mevcut Kitaplar",
        variable=mevcut_var
    ).grid(row=2, column=0, columnspan=2)

    kolonlar = (
        "KitapAdi", "Yazar", "Kategori",
        "BasimYili", "ToplamAdet", "MevcutAdet"
    )

    tablo = ttk.Treeview(
        pencere,
        columns=kolonlar,
        show="headings"
    )

    for k in kolonlar:
        tablo.heading(k, text=k)

    tablo.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)


    def dinamik_kitap_ara():
        sql = """
            SELECT KitapAdi, Yazar, Kategori,
                   BasimYili, ToplamAdet, MevcutAdet
            FROM KITAP
            WHERE 1=1
        """
        params = []

        if entry_kitapadi.get():
            sql += " AND KitapAdi LIKE %s"
            params.append(f"%{entry_kitapadi.get()}%")

        if entry_yazar.get():
            sql += " AND Yazar LIKE %s"
            params.append(f"%{entry_yazar.get()}%")

        if combo_kategori.get():
            sql += " AND Kategori = %s"
            params.append(combo_kategori.get())

        if entry_min.get():
            sql += " AND BasimYili >= %s"
            params.append(entry_min.get())

        if entry_max.get():
            sql += " AND BasimYili <= %s"
            params.append(entry_max.get())

        if mevcut_var.get() == 1:
            sql += " AND MevcutAdet > 0"

        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute(sql, params)

        for r in tablo.get_children():
            tablo.delete(r)

        for row in cursor.fetchall():
            tablo.insert("", tk.END, values=row)

        conn.close()

    def excel_export():
        if not tablo.get_children():
            messagebox.showwarning(
                "Uyarı",
                "Excel'e aktarılacak veri yok"
            )
            return

        dosya_yolu = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel Dosyası", "*.xlsx")]
        )

        if not dosya_yolu:
            return

        veriler = []
        kolon_isimleri = list(kolonlar)

        for satir in tablo.get_children():
            veriler.append(tablo.item(satir)["values"])

        df = pd.DataFrame(veriler, columns=kolon_isimleri)
        df.to_excel(dosya_yolu, index=False)

        messagebox.showinfo(
            "Başarılı",
            "Excel dosyası oluşturuldu"
        )


    tk.Button(
        filtre,
        text="Sorgula",
        width=20,
        command=dinamik_kitap_ara
    ).grid(row=2, column=4, pady=5)

    tk.Button(
        filtre,
        text="Excel'e Aktar",
        width=20,
        command=excel_export
    ).grid(row=2, column=5, pady=5)

    def pdf_export():
     if not tablo.get_children():
         messagebox.showwarning(
             "Uyarı",
             "PDF'e aktarılacak veri yok"
         )
         return

     dosya_yolu = filedialog.asksaveasfilename(
         defaultextension=".pdf",
         filetypes=[("PDF Dosyası", "*.pdf")]
     )

     if not dosya_yolu:
         return

     c = canvas.Canvas(dosya_yolu, pagesize=A4)
     width, height = A4

     x = 40
     y = height - 40

     c.setFont("Helvetica-Bold", 12)
     c.drawString(x, y, "Dinamik Kitap Raporu")
     y -= 30

     c.setFont("Helvetica", 9)

     basliklar = list(kolonlar)
     for baslik in basliklar:
         c.drawString(x, y, baslik)
         x += 90

     y -= 15
     x = 40

     for satir in tablo.get_children():
         for veri in tablo.item(satir)["values"]:
             c.drawString(x, y, str(veri))
             x += 90

         y -= 15
         x = 40

         if y < 40:
             c.showPage()
             c.setFont("Helvetica", 9)
             y = height - 40
 
     c.save()
 
     messagebox.showinfo(
         "Başarılı",
         "PDF dosyası oluşturuldu"
     )

    tk.Button(
    filtre,
    text="PDF'e Aktar",
    width=20,
    command=pdf_export
    ).grid(row=2, column=6, pady=5)
