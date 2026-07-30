"""Grammar Explorer content tree + Verb Trainer conjugation data +
Article Trainer word list."""

GRAMMAR_TREE = {
    "Cases": {
        "min_level": 10,
        "lessons": [
            dict(title="The Four Cases", body=(
                "German has four grammatical cases: Nominative (subject), Accusative "
                "(direct object), Dative (indirect object), and Genitive (possession). "
                "The case changes the article and sometimes the noun/adjective ending."
            ), examples=["Der Hund (Nom.) sieht den Mann (Akk.).",
                         "Ich gebe dem Mann (Dat.) das Buch.", "das Auto des Mannes (Gen.)"]),
        ],
        "quiz": [
            dict(q="Ich sehe ___ Hund. (der Hund, accusative)", options=["der", "den", "dem", "des"], correct="den"),
            dict(q="Ich gebe ___ Frau das Buch. (die Frau, dative)", options=["die", "der", "den", "das"], correct="der"),
        ],
    },
    "Nouns & Articles": {
        "min_level": 10,
        "lessons": [
            dict(title="Gender & Articles", body=(
                "Every German noun has a grammatical gender: masculine (der), feminine "
                "(die), or neuter (das). Gender isn't always predictable from meaning, "
                "so it's usually memorized along with the noun."
            ), examples=["der Tisch (the table)", "die Lampe (the lamp)", "das Fenster (the window)"]),
        ],
        "quiz": [
            dict(q="___ Buch (book)", options=["der", "die", "das"], correct="das"),
            dict(q="___ Katze (cat)", options=["der", "die", "das"], correct="die"),
        ],
    },
    "Verbs": {
        "min_level": 10,
        "lessons": [
            dict(title="Present Tense Conjugation", body=(
                "Regular (weak) verbs conjugate by removing -en from the infinitive and "
                "adding an ending for each person: -e, -st, -t, -en, -t, -en."
            ), examples=["ich mache", "du machst", "er/sie/es macht", "wir machen"]),
        ],
        "quiz": [
            dict(q="du ___ (machen)", options=["mache", "machst", "macht", "machen"], correct="machst"),
        ],
    },
    "Adjectives": {
        "min_level": 10,
        "lessons": [
            dict(title="Adjective Endings", body=(
                "Adjective endings change based on the case, gender, and whether a "
                "definite/indefinite article precedes the adjective."
            ), examples=["der gute Mann", "ein guter Mann", "die gute Frau"]),
        ],
        "quiz": [
            dict(q="ein gut__ Mann", options=["e", "er", "es", "en"], correct="er"),
        ],
    },
    "Sentence Structure": {
        "min_level": 10,
        "lessons": [
            dict(title="Verb-Second (V2) Word Order", body=(
                "In main clauses, the conjugated verb is always the second element — "
                "not necessarily the second word. Whatever comes first (subject, time, "
                "etc.) is followed immediately by the verb."
            ), examples=["Heute gehe ich ins Kino.", "Ich gehe heute ins Kino."]),
        ],
        "quiz": [
            dict(q="Which is correct?", options=["Heute ich gehe ins Kino.", "Heute gehe ich ins Kino."],
                 correct="Heute gehe ich ins Kino."),
        ],
    },
    "Passive Voice": {
        "min_level": 10,
        "lessons": [
            dict(title="The Passive Voice", body=(
                "The passive voice is formed with a conjugated form of werden + the past "
                "participle. The focus shifts from who does the action to what happens to "
                "the subject."
            ), examples=["Das Haus wird gebaut. (The house is being built.)",
                         "Der Brief wurde geschrieben. (The letter was written.)"]),
        ],
        "quiz": [
            dict(q="Das Auto ___ repariert. (passive, present)", options=["ist", "wird", "hat", "war"], correct="wird"),
        ],
    },
    "Subjunctive": {
        "min_level": 10,
        "lessons": [
            dict(title="Konjunktiv II (Subjunctive)", body=(
                "Konjunktiv II expresses hypotheticals, wishes, and politeness — "
                "'would/could/should' in English. Common forms: würde + infinitive, "
                "hätte, wäre, könnte."
            ), examples=["Ich würde gerne kommen. (I would like to come.)",
                         "Wenn ich Zeit hätte, ... (If I had time, ...)"]),
        ],
        "quiz": [
            dict(q="Wenn ich reich ___, würde ich reisen.", options=["bin", "wäre", "war", "sei"], correct="wäre"),
        ],
    },
}


