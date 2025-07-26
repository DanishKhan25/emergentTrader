#!/usr/bin/env python3
"""
ML Integration Test Script
Comprehensive testing of ML Interface Engine integration with Signal Generator
"""

import sys
import os
import json
import time
from datetime import datetime
import requests
import subprocess
import threading

# Add python_backend to path
sys.path.append('python_backend')

def print_header(title):
    """Print formatted header"""
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print(f"{'='*60}")

def print_step(step, description):
    """Print test step"""
    print(f"\n{step}. {description}")
    print("-" * 40)

def test_ml_engine_import():
    """Test 1: ML Engine Import and Initialization"""
    print_step("1", "Testing ML Engine Import and Initialization")
    
    try:
        from python_backend.ml.ml_inference_engine import MLInferenceEngine
        
        # Initialize ML engine
        ml_engine = MLInferenceEngine()
        
        # Get model info
        model_info = ml_engine.get_model_info()
        
        print("✅ ML Engine imported successfully")
        print(f"   Models loaded: {model_info['models_loaded']}")
        print(f"   Features: {model_info['feature_count']}")
        print(f"   Inference ready: {model_info['inference_ready']}")
        
        return True, ml_engine
        
    except Exception as e:
        print(f"❌ ML Engine import failed: {str(e)}")
        return False, None

def test_ml_enhanced_signal_engine():
    """Test 2: ML-Enhanced Signal Engine"""
    print_step("2", "Testing ML-Enhanced Signal Engine")
    
    try:
        from python_backend.core.ml_enhanced_signal_engine import MLEnhancedSignalEngine
        
        # Initialize with ML enabled
        engine = MLEnhancedSignalEngine(enable_ml=True)
        
        # Test ML integration
        ml_test = engine.test_ml_integration()
        
        print("✅ ML-Enhanced Signal Engine initialized")
        print(f"   ML Integration Status: {ml_test['status']}")
        
        if ml_test['status'] == 'success':
            print(f"   Test Signal ML Probability: {ml_test['ml_result']['ml_probability']:.1%}")
            print(f"   ML Recommendation: {ml_test['ml_result']['recommendation']}")
            print(f"   Quality Score: {ml_test['ml_result']['quality_score']}")
        
        return True, engine
        
    except Exception as e:
        print(f"❌ ML-Enhanced Signal Engine failed: {str(e)}")
        return False, None

def test_market_context(engine):
    """Test 3: Market Context Analysis"""
    print_step("3", "Testing Market Context Analysis")
    
    try:
        market_context = engine.get_market_context()
        
        print("✅ Market context retrieved successfully")
        print(f"   Market Regime: {market_context['regime']}")
        print(f"   Volatility: {market_context['volatility']:.1%}")
        print(f"   20-day Trend: {market_context['trend_20d']:+.1%}")
        print(f"   Above SMA 50: {market_context['above_sma_50']}")
        
        return True, market_context
        
    except Exception as e:
        print(f"❌ Market context analysis failed: {str(e)}")
        return False, None

def test_ml_signal_generation(engine):
    """Test 4: ML-Enhanced Signal Generation"""
    print_step("4", "Testing ML-Enhanced Signal Generation")
    
    try:
        print("Generating ML-enhanced signals (this may take 30-60 seconds)...")
        
        start_time = time.time()
        
        # Generate ML-enhanced signals
        signals = engine.generate_ml_enhanced_signals(
            shariah_only=True,
            max_symbols=10,  # Small number for testing
            min_ml_probability=0.5  # Lower threshold for testing
        )
        
        end_time = time.time()
        generation_time = end_time - start_time
        
        print(f"✅ ML-enhanced signal generation completed")
        print(f"   Signals generated: {len(signals)}")
        print(f"   Generation time: {generation_time:.1f} seconds")
        
        # Show sample signals
        if signals:
            print(f"\n   Sample signals:")
            for i, signal in enumerate(signals[:3]):
                print(f"   {i+1}. {signal['symbol']} ({signal.get('strategy', 'consensus')})")
                print(f"      Original Confidence: {signal.get('confidence', 0):.1%}")
                if signal.get('ml_enhanced'):
                    print(f"      ML Probability: {signal.get('ml_probability', 0):.1%}")
                    print(f"      ML Recommendation: {signal.get('ml_recommendation', 'N/A')}")
                    print(f"      Quality Score: {signal.get('ml_quality_score', 'N/A')}")
                    print(f"      Confidence Adjustment: {signal.get('confidence_adjustment', 0):+.1%}")
        
        return True, signals
        
    except Exception as e:
        print(f"❌ ML-enhanced signal generation failed: {str(e)}")
        return False, []

