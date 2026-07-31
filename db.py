"""
Fluent Forest RPG — data layer.
Everything persists to SQLite (fluent_forest_rpg.db). No Streamlit imports here
so this module can be tested standalone.
"""

import sqlite3
import datetime as dt
import json
from contextlib import contextmanager
from pathlib import Path

DB_PATH = Path(__file__).parent / "fluent_forest_rpg.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS profile (
    key TEXT PRIMARY KEY,
    value TEXT
);

CREATE TABLE IF NOT EXISTS inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id TEXT NOT NULL,
    item_type TEXT NOT NULL,     -- theme, avatar_hair, avatar_clothes, avatar_bg, avatar_frame, pet, title, decoration, xp_effect
    rarity TEXT NOT NULL,
    acquired_at TEXT NOT NULL,
    acquired_via TEXT,           -- shop, chest, achievement
    UNIQUE(item_id)
);

CREATE TABLE IF NOT EXISTS achievements_unlocked (
    key TEXT PRIMARY KEY,
    unlocked_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS vocabulary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word TEXT NOT NULL,
    meaning TEXT NOT NULL,
    gender TEXT,
    example TEXT,
    tag TEXT DEFAULT 'General',
    favorite INTEGER DEFAULT 0,
    srs_state TEXT DEFAULT 'New',   -- New, Learning, Review, Mastered
    ease REAL DEFAULT 2.5,
    interval_days REAL DEFAULT 0,
    repetitions INTEGER DEFAULT 0,
    due_date TEXT NOT NULL,
    added_at TEXT NOT NULL,
    UNIQUE(word)
);

CREATE TABLE IF NOT EXISTS quiz_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quiz_type TEXT NOT NULL,      -- vocabulary, grammar, article, verb, listening, reading
    category TEXT,
    score INTEGER NOT NULL,
    total INTEGER NOT NULL,
    xp_earned INTEGER NOT NULL,
    date TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS story_progress (
    story_id TEXT PRIMARY KEY,
    completed INTEGER DEFAULT 0,
    comprehension_score INTEGER,
    completed_at TEXT
);

