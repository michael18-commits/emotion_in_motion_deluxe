from openai import OpenAI
import json

def generate_art_statement(data, api_key):
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
    client = OpenAI(api_key=api_key)
    resp = client.responses.create(model="gpt-4o-mini", input=prompt)
    text = getattr(resp, "output_text", "{}").strip()
    try:
        return json.loads(text)
    except Exception:
        return {"title": "Untitled Motion", "statement": text, "colors": ["#CBD5E0", "#A0AEC0", "#718096"]}
