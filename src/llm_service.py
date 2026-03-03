"""
LLM Service — Google Gemini integration via direct REST API.

Uses Gemini 2.0 Flash (free tier: 15 RPM, 1M tokens/day).
No dependency on deprecated google-generativeai SDK — uses urllib directly.
Falls back gracefully to template responses if API key is missing or quota exceeded.
"""

import os
import json
import threading
import urllib.request
import urllib.error
from typing import Optional, Callable
from dataclasses import dataclass

# Config file for storing API key locally
CONFIG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
CONFIG_FILE = os.path.join(CONFIG_DIR, '.env_config.json')

# Gemini REST API endpoint
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"

# ---------------------------------------------------------------------------
# System prompt — the soul of MindfulAI
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """Sen "MindfulAI" adlı empatik bir ruh sağlığı asistanısın. Kullanıcılar günlük yazıyor ve sen onlara sıcak, destekleyici, yargılamayan cevaplar veriyorsun.

KURALLAR:
1. ASLA klinik teşhis koyma. "Depresyonda olabilirsin" gibi şeyler SÖYLEME.
2. ASLA "intihar eğilimi", "bipolar", "kişilik bozukluğu" gibi klinik terimler KULLANMA.
3. Her zaman önce kullanıcının duygularını doğrula ve empati göster.
4. Pratik, uygulanabilir başa çıkma stratejileri öner.
5. Ciddi durumlarda (kullanıcı kendine zarar vermekten bahsediyorsa) MUTLAKA kriz hattı numaralarını ver: Türkiye 182, ABD 988, UK 116123
6. Samimi, sıcak ve arkadaşça ol — ama profesyonel sınırları koru.
7. Yanıtını kullanıcının diliyle yaz (Türkçe yazıyorsa Türkçe, İngilizce yazıyorsa İngilizce).
8. Kısa ve öz ol — 3-5 paragraf yeterli.
9. Uygun yerlerde emoji kullan ama abartma.

MOOD BİLGİSİ:
ML modelimiz kullanıcının yazısını analiz etti ve bir duygu durumu tespit etti. Bu bilgiyi kullan ama kullanıcıya HAM ETİKETİ GÖSTERME.
Tespit edilen kategori: {category}
Güven skoru: {confidence:.0%}
Şiddet seviyesi: {severity}/5

Kullanıcının orijinal metni (kendi dilinde): {original_text}
İngilizce çevirisi: {translated_text}

Yanıtını şu formatta ver:
1. Önce empati ve duygusal doğrulama (1-2 cümle)
2. Destekleyici mesaj ve başa çıkma önerisi (2-3 cümle)
3. Gerekirse profesyonel yardım önerisi (severity >= 4 ise)
4. Günlük yazma devam isteği (1 cümle, soru şeklinde)
"""

SYSTEM_PROMPT_EN = """You are "MindfulAI", an empathetic mental health wellness companion. Users write journal entries and you respond with warm, supportive, non-judgmental responses.

RULES:
1. NEVER give clinical diagnoses. NEVER say things like "you might be depressed".
2. NEVER use clinical terms like "suicidal ideation", "bipolar", "personality disorder" with the user.
3. Always validate the user's feelings first and show empathy.
4. Suggest practical, actionable coping strategies.
5. For serious situations (if user mentions self-harm), ALWAYS provide crisis hotline numbers: Turkey 182, USA 988, UK 116123
6. Be warm, friendly, and caring — but maintain professional boundaries.
7. Respond in the SAME LANGUAGE the user wrote in.
8. Keep it concise — 3-5 paragraphs are enough.
9. Use emoji where appropriate but don't overdo it.

MOOD INFORMATION:
Our ML model analyzed the user's text and detected an emotional state. Use this info but NEVER show the raw label to the user.
Detected category: {category}
Confidence score: {confidence:.0%}
Severity level: {severity}/5

User's original text: {original_text}
English translation: {translated_text}

Structure your response:
1. Empathy and emotional validation first (1-2 sentences)
2. Supportive message with coping suggestion (2-3 sentences)
3. Professional help suggestion if needed (severity >= 4)
4. A follow-up journaling prompt (1 sentence, as a question)
"""


@dataclass
class LLMResponse:
    """Response from the LLM service."""
    text: str
    success: bool
    source: str  # "gemini", "template", "error"
    error: Optional[str] = None


def _gemini_request(api_key: str, model: str, prompt: str,
                    temperature: float = 0.8, max_tokens: int = 500,
                    timeout: int = 20) -> dict:
    """
    Make a direct REST API call to Gemini. No SDK needed.
    Returns the parsed JSON response dict.
    """
    url = GEMINI_API_URL.format(model=model, key=api_key)
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": temperature,
            "topP": 0.9,
            "maxOutputTokens": max_tokens,
        },
        "safetySettings": [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]
    }
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        url, data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    resp = urllib.request.urlopen(req, timeout=timeout)
    return json.loads(resp.read().decode('utf-8'))


