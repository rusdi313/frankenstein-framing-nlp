"""
Apply all reviewer revisions to Revisi Makalah Luthfiana Dwi Raknawati (1).docx

This version targets the REVIEWER TEMPLATE version of the document, which still has
placeholders like [AUTHORS: ...] and [n1], [n2] etc.

Key findings from data audit:
- "I compassionated him..." (SEG_0472, Vol. II Ch. IX): NOT in gold standard.
  Only 86 words, never extracted as candidate. Used as literary reference only.
- "Every where I see bliss..." is part of PAS_0084 (Vol. II Ch. II, gold=Ambivalent, pred=Threat).
  Not a standalone Victim passage.
- No label changes are needed. All existing labels verified correct.
  Tables 2-5, kappa, confusion matrix, abstract, conclusion numbers stay unchanged.

Passage IDs verified:
  PAS_0030 | VOL. I - CHAPTER IV  | Gold: Threat     | Pred: Victim
  PAS_0035 | VOL. I - CHAPTER IV  | Gold: Threat     | Pred: Threat
  PAS_0039 | VOL. I - CHAPTER IV  | Gold: Threat     | Pred: Threat
  PAS_0084 | VOL. II - CHAPTER II | Gold: Ambivalent | Pred: Threat
  PAS_0086 | VOL. II - CHAPTER II | Gold: Threat     | Pred: Threat
  PAS_0089 | VOL. II - CHAPTER II | Gold: Ambivalent | Pred: Victim
  PAS_0092 | VOL. II - CHAPTER III| Gold: Victim     | Pred: Victim
  PAS_0186 | VOL. II - CHAPTER VII| Gold: Victim     | Pred: Threat
  PAS_0197 | VOL. II - CHAPTER VIII| Gold: Ambivalent| Pred: Victim
  PAS_0224 | VOL. II - CHAPTER VIII| Gold: Threat    | Pred: Threat
  PAS_0227 | VOL. II - CHAPTER VIII| Gold: Threat    | Pred: Threat
  PAS_0229 | VOL. II - CHAPTER VIII| Gold: Threat    | Pred: Threat
  PAS_0240 | VOL. II - CHAPTER IX | Gold: Ambivalent | Pred: Threat
  PAS_0331 | VOL. III - CHAPTER VII| Gold: Victim    | Pred: Victim
  PAS_0336 | VOL. III - CHAPTER VII| Gold: Victim    | Pred: Victim
"""

import docx
from docx import Document
import sys

sys.stdout.reconfigure(encoding='utf-8')

TARGET = "Revisi/Revisi Makalah Luthfiana Dwi Raknawati (1).docx"


def replace_paragraph_text_keep_formatting(p, new_text):
    """Replace all text in a paragraph, keeping the first run's formatting."""
    if not p.runs:
        r = p.add_run(new_text)
        r.font.highlight_color = None
        return

    r0 = p.runs[0]
    font_name = r0.font.name
    font_size = r0.font.size
    is_bold = r0.bold
    is_italic = r0.italic

    for r in p.runs:
        r.text = ""
        r.font.highlight_color = None

    r0.text = new_text
    if font_name:
        r0.font.name = font_name
    if font_size:
        r0.font.size = font_size
    r0.bold = is_bold
    r0.italic = is_italic
    r0.font.highlight_color = None


