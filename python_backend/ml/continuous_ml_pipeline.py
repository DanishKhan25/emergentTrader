#!/usr/bin/env python3
"""
Continuous ML Data Pipeline
Automatically collect signal outcomes and retrain models
"""

import schedule
import time
from datetime import datetime, timedelta
import logging
from signal_outcome_tracker import SignalOutcomeTracker
from historical_data_collector import HistoricalDataCollector
from ml_trainer_fixed import MLTrainerFixed

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContinuousMLPipeline:
    """Continuous ML data collection and training pipeline"""
    
    def __init__(self):
        self.outcome_tracker = SignalOutcomeTracker()
        self.data_collector = HistoricalDataCollector()
        self.ml_trainer = MLTrainerFixed()
        
        logger.info("Continuous ML Pipeline initialized")
    
    def daily_outcome_tracking(self):
        """Daily task: Track outcomes of recent signals"""
        logger.info("Running daily outcome tracking...")
        
        try:
            # Get signals from last 30 days that need outcome tracking
            recent_signals = self.get_signals_needing_tracking()
            
            tracked_count = 0
            for signal_id in recent_signals:
                result = self.outcome_tracker.track_signal_outcome(signal_id)
                if 'error' not in result:
                    tracked_count += 1
            
            logger.info(f"Tracked outcomes for {tracked_count} signals")
            
        except Exception as e:
            logger.error(f"Error in daily outcome tracking: {str(e)}")
    
    def weekly_data_collection(self):
        """Weekly task: Collect and process new training data"""
        logger.info("Running weekly data collection...")
        
        try:
            # Collect signals from last week
            historical_signals = self.data_collector.collect_historical_signals(months_back=1)
            
            # Calculate outcomes for new signals
            signals_with_outcomes = self.data_collector.calculate_historical_outcomes(historical_signals)
            
            # Update training dataset
            self.update_training_dataset(signals_with_outcomes)
            
            logger.info(f"Updated training data with {len(signals_with_outcomes)} new samples")
            
        except Exception as e:
            logger.error(f"Error in weekly data collection: {str(e)}")
    
    def monthly_model_retraining(self):
        """Monthly task: Retrain ML models with new data"""
        logger.info("Running monthly model retraining...")
        
        try:
            # Get latest training data
            training_data = self.outcome_tracker.get_training_data(days_back=180)
            
            if len(training_data) < 100:
                logger.warning("Insufficient training data for retraining")
                return
            
            # Prepare data for ML training
            ml_data = self.data_collector.prepare_ml_training_data(training_data)
            
            # Engineer features
            X, y = self.ml_trainer.engineer_features(ml_data)
            
            # Train new models
            performance = self.ml_trainer.train_models(X, y)
            
            # Save updated models
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            model_path = f'python_backend/ml/models/retrained_models_{timestamp}.pkl'
            self.ml_trainer.save_models(model_path)
            
            # Generate report
            report = self.ml_trainer.generate_training_report()
            
            # Save report
            with open(f'ml_retraining_report_{timestamp}.txt', 'w') as f:
                f.write(report)
            
            logger.info(f"Model retraining completed. Best AUC: {max(p['auc_score'] for p in performance.values()):.3f}")
            
        except Exception as e:
            logger.error(f"Error in monthly retraining: {str(e)}")
    
    def get_signals_needing_tracking(self):
        """Get signals that need outcome tracking"""
        # Implement based on your database schema
        # Return list of signal IDs that are 5-30 days old and don't have outcomes yet
        return []
    
    def update_training_dataset(self, new_data):
        """Update the training dataset with new signal outcomes"""
        # Implement based on your storage system
        pass
    
    def start_pipeline(self):
        """Start the continuous pipeline"""
        logger.info("Starting continuous ML pipeline...")
        
        # Schedule tasks
        schedule.every().day.at("09:00").do(self.daily_outcome_tracking)
        schedule.every().week.do(self.weekly_data_collection)
        schedule.every().month.do(self.monthly_model_retraining)
        
        # Run initial tasks
        self.daily_outcome_tracking()
        
        # Main loop
        while True:
            schedule.run_pending()
            time.sleep(3600)  # Check every hour

if __name__ == "__main__":
    pipeline = ContinuousMLPipeline()
    pipeline.start_pipeline()
