"""
Fluent Forest: German — data layer
All persistence is done via a local SQLite file (fluent_forest.db).
This module is intentionally free of any Streamlit imports so it can be
unit-tested / reused on its own.
"""

import sqlite3
import datetime as dt
from contextlib import contextmanager
from pathlib import Path

DB_PATH = Path(__file__).parent / "fluent_forest.db"

CATEGORIES = [
    "Reading", "Listening", "Watching (YouTube)", "Podcasts", "Movies/TV",
    "Speaking", "Flashcards", "Grammar", "Writing", "Other",
]

DIFFICULTIES = ["Very Easy", "Easy", "Comfortable", "Challenging", "Very Hard"]

MILESTONES_HOURS = [10, 25, 50, 100, 250, 500, 750, 1000, 1500, 2000]

SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,              -- ISO date, e.g. 2026-07-28
    category TEXT NOT NULL,
    minutes REAL NOT NULL,
    difficulty TEXT,
    resource TEXT,
    notes TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS profile (
    key TEXT PRIMARY KEY,
    value TEXT
);

CREATE TABLE IF NOT EXISTS saved_words (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word TEXT NOT NULL,
    base_form TEXT,
    meaning TEXT,
    gender TEXT,
    plural TEXT,
    example TEXT,
    collection TEXT DEFAULT 'General',
    added_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS achievements_unlocked (
    key TEXT PRIMARY KEY,
    unlocked_at TEXT NOT NULL
);
"""

DEFAULT_PROFILE = {
    "display_name": "Sprachfreund",
    "daily_goal_minutes": "30",
    "current_theme": "Neon Megacity",
    "unlocked_themes": "Neon Megacity",
    "current_streak": "0",
    "longest_streak": "0",
    "last_study_date": "",
    "streak_freeze_tokens": "1",
    "xp": "0",
}


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_conn() as conn:
        conn.executescript(SCHEMA)
        cur = conn.execute("SELECT COUNT(*) AS c FROM profile")
        if cur.fetchone()["c"] == 0:
            for k, v in DEFAULT_PROFILE.items():
                conn.execute(
                    "INSERT INTO profile (key, value) VALUES (?, ?)", (k, v)
                )


# ---------------------------------------------------------------- profile --
def get_profile() -> dict:
    with get_conn() as conn:
        rows = conn.execute("SELECT key, value FROM profile").fetchall()
        return {r["key"]: r["value"] for r in rows}


def set_profile(key: str, value):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO profile (key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, str(value)),
        )


# --------------------------------------------------------------- sessions --
def add_session(date_str, category, minutes, difficulty, resource, notes):
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO sessions
               (date, category, minutes, difficulty, resource, notes, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                date_str, category, minutes, difficulty, resource, notes,
                dt.datetime.now().isoformat(),
            ),
        )
    _update_streak(date_str)
    _award_xp(minutes)


def get_all_sessions():
    import pandas as pd
    with get_conn() as conn:
        df = pd.read_sql_query("SELECT * FROM sessions ORDER BY date DESC, id DESC", conn)
    if not df.empty:
        df["date"] = pd.to_datetime(df["date"])
        df["hours"] = df["minutes"] / 60.0
    return df


def delete_session(session_id: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))


# ----------------------------------------------------------------- streak --
def _update_streak(date_str: str):
    profile = get_profile()
    last = profile.get("last_study_date", "")
    today = dt.date.fromisoformat(date_str)

    if last == "":
        new_streak = 1
    else:
        last_date = dt.date.fromisoformat(last)
        delta = (today - last_date).days
        if delta == 0:
            new_streak = int(profile.get("current_streak", "1") or 1)
        elif delta == 1:
            new_streak = int(profile.get("current_streak", "0") or 0) + 1
        elif delta > 1:
            tokens = int(profile.get("streak_freeze_tokens", "0") or 0)
            missed = delta - 1
            if tokens >= missed:
                set_profile("streak_freeze_tokens", tokens - missed)
                new_streak = int(profile.get("current_streak", "0") or 0) + 1
            else:
                new_streak = 1
        else:
            # backfilled an earlier date; don't disturb streak
            return

    if last == "" or today >= dt.date.fromisoformat(last):
        set_profile("last_study_date", date_str)
        set_profile("current_streak", new_streak)
        longest = int(profile.get("longest_streak", "0") or 0)
        if new_streak > longest:
            set_profile("longest_streak", new_streak)


def _award_xp(minutes: float):
    profile = get_profile()
    xp = float(profile.get("xp", "0") or 0)
    xp += minutes * 2  # 2 XP per minute studied
    set_profile("xp", xp)


def maybe_earn_streak_freeze():
    """Award a streak-freeze token every 7-day streak milestone (idempotent-ish)."""
    profile = get_profile()
    streak = int(profile.get("current_streak", "0") or 0)
    earned_key = f"freeze_earned_at_{streak}"
    if streak > 0 and streak % 7 == 0:
        with get_conn() as conn:
            row = conn.execute(
                "SELECT 1 FROM achievements_unlocked WHERE key = ?", (earned_key,)
            ).fetchone()
        if not row:
            tokens = int(profile.get("streak_freeze_tokens", "0") or 0)
            set_profile("streak_freeze_tokens", tokens + 1)
            unlock_achievement(earned_key)
            return True
    return False


# ------------------------------------------------------------ achievements --
def unlock_achievement(key: str):
    with get_conn() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO achievements_unlocked (key, unlocked_at) VALUES (?, ?)",
            (key, dt.datetime.now().isoformat()),
        )


def get_unlocked_achievements() -> set:
    with get_conn() as conn:
        rows = conn.execute("SELECT key FROM achievements_unlocked").fetchall()
        return {r["key"] for r in rows}


# ------------------------------------------------------------- saved_words --
def save_word(word, base_form, meaning, gender, plural, example, collection="General"):
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO saved_words
               (word, base_form, meaning, gender, plural, example, collection, added_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (word, base_form, meaning, gender, plural, example, collection,
             dt.datetime.now().isoformat()),
        )


def get_saved_words():
    import pandas as pd
    with get_conn() as conn:
        return pd.read_sql_query("SELECT * FROM saved_words ORDER BY added_at DESC", conn)


def delete_word(word_id: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM saved_words WHERE id = ?", (word_id,))


# ------------------------------------------------------------------ totals --
def totals():
    df = get_all_sessions()
    if df.empty:
        return {
            "total_hours": 0.0, "week_hours": 0.0, "month_hours": 0.0,
            "today_minutes": 0.0, "sessions": 0,
        }
    now = dt.datetime.now()
    today = pd._libs.NaT if False else dt.date.today()
    import pandas as pd
    week_start = pd.Timestamp(today - dt.timedelta(days=today.weekday()))
    month_start = pd.Timestamp(today.replace(day=1))
    total_hours = df["hours"].sum()
    week_hours = df[df["date"] >= week_start]["hours"].sum()
    month_hours = df[df["date"] >= month_start]["hours"].sum()
    today_minutes = df[df["date"] == pd.Timestamp(today)]["minutes"].sum()
    return {
        "total_hours": round(total_hours, 2),
        "week_hours": round(week_hours, 2),
        "month_hours": round(month_hours, 2),
        "today_minutes": round(today_minutes, 1),
        "sessions": len(df),
    }
