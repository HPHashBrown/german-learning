"""Town Expansion system — configuration.

Everything here is data: terrain types, buildings, worlds, and challenge
difficulty tiers. Adding a new building or terrain type means adding an
entry to a dict below — no engine code changes required. `town_engine.py`
reads these structures; it never hardcodes a building/terrain/world name.
"""

from dataclasses import dataclass, field


# ------------------------------------------------------------- Terrain -----
@dataclass(frozen=True)
class Terrain:
    id: str
    name: str
    emoji: str
    # Data-driven hook for future terrain-specific buildings (e.g. Water Mill
    # requires 'river'). Not enforced yet — buildings just declare a
    # `preferred_terrain` they get a bonus on, engine ignores it until a
    # future update wants to use it. Present now so no redesign is needed later.


TERRAIN_TYPES: dict[str, Terrain] = {
    t.id: t for t in [
        Terrain("forest", "Forest", "🌲"),
        Terrain("grassland", "Grassland", "🌾"),
        Terrain("meadow", "Meadow", "🌼"),
        Terrain("rocky", "Rocky Ground", "🪨"),
        Terrain("river", "River", "🌊"),
        Terrain("sandy", "Sandy Ground", "🏖"),
        Terrain("dense_woods", "Dense Woods", "🌳"),
        Terrain("autumn_forest", "Autumn Forest", "🍂"),
        Terrain("plains", "Plains", "🌿"),
        Terrain("flower_field", "Flower Field", "🌸"),
    ]
}


# ------------------------------------------------------------- Buildings ---
@dataclass(frozen=True)
class BuildingLevel:
    coin_cost: int
    effect_value: float          # meaning depends on effect_type (see Building)
    min_player_level: int = 1
    emoji_override: str = ""     # if set, building shows this emoji once it reaches this level


@dataclass(frozen=True)
class Building:
    id: str
    name: str
    category: str                # residential, commercial, educational, cultural, utility
    emoji: str
    min_player_level: int
    levels: tuple[BuildingLevel, ...]
    effect_type: str             # see EFFECT_TYPES below
    description: str = ""
    preferred_terrain: str = ""  # optional: building's effect gets a bonus when built on this terrain
    required_terrain: str = ""   # optional: building can ONLY be built on this terrain (hard gate)
    unlock_content_key: str = "" # for cultural buildings; read by app.py to gate content

    @property
    def max_level(self) -> int:
        return len(self.levels)

    def build_cost(self) -> int:
        return self.levels[0].coin_cost

    def upgrade_cost(self, current_level: int) -> int | None:
        """Cost to go from current_level -> current_level+1, or None if maxed."""
        if current_level >= self.max_level:
            return None
        return self.levels[current_level].coin_cost

    def effect_at(self, level: int) -> float:
        """level is 1-indexed (a freshly built level-1 building already has an effect)."""
        if level < 1:
            return 0.0
        idx = min(level, self.max_level) - 1
        return self.levels[idx].effect_value

    def visual_emoji(self, level: int) -> str:
        """Returns the emoji this building shows at the given level — walks
        backward from the current level to find the most recent tier that
        defined an emoji_override, falling back to the base emoji if none did."""
        if level < 1:
            return self.emoji
        idx = min(level, self.max_level) - 1
        for i in range(idx, -1, -1):
            if self.levels[i].emoji_override:
                return self.levels[i].emoji_override
        return self.emoji


# Effect types:
#   "coin_flat"        — flat coins added to every lesson/immersion reward
#   "coin_pct"         — percentage bonus applied to the lesson reward
#   "upgrade_discount_pct" — reduces OTHER buildings' upgrade costs (utility)
#   "construction_discount_pct" — reduces OTHER buildings' build costs (utility)
#   "storage"          — increases total building capacity (# of tiles that may hold buildings) — reserved for future use
#   "daily_reward_bonus_pct" — increases daily login reward coin amounts (utility)
#   "content_unlock"   — cultural buildings; effect_value unused, unlock_content_key matters
#   "none"             — residential / decorations: no mechanical effect

