"""
Unified Multi-Portal Financial News Scraper
Scrapes telecom industry news across major Indonesian business & capital market portals:
- CNBC Indonesia (cnbcindonesia.com)
- Kontan (kontan.co.id)
- Bisnis.com (bisnis.com / market.bisnis.com)
- Investor Daily / Investor.id (investor.id)
- Detik Finance / Emitennews / IDNFinancials

Produces a harmonized, clean dataset for NLP Sentiment Analysis and Cloud Azure feature storage.
"""

import os
import re
import time
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime
import pandas as pd

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
}

PORTAL_DOMAINS = {
    'Bisnis.com': 'bisnis.com',
    'Investor.id': 'investor.id',
    'Detik Finance': 'finance.detik.com',
    'Katadata': 'katadata.co.id',
    'EmitenNews': 'emitennews.com'
}

SEARCH_THEMES = {
    'TLKM': [
        'TLKM saham kinerja laba',
        'Telkom dividen belanja modal capex',
        'Telkomsel pendapatan ARPU digital',
        'Telkom data center NeutraDC AI',
        'Telkom Infraco spin-off fiber'
    ],
    'ISAT': [
        'ISAT saham laba bersih pendapatan',
        'Indosat dividen kinerja keuangan',
        'Indosat Ooredoo Hutchison merger 5G',
        'Indosat AI Cloud kerja sama Nvidia',
        'Indosat ARPU pelanggan seluler'
    ],
    'EXCL': [
        'EXCL saham laba bersih kuartal',
        'XL Axiata pendapatan dividen',
        'XL Axiata merger akuisisi Link Net',
        'XL Axiata belanja modal jaringan fiber',
        'XLSmart merger telekomunikasi'
    ]
}

def parse_date_and_period(date_str):
    """Parses date string into datetime object and Period (e.g. 'Q2 2024')."""
    if not date_str:
        return None, None
        
    try:
        dt = datetime.strptime(date_str[:25].strip(), '%a, %d %b %Y %H:%M:%S')
        q = (dt.month - 1) // 3 + 1
        return dt, f"Q{q} {dt.year}"
    except Exception:
        pass
        
    try:
        dt = pd.to_datetime(date_str)
        q = (dt.month - 1) // 3 + 1
        return dt, f"Q{q} {dt.year}"
    except Exception:
        return None, None

def scrape_portal_rss(domain: str, portal_name: str, query: str, ticker: str) -> list:
    """Scrapes Google News RSS for a specific portal domain and query."""
    q_full = f"site:{domain} {query}"
    encoded = urllib.parse.quote(q_full)
    url = f"https://news.google.com/rss/search?q={encoded}&hl=id&gl=ID&ceid=ID:id"
    req = urllib.request.Request(url, headers=HEADERS)
    articles = []
    
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            xml_data = resp.read()
            root = ET.fromstring(xml_data)
            
            for item in root.findall('.//item'):
                title = item.find('title').text if item.find('title') is not None else ''
                link = item.find('link').text if item.find('link') is not None else ''
                pub_raw = item.find('pubDate').text if item.find('pubDate') is not None else ''
                desc_raw = item.find('description').text if item.find('description') is not None else ''
                
                # Strip portal name suffix if attached to title
                if ' - ' in title:
                    title_clean = title.rsplit(' - ', 1)[0].strip()
                else:
                    title_clean = title.strip()
                    
                dt, period = parse_date_and_period(pub_raw)
                desc_clean = re.sub(r'<.*?>', '', desc_raw).strip()
                
                articles.append({
                    'Portal': portal_name,
                    'Ticker': ticker,
                    'Tag_Query': query,
                    'Title': title_clean,
                    'Category': 'Pasar Modal & Industri Telekomunikasi',
                    'Published_Date': dt.strftime('%Y-%m-%d %H:%M:%S') if dt else pub_raw,
                    'Period': period if period else '',
                    'Description': desc_clean,
                    'URL': link
                })
    except Exception as e:
        print(f"    [{portal_name} RSS '{query}'] Error: {e}")
        
    return articles

