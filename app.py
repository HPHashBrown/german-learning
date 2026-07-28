import datetime as dt

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

import db
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


# ----------------------------------------------------------------------------
# Sidebar
# ----------------------------------------------------------------------------

profile = db.get_profile()
inject_css(profile.get("current_theme", "Neon Megacity"))

with st.sidebar:
    st.markdown("## 🌲 Fluent Forest")
    st.caption("German, immersively.")

    display_name = st.text_input("Your name", value=profile.get("display_name", "Sprachfreund"))
    if display_name != profile.get("display_name"):
        db.set_profile("display_name", display_name)

    page = st.radio(
        "Navigate",
        [
            "🏠 Dashboard", "⏱️ Log Study Time", "🌍 World Themes",
            "📖 Word of the Day", "🔍 Sentence Breakdown", "📚 Dictionary",
            "🎯 Recommendations", "🏆 Achievements", "📊 Statistics", "⚙️ Settings",
        ],
        label_visibility="collapsed",
    )

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
elif page == "🎯 Recommendations":
    st.markdown("## 🎯 Content Recommendation Engine")
    st.caption("Recommendations are driven by your cumulative logged hours, not a generic level label.")

    hours = totals["total_hours"]
    tier = recommendations_for_hours(hours)
    st.markdown(f"### You've logged **{hours}h** — estimated readiness: **{tier['level']}**")

    filters = st.multiselect("Filter by topic (affects future content, informational for now)", TOPIC_FILTERS)

    for name, why in tier["items"]:
        card_start()
        st.markdown(f"#### {name}")
        st.write(why)
        card_end()

    st.markdown("### Full Roadmap")
    for t in RECOMMENDATION_ROADMAP:
        active = t is tier
        label = f"**{t['level']}** ({t['min_hours']}–{t['max_hours'] if t['max_hours'] < 999999 else '∞'}h)"
        with st.expander(f"{'👉 ' if active else ''}{label}", expanded=active):
            for name, why in t["items"]:
                st.markdown(f"- **{name}** — {why}")


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

    goal = st.select_slider(
        "Daily goal", options=[15, 30, 45, 60, 120],
        value=int(profile.get("daily_goal_minutes", "30") or 30),
        format_func=lambda m: f"{m} min" if m < 60 else f"{m//60} hr",
    )
    if st.button("Save daily goal"):
        db.set_profile("daily_goal_minutes", goal)
        st.success("Saved!")

    st.markdown("---")
    st.markdown(f"**Streak Freeze tokens:** {profile.get('streak_freeze_tokens','0')} 🧊")
    st.caption("Earned automatically every 7-day streak. Auto-applied to cover a single missed day.")

    st.markdown("---")
    st.markdown("### Data")
    df_all = db.get_all_sessions()
    if not df_all.empty:
        st.download_button(
            "⬇️ Export sessions as CSV",
            df_all.to_csv(index=False).encode("utf-8"),
            file_name="fluent_forest_sessions.csv",
            mime="text/csv",
        )
    st.caption(f"Database file: `{db.DB_PATH.name}` (local SQLite — all your data stays on this machine).")
