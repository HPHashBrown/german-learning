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

CREATE TABLE IF NOT EXISTS daily_challenges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    difficulty TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    xp_reward INTEGER NOT NULL,
    completed INTEGER NOT NULL DEFAULT 0,
    completed_at TEXT,
    UNIQUE(date, difficulty)
);

CREATE TABLE IF NOT EXISTS favorites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_type TEXT NOT NULL,
    title TEXT NOT NULL,
    url TEXT,
    notes TEXT,
    added_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS resource_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    resource_id TEXT NOT NULL,
    shown_at TEXT NOT NULL,
    completed INTEGER NOT NULL DEFAULT 0,
    completed_at TEXT
);

CREATE TABLE IF NOT EXISTS study_notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS weekly_reflections (
    week_start TEXT PRIMARY KEY,
    report_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS study_plan (
    day_of_week TEXT PRIMARY KEY,
    activity TEXT,
    minutes INTEGER
);

CREATE TABLE IF NOT EXISTS timeline_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_key TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    icon TEXT,
    occurred_at TEXT NOT NULL
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
    "font_size": "Medium",
    "high_contrast": "0",
    "reduced_motion": "0",
    "colorblind_mode": "0",
    "layout_density": "Spacious",
    "keyboard_shortcuts": "0",
    "created_at": dt.datetime.now().isoformat(),
    "target_cefr": "B2",
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
    import pandas as pd
    today = dt.date.today()
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


def hours_before(cutoff_date: dt.date) -> float:
    """Total hours logged strictly before a given date — used for trend/forecast math."""
    df = get_all_sessions()
    if df.empty:
        return 0.0
    import pandas as pd
    cut = pd.Timestamp(cutoff_date)
    return round(df[df["date"] < cut]["hours"].sum(), 2)


# -------------------------------------------------------------- challenges --
def ensure_daily_challenges(date_str: str, challenges: list):
    """challenges: list of dicts with difficulty/title/description/xp_reward.
    Idempotent — only inserts if that date+difficulty combo doesn't exist yet."""
    with get_conn() as conn:
        for c in challenges:
            conn.execute(
                """INSERT OR IGNORE INTO daily_challenges
                   (date, difficulty, title, description, xp_reward, completed)
                   VALUES (?, ?, ?, ?, ?, 0)""",
                (date_str, c["difficulty"], c["title"], c["description"], c["xp_reward"]),
            )


def get_challenges_for_date(date_str: str):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM daily_challenges WHERE date = ? ORDER BY "
            "CASE difficulty WHEN 'Easy' THEN 1 WHEN 'Medium' THEN 2 ELSE 3 END",
            (date_str,),
        ).fetchall()
        return [dict(r) for r in rows]


def complete_challenge(challenge_id: int):
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM daily_challenges WHERE id = ?", (challenge_id,)).fetchone()
        if not row or row["completed"]:
            return None
        conn.execute(
            "UPDATE daily_challenges SET completed = 1, completed_at = ? WHERE id = ?",
            (dt.datetime.now().isoformat(), challenge_id),
        )
        xp_reward = row["xp_reward"]
    _award_xp_raw(xp_reward)
    return xp_reward


def recent_challenge_titles(days: int = 14):
    cutoff = (dt.date.today() - dt.timedelta(days=days)).isoformat()
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT DISTINCT title FROM daily_challenges WHERE date >= ?", (cutoff,)
        ).fetchall()
        return {r["title"] for r in rows}


def challenge_completion_stats():
    with get_conn() as conn:
        total = conn.execute("SELECT COUNT(*) c FROM daily_challenges").fetchone()["c"]
        done = conn.execute("SELECT COUNT(*) c FROM daily_challenges WHERE completed = 1").fetchone()["c"]
    return {"total": total, "completed": done}


def _award_xp_raw(amount: float):
    profile = get_profile()
    xp = float(profile.get("xp", "0") or 0)
    set_profile("xp", xp + amount)


# --------------------------------------------------------------- favorites --
def add_favorite(item_type, title, url, notes=""):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO favorites (item_type, title, url, notes, added_at) VALUES (?, ?, ?, ?, ?)",
            (item_type, title, url, notes, dt.datetime.now().isoformat()),
        )


def get_favorites():
    import pandas as pd
    with get_conn() as conn:
        return pd.read_sql_query("SELECT * FROM favorites ORDER BY added_at DESC", conn)


def delete_favorite(fav_id: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM favorites WHERE id = ?", (fav_id,))


# ---------------------------------------------------------- resource history --
def mark_resource_shown(resource_id: str):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO resource_history (resource_id, shown_at, completed) VALUES (?, ?, 0)",
            (resource_id, dt.datetime.now().isoformat()),
        )


def mark_resource_completed(resource_id: str):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT id FROM resource_history WHERE resource_id = ? AND completed = 0 "
            "ORDER BY shown_at DESC LIMIT 1", (resource_id,),
        ).fetchone()
        if row:
            conn.execute(
                "UPDATE resource_history SET completed = 1, completed_at = ? WHERE id = ?",
                (dt.datetime.now().isoformat(), row["id"]),
            )
        else:
            conn.execute(
                "INSERT INTO resource_history (resource_id, shown_at, completed, completed_at) "
                "VALUES (?, ?, 1, ?)",
                (resource_id, dt.datetime.now().isoformat(), dt.datetime.now().isoformat()),
            )


