import feedparser
import requests
import ssl
import certifi
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import logging
from sqlalchemy.orm import Session
from ..models import News, RSSSource, RawNews, AggregatedNews
import os
import re
import difflib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsService:
    def __init__(self):
        # List of curated RSS feeds (discovered from various sources)
        self.rss_sources = [
            # Direct from publisher (working)
            {"name": "Economic Times Markets", "url": "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms"},
            
            # CNBC-TV18 feeds (discovered)
            {"name": "CNBC-TV18 Latest", "url": "https://www.cnbctv18.com/commonfeeds/v1/cne/rss/latest.xml"},
            {"name": "CNBC-TV18 Business", "url": "https://www.cnbctv18.com/commonfeeds/v1/cne/rss/business.xml"},
            {"name": "CNBC-TV18 Economy", "url": "https://www.cnbctv18.com/commonfeeds/v1/cne/rss/economy.xml"},
            {"name": "CNBC-TV18 Market", "url": "https://www.cnbctv18.com/commonfeeds/v1/cne/rss/market.xml"},
            
            # Times of India feeds (discovered)
            {"name": "Times of India Top Stories", "url": "http://timesofindia.indiatimes.com/rssfeedstopstories.cms"},
            {"name": "Times of India Most Recent", "url": "http://timesofindia.indiatimes.com/rssfeedmostrecent.cms"},
            {"name": "Times of India Business", "url": "http://timesofindia.indiatimes.com/rssfeeds/3942666.cms"},
        ]
        self.default_stock = os.getenv("STOCK_SYMBOL", "TATAELXSI.NS")
        self.stock_name = os.getenv("STOCK_NAME", "Tata Elxsi")
    
    def fetch_news_from_all_sources(self) -> (List[Dict[str, Any]], List[Dict[str, Any]]):
        """
        Fetch news from all RSS sources, track health status, and deduplicate news.
        Returns (deduped_news, sources_status)
        """
        all_news = []
        sources_status = []
        seen = {}
        
        for source in self.rss_sources:
            url = source["url"]
            name = source["name"]
            try:
                # Try with proper SSL first
                try:
                    response = requests.get(url, verify=certifi.where(), timeout=10)
                    response.raise_for_status()
                    logger.info(f"Successfully fetched {name} with SSL verification")
                except Exception as ssl_error:
                    # Fall back to unverified SSL for development
                    logger.warning(f"SSL verification failed for {name}, trying without verification: {str(ssl_error)}")
                    response = requests.get(url, verify=False, timeout=10)
                    response.raise_for_status()
                    logger.info(f"Successfully fetched {name} without SSL verification")
                
                # Parse the content with feedparser
                feed = feedparser.parse(response.content)
                
                if not feed.entries:
                    sources_status.append({"name": name, "url": url, "status": "failed"})
                    continue
                sources_status.append({"name": name, "url": url, "status": "ok"})
                for entry in feed.entries:
                    # Parse publication date
                    published_date = datetime.now()
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        published_date = datetime(*entry.published_parsed[:6])
                    # Deduplication key: title + date (ignore case/punct)
                    title_key = re.sub(r'[^a-zA-Z0-9 ]', '', entry.title.lower()) if hasattr(entry, 'title') else ''
                    date_key = published_date.strftime('%Y-%m-%d')
                    dedup_key = f"{title_key}_{date_key}"
                    # Prepare news item
                    news_item = {
                        'title': entry.title if hasattr(entry, 'title') else '',
                        'description': entry.description if hasattr(entry, 'description') else '',
                        'link': entry.link if hasattr(entry, 'link') else '',
                        'published_date': published_date,
                        'source': name
                    }
                    # Deduplication logic
                    if dedup_key in seen:
                        # Merge sources and extra info
                        seen[dedup_key]['sources'].append(name)
                        # If this source has more info, add to additional_info
                        if len(entry.description if hasattr(entry, 'description') else '') > len(seen[dedup_key]['description']):
                            seen[dedup_key]['additional_info'] = {
                                'source': name,
                                'details': entry.description
                            }
                    else:
                        seen[dedup_key] = {
                            'title': news_item['title'],
                            'description': news_item['description'],
                            'link': news_item['link'],
                            'published_date': news_item['published_date'],
                            'sources': [name],
                            'additional_info': None
                        }
            except Exception as e:
                sources_status.append({"name": name, "url": url, "status": f"failed: {str(e)}"})
                continue
        # Prepare deduped news list
        deduped_news = []
        for item in seen.values():
            deduped_news.append(item)
        return deduped_news, sources_status
    
    def filter_news_by_stock(self, news_items: List[Dict[str, Any]], stock_symbol: str = None, stock_name: str = None) -> List[Dict[str, Any]]:
        """
        Filter news items that are related to the specified stock
        """
        if stock_symbol is None:
            stock_symbol = self.default_stock
        
        if stock_name is None:
            stock_name = self.stock_name
        
        try:
            logger.info(f"Filtering news for stock: {stock_name} ({stock_symbol})")
            
            # Create search keywords
            keywords = [
                stock_name.lower(),
                stock_symbol.lower().replace('.ns', '').replace('.bo', ''),
                'tata elxsi',
                'elxsi'
            ]
            
            # Remove common suffixes for broader matching
            base_symbol = stock_symbol.split('.')[0].lower()
            keywords.append(base_symbol)
            
            filtered_news = []
            
            for news_item in news_items:
                title = news_item.get('title', '').lower()
                description = news_item.get('description', '').lower()
                
                # Check if any keyword is present in title or description
                is_related = any(keyword in title or keyword in description for keyword in keywords)
                
                if is_related:
                    news_item['related_stock'] = stock_symbol
                    filtered_news.append(news_item)
                    logger.info(f"Found related news: {news_item.get('title', '')[:50]}...")
            
            logger.info(f"Filtered {len(filtered_news)} news items related to {stock_name}")
            return filtered_news
            
        except Exception as e:
            logger.error(f"Error filtering news: {str(e)}")
            return []
    
    def save_news_to_db(self, db: Session, news_items: List[Dict[str, Any]]) -> bool:
        """
        Save news items to database
        """
        try:
            logger.info(f"Saving {len(news_items)} news items to database")
            
            saved_count = 0
            
            for news_item in news_items:
                # Check if news already exists (by link)
                existing_news = db.query(News).filter(
                    News.link == news_item['link']
                ).first()
                
                if existing_news:
                    logger.debug(f"News already exists: {news_item.get('title', '')[:30]}...")
                    continue
                
                # Create new news record
                news = News(
                    title=news_item['title'],
                    description=news_item.get('description', ''),
                    link=news_item['link'],
                    published_date=news_item['published_date'],
                    source=news_item['source'],
                    related_stock=news_item.get('related_stock')
                )
                
                db.add(news)
                saved_count += 1
            
            db.commit()
            logger.info(f"Successfully saved {saved_count} new news items to database")
            return True
            
        except Exception as e:
            logger.error(f"Error saving news to database: {str(e)}")
            db.rollback()
            return False
    
    def get_news_from_db(self, db: Session, stock_symbol: str = None, limit: int = 5, days: int = 7) -> List[News]:
        """
        Get news from database
        """
        if stock_symbol is None:
            stock_symbol = self.default_stock
        
        try:
            # Calculate start date
            start_date = datetime.now() - timedelta(days=days)
            
            # Query database
            news_items = db.query(News).filter(
                News.related_stock == stock_symbol,
                News.published_date >= start_date
            ).order_by(News.published_date.desc()).limit(limit).all()
            
            logger.info(f"Retrieved {len(news_items)} news items from database for {stock_symbol}")
            return news_items
            
        except Exception as e:
            logger.error(f"Error retrieving news from database: {str(e)}")
            return []
    
    def update_news_data(self, db: Session, stock_symbol: str = None) -> bool:
        """
        Update news data by fetching from RSS and saving to database
        """
        if stock_symbol is None:
            stock_symbol = self.default_stock
        
        try:
            # Fetch news from RSS
            news_items = self.fetch_news_from_rss()
            
            if news_items is None:
                return False
            
            # Filter news for the specific stock
            filtered_news = self.filter_news_by_stock(news_items, stock_symbol)
            
            if not filtered_news:
                logger.info("No relevant news found for the stock")
                return True  # Not an error, just no relevant news
            
            # Save to database
            return self.save_news_to_db(db, filtered_news)
            
        except Exception as e:
            logger.error(f"Error updating news data for {stock_symbol}: {str(e)}")
            return False
    
    def get_latest_news_summary(self, db: Session, stock_symbol: str = None, limit: int = 5) -> Dict[str, Any]:
        """
        Get a summary of latest news for the stock
        """
        if stock_symbol is None:
            stock_symbol = self.default_stock
        
        try:
            news_items = self.get_news_from_db(db, stock_symbol, limit)
            
            summary = {
                'stock_symbol': stock_symbol,
                'total_news': len(news_items),
                'latest_news_date': None,
                'news_items': []
            }
            
            if news_items:
                summary['latest_news_date'] = news_items[0].published_date
                
                for news in news_items:
                    summary['news_items'].append({
                        'id': news.id,
                        'title': news.title,
                        'description': news.description,
                        'link': news.link,
                        'published_date': news.published_date,
                        'source': news.source
                    })
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting news summary: {str(e)}")
            return {
                'stock_symbol': stock_symbol,
                'total_news': 0,
                'latest_news_date': None,
                'news_items': []
            } 

    def discover_and_store_rss_sources(self, db: Session):
        """
        Discover RSS feeds from aggregator sites and store them in rss_sources table.
        For now, this is a placeholder for scraping/parsing logic. Add direct and curated links.
        """
        aggregator_sources = [
            ("Feedspot", [
                "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
                "https://www.business-standard.com/rss-feeds/listing",
            ]),
            ("GitHub List", [
                "https://www.cnbctv18.com/rss/",
                "https://www.nseindia.com/rss-feed",
            ]),
            ("Direct", [
                "https://timesofindia.indiatimes.com/rss.cms"
            ]),
        ]
        for source, urls in aggregator_sources:
            for url in urls:
                existing = db.query(RSSSource).filter(RSSSource.url == url).first()
                if not existing:
                    rss_source = RSSSource(url=url, source=source)
                    db.add(rss_source)
        db.commit()

    def deduplicate_and_store_aggregated_news(self, db: Session):
        """
        Deduplicate raw news and store in aggregated_news table (rule-based: title+date+fuzzy).
        """
        raw_news = db.query(RawNews).all()
        seen = []
        for news in raw_news:
            # Try to find a similar news in seen (title+date+fuzzy)
            found = None
            for agg in seen:
                # Fuzzy match on title
                ratio = difflib.SequenceMatcher(None, news.title.lower(), agg['title'].lower()).ratio()
                same_date = news.published_date.date() == agg['published_date'].date()
                if ratio > 0.85 and same_date:
                    found = agg
                    break
            if found:
                found['sources'].append(news.rss_source.source)
                # If this news has more info, update additional_info
                if len(news.description or '') > len(found['description'] or ''):
                    found['additional_info'] = {
                        'source': news.rss_source.source,
                        'details': news.description
                    }
            else:
                seen.append({
                    'title': news.title,
                    'description': news.description,
                    'published_date': news.published_date,
                    'sources': [news.rss_source.source],
                    'additional_info': None
                })
        # Store in aggregated_news table
        for agg in seen:
            exists = db.query(AggregatedNews).filter(
                AggregatedNews.title == agg['title'],
                AggregatedNews.published_date == agg['published_date']
            ).first()
            if not exists:
                aggregated = AggregatedNews(
                    title=agg['title'],
                    description=agg['description'],
                    published_date=agg['published_date'],
                    sources=agg['sources'],
                    additional_info=agg['additional_info']
                )
                db.add(aggregated)
        db.commit() 

    def fetch_and_store_raw_news(self, db: Session):
        """
        Fetch news from all RSS sources in DB, store raw news in raw_news table.
        """
        rss_sources = db.query(RSSSource).all()
        for rss_source in rss_sources:
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
                db.commit()
            except Exception as e:
                logger.error(f"Error fetching news from {rss_source.url}: {str(e)}") 