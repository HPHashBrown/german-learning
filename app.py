import datetime as dt
import json

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

import db
import intelligence as intel
import resources as res
import reports
from content import (
    THEMES, WORD_BANK, word_of_day, MINI_DICTIONARY, RECOMMENDATION_ROADMAP,
    TOPIC_FILTERS, recommendations_for_hours, QUOTES, quote_of_day,
    achievement_definitions,
)
from styles import inject_css, card_start, card_end, metric_html
from nlp_tools import analyze_with_claude, analyze_offline

st.set_page_config(
    page_title="Fluent Forest: German",
    page_icon="🌲",
    layout="wide",
    initial_sidebar_state="expanded",
)

db.init_db()
db.ensure_study_plan()

# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------

def unlocked_theme_list(profile):
    return [t.strip() for t in profile.get("unlocked_themes", "Neon Megacity").split(",") if t.strip()]


def check_theme_unlocks(total_hours, profile):
    unlocked = set(unlocked_theme_list(profile))
    newly = []
    for name, meta in THEMES.items():
        if total_hours >= meta["unlock_hours"] and name not in unlocked:
            unlocked.add(name)
            newly.append(name)
    if newly:
        db.set_profile("unlocked_themes", ",".join(sorted(unlocked)))
    return newly


def check_achievements(stats):
    unlocked_keys = db.get_unlocked_achievements()
    newly = []
    for a in achievement_definitions():
        if a["key"] not in unlocked_keys and a["check"](stats):
            db.unlock_achievement(a["key"])
            newly.append(a)
    return newly


def build_stats_snapshot():
    profile = db.get_profile()
    t = db.totals()
    saved_words_df = db.get_saved_words()
    return {
        "total_hours": t["total_hours"],
        "current_streak": int(profile.get("current_streak", "0") or 0),
        "longest_streak": int(profile.get("longest_streak", "0") or 0),
        "saved_words": len(saved_words_df),
        "themes_unlocked": len(unlocked_theme_list(profile)),
        "sessions": t["sessions"],
    }, profile, t


def cefr_estimate(total_hours: float) -> str:
    # Rough, widely-cited FSI-style bands adapted for informal self-study hours.
    bands = [
        (0, 50, "Pre-A1"), (50, 150, "A1"), (150, 300, "A2"),
        (300, 600, "B1"), (600, 1000, "B2"), (1000, 1600, "C1"),
        (1600, 999999, "C2 (approaching)"),
    ]
    for lo, hi, label in bands:
        if lo <= total_hours < hi:
            return label
    return "C2 (approaching)"


def hours_to_next_milestone(total_hours):
    for m in db.MILESTONES_HOURS:
        if total_hours < m:
            return m, m - total_hours
    return None, 0


CHALLENGE_TITLES_FLAT = [title for pool in intel.CHALLENGE_BANK.values() for title, _, _ in pool]


# ----------------------------------------------------------------------------
# Sidebar
# ----------------------------------------------------------------------------

profile = db.get_profile()
inject_css(
    profile.get("current_theme", "Neon Megacity"),
    font_size=profile.get("font_size", "Medium"),
    high_contrast=profile.get("high_contrast", "0") == "1",
    reduced_motion=profile.get("reduced_motion", "0") == "1",
    colorblind_mode=profile.get("colorblind_mode", "0") == "1",
    layout_density=profile.get("layout_density", "Spacious"),
)

# Auto-generate today's challenges and sync the timeline once per render.
intel.generate_daily_challenges()
intel.sync_timeline_events()

NAV_PAGES = [
    "🏠 Dashboard", "⏱️ Log Study Time", "🎯 Daily Challenges", "🌍 World Themes",
    "📖 Word of the Day", "🔍 Sentence Breakdown", "📚 Dictionary",
    "🧭 Recommendations", "📆 Study Planner", "🪞 Weekly Reflection",
    "🧬 Learning Profile", "🕰️ Timeline", "⭐ Favorites", "🔎 Search",
    "📅 Calendar", "🏆 Achievements", "📊 Statistics", "⚙️ Settings",
]

with st.sidebar:
    st.markdown("## 🌲 Fluent Forest")
    st.caption("German, immersively.")

    display_name = st.text_input("Your name", value=profile.get("display_name", "Sprachfreund"))
    if display_name != profile.get("display_name"):
        db.set_profile("display_name", display_name)

    page = st.radio("Navigate", NAV_PAGES, label_visibility="collapsed", key="ff_page")

    st.markdown("---")
    stats_snapshot, profile, totals = build_stats_snapshot()
    st.markdown(f"**Streak:** {stats_snapshot['current_streak']} 🔥  \n"
                f"**Total hours:** {totals['total_hours']}h  \n"
                f"**XP:** {int(float(profile.get('xp','0'))):,}")

    st.markdown("---")
    with st.expander("🔑 AI Analyzer (optional)"):
        st.caption(
            "The Sentence Breakdown tool uses the Claude API for real grammar "
            "analysis. Paste your Anthropic API key to enable it — it's kept "
            "only in this browser session, never saved to disk."
        )
        api_key = st.text_input("Anthropic API key", type="password", key="api_key_input")

    if profile.get("keyboard_shortcuts", "0") == "1":
        st.components.v1.html(
            """
            <script>
            const shortcuts = {'d':'🏠 Dashboard','l':'⏱️ Log Study Time','c':'🎯 Daily Challenges','f':'🔎 Search'};
            const handler = function(e) {
                const active = window.parent.document.activeElement;
                const tag = active ? active.tagName : '';
                if (tag === 'INPUT' || tag === 'TEXTAREA') { return; }
                const key = e.key.toLowerCase();
                if (shortcuts[key]) {
                    const label = shortcuts[key];
                    const labels = window.parent.document.querySelectorAll('label');
                    for (const el of labels) {
                        if (el.innerText && el.innerText.trim() === label) { el.click(); break; }
                    }
                }
            };
            if (!window.parent.__ffShortcutsBound) {
                window.parent.document.addEventListener('keydown', handler);
                window.parent.__ffShortcutsBound = true;
            }
            </script>
            """,
            height=0,
        )

# Fire achievement / theme checks once per render, after any state changes
newly_unlocked_themes = check_theme_unlocks(totals["total_hours"], profile)
newly_achievements = check_achievements(stats_snapshot)
db.maybe_earn_streak_freeze()

for t in newly_unlocked_themes:
    st.toast(f"🎉 New world unlocked: {t}!", icon="🌍")
