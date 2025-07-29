"""
Test module for RSS feed fetching functionality.
Tests the RSS discovery and fetching capabilities of the news service.
"""

import sys
import os
from datetime import datetime

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app.database import SessionLocal
from app.models import RSSSource, RawNews
from app.services.news_service import logger
import feedparser
import requests
import ssl
import certifi

class RSSFeedFetcherTest:
    """Test class for RSS feed fetching functionality."""
    
    # Updated with discovered feeds
    aggregator_sources = [
        ("Economic Times", [
            "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
        ]),
        ("CNBC-TV18", [
            "https://www.cnbctv18.com/commonfeeds/v1/cne/rss/latest.xml",
            "https://www.cnbctv18.com/commonfeeds/v1/cne/rss/business.xml",
            "https://www.cnbctv18.com/commonfeeds/v1/cne/rss/economy.xml",
            "https://www.cnbctv18.com/commonfeeds/v1/cne/rss/market.xml",
        ]),
        ("Times of India", [
            "http://timesofindia.indiatimes.com/rssfeedstopstories.cms",
            "http://timesofindia.indiatimes.com/rssfeedmostrecent.cms",
            "http://timesofindia.indiatimes.com/rssfeeds/3942666.cms",
        ]),
    ]

    @classmethod
    def test_fetch_all(cls):
        """Test fetching from all RSS sources."""
        print("=== RSS Feed Fetching Test ===")
        for source, urls in cls.aggregator_sources:
            for url in urls:
                print(f"\nFetching from [{source}] {url}")
                try:
                    # Try with proper SSL first
                    try:
                        response = requests.get(url, verify=certifi.where(), timeout=10)
                        response.raise_for_status()
                        print(f"  [SSL OK] Successfully fetched with SSL verification")
                    except Exception as ssl_error:
                        # Fall back to unverified SSL for development
                        print(f"  [SSL Warning] SSL verification failed, trying without verification: {str(ssl_error)}")
                        response = requests.get(url, verify=False, timeout=10)
                        response.raise_for_status()
                        print(f"  [SSL OK] Successfully fetched without SSL verification")
                    
                    # Parse the content with feedparser
                    feed = feedparser.parse(response.content)
                    
                    if not feed.entries:
                        print(f"  [Warning] No or empty response from: {url}")
                    else:
                        print(f"  [Success] Fetched {len(feed.entries)} entries.")
                        # Print first few entries for debugging
                        for i, entry in enumerate(feed.entries[:3]):
                            print(f"    Entry {i+1}: {entry.title if hasattr(entry, 'title') else 'No title'}")
                except Exception as e:
                    print(f"  [Error] Failed to fetch from {url}: {str(e)}")

    @classmethod
    def test_database_storage(cls):
        """Test storing RSS feeds in database."""
        print("\n=== Database Storage Test ===")
        db = SessionLocal()
        try:
            rss_sources = db.query(RSSSource).all()
            print(f"Found {len(rss_sources)} RSS sources in database")
            
            for rss_source in rss_sources:
                print(f"\nTesting storage for: {rss_source.url}")
                try:
                    # Try with proper SSL first
                    try:
                        response = requests.get(rss_source.url, verify=certifi.where(), timeout=10)
                        response.raise_for_status()
                    except Exception as ssl_error:
                        # Fall back to unverified SSL for development
                        logger.warning(f"SSL verification failed for {rss_source.url}, trying without verification: {str(ssl_error)}")
                        response = requests.get(rss_source.url, verify=False, timeout=10)
                        response.raise_for_status()
                    
                    # Parse the content with feedparser
                    feed = feedparser.parse(response.content)
                    
                    stored_count = 0
                    for entry in feed.entries:
                        published_date = datetime.now()
                        if hasattr(entry, 'published_parsed') and entry.published_parsed:
                            published_date = datetime(*entry.published_parsed[:6])
                        # Check if already exists (by link)
                        exists = db.query(RawNews).filter(RawNews.link == entry.link).first()
                        if not exists:
                            raw_news = RawNews(
                                rss_source_id=rss_source.id,
                                title=entry.title if hasattr(entry, 'title') else '',
                                description=entry.description if hasattr(entry, 'description') else '',
                                link=entry.link if hasattr(entry, 'link') else '',
                                published_date=published_date
                            )
                            db.add(raw_news)
                            stored_count += 1
                    db.commit()
                    print(f"  [Success] Stored {stored_count} new entries")
                except Exception as e:
                    logger.error(f"Error fetching news from {rss_source.url}: {str(e)}")
                    print(f"  [Error] Failed to store: {str(e)}")
        finally:
            db.close()

def run_all_tests():
    """Run all RSS feed tests."""
    RSSFeedFetcherTest.test_fetch_all()
    RSSFeedFetcherTest.test_database_storage()
    print("\n=== All tests completed ===")

if __name__ == "__main__":
    run_all_tests() 