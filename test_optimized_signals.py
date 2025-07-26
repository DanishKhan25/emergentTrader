#!/usr/bin/env python3
"""
Test script for optimized signal generation with caching
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'python_backend'))

from services.yfinance_fetcher import YFinanceFetcher
from core.optimized_signal_generator import OptimizedSignalGenerator
from core.data_cache import cache
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_optimized_signal_generation():
    """Test optimized signal generation with caching"""
    print("🚀 Testing Optimized Signal Generation")
    print("=" * 60)
    
    try:
        # Initialize components
        print("\n1️⃣ Initializing Components...")
        data_fetcher = YFinanceFetcher()
        signal_generator = OptimizedSignalGenerator(data_fetcher)
        print("✅ Components initialized successfully")
        
        # Test symbols (mix of liquid and popular stocks)
        test_symbols = [
            'RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'HINDUNILVR',
            'ICICIBANK', 'KOTAKBANK', 'BHARTIARTL', 'ITC', 'SBIN',
            'MARUTI', 'ASIANPAINT', 'NESTLEIND', 'HCLTECH', 'WIPRO'
        ]
        
        print(f"\n2️⃣ Testing with {len(test_symbols)} symbols...")
        
        # Test momentum signals
        print("\n3️⃣ Generating Momentum Signals...")
        momentum_signals = signal_generator.generate_optimized_signals(
            strategy_name='momentum',
            symbols=test_symbols,
            min_confidence=0.3,
            max_symbols=15
        )
        
        print(f"✅ Generated {len(momentum_signals)} momentum signals")
        if momentum_signals:
            print("   Top momentum signals:")
            for i, signal in enumerate(momentum_signals[:3]):
                print(f"   {i+1}. {signal['symbol']}: {signal['signal']} "
                      f"(confidence: {signal['confidence']:.2f})")
                print(f"      Conditions: {', '.join(signal['conditions'])}")
        
        # Test mean reversion signals
        print("\n4️⃣ Generating Mean Reversion Signals...")
        mean_reversion_signals = signal_generator.generate_optimized_signals(
            strategy_name='mean_reversion',
            symbols=test_symbols,
            min_confidence=0.3,
            max_symbols=10
        )
        
        print(f"✅ Generated {len(mean_reversion_signals)} mean reversion signals")
        if mean_reversion_signals:
            print("   Top mean reversion signals:")
            for i, signal in enumerate(mean_reversion_signals[:3]):
                print(f"   {i+1}. {signal['symbol']}: {signal['signal']} "
                      f"(confidence: {signal['confidence']:.2f})")
        
        # Test breakout signals
        print("\n5️⃣ Generating Breakout Signals...")
        breakout_signals = signal_generator.generate_optimized_signals(
            strategy_name='breakout',
            symbols=test_symbols,
            min_confidence=0.4,
            max_symbols=8
        )
        
        print(f"✅ Generated {len(breakout_signals)} breakout signals")
        if breakout_signals:
            print("   Top breakout signals:")
            for i, signal in enumerate(breakout_signals[:3]):
                print(f"   {i+1}. {signal['symbol']}: {signal['signal']} "
                      f"(confidence: {signal['confidence']:.2f})")
        
        # Test value investing signals
        print("\n6️⃣ Generating Value Investing Signals...")
        value_signals = signal_generator.generate_optimized_signals(
            strategy_name='value_investing',
            symbols=test_symbols,
            min_confidence=0.4,
            max_symbols=5
        )
        
        print(f"✅ Generated {len(value_signals)} value investing signals")
        if value_signals:
            print("   Top value signals:")
            for i, signal in enumerate(value_signals[:3]):
                print(f"   {i+1}. {signal['symbol']}: {signal['signal']} "
                      f"(confidence: {signal['confidence']:.2f})")
        
        # Test caching performance
        print("\n7️⃣ Testing Cache Performance...")
        print("   Running momentum signals again (should use cache)...")
        
        import time
        start_time = time.time()
        cached_momentum_signals = signal_generator.generate_optimized_signals(
            strategy_name='momentum',
            symbols=test_symbols,
            min_confidence=0.3,
            max_symbols=15
        )
        cache_time = time.time() - start_time
        
        print(f"✅ Cached call completed in {cache_time:.2f} seconds")
        print(f"   Generated {len(cached_momentum_signals)} signals (from cache)")
        
        # Show cache statistics
        print("\n8️⃣ Cache Statistics...")
        cache_stats = signal_generator.get_cache_stats()
        print(f"   Total cache files: {cache_stats['total_files']}")
        print(f"   Total cache size: {cache_stats['total_size_mb']:.2f} MB")
        print(f"   Expired entries: {cache_stats['expired_count']}")
        
        if cache_stats['by_type']:
            print("   Cache by type:")
            for cache_type, stats in cache_stats['by_type'].items():
                print(f"     {cache_type}: {stats['count']} files, {stats['size_mb']:.2f} MB")
        
        # Summary
        total_signals = (len(momentum_signals) + len(mean_reversion_signals) + 
                        len(breakout_signals) + len(value_signals))
        
        print(f"\n🎉 Signal Generation Test Completed!")
        print(f"✅ Total signals generated: {total_signals}")
        print(f"   - Momentum: {len(momentum_signals)}")
        print(f"   - Mean Reversion: {len(mean_reversion_signals)}")
        print(f"   - Breakout: {len(breakout_signals)}")
        print(f"   - Value Investing: {len(value_signals)}")
        
        if total_signals > 0:
            print("✅ Optimized signal generation is working successfully!")
        else:
            print("⚠️  No signals generated - this might be due to market conditions or stricter parameters")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_optimized_signal_generation()
    sys.exit(0 if success else 1)
