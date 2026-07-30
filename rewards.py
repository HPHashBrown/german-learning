"""Daily login rewards (procedurally generated up to day 200, with variety and
milestone spikes) and weekly challenge definitions."""

import random

MILESTONE_DAYS = {
    3: {"type": "xp", "amount": 50, "label": "+50 XP"},
    7: {"type": "chest", "chest": "uncommon", "label": "Bonus Chest (Uncommon)"},
    14: {"type": "theme", "item": "sakura", "label": "Rare Theme: Sakura"},
    21: {"type": "chest", "chest": "rare", "label": "Bonus Chest (Rare)"},
    25: {"type": "coins", "amount": 300, "label": "+300 Coins"},
    30: {"type": "title", "item": "Dedicated Learner", "label": "Exclusive Title: Dedicated Learner"},
    50: {"type": "chest", "chest": "rare", "label": "Bonus Chest (Rare)"},
    75: {"type": "coins", "amount": 750, "label": "+750 Coins"},
    100: {"type": "legend_status", "label": "Legend Status + Legendary Chest"},
    125: {"type": "chest", "chest": "legendary", "label": "Bonus Chest (Legendary)"},
    150: {"type": "pet", "item": "dragon", "label": "Legendary Pet: Tiny Dragon"},
    175: {"type": "xp", "amount": 1000, "label": "+1000 XP"},
    200: {"type": "legend_status_2", "label": "Grandmaster Status + Legendary Chest"},
}

DAILY_POOL = [
    {"type": "coins", "amount": 20, "label": "+20 Coins"},
    {"type": "coins", "amount": 35, "label": "+35 Coins"},
    {"type": "xp", "amount": 15, "label": "+15 XP"},
    {"type": "xp", "amount": 25, "label": "+25 XP"},
    {"type": "xp_boost", "label": "2x XP Boost (next session)"},
    {"type": "key", "key": "common", "label": "1x Common Key"},
]

WEEK_END_BONUS = {"type": "chest", "chest": "common", "label": "Weekly Bonus Chest (Common)"}


def reward_for_day(day_number: int) -> dict:
    """day_number = consecutive login day count (1-indexed). Deterministic per day
    number so refreshing doesn't reroll today's reward, but varies day to day."""
    if day_number in MILESTONE_DAYS:
        return dict(MILESTONE_DAYS[day_number])
    if day_number % 7 == 0:
        return dict(WEEK_END_BONUS)
    rng = random.Random(day_number * 9973 + 17)
    return dict(rng.choice(DAILY_POOL))


WEEKLY_CHALLENGE_POOL = [
    {"key": "earn_xp", "label": "Earn 2000 XP", "target": 2000, "unit": "XP",
     "reward_xp": 500, "reward_coins": 200},
    {"key": "finish_stories", "label": "Finish 5 stories", "target": 5, "unit": "stories",
     "reward_xp": 300, "reward_coins": 150},
    {"key": "master_words", "label": "Master 50 words", "target": 50, "unit": "words",
     "reward_xp": 400, "reward_coins": 150},
    {"key": "complete_quizzes", "label": "Complete 20 quizzes", "target": 20, "unit": "quizzes",
     "reward_xp": 350, "reward_coins": 150},
]


def challenges_for_week(week_start_str: str, count: int = 3):
    import hashlib
    seed = int(hashlib.md5(week_start_str.encode()).hexdigest(), 16) % (2**31)
    rng = random.Random(seed)
    pool = WEEKLY_CHALLENGE_POOL.copy()
    rng.shuffle(pool)
    return pool[:count]
