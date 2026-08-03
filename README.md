# 🐉 Fluent Forest RPG

A Duolingo-inspired, gamified German learning platform — XP/leveling, coins, loot chests,
a shop, pets, avatars, spaced-repetition flashcards, AI conversation/writing/pronunciation
tools (Gemini), and more. Built as a full transformation per the Phase 3 brief.

## Important scope note up front

This brief described a **fundamentally different app** from the hours-tracking dashboard
built in earlier phases — an XP/level RPG economy rather than an hours-logged CEFR tracker.
Rather than awkwardly bolt the two paradigms together, this is a clean rebuild using the
requested leveling/shop/loot systems as the core structure. It's a separate codebase from
the earlier "Fluent Forest" hours-tracker; nothing from that app is reused here except the
general engineering approach (SQLite persistence, tested interaction flows).

## What's real and fully working

- **Leveling system**: XP curve to Level 50, with the exact Level 1-4 thresholds specified
  (0/250/600/1100) and a progressively steeper curve beyond that. Content unlocks exactly
  as mapped in the brief (Greetings/Numbers/Colors/Basic Vocab at 1 → Master Challenges at 50).
  The sidebar and Home page show "Only X XP until [feature] unlocks!" live.
- **Log Immersion**: a dedicated page to log real-world German time (reading, listening,
  watching, speaking, whatever) — converts to XP and coins (60 XP + 15 coins per hour,
  constants live in `db.py`), shows total/weekly/monthly hours and your current streak, and
  keeps a full history table. This feeds the same XP/coins/weekly-challenge systems as every
  other activity in the app.
- **Wallet**: a dedicated page showing your coin balance, key counts, a recent-purchases
  table (pulled from real inventory acquisition records, not a fabricated log), and a
  capped mini-activity (a quick der/die/das "Word Flip" round, +5 coins per correct answer,
  limited to 5 rounds/day) for a little extra spending money without turning into a way to
  farm the coin economy.
- **Town Expansion**: a full Clash-of-Clans-style town-building system. A 3×3 starting grid
  hidden in fog; clicking an orthogonally-adjacent locked tile (no diagonal expansion, per
  spec) opens a real learning challenge — reusing the existing vocabulary/article/verb/
  grammar generators, not a separate content bank — scaled through four difficulty tiers
  (Easy → Medium → Hard → Advanced) based on how many tiles you've claimed. Passing reveals
  the tile's terrain (10 types) and awards the game's real XP/coins. 30 buildings across
  Residential/Commercial/Educational/Cultural/Utility/Decoration categories, each with real
  multi-level upgrade paths, gated by your actual Player Level. Commercial/Educational/
  Utility buildings modify (never generate) lesson coin rewards — flat bonus, then percent
  bonus, then the current world's multiplier, applied to every vocabulary quiz, reading
  story, immersion-hours log, and tile-claim reward, with the exact breakdown shown to the
  player each time. Six worlds (German Village → Berlin → Vienna → Zurich → European Tour →
  World Tour), each with a larger grid, its own terrain-weight table, and a harder starting
  difficulty tier; advancing requires 100% of the current world's grid unlocked. Everything
  — terrain types, buildings, worlds, difficulty tiers — lives in one data-driven config
  file (`town_config.py`); adding a new building or world is a dict entry, not an engine
  change. Built with plain Streamlit widgets only (button grid, forms, selects) — no custom
  HTML/JS, per the brief's explicit requirement. Persists in the same SQLite database and
  was verified to survive a full process restart with tile-for-tile identical state.

  Two honest notes on this system: (1) the brief's own worked coin-bonus example (100 base →
  137 final) doesn't actually resolve under any consistent stacking order I could construct
  — I tried flat-then-pct-then-world in several combinations and none hit exactly 137, so I
  treated it as illustrative rather than an exact spec and implemented a clearly-defined,
  documented, transparently-displayed formula instead (see `compute_coin_bonus` in
  `town_engine.py`). (2) Cultural buildings (Museum, Opera House, Town Hall, Castle) track
  which content-unlock keys they've earned (`unlocked_content_keys()` in the engine) but
  this isn't yet wired into gating actual Reading Stories/AI Chat scenarios — retrofitting a
  second unlock gate onto already-working, already-tested content pages carried more
  regression risk than benefit in this pass, so it's a clean, ready-to-use hook rather than
  a half-integrated feature.
- **Locked Buildings preview**: the Town page has a "🔒 Locked Buildings" expander showing
  every building you haven't unlocked yet, grouped by category, with the exact Player Level
  and remaining XP needed for each — so you can see what's coming before you get there.
- **Currency system**: coins, separate from XP, earned from quizzes/stories/challenges,
  spendable only on cosmetics (themes, avatar parts, pets, decorations, XP effects, titles)
  — never on anything that affects learning power.
