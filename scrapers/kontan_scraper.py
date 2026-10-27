"""
Dedicated Scraper for Kontan (kontan.co.id & investasi.kontan.co.id)
Scrapes telecom industry & financial news for TLKM, ISAT, EXCL from:
1. Kontan Search (https://www.kontan.co.id/search/?search={query})
2. Kontan RSS feed for emiten financial statements, stock recommendations, and capex
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
    'Accept-Language': 'id-ID,id;q=0.9',
}

KONTAN_QUERIES = {
    'TLKM': ['TLKM', 'Telkom Indonesia', 'Telkomsel laba', 'saham TLKM', 'Telkom data center'],
    'ISAT': ['ISAT', 'Indosat Ooredoo', 'saham ISAT', 'Indosat dividen', 'Indosat laba'],
    'EXCL': ['EXCL', 'XL Axiata', 'saham EXCL', 'XL Axiata laba', 'XL Axiata merger']
}

def parse_date_and_period(date_str):
    """Parses date string or Indonesian date into (datetime, Period e.g. 'Q3 2024')."""
    if not date_str:
        return None, None
        
    # Indo months mapping
    indo_months = {
        'januari': 1, 'februari': 2, 'maret': 3, 'april': 4, 'mei': 5, 'juni': 6,
        'juli': 7, 'agustus': 8, 'september': 9, 'oktober': 10, 'november': 11, 'desember': 12,
        'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
        'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12, 'okt': 10, 'des': 12
    }
    
    # Try RFC 822 format e.g. 'Sat, 24 Oct 2026 23:05:24 GMT'
    try:
        dt = datetime.strptime(date_str[:25].strip(), '%a, %d %b %Y %H:%M:%S')
        q = (dt.month - 1) // 3 + 1
        return dt, f"Q{q} {dt.year}"
    except Exception:
        pass

    # Check Indonesian format e.g. '24 Oktober 2026' or '24/10/2026'
    match_indo = re.search(r'(\d{1,2})\s+([a-zA-Z]+)\s+(\d{4})', date_str.lower())
    if match_indo:
        d, m_str, y = match_indo.groups()
        m = indo_months.get(m_str.lower())
        if m:
            try:
                dt = datetime(int(y), m, int(d))
                q = (m - 1) // 3 + 1
                return dt, f"Q{q} {y}"
            except Exception:
                pass
                
    try:
        dt = pd.to_datetime(date_str)
        q = (dt.month - 1) // 3 + 1
        return dt, f"Q{q} {dt.year}"
    except Exception:
        return None, None

def scrape_kontan_search(query: str, ticker: str, max_pages: int = 3) -> list:
    """Scrapes direct search results on Kontan."""
    articles = []
    
    for page in range(1, max_pages + 1):
        pos = (page - 1) * 20
        url = f"https://www.kontan.co.id/search/?search={urllib.parse.quote(query)}&pos={pos}"
        req = urllib.request.Request(url, headers=HEADERS)
        try:
            with urllib.request.urlopen(req, timeout=12) as resp:
                html = resp.read().decode('utf-8')
        except Exception as e:
            print(f"    [Kontan Search '{query}' p.{page}] Error: {e}")
            break
            
        soup = BeautifulSoup(html, 'html.parser')
        # Containers in kontan search
        items = soup.select('div.sp-list, div.list-berita')
        if not items:
            # Fallback to links containing /news/
            items = soup.find_all('div', class_=re.compile(r'mar-b-15|item-list', re.I))
            
        if not items:
            break
            
        page_found = 0
        for item in items:
            a_tag = item.find('a', href=True)
            if not a_tag or '/news/' not in a_tag['href']:
                continue
            link = a_tag['href']
            if not link.startswith('http'):
                link = 'https:' + link
                
            title_tag = item.find('h1') or item.find('h2') or item.find('h3') or a_tag
            title = title_tag.get_text(strip=True)
            if not title or len(title) < 15:
                continue
                
            # Date
            date_div = item.find('div', class_=re.compile(r'date|font-gray|tgl', re.I)) or item.find('span', class_=re.compile(r'date|tgl', re.I))
            date_text = date_div.get_text(strip=True) if date_div else ''
            dt, period = parse_date_and_period(date_text)
            
            # Snippet
            desc_tag = item.find('p')
            desc = desc_tag.get_text(strip=True) if desc_tag else title
            
            articles.append({
                'Portal': 'Kontan',
                'Ticker': ticker,
                'Tag_Query': query,
                'Title': title,
                'Category': 'Investasi & Emiten',
                'Published_Date': dt.strftime('%Y-%m-%d %H:%M:%S') if dt else date_text,
                'Period': period if period else '',
                'Description': desc,
                'URL': link
            })
            page_found += 1
            
        if page_found == 0:
            break
        time.sleep(0.5)
        
    return articles

def scrape_kontan_rss(query: str, ticker: str) -> list:
    """Scrapes Kontan articles via Google News RSS search for archived stories."""
    q_full = f"site:kontan.co.id {query}"
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
                
                # Strip portal suffix
                title = re.sub(r'\s*-\s*kontan\.co\.id.*', '', title, flags=re.I).strip()
                title = re.sub(r'\s*-\s*KONTAN.*', '', title, flags=re.I).strip()
                
                dt, period = parse_date_and_period(pub_raw)
                desc_clean = re.sub(r'<.*?>', '', desc_raw).strip()
                
                articles.append({
                    'Portal': 'Kontan',
                    'Ticker': ticker,
                    'Tag_Query': query,
                    'Title': title,
                    'Category': 'Investasi & Emiten',
                    'Published_Date': dt.strftime('%Y-%m-%d %H:%M:%S') if dt else pub_raw,
                    'Period': period if period else '',
                    'Description': desc_clean,
                    'URL': link
                })
    except Exception as e:
        print(f"    [Kontan RSS '{query}'] Error: {e}")
        
    return articles

def scrape_all_kontan(output_dir: str = 'data/raw/news_kontan') -> pd.DataFrame:
    """Scrapes news articles from Kontan for TLKM, ISAT, EXCL."""
    os.makedirs(output_dir, exist_ok=True)
    print("\n" + "="*50)
    print(">>> STARTING KONTAN TELECOM SCRAPER <<<")
    print("="*50)
    
    all_articles = []
    
    for ticker, queries in KONTAN_QUERIES.items():
        print(f"\n[Kontan] Scraping queries for {ticker}...")
        for q in queries:
            # Direct search
            arts_dir = scrape_kontan_search(q, ticker, max_pages=2)
            print(f"  Search '{q}': {len(arts_dir)} articles")
            all_articles.extend(arts_dir)
            
            # RSS
            arts_rss = scrape_kontan_rss(q, ticker)
            print(f"  RSS '{q}': {len(arts_rss)} articles")
            all_articles.extend(arts_rss)
            time.sleep(0.5)
            
    df = pd.DataFrame(all_articles)
    if not df.empty:
        initial_len = len(df)
        df = df.drop_duplicates(subset=['Title'])
        print(f"\n[KONTAN SUMMARY] Total articles fetched: {initial_len} -> Unique: {len(df)}")
        
        for ticker in ['TLKM', 'ISAT', 'EXCL']:
            df_t = df[df['Ticker'] == ticker]
            t_path = os.path.join(output_dir, f"kontan_{ticker}_news.csv")
            df_t.to_csv(t_path, index=False)
            print(f"  [SAVED] {t_path}: {len(df_t)} articles")
            
        combined_path = os.path.join(output_dir, "kontan_all_telecom_news.csv")
        df.to_csv(combined_path, index=False)
        print(f"[DONE] Combined Kontan News saved to {combined_path}")
        
    return df

if __name__ == '__main__':
    scrape_all_kontan()
