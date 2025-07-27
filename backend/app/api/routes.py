from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from ..database import get_db
from ..services.stock_service import StockService
from ..services.news_service import NewsService
from ..schemas import (
    StockPriceResponse, StockHistoryResponse, NewsResponse, 
    PredictionResponse, StockRequest, NewsRequest, PredictionRequest
)
from ..models import StockPrice, News, Prediction, AggregatedNews, RSSSource, RawNews

router = APIRouter(prefix="/api", tags=["stock-analyzer"])

# Initialize services
stock_service = StockService()
news_service = NewsService()

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now()}

# Stock Price Routes
@router.get("/stock/price", response_model=StockPriceResponse)
async def get_current_stock_price(
    symbol: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get current stock price"""
    try:
        current_price_data = stock_service.get_current_price(symbol)
        
        if current_price_data is None:
            raise HTTPException(status_code=404, detail="Could not fetch current stock price")
        
        return StockPriceResponse(
            symbol=current_price_data['symbol'],
            current_price=current_price_data['current_price'],
            change_percent=current_price_data['change_percent'],
            volume=current_price_data['volume'],
            last_updated=current_price_data['last_updated']
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stock price: {str(e)}")

@router.get("/stock/history", response_model=StockHistoryResponse)
async def get_stock_history(
    symbol: Optional[str] = None,
    days: Optional[int] = 30,
    db: Session = Depends(get_db)
):
    """Get historical stock data"""
    try:
        stock_prices = stock_service.get_stock_history_from_db(db, symbol, days)
        
        return StockHistoryResponse(
            symbol=symbol or stock_service.default_symbol,
            data=stock_prices,
            total_records=len(stock_prices)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stock history: {str(e)}")

@router.post("/stock/update")
async def update_stock_data(
    background_tasks: BackgroundTasks,
    symbol: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Update stock data from external source"""
    try:
        success = stock_service.update_stock_data(db, symbol)
        
        if success:
            return {"message": "Stock data updated successfully", "symbol": symbol or stock_service.default_symbol}
        else:
            raise HTTPException(status_code=500, detail="Failed to update stock data")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating stock data: {str(e)}")

# News Routes
@router.get("/news", response_model=NewsResponse)
async def get_news(
    stock_symbol: Optional[str] = None,
    limit: Optional[int] = 5,
    days: Optional[int] = 7,
    db: Session = Depends(get_db)
):
    """Get news for a specific stock"""
    try:
        news_items = news_service.get_news_from_db(db, stock_symbol, limit, days)
        
        return NewsResponse(
            news=news_items,
            total_count=len(news_items)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching news: {str(e)}")

@router.get("/news/summary")
async def get_news_summary(
    stock_symbol: Optional[str] = None,
    limit: Optional[int] = 5,
    db: Session = Depends(get_db)
):
    """Get news summary for a specific stock"""
    try:
        summary = news_service.get_latest_news_summary(db, stock_symbol, limit)
        return summary
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching news summary: {str(e)}")

@router.post("/news/update")
async def update_news_data(
    background_tasks: BackgroundTasks,
    stock_symbol: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Update news data from RSS feed"""
    try:
        success = news_service.update_news_data(db, stock_symbol)
        
        if success:
            return {"message": "News data updated successfully", "symbol": stock_symbol or news_service.default_stock}
        else:
            raise HTTPException(status_code=500, detail="Failed to update news data")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating news data: {str(e)}")

@router.post("/news/discover-sources")
async def discover_rss_sources(db: Session = Depends(get_db)):
    """Discover and store RSS sources from aggregators."""
    news_service.discover_and_store_rss_sources(db)
    return {"status": "sources discovered"}

@router.post("/news/fetch-raw")
async def fetch_raw_news(db: Session = Depends(get_db)):
    """Fetch and store raw news from all RSS sources."""
    news_service.fetch_and_store_raw_news(db)
    return {"status": "raw news fetched"}

@router.post("/news/deduplicate")
async def deduplicate_news(db: Session = Depends(get_db)):
    """Deduplicate raw news and store in aggregated news table."""
    news_service.deduplicate_and_store_aggregated_news(db)
    return {"status": "news deduplicated"}

@router.get("/news/aggregated")
async def get_aggregated_news(limit: int = 10, db: Session = Depends(get_db)):
    """Get deduplicated, aggregated news for the frontend."""
    news = db.query(AggregatedNews).order_by(AggregatedNews.published_date.desc()).limit(limit).all()
    return [
        {
            "title": n.title,
            "description": n.description,
            "published_date": n.published_date,
            "sources": n.sources,
            "additional_info": n.additional_info
        }
        for n in news
    ]

# Prediction Routes
@router.get("/prediction", response_model=PredictionResponse)
async def get_prediction(
    stock_symbol: Optional[str] = None,
    days_ahead: Optional[int] = 1,
    db: Session = Depends(get_db)
):
    """Get stock price prediction"""
    try:
        # For MVP, we'll implement a simple prediction algorithm
        # This is a placeholder - you can enhance this with ML models later
        
        # Get recent stock data
        stock_prices = stock_service.get_stock_history_from_db(db, stock_symbol, 10)
        
        if not stock_prices:
            raise HTTPException(status_code=404, detail="No stock data available for prediction")
        
        # Simple prediction: if last 3 days were up, predict up; else down
        recent_prices = sorted(stock_prices, key=lambda x: x.date)[-3:]
        
        if len(recent_prices) >= 3:
            # Calculate trend
            price_changes = []
            for i in range(1, len(recent_prices)):
                change = (recent_prices[i].close_price - recent_prices[i-1].close_price) / recent_prices[i-1].close_price
                price_changes.append(change)
            
            # Simple trend analysis
            avg_change = sum(price_changes) / len(price_changes)
            current_price = recent_prices[-1].close_price
            
            # Predict next day price (simple linear extrapolation)
            predicted_price = current_price * (1 + avg_change)
            confidence_score = min(abs(avg_change) * 10, 0.8)  # Simple confidence based on trend strength
            
            # Create prediction record
            prediction = Prediction(
                stock_symbol=stock_symbol or stock_service.default_symbol,
                prediction_date=datetime.now() + timedelta(days=days_ahead),
                predicted_price=round(predicted_price, 2),
                confidence_score=round(confidence_score, 3),
                prediction_type="daily",
                algorithm_used="simple_trend_analysis"
            )
            
            db.add(prediction)
            db.commit()
            
            return PredictionResponse(
                stock_symbol=stock_symbol or stock_service.default_symbol,
                prediction=prediction,
                historical_accuracy=None  # Will be calculated when actual prices are available
            )
        else:
            raise HTTPException(status_code=400, detail="Insufficient data for prediction")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating prediction: {str(e)}")

# Dashboard Route
@router.get("/dashboard")
async def get_dashboard_data(
    stock_symbol: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get comprehensive dashboard data"""
    try:
        # Get current stock price
        current_price = stock_service.get_current_price(stock_symbol)
        
        # Get recent stock history
        stock_history = stock_service.get_stock_history_from_db(db, stock_symbol, 30)
        
        # Get latest news
        news_summary = news_service.get_latest_news_summary(db, stock_symbol, 5)
        
        # Get latest prediction
        latest_prediction = db.query(Prediction).filter(
            Prediction.stock_symbol == (stock_symbol or stock_service.default_symbol)
        ).order_by(Prediction.created_at.desc()).first()
        
        dashboard_data = {
            "stock_info": {
                "symbol": stock_symbol or stock_service.default_symbol,
                "name": stock_service.stock_name if hasattr(stock_service, 'stock_name') else "Unknown",
                "current_price": current_price,
                "total_records": len(stock_history)
            },
            "news_summary": news_summary,
            "prediction": latest_prediction,
            "last_updated": datetime.now()
        }
        
        return dashboard_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching dashboard data: {str(e)}")

# Data Update Route (for background tasks)
@router.post("/update-all")
async def update_all_data(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Update both stock and news data"""
    try:
        # Update stock data
        stock_success = stock_service.update_stock_data(db)
        
        # Update news data
        news_success = news_service.update_news_data(db)
        
        return {
            "message": "Data update completed",
            "stock_update": "success" if stock_success else "failed",
            "news_update": "success" if news_success else "failed",
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating data: {str(e)}") 