def scrape_all_other_portals(output_base_dir: str = 'data/raw') -> pd.DataFrame:
    """Scrapes news across Bisnis.com, Investor.id, Detik Finance, and Katadata."""
    print("\n" + "="*50)
    print(">>> STARTING MULTI-PORTAL TELECOM NEWS SCRAPER <<<")
    print(">>> (Bisnis.com, Investor.id, Detik Finance, Katadata) <<<")
    print("="*50)
    
    all_articles = []
    
    for portal_name, domain in PORTAL_DOMAINS.items():
        print(f"\n--- Scraping Portal: {portal_name} ({domain}) ---")
        portal_slug = portal_name.lower().replace('.', '').replace(' ', '_')
        portal_dir = os.path.join(output_base_dir, f"news_{portal_slug}")
        os.makedirs(portal_dir, exist_ok=True)
        
        portal_articles = []
        for ticker, queries in SEARCH_THEMES.items():
            print(f"  Fetching {ticker} on {portal_name}...")
            for q in queries:
                arts = scrape_portal_rss(domain, portal_name, q, ticker)
                portal_articles.extend(arts)
                time.sleep(0.4)
                
        df_portal = pd.DataFrame(portal_articles)
        if not df_portal.empty:
            df_portal = df_portal.drop_duplicates(subset=['Title'])
            out_file = os.path.join(portal_dir, f"{portal_slug}_all_telecom_news.csv")
            df_portal.to_csv(out_file, index=False)
            print(f"  [SAVED] {out_file}: {len(df_portal)} unique articles")
            all_articles.extend(df_portal.to_dict('records'))
            
    df_all = pd.DataFrame(all_articles)
    return df_all

def compile_master_news_corpus(
    raw_dir: str = 'data/raw',
    output_dir: str = 'data/raw/news_combined'
) -> pd.DataFrame:
    """
    Merges news from all portals (CNBC, Kontan, Bisnis, Investor, Detik Finance)
    into a unified corpus with comprehensive deduplication.
    """
    os.makedirs(output_dir, exist_ok=True)
    all_dfs = []
    
    # Collect all CSVs in raw/news_*
    for root, _, files in os.walk(raw_dir):
        for f in files:
            if f.endswith('_news.csv') and not f.startswith('telecom_all_portals'):
                fpath = os.path.join(root, f)
                try:
                    df = pd.read_csv(fpath)
                    all_dfs.append(df)
                except Exception:
                    pass
                    
    if not all_dfs:
        print("No raw news files found to combine.")
        return pd.DataFrame()
        
    master_df = pd.concat(all_dfs, ignore_index=True)
    initial_count = len(master_df)
    
    # Deduplicate by Title
    master_df = master_df.drop_duplicates(subset=['Title']).reset_index(drop=True)
    
    # Assign theme tag
    def assign_theme(text):
        text_lower = str(text).lower()
        if any(k in text_lower for k in ['laba', 'rugi', 'untung', 'pendapatan', 'margin', 'roa', 'roe', 'ebitda']):
            return 'Profitabilitas & Kinerja Keuangan'
        elif any(k in text_lower for k in ['dividen', 'yield', 'cum date', 'payout']):
            return 'Dividen & Shareholder Value'
        elif any(k in text_lower for k in ['merger', 'akuisisi', 'infraco', 'spin off', 'kerja sama', 'konsolidasi']):
            return 'Aksi Korporasi & Merger'
        elif any(k in text_lower for k in ['capex', 'belanja modal', 'jaringan', '5g', 'bts', 'fiber', 'data center', 'ai']):
            return 'Infrastruktur, Data Center & AI'
        elif any(k in text_lower for k in ['saham', 'ihsg', 'target harga', 'rekomendasi', 'buy', 'net sell', 'asing']):
            return 'Pergerakan Pasar Modal'
        elif any(k in text_lower for k in ['kurs', 'rupiah', 'dolar', 'suku bunga', 'bi rate', 'inflasi']):
            return 'Faktor Makroekonomi'
        else:
            return 'Umum / Industri Telekomunikasi'
            
    master_df['Theme'] = master_df['Title'].apply(assign_theme)
    
    out_master = os.path.join(output_dir, 'telecom_all_portals_news.csv')
    master_df.to_csv(out_master, index=False)
    
    print("\n" + "="*50)
    print(">>> MASTER MULTI-PORTAL CORPUS COMPILED <<<")
    print(f"Total raw news gathered: {initial_count}")
    print(f"Total unique news after deduplication: {len(master_df)}")
    print(f"Distribution by Portal:\n{master_df['Portal'].value_counts()}")
    print(f"\nDistribution by Ticker:\n{master_df['Ticker'].value_counts()}")
    print(f"\nDistribution by Theme:\n{master_df['Theme'].value_counts()}")
    print(f"[SAVED] Master news corpus saved to {out_master}")
    print("="*50)
    
    return master_df

if __name__ == '__main__':
    # 1. Scrape other portals
    scrape_all_other_portals()
    # 2. Compile master news corpus
    compile_master_news_corpus()