CREATE TABLE IF NOT EXISTS daily_login (
    date TEXT PRIMARY KEY,
    reward_json TEXT NOT NULL,
    claimed_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS weekly_challenges (
    week_start TEXT NOT NULL,
    challenge_key TEXT NOT NULL,
    progress REAL DEFAULT 0,
    target REAL NOT NULL,
    completed INTEGER DEFAULT 0,
    reward_claimed INTEGER DEFAULT 0,
    PRIMARY KEY (week_start, challenge_key)
);

CREATE TABLE IF NOT EXISTS shop_daily (
    date TEXT PRIMARY KEY,
    items_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS xp_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    amount INTEGER NOT NULL,
    source TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS chest_openings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chest_type TEXT NOT NULL,
    item_won TEXT NOT NULL,
    rarity_won TEXT NOT NULL,
    opened_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS ai_conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scenario TEXT NOT NULL,
    role TEXT NOT NULL,          -- user / model
    content TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS immersion_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    hours REAL NOT NULL,
    category TEXT,
    notes TEXT,
    xp_earned INTEGER NOT NULL,
    coins_earned INTEGER NOT NULL,
    created_at TEXT NOT NULL
);
"""

DEFAULT_PROFILE = {
    "display_name": "Sprachheld",
    "xp": "0",
    "coins": "100",
    "level": "1",
    "current_streak": "0",
    "longest_streak": "0",
    "last_login_date": "",
    "streak_freeze_tokens": "1",
    "dark_mode": "1",
    "sound_enabled": "1",
    "equipped_theme": "light",
    "equipped_pet": "",
    "equipped_avatar_hair": "",
    "equipped_avatar_clothes": "",
    "equipped_avatar_bg": "",
    "equipped_avatar_frame": "",
    "equipped_title": "",
    "equipped_xp_effect": "xp_normal",
    "created_at": dt.datetime.now().isoformat(),
    "common_keys": "0",
    "uncommon_keys": "0",
    "rare_keys": "0",
    "legendary_keys": "0",
    "coin_activity_date": "",
    "coin_activity_count": "0",
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
                conn.execute("INSERT INTO profile (key, value) VALUES (?, ?)", (k, v))
        # Everyone starts owning the free/default cosmetics
        conn.execute(
            "INSERT OR IGNORE INTO inventory (item_id, item_type, rarity, acquired_at, acquired_via) "
            "VALUES ('light', 'theme', 'common', ?, 'starter')", (dt.datetime.now().isoformat(),)
        )
        conn.execute(
            "INSERT OR IGNORE INTO inventory (item_id, item_type, rarity, acquired_at, acquired_via) "
            "VALUES ('xp_normal', 'xp_effect', 'common', ?, 'starter')", (dt.datetime.now().isoformat(),)
        )


# ------------------------------------------------------------------ profile --
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


def add_xp(amount: int, source: str):
    profile = get_profile()
    xp = int(float(profile.get("xp", "0") or 0)) + amount
    set_profile("xp", xp)
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO xp_log (date, amount, source) VALUES (?, ?, ?)",
            (dt.date.today().isoformat(), amount, source),
        )
    return xp


def add_coins(amount: int):
    profile = get_profile()
    coins = int(float(profile.get("coins", "0") or 0)) + amount
    coins = max(0, coins)
    set_profile("coins", coins)
    return coins


def spend_coins(amount: int) -> bool:
    profile = get_profile()
    coins = int(float(profile.get("coins", "0") or 0))
    if coins < amount:
        return False
    set_profile("coins", coins - amount)
    return True


def get_xp_log():
    import pandas as pd
    with get_conn() as conn:
        return pd.read_sql_query("SELECT * FROM xp_log ORDER BY date", conn)


# --------------------------------------------------------------- inventory --
def grant_item(item_id: str, item_type: str, rarity: str, via: str = "shop"):
    with get_conn() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO inventory (item_id, item_type, rarity, acquired_at, acquired_via) "
            "VALUES (?, ?, ?, ?, ?)",
            (item_id, item_type, rarity, dt.datetime.now().isoformat(), via),
        )


def owns_item(item_id: str) -> bool:
    with get_conn() as conn:
        row = conn.execute("SELECT 1 FROM inventory WHERE item_id = ?", (item_id,)).fetchone()
        return row is not None


def get_inventory():
    import pandas as pd
    with get_conn() as conn:
        return pd.read_sql_query("SELECT * FROM inventory ORDER BY acquired_at DESC", conn)


def owned_item_ids(item_type: str = None):
    with get_conn() as conn:
        if item_type:
            rows = conn.execute("SELECT item_id FROM inventory WHERE item_type = ?", (item_type,)).fetchall()
        else:
            rows = conn.execute("SELECT item_id FROM inventory").fetchall()
        return {r["item_id"] for r in rows}


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


# --------------------------------------------------------------- vocabulary --
def add_vocab(word, meaning, gender="—", example="", tag="General"):
    with get_conn() as conn:
        conn.execute(
            """INSERT OR IGNORE INTO vocabulary
               (word, meaning, gender, example, tag, due_date, added_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (word, meaning, gender, example, tag, dt.date.today().isoformat(),
             dt.datetime.now().isoformat()),
        )


def get_vocab_df():
    import pandas as pd
    with get_conn() as conn:
        return pd.read_sql_query("SELECT * FROM vocabulary ORDER BY added_at DESC", conn)


def get_due_flashcards(limit=20):
    import pandas as pd
    today = dt.date.today().isoformat()
    with get_conn() as conn:
        df = pd.read_sql_query(
            "SELECT * FROM vocabulary WHERE due_date <= ? ORDER BY due_date LIMIT ?",
            conn, params=(today, limit),
        )
    return df


def update_flashcard_srs(word_id: int, ease: float, interval_days: float, repetitions: int,
                          due_date: str, srs_state: str):
    with get_conn() as conn:
        conn.execute(
            "UPDATE vocabulary SET ease=?, interval_days=?, repetitions=?, due_date=?, srs_state=? "
            "WHERE id=?",
            (ease, interval_days, repetitions, due_date, srs_state, word_id),
        )


def toggle_favorite(word_id: int):
    with get_conn() as conn:
        row = conn.execute("SELECT favorite FROM vocabulary WHERE id=?", (word_id,)).fetchone()
        if row:
            conn.execute("UPDATE vocabulary SET favorite=? WHERE id=?", (0 if row["favorite"] else 1, word_id))


def delete_vocab(word_id: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM vocabulary WHERE id=?", (word_id,))


# --------------------------------------------------------------- quizzes --
def record_quiz(quiz_type, category, score, total, xp_earned):
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO quiz_results (quiz_type, category, score, total, xp_earned, date, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (quiz_type, category, score, total, xp_earned, dt.date.today().isoformat(),
             dt.datetime.now().isoformat()),
        )


def get_quiz_results():
    import pandas as pd
    with get_conn() as conn:
        return pd.read_sql_query("SELECT * FROM quiz_results ORDER BY created_at DESC", conn)


# --------------------------------------------------------------- stories --
def mark_story_complete(story_id, comprehension_score):
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO story_progress (story_id, completed, comprehension_score, completed_at)
               VALUES (?, 1, ?, ?)
               ON CONFLICT(story_id) DO UPDATE SET completed=1,
                    comprehension_score=excluded.comprehension_score,
                    completed_at=excluded.completed_at""",
            (story_id, comprehension_score, dt.datetime.now().isoformat()),
        )


def get_story_progress():
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM story_progress").fetchall()
        return {r["story_id"]: dict(r) for r in rows}


# ------------------------------------------------------------- daily login --
def get_login_record(date_str):
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM daily_login WHERE date = ?", (date_str,)).fetchone()
        return dict(row) if row else None


def claim_daily_login(date_str, reward: dict):
    with get_conn() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO daily_login (date, reward_json, claimed_at) VALUES (?, ?, ?)",
            (date_str, json.dumps(reward), dt.datetime.now().isoformat()),
        )


def consecutive_login_days():
    with get_conn() as conn:
        rows = conn.execute("SELECT date FROM daily_login ORDER BY date DESC").fetchall()
    if not rows:
        return 0
    dates = [dt.date.fromisoformat(r["date"]) for r in rows]
    count = 1
    for i in range(1, len(dates)):
        if (dates[i - 1] - dates[i]).days == 1:
            count += 1
        else:
            break
    return count


def total_login_days():
    with get_conn() as conn:
        return conn.execute("SELECT COUNT(*) c FROM daily_login").fetchone()["c"]


# --------------------------------------------------------- weekly challenges --
def ensure_weekly_challenges(week_start_str, challenges: list):
    with get_conn() as conn:
        for c in challenges:
            conn.execute(
                "INSERT OR IGNORE INTO weekly_challenges (week_start, challenge_key, progress, target) "
                "VALUES (?, ?, 0, ?)",
                (week_start_str, c["key"], c["target"]),
            )


def get_weekly_challenges(week_start_str):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM weekly_challenges WHERE week_start = ?", (week_start_str,)
        ).fetchall()
        return [dict(r) for r in rows]


def bump_weekly_progress(week_start_str, challenge_key, amount):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM weekly_challenges WHERE week_start=? AND challenge_key=?",
            (week_start_str, challenge_key),
        ).fetchone()
        if not row:
            return
        new_progress = row["progress"] + amount
        completed = 1 if new_progress >= row["target"] else row["completed"]
        conn.execute(
            "UPDATE weekly_challenges SET progress=?, completed=? WHERE week_start=? AND challenge_key=?",
            (new_progress, completed, week_start_str, challenge_key),
        )


def claim_weekly_reward(week_start_str, challenge_key):
    with get_conn() as conn:
        conn.execute(
            "UPDATE weekly_challenges SET reward_claimed=1 WHERE week_start=? AND challenge_key=?",
            (week_start_str, challenge_key),
        )


# -------------------------------------------------------------- shop/keys --
def get_shop_for_date(date_str):
    with get_conn() as conn:
        row = conn.execute("SELECT items_json FROM shop_daily WHERE date = ?", (date_str,)).fetchone()
        return json.loads(row["items_json"]) if row else None


def save_shop_for_date(date_str, items: list):
    with get_conn() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO shop_daily (date, items_json) VALUES (?, ?)",
            (date_str, json.dumps(items)),
        )


def add_keys(key_type: str, amount: int):
    field = f"{key_type}_keys"
    profile = get_profile()
    current = int(float(profile.get(field, "0") or 0))
    set_profile(field, current + amount)


def spend_key(key_type: str) -> bool:
    field = f"{key_type}_keys"
    profile = get_profile()
    current = int(float(profile.get(field, "0") or 0))
    if current < 1:
        return False
    set_profile(field, current - 1)
    return True


def record_chest_opening(chest_type, item_won, rarity_won):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO chest_openings (chest_type, item_won, rarity_won, opened_at) VALUES (?, ?, ?, ?)",
            (chest_type, item_won, rarity_won, dt.datetime.now().isoformat()),
        )


def get_chest_history():
    import pandas as pd
    with get_conn() as conn:
        return pd.read_sql_query("SELECT * FROM chest_openings ORDER BY opened_at DESC", conn)


# ---------------------------------------------------------------- streak --
def process_login_streak(today: dt.date = None):
    """Call once per session load. Updates streak based on calendar days since last login."""
    today = today or dt.date.today()
    profile = get_profile()
    last = profile.get("last_login_date", "")

    if last == today.isoformat():
        return int(profile.get("current_streak", "0") or 0), False  # already processed today

    if last == "":
        new_streak = 1
    else:
        last_date = dt.date.fromisoformat(last)
        delta = (today - last_date).days
        if delta == 1:
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
            new_streak = int(profile.get("current_streak", "0") or 0)

    set_profile("last_login_date", today.isoformat())
    set_profile("current_streak", new_streak)
    longest = int(profile.get("longest_streak", "0") or 0)
    if new_streak > longest:
        set_profile("longest_streak", new_streak)
    if new_streak > 0 and new_streak % 7 == 0:
        tokens = int(get_profile().get("streak_freeze_tokens", "0") or 0)
        set_profile("streak_freeze_tokens", tokens + 1)

    return new_streak, True


# ----------------------------------------------------------- AI conversations --
def add_conversation_message(scenario, role, content):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO ai_conversations (scenario, role, content, created_at) VALUES (?, ?, ?, ?)",
            (scenario, role, content, dt.datetime.now().isoformat()),
        )


def get_conversation(scenario):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT role, content FROM ai_conversations WHERE scenario = ? ORDER BY id", (scenario,)
        ).fetchall()
        return [dict(r) for r in rows]


def clear_conversation(scenario):
    with get_conn() as conn:
        conn.execute("DELETE FROM ai_conversations WHERE scenario = ?", (scenario,))


# -------------------------------------------------------- immersion hours --
# Conversion rates from logged immersion hours to XP/coins. Kept as module
# constants (not buried in app.py) so the Wallet/Statistics pages and any
# future forecast tooling can reference the same numbers.
IMMERSION_XP_PER_HOUR = 60
IMMERSION_COINS_PER_HOUR = 15


def add_immersion_session(date_str, hours, category, notes):
    """Records the session and awards XP immediately (XP is never affected by
    town buildings — only coins are). Returns (xp_earned, base_coins_earned);
    the caller is responsible for running base_coins_earned through any town
    coin-bonus calculation and awarding the final coins itself."""
    xp_earned = round(hours * IMMERSION_XP_PER_HOUR)
    base_coins_earned = round(hours * IMMERSION_COINS_PER_HOUR)
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO immersion_sessions
               (date, hours, category, notes, xp_earned, coins_earned, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (date_str, hours, category, notes, xp_earned, base_coins_earned,
             dt.datetime.now().isoformat()),
        )
    add_xp(xp_earned, "immersion_hours")
    return xp_earned, base_coins_earned


def get_immersion_sessions():
    import pandas as pd
    with get_conn() as conn:
        df = pd.read_sql_query(
            "SELECT * FROM immersion_sessions ORDER BY date DESC, id DESC", conn
        )
    if not df.empty:
        df["date"] = pd.to_datetime(df["date"])
    return df


def immersion_totals():
    df = get_immersion_sessions()
    if df.empty:
        return {"total_hours": 0.0, "week_hours": 0.0, "month_hours": 0.0, "sessions": 0}
    import pandas as pd
    today = dt.date.today()
    week_start = pd.Timestamp(today - dt.timedelta(days=today.weekday()))
    month_start = pd.Timestamp(today.replace(day=1))
    return {
        "total_hours": round(float(df["hours"].sum()), 2),
        "week_hours": round(float(df[df["date"] >= week_start]["hours"].sum()), 2),
        "month_hours": round(float(df[df["date"] >= month_start]["hours"].sum()), 2),
        "sessions": len(df),
    }


# -------------------------------------------------------------- wallet ----
def get_recent_purchases(limit=15):
    """Items acquired via the shop or a loot chest (i.e. actual 'purchases' in
    the coins-economy sense — starter/daily-reward/achievement grants excluded)."""
    import pandas as pd
    with get_conn() as conn:
        return pd.read_sql_query(
            "SELECT * FROM inventory WHERE acquired_via IN ('shop','chest') "
            "ORDER BY acquired_at DESC LIMIT ?",
            conn, params=(limit,),
        )


def coin_activity_plays_today() -> int:
    profile = get_profile()
    today_str = dt.date.today().isoformat()
    if profile.get("coin_activity_date") != today_str:
        return 0
    return int(float(profile.get("coin_activity_count", "0") or 0))


def register_coin_activity_play():
    today_str = dt.date.today().isoformat()
    profile = get_profile()
    count = coin_activity_plays_today()
    set_profile("coin_activity_date", today_str)
    set_profile("coin_activity_count", count + 1)


# ---------------------------------------------------------------- export --
def export_all_data() -> dict:
    with get_conn() as conn:
        def rows(table):
            return [dict(r) for r in conn.execute(f"SELECT * FROM {table}").fetchall()]
        return {
            "exported_at": dt.datetime.now().isoformat(),
            "profile": get_profile(),
            "inventory": rows("inventory"),
            "achievements_unlocked": rows("achievements_unlocked"),
            "vocabulary": rows("vocabulary"),
            "quiz_results": rows("quiz_results"),
            "story_progress": rows("story_progress"),
            "daily_login": rows("daily_login"),
            "weekly_challenges": rows("weekly_challenges"),
            "xp_log": rows("xp_log"),
            "chest_openings": rows("chest_openings"),
            "immersion_sessions": rows("immersion_sessions"),
            "town_tiles": rows("town_tiles"),
            "town_profile": rows("town_profile"),
        }
