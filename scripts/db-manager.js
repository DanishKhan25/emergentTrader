#!/usr/bin/env node

/**
 * Database Management Utility for EmergentTrader
 * 
 * Usage:
 *   node scripts/db-manager.js status
 *   node scripts/db-manager.js reset
 *   node scripts/db-manager.js backup
 *   node scripts/db-manager.js cleanup
 */

const { MongoClient } = require('mongodb');
const fs = require('fs');
const path = require('path');
require('dotenv').config();

const MONGO_URL = process.env.MONGO_URL || 'mongodb://localhost:27017';
const DB_NAME = process.env.DB_NAME || 'emergent_trader';

class DatabaseManager {
  constructor() {
    this.client = null;
    this.db = null;
  }

  async connect() {
    if (!this.client) {
      this.client = new MongoClient(MONGO_URL);
      await this.client.connect();
      this.db = this.client.db(DB_NAME);
    }
    return this.db;
  }

  async disconnect() {
    if (this.client) {
      await this.client.close();
      this.client = null;
      this.db = null;
    }
  }

  async getStatus() {
    console.log('📊 EmergentTrader Database Status');
    console.log('=================================');
    
    try {
      await this.connect();
      
      // Database stats
      const stats = await this.db.stats();
      console.log(`\n🗄️  Database: ${stats.db}`);
      console.log(`📁 Collections: ${stats.collections}`);
      console.log(`💾 Data Size: ${(stats.dataSize / 1024 / 1024).toFixed(2)} MB`);
      console.log(`🗃️  Storage Size: ${(stats.storageSize / 1024 / 1024).toFixed(2)} MB`);
      console.log(`📄 Documents: ${stats.objects}`);
      
      // Collection counts
      console.log('\n📋 Collection Document Counts:');
      const collections = await this.db.listCollections().toArray();
      
      for (const collection of collections) {
        const count = await this.db.collection(collection.name).countDocuments();
        console.log(`  ${collection.name}: ${count} documents`);
      }
      
      // Recent activity
      console.log('\n🕒 Recent Activity:');
      
      // Recent signals
      const recentSignals = await this.db.collection('trading_signals')
        .find({})
        .sort({ generated_at: -1 })
        .limit(3)
        .toArray();
      
      if (recentSignals.length > 0) {
        console.log('  📈 Recent Signals:');
        recentSignals.forEach(signal => {
          console.log(`    ${signal.symbol} - ${signal.signal_type} (${signal.strategy})`);
        });
      } else {
        console.log('  📈 No signals generated yet');
      }
      
      // Recent backtests
      const recentBacktests = await this.db.collection('backtest_results')
        .find({})
        .sort({ created_at: -1 })
        .limit(3)
        .toArray();
      
      if (recentBacktests.length > 0) {
        console.log('  🧪 Recent Backtests:');
        recentBacktests.forEach(backtest => {
          const returnPct = (backtest.performance_metrics?.total_return * 100 || 0).toFixed(1);
          console.log(`    ${backtest.strategy} - ${returnPct}% return`);
        });
      } else {
        console.log('  🧪 No backtests run yet');
      }
      
      // Shariah stocks
      const shariahCount = await this.db.collection('stocks')
        .countDocuments({ shariah_compliant: true });
      console.log(`  ☪️  Shariah-compliant stocks: ${shariahCount}`);
      
    } catch (error) {
      console.error('❌ Error getting database status:', error.message);
    }
  }

  async resetDatabase() {
    console.log('🔄 Resetting EmergentTrader Database');
    console.log('===================================');
    
    try {
      await this.connect();
      
      // Drop all collections
      const collections = await this.db.listCollections().toArray();
      console.log(`\n🗑️  Dropping ${collections.length} collections...`);
      
      for (const collection of collections) {
        await this.db.collection(collection.name).drop();
        console.log(`  ✅ Dropped: ${collection.name}`);
      }
      
      console.log('\n🔄 Re-running database setup...');
      
      // Re-run setup
      const { setupDatabase } = require('./setup-database.js');
      await setupDatabase();
      
    } catch (error) {
      console.error('❌ Error resetting database:', error.message);
    }
  }

