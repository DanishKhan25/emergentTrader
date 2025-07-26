#!/usr/bin/env python3
"""
Shariah-Compliant Trading Signal Generation System
Generate trading signals exclusively for Shariah-compliant stocks with comprehensive analysis
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'python_backend'))

import logging
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any
from services.yfinance_fetcher import YFinanceFetcher
from core.enhanced_shariah_filter_batched import BatchedShariahFilter
from core.optimized_signal_generator import OptimizedSignalGenerator
from core.signal_engine import SignalEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ShariahCompliantTradingSystem:
    """Complete trading system for Shariah-compliant stocks"""
    
    def __init__(self):
        self.fetcher = YFinanceFetcher()
        self.shariah_filter = BatchedShariahFilter(batch_size=50)
        self.optimized_generator = OptimizedSignalGenerator(self.fetcher)  # Pass fetcher
        self.signal_engine = SignalEngine()
        
        logger.info("Initialized Shariah-Compliant Trading System")
    
    def get_compliant_stocks(self, force_refresh: bool = False, limit: int = None) -> List[Dict]:
        """
        Get Shariah-compliant stocks (uses 3-month cache unless force_refresh=True)
        
        Args:
            force_refresh: Force fresh data instead of using cache
            limit: Limit number of stocks to return
            
        Returns:
            List of compliant stocks with compliance details
        """
        try:
            logger.info(f"Getting Shariah-compliant stocks (force_refresh={force_refresh})")
            
            # Load NSE universe (you can customize this)
            nse_stocks = self._load_nse_universe()
            
            if not nse_stocks:
                logger.error("No NSE stocks loaded")
                return []
            
            # Get compliant stocks using batched processing
            results = self.shariah_filter.get_shariah_universe_batched(
                nse_stocks, self.fetcher, force_refresh=force_refresh
            )
            
            compliant_stocks = results['compliant_stocks']
            
            # Apply limit if specified
            if limit:
                compliant_stocks = compliant_stocks[:limit]
            
            logger.info(f"Found {len(compliant_stocks)} Shariah-compliant stocks")
            
            return compliant_stocks
            
        except Exception as e:
            logger.error(f"Error getting compliant stocks: {str(e)}")
            return []
    
    def generate_signals_for_compliant_stocks(self, 
                                            strategy: str = 'mean_reversion',
                                            max_stocks: int = 50,
                                            min_confidence: float = 0.4) -> Dict[str, Any]:
        """
        Generate trading signals for Shariah-compliant stocks only
        
        Args:
            strategy: Trading strategy ('mean_reversion', 'momentum', 'breakout', 'value_investing')
            max_stocks: Maximum number of stocks to analyze
            min_confidence: Minimum signal confidence threshold
            
        Returns:
            Dictionary with signals and analysis
        """
        try:
            logger.info(f"Generating {strategy} signals for compliant stocks")
            
            # Step 1: Get compliant stocks (uses cache if available)
            compliant_stocks = self.get_compliant_stocks(force_refresh=False, limit=max_stocks)
            
            if not compliant_stocks:
                return {
                    'success': False,
                    'error': 'No compliant stocks found',
                    'signals': []
                }
            
            # Step 2: Extract symbols for signal generation
            symbols = [stock['symbol'] for stock in compliant_stocks]
            logger.info(f"Analyzing {len(symbols)} compliant stocks for {strategy} signals")
            
            # Step 3: Generate signals using optimized generator
            signals = []
            
            if strategy == 'mean_reversion':
                signals = self.optimized_generator.generate_mean_reversion_signals(symbols)
            elif strategy == 'momentum':
                signals = self.optimized_generator.generate_momentum_signals(symbols)
            elif strategy == 'breakout':
                signals = self.optimized_generator.generate_breakout_signals(symbols)
            elif strategy == 'value_investing':
                signals = self.optimized_generator.generate_value_investing_signals(symbols)
            else:
                # Fallback to signal engine
                signals = self.signal_engine.generate_signals(strategy, symbols)
            
            # Step 4: Filter signals by confidence
            high_confidence_signals = [
                signal for signal in signals 
                if signal.get('confidence', 0) >= min_confidence
            ]
            
            # Step 5: Enrich signals with compliance data
            enriched_signals = self._enrich_signals_with_compliance_data(
                high_confidence_signals, compliant_stocks
            )
            
            # Step 6: Rank signals by combined score
            ranked_signals = self._rank_signals(enriched_signals)
            
            logger.info(f"Generated {len(ranked_signals)} high-confidence {strategy} signals")
            
            return {
                'success': True,
                'strategy': strategy,
                'total_stocks_analyzed': len(symbols),
                'signals_generated': len(signals),
                'high_confidence_signals': len(high_confidence_signals),
                'final_signals': len(ranked_signals),
                'min_confidence_used': min_confidence,
                'signals': ranked_signals,
                'generation_time': datetime.now().isoformat(),
                'compliance_filter_applied': True
            }
            
        except Exception as e:
            logger.error(f"Error generating signals: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'signals': []
            }
    
    def generate_multi_strategy_signals(self, 
                                      strategies: List[str] = None,
                                      max_stocks: int = 30,
                                      min_confidence: float = 0.5) -> Dict[str, Any]:
        """
        Generate signals using multiple strategies for comprehensive analysis
        
        Args:
            strategies: List of strategies to use
            max_stocks: Maximum stocks to analyze per strategy
            min_confidence: Minimum confidence threshold
            
        Returns:
            Dictionary with multi-strategy analysis
        """
        if strategies is None:
            strategies = ['mean_reversion', 'momentum', 'breakout', 'value_investing']
        
        logger.info(f"Generating multi-strategy signals: {strategies}")
        
        all_results = {}
        combined_signals = []
        
        for strategy in strategies:
            logger.info(f"Processing strategy: {strategy}")
            
            strategy_results = self.generate_signals_for_compliant_stocks(
                strategy=strategy,
                max_stocks=max_stocks,
                min_confidence=min_confidence
            )
            
            all_results[strategy] = strategy_results
            
            if strategy_results['success']:
                # Add strategy info to each signal
                for signal in strategy_results['signals']:
                    signal['strategy_used'] = strategy
                    combined_signals.append(signal)
        
        # Find consensus signals (signals from multiple strategies)
        consensus_signals = self._find_consensus_signals(combined_signals)
        
        return {
            'success': True,
            'strategies_used': strategies,
            'individual_results': all_results,
            'combined_signals': combined_signals,
            'consensus_signals': consensus_signals,
            'total_unique_signals': len(set(s['symbol'] for s in combined_signals)),
            'consensus_count': len(consensus_signals),
            'generation_time': datetime.now().isoformat()
        }
    
    def get_top_trading_opportunities(self, 
                                    max_opportunities: int = 10,
                                    min_confidence: float = 0.6) -> Dict[str, Any]:
        """
        Get top trading opportunities from Shariah-compliant stocks
        
        Args:
            max_opportunities: Maximum number of opportunities to return
            min_confidence: Minimum confidence for opportunities
            
        Returns:
            Dictionary with top trading opportunities
        """
        logger.info(f"Finding top {max_opportunities} trading opportunities")
        
        # Generate multi-strategy signals
        multi_results = self.generate_multi_strategy_signals(
            max_stocks=50,
            min_confidence=min_confidence
        )
        
        if not multi_results['success']:
            return multi_results
        
        # Prioritize consensus signals
        opportunities = []
        
        # Add consensus signals first (highest priority)
        for signal in multi_results['consensus_signals']:
            opportunities.append({
                **signal,
                'opportunity_type': 'consensus',
                'priority': 'high'
            })
        
        # Add high-confidence individual signals
        seen_symbols = set(opp['symbol'] for opp in opportunities)
        
        for signal in multi_results['combined_signals']:
            if (signal['symbol'] not in seen_symbols and 
                signal.get('confidence', 0) >= min_confidence):
                
                opportunities.append({
                    **signal,
                    'opportunity_type': 'individual',
                    'priority': 'medium'
                })
                seen_symbols.add(signal['symbol'])
        
        # Sort by combined score and limit
        opportunities.sort(key=lambda x: x.get('combined_score', 0), reverse=True)
        top_opportunities = opportunities[:max_opportunities]
        
        return {
            'success': True,
            'top_opportunities': top_opportunities,
            'total_opportunities_found': len(opportunities),
            'consensus_opportunities': len([o for o in top_opportunities if o['opportunity_type'] == 'consensus']),
            'individual_opportunities': len([o for o in top_opportunities if o['opportunity_type'] == 'individual']),
            'min_confidence_used': min_confidence,
            'analysis_time': datetime.now().isoformat()
        }
    
    def _load_nse_universe(self) -> List[Dict]:
        """Load NSE universe (customize as needed)"""
        try:
            import pandas as pd
            df = pd.read_csv('data/nse_raw.csv')
            
            stocks = []
            for _, row in df.iterrows():
                symbol = row.get('SYMBOL', '').strip()
                series = row.get(' SERIES', '').strip()
                face_value = row.get(' FACE VALUE', 0)
                
                if (symbol and len(symbol) > 0 and 
                    series.upper() in ['EQ', 'BE', 'SM'] and
                    face_value > 0):
                    
                    stocks.append({
                        'symbol': symbol,
                        'company_name': row.get('NAME OF COMPANY', '').strip(),
                        'series': series
                    })
            
            return stocks[:200]  # Limit for faster processing during development
            
        except Exception as e:
            logger.error(f"Error loading NSE universe: {str(e)}")
            return []
    
    def _enrich_signals_with_compliance_data(self, signals: List[Dict], compliant_stocks: List[Dict]) -> List[Dict]:
        """Enrich signals with Shariah compliance data"""
        
        # Create lookup dictionary
        compliance_lookup = {stock['symbol']: stock for stock in compliant_stocks}
        
        enriched_signals = []
        
        for signal in signals:
            symbol = signal.get('symbol', '')
            compliance_data = compliance_lookup.get(symbol, {})
            
            enriched_signal = {
                **signal,
                'compliance_score': compliance_data.get('compliance_score', 0),
                'compliance_confidence': compliance_data.get('confidence_level', 'unknown'),
                'sector': compliance_data.get('sector', 'Unknown'),
                'market_cap': compliance_data.get('market_cap', 0),
                'company_name': compliance_data.get('company_name', ''),
                'shariah_compliant': True  # All signals are from compliant stocks
            }
            
            enriched_signals.append(enriched_signal)
        
        return enriched_signals
    
    def _rank_signals(self, signals: List[Dict]) -> List[Dict]:
        """Rank signals by combined score (trading + compliance)"""
        
        for signal in signals:
            trading_confidence = signal.get('confidence', 0)
            compliance_score = signal.get('compliance_score', 0)
            
            # Combined score: 70% trading confidence + 30% compliance score
            combined_score = (trading_confidence * 0.7) + (compliance_score * 0.3)
            signal['combined_score'] = combined_score
        
        # Sort by combined score
        signals.sort(key=lambda x: x['combined_score'], reverse=True)
        
        return signals
    
    def _find_consensus_signals(self, combined_signals: List[Dict]) -> List[Dict]:
        """Find signals that appear in multiple strategies"""
        
        symbol_strategies = {}
        
        # Group signals by symbol
        for signal in combined_signals:
            symbol = signal['symbol']
            strategy = signal.get('strategy_used', 'unknown')
            
            if symbol not in symbol_strategies:
                symbol_strategies[symbol] = []
            
            symbol_strategies[symbol].append(signal)
        
        # Find symbols with multiple strategies
        consensus_signals = []
        
        for symbol, signals in symbol_strategies.items():
            if len(signals) > 1:  # Multiple strategies agree
                # Take the signal with highest confidence
                best_signal = max(signals, key=lambda x: x.get('confidence', 0))
                best_signal['strategies_count'] = len(signals)
                best_signal['strategies_list'] = [s.get('strategy_used') for s in signals]
                consensus_signals.append(best_signal)
        
        return consensus_signals

def main():
    """Main function to demonstrate the system"""
    
    print("🕌 Shariah-Compliant Trading Signal Generation System")
    print("=" * 60)
    
    # Initialize system
    trading_system = ShariahCompliantTradingSystem()
    
    # Menu options
    print("\nSelect an option:")
    print("1. Get Shariah-compliant stocks")
    print("2. Generate mean reversion signals")
    print("3. Generate momentum signals") 
    print("4. Generate multi-strategy signals")
    print("5. Get top trading opportunities")
    
    choice = input("\nEnter your choice (1-5): ").strip()
    
    if choice == '1':
        print("\n📊 Getting Shariah-compliant stocks...")
        stocks = trading_system.get_compliant_stocks(limit=20)
        
        print(f"\n✅ Found {len(stocks)} compliant stocks:")
        for i, stock in enumerate(stocks[:10], 1):
            score = stock.get('compliance_score', 0)
            confidence = stock.get('confidence_level', 'unknown')
            print(f"{i:2d}. {stock['symbol']:12} | {stock['company_name'][:25]:25} | Score: {score:.2f} | {confidence}")
    
    elif choice == '2':
        print("\n📈 Generating mean reversion signals...")
        results = trading_system.generate_signals_for_compliant_stocks(
            strategy='mean_reversion',
            max_stocks=30,
            min_confidence=0.4
        )
        
        if results['success']:
            print(f"\n✅ Generated {len(results['signals'])} mean reversion signals:")
            for i, signal in enumerate(results['signals'][:5], 1):
                conf = signal.get('confidence', 0)
                score = signal.get('combined_score', 0)
                print(f"{i}. {signal['symbol']:10} | Confidence: {conf:.2f} | Combined: {score:.2f} | {signal.get('signal_type', 'N/A')}")
    
    elif choice == '3':
        print("\n🚀 Generating momentum signals...")
        results = trading_system.generate_signals_for_compliant_stocks(
            strategy='momentum',
            max_stocks=30,
            min_confidence=0.4
        )
        
        if results['success']:
            print(f"\n✅ Generated {len(results['signals'])} momentum signals:")
            for i, signal in enumerate(results['signals'][:5], 1):
                conf = signal.get('confidence', 0)
                score = signal.get('combined_score', 0)
                print(f"{i}. {signal['symbol']:10} | Confidence: {conf:.2f} | Combined: {score:.2f} | {signal.get('signal_type', 'N/A')}")
    
    elif choice == '4':
        print("\n🎯 Generating multi-strategy signals...")
        results = trading_system.generate_multi_strategy_signals(
            max_stocks=20,
            min_confidence=0.5
        )
        
        if results['success']:
            print(f"\n✅ Multi-strategy analysis complete:")
            print(f"   • Total unique signals: {results['total_unique_signals']}")
            print(f"   • Consensus signals: {results['consensus_count']}")
            
            if results['consensus_signals']:
                print(f"\n🎯 Consensus signals (multiple strategies agree):")
                for i, signal in enumerate(results['consensus_signals'][:5], 1):
                    strategies = ', '.join(signal.get('strategies_list', []))
                    conf = signal.get('confidence', 0)
                    print(f"{i}. {signal['symbol']:10} | Confidence: {conf:.2f} | Strategies: {strategies}")
    
    elif choice == '5':
        print("\n🏆 Finding top trading opportunities...")
        results = trading_system.get_top_trading_opportunities(
            max_opportunities=10,
            min_confidence=0.5
        )
        
        if results['success']:
            print(f"\n🏆 Top {len(results['top_opportunities'])} trading opportunities:")
            for i, opp in enumerate(results['top_opportunities'], 1):
                symbol = opp['symbol']
                conf = opp.get('confidence', 0)
                score = opp.get('combined_score', 0)
                opp_type = opp.get('opportunity_type', 'unknown')
                strategy = opp.get('strategy_used', 'unknown')
                
                print(f"{i:2d}. {symbol:10} | Score: {score:.2f} | Conf: {conf:.2f} | {opp_type:10} | {strategy}")
    
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()
