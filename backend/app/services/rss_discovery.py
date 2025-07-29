import requests
from bs4 import BeautifulSoup
import re
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class RSSDiscoveryService:
    def __init__(self):
        self.session = requests.Session()
        # Suppress SSL warnings for development
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    def discover_business_standard_feeds(self) -> List[str]:
        """Discover RSS feeds from Business Standard RSS listing page"""
        try:
            url = "https://www.business-standard.com/rss-feeds/listing"
            response = self.session.get(url, verify=False, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            rss_links = []
            
            # Look for RSS links
            for link in soup.find_all('a', href=True):
                href = link['href']
                if '.rss' in href or 'rss' in href.lower():
                    if href.startswith('/'):
                        href = f"https://www.business-standard.com{href}"
                    elif not href.startswith('http'):
                        href = f"https://www.business-standard.com/{href}"
                    rss_links.append(href)
            
            # Remove duplicates
            rss_links = list(set(rss_links))
            logger.info(f"Discovered {len(rss_links)} RSS feeds from Business Standard")
            return rss_links
            
        except Exception as e:
            logger.error(f"Error discovering Business Standard feeds: {str(e)}")
            return []
    
    def discover_cnbc_feeds(self) -> List[str]:
        """Discover RSS feeds from CNBC-TV18"""
        try:
            url = "https://www.cnbctv18.com/rss/"
            response = self.session.get(url, verify=False, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            rss_links = []
            
            # Look for RSS links
            for link in soup.find_all('a', href=True):
                href = link['href']
                if '.rss' in href or 'rss' in href.lower():
                    if href.startswith('/'):
                        href = f"https://www.cnbctv18.com{href}"
                    elif not href.startswith('http'):
                        href = f"https://www.cnbctv18.com/{href}"
                    rss_links.append(href)
            
            rss_links = list(set(rss_links))
            logger.info(f"Discovered {len(rss_links)} RSS feeds from CNBC-TV18")
            return rss_links
            
        except Exception as e:
            logger.error(f"Error discovering CNBC feeds: {str(e)}")
            return []
    
    def discover_times_of_india_feeds(self) -> List[str]:
        """Discover RSS feeds from Times of India"""
        try:
            url = "https://timesofindia.indiatimes.com/rss.cms"
            response = self.session.get(url, verify=False, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            rss_links = []
            
            # Look for RSS links
            for link in soup.find_all('a', href=True):
                href = link['href']
                if '.rss' in href or 'rss' in href.lower():
                    if href.startswith('/'):
                        href = f"https://timesofindia.indiatimes.com{href}"
                    elif not href.startswith('http'):
                        href = f"https://timesofindia.indiatimes.com/{href}"
                    rss_links.append(href)
            
            rss_links = list(set(rss_links))
            logger.info(f"Discovered {len(rss_links)} RSS feeds from Times of India")
            return rss_links
            
        except Exception as e:
            logger.error(f"Error discovering Times of India feeds: {str(e)}")
            return []
    
    def discover_all_feeds(self) -> Dict[str, List[str]]:
        """Discover RSS feeds from all sources"""
        feeds = {
            "Business Standard": self.discover_business_standard_feeds(),
            "CNBC-TV18": self.discover_cnbc_feeds(),
            "Times of India": self.discover_times_of_india_feeds(),
        }
        
        # Add direct feeds that we know work
        feeds["Economic Times"] = [
            "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms"
        ]
        
        return feeds

# Test the discovery service
if __name__ == "__main__":
    discovery = RSSDiscoveryService()
    all_feeds = discovery.discover_all_feeds()
    
    for source, urls in all_feeds.items():
        print(f"\n{source}:")
        for url in urls:
            print(f"  {url}") 