- **Daily login rewards**: a procedurally-generated schedule through day 200, with milestone
  spikes at 3/7/14/21/25/30/50/75/100/125/150/175/200 (chests, themes, titles, legendary pet,
  "Legend Status"), and smaller varied rewards on ordinary days. Deterministic per day number
  (won't reroll on refresh) but varies day to day.
- **Loot chests**: exactly the rarity odds specified in the brief for Common/Rare/Legendary
  chests. **The Uncommon chest table in the brief summed to 95%, not 100%** (15/60/15/5) —
  this is flagged in `loot.py` and fixed by adjusting Uncommon's own rarity from 60%→65%,
  keeping the other three numbers exactly as given. All four tables were verified
  statistically against 200,000 simulated rolls each and matched their target percentages.
- **Shop**: full catalog (66 items — themes, pets, avatar parts, titles, decorations, XP
  effects) across all four rarity tiers, priced by rarity. **The Full Catalog tab now only
  sells Common and Uncommon items** — Rare and Legendary items are exclusive to Loot Chests
  and the Daily Shop's rotation (which draws from the full pool, including rares, plus its
  own 2% legendary chance), so top-tier cosmetics stay meaningfully special rather than a
  guaranteed same-day purchase. Plus a **Daily Shop** (10 discounted items, deterministic
  per-day rotation) and a Keys tab.
- **Vocabulary Quiz, Article Trainer, Verb Trainer, Grammar Explorer**: all generate real
  questions from real content and grade them correctly. The verb conjugation logic was
  bug-tested directly — including catching and fixing a real error where t-stem verbs
  (e.g. *arbeiten*) were conjugated wrong (*arbeitst* instead of *arbeitest*).
- **Reading Stories**: 16 original stories (4 each at A1/A2/B1/B2) — see the note below on
  why this isn't 100.
- **Flashcards**: genuine SM-2 spaced repetition (the same core algorithm behind Anki),
  verified to correctly grow intervals on success and reset on failure.
