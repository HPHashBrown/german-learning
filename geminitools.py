"""All Gemini-API-powered features: AI Conversation Mode, AI Writing Tutor,
Pronunciation Trainer, and the Dictionary lookup (per the brief: "change the
API key used for the dictionary to use gemini's").

Uses the current `google-genai` SDK (the older `google-generativeai` package
is deprecated as of this writing).

The user supplies their own Gemini API key in the sidebar — it's kept only
in `st.session_state` for the current browser session, never written to disk.
"""

import json
import re

from google import genai
from google.genai import types

MODEL = "gemini-2.5-flash"

SCENARIOS = {
    "Restaurant": "You are a friendly German waiter/waitress at a restaurant in Berlin.",
    "Airport": "You are a German airport check-in agent helping a traveler.",
    "Hotel": "You are a hotel receptionist in Munich checking in a guest.",
    "Job Interview": "You are a hiring manager conducting a German-language job interview.",
    "Shopping": "You are a shop assistant in a German clothing store.",
    "Doctor": "You are a German doctor (Hausarzt) talking with a patient about mild symptoms.",
    "Friends": "You are the user's German friend, chatting casually about weekend plans.",
    "Ordering Coffee": "You are a barista at a German café taking a coffee order.",
}

CONVERSATION_SYSTEM_TEMPLATE = """You are a German conversation partner for a language learner, roleplaying
this scenario: {scenario_desc}

Rules:
- Reply ONLY in German, at a level appropriate for a learner (mostly A2-B1 vocabulary
  unless the learner writes at a higher level).
- Keep replies short (2-4 sentences) and natural for the roleplay.
- If the learner's German message has a grammar or vocabulary mistake, gently correct
  it: first give your in-character reply, then on a new line write "📝 Correction: ..."
  explaining the mistake and the fix in English, and optionally "💡 Better: ..." with a
  more natural way to phrase it.
- If there's no mistake, skip the correction line entirely.
- Stay in character and keep the conversation moving naturally."""


def get_client(api_key: str) -> genai.Client:
    return genai.Client(api_key=api_key)


def conversation_reply(api_key: str, scenario: str, history: list, user_message: str) -> str:
    """history: list of {'role': 'user'|'model', 'content': str}."""
    client = get_client(api_key)
    scenario_desc = SCENARIOS.get(scenario, scenario)
    system = CONVERSATION_SYSTEM_TEMPLATE.format(scenario_desc=scenario_desc)

    contents = []
    for turn in history:
        role = "user" if turn["role"] == "user" else "model"
        contents.append(types.Content(role=role, parts=[types.Part(text=turn["content"])]))
    contents.append(types.Content(role="user", parts=[types.Part(text=user_message)]))

    resp = client.models.generate_content(
        model=MODEL,
        contents=contents,
        config=types.GenerateContentConfig(system_instruction=system, max_output_tokens=400),
    )
    return resp.text.strip()


WRITING_TUTOR_SYSTEM = """You are a German writing tutor. The learner will submit a paragraph they
wrote in German. Respond with ONLY valid JSON (no markdown fences), shaped exactly like:

{
  "corrected_text": "the full corrected version of their paragraph",
  "grammar_corrections": [{"original": "...", "corrected": "...", "explanation": "..."}],
  "vocabulary_improvements": [{"original": "...", "improved": "...", "why": "..."}],
  "natural_phrasing_notes": "1-3 sentences on phrasing that's grammatically fine but sounds unnatural",
  "alternative_expressions": ["alternative way to say something in the text", "..."],
  "overall_feedback": "2-3 encouraging but honest sentences on strengths and what to work on next"
}

Keep lists to at most 5 items each. Respond with raw JSON only."""


def writing_tutor_feedback(api_key: str, paragraph: str) -> dict:
    client = get_client(api_key)
    resp = client.models.generate_content(
        model=MODEL,
        contents=paragraph,
        config=types.GenerateContentConfig(system_instruction=WRITING_TUTOR_SYSTEM, max_output_tokens=1500),
    )
    text = resp.text.strip()
    text = re.sub(r"^```json\s*|\s*```$", "", text)
    text = re.sub(r"^```\s*|\s*```$", "", text)
    return json.loads(text)


PRONUNCIATION_SYSTEM = """You are a German pronunciation coach. You will receive an audio recording of a
learner saying a target German sentence, plus the target sentence text. Assess the
recording and respond with ONLY valid JSON, shaped exactly like:

{
  "overall_score": 85,
  "word_scores": [{"word": "...", "correct": true, "note": "..."}],
  "fluency_note": "1-2 sentences on pacing/fluency",
  "problem_sounds": ["ü", "ch"],
  "encouragement": "1 short encouraging sentence"
}

overall_score is an integer 0-100. Base it on how close the pronunciation is to
standard German. Be honest but encouraging. Respond with raw JSON only."""


def assess_pronunciation(api_key: str, target_sentence: str, audio_bytes: bytes, mime_type: str) -> dict:
    client = get_client(api_key)
    resp = client.models.generate_content(
        model=MODEL,
        contents=[
            f"Target sentence: {target_sentence}",
            types.Part.from_bytes(data=audio_bytes, mime_type=mime_type),
        ],
        config=types.GenerateContentConfig(system_instruction=PRONUNCIATION_SYSTEM, max_output_tokens=800),
    )
    text = resp.text.strip()
    text = re.sub(r"^```json\s*|\s*```$", "", text)
    text = re.sub(r"^```\s*|\s*```$", "", text)
    return json.loads(text)


DICTIONARY_SYSTEM = """You are a German dictionary. Given a single German word or short phrase, respond
with ONLY valid JSON, shaped exactly like:

{
  "word": "the word, in its dictionary/base form",
  "meaning": "concise English meaning",
  "gender": "m/f/n/— (— if not a noun)",
  "plural": "plural form, or — if not applicable",
  "cefr": "estimated CEFR level, e.g. A1",
  "example": "one example German sentence using the word",
  "example_translation": "English translation of the example",
  "synonyms": "comma-separated synonyms, or —",
  "related_words": "comma-separated related words/compounds, or —"
}

If the input isn't recognizable as German, do your best guess and note that in "meaning".
Respond with raw JSON only."""


def dictionary_lookup(api_key: str, word: str) -> dict:
    client = get_client(api_key)
    resp = client.models.generate_content(
        model=MODEL,
        contents=word,
        config=types.GenerateContentConfig(system_instruction=DICTIONARY_SYSTEM, max_output_tokens=400),
    )
    text = resp.text.strip()
    text = re.sub(r"^```json\s*|\s*```$", "", text)
    text = re.sub(r"^```\s*|\s*```$", "", text)
    return json.loads(text)
