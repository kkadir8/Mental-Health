# 🧠 MindfulAI — Mental Health Assistant

An empathetic AI-powered desktop wellness companion that listens to your journal entries and responds with care — never showing raw clinical labels, always offering supportive guidance.

Built with **PyQt6** + **scikit-learn / XGBoost** • Dark theme • Multi-language

![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python)
![PyQt6](https://img.shields.io/badge/GUI-PyQt6-green?logo=qt)
![scikit-learn](https://img.shields.io/badge/ML-scikit--learn-orange?logo=scikit-learn)
![License](https://img.shields.io/badge/License-MIT-yellow)

## Overview

MindfulAI uses NLP and machine learning to understand the emotional tone of your writing, then responds empathetically with supportive messages and coping strategies — like talking to a caring friend.

### Key Features

- **Empathetic AI Responses** — No raw clinical labels. The app recognizes your emotional state and responds with warmth, not diagnosis
- **Mood Journal** — Write in any language (auto-translated). Get supportive feedback with actionable coping strategies
- **Wellness Dashboard** — Track your emotional journey with mood stats, streaks, and daily wellness tips
- **Guided Breathing** — 3 techniques (4-7-8, Box, Calm Breath) with animated visual guide
- **AI Laboratory** — Train & compare 4 ML models with training time, confusion matrices, and classification reports
- **Crisis Safety Net** — Automatic support resources when high-severity states are detected
- **Dark Theme** — Modern, eye-friendly design throughout

### How It Works

Instead of telling users "you might be depressed", MindfulAI:

| User Mood | What the App Does |
|---|---|
| 😊 Feeling Good | Positive reinforcement + encouragement to keep journaling |
| 😤 Under Pressure | Stress management tips + breathing exercises |
| 😰 Feeling Uneasy | Grounding techniques + mindfulness suggestions |
| 😔 Feeling Low | Warm empathy + coping strategies + gentle professional help suggestion |
| 🌊 Emotional Waves | Mood tracking importance + stability tips |
| ⚠️ In Crisis | Immediate crisis resources + hotline numbers + safety planning |

## Project Structure

```
MentalHealthSentiment/
├── main_app.py                 # Entry point (dark theme, Fusion style)
├── requirements.txt            # Python dependencies
├── data/
│   └── Combined Data.csv       # Dataset (~53K labeled records)
├── models/                     # Saved trained models (.pkl)
├── src/
│   ├── data_pipeline.py        # Data loading, cleaning & TF-IDF vectorization
│   ├── model_factory.py        # Model creation, training & persistence
│   ├── evaluation.py           # Metrics, confusion matrix, classification report
│   ├── user_history.py         # JSON mood journal with rich metadata
│   ├── response_engine.py      # ★ Empathetic AI response generation
│   └── ui/
│       ├── main_window.py      # Sidebar navigation, page routing
│       ├── ai_lab.py           # AI Lab (data discovery + model benchmarking)
│       ├── assistant_ui.py     # Dashboard + Journal panels
│       ├── visualization_widget.py  # Dark-themed Matplotlib canvas
│       ├── breathing_widget.py # ★ Guided breathing exercises
│       ├── about_widget.py     # ★ About & ethics page
│       └── theme.py            # ★ QSS dark theme system
└── user_data.json              # User journal entries (auto-generated)
```

## Installation

### Prerequisites
- Python 3.9 or higher
- pip package manager

### Setup

```bash
# Clone the repository
git clone https://github.com/kkadir8/Mental-Health.git
cd Mental-Health

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Quick Start (macOS/Linux)
```bash
chmod +x baslat.sh
./baslat.sh
```

### Manual Start
```bash
source venv/bin/activate
python main_app.py
```

### Workflow

1. **AI Laboratory** → Load dataset, explore distributions, train models
2. **Journal** → Write your thoughts → get empathetic AI responses with coping tips
3. **Dashboard** → Monitor your mood trends, streaks, and wellness stats
4. **Breathing** → Practice guided breathing exercises when you need calm

## Technical Details

### NLP Pipeline
- **Text Preprocessing**: Lowercasing, HTML entity removal, URL removal, special character filtering
- **Feature Extraction**: TF-IDF Vectorization with bigrams (5000 features, min_df=2, max_df=0.95)
- **Translation**: Auto-translation from any language to English via Google Translate API

### Machine Learning Models
| Model | Best Accuracy | Training Time |
|---|---|---|
| Logistic Regression | ~77% | ~5s |
| Random Forest | ~76% | ~15s |
| XGBoost | ~77% | ~30s |
| SVM (Linear) | ~77% | ~60s |

### Dataset
- **Source**: Combined Mental Health Dataset
- **Size**: ~53,000 labeled text samples
- **Classes**: 7 mental health categories (imbalanced)
- **Split**: 80/20 train/test with stratification

## Screenshots

The app has 5 sections accessible from the sidebar:
- **📊 Dashboard** — Mood overview, streaks, daily tips
- **📝 Journal** — Write & receive empathetic AI feedback
- **🔬 AI Lab** — Data exploration, model training & comparison
- **🌬️ Breathing** — Animated guided breathing exercises
- **ℹ️ About** — Project info + ethical disclaimer

## Author

**Kadir Gedik**

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

> **Disclaimer**: This application is for educational and research purposes only. It is not a substitute for professional mental health care. If you or someone you know is struggling, please reach out to a qualified mental health professional.
