# EmergentTrader API Documentation

## 📚 Overview

The EmergentTrader API is a comprehensive REST API for AI-powered trading signal generation with Shariah compliance filtering. This API provides endpoints for stock data management, trading signal generation, backtesting, and performance analytics.

## 🚀 Quick Start

### Access the Interactive Documentation

Visit the interactive Swagger UI documentation at:
- **Local Development**: [http://localhost:3000/docs](http://localhost:3000/docs)
- **API Spec JSON**: [http://localhost:3000/api/docs/swagger.json](http://localhost:3000/api/docs/swagger.json)

### Base URL
```
http://localhost:3000/api
```

### Response Format
All API responses follow a consistent JSON structure:

```json
{
  "success": true,
  "data": {
    // Response data here
  },
  "error": null,
  "timestamp": "2025-07-26T13:00:00Z"
}
```

## 📋 API Endpoints

### 🔍 API Status
- `GET /` - Get API status and version information

### 📈 Stock Data Management
- `GET /stocks/all` - Retrieve all NSE stocks (53 stocks)
- `POST /stocks/refresh` - Refresh stock data for specified symbols
- `GET /stocks/shariah` - Get Shariah-compliant stocks only

### 🎯 Trading Signals
- `POST /signals/generate` - Generate new trading signals using AI strategies
- `POST /signals/track` - Track performance of specific signals
- `GET /signals/today` - Get all signals generated today
- `GET /signals/open` - Get all currently active signals

### 📊 Backtesting & Analytics
- `POST /backtest` - Run strategy backtests with historical data
- `GET /performance/summary` - Get overall performance metrics

## 🔧 Key Features

### ✅ **Shariah Compliance**
- Automatic filtering of Shariah-compliant stocks
- Currently supports 2 compliant stocks: MARUTI, DIVISLAB
- All endpoints support `shariah_only` parameter

### 🤖 **AI-Powered Strategies**
- **Momentum Strategy**: Identifies trending stocks with strong momentum
- **Mean Reversion**: Detects oversold/overbought conditions
- **Breakout Strategy**: Identifies price breakout patterns

### 📊 **Comprehensive Analytics**
- Real-time performance tracking
- Detailed backtesting with multiple metrics
- Risk-adjusted returns (Sharpe ratio, max drawdown)
- Win rate and trade statistics

### 🔒 **Robust Error Handling**
- Consistent error response format
- Detailed error messages and codes
- Graceful handling of edge cases

## 📝 Example Usage

### Generate Trading Signals
```bash
curl -X POST http://localhost:3000/api/signals/generate \
  -H "Content-Type: application/json" \
  -d '{
    "strategy": "momentum",
    "shariah_only": true,
    "min_confidence": 0.6
  }'
```

### Get Shariah-Compliant Stocks
```bash
curl http://localhost:3000/api/stocks/shariah
```

### Run Backtest
```bash
curl -X POST http://localhost:3000/api/backtest \
  -H "Content-Type: application/json" \
  -d '{
    "strategy": "momentum",
    "start_date": "2020-01-01",
    "end_date": "2024-12-31",
    "shariah_only": true
  }'
```

## 🏗️ Data Models

### Stock Object
```json
{
  "symbol": "RELIANCE.NS",
  "name": "Reliance Industries Limited",
  "sector": "Oil & Gas",
  "market_cap": 1500000,
  "current_price": 2450.50,
  "shariah_compliant": true,
  "last_updated": "2025-07-26T13:00:00Z"
}
```

### Trading Signal Object
```json
{
  "signal_id": "123e4567-e89b-12d3-a456-426614174000",
  "symbol": "RELIANCE.NS",
  "signal_type": "BUY",
  "strategy": "momentum",
  "confidence": 0.85,
  "entry_price": 2450.50,
  "target_price": 2650.00,
  "stop_loss": 2300.00,
  "generated_at": "2025-07-26T13:00:00Z",
  "status": "ACTIVE",
  "shariah_compliant": true
}
```

## 🔧 Configuration

### Environment Variables
```bash
# Database
MONGO_URL=mongodb://localhost:27017
DB_NAME=emergent_trader

# Trading Configuration
RISK_FREE_RATE=0.06
MAX_POSITION_SIZE=0.05
SECTOR_LIMIT=0.3
CORRELATION_THRESHOLD=0.7

# ML Configuration
ML_MODEL_RETRAIN_DAYS=30
SIGNAL_CONFIDENCE_THRESHOLD=0.6
```

## 🧪 Testing

### API Testing Scripts
- `test_python_api.py` - Comprehensive API endpoint testing
- `test_api_fixes.py` - Validation of recent fixes and improvements

### Run Tests
```bash
# Test all endpoints
python3 test_python_api.py

# Test specific fixes
python3 test_api_fixes.py
```

## 📊 Current Status

### ✅ **Working Features**
- All 9 API endpoints functional
- 53 NSE stocks in database
- 2 Shariah-compliant stocks identified
- Momentum strategy generating BUY/SELL signals
- UUID-based signal tracking
- Comprehensive error handling

### 🔄 **Recent Improvements**
- Fixed missing `/stocks/refresh` endpoint
- Resolved signal tracking "Invalid BulkOperation" error
- Added unique signal ID generation
- Enhanced error handling and validation
- Created comprehensive API documentation

## 🚀 Getting Started

1. **Start the application**:
   ```bash
   npm run dev
   ```

2. **Access the API documentation**:
   - Open [http://localhost:3000/docs](http://localhost:3000/docs)
   - Try out endpoints directly in the browser

3. **Test the API**:
   ```bash
   # Quick API status check
   curl http://localhost:3000/api/
   
   # Generate signals
   curl -X POST http://localhost:3000/api/signals/generate \
     -H "Content-Type: application/json" \
     -d '{"strategy": "momentum"}'
   ```

## 📞 Support

For API support, issues, or feature requests:
- Check the interactive documentation at `/docs`
- Review the test scripts for usage examples
- Refer to `APP_STATUS.md` for current system status
- Check `FIXES_SUMMARY.md` for recent improvements

---

**🎉 EmergentTrader API - Powering AI-driven Shariah-compliant trading decisions!**
