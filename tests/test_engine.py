import json
from pathlib import Path

import pytest

from chatbot import normalize, similarity, validate_theme

ROOT = Path(__file__).resolve().parent.parent


def test_theme_valid(themes):
    validate_theme(themes["skincare"])
    assert themes["skincare"]["bot_name"] == "SkinTant"


def test_theme_missing_key_rejected():
    with pytest.raises(ValueError):
        validate_theme({"id": "x"})


def test_normalize_removes_punctuation_and_stopwords():
    assert normalize("Skincare untuk KULIT berminyak, apa?!") == ["skincare", "kulit", "berminyak"]


def test_similarity_identical_is_one():
    assert similarity(["kulit", "kering"], ["kulit", "kering"]) == 1.0


@pytest.mark.parametrize("question,intent", [
    ("Hai", "sapaan"),
    ("Skincare untuk kulit berminyak apa?", "oily_skin"),
    ("Bagaimana merawat kulit kering?", "dry_skin"),
    ("Bagaimana mengatasi jerawat?", "acne_skin"),
    ("Bagaimana menghilangkan bekas jerawat?", "acne_scars"),
    ("Kenapa harus menggunakan sunscreen?", "sunscreen"),
    ("sunscren", "sunscreen"),
    ("Apa itu double cleansing?", "double_cleansing"),
    ("Dadah", "goodbye"),
])
def test_intent_dikenali(engine, question, intent):
    assert engine.reply(question)["intent"] == intent


def test_jawaban_sesuai_dokumen(engine):
    reply = engine.reply("Apa itu skin barrier?")["reply"]
    assert reply.startswith("Skin barrier adalah lapisan pelindung kulit")


def test_di_luar_topik_masuk_fallback(engine, themes):
    result = engine.reply("harga iphone terbaru berapa")
    assert result["intent"] == "fallback"
    assert result["reply"] in themes["skincare"]["fallback"]


def test_explain_mengembalikan_tiga_kandidat(engine):
    top = engine.explain("kulit berminyak")
    assert len(top) <= 3 and top[0]["intent"] == "oily_skin"
    assert top == sorted(top, key=lambda c: c["score"], reverse=True)


def test_data_uji_akurasi_minimal_90_persen(engine):
    cases = json.loads((ROOT / "evaluasi" / "data_uji_skincare.json").read_text(encoding="utf-8"))
    benar = sum(engine.reply(c["question"])["intent"] == c["expected"] for c in cases)
    assert benar / len(cases) >= 0.9
