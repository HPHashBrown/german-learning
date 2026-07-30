import datetime as dt
import json
import random

import pandas as pd
import streamlit as st

import db
import levels
import rewards
import shop_catalog as sc
import loot
import lessons
import grammar
import stories
import gemini_tools as gt
import achievements as ach
import daily_extras
from srs import sm2, next_due_date
from styles import inject_css, card_start, card_end, xp_bar, rarity_span
from effects import play_sound, confetti_burst

st.set_page_config(page_title="Fluent Forest RPG", page_icon="🐉", layout="wide",
                    initial_sidebar_state="expanded")

db.init_db()


# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------
def grant_reward(reward: dict):
    """Applies a reward dict (from rewards.py or loot) to the profile.
    Returns a human-readable description of what was granted."""
    t = reward.get("type")
    if t == "xp":
        db.add_xp(reward["amount"], "daily_reward")
        return f"+{reward['amount']} XP"
    if t == "coins":
        db.add_coins(reward["amount"])
        return f"+{reward['amount']} Coins"
    if t == "chest":
        db.add_keys(reward["chest"], 1)
        return f"1x {reward['chest'].title()} Key (open it in Loot Chests!)"
    if t == "theme":
        item = sc.get_item(reward["item"])
        if item:
            db.grant_item(item["id"], item["type"], item["rarity"], via="daily_reward")
            return f"New Theme: {item['name']}"
    if t == "title":
        db.grant_item(f"title_{reward['item'].lower().replace(' ', '_')}", "title", "rare", via="daily_reward")
        return f"New Title: {reward['item']}"
    if t == "pet":
        item = sc.get_item(reward["item"])
        if item:
            db.grant_item(item["id"], item["type"], item["rarity"], via="daily_reward")
            return f"New Pet: {item['name']}"
    if t == "key":
        db.add_keys(reward["key"], 1)
        return f"1x {reward['key'].title()} Key"
    if t == "xp_boost":
        return "2x XP Boost (cosmetic reward — noted, no mechanical boost wired up yet)"
    if t in ("legend_status", "legend_status_2"):
        db.add_keys("legendary", 1)
        db.unlock_achievement(t)
        return "Legend Status unlocked + 1x Legendary Key!"
    return reward.get("label", "Reward")


def process_daily_login():
    today_str = dt.date.today().isoformat()
    existing = db.get_login_record(today_str)
    if existing:
        return None  # already claimed today

    streak, changed = db.process_login_streak()
    day_number = db.total_login_days() + 1
    reward = rewards.reward_for_day(day_number)
    description = grant_reward(reward)
    db.claim_daily_login(today_str, reward)
    return {"day_number": day_number, "reward": reward, "description": description, "streak": streak}


def build_stats_snapshot():
    profile = db.get_profile()
    xp = int(float(profile.get("xp", "0") or 0))
    level = levels.level_for_xp(xp)
    if str(level) != profile.get("level"):
        db.set_profile("level", level)

    quiz_df = db.get_quiz_results()
    vocab_df = db.get_vocab_df()
    inventory_df = db.get_inventory()
    story_progress = db.get_story_progress()
    chest_history = db.get_chest_history()

    stats = {
        "xp": xp, "level": level, "coins": int(float(profile.get("coins", "0") or 0)),
        "current_streak": int(profile.get("current_streak", "0") or 0),
        "longest_streak": int(profile.get("longest_streak", "0") or 0),
        "quizzes_completed": len(quiz_df),
        "perfect_quizzes": int((quiz_df["score"] == quiz_df["total"]).sum()) if not quiz_df.empty else 0,
        "words_saved": len(vocab_df),
        "words_mastered": int((vocab_df["srs_state"] == "Mastered").sum()) if not vocab_df.empty else 0,
        "stories_completed": sum(1 for v in story_progress.values() if v["completed"]),
        "stories_total": len(stories.STORIES),
        "chests_opened": len(chest_history),
        "legendary_items_owned": int((inventory_df["rarity"] == "legendary").sum()) if not inventory_df.empty else 0,
        "pets_owned": int((inventory_df["item_type"] == "pet").sum()) if not inventory_df.empty else 0,
    }
    return stats, profile


def check_achievements(stats):
    unlocked_keys = db.get_unlocked_achievements()
    newly = []
    for a in ach.achievement_definitions():
        if a["key"] not in unlocked_keys and a["check"](stats):
            db.unlock_achievement(a["key"])
            newly.append(a)
    return newly


def equipped_pet_emoji(profile):
    pet_id = profile.get("equipped_pet", "")
    item = sc.get_item(pet_id) if pet_id else None
    return item["emoji"] if item else None


def pet_react(mood: str):
    """mood: 'happy' | 'sad' | 'excited'. Purely cosmetic flavor text."""
    reactions = {
        "happy": ["wags its tail! 🐾", "looks pleased!", "does a little happy hop!"],
        "sad": ["tilts its head sadly.", "looks a little disappointed.", "sighs softly."],
        "excited": ["can't contain its excitement! ✨", "does a happy spin!", "cheers you on!"],
    }
    return random.choice(reactions.get(mood, ["reacts."]))


def xp_gain_display(amount: int, profile: dict) -> str:
    """Renders an XP gain using whatever XP effect the player has equipped
    (defaults to a plain '+N XP' if none equipped or 'xp_normal' owned)."""
    effect_id = profile.get("equipped_xp_effect", "")
    effect = sc.get_item(effect_id) if effect_id else None
    if not effect or effect["type"] != "xp_effect" or effect_id == "xp_normal":
        return f"+{amount} XP"
    return f"{effect['emoji']} +{amount} XP {effect['emoji']}"


def _generate_daily_shop(date_str: str):
    import hashlib
    seed = int(hashlib.md5(date_str.encode()).hexdigest(), 16) % (2**31)
    rng = random.Random(seed)

    non_legendary = [i for i in sc.PURCHASABLE_ITEMS if i["rarity"] != "legendary"]
    picks = rng.sample(non_legendary, min(10, len(non_legendary)))
    items = [{"id": p["id"], "discount_pct": rng.choice([20, 25, 30, 40, 50])} for p in picks]

    if rng.random() < 0.02:
        legendary_pool = [i for i in sc.PURCHASABLE_ITEMS if i["rarity"] == "legendary"]
        if legendary_pool:
            leg = rng.choice(legendary_pool)
            items.append({"id": leg["id"], "discount_pct": 10, "is_legendary_special": True})

    db.save_shop_for_date(date_str, items)
    return items


def _get_daily_shop():
    today_str = dt.date.today().isoformat()
    existing = db.get_shop_for_date(today_str)
    return existing if existing else _generate_daily_shop(today_str)


def _buy_item(item_id: str, price: int, sound_enabled: bool):
    if db.owns_item(item_id):
        st.info("You already own this!")
        return
    if db.spend_coins(price):
        item = sc.get_item(item_id)
        db.grant_item(item["id"], item["type"], item["rarity"], via="shop")
        play_sound("coin", sound_enabled)
        st.toast(f"Purchased {item['name']}!")
        st.rerun()
    else:
        st.error("Not enough coins!")


# ----------------------------------------------------------------------------
# Sidebar
# ----------------------------------------------------------------------------
profile = db.get_profile()
inject_css(profile.get("equipped_theme", "light"), reduced_motion=False)

daily_result = process_daily_login()

NAV_PAGES = [
    "🏠 Home", "🌲 Log Immersion", "📚 Vocabulary Quiz", "🔤 Article Trainer", "🔀 Verb Trainer",
    "📝 Grammar Explorer", "📖 Reading Stories", "🃏 Flashcards", "📇 Vocabulary Manager",
    "💬 AI Chat", "✍️ AI Writing Tutor", "🎤 Pronunciation Trainer",
    "🗺️ CEFR Roadmap", "📊 Statistics", "🎯 Weekly Challenges", "💰 Wallet",
    "🛍️ Shop", "📦 Loot Chests", "🧑‍🎨 Avatar", "🏆 Trophy Room", "⚙️ Settings",
]

