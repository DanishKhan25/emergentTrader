#!/usr/bin/env python3
"""
Live Signal Generation - Practical ML-Enhanced Trading Signals
Generate actionable trading signals with optimized ML thresholds
"""

import sys
import os
from datetime import datetime
import json

# Add python_backend to path
sys.path.append('python_backend')

def main():
    """Generate live trading signals with practical settings"""
    print("🚀" + "="*60 + "🚀")
    print("📈  LIVE ML-ENHANCED TRADING SIGNALS  📈")
    print("🚀" + "="*60 + "🚀")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        from core.ml_enhanced_signal_engine import MLEnhancedSignalEngine
        
        print("\n🤖 Initializing ML-Enhanced Signal Engine...")
        engine = MLEnhancedSignalEngine(enable_ml=True)
        
        print("📊 Analyzing market conditions...")
        market_context = engine.get_market_context()
        
        print(f"Market Regime: {market_context['regime']} | Volatility: {market_context['volatility']:.1%}")
        
        print("\n🎯 Generating ML-enhanced signals with practical thresholds...")
        
        # Use practical settings for live trading
        signals = engine.generate_ml_enhanced_signals(
            shariah_only=True,
            max_symbols=50,  # Larger universe
            min_ml_probability=0.4  # Lower threshold for more signals
        )
        
        print(f"\n📈 GENERATED {len(signals)} ML-ENHANCED SIGNALS")
        
        if signals:
            # Sort by ML probability
            sorted_signals = sorted(signals, 
                                  key=lambda x: x.get('ml_probability', x.get('confidence', 0)), 
                                  reverse=True)
            
            print("\n🏆 TOP TRADING OPPORTUNITIES:")
            print("="*70)
            
            for i, signal in enumerate(sorted_signals[:15], 1):  # Top 15
                symbol = signal['symbol']
                signal_type = signal.get('signal_type', 'BUY')
                entry_price = signal.get('entry_price', signal.get('current_price', 0))
                strategy = signal.get('strategy', 'consensus')
                
                # ML data
                ml_prob = signal.get('ml_probability', 0)
                ml_rec = signal.get('ml_recommendation', 'N/A')
                quality = signal.get('ml_quality_score', 'N/A')
                
                print(f"\n{i:2d}. {symbol} - {signal_type} Signal")
                print(f"    💰 Entry Price: ₹{entry_price:,.2f}")
                print(f"    📊 Strategy: {strategy}")
                print(f"    🤖 ML Probability: {ml_prob:.1%}")
                print(f"    🎯 ML Recommendation: {ml_rec}")
                print(f"    ⭐ Quality: {quality}")
                
                # Targets and stops
                if 'target_price' in signal:
                    upside = (signal['target_price'] / entry_price - 1) * 100
                    print(f"    🎯 Target: ₹{signal['target_price']:,.2f} (+{upside:.1f}%)")
                
                if 'stop_loss' in signal:
                    downside = (signal['stop_loss'] / entry_price - 1) * 100
                    print(f"    🛡️  Stop Loss: ₹{signal['stop_loss']:,.2f} ({downside:.1f}%)")
                
                print(f"    ✅ Shariah: {'Yes' if signal.get('shariah_compliant') else 'No'}")
            
            # Save to file
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"live_signals_{timestamp}.json"
            
            with open(filename, 'w') as f:
                json.dump(sorted_signals, f, indent=2, default=str)
            
            print(f"\n💾 Signals saved to: {filename}")
            
            # Statistics
            print(f"\n📊 SIGNAL STATISTICS:")
            print("="*40)
            
            ml_enhanced = sum(1 for s in signals if s.get('ml_enhanced'))
            avg_ml_prob = sum(s.get('ml_probability', 0) for s in signals) / len(signals)
            
            print(f"Total Signals: {len(signals)}")
            print(f"ML Enhanced: {ml_enhanced} ({ml_enhanced/len(signals)*100:.1f}%)")
            print(f"Average ML Probability: {avg_ml_prob:.1%}")
            
            # Quality breakdown
            quality_counts = {}
            for signal in signals:
                quality = signal.get('ml_quality_score', 'UNKNOWN')
                quality_counts[quality] = quality_counts.get(quality, 0) + 1
            
            print(f"\nQuality Distribution:")
            for quality, count in quality_counts.items():
                print(f"  {quality}: {count} signals ({count/len(signals)*100:.1f}%)")
            
            # Strategy breakdown
            strategy_counts = {}
            for signal in signals:
                strategy = signal.get('strategy', 'unknown')
                strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1
            
            print(f"\nStrategy Distribution:")
            for strategy, count in strategy_counts.items():
                print(f"  {strategy}: {count} signals")
            
        else:
            print("\n⚠️  No signals generated with current settings")
            print("Try running with even lower thresholds or check market conditions")
        
        print(f"\n🎯 TRADING RECOMMENDATIONS:")
        print("="*40)
        print("1. Focus on signals with ML Probability > 50%")
        print("2. Prioritize HIGH and MEDIUM quality scores")
        print("3. Consider position sizing based on ML confidence")
        print("4. Always use stop losses for risk management")
        print("5. Monitor signals regularly for updates")
        
        print(f"\n📱 API Access:")
        print("Start API server: python python_backend/ml_enhanced_api_handler.py")
        print("Then access: http://localhost:8000")
        
        print(f"\n🚀 SYSTEM STATUS: READY FOR LIVE TRADING! 🚀")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("Check system requirements and try again")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
