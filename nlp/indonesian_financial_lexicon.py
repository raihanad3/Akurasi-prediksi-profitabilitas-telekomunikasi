"""
Domain-Specific Indonesian Financial & Telecom Industry Sentiment Lexicon
Tailored for:
- Emiten Telekomunikasi (TLKM, ISAT, EXCL)
- Laporan Keuangan (Laba bersih, Pendapatan, EBITDA, Margin, ROA, ROE)
- Belanja Modal (Capex), Utang, Valas/Kurs, Suku Bunga
- Aksi Korporasi (Merger, Akuisisi, Spin-off Infraco, Data Center AI)
"""

# Strong Positive (+2.0 weight)
STRONG_POSITIVE = {
    'meroket', 'melonjak', 'rekor', 'tertinggi', 'melesat', 'jumbo', 'cemerlang',
    'fantastis', 'berkilau', 'gemilang', 'melambung', 'luar biasa', 'moncer',
    'menggiurkan', 'terunggul', 'spektakuler', 'merajai', 'menanjak tajam'
}

# Positive (+1.0 weight)
POSITIVE = {
    'laba', 'untung', 'naik', 'meningkat', 'tumbuh', 'pertumbuhan', 'positif',
    'dividen', 'penguatan', 'menguat', 'ekspansi', 'akuisisi', 'sinergi',
    'sukses', 'optimis', 'optimistis', 'bullish', 'rekomendasi', 'buy',
    'target harga', 'unggul', 'efisiensi', 'prospek', 'investasi', 'kinerja',
    'keuntungan', 'pemulihan', 'berkembang', 'potensi', 'menjanjikan',
    'surplus', 'apresiasi', 'penambahan', 'peluang', 'inovasi', 'kolaborasi',
    'mitra', 'terpercaya', 'berhasil', 'stabil', 'solid', 'kokoh', 'tahan banting'
}

# Strong Negative (-2.0 weight)
STRONG_NEGATIVE = {
    'anjlok', 'ambles', 'terjun', 'terperosok', 'terburuk', 'terendah',
    'bangkrut', 'pailit', 'kolaps', 'merosot tajam', 'kehancuran', 'goncangan',
    'kerugian besar', 'gagal total', 'denda', 'gugatan', 'tersandung'
}

# Negative (-1.0 weight)
NEGATIVE = {
    'rugi', 'turun', 'merosot', 'penurunan', 'melemah', 'pelemahan', 'negatif',
    'tekanan', 'tertekan', 'beban', 'utang', 'koreksi', 'lesu', 'jatuh',
    'terpangkas', 'perlambatan', 'lambat', 'terkikis', 'risiko', 'waspada',
    'defisit', 'ancaman', 'sengketa', 'terbebani', 'susut', 'menyusut',
    'pesimis', 'bearish', 'sell', 'downgrade', 'inflasi', 'volatilitas',
    'ketidakpastian', 'hambatan', 'kendala', 'kehilangan', 'tergerus'
}

# Negation words that flip polarity
NEGATIONS = {
    'tidak', 'bukan', 'belum', 'tanpa', 'tak', 'tiada', 'jangan', 'kurang'
}

# Intensifiers (amplifies preceding/subsequent word by 1.5x)
INTENSIFIERS = {
    'sangat', 'amat', 'makin', 'kian', 'semakin', 'signifikan', 'drastis',
    'tajam', 'benar-benar', 'sungguh', 'teramat', 'banyak'
}

# Diminishers (reduces preceding/subsequent word by 0.5x)
DIMINISHERS = {
    'sedikit', 'agak', 'tipis', 'kurang', 'perlahan', 'moderat', 'cenderung'
}
