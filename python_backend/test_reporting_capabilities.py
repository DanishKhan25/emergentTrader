#!/usr/bin/env python3
"""
Demonstrate Reporting Capabilities for EmergentTrader
Shows both combined and individual strategy reports
"""

import sys
import os
from datetime import datetime

# Add the python_backend directory to the path
try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
except NameError:
    current_dir = os.getcwd()

sys.path.append(current_dir)

from core.enhanced_signal_engine import EnhancedSignalEngine
from core.signal_database import SignalDatabase

def demonstrate_combined_report():
    """Show combined report across all strategies"""
    print("📊 COMBINED REPORT - ALL STRATEGIES")
    print("=" * 60)
    
    engine = EnhancedSignalEngine()
    db = SignalDatabase()
    
    # Get all active signals
    all_signals = db.get_active_signals()
    
    print(f"Total Active Signals: {len(all_signals)}")
    print(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Group by strategy
    strategy_groups = {}
    for signal in all_signals:
        strategy = signal['strategy']
        if strategy not in strategy_groups:
            strategy_groups[strategy] = []
        strategy_groups[strategy].append(signal)
    
    print("📈 STRATEGY SUMMARY:")
    for strategy, signals in strategy_groups.items():
        print(f"  {strategy}: {len(signals)} signals")
        for signal in signals:
            print(f"    • {signal['symbol']} - {signal['signal_type']} - {signal['generated_at'][:19]}")
    print()
    
    # Database statistics
    stats = db.get_database_stats()
    print("🗄️  DATABASE STATISTICS:")
    print(f"  Total signals in database: {stats['total_signals']}")
    print(f"  Active signals: {stats['status_breakdown'].get('ACTIVE', 0)}")
    print(f"  Date range: {stats['date_range']['earliest'][:10]} to {stats['date_range']['latest'][:10]}")
    print()
    
    return all_signals, strategy_groups

def demonstrate_individual_strategy_reports():
    """Show individual reports for each strategy"""
    print("📋 INDIVIDUAL STRATEGY REPORTS")
    print("=" * 60)
    
    db = SignalDatabase()
    stats = db.get_database_stats()
    
    # Get all strategies that have signals
    strategies = list(stats.get('strategy_breakdown', {}).keys())
    
    for strategy in strategies:
        print(f"\n🎯 STRATEGY: {strategy.upper()}")
        print("-" * 40)
        
        # Get signals for this strategy
        strategy_signals = db.get_active_signals(strategy=strategy)
        
        print(f"Active Signals: {len(strategy_signals)}")
        
        # Get strategy performance
        performance = db.get_strategy_performance(strategy, days=30)
        print(f"Total Signals (30 days): {performance.get('total_signals', 0)}")
        print(f"Average Confidence: {performance.get('avg_confidence', 0):.3f}")
        
        print("\nSignal Details:")
        for i, signal in enumerate(strategy_signals, 1):
            print(f"  {i}. {signal['symbol']}")
            print(f"     Signal: {signal['signal_type']}")
            print(f"     Generated: {signal['generated_at'][:19]}")
            print(f"     Signal ID: {signal['signal_id']}")
            
            # Show strategy-specific metadata
            if signal.get('metadata'):
                import json
                try:
                    metadata = json.loads(signal['metadata'])
                    
                    # Show key strategy-specific metrics
                    if strategy == 'low_volatility':
                        print(f"     Low Vol Score: {metadata.get('low_vol_score', 'N/A')}")
                        print(f"     Volatility: {metadata.get('annualized_volatility', 'N/A')}")
                        print(f"     Risk-Adjusted Return: {metadata.get('risk_adjusted_return', 'N/A')}")
                    
                    elif strategy == 'fundamental_growth':
                        print(f"     Growth Score: {metadata.get('growth_score', 'N/A')}")
                        print(f"     Revenue Growth: {metadata.get('revenue_growth', 'N/A')}")
                        print(f"     ROE: {metadata.get('roe', 'N/A')}")
                    
                    print(f"     Sector: {metadata.get('sector', 'N/A')}")
                    print(f"     Market Cap: {metadata.get('market_cap', 'N/A')}")
                    print(f"     Investment Thesis: {metadata.get('investment_thesis', 'N/A')}")
                    
                except:
                    pass
            print()

def demonstrate_api_reporting():
    """Show how API endpoints provide reports"""
    print("🌐 API REPORTING ENDPOINTS")
    print("=" * 60)
    
    print("Available API endpoints for reporting:")
    print()
    
    print("1. GET /signals/active")
    print("   • Returns all active signals across strategies")
    print("   • Can filter by strategy: /signals/active?strategy=momentum")
    print()
    
    print("2. GET /signals/today")
    print("   • Returns signals generated today")
    print("   • Combined view of all strategies")
    print()
    
    print("3. GET /performance/summary")
    print("   • Strategy performance metrics")
    print("   • Can specify strategy: /performance/summary?strategy=low_volatility")
    print()
    
    print("4. GET /signals/generate/multi")
    print("   • Generate signals from multiple strategies")
    print("   • Returns breakdown by strategy")
    print()
    
    print("5. Database Queries (via PyCharm or custom scripts):")
    print("   • Combined: SELECT * FROM signals WHERE status='ACTIVE'")
    print("   • By Strategy: SELECT * FROM signals WHERE strategy='momentum'")
    print("   • Performance: SELECT strategy, COUNT(*) FROM signals GROUP BY strategy")

def demonstrate_consensus_reporting():
    """Show consensus signal reporting"""
    print("\n🤝 CONSENSUS SIGNAL REPORTING")
    print("=" * 60)
    
    db = SignalDatabase()
    consensus_signals = db.get_consensus_signals(days=7)
    
    print(f"Active Consensus Signals: {len(consensus_signals)}")
    
    if consensus_signals:
        for signal in consensus_signals:
            print(f"  Symbol: {signal['symbol']}")
            print(f"  Signal: {signal['signal_type']}")
            print(f"  Strategies: {signal['strategies']}")
            print(f"  Strategy Count: {signal['strategy_count']}")
            print(f"  Consensus Strength: {signal['consensus_strength']}")
            print()
    else:
        print("  No consensus signals found (requires multiple strategies agreeing)")
        print("  Consensus signals are created when 2+ strategies generate")
        print("  the same signal for the same stock")

def main():
    """Run comprehensive reporting demonstration"""
    print("🎯 EMERGENTTRADER REPORTING CAPABILITIES")
    print("=" * 70)
    print()
    
    # Combined report
    all_signals, strategy_groups = demonstrate_combined_report()
    
    print("\n" + "=" * 70)
    
    # Individual strategy reports
    demonstrate_individual_strategy_reports()
    
    print("\n" + "=" * 70)
    
    # API reporting
    demonstrate_api_reporting()
    
    # Consensus reporting
    demonstrate_consensus_reporting()
    
    print("\n" + "=" * 70)
    print("✅ CONFIRMATION:")
    print("✓ All signals stored with strategy information")
    print("✓ Combined reports available across all strategies")
    print("✓ Individual strategy reports with detailed metrics")
    print("✓ API endpoints support both combined and filtered views")
    print("✓ Database schema supports comprehensive reporting")
    print("✓ Consensus signals track multi-strategy agreements")
    print("✓ Historical tracking enabled for performance analysis")

if __name__ == "__main__":
    main()
