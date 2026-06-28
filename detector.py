import json
from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL


client = Groq(api_key=GROQ_API_KEY)


def analyze_with_groq(text: str) -> dict:
    prompt = f"""
You are part of Provenance Guard, an AI-content attribution system.

Analyze the text and estimate whether it appears AI-generated or human-written.

Return ONLY valid JSON with this format:
{{
  "score": 0.0,
  "attribution": "likely_human",
  "reason": "short explanation"
}}

Rules:
- score must be between 0 and 1
- score closer to 1 means more AI-like
- score closer to 0 means more human-like
- attribution must be one of: likely_ai, likely_human, uncertain

Text:
{text}
"""

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
    )

    content = response.choices[0].message.content

    try:
        result = json.loads(content)
    except json.JSONDecodeError:
        result = {
            "score": 0.5,
            "attribution": "uncertain",
            "reason": "Model response could not be parsed, so the system marked the result as uncertain."
        }

    return result