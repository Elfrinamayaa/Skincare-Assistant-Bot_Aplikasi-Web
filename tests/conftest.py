import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app import create_app  # noqa: E402
from chatbot import ChatbotEngine, load_themes  # noqa: E402


@pytest.fixture(scope="session")
def themes():
    return load_themes(str(ROOT / "themes"))


@pytest.fixture()
def engine(themes):
    return ChatbotEngine(themes["skincare"], 0.45)


@pytest.fixture()
def client(tmp_path):
    app = create_app({"TESTING": True, "DATABASE": str(tmp_path / "test.db")})
    return app.test_client()
