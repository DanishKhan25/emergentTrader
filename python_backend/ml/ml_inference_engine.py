#!/usr/bin/env python3
"""
ML Inference Engine
Real-time ML predictions for signal quality enhancement
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf
import joblib
import json
from typing import Dict, List, Optional, Tuple
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

class MLInferenceEngine:
    """Real-time ML inference for trading signal enhancement"""
    
    def __init__(self, model_path: str = None):
        self.models = {}
        self.scalers = {}
        self.feature_columns = []
        self.model_performance = {}
        self.feature_cache = {}
        
        # Load trained models
        if model_path:
            self.load_models(model_path)
        else:
            self._load_latest_model()
        
        logger.info("ML Inference Engine initialized")
    
    def _load_latest_model(self):
        """Load the latest trained model"""
        try:
            model_files = [f for f in os.listdir('ml/models/') if f.endswith('.pkl')]
            if model_files:
                latest_model = sorted(model_files)[-1]
                model_path = f'ml/models/{latest_model}'
                self.load_models(model_path)
                logger.info(f"Loaded latest model: {latest_model}")
            else:
                logger.warning("No trained models found. Using demo model.")
                self._create_demo_model()
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            self._create_demo_model()
    
    def load_models(self, model_path: str):
        """Load trained models from file"""
        try:
            model_data = joblib.load(model_path)
            
            if isinstance(model_data, dict):
                self.models = model_data.get('models', {})
                self.scalers = model_data.get('scalers', {})
                self.model_performance = model_data.get('model_performance', {})
                
                # Get feature columns from ensemble model if available
                if 'ensemble' in self.models:
                    ensemble_data = self.models['ensemble']
                    if isinstance(ensemble_data, dict) and 'feature_columns' in ensemble_data:
                        self.feature_columns = ensemble_data['feature_columns']
            
            logger.info(f"Models loaded successfully from {model_path}")
            
        except Exception as e:
            logger.error(f"Error loading models from {model_path}: {str(e)}")
            self._create_demo_model()
    
    def _create_demo_model(self):
        """Create a simple demo model for testing"""
        from sklearn.ensemble import RandomForestClassifier
        
        # Create a simple model with basic features
        model = RandomForestClassifier(n_estimators=50, random_state=42)
        
        # Train on synthetic data
        np.random.seed(42)
        X_demo = np.random.random((1000, 10))
        y_demo = (X_demo[:, 0] + X_demo[:, 1] > 1.0).astype(int)
        
        model.fit(X_demo, y_demo)
        
        self.models = {'demo_model': model}
        self.feature_columns = [f'feature_{i}' for i in range(10)]
        
        logger.info("Demo model created for testing")
    
    def extract_signal_features(self, signal: Dict, market_context: Dict = None) -> Dict:
        """Extract ML features from a trading signal"""
        try:
            # Basic signal features
            features = {
                'confidence': signal.get('confidence', 0.5),
                'strategy_encoded': self._encode_strategy(signal.get('strategy', 'momentum')),
                'entry_price': signal.get('entry_price', signal.get('current_price', 1000)),
            }
            
            # Market context features
            if market_context:
                features.update({
                    'market_volatility': market_context.get('volatility', 0.20),
                    'market_momentum': market_context.get('trend_20d', 0.0),
                    'bull_market': 1 if market_context.get('regime') == 'BULL' else 0,
                    'bear_market': 1 if market_context.get('regime') == 'BEAR' else 0,
                    'sideways_market': 1 if market_context.get('regime') == 'SIDEWAYS' else 0,
                })
            else:
                # Default market features
                features.update({
                    'market_volatility': 0.20,
                    'market_momentum': 0.0,
                    'bull_market': 0,
                    'bear_market': 0,
                    'sideways_market': 1,
                })
            
            # Technical features from signal metadata
            features.update(self._extract_technical_features(signal))
            
            # Time-based features
            features.update(self._extract_time_features())
            
            # Interaction features
            features.update(self._create_interaction_features(features))
            
            return features
            
        except Exception as e:
            logger.error(f"Error extracting features: {str(e)}")
            return self._default_features()
    
    def _encode_strategy(self, strategy: str) -> int:
        """Encode strategy name to integer"""
        strategy_mapping = {
            'momentum': 0,
            'low_volatility': 1,
            'fundamental_growth': 2,
            'mean_reversion': 3,
            'breakout': 4,
            'value_investing': 5,
            'swing_trading': 6,
            'multibagger': 7,
            'sector_rotation': 8,
            'pivot_cpr': 9
        }
        return strategy_mapping.get(strategy, 0)
    
    def _extract_technical_features(self, signal: Dict) -> Dict:
        """Extract technical features from signal"""
        try:
            # Try to get from signal metadata
            metadata = signal.get('metadata', {})
            if isinstance(metadata, str):
                import json
                metadata = json.loads(metadata)
            
            return {
                'rsi': metadata.get('rsi', signal.get('rsi', 50)),
                'macd': metadata.get('macd', signal.get('macd', 0)),
                'volume_ratio': metadata.get('volume_ratio', signal.get('volume_ratio', 1.0)),
                'price_momentum_20d': metadata.get('momentum_20d', signal.get('momentum_20d', 0)),
                'volatility': metadata.get('volatility', signal.get('volatility', 0.20)),
            }
        except:
            return {
                'rsi': 50,
                'macd': 0,
                'volume_ratio': 1.0,
                'price_momentum_20d': 0,
                'volatility': 0.20,
            }
    
    def _extract_time_features(self) -> Dict:
        """Extract time-based features"""
        now = datetime.now()
        return {
            'month': now.month,
            'quarter': (now.month - 1) // 3 + 1,
            'is_earnings_season': 1 if now.month in [1, 4, 7, 10] else 0,
            'is_quarter_end': 1 if now.month in [3, 6, 9, 12] else 0,
        }
    
    def _create_interaction_features(self, features: Dict) -> Dict:
        """Create interaction features"""
        try:
            return {
                'confidence_x_momentum': features['confidence'] * features.get('price_momentum_20d', 0),
                'volatility_x_momentum': features.get('volatility', 0.2) * features.get('price_momentum_20d', 0),
                'rsi_x_confidence': features.get('rsi', 50) * features['confidence'] / 100,
                'high_confidence': 1 if features['confidence'] > 0.7 else 0,
                'positive_momentum': 1 if features.get('price_momentum_20d', 0) > 0 else 0,
                'low_volatility_market': 1 if features.get('market_volatility', 0.2) < 0.2 else 0,
                'high_volume': 1 if features.get('volume_ratio', 1.0) > 1.5 else 0,
                'rsi_oversold': 1 if features.get('rsi', 50) < 30 else 0,
                'rsi_overbought': 1 if features.get('rsi', 50) > 70 else 0,
            }
        except:
            return {
                'confidence_x_momentum': 0,
                'volatility_x_momentum': 0,
                'rsi_x_confidence': 25,
                'high_confidence': 0,
                'positive_momentum': 0,
                'low_volatility_market': 1,
                'high_volume': 0,
                'rsi_oversold': 0,
                'rsi_overbought': 0,
            }
    
    def _default_features(self) -> Dict:
        """Default features when extraction fails"""
        return {
            'confidence': 0.5,
            'strategy_encoded': 0,
            'entry_price': 1000,
            'market_volatility': 0.20,
            'market_momentum': 0.0,
            'bull_market': 0,
            'bear_market': 0,
            'sideways_market': 1,
            'rsi': 50,
            'macd': 0,
            'volume_ratio': 1.0,
            'price_momentum_20d': 0,
            'volatility': 0.20,
            'month': datetime.now().month,
            'quarter': (datetime.now().month - 1) // 3 + 1,
            'is_earnings_season': 0,
            'is_quarter_end': 0,
            'confidence_x_momentum': 0,
            'volatility_x_momentum': 0,
            'rsi_x_confidence': 25,
            'high_confidence': 0,
            'positive_momentum': 0,
            'low_volatility_market': 1,
            'high_volume': 0,
            'rsi_oversold': 0,
            'rsi_overbought': 0,
        }
    
    def predict_signal_quality(self, signal: Dict, market_context: Dict = None) -> Dict:
        """Predict signal quality using ML models"""
        try:
            # Extract features
            features = self.extract_signal_features(signal, market_context)
            
            # Prepare feature vector
            if self.feature_columns:
                feature_vector = [features.get(col, 0) for col in self.feature_columns]
            else:
                # Use demo model features
                feature_vector = [
                    features.get('confidence', 0.5),
                    features.get('rsi', 50) / 100,
                    features.get('volatility', 0.2),
                    features.get('market_volatility', 0.2),
                    features.get('volume_ratio', 1.0),
                    features.get('price_momentum_20d', 0),
                    features.get('bull_market', 0),
                    features.get('high_confidence', 0),
                    features.get('positive_momentum', 0),
                    features.get('confidence_x_momentum', 0)
                ]
            
            # Get predictions from available models
            predictions = {}
            
            for model_name, model in self.models.items():
                try:
                    if model_name == 'ensemble':
                        # Handle ensemble model
                        pred = self._predict_ensemble(feature_vector, model)
                    else:
                        # Handle individual models
                        if model_name in self.scalers:
                            # Scale features if needed
                            scaled_features = self.scalers[model_name].transform([feature_vector])
                            pred = model.predict_proba(scaled_features)[0][1]
                        else:
                            pred = model.predict_proba([feature_vector])[0][1]
                    
                    predictions[model_name] = pred
                    
                except Exception as e:
                    logger.error(f"Error with model {model_name}: {str(e)}")
                    continue
            
            # Use best available prediction
            if predictions:
                # Use ensemble if available, otherwise best individual model
                if 'ensemble' in predictions:
                    ml_probability = predictions['ensemble']
                    best_model = 'ensemble'
                else:
                    best_model = max(predictions.keys(), key=lambda k: self.model_performance.get(k, {}).get('test_auc', 0))
                    ml_probability = predictions[best_model]
            else:
                # Fallback prediction
                ml_probability = features['confidence']
                best_model = 'fallback'
            
            # Generate recommendation
            if ml_probability > 0.75:
                recommendation = 'STRONG_BUY'
                quality_score = 'HIGH'
            elif ml_probability > 0.60:
                recommendation = 'BUY'
                quality_score = 'MEDIUM'
            elif ml_probability > 0.45:
                recommendation = 'WEAK_BUY'
                quality_score = 'LOW'
            else:
                recommendation = 'SKIP'
                quality_score = 'POOR'
            
            # Calculate confidence adjustment
            original_confidence = signal.get('confidence', 0.5)
            confidence_adjustment = ml_probability - original_confidence
            
            return {
                'ml_probability': ml_probability,
                'original_confidence': original_confidence,
                'confidence_adjustment': confidence_adjustment,
                'recommendation': recommendation,
                'quality_score': quality_score,
                'model_used': best_model,
                'all_predictions': predictions,
                'features_used': len(feature_vector),
                'prediction_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in ML prediction: {str(e)}")
            return self._fallback_prediction(signal)
    
    def _predict_ensemble(self, feature_vector: List, ensemble_data: Dict) -> float:
        """Make prediction using ensemble model"""
        try:
            component_models = ensemble_data.get('component_models', {})
            weights = ensemble_data.get('weights', [])
            scalers = ensemble_data.get('scalers', {})
            
            predictions = []
            
            for i, (model_name, model) in enumerate(component_models.items()):
                if model_name == 'ensemble':
                    continue
                
                try:
                    if model_name in scalers:
                        scaled_features = scalers[model_name].transform([feature_vector])
                        pred = model.predict_proba(scaled_features)[0][1]
                    else:
                        pred = model.predict_proba([feature_vector])[0][1]
                    
                    predictions.append(pred)
                except:
                    continue
            
            if predictions and len(weights) == len(predictions):
                return np.average(predictions, weights=weights)
            elif predictions:
                return np.mean(predictions)
            else:
                return 0.5
                
        except Exception as e:
            logger.error(f"Error in ensemble prediction: {str(e)}")
            return 0.5
    
    def _fallback_prediction(self, signal: Dict) -> Dict:
        """Fallback prediction when ML fails"""
        original_confidence = signal.get('confidence', 0.5)
        
        return {
            'ml_probability': original_confidence,
            'original_confidence': original_confidence,
            'confidence_adjustment': 0.0,
            'recommendation': 'BUY' if original_confidence > 0.6 else 'WEAK_BUY',
            'quality_score': 'MEDIUM' if original_confidence > 0.6 else 'LOW',
            'model_used': 'fallback',
            'all_predictions': {},
            'features_used': 0,
            'prediction_timestamp': datetime.now().isoformat(),
            'error': 'ML prediction failed, using original confidence'
        }
    
    def enhance_signals_batch(self, signals: List[Dict], market_context: Dict = None) -> List[Dict]:
        """Enhance a batch of signals with ML predictions"""
        enhanced_signals = []
        
        for signal in signals:
            try:
                # Get ML prediction
                ml_result = self.predict_signal_quality(signal, market_context)
                
                # Enhance signal with ML data
                enhanced_signal = signal.copy()
                enhanced_signal.update({
                    'ml_enhanced': True,
                    'ml_probability': ml_result['ml_probability'],
                    'ml_recommendation': ml_result['recommendation'],
                    'ml_quality_score': ml_result['quality_score'],
                    'confidence_adjustment': ml_result['confidence_adjustment'],
                    'model_used': ml_result['model_used'],
                    'ml_timestamp': ml_result['prediction_timestamp']
                })
                
                enhanced_signals.append(enhanced_signal)
                
            except Exception as e:
                logger.error(f"Error enhancing signal for {signal.get('symbol', 'Unknown')}: {str(e)}")
                # Add original signal without enhancement
                signal['ml_enhanced'] = False
                signal['ml_error'] = str(e)
                enhanced_signals.append(signal)
        
        logger.info(f"Enhanced {len(enhanced_signals)} signals with ML predictions")
        return enhanced_signals
    
    def filter_signals_by_quality(self, signals: List[Dict], min_ml_probability: float = 0.6) -> Tuple[List[Dict], List[Dict]]:
        """Filter signals based on ML quality predictions"""
        high_quality = []
        low_quality = []
        
        for signal in signals:
            ml_probability = signal.get('ml_probability', signal.get('confidence', 0.5))
            
            if ml_probability >= min_ml_probability:
                high_quality.append(signal)
            else:
                low_quality.append(signal)
        
        logger.info(f"Filtered signals: {len(high_quality)} high quality, {len(low_quality)} low quality")
        
        return high_quality, low_quality
    
    def get_model_info(self) -> Dict:
        """Get information about loaded models"""
        return {
            'models_loaded': list(self.models.keys()),
            'model_performance': self.model_performance,
            'feature_count': len(self.feature_columns),
            'scalers_available': list(self.scalers.keys()),
            'inference_ready': len(self.models) > 0
        }

def main():
    """Test ML inference engine"""
    print("🤖 Testing ML Inference Engine")
    print("=" * 50)
    
    # Initialize inference engine
    engine = MLInferenceEngine()
    
    # Show model info
    model_info = engine.get_model_info()
    print(f"📊 Model Info:")
    print(f"   Models loaded: {model_info['models_loaded']}")
    print(f"   Features: {model_info['feature_count']}")
    print(f"   Inference ready: {model_info['inference_ready']}")
    
    # Test with sample signals
    test_signals = [
        {
            'symbol': 'TCS',
            'strategy': 'low_volatility',
            'confidence': 0.7,
            'current_price': 3500,
            'rsi': 45,
            'volume_ratio': 1.2,
            'volatility': 0.18
        },
        {
            'symbol': 'RELIANCE',
            'strategy': 'momentum',
            'confidence': 0.6,
            'current_price': 2800,
            'rsi': 65,
            'volume_ratio': 1.8,
            'momentum_20d': 0.08
        }
    ]
    
    # Market context
    market_context = {
        'regime': 'BULL',
        'volatility': 0.20,
        'trend_20d': 0.05
    }
    
    print(f"\n🎯 Testing Signal Enhancement:")
    
    # Enhance signals
    enhanced_signals = engine.enhance_signals_batch(test_signals, market_context)
    
    for signal in enhanced_signals:
        print(f"\n{signal['symbol']} ({signal['strategy']}):")
        print(f"  Original Confidence: {signal['confidence']:.1%}")
        if signal.get('ml_enhanced'):
            print(f"  ML Probability: {signal['ml_probability']:.1%}")
            print(f"  ML Recommendation: {signal['ml_recommendation']}")
            print(f"  Quality Score: {signal['ml_quality_score']}")
            print(f"  Adjustment: {signal['confidence_adjustment']:+.1%}")
        else:
            print(f"  ML Enhancement: Failed")
    
    # Test filtering
    high_quality, low_quality = engine.filter_signals_by_quality(enhanced_signals, min_ml_probability=0.6)
    
    print(f"\n📈 Signal Filtering (min 60% probability):")
    print(f"   High quality: {len(high_quality)} signals")
    print(f"   Low quality: {len(low_quality)} signals")
    
    print(f"\n✅ ML Inference Engine test complete!")

if __name__ == "__main__":
    main()
