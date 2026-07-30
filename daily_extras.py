"""Random Daily Extras: a German idiom, an interesting Germany/Austria/
Switzerland fact, and a quote — one of each per day, deterministic per date
so it doesn't reroll on refresh, and rotates daily via a simple index."""

import datetime as dt

IDIOMS = [
    ("Ich verstehe nur Bahnhof.", "I only understand train station (= I don't understand anything at all)."),
    ("Da liegt der Hund begraben.", "That's where the dog is buried (= that's the real reason/root of the problem)."),
    ("Tomaten auf den Augen haben.", "To have tomatoes on your eyes (= to fail to notice something obvious)."),
    ("Die Katze im Sack kaufen.", "To buy the cat in the sack (= to buy something sight unseen)."),
    ("Ins Fettnäpfchen treten.", "To step into the little fat-pot (= to put your foot in your mouth)."),
    ("Alles hat ein Ende, nur die Wurst hat zwei.", "Everything has one end, only the sausage has two (playful proverb about endings)."),
    ("Jemandem die Daumen drücken.", "To press your thumbs for someone (= to keep your fingers crossed for them)."),
    ("Das ist mir Wurst.", "That's sausage to me (= I don't care either way)."),
    ("Um den heißen Brei herumreden.", "To talk around the hot porridge (= to beat around the bush)."),
    ("Kein Schwein war da.", "No pig was there (= literally nobody showed up)."),
    ("Da steppt der Bär.", "That's where the bear dances (= that's where the party's happening)."),
    ("Hummeln im Hintern haben.", "To have bumblebees in your backside (= to be very restless/fidgety)."),
    ("Schwein haben.", "To have pig (= to get lucky)."),
    ("Mit dem falschen Bein aufstehen.", "To get up with the wrong leg (= to wake up in a bad mood)."),
    ("Die Nase voll haben.", "To have your nose full (= to be fed up with something)."),
]

FACTS = [
    "Germany has over 1,500 different types of sausage (Wurst).",
    "The Autobahn has no general speed limit on many stretches — but roughly half of it does have posted limits.",
    "Switzerland has four official languages: German, French, Italian, and Romansh.",
    "Oktoberfest actually starts in September, not October, in Munich.",
    "Austria's Hallstatt is over 7,000 years old and one of the oldest known settlements in Europe.",
    "The world's oldest continuously operating restaurant, St. Peter Stiftskulinarium, is in Salzburg, Austria (since 803 AD).",
    "Berlin has more bridges than Venice — over 950 of them.",
    "German is the most widely spoken native language in the European Union.",
    "The Brothers Grimm collected their famous fairy tales largely from oral storytellers in Hesse, Germany.",
    "Switzerland's Large Hadron Collider (CERN) sits partly under the France-Switzerland border.",
    "Germany's Neuschwanstein Castle inspired Disney's Sleeping Beauty castle.",
    "Vienna, Austria has been ranked one of the world's most livable cities for years running.",
    "German has some famously long compound words, like Rindfleischetikettierungsüberwachungsaufgabenübertragungsgesetz (a now-repealed beef-labeling law).",
    "Cuckoo clocks actually originated in Germany's Black Forest region, not Switzerland.",
    "Switzerland has more castles per square kilometer than almost any other country.",
]

QUOTES = [
    ("Man lernt eine Sprache am besten dort, wo man sie leben muss.", "German proverb"),
    ("Die Grenzen meiner Sprache bedeuten die Grenzen meiner Welt.", "Ludwig Wittgenstein"),
    ("Wer fremde Sprachen nicht kennt, weiß nichts von seiner eigenen.", "Johann Wolfgang von Goethe"),
    ("Es ist nicht genug zu wissen, man muss es auch anwenden.", "Johann Wolfgang von Goethe"),
    ("Übung macht den Meister.", "German proverb"),
    ("Aller Anfang ist schwer.", "German proverb"),
    ("Was dich nicht umbringt, macht dich stärker.", "Friedrich Nietzsche"),
    ("Wer nichts weiß, muss alles glauben.", "Marie von Ebner-Eschenbach"),
    ("Der Weg ist das Ziel.", "German saying"),
    ("Man sieht nur mit dem Herzen gut.", "Antoine de Saint-Exupéry (German translation)"),
]


def _pick(pool, today: dt.date):
    return pool[today.toordinal() % len(pool)]


def daily_extras(today: dt.date = None) -> dict:
    today = today or dt.date.today()
    idiom, idiom_meaning = _pick(IDIOMS, today)
    fact = _pick(FACTS, today + dt.timedelta(days=1))  # offset so idiom/fact/quote don't all cycle in lockstep
    quote, quote_author = _pick(QUOTES, today + dt.timedelta(days=2))
    return {
        "idiom": idiom, "idiom_meaning": idiom_meaning,
        "fact": fact,
        "quote": quote, "quote_author": quote_author,
    }