BUILDINGS: dict[str, Building] = {}


def _add_building(b: Building):
    BUILDINGS[b.id] = b


# Residential — no XP, no coin effect, purely town development.
_add_building(Building(
    id="house", name="House", category="residential", emoji="🏠", min_player_level=1,
    levels=(
        BuildingLevel(coin_cost=50, effect_value=0),
        BuildingLevel(coin_cost=120, effect_value=0),
        BuildingLevel(coin_cost=250, effect_value=0, emoji_override="🏡"),
        BuildingLevel(coin_cost=450, effect_value=0),
        BuildingLevel(coin_cost=700, effect_value=0, emoji_override="🏘️"),
    ),
    effect_type="none", description="Basic housing. Grows your town's population feel — "
                                     "visibly evolves as it levels up.",
))
_add_building(Building(
    id="apartment", name="Apartment", category="residential", emoji="🏢", min_player_level=5,
    levels=tuple(BuildingLevel(coin_cost=c, effect_value=0) for c in [150, 300, 550, 900]),
    effect_type="none", description="Denser housing for a growing town.",
))
_add_building(Building(
    id="villa", name="Villa", category="residential", emoji="🏡", min_player_level=15,
    levels=tuple(BuildingLevel(coin_cost=c, effect_value=0) for c in [400, 800, 1400]),
    effect_type="none", description="An upscale residence.",
))
_add_building(Building(
    id="neighborhood", name="Neighborhood", category="residential", emoji="🏘️", min_player_level=25,
    levels=tuple(BuildingLevel(coin_cost=c, effect_value=0) for c in [900, 1600, 2600]),
    effect_type="none", description="A whole cluster of homes.",
))

# Commercial — boosts lesson coin rewards. Never passive income.
_add_building(Building(
    id="bakery", name="Bakery", category="commercial", emoji="🥐", min_player_level=1,
    levels=(
        BuildingLevel(coin_cost=80, effect_value=10),
        BuildingLevel(coin_cost=160, effect_value=20),
        BuildingLevel(coin_cost=300, effect_value=35, emoji_override="🍞"),
        BuildingLevel(coin_cost=500, effect_value=55),
        BuildingLevel(coin_cost=800, effect_value=80, emoji_override="🏪"),
    ),
    effect_type="coin_flat", description="+coins per completed lesson. Evolves visually as it levels up.",
))
_add_building(Building(
    id="cafe", name="Café", category="commercial", emoji="☕", min_player_level=5,
    levels=tuple(BuildingLevel(coin_cost=c, effect_value=v) for c, v in
                 [(150, 3), (300, 5), (550, 8), (900, 12)]),
    effect_type="coin_pct", description="+% bonus on lesson coin rewards.",
))
_add_building(Building(
    id="restaurant", name="Restaurant", category="commercial", emoji="🍽️", min_player_level=10,
    levels=tuple(BuildingLevel(coin_cost=c, effect_value=v) for c, v in
                 [(400, 30), (700, 55), (1100, 90)]),
    effect_type="coin_flat", description="+coins per completed lesson.",
))
_add_building(Building(
    id="market", name="Market", category="commercial", emoji="🏪", min_player_level=15,
    levels=tuple(BuildingLevel(coin_cost=c, effect_value=v) for c, v in
                 [(600, 6), (1000, 10), (1600, 15)]),
    effect_type="coin_pct", description="+% bonus on lesson coin rewards.",
))
_add_building(Building(
    id="bank", name="Bank", category="commercial", emoji="🏦", min_player_level=20,
    levels=tuple(BuildingLevel(coin_cost=c, effect_value=v) for c, v in
                 [(1200, 8), (2000, 14), (3200, 20)]),
    effect_type="coin_pct", description="+% bonus on lesson coin rewards.",
))
_add_building(Building(
    id="shopping_center", name="Shopping Center", category="commercial", emoji="🛍️", min_player_level=30,
    levels=tuple(BuildingLevel(coin_cost=c, effect_value=v) for c, v in
                 [(2500, 60), (4000, 100)]),
    effect_type="coin_flat", description="+coins per completed lesson.",
))

