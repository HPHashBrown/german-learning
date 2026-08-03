"""Sound Design + Confetti.

Sounds are generated procedurally with the browser's built-in Web Audio API
(oscillator tones) rather than shipped as audio files — this means there are
no external assets that can go missing/break, and it works completely
offline. Confetti uses canvas-confetti from a CDN with a no-op fallback if
the script can't load (e.g. offline), so it never breaks the app either way.
"""

import streamlit as st

# Each pack maps the same set of event keys to a distinct tone character.
# Each tone is (frequency Hz, duration ms, wave type).
SOUND_PACKS = {
    "classic": {
        "correct": [(880, 90, "sine"), (1175, 120, "sine")],
        "incorrect": [(220, 160, "sawtooth")],
        "level_up": [(523, 90, "sine"), (659, 90, "sine"), (784, 90, "sine"), (1047, 180, "sine")],
        "achievement": [(659, 100, "triangle"), (988, 160, "triangle")],
        "unlock": [(440, 80, "square"), (880, 140, "square")],
        "daily_reward": [(587, 100, "sine"), (784, 100, "sine"), (988, 160, "sine")],
        "coin": [(1046, 60, "sine"), (1568, 90, "sine")],
    },
    "chiptune": {
        "correct": [(988, 70, "square"), (1319, 70, "square"), (1568, 110, "square")],
        "incorrect": [(196, 90, "square"), (147, 140, "square")],
        "level_up": [(659, 70, "square"), (784, 70, "square"), (988, 70, "square"),
                     (1319, 70, "square"), (1568, 160, "square")],
        "achievement": [(784, 80, "square"), (988, 80, "square"), (1319, 140, "square")],
        "unlock": [(523, 70, "square"), (659, 70, "square"), (880, 130, "square")],
        "daily_reward": [(659, 80, "square"), (880, 80, "square"), (1108, 80, "square"), (1319, 140, "square")],
        "coin": [(1568, 45, "square"), (2093, 70, "square")],
    },
    "soft_chimes": {
        "correct": [(1046, 140, "sine"), (1318, 200, "sine")],
        "incorrect": [(392, 220, "sine")],
        "level_up": [(784, 140, "sine"), (988, 140, "sine"), (1318, 140, "sine"), (1568, 260, "sine")],
        "achievement": [(988, 160, "sine"), (1318, 240, "sine")],
        "unlock": [(659, 130, "sine"), (988, 220, "sine")],
        "daily_reward": [(880, 150, "sine"), (1108, 150, "sine"), (1318, 240, "sine")],
        "coin": [(1318, 90, "sine"), (1760, 130, "sine")],
    },
}

DEFAULT_PACK = "classic"


def play_sound(sound_key: str, enabled: bool = True, pack: str = DEFAULT_PACK):
    """Injects a tiny inline script that plays the given tone sequence once.
    Safe no-op if the browser blocks audio autoplay (common until the user
    has interacted with the page at least once — normal browser behavior)."""
    if not enabled:
        return
    presets = SOUND_PACKS.get(pack, SOUND_PACKS[DEFAULT_PACK])
    if sound_key not in presets:
        return
    notes = presets[sound_key]
    notes_js = ",".join(f"[{freq},{dur},'{wave}']" for freq, dur, wave in notes)
    st.components.v1.html(f"""
    <script>
    (function() {{
        try {{
            const ctx = new (window.AudioContext || window.webkitAudioContext)();
            const notes = [{notes_js}];
            let t = ctx.currentTime;
            notes.forEach(([freq, durMs, type]) => {{
                const osc = ctx.createOscillator();
                const gain = ctx.createGain();
                osc.type = type;
                osc.frequency.value = freq;
                gain.gain.setValueAtTime(0.15, t);
                gain.gain.exponentialRampToValueAtTime(0.001, t + durMs/1000);
                osc.connect(gain).connect(ctx.destination);
                osc.start(t);
                osc.stop(t + durMs/1000);
                t += durMs/1000;
            }});
        }} catch (e) {{ /* audio not available — silently skip */ }}
    }})();
    </script>
    """, height=0)


def speak_german(text: str, rate: float = 0.9, key_suffix: str = ""):
    """Renders a 'Play Audio' button that uses the browser's built-in
    SpeechSynthesis API (Web Speech API) to read German text aloud. No audio
    files, works fully offline once the page has loaded, and gracefully does
    nothing if the browser has no German voice available (rare, but some
    browsers/OSes have limited voice packs — shown as a caption fallback)."""
    safe_text = text.replace("\\", "\\\\").replace("`", "\\`").replace("</script>", "<\\/script>")
    st.components.v1.html(f"""
    <div style="display:flex; align-items:center; gap:8px;">
        <button id="speak_btn_{key_suffix}" style="
            padding: 8px 16px; border-radius: 10px; border: none;
            background: linear-gradient(90deg,#6366f1,#f59e0b); color: white;
            font-weight: 700; cursor: pointer; font-size: 14px;">
            🔊 Play Audio
        </button>
        <span id="speak_status_{key_suffix}" style="font-size: 12px; opacity: 0.7;"></span>
    </div>
    <script>
    (function() {{
        const btn = document.getElementById('speak_btn_{key_suffix}');
        const status = document.getElementById('speak_status_{key_suffix}');
        btn.addEventListener('click', function() {{
            try {{
                if (!('speechSynthesis' in window)) {{
                    status.textContent = 'Speech not supported in this browser.';
                    return;
                }}
                window.speechSynthesis.cancel();
                const utter = new SpeechSynthesisUtterance(`{safe_text}`);
                utter.lang = 'de-DE';
                utter.rate = {rate};
                const voices = window.speechSynthesis.getVoices();
                const deVoice = voices.find(v => v.lang && v.lang.startsWith('de'));
                if (deVoice) {{ utter.voice = deVoice; }}
                else {{ status.textContent = '(no German voice found — using default)'; }}
                window.speechSynthesis.speak(utter);
            }} catch (e) {{
                status.textContent = 'Audio playback unavailable.';
            }}
        }});
    }})();
    </script>
    """, height=50)


def confetti_burst(pieces: int = 120):
    st.components.v1.html(f"""
    <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.9.2/dist/confetti.browser.min.js"
            onerror="console.log('confetti script failed to load, skipping')"></script>
    <script>
    (function() {{
        function fire() {{
            if (typeof confetti === 'function') {{
                confetti({{particleCount: {pieces}, spread: 90, origin: {{y: 0.4}}}});
            }}
        }}
        if (typeof confetti === 'function') {{ fire(); }}
        else {{ setTimeout(fire, 400); }}
    }})();
    </script>
    """, height=0)
