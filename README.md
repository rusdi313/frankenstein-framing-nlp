# Frankenstein Narrative Framing Classification

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-1.7.2-orange.svg)](https://scikit-learn.org/)
[![License: Public Domain](https://img.shields.io/badge/Text-Public%20Domain%20(1818)-green.svg)](https://www.gutenberg.org/ebooks/41445)

> **Research Topic:** *Classifying the Narrative Framing of the Creature in Mary Shelley's Frankenstein (1818) Using TF-IDF and Machine Learning*  

This repository contains the complete experimental code, annotation guidelines, gold standard dataset, and reproducibility pipeline for analyzing the narrative framing of the Creature across different narrative tiers (*Walton*, *Victor Frankenstein*, and the *Creature*) in Mary Shelley's *Frankenstein* (1818 text, Project Gutenberg #41445).

---

## 📌 Research Overview & Workflow

The pipeline operationalizes the literary debate over the Creature's portrayal into a three-class classification task:
1. **Threat (Ancaman)**: Framing as a monstrous, violent, or vengeful demon.
2. **Victim (Korban)**: Framing as a suffering, rejected outcast longing for empathy and domestic affection.
3. **Ambivalent (Ambivalen)**: Tensions between suffering and vengeance, or moral dualities across narrative clauses (e.g., *"misery made me a fiend"*).

### Dataset Construction Flow
$$\text{340 candidate passages} \xrightarrow{-20\text{ pilot calibration}} \text{320 passages} \xrightarrow{-125\text{ Irrelevant}} \text{195 Gold Standard Passages}$$

* **Gold Standard Distribution (195 passages)**:
  * Threat: 76 passages
  * Victim: 90 passages
  * Ambivalent: 29 passages
* **Inter-Annotator Agreement (Double-Annotated Subset)**:
  * Sample size: 68 passages (34.9% of gold standard)
  * Cohen's Kappa: $\kappa = 0.6926$ (*Substantial Agreement*)

---

## 📂 Repository Structure

```text
├── data/
│   ├── corpus.jsonl                  # Cleaned 1818 Frankenstein text mapped by chapter and narrator
│   ├── designations.txt              # Lexicon of creature-referring epithets (monster, fiend, daemon, etc.)
│   ├── narrator_map.csv              # Mapping of chapters/letters to narrators (Walton, Victor, Creature)
│   ├── passages.csv                  # 340 candidate extracted passages
│   ├── gold.csv                      # Final gold standard dataset (195 passages with verified labels)
│   ├── vader_scores.csv              # VADER compound scores and mapped rule-based predictions
│   ├── annotation_guideline.md       # Operationalized annotation codebook & priority rules
│   └── agreement_report.md           # Inter-annotator reliability metrics & contingency matrix
├── Dataset/
│   └── frankenstein_1818_gutenberg.txt # Raw 1818 novel text (Project Gutenberg #41445)
├── src/
│   ├── f1_corpus.py                  # Step 1: Corpus acquisition and structural cleaning
│   ├── f2_passages.py                # Step 2: Rule-based extraction & long-paragraph splitting
│   ├── f3_annotation.py              # Step 3: Annotation calibration and gold standard extraction
│   ├── features.py                   # Step 4: Sublinear TF-IDF vectorization and lexical masking
│   ├── f5_f7_experiment.py           # Step 5 & 7: Stratified 5-Fold CV model training and evaluation
│   ├── f6_vader.py                   # Step 6: VADER rule-based sentiment baseline
│   └── f8_interpretability.py        # Step 8: Logistic Regression coefficient analysis & narrator breakdown
├── figures/                          # Confusion matrices (300 DPI), distribution charts, and methodology diagram
├── results/                          # CSV & Excel evaluation tables:
│   ├── results_table.csv             # 5-fold CV metrics (Mean ± SD) across all models & variants
│   ├── predictions_logreg_original.csv # Out-of-fold predictions (Logistic Regression, original variant)
│   ├── predictions_logreg_masked.csv   # Out-of-fold predictions (Logistic Regression, masked variant)
│   ├── top_features.csv              # Most influential n-gram coefficients per class
│   ├── all_195_passages_oof_predictions.xlsx / .csv # Complete out-of-fold predictions for all 195 passages
│   └── misclassified_65_passages_detailed.xlsx / .csv # Comprehensive qualitative analysis of 65 misclassifications
├── run_pipeline.py                   # Master runner script executing end-to-end pipeline
├── export_data_for_reviewers.py      # Detailed spreadsheet generator for out-of-fold predictions
├── analyze_errors.py                 # Error categorization & linguistic shift analysis script
├── Pipeline_Frankenstein_SINTA2.ipynb # Interactive Jupyter Notebook replicating the full pipeline
├── requirements.txt                  # Python dependencies
└── README.md
```

---

## ⚙️ Installation & Requirements

Ensure Python 3.10+ (tested on Python 3.12) is installed:

```bash
git clone https://github.com/rusdi313/frankenstein-framing-nlp.git
cd frankenstein-framing-nlp
pip install -r requirements.txt
```

### Key Libraries
- `scikit-learn` (1.7.2)
- `nltk` (3.10.3)
- `pandas` (2.2+)
- `numpy` (1.26+)
- `matplotlib` (3.9+)
- `openpyxl` (3.1+)

---

## 🚀 Running the Experiments

To run the complete pipeline from corpus preprocessing to model evaluation and visualization:

```bash
python run_pipeline.py
```

To run individual components:
```bash
# 1. Feature extraction & model evaluation (Stratified 5-Fold CV)
python src/f5_f7_experiment.py

# 2. Extract interpretability coefficients & generate confusion matrices
python src/f8_interpretability.py

# 3. Export detailed out-of-fold predictions & error breakdown
python export_data_for_reviewers.py
```

---

## 📊 Summary of Experimental Results (Stratified 5-Fold Cross-Validation)

| Model | Variant | Accuracy (%) | Macro-F1 (%) | Threat F1 (%) | Victim F1 (%) | Ambivalent F1 (%) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Logistic Regression** | **Original** | **66.67 ± 5.13** | **47.75 ± 3.64** | **68.84 ± 5.60** | **74.41 ± 6.27** | 0.00 ± 0.00 |
| **Linear SVM** | Original | 64.10 ± 7.25 | 46.18 ± 4.95 | 65.75 ± 7.53 | 72.79 ± 7.71 | 0.00 ± 0.00 |
| **Multinomial NB** | Original | 61.03 ± 4.10 | 42.54 ± 3.05 | 57.27 ± 4.69 | 70.36 ± 4.48 | 0.00 ± 0.00 |
| **Logistic Regression** | Masked | 63.59 ± 4.10 | 45.20 ± 2.96 | 63.54 ± 5.42 | 72.06 ± 5.77 | 0.00 ± 0.00 |
| **Linear SVM** | Masked | 63.59 ± 5.23 | 45.67 ± 3.54 | 65.18 ± 5.39 | 71.83 ± 5.75 | 0.00 ± 0.00 |
| **VADER Baseline** | Diagnostic | 54.36 ± 7.50 | 44.85 ± 7.55 | 56.39 ± 10.72 | 63.44 ± 5.35 | 14.74 ± 13.31 |
| **Majority Baseline** | Minimal Ref. | 46.15 ± 0.00 | 21.05 ± 0.00 | 0.00 ± 0.00 | 63.16 ± 0.00 | 0.00 ± 0.00 |

*Note: Model hyperparameters configured in `src/f5_f7_experiment.py`: Logistic Regression ($C = 1.0$, `solver='lbfgs'`, `class_weight='balanced'`), LinearSVC ($C = 1.0$, `class_weight='balanced'`), MultinomialNB ($\alpha = 1.0$), with a fixed random seed of 42.*

---

## 📜 Citation & License
* The primary text of Mary Shelley's *Frankenstein* (1818) is in the public domain.
* Code and annotations are made available under the MIT License for educational and academic research.
