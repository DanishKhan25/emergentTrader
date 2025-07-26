"""
Enhanced Shariah Compliance Filter - Advanced filtering with caching and fallback logic
Implements 3-month caching, robust fallback mechanisms, and comprehensive error handling
"""

import json
import logging
from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime, timedelta
from enum import Enum

from .data_cache import cache

logger = logging.getLogger(__name__)

class ComplianceStatus(Enum):
    """Enum for Shariah compliance status"""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    UNKNOWN = "unknown"  # When data is insufficient
    ERROR = "error"      # When there's a system error

class EnhancedShariahFilter:
    def __init__(self, config_path: Optional[str] = None):
        self.name = "Enhanced Shariah Compliance Filter"
        
        # Default Shariah compliance criteria
        self.prohibited_sectors = {
            'alcohol', 'tobacco', 'gambling', 'adult entertainment', 
            'conventional banking', 'insurance', 'weapons', 'pork',
            'interest-based finance', 'casinos', 'lottery'
        }
        
        # Financial ratio limits (based on AAOIFI standards)
        self.max_debt_ratio = 0.33  # Total debt / Market cap < 33%
        self.max_interest_income_ratio = 0.05  # Interest income / Total revenue < 5%
        self.max_liquid_assets_ratio = 0.33  # Liquid assets / Market cap < 33%
        
        # Fallback data sources for when primary data fails
        self.fallback_sources = [
            'cached_fundamental_data',
            'sector_classification',
            'industry_mapping',
            'manual_override'
        ]
        
        # Load custom config if provided
        if config_path:
            self.load_config(config_path)
    
    def load_config(self, config_path: str):
        """Load Shariah compliance configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                
            self.prohibited_sectors.update(config.get('prohibited_sectors', []))
            ratios = config.get('financial_ratios', {})
            
            self.max_debt_ratio = ratios.get('max_debt_ratio', self.max_debt_ratio)
            self.max_interest_income_ratio = ratios.get('max_interest_income_ratio', self.max_interest_income_ratio)
            self.max_liquid_assets_ratio = ratios.get('max_liquid_assets_ratio', self.max_liquid_assets_ratio)
            
            logger.info(f"Loaded Shariah compliance config from {config_path}")
            
        except Exception as e:
            logger.error(f"Error loading Shariah config: {str(e)}")
    
    def get_cached_compliance(self, symbol: str, force_refresh: bool = False) -> Optional[Dict]:
        """
        Get cached Shariah compliance data with 3-month TTL
        
        Args:
            symbol: Stock symbol
            force_refresh: Force refresh of cached data
            
        Returns:
            Cached compliance data or None if not found/expired
        """
        if force_refresh:
            cache.delete('shariah_compliance', symbol)
            return None
        
        cached_data = cache.get('shariah_compliance', symbol)
        
        if cached_data:
            # Check if cache is within 3-month window
            check_date = datetime.fromisoformat(cached_data.get('check_date', ''))
            if datetime.now() - check_date < timedelta(days=90):  # 3 months
                logger.debug(f"Using cached Shariah compliance for {symbol}")
                return cached_data
            else:
                logger.debug(f"Cached Shariah compliance expired for {symbol}")
                cache.delete('shariah_compliance', symbol)
        
        return None
    
    def set_cached_compliance(self, symbol: str, compliance_data: Dict) -> bool:
        """Cache Shariah compliance data"""
        return cache.set('shariah_compliance', symbol, compliance_data)
    
    def check_business_activity_with_fallback(self, stock_info: Dict, symbol: str) -> Tuple[bool, str, str]:
        """
        Check business activity compliance with fallback logic
        
        Returns:
            Tuple of (is_compliant, confidence_level, reason)
        """
        try:
            # Primary check using stock_info
            sector = stock_info.get('sector', '').lower()
            industry = stock_info.get('industry', '').lower()
            company_name = stock_info.get('company_name', '').lower()
            
            if sector and industry:  # We have good data
                for prohibited in self.prohibited_sectors:
                    if (prohibited in sector or 
                        prohibited in industry or 
                        prohibited in company_name):
                        return False, "high", f"Prohibited activity: {prohibited}"
                
                # Specific checks for financial institutions
                if any(keyword in sector for keyword in ['bank', 'financial', 'insurance']):
                    if not any(keyword in company_name for keyword in ['islamic', 'shariah', 'takaful']):
                        return False, "high", "Conventional financial institution"
                
                return True, "high", "Business activity compliant"
            
            # Fallback 1: Try cached fundamental data
            cached_fundamental = cache.get('stock_info', symbol)
            if cached_fundamental:
                logger.info(f"Using cached fundamental data for business activity check: {symbol}")
                return self.check_business_activity_with_fallback(cached_fundamental, symbol)
            
            # Fallback 2: Sector classification based on symbol patterns
            sector_guess = self._guess_sector_from_symbol(symbol)
            if sector_guess:
                logger.info(f"Using sector guess for {symbol}: {sector_guess}")
                for prohibited in self.prohibited_sectors:
                    if prohibited in sector_guess.lower():
                        return False, "medium", f"Likely prohibited sector: {sector_guess}"
                return True, "low", f"Likely compliant sector: {sector_guess}"
            
            # Fallback 3: Check manual override list
            manual_status = self._check_manual_override(symbol)
            if manual_status is not None:
                logger.info(f"Using manual override for {symbol}: {manual_status}")
                return manual_status, "high", "Manual override"
            
            # If all fallbacks fail, return unknown status
            logger.warning(f"Insufficient data for business activity check: {symbol}")
            return True, "unknown", "Insufficient data - defaulting to compliant pending review"
            
        except Exception as e:
            logger.error(f"Error in business activity check for {symbol}: {str(e)}")
            return True, "error", f"Error in check: {str(e)}"
    
    def check_financial_ratios_with_fallback(self, stock_info: Dict, symbol: str) -> Dict:
        """
        Check financial ratios with fallback logic
        
        Returns:
            Dictionary with ratio check results and confidence level
        """
        try:
            market_cap = stock_info.get('market_cap', 0)
            debt_to_equity = stock_info.get('debt_to_equity', 0)
            
            if market_cap > 0 and debt_to_equity is not None:
                # We have good financial data
                estimated_debt_ratio = debt_to_equity / (1 + debt_to_equity) if debt_to_equity > 0 else 0
                
                ratios_check = {
                    'debt_ratio': estimated_debt_ratio,
                    'debt_ratio_compliant': estimated_debt_ratio <= self.max_debt_ratio,
                    'interest_income_ratio': 0,  # Not available from yfinance
                    'interest_income_ratio_compliant': True,
                    'liquid_assets_ratio': 0,  # Not available from yfinance  
                    'liquid_assets_ratio_compliant': True,
                    'confidence_level': 'high',
                    'data_source': 'primary'
                }
                
                ratios_check['compliant'] = (
                    ratios_check['debt_ratio_compliant'] and
                    ratios_check['interest_income_ratio_compliant'] and
                    ratios_check['liquid_assets_ratio_compliant']
                )
                
                if not ratios_check['compliant']:
                    ratios_check['reason'] = f"Debt ratio ({estimated_debt_ratio:.2%}) exceeds limit ({self.max_debt_ratio:.2%})"
                
                return ratios_check
            
            # Fallback 1: Try cached financial data
            cached_info = cache.get('stock_info', symbol)
            if cached_info and cached_info.get('market_cap', 0) > 0:
                logger.info(f"Using cached financial data for ratios check: {symbol}")
                return self.check_financial_ratios_with_fallback(cached_info, symbol)
            
            # Fallback 2: Conservative assumption for unknown financial data
            logger.warning(f"Insufficient financial data for {symbol} - using conservative assumptions")
            return {
                'compliant': True,  # Conservative: assume compliant if no data
                'confidence_level': 'low',
                'data_source': 'assumption',
                'reason': 'Insufficient financial data - assumed compliant pending review',
                'debt_ratio': None,
                'interest_income_ratio': None,
                'liquid_assets_ratio': None,
                'debt_ratio_compliant': True,
                'interest_income_ratio_compliant': True,
                'liquid_assets_ratio_compliant': True
            }
            
        except Exception as e:
            logger.error(f"Error checking financial ratios for {symbol}: {str(e)}")
            return {
                'compliant': True,  # Conservative: assume compliant on error
                'confidence_level': 'error',
                'data_source': 'error',
                'reason': f'Error calculating ratios: {str(e)}',
                'debt_ratio': None,
                'interest_income_ratio': None,
                'liquid_assets_ratio': None
            }
    
    def is_shariah_compliant_enhanced(self, stock_info: Dict, symbol: str, force_refresh: bool = False) -> Dict:
        """
        Enhanced Shariah compliance check with caching and fallback logic
        
        Args:
            stock_info: Dictionary containing stock information
            symbol: Stock symbol
            force_refresh: Force refresh of cached data
            
        Returns:
            Dictionary with comprehensive compliance result
        """
        try:
            # Check cache first (unless force refresh)
            cached_result = self.get_cached_compliance(symbol, force_refresh)
            if cached_result:
                return cached_result
            
            # Business activity check with fallback
            business_compliant, business_confidence, business_reason = self.check_business_activity_with_fallback(
                stock_info, symbol
            )
            
            # Financial ratios check with fallback
            ratios_result = self.check_financial_ratios_with_fallback(stock_info, symbol)
            ratios_compliant = ratios_result['compliant']
            
            # Determine overall compliance status
            if business_confidence == "error" or ratios_result.get('confidence_level') == "error":
                compliance_status = ComplianceStatus.ERROR
                overall_compliant = None  # Unknown due to error
            elif business_confidence == "unknown" or ratios_result.get('confidence_level') == "low":
                compliance_status = ComplianceStatus.UNKNOWN
                overall_compliant = business_compliant and ratios_compliant  # Best guess
            else:
                compliance_status = ComplianceStatus.COMPLIANT if (business_compliant and ratios_compliant) else ComplianceStatus.NON_COMPLIANT
                overall_compliant = business_compliant and ratios_compliant
            
            # Calculate overall confidence
            confidence_levels = [business_confidence, ratios_result.get('confidence_level', 'low')]
            if 'error' in confidence_levels:
                overall_confidence = 'error'
            elif 'unknown' in confidence_levels:
                overall_confidence = 'unknown'
            elif 'low' in confidence_levels:
                overall_confidence = 'low'
            elif 'medium' in confidence_levels:
                overall_confidence = 'medium'
            else:
                overall_confidence = 'high'
            
            compliance_result = {
                'symbol': symbol,
                'shariah_compliant': overall_compliant,
                'compliance_status': compliance_status.value,
                'confidence_level': overall_confidence,
                'business_activity_compliant': business_compliant,
                'business_confidence': business_confidence,
                'business_reason': business_reason,
                'financial_ratios_compliant': ratios_compliant,
                'financial_confidence': ratios_result.get('confidence_level', 'low'),
                'compliance_score': self._calculate_compliance_score_enhanced(stock_info, overall_confidence),
                'check_date': datetime.now().isoformat(),
                'cache_expires': (datetime.now() + timedelta(days=90)).isoformat(),
                'details': {
                    'sector': stock_info.get('sector', ''),
                    'industry': stock_info.get('industry', ''),
                    'debt_ratio': ratios_result.get('debt_ratio', 0),
                    'ratios_details': ratios_result,
                    'data_sources_used': self._get_data_sources_used(stock_info, ratios_result)
                }
            }
            
            # Add non-compliance reasons if applicable
            if compliance_status == ComplianceStatus.NON_COMPLIANT:
                reasons = []
                if not business_compliant:
                    reasons.append(business_reason)
                if not ratios_compliant:
                    reasons.append(ratios_result.get('reason', 'Financial ratios not compliant'))
                compliance_result['non_compliance_reasons'] = reasons
            elif compliance_status == ComplianceStatus.UNKNOWN:
                compliance_result['review_required'] = True
                compliance_result['review_reason'] = "Insufficient data for definitive compliance determination"
            elif compliance_status == ComplianceStatus.ERROR:
                compliance_result['error_details'] = {
                    'business_error': business_reason if business_confidence == 'error' else None,
                    'financial_error': ratios_result.get('reason') if ratios_result.get('confidence_level') == 'error' else None
                }
            
            # Cache the result for 3 months
            self.set_cached_compliance(symbol, compliance_result)
            
            logger.info(f"Enhanced Shariah compliance check for {symbol}: {compliance_status.value} (confidence: {overall_confidence})")
            return compliance_result
            
        except Exception as e:
            logger.error(f"Critical error in enhanced Shariah compliance check for {symbol}: {str(e)}")
            
            # Return error status instead of defaulting to False
            error_result = {
                'symbol': symbol,
                'shariah_compliant': None,  # Unknown due to error
                'compliance_status': ComplianceStatus.ERROR.value,
                'confidence_level': 'error',
                'error': str(e),
                'check_date': datetime.now().isoformat(),
                'review_required': True,
                'review_reason': f'System error during compliance check: {str(e)}'
            }
            
            # Still cache error result to avoid repeated failures
            self.set_cached_compliance(symbol, error_result)
            return error_result
    
    def _guess_sector_from_symbol(self, symbol: str) -> Optional[str]:
        """Guess sector based on symbol patterns and known mappings"""
        symbol_patterns = {
            'BANK': 'Banking',
            'HDFC': 'Banking',
            'ICICI': 'Banking',
            'SBI': 'Banking',
            'KOTAK': 'Banking',
            'AXIS': 'Banking',
            'PHARMA': 'Pharmaceuticals',
            'TECH': 'Technology',
            'AUTO': 'Automobile',
            'STEEL': 'Steel',
            'CEMENT': 'Cement',
            'POWER': 'Power',
            'OIL': 'Oil & Gas',
            'GAS': 'Oil & Gas'
        }
        
        symbol_upper = symbol.upper()
        for pattern, sector in symbol_patterns.items():
            if pattern in symbol_upper:
                return sector
        
        return None
    
    def _check_manual_override(self, symbol: str) -> Optional[bool]:
        """Check manual override list for specific symbols"""
        # This could be loaded from a configuration file
        manual_overrides = {
            # Known compliant stocks
            'TCS': True,
            'INFY': True,
            'WIPRO': True,
            'HCLTECH': True,
            'TECHM': True,
            
            # Known non-compliant stocks
            'HDFCBANK': False,
            'ICICIBANK': False,
            'KOTAKBANK': False,
            'SBIN': False,
            'AXISBANK': False,
        }
        
        return manual_overrides.get(symbol.upper())
    
    def _calculate_compliance_score_enhanced(self, stock_info: Dict, confidence_level: str) -> float:
        """Calculate enhanced compliance score considering confidence level"""
        try:
            base_score = self._calculate_compliance_score(stock_info)
            
            # Adjust score based on confidence level
            confidence_multipliers = {
                'high': 1.0,
                'medium': 0.8,
                'low': 0.6,
                'unknown': 0.4,
                'error': 0.0
            }
            
            multiplier = confidence_multipliers.get(confidence_level, 0.5)
            return base_score * multiplier
            
        except Exception as e:
            logger.error(f"Error calculating enhanced compliance score: {str(e)}")
            return 0.0
    
    def _calculate_compliance_score(self, stock_info: Dict) -> float:
        """Original compliance score calculation"""
        try:
            score = 1.0
            
            # Business activity score
            if not self.check_business_activity_with_fallback(stock_info, stock_info.get('symbol', ''))[0]:
                score = 0.0
                return score
            
            # Financial ratios score
            debt_to_equity = stock_info.get('debt_to_equity', 0)
            if debt_to_equity > 0:
                estimated_debt_ratio = debt_to_equity / (1 + debt_to_equity)
                if estimated_debt_ratio > self.max_debt_ratio:
                    excess_ratio = estimated_debt_ratio - self.max_debt_ratio
                    penalty = min(excess_ratio * 2, 0.5)
                    score -= penalty
            
            return max(score, 0.0)
            
        except Exception as e:
            logger.error(f"Error calculating compliance score: {str(e)}")
            return 0.0
    
    def _get_data_sources_used(self, stock_info: Dict, ratios_result: Dict) -> List[str]:
        """Track which data sources were used for transparency"""
        sources = []
        
        if stock_info.get('sector') and stock_info.get('industry'):
            sources.append('primary_stock_info')
        
        if ratios_result.get('data_source'):
            sources.append(f"financial_{ratios_result['data_source']}")
        
        return sources
    
    def get_shariah_universe_enhanced(self, stock_universe: List[Dict], stock_fetcher, force_refresh: bool = False) -> List[Dict]:
        """
        Enhanced Shariah universe filtering with caching and fallback logic
        
        Args:
            stock_universe: List of stock dictionaries from NSE universe
            stock_fetcher: YFinanceFetcher instance to get stock data
            force_refresh: Force refresh of all cached compliance data
            
        Returns:
            List of Shariah compliant stocks with enhanced compliance details
        """
        compliant_stocks = []
        unknown_stocks = []
        error_stocks = []
        
        logger.info(f"Starting enhanced Shariah compliance check for {len(stock_universe)} stocks (force_refresh: {force_refresh})")
        
        for stock_dict in stock_universe:
            try:
                # Extract symbol from stock dictionary
                if isinstance(stock_dict, dict):
                    symbol = stock_dict.get('symbol', '')
                else:
                    symbol = str(stock_dict)
                
                if not symbol:
                    continue
                
                # Get stock information (with caching)
                stock_info = stock_fetcher.get_stock_info(symbol)
                
                if not stock_info:
                    logger.warning(f"No stock info available for {symbol}")
                    continue
                
                # Enhanced compliance check
                compliance_result = self.is_shariah_compliant_enhanced(stock_info, symbol, force_refresh)
                
                # Categorize based on compliance status
                if compliance_result['compliance_status'] == ComplianceStatus.COMPLIANT.value:
                    compliant_stocks.append({
                        'symbol': symbol,
                        'company_name': stock_info.get('company_name', ''),
                        'sector': stock_info.get('sector', ''),
                        'market_cap': stock_info.get('market_cap', 0),
                        'compliance_score': compliance_result['compliance_score'],
                        'confidence_level': compliance_result['confidence_level'],
                        'compliance_details': compliance_result
                    })
                elif compliance_result['compliance_status'] == ComplianceStatus.UNKNOWN.value:
                    unknown_stocks.append({
                        'symbol': symbol,
                        'company_name': stock_info.get('company_name', ''),
                        'compliance_details': compliance_result,
                        'review_required': True
                    })
                elif compliance_result['compliance_status'] == ComplianceStatus.ERROR.value:
                    error_stocks.append({
                        'symbol': symbol,
                        'error': compliance_result.get('error', 'Unknown error'),
                        'compliance_details': compliance_result
                    })
                
                status_emoji = {
                    ComplianceStatus.COMPLIANT.value: '✅',
                    ComplianceStatus.NON_COMPLIANT.value: '❌',
                    ComplianceStatus.UNKNOWN.value: '❓',
                    ComplianceStatus.ERROR.value: '⚠️'
                }
                
                emoji = status_emoji.get(compliance_result['compliance_status'], '❓')
                logger.info(f"{emoji} {symbol}: {compliance_result['compliance_status']} (confidence: {compliance_result['confidence_level']})")
                
            except Exception as e:
                logger.error(f"Error processing {stock_dict}: {str(e)}")
                error_stocks.append({
                    'symbol': symbol if 'symbol' in locals() else 'unknown',
                    'error': str(e)
                })
                continue
        
        # Sort compliant stocks by compliance score and market cap
        compliant_stocks.sort(key=lambda x: (-x['compliance_score'], -x['market_cap']))
        
        # Log comprehensive summary
        logger.info(f"Enhanced Shariah compliance filtering completed:")
        logger.info(f"  ✅ Compliant: {len(compliant_stocks)} stocks")
        logger.info(f"  ❓ Unknown/Review needed: {len(unknown_stocks)} stocks")
        logger.info(f"  ⚠️  Errors: {len(error_stocks)} stocks")
        logger.info(f"  ❌ Non-compliant: {len(stock_universe) - len(compliant_stocks) - len(unknown_stocks) - len(error_stocks)} stocks")
        
        # Store summary for reporting
        summary = {
            'total_processed': len(stock_universe),
            'compliant_count': len(compliant_stocks),
            'unknown_count': len(unknown_stocks),
            'error_count': len(error_stocks),
            'processing_date': datetime.now().isoformat(),
            'force_refresh_used': force_refresh
        }
        
        cache.set('shariah_summary', 'latest', summary)
        
        return compliant_stocks
    
    def refresh_compliance_cache(self, symbols: List[str] = None) -> Dict:
        """
        Refresh Shariah compliance cache for specific symbols or all cached symbols
        
        Args:
            symbols: List of symbols to refresh, or None for all cached symbols
            
        Returns:
            Summary of refresh operation
        """
        try:
            if symbols is None:
                # Get all cached compliance symbols
                cache_stats = cache.get_cache_stats()
                symbols = []
                # This would need to be implemented in the cache class
                # For now, we'll work with provided symbols
            
            refreshed = []
            errors = []
            
            for symbol in symbols:
                try:
                    # Force refresh by deleting cache
                    cache.delete('shariah_compliance', symbol)
                    refreshed.append(symbol)
                    logger.info(f"Refreshed compliance cache for {symbol}")
                except Exception as e:
                    errors.append({'symbol': symbol, 'error': str(e)})
                    logger.error(f"Error refreshing cache for {symbol}: {str(e)}")
            
            summary = {
                'refreshed_count': len(refreshed),
                'error_count': len(errors),
                'refreshed_symbols': refreshed,
                'errors': errors,
                'refresh_date': datetime.now().isoformat()
            }
            
            logger.info(f"Cache refresh completed: {len(refreshed)} refreshed, {len(errors)} errors")
            return summary
            
        except Exception as e:
            logger.error(f"Error in cache refresh operation: {str(e)}")
            return {
                'error': str(e),
                'refresh_date': datetime.now().isoformat()
            }

# Backward compatibility
ShariahFilter = EnhancedShariahFilter