for a in newly_achievements:
    st.toast(f"{a['emoji']} Achievement unlocked: {a['name']}!", icon="🏆")


# ----------------------------------------------------------------------------
# PAGE: Dashboard
# ----------------------------------------------------------------------------
if page == "🏠 Dashboard":
    theme = THEMES[profile.get("current_theme", "Neon Megacity")]

    st.markdown(
        f"""<div class="ff-hero">
        <div style="font-size:0.85rem;opacity:.75;text-transform:uppercase;letter-spacing:.1em;">
            {dt.date.today().strftime('%A, %d %B %Y')}
        </div>
        <h1 style="margin-top:0.3rem;">Willkommen zurück, {profile.get('display_name','Sprachfreund')} {theme['emoji']}</h1>
        <div class="ff-quote">„{quote_of_day()[0]}“ — {quote_of_day()[1]}</div>
        </div>""",
        unsafe_allow_html=True,
    )

    motivation_msgs = intel.personalized_motivation_messages()
    st.markdown(
        "".join(f'<span class="ff-pill">✨ {m}</span>' for m in motivation_msgs[:3]),
        unsafe_allow_html=True,
    )
    st.markdown("<div style='height:0.6rem;'></div>", unsafe_allow_html=True)

    adaptive = intel.adaptive_goal_suggestion()
    if adaptive:
        msg, suggested = adaptive
        c_a, c_b = st.columns([4, 1])
        with c_a:
            st.info(msg, icon="🎯")
        with c_b:
            if st.button("Apply", key="apply_adaptive_goal"):
                db.set_profile("daily_goal_minutes", suggested)
                st.rerun()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(metric_html("Current Streak", stats_snapshot["current_streak"], " days 🔥"), unsafe_allow_html=True)
    with c2:
        st.markdown(metric_html("Total Hours", totals["total_hours"], "h"), unsafe_allow_html=True)
    with c3:
        st.markdown(metric_html("This Week", totals["week_hours"], "h"), unsafe_allow_html=True)
    with c4:
        st.markdown(metric_html("This Month", totals["month_hours"], "h"), unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(metric_html("Estimated CEFR", cefr_estimate(totals["total_hours"])), unsafe_allow_html=True)
    with c2:
        st.markdown(metric_html("XP", f"{int(float(profile.get('xp','0'))):,}"), unsafe_allow_html=True)
    with c3:
        next_m, remaining = hours_to_next_milestone(totals["total_hours"])
        label = f"{remaining:.1f}h to {next_m}h" if next_m else "All milestones reached!"
        st.markdown(metric_html("Next Milestone", label), unsafe_allow_html=True)

    st.markdown("### 🔮 Progress Forecast")
    forecast = intel.progress_forecast()
    if forecast["next_level"]:
        fc1, fc2 = st.columns([2, 1])
        with fc1:
            st.markdown(
                f"You're **{forecast['pct_in_band']*100:.0f}%** through **{forecast['current_level']}**, "
                f"roughly **{forecast['hours_remaining']}h** away from **{forecast['next_level']}**-level "
                f"comprehension."
            )
            st.progress(forecast["pct_in_band"])
            if forecast["weekly_pace"] > 0:
                st.caption(
                    f"Recent pace: {forecast['weekly_pace']}h/week. "
                    f"At this pace: **{forecast['est_date_current_pace'].strftime('%d %b %Y')}**. "
                    f"At 25% faster: **{forecast['est_date_faster_pace'].strftime('%d %b %Y')}**."
                )
            else:
                st.caption("Log a few sessions this week to unlock a pace-based completion estimate.")
        with fc2:
            st.markdown(metric_html("Weekly Pace", forecast["weekly_pace"], "h/wk"), unsafe_allow_html=True)
    else:
        st.success("You've reached the top of our estimation scale (C2)! 🎉")

    st.markdown("### Today's Goal")
    goal_min = int(profile.get("daily_goal_minutes", "30") or 30)
    today_min = totals["today_minutes"]
    pct = min(1.0, today_min / goal_min) if goal_min else 0

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=today_min,
        number={"suffix": " min", "font": {"color": theme["text"]}},
        gauge={
            "axis": {"range": [0, max(goal_min, today_min, 1)], "tickcolor": theme["text"]},
            "bar": {"color": theme["accent"]},
            "bgcolor": "rgba(255,255,255,0.05)",
            "borderwidth": 0,
            "steps": [{"range": [0, goal_min], "color": "rgba(255,255,255,0.08)"}],
            "threshold": {"line": {"color": theme["accent2"], "width": 4},
                          "thickness": 0.85, "value": goal_min},
        },
        title={"text": f"Daily goal: {goal_min} min", "font": {"color": theme["text"], "size": 14}},
    ))
    fig.update_layout(height=260, margin=dict(l=20, r=20, t=50, b=10),
                       paper_bgcolor="rgba(0,0,0,0)", font_color=theme["text"])
    st.plotly_chart(fig, width='stretch')

    col1, col2 = st.columns([1, 1])
    with col1:
        card_start()
        st.markdown("#### 📖 Word of the Day")
        w = word_of_day()
        st.markdown(f"### {w['word']}")
        st.caption(f"/{w['ipa']}/  ·  gender: {w['gender']}  ·  plural: {w['plural']}")
        st.write(f"**Meaning:** {w['meaning']}")
        st.write(f"**Example:** _{w['example']}_")
        st.write(f"**Translation:** {w['translation']}")
        st.write(f"**Memory tip:** {w['tip']}")
        if st.button("💾 Save this word", key="dash_save_word"):
            db.save_word(w["word"], w["word"], w["meaning"], w["gender"], w["plural"], w["example"])
            st.success("Saved to your dictionary!")
        card_end()

    with col2:
        card_start()
        st.markdown("#### 🎯 Suggested Today")
        tier = recommendations_for_hours(totals["total_hours"])
        st.markdown(f"Based on your **{totals['total_hours']}h** logged — you're roughly at **{tier['level']}**.")
        for name, why in tier["items"][:3]:
            st.markdown(f"- **{name}** — {why}")
        st.caption("See the full Recommendations page for more.")
        card_end()

        card_start()
        st.markdown("#### 🌍 Current World")
        st.markdown(f"### {theme['emoji']} {profile.get('current_theme')}")
        st.caption(theme["blurb"])
        card_end()

    col3, col4 = st.columns([1, 1])
    with col3:
        card_start()
        st.markdown("#### 🎯 Today's Challenges")
        todays_challenges = db.get_challenges_for_date(dt.date.today().isoformat())
        icons = {"Easy": "🟢", "Medium": "🟡", "Hard": "🔴"}
        for c in todays_challenges:
            status = "✅" if c["completed"] else icons.get(c["difficulty"], "•")
            st.markdown(f"{status} **{c['title']}** ({c['xp_reward']} XP)")
        st.caption("Head to the Daily Challenges page to complete them.")
        card_end()

    with col4:
        insight = intel.session_insight()
        if insight:
            card_start()
            st.markdown("#### 📋 Today's Study Insight")
            for cat, minutes in insight["by_category"].items():
                st.markdown(f"- **{cat}:** {minutes:.0f} min")
            st.markdown(f"- **Weekly progress:** {insight['weekly_pct']}%")
            if insight["hours_to_next_level"] is not None:
                st.markdown(f"- **Hours until {insight['next_level']}:** {insight['hours_to_next_level']}")
            if insight["suggestion"]:
                st.info(insight["suggestion"], icon="💡")
            card_end()
        else:
            card_start()
            st.markdown("#### 📋 Today's Study Insight")
            st.caption("Log a session today to see your personalized insight here.")
            card_end()


