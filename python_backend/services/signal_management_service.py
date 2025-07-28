"""
Signal Management Service for EmergentTrader
Handles signal generation, tracking, and performance monitoring
"""

import sqlite3
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import asyncio
import yfinance as yf

logger = logging.getLogger(__name__)

@dataclass
class SignalData:
    """Data class for signal information"""
    signal_id: str
    symbol: str
    strategy: str
    signal_type: str
    entry_price: float
    target_price: float
    stop_loss: float
    confidence: float
    created_at: str
    status: str = 'active'

class SignalManagementService:
    def __init__(self, db_path: str = "python_backend/emergent_trader.db"):
        """Initialize signal management service"""
        self.db_path = db_path
        self.init_database()
        logger.info("Signal Management Service initialized")
    
    def init_database(self):
        """Initialize signal tracking database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create signals table (enhanced)
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS signals (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        signal_id TEXT UNIQUE NOT NULL,
                        symbol TEXT NOT NULL,
                        strategy TEXT NOT NULL,
                        signal_type TEXT NOT NULL,
                        entry_price REAL NOT NULL,
                        target_price REAL NOT NULL,
                        stop_loss REAL NOT NULL,
                        confidence REAL NOT NULL,
                        current_price REAL,
                        status TEXT DEFAULT 'active',
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL,
                        target_hit_at TEXT,
                        stop_loss_hit_at TEXT,
                        profit_loss REAL DEFAULT 0,
                        profit_loss_percent REAL DEFAULT 0,
                        max_price REAL DEFAULT 0,
                        min_price REAL DEFAULT 0,
                        days_active INTEGER DEFAULT 0,
                        metadata TEXT
                    )
                ''')
                
                # Create signal performance summary table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS signal_performance (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date TEXT NOT NULL,
                        total_signals INTEGER DEFAULT 0,
                        active_signals INTEGER DEFAULT 0,
                        target_hits INTEGER DEFAULT 0,
                        stop_losses INTEGER DEFAULT 0,
                        success_rate REAL DEFAULT 0,
                        avg_profit_percent REAL DEFAULT 0,
                        avg_loss_percent REAL DEFAULT 0,
                        total_profit_loss REAL DEFAULT 0,
                        created_at TEXT NOT NULL,
                        UNIQUE(date)
                    )
                ''')
                
                # Create strategy performance table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS strategy_performance (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        strategy TEXT NOT NULL,
                        total_signals INTEGER DEFAULT 0,
                        target_hits INTEGER DEFAULT 0,
                        stop_losses INTEGER DEFAULT 0,
                        success_rate REAL DEFAULT 0,
                        avg_profit_percent REAL DEFAULT 0,
                        avg_loss_percent REAL DEFAULT 0,
                        last_updated TEXT NOT NULL,
                        UNIQUE(strategy)
                    )
                ''')
                
                conn.commit()
                logger.info("Signal database initialized successfully")
                
        except Exception as e:
            logger.error(f"Error initializing signal database: {e}")
    
    def clear_all_signals(self) -> Dict:
        """Clear all signals from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get count before clearing
                cursor.execute('SELECT COUNT(*) FROM signals')
                count_before = cursor.fetchone()[0]
                
                # Clear signals table
                cursor.execute('DELETE FROM signals')
                
                # Reset auto-increment
                cursor.execute('DELETE FROM sqlite_sequence WHERE name="signals"')
                
                conn.commit()
                
                logger.info(f"Cleared {count_before} signals from database")
                
                return {
                    'success': True,
                    'message': f'Cleared {count_before} signals',
                    'count_cleared': count_before
                }
                
        except Exception as e:
            logger.error(f"Error clearing signals: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def add_signal(self, signal_data: Dict) -> Dict:
        """Add new signal to database"""
        try:
            signal_id = signal_data.get('signal_id', f"signal_{signal_data.get('symbol')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO signals 
                    (signal_id, symbol, strategy, signal_type, entry_price, target_price, 
                     stop_loss, confidence, current_price, status, created_at, updated_at, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    signal_id,
                    signal_data.get('symbol'),
                    signal_data.get('strategy'),
                    signal_data.get('signal_type', 'BUY'),
                    signal_data.get('entry_price'),
                    signal_data.get('target_price'),
                    signal_data.get('stop_loss'),
                    signal_data.get('confidence', 0.0),
                    signal_data.get('current_price', signal_data.get('entry_price')),
                    'active',
                    datetime.now().isoformat(),
                    datetime.now().isoformat(),
                    json.dumps(signal_data.get('metadata', {}))
                ))
                
                conn.commit()
                
                logger.info(f"Added signal for {signal_data.get('symbol')} - {signal_data.get('strategy')}")
                
                return {
                    'success': True,
                    'signal_id': signal_id,
                    'message': 'Signal added successfully'
                }
                
        except Exception as e:
            logger.error(f"Error adding signal: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def update_signal_prices(self, price_updates: Dict[str, float]) -> Dict:
        """Update current prices for active signals"""
        try:
            updated_count = 0
            target_hits = []
            stop_losses = []
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get active signals
                cursor.execute('''
                    SELECT signal_id, symbol, entry_price, target_price, stop_loss, max_price, min_price
                    FROM signals 
                    WHERE status = 'active'
                ''')
                
                active_signals = cursor.fetchall()
                
                for signal in active_signals:
                    signal_id, symbol, entry_price, target_price, stop_loss, max_price, min_price = signal
                    
                    if symbol not in price_updates:
                        continue
                    
                    current_price = price_updates[symbol]
                    new_max_price = max(max_price or 0, current_price)
                    new_min_price = min(min_price or float('inf'), current_price) if min_price else current_price
                    
                    # Calculate days active
                    cursor.execute('SELECT created_at FROM signals WHERE signal_id = ?', (signal_id,))
                    created_at = cursor.fetchone()[0]
                    created_date = datetime.fromisoformat(created_at)
                    days_active = (datetime.now() - created_date).days
                    
                    # Update current price and tracking data
                    cursor.execute('''
                        UPDATE signals 
                        SET current_price = ?, max_price = ?, min_price = ?, 
                            days_active = ?, updated_at = ?
                        WHERE signal_id = ?
                    ''', (current_price, new_max_price, new_min_price, days_active, 
                          datetime.now().isoformat(), signal_id))
                    
                    updated_count += 1
                    
                    # Check for target hit
                    if current_price >= target_price:
                        profit = current_price - entry_price
                        profit_percent = (profit / entry_price) * 100
                        
                        cursor.execute('''
                            UPDATE signals 
                            SET status = 'target_hit', target_hit_at = ?, 
                                profit_loss = ?, profit_loss_percent = ?
                            WHERE signal_id = ?
                        ''', (datetime.now().isoformat(), profit, profit_percent, signal_id))
                        
                        target_hits.append({
                            'signal_id': signal_id,
                            'symbol': symbol,
                            'entry_price': entry_price,
                            'target_price': target_price,
                            'current_price': current_price,
                            'profit_percent': profit_percent
                        })
                    
                    # Check for stop loss hit
                    elif current_price <= stop_loss:
                        loss = current_price - entry_price
                        loss_percent = (loss / entry_price) * 100
                        
                        cursor.execute('''
                            UPDATE signals 
                            SET status = 'stop_loss_hit', stop_loss_hit_at = ?, 
                                profit_loss = ?, profit_loss_percent = ?
                            WHERE signal_id = ?
                        ''', (datetime.now().isoformat(), loss, loss_percent, signal_id))
                        
                        stop_losses.append({
                            'signal_id': signal_id,
                            'symbol': symbol,
                            'entry_price': entry_price,
                            'stop_loss': stop_loss,
                            'current_price': current_price,
                            'loss_percent': loss_percent
                        })
                
                conn.commit()
                
                return {
                    'success': True,
                    'updated_count': updated_count,
                    'target_hits': target_hits,
                    'stop_losses': stop_losses
                }
                
        except Exception as e:
            logger.error(f"Error updating signal prices: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_signal_statistics(self) -> Dict:
        """Get comprehensive signal statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Overall statistics
                cursor.execute('''
                    SELECT 
                        COUNT(*) as total_signals,
                        COUNT(CASE WHEN status = 'active' THEN 1 END) as active_signals,
                        COUNT(CASE WHEN status = 'target_hit' THEN 1 END) as target_hits,
                        COUNT(CASE WHEN status = 'stop_loss_hit' THEN 1 END) as stop_losses,
                        AVG(CASE WHEN status = 'target_hit' THEN profit_loss_percent END) as avg_profit,
                        AVG(CASE WHEN status = 'stop_loss_hit' THEN profit_loss_percent END) as avg_loss,
                        SUM(CASE WHEN status IN ('target_hit', 'stop_loss_hit') THEN profit_loss ELSE 0 END) as total_pnl
                    FROM signals
                ''')
                
                overall_stats = cursor.fetchone()
                
                # Strategy-wise statistics
                cursor.execute('''
                    SELECT 
                        strategy,
                        COUNT(*) as total,
                        COUNT(CASE WHEN status = 'target_hit' THEN 1 END) as hits,
                        COUNT(CASE WHEN status = 'stop_loss_hit' THEN 1 END) as losses,
                        AVG(CASE WHEN status = 'target_hit' THEN profit_loss_percent END) as avg_profit
                    FROM signals
                    GROUP BY strategy
                    ORDER BY total DESC
                ''')
                
                strategy_stats = cursor.fetchall()
                
                # Recent signals (last 7 days)
                cursor.execute('''
                    SELECT COUNT(*) 
                    FROM signals 
                    WHERE created_at >= datetime('now', '-7 days')
                ''')
                
                recent_signals = cursor.fetchone()[0]
                
                return {
                    'success': True,
                    'overall': {
                        'total_signals': overall_stats[0] or 0,
                        'active_signals': overall_stats[1] or 0,
                        'target_hits': overall_stats[2] or 0,
                        'stop_losses': overall_stats[3] or 0,
                        'success_rate': (overall_stats[2] / overall_stats[0] * 100) if overall_stats[0] > 0 else 0,
                        'avg_profit_percent': overall_stats[4] or 0,
                        'avg_loss_percent': overall_stats[5] or 0,
                        'total_pnl': overall_stats[6] or 0,
                        'recent_signals_7d': recent_signals
                    },
                    'by_strategy': [
                        {
                            'strategy': row[0],
                            'total': row[1],
                            'target_hits': row[2],
                            'stop_losses': row[3],
                            'success_rate': (row[2] / row[1] * 100) if row[1] > 0 else 0,
                            'avg_profit_percent': row[4] or 0
                        }
                        for row in strategy_stats
                    ]
                }
                
        except Exception as e:
            logger.error(f"Error getting signal statistics: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_active_signals(self) -> Dict:
        """Get all active signals"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT signal_id, symbol, strategy, signal_type, entry_price, 
                           target_price, stop_loss, confidence, current_price, 
                           created_at, days_active, max_price, min_price
                    FROM signals 
                    WHERE status = 'active'
                    ORDER BY created_at DESC
                ''')
                
                signals = cursor.fetchall()
                columns = [description[0] for description in cursor.description]
                
                active_signals = []
                for row in signals:
                    signal_dict = dict(zip(columns, row))
                    
                    # Calculate unrealized P&L
                    if signal_dict['current_price'] and signal_dict['entry_price']:
                        unrealized_pnl = ((signal_dict['current_price'] - signal_dict['entry_price']) / 
                                        signal_dict['entry_price']) * 100
                        signal_dict['unrealized_pnl_percent'] = unrealized_pnl
                    
                    active_signals.append(signal_dict)
                
                return {
                    'success': True,
                    'signals': active_signals,
                    'count': len(active_signals)
                }
                
        except Exception as e:
            logger.error(f"Error getting active signals: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_all_signals(self, limit: int = 100) -> Dict:
        """Get all signals (active and completed)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT signal_id, symbol, strategy, signal_type, entry_price, 
                           target_price, stop_loss, confidence, current_price, 
                           status, created_at, updated_at, target_hit_at, 
                           stop_loss_hit_at, profit_loss_percent, days_active
                    FROM signals 
                    ORDER BY created_at DESC
                    LIMIT ?
                ''', (limit,))
                
                signals = cursor.fetchall()
                columns = [description[0] for description in cursor.description]
                
                all_signals = []
                for row in signals:
                    signal_dict = dict(zip(columns, row))
                    
                    # Calculate unrealized P&L for active signals
                    if signal_dict['status'] == 'active' and signal_dict['current_price'] and signal_dict['entry_price']:
                        unrealized_pnl = ((signal_dict['current_price'] - signal_dict['entry_price']) / 
                                        signal_dict['entry_price']) * 100
                        signal_dict['unrealized_pnl_percent'] = unrealized_pnl
                    else:
                        signal_dict['unrealized_pnl_percent'] = signal_dict.get('profit_loss_percent', 0)
                    
                    all_signals.append(signal_dict)
                
                return {
                    'success': True,
                    'signals': all_signals,
                    'count': len(all_signals)
                }
                
        except Exception as e:
            logger.error(f"Error getting all signals: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def fetch_current_prices(self, symbols: List[str]) -> Dict[str, float]:
        """Fetch current prices for given symbols"""
        try:
            prices = {}
            
            # Use yfinance to get current prices
            for symbol in symbols:
                try:
                    ticker = yf.Ticker(f"{symbol}.NS")  # NSE suffix
                    hist = ticker.history(period="1d")
                    
                    if not hist.empty:
                        prices[symbol] = float(hist['Close'].iloc[-1])
                    
                except Exception as e:
                    logger.warning(f"Could not fetch price for {symbol}: {e}")
                    continue
            
            return prices
            
        except Exception as e:
            logger.error(f"Error fetching current prices: {e}")
            return {}

# Global instance
signal_manager = SignalManagementService()
