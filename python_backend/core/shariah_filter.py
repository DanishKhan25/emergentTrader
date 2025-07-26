"""
Shariah Compliance Filter - Filters stocks based on Islamic finance principles
Screens stocks based on business activities and financial ratios
"""

import json
import logging
from typing import Dict, List, Optional, Set
from datetime import datetime

logger = logging.getLogger(__name__)

class ShariahFilter:
    def __init__(self, config_path: Optional[str] = None):
        self.name = "Shariah Compliance Filter"
        
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
    
    def check_business_activity(self, stock_info: Dict) -> bool:
        """
        Check if company's business activities are Shariah compliant
        
        Args:
            stock_info: Dictionary containing stock information
            
        Returns:
            True if compliant, False otherwise
        """
        try:
            sector = stock_info.get('sector', '').lower()
            industry = stock_info.get('industry', '').lower()
            company_name = stock_info.get('company_name', '').lower()
            
            # Check against prohibited sectors
            for prohibited in self.prohibited_sectors:
                if (prohibited in sector or 
                    prohibited in industry or 
                    prohibited in company_name):
                    logger.info(f"Stock failed business activity check: {prohibited} found")
                    return False
            
            # Specific checks for financial institutions
            if any(keyword in sector for keyword in ['bank', 'financial', 'insurance']):
                # Allow Islamic banks and Shariah-compliant financial institutions
                if not any(keyword in company_name for keyword in ['islamic', 'shariah', 'takaful']):
                    logger.info("Conventional financial institution - not Shariah compliant")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking business activity: {str(e)}")
            return False
    
    def check_financial_ratios(self, stock_info: Dict) -> Dict:
        """
        Check if company's financial ratios meet Shariah compliance standards
        
        Args:
            stock_info: Dictionary containing financial information
            
        Returns:
            Dictionary with ratio check results
        """
        try:
            market_cap = stock_info.get('market_cap', 0)
            debt_to_equity = stock_info.get('debt_to_equity', 0)
            
            if market_cap == 0:
                return {
                    'compliant': False,
                    'reason': 'Market cap data not available',
                    'debt_ratio': None,
                    'interest_income_ratio': None,
                    'liquid_assets_ratio': None
                }
            
            # Calculate debt ratio (approximation using debt-to-equity)
            # Debt ratio = Total Debt / Market Cap
            # We approximate using debt-to-equity ratio
            estimated_debt_ratio = debt_to_equity / (1 + debt_to_equity) if debt_to_equity > 0 else 0
            
            ratios_check = {
                'debt_ratio': estimated_debt_ratio,
                'debt_ratio_compliant': estimated_debt_ratio <= self.max_debt_ratio,
                'interest_income_ratio': 0,  # Not available from yfinance
                'interest_income_ratio_compliant': True,  # Assume compliant for now
                'liquid_assets_ratio': 0,  # Not available from yfinance  
                'liquid_assets_ratio_compliant': True  # Assume compliant for now
            }
            
            # Overall compliance
            ratios_check['compliant'] = (
                ratios_check['debt_ratio_compliant'] and
                ratios_check['interest_income_ratio_compliant'] and
                ratios_check['liquid_assets_ratio_compliant']
            )
            
            if not ratios_check['compliant']:
                if not ratios_check['debt_ratio_compliant']:
                    ratios_check['reason'] = f"Debt ratio ({estimated_debt_ratio:.2%}) exceeds limit ({self.max_debt_ratio:.2%})"
                else:
                    ratios_check['reason'] = "Financial ratios not compliant"
            
            return ratios_check
            
        except Exception as e:
            logger.error(f"Error checking financial ratios: {str(e)}")
            return {
                'compliant': False,
                'reason': f'Error calculating ratios: {str(e)}',
                'debt_ratio': None,
                'interest_income_ratio': None,
                'liquid_assets_ratio': None
            }
    
    def is_shariah_compliant(self, stock_info: Dict) -> Dict:
        """
        Comprehensive Shariah compliance check
        
        Args:
            stock_info: Dictionary containing stock information
            
        Returns:
            Dictionary with compliance result and details
        """
        try:
            symbol = stock_info.get('symbol', 'Unknown')
            
            # Business activity check
            business_compliant = self.check_business_activity(stock_info)
            
            # Financial ratios check
            ratios_result = self.check_financial_ratios(stock_info)
            ratios_compliant = ratios_result['compliant']
            
            # Overall compliance
            overall_compliant = business_compliant and ratios_compliant
            
            compliance_result = {
                'symbol': symbol,
                'shariah_compliant': overall_compliant,
                'business_activity_compliant': business_compliant,
                'financial_ratios_compliant': ratios_compliant,
                'compliance_score': self._calculate_compliance_score(stock_info),
                'check_date': datetime.now().isoformat(),
                'details': {
                    'sector': stock_info.get('sector', ''),
                    'industry': stock_info.get('industry', ''),
                    'debt_ratio': ratios_result.get('debt_ratio', 0),
                    'ratios_details': ratios_result
                }
            }
            
            if not overall_compliant:
                reasons = []
                if not business_compliant:
                    reasons.append("Business activity not compliant")
                if not ratios_compliant:
                    reasons.append(ratios_result.get('reason', 'Financial ratios not compliant'))
                compliance_result['non_compliance_reasons'] = reasons
            
            logger.info(f"Shariah compliance check for {symbol}: {overall_compliant}")
            return compliance_result
            
        except Exception as e:
            logger.error(f"Error in Shariah compliance check: {str(e)}")
            return {
                'symbol': stock_info.get('symbol', 'Unknown'),
                'shariah_compliant': False,
                'error': str(e),
                'check_date': datetime.now().isoformat()
            }
    
    def _calculate_compliance_score(self, stock_info: Dict) -> float:
        """
        Calculate a compliance score from 0-1 based on how well
        the stock meets Shariah criteria
        
        Args:
            stock_info: Stock information dictionary
            
        Returns:
            Compliance score between 0 and 1
        """
        try:
            score = 1.0
            
            # Business activity score
            if not self.check_business_activity(stock_info):
                score = 0.0
                return score
            
            # Financial ratios score
            debt_to_equity = stock_info.get('debt_to_equity', 0)
            if debt_to_equity > 0:
                estimated_debt_ratio = debt_to_equity / (1 + debt_to_equity)
                if estimated_debt_ratio > self.max_debt_ratio:
                    # Penalize based on how much it exceeds the limit
                    excess_ratio = estimated_debt_ratio - self.max_debt_ratio
                    penalty = min(excess_ratio * 2, 0.5)  # Max 50% penalty
                    score -= penalty
            
            return max(score, 0.0)
            
        except Exception as e:
            logger.error(f"Error calculating compliance score: {str(e)}")
            return 0.0
    
    def get_shariah_universe(self, stock_universe: List[str], stock_fetcher) -> List[Dict]:
        """
        Filter a universe of stocks for Shariah compliance
        
        Args:
            stock_universe: List of stock symbols to check
            stock_fetcher: YFinanceFetcher instance to get stock data
            
        Returns:
            List of Shariah compliant stocks with compliance details
        """
        compliant_stocks = []
        
        for symbol in stock_universe:
            try:
                # Get stock information
                stock_info = stock_fetcher.get_stock_info(symbol)
                
                if not stock_info:
                    continue
                
                # Check compliance
                compliance_result = self.is_shariah_compliant(stock_info)
                
                if compliance_result['shariah_compliant']:
                    compliant_stocks.append({
                        'symbol': symbol,
                        'company_name': stock_info.get('company_name', ''),
                        'sector': stock_info.get('sector', ''),
                        'market_cap': stock_info.get('market_cap', 0),
                        'compliance_score': compliance_result['compliance_score'],
                        'compliance_details': compliance_result
                    })
                
                logger.info(f"Processed {symbol}: {'Compliant' if compliance_result['shariah_compliant'] else 'Not Compliant'}")
                
            except Exception as e:
                logger.error(f"Error processing {symbol}: {str(e)}")
                continue
        
        # Sort by compliance score and market cap
        compliant_stocks.sort(key=lambda x: (-x['compliance_score'], -x['market_cap']))
        
        logger.info(f"Found {len(compliant_stocks)} Shariah compliant stocks out of {len(stock_universe)} checked")
        return compliant_stocks