def test_system_status(engine):
    """Test 5: System Status and ML Performance"""
    print_step("5", "Testing System Status and ML Performance")
    
    try:
        # Get system status
        status = engine.get_system_status()
        
        print("✅ System status retrieved")
        print(f"   System Ready: {status['system_ready']}")
        print(f"   Strategies Available: {status['strategies_available']}")
        print(f"   Active Signals: {status['active_signals']}")
        print(f"   ML Enhanced Signals: {status.get('ml_enhanced_signals', 0)}")
        
        # ML status
        ml_status = status.get('ml_status', {})
        print(f"\n   ML Status:")
        print(f"   - ML Enabled: {ml_status.get('ml_enabled', False)}")
        print(f"   - ML Engine Loaded: {ml_status.get('ml_engine_loaded', False)}")
        print(f"   - ML Enhanced Signals Count: {ml_status.get('ml_enhanced_signals_count', 0)}")
        
        # Get ML performance summary
        ml_performance = engine.get_ml_performance_summary()
        
        if ml_performance.get('ml_enabled'):
            print(f"\n   ML Performance:")
            print(f"   - Enhancement Rate: {ml_performance.get('ml_enhancement_rate', 0):.1f}%")
            print(f"   - Average ML Probability: {ml_performance.get('average_ml_probability', 0):.1%}")
            print(f"   - Average Confidence Adjustment: {ml_performance.get('average_confidence_adjustment', 0):+.1%}")
        
        return True, status
        
    except Exception as e:
        print(f"❌ System status check failed: {str(e)}")
        return False, None

