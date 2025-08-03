#!/usr/bin/env python3
"""
Database Migration Script for Production Deployment
Migrates from SQLite to PostgreSQL and sets up production schema
"""

import os
import sys
import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path

# Database imports
try:
    import psycopg2
    import psycopg2.extras
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False
    print("Warning: psycopg2 not available. Install with: pip install psycopg2-binary")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProductionMigrator:
    def __init__(self):
        self.sqlite_db = "emergent_trader.db"
        self.postgres_url = os.getenv("DATABASE_URL")
        
        if not self.postgres_url:
            logger.warning("DATABASE_URL not set. Using SQLite for development.")
            self.use_postgres = False
        else:
            self.use_postgres = POSTGRES_AVAILABLE
    
    def create_production_schema(self):
        """Create production database schema"""
        schema_sql = """
        -- Signals table
        CREATE TABLE IF NOT EXISTS signals (
            id SERIAL PRIMARY KEY,
            symbol VARCHAR(20) NOT NULL,
            strategy VARCHAR(50) NOT NULL,
            signal_type VARCHAR(20) NOT NULL,
            confidence DECIMAL(5,4) NOT NULL,
            entry_price DECIMAL(10,2),
            target_price DECIMAL(10,2),
            stop_loss DECIMAL(10,2),
            current_price DECIMAL(10,2),
            returns DECIMAL(8,4),
            status VARCHAR(20) DEFAULT 'active',
            generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            run_type VARCHAR(20),
            scan_id VARCHAR(100),
            ml_score DECIMAL(5,4),
            shariah_compliant BOOLEAN DEFAULT true,
            metadata JSONB
        );
        
        -- Portfolio table
        CREATE TABLE IF NOT EXISTS portfolio (
            id SERIAL PRIMARY KEY,
            symbol VARCHAR(20) NOT NULL,
            quantity INTEGER NOT NULL,
            entry_price DECIMAL(10,2) NOT NULL,
            current_price DECIMAL(10,2),
            entry_date DATE NOT NULL,
            exit_date DATE,
            status VARCHAR(20) DEFAULT 'active',
            returns DECIMAL(8,4),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Market data cache table
        CREATE TABLE IF NOT EXISTS market_data_cache (
            id SERIAL PRIMARY KEY,
            symbol VARCHAR(20) NOT NULL,
            data JSONB NOT NULL,
            cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            UNIQUE(symbol)
        );
        
        -- Scheduled job reports table
        CREATE TABLE IF NOT EXISTS scheduled_reports (
            id SERIAL PRIMARY KEY,
            run_type VARCHAR(20) NOT NULL,
            run_name VARCHAR(100) NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total_signals_generated INTEGER DEFAULT 0,
            signals_saved INTEGER DEFAULT 0,
            success BOOLEAN DEFAULT true,
            error_message TEXT,
            report_data JSONB
        );
        
        -- User notifications table
        CREATE TABLE IF NOT EXISTS notifications (
            id SERIAL PRIMARY KEY,
            title VARCHAR(200) NOT NULL,
            message TEXT NOT NULL,
            type VARCHAR(50) NOT NULL,
            data JSONB,
            read BOOLEAN DEFAULT false,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Indexes for performance
        CREATE INDEX IF NOT EXISTS idx_signals_symbol ON signals(symbol);
        CREATE INDEX IF NOT EXISTS idx_signals_generated_at ON signals(generated_at);
        CREATE INDEX IF NOT EXISTS idx_signals_status ON signals(status);
        CREATE INDEX IF NOT EXISTS idx_signals_run_type ON signals(run_type);
        CREATE INDEX IF NOT EXISTS idx_portfolio_symbol ON portfolio(symbol);
        CREATE INDEX IF NOT EXISTS idx_portfolio_status ON portfolio(status);
        CREATE INDEX IF NOT EXISTS idx_market_data_symbol ON market_data_cache(symbol);
        CREATE INDEX IF NOT EXISTS idx_scheduled_reports_timestamp ON scheduled_reports(timestamp);
        CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications(created_at);
        """
        
        if self.use_postgres:
            return self.execute_postgres_schema(schema_sql)
        else:
            return self.execute_sqlite_schema(schema_sql)
    
    def execute_postgres_schema(self, schema_sql):
        """Execute schema creation in PostgreSQL"""
        try:
            conn = psycopg2.connect(self.postgres_url)
            cursor = conn.cursor()
            
            # Execute schema creation
            cursor.execute(schema_sql)
            conn.commit()
            
            logger.info("PostgreSQL schema created successfully")
            
            cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Error creating PostgreSQL schema: {e}")
            return False
    
    def execute_sqlite_schema(self, schema_sql):
        """Execute schema creation in SQLite (for development)"""
        try:
            # Convert PostgreSQL schema to SQLite
            sqlite_schema = self.convert_postgres_to_sqlite(schema_sql)
            
            conn = sqlite3.connect(self.sqlite_db)
            cursor = conn.cursor()
            
            # Execute schema creation
            cursor.executescript(sqlite_schema)
            conn.commit()
            
            logger.info("SQLite schema created successfully")
            
            cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Error creating SQLite schema: {e}")
            return False
    
    def convert_postgres_to_sqlite(self, postgres_sql):
        """Convert PostgreSQL schema to SQLite compatible"""
        sqlite_sql = postgres_sql
        
        # Replace PostgreSQL specific types
        replacements = {
            'SERIAL PRIMARY KEY': 'INTEGER PRIMARY KEY AUTOINCREMENT',
            'DECIMAL(10,2)': 'REAL',
            'DECIMAL(8,4)': 'REAL',
            'DECIMAL(5,4)': 'REAL',
            'VARCHAR(20)': 'TEXT',
            'VARCHAR(50)': 'TEXT',
            'VARCHAR(100)': 'TEXT',
            'VARCHAR(200)': 'TEXT',
            'BOOLEAN': 'INTEGER',
            'JSONB': 'TEXT',
            'TIMESTAMP': 'TEXT',
            'DATE': 'TEXT',
            'CURRENT_TIMESTAMP': "datetime('now')",
        }
        
        for postgres_type, sqlite_type in replacements.items():
            sqlite_sql = sqlite_sql.replace(postgres_type, sqlite_type)
        
        return sqlite_sql
    
    def migrate_existing_data(self):
        """Migrate existing SQLite data to production database"""
        if not Path(self.sqlite_db).exists():
            logger.info("No existing SQLite database found. Starting fresh.")
            return True
        
        try:
            # Read from SQLite
            sqlite_conn = sqlite3.connect(self.sqlite_db)
            sqlite_conn.row_factory = sqlite3.Row
            sqlite_cursor = sqlite_conn.cursor()
            
            # Get existing signals
            sqlite_cursor.execute("SELECT * FROM signals ORDER BY id")
            signals = sqlite_cursor.fetchall()
            
            logger.info(f"Found {len(signals)} signals to migrate")
            
            if self.use_postgres:
                self.migrate_to_postgres(signals)
            else:
                logger.info("Using SQLite - no migration needed")
            
            sqlite_cursor.close()
            sqlite_conn.close()
            
            return True
            
        except Exception as e:
            logger.error(f"Error migrating data: {e}")
            return False
    
    def migrate_to_postgres(self, signals):
        """Migrate signals to PostgreSQL"""
        try:
            conn = psycopg2.connect(self.postgres_url)
            cursor = conn.cursor()
            
            # Insert signals
            for signal in signals:
                insert_sql = """
                INSERT INTO signals (
                    symbol, strategy, signal_type, confidence, entry_price,
                    target_price, stop_loss, current_price, returns, status,
                    generated_at, updated_at, run_type, scan_id, ml_score,
                    shariah_compliant, metadata
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s
                )
                """
                
                cursor.execute(insert_sql, (
                    signal['symbol'],
                    signal['strategy'],
                    signal.get('signal_type', 'buy'),
                    signal['confidence'],
                    signal.get('entry_price'),
                    signal.get('target_price'),
                    signal.get('stop_loss'),
                    signal.get('current_price'),
                    signal.get('returns'),
                    signal.get('status', 'active'),
                    signal.get('generated_at'),
                    signal.get('updated_at'),
                    signal.get('run_type'),
                    signal.get('scan_id'),
                    signal.get('ml_score'),
                    signal.get('shariah_compliant', True),
                    json.dumps(signal.get('metadata', {}))
                ))
            
            conn.commit()
            logger.info(f"Migrated {len(signals)} signals to PostgreSQL")
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error migrating to PostgreSQL: {e}")
            raise
    
    def setup_production_data(self):
        """Setup initial production data"""
        try:
            # Create sample notification
            notification_data = {
                'title': 'EmergentTrader Production Deployed',
                'message': 'Your trading signal system is now running in production with automated daily scans.',
                'type': 'system',
                'data': {
                    'deployment_time': datetime.now().isoformat(),
                    'version': '2.0.0'
                }
            }
            
            if self.use_postgres:
                self.insert_postgres_notification(notification_data)
            else:
                self.insert_sqlite_notification(notification_data)
            
            logger.info("Production setup data inserted")
            return True
            
        except Exception as e:
            logger.error(f"Error setting up production data: {e}")
            return False
    
    def insert_postgres_notification(self, notification):
        """Insert notification into PostgreSQL"""
        conn = psycopg2.connect(self.postgres_url)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO notifications (title, message, type, data)
            VALUES (%s, %s, %s, %s)
        """, (
            notification['title'],
            notification['message'],
            notification['type'],
            json.dumps(notification['data'])
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
    
    def insert_sqlite_notification(self, notification):
        """Insert notification into SQLite"""
        conn = sqlite3.connect(self.sqlite_db)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO notifications (title, message, type, data)
            VALUES (?, ?, ?, ?)
        """, (
            notification['title'],
            notification['message'],
            notification['type'],
            json.dumps(notification['data'])
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
    
    def verify_migration(self):
        """Verify migration was successful"""
        try:
            if self.use_postgres:
                conn = psycopg2.connect(self.postgres_url)
                cursor = conn.cursor()
                
                # Check tables exist
                cursor.execute("""
                    SELECT table_name FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """)
                tables = [row[0] for row in cursor.fetchall()]
                
                expected_tables = ['signals', 'portfolio', 'market_data_cache', 
                                 'scheduled_reports', 'notifications']
                
                for table in expected_tables:
                    if table in tables:
                        cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        count = cursor.fetchone()[0]
                        logger.info(f"Table {table}: {count} records")
                    else:
                        logger.error(f"Table {table} not found!")
                        return False
                
                cursor.close()
                conn.close()
                
            else:
                conn = sqlite3.connect(self.sqlite_db)
                cursor = conn.cursor()
                
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                
                logger.info(f"SQLite tables: {tables}")
                
                cursor.close()
                conn.close()
            
            logger.info("Migration verification completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error verifying migration: {e}")
            return False
    
    def run_migration(self):
        """Run complete migration process"""
        logger.info("Starting production database migration...")
        
        # Step 1: Create schema
        if not self.create_production_schema():
            logger.error("Schema creation failed")
            return False
        
        # Step 2: Migrate existing data
        if not self.migrate_existing_data():
            logger.error("Data migration failed")
            return False
        
        # Step 3: Setup production data
        if not self.setup_production_data():
            logger.error("Production data setup failed")
            return False
        
        # Step 4: Verify migration
        if not self.verify_migration():
            logger.error("Migration verification failed")
            return False
        
        logger.info("Production database migration completed successfully!")
        return True

def main():
    """Main migration function"""
    migrator = ProductionMigrator()
    
    if migrator.run_migration():
        print("✅ Database migration completed successfully!")
        print("🚀 Your EmergentTrader is ready for production!")
        return 0
    else:
        print("❌ Database migration failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
