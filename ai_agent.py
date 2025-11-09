# ai_agent.py
from openai import OpenAI
import json, os

def generate_art_statement(data: dict, api_key: str) -> dict:
    # Ensure env var is set so the SDK can read it implicitly
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key

    client = OpenAI()  # no kwargs → read from env

    prompt = f"""
You are an AI art critic and poet.
Given the user's daily biometric and emotional data: {data},
create:
1. A poetic title (3–6 words)
2. A short artist's statement (<100 words)
3. Three color tone recommendations.

Respond in JSON as:
{{"title": "...", "statement": "...", "colors": ["...","...","..."]}}
"""
    resp = client.responses.create(model="gpt-4o-mini", input=prompt)

    # Robustly extract text across SDK versions
    text = getattr(resp, "output_text", None)
    if not text:
        try:
            # fallback path if output_text isn't available
            text = resp.output[0].content[0].text
        except Exception:
            text = "{}"

    try:
        return json.loads(text.strip())
    except Exception:
        return {
            "title": "Untitled Motion",
            "statement": text.strip(),
            "colors": ["#CBD5E0", "#A0AEC0", "#718096"]
        }
