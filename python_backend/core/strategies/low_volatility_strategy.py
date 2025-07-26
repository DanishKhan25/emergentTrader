"""
Low Volatility Strategy - Identifies stable, low-risk stocks with consistent returns
Focuses on defensive stocks with low price volatility and steady dividend yields
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class LowVolatilityStrategy:
    def __init__(self, name: str = "Low Volatility"):
        self.name = name
        self.volatility_period = 60  # Days to calculate volatility
        self.max_volatility_threshold = 0.25  # Maximum 25% annualized volatility
        self.min_dividend_yield = 1.0  # Minimum 1% dividend yield
        self.max_beta = 0.8  # Maximum beta (less volatile than market)
        self.min_market_cap = 5000000000  # 5B INR minimum (avoid penny stocks)
        self.consistency_period = 90  # Days to check return consistency
        self.max_drawdown_threshold = 0.15  # Maximum 15% drawdown
        self.quality_score_threshold = 0.6  # Minimum quality score
        self.defensive_sectors = [
            'FMCG', 'Pharmaceuticals', 'Utilities', 'Consumer Goods', 
            'Healthcare', 'Food & Beverages', 'Telecom'
        ]
        
    def calculate_volatility_metrics(self, data: pd.DataFrame) -> Dict:
        """
        Calculate comprehensive volatility metrics
        
        Args:
            data: Historical price data
        
        Returns:
            Volatility analysis results
        """
        try:
            if len(data) < self.volatility_period:
                return {}
            
            # Use recent data for volatility calculation
            recent_data = data.tail(self.volatility_period)
            
            # Daily returns
            daily_returns = recent_data['close'].pct_change().dropna()
            
            # Volatility metrics
            daily_volatility = daily_returns.std()
            annualized_volatility = daily_volatility * np.sqrt(252)  # 252 trading days
            
            # Downside volatility (only negative returns)
            negative_returns = daily_returns[daily_returns < 0]
            downside_volatility = negative_returns.std() * np.sqrt(252) if len(negative_returns) > 0 else 0
            
            # Maximum drawdown
            cumulative_returns = (1 + daily_returns).cumprod()
            rolling_max = cumulative_returns.expanding().max()
            drawdowns = (cumulative_returns - rolling_max) / rolling_max
            max_drawdown = abs(drawdowns.min())
            
            # Volatility trend (is volatility increasing or decreasing?)
            if len(data) >= 120:  # Need 4 months of data
                recent_vol = data.tail(30)['close'].pct_change().std()
                previous_vol = data.iloc[-60:-30]['close'].pct_change().std()
                volatility_trend = (recent_vol - previous_vol) / previous_vol if previous_vol > 0 else 0
            else:
                volatility_trend = 0
            
            # Price stability (coefficient of variation)
            mean_price = recent_data['close'].mean()
            price_cv = (recent_data['close'].std() / mean_price) if mean_price > 0 else 1
            
            # Volatility ranking (lower is better for this strategy)
            vol_score = max(0, (self.max_volatility_threshold - annualized_volatility) / self.max_volatility_threshold)
            
            return {
                'daily_volatility': daily_volatility,
                'annualized_volatility': annualized_volatility,
                'downside_volatility': downside_volatility,
                'max_drawdown': max_drawdown,
                'volatility_trend': volatility_trend,
                'price_cv': price_cv,
                'volatility_score': vol_score,
                'is_low_volatility': annualized_volatility <= self.max_volatility_threshold,
                'is_low_drawdown': max_drawdown <= self.max_drawdown_threshold
            }
            
        except Exception as e:
            logger.error(f"Error calculating volatility metrics: {str(e)}")
            return {}
    
    def analyze_return_consistency(self, data: pd.DataFrame) -> Dict:
        """
        Analyze return consistency and stability
        
        Args:
            data: Historical price data
        
        Returns:
            Return consistency analysis
        """
        try:
            if len(data) < self.consistency_period:
                return {}
            
            recent_data = data.tail(self.consistency_period)
            
            # Monthly returns for consistency analysis
            monthly_returns = []
            for i in range(0, len(recent_data) - 20, 20):  # Approximate monthly periods
                month_data = recent_data.iloc[i:i+20]
                if len(month_data) >= 2:
                    month_return = (month_data.iloc[-1]['close'] - month_data.iloc[0]['close']) / month_data.iloc[0]['close']
                    monthly_returns.append(month_return)
            
            if len(monthly_returns) < 3:
                return {}
            
            # Consistency metrics
            positive_months = sum(1 for ret in monthly_returns if ret > 0)
            consistency_ratio = positive_months / len(monthly_returns)
            
            # Return stability (low standard deviation of returns)
            return_stability = 1 / (1 + np.std(monthly_returns)) if monthly_returns else 0
            
            # Average return
            avg_monthly_return = np.mean(monthly_returns)
            annualized_return = (1 + avg_monthly_return) ** 12 - 1
            
            # Sharpe-like ratio (return per unit of volatility)
            volatility = np.std(monthly_returns)
            risk_adjusted_return = avg_monthly_return / volatility if volatility > 0 else 0
            
            # Worst month performance
            worst_month = min(monthly_returns) if monthly_returns else 0
            best_month = max(monthly_returns) if monthly_returns else 0
            
            return {
                'monthly_returns': monthly_returns,
                'consistency_ratio': consistency_ratio,
                'return_stability': return_stability,
                'avg_monthly_return': avg_monthly_return,
                'annualized_return': annualized_return,
                'risk_adjusted_return': risk_adjusted_return,
                'worst_month': worst_month,
                'best_month': best_month,
                'return_range': best_month - worst_month
            }
            
        except Exception as e:
            logger.error(f"Error analyzing return consistency: {str(e)}")
            return {}
    
    def analyze_defensive_characteristics(self, stock_info: Dict) -> Dict:
        """
        Analyze defensive characteristics of the stock
        
        Args:
            stock_info: Fundamental stock information
        
        Returns:
            Defensive characteristics analysis
        """
        try:
            # Extract defensive metrics
            dividend_yield = stock_info.get('dividend_yield', 0)
            beta = stock_info.get('beta', 1.0)
            market_cap = stock_info.get('market_cap', 0)
            sector = stock_info.get('sector', '')
            
            # Debt and liquidity (defensive companies should be financially stable)
            debt_equity = stock_info.get('debt_equity_ratio', 999)
            current_ratio = stock_info.get('current_ratio', 0)
            roe = stock_info.get('roe', 0)
            
            # Defensive score components
            defensive_score = 0
            
            # 1. Dividend yield (higher is better for defensive stocks)
            if dividend_yield >= self.min_dividend_yield:
                defensive_score += min(dividend_yield / 5, 2)  # Cap at 2 points
            
            # 2. Beta (lower is better)
            if beta <= self.max_beta:
                defensive_score += (self.max_beta - beta) * 3
            
            # 3. Market cap (larger companies are typically more stable)
            if market_cap >= self.min_market_cap:
                # Bonus for very large companies
                if market_cap >= 50000000000:  # 50B+
                    defensive_score += 1.5
                else:
                    defensive_score += 1
            
            # 4. Sector defensiveness
            is_defensive_sector = any(def_sector.lower() in sector.lower() for def_sector in self.defensive_sectors)
            if is_defensive_sector:
                defensive_score += 1
            
            # 5. Financial stability
            if debt_equity <= 0.5:  # Low debt
                defensive_score += 1
            if current_ratio >= 1.5:  # Good liquidity
                defensive_score += 0.5
            if roe >= 10:  # Decent profitability
                defensive_score += 0.5
            
            # Quality flags
            quality_flags = {
                'pays_dividend': dividend_yield > 0,
                'low_beta': beta <= self.max_beta,
                'large_cap': market_cap >= self.min_market_cap,
                'defensive_sector': is_defensive_sector,
                'stable_finances': debt_equity <= 0.5 and current_ratio >= 1.2
            }
            
            quality_score = sum(quality_flags.values()) / len(quality_flags)
            
            return {
                'dividend_yield': dividend_yield,
                'beta': beta,
                'market_cap': market_cap,
                'sector': sector,
                'debt_equity': debt_equity,
                'current_ratio': current_ratio,
                'roe': roe,
                'defensive_score': defensive_score,
                'quality_score': quality_score,
                'quality_flags': quality_flags,
                'is_defensive_sector': is_defensive_sector,
                'meets_defensive_criteria': (
                    dividend_yield >= self.min_dividend_yield and
                    beta <= self.max_beta and
                    market_cap >= self.min_market_cap
                )
            }
            
        except Exception as e:
            logger.error(f"Error analyzing defensive characteristics: {str(e)}")
            return {}
    
    def calculate_low_volatility_score(self, data: pd.DataFrame, stock_info: Dict) -> float:
        """
        Calculate overall low volatility strategy score
        
        Args:
            data: Price data
            stock_info: Fundamental information
        
        Returns:
            Low volatility score (higher indicates better low-vol opportunity)
        """
        try:
            # Get analysis components
            volatility_analysis = self.calculate_volatility_metrics(data)
            consistency_analysis = self.analyze_return_consistency(data)
            defensive_analysis = self.analyze_defensive_characteristics(stock_info)
            
            if not all([volatility_analysis, consistency_analysis, defensive_analysis]):
                return 0
            
            # Weighted scoring
            score = 0
            
            # 1. Low volatility (35% weight)
            vol_component = (
                volatility_analysis.get('volatility_score', 0) * 2 +
                (1 - volatility_analysis.get('max_drawdown', 1)) * 1.5 +
                volatility_analysis.get('downside_volatility', 0.5) * -2  # Lower downside vol is better
            )
            score += vol_component * 0.35
            
            # 2. Return consistency (25% weight)
            consistency_component = (
                consistency_analysis.get('consistency_ratio', 0) * 2 +
                consistency_analysis.get('return_stability', 0) * 1.5 +
                max(consistency_analysis.get('risk_adjusted_return', 0), 0) * 1
            )
            score += consistency_component * 0.25
            
            # 3. Defensive characteristics (25% weight)
            defensive_component = (
                defensive_analysis.get('defensive_score', 0) +
                defensive_analysis.get('quality_score', 0) * 2
            )
            score += defensive_component * 0.25
            
            # 4. Positive returns (15% weight)
            if consistency_analysis.get('annualized_return', 0) > 0:
                return_component = min(consistency_analysis.get('annualized_return', 0) * 5, 1.5)
                score += return_component * 0.15
            
            # Penalty for high volatility or poor defensive characteristics
            if volatility_analysis.get('annualized_volatility', 1) > self.max_volatility_threshold:
                score *= 0.5  # Heavy penalty for high volatility
            
            if defensive_analysis.get('quality_score', 0) < self.quality_score_threshold:
                score *= 0.7  # Penalty for poor quality
            
            return max(score, 0)  # Ensure non-negative score
            
        except Exception as e:
            logger.error(f"Error calculating low volatility score: {str(e)}")
            return 0
    
    def generate_signal(self, symbol: str, data: pd.DataFrame, stock_info: Dict) -> Optional[Dict]:
        """
        Generate low volatility signal
        
        Args:
            symbol: Stock symbol
            data: Historical price data with indicators
            stock_info: Fundamental stock information
        
        Returns:
            Signal dictionary or None if no signal
        """
        if data.empty or len(data) < self.volatility_period:
            return None
        
        try:
            latest = data.iloc[-1]
            current_price = latest['close']
            low_vol_score = self.calculate_low_volatility_score(data, stock_info)
            
            # Get analysis components
            volatility_analysis = self.calculate_volatility_metrics(data)
            consistency_analysis = self.analyze_return_consistency(data)
            defensive_analysis = self.analyze_defensive_characteristics(stock_info)
            
            # Low volatility criteria
            criteria_checks = [
                low_vol_score > 3.0,  # High low-vol score
                volatility_analysis.get('is_low_volatility', False),
                volatility_analysis.get('is_low_drawdown', False),
                defensive_analysis.get('meets_defensive_criteria', False),
                consistency_analysis.get('consistency_ratio', 0) > 0.6  # 60%+ positive months
            ]
            
            # Must meet at least 4 out of 5 criteria
            if sum(criteria_checks) >= 4:
                
                # Calculate position parameters (conservative for low-vol strategy)
                entry_price = current_price
                
                # Tighter stop loss for low volatility stocks
                volatility = volatility_analysis.get('annualized_volatility', 0.2)
                stop_loss_pct = min(volatility * 0.5, 0.12)  # Max 12% stop loss
                stop_loss = current_price * (1 - stop_loss_pct)
                
                # Conservative target (low-vol stocks don't move dramatically)
                expected_annual_return = max(consistency_analysis.get('annualized_return', 0.08), 0.08)
                target_return = min(expected_annual_return * 0.5, 0.15)  # Max 15% target
                target_price = current_price * (1 + target_return)
                
                # Larger position size due to lower risk
                risk_amount = 10000 * 0.02  # 2% risk (higher due to lower volatility)
                risk_per_share = entry_price - stop_loss
                position_size = int(risk_amount / risk_per_share) if risk_per_share > 0 else 150
                
                signal = {
                    'signal_id': f"{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    'symbol': symbol,
                    'strategy': self.name,
                    'signal_type': 'BUY',
                    'entry_price': round(entry_price, 2),
                    'target_price': round(target_price, 2),
                    'stop_loss': round(stop_loss, 2),
                    'quantity': position_size,
                    'low_vol_score': round(low_vol_score, 2),
                    
                    # Volatility metrics
                    'annualized_volatility': round(volatility_analysis.get('annualized_volatility', 0) * 100, 2),
                    'max_drawdown': round(volatility_analysis.get('max_drawdown', 0) * 100, 2),
                    'downside_volatility': round(volatility_analysis.get('downside_volatility', 0) * 100, 2),
                    
                    # Consistency metrics
                    'consistency_ratio': round(consistency_analysis.get('consistency_ratio', 0) * 100, 2),
                    'annualized_return': round(consistency_analysis.get('annualized_return', 0) * 100, 2),
                    'risk_adjusted_return': round(consistency_analysis.get('risk_adjusted_return', 0), 2),
                    
                    # Defensive characteristics
                    'dividend_yield': round(defensive_analysis.get('dividend_yield', 0), 2),
                    'beta': round(defensive_analysis.get('beta', 1), 2),
                    'defensive_score': round(defensive_analysis.get('defensive_score', 0), 2),
                    'quality_score': round(defensive_analysis.get('quality_score', 0), 2),
                    'is_defensive_sector': defensive_analysis.get('is_defensive_sector', False),
                    
                    'timestamp': datetime.now().isoformat(),
                    'risk_reward_ratio': round((target_price - entry_price) / (entry_price - stop_loss), 2),
                    'sector': stock_info.get('sector', ''),
                    'market_cap': stock_info.get('market_cap', 0),
                    'confidence_score': min(low_vol_score / 6, 1.0),  # Normalize to 0-1
                    'validity_days': 120,  # Low-vol signals valid for 4 months
                    'strategy_reason': f'Low volatility defensive stock with {volatility_analysis.get("annualized_volatility", 0)*100:.1f}% volatility',
                    'holding_period': '6-18 months',
                    'investment_thesis': self._generate_low_vol_thesis(volatility_analysis, consistency_analysis, defensive_analysis)
                }
                
                logger.info(f"Generated LOW VOLATILITY signal for {symbol} - Score: {low_vol_score}")
                return signal
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating low volatility signal for {symbol}: {str(e)}")
            return None
    
    def _generate_low_vol_thesis(self, volatility_analysis: Dict, consistency_analysis: Dict, defensive_analysis: Dict) -> str:
        """Generate investment thesis for low volatility opportunity"""
        try:
            thesis_points = []
            
            # Volatility highlights
            vol = volatility_analysis.get('annualized_volatility', 0) * 100
            if vol < 15:
                thesis_points.append(f"Very low volatility ({vol:.1f}%)")
            elif vol < 20:
                thesis_points.append(f"Low volatility ({vol:.1f}%)")
            
            # Consistency
            consistency = consistency_analysis.get('consistency_ratio', 0) * 100
            if consistency > 70:
                thesis_points.append(f"High return consistency ({consistency:.0f}% positive months)")
            
            # Defensive characteristics
            dividend_yield = defensive_analysis.get('dividend_yield', 0)
            if dividend_yield > 2:
                thesis_points.append(f"Good dividend yield ({dividend_yield:.1f}%)")
            
            beta = defensive_analysis.get('beta', 1)
            if beta < 0.7:
                thesis_points.append(f"Low market beta ({beta:.2f})")
            
            if defensive_analysis.get('is_defensive_sector', False):
                thesis_points.append("Defensive sector")
            
            # Financial stability
            if defensive_analysis.get('quality_score', 0) > 0.8:
                thesis_points.append("Strong financial quality")
            
            return "; ".join(thesis_points) if thesis_points else "Stable, low-risk defensive stock"
            
        except Exception:
            return "Low volatility stock with consistent returns"
    
    def get_strategy_params(self) -> Dict:
        """Return strategy parameters for configuration"""
        return {
            'name': self.name,
            'volatility_period': self.volatility_period,
            'max_volatility_threshold': self.max_volatility_threshold,
            'min_dividend_yield': self.min_dividend_yield,
            'max_beta': self.max_beta,
            'min_market_cap': self.min_market_cap,
            'consistency_period': self.consistency_period,
            'max_drawdown_threshold': self.max_drawdown_threshold,
            'quality_score_threshold': self.quality_score_threshold,
            'defensive_sectors': self.defensive_sectors
        }
    
    def backtest_signal(self, data: pd.DataFrame, entry_date: str, exit_days: int = 180) -> Dict:
        """
        Backtest a low volatility signal
        
        Args:
            data: Historical price data
            entry_date: Date when signal was generated
            exit_days: Number of days to hold (6 months default)
        
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
            
            # Low volatility specific metrics
            holding_data = data.iloc[entry_idx:exit_idx + 1]
            daily_returns = holding_data['close'].pct_change().dropna()
            
            # Volatility during holding period
            holding_volatility = daily_returns.std() * np.sqrt(252) * 100
            
            # Maximum drawdown during holding
            cumulative_returns = (1 + daily_returns).cumprod()
            rolling_max = cumulative_returns.expanding().max()
            drawdowns = (cumulative_returns - rolling_max) / rolling_max
            max_drawdown_holding = abs(drawdowns.min()) * 100
            
            # Sharpe ratio
            excess_returns = daily_returns - 0.05/252  # Assume 5% risk-free rate
            sharpe_ratio = (excess_returns.mean() / excess_returns.std() * np.sqrt(252)) if excess_returns.std() > 0 else 0
            
            # Consistency during holding
            monthly_periods = len(holding_data) // 20
            positive_periods = 0
            for i in range(monthly_periods):
                start_idx = i * 20
                end_idx = min((i + 1) * 20, len(holding_data))
                if end_idx > start_idx + 1:
                    period_return = (holding_data.iloc[end_idx-1]['close'] - holding_data.iloc[start_idx]['close']) / holding_data.iloc[start_idx]['close']
                    if period_return > 0:
                        positive_periods += 1
            
            consistency_during_holding = positive_periods / monthly_periods if monthly_periods > 0 else 0
            
            return {
                'entry_price': entry_price,
                'exit_price': exit_price,
                'absolute_return': absolute_return,
                'percentage_return': percentage_return,
                'holding_volatility': holding_volatility,
                'max_drawdown_holding': max_drawdown_holding,
                'sharpe_ratio': sharpe_ratio,
                'consistency_during_holding': consistency_during_holding,
                'holding_days': exit_idx - entry_idx,
                'success': percentage_return > 0,
                'low_risk_success': percentage_return > 0 and max_drawdown_holding < 10,
                'strategy_type': 'low_volatility'
            }
            
        except Exception as e:
            logger.error(f"Error in low volatility backtesting: {str(e)}")
            return {}
