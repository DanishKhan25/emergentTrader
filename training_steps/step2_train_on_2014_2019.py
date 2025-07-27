#!/usr/bin/env python3
"""
Step 2: Train ML Model on 2014-2019 Data
Trains ML to predict multibaggers using 5 years of historical data
"""

import pandas as pd
import numpy as np
import os
import pickle
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

class MultibaggerMLTrainer:
    def __init__(self):
        self.training_data_dir = "../data_collection/testing_data_2019_2025"
        self.models_dir = "trained_models_2019"
        self.scaler = StandardScaler()
        self.models = {}

        # Create models directory
        os.makedirs(self.models_dir, exist_ok=True)

    def load_training_data(self):
        """Load all training data from 2014-2019"""
        print("📊 Loading training data (2014-2019)...")

        if not os.path.exists(self.training_data_dir):
            print(f"❌ Training data directory not found: {self.training_data_dir}")
            return None

        training_files = [f for f in os.listdir(self.training_data_dir) if f.endswith('.csv')]
        print(f"📁 Found {len(training_files)} training files")

        all_data = []

        for i, file in enumerate(training_files):
            try:
                # Load stock data
                df = pd.read_csv(f"{self.training_data_dir}/{file}")
                df['Date'] = pd.to_datetime(df['Date'])
                df.set_index('Date', inplace=True)

                # Add symbol
                symbol = file.replace('_training.csv', '')
                df['Symbol'] = symbol

                # Calculate technical indicators
                df = self.calculate_technical_indicators(df)

                # Generate multibagger labels
                df = self.generate_multibagger_labels(df)

                all_data.append(df)

                if (i + 1) % 25 == 0:
                    print(f"Processed {i + 1}/{len(training_files)} files...")

            except Exception as e:
                print(f"❌ Error processing {file}: {str(e)}")
                continue

        if all_data:
            combined_data = pd.concat(all_data, ignore_index=True)
            print(f"✅ Combined training data: {len(combined_data):,} records")
            return combined_data
        else:
            print("❌ No training data loaded")
            return None

    def calculate_technical_indicators(self, df):
        """Calculate comprehensive technical indicators"""

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

    def generate_multibagger_labels(self, df):
        """Generate labels for multibagger prediction"""

        # Calculate future returns at different horizons
        for days in [30, 60, 90, 180, 365]:
            df[f'Future_Return_{days}D'] = df['Close'].shift(-days) / df['Close'] - 1

        # Define multibagger thresholds
        # 2x = 100%, 3x = 200%, 5x = 400%, 10x = 900%

        # Primary labels for different time horizons
        df['Multibagger_60D'] = (df['Future_Return_60D'] > 0.50).astype(int)    # 50% in 2 months
        df['Multibagger_180D'] = (df['Future_Return_180D'] > 1.0).astype(int)   # 100% in 6 months
        df['Multibagger_365D'] = (df['Future_Return_365D'] > 2.0).astype(int)   # 200% in 1 year

        # Combined multibagger label (any significant return)
        df['Is_Multibagger'] = (
            (df['Future_Return_60D'] > 0.30) |   # 30% in 2 months
            (df['Future_Return_180D'] > 0.50) |  # 50% in 6 months
            (df['Future_Return_365D'] > 1.0)     # 100% in 1 year
        ).astype(int)

        return df

    def prepare_features(self, df):
        """Prepare feature matrix for ML training"""

        feature_columns = [
            'RSI', 'MACD', 'MACD_Histogram', 'BB_Position', 'Volume_Ratio',
            'Price_Change_1D', 'Price_Change_5D', 'Price_Change_20D',
            'Volatility_20D', 'Trend_Strength'
        ]

        # Clean data - remove rows with NaN values
        clean_df = df.dropna(subset=feature_columns + ['Is_Multibagger'])

        if len(clean_df) < 1000:
            print(f"⚠️ Warning: Only {len(clean_df)} clean samples available")

        X = clean_df[feature_columns]
        y = clean_df['Is_Multibagger']

        print(f"📊 Feature matrix: {X.shape}")
        print(f"🎯 Multibagger rate: {y.mean():.2%}")

        return X, y, feature_columns

    def train_ensemble_models(self, X, y):
        """Train ensemble of ML models"""
        print("🤖 Training ensemble ML models...")

        # Split data
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_val_scaled = self.scaler.transform(X_val)

        # Train multiple models
        models_config = {
            'RandomForest': RandomForestClassifier(
                n_estimators=100, max_depth=10, random_state=42,
                class_weight='balanced'
            ),
            'GradientBoosting': GradientBoostingClassifier(
                n_estimators=100, max_depth=6, random_state=42
            ),
            'LogisticRegression': LogisticRegression(
                random_state=42, class_weight='balanced', max_iter=1000
            )
        }

        results = {}

        for name, model in models_config.items():
            print(f"Training {name}...")

            if name == 'LogisticRegression':
                model.fit(X_train_scaled, y_train)
                val_score = model.score(X_val_scaled, y_val)
                y_pred = model.predict(X_val_scaled)
            else:
                model.fit(X_train, y_train)
                val_score = model.score(X_val, y_val)
                y_pred = model.predict(X_val)

            results[name] = {
                'model': model,
                'accuracy': val_score,
                'predictions': y_pred
            }

            print(f"✅ {name} - Accuracy: {val_score:.3f}")

        # Save models
        self.models = {name: result['model'] for name, result in results.items()}

        # Print detailed results for best model
        best_model_name = max(results.keys(), key=lambda k: results[k]['accuracy'])
        best_predictions = results[best_model_name]['predictions']

        print(f"\n🏆 Best Model: {best_model_name}")
        print("\n📊 Classification Report:")
        print(classification_report(y_val, best_predictions))

        return results

    def save_trained_models(self, feature_columns):
        """Save trained models and metadata"""
        print("💾 Saving trained models...")

        # Save models
        for name, model in self.models.items():
            model_path = f"{self.models_dir}/{name}_multibagger_2019.pkl"
            with open(model_path, 'wb') as f:
                pickle.dump(model, f)
            print(f"✅ Saved {name} to {model_path}")

        # Save scaler
        scaler_path = f"{self.models_dir}/scaler_2019.pkl"
        with open(scaler_path, 'wb') as f:
            pickle.dump(self.scaler, f)
        print(f"✅ Saved scaler to {scaler_path}")

        # Save metadata
        metadata = {
            'training_period': '2014-2019',
            'feature_columns': feature_columns,
            'models_trained': list(self.models.keys()),
            'training_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'purpose': 'Multibagger prediction for 2019 signals'
        }

        metadata_path = f"{self.models_dir}/training_metadata.pkl"
        with open(metadata_path, 'wb') as f:
            pickle.dump(metadata, f)
        print(f"✅ Saved metadata to {metadata_path}")

    def generate_training_report(self, results, total_samples):
        """Generate comprehensive training report"""

        report = f"""
🎯 MULTIBAGGER ML TRAINING REPORT (2014-2019)
==============================================

📊 TRAINING DATA
- Training Period: 2014-01-01 to 2019-12-31
- Total Samples: {total_samples:,}
- Training Files: 165 stocks
- Features Used: 10 technical indicators

🤖 MODEL PERFORMANCE
"""

        for name, result in results.items():
            report += f"- {name}: {result['accuracy']:.3f} accuracy\n"

        best_model = max(results.keys(), key=lambda k: results[k]['accuracy'])

        report += f"""
🏆 BEST MODEL: {best_model}
- Accuracy: {results[best_model]['accuracy']:.3f}
- Ready for 2019 signal generation

🎯 NEXT STEPS
1. Generate signals for January 2019
2. Track performance through 2019-2025
3. Identify multibaggers and validate model
4. If successful → retrain with complete data

📁 SAVED FILES
- Models: trained_models_2019/
- Ready for step3_generate_2019_signals.py
"""

        return report

    def run_complete_training(self):
        """Run complete training pipeline"""
        print("🚀 Starting ML Training on 2014-2019 Data")
        print("=" * 50)
        
        # Step 1: Load training data
        training_data = self.load_training_data()
        if training_data is None:
            return False
            
        # Step 2: Prepare features
        X, y, feature_columns = self.prepare_features(training_data)
        
        # Step 3: Train models
        results = self.train_ensemble_models(X, y)
        
        # Step 4: Save models
        self.save_trained_models(feature_columns)
        
        # Step 5: Generate report
        report = self.generate_training_report(results, len(training_data))
        
        print("\n" + "=" * 50)
        print(report)
        print("=" * 50)
        
        # Save report
        with open(f"training_report_2019_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt", 'w') as f:
            f.write(report)
            
        print(f"\n✅ TRAINING COMPLETED!")
        print(f"🎯 Models ready for 2019 signal generation")
        
        return True

if __name__ == "__main__":
    trainer = MultibaggerMLTrainer()
    success = trainer.run_complete_training()
    
    if success:
        print("\n🚀 Next: Run step3_generate_2019_signals.py")
    else:
        print("\n❌ Training failed. Check data and try again.")
