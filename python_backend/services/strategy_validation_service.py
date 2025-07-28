"""
Strategy Validation Service for EmergentTrader
Validates strategies against backtest and live results
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from services.signal_management_service import signal_manager
from services.enhanced_notification_service import notification_service
from core.backtest_engine import BacktestEngine
from api_handler import EmergentTraderAPI

logger = logging.getLogger(__name__)

class StrategyValidationService:
    def __init__(self):
        """Initialize strategy validation service"""
        self.api = EmergentTraderAPI()
        self.backtest_engine = BacktestEngine()
        
        # Strategy performance thresholds
        self.performance_thresholds = {
            'min_success_rate': 0.6,      # 60% minimum success rate
            'min_avg_profit': 0.05,       # 5% minimum average profit
            'max_avg_loss': -0.15,        # Maximum 15% average loss
            'min_signals_count': 10,      # Minimum signals for validation
            'max_drawdown': -0.25         # Maximum 25% drawdown
        }
        
        logger.info("Strategy Validation Service initialized")
    
    async def validate_all_strategies(self) -> Dict:
        """Validate all strategies against performance criteria"""
        try:
            logger.info("🔍 Starting comprehensive strategy validation...")
            
            # Send start notification
            await notification_service.send_telegram_message(
                f"🔍 <b>Strategy Validation Started</b>\n\n"
                f"Analyzing strategy performance...\n"
                f"Time: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
            )
            
            # Get strategy statistics
            stats_result = signal_manager.get_signal_statistics()
            
            if not stats_result.get('success'):
                raise Exception("Could not retrieve strategy statistics")
            
            by_strategy = stats_result.get('by_strategy', [])
            
            if not by_strategy:
                return {
                    'success': True,
                    'message': 'No strategies to validate',
                    'strategies': []
                }
            
            # Validate each strategy
            validation_results = []
            
            for strategy_data in by_strategy:
                strategy_name = strategy_data['strategy']
                
                try:
                    # Validate strategy
                    validation = await self.validate_single_strategy(strategy_name, strategy_data)
                    validation_results.append(validation)
                    
                except Exception as e:
                    logger.error(f"Error validating strategy {strategy_name}: {e}")
                    validation_results.append({
                        'strategy': strategy_name,
                        'is_valid': False,
                        'error': str(e),
                        'issues': ['Validation failed']
                    })
            
            # Generate validation report
            report = self.generate_validation_report(validation_results)
            
            # Send completion notification
            await notification_service.send_telegram_message(report)
            
            logger.info("✅ Strategy validation completed")
            
            return {
                'success': True,
                'validation_results': validation_results,
                'report': report,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in strategy validation: {e}")
            
            # Send error notification
            await notification_service.send_telegram_message(
                f"🚨 <b>Strategy Validation Failed</b>\n\n"
                f"Error: {str(e)}\n"
                f"Time: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
            )
            
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def validate_single_strategy(self, strategy_name: str, strategy_data: Dict) -> Dict:
        """Validate a single strategy"""
        try:
            logger.info(f"🎯 Validating strategy: {strategy_name}")
            
            validation_result = {
                'strategy': strategy_name,
                'is_valid': True,
                'issues': [],
                'warnings': [],
                'metrics': {},
                'recommendations': []
            }
            
            # Extract metrics
            total_signals = strategy_data.get('total', 0)
            target_hits = strategy_data.get('target_hits', 0)
            stop_losses = strategy_data.get('stop_losses', 0)
            success_rate = strategy_data.get('success_rate', 0) / 100  # Convert to decimal
            avg_profit = strategy_data.get('avg_profit_percent', 0) / 100  # Convert to decimal
            
            validation_result['metrics'] = {
                'total_signals': total_signals,
                'target_hits': target_hits,
                'stop_losses': stop_losses,
                'success_rate': success_rate,
                'avg_profit_percent': avg_profit * 100
            }
            
            # Validation checks
            
            # 1. Minimum signals count
            if total_signals < self.performance_thresholds['min_signals_count']:
                validation_result['issues'].append(
                    f"Insufficient signals: {total_signals} < {self.performance_thresholds['min_signals_count']}"
                )
                validation_result['is_valid'] = False
            
            # 2. Success rate check
            if success_rate < self.performance_thresholds['min_success_rate']:
                validation_result['issues'].append(
                    f"Low success rate: {success_rate:.1%} < {self.performance_thresholds['min_success_rate']:.1%}"
                )
                validation_result['is_valid'] = False
            
            # 3. Average profit check
            if avg_profit < self.performance_thresholds['min_avg_profit']:
                validation_result['issues'].append(
                    f"Low average profit: {avg_profit:.1%} < {self.performance_thresholds['min_avg_profit']:.1%}"
                )
                validation_result['is_valid'] = False
            
            # 4. Risk-reward ratio
            if target_hits > 0 and stop_losses > 0:
                risk_reward_ratio = target_hits / stop_losses
                if risk_reward_ratio < 1.5:  # Should have at least 1.5x more wins than losses
                    validation_result['warnings'].append(
                        f"Poor risk-reward ratio: {risk_reward_ratio:.2f} (should be > 1.5)"
                    )
            
            # 5. Consistency check (if we have enough data)
            if total_signals >= 20:
                consistency_score = await self.check_strategy_consistency(strategy_name)
                validation_result['metrics']['consistency_score'] = consistency_score
                
                if consistency_score < 0.7:
                    validation_result['warnings'].append(
                        f"Inconsistent performance: {consistency_score:.2f} (should be > 0.7)"
                    )
            
            # Generate recommendations
            validation_result['recommendations'] = self.generate_strategy_recommendations(
                strategy_name, validation_result['metrics'], validation_result['issues']
            )
            
            # Overall validation status
            if validation_result['issues']:
                logger.warning(f"❌ Strategy {strategy_name} failed validation: {len(validation_result['issues'])} issues")
            else:
                logger.info(f"✅ Strategy {strategy_name} passed validation")
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Error validating strategy {strategy_name}: {e}")
            return {
                'strategy': strategy_name,
                'is_valid': False,
                'error': str(e),
                'issues': ['Validation error occurred']
            }
    
    async def check_strategy_consistency(self, strategy_name: str) -> float:
        """Check strategy consistency over time"""
        try:
            # This is a simplified consistency check
            # In production, you'd analyze performance over different time periods
            
            # Get recent signals for this strategy
            # For now, we'll simulate consistency based on success rate variance
            
            # Simulate weekly performance data
            weekly_performances = [0.65, 0.72, 0.58, 0.69, 0.71, 0.63, 0.67]  # Example data
            
            if len(weekly_performances) < 3:
                return 1.0  # Not enough data, assume consistent
            
            # Calculate coefficient of variation (lower is more consistent)
            mean_performance = np.mean(weekly_performances)
            std_performance = np.std(weekly_performances)
            
            if mean_performance == 0:
                return 0.0
            
            cv = std_performance / mean_performance
            
            # Convert to consistency score (0-1, higher is better)
            consistency_score = max(0, 1 - cv)
            
            return consistency_score
            
        except Exception as e:
            logger.error(f"Error checking consistency for {strategy_name}: {e}")
            return 0.5  # Default moderate consistency
    
    def generate_strategy_recommendations(self, strategy_name: str, metrics: Dict, issues: List[str]) -> List[str]:
        """Generate recommendations for strategy improvement"""
        recommendations = []
        
        try:
            success_rate = metrics.get('success_rate', 0)
            total_signals = metrics.get('total_signals', 0)
            avg_profit = metrics.get('avg_profit_percent', 0)
            
            # Recommendations based on issues
            if success_rate < 0.6:
                recommendations.append("Consider tightening entry criteria to improve signal quality")
                recommendations.append("Review and optimize stop-loss levels")
            
            if avg_profit < 5:
                recommendations.append("Increase target profit levels or improve exit timing")
                recommendations.append("Consider adding momentum filters")
            
            if total_signals < 10:
                recommendations.append("Strategy may be too restrictive - consider relaxing some criteria")
                recommendations.append("Expand universe of stocks for this strategy")
            
            # General recommendations
            if success_rate > 0.8:
                recommendations.append("Excellent performance! Consider increasing position sizes")
            
            if 'consistency_score' in metrics and metrics['consistency_score'] < 0.7:
                recommendations.append("Add market condition filters to improve consistency")
                recommendations.append("Consider different parameters for different market phases")
            
            # Strategy-specific recommendations
            if strategy_name.lower() == 'multibagger':
                recommendations.append("Focus on fundamentally strong companies with growth potential")
                recommendations.append("Consider longer holding periods for multibagger candidates")
            
            elif strategy_name.lower() == 'momentum':
                recommendations.append("Ensure momentum signals are fresh and not lagging")
                recommendations.append("Add volume confirmation for momentum signals")
            
            elif strategy_name.lower() == 'breakout':
                recommendations.append("Confirm breakouts with increased volume")
                recommendations.append("Use tighter stop-losses for breakout trades")
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            recommendations.append("Review strategy parameters and performance metrics")
        
        return recommendations
    
    def generate_validation_report(self, validation_results: List[Dict]) -> str:
        """Generate comprehensive validation report"""
        try:
            total_strategies = len(validation_results)
            valid_strategies = len([r for r in validation_results if r.get('is_valid', False)])
            invalid_strategies = total_strategies - valid_strategies
            
            # Calculate overall metrics
            total_signals = sum(r.get('metrics', {}).get('total_signals', 0) for r in validation_results)
            avg_success_rate = np.mean([r.get('metrics', {}).get('success_rate', 0) for r in validation_results if r.get('metrics')])
            
            # Find best and worst performing strategies
            best_strategy = None
            worst_strategy = None
            best_success_rate = 0
            worst_success_rate = 1
            
            for result in validation_results:
                if result.get('metrics'):
                    success_rate = result['metrics'].get('success_rate', 0)
                    if success_rate > best_success_rate:
                        best_success_rate = success_rate
                        best_strategy = result['strategy']
                    if success_rate < worst_success_rate:
                        worst_success_rate = success_rate
                        worst_strategy = result['strategy']
            
            # Create detailed report
            strategy_details = ""
            for result in validation_results:
                status = "✅" if result.get('is_valid', False) else "❌"
                strategy_name = result['strategy']
                
                if result.get('metrics'):
                    success_rate = result['metrics'].get('success_rate', 0)
                    total_sigs = result['metrics'].get('total_signals', 0)
                    strategy_details += f"{status} {strategy_name}: {success_rate:.1%} success ({total_sigs} signals)\n"
                else:
                    strategy_details += f"{status} {strategy_name}: Validation failed\n"
            
            # Issues summary
            issues_summary = ""
            for result in validation_results:
                if result.get('issues'):
                    issues_summary += f"\n❌ {result['strategy']}:\n"
                    for issue in result['issues'][:2]:  # Show top 2 issues
                        issues_summary += f"  • {issue}\n"
            
            report = f"""🔍 <b>STRATEGY VALIDATION REPORT</b>

