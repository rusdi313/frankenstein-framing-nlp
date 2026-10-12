"""
F6: Baseline VADER (Sentiment-Based Framing Baseline)
Menghitung skor sentimen VADER per passage dan memetakan ke 3 label (Ancaman, Korban, Ambivalen).
"""

import pandas as pd
import numpy as np
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon', quiet=True)

def run_vader_baseline(gold_csv: str = "data/gold.csv", output_csv: str = "data/vader_scores.csv"):
    df = pd.read_csv(gold_csv)
    sia = SentimentIntensityAnalyzer()

    results = []

    for _, row in df.iterrows():
        text = str(row['text'])
        # Tokenisasi kalimat untuk merata-ratakan skor compound (FR-6.1)
        try:
            sentences = nltk.sent_tokenize(text)
        except Exception:
            sentences = [text]

        compounds = [sia.polarity_scores(s)['compound'] for s in sentences]
        avg_compound = float(np.mean(compounds)) if compounds else 0.0

        # Aturan pemetaan standar FR-6.2
        if avg_compound <= -0.05:
            pred_label = "Ancaman"
        elif avg_compound >= 0.05:
            pred_label = "Korban"
        else:
            pred_label = "Ambivalen"

        results.append({
            "passage_id": row['passage_id'],
            "narrator": row['narrator'],
            "true_label": row['label'],
            "compound_score": round(avg_compound, 4),
            "predicted_label": pred_label
        })

    df_res = pd.DataFrame(results)
    df_res.to_csv(output_csv, index=False)
    print(f"=== F6 VADER Baseline Computed ({len(df_res)} passages) ===")
    return df_res

if __name__ == "__main__":
    run_vader_baseline()
