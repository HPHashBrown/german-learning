"""True spaced repetition using the SM-2 algorithm (the same core algorithm
behind Anki/SuperMemo). Grades are 0-5:
  0-2 = fail (forgot / hard), 3 = correct with difficulty, 4 = correct, 5 = easy.
"""

import datetime as dt

MIN_EASE = 1.3


def sm2(ease: float, interval_days: float, repetitions: int, grade: int):
    """Returns (new_ease, new_interval_days, new_repetitions, new_srs_state)."""
    grade = max(0, min(5, grade))

    if grade < 3:
        # Failed recall — reset repetitions, review again soon.
        repetitions = 0
        interval = 1
        state = "Learning"
    else:
        if repetitions == 0:
            interval = 1
        elif repetitions == 1:
            interval = 6
        else:
            interval = round(interval_days * ease, 1)
        repetitions += 1
        state = "Review" if interval < 21 else "Mastered"

    new_ease = ease + (0.1 - (5 - grade) * (0.08 + (5 - grade) * 0.02))
    new_ease = max(MIN_EASE, round(new_ease, 2))

    return new_ease, interval, repetitions, state


def next_due_date(interval_days: float, today: dt.date = None) -> str:
    today = today or dt.date.today()
    return (today + dt.timedelta(days=max(1, round(interval_days)))).isoformat()
