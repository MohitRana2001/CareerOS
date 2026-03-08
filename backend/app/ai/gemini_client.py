import json

import httpx

from app.ai.contracts import TailorOutput, validate_tailor_output
from app.config import settings


class GeminiClientError(Exception):
    pass


def generate_tailored_content(prompt: str, model_name: str | None) -> TailorOutput:
    if not settings.gemini_api_key:
        raise GeminiClientError("GEMINI_API_KEY is not configured")

    model = model_name or settings.gemini_default_model
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

    response = httpx.post(
        url,
        params={"key": settings.gemini_api_key},
        json={
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"responseMimeType": "application/json"},
        },
        timeout=45.0,
    )

    if response.status_code >= 400:
        raise GeminiClientError(f"Gemini request failed with status {response.status_code}")

    payload = response.json()
    try:
        text = payload["candidates"][0]["content"]["parts"][0]["text"]
        parsed = json.loads(text)
    except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
        raise GeminiClientError("Unexpected Gemini response shape") from exc

    return validate_tailor_output(parsed)
