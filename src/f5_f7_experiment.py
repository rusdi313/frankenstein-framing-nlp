"""
F5 & F7: Pelatihan Model, Validasi Silang (5-Fold Stratified CV) & Evaluasi Lengkap
Membandingkan Dummy Classifier (Mayoritas), VADER, Naive Bayes, SVM, dan Logistic Regression pada varian Asli & Masked.
"""

import os
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.dummy import DummyClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, precision_recall_fscore_support,
    confusion_matrix, ConfusionMatrixDisplay
)

from features import load_designations, mask_designations, get_tfidf_vectorizer
from f6_vader import run_vader_baseline

LABELS = ["Ancaman", "Korban", "Ambivalen"]

def run_experiment(gold_path: str = "data/gold.csv"):
    df_gold = pd.read_csv(gold_path)
    designations = load_designations("data/designations.txt")

    # Siapkan varian teks
    df_gold['text_original'] = df_gold['text'].astype(str)
    df_gold['text_masked'] = df_gold['text_original'].apply(lambda t: mask_designations(t, designations))

    X_orig = df_gold['text_original'].values
    X_mask = df_gold['text_masked'].values
    y = df_gold['label'].values

    # 5-Fold Stratified K-Fold
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    # Bobot kelas custom untuk memberi perhatian pada Ambivalen (minoritas)
    class_weights = {"Ancaman": 1.0, "Korban": 1.0, "Ambivalen": 2.2}

    models = {
        "Majority Baseline": lambda: DummyClassifier(strategy="most_frequent"),
        "Multinomial NB": lambda: MultinomialNB(),
        "Linear SVM": lambda: LinearSVC(class_weight=class_weights, random_state=42, max_iter=2000),
        "Logistic Regression": lambda: LogisticRegression(class_weight=class_weights, random_state=42, max_iter=1000)
    }

    variants = ["Original", "Masked"]
    all_results = []
    predictions_store = {}
    aggregated_cms = {}

    # Jalankan VADER
    df_vader = run_vader_baseline(gold_path, "data/vader_scores.csv")
    vader_preds = df_vader['predicted_label'].values

    # Evaluasi per model dan per varian
    for var_name in variants:
        X_data = X_orig if var_name == "Original" else X_mask

        for model_name, model_fn in models.items():
            fold_accs = []
            fold_macro_f1s = []
            fold_macro_precisions = []
            fold_macro_recalls = []

            fold_threat_f1 = []
            fold_victim_f1 = []
            fold_ambiv_f1 = []

            all_y_true = []
            all_y_pred = []
            passage_preds = []

            for fold_idx, (train_idx, test_idx) in enumerate(skf.split(X_data, y)):
                X_train, X_test = X_data[train_idx], X_data[test_idx]
                y_train, y_test = y[train_idx], y[test_idx]
                test_pids = df_gold.iloc[test_idx]['passage_id'].values

                if model_name == "Majority Baseline":
                    clf = model_fn()
                    clf.fit(X_train, y_train)
                    y_pred = clf.predict(X_test)
                else:
                    pipeline = Pipeline([
                        ('tfidf', get_tfidf_vectorizer()),
                        ('clf', model_fn())
                    ])
                    pipeline.fit(X_train, y_train)
                    y_pred = pipeline.predict(X_test)

                for pid, yt, yp in zip(test_pids, y_test, y_pred):
                    passage_preds.append({"passage_id": pid, "true_label": yt, "pred_label": yp, "fold": fold_idx + 1})

                all_y_true.extend(y_test)
                all_y_pred.extend(y_pred)

                acc = accuracy_score(y_test, y_pred)
                p_macro, r_macro, f1_macro, _ = precision_recall_fscore_support(y_test, y_pred, average='macro', zero_division=0)
                p_cls, r_cls, f1_cls, _ = precision_recall_fscore_support(y_test, y_pred, labels=LABELS, zero_division=0)

                fold_accs.append(acc)
                fold_macro_f1s.append(f1_macro)
                fold_macro_precisions.append(p_macro)
                fold_macro_recalls.append(r_macro)

                fold_threat_f1.append(f1_cls[0])
                fold_victim_f1.append(f1_cls[1])
                fold_ambiv_f1.append(f1_cls[2])

            pm = "±"
            all_results.append({
                "Model": model_name,
                "Variant": var_name,
                "Accuracy": f"{np.mean(fold_accs)*100:.2f} {pm} {np.std(fold_accs)*100:.2f}",
                "Macro-Precision": f"{np.mean(fold_macro_precisions)*100:.2f} {pm} {np.std(fold_macro_precisions)*100:.2f}",
                "Macro-Recall": f"{np.mean(fold_macro_recalls)*100:.2f} {pm} {np.std(fold_macro_recalls)*100:.2f}",
                "Macro-F1": f"{np.mean(fold_macro_f1s)*100:.2f} {pm} {np.std(fold_macro_f1s)*100:.2f}",
                "Threat F1": f"{np.mean(fold_threat_f1)*100:.2f} {pm} {np.std(fold_threat_f1)*100:.2f}",
                "Victim F1": f"{np.mean(fold_victim_f1)*100:.2f} {pm} {np.std(fold_victim_f1)*100:.2f}",
                "Ambivalent F1": f"{np.mean(fold_ambiv_f1)*100:.2f} {pm} {np.std(fold_ambiv_f1)*100:.2f}",
                "raw_macro_f1_mean": np.mean(fold_macro_f1s)
            })

            predictions_store[f"{model_name}_{var_name}"] = pd.DataFrame(passage_preds)
            aggregated_cms[f"{model_name}_{var_name}"] = confusion_matrix(all_y_true, all_y_pred, labels=LABELS)

    # Evaluasi VADER
    vader_accs = []
    vader_macro_f1s = []
    vader_macro_ps = []
    vader_macro_rs = []
    vader_threat_f1 = []
    vader_victim_f1 = []
    vader_ambiv_f1 = []

    for fold_idx, (train_idx, test_idx) in enumerate(skf.split(X_orig, y)):
        y_test = y[test_idx]
        y_pred = vader_preds[test_idx]

        acc = accuracy_score(y_test, y_pred)
        p_macro, r_macro, f1_macro, _ = precision_recall_fscore_support(y_test, y_pred, average='macro', zero_division=0)
        p_cls, r_cls, f1_cls, _ = precision_recall_fscore_support(y_test, y_pred, labels=LABELS, zero_division=0)

        vader_accs.append(acc)
        vader_macro_f1s.append(f1_macro)
        vader_macro_ps.append(p_macro)
        vader_macro_rs.append(r_macro)
        vader_threat_f1.append(f1_cls[0])
        vader_victim_f1.append(f1_cls[1])
        vader_ambiv_f1.append(f1_cls[2])

    for var in ["Original", "Masked"]:
        pm = "±"
        all_results.append({
            "Model": "VADER Lexicon",
            "Variant": var,
            "Accuracy": f"{np.mean(vader_accs)*100:.2f} {pm} {np.std(vader_accs)*100:.2f}",
            "Macro-Precision": f"{np.mean(vader_macro_ps)*100:.2f} {pm} {np.std(vader_macro_ps)*100:.2f}",
            "Macro-Recall": f"{np.mean(vader_macro_rs)*100:.2f} {pm} {np.std(vader_macro_rs)*100:.2f}",
            "Macro-F1": f"{np.mean(vader_macro_f1s)*100:.2f} {pm} {np.std(vader_macro_f1s)*100:.2f}",
            "Threat F1": f"{np.mean(vader_threat_f1)*100:.2f} {pm} {np.std(vader_threat_f1)*100:.2f}",
            "Victim F1": f"{np.mean(vader_victim_f1)*100:.2f} {pm} {np.std(vader_victim_f1)*100:.2f}",
            "Ambivalent F1": f"{np.mean(vader_ambiv_f1)*100:.2f} {pm} {np.std(vader_ambiv_f1)*100:.2f}",
            "raw_macro_f1_mean": np.mean(vader_macro_f1s)
        })

    # Simpan tabel hasil komparasi
    df_results = pd.DataFrame(all_results)
    df_results = df_results.sort_values(by=["Variant", "raw_macro_f1_mean"], ascending=[True, False]).drop(columns=["raw_macro_f1_mean"])
    df_results.to_csv("results/results_table.csv", index=False)

    print("\n=== HASIL UTAMA EKSPERIMEN (5-Fold CV) ===")
    print(df_results.to_markdown(index=False))

    # Simpan Prediksi & Misclassifications
    best_model_key_orig = "Logistic Regression_Original"
    best_model_key_mask = "Logistic Regression_Masked"

    predictions_store[best_model_key_orig].to_csv("results/predictions_logreg_original.csv", index=False)
    predictions_store[best_model_key_mask].to_csv("results/predictions_logreg_masked.csv", index=False)

    merged_errors = df_gold.merge(predictions_store[best_model_key_orig], on="passage_id")
    errors_df = merged_errors[merged_errors['label'] != merged_errors['pred_label']]
    sample_errors = errors_df[['passage_id', 'volume', 'section', 'narrator', 'label', 'pred_label', 'text']].head(20)
    sample_errors.to_csv("results/misclassified.csv", index=False)

    # Gambar Confusion Matrix (300 DPI)
    for key, title_suffix, filename in [
        (best_model_key_orig, "Logistic Regression (Original)", "figures/confusion_matrix_logreg_original.png"),
        (best_model_key_mask, "Logistic Regression (Masked)", "figures/confusion_matrix_logreg_masked.png"),
        ("Linear SVM_Original", "Linear SVM (Original)", "figures/confusion_matrix_svm_original.png"),
        ("Linear SVM_Masked", "Linear SVM (Masked)", "figures/confusion_matrix_svm_masked.png")
    ]:
        cm = aggregated_cms[key]
        fig, ax = plt.subplots(figsize=(6, 5), dpi=300)
        disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=LABELS)
        disp.plot(cmap=plt.cm.Blues, ax=ax, colorbar=False)
        ax.set_title(f"Confusion Matrix: {title_suffix}", fontsize=12, pad=10, fontweight='bold')
        ax.set_xlabel("Predicted Framing", fontsize=10, fontweight='semibold')
        ax.set_ylabel("True Framing (Gold Standard)", fontsize=10, fontweight='semibold')
        plt.tight_layout()
        plt.savefig(filename, dpi=300)
        plt.close(fig)

    print("\nVisualisasi Confusion Matrix berhasil disimpan ke folder 'figures/'.")

if __name__ == "__main__":
    run_experiment()
