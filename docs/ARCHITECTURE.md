# Architecture & Data Flow

## System Overview

The Stock Analyzer MVP follows a **3-tier architecture** with clear separation of concerns:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Data Sources  │
│   (HTML/JS)     │◄──►│   (FastAPI)     │◄──►│                 │
│                 │    │                 │    │                 │
│ • Dashboard     │    │ • API Routes    │    │ • Yahoo Finance │
│ • Real-time     │    │ • Services      │    │ • RSS Feeds     │
│ • Auto-refresh  │    │ • Database      │    │ • News APIs     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Database      │
                       │   (SQLite)      │
                       │                 │
                       │ • Stock Prices  │
                       │ • News Data     │
                       │ • Predictions   │
                       └─────────────────┘
```

## Component Responsibilities

### **1. Frontend Layer (frontend/index.html)**

**Purpose**: User interface for the stock analyzer

**Responsibilities**:
- Display current stock price, predictions, and news
- Make API calls to backend every 5 minutes
- Provide refresh button for manual updates
- Show color-coded price changes (green/red)
- Handle loading states and error messages

**Key Features**:
- Responsive design for mobile and desktop
- Real-time data updates
- Auto-refresh functionality
- Error handling and user feedback

### **2. Backend API Layer (backend/app/main.py)**

**Purpose**: FastAPI application entry point

**Responsibilities**:
- Create FastAPI app with CORS enabled
- Set up database tables automatically
- Include all API routes
- Handle global exceptions
- Configure middleware and dependencies

**Key Features**:
- Automatic API documentation (Swagger UI)
- CORS configuration for frontend communication
- Global exception handling
- Database initialization

### **3. Database Layer (backend/app/database.py)**

**Purpose**: Database connection and session management

**Responsibilities**:
- Create SQLAlchemy engine for SQLite
- Provide database session dependency
- Manage connection lifecycle
- Handle database transactions

**Key Features**:
- SQLite database for MVP (easily upgradable to PostgreSQL)
- Connection pooling
- Session management
- Transaction handling

### **4. Data Models (backend/app/models.py)**

**Purpose**: Database table definitions

**Responsibilities**:
- Define database schema
- Establish relationships between tables
- Set up indexes for performance
- Handle data validation

**Models**:
- `StockPrice`: Stores daily OHLCV data
- `News`: Stores news articles and metadata
- `Prediction`: Stores price predictions and accuracy
- `NewsPriceMapping`: Links news events to price movements

### **5. API Schemas (backend/app/schemas.py)**

**Purpose**: Request/response validation

**Responsibilities**:
- Define Pydantic models for API input/output
- Ensure data validation and type safety
- Provide automatic API documentation
- Handle data serialization/deserialization

**Key Features**:
- Input validation
- Response formatting
- Type hints for better IDE support
- Automatic OpenAPI documentation

### **6. Stock Service (backend/app/services/stock_service.py)**

**Purpose**: Stock data fetching and processing

**Responsibilities**:
- Fetch real-time data from Yahoo Finance using `yfinance`
- Store historical data in database
- Provide current price and company info
- Handle data updates and retrieval

**Key Features**:
- Real-time stock data fetching
- Historical data management
- Data validation and cleaning
- Error handling for API failures

### **7. News Service (backend/app/services/news_service.py)**

**Purpose**: News data fetching and filtering

**Responsibilities**:
- Fetch RSS feeds from news sources
- Filter news relevant to Tata Elxsi
- Store news in database
- Provide news summaries

**Key Features**:
- RSS feed parsing
- Content filtering
- Duplicate detection
- Source management

### **8. API Routes (backend/app/api/routes.py)**

**Purpose**: HTTP endpoints for frontend

**Responsibilities**:
- Define REST API endpoints
- Handle HTTP requests and responses
- Implement business logic
- Manage error responses

**Endpoints**:
- `GET /api/stock/price`: Current stock price
- `GET /api/stock/history`: Historical data
- `GET /api/prediction`: Price predictions
- `GET /api/news`: Latest news
- `GET /api/dashboard`: Complete dashboard data

### **9. Prediction Algorithm (in routes.py)**

**Purpose**: Simple price prediction

**Responsibilities**:
- Analyze price trends
- Calculate predictions
- Provide confidence scores
- Store prediction results

**Algorithm**:
- Analyzes last 3 days of price trends
- Calculates average price change
- Predicts next day price using linear extrapolation
- Provides confidence score based on trend strength

## Complete Data Flow

### **1. User Interaction Flow**

```
User opens dashboard
    ↓
Frontend loads (index.html)
    ↓
JavaScript makes API call to /api/dashboard
    ↓
Backend processes request
    ↓
Services fetch data from external sources
    ↓
Data stored in database
    ↓
Response sent to frontend
    ↓
Frontend displays data
```

### **2. Stock Data Flow**

```
Frontend requests stock data
    ↓
API route calls stock service
    ↓
Stock service fetches from Yahoo Finance
    ↓
Data validated and cleaned
    ↓
Stored in StockPrice table
    ↓
Returned to frontend
```

### **3. News Data Flow**

```
Frontend requests news data
    ↓
API route calls news service
    ↓
News service fetches RSS feeds
    ↓
Content filtered for Tata Elxsi
    ↓
Stored in News table
    ↓
Returned to frontend
```

### **4. Prediction Flow**

```
Frontend requests prediction
    ↓
API route gets historical data
    ↓
Prediction algorithm analyzes trends
    ↓
Prediction calculated and stored
    ↓
Result returned to frontend
```

## Database Schema

### **StockPrice Table**
```sql
CREATE TABLE stock_prices (
    id INTEGER PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    date DATETIME NOT NULL,
    open_price FLOAT NOT NULL,
    high_price FLOAT NOT NULL,
    low_price FLOAT NOT NULL,
    close_price FLOAT NOT NULL,
    volume INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME
);
```

### **News Table**
```sql
CREATE TABLE news (
    id INTEGER PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    link VARCHAR(1000) NOT NULL UNIQUE,
    published_date DATETIME NOT NULL,
    source VARCHAR(100) DEFAULT 'Moneycontrol',
    related_stock VARCHAR(20),
    sentiment_score FLOAT,
    is_processed BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### **Prediction Table**
```sql
CREATE TABLE predictions (
    id INTEGER PRIMARY KEY,
    stock_symbol VARCHAR(20) NOT NULL,
    prediction_date DATETIME NOT NULL,
    predicted_price FLOAT NOT NULL,
    confidence_score FLOAT,
    prediction_type VARCHAR(50) DEFAULT 'daily',
    algorithm_used VARCHAR(100) DEFAULT 'simple_rule',
    features_used TEXT,
    actual_price FLOAT,
    accuracy FLOAT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## Performance Considerations

### **Database Optimization**
- Indexes on frequently queried columns
- Composite indexes for complex queries
- Connection pooling for better performance

### **API Optimization**
- Caching for frequently accessed data
- Pagination for large datasets
- Async operations for external API calls

### **Frontend Optimization**
- Debounced API calls
- Local storage for caching
- Progressive loading for better UX

## Security Considerations

### **API Security**
- Input validation on all endpoints
- Rate limiting for API calls
- CORS configuration for frontend access

### **Data Security**
- SQL injection prevention through ORM
- Data validation and sanitization
- Secure environment variable handling

## Scalability Considerations

### **Current MVP Limitations**
- Single stock tracking
- Simple prediction algorithm
- Basic error handling
- SQLite database

### **Production Readiness**
- PostgreSQL database
- Multiple stock support
- Advanced ML algorithms
- Background job processing
- Monitoring and logging
- Docker containerization 