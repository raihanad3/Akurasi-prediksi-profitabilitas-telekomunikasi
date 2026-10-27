"""
Pipeline Preprocessing, Pembersihan Teks, Analisis Sentimen NLP,
dan Ekspor Dataset Akhir ke Format Excel (.xlsx Multi-Sheet) dan CSV.
"""

import os
import re
import html
from datetime import datetime
import pandas as pd
import numpy as np

from nlp.indonesian_financial_lexicon import (
    STRONG_POSITIVE, POSITIVE,
    STRONG_NEGATIVE, NEGATIVE,
    NEGATIONS, INTENSIFIERS, DIMINISHERS
)

# Regex entitas emiten
TLKM_REGEX = re.compile(r'\b(tlkm|telkom|telkomsel|indihome|neutradc|infraco|mitratel)\b', re.IGNORECASE)
ISAT_REGEX = re.compile(r'\b(isat|indosat|ooredoo|hutchison|tri\b|ioh|bdx)\b', re.IGNORECASE)
EXCL_REGEX = re.compile(r'\b(excl|xl\b|axiata|xlsmart|link\s*net|axis)\b', re.IGNORECASE)

UNRELATED_ENTITIES = [
    r'\b(bca|bbca|bni|bbni|bri|bbri|mandiri|bmri|btn|bbtn)\b',
    r'\b(bumi\b|brms|ptba|adaro|adro|antm|inco|medco|medc|untr|harum)\b',
    r'\b(asii|astra|goto|bukalapak|shopee|pegadaian)\b',
    r'\b(unilever|unvr|icbp|indofood|indf|kalbe|klbf|sido)\b',
    r'\b(barito|bren|chandra asri|tpia|pancoran)\b',
]

def clean_html_and_text(raw_text: str) -> str:
    """Membersihkan entitas HTML, markup, dan watermark portal."""
    if not isinstance(raw_text, str) or not raw_text.strip():
        return ""
    text = html.unescape(raw_text)
    text = re.sub(r'<.*?>', ' ', text)
    boilerplate_patterns = [
        r'^kontan\.co\.id\s*-\s*jakarta\.?',
        r'^bisnis\.com\s*,\s*jakarta\s*-?',
        r'^cnbc\s*indonesia\s*,\s*jakarta\s*-?',
        r'^jakarta\s*,\s*investor\.id\s*-?',
        r'^detikfinance\s*-\s*jakarta\.?',
        r'^katadata\s*,\s*jakarta\s*-?',
        r'^emitennews\.com\s*-\s*',
        r'\s*-\s*cnbc\s*indonesia.*$',
        r'\s*-\s*kontan\.co\.id.*$',
        r'\s*-\s*bisnis\.com.*$',
        r'\s*-\s*investor\.id.*$',
        r'\s*-\s*katadata\.co\.id.*$',
        r'\s*-\s*detikfinance.*$',
        r'\s*-\s*emitennews.*$',
    ]
    for pattern in boilerplate_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE).strip()
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def parse_and_standardize_date(date_str: str):
    """Menstandardisasi tanggal ke ISO, Year, Quarter, Month, Fiscal Period."""
    if not date_str or pd.isna(date_str) or str(date_str).strip() in ['', 'None', 'nan']:
        return None, None, None, None, None, None
        
    date_str_clean = str(date_str).strip()
    dt = None
    formats = [
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d',
        '%a, %d %b %Y %H:%M:%S',
        '%a, %d %b %Y %H:%M:%S %Z',
        '%d/%m/%Y %H:%M:%S',
        '%d/%m/%Y',
    ]
    
    match_ts = re.search(r'(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})', date_str_clean)
    if match_ts:
        try:
            y, m, d, H, M, S = [int(x) for x in match_ts.groups()]
            dt = datetime(y, m, d, H, M, S)
        except Exception:
            pass
            
    if dt is None:
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str_clean[:25].strip(), fmt)
                break
            except Exception:
                continue
                
    if dt is None:
        try:
            dt = pd.to_datetime(date_str_clean)
        except Exception:
            return None, None, None, None, None, None

    iso_date = dt.strftime('%Y-%m-%d %H:%M:%S')
    date_only = dt.strftime('%Y-%m-%d')
    year = dt.year
    month = dt.month
    quarter = (month - 1) // 3 + 1
    period = f"Q{quarter} {year}"
    
    return iso_date, date_only, year, quarter, month, period

