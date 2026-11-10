"""Riwayat percakapan & statistik, disimpan di SQLite."""
import sqlite3
from contextlib import closing


class ChatHistory:
    def __init__(self, path: str):
        self.path = path
        with closing(self._conn()) as c, c:
            c.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sid TEXT NOT NULL,
                    theme TEXT NOT NULL,
                    role TEXT NOT NULL,
                    text TEXT NOT NULL,
                    intent TEXT,
                    score REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )""")
            c.execute("CREATE INDEX IF NOT EXISTS idx_sid ON messages (sid, theme)")

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def add(self, sid, theme, role, text, intent=None, score=None) -> None:
        with closing(self._conn()) as c, c:
            c.execute("INSERT INTO messages (sid, theme, role, text, intent, score) VALUES (?,?,?,?,?,?)",
                      (sid, theme, role, text, intent, score))

    def get(self, sid: str, theme: str) -> list[dict]:
        with closing(self._conn()) as c:
            rows = c.execute("SELECT role, text, intent, score, created_at FROM messages "
                             "WHERE sid=? AND theme=? ORDER BY id", (sid, theme)).fetchall()
        return [dict(r) for r in rows]

    def clear(self, sid: str, theme: str) -> None:
        with closing(self._conn()) as c, c:
            c.execute("DELETE FROM messages WHERE sid=? AND theme=?", (sid, theme))

    def stats(self, theme: str) -> dict:
        with closing(self._conn()) as c:
            row = c.execute("""
                SELECT COUNT(*) AS total,
                       COALESCE(SUM(intent='fallback'), 0) AS fallback,
                       COALESCE(AVG(score), 0) AS avg_score,
                       COUNT(DISTINCT sid) AS sessions
                FROM messages WHERE theme=? AND role='user'""", (theme,)).fetchone()
        total, fallback = row["total"], row["fallback"]
        return {
            "total_questions": total,
            "answered": total - fallback,
            "fallback": fallback,
            "fallback_rate": round(100 * fallback / total, 1) if total else 0.0,
            "avg_score": round(row["avg_score"], 3),
            "sessions": row["sessions"],
        }

    def summary(self, theme: str) -> list[dict]:
        """Jumlah pertanyaan per intent, dari yang paling sering."""
        with closing(self._conn()) as c:
            rows = c.execute("""
                SELECT intent, COUNT(*) AS count, ROUND(AVG(score), 3) AS avg_score
                FROM messages WHERE theme=? AND role='user'
                GROUP BY intent ORDER BY count DESC, intent""", (theme,)).fetchall()
        return [dict(r) for r in rows]

    def unknown_questions(self, theme: str, limit: int = 50) -> list[dict]:
        """Pertanyaan yang tidak dikenali bot: bahan untuk menambah pattern baru."""
        with closing(self._conn()) as c:
            rows = c.execute("""
                SELECT text, score, created_at FROM messages
                WHERE theme=? AND role='user' AND intent='fallback'
                ORDER BY id DESC LIMIT ?""", (theme, limit)).fetchall()
        return [dict(r) for r in rows]
