"""
Value Investing Strategy - Identifies undervalued stocks based on fundamental analysis
Focuses on stocks trading below their intrinsic value with strong fundamentals
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class ValueInvestingStrategy:
    def __init__(self, name: str = "Value Investing"):
        self.name = name
        self.max_pe_ratio = 15  # Maximum P/E ratio for value stocks
        self.min_roe = 15  # Minimum Return on Equity (%)
        self.max_debt_equity = 0.5  # Maximum debt-to-equity ratio
        self.min_current_ratio = 1.2  # Minimum current ratio for liquidity
        self.min_profit_growth = 10  # Minimum profit growth (%)
        self.max_pb_ratio = 2.0  # Maximum Price-to-Book ratio
        self.min_dividend_yield = 1.0  # Minimum dividend yield (%)
        self.price_momentum_weight = 0.3  # Weight for technical momentum
        
    def calculate_intrinsic_value(self, stock_info: Dict) -> float:
        """
        Calculate intrinsic value using simplified DCF and P/E methods
        
        Args:
            stock_info: Dictionary with fundamental data
        
        Returns:
            Estimated intrinsic value per share
        """
        try:
            # Get fundamental metrics
            eps = stock_info.get('eps', 0)
            roe = stock_info.get('roe', 0)
            book_value = stock_info.get('book_value_per_share', 0)
            growth_rate = stock_info.get('profit_growth', 0) / 100
            
            if eps <= 0 or roe <= 0:
                return 0
            
            # Method 1: P/E based valuation (conservative P/E for value stocks)
            conservative_pe = min(self.max_pe_ratio, 12)  # Use conservative P/E
            pe_value = eps * conservative_pe
            
            # Method 2: Book value based (P/B approach)
            if book_value > 0:
                pb_value = book_value * 1.5  # Conservative P/B multiple
            else:
                pb_value = pe_value
            
            # Method 3: Growth-adjusted value (simplified PEG)
            if growth_rate > 0:
                peg_pe = min(growth_rate * 100, 20)  # Cap PEG-based P/E at 20
                growth_value = eps * peg_pe
            else:
                growth_value = pe_value
            
            # Weighted average of different valuation methods
            intrinsic_value = (pe_value * 0.4 + pb_value * 0.3 + growth_value * 0.3)
            
            return max(intrinsic_value, 0)
            
        except Exception as e:
            logger.error(f"Error calculating intrinsic value: {str(e)}")
            return 0
    
    def calculate_value_score(self, data: pd.DataFrame, stock_info: Dict) -> float:
        """
        Calculate value investing score based on fundamental and technical factors
        
        Args:
            data: DataFrame with price data
            stock_info: Dictionary with fundamental data
        
        Returns:
            Value score (higher indicates better value opportunity)
        """
        try:
            if data.empty:
                return 0
            
            current_price = data.iloc[-1]['close']
            
            # Get fundamental metrics
            pe_ratio = stock_info.get('pe_ratio', 999)
            pb_ratio = stock_info.get('pb_ratio', 999)
            roe = stock_info.get('roe', 0)
            debt_equity = stock_info.get('debt_equity_ratio', 999)
            current_ratio = stock_info.get('current_ratio', 0)
            profit_growth = stock_info.get('profit_growth', 0)
            dividend_yield = stock_info.get('dividend_yield', 0)
            
            # Calculate intrinsic value
            intrinsic_value = self.calculate_intrinsic_value(stock_info)
            
            # Value score components
            score_components = {}
            
            # 1. Price vs Intrinsic Value (30% weight)
            if intrinsic_value > 0:
                value_discount = (intrinsic_value - current_price) / current_price
                score_components['value_discount'] = max(value_discount * 10, -5)  # Cap negative impact
            else:
                score_components['value_discount'] = -2
            
            # 2. P/E Ratio Score (20% weight)
            if 0 < pe_ratio <= self.max_pe_ratio:
                score_components['pe_score'] = (self.max_pe_ratio - pe_ratio) / 2
            else:
                score_components['pe_score'] = -3
            
            # 3. P/B Ratio Score (15% weight)
            if 0 < pb_ratio <= self.max_pb_ratio:
                score_components['pb_score'] = (self.max_pb_ratio - pb_ratio) * 2
            else:
                score_components['pb_score'] = -2
            
            # 4. ROE Score (15% weight)
            if roe >= self.min_roe:
                score_components['roe_score'] = min((roe - self.min_roe) / 5, 3)
            else:
                score_components['roe_score'] = -2
            
            # 5. Debt-to-Equity Score (10% weight)
            if debt_equity <= self.max_debt_equity:
                score_components['debt_score'] = (self.max_debt_equity - debt_equity) * 4
            else:
                score_components['debt_score'] = -2
            
            # 6. Liquidity Score (5% weight)
            if current_ratio >= self.min_current_ratio:
                score_components['liquidity_score'] = min((current_ratio - self.min_current_ratio) * 2, 2)
            else:
                score_components['liquidity_score'] = -1
            
            # 7. Growth Score (5% weight)
            if profit_growth >= self.min_profit_growth:
                score_components['growth_score'] = min(profit_growth / 10, 2)
            else:
                score_components['growth_score'] = max(profit_growth / 20, -1)
            
            # 8. Technical Momentum (for timing) - reduced weight for value investing
            if len(data) >= 20:
                sma_20 = data['close'].tail(20).mean()
                momentum_score = ((current_price - sma_20) / sma_20) * 5
                score_components['momentum_score'] = max(min(momentum_score, 1), -1)
            else:
                score_components['momentum_score'] = 0
            
            # Weighted total score
            weights = {
                'value_discount': 0.30,
                'pe_score': 0.20,
                'pb_score': 0.15,
                'roe_score': 0.15,
                'debt_score': 0.10,
                'liquidity_score': 0.05,
                'growth_score': 0.05,
                'momentum_score': self.price_momentum_weight * 0.1
            }
            
            total_score = sum(score_components[key] * weights[key] for key in score_components)
            
            return total_score
            
        except Exception as e:
            logger.error(f"Error calculating value score: {str(e)}")
            return 0
    
    def generate_signal(self, symbol: str, data: pd.DataFrame, stock_info: Dict) -> Optional[Dict]:
        """
        Generate buy signal based on value investing strategy
        
        Args:
            symbol: Stock symbol
            data: Historical price data with indicators
            stock_info: Fundamental stock information
        
        Returns:
            Signal dictionary or None if no signal
        """
        if data.empty:
            return None
        
        try:
            latest = data.iloc[-1]
            current_price = latest['close']
            value_score = self.calculate_value_score(data, stock_info)
            
            # Get fundamental metrics for validation
            pe_ratio = stock_info.get('pe_ratio', 999)
            roe = stock_info.get('roe', 0)
            debt_equity = stock_info.get('debt_equity_ratio', 999)
            current_ratio = stock_info.get('current_ratio', 0)
            
            # Value investing criteria
            fundamental_checks = [
                pe_ratio <= self.max_pe_ratio,
                roe >= self.min_roe,
                debt_equity <= self.max_debt_equity,
                current_ratio >= self.min_current_ratio,
                value_score > 2.0  # Minimum value score threshold
            ]
            
            # Must pass at least 4 out of 5 fundamental checks
            if sum(fundamental_checks) >= 4:
                
                # Calculate intrinsic value and margin of safety
                intrinsic_value = self.calculate_intrinsic_value(stock_info)
                margin_of_safety = ((intrinsic_value - current_price) / current_price) * 100 if intrinsic_value > 0 else 0
                
                # Only generate signal if there's a reasonable margin of safety
                if margin_of_safety > 10:  # At least 10% margin of safety
                    
                    # Calculate position sizing (value investing typically uses larger positions)
                    atr = latest.get('atr', current_price * 0.02)
                    stop_loss = current_price * 0.85  # 15% stop loss for value stocks
                    target_price = min(intrinsic_value * 0.9, current_price * 1.5)  # Conservative target
                    
                    # Position size based on 2% risk (higher for value investing)
                    risk_amount = 10000 * 0.02
                    risk_per_share = current_price - stop_loss
                    position_size = int(risk_amount / risk_per_share) if risk_per_share > 0 else 100
                    
                    signal = {
                        'signal_id': f"{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        'symbol': symbol,
                        'strategy': self.name,
                        'signal_type': 'BUY',
                        'entry_price': round(current_price, 2),
                        'target_price': round(target_price, 2),
                        'stop_loss': round(stop_loss, 2),
                        'quantity': position_size,
                        'value_score': round(value_score, 2),
                        'intrinsic_value': round(intrinsic_value, 2),
                        'margin_of_safety': round(margin_of_safety, 2),
                        'pe_ratio': round(pe_ratio, 2),
                        'pb_ratio': round(stock_info.get('pb_ratio', 0), 2),
                        'roe': round(roe, 2),
                        'debt_equity_ratio': round(debt_equity, 2),
                        'current_ratio': round(current_ratio, 2),
                        'profit_growth': round(stock_info.get('profit_growth', 0), 2),
                        'dividend_yield': round(stock_info.get('dividend_yield', 0), 2),
                        'timestamp': datetime.now().isoformat(),
                        'risk_reward_ratio': round((target_price - current_price) / (current_price - stop_loss), 2),
                        'sector': stock_info.get('sector', ''),
                        'market_cap': stock_info.get('market_cap', 0),
                        'confidence_score': min(value_score / 5, 1.0),  # Normalize to 0-1
                        'validity_days': 30,  # Value signals valid for longer period
                        'strategy_reason': f'Undervalued stock with {margin_of_safety:.1f}% margin of safety',
                        'investment_thesis': self._generate_investment_thesis(stock_info, margin_of_safety)
                    }
                    
                    logger.info(f"Generated VALUE BUY signal for {symbol} - Score: {value_score}, Margin: {margin_of_safety}%")
                    return signal
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating value investing signal for {symbol}: {str(e)}")
            return None
    
    def _generate_investment_thesis(self, stock_info: Dict, margin_of_safety: float) -> str:
        """Generate investment thesis based on fundamental analysis"""
        try:
            thesis_points = []
            
            pe_ratio = stock_info.get('pe_ratio', 0)
            roe = stock_info.get('roe', 0)
            profit_growth = stock_info.get('profit_growth', 0)
            debt_equity = stock_info.get('debt_equity_ratio', 0)
            
            if pe_ratio > 0 and pe_ratio <= self.max_pe_ratio:
                thesis_points.append(f"Low P/E of {pe_ratio:.1f}")
            
            if roe >= self.min_roe:
                thesis_points.append(f"Strong ROE of {roe:.1f}%")
            
            if profit_growth > 0:
                thesis_points.append(f"Profit growth of {profit_growth:.1f}%")
            
            if debt_equity <= self.max_debt_equity:
                thesis_points.append(f"Conservative debt level ({debt_equity:.2f})")
            
            thesis_points.append(f"{margin_of_safety:.1f}% margin of safety")
            
            return "; ".join(thesis_points)
            
        except Exception:
            return "Value opportunity identified"
    
    def get_strategy_params(self) -> Dict:
        """Return strategy parameters for configuration"""
        return {
            'name': self.name,
            'max_pe_ratio': self.max_pe_ratio,
            'min_roe': self.min_roe,
            'max_debt_equity': self.max_debt_equity,
            'min_current_ratio': self.min_current_ratio,
            'min_profit_growth': self.min_profit_growth,
            'max_pb_ratio': self.max_pb_ratio,
            'min_dividend_yield': self.min_dividend_yield,
            'price_momentum_weight': self.price_momentum_weight
        }
    
    def backtest_signal(self, data: pd.DataFrame, entry_date: str, exit_days: int = 60) -> Dict:
        """
        Backtest a value investing signal (longer holding period)
        
        Args:
            data: Historical price data
            entry_date: Date when signal was generated
            exit_days: Number of days to hold position (longer for value investing)
        
        Returns:
            Backtest results dictionary
        """
        try:
            entry_idx = data[data['date'] >= entry_date].index[0]
            exit_idx = min(entry_idx + exit_days, len(data) - 1)
            
            entry_price = data.iloc[entry_idx]['close']
            exit_price = data.iloc[exit_idx]['close']
            
            # Calculate returns
            absolute_return = exit_price - entry_price
            percentage_return = (absolute_return / entry_price) * 100
            
            # Calculate annualized return
            holding_days = exit_idx - entry_idx
            annualized_return = (percentage_return / holding_days) * 365 if holding_days > 0 else 0
            
            # Track maximum drawdown during holding period
            holding_data = data.iloc[entry_idx:exit_idx + 1]
            cumulative_returns = (holding_data['close'] / entry_price - 1) * 100
            max_drawdown = cumulative_returns.min()
            max_gain = cumulative_returns.max()
            
            # Value-specific metrics
            dividend_received = 0  # Would need dividend data
            total_return = percentage_return + dividend_received
            
            return {
                'entry_price': entry_price,
                'exit_price': exit_price,
                'absolute_return': absolute_return,
                'percentage_return': percentage_return,
                'annualized_return': annualized_return,
                'total_return': total_return,
                'max_drawdown': max_drawdown,
                'max_gain': max_gain,
                'holding_days': holding_days,
                'success': percentage_return > 0,
                'beat_market': percentage_return > 8,  # Assuming 8% market return
                'strategy_type': 'value_investing'
            }
            
        except Exception as e:
            logger.error(f"Error in value investing backtesting: {str(e)}")
            return {}
    
    def screen_value_stocks(self, stocks_data: List[Dict]) -> List[Dict]:
        """
        Screen stocks for value investing opportunities
        
        Args:
            stocks_data: List of stock data dictionaries
        
        Returns:
            List of stocks that pass value screening criteria
        """
        try:
            value_stocks = []
            
            for stock in stocks_data:
                # Apply fundamental filters
                pe_ratio = stock.get('pe_ratio', 999)
                roe = stock.get('roe', 0)
                debt_equity = stock.get('debt_equity_ratio', 999)
                current_ratio = stock.get('current_ratio', 0)
                profit_growth = stock.get('profit_growth', -999)
                
                # Value screening criteria
                passes_screen = (
                    0 < pe_ratio <= self.max_pe_ratio and
                    roe >= self.min_roe and
                    debt_equity <= self.max_debt_equity and
                    current_ratio >= self.min_current_ratio and
                    profit_growth >= 0  # At least positive growth
                )
                
                if passes_screen:
                    # Calculate additional value metrics
                    stock['value_rank'] = self._calculate_value_rank(stock)
                    value_stocks.append(stock)
            
            # Sort by value rank (best opportunities first)
            value_stocks.sort(key=lambda x: x.get('value_rank', 0), reverse=True)
            
            return value_stocks
            
        except Exception as e:
            logger.error(f"Error screening value stocks: {str(e)}")
            return []
    
    def _calculate_value_rank(self, stock: Dict) -> float:
        """Calculate overall value ranking for a stock"""
        try:
            pe_ratio = stock.get('pe_ratio', 999)
            pb_ratio = stock.get('pb_ratio', 999)
            roe = stock.get('roe', 0)
            profit_growth = stock.get('profit_growth', 0)
            
            # Simple ranking formula (lower P/E and P/B, higher ROE and growth)
            rank = 0
            
            if pe_ratio > 0:
                rank += (20 - pe_ratio) / 2  # Favor lower P/E
            
            if pb_ratio > 0:
                rank += (3 - pb_ratio) * 2  # Favor lower P/B
            
            rank += roe / 5  # Favor higher ROE
            rank += profit_growth / 10  # Favor higher growth
            
            return max(rank, 0)
            
        except Exception:
            return 0
