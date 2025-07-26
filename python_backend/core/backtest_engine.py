"""
Backtest Engine - Comprehensive backtesting system for trading strategies
Tests strategies against historical data with proper risk management
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
import json

logger = logging.getLogger(__name__)

class BacktestEngine:
    def __init__(self, 
                 initial_capital: float = 100000,
                 commission_rate: float = 0.001,  # 0.1% per trade
                 slippage_rate: float = 0.0005):   # 0.05% slippage
        
        self.initial_capital = initial_capital
        self.commission_rate = commission_rate
        self.slippage_rate = slippage_rate
        
        # Portfolio tracking
        self.portfolio_value = []
        self.trades = []
        self.positions = {}
        self.cash = initial_capital
        
        # Performance metrics
        self.total_return = 0
        self.sharpe_ratio = 0
        self.max_drawdown = 0
        self.win_rate = 0
        self.profit_factor = 0
        
    def reset_portfolio(self):
        """Reset portfolio for new backtest"""
        self.portfolio_value = []
        self.trades = []
        self.positions = {}
        self.cash = self.initial_capital
        
    def execute_trade(self, 
                     signal: Dict, 
                     current_date: str, 
                     current_price: float) -> bool:
        """
        Execute a trade based on signal
        
        Args:
            signal: Trading signal dictionary
            current_date: Current date
            current_price: Current market price
            
        Returns:
            True if trade executed successfully
        """
        try:
            symbol = signal['symbol']
            signal_type = signal['signal_type']
            quantity = signal.get('quantity', 100)
            
            # Apply slippage
            if signal_type == 'BUY':
                execution_price = current_price * (1 + self.slippage_rate)
            else:
                execution_price = current_price * (1 - self.slippage_rate)
            
            # Calculate trade value and commission
            trade_value = quantity * execution_price
            commission = trade_value * self.commission_rate
            
            if signal_type == 'BUY':
                # Check if we have enough cash
                total_cost = trade_value + commission
                if self.cash >= total_cost:
                    # Execute buy order
                    self.cash -= total_cost
                    
                    if symbol not in self.positions:
                        self.positions[symbol] = {
                            'quantity': 0,
                            'avg_price': 0,
                            'total_cost': 0
                        }
                    
                    # Update position
                    old_quantity = self.positions[symbol]['quantity']
                    old_total_cost = self.positions[symbol]['total_cost']
                    
                    new_quantity = old_quantity + quantity
                    new_total_cost = old_total_cost + trade_value
                    
                    self.positions[symbol]['quantity'] = new_quantity
                    self.positions[symbol]['avg_price'] = new_total_cost / new_quantity
                    self.positions[symbol]['total_cost'] = new_total_cost
                    
                    # Record trade
                    self.trades.append({
                        'date': current_date,
                        'symbol': symbol,
                        'action': 'BUY',
                        'quantity': quantity,
                        'price': execution_price,
                        'commission': commission,
                        'trade_value': trade_value,
                        'signal_id': signal.get('signal_id', ''),
                        'strategy': signal.get('strategy', ''),
                        'stop_loss': signal.get('stop_loss', 0),
                        'target_price': signal.get('target_price', 0)
                    })
                    
                    return True
                else:
                    logger.warning(f"Insufficient cash for {symbol} buy order")
                    return False
                    
            elif signal_type == 'SELL' and symbol in self.positions:
                # Execute sell order
                available_quantity = self.positions[symbol]['quantity']
                sell_quantity = min(quantity, available_quantity)
                
                if sell_quantity > 0:
                    sell_value = sell_quantity * execution_price
                    self.cash += sell_value - commission
                    
                    # Update position
                    self.positions[symbol]['quantity'] -= sell_quantity
                    if self.positions[symbol]['quantity'] == 0:
                        del self.positions[symbol]
                    
                    # Record trade
                    self.trades.append({
                        'date': current_date,
                        'symbol': symbol,
                        'action': 'SELL',
                        'quantity': sell_quantity,
                        'price': execution_price,
                        'commission': commission,
                        'trade_value': sell_value,
                        'signal_id': signal.get('signal_id', ''),
                        'strategy': signal.get('strategy', '')
                    })
                    
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error executing trade: {str(e)}")
            return False
    
    def check_exit_conditions(self, symbol: str, current_price: float, current_date: str) -> Optional[Dict]:
        """
        Check if position should be exited based on stop loss or target
        
        Args:
            symbol: Stock symbol
            current_price: Current market price
            current_date: Current date
            
        Returns:
            Exit signal if conditions met, None otherwise
        """
        if symbol not in self.positions:
            return None
        
        try:
            position = self.positions[symbol]
            
            # Find the latest buy trade for this symbol to get stop loss and target
            latest_buy_trade = None
            for trade in reversed(self.trades):
                if (trade['symbol'] == symbol and 
                    trade['action'] == 'BUY' and
                    'stop_loss' in trade and 
                    'target_price' in trade):
                    latest_buy_trade = trade
                    break
            
            if not latest_buy_trade:
                return None
            
            stop_loss = latest_buy_trade.get('stop_loss', 0)
            target_price = latest_buy_trade.get('target_price', 0)
            
            # Check stop loss
            if stop_loss > 0 and current_price <= stop_loss:
                return {
                    'symbol': symbol,
                    'signal_type': 'SELL',
                    'quantity': position['quantity'],
                    'reason': 'stop_loss_hit',
                    'signal_id': f"{symbol}_sl_{current_date}",
                    'strategy': latest_buy_trade.get('strategy', '')
                }
            
            # Check target price
            if target_price > 0 and current_price >= target_price:
                return {
                    'symbol': symbol,
                    'signal_type': 'SELL',
                    'quantity': position['quantity'],
                    'reason': 'target_hit',
                    'signal_id': f"{symbol}_target_{current_date}",
                    'strategy': latest_buy_trade.get('strategy', '')
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking exit conditions for {symbol}: {str(e)}")
            return None
    
    def calculate_portfolio_value(self, current_prices: Dict[str, float]) -> float:
        """
        Calculate current portfolio value
        
        Args:
            current_prices: Dictionary of current stock prices
            
        Returns:
            Total portfolio value
        """
        try:
            total_value = self.cash
            
            for symbol, position in self.positions.items():
                if symbol in current_prices:
                    position_value = position['quantity'] * current_prices[symbol]
                    total_value += position_value
                else:
                    # If price not available, use last known average price
                    position_value = position['quantity'] * position['avg_price']
                    total_value += position_value
            
            return total_value
            
        except Exception as e:
            logger.error(f"Error calculating portfolio value: {str(e)}")
            return self.cash
    
    def run_backtest(self, 
                    signals: List[Dict], 
                    price_data: Dict[str, pd.DataFrame],
                    start_date: str = "2012-01-01",
                    end_date: str = "2018-12-31") -> Dict:
        """
        Run backtest on historical data
        
        Args:
            signals: List of trading signals with dates
            price_data: Dictionary of price data by symbol
            start_date: Backtest start date
            end_date: Backtest end date
            
        Returns:
            Backtest results dictionary
        """
        try:
            self.reset_portfolio()
            
            # Create date range
            date_range = pd.date_range(start=start_date, end=end_date, freq='D')
            
            for current_date in date_range:
                current_date_str = current_date.strftime('%Y-%m-%d')
                
                # Get current prices for all symbols
                current_prices = {}
                for symbol, data in price_data.items():
                    price_row = data[data['date'] <= current_date_str].tail(1)
                    if not price_row.empty:
                        current_prices[symbol] = price_row.iloc[0]['close']
                
                # Check for exit conditions first
                exit_signals = []
                for symbol in list(self.positions.keys()):
                    if symbol in current_prices:
                        exit_signal = self.check_exit_conditions(
                            symbol, current_prices[symbol], current_date_str
                        )
                        if exit_signal:
                            exit_signals.append(exit_signal)
                
                # Execute exit signals
                for exit_signal in exit_signals:
                    self.execute_trade(exit_signal, current_date_str, 
                                     current_prices[exit_signal['symbol']])
                
                # Process new entry signals for this date
                daily_signals = [s for s in signals if s.get('date', s.get('timestamp', ''))[:10] == current_date_str]
                
                for signal in daily_signals:
                    symbol = signal['symbol']
                    if symbol in current_prices:
                        self.execute_trade(signal, current_date_str, current_prices[symbol])
                
                # Record portfolio value
                portfolio_value = self.calculate_portfolio_value(current_prices)
                self.portfolio_value.append({
                    'date': current_date_str,
                    'value': portfolio_value,
                    'cash': self.cash,
                    'positions_value': portfolio_value - self.cash
                })
            
            # Calculate performance metrics
            performance_metrics = self.calculate_performance_metrics()
            
            return {
                'backtest_period': {'start': start_date, 'end': end_date},
                'initial_capital': self.initial_capital,
                'final_portfolio_value': self.portfolio_value[-1]['value'] if self.portfolio_value else self.initial_capital,
                'total_trades': len(self.trades),
                'performance_metrics': performance_metrics,
                'portfolio_history': self.portfolio_value,
                'trades_history': self.trades,
                'final_positions': self.positions
            }
            
        except Exception as e:
            logger.error(f"Error running backtest: {str(e)}")
            return {'error': str(e)}
    
    def calculate_performance_metrics(self) -> Dict:
        """Calculate comprehensive performance metrics"""
        try:
            if not self.portfolio_value:
                return {}
            
            # Convert to DataFrame for easier calculations
            portfolio_df = pd.DataFrame(self.portfolio_value)
            portfolio_df['date'] = pd.to_datetime(portfolio_df['date'])
            portfolio_df['returns'] = portfolio_df['value'].pct_change()
            
            # Total return
            initial_value = portfolio_df.iloc[0]['value']
            final_value = portfolio_df.iloc[-1]['value']
            total_return = (final_value - initial_value) / initial_value
            
            # Annualized return
            days = (portfolio_df.iloc[-1]['date'] - portfolio_df.iloc[0]['date']).days
            years = days / 365.25
            annualized_return = (1 + total_return) ** (1/years) - 1 if years > 0 else 0
            
            # Volatility and Sharpe ratio
            returns = portfolio_df['returns'].dropna()
            volatility = returns.std() * np.sqrt(252)  # Annualized volatility
            sharpe_ratio = annualized_return / volatility if volatility != 0 else 0
            
            # Maximum drawdown
            portfolio_df['cumulative_return'] = (1 + portfolio_df['returns'].fillna(0)).cumprod()
            portfolio_df['peak'] = portfolio_df['cumulative_return'].expanding().max()
            portfolio_df['drawdown'] = (portfolio_df['cumulative_return'] - portfolio_df['peak']) / portfolio_df['peak']
            max_drawdown = portfolio_df['drawdown'].min()
            
            # Trade statistics
            if self.trades:
                buy_trades = [t for t in self.trades if t['action'] == 'BUY']
                sell_trades = [t for t in self.trades if t['action'] == 'SELL']
                
                # Calculate P&L for each completed trade
                completed_trades = []
                for sell_trade in sell_trades:
                    # Find corresponding buy trade
                    symbol = sell_trade['symbol']
                    for buy_trade in reversed(buy_trades):
                        if buy_trade['symbol'] == symbol and buy_trade['date'] <= sell_trade['date']:
                            pnl = sell_trade['quantity'] * (sell_trade['price'] - buy_trade['price'])
                            pnl -= sell_trade['commission'] + buy_trade['commission']
                            
                            completed_trades.append({
                                'symbol': symbol,
                                'pnl': pnl,
                                'return_pct': (sell_trade['price'] - buy_trade['price']) / buy_trade['price'],
                                'holding_days': (pd.to_datetime(sell_trade['date']) - pd.to_datetime(buy_trade['date'])).days
                            })
                            break
                
                # Win rate and profit factor
                if completed_trades:
                    winning_trades = [t for t in completed_trades if t['pnl'] > 0]
                    losing_trades = [t for t in completed_trades if t['pnl'] < 0]
                    
                    win_rate = len(winning_trades) / len(completed_trades)
                    
                    total_profits = sum(t['pnl'] for t in winning_trades)
                    total_losses = abs(sum(t['pnl'] for t in losing_trades))
                    profit_factor = total_profits / total_losses if total_losses != 0 else float('inf')
                    
                    avg_win = total_profits / len(winning_trades) if winning_trades else 0
                    avg_loss = total_losses / len(losing_trades) if losing_trades else 0
                    
                else:
                    win_rate = 0
                    profit_factor = 0
                    avg_win = 0
                    avg_loss = 0
                    completed_trades = []
            else:
                win_rate = 0
                profit_factor = 0
                avg_win = 0
                avg_loss = 0
                completed_trades = []
            
            return {
                'total_return': total_return,
                'annualized_return': annualized_return,
                'volatility': volatility,
                'sharpe_ratio': sharpe_ratio,
                'max_drawdown': max_drawdown,
                'win_rate': win_rate,
                'profit_factor': profit_factor,
                'total_trades': len(self.trades),
                'completed_trades': len(completed_trades),
                'avg_win': avg_win,
                'avg_loss': avg_loss,
                'avg_holding_days': np.mean([t['holding_days'] for t in completed_trades]) if completed_trades else 0
            }
            
        except Exception as e:
            logger.error(f"Error calculating performance metrics: {str(e)}")
            return {}