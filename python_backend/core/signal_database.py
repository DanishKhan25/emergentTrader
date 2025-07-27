import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import os

logger = logging.getLogger(__name__)

class SignalDatabase:
    """Database manager for trading signals with performance tracking"""
    
    def __init__(self, db_path: str = "data/signals.db"):
        """Initialize signal database"""
        self.db_path = db_path
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Initialize database
        self._init_database()
        logger.info(f"Signal database initialized at {db_path}")
    
    def _init_database(self):
        """Create database tables if they don't exist"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Signals table - stores all generated signals
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS signals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    signal_id TEXT UNIQUE NOT NULL,
                    symbol TEXT NOT NULL,
                    strategy TEXT NOT NULL,
                    signal_type TEXT NOT NULL,  -- BUY, SELL, HOLD
                    confidence REAL NOT NULL,
                    price REAL,
                    target_price REAL,
                    stop_loss REAL,
                    generated_at TIMESTAMP NOT NULL,
                    expires_at TIMESTAMP,
                    status TEXT DEFAULT 'ACTIVE',  -- ACTIVE, EXPIRED, EXECUTED, CANCELLED
                    metadata TEXT,  -- JSON string for additional data
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Signal performance tracking
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS signal_performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    signal_id TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    strategy TEXT NOT NULL,
                    entry_price REAL,
                    current_price REAL,
                    highest_price REAL,
                    lowest_price REAL,
                    return_pct REAL,
                    max_gain_pct REAL,
                    max_loss_pct REAL,
                    days_active INTEGER,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (signal_id) REFERENCES signals (signal_id)
                )
            ''')
            
            # Strategy performance summary
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS strategy_performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    strategy TEXT NOT NULL,
                    date DATE NOT NULL,
                    total_signals INTEGER DEFAULT 0,
                    active_signals INTEGER DEFAULT 0,
                    successful_signals INTEGER DEFAULT 0,
                    failed_signals INTEGER DEFAULT 0,
                    avg_return_pct REAL DEFAULT 0.0,
                    success_rate REAL DEFAULT 0.0,
                    sharpe_ratio REAL,
                    max_drawdown REAL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(strategy, date)
                )
            ''')
            
            # Consensus signals - tracks multi-strategy agreements
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS consensus_signals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    consensus_id TEXT UNIQUE NOT NULL,
                    symbol TEXT NOT NULL,
                    signal_type TEXT NOT NULL,
                    strategies TEXT NOT NULL,  -- JSON array of strategy names
                    strategy_count INTEGER NOT NULL,
                    avg_confidence REAL NOT NULL,
                    consensus_strength REAL NOT NULL,  -- 0-1 score
                    generated_at TIMESTAMP NOT NULL,
                    status TEXT DEFAULT 'ACTIVE',
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_signals_symbol ON signals(symbol)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_signals_strategy ON signals(strategy)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_signals_generated_at ON signals(generated_at)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_signals_status ON signals(status)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_consensus_symbol ON consensus_signals(symbol)')
            
            conn.commit()
            logger.info("Database tables created/verified successfully")
    
    def check_duplicate_signal(self, symbol: str, target_price: float, stop_loss: float, strategy: str = None) -> bool:
        """Check if a signal with same symbol, target, and stop loss already exists"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check for active signals with same symbol, target, and stop loss
                query = '''
                    SELECT COUNT(*) FROM signals 
                    WHERE symbol = ? 
                    AND target_price = ? 
                    AND stop_loss = ? 
                    AND status = 'ACTIVE'
                '''
                params = [symbol, target_price, stop_loss]
                
                # Optionally exclude same strategy (allow different strategies with same levels)
                if strategy:
                    query += ' AND strategy != ?'
                    params.append(strategy)
                
                cursor.execute(query, params)
                count = cursor.fetchone()[0]
                
                if count > 0:
                    logger.info(f"Duplicate signal detected for {symbol} with target {target_price} and SL {stop_loss}")
                    return True
                    
                return False
                
        except Exception as e:
            logger.error(f"Error checking duplicate signal: {str(e)}")
            return False

    def save_signal(self, signal: Dict[str, Any]) -> bool:
        """Save a single signal to database with duplicate detection"""
        try:
            symbol = signal['symbol']
            target_price = signal.get('target_price')
            stop_loss = signal.get('stop_loss')
            strategy = signal['strategy']
            
            # Check for duplicates if target and stop loss are provided
            if target_price and stop_loss:
                if self.check_duplicate_signal(symbol, target_price, stop_loss, strategy):
                    logger.warning(f"Skipping duplicate signal for {symbol} (Target: {target_price}, SL: {stop_loss})")
                    return False
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Generate unique signal ID if not provided
                signal_id = signal.get('signal_id', f"{signal['symbol']}_{signal['strategy']}_{int(datetime.now().timestamp())}")
                
                cursor.execute('''
                    INSERT OR REPLACE INTO signals 
                    (signal_id, symbol, strategy, signal_type, confidence, price, 
                     target_price, stop_loss, generated_at, expires_at, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    signal_id,
                    signal['symbol'],
                    signal['strategy'],
                    signal.get('signal', 'BUY'),
                    signal.get('confidence', 0.0),
                    signal.get('price', signal.get('current_price')),
                    signal.get('target_price'),
                    signal.get('stop_loss'),
                    signal.get('generated_at', datetime.now().isoformat()),
                    signal.get('expires_at'),
                    json.dumps({k: v for k, v in signal.items() if k not in [
                        'signal_id', 'symbol', 'strategy', 'signal', 'confidence', 
                        'price', 'target_price', 'stop_loss', 'generated_at', 'expires_at'
                    ]})
                ))
                
                conn.commit()
                logger.info(f"Signal saved: {signal_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error saving signal: {str(e)}")
            return False
    
    def save_signals_batch(self, signals: List[Dict[str, Any]]) -> Dict[str, int]:
        """Save multiple signals in batch with duplicate tracking"""
        saved_count = 0
        duplicate_count = 0
        error_count = 0
        
        for signal in signals:
            try:
                if self.save_signal(signal):
                    saved_count += 1
                else:
                    # Check if it was a duplicate or error
                    symbol = signal['symbol']
                    target_price = signal.get('target_price')
                    stop_loss = signal.get('stop_loss')
                    strategy = signal['strategy']
                    
                    if target_price and stop_loss and self.check_duplicate_signal(symbol, target_price, stop_loss, strategy):
                        duplicate_count += 1
                    else:
                        error_count += 1
            except Exception as e:
                logger.error(f"Error in batch save for signal: {str(e)}")
                error_count += 1
        
        logger.info(f"Batch save complete: {saved_count} saved, {duplicate_count} duplicates skipped, {error_count} errors")
        
        return {
            'saved': saved_count,
            'duplicates': duplicate_count,
            'errors': error_count,
            'total_processed': len(signals)
        }
    
    def save_consensus_signal(self, consensus_signal: Dict[str, Any]) -> bool:
        """Save a consensus signal (multi-strategy agreement)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                consensus_id = consensus_signal.get('consensus_id', 
                    f"consensus_{consensus_signal['symbol']}_{int(datetime.now().timestamp())}")
                
                cursor.execute('''
                    INSERT OR REPLACE INTO consensus_signals 
                    (consensus_id, symbol, signal_type, strategies, strategy_count, 
                     avg_confidence, consensus_strength, generated_at, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    consensus_id,
                    consensus_signal['symbol'],
                    consensus_signal.get('signal', 'BUY'),
                    json.dumps(consensus_signal.get('strategies', [])),
                    consensus_signal.get('strategy_count', 0),
                    consensus_signal.get('avg_confidence', 0.0),
                    consensus_signal.get('consensus_strength', 0.0),
                    consensus_signal.get('generated_at', datetime.now().isoformat()),
                    json.dumps({k: v for k, v in consensus_signal.items() if k not in [
                        'consensus_id', 'symbol', 'signal', 'strategies', 'strategy_count',
                        'avg_confidence', 'consensus_strength', 'generated_at'
                    ]})
                ))
                
                conn.commit()
                logger.info(f"Consensus signal saved: {consensus_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error saving consensus signal: {str(e)}")
            return False
    
    def get_active_signals(self, strategy: Optional[str] = None, symbol: Optional[str] = None) -> List[Dict]:
        """Get currently active signals"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                query = "SELECT * FROM signals WHERE status = 'ACTIVE'"
                params = []
                
                if strategy:
                    query += " AND strategy = ?"
                    params.append(strategy)
                
                if symbol:
                    query += " AND symbol = ?"
                    params.append(symbol)
                
                query += " ORDER BY generated_at DESC"
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                # Convert to dictionaries
                columns = [desc[0] for desc in cursor.description]
                signals = []
                for row in rows:
                    signal = dict(zip(columns, row))
                    # Parse metadata JSON
                    if signal['metadata']:
                        try:
                            metadata = json.loads(signal['metadata'])
                            signal.update(metadata)
                        except:
                            pass
                    signals.append(signal)
                
                return signals
                
        except Exception as e:
            logger.error(f"Error getting active signals: {str(e)}")
            return []
    
    def get_strategy_performance(self, strategy: str, days: int = 30) -> Dict:
        """Get performance summary for a strategy"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get signals from last N days
                cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
                
                cursor.execute('''
                    SELECT COUNT(*) as total_signals,
                           AVG(confidence) as avg_confidence,
                           COUNT(CASE WHEN status = 'ACTIVE' THEN 1 END) as active_signals
                    FROM signals 
                    WHERE strategy = ? AND generated_at >= ?
                ''', (strategy, cutoff_date))
                
                result = cursor.fetchone()
                
                return {
                    'strategy': strategy,
                    'period_days': days,
                    'total_signals': result[0] or 0,
                    'avg_confidence': round(result[1] or 0.0, 3),
                    'active_signals': result[2] or 0,
                    'success_rate': 0.0,  # TODO: Calculate based on performance tracking
                    'avg_return': 0.0     # TODO: Calculate based on performance tracking
                }
                
        except Exception as e:
            logger.error(f"Error getting strategy performance: {str(e)}")
            return {'strategy': strategy, 'error': str(e)}
    
    def get_consensus_signals(self, days: int = 7) -> List[Dict]:
        """Get recent consensus signals"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
                
                cursor.execute('''
                    SELECT * FROM consensus_signals 
                    WHERE generated_at >= ? AND status = 'ACTIVE'
                    ORDER BY consensus_strength DESC, generated_at DESC
                ''', (cutoff_date,))
                
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                
                consensus_signals = []
                for row in rows:
                    signal = dict(zip(columns, row))
                    # Parse JSON fields
                    if signal['strategies']:
                        signal['strategies'] = json.loads(signal['strategies'])
                    if signal['metadata']:
                        try:
                            metadata = json.loads(signal['metadata'])
                            signal.update(metadata)
                        except:
                            pass
                    consensus_signals.append(signal)
                
                return consensus_signals
                
        except Exception as e:
            logger.error(f"Error getting consensus signals: {str(e)}")
            return []
    
    def get_database_stats(self) -> Dict:
        """Get database statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Count signals by status
                cursor.execute('SELECT status, COUNT(*) FROM signals GROUP BY status')
                status_counts = dict(cursor.fetchall())
                
                # Count signals by strategy
                cursor.execute('SELECT strategy, COUNT(*) FROM signals GROUP BY strategy ORDER BY COUNT(*) DESC')
                strategy_counts = dict(cursor.fetchall())
                
                # Count consensus signals
                cursor.execute('SELECT COUNT(*) FROM consensus_signals WHERE status = "ACTIVE"')
                active_consensus = cursor.fetchone()[0]
                
                # Get date range
                cursor.execute('SELECT MIN(generated_at), MAX(generated_at) FROM signals')
                date_range = cursor.fetchone()
                
                return {
                    'total_signals': sum(status_counts.values()),
                    'status_breakdown': status_counts,
                    'strategy_breakdown': strategy_counts,
                    'active_consensus_signals': active_consensus,
                    'date_range': {
                        'earliest': date_range[0],
                        'latest': date_range[1]
                    },
                    'database_path': self.db_path
                }
                
        except Exception as e:
            logger.error(f"Error getting database stats: {str(e)}")
            return {'error': str(e)}

# Convenience functions for easy integration
def get_signal_db() -> SignalDatabase:
    """Get singleton signal database instance"""
    if not hasattr(get_signal_db, '_instance'):
        get_signal_db._instance = SignalDatabase()
    return get_signal_db._instance

def save_signals(signals: List[Dict[str, Any]]) -> int:
    """Quick function to save signals"""
    db = get_signal_db()
    return db.save_signals_batch(signals)

def save_consensus_signals(consensus_signals: List[Dict[str, Any]]) -> int:
    """Quick function to save consensus signals"""
    db = get_signal_db()
    saved = 0
    for signal in consensus_signals:
        if db.save_consensus_signal(signal):
            saved += 1
    return saved
