"""
F1: Akuisisi & Praproses Korpus Frankenstein (1818 Edition)
Memecah teks novel menjadi segmen terstruktur (Volume, Chapter/Letter, Paragraf, Narator).
"""

import os
import re
import json
import pandas as pd

def clean_text(text: str) -> str:
    """Normalisasi tanda kutip, dash, dan whitespace."""
    text = text.replace('“', '"').replace('”', '"').replace('‘', "'").replace('’', "'")
    text = text.replace('—', ' -- ').replace('–', ' -- ')
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()

def process_corpus(raw_path: str, output_jsonl: str, output_narrator_map: str):
    with open(raw_path, 'r', encoding='utf-8') as f:
        raw_content = f.read()

    # Hapus Header dan Footer Project Gutenberg (FR-1.3)
    start_match = re.search(r'\*\*\* START OF THE PROJECT GUTENBERG EBOOK.*?\*\*\*', raw_content)
    end_match = re.search(r'\*\*\* END OF THE PROJECT GUTENBERG EBOOK.*?\*\*\*', raw_content)

    if start_match:
        content = raw_content[start_match.end():]
    else:
        content = raw_content

    if end_match:
        content = content[:content.find('*** END OF THE PROJECT GUTENBERG')]

    letter1_idx = content.find("LETTER I.")
    if letter1_idx != -1:
        novel_text = content[letter1_idx:]
    else:
        novel_text = content

    lines = novel_text.split('\n')
    
    current_vol = "VOL. I"
    current_section = "LETTER I"
    current_narrator = "Walton"
    
    segments = []
    current_para_lines = []
    segment_id = 0
    para_no_in_section = 0
    
    narrator_records = []

    def flush_paragraph():
        nonlocal segment_id, para_no_in_section
        if current_para_lines:
            para_text = clean_text(" ".join(current_para_lines))
            if para_text and len(para_text.split()) >= 3:
                segment_id += 1
                para_no_in_section += 1
                segments.append({
                    "segment_id": f"SEG_{segment_id:04d}",
                    "volume": current_vol,
                    "section": current_section,
                    "paragraph_no": para_no_in_section,
                    "narrator": current_narrator,
                    "word_count": len(para_text.split()),
                    "text": para_text
                })
            current_para_lines.clear()

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Deteksi Header Volume (misal: 'VOL. II.', 'VOL. III.')
        vol_search = re.search(r'VOL\.\s*(III|II|I)\b', line, re.I)
        if vol_search and not line.startswith("END OF"):
            flush_paragraph()
            current_vol = f"VOL. {vol_search.group(1).upper()}"
            i += 1
            continue

        # Deteksi Header Letter
        if re.match(r'^LETTER\s+[IVXLCDM]+\.?', line, re.I):
            flush_paragraph()
            current_section = f"{current_vol} - {line.strip('.').upper()}"
            current_narrator = "Walton"
            para_no_in_section = 0
            narrator_records.append({"volume": current_vol, "section": current_section, "narrator": current_narrator})
            i += 1
            continue

        # Deteksi Header Chapter
        if re.match(r'^CHAPTER\s+[IVXLCDM]+\.?', line, re.I):
            flush_paragraph()
            chap_match = re.search(r'CHAPTER\s+([IVXLCDM]+)', line, re.I)
            chap_roman = chap_match.group(1).upper() if chap_match else ""
            current_section = f"{current_vol} - CHAPTER {chap_roman}"
            para_no_in_section = 0
            
            # Peta Narator sesuai FR-1.5 & FR-1.6
            if current_vol == "VOL. I":
                current_narrator = "Victor"
            elif current_vol == "VOL. II":
                # Bab III sampai VIII adalah kisah Makhluk sendiri
                if chap_roman in ["III", "IV", "V", "VI", "VII", "VIII"]:
                    current_narrator = "Makhluk"
                else:
                    current_narrator = "Victor"
            elif current_vol == "VOL. III":
                current_narrator = "Victor"
                
            narrator_records.append({"volume": current_vol, "section": current_section, "narrator": current_narrator})
            i += 1
            continue

        # Deteksi Walton continuation di akhir Vol III
        if "walton, in continuation" in line.lower() or "walton's continuation" in line.lower() or "august 26th, 17--" in line.lower():
            flush_paragraph()
            current_section = "VOL. III - WALTON CONTINUATION"
            current_narrator = "Walton"
            para_no_in_section = 0
            narrator_records.append({"volume": current_vol, "section": current_section, "narrator": current_narrator})
            if line:
                current_para_lines.append(line)
            i += 1
            continue

        if line == "" or line.startswith("END OF VOL."):
            flush_paragraph()
        else:
            current_para_lines.append(line)
        i += 1

    flush_paragraph()

    # Simpan corpus.jsonl
    with open(output_jsonl, 'w', encoding='utf-8') as f:
        for seg in segments:
            f.write(json.dumps(seg, ensure_ascii=False) + '\n')

    # Simpan narrator_map.csv
    df_narrator = pd.DataFrame(narrator_records).drop_duplicates()
    df_narrator.to_csv(output_narrator_map, index=False)

    df_segments = pd.DataFrame(segments)
    summary = df_segments.groupby('narrator').agg(
        paragraphs=('segment_id', 'count'),
        total_words=('word_count', 'sum'),
        avg_words_per_para=('word_count', 'mean')
    ).reset_index()

    print("=== F1 Corpus Summary ===")
    print(f"Total Segments: {len(segments)}")
    print(f"Total Words: {df_segments['word_count'].sum():,}")
    print(summary.to_string(index=False))

    # Tulis README sumber
    readme_path = "data/README_corpus.md"
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write("# Dokumentasi Korpus Frankenstein (1818 Text)\n\n")
        f.write("- **Sumber Primer**: Project Gutenberg EBook #41445 (Photo-reprint of 1818 first edition).\n")
        f.write("- **Total Paragraf**: {}\n".format(len(segments)))
        f.write("- **Total Kata**: {}\n\n".format(df_segments['word_count'].sum()))
        f.write("## Distribusi Narator\n\n")
        f.write("| Narator | Paragraf | Total Kata | Rata-rata Kata/Paragraf |\n")
        f.write("| :--- | :--- | :--- | :--- |\n")
        for _, row in summary.iterrows():
            f.write(f"| {row['narrator']} | {row['paragraphs']} | {row['total_words']:,} | {row['avg_words_per_para']:.2f} |\n")
        f.write("\n")

if __name__ == "__main__":
    raw_file = "Dataset/frankenstein_1818_gutenberg.txt"
    jsonl_file = "data/corpus.jsonl"
    narrator_map_file = "data/narrator_map.csv"
    process_corpus(raw_file, jsonl_file, narrator_map_file)
