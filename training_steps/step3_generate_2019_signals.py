#!/usr/bin/env python3
"""
Step 3: Generate 2019 Signals Using Trained ML Models
Uses the trained models to generate buy signals for January 2019
"""

import pandas as pd
import numpy as np
import os
import pickle
from datetime import datetime
import json
import warnings
warnings.filterwarnings('ignore')

class Signal2019Generator:
    def __init__(self):
        self.testing_data_dir = "testing_data_2019_2025"
        self.models_dir = "trained_models_2019"
        self.signals_dir = "signals_2019"
        
        # Create signals directory
        os.makedirs(self.signals_dir, exist_ok=True)
        
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
                else:
                    print(f"❌ Model not found: {model_path}")
                    
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
                
            return len(self.models) > 0
            
        except Exception as e:
            print(f"❌ Error loading models: {str(e)}")
            return False
            
    def load_january_2019_data(self):
        """Load stock data for January 2019 signal generation"""
        print("📊 Loading January 2019 data for signal generation...")
        
        if not os.path.exists(self.testing_data_dir):
            print(f"❌ Testing data directory not found: {self.testing_data_dir}")
            return None
            
        testing_files = [f for f in os.listdir(self.testing_data_dir) if f.endswith('.csv')]
        print(f"📁 Found {len(testing_files)} testing files")
        
        january_data = {}
        
        for file in testing_files:
            try:
                # Load stock data
                df = pd.read_csv(f"{self.testing_data_dir}/{file}")
                df['Date'] = pd.to_datetime(df['Date'])
                df.set_index('Date', inplace=True)
                
                # Filter for January 2019 (first month of testing period)
                jan_2019 = df[(df.index >= '2019-01-01') & (df.index <= '2019-01-31')]
                
                if len(jan_2019) > 0:
                    symbol = file.replace('_testing.csv', '')
                    january_data[symbol] = jan_2019
                    
            except Exception as e:
                print(f"❌ Error processing {file}: {str(e)}")
                continue
                
        print(f"✅ Loaded January 2019 data for {len(january_data)} stocks")
        return january_data
        
    def calculate_technical_indicators(self, df):
        """Calculate the same technical indicators used in training"""
        
        # Price-based indicators
        df['SMA_20'] = df['Close'].rolling(20).mean()
        df['SMA_50'] = df['Close'].rolling(50).mean()
        df['EMA_12'] = df['Close'].ewm(span=12).mean()
        df['EMA_26'] = df['Close'].ewm(span=26).mean()
        
        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # MACD
        df['MACD'] = df['EMA_12'] - df['EMA_26']
        df['MACD_Signal'] = df['MACD'].ewm(span=9).mean()
        df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']
        
        # Bollinger Bands
        df['BB_Middle'] = df['Close'].rolling(20).mean()
        bb_std = df['Close'].rolling(20).std()
        df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
        df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)
        df['BB_Position'] = (df['Close'] - df['BB_Lower']) / (df['BB_Upper'] - df['BB_Lower'])
        
        # Volume indicators
        df['Volume_SMA'] = df['Volume'].rolling(20).mean()
        df['Volume_Ratio'] = df['Volume'] / df['Volume_SMA']
        
        # Price momentum
        df['Price_Change_1D'] = df['Close'].pct_change(1)
        df['Price_Change_5D'] = df['Close'].pct_change(5)
        df['Price_Change_20D'] = df['Close'].pct_change(20)
        
        # Volatility
        df['Volatility_20D'] = df['Close'].pct_change().rolling(20).std()
        
        # Trend strength
        df['Trend_Strength'] = (df['Close'] - df['SMA_50']) / df['SMA_50']
        
        return df
        
    def generate_ensemble_predictions(self, features):
        """Generate predictions using ensemble of models"""
        predictions = {}
        
        # Get predictions from each model
        for name, model in self.models.items():
            if name == 'LogisticRegression':
                # Use scaled features for logistic regression
                scaled_features = self.scaler.transform(features)
                prob = model.predict_proba(scaled_features)[:, 1]
            else:
                # Use raw features for tree-based models
                prob = model.predict_proba(features)[:, 1]
                
            predictions[name] = prob
            
        # Create ensemble prediction (weighted average)
        ensemble_weights = {
            'GradientBoosting': 0.5,  # Best model gets highest weight
            'RandomForest': 0.3,
            'LogisticRegression': 0.2
        }
        
        ensemble_prob = np.zeros(len(features))
        for name, weight in ensemble_weights.items():
            if name in predictions:
                ensemble_prob += predictions[name] * weight
                
        return ensemble_prob, predictions
        
    def generate_2019_signals(self, january_data):
        """Generate buy signals for January 2019"""
        print("🎯 Generating 2019 buy signals...")
        
        signals = []
        
        for symbol, data in january_data.items():
            try:
                # Calculate technical indicators
                data_with_indicators = self.calculate_technical_indicators(data)
                
                # Get the last available day in January 2019
                last_day = data_with_indicators.dropna().iloc[-1]
                
                # Prepare features
                feature_values = []
                for col in self.feature_columns:
                    if col in last_day:
                        feature_values.append(last_day[col])
                    else:
                        feature_values.append(0)  # Default value for missing features
                        
                features = np.array(feature_values).reshape(1, -1)
                
                # Generate ensemble prediction
                ensemble_prob, individual_probs = self.generate_ensemble_predictions(features)
                
                # Create signal if probability > 70%
                if ensemble_prob[0] > 0.70:
                    signal = {
                        'symbol': symbol,
                        'date': last_day.name.strftime('%Y-%m-%d'),
                        'price': last_day['Close'],
                        'ensemble_probability': float(ensemble_prob[0]),
                        'gradient_boosting_prob': float(individual_probs.get('GradientBoosting', [0])[0]),
                        'random_forest_prob': float(individual_probs.get('RandomForest', [0])[0]),
                        'logistic_regression_prob': float(individual_probs.get('LogisticRegression', [0])[0]),
                        'rsi': last_day['RSI'],
                        'macd': last_day['MACD'],
                        'volume_ratio': last_day['Volume_Ratio'],
                        'trend_strength': last_day['Trend_Strength']
                    }
                    signals.append(signal)
                    
            except Exception as e:
                print(f"❌ Error generating signal for {symbol}: {str(e)}")
                continue
                
        # Sort signals by ensemble probability (highest first)
        signals.sort(key=lambda x: x['ensemble_probability'], reverse=True)
        
        print(f"✅ Generated {len(signals)} high-confidence signals")
        return signals
        
    def save_signals(self, signals):
        """Save generated signals"""
        print("💾 Saving 2019 signals...")
        
        # Save as JSON
        signals_file = f"{self.signals_dir}/signals_january_2019.json"
        with open(signals_file, 'w') as f:
            json.dump(signals, f, indent=2, default=str)
        print(f"✅ Saved signals to {signals_file}")
        
        # Save as CSV for easy viewing
        if signals:
            df = pd.DataFrame(signals)
            csv_file = f"{self.signals_dir}/signals_january_2019.csv"
            df.to_csv(csv_file, index=False)
            print(f"✅ Saved signals to {csv_file}")
            
        return signals_file
        
    def generate_signals_report(self, signals):
        """Generate comprehensive signals report"""
        
        if not signals:
            return "❌ No signals generated"
            
        # Top 10 signals
        top_10 = signals[:10]
        
        report = f"""
🎯 2019 MULTIBAGGER SIGNALS REPORT
==================================

📊 SIGNAL SUMMARY
- Total High-Confidence Signals: {len(signals)}
- Probability Threshold: >70%
- Signal Date: January 2019
- Based on 2014-2019 ML Training

🏆 TOP 10 SIGNALS (Highest Probability)
"""
        
        for i, signal in enumerate(top_10, 1):
            report += f"""
{i}. {signal['symbol']}
   - Probability: {signal['ensemble_probability']:.1%}
   - Price: ₹{signal['price']:.2f}
   - Date: {signal['date']}
   - RSI: {signal['rsi']:.1f}
   - MACD: {signal['macd']:.3f}
"""
        
        # Probability distribution
        prob_ranges = {
            '90-100%': len([s for s in signals if s['ensemble_probability'] >= 0.90]),
            '80-90%': len([s for s in signals if 0.80 <= s['ensemble_probability'] < 0.90]),
            '70-80%': len([s for s in signals if 0.70 <= s['ensemble_probability'] < 0.80])
        }
        
        report += f"""
📈 PROBABILITY DISTRIBUTION
- 90-100%: {prob_ranges['90-100%']} signals
- 80-90%: {prob_ranges['80-90%']} signals  
- 70-80%: {prob_ranges['70-80%']} signals

🎯 NEXT STEPS
1. Track performance of these signals from 2019-2025
2. Calculate actual returns achieved
3. Identify which became 2x, 5x, 10x multibaggers
4. Validate ML model accuracy

📁 FILES SAVED
- signals_2019/signals_january_2019.json
- signals_2019/signals_january_2019.csv
"""
        
        return report
        
    def run_signal_generation(self):
        """Run complete signal generation process"""
        print("🚀 Starting 2019 Signal Generation")
        print("=" * 50)
        
        # Step 1: Load trained models
        if not self.load_trained_models():
            print("❌ Failed to load trained models")
            return False
            
        # Step 2: Load January 2019 data
        january_data = self.load_january_2019_data()
        if not january_data:
            print("❌ Failed to load January 2019 data")
            return False
            
        # Step 3: Generate signals
        signals = self.generate_2019_signals(january_data)
        
        # Step 4: Save signals
        signals_file = self.save_signals(signals)
        
        # Step 5: Generate report
        report = self.generate_signals_report(signals)
        
        print("\n" + "=" * 50)
        print(report)
        print("=" * 50)
        
        # Save report
        report_file = f"signals_report_2019_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_file, 'w') as f:
            f.write(report)
            
        print(f"\n✅ SIGNAL GENERATION COMPLETED!")
        print(f"📊 Generated {len(signals)} high-confidence signals")
        print(f"📁 Files saved in {self.signals_dir}/")
        
        return True

if __name__ == "__main__":
    generator = Signal2019Generator()
    success = generator.run_signal_generation()
    
    if success:
        print("\n🚀 Next: Run step4_validate_multibaggers.py")
    else:
        print("\n❌ Signal generation failed. Check models and data.")
