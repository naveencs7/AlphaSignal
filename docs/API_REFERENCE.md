# API Reference

## Base URL
```
http://localhost:8000
```

## Authentication
Currently, the API does not require authentication for MVP purposes.

## Response Format
All API responses are in JSON format with the following structure:
```json
{
  "data": {...},
  "message": "Success",
  "status": "success"
}
```

## Error Responses
```json
{
  "detail": "Error message",
  "status_code": 400
}
```

---

## Endpoints

### Health Check

#### `GET /health`
Check if the API is running.

**Response:**
```json
{
  "status": "healthy",
  "service": "stock-analyzer-api"
}
```

#### `GET /api/health`
Alternative health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-07-27T12:00:00"
}
```

---

### Stock Data

#### `GET /api/stock/price`
Get current stock price and basic information.

**Query Parameters:**
- `symbol` (optional): Stock symbol (default: TATAELXSI.NS)

**Response:**
```json
{
  "symbol": "TATAELXSI.NS",
  "current_price": 6062.0,
  "change_percent": -2.63,
  "volume": 102770,
  "last_updated": "2025-07-27T12:47:41.521334"
}
```

**Example:**
```bash
curl http://localhost:8000/api/stock/price
```

#### `GET /api/stock/history`
Get historical stock price data.

**Query Parameters:**
- `symbol` (optional): Stock symbol (default: TATAELXSI.NS)
- `days` (optional): Number of days (default: 30)

**Response:**
```json
{
  "symbol": "TATAELXSI.NS",
  "data": [
    {
      "id": 21,
      "symbol": "TATAELXSI.NS",
      "date": "2025-07-25T00:00:00",
      "open_price": 6226.0,
      "high_price": 6257.0,
      "low_price": 6031.0,
      "close_price": 6062.0,
      "volume": 102809,
      "created_at": "2025-07-27T07:17:59",
      "updated_at": null
    }
  ],
  "total_records": 1
}
```

**Example:**
```bash
curl "http://localhost:8000/api/stock/history?days=7"
```

#### `POST /api/stock/update`
Update stock data from external source.

**Query Parameters:**
- `symbol` (optional): Stock symbol to update (default: TATAELXSI.NS)

**Response:**
```json
{
  "message": "Stock data updated successfully",
  "symbol": "TATAELXSI.NS"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/stock/update
```

---

### News Data

#### `GET /api/news`
Get latest news for a specific stock.

**Query Parameters:**
- `stock_symbol` (optional): Stock symbol (default: TATAELXSI.NS)
- `limit` (optional): Number of news items (default: 5)
- `days` (optional): Number of days to look back (default: 7)

**Response:**
```json
{
  "news": [
    {
      "id": 1,
      "title": "Tata Elxsi reports strong Q2 results",
      "description": "Company announces 15% growth in revenue...",
      "link": "https://example.com/news/1",
      "published_date": "2025-07-27T10:00:00",
      "source": "Economic Times",
      "related_stock": "TATAELXSI.NS",
      "sentiment_score": null,
      "is_processed": false,
      "created_at": "2025-07-27T12:00:00"
    }
  ],
  "total_count": 1
}
```

**Example:**
```bash
curl "http://localhost:8000/api/news?limit=3&days=3"
```

#### `GET /api/news/summary`
Get news summary for a specific stock.

**Query Parameters:**
- `stock_symbol` (optional): Stock symbol (default: TATAELXSI.NS)
- `limit` (optional): Number of news items (default: 5)

**Response:**
```json
{
  "stock_symbol": "TATAELXSI.NS",
  "total_news": 1,
  "latest_news_date": "2025-07-27T10:00:00",
  "news_items": [
    {
      "id": 1,
      "title": "Tata Elxsi reports strong Q2 results",
      "description": "Company announces 15% growth in revenue...",
      "link": "https://example.com/news/1",
      "published_date": "2025-07-27T10:00:00",
      "source": "Economic Times"
    }
  ]
}
```

**Example:**
```bash
curl "http://localhost:8000/api/news/summary?limit=5"
```

#### `POST /api/news/update`
Update news data from RSS feeds.

**Query Parameters:**
- `stock_symbol` (optional): Stock symbol (default: TATAELXSI.NS)

**Response:**
```json
{
  "message": "News data updated successfully",
  "symbol": "TATAELXSI.NS"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/news/update
```

---

### Predictions

#### `GET /api/prediction`
Get stock price prediction.

**Query Parameters:**
- `stock_symbol` (optional): Stock symbol (default: TATAELXSI.NS)
- `days_ahead` (optional): Number of days to predict (default: 1)

**Response:**
```json
{
  "stock_symbol": "TATAELXSI.NS",
  "prediction": {
    "id": 1,
    "stock_symbol": "TATAELXSI.NS",
    "prediction_date": "2025-07-28T12:48:09.057010",
    "predicted_price": 5977.54,
    "confidence_score": 0.139,
    "prediction_type": "daily",
    "algorithm_used": "simple_trend_analysis",
    "actual_price": null,
    "accuracy": null,
    "created_at": "2025-07-27T07:18:09"
  },
  "historical_accuracy": null
}
```

**Example:**
```bash
curl "http://localhost:8000/api/prediction?days_ahead=1"
```

---

### Dashboard

#### `GET /api/dashboard`
Get comprehensive dashboard data.

**Query Parameters:**
- `stock_symbol` (optional): Stock symbol (default: TATAELXSI.NS)

**Response:**
```json
{
  "stock_info": {
    "symbol": "TATAELXSI.NS",
    "name": "Tata Elxsi",
    "current_price": {
      "symbol": "TATAELXSI.NS",
      "current_price": 6062.0,
      "previous_close": 6226.0,
      "change_percent": -2.63,
      "volume": 102770,
      "market_cap": 384508428288,
      "company_name": "Tata Elxsi Limited",
      "last_updated": "2025-07-27T12:48:14.181314"
    },
    "total_records": 20
  },
  "news_summary": {
    "stock_symbol": "TATAELXSI.NS",
    "total_news": 0,
    "latest_news_date": null,
    "news_items": []
  },
  "prediction": {
    "predicted_price": 5977.54,
    "id": 1,
    "prediction_type": "daily",
    "features_used": null,
    "accuracy": null,
    "stock_symbol": "TATAELXSI.NS",
    "prediction_date": "2025-07-28T12:48:09.057010",
    "confidence_score": 0.139,
    "algorithm_used": "simple_trend_analysis",
    "actual_price": null,
    "created_at": "2025-07-27T07:18:09"
  },
  "last_updated": "2025-07-27T12:48:14.188111"
}
```

**Example:**
```bash
curl http://localhost:8000/api/dashboard
```

---

### Data Management

#### `POST /api/update-all`
Update both stock and news data.

**Response:**
```json
{
  "message": "Data update completed",
  "stock_update": "success",
  "news_update": "success",
  "timestamp": "2025-07-27T12:00:00"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/update-all
```

---

## News Aggregation Pipeline

### Discover and Store RSS Sources

#### `POST /api/news/discover-sources`
Discovers RSS feeds from aggregators and stores them in the database.

**Response:**
```json
{"status": "sources discovered"}
```
**Example:**
```bash
curl -X POST http://localhost:8000/api/news/discover-sources
```

### Fetch and Store Raw News

#### `POST /api/news/fetch-raw`
Fetches news from all stored RSS feeds and saves each item as raw news.

**Response:**
```json
{"status": "raw news fetched"}
```
**Example:**
```bash
curl -X POST http://localhost:8000/api/news/fetch-raw
```

### Deduplicate and Store Aggregated News

#### `POST /api/news/deduplicate`
Deduplicates raw news and stores the result in the aggregated news table.

**Response:**
```json
{"status": "news deduplicated"}
```
**Example:**
```bash
curl -X POST http://localhost:8000/api/news/deduplicate
```

### Get Aggregated (Deduplicated) News

#### `GET /api/news/aggregated?limit=10`
Returns the latest deduplicated news for the frontend, including sources and additional info.

**Response:**
```json
[
  {
    "title": "Tata Elxsi reports strong Q2 results",
    "description": "Company announces 15% growth in revenue...",
    "published_date": "2025-07-27T10:00:00",
    "sources": ["Economic Times", "Business Standard"],
    "additional_info": {
      "source": "Business Standard",
      "details": "Business Standard provided more in-depth analysis on the revenue split."
    }
  }
]
```
**Example:**
```bash
curl http://localhost:8000/api/news/aggregated?limit=10
```

## Error Codes

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 400 | Bad Request - Invalid parameters |
| 404 | Not Found - Resource not found |
| 500 | Internal Server Error - Server error |

## Rate Limiting
Currently, there are no rate limits implemented for the MVP.

## CORS
The API supports CORS for frontend communication from:
- `http://localhost:3000`
- `http://127.0.0.1:3000`

## API Documentation
Interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Testing the API

### Using curl
```bash
# Health check
curl http://localhost:8000/health

# Get current stock price
curl http://localhost:8000/api/stock/price

# Get historical data
curl "http://localhost:8000/api/stock/history?days=7"

# Get prediction
curl http://localhost:8000/api/prediction

# Update all data
curl -X POST http://localhost:8000/api/update-all
```

### Using Python requests
```python
import requests

# Base URL
base_url = "http://localhost:8000"

# Get dashboard data
response = requests.get(f"{base_url}/api/dashboard")
data = response.json()
print(data)

# Update stock data
response = requests.post(f"{base_url}/api/stock/update")
print(response.json())
```

### Using JavaScript fetch
```javascript
// Get dashboard data
fetch('http://localhost:8000/api/dashboard')
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(error => console.error('Error:', error));

// Update news data
fetch('http://localhost:8000/api/news/update', {
  method: 'POST'
})
  .then(response => response.json())
  .then(data => console.log(data));
``` 