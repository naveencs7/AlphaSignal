# Known Issues & Limitations

**Note:** Technical issues are now tracked in technical_issues.md. This file is for business/product issues only.

## Current Issues

### **1. Price Accuracy Issues**

#### **Problem**
- **Current Price**: ₹6,062.00 (Yahoo Finance)
- **Google Finance**: ₹6,041.00
- **Difference**: ₹21.00 (0.35% variance)

#### **Root Causes**
1. **Data Source Lag**: Yahoo Finance may have 15-20 minute delay
2. **Market Hours**: Prices change continuously during trading hours
3. **Cache Issues**: Data might be cached from previous fetch
4. **Source Differences**: Different platforms show slightly different prices

#### **Solutions**
1. **Multiple Data Sources**: Implement validation against multiple sources
2. **Real-time Updates**: Add more frequent data fetching during market hours
3. **Source Comparison**: Compare prices from multiple sources
4. **Cache Management**: Implement proper cache invalidation

#### **Implementation**
```python
# Add multiple data source validation
def validate_price_accuracy():
    sources = [
        "yahoo_finance",
        "google_finance", 
        "nse_india"
    ]
    
    prices = {}
    for source in sources:
        prices[source] = get_price_from_source(source)
    
    # Calculate average and flag discrepancies
    return prices
```

---

### **2. News Integration Issues**

#### **Problem**
- Moneycontrol RSS feed is currently not accessible
- News update endpoint is failing
- No news data available in dashboard

#### **Root Causes**
1. **RSS Feed Blocked**: Moneycontrol RSS feed is blocked or changed
2. **Error Handling**: Insufficient error handling for failed RSS requests
3. **Single Source**: Only one news source implemented

#### **Solutions**
1. **Alternative Sources**: Implement Economic Times and Business Standard RSS
2. **Error Handling**: Add proper error handling and fallback mechanisms
3. **Multiple Sources**: Aggregate news from multiple sources

#### **Implementation**
```python
# Update news_service.py with multiple sources
NEWS_SOURCES = [
    "https://economictimes.indiatimes.com/rss.cms",
    "https://www.business-standard.com/rss/",
    "https://www.ndtv.com/business/market/rss"
]

def fetch_news_with_fallback():
    for source in NEWS_SOURCES:
        try:
            news = fetch_from_source(source)
            if news:
                return news
        except Exception as e:
            logger.warning(f"Failed to fetch from {source}: {e}")
            continue
    return []
```

---

### **3. Prediction Algorithm Limitations**

#### **Problem**
- Simple trend-based algorithm
- Low confidence scores (13.9%)
- Limited accuracy for complex market conditions

#### **Root Causes**
1. **Basic Algorithm**: Only uses 3-day trend analysis
2. **Limited Features**: No technical indicators or market sentiment
3. **No ML**: No machine learning models implemented

#### **Solutions**
1. **Enhanced Algorithm**: Add technical indicators (MA, RSI, MACD)
2. **ML Models**: Implement scikit-learn models
3. **Feature Engineering**: Add more relevant features

#### **Implementation**
```python
# Enhanced prediction algorithm
def enhanced_prediction(stock_data):
    features = {
        'sma_5': calculate_sma(stock_data, 5),
        'sma_20': calculate_sma(stock_data, 20),
        'rsi': calculate_rsi(stock_data),
        'volume_ma': calculate_volume_ma(stock_data),
        'price_momentum': calculate_momentum(stock_data)
    }
    
    # Use ML model for prediction
    prediction = ml_model.predict(features)
    return prediction
```

---

## Scalability Issues

### **1. Single Stock Limitation**

#### **Problem**
- Only tracks Tata Elxsi
- No support for multiple stocks
- Hardcoded stock symbol

#### **Solutions**
1. **Multi-stock Support**: Add support for multiple stocks
2. **Dynamic Configuration**: Make stock selection configurable
3. **Portfolio Management**: Add portfolio features

### **2. Single User Limitation**

#### **Problem**
- No user authentication
- No personalized dashboards
- No user preferences

#### **Solutions**
1. **User Authentication**: Add user registration/login
2. **Personalization**: Add user preferences
3. **Multi-tenancy**: Support multiple users

---

## Monitoring & Observability

### **1. Limited Monitoring**

#### **Problem**
- No application monitoring
- No performance metrics
- No error tracking

#### **Solutions**
1. **Application Monitoring**: Add monitoring tools
2. **Performance Metrics**: Track key performance indicators
3. **Error Tracking**: Implement error tracking and alerting

### **2. No Health Checks**

#### **Problem**
- Basic health check endpoint
- No dependency health checks
- No automated testing

#### **Solutions**
1. **Comprehensive Health Checks**: Add dependency health checks
2. **Automated Testing**: Implement unit and integration tests
3. **CI/CD Pipeline**: Add continuous integration

---

## Roadmap for Resolution

### **Phase 1: Critical Fixes (Immediate)**
1. **Fix News Integration**: Implement Economic Times RSS
2. **Price Validation**: Add multiple data source validation
3. **Error Handling**: Improve error handling and logging

### **Phase 2: Performance Improvements (Next Sprint)**
1. **Caching**: Implement Redis caching
2. **Async Operations**: Add async support
3. **Database Optimization**: Optimize queries and add indexes

### **Phase 3: Advanced Features (Future)**
1. **ML Models**: Implement advanced prediction algorithms
2. **Multi-stock Support**: Add support for multiple stocks
3. **User Authentication**: Add user management

### **Phase 4: Production Ready (Long-term)**
1. **PostgreSQL Migration**: Switch to production database
2. **Background Jobs**: Add Celery for scheduled tasks
3. **Monitoring**: Add comprehensive monitoring and alerting

---

## Workarounds

### **For Price Accuracy**
- Use multiple data sources for validation
- Implement price discrepancy alerts
- Add timestamp information for data freshness

### **For News Issues**
- Implement fallback news sources
- Add manual news entry capability
- Use web scraping as backup

### **For Prediction Accuracy**
- Add confidence score thresholds
- Implement ensemble methods
- Add disclaimer about prediction accuracy

---

## Testing Strategy

### **Unit Tests**
- Test individual components
- Mock external dependencies
- Validate data processing logic

### **Integration Tests**
- Test API endpoints
- Validate database operations
- Test external service integration

### **End-to-End Tests**
- Test complete user workflows
- Validate frontend-backend integration
- Test error scenarios 