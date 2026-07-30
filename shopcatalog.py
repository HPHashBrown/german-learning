"""The full cosmetics catalog: themes, avatar parts, pets, titles, decorations,
XP effects. Every item has a rarity, which drives price and chest odds."""

RARITY_PRICES = {"common": 150, "uncommon": 350, "rare": 800, "legendary": 2500}
RARITY_COLORS = {"common": "#9aa5b1", "uncommon": "#3ecf8e", "rare": "#3e8ef7", "legendary": "#f7b32e"}
KEY_PRICES = {"common": 100, "uncommon": 250, "rare": 600, "legendary": 1800}

# item_id -> dict(name, type, rarity, emoji/preview, css)
CATALOG = {}


def _add(item_id, name, item_type, rarity, emoji, css=None, chest_only=False):
    CATALOG[item_id] = dict(
        id=item_id, name=name, type=item_type, rarity=rarity, emoji=emoji,
        price=RARITY_PRICES[rarity], css=css or {}, chest_only=chest_only,
    )


# --------------------------------------------------------------- Themes ----
_add("light", "Light", "theme", "common", "☀️", {"bg": "linear-gradient(135deg,#f8fafc,#e2e8f0)", "text": "#1a1a1a", "accent": "#4f46e5"})
_add("dark", "Dark", "theme", "common", "🌙", {"bg": "linear-gradient(135deg,#0f172a,#1e293b)", "text": "#f1f5f9", "accent": "#818cf8"})
_add("midnight", "Midnight", "theme", "common", "🌌", {"bg": "linear-gradient(135deg,#000000,#0a0a1a)", "text": "#e0e0ff", "accent": "#6366f1"})
_add("forest", "Forest", "theme", "common", "🌲", {"bg": "linear-gradient(135deg,#0b2818,#1a4a2e)", "text": "#eafff0", "accent": "#4ade80"})
_add("ocean", "Ocean", "theme", "common", "🌊", {"bg": "linear-gradient(135deg,#012a4a,#0466a3)", "text": "#e0f7ff", "accent": "#38bdf8"})

_add("cyberpunk", "Cyberpunk", "theme", "rare", "🤖", {"bg": "linear-gradient(135deg,#0d0221,#240046,#3c096c)", "text": "#f5f3ff", "accent": "#ff2fd0"})
_add("sakura", "Sakura", "theme", "rare", "🌸", {"bg": "linear-gradient(135deg,#ffe3ec,#ffc2d9,#ff8fb3)", "text": "#4a0e2b", "accent": "#e8437a"})
_add("vaporwave", "Vaporwave", "theme", "rare", "🌴", {"bg": "linear-gradient(135deg,#2b0a3d,#6a0f9e,#ff6ec7)", "text": "#fdf4ff", "accent": "#00e5ff"})
_add("medieval", "Medieval", "theme", "rare", "🏰", {"bg": "linear-gradient(135deg,#2b1d0e,#4a3218,#6b4423)", "text": "#f0e6d2", "accent": "#c9a15a"})
_add("pixel_art", "Pixel Art", "theme", "rare", "👾", {"bg": "linear-gradient(135deg,#1a1a2e,#16213e,#0f3460)", "text": "#e6e6e6", "accent": "#e94560"})
_add("northern_lights", "Northern Lights", "theme", "rare", "🌠", {"bg": "linear-gradient(135deg,#02111b,#0e4749,#1a936f)", "text": "#eafff5", "accent": "#88d498"})

_add("space_station", "Space Station", "theme", "legendary", "🛰️", {"bg": "linear-gradient(135deg,#000000,#0a0e1a,#1b2735)", "text": "#ffffff", "accent": "#00d4ff"})
_add("ancient_germany", "Ancient Germania", "theme", "legendary", "🪓", {"bg": "linear-gradient(135deg,#1a1005,#3d2817,#5c3d24)", "text": "#f5e6c8", "accent": "#c0a062"})
_add("castle_library", "Castle Library", "theme", "legendary", "🕯️", {"bg": "linear-gradient(135deg,#1a1310,#2e2117,#1a1310)", "text": "#f2e6d0", "accent": "#d4af37"})
_add("neon_city", "Neon City", "theme", "legendary", "🌆", {"bg": "linear-gradient(135deg,#0f0c29,#302b63,#24243e)", "text": "#f5f3ff", "accent": "#ff2fd0"})
_add("viking_hall", "Viking Hall", "theme", "legendary", "⚔️", {"bg": "linear-gradient(135deg,#0a1420,#1a2634,#2c3e50)", "text": "#e8eef3", "accent": "#a8b8c8"})

# --------------------------------------------------------- Seasonal (shop) --
_add("halloween", "Halloween", "theme", "rare", "🎃", {"bg": "linear-gradient(135deg,#1a0f00,#3d1f00,#e8730a)", "text": "#ffe8c9", "accent": "#ff7518"}, chest_only=False)
_add("christmas", "Christmas", "theme", "rare", "🎄", {"bg": "linear-gradient(135deg,#0d1b2a,#1b3a4b,#3a0d17)", "text": "#fff8f0", "accent": "#ff5a5f"})
_add("oktoberfest", "Oktoberfest", "theme", "rare", "🍺", {"bg": "linear-gradient(135deg,#2b1a00,#5c3a00,#a06a1a)", "text": "#fff3d6", "accent": "#f2c14e"})
_add("summer", "Summer", "theme", "rare", "☀️", {"bg": "linear-gradient(135deg,#fff2c9,#ffd97a,#ff9a3c)", "text": "#3a2400", "accent": "#ff6a3c"})
_add("valentines", "Valentine's", "theme", "rare", "💘", {"bg": "linear-gradient(135deg,#3a0d1f,#7a1638,#c92a5e)", "text": "#ffe6ee", "accent": "#ff4d6d"})

