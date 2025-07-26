#!/usr/bin/env python3
"""
Comprehensive test suite for all 10 trading strategies and API endpoints
Tests strategy functionality, API integration, and system reliability
"""

import sys
import os
import json
import time
from datetime import datetime
import logging

# Add python_backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'python_backend'))

from python_backend.api_handler import handle_api_request
from python_backend.core.signal_engine import SignalEngine

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ComprehensiveStrategyTester:
    def __init__(self):
        self.signal_engine = SignalEngine()
        self.test_results = {}
        self.test_symbols = ['MARUTI', 'DIVISLAB', 'RELIANCE', 'TCS', 'INFY']  # Known working symbols
        
    def print_header(self, title):
        """Print formatted test section header"""
        print(f"\n{'='*60}")
        print(f"🧪 {title}")
        print(f"{'='*60}")
    
    def print_subheader(self, title):
        """Print formatted test subsection header"""
        print(f"\n{'─'*50}")
        print(f"📋 {title}")
        print(f"{'─'*50}")
    
    def test_strategy_availability(self):
        """Test that all 10 strategies are available and properly initialized"""
        self.print_header("STRATEGY AVAILABILITY TEST")
        
        expected_strategies = [
            'momentum', 'mean_reversion', 'breakout', 'value_investing',
            'swing_trading', 'multibagger', 'fundamental_growth', 
            'sector_rotation', 'low_volatility', 'pivot_cpr'
        ]
        
        available_strategies = self.signal_engine.get_available_strategies()
        
        print(f"Expected strategies: {len(expected_strategies)}")
        print(f"Available strategies: {len(available_strategies)}")
        print(f"Strategies found: {available_strategies}")
        
        # Check each strategy
        all_present = True
        for strategy in expected_strategies:
            if strategy in available_strategies:
                print(f"✅ {strategy.replace('_', ' ').title()} Strategy - Available")
                
                # Test strategy info
                try:
                    info = self.signal_engine.get_strategy_info(strategy)
                    params_count = len(info.get('parameters', {}))
                    print(f"   📋 Parameters: {params_count} configured")
                    print(f"   📝 Description: {info.get('description', 'N/A')[:50]}...")
                except Exception as e:
                    print(f"   ⚠️  Warning: Error getting strategy info - {str(e)}")
            else:
                print(f"❌ {strategy.replace('_', ' ').title()} Strategy - Missing")
                all_present = False
        
        self.test_results['strategy_availability'] = {
            'expected_count': len(expected_strategies),
            'available_count': len(available_strategies),
            'all_present': all_present,
            'missing_strategies': [s for s in expected_strategies if s not in available_strategies]
        }
        
        if all_present:
            print(f"\n🎉 SUCCESS: All {len(expected_strategies)} strategies are available!")
        else:
            print(f"\n❌ FAILURE: Missing strategies detected")
    
    def test_individual_strategies(self):
        """Test each strategy individually with sample data"""
        self.print_header("INDIVIDUAL STRATEGY TESTING")
        
        strategies_to_test = self.signal_engine.get_available_strategies()
        test_symbols = self.test_symbols[:2]  # Use 2 symbols for faster testing
        
        strategy_results = {}
        
        for strategy in strategies_to_test:
            self.print_subheader(f"Testing {strategy.replace('_', ' ').title()} Strategy")
            
            try:
                # Test signal generation with lower confidence threshold
                signals = self.signal_engine.generate_signals(
                    symbols=test_symbols,
                    strategy_name=strategy,
                    shariah_only=True,
                    min_confidence=0.3  # Lower threshold for testing
                )
                
                print(f"   📊 Generated {len(signals)} signals")
                
                if signals:
                    sample_signal = signals[0]
                    print(f"   📈 Sample signal: {sample_signal['symbol']} - {sample_signal['signal_type']}")
                    print(f"   💰 Entry: ₹{sample_signal.get('entry_price', 0)}")
                    print(f"   🎯 Target: ₹{sample_signal.get('target_price', 0)}")
                    print(f"   🛡️  Stop Loss: ₹{sample_signal.get('stop_loss', 0)}")
                    print(f"   📊 Confidence: {sample_signal.get('confidence_score', 0):.2f}")
                    
                    # Strategy-specific metrics
                    if strategy == 'momentum':
                        print(f"   ⚡ Momentum Score: {sample_signal.get('momentum_score', 0)}")
                    elif strategy == 'mean_reversion':
                        print(f"   🔄 Reversion Score: {sample_signal.get('reversion_score', 0)}")
                    elif strategy == 'breakout':
                        print(f"   💥 Breakout Score: {sample_signal.get('breakout_score', 0)}")
                    elif strategy == 'value_investing':
                        print(f"   💎 Value Score: {sample_signal.get('value_score', 0)}")
                    elif strategy == 'swing_trading':
                        print(f"   🔄 Swing Score: {sample_signal.get('swing_score', 0)}")
                    elif strategy == 'multibagger':
                        print(f"   🚀 Multibagger Score: {sample_signal.get('multibagger_score', 0)}")
                    elif strategy == 'fundamental_growth':
                        print(f"   📈 Growth Score: {sample_signal.get('growth_score', 0)}")
                    elif strategy == 'sector_rotation':
                        print(f"   🔄 Rotation Score: {sample_signal.get('rotation_score', 0)}")
                    elif strategy == 'low_volatility':
                        print(f"   📉 Low Vol Score: {sample_signal.get('low_vol_score', 0)}")
                    elif strategy == 'pivot_cpr':
                        print(f"   📊 Pivot Score: {sample_signal.get('pivot_score', 0)}")
                
                strategy_results[strategy] = {
                    'signals_generated': len(signals),
                    'success': True,
                    'sample_signal': signals[0] if signals else None
                }
                
                print(f"   ✅ {strategy.replace('_', ' ').title()} strategy test PASSED")
                
            except Exception as e:
                print(f"   ❌ Error testing {strategy}: {str(e)}")
                strategy_results[strategy] = {
                    'signals_generated': 0,
                    'success': False,
                    'error': str(e)
                }
        
        self.test_results['individual_strategies'] = strategy_results
        
        # Summary
        successful_strategies = sum(1 for result in strategy_results.values() if result.get('success', False))
        total_strategies = len(strategy_results)
        
        print(f"\n📊 STRATEGY TESTING SUMMARY:")
        print(f"   Total strategies tested: {total_strategies}")
        print(f"   Successful: {successful_strategies}")
        print(f"   Failed: {total_strategies - successful_strategies}")
        print(f"   Success rate: {(successful_strategies/total_strategies)*100:.1f}%")
    
    def test_api_endpoints(self):
        """Test all API endpoints"""
        self.print_header("API ENDPOINTS TESTING")
        
        api_tests = [
            {
                'name': 'API Health Check',
                'endpoint': '/',
                'method': 'GET',
                'params': {}
            },
            {
                'name': 'Available Strategies',
                'endpoint': 'strategies/available',
                'method': 'GET',
                'params': {}
            },
            {
                'name': 'NSE Stocks All',
                'endpoint': 'stocks/all',
                'method': 'GET',
                'params': {}
            },
            {
                'name': 'Shariah Stocks',
                'endpoint': 'stocks/shariah',
                'method': 'GET',
                'params': {}
            },
            {
                'name': 'Today\'s Signals',
                'endpoint': 'signals/today',
                'method': 'GET',
                'params': {}
            },
            {
                'name': 'Generate Momentum Signals',
                'endpoint': 'signals/generate',
                'method': 'POST',
                'params': {'strategy': 'momentum', 'shariah_only': True, 'min_confidence': 0.3}
            },
            {
                'name': 'Generate Mean Reversion Signals',
                'endpoint': 'signals/generate',
                'method': 'POST',
                'params': {'strategy': 'mean_reversion', 'shariah_only': True, 'min_confidence': 0.3}
            },
            {
                'name': 'Generate Breakout Signals',
                'endpoint': 'signals/generate',
                'method': 'POST',
                'params': {'strategy': 'breakout', 'shariah_only': True, 'min_confidence': 0.3}
            },
            {
                'name': 'Generate Value Investing Signals',
                'endpoint': 'signals/generate',
                'method': 'POST',
                'params': {'strategy': 'value_investing', 'shariah_only': True, 'min_confidence': 0.3}
            },
            {
                'name': 'Generate Multi-Strategy Signals',
                'endpoint': 'signals/generate/multi',
                'method': 'POST',
                'params': {
                    'strategies': ['momentum', 'mean_reversion', 'breakout'],
                    'shariah_only': True,
                    'min_confidence': 0.3
                }
            },
            {
                'name': 'Active Signals',
                'endpoint': 'signals/active',
                'method': 'GET',
                'params': {}
            },
            {
                'name': 'Performance Summary',
                'endpoint': 'performance/summary',
                'method': 'GET',
                'params': {'period': '30d'}
            }
        ]
        
        api_results = {}
        
        for test in api_tests:
            self.print_subheader(f"Testing {test['name']}")
            
            try:
                start_time = time.time()
                response = handle_api_request(test['endpoint'], test['method'], test['params'])
                end_time = time.time()
                
                response_time = (end_time - start_time) * 1000  # Convert to milliseconds
                
                if response.get('success'):
                    print(f"   ✅ SUCCESS - Response time: {response_time:.0f}ms")
                    
                    # Print relevant data info
                    data = response.get('data', {})
                    if 'count' in data:
                        print(f"   📊 Count: {data['count']}")
                    if 'signals' in data:
                        print(f"   📈 Signals: {len(data['signals'])}")
                    if 'stocks' in data:
                        print(f"   📋 Stocks: {len(data['stocks'])}")
                    if 'strategies' in data:
                        print(f"   🎯 Strategies: {len(data['strategies'])}")
                    
                    api_results[test['name']] = {
                        'success': True,
                        'response_time': response_time,
                        'data_summary': {
                            'count': data.get('count', 0),
                            'has_data': bool(data)
                        }
                    }
                else:
                    print(f"   ❌ FAILED - Error: {response.get('error', 'Unknown error')}")
                    api_results[test['name']] = {
                        'success': False,
                        'error': response.get('error', 'Unknown error'),
                        'response_time': response_time
                    }
                
            except Exception as e:
                print(f"   ❌ EXCEPTION - {str(e)}")
                api_results[test['name']] = {
                    'success': False,
                    'error': str(e),
                    'response_time': 0
                }
        
        self.test_results['api_endpoints'] = api_results
        
        # Summary
        successful_apis = sum(1 for result in api_results.values() if result.get('success', False))
        total_apis = len(api_results)
        avg_response_time = np.mean([r.get('response_time', 0) for r in api_results.values() if r.get('success', False)])
        
        print(f"\n📊 API TESTING SUMMARY:")
        print(f"   Total endpoints tested: {total_apis}")
        print(f"   Successful: {successful_apis}")
        print(f"   Failed: {total_apis - successful_apis}")
        print(f"   Success rate: {(successful_apis/total_apis)*100:.1f}%")
        print(f"   Average response time: {avg_response_time:.0f}ms")
    
    def test_multi_strategy_generation(self):
        """Test multi-strategy signal generation"""
        self.print_header("MULTI-STRATEGY GENERATION TEST")
        
        try:
            # Test with multiple strategies
            strategies_to_test = ['momentum', 'mean_reversion', 'breakout', 'value_investing']
            
            print(f"Testing multi-strategy generation with: {strategies_to_test}")
            
            all_signals = self.signal_engine.generate_multi_strategy_signals(
                symbols=self.test_symbols[:2],  # Use 2 symbols
                strategies=strategies_to_test,
                shariah_only=True,
                min_confidence=0.3
            )
            
            total_signals = sum(len(signals) for signals in all_signals.values())
            print(f"📊 Total signals generated: {total_signals}")
            
            for strategy, signals in all_signals.items():
                print(f"   {strategy.replace('_', ' ').title()}: {len(signals)} signals")
                
                if signals:
                    sample = signals[0]
                    print(f"      Sample: {sample['symbol']} - {sample['signal_type']} - Confidence: {sample.get('confidence_score', 0):.2f}")
            
            self.test_results['multi_strategy_test'] = {
                'strategies_tested': len(strategies_to_test),
                'total_signals': total_signals,
                'strategy_breakdown': {k: len(v) for k, v in all_signals.items()},
                'success': True
            }
            
            print("✅ Multi-strategy generation test PASSED")
            
        except Exception as e:
            print(f"❌ Multi-strategy generation test FAILED: {str(e)}")
            self.test_results['multi_strategy_test'] = {
                'success': False,
                'error': str(e)
            }
    
    def test_data_fetching(self):
        """Test data fetching capabilities"""
        self.print_header("DATA FETCHING TEST")
        
        try:
            # Test NSE universe loading
            print("Testing NSE universe loading...")
            universe = self.signal_engine.data_fetcher.get_nse_universe()
            print(f"✅ NSE Universe: {len(universe)} stocks loaded")
            
            # Test Shariah filtering
            print("Testing Shariah filtering...")
            shariah_stocks = self.signal_engine.get_shariah_universe()
            print(f"✅ Shariah Stocks: {len(shariah_stocks)} compliant stocks")
            
            # Test individual stock data fetching
            print("Testing individual stock data fetching...")
            test_symbol = 'MARUTI'
            stock_data = self.signal_engine.data_fetcher.get_nse_stock_data(test_symbol, period="6mo")
            
            if not stock_data.empty:
                print(f"✅ Stock Data: {len(stock_data)} data points for {test_symbol}")
                print(f"   Date range: {stock_data.iloc[0]['date']} to {stock_data.iloc[-1]['date']}")
            else:
                print(f"⚠️  Warning: No data retrieved for {test_symbol}")
            
            self.test_results['data_fetching'] = {
                'nse_universe_count': len(universe),
                'shariah_stocks_count': len(shariah_stocks),
                'sample_data_points': len(stock_data),
                'success': True
            }
            
        except Exception as e:
            print(f"❌ Data fetching test FAILED: {str(e)}")
            self.test_results['data_fetching'] = {
                'success': False,
                'error': str(e)
            }
    
    def test_error_handling(self):
        """Test error handling and edge cases"""
        self.print_header("ERROR HANDLING TEST")
        
        error_tests = [
            {
                'name': 'Invalid Strategy',
                'endpoint': 'signals/generate',
                'method': 'POST',
                'params': {'strategy': 'invalid_strategy'},
                'expect_error': True
            },
            {
                'name': 'Invalid Endpoint',
                'endpoint': 'invalid/endpoint',
                'method': 'GET',
                'params': {},
                'expect_error': True
            },
            {
                'name': 'Empty Symbol List',
                'test_type': 'direct',
                'function': lambda: self.signal_engine.generate_signals(symbols=[], strategy_name='momentum'),
                'expect_error': False  # Should handle gracefully
            }
        ]
        
        error_results = {}
        
        for test in error_tests:
            print(f"Testing: {test['name']}")
            
            try:
                if test.get('test_type') == 'direct':
                    result = test['function']()
                    if test['expect_error']:
                        print(f"   ⚠️  Expected error but got result: {type(result)}")
                        error_results[test['name']] = {'handled_correctly': False}
                    else:
                        print(f"   ✅ Handled gracefully: {type(result)}")
                        error_results[test['name']] = {'handled_correctly': True}
                else:
                    response = handle_api_request(test['endpoint'], test['method'], test['params'])
                    
                    if test['expect_error']:
                        if not response.get('success'):
                            print(f"   ✅ Error handled correctly: {response.get('error', 'Unknown error')}")
                            error_results[test['name']] = {'handled_correctly': True}
                        else:
                            print(f"   ⚠️  Expected error but got success")
                            error_results[test['name']] = {'handled_correctly': False}
                    else:
                        if response.get('success'):
                            print(f"   ✅ Handled correctly")
                            error_results[test['name']] = {'handled_correctly': True}
                        else:
                            print(f"   ⚠️  Unexpected error: {response.get('error')}")
                            error_results[test['name']] = {'handled_correctly': False}
                            
            except Exception as e:
                if test['expect_error']:
                    print(f"   ✅ Exception handled: {str(e)}")
                    error_results[test['name']] = {'handled_correctly': True}
                else:
                    print(f"   ❌ Unexpected exception: {str(e)}")
                    error_results[test['name']] = {'handled_correctly': False}
        
        self.test_results['error_handling'] = error_results
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        self.print_header("COMPREHENSIVE TEST REPORT")
        
        # Calculate overall statistics
        total_tests = 0
        passed_tests = 0
        
        for test_category, results in self.test_results.items():
            if isinstance(results, dict):
                if 'success' in results:
                    total_tests += 1
                    if results['success']:
                        passed_tests += 1
                elif isinstance(results, dict):
                    # Handle nested results
                    for sub_test, sub_result in results.items():
                        if isinstance(sub_result, dict) and 'success' in sub_result:
                            total_tests += 1
                            if sub_result['success']:
                                passed_tests += 1
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 OVERALL TEST STATISTICS:")
        print(f"   Total tests executed: {total_tests}")
        print(f"   Tests passed: {passed_tests}")
        print(f"   Tests failed: {total_tests - passed_tests}")
        print(f"   Success rate: {success_rate:.1f}%")
        
        # Detailed results by category
        print(f"\n📋 DETAILED RESULTS BY CATEGORY:")
        
        for category, results in self.test_results.items():
            print(f"\n   {category.replace('_', ' ').title()}:")
            
            if category == 'strategy_availability':
                print(f"      Available strategies: {results.get('available_count', 0)}/{results.get('expected_count', 0)}")
                if results.get('missing_strategies'):
                    print(f"      Missing: {results['missing_strategies']}")
            
            elif category == 'individual_strategies':
                successful = sum(1 for r in results.values() if r.get('success', False))
                total = len(results)
                print(f"      Strategy tests: {successful}/{total} passed")
                
                for strategy, result in results.items():
                    status = "✅" if result.get('success', False) else "❌"
                    signals = result.get('signals_generated', 0)
                    print(f"         {status} {strategy}: {signals} signals")
            
            elif category == 'api_endpoints':
                successful = sum(1 for r in results.values() if r.get('success', False))
                total = len(results)
                avg_time = np.mean([r.get('response_time', 0) for r in results.values() if r.get('success', False)])
                print(f"      API tests: {successful}/{total} passed")
                print(f"      Average response time: {avg_time:.0f}ms")
        
        # Save detailed report to file
        try:
            report_data = {
                'test_date': datetime.now().isoformat(),
                'summary': {
                    'total_tests': total_tests,
                    'passed_tests': passed_tests,
                    'success_rate': success_rate
                },
                'detailed_results': self.test_results
            }
            
            with open('comprehensive_test_report.json', 'w') as f:
                json.dump(report_data, f, indent=2, default=str)
            
            print(f"\n💾 Detailed test report saved to: comprehensive_test_report.json")
            
        except Exception as e:
            print(f"⚠️  Warning: Could not save test report: {str(e)}")
        
        # Final status
        if success_rate >= 90:
            print(f"\n🎉 EXCELLENT: System is performing exceptionally well!")
        elif success_rate >= 75:
            print(f"\n✅ GOOD: System is performing well with minor issues")
        elif success_rate >= 50:
            print(f"\n⚠️  WARNING: System has significant issues that need attention")
        else:
            print(f"\n❌ CRITICAL: System has major issues and needs immediate attention")
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 EmergentTrader Comprehensive Test Suite")
        print("=" * 70)
        print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run all test categories
        self.test_strategy_availability()
        self.test_data_fetching()
        self.test_individual_strategies()
        self.test_multi_strategy_generation()
        self.test_api_endpoints()
        self.test_error_handling()
        
        # Generate comprehensive report
        self.generate_test_report()
        
        print(f"\n🏁 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    """Main test function"""
    # Import numpy for calculations
    global np
    import numpy as np
    
    tester = ComprehensiveStrategyTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()
