"""All the 'smart' logic for Phase 2: daily challenges, progress forecasting,
weekly reflections, adaptive goal suggestions, and personalized motivation.

Deliberately rule-based and transparent rather than a black box — every
number shown to the user is traceable back to their actual logged sessions.
"""

import datetime as dt
import random

import db

# ------------------------------------------------------------- CEFR bands --
CEFR_BANDS = [
    ("Pre-A1", 0, 50), ("A1", 50, 150), ("A2", 150, 300),
    ("B1", 300, 600), ("B2", 600, 1000), ("C1", 1000, 1600),
    ("C2", 1600, 999999),
]


def cefr_estimate(total_hours: float) -> str:
    for label, lo, hi in CEFR_BANDS:
        if lo <= total_hours < hi:
            return label
    return "C2"


def next_band(total_hours: float):
    for i, (label, lo, hi) in enumerate(CEFR_BANDS):
        if lo <= total_hours < hi:
            if i + 1 < len(CEFR_BANDS):
                nxt_label, nxt_lo, _ = CEFR_BANDS[i + 1]
                return label, lo, hi, nxt_label, hi
            return label, lo, hi, None, None
    return "C2", 1600, 999999, None, None


# ------------------------------------------------------------------ pace ---
def weekly_pace(weeks: int = 4) -> float:
    """Average hours/week over the trailing N weeks (uses actual session data)."""
    df = db.get_all_sessions()
    if df.empty:
        return 0.0
    cutoff = dt.date.today() - dt.timedelta(weeks=weeks)
    import pandas as pd
    recent = df[df["date"] >= pd.Timestamp(cutoff)]
    if recent.empty:
        return 0.0
    total_hours = recent["hours"].sum()
    return round(total_hours / weeks, 2)


def progress_forecast():
    totals = db.totals()
    total_hours = totals["total_hours"]
    cur_label, band_lo, band_hi, nxt_label, hours_needed_total = next_band(total_hours)
    pct_in_band = 0.0
    hours_remaining = None
    if nxt_label:
        span = band_hi - band_lo
        pct_in_band = max(0.0, min(1.0, (total_hours - band_lo) / span)) if span else 1.0
        hours_remaining = round(band_hi - total_hours, 1)

    pace = weekly_pace()
    est_date_current = est_date_faster = None
    if hours_remaining is not None and pace > 0:
        weeks_needed = hours_remaining / pace
        est_date_current = dt.date.today() + dt.timedelta(weeks=weeks_needed)
        faster_pace = pace * 1.25
        weeks_needed_fast = hours_remaining / faster_pace
        est_date_faster = dt.date.today() + dt.timedelta(weeks=weeks_needed_fast)

    return {
        "total_hours": total_hours,
        "current_level": cur_label,
        "next_level": nxt_label,
        "pct_in_band": pct_in_band,
        "hours_remaining": hours_remaining,
        "weekly_pace": pace,
        "est_date_current_pace": est_date_current,
        "est_date_faster_pace": est_date_faster,
    }


# -------------------------------------------------------- daily challenges --
CHALLENGE_BANK = {
    "Easy": [
        ("Learn 5 new words", "Find and save 5 new words to your dictionary today.", 20),
        ("Read one short paragraph", "Read any short German paragraph — a menu, sign, or headline works.", 20),
        ("Listen for 10 minutes", "Log at least 10 minutes of listening practice.", 20),
        ("Review 10 saved words", "Look back over 10 words you've already saved.", 15),
        ("Say 5 sentences out loud", "Practice speaking — even to yourself — with 5 simple sentences.", 20),
    ],
    "Medium": [
        ("Watch and summarize a video", "Watch a 10-minute German video and summarize it in your notes.", 40),
        ("Read one news article", "Read a full news article and note 3 new words.", 40),
        ("Complete one grammar exercise", "Do a short grammar drill on a topic you find tricky.", 40),
        ("30-minute mixed session", "Combine two categories (e.g. listening + flashcards) for 30 minutes.", 40),
        ("Write a short paragraph", "Write 50-80 words about your day in German.", 40),
    ],
    "Hard": [
        ("Watch native content, no subtitles", "Watch a native German YouTube video with no subtitles.", 80),
        ("Write 200 words", "Write a 200-word journal entry or story in German.", 80),
        ("Podcast + summary", "Listen to a full podcast episode and summarize it in German.", 80),
        ("5-minute conversation", "Hold a five-minute conversation in German, live or with an AI tutor.", 80),
        ("Read a full article, no translation", "Read a full native article without using a translator.", 80),
    ],
}


