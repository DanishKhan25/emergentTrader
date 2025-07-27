#!/usr/bin/env python3
"""
Step 4: Validate Multibagger Predictions (Fixed)
Check which 2019 ML signals actually became multibaggers from 2019-2025
"""

import pandas as pd
import numpy as np
import os
import json
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class MultibaggerValidatorFixed:
    def __init__(self):
        self.testing_data_dir = "testing_data_2019_2025"
        self.signals_dir = "signals_2019"
        self.results_dir = "validation_results"
        
        # Create results directory
        os.makedirs(self.results_dir, exist_ok=True)
        
        # Multibagger thresholds
        self.multibagger_thresholds = {
            "2x": 100,    # 100% return
            "3x": 200,    # 200% return
            "5x": 400,    # 400% return
            "10x": 900,   # 900% return
            "20x": 1900   # 1900% return
        }
        
    def load_2019_signals(self):
        """Load the 2019 high-confidence signals"""
        print("📊 Loading 2019 high-confidence signals...")
        
        signals_file = f"{self.signals_dir}/high_confidence_signals_2019.json"
        
        if not os.path.exists(signals_file):
            print(f"❌ Signals file not found: {signals_file}")
            return None
            
        with open(signals_file, 'r') as f:
            signals = json.load(f)
            
        print(f"✅ Loaded {len(signals)} high-confidence signals")
        return signals
        
    def load_stock_data(self, symbol):
        """Load complete stock data for validation"""
        try:
            data_file = f"{self.testing_data_dir}/{symbol}_testing.csv"
            
            if not os.path.exists(data_file):
                print(f"❌ Data file not found for {symbol}")
                return None
                
            df = pd.read_csv(data_file)
            df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize(None)  # Remove timezone
            df.set_index('Date', inplace=True)
            
            return df
            
        except Exception as e:
            print(f"❌ Error loading data for {symbol}: {str(e)}")
            return None
            
    def calculate_returns_over_time(self, signal, stock_data):
        """Calculate returns at different time horizons"""
        try:
            signal_date = pd.to_datetime(signal['date']).tz_localize(None)  # Remove timezone
            entry_price = signal['price']
            
            # Find data after signal date
            future_data = stock_data[stock_data.index > signal_date].copy()
            
            if len(future_data) == 0:
                print(f"  ⚠️ No future data available for {signal['symbol']}")
                return None
                
            # Calculate returns at different time periods
            time_periods = {
                '1_month': 22,    # ~1 month
                '3_months': 66,   # ~3 months
                '6_months': 132,  # ~6 months
                '1_year': 252,    # ~1 year
                '2_years': 504,   # ~2 years
                '3_years': 756,   # ~3 years
                '4_years': 1008,  # ~4 years
                '5_years': 1260,  # ~5 years
                '6_years': 1512   # ~6 years (till 2025)
            }
            
            returns_data = {
                'symbol': signal['symbol'],
                'signal_date': signal['date'],
                'entry_price': entry_price,
                'ml_probability': signal['ensemble_probability'],
                'returns': {},
                'prices': {},
                'max_return': 0,
                'max_return_date': None,
                'max_return_price': entry_price
            }
            
            # Calculate returns for each time period
            for period_name, days in time_periods.items():
                if len(future_data) >= days:
                    exit_price = future_data.iloc[days-1]['Close']
                    return_pct = (exit_price / entry_price - 1) * 100
                    
                    returns_data['returns'][period_name] = return_pct
                    returns_data['prices'][period_name] = exit_price
                    
            # Find maximum return achieved over entire period
            max_return = -100  # Start with -100% (total loss)
            max_date = None
            max_price = entry_price
            
            for date, row in future_data.iterrows():
                current_return = (row['Close'] / entry_price - 1) * 100
                if current_return > max_return:
                    max_return = current_return
                    max_date = date
                    max_price = row['Close']
                    
            returns_data['max_return'] = max_return
            returns_data['max_return_date'] = max_date.strftime('%Y-%m-%d') if max_date else None
            returns_data['max_return_price'] = max_price
                    
            return returns_data
            
        except Exception as e:
            print(f"❌ Error calculating returns for {signal['symbol']}: {str(e)}")
            return None
            
    def classify_multibagger_level(self, max_return):
        """Classify the multibagger level based on maximum return"""
        if max_return >= self.multibagger_thresholds['20x']:
            return '20x+'
        elif max_return >= self.multibagger_thresholds['10x']:
            return '10x'
        elif max_return >= self.multibagger_thresholds['5x']:
            return '5x'
        elif max_return >= self.multibagger_thresholds['3x']:
            return '3x'
        elif max_return >= self.multibagger_thresholds['2x']:
            return '2x'
        elif max_return >= 50:
            return '1.5x'
        elif max_return >= 0:
            return 'Positive'
        else:
            return 'Loss'
            
    def validate_all_signals(self, signals):
        """Validate all 2019 signals"""
        print("🔍 Validating multibagger performance...")
        
        validation_results = []
        
        for i, signal in enumerate(signals, 1):
            print(f"[{i}/{len(signals)}] Validating {signal['symbol']}...")
            
            # Load stock data
            stock_data = self.load_stock_data(signal['symbol'])
            
            if stock_data is None:
                continue
                
            # Calculate returns
            returns_data = self.calculate_returns_over_time(signal, stock_data)
            
            if returns_data is None:
                continue
                
            # Classify multibagger level
            multibagger_level = self.classify_multibagger_level(returns_data['max_return'])
            
            # Add classification to results
            returns_data['multibagger_level'] = multibagger_level
            returns_data['is_multibagger'] = returns_data['max_return'] >= 100  # 2x or more
            
            validation_results.append(returns_data)
            
            # Print quick result
            print(f"  ✅ Max Return: {returns_data['max_return']:.1f}% ({multibagger_level}) on {returns_data['max_return_date']}")
            
        print(f"✅ Validation completed for {len(validation_results)} signals")
        return validation_results
        
    def analyze_results(self, validation_results):
        """Analyze validation results"""
        print("📊 Analyzing validation results...")
        
        if not validation_results:
            return None
            
        # Overall statistics
        total_signals = len(validation_results)
        multibaggers = [r for r in validation_results if r['is_multibagger']]
        positive_returns = [r for r in validation_results if r['max_return'] > 0]
        
        # Multibagger breakdown
        multibagger_breakdown = {}
        for level in ['20x+', '10x', '5x', '3x', '2x', '1.5x', 'Positive', 'Loss']:
            count = len([r for r in validation_results if r['multibagger_level'] == level])
            multibagger_breakdown[level] = {
                'count': count,
                'percentage': count / total_signals * 100 if total_signals > 0 else 0
            }
            
        # Performance statistics
        max_returns = [r['max_return'] for r in validation_results]
        ml_probabilities = [r['ml_probability'] for r in validation_results]
        
        analysis = {
            'total_signals': total_signals,
            'multibaggers_count': len(multibaggers),
            'multibagger_rate': len(multibaggers) / total_signals * 100 if total_signals > 0 else 0,
            'positive_returns_count': len(positive_returns),
            'positive_rate': len(positive_returns) / total_signals * 100 if total_signals > 0 else 0,
            'multibagger_breakdown': multibagger_breakdown,
            'performance_stats': {
                'mean_return': np.mean(max_returns) if max_returns else 0,
                'median_return': np.median(max_returns) if max_returns else 0,
                'max_return': np.max(max_returns) if max_returns else 0,
                'min_return': np.min(max_returns) if max_returns else 0,
                'std_return': np.std(max_returns) if max_returns else 0
            },
            'ml_accuracy': {
                'mean_probability': np.mean(ml_probabilities) if ml_probabilities else 0,
                'median_probability': np.median(ml_probabilities) if ml_probabilities else 0,
                'correlation_prob_return': np.corrcoef(ml_probabilities, max_returns)[0, 1] if len(ml_probabilities) > 1 else 0
            }
        }
        
        return analysis
        
    def save_results(self, validation_results, analysis):
        """Save validation results"""
        print("💾 Saving validation results...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save detailed results
        results_file = f"{self.results_dir}/validation_results_{timestamp}.json"
        with open(results_file, 'w') as f:
            json.dump(validation_results, f, indent=2, default=str)
        print(f"✅ Saved detailed results to {results_file}")
        
        # Save analysis
        analysis_file = f"{self.results_dir}/validation_analysis_{timestamp}.json"
        with open(analysis_file, 'w') as f:
            json.dump(analysis, f, indent=2, default=str)
        print(f"✅ Saved analysis to {analysis_file}")
        
        # Save as CSV for easy viewing
        if validation_results:
            # Flatten data for CSV
            csv_data = []
            for result in validation_results:
                row = {
                    'symbol': result['symbol'],
                    'signal_date': result['signal_date'],
                    'entry_price': result['entry_price'],
                    'ml_probability': result['ml_probability'],
                    'max_return_pct': result['max_return'],
                    'max_return_date': result['max_return_date'],
                    'max_return_price': result['max_return_price'],
                    'multibagger_level': result['multibagger_level'],
                    'is_multibagger': result['is_multibagger']
                }
                
                # Add time-based returns
                for period, return_val in result['returns'].items():
                    row[f'return_{period}'] = return_val
                    
                csv_data.append(row)
                
            df = pd.DataFrame(csv_data)
            csv_file = f"{self.results_dir}/validation_results_{timestamp}.csv"
            df.to_csv(csv_file, index=False)
            print(f"✅ Saved CSV results to {csv_file}")
            
        return results_file
        
    def generate_validation_report(self, validation_results, analysis):
        """Generate comprehensive validation report"""
        
        if not validation_results or not analysis:
            return "❌ No validation results to report"
            
        # Sort by max return for top performers
        top_performers = sorted(validation_results, key=lambda x: x['max_return'], reverse=True)
        
        report = f"""
🎯 MULTIBAGGER VALIDATION REPORT (2019-2025)
============================================

📊 OVERALL PERFORMANCE
- Total Signals Tested: {analysis['total_signals']}
- Multibaggers (≥2x): {analysis['multibaggers_count']} ({analysis['multibagger_rate']:.1f}%)
- Positive Returns: {analysis['positive_returns_count']} ({analysis['positive_rate']:.1f}%)
- ML Model Success Rate: {analysis['multibagger_rate']:.1f}%

🚀 MULTIBAGGER BREAKDOWN
"""
        
        for level, data in analysis['multibagger_breakdown'].items():
            if data['count'] > 0:
                report += f"- {level:<8}: {data['count']:>2} signals ({data['percentage']:>5.1f}%)\n"
                
        report += f"""
📈 PERFORMANCE STATISTICS
- Average Return: {analysis['performance_stats']['mean_return']:>8.1f}%
- Median Return:  {analysis['performance_stats']['median_return']:>8.1f}%
- Best Return:    {analysis['performance_stats']['max_return']:>8.1f}%
- Worst Return:   {analysis['performance_stats']['min_return']:>8.1f}%
- Std Deviation:  {analysis['performance_stats']['std_return']:>8.1f}%

🤖 ML MODEL ACCURACY
- Average ML Probability: {analysis['ml_accuracy']['mean_probability']:>6.1%}
- Median ML Probability:  {analysis['ml_accuracy']['median_probability']:>6.1%}
- Correlation (Prob vs Return): {analysis['ml_accuracy']['correlation_prob_return']:>6.3f}

🏆 ALL PERFORMERS (Ranked by Return)
"""
        
        for i, result in enumerate(top_performers, 1):
            report += f"""
{i:2d}. {result['symbol']:<12} | {result['multibagger_level']:<4} | {result['max_return']:>7.1f}% | ML: {result['ml_probability']:>5.1%}
    Entry: ₹{result['entry_price']:>8.2f} → Peak: ₹{result['max_return_price']:>8.2f} | Date: {result['max_return_date']}
"""
        
        # Show time-based performance for top performers
        if len(top_performers) >= 3:
            report += f"\n📅 TIME-BASED RETURNS (TOP 3 PERFORMERS)\n"
            
            for i, result in enumerate(top_performers[:3], 1):
                report += f"\n{i}. {result['symbol']} (ML: {result['ml_probability']:.1%}):\n"
                
                time_labels = {
                    '1_month': '1M', '3_months': '3M', '6_months': '6M', 
                    '1_year': '1Y', '2_years': '2Y', '3_years': '3Y',
                    '4_years': '4Y', '5_years': '5Y', '6_years': '6Y'
                }
                
                returns_line = "   "
                for period, return_val in result['returns'].items():
                    label = time_labels.get(period, period)
                    returns_line += f"{label}: {return_val:>7.1f}%  "
                    
                report += returns_line + "\n"
                    
        report += f"""

🎯 VALIDATION CONCLUSION
- ML Model Accuracy: {'✅ EXCELLENT' if analysis['multibagger_rate'] >= 60 else '✅ GOOD' if analysis['multibagger_rate'] >= 40 else '⚡ MODERATE' if analysis['multibagger_rate'] >= 20 else '❌ POOR'}
- Multibagger Rate: {analysis['multibagger_rate']:.1f}% (Target: ≥20%)
- Positive Rate: {analysis['positive_rate']:.1f}% (Target: ≥70%)

🚀 RECOMMENDATION
"""
        
        if analysis['multibagger_rate'] >= 40 and analysis['positive_rate'] >= 70:
            report += """✅ DEPLOY TO PRODUCTION
- Model shows excellent predictive accuracy
- Ready for live trading with current data
- Recommend retraining with 2014-2025 data"""
        elif analysis['multibagger_rate'] >= 20 and analysis['positive_rate'] >= 60:
            report += """⚡ CONDITIONAL DEPLOYMENT
- Model shows good predictive accuracy
- Consider smaller position sizes initially
- Monitor performance closely"""
        else:
            report += """❌ NEEDS IMPROVEMENT
- Model accuracy below acceptable threshold
- Recommend feature engineering improvements
- Consider additional training data"""
            
        report += f"""

📁 FILES SAVED
- validation_results/validation_results_*.json
- validation_results/validation_analysis_*.json  
- validation_results/validation_results_*.csv

🎉 VALIDATION COMPLETE!
"""
        
        return report
        
    def run_validation(self):
        """Run complete validation process"""
        print("🚀 Starting Multibagger Validation (2019-2025)")
        print("=" * 60)
        
        # Step 1: Load 2019 signals
        signals = self.load_2019_signals()
        if not signals:
            return False
            
        # Step 2: Validate all signals
        validation_results = self.validate_all_signals(signals)
        
        if not validation_results:
            print("❌ No validation results generated")
            return False
            
        # Step 3: Analyze results
        analysis = self.analyze_results(validation_results)
        
        # Step 4: Save results
        results_file = self.save_results(validation_results, analysis)
        
        # Step 5: Generate report
        report = self.generate_validation_report(validation_results, analysis)
        
        print("\n" + "=" * 60)
        print(report)
        print("=" * 60)
        
        # Save report
        report_file = f"multibagger_validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_file, 'w') as f:
            f.write(report)
            
        print(f"\n✅ VALIDATION COMPLETED!")
        print(f"📊 Multibagger Rate: {analysis['multibagger_rate']:.1f}%")
        print(f"📈 Positive Rate: {analysis['positive_rate']:.1f}%")
        print(f"📁 Results saved in {self.results_dir}/")
        
        # Decision on next steps
        if analysis['multibagger_rate'] >= 20 and analysis['positive_rate'] >= 60:
            print("\n🚀 VALIDATION PASSED! Ready for production deployment.")
            return True
        else:
            print("\n⚠️ VALIDATION NEEDS REVIEW. Check results before deployment.")
            return False

if __name__ == "__main__":
    validator = MultibaggerValidatorFixed()
    success = validator.run_validation()
    
    if success:
        print("\n🎉 Next: Run retrain_with_latest_data.py for production deployment")
    else:
        print("\n🔧 Next: Review results and improve model if needed")
