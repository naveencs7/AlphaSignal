from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, Index, JSON, ForeignKey
from sqlalchemy.sql import func
from .database import Base
from sqlalchemy.orm import relationship
from datetime import datetime

class StockPrice(Base):
    """Model for storing stock price data"""
    __tablename__ = "stock_prices"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    date = Column(DateTime, nullable=False, index=True)
    open_price = Column(Float, nullable=False)
    high_price = Column(Float, nullable=False)
    low_price = Column(Float, nullable=False)
    close_price = Column(Float, nullable=False)
    volume = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Composite index for efficient querying by symbol and date
    __table_args__ = (
        Index('idx_symbol_date', 'symbol', 'date'),
    )

class News(Base):
    """Model for storing news data"""
    __tablename__ = "news"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    link = Column(String(1000), nullable=False, unique=True)
    published_date = Column(DateTime, nullable=False, index=True)
    source = Column(String(100), nullable=False, default="Moneycontrol")
    related_stock = Column(String(20), nullable=True, index=True)
    sentiment_score = Column(Float, nullable=True)  # For future sentiment analysis
    is_processed = Column(Boolean, default=False)  # For tracking if news has been analyzed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Index for efficient querying by stock and date
    __table_args__ = (
        Index('idx_stock_date', 'related_stock', 'published_date'),
    )

class NewsPriceMapping(Base):
    """Model for manually mapping news events to price movements"""
    __tablename__ = "news_price_mappings"
    
    id = Column(Integer, primary_key=True, index=True)
    news_id = Column(Integer, nullable=False, index=True)
    stock_symbol = Column(String(20), nullable=False, index=True)
    event_date = Column(DateTime, nullable=False, index=True)
    price_before = Column(Float, nullable=False)
    price_after = Column(Float, nullable=False)
    price_change_percent = Column(Float, nullable=False)
    impact_days = Column(Integer, default=1)  # How many days the news affected the price
    notes = Column(Text, nullable=True)  # Manual notes about the impact
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Foreign key relationship (for future use)
    # news = relationship("News", back_populates="price_mappings")

class Prediction(Base):
    """Model for storing price predictions"""
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    stock_symbol = Column(String(20), nullable=False, index=True)
    prediction_date = Column(DateTime, nullable=False, index=True)
    predicted_price = Column(Float, nullable=False)
    confidence_score = Column(Float, nullable=True)
    prediction_type = Column(String(50), nullable=False, default="daily")  # daily, weekly, etc.
    algorithm_used = Column(String(100), nullable=False, default="simple_rule")
    features_used = Column(Text, nullable=True)  # JSON string of features used
    actual_price = Column(Float, nullable=True)  # To be filled when actual price is available
    accuracy = Column(Float, nullable=True)  # To be calculated when actual price is available
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Index for efficient querying
    __table_args__ = (
        Index('idx_symbol_prediction_date', 'stock_symbol', 'prediction_date'),
    ) 

class RSSSource(Base):
    __tablename__ = 'rss_sources'
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(1000), unique=True, nullable=False)
    source = Column(String(100), nullable=False)  # e.g., Feedspot, GitHub List
    discovered_at = Column(DateTime, default=datetime.utcnow)
    raw_news = relationship('RawNews', back_populates='rss_source')

class RawNews(Base):
    __tablename__ = 'raw_news'
    id = Column(Integer, primary_key=True, index=True)
    rss_source_id = Column(Integer, ForeignKey('rss_sources.id'))
    title = Column(String(500), nullable=False)
    description = Column(Text)
    link = Column(String(1000), nullable=False)
    published_date = Column(DateTime, nullable=False)
    fetched_at = Column(DateTime, default=datetime.utcnow)
    rss_source = relationship('RSSSource', back_populates='raw_news')

class AggregatedNews(Base):
    __tablename__ = 'aggregated_news'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    published_date = Column(DateTime, nullable=False)
    sources = Column(JSON)  # List of sources that had this news
    additional_info = Column(JSON)  # Optional: extra info from a source
    created_at = Column(DateTime, default=datetime.utcnow) 