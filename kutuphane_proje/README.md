Kütüphane Yönetim Sistemi (VTYS Projesi)

Bu proje, Veritabanı Yönetim Sistemleri dersi kapsamında geliştirilmiş bir kütüphane otomasyon sistemidir. Python kullanılarak geliştirilmiş olup, arka planda SQL veritabanı ile çalışmaktadır.

🚀 Özellikler

Proje aşağıdaki temel modülleri içerir:
* **Üye Yönetimi:** Yeni üye kaydı, düzenleme ve silme işlemleri.
* **Kitap Yönetimi:** Kitap stok takibi ve yönetimi.
* **Ödünç/Teslim İşlemleri:** Kitap verme ve geri alma süreçleri.
* **Ceza Sistemi:** Geciken kitaplar için ceza görüntüleme ve hesaplama.
* **Raporlama:** * Dinamik kitap raporları
    * En çok ödünç alınan kitaplar
    * Geciken kitapların listesi
    * Ödünç alma tarihçesi

🛠️ Kurulum ve Çalıştırma

1.  Bu projeyi bilgisayarınıza klonlayın.
2.  `SQL` klasörü içerisindeki veritabanı dosyasını içe aktarın.
3.  `db.py` veya `bağlantı.txt` içerisindeki veritabanı bağlantı ayarlarını kendi sisteminize göre düzenleyin.
4.  Uygulamayı başlatmak için:
    giriş ekranı için
    python login.py
    ```

📂 Dosya Yapısı

* `Rapor/`: Proje teknik raporu.
* `SQL/`: Veritabanı kurulum dosyaları.
* `db.py`: Veritabanı bağlantı modülü.

### 1. Gerekli Kütüphanelerin Yüklenmesi
Projenin çalışması için Python yüklü olmalıdır. Terminal veya CMD ekranında şu komutu çalıştırarak gerekli paketleri yükleyin:


pip install mysql-connector-python pandas openpyxl reportlab

### 2. Veritabanı Kurulumu
1)MySQL yönetim panelinizi (phpMyAdmin) açın.
2)kutuphane_db adında boş bir veritabanı oluşturun.
3)Proje dosyasındaki kutuphane_db.sql dosyasını içeri aktarın (Import).

### 3. Bağlantı Ayarları
db.py dosyasını açın ve kendi MySQL kullanıcı adı/şifrenizi girin.

### 4. Uygulamayı Başlatma
1)Terminalden proje dizinine gelerek giriş ekranını çalıştırın:
python login.py
(Varsayılan Giriş Bilgileri: Kullanıcı Adı: (admin) Şifre: (1234))

📂 Dosya Yapısı
* login.py: Uygulamanın giriş ekranı.
* menu.py: Rol tabanlı ana menü (Admin/Görevli ayrımı).
* kitap_yonetimi.py: Kitap CRUD işlemleri.
* uye_yonetimi.py: Üye işlemleri ve "Durum Özeti" görüntüleme
* odunc_verme.py & teslim_alma.py: Ödünç/İade süreçleri.
* dinamik_kitap_raporu.py: Filtreli arama ve Excel/PDF çıktı modülü.
* ceza_goruntuleme.py: Üyelerin cezalarını listeleme ekranı.
* db.py: Veritabanı bağlantı modülü.
* SQL/: Veritabanı kurulum dosyaları.

💻 Kullanılan Teknolojiler
* Programlama Dili: Python 3.12
* GUI Kütüphanesi: Tkinter
* Veritabanı: MySQL (MariaDB)
* Veri İşleme & Raporlama: Pandas, ReportLab, OpenPyXL