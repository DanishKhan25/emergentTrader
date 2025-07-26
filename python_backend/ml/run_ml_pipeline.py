#!/usr/bin/env python3
"""
Master ML Pipeline Script
Run the complete ML training pipeline for EmergentTrader
"""

import sys
import os
import time
from datetime import datetime
import logging

# Add the python_backend directory to the path
try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
except NameError:
    parent_dir = os.getcwd()

sys.path.append(parent_dir)

# Import pipeline components
from ml.historical_data_collector import HistoricalDataCollector
from ml.outcome_tracker import OutcomeTracker
from ml.feature_engineer import FeatureEngineer
from ml.model_trainer import ModelTrainer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MLPipeline:
    """Complete ML training pipeline for EmergentTrader"""
    
    def __init__(self, start_date='2020-01-01', end_date='2024-12-31'):
        self.start_date = start_date
        self.end_date = end_date
        self.pipeline_start_time = datetime.now()
        
        # Create directories
        os.makedirs('ml/data', exist_ok=True)
        os.makedirs('ml/features', exist_ok=True)
        os.makedirs('ml/models', exist_ok=True)
        os.makedirs('ml/results', exist_ok=True)
        
        logger.info(f"ML Pipeline initialized: {start_date} to {end_date}")
    
    def run_phase_1_data_collection(self) -> str:
        """Phase 1: Historical Data Collection"""
        print("🚀 Phase 1: Historical Data Collection")
        print("=" * 50)
        
        try:
            collector = HistoricalDataCollector(self.start_date, self.end_date)
            
            # Generate sample dates (every 15 days for faster processing)
            import pandas as pd
            date_range = pd.date_range(start=self.start_date, end=self.end_date, freq='15D')
            sample_dates = [date.strftime('%Y-%m-%d') for date in date_range]
            
            print(f"📅 Processing {len(sample_dates)} sample dates...")
            
            # Collect historical signals
            historical_df = collector.collect_historical_data(sample_dates)
            
            if len(historical_df) > 0:
                print(f"✅ Phase 1 Complete: {len(historical_df)} historical signals collected")
                return 'ml/data/historical_signals.pkl'
            else:
                print("❌ Phase 1 Failed: No historical signals collected")
                return None
                
        except Exception as e:
            print(f"❌ Phase 1 Error: {str(e)}")
            return None
    
    def run_phase_2_outcome_tracking(self, signals_file: str) -> str:
        """Phase 2: Outcome Tracking"""
        print("\n📊 Phase 2: Outcome Tracking")
        print("=" * 50)
        
        try:
            import pandas as pd
            
            # Load historical signals
            signals_df = pd.read_pickle(signals_file)
            print(f"📈 Loaded {len(signals_df)} historical signals")
            
            # Track outcomes
            tracker = OutcomeTracker()
            outcomes_df = tracker.track_batch_outcomes(signals_df, holding_days=30)
            
            if len(outcomes_df) > 0:
                # Analyze results
                analysis = tracker.analyze_outcomes(outcomes_df)
                
                print(f"✅ Phase 2 Complete: {len(outcomes_df)} outcomes calculated")
                print(f"📊 Success rate: {analysis.get('success_rate', 0):.2%}")
                print(f"📈 Average return: {analysis.get('avg_return', 0):.2%}")
                
                # Save outcomes
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                outcomes_file = f'ml/data/signal_outcomes_{timestamp}.pkl'
                outcomes_df.to_pickle(outcomes_file)
                
                return outcomes_file
            else:
                print("❌ Phase 2 Failed: No outcomes calculated")
                return None
                
        except Exception as e:
            print(f"❌ Phase 2 Error: {str(e)}")
            return None
    
    def run_phase_3_feature_engineering(self, outcomes_file: str) -> str:
        """Phase 3: Feature Engineering"""
        print("\n🔧 Phase 3: Feature Engineering")
        print("=" * 50)
        
        try:
            import pandas as pd
            
            # Load outcomes
            outcomes_df = pd.read_pickle(outcomes_file)
            print(f"📊 Loaded {len(outcomes_df)} signal outcomes")
            
            # Engineer features
            engineer = FeatureEngineer()
            features_df = engineer.engineer_features(outcomes_df)
            
            if len(features_df) > 0:
                print(f"✅ Phase 3 Complete: {len(features_df)} samples with {len(features_df.columns)} features")
                
                # Show feature categories
                feature_categories = {
                    'Technical': len([col for col in features_df.columns if any(x in col for x in ['rsi', 'macd', 'bb_', 'sma_', 'volume_', 'momentum_'])]),
                    'Market': len([col for col in features_df.columns if 'market_' in col]),
                    'Strategy': len([col for col in features_df.columns if 'strategy_' in col]),
                    'Interaction': len([col for col in features_df.columns if '_x_' in col]),
                    'Target': len([col for col in features_df.columns if col.startswith('target_')])
                }
                
                print("📈 Feature Categories:")
                for category, count in feature_categories.items():
                    print(f"   {category}: {count} features")
                
                # Save features
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                features_file = f'ml/features/engineered_features_{timestamp}.pkl'
                features_df.to_pickle(features_file)
                
                return features_file
            else:
                print("❌ Phase 3 Failed: No features generated")
                return None
                
        except Exception as e:
            print(f"❌ Phase 3 Error: {str(e)}")
            return None
    
    def run_phase_4_model_training(self, features_file: str) -> dict:
        """Phase 4: Model Training"""
        print("\n🤖 Phase 4: Model Training")
        print("=" * 50)
        
        try:
            import pandas as pd
            
            # Load features
            features_df = pd.read_pickle(features_file)
            print(f"📊 Loaded {len(features_df)} samples with {len(features_df.columns)} features")
            
            # Train models
            trainer = ModelTrainer()
            results = trainer.train_models(features_df, target_column='target_success')
            
            print(f"✅ Phase 4 Complete: Models trained successfully")
            
            # Show results
            report = results['report']
            training_summary = report['training_summary']
            print(f"📊 Models trained: {training_summary['successful_models']}/{training_summary['total_models_trained']}")
            
            # Best model performance
            best_models = report['best_models']
            best_auc = best_models['best_test_auc'][1]['test_auc']
            print(f"🏆 Best model AUC: {best_auc:.4f}")
            
            # Ensemble performance
            if 'ensemble_performance' in results:
                ensemble_auc = results['ensemble_performance']['test_auc']
                print(f"🎯 Ensemble AUC: {ensemble_auc:.4f}")
            
            return results
            
        except Exception as e:
            print(f"❌ Phase 4 Error: {str(e)}")
            return None
    
    def run_complete_pipeline(self):
        """Run the complete ML pipeline"""
        print("🧠 EmergentTrader ML Training Pipeline")
        print("=" * 70)
        print(f"📅 Date Range: {self.start_date} to {self.end_date}")
        print(f"🕐 Started: {self.pipeline_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Phase 1: Data Collection
        signals_file = self.run_phase_1_data_collection()
        if not signals_file:
            print("❌ Pipeline failed at Phase 1")
            return
        
        # Phase 2: Outcome Tracking
        outcomes_file = self.run_phase_2_outcome_tracking(signals_file)
        if not outcomes_file:
            print("❌ Pipeline failed at Phase 2")
            return
        
        # Phase 3: Feature Engineering
        features_file = self.run_phase_3_feature_engineering(outcomes_file)
        if not features_file:
            print("❌ Pipeline failed at Phase 3")
            return
        
        # Phase 4: Model Training
        training_results = self.run_phase_4_model_training(features_file)
        if not training_results:
            print("❌ Pipeline failed at Phase 4")
            return
        
        # Pipeline completion
        pipeline_end_time = datetime.now()
        total_time = pipeline_end_time - self.pipeline_start_time
        
        print("\n" + "=" * 70)
        print("🎉 ML PIPELINE COMPLETE!")
        print("=" * 70)
        print(f"⏱️  Total time: {total_time}")
        print(f"📊 Final model performance:")
        
        if training_results and 'ensemble_performance' in training_results:
            ensemble_perf = training_results['ensemble_performance']
            print(f"   🎯 Ensemble AUC: {ensemble_perf['test_auc']:.4f}")
            print(f"   📈 Expected improvement: {(ensemble_perf['test_auc'] - 0.5) * 200:.1f}% above random")
        
        print(f"\n💾 Files generated:")
        print(f"   📊 Historical signals: {signals_file}")
        print(f"   📈 Outcomes: {outcomes_file}")
        print(f"   🔧 Features: {features_file}")
        if training_results:
            print(f"   🤖 Models: {training_results['models_file']}")
            print(f"   📋 Report: {training_results['report_file']}")
        
        print(f"\n🚀 Next Steps:")
        print("1. Integrate trained models into signal generation")
        print("2. Implement real-time ML inference")
        print("3. Set up model monitoring and retraining")
        print("4. Deploy ML-enhanced trading system")
        
        return training_results

def main():
    """Run the complete ML pipeline"""
    # Initialize pipeline
    pipeline = MLPipeline(start_date='2020-01-01', end_date='2024-12-31')
    
    # Run complete pipeline
    results = pipeline.run_complete_pipeline()
    
    if results:
        print("\n✅ ML Pipeline executed successfully!")
    else:
        print("\n❌ ML Pipeline failed!")

if __name__ == "__main__":
    main()
