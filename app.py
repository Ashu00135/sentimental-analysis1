"""
Sentiment Analysis Web Dashboard
Flask application to visualize and explore the sentiment database
"""
from flask import Flask, render_template, request, jsonify
import sqlite3
from pathlib import Path
import json
import re

app = Flask(__name__)
DB_PATH = 'sentiment_tweets.db'

# Simple sentiment analysis using word lists
POSITIVE_WORDS = {
    'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'awesome', 'love', 
    'happy', 'joy', 'perfect', 'best', 'beautiful', 'brilliant', 'nice', 'pleased',
    'excited', 'enjoy', 'thanks', 'thank', 'appreciate', 'fun', 'cool', 'super',
    'delighted', 'glad', 'awesome', 'yay', 'yes', 'liked', 'loving', 'loved',
    'positive', 'optimistic', 'hopeful', 'successful', 'win', 'winning', 'winner'
}

NEGATIVE_WORDS = {
    'bad', 'terrible', 'awful', 'horrible', 'worst', 'hate', 'sad', 'angry',
    'upset', 'disappointed', 'disappointing', 'poor', 'sucks', 'suck', 'annoying',
    'frustrating', 'frustrated', 'annoyed', 'mad', 'unhappy', 'dislike', 'disgusting',
    'ugly', 'boring', 'bored', 'waste', 'useless', 'pathetic', 'depressed',
    'negative', 'pessimistic', 'fail', 'failed', 'failure', 'lose', 'losing', 'loser'
}

def analyze_sentiment(text):
    """Simple rule-based sentiment analysis"""
    # Clean and tokenize
    text = text.lower()
    words = re.findall(r'\b\w+\b', text)
    
    # Count positive and negative words
    pos_count = sum(1 for word in words if word in POSITIVE_WORDS)
    neg_count = sum(1 for word in words if word in NEGATIVE_WORDS)
    
    # Calculate sentiment
    if pos_count == 0 and neg_count == 0:
        sentiment = 'neutral'
        confidence = 0.5
    elif pos_count > neg_count:
        sentiment = 'positive'
        confidence = min(0.95, 0.5 + (pos_count / (pos_count + neg_count)) * 0.5)
    elif neg_count > pos_count:
        sentiment = 'negative'
        confidence = min(0.95, 0.5 + (neg_count / (pos_count + neg_count)) * 0.5)
    else:
        sentiment = 'neutral'
        confidence = 0.5
    
    return {
        'sentiment': sentiment,
        'confidence': round(confidence * 100, 1),
        'positive_words': pos_count,
        'negative_words': neg_count,
        'total_words': len(words)
    }


def get_db_connection():
    """Create database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')


@app.route('/api/stats')
def get_stats():
    """Get database statistics"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Total tweets
    cursor.execute('SELECT COUNT(*) as total FROM tweets')
    total = cursor.fetchone()['total']
    
    # Sentiment distribution
    cursor.execute('SELECT sentiment, COUNT(*) as count FROM tweets GROUP BY sentiment')
    sentiment_data = cursor.fetchall()
    
    # Cleaned tweets
    cursor.execute('SELECT COUNT(*) FROM tweets WHERE clean_text IS NOT NULL AND clean_text != ""')
    cleaned = cursor.fetchone()[0]
    
    # Average text length
    cursor.execute('SELECT AVG(text_length) as avg_len, AVG(word_count) as avg_words FROM tweets')
    avg_data = cursor.fetchone()
    
    # Top users
    cursor.execute('''
        SELECT username, COUNT(*) as tweet_count 
        FROM tweets 
        GROUP BY username 
        ORDER BY tweet_count DESC 
        LIMIT 10
    ''')
    top_users = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return jsonify({
        'total_tweets': total,
        'sentiment_distribution': {
            'negative': next((row['count'] for row in sentiment_data if row['sentiment'] == 0), 0),
            'positive': next((row['count'] for row in sentiment_data if row['sentiment'] == 4), 0)
        },
        'cleaned_tweets': cleaned,
        'avg_text_length': round(avg_data['avg_len'], 1) if avg_data['avg_len'] else 0,
        'avg_word_count': round(avg_data['avg_words'], 1) if avg_data['avg_words'] else 0,
        'top_users': top_users
    })


@app.route('/api/search')
def search_tweets():
    """Search tweets by keyword or username"""
    query = request.args.get('q', '')
    sentiment_filter = request.args.get('sentiment', '')
    page = int(request.args.get('page', 1))
    per_page = 20
    offset = (page - 1) * per_page
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    sql = 'SELECT * FROM tweets WHERE 1=1'
    params = []
    
    if query:
        sql += ' AND (tweet_text LIKE ? OR username LIKE ? OR clean_text LIKE ?)'
        search_term = f'%{query}%'
        params.extend([search_term, search_term, search_term])
    
    if sentiment_filter:
        sql += ' AND sentiment = ?'
        params.append(int(sentiment_filter))
    
    # Get total count
    count_sql = sql.replace('SELECT *', 'SELECT COUNT(*)')
    cursor.execute(count_sql, params)
    total = cursor.fetchone()[0]
    
    # Get paginated results
    sql += ' ORDER BY id DESC LIMIT ? OFFSET ?'
    params.extend([per_page, offset])
    
    cursor.execute(sql, params)
    tweets = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return jsonify({
        'tweets': tweets,
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': (total + per_page - 1) // per_page
    })


@app.route('/api/random')
def random_tweets():
    """Get random sample of tweets"""
    count = int(request.args.get('count', 10))
    sentiment_filter = request.args.get('sentiment', '')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    sql = 'SELECT * FROM tweets'
    params = []
    
    if sentiment_filter:
        sql += ' WHERE sentiment = ?'
        params.append(int(sentiment_filter))
    
    sql += ' ORDER BY RANDOM() LIMIT ?'
    params.append(count)
    
    cursor.execute(sql, params)
    tweets = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return jsonify({'tweets': tweets})


@app.route('/api/tweet/<int:tweet_id>')
def get_tweet(tweet_id):
    """Get specific tweet by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM tweets WHERE id = ?', (tweet_id,))
    tweet = cursor.fetchone()
    
    conn.close()
    
    if tweet:
        return jsonify(dict(tweet))
    else:
        return jsonify({'error': 'Tweet not found'}), 404


@app.route('/api/analyze', methods=['POST'])
def analyze_text():
    """Analyze sentiment of custom text"""
    data = request.get_json()
    text = data.get('text', '')
    
    if not text or len(text.strip()) == 0:
        return jsonify({'error': 'Please provide text to analyze'}), 400
    
    # Analyze sentiment
    result = analyze_sentiment(text)
    
    return jsonify({
        'text': text,
        'sentiment': result['sentiment'],
        'confidence': result['confidence'],
        'positive_words': result['positive_words'],
        'negative_words': result['negative_words'],
        'total_words': result['total_words']
    })


if __name__ == '__main__':
    # Check if database exists
    if not Path(DB_PATH).exists():
        print(f"❌ Database not found: {DB_PATH}")
        print("Please run create_offline_db.py first")
        exit(1)
    
    print("="*60)
    print("🚀 SENTIMENT ANALYSIS DASHBOARD")
    print("="*60)
    print(f"📊 Database: {DB_PATH}")
    print(f"🌐 Server: http://localhost:5000")
    print("="*60)
    print("\nPress CTRL+C to stop the server")
    print("="*60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
