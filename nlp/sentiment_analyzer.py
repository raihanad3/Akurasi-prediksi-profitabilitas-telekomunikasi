"""
NLP Sentiment Analysis Engine for Indonesian Financial & Telecom News
Processes scraped articles from CNBC, Kontan, Bisnis.com, Investor.id, Detik Finance, etc.
Implements:
- Negation handling (e.g. 'tidak naik', 'belum untung')
- Valence shifting & intensification
- Article-level scoring
- Quarterly aggregation by Ticker & Period for Azure ML Profitability Prediction
- Multi-portal sentiment comparison analysis
"""

import os
import re
import pandas as pd
import numpy as np
from nlp.indonesian_financial_lexicon import (
    STRONG_POSITIVE, POSITIVE,
    STRONG_NEGATIVE, NEGATIVE,
    NEGATIONS, INTENSIFIERS, DIMINISHERS
)

def clean_and_tokenize(text: str) -> list:
    """Preprocesses Indonesian text and tokenizes into words."""
    if not isinstance(text, str):
        return []
    text = text.lower()
    # Remove URLs, email, numbers with punctuation
    text = re.sub(r'http\S+|www\S+', '', text)
    text = re.sub(r'[^a-zA-Z0-9\s\-]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text.split()

def analyze_sentiment(text: str):
    """
    Computes sentiment polarity (-1.0 to 1.0), label, subjectivity, and trigger words.
    Takes into account negations (window of 2 words) and intensifiers/diminishers.
    """
    words = clean_and_tokenize(text)
    if not words:
        return 0.0, 'Netral', 0.0, [], []
        
    pos_score = 0.0
    neg_score = 0.0
    pos_words_found = []
    neg_words_found = []
    
    n = len(words)
    i = 0
    
    while i < n:
        w = words[i]
        
        # Check window for negation / intensifier
        is_negated = False
        multiplier = 1.0
        
        # Check if preceding word is a negation or intensifier
        if i > 0:
            prev_1 = words[i-1]
            if prev_1 in NEGATIONS:
                is_negated = True
            elif prev_1 in INTENSIFIERS:
                multiplier *= 1.5
            elif prev_1 in DIMINISHERS:
                multiplier *= 0.6
                
        if i > 1 and not is_negated:
            prev_2 = words[i-2]
            if prev_2 in NEGATIONS:
                is_negated = True
                
        # Determine base weight of current word
        weight = 0.0
        w_type = None
        
        if w in STRONG_POSITIVE:
            weight = 2.0 * multiplier
            w_type = 'pos'
        elif w in POSITIVE:
            weight = 1.0 * multiplier
            w_type = 'pos'
        elif w in STRONG_NEGATIVE:
            weight = 2.0 * multiplier
            w_type = 'neg'
        elif w in NEGATIVE:
            weight = 1.0 * multiplier
            w_type = 'neg'
            
        if w_type == 'pos':
            if is_negated:
                neg_score += weight
                neg_words_found.append(f"tidak_{w}")
            else:
                pos_score += weight
                pos_words_found.append(w)
        elif w_type == 'neg':
            if is_negated:
                pos_score += weight
                pos_words_found.append(f"tidak_{w}")
            else:
                neg_score += weight
                neg_words_found.append(w)
                
        i += 1
        
    total_sentiment_weight = pos_score + neg_score
    total_words = len(words)
    
    if total_sentiment_weight == 0:
        return 0.0, 'Netral', 0.0, [], []
        
    # Polarity Score (-1.0 to 1.0)
    score = (pos_score - neg_score) / (pos_score + neg_score)
    # Subjectivity Score (density of emotive/evaluative terms)
    subjectivity = min(1.0, total_sentiment_weight / (total_words * 0.3 + 1))
    
    # Classification Threshold
    if score >= 0.15:
        label = 'Positif'
    elif score <= -0.15:
        label = 'Negatif'
    else:
        label = 'Netral'
        
    return round(score, 4), label, round(subjectivity, 4), pos_words_found, neg_words_found

def run_sentiment_pipeline(
    input_file: str = 'data/raw/news_combined/telecom_all_portals_news.csv',
    output_dir: str = 'data/processed'
):
    """Executes NLP sentiment analysis over the master multi-portal news corpus."""
    os.makedirs(output_dir, exist_ok=True)
    print("\n" + "="*50)
    print(">>> STARTING NLP NEWS SENTIMENT ENGINE <<<")
    print("="*50)
    
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        return None
        
    df = pd.read_csv(input_file)
    print(f"Loaded master corpus: {len(df)} articles across {df['Portal'].nunique()} portals.")
    
    scores = []
    labels = []
    subjectivities = []
    pos_triggers = []
    neg_triggers = []
    
    for _, row in df.iterrows():
        content_to_analyze = f"{row.get('Title', '')}. {row.get('Description', '')}"
        score, label, subj, pos_w, neg_w = analyze_sentiment(content_to_analyze)
        scores.append(score)
        labels.append(label)
        subjectivities.append(subj)
        pos_triggers.append(', '.join(pos_w[:5]))
        neg_triggers.append(', '.join(neg_w[:5]))
        
    df['Sentiment_Score'] = scores
    df['Sentiment_Label'] = labels
    df['Subjectivity'] = subjectivities
    df['Positive_Triggers'] = pos_triggers
    df['Negative_Triggers'] = neg_triggers
    
    # 1. Save Article-Level Sentiment Scored Dataset
    article_out = os.path.join(output_dir, 'sentiment_scored_articles.csv')
    df.to_csv(article_out, index=False)
    print(f"\n[DONE] Article-level sentiment saved to {article_out}")
    print("\nSentiment Label Distribution across All Portals:")
    print(df['Sentiment_Label'].value_counts(normalize=True).round(3) * 100)
    
    # 2. Portal Comparison Sentiment Analysis
    portal_summary = df.groupby('Portal').agg(
        Total_Articles=('Title', 'count'),
        Avg_Sentiment_Score=('Sentiment_Score', 'mean'),
        Pos_Articles=('Sentiment_Label', lambda x: (x == 'Positif').sum()),
        Neg_Articles=('Sentiment_Label', lambda x: (x == 'Negatif').sum()),
        Neu_Articles=('Sentiment_Label', lambda x: (x == 'Netral').sum()),
        Avg_Subjectivity=('Subjectivity', 'mean')
    ).reset_index()
    
    portal_summary['Pos_Ratio'] = (portal_summary['Pos_Articles'] / portal_summary['Total_Articles']).round(3)
    portal_summary['Neg_Ratio'] = (portal_summary['Neg_Articles'] / portal_summary['Total_Articles']).round(3)
    portal_summary['Net_Polarity'] = (portal_summary['Pos_Ratio'] - portal_summary['Neg_Ratio']).round(3)
    
    portal_out = os.path.join(output_dir, 'portal_comparison_sentiment.csv')
    portal_summary.to_csv(portal_out, index=False)
    print(f"\n[DONE] Saved Portal Comparison to {portal_out}")
    print("\nPortal Comparison Table:")
    print(portal_summary[['Portal', 'Total_Articles', 'Avg_Sentiment_Score', 'Pos_Ratio', 'Neg_Ratio', 'Net_Polarity']])
    
    # Financial performance specific sentiment
    df['is_financial_theme'] = df['Theme'] == 'Profitabilitas & Kinerja Keuangan'
    
    # 3. Quarterly Sentiment Features per Ticker (for Azure ML Profitability Model)
    valid_periods = df[df['Period'].notna() & (df['Period'] != '') & df['Period'].str.startswith('Q')].copy()
    
    quarterly_sentiment = valid_periods.groupby(['Ticker', 'Period']).agg(
        News_Volume=('Title', 'count'),
        Sentiment_Mean_Score=('Sentiment_Score', 'mean'),
        Sentiment_Score_Std=('Sentiment_Score', 'std'),
        Sentiment_Pos_Count=('Sentiment_Label', lambda x: (x == 'Positif').sum()),
        Sentiment_Neg_Count=('Sentiment_Label', lambda x: (x == 'Negatif').sum()),
        Sentiment_Neu_Count=('Sentiment_Label', lambda x: (x == 'Netral').sum()),
        Financial_News_Count=('is_financial_theme', 'sum'),
        Financial_Sentiment_Mean=('Sentiment_Score', lambda x: x[valid_periods.loc[x.index, 'is_financial_theme']].mean() if valid_periods.loc[x.index, 'is_financial_theme'].any() else 0.0),
        Avg_Subjectivity=('Subjectivity', 'mean')
    ).reset_index()

    
    quarterly_sentiment['Sentiment_Score_Std'] = quarterly_sentiment['Sentiment_Score_Std'].fillna(0.0)
    quarterly_sentiment['Sentiment_Pos_Ratio'] = (quarterly_sentiment['Sentiment_Pos_Count'] / quarterly_sentiment['News_Volume']).round(4)
    quarterly_sentiment['Sentiment_Neg_Ratio'] = (quarterly_sentiment['Sentiment_Neg_Count'] / quarterly_sentiment['News_Volume']).round(4)
    quarterly_sentiment['Sentiment_Net_Polarity'] = (quarterly_sentiment['Sentiment_Pos_Ratio'] - quarterly_sentiment['Sentiment_Neg_Ratio']).round(4)
    
    quarterly_out = os.path.join(output_dir, 'telecom_quarterly_sentiment.csv')
    quarterly_sentiment.to_csv(quarterly_out, index=False)
    print(f"\n[DONE] Saved Quarterly Sentiment Aggregations for Azure ML to {quarterly_out}")
    print(f"Total quarterly records: {len(quarterly_sentiment)}")
    print(quarterly_sentiment.head(8))
    
    return df, quarterly_sentiment

if __name__ == '__main__':
    run_sentiment_pipeline()
