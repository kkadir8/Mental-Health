"""
LLM Service — Google Gemini integration for empathetic AI responses.

Uses Gemini 2.0 Flash (free tier: 15 RPM, 1M tokens/day).
Falls back gracefully to template responses if API key is missing or quota exceeded.
"""

import os
import json
import threading
from typing import Optional, Callable
from dataclasses import dataclass

# Config file for storing API key locally
CONFIG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
CONFIG_FILE = os.path.join(CONFIG_DIR, '.env_config.json')

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


class LLMService:
    """
    Google Gemini integration with graceful fallback.
    
    Usage:
        service = LLMService()
        service.set_api_key("your-key")
        service.generate_async(prompt, callback_fn)
    """

    def __init__(self):
        self._api_key: Optional[str] = None
        self._model = None
        self._available = False
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
        """Set and validate the Gemini API key."""
        self._api_key = key.strip()
        try:
            import google.generativeai as genai
            genai.configure(api_key=self._api_key)
            self._model = genai.GenerativeModel('gemini-2.0-flash')
            self._available = True
            self._save_config()
            return True
        except Exception as e:
            print(f"[LLM] Failed to configure Gemini: {e}")
            self._available = False
            self._model = None
            return False

    def remove_api_key(self):
        """Remove API key and disable LLM."""
        self._api_key = None
        self._model = None
        self._available = False
        self._save_config()

    # ---- Generation ----

    def generate(self, category: str, confidence: float, severity: int,
                 original_text: str, translated_text: str) -> LLMResponse:
        """
        Generate an empathetic response using Gemini.
        Synchronous — use generate_async for UI thread safety.
        """
        if not self._available or not self._model:
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
            response = self._model.generate_content(
                prompt,
                generation_config={
                    'temperature': 0.8,
                    'top_p': 0.9,
                    'max_output_tokens': 500,
                }
            )
            text = response.text.strip()
            if text:
                return LLMResponse(text=text, success=True, source="gemini")
            else:
                return LLMResponse(text="", success=False, source="template",
                                   error="Empty response from Gemini")
        except Exception as e:
            error_msg = str(e)
            print(f"[LLM] Gemini error: {error_msg}")
            return LLMResponse(text="", success=False, source="template",
                               error=error_msg)

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
