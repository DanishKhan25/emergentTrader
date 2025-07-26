#!/usr/bin/env python3
"""
Real Signal Outcome Tracker
Track actual outcomes of trading signals for ML training
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List
import sqlite3

class SignalOutcomeTracker:
    """Track real outcomes of trading signals"""
    
    def __init__(self, db_path: str = "data/signals.db"):
        self.db_path = db_path
        self.setup_outcome_table()
    
    def setup_outcome_table(self):
        """Create outcome tracking table"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS signal_outcomes (
                signal_id TEXT PRIMARY KEY,
                symbol TEXT,
                strategy TEXT,
                entry_date DATE,
                entry_price REAL,
                target_price REAL,
                stop_loss REAL,
                confidence REAL,
                
                -- Outcome data
                outcome INTEGER,  -- 1=success, 0=failure
                exit_price REAL,
                exit_date DATE,
                return_pct REAL,
                days_held INTEGER,
                hit_target BOOLEAN,
                hit_stop BOOLEAN,
                max_gain REAL,
                max_loss REAL,
                
                -- ML features at signal time
                rsi REAL,
                macd REAL,
                volume_ratio REAL,
                market_regime TEXT,
                market_volatility REAL,
                
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def track_signal_outcome(self, signal_id: str, days_to_track: int = 30) -> Dict:
        """Track outcome of a specific signal"""
        
        # Get signal details from database
        signal = self.get_signal_details(signal_id)
        if not signal:
            return {"error": "Signal not found"}
        
        # Get price data after signal date
        end_date = signal['entry_date'] + timedelta(days=days_to_track)
        
        try:
            price_data = yf.download(
                f"{signal['symbol']}.NS",
                start=signal['entry_date'],
                end=end_date,
                progress=False
            )
            
            if price_data.empty:
                return {"error": "No price data available"}
            
            # Calculate outcome
            outcome_data = self.calculate_outcome(signal, price_data)
            
            # Save outcome to database
            self.save_outcome(signal_id, outcome_data)
            
            return outcome_data
            
        except Exception as e:
            return {"error": str(e)}
    
    def calculate_outcome(self, signal: Dict, price_data: pd.DataFrame) -> Dict:
        """Calculate signal outcome based on price movement"""
        
        entry_price = signal['entry_price']
        target_price = signal.get('target_price', entry_price * 1.1)  # 10% default
        stop_loss = signal.get('stop_loss', entry_price * 0.95)       # 5% default
        
        # Track price movement
        max_price = price_data['High'].max()
        min_price = price_data['Low'].min()
        final_price = price_data['Close'].iloc[-1]
        
        # Calculate gains/losses
        max_gain = (max_price - entry_price) / entry_price
        max_loss = (min_price - entry_price) / entry_price
        final_return = (final_price - entry_price) / entry_price
        
        # Determine if target or stop was hit
        if signal['signal_type'] == 'BUY':
            hit_target = (price_data['High'] >= target_price).any()
            hit_stop = (price_data['Low'] <= stop_loss).any()
        else:  # SELL signal
            hit_target = (price_data['Low'] <= target_price).any()
            hit_stop = (price_data['High'] >= stop_loss).any()
        
        # Determine overall outcome
        if hit_target and not hit_stop:
            outcome = 1  # Success
            exit_price = target_price
        elif hit_stop:
            outcome = 0  # Failure
            exit_price = stop_loss
        else:
            # Neither hit - judge by final return
            outcome = 1 if final_return > 0.02 else 0  # 2% threshold
            exit_price = final_price
        
        return {
            'outcome': outcome,
            'exit_price': exit_price,
            'exit_date': price_data.index[-1].date(),
            'return_pct': final_return,
            'days_held': len(price_data),
            'hit_target': hit_target,
            'hit_stop': hit_stop,
            'max_gain': max_gain,
            'max_loss': max_loss
        }
    
    def get_signal_details(self, signal_id: str) -> Dict:
        """Get signal details from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM signals WHERE signal_id = ?
        """, (signal_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            # Convert to dictionary (implement based on your schema)
            return {
                'signal_id': result[0],
                'symbol': result[1],
                'strategy': result[2],
                'entry_date': datetime.fromisoformat(result[3]).date(),
                'entry_price': result[4],
                'signal_type': result[5],
                'confidence': result[6]
            }
        return None
    
    def save_outcome(self, signal_id: str, outcome_data: Dict):
        """Save outcome data to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO signal_outcomes 
            (signal_id, outcome, exit_price, exit_date, return_pct, 
             days_held, hit_target, hit_stop, max_gain, max_loss)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            signal_id,
            outcome_data['outcome'],
            outcome_data['exit_price'],
            outcome_data['exit_date'],
            outcome_data['return_pct'],
            outcome_data['days_held'],
            outcome_data['hit_target'],
            outcome_data['hit_stop'],
            outcome_data['max_gain'],
            outcome_data['max_loss']
        ))
        
        conn.commit()
        conn.close()
    
    def get_training_data(self, days_back: int = 180) -> pd.DataFrame:
        """Get signals with outcomes for ML training"""
        conn = sqlite3.connect(self.db_path)
        
        query = """
            SELECT s.*, so.outcome, so.return_pct, so.days_held
            FROM signals s
            JOIN signal_outcomes so ON s.signal_id = so.signal_id
            WHERE s.generated_at >= date('now', '-{} days')
        """.format(days_back)
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        return df

# Usage example
if __name__ == "__main__":
    tracker = SignalOutcomeTracker()
    
    # Track outcome of a specific signal
    result = tracker.track_signal_outcome("signal_123", days_to_track=30)
    print(f"Outcome: {result}")
    
    # Get training data
    training_data = tracker.get_training_data(days_back=90)
    print(f"Training data: {len(training_data)} signals with outcomes")
