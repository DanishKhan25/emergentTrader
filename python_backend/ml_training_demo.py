#!/usr/bin/env python3
"""
ML Training Demo for EmergentTrader
Simplified demo showing how ML training would work
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score
import joblib
import os

def create_synthetic_training_data():
    """Create synthetic training data to demonstrate ML training"""
    print("📊 Creating synthetic training data for ML demo...")
    
    np.random.seed(42)
    n_samples = 5000
    
    # Simulate historical signals with features
    data = []
    
    for i in range(n_samples):
        # Strategy types
        strategies = ['momentum', 'low_volatility', 'fundamental_growth', 'breakout', 'value_investing']
        strategy = np.random.choice(strategies)
        
        # Market regimes
        market_regime = np.random.choice(['BULL', 'BEAR', 'SIDEWAYS'], p=[0.3, 0.2, 0.5])
        
        # Features
        confidence = np.random.uniform(0.3, 0.9)
        volatility = np.random.uniform(0.1, 0.4)
        rsi = np.random.uniform(20, 80)
        pe_ratio = np.random.uniform(5, 50)
        roe = np.random.uniform(-10, 40)
        
        # Market context
        market_trend = 1 if market_regime == 'BULL' else 0
        sector_momentum = np.random.uniform(-0.1, 0.1)
        
        # Strategy-specific success probabilities
        base_success_prob = {
            'momentum': 0.45,
            'low_volatility': 0.55,
            'fundamental_growth': 0.50,
            'breakout': 0.40,
            'value_investing': 0.48
        }[strategy]
        
        # Adjust success probability based on features
        success_prob = base_success_prob
        
        # Market regime impact
        if market_regime == 'BULL':
            if strategy in ['momentum', 'breakout']:
                success_prob += 0.15
            elif strategy == 'low_volatility':
                success_prob -= 0.05
        elif market_regime == 'BEAR':
            if strategy in ['low_volatility', 'value_investing']:
                success_prob += 0.10
            elif strategy in ['momentum', 'breakout']:
                success_prob -= 0.15
        
        # Confidence impact
        success_prob += (confidence - 0.6) * 0.3
        
        # Volatility impact (lower volatility generally better)
        success_prob += (0.25 - volatility) * 0.2
        
        # RSI impact
        if 30 <= rsi <= 70:  # Neutral RSI is better
            success_prob += 0.05
        
        # Fundamental impact
        if roe > 15:
            success_prob += 0.05
        if 10 <= pe_ratio <= 25:
            success_prob += 0.05
        
        # Ensure probability is between 0 and 1
        success_prob = max(0.1, min(0.9, success_prob))
        
        # Generate outcome
        success = 1 if np.random.random() < success_prob else 0
        return_pct = np.random.normal(0.03 if success else -0.02, 0.05)
        
        sample = {
            'strategy': strategy,
            'confidence': confidence,
            'volatility': volatility,
            'rsi': rsi,
            'pe_ratio': pe_ratio,
            'roe': roe,
            'market_regime': market_regime,
            'market_trend': market_trend,
            'sector_momentum': sector_momentum,
            'success': success,
            'return_pct': return_pct
        }
        
        data.append(sample)
    
    df = pd.DataFrame(data)
    print(f"Generated {len(df)} training samples")
    print(f"Overall success rate: {df['success'].mean():.2%}")
    print(f"Success rate by strategy:")
    print(df.groupby('strategy')['success'].mean().sort_values(ascending=False))
    
    return df

def train_signal_quality_model(training_data):
    """Train ML model to predict signal success"""
    print("\\n🤖 Training Signal Quality Model...")
    
    # Prepare features
    # Convert categorical variables to dummy variables
    df = training_data.copy()
    df = pd.get_dummies(df, columns=['strategy', 'market_regime'], prefix=['strat', 'regime'])
    
    # Feature columns
    feature_columns = [col for col in df.columns if col not in ['success', 'return_pct']]
    
    X = df[feature_columns]
    y = df['success']
    
    print(f"Features: {len(feature_columns)}")
    print(f"Training samples: {len(X)}")
    
    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Train model
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=15,
        min_samples_split=10,
        min_samples_leaf=5,
        random_state=42
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate
    train_pred = model.predict_proba(X_train)[:, 1]
    test_pred = model.predict_proba(X_test)[:, 1]
    
    train_auc = roc_auc_score(y_train, train_pred)
    test_auc = roc_auc_score(y_test, test_pred)
    
    print(f"Training AUC: {train_auc:.4f}")
    print(f"Test AUC: {test_auc:.4f}")
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': feature_columns,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print("\\nTop 10 Most Important Features:")
    print(feature_importance.head(10))
    
    # Classification report
    test_pred_binary = (test_pred > 0.5).astype(int)
    print("\\nClassification Report:")
    print(classification_report(y_test, test_pred_binary))
    
    return model, feature_columns, test_auc

def demonstrate_ml_predictions(model, feature_columns):
    """Demonstrate how ML model would enhance signals"""
    print("\\n🎯 ML Signal Enhancement Demo")
    print("=" * 50)
    
    # Simulate current signals
    current_signals = [
        {
            'symbol': 'TCS',
            'strategy': 'low_volatility',
            'confidence': 0.7,
            'volatility': 0.18,
            'rsi': 45,
            'pe_ratio': 22,
            'roe': 25,
            'market_regime': 'SIDEWAYS'
        },
        {
            'symbol': 'RELIANCE',
            'strategy': 'momentum',
            'confidence': 0.6,
            'volatility': 0.25,
            'rsi': 65,
            'pe_ratio': 15,
            'roe': 12,
            'market_regime': 'BULL'
        },
        {
            'symbol': 'INFY',
            'strategy': 'fundamental_growth',
            'confidence': 0.8,
            'volatility': 0.20,
            'rsi': 55,
            'pe_ratio': 18,
            'roe': 28,
            'market_regime': 'BULL'
        }
    ]
    
    print("Original vs ML-Enhanced Signals:")
    print("-" * 50)
    
    for signal in current_signals:
        # Prepare features for ML model
        features_dict = {
            'confidence': signal['confidence'],
            'volatility': signal['volatility'],
            'rsi': signal['rsi'],
            'pe_ratio': signal['pe_ratio'],
            'roe': signal['roe'],
            'market_trend': 1 if signal['market_regime'] == 'BULL' else 0,
            'sector_momentum': 0.02,  # Default value
        }
        
        # Add strategy dummies
        strategies = ['momentum', 'low_volatility', 'fundamental_growth', 'breakout', 'value_investing']
        for strat in strategies:
            features_dict[f'strat_{strat}'] = 1 if signal['strategy'] == strat else 0
        
        # Add regime dummies
        regimes = ['BULL', 'BEAR', 'SIDEWAYS']
        for regime in regimes:
            features_dict[f'regime_{regime}'] = 1 if signal['market_regime'] == regime else 0
        
        # Create feature vector
        feature_vector = []
        for col in feature_columns:
            feature_vector.append(features_dict.get(col, 0))
        
        # ML prediction
        ml_probability = model.predict_proba([feature_vector])[0][1]
        ml_recommendation = "STRONG_BUY" if ml_probability > 0.7 else "BUY" if ml_probability > 0.5 else "SKIP"
        
        print(f"\\n{signal['symbol']} ({signal['strategy']}):")
        print(f"  Original Confidence: {signal['confidence']:.1%}")
        print(f"  ML Success Probability: {ml_probability:.1%}")
        print(f"  ML Recommendation: {ml_recommendation}")
        
        # Show improvement
        improvement = "📈 UPGRADE" if ml_probability > signal['confidence'] else "📉 DOWNGRADE" if ml_probability < signal['confidence'] else "➡️ SAME"
        print(f"  ML vs Original: {improvement}")

def save_demo_model(model, feature_columns):
    """Save the demo model"""
    print("\\n💾 Saving ML model...")
    
    os.makedirs('models', exist_ok=True)
    
    model_data = {
        'model': model,
        'feature_columns': feature_columns,
        'model_type': 'signal_quality_classifier',
        'version': '1.0_demo'
    }
    
    joblib.dump(model_data, 'models/signal_quality_demo.pkl')
    print("Model saved to 'models/signal_quality_demo.pkl'")

def main():
    """Run ML training demonstration"""
    print("🧠 EmergentTrader ML Training Demonstration")
    print("=" * 60)
    
    # Step 1: Create training data
    training_data = create_synthetic_training_data()
    
    # Step 2: Train model
    model, feature_columns, test_auc = train_signal_quality_model(training_data)
    
    # Step 3: Demonstrate predictions
    demonstrate_ml_predictions(model, feature_columns)
    
    # Step 4: Save model
    save_demo_model(model, feature_columns)
    
    print("\\n" + "=" * 60)
    print("✅ ML Training Demo Complete!")
    print(f"🎯 Model Performance: {test_auc:.1%} AUC Score")
    print("\\n🚀 Next Steps for Real Implementation:")
    print("1. Collect real historical signal outcomes")
    print("2. Add more sophisticated features (news sentiment, etc.)")
    print("3. Implement ensemble models (XGBoost + Neural Networks)")
    print("4. Add real-time inference to signal generation")
    print("5. Implement continuous model retraining")
    
    return model, feature_columns, test_auc

if __name__ == "__main__":
    main()
