"""Renders the current town grid to a downloadable PNG image using Pillow.

Deliberately avoids relying on emoji glyphs rendering correctly (color-emoji
font support varies a lot across deployment environments, including
Streamlit Cloud) — instead uses a colored-tile + short-text-label scheme
that's guaranteed to render consistently anywhere Pillow + a basic TrueType
font are available, which DejaVu Sans reliably is on Debian-based systems
(the base of Streamlit Cloud's environment).
"""

import io
from PIL import Image, ImageDraw, ImageFont

import town_config as tcfg

TILE_SIZE = 48
MARGIN = 24
HEADER_HEIGHT = 70

FONT_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]

FOG_COLOR = (40, 40, 48)
LOCKED_COLOR = (90, 90, 100)
BG_COLOR = (22, 22, 28)

TERRAIN_COLORS = {
    "forest": (34, 90, 52), "grassland": (120, 180, 90), "meadow": (170, 210, 120),
    "rocky": (130, 120, 110), "river": (70, 130, 190), "sandy": (220, 200, 150),
    "dense_woods": (24, 70, 40), "autumn_forest": (170, 100, 50), "plains": (150, 190, 110),
    "flower_field": (220, 160, 190),
}

CATEGORY_COLORS = {
    "residential": (150, 110, 70), "commercial": (210, 170, 40), "educational": (60, 110, 200),
    "cultural": (140, 70, 180), "utility": (100, 110, 120), "decoration": (200, 90, 130),
}


def _load_font(size: int):
    for path in FONT_PATHS:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()


def render_town_image(world: tcfg.World, tiles_df, completion_pct: float) -> bytes:
    """tiles_df: the DataFrame from town_db.get_tiles() (NaN already normalized to None)."""
    grid_size = world.grid_size
    width = MARGIN * 2 + grid_size * TILE_SIZE
    height = MARGIN * 2 + HEADER_HEIGHT + grid_size * TILE_SIZE

    img = Image.new("RGB", (width, height), BG_COLOR)
    draw = ImageDraw.Draw(img)

    title_font = _load_font(22)
    subtitle_font = _load_font(14)
    label_font = _load_font(16)

    title = f"{world.flag} {world.name}"
    draw.text((MARGIN, MARGIN - 6), title, font=title_font, fill=(245, 245, 250))
    draw.text((MARGIN, MARGIN + 26), f"{completion_pct}% expanded", font=subtitle_font, fill=(190, 190, 200))

    tiles_by_pos = {(int(r["x"]), int(r["y"])): r for _, r in tiles_df.iterrows()}
    grid_top = MARGIN + HEADER_HEIGHT

    for y in range(grid_size):
        for x in range(grid_size):
            tile = tiles_by_pos.get((x, y))
            px = MARGIN + x * TILE_SIZE
            py = grid_top + y * TILE_SIZE

            if tile is None or tile["locked"]:
                color = FOG_COLOR
                label = ""
            else:
                building_id = tile["building_id"]
                if building_id:
                    building = tcfg.BUILDINGS.get(building_id)
                    color = CATEGORY_COLORS.get(building.category, LOCKED_COLOR) if building else LOCKED_COLOR
                    label = (building.name[:2].upper() if building else "??")
                else:
                    color = TERRAIN_COLORS.get(tile["terrain_id"], (80, 100, 80))
                    label = ""

            draw.rectangle(
                [px + 2, py + 2, px + TILE_SIZE - 2, py + TILE_SIZE - 2],
                fill=color, outline=(15, 15, 20), width=1,
            )

            if label:
                bbox = draw.textbbox((0, 0), label, font=label_font)
                tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
                draw.text(
                    (px + TILE_SIZE / 2 - tw / 2, py + TILE_SIZE / 2 - th / 2 - 2),
                    label, font=label_font, fill=(255, 255, 255),
                )
            elif tile is not None and not tile["locked"] and tile["decoration_id"]:
                # small dot to show a decoration is present on an otherwise-empty tile
                draw.ellipse(
                    [px + TILE_SIZE - 14, py + 4, px + TILE_SIZE - 4, py + 14],
                    fill=CATEGORY_COLORS["decoration"],
                )

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.read()
