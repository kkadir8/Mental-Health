"""
Response Engine — The empathetic brain of the Mental Health Assistant.

Instead of showing raw clinical labels like 'Suicidal' or 'Depression',
this engine generates warm, supportive, research-backed responses based on
the detected mental health category and confidence level.

Design principles:
  - NEVER show raw clinical labels to the user
  - Always validate feelings first
  - Provide actionable coping strategies
  - Show crisis resources for high-severity cases
  - Encourage professional help when appropriate
  - Maintain a warm, non-judgmental tone
"""

import random
from dataclasses import dataclass
from typing import List, Optional

# ---------------------------------------------------------------------------
# Friendly mood labels (user-facing) mapped from clinical categories
# ---------------------------------------------------------------------------
MOOD_MAP = {
    "Normal":               {"label": "Feeling Good",      "emoji": "😊", "color": "#27ae60", "severity": 1},
    "Stress":               {"label": "Under Pressure",    "emoji": "😤", "color": "#f39c12", "severity": 2},
    "Anxiety":              {"label": "Feeling Uneasy",    "emoji": "😰", "color": "#e67e22", "severity": 3},
    "Depression":           {"label": "Feeling Low",       "emoji": "😔", "color": "#8e44ad", "severity": 4},
    "Bipolar":              {"label": "Emotional Waves",   "emoji": "🌊", "color": "#2980b9", "severity": 4},
    "Personality disorder": {"label": "Inner Conflict",    "emoji": "💭", "color": "#7f8c8d", "severity": 4},
    "Suicidal":             {"label": "In Deep Pain",      "emoji": "💙", "color": "#e74c3c", "severity": 5},
}

# ---------------------------------------------------------------------------
# Empathetic acknowledgments by severity level
# ---------------------------------------------------------------------------
ACKNOWLEDGMENTS = {
    1: [
        "It's wonderful to hear you're doing well! 🌟",
        "I'm glad you're in a good place right now. Keep it up!",
        "Your positive energy is inspiring. Thank you for sharing!",
        "It sounds like things are going well — that's great to hear.",
    ],
    2: [
        "I hear you — stress can feel overwhelming, but you're not alone.",
        "It sounds like you're carrying a heavy load right now. That takes real strength.",
        "Pressure can build up, and it's important you're acknowledging it.",
        "Thank you for being honest about how you feel. Stress is a valid feeling.",
    ],
    3: [
        "What you're feeling is completely valid. Anxiety can be really tough.",
        "I understand that uneasy feeling. You're brave for expressing it.",
        "Anxiety doesn't define you — it's just something you're experiencing right now.",
        "Thank you for trusting me with this. Feeling anxious is more common than you think.",
    ],
    4: [
        "I'm here for you. What you're going through sounds really difficult.",
        "Thank you for sharing something so personal. Your feelings matter.",
        "I want you to know that feeling this way doesn't make you weak — it makes you human.",
        "You don't have to go through this alone. I'm glad you're expressing yourself.",
        "It takes courage to put these feelings into words. I hear you.",
    ],
    5: [
        "I'm really glad you reached out. What you're feeling right now is serious, and you deserve support.",
        "You are not alone, even though it might feel that way. Please know that help is available.",
        "I hear you, and I want you to know that your life has value. This pain can get better with the right support.",
        "Thank you for being honest about how you feel. That takes incredible courage.",
    ],
}

