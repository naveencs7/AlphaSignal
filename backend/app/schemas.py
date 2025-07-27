from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# Stock Price Schemas
class StockPriceBase(BaseModel):
    symbol: str = Field(..., description="Stock symbol (e.g., TATAELXSI.NS)")
    date: datetime = Field(..., description="Date of the price data")
    open_price: float = Field(..., description="Opening price")
    high_price: float = Field(..., description="Highest price of the day")
    low_price: float = Field(..., description="Lowest price of the day")
    close_price: float = Field(..., description="Closing price")
    volume: int = Field(..., description="Trading volume")

class StockPriceCreate(StockPriceBase):
    pass

class StockPrice(StockPriceBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# News Schemas
class NewsBase(BaseModel):
    title: str = Field(..., description="News headline")
    description: Optional[str] = Field(None, description="News description")
    link: str = Field(..., description="News article URL")
    published_date: datetime = Field(..., description="Publication date")
    source: str = Field(default="Moneycontrol", description="News source")
    related_stock: Optional[str] = Field(None, description="Related stock symbol")

class NewsCreate(NewsBase):
    pass

class News(NewsBase):
    id: int
    sentiment_score: Optional[float] = None
    is_processed: bool = False
    created_at: datetime
    
    class Config:
        from_attributes = True

# News Price Mapping Schemas
class NewsPriceMappingBase(BaseModel):
    news_id: int = Field(..., description="ID of the related news")
    stock_symbol: str = Field(..., description="Stock symbol")
    event_date: datetime = Field(..., description="Date of the event")
    price_before: float = Field(..., description="Price before the news")
    price_after: float = Field(..., description="Price after the news")
    price_change_percent: float = Field(..., description="Percentage change in price")
    impact_days: int = Field(default=1, description="Number of days the news affected the price")
    notes: Optional[str] = Field(None, description="Manual notes about the impact")

class NewsPriceMappingCreate(NewsPriceMappingBase):
    pass

class NewsPriceMapping(NewsPriceMappingBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Prediction Schemas
class PredictionBase(BaseModel):
    stock_symbol: str = Field(..., description="Stock symbol")
    prediction_date: datetime = Field(..., description="Date for which prediction is made")
    predicted_price: float = Field(..., description="Predicted price")
    confidence_score: Optional[float] = Field(None, description="Confidence in the prediction (0-1)")
    prediction_type: str = Field(default="daily", description="Type of prediction")
    algorithm_used: str = Field(default="simple_rule", description="Algorithm used for prediction")

class PredictionCreate(PredictionBase):
    pass

class Prediction(PredictionBase):
    id: int
    actual_price: Optional[float] = None
    accuracy: Optional[float] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# API Response Schemas
class StockPriceResponse(BaseModel):
    symbol: str
    current_price: float
    change_percent: float
    volume: int
    last_updated: datetime

class StockHistoryResponse(BaseModel):
    symbol: str
    data: List[StockPrice]
    total_records: int

class NewsResponse(BaseModel):
    news: List[News]
    total_count: int

class PredictionResponse(BaseModel):
    stock_symbol: str
    prediction: Prediction
    historical_accuracy: Optional[float] = None

# Request Schemas
class StockRequest(BaseModel):
    symbol: str = Field(..., description="Stock symbol to fetch data for")
    days: Optional[int] = Field(30, description="Number of days of historical data")

class NewsRequest(BaseModel):
    stock_symbol: Optional[str] = Field(None, description="Filter news by stock symbol")
    limit: Optional[int] = Field(5, description="Number of news items to return")
    days: Optional[int] = Field(7, description="Number of days to look back")

class PredictionRequest(BaseModel):
    stock_symbol: str = Field(..., description="Stock symbol to predict")
    days_ahead: Optional[int] = Field(1, description="Number of days to predict ahead") 