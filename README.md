# 🌲 Fluent Forest: German

A premium, immersion-focused German learning companion built with Streamlit — now with Phase 2's
personalization, forecasting, and intelligence layer added on top of the original tracker.

Every feature below was individually exercised with Streamlit's `AppTest` framework (fresh-start
and with hundreds of seeded sessions across 400+ days) and checked for real, correct behavior —
not just "does it render." See **Testing notes** at the bottom for specifics.

## Phase 1 — Core tracker (unchanged, still fully intact)

- **Dashboard**, **Study Time Logger**, **Streak System** (with auto-earned Streak Freeze tokens),
  **World Themes** (6 unlockable, fully re-themed), **Word of the Day**, **Sentence Breakdown Tool**
  (Claude API + offline fallback), **Smart Dictionary**, **Achievements** (12, auto-unlocking),
  **Statistics** (heatmap, pie, weekly/monthly trends).

## Phase 2 — What's new

### Reliable progress saving
Nothing had to change here in the sense of "switch to a database" — the app already used SQLite
exclusively (never Streamlit session state) from Phase 1, so restarts, refreshes, and returning days
later already preserved everything. What Phase 2 adds is **autosave on every new surface**: study
notes, study-plan edits, accessibility toggles, and challenge completions all write to SQLite the
instant they change — no "Save" button anywhere except where a multi-field form genuinely needs one
(e.g. logging a session, which needs several fields filled in together). On top of that, Phase 2
adds full **JSON backup export/import** (Settings page) so you can restore your entire history —
sessions, words, favorites, notes, achievements, streaks, XP, everything — on a fresh install or
another machine. This was tested with a real export → wipe database → import round-trip.

### Dynamic Daily Challenges
Three challenges/day (🟢 Easy / 🟡 Medium / 🔴 Hard), deterministically generated per calendar date
(same challenges if you reload, new ones tomorrow) while avoiding titles used in the last 10 days.
Completing one awards XP instantly. New page: **🎯 Daily Challenges**, plus a preview on the Dashboard.

### Personalized Resource Engine
Real resources with real, stable URLs (Easy German, Slow German, DW's Nicos Weg, Tagesschau, Terra X,
Kurzgesagt, Netflix, Twitch, etc.) — filterable by topic, adapted to your logged hours, with
"mark done" (so it stops resurfacing) and one-click "⭐ Favorite." Honest design note: these link to
each resource's **channel/homepage**, not a specific video or article, because a deep link to one
video would go stale and there's no way to verify a specific URL still resolves — the homepage link
is guaranteed valid and still gets you to exactly the right place. This is disclosed in the UI.

### Progress Forecast
On the Dashboard: % through your current estimated CEFR band, hours remaining to the next one,
your actual trailing 4-week pace, and estimated arrival dates at your current pace and at a 25%
faster pace — recalculated fresh on every page load from your real session data.

### Weekly AI Reflection
New page: **🪞 Weekly Reflection**. At the end of each completed week, generates (and caches) a
report: strongest/weakest skill by hours, consistency %, most productive day and method, any
milestone crossed that week, a recommended focus, and a suggested challenge for next week. Past
reports remain browsable.

### Smart Study Planner
New page: **📆 Study Planner**. An editable weekly rhythm (defaults to a sensible Mon–Sun spread)
that autosaves per-field on edit, plus a "this week so far" tracker showing which days you've
actually studied against the plan.

### Personal Learning Profile
New page: **🧬 Learning Profile**. Favorite method (by session count), most successful method (by
hours), average/longest session, favorite study day — all derived live from your logged sessions.
Honest note included in the page itself: "most difficult grammar topics" and "preferred time of
day" aren't shown because they'd need richer per-session metadata than the app currently captures —
nothing here is guessed.

### Learning Timeline
New page: **🕰️ Timeline**. Auto-records real milestones as you hit them (first session, 10 hours,
each hour milestone, 100th saved word, 7-day and 30-day streaks, each CEFR band, each theme
unlock) — idempotent, so it won't duplicate entries on repeat visits.

### Adaptive Goal Suggestions
Compares your trailing 14-day daily average against your current goal and suggests a change (up or
down) with a one-click "Apply" button — shown on the Dashboard and in Settings.

