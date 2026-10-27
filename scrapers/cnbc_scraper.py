"""
Dedicated Scraper for CNBC Indonesia (cnbcindonesia.com)
Scrapes telecom industry & financial news for TLKM, ISAT, EXCL from:
1. CNBC Indonesia Tag Pages (/tag/tlkm, /tag/telkom, /tag/indosat, /tag/xl-axiata) with pagination
2. CNBC Google News RSS queries for targeted corporate actions, earnings, and market news
"""

import os
import re
import time
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime
import pandas as pd
from bs4 import BeautifulSoup

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
}

CNBC_TAGS = {
    'TLKM': ['tlkm', 'telkom', 'telkomsel'],
    'ISAT': ['isat', 'indosat', 'indosat-ooredoo'],
    'EXCL': ['excl', 'xl-axiata', 'xlsmart']
}

CNBC_RSS_QUERIES = {
    'TLKM': ['TLKM saham', 'Telkom laba pendapatan', 'Telkomsel dividen capex', 'Telkom data center AI'],
    'ISAT': ['ISAT saham', 'Indosat Ooredoo laba', 'Indosat dividen merger', 'Indosat belanja modal'],
    'EXCL': ['EXCL saham', 'XL Axiata laba pendapatan', 'XL Axiata merger akuisisi', 'XL Axiata dividen']
}

def parse_date_and_period(date_str):
    """Parses date string or URL timestamp into (datetime, Period e.g. 'Q3 2024')."""
    if not date_str:
        return None, None
        
    # Check if string is 14-digit timestamp like 20261021130426
    match_ts = re.search(r'(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})', date_str)
    if match_ts:
        try:
            y, m, d, H, M, S = [int(x) for x in match_ts.groups()]
            dt = datetime(y, m, d, H, M, S)
            q = (m - 1) // 3 + 1
            return dt, f"Q{q} {y}"
        except Exception:
            pass
            
    # Try RFC 822 format e.g. 'Sat, 24 Oct 2026 23:05:24 GMT'
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

def scrape_cnbc_tag_page(tag: str, page: int = 1) -> list:
    """Scrapes single tag page on CNBC Indonesia."""
    url = f"https://www.cnbcindonesia.com/tag/{tag}?page={page}"
    req = urllib.request.Request(url, headers=HEADERS)
    articles = []
    
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            html = resp.read().decode('utf-8')
    except Exception as e:
        print(f"    [CNBC Tag {tag} p.{page}] Request error: {e}")
        return []
        
    soup = BeautifulSoup(html, 'html.parser')
    for art in soup.find_all('article'):
        a_tag = art.find('a', href=True)
        if not a_tag:
            continue
        link = a_tag['href']
        
        # Title
        h2 = art.find('h2') or art.find('h3')
        title = h2.get_text(strip=True) if h2 else a_tag.get_text(strip=True)
        if not title or len(title) < 10:
            continue
            
        # Category
        cat_span = art.find('span', class_=re.compile(r'text-cnbc|uppercase', re.I))
        category = cat_span.get_text(strip=True) if cat_span else 'News'
        
        # Date from URL timestamp
        dt, period = parse_date_and_period(link)
        
        articles.append({
            'Portal': 'CNBC Indonesia',
            'Tag_Query': tag,
            'Title': title,
            'Category': category,
            'Published_Date': dt.strftime('%Y-%m-%d %H:%M:%S') if dt else '',
            'Period': period if period else '',
            'Description': title,
            'URL': link
        })
        
    return articles

def scrape_cnbc_rss(query: str, ticker: str) -> list:
    """Scrapes CNBC Indonesia articles via Google News RSS search."""
    q_full = f"site:cnbcindonesia.com {query}"
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
                
                # Strip ' - CNBC Indonesia' suffix
                if ' - CNBC Indonesia' in title:
                    title = title.replace(' - CNBC Indonesia', '').strip()
                elif ' - CNBC' in title:
                    title = title.replace(' - CNBC', '').strip()
                    
                dt, period = parse_date_and_period(pub_raw)
                # Clean html in desc
                desc_clean = re.sub(r'<.*?>', '', desc_raw).strip()
                
                articles.append({
                    'Portal': 'CNBC Indonesia',
                    'Ticker': ticker,
                    'Tag_Query': query,
                    'Title': title,
                    'Category': 'Market & Tech',
                    'Published_Date': dt.strftime('%Y-%m-%d %H:%M:%S') if dt else pub_raw,
                    'Period': period if period else '',
                    'Description': desc_clean,
                    'URL': link
                })
    except Exception as e:
        print(f"    [CNBC RSS '{query}'] Error: {e}")
        
    return articles

def scrape_all_cnbc(output_dir: str = 'data/raw/news_cnbc', max_pages_per_tag: int = 4) -> pd.DataFrame:
    """Scrapes both tags and RSS for all telecom emiten from CNBC Indonesia."""
    os.makedirs(output_dir, exist_ok=True)
    print("\n" + "="*50)
    print(">>> STARTING CNBC INDONESIA TELECOM SCRAPER <<<")
    print("="*50)
    
    all_articles = []
    
    # 1. Scrape by Tags
    for ticker, tags in CNBC_TAGS.items():
        print(f"\n[CNBC Tags] Scraping tags for {ticker}...")
        for tag in tags:
            for page in range(1, max_pages_per_tag + 1):
                arts = scrape_cnbc_tag_page(tag, page=page)
                for a in arts:
                    a['Ticker'] = ticker
                print(f"  Tag '{tag}' (page {page}): {len(arts)} articles")
                all_articles.extend(arts)
                time.sleep(0.5)
                
    # 2. Scrape by RSS Queries
    for ticker, queries in CNBC_RSS_QUERIES.items():
        print(f"\n[CNBC RSS] Scraping queries for {ticker}...")
        for q in queries:
            arts = scrape_cnbc_rss(q, ticker)
            print(f"  Query '{q}': {len(arts)} articles")
            all_articles.extend(arts)
            time.sleep(0.5)
            
    df = pd.DataFrame(all_articles)
    if not df.empty:
        # Deduplicate
        initial_len = len(df)
        df = df.drop_duplicates(subset=['Title'])
        print(f"\n[CNBC SUMMARY] Total articles fetched: {initial_len} -> Unique: {len(df)}")
        
        # Save per ticker
        for ticker in ['TLKM', 'ISAT', 'EXCL']:
            df_t = df[df['Ticker'] == ticker]
            t_path = os.path.join(output_dir, f"cnbc_{ticker}_news.csv")
            df_t.to_csv(t_path, index=False)
            print(f"  [SAVED] {t_path}: {len(df_t)} articles")
            
        combined_path = os.path.join(output_dir, "cnbc_all_telecom_news.csv")
        df.to_csv(combined_path, index=False)
        print(f"[DONE] Combined CNBC News saved to {combined_path}")
        
    return df

if __name__ == '__main__':
    scrape_all_cnbc()