with st.sidebar:
    st.markdown("## 🐉 Fluent Forest RPG")
    stats, profile = build_stats_snapshot()
    lvl, into, span, pct, next_lvl = levels.xp_progress(stats["xp"])

    pet_emoji = equipped_pet_emoji(profile)
    if pet_emoji:
        st.markdown(f'<div class="pet-companion">{pet_emoji}</div>', unsafe_allow_html=True)

    st.markdown(f"**{profile.get('display_name','Sprachheld')}** — Level {lvl}")
    xp_bar(pct, f"{into}/{span} XP to Level {next_lvl}" if next_lvl else "Max Level!")
    st.markdown(f"🪙 **{stats['coins']:,}** coins &nbsp;&nbsp; 🔥 **{stats['current_streak']}** day streak")

    nu = levels.next_unlock(lvl)
    if nu:
        feat, req_lvl, req_xp = nu
        st.caption(f"Only {max(0, req_xp - stats['xp'])} XP until **{feat}** unlocks!")

    page = st.radio("Navigate", NAV_PAGES, label_visibility="collapsed", key="ff_page")

    st.markdown("---")
    with st.expander("🔑 Gemini API Key"):
        st.caption(
            "AI Chat, Writing Tutor, Pronunciation Trainer, and AI Dictionary lookups "
            "use Google's Gemini API. Paste your key below — kept only in this "
            "browser session, never saved to disk."
        )
        gemini_key = st.text_input("Gemini API key", type="password", key="gemini_api_key")

newly_ach = check_achievements(stats)
for a in newly_ach:
    db.grant_item(f"trophy_{a['key']}", "trophy", a["rarity"], via="achievement")
    st.toast(f"{a['emoji']} Achievement unlocked: {a['name']}!", icon="🏆")


# ----------------------------------------------------------------------------
# PAGE: Home
# ----------------------------------------------------------------------------
if page == "🏠 Home":
    theme_item = sc.get_item(profile.get("equipped_theme", "light"))
    st.markdown(f"# Willkommen zurück, {profile.get('display_name','Sprachheld')}! {theme_item['emoji'] if theme_item else ''}")

    if daily_result:
        card_start()
        st.markdown(f"### 🎁 Day {daily_result['day_number']} Login Reward!")
        st.markdown(f"## {daily_result['description']}")
        st.caption(f"Current streak: {daily_result['streak']} days")
        card_end()
        confetti_burst(100)
        play_sound("daily_reward", profile.get("sound_enabled", "1") == "1")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        card_start(); st.metric("Level", stats["level"]); card_end()
    with c2:
        card_start(); st.metric("XP", f"{stats['xp']:,}"); card_end()
    with c3:
        card_start(); st.metric("Coins", f"{stats['coins']:,}"); card_end()
    with c4:
        card_start(); st.metric("Streak", f"{stats['current_streak']} 🔥"); card_end()

    lvl, into, span, pct, next_lvl = levels.xp_progress(stats["xp"])
    st.markdown("### Level Progress")
    xp_bar(pct, f"{into} / {span} XP to Level {next_lvl}" if next_lvl else "Maximum level reached!")

    nu = levels.next_unlock(lvl)
    if nu:
        feat, req_lvl, req_xp = nu
        remaining = max(0, req_xp - stats["xp"])
        st.info(f"🔓 Only **{remaining} XP** until **{feat}** unlocks at Level {req_lvl}!", icon="🔓")

    col1, col2 = st.columns(2)
    with col1:
        card_start()
        st.markdown("#### 🐾 Your Companion")
        pet_emoji = equipped_pet_emoji(profile)
        if pet_emoji:
            st.markdown(f'<div class="pet-companion" style="font-size:4rem;">{pet_emoji}</div>', unsafe_allow_html=True)
            st.caption(f"Your pet {pet_react('happy')}")
        else:
            st.caption("No pet equipped yet — visit the Shop or open a Loot Chest!")
        card_end()

        card_start()
        st.markdown("#### 📚 Unlocked Content")
        unlocked = levels.unlocked_features(lvl)
        st.markdown("".join(f'<span class="rpg-pill">{f}</span>' for f in unlocked), unsafe_allow_html=True)
        card_end()

    with col2:
        card_start()
        st.markdown("#### 🎯 This Week's Challenges")
        week_start = (dt.date.today() - dt.timedelta(days=dt.date.today().weekday())).isoformat()
        challenges = rewards.challenges_for_week(week_start)
        db.ensure_weekly_challenges(week_start, [
            {"key": c["key"], "target": c["target"]} for c in challenges
        ])
        saved_challenges = {c["challenge_key"]: c for c in db.get_weekly_challenges(week_start)}
        for c in challenges:
            saved = saved_challenges.get(c["key"], {})
            progress = saved.get("progress", 0)
            pct_c = min(1.0, progress / c["target"]) if c["target"] else 0
            st.markdown(f"**{c['label']}**")
            st.progress(pct_c)
            st.caption(f"{progress:.0f} / {c['target']} {c['unit']}")
        card_end()

    st.markdown("### ✨ Daily Extras")
    extras = daily_extras.daily_extras()
    ec1, ec2, ec3 = st.columns(3)
    with ec1:
        card_start()
        st.markdown("#### 🗣️ Idiom of the Day")
        st.markdown(f"**{extras['idiom']}**")
        st.caption(extras["idiom_meaning"])
        card_end()
    with ec2:
        card_start()
        st.markdown("#### 🌍 DACH Fact")
        st.write(extras["fact"])
        card_end()
    with ec3:
        card_start()
        st.markdown("#### 💬 Quote of the Day")
        st.markdown(f"_„{extras['quote']}“_")
        st.caption(f"— {extras['quote_author']}")
        card_end()

    st.markdown("### 📖 Continue Reading")
    available = stories.available_stories(lvl)
    progress = db.get_story_progress()
    unread = [s for s in available if s["id"] not in progress or not progress[s["id"]]["completed"]]
    if unread:
        for s in unread[:3]:
            st.markdown(f"- **{s['title']}** ({s['level']})")
    else:
        st.caption("You've completed every unlocked story — nice work! Level up for more.")


# ----------------------------------------------------------------------------
# PAGE: Log Immersion
# ----------------------------------------------------------------------------
elif page == "🌲 Log Immersion":
    st.markdown("## 🌲 Log German Immersion")
    st.caption(
        f"Log any time spent with German outside the app — reading, listening, watching, "
        f"speaking, whatever. Converts to **{db.IMMERSION_XP_PER_HOUR} XP** and "
        f"**{db.IMMERSION_COINS_PER_HOUR} 🪙 per hour**."
    )

    c1, c2, c3, c4 = st.columns(4)
    imm_totals = db.immersion_totals()
    with c1:
        card_start(); st.metric("Total Hours", imm_totals["total_hours"]); card_end()
    with c2:
        card_start(); st.metric("This Week", imm_totals["week_hours"]); card_end()
    with c3:
        card_start(); st.metric("This Month", imm_totals["month_hours"]); card_end()
    with c4:
        card_start(); st.metric("Streak", f"{stats['current_streak']} 🔥"); card_end()

    with st.form("log_immersion_form", clear_on_submit=True):
        cc1, cc2 = st.columns(2)
        with cc1:
            log_date = st.date_input("Date", value=dt.date.today(), max_value=dt.date.today())
            hours = st.number_input("Hours", min_value=0.1, max_value=16.0, value=0.5, step=0.25)
        with cc2:
            category = st.selectbox("Category", [
                "Reading", "Listening", "Watching", "Speaking", "Podcast",
                "Movies/TV", "Conversation", "Other",
            ])
            notes = st.text_input("Notes (optional)", placeholder="e.g. Easy German episode 214")

        submitted = st.form_submit_button("✅ Log Immersion Time", type="primary", width='stretch')
        if submitted:
            xp_earned, coins_earned = db.add_immersion_session(
                log_date.isoformat(), hours, category, notes,
            )
            week_start = (dt.date.today() - dt.timedelta(days=dt.date.today().weekday())).isoformat()
            db.bump_weekly_progress(week_start, "earn_xp", xp_earned)
            st.success(f"Logged {hours}h of {category}! {xp_gain_display(xp_earned, profile)}, +{coins_earned} 🪙")
            play_sound("coin", profile.get("sound_enabled", "1") == "1")
            st.rerun()

    st.markdown("### Recent Sessions")
    sessions_df = db.get_immersion_sessions()
    if sessions_df.empty:
        st.info("No immersion time logged yet — add your first session above!")
    else:
        show = sessions_df[["date", "hours", "category", "notes", "xp_earned", "coins_earned"]].head(20).copy()
        show["date"] = show["date"].dt.strftime("%Y-%m-%d")
        st.dataframe(show, width='stretch', hide_index=True)