def generate_daily_challenges(today: dt.date | None = None):
    today = today or dt.date.today()
    date_str = today.isoformat()

    existing = db.get_challenges_for_date(date_str)
    if existing:
        return existing

    recent_titles = db.recent_challenge_titles(days=10)
    rng = random.Random(today.toordinal())  # deterministic per-day, but varies day to day

    chosen = []
    for difficulty in ["Easy", "Medium", "Hard"]:
        pool = CHALLENGE_BANK[difficulty]
        fresh = [c for c in pool if c[0] not in recent_titles]
        options = fresh if fresh else pool
        title, desc, xp = rng.choice(options)
        chosen.append(dict(difficulty=difficulty, title=title, description=desc, xp_reward=xp))

    db.ensure_daily_challenges(date_str, chosen)
    return db.get_challenges_for_date(date_str)


# --------------------------------------------------------- adaptive goals --
def adaptive_goal_suggestion():
    df = db.get_all_sessions()
    profile = db.get_profile()
    current_goal = int(profile.get("daily_goal_minutes", "30") or 30)
    if df.empty or len(df) < 5:
        return None

    import pandas as pd
    cutoff = dt.date.today() - dt.timedelta(days=14)
    recent = df[df["date"] >= pd.Timestamp(cutoff)]
    if recent.empty:
        return None

    daily = recent.groupby(recent["date"].dt.date)["minutes"].sum()
    avg_minutes = daily.mean()

    if avg_minutes >= current_goal * 1.3:
        suggested = int(round((avg_minutes * 0.9) / 5) * 5)
        return (f"You've averaged {avg_minutes:.0f} min/day recently — well above your "
                f"{current_goal}-min goal. Consider raising it to {suggested} min.", suggested)
    if avg_minutes <= current_goal * 0.5 and avg_minutes > 0:
        suggested = max(10, int(round((avg_minutes * 1.1) / 5) * 5))
        return (f"Your recent daily average is {avg_minutes:.0f} min, below your "
                f"{current_goal}-min goal. Consider a more achievable {suggested}-min goal "
                f"to protect your streak.", suggested)
    return None


# ----------------------------------------------------- motivation messages --
def personalized_motivation_messages(limit=4):
    totals = db.totals()
    profile = db.get_profile()
    df = db.get_all_sessions()
    msgs = []

    if totals["total_hours"] > 0:
        msgs.append(f"You've already invested {totals['total_hours']:.0f} hours into German.")

    streak = int(profile.get("current_streak", "0") or 0)
    if streak >= 3:
        msgs.append(f"You're on a {streak}-day streak — keep the chain going.")

    cur, lo, hi, nxt, hi2 = next_band(totals["total_hours"])
    if nxt:
        span = hi - lo
        pct = max(0.0, min(1.0, (totals["total_hours"] - lo) / span)) if span else 1.0
        if pct >= 0.5:
            msgs.append(f"You're closer to {nxt} than you were to {cur} — {pct*100:.0f}% through this level.")

    if not df.empty:
        import pandas as pd
        this_month = df[df["date"] >= pd.Timestamp(dt.date.today().replace(day=1))]
        if len(this_month) > 0:
            msgs.append(f"You've completed {len(this_month)} study sessions this month.")

    if len(msgs) < limit:
        words_df = db.get_saved_words()
        if len(words_df) > 0:
            msgs.append(f"You've saved {len(words_df)} words to your personal dictionary.")

    return msgs[:limit] if msgs else ["Log your first session to start seeing your progress here."]


