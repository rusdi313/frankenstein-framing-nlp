"""
F4: Ekstraksi Fitur TF-IDF (Teks Asli & Teks Masked)
Menyediakan pipeline ekstraksi fitur TF-IDF dan fungsi masking leksikal untuk pencegahan kebocoran.
"""

import re
from sklearn.feature_extraction.text import TfidfVectorizer

def load_designations(designations_path: str = "data/designations.txt") -> list[str]:
    with open(designations_path, 'r', encoding='utf-8') as f:
        return [line.strip().lower() for line in f if line.strip()]

def mask_designations(text: str, designations: list[str]) -> str:
    """Mengganti semua sebutan spesifik Makhluk dengan token netral CREATURE (FR-4.3)."""
    masked_text = text
    for term in sorted(designations, key=len, reverse=True):
        # Cocokkan bentuk tunggal & jamak
        pattern = re.compile(rf'\b{re.escape(term)}(?:s|es)?\b', re.IGNORECASE)
        masked_text = pattern.sub("CREATURE", masked_text)
    return masked_text

def get_tfidf_vectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True) -> TfidfVectorizer:
    """Mengembalikan TfidfVectorizer terkonfigurasi sesuai spesifikasi FR-4.1 & FR-4.2."""
    return TfidfVectorizer(
        ngram_range=ngram_range,
        min_df=min_df,
        sublinear_tf=sublinear_tf,
        lowercase=True,
        stop_words=None  # Stopword dipertahankan untuk mempertahankan sudut pandang naratif
    )
