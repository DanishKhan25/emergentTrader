#!/usr/bin/env python3
"""
Historical Signal Data Collector
Collect and process historical signals for ML training
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf
import sqlite3
from typing import List, Dict

class HistoricalDataCollector:
    """Collect historical signals and calculate their outcomes"""
    
    def __init__(self, db_path: str = "data/signals.db"):
        self.db_path = db_path
    
    def collect_historical_signals(self, months_back: int = 6) -> pd.DataFrame:
        """Collect historical signals from database"""
        
        conn = sqlite3.connect(self.db_path)
        
        # Get signals from last N months
        query = """
            SELECT signal_id, symbol, strategy, signal_type, 
                   entry_price, target_price, stop_loss, confidence,
                   generated_at, metadata
            FROM signals 
            WHERE generated_at >= date('now', '-{} months')
            ORDER BY generated_at DESC
        """.format(months_back)
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        return df
    
    def calculate_historical_outcomes(self, signals_df: pd.DataFrame) -> pd.DataFrame:
        """Calculate outcomes for historical signals"""
        
        results = []
        
        for _, signal in signals_df.iterrows():
            try:
                # Calculate outcome for this signal
                outcome_data = self.calculate_signal_outcome(signal)
                
                # Combine signal data with outcome
                result = signal.to_dict()
                result.update(outcome_data)
                results.append(result)
                
                print(f"Processed {signal['symbol']} ({signal['strategy']}): {'Success' if outcome_data['outcome'] else 'Failure'}")
                
            except Exception as e:
                print(f"Error processing {signal['symbol']}: {str(e)}")
                continue
        
        return pd.DataFrame(results)
    
    def calculate_signal_outcome(self, signal: pd.Series) -> Dict:
        """Calculate outcome for a single historical signal"""
        
        entry_date = pd.to_datetime(signal['generated_at']).date()
        end_date = entry_date + timedelta(days=30)  # 30-day tracking period
        
        # Get price data
        price_data = yf.download(
            f"{signal['symbol']}.NS",
            start=entry_date,
            end=end_date,
            progress=False
        )
        
        if price_data.empty:
            return {'outcome': 0, 'return_pct': 0, 'error': 'No price data'}
        
        entry_price = signal['entry_price']
        target_price = signal.get('target_price', entry_price * 1.1)
        stop_loss = signal.get('stop_loss', entry_price * 0.95)
        
        # Calculate outcome based on price movement
        if signal['signal_type'] == 'BUY':
            hit_target = (price_data['High'] >= target_price).any()
            hit_stop = (price_data['Low'] <= stop_loss).any()
        else:
            hit_target = (price_data['Low'] <= target_price).any()
            hit_stop = (price_data['High'] >= stop_loss).any()
        
        # Determine success/failure
        if hit_target and not hit_stop:
            outcome = 1
            exit_price = target_price
        elif hit_stop:
            outcome = 0
            exit_price = stop_loss
        else:
            final_price = price_data['Close'].iloc[-1]
            return_pct = (final_price - entry_price) / entry_price
            outcome = 1 if return_pct > 0.02 else 0
            exit_price = final_price
        
        return_pct = (exit_price - entry_price) / entry_price
        
        return {
            'outcome': outcome,
            'return_pct': return_pct,
            'exit_price': exit_price,
            'hit_target': hit_target,
            'hit_stop': hit_stop,
            'days_held': len(price_data)
        }
    
    def prepare_ml_training_data(self, signals_with_outcomes: pd.DataFrame) -> pd.DataFrame:
        """Prepare data for ML training"""
        
        # Add engineered features
        ml_data = signals_with_outcomes.copy()
        
        # Strategy encoding
        strategy_map = {
            'momentum': 0, 'low_volatility': 1, 'fundamental_growth': 2,
            'mean_reversion': 3, 'breakout': 4, 'value_investing': 5,
            'swing_trading': 6, 'multibagger': 7, 'sector_rotation': 8, 'pivot_cpr': 9
        }
        ml_data['strategy_encoded'] = ml_data['strategy'].map(strategy_map).fillna(0)
        
        # Time features
        ml_data['generated_at'] = pd.to_datetime(ml_data['generated_at'])
        ml_data['month'] = ml_data['generated_at'].dt.month
        ml_data['quarter'] = ml_data['generated_at'].dt.quarter
        ml_data['is_earnings_season'] = ml_data['month'].isin([1, 4, 7, 10]).astype(int)
        
        # Price features
        ml_data['entry_price_log'] = np.log(ml_data['entry_price'])
        
        # Confidence features
        ml_data['high_confidence'] = (ml_data['confidence'] > 0.7).astype(int)
        
        # Add market context (you'll need to implement this)
        ml_data = self.add_market_context(ml_data)
        
        return ml_data
    
    def add_market_context(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add market context features"""
        
        # Get NIFTY data for market context
        nifty_data = yf.download("^NSEI", start="2023-01-01", progress=False)
        
        # Calculate market features for each signal date
        market_features = []
        
        for _, row in df.iterrows():
            signal_date = row['generated_at'].date()
            
            # Get market data around signal date
            market_slice = nifty_data[nifty_data.index.date <= signal_date].tail(50)
            
            if len(market_slice) > 20:
                # Calculate market volatility
                returns = market_slice['Close'].pct_change()
                volatility = returns.rolling(20).std().iloc[-1] * np.sqrt(252)
                
                # Calculate market momentum
                momentum_20d = (market_slice['Close'].iloc[-1] / market_slice['Close'].iloc[-21] - 1)
                
                # Market regime
                sma_20 = market_slice['Close'].rolling(20).mean().iloc[-1]
                sma_50 = market_slice['Close'].rolling(50).mean().iloc[-1] if len(market_slice) >= 50 else sma_20
                
                current_price = market_slice['Close'].iloc[-1]
                
                if current_price > sma_20 > sma_50:
                    regime = 'BULL'
                elif current_price < sma_20 < sma_50:
                    regime = 'BEAR'
                else:
                    regime = 'SIDEWAYS'
            else:
                volatility = 0.2
                momentum_20d = 0.0
                regime = 'SIDEWAYS'
            
            market_features.append({
                'market_volatility': volatility,
                'market_momentum': momentum_20d,
                'market_regime': regime,
                'bull_market': 1 if regime == 'BULL' else 0,
                'bear_market': 1 if regime == 'BEAR' else 0
            })
        
        # Add market features to dataframe
        market_df = pd.DataFrame(market_features)
        return pd.concat([df.reset_index(drop=True), market_df], axis=1)

# Usage example
if __name__ == "__main__":
    collector = HistoricalDataCollector()
    
    # Collect historical signals
    historical_signals = collector.collect_historical_signals(months_back=6)
    print(f"Collected {len(historical_signals)} historical signals")
    
    # Calculate outcomes
    signals_with_outcomes = collector.calculate_historical_outcomes(historical_signals)
    print(f"Calculated outcomes for {len(signals_with_outcomes)} signals")
    
    # Prepare ML training data
    ml_training_data = collector.prepare_ml_training_data(signals_with_outcomes)
    
    # Save training data
    ml_training_data.to_csv('ml_training_data.csv', index=False)
    print(f"ML training data saved: {len(ml_training_data)} samples")
    print(f"Success rate: {ml_training_data['outcome'].mean():.1%}")