# -------------------------------------------------------- session insights --
def session_insight(today: dt.date | None = None):
    today = today or dt.date.today()
    df = db.get_all_sessions()
    profile = db.get_profile()
    if df.empty:
        return None
    import pandas as pd
    today_df = df[df["date"] == pd.Timestamp(today)]
    if today_df.empty:
        return None

    by_cat = today_df.groupby("category")["minutes"].sum().to_dict()
    forecast = progress_forecast()
    week_start = pd.Timestamp(today - dt.timedelta(days=today.weekday()))
    week_df = df[df["date"] >= week_start]
    goal = int(profile.get("daily_goal_minutes", "30") or 30)
    weekly_target = goal * 7
    weekly_pct = min(100, round((week_df["minutes"].sum() / weekly_target) * 100)) if weekly_target else 0

    least_practiced = min(by_cat, key=by_cat.get) if len(by_cat) > 1 else None
    heaviest = max(by_cat, key=by_cat.get)
    suggestion = None
    all_cats = set(db.CATEGORIES)
    untouched_today = all_cats - set(by_cat.keys())
    if untouched_today:
        suggestion = f"Try some {sorted(untouched_today)[0]} to balance today's {heaviest.lower()}-heavy session."
    elif least_practiced and least_practiced != heaviest:
        suggestion = f"Consider a bit more {least_practiced} tomorrow to balance things out."

    return {
        "by_category": by_cat,
        "streak": int(profile.get("current_streak", "0") or 0),
        "weekly_pct": weekly_pct,
        "hours_to_next_level": forecast["hours_remaining"],
        "next_level": forecast["next_level"],
        "suggestion": suggestion,
    }


# ------------------------------------------------------- weekly reflection --
def generate_weekly_reflection(week_start: dt.date):
    """week_start must be a Monday. Idempotent: cached in db.weekly_reflections."""
    week_start_str = week_start.isoformat()
    cached = db.get_weekly_reflection(week_start_str)
    if cached:
        return cached

    df = db.get_all_sessions()
    if df.empty:
        return None
    import pandas as pd
    week_end = week_start + dt.timedelta(days=7)
    week_df = df[(df["date"] >= pd.Timestamp(week_start)) & (df["date"] < pd.Timestamp(week_end))]
    prev_start = week_start - dt.timedelta(days=7)
    prev_df = df[(df["date"] >= pd.Timestamp(prev_start)) & (df["date"] < pd.Timestamp(week_start))]

    if week_df.empty:
        return None

    by_cat = week_df.groupby("category")["hours"].sum().sort_values(ascending=False)
    strongest_skill = by_cat.index[0] if len(by_cat) else "—"
    weakest_skill = by_cat.index[-1] if len(by_cat) else "—"

    days_active = int(week_df["date"].dt.date.nunique())
    consistency_pct = round((days_active / 7) * 100)

    by_day = week_df.groupby(week_df["date"].dt.day_name())["hours"].sum()
    most_productive_day = by_day.idxmax() if len(by_day) else "—"

    total_this_week = float(round(week_df["hours"].sum(), 2))
    total_prev_week = float(round(prev_df["hours"].sum(), 2)) if not prev_df.empty else 0.0
    improved = bool(total_this_week > total_prev_week)

    hours_before_week = db.hours_before(week_start)
    hours_after_week = hours_before_week + total_this_week
    milestone_reached = None
    for m in db.MILESTONES_HOURS:
        if hours_before_week < m <= hours_after_week:
            milestone_reached = m

    all_cats = set(db.CATEGORIES)
    untouched = all_cats - set(by_cat.index)
    recommended_focus = sorted(untouched)[0] if untouched else weakest_skill

    report = {
        "week_start": week_start_str,
        "total_hours": total_this_week,
        "prev_week_hours": total_prev_week,
        "improved": improved,
        "strongest_skill": strongest_skill,
        "weakest_skill": weakest_skill,
        "consistency_pct": consistency_pct,
        "days_active": days_active,
        "most_productive_day": most_productive_day,
        "most_productive_method": strongest_skill,
        "milestone_reached": milestone_reached,
        "recommended_focus": recommended_focus,
        "suggested_challenge": f"Log at least one {recommended_focus} session on 4 different days next week.",
    }
    db.save_weekly_reflection(week_start_str, report)
    return report


