#!/usr/bin/env node

/**
 * MongoDB Database Setup Script for EmergentTrader
 * 
 * This script initializes the MongoDB database with:
 * - Required collections
 * - Indexes for performance
 * - Sample data for testing
 * - Database schema validation
 */

const { MongoClient } = require('mongodb');
require('dotenv').config();

const MONGO_URL = process.env.MONGO_URL || 'mongodb://localhost:27017';
const DB_NAME = process.env.DB_NAME || 'emergent_trader';

console.log('🚀 EmergentTrader Database Setup');
console.log('================================');
console.log(`MongoDB URL: ${MONGO_URL}`);
console.log(`Database: ${DB_NAME}`);
console.log('');

async function setupDatabase() {
  let client;
  
  try {
    // Connect to MongoDB
    console.log('📡 Connecting to MongoDB...');
    client = new MongoClient(MONGO_URL);
    await client.connect();
    console.log('✅ Connected to MongoDB successfully');
    
    const db = client.db(DB_NAME);
    
    // 1. Create Collections
    console.log('\n📁 Creating collections...');
    
    const collections = [
      'stocks',
      'trading_signals', 
      'backtest_results',
      'performance_metrics',
      'user_preferences',
      'signal_tracking',
      'shariah_compliance'
    ];
    
    for (const collectionName of collections) {
      try {
        await db.createCollection(collectionName);
        console.log(`✅ Created collection: ${collectionName}`);
      } catch (error) {
        if (error.code === 48) {
          console.log(`ℹ️  Collection already exists: ${collectionName}`);
        } else {
          console.log(`❌ Error creating collection ${collectionName}:`, error.message);
        }
      }
    }
    
    // 2. Create Indexes for Performance
    console.log('\n🔍 Creating indexes...');
    
    // Stocks collection indexes
    await db.collection('stocks').createIndex({ symbol: 1 }, { unique: true });
    await db.collection('stocks').createIndex({ sector: 1 });
    await db.collection('stocks').createIndex({ shariah_compliant: 1 });
    await db.collection('stocks').createIndex({ market_cap: -1 });
    console.log('✅ Created indexes for stocks collection');
    
    // Trading signals indexes
    await db.collection('trading_signals').createIndex({ signal_id: 1 }, { unique: true });
    await db.collection('trading_signals').createIndex({ symbol: 1 });
    await db.collection('trading_signals').createIndex({ generated_at: -1 });
    await db.collection('trading_signals').createIndex({ strategy: 1 });
    await db.collection('trading_signals').createIndex({ status: 1 });
    await db.collection('trading_signals').createIndex({ shariah_compliant: 1 });
    console.log('✅ Created indexes for trading_signals collection');
    
    // Backtest results indexes
    await db.collection('backtest_results').createIndex({ strategy: 1 });
    await db.collection('backtest_results').createIndex({ created_at: -1 });
    await db.collection('backtest_results').createIndex({ shariah_only: 1 });
    console.log('✅ Created indexes for backtest_results collection');
    
    // Performance metrics indexes
    await db.collection('performance_metrics').createIndex({ date: -1 });
    await db.collection('performance_metrics').createIndex({ strategy: 1 });
    console.log('✅ Created indexes for performance_metrics collection');
    
    // Signal tracking indexes
    await db.collection('signal_tracking').createIndex({ signal_id: 1 });
    await db.collection('signal_tracking').createIndex({ updated_at: -1 });
    console.log('✅ Created indexes for signal_tracking collection');
    
    // 3. Insert Sample Data
    console.log('\n📊 Inserting sample data...');
    
    // Sample NSE stocks data
    const sampleStocks = [
      {
        symbol: 'RELIANCE.NS',
        name: 'Reliance Industries Limited',
        sector: 'Oil & Gas',
        market_cap: 1500000,
        current_price: 2450.50,
        shariah_compliant: false,
        last_updated: new Date(),
        created_at: new Date()
      },
      {
        symbol: 'TCS.NS',
        name: 'Tata Consultancy Services Limited',
        sector: 'Information Technology',
        market_cap: 1200000,
        current_price: 3650.75,
        shariah_compliant: false,
        last_updated: new Date(),
        created_at: new Date()
      },
      {
        symbol: 'MARUTI.NS',
        name: 'Maruti Suzuki India Limited',
        sector: 'Automobile',
        market_cap: 800000,
        current_price: 10500.25,
        shariah_compliant: true,
        last_updated: new Date(),
        created_at: new Date()
      },
      {
        symbol: 'DIVISLAB.NS',
        name: 'Divi\'s Laboratories Limited',
        sector: 'Pharmaceuticals',
        market_cap: 450000,
        current_price: 3850.00,
        shariah_compliant: true,
        last_updated: new Date(),
        created_at: new Date()
      },
      {
        symbol: 'INFY.NS',
        name: 'Infosys Limited',
        sector: 'Information Technology',
        market_cap: 750000,
        current_price: 1750.30,
        shariah_compliant: false,
        last_updated: new Date(),
        created_at: new Date()
      }
    ];
    
    // Insert stocks (update if exists)
    for (const stock of sampleStocks) {
      await db.collection('stocks').replaceOne(
        { symbol: stock.symbol },
        stock,
        { upsert: true }
      );
    }
    console.log(`✅ Inserted ${sampleStocks.length} sample stocks`);
    
    // Sample Shariah compliance data
    const shariahCompliance = [
      {
        symbol: 'MARUTI.NS',
        compliant: true,
        reason: 'Automobile manufacturing - permissible business',
        last_reviewed: new Date(),
        created_at: new Date()
      },
      {
        symbol: 'DIVISLAB.NS',
        compliant: true,
        reason: 'Pharmaceutical manufacturing - permissible business',
        last_reviewed: new Date(),
        created_at: new Date()
      },
      {
        symbol: 'RELIANCE.NS',
        compliant: false,
        reason: 'Oil & Gas with interest-based financing',
        last_reviewed: new Date(),
        created_at: new Date()
      }
    ];
    
    for (const compliance of shariahCompliance) {
      await db.collection('shariah_compliance').replaceOne(
        { symbol: compliance.symbol },
        compliance,
        { upsert: true }
      );
    }
    console.log(`✅ Inserted ${shariahCompliance.length} Shariah compliance records`);
    
    // 4. Database Statistics
    console.log('\n📈 Database Statistics:');
    const stats = await db.stats();
    console.log(`Database: ${stats.db}`);
    console.log(`Collections: ${stats.collections}`);
    console.log(`Data Size: ${(stats.dataSize / 1024 / 1024).toFixed(2)} MB`);
    console.log(`Storage Size: ${(stats.storageSize / 1024 / 1024).toFixed(2)} MB`);
    
    // 5. Collection Counts
    console.log('\n📊 Collection Document Counts:');
    for (const collectionName of collections) {
      const count = await db.collection(collectionName).countDocuments();
      console.log(`${collectionName}: ${count} documents`);
    }
    
    console.log('\n🎉 Database setup completed successfully!');
    console.log('\n📋 Next Steps:');
    console.log('1. Start your application: npm run dev');
    console.log('2. Visit: http://localhost:3000');
    console.log('3. Test API endpoints: http://localhost:3000/docs');
    console.log('4. Generate signals: POST /api/signals/generate');
    
  } catch (error) {
    console.error('❌ Database setup failed:', error);
    process.exit(1);
  } finally {
    if (client) {
      await client.close();
      console.log('\n📡 Disconnected from MongoDB');
    }
  }
}

// Run the setup
if (require.main === module) {
  setupDatabase().catch(console.error);
}

module.exports = { setupDatabase };