# ----------------------------------------------------------------------------
# PAGE: Log Study Time
# ----------------------------------------------------------------------------
elif page == "⏱️ Log Study Time":
    st.markdown("## ⏱️ Log a Study Session")
    st.caption("Every minute counts toward your total, your streak, and your next world.")

    with st.form("log_session_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            session_date = st.date_input("Date", value=dt.date.today(), max_value=dt.date.today())
            category = st.selectbox("Category", db.CATEGORIES)
            minutes = st.number_input("Duration (minutes)", min_value=1, max_value=600, value=30, step=5)
        with c2:
            difficulty = st.select_slider("Difficulty", options=db.DIFFICULTIES, value="Comfortable")
            resource = st.text_input("Resource used (optional)", placeholder="e.g. Easy German Ep. 214")
            notes = st.text_area("Notes (optional)", placeholder="What did you learn today?")

        submitted = st.form_submit_button("✅ Log Session", width='stretch')
        if submitted:
            db.add_session(session_date.isoformat(), category, float(minutes), difficulty, resource, notes)
            st.success(f"Logged {minutes} minutes of {category}! Great work. 🎉")
            st.rerun()

    st.markdown("### Recent Sessions")
    df = db.get_all_sessions()
    if df.empty:
        st.info("No sessions logged yet — add your first one above!")
    else:
        show = df[["id", "date", "category", "minutes", "difficulty", "resource", "notes"]].head(25).copy()
        show["date"] = show["date"].dt.strftime("%Y-%m-%d")
        st.dataframe(show, width='stretch', hide_index=True)

        del_id = st.number_input("Delete session by ID", min_value=0, value=0, step=1)
        if st.button("🗑️ Delete") and del_id:
            db.delete_session(int(del_id))
            st.success(f"Deleted session {int(del_id)}.")
            st.rerun()

    st.markdown("### 📝 Study Notes")
    st.caption("Freeform notes — searchable from the Search page, saved instantly.")
    note_text = st.text_area("Add a note", key="note_input", placeholder="Anything you want to remember...")
    if st.button("Save Note") and note_text.strip():
        db.add_note(dt.date.today().isoformat(), note_text.strip())
        st.success("Note saved!")
        st.rerun()
    notes_df = db.get_notes()
    if not notes_df.empty:
        st.dataframe(notes_df[["date", "content"]].head(10), width='stretch', hide_index=True)


# ----------------------------------------------------------------------------
# PAGE: Daily Challenges
# ----------------------------------------------------------------------------
elif page == "🎯 Daily Challenges":
    st.markdown("## 🎯 Daily Challenges")
    st.caption("Three fresh challenges every day, scaled to your recent activity. Complete them for bonus XP.")

    today_str = dt.date.today().isoformat()
    challenges = intel.generate_daily_challenges()
    icons = {"Easy": "🟢", "Medium": "🟡", "Hard": "🔴"}

    for c in challenges:
        card_start()
        c1, c2 = st.columns([5, 1])
        with c1:
            st.markdown(f"### {icons.get(c['difficulty'], '•')} {c['difficulty']} — {c['title']}")
            st.write(c["description"])
            st.caption(f"Reward: {c['xp_reward']} XP")
        with c2:
            if c["completed"]:
                st.success("Done ✅")
            else:
                if st.button("Complete", key=f"complete_{c['id']}"):
                    xp = db.complete_challenge(c["id"])
                    if xp:
                        st.balloons()
                        st.success(f"+{xp} XP! Great work.")
                        st.rerun()
        card_end()

    stats = db.challenge_completion_stats()
    if stats["total"]:
        st.markdown("### Lifetime Challenge Stats")
        pct = stats["completed"] / stats["total"]
        st.progress(pct)
        st.caption(f"{stats['completed']} / {stats['total']} challenges completed ({pct*100:.0f}%)")


# ----------------------------------------------------------------------------
# PAGE: World Themes
# ----------------------------------------------------------------------------
elif page == "🌍 World Themes":
    st.markdown("## 🌍 World Themes")
    st.caption("Unlock new worlds as your logged hours grow. Switch anytime between unlocked worlds.")

    unlocked = unlocked_theme_list(profile)
    cols = st.columns(3)
    for i, (name, meta) in enumerate(THEMES.items()):
        with cols[i % 3]:
            is_unlocked = name in unlocked
            is_current = name == profile.get("current_theme")
            st.markdown(
                f"""<div class="ff-card" style="background:{meta['gradient']};
                    opacity:{1 if is_unlocked else 0.55};">
                    <div style="font-size:2rem;">{meta['emoji']}</div>
                    <h4 style="color:{meta['text']};margin:0.2rem 0;">{name}</h4>
                    <div style="color:{meta['text']};opacity:.85;font-size:0.85rem;">{meta['blurb']}</div>
                    <div style="margin-top:0.6rem;color:{meta['text']};font-size:0.78rem;">
                        {'✅ Unlocked' if is_unlocked else f"🔒 Unlocks at {meta['unlock_hours']}h"}
                    </div>
                </div>""",
                unsafe_allow_html=True,
            )
            if is_unlocked and not is_current:
                if st.button(f"Switch to {name}", key=f"switch_{name}"):
                    db.set_profile("current_theme", name)
                    st.rerun()
            elif is_current:
                st.success("Currently active", icon="✨")


# ----------------------------------------------------------------------------
# PAGE: Word of the Day (full archive)
# ----------------------------------------------------------------------------
elif page == "📖 Word of the Day":
    st.markdown("## 📖 Word of the Day")
    w = word_of_day()
    card_start()
    st.markdown(f"# {w['word']}")
    st.caption(f"IPA: /{w['ipa']}/")
    c1, c2 = st.columns(2)
    with c1:
        st.write(f"**Gender:** {w['gender']}")
        st.write(f"**Plural:** {w['plural']}")
        st.write(f"**Meaning:** {w['meaning']}")
        st.write(f"**Related words:** {w['related']}")
    with c2:
        st.write(f"**Example:** _{w['example']}_")
        st.write(f"**Translation:** {w['translation']}")
        st.write(f"**Memory tip:** 💡 {w['tip']}")
    if st.button("💾 Save to Dictionary"):
        db.save_word(w["word"], w["word"], w["meaning"], w["gender"], w["plural"], w["example"])
        st.success("Saved!")
    card_end()

    st.markdown("### Word Archive")
    for word in WORD_BANK:
        with st.expander(f"{word['word']} — {word['meaning']}"):
            st.write(f"IPA: /{word['ipa']}/ · Gender: {word['gender']} · Plural: {word['plural']}")
            st.write(f"Example: _{word['example']}_ → {word['translation']}")
            st.write(f"Tip: {word['tip']}")
            if st.button("Save", key=f"save_archive_{word['word']}"):
                db.save_word(word["word"], word["word"], word["meaning"], word["gender"], word["plural"], word["example"])
                st.success("Saved!")


# ----------------------------------------------------------------------------
# PAGE: Sentence Breakdown
# ----------------------------------------------------------------------------
elif page == "🔍 Sentence Breakdown":
    st.markdown("## 🔍 Sentence Breakdown Tool")
    st.caption("Paste a German sentence to see it decomposed word-by-word, with grammar and translation notes.")

    sentence = st.text_area(
        "German sentence",
        value="Ich habe gestern mit meiner Freundin im Park gesprochen.",
        height=90,
    )
    key_from_sidebar = st.session_state.get("api_key_input", "")
    use_ai = bool(key_from_sidebar)

    if not use_ai:
        st.info(
            "No Anthropic API key set — using offline mode (limited to a small "
            "built-in dictionary, no grammar synthesis). Add a key in the sidebar "
            "under **AI Analyzer** for full grammar analysis.",
            icon="ℹ️",
        )

    if st.button("Analyze Sentence", type="primary"):
        if not sentence.strip():
            st.warning("Please enter a sentence.")
        else:
            with st.spinner("Analyzing..."):
                try:
                    if use_ai:
                        result = analyze_with_claude(sentence.strip(), key_from_sidebar)
                    else:
                        result = analyze_offline(sentence.strip())
                except Exception as e:
                    st.error(f"AI analysis failed ({e}). Falling back to offline mode.")
                    result = analyze_offline(sentence.strip())

            st.markdown("### Word-by-Word Breakdown")
            wdf = pd.DataFrame(result.get("words", []))
            if not wdf.empty:
                wdf = wdf.rename(columns={
                    "word": "Word", "base_form": "Base Form",
                    "meaning": "Meaning", "grammar": "Grammar",
                })
                st.dataframe(wdf, width='stretch', hide_index=True)

            c1, c2 = st.columns(2)
            with c1:
                card_start()
                st.markdown("**Cases**")
                st.write(result.get("cases_explained", "—"))
                st.markdown("**Word Order**")
                st.write(result.get("word_order_notes", "—"))
                st.markdown("**Separable Verbs**")
                st.write(result.get("separable_verbs", "—"))
                card_end()
            with c2:
                card_start()
                st.markdown("**Idioms**")
                st.write(result.get("idioms", "—"))
                st.markdown("**Literal Translation**")
                st.write(result.get("literal_translation", "—"))
                st.markdown("**Natural Translation**")
                st.write(result.get("natural_translation", "—"))
                card_end()

            if result.get("difficulty_notes"):
                st.info(result["difficulty_notes"], icon="🎓")


# ----------------------------------------------------------------------------
# PAGE: Dictionary
# ----------------------------------------------------------------------------
elif page == "📚 Dictionary":
    st.markdown("## 📚 Your Smart Dictionary")

    tab1, tab2 = st.tabs(["Saved Words", "Quick Lookup"])

    with tab1:
        words_df = db.get_saved_words()
        if words_df.empty:
            st.info("No saved words yet. Save words from the Word of the Day or Sentence Breakdown pages.")
        else:
            collections = ["All"] + sorted(words_df["collection"].dropna().unique().tolist())
            chosen = st.selectbox("Collection", collections)
            view = words_df if chosen == "All" else words_df[words_df["collection"] == chosen]
            st.dataframe(
                view[["id", "word", "meaning", "gender", "plural", "example", "collection"]],
                width='stretch', hide_index=True,
            )
            del_id = st.number_input("Delete word by ID", min_value=0, value=0, step=1)
            if st.button("🗑️ Delete word") and del_id:
                db.delete_word(int(del_id))
                st.rerun()

    with tab2:
        st.caption("Searches the small built-in reference dictionary (also used by offline sentence analysis).")
        query = st.text_input("Look up a German word")
        if query:
            entry = MINI_DICTIONARY.get(query) or MINI_DICTIONARY.get(query.lower())
            if entry:
                st.markdown(f"### {query}")
                st.write(f"**Meaning:** {entry['meaning']}")
                st.write(f"**Gender:** {entry['gender']}  ·  **CEFR:** {entry['cefr']}")
                st.write(f"**Example:** _{entry['example']}_")
                st.write(f"**Synonyms:** {entry['synonyms']}")
                st.write(f"**Compound words:** {entry['compound']}")
                if st.button("💾 Save this word"):
                    db.save_word(query, query, entry["meaning"], entry["gender"], "—", entry["example"])
                    st.success("Saved!")
            else:
                st.warning("Not found in the built-in dictionary. Try the Sentence Breakdown tool with an AI key for broader coverage.")


# ----------------------------------------------------------------------------
# PAGE: Recommendations
# ----------------------------------------------------------------------------
elif page == "🧭 Recommendations":
    st.markdown("## 🧭 Personalized Resource Engine")
    st.caption(
        "Recommendations adapt to your logged hours and topic interests, and avoid repeating "
        "resources you've already completed. Links go to the resource's real homepage/channel "
        "(not a single video/article) since those stay valid — no dead links."
    )

    hours = totals["total_hours"]
    tier = recommendations_for_hours(hours)
    st.markdown(f"### You've logged **{hours}h** — estimated readiness: **{tier['level']}**")

    topic_filters = st.multiselect("Filter by topic", TOPIC_FILTERS, key="rec_topic_filters")
    completed_ids = db.completed_resource_ids()
    picks = res.resources_for(hours, topics_filter=topic_filters, exclude_ids=set(), limit=8)

    for r in picks:
        db.mark_resource_shown(r["id"])
        already_done = r["id"] in completed_ids
        card_start()
        c1, c2 = st.columns([4, 1])
        with c1:
            st.markdown(f"#### {r['title']} {'✅' if already_done else ''}")
            st.write(r["desc"])
            st.caption(
                f"Category: {r['category']} · Difficulty: {r['difficulty']} · "
                f"~{r['duration']} · Est. comprehension: {r['comprehension_pct']}% · "
                f"Topics: {', '.join(r['topics'])}"
            )
            st.caption(res.why_selected(r, hours))
        with c2:
            st.link_button("Open ↗", r["url"], width='stretch')
            if st.button("Mark done", key=f"done_{r['id']}"):
                db.mark_resource_completed(r["id"])
                st.rerun()
            if st.button("⭐ Favorite", key=f"fav_{r['id']}"):
                db.add_favorite(r["category"], r["title"], r["url"], r["desc"])
                st.toast("Added to Favorites!")
        card_end()

    st.markdown("### Full Roadmap (by hours)")
    for t in RECOMMENDATION_ROADMAP:
        active = t is tier
        label = f"**{t['level']}** ({t['min_hours']}–{t['max_hours'] if t['max_hours'] < 999999 else '∞'}h)"
        with st.expander(f"{'👉 ' if active else ''}{label}", expanded=active):
            for name, why in t["items"]:
                st.markdown(f"- **{name}** — {why}")


# ----------------------------------------------------------------------------
# PAGE: Study Planner
# ----------------------------------------------------------------------------
elif page == "📆 Study Planner":
    st.markdown("## 📆 Smart Study Planner")
    st.caption("A weekly rhythm you can edit anytime. Missed a day? Just study when you can — nothing resets.")

    plan = db.get_study_plan()
    for row in plan:
        c1, c2, c3 = st.columns([1.2, 3, 1.5])
        with c1:
            st.markdown(f"**{row['day_of_week']}**")
        with c2:
            new_activity = st.text_input(
                "Activity", value=row["activity"] or "", key=f"plan_act_{row['day_of_week']}",
                label_visibility="collapsed",
            )
        with c3:
            new_minutes = st.number_input(
                "Minutes", value=int(row["minutes"] or 0), min_value=0, max_value=300, step=5,
                key=f"plan_min_{row['day_of_week']}", label_visibility="collapsed",
            )
        if new_activity != row["activity"] or new_minutes != row["minutes"]:
            db.set_study_plan_day(row["day_of_week"], new_activity, new_minutes)

    st.caption("Changes save automatically — no submit button needed.")

    st.markdown("### This Week So Far")
    df = db.get_all_sessions()
    if not df.empty:
        today = dt.date.today()
        week_start = today - dt.timedelta(days=today.weekday())
        week_df = df[df["date"] >= pd.Timestamp(week_start)]
        done_days = set(week_df["date"].dt.day_name())
        cols = st.columns(7)
        order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        for i, day in enumerate(order):
            with cols[i]:
                status = "✅" if day in done_days else ("📅" if today.strftime("%A") == day else "⚪")
                st.markdown(f"<div style='text-align:center;'>{status}<br><small>{day[:3]}</small></div>",
                             unsafe_allow_html=True)


# ----------------------------------------------------------------------------
# PAGE: Weekly Reflection
# ----------------------------------------------------------------------------
elif page == "🪞 Weekly Reflection":
    st.markdown("## 🪞 Weekly AI Reflection")
    st.caption("A personalized report generated at the end of each week from your actual logged data.")

    past_week_start = intel.most_recent_complete_week_start()
    report = intel.generate_weekly_reflection(past_week_start)

    if not report:
        st.info("No sessions logged in the most recent complete week yet — log some study time to unlock your first report!")
    else:
        card_start()
        st.markdown(f"### Week of {report['week_start']}")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(metric_html("Hours this week", report["total_hours"], "h"), unsafe_allow_html=True)
        with c2:
            trend = "📈 improved" if report["improved"] else "📉 lighter"
            st.markdown(metric_html("Vs. previous week", trend), unsafe_allow_html=True)
        with c3:
            st.markdown(metric_html("Consistency", f"{report['consistency_pct']}%"), unsafe_allow_html=True)

        st.markdown(f"**Strongest skill:** {report['strongest_skill']}")
        st.markdown(f"**Weakest / least-practiced skill:** {report['weakest_skill']}")
        st.markdown(f"**Most productive day:** {report['most_productive_day']}")
        st.markdown(f"**Most productive method:** {report['most_productive_method']}")
        if report["milestone_reached"]:
            st.success(f"🏅 You crossed the {report['milestone_reached']}-hour milestone this week!")
        st.markdown(f"**Recommended focus next week:** {report['recommended_focus']}")
        st.info(f"**Suggested challenge:** {report['suggested_challenge']}", icon="🎯")
        card_end()

    past_reports = db.get_all_weekly_reflections()
    if len(past_reports) > 1:
        st.markdown("### Past Reports")
        for week_start_str, r in past_reports[1:]:
            with st.expander(f"Week of {week_start_str} — {r['total_hours']}h"):
                st.write(f"Strongest: {r['strongest_skill']} · Focus next: {r['recommended_focus']}")


# ----------------------------------------------------------------------------
# PAGE: Learning Profile
# ----------------------------------------------------------------------------
elif page == "🧬 Learning Profile":
    st.markdown("## 🧬 Personal Learning Profile")
    st.caption("Continuously derived from your actual study sessions — the more you log, the sharper this gets.")

    lp = intel.derive_learning_profile()
    if not lp:
        st.info("Log a few sessions to build your learning profile.")
    else:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(metric_html("Favorite method (most sessions)", lp["favorite_method"]), unsafe_allow_html=True)
            st.markdown(metric_html("Average session length", lp["avg_session_minutes"], " min"), unsafe_allow_html=True)
            st.markdown(metric_html("Favorite study day", lp["favorite_day"]), unsafe_allow_html=True)
        with c2:
            st.markdown(metric_html("Most successful method (most hours)", lp["most_successful_method"]), unsafe_allow_html=True)
            st.markdown(metric_html("Longest single session", f"{lp['longest_session_minutes']:.0f}", f" min ({lp['longest_session_category']})"), unsafe_allow_html=True)
            st.markdown(metric_html("Total sessions logged", lp["total_sessions"]), unsafe_allow_html=True)

        st.caption(
            "Note: 'most difficult grammar topics' and 'preferred learning times of day' would need "
            "richer session metadata (e.g. time-of-day logging, per-session difficulty feedback on "
            "grammar points) than is currently captured — everything shown above is derived from what "
            "you've actually logged, nothing is guessed."
        )


# ----------------------------------------------------------------------------
# PAGE: Timeline
# ----------------------------------------------------------------------------
elif page == "🕰️ Timeline":
    st.markdown("## 🕰️ Your Learning Timeline")
    st.caption("A chronological record of your journey — milestones are recorded automatically as you reach them.")

    timeline_df = db.get_timeline()
    if timeline_df.empty:
        st.info("Your timeline will start filling in as soon as you log your first session.")
    else:
        for _, row in timeline_df.sort_values("occurred_at", ascending=False).iterrows():
            card_start()
            occurred = pd.to_datetime(row["occurred_at"]).strftime("%d %B %Y")
            st.markdown(f"#### {row['icon']} {row['title']}")
            st.caption(occurred)
            if row["description"]:
                st.write(row["description"])
            card_end()


# ----------------------------------------------------------------------------
# PAGE: Favorites
# ----------------------------------------------------------------------------
elif page == "⭐ Favorites":
    st.markdown("## ⭐ Favorites Library")
    st.caption("Bookmark anything useful — resources, articles, your own notes about grammar points, etc.")

    with st.expander("➕ Add a favorite manually"):
        f_type = st.selectbox("Type", ["video", "article", "podcast", "book", "grammar", "other"])
        f_title = st.text_input("Title")
        f_url = st.text_input("URL (optional)")
        f_notes = st.text_area("Notes (optional)")
        if st.button("Save Favorite") and f_title.strip():
            db.add_favorite(f_type, f_title.strip(), f_url.strip(), f_notes.strip())
            st.success("Saved!")
            st.rerun()

    favs = db.get_favorites()
    if favs.empty:
        st.info("No favorites yet. Add resources from the Recommendations page or manually above.")
    else:
        types = ["All"] + sorted(favs["item_type"].unique().tolist())
        chosen_type = st.selectbox("Filter by type", types)
        view = favs if chosen_type == "All" else favs[favs["item_type"] == chosen_type]
        for _, row in view.iterrows():
            card_start()
            c1, c2 = st.columns([4, 1])
            with c1:
                st.markdown(f"#### {row['title']}")
                st.caption(f"Type: {row['item_type']}")
                if row["notes"]:
                    st.write(row["notes"])
            with c2:
                if row["url"]:
                    st.link_button("Open ↗", row["url"], width='stretch')
                if st.button("Remove", key=f"remove_fav_{row['id']}"):
                    db.delete_favorite(int(row["id"]))
                    st.rerun()
            card_end()


# ----------------------------------------------------------------------------
# PAGE: Search
# ----------------------------------------------------------------------------
elif page == "🔎 Search":
    st.markdown("## 🔎 Search Everything")
    st.caption("Fuzzy search across saved words, notes, favorites, achievements, sessions, and challenges.")

    query = st.text_input("Search", placeholder="Type to search...")

    def fuzzy_match(needle: str, haystack: str) -> bool:
        if not needle:
            return False
        n, h = needle.lower(), (haystack or "").lower()
        if n in h:
            return True
        # simple subsequence fuzzy match for typo tolerance
        it = iter(h)
        return all(ch in it for ch in n)

    if query:
        results_found = False

        words_df = db.get_saved_words()
        word_hits = words_df[words_df.apply(
            lambda r: fuzzy_match(query, str(r["word"])) or fuzzy_match(query, str(r["meaning"])), axis=1
        )] if not words_df.empty else words_df
        if not word_hits.empty:
            results_found = True
            st.markdown(f"### 📚 Saved Words ({len(word_hits)})")
            st.dataframe(word_hits[["word", "meaning", "collection"]], width='stretch', hide_index=True)

        notes_df = db.get_notes()
        note_hits = notes_df[notes_df["content"].apply(lambda c: fuzzy_match(query, c))] if not notes_df.empty else notes_df
        if not note_hits.empty:
            results_found = True
            st.markdown(f"### 📝 Notes ({len(note_hits)})")
            st.dataframe(note_hits[["date", "content"]], width='stretch', hide_index=True)

        favs_df = db.get_favorites()
        fav_hits = favs_df[favs_df["title"].apply(lambda t: fuzzy_match(query, t))] if not favs_df.empty else favs_df
        if not fav_hits.empty:
            results_found = True
            st.markdown(f"### ⭐ Favorites ({len(fav_hits)})")
            st.dataframe(fav_hits[["title", "item_type", "url"]], width='stretch', hide_index=True)

        ach_hits = [a for a in achievement_definitions()
                    if fuzzy_match(query, a["name"]) or fuzzy_match(query, a["desc"])]
        if ach_hits:
            results_found = True
            st.markdown(f"### 🏆 Achievements ({len(ach_hits)})")
            for a in ach_hits:
                st.markdown(f"- {a['emoji']} **{a['name']}** — {a['desc']}")

        sessions_df = db.get_all_sessions()
        session_hits = sessions_df[sessions_df.apply(
            lambda r: fuzzy_match(query, str(r["category"])) or fuzzy_match(query, str(r["resource"]))
            or fuzzy_match(query, str(r["notes"])), axis=1
        )] if not sessions_df.empty else sessions_df
        if not session_hits.empty:
            results_found = True
            st.markdown(f"### ⏱️ Sessions ({len(session_hits)})")
            show = session_hits[["date", "category", "minutes", "resource", "notes"]].head(20).copy()
            show["date"] = show["date"].dt.strftime("%Y-%m-%d")
            st.dataframe(show, width='stretch', hide_index=True)

        challenge_hits = [c for c in CHALLENGE_TITLES_FLAT if fuzzy_match(query, c)]
        if challenge_hits:
            results_found = True
            st.markdown(f"### 🎯 Challenge Types ({len(challenge_hits)})")
            for c in challenge_hits:
                st.markdown(f"- {c}")

        if not results_found:
            st.warning("No matches found.")
    else:
        st.caption("Start typing above to search across your entire learning history.")


# ----------------------------------------------------------------------------
# PAGE: Calendar
# ----------------------------------------------------------------------------
elif page == "📅 Calendar":
    st.markdown("## 📅 Calendar View")
    st.caption("Click a date below to see everything that happened that day.")

    df = db.get_all_sessions()
    if df.empty:
        st.info("Log some sessions to populate your calendar.")
    else:
        month_options = sorted(df["date"].dt.to_period("M").unique(), reverse=True)
        month_labels = [str(m) for m in month_options]
        chosen_month = st.selectbox("Month", month_labels)
        month_df = df[df["date"].dt.to_period("M").astype(str) == chosen_month]

        by_day = month_df.groupby(month_df["date"].dt.date)["hours"].sum()
        achievements_df_dates = set()  # achievements have no per-day date column; skipped intentionally

        import calendar as cal
        year, mo = map(int, chosen_month.split("-"))
        st.markdown(f"### {cal.month_name[mo]} {year}")
        weeks = cal.monthcalendar(year, mo)
        header_cols = st.columns(7)
        for i, d in enumerate(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]):
            header_cols[i].markdown(f"**{d}**")
        for week in weeks:
            cols = st.columns(7)
            for i, day_num in enumerate(week):
                with cols[i]:
                    if day_num == 0:
                        st.write("")
                    else:
                        the_date = dt.date(year, mo, day_num)
                        hrs = by_day.get(the_date, 0.0)
                        marker = "🟩" if hrs > 0 else "⬜"
                        st.markdown(f"{marker} **{day_num}**")
                        if hrs > 0:
                            st.caption(f"{hrs:.1f}h")

        st.markdown("### Day Detail")
        picked = st.date_input("Pick a date to inspect", value=dt.date.today())
        day_sessions = df[df["date"] == pd.Timestamp(picked)]
        if day_sessions.empty:
            st.caption("No sessions logged on this date.")
        else:
            show = day_sessions[["category", "minutes", "difficulty", "resource", "notes"]]
            st.dataframe(show, width='stretch', hide_index=True)


