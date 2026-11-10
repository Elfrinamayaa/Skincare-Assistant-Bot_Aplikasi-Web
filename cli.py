"""Chat lewat terminal.   Contoh:  python cli.py --theme skincare"""
import argparse
from pathlib import Path
from chatbot import ChatbotEngine, load_themes

BASE_DIR = Path(__file__).resolve().parent


def main() -> None:
    parser = argparse.ArgumentParser(description="Chatbot tematik di terminal")
    parser.add_argument("--theme", default="skincare", help="id tema (nama file di themes/)")
    parser.add_argument("--threshold", type=float, default=0.45)
    parser.add_argument("--debug", action="store_true", help="tampilkan intent dan skor")
    args = parser.parse_args()

    themes = load_themes(str(BASE_DIR / "themes"))
    if args.theme not in themes:
        raise SystemExit(f"Tema '{args.theme}' tidak ada. Pilihan: {', '.join(themes)}")
    theme = themes[args.theme]
    engine = ChatbotEngine(theme, args.threshold)

    print(f"{theme['avatar']} {theme['bot_name']}: {theme['greeting']}")
    print("(ketik 'keluar' untuk berhenti)\n")
    while True:
        try:
            message = input("Kamu : ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not message:
            continue
        if message.lower() in {"keluar", "exit", "quit"}:
            print(f"{theme['bot_name']}: Sampai jumpa!")
            break
        result = engine.reply(message)
        extra = f"  [{result['intent']} | {result['score']}]" if args.debug else ""
        print(f"{theme['bot_name']}: {result['reply']}{extra}\n")

if __name__ == "__main__":
    main()