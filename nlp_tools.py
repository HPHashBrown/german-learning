"""Sentence breakdown tool.

Real grammatical analysis (case, verb position, separable verbs, idioms,
etc.) requires actual language understanding — a hand-written rule table
would silently mislabel plenty of real sentences, which is worse than
being upfront about it. So this module calls the Anthropic API when the
user supplies a key, and otherwise falls back to a clearly-labeled
word-by-word lookup against the small local dictionary (content.MINI_DICTIONARY)
so the app still *works* offline, just with reduced grammar detail.
"""

import json
import re
from content import MINI_DICTIONARY

SYSTEM_PROMPT = """You are a precise German grammar analyzer for a language-learning app.
Given a German sentence, return ONLY valid JSON (no markdown fences, no commentary) with this exact shape:

{
  "words": [
    {"word": "Ich", "base_form": "ich", "meaning": "I", "grammar": "pronoun"},
    ...
  ],
  "cases_explained": "short explanation of the cases used in this sentence",
  "word_order_notes": "short explanation of verb position / word order",
  "separable_verbs": "note any separable-prefix verbs found, or 'None'",
  "idioms": "note any idioms/fixed expressions, or 'None'",
  "literal_translation": "word-for-word English gloss",
  "natural_translation": "natural fluent English translation",
  "difficulty_notes": "one short sentence on what makes this sentence easy or hard for a learner"
}

Keep every field concise. The "words" array must cover every word in the original sentence, in order, including punctuation-adjacent tokens attached correctly.
Respond with raw JSON only — your entire output must be parseable by json.loads()."""


def analyze_with_claude(sentence: str, api_key: str, model: str = "claude-sonnet-4-6"):
    from anthropic import Anthropic

    client = Anthropic(api_key=api_key)
    resp = client.messages.create(
        model=model,
        max_tokens=1500,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": sentence}],
    )
    text = "".join(block.text for block in resp.content if block.type == "text").strip()
    text = re.sub(r"^```json\s*|\s*```$", "", text.strip())
    text = re.sub(r"^```\s*|\s*```$", "", text.strip())
    return json.loads(text)


def analyze_offline(sentence: str):
    """Fallback: word-by-word dictionary lookup, no grammar synthesis.
    Clearly marked as limited so learners aren't misled."""
    tokens = re.findall(r"[A-Za-zÀ-ÿäöüÄÖÜß]+|[^\sA-Za-zÀ-ÿäöüÄÖÜß]", sentence)
    words = []
    for tok in tokens:
        if not re.match(r"[A-Za-zÀ-ÿäöüÄÖÜß]+", tok):
            continue
        key = tok.strip(".,!?;:")
        entry = MINI_DICTIONARY.get(key) or MINI_DICTIONARY.get(key.lower())
        words.append({
            "word": tok,
            "base_form": key.lower() if not entry else key,
            "meaning": entry["meaning"] if entry else "(not in local dictionary — try the AI analyzer)",
            "grammar": "—",
        })
    return {
        "words": words,
        "cases_explained": "Grammar analysis requires the AI analyzer (add your Anthropic API key in the sidebar).",
        "word_order_notes": "—",
        "separable_verbs": "—",
        "idioms": "—",
        "literal_translation": "—",
        "natural_translation": "—",
        "difficulty_notes": "Offline mode only shows words found in the small built-in dictionary.",
        "offline_mode": True,
    }
