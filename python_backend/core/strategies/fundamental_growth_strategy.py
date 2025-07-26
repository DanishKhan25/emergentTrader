"""
Fundamental Growth Strategy - Identifies stocks with strong and consistent fundamental growth
Focuses on companies with accelerating earnings, revenue, and operational metrics
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class FundamentalGrowthStrategy:
    def __init__(self, name: str = "Fundamental Growth"):
        self.name = name
        self.min_revenue_growth = 15  # Minimum revenue growth %
        self.min_earnings_growth = 20  # Minimum earnings growth %
        self.min_roe = 15  # Minimum Return on Equity
        self.max_pe_ratio = 30  # Maximum P/E for growth stocks
        self.min_profit_margin = 5  # Minimum profit margin %
        self.max_debt_equity = 0.5  # Maximum debt-to-equity ratio
        self.min_current_ratio = 1.2  # Minimum current ratio
        self.growth_acceleration_threshold = 1.2  # Growth acceleration factor
        self.quality_score_threshold = 0.7  # Minimum quality score
        
    def analyze_growth_trends(self, stock_info: Dict) -> Dict:
        """
        Analyze growth trends and consistency
        
        Args:
            stock_info: Fundamental stock information
        
        Returns:
            Growth trend analysis
        """
        try:
            # Extract growth metrics
            revenue_growth = stock_info.get('revenue_growth', 0)
            earnings_growth = stock_info.get('earnings_growth', 0)
            profit_growth = stock_info.get('profit_growth', 0)
            
            # Use the best available growth metric
            primary_growth = max(earnings_growth, profit_growth)
            
            # Growth quality assessment
            growth_metrics = {
                'revenue_growth': revenue_growth,
                'earnings_growth': earnings_growth,
                'profit_growth': profit_growth,
                'primary_growth': primary_growth
            }
            
            # Growth consistency (all metrics should be positive and significant)
            positive_growth_count = sum(1 for growth in growth_metrics.values() if growth > 10)
            growth_consistency = positive_growth_count / len(growth_metrics)
            
            # Growth acceleration (higher growth rates get higher scores)
            acceleration_score = 0
            if revenue_growth > 25:
                acceleration_score += 1
            if primary_growth > 30:
                acceleration_score += 1
            if primary_growth > 50:
                acceleration_score += 1  # Exceptional growth
            
            # Growth sustainability indicators
            sustainability_factors = []
            
            # Revenue growth should support earnings growth
            if revenue_growth > 0 and primary_growth > 0:
                growth_alignment = min(primary_growth / revenue_growth, 2.0)  # Cap at 2x
                sustainability_factors.append(growth_alignment)
            
            # Consistent double-digit growth
            if revenue_growth >= 15 and primary_growth >= 20:
                sustainability_factors.append(1.5)
            
            sustainability_score = np.mean(sustainability_factors) if sustainability_factors else 0
            
            return {
                'revenue_growth': revenue_growth,
                'earnings_growth': earnings_growth,
                'profit_growth': profit_growth,
                'primary_growth': primary_growth,
                'growth_consistency': growth_consistency,
                'acceleration_score': acceleration_score,
                'sustainability_score': sustainability_score,
                'meets_growth_criteria': (
                    revenue_growth >= self.min_revenue_growth and
                    primary_growth >= self.min_earnings_growth
                )
            }
            
        except Exception as e:
            logger.error(f"Error analyzing growth trends: {str(e)}")
            return {}
    
    def analyze_profitability_metrics(self, stock_info: Dict) -> Dict:
        """
        Analyze profitability and efficiency metrics
        
        Args:
            stock_info: Fundamental stock information
        
        Returns:
            Profitability analysis
        """
        try:
            # Extract profitability metrics
            roe = stock_info.get('roe', 0)
            profit_margin = stock_info.get('profit_margin', 0)
            operating_margin = stock_info.get('operating_margin', 0)
            gross_margin = stock_info.get('gross_margin', 0)
            
            # Profitability score
            profitability_score = 0
            
            # ROE score (higher is better)
            if roe >= self.min_roe:
                profitability_score += min((roe - self.min_roe) / 10, 2)  # Cap at 2
            
            # Margin analysis
            margins = [profit_margin, operating_margin, gross_margin]
            valid_margins = [m for m in margins if m > 0]
            
            if valid_margins:
                avg_margin = np.mean(valid_margins)
                if avg_margin >= self.min_profit_margin:
                    profitability_score += min(avg_margin / 20, 1.5)  # Cap at 1.5
            
            # Margin expansion potential
            margin_quality = 0
            if profit_margin > 10:
                margin_quality += 1
            if operating_margin > 15:
                margin_quality += 1
            if gross_margin > 25:
                margin_quality += 1
            
            # Efficiency indicators
            efficiency_score = margin_quality / 3  # Normalize to 0-1
            
            return {
                'roe': roe,
                'profit_margin': profit_margin,
                'operating_margin': operating_margin,
                'gross_margin': gross_margin,
                'profitability_score': profitability_score,
                'efficiency_score': efficiency_score,
                'margin_quality': margin_quality,
                'meets_profitability_criteria': (
                    roe >= self.min_roe and
                    profit_margin >= self.min_profit_margin
                )
            }
            
        except Exception as e:
            logger.error(f"Error analyzing profitability metrics: {str(e)}")
            return {}
    
    def analyze_financial_health(self, stock_info: Dict) -> Dict:
        """
        Analyze financial health and balance sheet strength
        
        Args:
            stock_info: Fundamental stock information
        
        Returns:
            Financial health analysis
        """
        try:
            # Extract financial health metrics
            debt_equity = stock_info.get('debt_equity_ratio', 999)
            current_ratio = stock_info.get('current_ratio', 0)
            pe_ratio = stock_info.get('pe_ratio', 999)
            pb_ratio = stock_info.get('pb_ratio', 999)
            
            # Financial health score
            health_score = 0
            
            # Debt management
            if debt_equity <= self.max_debt_equity:
                health_score += (self.max_debt_equity - debt_equity) * 4  # Reward low debt
            
            # Liquidity
            if current_ratio >= self.min_current_ratio:
                health_score += min((current_ratio - self.min_current_ratio) * 2, 2)
            
            # Valuation reasonableness for growth stock
            if 0 < pe_ratio <= self.max_pe_ratio:
                # Growth stocks can have higher P/E, but not excessive
                valuation_score = (self.max_pe_ratio - pe_ratio) / 10
                health_score += valuation_score
            
            # Balance sheet quality flags
            quality_flags = {
                'low_debt': debt_equity <= self.max_debt_equity,
                'good_liquidity': current_ratio >= self.min_current_ratio,
                'reasonable_pe': pe_ratio <= self.max_pe_ratio,
                'reasonable_pb': pb_ratio <= 5  # Growth stocks can have higher P/B
            }
            
            balance_sheet_quality = sum(quality_flags.values()) / len(quality_flags)
            
            return {
                'debt_equity': debt_equity,
                'current_ratio': current_ratio,
                'pe_ratio': pe_ratio,
                'pb_ratio': pb_ratio,
                'health_score': health_score,
                'balance_sheet_quality': balance_sheet_quality,
                'quality_flags': quality_flags,
                'meets_health_criteria': (
                    debt_equity <= self.max_debt_equity and
                    current_ratio >= self.min_current_ratio and
                    pe_ratio <= self.max_pe_ratio
                )
            }
            
        except Exception as e:
            logger.error(f"Error analyzing financial health: {str(e)}")
            return {}
    
    def calculate_growth_score(self, data: pd.DataFrame, stock_info: Dict) -> float:
        """
        Calculate overall fundamental growth score
        
        Args:
            data: Price data (for technical confirmation)
            stock_info: Fundamental information
        
        Returns:
            Growth score (higher indicates better growth opportunity)
        """
        try:
            # Get analysis components
            growth_analysis = self.analyze_growth_trends(stock_info)
            profitability_analysis = self.analyze_profitability_metrics(stock_info)
            health_analysis = self.analyze_financial_health(stock_info)
            
            if not all([growth_analysis, profitability_analysis, health_analysis]):
                return 0
            
            # Weighted scoring
            score = 0
            
            # 1. Growth trends (40% weight)
            growth_component = (
                growth_analysis.get('growth_consistency', 0) * 2 +
                growth_analysis.get('acceleration_score', 0) * 1.5 +
                growth_analysis.get('sustainability_score', 0) * 1
            )
            score += growth_component * 0.4
            
            # 2. Profitability (30% weight)
            profitability_component = (
                profitability_analysis.get('profitability_score', 0) +
                profitability_analysis.get('efficiency_score', 0) * 2
            )
            score += profitability_component * 0.3
            
            # 3. Financial health (20% weight)
            health_component = (
                health_analysis.get('health_score', 0) +
                health_analysis.get('balance_sheet_quality', 0) * 2
            )
            score += health_component * 0.2
            
            # 4. Technical confirmation (10% weight)
            if len(data) >= 20:
                latest = data.iloc[-1]
                sma_20 = latest.get('sma_20', latest['close'])
                
                # Price above moving average (growth momentum)
                if latest['close'] > sma_20:
                    score += 1 * 0.1
                
                # Volume confirmation
                if 'volume' in data.columns:
                    recent_volume = data.tail(10)['volume'].mean()
                    avg_volume = data['volume'].mean()
                    if recent_volume > avg_volume * 1.2:
                        score += 0.5 * 0.1
            
            # Bonus for exceptional growth
            if (growth_analysis.get('primary_growth', 0) > 40 and
                profitability_analysis.get('roe', 0) > 20):
                score += 1  # Bonus for exceptional growth with strong ROE
            
            return score
            
        except Exception as e:
            logger.error(f"Error calculating growth score: {str(e)}")
            return 0
    
    def generate_signal(self, symbol: str, data: pd.DataFrame, stock_info: Dict) -> Optional[Dict]:
        """
        Generate fundamental growth signal
        
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
            growth_score = self.calculate_growth_score(data, stock_info)
            
            # Get analysis components
            growth_analysis = self.analyze_growth_trends(stock_info)
            profitability_analysis = self.analyze_profitability_metrics(stock_info)
            health_analysis = self.analyze_financial_health(stock_info)
            
            # Fundamental growth criteria
            criteria_checks = [
                growth_score > 3.0,  # High growth score
                growth_analysis.get('meets_growth_criteria', False),
                profitability_analysis.get('meets_profitability_criteria', False),
                health_analysis.get('meets_health_criteria', False)
            ]
            
            # Must meet at least 3 out of 4 criteria
            if sum(criteria_checks) >= 3:
                
                # Calculate position parameters
                entry_price = current_price
                
                # Growth stocks can be more volatile, so wider stop loss
                atr = latest.get('atr', current_price * 0.03)
                stop_loss = current_price - (atr * 3)  # 3 ATR stop loss
                
                # Target based on growth potential
                pe_ratio = health_analysis.get('pe_ratio', 20)
                growth_rate = growth_analysis.get('primary_growth', 20)
                
                # Conservative target for growth stocks
                expected_growth_multiple = min(growth_rate / 20, 2.0)  # Cap at 2x
                target_price = current_price * (1 + expected_growth_multiple * 0.3)  # 30% of growth potential
                
                # Ensure minimum risk-reward
                risk_reward = (target_price - entry_price) / (entry_price - stop_loss)
                if risk_reward < 1.5:
                    target_price = entry_price + ((entry_price - stop_loss) * 1.5)
                
                # Position sizing
                risk_amount = 10000 * 0.015  # 1.5% risk for growth stocks
                risk_per_share = entry_price - stop_loss
                position_size = int(risk_amount / risk_per_share) if risk_per_share > 0 else 100
                
                signal = {
                    'signal_id': f"{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    'symbol': symbol,
                    'strategy': self.name,
                    'signal_type': 'BUY',
                    'entry_price': round(entry_price, 2),
                    'target_price': round(target_price, 2),
                    'stop_loss': round(stop_loss, 2),
                    'quantity': position_size,
                    'growth_score': round(growth_score, 2),
                    
                    # Growth metrics
                    'revenue_growth': round(growth_analysis.get('revenue_growth', 0), 2),
                    'earnings_growth': round(growth_analysis.get('earnings_growth', 0), 2),
                    'profit_growth': round(growth_analysis.get('profit_growth', 0), 2),
                    'primary_growth': round(growth_analysis.get('primary_growth', 0), 2),
                    'growth_consistency': round(growth_analysis.get('growth_consistency', 0), 2),
                    
                    # Profitability metrics
                    'roe': round(profitability_analysis.get('roe', 0), 2),
                    'profit_margin': round(profitability_analysis.get('profit_margin', 0), 2),
                    'operating_margin': round(profitability_analysis.get('operating_margin', 0), 2),
                    
                    # Financial health
                    'pe_ratio': round(health_analysis.get('pe_ratio', 0), 2),
                    'debt_equity': round(health_analysis.get('debt_equity', 0), 2),
                    'current_ratio': round(health_analysis.get('current_ratio', 0), 2),
                    'balance_sheet_quality': round(health_analysis.get('balance_sheet_quality', 0), 2),
                    
                    'timestamp': datetime.now().isoformat(),
                    'risk_reward_ratio': round((target_price - entry_price) / (entry_price - stop_loss), 2),
                    'sector': stock_info.get('sector', ''),
                    'market_cap': stock_info.get('market_cap', 0),
                    'confidence_score': min(growth_score / 6, 1.0),  # Normalize to 0-1
                    'validity_days': 60,  # Growth signals valid for 2 months
                    'strategy_reason': f'Strong fundamental growth with {growth_analysis.get("primary_growth", 0):.1f}% earnings growth',
                    'holding_period': '3-12 months',
                    'investment_thesis': self._generate_growth_thesis(growth_analysis, profitability_analysis, health_analysis)
                }
                
                logger.info(f"Generated GROWTH signal for {symbol} - Score: {growth_score}")
                return signal
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating growth signal for {symbol}: {str(e)}")
            return None
    
    def _generate_growth_thesis(self, growth_analysis: Dict, profitability_analysis: Dict, health_analysis: Dict) -> str:
        """Generate investment thesis for growth opportunity"""
        try:
            thesis_points = []
            
            # Growth highlights
            primary_growth = growth_analysis.get('primary_growth', 0)
            if primary_growth > 30:
                thesis_points.append(f"Exceptional earnings growth of {primary_growth:.1f}%")
            elif primary_growth > 20:
                thesis_points.append(f"Strong earnings growth of {primary_growth:.1f}%")
            
            revenue_growth = growth_analysis.get('revenue_growth', 0)
            if revenue_growth > 20:
                thesis_points.append(f"Revenue growth of {revenue_growth:.1f}%")
            
            # Profitability strengths
            roe = profitability_analysis.get('roe', 0)
            if roe > 20:
                thesis_points.append(f"High ROE of {roe:.1f}%")
            
            profit_margin = profitability_analysis.get('profit_margin', 0)
            if profit_margin > 15:
                thesis_points.append(f"Strong profit margins ({profit_margin:.1f}%)")
            
            # Financial health
            debt_equity = health_analysis.get('debt_equity', 1)
            if debt_equity < 0.3:
                thesis_points.append("Low debt levels")
            
            balance_sheet_quality = health_analysis.get('balance_sheet_quality', 0)
            if balance_sheet_quality > 0.8:
                thesis_points.append("Strong balance sheet")
            
            return "; ".join(thesis_points) if thesis_points else "Strong fundamental growth opportunity"
            
        except Exception:
            return "Consistent fundamental growth with strong profitability"
    
    def get_strategy_params(self) -> Dict:
        """Return strategy parameters for configuration"""
        return {
            'name': self.name,
            'min_revenue_growth': self.min_revenue_growth,
            'min_earnings_growth': self.min_earnings_growth,
            'min_roe': self.min_roe,
            'max_pe_ratio': self.max_pe_ratio,
            'min_profit_margin': self.min_profit_margin,
            'max_debt_equity': self.max_debt_equity,
            'min_current_ratio': self.min_current_ratio,
            'growth_acceleration_threshold': self.growth_acceleration_threshold,
            'quality_score_threshold': self.quality_score_threshold
        }
    
    def backtest_signal(self, data: pd.DataFrame, entry_date: str, exit_days: int = 180) -> Dict:
        """
        Backtest a fundamental growth signal
        
        Args:
            data: Historical price data
            entry_date: Date when signal was generated
            exit_days: Number of days to hold (6 months default for growth)
        
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
            
            # Annualized return
            holding_days = exit_idx - entry_idx
            annualized_return = ((exit_price / entry_price) ** (365 / holding_days) - 1) * 100 if holding_days > 0 else 0
            
            # Growth-specific metrics
            holding_data = data.iloc[entry_idx:exit_idx + 1]
            
            # Maximum gain during holding period
            max_price = holding_data['high'].max()
            max_gain = ((max_price - entry_price) / entry_price) * 100
            
            # Maximum drawdown
            cumulative_returns = (holding_data['close'] / entry_price - 1) * 100
            max_drawdown = cumulative_returns.min()
            
            # Growth momentum (did the stock continue growing?)
            final_momentum = (holding_data['close'].iloc[-1] - holding_data['close'].iloc[0]) / holding_data['close'].iloc[0] * 100
            
            # Volatility during holding period
            daily_returns = holding_data['close'].pct_change().dropna()
            volatility = daily_returns.std() * np.sqrt(252) * 100  # Annualized volatility
            
            return {
                'entry_price': entry_price,
                'exit_price': exit_price,
                'absolute_return': absolute_return,
                'percentage_return': percentage_return,
                'annualized_return': annualized_return,
                'max_gain': max_gain,
                'max_drawdown': max_drawdown,
                'volatility': volatility,
                'final_momentum': final_momentum,
                'holding_days': holding_days,
                'success': percentage_return > 0,
                'strong_growth': percentage_return > 15,  # 15%+ considered strong for growth
                'beat_market': annualized_return > 12,  # Beat typical market return
                'strategy_type': 'fundamental_growth'
            }
            
        except Exception as e:
            logger.error(f"Error in fundamental growth backtesting: {str(e)}")
            return {}
