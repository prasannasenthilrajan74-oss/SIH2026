import urllib.request
import json
import logging
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

def query_gemini_api(prompt: str, system_prompt: str = "", api_key: str = None) -> dict:
    """
    Queries Google Gemini API as PRIMARY AI Model.
    Attempts official google.genai Client first, with SDK and REST API fallbacks.
    """
    key = api_key or settings.GEMINI_API_KEY
    if not key or key == "mock_key":
        return {"success": False, "reason": "No valid GEMINI_API_KEY configured in environment."}

    # 1. Primary Attempt via new google.genai Client SDK
    try:
        from google import genai
        client = genai.Client(api_key=key)
        genai_models = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]
        for m_name in genai_models:
            try:
                contents_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
                res = client.models.generate_content(
                    model=m_name,
                    contents=contents_prompt,
                )
                if res and hasattr(res, 'text') and res.text:
                    logger.info(f"Successfully generated response using Primary google.genai model: {m_name}")
                    return {
                        "success": True,
                        "response": res.text.strip(),
                        "model": f"Gemini Primary ({m_name})"
                    }
            except Exception as e:
                logger.debug(f"google.genai model {m_name} failed: {e}")
                continue
    except ImportError:
        pass
    except Exception as e:
        logger.warning(f"google.genai client initialization error: {e}")

    # 2. Legacy google.generativeai SDK attempt
    try:
        import google.generativeai as legacy_genai
        legacy_genai.configure(api_key=key)
        sdk_models = ["gemini-1.5-flash", "gemini-2.0-flash-exp", "gemini-1.5-pro", "gemini-pro"]
        for m_name in sdk_models:
            try:
                model = legacy_genai.GenerativeModel(
                    model_name=m_name,
                    system_instruction=system_prompt if system_prompt else None
                )
                response = model.generate_content(prompt)
                if response and hasattr(response, 'text') and response.text:
                    logger.info(f"Successfully generated response using Primary Gemini SDK model: {m_name}")
                    return {
                        "success": True,
                        "response": response.text.strip(),
                        "model": f"Gemini Primary ({m_name})"
                    }
            except Exception as e:
                logger.debug(f"Gemini SDK model {m_name} attempt failed: {e}")
                continue
    except ImportError:
        pass
    except Exception as e:
        logger.warning(f"Gemini legacy SDK initialization error: {e}")

    # 3. Fallback REST API endpoints
    models = ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-pro", "gemini-pro"]
    for model_name in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        if system_prompt:
            payload["system_instruction"] = {"parts": [{"text": system_prompt}]}

        try:
            req_data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(
                url,
                data=req_data,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                if resp.status == 200:
                    res_json = json.loads(resp.read().decode('utf-8'))
                    candidates = res_json.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            text = parts[0].get("text", "").strip()
                            if text:
                                return {
                                    "success": True,
                                    "response": text,
                                    "model": f"Gemini Primary ({model_name})"
                                }
        except Exception as e:
            logger.warning(f"Gemini REST API attempt with {model_name} failed: {e}")
            continue

    return {"success": False, "reason": "Gemini API request failed for available models."}
