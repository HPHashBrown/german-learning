"""Static content used across the app: themes, dictionary seed data,
word-of-the-day list, the hours-based recommendation roadmap, achievement
definitions, and motivational quotes."""

import datetime as dt

# --------------------------------------------------------------- THEMES ----
THEMES = {
    "Neon Megacity": {
        "unlock_hours": 0,
        "gradient": "linear-gradient(135deg,#0f0c29 0%,#302b63 45%,#24243e 100%)",
        "accent": "#ff2fd0",
        "accent2": "#2fe0ff",
        "text": "#f5f3ff",
        "emoji": "🌆",
        "blurb": "Rain-slicked streets, holograms, and synthwave nights.",
    },
    "Swiss Alps": {
        "unlock_hours": 25,
        "gradient": "linear-gradient(135deg,#e0f7fa 0%,#80deea 40%,#4fc3f7 100%)",
        "accent": "#0277bd",
        "accent2": "#ffffff",
        "text": "#062b3a",
        "emoji": "🏔️",
        "blurb": "Crisp alpine air, waterfalls, and golden sunrise peaks.",
    },
    "Black Forest": {
        "unlock_hours": 75,
        "gradient": "linear-gradient(135deg,#0b1d13 0%,#173425 50%,#0e2318 100%)",
        "accent": "#5fd97a",
        "accent2": "#c9a15a",
        "text": "#eafff0",
        "emoji": "🌲",
        "blurb": "Fog between the pines, campfires, and quiet rivers.",
    },
    "Bavarian Village": {
        "unlock_hours": 150,
        "gradient": "linear-gradient(135deg,#3a1f0f 0%,#7a4a24 45%,#c98a3e 100%)",
        "accent": "#ffd27a",
        "accent2": "#8a3b2b",
        "text": "#fff4e0",
        "emoji": "🏘️",
        "blurb": "Timber houses, castle spires, and warm café light.",
    },
    "German Christmas": {
        "unlock_hours": 300,
        "gradient": "linear-gradient(135deg,#0d1b2a 0%,#1b3a4b 40%,#3a0d17 100%)",
        "accent": "#ff5a5f",
        "accent2": "#a8e6cf",
        "text": "#fff8f0",
        "emoji": "🎄",
        "blurb": "Snow, market lights, mulled wine, and fireplaces.",
    },
    "Castle Library": {
        "unlock_hours": 500,
        "gradient": "linear-gradient(135deg,#1a1310 0%,#2e2117 45%,#1a1310 100%)",
        "accent": "#d4af37",
        "accent2": "#8b5e34",
        "text": "#f2e6d0",
        "emoji": "🕯️",
        "blurb": "Candlelight, ancient maps, and shelves of old books.",
    },
}

# ---------------------------------------------------------- WORD OF DAY ----
WORD_BANK = [
    dict(word="die Sehnsucht", ipa="ˈzeːnˌzʊxt", gender="f", plural="die Sehnsüchte",
         meaning="longing / yearning", example="Ich habe Sehnsucht nach dem Sommer.",
         translation="I long for summer.", related="sich sehnen (to yearn), die Nostalgie",
         tip="Think 'seeking' + 'sickness' — a sickness of seeking something far away."),
    dict(word="der Feierabend", ipa="ˈfaɪ̯ɐˌʔaːbn̩t", gender="m", plural="die Feierabende",
         meaning="end of the work day / evening off", example="Endlich Feierabend!",
         translation="Finally, quitting time!", related="feiern (to celebrate), der Abend (evening)",
         tip="Literally 'celebration evening' — Germans treat the end of work as worth celebrating."),
    dict(word="gemütlich", ipa="ɡəˈmyːtlɪç", gender="—", plural="—",
         meaning="cozy, comfortable, pleasant", example="Das Café ist sehr gemütlich.",
         translation="The café is very cozy.", related="die Gemütlichkeit (coziness)",
         tip="No direct English word — think 'hygge' but German."),
    dict(word="der Kummerspeck", ipa="ˈkʊmɐˌʃpɛk", gender="m", plural="—",
         meaning="weight gained from emotional overeating (lit. 'grief bacon')",
         example="Nach der Trennung hatte er etwas Kummerspeck.",
         translation="After the breakup he'd put on a bit of grief-weight.",
         related="der Kummer (grief), der Speck (bacon/fat)",
         tip="One of the most famous 'untranslatable' German compounds."),
    dict(word="die Ohrwurm", ipa="ˈoːɐ̯ˌvʊʁm", gender="m", plural="die Ohrwürmer",
         meaning="earworm / catchy song stuck in your head", example="Dieses Lied ist ein Ohrwurm.",
         translation="This song is an earworm.", related="das Ohr (ear), der Wurm (worm)",
         tip="Same idea as English 'earworm' — German gave English this word!"),
    dict(word="die Zwischenzeit", ipa="ˈtsvɪʃn̩ˌtsaɪ̯t", gender="f", plural="—",
         meaning="meantime / interim", example="In der Zwischenzeit kannst du üben.",
         translation="In the meantime you can practice.", related="zwischen (between), die Zeit (time)",
         tip="zwischen + Zeit = 'between-time'."),
    dict(word="der Wanderlust", ipa="ˈvandɐˌlʊst", gender="m", plural="—",
         meaning="desire to travel / wanderlust", example="Er hat großen Wanderlust.",
         translation="He has a great wanderlust.", related="wandern (to hike/wander), die Lust (desire)",
         tip="Another German loanword that entered English almost unchanged."),
    dict(word="die Vorfreude", ipa="ˈfoːɐ̯ˌfrɔɪ̯də", gender="f", plural="—",
         meaning="joyful anticipation", example="Die Vorfreude auf die Reise ist riesig.",
         translation="The anticipation for the trip is huge.", related="vor (before), die Freude (joy)",
         tip="Germans say Vorfreude ist die schönste Freude — anticipation is the best joy."),
]


