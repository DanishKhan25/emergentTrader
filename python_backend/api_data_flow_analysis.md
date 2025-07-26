# API Endpoint Data Source Analysis
## Complete mapping of where each endpoint gets its data

### 🔄 **SIGNAL GENERATION ENDPOINTS**

#### `POST /signals/generate`
**Data Sources:**
- **Primary**: Live market data via `YFinanceFetcher` → Yahoo Finance API
- **Universe**: Shariah compliant stocks from `SmartShariahFilter` (cached)
- **Storage**: Saves to SQLite database (`data/signals.db`)
- **Processing**: Single strategy analysis using technical indicators

**Data Flow:**
```
Yahoo Finance → YFinanceFetcher → Technical Indicators → Strategy Analysis → SQLite Database
```

#### `POST /signals/generate/multi`
**Data Sources:**
- **Primary**: Live market data via `YFinanceFetcher` → Yahoo Finance API
- **Universe**: Shariah compliant stocks from `SmartShariahFilter` (cached)
- **Storage**: Saves to SQLite database (`data/signals.db`)
- **Processing**: Multiple strategy analysis + consensus engine

**Data Flow:**
```
Yahoo Finance → YFinanceFetcher → 10 Strategies → Consensus Engine → SQLite Database
```

---

### 📊 **SIGNAL RETRIEVAL ENDPOINTS**

#### `GET /signals/active` & `GET /signals/open`
**Data Sources:**
- **Primary**: SQLite database (`data/signals.db` → `signals` table)
- **Filter**: Status = 'ACTIVE'
- **Real-time**: No live market data, pure database query

**Data Flow:**
```
SQLite Database → signals table → WHERE status='ACTIVE' → API Response
```

#### `GET /signals/today`
**Data Sources:**
- **Primary**: SQLite database (`data/signals.db` → `signals` table)
- **Filter**: Generated today + Status = 'ACTIVE'
- **Real-time**: No live market data, pure database query

**Data Flow:**
```
SQLite Database → signals table → WHERE date=today AND status='ACTIVE' → API Response
```

#### `POST /signals/track`
**Data Sources:**
- **Primary**: SQLite database (`data/signals.db` → `signal_performance` table)
- **Secondary**: Live price data for performance calculation (not fully implemented)
- **Real-time**: Partial (needs real-time price tracking)

**Data Flow:**
```
SQLite Database → signal_performance table → [Future: Live Price Data] → Performance Metrics
```

---

### 📈 **STRATEGY & PERFORMANCE ENDPOINTS**

#### `GET /strategies/available`
**Data Sources:**
- **Primary**: In-memory strategy registry (`EnhancedSignalEngine.strategies`)
- **Static**: List of 10 hardcoded strategies
- **Real-time**: No external data

**Data Flow:**
```
EnhancedSignalEngine.strategies → Strategy Names & Metadata → API Response
```

#### `GET /performance/summary`
**Data Sources:**
- **Primary**: SQLite database (`data/signals.db` → `strategy_performance` table)
- **Aggregation**: Database queries for success rates, returns
- **Real-time**: No live data, historical analysis

**Data Flow:**
```
SQLite Database → strategy_performance table → Aggregated Statistics → API Response
```

---

### 🕌 **SHARIAH COMPLIANCE ENDPOINTS**

#### `GET /stocks/shariah`
**Data Sources:**
- **Primary**: File cache (`data/cache/shariah_*.json`)
- **Fallback**: Live processing via `SmartShariahFilter`
- **External**: Yahoo Finance for fundamental data
- **Cache**: 216x speed improvement with universe-level caching

**Data Flow:**
```
Cache File → [If expired] → Yahoo Finance → Shariah Analysis → Cache Update → API Response
```

#### `POST /shariah/refresh`
**Data Sources:**
- **Primary**: Live market data via `YFinanceFetcher` → Yahoo Finance API
- **Processing**: Real-time Shariah compliance analysis
- **Storage**: Updates cache files (`data/cache/`)

