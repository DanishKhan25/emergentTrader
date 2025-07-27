"""
Database models and connection for EmergentTrader
Uses SQLite for local development, easily upgradeable to PostgreSQL/MySQL
"""

import sqlite3
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import logging
import os

logger = logging.getLogger(__name__)

# Database file path
DB_PATH = os.path.join(os.path.dirname(__file__), 'emergent_trader.db')

@dataclass
class Position:
    id: str
    symbol: str
    strategy: str
    quantity: int
    entry_price: float
    current_price: float
    invested: float
    current_value: float
    pnl: float
    pnl_percent: float
    entry_date: str
    target_price: float
    stop_loss: float
    status: str
    position_type: str
    notes: str
    created_at: str
    updated_at: str

@dataclass
class WatchlistItem:
    id: str
    symbol: str
    name: str
    sector: str
    current_price: float
    change: float
    change_percent: float
    volume: int
    market_cap: Optional[float]
    added_date: str
    notes: str
    alerts: str  # JSON string of alert conditions
    created_at: str
    updated_at: str

@dataclass
class Signal:
    id: str
    signal_id: str
    symbol: str
    strategy: str
    signal_type: str
    confidence: float
    price: float
    target_price: float
    stop_loss: float
    generated_at: str
    expires_at: Optional[str]
    status: str
    metadata: str  # JSON string
    created_at: str
    updated_at: str

@dataclass
class PortfolioFunds:
    id: int
    total_funds: float
    available_funds: float
    invested_funds: float
    last_updated: str

