# ai_agent.py  (robust, env-based, with fallbacks)
from openai import OpenAI
import os, json

def _safe_json_loads(text: str):
    try:
        return json.loads(text.strip())
    except Exception:
        return None

def generate_art_statement(data: dict, api_key: str) -> dict:
    # 1) 统一走环境变量，避免 SDK 在不同环境对参数挑剔
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key

    # 2) 创建客户端（不传参，读 env）
    client = OpenAI()

    # 3) 主路径：Responses API
    prompt = f"""
You are an AI art critic and poet.
Given the user's daily biometric and emotional data: {data},
create:
1) A poetic title (3–6 words)
2) A short artist's statement (<100 words)
3) Three color tone recommendations.

Reply in pure JSON (no code fences):
{{"title":"...","statement":"...","colors":["...","...","..."]}}
"""
    text = None
    try:
        resp = client.responses.create(model="gpt-4o-mini", input=prompt)
        # 新版 SDK 提供 output_text；部分环境没有时 fallback
        text = getattr(resp, "output_text", None)
        if not text:
            text = resp.output[0].content[0].text  # 兜底
        js = _safe_json_loads(text)
        if js:
            return js
    except Exception:
        pass

    # 4) 备用路径：Chat Completions（避免 responses 在少数环境异常）
    try:
        chat = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role":"system","content":"Return ONLY compact JSON."},
                      {"role":"user","content": prompt}]
        )
        text = chat.choices[0].message.content
        js = _safe_json_loads(text)
        if js:
            return js
    except Exception:
        pass

    # 5) 最终兜底（不让页面报错）
    return {
        "title": "Untitled Motion",
        "statement": (text or "An abstract visualization of motion and mood.").strip(),
        "colors": ["#CBD5E0", "#A0AEC0", "#718096"]
    }
