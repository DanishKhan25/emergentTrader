"""
AI-Enhanced Signal Generator
Integrates AI/ML predictions with traditional signal generation for 2000+ stocks
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import logging
import asyncio
import concurrent.futures
from dataclasses import dataclass
import yfinance as yf
from services.ai_price_predictor import ai_predictor
from core.enhanced_signal_engine import EnhancedSignalEngine
from core.enhanced_shariah_filter import EnhancedShariahFilter
import json
import os

logger = logging.getLogger(__name__)

@dataclass
class AIEnhancedSignal:
    """Enhanced signal with AI predictions"""
    # Traditional signal fields
    symbol: str
    strategy: str
    signal: str  # BUY/SELL
    confidence: float
    price: float
    target_price: float
    stop_loss: float
    
    # AI enhancement fields
    ai_prediction_1d: float
    ai_prediction_7d: float
    ai_prediction_30d: float
    ai_confidence_1d: float
    ai_confidence_7d: float
    ai_confidence_30d: float
    ai_trend_direction: str
    ai_risk_score: float
    
    # Combined analysis
    combined_confidence: float
    enhanced_target: float
    enhanced_stop_loss: float
    recommendation_strength: str  # STRONG_BUY, BUY, HOLD, SELL, STRONG_SELL
    
    # Metadata
    generated_at: str
    ai_model_accuracy: float
    traditional_factors: Dict[str, Any]
    ai_factors: Dict[str, Any]

class AIEnhancedSignalGenerator:
    """AI-Enhanced Signal Generation System for 2000+ stocks"""
    
    def __init__(self):
        """Initialize the AI-enhanced signal generator"""
        self.ai_predictor = ai_predictor
        self.signal_engine = EnhancedSignalEngine()
        self.shariah_filter = EnhancedShariahFilter()
        
        # Stock universe
        self.stock_universe = []
        self.trained_models = set()
        
        # Performance tracking
        self.generation_stats = {
            'total_processed': 0,
            'ai_enhanced': 0,
            'traditional_only': 0,
            'failed': 0,
            'avg_processing_time': 0
        }
        
        logger.info("AI-Enhanced Signal Generator initialized")
    
    async def load_stock_universe(self, shariah_only: bool = True) -> List[str]:
        """Load the complete stock universe (2000+ stocks)"""
        try:
            if shariah_only:
                # Get Shariah-compliant stocks
                shariah_stocks = await self.shariah_filter.get_shariah_universe()
                self.stock_universe = list(shariah_stocks.keys())
            else:
                # Load from NSE/BSE stock list (implement based on your data source)
                self.stock_universe = await self._load_complete_stock_universe()
            
            logger.info(f"Loaded {len(self.stock_universe)} stocks in universe")
            return self.stock_universe
            
        except Exception as e:
            logger.error(f"Error loading stock universe: {str(e)}")
            return []
    
    async def _load_complete_stock_universe(self) -> List[str]:
        """Load complete NSE/BSE stock universe"""
        # This would typically load from a comprehensive stock database
        # For now, using a representative sample
        sample_stocks = [
            'RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ICICIBANK', 'KOTAKBANK',
            'HINDUNILVR', 'SBIN', 'BHARTIARTL', 'ITC', 'ASIANPAINT', 'MARUTI',
            'AXISBANK', 'LT', 'NESTLEIND', 'HCLTECH', 'WIPRO', 'ULTRACEMCO',
            'TITAN', 'SUNPHARMA', 'ONGC', 'NTPC', 'POWERGRID', 'COALINDIA',
            'TECHM', 'TATAMOTORS', 'BAJFINANCE', 'BAJAJFINSV', 'HDFCLIFE',
            'SBILIFE', 'DIVISLAB', 'DRREDDY', 'CIPLA', 'APOLLOHOSP',
            'ADANIPORTS', 'JSWSTEEL', 'TATASTEEL', 'HINDALCO', 'VEDL',
            'GRASIM', 'BRITANNIA', 'DABUR', 'GODREJCP', 'MARICO',
            'PIDILITIND', 'BERGEPAINT', 'INDUSINDBK', 'BANDHANBNK', 'FEDERALBNK'
        ]
        
        # In production, this would query your stock database
        # and return all 2000+ stocks
        return sample_stocks
    
    async def batch_train_models(self, symbols: List[str], max_concurrent: int = 5) -> Dict[str, bool]:
        """Train AI models for multiple stocks concurrently"""
        logger.info(f"Starting batch training for {len(symbols)} symbols")
        
        results = {}
        
        # Process in batches to avoid overwhelming the system
        for i in range(0, len(symbols), max_concurrent):
            batch = symbols[i:i + max_concurrent]
            
            # Create tasks for concurrent training
            tasks = []
            for symbol in batch:
                task = self._train_single_model(symbol)
                tasks.append(task)
            
            # Execute batch concurrently
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for symbol, result in zip(batch, batch_results):
                if isinstance(result, Exception):
                    logger.error(f"Training failed for {symbol}: {str(result)}")
                    results[symbol] = False
                else:
                    results[symbol] = result
                    if result:
                        self.trained_models.add(symbol)
            
            # Progress update
            logger.info(f"Batch training progress: {min(i + max_concurrent, len(symbols))}/{len(symbols)}")
            
            # Small delay between batches
            await asyncio.sleep(1)
        
        successful = sum(1 for success in results.values() if success)
        logger.info(f"Batch training complete: {successful}/{len(symbols)} successful")
        
        return results
    
    async def _train_single_model(self, symbol: str) -> bool:
        """Train AI model for a single stock"""
        try:
            # Train with retrain=True to ensure fresh models
            metrics = self.ai_predictor.train_models(symbol, retrain=True)
            
            if metrics:
                # Check if training was successful (at least one model with decent accuracy)
                for horizon_metrics in metrics.values():
                    for model_metrics in horizon_metrics.values():
                        if model_metrics.accuracy_percentage > 70:  # Minimum 70% accuracy
                            return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error training model for {symbol}: {str(e)}")
            return False
    
    async def generate_ai_enhanced_signals(self, 
                                         symbols: Optional[List[str]] = None,
                                         strategies: Optional[List[str]] = None,
                                         shariah_only: bool = True,
                                         min_confidence: float = 0.6,
                                         ai_weight: float = 0.4) -> List[AIEnhancedSignal]:
        """Generate AI-enhanced signals for multiple stocks"""
        
        start_time = datetime.now()
        
        # Use provided symbols or load universe
        if symbols is None:
            symbols = await self.load_stock_universe(shariah_only)
        
        # Default strategies
        if strategies is None:
            strategies = ['multibagger', 'momentum', 'swing_trading', 'breakout', 'mean_reversion']
        
        logger.info(f"Generating AI-enhanced signals for {len(symbols)} symbols using {len(strategies)} strategies")
        
        enhanced_signals = []
        stats = {'processed': 0, 'ai_enhanced': 0, 'traditional_only': 0, 'failed': 0}
        
        # Process symbols in batches
        batch_size = 10
        for i in range(0, len(symbols), batch_size):
            batch_symbols = symbols[i:i + batch_size]
            
            # Generate signals for batch
            batch_signals = await self._process_symbol_batch(
                batch_symbols, strategies, shariah_only, min_confidence, ai_weight
            )
            
            enhanced_signals.extend(batch_signals)
            
            # Update stats
            for signal in batch_signals:
                stats['processed'] += 1
                if signal.ai_confidence_1d > 0.5:  # Has meaningful AI prediction
                    stats['ai_enhanced'] += 1
                else:
                    stats['traditional_only'] += 1
            
            # Progress update
            logger.info(f"Signal generation progress: {min(i + batch_size, len(symbols))}/{len(symbols)}")
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()
        stats['avg_processing_time'] = processing_time / len(symbols) if symbols else 0
        
        # Update global stats
        self.generation_stats.update(stats)
        
        logger.info(f"AI-enhanced signal generation complete: {len(enhanced_signals)} signals generated")
        logger.info(f"Stats: {stats['ai_enhanced']} AI-enhanced, {stats['traditional_only']} traditional-only")
        
        return enhanced_signals
    
    async def _process_symbol_batch(self, 
                                  symbols: List[str],
                                  strategies: List[str],
                                  shariah_only: bool,
                                  min_confidence: float,
                                  ai_weight: float) -> List[AIEnhancedSignal]:
        """Process a batch of symbols for signal generation"""
        
        batch_signals = []
        
        for symbol in symbols:
            try:
                # Generate traditional signals for all strategies
                traditional_signals = []
                
                for strategy in strategies:
                    try:
                        signals = self.signal_engine.generate_signals(
                            symbols=[symbol],
                            strategy_name=strategy,
                            shariah_only=shariah_only,
                            min_confidence=min_confidence
                        )
                        traditional_signals.extend(signals)
                    except Exception as e:
                        logger.warning(f"Traditional signal generation failed for {symbol} {strategy}: {str(e)}")
                
                # Generate AI predictions if model is available
                ai_prediction = None
                if symbol in self.trained_models:
                    try:
                        ai_prediction = self.ai_predictor.predict_price(symbol, days_ahead=1)
                    except Exception as e:
                        logger.warning(f"AI prediction failed for {symbol}: {str(e)}")
                
                # Combine traditional signals with AI predictions
                for traditional_signal in traditional_signals:
                    enhanced_signal = self._create_enhanced_signal(
                        traditional_signal, ai_prediction, ai_weight
                    )
                    batch_signals.append(enhanced_signal)
                
            except Exception as e:
                logger.error(f"Error processing {symbol}: {str(e)}")
                continue
        
        return batch_signals
    
    def _create_enhanced_signal(self, 
                              traditional_signal: Dict[str, Any],
                              ai_prediction: Optional[Any],
                              ai_weight: float) -> AIEnhancedSignal:
        """Create an AI-enhanced signal from traditional signal and AI prediction"""
        
        # Extract traditional signal data
        symbol = traditional_signal['symbol']
        strategy = traditional_signal['strategy']
        signal_type = traditional_signal.get('signal', 'BUY')
        traditional_confidence = traditional_signal.get('confidence', 0.5)
        price = traditional_signal.get('price', traditional_signal.get('current_price', 0))
        target_price = traditional_signal.get('target_price', price * 1.05)
        stop_loss = traditional_signal.get('stop_loss', price * 0.95)
        
        # Default AI values
        ai_prediction_1d = price
        ai_prediction_7d = price
        ai_prediction_30d = price
        ai_confidence_1d = 0.5
        ai_confidence_7d = 0.5
        ai_confidence_30d = 0.5
        ai_trend_direction = 'SIDEWAYS'
        ai_risk_score = 0.5
        ai_model_accuracy = 0.5
        
        # Use AI prediction if available
        if ai_prediction:
            ai_prediction_1d = ai_prediction.predicted_price_1d
            ai_prediction_7d = ai_prediction.predicted_price_7d
            ai_prediction_30d = ai_prediction.predicted_price_30d
            ai_confidence_1d = ai_prediction.confidence_1d
            ai_confidence_7d = ai_prediction.confidence_7d
            ai_confidence_30d = ai_prediction.confidence_30d
            ai_trend_direction = ai_prediction.trend_direction
            ai_risk_score = ai_prediction.risk_score
            ai_model_accuracy = ai_prediction.model_accuracy / 100
        
        # Calculate combined confidence
        combined_confidence = (
            (1 - ai_weight) * traditional_confidence + 
            ai_weight * ai_confidence_1d
        )
        
        # Enhanced target and stop loss using AI prediction
        if ai_prediction and ai_confidence_1d > 0.7:
            # Use AI prediction to enhance targets
            ai_change_pct = (ai_prediction_1d - price) / price
            
            if ai_change_pct > 0:  # Bullish AI prediction
                enhanced_target = max(target_price, ai_prediction_1d * 0.98)  # Slightly conservative
            else:  # Bearish AI prediction
                enhanced_target = min(target_price, price * 1.02)  # More conservative target
                
            # Adjust stop loss based on AI risk score
            risk_multiplier = 1 + (ai_risk_score * 0.5)  # Higher risk = wider stop
            enhanced_stop_loss = price * (1 - 0.05 * risk_multiplier)
        else:
            enhanced_target = target_price
            enhanced_stop_loss = stop_loss
        
        # Determine recommendation strength
        recommendation_strength = self._calculate_recommendation_strength(
            traditional_confidence, ai_confidence_1d, ai_trend_direction, combined_confidence
        )
        
        # Create enhanced signal
        return AIEnhancedSignal(
            symbol=symbol,
            strategy=strategy,
            signal=signal_type,
            confidence=traditional_confidence,
            price=price,
            target_price=target_price,
            stop_loss=stop_loss,
            ai_prediction_1d=ai_prediction_1d,
            ai_prediction_7d=ai_prediction_7d,
            ai_prediction_30d=ai_prediction_30d,
            ai_confidence_1d=ai_confidence_1d,
            ai_confidence_7d=ai_confidence_7d,
            ai_confidence_30d=ai_confidence_30d,
            ai_trend_direction=ai_trend_direction,
            ai_risk_score=ai_risk_score,
            combined_confidence=combined_confidence,
            enhanced_target=enhanced_target,
            enhanced_stop_loss=enhanced_stop_loss,
            recommendation_strength=recommendation_strength,
            generated_at=datetime.now().isoformat(),
            ai_model_accuracy=ai_model_accuracy,
            traditional_factors=traditional_signal,
            ai_factors={
                'prediction_1d': ai_prediction_1d,
                'trend': ai_trend_direction,
                'risk_score': ai_risk_score,
                'model_accuracy': ai_model_accuracy
            }
        )
    
    def _calculate_recommendation_strength(self, 
                                         traditional_confidence: float,
                                         ai_confidence: float,
                                         ai_trend: str,
                                         combined_confidence: float) -> str:
        """Calculate recommendation strength based on traditional and AI factors"""
        
        # Strong agreement between traditional and AI
        if combined_confidence > 0.8:
            if ai_trend == 'BULLISH' and traditional_confidence > 0.7:
                return 'STRONG_BUY'
            elif ai_trend == 'BEARISH' and traditional_confidence < 0.4:
                return 'STRONG_SELL'
            elif ai_trend == 'BULLISH':
                return 'BUY'
            elif ai_trend == 'BEARISH':
                return 'SELL'
        
        # Moderate confidence
        elif combined_confidence > 0.6:
            if ai_trend == 'BULLISH':
                return 'BUY'
            elif ai_trend == 'BEARISH':
                return 'SELL'
        
        # Low confidence or conflicting signals
        return 'HOLD'
    
    async def get_top_ai_enhanced_signals(self, 
                                        limit: int = 50,
                                        min_combined_confidence: float = 0.7,
                                        strategies: Optional[List[str]] = None) -> List[AIEnhancedSignal]:
        """Get top AI-enhanced signals sorted by combined confidence"""
        
        # Generate signals for entire universe
        all_signals = await self.generate_ai_enhanced_signals(
            symbols=None,  # Use entire universe
            strategies=strategies,
            shariah_only=True,
            min_confidence=0.6
        )
        
        # Filter by minimum combined confidence
        filtered_signals = [
            signal for signal in all_signals 
            if signal.combined_confidence >= min_combined_confidence
        ]
        
        # Sort by combined confidence (descending)
        sorted_signals = sorted(
            filtered_signals,
            key=lambda x: x.combined_confidence,
            reverse=True
        )
        
        # Return top signals
        return sorted_signals[:limit]
    
    def get_generation_stats(self) -> Dict[str, Any]:
        """Get signal generation statistics"""
        return {
            'generation_stats': self.generation_stats,
            'trained_models_count': len(self.trained_models),
            'stock_universe_size': len(self.stock_universe),
            'trained_models': list(self.trained_models)
        }

# Global instance
ai_enhanced_generator = AIEnhancedSignalGenerator()
