"""
Master Pipeline Runner: Eksekusi Otomatis Seluruh Tahapan F1 s.d. F8
Menjalankan seluruh alur eksperimen dari praproses korpus Gutenberg 1818 hingga pelaporan hasil.
"""

import sys
import os
import subprocess
import time

def run_step(step_name: str, script_path: str):
    print(f"\n========================================================")
    print(f"[*] Menjalankan {step_name}: {script_path}")
    print(f"========================================================")
    start_time = time.time()
    result = subprocess.run([sys.executable, script_path], capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)
        
    if result.returncode != 0:
        print(f"[!] Gagal pada tahapan {step_name} (Exit code: {result.returncode})")
        sys.exit(result.returncode)
        
    elapsed = time.time() - start_time
    print(f"[+] {step_name} SELESAI ({elapsed:.2f} detik).")

if __name__ == "__main__":
    print("========================================================")
    print(" PIPELINE KLASIFIKASI REPRESENTASI MAKHLUK FRANKENSTEIN ")
    print(" Target: Publikasi JTI (SINTA 2)                        ")
    print("========================================================")

    total_start = time.time()
    
    # F1: Korpus
    run_step("F1 - Praproses Korpus", "src/f1_corpus.py")
    
    # F2: Ekstraksi Passage
    run_step("F2 - Ekstraksi Passage", "src/f2_passages.py")
    
    # F3: Anotasi & Cohen's Kappa
    run_step("F3 - Anotasi Gold Set", "src/f3_annotation.py")
    
    # F5, F6, F7: Training & Evaluasi
    run_step("F5, F6, F7 - Pelatihan & Evaluasi Model", "src/f5_f7_experiment.py")
    
    # F8: Interpretabilitas & Visualisasi
    run_step("F8 - Interpretabilitas & Analisis Narator", "src/f8_interpretability.py")

    total_elapsed = time.time() - total_start
    print("\n========================================================")
    print(f"[SUCCESS] Seluruh pipeline F1 - F8 berhasil dieksekusi ({total_elapsed:.2f} detik).")
    print("Seluruh tabel dan visualisasi siap dimasukkan ke naskah JTI.")
    print("========================================================")
