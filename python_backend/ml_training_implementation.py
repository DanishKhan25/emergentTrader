#!/usr/bin/env python3
"""
ML Training Implementation for EmergentTrader
Practical implementation to start training ML models
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split, TimeSeriesSplit
from sklearn.metrics import classification_report, roc_auc_score, mean_squared_error
import joblib
import warnings
warnings.filterwarnings('ignore')

# Add the python_backend directory to the path
try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
except NameError:
    current_dir = os.getcwd()

sys.path.append(current_dir)

from core.enhanced_signal_engine import EnhancedSignalEngine
from core.signal_database import SignalDatabase

class MLTrainingStarter:
    """Practical ML training implementation to get started quickly"""
    
    def __init__(self):
        self.engine = EnhancedSignalEngine()
        self.db = SignalDatabase()
        
    def collect_current_signals_for_training(self):
        """Use current signals as starting point for ML training"""
        print("📊 Collecting current signals for ML training...")
        
        # Get current active signals
        current_signals = self.db.get_active_signals()
        
        if not current_signals:
            print("❌ No signals found in database. Generate some signals first!")
            return None
        
        print(f"Found {len(current_signals)} current signals")
        
        # Enhance signals with additional features for ML
        enhanced_signals = []
        
        for signal in current_signals:
            try:
                # Get current stock data
                stock_data = yf.download(signal['symbol'], period='1y', progress=False)
                
                if stock_data.empty:
                    continue
                
                # Calculate additional features
                current_price = stock_data['Close'].iloc[-1]
                volatility = stock_data['Close'].pct_change().std() * np.sqrt(252)
                
                # Technical indicators
                stock_data['sma_20'] = stock_data['Close'].rolling(20).mean()
                stock_data['sma_50'] = stock_data['Close'].rolling(50).mean()
                stock_data['rsi'] = self.calculate_rsi(stock_data['Close'])
                
                latest_rsi = stock_data['rsi'].iloc[-1] if not pd.isna(stock_data['rsi'].iloc[-1]) else 50
                sma_20 = stock_data['sma_20'].iloc[-1]
                sma_50 = stock_data['sma_50'].iloc[-1]
                
                # Market context
                nifty_data = yf.download('^NSEI', period='6m', progress=False)
                market_trend = 1 if nifty_data['Close'].iloc[-1] > nifty_data['Close'].iloc[-30] else 0
                
                enhanced_signal = {
                    'signal_id': signal['signal_id'],
                    'symbol': signal['symbol'],
                    'strategy': signal['strategy'],
                    'confidence': signal.get('confidence', 0),
                    'current_price': current_price,
                    'volatility': volatility,
                    'rsi': latest_rsi,
                    'price_above_sma20': 1 if current_price > sma_20 else 0,
                    'price_above_sma50': 1 if current_price > sma_50 else 0,
                    'market_trend': market_trend,
                    'generated_at': signal['generated_at']
                }
                
                enhanced_signals.append(enhanced_signal)
                
            except Exception as e:
                print(f"Error processing {signal['symbol']}: {str(e)}")
                continue
        
        return pd.DataFrame(enhanced_signals)
    
    def simulate_historical_outcomes(self, signals_df):
        """Simulate historical outcomes for training (since we don't have real outcomes yet)"""
        print("🎯 Simulating historical outcomes for training...")
        
        training_data = []
        
        for _, signal in signals_df.iterrows():
            try:
                # Get historical data to simulate outcome
                symbol = signal['symbol']
                stock_data = yf.download(symbol, period='2y', progress=False)
                
                if len(stock_data) < 100:
                    continue
                
                # Simulate multiple historical scenarios
                for i in range(50, len(stock_data) - 30, 10):  # Every 10 days
                    historical_price = stock_data['Close'].iloc[i]
                    future_price = stock_data['Close'].iloc[i + 30]  # 30 days later
                    
                    # Calculate return
                    return_pct = (future_price - historical_price) / historical_price
                    
                    # Simulate signal features at that historical point
                    hist_volatility = stock_data['Close'].iloc[i-20:i].pct_change().std() * np.sqrt(252)
                    hist_rsi = self.calculate_rsi(stock_data['Close'].iloc[i-14:i+1]).iloc[-1]
                    
                    # Create training sample
                    training_sample = {
                        'strategy': signal['strategy'],
                        'confidence': signal['confidence'] + np.random.normal(0, 0.1),  # Add noise
                        'volatility': hist_volatility,
                        'rsi': hist_rsi if not pd.isna(hist_rsi) else 50,
                        'market_trend': np.random.choice([0, 1]),  # Simulate market trend
                        
                        # Target variables
                        'success': 1 if return_pct > 0.02 else 0,  # 2% profit threshold
                        'return_pct': return_pct,
                        'profitable': 1 if return_pct > 0 else 0
                    }
                    
                    training_data.append(training_sample)
                    
            except Exception as e:
                print(f"Error simulating outcomes for {signal['symbol']}: {str(e)}")
                continue
        
        return pd.DataFrame(training_data)
    
    def calculate_rsi(self, prices, window=14):
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def train_signal_quality_model(self, training_data):
        """Train a simple signal quality classifier"""
        print("🤖 Training signal quality model...")
        
        # Prepare features
        feature_columns = ['confidence', 'volatility', 'rsi', 'market_trend']
        X = training_data[feature_columns].fillna(0)
        y = training_data['success']
        
        print(f"Training data shape: {X.shape}")
        print(f"Success rate in training data: {y.mean():.2%}")
        
        # Time series split for validation
        tscv = TimeSeriesSplit(n_splits=3)
        
        # Train model
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=20,
            random_state=42
        )
        
        # Cross-validation
        cv_scores = []
        for train_idx, val_idx in tscv.split(X):
            X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
            y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]
            
            model.fit(X_train, y_train)
            val_pred = model.predict_proba(X_val)[:, 1]
            score = roc_auc_score(y_val, val_pred)
            cv_scores.append(score)
        
        print(f"Cross-validation AUC scores: {cv_scores}")
        print(f"Mean CV AUC: {np.mean(cv_scores):.4f} ± {np.std(cv_scores):.4f}")
        
        # Train final model on all data
        model.fit(X, y)
        
        # Feature importance
        feature_importance = pd.DataFrame({
            'feature': feature_columns,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print("\\nFeature Importance:")
        print(feature_importance)
        
        return model, feature_columns, np.mean(cv_scores)
    
    def train_return_predictor(self, training_data):
        """Train a model to predict expected returns"""
        print("📈 Training return prediction model...")
        
        # Prepare features
        feature_columns = ['confidence', 'volatility', 'rsi', 'market_trend']
        X = training_data[feature_columns].fillna(0)
        y = training_data['return_pct']
        
        # Train model
        model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            min_samples_split=20,
            random_state=42
        )
        
        # Time series split
        tscv = TimeSeriesSplit(n_splits=3)
        cv_scores = []
        
        for train_idx, val_idx in tscv.split(X):
            X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
            y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]
            
            model.fit(X_train, y_train)
            val_pred = model.predict(X_val)
            score = -mean_squared_error(y_val, val_pred)  # Negative MSE for scoring
            cv_scores.append(score)
        
        print(f"Cross-validation MSE scores: {[-s for s in cv_scores]}")
        print(f"Mean CV MSE: {-np.mean(cv_scores):.6f}")
        
        # Train final model
        model.fit(X, y)
        
        return model, feature_columns, -np.mean(cv_scores)
    
    def save_models(self, models_dict):
        """Save trained models"""
        print("💾 Saving trained models...")
        
        # Create models directory
        os.makedirs('models', exist_ok=True)
        
        for model_name, model_data in models_dict.items():
            joblib.dump(model_data, f'models/{model_name}.pkl')
            print(f"Saved {model_name} model")
    
    def test_models(self, models_dict):
        """Test the trained models with current signals"""
        print("🧪 Testing trained models...")
        
        # Get current signals
        current_signals = self.db.get_active_signals()
        
        if not current_signals:
            print("No current signals to test")
            return
        
        quality_model = models_dict['signal_quality']['model']
        return_model = models_dict['return_predictor']['model']
        feature_columns = models_dict['signal_quality']['features']
        
        print("\\nML Predictions for Current Signals:")
        print("-" * 60)
        
        for signal in current_signals:
            try:
                # Prepare features (simplified for testing)
                features = [
                    signal.get('confidence', 0.5),
                    0.2,  # Default volatility
                    50,   # Default RSI
                    1     # Default market trend
                ]
                
                # Make predictions
                quality_prob = quality_model.predict_proba([features])[0][1]
                expected_return = return_model.predict([features])[0]
                
                print(f"{signal['symbol']} ({signal['strategy']}):")
                print(f"  Success Probability: {quality_prob:.2%}")
                print(f"  Expected Return: {expected_return:.2%}")
                print(f"  ML Recommendation: {'TAKE' if quality_prob > 0.6 else 'SKIP'}")
                print()
                
            except Exception as e:
                print(f"Error predicting for {signal['symbol']}: {str(e)}")
    
    def run_training_pipeline(self):
        """Run the complete ML training pipeline"""
        print("🚀 Starting ML Training Pipeline for EmergentTrader")
        print("=" * 60)
        
        # Step 1: Collect current signals
        signals_df = self.collect_current_signals_for_training()
        if signals_df is None or len(signals_df) == 0:
            print("❌ No signals available for training. Generate signals first!")
            return
        
        # Step 2: Simulate historical outcomes
        training_data = self.simulate_historical_outcomes(signals_df)
        if len(training_data) == 0:
            print("❌ Could not generate training data")
            return
        
        print(f"Generated {len(training_data)} training samples")
        
        # Step 3: Train models
        quality_model, quality_features, quality_score = self.train_signal_quality_model(training_data)
        return_model, return_features, return_score = self.train_return_predictor(training_data)
        
        # Step 4: Save models
        models_dict = {
            'signal_quality': {
                'model': quality_model,
                'features': quality_features,
                'score': quality_score
            },
            'return_predictor': {
                'model': return_model,
                'features': return_features,
                'score': return_score
            }
        }
        
        self.save_models(models_dict)
        
        # Step 5: Test models
        self.test_models(models_dict)
        
        print("\\n✅ ML Training Pipeline Complete!")
        print(f"Signal Quality Model AUC: {quality_score:.4f}")
        print(f"Return Predictor MSE: {return_score:.6f}")
        
        return models_dict

def main():
    """Run ML training"""
    trainer = MLTrainingStarter()
    models = trainer.run_training_pipeline()
    
    if models:
        print("\\n🎯 Next Steps:")
        print("1. Generate more signals to improve training data")
        print("2. Implement real-time ML inference in signal generation")
        print("3. Add more sophisticated features (news sentiment, etc.)")
        print("4. Implement proper backtesting with historical data")

if __name__ == "__main__":
    main()
