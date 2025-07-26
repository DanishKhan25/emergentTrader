#!/usr/bin/env python3
"""
Test Signal Database Integration
Tests the new database storage functionality for trading signals
"""

import sys
import os
import logging
from datetime import datetime

# Add the python_backend directory to the path
try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
except NameError:
    # If __file__ is not defined, use current working directory
    current_dir = os.getcwd()

sys.path.append(current_dir)

from core.enhanced_signal_engine import EnhancedSignalEngine
from core.signal_database import SignalDatabase

def test_database_initialization():
    """Test database initialization"""
    print("🔧 Testing database initialization...")
    
    try:
        db = SignalDatabase()
        stats = db.get_database_stats()
        print(f"✅ Database initialized successfully")
        print(f"   Database path: {stats.get('database_path', 'Unknown')}")
        print(f"   Total signals: {stats.get('total_signals', 0)}")
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {str(e)}")
        return False

def test_signal_generation_with_storage():
    """Test signal generation with database storage"""
    print("\n📊 Testing signal generation with database storage...")
    
    try:
        # Initialize enhanced signal engine (includes database)
        engine = EnhancedSignalEngine()
        
        # Test single strategy signal generation
        print("   Testing single strategy signals...")
        momentum_signals = engine._generate_single_strategy_signals(
            symbols=['RELIANCE', 'TCS', 'INFY'],
            strategy_name='momentum',
            shariah_only=True,
            min_confidence=0.5
        )
        
        print(f"   Generated {len(momentum_signals)} momentum signals")
        
        # Test consensus signal generation (limited symbols for speed)
        print("   Testing consensus signals...")
        consensus_signals = engine.generate_consensus_signals(
            symbols=['RELIANCE', 'TCS'],
            shariah_only=True,
            max_symbols=2
        )
        
        print(f"   Generated {len(consensus_signals)} consensus signals")
        
        return len(momentum_signals) + len(consensus_signals) > 0
        
    except Exception as e:
        print(f"❌ Signal generation test failed: {str(e)}")
        return False

def test_database_queries():
    """Test database query functionality"""
    print("\n🔍 Testing database queries...")
    
    try:
        db = SignalDatabase()
        
        # Test active signals query
        active_signals = db.get_active_signals()
        print(f"   Active signals: {len(active_signals)}")
        
        # Test strategy performance
        momentum_perf = db.get_strategy_performance('momentum', days=30)
        print(f"   Momentum strategy performance: {momentum_perf.get('total_signals', 0)} signals")
        
        # Test consensus signals
        consensus_signals = db.get_consensus_signals(days=7)
        print(f"   Recent consensus signals: {len(consensus_signals)}")
        
        # Test database stats
        stats = db.get_database_stats()
        print(f"   Database statistics:")
        print(f"     Total signals: {stats.get('total_signals', 0)}")
        print(f"     Active consensus: {stats.get('active_consensus_signals', 0)}")
        
        if stats.get('strategy_breakdown'):
            print(f"     Strategy breakdown: {stats['strategy_breakdown']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database query test failed: {str(e)}")
        return False

def test_enhanced_engine_integration():
    """Test enhanced signal engine database integration"""
    print("\n🚀 Testing enhanced engine database integration...")
    
    try:
        engine = EnhancedSignalEngine()
        
        # Test system status (includes database stats)
        status = engine.get_system_status()
        print(f"   System ready: {status.get('system_ready', False)}")
        print(f"   Strategies available: {status.get('strategies_available', 0)}")
        
        if 'database_stats' in status:
            db_stats = status['database_stats']
            print(f"   Database total signals: {db_stats.get('total_signals', 0)}")
        
        # Test active signals retrieval
        active_signals = engine.get_active_signals()
        print(f"   Active signals from DB: {len(active_signals)}")
        
        # Test strategy performance
        momentum_perf = engine.get_strategy_performance('momentum')
        print(f"   Momentum performance: {momentum_perf.get('total_signals', 0)} signals")
        
        return True
        
    except Exception as e:
        print(f"❌ Enhanced engine integration test failed: {str(e)}")
        return False

def main():
    """Run all database integration tests"""
    print("🧪 Signal Database Integration Tests")
    print("=" * 50)
    
    # Configure logging
    logging.basicConfig(level=logging.WARNING)  # Reduce noise during testing
    
    tests = [
        ("Database Initialization", test_database_initialization),
        ("Signal Generation with Storage", test_signal_generation_with_storage),
        ("Database Queries", test_database_queries),
        ("Enhanced Engine Integration", test_enhanced_engine_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔬 Running: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"💥 {test_name}: ERROR - {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Database integration is working correctly.")
        print("\n📝 Next steps:")
        print("   1. Run your signal generation to populate database")
        print("   2. Use API endpoints to query stored signals")
        print("   3. Implement real-time performance tracking")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
