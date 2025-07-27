#!/usr/bin/env python3
"""
Test script to verify the setup and basic functionality
"""

import os
import sys
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all required packages can be imported"""
    print("Testing imports...")
    
    try:
        import fastapi
        print("✓ FastAPI imported successfully")
    except ImportError as e:
        print(f"✗ FastAPI import failed: {e}")
        return False
    
    try:
        import uvicorn
        print("✓ Uvicorn imported successfully")
    except ImportError as e:
        print(f"✗ Uvicorn import failed: {e}")
        return False
    
    try:
        import sqlalchemy
        print("✓ SQLAlchemy imported successfully")
    except ImportError as e:
        print(f"✗ SQLAlchemy import failed: {e}")
        return False
    
    try:
        import yfinance
        print("✓ yfinance imported successfully")
    except ImportError as e:
        print(f"✗ yfinance import failed: {e}")
        return False
    
    try:
        import feedparser
        print("✓ feedparser imported successfully")
    except ImportError as e:
        print(f"✗ feedparser import failed: {e}")
        return False
    
    return True

def test_app_imports():
    """Test if our app modules can be imported"""
    print("\nTesting app imports...")
    
    try:
        from app.database import engine, Base, get_db
        print("✓ Database module imported successfully")
    except ImportError as e:
        print(f"✗ Database module import failed: {e}")
        return False
    
    try:
        from app.models import StockPrice, News, Prediction
        print("✓ Models imported successfully")
    except ImportError as e:
        print(f"✗ Models import failed: {e}")
        return False
    
    try:
        from app.services.stock_service import StockService
        print("✓ Stock service imported successfully")
    except ImportError as e:
        print(f"✗ Stock service import failed: {e}")
        return False
    
    try:
        from app.services.news_service import NewsService
        print("✓ News service imported successfully")
    except ImportError as e:
        print(f"✗ News service import failed: {e}")
        return False
    
    return True

def test_database_connection():
    """Test database connection and table creation"""
    print("\nTesting database connection...")
    
    try:
        from app.database import engine, Base
        from app.models import StockPrice, News, Prediction
        
        # Create tables
        Base.metadata.create_all(bind=engine)
        print("✓ Database tables created successfully")
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(sqlalchemy.text("SELECT 1"))
            print("✓ Database connection successful")
        
        return True
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        return False

def test_stock_service():
    """Test stock service functionality"""
    print("\nTesting stock service...")
    
    try:
        from app.services.stock_service import StockService
        
        service = StockService()
        print(f"✓ Stock service initialized with symbol: {service.default_symbol}")
        
        # Test current price fetch (this might fail if no internet)
        try:
            current_price = service.get_current_price()
            if current_price:
                print(f"✓ Current price fetched: {current_price['current_price']}")
            else:
                print("⚠ Current price fetch returned None (might be network issue)")
        except Exception as e:
            print(f"⚠ Current price fetch failed (might be network issue): {e}")
        
        return True
    except Exception as e:
        print(f"✗ Stock service test failed: {e}")
        return False

def test_news_service():
    """Test news service functionality"""
    print("\nTesting news service...")
    
    try:
        from app.services.news_service import NewsService
        
        service = NewsService()
        print(f"✓ News service initialized with RSS URL: {service.rss_url}")
        
        # Test RSS fetch (this might fail if no internet)
        try:
            news_items = service.fetch_news_from_rss()
            if news_items:
                print(f"✓ RSS feed fetched {len(news_items)} items")
            else:
                print("⚠ RSS feed fetch returned None (might be network issue)")
        except Exception as e:
            print(f"⚠ RSS feed fetch failed (might be network issue): {e}")
        
        return True
    except Exception as e:
        print(f"✗ News service test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("Stock Analyzer MVP - Setup Test")
    print("=" * 50)
    print(f"Test time: {datetime.now()}")
    print()
    
    tests = [
        test_imports,
        test_app_imports,
        test_database_connection,
        test_stock_service,
        test_news_service
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your setup is ready.")
        print("\nNext steps:")
        print("1. Run: python -m uvicorn app.main:app --reload")
        print("2. Open: http://localhost:8000/docs")
        print("3. Test the API endpoints")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    print("=" * 50)

if __name__ == "__main__":
    main() 