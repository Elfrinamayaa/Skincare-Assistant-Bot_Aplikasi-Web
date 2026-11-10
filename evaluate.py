"""Evaluasi akurasi chatbot memakai data uji di folder evaluasi/.

Contoh:
    python evaluate.py
    python evaluate.py --theme skincare --threshold 0.5
Hasil rinci disimpan ke evaluasi/hasil_evaluasi.csv
"""
import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

from chatbot import ChatbotEngine, load_themes

BASE_DIR = Path(__file__).resolve().parent


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluasi akurasi intent")
    parser.add_argument("--theme", default="skincare")
    parser.add_argument("--threshold", type=float, default=0.45)
    parser.add_argument("--data", help="file data uji (default evaluasi/data_uji_<tema>.json)")
    args = parser.parse_args()

    themes = load_themes(str(BASE_DIR / "themes"))
    if args.theme not in themes:
        raise SystemExit(f"Tema '{args.theme}' tidak ada. Pilihan: {', '.join(themes)}")
    engine = ChatbotEngine(themes[args.theme], args.threshold)
    data_path = Path(args.data) if args.data else BASE_DIR / "evaluasi" / f"data_uji_{args.theme}.json"
    cases = json.loads(data_path.read_text(encoding="utf-8"))

    rows, per_intent = [], defaultdict(lambda: [0, 0])
    for case in cases:
        result = engine.reply(case["question"])
        ok = result["intent"] == case["expected"]
        per_intent[case["expected"]][0] += ok
        per_intent[case["expected"]][1] += 1
        rows.append({"pertanyaan": case["question"], "harapan": case["expected"],
                     "prediksi": result["intent"], "skor": result["score"],
                     "benar": "ya" if ok else "tidak"})

    correct = sum(r["benar"] == "ya" for r in rows)
    print(f"Tema: {args.theme} | threshold: {args.threshold} | data uji: {len(rows)}")
    print(f"Akurasi: {correct}/{len(rows)} = {100 * correct / len(rows):.1f}%\n")
    print(f"{'Intent':<18}{'Benar':>6}{'Total':>7}{'Akurasi':>9}")
    for tag, (ok, total) in sorted(per_intent.items()):
        print(f"{tag:<18}{ok:>6}{total:>7}{100 * ok / total:>8.0f}%")

    wrong = [r for r in rows if r["benar"] == "tidak"]
    if wrong:
        print("\nPrediksi yang salah:")
        for r in wrong:
            print(f"  '{r['pertanyaan']}' -> {r['prediksi']} (harapan {r['harapan']}, skor {r['skor']})")

    out = BASE_DIR / "evaluasi" / "hasil_evaluasi.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nHasil rinci disimpan di {out.relative_to(BASE_DIR)}")


if __name__ == "__main__":
    main()
