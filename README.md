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
  effects) across all four rarity tiers, priced by rarity, plus a **Daily Shop** (10
  discounted items, deterministic per-day rotation, with a genuine 2% chance of a bonus
  legendary item appearing) and a Keys tab.
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