# ----------------------------------------------------------------------------
# PAGE: Achievements
# ----------------------------------------------------------------------------
elif page == "🏆 Achievements":
    st.markdown("## 🏆 Achievements")
    unlocked_keys = db.get_unlocked_achievements()
    defs = achievement_definitions()
    unlocked_count = sum(1 for d in defs if d["key"] in unlocked_keys)
    st.progress(unlocked_count / len(defs))
    st.caption(f"{unlocked_count} / {len(defs)} unlocked")

    badge_html = "<div style='display:flex;flex-wrap:wrap;'>"
    for a in defs:
        locked_cls = "" if a["key"] in unlocked_keys else "locked"
        badge_html += f"""
        <div class="ff-badge {locked_cls}" title="{a['desc']}">
            <div class="emoji">{a['emoji']}</div>
            <div class="name">{a['name']}</div>
        </div>"""
    badge_html += "</div>"
    st.markdown(badge_html, unsafe_allow_html=True)

    st.markdown("### Details")
    for a in defs:
        status = "✅" if a["key"] in unlocked_keys else "🔒"
        st.markdown(f"{status} **{a['name']}** — {a['desc']}")

    st.markdown("### Milestones")
    milestone_cols = st.columns(4)
    for i, m in enumerate(db.MILESTONES_HOURS):
        reached = totals["total_hours"] >= m
        with milestone_cols[i % 4]:
            st.markdown(
                f"""<div class="ff-card" style="text-align:center;opacity:{1 if reached else 0.4};">
                <div style="font-size:1.5rem;">{'🏅' if reached else '⚪'}</div>
                <b>{m}h</b></div>""",
                unsafe_allow_html=True,
            )


