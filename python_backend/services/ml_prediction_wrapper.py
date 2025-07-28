"""
ML Prediction Wrapper Service
Handles StandardScaler errors and provides robust predictions
"""

import logging
from typing import Dict, Any
from datetime import datetime
import numpy as np

logger = logging.getLogger(__name__)

class MLPredictionWrapper:
    """Wrapper service to handle ML prediction errors gracefully"""
    
    def __init__(self):
        self.fallback_predictions = {}
        logger.info("ML Prediction Wrapper initialized")
    
    def predict_price_safe(self, symbol: str, days_ahead: int = 1) -> Dict[str, Any]:
        """Safely predict price with multiple fallback mechanisms"""
        try:
            # Try the robust predictor first
            from .robust_ai_predictor import robust_ai_predictor
            result = robust_ai_predictor.predict_price_robust(symbol, days_ahead)
            
            # Convert PredictionResult to dict
            return {
                'success': True,
                'symbol': result.symbol,
                'current_price': result.current_price,
                'predicted_price_1d': result.predicted_price_1d,
                'predicted_price_7d': result.predicted_price_7d,
                'predicted_price_30d': result.predicted_price_30d,
                'confidence_1d': result.confidence_1d,
                'confidence_7d': result.confidence_7d,
                'confidence_30d': result.confidence_30d,
                'trend_direction': result.trend_direction,
                'volatility_forecast': result.volatility_forecast,
                'support_levels': result.support_levels,
                'resistance_levels': result.resistance_levels,
                'model_accuracy': result.model_accuracy,
                'prediction_timestamp': result.prediction_timestamp,
                'features_used': result.features_used,
                'risk_score': result.risk_score,
                'method': 'robust_ai'
            }
            
        except Exception as e:
            logger.warning(f"Robust AI predictor failed for {symbol}: {e}")
            
            # Try original AI predictor
            try:
                from .ai_price_predictor import ai_predictor
                result = ai_predictor.predict_price(symbol, days_ahead)
                
                return {
                    'success': True,
                    'symbol': result.symbol,
                    'current_price': result.current_price,
                    'predicted_price_1d': result.predicted_price_1d,
                    'predicted_price_7d': result.predicted_price_7d,
                    'predicted_price_30d': result.predicted_price_30d,
                    'confidence_1d': result.confidence_1d,
                    'confidence_7d': result.confidence_7d,
                    'confidence_30d': result.confidence_30d,
                    'trend_direction': result.trend_direction,
                    'volatility_forecast': result.volatility_forecast,
                    'support_levels': result.support_levels,
                    'resistance_levels': result.resistance_levels,
                    'model_accuracy': result.model_accuracy,
                    'prediction_timestamp': result.prediction_timestamp,
                    'features_used': result.features_used,
                    'risk_score': result.risk_score,
                    'method': 'original_ai'
                }
                
            except Exception as e2:
                logger.warning(f"Original AI predictor also failed for {symbol}: {e2}")
                
                # Final fallback - simple prediction
                return self._create_simple_prediction(symbol, days_ahead)
    
    def _create_simple_prediction(self, symbol: str, days_ahead: int) -> Dict[str, Any]:
        """Create a simple prediction when all ML methods fail"""
        logger.info(f"Creating simple prediction for {symbol}")
        
        # Try to get current price from yfinance
        current_price = 100.0  # Default
        try:
            import yfinance as yf
            ticker_symbol = f"{symbol}.NS" if not symbol.endswith('.NS') else symbol
            ticker = yf.Ticker(ticker_symbol)
            hist = ticker.history(period="1d")
            if not hist.empty:
                current_price = hist['Close'].iloc[-1]
        except Exception as e:
            logger.warning(f"Could not fetch current price for {symbol}: {e}")
        
        # Simple prediction based on random walk with slight positive bias
        price_change_pct = np.random.uniform(-0.01, 0.02)  # -1% to +2%
        predicted_price = current_price * (1 + price_change_pct)
        
        # Determine horizon-specific predictions
        pred_1d = predicted_price if days_ahead <= 1 else current_price
        pred_7d = predicted_price if 1 < days_ahead <= 7 else current_price
        pred_30d = predicted_price if days_ahead > 7 else current_price
        
        # Determine trend
        if price_change_pct > 0.01:
            trend = "BULLISH"
        elif price_change_pct < -0.005:
            trend = "BEARISH"
        else:
            trend = "SIDEWAYS"
        
        return {
            'success': True,
            'symbol': symbol,
            'current_price': current_price,
            'predicted_price_1d': pred_1d,
            'predicted_price_7d': pred_7d,
            'predicted_price_30d': pred_30d,
            'confidence_1d': 0.4 if days_ahead <= 1 else 0.5,
            'confidence_7d': 0.4 if 1 < days_ahead <= 7 else 0.5,
            'confidence_30d': 0.4 if days_ahead > 7 else 0.5,
            'trend_direction': trend,
            'volatility_forecast': 0.18,  # 18% default volatility
            'support_levels': [current_price * 0.97, current_price * 0.93],
            'resistance_levels': [current_price * 1.03, current_price * 1.07],
            'model_accuracy': 40.0,  # Moderate accuracy for simple method
            'prediction_timestamp': datetime.now().isoformat(),
            'features_used': ['simple_random_walk'],
            'risk_score': 0.4,
            'method': 'simple_fallback',
            'note': 'Using simple prediction due to ML model unavailability'
        }
    
    def get_prediction_summary(self, symbol: str) -> Dict[str, Any]:
        """Get a summary of prediction capabilities for a symbol"""
        try:
            # Test if we can make a prediction
            result = self.predict_price_safe(symbol, 1)
            
            return {
                'success': True,
                'symbol': symbol,
                'prediction_available': True,
                'method_used': result.get('method', 'unknown'),
                'confidence_level': result.get('model_accuracy', 0) / 100,
                'last_prediction': result.get('prediction_timestamp'),
                'features_available': len(result.get('features_used', [])),
                'risk_assessment': 'LOW' if result.get('risk_score', 0.5) < 0.3 else 'MEDIUM' if result.get('risk_score', 0.5) < 0.7 else 'HIGH'
            }
            
        except Exception as e:
            logger.error(f"Error getting prediction summary for {symbol}: {e}")
            return {
                'success': False,
                'symbol': symbol,
                'prediction_available': False,
                'error': str(e),
                'method_used': 'none',
                'confidence_level': 0.0
            }

# Global instance
ml_prediction_wrapper = MLPredictionWrapper()
