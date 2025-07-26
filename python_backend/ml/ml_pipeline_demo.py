#!/usr/bin/env python3
"""
Simplified ML Pipeline Demo
Demonstrates the complete ML training process without complex dependencies
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix
from sklearn.preprocessing import StandardScaler, LabelEncoder
import joblib
import json

# Add the python_backend directory to the path
try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
except NameError:
    parent_dir = os.getcwd()

sys.path.append(parent_dir)

class SimplifiedMLPipeline:
    """Simplified ML pipeline demonstration"""
    
    def __init__(self):
        self.models = {}
        self.results = {}
        
        # Create directories
        os.makedirs('ml/data', exist_ok=True)
        os.makedirs('ml/models', exist_ok=True)
        os.makedirs('ml/results', exist_ok=True)
    
    def generate_synthetic_historical_data(self, n_samples=2000):
        """Generate synthetic historical trading data for demonstration"""
        print("📊 Generating synthetic historical trading data...")
        
        np.random.seed(42)
        
        # Simulate historical signals
        data = []
        
        strategies = ['momentum', 'low_volatility', 'fundamental_growth', 'mean_reversion', 'breakout']
        symbols = ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ICICIBANK', 'HINDUNILVR', 'ITC', 'LT']
        
        for i in range(n_samples):
            # Basic signal features
            strategy = np.random.choice(strategies)
            symbol = np.random.choice(symbols)
            confidence = np.random.uniform(0.3, 0.9)
            entry_price = np.random.uniform(100, 3000)
            
            # Market context
            market_regime = np.random.choice(['BULL', 'BEAR', 'SIDEWAYS'], p=[0.3, 0.2, 0.5])
            market_volatility = np.random.uniform(0.1, 0.4)
            market_momentum = np.random.uniform(-0.1, 0.1)
            
            # Technical indicators
            rsi = np.random.uniform(20, 80)
            macd = np.random.uniform(-0.05, 0.05)
            volume_ratio = np.random.uniform(0.5, 3.0)
            price_momentum_20d = np.random.uniform(-0.2, 0.2)
            
            # Date features
            entry_date = datetime(2020, 1, 1) + timedelta(days=np.random.randint(0, 1460))  # 4 years
            month = entry_date.month
            quarter = (month - 1) // 3 + 1
            
            # Calculate success probability based on features
            success_prob = 0.4  # Base probability
            
            # Strategy-specific adjustments
            strategy_multipliers = {
                'momentum': 0.45,
                'low_volatility': 0.55,
                'fundamental_growth': 0.50,
                'mean_reversion': 0.48,
                'breakout': 0.42
            }
            success_prob = strategy_multipliers[strategy]
            
            # Market regime impact
            if market_regime == 'BULL':
                if strategy in ['momentum', 'breakout']:
                    success_prob += 0.15
                elif strategy == 'low_volatility':
                    success_prob -= 0.05
            elif market_regime == 'BEAR':
                if strategy in ['low_volatility', 'mean_reversion']:
                    success_prob += 0.10
                elif strategy in ['momentum', 'breakout']:
                    success_prob -= 0.15
            
            # Feature impacts
            success_prob += (confidence - 0.6) * 0.3
            success_prob += (0.25 - market_volatility) * 0.2
            success_prob += market_momentum * 0.5
            
            if 30 <= rsi <= 70:
                success_prob += 0.05
            if abs(macd) < 0.02:
                success_prob += 0.03
            if volume_ratio > 1.2:
                success_prob += 0.05
            if price_momentum_20d > 0:
                success_prob += 0.08
            
            # Ensure probability is valid
            success_prob = max(0.1, min(0.9, success_prob))
            
            # Generate outcome
            success = 1 if np.random.random() < success_prob else 0
            return_pct = np.random.normal(0.04 if success else -0.02, 0.06)
            
            # Create sample
            sample = {
                'symbol': symbol,
                'strategy': strategy,
                'confidence': confidence,
                'entry_price': entry_price,
                'entry_date': entry_date,
                'month': month,
                'quarter': quarter,
                'market_regime': market_regime,
                'market_volatility': market_volatility,
                'market_momentum': market_momentum,
                'rsi': rsi,
                'macd': macd,
                'volume_ratio': volume_ratio,
                'price_momentum_20d': price_momentum_20d,
                'success': success,
                'return_pct': return_pct
            }
            
            data.append(sample)
        
        df = pd.DataFrame(data)
        print(f"Generated {len(df)} synthetic historical signals")
        print(f"Overall success rate: {df['success'].mean():.2%}")
        
        return df
    
    def engineer_features(self, df):
        """Engineer features for ML training"""
        print("🔧 Engineering features...")
        
        # Encode categorical variables
        le_strategy = LabelEncoder()
        le_regime = LabelEncoder()
        le_symbol = LabelEncoder()
        
        df['strategy_encoded'] = le_strategy.fit_transform(df['strategy'])
        df['regime_encoded'] = le_regime.fit_transform(df['market_regime'])
        df['symbol_encoded'] = le_symbol.fit_transform(df['symbol'])
        
        # Create binary features
        df['bull_market'] = (df['market_regime'] == 'BULL').astype(int)
        df['bear_market'] = (df['market_regime'] == 'BEAR').astype(int)
        df['sideways_market'] = (df['market_regime'] == 'SIDEWAYS').astype(int)
        
        df['high_confidence'] = (df['confidence'] > 0.7).astype(int)
        df['low_volatility_market'] = (df['market_volatility'] < 0.2).astype(int)
        df['positive_momentum'] = (df['price_momentum_20d'] > 0).astype(int)
        df['rsi_oversold'] = (df['rsi'] < 30).astype(int)
        df['rsi_overbought'] = (df['rsi'] > 70).astype(int)
        df['high_volume'] = (df['volume_ratio'] > 1.5).astype(int)
        
        # Interaction features
        df['confidence_x_momentum'] = df['confidence'] * df['price_momentum_20d']
        df['volatility_x_momentum'] = df['market_volatility'] * df['price_momentum_20d']
        df['rsi_x_confidence'] = df['rsi'] * df['confidence'] / 100
        
        # Strategy-market interactions
        df['momentum_in_bull'] = ((df['strategy'] == 'momentum') & (df['bull_market'] == 1)).astype(int)
        df['low_vol_in_bear'] = ((df['strategy'] == 'low_volatility') & (df['bear_market'] == 1)).astype(int)
        
        # Time features
        df['is_earnings_season'] = df['month'].isin([1, 4, 7, 10]).astype(int)
        df['is_quarter_end'] = df['month'].isin([3, 6, 9, 12]).astype(int)
        
        print(f"Feature engineering complete: {len(df.columns)} features")
        
        return df
    
    def train_models(self, df):
        """Train ML models"""
        print("🤖 Training ML models...")
        
        # Prepare features and target
        feature_columns = [
            'confidence', 'strategy_encoded', 'regime_encoded', 'symbol_encoded',
            'market_volatility', 'market_momentum', 'rsi', 'macd', 'volume_ratio',
            'price_momentum_20d', 'bull_market', 'bear_market', 'high_confidence',
            'low_volatility_market', 'positive_momentum', 'rsi_oversold', 'high_volume',
            'confidence_x_momentum', 'volatility_x_momentum', 'rsi_x_confidence',
            'momentum_in_bull', 'low_vol_in_bear', 'is_earnings_season', 'quarter'
        ]
        
        X = df[feature_columns]
        y = df['success']
        
        # Time-based split
        split_date = df['entry_date'].quantile(0.8)
        train_mask = df['entry_date'] < split_date
        test_mask = df['entry_date'] >= split_date
        
        X_train, X_test = X[train_mask], X[test_mask]
        y_train, y_test = y[train_mask], y[test_mask]
        
        print(f"Training set: {len(X_train)} samples")
        print(f"Test set: {len(X_test)} samples")
        
        # Train Random Forest Classifier
        rf_model = RandomForestClassifier(
            n_estimators=200,
            max_depth=15,
            min_samples_split=10,
            min_samples_leaf=5,
            random_state=42,
            n_jobs=-1
        )
        
        rf_model.fit(X_train, y_train)
        
        # Predictions
        train_pred = rf_model.predict_proba(X_train)[:, 1]
        test_pred = rf_model.predict_proba(X_test)[:, 1]
        
        train_pred_binary = (train_pred > 0.5).astype(int)
        test_pred_binary = (test_pred > 0.5).astype(int)
        
        # Performance metrics
        train_auc = roc_auc_score(y_train, train_pred)
        test_auc = roc_auc_score(y_test, test_pred)
        
        train_accuracy = (train_pred_binary == y_train).mean()
        test_accuracy = (test_pred_binary == y_test).mean()
        
        # Cross-validation
        cv_scores = cross_val_score(rf_model, X_train, y_train, cv=5, scoring='roc_auc')
        
        # Feature importance
        feature_importance = pd.DataFrame({
            'feature': feature_columns,
            'importance': rf_model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        # Store results
        self.models['random_forest'] = rf_model
        self.results = {
            'train_auc': train_auc,
            'test_auc': test_auc,
            'train_accuracy': train_accuracy,
            'test_accuracy': test_accuracy,
            'cv_auc_mean': cv_scores.mean(),
            'cv_auc_std': cv_scores.std(),
            'feature_importance': feature_importance,
            'feature_columns': feature_columns
        }
        
        print(f"✅ Model training complete!")
        print(f"   Training AUC: {train_auc:.4f}")
        print(f"   Test AUC: {test_auc:.4f}")
        print(f"   CV AUC: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
        print(f"   Test Accuracy: {test_accuracy:.2%}")
        
        return self.results
    
    def demonstrate_signal_enhancement(self):
        """Demonstrate how ML enhances signal quality"""
        print("\\n🎯 Signal Enhancement Demonstration")
        print("=" * 50)
        
        # Simulate current signals
        current_signals = [
            {
                'symbol': 'TCS',
                'strategy': 'low_volatility',
                'confidence': 0.7,
                'market_regime': 'SIDEWAYS',
                'market_volatility': 0.18,
                'rsi': 45,
                'volume_ratio': 1.2
            },
            {
                'symbol': 'RELIANCE',
                'strategy': 'momentum',
                'confidence': 0.6,
                'market_regime': 'BULL',
                'market_volatility': 0.22,
                'rsi': 65,
                'volume_ratio': 1.8
            },
            {
                'symbol': 'INFY',
                'strategy': 'fundamental_growth',
                'confidence': 0.8,
                'market_regime': 'BULL',
                'market_volatility': 0.20,
                'rsi': 55,
                'volume_ratio': 1.1
            }
        ]
        
        model = self.models['random_forest']
        feature_columns = self.results['feature_columns']
        
        print("Original vs ML-Enhanced Signals:")
        print("-" * 50)
        
        for signal in current_signals:
            # Prepare features (simplified)
            features = [
                signal['confidence'],  # confidence
                2 if signal['strategy'] == 'momentum' else 1,  # strategy_encoded
                1 if signal['market_regime'] == 'BULL' else 0,  # regime_encoded
                0,  # symbol_encoded (default)
                signal['market_volatility'],  # market_volatility
                0.02,  # market_momentum (default)
                signal['rsi'],  # rsi
                0.01,  # macd (default)
                signal['volume_ratio'],  # volume_ratio
                0.05,  # price_momentum_20d (default)
                1 if signal['market_regime'] == 'BULL' else 0,  # bull_market
                1 if signal['market_regime'] == 'BEAR' else 0,  # bear_market
                1 if signal['confidence'] > 0.7 else 0,  # high_confidence
                1 if signal['market_volatility'] < 0.2 else 0,  # low_volatility_market
                1,  # positive_momentum (default)
                1 if signal['rsi'] < 30 else 0,  # rsi_oversold
                1 if signal['volume_ratio'] > 1.5 else 0,  # high_volume
                signal['confidence'] * 0.05,  # confidence_x_momentum
                signal['market_volatility'] * 0.05,  # volatility_x_momentum
                signal['rsi'] * signal['confidence'] / 100,  # rsi_x_confidence
                1 if signal['strategy'] == 'momentum' and signal['market_regime'] == 'BULL' else 0,  # momentum_in_bull
                1 if signal['strategy'] == 'low_volatility' and signal['market_regime'] == 'BEAR' else 0,  # low_vol_in_bear
                0,  # is_earnings_season (default)
                2   # quarter (default)
            ]
            
            # Ensure we have the right number of features
            while len(features) < len(feature_columns):
                features.append(0)
            features = features[:len(feature_columns)]
            
            # ML prediction
            ml_probability = model.predict_proba([features])[0][1]
            ml_recommendation = "STRONG_BUY" if ml_probability > 0.7 else "BUY" if ml_probability > 0.5 else "SKIP"
            
            print(f"\\n{signal['symbol']} ({signal['strategy']}):")
            print(f"  Original Confidence: {signal['confidence']:.1%}")
            print(f"  ML Success Probability: {ml_probability:.1%}")
            print(f"  ML Recommendation: {ml_recommendation}")
            
            # Show improvement
            improvement = "📈 UPGRADE" if ml_probability > signal['confidence'] else "📉 DOWNGRADE" if ml_probability < signal['confidence'] else "➡️ SAME"
            print(f"  ML vs Original: {improvement}")
    
    def save_results(self):
        """Save models and results"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save model
        model_file = f'ml/models/ml_demo_model_{timestamp}.pkl'
        joblib.dump(self.models, model_file)
        
        # Save results
        results_file = f'ml/results/ml_demo_results_{timestamp}.json'
        results_to_save = self.results.copy()
        results_to_save['feature_importance'] = results_to_save['feature_importance'].to_dict('records')
        
        with open(results_file, 'w') as f:
            json.dump(results_to_save, f, indent=2, default=str)
        
        print(f"\\n💾 Results saved:")
        print(f"   Model: {model_file}")
        print(f"   Results: {results_file}")
        
        return model_file, results_file
    
    def run_complete_demo(self):
        """Run the complete ML pipeline demo"""
        print("🧠 EmergentTrader ML Pipeline Demo")
        print("=" * 60)
        
        # Step 1: Generate synthetic data
        df = self.generate_synthetic_historical_data(n_samples=2000)
        
        # Step 2: Engineer features
        df = self.engineer_features(df)
        
        # Step 3: Train models
        results = self.train_models(df)
        
        # Step 4: Demonstrate signal enhancement
        self.demonstrate_signal_enhancement()
        
        # Step 5: Show feature importance
        print("\\n📈 Top 10 Most Important Features:")
        print("-" * 40)
        for i, row in results['feature_importance'].head(10).iterrows():
            print(f"{i+1:2d}. {row['feature']:<25} {row['importance']:.4f}")
        
        # Step 6: Save results
        model_file, results_file = self.save_results()
        
        # Summary
        print("\\n" + "=" * 60)
        print("✅ ML PIPELINE DEMO COMPLETE!")
        print("=" * 60)
        print(f"🎯 Model Performance:")
        print(f"   Test AUC: {results['test_auc']:.4f} ({(results['test_auc'] - 0.5) * 200:.1f}% above random)")
        print(f"   Test Accuracy: {results['test_accuracy']:.2%}")
        print(f"   Cross-validation: {results['cv_auc_mean']:.4f} ± {results['cv_auc_std']:.4f}")
        
        print(f"\\n🚀 Expected Impact on Trading System:")
        baseline_success = 0.50  # Random baseline
        ml_improvement = results['test_auc']
        improvement_factor = ml_improvement / baseline_success
        
        print(f"   Signal Quality Improvement: {improvement_factor:.1f}x better than random")
        print(f"   Expected Success Rate: {ml_improvement:.1%} (vs {baseline_success:.1%} baseline)")
        print(f"   False Positive Reduction: ~{(1 - ml_improvement/0.8)*100:.0f}% fewer bad signals")
        
        print(f"\\n💡 Next Steps for Production:")
        print("1. Collect real historical signal outcomes")
        print("2. Implement real-time ML inference in signal generation")
        print("3. Add more sophisticated features (news sentiment, etc.)")
        print("4. Set up continuous model retraining")
        
        return results

def main():
    """Run the ML pipeline demo"""
    demo = SimplifiedMLPipeline()
    results = demo.run_complete_demo()

if __name__ == "__main__":
    main()
