"""
Consensus Engine - Multi-Strategy Signal Aggregation and Consensus Building
Combines signals from all 10 trading strategies to generate high-confidence consensus signals
"""

import sys
import os
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from collections import Counter
import numpy as np

# Add the python_backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

logger = logging.getLogger(__name__)

class ConsensusEngine:
    def __init__(self, signal_engine):
        """
        Initialize consensus engine with reference to main signal engine
        
        Args:
            signal_engine: Instance of SignalEngine with all strategies
        """
        self.signal_engine = signal_engine
        
        # Strategy weights based on historical performance and market conditions
        self.strategy_weights = {
            'momentum': 0.15,           # Strong in trending markets
            'mean_reversion': 0.12,     # Good in choppy markets
            'breakout': 0.13,           # Excellent for capturing trends
            'value_investing': 0.11,    # Long-term stability
            'swing_trading': 0.10,      # Medium-term opportunities
            'multibagger': 0.08,        # High-growth potential
            'fundamental_growth': 0.09, # Quality companies
            'sector_rotation': 0.07,    # Market cycle awareness
            'low_volatility': 0.08,     # Risk management
            'pivot_cpr': 0.07          # Technical precision
        }
        
        # Minimum number of strategies that must agree for a consensus signal
        self.min_consensus_strategies = 3
        
        # Confidence thresholds
        self.high_confidence_threshold = 0.75
        self.medium_confidence_threshold = 0.60
        self.low_confidence_threshold = 0.45
        
    def generate_consensus_signals(self, 
                                 symbols: Optional[List[str]] = None,
                                 shariah_only: bool = True,
                                 max_symbols: int = 50,
                                 min_strategy_confidence: float = 0.5) -> List[Dict]:
        """
        Generate consensus signals by combining all strategy outputs
        
        Args:
            symbols: List of symbols to analyze (None for auto-selection)
            shariah_only: Whether to use only Shariah compliant stocks
            max_symbols: Maximum number of symbols to process
            min_strategy_confidence: Minimum confidence for individual strategy signals
            
        Returns:
            List of consensus signals with aggregated confidence scores
        """
        try:
            logger.info("Starting consensus signal generation...")
            
            # Get symbol universe
            if symbols is None:
                if shariah_only:
                    symbols = self.signal_engine.get_shariah_universe()
                else:
                    nse_stocks = self.signal_engine.data_fetcher.get_nse_universe()
                    symbols = [stock['symbol'] for stock in nse_stocks]
            
            # Limit symbols for performance
            symbols = symbols[:max_symbols]
            logger.info(f"Processing {len(symbols)} symbols for consensus signals")
            
            # Generate signals from all strategies
            all_strategy_signals = self._generate_all_strategy_signals(
                symbols, shariah_only, min_strategy_confidence
            )
            
            # Build consensus signals
            consensus_signals = self._build_consensus_signals(all_strategy_signals)
            
            # Rank and filter consensus signals
            final_signals = self._rank_and_filter_signals(consensus_signals)
            
            logger.info(f"Generated {len(final_signals)} consensus signals")
            return final_signals
            
        except Exception as e:
            logger.error(f"Error generating consensus signals: {str(e)}")
            return []
    
    def _generate_all_strategy_signals(self, 
                                     symbols: List[str], 
                                     shariah_only: bool,
                                     min_confidence: float) -> Dict[str, Dict[str, Dict]]:
        """
        Generate signals from all strategies for all symbols
        
        Returns:
            Nested dict: {symbol: {strategy: signal_data}}
        """
        all_signals = {}
        
        # Get available strategies
        strategies = self.signal_engine.get_available_strategies()
        
        logger.info(f"Generating signals from {len(strategies)} strategies")
        
        for strategy_name in strategies:
            try:
                logger.info(f"Generating {strategy_name} signals...")
                
                # Generate signals for this strategy
                strategy_signals = self.signal_engine.generate_signals(
                    symbols=symbols,
                    strategy_name=strategy_name,
                    shariah_only=shariah_only,
                    min_confidence=min_confidence
                )
                
                # Organize by symbol
                for signal in strategy_signals:
                    symbol = signal['symbol']
                    if symbol not in all_signals:
                        all_signals[symbol] = {}
                    
                    all_signals[symbol][strategy_name] = signal
                    
                logger.info(f"Generated {len(strategy_signals)} {strategy_name} signals")
                
            except Exception as e:
                logger.error(f"Error generating {strategy_name} signals: {str(e)}")
                continue
        
        return all_signals
    
    def _build_consensus_signals(self, all_strategy_signals: Dict[str, Dict[str, Dict]]) -> List[Dict]:
        """
        Build consensus signals from individual strategy signals
        
        Args:
            all_strategy_signals: {symbol: {strategy: signal_data}}
            
        Returns:
            List of consensus signals
        """
        consensus_signals = []
        
        for symbol, strategy_signals in all_strategy_signals.items():
            try:
                # Need minimum number of strategies to agree
                if len(strategy_signals) < self.min_consensus_strategies:
                    continue
                
                # Analyze signal consensus
                consensus_data = self._analyze_signal_consensus(symbol, strategy_signals)
                
                if consensus_data:
                    consensus_signals.append(consensus_data)
                    
            except Exception as e:
                logger.error(f"Error building consensus for {symbol}: {str(e)}")
                continue
        
        return consensus_signals
    
    def _analyze_signal_consensus(self, symbol: str, strategy_signals: Dict[str, Dict]) -> Optional[Dict]:
        """
        Analyze consensus among strategy signals for a single symbol
        
        Args:
            symbol: Stock symbol
            strategy_signals: {strategy_name: signal_data}
            
        Returns:
            Consensus signal data or None if no consensus
        """
        try:
            # Count signal types
            signal_types = [signal['signal_type'] for signal in strategy_signals.values()]
            signal_counter = Counter(signal_types)
            
            # Determine consensus signal type
            if len(signal_counter) == 0:
                return None
            
            # Get most common signal type
            consensus_signal_type = signal_counter.most_common(1)[0][0]
            consensus_count = signal_counter[consensus_signal_type]
            
            # Check if we have enough agreement
            total_signals = len(strategy_signals)
            agreement_ratio = consensus_count / total_signals
            
            if agreement_ratio < 0.5:  # Less than 50% agreement
                return None
            
            # Calculate weighted confidence score
            weighted_confidence = self._calculate_weighted_confidence(
                strategy_signals, consensus_signal_type
            )
            
            # Get consensus price targets
            price_data = self._calculate_consensus_prices(
                strategy_signals, consensus_signal_type
            )
            
            # Build consensus signal
            consensus_signal = {
                'signal_id': str(uuid.uuid4()),
                'symbol': symbol,
                'signal_type': consensus_signal_type,
                'strategy': 'consensus',
                'consensus_confidence': weighted_confidence,
                'agreement_ratio': agreement_ratio,
                'supporting_strategies': consensus_count,
                'total_strategies': total_signals,
                'entry_price': price_data['entry_price'],
                'target_price': price_data['target_price'],
                'stop_loss': price_data['stop_loss'],
                'generated_at': datetime.now().isoformat(),
                'strategy_breakdown': self._get_strategy_breakdown(strategy_signals),
                'shariah_compliant': strategy_signals[list(strategy_signals.keys())[0]].get('shariah_compliant', False),
                'consensus_reason': self._generate_consensus_reason(
                    strategy_signals, consensus_signal_type, agreement_ratio
                )
            }
            
            return consensus_signal
            
        except Exception as e:
            logger.error(f"Error analyzing consensus for {symbol}: {str(e)}")
            return None
    
    def _calculate_weighted_confidence(self, 
                                     strategy_signals: Dict[str, Dict], 
                                     consensus_signal_type: str) -> float:
        """
        Calculate weighted confidence score based on strategy weights and individual confidences
        """
        try:
            total_weight = 0
            weighted_sum = 0
            
            for strategy_name, signal in strategy_signals.items():
                if signal['signal_type'] == consensus_signal_type:
                    strategy_weight = self.strategy_weights.get(strategy_name, 0.1)
                    signal_confidence = signal.get('confidence_score', 0.5)
                    
                    weighted_sum += strategy_weight * signal_confidence
                    total_weight += strategy_weight
            
            if total_weight == 0:
                return 0.5
            
            return min(weighted_sum / total_weight, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating weighted confidence: {str(e)}")
            return 0.5
    
    def _calculate_consensus_prices(self, 
                                  strategy_signals: Dict[str, Dict], 
                                  consensus_signal_type: str) -> Dict[str, float]:
        """
        Calculate consensus entry, target, and stop loss prices
        """
        try:
            entry_prices = []
            target_prices = []
            stop_losses = []
            
            for strategy_name, signal in strategy_signals.items():
                if signal['signal_type'] == consensus_signal_type:
                    entry_prices.append(signal.get('entry_price', 0))
                    target_prices.append(signal.get('target_price', 0))
                    stop_losses.append(signal.get('stop_loss', 0))
            
            # Use median for more robust consensus
            return {
                'entry_price': np.median(entry_prices) if entry_prices else 0,
                'target_price': np.median(target_prices) if target_prices else 0,
                'stop_loss': np.median(stop_losses) if stop_losses else 0
            }
            
        except Exception as e:
            logger.error(f"Error calculating consensus prices: {str(e)}")
            return {'entry_price': 0, 'target_price': 0, 'stop_loss': 0}
    
    def _get_strategy_breakdown(self, strategy_signals: Dict[str, Dict]) -> Dict[str, Dict]:
        """
        Get detailed breakdown of each strategy's contribution
        """
        breakdown = {}
        
        for strategy_name, signal in strategy_signals.items():
            breakdown[strategy_name] = {
                'signal_type': signal['signal_type'],
                'confidence': signal.get('confidence_score', 0),
                'weight': self.strategy_weights.get(strategy_name, 0.1),
                'entry_price': signal.get('entry_price', 0),
                'reason': signal.get('reason', 'No reason provided')
            }
        
        return breakdown
    
    def _generate_consensus_reason(self, 
                                 strategy_signals: Dict[str, Dict], 
                                 consensus_signal_type: str, 
                                 agreement_ratio: float) -> str:
        """
        Generate human-readable reason for consensus signal
        """
        try:
            supporting_strategies = [
                name for name, signal in strategy_signals.items() 
                if signal['signal_type'] == consensus_signal_type
            ]
            
            agreement_level = "Strong" if agreement_ratio >= 0.8 else "Moderate" if agreement_ratio >= 0.6 else "Weak"
            
            reason = f"{agreement_level} consensus {consensus_signal_type} signal from {len(supporting_strategies)} strategies: "
            reason += ", ".join(supporting_strategies[:3])  # Show first 3 strategies
            
            if len(supporting_strategies) > 3:
                reason += f" and {len(supporting_strategies) - 3} others"
            
            return reason
            
        except Exception as e:
            logger.error(f"Error generating consensus reason: {str(e)}")
            return f"Consensus {consensus_signal_type} signal"
    
    def _rank_and_filter_signals(self, consensus_signals: List[Dict]) -> List[Dict]:
        """
        Rank consensus signals by quality and filter top signals
        """
        try:
            # Calculate composite score for ranking
            for signal in consensus_signals:
                confidence = signal['consensus_confidence']
                agreement = signal['agreement_ratio']
                strategy_count = signal['supporting_strategies']
                
                # Composite score combining multiple factors
                composite_score = (
                    confidence * 0.4 +           # 40% confidence weight
                    agreement * 0.3 +            # 30% agreement weight
                    (strategy_count / 10) * 0.3  # 30% strategy count weight
                )
                
                signal['composite_score'] = min(composite_score, 1.0)
                signal['quality_tier'] = self._determine_quality_tier(composite_score)
            
            # Sort by composite score (highest first)
            consensus_signals.sort(key=lambda x: x['composite_score'], reverse=True)
            
            # Filter by minimum quality
            filtered_signals = [
                signal for signal in consensus_signals 
                if signal['composite_score'] >= self.low_confidence_threshold
            ]
            
            # Limit to top signals
            return filtered_signals[:20]  # Top 20 consensus signals
            
        except Exception as e:
            logger.error(f"Error ranking and filtering signals: {str(e)}")
            return consensus_signals
    
    def _determine_quality_tier(self, composite_score: float) -> str:
        """Determine quality tier based on composite score"""
        if composite_score >= self.high_confidence_threshold:
            return "HIGH"
        elif composite_score >= self.medium_confidence_threshold:
            return "MEDIUM"
        else:
            return "LOW"
    
    def get_consensus_summary(self, consensus_signals: List[Dict]) -> Dict:
        """
        Generate summary statistics for consensus signals
        """
        try:
            if not consensus_signals:
                return {'error': 'No consensus signals to summarize'}
            
            # Signal type distribution
            signal_types = Counter([s['signal_type'] for s in consensus_signals])
            
            # Quality tier distribution
            quality_tiers = Counter([s['quality_tier'] for s in consensus_signals])
            
            # Average metrics
            avg_confidence = np.mean([s['consensus_confidence'] for s in consensus_signals])
            avg_agreement = np.mean([s['agreement_ratio'] for s in consensus_signals])
            avg_strategies = np.mean([s['supporting_strategies'] for s in consensus_signals])
            
            # Top strategies by participation
            all_strategies = []
            for signal in consensus_signals:
                all_strategies.extend(signal['strategy_breakdown'].keys())
            strategy_participation = Counter(all_strategies)
            
            return {
                'total_consensus_signals': len(consensus_signals),
                'signal_type_distribution': dict(signal_types),
                'quality_tier_distribution': dict(quality_tiers),
                'average_confidence': round(avg_confidence, 3),
                'average_agreement_ratio': round(avg_agreement, 3),
                'average_supporting_strategies': round(avg_strategies, 1),
                'top_participating_strategies': dict(strategy_participation.most_common(5)),
                'high_quality_signals': len([s for s in consensus_signals if s['quality_tier'] == 'HIGH']),
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating consensus summary: {str(e)}")
            return {'error': str(e)}

# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # This would be used with the main SignalEngine
    print("Consensus Engine created successfully!")
    print("Use with SignalEngine instance to generate multi-strategy consensus signals")