def word_of_day(today: dt.date | None = None) -> dict:
    today = today or dt.date.today()
    idx = today.toordinal() % len(WORD_BANK)
    return WORD_BANK[idx]


# -------------------------------------------------------- MINI DICTIONARY --
MINI_DICTIONARY = {
    "haben": dict(meaning="to have", gender="—", plural="—", cefr="A1",
                  example="Ich habe einen Hund.", synonyms="besitzen",
                  compound="—"),
    "sprechen": dict(meaning="to speak", gender="—", plural="—", cefr="A1",
                      example="Sprichst du Deutsch?", synonyms="reden, sich unterhalten",
                      compound="das Gespräch (conversation)"),
    "Freundin": dict(meaning="girlfriend / female friend", gender="f",
                      plural="die Freundinnen", cefr="A1",
                      example="Sie ist meine beste Freundin.", synonyms="Kumpelin",
                      compound="die Brieffreundin (pen pal)"),
    "Park": dict(meaning="park", gender="m", plural="die Parks", cefr="A1",
                 example="Wir gehen in den Park.", synonyms="Grünanlage",
                 compound="der Nationalpark"),
    "gestern": dict(meaning="yesterday", gender="—", plural="—", cefr="A1",
                     example="Gestern war es sonnig.", synonyms="—",
                     compound="vorgestern (day before yesterday)"),
    "mit": dict(meaning="with", gender="—", plural="—", cefr="A1",
                example="Ich komme mit dir.", synonyms="—", compound="—"),
    "mein": dict(meaning="my", gender="—", plural="—", cefr="A1",
                 example="Das ist mein Buch.", synonyms="—", compound="—"),
    "in": dict(meaning="in", gender="—", plural="—", cefr="A1",
               example="Das Buch ist in der Tasche.", synonyms="—", compound="—"),
    "ich": dict(meaning="I", gender="—", plural="—", cefr="A1", example="Ich bin müde.",
                synonyms="—", compound="—"),
}


# ---------------------------------------------------- RECOMMENDATION MAP ---
RECOMMENDATION_ROADMAP = [
    dict(min_hours=0, max_hours=50, level="A1 (start)",
         items=[
             ("Slow German (Podcast)", "Very slow, clear narration for beginners."),
             ("Super Easy German (YouTube)", "Street interviews with subtitles + slow speech."),
             ("DW Nico's Weg (Course)", "Structured A1 story-based course from Deutsche Welle."),
             ("Picture books / graded A1 readers", "Minimal text, high visual support."),
         ]),
    dict(min_hours=50, max_hours=150, level="A1–A2",
         items=[
             ("Easy German (YouTube)", "Real street interviews with dual subtitles."),
             ("DW Langsam Gesprochene Nachrichten", "Slow-spoken daily news."),
             ("Simple children's shows", "Basic vocabulary, visual context."),
             ("Graded readers (A2)", "Short stories written for learners."),
         ]),
    dict(min_hours=150, max_hours=300, level="A2–B1",
         items=[
             ("Easy German (longer episodes)", "Slightly faster, broader topics."),
             ("Logo! Nachrichten", "News made for German children — clear and simple."),
             ("Deutsch Perfekt (Magazine)", "Graded-difficulty articles with vocab notes."),
             ("LingQ Mini Stories", "Short A2/B1 stories with audio + text."),
             ("Beginner-friendly podcasts", "Slower conversational podcasts."),
         ]),
    dict(min_hours=300, max_hours=600, level="B1–B2",
         items=[
             ("Tagesschau (selected reports)", "Real news, pick shorter/clearer segments."),
             ("Kurzgesagt (DE channel)", "Science explainers, clear narration."),
             ("Terra X", "Documentary series — history, nature, science."),
             ("Travel vlogs", "Natural speech, visual grounding."),
             ("History channels", "Structured narration, useful vocabulary."),
         ]),
    dict(min_hours=600, max_hours=1000, level="B2–C1",
         items=[
             ("Native YouTube (general)", "Full native content across any topic you enjoy."),
             ("German Twitch streams", "Fast, informal, unscripted native speech."),
             ("Netflix (German audio)", "Native shows/films at natural pace."),
             ("Tagesschau / news (full)", "Full-length native news broadcasts."),
             ("Comedy shows / podcasts", "Native humor — tests deep comprehension."),
         ]),
    dict(min_hours=1000, max_hours=999999, level="C1+",
         items=[
             ("Native content, unfiltered", "Choose based on interest, not difficulty."),
             ("Literature / novels", "Full native prose."),
             ("Political talk shows", "Fast, nuanced, opinionated speech."),
             ("Niche podcasts", "Anything from finance to philosophy, native speed."),
         ]),
]