# Educational — supports learning rewards (still coin-side; XP itself never
# comes from buildings, only from actually completing lessons/challenges).
_add_building(Building(
    id="library", name="Library", category="educational", emoji="📚", min_player_level=5,
    levels=(
        BuildingLevel(coin_cost=200, effect_value=5),
        BuildingLevel(coin_cost=400, effect_value=8),
        BuildingLevel(coin_cost=700, effect_value=12, emoji_override="🏛️"),
        BuildingLevel(coin_cost=1100, effect_value=18),
    ),
    effect_type="coin_pct", description="+% bonus on lesson coin rewards. Evolves visually as it levels up.",
))
_add_building(Building(
    id="school", name="School", category="educational", emoji="🏫", min_player_level=10,
    levels=tuple(BuildingLevel(coin_cost=c, effect_value=v) for c, v in
                 [(500, 40), (900, 70), (1400, 110)]),
    effect_type="coin_flat", description="+coins per completed lesson.",
))
_add_building(Building(
    id="university", name="University", category="educational", emoji="🎓", min_player_level=20,
    levels=tuple(BuildingLevel(coin_cost=c, effect_value=v) for c, v in
                 [(1500, 10), (2400, 16), (3600, 22)]),
    effect_type="coin_pct", description="+% bonus on lesson coin rewards.",
))
_add_building(Building(
    id="language_institute", name="Language Institute", category="educational", emoji="🗣️", min_player_level=25,
    levels=tuple(BuildingLevel(coin_cost=c, effect_value=v) for c, v in
                 [(1800, 15), (2800, 22)]),
    effect_type="coin_pct", description="+% bonus on lesson coin rewards.",
))

# Cultural — unlock content, not coins.
_add_building(Building(
    id="museum", name="Museum", category="cultural", emoji="🏛️", min_player_level=15,
    levels=(BuildingLevel(coin_cost=700, effect_value=0),),
    effect_type="content_unlock", unlock_content_key="german_history",
    description="Unlocks German history reading content.",
))
_add_building(Building(
    id="opera_house", name="Opera House", category="cultural", emoji="🎭", min_player_level=20,
    levels=(BuildingLevel(coin_cost=1400, effect_value=0),),
    effect_type="content_unlock", unlock_content_key="special_ai_conversations",
    description="Unlocks special AI conversation scenarios.",
))
_add_building(Building(
    id="town_hall", name="Town Hall", category="cultural", emoji="🏛️", min_player_level=10,
    levels=(BuildingLevel(coin_cost=900, effect_value=0),),
    effect_type="content_unlock", unlock_content_key="town_achievements",
    description="Unlocks unique town-building achievements.",
))
_add_building(Building(
    id="castle", name="Castle", category="cultural", emoji="🏰", min_player_level=30,
    levels=(BuildingLevel(coin_cost=3000, effect_value=0),),
    effect_type="content_unlock", unlock_content_key="advanced_stories",
    description="Unlocks the hardest reading stories.",
))

