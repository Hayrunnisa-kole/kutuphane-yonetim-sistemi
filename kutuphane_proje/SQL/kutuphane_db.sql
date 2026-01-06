-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Anamakine: 127.0.0.1
-- Üretim Zamanı: 06 Oca 2026, 15:40:45
-- Sunucu sürümü: 10.4.32-MariaDB
-- PHP Sürümü: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Veritabanı: `kutuphane_db`
--

DELIMITER $$
--
-- Yordamlar
--
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_KitapEkleVeyaGuncelle` (IN `p_KitapAdi` VARCHAR(100), IN `p_Yazar` VARCHAR(100), IN `p_BasimYili` INT, IN `p_Adet` INT)   BEGIN
    DECLARE v_KitapID INT DEFAULT NULL;

    SELECT KitapID
    INTO v_KitapID
    FROM KITAP
    WHERE KitapAdi = p_KitapAdi
      AND Yazar = p_Yazar
    LIMIT 1;

    IF v_KitapID IS NOT NULL THEN
        UPDATE KITAP
        SET
            BasimYili = p_BasimYili,
            ToplamAdet = ToplamAdet + p_Adet,
            MevcutAdet = MevcutAdet + p_Adet
        WHERE KitapID = v_KitapID;

    ELSE
        INSERT INTO KITAP
        (KitapAdi, Yazar, BasimYili, ToplamAdet, MevcutAdet)
        VALUES
        (p_KitapAdi, p_Yazar, p_BasimYili, p_Adet, p_Adet);
    END IF;
END$$

CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_KitapTeslimAl` (IN `p_OduncID` INT, IN `p_TeslimTarihi` DATE)   BEGIN
    DECLARE v_KitapID INT;
    DECLARE v_GecikmeGun INT;
    DECLARE v_Ceza DECIMAL(10,2);

    -- 1. Ödünç bilgilerini al (Henüz teslim edilmemiş olanı)
    SELECT KitapID, DATEDIFF(p_TeslimTarihi, SonTeslimTarihi)
    INTO v_KitapID, v_GecikmeGun
    FROM ODUNC
    WHERE OduncID = p_OduncID
      AND TeslimTarihi IS NULL;

    -- 2. Teslim tarihini güncelle (Python'dan gelen tarihi kullan)
    UPDATE ODUNC
    SET TeslimTarihi = p_TeslimTarihi
    WHERE OduncID = p_OduncID;

    -- 3. Kitap stoğunu artır
    UPDATE KITAP
    SET MevcutAdet = MevcutAdet + 1
    WHERE KitapID = v_KitapID;

    -- 4. Gecikme varsa ceza ekle
    IF v_GecikmeGun > 0 THEN
        SET v_Ceza = v_GecikmeGun * 5; -- Günlük 5 TL

        -- Tablonda 'CezaTarihi' sütunu artık var, oraya bugünü yazıyoruz
        INSERT INTO CEZA (OduncID, Tutar, CezaTarihi)
        VALUES (p_OduncID, v_Ceza, CURDATE());
    END IF;
END$$

CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_UyeOzetRaporu` (IN `p_UyeID` INT)   BEGIN
    DECLARE v_AktifOdunc INT;
    DECLARE v_GecikmisOdunc INT;
    DECLARE v_AdSoyad VARCHAR(120);
    DECLARE v_Borc DECIMAL(10,2);

    -- Üye bilgileri
    SELECT CONCAT(Ad, ' ', Soyad), ToplamBorc
    INTO v_AdSoyad, v_Borc
    FROM UYE
    WHERE UyeID = p_UyeID;

    -- Aktif ödünç sayısı
    SELECT COUNT(*) INTO v_AktifOdunc
    FROM ODUNC
    WHERE UyeID = p_UyeID
      AND TeslimTarihi IS NULL;

    -- Gecikmiş ödünç sayısı
    SELECT COUNT(*) INTO v_GecikmisOdunc
    FROM ODUNC
    WHERE UyeID = p_UyeID
      AND TeslimTarihi IS NULL
      AND SonTeslimTarihi < CURDATE();

    -- Rapor çıktısı
    SELECT
        v_AdSoyad AS Uye,
        v_AktifOdunc AS AktifOduncSayisi,
        v_GecikmisOdunc AS GecikmisOduncSayisi,
        v_Borc AS ToplamBorc;
END$$

CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_YeniOduncVer` (IN `p_UyeID` INT, IN `p_KitapID` INT, IN `p_KullaniciID` INT)   BEGIN
    DECLARE aktif_odunc INT DEFAULT 0;
    DECLARE stok INT DEFAULT 0;

    SELECT COUNT(*) INTO aktif_odunc
    FROM ODUNC
    WHERE UyeID = p_UyeID
      AND TeslimTarihi IS NULL;

    SELECT MevcutAdet INTO stok
    FROM KITAP
    WHERE KitapID = p_KitapID;

    IF aktif_odunc < 5 AND stok > 0 THEN
        INSERT INTO ODUNC
        (UyeID, KitapID, KullaniciID, OduncTarihi, SonTeslimTarihi)
        VALUES
        (p_UyeID, p_KitapID, p_KullaniciID,
         CURDATE(), DATE_ADD(CURDATE(), INTERVAL 15 DAY));
    END IF;
END$$

DELIMITER ;

-- --------------------------------------------------------

--
-- Tablo için tablo yapısı `ceza`
--

CREATE TABLE `ceza` (
  `CezaID` int(11) NOT NULL,
  `OduncID` int(11) DEFAULT NULL,
  `Tutar` decimal(10,2) DEFAULT NULL,
  `CezaTarihi` date DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Tablo döküm verisi `ceza`
--

INSERT INTO `ceza` (`CezaID`, `OduncID`, `Tutar`, `CezaTarihi`) VALUES
(1, 3, 25.00, '2026-01-06');

--
-- Tetikleyiciler `ceza`
--
DELIMITER $$
CREATE TRIGGER `TR_CEZA_BORC_ARTIR` AFTER INSERT ON `ceza` FOR EACH ROW UPDATE UYE
SET ToplamBorc = ToplamBorc + NEW.Tutar
WHERE UyeID = (
    SELECT UyeID FROM ODUNC WHERE OduncID = NEW.OduncID
)
$$
DELIMITER ;
DELIMITER $$
CREATE TRIGGER `trg_ceza_insert_log` AFTER INSERT ON `ceza` FOR EACH ROW BEGIN
    DECLARE vUyeID INT;

    SELECT UyeID
    INTO vUyeID
    FROM ODUNC
    WHERE OduncID = NEW.OduncID;

    INSERT INTO LOG (TabloAdi, IslemTipi, Aciklama)
    VALUES (
        'CEZA',
        'INSERT',
        CONCAT(
            'UyeID=', vUyeID,
            ', OduncID=', NEW.OduncID,
            ', Ceza=', NEW.Tutar
        )
    );
END
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Tablo için tablo yapısı `kitap`
--

CREATE TABLE `kitap` (
  `KitapID` int(11) NOT NULL,
  `KitapAdi` varchar(100) DEFAULT NULL,
  `Yazar` varchar(100) DEFAULT NULL,
  `Kategori` varchar(50) DEFAULT NULL,
  `BasimYili` int(11) DEFAULT NULL,
  `ToplamAdet` int(11) DEFAULT NULL,
  `MevcutAdet` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Tablo döküm verisi `kitap`
--

INSERT INTO `kitap` (`KitapID`, `KitapAdi`, `Yazar`, `Kategori`, `BasimYili`, `ToplamAdet`, `MevcutAdet`) VALUES
(3, 'Suç ve Ceza', 'Dostoyevski', 'Klasik', 1858, 8, 7),
(8, 'Tutunamayanlar', 'Oğuz Atay', 'Roman', 1972, 5, 2),
(9, 'Kürk Mantolu Madonna', 'Sabahattin Ali', 'Roman', 1943, 6, 3),
(10, 'Saatleri Ayarlama Enstitüsü', 'Ahmet Hamdi Tanpınar', 'Roman', 1961, 4, 2),
(11, '1984', 'George Orwell', 'Distopya', 1949, 8, 6),
(12, 'Hayvan Çiftliği', 'George Orwell', 'Siyasi Roman', 1945, 7, 2),
(13, 'Suç ve Ceza', 'Fyodor Dostoyevski', 'Roman', 1866, 5, 2),
(14, 'Sefiller', 'Victor Hugo', 'Klasik', 1862, 6, 2),
(15, 'Simyacı', 'Paulo Coelho', 'Felsefi Roman', 1988, 10, 9),
(16, 'Beyaz Diş', 'Jack London', 'Macera', 1906, 4, 3),
(17, 'Çalıkuşu', 'Reşat Nuri Güntekin', 'Roman', 1922, 5, 5);

-- --------------------------------------------------------

--
-- Tablo için tablo yapısı `kullanici`
--

CREATE TABLE `kullanici` (
  `KullaniciID` int(11) NOT NULL,
  `KullaniciAdi` varchar(50) NOT NULL,
  `Sifre` varchar(50) NOT NULL,
  `Rol` enum('Admin','Gorevli') NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Tablo döküm verisi `kullanici`
--

INSERT INTO `kullanici` (`KullaniciID`, `KullaniciAdi`, `Sifre`, `Rol`) VALUES
(1, 'admin', '1234', 'Admin'),
(3, 'gorevli1', '1234', 'Gorevli'),
(4, 'gorevli2', '1234', 'Gorevli'),
(5, 'gorevli3', '1234', 'Gorevli');

-- --------------------------------------------------------

--
-- Tablo için tablo yapısı `log`
--

CREATE TABLE `log` (
  `LogID` int(11) NOT NULL,
  `TabloAdi` varchar(50) DEFAULT NULL,
  `IslemTipi` varchar(50) DEFAULT NULL,
  `IslemZamani` datetime DEFAULT current_timestamp(),
  `Aciklama` varchar(255) DEFAULT NULL,
  `KullaniciID` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Tablo döküm verisi `log`
--

INSERT INTO `log` (`LogID`, `TabloAdi`, `IslemTipi`, `IslemZamani`, `Aciklama`, `KullaniciID`) VALUES
(1, 'ODUNC', 'INSERT', '2026-01-01 18:13:01', 'UyeID=5, KitapID=5 için ödünç verildi', NULL),
(2, 'ODUNC', 'UPDATE', '2026-01-01 18:14:25', 'OduncID=5 teslim alındı', NULL),
(3, 'ODUNC', 'INSERT', '2026-01-01 18:33:12', 'UyeID=11, KitapID=12 için ödünç verildi', NULL),
(4, 'ODUNC', 'INSERT', '2026-01-01 18:33:19', 'UyeID=15, KitapID=14 için ödünç verildi', NULL),
(5, 'ODUNC', 'INSERT', '2026-01-01 18:33:25', 'UyeID=6, KitapID=12 için ödünç verildi', NULL),
(6, 'ODUNC', 'INSERT', '2026-01-01 18:33:31', 'UyeID=10, KitapID=9 için ödünç verildi', NULL),
(7, 'ODUNC', 'INSERT', '2026-01-01 18:33:43', 'UyeID=12, KitapID=8 için ödünç verildi', NULL),
(8, 'ODUNC', 'INSERT', '2026-01-01 18:33:50', 'UyeID=10, KitapID=8 için ödünç verildi', NULL),
(9, 'ODUNC', 'INSERT', '2026-01-01 18:33:56', 'UyeID=14, KitapID=14 için ödünç verildi', NULL),
(10, 'ODUNC', 'UPDATE', '2026-01-01 18:34:09', 'OduncID=6 teslim alındı', NULL),
(11, 'ODUNC', 'INSERT', '2026-01-01 18:39:37', 'UyeID=6, KitapID=12 için ödünç verildi', NULL),
(12, 'ODUNC', 'INSERT', '2026-01-01 18:39:53', 'UyeID=6, KitapID=13 için ödünç verildi', NULL),
(13, 'ODUNC', 'UPDATE', '2026-01-01 18:40:13', 'OduncID=11 teslim alındı', NULL),
(14, 'ODUNC', 'UPDATE', '2026-01-01 18:40:24', 'OduncID=15 teslim alındı', NULL),
(15, 'CEZA', 'INSERT', '2026-01-06 17:22:38', 'UyeID=1, OduncID=3, Ceza=25.00', NULL);

-- --------------------------------------------------------

--
-- Tablo için tablo yapısı `odunc`
--

CREATE TABLE `odunc` (
  `OduncID` int(11) NOT NULL,
  `UyeID` int(11) DEFAULT NULL,
  `KitapID` int(11) DEFAULT NULL,
  `KullaniciID` int(11) DEFAULT NULL,
  `OduncTarihi` date DEFAULT NULL,
  `SonTeslimTarihi` date DEFAULT NULL,
  `TeslimTarihi` date DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Tablo döküm verisi `odunc`
--

INSERT INTO `odunc` (`OduncID`, `UyeID`, `KitapID`, `KullaniciID`, `OduncTarihi`, `SonTeslimTarihi`, `TeslimTarihi`) VALUES
(3, 1, 3, 1, '2025-12-27', '2026-01-11', NULL),
(7, 11, 12, 1, '2026-01-01', '2026-01-16', NULL),
(8, 15, 14, 1, '2026-01-01', '2026-01-16', NULL),
(9, 6, 12, 1, '2026-01-01', '2026-01-16', NULL),
(10, 10, 9, 1, '2026-01-01', '2026-01-16', NULL),
(11, 12, 8, 1, '2026-01-01', '2026-01-16', '2026-01-01'),
(12, 10, 8, 1, '2026-01-01', '2026-01-16', NULL),
(13, 14, 14, 1, '2026-01-01', '2026-01-16', NULL),
(14, 6, 12, 1, '2026-01-01', '2026-01-16', NULL),
(15, 6, 13, 1, '2026-01-01', '2026-01-16', '2026-01-01');

--
-- Tetikleyiciler `odunc`
--
DELIMITER $$
CREATE TRIGGER `TR_ODUNC_STOK_ARTIR` AFTER UPDATE ON `odunc` FOR EACH ROW UPDATE KITAP
SET MevcutAdet = MevcutAdet + 1
WHERE KitapID = NEW.KitapID
AND OLD.TeslimTarihi IS NULL
AND NEW.TeslimTarihi IS NOT NULL
$$
DELIMITER ;
DELIMITER $$
CREATE TRIGGER `TR_ODUNC_STOK_AZALT` AFTER INSERT ON `odunc` FOR EACH ROW UPDATE KITAP
SET MevcutAdet = MevcutAdet - 1
WHERE KitapID = NEW.KitapID
$$
DELIMITER ;
DELIMITER $$
CREATE TRIGGER `trg_odunc_insert_log` AFTER INSERT ON `odunc` FOR EACH ROW BEGIN
    INSERT INTO LOG (TabloAdi, IslemTipi, Aciklama)
    VALUES (
        'ODUNC',
        'INSERT',
        CONCAT(
            'UyeID=', NEW.UyeID,
            ', KitapID=', NEW.KitapID,
            ' için ödünç verildi'
        )
    );
END
$$
DELIMITER ;
DELIMITER $$
CREATE TRIGGER `trg_odunc_teslim_log` AFTER UPDATE ON `odunc` FOR EACH ROW BEGIN
    IF NEW.TeslimTarihi IS NOT NULL AND OLD.TeslimTarihi IS NULL THEN
        INSERT INTO LOG (TabloAdi, IslemTipi, Aciklama)
        VALUES (
            'ODUNC',
            'UPDATE',
            CONCAT(
                'OduncID=', NEW.OduncID,
                ' teslim alındı'
            )
        );
    END IF;
END
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Tablo için tablo yapısı `uye`
--

CREATE TABLE `uye` (
  `UyeID` int(11) NOT NULL,
  `Ad` varchar(50) NOT NULL,
  `Soyad` varchar(50) NOT NULL,
  `Telefon` varchar(20) DEFAULT NULL,
  `Email` varchar(100) DEFAULT NULL,
  `ToplamBorc` decimal(10,2) DEFAULT 0.00
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Tablo döküm verisi `uye`
--

INSERT INTO `uye` (`UyeID`, `Ad`, `Soyad`, `Telefon`, `Email`, `ToplamBorc`) VALUES
(1, 'Hayrunnisa', 'Köle', '05454545454', 'h.nisa@gmail.com', 25.00),
(6, 'Ahmet', 'Yılmaz', '05551234501', 'ahmet.yilmaz@gmail.com', 0.00),
(7, 'Ayşe', 'Demir', '05551234502', 'ayse.demir@gmail.com', 15.00),
(8, 'Mehmet', 'Kaya', '05551234503', 'mehmet.kaya@gmail.com', 0.00),
(9, 'Elif', 'Şahin', '05551234504', 'elif.sahin@gmail.com', 5.00),
(10, 'Can', 'Öztürk', '05551234505', 'can.ozturk@gmail.com', 0.00),
(11, 'Zeynep', 'Aydın', '05551234506', 'zeynep.aydin@gmail.com', 20.00),
(12, 'Burak', 'Koç', '05551234507', 'burak.koc@gmail.com', 0.00),
(13, 'Merve', 'Arslan', '05551234508', 'merve.arslan@gmail.com', 10.00),
(14, 'Emre', 'Çelik', '05551234509', 'emre.celik@gmail.com', 0.00),
(15, 'Buse', 'Karaca', '05551234510', 'buse.karaca@gmail.com', 0.00);

-- --------------------------------------------------------

--
-- Görünüm yapısı durumu `vw_aktif_oduncler`
-- (Asıl görünüm için aşağıya bakın)
--
CREATE TABLE `vw_aktif_oduncler` (
`OduncID` int(11)
,`Uye` varchar(101)
,`KitapAdi` varchar(100)
,`OduncTarihi` date
,`SonTeslimTarihi` date
);

-- --------------------------------------------------------

--
-- Görünüm yapısı `vw_aktif_oduncler`
--
DROP TABLE IF EXISTS `vw_aktif_oduncler`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `vw_aktif_oduncler`  AS SELECT `o`.`OduncID` AS `OduncID`, concat(`u`.`Ad`,' ',`u`.`Soyad`) AS `Uye`, `k`.`KitapAdi` AS `KitapAdi`, `o`.`OduncTarihi` AS `OduncTarihi`, `o`.`SonTeslimTarihi` AS `SonTeslimTarihi` FROM ((`odunc` `o` join `uye` `u` on(`u`.`UyeID` = `o`.`UyeID`)) join `kitap` `k` on(`k`.`KitapID` = `o`.`KitapID`)) WHERE `o`.`TeslimTarihi` is null ;

--
-- Dökümü yapılmış tablolar için indeksler
--

--
-- Tablo için indeksler `ceza`
--
ALTER TABLE `ceza`
  ADD PRIMARY KEY (`CezaID`),
  ADD KEY `OduncID` (`OduncID`);

--
-- Tablo için indeksler `kitap`
--
ALTER TABLE `kitap`
  ADD PRIMARY KEY (`KitapID`);

--
-- Tablo için indeksler `kullanici`
--
ALTER TABLE `kullanici`
  ADD PRIMARY KEY (`KullaniciID`),
  ADD UNIQUE KEY `KullaniciAdi` (`KullaniciAdi`);

--
-- Tablo için indeksler `log`
--
ALTER TABLE `log`
  ADD PRIMARY KEY (`LogID`),
  ADD KEY `fk_log_kullanici` (`KullaniciID`);

--
-- Tablo için indeksler `odunc`
--
ALTER TABLE `odunc`
  ADD PRIMARY KEY (`OduncID`),
  ADD KEY `UyeID` (`UyeID`),
  ADD KEY `KitapID` (`KitapID`),
  ADD KEY `GorevliID` (`KullaniciID`);

--
-- Tablo için indeksler `uye`
--
ALTER TABLE `uye`
  ADD PRIMARY KEY (`UyeID`);

--
-- Dökümü yapılmış tablolar için AUTO_INCREMENT değeri
--

--
-- Tablo için AUTO_INCREMENT değeri `ceza`
--
ALTER TABLE `ceza`
  MODIFY `CezaID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- Tablo için AUTO_INCREMENT değeri `kitap`
--
ALTER TABLE `kitap`
  MODIFY `KitapID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=18;

--
-- Tablo için AUTO_INCREMENT değeri `kullanici`
--
ALTER TABLE `kullanici`
  MODIFY `KullaniciID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- Tablo için AUTO_INCREMENT değeri `log`
--
ALTER TABLE `log`
  MODIFY `LogID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=16;

--
-- Tablo için AUTO_INCREMENT değeri `odunc`
--
ALTER TABLE `odunc`
  MODIFY `OduncID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=16;

--
-- Tablo için AUTO_INCREMENT değeri `uye`
--
ALTER TABLE `uye`
  MODIFY `UyeID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=16;

--
-- Dökümü yapılmış tablolar için kısıtlamalar
--

--
-- Tablo kısıtlamaları `ceza`
--
ALTER TABLE `ceza`
  ADD CONSTRAINT `ceza_ibfk_1` FOREIGN KEY (`OduncID`) REFERENCES `odunc` (`OduncID`);

--
-- Tablo kısıtlamaları `log`
--
ALTER TABLE `log`
  ADD CONSTRAINT `fk_log_kullanici` FOREIGN KEY (`KullaniciID`) REFERENCES `kullanici` (`KullaniciID`);

--
-- Tablo kısıtlamaları `odunc`
--
ALTER TABLE `odunc`
  ADD CONSTRAINT `fk_odunc_kullanici` FOREIGN KEY (`KullaniciID`) REFERENCES `kullanici` (`KullaniciID`),
  ADD CONSTRAINT `odunc_ibfk_1` FOREIGN KEY (`UyeID`) REFERENCES `uye` (`UyeID`),
  ADD CONSTRAINT `odunc_ibfk_2` FOREIGN KEY (`KitapID`) REFERENCES `kitap` (`KitapID`),
  ADD CONSTRAINT `odunc_ibfk_3` FOREIGN KEY (`KullaniciID`) REFERENCES `kullanici` (`KullaniciID`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
