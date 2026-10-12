"""
F2: Ekstraksi Passage tentang Makhluk
Mengambil kandidat passage (paragraf) yang merepresentasikan Makhluk dari ketiga sudut pandang narator.
"""

import re
import json
import pandas as pd
import nltk

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    try:
        nltk.download('punkt', quiet=True)
        nltk.download('punkt_tab', quiet=True)
    except Exception:
        pass

def load_designations(filepath: str) -> list[str]:
    with open(filepath, 'r', encoding='utf-8') as f:
        terms = [line.strip().lower() for line in f if line.strip()]
    return terms

def split_long_passage(text: str, max_words: int = 200) -> list[str]:
    """Jika paragraf lebih dari 200 kata, potong pada batas kalimat (FR-2.1)."""
    words = text.split()
    if len(words) <= max_words:
        return [text]

    # Coba gunakan sentence tokenizer
    try:
        sentences = nltk.sent_tokenize(text)
    except Exception:
        sentences = re.split(r'(?<=[.!?])\s+', text)

    chunks = []
    current_chunk = []
    current_count = 0

    for sent in sentences:
        sent_words = len(sent.split())
        if current_count + sent_words > max_words and current_chunk:
            chunks.append(" ".join(current_chunk))
            current_chunk = [sent]
            current_count = sent_words
        else:
            current_chunk.append(sent)
            current_count += sent_words

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks

def extract_passages(corpus_jsonl: str, designations_file: str, output_csv: str):
    designations = load_designations(designations_file)
    # Buat regex pattern untuk pencocokan term (termasuk plural 's'/'es')
    designation_patterns = [
        (term, re.compile(rf'\b{re.escape(term)}(?:s|es)?\b', re.IGNORECASE))
        for term in designations
    ]

    candidates = []
    passage_id_counter = 0

    with open(corpus_jsonl, 'r', encoding='utf-8') as f:
        for line in f:
            seg = json.loads(line)
            narrator = seg['narrator']
            text = seg['text']

            # Potong jika lebih dari 200 kata
            text_chunks = split_long_passage(text, max_words=200)

            for chunk_idx, chunk in enumerate(text_chunks):
                # Cari kata pemicu (trigger terms)
                matched_triggers = []
                for term, pat in designation_patterns:
                    if pat.search(chunk):
                        matched_triggers.append(term)

                is_candidate = False
                # Aturan Walton & Victor (FR-2.2): harus ada kata pemicu
                if narrator in ["Walton", "Victor"]:
                    if matched_triggers:
                        is_candidate = True
                # Aturan Makhluk (FR-2.3): narasi first-person Makhluk
                elif narrator == "Makhluk":
                    # Makhluk menceritakan pengalamannya, emosinya, atau interaksinya
                    # Cek keberadaan 'I', 'me', 'my', 'myself', atau trigger terms
                    first_person_match = re.search(r'\b(I|me|my|myself)\b', chunk, re.IGNORECASE)
                    if first_person_match or matched_triggers:
                        is_candidate = True
                        if not matched_triggers:
                            matched_triggers = ["first_person_narration"]

                if is_candidate:
                    passage_id_counter += 1
                    candidates.append({
                        "passage_id": f"PAS_{passage_id_counter:04d}",
                        "segment_id": seg['segment_id'],
                        "volume": seg['volume'],
                        "section": seg['section'],
                        "narrator": narrator,
                        "chunk_index": chunk_idx,
                        "word_count": len(chunk.split()),
                        "trigger_terms": ", ".join(matched_triggers),
                        "text": chunk
                    })

    df_candidates = pd.DataFrame(candidates)
    df_candidates.to_csv(output_csv, index=False)

    print("=== F2 Candidate Passages Summary ===")
    print(f"Total Extracted Passages: {len(df_candidates)}")
    print(df_candidates.groupby('narrator').agg(
        passages=('passage_id', 'count'),
        avg_words=('word_count', 'mean')
    ))

if __name__ == "__main__":
    corpus_file = "data/corpus.jsonl"
    desig_file = "data/designations.txt"
    out_file = "data/passages.csv"
    extract_passages(corpus_file, desig_file, out_file)
