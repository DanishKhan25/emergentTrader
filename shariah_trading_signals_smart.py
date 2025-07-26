#!/usr/bin/env python3
"""
Smart Shariah-Compliant Trading Signal Generation
Uses smart batch processing for instant access to compliant stocks
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'python_backend'))

import logging
from datetime import datetime
from typing import List, Dict, Any
from services.yfinance_fetcher import YFinanceFetcher
from core.enhanced_shariah_filter_smart import SmartShariahFilter
from core.optimized_signal_generator import OptimizedSignalGenerator

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SmartShariahTradingSystem:
    """Smart trading system with instant access to Shariah-compliant stocks"""
    
    def __init__(self):
        self.fetcher = YFinanceFetcher()
        self.smart_shariah_filter = SmartShariahFilter(batch_size=50)
        self.signal_generator = OptimizedSignalGenerator(self.fetcher)
        
        logger.info("Initialized Smart Shariah Trading System")
    
    def get_compliant_stocks_instantly(self, limit: int = 50) -> List[Dict]:
        """Get Shariah-compliant stocks instantly from cache"""
        try:
            logger.info(f"Getting compliant stocks instantly (limit={limit})")
            
            # Load test stocks (you can expand this)
            test_stocks = self._load_test_stocks()
            
            # Use smart filter - will be instant if cached
            start_time = datetime.now()
            
            results = self.smart_shariah_filter.get_shariah_universe_smart(
                test_stocks, self.fetcher, force_refresh=False
            )
            
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            compliant_stocks = results['compliant_stocks'][:limit]
            
            logger.info(f"Retrieved {len(compliant_stocks)} compliant stocks in {processing_time:.3f}s")
            logger.info(f"Cache hit rate: {results['summary']['cache_usage_rate']:.1f}%")
            
            return compliant_stocks
            
        except Exception as e:
            logger.error(f"Error getting compliant stocks: {str(e)}")
            return []
    
    def generate_trading_signals(self, 
                               strategy: str = 'mean_reversion',
                               max_stocks: int = 20,
                               min_confidence: float = 0.5) -> Dict[str, Any]:
        """Generate trading signals for compliant stocks"""
        try:
            logger.info(f"Generating {strategy} signals for compliant stocks")
            
            # Step 1: Get compliant stocks instantly
            start_time = datetime.now()
            compliant_stocks = self.get_compliant_stocks_instantly(limit=max_stocks)
            compliant_time = (datetime.now() - start_time).total_seconds()
            
            if not compliant_stocks:
                return {
                    'success': False,
                    'error': 'No compliant stocks found',
                    'signals': []
                }
            
            # Step 2: Extract symbols
            symbols = [stock['symbol'] for stock in compliant_stocks]
            logger.info(f"Analyzing {len(symbols)} compliant stocks: {', '.join(symbols[:5])}...")
            
            # Step 3: Generate signals
            signal_start_time = datetime.now()
            
            if strategy == 'mean_reversion':
                signals = self.signal_generator.generate_optimized_signals('mean_reversion', symbols)
            elif strategy == 'momentum':
                signals = self.signal_generator.generate_optimized_signals('momentum', symbols)
            elif strategy == 'breakout':
                signals = self.signal_generator.generate_optimized_signals('breakout', symbols)
            elif strategy == 'value_investing':
                signals = self.signal_generator.generate_optimized_signals('value_investing', symbols)
            else:
                return {
                    'success': False,
                    'error': f'Unknown strategy: {strategy}',
                    'signals': []
                }
            
            signal_time = (datetime.now() - signal_start_time).total_seconds()
            
            # Step 4: Filter by confidence
            high_confidence_signals = [
                signal for signal in signals 
                if signal.get('confidence', 0) >= min_confidence
            ]
            
            # Step 5: Enrich with compliance data
            enriched_signals = self._enrich_signals(high_confidence_signals, compliant_stocks)
            
            # Step 6: Rank by combined score
            ranked_signals = self._rank_signals(enriched_signals)
            
            total_time = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"Generated {len(ranked_signals)} high-confidence signals in {total_time:.1f}s")
            
            return {
                'success': True,
                'strategy': strategy,
                'compliant_stocks_found': len(compliant_stocks),
                'signals_generated': len(signals),
                'high_confidence_signals': len(high_confidence_signals),
                'final_signals': len(ranked_signals),
                'signals': ranked_signals,
                'performance': {
                    'compliant_stocks_time': compliant_time,
                    'signal_generation_time': signal_time,
                    'total_time': total_time,
                    'instant_compliance_check': compliant_time < 1.0
                },
                'generation_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating signals: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'signals': []
            }
    
    def get_top_opportunities(self, max_opportunities: int = 10) -> Dict[str, Any]:
        """Get top trading opportunities across multiple strategies"""
        
        logger.info(f"Finding top {max_opportunities} trading opportunities")
        
        strategies = ['mean_reversion', 'momentum', 'breakout']
        all_signals = []
        strategy_results = {}
        
        start_time = datetime.now()
        
        for strategy in strategies:
            logger.info(f"Processing {strategy} strategy...")
            
            strategy_result = self.generate_trading_signals(
                strategy=strategy,
                max_stocks=30,
                min_confidence=0.4
            )
            
            strategy_results[strategy] = strategy_result
            
            if strategy_result['success']:
                for signal in strategy_result['signals']:
                    signal['strategy_used'] = strategy
                    all_signals.append(signal)
        
        # Find consensus signals (multiple strategies)
        consensus_signals = self._find_consensus_signals(all_signals)
        
        # Get top opportunities
        all_opportunities = consensus_signals + [
            s for s in all_signals 
            if s['symbol'] not in [cs['symbol'] for cs in consensus_signals]
        ]
        
        # Sort and limit
        all_opportunities.sort(key=lambda x: x.get('combined_score', 0), reverse=True)
        top_opportunities = all_opportunities[:max_opportunities]
        
        total_time = (datetime.now() - start_time).total_seconds()
        
        return {
            'success': True,
            'top_opportunities': top_opportunities,
            'consensus_signals': len(consensus_signals),
            'total_signals': len(all_signals),
            'strategies_used': strategies,
            'strategy_results': strategy_results,
            'processing_time': total_time,
            'analysis_time': datetime.now().isoformat()
        }
    
    def _load_test_stocks(self) -> List[Dict]:
        """Load test stocks for demonstration"""
        return [
            {'symbol': 'TCS', 'company_name': 'Tata Consultancy Services'},
            {'symbol': 'HDFCBANK', 'company_name': 'HDFC Bank'},
            {'symbol': 'RELIANCE', 'company_name': 'Reliance Industries'},
            {'symbol': 'WIPRO', 'company_name': 'Wipro Limited'},
            {'symbol': 'INFY', 'company_name': 'Infosys Limited'},
            {'symbol': 'ICICIBANK', 'company_name': 'ICICI Bank'},
            {'symbol': 'HINDUNILVR', 'company_name': 'Hindustan Unilever'},
            {'symbol': 'ITC', 'company_name': 'ITC Limited'},
            {'symbol': 'MARUTI', 'company_name': 'Maruti Suzuki'},
            {'symbol': 'ASIANPAINT', 'company_name': 'Asian Paints'},
            {'symbol': 'NESTLEIND', 'company_name': 'Nestle India'},
            {'symbol': 'HCLTECH', 'company_name': 'HCL Technologies'},
            {'symbol': 'TECHM', 'company_name': 'Tech Mahindra'},
            {'symbol': 'TITAN', 'company_name': 'Titan Company'},
            {'symbol': 'ULTRACEMCO', 'company_name': 'UltraTech Cement'}
        ]
    
    def _enrich_signals(self, signals: List[Dict], compliant_stocks: List[Dict]) -> List[Dict]:
        """Enrich signals with compliance data"""
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
                'shariah_compliant': True
            }
            
            enriched_signals.append(enriched_signal)
        
        return enriched_signals
    
    def _rank_signals(self, signals: List[Dict]) -> List[Dict]:
        """Rank signals by combined score"""
        for signal in signals:
            trading_confidence = signal.get('confidence', 0)
            compliance_score = signal.get('compliance_score', 0)
            
            # Combined score: 70% trading + 30% compliance
            combined_score = (trading_confidence * 0.7) + (compliance_score * 0.3)
            signal['combined_score'] = combined_score
        
        signals.sort(key=lambda x: x['combined_score'], reverse=True)
        return signals
    
    def _find_consensus_signals(self, all_signals: List[Dict]) -> List[Dict]:
        """Find signals that appear in multiple strategies"""
        symbol_strategies = {}
        
        for signal in all_signals:
            symbol = signal['symbol']
            if symbol not in symbol_strategies:
                symbol_strategies[symbol] = []
            symbol_strategies[symbol].append(signal)
        
        consensus_signals = []
        for symbol, signals in symbol_strategies.items():
            if len(signals) > 1:  # Multiple strategies agree
                best_signal = max(signals, key=lambda x: x.get('confidence', 0))
                best_signal['strategies_count'] = len(signals)
                best_signal['strategies_list'] = [s.get('strategy_used') for s in signals]
                consensus_signals.append(best_signal)
        
        return consensus_signals

def main():
    """Interactive demo of smart trading system"""
    
    print("⚡ Smart Shariah-Compliant Trading System")
    print("=" * 50)
    
    # Initialize system
    trading_system = SmartShariahTradingSystem()
    
    print("\nSelect an option:")
    print("1. Get compliant stocks (instant)")
    print("2. Generate mean reversion signals")
    print("3. Generate momentum signals")
    print("4. Get top trading opportunities")
    print("5. Performance benchmark")
    
    choice = input("\nEnter choice (1-5): ").strip()
    
    if choice == '1':
        print("\n⚡ Getting compliant stocks instantly...")
        start_time = datetime.now()
        
        stocks = trading_system.get_compliant_stocks_instantly(limit=15)
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        print(f"✅ Retrieved {len(stocks)} compliant stocks in {processing_time:.3f} seconds")
        
        for i, stock in enumerate(stocks[:10], 1):
            score = stock.get('compliance_score', 0)
            confidence = stock.get('confidence_level', 'unknown')
            source = stock.get('data_source', 'unknown')
            print(f"{i:2d}. {stock['symbol']:12} | {confidence:6} | {score:.2f} | {source}")
    
    elif choice == '2':
        print("\n📈 Generating mean reversion signals...")
        results = trading_system.generate_trading_signals(
            strategy='mean_reversion',
            max_stocks=20,
            min_confidence=0.4
        )
        
        if results['success']:
            perf = results['performance']
            print(f"✅ Generated {len(results['signals'])} signals:")
            print(f"   • Compliance check: {perf['compliant_stocks_time']:.3f}s")
            print(f"   • Signal generation: {perf['signal_generation_time']:.1f}s")
            print(f"   • Total time: {perf['total_time']:.1f}s")
            print(f"   • Instant compliance: {'Yes' if perf['instant_compliance_check'] else 'No'}")
            
            for i, signal in enumerate(results['signals'][:5], 1):
                conf = signal.get('confidence', 0)
                score = signal.get('combined_score', 0)
                print(f"{i}. {signal['symbol']:10} | Conf: {conf:.2f} | Score: {score:.2f}")
    
    elif choice == '3':
        print("\n🚀 Generating momentum signals...")
        results = trading_system.generate_trading_signals(
            strategy='momentum',
            max_stocks=20,
            min_confidence=0.4
        )
        
        if results['success']:
            perf = results['performance']
            print(f"✅ Generated {len(results['signals'])} signals in {perf['total_time']:.1f}s")
            
            for i, signal in enumerate(results['signals'][:5], 1):
                conf = signal.get('confidence', 0)
                score = signal.get('combined_score', 0)
                print(f"{i}. {signal['symbol']:10} | Conf: {conf:.2f} | Score: {score:.2f}")
    
    elif choice == '4':
        print("\n🏆 Finding top trading opportunities...")
        results = trading_system.get_top_opportunities(max_opportunities=10)
        
        if results['success']:
            print(f"✅ Found {len(results['top_opportunities'])} opportunities in {results['processing_time']:.1f}s")
            print(f"   • Consensus signals: {results['consensus_signals']}")
            print(f"   • Total signals: {results['total_signals']}")
            
            for i, opp in enumerate(results['top_opportunities'], 1):
                symbol = opp['symbol']
                conf = opp.get('confidence', 0)
                score = opp.get('combined_score', 0)
                strategy = opp.get('strategy_used', 'unknown')
                strategies_count = opp.get('strategies_count', 1)
                
                consensus_indicator = f"({strategies_count} strategies)" if strategies_count > 1 else ""
                print(f"{i:2d}. {symbol:10} | Score: {score:.2f} | {strategy:12} {consensus_indicator}")
    
    elif choice == '5':
        print("\n⚡ Performance Benchmark...")
        
        # Test compliance speed
        print("Testing compliance retrieval speed...")
        start_time = datetime.now()
        stocks = trading_system.get_compliant_stocks_instantly(limit=20)
        compliance_time = (datetime.now() - start_time).total_seconds()
        
        # Test signal generation speed
        print("Testing signal generation speed...")
        start_time = datetime.now()
        results = trading_system.generate_trading_signals('mean_reversion', max_stocks=15)
        signal_time = (datetime.now() - start_time).total_seconds()
        
        print(f"\n📊 Performance Results:")
        print(f"   • Compliance retrieval: {compliance_time:.3f}s ({len(stocks)} stocks)")
        print(f"   • Signal generation: {signal_time:.1f}s")
        print(f"   • Compliance speed: {len(stocks)/compliance_time:.0f} stocks/second")
        print(f"   • Overall efficiency: {'Excellent' if compliance_time < 1.0 else 'Good'}")
    
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()