# Terrain-tied buildings — per the brief's own examples. "Requires" terrain
# is a hard build gate; "performs better on" is a soft bonus (preferred_terrain).
_add_building(Building(
    id="water_mill", name="Water Mill", category="commercial", emoji="💧", min_player_level=8,
    levels=tuple(BuildingLevel(coin_cost=c, effect_value=v) for c, v in
                 [(350, 25), (600, 45), (950, 70)]),
    effect_type="coin_flat", required_terrain="river",
    description="+coins per completed lesson. Can only be built on River terrain.",
))
_add_building(Building(
    id="farm", name="Farm", category="commercial", emoji="🌻", min_player_level=3,
    levels=(
        BuildingLevel(coin_cost=120, effect_value=12),
        BuildingLevel(coin_cost=240, effect_value=22, emoji_override="🌾"),
        BuildingLevel(coin_cost=420, effect_value=38),
        BuildingLevel(coin_cost=650, effect_value=58, emoji_override="🚜"),
    ),
    effect_type="coin_flat", preferred_terrain="grassland",
    description="+coins per completed lesson. Effect is boosted 50% when built on Grassland. "
                "Evolves visually as it levels up.",
))
_add_building(Building(
    id="lumber_mill", name="Lumber Mill", category="utility", emoji="🪵", min_player_level=8,
    levels=tuple(BuildingLevel(coin_cost=c, effect_value=v) for c, v in
                 [(300, 4), (550, 7), (850, 10)]),
    effect_type="construction_discount_pct", required_terrain="forest",
    description="Reduces building costs town-wide. Can only be built on Forest terrain.",
))
_add_building(Building(
    id="stone_quarry", name="Stone Quarry", category="utility", emoji="⛏️", min_player_level=8,
    levels=tuple(BuildingLevel(coin_cost=c, effect_value=v) for c, v in
                 [(350, 4), (600, 7)]),
    effect_type="upgrade_discount_pct", required_terrain="rocky",
    description="Reduces upgrade costs town-wide. Can only be built on Rocky Ground.",
))

# Utility — global, non-adjacency bonuses per the brief.
_add_building(Building(
    id="road", name="Road", category="utility", emoji="🛣️", min_player_level=1,
    levels=tuple(BuildingLevel(coin_cost=c, effect_value=v) for c, v in
                 [(40, 2), (90, 4), (160, 6)]),
    effect_type="construction_discount_pct", description="Reduces building costs town-wide.",
))
_add_building(Building(
    id="bridge", name="Bridge", category="utility", emoji="🌉", min_player_level=5,
    levels=tuple(BuildingLevel(coin_cost=c, effect_value=v) for c, v in
                 [(300, 5), (500, 9)]),
    effect_type="construction_discount_pct", description="Reduces building costs town-wide.",
))
_add_building(Building(
    id="town_square", name="Town Square", category="utility", emoji="🎪", min_player_level=10,
    levels=tuple(BuildingLevel(coin_cost=c, effect_value=v) for c, v in
                 [(600, 5), (1000, 10)]),
    effect_type="daily_reward_bonus_pct", description="Boosts daily login reward coins.",
))
_add_building(Building(
    id="clock_tower", name="Clock Tower", category="utility", emoji="🕰️", min_player_level=15,
    levels=(BuildingLevel(coin_cost=1100, effect_value=10),),
    effect_type="upgrade_discount_pct", description="Reduces upgrade costs town-wide.",
))
_add_building(Building(
    id="storage_building", name="Storage Building", category="utility", emoji="📦", min_player_level=5,
    levels=tuple(BuildingLevel(coin_cost=c, effect_value=v) for c, v in
                 [(250, 5), (450, 10)]),
    effect_type="storage", description="Increases building capacity (reserved for future use).",
))

# Decorations — cosmetic only, own category so they never affect coin math.
for _iid, _name, _emoji, _lvl, _cost in [
    ("tree", "Tree", "🌳", 1, 20), ("flower", "Flowers", "🌷", 1, 15),
    ("bench", "Bench", "🪑", 1, 25), ("street_lamp", "Street Lamp", "💡", 3, 40),
    ("fountain", "Fountain", "⛲", 8, 150), ("statue", "Statue", "🗿", 12, 300),
    ("flag", "Flag", "🚩", 1, 10),
]:
    _add_building(Building(
        id=f"deco_{_iid}", name=_name, category="decoration", emoji=_emoji,
        min_player_level=_lvl, levels=(BuildingLevel(coin_cost=_cost, effect_value=0),),
        effect_type="none", description="Purely cosmetic.",
    ))


def buildings_by_category(category: str):
    return [b for b in BUILDINGS.values() if b.category == category]


def available_buildings(player_level: int):
    return [b for b in BUILDINGS.values() if b.min_player_level <= player_level]


def locked_buildings(player_level: int):
    """Buildings the player hasn't reached the level for yet, sorted by how
    soon they unlock — used to show players what's coming."""
    locked = [b for b in BUILDINGS.values() if b.min_player_level > player_level]
    return sorted(locked, key=lambda b: (b.min_player_level, b.category, b.name))


