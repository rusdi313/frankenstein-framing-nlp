"""
F8: Analisis Interpretabilitas Leksikal & Distribusi per Narator
Mengekstrak bobot fitur teratas dari Logistic Regression, distribusi representasi per narator, dan visualisasi.
"""

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from features import load_designations, mask_designations, get_tfidf_vectorizer

LABELS = ["Ancaman", "Korban", "Ambivalen"]

def run_interpretability(gold_path: str = "data/gold.csv"):
    df_gold = pd.read_csv(gold_path)
    designations = load_designations("data/designations.txt")

    df_gold['text_original'] = df_gold['text'].astype(str)
    df_gold['text_masked'] = df_gold['text_original'].apply(lambda t: mask_designations(t, designations))

    # 1. Distribusi Gold Label Berdasarkan Narator (FR-8.4)
    narrator_cross = pd.crosstab(df_gold['narrator'], df_gold['label'], margins=True)
    narrator_norm = pd.crosstab(df_gold['narrator'], df_gold['label'], normalize='index') * 100

    narrator_summary = []
    for narr in ["Victor", "Makhluk", "Walton"]:
        if narr in narrator_cross.index:
            narrator_summary.append({
                "Narator": narr,
                "Total Passage": narrator_cross.loc[narr, 'All'],
                "Ancaman (n / %)": f"{narrator_cross.loc[narr, 'Ancaman']} ({narrator_norm.loc[narr, 'Ancaman']:.1f}%)",
                "Korban (n / %)": f"{narrator_cross.loc[narr, 'Korban']} ({narrator_norm.loc[narr, 'Korban']:.1f}%)",
                "Ambivalen (n / %)": f"{narrator_cross.loc[narr, 'Ambivalen']} ({narrator_norm.loc[narr, 'Ambivalen']:.1f}%)",
            })

    df_narr_summary = pd.DataFrame(narrator_summary)
    df_narr_summary.to_csv("results/label_by_narrator.csv", index=False)

    # Visualisasi Bar Chart Distribusi Narasi (300 DPI)
    fig, ax = plt.subplots(figsize=(7, 4.5), dpi=300)
    plot_df = narrator_norm.loc[["Victor", "Makhluk", "Walton"], ["Ancaman", "Korban", "Ambivalen"]]
    colors = ["#d9534f", "#5bc0de", "#f0ad4e"] # Merah (Threat), Biru (Victim), Kuning (Ambivalent)
    plot_df.plot(kind='bar', stacked=True, ax=ax, color=colors, edgecolor='black', linewidth=0.7)
    ax.set_title("Framing Distribution by Narrator Level (Frankenstein 1818)", fontsize=11, fontweight='bold', pad=12)
    ax.set_xlabel("Narrator Level", fontsize=10, fontweight='semibold')
    ax.set_ylabel("Proportion of Passages (%)", fontsize=10, fontweight='semibold')
    ax.set_xticklabels(plot_df.index, rotation=0)
    ax.legend(title="Narrative Framing", frameon=True, facecolor='white', framealpha=1)
    ax.set_ylim(0, 100)
    plt.tight_layout()
    plt.savefig("figures/distribution_narrators.png", dpi=300)
    plt.close(fig)

    # 2. Ekstraksi Bobot Fitur Teratas dari Logistic Regression (FR-8.1 & FR-8.2)
    feature_records = []

    for var_name, col in [("Original", "text_original"), ("Masked", "text_masked")]:
        X = df_gold[col].values
        y = df_gold['label'].values

        vec = get_tfidf_vectorizer()
        X_vec = vec.fit_transform(X)
        feature_names = np.array(vec.get_feature_names_out())

        clf = LogisticRegression(class_weight={"Ancaman": 1.0, "Korban": 1.0, "Ambivalen": 2.2}, random_state=42, max_iter=1000)
        clf.fit(X_vec, y)

        # Ambil top 15 fitur per kelas
        for class_idx, class_label in enumerate(clf.classes_):
            coefs = clf.coef_[class_idx]
            top15_idx = np.argsort(coefs)[-15:][::-1]
            for rank, idx in enumerate(top15_idx, start=1):
                feature_records.append({
                    "Variant": var_name,
                    "Class": class_label,
                    "Rank": rank,
                    "Feature": feature_names[idx],
                    "Coefficient": round(float(coefs[idx]), 4)
                })

    df_features = pd.DataFrame(feature_records)
    df_features.to_csv("results/top_features.csv", index=False)

    print("=== F8 Interpretability & Narrator Distribution Summary ===")
    print("\n--- Distribusi Narator ---")
    print(df_narr_summary.to_markdown(index=False))

    print("\n--- Contoh Fitur Teratas (Varian Masked) ---")
    top_masked = df_features[df_features['Variant'] == 'Masked']
    for cls in LABELS:
        cls_feats = top_masked[top_masked['Class'] == cls].head(8)
        feat_str = ", ".join([f"{r['Feature']} ({r['Coefficient']:.2f})" for _, r in cls_feats.iterrows()])
        print(f"[{cls}]: {feat_str}")

if __name__ == "__main__":
    run_interpretability()
