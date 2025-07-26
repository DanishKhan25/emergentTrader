#!/usr/bin/env python3
"""
Outcome Tracking System
Calculate actual returns for each historical signal
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf
import pickle
from typing import Dict, List, Optional
import logging

# Add the python_backend directory to the path
try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
except NameError:
    parent_dir = os.getcwd()

sys.path.append(parent_dir)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OutcomeTracker:
    """Track actual outcomes for historical trading signals"""
    
    def __init__(self):
        self.holding_periods = [5, 10, 15, 30, 60]  # Days to track
        
        # Create directories
        os.makedirs('ml/data', exist_ok=True)
        
        logger.info("Outcome tracker initialized")
    
    def calculate_signal_outcome(self, signal: Dict, holding_days: int = 30) -> Dict:
        """Calculate actual outcome for a single signal"""
        try:
            symbol = signal['symbol']
            entry_date = pd.to_datetime(signal['generated_date'])
            entry_price = signal['entry_price']
            
            # Add .NS suffix for NSE stocks
            yf_symbol = f"{symbol}.NS"
            
            # Get price data for the holding period
            start_date = entry_date
            end_date = entry_date + timedelta(days=holding_days + 10)  # Buffer for weekends
            
            stock_data = yf.download(yf_symbol, start=start_date, end=end_date, progress=False)
            
            if stock_data.empty or len(stock_data) < 2:
                return self._default_outcome(signal, holding_days)
            
            # Find the actual entry price (next trading day after signal)
            actual_entry_price = stock_data['Open'].iloc[1] if len(stock_data) > 1 else entry_price
            
            # Calculate outcomes for different time horizons
            outcomes = {}
            
            for days in self.holding_periods:
                if days <= holding_days:
                    outcome = self._calculate_period_outcome(
                        stock_data, actual_entry_price, days, signal
                    )
                    outcomes[f'{days}d'] = outcome
            
            # Primary outcome (30-day default)
            primary_outcome = outcomes.get('30d', outcomes.get('15d', outcomes.get('10d', {})))
            
            return {
                'symbol': symbol,
                'strategy': signal['strategy'],
                'entry_date': entry_date.strftime('%Y-%m-%d'),
                'entry_price': actual_entry_price,
                'original_confidence': signal.get('confidence', 0.5),
                
                # Primary outcome metrics
                'holding_days': holding_days,
                'exit_price': primary_outcome.get('exit_price', actual_entry_price),
                'return_pct': primary_outcome.get('return_pct', 0),
                'success': primary_outcome.get('success', 0),
                'max_gain_pct': primary_outcome.get('max_gain_pct', 0),
                'max_loss_pct': primary_outcome.get('max_loss_pct', 0),
                'volatility': primary_outcome.get('volatility', 0),
                'sharpe_ratio': primary_outcome.get('sharpe_ratio', 0),
                
                # Multi-period outcomes
                'outcomes_by_period': outcomes,
                
                # Risk metrics
                'max_drawdown': primary_outcome.get('max_drawdown', 0),
                'days_to_profit': primary_outcome.get('days_to_profit', holding_days),
                'profit_probability': primary_outcome.get('profit_probability', 0),
                
                # Signal quality metrics
                'signal_accuracy': 1 if primary_outcome.get('success', 0) else 0,
                'risk_adjusted_return': primary_outcome.get('risk_adjusted_return', 0)
            }
            
        except Exception as e:
            logger.error(f"Error calculating outcome for {signal.get('symbol', 'Unknown')}: {str(e)}")
            return self._default_outcome(signal, holding_days)
    
    def _calculate_period_outcome(self, stock_data: pd.DataFrame, entry_price: float, 
                                 holding_days: int, signal: Dict) -> Dict:
        """Calculate outcome for a specific holding period"""
        try:
            if len(stock_data) < holding_days:
                # Use available data if less than holding period
                exit_price = stock_data['Close'].iloc[-1]
                actual_days = len(stock_data) - 1
            else:
                exit_price = stock_data['Close'].iloc[holding_days]
                actual_days = holding_days
            
            # Basic return calculation
            return_pct = (exit_price - entry_price) / entry_price
            
            # Success criteria (2% profit threshold)
            success = 1 if return_pct > 0.02 else 0
            
            # Calculate max gain and loss during holding period
            period_data = stock_data.iloc[1:actual_days+1]  # Exclude entry day
            
            if not period_data.empty:
                max_price = period_data['High'].max()
                min_price = period_data['Low'].min()
                
                max_gain_pct = (max_price - entry_price) / entry_price
                max_loss_pct = (min_price - entry_price) / entry_price
                
                # Calculate volatility
                returns = period_data['Close'].pct_change().dropna()
                volatility = returns.std() * np.sqrt(252) if len(returns) > 1 else 0
                
                # Sharpe ratio (assuming risk-free rate of 6%)
                excess_return = return_pct - (0.06 * actual_days / 252)
                sharpe_ratio = excess_return / volatility if volatility > 0 else 0
                
                # Max drawdown
                cumulative_returns = (1 + returns).cumprod()
                rolling_max = cumulative_returns.expanding().max()
                drawdown = (cumulative_returns - rolling_max) / rolling_max
                max_drawdown = drawdown.min() if not drawdown.empty else 0
                
                # Days to profit
                profit_prices = period_data['Close'] > entry_price * 1.02
                days_to_profit = profit_prices.idxmax() if profit_prices.any() else actual_days
                if isinstance(days_to_profit, pd.Timestamp):
                    days_to_profit = (days_to_profit - period_data.index[0]).days
                
                # Profit probability (percentage of days in profit)
                profit_days = (period_data['Close'] > entry_price).sum()
                profit_probability = profit_days / len(period_data) if len(period_data) > 0 else 0
                
            else:
                max_gain_pct = max_loss_pct = return_pct
                volatility = 0
                sharpe_ratio = 0
                max_drawdown = 0
                days_to_profit = actual_days
                profit_probability = 1 if return_pct > 0 else 0
            
            # Risk-adjusted return
            risk_adjusted_return = return_pct / max(volatility, 0.01)  # Avoid division by zero
            
            return {
                'exit_price': exit_price,
                'return_pct': return_pct,
                'success': success,
                'max_gain_pct': max_gain_pct,
                'max_loss_pct': max_loss_pct,
                'volatility': volatility,
                'sharpe_ratio': sharpe_ratio,
                'max_drawdown': max_drawdown,
                'days_to_profit': days_to_profit,
                'profit_probability': profit_probability,
                'risk_adjusted_return': risk_adjusted_return,
                'actual_holding_days': actual_days
            }
            
        except Exception as e:
            logger.error(f"Error calculating period outcome: {str(e)}")
            return {
                'exit_price': entry_price,
                'return_pct': 0,
                'success': 0,
                'max_gain_pct': 0,
                'max_loss_pct': 0,
                'volatility': 0,
                'sharpe_ratio': 0,
                'max_drawdown': 0,
                'days_to_profit': holding_days,
                'profit_probability': 0,
                'risk_adjusted_return': 0,
                'actual_holding_days': holding_days
            }
    
    def _default_outcome(self, signal: Dict, holding_days: int) -> Dict:
        """Default outcome when data is unavailable"""
        return {
            'symbol': signal.get('symbol', ''),
            'strategy': signal.get('strategy', ''),
            'entry_date': signal.get('generated_date', ''),
            'entry_price': signal.get('entry_price', 0),
            'original_confidence': signal.get('confidence', 0.5),
            'holding_days': holding_days,
            'exit_price': signal.get('entry_price', 0),
            'return_pct': 0,
            'success': 0,
            'max_gain_pct': 0,
            'max_loss_pct': 0,
            'volatility': 0,
            'sharpe_ratio': 0,
            'outcomes_by_period': {},
            'max_drawdown': 0,
            'days_to_profit': holding_days,
            'profit_probability': 0,
            'signal_accuracy': 0,
            'risk_adjusted_return': 0
        }
    
    def track_batch_outcomes(self, signals_df: pd.DataFrame, 
                           holding_days: int = 30) -> pd.DataFrame:
        """Track outcomes for a batch of signals"""
        logger.info(f"Tracking outcomes for {len(signals_df)} signals...")
        
        outcomes = []
        
        for idx, signal in signals_df.iterrows():
            try:
                outcome = self.calculate_signal_outcome(signal.to_dict(), holding_days)
                outcomes.append(outcome)
                
                # Progress update
                if len(outcomes) % 50 == 0:
                    logger.info(f"Processed {len(outcomes)}/{len(signals_df)} signals...")
                    
            except Exception as e:
                logger.error(f"Error processing signal {idx}: {str(e)}")
                continue
        
        outcomes_df = pd.DataFrame(outcomes)
        
        logger.info(f"Outcome tracking complete: {len(outcomes_df)} outcomes calculated")
        
        return outcomes_df
    
    def analyze_outcomes(self, outcomes_df: pd.DataFrame) -> Dict:
        """Analyze overall outcome statistics"""
        try:
            analysis = {
                'total_signals': len(outcomes_df),
                'successful_signals': outcomes_df['success'].sum(),
                'success_rate': outcomes_df['success'].mean(),
                'avg_return': outcomes_df['return_pct'].mean(),
                'median_return': outcomes_df['return_pct'].median(),
                'avg_positive_return': outcomes_df[outcomes_df['return_pct'] > 0]['return_pct'].mean(),
                'avg_negative_return': outcomes_df[outcomes_df['return_pct'] < 0]['return_pct'].mean(),
                'max_gain': outcomes_df['max_gain_pct'].max(),
                'max_loss': outcomes_df['max_loss_pct'].min(),
                'avg_volatility': outcomes_df['volatility'].mean(),
                'avg_sharpe_ratio': outcomes_df['sharpe_ratio'].mean(),
                'avg_max_drawdown': outcomes_df['max_drawdown'].mean(),
                'avg_days_to_profit': outcomes_df['days_to_profit'].mean(),
                'avg_profit_probability': outcomes_df['profit_probability'].mean()
            }
            
            # Strategy-wise analysis
            strategy_analysis = {}
            for strategy in outcomes_df['strategy'].unique():
                strategy_data = outcomes_df[outcomes_df['strategy'] == strategy]
                
                strategy_analysis[strategy] = {
                    'signals': len(strategy_data),
                    'success_rate': strategy_data['success'].mean(),
                    'avg_return': strategy_data['return_pct'].mean(),
                    'avg_sharpe_ratio': strategy_data['sharpe_ratio'].mean(),
                    'best_return': strategy_data['return_pct'].max(),
                    'worst_return': strategy_data['return_pct'].min()
                }
            
            analysis['strategy_breakdown'] = strategy_analysis
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing outcomes: {str(e)}")
            return {}
    
    def save_outcomes(self, outcomes_df: pd.DataFrame, filename: str = None):
        """Save outcomes to file"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'ml/data/signal_outcomes_{timestamp}.pkl'
        
        outcomes_df.to_pickle(filename)
        logger.info(f"Outcomes saved to {filename}")
        
        # Also save as CSV for easy viewing
        csv_filename = filename.replace('.pkl', '.csv')
        outcomes_df.to_csv(csv_filename, index=False)
        logger.info(f"Outcomes also saved as CSV: {csv_filename}")