# ----------------------------------------------------------------------------
# PAGE: Statistics
# ----------------------------------------------------------------------------
elif page == "📊 Statistics":
    st.markdown("## 📊 Statistics")
    df = db.get_all_sessions()
    theme = THEMES[profile.get("current_theme", "Neon Megacity")]

    if df.empty:
        st.info("Log some study sessions to see your statistics here.")
    else:
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(metric_html("Sessions", len(df)), unsafe_allow_html=True)
        with c2:
            st.markdown(metric_html("Avg session", f"{df['minutes'].mean():.0f}", " min"), unsafe_allow_html=True)
        with c3:
            fav = df.groupby("category")["minutes"].sum().idxmax()
            st.markdown(metric_html("Favorite activity", fav), unsafe_allow_html=True)
        with c4:
            fav_day = df["date"].dt.day_name().value_counts().idxmax()
            st.markdown(metric_html("Most productive day", fav_day), unsafe_allow_html=True)

        st.markdown("### Study Calendar Heatmap")
        daily = df.groupby(df["date"].dt.date)["hours"].sum().reset_index()
        daily.columns = ["date", "hours"]
        daily["date"] = pd.to_datetime(daily["date"])
        daily["week"] = daily["date"].dt.isocalendar().week
        daily["weekday"] = daily["date"].dt.day_name()
        order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        pivot = daily.pivot_table(index="weekday", columns="week", values="hours", aggfunc="sum").reindex(order)
        fig_heat = px.imshow(
            pivot, color_continuous_scale=[[0, "rgba(255,255,255,0.05)"], [1, theme["accent"]]],
            aspect="auto", labels=dict(color="Hours"),
        )
        fig_heat.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                                font_color=theme["text"], height=320)
        st.plotly_chart(fig_heat, width='stretch')

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Hours by Category")
            cat = df.groupby("category")["hours"].sum().reset_index().sort_values("hours", ascending=False)
            fig_pie = px.pie(cat, names="category", values="hours", hole=0.5)
            fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color=theme["text"], height=350)
            st.plotly_chart(fig_pie, width='stretch')
        with col2:
            st.markdown("### Weekly Trend")
            weekly = df.set_index("date").resample("W")["hours"].sum().reset_index()
            fig_line = px.bar(weekly, x="date", y="hours")
            fig_line.update_traces(marker_color=theme["accent"])
            fig_line.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                                    font_color=theme["text"], height=350)
            st.plotly_chart(fig_line, width='stretch')

        st.markdown("### Monthly Trend")
        monthly = df.set_index("date").resample("ME")["hours"].sum().reset_index()
        fig_month = px.area(monthly, x="date", y="hours")
        fig_month.update_traces(line_color=theme["accent2"])
        fig_month.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                                 font_color=theme["text"], height=320)
        st.plotly_chart(fig_month, width='stretch')

        st.markdown(f"**Longest streak:** {stats_snapshot['longest_streak']} days")


