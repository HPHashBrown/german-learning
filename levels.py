"""XP leveling curve and the content-unlock map tied to levels."""

# Level thresholds: cumulative XP required to REACH that level.
# Curve: progressively steeper (roughly quadratic) as requested in the brief.
LEVEL_THRESHOLDS = {1: 0, 2: 250, 3: 600, 4: 1100}
_lvl = 4
_xp = 1100
_step = 700
while _lvl < 50:
    _lvl += 1
    _step += 120
    _xp += _step
    LEVEL_THRESHOLDS[_lvl] = _xp

MAX_LEVEL = max(LEVEL_THRESHOLDS)

UNLOCKS = {
    1: ["Greetings", "Numbers", "Colors", "Basic Vocabulary"],
    2: ["Restaurant Vocabulary", "AI Chat", "Daily Challenges"],
    3: ["Reading Stories", "Pronunciation Practice"],
    5: ["Travel German"],
    7: ["Verb Trainer"],
    10: ["Intermediate Grammar"],
    15: ["Listening Practice"],
    20: ["AI Roleplay"],
    30: ["Business German"],
    40: ["Native Stories"],
    50: ["Master Challenges"],
}


def level_for_xp(xp: int) -> int:
    lvl = 1
    for level, threshold in sorted(LEVEL_THRESHOLDS.items()):
        if xp >= threshold:
            lvl = level
        else:
            break
    return min(lvl, MAX_LEVEL)


def xp_for_level(level: int) -> int:
    return LEVEL_THRESHOLDS.get(level, LEVEL_THRESHOLDS[MAX_LEVEL])


def xp_progress(xp: int):
    """Returns (current_level, xp_into_level, xp_needed_for_level, pct_complete, next_level_or_None)."""
    lvl = level_for_xp(xp)
    cur_threshold = xp_for_level(lvl)
    if lvl >= MAX_LEVEL:
        return lvl, 0, 0, 1.0, None
    next_threshold = xp_for_level(lvl + 1)
    span = next_threshold - cur_threshold
    into = xp - cur_threshold
    pct = max(0.0, min(1.0, into / span)) if span else 1.0
    return lvl, into, span, pct, lvl + 1


def unlocked_features(level: int) -> list:
    features = []
    for lvl, feats in UNLOCKS.items():
        if level >= lvl:
            features.extend(feats)
    return features


def next_unlock(level: int):
    """Returns (feature_name, level_required, xp_needed) for the next thing to unlock, or None."""
    upcoming = sorted((lvl, feats) for lvl, feats in UNLOCKS.items() if lvl > level)
    if not upcoming:
        return None
    lvl, feats = upcoming[0]
    return feats[0], lvl, xp_for_level(lvl)


def is_unlocked(feature_name: str, level: int) -> bool:
    return feature_name in unlocked_features(level)
