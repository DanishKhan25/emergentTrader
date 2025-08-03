# EmergentTrader - File Dependency Map

## Core Application Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Next.js)                       │
├─────────────────────────────────────────────────────────────────┤
│ app/layout.js (Root Layout)                                     │
│ ├── contexts/AuthContext.js                                     │
│ ├── contexts/WebSocketContext.js                                │
│ ├── contexts/DataContext.js                                     │
│ └── components/notifications/NotificationProvider.js            │
│                                                                 │
│ app/page.js (Main Dashboard)                                    │
│ ├── components/DynamicDashboard.js                              │
│ └── components/auth/ProtectedRoute.js                           │
│                                                                 │
│ Key Pages:                                                      │
│ ├── app/signals/page.js → components/SignalTrackingDashboard.js │
│ ├── app/portfolio/page.js → components/portfolio/*              │
│ ├── app/stocks/page.js → components/DynamicStocksPage.js        │
│ └── app/login/page.js → components/auth/LoginPage.js            │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    │ HTTP/WebSocket
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                    API PROXY LAYER                              │
├─────────────────────────────────────────────────────────────────┤
│ app/api/[[...path]]/route.js                                   │
│ └── Forwards requests to Python backend                        │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    │ FastAPI
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PYTHON BACKEND                               │
├─────────────────────────────────────────────────────────────────┤
│ python_backend/main.py (FastAPI App)                           │
│ ├── api_handler.py (Main API Logic)                            │
│ ├── ai_prediction_endpoints.py                                 │
│ └── ai_enhanced_endpoints.py                                   │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CORE ENGINES                                 │
├─────────────────────────────────────────────────────────────────┤
│ python_backend/core/enhanced_signal_engine.py                  │
│ ├── ml_enhanced_signal_engine.py                               │
│ ├── consensus_engine.py                                        │
│ ├── backtest_engine.py                                         │
│ └── signal_database.py                                         │
└─────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│   STRATEGIES    │ │   ML MODELS     │ │   DATA LAYER    │
├─────────────────┤ ├─────────────────┤ ├─────────────────┤
│ multibagger_    │ │ improved_ml_    │ │ data/nse_raw.   │
│ strategy.py     │ │ inference_      │ │ csv             │
│                 │ │ engine.py       │ │                 │
│ momentum_       │ │                 │ │ nse_shariah_    │
│ strategy.py     │ │ ml_strategy_    │ │ compliance_     │
│                 │ │ enhancer.py     │ │ results.json    │
│ breakout_       │ │                 │ │                 │
│ strategy.py     │ │ price_          │ │ emergent_       │
│                 │ │ prediction_     │ │ trader.db       │
│ [8 more         │ │ model.py        │ │                 │
│ strategies]     │ │                 │ │ yfinance_       │
│                 │ │ [7,468 .pkl     │ │ fetcher.py      │
│                 │ │ model files]    │ │                 │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

## File Usage Categories

### 🟢 Core Active Files (47 files - 0.4%)
These files are actively imported/referenced and form the application backbone:

#### Frontend Core (8 files)
- `app/layout.js` - Root application layout
- `app/page.js` - Main dashboard entry point
- `components/DynamicDashboard.js` - Primary dashboard component
- `components/SignalTrackingDashboard.js` - Signal monitoring
- `components/auth/LoginPage.js` - Authentication interface
- `contexts/AuthContext.js` - Authentication state
- `contexts/WebSocketContext.js` - Real-time connections
- `app/api/[[...path]]/route.js` - API proxy

#### Backend Core (12 files)
- `python_backend/main.py` - FastAPI application
- `python_backend/api_handler.py` - Main API logic
- `python_backend/core/enhanced_signal_engine.py` - Signal generation
- `python_backend/core/ml_enhanced_signal_engine.py` - ML integration
- `python_backend/core/backtest_engine.py` - Strategy testing
- `python_backend/core/consensus_engine.py` - Signal consensus
- `python_backend/core/signal_database.py` - Data persistence
- `python_backend/core/shariah_filter.py` - Compliance filtering
- `python_backend/core/batch_processor.py` - Batch operations
- `python_backend/services/yfinance_fetcher.py` - Market data
- `python_backend/ml/improved_ml_inference_engine.py` - ML inference
- `python_backend/database.py` - Database operations

#### Configuration (6 files)
- `package.json` - Node.js dependencies
- `next.config.js` - Next.js configuration
- `tailwind.config.js` - Styling configuration
- `jsconfig.json` - JavaScript project settings
- `.env` - Environment variables
- `python_backend/requirements.txt` - Python dependencies

#### Data Files (5 files)
- `data/nse_raw.csv` - Primary stock data
- `nse_shariah_compliance_results.json` - Compliance cache
- `failed_downloads.txt` - Error tracking
- `python_backend/emergent_trader.db` - Main database
- `emergent_trader.db` - Frontend database

### 🟡 Dynamically Loaded Files (7,741 files - 67.8%)
These files are loaded at runtime but not directly imported:

#### ML Model Files (7,468 files)
- `.pkl` files containing trained machine learning models
- Loaded dynamically by the ML inference engine
- Stored in `models/` and `trained_models_2019/` directories

#### CSV Data Files (273 files)
- Historical stock data and training datasets
- Loaded by data processing scripts
- Used for backtesting and model training

### 🔴 Potentially Unused Files (3,621 files - 31.8%)
These files may be candidates for cleanup:

#### Documentation (46 .md files)
- Project documentation and guides
- Status reports and analysis documents
- Many could be consolidated or archived

#### Log Files (10 files)
- Application logs and debug output
- Can be cleaned up regularly

#### Test Artifacts (19 .txt files)
- Test results and temporary outputs
- Should be cleaned after testing

#### Build Artifacts
- Generated files from build processes
- Cache files and temporary data

## Dependency Relationships

### High-Level Dependencies
```
Frontend (Next.js)
    ↓
API Proxy Layer
    ↓
Python Backend (FastAPI)
    ↓
Core Engines
    ↓
┌─────────────┬─────────────┬─────────────┐
│ Strategies  │ ML Models   │ Data Layer  │
└─────────────┴─────────────┴─────────────┘
```

### Critical Path Files
1. **`python_backend/main.py`** - Application entry point
2. **`python_backend/api_handler.py`** - API orchestration
3. **`python_backend/core/enhanced_signal_engine.py`** - Core logic
4. **`data/nse_raw.csv`** - Primary data source
5. **`app/layout.js`** - Frontend foundation

### Most Referenced Files
1. **`data/nse_raw.csv`** - Used by 6 different scripts
2. **`failed_downloads.txt`** - Referenced by 7 data collection scripts
3. **`nse_shariah_compliance_results.json`** - Used by 8 compliance scripts
4. **`python_backend/api_handler.py`** - Imported by 12 test files

## Optimization Recommendations

### Immediate Cleanup (Safe to remove/archive)
- Old log files (`.log` files older than 30 days)
- Temporary test output files (`.txt` files in root)
- Duplicate documentation files
- Unused CSV files (not referenced in last 90 days)

### Code Organization
- Create index files for better module imports
- Consolidate similar utility functions
- Standardize file naming conventions
- Add dependency documentation headers

### Performance Improvements
- Implement lazy loading for ML models
- Cache frequently accessed data files
- Optimize database queries with indexing
- Reduce frontend bundle size

This dependency map shows the actual usage patterns and helps identify optimization opportunities while maintaining system functionality.
