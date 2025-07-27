"""
AI Price Prediction API Endpoints
RESTful endpoints for machine learning price forecasting
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
from services.ai_price_predictor import ai_predictor, PredictionResult

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/ai", tags=["AI Price Predictions"])

# Request/Response Models
class PredictionRequest(BaseModel):
    symbol: str
    days_ahead: Optional[int] = 1
    retrain: Optional[bool] = False

class BatchPredictionRequest(BaseModel):
    symbols: List[str]
    days_ahead: Optional[int] = 1
    retrain: Optional[bool] = False

class TrainingRequest(BaseModel):
    symbol: str
    retrain: Optional[bool] = True

class PredictionResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

@router.post("/predict", response_model=PredictionResponse)
async def predict_stock_price(request: PredictionRequest):
    """
    Generate AI-powered price prediction for a single stock
    
    Features:
    - Multi-horizon predictions (1d, 7d, 30d)
    - Ensemble ML models (Random Forest, Gradient Boosting, Linear)
    - Technical analysis features
    - Confidence scoring
    - Support/Resistance levels
    - Risk assessment
    """
    try:
        logger.info(f"Generating AI prediction for {request.symbol} ({request.days_ahead} days ahead)")
        
        # Train models if needed
        if request.retrain:
            logger.info(f"Retraining models for {request.symbol}")
            await train_model_background(request.symbol, retrain=True)
        
        # Generate prediction
        prediction = ai_predictor.predict_price(
            symbol=request.symbol,
            days_ahead=request.days_ahead
        )
        
        # Format response
        response_data = {
            'symbol': prediction.symbol,
            'current_price': round(prediction.current_price, 2),
            'predictions': {
                '1_day': {
                    'price': round(prediction.predicted_price_1d, 2),
                    'confidence': round(prediction.confidence_1d * 100, 1),
                    'change_percent': round(((prediction.predicted_price_1d - prediction.current_price) / prediction.current_price) * 100, 2)
                },
                '7_day': {
                    'price': round(prediction.predicted_price_7d, 2),
                    'confidence': round(prediction.confidence_7d * 100, 1),
                    'change_percent': round(((prediction.predicted_price_7d - prediction.current_price) / prediction.current_price) * 100, 2)
                },
                '30_day': {
                    'price': round(prediction.predicted_price_30d, 2),
                    'confidence': round(prediction.confidence_30d * 100, 1),
                    'change_percent': round(((prediction.predicted_price_30d - prediction.current_price) / prediction.current_price) * 100, 2)
                }
            },
            'analysis': {
                'trend_direction': prediction.trend_direction,
                'volatility_forecast': round(prediction.volatility_forecast * 100, 2),
                'risk_score': round(prediction.risk_score * 100, 1),
                'model_accuracy': round(prediction.model_accuracy, 1)
            },
            'levels': {
                'support': [round(level, 2) for level in prediction.support_levels],
                'resistance': [round(level, 2) for level in prediction.resistance_levels]
            },
            'metadata': {
                'features_count': len(prediction.features_used),
                'prediction_timestamp': prediction.prediction_timestamp,
                'days_ahead': request.days_ahead
            }
        }
        
        logger.info(f"AI prediction generated for {request.symbol}: {prediction.trend_direction} trend, {prediction.model_accuracy:.1f}% accuracy")
        
        return PredictionResponse(
            success=True,
            data=response_data
        )
        
    except Exception as e:
        logger.error(f"Error generating AI prediction for {request.symbol}: {str(e)}")
        return PredictionResponse(
            success=False,
            error=f"Failed to generate prediction: {str(e)}"
        )

@router.post("/predict/batch", response_model=PredictionResponse)
async def predict_multiple_stocks(request: BatchPredictionRequest):
    """
    Generate AI predictions for multiple stocks
    
    Efficiently processes multiple symbols with batch optimization
    """
    try:
        logger.info(f"Generating batch AI predictions for {len(request.symbols)} symbols")
        
        predictions = {}
        errors = {}
        
        for symbol in request.symbols:
            try:
                # Train models if needed
                if request.retrain:
                    await train_model_background(symbol, retrain=True)
                
                # Generate prediction
                prediction = ai_predictor.predict_price(
                    symbol=symbol,
                    days_ahead=request.days_ahead
                )
                
                # Format prediction data
                predictions[symbol] = {
                    'current_price': round(prediction.current_price, 2),
                    'predicted_price': round(getattr(prediction, f'predicted_price_{request.days_ahead}d', prediction.predicted_price_1d), 2),
                    'confidence': round(getattr(prediction, f'confidence_{request.days_ahead}d', prediction.confidence_1d) * 100, 1),
                    'trend_direction': prediction.trend_direction,
                    'risk_score': round(prediction.risk_score * 100, 1),
                    'change_percent': round(((getattr(prediction, f'predicted_price_{request.days_ahead}d', prediction.predicted_price_1d) - prediction.current_price) / prediction.current_price) * 100, 2)
                }
                
            except Exception as e:
                logger.error(f"Error predicting {symbol}: {str(e)}")
                errors[symbol] = str(e)
        
        response_data = {
            'predictions': predictions,
            'errors': errors,
            'summary': {
                'total_requested': len(request.symbols),
                'successful_predictions': len(predictions),
                'failed_predictions': len(errors),
                'days_ahead': request.days_ahead,
                'generated_at': datetime.now().isoformat()
            }
        }
        
        logger.info(f"Batch predictions complete: {len(predictions)} successful, {len(errors)} failed")
        
        return PredictionResponse(
            success=True,
            data=response_data
        )
        
    except Exception as e:
        logger.error(f"Error in batch prediction: {str(e)}")
        return PredictionResponse(
            success=False,
            error=f"Batch prediction failed: {str(e)}"
        )

@router.post("/train", response_model=PredictionResponse)
async def train_prediction_model(request: TrainingRequest, background_tasks: BackgroundTasks):
    """
    Train or retrain AI models for a specific stock
    
    Features:
    - Comprehensive feature engineering
    - Multiple ML algorithms
    - Cross-validation
    - Performance metrics
    - Model persistence
    """
    try:
        logger.info(f"Starting model training for {request.symbol}")
        
        # Start training in background
        background_tasks.add_task(train_model_background, request.symbol, request.retrain)
        
        return PredictionResponse(
            success=True,
            data={
                'message': f"Model training started for {request.symbol}",
                'symbol': request.symbol,
                'retrain': request.retrain,
                'estimated_time': '2-5 minutes',
                'status': 'training_started'
            }
        )
        
    except Exception as e:
        logger.error(f"Error starting model training for {request.symbol}: {str(e)}")
        return PredictionResponse(
            success=False,
            error=f"Failed to start training: {str(e)}"
        )

@router.get("/model/performance/{symbol}", response_model=PredictionResponse)
async def get_model_performance(symbol: str):
    """
    Get detailed performance metrics for trained models
    
    Returns:
    - Accuracy percentages
    - R-squared scores
    - Error metrics (MAE, RMSE)
    - Cross-validation scores
    - Training timestamps
    """
    try:
        logger.info(f"Retrieving model performance for {symbol}")
        
        performance = ai_predictor.get_model_performance(symbol)
        
        if 'error' in performance:
            return PredictionResponse(
                success=False,
                error=performance['error']
            )
        
        return PredictionResponse(
            success=True,
            data=performance
        )
        
    except Exception as e:
        logger.error(f"Error getting model performance for {symbol}: {str(e)}")
        return PredictionResponse(
            success=False,
            error=f"Failed to get performance metrics: {str(e)}"
        )

@router.get("/models/list", response_model=PredictionResponse)
async def list_trained_models():
    """
    List all available trained models
    
    Returns information about all symbols with trained models
    """
    try:
        import os
        from glob import glob
        
        model_files = glob(os.path.join(ai_predictor.model_dir, "*_models.joblib"))
        
        models = []
        for model_file in model_files:
            symbol = os.path.basename(model_file).replace('_models.joblib', '')
            
            # Get basic model info
            try:
                import joblib
                saved_data = joblib.load(model_file)
                models.append({
                    'symbol': symbol,
                    'trained_at': saved_data.get('trained_at'),
                    'features_count': len(saved_data.get('features', [])),
                    'model_types': list(saved_data.get('models', {}).keys()),
                    'file_size': os.path.getsize(model_file)
                })
            except Exception as e:
                logger.warning(f"Error reading model file {model_file}: {str(e)}")
        
        return PredictionResponse(
            success=True,
            data={
                'models': models,
                'total_models': len(models),
                'model_directory': ai_predictor.model_dir
            }
        )
        
    except Exception as e:
        logger.error(f"Error listing trained models: {str(e)}")
        return PredictionResponse(
            success=False,
            error=f"Failed to list models: {str(e)}"
        )

@router.delete("/model/{symbol}", response_model=PredictionResponse)
async def delete_model(symbol: str):
    """
    Delete trained model for a specific symbol
    
    Useful for cleanup or forcing model retraining
    """
    try:
        import os
        
        model_path = os.path.join(ai_predictor.model_dir, f"{symbol}_models.joblib")
        
        if os.path.exists(model_path):
            os.remove(model_path)
            logger.info(f"Deleted model for {symbol}")
            
            return PredictionResponse(
                success=True,
                data={
                    'message': f"Model deleted for {symbol}",
                    'symbol': symbol
                }
            )
        else:
            return PredictionResponse(
                success=False,
                error=f"No model found for {symbol}"
            )
            
    except Exception as e:
        logger.error(f"Error deleting model for {symbol}: {str(e)}")
        return PredictionResponse(
            success=False,
            error=f"Failed to delete model: {str(e)}"
        )

# Background task functions
async def train_model_background(symbol: str, retrain: bool = True):
    """Background task for model training"""
    try:
        logger.info(f"Background training started for {symbol}")
        
        metrics = ai_predictor.train_models(symbol, retrain=retrain)
        
        # Log training results
        for horizon, horizon_metrics in metrics.items():
            for model_name, model_metrics in horizon_metrics.items():
                logger.info(f"{symbol} {model_name} {horizon}: {model_metrics.accuracy_percentage:.2f}% accuracy")
        
        logger.info(f"Background training completed for {symbol}")
        
    except Exception as e:
        logger.error(f"Background training failed for {symbol}: {str(e)}")

# Health check endpoint
@router.get("/health", response_model=PredictionResponse)
async def health_check():
    """Health check for AI prediction service"""
    try:
        return PredictionResponse(
            success=True,
            data={
                'status': 'healthy',
                'service': 'AI Price Prediction',
                'models_directory': ai_predictor.model_dir,
                'timestamp': datetime.now().isoformat()
            }
        )
    except Exception as e:
        return PredictionResponse(
            success=False,
            error=f"Health check failed: {str(e)}"
        )
