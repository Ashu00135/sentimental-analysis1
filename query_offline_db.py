"""
Query Offline SQLite Database
Quick analysis and testing utilities
"""
import sqlite3
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OfflineDB:
    """Simple interface to query offline database"""
    
    def __init__(self, db_path='sentiment_tweets.db'):
        self.db_path = Path(db_path)
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database not found: {db_path}")
        
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row  # Return dict-like rows
    
    def stats(self):
        """Get database statistics"""
        cursor = self.conn.cursor()
        
        # Total tweets
        cursor.execute('SELECT COUNT(*) FROM tweets')
        total = cursor.fetchone()[0]
        
        # Sentiment distribution
        cursor.execute('SELECT sentiment, COUNT(*) FROM tweets GROUP BY sentiment')
        sentiment_dist = dict(cursor.fetchall())
        
        # Cleaned tweets
        cursor.execute('SELECT COUNT(*) FROM tweets WHERE clean_text IS NOT NULL AND clean_text != ""')
        cleaned = cursor.fetchone()[0]
        
        # Database size
        db_size_mb = self.db_path.stat().st_size / 1024 / 1024
        
        logger.info("="*60)
        logger.info("DATABASE STATISTICS")
        logger.info("="*60)
        logger.info(f"Total tweets: {total:,}")
        logger.info(f"Negative (0): {sentiment_dist.get(0, 0):,} ({sentiment_dist.get(0, 0)/total*100:.1f}%)")
        logger.info(f"Positive (4): {sentiment_dist.get(4, 0):,} ({sentiment_dist.get(4, 0)/total*100:.1f}%)")
        logger.info(f"Cleaned: {cleaned:,} ({cleaned/total*100:.1f}%)")
        logger.info(f"Database size: {db_size_mb:.1f} MB")
        logger.info("="*60)
    
    def sample(self, n=5, sentiment=None):
        """Get sample tweets"""
        cursor = self.conn.cursor()
        
        if sentiment is not None:
            cursor.execute(
                'SELECT * FROM tweets WHERE sentiment = ? LIMIT ?',
                (sentiment, n)
            )
        else:
            cursor.execute('SELECT * FROM tweets LIMIT ?', (n,))
        
        rows = cursor.fetchall()
        
        logger.info(f"\n{'='*60}")
        logger.info(f"SAMPLE TWEETS (n={len(rows)})")
        logger.info("="*60)
        
        for i, row in enumerate(rows, 1):
            logger.info(f"\n--- Tweet {i} ---")
            logger.info(f"Tweet ID: {row['tweet_id']}")
            logger.info(f"Sentiment: {'Positive' if row['sentiment'] == 4 else 'Negative'}")
            logger.info(f"Username: @{row['username']}")
            logger.info(f"Original: {row['tweet_text'][:100]}...")
            logger.info(f"Cleaned: {row['clean_text'][:100] if row['clean_text'] else 'N/A'}...")
    
    def query(self, sql, params=None):
        """Execute custom SQL query"""
        cursor = self.conn.cursor()
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        return cursor.fetchall()
    
    def close(self):
        """Close database connection"""
        self.conn.close()


def main():
    """Demo usage"""
    try:
        db = OfflineDB()
        
        # Show stats
        db.stats()
        
        # Show samples
        db.sample(n=3, sentiment=0)  # Negative
        db.sample(n=3, sentiment=4)  # Positive
        
        # Close
        db.close()
        
    except FileNotFoundError:
        logger.error("Database not found! Run create_offline_db.py first")


if __name__ == "__main__":
    main()