# ----------------------------------------------------------------------------
# PAGE: Vocabulary Quiz
# ----------------------------------------------------------------------------
elif page == "📚 Vocabulary Quiz":
    st.markdown("## 📚 Vocabulary Quiz")
    lvl = stats["level"]
    categories = lessons.available_categories(lvl)

    if "vocab_quiz" not in st.session_state:
        st.session_state.vocab_quiz = None

    category = st.selectbox("Category", categories, key="vocab_quiz_category")

    if st.session_state.vocab_quiz is None or st.session_state.vocab_quiz.get("category") != category:
        if st.button("Start Quiz", type="primary"):
            questions = lessons.make_quiz(category, 8, random.Random())
            st.session_state.vocab_quiz = {
                "category": category, "questions": questions, "index": 0,
                "score": 0, "answers": [],
            }
            st.rerun()
    else:
        quiz = st.session_state.vocab_quiz
        idx = quiz["index"]
        if idx < len(quiz["questions"]):
            q = quiz["questions"][idx]
            card_start()
            st.markdown(f"**Question {idx+1} / {len(quiz['questions'])}**")
            st.markdown(f"### {q['prompt']}")
            choice = st.radio("What does this mean?", q["options"], key=f"vocab_q_{idx}", index=None)
            if st.button("Submit Answer", key=f"vocab_submit_{idx}"):
                if choice is None:
                    st.warning("Pick an answer first!")
                else:
                    correct = choice == q["correct"]
                    quiz["answers"].append(correct)
                    if correct:
                        quiz["score"] += 1
                        st.success(f"Correct! Your pet {pet_react('happy')}")
                        play_sound("correct", profile.get("sound_enabled", "1") == "1")
                    else:
                        st.error(f"Not quite — the answer was **{q['correct']}**. Your pet {pet_react('sad')}")
                        play_sound("incorrect", profile.get("sound_enabled", "1") == "1")
                    quiz["index"] += 1
                    st.rerun()
            card_end()
        else:
            score, total = quiz["score"], len(quiz["questions"])
            pct = score / total if total else 0
            xp_earned = int(20 * total * pct) + (15 if pct == 1.0 else 0)
            coins_earned = int(5 * total * pct)
            db.record_quiz("vocabulary", quiz["category"], score, total, xp_earned)
            db.add_xp(xp_earned, "vocabulary_quiz")
            db.add_coins(coins_earned)
            week_start = (dt.date.today() - dt.timedelta(days=dt.date.today().weekday())).isoformat()
            db.bump_weekly_progress(week_start, "earn_xp", xp_earned)
            db.bump_weekly_progress(week_start, "complete_quizzes", 1)

            card_start()
            st.markdown(f"## Quiz Complete! {score}/{total}")
            st.markdown(f"**{xp_gain_display(xp_earned, profile)}** &nbsp;&nbsp; **+{coins_earned} 🪙**")
            if pct == 1.0:
                st.success("🎉 Perfect score bonus applied!")
                confetti_burst(150)
                play_sound("level_up", profile.get("sound_enabled", "1") == "1")
            if st.button("Take Another Quiz"):
                st.session_state.vocab_quiz = None
                st.rerun()
            card_end()


# ----------------------------------------------------------------------------
# PAGE: Article Trainer
# ----------------------------------------------------------------------------
elif page == "🔤 Article Trainer":
    st.markdown("## 🔤 Article Trainer")
    st.caption("der, die, or das? Timed mode with a combo multiplier.")

    if "article_game" not in st.session_state:
        st.session_state.article_game = None

    if st.session_state.article_game is None:
        if st.button("Start (10 words)", type="primary"):
            qs = [grammar.make_article_question(random.Random()) for _ in range(10)]
            st.session_state.article_game = {"questions": qs, "index": 0, "score": 0, "combo": 0, "max_combo": 0}
            st.rerun()
    else:
        game = st.session_state.article_game
        idx = game["index"]
        if idx < len(game["questions"]):
            q = game["questions"][idx]
            card_start()
            st.markdown(f"**Word {idx+1}/10** &nbsp;&nbsp; Combo: 🔥×{game['combo']}")
            st.markdown(f"### ___ {q['noun']}")
            cols = st.columns(3)
            for i, opt in enumerate(q["options"]):
                with cols[i]:
                    if st.button(opt, key=f"article_{idx}_{opt}", width='stretch'):
                        if opt == q["correct"]:
                            game["score"] += 1
                            game["combo"] += 1
                            game["max_combo"] = max(game["max_combo"], game["combo"])
                            st.success(f"Richtig! {q['correct']} {q['noun']}")
                        else:
                            game["combo"] = 0
                            st.error(f"Nope — it's **{q['correct']} {q['noun']}**")
                        game["index"] += 1
                        st.rerun()
            card_end()
        else:
            score = game["score"]
            xp_earned = score * 8 + game["max_combo"] * 5
            db.add_xp(xp_earned, "article_trainer")
            db.record_quiz("article", "der/die/das", score, 10, xp_earned)
            card_start()
            st.markdown(f"## Done! {score}/10 correct")
            st.markdown(f"Best combo: 🔥×{game['max_combo']} &nbsp;&nbsp; **{xp_gain_display(xp_earned, profile)}**")
            if st.button("Play Again"):
                st.session_state.article_game = None
                st.rerun()
            card_end()


# ----------------------------------------------------------------------------
# PAGE: Verb Trainer
# ----------------------------------------------------------------------------
elif page == "🔀 Verb Trainer":
    st.markdown("## 🔀 Verb Trainer")
    st.caption("Practice conjugation. Requires Level 7+ (unlocked once you get there).")

    if not levels.is_unlocked("Verb Trainer", stats["level"]):
        st.warning(f"🔒 Verb Trainer unlocks at Level 7. You're currently Level {stats['level']}.")
    else:
        mode = st.selectbox("Mode", ["mixed", "weak", "strong"], format_func=lambda m: {
            "mixed": "Mixed", "weak": "Weak Verbs (regular)", "strong": "Strong Verbs (irregular)",
        }[m])

        if "verb_game" not in st.session_state:
            st.session_state.verb_game = None

        if st.session_state.verb_game is None or st.session_state.verb_game.get("mode") != mode:
            if st.button("Start (10 questions)", type="primary"):
                qs = [grammar.make_verb_question(mode, random.Random()) for _ in range(10)]
                st.session_state.verb_game = {"mode": mode, "questions": qs, "index": 0, "score": 0}
                st.rerun()
        else:
            game = st.session_state.verb_game
            idx = game["index"]
            if idx < len(game["questions"]):
                q = game["questions"][idx]
                card_start()
                st.markdown(f"**Question {idx+1}/10**")
                st.markdown(f"### {q['pronoun']} ___ ({q['verb']})")
                answer = st.text_input("Your answer", key=f"verb_answer_{idx}")
                if st.button("Submit", key=f"verb_submit_{idx}"):
                    correct = answer.strip().lower() == q["correct"].lower()
                    if correct:
                        game["score"] += 1
                        st.success("Richtig!")
                    else:
                        st.error(f"The correct form was **{q['correct']}**")
                    game["index"] += 1
                    st.rerun()
                card_end()
            else:
                score = game["score"]
                xp_earned = score * 10
                db.add_xp(xp_earned, "verb_trainer")
                db.record_quiz("verb", mode, score, 10, xp_earned)
                card_start()
                st.markdown(f"## Done! {score}/10 correct — **{xp_gain_display(xp_earned, profile)}**")
                if st.button("Play Again"):
                    st.session_state.verb_game = None
                    st.rerun()
                card_end()


