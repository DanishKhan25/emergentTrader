#!/usr/bin/env python3
"""
Comprehensive test script for all trading strategies in EmergentTrader
Tests signal generation, API integration, and strategy performance
"""

import sys
import os
import json
from datetime import datetime
import logging

# Add python_backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'python_backend'))

from python_backend.api_handler import handle_api_request
from python_backend.core.signal_engine import SignalEngine
from python_backend.core.strategies.momentum_strategy import MomentumStrategy
from python_backend.core.strategies.mean_reversion_strategy import MeanReversionStrategy
from python_backend.core.strategies.breakout_strategy import BreakoutStrategy
from python_backend.core.strategies.value_investing_strategy import ValueInvestingStrategy

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TradingStrategyTester:
    def __init__(self):
        self.signal_engine = SignalEngine()
        self.test_results = {}
        
    def test_strategy_availability(self):
        """Test that all strategies are available"""
        print("\n🔍 Testing Strategy Availability")
        print("=" * 50)
        
        try:
            available_strategies = self.signal_engine.get_available_strategies()
            expected_strategies = ['momentum', 'mean_reversion', 'breakout', 'value_investing']
            
            print(f"Available strategies: {available_strategies}")
            
            for strategy in expected_strategies:
                if strategy in available_strategies:
                    print(f"✅ {strategy.replace('_', ' ').title()} Strategy - Available")
                    
                    # Get strategy info
                    info = self.signal_engine.get_strategy_info(strategy)
                    print(f"   📋 Parameters: {len(info.get('parameters', {}))} configured")
                else:
                    print(f"❌ {strategy.replace('_', ' ').title()} Strategy - Missing")
            
            self.test_results['strategy_availability'] = {
                'available': available_strategies,
                'expected': expected_strategies,
                'all_available': all(s in available_strategies for s in expected_strategies)
            }
            
        except Exception as e:
            print(f"❌ Error testing strategy availability: {str(e)}")
            self.test_results['strategy_availability'] = {'error': str(e)}
    
    def test_individual_strategies(self):
        """Test each strategy individually"""
        print("\n🎯 Testing Individual Strategies")
        print("=" * 50)
        
        strategies_to_test = ['momentum', 'mean_reversion', 'breakout', 'value_investing']
        test_symbols = ['MARUTI.NS', 'DIVISLAB.NS']  # Known Shariah-compliant stocks
        
        for strategy in strategies_to_test:
            print(f"\n📊 Testing {strategy.replace('_', ' ').title()} Strategy")
            print("-" * 40)
            
            try:
                # Test signal generation
                signals = self.signal_engine.generate_signals(
                    symbols=test_symbols,
                    strategy_name=strategy,
                    shariah_only=True,
                    min_confidence=0.5  # Lower threshold for testing
                )
                
                print(f"   Generated {len(signals)} signals")
                
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
                        print(f"   📍 Bollinger Position: {sample_signal.get('bollinger_position', 'N/A')}")
                    elif strategy == 'breakout':
                        print(f"   💥 Breakout Score: {sample_signal.get('breakout_score', 0)}")
                        print(f"   📈 Breakout Type: {sample_signal.get('breakout_type', 'N/A')}")
                    elif strategy == 'value_investing':
                        print(f"   💎 Value Score: {sample_signal.get('value_score', 0)}")
                        print(f"   🛡️  Margin of Safety: {sample_signal.get('margin_of_safety', 0)}%")
                
                self.test_results[f'{strategy}_test'] = {
                    'signals_generated': len(signals),
                    'success': True,
                    'sample_signal': signals[0] if signals else None
                }
                
                print(f"   ✅ {strategy.replace('_', ' ').title()} strategy test passed")
                
            except Exception as e:
                print(f"   ❌ Error testing {strategy}: {str(e)}")
                self.test_results[f'{strategy}_test'] = {
                    'success': False,
                    'error': str(e)
                }
    
    def test_multi_strategy_generation(self):
        """Test multi-strategy signal generation"""
        print("\n🎯 Testing Multi-Strategy Generation")
        print("=" * 50)
        
        try:
            test_symbols = ['MARUTI.NS', 'DIVISLAB.NS']
            strategies = ['momentum', 'mean_reversion', 'breakout', 'value_investing']
            
            all_signals = self.signal_engine.generate_multi_strategy_signals(
                symbols=test_symbols,
                strategies=strategies,
                shariah_only=True,
                min_confidence=0.4
            )
            
            total_signals = sum(len(signals) for signals in all_signals.values())
            print(f"📊 Total signals generated: {total_signals}")
            
            for strategy, signals in all_signals.items():
                print(f"   {strategy.replace('_', ' ').title()}: {len(signals)} signals")
            
            self.test_results['multi_strategy_test'] = {
                'strategies_tested': len(strategies),
                'total_signals': total_signals,
                'strategy_breakdown': {k: len(v) for k, v in all_signals.items()},
                'success': True
            }
            
            print("✅ Multi-strategy generation test passed")
            
        except Exception as e:
            print(f"❌ Error in multi-strategy test: {str(e)}")
            self.test_results['multi_strategy_test'] = {
                'success': False,
                'error': str(e)
            }
    
    def test_api_integration(self):
        """Test API integration with new strategies"""
        print("\n🔌 Testing API Integration")
        print("=" * 50)
        
        # Test available strategies endpoint
        try:
            response = handle_api_request('strategies/available', 'GET')
            if response.get('success'):
                strategies = response['data']['strategies']
                print(f"✅ Available strategies API: {len(strategies)} strategies")
                print(f"   Strategies: {', '.join(strategies)}")
            else:
                print(f"❌ Available strategies API failed: {response.get('error')}")
        except Exception as e:
            print(f"❌ Available strategies API error: {str(e)}")
        
        # Test signal generation for each strategy
        strategies_to_test = ['momentum', 'mean_reversion', 'breakout', 'value_investing']
        
        for strategy in strategies_to_test:
            try:
                params = {
                    'strategy': strategy,
                    'shariah_only': True,
                    'min_confidence': 0.4
                }
                
                response = handle_api_request('signals/generate', 'POST', params)
                
                if response.get('success'):
                    count = response['data']['count']
                    print(f"✅ {strategy.replace('_', ' ').title()} API: {count} signals generated")
                else:
                    print(f"❌ {strategy.replace('_', ' ').title()} API failed: {response.get('error')}")
                    
            except Exception as e:
                print(f"❌ {strategy.replace('_', ' ').title()} API error: {str(e)}")
        
        # Test multi-strategy API
        try:
            params = {
                'strategies': ['momentum', 'mean_reversion'],
                'shariah_only': True,
                'min_confidence': 0.4
            }
            
            response = handle_api_request('signals/generate/multi', 'POST', params)
            
            if response.get('success'):
                total_count = response['data']['total_count']
                breakdown = response['data']['strategy_breakdown']
                print(f"✅ Multi-strategy API: {total_count} total signals")
                print(f"   Breakdown: {breakdown}")
            else:
                print(f"❌ Multi-strategy API failed: {response.get('error')}")
                
        except Exception as e:
            print(f"❌ Multi-strategy API error: {str(e)}")
    
    def test_strategy_parameters(self):
        """Test strategy parameter configuration"""
        print("\n⚙️  Testing Strategy Parameters")
        print("=" * 50)
        
        strategies = ['momentum', 'mean_reversion', 'breakout', 'value_investing']
        
        for strategy_name in strategies:
            try:
                if strategy_name in self.signal_engine.strategies:
                    strategy = self.signal_engine.strategies[strategy_name]
                    params = strategy.get_strategy_params()
                    
                    print(f"📋 {strategy_name.replace('_', ' ').title()} Parameters:")
                    for key, value in params.items():
                        print(f"   {key}: {value}")
                    
                    self.test_results[f'{strategy_name}_params'] = params
                    print(f"✅ {strategy_name.replace('_', ' ').title()} parameters loaded")
                    
            except Exception as e:
                print(f"❌ Error loading {strategy_name} parameters: {str(e)}")
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        print("\n📊 Test Report Summary")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() 
                          if isinstance(result, dict) and result.get('success', False))
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Detailed results
        print("\n📋 Detailed Results:")
        for test_name, result in self.test_results.items():
            if isinstance(result, dict):
                status = "✅ PASS" if result.get('success', False) else "❌ FAIL"
                print(f"   {test_name}: {status}")
                if not result.get('success', False) and 'error' in result:
                    print(f"      Error: {result['error']}")
        
        # Save results to file
        try:
            with open('strategy_test_results.json', 'w') as f:
                json.dump({
                    'test_date': datetime.now().isoformat(),
                    'summary': {
                        'total_tests': total_tests,
                        'passed_tests': passed_tests,
                        'success_rate': (passed_tests/total_tests)*100
                    },
                    'detailed_results': self.test_results
                }, f, indent=2)
            print(f"\n💾 Test results saved to: strategy_test_results.json")
        except Exception as e:
            print(f"❌ Error saving test results: {str(e)}")
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 EmergentTrader Trading Strategies Test Suite")
        print("=" * 60)
        print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run all tests
        self.test_strategy_availability()
        self.test_strategy_parameters()
        self.test_individual_strategies()
        self.test_multi_strategy_generation()
        self.test_api_integration()
        
        # Generate report
        self.generate_test_report()
        
        print(f"\n🏁 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    """Main test function"""
    tester = TradingStrategyTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()
