"""Town Expansion system — engine.

Pure game logic: no Streamlit, no direct UI concerns. Reads/writes through
town_db.py, reads definitions from town_config.py. This module is what
app.py's Town page calls into; it's also what tests exercise directly.
"""

import random

import town_config as cfg
import town_db as tdb


def grid_center(grid_size: int) -> int:
    return grid_size // 2


def get_or_create_world_grid(world_id: str):
    world = cfg.WORLDS[world_id]
    tdb.ensure_world_tiles(world_id, world.grid_size)
    center = grid_center(world.grid_size)
    tdb.unlock_starting_area(world_id, center, center, radius=1)
    return world


def is_adjacent_to_unlocked(world_id: str, x: int, y: int) -> bool:
    """Orthogonal adjacency only — no diagonals, per the brief."""
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        neighbor = tdb.get_tile(world_id, x + dx, y + dy)
        if neighbor and not neighbor["locked"]:
            return True
    return False


def claimable_tiles(world_id: str) -> list[dict]:
    """All currently-locked tiles that are adjacent to an unlocked tile —
    i.e. tiles the player is allowed to attempt to claim right now."""
    tiles = tdb.get_tiles(world_id)
    result = []
    for _, row in tiles.iterrows():
        if row["locked"] and is_adjacent_to_unlocked(world_id, row["x"], row["y"]):
            result.append(row.to_dict())
    return result


def pick_terrain_for_tile(world_id: str, x: int, y: int) -> str:
    world = cfg.WORLDS[world_id]
    ids = list(world.terrain_weights.keys())
    weights = list(world.terrain_weights.values())
    # Deterministic-per-tile so re-rendering the page never changes what a
    # not-yet-unlocked tile *would* reveal — but the player can't see this
    # value until they actually succeed, since the UI never reads terrain_id
    # for locked tiles.
    rng = random.Random(f"{world_id}-{x}-{y}-terrain")
    return rng.choices(ids, weights=weights, k=1)[0]


def current_tier(world_id: str) -> str:
    world = cfg.WORLDS[world_id]
    claimed = tdb.claimed_tile_count(world_id)
    return cfg.tier_for_claimed_count(claimed, world.difficulty_offset)


def claim_tile_success(world_id: str, x: int, y: int) -> dict:
    """Call after a challenge is passed. Unlocks the tile, assigns terrain,
    bumps the claimed counter. Returns the revealed terrain info."""
    terrain_id = pick_terrain_for_tile(world_id, x, y)
    tdb.unlock_tile(world_id, x, y, terrain_id)
    tdb.increment_claimed_tile_count(world_id)
    return {"terrain_id": terrain_id, "terrain": cfg.TERRAIN_TYPES[terrain_id]}


# ------------------------------------------------------------- Buildings ---
def can_build(world_id: str, x: int, y: int, building_id: str, player_level: int) -> tuple[bool, str]:
    tile = tdb.get_tile(world_id, x, y)
    if not tile:
        return False, "Tile does not exist."
    if tile["locked"]:
        return False, "Tile is still locked."
    if tile["building_id"]:
        return False, "Tile already has a building."
    building = cfg.BUILDINGS.get(building_id)
    if not building:
        return False, "Unknown building."
    if player_level < building.min_player_level:
        return False, f"Requires Player Level {building.min_player_level}."
    return True, ""


def effective_build_cost(world_id: str, building: cfg.Building) -> int:
    discount = total_construction_discount_pct(world_id)
    base = building.build_cost()
    return max(0, round(base * (1 - discount / 100)))


def effective_upgrade_cost(world_id: str, building: cfg.Building, current_level: int) -> int | None:
    base = building.upgrade_cost(current_level)
    if base is None:
        return None
    discount = total_upgrade_discount_pct(world_id)
    return max(0, round(base * (1 - discount / 100)))


def build(world_id: str, x: int, y: int, building_id: str, player_level: int) -> tuple[bool, str, int]:
    """Returns (success, message, coin_cost_charged). Caller is responsible
    for actually deducting coins from the player's wallet — this function
    only validates and, on success, writes the tile."""
    ok, reason = can_build(world_id, x, y, building_id, player_level)
    if not ok:
        return False, reason, 0
    building = cfg.BUILDINGS[building_id]
    cost = effective_build_cost(world_id, building)
    tdb.place_building(world_id, x, y, building_id)
    return True, f"Built {building.name}!", cost


