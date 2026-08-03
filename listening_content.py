"""Listening Practice content bank.

Each entry provides everything needed for all three exercise types:
- Fill in the Blank: one word is removed from the sentence; player picks it
  from multiple-choice options.
- Translate: player hears the sentence and picks the correct English
  translation from multiple-choice options (free-text grading of a full
  sentence translation is too fragile to grade reliably without an AI call,
  so this stays multiple-choice for objective, reliable scoring).
- Listen & Identify: player hears the sentence and picks which of several
  similar-looking written German sentences matches what was said — tests
  fine-grained listening discrimination rather than duplicating the
  Pronunciation Trainer's speaking-practice role.

Difficulty increases through the list (A1 -> B2), per the brief's
"difficulty increases" requirement — pages further into the bank are harder.
"""

SENTENCES = [
    # ---- A1 ----
    dict(id="l01", level="A1", text="Ich heiße Anna.", translation="My name is Anna.",
         blank_word="heiße", blank_options=["heiße", "wohne", "komme", "spiele"],
         similar_sentences=["Ich heiße Anna.", "Ich heiße Anja.", "Sie heißt Anna.", "Ich wohne in Anna."]),
    dict(id="l02", level="A1", text="Der Hund ist braun.", translation="The dog is brown.",
         blank_word="braun", blank_options=["braun", "blau", "groß", "klein"],
         similar_sentences=["Der Hund ist braun.", "Die Katze ist braun.", "Der Hund ist grau.", "Der Hund war braun."]),
    dict(id="l03", level="A1", text="Wir essen um sieben Uhr.", translation="We eat at seven o'clock.",
         blank_word="sieben", blank_options=["sieben", "sechs", "acht", "neun"],
         similar_sentences=["Wir essen um sieben Uhr.", "Wir essen um sieben Uhr abends.",
                             "Sie essen um sieben Uhr.", "Wir schlafen um sieben Uhr."]),
    dict(id="l04", level="A1", text="Das Buch liegt auf dem Tisch.", translation="The book is lying on the table.",
         blank_word="Tisch", blank_options=["Tisch", "Stuhl", "Boden", "Bett"],
         similar_sentences=["Das Buch liegt auf dem Tisch.", "Das Buch liegt unter dem Tisch.",
                             "Die Tasse liegt auf dem Tisch.", "Das Buch liegt auf dem Stuhl."]),

    # ---- A2 ----
    dict(id="l05", level="A2", text="Gestern bin ich ins Kino gegangen.", translation="Yesterday I went to the cinema.",
         blank_word="Kino", blank_options=["Kino", "Museum", "Park", "Büro"],
         similar_sentences=["Gestern bin ich ins Kino gegangen.", "Heute bin ich ins Kino gegangen.",
                             "Gestern bin ich ins Museum gegangen.", "Gestern ist er ins Kino gegangen."]),
    dict(id="l06", level="A2", text="Können Sie mir bitte helfen?", translation="Can you help me, please?",
         blank_word="helfen", blank_options=["helfen", "zeigen", "folgen", "danken"],
         similar_sentences=["Können Sie mir bitte helfen?", "Könnten Sie mir bitte helfen?",
                             "Kannst du mir bitte helfen?", "Können Sie ihm bitte helfen?"]),
    dict(id="l07", level="A2", text="Ich habe meinen Schlüssel verloren.", translation="I lost my key.",
         blank_word="Schlüssel", blank_options=["Schlüssel", "Ausweis", "Pass", "Regenschirm"],
         similar_sentences=["Ich habe meinen Schlüssel verloren.", "Ich habe meinen Schlüssel vergessen.",
                             "Du hast deinen Schlüssel verloren.", "Ich habe meinen Ausweis verloren."]),
    dict(id="l08", level="A2", text="Das Wetter wird morgen besser.", translation="The weather will be better tomorrow.",
         blank_word="morgen", blank_options=["morgen", "heute", "bald", "später"],
         similar_sentences=["Das Wetter wird morgen besser.", "Das Wetter wird heute besser.",
                             "Das Wetter wird morgen schlechter.", "Das Wetter war gestern besser."]),

    # ---- B1 ----
    dict(id="l09", level="B1", text="Ich würde gerne mehr über das Projekt erfahren.",
         translation="I would like to learn more about the project.",
         blank_word="Projekt", blank_options=["Projekt", "Thema", "Angebot", "Ergebnis"],
         similar_sentences=["Ich würde gerne mehr über das Projekt erfahren.",
                             "Ich möchte gerne mehr über das Projekt erfahren.",
                             "Ich würde gerne mehr über das Thema erfahren.",
                             "Wir würden gerne mehr über das Projekt erfahren."]),
    dict(id="l10", level="B1", text="Obwohl es regnete, sind wir spazieren gegangen.",
         translation="Although it was raining, we went for a walk.",
         blank_word="regnete", blank_options=["regnete", "schneite", "stürmte", "hagelte"],
         similar_sentences=["Obwohl es regnete, sind wir spazieren gegangen.",
                             "Weil es regnete, sind wir spazieren gegangen.",
                             "Obwohl es regnete, sind wir zu Hause geblieben.",
                             "Obwohl es schneite, sind wir spazieren gegangen."]),
    dict(id="l11", level="B1", text="Die Besprechung wurde auf nächste Woche verschoben.",
         translation="The meeting was postponed to next week.",
         blank_word="verschoben", blank_options=["verschoben", "abgesagt", "verlängert", "geplant"],
         similar_sentences=["Die Besprechung wurde auf nächste Woche verschoben.",
                             "Die Besprechung wurde auf nächsten Monat verschoben.",
                             "Die Besprechung wurde abgesagt.",
                             "Der Termin wurde auf nächste Woche verschoben."]),

    # ---- B2 ----
    dict(id="l12", level="B2", text="Trotz der Herausforderungen konnte das Team seine Ziele erreichen.",
         translation="Despite the challenges, the team was able to achieve its goals.",
         blank_word="Herausforderungen", blank_options=["Herausforderungen", "Schwierigkeiten", "Bedenken", "Verzögerungen"],
         similar_sentences=["Trotz der Herausforderungen konnte das Team seine Ziele erreichen.",
                             "Wegen der Herausforderungen konnte das Team seine Ziele nicht erreichen.",
                             "Trotz der Herausforderungen konnte das Team seinen Zeitplan einhalten.",
                             "Trotz der Schwierigkeiten konnte das Team seine Ziele erreichen."]),
    dict(id="l13", level="B2", text="Es ist unwahrscheinlich, dass sich die Lage kurzfristig verbessert.",
         translation="It's unlikely that the situation will improve in the short term.",
         blank_word="unwahrscheinlich", blank_options=["unwahrscheinlich", "wahrscheinlich", "sicher", "möglich"],
         similar_sentences=["Es ist unwahrscheinlich, dass sich die Lage kurzfristig verbessert.",
                             "Es ist wahrscheinlich, dass sich die Lage kurzfristig verbessert.",
                             "Es ist unwahrscheinlich, dass sich die Lage langfristig verbessert.",
                             "Es ist unklar, ob sich die Lage kurzfristig verbessert."]),
]


def sentences_for_level(player_level: int):
    """Difficulty increases with player level, per the brief. Below Level 25
    only A1/A2 sentences appear; B1 unlocks at 25, B2 at 35."""
    allowed_cefr = ["A1", "A2"]
    if player_level >= 25:
        allowed_cefr.append("B1")
    if player_level >= 35:
        allowed_cefr.append("B2")
    return [s for s in SENTENCES if s["level"] in allowed_cefr]
