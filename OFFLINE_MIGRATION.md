# Offline SQLite Migration Guide

## 🎯 Why SQLite?

**Problem:** Supabase storage limit reached (490 MB at 1.095M tweets)
**Solution:** Local SQLite database with unlimited storage

### Benefits:
- ✅ **No storage limits** - Local disk space only
- ✅ **100x faster** - No network calls, bulk inserts
- ✅ **No API costs** - Everything local
- ✅ **Easy queries** - Standard SQL
- ✅ **Portable** - Single `.db` file

## 📊 Current Status

### Supabase (Cloud):
- Total tweets: 1,095,500
- Preprocessed: 50,097 (4.6%)
- Storage: 490 MB (FULL)
- Update rate: 4.8 tweets/sec
- Estimated completion: 60+ hours ❌

### SQLite (Local):
- Total capacity: Unlimited (disk space)
- Expected rate: 1,000-5,000 tweets/sec ✅
- Estimated completion: 30-60 minutes ✅
- All 1.6M tweets preprocessed locally

## 🚀 Migration Steps

### Step 1: Create Offline Database

```powershell
# Activate virtual environment
D:\PROJECTS\sentiment_analysis\venv_sent\Scripts\activate

# Create offline database (processes ALL 1.6M tweets)
python create_offline_db.py
```

**What it does:**
1. Creates `sentiment_tweets.db` with optimized schema
2. Reads entire CSV (1.6M tweets)
3. Preprocesses each tweet inline
4. Bulk inserts (10,000 at a time)
5. Creates indexes for fast queries

**Expected output:**
```
📊 Processed 1,600,000 tweets | Rate: 2000 tweets/sec
✅ Total tweets: 1,600,000
📁 Database file: sentiment_tweets.db
💾 Database size: ~800 MB
⏱️  Time taken: 15-30 minutes
```

### Step 2: Query Database

```powershell
# Check database stats
python query_offline_db.py
```

**Example output:**
```
DATABASE STATISTICS
Total tweets: 1,600,000
Negative (0): 800,000 (50.0%)
Positive (4): 800,000 (50.0%)
Cleaned: 1,600,000 (100.0%)
Database size: 800.0 MB
```

### Step 3: Direct SQL Queries

```powershell
# Open SQLite shell
sqlite3 sentiment_tweets.db

# Example queries:
sqlite> SELECT COUNT(*) FROM tweets;
sqlite> SELECT sentiment, COUNT(*) FROM tweets GROUP BY sentiment;
sqlite> SELECT * FROM tweets WHERE username = 'someuser' LIMIT 5;
sqlite> .exit
```

## 📁 Database Schema

```sql
CREATE TABLE tweets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tweet_id TEXT UNIQUE NOT NULL,
    sentiment INTEGER NOT NULL CHECK (sentiment IN (0, 4)),
    date_posted TEXT,
    query_term TEXT,
    username TEXT,
    tweet_text TEXT NOT NULL,
    clean_text TEXT,              -- ✅ Preprocessed text
    text_length INTEGER,
    word_count INTEGER,
    predicted_sentiment INTEGER,   -- To be filled by model
    confidence_score REAL,         -- To be filled by model
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for fast queries
CREATE INDEX idx_sentiment ON tweets(sentiment);
CREATE INDEX idx_tweet_id ON tweets(tweet_id);
CREATE INDEX idx_username ON tweets(username);
```

## 🔄 What About Existing Supabase Data?

**Option 1: Start Fresh (Recommended)**
- SQLite will process all 1.6M tweets from CSV
- Much faster than downloading from Supabase
- Clean, consistent data

**Option 2: Export from Supabase**
- Download 50k preprocessed tweets
- Import into SQLite
- Continue with remaining 1.55M

**Recommendation:** Option 1 is faster and simpler

## 📈 Next Steps After Migration

### 1. Feature Extraction
```python
from sklearn.feature_extraction.text import TfidfVectorizer
import sqlite3

conn = sqlite3.connect('sentiment_tweets.db')
cursor = conn.cursor()

# Load clean text
cursor.execute('SELECT clean_text, sentiment FROM tweets')
data = cursor.fetchall()

# Create TF-IDF features
vectorizer = TfidfVectorizer(max_features=5000)
X = vectorizer.fit_transform([row[0] for row in data])
y = [0 if row[1] == 0 else 1 for row in data]
```

### 2. Train Model
```python
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

accuracy = model.score(X_test, y_test)
print(f"Accuracy: {accuracy:.2%}")  # Target: 90%+
```

### 3. Update Predictions
```python
# Predict on all tweets
predictions = model.predict(X)
probabilities = model.predict_proba(X)

# Update database
cursor.execute('SELECT id FROM tweets')
tweet_ids = [row[0] for row in cursor.fetchall()]

for tweet_id, pred, prob in zip(tweet_ids, predictions, probabilities):
    confidence = max(prob)
    cursor.execute('''
        UPDATE tweets 
        SET predicted_sentiment = ?, confidence_score = ?
        WHERE id = ?
    ''', (pred, confidence, tweet_id))

conn.commit()
```

## 🛠️ Python Interface

```python
from query_offline_db import OfflineDB

# Open database
db = OfflineDB('sentiment_tweets.db')

# Get statistics
db.stats()

# Sample tweets
db.sample(n=5, sentiment=0)  # Negative
db.sample(n=5, sentiment=4)  # Positive

# Custom query
results = db.query('SELECT * FROM tweets WHERE text_length > 200 LIMIT 10')

# Close
db.close()
```

## 📊 Performance Comparison

| Operation | Supabase (Cloud) | SQLite (Local) |
|-----------|------------------|----------------|
| Upload rate | 400-600/sec | 2,000-5,000/sec |
| Update rate | 4.8/sec | 10,000+/sec |
| Storage limit | 490 MB (FULL) | Unlimited |
| Query speed | 100-500ms | <10ms |
| Cost | $$ (storage fees) | $0 |
| Preprocessing 1.6M | 60+ hours | 30-60 minutes |

## ⚠️ Important Notes

1. **Backup CSV:** Keep original `training.1600000.processed.noemoticon.csv` safe
2. **Database backup:** Copy `sentiment_tweets.db` after creation
3. **Disk space:** Ensure ~1-2 GB free space
4. **Progress:** Script shows real-time progress and can be interrupted (Ctrl+C)

## 🎯 Expected Timeline

- ✅ Database creation: 30-60 minutes
- ✅ Feature extraction: 5-10 minutes
- ✅ Model training: 10-30 minutes
- ✅ Prediction updates: 5-10 minutes
- **Total: 1-2 hours** (vs 60+ hours with Supabase)

## 🚨 Troubleshooting

**Error: "Database is locked"**
- Close all SQLite connections
- Delete `sentiment_tweets.db-journal` if exists

**Error: "Disk full"**
- Need at least 1-2 GB free space
- Check with `Get-PSDrive C`

**Slow performance:**
- Ensure no antivirus scanning `.db` file
- Close other programs
- Expected: 1,000-5,000 tweets/sec

## ✅ Summary

Run this single command to create complete offline database:

```powershell
D:\PROJECTS\sentiment_analysis\venv_sent\Scripts\activate
python create_offline_db.py
```

This will:
- ✅ Process all 1.6M tweets
- ✅ Preprocess and clean text
- ✅ Store in local SQLite database
- ✅ Complete in 30-60 minutes
- ✅ Ready for ML training

**No more Supabase storage limits! 🎉**
