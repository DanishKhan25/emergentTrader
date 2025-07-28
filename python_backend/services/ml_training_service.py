"""
ML Training Service for EmergentTrader
Handles daily ML model training after market hours
"""

import os
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, classification_report
import joblib
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from services.enhanced_notification_service import notification_service
from api_handler import EmergentTraderAPI

logger = logging.getLogger(__name__)

class MLTrainingService:
    def __init__(self):
        """Initialize ML training service"""
        self.api = EmergentTraderAPI()
        self.models_dir = "python_backend/models/daily_training"
        self.ensure_models_directory()
        
        # Model configurations
        self.model_configs = {
            'multibagger_rf': {
                'model': RandomForestClassifier(n_estimators=100, random_state=42),
                'name': 'Multibagger Random Forest'
            },
            'multibagger_gb': {
                'model': GradientBoostingClassifier(n_estimators=100, random_state=42),
                'name': 'Multibagger Gradient Boosting'
            },
            'momentum_rf': {
                'model': RandomForestClassifier(n_estimators=80, random_state=42),
                'name': 'Momentum Random Forest'
            }
        }
        
        logger.info("ML Training Service initialized")
    
    def ensure_models_directory(self):
        """Ensure models directory exists"""
        os.makedirs(self.models_dir, exist_ok=True)
    
    async def daily_training_task(self) -> Dict:
        """Main daily training task"""
        try:
            logger.info("🤖 Starting daily ML model training...")
            
            # Send start notification
            await notification_service.send_telegram_message(
                f"🤖 <b>Daily ML Training Started</b>\n\n"
                f"Training models with latest market data...\n"
                f"Time: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n"
                f"<i>This may take 10-15 minutes. You'll be notified when complete.</i>"
            )
            
            # Step 1: Prepare training data
            training_data = await self.prepare_training_data()
            
            if not training_data['success']:
                raise Exception(f"Data preparation failed: {training_data['error']}")
            
            # Step 2: Train models
            training_results = await self.train_models(training_data['data'])
            
            # Step 3: Validate models
            validation_results = await self.validate_models(training_results)
            
            # Step 4: Save best models
            save_results = await self.save_models(validation_results)
            
            # Step 5: Generate training report
            report = self.generate_training_report(training_results, validation_results, save_results)
            
            # Send completion notification
            await notification_service.send_telegram_message(report)
            
            logger.info("✅ Daily ML training completed successfully")
            
            return {
                'success': True,
                'training_results': training_results,
                'validation_results': validation_results,
                'report': report,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in daily ML training: {e}")
            
            # Send error notification
            await notification_service.send_telegram_message(
                f"🚨 <b>ML Training Failed</b>\n\n"
                f"Error: {str(e)}\n"
                f"Time: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n"
                f"<i>Please check system logs for details.</i>"
            )
            
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def prepare_training_data(self) -> Dict:
        """Prepare training data from recent market data"""
        try:
            logger.info("📊 Preparing training data...")
            
            # Get Shariah stocks for training
            stocks_result = self.api.get_shariah_stocks(include_prices=True, force_refresh=True)
            
            if not stocks_result.get('success'):
                return {
                    'success': False,
                    'error': 'Could not fetch stocks data'
                }
            
            stocks = stocks_result.get('data', {}).get('stocks', [])
            
            if len(stocks) < 100:
                return {
                    'success': False,
                    'error': f'Insufficient data: only {len(stocks)} stocks available'
                }
            
            # Create feature matrix
            features = []
            labels = []
            
            for stock in stocks:
                try:
                    # Extract features
                    feature_vector = self.extract_features(stock)
                    
                    if feature_vector is not None:
                        features.append(feature_vector)
                        
                        # Create label based on recent performance
                        # This is a simplified labeling - in production, you'd use historical data
                        label = self.create_label(stock)
                        labels.append(label)
                
                except Exception as e:
                    logger.warning(f"Error processing stock {stock.get('symbol', 'Unknown')}: {e}")
                    continue
            
            if len(features) < 50:
                return {
                    'success': False,
                    'error': f'Insufficient valid features: only {len(features)} samples'
                }
            
            # Convert to numpy arrays
            X = np.array(features)
            y = np.array(labels)
            
            logger.info(f"✅ Prepared training data: {X.shape[0]} samples, {X.shape[1]} features")
            
            return {
                'success': True,
                'data': {
                    'X': X,
                    'y': y,
                    'feature_names': self.get_feature_names(),
                    'samples_count': X.shape[0],
                    'features_count': X.shape[1]
                }
            }
            
        except Exception as e:
            logger.error(f"Error preparing training data: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def extract_features(self, stock: Dict) -> Optional[List[float]]:
        """Extract features from stock data"""
        try:
            # Basic features from stock data
            features = []
            
            # Price-based features
            current_price = stock.get('current_price', 0)
            market_cap = stock.get('market_cap', 0)
            volume = stock.get('volume', 0)
            
            if current_price <= 0:
                return None
            
            features.extend([
                current_price,
                market_cap / 1e9 if market_cap > 0 else 0,  # Market cap in billions
                volume / 1e6 if volume > 0 else 0,  # Volume in millions
            ])
            
            # Technical indicators (simplified)
            price_change = stock.get('price_change_percent', 0)
            features.append(price_change)
            
            # Sector encoding (simplified)
            sector = stock.get('sector', 'Unknown')
            sector_encoding = hash(sector) % 10  # Simple hash-based encoding
            features.append(sector_encoding)
            
            # Financial ratios (if available)
            pe_ratio = stock.get('pe_ratio', 0)
            pb_ratio = stock.get('pb_ratio', 0)
            
            features.extend([
                pe_ratio if pe_ratio > 0 else 0,
                pb_ratio if pb_ratio > 0 else 0,
            ])
            
            # Additional derived features
            features.extend([
                1 if current_price > 100 else 0,  # High price stock
                1 if market_cap > 1e10 else 0,    # Large cap
                1 if volume > 1e6 else 0,         # High volume
            ])
            
            return features
            
        except Exception as e:
            logger.warning(f"Error extracting features: {e}")
            return None
    
    def create_label(self, stock: Dict) -> int:
        """Create label for supervised learning"""
        try:
            # Simplified labeling based on recent performance
            # In production, this would use historical data and future returns
            
            price_change = stock.get('price_change_percent', 0)
            volume = stock.get('volume', 0)
            market_cap = stock.get('market_cap', 0)
            
            # Positive label criteria (potential multibagger)
            if (price_change > 5 and volume > 1e6 and market_cap > 1e9):
                return 1
            else:
                return 0
                
        except Exception as e:
            logger.warning(f"Error creating label: {e}")
            return 0
    
    def get_feature_names(self) -> List[str]:
        """Get feature names for model interpretation"""
        return [
            'current_price',
            'market_cap_billions',
            'volume_millions',
            'price_change_percent',
            'sector_encoding',
            'pe_ratio',
            'pb_ratio',
            'is_high_price',
            'is_large_cap',
            'is_high_volume'
        ]
    
    async def train_models(self, training_data: Dict) -> Dict:
        """Train all configured models"""
        try:
            logger.info("🎯 Training ML models...")
            
            X = training_data['X']
            y = training_data['y']
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            training_results = {}
            
            for model_name, config in self.model_configs.items():
                try:
                    logger.info(f"Training {config['name']}...")
                    
                    model = config['model']
                    
                    # Train model
                    model.fit(X_train, y_train)
                    
                    # Make predictions
                    y_pred = model.predict(X_test)
                    
                    # Calculate metrics
                    accuracy = accuracy_score(y_test, y_pred)
                    cv_scores = cross_val_score(model, X_train, y_train, cv=5)
                    
                    training_results[model_name] = {
                        'model': model,
                        'accuracy': accuracy,
                        'cv_mean': cv_scores.mean(),
                        'cv_std': cv_scores.std(),
                        'predictions': y_pred,
                        'test_labels': y_test
                    }
                    
                    logger.info(f"✅ {config['name']} - Accuracy: {accuracy:.3f}, CV: {cv_scores.mean():.3f}±{cv_scores.std():.3f}")
                    
                except Exception as e:
                    logger.error(f"Error training {model_name}: {e}")
                    continue
            
            return {
                'success': True,
                'results': training_results,
                'data_split': {
                    'train_samples': len(X_train),
                    'test_samples': len(X_test),
                    'features': X.shape[1]
                }
            }
            
        except Exception as e:
            logger.error(f"Error training models: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def validate_models(self, training_results: Dict) -> Dict:
        """Validate trained models"""
        try:
            logger.info("✅ Validating models...")
            
            if not training_results.get('success'):
                return {
                    'success': False,
                    'error': 'No training results to validate'
                }
            
            results = training_results['results']
            validation_results = {}
            
            for model_name, result in results.items():
                try:
                    accuracy = result['accuracy']
                    cv_mean = result['cv_mean']
                    cv_std = result['cv_std']
                    
                    # Validation criteria
                    is_valid = (
                        accuracy > 0.6 and  # Minimum accuracy
                        cv_mean > 0.55 and  # Minimum cross-validation score
                        cv_std < 0.1        # Maximum standard deviation
                    )
                    
                    validation_results[model_name] = {
                        'is_valid': is_valid,
                        'accuracy': accuracy,
                        'cv_mean': cv_mean,
                        'cv_std': cv_std,
                        'model': result['model']
                    }
                    
                    status = "✅ VALID" if is_valid else "❌ INVALID"
                    logger.info(f"{model_name}: {status} (Acc: {accuracy:.3f}, CV: {cv_mean:.3f}±{cv_std:.3f})")
                    
                except Exception as e:
                    logger.error(f"Error validating {model_name}: {e}")
                    continue
            
            return {
                'success': True,
                'results': validation_results
            }
            
        except Exception as e:
            logger.error(f"Error validating models: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def save_models(self, validation_results: Dict) -> Dict:
        """Save validated models"""
        try:
            logger.info("💾 Saving validated models...")
            
            if not validation_results.get('success'):
                return {
                    'success': False,
                    'error': 'No validation results to save'
                }
            
            results = validation_results['results']
            saved_models = {}
            
            for model_name, result in results.items():
                try:
                    if result['is_valid']:
                        model = result['model']
                        
                        # Save model with timestamp
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        filename = f"{model_name}_{timestamp}.joblib"
                        filepath = os.path.join(self.models_dir, filename)
                        
                        joblib.dump(model, filepath)
                        
                        # Also save as latest
                        latest_filepath = os.path.join(self.models_dir, f"{model_name}_latest.joblib")
                        joblib.dump(model, latest_filepath)
                        
                        saved_models[model_name] = {
                            'filepath': filepath,
                            'latest_filepath': latest_filepath,
                            'accuracy': result['accuracy'],
                            'cv_mean': result['cv_mean']
                        }
                        
                        logger.info(f"✅ Saved {model_name} to {filename}")
                    
                except Exception as e:
                    logger.error(f"Error saving {model_name}: {e}")
                    continue
            
            return {
                'success': True,
                'saved_models': saved_models,
                'saved_count': len(saved_models)
            }
            
        except Exception as e:
            logger.error(f"Error saving models: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_training_report(self, training_results: Dict, validation_results: Dict, save_results: Dict) -> str:
        """Generate training report for notification"""
        try:
            if not all([training_results.get('success'), validation_results.get('success'), save_results.get('success')]):
                return f"""❌ <b>ML Training Failed</b>

Some steps failed during training process.
Time: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

<i>Check logs for details.</i>"""
            
            # Get statistics
            total_models = len(self.model_configs)
            trained_models = len(training_results['results'])
            valid_models = len([r for r in validation_results['results'].values() if r['is_valid']])
            saved_models = save_results['saved_count']
            
            # Get best model
            best_model = None
            best_accuracy = 0
            
            for model_name, result in validation_results['results'].items():
                if result['is_valid'] and result['accuracy'] > best_accuracy:
                    best_accuracy = result['accuracy']
                    best_model = model_name
            
            # Create detailed report
            model_details = ""
            for model_name, result in validation_results['results'].items():
                status = "✅" if result['is_valid'] else "❌"
                model_details += f"{status} {model_name}: {result['accuracy']:.1%} accuracy\n"
            
            report = f"""✅ <b>ML Training Complete!</b>

📊 <b>Training Summary:</b>
• Models Configured: {total_models}
• Successfully Trained: {trained_models}
• Passed Validation: {valid_models}
• Saved to Disk: {saved_models}

🏆 <b>Best Model:</b> {best_model or 'None'}
📈 <b>Best Accuracy:</b> {best_accuracy:.1%}

📋 <b>Model Results:</b>
{model_details}

💾 <b>Data Used:</b>
• Training Samples: {training_results.get('data_split', {}).get('train_samples', 'N/A')}
• Test Samples: {training_results.get('data_split', {}).get('test_samples', 'N/A')}
• Features: {training_results.get('data_split', {}).get('features', 'N/A')}

⏰ <b>Completed:</b> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

<i>Models are ready for tomorrow's trading! 🚀</i>"""
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating training report: {e}")
            return f"""✅ <b>ML Training Complete!</b>

Training finished successfully but report generation failed.
Time: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

<i>Check logs for details.</i>"""

# Global instance
ml_training_service = MLTrainingService()