def main():
    """Run outcome tracking on historical signals"""
    print("📊 Starting Outcome Tracking for Historical Signals")
    print("=" * 60)
    
    # Load historical signals
    signals_file = 'ml/data/historical_signals.pkl'
    
    if not os.path.exists(signals_file):
        print(f"❌ Historical signals file not found: {signals_file}")
        print("Run historical_data_collector.py first to generate signals")
        return
    
    try:
        signals_df = pd.read_pickle(signals_file)
        print(f"📈 Loaded {len(signals_df)} historical signals")
        
        # Initialize outcome tracker
        tracker = OutcomeTracker()
        
        # Track outcomes
        outcomes_df = tracker.track_batch_outcomes(signals_df, holding_days=30)
        
        if len(outcomes_df) > 0:
            # Analyze results
            analysis = tracker.analyze_outcomes(outcomes_df)
            
            print(f"\n✅ Outcome Tracking Complete!")
            print(f"📊 Results Summary:")
            print(f"   Total signals: {analysis.get('total_signals', 0)}")
            print(f"   Success rate: {analysis.get('success_rate', 0):.2%}")
            print(f"   Average return: {analysis.get('avg_return', 0):.2%}")
            print(f"   Average Sharpe ratio: {analysis.get('avg_sharpe_ratio', 0):.3f}")
            
            print(f"\n📈 Strategy Performance:")
            for strategy, stats in analysis.get('strategy_breakdown', {}).items():
                print(f"   {strategy}:")
                print(f"     Signals: {stats['signals']}")
                print(f"     Success rate: {stats['success_rate']:.2%}")
                print(f"     Avg return: {stats['avg_return']:.2%}")
            
            # Save outcomes
            tracker.save_outcomes(outcomes_df)
            
            print(f"\n💾 Outcomes saved to ml/data/")
            print(f"🔄 Next step: Run feature engineering")
            
        else:
            print("❌ No outcomes calculated")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()
