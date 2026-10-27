# Dokumentasi Data Sentimen Berita Industri Telekomunikasi (TLKM, ISAT, EXCL)

Folder **`hasil_data_bersih/`** memuat kumpulan data hasil penarikan (*web scraping*) dan pembersihan intensif (*data preprocessing & NLP sentiment analysis*) terkait berita industri telekomunikasi Indonesia pada tiga emiten utama di Bursa Efek Indonesia (BEI):
1. **TLKM** : PT Telkom Indonesia (Persero) Tbk / Telkomsel
2. **ISAT** : PT Indosat Tbk / Indosat Ooredoo Hutchison
3. **EXCL** : PT XL Axiata Tbk / XLSMART

Dataset ini dirancang khusus untuk mendukung penelitian prediksi fluktuasi rasio profitabilitas (**ROA, ROE, Net Profit Margin**) berbasis integrasi data fundamental, pasar keuangan, dan sentimen berita.

---

## 1. Asal Sumber Data (Data Sources)

Data dikumpulkan dari **7 portal berita ekonomi, bisnis, dan pasar modal terkemuka di Indonesia** guna memperoleh sudut pandang informasi yang komprehensif, obyektif, dan kredibel:

| No | Portal Berita | Domain | Karakteristik Liputan | Jumlah Artikel Bersih |
|---|---|---|---|---|
| 1 | **CNBC Indonesia** *(Rekomendasi Utama)* | `cnbcindonesia.com` | Liputan pasar saham real-time (*Market*), teknologi (*Tech*), ARPU pelanggan, dan data center AI. | **576 artikel** (35,1%) |
| 2 | **Kontan** | `kontan.co.id` | Rujukan utama investor saham; memuat analisis laba bersih emiten, dividen, dan rekomendasi analis. | **466 artikel** (28,4%) |
| 3 | **Bisnis.com** | `bisnis.com` | Media ekonomi otoritatif; mengulas aksi korporasi emiten, merger, regulasi, dan belanja modal (*capex*). | **296 artikel** (18,0%) |
| 4 | **Investor.id** | `investor.id` | Harian pasar modal (*Investor Daily*); memuat riset sekuritas, valuasi emiten, dan target harga saham. | **103 artikel** (6,3%) |
| 5 | **Katadata** | `katadata.co.id` | Analisis mendalam data industri digital, valuasi emiten telko, serta faktor makroekonomi (kurs & suku bunga). | **102 artikel** (6,2%) |
| 6 | **Detik Finance** | `finance.detik.com` | Sentimen makroekonomi, tren tarif internet seluler, dan dinamika konsumen telekomunikasi. | **51 artikel** (3,1%) |
| 7 | **EmitenNews** | `emitennews.com` | Keterbukaan informasi Bursa Efek Indonesia (IDX), pengumuman RUPS, dividen, dan aksi korporasi. | **48 artikel** (2,9%) |
| **TOTAL** | **7 Portal Media** | - | **Dataset Terverifikasi & Bebas Noise** | **1.642 artikel** (100%) |

---

## 2. Rentang Waktu Data (Time Horizon & Temporal Coverage)

- **Rentang Tanggal Kalender**: **23 September 2004 s.d. 27 Oktober 2026**
- **Rentang Periode Kuarter Fiskal**: **Q3 2004 s.d. Q4 2026** (mencakup 146 kuarter terpisah)
- **Kepadatan Terbesar (Periode Observasi Aktif)**:
  Sekitar **87,1% (1.431 artikel)** berada pada rentang **tahun 2021 hingga 2026**, yang merupakan periode paling dinamis dalam industri telekomunikasi Indonesia, meliputi:
  - Integrasi pasca-merger Indosat Ooredoo dan Hutchison 3 (IOH).
  - Konsolidasi XL Axiata dengan Link Net dan rencana merger XLSMART.
  - Pembentukan entitas infrastruktur serat optik Telkom (*Infraco* / Telkom Data Ekosistem / NeutraDC).
  - Ekspansi masif belanja modal 5G dan pembangunan pusat data kecerdasan buatan (*AI Cloud*).