# --------------------------------------------------------------- Worlds ----
@dataclass(frozen=True)
class World:
    id: str
    name: str
    flag: str
    order: int
    grid_size: int                 # square grid, grid_size x grid_size
    terrain_weights: dict[str, float]
    difficulty_offset: int         # shifts the tile-count difficulty tier up (0=none)
    coin_reward_multiplier: float  # world-wide multiplier applied on top of buildings


WORLDS: dict[str, World] = {
    w.id: w for w in [
        World("german_village", "German Village", "🇩🇪", 0, 7,
              {"grassland": 0.3, "meadow": 0.25, "forest": 0.2, "plains": 0.15, "flower_field": 0.1},
              difficulty_offset=0, coin_reward_multiplier=1.0),
        World("berlin", "Berlin", "🇩🇪", 1, 9,
              {"plains": 0.3, "grassland": 0.25, "river": 0.2, "sandy": 0.15, "rocky": 0.1},
              difficulty_offset=1, coin_reward_multiplier=1.15),
        World("vienna", "Vienna", "🇦🇹", 2, 9,
              {"meadow": 0.3, "forest": 0.25, "flower_field": 0.2, "dense_woods": 0.15, "river": 0.1},
              difficulty_offset=2, coin_reward_multiplier=1.3),
        World("zurich", "Zurich", "🇨🇭", 3, 11,
              {"rocky": 0.3, "river": 0.25, "dense_woods": 0.2, "meadow": 0.15, "autumn_forest": 0.1},
              difficulty_offset=3, coin_reward_multiplier=1.5),
        World("european_tour", "European Tour", "🌍", 4, 11,
              {"autumn_forest": 0.2, "flower_field": 0.2, "plains": 0.2, "river": 0.2, "rocky": 0.2},
              difficulty_offset=4, coin_reward_multiplier=1.75),
        World("world_tour", "World Tour", "🌎", 5, 13,
              {t: 1 / len(TERRAIN_TYPES) for t in TERRAIN_TYPES},
              difficulty_offset=5, coin_reward_multiplier=2.0),
    ]
}

WORLD_ORDER = [w.id for w in sorted(WORLDS.values(), key=lambda w: w.order)]


def next_world_id(current_world_id: str) -> str | None:
    idx = WORLD_ORDER.index(current_world_id)
    if idx + 1 < len(WORLD_ORDER):
        return WORLD_ORDER[idx + 1]
    return None


# ----------------------------------------------------- Challenge Tiers -----
# (claimed_tiles_lower_bound, claimed_tiles_upper_bound_exclusive, tier_name)
# "claimed" excludes the free starting 3x3 — only tiles unlocked via a
# successful challenge count toward these thresholds.
CHALLENGE_TIERS = [
    (0, 10, "easy"),
    (10, 30, "medium"),
    (30, 60, "hard"),
]
CHALLENGE_TIER_LATE = "advanced"

TIER_ORDER = ["easy", "medium", "hard", "advanced"]

TIER_PASS_THRESHOLD = {"easy": 0.6, "medium": 0.7, "hard": 0.8, "advanced": 0.9}
TIER_QUESTION_COUNT = {"easy": 5, "medium": 5, "hard": 5, "advanced": 6}

# Multiplier applied to a building's effect when it sits on its preferred_terrain.
PREFERRED_TERRAIN_BONUS_MULT = 1.5

# Relocating a building costs this fraction of its current build cost.
MOVE_COST_PCT = 0.5


def tier_for_claimed_count(claimed_count: int, world_difficulty_offset: int = 0) -> str:
    base_tier = CHALLENGE_TIER_LATE
    for lo, hi, name in CHALLENGE_TIERS:
        if lo <= claimed_count < hi:
            base_tier = name
            break
    idx = min(len(TIER_ORDER) - 1, TIER_ORDER.index(base_tier) + world_difficulty_offset)
    return TIER_ORDER[idx]
