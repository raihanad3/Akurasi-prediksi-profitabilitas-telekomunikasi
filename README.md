# Akurasi Prediksi Profitabilitas Telekomunikasi

> **Prediksi Arah Fluktuasi Rasio Profitabilitas Perusahaan Sektor Jaringan Telekomunikasi Indonesia (TLKM, ISAT, EXCL) Melalui Integrasi Data Pasar Keuangan, Makroekonomi, dan Analisis Sentimen Berita Industri.**

---

## 📌 Ringkasan Proyek

Proyek ini bertujuan untuk menguji dan memprediksi akurasi arah fluktuasi rasio profitabilitas (**Return on Assets / ROA, Return on Equity / ROE, dan Net Profit Margin / NPM**) pada 3 emiten utama industri telekomunikasi di Bursa Efek Indonesia (BEI):
1. **TLKM** – PT Telkom Indonesia (Persero) Tbk / Telkomsel
2. **ISAT** – PT Indosat Tbk / Indosat Ooredoo Hutchison
3. **EXCL** – PT XL Axiata Tbk / XLSMART

Industri telekomunikasi sangat sensitif terhadap aksi korporasi, dinamika perang tarif, belanja modal infrastruktur (Capex 5G, fiber optic, AI Cloud data center), serta opini media massa. Repositori ini memuat **pipeline web scraping multi-portal**, modul **NLP lexicon-based financial sentiment analysis berbahasa Indonesia**, serta **dataset sentimen berita bersih terkurasi** siap latih (*model-ready*) yang diselaraskan secara kuartalan (*quarterly aligned*).

---

## 📊 Ringkasan Dataset Sentimen Bersih

Semua dataset yang telah melalui tahap *scraping*, pemfilteran *noise* entitas emiten tidak relevan, standardisasi tanggal ISO-8601, kategorisasi tematik, dan pembobotan polaritas sentimen tersedia di folder [`hasil_data_bersih/`](./hasil_data_bersih/):

- **Total Berita Bersih Terverifikasi**: **1.642 artikel** (dari total 3.288 data mentah awal, 1.646 artikel non-emiten berhasil disaring).
- **Distribusi Emiten**:
  - **TLKM**: 613 artikel (37,3%)
  - **ISAT**: 539 artikel (32,8%)
  - **EXCL**: 490 artikel (29,8%)
- **Cakupan Waktu**: **23 September 2004 s.d. 27 Oktober 2026** (146 kuarter fiskal, dengan 87,1% data terkonsentrasi pada era 2021–2026).
- **Sumber Data (7 Portal Bisnis & Pasar Modal Indonesia)**:
  1. **CNBC Indonesia** (576 artikel)
  2. **Kontan** (466 artikel)
  3. **Bisnis.com** (296 artikel)
  4. **Investor.id** (103 artikel)
  5. **Katadata** (102 artikel)
  6. **Detik Finance** (51 artikel)
  7. **EmitenNews** (48 artikel)

---

## 📁 Struktur Direktori Repositori

```text
├── hasil_data_bersih/
│   ├── DATASET_SENTIMEN_BERITA_TELEKOMUNIKASI_MASTER.xlsx   <- Master Excel 6 sheets (Data bersih, sentimen kuartalan, per emiten)
│   ├── DATASET_SENTIMEN_BERITA_TELEKOMUNIKASI_MASTER.csv    <- Master CSV seluruh berita bersih (1.642 baris)
│   ├── FITUR_SENTIMEN_KUARTALAN_TLKM_ISAT_EXCL.csv          <- Agregasi kuartalan 146 periode (TLKM, ISAT, EXCL)
│   ├── berita_sentimen_TLKM_bersih.csv                      <- Dataset berita khusus TLKM (613 baris)
│   ├── berita_sentimen_ISAT_bersih.csv                      <- Dataset berita khusus ISAT (539 baris)
│   ├── berita_sentimen_EXCL_bersih.csv                      <- Dataset berita khusus EXCL (490 baris)
│   └── README.md                                            <- Dokumentasi lengkap kamus data dan metodologi
├── nlp/
│   ├── __init__.py
│   ├── indonesian_financial_lexicon.py                      <- Kamus leksikon finansial Indonesia (bobot sentimen & tema)
│   └── sentiment_analyzer.py                                <- Engine pembobotan polaritas NLP & rolling aggregate
├── scrapers/
│   ├── __init__.py
│   ├── cnbc_scraper.py                                      <- Scraper portal CNBC Indonesia (API & HTML parsing)
│   ├── kontan_scraper.py                                    <- Scraper portal Kontan.co.id
│   └── multiportal_scraper.py                               <- Scraper portal Bisnis, Katadata, Detik, Investor, EmitenNews
├── data/
│   └── raw/                                                 <- Data mentah hasil scraping per portal
├── preprocessing.py                                         <- Script preprocessing pembersihan data & ekstraksi sentimen
├── main_news_sentiment.py                                   <- Script orkestrasi penarikan & pemrosesan berita otomatis
├── requirements.txt                                         <- Dependensi library Python
└── README.md                                                <- Dokumentasi utama proyek
```

