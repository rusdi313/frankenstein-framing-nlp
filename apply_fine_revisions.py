import docx
from docx import Document
import sys

sys.stdout.reconfigure(encoding='utf-8')

def replace_paragraph_text(p, new_text):
    if not p.runs:
        p.add_run(new_text)
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

def main():
    doc_path = "Revisi/Revisi Makalah Luthfiana Dwi Raknawati (1).docx"
    print(f"Loading {doc_path}...")
    doc = Document(doc_path)
    
    # 1. Paragraph 30 (Section 2.3)
    p30_text = (
        "The unit of analysis was defined at the paragraph-level passage. In 19th-century Gothic fiction, "
        "paragraphs frequently extend beyond modern paragraph lengths (often 500–800 words in descriptive sections) "
        "and contain multi-emotional shifts (topic drift). Consequently, paragraphs exceeding 200 words were split "
        "into consecutive segments at the sentence boundary closest to each 200-word mark, so that no sentence was divided. "
        "In the gold-standard corpus, candidate paragraphs meeting the inclusion criteria that exceeded 200 words were moderately "
        "long (ranging from 206 to 297 words), resulting in exactly 10 source paragraphs being divided into two segments each "
        "(yielding 20 passages); the remaining 175 source paragraphs each produced a single passage (totaling 185 unique source "
        "paragraphs and 195 passages). Longer discursive paragraphs in the novel either lacked direct character interactions "
        "or were filtered out as Irrelevant during initial annotation. Each resulting segment was annotated independently "
        "rather than inheriting the label of its source paragraph, segments whose framing still changed internally were "
        "labeled with the priority rules in Table 1, and every segment retained the identifier of its source paragraph. "
        "Because framing can still shift within a segment, this unitization remains a source of error (Section 3.8)."
    )
    replace_paragraph_text(doc.paragraphs[30], p30_text)
    print("Updated Paragraph 30 (Section 2.3).")
    
    # 2. Paragraph 85 (Section 3.6 Poin 2)
    p85_text = (
        "2. The Creature's Victim Framing (Vol. II Chapters III & VII): In his autobiographical narrative, the Creature "
        "repeatedly emphasizes his helplessness, isolation, and social abandonment. In his earliest recollections: "
        "\"I was a poor, helpless, miserable wretch; I knew, and could distinguish, nothing; but, feeling pain invade me "
        "on all sides, I sat down and wept\" (PAS_0092, gold Victim) [1]. This vulnerable self-representation recurs "
        "during his attempt to converse with the blind De Lacey: \"I am an unfortunate and deserted creature; I look around, "
        "and I have no relation or friend upon earth\" (PAS_0186, gold Victim) [1]."
    )
    replace_paragraph_text(doc.paragraphs[85], p85_text)
    print("Updated Paragraph 85 (Section 3.6 Poin 2).")
    
    # 3. Paragraph 86 (Section 3.6 Poin 3)
    p86_text = (
        "3. Ambivalent Framing (Vol. II Chapters II & VIII):\n"
        "Ambivalent framing captures passages where moral virtue and destructive impulses coexist, or where compassion "
        "is locked in tension with horror. On Montanvert, the Creature asserts the causal link between suffering and malevolence: "
        "\"I was benevolent and good; misery made me a fiend. Make me happy, and I shall again be virtuous\" (PAS_0084, gold Ambivalent) [1]. "
        "The same passage also contains his claim to victimhood (\"Every where I see bliss, from which I alone am irrevocably excluded\"), "
        "illustrating how the Ambivalent label captures the co-presence of vulnerability and conditional menace within a single "
        "speech act. Similarly, after violent rejection from the De Lacey cottage, the Creature reflects on his agonizing despair "
        "alongside destructive rage: \"I, like the arch fiend, bore a hell within me; and, finding myself unsympathized with, "
        "wished to tear up the trees, spread havoc and destruction around me\" (PAS_0197, gold Ambivalent) [1]. On Victor's side, "
        "ambivalence surfaces when listening to the Creature on the Mer de Glace: \"For the first time, also, I felt what the "
        "duties of a creator towards his creature were, and that I ought to render him happy before I complained of his wickedness\" "
        "(PAS_0089, gold Ambivalent) [1]."
    )
    replace_paragraph_text(doc.paragraphs[86], p86_text)
    print("Updated Paragraph 86 (Section 3.6 Poin 3).")
    
    # 4. Paragraph 87 (Section 3.6 Poin 4)
    p87_text = (
        "4. Cross-Framed Passages: Table 2 also contains counter-intuitive cases: 29 of Victor's passages are labeled Victim "
        "(26.6%) and 14 of the Creature's passages are labeled Threat (17.3%). Read through Genette's distinction between "
        "voice (who speaks) and focalization (whose perspective or evaluative stance is represented) [33], Victor's "
        "narrator-level passages labeled Victim correspond primarily to instances where the external narrative voice "
        "belongs to Victor (or Walton transcribing Victor), yet the evaluative focalization centers on the Creature's suffering "
        "or directly embeds the Creature's own voice. A related tension between visual revulsion and acoustic empathy appears "
        "when Victor hears the Creature's plea for a female companion in Vol. II Chapter IX (\"His words had a strange effect "
        "upon me. I compassionated him, and sometimes felt a wish to console him; but when I looked upon him... my heart "
        "sickened\"; SEG_0472, an 86-word segment outside the 100-word gold standard threshold) [1], [34, p. 201]. In the "
        "annotated gold sample itself, this cross-framed dynamic is demonstrated in the closing frame narrative aboard Walton's "
        "ship, where Victor's overarching narration transcribes the Creature's direct lamentation over Frankenstein's corpse: "
        "\"'Oh, it is not thus -- not thus,' interrupted the being; 'yet such must be the impression conveyed to you by what "
        "appears to be the purport of my actions. Yet I seek not a fellow-feeling in my misery. No sympathy may I ever find... "
        "in what should I seek for sympathy? I am content to suffer alone, while my sufferings shall endure'\" (PAS_0336, gold "
        "Victim, predicted Victim) [1]. Here, while the structural narrative voice is situated within Victor's and Walton's "
        "frame, the passage focalizes the Creature as an agonizing, abandoned victim grieving lost virtue and companionship. "
        "Because the codebook evaluates the framing assigned to the Creature by the passage as a whole (Table 1), such "
        "embedded speeches are annotated as Victim, and the model correctly predicts them as Victim on the basis of their "
        "dense elegiac vocabulary."
    )
    replace_paragraph_text(doc.paragraphs[87], p87_text)
    print("Updated Paragraph 87 (Section 3.6 Poin 4).")
    
    # 5. Paragraph 97 (Section 3.8 Source 1)
    p97_text = (
        "Logistic Regression misclassified 65 of the 195 passages (Figure 2). As shown in the pooled confusion matrix "
        "(Figure 2), these errors consist quantitatively of: 29 Ambivalent passages misclassified (20 as Victim, 9 as Threat); "
        "27 Threat passages misclassified as Victim; and 9 Victim passages misclassified (8 as Threat, 1 as Ambivalent). "
        "A qualitative linguistic review of these 65 error cases identifies four primary textual mechanisms:\n"
        "1. Intra-Paragraph Emotional Shifts: Passages that begin with empathetic reflection or vulnerability and conclude "
        "with violent oaths combine vocabulary from opposing poles. Because n-gram TF-IDF weights words independently of "
        "clause ordering, it cannot capture how an adversative connective (such as 'but', 'yet', or 'however') pivots the "
        "overall evaluative stance of the passage. For instance, in PAS_0030, Victor opens with aesthetic dedication and "
        "care ('infinite pains and care I had endeavoured to form') before pivoting sharply to revulsion ('breathless horror "
        "and disgust filled my heart'), causing a gold Threat passage to be mispredicted as Victim. Similarly, in PAS_0084, "
        "the Creature's Montanvert plea opens with conditional virtue and suffering (\"I was benevolent and good; misery "
        "made me a fiend. Make me happy, and I shall again be virtuous\") before concluding with threats of superior physical "
        "strength, causing a gold Ambivalent passage to be misclassified as Threat."
    )
    replace_paragraph_text(doc.paragraphs[97], p97_text)
    print("Updated Paragraph 97 (Section 3.8 Source 1).")
    
    doc.save(doc_path)
    print(f"Successfully saved updated document to {doc_path}!")

if __name__ == "__main__":
    main()
