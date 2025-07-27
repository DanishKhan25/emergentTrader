"""
Enhanced Market Regime Filter with Real-time Data Integration
Uses live market data for accurate regime detection
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
from services.logging_service import get_logger, log_performance
from services.realtime_market_data import get_market_data_service

class MarketRegime(Enum):
    BULL = "bull"
    BEAR = "bear"
    SIDEWAYS = "sideways"
    VOLATILE = "volatile"
    UNKNOWN = "unknown"

class RealTimeMarketRegimeFilter:
    def __init__(self):
        self.logger = get_logger('signals')
        self.market_data_service = get_market_data_service()
        
        # Enhanced regime thresholds based on Indian market characteristics
        self.bull_threshold = 0.03      # 3% upward trend (adjusted for Indian markets)
        self.bear_threshold = -0.03     # 3% downward trend
        self.volatility_threshold = 0.25 # 25% annualized volatility threshold
        self.sideways_threshold = 0.015  # 1.5% for sideways detection
        
        # RSI thresholds
        self.rsi_overbought = 70
        self.rsi_oversold = 30
        
        # Volume thresholds
        self.high_volume_threshold = 1.5  # 50% above average
        self.low_volume_threshold = 0.7   # 30% below average
        
        # Strategy-regime compatibility matrix (enhanced)
        self.strategy_regime_compatibility = {
            'multibagger': {
                MarketRegime.BULL: 1.0,      # Excellent in bull markets
                MarketRegime.SIDEWAYS: 0.8,  # Good in sideways (value hunting)
                MarketRegime.BEAR: 0.4,      # Poor in bear markets
                MarketRegime.VOLATILE: 0.6,  # Moderate in volatile
            },
            'momentum': {
                MarketRegime.BULL: 0.9,      # Great in bull markets
                MarketRegime.BEAR: 0.8,      # Good in bear (short momentum)
                MarketRegime.SIDEWAYS: 0.3,  # Poor in sideways
                MarketRegime.VOLATILE: 0.7,  # Good in volatile
            },
            'swing': {
                MarketRegime.BULL: 0.7,      # Good in bull
                MarketRegime.BEAR: 0.7,      # Good in bear
                MarketRegime.SIDEWAYS: 0.9,  # Excellent in sideways
                MarketRegime.VOLATILE: 0.8,  # Great in volatile
            },
            'breakout': {
                MarketRegime.BULL: 0.8,      # Great in bull
                MarketRegime.BEAR: 0.5,      # Moderate in bear
                MarketRegime.SIDEWAYS: 0.4,  # Poor in sideways
                MarketRegime.VOLATILE: 0.9,  # Excellent in volatile
            },
            'mean_reversion': {
                MarketRegime.BULL: 0.4,      # Poor in strong bull
                MarketRegime.BEAR: 0.4,      # Poor in strong bear
                MarketRegime.SIDEWAYS: 0.9,  # Excellent in sideways
                MarketRegime.VOLATILE: 0.8,  # Great in volatile
            },
            'value': {
                MarketRegime.BULL: 0.6,      # Moderate in bull
                MarketRegime.BEAR: 0.9,      # Excellent in bear (value opportunities)
                MarketRegime.SIDEWAYS: 0.8,  # Good in sideways
                MarketRegime.VOLATILE: 0.5,  # Moderate in volatile
            }
        }
        
        # Current market state cache
        self.current_regime = MarketRegime.UNKNOWN
        self.regime_confidence = 0.0
        self.last_update = None
        self.market_metrics = {}
        self.raw_market_data = {}
        
    @log_performance('signals')
    async def detect_market_regime(self, use_cache: bool = True) -> Dict:
        """
        Detect current market regime using real-time data
        
        Args:
            use_cache: Whether to use cached data if available
        """
        try:
            self.logger.info("Detecting market regime using real-time data")
            
            # Check if we should use cached data
            if (use_cache and self.last_update and 
                datetime.now() - self.last_update < timedelta(minutes=5)):
                self.logger.info("Using cached regime data")
                return {
                    'success': True,
                    'regime': self.current_regime.value,
                    'confidence': round(self.regime_confidence, 3),
                    'indicators': self.market_metrics,
                    'timestamp': self.last_update.isoformat(),
                    'description': self._get_regime_description(self.current_regime),
                    'data_source': 'cached'
                }
            
            # Fetch real-time market data
            market_data_result = await self.market_data_service.get_live_market_data(period_days=60)
            
            if not market_data_result.get('success'):
                self.logger.error(f"Failed to fetch market data: {market_data_result.get('error')}")
                return {
                    'success': False,
                    'error': 'Unable to fetch real-time market data'
                }
            
            market_data = market_data_result['data']
            self.raw_market_data = market_data
            
            # Calculate enhanced regime indicators
            indicators = await self._calculate_enhanced_regime_indicators(market_data)
            
            # Determine regime using multiple data sources
            regime, confidence = await self._determine_regime_with_multiple_sources(indicators, market_data)
            
            # Update cache
            self.current_regime = regime
            self.regime_confidence = confidence
            self.last_update = datetime.now()
            self.market_metrics = indicators
            
            result = {
                'success': True,
                'regime': regime.value,
                'confidence': round(confidence, 3),
                'indicators': indicators,
                'timestamp': self.last_update.isoformat(),
                'description': self._get_regime_description(regime),
                'market_status': market_data.get('market_status', {}),
                'data_source': 'real_time'
            }
            
            self.logger.info(f"Real-time market regime detected: {regime.value} (confidence: {confidence:.1%})")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error detecting market regime: {str(e)}", exc_info=True)
            return {'success': False, 'error': str(e)}
    
    async def _calculate_enhanced_regime_indicators(self, market_data: Dict) -> Dict:
        """Calculate enhanced indicators using real-time market data"""
        try:
            primary_data = market_data.get('primary_index')
            all_indices = market_data.get('all_indices', {})
            market_metrics = market_data.get('market_metrics', {})
            current_snapshot = market_data.get('current_snapshot', {})
            
            if not primary_data:
                raise ValueError("No primary index data available")
            
            prices = np.array(primary_data['prices'])
            volumes = np.array(primary_data.get('volumes', []))
            
            # Basic price indicators
            current_price = prices[-1]
            
            # Moving averages
            sma_5 = np.mean(prices[-5:]) if len(prices) >= 5 else current_price
            sma_20 = np.mean(prices[-20:]) if len(prices) >= 20 else current_price
            sma_50 = np.mean(prices[-50:]) if len(prices) >= 50 else current_price
            
            # Trend indicators
            trend_5_20 = (sma_5 - sma_20) / sma_20 if sma_20 != 0 else 0
            trend_20_50 = (sma_20 - sma_50) / sma_50 if sma_50 != 0 else 0
            
            # Price momentum
            momentum_5d = (prices[-1] - prices[-6]) / prices[-6] if len(prices) > 5 else 0
            momentum_20d = (prices[-1] - prices[-21]) / prices[-21] if len(prices) > 20 else 0
            
            # Volatility calculations
            returns = np.diff(prices) / prices[:-1]
            volatility_10d = np.std(returns[-10:]) * np.sqrt(252) if len(returns) >= 10 else 0
            volatility_20d = np.std(returns[-20:]) * np.sqrt(252) if len(returns) >= 20 else 0
            
            # RSI from market metrics
            nifty_metrics = market_metrics.get('NIFTY50', {})
            rsi = nifty_metrics.get('rsi', 50)
            
            # Volume analysis
            if len(volumes) > 0:
                avg_volume = np.mean(volumes)
                recent_volume = np.mean(volumes[-5:]) if len(volumes) >= 5 else avg_volume
                volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 1
            else:
                volume_ratio = 1
            
            # Drawdown analysis
            peak = np.maximum.accumulate(prices)
            drawdown = (prices - peak) / peak
            max_drawdown = np.min(drawdown)
            current_drawdown = drawdown[-1]
            
            # Support/Resistance levels
            recent_high = np.max(prices[-20:]) if len(prices) >= 20 else current_price
            recent_low = np.min(prices[-20:]) if len(prices) >= 20 else current_price
            price_position = (current_price - recent_low) / (recent_high - recent_low) if recent_high != recent_low else 0.5
            
            # Market breadth from multiple indices
            market_wide_metrics = market_metrics.get('MARKET_WIDE', {})
            market_breadth = market_wide_metrics.get('market_breadth', 0.5)
            avg_daily_change = market_wide_metrics.get('avg_daily_change_pct', 0)
            
            # Intraday volatility (if available)
            intraday_data = await self.market_data_service.get_intraday_data()
            intraday_volatility = 0
            if intraday_data.get('success'):
                intraday_prices = np.array(intraday_data['data']['prices'])
                if len(intraday_prices) > 1:
                    intraday_returns = np.diff(intraday_prices) / intraday_prices[:-1]
                    intraday_volatility = np.std(intraday_returns) * np.sqrt(78)  # Annualized (78 5-min intervals per day)
            
            indicators = {
                # Price indicators
                'current_price': float(current_price),
                'sma_5': float(sma_5),
                'sma_20': float(sma_20),
                'sma_50': float(sma_50),
                
                # Trend indicators
                'trend_5_20': float(trend_5_20),
                'trend_20_50': float(trend_20_50),
                'momentum_5d': float(momentum_5d),
                'momentum_20d': float(momentum_20d),
                
                # Volatility indicators
                'volatility_10d': float(volatility_10d),
                'volatility_20d': float(volatility_20d),
                'intraday_volatility': float(intraday_volatility),
                
                # Technical indicators
                'rsi': float(rsi),
                'volume_ratio': float(volume_ratio),
                
                # Market structure
                'max_drawdown': float(max_drawdown),
                'current_drawdown': float(current_drawdown),
                'price_position': float(price_position),
                'recent_high': float(recent_high),
                'recent_low': float(recent_low),
                
                # Market breadth
                'market_breadth': float(market_breadth),
                'avg_daily_change': float(avg_daily_change),
                
                # Additional metrics
                'indices_analyzed': len(all_indices),
                'data_quality_score': self._calculate_data_quality_score(market_data)
            }
            
            return indicators
            
        except Exception as e:
            self.logger.error(f"Error calculating enhanced regime indicators: {str(e)}")
            return {}
    
    async def _determine_regime_with_multiple_sources(self, indicators: Dict, market_data: Dict) -> Tuple[MarketRegime, float]:
        """Determine market regime using multiple data sources and enhanced logic"""
        try:
            # Initialize regime scores
            regime_scores = {
                MarketRegime.BULL: 0,
                MarketRegime.BEAR: 0,
                MarketRegime.SIDEWAYS: 0,
                MarketRegime.VOLATILE: 0
            }
            
            # Extract key indicators
            trend_5_20 = indicators.get('trend_5_20', 0)
            trend_20_50 = indicators.get('trend_20_50', 0)
            momentum_20d = indicators.get('momentum_20d', 0)
            volatility_20d = indicators.get('volatility_20d', 0)
            intraday_volatility = indicators.get('intraday_volatility', 0)
            rsi = indicators.get('rsi', 50)
            current_drawdown = indicators.get('current_drawdown', 0)
            market_breadth = indicators.get('market_breadth', 0.5)
            volume_ratio = indicators.get('volume_ratio', 1)
            
            # Bull market indicators (enhanced)
            bull_score = 0
            if trend_5_20 > self.bull_threshold:
                bull_score += 3
            if trend_20_50 > self.bull_threshold:
                bull_score += 2
            if momentum_20d > 0.05:  # 5% monthly momentum
                bull_score += 2
            if current_drawdown > -0.05:  # Small drawdown
                bull_score += 1
            if market_breadth > 0.6:  # Most indices positive
                bull_score += 2
            if rsi > 50 and rsi < self.rsi_overbought:  # Healthy bullish RSI
                bull_score += 1
            if volume_ratio > 1.2:  # Above average volume
                bull_score += 1
            
            regime_scores[MarketRegime.BULL] = bull_score
            
            # Bear market indicators (enhanced)
            bear_score = 0
            if trend_5_20 < self.bear_threshold:
                bear_score += 3
            if trend_20_50 < self.bear_threshold:
                bear_score += 2
            if momentum_20d < -0.05:  # -5% monthly momentum
                bear_score += 2
            if current_drawdown < -0.15:  # Significant drawdown
                bear_score += 2
            if market_breadth < 0.4:  # Most indices negative
                bear_score += 2
            if rsi < 50 and rsi > self.rsi_oversold:  # Healthy bearish RSI
                bear_score += 1
            if volume_ratio > 1.2:  # High volume in decline
                bear_score += 1
            
            regime_scores[MarketRegime.BEAR] = bear_score
            
            # Sideways market indicators (enhanced)
            sideways_score = 0
            if abs(trend_5_20) < self.sideways_threshold:
                sideways_score += 3
            if abs(trend_20_50) < self.sideways_threshold:
                sideways_score += 2
            if abs(momentum_20d) < 0.03:  # Low momentum
                sideways_score += 2
            if volatility_20d < 0.20:  # Low volatility
                sideways_score += 2
            if 0.4 <= market_breadth <= 0.6:  # Mixed market
                sideways_score += 1
            if 40 <= rsi <= 60:  # Neutral RSI
                sideways_score += 1
            
            regime_scores[MarketRegime.SIDEWAYS] = sideways_score
            
            # Volatile market indicators (enhanced)
            volatile_score = 0
            if volatility_20d > self.volatility_threshold:
                volatile_score += 3
            if intraday_volatility > 0.30:  # High intraday volatility
                volatile_score += 2
            if abs(momentum_20d) > 0.08:  # High momentum (either direction)
                volatile_score += 1
            if volume_ratio > self.high_volume_threshold:  # High volume
                volatile_score += 2
            if rsi < self.rsi_oversold or rsi > self.rsi_overbought:  # Extreme RSI
                volatile_score += 1
            if abs(current_drawdown) > 0.10:  # Significant price swings
                volatile_score += 1
            
            regime_scores[MarketRegime.VOLATILE] = volatile_score
            
            # Find regime with highest score
            best_regime = max(regime_scores, key=regime_scores.get)
            max_score = regime_scores[best_regime]
            
            # Calculate confidence with enhanced logic
            total_score = sum(regime_scores.values())
            base_confidence = max_score / total_score if total_score > 0 else 0
            
            # Adjust confidence based on data quality and market conditions
            data_quality = indicators.get('data_quality_score', 0.8)
            market_status = market_data.get('market_status', {})
            is_market_open = market_status.get('is_open', False)
            
            # Boost confidence if market is open (real-time data)
            if is_market_open:
                base_confidence *= 1.1
            
            # Adjust for data quality
            confidence = base_confidence * data_quality
            
            # Apply minimum confidence threshold
            if confidence < 0.4:
                return MarketRegime.UNKNOWN, confidence
            
            # Cap confidence at 0.95
            confidence = min(confidence, 0.95)
            
            self.logger.info(f"Regime scores: {regime_scores}, Winner: {best_regime.value}")
            
            return best_regime, confidence
            
        except Exception as e:
            self.logger.error(f"Error determining regime: {str(e)}")
            return MarketRegime.UNKNOWN, 0.0
    
    def _calculate_data_quality_score(self, market_data: Dict) -> float:
        """Calculate data quality score based on available data"""
        try:
            score = 0.0
            max_score = 0.0
            
            # Primary index data quality
            primary_data = market_data.get('primary_index')
            if primary_data:
                if len(primary_data.get('prices', [])) >= 30:  # At least 30 days
                    score += 0.3
                if primary_data.get('current_price'):
                    score += 0.1
                max_score += 0.4
            
            # Multiple indices availability
            all_indices = market_data.get('all_indices', {})
            indices_count = len(all_indices)
            if indices_count >= 3:
                score += 0.2
            elif indices_count >= 2:
                score += 0.1
            max_score += 0.2
            
            # Market metrics availability
            market_metrics = market_data.get('market_metrics', {})
            if market_metrics:
                score += 0.2
            max_score += 0.2
            
            # Current snapshot availability
            current_snapshot = market_data.get('current_snapshot', {})
            if current_snapshot:
                score += 0.1
            max_score += 0.1
            
            # Market status availability
            market_status = market_data.get('market_status', {})
            if market_status:
                score += 0.1
            max_score += 0.1
            
            return score / max_score if max_score > 0 else 0.5
            
        except Exception:
            return 0.5
    
    def _get_regime_description(self, regime: MarketRegime) -> str:
        """Get enhanced human-readable description of market regime"""
        descriptions = {
            MarketRegime.BULL: "Strong upward trend with positive momentum and broad market participation",
            MarketRegime.BEAR: "Downward trend with negative momentum and widespread selling pressure",
            MarketRegime.SIDEWAYS: "Range-bound market with low volatility and mixed signals",
            MarketRegime.VOLATILE: "High volatility environment with frequent price swings and uncertainty",
            MarketRegime.UNKNOWN: "Market regime unclear due to mixed signals or insufficient data"
        }
        return descriptions.get(regime, "Unknown market condition")
    
    async def get_regime_with_intraday_update(self) -> Dict:
        """Get regime with intraday updates for more responsive detection"""
        try:
            # Get base regime
            base_result = await self.detect_market_regime(use_cache=False)
            
            if not base_result.get('success'):
                return base_result
            
            # Get intraday data for fine-tuning
            intraday_result = await self.market_data_service.get_intraday_data()
            
            if intraday_result.get('success'):
                intraday_data = intraday_result['data']
                
                # Calculate intraday adjustments
                adjustments = self._calculate_intraday_adjustments(intraday_data)
                
                # Apply adjustments to confidence
                adjusted_confidence = base_result['confidence'] * adjustments.get('confidence_multiplier', 1.0)
                adjusted_confidence = max(0.1, min(0.95, adjusted_confidence))
                
                base_result['confidence'] = round(adjusted_confidence, 3)
                base_result['intraday_adjustments'] = adjustments
                base_result['data_source'] = 'real_time_with_intraday'
            
            return base_result
            
        except Exception as e:
            self.logger.error(f"Error getting regime with intraday update: {e}")
            return await self.detect_market_regime()
    
    def _calculate_intraday_adjustments(self, intraday_data: Dict) -> Dict:
        """Calculate adjustments based on intraday price action"""
        try:
            prices = np.array(intraday_data.get('prices', []))
            volumes = np.array(intraday_data.get('volumes', []))
            
            if len(prices) < 10:  # Need sufficient data
                return {'confidence_multiplier': 1.0}
            
            # Intraday momentum
            intraday_change = (prices[-1] - prices[0]) / prices[0]
            
            # Intraday volatility
            returns = np.diff(prices) / prices[:-1]
            intraday_vol = np.std(returns)
            
            # Volume pattern
            avg_volume = np.mean(volumes) if len(volumes) > 0 else 0
            recent_volume = np.mean(volumes[-5:]) if len(volumes) >= 5 else avg_volume
            volume_surge = recent_volume / avg_volume if avg_volume > 0 else 1
            
            # Calculate confidence multiplier
            confidence_multiplier = 1.0
            
            # Strong intraday momentum increases confidence
            if abs(intraday_change) > 0.02:  # 2% intraday move
                confidence_multiplier *= 1.1
            
            # High volume confirms the move
            if volume_surge > 1.5:
                confidence_multiplier *= 1.05
            
            # Very high volatility reduces confidence
            if intraday_vol > 0.03:  # 3% intraday volatility
                confidence_multiplier *= 0.95
            
            return {
                'confidence_multiplier': confidence_multiplier,
                'intraday_change': float(intraday_change),
                'intraday_volatility': float(intraday_vol),
                'volume_surge': float(volume_surge)
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating intraday adjustments: {e}")
            return {'confidence_multiplier': 1.0}

# Global instance
_realtime_regime_filter = None

def get_realtime_regime_filter() -> RealTimeMarketRegimeFilter:
    """Get global real-time market regime filter instance"""
    global _realtime_regime_filter
    if _realtime_regime_filter is None:
        _realtime_regime_filter = RealTimeMarketRegimeFilter()
    return _realtime_regime_filter
