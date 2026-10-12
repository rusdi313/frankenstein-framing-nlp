import os
import re
import pandas as pd
import numpy as np

# Load source datasets
df_gold = pd.read_csv('data/gold.csv')
df_pred = pd.read_csv('results/predictions_logreg_original.csv')
df_vader = pd.read_csv('data/vader_scores.csv')

# Merge
df_all = df_gold.merge(df_pred, on='passage_id', how='left')
df_all = df_all.merge(df_vader[['passage_id', 'compound_score', 'predicted_label']].rename(
    columns={'compound_score': 'vader_compound', 'predicted_label': 'vader_prediction'}), on='passage_id', how='left')

# Translation mappings
label_map_en = {'Ancaman': 'Threat', 'Korban': 'Victim', 'Ambivalen': 'Ambivalent'}
narrator_map_en = {'Makhluk': 'Creature', 'Victor': 'Victor', 'Walton': 'Walton'}

df_all['gold_label_en'] = df_all['label'].map(label_map_en)
df_all['pred_label_en'] = df_all['pred_label'].map(label_map_en)
df_all['narrator_en'] = df_all['narrator'].map(narrator_map_en)
df_all['vader_prediction_en'] = df_all['vader_prediction'].map(label_map_en)
df_all['is_correct'] = df_all['label'] == df_all['pred_label']
df_all['status_klasifikasi'] = df_all['is_correct'].apply(lambda x: 'BENAR (Correct)' if x else 'SALAH (Misclassified)')

# Reorder columns for clean presentation
cols_195 = [
    'passage_id', 'volume', 'section', 'narrator', 'narrator_en',
    'label', 'gold_label_en', 'pred_label', 'pred_label_en',
    'status_klasifikasi', 'fold', 'vader_compound', 'vader_prediction',
    'text'
]
df_195_export = df_all[cols_195].copy()

# Detailed error classification for 65 errors
df_errors = df_all[~df_all['is_correct']].copy()

def classify_error(row):
    gold = row['label']
    pred = row['pred_label']
    text = row['text']
    text_lower = text.lower()
    
    direction = f"{gold} → {pred}"
    direction_en = f"{label_map_en[gold]} → {label_map_en[pred]}"
    
    # Check error sources
    has_shift = bool(re.search(r'\b(but|yet|however|although|nevertheless|instead|suddenly|altered|while)\b', text_lower))
    has_dialogue = bool(re.search(r'["“”\']', text)) and any(w in text_lower for w in ['said', 'cried', 'replied', 'exclaimed', 'asked', 'whispered'])
    
    sources = []
    analysis = []
    
    if gold == 'Ambivalen':
        sources.append("Ambivalent Framing Collapse (Dualitas Moral & Emosional)")
        if pred == 'Korban':
            analysis.append("Passage memuat penderitaan mendalam ('misery', 'alone', 'pity') bersamaan dengan potensi/ancaman jahat, namun model n-gram didominasi oleh fitur afektif Korban.")
        else: # Ancaman
            analysis.append("Passage memuat pengakuan penderitaan yang melahirkan dendam ('misery made me a fiend'), tetapi model mengabaikan relasi kausalitas antar klausa dan hanya menangkap leksikon permusuhan/ancaman.")
    
    if gold == 'Ancaman' and pred == 'Korban':
        sources.append("Affect-Laden Threat Vocabulary (Kosakata Afektif Terserap Korban)")
        analysis.append("Pernyataan ancaman atau pemonsteran diungkapkan melalui tuturan bersudut pandang orang pertama atau ratapan luka hati yang berbagi kosakata leksikal intens dengan kelas Korban.")
        
    if gold == 'Korban' and pred == 'Ancaman':
        sources.append("Suffering-Threat Lexical Overlap (Penderitaan Berkosakata Ekstrem)")
        analysis.append("Kondisi korban dideskripsikan dengan kata-kata ekstrem (seperti 'agony', 'hell', 'dread', 'horror') yang oleh TF-IDF terbobot kuat ke leksikon Ancaman.")

    if has_dialogue:
        sources.append("Embedded Dialogue / Quoted Speech (Ucapan Langsung Tokoh Lain)")
        analysis.append("Passage memuat ujaran langsung/kutipan dialog tokoh lain (misal Victor mengutip kutukan Makhluk), di mana model bag-of-words gagal membedakan suara penutur (voice) vs perspektif (focalization).")

    if has_shift:
        sources.append("Intra-Paragraph Emotional Shift (Pergeseran Emosi Antar Klausa)")
        analysis.append("Terdapat transisi emosional kontras (ditandai konjungsi adversatif) di mana nada awal simpatik berubah menjadi sumpah permusuhan di akhir kalimat/paragraf.")
        
    source_str = "; ".join(sources) if sources else "Lexical Overlap / Subtle Contextual Nuance"
    analysis_str = " ".join(analysis)
    
    return pd.Series([direction, direction_en, source_str, analysis_str])

df_errors[['arah_kesalahan', 'error_direction_en', 'sumber_kesalahan_utama', 'catatan_analisis_linguistik_sastra']] = df_errors.apply(classify_error, axis=1)

cols_65 = [
    'passage_id', 'volume', 'section', 'narrator', 'narrator_en',
    'label', 'gold_label_en', 'pred_label', 'pred_label_en',
    'arah_kesalahan', 'error_direction_en', 'sumber_kesalahan_utama',
    'fold', 'catatan_analisis_linguistik_sastra', 'text'
]
df_65_export = df_errors[cols_65].copy()

# Export paths
paths = [
    ('results/all_195_passages_oof_predictions', df_195_export),
    ('results/misclassified_65_passages_detailed', df_65_export),
    ('Revisi/Data_Prediksi_OOF_195_Passage_Frankenstein', df_195_export),
    ('Revisi/Daftar_65_Passage_Salah_Klasifikasi_Analisis_Sastra_Linguistik', df_65_export)
]

for base_path, df_exp in paths:
    df_exp.to_csv(f"{base_path}.csv", index=False, encoding='utf-8-sig')
    df_exp.to_excel(f"{base_path}.xlsx", index=False, engine='openpyxl')
    print(f"Exported {base_path}.csv and .xlsx ({len(df_exp)} rows)")

print("\n=== SEMUA FILE PENDUKUNG UNTUK DOSEN SASTRA & LINGUISTIK BERHASIL DIEKSPOR ===")
