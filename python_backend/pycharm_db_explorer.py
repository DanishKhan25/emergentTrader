#!/usr/bin/env python3
"""
PyCharm Database Explorer for EmergentTrader
Run this script in PyCharm to explore your SQLite database interactively
"""

import sqlite3
import pandas as pd
import json
from datetime import datetime, timedelta
import os

class EmergentTraderDBExplorer:
    def __init__(self, db_path="data/signals.db"):
        """Initialize database explorer"""
        self.db_path = db_path
        if not os.path.exists(db_path):
            print(f"❌ Database not found at {db_path}")
            print("Make sure you're running from python_backend directory")
            return
        
        self.conn = sqlite3.connect(db_path)
        print(f"✅ Connected to database: {db_path}")
    
    def show_tables(self):
        """Show all tables in database"""
        query = "SELECT name FROM sqlite_master WHERE type='table'"
        tables = pd.read_sql_query(query, self.conn)
        print("\n📊 Database Tables:")
        for table in tables['name']:
            print(f"  • {table}")
        return tables
    
    def show_table_schema(self, table_name):
        """Show schema for a specific table"""
        query = f"PRAGMA table_info({table_name})"
        schema = pd.read_sql_query(query, self.conn)
        print(f"\n🏗️  Schema for '{table_name}':")
        print(schema.to_string(index=False))
        return schema
    
    def get_active_signals(self):
        """Get all active signals"""
        query = """
        SELECT signal_id, symbol, strategy, signal_type, confidence, 
               price, generated_at, status
        FROM signals 
        WHERE status = 'ACTIVE'
        ORDER BY generated_at DESC
        """
        signals = pd.read_sql_query(query, self.conn)
        print(f"\n🎯 Active Signals ({len(signals)} total):")
        if not signals.empty:
            print(signals.to_string(index=False))
        else:
            print("  No active signals found")
        return signals
    
    def get_strategy_summary(self):
        """Get strategy performance summary"""
        query = """
        SELECT 
            strategy,
            COUNT(*) as total_signals,
            COUNT(CASE WHEN status = 'ACTIVE' THEN 1 END) as active_signals,
            ROUND(AVG(confidence), 3) as avg_confidence,
            MIN(generated_at) as first_signal,
            MAX(generated_at) as latest_signal
        FROM signals
        GROUP BY strategy
        ORDER BY total_signals DESC
        """
        summary = pd.read_sql_query(query, self.conn)
        print(f"\n📈 Strategy Summary:")
        if not summary.empty:
            print(summary.to_string(index=False))
        else:
            print("  No signals found")
        return summary
    
    def get_consensus_signals(self):
        """Get consensus signals"""
        query = """
        SELECT consensus_id, symbol, signal_type, strategies, 
               strategy_count, consensus_strength, generated_at
        FROM consensus_signals
        WHERE status = 'ACTIVE'
        ORDER BY consensus_strength DESC
        """
        consensus = pd.read_sql_query(query, self.conn)
        print(f"\n🤝 Consensus Signals ({len(consensus)} total):")
        if not consensus.empty:
            print(consensus.to_string(index=False))
        else:
            print("  No consensus signals found")
        return consensus
    
    def get_recent_activity(self, days=7):
        """Get recent signal activity"""
        query = f"""
        SELECT 
            DATE(generated_at) as date,
            COUNT(*) as signals_generated,
            COUNT(DISTINCT strategy) as strategies_used,
            COUNT(DISTINCT symbol) as unique_symbols,
            GROUP_CONCAT(DISTINCT strategy) as strategies_list
        FROM signals
        WHERE generated_at >= datetime('now', '-{days} days')
        GROUP BY DATE(generated_at)
        ORDER BY date DESC
        """
        activity = pd.read_sql_query(query, self.conn)
        print(f"\n📅 Recent Activity (Last {days} days):")
        if not activity.empty:
            print(activity.to_string(index=False))
        else:
            print("  No recent activity found")
        return activity
    
    def search_signals(self, symbol=None, strategy=None, signal_type=None):
        """Search signals with filters"""
        conditions = ["1=1"]  # Always true condition
        params = []
        
        if symbol:
            conditions.append("symbol = ?")
            params.append(symbol)
        
        if strategy:
            conditions.append("strategy = ?")
            params.append(strategy)
        
        if signal_type:
            conditions.append("signal_type = ?")
            params.append(signal_type)
        
        query = f"""
        SELECT signal_id, symbol, strategy, signal_type, confidence, 
               price, generated_at, status
        FROM signals 
        WHERE {' AND '.join(conditions)}
        ORDER BY generated_at DESC
        """
        
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        columns = ['signal_id', 'symbol', 'strategy', 'signal_type', 
                  'confidence', 'price', 'generated_at', 'status']
        df = pd.DataFrame(results, columns=columns)
        
        print(f"\n🔍 Search Results:")
        print(f"   Filters: symbol={symbol}, strategy={strategy}, signal_type={signal_type}")
        if not df.empty:
            print(df.to_string(index=False))
        else:
            print("  No matching signals found")
        return df
    
    def get_database_stats(self):
        """Get comprehensive database statistics"""
        stats = {}
        
        # Total signals
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM signals")
        stats['total_signals'] = cursor.fetchone()[0]
        
        # Active signals
        cursor.execute("SELECT COUNT(*) FROM signals WHERE status = 'ACTIVE'")
        stats['active_signals'] = cursor.fetchone()[0]
        
        # Consensus signals
        cursor.execute("SELECT COUNT(*) FROM consensus_signals WHERE status = 'ACTIVE'")
        stats['consensus_signals'] = cursor.fetchone()[0]
        
        # Date range
        cursor.execute("SELECT MIN(generated_at), MAX(generated_at) FROM signals")
        date_range = cursor.fetchone()
        stats['date_range'] = {'earliest': date_range[0], 'latest': date_range[1]}
        
        print(f"\n📊 Database Statistics:")
        print(f"   Total signals: {stats['total_signals']}")
        print(f"   Active signals: {stats['active_signals']}")
        print(f"   Consensus signals: {stats['consensus_signals']}")
        print(f"   Date range: {stats['date_range']['earliest']} to {stats['date_range']['latest']}")
        
        return stats
    
    def run_custom_query(self, query):
        """Run a custom SQL query"""
        try:
            result = pd.read_sql_query(query, self.conn)
            print(f"\n🔧 Custom Query Results:")
            print(result.to_string(index=False))
            return result
        except Exception as e:
            print(f"❌ Query error: {str(e)}")
            return None
    
    def close(self):
        """Close database connection"""
        if hasattr(self, 'conn'):
            self.conn.close()
            print("✅ Database connection closed")

def main():
    """Main exploration function - run this in PyCharm"""
    print("🗄️  EmergentTrader Database Explorer")
    print("=" * 50)
    
    # Initialize explorer
    explorer = EmergentTraderDBExplorer()
    
    # Show database overview
    explorer.show_tables()
    explorer.get_database_stats()
    
    # Show current data
    explorer.get_active_signals()
    explorer.get_strategy_summary()
    explorer.get_consensus_signals()
    explorer.get_recent_activity()
    
    # Example searches
    print("\n" + "=" * 50)
    print("🔍 Example Searches:")
    
    # Search for TCS signals
    explorer.search_signals(symbol='TCS')
    
    # Search for low_volatility strategy
    explorer.search_signals(strategy='low_volatility')
    
    # Search for BUY signals
    explorer.search_signals(signal_type='BUY')
    
    # Close connection
    explorer.close()
    
    print("\n🎯 PyCharm Usage Tips:")
    print("1. Set breakpoints to inspect DataFrames")
    print("2. Use Variables view to explore data structures")
    print("3. Run individual methods: explorer.get_active_signals()")
    print("4. Modify queries and re-run for custom analysis")

if __name__ == "__main__":
    main()
