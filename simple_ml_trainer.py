#!/usr/bin/env python3
"""
Simple ML Training Demo
Demonstrates how to train and improve ML models for signal quality prediction
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

# Add python_backend to path
sys.path.append('python_backend')

def main():
    """Demonstrate ML training and improvement process"""
    print("🤖" + "="*60 + "🤖")
    print("📊  ML TRAINING & IMPROVEMENT DEMONSTRATION  📊")
    print("🤖" + "="*60 + "🤖")
    print(f"Training Session: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        from ml.ml_trainer import MLTrainer
        from ml.ml_improvement_system import MLImprovementSystem
        
        print("\n🎯 STEP 1: INITIALIZE ML TRAINING SYSTEM")
        print("-" * 50)
        
        trainer = MLTrainer()
        improvement_system = MLImprovementSystem()
        
        print("✅ ML Trainer initialized")
        print(f"   Features to use: {len(trainer.feature_columns)}")
        print(f"   Feature examples: {trainer.feature_columns[:5]}")
        
        print("\n📊 STEP 2: COLLECT HISTORICAL DATA")
        print("-" * 50)
        
        # Simulate collecting historical signal data
        print("Collecting historical signals (simulated for demo)...")
        historical_data = trainer.collect_historical_data(days_back=90)
        
        print(f"✅ Collected {len(historical_data)} historical signals")
        print(f"   Success rate in data: {historical_data['outcome'].mean():.1%}")
        print(f"   Date range: {historical_data['generated_at'].min()} to {historical_data['generated_at'].max()}")
        
        # Show sample data
        print(f"\n   Sample signals:")
        for i, (_, signal) in enumerate(historical_data.head(3).iterrows()):
            outcome = "✅ Success" if signal['outcome'] else "❌ Failed"
            print(f"   {i+1}. {signal['symbol']} ({signal['strategy']}) - {outcome}")
            print(f"      Confidence: {signal['confidence']:.1%}, Return: {signal.get('return_pct', 0):.1%}")
        
        print("\n🔧 STEP 3: FEATURE ENGINEERING")
        print("-" * 50)
        
        print("Engineering features from historical signals...")
        X, y = trainer.engineer_features(historical_data)
        
        print(f"✅ Feature engineering completed")
        print(f"   Feature matrix shape: {X.shape}")
        print(f"   Target distribution: {y.sum()} successes, {len(y) - y.sum()} failures")
        print(f"   Success rate: {y.mean():.1%}")
        
        print("\n🎯 STEP 4: TRAIN ML MODELS")
        print("-" * 50)
        
        print("Training multiple ML models...")
        performance = trainer.train_models(X, y)
        
        print(f"✅ Model training completed")
        print(f"   Models trained: {len(performance)}")
        
        # Show performance results
        print(f"\n   📈 Model Performance Results:")
        for model_name, perf in performance.items():
            print(f"   {model_name.upper()}:")
            print(f"     Test Accuracy: {perf['test_accuracy']:.3f}")
            print(f"     AUC Score: {perf['auc_score']:.3f}")
            print(f"     CV Score: {perf['cv_mean']:.3f} ± {perf['cv_std']:.3f}")
        
        # Find best model
        best_model = max(performance.items(), key=lambda x: x[1]['auc_score'])
        print(f"\n   🏆 Best Model: {best_model[0]} (AUC: {best_model[1]['auc_score']:.3f})")
        
        print("\n⚙️  STEP 5: HYPERPARAMETER TUNING")
        print("-" * 50)
        
        print(f"Tuning hyperparameters for {best_model[0]}...")
        trainer.hyperparameter_tuning(X, y, best_model[0])
        print(f"✅ Hyperparameter tuning completed")
        
        print("\n📈 STEP 6: MODEL EVALUATION")
        print("-" * 50)
        
        from sklearn.model_selection import train_test_split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        evaluation = trainer.evaluate_models(X_test, y_test)
        
        print(f"✅ Model evaluation completed")
        print(f"\n   📊 Detailed Evaluation Results:")
        
        for model_name, eval_results in evaluation.items():
            print(f"   {model_name.upper()}:")
            print(f"     Accuracy: {eval_results['accuracy']:.3f}")
            print(f"     AUC Score: {eval_results['auc_score']:.3f}")
            print(f"     Precision: {eval_results['precision']:.3f}")
            print(f"     Recall: {eval_results['recall']:.3f}")
            print(f"     F1 Score: {eval_results['f1_score']:.3f}")
        
        print("\n💾 STEP 7: SAVE TRAINED MODELS")
        print("-" * 50)
        
        trainer.save_models()
        print(f"✅ Models saved successfully")
        
        print("\n📋 STEP 8: GENERATE TRAINING REPORT")
        print("-" * 50)
        
        report = trainer.generate_training_report()
        print(report)
        
        # Save report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = f'ml_training_report_{timestamp}.txt'
        with open(report_file, 'w') as f:
            f.write(report)
        print(f"\n💾 Training report saved to: {report_file}")
        
        print("\n🔄 STEP 9: CONTINUOUS IMPROVEMENT DEMO")
        print("-" * 50)
        
        print("Evaluating current performance...")
        current_performance = improvement_system.evaluate_current_performance()
        
        print(f"✅ Performance evaluation completed")
        print(f"   Overall Success Rate: {current_performance.get('overall_success_rate', 0):.1%}")
        print(f"   ML Prediction Accuracy: {current_performance.get('ml_prediction_accuracy', 0):.1%}")
        print(f"   Performance Grade: {current_performance.get('performance_grade', 'UNKNOWN')}")
        
        # Check if retraining is needed
        should_retrain, reason = improvement_system.should_retrain_models()
        print(f"\n   Retraining Analysis:")
        print(f"   Should Retrain: {should_retrain}")
        print(f"   Reason: {reason}")
        
        print("\n🔍 STEP 10: FEATURE IMPORTANCE ANALYSIS")
        print("-" * 50)
        
        # Set trainer models for analysis
        improvement_system.trainer = trainer
        feature_analysis = improvement_system.feature_importance_analysis()
        
        if 'top_features' in feature_analysis:
            print(f"✅ Feature importance analysis completed")
            print(f"\n   🏆 Top 10 Most Important Features:")
            
            for i, (feature, importance) in enumerate(feature_analysis['top_features'][:10]):
                print(f"   {i+1:2d}. {feature}: {importance:.4f}")
            
            if feature_analysis['recommendations']:
                print(f"\n   💡 Recommendations:")
                for rec in feature_analysis['recommendations']:
                    print(f"   • {rec}")
        
        print("\n🎯 STEP 11: IMPROVEMENT RECOMMENDATIONS")
        print("-" * 50)
        
        print("Based on training results, here are improvement recommendations:")
        print()
        
        # Performance-based recommendations
        best_auc = best_model[1]['auc_score']
        if best_auc > 0.8:
            print("✅ EXCELLENT: Your models are performing very well!")
            print("   • Deploy to production immediately")
            print("   • Set up monthly retraining schedule")
        elif best_auc > 0.7:
            print("✅ GOOD: Models are performing well")
            print("   • Consider adding more features")
            print("   • Set up bi-weekly retraining")
        elif best_auc > 0.6:
            print("⚠️  FAIR: Models need improvement")
            print("   • Collect more historical data")
            print("   • Add advanced features (sentiment, earnings, etc.)")
            print("   • Set up weekly retraining")
        else:
            print("❌ POOR: Models need significant improvement")
            print("   • Review feature engineering")
            print("   • Collect more diverse training data")
            print("   • Consider different algorithms")
        
        print(f"\n   📊 Data Quality Recommendations:")
        data_size = len(historical_data)
        if data_size < 500:
            print("   • Collect more historical signals (target: 1000+)")
        if historical_data['outcome'].mean() < 0.4:
            print("   • Review signal generation logic (low success rate)")
        if len(set(historical_data['strategy'])) < 3:
            print("   • Include more diverse strategies in training")
        
        print(f"\n   🔧 Technical Recommendations:")
        print("   • Implement real-time outcome tracking")
        print("   • Set up automated model monitoring")
        print("   • Add more market context features")
        print("   • Consider ensemble methods")
        print("   • Implement online learning for real-time adaptation")
        
        print("\n🚀 NEXT STEPS")
        print("=" * 50)
        
        print("1. 📊 IMMEDIATE (This Week):")
        print("   • Replace simulated data with real historical signals")
        print("   • Implement outcome tracking for new signals")
        print("   • Deploy trained models to production")
        
        print("\n2. 📈 SHORT-TERM (Next Month):")
        print("   • Set up continuous improvement system")
        print("   • Add advanced features (earnings, sentiment)")
        print("   • Implement automated retraining")
        
        print("\n3. 🎯 LONG-TERM (Next Quarter):")
        print("   • Develop online learning capabilities")
        print("   • Add alternative data sources")
        print("   • Implement advanced ensemble methods")
        
        print(f"\n🎉 ML TRAINING DEMONSTRATION COMPLETE!")
        print("=" * 60)
        print("Your ML system is ready for production training!")
        print("Follow the ML_TRAINING_GUIDE.md for detailed implementation steps.")
        
    except Exception as e:
        print(f"\n❌ Error in ML training demo: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
