# 🗄️ MongoDB Database Setup - EmergentTrader

## 📋 Overview

EmergentTrader uses MongoDB as its primary database for storing trading signals, stock data, backtest results, and performance metrics. This guide covers the complete database setup, schema, and usage.

## 🔧 Database Configuration

### Environment Variables
```bash
# .env file
MONGO_URL=mongodb://localhost:27017
DB_NAME=emergent_trader
```

### Connection Details
- **Host**: localhost
- **Port**: 27017 (default MongoDB port)
- **Database**: emergent_trader
- **Connection Type**: Direct connection (no authentication in development)

## 🏗️ Database Schema

### Collections Overview

| Collection | Purpose | Documents | Indexes |
|------------|---------|-----------|---------|
| `stocks` | NSE stock data and metadata | ~53 | symbol, sector, shariah_compliant |
| `trading_signals` | Generated trading signals | Dynamic | signal_id, symbol, generated_at |
| `backtest_results` | Strategy backtest results | Dynamic | strategy, created_at |
| `performance_metrics` | Performance analytics | Dynamic | date, strategy |
| `signal_tracking` | Signal performance tracking | Dynamic | signal_id, updated_at |
| `shariah_compliance` | Shariah compliance data | ~53 | symbol, compliant |
| `user_preferences` | User settings (future) | Dynamic | user_id |

### 📊 Collection Schemas

#### 1. **stocks** Collection
```javascript
{
  _id: ObjectId,
  symbol: "RELIANCE.NS",           // Unique stock symbol
  name: "Reliance Industries Ltd", // Company name
  sector: "Oil & Gas",             // Industry sector
  market_cap: 1500000,             // Market cap in crores
  current_price: 2450.50,          // Current stock price
  shariah_compliant: false,        // Shariah compliance status
  last_updated: ISODate,           // Last price update
  created_at: ISODate              // Record creation time
}
```

#### 2. **trading_signals** Collection
```javascript
{
  _id: ObjectId,
  signal_id: "uuid-string",        // Unique signal identifier
  symbol: "MARUTI.NS",             // Stock symbol
  signal_type: "BUY",              // BUY, SELL, HOLD
  strategy: "momentum",            // Strategy used
  confidence: 0.85,                // Confidence score (0-1)
  entry_price: 10500.25,           // Recommended entry price
  target_price: 11200.00,          // Target price
  stop_loss: 9800.00,              // Stop loss price
  generated_at: ISODate,           // Signal generation time
  status: "ACTIVE",                // ACTIVE, EXECUTED, EXPIRED
  shariah_compliant: true,         // Shariah compliance
  created_at: ISODate,             // Record creation
  updated_at: ISODate              // Last update
}
```

#### 3. **backtest_results** Collection
```javascript
{
  _id: ObjectId,
  id: "uuid-string",               // Unique backtest ID
  strategy: "momentum",            // Strategy name
  start_date: "2020-01-01",        // Backtest start date
  end_date: "2024-12-31",          // Backtest end date
  shariah_only: true,              // Shariah-only backtest
  performance_metrics: {
    total_return: 0.4567,          // Total return percentage
    annualized_return: 0.1234,     // Annualized return
    sharpe_ratio: 1.25,            // Risk-adjusted return
    max_drawdown: -0.1567,         // Maximum drawdown
    win_rate: 0.655,               // Win rate percentage
    total_trades: 150              // Total number of trades
  },
  created_at: ISODate,             // Backtest run time
  parameters: {                    // Strategy parameters
    lookback_period: 20,
    threshold: 0.02
  }
}
```

#### 4. **signal_tracking** Collection
```javascript
{
  _id: ObjectId,
  signal_id: "uuid-string",        // Reference to trading signal
  symbol: "MARUTI.NS",             // Stock symbol
  entry_price: 10500.25,           // Actual entry price
  current_price: 10750.50,         // Current market price
  current_return: 0.0238,          // Current return percentage
  max_return: 0.0456,              // Maximum return achieved
  min_return: -0.0123,             // Minimum return (drawdown)
  status: "ACTIVE",                // Tracking status
  last_updated: ISODate,           // Last price update
  created_at: ISODate              // Tracking start time
}
```

#### 5. **shariah_compliance** Collection
```javascript
{
  _id: ObjectId,
  symbol: "MARUTI.NS",             // Stock symbol
  compliant: true,                 // Compliance status
  reason: "Automobile manufacturing - permissible business",
  debt_ratio: 0.15,                // Debt to market cap ratio
  interest_income_ratio: 0.02,     // Interest income ratio
  last_reviewed: ISODate,          // Last compliance review
  created_at: ISODate              // Record creation
}
```

## 🚀 Database Setup

### 1. **Prerequisites**
```bash
# Install MongoDB (macOS)
brew tap mongodb/brew
brew install mongodb-community

# Start MongoDB service
brew services start mongodb-community

# Verify MongoDB is running
brew services list | grep mongodb
```

### 2. **Automated Setup**
```bash
# Run the database setup script
node scripts/setup-database.js
```

### 3. **Manual Setup**
```bash
# Connect to MongoDB
mongosh

# Create database and collections
use emergent_trader

# Create collections
db.createCollection("stocks")
db.createCollection("trading_signals")
db.createCollection("backtest_results")
db.createCollection("performance_metrics")
db.createCollection("signal_tracking")
db.createCollection("shariah_compliance")
```

