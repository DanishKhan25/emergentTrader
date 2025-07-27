"""
Market Regime Filter for EmergentTrader
Detects market conditions and filters strategies accordingly
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
from services.logging_service import get_logger, log_performance

class MarketRegime(Enum):
    BULL = "bull"
    BEAR = "bear"
    SIDEWAYS = "sideways"
    VOLATILE = "volatile"
    UNKNOWN = "unknown"

class MarketRegimeFilter:
    def __init__(self):
        self.logger = get_logger('signals')
        
        # Market regime thresholds
        self.bull_threshold = 0.05      # 5% upward trend
        self.bear_threshold = -0.05     # 5% downward trend
        self.volatility_threshold = 0.03 # 3% daily volatility threshold
        
        # Strategy-regime compatibility matrix
        self.strategy_regime_compatibility = {
            'multibagger': {
                MarketRegime.BULL: 1.0,      # Excellent in bull markets
                MarketRegime.SIDEWAYS: 0.7,  # Good in sideways
                MarketRegime.BEAR: 0.3,      # Poor in bear markets
                MarketRegime.VOLATILE: 0.5,  # Moderate in volatile
            },
            'momentum': {
                MarketRegime.BULL: 0.9,      # Great in bull markets
                MarketRegime.BEAR: 0.8,      # Good in bear (short momentum)
                MarketRegime.SIDEWAYS: 0.4,  # Poor in sideways
                MarketRegime.VOLATILE: 0.6,  # Moderate in volatile
            },
            'swing': {
                MarketRegime.BULL: 0.7,      # Good in bull
                MarketRegime.BEAR: 0.7,      # Good in bear
                MarketRegime.SIDEWAYS: 0.9,  # Excellent in sideways
                MarketRegime.VOLATILE: 0.8,  # Great in volatile
            },
            'breakout': {
                MarketRegime.BULL: 0.8,      # Great in bull
                MarketRegime.BEAR: 0.6,      # Moderate in bear
                MarketRegime.SIDEWAYS: 0.5,  # Poor in sideways
                MarketRegime.VOLATILE: 0.9,  # Excellent in volatile
            },
            'mean_reversion': {
                MarketRegime.BULL: 0.5,      # Moderate in bull
                MarketRegime.BEAR: 0.5,      # Moderate in bear
                MarketRegime.SIDEWAYS: 0.9,  # Excellent in sideways
                MarketRegime.VOLATILE: 0.8,  # Great in volatile
            },
            'value': {
                MarketRegime.BULL: 0.6,      # Moderate in bull
                MarketRegime.BEAR: 0.8,      # Great in bear (value opportunities)
                MarketRegime.SIDEWAYS: 0.7,  # Good in sideways
                MarketRegime.VOLATILE: 0.6,  # Moderate in volatile
            }
        }
        
        # Current market state cache
        self.current_regime = MarketRegime.UNKNOWN
        self.regime_confidence = 0.0
        self.last_update = None
        self.market_metrics = {}
        
    @log_performance('signals')
    def detect_market_regime(self, market_data: Optional[Dict] = None) -> Dict:
        """
        Detect current market regime based on various indicators
        
        Args:
            market_data: Optional market data, if None will fetch current data
        """
        try:
            self.logger.info("Detecting current market regime")
            
            # Get market data
            if market_data is None:
                market_data = self._fetch_market_data()
            
            if not market_data:
                return {
                    'success': False,
                    'error': 'Unable to fetch market data'
                }
            
            # Calculate regime indicators
            indicators = self._calculate_regime_indicators(market_data)
            
            # Determine regime
            regime, confidence = self._determine_regime(indicators)
            
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
                'description': self._get_regime_description(regime)
            }
            
            self.logger.info(f"Market regime detected: {regime.value} (confidence: {confidence:.1%})")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error detecting market regime: {str(e)}", exc_info=True)
            return {'success': False, 'error': str(e)}
    
    def _fetch_market_data(self) -> Optional[Dict]:
        """Fetch current market data for regime analysis"""
        try:
            # This is a simplified implementation
            # In production, you would fetch real market data from your data source
            
            # Simulate market data for demonstration
            # You should replace this with actual market data fetching
            
            import random
            from datetime import datetime, timedelta
            
            # Generate sample market data
            dates = [datetime.now() - timedelta(days=i) for i in range(30, 0, -1)]
            
            # Simulate different market conditions
            base_price = 15000  # Nifty base
            prices = []
            
            for i, date in enumerate(dates):
                # Add some trend and noise
                trend = (i - 15) * 10  # Trend component
                noise = random.gauss(0, 100)  # Random noise
                price = base_price + trend + noise
                prices.append(price)
            
            volumes = [random.randint(100000, 500000) for _ in dates]
            
            return {
                'dates': dates,
                'prices': prices,
                'volumes': volumes,
                'symbol': 'NIFTY50'
            }
            
        except Exception as e:
            self.logger.error(f"Error fetching market data: {str(e)}")
            return None
    
    def _calculate_regime_indicators(self, market_data: Dict) -> Dict:
        """Calculate various indicators for regime detection"""
        try:
            prices = np.array(market_data['prices'])
            volumes = np.array(market_data['volumes'])
            
            # Price-based indicators
            returns = np.diff(prices) / prices[:-1]
            
            # Trend indicators
            sma_short = np.mean(prices[-5:])   # 5-day SMA
            sma_long = np.mean(prices[-20:])   # 20-day SMA
            trend_strength = (sma_short - sma_long) / sma_long
            
            # Volatility indicators
            volatility = np.std(returns) * np.sqrt(252)  # Annualized volatility
            recent_volatility = np.std(returns[-10:]) * np.sqrt(252)
            
            # Momentum indicators
            momentum_5d = (prices[-1] - prices[-6]) / prices[-6] if len(prices) > 5 else 0
            momentum_20d = (prices[-1] - prices[-21]) / prices[-21] if len(prices) > 20 else 0
            
            # Volume indicators
            avg_volume = np.mean(volumes)
            recent_volume = np.mean(volumes[-5:])
            volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 1
            
            # Drawdown calculation
            peak = np.maximum.accumulate(prices)
            drawdown = (prices - peak) / peak
            max_drawdown = np.min(drawdown)
            current_drawdown = drawdown[-1]
            
            # Support/Resistance levels
            recent_high = np.max(prices[-10:])
            recent_low = np.min(prices[-10:])
            price_position = (prices[-1] - recent_low) / (recent_high - recent_low) if recent_high != recent_low else 0.5
            
            indicators = {
                'trend_strength': float(trend_strength),
                'volatility': float(volatility),
                'recent_volatility': float(recent_volatility),
                'momentum_5d': float(momentum_5d),
                'momentum_20d': float(momentum_20d),
                'volume_ratio': float(volume_ratio),
                'max_drawdown': float(max_drawdown),
                'current_drawdown': float(current_drawdown),
                'price_position': float(price_position),
                'current_price': float(prices[-1]),
                'sma_short': float(sma_short),
                'sma_long': float(sma_long)
            }
            
            return indicators
            
        except Exception as e:
            self.logger.error(f"Error calculating regime indicators: {str(e)}")
            return {}
    
    def _determine_regime(self, indicators: Dict) -> Tuple[MarketRegime, float]:
        """Determine market regime based on indicators"""
        try:
            trend_strength = indicators.get('trend_strength', 0)
            volatility = indicators.get('recent_volatility', 0)
            momentum_20d = indicators.get('momentum_20d', 0)
            current_drawdown = indicators.get('current_drawdown', 0)
            
            # Initialize regime scores
            regime_scores = {
                MarketRegime.BULL: 0,
                MarketRegime.BEAR: 0,
                MarketRegime.SIDEWAYS: 0,
                MarketRegime.VOLATILE: 0
            }
            
            # Bull market indicators
            if trend_strength > self.bull_threshold:
                regime_scores[MarketRegime.BULL] += 2
            if momentum_20d > 0.1:
                regime_scores[MarketRegime.BULL] += 2
            if current_drawdown > -0.05:  # Small drawdown
                regime_scores[MarketRegime.BULL] += 1
            
            # Bear market indicators
            if trend_strength < self.bear_threshold:
                regime_scores[MarketRegime.BEAR] += 2
            if momentum_20d < -0.1:
                regime_scores[MarketRegime.BEAR] += 2
            if current_drawdown < -0.15:  # Large drawdown
                regime_scores[MarketRegime.BEAR] += 1
            
            # Sideways market indicators
            if abs(trend_strength) < 0.02:  # Low trend strength
                regime_scores[MarketRegime.SIDEWAYS] += 2
            if abs(momentum_20d) < 0.05:  # Low momentum
                regime_scores[MarketRegime.SIDEWAYS] += 1
            if volatility < 0.15:  # Low volatility
                regime_scores[MarketRegime.SIDEWAYS] += 1
            
            # Volatile market indicators
            if volatility > self.volatility_threshold:
                regime_scores[MarketRegime.VOLATILE] += 2
            if abs(indicators.get('momentum_5d', 0)) > 0.03:  # High short-term momentum
                regime_scores[MarketRegime.VOLATILE] += 1
            if indicators.get('volume_ratio', 1) > 1.5:  # High volume
                regime_scores[MarketRegime.VOLATILE] += 1
            
            # Find regime with highest score
            best_regime = max(regime_scores, key=regime_scores.get)
            max_score = regime_scores[best_regime]
            
            # Calculate confidence (normalize scores)
            total_score = sum(regime_scores.values())
            confidence = max_score / total_score if total_score > 0 else 0
            
            # Minimum confidence threshold
            if confidence < 0.4:
                return MarketRegime.UNKNOWN, confidence
            
            return best_regime, confidence
            
        except Exception as e:
            self.logger.error(f"Error determining regime: {str(e)}")
            return MarketRegime.UNKNOWN, 0.0
    
    def _get_regime_description(self, regime: MarketRegime) -> str:
        """Get human-readable description of market regime"""
        descriptions = {
            MarketRegime.BULL: "Strong upward trend with positive momentum",
            MarketRegime.BEAR: "Downward trend with negative momentum",
            MarketRegime.SIDEWAYS: "Range-bound market with low volatility",
            MarketRegime.VOLATILE: "High volatility with frequent price swings",
            MarketRegime.UNKNOWN: "Market regime unclear or transitioning"
        }
        return descriptions.get(regime, "Unknown market condition")
    
    def filter_strategies_by_regime(self, strategies: List[str], 
                                   regime: Optional[MarketRegime] = None) -> Dict:
        """Filter and rank strategies based on current market regime"""
        try:
            # Use current regime if not specified
            if regime is None:
                if self.current_regime == MarketRegime.UNKNOWN or self.last_update is None:
                    # Update regime if unknown or stale
                    regime_result = self.detect_market_regime()
                    if not regime_result.get('success'):
                        return {'success': False, 'error': 'Could not determine market regime'}
                    regime = MarketRegime(regime_result['regime'])
                else:
                    regime = self.current_regime
            
            # Filter and score strategies
            strategy_scores = {}
            
            for strategy in strategies:
                if strategy in self.strategy_regime_compatibility:
                    compatibility = self.strategy_regime_compatibility[strategy]
                    score = compatibility.get(regime, 0.5)  # Default moderate compatibility
                    strategy_scores[strategy] = score
                else:
                    # Unknown strategy gets neutral score
                    strategy_scores[strategy] = 0.5
            
            # Sort strategies by score
            ranked_strategies = sorted(
                strategy_scores.items(), 
                key=lambda x: x[1], 
                reverse=True
            )
            
            # Categorize strategies
            excellent = [(s, score) for s, score in ranked_strategies if score >= 0.8]
            good = [(s, score) for s, score in ranked_strategies if 0.6 <= score < 0.8]
            moderate = [(s, score) for s, score in ranked_strategies if 0.4 <= score < 0.6]
            poor = [(s, score) for s, score in ranked_strategies if score < 0.4]
            
            result = {
                'success': True,
                'regime': regime.value,
                'regime_confidence': self.regime_confidence,
                'total_strategies': len(strategies),
                'strategy_scores': strategy_scores,
                'ranked_strategies': ranked_strategies,
                'categories': {
                    'excellent': [s for s, _ in excellent],
                    'good': [s for s, _ in good],
                    'moderate': [s for s, _ in moderate],
                    'poor': [s for s, _ in poor]
                },
                'recommendations': {
                    'use': [s for s, _ in excellent + good],
                    'caution': [s for s, _ in moderate],
                    'avoid': [s for s, _ in poor]
                }
            }
            
            self.logger.info(
                f"Filtered {len(strategies)} strategies for {regime.value} market: "
                f"{len(result['recommendations']['use'])} recommended, "
                f"{len(result['recommendations']['avoid'])} to avoid"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error filtering strategies by regime: {str(e)}", exc_info=True)
            return {'success': False, 'error': str(e)}
    
    def get_optimal_timing_score(self, signal_data: Dict) -> Dict:
        """Calculate timing score for a signal based on market regime"""
        try:
            strategy = signal_data.get('strategy', 'unknown')
            confidence = signal_data.get('confidence', 0.8)
            
            # Get current regime
            if self.current_regime == MarketRegime.UNKNOWN:
                regime_result = self.detect_market_regime()
                if not regime_result.get('success'):
                    return {'success': False, 'error': 'Could not determine market regime'}
            
            # Get strategy compatibility with current regime
            if strategy in self.strategy_regime_compatibility:
                regime_compatibility = self.strategy_regime_compatibility[strategy].get(
                    self.current_regime, 0.5
                )
            else:
                regime_compatibility = 0.5
            
            # Calculate timing score
            # Combines signal confidence with regime compatibility
            timing_score = (confidence * 0.6) + (regime_compatibility * 0.4)
            
            # Adjust for regime confidence
            timing_score *= (0.5 + self.regime_confidence * 0.5)
            
            # Categorize timing
            if timing_score >= 0.8:
                timing_category = "excellent"
            elif timing_score >= 0.6:
                timing_category = "good"
            elif timing_score >= 0.4:
                timing_category = "moderate"
            else:
                timing_category = "poor"
            
            return {
                'success': True,
                'timing_score': round(timing_score, 3),
                'timing_category': timing_category,
                'regime': self.current_regime.value,
                'regime_compatibility': round(regime_compatibility, 3),
                'signal_confidence': confidence,
                'recommendation': self._get_timing_recommendation(timing_category)
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating timing score: {str(e)}", exc_info=True)
            return {'success': False, 'error': str(e)}
    
    def _get_timing_recommendation(self, category: str) -> str:
        """Get timing recommendation based on category"""
        recommendations = {
            "excellent": "Strong timing - execute signal immediately",
            "good": "Good timing - execute with normal position size",
            "moderate": "Moderate timing - consider reduced position size",
            "poor": "Poor timing - consider waiting or avoiding"
        }
        return recommendations.get(category, "Unknown timing category")
    
    def get_regime_summary(self) -> Dict:
        """Get comprehensive market regime summary"""
        try:
            # Update regime if stale (older than 1 hour)
            if (self.last_update is None or 
                datetime.now() - self.last_update > timedelta(hours=1)):
                self.detect_market_regime()
            
            return {
                'success': True,
                'current_regime': self.current_regime.value,
                'confidence': round(self.regime_confidence, 3),
                'description': self._get_regime_description(self.current_regime),
                'last_update': self.last_update.isoformat() if self.last_update else None,
                'market_metrics': self.market_metrics,
                'strategy_recommendations': self._get_strategy_recommendations_for_regime()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting regime summary: {str(e)}", exc_info=True)
            return {'success': False, 'error': str(e)}
    
    def _get_strategy_recommendations_for_regime(self) -> Dict:
        """Get strategy recommendations for current regime"""
        if self.current_regime == MarketRegime.UNKNOWN:
            return {}
        
        all_strategies = list(self.strategy_regime_compatibility.keys())
        filter_result = self.filter_strategies_by_regime(all_strategies)
        
        if filter_result.get('success'):
            return filter_result.get('recommendations', {})
        else:
            return {}

# Global instance
_regime_filter = None

def get_regime_filter() -> MarketRegimeFilter:
    """Get global market regime filter instance"""
    global _regime_filter
    if _regime_filter is None:
        _regime_filter = MarketRegimeFilter()
    return _regime_filter