class DatabaseManager:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        return conn
    
    def init_database(self):
        """Initialize database with all required tables"""
        conn = self.get_connection()
        try:
            # Create positions table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS positions (
                    id TEXT PRIMARY KEY,
                    symbol TEXT NOT NULL,
                    strategy TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    entry_price REAL NOT NULL,
                    current_price REAL NOT NULL,
                    invested REAL NOT NULL,
                    current_value REAL NOT NULL,
                    pnl REAL NOT NULL,
                    pnl_percent REAL NOT NULL,
                    entry_date TEXT NOT NULL,
                    target_price REAL,
                    stop_loss REAL,
                    status TEXT DEFAULT 'active',
                    position_type TEXT DEFAULT 'manual',
                    notes TEXT DEFAULT '',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            ''')
            
            # Create watchlist table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS watchlist (
                    id TEXT PRIMARY KEY,
                    symbol TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    sector TEXT,
                    current_price REAL DEFAULT 0,
                    change REAL DEFAULT 0,
                    change_percent REAL DEFAULT 0,
                    volume INTEGER DEFAULT 0,
                    market_cap REAL,
                    added_date TEXT NOT NULL,
                    notes TEXT DEFAULT '',
                    alerts TEXT DEFAULT '{}',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            ''')
            
            # Create signals table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS signals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    signal_id TEXT UNIQUE NOT NULL,
                    symbol TEXT NOT NULL,
                    strategy TEXT NOT NULL,
                    signal_type TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    price REAL,
                    target_price REAL,
                    stop_loss REAL,
                    generated_at TEXT NOT NULL,
                    expires_at TEXT,
                    status TEXT DEFAULT 'ACTIVE',
                    metadata TEXT DEFAULT '{}',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            ''')
            
            # Create portfolio_funds table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS portfolio_funds (
                    id INTEGER PRIMARY KEY,
                    total_funds REAL NOT NULL,
                    available_funds REAL NOT NULL,
                    invested_funds REAL NOT NULL,
                    last_updated TEXT NOT NULL
                )
            ''')
            
            # Create indexes for better performance
            conn.execute('CREATE INDEX IF NOT EXISTS idx_positions_symbol ON positions(symbol)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_positions_status ON positions(status)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_watchlist_symbol ON watchlist(symbol)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_signals_symbol ON signals(symbol)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_signals_status ON signals(status)')
            
            # Initialize default funds if not exists
            funds_count = conn.execute('SELECT COUNT(*) FROM portfolio_funds').fetchone()[0]
            if funds_count == 0:
                conn.execute('''
                    INSERT INTO portfolio_funds (id, total_funds, available_funds, invested_funds, last_updated)
                    VALUES (1, 1000000, 1000000, 0, ?)
                ''', (datetime.now().isoformat(),))
            
            conn.commit()
            logger.info(f"Database initialized successfully at {self.db_path}")
            
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()
    
    # Position methods
    def add_position(self, position_data: Dict) -> Position:
        """Add a new position to database"""
        conn = self.get_connection()
        try:
            position_id = position_data.get('id', str(uuid.uuid4()))
            now = datetime.now().isoformat()
            
            position = Position(
                id=position_id,
                symbol=position_data['symbol'].upper(),
                strategy=position_data['strategy'],
                quantity=int(position_data['quantity']),
                entry_price=float(position_data['entry_price']),
                current_price=float(position_data.get('current_price', position_data['entry_price'])),
                invested=float(position_data['invested']),
                current_value=float(position_data.get('current_value', position_data['invested'])),
                pnl=float(position_data.get('pnl', 0)),
                pnl_percent=float(position_data.get('pnl_percent', 0)),
                entry_date=position_data.get('entry_date', now),
                target_price=float(position_data.get('target_price', 0)),
                stop_loss=float(position_data.get('stop_loss', 0)),
                status=position_data.get('status', 'active'),
                position_type=position_data.get('type', 'manual'),
                notes=position_data.get('notes', ''),
                created_at=now,
                updated_at=now
            )
            
            conn.execute('''
                INSERT INTO positions (
                    id, symbol, strategy, quantity, entry_price, current_price,
                    invested, current_value, pnl, pnl_percent, entry_date,
                    target_price, stop_loss, status, position_type, notes,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                position.id, position.symbol, position.strategy, position.quantity,
                position.entry_price, position.current_price, position.invested,
                position.current_value, position.pnl, position.pnl_percent,
                position.entry_date, position.target_price, position.stop_loss,
                position.status, position.position_type, position.notes,
                position.created_at, position.updated_at
            ))
            
            conn.commit()
            logger.info(f"Added position {position.symbol} to database")
            return position
            
        except Exception as e:
            logger.error(f"Error adding position: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def get_positions(self, status: str = None) -> List[Position]:
        """Get all positions from database"""
        conn = self.get_connection()
        try:
            if status:
                cursor = conn.execute('SELECT * FROM positions WHERE status = ? ORDER BY created_at DESC', (status,))
            else:
                cursor = conn.execute('SELECT * FROM positions ORDER BY created_at DESC')
            
            positions = []
            for row in cursor.fetchall():
                positions.append(Position(**dict(row)))
            
            return positions
            
        except Exception as e:
            logger.error(f"Error getting positions: {e}")
            return []
        finally:
            conn.close()
    
    def update_position(self, position_id: str, updates: Dict) -> bool:
        """Update position in database"""
        conn = self.get_connection()
        try:
            updates['updated_at'] = datetime.now().isoformat()
            
            # Build dynamic update query
            set_clause = ', '.join([f"{key} = ?" for key in updates.keys()])
            values = list(updates.values()) + [position_id]
            
            conn.execute(f'UPDATE positions SET {set_clause} WHERE id = ?', values)
            conn.commit()
            
            return conn.total_changes > 0
            
        except Exception as e:
            logger.error(f"Error updating position {position_id}: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def delete_position(self, position_id: str) -> bool:
        """Delete position from database"""
        conn = self.get_connection()
        try:
            conn.execute('DELETE FROM positions WHERE id = ?', (position_id,))
            conn.commit()
            return conn.total_changes > 0
        except Exception as e:
            logger.error(f"Error deleting position {position_id}: {e}")
            return False
        finally:
            conn.close()
    
    # Watchlist methods
    def add_to_watchlist(self, symbol: str, name: str = None, sector: str = None, notes: str = '') -> WatchlistItem:
        """Add symbol to watchlist"""
        conn = self.get_connection()
        try:
            now = datetime.now().isoformat()
            
            watchlist_item = WatchlistItem(
                id=str(uuid.uuid4()),
                symbol=symbol.upper(),
                name=name or symbol,
                sector=sector or '',
                current_price=0,
                change=0,
                change_percent=0,
                volume=0,
                market_cap=None,
                added_date=now,
                notes=notes,
                alerts='{}',
                created_at=now,
                updated_at=now
            )
            
            conn.execute('''
                INSERT OR REPLACE INTO watchlist (
                    id, symbol, name, sector, current_price, change, change_percent,
                    volume, market_cap, added_date, notes, alerts, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                watchlist_item.id, watchlist_item.symbol, watchlist_item.name,
                watchlist_item.sector, watchlist_item.current_price, watchlist_item.change,
                watchlist_item.change_percent, watchlist_item.volume, watchlist_item.market_cap,
                watchlist_item.added_date, watchlist_item.notes, watchlist_item.alerts,
                watchlist_item.created_at, watchlist_item.updated_at
            ))
            
            conn.commit()
            logger.info(f"Added {symbol} to watchlist")
            return watchlist_item
            
        except Exception as e:
            logger.error(f"Error adding {symbol} to watchlist: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def get_watchlist(self) -> List[WatchlistItem]:
        """Get all watchlist items"""
        conn = self.get_connection()
        try:
            cursor = conn.execute('SELECT * FROM watchlist ORDER BY added_date DESC')
            watchlist = []
            for row in cursor.fetchall():
                watchlist.append(WatchlistItem(**dict(row)))
            return watchlist
        except Exception as e:
            logger.error(f"Error getting watchlist: {e}")
            return []
        finally:
            conn.close()
    
    def remove_from_watchlist(self, symbol: str) -> bool:
        """Remove symbol from watchlist"""
        conn = self.get_connection()
        try:
            conn.execute('DELETE FROM watchlist WHERE symbol = ?', (symbol.upper(),))
            conn.commit()
            return conn.total_changes > 0
        except Exception as e:
            logger.error(f"Error removing {symbol} from watchlist: {e}")
            return False
        finally:
            conn.close()
    
    def update_watchlist_prices(self, price_updates: Dict[str, Dict]) -> int:
        """Update prices for watchlist items"""
        conn = self.get_connection()
        updated_count = 0
        try:
            for symbol, price_data in price_updates.items():
                conn.execute('''
                    UPDATE watchlist SET 
                        current_price = ?, change = ?, change_percent = ?,
                        volume = ?, market_cap = ?, updated_at = ?
                    WHERE symbol = ?
                ''', (
                    price_data.get('price', 0),
                    price_data.get('change', 0),
                    price_data.get('change_percent', 0),
                    price_data.get('volume', 0),
                    price_data.get('market_cap'),
                    datetime.now().isoformat(),
                    symbol.upper()
                ))
                if conn.total_changes > 0:
                    updated_count += 1
            
            conn.commit()
            return updated_count
        except Exception as e:
            logger.error(f"Error updating watchlist prices: {e}")
            conn.rollback()
            return 0
        finally:
            conn.close()
    
    # Portfolio funds methods
    def get_portfolio_funds(self) -> PortfolioFunds:
        """Get portfolio funds"""
        conn = self.get_connection()
        try:
            cursor = conn.execute('SELECT * FROM portfolio_funds WHERE id = 1')
            row = cursor.fetchone()
            if row:
                return PortfolioFunds(**dict(row))
            else:
                # Create default funds
                return self.reset_portfolio_funds()
        except Exception as e:
            logger.error(f"Error getting portfolio funds: {e}")
            return self.reset_portfolio_funds()
        finally:
            conn.close()
    
    def update_portfolio_funds(self, funds_data: Dict) -> bool:
        """Update portfolio funds"""
        conn = self.get_connection()
        try:
            conn.execute('''
                UPDATE portfolio_funds SET 
                    total_funds = ?, available_funds = ?, invested_funds = ?, last_updated = ?
                WHERE id = 1
            ''', (
                funds_data['total_funds'],
                funds_data['available_funds'],
                funds_data['invested_funds'],
                datetime.now().isoformat()
            ))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error updating portfolio funds: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def reset_portfolio_funds(self, total_funds: float = 1000000) -> PortfolioFunds:
        """Reset portfolio funds to default"""
        conn = self.get_connection()
        try:
            now = datetime.now().isoformat()
            funds = PortfolioFunds(
                id=1,
                total_funds=total_funds,
                available_funds=total_funds,
                invested_funds=0,
                last_updated=now
            )
            
            conn.execute('''
                INSERT OR REPLACE INTO portfolio_funds (id, total_funds, available_funds, invested_funds, last_updated)
                VALUES (?, ?, ?, ?, ?)
            ''', (funds.id, funds.total_funds, funds.available_funds, funds.invested_funds, funds.last_updated))
            
            conn.commit()
            return funds
        except Exception as e:
            logger.error(f"Error resetting portfolio funds: {e}")
            raise
        finally:
            conn.close()
    
    # Signal methods
    def add_signal(self, signal_data: Dict) -> bool:
        """Add signal to database"""
        conn = self.get_connection()
        try:
            now = datetime.now().isoformat()
            
            conn.execute('''
                INSERT INTO signals (
                    signal_id, symbol, strategy, signal_type, confidence, price,
                    target_price, stop_loss, generated_at, expires_at, status,
                    metadata, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                signal_data['signal_id'],
                signal_data['symbol'].upper(),
                signal_data['strategy'],
                signal_data['signal_type'],
                signal_data['confidence'],
                signal_data.get('price'),
                signal_data.get('target_price'),
                signal_data.get('stop_loss'),
                signal_data['generated_at'],
                signal_data.get('expires_at'),
                signal_data.get('status', 'ACTIVE'),
                json.dumps(signal_data.get('metadata', {})),
                now,
                now
            ))
            
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error adding signal: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def get_signals(self, status: str = None, limit: int = None) -> List[Dict]:
        """Get signals from database"""
        conn = self.get_connection()
        try:
            query = 'SELECT * FROM signals'
            params = []
            
            if status:
                query += ' WHERE status = ?'
                params.append(status)
            
            query += ' ORDER BY created_at DESC'
            
            if limit:
                query += ' LIMIT ?'
                params.append(limit)
            
            cursor = conn.execute(query, params)
            signals = []
            
            for row in cursor.fetchall():
                signal_dict = dict(row)
                # Parse metadata JSON
                try:
                    signal_dict['metadata'] = json.loads(signal_dict['metadata'])
                except:
                    signal_dict['metadata'] = {}
                signals.append(signal_dict)
            
            return signals
        except Exception as e:
            logger.error(f"Error getting signals: {e}")
            return []
        finally:
            conn.close()
    
    def clear_old_signals(self, days: int = 7) -> int:
        """Clear signals older than specified days"""
        conn = self.get_connection()
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            cursor = conn.execute('DELETE FROM signals WHERE created_at < ?', (cutoff_date,))
            conn.commit()
            return cursor.rowcount
        except Exception as e:
            logger.error(f"Error clearing old signals: {e}")
            return 0
        finally:
            conn.close()

# Global database instance
db = DatabaseManager()
