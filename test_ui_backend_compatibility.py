#!/usr/bin/env python3
"""
UI-Backend Compatibility Test Script
Tests all API endpoints that the frontend expects
"""

import requests
import json
import time
from datetime import datetime
import sys

class UIBackendCompatibilityTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.test_results = []
        
    def log_test(self, test_name, success, details=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    {details}")
        
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
    
    def test_endpoint(self, endpoint, method="GET", data=None, expected_keys=None):
        """Test a single endpoint"""
        try:
            url = f"{self.base_url}{endpoint}"
            
            if method == "GET":
                response = requests.get(url, timeout=10)
            elif method == "POST":
                response = requests.post(url, json=data, timeout=10)
            else:
                return False, f"Unsupported method: {method}"
            
            if response.status_code != 200:
                return False, f"HTTP {response.status_code}: {response.text}"
            
            try:
                json_data = response.json()
            except:
                return False, "Response is not valid JSON"
            
            # Check for expected keys
            if expected_keys:
                missing_keys = []
                for key in expected_keys:
                    if key not in json_data:
                        missing_keys.append(key)
                
                if missing_keys:
                    return False, f"Missing keys: {missing_keys}"
            
            return True, f"Response: {json.dumps(json_data, indent=2)[:200]}..."
            
        except requests.exceptions.ConnectionError:
            return False, "Connection failed - is the backend running?"
        except requests.exceptions.Timeout:
            return False, "Request timeout"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def run_compatibility_tests(self):
        """Run all compatibility tests"""
        print("🔍 UI-Backend Compatibility Test Suite")
        print("=" * 50)
        
        # Test 1: Root endpoint
        success, details = self.test_endpoint("/", expected_keys=["name", "version"])
        self.log_test("Root Endpoint (/)", success, details)
        
        # Test 2: Health check
        success, details = self.test_endpoint("/health", expected_keys=["status"])
        self.log_test("Health Check (/health)", success, details)
        
        # Test 3: All stocks
        success, details = self.test_endpoint("/stocks/all", expected_keys=["success"])
        self.log_test("All Stocks (/stocks/all)", success, details)
        
        # Test 4: Shariah stocks
        success, details = self.test_endpoint("/stocks/shariah", expected_keys=["success"])
        self.log_test("Shariah Stocks (/stocks/shariah)", success, details)
        
        # Test 5: Stocks with filter
        success, details = self.test_endpoint("/stocks?shariah_only=true", expected_keys=["success"])
        self.log_test("Stocks with Filter (/stocks)", success, details)
        
        # Test 6: Today's signals
        success, details = self.test_endpoint("/signals/today", expected_keys=["success"])
        self.log_test("Today's Signals (/signals/today)", success, details)
        
        # Test 7: Open signals
        success, details = self.test_endpoint("/signals/open", expected_keys=["success"])
        self.log_test("Open Signals (/signals/open)", success, details)
        
        # Test 8: Generate signals
        signal_data = {
            "strategy": "multibagger",
            "shariah_only": True,
            "min_confidence": 0.7
        }
        success, details = self.test_endpoint("/signals", "POST", signal_data, expected_keys=["success"])
        self.log_test("Generate Signals (POST /signals)", success, details)
        
        # Test 9: Alternative generate signals endpoint
        success, details = self.test_endpoint("/signals/generate", "POST", signal_data, expected_keys=["success"])
        self.log_test("Generate Signals Alt (POST /signals/generate)", success, details)
        
        # Test 10: Performance summary
        success, details = self.test_endpoint("/performance", expected_keys=["success"])
        self.log_test("Performance (/performance)", success, details)
        
        # Test 11: Performance with period
        success, details = self.test_endpoint("/performance/summary?period=30d", expected_keys=["success"])
        self.log_test("Performance Summary (/performance/summary)", success, details)
        
        # Test 12: Available strategies
        success, details = self.test_endpoint("/strategies", expected_keys=["strategies"])
        self.log_test("Available Strategies (/strategies)", success, details)
        
        # Test 13: Backtest
        backtest_data = {
            "strategy": "multibagger",
            "start_date": "2019-01-01",
            "end_date": "2020-01-01"
        }
        success, details = self.test_endpoint("/backtest", "POST", backtest_data, expected_keys=["success"])
        self.log_test("Backtest (POST /backtest)", success, details)
        
        # Test 14: Stock details
        success, details = self.test_endpoint("/stock/RELIANCE", expected_keys=["success"])
        self.log_test("Stock Details (/stock/RELIANCE)", success, details)
        
        # Test 15: Track signals
        track_data = {
            "signal_ids": ["test_signal_1", "test_signal_2"]
        }
        success, details = self.test_endpoint("/signals/track", "POST", track_data, expected_keys=["success"])
        self.log_test("Track Signals (POST /signals/track)", success, details)
        
        print("\n" + "=" * 50)
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"📊 TEST SUMMARY")
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   - {result['test']}: {result['details']}")
        
        # Save results to file
        with open('ui_backend_compatibility_results.json', 'w') as f:
            json.dump({
                'summary': {
                    'total_tests': total_tests,
                    'passed_tests': passed_tests,
                    'failed_tests': failed_tests,
                    'success_rate': (passed_tests/total_tests)*100,
                    'test_date': datetime.now().isoformat()
                },
                'detailed_results': self.test_results
            }, f, indent=2)
        
        print(f"\n📁 Detailed results saved to: ui_backend_compatibility_results.json")
        
        if passed_tests == total_tests:
            print(f"\n🎉 ALL TESTS PASSED! UI-Backend compatibility is PERFECT!")
            return True
        else:
            print(f"\n⚠️ Some tests failed. Check the backend implementation.")
            return False

def main():
    """Main function"""
    print("🚀 Starting UI-Backend Compatibility Tests...")
    print("Make sure the FastAPI backend is running on http://localhost:8000")
    print()
    
    # Wait a moment for user to read
    time.sleep(2)
    
    tester = UIBackendCompatibilityTester()
    success = tester.run_compatibility_tests()
    
    if success:
        print("\n✅ UI-Backend compatibility verified!")
        print("🚀 Ready for production deployment!")
        sys.exit(0)
    else:
        print("\n❌ Compatibility issues found!")
        print("🔧 Fix the issues before deployment.")
        sys.exit(1)

if __name__ == "__main__":
    main()
