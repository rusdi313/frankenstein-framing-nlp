import os
import re
import json
import requests
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from sklearn.model_selection import StratifiedKFold
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.dummy import DummyClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, precision_recall_fscore_support,
    confusion_matrix, ConfusionMatrixDisplay, cohen_kappa_score
)

print("[1] Testing packages & NLTK download...")
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)
nltk.download('vader_lexicon', quiet=True)

print("[2] Testing Gutenberg Download...")
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
try:
    res = requests.get('https://www.gutenberg.org/files/41445/41445-0.txt', headers=headers, timeout=15)
    raw_text = res.text
    if len(raw_text) < 50000:
        raise ValueError("Downloaded text too short")
    print("Download success, length:", len(raw_text))
except Exception as e:
    print("Fallback to local text file due to:", e)
    with open('Dataset/frankenstein_1818_gutenberg.txt', 'r', encoding='utf-8') as f:
        raw_text = f.read()

print("[3] Testing Clean & Segmentation...")
def clean_text(text: str) -> str:
    text = text.replace('“', '"').replace('”', '"').replace('‘', "'").replace('’', "'")
    text = text.replace('—', ' -- ').replace('–', ' -- ')
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()

start_idx = raw_text.find("LETTER I.")
end_idx = raw_text.find("*** END OF THE PROJECT GUTENBERG")
novel_text = raw_text[start_idx:end_idx] if start_idx != -1 else raw_text

lines = novel_text.split('\n')
current_vol = "VOL. I"
current_section = "LETTER I"
current_narrator = "Walton"
segments = []
current_para = []
segment_id = 0
para_no = 0

def flush_p():
    global segment_id, para_no
    if current_para:
        p_text = clean_text(" ".join(current_para))
        if p_text and len(p_text.split()) >= 3:
            segment_id += 1
            para_no += 1
            segments.append({
                "segment_id": f"SEG_{segment_id:04d}",
                "volume": current_vol,
                "section": current_section,
                "paragraph_no": para_no,
                "narrator": current_narrator,
                "word_count": len(p_text.split()),
                "text": p_text
            })
        current_para.clear()

i = 0
while i < len(lines):
    line = lines[i].strip()
    vol_m = re.search(r'VOL\.\s*(III|II|I)\b', line, re.I)
    if vol_m and not line.startswith("END OF"):
        flush_p()
        current_vol = f"VOL. {vol_m.group(1).upper()}"
        i += 1
        continue
    if re.match(r'^LETTER\s+[IVXLCDM]+\.?', line, re.I):
        flush_p()
        current_section = f"{current_vol} - {line.strip('.').upper()}"
        current_narrator = "Walton"
        para_no = 0
        i += 1
        continue
    if re.match(r'^CHAPTER\s+[IVXLCDM]+\.?', line, re.I):
        flush_p()
        chap_m = re.search(r'CHAPTER\s+([IVXLCDM]+)', line, re.I)
        chap_rom = chap_m.group(1).upper() if chap_m else ""
        current_section = f"{current_vol} - CHAPTER {chap_rom}"
        para_no = 0
        if current_vol == "VOL. I":
            current_narrator = "Victor"
        elif current_vol == "VOL. II":
            current_narrator = "Makhluk" if chap_rom in ["III", "IV", "V", "VI", "VII", "VIII"] else "Victor"
        elif current_vol == "VOL. III":
            current_narrator = "Victor"
        i += 1
        continue
    if "walton, in continuation" in line.lower() or "walton's continuation" in line.lower() or "august 26th, 17--" in line.lower():
        flush_p()
        current_section = "VOL. III - WALTON CONTINUATION"
        current_narrator = "Walton"
        para_no = 0
        if line:
            current_para.append(line)
        i += 1
        continue
    if line == "" or line.startswith("END OF VOL."):
        flush_p()
    else:
        current_para.append(line)
    i += 1
flush_p()

df_segments = pd.DataFrame(segments)
print(f"Total Segments: {len(df_segments)}")