# ----------------------------------------------------------------------------
# PAGE: Grammar Explorer
# ----------------------------------------------------------------------------
elif page == "📝 Grammar Explorer":
    st.markdown("## 📝 Grammar Explorer")

    if not levels.is_unlocked("Intermediate Grammar", stats["level"]):
        st.warning(f"🔒 Full Grammar Explorer unlocks at Level 10 (Intermediate Grammar). "
                   f"You're currently Level {stats['level']} — basic topics below are still open to browse.")

    for topic, data in grammar.GRAMMAR_TREE.items():
        locked = stats["level"] < data["min_level"] and not levels.is_unlocked("Intermediate Grammar", stats["level"])
        with st.expander(f"{'🔒 ' if locked else ''}{topic}", expanded=False):
            if locked:
                st.caption(f"Unlocks at Level {data['min_level']}.")
                continue
            for lesson in data["lessons"]:
                st.markdown(f"#### {lesson['title']}")
                st.write(lesson["body"])
                for ex in lesson["examples"]:
                    st.markdown(f"- _{ex}_")
            st.markdown("##### Mini Quiz")
            for qi, q in enumerate(data["quiz"]):
                choice = st.radio(q["q"], q["options"], key=f"grammar_{topic}_{qi}", index=None)
                if choice is not None:
                    if choice == q["correct"]:
                        st.success("Correct!")
                    else:
                        st.error(f"Not quite — the answer is **{q['correct']}**")


# ----------------------------------------------------------------------------
# PAGE: Reading Stories
# ----------------------------------------------------------------------------
elif page == "📖 Reading Stories":
    st.markdown("## 📖 Reading Stories")
    st.caption(
        "Click any highlighted vocabulary word below a story to see its definition "
        "and save it to your dictionary. (Only the listed vocab words are clickable — "
        "full free-text lookup for every word would need a live dictionary API.)"
    )

    available = stories.available_stories(stats["level"])
    progress = db.get_story_progress()

    if "reading_story_id" not in st.session_state:
        st.session_state.reading_story_id = None

    if st.session_state.reading_story_id is None:
        level_filter = st.multiselect("Filter by CEFR level", ["A1", "A2", "B1", "B2"])
        shown = [s for s in available if not level_filter or s["level"] in level_filter]
        for s in shown:
            done = progress.get(s["id"], {}).get("completed")
            card_start()
            st.markdown(f"#### {'✅ ' if done else ''}{s['title']} — {s['level']}")
            st.caption(f"{len(s['text'].split())} words · {len(s['vocab'])} vocab words")
            if st.button("Read", key=f"read_{s['id']}"):
                st.session_state.reading_story_id = s["id"]
                st.rerun()
            card_end()
    else:
        story = stories.get_story(st.session_state.reading_story_id)
        if st.button("← Back to stories"):
            st.session_state.reading_story_id = None
            st.rerun()

        card_start()
        st.markdown(f"# {story['title']}")
        st.caption(f"CEFR {story['level']}")
        st.write(story["text"])
        card_end()

        col1, col2 = st.columns(2)
        with col1:
            card_start()
            st.markdown("#### 📘 Vocabulary")
            for word, meaning in story["vocab"]:
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.markdown(f"**{word}** — {meaning}")
                with c2:
                    if st.button("💾", key=f"save_vocab_{story['id']}_{word}"):
                        db.add_vocab(word, meaning, tag=story["title"])
                        st.toast(f"Saved {word}!")
            card_end()
        with col2:
            card_start()
            st.markdown("#### ✏️ Grammar Notes")
            st.write(story["grammar_notes"])
            card_end()

        st.markdown("### ❓ Comprehension Questions")
        answers = {}
        for qi, q in enumerate(story["questions"]):
            answers[qi] = st.radio(q["q"], q["options"], key=f"story_q_{story['id']}_{qi}", index=None)

        if st.button("Submit Answers", type="primary"):
            if any(a is None for a in answers.values()):
                st.warning("Please answer every question first.")
            else:
                correct_count = sum(
                    1 for qi, q in enumerate(story["questions"]) if answers[qi] == q["correct"]
                )
                score_pct = int(100 * correct_count / len(story["questions"]))
                already_done = story["id"] in progress and progress[story["id"]]["completed"]
                db.mark_story_complete(story["id"], score_pct)
                if not already_done:
                    xp_earned = 40 + score_pct // 2
                    db.add_xp(xp_earned, "reading_story")
                    db.add_coins(15)
                    week_start = (dt.date.today() - dt.timedelta(days=dt.date.today().weekday())).isoformat()
                    db.bump_weekly_progress(week_start, "finish_stories", 1)
                    st.success(f"Comprehension: {score_pct}%! {xp_gain_display(xp_earned, profile)}, +15 🪙")
                    if score_pct == 100:
                        confetti_burst(120)
                else:
                    st.info(f"Comprehension: {score_pct}%. (Already completed once — no repeat rewards.)")


# ----------------------------------------------------------------------------
# PAGE: Flashcards (Spaced Repetition)
# ----------------------------------------------------------------------------
elif page == "🃏 Flashcards":
    st.markdown("## 🃏 Flashcards — Spaced Repetition")
    st.caption("Real SM-2 spaced repetition: cards you know well come back less often; cards you miss come back sooner.")

    due_df = db.get_due_flashcards(limit=20)

    if "flashcard_queue" not in st.session_state or st.session_state.get("flashcard_queue_stale", True):
        st.session_state.flashcard_queue = due_df.to_dict("records")
        st.session_state.flashcard_queue_stale = False
        st.session_state.flashcard_show_answer = False

    queue = st.session_state.flashcard_queue

    if not queue:
        st.info("No flashcards due right now! Save more words (from Reading Stories or the Dictionary) "
                 "or check back later as your reviews come due.")
    else:
        card = queue[0]
        card_start()
        st.markdown(f"**{len(queue)} card(s) due**")
        st.markdown(f"# {card['word']}")
        if not st.session_state.flashcard_show_answer:
            if st.button("Show Answer", type="primary"):
                st.session_state.flashcard_show_answer = True
                st.rerun()
        else:
            st.markdown(f"### {card['meaning']}")
            if card["gender"] and card["gender"] != "—":
                st.caption(f"Gender: {card['gender']}")
            if card["example"]:
                st.caption(f"_{card['example']}_")

            st.markdown("How well did you know this?")
            cols = st.columns(4)
            grade_labels = [("Forgot", 1), ("Hard", 3), ("Good", 4), ("Easy", 5)]
            for i, (label, grade) in enumerate(grade_labels):
                with cols[i]:
                    if st.button(label, key=f"grade_{card['id']}_{grade}", width='stretch'):
                        new_ease, new_interval, new_reps, new_state = sm2(
                            card["ease"], card["interval_days"], card["repetitions"], grade,
                        )
                        due = next_due_date(new_interval)
                        db.update_flashcard_srs(card["id"], new_ease, new_interval, new_reps, due, new_state)
                        db.add_xp(5, "flashcard_review")
                        st.session_state.flashcard_queue = queue[1:]
                        st.session_state.flashcard_show_answer = False
                        st.rerun()
        card_end()

    if st.button("🔄 Refresh queue"):
        st.session_state.flashcard_queue_stale = True
        st.rerun()


