#!/usr/bin/env python3
"""
Model Training System
Train ensemble models for signal quality prediction
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime
import pickle
import json
from typing import Dict, List, Optional, Tuple
import logging

# ML imports
from sklearn.model_selection import TimeSeriesSplit, cross_val_score, GridSearchCV
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import (classification_report, confusion_matrix, roc_auc_score, 
                           precision_recall_curve, mean_squared_error, r2_score)
from sklearn.preprocessing import StandardScaler
import xgboost as xgb
import joblib

# Add the python_backend directory to the path
try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
except NameError:
    parent_dir = os.getcwd()

sys.path.append(parent_dir)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelTrainer:
    """Train and evaluate ML models for trading signal prediction"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.feature_importance = {}
        self.model_performance = {}
        
        # Create directories
        os.makedirs('ml/models', exist_ok=True)
        os.makedirs('ml/results', exist_ok=True)
        
        logger.info("Model trainer initialized")
    
    def prepare_data(self, features_df: pd.DataFrame, target_column: str = 'target_success') -> Tuple:
        """Prepare data for training"""
        logger.info(f"Preparing data for target: {target_column}")
        
        # Separate features and target
        target_cols = [col for col in features_df.columns if col.startswith('target_')]
        feature_cols = [col for col in features_df.columns if col not in target_cols + 
                       ['symbol', 'entry_date', 'strategy', 'target_return_category']]
        
        X = features_df[feature_cols].copy()
        y = features_df[target_column].copy()
        
        # Handle missing values
        X = X.fillna(X.median())
        
        # Remove infinite values
        X = X.replace([np.inf, -np.inf], np.nan).fillna(X.median())
        
        # Time-based split (important for financial data)
        split_date = features_df['entry_date'].quantile(0.8)  # 80% for training
        train_mask = features_df['entry_date'] < split_date
        test_mask = features_df['entry_date'] >= split_date
        
        X_train, X_test = X[train_mask], X[test_mask]
        y_train, y_test = y[train_mask], y[test_mask]
        
        logger.info(f"Data prepared: {len(X_train)} train, {len(X_test)} test samples")
        logger.info(f"Features: {len(feature_cols)}")
        logger.info(f"Target distribution - Train: {y_train.mean():.3f}, Test: {y_test.mean():.3f}")
        
        return X_train, X_test, y_train, y_test, feature_cols
    
    def initialize_models(self) -> Dict:
        """Initialize ML models for training"""
        models = {
            'random_forest': RandomForestClassifier(
                n_estimators=200,
                max_depth=15,
                min_samples_split=10,
                min_samples_leaf=5,
                random_state=42,
                n_jobs=-1
            ),
            
            'xgboost': xgb.XGBClassifier(
                n_estimators=200,
                max_depth=8,
                learning_rate=0.1,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42,
                eval_metric='logloss'
            ),
            
            'gradient_boosting': GradientBoostingClassifier(
                n_estimators=200,
                max_depth=6,
                learning_rate=0.1,
                subsample=0.8,
                random_state=42
            ),
            
            'logistic_regression': LogisticRegression(
                random_state=42,
                max_iter=1000,
                C=1.0
            ),
            
            'neural_network': MLPClassifier(
                hidden_layer_sizes=(100, 50, 25),
                activation='relu',
                solver='adam',
                alpha=0.001,
                max_iter=500,
                random_state=42
            ),
            
            'svm': SVC(
                kernel='rbf',
                C=1.0,
                probability=True,
                random_state=42
            )
        }
        
        return models
    
    def train_single_model(self, model, model_name: str, X_train: pd.DataFrame, 
                          y_train: pd.Series, X_test: pd.DataFrame, y_test: pd.Series) -> Dict:
        """Train a single model and evaluate performance"""
        logger.info(f"Training {model_name}...")
        
        try:
            # Scale features for models that need it
            if model_name in ['logistic_regression', 'neural_network', 'svm']:
                scaler = StandardScaler()
                X_train_scaled = scaler.fit_transform(X_train)
                X_test_scaled = scaler.transform(X_test)
                self.scalers[model_name] = scaler
            else:
                X_train_scaled = X_train
                X_test_scaled = X_test
            
            # Train model
            model.fit(X_train_scaled, y_train)
            
            # Predictions
            train_pred = model.predict_proba(X_train_scaled)[:, 1]
            test_pred = model.predict_proba(X_test_scaled)[:, 1]
            
            train_pred_binary = (train_pred > 0.5).astype(int)
            test_pred_binary = (test_pred > 0.5).astype(int)
            
            # Performance metrics
            performance = {
                'model_name': model_name,
                'train_auc': roc_auc_score(y_train, train_pred),
                'test_auc': roc_auc_score(y_test, test_pred),
                'train_accuracy': (train_pred_binary == y_train).mean(),
                'test_accuracy': (test_pred_binary == y_test).mean(),
                'train_precision': ((train_pred_binary == 1) & (y_train == 1)).sum() / max((train_pred_binary == 1).sum(), 1),
                'test_precision': ((test_pred_binary == 1) & (y_test == 1)).sum() / max((test_pred_binary == 1).sum(), 1),
                'train_recall': ((train_pred_binary == 1) & (y_train == 1)).sum() / max((y_train == 1).sum(), 1),
                'test_recall': ((test_pred_binary == 1) & (y_test == 1)).sum() / max((y_test == 1).sum(), 1)
            }
            
            # Feature importance (if available)
            if hasattr(model, 'feature_importances_'):
                self.feature_importance[model_name] = model.feature_importances_
            elif hasattr(model, 'coef_'):
                self.feature_importance[model_name] = abs(model.coef_[0])
            
            # Cross-validation score
            cv_scores = cross_val_score(model, X_train_scaled, y_train, 
                                      cv=TimeSeriesSplit(n_splits=3), scoring='roc_auc')
            performance['cv_auc_mean'] = cv_scores.mean()
            performance['cv_auc_std'] = cv_scores.std()
            
            # Store model
            self.models[model_name] = model
            self.model_performance[model_name] = performance
            
            logger.info(f"{model_name} - Test AUC: {performance['test_auc']:.4f}, "
                       f"CV AUC: {performance['cv_auc_mean']:.4f} ± {performance['cv_auc_std']:.4f}")
            
            return performance
            
        except Exception as e:
            logger.error(f"Error training {model_name}: {str(e)}")
            return {'model_name': model_name, 'error': str(e)}
    
    def create_ensemble(self, X_train: pd.DataFrame, y_train: pd.Series, 
                       X_test: pd.DataFrame, y_test: pd.Series, 
                       feature_cols: List[str]) -> Dict:
        """Create ensemble model from trained models"""
        logger.info("Creating ensemble model...")
        
        # Get predictions from all models
        train_predictions = []
        test_predictions = []
        model_weights = []
        
        for model_name, model in self.models.items():
            if model_name in self.model_performance and 'error' not in self.model_performance[model_name]:
                # Get scaled features if needed
                if model_name in self.scalers:
                    X_train_scaled = self.scalers[model_name].transform(X_train)
                    X_test_scaled = self.scalers[model_name].transform(X_test)
                else:
                    X_train_scaled = X_train
                    X_test_scaled = X_test
                
                # Get predictions
                train_pred = model.predict_proba(X_train_scaled)[:, 1]
                test_pred = model.predict_proba(X_test_scaled)[:, 1]
                
                train_predictions.append(train_pred)
                test_predictions.append(test_pred)
                
                # Weight by test AUC performance
                weight = self.model_performance[model_name]['test_auc']
                model_weights.append(weight)
        
        if not train_predictions:
            logger.error("No valid models for ensemble")
            return {}
        
        # Normalize weights
        model_weights = np.array(model_weights)
        model_weights = model_weights / model_weights.sum()
        
        # Create weighted ensemble predictions
        ensemble_train_pred = np.average(train_predictions, axis=0, weights=model_weights)
        ensemble_test_pred = np.average(test_predictions, axis=0, weights=model_weights)
        
        # Evaluate ensemble
        ensemble_performance = {
            'model_name': 'ensemble',
            'train_auc': roc_auc_score(y_train, ensemble_train_pred),
            'test_auc': roc_auc_score(y_test, ensemble_test_pred),
            'train_accuracy': ((ensemble_train_pred > 0.5) == y_train).mean(),
            'test_accuracy': ((ensemble_test_pred > 0.5) == y_test).mean(),
            'model_weights': dict(zip(self.models.keys(), model_weights)),
            'component_models': list(self.models.keys())
        }
        
        # Store ensemble
        self.models['ensemble'] = {
            'type': 'ensemble',
            'component_models': self.models.copy(),
            'weights': model_weights,
            'scalers': self.scalers.copy(),
            'feature_columns': feature_cols
        }
        
        self.model_performance['ensemble'] = ensemble_performance
        
        logger.info(f"Ensemble created - Test AUC: {ensemble_performance['test_auc']:.4f}")
        
        return ensemble_performance
    
    def hyperparameter_tuning(self, model_name: str, X_train: pd.DataFrame, y_train: pd.Series) -> Dict:
        """Perform hyperparameter tuning for a specific model"""
        logger.info(f"Hyperparameter tuning for {model_name}...")
        
        param_grids = {
            'random_forest': {
                'n_estimators': [100, 200, 300],
                'max_depth': [10, 15, 20],
                'min_samples_split': [5, 10, 20],
                'min_samples_leaf': [2, 5, 10]
            },
            
            'xgboost': {
                'n_estimators': [100, 200, 300],
                'max_depth': [4, 6, 8],
                'learning_rate': [0.05, 0.1, 0.2],
                'subsample': [0.8, 0.9, 1.0]
            },
            
            'logistic_regression': {
                'C': [0.1, 1.0, 10.0],
                'penalty': ['l1', 'l2'],
                'solver': ['liblinear', 'saga']
            }
        }
        
        if model_name not in param_grids:
            logger.warning(f"No parameter grid defined for {model_name}")
            return {}
        
        try:
            # Initialize model
            models_init = self.initialize_models()
            base_model = models_init[model_name]
            
            # Scale features if needed
            if model_name in ['logistic_regression', 'neural_network', 'svm']:
                scaler = StandardScaler()
                X_train_scaled = scaler.fit_transform(X_train)
            else:
                X_train_scaled = X_train
            
            # Grid search with time series cross-validation
            grid_search = GridSearchCV(
                base_model,
                param_grids[model_name],
                cv=TimeSeriesSplit(n_splits=3),
                scoring='roc_auc',
                n_jobs=-1,
                verbose=1
            )
            
            grid_search.fit(X_train_scaled, y_train)
            
            tuning_results = {
                'best_params': grid_search.best_params_,
                'best_score': grid_search.best_score_,
                'best_model': grid_search.best_estimator_
            }
            
            logger.info(f"Best parameters for {model_name}: {grid_search.best_params_}")
            logger.info(f"Best CV score: {grid_search.best_score_:.4f}")
            
            return tuning_results
            
        except Exception as e:
            logger.error(f"Error in hyperparameter tuning for {model_name}: {str(e)}")
            return {}
    
    def analyze_feature_importance(self, feature_cols: List[str]) -> pd.DataFrame:
        """Analyze feature importance across models"""
        logger.info("Analyzing feature importance...")
        
        importance_data = []
        
        for model_name, importance_values in self.feature_importance.items():
            if len(importance_values) == len(feature_cols):
                for feature, importance in zip(feature_cols, importance_values):
                    importance_data.append({
                        'model': model_name,
                        'feature': feature,
                        'importance': importance
                    })
        
        if not importance_data:
            logger.warning("No feature importance data available")
            return pd.DataFrame()
        
        importance_df = pd.DataFrame(importance_data)
        
        # Aggregate importance across models
        avg_importance = importance_df.groupby('feature')['importance'].agg(['mean', 'std', 'count']).reset_index()
        avg_importance = avg_importance.sort_values('mean', ascending=False)
        
        logger.info(f"Feature importance analysis complete for {len(avg_importance)} features")
        
        return avg_importance
    
    def generate_model_report(self, feature_cols: List[str]) -> Dict:
        """Generate comprehensive model performance report"""
        logger.info("Generating model performance report...")
        
        report = {
            'training_summary': {
                'total_models_trained': len(self.models),
                'successful_models': len([p for p in self.model_performance.values() if 'error' not in p]),
                'failed_models': len([p for p in self.model_performance.values() if 'error' in p]),
                'training_timestamp': datetime.now().isoformat()
            },
            
            'model_performance': self.model_performance,
            
            'best_models': {
                'best_test_auc': max(self.model_performance.items(), 
                                   key=lambda x: x[1].get('test_auc', 0) if 'error' not in x[1] else 0),
                'best_cv_auc': max(self.model_performance.items(), 
                                 key=lambda x: x[1].get('cv_auc_mean', 0) if 'error' not in x[1] else 0),
                'most_stable': min(self.model_performance.items(), 
                                 key=lambda x: x[1].get('cv_auc_std', float('inf')) if 'error' not in x[1] else float('inf'))
            },
            
            'feature_analysis': self.analyze_feature_importance(feature_cols).to_dict('records'),
            
            'recommendations': self._generate_recommendations()
        }
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on model performance"""
        recommendations = []
        
        # Find best performing model
        valid_performances = {k: v for k, v in self.model_performance.items() if 'error' not in v}
        
        if valid_performances:
            best_model = max(valid_performances.items(), key=lambda x: x[1].get('test_auc', 0))
            recommendations.append(f"Best performing model: {best_model[0]} (AUC: {best_model[1]['test_auc']:.4f})")
            
            # Check for overfitting
            for model_name, perf in valid_performances.items():
                train_auc = perf.get('train_auc', 0)
                test_auc = perf.get('test_auc', 0)
                if train_auc - test_auc > 0.1:
                    recommendations.append(f"Warning: {model_name} may be overfitting (train AUC: {train_auc:.4f}, test AUC: {test_auc:.4f})")
            
            # Ensemble recommendation
            if 'ensemble' in valid_performances:
                ensemble_auc = valid_performances['ensemble']['test_auc']
                best_single_auc = max([v['test_auc'] for k, v in valid_performances.items() if k != 'ensemble'])
                if ensemble_auc > best_single_auc:
                    recommendations.append(f"Ensemble model outperforms individual models (AUC: {ensemble_auc:.4f} vs {best_single_auc:.4f})")
        
        return recommendations
    
    def save_models(self, filename_prefix: str = None):
        """Save trained models and results"""
        if filename_prefix is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename_prefix = f'ml_models_{timestamp}'
        
        # Save models
        models_file = f'ml/models/{filename_prefix}_models.pkl'
        joblib.dump({
            'models': self.models,
            'scalers': self.scalers,
            'feature_importance': self.feature_importance,
            'model_performance': self.model_performance
        }, models_file)
        
        logger.info(f"Models saved to {models_file}")
        
        # Save performance report
        report_file = f'ml/results/{filename_prefix}_report.json'
        with open(report_file, 'w') as f:
            json.dump(self.model_performance, f, indent=2, default=str)
        
        logger.info(f"Performance report saved to {report_file}")
        
        return models_file, report_file
    
    def train_models(self, features_df: pd.DataFrame, target_column: str = 'target_success') -> Dict:
        """Main training pipeline"""
        logger.info("Starting model training pipeline...")
        
        # Prepare data
        X_train, X_test, y_train, y_test, feature_cols = self.prepare_data(features_df, target_column)
        
        # Initialize models
        models = self.initialize_models()
        
        # Train individual models
        for model_name, model in models.items():
            self.train_single_model(model, model_name, X_train, y_train, X_test, y_test)
        
        # Create ensemble
        ensemble_performance = self.create_ensemble(X_train, y_train, X_test, y_test, feature_cols)
        
        # Generate report
        report = self.generate_model_report(feature_cols)
        
        # Save models
        models_file, report_file = self.save_models()
        
        logger.info("Model training pipeline complete")
        
        return {
            'report': report,
            'models_file': models_file,
            'report_file': report_file,
            'ensemble_performance': ensemble_performance
        }

def main():
    """Run model training on engineered features"""
    print("🤖 Starting Model Training for ML-Enhanced Trading Signals")
    print("=" * 70)
    
    # Find the latest features file
    features_files = [f for f in os.listdir('ml/features/') if f.startswith('engineered_features_') and f.endswith('.pkl')]
    
    if not features_files:
        print("❌ No features files found in ml/features/")
        print("Run feature_engineer.py first to generate features")
        return
    
    # Use the latest features file
    latest_file = sorted(features_files)[-1]
    features_file = f'ml/features/{latest_file}'
    
    try:
        features_df = pd.read_pickle(features_file)
        print(f"📊 Loaded {len(features_df)} samples with {len(features_df.columns)} features from {latest_file}")
        
        # Initialize trainer
        trainer = ModelTrainer()
        
        # Train models
        results = trainer.train_models(features_df, target_column='target_success')
        
        print(f"\n✅ Model Training Complete!")
        print(f"📊 Training Summary:")
        
        report = results['report']
        training_summary = report['training_summary']
        print(f"   Models trained: {training_summary['successful_models']}/{training_summary['total_models_trained']}")
        
        # Show best models
        best_models = report['best_models']
        print(f"\n🏆 Best Models:")
        print(f"   Best Test AUC: {best_models['best_test_auc'][0]} ({best_models['best_test_auc'][1]['test_auc']:.4f})")
        print(f"   Best CV AUC: {best_models['best_cv_auc'][0]} ({best_models['best_cv_auc'][1]['cv_auc_mean']:.4f})")
        
        # Show ensemble performance
        if 'ensemble_performance' in results:
            ensemble_perf = results['ensemble_performance']
            print(f"   Ensemble AUC: {ensemble_perf['test_auc']:.4f}")
        
        # Show top features
        feature_analysis = report['feature_analysis']
        if feature_analysis:
            print(f"\n📈 Top 10 Most Important Features:")
            for i, feature in enumerate(feature_analysis[:10], 1):
                print(f"   {i}. {feature['feature']}: {feature['mean']:.4f}")
        
        # Show recommendations
        recommendations = report['recommendations']
        if recommendations:
            print(f"\n💡 Recommendations:")
            for rec in recommendations:
                print(f"   • {rec}")
        
        print(f"\n💾 Results saved:")
        print(f"   Models: {results['models_file']}")
        print(f"   Report: {results['report_file']}")
        
        print(f"\n🎯 Next Steps:")
        print("1. Integrate best model into signal generation pipeline")
        print("2. Implement real-time ML inference")
        print("3. Set up model monitoring and retraining")
        print("4. Deploy ML-enhanced signal system to production")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()