def check_article_relevance(row):
    """Filter ketat: hanya pertahankan artikel yang relevan dengan emiten."""
    ticker = str(row.get('Ticker', '')).upper()
    title = str(row.get('Title', '')).lower()
    desc = str(row.get('Description', '')).lower()
    full_text = f"{title} {desc}"
    
    has_target = False
    if ticker == 'TLKM':
        has_target = bool(TLKM_REGEX.search(full_text))
    elif ticker == 'ISAT':
        has_target = bool(ISAT_REGEX.search(full_text))
    elif ticker == 'EXCL':
        has_target = bool(EXCL_REGEX.search(full_text))
        
    has_target_in_title = False
    if ticker == 'TLKM' and TLKM_REGEX.search(title):
        has_target_in_title = True
    elif ticker == 'ISAT' and ISAT_REGEX.search(title):
        has_target_in_title = True
    elif ticker == 'EXCL' and EXCL_REGEX.search(title):
        has_target_in_title = True
        
    has_unrelated_in_title = any(re.search(pat, title, re.IGNORECASE) for pat in UNRELATED_ENTITIES)
    if has_unrelated_in_title and not has_target_in_title:
        return False
        
    return has_target

def classify_financial_theme(text: str) -> str:
    """Mengelompokkan tema bahasan berita bisnis/industri telekomunikasi."""
    t = text.lower()
    if any(k in t for k in ['laba', 'rugi', 'untung', 'pendapatan', 'revenue', 'ebitda', 'margin', 'roa', 'roe', 'kinerja keuangan', 'laporan keuangan']):
        return 'Profitabilitas & Kinerja Keuangan'
    elif any(k in t for k in ['capex', 'belanja modal', 'jaringan', '5g', 'bts', 'fiber', 'data center', 'ai', 'neutradc', 'infrastruktur']):
        return 'Infrastruktur, Data Center & AI'
    elif any(k in t for k in ['dividen', 'yield', 'cum date', 'payout', 'pemegang saham']):
        return 'Dividen & Shareholder Value'
    elif any(k in t for k in ['merger', 'akuisisi', 'infraco', 'spin off', 'konsolidasi', 'kerja sama', 'kemitraan']):
        return 'Aksi Korporasi & Merger'
    elif any(k in t for k in ['saham', 'ihsg', 'target harga', 'rekomendasi', 'buy', 'net sell', 'asing', 'kapitalisasi pasar']):
        return 'Pasar Modal & Saham'
    elif any(k in t for k in ['kurs', 'rupiah', 'dolar', 'suku bunga', 'bi rate', 'inflasi', 'makro']):
        return 'Faktor Makroekonomi'
    elif any(k in t for k in ['arpu', 'kuota', 'paket data', 'pelanggan', 'tarif']):
        return 'Tarif & Pelanggan Seluler'
    else:
        return 'Industri Telekomunikasi Umum'

def compute_nlp_sentiment(text: str):
    """Menghitung polaritas sentimen (-1.0 s.d. +1.0) dengan negation handling."""
    if not isinstance(text, str):
        return 0.0, 'Netral', 0.0, 0.0, '', ''
        
    words = re.sub(r'[^a-zA-Z0-9\s\-]', ' ', text.lower()).split()
    if not words:
        return 0.0, 'Netral', 0.0, 0.0, '', ''
        
    pos_score = 0.0
    neg_score = 0.0
    pos_keywords = []
    neg_keywords = []
    
    n = len(words)
    i = 0
    while i < n:
        w = words[i]
        is_negated = False
        multiplier = 1.0
        
        if i > 0:
            if words[i-1] in NEGATIONS:
                is_negated = True
            elif words[i-1] in INTENSIFIERS:
                multiplier *= 1.5
            elif words[i-1] in DIMINISHERS:
                multiplier *= 0.6
                
        if i > 1 and not is_negated and words[i-2] in NEGATIONS:
            is_negated = True
            
        weight = 0.0
        kind = None
        
        if w in STRONG_POSITIVE:
            weight = 2.0 * multiplier
            kind = 'pos'
        elif w in POSITIVE:
            weight = 1.0 * multiplier
            kind = 'pos'
        elif w in STRONG_NEGATIVE:
            weight = 2.0 * multiplier
            kind = 'neg'
        elif w in NEGATIVE:
            weight = 1.0 * multiplier
            kind = 'neg'
            
        if kind == 'pos':
            if is_negated:
                neg_score += weight
                neg_keywords.append(f"tidak_{w}")
            else:
                pos_score += weight
                pos_keywords.append(w)
        elif kind == 'neg':
            if is_negated:
                pos_score += weight
                pos_keywords.append(f"tidak_{w}")
            else:
                neg_score += weight
                neg_keywords.append(w)
                
        i += 1
        
    total_w = pos_score + neg_score
    if total_w == 0:
        return 0.0, 'Netral', 0.0, 0.0, '', ''
        
    score = (pos_score - neg_score) / total_w
    confidence = min(1.0, total_w / (len(words) * 0.2 + 1))
    subjectivity = min(1.0, total_w / (len(words) * 0.35 + 1))
    
    if score >= 0.15:
        label = 'Positif'
    elif score <= -0.15:
        label = 'Negatif'
    else:
        label = 'Netral'
        
    pos_str = ', '.join(list(dict.fromkeys(pos_keywords))[:5])
    neg_str = ', '.join(list(dict.fromkeys(neg_keywords))[:5])
    
    return round(score, 4), label, round(confidence, 4), round(subjectivity, 4), pos_str, neg_str

