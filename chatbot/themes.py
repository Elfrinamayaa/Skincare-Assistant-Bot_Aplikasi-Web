"""Memuat dan memvalidasi file tema (*.json) dari folder themes/."""
import json
from pathlib import Path

REQUIRED = ("id", "name", "bot_name", "greeting", "fallback", "intents")


def validate_theme(theme: dict, source: str = "tema") -> None:
    """Melempar ValueError dengan pesan jelas jika struktur tema salah."""
    for key in REQUIRED:
        if key not in theme:
            raise ValueError(f"{source}: kunci '{key}' wajib ada")
    if not theme["fallback"]:
        raise ValueError(f"{source}: 'fallback' minimal berisi satu jawaban")
    tags = set()
    for intent in theme["intents"]:
        tag = intent.get("tag")
        if not tag or not intent.get("patterns") or not intent.get("responses"):
            raise ValueError(f"{source}: intent '{tag}' harus punya tag, patterns, dan responses")
        if tag in tags:
            raise ValueError(f"{source}: tag '{tag}' ganda")
        tags.add(tag)


def load_themes(folder: str) -> dict:
    """Mengembalikan {id_tema: dict_tema} dari semua file .json di folder."""
    themes = {}
    for path in sorted(Path(folder).glob("*.json")):
        with open(path, encoding="utf-8") as f:
            theme = json.load(f)
        validate_theme(theme, path.name)
        theme.setdefault("avatar", "🤖")
        theme.setdefault("color", "#2563eb")
        theme.setdefault("description", "")
        theme.setdefault("suggestions", [])
        themes[theme["id"]] = theme
    return themes