### Sebaran Berita per Tahun
| Tahun | Jumlah Artikel | Keterangan Peristiwa Industri Utama |
|---|---|---|
| **2004 - 2017** | 68 artikel | Fase historis ekspansi 3G, IPO, dan akuisisi Axis oleh XL Axiata (2014). |
| **2018 - 2020** | 145 artikel | Fase perang tarif data seluler, penurunan SMS/Voice ke layanan data internet, dan pandemi COVID-19. |
| **2021** | 126 artikel | Implementasi awal jaringan 5G komersial di Indonesia. |
| **2022** | 131 artikel | Peresmian merger Indosat Ooredoo Hutchison (IOH) senilai US$ 6 miliar. |
| **2023** | 128 artikel | Pemulihan ARPU industri dan spin-off IndiHome ke Telkomsel (*Fixed-Mobile Convergence*). |
| **2024** | 256 artikel | Kemitraan strategis Sovereign AI Cloud Indosat-Nvidia, dividen rekor Telkom. |
| **2025** | 300 artikel | Peningkatan profitabilitas emiten telko dan monetisasi pusat data AI. |
| **2026** | 490 artikel | Evaluasi laba kuartal berjalan, konsolidasi XLSmart, dan peluncuran layanan satelit LEO. |
| **Total** | **1.642 artikel** | - |

---

## 3. Daftar File yang Tersedia di Folder Ini

### 1. `DATASET_SENTIMEN_BERITA_TELEKOMUNIKASI_MASTER.xlsx`
File **Microsoft Excel (Multi-Sheet)** berukuran ~1,1 MB yang telah diformat rapi dan terdiri dari 6 lembar kerja (*sheets*):
* **`Semua_Berita_Bersih`**: Seluruh 1.642 artikel berita bersih dengan 20 atribut kolom lengkap.
* **`Sentimen_Kuartalan`**: Tabel ringkasan 146 baris yang mengagregasikan sentimen per kuarter (`TLKM`, `ISAT`, `EXCL`).
* **`TLKM_Telkom`**: Lembar khusus 613 berita emiten Telkom Indonesia.
* **`ISAT_Indosat`**: Lembar khusus 539 berita emiten Indosat Ooredoo Hutchison.
* **`EXCL_XL`**: Lembar khusus 490 berita emiten XL Axiata.
* **`Ringkasan_Statistik`**: Tabel pivot ringkasan sebaran artikel per portal, per tema, dan metrik rata-rata polaritas.

### 2. `DATASET_SENTIMEN_BERITA_TELEKOMUNIKASI_MASTER.csv`
Master dataset dalam format CSV standar (1.642 baris data + 1 header baris) dengan encoding UTF-8, cocok untuk pembacaan langsung di Python (*pandas*), R, SQL, maupun pipeline ETL.

### 3. `FITUR_SENTIMEN_KUARTALAN_TLKM_ISAT_EXCL.csv`
Dataset agregasi berbasis waktu kuartal (**146 baris**). File ini dirancang untuk di-*merge* / di-*join* langsung dengan angka rasio laporan keuangan (seperti ROA, ROE, Net Profit Margin, Debt-to-Equity) menggunakan kunci relasi `Kode_Emiten` dan `Periode_Kuarter`.

### 4. File CSV Spesifik per Emiten
* **`berita_sentimen_TLKM_bersih.csv`** : 613 baris berita Telkom Indonesia.
* **`berita_sentimen_ISAT_bersih.csv`** : 539 baris berita Indosat Ooredoo Hutchison.
* **`berita_sentimen_EXCL_bersih.csv`** : 490 baris berita XL Axiata.

---

## 4. Kamus Data (Data Dictionary)

### A. Struktur Kolom File Master Berita (`DATASET_SENTIMEN_BERITA_TELEKOMUNIKASI_MASTER.csv`)

