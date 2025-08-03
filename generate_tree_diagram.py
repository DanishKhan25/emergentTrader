#!/usr/bin/env python3
"""
Generate a comprehensive tree diagram of the EmergentTrader project
"""

import os
from pathlib import Path

def generate_tree_diagram():
    """Generate a visual tree diagram of the project structure"""
    
    project_root = Path("/Users/danishkhan/Development/Clients/emergentTrader")
    
    # Directories and files to ignore
    ignore_dirs = {
        '.git', 'node_modules', '__pycache__', '.next', 'venv', '.idea', 
        'archive', '.DS_Store', 'yarn.lock', 'package-lock.json'
    }
    
    ignore_extensions = {'.pyc', '.log', '.pkl', '.joblib'}
    
    def should_ignore(path):
        """Check if path should be ignored"""
        if path.name in ignore_dirs:
            return True
        if path.suffix in ignore_extensions:
            return True
        if path.name.startswith('.') and path.name not in {'.env', '.env.example', '.gitignore'}:
            return True
        return False
    
    def get_tree_structure(directory, prefix="", max_depth=4, current_depth=0):
        """Recursively build tree structure"""
        if current_depth >= max_depth:
            return []
        
        items = []
        try:
            # Get all items in directory, sorted
            all_items = sorted([item for item in directory.iterdir() if not should_ignore(item)])
            
            # Separate directories and files
            directories = [item for item in all_items if item.is_dir()]
            files = [item for item in all_items if item.is_file()]
            
            # Limit files shown per directory
            if len(files) > 10:
                files = files[:8] + [Path("... and {} more files".format(len(files) - 8))]
            
            all_items = directories + files
            
            for i, item in enumerate(all_items):
                is_last = i == len(all_items) - 1
                current_prefix = "└── " if is_last else "├── "
                
                if "... and" in str(item):
                    items.append(f"{prefix}{current_prefix}{item}")
                elif item.is_dir() and item.exists():
                    items.append(f"{prefix}{current_prefix}{item.name}/")
                    
                    # Add subdirectory contents
                    extension = "    " if is_last else "│   "
                    sub_items = get_tree_structure(
                        item, 
                        prefix + extension, 
                        max_depth, 
                        current_depth + 1
                    )
                    items.extend(sub_items)
                else:
                    # Add file size for important files
                    size_info = ""
                    if item.exists() and item.is_file():
                        size = item.stat().st_size
                        if size > 1024 * 1024:  # > 1MB
                            size_info = f" ({size / (1024*1024):.1f}MB)"
                        elif size > 1024:  # > 1KB
                            size_info = f" ({size / 1024:.1f}KB)"
                    
                    items.append(f"{prefix}{current_prefix}{item.name}{size_info}")
                    
        except PermissionError:
            items.append(f"{prefix}└── [Permission Denied]")
        
        return items
    
    # Generate the tree
    tree_lines = [f"📁 {project_root.name}/"]
    tree_lines.extend(get_tree_structure(project_root))
    
    return "\n".join(tree_lines)