# ------------------------------------------------------------- Verb Trainer --
REGULAR_VERBS = ["machen", "spielen", "lernen", "arbeiten", "kaufen", "wohnen", "kochen", "hören"]
IRREGULAR_VERBS = {
    "sein": ["bin", "bist", "ist", "sind", "seid", "sind"],
    "haben": ["habe", "hast", "hat", "haben", "habt", "haben"],
    "werden": ["werde", "wirst", "wird", "werden", "werdet", "werden"],
    "gehen": ["gehe", "gehst", "geht", "gehen", "geht", "gehen"],
    "fahren": ["fahre", "fährst", "fährt", "fahren", "fahrt", "fahren"],
    "sehen": ["sehe", "siehst", "sieht", "sehen", "seht", "sehen"],
    "essen": ["esse", "isst", "isst", "essen", "esst", "essen"],
    "sprechen": ["spreche", "sprichst", "spricht", "sprechen", "sprecht", "sprechen"],
    "lesen": ["lese", "liest", "liest", "lesen", "lest", "lesen"],
    "nehmen": ["nehme", "nimmst", "nimmt", "nehmen", "nehmt", "nehmen"],
}
PRONOUNS = ["ich", "du", "er/sie/es", "wir", "ihr", "sie/Sie"]


def _regular_conjugation(verb: str):
    stem = verb[:-2] if verb.endswith("en") else verb[:-1]
    # Stems ending in -t/-d (and a few consonant clusters like -chn, -ffn, -gn, -dn)
    # insert an -e- before consonant-initial endings so the result is pronounceable:
    # arbeiten -> arbeite, arbeitest, arbeitet, arbeiten, arbeitet, arbeiten.
    needs_e = stem.endswith(("t", "d")) or stem.endswith(("chn", "ffn", "gn", "dn"))
    if needs_e:
        return [stem + "e", stem + "est", stem + "et", stem + "en", stem + "et", stem + "en"]
    return [stem + "e", stem + "st", stem + "t", stem + "en", stem + "t", stem + "en"]


def conjugate(verb: str):
    if verb in IRREGULAR_VERBS:
        return IRREGULAR_VERBS[verb]
    return _regular_conjugation(verb)


def make_verb_question(mode: str, rng=None):
    """mode: timed/infinite/random use all verbs; weak = regular only; strong = irregular only."""
    import random
    rng = rng or random.Random()
    if mode == "weak":
        verb = rng.choice(REGULAR_VERBS)
    elif mode == "strong":
        verb = rng.choice(list(IRREGULAR_VERBS.keys()))
    else:
        verb = rng.choice(REGULAR_VERBS + list(IRREGULAR_VERBS.keys()))

    pronoun_idx = rng.randrange(6)
    correct_form = conjugate(verb)[pronoun_idx]
    return {
        "verb": verb, "pronoun": PRONOUNS[pronoun_idx],
        "pronoun_idx": pronoun_idx, "correct": correct_form,
    }


# ---------------------------------------------------------- Article Trainer --
ARTICLE_WORDS = [
    ("Hund", "der"), ("Katze", "die"), ("Buch", "das"), ("Tisch", "der"),
    ("Lampe", "die"), ("Fenster", "das"), ("Auto", "das"), ("Frau", "die"),
    ("Mann", "der"), ("Kind", "das"), ("Stadt", "die"), ("Land", "das"),
    ("Baum", "der"), ("Blume", "die"), ("Haus", "das"), ("Schule", "die"),
    ("Lehrer", "der"), ("Straße", "die"), ("Zimmer", "das"), ("Garten", "der"),
]


def make_article_question(rng=None):
    import random
    rng = rng or random.Random()
    noun, correct = rng.choice(ARTICLE_WORDS)
    return {"noun": noun, "correct": correct, "options": ["der", "die", "das"]}
