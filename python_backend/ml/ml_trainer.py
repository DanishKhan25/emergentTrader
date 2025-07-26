#!/usr/bin/env python3
"""
ML Training System for EmergentTrader
Train and improve ML models using historical signal outcomes
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
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, roc_curve
import seaborn as sns

# Add the python_backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.signal_database import SignalDatabase
from services.yfinance_fetcher import YFinanceFetcher

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MLTrainer:
    """
    ML Training System for Signal Quality Prediction
    
    Features:
    1. Historical data collection
    2. Feature engineering
    3. Model training and validation
    4. Performance evaluation
    5. Model improvement
    """
    
    def __init__(self):
        self.signal_db = SignalDatabase()
        self.data_fetcher = YFinanceFetcher()
        self.models = {}
        self.scalers = {}
        self.feature_columns = []
        self.training_data = None
        self.model_performance = {}
        
        # Define feature columns
        self.feature_columns = [
            'confidence', 'strategy_encoded', 'entry_price_normalized',
            'market_volatility', 'market_momentum', 'bull_market', 'bear_market',
            'rsi', 'macd', 'volume_ratio', 'price_momentum_20d', 'volatility',
            'month', 'quarter', 'is_earnings_season',
            'confidence_x_momentum', 'volatility_x_momentum', 'rsi_x_confidence',
            'high_confidence', 'positive_momentum', 'low_volatility_market',
            'high_volume', 'rsi_oversold', 'rsi_overbought',
            'days_since_signal', 'sector_performance', 'market_cap_category'
        ]
        
        logger.info("ML Trainer initialized")
    
    def collect_historical_data(self, days_back: int = 90) -> pd.DataFrame:
        """
        Collect historical signals and their outcomes
        
        Args:
            days_back: Number of days to look back for signals
            
        Returns:
            DataFrame with signals and their outcomes
        """
        try:
            logger.info(f"Collecting historical signals from last {days_back} days...")
            
            # Get historical signals from database
            cutoff_date = datetime.now() - timedelta(days=days_back)
            
            # This would be implemented in your signal database
            # For now, let's simulate historical data collection
            historical_signals = self._simulate_historical_signals(days_back)
            
            logger.info(f"Collected {len(historical_signals)} historical signals")
            return historical_signals
            
        except Exception as e:
            logger.error(f"Error collecting historical data: {str(e)}")
            return pd.DataFrame()
    
    def _simulate_historical_signals(self, days_back: int) -> pd.DataFrame:
        """Simulate historical signals for training (replace with real data)"""
        
        np.random.seed(42)
        n_signals = min(1000, days_back * 5)  # ~5 signals per day
        
        signals = []
        
        for i in range(n_signals):
            # Generate realistic historical signal
            signal_date = datetime.now() - timedelta(days=np.random.randint(1, days_back))
            
            signal = {
                'signal_id': f'hist_{i}',
                'symbol': np.random.choice(['TCS', 'RELIANCE', 'HDFC', 'INFY', 'WIPRO', 'ITC', 'HDFCBANK', 'ICICIBANK', 'SBIN', 'LT']),
                'strategy': np.random.choice(['momentum', 'low_volatility', 'fundamental_growth', 'mean_reversion', 'breakout']),
                'signal_type': np.random.choice(['BUY', 'SELL'], p=[0.7, 0.3]),
                'confidence': np.random.beta(2, 2) * 0.7 + 0.3,
                'entry_price': np.random.lognormal(7, 0.5),
                'generated_at': signal_date,
                
                # Technical indicators
                'rsi': np.random.beta(2, 2) * 60 + 20,
                'macd': np.random.normal(0, 0.02),
                'volume_ratio': np.random.gamma(2, 0.5) + 0.5,
                'volatility': np.random.gamma(2, 0.08) + 0.12,
                'price_momentum_20d': np.random.normal(0, 0.08),
                
                # Market context
                'market_volatility': np.random.gamma(2, 0.1),
                'market_momentum': np.random.normal(0, 0.05),
                'bull_market': np.random.choice([0, 1], p=[0.6, 0.4]),
                'bear_market': np.random.choice([0, 1], p=[0.7, 0.3]),
            }
            
            # Calculate outcome based on realistic factors
            signal['outcome'] = self._calculate_signal_outcome(signal)
            
            signals.append(signal)
        
        return pd.DataFrame(signals)
    
    def _calculate_signal_outcome(self, signal: Dict) -> int:
        """Calculate realistic signal outcome (1=success, 0=failure)"""
        
        # Base success probability
        success_prob = 0.4
        
        # Confidence boost
        success_prob += signal['confidence'] * 0.3
        
        # Strategy-specific adjustments
        strategy_multipliers = {
            'momentum': 1.1,
            'low_volatility': 1.2,
            'fundamental_growth': 1.0,
            'mean_reversion': 0.9,
            'breakout': 0.8
        }
        success_prob *= strategy_multipliers.get(signal['strategy'], 1.0)
        
        # Market conditions
        if signal['bull_market']:
            success_prob += 0.15
        if signal['bear_market']:
            success_prob -= 0.1
        
        # Technical indicators
        if 30 < signal['rsi'] < 70:
            success_prob += 0.1
        if signal['volume_ratio'] > 1.2:
            success_prob += 0.05
        if abs(signal['price_momentum_20d']) > 0.05:
            success_prob += 0.05
        
        # Volatility penalty
        if signal['volatility'] > 0.3:
            success_prob -= 0.1
        
        # Add noise
        success_prob += np.random.normal(0, 0.1)
        
        # Clip and convert to binary
        success_prob = np.clip(success_prob, 0.05, 0.95)
        return 1 if np.random.random() < success_prob else 0
    
    def engineer_features(self, signals_df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Engineer features from historical signals
        
        Args:
            signals_df: DataFrame with historical signals
            
        Returns:
            Feature matrix X and target vector y
        """
        try:
            logger.info("Engineering features from historical signals...")
            
            n_signals = len(signals_df)
            X = np.zeros((n_signals, len(self.feature_columns)))
            y = signals_df['outcome'].values
            
            for i, (_, signal) in enumerate(signals_df.iterrows()):
                features = self._extract_features_from_signal(signal)
                X[i] = [features.get(col, 0) for col in self.feature_columns]
            
            logger.info(f"Engineered {X.shape[1]} features for {X.shape[0]} signals")
            return X, y
            
        except Exception as e:
            logger.error(f"Error engineering features: {str(e)}")
            return np.array([]), np.array([])
    
    def _extract_features_from_signal(self, signal: pd.Series) -> Dict:
        """Extract features from a single historical signal"""
        
        # Strategy encoding
        strategy_mapping = {
            'momentum': 0, 'low_volatility': 1, 'fundamental_growth': 2,
            'mean_reversion': 3, 'breakout': 4, 'value_investing': 5,
            'swing_trading': 6, 'multibagger': 7, 'sector_rotation': 8, 'pivot_cpr': 9
        }
        
        # Time features
        signal_date = pd.to_datetime(signal['generated_at'])
        days_since_signal = (datetime.now() - signal_date).days
        
        # Market cap category (simulate)
        market_cap_category = np.random.choice([0, 1, 2])  # 0=small, 1=mid, 2=large
        
        # Sector performance (simulate)
        sector_performance = np.random.normal(0, 0.05)
        
        features = {
            'confidence': signal['confidence'],
            'strategy_encoded': strategy_mapping.get(signal['strategy'], 0),
            'entry_price_normalized': np.log(signal['entry_price']),
            'market_volatility': signal['market_volatility'],
            'market_momentum': signal['market_momentum'],
            'bull_market': signal['bull_market'],
            'bear_market': signal['bear_market'],
            'rsi': signal['rsi'],
            'macd': signal['macd'],
            'volume_ratio': signal['volume_ratio'],
            'price_momentum_20d': signal['price_momentum_20d'],
            'volatility': signal['volatility'],
            'month': signal_date.month,
            'quarter': (signal_date.month - 1) // 3 + 1,
            'is_earnings_season': 1 if signal_date.month in [1, 4, 7, 10] else 0,
            'confidence_x_momentum': signal['confidence'] * signal['price_momentum_20d'],
            'volatility_x_momentum': signal['volatility'] * signal['price_momentum_20d'],
            'rsi_x_confidence': signal['rsi'] * signal['confidence'] / 100,
            'high_confidence': 1 if signal['confidence'] > 0.7 else 0,
            'positive_momentum': 1 if signal['price_momentum_20d'] > 0 else 0,
            'low_volatility_market': 1 if signal['market_volatility'] < 0.2 else 0,
            'high_volume': 1 if signal['volume_ratio'] > 1.5 else 0,
            'rsi_oversold': 1 if signal['rsi'] < 30 else 0,
            'rsi_overbought': 1 if signal['rsi'] > 70 else 0,
            'days_since_signal': days_since_signal,
            'sector_performance': sector_performance,
            'market_cap_category': market_cap_category,
        }
        
        return features
    
    def train_models(self, X: np.ndarray, y: np.ndarray) -> Dict:
        """
        Train multiple ML models and select the best ones
        
        Args:
            X: Feature matrix
            y: Target vector
            
        Returns:
            Dictionary with trained models and performance metrics
        """
        try:
            logger.info("Training ML models...")
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Define models to train
            models_to_train = {
                'random_forest': RandomForestClassifier(n_estimators=100, random_state=42),
                'gradient_boost': GradientBoostingClassifier(n_estimators=100, random_state=42),
                'logistic': LogisticRegression(random_state=42, max_iter=1000),
                'svm': SVC(probability=True, random_state=42),
                'neural_net': MLPClassifier(hidden_layer_sizes=(100, 50), random_state=42, max_iter=500)
            }
            
            trained_models = {}
            scalers = {}
            performance = {}
            
            for name, model in models_to_train.items():
                logger.info(f"Training {name}...")
                
                # Scale features for models that need it
                if name in ['logistic', 'svm', 'neural_net']:
                    scaler = StandardScaler()
                    X_train_scaled = scaler.fit_transform(X_train)
                    X_test_scaled = scaler.transform(X_test)
                    scalers[name] = scaler
                else:
                    X_train_scaled = X_train
                    X_test_scaled = X_test
                
                # Train model
                model.fit(X_train_scaled, y_train)
                
                # Evaluate
                train_score = model.score(X_train_scaled, y_train)
                test_score = model.score(X_test_scaled, y_test)
                
                # Cross-validation
                cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5)
                
                # ROC AUC
                y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]
                auc_score = roc_auc_score(y_test, y_pred_proba)
                
                trained_models[name] = model
                performance[name] = {
                    'train_accuracy': train_score,
                    'test_accuracy': test_score,
                    'cv_mean': cv_scores.mean(),
                    'cv_std': cv_scores.std(),
                    'auc_score': auc_score
                }
                
                logger.info(f"{name}: Test Accuracy={test_score:.3f}, AUC={auc_score:.3f}")
            
            self.models = trained_models
            self.scalers = scalers
            self.model_performance = performance
            
            # Create ensemble
            self._create_ensemble(X_test, y_test)
            
            logger.info("Model training completed successfully")
            return performance
            
        except Exception as e:
            logger.error(f"Error training models: {str(e)}")
            return {}
    
    def _create_ensemble(self, X_test: np.ndarray, y_test: np.ndarray):
        """Create ensemble model from trained models"""
        try:
            logger.info("Creating ensemble model...")
            
            # Get predictions from all models
            ensemble_predictions = []
            model_weights = []
            
            for name, model in self.models.items():
                if name in self.scalers:
                    X_test_scaled = self.scalers[name].transform(X_test)
                else:
                    X_test_scaled = X_test
                
                pred_proba = model.predict_proba(X_test_scaled)[:, 1]
                ensemble_predictions.append(pred_proba)
                
                # Weight by AUC score
                weight = self.model_performance[name]['auc_score']
                model_weights.append(weight)
            
            # Calculate ensemble prediction
            ensemble_predictions = np.array(ensemble_predictions)
            model_weights = np.array(model_weights)
            model_weights = model_weights / model_weights.sum()  # Normalize
            
            ensemble_pred = np.average(ensemble_predictions, axis=0, weights=model_weights)
            ensemble_auc = roc_auc_score(y_test, ensemble_pred)
            
            # Store ensemble info
            self.ensemble_weights = dict(zip(self.models.keys(), model_weights))
            self.model_performance['ensemble'] = {
                'auc_score': ensemble_auc,
                'component_models': list(self.models.keys()),
                'weights': model_weights.tolist()
            }
            
            logger.info(f"Ensemble created with AUC: {ensemble_auc:.3f}")
            
        except Exception as e:
            logger.error(f"Error creating ensemble: {str(e)}")
    
    def hyperparameter_tuning(self, X: np.ndarray, y: np.ndarray, model_name: str = 'random_forest'):
        """
        Perform hyperparameter tuning for a specific model
        
        Args:
            X: Feature matrix
            y: Target vector
            model_name: Name of model to tune
        """
        try:
            logger.info(f"Performing hyperparameter tuning for {model_name}...")
            
            # Define parameter grids
            param_grids = {
                'random_forest': {
                    'n_estimators': [50, 100, 200],
                    'max_depth': [10, 20, None],
                    'min_samples_split': [2, 5, 10],
                    'min_samples_leaf': [1, 2, 4]
                },
                'gradient_boost': {
                    'n_estimators': [50, 100, 200],
                    'learning_rate': [0.01, 0.1, 0.2],
                    'max_depth': [3, 5, 7],
                    'subsample': [0.8, 0.9, 1.0]
                },
                'logistic': {
                    'C': [0.1, 1, 10, 100],
                    'penalty': ['l1', 'l2'],
                    'solver': ['liblinear', 'saga']
                }
            }
            
            if model_name not in param_grids:
                logger.warning(f"No parameter grid defined for {model_name}")
                return
            
            # Get base model
            base_models = {
                'random_forest': RandomForestClassifier(random_state=42),
                'gradient_boost': GradientBoostingClassifier(random_state=42),
                'logistic': LogisticRegression(random_state=42, max_iter=1000)
            }
            
            model = base_models[model_name]
            param_grid = param_grids[model_name]
            
            # Prepare data
            if model_name == 'logistic':
                scaler = StandardScaler()
                X_scaled = scaler.fit_transform(X)
            else:
                X_scaled = X
            
            # Grid search
            grid_search = GridSearchCV(
                model, param_grid, cv=5, scoring='roc_auc', n_jobs=-1, verbose=1
            )
            
            grid_search.fit(X_scaled, y)
            
            # Update model with best parameters
            best_model = grid_search.best_estimator_
            self.models[model_name] = best_model
            
            if model_name == 'logistic':
                self.scalers[model_name] = scaler
            
            logger.info(f"Best parameters for {model_name}: {grid_search.best_params_}")
            logger.info(f"Best CV score: {grid_search.best_score_:.3f}")
            
        except Exception as e:
            logger.error(f"Error in hyperparameter tuning: {str(e)}")
    
    def evaluate_models(self, X_test: np.ndarray, y_test: np.ndarray) -> Dict:
        """
        Comprehensive model evaluation
        
        Args:
            X_test: Test feature matrix
            y_test: Test target vector
            
        Returns:
            Evaluation results
        """
        try:
            logger.info("Evaluating trained models...")
            
            evaluation_results = {}
            
            for name, model in self.models.items():
                # Prepare test data
                if name in self.scalers:
                    X_test_scaled = self.scalers[name].transform(X_test)
                else:
                    X_test_scaled = X_test
                
                # Predictions
                y_pred = model.predict(X_test_scaled)
                y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]
                
                # Metrics
                accuracy = model.score(X_test_scaled, y_test)
                auc_score = roc_auc_score(y_test, y_pred_proba)
                
                # Classification report
                class_report = classification_report(y_test, y_pred, output_dict=True)
                
                evaluation_results[name] = {
                    'accuracy': accuracy,
                    'auc_score': auc_score,
                    'precision': class_report['1']['precision'],
                    'recall': class_report['1']['recall'],
                    'f1_score': class_report['1']['f1-score'],
                    'classification_report': class_report
                }
                
                logger.info(f"{name}: Accuracy={accuracy:.3f}, AUC={auc_score:.3f}, F1={class_report['1']['f1-score']:.3f}")
            
            return evaluation_results
            
        except Exception as e:
            logger.error(f"Error evaluating models: {str(e)}")
            return {}
    
    def save_models(self, filepath: str = None):
        """
        Save trained models to file
        
        Args:
            filepath: Path to save models (optional)
        """
        try:
            if filepath is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filepath = f'ml/models/trained_models_{timestamp}.pkl'
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            model_data = {
                'models': self.models,
                'scalers': self.scalers,
                'feature_columns': self.feature_columns,
                'model_performance': self.model_performance,
                'ensemble_weights': getattr(self, 'ensemble_weights', {}),
                'training_date': datetime.now().isoformat(),
                'version': '1.0'
            }
            
            joblib.dump(model_data, filepath)
            logger.info(f"Models saved to {filepath}")
            
        except Exception as e:
            logger.error(f"Error saving models: {str(e)}")
    
    def generate_training_report(self) -> str:
        """Generate comprehensive training report"""
        try:
            report = []
            report.append("="*60)
            report.append("ML TRAINING REPORT")
            report.append("="*60)
            report.append(f"Training Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report.append(f"Features Used: {len(self.feature_columns)}")
            report.append("")
            
            report.append("MODEL PERFORMANCE:")
            report.append("-" * 40)
            
            for name, perf in self.model_performance.items():
                if name == 'ensemble':
                    continue
                    
                report.append(f"{name.upper()}:")
                report.append(f"  Test Accuracy: {perf['test_accuracy']:.3f}")
                report.append(f"  AUC Score: {perf['auc_score']:.3f}")
                report.append(f"  CV Mean: {perf['cv_mean']:.3f} ± {perf['cv_std']:.3f}")
                report.append("")
            
            if 'ensemble' in self.model_performance:
                ens_perf = self.model_performance['ensemble']
                report.append("ENSEMBLE MODEL:")
                report.append(f"  AUC Score: {ens_perf['auc_score']:.3f}")
                report.append(f"  Component Models: {', '.join(ens_perf['component_models'])}")
                report.append("")
            
            report.append("FEATURE IMPORTANCE (Top 10):")
            report.append("-" * 40)
            
            # Get feature importance from Random Forest
            if 'random_forest' in self.models:
                rf_model = self.models['random_forest']
                feature_importance = list(zip(self.feature_columns, rf_model.feature_importances_))
                feature_importance.sort(key=lambda x: x[1], reverse=True)
                
                for i, (feature, importance) in enumerate(feature_importance[:10]):
                    report.append(f"  {i+1:2d}. {feature}: {importance:.4f}")
            
            report.append("")
            report.append("RECOMMENDATIONS:")
            report.append("-" * 40)
            
            best_model = max(self.model_performance.items(), 
                           key=lambda x: x[1].get('auc_score', 0) if x[0] != 'ensemble' else 0)
            
            report.append(f"• Best individual model: {best_model[0]} (AUC: {best_model[1]['auc_score']:.3f})")
            
            if 'ensemble' in self.model_performance:
                ens_auc = self.model_performance['ensemble']['auc_score']
                if ens_auc > best_model[1]['auc_score']:
                    report.append("• Recommend using ensemble model for best performance")
                else:
                    report.append(f"• Recommend using {best_model[0]} model")
            
            report.append("• Retrain models monthly with new signal outcomes")
            report.append("• Monitor model performance and retrain if AUC drops below 0.65")
            
            return "\n".join(report)
            
        except Exception as e:
            logger.error(f"Error generating training report: {str(e)}")
            return "Error generating report"

def main():
    """Main training execution"""
    print("🤖 ML Training System for EmergentTrader")
    print("=" * 50)
    
    # Initialize trainer
    trainer = MLTrainer()
    
    # Step 1: Collect historical data
    print("\n📊 Step 1: Collecting Historical Data...")
    historical_data = trainer.collect_historical_data(days_back=90)
    
    if historical_data.empty:
        print("❌ No historical data available")
        return
    
    print(f"✅ Collected {len(historical_data)} historical signals")
    
    # Step 2: Engineer features
    print("\n🔧 Step 2: Engineering Features...")
    X, y = trainer.engineer_features(historical_data)
    
    if len(X) == 0:
        print("❌ Feature engineering failed")
        return
    
    print(f"✅ Engineered {X.shape[1]} features for {X.shape[0]} signals")
    print(f"   Success rate in training data: {y.mean():.1%}")
    
    # Step 3: Train models
    print("\n🎯 Step 3: Training ML Models...")
    performance = trainer.train_models(X, y)
    
    if not performance:
        print("❌ Model training failed")
        return
    
    print("✅ Model training completed")
    
    # Step 4: Hyperparameter tuning (optional)
    print("\n⚙️  Step 4: Hyperparameter Tuning...")
    trainer.hyperparameter_tuning(X, y, 'random_forest')
    
    # Step 5: Final evaluation
    print("\n📈 Step 5: Model Evaluation...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    evaluation = trainer.evaluate_models(X_test, y_test)
    
    # Step 6: Save models
    print("\n💾 Step 6: Saving Models...")
    trainer.save_models()
    
    # Step 7: Generate report
    print("\n📋 Step 7: Generating Training Report...")
    report = trainer.generate_training_report()
    print(report)
    
    # Save report
    with open(f'ml/training_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt', 'w') as f:
        f.write(report)
    
    print("\n🎉 ML Training Complete!")
    print("   Models are ready for production use")
    print("   Check the training report for detailed results")

if __name__ == "__main__":
    main()