### 4. **Create Indexes**
```javascript
// Stocks collection indexes
db.stocks.createIndex({ symbol: 1 }, { unique: true })
db.stocks.createIndex({ sector: 1 })
db.stocks.createIndex({ shariah_compliant: 1 })
db.stocks.createIndex({ market_cap: -1 })

// Trading signals indexes
db.trading_signals.createIndex({ signal_id: 1 }, { unique: true })
db.trading_signals.createIndex({ symbol: 1 })
db.trading_signals.createIndex({ generated_at: -1 })
db.trading_signals.createIndex({ strategy: 1 })
db.trading_signals.createIndex({ status: 1 })

// Backtest results indexes
db.backtest_results.createIndex({ strategy: 1 })
db.backtest_results.createIndex({ created_at: -1 })

// Signal tracking indexes
db.signal_tracking.createIndex({ signal_id: 1 })
db.signal_tracking.createIndex({ updated_at: -1 })
```

## 💻 Database Usage in Code

### Next.js API Routes (`app/api/[[...path]]/route.js`)

```javascript
import { MongoClient } from 'mongodb'

// Connection setup
let client
let db

async function connectToMongo() {
  if (!client) {
    client = new MongoClient(process.env.MONGO_URL)
    await client.connect()
    db = client.db(process.env.DB_NAME)
  }
  return db
}

// Usage examples
const db = await connectToMongo()

// Store trading signals
const signalsCollection = db.collection('trading_signals')
await signalsCollection.insertMany(signals)

// Store backtest results
const backtestCollection = db.collection('backtest_results')
await backtestCollection.insertOne(backtestResult)

// Get collection counts
const signalsCount = await db.collection('trading_signals').countDocuments()
```

### Python Backend Integration

Currently, the Python backend doesn't directly connect to MongoDB. Instead, it:
1. Generates signals and returns JSON data
2. Next.js API routes receive the data
3. Next.js stores the data in MongoDB

**Future Enhancement**: Direct MongoDB connection in Python backend using PyMongo.

## 📊 Current Database State

### Collections Status
- ✅ **stocks**: Ready for NSE stock data
- ✅ **trading_signals**: Stores generated signals with UUID tracking
- ✅ **backtest_results**: Stores strategy backtest results
- ⏳ **performance_metrics**: Ready for implementation
- ⏳ **signal_tracking**: Ready for signal performance tracking
- ⏳ **shariah_compliance**: Ready for compliance data

### Sample Data
The setup script includes sample data:
- 5 NSE stocks (RELIANCE, TCS, MARUTI, DIVISLAB, INFY)
- 2 Shariah-compliant stocks (MARUTI, DIVISLAB)
- Shariah compliance reasons and metadata

## 🔍 Database Monitoring

### Check Database Status
```bash
# Connect to MongoDB
mongosh emergent_trader

# Show collections
show collections

# Count documents in each collection
db.stocks.countDocuments()
db.trading_signals.countDocuments()
db.backtest_results.countDocuments()

# View recent signals
db.trading_signals.find().sort({generated_at: -1}).limit(5)

# Check Shariah-compliant stocks
db.stocks.find({shariah_compliant: true})
```

### Database Statistics
```javascript
// Get database stats
db.stats()

// Get collection stats
db.trading_signals.stats()

// Check indexes
db.trading_signals.getIndexes()
```

## 🛠️ Maintenance Tasks

### Regular Maintenance
```bash
# Backup database
mongodump --db emergent_trader --out backup/

# Restore database
mongorestore --db emergent_trader backup/emergent_trader/

# Compact database
db.runCommand({compact: "trading_signals"})

# Rebuild indexes
db.trading_signals.reIndex()
```

### Data Cleanup
```javascript
// Remove old signals (older than 30 days)
db.trading_signals.deleteMany({
  generated_at: {
    $lt: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000)
  }
})

// Remove expired signals
db.trading_signals.deleteMany({status: "EXPIRED"})
```

## 🚨 Troubleshooting

### Common Issues

1. **Connection Failed**
   ```bash
   # Check if MongoDB is running
   brew services list | grep mongodb
   
   # Start MongoDB if not running
   brew services start mongodb-community
   ```

2. **Database Not Found**
   ```bash
   # The database is created automatically when first document is inserted
   # Run the setup script to initialize
   node scripts/setup-database.js
   ```

3. **Collection Not Found**
   ```javascript
   // Collections are created automatically or via setup script
   db.createCollection("collection_name")
   ```

4. **Index Errors**
   ```javascript
   // Drop and recreate indexes if needed
   db.collection.dropIndexes()
   db.collection.createIndex({field: 1})
   ```

## 📈 Performance Optimization

### Index Strategy
- **Primary Keys**: Unique indexes on `symbol`, `signal_id`
- **Query Optimization**: Indexes on frequently queried fields
- **Sorting**: Indexes on `generated_at`, `created_at` for time-based queries
- **Filtering**: Indexes on `status`, `strategy`, `shariah_compliant`

### Query Optimization
```javascript
// Efficient queries with proper indexes
db.trading_signals.find({
  strategy: "momentum",
  status: "ACTIVE",
  shariah_compliant: true
}).sort({generated_at: -1}).limit(10)

// Use projection to limit returned fields
db.stocks.find(
  {shariah_compliant: true},
  {symbol: 1, name: 1, current_price: 1}
)
```

## 🔮 Future Enhancements

### Planned Features
1. **User Management**: User accounts and preferences
2. **Portfolio Tracking**: User portfolio and positions
3. **Real-time Updates**: WebSocket integration for live data
4. **Advanced Analytics**: Time-series data and aggregations
5. **Audit Logging**: Track all database changes
6. **Data Archiving**: Archive old signals and results

### Scaling Considerations
1. **Sharding**: Horizontal scaling for large datasets
2. **Replication**: Master-slave setup for high availability
3. **Caching**: Redis integration for frequently accessed data
4. **Connection Pooling**: Optimize database connections

---

**🎯 Your MongoDB database is now ready for EmergentTrader's AI-powered trading signals!**