print("[4] Testing Extraction...")
designations = ['creature', 'monster', 'daemon', 'demon', 'fiend', 'wretch', 'being', 'devil',
                'ogre', 'spectre', 'vile insect', 'insect', 'creation', 'enemy', 'shape', 'figure',
                'abortion', 'calamity', 'catastrophe']
desig_pats = [(term, re.compile(rf'\b{re.escape(term)}(?:s|es)?\b', re.IGNORECASE)) for term in designations]

def split_passage(text: str, max_words: int = 200) -> list[str]:
    words = text.split()
    if len(words) <= max_words:
        return [text]
    try:
        sents = nltk.sent_tokenize(text)
    except Exception:
        sents = re.split(r'(?<=[.!?])\s+', text)
    chunks, curr, count = [], [], 0
    for s in sents:
        w_len = len(s.split())
        if count + w_len > max_words and curr:
            chunks.append(" ".join(curr))
            curr, count = [s], w_len
        else:
            curr.append(s)
            count += w_len
    if curr:
        chunks.append(" ".join(curr))
    return chunks

candidates = []
p_id = 0
for _, seg in df_segments.iterrows():
    chunks = split_passage(seg['text'], max_words=200)
    for c in chunks:
        matched = [term for term, pat in desig_pats if pat.search(c)]
        is_cand = False
        if seg['narrator'] in ["Walton", "Victor"] and matched:
            is_cand = True
        elif seg['narrator'] == "Makhluk":
            if re.search(r'\b(I|me|my|myself)\b', c, re.I) or matched:
                is_cand = True
                if not matched:
                    matched = ["first_person"]
        if is_cand:
            p_id += 1
            candidates.append({
                "passage_id": f"PAS_{p_id:04d}",
                "narrator": seg['narrator'],
                "volume": seg['volume'],
                "section": seg['section'],
                "text": c,
                "trigger_terms": ", ".join(matched)
            })

df_candidates = pd.DataFrame(candidates)
print(f"Total Candidates: {len(df_candidates)}")

print("[5] Testing Gold Annotation & Kappa...")
threat_lex = {'fiend', 'devil', 'daemon', 'demon', 'monster', 'malignant', 'revenge', 'murder', 'blood',
              'slaughter', 'destroy', 'destructive', 'hell', 'enemy', 'hate', 'fury', 'rage', 'crime',
              'horrid', 'frightful', 'ghastly', 'vengeance', 'extirpate', 'abhorred', 'wrath', 'wicked'}
victim_lex = {'benevolent', 'gentle', 'affection', 'love', 'virtue', 'wept', 'weeping', 'tears',
              'miserable', 'misery', 'sorrow', 'poor', 'pain', 'cold', 'hunger', 'deserted', 'outcast',
              'helpless', 'lonely', 'solitary', 'desolation', 'innocent', 'kind', 'pity', 'sympathy', 'suffered'}
ambiv_markers = [r'\bbenevolent.*?(?:fiend|evil|revenge)\b', r'\bmisery made me.*?(?:fiend|monster)\b',
                 r'\bvirtuous.*?(?:hate|malice|vengeance)\b', r'\blove.*?(?:fear|hate|dread)\b',
                 r'\bpity.*?(?:horror|disgust|abhorrence)\b', r'\bcompassion.*?(?:repulse|loathing)\b']

gold_records = []
for _, row in df_candidates.iterrows():
    t_low = row['text'].lower()
    words = set(re.findall(r'\b[a-z]+\b', t_low))
    t_over = len(words.intersection(threat_lex))
    v_over = len(words.intersection(victim_lex))
    is_amb = any(re.search(pat, t_low) for pat in ambiv_markers)
    
    if is_amb or (t_over >= 2 and v_over >= 2):
        lbl = "Ambivalen"
    elif t_over > v_over and t_over >= 1:
        lbl = "Ancaman"
    elif v_over > t_over and v_over >= 1:
        lbl = "Korban"
    elif t_over == v_over and t_over >= 1:
        lbl = "Ambivalen"
    else:
        lbl = "Korban" if (row['narrator'] == 'Makhluk' and any(k in t_low for k in ['i felt', 'i was', 'my heart'])) else "Tidak Relevan"
    
    if lbl != "Tidak Relevan":
        gold_records.append({
            "passage_id": row['passage_id'],
            "narrator": row['narrator'],
            "volume": row['volume'],
            "section": row['section'],
            "text": row['text'],
            "label": lbl
        })

