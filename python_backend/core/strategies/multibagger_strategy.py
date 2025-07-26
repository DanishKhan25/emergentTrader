"""
Multibagger Strategy - Identifies stocks with potential for multi-fold returns (2x, 3x, 5x+)
Focuses on small/mid-cap stocks with strong fundamentals and emerging growth trends
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class MultibaggerStrategy:
    def __init__(self, name: str = "Multibagger"):
        self.name = name
        self.max_market_cap = 50000000000  # 50B INR (focus on small/mid cap)
        self.min_revenue_growth = 20  # Minimum 20% revenue growth
        self.min_profit_growth = 25  # Minimum 25% profit growth
        self.max_pe_ratio = 25  # Not too expensive
        self.min_roe = 15  # Strong return on equity
        self.max_debt_equity = 0.6  # Manageable debt levels
        self.min_price_momentum = 0.15  # 15% price momentum over 6 months
        self.volume_surge_threshold = 2.0  # 2x volume surge
        self.breakout_threshold = 0.10  # 10% breakout from consolidation
        self.min_consolidation_days = 30  # Minimum consolidation period
        
    def analyze_growth_metrics(self, stock_info: Dict) -> Dict:
        """
        Analyze growth metrics for multibagger potential
        
        Args:
            stock_info: Fundamental stock information
        
        Returns:
            Growth analysis results
        """
        try:
            # Extract growth metrics
            revenue_growth = stock_info.get('revenue_growth', 0)
            profit_growth = stock_info.get('profit_growth', 0)
            earnings_growth = stock_info.get('earnings_growth', 0)
            
            # Market cap analysis
            market_cap = stock_info.get('market_cap', 0)
            
            # Determine market cap category
            if market_cap < 5000000000:  # < 5B INR
                cap_category = 'SMALL_CAP'
                growth_multiplier = 1.5  # Higher potential
            elif market_cap < 20000000000:  # < 20B INR
                cap_category = 'MID_CAP'
                growth_multiplier = 1.2
            else:
                cap_category = 'LARGE_CAP'
                growth_multiplier = 0.8  # Lower multibagger potential
            
            # Growth consistency score
            growth_scores = []
            if revenue_growth > 0:
                growth_scores.append(min(revenue_growth / 30, 2))  # Cap at 2x
            if profit_growth > 0:
                growth_scores.append(min(profit_growth / 40, 2))
            if earnings_growth > 0:
                growth_scores.append(min(earnings_growth / 35, 2))
            
            growth_consistency = np.mean(growth_scores) if growth_scores else 0
            
            # Acceleration score (higher growth = higher score)
            acceleration_score = 0
            if revenue_growth > 30:
                acceleration_score += 1
            if profit_growth > 40:
                acceleration_score += 1
            if earnings_growth > 35:
                acceleration_score += 1
            
            return {
                'revenue_growth': revenue_growth,
                'profit_growth': profit_growth,
                'earnings_growth': earnings_growth,
                'market_cap': market_cap,
                'cap_category': cap_category,
                'growth_multiplier': growth_multiplier,
                'growth_consistency': growth_consistency,
                'acceleration_score': acceleration_score,
                'meets_growth_criteria': (
                    revenue_growth >= self.min_revenue_growth and
                    profit_growth >= self.min_profit_growth
                )
            }
            
        except Exception as e:
            logger.error(f"Error analyzing growth metrics: {str(e)}")
            return {}
    
    def analyze_financial_strength(self, stock_info: Dict) -> Dict:
        """
        Analyze financial strength for sustainable growth
        
        Args:
            stock_info: Fundamental stock information
        
        Returns:
            Financial strength analysis
        """
        try:
            pe_ratio = stock_info.get('pe_ratio', 999)
            pb_ratio = stock_info.get('pb_ratio', 999)
            roe = stock_info.get('roe', 0)
            debt_equity = stock_info.get('debt_equity_ratio', 999)
            current_ratio = stock_info.get('current_ratio', 0)
            
            # Financial strength score
            strength_score = 0
            
            # Valuation score (not too expensive)
            if 0 < pe_ratio <= self.max_pe_ratio:
                strength_score += (self.max_pe_ratio - pe_ratio) / 10
            
            if 0 < pb_ratio <= 3:
                strength_score += (3 - pb_ratio) / 2
            
            # Profitability score
            if roe >= self.min_roe:
                strength_score += min((roe - self.min_roe) / 10, 2)
            
            # Debt management score
            if debt_equity <= self.max_debt_equity:
                strength_score += (self.max_debt_equity - debt_equity) * 3
            
            # Liquidity score
            if current_ratio >= 1.2:
                strength_score += min((current_ratio - 1.2) * 2, 1.5)
            
            # Quality flags
            quality_flags = {
                'reasonable_valuation': pe_ratio <= self.max_pe_ratio,
                'strong_roe': roe >= self.min_roe,
                'manageable_debt': debt_equity <= self.max_debt_equity,
                'good_liquidity': current_ratio >= 1.2,
                'not_overvalued': pb_ratio <= 3
            }
            
            quality_score = sum(quality_flags.values()) / len(quality_flags)
            
            return {
                'strength_score': strength_score,
                'quality_score': quality_score,
                'quality_flags': quality_flags,
                'pe_ratio': pe_ratio,
                'roe': roe,
                'debt_equity': debt_equity,
                'meets_financial_criteria': (
                    pe_ratio <= self.max_pe_ratio and
                    roe >= self.min_roe and
                    debt_equity <= self.max_debt_equity
                )
            }
            
        except Exception as e:
            logger.error(f"Error analyzing financial strength: {str(e)}")
            return {}
    
    def analyze_price_action(self, data: pd.DataFrame) -> Dict:
        """
        Analyze price action for multibagger setup
        
        Args:
            data: Historical price data
        
        Returns:
            Price action analysis
        """
        try:
            if len(data) < 180:  # Need at least 6 months of data
                return {}
            
            latest = data.iloc[-1]
            current_price = latest['close']
            
            # Long-term momentum (6 months)
            six_months_ago = data.iloc[-126] if len(data) >= 126 else data.iloc[0]
            long_term_momentum = (current_price - six_months_ago['close']) / six_months_ago['close']
            
            # Medium-term momentum (3 months)
            three_months_ago = data.iloc[-63] if len(data) >= 63 else data.iloc[0]
            medium_term_momentum = (current_price - three_months_ago['close']) / three_months_ago['close']
            
            # Recent consolidation analysis
            recent_data = data.tail(60)  # Last 60 days
            recent_high = recent_data['high'].max()
            recent_low = recent_data['low'].min()
            consolidation_range = (recent_high - recent_low) / recent_low
            
            # Volume analysis
            recent_volume = data.tail(20)['volume'].mean() if 'volume' in data.columns else 0
            avg_volume = data['volume'].mean() if 'volume' in data.columns else 1
            volume_surge = recent_volume / avg_volume if avg_volume > 0 else 1
            
            # Breakout analysis
            consolidation_high = recent_data.iloc[:-5]['high'].max()  # Exclude last 5 days
            is_breaking_out = current_price > consolidation_high * (1 + self.breakout_threshold)
            
            # Support/resistance levels
            support_level = recent_low
            resistance_level = recent_high
            price_position = (current_price - support_level) / (resistance_level - support_level) if resistance_level > support_level else 0.5
            
            # Accumulation phase detection (low volatility + volume increase)
            volatility = recent_data['close'].std() / recent_data['close'].mean()
            is_accumulating = volatility < 0.05 and volume_surge > 1.2
            
            return {
                'long_term_momentum': long_term_momentum,
                'medium_term_momentum': medium_term_momentum,
                'consolidation_range': consolidation_range,
                'volume_surge': volume_surge,
                'is_breaking_out': is_breaking_out,
                'is_accumulating': is_accumulating,
                'price_position': price_position,
                'support_level': support_level,
                'resistance_level': resistance_level,
                'volatility': volatility,
                'meets_momentum_criteria': long_term_momentum >= self.min_price_momentum
            }
            
        except Exception as e:
            logger.error(f"Error analyzing price action: {str(e)}")
            return {}
    
    def calculate_multibagger_score(self, data: pd.DataFrame, stock_info: Dict) -> float:
        """
        Calculate multibagger potential score
        
        Args:
            data: Price data
            stock_info: Fundamental information
        
        Returns:
            Multibagger score (higher indicates better potential)
        """
        try:
            # Get analysis components
            growth_analysis = self.analyze_growth_metrics(stock_info)
            financial_analysis = self.analyze_financial_strength(stock_info)
            price_analysis = self.analyze_price_action(data)
            
            if not all([growth_analysis, financial_analysis, price_analysis]):
                return 0
            
            # Score components (weighted)
            score = 0
            
            # 1. Growth potential (40% weight)
            growth_score = (
                growth_analysis.get('growth_consistency', 0) * 2 +
                growth_analysis.get('acceleration_score', 0) * 1.5 +
                growth_analysis.get('growth_multiplier', 1) * 1
            )
            score += growth_score * 0.4
            
            # 2. Financial strength (25% weight)
            financial_score = (
                financial_analysis.get('strength_score', 0) +
                financial_analysis.get('quality_score', 0) * 2
            )
            score += financial_score * 0.25
            
            # 3. Price momentum (20% weight)
            momentum_score = (
                max(price_analysis.get('long_term_momentum', 0) * 5, 0) +
                max(price_analysis.get('medium_term_momentum', 0) * 3, 0)
            )
            score += momentum_score * 0.2
            
            # 4. Technical setup (15% weight)
            technical_score = 0
            if price_analysis.get('is_breaking_out', False):
                technical_score += 2
            if price_analysis.get('is_accumulating', False):
                technical_score += 1.5
            if price_analysis.get('volume_surge', 0) > self.volume_surge_threshold:
                technical_score += 1
            
            score += technical_score * 0.15
            
            # Bonus for small/mid cap with exceptional growth
            if (growth_analysis.get('cap_category') in ['SMALL_CAP', 'MID_CAP'] and
                growth_analysis.get('profit_growth', 0) > 50):
                score += 1  # Bonus for exceptional growth in smaller companies
            
            return score
            
        except Exception as e:
            logger.error(f"Error calculating multibagger score: {str(e)}")
            return 0
    
    def generate_signal(self, symbol: str, data: pd.DataFrame, stock_info: Dict) -> Optional[Dict]:
        """
        Generate multibagger signal
        
        Args:
            symbol: Stock symbol
            data: Historical price data with indicators
            stock_info: Fundamental stock information
        
        Returns:
            Signal dictionary or None if no signal
        """
        if data.empty or len(data) < 180:  # Need sufficient history
            return None
        
        try:
            latest = data.iloc[-1]
            current_price = latest['close']
            multibagger_score = self.calculate_multibagger_score(data, stock_info)
            
            # Get analysis components
            growth_analysis = self.analyze_growth_metrics(stock_info)
            financial_analysis = self.analyze_financial_strength(stock_info)
            price_analysis = self.analyze_price_action(data)
            
            # Multibagger criteria
            criteria_met = [
                multibagger_score > 4.0,  # High overall score
                growth_analysis.get('meets_growth_criteria', False),
                financial_analysis.get('meets_financial_criteria', False),
                price_analysis.get('meets_momentum_criteria', False),
                stock_info.get('market_cap', 0) <= self.max_market_cap
            ]
            
            # Must meet at least 4 out of 5 criteria
            if sum(criteria_met) >= 4:
                
                # Calculate position sizing (larger for multibaggers)
                entry_price = current_price
                
                # Conservative stop loss for long-term holding
                support_level = price_analysis.get('support_level', current_price * 0.8)
                stop_loss = min(support_level * 0.95, current_price * 0.8)  # Max 20% stop loss
                
                # Multiple targets for multibagger potential
                target_1 = current_price * 2.0   # 2x (100% return)
                target_2 = current_price * 3.0   # 3x (200% return)
                target_3 = current_price * 5.0   # 5x (400% return)
                
                # Position size (smaller due to higher risk)
                risk_amount = 10000 * 0.02  # 2% risk for multibagger bets
                risk_per_share = entry_price - stop_loss
                position_size = int(risk_amount / risk_per_share) if risk_per_share > 0 else 50
                
                signal = {
                    'signal_id': f"{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    'symbol': symbol,
                    'strategy': self.name,
                    'signal_type': 'BUY',
                    'entry_price': round(entry_price, 2),
                    'target_price': round(target_1, 2),  # Primary target
                    'target_2': round(target_2, 2),
                    'target_3': round(target_3, 2),
                    'stop_loss': round(stop_loss, 2),
                    'quantity': position_size,
                    'multibagger_score': round(multibagger_score, 2),
                    
                    # Growth metrics
                    'revenue_growth': round(growth_analysis.get('revenue_growth', 0), 2),
                    'profit_growth': round(growth_analysis.get('profit_growth', 0), 2),
                    'market_cap_category': growth_analysis.get('cap_category', 'UNKNOWN'),
                    'growth_consistency': round(growth_analysis.get('growth_consistency', 0), 2),
                    
                    # Financial metrics
                    'pe_ratio': round(financial_analysis.get('pe_ratio', 0), 2),
                    'roe': round(financial_analysis.get('roe', 0), 2),
                    'debt_equity': round(financial_analysis.get('debt_equity', 0), 2),
                    'financial_strength': round(financial_analysis.get('strength_score', 0), 2),
                    
                    # Price action
                    'long_term_momentum': round(price_analysis.get('long_term_momentum', 0) * 100, 2),
                    'volume_surge': round(price_analysis.get('volume_surge', 0), 2),
                    'is_breaking_out': price_analysis.get('is_breaking_out', False),
                    'is_accumulating': price_analysis.get('is_accumulating', False),
                    
                    'timestamp': datetime.now().isoformat(),
                    'risk_reward_ratio': round((target_1 - entry_price) / (entry_price - stop_loss), 2),
                    'sector': stock_info.get('sector', ''),
                    'market_cap': stock_info.get('market_cap', 0),
                    'confidence_score': min(multibagger_score / 8, 1.0),  # Normalize to 0-1
                    'validity_days': 90,  # Multibagger signals valid for 3 months
                    'strategy_reason': f'Multibagger potential in {growth_analysis.get("cap_category", "").lower().replace("_", " ")} stock',
                    'holding_period': '6 months to 3 years',
                    'investment_thesis': self._generate_multibagger_thesis(growth_analysis, financial_analysis, price_analysis)
                }
                
                logger.info(f"Generated MULTIBAGGER signal for {symbol} - Score: {multibagger_score}")
                return signal
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating multibagger signal for {symbol}: {str(e)}")
            return None
    
    def _generate_multibagger_thesis(self, growth_analysis: Dict, financial_analysis: Dict, price_analysis: Dict) -> str:
        """Generate investment thesis for multibagger opportunity"""
        try:
            thesis_points = []
            
            # Growth story
            if growth_analysis.get('profit_growth', 0) > 40:
                thesis_points.append(f"Exceptional profit growth of {growth_analysis['profit_growth']:.1f}%")
            
            if growth_analysis.get('cap_category') == 'SMALL_CAP':
                thesis_points.append("Small-cap with high growth potential")
            elif growth_analysis.get('cap_category') == 'MID_CAP':
                thesis_points.append("Mid-cap in expansion phase")
            
            # Financial strength
            if financial_analysis.get('roe', 0) > 20:
                thesis_points.append(f"Strong ROE of {financial_analysis['roe']:.1f}%")
            
            if financial_analysis.get('debt_equity', 1) < 0.3:
                thesis_points.append("Conservative debt management")
            
            # Technical setup
            if price_analysis.get('is_breaking_out'):
                thesis_points.append("Breaking out of consolidation")
            
            if price_analysis.get('volume_surge', 0) > 2:
                thesis_points.append("Strong volume accumulation")
            
            if price_analysis.get('long_term_momentum', 0) > 0.3:
                thesis_points.append("Strong 6-month price momentum")
            
            return "; ".join(thesis_points) if thesis_points else "Multibagger potential identified"
            
        except Exception:
            return "Multibagger opportunity with strong growth fundamentals"
    
    def get_strategy_params(self) -> Dict:
        """Return strategy parameters for configuration"""
        return {
            'name': self.name,
            'max_market_cap': self.max_market_cap,
            'min_revenue_growth': self.min_revenue_growth,
            'min_profit_growth': self.min_profit_growth,
            'max_pe_ratio': self.max_pe_ratio,
            'min_roe': self.min_roe,
            'max_debt_equity': self.max_debt_equity,
            'min_price_momentum': self.min_price_momentum,
            'volume_surge_threshold': self.volume_surge_threshold,
            'breakout_threshold': self.breakout_threshold
        }
    
    def backtest_signal(self, data: pd.DataFrame, entry_date: str, exit_days: int = 365) -> Dict:
        """
        Backtest a multibagger signal (longer holding period)
        
        Args:
            data: Historical price data
            entry_date: Date when signal was generated
            exit_days: Number of days to hold (1 year default for multibaggers)
        
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
            
            # Track multibagger achievements
            holding_data = data.iloc[entry_idx:exit_idx + 1]
            max_price = holding_data['high'].max()
            max_return = ((max_price - entry_price) / entry_price) * 100
            
            # Multibagger milestones
            achieved_2x = max_return >= 100  # 2x return
            achieved_3x = max_return >= 200  # 3x return
            achieved_5x = max_return >= 400  # 5x return
            
            # Drawdown analysis
            cumulative_returns = (holding_data['close'] / entry_price - 1) * 100
            max_drawdown = cumulative_returns.min()
            
            # Time to achieve milestones
            time_to_2x = None
            if achieved_2x:
                double_price = entry_price * 2
                double_idx = holding_data[holding_data['high'] >= double_price].index
                if len(double_idx) > 0:
                    time_to_2x = double_idx[0] - entry_idx
            
            return {
                'entry_price': entry_price,
                'exit_price': exit_price,
                'absolute_return': absolute_return,
                'percentage_return': percentage_return,
                'annualized_return': annualized_return,
                'max_return': max_return,
                'max_drawdown': max_drawdown,
                'achieved_2x': achieved_2x,
                'achieved_3x': achieved_3x,
                'achieved_5x': achieved_5x,
                'time_to_2x': time_to_2x,
                'holding_days': holding_days,
                'success': percentage_return > 0,
                'multibagger_success': achieved_2x,
                'strategy_type': 'multibagger'
            }
            
        except Exception as e:
            logger.error(f"Error in multibagger backtesting: {str(e)}")
            return {}
