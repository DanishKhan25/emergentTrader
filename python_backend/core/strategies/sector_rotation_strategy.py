"""
Sector Rotation Strategy - Identifies sectors showing relative strength and momentum
Focuses on stocks in outperforming sectors with strong relative performance
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class SectorRotationStrategy:
    def __init__(self, name: str = "Sector Rotation"):
        self.name = name
        self.sector_momentum_period = 60  # Days to analyze sector momentum
        self.relative_strength_period = 30  # Days for relative strength calculation
        self.min_sector_outperformance = 0.05  # 5% minimum sector outperformance
        self.min_stock_relative_strength = 0.03  # 3% minimum stock relative strength vs sector
        self.volume_confirmation_threshold = 1.3  # Volume surge confirmation
        self.sector_trend_threshold = 0.02  # 2% sector trend strength
        
        # Define major sectors for rotation analysis
        self.major_sectors = {
            'Technology': ['INFY', 'TCS', 'WIPRO', 'HCLTECH', 'TECHM'],
            'Banking': ['HDFCBANK', 'ICICIBANK', 'KOTAKBANK', 'SBIN', 'AXISBANK'],
            'Pharmaceuticals': ['SUNPHARMA', 'DIVISLAB', 'DRREDDY', 'CIPLA', 'BIOCON'],
            'Automobile': ['MARUTI', 'TATAMOTORS', 'M&M', 'BAJAJ-AUTO', 'EICHERMOT'],
            'FMCG': ['HINDUNILVR', 'ITC', 'NESTLEIND', 'BRITANNIA', 'DABUR'],
            'Energy': ['RELIANCE', 'ONGC', 'IOC', 'BPCL', 'GAIL'],
            'Metals': ['TATASTEEL', 'JSWSTEEL', 'HINDALCO', 'VEDL', 'COALINDIA'],
            'Telecom': ['BHARTIARTL', 'IDEA', 'RCOM'],
            'Infrastructure': ['LT', 'UBL', 'GRASIM', 'ACC', 'AMBUJACEMENT']
        }
        
    def get_sector_performance(self, sector_stocks: List[str], market_data: Dict[str, pd.DataFrame]) -> Dict:
        """
        Calculate sector performance metrics
        
        Args:
            sector_stocks: List of stock symbols in the sector
            market_data: Dictionary mapping symbols to their price data
        
        Returns:
            Sector performance analysis
        """
        try:
            if not sector_stocks or not market_data:
                return {}
            
            # Get available stocks with data
            available_stocks = [stock for stock in sector_stocks if stock in market_data and not market_data[stock].empty]
            
            if len(available_stocks) < 2:  # Need at least 2 stocks for sector analysis
                return {}
            
            # Calculate sector index (equal weighted average)
            sector_returns = []
            sector_volumes = []
            
            for stock in available_stocks:
                stock_data = market_data[stock]
                if len(stock_data) >= self.sector_momentum_period:
                    # Calculate stock returns
                    recent_data = stock_data.tail(self.sector_momentum_period)
                    stock_return = (recent_data.iloc[-1]['close'] - recent_data.iloc[0]['close']) / recent_data.iloc[0]['close']
                    sector_returns.append(stock_return)
                    
                    # Average volume
                    if 'volume' in stock_data.columns:
                        avg_volume = recent_data['volume'].mean()
                        sector_volumes.append(avg_volume)
            
            if not sector_returns:
                return {}
            
            # Sector performance metrics
            sector_return = np.mean(sector_returns)
            sector_volatility = np.std(sector_returns)
            sector_consistency = len([r for r in sector_returns if r > 0]) / len(sector_returns)
            
            # Recent momentum (last 30 days vs previous 30 days)
            recent_returns = []
            previous_returns = []
            
            for stock in available_stocks:
                stock_data = market_data[stock]
                if len(stock_data) >= 60:
                    recent_30 = stock_data.tail(30)
                    previous_30 = stock_data.iloc[-60:-30]
                    
                    recent_ret = (recent_30.iloc[-1]['close'] - recent_30.iloc[0]['close']) / recent_30.iloc[0]['close']
                    prev_ret = (previous_30.iloc[-1]['close'] - previous_30.iloc[0]['close']) / previous_30.iloc[0]['close']
                    
                    recent_returns.append(recent_ret)
                    previous_returns.append(prev_ret)
            
            momentum_acceleration = 0
            if recent_returns and previous_returns:
                recent_avg = np.mean(recent_returns)
                previous_avg = np.mean(previous_returns)
                momentum_acceleration = recent_avg - previous_avg
            
            return {
                'sector_return': sector_return,
                'sector_volatility': sector_volatility,
                'sector_consistency': sector_consistency,
                'momentum_acceleration': momentum_acceleration,
                'available_stocks': len(available_stocks),
                'total_stocks': len(sector_stocks),
                'coverage_ratio': len(available_stocks) / len(sector_stocks)
            }
            
        except Exception as e:
            logger.error(f"Error calculating sector performance: {str(e)}")
            return {}
    
    def analyze_market_sectors(self, market_data: Dict[str, pd.DataFrame]) -> Dict:
        """
        Analyze all sectors for rotation opportunities
        
        Args:
            market_data: Dictionary mapping symbols to their price data
        
        Returns:
            Sector analysis results
        """
        try:
            sector_analysis = {}
            
            # Analyze each sector
            for sector_name, sector_stocks in self.major_sectors.items():
                sector_perf = self.get_sector_performance(sector_stocks, market_data)
                if sector_perf:
                    sector_analysis[sector_name] = sector_perf
            
            if not sector_analysis:
                return {}
            
            # Rank sectors by performance
            sector_rankings = []
            for sector, metrics in sector_analysis.items():
                sector_score = (
                    metrics.get('sector_return', 0) * 0.4 +
                    metrics.get('momentum_acceleration', 0) * 0.3 +
                    metrics.get('sector_consistency', 0) * 0.2 +
                    (1 - metrics.get('sector_volatility', 1)) * 0.1
                )
                
                sector_rankings.append({
                    'sector': sector,
                    'score': sector_score,
                    'return': metrics.get('sector_return', 0),
                    'momentum': metrics.get('momentum_acceleration', 0),
                    'consistency': metrics.get('sector_consistency', 0),
                    'volatility': metrics.get('sector_volatility', 0)
                })
            
            # Sort by score (best performing first)
            sector_rankings.sort(key=lambda x: x['score'], reverse=True)
            
            # Identify top and bottom sectors
            top_sectors = sector_rankings[:3]  # Top 3 sectors
            bottom_sectors = sector_rankings[-2:]  # Bottom 2 sectors
            
            return {
                'sector_analysis': sector_analysis,
                'sector_rankings': sector_rankings,
                'top_sectors': top_sectors,
                'bottom_sectors': bottom_sectors,
                'market_breadth': len(sector_analysis)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing market sectors: {str(e)}")
            return {}
    
    def calculate_relative_strength(self, stock_data: pd.DataFrame, sector_performance: Dict) -> Dict:
        """
        Calculate stock's relative strength vs its sector
        
        Args:
            stock_data: Individual stock price data
            sector_performance: Sector performance metrics
        
        Returns:
            Relative strength analysis
        """
        try:
            if stock_data.empty or not sector_performance:
                return {}
            
            # Stock performance over relative strength period
            rs_data = stock_data.tail(self.relative_strength_period)
            if len(rs_data) < self.relative_strength_period:
                return {}
            
            stock_return = (rs_data.iloc[-1]['close'] - rs_data.iloc[0]['close']) / rs_data.iloc[0]['close']
            sector_return = sector_performance.get('sector_return', 0)
            
            # Relative strength vs sector
            relative_strength = stock_return - sector_return
            
            # Relative strength trend (improving or deteriorating)
            if len(stock_data) >= 60:
                # Compare recent RS vs previous RS
                recent_data = stock_data.tail(30)
                previous_data = stock_data.iloc[-60:-30]
                
                recent_stock_ret = (recent_data.iloc[-1]['close'] - recent_data.iloc[0]['close']) / recent_data.iloc[0]['close']
                prev_stock_ret = (previous_data.iloc[-1]['close'] - previous_data.iloc[0]['close']) / previous_data.iloc[0]['close']
                
                # Assume sector had similar trend for simplicity
                rs_trend = (recent_stock_ret - prev_stock_ret)
            else:
                rs_trend = 0
            
            # Price momentum confirmation
            latest = stock_data.iloc[-1]
            sma_20 = latest.get('sma_20', latest['close'])
            price_momentum = (latest['close'] - sma_20) / sma_20
            
            return {
                'stock_return': stock_return,
                'sector_return': sector_return,
                'relative_strength': relative_strength,
                'rs_trend': rs_trend,
                'price_momentum': price_momentum,
                'outperforming_sector': relative_strength > self.min_stock_relative_strength
            }
            
        except Exception as e:
            logger.error(f"Error calculating relative strength: {str(e)}")
            return {}
    
    def calculate_rotation_score(self, stock_data: pd.DataFrame, stock_info: Dict, market_analysis: Dict) -> float:
        """
        Calculate sector rotation score for a stock
        
        Args:
            stock_data: Stock price data
            stock_info: Stock fundamental information
            market_analysis: Market sector analysis
        
        Returns:
            Rotation score (higher indicates better rotation opportunity)
        """
        try:
            if stock_data.empty or not market_analysis:
                return 0
            
            # Identify stock's sector
            stock_sector = stock_info.get('sector', 'Unknown')
            
            # Find matching sector in our analysis
            sector_match = None
            for sector_name in self.major_sectors.keys():
                if sector_name.lower() in stock_sector.lower() or stock_sector.lower() in sector_name.lower():
                    sector_match = sector_name
                    break
            
            if not sector_match or sector_match not in market_analysis.get('sector_analysis', {}):
                return 0
            
            sector_performance = market_analysis['sector_analysis'][sector_match]
            
            # Check if sector is in top performers
            top_sectors = [s['sector'] for s in market_analysis.get('top_sectors', [])]
            is_top_sector = sector_match in top_sectors
            
            if not is_top_sector:
                return 0  # Only consider stocks in top-performing sectors
            
            # Calculate relative strength
            rs_analysis = self.calculate_relative_strength(stock_data, sector_performance)
            if not rs_analysis:
                return 0
            
            # Score components
            score = 0
            
            # 1. Sector strength (40% weight)
            sector_score = (
                sector_performance.get('sector_return', 0) * 10 +
                sector_performance.get('momentum_acceleration', 0) * 5 +
                sector_performance.get('sector_consistency', 0) * 2
            )
            score += sector_score * 0.4
            
            # 2. Relative strength (30% weight)
            rs_score = (
                rs_analysis.get('relative_strength', 0) * 10 +
                rs_analysis.get('rs_trend', 0) * 5
            )
            score += rs_score * 0.3
            
            # 3. Individual stock momentum (20% weight)
            momentum_score = rs_analysis.get('price_momentum', 0) * 10
            score += momentum_score * 0.2
            
            # 4. Volume confirmation (10% weight)
            if 'volume' in stock_data.columns and len(stock_data) >= 20:
                recent_volume = stock_data.tail(10)['volume'].mean()
                avg_volume = stock_data['volume'].mean()
                volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 1
                
                if volume_ratio > self.volume_confirmation_threshold:
                    score += 1 * 0.1
            
            # Bonus for being in #1 sector
            top_sector_rankings = market_analysis.get('top_sectors', [])
            if top_sector_rankings and top_sector_rankings[0]['sector'] == sector_match:
                score += 0.5  # Bonus for being in the top sector
            
            return score
            
        except Exception as e:
            logger.error(f"Error calculating rotation score: {str(e)}")
            return 0
    
    def generate_signal(self, symbol: str, data: pd.DataFrame, stock_info: Dict, market_analysis: Optional[Dict] = None) -> Optional[Dict]:
        """
        Generate sector rotation signal
        
        Args:
            symbol: Stock symbol
            data: Historical price data with indicators
            stock_info: Fundamental stock information
            market_analysis: Market sector analysis (if available)
        
        Returns:
            Signal dictionary or None if no signal
        """
        if data.empty or len(data) < self.sector_momentum_period:
            return None
        
        # If no market analysis provided, we can't do sector rotation
        if not market_analysis:
            return None
        
        try:
            latest = data.iloc[-1]
            current_price = latest['close']
            rotation_score = self.calculate_rotation_score(data, stock_info, market_analysis)
            
            # Sector rotation criteria
            if rotation_score > 2.0:  # Minimum rotation score threshold
                
                # Identify stock's sector
                stock_sector = stock_info.get('sector', 'Unknown')
                sector_match = None
                for sector_name in self.major_sectors.keys():
                    if sector_name.lower() in stock_sector.lower() or stock_sector.lower() in sector_name.lower():
                        sector_match = sector_name
                        break
                
                if not sector_match:
                    return None
                
                sector_performance = market_analysis['sector_analysis'].get(sector_match, {})
                rs_analysis = self.calculate_relative_strength(data, sector_performance)
                
                # Calculate position parameters
                entry_price = current_price
                atr = latest.get('atr', current_price * 0.02)
                
                # Sector rotation typically has medium-term holding period
                stop_loss = current_price - (atr * 2.5)  # 2.5 ATR stop
                
                # Target based on sector momentum
                sector_return = sector_performance.get('sector_return', 0.1)
                expected_move = max(sector_return * 0.5, 0.08)  # At least 8% target
                target_price = current_price * (1 + expected_move)
                
                # Position sizing
                risk_amount = 10000 * 0.015  # 1.5% risk
                risk_per_share = entry_price - stop_loss
                position_size = int(risk_amount / risk_per_share) if risk_per_share > 0 else 100
                
                # Get sector ranking
                sector_rank = None
                for i, sector_data in enumerate(market_analysis.get('top_sectors', []), 1):
                    if sector_data['sector'] == sector_match:
                        sector_rank = i
                        break
                
                signal = {
                    'signal_id': f"{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    'symbol': symbol,
                    'strategy': self.name,
                    'signal_type': 'BUY',
                    'entry_price': round(entry_price, 2),
                    'target_price': round(target_price, 2),
                    'stop_loss': round(stop_loss, 2),
                    'quantity': position_size,
                    'rotation_score': round(rotation_score, 2),
                    
                    # Sector information
                    'sector': sector_match,
                    'sector_rank': sector_rank,
                    'sector_return': round(sector_performance.get('sector_return', 0) * 100, 2),
                    'sector_momentum': round(sector_performance.get('momentum_acceleration', 0) * 100, 2),
                    'sector_consistency': round(sector_performance.get('sector_consistency', 0) * 100, 2),
                    
                    # Relative strength
                    'relative_strength': round(rs_analysis.get('relative_strength', 0) * 100, 2),
                    'stock_vs_sector': round(rs_analysis.get('stock_return', 0) * 100, 2),
                    'outperforming_sector': rs_analysis.get('outperforming_sector', False),
                    
                    'timestamp': datetime.now().isoformat(),
                    'risk_reward_ratio': round((target_price - entry_price) / (entry_price - stop_loss), 2),
                    'market_cap': stock_info.get('market_cap', 0),
                    'confidence_score': min(rotation_score / 4, 1.0),  # Normalize to 0-1
                    'validity_days': 45,  # Sector rotation signals valid for 1.5 months
                    'strategy_reason': f'Strong sector rotation into {sector_match} (rank #{sector_rank})',
                    'holding_period': '1-3 months'
                }
                
                logger.info(f"Generated SECTOR ROTATION signal for {symbol} in {sector_match} - Score: {rotation_score}")
                return signal
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating sector rotation signal for {symbol}: {str(e)}")
            return None
    
    def get_strategy_params(self) -> Dict:
        """Return strategy parameters for configuration"""
        return {
            'name': self.name,
            'sector_momentum_period': self.sector_momentum_period,
            'relative_strength_period': self.relative_strength_period,
            'min_sector_outperformance': self.min_sector_outperformance,
            'min_stock_relative_strength': self.min_stock_relative_strength,
            'volume_confirmation_threshold': self.volume_confirmation_threshold,
            'sector_trend_threshold': self.sector_trend_threshold,
            'major_sectors': list(self.major_sectors.keys())
        }
    
    def backtest_signal(self, data: pd.DataFrame, entry_date: str, exit_days: int = 60) -> Dict:
        """
        Backtest a sector rotation signal
        
        Args:
            data: Historical price data
            entry_date: Date when signal was generated
            exit_days: Number of days to hold (2 months default)
        
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
            
            # Sector rotation specific metrics
            holding_data = data.iloc[entry_idx:exit_idx + 1]
            
            # Track momentum persistence
            momentum_periods = []
            for i in range(0, len(holding_data) - 10, 10):  # Every 10 days
                period_data = holding_data.iloc[i:i+10]
                if len(period_data) >= 2:
                    period_return = (period_data.iloc[-1]['close'] - period_data.iloc[0]['close']) / period_data.iloc[0]['close']
                    momentum_periods.append(period_return > 0)
            
            momentum_consistency = sum(momentum_periods) / len(momentum_periods) if momentum_periods else 0
            
            # Maximum favorable and adverse excursions
            max_favorable = ((holding_data['high'].max() - entry_price) / entry_price) * 100
            max_adverse = ((holding_data['low'].min() - entry_price) / entry_price) * 100
            
            return {
                'entry_price': entry_price,
                'exit_price': exit_price,
                'absolute_return': absolute_return,
                'percentage_return': percentage_return,
                'max_favorable_excursion': max_favorable,
                'max_adverse_excursion': max_adverse,
                'momentum_consistency': momentum_consistency,
                'holding_days': exit_idx - entry_idx,
                'success': percentage_return > 0,
                'strong_rotation': percentage_return > 10,  # 10%+ considered strong rotation
                'strategy_type': 'sector_rotation'
            }
            
        except Exception as e:
            logger.error(f"Error in sector rotation backtesting: {str(e)}")
            return {}
