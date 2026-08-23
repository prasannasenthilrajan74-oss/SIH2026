import urllib.request
import json
import logging
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

def get_ollama_status() -> dict:
    url = f"{settings.OLLAMA_BASE_URL.rstrip('/')}/api/tags"
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=2) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode('utf-8'))
                models = [m.get('name') for m in data.get('models', []) if m.get('name')]
                return {
                    "running": True,
                    "url": settings.OLLAMA_BASE_URL,
                    "models": models
                }
    except Exception:
        pass
    return {"running": False, "url": settings.OLLAMA_BASE_URL, "models": []}

def query_ollama(prompt: str, system_prompt: str = "", model_override: str = None) -> dict:
    status = get_ollama_status()
    if not status["running"]:
        return {"success": False, "reason": "Ollama service is not running locally.", "status": status}

    available_models = status["models"]
    if not available_models:
        return {
            "success": False,
            "reason": f"Ollama is running at {settings.OLLAMA_BASE_URL}, but no local models have been pulled yet.",
            "status": status,
            "instruction": f"Run 'ollama pull {settings.OLLAMA_MODEL}' or 'ollama pull mistral' in your terminal."
        }

    # Select model
    model = model_override or settings.OLLAMA_MODEL
    if model not in available_models and available_models:
        # Match base name if version tag differs
        base_target = model.split(':')[0]
        matched = [m for m in available_models if m.startswith(base_target)]
        if matched:
            model = matched[0]
        else:
            model = available_models[0]

    url = f"{settings.OLLAMA_BASE_URL.rstrip('/')}/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "system": system_prompt or "You are Sentinel AI, an expert governance assistant for the MPLADS platform. Answer concisely and accurately based on the provided ground-truth context.",
        "stream": False
    }

    try:
        data_bytes = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data_bytes, headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=60) as resp:
            if resp.status == 200:
                res_data = json.loads(resp.read().decode('utf-8'))
                response_text = res_data.get("response", "").strip()
                return {
                    "success": True,
                    "model": model,
                    "response": response_text,
                    "status": status
                }
    except Exception as e:
        logger.error(f"Error querying Ollama model {model}: {e}")
        return {"success": False, "reason": str(e), "model": model, "status": status}

    return {"success": False, "reason": "Unknown generation error.", "status": status}
