"""Town Expansion system — persistence.

Uses the same SQLite database as the rest of the app (via db.get_conn), just
with its own tables, so there's still exactly one database file. Call
init_town_db() once at app startup alongside db.init_db().
"""

import datetime as dt

import db as maindb

TOWN_SCHEMA = """
CREATE TABLE IF NOT EXISTS town_tiles (
    world_id TEXT NOT NULL,
    x INTEGER NOT NULL,
    y INTEGER NOT NULL,
    locked INTEGER NOT NULL DEFAULT 1,
    terrain_id TEXT,
    building_id TEXT,
    building_level INTEGER DEFAULT 0,
    decoration_id TEXT,
    unlocked_at TEXT,
    PRIMARY KEY (world_id, x, y)
);

CREATE TABLE IF NOT EXISTS town_profile (
    key TEXT PRIMARY KEY,
    value TEXT
);
"""

TOWN_DEFAULT_PROFILE = {
    "current_world": "german_village",
}


def init_town_db():
    with maindb.get_conn() as conn:
        conn.executescript(TOWN_SCHEMA)
        cur = conn.execute("SELECT COUNT(*) c FROM town_profile")
        if cur.fetchone()["c"] == 0:
            for k, v in TOWN_DEFAULT_PROFILE.items():
                conn.execute("INSERT INTO town_profile (key, value) VALUES (?, ?)", (k, v))


def get_town_profile() -> dict:
    with maindb.get_conn() as conn:
        rows = conn.execute("SELECT key, value FROM town_profile").fetchall()
        return {r["key"]: r["value"] for r in rows}


def set_town_profile(key: str, value):
    with maindb.get_conn() as conn:
        conn.execute(
            "INSERT INTO town_profile (key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, str(value)),
        )


def ensure_world_tiles(world_id: str, grid_size: int):
    """Idempotent: creates the locked-tile grid for a world the first time it's touched."""
    with maindb.get_conn() as conn:
        cur = conn.execute("SELECT COUNT(*) c FROM town_tiles WHERE world_id = ?", (world_id,))
        if cur.fetchone()["c"] > 0:
            return
        for x in range(grid_size):
            for y in range(grid_size):
                conn.execute(
                    "INSERT INTO town_tiles (world_id, x, y, locked) VALUES (?, ?, ?, 1)",
                    (world_id, x, y),
                )


def unlock_starting_area(world_id: str, center_x: int, center_y: int, radius: int = 1):
    """Unlocks the initial N x N area (radius=1 -> 3x3) with no terrain assigned
    yet — starting tiles are free, so they skip the 'discover terrain via
    challenge' moment and just get a default terrain immediately."""
    import random
    with maindb.get_conn() as conn:
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                x, y = center_x + dx, center_y + dy
                row = conn.execute(
                    "SELECT locked FROM town_tiles WHERE world_id=? AND x=? AND y=?",
                    (world_id, x, y),
                ).fetchone()
                if row and row["locked"]:
                    terrain = random.Random(f"{world_id}-{x}-{y}").choice(["grassland", "meadow", "plains"])
                    conn.execute(
                        "UPDATE town_tiles SET locked=0, terrain_id=?, unlocked_at=? "
                        "WHERE world_id=? AND x=? AND y=?",
                        (terrain, dt.datetime.now().isoformat(), world_id, x, y),
                    )


def get_tiles(world_id: str):
    import pandas as pd
    with maindb.get_conn() as conn:
        return pd.read_sql_query(
            "SELECT * FROM town_tiles WHERE world_id = ? ORDER BY y, x", conn, params=(world_id,)
        )


def get_tile(world_id: str, x: int, y: int):
    with maindb.get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM town_tiles WHERE world_id=? AND x=? AND y=?", (world_id, x, y)
        ).fetchone()
        return dict(row) if row else None


def unlock_tile(world_id: str, x: int, y: int, terrain_id: str):
    with maindb.get_conn() as conn:
        conn.execute(
            "UPDATE town_tiles SET locked=0, terrain_id=?, unlocked_at=? "
            "WHERE world_id=? AND x=? AND y=?",
            (terrain_id, dt.datetime.now().isoformat(), world_id, x, y),
        )


def claimed_tile_count(world_id: str) -> int:
    """Tiles unlocked via a challenge (tracked directly, not inferred, to
    avoid any ambiguity with the free starting tiles)."""
    profile = get_town_profile()
    return int(float(profile.get(f"claimed_count_{world_id}", "0") or 0))


def increment_claimed_tile_count(world_id: str):
    count = claimed_tile_count(world_id) + 1
    set_town_profile(f"claimed_count_{world_id}", count)
    return count


def place_building(world_id: str, x: int, y: int, building_id: str):
    with maindb.get_conn() as conn:
        conn.execute(
            "UPDATE town_tiles SET building_id=?, building_level=1 "
            "WHERE world_id=? AND x=? AND y=?",
            (building_id, world_id, x, y),
        )


def remove_building(world_id: str, x: int, y: int):
    with maindb.get_conn() as conn:
        conn.execute(
            "UPDATE town_tiles SET building_id=NULL, building_level=0 "
            "WHERE world_id=? AND x=? AND y=?",
            (world_id, x, y),
        )


def upgrade_building(world_id: str, x: int, y: int, new_level: int):
    with maindb.get_conn() as conn:
        conn.execute(
            "UPDATE town_tiles SET building_level=? WHERE world_id=? AND x=? AND y=?",
            (new_level, world_id, x, y),
        )


def place_decoration(world_id: str, x: int, y: int, decoration_id: str):
    with maindb.get_conn() as conn:
        conn.execute(
            "UPDATE town_tiles SET decoration_id=? WHERE world_id=? AND x=? AND y=?",
            (decoration_id, world_id, x, y),
        )


def all_buildings_in_world(world_id: str):
    import pandas as pd
    with maindb.get_conn() as conn:
        return pd.read_sql_query(
            "SELECT * FROM town_tiles WHERE world_id=? AND building_id IS NOT NULL", conn, params=(world_id,)
        )


def export_town_data() -> dict:
    with maindb.get_conn() as conn:
        tiles = [dict(r) for r in conn.execute("SELECT * FROM town_tiles").fetchall()]
        profile = [dict(r) for r in conn.execute("SELECT * FROM town_profile").fetchall()]
    return {"town_tiles": tiles, "town_profile": profile}
