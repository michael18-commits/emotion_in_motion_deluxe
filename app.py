import streamlit as st
import pandas as pd
from datetime import datetime
from art_engine import generate_fluid_art, fig_to_bytes
from ai_agent import generate_art_statement

st.set_page_config(page_title="Emotion in Motion", page_icon="🎨", layout="wide")
st.title("🎨 Emotion in Motion — The Algorithmic Soul")
st.caption("A generative art system that visualizes emotion through data and AI interpretation.")

if "api_key" not in st.session_state:
    st.session_state.api_key = st.secrets.get("OPENAI_API_KEY", None)

if not st.session_state.api_key:
    with st.expander("🔑 Enter your OpenAI API Key", expanded=True):
        st.markdown("You can get one from [OpenAI API](https://platform.openai.com/account/api-keys).")
        key_input = st.text_input("Paste your API Key here:", type="password")
        if key_input:
            st.session_state.api_key = key_input.strip()
            st.experimental_rerun()
    st.stop()

api_key = st.session_state.api_key

with st.sidebar:
    st.header("Data Input")
    mode = st.radio("Select Data Mode:", ["Manual Entry", "Use Sample"])
    mood = st.selectbox("Mood", ["calm", "joyful", "anxious", "tired", "focused"])
    seed = st.number_input("Seed", 0, 999999, 42)
    steps = st.slider("Steps", 0, 30000, 8000, step=500)
    hr = st.slider("Average Heart Rate (bpm)", 40, 160, 80)
    sleep = st.slider("Sleep Hours", 0.0, 12.0, 7.0, step=0.1)
    fatigue = st.slider("Fatigue (0–1)", 0.0, 1.0, 0.4, step=0.05)
    st.markdown("---")
    st.caption("🎬 Click below to generate:")
    generate = st.button("Generate Artwork")

if mode == "Use Sample":
    steps, hr, sleep, fatigue, mood = 9800, 88, 6.5, 0.5, "joyful"

if generate:
    st.subheader("Generated Artwork")
    fig = generate_fluid_art(seed, steps, hr, sleep, fatigue, mood)
    st.pyplot(fig, use_container_width=True)

    image_bytes = fig_to_bytes(fig)
    st.download_button("💾 Download Artwork", data=image_bytes,
                       file_name=f"emotion_in_motion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                       mime="image/png")

    st.subheader("AI Interpretation")
    data = {"steps": steps, "heart_rate": hr, "sleep": sleep, "fatigue": fatigue, "mood": mood}
    with st.spinner("AI analyzing emotional patterns..."):
        result = generate_art_statement(data, api_key)

    st.markdown(f"### 🖼️ *{result.get('title', 'Untitled Motion')}*")
    st.write(result.get("statement", ""))
    st.caption(f"🎨 Suggested Colors: {', '.join(result.get('colors', []))}")
else:
    st.info("Adjust parameters in the sidebar and click **Generate Artwork**.")
