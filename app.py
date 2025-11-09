# app.py (deluxe controls)
import os
import streamlit as st
from datetime import datetime
from art_engine import generate_art, fig_to_bytes
from ai_agent import generate_art_statement

st.set_page_config(page_title="Emotion in Motion", page_icon="🎨", layout="wide")
st.title("🎨 Emotion in Motion — The Algorithmic Soul")
st.caption("Generative art that reacts to your body & mood, with AI titles and statements.")

# --- API key handling (secrets → session) ---
if "api_key" not in st.session_state:
    st.session_state.api_key = st.secrets.get("OPENAI_API_KEY", None)
if st.session_state.api_key:
    os.environ["OPENAI_API_KEY"] = st.session_state.api_key

if not st.session_state.api_key:
    with st.expander("🔑 Enter your OpenAI API Key", expanded=True):
        st.markdown("Get one at **OpenAI → API keys**. The key is used in-session only.")
        key_input = st.text_input("API Key", type="password")
        if key_input:
            st.session_state.api_key = key_input.strip()
            os.environ["OPENAI_API_KEY"] = st.session_state.api_key
            st.rerun()
    st.stop()

# ================= Sidebar (much richer) =================
with st.sidebar:
    st.header("Data / Mood")
    mode = st.radio("Data Mode", ["Manual Entry", "Use Sample"], index=0)
    mood = st.selectbox("Mood", ["calm", "joyful", "anxious", "tired", "focused", "blue"], index=0)
    seed = st.number_input("Seed", 0, 999999, 42)

    steps = st.slider("Steps", 0, 40000, 9000, step=500)
    hr = st.slider("Avg Heart Rate (bpm)", 40, 180, 82)
    sleep = st.slider("Sleep Hours", 0.0, 12.0, 6.8, step=0.1)
    fatigue = st.slider("Fatigue (0–1)", 0.0, 1.0, 0.45, step=0.05)

    st.markdown("---")
    st.header("Style & Pattern")
    pattern = st.selectbox("Pattern Mode", ["Flow Field", "Ribbon Trails", "Bubble Bloom", "Hybrid"])
    bg_gradient = st.checkbox("Background Gradient", True)
    vignette = st.slider("Vignette Strength", 0.0, 1.0, 0.25, 0.05)
    grain = st.slider("Film Grain", 0.0, 1.0, 0.15, 0.05)

    st.markdown("### Color System")
    color_mode = st.selectbox("Palette Mode", ["Mood", "Mood + Complement", "Triadic", "Analogous", "Custom"])
    colorfulness = st.slider("Colorfulness", 0.0, 1.0, 0.7, 0.05)
    saturation = st.slider("Saturation", 0.0, 1.0, 0.85, 0.05)
    brightness = st.slider("Brightness", 0.0, 1.0, 0.9, 0.05)
    custom_hex = st.text_input("Custom base color (HEX, optional)", "")

    st.markdown("### Geometry & Flow")
    density = st.slider("Stroke Density", 50, 1200, 450, 10)
    path_len = st.slider("Path Length", 80, 1200, 420, 10)
    stroke_min = st.slider("Stroke Min", 0.2, 3.0, 0.5, 0.1)
    stroke_max = st.slider("Stroke Max", 0.5, 6.0, 1.6, 0.1)
    octaves = st.slider("Noise Octaves", 1, 8, 3)
    flow_strength = st.slider("Flow Strength", 0.2, 2.5, 1.2, 0.05)

    st.markdown("---")
    generate = st.button("🎬 Generate Artwork")

# Sample data override
if mode == "Use Sample":
    steps, hr, sleep, fatigue, mood = 11800, 90, 6.2, 0.52, "joyful"

# ================= Main =================
if generate:
    st.subheader("Generated Artwork")
    fig = generate_art(
        seed=seed,
        steps=steps,
        heart_rate=hr,
        sleep=sleep,
        fatigue=fatigue,
        mood=mood,
        pattern=pattern,
        bg_gradient=bg_gradient,
        vignette=vignette,
        grain=grain,
        color_mode=color_mode,
        colorfulness=colorfulness,
        saturation=saturation,
        brightness=brightness,
        custom_hex=custom_hex or None,
        density=density,
        path_length=path_len,
        stroke_min=stroke_min,
        stroke_max=stroke_max,
        noise_octaves=octaves,
        flow_strength=flow_strength,
        size=(1200, 800),
    )
    st.pyplot(fig, use_container_width=True)

    png = fig_to_bytes(fig)
    st.download_button("💾 Download PNG", data=png,
                       file_name=f"emotion_in_motion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                       mime="image/png")

    st.subheader("AI Interpretation")
    payload = {"steps": steps, "heart_rate": hr, "sleep": sleep,
               "fatigue": fatigue, "mood": mood}
    with st.spinner("AI analyzing emotional patterns..."):
        result = generate_art_statement(payload, st.session_state.api_key)
    st.markdown(f"### 🖼️ *{result.get('title','Untitled Motion')}*")
    st.write(result.get("statement", ""))
    st.caption(f"🎨 Suggested Colors: {', '.join(result.get('colors', []))}")
else:
    st.info("Adjust parameters on the left, then click **Generate Artwork**.")