def update_document(doc_path):
    print(f"Loading {doc_path}...")
    doc = Document(doc_path)

    # ═══════════════════════════════════════════════════════════════════
    # 1. ABSTRACT (Table 0) — Future Work: paragraph → episode-level
    # ═══════════════════════════════════════════════════════════════════
    cell_abstract = doc.tables[0].rows[0].cells[1]
    for p in cell_abstract.paragraphs:
        if "apply group-based and repeated cross-validation" in p.text:
            new_t = p.text.replace(
                "apply group-based and repeated cross-validation",
                "apply episode-level group cross-validation on larger corpora"
            )
            replace_paragraph_text_keep_formatting(p, new_t)
            print("  [1] Updated Abstract future work.")

    # ═══════════════════════════════════════════════════════════════════
    # 2. FIGURE 1 Stage 6 (Table 1, Row 10) — add StratifiedGroupKFold
    # ═══════════════════════════════════════════════════════════════════
    cell_stage6 = doc.tables[1].rows[10].cells[0]
    for p in cell_stage6.paragraphs:
        if "Stage 6" in p.text:
            new_stage6 = (
                "Stage 6. Stratified 5-fold cross-validation & StratifiedGroupKFold "
                "sensitivity analysis (seed 42) — Accuracy, Macro-Recall, Macro-F1 "
                "(mean ± SD, 95% CI); paragraph-grouped validation across 185 source "
                "paragraphs; pooled confusion matrix and class-level metrics"
            )
            replace_paragraph_text_keep_formatting(p, new_stage6)
            print("  [2] Updated Figure 1 Stage 6.")

    # ═══════════════════════════════════════════════════════════════════
    # 3. TABLE 1 CODEBOOK (Table 2, Row 1) — Threat example → PAS_0035
    # ═══════════════════════════════════════════════════════════════════
    cell_threat = doc.tables[2].rows[1].cells[1]
    for p in cell_threat.paragraphs:
        if "Nothing in human shape" in p.text:
            new_threat = (
                "The passage presents the Creature primarily as dangerous: violence, "
                "murder, menace, revenge, or demonic agency. Example: \"Because he "
                "knows a frightful fiend / Doth close behind him tread\" "
                "(Vol. I Chapter IV / PAS_0035)."
            )
            replace_paragraph_text_keep_formatting(p, new_threat)
            print("  [3] Updated Codebook Threat example → PAS_0035.")

    # ═══════════════════════════════════════════════════════════════════
    # 4. PARAGRAPH 30 (Section 2.3) — Reconcile 206–297 word split
    # ═══════════════════════════════════════════════════════════════════
    p30_text = (
        "The unit of analysis was defined at the paragraph-level passage. In "
        "19th-century Gothic fiction, paragraphs frequently extend beyond modern "
        "paragraph lengths and contain multi-emotional shifts (topic drift). "
        "Consequently, paragraphs exceeding 200 words were split into consecutive "
        "segments at the sentence boundary closest to each 200-word mark, so that "
        "no sentence was divided. In the gold-standard corpus, the candidate "
        "paragraphs that exceeded 200 words were moderately long (ranging from 206 "
        "to 297 words), resulting in exactly 10 source paragraphs being divided "
        "into two segments each (yielding 20 passages); the remaining 175 source "
        "paragraphs each produced a single passage. Longer discursive paragraphs "
        "in the novel were either absent from character-focused scenes or filtered "
        "out as Irrelevant during annotation. Each resulting segment was annotated "
        "independently rather than inheriting the label of its source paragraph, "
        "segments whose framing still changed internally were labeled with the "
        "priority rules in Table 1, and every segment retained the identifier of "
        "its source paragraph. Because framing can still shift within a segment, "
        "this unitization remains a source of error (Section 3.8)."
    )
    replace_paragraph_text_keep_formatting(doc.paragraphs[30], p30_text)
    print("  [4] Updated P30 (Section 2.3 splitting: 206–297 words, 10 paragraphs → 20 passages).")

    # ═══════════════════════════════════════════════════════════════════
    # 5. PARAGRAPH 55 (Section 2.6) — StratifiedGroupKFold methodology
    # ═══════════════════════════════════════════════════════════════════
    p55_text = (
        "All configurations were evaluated using stratified 5-fold cross-validation "
        "with a fixed random seed (42), using the same folds for every configuration. "
        "Each test fold contains 39 passages, with about 15–16 Threat, 18 Victim, "
        "and 5–6 Ambivalent passages, so a single Ambivalent prediction changes "
        "fold-level Ambivalent recall by roughly 17–20 percentage points. The 195 "
        "passages originate from 185 unique source paragraphs: 175 paragraphs each "
        "yielded a single passage, while 10 paragraphs (206–297 words) were split "
        "into two segments (20 passages). To evaluate whether potential lexical "
        "overlap between segments split from the same source paragraph influences "
        "performance estimates, a sensitivity analysis was additionally conducted "
        "using StratifiedGroupKFold (5 folds, seed 42) grouped by the 185 unique "
        "source paragraphs, with comparative results reported in Section 3.2. "
        "For each configuration, Accuracy, Macro-Recall, and Macro-F1 (Equations 5–6) "
        "are reported as the mean ± standard deviation over the five test folds "
        "[25], [30], and 95% confidence intervals for the fold means are computed "
        "as mean ± t(0.975, 4)·s/√5. In addition, the out-of-fold predictions of "
        "the best configuration were pooled into one confusion matrix (Figure 2), "
        "in which each passage appears exactly once, and class-level precision, "
        "recall, and F1 were derived from it (Table 4):"
    )
    replace_paragraph_text_keep_formatting(doc.paragraphs[55], p55_text)
    print("  [5] Updated P55 (Section 2.6 cross-validation with StratifiedGroupKFold).")

    # ═══════════════════════════════════════════════════════════════════
    # 6. PARAGRAPH 66 (Section 3.2) — Add StratifiedGroupKFold results
    # ═══════════════════════════════════════════════════════════════════
    p66_text = (
        "Table 3 presents the stratified 5-fold cross-validation results for all "
        "model configurations and baselines. Logistic Regression on the original "
        "variant obtained the highest mean scores under standard stratified validation "
        "(Macro-F1 47.75% ± 3.64%; accuracy 66.67% ± 5.13%), followed by Linear SVM "
        "(46.18% ± 4.95%; 64.10% ± 7.25%). The 95% confidence intervals of the fold "
        "means overlap substantially (Macro-F1: Logistic Regression 43.2–52.3%, "
        "Linear SVM 40.0–52.3%, VADER 35.5–54.2%), so the ranking among these "
        "configurations should not be read as a decisive difference. With only five "
        "folds, paired comparisons have low statistical power; Logistic Regression "
        "is therefore reported as the configuration with the highest mean score under "
        "stratified cross-validation rather than as a definitively superior model. "
        "In accuracy, Logistic Regression exceeded VADER by 12.3 percentage points, "
        "but in Macro-F1 the gap was only 2.9 points. All supervised models clearly "
        "exceeded the majority baseline (21.05% Macro-F1); however, this baseline is "
        "deliberately minimal, and exceeding it does not establish that the approach "
        "is competitive with framing-specific methods.\n\n"
        "To assess whether segment splitting introduces optimistic bias, models were "
        "also evaluated under StratifiedGroupKFold grouped by the 185 unique source "
        "paragraphs (Table 3, bottom rows). Under group-disjoint folds, Linear SVM "
        "achieved an accuracy of 65.26% ± 5.37% and Macro-F1 of 47.13% ± 3.18%, "
        "slightly higher than its standard stratified score, whereas Logistic Regression "
        "experienced a modest decline of 3.9 percentage points in accuracy "
        "(62.75% ± 6.95%) and 3.1 points in Macro-F1 (44.62% ± 5.42%). In this grouped "
        "scheme, Linear SVM slightly outperformed Logistic Regression. This sensitivity "
        "comparison suggests that lexical overlap between split segments of the same "
        "source paragraph has at most a modest effect on overall performance estimates, "
        "though it introduces slight sensitivity in the relative ranking between "
        "Logistic Regression and Linear SVM."
    )
    replace_paragraph_text_keep_formatting(doc.paragraphs[66], p66_text)
    print("  [6] Updated P66 (Section 3.2 StratifiedGroupKFold results).")

    # ═══════════════════════════════════════════════════════════════════
    # 7. PARAGRAPH 67 (Table 3 caption) — Add StratifiedGroupKFold note
    # ═══════════════════════════════════════════════════════════════════
    p67_text = (
        "Table 3. Classification performance (mean ± standard deviation over five "
        "folds; bottom two rows evaluate StratifiedGroupKFold across 185 source "
        "paragraphs)"
    )
    replace_paragraph_text_keep_formatting(doc.paragraphs[67], p67_text)
    print("  [7] Updated P67 (Table 3 caption).")

    # ═══════════════════════════════════════════════════════════════════
    # 8. TABLE 4 (Table 3) — Add StratifiedGroupKFold rows if missing
    # ═══════════════════════════════════════════════════════════════════
    t3 = doc.tables[4]
    existing_table_text = " ".join(c.text for r in t3.rows for c in r.cells)
    if "StratifiedGroupKFold" not in existing_table_text:
        r_svm = t3.add_row()
        r_svm.cells[0].text = "Linear SVM (Grouped)"
        r_svm.cells[1].text = "Original (StratifiedGroupKFold)"
        r_svm.cells[2].text = "65.26 ± 5.37"
        r_svm.cells[3].text = "50.68 ± 3.05"
        r_svm.cells[4].text = "47.13 ± 3.18"

        r_lr = t3.add_row()
        r_lr.cells[0].text = "Logistic Regression (Grouped)"
        r_lr.cells[1].text = "Original (StratifiedGroupKFold)"
        r_lr.cells[2].text = "62.75 ± 6.95"
        r_lr.cells[3].text = "48.38 ± 4.26"
        r_lr.cells[4].text = "44.62 ± 5.42"

        for row in [r_svm, r_lr]:
            for cell in row.cells:
                for p in cell.paragraphs:
                    for run in p.runs:
                        run.font.name = "Times New Roman"
                        run.font.size = docx.shared.Pt(9)
        print("  [8] Added StratifiedGroupKFold rows to Table 3.")
    else:
        print("  [8] Table 3 already has StratifiedGroupKFold rows.")

    # ═══════════════════════════════════════════════════════════════════
    # 9. PARAGRAPH 81 (Section 3.5) — "Victim framing" → "Ambivalent framing"
    # ═══════════════════════════════════════════════════════════════════
    p81_text = (
        "The coefficients suggest the following tendencies:\n"
        "• Threat vocabulary: the token 'creature' carries the highest weight (0.55). "
        "This reflects the masking procedure: all designations (monster, fiend, daemon) "
        "were mapped to 'creature', which is frequent in Victor's hostile denunciations. "
        "The same token, however, also occurs in Victor's sympathetic reflection on "
        "'the duties of a creator towards his creature' (quoted in Section 3.6 as an "
        "instance of Victor's Ambivalent framing), so a positive Threat coefficient does "
        "not fix the word's meaning. The phrases 'to me' (0.42), 'you' (0.33), and "
        "'do not' (0.31), together with 'destroy' (0.28) and 'enemy' (0.30), plausibly "
        "reflect direct address and personal confrontation between the Creature and Victor."
    )
    replace_paragraph_text_keep_formatting(doc.paragraphs[81], p81_text)
    print("  [9] Updated P81 (Section 3.5 Threat bullet: Victim → Ambivalent framing).")

    # ═══════════════════════════════════════════════════════════════════
    # 10. PARAGRAPH 82 (Section 3.5 Victim & Ambivalent bullets)
    # ═══════════════════════════════════════════════════════════════════
    p82_text = (
        "• Victim vocabulary: this class is associated with terms of moral virtue and "
        "domestic life (gentle, amiable, virtue, old man, cottage, affection), which "
        "point to the Creature's observations of the De Lacey family, where he presents "
        "himself as an admirer of human kindness who is nonetheless excluded.\n"
        "• Ambivalent vocabulary: this class is associated with existential and affective "
        "terms (misery, alone, behold, love, pity), as in 'misery made me a fiend'. "
        "Several of these terms also appear in the Creature's excluded self-representations, "
        "such as 'Every where I see bliss, from which I alone am irrevocably excluded' "
        "(PAS_0084, Section 3.6), which helps explain why the classifier could not "
        "separate Ambivalent from Victim passages (Section 3.8)."
    )
    replace_paragraph_text_keep_formatting(doc.paragraphs[82], p82_text)
    print("  [10] Updated P82 (Section 3.5 Ambivalent bullet with PAS_0084 ID).")

    # ═══════════════════════════════════════════════════════════════════
    # 11. PARAGRAPH 84 (Section 3.6 poin 1) — Fix chapter numbers to
    #     Vol. I Chapter IV; use gold-standard passages with IDs
    # ═══════════════════════════════════════════════════════════════════
    p84_text = (
        "Within the annotated sample (Table 2), Victor's passages are most often "
        "labeled Threat (55.0%), whereas the Creature's are most often labeled Victim "
        "(72.8%). These are descriptive findings about human-assigned labels on "
        "selectively extracted passages. They are distinct from the classification "
        "results in Sections 3.2–3.3, which measure how well the models reproduce "
        "those labels, and they are not independent confirmation that the models "
        "capture the novel's framing. Representative gold-standard passages illustrate "
        "the contrast:\n"
        "1. Victor Frankenstein's Threat Framing (Vol. I Chapter IV): In the immediate "
        "aftermath of animation, Victor recoils in horror from the Creature's form: "
        "\"How can I describe my emotions at this catastrophe, or how delineate the "
        "wretch whom with such infinite pains and care I had endeavoured to form? ... "
        "breathless horror and disgust filled my heart\" (PAS_0030) [1]. This hostile "
        "perception intensifies into persistent terror, captured through Coleridge's "
        "imagery of walking in fear of a \"frightful fiend\" (PAS_0035) [1], and "
        "Victor's exhilaration when he believes \"my enemy had indeed fled\" "
        "(PAS_0039) [1]."
    )
    replace_paragraph_text_keep_formatting(doc.paragraphs[84], p84_text)
    print("  [11] Updated P84 (Section 3.6 poin 1: Vol. I Chapter IV, PAS IDs).")

    # ═══════════════════════════════════════════════════════════════════
    # 12. PARAGRAPH 85 (Section 3.6 poin 2) — Correct chapter heading;
    #     add PAS_0084 ID for "Every where I see bliss..."; note that
    #     PAS_0084 is gold Ambivalent but the quote illustrates a
    #     Victim-register fragment within an Ambivalent passage.
    # ═══════════════════════════════════════════════════════════════════
    p85_text = (
        "2. The Creature's Victim Framing (Vol. II Chapters II–III & VII): In his "
        "confrontation with Victor and subsequent autobiography, the Creature "
        "repeatedly emphasizes his helplessness, isolation, and social abandonment. "
        "On Montanvert, he laments: \"Every where I see bliss, from which I alone am "
        "irrevocably excluded\" (within PAS_0084, gold Ambivalent; see also poin 3 "
        "below) [1]. In his earliest recollections: \"I was a poor, helpless, miserable "
        "wretch; I knew, and could distinguish, nothing; but, feeling pain invade me "
        "on all sides, I sat down and wept\" (PAS_0092, gold Victim) [1]. This "
        "vulnerable self-representation recurs during his attempt to converse with "
        "the blind De Lacey: \"I am an unfortunate and deserted creature; I look "
        "around, and I have no relation or friend upon earth\" (PAS_0186, gold "
        "Victim) [1]."
    )
    replace_paragraph_text_keep_formatting(doc.paragraphs[85], p85_text)
    print("  [12] Updated P85 (Section 3.6 poin 2: Chapter heading, PAS IDs, note on PAS_0084 Ambivalent).")

    # ═══════════════════════════════════════════════════════════════════
    # 13. PARAGRAPH 86 (Section 3.6 poin 3) — Expand Ambivalent with
    #     full passages, PAS IDs, and consistent PAS_0084 quote
    # ═══════════════════════════════════════════════════════════════════
    p86_text = (
        "3. Ambivalent Framing (Vol. II Chapters II & VIII):\n"
        "Ambivalent framing captures passages where moral virtue and destructive "
        "impulses coexist, or where compassion is locked in tension with horror. "
        "On Montanvert, the Creature asserts the causal link between suffering and "
        "malevolence: \"I was benevolent and good; misery made me a fiend. Make me "
        "happy, and I shall again be virtuous\" (PAS_0084) [1]. The same passage "
        "also contains his claim to victimhood (\"Every where I see bliss, from which "
        "I alone am irrevocably excluded\"), illustrating how the Ambivalent label "
        "captures the co-presence of vulnerability and conditional menace within a "
        "single speech act. Similarly, after violent rejection from the De Lacey "
        "cottage, the Creature reflects on his agonizing despair alongside destructive "
        "rage: \"I, like the arch fiend, bore a hell within me; and, finding myself "
        "unsympathized with, wished to tear up the trees, spread havoc and destruction "
        "around me\" (PAS_0197, gold Ambivalent) [1]. On Victor's side, ambivalence "
        "surfaces when listening to the Creature on the Mer de Glace: \"For the first "
        "time, also, I felt what the duties of a creator towards his creature were, "
        "and that I ought to render him happy before I complained of his wickedness\" "
        "(PAS_0089, gold Ambivalent) [1]."
    )
    replace_paragraph_text_keep_formatting(doc.paragraphs[86], p86_text)
    print("  [13] Updated P86 (Section 3.6 poin 3: consistent PAS_0084 quote, all PAS IDs).")

    # ═══════════════════════════════════════════════════════════════════
    # 14. PARAGRAPH 87 (Section 3.6 poin 4) — Cross-Framed with PAS_0336
    #     "I compassionated him..." is NOT in gold standard; replaced with
    #     PAS_0336 (Genette voice vs. focalization)
    # ═══════════════════════════════════════════════════════════════════
    p87_text = (
        "4. Cross-Framed Passages: Table 2 also contains counter-intuitive cases: "
        "29 of Victor's passages are labeled Victim (26.6%) and 14 of the Creature's "
        "passages are labeled Threat (17.3%). Read through Genette's distinction "
        "between voice (who speaks) and focalization (whose perspective or evaluative "
        "stance is represented) [33], Victor's narrator-level passages labeled Victim "
        "correspond primarily to instances where the external narrative voice belongs "
        "to Victor (or Walton transcribing Victor), yet the evaluative focalization "
        "centers on the Creature's suffering or directly embeds the Creature's own "
        "voice. A prominent example occurs in the closing frame narrative aboard "
        "Walton's ship, where Victor's overarching narration transcribes the Creature's "
        "direct lamentation over Frankenstein's corpse: \"'Oh, it is not thus -- not "
        "thus,' interrupted the being; 'yet such must be the impression conveyed to "
        "you by what appears to be the purport of my actions. Yet I seek not a "
        "fellow-feeling in my misery. No sympathy may I ever find... in what should I "
        "seek for sympathy? I am content to suffer alone, while my sufferings shall "
        "endure'\" (PAS_0336, gold Victim, predicted Victim) [1]. Here, while the "
        "structural narrative voice is situated within Victor's and Walton's frame, "
        "the passage focalizes the Creature as an agonizing, abandoned victim grieving "
        "lost virtue and companionship. Because the codebook evaluates the framing "
        "assigned to the Creature by the passage as a whole (Table 1), such embedded "
        "speeches are annotated as Victim, and the model correctly predicts them as "
        "Victim on the basis of their dense elegiac vocabulary."
    )
    replace_paragraph_text_keep_formatting(doc.paragraphs[87], p87_text)
    print("  [14] Updated P87 (Section 3.6 poin 4: PAS_0336 replaces compassionated).")

    # ═══════════════════════════════════════════════════════════════════
    # 15. PARAGRAPH 88 (Section 3.6 Creature Threat)
    # ═══════════════════════════════════════════════════════════════════
    p88_text = (
        "By contrast, the Creature's own Threat framing (14 passages in Table 2) "
        "emerges at the point where his narrative turns explicitly to vengeance and "
        "murder. Confronting William in the forest, the Creature narrates William's "
        "terror—\"monster! ugly wretch! you wish to eat me, and tear me to pieces\" "
        "(PAS_0224, gold Threat) [1]—and immediately vows revenge: \"Frankenstein! "
        "you belong then to my enemy -- to him towards whom I have sworn eternal "
        "revenge; you shall be my first victim\" (PAS_0227, gold Threat) [1]. After "
        "murdering the child, he exclaims with triumphant malice: \"I gazed on my "
        "victim, and my heart swelled with exultation and hellish triumph: clapping "
        "my hands, I exclaimed, 'I, too, can create desolation'\" (PAS_0229, gold "
        "Threat) [1]. In these passages, the Creature abandons his plea for sympathy "
        "and fully adopts the role of a destructive agent. Brooks's observation that "
        "a monster is \"that which calls into question all our cultural codes, "
        "including language itself\" [34, p. 219] illuminates how the Creature's "
        "self-narration alternates between eloquence pleading for justice and horrific "
        "vows of destruction."
    )
    replace_paragraph_text_keep_formatting(doc.paragraphs[88], p88_text)
    print("  [15] Updated P88 (Section 3.6 Creature Threat with PAS IDs).")

    # ═══════════════════════════════════════════════════════════════════
    # 16. PARAGRAPH 89 (Section 3.6 predictions) — Fill in placeholder
    #     with actual gold/pred labels; soften to "plausibly because"
    # ═══════════════════════════════════════════════════════════════════
    p89_text = (
        "To connect these close readings with the model, the out-of-fold predictions "
        "of Logistic Regression for the gold-standard passages analyzed above are as "
        "follows:\n"
        "• Victor Threat passages: Victor's expressions of dread and enmity in "
        "PAS_0035 ('frightful fiend') and PAS_0039 ('my enemy had indeed fled') are "
        "correctly classified as Threat (gold Threat, predicted Threat). Conversely, "
        "PAS_0030 ('breathless horror and disgust'), while labeled Threat, is "
        "misclassified as Victim (gold Threat, predicted Victim), plausibly because "
        "its opening reflection contains affective terms ('infinite pains', 'beauty') "
        "that may confound bag-of-words weighting.\n"
        "• Creature Victim passages: The Creature's awakening confession in PAS_0092 "
        "('poor, helpless, miserable wretch') is correctly classified as Victim (gold "
        "Victim, predicted Victim). In contrast, his plea to De Lacey in PAS_0186 "
        "('unfortunate and deserted creature') is misclassified as Threat (gold Victim, "
        "predicted Threat), plausibly because words of social rejection and hostility "
        "in the surrounding dialogue dominate the passage's lexical distribution.\n"
        "• Ambivalent passages: As reflected in the zero Ambivalent recall, the model "
        "collapses all ambivalent passages into one of the two polar classes: PAS_0084 "
        "('misery made me a fiend') is misclassified as Threat (gold Ambivalent, "
        "predicted Threat), whereas Victor's acknowledgment of creator duties in "
        "PAS_0089 and the Creature's Miltonic lament in PAS_0197 ('like the arch "
        "fiend, bore a hell within me') are both misclassified as Victim (gold "
        "Ambivalent, predicted Victim).\n"
        "• Cross-Framed and Creature Threat passages: In PAS_0336 ('Oh, it is not "
        "thus -- not thus...'), where the Creature directly laments his fallen virtue "
        "within Victor and Walton's frame narration, the model correctly predicts "
        "Victim (gold Victim, predicted Victim), showing that the strong density of "
        "elegiac and affective terms successfully guides bag-of-words classification "
        "when focalization and lexical stance align. Meanwhile, the Creature's violent "
        "confrontation with William in PAS_0224, his oath of vengeance in PAS_0227, "
        "and his declaration of ruin in PAS_0229 are all correctly classified as Threat "
        "(gold Threat, predicted Threat).\n"
        "Correctly classified passages demonstrate where salient lexical cues align "
        "directly with close reading, whereas misclassified passages highlight where "
        "narrative framing depends on voice, focalization, or inter-clausal causal "
        "relations that a bag-of-words representation cannot capture (Section 3.8)."
    )
    replace_paragraph_text_keep_formatting(doc.paragraphs[89], p89_text)
    print("  [16] Updated P89 (Section 3.6 predictions filled in, softened).")

    # ═══════════════════════════════════════════════════════════════════
    # 17. PARAGRAPH 97 (Section 3.8 Source 1) — Add PAS_0030 and PAS_0084
    #     as concrete examples; use CONSISTENT PAS_0084 quote
    # ═══════════════════════════════════════════════════════════════════
    p97_text = (
        "Logistic Regression misclassified 65 of the 195 passages (Figure 2). As "
        "shown in the pooled confusion matrix (Figure 2), these errors consist "
        "quantitatively of: 29 Ambivalent passages misclassified (20 as Victim, 9 as "
        "Threat); 27 Threat passages misclassified as Victim; and 9 Victim passages "
        "misclassified (8 as Threat, 1 as Ambivalent). A qualitative linguistic review "
        "of these 65 error cases identifies four primary textual mechanisms:\n"
        "1. Intra-Paragraph Emotional Shifts: Passages that begin with empathetic "
        "reflection or vulnerability and conclude with violent oaths combine vocabulary "
        "from opposing poles. Because n-gram TF-IDF weights words independently of "
        "clause ordering, it cannot capture how an adversative connective (such as "
        "'but', 'yet', or 'however') pivots the overall evaluative stance of the "
        "passage. For instance, in PAS_0030, Victor opens with aesthetic dedication "
        "and care ('infinite pains and care I had endeavoured to form') before pivoting "
        "sharply to revulsion ('breathless horror and disgust filled my heart'), "
        "causing a gold Threat passage to be mispredicted as Victim. Similarly, in "
        "PAS_0084, the Creature's Montanvert plea opens with vulnerability ('I am thy "
        "creature... I ought to be thy Adam') and conditional virtue ('I was benevolent "
        "and good; misery made me a fiend. Make me happy, and I shall again be "
        "virtuous'), causing a gold Ambivalent passage to be misclassified as Threat."
    )
    replace_paragraph_text_keep_formatting(doc.paragraphs[97], p97_text)
    print("  [17] Updated P97 (Section 3.8 Source 1: PAS_0030 and PAS_0084 examples, consistent quote).")

    # ═══════════════════════════════════════════════════════════════════
    # 18. PARAGRAPH 98 (Section 3.8 Source 2) — Add PAS_0240 example
    # ═══════════════════════════════════════════════════════════════════
    p98_text = (
        "2. Embedded Dialogue (Voice vs. Focalization): In passages where Victor "
        "quotes the Creature's threats verbatim or the Creature recounts human "
        "hostility, the bag-of-words representation cannot separate the grammatical "
        "narrator (Genette's category of voice [33]) from the quoted character's "
        "evaluative perspective (focalization). For instance, in PAS_0240, Victor "
        "quotes the Creature pleading ('How is this? I thought I had moved your "
        "compassion...'), resulting in an Ambivalent passage being predicted as Threat "
        "due to hostile surrounding dialogue."
    )
    replace_paragraph_text_keep_formatting(doc.paragraphs[98], p98_text)
    print("  [18] Updated P98 (Section 3.8 Source 2: PAS_0240 example).")

    # ═══════════════════════════════════════════════════════════════════
    # 19. PARAGRAPH 99 (Section 3.8 Sources 3 & 4) — Fill in placeholders
    # ═══════════════════════════════════════════════════════════════════
    p99_text = (
        "3. Ambivalent Boundary Collapse (29 errors in Figure 2): Every one of the "
        "29 Ambivalent passages was misassigned to either Victim (20) or Threat (9). "
        "Ambivalent framing is fundamentally expressed through inter-clausal relations—"
        "such as the causal bond in 'misery made me a fiend' (PAS_0084), Victor's "
        "tension between duty and hatred in PAS_0089, or the Creature's mixture of "
        "misery and destructive rage in PAS_0197. Lacking syntactical awareness, the "
        "model simply defaults to whichever lexical pole carries greater cumulative "
        "TF-IDF weight. Furthermore, inter-annotator agreement was lowest precisely "
        "on this boundary, as all 13 disagreements in the reliability sample involved "
        "Ambivalent.\n"
        "4. Threat Predicted as Victim (27 errors in Figure 2): This represents the "
        "largest error category between opposing poles. Hostile passages narrated by "
        "the Creature or Victor frequently incorporate intense, affect-laden vocabulary "
        "('misery', 'tears', 'horror') that overlaps heavily with the Victim lexicon "
        "(e.g., PAS_0030, where Victor's disgust at the Creature is accompanied by "
        "words of care and beauty, or PAS_0201, where the Creature's declaration of "
        "war follows an account of bodily fever and suffering).\n"
        "Representative misclassified passages for each category are documented with "
        "complete text, gold annotations, and model predictions in the supplementary "
        "evaluation dataset."
    )
    replace_paragraph_text_keep_formatting(doc.paragraphs[99], p99_text)
    print("  [19] Updated P99 (Section 3.8 Sources 3 & 4: filled placeholders).")

    # ═══════════════════════════════════════════════════════════════════
    # 20. PARAGRAPH 105 (Section 3.9 poin 4) — Softened validation limitation
    # ═══════════════════════════════════════════════════════════════════
    p105_text = (
        "(4) Validation: Stratified 5-fold cross-validation with 5–6 Ambivalent "
        "passages per test fold yields unstable class-level estimates for the minority "
        "class. While a sensitivity analysis using StratifiedGroupKFold grouped by the "
        "185 unique source paragraphs suggests that segment splitting has at most a "
        "modest effect on performance (Macro-F1 of 44.62% for Logistic Regression and "
        "47.13% for Linear SVM), the drop of ~3.1 percentage points for Logistic "
        "Regression and the slight shift in algorithmic ranking indicate that group "
        "structure does introduce sensitivity. Furthermore, adjacent passages within "
        "the same chapter or episode may still share stylistic and vocabulary cues, "
        "and multi-chapter episode-level clustering on larger corpora remains an "
        "important recommendation for future work."
    )
    replace_paragraph_text_keep_formatting(doc.paragraphs[105], p105_text)
    print("  [20] Updated P105 (Section 3.9 poin 4: softened validation).")

    # ═══════════════════════════════════════════════════════════════════
    # 21. PARAGRAPH 112 (Conclusion Future Work) — episode-level grouping
    # ═══════════════════════════════════════════════════════════════════
    p112_text = (
        "Future work should: (1) expand the corpus within Frankenstein, including a "
        "larger and uniformly extracted Walton sample, and extend it to other "
        "nineteenth-century Gothic and science fiction novels (e.g., by Bram Stoker "
        "and H. G. Wells); (2) strengthen validation through repeated and episode- or "
        "chapter-level group cross-validation on larger multi-chapter corpora, together "
        "with paired statistical comparison of models; (3) refine the annotation "
        "scheme, for example by adding annotators, reporting agreement per class, and "
        "testing a multi-label or graded alternative to the single Ambivalent class; "
        "(4) test whether framing cues can be separated from narrator-specific "
        "vocabulary, for instance by training and testing within a single narrator or "
        "by masking pronouns and narrator-specific terms; (5) compare the models with "
        "stronger baselines, including a zero- or few-shot LLM; and (6) use dependency "
        "parsing or quotation detection to separate embedded dialogue from narratorial "
        "report."
    )
    replace_paragraph_text_keep_formatting(doc.paragraphs[112], p112_text)
    print("  [21] Updated P112 (Future Work: episode-level grouping).")

    # ═══════════════════════════════════════════════════════════════════
    # SAVE
    # ═══════════════════════════════════════════════════════════════════
    doc.save(doc_path)
    print(f"\nSUCCESS: Saved all revisions to {doc_path}")


if __name__ == '__main__':
    update_document(TARGET)