| No | Nama Kolom | Tipe Data | Contoh Nilai | Deskripsi & Kegunaan |
|---|---|---|---|---|
| 1 | **`Kode_Emiten`** | String | `TLKM`, `ISAT`, `EXCL` | Kode saham resmi emiten di Bursa Efek Indonesia (BEI). |
| 2 | **`Sumber_Portal`** | String | `CNBC Indonesia`, `Kontan`, dll | Nama media penerbit artikel berita. |
| 3 | **`Judul_Berita`** | String | *"Kinerja Solid Telkomsel: Laba Bersih Naik 11,5%"* | Judul artikel yang telah dibersihkan dari watermark dan tag HTML. |
| 4 | **`Ringkasan_Teks`** | String | Ringkasan teks berita | Paragraf pembuka / lead ringkasan berita bersih. |
| 5 | **`Kategori_Topik`** | String | `Profitabilitas & Kinerja Keuangan` | Kategori tema bisnis & industri telekomunikasi (lihat Bagian 5). |
| 6 | **`Fokus_Keuangan`** | Boolean | `True` / `False` | Bernilai `True` jika artikel secara spesifik mengulas laba, pendapatan, atau dividen. |
| 7 | **`Skor_Sentimen`** | Float | `0.4500`, `-0.5000`, `0.0000` | Skor sentimen bernilai kontinu dari `-1.0000` (sangat negatif) hingga `+1.0000` (sangat positif). |
| 8 | **`Label_Sentimen`** | String | `Positif`, `Netral`, `Negatif` | Klasifikasi sentimen diskret: `Positif` ($> +0.15$), `Negatif` ($< -0.15$), `Netral` ($-0.15 \leq x \leq +0.15$). |
| 9 | **`Keyakinan_Sentimen`**| Float | `0.6500` | Rasio densitas kata sentimen terhadap total kata (0.0 s.d. 1.0). |
| 10 | **`Tingkat_Subjektivitas`**| Float | `0.3200` | Skor subjektivitas teks (0.0 = faktual objektif, 1.0 = sarat opini). |
| 11 | **`Kata_Kunci_Positif`**| String | `laba, naik, tumbuh` | Kata bernada positif yang terdeteksi oleh leksikon NLP (jika tidak ada: `-`). |
| 12 | **`Kata_Kunci_Negatif`**| String | `utang, beban, merosot` | Kata bernada negatif yang terdeteksi oleh leksikon NLP (jika tidak ada: `-`). |
| 13 | **`Waktu_Publikasi`** | Datetime | `2024-03-25 10:15:00` | Waktu dan jam publikasi standar ISO-8601. |
| 14 | **`Tanggal`** | Date | `2024-03-25` | Tanggal penerbitan (`YYYY-MM-DD`). |
| 15 | **`Tahun`** | Integer | `2024` | Tahun penerbitan berita. |
| 16 | **`Kuarter`** | Integer | `1`, `2`, `3`, `4` | Kuarter kalender (1: Jan-Mar, 2: Apr-Jun, 3: Jul-Sep, 4: Okt-Des). |
| 17 | **`Bulan`** | Integer | `3` | Bulan kalender (1 s.d. 12). |
| 18 | **`Periode_Laporan`** | String | `Q1 2024` | Kuarter finansial terformat standar untuk integrasi laporan keuangan. |
| 19 | **`Jumlah_Kata`** | Integer | `18` | Total kata dalam judul dan ringkasan berita. |
| 20 | **`URL_Sumber`** | String | `https://...` | Tautan URL sumber berita asli untuk validasi atau audit teks. |

---

### B. Struktur Kolom Fitur Kuartalan (`FITUR_SENTIMEN_KUARTALAN_TLKM_ISAT_EXCL.csv`)

| Nama Kolom | Tipe Data | Deskripsi Kegunaan untuk Machine Learning |
|---|---|---|
| **`Kode_Emiten`** | String | Kunci penggabungan (*join key*) emiten (`TLKM`, `ISAT`, `EXCL`). |
| **`Periode_Kuarter`** | String | Kunci penggabungan periode kuartal (misal: `Q1 2024`, `Q2 2024`). |
| **`Total_Berita`** | Integer | Volume artikel berita yang diterbitkan pada kuarter tersebut. |
| **`Rata_Rata_Skor_Sentimen`** | Float | Rata-rata skor sentimen polaritas pada kuarter bersangkutan (-1.0 s.d. +1.0). |
| **`Std_Deviasi_Sentimen`** | Float | Tingkat volatilitas/variasi opini pasar pada kuarter tersebut. |
| **`Rata_Rata_Keyakinan`** | Float | Rata-rata kekuatan sinyal kata sentimen pada kuarter tersebut. |
| **`Rata_Rata_Subjektivitas`** | Float | Derajat subjektivitas pemberitaan pada kuarter tersebut. |
| **`Jumlah_Berita_Positif`** | Integer | Frekuensi berita bernada positif dalam kuarter. |
| **`Jumlah_Berita_Negatif`** | Integer | Frekuensi berita bernada negatif dalam kuarter. |
| **`Jumlah_Berita_Netral`** | Integer | Frekuensi berita netral/deskriptif dalam kuarter. |
| **`Jumlah_Berita_Fokus_Keuangan`** | Integer | Frekuensi berita yang secara khusus membahas laba, pendapatan, dan dividen. |
| **`Sentimen_Khusus_Keuangan`** | Float | Skor sentimen rata-rata khusus pada artikel laba & dividen. |
| **`Rasio_Positif`** | Float | Proporsi berita positif terhadap total berita kuarter (`Jumlah_Positif / Total_Berita`). |
| **`Rasio_Negatif`** | Float | Proporsi berita negatif terhadap total berita kuarter (`Jumlah_Negatif / Total_Berita`). |
| **`Polaritas_Bersih`** | Float | **Sinyal Sentimen Utama** (`Rasio_Positif - Rasio_Negatif`). Nilai positif menunjukkan optimisme pasar; nilai negatif menunjukkan tekanan pesimisme pasar. |

---

## 5. Klasifikasi Kategori Topik Finansial & Industri

Seluruh berita telah diklasifikasikan ke dalam 8 kategori tema:

