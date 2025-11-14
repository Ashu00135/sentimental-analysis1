<div align="center">

# 🎭 Sentiment Analysis Dashboard

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.1-green.svg)](https://flask.palletsprojects.com/)
[![SQLite](https://img.shields.io/badge/SQLite-Local-orange.svg)](https://www.sqlite.org/)
[![Dataset](https://img.shields.io/badge/Dataset-Sentiment140%20(1.6M)-red.svg)](http://help.sentiment140.com/)

An offline, fast, and interactive sentiment analysis dashboard built with Flask and SQLite, powered by the Sentiment140 dataset (1.6M tweets). It includes a real-time analyzer and REST APIs for search, stats, and analysis.

</div>

---

## 🌟 Overview

- 1.6M tweets stored locally in `SQLite` for speed and portability
- Beautiful Flask dashboard (template in `templates/index.html`)
- Real-time text analyzer (rule-based, with confidence score)
- REST API: `/api/stats`, `/api/search`, `/api/random`, `/api/analyze`
- Optional ML pipeline: TF‑IDF + Logistic Regression (`train_model.py`)

For full in-depth docs (screens, endpoints, examples), see `README_COMPLETE.md`.

---

## 📦 Project Structure

```
sentiment_analysis/
├── app.py                   # Flask web app + REST API + analyzer
├── create_offline_db.py     # Build SQLite DB from CSV
├── query_offline_db.py      # Utility to inspect/query DB
├── text_preprocessing.py    # Cleaning/tokenization utilities
├── train_model.py           # TF‑IDF + Logistic Regression trainer
├── templates/
│   └── index.html           # Dashboard UI
├── dataset/
│   └── training.1600000.processed.noemoticon.csv  # Source CSV (place here)
├── sentiment_tweets.db      # Generated SQLite DB (created by script)
├── README_COMPLETE.md       # Detailed documentation
└── README.md                # You are here
```

---

## 🚀 Quick Start (Windows PowerShell)

### 1) Create and activate a virtual environment

```powershell
cd D:\PROJECTS\sentiment_analysis
python -m venv venv_sent
.\venv_sent\Scripts\Activate.ps1
```

### 2) Install dependencies

```powershell
pip install flask
```

If you plan to train the ML model:

```powershell
pip install scikit-learn numpy
```

### 3) Download the dataset

1) Get the CSV: training.1600000.processed.noemoticon.csv
2) Source: http://help.sentiment140.com/for-students
3) Place it in `dataset/`

### 4) Create the local SQLite database

```powershell
python create_offline_db.py
```

This reads the CSV, cleans text, and writes `sentiment_tweets.db`.

### 5) Start the dashboard

```powershell
python app.py
```

Open http://localhost:5000 and explore.

---

## 🔌 API Reference

- `GET /api/stats` → dataset counts, averages, top users
- `GET /api/search?q=<term>&sentiment=<0|4>&page=<n>` → search/paginate tweets
- `GET /api/random?count=<n>&sentiment=<0|4>` → random samples
- `POST /api/analyze` (JSON: `{ "text": "..." }`) → quick rule‑based analysis

Example (PowerShell):

```powershell
curl -X POST http://localhost:5000/api/analyze `
  -H "Content-Type: application/json" `
  -d '{"text":"I love this amazing product but hate the price"}'
```

---

## 🤖 Train a Model (Optional)

Train a simple classifier using TF‑IDF and Logistic Regression on the preprocessed DB.

```powershell
python train_model.py
```

Outputs:
- `sentiment_model.pkl` (classifier)
- `tfidf_vectorizer.pkl` (vectorizer)

Note: `train_model.py` loads data from `sentiment_tweets.db` and automatically splits into train/test.

---

## 🧹 Text Preprocessing

See `text_preprocessing.py` for cleaning steps (URLs/mentions/hashtags removal, tokenization, simple stop‑word removal). The dashboard also exposes the cleaned text for each tweet.

---

## 📚 Dataset Notes

- Source: Sentiment140 (1.6M English tweets)
- Labels: `0` = negative, `4` = positive
- Original fields: `sentiment,tweet_id,date,query,username,text`

Please review the dataset’s terms of use before redistribution.

---

## 🛠️ Development

- Backend: Flask (see `app.py`)
- Templates: Jinja2 (see `templates/index.html`)
- Database: SQLite (file `sentiment_tweets.db`)

Suggested next steps:
- Swap rule‑based analyzer with the trained model
- Add pagination/sorting enhancements to the UI
- Package requirements into `requirements.txt`

---

## 📖 More Documentation

For a deeper walk‑through (screenshots, detailed API examples, DB schema, and more), read `README_COMPLETE.md`.