def most_recent_complete_week_start(today: dt.date | None = None):
    today = today or dt.date.today()
    this_monday = today - dt.timedelta(days=today.weekday())
    return this_monday - dt.timedelta(days=7)


# --------------------------------------------------------- learning profile --
def derive_learning_profile():
    df = db.get_all_sessions()
    if df.empty:
        return None

    by_cat_count = df.groupby("category").size().sort_values(ascending=False)
    favorite_method = by_cat_count.index[0]

    by_cat_hours = df.groupby("category")["hours"].sum().sort_values(ascending=False)
    most_successful_method = by_cat_hours.index[0]

    avg_session_min = round(df["minutes"].mean(), 1)
    longest_session = df.loc[df["minutes"].idxmax()]

    weekday_counts = df["date"].dt.day_name().value_counts()
    favorite_day = weekday_counts.idxmax() if len(weekday_counts) else "—"

    return {
        "favorite_method": favorite_method,
        "most_successful_method": most_successful_method,
        "avg_session_minutes": avg_session_min,
        "longest_session_minutes": float(longest_session["minutes"]),
        "longest_session_category": longest_session["category"],
        "favorite_day": favorite_day,
        "total_sessions": len(df),
    }


# ------------------------------------------------------------- timeline ----
def sync_timeline_events():
    """Idempotently records milestone events into the timeline as they happen."""
    totals = db.totals()
    profile = db.get_profile()

    if totals["sessions"] >= 1:
        df = db.get_all_sessions()
        first_date = df["date"].min()
        db.record_timeline_event(
            "started_learning", "Started learning German", "Logged your first study session.",
            "🌱", first_date.isoformat(),
        )

    if totals["total_hours"] >= 10:
        db.record_timeline_event("first_10_hours", "First 10 hours", "Crossed 10 hours of study.", "⏱️")

    for m in db.MILESTONES_HOURS:
        if totals["total_hours"] >= m:
            db.record_timeline_event(f"milestone_{m}h", f"{m} hours reached",
                                      f"Crossed {m} total hours of German study.", "🏅")

    words_df = db.get_saved_words()
    if len(words_df) >= 100:
        db.record_timeline_event("100th_word", "100th word saved", "Your dictionary passed 100 words.", "📚")

    longest_streak = int(profile.get("longest_streak", "0") or 0)
    if longest_streak >= 7:
        db.record_timeline_event("one_week_streak", "One week streak", "Reached a 7-day streak.", "🔥")
    if longest_streak >= 30:
        db.record_timeline_event("one_month_streak", "One month streak", "Reached a 30-day streak.", "🔥")

    cur_level = cefr_estimate(totals["total_hours"])
    if cur_level not in ("Pre-A1",):
        db.record_timeline_event(f"reached_{cur_level}", f"Reached {cur_level} (estimated)",
                                  f"Estimated CEFR level reached: {cur_level}.", "🎓")

    unlocked = [t.strip() for t in profile.get("unlocked_themes", "").split(",") if t.strip()]
    for theme in unlocked:
        if theme != "Neon Megacity":
            db.record_timeline_event(f"unlocked_{theme}", f"Unlocked {theme}",
                                      f"Unlocked the {theme} world theme.", "🌍")
