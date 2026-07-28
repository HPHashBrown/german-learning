# 🌲 Fluent Forest: German

A premium, immersion-focused German learning companion built with Streamlit.

## What's implemented (fully working, not mockups)

- **Dashboard** — streak, total/weekly/monthly hours, XP, estimated CEFR level, animated daily-goal gauge, Word of the Day, top content recommendation, current world.
- **Study Time Logger** — logs sessions (category, duration, difficulty, resource, notes) to a local SQLite database; recalculates lifetime/weekly/monthly hours automatically.
- **Streak System** — daily streak with a real calendar-based algorithm, longest streak tracking, and auto-earned Streak Freeze tokens every 7-day streak that silently cover one missed day.
- **World Themes** — 6 fully styled world themes (Neon Megacity, Swiss Alps, Black Forest, Bavarian Village, German Christmas, Castle Library) that unlock automatically at hour thresholds, each with its own gradient, accent colors, and full app re-theming.
- **Word of the Day** — rotates deterministically by date, full word detail (IPA, gender, plural, example, memory tip), archive of past words, one-click save to your dictionary.
- **Sentence Breakdown Tool** — paste any German sentence and get a word-by-word table (base form, meaning, grammar) plus notes on cases, word order, separable verbs, idioms, and translations.
  - This calls the **Claude API** for real grammatical analysis (enter your own Anthropic API key in the sidebar — kept only in-session, never written to disk).
  - Without a key, it falls back to an **offline mode** using a small built-in dictionary — clearly labeled as limited, rather than pretending to give real grammar analysis it can't back up.
- **Smart Dictionary** — save words into collections; a quick-lookup tab against a built-in reference dictionary.
- **Content Recommendation Engine** — recommends real, named resources (Slow German, Easy German, Tagesschau, Netflix, etc.) based on your *cumulative logged hours*, following the roadmap you specified, with a full expandable roadmap view.
- **Achievements** — 12 real achievements (hours milestones, streaks, vocabulary size, sessions count, themes unlocked) that unlock automatically and show as animated badge grids, plus an hours-milestone tracker (10h → 2000h).
- **Statistics** — session count, average session length, favorite activity, most productive day, a real calendar heatmap, category pie chart, weekly bar trend, and monthly area trend — all computed from your actual logged data.
- **Settings** — daily goal selector, streak freeze balance, CSV export of all sessions.

## Honest limitations (by design, not oversight)

- The **AI Tutor** (freeform Q&A, roleplay, pronunciation feedback) described in the original brief is **not included**. Building it well needs a dedicated chat interface and conversation-history handling; wiring it in half-heartedly would be worse than leaving it out. The Sentence Breakdown tool already demonstrates the Claude API integration pattern, so it — or an AI Tutor page — can be added as a next step.
- The offline sentence analysis fallback only recognizes the small hand-written dictionary in `content.py`. It's intentionally transparent about this rather than guessing at grammar it can't verify.
- Everything else in the "Future Features" section of the brief (OCR, subtitle import, pronunciation scoring, leaderboards, mobile app, etc.) is out of scope for this build, same as stated in the original spec.

## Running it

```bash
pip install -r requirements.txt
streamlit run app.py
```

The app creates a local `fluent_forest.db` SQLite file next to `app.py` on first run — all your data stays on your machine. No API key is required to use the app; it's only needed for the AI-powered sentence grammar analysis.

## Files

- `app.py` — main Streamlit app and all pages
- `db.py` — SQLite data layer (sessions, profile, streaks, achievements, saved words)
- `content.py` — themes, word bank, dictionary, recommendation roadmap, quotes, achievement definitions
- `styles.py` — glassmorphism/gradient CSS injection, theme-aware
- `nlp_tools.py` — sentence breakdown (Claude API + offline fallback)
