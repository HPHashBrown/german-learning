"""PDF progress report generation, using reportlab (per /mnt/skills/public/pdf/SKILL.md)."""

import io
import datetime as dt

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
)

import db
import intelligence as intel


def build_progress_report_pdf(profile: dict) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter, topMargin=0.75 * inch, bottomMargin=0.75 * inch)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("FFTitle", parent=styles["Title"], textColor=colors.HexColor("#2e2158"))
    h2 = ParagraphStyle("FFH2", parent=styles["Heading2"], textColor=colors.HexColor("#4a3a8a"))
    body = styles["Normal"]

    story = []
    name = profile.get("display_name", "Sprachfreund")
    story.append(Paragraph(f"Fluent Forest: German — Progress Report", title_style))
    story.append(Paragraph(f"Prepared for {name} on {dt.date.today().strftime('%d %B %Y')}", body))
    story.append(Spacer(1, 16))

    totals = db.totals()
    forecast = intel.progress_forecast()

    story.append(Paragraph("Overview", h2))
    overview_rows = [
        ["Total hours studied", f"{totals['total_hours']}h"],
        ["Current streak", f"{profile.get('current_streak', '0')} days"],
        ["Longest streak", f"{profile.get('longest_streak', '0')} days"],
        ["Estimated CEFR level", forecast["current_level"]],
        ["XP", f"{int(float(profile.get('xp', '0'))):,}"],
        ["Sessions logged", str(totals["sessions"])],
    ]
    t = Table(overview_rows, colWidths=[220, 250])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#eee8fb")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t)
    story.append(Spacer(1, 16))

    if forecast["next_level"]:
        story.append(Paragraph("Forecast", h2))
        story.append(Paragraph(
            f"Approximately {forecast['hours_remaining']}h remaining to reach "
            f"{forecast['next_level']}, based on a recent pace of {forecast['weekly_pace']}h/week.",
            body,
        ))
        if forecast["est_date_current_pace"]:
            story.append(Paragraph(
                f"At your current pace, estimated arrival: "
                f"{forecast['est_date_current_pace'].strftime('%d %B %Y')}.", body))
        if forecast["est_date_faster_pace"]:
            story.append(Paragraph(
                f"At a 25% faster pace, estimated arrival: "
                f"{forecast['est_date_faster_pace'].strftime('%d %B %Y')}.", body))
        story.append(Spacer(1, 16))

    profile_data = intel.derive_learning_profile()
    if profile_data:
        story.append(Paragraph("Learning Profile", h2))
        rows = [
            ["Favorite method (most sessions)", profile_data["favorite_method"]],
            ["Most successful method (most hours)", profile_data["most_successful_method"]],
            ["Average session length", f"{profile_data['avg_session_minutes']} min"],
            ["Favorite study day", profile_data["favorite_day"]],
        ]
        t2 = Table(rows, colWidths=[260, 210])
        t2.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#eee8fb")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(t2)
        story.append(Spacer(1, 16))

    achievements = db.get_unlocked_achievements()
    story.append(Paragraph("Achievements", h2))
    story.append(Paragraph(f"{len(achievements)} unlocked so far.", body))
    story.append(Spacer(1, 16))

    words_df = db.get_saved_words()
    story.append(Paragraph("Vocabulary", h2))
    story.append(Paragraph(f"{len(words_df)} words saved to your personal dictionary.", body))

    doc.build(story)
    buf.seek(0)
    return buf.read()
