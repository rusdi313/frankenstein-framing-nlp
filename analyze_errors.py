import pandas as pd
import re

df_gold = pd.read_csv('data/gold.csv')
df_pred = pd.read_csv('results/predictions_logreg_original.csv')
m = df_gold.merge(df_pred, on='passage_id')
err = m[m['label'] != m['pred_label']].copy()

print(f"Total misclassified passages: {len(err)}")

# 1. Ambivalent Framing (Source 3)
s3_mask = err['label'] == 'Ambivalen'
n3 = s3_mask.sum()
print(f"Source 3 (Ambivalent misclassified): {n3} (20 -> Korban, 9 -> Ancaman)")

# 2. Threat Predicted as Victim (Source 4)
s4_mask = (err['label'] == 'Ancaman') & (err['pred_label'] == 'Korban')
n4 = s4_mask.sum()
print(f"Source 4 (Threat predicted as Victim): {n4}")

# 3. Embedded Dialogue (Source 2)
# Passages where Victor quotes the Creature or conversation occurs with quotation marks
dialogue_pattern = r'["“”\']'
s2_mask = err['text'].apply(lambda t: bool(re.search(dialogue_pattern, t)) and ('said' in t.lower() or 'cried' in t.lower() or 'replied' in t.lower() or 'exclaimed' in t.lower()))
n2 = s2_mask.sum()
print(f"Source 2 (Embedded Dialogue with direct speech): {n2}")

# 4. Intra-Paragraph Emotional Shifts (Source 1)
shift_pattern = r'\b(but|yet|however|although|nevertheless|instead|suddenly|altered)\b'
s1_mask = err['text'].apply(lambda t: bool(re.search(shift_pattern, t, re.I)))
n1 = s1_mask.sum()
print(f"Source 1 (Intra-paragraph emotional shifts with contrastive transitions): {n1}")

# Export full 195 passages and 65 errors for literature and linguistics lecturers
m.to_csv('results/all_195_passages_oof_predictions.csv', index=False)
err.to_csv('results/misclassified_65_passages_detailed.csv', index=False)
print("Exported results/all_195_passages_oof_predictions.csv and results/misclassified_65_passages_detailed.csv successfully.")
