#!/usr/bin/env python3
"""
Step 3: Diagnostic Signal Generation
Check what probabilities our ML models are generating
"""

import pandas as pd
import numpy as np
import os
import pickle
from datetime import datetime
import json
import warnings
warnings.filterwarnings('ignore')

class DiagnosticSignalGenerator:
    def __init__(self):
        self.testing_data_dir = "testing_data_2019_2025"
        self.models_dir = "trained_models_2019"
        
        # Load trained models
        self.models = {}
        self.scaler = None
        self.feature_columns = []
        
    def load_trained_models(self):
        """Load the trained ML models"""
        print("🤖 Loading trained ML models...")
        
        try:
            # Load models
            model_files = {
                'RandomForest': 'RandomForest_multibagger_2019.pkl',
                'GradientBoosting': 'GradientBoosting_multibagger_2019.pkl',
                'LogisticRegression': 'LogisticRegression_multibagger_2019.pkl'
            }
            
            for name, filename in model_files.items():
                model_path = f"{self.models_dir}/{filename}"
                if os.path.exists(model_path):
                    with open(model_path, 'rb') as f:
                        self.models[name] = pickle.load(f)
                    print(f"✅ Loaded {name}")
                    
            # Load scaler
            scaler_path = f"{self.models_dir}/scaler_2019.pkl"
            if os.path.exists(scaler_path):
                with open(scaler_path, 'rb') as f:
                    self.scaler = pickle.load(f)
                print("✅ Loaded scaler")
                
            # Load metadata
            metadata_path = f"{self.models_dir}/training_metadata.pkl"
            if os.path.exists(metadata_path):
                with open(metadata_path, 'rb') as f:
                    metadata = pickle.load(f)
                    self.feature_columns = metadata['feature_columns']
                print("✅ Loaded feature columns")
                print(f"📊 Features: {self.feature_columns}")
                
            return len(self.models) > 0
            
        except Exception as e:
            print(f"❌ Error loading models: {str(e)}")
            return False
            
    def test_sample_predictions(self):
        """Test predictions on a few sample stocks"""
        print("\n🔍 DIAGNOSTIC: Testing sample predictions...")
        
        # Get a few sample files
        testing_files = [f for f in os.listdir(self.testing_data_dir) if f.endswith('.csv')][:10]
        
        all_probabilities = []
        
        for file in testing_files:
            try:
                symbol = file.replace('_testing.csv', '')
                print(f"\n📊 Testing {symbol}:")
                
                # Load data
                df = pd.read_csv(f"{self.testing_data_dir}/{file}")
                df['Date'] = pd.to_datetime(df['Date'])
                df.set_index('Date', inplace=True)
                
                # Get early 2019 data
                early_2019 = df[(df.index >= '2019-01-01') & (df.index <= '2019-03-31')]
                
                if len(early_2019) < 20:
                    print(f"❌ Insufficient data: {len(early_2019)} records")
                    continue
                    
                # Calculate indicators
                data_with_indicators = self.calculate_technical_indicators(early_2019)
                
                if data_with_indicators is None:
                    print("❌ Failed to calculate indicators")
                    continue
                    
                # Get valid data
                valid_data = data_with_indicators.dropna(subset=self.feature_columns)
                
                if len(valid_data) == 0:
                    print("❌ No valid data after indicator calculation")
                    continue
                    
                # Use last available data point
                signal_row = valid_data.iloc[-1]
                
                # Prepare features
                feature_values = []
                for col in self.feature_columns:
                    if col in signal_row and not pd.isna(signal_row[col]):
                        feature_values.append(signal_row[col])
                    else:
                        defaults = {
                            'RSI': 50, 'MACD': 0, 'MACD_Histogram': 0, 'BB_Position': 0.5,
                            'Volume_Ratio': 1.0, 'Price_Change_1D': 0, 'Price_Change_5D': 0,
                            'Price_Change_20D': 0, 'Volatility_20D': 0.02, 'Trend_Strength': 0
                        }
                        feature_values.append(defaults.get(col, 0))
                        
                features = np.array(feature_values).reshape(1, -1)
                
                # Get predictions from each model
                predictions = {}
                for name, model in self.models.items():
                    try:
                        if name == 'LogisticRegression':
                            scaled_features = self.scaler.transform(features)
                            prob = model.predict_proba(scaled_features)[0, 1]
                        else:
                            prob = model.predict_proba(features)[0, 1]
                        predictions[name] = prob
                        print(f"  {name}: {prob:.3f}")
                    except Exception as e:
                        print(f"  ❌ {name}: Error - {str(e)}")
                        
                # Calculate ensemble
                if predictions:
                    ensemble_weights = {'GradientBoosting': 0.5, 'RandomForest': 0.3, 'LogisticRegression': 0.2}
                    ensemble_prob = sum(predictions.get(name, 0) * weight for name, weight in ensemble_weights.items())
                    print(f"  🎯 Ensemble: {ensemble_prob:.3f}")
                    
                    all_probabilities.append({
                        'symbol': symbol,
                        'ensemble': ensemble_prob,
                        **predictions
                    })
                    
            except Exception as e:
                print(f"❌ Error testing {symbol}: {str(e)}")
                continue
                
        # Summary statistics
        if all_probabilities:
            print(f"\n📈 PROBABILITY STATISTICS:")
            ensemble_probs = [p['ensemble'] for p in all_probabilities]
            print(f"Mean: {np.mean(ensemble_probs):.3f}")
            print(f"Median: {np.median(ensemble_probs):.3f}")
            print(f"Min: {np.min(ensemble_probs):.3f}")
            print(f"Max: {np.max(ensemble_probs):.3f}")
            print(f"Std: {np.std(ensemble_probs):.3f}")
            
            # Count by thresholds
            thresholds = [0.5, 0.6, 0.65, 0.7, 0.75, 0.8]
            for threshold in thresholds:
                count = len([p for p in ensemble_probs if p >= threshold])
                print(f"≥{threshold}: {count}/{len(ensemble_probs)} ({count/len(ensemble_probs)*100:.1f}%)")
                
        return all_probabilities
        
    def calculate_technical_indicators(self, df):
        """Calculate technical indicators with proper error handling"""
        try:
            if len(df) < 20:
                return None
                
            # Price-based indicators
            df['SMA_20'] = df['Close'].rolling(20, min_periods=5).mean()
            df['SMA_50'] = df['Close'].rolling(50, min_periods=10).mean()
            df['EMA_12'] = df['Close'].ewm(span=12, min_periods=3).mean()
            df['EMA_26'] = df['Close'].ewm(span=26, min_periods=5).mean()
            
            # RSI
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14, min_periods=3).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14, min_periods=3).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))
            
            # MACD
            df['MACD'] = df['EMA_12'] - df['EMA_26']
            df['MACD_Signal'] = df['MACD'].ewm(span=9, min_periods=2).mean()
            df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']
            
            # Bollinger Bands
            df['BB_Middle'] = df['Close'].rolling(20, min_periods=5).mean()
            bb_std = df['Close'].rolling(20, min_periods=5).std()
            df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
            df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)
            
            bb_range = df['BB_Upper'] - df['BB_Lower']
            df['BB_Position'] = np.where(bb_range > 0, 
                                       (df['Close'] - df['BB_Lower']) / bb_range, 
                                       0.5)
            
            # Volume indicators
            df['Volume_SMA'] = df['Volume'].rolling(20, min_periods=5).mean()
            df['Volume_Ratio'] = np.where(df['Volume_SMA'] > 0, 
                                        df['Volume'] / df['Volume_SMA'], 
                                        1.0)
            
            # Price momentum
            df['Price_Change_1D'] = df['Close'].pct_change(1)
            df['Price_Change_5D'] = df['Close'].pct_change(5)
            df['Price_Change_20D'] = df['Close'].pct_change(20)
            
            # Volatility
            df['Volatility_20D'] = df['Close'].pct_change().rolling(20, min_periods=5).std()
            
            # Trend strength
            df['Trend_Strength'] = np.where(df['SMA_50'] > 0, 
                                          (df['Close'] - df['SMA_50']) / df['SMA_50'], 
                                          0)
            
            return df
            
        except Exception as e:
            print(f"❌ Error calculating indicators: {str(e)}")
            return None
            
    def run_diagnostic(self):
        """Run diagnostic analysis"""
        print("🔍 Starting Diagnostic Analysis")
        print("=" * 50)
        
        # Load models
        if not self.load_trained_models():
            return False
            
        # Test sample predictions
        probabilities = self.test_sample_predictions()
        
        print("\n" + "=" * 50)
        print("🎯 DIAGNOSTIC COMPLETE")
        
        return True

if __name__ == "__main__":
    diagnostic = DiagnosticSignalGenerator()
    diagnostic.run_diagnostic()
