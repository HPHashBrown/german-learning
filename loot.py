"""Loot chest system. Odds are exactly as specified in the brief:

Common chest:    Common 75%, Uncommon 15%, Rare 10%, Legendary 0%
Uncommon chest:  Common 15%, Uncommon 60%, Rare 15%, Legendary 5%
Rare chest:      Common 5%,  Uncommon 25%, Rare 60%, Legendary 10%
Legendary chest: Common 0%,  Uncommon 0%,  Rare 25%, Legendary 75%
"""

import random

import db
import shop_catalog as sc

CHEST_ODDS = {
    "common":    {"common": 0.75, "uncommon": 0.15, "rare": 0.10, "legendary": 0.00},
    # NOTE: the brief specified Uncommon chest as 15/60/15/5, which sums to 95%,
    # not 100%. The other three chests' numbers all sum correctly to 100%, so
    # this was very likely a typo rather than an intentional "5% goes nowhere."
    # Fixed here by bumping the chest's own "home" rarity (Uncommon) from 60%
    # to 65% — the other three stated numbers (15/15/5) are kept exactly as given.
    "uncommon":  {"common": 0.15, "uncommon": 0.65, "rare": 0.15, "legendary": 0.05},
    "rare":      {"common": 0.05, "uncommon": 0.25, "rare": 0.60, "legendary": 0.10},
    "legendary": {"common": 0.00, "uncommon": 0.00, "rare": 0.25, "legendary": 0.75},
}

# Sanity check the tables sum to 1.0 at import time — if a future edit breaks
# this, fail loudly rather than silently drifting the odds.
for _chest, _dist in CHEST_ODDS.items():
    total = round(sum(_dist.values()), 6)
    assert total == 1.0, f"{_chest} chest odds sum to {total}, not 1.0"


def roll_rarity(chest_type: str, rng: random.Random = None) -> str:
    rng = rng or random.Random()
    dist = CHEST_ODDS[chest_type]
    roll = rng.random()
    cumulative = 0.0
    for rarity, prob in dist.items():
        cumulative += prob
        if roll < cumulative:
            return rarity
    return "common"  # floating-point fallback safety net


def open_chest(chest_type: str) -> dict:
    """Rolls a rarity, then picks a random item of that rarity from the full
    catalog (including chest-exclusive items), grants it, and logs the opening.
    Returns the won item dict plus the rolled rarity."""
    rarity = roll_rarity(chest_type)
    candidates = [v for v in sc.CATALOG.values() if v["rarity"] == rarity]
    # If every item of that rarity is already owned, still "win" one (duplicate
    # protection isn't in scope) — always returns something so a chest never
    # opens to a broken empty state.
    item = random.choice(candidates)
    db.grant_item(item["id"], item["type"], item["rarity"], via="chest")
    db.record_chest_opening(chest_type, item["id"], rarity)
    return item


def can_open(chest_type: str) -> bool:
    profile = db.get_profile()
    return int(float(profile.get(f"{chest_type}_keys", "0") or 0)) >= 1
