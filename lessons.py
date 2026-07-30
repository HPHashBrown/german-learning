"""Vocabulary lesson content, organized into the categories referenced by the
level-unlock system. Each entry is (german, english, gender_or_dash).
This is a representative starter set per category — structured so more words
can be appended trivially without touching any other code."""

LESSONS = {
    "Greetings": [
        ("Hallo", "Hello", "—"), ("Guten Morgen", "Good morning", "—"),
        ("Guten Tag", "Good day", "—"), ("Guten Abend", "Good evening", "—"),
        ("Auf Wiedersehen", "Goodbye", "—"), ("Tschüss", "Bye", "—"),
        ("Wie geht's?", "How's it going?", "—"), ("Danke", "Thank you", "—"),
        ("Bitte", "Please / You're welcome", "—"), ("Entschuldigung", "Excuse me / Sorry", "—"),
    ],
    "Numbers": [
        ("eins", "one", "—"), ("zwei", "two", "—"), ("drei", "three", "—"),
        ("vier", "four", "—"), ("fünf", "five", "—"), ("sechs", "six", "—"),
        ("sieben", "seven", "—"), ("acht", "eight", "—"), ("neun", "nine", "—"),
        ("zehn", "ten", "—"), ("zwanzig", "twenty", "—"), ("hundert", "hundred", "—"),
    ],
    "Colors": [
        ("rot", "red", "—"), ("blau", "blue", "—"), ("grün", "green", "—"),
        ("gelb", "yellow", "—"), ("schwarz", "black", "—"), ("weiß", "white", "—"),
        ("orange", "orange", "—"), ("lila", "purple", "—"), ("rosa", "pink", "—"),
        ("braun", "brown", "—"),
    ],
    "Basic Vocabulary": [
        ("das Haus", "the house", "n"), ("der Hund", "the dog", "m"),
        ("die Katze", "the cat", "f"), ("das Wasser", "the water", "n"),
        ("das Brot", "the bread", "n"), ("der Tisch", "the table", "m"),
        ("die Tür", "the door", "f"), ("das Buch", "the book", "n"),
        ("die Zeit", "the time", "f"), ("der Tag", "the day", "m"),
    ],
    "Restaurant Vocabulary": [
        ("die Speisekarte", "the menu", "f"), ("die Rechnung", "the bill", "f"),
        ("bestellen", "to order", "—"), ("das Trinkgeld", "the tip", "n"),
        ("die Vorspeise", "the appetizer", "f"), ("das Hauptgericht", "the main course", "n"),
        ("der Nachtisch", "the dessert", "m"), ("die Gabel", "the fork", "f"),
        ("das Messer", "the knife", "n"), ("der Löffel", "the spoon", "m"),
    ],
    "Travel German": [
        ("der Flughafen", "the airport", "m"), ("der Bahnhof", "the train station", "m"),
        ("das Gepäck", "the luggage", "n"), ("die Fahrkarte", "the ticket", "f"),
        ("die Ankunft", "the arrival", "f"), ("die Abfahrt", "the departure", "f"),
        ("das Hotel", "the hotel", "n"), ("die Unterkunft", "the accommodation", "f"),
        ("der Reisepass", "the passport", "m"), ("die Grenze", "the border", "f"),
    ],
    "Business German": [
        ("die Besprechung", "the meeting", "f"), ("der Vertrag", "the contract", "m"),
        ("das Angebot", "the offer/quote", "n"), ("die Frist", "the deadline", "f"),
        ("der Kollege", "the colleague (m)", "m"), ("die Kollegin", "the colleague (f)", "f"),
        ("verhandeln", "to negotiate", "—"), ("die Rechnung", "the invoice", "f"),
        ("der Umsatz", "the revenue", "m"), ("die Kündigung", "the termination/notice", "f"),
    ],
}

CATEGORY_MIN_LEVEL = {
    "Greetings": 1, "Numbers": 1, "Colors": 1, "Basic Vocabulary": 1,
    "Restaurant Vocabulary": 2, "Travel German": 5, "Business German": 30,
}


def available_categories(level: int):
    return [c for c, min_lvl in CATEGORY_MIN_LEVEL.items() if level >= min_lvl]


def make_quiz(category: str, num_questions: int = 8, rng=None):
    """Generates a multiple-choice quiz: each question shows the German word,
    4 English options (1 correct + 3 distractors from elsewhere in the category
    or, if too small, from the whole bank)."""
    import random
    rng = rng or random.Random()
    words = LESSONS.get(category, [])
    if len(words) < 4:
        # borrow distractors from other categories if the category is tiny
        pool = [w for cat in LESSONS.values() for w in cat if w not in words]
    else:
        pool = words

    n = min(num_questions, len(words))
    chosen = rng.sample(words, n)
    questions = []
    for de, en, gender in chosen:
        distractor_pool = [w for w in pool if w[1] != en]
        distractors = rng.sample(distractor_pool, min(3, len(distractor_pool)))
        options = [en] + [d[1] for d in distractors]
        rng.shuffle(options)
        questions.append({
            "prompt": de, "correct": en, "options": options, "gender": gender,
        })
    return questions
