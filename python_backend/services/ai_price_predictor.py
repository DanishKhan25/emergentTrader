"""
AI/ML Price Prediction Service
Advanced machine learning models for stock price forecasting
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import logging
import joblib
import os
from dataclasses import dataclass
import yfinance as yf
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split, cross_val_score
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

@dataclass
class PredictionResult:
    """Structure for price prediction results"""
    symbol: str
    current_price: float
    predicted_price_1d: float
    predicted_price_7d: float
    predicted_price_30d: float
    confidence_1d: float
    confidence_7d: float
    confidence_30d: float
    trend_direction: str  # 'BULLISH', 'BEARISH', 'SIDEWAYS'
    volatility_forecast: float
    support_levels: List[float]
    resistance_levels: List[float]
    model_accuracy: float
    prediction_timestamp: str
    features_used: List[str]
    risk_score: float  # 0-1, higher = riskier

@dataclass
class ModelMetrics:
    """Model performance metrics"""
    mae: float  # Mean Absolute Error
    mse: float  # Mean Squared Error
    rmse: float  # Root Mean Squared Error
    r2: float   # R-squared
    accuracy_percentage: float
    cross_val_score: float

class AIFeatureEngineer:
    """Advanced feature engineering for price prediction"""
    
    @staticmethod
    def create_technical_features(df: pd.DataFrame) -> pd.DataFrame:
        """Create comprehensive technical analysis features"""
        
        # Price-based features
        df['returns'] = df['Close'].pct_change()
        df['log_returns'] = np.log(df['Close'] / df['Close'].shift(1))
        df['price_change'] = df['Close'] - df['Open']
        df['price_range'] = df['High'] - df['Low']
        df['body_size'] = abs(df['Close'] - df['Open'])
        
        # Moving averages
        for period in [5, 10, 20, 50, 200]:
            df[f'sma_{period}'] = df['Close'].rolling(window=period).mean()
            df[f'ema_{period}'] = df['Close'].ewm(span=period).mean()
            df[f'price_to_sma_{period}'] = df['Close'] / df[f'sma_{period}']
        
        # Volatility features
        df['volatility_5'] = df['returns'].rolling(window=5).std()
        df['volatility_20'] = df['returns'].rolling(window=20).std()
        df['atr'] = AIFeatureEngineer._calculate_atr(df)
        
        # Momentum indicators
        df['rsi'] = AIFeatureEngineer._calculate_rsi(df['Close'])
        df['macd'], df['macd_signal'] = AIFeatureEngineer._calculate_macd(df['Close'])
        df['stoch_k'], df['stoch_d'] = AIFeatureEngineer._calculate_stochastic(df)
        
        # Volume features
        df['volume_sma_20'] = df['Volume'].rolling(window=20).mean()
        df['volume_ratio'] = df['Volume'] / df['volume_sma_20']
        df['price_volume'] = df['Close'] * df['Volume']
        
        # Support/Resistance levels
        df['support'], df['resistance'] = AIFeatureEngineer._calculate_support_resistance(df)
        
        # Trend features
        df['trend_strength'] = AIFeatureEngineer._calculate_trend_strength(df)
        df['trend_direction'] = AIFeatureEngineer._calculate_trend_direction(df)
        
        return df
    
    @staticmethod
    def _calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Average True Range"""
        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - df['Close'].shift())
        low_close = np.abs(df['Low'] - df['Close'].shift())
        true_range = np.maximum(high_low, np.maximum(high_close, low_close))
        return true_range.rolling(window=period).mean()
    
    @staticmethod
    def _calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    @staticmethod
    def _calculate_macd(prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series]:
        """Calculate MACD and Signal line"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd = ema_fast - ema_slow
        macd_signal = macd.ewm(span=signal).mean()
        return macd, macd_signal
    
    @staticmethod
    def _calculate_stochastic(df: pd.DataFrame, k_period: int = 14, d_period: int = 3) -> Tuple[pd.Series, pd.Series]:
        """Calculate Stochastic Oscillator"""
        lowest_low = df['Low'].rolling(window=k_period).min()
        highest_high = df['High'].rolling(window=k_period).max()
        k_percent = 100 * ((df['Close'] - lowest_low) / (highest_high - lowest_low))
        d_percent = k_percent.rolling(window=d_period).mean()
        return k_percent, d_percent
    
    @staticmethod
    def _calculate_support_resistance(df: pd.DataFrame, window: int = 20) -> Tuple[pd.Series, pd.Series]:
        """Calculate dynamic support and resistance levels"""
        support = df['Low'].rolling(window=window).min()
        resistance = df['High'].rolling(window=window).max()
        return support, resistance
    
    @staticmethod
    def _calculate_trend_strength(df: pd.DataFrame, period: int = 20) -> pd.Series:
        """Calculate trend strength indicator"""
        price_change = df['Close'] - df['Close'].shift(period)
        volatility = df['Close'].rolling(window=period).std()
        return price_change / volatility
    
    @staticmethod
    def _calculate_trend_direction(df: pd.DataFrame, short: int = 10, long: int = 30) -> pd.Series:
        """Calculate trend direction"""
        short_ma = df['Close'].rolling(window=short).mean()
        long_ma = df['Close'].rolling(window=long).mean()
        return np.where(short_ma > long_ma, 1, -1)

class AIPricePredictor:
    """Advanced AI/ML Price Prediction System"""
    
    def __init__(self, model_dir: str = "models/price_prediction"):
        """Initialize the AI Price Predictor"""
        self.model_dir = model_dir
        os.makedirs(model_dir, exist_ok=True)
        
        # Initialize models
        self.models = {
            'random_forest': RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            ),
            'gradient_boost': GradientBoostingRegressor(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=42
            ),
            'linear': LinearRegression()
        }
        
        # Scalers for different prediction horizons
        self.scalers = {
            '1d': StandardScaler(),
            '7d': StandardScaler(),
            '30d': StandardScaler()
        }
        
        # Feature engineer
        self.feature_engineer = AIFeatureEngineer()
        
        # Model performance tracking
        self.model_metrics = {}
        
        logger.info("AI Price Predictor initialized")
    
    def fetch_stock_data(self, symbol: str, period: str = "2y") -> pd.DataFrame:
        """Fetch comprehensive stock data for training"""
        try:
            # Add .NS suffix for Indian stocks if not present
            if not symbol.endswith('.NS'):
                symbol = f"{symbol}.NS"
            
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period)
            
            if df.empty:
                raise ValueError(f"No data found for symbol {symbol}")
            
            logger.info(f"Fetched {len(df)} days of data for {symbol}")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {str(e)}")
            raise
    
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare features for ML models"""
        try:
            # Create technical features
            df = self.feature_engineer.create_technical_features(df)
            
            # Create lag features
            for lag in [1, 2, 3, 5, 10]:
                df[f'close_lag_{lag}'] = df['Close'].shift(lag)
                df[f'volume_lag_{lag}'] = df['Volume'].shift(lag)
                df[f'returns_lag_{lag}'] = df['returns'].shift(lag)
            
            # Create future targets
            df['target_1d'] = df['Close'].shift(-1)
            df['target_7d'] = df['Close'].shift(-7)
            df['target_30d'] = df['Close'].shift(-30)
            
            # Drop rows with NaN values
            df = df.dropna()
            
            logger.info(f"Prepared features: {df.shape[1]} columns, {df.shape[0]} rows")
            return df
            
        except Exception as e:
            logger.error(f"Error preparing features: {str(e)}")
            raise
    
    def select_features(self, df: pd.DataFrame) -> List[str]:
        """Select the most important features for prediction"""
        
        # Define feature categories
        price_features = [col for col in df.columns if 'sma_' in col or 'ema_' in col or 'price_to_' in col]
        momentum_features = ['rsi', 'macd', 'macd_signal', 'stoch_k', 'stoch_d']
        volatility_features = ['volatility_5', 'volatility_20', 'atr']
        volume_features = ['volume_ratio', 'price_volume']
        lag_features = [col for col in df.columns if '_lag_' in col]
        trend_features = ['trend_strength', 'trend_direction']
        support_resistance = ['support', 'resistance']
        
        # Combine all feature categories
        selected_features = (
            price_features + momentum_features + volatility_features + 
            volume_features + lag_features + trend_features + support_resistance
        )
        
        # Filter features that exist in the dataframe
        selected_features = [f for f in selected_features if f in df.columns]
        
        logger.info(f"Selected {len(selected_features)} features for training")
        return selected_features
    
    def train_models(self, symbol: str, retrain: bool = False) -> Dict[str, ModelMetrics]:
        """Train ML models for price prediction"""
        try:
            model_path = os.path.join(self.model_dir, f"{symbol}_models.joblib")
            
            # Load existing models if available and not retraining
            if os.path.exists(model_path) and not retrain:
                logger.info(f"Loading existing models for {symbol}")
                import joblib
                saved_data = joblib.load(model_path)
                self.models = saved_data['models']
                self.scalers = saved_data['scalers']
                self.model_metrics = saved_data['metrics']
                return self.model_metrics
            
            # Fetch and prepare data
            df = self.fetch_stock_data(symbol)
            df = self.prepare_features(df)
            
            # Select features
            feature_columns = self.select_features(df)
            X = df[feature_columns]
            
            # Train models for different horizons
            metrics = {}
            
            for horizon in ['1d', '7d', '30d']:
                y = df[f'target_{horizon}']
                
                # Remove rows where target is NaN
                valid_idx = ~y.isna()
                X_valid = X[valid_idx]
                y_valid = y[valid_idx]
                
                if len(X_valid) < 100:  # Need minimum data for training
                    logger.warning(f"Insufficient data for {horizon} prediction")
                    continue
                
                # Split data
                X_train, X_test, y_train, y_test = train_test_split(
                    X_valid, y_valid, test_size=0.2, random_state=42, shuffle=False
                )
                
                # Scale features
                X_train_scaled = self.scalers[horizon].fit_transform(X_train)
                X_test_scaled = self.scalers[horizon].transform(X_test)
                
                # Train each model
                horizon_metrics = {}
                
                for model_name, model in self.models.items():
                    # Train model
                    model.fit(X_train_scaled, y_train)
                    
                    # Make predictions
                    y_pred = model.predict(X_test_scaled)
                    
                    # Calculate metrics
                    mae = mean_absolute_error(y_test, y_pred)
                    mse = mean_squared_error(y_test, y_pred)
                    rmse = np.sqrt(mse)
                    r2 = r2_score(y_test, y_pred)
                    
                    # Calculate accuracy percentage
                    accuracy = 100 * (1 - mae / y_test.mean())
                    
                    # Cross-validation score
                    cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5, scoring='r2')
                    cv_score = cv_scores.mean()
                    
                    horizon_metrics[model_name] = ModelMetrics(
                        mae=mae,
                        mse=mse,
                        rmse=rmse,
                        r2=r2,
                        accuracy_percentage=max(0, accuracy),
                        cross_val_score=cv_score
                    )
                    
                    logger.info(f"{model_name} {horizon} - Accuracy: {accuracy:.2f}%, R2: {r2:.3f}")
                
                metrics[horizon] = horizon_metrics
            
            # Save models and metrics
            self.model_metrics = metrics
            import joblib
            joblib.dump({
                'models': self.models,
                'scalers': self.scalers,
                'metrics': metrics,
                'features': feature_columns,
                'trained_at': datetime.now().isoformat()
            }, model_path)
            
            logger.info(f"Models trained and saved for {symbol}")
            return metrics
            
        except Exception as e:
            logger.error(f"Error training models for {symbol}: {str(e)}")
            raise
    
    def predict_price(self, symbol: str, days_ahead: int = 1) -> PredictionResult:
        """Generate comprehensive price prediction"""
        try:
            # Determine prediction horizon
            if days_ahead <= 1:
                horizon = '1d'
            elif days_ahead <= 7:
                horizon = '7d'
            else:
                horizon = '30d'
            
            # Fetch recent data with more history for feature calculation
            df = self.fetch_stock_data(symbol, period="1y")
            df = self.prepare_features(df)
            
            # Ensure we have enough data after feature preparation
            if len(df) == 0:
                raise ValueError(f"Insufficient data after feature preparation for {symbol}")
            
            # Get latest data point
            latest_data = df.iloc[-1]
            current_price = latest_data['Close']
            
            # Select features (load from saved model if available)
            model_path = os.path.join(self.model_dir, f"{symbol}_models.joblib")
            if os.path.exists(model_path):
                import joblib
                saved_data = joblib.load(model_path)
                feature_columns = saved_data.get('features', self.select_features(df))
            else:
                feature_columns = self.select_features(df)
            
            # Ensure all feature columns exist in the dataframe
            available_features = [f for f in feature_columns if f in df.columns]
            if len(available_features) == 0:
                raise ValueError(f"No valid features found for prediction")
            
            X_latest = df[available_features].iloc[-1:].values
            
            # Scale features
            X_scaled = self.scalers[horizon].transform(X_latest)
            
            # Make predictions with ensemble
            predictions = {}
            confidences = {}
            
            for model_name, model in self.models.items():
                pred = model.predict(X_scaled)[0]
                predictions[model_name] = pred
                
                # Calculate confidence based on model performance
                if horizon in self.model_metrics and model_name in self.model_metrics[horizon]:
                    metrics = self.model_metrics[horizon][model_name]
                    confidences[model_name] = metrics.accuracy_percentage / 100
                else:
                    confidences[model_name] = 0.5  # Default confidence
            
            # Ensemble prediction (weighted average)
            weights = np.array(list(confidences.values()))
            weights = weights / weights.sum()  # Normalize weights
            
            ensemble_prediction = np.average(list(predictions.values()), weights=weights)
            ensemble_confidence = np.average(list(confidences.values()), weights=weights)
            
            # Calculate trend direction
            price_change = ensemble_prediction - current_price
            price_change_pct = (price_change / current_price) * 100
            
            if price_change_pct > 2:
                trend = 'BULLISH'
            elif price_change_pct < -2:
                trend = 'BEARISH'
            else:
                trend = 'SIDEWAYS'
            
            # Calculate volatility forecast
            volatility_forecast = latest_data.get('volatility_20', 0.02)
            
            # Calculate support and resistance levels
            support_levels = [
                latest_data.get('support', current_price * 0.95),
                current_price * 0.98,
                current_price * 0.95
            ]
            
            resistance_levels = [
                current_price * 1.02,
                current_price * 1.05,
                latest_data.get('resistance', current_price * 1.05)
            ]
            
            # Calculate risk score
            risk_score = min(1.0, volatility_forecast * 10 + (1 - ensemble_confidence))
            
            # Get model accuracy
            model_accuracy = ensemble_confidence * 100
            
            return PredictionResult(
                symbol=symbol,
                current_price=current_price,
                predicted_price_1d=ensemble_prediction if horizon == '1d' else current_price,
                predicted_price_7d=ensemble_prediction if horizon == '7d' else current_price,
                predicted_price_30d=ensemble_prediction if horizon == '30d' else current_price,
                confidence_1d=ensemble_confidence if horizon == '1d' else 0.5,
                confidence_7d=ensemble_confidence if horizon == '7d' else 0.5,
                confidence_30d=ensemble_confidence if horizon == '30d' else 0.5,
                trend_direction=trend,
                volatility_forecast=volatility_forecast,
                support_levels=support_levels,
                resistance_levels=resistance_levels,
                model_accuracy=model_accuracy,
                prediction_timestamp=datetime.now().isoformat(),
                features_used=available_features,
                risk_score=risk_score
            )
            
        except Exception as e:
            logger.error(f"Error predicting price for {symbol}: {str(e)}")
            raise
    
    def get_model_performance(self, symbol: str) -> Dict[str, Any]:
        """Get detailed model performance metrics"""
        try:
            model_path = os.path.join(self.model_dir, f"{symbol}_models.joblib")
            
            if not os.path.exists(model_path):
                return {'error': 'No trained models found for this symbol'}
            
            import joblib
            saved_data = joblib.load(model_path)
            metrics = saved_data.get('metrics', {})
            
            # Format metrics for API response
            performance = {
                'symbol': symbol,
                'trained_at': saved_data.get('trained_at'),
                'horizons': {}
            }
            
            for horizon, horizon_metrics in metrics.items():
                performance['horizons'][horizon] = {}
                for model_name, model_metrics in horizon_metrics.items():
                    performance['horizons'][horizon][model_name] = {
                        'accuracy_percentage': round(model_metrics.accuracy_percentage, 2),
                        'r2_score': round(model_metrics.r2, 3),
                        'mae': round(model_metrics.mae, 2),
                        'rmse': round(model_metrics.rmse, 2),
                        'cross_val_score': round(model_metrics.cross_val_score, 3)
                    }
            
            return performance
            
        except Exception as e:
            logger.error(f"Error getting model performance for {symbol}: {str(e)}")
            return {'error': str(e)}

# Global instance
ai_predictor = AIPricePredictor()
