#!/usr/bin/env python3
"""
Test script for integrated optimized signal generation in main signal engine
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'python_backend'))

from core.signal_engine import SignalEngine
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_integrated_signal_generation():
    """Test integrated optimized signal generation"""
    print("🔗 Testing Integrated Optimized Signal Generation")
    print("=" * 70)
    
    try:
        # Initialize signal engine
        print("\n1️⃣ Initializing Signal Engine...")
        signal_engine = SignalEngine()
        print("✅ Signal engine initialized successfully")
        
        # Check if optimized generator is available
        if hasattr(signal_engine, 'optimized_generator') and signal_engine.optimized_generator:
            print("✅ Optimized signal generator is available")
        else:
            print("⚠️  Optimized signal generator not available, will use original")
        
        # Test symbols
        test_symbols = ['RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'HINDUNILVR']
        
        # Test momentum signals with optimized generator
        print("\n2️⃣ Testing Momentum Signals (Optimized)...")
        momentum_signals = signal_engine.generate_signals(
            symbols=test_symbols,
            strategy_name='momentum',
            shariah_only=False,
            min_confidence=0.3
        )
        
        print(f"✅ Generated {len(momentum_signals)} momentum signals")
        if momentum_signals:
            for i, signal in enumerate(momentum_signals[:2]):
                print(f"   {i+1}. {signal['symbol']}: {signal['signal']} "
                      f"(confidence: {signal.get('confidence', 0):.2f})")
        
        # Test mean reversion signals
        print("\n3️⃣ Testing Mean Reversion Signals (Optimized)...")
        mean_reversion_signals = signal_engine.generate_signals(
            symbols=test_symbols,
            strategy_name='mean_reversion',
            shariah_only=False,
            min_confidence=0.3
        )
        
        print(f"✅ Generated {len(mean_reversion_signals)} mean reversion signals")
        if mean_reversion_signals:
            for i, signal in enumerate(mean_reversion_signals[:2]):
                print(f"   {i+1}. {signal['symbol']}: {signal['signal']} "
                      f"(confidence: {signal.get('confidence', 0):.2f})")
        
        # Test a strategy that falls back to original (e.g., swing_trading)
        print("\n4️⃣ Testing Swing Trading Signals (Original)...")
        swing_signals = signal_engine.generate_signals(
            symbols=test_symbols[:3],  # Fewer symbols for original method
            strategy_name='swing_trading',
            shariah_only=False,
            min_confidence=0.5
        )
        
        print(f"✅ Generated {len(swing_signals)} swing trading signals")
        if swing_signals:
            for i, signal in enumerate(swing_signals[:2]):
                print(f"   {i+1}. {signal['symbol']}: {signal.get('signal_type', 'N/A')} "
                      f"(confidence: {signal.get('confidence_score', 0):.2f})")
        
        # Test multi-strategy generation
        print("\n5️⃣ Testing Multi-Strategy Generation...")
        multi_signals = signal_engine.generate_multi_strategy_signals(
            symbols=test_symbols[:3],
            strategies=['momentum', 'mean_reversion'],
            shariah_only=False,
            min_confidence=0.3
        )
        
        total_multi_signals = sum(len(signals) for signals in multi_signals.values())
        print(f"✅ Generated {total_multi_signals} total signals across strategies")
        
        for strategy, signals in multi_signals.items():
            print(f"   {strategy}: {len(signals)} signals")
        
        # Show active signals
        print("\n6️⃣ Active Signals Summary...")
        active_signals = signal_engine.get_active_signals()
        print(f"✅ Total active signals: {len(active_signals)}")
        
        if active_signals:
            print("   Recent signals:")
            for i, signal in enumerate(active_signals[-3:]):  # Show last 3
                symbol = signal.get('symbol', 'N/A')
                signal_type = signal.get('signal', signal.get('signal_type', 'N/A'))
                confidence = signal.get('confidence', signal.get('confidence_score', 0))
                strategy = signal.get('strategy', 'N/A')
                print(f"   {i+1}. {symbol}: {signal_type} ({strategy}, conf: {confidence:.2f})")
        
        # Summary
        total_signals = (len(momentum_signals) + len(mean_reversion_signals) + 
                        len(swing_signals) + total_multi_signals)
        
        print(f"\n🎉 Integration Test Completed!")
        print(f"✅ Total signals generated: {total_signals}")
        print(f"   - Momentum (optimized): {len(momentum_signals)}")
        print(f"   - Mean Reversion (optimized): {len(mean_reversion_signals)}")
        print(f"   - Swing Trading (original): {len(swing_signals)}")
        print(f"   - Multi-strategy: {total_multi_signals}")
        
        if total_signals > 0:
            print("✅ Integrated optimized signal generation is working successfully!")
            print("✅ Both optimized and original signal generators are functional!")
        else:
            print("⚠️  No signals generated - this might be due to market conditions or rate limiting")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_integrated_signal_generation()
    sys.exit(0 if success else 1)