# ----------------------------------------------------------------------------
# PAGE: Vocabulary Manager
# ----------------------------------------------------------------------------
elif page == "📇 Vocabulary Manager":
    st.markdown("## 📇 Vocabulary Manager")

    vocab_df = db.get_vocab_df()
    if vocab_df.empty:
        st.info("No saved words yet. Save some from Reading Stories, Flashcards, or the AI Dictionary lookup.")
    else:
        c1, c2, c3 = st.columns(3)
        with c1:
            search = st.text_input("Search", placeholder="Search words or meanings...")
        with c2:
            tags = ["All"] + sorted(vocab_df["tag"].dropna().unique().tolist())
            tag_filter = st.selectbox("Filter by tag", tags)
        with c3:
            state_filter = st.selectbox("Filter by SRS state", ["All", "New", "Learning", "Review", "Mastered"])

        view = vocab_df.copy()
        if search:
            mask = view["word"].str.contains(search, case=False, na=False) | view["meaning"].str.contains(search, case=False, na=False)
            view = view[mask]
        if tag_filter != "All":
            view = view[view["tag"] == tag_filter]
        if state_filter != "All":
            view = view[view["srs_state"] == state_filter]

        only_favorites = st.checkbox("⭐ Favorites only")
        if only_favorites:
            view = view[view["favorite"] == 1]

        st.dataframe(
            view[["id", "word", "meaning", "gender", "tag", "srs_state", "due_date", "favorite"]],
            width='stretch', hide_index=True,
        )

        c1, c2, c3 = st.columns(3)
        with c1:
            fav_id = st.number_input("Toggle favorite (ID)", min_value=0, value=0, step=1)
            if st.button("⭐ Toggle") and fav_id:
                db.toggle_favorite(int(fav_id))
                st.rerun()
        with c2:
            del_id = st.number_input("Delete word (ID)", min_value=0, value=0, step=1)
            if st.button("🗑️ Delete") and del_id:
                db.delete_vocab(int(del_id))
                st.rerun()
        with c3:
            anki_csv = view[["word", "meaning"]].to_csv(index=False, header=False)
            st.download_button("⬇️ Export to Anki (CSV)", anki_csv, file_name="vocab_anki_export.csv", mime="text/csv")


# ----------------------------------------------------------------------------
# PAGE: AI Chat (Conversation Mode)
# ----------------------------------------------------------------------------
elif page == "💬 AI Chat":
    st.markdown("## 💬 AI Conversation Mode")
    st.caption("Powered by Gemini. Roleplay a scenario in German — mistakes get gently corrected in-character.")

    if not gemini_key:
        st.warning("Add your Gemini API key in the sidebar to use AI Chat.")
    else:
        roleplay_unlocked = levels.is_unlocked("AI Roleplay", stats["level"])
        available_scenarios = list(gt.SCENARIOS.keys()) if roleplay_unlocked else ["Restaurant", "Ordering Coffee", "Shopping"]
        if not roleplay_unlocked:
            st.caption(f"Basic scenarios unlocked. Full AI Roleplay (all scenarios) unlocks at Level 20 "
                       f"— you're Level {stats['level']}.")

        scenario = st.selectbox("Scenario", available_scenarios)
        history = db.get_conversation(scenario)

        for turn in history:
            with st.chat_message("user" if turn["role"] == "user" else "assistant"):
                st.write(turn["content"])

        user_msg = st.chat_input("Type your message in German...")
        if user_msg:
            db.add_conversation_message(scenario, "user", user_msg)
            with st.chat_message("user"):
                st.write(user_msg)
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        reply = gt.conversation_reply(gemini_key, scenario, history, user_msg)
                    except Exception as e:
                        reply = f"(AI error: {e})"
                st.write(reply)
            db.add_conversation_message(scenario, "model", reply)
            db.add_xp(10, "ai_chat")
            st.rerun()

        if st.button("🗑️ Clear conversation"):
            db.clear_conversation(scenario)
            st.rerun()


# ----------------------------------------------------------------------------
# PAGE: AI Writing Tutor
# ----------------------------------------------------------------------------
elif page == "✍️ AI Writing Tutor":
    st.markdown("## ✍️ AI Writing Tutor")
    st.caption("Write a paragraph in German. Gemini returns grammar corrections, vocabulary "
               "improvements, natural phrasing notes, and alternatives.")

    if not gemini_key:
        st.warning("Add your Gemini API key in the sidebar to use the Writing Tutor.")
    else:
        paragraph = st.text_area("Your German paragraph", height=150,
                                  placeholder="Schreibe hier ein paar Sätze auf Deutsch...")
        if st.button("Get Feedback", type="primary") and paragraph.strip():
            with st.spinner("Analyzing your writing..."):
                try:
                    feedback = gt.writing_tutor_feedback(gemini_key, paragraph.strip())
                except Exception as e:
                    st.error(f"AI error: {e}")
                    feedback = None

            if feedback:
                db.add_xp(25, "writing_tutor")
                card_start()
                st.markdown("#### ✅ Corrected Text")
                st.write(feedback.get("corrected_text", "—"))
                card_end()

                if feedback.get("grammar_corrections"):
                    st.markdown("#### 📝 Grammar Corrections")
                    for gc in feedback["grammar_corrections"]:
                        st.markdown(f"- ~~{gc['original']}~~ → **{gc['corrected']}** — {gc['explanation']}")

                if feedback.get("vocabulary_improvements"):
                    st.markdown("#### 📚 Vocabulary Improvements")
                    for vi in feedback["vocabulary_improvements"]:
                        st.markdown(f"- {vi['original']} → **{vi['improved']}** — {vi['why']}")

                if feedback.get("natural_phrasing_notes"):
                    st.markdown("#### 🗣️ Natural Phrasing")
                    st.write(feedback["natural_phrasing_notes"])

                if feedback.get("alternative_expressions"):
                    st.markdown("#### 💡 Alternative Expressions")
                    for alt in feedback["alternative_expressions"]:
                        st.markdown(f"- {alt}")

                st.info(feedback.get("overall_feedback", ""), icon="🎓")