TOPIC_FILTERS = [
    "News", "Science", "Technology", "History", "Gaming", "Cooking",
    "Travel", "Philosophy", "Finance", "Business", "Politics", "Comedy",
]


def recommendations_for_hours(hours: float):
    for tier in RECOMMENDATION_ROADMAP:
        if tier["min_hours"] <= hours < tier["max_hours"]:
            return tier
    return RECOMMENDATION_ROADMAP[-1]


# -------------------------------------------------------------- QUOTES -----
QUOTES = [
    ("Man lernt eine Sprache am besten dort, wo man sie leben muss.", "German proverb"),
    ("Die Grenzen meiner Sprache bedeuten die Grenzen meiner Welt.", "Ludwig Wittgenstein"),
    ("Wer fremde Sprachen nicht kennt, weiß nichts von seiner eigenen.", "Johann Wolfgang von Goethe"),
    ("Es ist nicht genug zu wissen, man muss es auch anwenden.", "Johann Wolfgang von Goethe"),
    ("Der Weg ist das Ziel.", "Confucius (popular German rendering)"),
    ("Alles, was wir vorwärts bringt, ist des Weges wert.", "German saying"),
    ("Wer nichts weiß, muss alles glauben.", "Marie von Ebner-Eschenbach"),
    ("Übung macht den Meister.", "German proverb"),
    ("Aller Anfang ist schwer.", "German proverb"),
    ("Was dich nicht umbringt, macht dich stärker.", "Friedrich Nietzsche"),
]


def quote_of_day(today: dt.date | None = None):
    today = today or dt.date.today()
    return QUOTES[today.toordinal() % len(QUOTES)]


# --------------------------------------------------------- ACHIEVEMENTS ----
def achievement_definitions():
    """Returns list of dicts: key, name, emoji, description, check(stats)->bool"""
    return [
        dict(key="first_hour", name="First Hour", emoji="🌱",
             desc="Log your first hour of German study.",
             check=lambda s: s["total_hours"] >= 1),
        dict(key="one_week_streak", name="One Week Streak", emoji="🔥",
             desc="Study 7 days in a row.",
             check=lambda s: s["current_streak"] >= 7),
        dict(key="hours_25", name="25 Hours", emoji="📘",
             desc="Reach 25 total hours.", check=lambda s: s["total_hours"] >= 25),
        dict(key="hours_100", name="100 Hours", emoji="📗",
             desc="Reach 100 total hours.", check=lambda s: s["total_hours"] >= 100),
        dict(key="hours_250", name="250 Hours", emoji="📙",
             desc="Reach 250 total hours.", check=lambda s: s["total_hours"] >= 250),
        dict(key="hours_500", name="500 Hours", emoji="📕",
             desc="Reach 500 total hours.", check=lambda s: s["total_hours"] >= 500),
        dict(key="hours_1000", name="1000 Hours", emoji="🏆",
             desc="Reach 1000 total hours — true dedication.",
             check=lambda s: s["total_hours"] >= 1000),
        dict(key="vocab_25", name="Vocabulary Builder", emoji="🧠",
             desc="Save 25 words to your dictionary.",
             check=lambda s: s["saved_words"] >= 25),
        dict(key="vocab_100", name="Vocabulary Master", emoji="🎓",
             desc="Save 100 words to your dictionary.",
             check=lambda s: s["saved_words"] >= 100),
        dict(key="consistency_king", name="Consistency King", emoji="👑",
             desc="Reach a 30-day streak.", check=lambda s: s["current_streak"] >= 30),
        dict(key="german_explorer", name="German Explorer", emoji="🗺️",
             desc="Unlock 3 different world themes.",
             check=lambda s: s["themes_unlocked"] >= 3),
        dict(key="sessions_50", name="Fifty Sessions", emoji="📅",
             desc="Log 50 study sessions.", check=lambda s: s["sessions"] >= 50),
    ]