# ---------------------------------------------------------------------------
# Supportive messages / coping advice by category
# ---------------------------------------------------------------------------
SUPPORTIVE_MESSAGES = {
    "Normal": [
        "Keep nurturing your well-being! Consider writing about what's making you feel good — gratitude journaling can strengthen positive feelings.",
        "This is a great time to build resilience. Try setting a small goal for today that brings you joy.",
        "Positive moments are worth celebrating. What made you smile today?",
    ],
    "Stress": [
        "When stress builds up, your body needs a reset. Try the 4-7-8 breathing technique: inhale for 4 seconds, hold for 7, exhale for 8.",
        "Consider breaking your tasks into smaller, manageable pieces. You don't have to solve everything at once.",
        "Physical movement is one of the best stress relievers. Even a 10-minute walk can make a difference.",
        "Try progressive muscle relaxation: tense each muscle group for 5 seconds, then release. Start from your toes and work up.",
    ],
    "Anxiety": [
        "Let's try a grounding exercise: Name 5 things you can see, 4 you can touch, 3 you can hear, 2 you can smell, and 1 you can taste.",
        "Anxiety often lives in the future. Try bringing yourself back to the present moment — what is actually happening right now?",
        "Deep breathing can activate your body's calming response. Try breathing in for 4 counts, out for 6 counts, for 2 minutes.",
        "Write down your worries, then ask: 'Is this something I can control?' Focus your energy on what you can influence.",
    ],
    "Depression": [
        "Even small steps matter. Can you do one kind thing for yourself today? It could be as simple as drinking water or stepping outside for a moment.",
        "Depression can make everything feel heavy. Remember: you don't have to feel motivated to take action — sometimes action comes first, and motivation follows.",
        "Connection helps. Can you reach out to someone you trust today, even with a simple 'hi'?",
        "You might not believe this right now, but this feeling is temporary. Many people have walked this path and found their way through.",
    ],
    "Bipolar": [
        "Tracking your mood patterns is incredibly valuable. Notice what triggers shifts — sleep, stress, social situations.",
        "Consistency in daily routines (sleep, meals, exercise) can help stabilize mood fluctuations.",
        "Be gentle with yourself during both highs and lows. Neither defines who you truly are.",
        "Consider keeping a mood diary alongside this journal to track patterns over time.",
    ],
    "Personality disorder": [
        "Your emotions are valid, even when they feel intense or confusing. Learning to observe them without judgment is a powerful skill.",
        "DBT (Dialectical Behavior Therapy) skills like 'TIPP' can help: Temperature (cold water on face), Intense exercise, Paced breathing, Progressive relaxation.",
        "Try the 'wise mind' approach: balance your emotional feelings with rational thoughts to find your centered self.",
    ],
    "Suicidal": [
        "Your pain is real, and you deserve help right now. Please consider reaching out to a crisis helpline.",
        "You don't have to figure this out alone. There are trained professionals available 24/7 who want to help.",
        "Sometimes the bravest thing you can do is ask for help. You've already taken a step by writing this down.",
    ],
}

# ---------------------------------------------------------------------------
# Crisis resources (shown for severity >= 5)
# ---------------------------------------------------------------------------
CRISIS_RESOURCES = """
🆘 **If you're in immediate danger, please reach out now:**

🇹🇷 **Turkey**: 182 (Alo Psikiyatri Hattı) | 112 (Acil)
🇺🇸 **USA**: 988 (Suicide & Crisis Lifeline) | Text HOME to 741741
🇬🇧 **UK**: 116 123 (Samaritans)
🌍 **International**: https://findahelpline.com

💬 You can also text a crisis counselor — you don't have to call.
🏥 Consider visiting your nearest emergency room if you feel unsafe.

**Remember: Asking for help is a sign of strength, not weakness.**
"""

# ---------------------------------------------------------------------------
# Professional help suggestion (shown for severity >= 3)
# ---------------------------------------------------------------------------
PROFESSIONAL_HELP = {
    3: "💡 **Tip:** If these feelings persist, talking to a counselor or therapist can be very helpful. You deserve support.",
    4: "🩺 **Important:** Please consider speaking with a mental health professional. Therapy and/or medication can make a real difference. You deserve to feel better.",
    5: "🚨 **Please reach out to a professional or crisis line now.** You don't have to carry this alone.",
}

# ---------------------------------------------------------------------------
# Daily wellness tips (shown randomly)
# ---------------------------------------------------------------------------
DAILY_TIPS = [
    "🧘 Try 5 minutes of mindfulness meditation today.",
    "🚶 A short walk in nature can boost your mood significantly.",
    "💧 Stay hydrated — dehydration can worsen anxiety and fatigue.",
    "😴 Aim for 7-9 hours of sleep. Sleep is foundational for mental health.",
    "📝 Writing down 3 things you're grateful for can shift your perspective.",
    "🎵 Listen to music that makes you feel calm or uplifted.",
    "🤗 Reach out to a friend or loved one today, even if just to say hi.",
    "🍎 Nourish your body with wholesome food — it affects your mood more than you think.",
    "📵 Take a 30-minute break from screens and social media.",
    "🌅 Spend a few minutes watching the sunrise or sunset.",
    "💪 Move your body for at least 15 minutes — dance, stretch, walk.",
    "📖 Read something inspiring or uplifting before bed instead of scrolling.",
]