# ----------------------------------------------------------------------------
# PAGE: Pronunciation Trainer
# ----------------------------------------------------------------------------
elif page == "🎤 Pronunciation Trainer":
    st.markdown("## 🎤 Pronunciation Trainer")

    if not levels.is_unlocked("Pronunciation Practice", stats["level"]):
        st.warning(f"🔒 Unlocks at Level 3. You're currently Level {stats['level']}.")
    elif not gemini_key:
        st.warning("Add your Gemini API key in the sidebar to use the Pronunciation Trainer.")
    else:
        st.caption(
            "Best-effort feature: Gemini listens to your recording and gives a qualitative "
            "assessment. This is an AI estimate, not a calibrated phonetic scoring system — "
            "treat the score as a rough guide, not a precise measurement."
        )
        practice_sentences = [
            "Ich möchte einen Kaffee bestellen, bitte.",
            "Wo ist der nächste Bahnhof?",
            "Das Wetter ist heute wirklich schön.",
            "Können Sie mir bitte helfen?",
            "Ich lerne seit drei Monaten Deutsch.",
        ]
        sentence = st.selectbox("Target sentence", practice_sentences)
        st.markdown(f"### 🗣️ Say: *{sentence}*")

        audio = st.audio_input("Record yourself")
        if audio is not None and st.button("Analyze Pronunciation", type="primary"):
            with st.spinner("Analyzing..."):
                try:
                    result = gt.assess_pronunciation(gemini_key, sentence, audio.getvalue(), audio.type or "audio/wav")
                except Exception as e:
                    st.error(f"AI error: {e}")
                    result = None

            if result:
                score = result.get("overall_score", 0)
                card_start()
                st.markdown(f"## Score: {score}%")
                st.progress(min(1.0, score / 100))
                if result.get("word_scores"):
                    st.markdown("**Word-by-word:**")
                    for ws in result["word_scores"]:
                        icon = "✅" if ws.get("correct") else "⚠️"
                        st.markdown(f"{icon} {ws['word']} — {ws.get('note','')}")
                if result.get("problem_sounds"):
                    st.caption(f"Sounds to work on: {', '.join(result['problem_sounds'])}")
                st.write(result.get("fluency_note", ""))
                st.success(result.get("encouragement", "Keep practicing!"))
                card_end()
                xp_earned = max(5, score // 5)
                db.add_xp(xp_earned, "pronunciation")
                if score >= 90:
                    confetti_burst(100)


# ----------------------------------------------------------------------------
# PAGE: CEFR Roadmap
# ----------------------------------------------------------------------------
elif page == "🗺️ CEFR Roadmap":
    st.markdown("## 🗺️ CEFR Roadmap")
    st.caption("Your progress across the standard European proficiency scale.")

    quiz_df = db.get_quiz_results()
    vocab_df = db.get_vocab_df()
    story_progress = db.get_story_progress()

    cefr_defs = [
        ("A1", 1, 3), ("A2", 3, 10), ("B1", 10, 20), ("B2", 20, 40), ("C1", 40, 50),
    ]
    for cefr, lvl_lo, lvl_hi in cefr_defs:
        level_stories = [s for s in stories.STORIES if s["level"] == cefr] if cefr in ("A1", "A2", "B1", "B2") else []
        completed_stories = sum(1 for s in level_stories if story_progress.get(s["id"], {}).get("completed"))
        story_pct = (completed_stories / len(level_stories)) if level_stories else None

        in_range = stats["level"] >= lvl_lo
        span = lvl_hi - lvl_lo
        level_pct = max(0.0, min(1.0, (stats["level"] - lvl_lo) / span)) if span else (1.0 if in_range else 0.0)

        card_start()
        st.markdown(f"### {cefr} {'✅' if stats['level'] >= lvl_hi else ('🟡' if in_range else '🔒')}")
        st.markdown(f"Levels {lvl_lo}–{lvl_hi}")
        xp_bar(level_pct)
        if story_pct is not None:
            st.caption(f"Stories: {completed_stories}/{len(level_stories)} completed")
        card_end()


# ----------------------------------------------------------------------------
# PAGE: Statistics
# ----------------------------------------------------------------------------
elif page == "📊 Statistics":
    st.markdown("## 📊 Statistics Dashboard")

    quiz_df = db.get_quiz_results()
    xp_log = db.get_xp_log()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        card_start(); st.metric("Level", stats["level"]); card_end()
    with c2:
        card_start(); st.metric("Total XP", f"{stats['xp']:,}"); card_end()
    with c3:
        card_start(); st.metric("Words Learned", stats["words_saved"]); card_end()
    with c4:
        card_start(); st.metric("Words Mastered", stats["words_mastered"]); card_end()

    if not quiz_df.empty:
        import plotly.express as px
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### Quiz Accuracy by Type")
            acc = quiz_df.groupby("quiz_type").apply(
                lambda g: 100 * g["score"].sum() / g["total"].sum() if g["total"].sum() else 0,
                include_groups=False,
            ).reset_index(name="accuracy")
            fig = px.bar(acc, x="quiz_type", y="accuracy", range_y=[0, 100])
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, width='stretch')
            weakest = acc.loc[acc["accuracy"].idxmin(), "quiz_type"] if len(acc) else "—"
            strongest = acc.loc[acc["accuracy"].idxmax(), "quiz_type"] if len(acc) else "—"
            st.caption(f"Strongest: **{strongest}** · Weakest: **{weakest}**")
        with c2:
            st.markdown("#### Average Quiz Score")
            avg_score = 100 * quiz_df["score"].sum() / quiz_df["total"].sum() if quiz_df["total"].sum() else 0
            st.metric("Average", f"{avg_score:.1f}%")
            st.markdown("#### Quizzes Over Time")
            by_date = quiz_df.groupby("date").size().reset_index(name="count")
            fig2 = px.line(by_date, x="date", y="count")
            fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig2, width='stretch')
    else:
        st.info("Complete some quizzes to see your statistics here.")

    if not xp_log.empty:
        import plotly.express as px
        st.markdown("#### XP Sources")
        by_source = xp_log.groupby("source")["amount"].sum().reset_index().sort_values("amount", ascending=False)
        fig3 = px.pie(by_source, names="source", values="amount", hole=0.5)
        fig3.update_layout(paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig3, width='stretch')

        st.markdown("#### Study Calendar Heatmap (XP earned per day)")
        daily = xp_log.groupby("date")["amount"].sum().reset_index()
        daily["date"] = pd.to_datetime(daily["date"])
        daily["weekday"] = daily["date"].dt.day_name()
        daily["week"] = daily["date"].dt.isocalendar().week
        order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        pivot = daily.pivot_table(index="weekday", columns="week", values="amount", aggfunc="sum").reindex(order)
        fig4 = px.imshow(pivot, aspect="auto", labels=dict(color="XP"))
        fig4.update_layout(paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig4, width='stretch')


# ----------------------------------------------------------------------------
# PAGE: Weekly Challenges
# ----------------------------------------------------------------------------
elif page == "🎯 Weekly Challenges":
    st.markdown("## 🎯 Weekly Challenges")
    week_start = (dt.date.today() - dt.timedelta(days=dt.date.today().weekday())).isoformat()
    challenges = rewards.challenges_for_week(week_start)
    db.ensure_weekly_challenges(week_start, [{"key": c["key"], "target": c["target"]} for c in challenges])
    saved = {c["challenge_key"]: c for c in db.get_weekly_challenges(week_start)}

    st.caption(f"Week of {week_start} — new challenges every Monday.")

    for c in challenges:
        s = saved.get(c["key"], {})
        progress = s.get("progress", 0)
        completed = s.get("completed", 0)
        reward_claimed = s.get("reward_claimed", 0)
        pct = min(1.0, progress / c["target"]) if c["target"] else 0

        card_start()
        st.markdown(f"### {'✅' if completed else '🎯'} {c['label']}")
        st.progress(pct)
        st.caption(f"{progress:.0f} / {c['target']} {c['unit']}")
        st.markdown(f"Reward: **+{c['reward_xp']} XP**, **+{c['reward_coins']} 🪙**")
        if completed and not reward_claimed:
            if st.button("Claim Reward", key=f"claim_{c['key']}", type="primary"):
                db.add_xp(c["reward_xp"], "weekly_challenge")
                db.add_coins(c["reward_coins"])
                db.claim_weekly_reward(week_start, c["key"])
                confetti_burst(150)
                st.rerun()
        elif reward_claimed:
            st.success("Reward claimed!")
        card_end()