def create_enhanced_tree_diagram():
    """Create an enhanced tree diagram with annotations"""
    
    tree_content = f"""# 🌳 EmergentTrader Project Tree Diagram

## 📊 Project Structure Overview

```
{generate_tree_diagram()}
```

## 🏗️ Architecture Breakdown

### 🎨 Frontend (Next.js)
```
app/                          # Next.js 14 App Router
├── layout.js                 # Root layout with providers
├── page.js                   # Main dashboard entry point
├── globals.css               # Global styles
├── api/[[...path]]/route.js  # API proxy to Python backend
├── dashboard/page.js         # Trading dashboard
├── signals/page.js           # Signal tracking interface
├── portfolio/page.js         # Portfolio management
├── stocks/page.js            # Stock analysis
├── backtest/page.js          # Strategy backtesting
├── analytics/page.js         # Performance analytics
├── login/page.js             # Authentication
└── settings/page.js          # User settings

components/                   # React components
├── ui/                       # Radix UI components (50 files)
├── DynamicDashboard.js       # Main dashboard (25KB)
├── SignalTrackingDashboard.js # Signal monitoring
├── AIPricePrediction.js      # AI price predictions
├── WebSocketStatus.js        # Real-time status
├── auth/                     # Authentication components
├── charts/                   # Data visualization
├── portfolio/                # Portfolio components
└── notifications/            # Alert system

contexts/                     # React Context providers
├── AuthContext.js            # Authentication state
├── WebSocketContext.js       # Real-time connections
└── DataContext.js            # Global data state
```

### 🐍 Backend (Python FastAPI)
```
python_backend/               # Python FastAPI backend
├── main.py                   # FastAPI application entry (34KB)
├── api_handler.py            # Main API logic (101KB)
├── database.py               # Database operations
├── requirements.txt          # Python dependencies
│
├── core/                     # Core trading engines
│   ├── enhanced_signal_engine.py      # Main signal generation
│   ├── ml_enhanced_signal_engine.py   # ML-enhanced signals
│   ├── backtest_engine.py             # Strategy backtesting
│   ├── consensus_engine.py            # Signal consensus
│   ├── signal_database.py             # Data persistence
│   ├── shariah_filter.py              # Shariah compliance
│   ├── batch_processor.py             # Batch operations
│   └── strategies/                    # Trading strategies (10 files)
│       ├── multibagger_strategy.py    # High-growth stocks
│       ├── momentum_strategy.py       # Momentum signals
│       ├── breakout_strategy.py       # Breakout patterns
│       ├── swing_trading_strategy.py  # Swing trading
│       ├── value_investing_strategy.py # Value screening
│       └── [5 more strategies]
│
├── ml/                       # Machine Learning components
│   ├── improved_ml_inference_engine.py # ML inference
│   ├── ml_strategy_enhancer.py        # Strategy enhancement
│   ├── price_prediction_model.py      # Price predictions
│   └── signal_confidence_scorer.py    # Confidence scoring
│
├── services/                 # External services
│   ├── yfinance_fetcher.py   # Market data fetching
│   ├── market_data_service.py # Data aggregation
│   ├── notification_service.py # Alerts
│   └── portfolio_service.py  # Portfolio management
│
├── models/                   # ML model storage
│   └── [Various .pkl files]
│
└── data/                     # Data and cache
    ├── cache/                # Cache files (7,456 .pkl files)
    └── signals.db            # Signal database
```

### 📊 Data & Training
```
data/                         # Core data files
├── nse_raw.csv              # Primary NSE stock data (274KB)
└── [Other data files]

data_collection/              # Data collection scripts (455MB)
├── step1_comprehensive_data_collector.py
├── step1_corrected_data_collector.py
├── cleanup_after_training.py
└── [Various CSV files and collectors]

training_steps/               # ML training pipeline
├── step1_data_collection.py
├── step2_train_on_2014_2019.py
├── step3_generate_2019_signals.py
├── step4_validate_multibaggers.py
└── trained_models_2019/     # Historical models
    ├── RandomForest_multibagger_2019.pkl (12.4MB)
    ├── GradientBoosting_multibagger_2019.pkl
    └── [Other model files]

models/                       # Current production models
└── signal_quality_demo.pkl  # Demo model (10.5MB)
```

### 🧪 Testing & Validation
```
tests/                        # Test suite
├── test_api_fixes.py
├── test_python_api.py
├── test_trading_strategies.py
├── test_all_strategies.py
├── test_core_functionality.py
└── test_fixed_endpoints.py

validation_results/           # Validation outputs
├── [Various validation files]
└── [Test results]
```

### ⚙️ Configuration & Scripts
```
Configuration Files:
├── package.json             # Node.js dependencies
├── next.config.js           # Next.js configuration
├── tailwind.config.js       # Tailwind CSS config
├── jsconfig.json            # JavaScript config
├── .env                     # Environment variables
├── .env.example             # Environment template
└── .gitignore               # Git ignore rules

Setup & Deployment Scripts:
├── start_app.sh             # Application startup
├── start_production.sh      # Production deployment
├── setup_auth.sh            # Authentication setup
├── backup_to_oracle_storage.sh # Backup script
├── train_oracle_cloud.sh   # Cloud training
└── [Various other scripts]

Cleanup & Analysis Tools:
├── execute_targeted_cleanup.sh     # Main cleanup script
├── project_file_usage_analyzer.py  # Usage analyzer
├── comprehensive_cleanup.py        # Cleanup tool
└── [Analysis and cleanup tools]
```

### 📚 Documentation
```
Documentation Files:
├── PROJECT_ANALYSIS_SUMMARY.md           # Executive summary
├── COMPREHENSIVE_PROJECT_DOCUMENTATION.md # Complete overview
├── CLEANUP_IMPLEMENTATION_GUIDE.md       # Cleanup guide
├── PROJECT_DEPENDENCY_MAP.md             # Dependencies
├── TARGETED_CLEANUP_STRATEGY.md          # Cleanup strategy
├── ML_TRAINING_GUIDE.md                  # ML training guide
├── SECURITY_ENV_SETUP.md                 # Security setup
├── PRODUCTION_DEPLOYMENT_GUIDE.md        # Deployment guide
└── [Various other documentation files]
```

## 🎯 Key File Relationships

### Critical Path Files
1. **Frontend Entry**: `app/layout.js` → `app/page.js` → `components/DynamicDashboard.js`
2. **Backend Entry**: `python_backend/main.py` → `api_handler.py` → `core/enhanced_signal_engine.py`
3. **Data Flow**: `data/nse_raw.csv` → `services/yfinance_fetcher.py` → `core/strategies/*`
4. **ML Pipeline**: `training_steps/*` → `models/*.pkl` → `ml/improved_ml_inference_engine.py`

### Most Referenced Files
- `data/nse_raw.csv` - Used by 6 different scripts
- `python_backend/api_handler.py` - Imported by 12 test files
- `nse_shariah_compliance_results.json` - Used by 8 compliance scripts

## 📊 Storage Distribution
- **Total Size**: ~2.2 GB
- **File Count**: 11,409 files
- **Largest Components**:
  - `.joblib` files: 622 MB (28%)
  - CSV data: 457 MB (21%)
  - Node modules: 199 MB (9%)
  - JavaScript: 155 MB (7%)
  - Python cache: 44 MB (2%)

## 🧹 Cleanup Opportunities
- **High Impact**: Archive .joblib files (622 MB savings)
- **Medium Impact**: Clean old CSV files (400+ MB savings)
- **Low Impact**: Clean cache files (44 MB, many files)
- **Total Potential**: ~1.2 GB savings (54% reduction)

This tree diagram shows a well-structured full-stack trading platform with clear separation of concerns and significant optimization opportunities.
"""
    
    return tree_content

def main():
    """Generate and save the tree diagram"""
    print("Generating comprehensive tree diagram...")
    
    tree_content = create_enhanced_tree_diagram()
    
    # Save to file
    output_file = Path("/Users/danishkhan/Development/Clients/emergentTrader/PROJECT_TREE_DIAGRAM.md")
    with open(output_file, 'w') as f:
        f.write(tree_content)
    
    print(f"Tree diagram saved to: {output_file}")
    print("\nTree diagram preview:")
    print("=" * 60)
    
    # Show a preview of the actual tree structure
    tree_structure = generate_tree_diagram()
    lines = tree_structure.split('\n')
    for line in lines[:30]:  # Show first 30 lines
        print(line)
    
    if len(lines) > 30:
        print(f"... and {len(lines) - 30} more lines")
    
    print("=" * 60)
    print(f"Complete tree diagram with annotations saved to PROJECT_TREE_DIAGRAM.md")

if __name__ == "__main__":
    main()