def start_api_server():
    """Start the ML-enhanced API server in background"""
    try:
        print("Starting ML-Enhanced API server...")
        
        # Start server in background
        process = subprocess.Popen([
            'python', 'python_backend/ml_enhanced_api_handler.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a bit for server to start
        time.sleep(5)
        
        return process
        
    except Exception as e:
        print(f"Failed to start API server: {str(e)}")
        return None

def test_api_endpoints():
    """Test 6: API Endpoints"""
    print_step("6", "Testing ML-Enhanced API Endpoints")
    
    base_url = "http://localhost:8000"
    
    # Test endpoints
    endpoints = [
        ("GET", "/health", "Health Check"),
        ("GET", "/", "Root Endpoint"),
        ("GET", "/system/status", "System Status"),
        ("GET", "/ml/test", "ML Test"),
        ("GET", "/market/context", "Market Context"),
        ("GET", "/strategies/available", "Available Strategies")
    ]
    
    results = {}
    
    for method, endpoint, description in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{base_url}{endpoint}", timeout=10)
            else:
                response = requests.post(f"{base_url}{endpoint}", timeout=10)
            
            if response.status_code == 200:
                print(f"   ✅ {description}: {response.status_code}")
                results[endpoint] = True
            else:
                print(f"   ❌ {description}: {response.status_code}")
                results[endpoint] = False
                
        except requests.exceptions.ConnectionError:
            print(f"   ⚠️  {description}: Server not running")
            results[endpoint] = False
        except Exception as e:
            print(f"   ❌ {description}: {str(e)}")
            results[endpoint] = False
    
    # Test ML-enhanced signal generation via API
    try:
        print(f"\n   Testing ML-enhanced signal generation via API...")
        
        response = requests.post(f"{base_url}/signals/ml-enhanced", 
                               json={
                                   "shariah_only": True,
                                   "max_symbols": 5,
                                   "min_ml_probability": 0.5
                               }, 
                               timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ ML Signal Generation API: {data['signals_count']} signals")
            results['/signals/ml-enhanced'] = True
        else:
            print(f"   ❌ ML Signal Generation API: {response.status_code}")
            results['/signals/ml-enhanced'] = False
            
    except Exception as e:
        print(f"   ❌ ML Signal Generation API: {str(e)}")
        results['/signals/ml-enhanced'] = False
    
    return results

def test_performance_benchmark():
    """Test 7: Performance Benchmark"""
    print_step("7", "Performance Benchmark")
    
    try:
        from python_backend.core.ml_enhanced_signal_engine import MLEnhancedSignalEngine
        
        # Test with ML enabled
        print("Testing with ML enabled...")
        engine_ml = MLEnhancedSignalEngine(enable_ml=True)
        
        start_time = time.time()
        signals_ml = engine_ml.generate_ml_enhanced_signals(
            shariah_only=True,
            max_symbols=5,
            min_ml_probability=0.5
        )
        ml_time = time.time() - start_time
        
        # Test with ML disabled
        print("Testing with ML disabled...")
        engine_no_ml = MLEnhancedSignalEngine(enable_ml=False)
        
        start_time = time.time()
        signals_no_ml = engine_no_ml.generate_signals(
            strategy_name='consensus',
            shariah_only=True
        )
        no_ml_time = time.time() - start_time
        
        print(f"✅ Performance benchmark completed")
        print(f"   With ML: {len(signals_ml)} signals in {ml_time:.1f}s")
        print(f"   Without ML: {len(signals_no_ml)} signals in {no_ml_time:.1f}s")
        print(f"   ML Overhead: {ml_time - no_ml_time:.1f}s ({((ml_time/no_ml_time - 1) * 100):+.1f}%)")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance benchmark failed: {str(e)}")
        return False

def generate_test_report(test_results):
    """Generate comprehensive test report"""
    print_header("TEST REPORT SUMMARY")
    
    total_tests = len(test_results)
    passed_tests = sum(1 for result in test_results.values() if result)
    
    print(f"📊 Overall Results: {passed_tests}/{total_tests} tests passed ({passed_tests/total_tests*100:.1f}%)")
    
    print(f"\n📋 Detailed Results:")
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} - {test_name}")
    
    # Integration status
    if passed_tests >= total_tests * 0.8:  # 80% pass rate
        print(f"\n🎉 ML INTEGRATION STATUS: SUCCESS")
        print(f"   Your ML Interface Engine is successfully integrated!")
        print(f"   Ready for production use with ML-enhanced signal generation.")
    else:
        print(f"\n⚠️  ML INTEGRATION STATUS: NEEDS ATTENTION")
        print(f"   Some tests failed. Please review the errors above.")
        print(f"   Check the ML_INTEGRATION_GUIDE.md for troubleshooting.")
    
    # Next steps
    print(f"\n🚀 NEXT STEPS:")
    if test_results.get('ML Signal Generation', False):
        print(f"   1. ✅ Start using ML-enhanced signals in production")
        print(f"   2. 📊 Monitor ML performance metrics")
        print(f"   3. 🔧 Fine-tune ML probability thresholds")
        print(f"   4. 📱 Update frontend to use ML endpoints")
    else:
        print(f"   1. 🔍 Review error logs for ML signal generation")
        print(f"   2. 📚 Check ML_INTEGRATION_GUIDE.md")
        print(f"   3. 🛠️  Fix any dependency issues")
        print(f"   4. 🔄 Re-run this test script")

def main():
    """Main test execution"""
    print_header("ML INTEGRATION COMPREHENSIVE TEST")
    print(f"Testing ML Interface Engine integration with Signal Generator")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_results = {}
    
    # Test 1: ML Engine Import
    success, ml_engine = test_ml_engine_import()
    test_results['ML Engine Import'] = success
    
    # Test 2: ML-Enhanced Signal Engine
    success, enhanced_engine = test_ml_enhanced_signal_engine()
    test_results['ML-Enhanced Signal Engine'] = success
    
    if enhanced_engine:
        # Test 3: Market Context
        success, market_context = test_market_context(enhanced_engine)
        test_results['Market Context Analysis'] = success
        
        # Test 4: ML Signal Generation
        success, signals = test_ml_signal_generation(enhanced_engine)
        test_results['ML Signal Generation'] = success
        
        # Test 5: System Status
        success, status = test_system_status(enhanced_engine)
        test_results['System Status'] = success
    
    # Test 6: API Endpoints (optional - requires server)
    print(f"\n⚠️  API tests require manual server start. Skipping for now.")
    print(f"   To test APIs: python python_backend/ml_enhanced_api_handler.py")
    
    # Test 7: Performance Benchmark
    success = test_performance_benchmark()
    test_results['Performance Benchmark'] = success
    
    # Generate final report
    generate_test_report(test_results)
    
    print(f"\n🏁 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
