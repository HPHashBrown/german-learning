"""Curated resource library for the Personalized Resource Engine.

Honesty note: these link to the *real, stable homepage or channel* for each
resource rather than a specific video/article ID. Deep-linking to a single
video would go stale fast (videos get removed, articles get archived) and
there's no way to verify a specific URL will still resolve by the time
someone clicks it. A channel/show link is guaranteed valid and still gets
the learner to exactly the right place — this is disclosed in the UI rather
than pretending these are exact-episode links.
"""

RESOURCES = [
    # id, category, type, title, url, min_hours, max_hours, difficulty,
    # duration, comprehension_pct, topics, description
    dict(id="slow_german", category="Listening", type="podcast",
         title="Slow German (Podcast by Annik Rubens)",
         url="https://slowgerman.com/",
         min_hours=0, max_hours=80, difficulty="Very Easy",
         duration="10-15 min/ep", comprehension_pct=80,
         topics=["Culture", "Travel"],
         desc="Deliberately slow, clearly-enunciated German aimed squarely at beginners."),
    dict(id="super_easy_german", category="Video", type="video",
         title="Super Easy German (YouTube channel)",
         url="https://www.youtube.com/@SuperEasyGerman",
         min_hours=0, max_hours=100, difficulty="Very Easy",
         duration="5-12 min/ep", comprehension_pct=75,
         topics=["Culture", "Comedy"],
         desc="Street interviews with slow, simple speech and full dual subtitles."),
    dict(id="nicos_weg", category="Course", type="website",
         title="Nicos Weg (DW's free A1-B1 course)",
         url="https://learngerman.dw.com/en/nicos-weg/c-36519898",
         min_hours=0, max_hours=150, difficulty="Very Easy",
         duration="15-20 min/unit", comprehension_pct=85,
         topics=["Grammar", "Daily life"],
         desc="Free structured course from Deutsche Welle with a story-driven format."),
    dict(id="easy_german", category="Video", type="video",
         title="Easy German (YouTube channel)",
         url="https://www.youtube.com/@EasyGerman",
         min_hours=30, max_hours=400, difficulty="Easy",
         duration="10-25 min/ep", comprehension_pct=70,
         topics=["Culture", "Travel", "Daily life"],
         desc="Real unscripted street interviews across German-speaking cities, dual subtitles."),
    dict(id="dw_langsam_nachrichten", category="Listening", type="podcast",
         title="DW Langsam gesprochene Nachrichten",
         url="https://www.dw.com/de/langsam-gesprochene-nachrichten/s-8034",
         min_hours=50, max_hours=300, difficulty="Easy",
         duration="5-8 min/ep", comprehension_pct=70,
         topics=["News", "Politics"],
         desc="Real daily news, read slowly and clearly for learners."),
    dict(id="logo_nachrichten", category="Video", type="video",
         title="logo! Kindernachrichten (Tagesschau für Kinder)",
         url="https://www.tagesschau.de/kinder/",
         min_hours=50, max_hours=300, difficulty="Easy",
         duration="10 min/ep", comprehension_pct=65,
         topics=["News"],
         desc="News explained for German children — same real topics, much simpler language."),
    dict(id="deutsch_perfekt", category="Reading", type="article",
         title="Deutsch Perfekt (graded-difficulty magazine)",
         url="https://www.deutsch-perfekt.com/",
         min_hours=100, max_hours=500, difficulty="Comfortable",
         duration="10-15 min/article", comprehension_pct=65,
         topics=["Culture", "Business", "Travel"],
         desc="Articles tagged by difficulty level with built-in vocabulary support."),
    dict(id="kurzgesagt", category="Video", type="video",
         title="Kurzgesagt – In a Nutshell",
         url="https://www.youtube.com/@kurzgesagt",
         min_hours=150, max_hours=700, difficulty="Comfortable",
         duration="8-12 min/ep", comprehension_pct=60,
         topics=["Science", "Philosophy"],
         desc="Beautifully animated science explainers — try switching audio/subtitles to German where available."),
    dict(id="terra_x", category="Video", type="documentary",
         title="Terra X (ZDF documentary strand)",
         url="https://www.zdf.de/dokumentation/terra-x",
         min_hours=200, max_hours=800, difficulty="Comfortable",
         duration="30-45 min/ep", comprehension_pct=55,
         topics=["History", "Science", "Nature"],
         desc="Long-running native German documentary series covering history, nature, and science."),
    dict(id="tagesschau", category="News", type="video",
         title="Tagesschau (main German news broadcast)",
         url="https://www.tagesschau.de/",
         min_hours=300, max_hours=999999, difficulty="Challenging",
         duration="15 min/broadcast", comprehension_pct=50,
         topics=["News", "Politics", "Business"],
         desc="The flagship native news broadcast — full native speed and vocabulary."),
    dict(id="deutschlandfunk", category="Listening", type="podcast",
         title="Deutschlandfunk (native news & culture radio)",
         url="https://www.deutschlandfunk.de/",
         min_hours=400, max_hours=999999, difficulty="Challenging",
         duration="Varies", comprehension_pct=50,
         topics=["News", "Politics", "Philosophy"],
         desc="Native public radio — news, culture, and long-form discussion at natural pace."),
    dict(id="netflix_de", category="Entertainment", type="streaming",
         title="Netflix — German-audio titles",
         url="https://www.netflix.com/",
         min_hours=300, max_hours=999999, difficulty="Challenging",
         duration="20-50 min/ep", comprehension_pct=55,
         topics=["Comedy", "Drama"],
         desc="Search Netflix's German-language originals (e.g. Dark, Barbaren) and switch audio to German with German subtitles."),
    dict(id="twitch_de", category="Entertainment", type="streaming",
         title="Twitch — German-language streamers",
         url="https://www.twitch.tv/directory/language/de",
         min_hours=600, max_hours=999999, difficulty="Very Hard",
         duration="Live, hours", comprehension_pct=45,
         topics=["Gaming", "Comedy"],
         desc="Live, fast, informal native speech — filter Twitch's directory by German language."),
]

CATEGORY_TO_ACTIVITY = {
    "Listening": "Listening", "Video": "Watching (YouTube)", "Reading": "Reading",
    "News": "Reading", "Entertainment": "Movies/TV", "Course": "Grammar",
}


def resources_for(total_hours: float, topics_filter=None, exclude_ids=None, limit=6):
    exclude_ids = exclude_ids or set()
    candidates = [
        r for r in RESOURCES
        if r["min_hours"] <= total_hours <= r["max_hours"] and r["id"] not in exclude_ids
    ]
    if topics_filter:
        filtered = [r for r in candidates if any(t in r["topics"] for t in topics_filter)]
        if filtered:
            candidates = filtered
    if not candidates:
        # widen the net rather than showing nothing
        candidates = [r for r in RESOURCES if r["id"] not in exclude_ids] or RESOURCES
    return candidates[:limit]


def why_selected(resource, total_hours):
    return (
        f"Matches your {total_hours:.0f}h logged (typical range {resource['min_hours']}-"
        f"{resource['max_hours'] if resource['max_hours'] < 999999 else '∞'}h) and its "
        f"{resource['difficulty'].lower()} difficulty."
    )