# ----------------------------------------------------------------------------
# PAGE: Wallet
# ----------------------------------------------------------------------------
elif page == "💰 Wallet":
    st.markdown("## 💰 Wallet")

    c1, c2 = st.columns(2)
    with c1:
        card_start()
        st.markdown("#### Balance")
        st.markdown(f"# 🪙 {stats['coins']:,}")
        card_end()
    with c2:
        card_start()
        st.markdown("#### Keys")
        key_line = "  &nbsp;&nbsp; ".join(
            f"🔑 {kt.title()}: {profile.get(f'{kt}_keys','0')}"
            for kt in ["common", "uncommon", "rare", "legendary"]
        )
        st.markdown(key_line)
        card_end()

    st.markdown("### 🧾 Recent Purchases")
    recent = db.get_recent_purchases(15)
    if recent.empty:
        st.info("No purchases yet — visit the Shop or open a Loot Chest!")
    else:
        display = recent.copy()
        display["item"] = display["item_id"].apply(lambda i: sc.get_item(i)["name"] if sc.get_item(i) else i)
        display["source"] = display["acquired_via"].map({"shop": "🛍️ Shop", "chest": "📦 Chest"})
        st.dataframe(
            display[["item", "item_type", "rarity", "source", "acquired_at"]],
            width='stretch', hide_index=True,
        )

    st.markdown("---")
    st.markdown("### 🎮 Quick Coin Activity: Word Flip")
    st.caption(
        "A fast der/die/das round for a few extra coins — capped at 5 rounds per day so it "
        "stays a fun bonus rather than a way to farm the economy. +5 🪙 per correct answer."
    )
    plays_today = db.coin_activity_plays_today()
    remaining = max(0, 5 - plays_today)
    st.markdown(f"**Rounds left today: {remaining}/5**")

    if remaining <= 0:
        st.info("You've used today's rounds — come back tomorrow!")
    else:
        if "wallet_flip_q" not in st.session_state:
            st.session_state.wallet_flip_q = None

        if st.session_state.wallet_flip_q is None:
            if st.button("Start Round", type="primary"):
                st.session_state.wallet_flip_q = grammar.make_article_question(random.Random())
                st.rerun()
        else:
            q = st.session_state.wallet_flip_q
            card_start()
            st.markdown(f"### ___ {q['noun']}")
            cols = st.columns(3)
            for i, opt in enumerate(q["options"]):
                with cols[i]:
                    if st.button(opt, key=f"wallet_flip_{opt}", width='stretch'):
                        db.register_coin_activity_play()
                        if opt == q["correct"]:
                            db.add_coins(5)
                            play_sound("coin", profile.get("sound_enabled", "1") == "1")
                            st.success(f"Richtig! +5 🪙")
                        else:
                            st.error(f"Nope — it's **{q['correct']} {q['noun']}**")
                        st.session_state.wallet_flip_q = None
                        st.rerun()
            card_end()


# ----------------------------------------------------------------------------
# PAGE: Shop
# ----------------------------------------------------------------------------
elif page == "🛍️ Shop":
    st.markdown("## 🛍️ Shop")
    st.markdown(f"🪙 Balance: **{stats['coins']:,}**")
    st.caption("Coins never buy learning shortcuts — only cosmetics and fun extras.")

    tab1, tab2, tab3, tab4 = st.tabs(["⭐ Daily Shop", "🏬 Full Catalog", "🔑 Keys", "🎁 Seasonal Shop"])

    with tab1:
        st.caption("Refreshes every 24 hours. Rare chance (2%) for a discounted legendary item!")
        daily_items = _get_daily_shop()
        owned = db.owned_item_ids()
        cols = st.columns(5)
        for i, entry in enumerate(daily_items):
            item = sc.get_item(entry["id"])
            if not item:
                continue
            discounted_price = int(item["price"] * (1 - entry["discount_pct"] / 100))
            with cols[i % 5]:
                card_start()
                is_special = entry.get("is_legendary_special")
                st.markdown(f"{'🌟 ' if is_special else ''}{item['emoji']} **{item['name']}**")
                st.caption(f"{item['rarity'].title()} · -{entry['discount_pct']}%")
                st.markdown(f"~~{item['price']}~~ **{discounted_price}** 🪙")
                if item["id"] in owned:
                    st.caption("Owned ✅")
                elif st.button("Buy", key=f"buy_daily_{item['id']}", width='stretch'):
                    _buy_item(item["id"], discounted_price, profile.get("sound_enabled", "1") == "1")
                card_end()

    with tab2:
        st.caption("Rare and Legendary items aren't sold here — they're exclusive to "
                   "Loot Chests and the Daily Shop's rotation. Keeps them special!")
        type_filter = st.selectbox("Category", ["All"] + sorted({i["type"] for i in sc.CATALOG_TAB_ITEMS}))
        rarity_filter = st.selectbox("Rarity", ["All", "common", "uncommon"])
        items = sc.CATALOG_TAB_ITEMS
        if type_filter != "All":
            items = [i for i in items if i["type"] == type_filter]
        if rarity_filter != "All":
            items = [i for i in items if i["rarity"] == rarity_filter]

        owned = db.owned_item_ids()
        cols = st.columns(4)
        for i, item in enumerate(items):
            with cols[i % 4]:
                card_start()
                st.markdown(f"{item['emoji']} **{item['name']}**")
                st.markdown(rarity_span(item["rarity"], item["rarity"].title()), unsafe_allow_html=True)
                st.markdown(f"**{item['price']}** 🪙")
                if item["id"] in owned:
                    st.caption("Owned ✅")
                elif st.button("Buy", key=f"buy_cat_{item['id']}", width='stretch'):
                    _buy_item(item["id"], item["price"], profile.get("sound_enabled", "1") == "1")
                card_end()

    with tab3:
        st.caption("Keys open Loot Chests in the Loot Chests page.")
        cols = st.columns(4)
        for i, (key_type, price) in enumerate(sc.KEY_PRICES.items()):
            with cols[i]:
                card_start()
                st.markdown(f"🔑 **{key_type.title()} Key**")
                st.markdown(f"You have: {profile.get(f'{key_type}_keys','0')}")
                st.markdown(f"**{price}** 🪙")
                if st.button("Buy Key", key=f"buy_key_{key_type}", width='stretch'):
                    if db.spend_coins(price):
                        db.add_keys(key_type, 1)
                        play_sound("coin", profile.get("sound_enabled", "1") == "1")
                        st.rerun()
                    else:
                        st.error("Not enough coins!")
                card_end()

    with tab4:
        active_now = sc.seasonal_items_active()
        st.caption("Seasonal items are always purchasable in the Full Catalog tab too — "
                   "this tab just highlights what's 'in season' right now.")
        owned = db.owned_item_ids()
        if not active_now:
            st.info("Nothing is in season right now. Check back later, or grab any seasonal "
                    "theme early from the Full Catalog tab.")
        else:
            cols = st.columns(len(active_now))
            for i, item in enumerate(active_now):
                with cols[i]:
                    card_start()
                    st.markdown(f"{item['emoji']} **{item['name']}**")
                    st.markdown(rarity_span(item["rarity"], item["rarity"].title()), unsafe_allow_html=True)
                    st.markdown(f"**{item['price']}** 🪙")
                    if item["id"] in owned:
                        st.caption("Owned ✅")
                    elif st.button("Buy", key=f"buy_seasonal_{item['id']}", width='stretch'):
                        _buy_item(item["id"], item["price"], profile.get("sound_enabled", "1") == "1")
                    card_end()

        st.markdown("#### All Seasonal Themes")
        for item in sc.seasonal_items_all():
            in_season = item in active_now
            st.markdown(f"{'🟢' if in_season else '⚪'} {item['emoji']} {item['name']} "
                        f"{'(in season now)' if in_season else ''}")