1. **`Infrastruktur, Data Center & AI` (531 artikel)**: Pembangunan pusat data AI (NeutraDC, BDx), belanja modal (*capex*), modernisasi jaringan fiber optic, BTS, dan 5G.
2. **`Industri Telekomunikasi Umum` (486 artikel)**: Program kemitraan, layanan pelanggan, penghargaan industri, dan inisiatif transformasi digital.
3. **`Profitabilitas & Kinerja Keuangan` (203 artikel)**: Realisasi laba bersih, pendapatan (*revenue*), EBITDA, pergerakan margin profitabilitas (NPM, ROE, ROA).
4. **`Aksi Korporasi & Merger` (165 artikel)**: Integrasi Indosat-Tri, konsolidasi XL-Smartfren, *spin-off fiber optic* Telkom Infraco, dan program *buyback* saham.
5. **`Pasar Modal & Saham` (152 artikel)**: Target harga saham oleh analis sekuritas, pergerakan indeks IHSG, dan arus modal investor asing (*net foreign buy/sell*).
6. **`Dividen & Shareholder Value` (57 artikel)**: *Dividend payout ratio*, dividen interim, *cum-date*, dan imbal hasil (*yield*).
7. **`Tarif & Pelanggan Seluler` (43 artikel)**: Dinamika ARPU (*Average Revenue Per User*), kebijakan kuota data, dan pertumbuhan jumlah pelanggan aktif.
8. **`Faktor Makroekonomi` (5 artikel)**: Pengaruh fluktuasi kurs Rupiah/USD dan suku bunga BI Rate terhadap beban keuangan emiten telko.

---

## 6. Metodologi Data Preprocessing & Pembersihan Teks

Sebelum data diekspor ke folder ini, tahapan pembersihan dilakukan melalui skrip `preprocess_scraped_data.py`:

```
[Raw Data dari 7 Portal] (3.293 baris)
           │
           ▼
[1. Text Cleaning & Unescaping]
   • Menghapus kode HTML (&amp;, &quot;, dll)
   • Membuang watermark portal ("KONTAN.CO.ID - JAKARTA.", "Bisnis.com -")
           │
           ▼
[2. Strict Entity Relevance Filtering]
   • Memfilter dan membuang 1.646 artikel noise yang membahas emiten lain 
     (BCA, BNI, BRI, BUMI, Pegadaian, Astra, dll)
   • Memastikan artikel menyebut Telkom, Indosat, atau XL Axiata
           │
           ▼
[3. Deduplikasi Tingkat Lanjut]
   • Menghapus artikel ganda berdasarkan kesamaan URL dan judul berita
           │
           ▼
[4. Standardisasi Waktu & Kuarter]
   • Penyeragaman ke format ISO-8601 (YYYY-MM-DD HH:MM:SS)
   • Ekstraksi Tanggal, Tahun, Bulan, dan Kuarter (Q1-Q4)
           │
           ▼
[5. NLP Sentiment Scoring Berbobot]
   • Pembobotan kata positif (+1 s.d. +2) dan negatif (-1 s.d. -2)
   • Negation Handling: membalik polaritas jika ada kata ingkar ("tidak naik" -> negatif)
           │
           ▼
[DATASET BERSIH SIAP PAKAI] (1.642 baris artikel & 146 baris kuartalan)
```

---

## 7. Distribusi Sentimen Akhir

Dari total 1.642 artikel bersih:
- **Positif**: **468 artikel (28,5%)**
- **Netral**: **1.115 artikel (67,9%)**
- **Negatif**: **59 artikel (3,6%)**
- **Rata-Rata Skor Sentimen Keseluruhan**: **+0,2500** (Sentimen industri telekomunikasi secara umum didominasi optimisme terhadap ekspansi data center AI dan perbaikan laba).

---

## 8. Cara Menggunakan Data Ini untuk Pemodelan

Untuk menggabungkan fitur sentimen berita dengan data rasio keuangan dalam Python:

```python
import pandas as pd

# 1. Baca data fitur sentimen kuartalan
df_sentimen = pd.read_csv('hasil_data_bersih/FITUR_SENTIMEN_KUARTALAN_TLKM_ISAT_EXCL.csv')

# 2. Baca data rasio profitabilitas keuangan Anda (misal memuat ROE, ROA, NPM)
# df_rasio = pd.read_csv('data_rasio_keuangan.csv')

# 3. Gabungkan (Merge) menggunakan Kode_Emiten dan Periode_Kuarter
# df_final = pd.merge(df_rasio, df_sentimen, on=['Kode_Emiten', 'Periode_Kuarter'], how='inner')

# 4. Kolom 'Polaritas_Bersih', 'Rata_Rata_Skor_Sentimen', dan 'Total_Berita' 
#    siap digunakan sebagai fitur prediktor Machine Learning.
```