def recently_shown_resource_ids(days: int = 21):
    cutoff = (dt.date.today() - dt.timedelta(days=days)).isoformat()
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT DISTINCT resource_id FROM resource_history WHERE shown_at >= ?", (cutoff,)
        ).fetchall()
        return {r["resource_id"] for r in rows}


def completed_resource_ids():
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT DISTINCT resource_id FROM resource_history WHERE completed = 1"
        ).fetchall()
        return {r["resource_id"] for r in rows}


# -------------------------------------------------------------- study notes --
def add_note(date_str, content):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO study_notes (date, content, created_at) VALUES (?, ?, ?)",
            (date_str, content, dt.datetime.now().isoformat()),
        )


def get_notes():
    import pandas as pd
    with get_conn() as conn:
        return pd.read_sql_query("SELECT * FROM study_notes ORDER BY date DESC", conn)


# --------------------------------------------------------- weekly reflection --
def save_weekly_reflection(week_start_str, report_dict):
    import json
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO weekly_reflections (week_start, report_json, created_at) VALUES (?, ?, ?) "
            "ON CONFLICT(week_start) DO UPDATE SET report_json=excluded.report_json",
            (week_start_str, json.dumps(report_dict), dt.datetime.now().isoformat()),
        )


def get_weekly_reflection(week_start_str):
    import json
    with get_conn() as conn:
        row = conn.execute(
            "SELECT report_json FROM weekly_reflections WHERE week_start = ?", (week_start_str,)
        ).fetchone()
    return json.loads(row["report_json"]) if row else None


def get_all_weekly_reflections():
    import json
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT week_start, report_json FROM weekly_reflections ORDER BY week_start DESC"
        ).fetchall()
    return [(r["week_start"], json.loads(r["report_json"])) for r in rows]


# ------------------------------------------------------------- study plan --
DEFAULT_PLAN = {
    "Monday": ("Listening + Reading", 30),
    "Tuesday": ("Grammar", 30),
    "Wednesday": ("YouTube / Video", 30),
    "Thursday": ("Podcast", 30),
    "Friday": ("News Article", 30),
    "Saturday": ("Conversation Practice", 30),
    "Sunday": ("Review / Flashcards", 30),
}


def ensure_study_plan():
    with get_conn() as conn:
        cur = conn.execute("SELECT COUNT(*) c FROM study_plan").fetchone()
        if cur["c"] == 0:
            for day, (activity, minutes) in DEFAULT_PLAN.items():
                conn.execute(
                    "INSERT INTO study_plan (day_of_week, activity, minutes) VALUES (?, ?, ?)",
                    (day, activity, minutes),
                )


def get_study_plan():
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM study_plan").fetchall()
    order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    plan = {r["day_of_week"]: dict(r) for r in rows}
    return [plan[d] for d in order if d in plan]


def set_study_plan_day(day_of_week, activity, minutes):
    with get_conn() as conn:
        conn.execute(
            "UPDATE study_plan SET activity = ?, minutes = ? WHERE day_of_week = ?",
            (activity, minutes, day_of_week),
        )


# ---------------------------------------------------------------- timeline --
def record_timeline_event(event_key, title, description, icon, occurred_at=None):
    """Idempotent — a given event_key is only ever recorded once."""
    with get_conn() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO timeline_events (event_key, title, description, icon, occurred_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (event_key, title, description, icon, occurred_at or dt.datetime.now().isoformat()),
        )


def get_timeline():
    import pandas as pd
    with get_conn() as conn:
        return pd.read_sql_query(
            "SELECT * FROM timeline_events ORDER BY occurred_at ASC", conn
        )


# ---------------------------------------------------------- export / import --
def export_all_data() -> dict:
    """Full JSON-serializable snapshot of all user data for backup/migration."""
    import json
    with get_conn() as conn:
        def rows(table):
            return [dict(r) for r in conn.execute(f"SELECT * FROM {table}").fetchall()]

        return {
            "exported_at": dt.datetime.now().isoformat(),
            "profile": get_profile(),
            "sessions": rows("sessions"),
            "saved_words": rows("saved_words"),
            "achievements_unlocked": rows("achievements_unlocked"),
            "daily_challenges": rows("daily_challenges"),
            "favorites": rows("favorites"),
            "resource_history": rows("resource_history"),
            "study_notes": rows("study_notes"),
            "weekly_reflections": rows("weekly_reflections"),
            "study_plan": rows("study_plan"),
            "timeline_events": rows("timeline_events"),
        }


def import_all_data(data: dict, mode: str = "merge"):
    """Restore data previously produced by export_all_data().
    mode='merge' keeps existing rows and adds missing ones (skip on conflict);
    mode='replace' wipes current data first."""
    tables = [
        "sessions", "saved_words", "achievements_unlocked", "daily_challenges",
        "favorites", "resource_history", "study_notes", "weekly_reflections",
        "study_plan", "timeline_events",
    ]
    with get_conn() as conn:
        if mode == "replace":
            for t in tables:
                conn.execute(f"DELETE FROM {t}")

        for key, value in data.get("profile", {}).items():
            conn.execute(
                "INSERT INTO profile (key, value) VALUES (?, ?) "
                "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (key, str(value)),
            )

        for table in tables:
            for row in data.get(table, []):
                row = dict(row)
                row.pop("id", None)  # let autoincrement assign fresh ids on merge
                cols = ", ".join(row.keys())
                placeholders = ", ".join(["?"] * len(row))
                try:
                    conn.execute(
                        f"INSERT OR IGNORE INTO {table} ({cols}) VALUES ({placeholders})",
                        tuple(row.values()),
                    )
                except sqlite3.IntegrityError:
                    continue