### Personalized Motivation System
Every message on the Dashboard is generated from your real numbers ("You've already invested 143
hours...", "You're closer to B2 than A2...", "You've completed 46 sessions this month...") — no
generic filler.

### Intelligent Session Insights
After logging a session, the Dashboard shows a same-day breakdown by category, weekly goal %, hours
to your next level, and one balancing suggestion (e.g. "you did a lot of listening today, try some
reading").

### Favorites Library
New page: **⭐ Favorites**. Bookmark anything (from the Resource Engine, or manually), filterable by
type.

### Search Everything
New page: **🔎 Search**. Fuzzy search (substring + typo-tolerant subsequence matching) across saved
words, notes, favorites, achievements, sessions, and challenge types — tested with real queries
against real seeded data.

### Calendar View
New page: **📅 Calendar**. Month grid showing which days you studied and how much; click any date
to see that day's full session detail.

### Data Export & Backup
Settings page now offers: CSV (sessions), full JSON backup (everything), and a generated **PDF
progress report** (via reportlab) — plus JSON import with a Merge/Replace choice, tested end-to-end.

### Keyboard Shortcuts
Toggle in Settings (off by default, clearly marked "beta"). When enabled: **D** Dashboard, **L** Log
Study Time, **C** Daily Challenges, **F** Search. Implemented as a small injected script that clicks
the matching sidebar option — this is genuinely best-effort, since client-side JS behavior can't be
verified by the same automated testing used for everything else in this app, and it's labeled as
such in the UI rather than promised as guaranteed.

### Accessibility & Customization
Settings page: font size (4 steps), high-contrast mode, reduced motion (disables hover/flicker
animations app-wide), a color-blind-safe accent palette (Okabe-Ito), and compact/spacious layout
density — all apply instantly, all autosave.

## Honest limitations (by design, not oversight)

- **AI Tutor** (freeform Q&A, roleplay, live pronunciation feedback) is still not included, same as
  Phase 1 — it needs its own chat/conversation-state architecture and deserves to be built properly
  rather than bolted on.
- **Custom dashboard widgets that users can rearrange** — not implemented. The dashboard layout is
  fixed. Drag-and-drop widget rearrangement in Streamlit requires a custom JS component beyond what
  could be built and verified to this standard in this pass.
- Offline Sentence Breakdown still only recognizes the small built-in dictionary — unchanged from
  Phase 1, still transparent about the limitation rather than guessing.
- Resource links go to channel/show homepages, not individual videos/articles — see the
  Recommendations page note above for why.
- "Most difficult grammar topics" and "preferred learning times" in the Learning Profile aren't
  shown, for the reason stated on that page itself.

## Running it

```bash
pip install -r requirements.txt
streamlit run app.py
```

Creates `fluent_forest.db` (SQLite) next to `app.py` on first run. All data stays local. No API key
is required except for the optional AI-powered Sentence Breakdown grammar analysis.

## Files

- `app.py` — main Streamlit app, all 18 pages
- `db.py` — SQLite data layer (sessions, profile, streaks, achievements, challenges, favorites,
  notes, weekly reflections, study plan, timeline, export/import)
- `intelligence.py` — forecasting, challenge generation, adaptive goals, motivation messages,
  session insights, weekly reflections, learning profile derivation, timeline sync
- `resources.py` — curated resource library with real URLs, used by the recommendation engine
- `reports.py` — PDF progress report generation (reportlab)
- `content.py` — themes, word bank, dictionary, recommendation roadmap, quotes, achievement defs
- `styles.py` — glassmorphism/gradient CSS injection, theme- and accessibility-aware
- `nlp_tools.py` — sentence breakdown (Claude API + offline fallback)

## Testing notes

Every page was run through `streamlit.testing.v1.AppTest` both fresh (empty database) and against a
stress dataset (310 sessions across ~400 days with random gaps, 40 saved words) — chosen specifically
to exercise streak-with-gaps logic, multiple simultaneous theme/achievement unlocks, and week/month
boundary math. Interactive flows were driven end-to-end through the actual widgets (not just the
data layer): logging a session, completing a challenge, marking a resource done, adding/removing a
favorite, saving a note and finding it via Search, editing the study planner (autosave), toggling
accessibility settings, generating a PDF, and a full backup export → wipe → import round-trip. Two
real bugs were caught and fixed this way: a numpy-vs-JSON serialization error in the weekly
reflection cache, and a leftover dead-code branch in the hours-totals calculation.
