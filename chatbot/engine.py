"""Mesin chatbot berbasis kemiripan teks (tanpa library tambahan).

Cara kerja:
1. Pesan dinormalisasi: huruf kecil, buang tanda baca & kata umum (stopword).
2. Setiap pattern di tema dibandingkan dengan pesan memakai koefisien Dice
   pada tingkat kata. Kata yang mirip (typo ringan) tetap dianggap cocok.
3. Intent dengan skor tertinggi dipilih; jika skor < threshold -> fallback.
"""
import random
import re
from datetime import datetime
from difflib import SequenceMatcher

STOPWORDS = {
    "apa", "yang", "itu", "untuk", "dong", "deh", "sih", "ya", "nih", "kak",
    "dan", "di", "ke", "dari", "aku", "saya", "kamu", "bagaimana", "gimana",
    "cara", "apakah", "bisa", "boleh", "tolong", "mau", "tanya", "ini",
    "kenapa", "harus", "girl", "min", "bot", "skintant",
    "banget", "gak", "nggak", "ga", "perlu", "tahu", "aja", "sangat",
}
HARI = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
BULAN = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli",
         "Agustus", "September", "Oktober", "November", "Desember"]


def normalize(text: str) -> list[str]:
    """Teks -> daftar kata bersih. Jika semua kata stopword, pakai kata aslinya."""
    words = [re.sub(r"(ku|mu|nya)$", "", w) if len(w) > 5 else w
             for w in re.findall(r"[a-z0-9]+", text.lower())]
    cleaned = [w for w in words if w not in STOPWORDS]
    return cleaned or words

def _same_word(a: str, b: str) -> bool:
    if a == b:
        return True
    return len(a) >= 5 and len(b) >= 5 and SequenceMatcher(None, a, b).ratio() >= 0.84


def similarity(user: list[str], pattern: list[str]) -> float:
    """Koefisien Dice antar dua daftar kata, toleran terhadap typo ringan."""
    if not user or not pattern:
        return 0.0
    used, matched = set(), 0
    for word in user:
        for j, other in enumerate(pattern):
            if j not in used and _same_word(word, other):
                used.add(j)
                matched += 1
                break
    return 2 * matched / (len(user) + len(pattern))


class ChatbotEngine:
    def __init__(self, theme: dict, threshold: float = 0.45):
        self.theme = theme
        self.threshold = threshold
        self._index = [
            (intent["tag"], pattern, normalize(pattern))
            for intent in theme["intents"]
            for pattern in intent["patterns"]
        ]
        self._responses = {i["tag"]: i["responses"] for i in theme["intents"]}

    def explain(self, message: str, top: int = 3) -> list[dict]:
        """Kandidat intent teratas beserta skor dan pattern yang paling cocok."""
        user = normalize(message)
        best: dict[str, dict] = {}
        for tag, pattern, tokens in self._index:
            score = similarity(user, tokens)
            if tag not in best or score > best[tag]["score"]:
                best[tag] = {"intent": tag, "score": round(score, 3), "pattern": pattern}
        ranked = sorted(best.values(), key=lambda c: c["score"], reverse=True)
        return [c for c in ranked[:top] if c["score"] > 0]

    def _fill(self, text: str) -> str:
        now = datetime.now()
        return (text.replace("{nama_bot}", self.theme["bot_name"])
                    .replace("{waktu}", now.strftime("%H.%M"))
                    .replace("{tanggal}", f"{HARI[now.weekday()]}, {now.day} {BULAN[now.month - 1]} {now.year}"))

    def reply(self, message: str) -> dict:
        candidates = self.explain(message, top=1)
        if candidates and candidates[0]["score"] >= self.threshold:
            tag, score = candidates[0]["intent"], candidates[0]["score"]
            text = random.choice(self._responses[tag])
        else:
            tag = "fallback"
            score = candidates[0]["score"] if candidates else 0.0
            text = random.choice(self.theme["fallback"])
        return {"reply": self._fill(text), "intent": tag, "score": score,
                "bot_name": self.theme["bot_name"]}