  async cleanupOldData() {
    console.log('🧹 Cleaning up old data');
    console.log('======================');
    
    try {
      await this.connect();
      
      const thirtyDaysAgo = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000);
      const sevenDaysAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000);
      
      // Clean old signals
      const oldSignalsResult = await this.db.collection('trading_signals')
        .deleteMany({
          generated_at: { $lt: thirtyDaysAgo },
          status: { $in: ['EXPIRED', 'EXECUTED'] }
        });
      console.log(`🗑️  Removed ${oldSignalsResult.deletedCount} old signals`);
      
      // Clean old backtest results (keep last 10)
      const backtests = await this.db.collection('backtest_results')
        .find({})
        .sort({ created_at: -1 })
        .skip(10)
        .toArray();
      
      if (backtests.length > 0) {
        const oldBacktestIds = backtests.map(b => b._id);
        const oldBacktestsResult = await this.db.collection('backtest_results')
          .deleteMany({ _id: { $in: oldBacktestIds } });
        console.log(`🗑️  Removed ${oldBacktestsResult.deletedCount} old backtest results`);
      }
      
      // Clean old tracking data
      const oldTrackingResult = await this.db.collection('signal_tracking')
        .deleteMany({ last_updated: { $lt: sevenDaysAgo } });
      console.log(`🗑️  Removed ${oldTrackingResult.deletedCount} old tracking records`);
      
      console.log('✅ Cleanup completed');
      
    } catch (error) {
      console.error('❌ Error during cleanup:', error.message);
    }
  }

  async exportData() {
    console.log('📤 Exporting database data');
    console.log('=========================');
    
    try {
      await this.connect();
      
      const exportDir = path.join(process.cwd(), 'exports');
      if (!fs.existsSync(exportDir)) {
        fs.mkdirSync(exportDir);
      }
      
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      const exportFile = path.join(exportDir, `emergent_trader_${timestamp}.json`);
      
      const collections = ['stocks', 'trading_signals', 'backtest_results', 'shariah_compliance'];
      const exportData = {};
      
      for (const collectionName of collections) {
        const data = await this.db.collection(collectionName).find({}).toArray();
        exportData[collectionName] = data;
        console.log(`📋 Exported ${data.length} documents from ${collectionName}`);
      }
      
      fs.writeFileSync(exportFile, JSON.stringify(exportData, null, 2));
      console.log(`✅ Data exported to: ${exportFile}`);
      
    } catch (error) {
      console.error('❌ Error exporting data:', error.message);
    }
  }
}

// CLI Interface
async function main() {
  const command = process.argv[2];
  const dbManager = new DatabaseManager();
  
  try {
    switch (command) {
      case 'status':
        await dbManager.getStatus();
        break;
        
      case 'reset':
        console.log('⚠️  This will delete all data. Continue? (y/N)');
        process.stdin.setRawMode(true);
        process.stdin.resume();
        process.stdin.on('data', async (key) => {
          if (key.toString().toLowerCase() === 'y') {
            await dbManager.resetDatabase();
          } else {
            console.log('❌ Reset cancelled');
          }
          process.exit(0);
        });
        return;
        
      case 'cleanup':
        await dbManager.cleanupOldData();
        break;
        
      case 'export':
        await dbManager.exportData();
        break;
        
      default:
        console.log('🛠️  EmergentTrader Database Manager');
        console.log('==================================');
        console.log('');
        console.log('Usage:');
        console.log('  node scripts/db-manager.js status   - Show database status');
        console.log('  node scripts/db-manager.js reset    - Reset database (WARNING: deletes all data)');
        console.log('  node scripts/db-manager.js cleanup  - Clean up old data');
        console.log('  node scripts/db-manager.js export   - Export data to JSON');
        console.log('');
        break;
    }
  } catch (error) {
    console.error('❌ Command failed:', error.message);
  } finally {
    await dbManager.disconnect();
  }
}

if (require.main === module) {
  main().catch(console.error);
}

module.exports = DatabaseManager;
