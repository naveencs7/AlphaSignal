import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import logging
from sqlalchemy.orm import Session
from ..models import StockPrice
from ..schemas import StockPriceCreate
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StockService:
    def __init__(self):
        self.default_symbol = os.getenv("STOCK_SYMBOL", "TATAELXSI.NS")
        self.historical_days = int(os.getenv("HISTORICAL_DAYS", "30"))
    
    def fetch_stock_data(self, symbol: str = None, days: int = None) -> Optional[pd.DataFrame]:
        """
        Fetch stock data from Yahoo Finance
        """
        if symbol is None:
            symbol = self.default_symbol
        
        if days is None:
            days = self.historical_days
        
        try:
            logger.info(f"Fetching stock data for {symbol} for the last {days} days")
            
            # Calculate start date
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Fetch data from Yahoo Finance
            ticker = yf.Ticker(symbol)
            data = ticker.history(start=start_date, end=end_date)
            
            if data.empty:
                logger.warning(f"No data found for {symbol}")
                return None
            
            # Reset index to make date a column
            data = data.reset_index()
            
            # Rename columns to match our schema
            data = data.rename(columns={
                'Date': 'date',
                'Open': 'open_price',
                'High': 'high_price',
                'Low': 'low_price',
                'Close': 'close_price',
                'Volume': 'volume'
            })
            
            # Add symbol column
            data['symbol'] = symbol
            
            # Convert date to datetime if it's not already
            data['date'] = pd.to_datetime(data['date'])
            
            logger.info(f"Successfully fetched {len(data)} records for {symbol}")
            return data
            
        except Exception as e:
            logger.error(f"Error fetching stock data for {symbol}: {str(e)}")
            return None
    
    def get_current_price(self, symbol: str = None) -> Optional[Dict[str, Any]]:
        """
        Get current stock price and basic info
        """
        if symbol is None:
            symbol = self.default_symbol
        
        try:
            logger.info(f"Fetching current price for {symbol}")
            
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Get current price
            current_price = info.get('currentPrice', info.get('regularMarketPrice'))
            
            if current_price is None:
                logger.warning(f"Could not get current price for {symbol}")
                return None
            
            # Get previous close for calculating change
            previous_close = info.get('previousClose', current_price)
            change_percent = ((current_price - previous_close) / previous_close) * 100
            
            result = {
                'symbol': symbol,
                'current_price': current_price,
                'previous_close': previous_close,
                'change_percent': round(change_percent, 2),
                'volume': info.get('volume', 0),
                'market_cap': info.get('marketCap'),
                'company_name': info.get('longName', symbol),
                'last_updated': datetime.now()
            }
            
            logger.info(f"Current price for {symbol}: {current_price}")
            return result
            
        except Exception as e:
            logger.error(f"Error fetching current price for {symbol}: {str(e)}")
            return None
    
    def save_stock_data_to_db(self, db: Session, stock_data: pd.DataFrame) -> bool:
        """
        Save stock data to database
        """
        try:
            logger.info(f"Saving {len(stock_data)} stock records to database")
            
            for _, row in stock_data.iterrows():
                # Check if record already exists
                existing_record = db.query(StockPrice).filter(
                    StockPrice.symbol == row['symbol'],
                    StockPrice.date == row['date']
                ).first()
                
                if existing_record:
                    # Update existing record
                    existing_record.open_price = row['open_price']
                    existing_record.high_price = row['high_price']
                    existing_record.low_price = row['low_price']
                    existing_record.close_price = row['close_price']
                    existing_record.volume = row['volume']
                else:
                    # Create new record
                    stock_price = StockPrice(
                        symbol=row['symbol'],
                        date=row['date'],
                        open_price=row['open_price'],
                        high_price=row['high_price'],
                        low_price=row['low_price'],
                        close_price=row['close_price'],
                        volume=row['volume']
                    )
                    db.add(stock_price)
            
            db.commit()
            logger.info("Successfully saved stock data to database")
            return True
            
        except Exception as e:
            logger.error(f"Error saving stock data to database: {str(e)}")
            db.rollback()
            return False
    
    def get_stock_history_from_db(self, db: Session, symbol: str = None, days: int = None) -> List[StockPrice]:
        """
        Get stock history from database
        """
        if symbol is None:
            symbol = self.default_symbol
        
        if days is None:
            days = self.historical_days
        
        try:
            # Calculate start date
            start_date = datetime.now() - timedelta(days=days)
            
            # Query database
            stock_prices = db.query(StockPrice).filter(
                StockPrice.symbol == symbol,
                StockPrice.date >= start_date
            ).order_by(StockPrice.date.desc()).all()
            
            logger.info(f"Retrieved {len(stock_prices)} stock records from database for {symbol}")
            return stock_prices
            
        except Exception as e:
            logger.error(f"Error retrieving stock history from database: {str(e)}")
            return []
    
    def update_stock_data(self, db: Session, symbol: str = None) -> bool:
        """
        Update stock data by fetching latest data and saving to database
        """
        if symbol is None:
            symbol = self.default_symbol
        
        try:
            # Fetch latest data
            stock_data = self.fetch_stock_data(symbol, self.historical_days)
            
            if stock_data is None:
                return False
            
            # Save to database
            return self.save_stock_data_to_db(db, stock_data)
            
        except Exception as e:
            logger.error(f"Error updating stock data for {symbol}: {str(e)}")
            return False 