- **Vocabulary Manager**: search, tag/state filters, favorites, Anki CSV export.
- **AI Chat, AI Writing Tutor, Pronunciation Trainer**: all wired to Google's **Gemini**
  API using the current `google-genai` SDK (the older `google-generativeai` package is
  deprecated and was deliberately avoided). Also used for the Dictionary-style lookups
  wherever the app needs one, per the brief's request to switch the dictionary to Gemini.
  You supply your own Gemini API key in the sidebar (session-only, never written to disk).
  I could not test live API calls from this build environment (no network route to
  Google's API here) — but the request-building code was checked line-by-line against the
  actual installed SDK's real method signatures, and the error-handling paths were verified
  to fail gracefully (tested with an invalid key) rather than crash the app.
- **CEFR Roadmap, Statistics Dashboard, Weekly Challenges, Trophy Room (achievements +
  collectibles), Avatar Customization**: all functional, all backed by real data.
- **XP effects** (Fire/Ice/Lightning/Rainbow/Golden/Pixel/Fancy/Normal): ownable and
  equippable via Avatar Customization, and actually change the "+N XP" text shown after
  quizzes, the article trainer, verb trainer, and reading stories — not just sitting unused
  in the inventory.
- **Random Daily Extras**: an idiom, a Germany/Austria/Switzerland fact, and a quote, one of
  each per day, shown on the Home page — deterministic per date (won't reroll on refresh).
- **Seasonal Shop**: a dedicated tab showing which seasonal themes are "in season" by actual
  calendar month (Valentine's in Feb, Summer in Jun-Aug, Oktoberfest in Sep-Oct, Halloween in
  Oct, Christmas in Dec), plus a status list of all seasonal items and when they're active.
  They remain purchasable in the Full Catalog tab year-round too — a hard lockout felt more
  frustrating than fun for a single-player app; the Seasonal tab is where the "featured right
  now" framing lives.
- **Sound design**: procedurally generated tones via the Web Audio API (correct/incorrect/
  level-up/achievement/unlock/daily-reward/coin) — no external audio files that can go
  missing. Toggleable in Settings.
- **Confetti**: via canvas-confetti (CDN), with a silent no-op fallback if it can't load.
- **Persistence**: everything lives in SQLite (`fluent_forest_rpg.db`), autosaves on every
  action, survives restarts. Full JSON backup export in Settings.

## Latest additions (this round)

- **Equipped Title** now shows on the Home page header next to your name.
- **Terrain-specific buildings**: Water Mill (requires River), Lumber Mill (requires Forest),
  Stone Quarry (requires Rocky Ground) — hard terrain gates — and Farm (+50% effect on
  Grassland) — a soft bonus. The Build panel shows terrain requirements/bonuses per building
  and disables ones that can't go on the selected tile, with a clear explanation why.
- **Building relocation**: a "🚚 Move" button on any built tile starts a guided
  "click an empty tile to place it there" flow, costs 50% of the building's original build
  cost, preserves its current level, and safely rolls back (no ghost buildings, no lost
  coins) if you cancel or can't afford it.
- **Decorations now layer independently from buildings** — they use the `decoration_id`
  column that already existed in the schema but was unused; a tile can hold one building
  *and* one decoration at the same time, each with its own occupancy rule. The grid shows
  both together (e.g. 🥐🌳), and decorations are placed either from the Build panel (on
  empty tiles) or a dedicated section in the Upgrade panel (on tiles that already have a
  building).
- **Building visual evolution**: a building's emoji can now change at higher levels (e.g.
  Bakery 🥐 → 🍞 → 🏪, House 🏠 → 🏡 → 🏘️, Farm 🌻 → 🌾 → 🚜, Library 📚 → 🏛️) via an
  `emoji_override` on specific `BuildingLevel` tiers — added to five representative
  buildings; the pattern is data-driven so more can be added with a one-line change per tier.
- **Town snapshot download**: a "📸 Snapshot" button renders the current town grid to a PNG
  (via Pillow, pure Python) and offers it as a download. Deliberately uses colored tiles +
  short text labels instead of literal emoji glyphs, since color-emoji font support isn't
  guaranteed across deployment environments (including Streamlit Cloud) — this renders
  identically everywhere.
- **3 new C1 stories**, gated behind Level 40 (the "Native Stories" unlock) rather than the
  general Level 3 "Reading Stories" gate the other 16 stories use.
- **AI Chat scenarios expanded from 8 to 16** — Pharmacy, Post Office, Bank, Apartment
  Hunting, Public Transport, Tech Support, Small Talk, Returning a Product — so hitting the
  Level 20 "AI Roleplay" unlock roughly doubles your options, a real content expansion.
- **Weakest grammar topic tracker**: Grammar Explorer mini-quizzes now actually get recorded
  (they didn't before — no XP, no tracking) and award small XP per question. A banner at the
  top surfaces your weakest topic by accuracy once you've answered at least 2 questions in
  it, and each topic's expander shows its running accuracy.
- **Personal Records page**: longest streak, peak coins ever held, best single day/week for
  XP, most quizzes in a day, most immersion hours in a day, stories completed, chests
  opened — all computed from real logged history. No fake leaderboard; genuinely "beat your
  own record."
- **Sound packs**: two purchasable alternates (Chiptune, Soft Chimes) alongside the
  starter-owned Classic pack, each with a distinct tone character across all 7 sound events.
  Equip via the Avatar page's new "Sound Pack" slot.
- **Verb Trainer**: added Speed Round (60-second time budget, unlimited questions within it)
  and Infinite Streak (keep going until you miss one, tracks your personal best streak)
  alongside the original Standard 10-question mode. Honest note: without JavaScript there's
  no live-ticking visual countdown in Speed Round — the remaining-time estimate updates each
  time you submit an answer rather than ticking every second, which is disclosed directly in
  the UI rather than faking a smoother experience than what Streamlit can actually do.
- **Listening Practice** (finally a real page behind the Level 15 unlock label): uses the
  browser's built-in text-to-speech (Web Speech API, German voice, no audio files) with three
  exercise types — Fill in the Blank, Translate, and Listen & Identify (pick which of several
  similar written sentences matches what you heard). 13 sentences across A1–B2, with B1/B2
  gated behind Level 25/35 so difficulty genuinely increases as you progress.

## Honestly descoped or simplified (and why)

- **100 stories → 16 stories.** Writing 100 original, grammatically correct short stories
  with working comprehension questions isn't achievable at real quality in one pass. 16
  well-tested stories (all internally verified — every question's answer is in its options,
  every story has vocab/grammar notes/questions) beats 100 padded-out ones. The data
  structure is flat and simple specifically so more can be appended later without touching
  any other code.
- **Audio narration for stories** isn't included as pre-recorded files (no assets to
  ship/break); the browser's built-in speech synthesis could read stories aloud as a
  follow-up, but wasn't wired in this pass.
- **Pronunciation scoring** uses Gemini's qualitative judgment of an audio recording, not a
  calibrated phonetic-analysis pipeline (that would need a dedicated speech model). This is
  disclosed directly on the Pronunciation Trainer page — treat scores as a rough guide.
- **Global/friends leaderboards**: not implemented. A real leaderboard needs a shared
  backend with multiple real users; this is a local single-user SQLite app. Faking a
  leaderboard with bot data would be actively misleading, so it's left out — genuine
  multiplayer is explicitly listed as a "Future Expansion" in the brief itself, so this
  isn't a gap so much as sequencing.
- **Seasonal Shop date-gating** now only affects the *featured* tab (see above) — items
  aren't hard-locked outside their season, by design.
- **"Random Daily Extras"** — now implemented (see above).
- **XP effect visuals** — now implemented (see above); they change completion-screen text,
  not yet a full animated popup overlay on every point gained.

## Running it

```bash
pip install -r requirements.txt
streamlit run app.py
```

Creates `fluent_forest_rpg.db` (SQLite) next to `app.py` on first run. All data stays local.
A Gemini API key (from Google AI Studio) is only needed for AI Chat, Writing Tutor,
Pronunciation Trainer — everything else works with zero API keys.

## Files

- `app.py` — main Streamlit app, all 19 pages
- `db.py` — SQLite data layer
- `levels.py` — XP curve + level-gated content unlocks
- `rewards.py` — daily login reward schedule (200 days) + weekly challenge pool
- `shop_catalog.py` — full cosmetics catalog (themes/pets/avatar parts/titles/decorations/XP effects)
- `loot.py` — loot chest odds and opening logic (includes the brief's math-error fix, documented inline)
- `lessons.py` — vocabulary categories + quiz generator
- `grammar.py` — grammar explorer content, verb conjugation engine, article trainer
- `stories.py` — 16 original reading stories with vocab/grammar/comprehension questions
- `srs.py` — SM-2 spaced repetition algorithm
- `daily_extras.py` — idiom / DACH fact / quote of the day
- `town_config.py` — town system config: terrain, buildings, worlds, challenge tiers (data-driven)
- `town_db.py` — town system persistence (same SQLite file, its own tables)
- `town_engine.py` — town system pure game logic (grid, adjacency, building, coin bonuses, moving)
- `town_snapshot.py` — renders the town grid to a downloadable PNG (Pillow, no JS)
- `listening_content.py` — sentence bank for the Listening Practice page
- `tile_challenge.py` — generates tile-claim challenges by reusing existing quiz/grammar content
- `gemini_tools.py` — Gemini API integration (chat, writing tutor, pronunciation, dictionary)
- `achievements.py` — Trophy Room achievement definitions
- `effects.py` — procedural sound tones + confetti
- `styles.py` — theme-aware CSS injection

## Testing notes

Every page was run through `streamlit.testing.v1.AppTest`, both fresh and under a stress
scenario (50,000 XP, 10,000 coins, 20 loot chests opened across all four types, 30 saved
words, 15 quiz results). Full interactive playthroughs (not just page loads) were run for:
a full 8-question vocabulary quiz, a full 10-word article trainer round, a full verb trainer
round, a complete reading story (read → save vocab → answer questions → submit), a flashcard
SM-2 review, vocabulary search/favorite/export, a shop purchase, a full loot chest opening,
an avatar equip, and the settings reset flow (both cancel and confirm paths). Four real bugs
were caught and fixed in the process: a non-deterministic `hash()` call that would have
silently changed weekly challenges on every restart, the brief's own Uncommon-chest odds not
summing to 100%, an incorrect conjugation rule for t-stem verbs, and a `format_func`-related
Streamlit widget-state crash when navigating away from the Avatar page after making a
selection (fixed by using plain string options instead of `format_func`).

A follow-up pass added XP effects, Daily Extras, and the Seasonal Shop tab. During that
work, an edit accidentally deleted a function's `def` line while inserting a new function
above it, orphaning `_generate_daily_shop`'s body and breaking the Shop page — caught
immediately by re-running the same page-by-page regression test after the change, before
it reached delivery.

The Town Expansion system added the largest single batch of new code in this project.
Testing there included: statistical odds-table verification wasn't needed this time, but
every boundary of the difficulty-tier thresholds (0/10/30/60 tiles) and world difficulty
offsets was checked directly, all four challenge tiers were verified to generate valid
questions and grade pass/fail correctly at both extremes and exactly at the pass threshold,
diagonal-adjacency exclusion and max-level upgrade rejection were both explicitly tested,
and the full click-through flows (claim a tile with correct answers, claim with wrong
answers, build, upgrade, complete a world, advance to the next world) were driven through
actual Streamlit widgets via AppTest, not just called as functions. Two real bugs were
caught this round: the exact same "accidentally deleted a function's `def` line" mistake
happened again while wiring in the coin-bonus helper (caught immediately by the same
regression check, which is now just a standard step after every edit to this file), and a
dataclass-vs-dict attribute access bug in the tile-claim success message (`reveal['terrain']
['emoji']` instead of `reveal['terrain'].emoji`) that only surfaced when testing the
success path with genuinely correct answers rather than random/wrong ones — a reminder that
testing only the failure path isn't enough when both paths render different messages.