# ----------------------------------------------------------------------------
# PAGE: Settings
# ----------------------------------------------------------------------------
elif page == "⚙️ Settings":
    st.markdown("## ⚙️ Settings")

    st.markdown("### Daily Goal")
    goal = st.select_slider(
        "Daily goal", options=[15, 30, 45, 60, 120],
        value=int(profile.get("daily_goal_minutes", "30") or 30),
        format_func=lambda m: f"{m} min" if m < 60 else f"{m//60} hr",
        key="settings_goal_slider",
    )
    if goal != int(profile.get("daily_goal_minutes", "30") or 30):
        db.set_profile("daily_goal_minutes", goal)
        st.toast("Daily goal saved!")

    adaptive = intel.adaptive_goal_suggestion()
    if adaptive:
        st.info(adaptive[0], icon="🎯")

    st.markdown("---")
    st.markdown(f"**Streak Freeze tokens:** {profile.get('streak_freeze_tokens','0')} 🧊")
    st.caption("Earned automatically every 7-day streak. Auto-applied to cover a single missed day.")

    st.markdown("---")
    st.markdown("### ♿ Accessibility & Customization")
    st.caption("All changes save instantly and apply across the whole app.")

    ac1, ac2 = st.columns(2)
    with ac1:
        font_size = st.select_slider(
            "Font size", options=["Small", "Medium", "Large", "Extra Large"],
            value=profile.get("font_size", "Medium"), key="settings_font_size",
        )
        layout_density = st.radio(
            "Layout density", ["Spacious", "Compact"],
            index=0 if profile.get("layout_density", "Spacious") == "Spacious" else 1,
            key="settings_density", horizontal=True,
        )
    with ac2:
        high_contrast = st.toggle("High-contrast mode", value=profile.get("high_contrast", "0") == "1", key="settings_hc")
        reduced_motion = st.toggle("Reduced motion", value=profile.get("reduced_motion", "0") == "1", key="settings_rm")
        colorblind_mode = st.toggle("Color-blind-friendly palette", value=profile.get("colorblind_mode", "0") == "1", key="settings_cb")

    changed = False
    if font_size != profile.get("font_size", "Medium"):
        db.set_profile("font_size", font_size); changed = True
    if layout_density != profile.get("layout_density", "Spacious"):
        db.set_profile("layout_density", layout_density); changed = True
    if str(int(high_contrast)) != profile.get("high_contrast", "0"):
        db.set_profile("high_contrast", int(high_contrast)); changed = True
    if str(int(reduced_motion)) != profile.get("reduced_motion", "0"):
        db.set_profile("reduced_motion", int(reduced_motion)); changed = True
    if str(int(colorblind_mode)) != profile.get("colorblind_mode", "0"):
        db.set_profile("colorblind_mode", int(colorblind_mode)); changed = True
    if changed:
        st.rerun()

    st.markdown("---")
    st.markdown("### ⌨️ Keyboard Shortcuts")
    shortcuts_enabled = st.toggle(
        "Enable keyboard shortcuts (beta)",
        value=profile.get("keyboard_shortcuts", "0") == "1",
        key="settings_shortcuts",
        help="Best-effort: jumps to a page by simulating a click on the sidebar nav. "
             "May not work in every browser."
    )
    if str(int(shortcuts_enabled)) != profile.get("keyboard_shortcuts", "0"):
        db.set_profile("keyboard_shortcuts", int(shortcuts_enabled))
        st.rerun()

    with st.expander("Shortcut reference"):
        st.markdown(
            "- **D** → Dashboard\n"
            "- **L** → Log Study Time\n"
            "- **C** → Daily Challenges\n"
            "- **F** → Search\n"
            "- **Esc** → Unfocus the current field\n\n"
            "Shortcuts are ignored while typing in a text field."
        )

    st.markdown("---")
    st.markdown("### 💾 Data Export & Backup")

    exp1, exp2, exp3 = st.columns(3)
    with exp1:
        df_all = db.get_all_sessions()
        if not df_all.empty:
            st.download_button(
                "⬇️ Sessions (CSV)",
                df_all.to_csv(index=False).encode("utf-8"),
                file_name="fluent_forest_sessions.csv",
                mime="text/csv",
                width='stretch',
            )
    with exp2:
        full_export = db.export_all_data()
        st.download_button(
            "⬇️ Full Backup (JSON)",
            json.dumps(full_export, indent=2, default=str).encode("utf-8"),
            file_name=f"fluent_forest_backup_{dt.date.today().isoformat()}.json",
            mime="application/json",
            width='stretch',
        )
    with exp3:
        if st.button("📄 Generate PDF Report", width='stretch'):
            pdf_bytes = reports.build_progress_report_pdf(profile)
            st.session_state["pdf_report_bytes"] = pdf_bytes
        if "pdf_report_bytes" in st.session_state:
            st.download_button(
                "⬇️ Download PDF Report",
                st.session_state["pdf_report_bytes"],
                file_name=f"fluent_forest_report_{dt.date.today().isoformat()}.pdf",
                mime="application/pdf",
                width='stretch',
            )

    st.markdown("#### Restore from Backup")
    st.caption("Import a previously exported JSON backup. 'Merge' keeps your current data and adds anything missing; 'Replace' wipes current data first.")
    uploaded = st.file_uploader("Upload backup JSON", type=["json"])
    import_mode = st.radio("Import mode", ["Merge", "Replace"], horizontal=True, key="import_mode")
    if uploaded is not None:
        if st.button("Restore Backup", type="primary"):
            try:
                data = json.load(uploaded)
                db.import_all_data(data, mode="merge" if import_mode == "Merge" else "replace")
                st.success("Backup restored! Reloading...")
                st.rerun()
            except Exception as e:
                st.error(f"Could not restore backup: {e}")

    st.markdown("---")
    st.caption(f"Database file: `{db.DB_PATH.name}` (local SQLite — all your data stays on this machine, "
               f"and everything above autosaves — there's no manual 'Save' button anywhere in the app).")