def can_upgrade(world_id: str, x: int, y: int, player_level: int) -> tuple[bool, str, int | None]:
    tile = tdb.get_tile(world_id, x, y)
    if not tile or not tile["building_id"]:
        return False, "No building here.", None
    building = cfg.BUILDINGS.get(tile["building_id"])
    if building is None:
        return False, "Unknown building type (data mismatch) — clear and rebuild this tile.", None
    current_level = tile["building_level"]
    cost = effective_upgrade_cost(world_id, building, current_level)
    if cost is None:
        return False, "Already at max level.", None
    next_level_req = building.levels[current_level].min_player_level if current_level < len(building.levels) else 1
    if player_level < next_level_req:
        return False, f"Requires Player Level {next_level_req}.", None
    return True, "", cost


def upgrade(world_id: str, x: int, y: int, player_level: int) -> tuple[bool, str, int]:
    ok, reason, cost = can_upgrade(world_id, x, y, player_level)
    if not ok:
        return False, reason, 0
    tile = tdb.get_tile(world_id, x, y)
    new_level = tile["building_level"] + 1
    tdb.upgrade_building(world_id, x, y, new_level)
    building = cfg.BUILDINGS.get(tile["building_id"])
    building_name = building.name if building else tile["building_id"]
    return True, f"{building_name} upgraded to level {new_level}!", cost


# --------------------------------------------------------- Coin bonuses ----
def _sum_effect(world_id: str, effect_type: str) -> float:
    df = tdb.all_buildings_in_world(world_id)
    if df.empty:
        return 0.0
    total = 0.0
    for _, row in df.iterrows():
        building = cfg.BUILDINGS.get(row["building_id"])
        if building and building.effect_type == effect_type:
            total += building.effect_at(int(row["building_level"]))
    return total


def total_flat_coin_bonus(world_id: str) -> int:
    return round(_sum_effect(world_id, "coin_flat"))


def total_pct_coin_bonus(world_id: str) -> float:
    return _sum_effect(world_id, "coin_pct")


def total_construction_discount_pct(world_id: str) -> float:
    return min(75.0, _sum_effect(world_id, "construction_discount_pct"))


def total_upgrade_discount_pct(world_id: str) -> float:
    return min(75.0, _sum_effect(world_id, "upgrade_discount_pct"))


def total_daily_reward_bonus_pct(world_id: str) -> float:
    return _sum_effect(world_id, "daily_reward_bonus_pct")


def compute_coin_bonus(world_id: str, base_coins: int) -> dict:
    """Applies flat building bonuses, then percentage building bonuses, then
    the world-wide multiplier — matching the brief's worked example order
    (base -> flat building bonus -> % building bonus -> world bonus)."""
    world = cfg.WORLDS[world_id]
    flat = total_flat_coin_bonus(world_id)
    pct = total_pct_coin_bonus(world_id)

    after_flat = base_coins + flat
    after_pct = after_flat * (1 + pct / 100)
    world_bonus_pct = (world.coin_reward_multiplier - 1) * 100
    final = after_pct * world.coin_reward_multiplier

    return {
        "base": base_coins,
        "flat_bonus": flat,
        "pct_bonus": pct,
        "world_bonus_pct": round(world_bonus_pct, 1),
        "final": round(final),
    }


# ------------------------------------------------------------ Content -----
def unlocked_content_keys(world_id: str) -> set[str]:
    df = tdb.all_buildings_in_world(world_id)
    keys = set()
    if df.empty:
        return keys
    for _, row in df.iterrows():
        building = cfg.BUILDINGS.get(row["building_id"])
        if building and building.effect_type == "content_unlock" and building.unlock_content_key:
            keys.add(building.unlock_content_key)
    return keys


# -------------------------------------------------------- World progress ---
def world_completion_pct(world_id: str) -> float:
    tiles = tdb.get_tiles(world_id)
    if tiles.empty:
        return 0.0
    unlocked = (tiles["locked"] == 0).sum()
    return round(100 * unlocked / len(tiles), 1)


def is_world_complete(world_id: str) -> bool:
    return world_completion_pct(world_id) >= 100.0
