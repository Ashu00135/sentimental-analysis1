"""
Create Offline SQLite Database from CSV
Load all 1.6M tweets into local SQLite database
MUCH faster than Supabase and unlimited storage
"""
import sqlite3
import csv
import time
from pathlib import Path
from text_preprocessing import TextPreprocessor
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_sqlite_database():
    """Create SQLite database with optimized schema"""
    
    logger.info("="*80)
    logger.info("CREATE OFFLINE SQLITE DATABASE")
    logger.info("="*80)
    
    csv_path = Path("dataset/training.1600000.processed.noemoticon.csv")
    db_path = Path("sentiment_tweets.db")
    
    if not csv_path.exists():
        logger.error(f"CSV not found: {csv_path}")
        return
    
    # Delete existing database
    if db_path.exists():
        logger.info(f"⚠️  Deleting existing database: {db_path}")
        db_path.unlink()
    
    # Create database
    logger.info(f"📊 Creating database: {db_path}")
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Create table with indexes
    logger.info("📋 Creating schema...")
    cursor.execute('''
        CREATE TABLE tweets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tweet_id TEXT UNIQUE NOT NULL,
            sentiment INTEGER NOT NULL CHECK (sentiment IN (0, 4)),
            date_posted TEXT,
            query_term TEXT,
            username TEXT,
            tweet_text TEXT NOT NULL,
            clean_text TEXT,
            text_length INTEGER,
            word_count INTEGER,
            predicted_sentiment INTEGER,
            confidence_score REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create indexes
    cursor.execute('CREATE INDEX idx_sentiment ON tweets(sentiment)')
    cursor.execute('CREATE INDEX idx_tweet_id ON tweets(tweet_id)')
    cursor.execute('CREATE INDEX idx_username ON tweets(username)')
    
    conn.commit()
    logger.info("✅ Schema created with indexes")
    
    # Initialize preprocessor
    preprocessor = TextPreprocessor()
    
    # Load CSV and insert
    logger.info(f"📖 Reading {csv_path.name}...")
    
    batch_size = 10000  # Large batch for SQLite
    batch = []
    total_processed = 0
    start_time = time.time()
    
    try:
        with open(csv_path, 'r', encoding='latin-1') as f:
            reader = csv.reader(f)
            
            for row_num, row in enumerate(reader, 1):
                if len(row) < 6:
                    continue
                
                # Parse row
                tweet_id = row[1]
                sentiment = int(row[0])
                date = row[2]
                query = row[3] if row[3] != 'NO_QUERY' else None
                username = row[4]
                tweet_text = row[5]
                
                # Preprocess
                try:
                    clean_text = preprocessor.preprocess(tweet_text)
                except Exception as e:
                    clean_text = ""
                
                # Add to batch
                batch.append((
                    tweet_id, sentiment, date, query, username,
                    tweet_text, clean_text,
                    len(tweet_text), len(tweet_text.split())
                ))
                
                # Insert batch
                if len(batch) >= batch_size:
                    cursor.executemany('''
                        INSERT OR IGNORE INTO tweets 
                        (tweet_id, sentiment, date_posted, query_term, username, 
                         tweet_text, clean_text, text_length, word_count)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', batch)
                    
                    conn.commit()
                    total_processed += len(batch)
                    
                    elapsed = time.time() - start_time
                    rate = total_processed / elapsed if elapsed > 0 else 0
                    
                    logger.info(
                        f"📊 Processed {total_processed:,} tweets "
                        f"(Row {row_num:,}) | "
                        f"Rate: {rate:.0f} tweets/sec"
                    )
                    
                    batch = []
            
            # Insert remaining
            if batch:
                cursor.executemany('''
                    INSERT OR IGNORE INTO tweets 
                    (tweet_id, sentiment, date_posted, query_term, username, 
                     tweet_text, clean_text, text_length, word_count)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', batch)
                conn.commit()
                total_processed += len(batch)
    
    except KeyboardInterrupt:
        logger.warning("\n⚠️  Interrupted by user")
        conn.commit()
    except Exception as e:
        logger.error(f"\n❌ Error: {e}", exc_info=True)
    finally:
        elapsed = time.time() - start_time
        
        # Get final count
        cursor.execute('SELECT COUNT(*) FROM tweets')
        final_count = cursor.fetchone()[0]
        
        # Get sentiment distribution
        cursor.execute('SELECT sentiment, COUNT(*) FROM tweets GROUP BY sentiment')
        sentiment_dist = dict(cursor.fetchall())
        
        # Database size
        db_size_mb = db_path.stat().st_size / 1024 / 1024
        
        conn.close()
        
        logger.info("\n" + "="*80)
        logger.info("DATABASE CREATION COMPLETE")
        logger.info("="*80)
        logger.info(f"✅ Total tweets: {final_count:,}")
        logger.info(f"📊 Sentiment distribution:")
        logger.info(f"   Negative (0): {sentiment_dist.get(0, 0):,}")
        logger.info(f"   Positive (4): {sentiment_dist.get(4, 0):,}")
        logger.info(f"📁 Database file: {db_path}")
        logger.info(f"💾 Database size: {db_size_mb:.1f} MB")
        logger.info(f"⏱️  Time taken: {elapsed/60:.1f} minutes")
        if elapsed > 0:
            logger.info(f"📈 Average rate: {total_processed/elapsed:.0f} tweets/sec")
        logger.info("="*80)
        logger.info("\nNext steps:")
        logger.info("1. Use 'sqlite3 sentiment_tweets.db' to query")
        logger.info("2. Train ML model using this database")
        logger.info("3. All data is local - no Supabase storage needed!")
        logger.info("="*80)


if __name__ == "__main__":
    create_sqlite_database()
