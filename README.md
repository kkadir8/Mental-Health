# Mental Health Sentiment Analyzer

A desktop AI application that analyzes mental health sentiment from text using NLP and machine learning. Built with **PyQt6** for the GUI and **scikit-learn / XGBoost** for the ML backend.

![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python)
![PyQt6](https://img.shields.io/badge/GUI-PyQt6-green?logo=qt)
![scikit-learn](https://img.shields.io/badge/ML-scikit--learn-orange?logo=scikit-learn)
![License](https://img.shields.io/badge/License-MIT-yellow)

## Overview

This application provides:

- **AI Laboratory** — Load the dataset, explore class distributions, train and compare multiple ML algorithms (Logistic Regression, Random Forest, XGBoost, SVM) side by side with confusion matrix and performance metrics.
- **Mood Journal** — Write your thoughts in any language (auto-translated to English), and the trained model predicts the mental health sentiment with confidence scores.
- **Dashboard** — Track your mood history over time with visual charts and statistics.

### Mental Health Categories

The model classifies text into **7 categories**:
| Category | Description |
|---|---|
| Normal | Healthy mental state |
| Depression | Depressive symptoms |
| Anxiety | Anxiety-related expressions |
| Stress | Stress indicators |
| Suicidal | Suicidal ideation (critical) |
| Bipolar | Bipolar disorder indicators |
| Personality disorder | Personality disorder patterns |

## Project Structure

```
MentalHealthSentiment/
├── main_app.py                 # Application entry point
├── requirements.txt            # Python dependencies
├── baslat.sh                   # Quick launch script (macOS/Linux)
├── data/
│   └── Combined Data.csv       # Dataset (~53K labeled records)
├── models/                     # Saved trained models (.pkl)
├── src/
│   ├── data_pipeline.py        # Data loading, cleaning & TF-IDF vectorization
│   ├── model_factory.py        # Model creation, training & persistence
│   ├── evaluation.py           # Metrics, confusion matrix, ROC curves
│   ├── user_history.py         # JSON-based mood journal storage
│   └── ui/
│       ├── main_window.py      # Main application window
│       ├── ai_lab.py           # AI Laboratory (data discovery + benchmarking)
│       ├── assistant_ui.py     # Dashboard & Journal panels
│       └── visualization_widget.py  # Matplotlib canvas for PyQt6
└── user_data.json              # User journal entries (auto-generated)
```

## Installation

### Prerequisites
- Python 3.9 or higher
- pip package manager

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/MentalHealthSentiment.git
cd MentalHealthSentiment

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

1. **Open the app** → Go to the **AI Laboratory** tab
2. **Data Discovery** → Click "Load & Analyze Dataset" to explore the data
3. **Model Comparison** → Select an algorithm and click "Train & Bench", or use "Train All Models" to benchmark all 4 algorithms
4. **My Journal** → Write your thoughts and click "Analyze & Save to Journal"
5. **Dashboard** → View your mood history and trends

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

The application has 3 main tabs:
- **Dashboard** — Mood summary with bar charts
- **My Journal** — Text input with AI-powered sentiment analysis
- **AI Laboratory** — Data exploration, model training & comparison with confusion matrices

## Author

**Kadir Gedik**

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

> **Disclaimer**: This application is for educational and research purposes only. It is not a substitute for professional mental health care. If you or someone you know is struggling, please reach out to a qualified mental health professional.
