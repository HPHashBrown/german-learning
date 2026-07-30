"""Sound Design + Confetti.

Sounds are generated procedurally with the browser's built-in Web Audio API
(oscillator tones) rather than shipped as audio files — this means there are
no external assets that can go missing/break, and it works completely
offline. Confetti uses canvas-confetti from a CDN with a no-op fallback if
the script can't load (e.g. offline), so it never breaks the app either way.
"""

import streamlit as st

# Each tone is (frequency Hz, duration ms, wave type)
TONE_PRESETS = {
    "correct": [(880, 90, "sine"), (1175, 120, "sine")],
    "incorrect": [(220, 160, "sawtooth")],
    "level_up": [(523, 90, "sine"), (659, 90, "sine"), (784, 90, "sine"), (1047, 180, "sine")],
    "achievement": [(659, 100, "triangle"), (988, 160, "triangle")],
    "unlock": [(440, 80, "square"), (880, 140, "square")],
    "daily_reward": [(587, 100, "sine"), (784, 100, "sine"), (988, 160, "sine")],
    "coin": [(1046, 60, "sine"), (1568, 90, "sine")],
}


def play_sound(sound_key: str, enabled: bool = True):
    """Injects a tiny inline script that plays the given tone sequence once.
    Safe no-op if the browser blocks audio autoplay (common until the user
    has interacted with the page at least once — normal browser behavior)."""
    if not enabled or sound_key not in TONE_PRESETS:
        return
    notes = TONE_PRESETS[sound_key]
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
