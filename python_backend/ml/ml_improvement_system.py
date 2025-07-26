#!/usr/bin/env python3
"""
ML Continuous Improvement System
Automatically improve ML models based on real trading outcomes
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
from sklearn.metrics import roc_auc_score, accuracy_score
import schedule
import time

# Add the python_backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from ml.ml_trainer import MLTrainer
from core.signal_database import SignalDatabase
from services.yfinance_fetcher import YFinanceFetcher

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MLImprovementSystem:
    """
    Continuous ML Improvement System
    
    Features:
    1. Automatic outcome tracking
    2. Performance monitoring
    3. Automatic retraining
    4. A/B testing of models
    5. Feature importance analysis
    """
    
    def __init__(self):
        self.signal_db = SignalDatabase()
        self.data_fetcher = YFinanceFetcher()
        self.trainer = MLTrainer()
        self.current_models = {}
        self.performance_history = []
        self.improvement_log = []
        
        logger.info("ML Improvement System initialized")
    
    def track_signal_outcomes(self, days_back: int = 7) -> Dict:
        """
        Track outcomes of recent signals
        
        Args:
            days_back: Number of days to look back
            
        Returns:
            Dictionary with outcome statistics
        """
        try:
            logger.info(f"Tracking signal outcomes for last {days_back} days...")
            
            # Get recent signals from database
            cutoff_date = datetime.now() - timedelta(days=days_back)
            
            # This would query your actual signal database
            # For now, simulate outcome tracking
            outcomes = self._simulate_outcome_tracking(days_back)
            
            logger.info(f"Tracked outcomes for {len(outcomes)} signals")
            return outcomes
            
        except Exception as e:
            logger.error(f"Error tracking signal outcomes: {str(e)}")
            return {}
    
    def _simulate_outcome_tracking(self, days_back: int) -> Dict:
        """Simulate outcome tracking (replace with real implementation)"""
        
        # In production, this would:
        # 1. Get signals from database
        # 2. Check current prices vs entry prices
        # 3. Determine if targets/stops were hit
        # 4. Calculate actual returns
        
        outcomes = {
            'total_signals': np.random.randint(50, 200),
            'successful_signals': 0,
            'failed_signals': 0,
            'pending_signals': 0,
            'average_return': 0,
            'success_rate': 0,
            'by_strategy': {},
            'by_ml_confidence': {}
        }
        
        # Simulate outcomes
        total = outcomes['total_signals']
        success_rate = np.random.uniform(0.4, 0.7)  # 40-70% success rate
        
        outcomes['successful_signals'] = int(total * success_rate)
        outcomes['failed_signals'] = int(total * (1 - success_rate) * 0.8)
        outcomes['pending_signals'] = total - outcomes['successful_signals'] - outcomes['failed_signals']
        outcomes['success_rate'] = success_rate
        outcomes['average_return'] = np.random.uniform(0.02, 0.08)  # 2-8% average return
        
        # By strategy
        strategies = ['momentum', 'low_volatility', 'fundamental_growth', 'mean_reversion']
        for strategy in strategies:
            outcomes['by_strategy'][strategy] = {
                'signals': np.random.randint(5, 30),
                'success_rate': np.random.uniform(0.3, 0.8),
                'avg_return': np.random.uniform(0.01, 0.10)
            }
        
        # By ML confidence
        confidence_ranges = ['0.4-0.6', '0.6-0.8', '0.8-1.0']
        for range_str in confidence_ranges:
            outcomes['by_ml_confidence'][range_str] = {
                'signals': np.random.randint(10, 50),
                'success_rate': np.random.uniform(0.4, 0.9),
                'avg_return': np.random.uniform(0.02, 0.12)
            }
        
        return outcomes
    
    def evaluate_current_performance(self) -> Dict:
        """
        Evaluate current ML model performance
        
        Returns:
            Performance metrics
        """
        try:
            logger.info("Evaluating current ML model performance...")
            
            # Get recent outcomes
            outcomes = self.track_signal_outcomes(days_back=30)
            
            # Calculate ML model accuracy
            ml_accuracy = self._calculate_ml_accuracy(outcomes)
            
            # Performance metrics
            performance = {
                'overall_success_rate': outcomes.get('success_rate', 0),
                'ml_prediction_accuracy': ml_accuracy,
                'total_signals_evaluated': outcomes.get('total_signals', 0),
                'average_return': outcomes.get('average_return', 0),
                'evaluation_date': datetime.now().isoformat(),
                'performance_grade': self._grade_performance(ml_accuracy, outcomes.get('success_rate', 0))
            }
            
            # Store in history
            self.performance_history.append(performance)
            
            logger.info(f"Current performance: {ml_accuracy:.1%} ML accuracy, {outcomes.get('success_rate', 0):.1%} success rate")
            return performance
            
        except Exception as e:
            logger.error(f"Error evaluating performance: {str(e)}")
            return {}
    
    def _calculate_ml_accuracy(self, outcomes: Dict) -> float:
        """Calculate how accurate ML predictions were"""
        
        # In production, this would compare ML predictions to actual outcomes
        # For now, simulate based on confidence ranges
        
        total_weighted_accuracy = 0
        total_signals = 0
        
        for confidence_range, data in outcomes.get('by_ml_confidence', {}).items():
            signals = data['signals']
            success_rate = data['success_rate']
            
            # Higher confidence should correlate with higher success rate
            if confidence_range == '0.8-1.0':
                expected_success = 0.75
            elif confidence_range == '0.6-0.8':
                expected_success = 0.60
            else:
                expected_success = 0.45
            
            # Calculate accuracy as how close actual was to expected
            accuracy = 1 - abs(success_rate - expected_success) / expected_success
            accuracy = max(0, min(1, accuracy))  # Clip to [0, 1]
            
            total_weighted_accuracy += accuracy * signals
            total_signals += signals
        
        return total_weighted_accuracy / total_signals if total_signals > 0 else 0.5
    
    def _grade_performance(self, ml_accuracy: float, success_rate: float) -> str:
        """Grade overall performance"""
        
        combined_score = (ml_accuracy + success_rate) / 2
        
        if combined_score >= 0.8:
            return 'EXCELLENT'
        elif combined_score >= 0.7:
            return 'GOOD'
        elif combined_score >= 0.6:
            return 'FAIR'
        else:
            return 'NEEDS_IMPROVEMENT'
    
    def should_retrain_models(self) -> Tuple[bool, str]:
        """
        Determine if models should be retrained
        
        Returns:
            (should_retrain, reason)
        """
        try:
            # Get current performance
            current_perf = self.evaluate_current_performance()
            
            # Retrain conditions
            reasons = []
            
            # 1. Low ML accuracy
            ml_accuracy = current_perf.get('ml_prediction_accuracy', 0)
            if ml_accuracy < 0.6:
                reasons.append(f"Low ML accuracy: {ml_accuracy:.1%}")
            
            # 2. Low overall success rate
            success_rate = current_perf.get('overall_success_rate', 0)
            if success_rate < 0.5:
                reasons.append(f"Low success rate: {success_rate:.1%}")
            
            # 3. Performance degradation
            if len(self.performance_history) >= 2:
                prev_perf = self.performance_history[-2]
                current_ml = current_perf.get('ml_prediction_accuracy', 0)
                prev_ml = prev_perf.get('ml_prediction_accuracy', 0)
                
                if current_ml < prev_ml - 0.1:  # 10% drop
                    reasons.append(f"Performance degradation: {prev_ml:.1%} → {current_ml:.1%}")
            
            # 4. Time-based retraining (monthly)
            if len(self.performance_history) > 0:
                last_eval = datetime.fromisoformat(self.performance_history[-1]['evaluation_date'])
                if (datetime.now() - last_eval).days >= 30:
                    reasons.append("Monthly retraining schedule")
            
            # 5. Insufficient data for current models
            total_signals = current_perf.get('total_signals_evaluated', 0)
            if total_signals < 50:
                reasons.append(f"Insufficient recent data: {total_signals} signals")
            
            should_retrain = len(reasons) > 0
            reason = "; ".join(reasons) if reasons else "No retraining needed"
            
            logger.info(f"Retrain decision: {should_retrain} - {reason}")
            return should_retrain, reason
            
        except Exception as e:
            logger.error(f"Error determining retrain need: {str(e)}")
            return False, f"Error: {str(e)}"
    
    def automatic_retraining(self) -> Dict:
        """
        Perform automatic model retraining
        
        Returns:
            Retraining results
        """
        try:
            logger.info("Starting automatic model retraining...")
            
            # Collect more historical data
            historical_data = self.trainer.collect_historical_data(days_back=180)  # 6 months
            
            if historical_data.empty:
                return {'success': False, 'reason': 'No historical data available'}
            
            # Engineer features
            X, y = self.trainer.engineer_features(historical_data)
            
            if len(X) == 0:
                return {'success': False, 'reason': 'Feature engineering failed'}
            
            # Train new models
            performance = self.trainer.train_models(X, y)
            
            if not performance:
                return {'success': False, 'reason': 'Model training failed'}
            
            # Hyperparameter tuning for best model
            best_model = max(performance.items(), key=lambda x: x[1].get('auc_score', 0))
            self.trainer.hyperparameter_tuning(X, y, best_model[0])
            
            # Save new models
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            model_path = f'ml/models/retrained_models_{timestamp}.pkl'
            self.trainer.save_models(model_path)
            
            # Generate improvement report
            improvement_report = self._generate_improvement_report(performance)
            
            # Log improvement
            improvement_log = {
                'timestamp': datetime.now().isoformat(),
                'trigger': 'automatic_retraining',
                'data_points': len(X),
                'success_rate_in_training': y.mean(),
                'best_model': best_model[0],
                'best_auc': best_model[1]['auc_score'],
                'model_path': model_path,
                'report': improvement_report
            }
            
            self.improvement_log.append(improvement_log)
            
            logger.info(f"Retraining completed successfully. Best model: {best_model[0]} (AUC: {best_model[1]['auc_score']:.3f})")
            
            return {
                'success': True,
                'best_model': best_model[0],
                'best_auc': best_model[1]['auc_score'],
                'model_path': model_path,
                'training_data_points': len(X),
                'report': improvement_report
            }
            
        except Exception as e:
            logger.error(f"Error in automatic retraining: {str(e)}")
            return {'success': False, 'reason': str(e)}
    
    def _generate_improvement_report(self, performance: Dict) -> str:
        """Generate improvement report after retraining"""
        
        report = []
        report.append("ML MODEL IMPROVEMENT REPORT")
        report.append("=" * 40)
        report.append(f"Retraining Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Performance comparison
        if len(self.performance_history) > 0:
            prev_perf = self.performance_history[-1]
            report.append("PERFORMANCE COMPARISON:")
            report.append(f"Previous ML Accuracy: {prev_perf.get('ml_prediction_accuracy', 0):.1%}")
            report.append(f"Previous Success Rate: {prev_perf.get('overall_success_rate', 0):.1%}")
            report.append("")
        
        # New model performance
        report.append("NEW MODEL PERFORMANCE:")
        for model_name, perf in performance.items():
            if model_name != 'ensemble':
                report.append(f"{model_name}: AUC={perf['auc_score']:.3f}, Accuracy={perf['test_accuracy']:.3f}")
        
        report.append("")
        
        # Best model
        best_model = max(performance.items(), key=lambda x: x[1].get('auc_score', 0))
        report.append(f"RECOMMENDED MODEL: {best_model[0]}")
        report.append(f"Expected Improvement: {best_model[1]['auc_score']:.1%} AUC score")
        
        return "\n".join(report)
    
    def feature_importance_analysis(self) -> Dict:
        """
        Analyze feature importance and suggest improvements
        
        Returns:
            Feature analysis results
        """
        try:
            logger.info("Analyzing feature importance...")
            
            # Load current models
            if 'random_forest' in self.trainer.models:
                rf_model = self.trainer.models['random_forest']
                feature_importance = list(zip(self.trainer.feature_columns, rf_model.feature_importances_))
                feature_importance.sort(key=lambda x: x[1], reverse=True)
                
                # Analyze top features
                top_features = feature_importance[:10]
                low_importance_features = [f for f, imp in feature_importance if imp < 0.01]
                
                analysis = {
                    'top_features': top_features,
                    'low_importance_features': low_importance_features,
                    'feature_count': len(self.trainer.feature_columns),
                    'recommendations': self._generate_feature_recommendations(feature_importance)
                }
                
                logger.info(f"Feature analysis complete. Top feature: {top_features[0][0]} ({top_features[0][1]:.3f})")
                return analysis
            
            else:
                return {'error': 'No Random Forest model available for feature analysis'}
                
        except Exception as e:
            logger.error(f"Error in feature importance analysis: {str(e)}")
            return {'error': str(e)}
    
    def _generate_feature_recommendations(self, feature_importance: List[Tuple]) -> List[str]:
        """Generate recommendations based on feature importance"""
        
        recommendations = []
        
        # Check if confidence is top feature
        top_features = [f[0] for f in feature_importance[:5]]
        
        if 'confidence' in top_features:
            recommendations.append("Strategy confidence is highly predictive - ensure accurate confidence scoring")
        
        if 'rsi' in top_features:
            recommendations.append("RSI is important - consider adding more technical indicators")
        
        if 'market_volatility' in top_features:
            recommendations.append("Market conditions matter - enhance market regime detection")
        
        # Check for low importance features
        low_importance = [f[0] for f in feature_importance if f[1] < 0.01]
        
        if len(low_importance) > 5:
            recommendations.append(f"Consider removing {len(low_importance)} low-importance features to reduce noise")
        
        if 'volume_ratio' not in top_features:
            recommendations.append("Volume analysis may need improvement - consider volume-based features")
        
        return recommendations
    
    def schedule_improvements(self):
        """Schedule automatic improvements"""
        
        # Daily performance evaluation
        schedule.every().day.at("09:00").do(self.evaluate_current_performance)
        
        # Weekly retraining check
        schedule.every().week.do(self._weekly_improvement_check)
        
        # Monthly comprehensive retraining
        schedule.every().month.do(self._monthly_comprehensive_retraining)
        
        logger.info("Improvement schedule configured")
    
    def _weekly_improvement_check(self):
        """Weekly improvement check"""
        logger.info("Running weekly improvement check...")
        
        should_retrain, reason = self.should_retrain_models()
        
        if should_retrain:
            logger.info(f"Triggering retraining: {reason}")
            result = self.automatic_retraining()
            
            if result['success']:
                logger.info("Weekly retraining completed successfully")
            else:
                logger.error(f"Weekly retraining failed: {result['reason']}")
    
    def _monthly_comprehensive_retraining(self):
        """Monthly comprehensive retraining"""
        logger.info("Running monthly comprehensive retraining...")
        
        # Always retrain monthly regardless of performance
        result = self.automatic_retraining()
        
        if result['success']:
            # Also run feature analysis
            feature_analysis = self.feature_importance_analysis()
            
            # Generate comprehensive report
            report = self._generate_monthly_report(result, feature_analysis)
            
            # Save report
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            with open(f'ml/monthly_report_{timestamp}.txt', 'w') as f:
                f.write(report)
            
            logger.info("Monthly comprehensive retraining completed")
        else:
            logger.error(f"Monthly retraining failed: {result['reason']}")
    
    def _generate_monthly_report(self, retraining_result: Dict, feature_analysis: Dict) -> str:
        """Generate comprehensive monthly report"""
        
        report = []
        report.append("MONTHLY ML IMPROVEMENT REPORT")
        report.append("=" * 50)
        report.append(f"Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Performance history
        if len(self.performance_history) > 0:
            report.append("PERFORMANCE TREND (Last 4 weeks):")
            for perf in self.performance_history[-4:]:
                date = datetime.fromisoformat(perf['evaluation_date']).strftime('%Y-%m-%d')
                report.append(f"  {date}: {perf['ml_prediction_accuracy']:.1%} ML accuracy, {perf['overall_success_rate']:.1%} success rate")
            report.append("")
        
        # Retraining results
        report.append("RETRAINING RESULTS:")
        if retraining_result['success']:
            report.append(f"  ✅ Success - Best Model: {retraining_result['best_model']}")
            report.append(f"  📊 AUC Score: {retraining_result['best_auc']:.3f}")
            report.append(f"  📈 Training Data: {retraining_result['training_data_points']} signals")
        else:
            report.append(f"  ❌ Failed: {retraining_result['reason']}")
        
        report.append("")
        
        # Feature analysis
        if 'top_features' in feature_analysis:
            report.append("TOP PREDICTIVE FEATURES:")
            for i, (feature, importance) in enumerate(feature_analysis['top_features'][:5]):
                report.append(f"  {i+1}. {feature}: {importance:.4f}")
            report.append("")
            
            if feature_analysis['recommendations']:
                report.append("RECOMMENDATIONS:")
                for rec in feature_analysis['recommendations']:
                    report.append(f"  • {rec}")
        
        report.append("")
        report.append("NEXT STEPS:")
        report.append("  1. Deploy new models to production")
        report.append("  2. Monitor performance for next 7 days")
        report.append("  3. Implement feature recommendations")
        report.append("  4. Continue collecting signal outcomes")
        
        return "\n".join(report)
    
    def run_improvement_loop(self):
        """Run the continuous improvement loop"""
        logger.info("Starting ML improvement loop...")
        
        # Schedule improvements
        self.schedule_improvements()
        
        # Run initial evaluation
        self.evaluate_current_performance()
        
        # Main loop
        while True:
            schedule.run_pending()
            time.sleep(3600)  # Check every hour

def main():
    """Main improvement system execution"""
    print("🔄 ML Continuous Improvement System")
    print("=" * 50)
    
    # Initialize improvement system
    improvement_system = MLImprovementSystem()
    
    # Run initial evaluation
    print("\n📊 Initial Performance Evaluation...")
    performance = improvement_system.evaluate_current_performance()
    print(f"Current Performance Grade: {performance.get('performance_grade', 'UNKNOWN')}")
    
    # Check if retraining is needed
    print("\n🔍 Checking Retraining Requirements...")
    should_retrain, reason = improvement_system.should_retrain_models()
    print(f"Retrain Needed: {should_retrain}")
    print(f"Reason: {reason}")
    
    # Run retraining if needed
    if should_retrain:
        print("\n🎯 Running Automatic Retraining...")
        result = improvement_system.automatic_retraining()
        
        if result['success']:
            print(f"✅ Retraining successful!")
            print(f"   Best Model: {result['best_model']}")
            print(f"   AUC Score: {result['best_auc']:.3f}")
        else:
            print(f"❌ Retraining failed: {result['reason']}")
    
    # Feature analysis
    print("\n🔍 Feature Importance Analysis...")
    feature_analysis = improvement_system.feature_importance_analysis()
    
    if 'top_features' in feature_analysis:
        print("Top 5 Features:")
        for i, (feature, importance) in enumerate(feature_analysis['top_features'][:5]):
            print(f"   {i+1}. {feature}: {importance:.4f}")
        
        if feature_analysis['recommendations']:
            print("\nRecommendations:")
            for rec in feature_analysis['recommendations']:
                print(f"   • {rec}")
    
    print("\n🎉 ML Improvement System Ready!")
    print("   Run with continuous monitoring: improvement_system.run_improvement_loop()")

if __name__ == "__main__":
    main()
