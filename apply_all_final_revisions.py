import docx
from docx import Document
import sys
import shutil

sys.stdout.reconfigure(encoding='utf-8')

def replace_paragraph_text_keep_formatting(p, new_text):
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

    # 1. Table 0 (Abstract): Change future work from group-based to episode-level
    cell_abstract = doc.tables[0].rows[0].cells[1]
    for p in cell_abstract.paragraphs:
        if "apply group-based and repeated cross-validation" in p.text:
            new_t = p.text.replace(
                "apply group-based and repeated cross-validation",
                "apply episode-level group cross-validation on larger corpora"
            )
            replace_paragraph_text_keep_formatting(p, new_t)
            print("Updated Abstract future work.")

    # 2. Table 1 (Figure 1 Workflow): Row 10 (Stage 6) add StratifiedGroupKFold
    cell_stage6 = doc.tables[1].rows[10].cells[0]
    for p in cell_stage6.paragraphs:
        if "Stage 6" in p.text:
            new_stage6_text = (
                "Stage 6. Stratified 5-fold cross-validation & StratifiedGroupKFold sensitivity analysis (seed 42) — "
                "Accuracy, Macro-Recall, Macro-F1 (mean ± SD, 95% CI); paragraph-grouped validation across 185 source paragraphs; "
                "pooled confusion matrix and class-level metrics"
            )
            replace_paragraph_text_keep_formatting(p, new_stage6_text)
            print("Updated Figure 1 Stage 6 workflow row.")

    # 3. Table 2 (Table 1 Codebook): Threat example replace with PAS_0035
    cell_threat = doc.tables[2].rows[1].cells[1]
    for p in cell_threat.paragraphs:
        if "Nothing in human shape" in p.text:
            new_threat_example = (
                "The passage presents the Creature primarily as dangerous: violence, murder, menace, revenge, or demonic agency. "
                'Example: "Because he knows a frightful fiend / Doth close behind him tread" (Vol. I Chapter IV / PAS_0035).'
            )
            replace_paragraph_text_keep_formatting(p, new_threat_example)
            print("Updated Table 1 Codebook Threat example to PAS_0035.")

    # 4. Paragraph 30 (Section 2.3): Reconcile paragraph splitting rule (206-297 words, 10 paragraphs split into 2 segments)
    p30_text = (
        "The unit of analysis was defined at the paragraph-level passage. In 19th-century Gothic fiction, paragraphs frequently extend beyond "
        "modern paragraph lengths and contain multi-emotional shifts (topic drift). Consequently, paragraphs exceeding 200 words were split "
        "into consecutive segments at the sentence boundary closest to each 200-word mark, so that no sentence was divided. In the gold-standard corpus, "
        "candidate paragraphs meeting the inclusion criteria that exceeded 200 words were moderately long (ranging from 206 to 297 words), resulting "
        "in exactly 10 source paragraphs being divided into two segments each (yielding 20 passages), while longer discursive paragraphs throughout the novel "
        "were either absent from character-focused scenes or filtered out during candidate filtering as Irrelevant. Each resulting segment was annotated "
        "independently rather than inheriting the label of its source paragraph, segments whose framing still changed internally were labeled with the priority "
        "rules in Table 1, and every segment retained the identifier of its source paragraph. Because framing can still shift within a segment, this unitization "
        "remains a source of error (Section 3.8)."
    )
    replace_paragraph_text_keep_formatting(doc.paragraphs[30], p30_text)
    print("Updated Paragraph 30 (Section 2.3 splitting explanation).")

    # 5. Paragraph 67 (Table 3 Title): Add mention of StratifiedGroupKFold on bottom two rows
    p67_text = "Table 3. Classification performance (mean ± standard deviation over five folds; bottom two rows evaluate StratifiedGroupKFold across 185 source paragraphs)"
    replace_paragraph_text_keep_formatting(doc.paragraphs[67], p67_text)
    print("Updated Paragraph 67 (Table 3 caption).")

    # 6. Paragraph 81 (Section 3.5 Threat bullet): Change "as an instance of Victor's Victim framing" -> "as an instance of Victor's Ambivalent framing"
    p81_text = (
        "The coefficients suggest the following tendencies:\n"
        "• Threat vocabulary: the token 'creature' carries the highest weight (0.55). This reflects the masking procedure: all designations (monster, fiend, daemon) "
        "were mapped to 'creature', which is frequent in Victor's hostile denunciations. The same token, however, also occurs in Victor's sympathetic reflection on "
        "'the duties of a creator towards his creature' (quoted in Section 3.6 as an instance of Victor's Ambivalent framing), so a positive Threat coefficient does not "
        "fix the word's meaning. The phrases 'to me' (0.42), 'you' (0.33), and 'do not' (0.31), together with 'destroy' (0.28) and 'enemy' (0.30), plausibly reflect "
        "direct address and personal confrontation between the Creature and Victor."
    )
    replace_paragraph_text_keep_formatting(doc.paragraphs[81], p81_text)
    print("Updated Paragraph 81 (Section 3.5 Threat vocabulary citation to Ambivalent).")

    # 7. Paragraph 82 (Section 3.5 Ambivalent bullet): Reconcile reference to Section 3.6
    p82_text = (
        "• Victim vocabulary: this class is associated with terms of moral virtue and domestic life (gentle, amiable, virtue, old man, cottage, affection), which point "
        "to the Creature's observations of the De Lacey family, where he presents himself as an admirer of human kindness who is nonetheless excluded.\n"
        "• Ambivalent vocabulary: this class is associated with existential and affective terms (misery, alone, behold, love, pity), as in 'misery made me a fiend'. "
        "Several of these terms also appear in the Creature's excluded self-representations, such as 'from which I alone am irrevocably excluded' (Section 3.6), which "
        "helps explain why the classifier could not separate Ambivalent from Victim passages (Section 3.8)."
    )
    replace_paragraph_text_keep_formatting(doc.paragraphs[82], p82_text)
    print("Updated Paragraph 82 (Section 3.5 Ambivalent vocabulary).")

    # 8. Paragraph 84 (Section 3.6 Victor Threat Framing): Correct chapter to Vol. I Chapter IV
    p84_text = (
        "Within the annotated sample (Table 2), Victor's passages are most often labeled Threat (55.0%), whereas the Creature's are most often labeled Victim (72.8%). "
        "These are descriptive findings about human-assigned labels on selectively extracted passages. They are distinct from the classification results in Sections 3.2–3.3, "
        "which measure how well the models reproduce those labels, and they are not independent confirmation that the models capture the novel's framing. Representative gold-standard "
        "passages illustrate the contrast:\n"
        "1. Victor Frankenstein's Threat Framing (Vol. I Chapter IV): In the immediate aftermath of animation, Victor recoils in horror from the Creature's form: "
        "\"How can I describe my emotions at this catastrophe, or how delineate the wretch whom with such infinite pains and care I had endeavoured to form? ... breathless horror "
        "and disgust filled my heart\" (Vol. I Chapter IV / PAS_0030) [1]. This hostile perception intensifies into persistent terror within the same chapter, captured through "
        "Coleridge's imagery of walking in fear of a \"frightful fiend\" (Vol. I Chapter IV / PAS_0035) [1], and Victor's exhilaration when he believes \"my enemy had indeed fled\" "
        "(Vol. I Chapter IV / PAS_0039) [1]."
    )
    replace_paragraph_text_keep_formatting(doc.paragraphs[84], p84_text)
    print("Updated Paragraph 84 (Section 3.6 Chapter numbers to Vol. I Chapter IV).")

    # 9. Paragraph 85 (Section 3.6 Creature Victim Framing): Restore quote 'from which I alone am irrevocably excluded'
    p85_text = (
        "2. The Creature's Victim Framing (Vol. II Chapters II, III & VII): In his confrontation with Victor and subsequent autobiography, the Creature repeatedly emphasizes his helplessness, "
        "isolation, and social abandonment: \"Every where I see bliss, from which I alone am irrevocably excluded\" (Vol. II Chapter II) [1]; \"I was a poor, helpless, miserable wretch; "
        "I knew, and could distinguish, nothing; but, feeling pain invade me on all sides, I sat down and wept\" (Vol. II Chapter III / PAS_0092) [1]. This vulnerable self-representation "
        "recurs during his attempt to converse with the blind De Lacey: \"I am an unfortunate and deserted creature; I look around, and I have no relation or friend upon earth\" "
        "(Vol. II Chapter VII / PAS_0186) [1]."
    )
    replace_paragraph_text_keep_formatting(doc.paragraphs[85], p85_text)
    print("Updated Paragraph 85 (Section 3.6 restored quote 'from which I alone am irrevocably excluded').")

    # 10. Paragraph 87 (Section 3.6 Cross-Framed Passages): Replace PAS_0069/PAS_0331 with true Genette voice vs focalization (PAS_0336)
    p87_text = (
        "4. Cross-Framed Passages: Table 2 also contains counter-intuitive cases: 29 of Victor's passages are labeled Victim (26.6%) and 14 of the Creature's passages are labeled Threat (17.3%). "
        "Read through Genette's distinction between voice (who speaks) and focalization (whose perspective or evaluative stance is represented) [33], Victor's narrator-level passages labeled Victim "
        "correspond primarily to instances where the external narrative voice belongs to Victor (or Walton transcribing Victor), yet the evaluative focalization centers on the Creature's suffering or "
        "directly embeds the Creature's own voice. A prominent example occurs in the closing frame narrative aboard Walton's ship, where Victor's overarching narration transcribes the Creature's direct "
        "lamentation over Frankenstein's corpse: \"'Oh, it is not thus -- not thus,' interrupted the being; 'yet such must be the impression conveyed to you by what appears to be the purport of my actions. "
        "Yet I seek not a fellow-feeling in my misery. No sympathy may I ever find... in what should I seek for sympathy? I am content to suffer alone, while my sufferings shall endure'\" "
        "(Vol. III Chapter VII / PAS_0336) [1]. Here, while the structural narrative voice is situated within Victor's and Walton's frame, the passage focalizes the Creature as an agonizing, abandoned victim "
        "grieving lost virtue and companionship. Because the codebook evaluates the framing assigned to the Creature by the passage as a whole (Table 1), such embedded speeches are annotated as Victim, "
        "and the model correctly predicts them as Victim on the basis of their dense elegiac vocabulary."
    )
    replace_paragraph_text_keep_formatting(doc.paragraphs[87], p87_text)
    print("Updated Paragraph 87 (Section 3.6 Cross-Framed with PAS_0336 Genette voice vs focalization).")

    # 11. Paragraph 89 (Section 3.6 Predictions): Soften to "plausibly because" and include PAS_0336
    p89_text = (
        "To connect these close readings with the model, the out-of-fold predictions of Logistic Regression for the gold-standard passages analyzed above are as follows:\n"
        "• Victor Threat passages: Victor's expressions of dread and enmity in PAS_0035 ('frightful fiend') and PAS_0039 ('my enemy had indeed fled') are correctly classified as Threat "
        "(gold Threat, predicted Threat). Conversely, PAS_0030 ('breathless horror and disgust'), while labeled Threat, is misclassified as Victim (gold Threat, predicted Victim), "
        "plausibly because its opening reflection contains affective terms ('infinite pains', 'beauty') that may confound bag-of-words weighting.\n"
        "• Creature Victim passages: The Creature's awakening confession in PAS_0092 ('poor, helpless, miserable wretch') is correctly classified as Victim (gold Victim, predicted Victim). "
        "In contrast, his plea to De Lacey in PAS_0186 ('unfortunate and deserted creature') is misclassified as Threat (gold Victim, predicted Threat), plausibly because words of social rejection "
        "and hostility in the surrounding dialogue dominate the passage's lexical distribution.\n"
        "• Ambivalent passages: As reflected in the zero Ambivalent recall, the model collapses all ambivalent passages into one of the two polar classes: PAS_0084 ('misery made me a fiend') is "
        "misclassified as Threat (gold Ambivalent, predicted Threat), whereas Victor's acknowledgment of creator duties in PAS_0089 and the Creature's Miltonic lament in PAS_0197 ('like the arch fiend, "
        "bore a hell within me') are both misclassified as Victim (gold Ambivalent, predicted Victim).\n"
        "• Cross-Framed and Creature Threat passages: In PAS_0336 ('Oh, it is not thus -- not thus...'), where the Creature directly laments his fallen virtue within Victor and Walton's frame narration, "
        "the model correctly predicts Victim (gold Victim, predicted Victim), showing that the strong density of elegiac and affective terms ('virtue', 'affection', 'misery', 'suffer') successfully guides "
        "bag-of-words classification when focalization and lexical stance align. Meanwhile, the Creature's violent confrontation with William in PAS_0224 ('monster! ugly wretch!'), his oath of vengeance "
        "in PAS_0227 ('sworn eternal revenge'), and his declaration of ruin in PAS_0229 ('I, too, can create desolation') are all correctly classified as Threat (gold Threat, predicted Threat).\n"
        "Correctly classified passages demonstrate where salient lexical cues align directly with close reading, whereas misclassified passages highlight where narrative framing depends on voice, "
        "focalization, or inter-clausal causal relations that a bag-of-words representation cannot capture (Section 3.8)."
    )
    replace_paragraph_text_keep_formatting(doc.paragraphs[89], p89_text)
    print("Updated Paragraph 89 (Section 3.6 predictions softened and included PAS_0336).")

    # 12. Paragraph 97 (Section 3.8 Error Analysis Source 1): Add passage IDs (PAS_0030 and PAS_0084)
    p97_text = (
        "Logistic Regression misclassified 65 of the 195 passages (Figure 2). As shown in the pooled confusion matrix (Figure 2), these errors consist quantitatively of: 29 Ambivalent passages "
        "misclassified (20 as Victim, 9 as Threat); 27 Threat passages misclassified as Victim; and 9 Victim passages misclassified (8 as Threat, 1 as Ambivalent). A qualitative linguistic review of these "
        "65 error cases identifies four primary textual mechanisms:\n"
        "1. Intra-Paragraph Emotional Shifts: Passages that begin with empathetic reflection or vulnerability and conclude with violent oaths combine vocabulary from opposing poles. Because n-gram TF-IDF "
        "weights words independently of clause ordering, it cannot capture how an adversative connective (such as 'but', 'yet', or 'however') pivots the overall evaluative stance of the passage. "
        "For instance, in PAS_0030, Victor opens with aesthetic dedication and care ('infinite pains and care', 'features as beautiful') before pivoting sharply to revulsion ('but these luxuriances only "
        "formed a more horrific contrast... breathless horror and disgust filled my heart'), causing a gold Threat passage to be mispredicted as Victim. Similarly, in PAS_0084 ('Life, although it may only "
        "be an accumulation of anguish, is dear to me... but I will not be tempted...'), the Creature's balanced stance between docility and defiance leads an Ambivalent passage to be misclassified as Threat."
    )
    replace_paragraph_text_keep_formatting(doc.paragraphs[97], p97_text)
    print("Updated Paragraph 97 (Section 3.8 Source 1 added PAS_0030 and PAS_0084 examples).")

    # 13. Paragraph 112 (Conclusion Future Work point 2): Change paragraph to episode/chapter-level group cross-validation
    p112_text = (
        "Future work should: (1) expand the corpus within Frankenstein, including a larger and uniformly extracted Walton sample, and extend it to other nineteenth-century Gothic and science fiction "
        "novels (e.g., by Bram Stoker and H. G. Wells); (2) strengthen validation through repeated and episode- or chapter-level group cross-validation on larger multi-chapter corpora, together with "
        "paired statistical comparison of models; (3) refine the annotation scheme, for example by adding annotators, reporting agreement per class, and testing a multi-label or graded alternative to "
        "the single Ambivalent class; (4) test whether framing cues can be separated from narrator-specific vocabulary, for instance by training and testing within a single narrator or by masking pronouns "
        "and narrator-specific terms; (5) compare the models with stronger baselines, including a zero- or few-shot LLM; and (6) use dependency parsing or quotation detection to separate embedded "
        "dialogue from narratorial report."
    )
    replace_paragraph_text_keep_formatting(doc.paragraphs[112], p112_text)
    print("Updated Paragraph 112 (Conclusion Future Work point 2).")

    doc.save(doc_path)
    print(f"SUCCESS: Saved all revisions to {doc_path}")

if __name__ == '__main__':
    # 1. Update Revisi Makalah Luthfiana Dwi Raknawati.docx
    target1 = "Revisi/Revisi Makalah Luthfiana Dwi Raknawati.docx"
    try:
        update_document(target1)
    except Exception as e:
        print(f"ERROR updating {target1}: {e}")

    # 2. Save a fresh copy as Revisi/Revisi Makalah Luthfiana Dwi Raknawati_Terbaru_Updated.docx
    target_copy = "Revisi/Revisi Makalah Luthfiana Dwi Raknawati_Terbaru_Updated.docx"
    try:
        shutil.copyfile(target1, target_copy)
        print(f"SUCCESS: Copied updated file to {target_copy}")
    except Exception as e:
        print(f"ERROR copying to {target_copy}: {e}")

    # 3. Try to update Revisi Makalah Luthfiana Dwi Raknawati_Terbaru.docx if not locked
    target2 = "Revisi/Revisi Makalah Luthfiana Dwi Raknawati_Terbaru.docx"
    try:
        shutil.copyfile(target1, target2)
        print(f"SUCCESS: Overwrote {target2} with updated file!")
    except Exception as e:
        print(f"NOTE: {target2} is currently locked by Word: {e}")