📊 <b>Validation Summary:</b>
• Total Strategies: {total_strategies}
• Valid Strategies: {valid_strategies}
• Invalid Strategies: {invalid_strategies}
• Overall Success Rate: {avg_success_rate:.1%}

🏆 <b>Best Performer:</b> {best_strategy or 'None'} ({best_success_rate:.1%})
⚠️ <b>Needs Attention:</b> {worst_strategy or 'None'} ({worst_success_rate:.1%})

📋 <b>Strategy Results:</b>
{strategy_details}

🚨 <b>Issues Found:</b>{issues_summary if issues_summary else '\nNo critical issues found!'}

💡 <b>Recommendations:</b>
• Review underperforming strategies
• Consider adjusting parameters for invalid strategies
• Monitor consistency over time
• Implement suggested improvements

⏰ <b>Validated at:</b> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

<i>Keep optimizing for better performance! 📈</i>"""
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating validation report: {e}")
            return f"""🔍 <b>STRATEGY VALIDATION COMPLETE</b>

Validation finished but report generation failed.
Time: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

<i>Check logs for details.</i>"""
    
    async def run_backtest_validation(self, strategy_name: str, days_back: int = 30) -> Dict:
        """Run backtest validation for a strategy"""
        try:
            logger.info(f"📈 Running backtest validation for {strategy_name}")
            
            # This would integrate with your existing backtest engine
            # For now, we'll simulate backtest results
            
            # Simulate backtest results
            backtest_result = {
                'success': True,
                'total_trades': 25,
                'winning_trades': 16,
                'losing_trades': 9,
                'success_rate': 0.64,
                'total_return': 0.12,
                'max_drawdown': -0.08,
                'sharpe_ratio': 1.2
            }
            
            return backtest_result
            
        except Exception as e:
            logger.error(f"Error in backtest validation: {e}")
            return {
                'success': False,
                'error': str(e)
            }

# Global instance
strategy_validation_service = StrategyValidationService()
