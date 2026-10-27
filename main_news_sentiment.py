"""
Main CLI Runner: Scraping Multi-Portal Berita & Pemrosesan Data Sentimen Bersih
Target Emiten: TLKM (Telkom), ISAT (Indosat), EXCL (XL Axiata)
Output: File Excel (.xlsx) dan CSV (.csv) bersih di folder hasil_data_bersih/
"""

import os
import sys
import argparse
from scrapers.cnbc_scraper import scrape_all_cnbc
from scrapers.kontan_scraper import scrape_all_kontan
from scrapers.multiportal_scraper import scrape_all_other_portals, compile_master_news_corpus
from proses_dan_ekspor import jalankan_pembersihan_dan_ekspor

def main():
    parser = argparse.ArgumentParser(
        description="Scraping Berita & Preprocessing Data Sentimen (TLKM, ISAT, EXCL)"
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help="Jalankan scraper seluruh portal berita + preprocessing + ekspor ke Excel & CSV"
    )
    parser.add_argument(
        '--scrape-only',
        action='store_true',
        help="Hanya jalankan scraping berita mentah"
    )
    parser.add_argument(
        '--clean-only',
        action='store_true',
        help="Hanya jalankan preprocessing dan ekspor data bersih (tanpa scraping ulang)"
    )
    
    args = parser.parse_args()
    
    if not any([args.all, args.scrape_only, args.clean_only]):
        args.all = True
        
    if args.scrape_only or args.all:
        print("\n" + "="*60)
        print("  MEMULAI SCRAPING MULTI-PORTAL BERITA TELEKOMUNIKASI")
        print("  (CNBC Indonesia, Kontan, Bisnis.com, Investor.id, dll)")
        print("="*60 + "\n")
        scrape_all_cnbc()
        scrape_all_kontan()
        scrape_all_other_portals()
        compile_master_news_corpus()
        
    if args.clean_only or args.all:
        jalankan_pembersihan_dan_ekspor()

if __name__ == '__main__':
    main()
