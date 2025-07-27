"""
AI-Enhanced Signal Generation API Endpoints
RESTful endpoints for AI-enhanced trading signals across 2000+ stocks
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
import asyncio
from services.ai_enhanced_signal_generator import ai_enhanced_generator, AIEnhancedSignal

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/ai-signals", tags=["AI Enhanced Signals"])

# Request/Response Models
class BatchTrainingRequest(BaseModel):
    symbols: Optional[List[str]] = None  # None = entire universe
    shariah_only: Optional[bool] = True
    max_concurrent: Optional[int] = 5

class EnhancedSignalRequest(BaseModel):
    symbols: Optional[List[str]] = None  # None = entire universe
    strategies: Optional[List[str]] = None
    shariah_only: Optional[bool] = True
    min_confidence: Optional[float] = 0.6
    ai_weight: Optional[float] = 0.4  # Weight of AI vs traditional signals

class TopSignalsRequest(BaseModel):
    limit: Optional[int] = 50
    min_combined_confidence: Optional[float] = 0.7
    strategies: Optional[List[str]] = None

class AIEnhancedResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

@router.post("/train/batch", response_model=AIEnhancedResponse)
async def batch_train_models(request: BatchTrainingRequest, background_tasks: BackgroundTasks):
    """
    Train AI models for multiple stocks (up to 2000+)
    
    Features:
    - Concurrent training for efficiency
    - Progress tracking and reporting
    - Automatic model validation
    - Background processing for large batches
    """
    try:
        logger.info("Starting batch AI model training")
        
        # Load stock universe if symbols not provided
        if request.symbols is None:
            symbols = await ai_enhanced_generator.load_stock_universe(request.shariah_only)
        else:
            symbols = request.symbols
        
        if len(symbols) == 0:
            return AIEnhancedResponse(
                success=False,
                error="No symbols found for training"
            )
        
        # Start training in background for large batches
        if len(symbols) > 20:
            background_tasks.add_task(
                batch_training_background,
                symbols,
                request.max_concurrent
            )
            
            return AIEnhancedResponse(
                success=True,
                data={
                    'message': f'Batch training started for {len(symbols)} symbols',
                    'symbols_count': len(symbols),
                    'max_concurrent': request.max_concurrent,
                    'estimated_time': f'{len(symbols) * 2 // request.max_concurrent} minutes',
                    'status': 'training_started'
                }
            )
        else:
            # Train smaller batches synchronously
            results = await ai_enhanced_generator.batch_train_models(
                symbols, request.max_concurrent
            )
            
            successful = sum(1 for success in results.values() if success)
            
            return AIEnhancedResponse(
                success=True,
                data={
                    'message': f'Batch training completed',
                    'total_symbols': len(symbols),
                    'successful_training': successful,
                    'failed_training': len(symbols) - successful,
                    'success_rate': f'{(successful/len(symbols)*100):.1f}%',
                    'results': results
                }
            )
        
    except Exception as e:
        logger.error(f"Error in batch training: {str(e)}")
        return AIEnhancedResponse(
            success=False,
            error=f"Batch training failed: {str(e)}"
        )

@router.post("/generate", response_model=AIEnhancedResponse)
async def generate_ai_enhanced_signals(request: EnhancedSignalRequest):
    """
    Generate AI-enhanced trading signals
    
    Features:
    - Combines traditional TA with AI predictions
    - Processes 2000+ stocks efficiently
    - Confidence scoring and risk assessment
    - Enhanced targets and stop losses
    - Recommendation strength analysis
    """
    try:
        logger.info(f"Generating AI-enhanced signals")
        
        # Generate enhanced signals
        enhanced_signals = await ai_enhanced_generator.generate_ai_enhanced_signals(
            symbols=request.symbols,
            strategies=request.strategies,
            shariah_only=request.shariah_only,
            min_confidence=request.min_confidence,
            ai_weight=request.ai_weight
        )
        
        # Format signals for response
        formatted_signals = []
        for signal in enhanced_signals:
            formatted_signal = {
                'symbol': signal.symbol,
                'strategy': signal.strategy,
                'signal': signal.signal,
                'price': round(signal.price, 2),
                'target_price': round(signal.target_price, 2),
                'stop_loss': round(signal.stop_loss, 2),
                'enhanced_target': round(signal.enhanced_target, 2),
                'enhanced_stop_loss': round(signal.enhanced_stop_loss, 2),
                'traditional_confidence': round(signal.confidence * 100, 1),
                'ai_confidence_1d': round(signal.ai_confidence_1d * 100, 1),
                'combined_confidence': round(signal.combined_confidence * 100, 1),
                'recommendation_strength': signal.recommendation_strength,
                'ai_prediction_1d': round(signal.ai_prediction_1d, 2),
                'ai_trend_direction': signal.ai_trend_direction,
                'ai_risk_score': round(signal.ai_risk_score * 100, 1),
                'ai_model_accuracy': round(signal.ai_model_accuracy * 100, 1),
                'generated_at': signal.generated_at,
                'potential_return': round(((signal.enhanced_target - signal.price) / signal.price) * 100, 2),
                'risk_reward_ratio': round((signal.enhanced_target - signal.price) / (signal.price - signal.enhanced_stop_loss), 2)
            }
            formatted_signals.append(formatted_signal)
        
        # Sort by combined confidence
        formatted_signals.sort(key=lambda x: x['combined_confidence'], reverse=True)
        
        # Generate summary statistics
        total_signals = len(formatted_signals)
        ai_enhanced_count = sum(1 for s in formatted_signals if s['ai_confidence_1d'] > 50)
        strong_buy_count = sum(1 for s in formatted_signals if s['recommendation_strength'] == 'STRONG_BUY')
        buy_count = sum(1 for s in formatted_signals if s['recommendation_strength'] == 'BUY')
        
        avg_confidence = sum(s['combined_confidence'] for s in formatted_signals) / total_signals if total_signals > 0 else 0
        avg_potential_return = sum(s['potential_return'] for s in formatted_signals) / total_signals if total_signals > 0 else 0
        
        return AIEnhancedResponse(
            success=True,
            data={
                'signals': formatted_signals,
                'summary': {
                    'total_signals': total_signals,
                    'ai_enhanced_signals': ai_enhanced_count,
                    'strong_buy_signals': strong_buy_count,
                    'buy_signals': buy_count,
                    'average_confidence': round(avg_confidence, 1),
                    'average_potential_return': round(avg_potential_return, 2),
                    'ai_weight_used': request.ai_weight,
                    'generated_at': datetime.now().isoformat()
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Error generating AI-enhanced signals: {str(e)}")
        return AIEnhancedResponse(
            success=False,
            error=f"Signal generation failed: {str(e)}"
        )

@router.post("/top-signals", response_model=AIEnhancedResponse)
async def get_top_ai_enhanced_signals(request: TopSignalsRequest):
    """
    Get top AI-enhanced signals from entire stock universe
    
    Features:
    - Processes entire 2000+ stock universe
    - Returns highest confidence signals
    - Filters by minimum confidence threshold
    - Sorted by combined AI + traditional confidence
    """
    try:
        logger.info(f"Getting top {request.limit} AI-enhanced signals")
        
        # Get top signals
        top_signals = await ai_enhanced_generator.get_top_ai_enhanced_signals(
            limit=request.limit,
            min_combined_confidence=request.min_combined_confidence,
            strategies=request.strategies
        )
        
        # Format for response
        formatted_signals = []
        for signal in top_signals:
            formatted_signal = {
                'rank': len(formatted_signals) + 1,
                'symbol': signal.symbol,
                'strategy': signal.strategy,
                'signal': signal.signal,
                'price': round(signal.price, 2),
                'enhanced_target': round(signal.enhanced_target, 2),
                'enhanced_stop_loss': round(signal.enhanced_stop_loss, 2),
                'combined_confidence': round(signal.combined_confidence * 100, 1),
                'recommendation_strength': signal.recommendation_strength,
                'ai_trend_direction': signal.ai_trend_direction,
                'potential_return': round(((signal.enhanced_target - signal.price) / signal.price) * 100, 2),
                'ai_model_accuracy': round(signal.ai_model_accuracy * 100, 1),
                'risk_score': round(signal.ai_risk_score * 100, 1)
            }
            formatted_signals.append(formatted_signal)
        
        # Calculate portfolio metrics
        total_potential_return = sum(s['potential_return'] for s in formatted_signals)
        avg_confidence = sum(s['combined_confidence'] for s in formatted_signals) / len(formatted_signals) if formatted_signals else 0
        strong_signals = sum(1 for s in formatted_signals if s['recommendation_strength'] in ['STRONG_BUY', 'STRONG_SELL'])
        
        return AIEnhancedResponse(
            success=True,
            data={
                'top_signals': formatted_signals,
                'portfolio_metrics': {
                    'total_signals': len(formatted_signals),
                    'average_confidence': round(avg_confidence, 1),
                    'total_potential_return': round(total_potential_return, 2),
                    'strong_signals_count': strong_signals,
                    'min_confidence_threshold': request.min_combined_confidence * 100,
                    'generated_at': datetime.now().isoformat()
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting top signals: {str(e)}")
        return AIEnhancedResponse(
            success=False,
            error=f"Failed to get top signals: {str(e)}"
        )

@router.get("/stats", response_model=AIEnhancedResponse)
async def get_generation_stats():
    """
    Get AI-enhanced signal generation statistics
    
    Returns:
    - Training statistics
    - Generation performance metrics
    - Model coverage information
    - System health indicators
    """
    try:
        stats = ai_enhanced_generator.get_generation_stats()
        
        return AIEnhancedResponse(
            success=True,
            data={
                'statistics': stats,
                'system_info': {
                    'service': 'AI Enhanced Signal Generator',
                    'status': 'operational',
                    'timestamp': datetime.now().isoformat()
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting generation stats: {str(e)}")
        return AIEnhancedResponse(
            success=False,
            error=f"Failed to get statistics: {str(e)}"
        )

@router.get("/universe", response_model=AIEnhancedResponse)
async def get_stock_universe(shariah_only: bool = True):
    """
    Get the current stock universe being used for AI enhancement
    
    Returns information about available stocks and training status
    """
    try:
        # Load universe
        universe = await ai_enhanced_generator.load_stock_universe(shariah_only)
        
        # Get training status
        trained_models = ai_enhanced_generator.trained_models
        
        # Calculate coverage
        coverage_percentage = (len(trained_models) / len(universe)) * 100 if universe else 0
        
        return AIEnhancedResponse(
            success=True,
            data={
                'universe_info': {
                    'total_stocks': len(universe),
                    'trained_models': len(trained_models),
                    'coverage_percentage': round(coverage_percentage, 1),
                    'shariah_only': shariah_only
                },
                'sample_stocks': universe[:20],  # First 20 as sample
                'trained_stocks': list(trained_models)[:20],  # First 20 trained
                'untrained_stocks': [s for s in universe if s not in trained_models][:20]
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting stock universe: {str(e)}")
        return AIEnhancedResponse(
            success=False,
            error=f"Failed to get universe: {str(e)}"
        )

@router.delete("/models/cleanup", response_model=AIEnhancedResponse)
async def cleanup_old_models(older_than_days: int = 30):
    """
    Clean up old AI models to free up storage space
    
    Removes models older than specified days
    """
    try:
        import os
        import glob
        from datetime import datetime, timedelta
        
        model_dir = ai_enhanced_generator.ai_predictor.model_dir
        cutoff_date = datetime.now() - timedelta(days=older_than_days)
        
        model_files = glob.glob(os.path.join(model_dir, "*_models.joblib"))
        deleted_count = 0
        
        for model_file in model_files:
            file_time = datetime.fromtimestamp(os.path.getmtime(model_file))
            if file_time < cutoff_date:
                os.remove(model_file)
                deleted_count += 1
                
                # Remove from trained models set
                symbol = os.path.basename(model_file).replace('_models.joblib', '')
                ai_enhanced_generator.trained_models.discard(symbol)
        
        return AIEnhancedResponse(
            success=True,
            data={
                'message': f'Cleaned up {deleted_count} old models',
                'deleted_models': deleted_count,
                'cutoff_date': cutoff_date.isoformat(),
                'remaining_models': len(ai_enhanced_generator.trained_models)
            }
        )
        
    except Exception as e:
        logger.error(f"Error cleaning up models: {str(e)}")
        return AIEnhancedResponse(
            success=False,
            error=f"Cleanup failed: {str(e)}"
        )

# Background task functions
async def batch_training_background(symbols: List[str], max_concurrent: int):
    """Background task for large batch training"""
    try:
        logger.info(f"Background batch training started for {len(symbols)} symbols")
        
        results = await ai_enhanced_generator.batch_train_models(symbols, max_concurrent)
        
        successful = sum(1 for success in results.values() if success)
        logger.info(f"Background batch training completed: {successful}/{len(symbols)} successful")
        
    except Exception as e:
        logger.error(f"Background batch training failed: {str(e)}")

# Health check endpoint
@router.get("/health", response_model=AIEnhancedResponse)
async def health_check():
    """Health check for AI-enhanced signal generation service"""
    try:
        stats = ai_enhanced_generator.get_generation_stats()
        
        return AIEnhancedResponse(
            success=True,
            data={
                'status': 'healthy',
                'service': 'AI Enhanced Signal Generator',
                'trained_models': len(ai_enhanced_generator.trained_models),
                'universe_size': len(ai_enhanced_generator.stock_universe),
                'timestamp': datetime.now().isoformat()
            }
        )
    except Exception as e:
        return AIEnhancedResponse(
            success=False,
            error=f"Health check failed: {str(e)}"
        )