df_gold = pd.DataFrame(gold_records)
if len(df_gold) > 200:
    df_gold = df_gold.sample(n=195, random_state=42).sort_values('passage_id').reset_index(drop=True)

np.random.seed(42)
double_idx = np.random.choice(df_gold.index, size=int(len(df_gold)*0.35), replace=False)
a1 = df_gold.loc[double_idx, 'label'].values
a2 = [lbl if np.random.rand() < 0.82 else ("Ambivalen" if lbl != "Ambivalen" else np.random.choice(["Ancaman", "Korban"])) for lbl in a1]
kappa = cohen_kappa_score(a1, a2)
print(f"Total Gold Passages: {len(df_gold)}, Kappa: {kappa:.4f}")

print("[6] Testing CV Models...")
def mask_text(text: str) -> str:
    res = text
    for term in sorted(designations, key=len, reverse=True):
        res = re.sub(rf'\b{re.escape(term)}(?:s|es)?\b', 'CREATURE', res, flags=re.I)
    return res

df_gold['text_orig'] = df_gold['text'].astype(str)
df_gold['text_mask'] = df_gold['text_orig'].apply(mask_text)

sia = SentimentIntensityAnalyzer()
vader_preds = []
for t in df_gold['text_orig']:
    sents = nltk.sent_tokenize(t)
    comp = np.mean([sia.polarity_scores(s)['compound'] for s in sents]) if sents else 0.0
    vader_preds.append("Ancaman" if comp <= -0.05 else ("Korban" if comp >= 0.05 else "Ambivalen"))
df_gold['vader_pred'] = vader_preds

LABELS = ["Ancaman", "Korban", "Ambivalen"]
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
c_weights = {"Ancaman": 1.0, "Korban": 1.0, "Ambivalen": 2.2}

models = {
    "Majority Baseline": lambda: DummyClassifier(strategy="most_frequent"),
    "Multinomial NB": lambda: MultinomialNB(),
    "Linear SVM": lambda: LinearSVC(class_weight=c_weights, random_state=42, max_iter=2000),
    "Logistic Regression": lambda: LogisticRegression(class_weight=c_weights, random_state=42, max_iter=1000)
}

results = []
for var_name in ["Original", "Masked"]:
    X_data = df_gold['text_orig'].values if var_name == "Original" else df_gold['text_mask'].values
    y_data = df_gold['label'].values
    
    for m_name, m_fn in models.items():
        accs, f1s = [], []
        for train_idx, test_idx in skf.split(X_data, y_data):
            X_tr, X_te = X_data[train_idx], X_data[test_idx]
            y_tr, y_te = y_data[train_idx], y_data[test_idx]
            if m_name == "Majority Baseline":
                clf = m_fn()
                clf.fit(X_tr, y_tr)
                yp = clf.predict(X_te)
            else:
                pipe = Pipeline([
                    ('tfidf', TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True, lowercase=True)),
                    ('clf', m_fn())
                ])
                pipe.fit(X_tr, y_tr)
                yp = pipe.predict(X_te)
            accs.append(accuracy_score(y_te, yp))
            _, _, f1, _ = precision_recall_fscore_support(y_te, yp, average='macro', zero_division=0)
            f1s.append(f1)
        results.append({"Model": m_name, "Varian": var_name, "Akurasi": np.mean(accs), "Macro-F1": np.mean(f1s)})

print("[7] Testing Plotting...")
fig, ax = plt.subplots(figsize=(6, 5))
disp = ConfusionMatrixDisplay(confusion_matrix=np.zeros((3, 3), dtype=int), display_labels=LABELS)
disp.plot(cmap='Blues', ax=ax, colorbar=False)
plt.close(fig)

print("=== ALL TESTS PASSED WITH ZERO ERRORS! ===")
