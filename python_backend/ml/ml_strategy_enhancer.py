#!/usr/bin/env python3
"""
ML Strategy Enhancer - Adds ML capabilities to all trading strategies
Provides unified ML enhancement for all 10 trading strategies
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf
from typing import Dict, List, Optional, Tuple, Any
import logging
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score
import joblib
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class MLStrategyEnhancer:
    """
    ML Strategy Enhancer - Adds ML capabilities to all trading strategies
    
    Features:
    - Strategy-specific ML models for each of the 10 strategies
    - Feature engineering for different strategy types
    - Confidence scoring and signal quality assessment
    - Market regime detection and adaptation
    - Real-time ML inference for signal enhancement
    """
    
    def __init__(self, enable_training: bool = False):
        self.enable_training = enable_training
        self.models = {}
        self.scalers = {}
        self.feature_extractors = {}
        self.strategy_configs = {}
        
        # Initialize strategy-specific configurations
        self._initialize_strategy_configs()
        
        # Initialize ML models for each strategy
        self._initialize_ml_models()
        
        logger.info("ML Strategy Enhancer initialized with support for all 10 strategies")
    
    def _initialize_strategy_configs(self):
        """Initialize ML configurations for each strategy"""
        self.strategy_configs = {
            'multibagger': {
                'features': ['growth_score', 'momentum_score', 'value_score', 'quality_score', 'market_cap_score'],
                'target_return': 2.0,  # 2x return target
                'holding_period': 365,  # 1 year
                'success_threshold': 0.8
            },
            'momentum': {
                'features': ['price_momentum', 'volume_momentum', 'rsi', 'macd', 'trend_strength'],
                'target_return': 0.3,  # 30% return target
                'holding_period': 60,  # 2 months
                'success_threshold': 0.75
            },
            'swing_trading': {
                'features': ['swing_high_low', 'volatility', 'support_resistance', 'oscillator_signals', 'volume_profile'],
                'target_return': 0.15,  # 15% return target
                'holding_period': 21,  # 3 weeks
                'success_threshold': 0.7
            },
            'breakout': {
                'features': ['breakout_strength', 'volume_surge', 'consolidation_time', 'resistance_level', 'momentum_confirmation'],
                'target_return': 0.25,  # 25% return target
                'holding_period': 45,  # 6 weeks
                'success_threshold': 0.72
            },
            'mean_reversion': {
                'features': ['oversold_level', 'deviation_from_mean', 'bounce_probability', 'support_strength', 'market_sentiment'],
                'target_return': 0.12,  # 12% return target
                'holding_period': 30,  # 1 month
                'success_threshold': 0.68
            },
            'value_investing': {
                'features': ['pe_ratio', 'pb_ratio', 'debt_equity', 'roe', 'dividend_yield', 'intrinsic_value_score'],
                'target_return': 0.5,  # 50% return target
                'holding_period': 180,  # 6 months
                'success_threshold': 0.78
            },
            'fundamental_growth': {
                'features': ['revenue_growth', 'profit_growth', 'eps_growth', 'market_expansion', 'competitive_advantage'],
                'target_return': 0.4,  # 40% return target
                'holding_period': 120,  # 4 months
                'success_threshold': 0.76
            },
            'sector_rotation': {
                'features': ['sector_momentum', 'relative_strength', 'economic_indicators', 'sector_rotation_signal', 'market_cycle'],
                'target_return': 0.2,  # 20% return target
                'holding_period': 90,  # 3 months
                'success_threshold': 0.73
            },
            'low_volatility': {
                'features': ['volatility_score', 'beta', 'sharpe_ratio', 'max_drawdown', 'consistency_score'],
                'target_return': 0.18,  # 18% return target
                'holding_period': 150,  # 5 months
                'success_threshold': 0.8
            },
            'pivot_cpr': {
                'features': ['pivot_levels', 'cpr_width', 'price_action', 'support_resistance_strength', 'intraday_momentum'],
                'target_return': 0.08,  # 8% return target
                'holding_period': 14,  # 2 weeks
                'success_threshold': 0.65
            }
        }
    
    def _initialize_ml_models(self):
        """Initialize ML models for each strategy"""
        for strategy_name, config in self.strategy_configs.items():
            # Create strategy-specific model
            if strategy_name in ['multibagger', 'value_investing', 'fundamental_growth']:
                # Use Gradient Boosting for long-term strategies
                model = GradientBoostingClassifier(
                    n_estimators=100,
                    learning_rate=0.1,
                    max_depth=6,
                    random_state=42
                )
            else:
                # Use Random Forest for short-term strategies
                model = RandomForestClassifier(
                    n_estimators=100,
                    max_depth=8,
                    random_state=42
                )
            
            self.models[strategy_name] = model
            self.scalers[strategy_name] = StandardScaler()
            
            # Initialize feature extractor
            self.feature_extractors[strategy_name] = self._create_feature_extractor(strategy_name)
        
        logger.info(f"Initialized ML models for {len(self.models)} strategies")
    
    def _create_feature_extractor(self, strategy_name: str):
        """Create feature extractor for specific strategy"""
        def extract_features(stock_data: Dict, price_data: pd.DataFrame = None) -> Dict:
            """Extract strategy-specific features"""
            features = {}
            
            try:
                if strategy_name == 'multibagger':
                    features.update(self._extract_multibagger_features(stock_data, price_data))
                elif strategy_name == 'momentum':
                    features.update(self._extract_momentum_features(stock_data, price_data))
                elif strategy_name == 'swing_trading':
                    features.update(self._extract_swing_features(stock_data, price_data))
                elif strategy_name == 'breakout':
                    features.update(self._extract_breakout_features(stock_data, price_data))
                elif strategy_name == 'mean_reversion':
                    features.update(self._extract_mean_reversion_features(stock_data, price_data))
                elif strategy_name == 'value_investing':
                    features.update(self._extract_value_features(stock_data, price_data))
                elif strategy_name == 'fundamental_growth':
                    features.update(self._extract_growth_features(stock_data, price_data))
                elif strategy_name == 'sector_rotation':
                    features.update(self._extract_sector_features(stock_data, price_data))
                elif strategy_name == 'low_volatility':
                    features.update(self._extract_volatility_features(stock_data, price_data))
                elif strategy_name == 'pivot_cpr':
                    features.update(self._extract_pivot_features(stock_data, price_data))
                
                # Add common features
                features.update(self._extract_common_features(stock_data, price_data))
                
            except Exception as e:
                logger.error(f"Error extracting features for {strategy_name}: {str(e)}")
                # Return default features
                for feature_name in self.strategy_configs[strategy_name]['features']:
                    features[feature_name] = 0.5
            
            return features
        
    
    def _extract_multibagger_features(self, stock_data: Dict, price_data: pd.DataFrame) -> Dict:
        """Extract multibagger-specific features"""
        features = {}
        
        # Growth metrics
        revenue_growth = stock_data.get('revenue_growth', 0)
        profit_growth = stock_data.get('profit_growth', 0)
        features['growth_score'] = min((revenue_growth + profit_growth) / 40, 1.0)
        
        # Momentum score
        if price_data is not None and len(price_data) > 60:
            price_change_3m = (price_data['Close'].iloc[-1] / price_data['Close'].iloc[-60] - 1)
            features['momentum_score'] = min(max(price_change_3m, -1), 1)
        else:
            features['momentum_score'] = 0.5
        
        # Value score (inverse of PE)
        pe_ratio = stock_data.get('pe_ratio', 20)
        features['value_score'] = max(0, 1 - (pe_ratio / 50))
        
        # Quality score
        roe = stock_data.get('roe', 10)
        debt_equity = stock_data.get('debt_equity', 0.5)
        features['quality_score'] = min(roe / 25, 1) * max(0, 1 - debt_equity)
        
        # Market cap score (favor small/mid cap)
        market_cap = stock_data.get('market_cap', 10000000000)
        if market_cap < 5000000000:  # Small cap
            features['market_cap_score'] = 1.0
        elif market_cap < 20000000000:  # Mid cap
            features['market_cap_score'] = 0.8
        else:  # Large cap
            features['market_cap_score'] = 0.4
        
        return features
    
    def _extract_momentum_features(self, stock_data: Dict, price_data: pd.DataFrame) -> Dict:
        """Extract momentum-specific features"""
        features = {}
        
        if price_data is not None and len(price_data) > 30:
            # Price momentum
            price_change_1m = (price_data['Close'].iloc[-1] / price_data['Close'].iloc[-20] - 1)
            features['price_momentum'] = min(max(price_change_1m * 2, -1), 1)
            
            # Volume momentum
            avg_volume_recent = price_data['Volume'].iloc[-10:].mean()
            avg_volume_older = price_data['Volume'].iloc[-30:-10].mean()
            volume_ratio = avg_volume_recent / max(avg_volume_older, 1)
            features['volume_momentum'] = min(volume_ratio / 3, 1)
            
            # RSI
            delta = price_data['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            features['rsi'] = rsi.iloc[-1] / 100 if not pd.isna(rsi.iloc[-1]) else 0.5
            
            # MACD
            exp1 = price_data['Close'].ewm(span=12).mean()
            exp2 = price_data['Close'].ewm(span=26).mean()
            macd = exp1 - exp2
            features['macd'] = min(max(macd.iloc[-1] / price_data['Close'].iloc[-1], -0.1), 0.1) * 10
            
            # Trend strength
            sma_20 = price_data['Close'].rolling(20).mean()
            trend_strength = (price_data['Close'].iloc[-1] / sma_20.iloc[-1] - 1)
            features['trend_strength'] = min(max(trend_strength * 5, -1), 1)
        else:
            # Default values
            for feature in ['price_momentum', 'volume_momentum', 'rsi', 'macd', 'trend_strength']:
                features[feature] = 0.5
        
        return features
    
    def _extract_swing_features(self, stock_data: Dict, price_data: pd.DataFrame) -> Dict:
        """Extract swing trading features"""
        features = {}
        
        if price_data is not None and len(price_data) > 20:
            # Swing high/low analysis
            highs = price_data['High'].rolling(5).max()
            lows = price_data['Low'].rolling(5).min()
            current_price = price_data['Close'].iloc[-1]
            
            # Position in swing range
            recent_high = highs.iloc[-10:].max()
            recent_low = lows.iloc[-10:].min()
            swing_position = (current_price - recent_low) / max(recent_high - recent_low, 1)
            features['swing_high_low'] = swing_position
            
            # Volatility
            returns = price_data['Close'].pct_change()
            volatility = returns.rolling(20).std().iloc[-1]
            features['volatility'] = min(volatility * 100, 1)
            
            # Support/Resistance strength
            support_level = lows.iloc[-20:].min()
            resistance_level = highs.iloc[-20:].max()
            sr_strength = (resistance_level - support_level) / current_price
            features['support_resistance'] = min(sr_strength * 10, 1)
            
            # Oscillator signals (Stochastic)
            low_14 = price_data['Low'].rolling(14).min()
            high_14 = price_data['High'].rolling(14).max()
            k_percent = 100 * ((current_price - low_14.iloc[-1]) / (high_14.iloc[-1] - low_14.iloc[-1]))
            features['oscillator_signals'] = k_percent / 100
            
            # Volume profile
            volume_sma = price_data['Volume'].rolling(20).mean()
            volume_ratio = price_data['Volume'].iloc[-1] / volume_sma.iloc[-1]
            features['volume_profile'] = min(volume_ratio / 2, 1)
        else:
            for feature in ['swing_high_low', 'volatility', 'support_resistance', 'oscillator_signals', 'volume_profile']:
                features[feature] = 0.5
        
        return features
    
    def _extract_breakout_features(self, stock_data: Dict, price_data: pd.DataFrame) -> Dict:
        """Extract breakout-specific features"""
        features = {}
        
        if price_data is not None and len(price_data) > 30:
            current_price = price_data['Close'].iloc[-1]
            
            # Breakout strength
            resistance_level = price_data['High'].rolling(20).max().iloc[-1]
            breakout_strength = max(0, (current_price - resistance_level) / resistance_level)
            features['breakout_strength'] = min(breakout_strength * 10, 1)
            
            # Volume surge
            avg_volume = price_data['Volume'].rolling(20).mean().iloc[-1]
            current_volume = price_data['Volume'].iloc[-1]
            volume_surge = current_volume / max(avg_volume, 1)
            features['volume_surge'] = min(volume_surge / 3, 1)
            
            # Consolidation time
            price_range = price_data['High'].rolling(20).max() - price_data['Low'].rolling(20).min()
            avg_range = price_range.mean()
            recent_range = price_range.iloc[-1]
            consolidation_score = 1 - (recent_range / max(avg_range, 1))
            features['consolidation_time'] = max(0, consolidation_score)
            
            # Resistance level strength
            touches = sum(1 for price in price_data['High'].iloc[-20:] if abs(price - resistance_level) / resistance_level < 0.02)
            features['resistance_level'] = min(touches / 5, 1)
            
            # Momentum confirmation
            sma_10 = price_data['Close'].rolling(10).mean().iloc[-1]
            momentum_conf = (current_price - sma_10) / sma_10
            features['momentum_confirmation'] = min(max(momentum_conf * 5, -1), 1)
        else:
            for feature in ['breakout_strength', 'volume_surge', 'consolidation_time', 'resistance_level', 'momentum_confirmation']:
                features[feature] = 0.5
        
        return features
    
    def _extract_mean_reversion_features(self, stock_data: Dict, price_data: pd.DataFrame) -> Dict:
        """Extract mean reversion features"""
        features = {}
        
        if price_data is not None and len(price_data) > 30:
            current_price = price_data['Close'].iloc[-1]
            
            # Oversold level (RSI-based)
            delta = price_data['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            oversold_level = max(0, (30 - rsi.iloc[-1]) / 30) if not pd.isna(rsi.iloc[-1]) else 0.5
            features['oversold_level'] = oversold_level
            
            # Deviation from mean
            sma_20 = price_data['Close'].rolling(20).mean().iloc[-1]
            deviation = (sma_20 - current_price) / sma_20
            features['deviation_from_mean'] = min(max(deviation * 2, -1), 1)
            
            # Bounce probability (Bollinger Bands)
            sma = price_data['Close'].rolling(20).mean()
            std = price_data['Close'].rolling(20).std()
            lower_band = sma - (2 * std)
            distance_to_lower = (current_price - lower_band.iloc[-1]) / max(lower_band.iloc[-1], 1)
            features['bounce_probability'] = max(0, 1 - distance_to_lower * 5)
            
            # Support strength
            support_level = price_data['Low'].rolling(20).min().iloc[-1]
            support_distance = (current_price - support_level) / current_price
            features['support_strength'] = 1 - min(support_distance * 10, 1)
            
            # Market sentiment (volume-price)
            volume_weighted_price = (price_data['Close'] * price_data['Volume']).rolling(10).sum() / price_data['Volume'].rolling(10).sum()
            sentiment = (current_price - volume_weighted_price.iloc[-1]) / current_price
            features['market_sentiment'] = min(max(sentiment * 10, -1), 1)
        else:
            for feature in ['oversold_level', 'deviation_from_mean', 'bounce_probability', 'support_strength', 'market_sentiment']:
                features[feature] = 0.5
        
        return features
    
    def _extract_value_features(self, stock_data: Dict, price_data: pd.DataFrame) -> Dict:
        """Extract value investing features"""
        features = {}
        
        # PE Ratio score (lower is better)
        pe_ratio = stock_data.get('pe_ratio', 20)
        features['pe_ratio'] = max(0, 1 - (pe_ratio / 30))
        
        # PB Ratio score (lower is better)
        pb_ratio = stock_data.get('pb_ratio', 2)
        features['pb_ratio'] = max(0, 1 - (pb_ratio / 3))
        
        # Debt to Equity (lower is better)
        debt_equity = stock_data.get('debt_equity', 0.5)
        features['debt_equity'] = max(0, 1 - debt_equity)
        
        # ROE (higher is better)
        roe = stock_data.get('roe', 15)
        features['roe'] = min(roe / 25, 1)
        
        # Dividend Yield
        dividend_yield = stock_data.get('dividend_yield', 2)
        features['dividend_yield'] = min(dividend_yield / 5, 1)
        
        # Intrinsic value score
        book_value = stock_data.get('book_value', 100)
        current_price = stock_data.get('current_price', 100)
        intrinsic_score = book_value / max(current_price, 1)
        features['intrinsic_value_score'] = min(intrinsic_score, 2) / 2
        
        return features
    
    def _extract_growth_features(self, stock_data: Dict, price_data: pd.DataFrame) -> Dict:
        """Extract fundamental growth features"""
        features = {}
        
        # Revenue growth
        revenue_growth = stock_data.get('revenue_growth', 10)
        features['revenue_growth'] = min(revenue_growth / 30, 1)
        
        # Profit growth
        profit_growth = stock_data.get('profit_growth', 15)
        features['profit_growth'] = min(profit_growth / 40, 1)
        
        # EPS growth
        eps_growth = stock_data.get('eps_growth', 12)
        features['eps_growth'] = min(eps_growth / 35, 1)
        
        # Market expansion (proxy using market cap growth)
        market_cap = stock_data.get('market_cap', 10000000000)
        sector_avg_cap = stock_data.get('sector_avg_market_cap', market_cap)
        market_expansion = market_cap / max(sector_avg_cap, 1)
        features['market_expansion'] = min(market_expansion, 2) / 2
        
        # Competitive advantage (ROE vs sector average)
        roe = stock_data.get('roe', 15)
        sector_avg_roe = stock_data.get('sector_avg_roe', 12)
        competitive_advantage = roe / max(sector_avg_roe, 1)
        features['competitive_advantage'] = min(competitive_advantage, 2) / 2
        
        return features
    
    def _extract_sector_features(self, stock_data: Dict, price_data: pd.DataFrame) -> Dict:
        """Extract sector rotation features"""
        features = {}
        
        # Sector momentum (relative to market)
        sector_performance = stock_data.get('sector_performance', 0.1)
        market_performance = stock_data.get('market_performance', 0.08)
        sector_momentum = (sector_performance - market_performance) / max(abs(market_performance), 0.01)
        features['sector_momentum'] = min(max(sector_momentum, -1), 1)
        
        # Relative strength
        stock_return = stock_data.get('stock_return_3m', 0.1)
        sector_return = stock_data.get('sector_return_3m', 0.08)
        relative_strength = (stock_return - sector_return) / max(abs(sector_return), 0.01)
        features['relative_strength'] = min(max(relative_strength, -1), 1)
        
        # Economic indicators (simplified)
        gdp_growth = stock_data.get('gdp_growth', 6.5)
        inflation = stock_data.get('inflation', 4.0)
        economic_score = (gdp_growth - inflation) / 10
        features['economic_indicators'] = min(max(economic_score, -1), 1)
        
        # Sector rotation signal
        sector_rank = stock_data.get('sector_rank', 5)  # Out of 10 sectors
        features['sector_rotation_signal'] = (10 - sector_rank) / 10
        
        # Market cycle position
        market_cycle = stock_data.get('market_cycle_position', 0.5)  # 0-1 scale
        features['market_cycle'] = market_cycle
        
        return features
    
    def _extract_volatility_features(self, stock_data: Dict, price_data: pd.DataFrame) -> Dict:
        """Extract low volatility features"""
        features = {}
        
        if price_data is not None and len(price_data) > 60:
            returns = price_data['Close'].pct_change()
            
            # Volatility score (lower is better)
            volatility = returns.rolling(30).std().iloc[-1]
            features['volatility_score'] = max(0, 1 - (volatility * 100))
            
            # Beta (lower is better for low vol strategy)
            market_returns = returns  # Simplified - should be market index
            beta = returns.rolling(60).cov(market_returns).iloc[-1] / market_returns.rolling(60).var().iloc[-1]
            features['beta'] = max(0, 1 - abs(beta))
            
            # Sharpe ratio
            risk_free_rate = 0.06 / 252  # 6% annual risk-free rate
            excess_returns = returns - risk_free_rate
            sharpe = excess_returns.mean() / max(returns.std(), 0.001)
            features['sharpe_ratio'] = min(max(sharpe / 2, -1), 1)
            
            # Max drawdown
            cumulative = (1 + returns).cumprod()
            running_max = cumulative.expanding().max()
            drawdown = (cumulative - running_max) / running_max
            max_drawdown = abs(drawdown.min())
            features['max_drawdown'] = max(0, 1 - (max_drawdown * 5))
            
            # Consistency score
            positive_days = (returns > 0).sum()
            total_days = len(returns.dropna())
            consistency = positive_days / max(total_days, 1)
            features['consistency_score'] = consistency
        else:
            for feature in ['volatility_score', 'beta', 'sharpe_ratio', 'max_drawdown', 'consistency_score']:
                features[feature] = 0.5
        
        return features
    
    def _extract_pivot_features(self, stock_data: Dict, price_data: pd.DataFrame) -> Dict:
        """Extract pivot CPR features"""
        features = {}
        
        if price_data is not None and len(price_data) > 5:
            # Calculate pivot levels
            high = price_data['High'].iloc[-2]  # Previous day
            low = price_data['Low'].iloc[-2]
            close = price_data['Close'].iloc[-2]
            
            pivot = (high + low + close) / 3
            bc = (high + low) / 2
            tc = (pivot - bc) + pivot
            
            current_price = price_data['Close'].iloc[-1]
            
            # Pivot levels score
            pivot_distance = abs(current_price - pivot) / current_price
            features['pivot_levels'] = max(0, 1 - (pivot_distance * 20))
            
            # CPR width (narrower is better for breakout)
            cpr_width = (tc - bc) / current_price
            features['cpr_width'] = max(0, 1 - (cpr_width * 50))
            
            # Price action relative to CPR
            if bc <= current_price <= tc:
                price_action_score = 0.5  # Inside CPR
            elif current_price > tc:
                price_action_score = 0.8  # Above CPR (bullish)
            else:
                price_action_score = 0.2  # Below CPR (bearish)
            features['price_action'] = price_action_score
            
            # Support/Resistance strength
            sr_levels = [pivot, bc, tc]
            min_distance = min(abs(current_price - level) / current_price for level in sr_levels)
            features['support_resistance_strength'] = 1 - min(min_distance * 100, 1)
            
            # Intraday momentum
            if len(price_data) > 1:
                intraday_change = (current_price - price_data['Close'].iloc[-2]) / price_data['Close'].iloc[-2]
                features['intraday_momentum'] = min(max(intraday_change * 10, -1), 1)
            else:
                features['intraday_momentum'] = 0.5
        else:
            for feature in ['pivot_levels', 'cpr_width', 'price_action', 'support_resistance_strength', 'intraday_momentum']:
                features[feature] = 0.5
        
        return features
    
    def _extract_common_features(self, stock_data: Dict, price_data: pd.DataFrame) -> Dict:
        """Extract common features used across strategies"""
        features = {}
        
        # Market cap category
        market_cap = stock_data.get('market_cap', 10000000000)
        if market_cap < 5000000000:
            features['market_cap_category'] = 0.8  # Small cap
        elif market_cap < 50000000000:
            features['market_cap_category'] = 0.6  # Mid cap
        else:
            features['market_cap_category'] = 0.4  # Large cap
        
        # Liquidity score
        avg_volume = stock_data.get('avg_volume', 1000000)
        features['liquidity_score'] = min(avg_volume / 10000000, 1)
        
        # Market sentiment
        market_trend = stock_data.get('market_trend', 0.05)
        features['market_sentiment'] = min(max(market_trend * 10, -1), 1)
        
        return features
    
    def enhance_signal_with_ml(self, strategy_name: str, signal: Dict, stock_data: Dict, price_data: pd.DataFrame = None) -> Dict:
        """
        Enhance a trading signal with ML predictions
        
        Args:
            strategy_name: Name of the trading strategy
            signal: Original signal from strategy
            stock_data: Stock fundamental data
            price_data: Historical price data
            
        Returns:
            Enhanced signal with ML confidence and adjustments
        """
        try:
            if strategy_name not in self.models:
                logger.warning(f"No ML model found for strategy: {strategy_name}")
                return signal
            
            # Extract features
            features = self.feature_extractors[strategy_name](stock_data, price_data)
            
            # Prepare feature vector
            feature_names = self.strategy_configs[strategy_name]['features']
            feature_vector = []
            
            for feature_name in feature_names:
                feature_vector.append(features.get(feature_name, 0.5))
            
            # Scale features
            feature_vector = np.array(feature_vector).reshape(1, -1)
            scaled_features = self.scalers[strategy_name].transform(feature_vector)
            
            # Get ML prediction
            ml_confidence = self.models[strategy_name].predict_proba(scaled_features)[0][1]  # Probability of success
            
            # Enhance signal
            enhanced_signal = signal.copy()
            enhanced_signal['ml_confidence'] = float(ml_confidence)
            enhanced_signal['ml_enhanced'] = True
            enhanced_signal['original_confidence'] = signal.get('confidence_score', 0.5)
            
            # Combine original and ML confidence
            combined_confidence = (signal.get('confidence_score', 0.5) * 0.6) + (ml_confidence * 0.4)
            enhanced_signal['confidence_score'] = combined_confidence
            
            # Add ML reasoning
            enhanced_signal['ml_reasoning'] = self._generate_ml_reasoning(strategy_name, features, ml_confidence)
            
            # Adjust targets based on ML confidence
            if ml_confidence > 0.8:
                # High confidence - increase targets
                enhanced_signal['target_multiplier'] = 1.2
            elif ml_confidence < 0.4:
                # Low confidence - reduce targets
                enhanced_signal['target_multiplier'] = 0.8
            else:
                enhanced_signal['target_multiplier'] = 1.0
            
            logger.info(f"Enhanced {strategy_name} signal for {signal.get('symbol', 'Unknown')} - ML confidence: {ml_confidence:.3f}")
            
            return enhanced_signal
            
        except Exception as e:
            logger.error(f"Error enhancing signal with ML: {str(e)}")
            return signal
    
    def _generate_ml_reasoning(self, strategy_name: str, features: Dict, ml_confidence: float) -> str:
        """Generate human-readable ML reasoning"""
        try:
            config = self.strategy_configs[strategy_name]
            feature_names = config['features']
            
            # Find top contributing features
            top_features = sorted([(name, features.get(name, 0.5)) for name in feature_names], 
                                key=lambda x: x[1], reverse=True)[:3]
            
            reasoning_parts = []
            
            if ml_confidence > 0.8:
                reasoning_parts.append(f"High ML confidence ({ml_confidence:.1%}) based on strong")
            elif ml_confidence > 0.6:
                reasoning_parts.append(f"Good ML confidence ({ml_confidence:.1%}) supported by")
            else:
                reasoning_parts.append(f"Moderate ML confidence ({ml_confidence:.1%}) with mixed")
            
            feature_descriptions = {
                'growth_score': 'growth metrics',
                'momentum_score': 'price momentum',
                'value_score': 'valuation attractiveness',
                'quality_score': 'financial quality',
                'volatility_score': 'low volatility profile',
                'breakout_strength': 'breakout confirmation',
                'oversold_level': 'oversold conditions',
                'sector_momentum': 'sector outperformance'
            }
            
            feature_desc = []
            for feature_name, score in top_features:
                desc = feature_descriptions.get(feature_name, feature_name.replace('_', ' '))
                feature_desc.append(f"{desc} ({score:.1%})")
            
            reasoning_parts.append(", ".join(feature_desc))
            
            return " ".join(reasoning_parts) + "."
            
        except Exception as e:
            return f"ML analysis completed with {ml_confidence:.1%} confidence."
    
    def get_strategy_ml_performance(self, strategy_name: str) -> Dict:
        """Get ML performance metrics for a strategy"""
        if strategy_name not in self.models:
            return {'error': f'No ML model found for {strategy_name}'}
        
        config = self.strategy_configs[strategy_name]
        
        return {
            'strategy': strategy_name,
            'ml_enabled': True,
            'features_count': len(config['features']),
            'target_return': config['target_return'],
            'holding_period_days': config['holding_period'],
            'success_threshold': config['success_threshold'],
            'model_type': type(self.models[strategy_name]).__name__,
            'features': config['features']
        }
    
    def get_all_ml_performance(self) -> Dict:
        """Get ML performance for all strategies"""
        performance = {}
        
        for strategy_name in self.strategy_configs.keys():
            performance[strategy_name] = self.get_strategy_ml_performance(strategy_name)
        
        return {
            'total_strategies': len(self.strategy_configs),
            'ml_enabled_strategies': len([s for s in performance.values() if s.get('ml_enabled', False)]),
            'strategies': performance
        }

# Initialize global ML enhancer
ml_enhancer = MLStrategyEnhancer()

def enhance_signal_with_ml(strategy_name: str, signal: Dict, stock_data: Dict, price_data: pd.DataFrame = None) -> Dict:
    """Global function to enhance signals with ML"""
    return ml_enhancer.enhance_signal_with_ml(strategy_name, signal, stock_data, price_data)

def get_ml_performance_summary() -> Dict:
    """Get ML performance summary for all strategies"""
    return ml_enhancer.get_all_ml_performance()
