"""
User journal & mood history — JSON-based local storage.
"""

import json
import os
from datetime import datetime

HISTORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            '..', 'user_data.json')


class UserHistory:
    """Persistent mood journal stored as JSON."""

    def __init__(self, filepath=None):
        self.filepath = filepath or HISTORY_FILE
        self.entries: list[dict] = []
        self.load_history()

    def load_history(self):
        try:
            if os.path.exists(self.filepath):
                with open(self.filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.entries = data if isinstance(data, list) else []
            else:
                self.entries = []
        except (json.JSONDecodeError, IOError):
            self.entries = []

    def save_history(self):
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(self.entries, f, ensure_ascii=False, indent=2)

    def add_entry(self, text: str, sentiment: str, confidence: float,
                  original_text: str = None, mood_label: str = None,
                  severity: int = 1):
        """Add a journal entry with rich metadata."""
        entry = {
            'text': text,
            'original_text': original_text or text,
            'sentiment': sentiment,
            'mood_label': mood_label or sentiment,
            'confidence': round(confidence, 4),
            'severity': severity,
            'timestamp': datetime.now().isoformat()
        }
        self.entries.append(entry)
        self.save_history()
        return entry

    def clear_history(self):
        self.entries = []
        self.save_history()

    def get_stats(self) -> dict:
        """Return summary statistics."""
        if not self.entries:
            return {
                'total': 0,
                'mood_counts': {},
                'last_entry': None,
                'streak': 0,
                'avg_severity': 0,
                'mood_timeline': []
            }

        mood_counts: dict[str, int] = {}
        for e in self.entries:
            label = e.get('mood_label', e.get('sentiment', 'Unknown'))
            mood_counts[label] = mood_counts.get(label, 0) + 1

        # Calculate day streak
        dates = set()
        for e in self.entries:
            try:
                dt = datetime.fromisoformat(e['timestamp'])
                dates.add(dt.date())
            except (KeyError, ValueError):
                pass

        streak = 0
        if dates:
            today = datetime.now().date()
            from datetime import timedelta
            check = today
            while check in dates:
                streak += 1
                check -= timedelta(days=1)

        # Average severity
        severities = [e.get('severity', 1) for e in self.entries]
        avg_sev = sum(severities) / len(severities) if severities else 0

        # Mood timeline (last 30 entries)
        timeline = []
        for e in self.entries[-30:]:
            try:
                dt = datetime.fromisoformat(e['timestamp'])
                timeline.append({
                    'date': dt.strftime('%m/%d'),
                    'mood': e.get('mood_label', e.get('sentiment', '')),
                    'severity': e.get('severity', 1)
                })
            except (KeyError, ValueError):
                pass

        return {
            'total': len(self.entries),
            'mood_counts': mood_counts,
            'last_entry': self.entries[-1] if self.entries else None,
            'streak': streak,
            'avg_severity': round(avg_sev, 2),
            'mood_timeline': timeline
        }