# ---------------------------------------------------------------------------
# Follow-up prompts to encourage continued journaling
# ---------------------------------------------------------------------------
FOLLOWUP_PROMPTS = {
    1: [
        "What made today special for you?",
        "Who or what are you grateful for today?",
        "What's something you're looking forward to?",
    ],
    2: [
        "What's the one thing causing the most stress right now?",
        "If you could let go of one worry, what would it be?",
        "What usually helps you decompress after a long day?",
    ],
    3: [
        "When did you first notice this anxious feeling today?",
        "What's one thing that would make you feel safer right now?",
        "Is there someone you trust that you could talk to about this?",
    ],
    4: [
        "What's been on your mind the most lately?",
        "Can you remember a time when you felt a little better? What was different?",
        "What's one small thing you could do for yourself today?",
    ],
    5: [
        "Would you feel comfortable telling someone you trust about how you're feeling?",
        "What would help you feel even a little bit safer right now?",
    ],
}


@dataclass
class AssistantResponse:
    """Structured response from the Mental Health Assistant."""
    mood_label: str          # User-friendly mood label (e.g., "Feeling Low")
    mood_emoji: str          # Emoji representation
    mood_color: str          # Color for UI
    severity: int            # 1-5 severity level
    acknowledgment: str      # Empathetic opening
    supportive_message: str  # Main advice/coping strategy
    professional_help: str   # Professional help suggestion (if applicable)
    crisis_resources: str    # Crisis resources (if severity >= 5)
    daily_tip: str           # Random wellness tip
    followup_prompt: str     # Prompt for next journal entry
    confidence: float        # Model confidence
    clinical_category: str   # Internal category (not shown to user directly)


class ResponseEngine:
    """
    Generates empathetic, supportive responses based on ML predictions.
    
    This engine transforms raw clinical classifications into warm, helpful
    assistant responses with actionable coping strategies.
    """

    def generate_response(self, category: str, confidence: float) -> AssistantResponse:
        """
        Generate a complete assistant response for the given prediction.
        
        Args:
            category: Clinical category from the ML model
            confidence: Model prediction confidence (0.0 - 1.0)
        
        Returns:
            AssistantResponse with all fields populated
        """
        mood_info = MOOD_MAP.get(category, MOOD_MAP["Normal"])
        severity = mood_info["severity"]

        # Adjust severity based on confidence
        # Low confidence on high-severity → reduce perceived severity
        if confidence < 0.5 and severity >= 4:
            severity = max(severity - 1, 2)

        acknowledgment = random.choice(ACKNOWLEDGMENTS.get(severity, ACKNOWLEDGMENTS[1]))
        supportive_message = random.choice(SUPPORTIVE_MESSAGES.get(category, SUPPORTIVE_MESSAGES["Normal"]))
        professional_help = PROFESSIONAL_HELP.get(severity, "")
        crisis_resources = CRISIS_RESOURCES if severity >= 5 else ""
        daily_tip = random.choice(DAILY_TIPS)
        followup_prompt = random.choice(FOLLOWUP_PROMPTS.get(severity, FOLLOWUP_PROMPTS[1]))

        return AssistantResponse(
            mood_label=mood_info["label"],
            mood_emoji=mood_info["emoji"],
            mood_color=mood_info["color"],
            severity=severity,
            acknowledgment=acknowledgment,
            supportive_message=supportive_message,
            professional_help=professional_help,
            crisis_resources=crisis_resources,
            daily_tip=daily_tip,
            followup_prompt=followup_prompt,
            confidence=confidence,
            clinical_category=category,
        )

    def get_mood_info(self, category: str) -> dict:
        """Get mood display info for a category."""
        return MOOD_MAP.get(category, MOOD_MAP["Normal"])

    def get_daily_tip(self) -> str:
        """Get a random daily wellness tip."""
        return random.choice(DAILY_TIPS)
