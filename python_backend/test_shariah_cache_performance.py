#!/usr/bin/env python3
"""
Performance test for cached Shariah universe functionality
Tests the improvement in speed when using cached universe vs full processing
"""

import sys
import os
import time
import logging
from datetime import datetime

# Add the python_backend directory to the path
sys.path.append(os.path.dirname(__file__))

from core.enhanced_signal_engine import EnhancedSignalEngine

def test_shariah_cache_performance():
    """Test the performance improvement with cached Shariah universe"""
    
    print("=" * 80)
    print("🚀 TESTING SHARIAH UNIVERSE CACHE PERFORMANCE")
    print("=" * 80)
    
    # Set up logging to suppress verbose output
    logging.basicConfig(level=logging.WARNING)
    
    try:
        # Initialize enhanced signal engine
        print("\n1️⃣ Initializing Enhanced Signal Engine...")
        engine = EnhancedSignalEngine()
        
        # Test 1: First call (cache miss - should be slow)
        print("\n2️⃣ First Call (Cache Miss - Expected to be slow):")
        start_time = time.time()
        shariah_stocks_1 = engine.get_shariah_universe(force_refresh=False)
        first_call_time = time.time() - start_time
        print(f"   ⏱️  Time taken: {first_call_time:.2f} seconds")
        print(f"   📊 Found {len(shariah_stocks_1)} Shariah compliant stocks")
        
        # Test 2: Second call (cache hit - should be fast)
        print("\n3️⃣ Second Call (Cache Hit - Expected to be fast):")
        start_time = time.time()
        shariah_stocks_2 = engine.get_shariah_universe(force_refresh=False)
        second_call_time = time.time() - start_time
        print(f"   ⏱️  Time taken: {second_call_time:.2f} seconds")
        print(f"   📊 Found {len(shariah_stocks_2)} Shariah compliant stocks")
        
        # Test 3: Third call (cache hit - should be fast)
        print("\n4️⃣ Third Call (Cache Hit - Should be fast):")
        start_time = time.time()
        shariah_stocks_3 = engine.get_shariah_universe(force_refresh=False)
        third_call_time = time.time() - start_time
        print(f"   ⏱️  Time taken: {third_call_time:.2f} seconds")
        print(f"   📊 Found {len(shariah_stocks_3)} Shariah compliant stocks")
        
        # Test 4: Force refresh (should be slow again)
        print("\n5️⃣ Force Refresh Call (Expected to be slow):")
        start_time = time.time()
        shariah_stocks_4 = engine.get_shariah_universe(force_refresh=True)
        force_refresh_time = time.time() - start_time
        print(f"   ⏱️  Time taken: {force_refresh_time:.2f} seconds")
        print(f"   📊 Found {len(shariah_stocks_4)} Shariah compliant stocks")
        
        # Performance Analysis
        print("\n" + "=" * 80)
        print("📈 PERFORMANCE ANALYSIS")
        print("=" * 80)
        
        # Calculate improvements
        if first_call_time > 0:
            cache_improvement_2 = ((first_call_time - second_call_time) / first_call_time) * 100
            cache_improvement_3 = ((first_call_time - third_call_time) / first_call_time) * 100
        else:
            cache_improvement_2 = 0
            cache_improvement_3 = 0
        
        print(f"📊 First Call (Cache Miss):     {first_call_time:.3f}s")
        print(f"📊 Second Call (Cache Hit):     {second_call_time:.3f}s ({cache_improvement_2:.1f}% faster)")
        print(f"📊 Third Call (Cache Hit):      {third_call_time:.3f}s ({cache_improvement_3:.1f}% faster)")
        print(f"📊 Force Refresh:               {force_refresh_time:.3f}s")
        
        # Speed comparison
        if second_call_time > 0:
            speed_multiplier = first_call_time / second_call_time
            print(f"🚀 Cache Hit Speed Improvement: {speed_multiplier:.1f}x faster")
        
        # Consistency check
        print(f"\n🔍 Data Consistency Check:")
        print(f"   First call stocks:  {len(shariah_stocks_1)}")
        print(f"   Second call stocks: {len(shariah_stocks_2)}")
        print(f"   Third call stocks:  {len(shariah_stocks_3)}")
        print(f"   Force refresh stocks: {len(shariah_stocks_4)}")
        
        # Check if results are consistent
        consistent = (len(shariah_stocks_1) == len(shariah_stocks_2) == 
                     len(shariah_stocks_3) == len(shariah_stocks_4))
        print(f"   ✅ Results consistent: {consistent}")
        
        # Test consensus signal generation with cached universe
        print("\n6️⃣ Testing Consensus Signal Generation with Cached Universe:")
        test_symbols = ['RELIANCE', 'TCS', 'INFY']
        
        start_time = time.time()
        consensus_signals = engine.generate_consensus_signals(
            symbols=test_symbols,
            shariah_only=True,
            max_symbols=3
        )
        consensus_time = time.time() - start_time
        
        print(f"   ⏱️  Consensus generation time: {consensus_time:.3f}s")
        print(f"   📈 Generated {len(consensus_signals)} consensus signals")
        
        print("\n" + "=" * 80)
        print("✅ SHARIAH CACHE PERFORMANCE TEST COMPLETED!")
        print("=" * 80)
        
        # Summary
        print(f"\n🎯 PERFORMANCE SUMMARY:")
        if cache_improvement_2 > 50:
            print(f"   • Cache Performance: ✅ EXCELLENT ({cache_improvement_2:.1f}% improvement)")
        elif cache_improvement_2 > 20:
            print(f"   • Cache Performance: ✅ GOOD ({cache_improvement_2:.1f}% improvement)")
        else:
            print(f"   • Cache Performance: ⚠️  NEEDS IMPROVEMENT ({cache_improvement_2:.1f}% improvement)")
        
        print(f"   • Data Consistency: {'✅ PASSED' if consistent else '❌ FAILED'}")
        print(f"   • Cache Hit Speed: {speed_multiplier:.1f}x faster than cache miss")
        
        return True
        
    except Exception as e:
        print(f"\n❌ PERFORMANCE TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_shariah_cache_performance()
    sys.exit(0 if success else 1)
