# AlphaSignal - Stock Analysis & Prediction Tool

A comprehensive stock analysis and prediction tool for Indian small-cap stocks, providing real-time market insights and price predictions with the "WHY" behind stock movements.

## Features

- **Real-time Stock Data**: Track Tata Elxsi (TATAELXSI.NS) with live price updates
- **Historical Analysis**: 30 days of price history with OHLCV data
- **Price Predictions**: Simple trend-based prediction algorithm
- **News Integration**: RSS feed integration for market news
- **Modern Dashboard**: Beautiful, responsive web interface
- **RESTful API**: Complete API with automatic documentation

## Tech Stack

- **Backend**: FastAPI (Python)
- **Database**: SQLite (MVP) / PostgreSQL (Production)
- **Frontend**: HTML/CSS/JavaScript (Vanilla)
- **Data Sources**: Yahoo Finance (yfinance), RSS feeds
- **ML**: Simple trend analysis (scikit-learn ready for Phase 2)

## Project Structure

```
mvp-phase1/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application
│   │   ├── database.py          # Database connection
│   │   ├── models.py            # SQLAlchemy models
│   │   ├── schemas.py           # Pydantic schemas
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── stock_service.py # Stock data fetching
│   │   │   └── news_service.py  # News data fetching
│   │   └── api/
│   │       ├── __init__.py
│   │       └── routes.py        # API endpoints
│   ├── requirements.txt         # Python dependencies
│   ├── test_setup.py           # Setup verification script
│   └── env.example             # Environment variables template
├── frontend/
│   └── index.html              # Dashboard interface
├── docs/
│   ├── ARCHITECTURE.md         # Detailed architecture & flow
│   ├── API_REFERENCE.md        # API documentation
│   ├── NEWS_SOURCES.md         # News sources analysis
│   └── ISSUES.md               # Known issues & limitations
└── README.md                   # This file
```

## Architectural Flow

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

## Setup Instructions

### Prerequisites

- Python 3.8+
- Web browser
- Git

### Development Setup

1. **Clone and Setup**
```bash
git clone <repository-url>
cd mvp-phase1
```

2. **Backend Setup**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Environment Configuration**
```bash
cp env.example .env
# Edit .env with your configuration
```

### Running the Application

1. **Start Backend Server**
```bash
cd backend
source venv/bin/activate
python -m uvicorn app.main:app --reload
```
- Server: http://localhost:8000
- API Docs: http://localhost:8000/docs

2. **Start Frontend**
```bash
cd frontend
python3 -m http.server 3000
```
- Dashboard: http://localhost:3000

3. **Verify Setup**
```bash
cd backend
python test_setup.py
```

### API Endpoints

- `GET /api/health` - Health check
- `GET /api/stock/price` - Current stock price
- `GET /api/stock/history` - Historical price data
- `GET /api/prediction` - Price prediction
- `GET /api/dashboard` - Complete dashboard data

## Documentation

- **[Architecture & Flow](docs/ARCHITECTURE.md)** - Detailed system architecture and data flow
- **[API Reference](docs/API_REFERENCE.md)** - Complete API documentation
- **[News Sources](docs/NEWS_SOURCES.md)** - Comprehensive news sources analysis
- **[Known Issues](docs/ISSUES.md)** - Current limitations and solutions

## Next Steps

- React frontend with interactive charts
- Advanced ML prediction algorithms
- Multiple stock support
- User authentication & portfolios
- Real-time notifications

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request 