---

## ⚙️ Metodologi Preprocessing & Sentimen NLP

Pipeline pada [`preprocessing.py`](./preprocessing.py) menjalankan tahapan:
1. **Deduplikasi**: Mengeliminasi duplikasi judul artikel dan URL lintas portal berita.
2. **Entity Validation & Anti-Noise Filtering**: Menghapus artikel yang hanya menyebut emiten lain (misalnya sektor perbankan BBCA/BBRI atau komoditas) tanpa ada konteks operasional telekomunikasi TLKM/ISAT/EXCL.
3. **Date Normalization & Fiscal Quartering**: Mengonversi format tanggal lokal Indonesia (`27 Oktober 2026`) menjadi format ISO-8601 (`2026-10-27T00:00:00Z`) dan memetakannya ke periode kuartal fiskal (`2026Q4`).
4. **Lexicon-Based Financial Sentiment Scoring**:
   - Memanfaatkan leksikon terminologi pasar modal Indonesia (laba, rugi, dividen, capex, arpu, akuisisi, merger, dsb.).
   - Menghasilkan nilai sentimen terstandarisasi $[-1.0, +1.0]$ serta label polaritas (`positif`, `netral`, `negatif`).
5. **Thematic Categorization**: Mengidentifikasi tema artikel (`kinerja_keuangan`, `merger_akuisisi`, `dividen_saham`, `infrastruktur_5g`, `tarif_persaingan`).
6. **Quarterly Feature Aggregation**: Mengagregasikan rata-rata skor sentimen, rasio berita positif, dan volume berita per kuarter untuk dijadikan variabel independen prediksi profitabilitas.

---

## 🚀 Panduan Menjalankan

### 1. Kloning Repositori & Instalasi Dependensi
```bash
git clone https://github.com/raihanad3/Akurasi-prediksi-profitabilitas-telekomunikasi.git
cd Akurasi-prediksi-profitabilitas-telekomunikasi
pip install -r requirements.txt
```

### 2. Menjalankan Preprocessing
Untuk memproses ulang data mentah dan menghasilkan file data bersih terbaru:
```bash
python preprocessing.py
```

### 3. Menjalankan Scraping Berita Baru
Untuk menarik berita terkini dari 7 portal:
```bash
python main_news_sentiment.py
```

---

## ☁️ Kesiapan Integrasi Cloud (Microsoft Azure)

Dataset dalam format CSV dan Excel pada direktori `hasil_data_bersih/` telah distandardisasi agar siap diintegrasikan ke arsitektur Cloud Computing Microsoft Azure:
- **Azure Blob Storage / Data Lake Storage Gen2**: Penyimpanan dataset terstruktur `FITUR_SENTIMEN_KUARTALAN_TLKM_ISAT_EXCL.csv` sebagai sumber data analisis.
- **Azure Data Factory / Synapse**: Orkestrasi penggabungan data sentimen dengan data fundamental laporan keuangan emiten dan indikator makroekonomi (BI-Rate, inflasi, kurs USD/IDR).
- **Azure Machine Learning**: Pelatihan model regresi / klasifikasi (*Random Forest, XGBoost, LSTM*) untuk mengevaluasi akurasi prediksi pergerakan rasio profitabilitas.

---

## 📄 Lisensi & Kontributor

- **Mata Kuliah**: Teknologi Cloud untuk Big Data dan Data Analitik (Semester 5)
- **Topik Proyek**: Prediksi Profitabilitas Perusahaan Telekomunikasi Indonesia (TLKM, ISAT, EXCL)
- **Repositori GitHub**: [raihanad3/Akurasi-prediksi-profitabilitas-telekomunikasi](https://github.com/raihanad3/Akurasi-prediksi-profitabilitas-telekomunikasi)