def jalankan_pembersihan_dan_ekspor(
    raw_news_path: str = 'data/raw/news_combined/telecom_all_portals_news.csv',
    output_dir: str = 'hasil_data_bersih'
):
    """Menjalankan preprocessing dan menghasilkan output Excel & CSV bersih."""
    os.makedirs(output_dir, exist_ok=True)
    print("\n" + "="*65)
    print(">>> MEMULAI PREPROCESSING & PEMBUATAN DATASET SENTIMEN BERSIH <<<")
    print("="*65)
    
    if not os.path.exists(raw_news_path):
        print(f"Error: {raw_news_path} tidak ditemukan.")
        return
        
    df_raw = pd.read_csv(raw_news_path)
    print(f"1. Membaca dataset mentah: {len(df_raw)} baris dari {df_raw['Portal'].nunique()} portal.")
    
    # Cleaning
    print("2. Membersihkan entitas HTML dan watermark...")
    df_raw['Clean_Title'] = df_raw['Title'].apply(clean_html_and_text)
    df_raw['Clean_Description'] = df_raw['Description'].apply(clean_html_and_text)
    df_raw['Full_Text'] = df_raw['Clean_Title'] + '. ' + df_raw['Clean_Description']
    df_raw['Word_Count'] = df_raw['Full_Text'].apply(lambda x: len(x.split()))
    
    df_valid = df_raw[df_raw['Word_Count'] >= 4].copy()
    
    # Relevance filtering
    print("3. Memfilter noise non-telekomunikasi...")
    df_valid['is_relevant'] = df_valid.apply(check_article_relevance, axis=1)
    df_relevant = df_valid[df_valid['is_relevant']].copy().reset_index(drop=True)
    
    # Deduplication
    print("4. Melakukan deduplikasi artikel...")
    df_dedup = df_relevant.drop_duplicates(subset=['Clean_Title']).drop_duplicates(subset=['URL']).copy().reset_index(drop=True)
    
    # Standardize date
    print("5. Menstandardisasi tanggal & kuarter...")
    dates_data = df_dedup['Published_Date'].apply(parse_and_standardize_date)
    df_dedup['ISO_Published_Date'] = [d[0] for d in dates_data]
    df_dedup['Date'] = [d[1] for d in dates_data]
    df_dedup['Year'] = [int(d[2]) if d[2] is not None else np.nan for d in dates_data]
    df_dedup['Quarter'] = [int(d[3]) if d[3] is not None else np.nan for d in dates_data]
    df_dedup['Month'] = [int(d[4]) if d[4] is not None else np.nan for d in dates_data]
    df_dedup['Fiscal_Period'] = [d[5] for d in dates_data]
    
    df_clean = df_dedup[df_dedup['Date'].notna() & df_dedup['Fiscal_Period'].notna()].copy()
    
    # Theme & Sentiment
    print("6. Mengklasifikasi tema & menghitung skor sentimen NLP...")
    df_clean['Theme_Category'] = df_clean['Full_Text'].apply(classify_financial_theme)
    df_clean['Is_Financial_Metric'] = df_clean['Theme_Category'].isin(['Profitabilitas & Kinerja Keuangan', 'Dividen & Shareholder Value'])
    
    sentiment_results = df_clean['Full_Text'].apply(compute_nlp_sentiment)
    df_clean['Sentiment_Score'] = [s[0] for s in sentiment_results]
    df_clean['Sentiment_Label'] = [s[1] for s in sentiment_results]
    df_clean['Confidence_Score'] = [s[2] for s in sentiment_results]
    df_clean['Subjectivity'] = [s[3] for s in sentiment_results]
    df_clean['Positive_Keywords'] = [s[4] if s[4] else '-' for s in sentiment_results]
    df_clean['Negative_Keywords'] = [s[5] if s[5] else '-' for s in sentiment_results]
    
    df_clean = df_clean.sort_values(by=['Ticker', 'Date']).reset_index(drop=True)
    
    # Format Indonesian column names
    col_map = {
        'Ticker': 'Kode_Emiten',
        'Portal': 'Sumber_Portal',
        'Clean_Title': 'Judul_Berita',
        'Clean_Description': 'Ringkasan_Teks',
        'Theme_Category': 'Kategori_Topik',
        'Is_Financial_Metric': 'Fokus_Keuangan',
        'Sentiment_Score': 'Skor_Sentimen',
        'Sentiment_Label': 'Label_Sentimen',
        'Confidence_Score': 'Keyakinan_Sentimen',
        'Subjectivity': 'Tingkat_Subjektivitas',
        'Positive_Keywords': 'Kata_Kunci_Positif',
        'Negative_Keywords': 'Kata_Kunci_Negatif',
        'ISO_Published_Date': 'Waktu_Publikasi',
        'Date': 'Tanggal',
        'Year': 'Tahun',
        'Quarter': 'Kuarter',
        'Month': 'Bulan',
        'Fiscal_Period': 'Periode_Laporan',
        'Word_Count': 'Jumlah_Kata',
        'URL': 'URL_Sumber'
    }
    
    df_final = df_clean[list(col_map.keys())].rename(columns=col_map).copy()
    df_final['Tahun'] = df_final['Tahun'].astype(int)
    df_final['Kuarter'] = df_final['Kuarter'].astype(int)
    df_final['Bulan'] = df_final['Bulan'].astype(int)
    
    # 7. Quarterly Features
    print("7. Membangun agregasi fitur kuartalan...")
    quarterly_features = df_final.groupby(['Kode_Emiten', 'Periode_Laporan']).agg(
        Total_Berita=('Judul_Berita', 'count'),
        Rata_Rata_Skor_Sentimen=('Skor_Sentimen', 'mean'),
        Std_Deviasi_Sentimen=('Skor_Sentimen', lambda x: x.std() if len(x) > 1 else 0.0),
        Rata_Rata_Keyakinan=('Keyakinan_Sentimen', 'mean'),
        Rata_Rata_Subjektivitas=('Tingkat_Subjektivitas', 'mean'),
        Jumlah_Berita_Positif=('Label_Sentimen', lambda x: (x == 'Positif').sum()),
        Jumlah_Berita_Negatif=('Label_Sentimen', lambda x: (x == 'Negatif').sum()),
        Jumlah_Berita_Netral=('Label_Sentimen', lambda x: (x == 'Netral').sum()),
        Jumlah_Berita_Fokus_Keuangan=('Fokus_Keuangan', 'sum'),
        Sentimen_Khusus_Keuangan=('Skor_Sentimen', lambda x: x[df_final.loc[x.index, 'Fokus_Keuangan']].mean() if df_final.loc[x.index, 'Fokus_Keuangan'].any() else 0.0),
    ).reset_index()
    
    quarterly_features['Std_Deviasi_Sentimen'] = quarterly_features['Std_Deviasi_Sentimen'].fillna(0.0)
    quarterly_features['Rasio_Positif'] = (quarterly_features['Jumlah_Berita_Positif'] / quarterly_features['Total_Berita']).round(4)
    quarterly_features['Rasio_Negatif'] = (quarterly_features['Jumlah_Berita_Negatif'] / quarterly_features['Total_Berita']).round(4)
    quarterly_features['Polaritas_Bersih'] = (quarterly_features['Rasio_Positif'] - quarterly_features['Rasio_Negatif']).round(4)
    quarterly_features['Periode_Kuarter'] = quarterly_features['Periode_Laporan']
    quarterly_features = quarterly_features.drop(columns=['Periode_Laporan'])
    
    # Reorder columns
    q_cols = [
        'Kode_Emiten', 'Periode_Kuarter', 'Total_Berita', 'Rata_Rata_Skor_Sentimen',
        'Std_Deviasi_Sentimen', 'Rata_Rata_Keyakinan', 'Rata_Rata_Subjektivitas',
        'Jumlah_Berita_Positif', 'Jumlah_Berita_Negatif', 'Jumlah_Berita_Netral',
        'Jumlah_Berita_Fokus_Keuangan', 'Sentimen_Khusus_Keuangan',
        'Rasio_Positif', 'Rasio_Negatif', 'Polaritas_Bersih'
    ]
    quarterly_features = quarterly_features[q_cols]
    
    # 8. Slices per emiten
    df_tlkm = df_final[df_final['Kode_Emiten'] == 'TLKM'].reset_index(drop=True)
    df_isat = df_final[df_final['Kode_Emiten'] == 'ISAT'].reset_index(drop=True)
    df_excl = df_final[df_final['Kode_Emiten'] == 'EXCL'].reset_index(drop=True)
    
    # Summary
    summary_data = [
        {'Indikator': 'Total Artikel Berita Bersih', 'Nilai': len(df_final)},
        {'Indikator': 'Total Berita TLKM (Telkom)', 'Nilai': len(df_tlkm)},
        {'Indikator': 'Total Berita ISAT (Indosat)', 'Nilai': len(df_isat)},
        {'Indikator': 'Total Berita EXCL (XL Axiata)', 'Nilai': len(df_excl)},
        {'Indikator': 'Jumlah Berita Positif', 'Nilai': (df_final['Label_Sentimen'] == 'Positif').sum()},
        {'Indikator': 'Jumlah Berita Netral', 'Nilai': (df_final['Label_Sentimen'] == 'Netral').sum()},
        {'Indikator': 'Jumlah Berita Negatif', 'Nilai': (df_final['Label_Sentimen'] == 'Negatif').sum()},
        {'Indikator': 'Rata-Rata Skor Sentimen Keseluruhan', 'Nilai': round(df_final['Skor_Sentimen'].mean(), 4)},
        {'Indikator': 'Net Polarity Score', 'Nilai': round((df_final['Label_Sentimen'] == 'Positif').mean() - (df_final['Label_Sentimen'] == 'Negatif').mean(), 4)}
    ]
    df_sum = pd.DataFrame(summary_data)
    portal_dist = df_final['Sumber_Portal'].value_counts().reset_index()
    portal_dist.columns = ['Portal_Berita', 'Jumlah_Artikel']
    theme_dist = df_final['Kategori_Topik'].value_counts().reset_index()
    theme_dist.columns = ['Kategori_Topik', 'Jumlah_Artikel']
    
    # 9. Export to Excel & CSV
    print("8. Mengekspor file Excel Master (.xlsx) dan file CSV...")
    excel_path = os.path.join(output_dir, 'DATASET_SENTIMEN_BERITA_TELEKOMUNIKASI_MASTER.xlsx')
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        df_final.to_excel(writer, sheet_name='Semua_Berita_Bersih', index=False)
        quarterly_features.to_excel(writer, sheet_name='Sentimen_Kuartalan', index=False)
        df_tlkm.to_excel(writer, sheet_name='TLKM_Telkom', index=False)
        df_isat.to_excel(writer, sheet_name='ISAT_Indosat', index=False)
        df_excl.to_excel(writer, sheet_name='EXCL_XL', index=False)
        df_sum.to_excel(writer, sheet_name='Ringkasan_Statistik', index=False, startrow=0, startcol=0)
        portal_dist.to_excel(writer, sheet_name='Ringkasan_Statistik', index=False, startrow=12, startcol=0)
        theme_dist.to_excel(writer, sheet_name='Ringkasan_Statistik', index=False, startrow=23, startcol=0)
        
    df_final.to_csv(os.path.join(output_dir, 'DATASET_SENTIMEN_BERITA_TELEKOMUNIKASI_MASTER.csv'), index=False)
    quarterly_features.to_csv(os.path.join(output_dir, 'FITUR_SENTIMEN_KUARTALAN_TLKM_ISAT_EXCL.csv'), index=False)
    df_tlkm.to_csv(os.path.join(output_dir, 'berita_sentimen_TLKM_bersih.csv'), index=False)
    df_isat.to_csv(os.path.join(output_dir, 'berita_sentimen_ISAT_bersih.csv'), index=False)
    df_excl.to_csv(os.path.join(output_dir, 'berita_sentimen_EXCL_bersih.csv'), index=False)
    
    print(f"\n[SUKSES] Seluruh file data bersih tersimpan di: {output_dir}/")
    print(f"  • {excel_path} ({len(df_final)} baris)")
    print(f"  • DATASET_SENTIMEN_BERITA_TELEKOMUNIKASI_MASTER.csv ({len(df_final)} baris)")
    print(f"  • FITUR_SENTIMEN_KUARTALAN_TLKM_ISAT_EXCL.csv ({len(quarterly_features)} baris kuartal)")
    print(f"  • berita_sentimen_TLKM_bersih.csv ({len(df_tlkm)} baris)")
    print(f"  • berita_sentimen_ISAT_bersih.csv ({len(df_isat)} baris)")
    print(f"  • berita_sentimen_EXCL_bersih.csv ({len(df_excl)} baris)")

if __name__ == '__main__':
    jalankan_pembersihan_dan_ekspor()