class LLMService:
    """
    Google Gemini integration via REST API with graceful fallback.

    Usage:
        service = LLMService()
        service.set_api_key("your-key")
        service.generate_async(category, conf, sev, text, translated, callback)
    """

    def __init__(self):
        self._api_key: Optional[str] = None
        self._model_name: str = "gemini-2.0-flash"
        self._available: bool = False
        self._load_config()

    # ---- Config persistence ----

    def _load_config(self):
        """Load API key from local config file."""
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    key = config.get('gemini_api_key', '')
                    if key:
                        self.set_api_key(key)
        except (json.JSONDecodeError, IOError):
            pass

    def _save_config(self):
        """Save API key to local config file."""
        try:
            config = {}
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
            config['gemini_api_key'] = self._api_key or ''
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=2)
        except IOError:
            pass

    # ---- API key management ----

    @property
    def is_available(self) -> bool:
        return self._available

    @property
    def api_key(self) -> Optional[str]:
        return self._api_key

    def set_api_key(self, key: str) -> bool:
        """Set and validate the Gemini API key with a quick test call."""
        self._api_key = key.strip()
        if not self._api_key:
            self._available = False
            return False

        # Try models in order
        for model in ['gemini-2.0-flash', 'gemini-1.5-flash']:
            try:
                result = _gemini_request(
                    self._api_key, model, "Say OK",
                    max_tokens=5, timeout=10
                )
                # Check if we got a valid response
                candidates = result.get('candidates', [])
                if candidates:
                    self._model_name = model
                    self._available = True
                    self._save_config()
                    print(f"[LLM] Connected to {model}")
                    return True
            except urllib.error.HTTPError as e:
                body = e.read().decode('utf-8', errors='ignore')
                print(f"[LLM] {model} HTTP {e.code}: {body[:200]}")
                if e.code == 400 and 'not found' in body.lower():
                    continue  # Try next model
                elif e.code in (401, 403):
                    break  # Bad key, don't try other models
                continue
            except Exception as e:
                print(f"[LLM] {model} failed: {e}")
                continue

        self._available = False
        return False

    def remove_api_key(self):
        """Remove API key and disable LLM."""
        self._api_key = None
        self._available = False
        self._save_config()

    # ---- Generation ----

    def generate(self, category: str, confidence: float, severity: int,
                 original_text: str, translated_text: str) -> LLMResponse:
        """
        Generate an empathetic response using Gemini REST API.
        Synchronous — use generate_async for UI thread safety.
        """
        if not self._available or not self._api_key:
            return LLMResponse(text="", success=False, source="template",
                               error="LLM not configured")

        # Detect language (simple heuristic)
        has_turkish = any(c in original_text.lower() for c in 'çğıöşü')
        prompt_template = SYSTEM_PROMPT if has_turkish else SYSTEM_PROMPT_EN

        prompt = prompt_template.format(
            category=category,
            confidence=confidence,
            severity=severity,
            original_text=original_text,
            translated_text=translated_text,
        )

        try:
            result = _gemini_request(
                self._api_key, self._model_name, prompt,
                temperature=0.8, max_tokens=500, timeout=20
            )

            # Extract text from response
            candidates = result.get('candidates', [])
            if not candidates:
                # Check for prompt feedback (blocked)
                feedback = result.get('promptFeedback', {})
                block_reason = feedback.get('blockReason', '')
                if block_reason:
                    return LLMResponse(text="", success=False, source="template",
                                       error=f"Content filtered: {block_reason}")
                return LLMResponse(text="", success=False, source="template",
                                   error="No response from Gemini")

            # Get text from first candidate
            parts = candidates[0].get('content', {}).get('parts', [])
            text = ''.join(p.get('text', '') for p in parts).strip()

            if text:
                return LLMResponse(text=text, success=True, source="gemini")
            else:
                finish_reason = candidates[0].get('finishReason', 'UNKNOWN')
                return LLMResponse(text="", success=False, source="template",
                                   error=f"Empty response (finishReason: {finish_reason})")

        except urllib.error.HTTPError as e:
            body = e.read().decode('utf-8', errors='ignore')[:200]
            print(f"[LLM] Gemini HTTP {e.code}: {body}")
            return LLMResponse(text="", success=False, source="template",
                               error=f"HTTP {e.code}: {body[:100]}")
        except Exception as e:
            print(f"[LLM] Gemini error: {e}")
            return LLMResponse(text="", success=False, source="template",
                               error=str(e)[:100])

    def generate_async(self, category: str, confidence: float, severity: int,
                       original_text: str, translated_text: str,
                       callback: Callable[[LLMResponse], None]):
        """
        Generate response asynchronously (non-blocking for UI).
        Calls callback(LLMResponse) on completion.
        """
        def _worker():
            result = self.generate(category, confidence, severity,
                                   original_text, translated_text)
            callback(result)

        thread = threading.Thread(target=_worker, daemon=True)
        thread.start()


# Singleton instance
_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """Get the global LLM service instance."""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