**Data Flow:**
```
Yahoo Finance → Fundamental Data → Shariah Compliance Rules → Cache Update → API Response
```

#### `GET /shariah/summary`
**Data Sources:**
- **Primary**: Cached Shariah compliance data (`data/cache/`)
- **Aggregation**: Statistics from cached compliance results
- **Real-time**: No live data, cache analysis

**Data Flow:**
```
Cache Files → Compliance Statistics → Aggregated Summary → API Response
```

---

### 📊 **STOCK DATA ENDPOINTS**

#### `GET /stocks/all`
**Data Sources:**
- **Primary**: NSE stock universe from `YFinanceFetcher`
- **External**: Yahoo Finance API for stock listings
- **Processing**: Live data fetch with basic stock info

**Data Flow:**
```
Yahoo Finance → NSE Stock Universe → Stock Metadata → API Response
```

#### `POST /stocks/refresh`
**Data Sources:**
- **Primary**: Live market data via `YFinanceFetcher` → Yahoo Finance API
- **Processing**: Real-time price and technical indicator updates
- **Storage**: Updates in-memory cache

**Data Flow:**
```
Yahoo Finance → Live Stock Data → Technical Indicators → Memory Cache → API Response
```

---

### 🔙 **BACKTESTING ENDPOINTS**

#### `POST /backtest`
**Data Sources:**
- **Primary**: Historical market data via `YFinanceFetcher` → Yahoo Finance API
- **Processing**: `BacktestEngine` with historical price data
- **Time Range**: User-specified date range for historical analysis

**Data Flow:**
```
Yahoo Finance → Historical Data → BacktestEngine → Strategy Simulation → API Response
```

#### `GET /backtest/results`
**Data Sources:**
- **Primary**: In-memory backtest results from `BacktestEngine`
- **Storage**: Temporary storage of last backtest run
- **Real-time**: No live data, cached results

**Data Flow:**
```
BacktestEngine Memory → Last Results → API Response
```

---

### 🏥 **SYSTEM HEALTH ENDPOINTS**

#### `GET /health`
**Data Sources:**
- **Primary**: System component status checks
- **Database**: SQLite database connection test
- **External**: Yahoo Finance API connectivity test
- **Real-time**: Live system status

**Data Flow:**
```
System Components → Database Test → API Test → Health Status → API Response
```

---

## 🗄️ **DATA STORAGE SUMMARY**

### **Persistent Storage:**
1. **SQLite Database** (`data/signals.db`)
   - All generated signals
   - Strategy performance metrics
   - Consensus signal tracking

2. **File Cache** (`data/cache/`)
   - Shariah compliance results
   - Stock universe data
   - Technical indicator cache

3. **CSV Files** (`data/`)
   - NSE raw stock data
   - Historical data backups

### **Temporary Storage:**
1. **Memory Cache**
   - Live stock data
   - Technical indicators
   - Active signals list

2. **Session Storage**
   - Backtest results
   - API response cache

---

## 🔄 **DATA FLOW PRIORITIES**

### **Real-time Data Sources:**
1. **Yahoo Finance API** - Live market data, prices, fundamentals
2. **SQLite Database** - Signal storage and retrieval
3. **File Cache** - Shariah compliance (216x speed improvement)

### **Performance Optimizations:**
1. **Universe-level caching** - Prevents reprocessing 1,781 stocks
2. **Smart batch processing** - Handles rate limits efficiently
3. **Database indexing** - Fast signal queries by symbol/strategy/date

### **Data Consistency:**
- All signal generation endpoints save to database automatically
- Cache invalidation ensures fresh Shariah compliance data
- Database transactions ensure signal integrity

This shows that your system now has a **complete data persistence layer** with the database integration, addressing the gap identified in our conversation summary about signal storage and strategy performance tracking.
