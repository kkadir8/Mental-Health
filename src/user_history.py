import json
import os
from datetime import datetime

class UserHistory:
    def __init__(self, filepath="user_data.json"):
        self.filepath = filepath
        self.entries = []
        self.load_history()

    def load_history(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r', encoding='utf-8') as f:
                    self.entries = json.load(f)
            except Exception as e:
                print(f"Error loading history: {e}")
                self.entries = []
        else:
            self.entries = []

    def add_entry(self, text, sentiment, confidence):
        entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "text": text,
            "sentiment": sentiment,
            "confidence": float(confidence)
        }
        self.entries.append(entry)
        self.save_history()

    def clear_history(self):
        self.entries = []
        self.save_history()

    def save_history(self):
        try:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(self.entries, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving history: {e}")

    def get_stats(self):
        if not self.entries:
            return {"total": 0, "mood_counts": {}, "last_entry": None}
        
        mood_counts = {}
        for e in self.entries:
            s = e.get('sentiment', 'Unknown')
            mood_counts[s] = mood_counts.get(s, 0) + 1
            
        return {
            "total": len(self.entries),
            "mood_counts": mood_counts,
            "last_entry": self.entries[-1] if self.entries else None
        }