# --------------------------------------------------------------- Pets ------
_add("dachshund", "Dachshund", "pet", "common", "🐶")
_add("black_cat", "Black Cat", "pet", "common", "🐱")
_add("fox", "Fox", "pet", "uncommon", "🦊")
_add("frog", "Frog", "pet", "uncommon", "🐸")
_add("bee", "Bee", "pet", "uncommon", "🐝")
_add("owl", "Owl", "pet", "rare", "🦉")
_add("penguin", "Penguin", "pet", "rare", "🐧")
_add("panda", "Panda", "pet", "rare", "🐼")
_add("dragon", "Tiny Dragon", "pet", "legendary", "🐉")
_add("unicorn", "Unicorn", "pet", "legendary", "🦄")
_add("phoenix", "Phoenix", "pet", "legendary", "🔥🐦", chest_only=True)

# ---------------------------------------------------------- Avatar parts ---
for iid, name, rarity, emoji in [
    ("hair_short", "Short Hair", "common", "💇"), ("hair_long", "Long Hair", "common", "💁"),
    ("hair_curly", "Curly Hair", "uncommon", "🦱"), ("hair_rainbow", "Rainbow Hair", "rare", "🌈"),
    ("hair_crown_braid", "Crown Braid", "legendary", "👑"),
]:
    _add(iid, name, "avatar_hair", rarity, emoji)

for iid, name, rarity, emoji in [
    ("outfit_casual", "Casual Outfit", "common", "👕"), ("outfit_scholar", "Scholar Robes", "uncommon", "🎓"),
    ("outfit_trachten", "Bavarian Tracht", "rare", "🥨"), ("outfit_knight", "Knight Armor", "legendary", "🛡️"),
]:
    _add(iid, name, "avatar_clothes", rarity, emoji)

for iid, name, rarity, emoji in [
    ("bg_meadow", "Meadow", "common", "🌾"), ("bg_city", "City Street", "common", "🏙️"),
    ("bg_alps", "Alps", "uncommon", "🏔️"), ("bg_castle", "Castle", "rare", "🏰"),
    ("bg_aurora", "Aurora", "legendary", "🌌"),
]:
    _add(iid, name, "avatar_bg", rarity, emoji)

for iid, name, rarity, emoji in [
    ("frame_wood", "Wooden Frame", "common", "🖼️"), ("frame_silver", "Silver Frame", "uncommon", "⚪"),
    ("frame_gold", "Gold Frame", "rare", "🟡"), ("frame_diamond", "Diamond Frame", "legendary", "💎"),
]:
    _add(iid, name, "avatar_frame", rarity, emoji)

# ---------------------------------------------------------------- Titles ---
for iid, name, rarity in [
    ("title_beginner", "Beginner", "common"), ("title_wordsmith", "Wordsmith", "uncommon"),
    ("title_polyglot", "Rising Polyglot", "rare"), ("title_meister", "Sprachmeister", "legendary"),
]:
    _add(iid, name, "title", rarity, "🏷️")

# ----------------------------------------------------------- Decorations ---
for iid, name, rarity, emoji in [
    ("deco_sticker_pack", "Sticker Pack", "common", "✨"), ("deco_confetti_gold", "Golden Confetti Burst", "uncommon", "🎊"),
    ("deco_fireworks", "Fireworks Finish", "rare", "🎆"), ("deco_aurora_trail", "Aurora Trail", "legendary", "🌈"),
]:
    _add(iid, name, "decoration", rarity, emoji)

# ------------------------------------------------------------- XP Effects --
for iid, name, rarity, emoji in [
    ("xp_normal", "Normal XP", "common", "+"), ("xp_fancy", "Fancy XP", "common", "✨"),
    ("xp_fire", "Fire XP", "uncommon", "🔥"), ("xp_ice", "Ice XP", "uncommon", "❄️"),
    ("xp_lightning", "Lightning XP", "rare", "⚡"), ("xp_rainbow", "Rainbow XP", "rare", "🌈"),
    ("xp_golden", "Golden XP", "legendary", "🌟"), ("xp_pixel", "Pixel XP", "legendary", "👾"),
]:
    _add(iid, name, "xp_effect", rarity, emoji)


def items_by_type(item_type):
    return [v for v in CATALOG.values() if v["type"] == item_type]


def items_by_rarity(rarity, exclude_chest_only=True):
    return [v for v in CATALOG.values() if v["rarity"] == rarity and not (exclude_chest_only and v["chest_only"])]


def get_item(item_id):
    return CATALOG.get(item_id)


PURCHASABLE_ITEMS = [v for v in CATALOG.values() if not v["chest_only"]]

# Seasonal availability windows: item_id -> list of month numbers (1-12) when
# it's featured in the Seasonal Shop tab. Items remain purchasable in the Full
# Catalog tab year-round (a hard lockout felt more frustrating than fun for a
# single-player app) — the Seasonal Shop tab is where the "only right now"
# framing actually lives, per the brief's "Seasonal Shop" section.
SEASONAL_WINDOWS = {
    "halloween": [10],
    "christmas": [12],
    "oktoberfest": [9, 10],
    "summer": [6, 7, 8],
    "valentines": [2],
}


def seasonal_items_active(month: int = None):
    import datetime as _dt
    month = month or _dt.date.today().month
    return [CATALOG[iid] for iid, months in SEASONAL_WINDOWS.items() if month in months]


def seasonal_items_all():
    return [CATALOG[iid] for iid in SEASONAL_WINDOWS]