# ----------------------------------------------------------------------------
# PAGE: Loot Chests
# ----------------------------------------------------------------------------
elif page == "📦 Loot Chests":
    st.markdown("## 📦 Loot Chests")
    st.caption("Open chests with keys for a chance at cosmetics, pets, and exclusive chest-only items.")

    chest_info = {
        "common": ("📦", "Common: 75% Common · 15% Uncommon · 10% Rare"),
        "uncommon": ("🎁", "Uncommon: 15% Common · 65% Uncommon · 15% Rare · 5% Legendary"),
        "rare": ("💎", "Rare: 5% Common · 25% Uncommon · 60% Rare · 10% Legendary"),
        "legendary": ("🌟", "Legendary: 25% Rare · 75% Legendary"),
    }

    cols = st.columns(4)
    for i, (chest_type, (emoji, odds_label)) in enumerate(chest_info.items()):
        with cols[i]:
            card_start()
            st.markdown(f"### {emoji} {chest_type.title()}")
            st.caption(odds_label)
            keys_owned = int(float(profile.get(f"{chest_type}_keys", "0") or 0))
            st.markdown(f"🔑 Keys: **{keys_owned}**")
            if keys_owned >= 1:
                if st.button(f"Open {chest_type.title()} Chest", key=f"open_{chest_type}"):
                    st.session_state["opening_chest"] = chest_type
                    st.rerun()
            else:
                st.caption("No keys — buy some in the Shop!")
            card_end()

    if st.session_state.get("opening_chest"):
        chest_type = st.session_state["opening_chest"]
        db.spend_key(chest_type)
        won_item = loot.open_chest(chest_type)

        st.markdown("### 🎰 ...")
        spin_html = f"""
        <div style="text-align:center; padding:2rem;">
            <div id="spin" style="font-size:4rem; transition: transform 2s cubic-bezier(.2,.8,.2,1);">
                🎁🎁🎁🎁🎁
            </div>
        </div>
        <script>
        setTimeout(function() {{
            const el = document.getElementById('spin');
            if (el) {{
                el.style.transform = 'rotate(1080deg) scale(1.3)';
                el.innerText = '{won_item["emoji"]}';
            }}
        }}, 100);
        </script>
        """
        st.components.v1.html(spin_html, height=150)

        card_start()
        st.markdown(f"## You won: {won_item['emoji']} {won_item['name']}!")
        st.markdown(rarity_span(won_item["rarity"], won_item["rarity"].upper()), unsafe_allow_html=True)
        card_end()
        confetti_burst(200 if won_item["rarity"] == "legendary" else 100)
        play_sound("unlock", profile.get("sound_enabled", "1") == "1")

        if st.button("Awesome!"):
            del st.session_state["opening_chest"]
            st.rerun()


# ----------------------------------------------------------------------------
# PAGE: Avatar Customization
# ----------------------------------------------------------------------------
elif page == "🧑‍🎨 Avatar":
    st.markdown("## 🧑‍🎨 Avatar Customization")
    st.caption("Equip cosmetics you've earned through learning, shopping, or loot chests. Everything shown here is unlocked, not just bought — nothing here affects learning power.")

    owned = db.owned_item_ids()

    slots = [
        ("Theme", "theme", "equipped_theme"),
        ("Pet", "pet", "equipped_pet"),
        ("Hair", "avatar_hair", "equipped_avatar_hair"),
        ("Clothes", "avatar_clothes", "equipped_avatar_clothes"),
        ("Background", "avatar_bg", "equipped_avatar_bg"),
        ("Frame", "avatar_frame", "equipped_avatar_frame"),
        ("Title", "title", "equipped_title"),
        ("XP Effect", "xp_effect", "equipped_xp_effect"),
    ]

    preview_col, slots_col = st.columns([1, 2])
    with preview_col:
        card_start()
        st.markdown("#### Preview")
        pet_emoji = equipped_pet_emoji(profile)
        bg_item = sc.get_item(profile.get("equipped_avatar_bg", ""))
        st.markdown(f"<div style='font-size:1.2rem;'>{bg_item['emoji'] if bg_item else '🖼️'} "
                    f"{'👤'} {pet_emoji or ''}</div>", unsafe_allow_html=True)
        title_item = sc.get_item(profile.get("equipped_title", ""))
        if title_item:
            st.caption(f"Title: {title_item['name']}")
        card_end()

    with slots_col:
        for label, item_type, profile_key in slots:
            owned_of_type = [sc.get_item(i) for i in owned if sc.get_item(i) and sc.get_item(i)["type"] == item_type]
            if not owned_of_type:
                st.caption(f"**{label}:** nothing owned yet.")
                continue

            # Build option *strings* directly (no format_func) — using format_func here
            # caused a widget-state reconstruction error when navigating away from this
            # page with a selection made, so labels are the actual option values and we
            # map back to the item id afterward.
            none_label = "(None)"
            label_to_id = {f"{i['emoji']} {i['name']}": i["id"] for i in owned_of_type}
            id_to_label = {v: k for k, v in label_to_id.items()}
            options = [none_label] + list(label_to_id.keys())

            current_id = profile.get(profile_key, "") or ""
            current_label = id_to_label.get(current_id, none_label)
            if current_label not in options:
                current_label = none_label

            choice_label = st.selectbox(label, options, index=options.index(current_label),
                                         key=f"equip_{profile_key}")
            if choice_label != current_label:
                new_id = "" if choice_label == none_label else label_to_id[choice_label]
                db.set_profile(profile_key, new_id)
                st.rerun()


# ----------------------------------------------------------------------------
# PAGE: Trophy Room
# ----------------------------------------------------------------------------
elif page == "🏆 Trophy Room":
    st.markdown("## 🏆 Trophy Room")
    st.caption("Achievements, badges, and rare collectibles you've earned.")

    unlocked_keys = db.get_unlocked_achievements()
    defs = ach.achievement_definitions()
    unlocked_count = sum(1 for d in defs if d["key"] in unlocked_keys)
    st.progress(unlocked_count / len(defs) if defs else 0)
    st.caption(f"{unlocked_count} / {len(defs)} achievements unlocked")

    badge_html = "<div style='display:flex;flex-wrap:wrap;'>"
    for a in defs:
        locked_cls = "" if a["key"] in unlocked_keys else "locked"
        badge_html += f"""
        <div class="rpg-badge {locked_cls}" title="{a['desc']}">
            <div class="emoji">{a['emoji']}</div>
            <div class="name">{a['name']}</div>
        </div>"""
    badge_html += "</div>"
    st.markdown(badge_html, unsafe_allow_html=True)

    st.markdown("### Details")
    for a in defs:
        status = "✅" if a["key"] in unlocked_keys else "🔒"
        st.markdown(f"{status} {rarity_span(a['rarity'], a['rarity'].title())} **{a['name']}** — {a['desc']}",
                    unsafe_allow_html=True)

    st.markdown("### 🎒 Collectibles Inventory")
    inv = db.get_inventory()
    if inv.empty:
        st.info("No items yet — visit the Shop or open a Loot Chest!")
    else:
        by_type = inv.groupby("item_type").size().sort_values(ascending=False)
        st.bar_chart(by_type)
        st.dataframe(inv[["item_id", "item_type", "rarity", "acquired_via", "acquired_at"]],
                     width='stretch', hide_index=True)


# ----------------------------------------------------------------------------
# PAGE: Settings
# ----------------------------------------------------------------------------
elif page == "⚙️ Settings":
    st.markdown("## ⚙️ Settings")

    display_name = st.text_input("Display name", value=profile.get("display_name", "Sprachheld"))
    if display_name != profile.get("display_name"):
        db.set_profile("display_name", display_name)
        st.rerun()

    sound_on = st.toggle("🔊 Sound effects", value=profile.get("sound_enabled", "1") == "1")
    if str(int(sound_on)) != profile.get("sound_enabled", "1"):
        db.set_profile("sound_enabled", int(sound_on))
        st.rerun()

    st.markdown("---")
    st.markdown(f"🧊 Streak Freeze tokens: **{profile.get('streak_freeze_tokens','0')}** "
                f"(earned automatically every 7-day streak)")

    st.markdown("---")
    st.markdown("### 💾 Data Export & Backup")
    full_export = db.export_all_data()
    st.download_button(
        "⬇️ Full Backup (JSON)",
        json.dumps(full_export, indent=2, default=str).encode("utf-8"),
        file_name=f"fluent_forest_rpg_backup_{dt.date.today().isoformat()}.json",
        mime="application/json",
    )
    st.caption(f"Database file: `{db.DB_PATH.name}` (local SQLite — everything autosaves, "
               f"no manual Save button anywhere in the app).")

    st.markdown("---")
    st.markdown("### ⚠️ Danger Zone")
    if st.button("Reset ALL progress (cannot be undone)"):
        st.session_state["confirm_reset"] = True
    if st.session_state.get("confirm_reset"):
        st.warning("Are you absolutely sure? This deletes everything.")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Yes, reset everything", type="primary"):
                import os
                db.DB_PATH.unlink(missing_ok=True)
                st.session_state.clear()
                st.rerun()
        with c2:
            if st.button("Cancel"):
                st.session_state["confirm_reset"] = False
                st.rerun()
