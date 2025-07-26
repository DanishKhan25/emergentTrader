#!/usr/bin/env python3
"""
Feature Engineering System
Create comprehensive ML features from historical signals and outcomes
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf
import pickle
from typing import Dict, List, Optional
import logging
from sklearn.preprocessing import StandardScaler, LabelEncoder

# Add the python_backend directory to the path
try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
except NameError:
    parent_dir = os.getcwd()

sys.path.append(parent_dir)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FeatureEngineer:
    """Engineer comprehensive features for ML training"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoders = {}
        
        # Create directories
        os.makedirs('ml/data', exist_ok=True)
        os.makedirs('ml/features', exist_ok=True)
        
        logger.info("Feature engineer initialized")
    
    def create_base_features(self, outcomes_df: pd.DataFrame) -> pd.DataFrame:
        """Create base features from signals and outcomes"""
        logger.info("Creating base features...")
        
        df = outcomes_df.copy()
        
        # 1. Signal-based features
        df['confidence_score'] = df['original_confidence']
        df['strategy_encoded'] = self._encode_categorical(df['strategy'], 'strategy')
        
        # 2. Date-based features
        df['entry_date'] = pd.to_datetime(df['entry_date'])
        df['year'] = df['entry_date'].dt.year
        df['month'] = df['entry_date'].dt.month
        df['quarter'] = df['entry_date'].dt.quarter
        df['day_of_week'] = df['entry_date'].dt.dayofweek
        df['is_month_end'] = (df['entry_date'].dt.day > 25).astype(int)
        df['is_quarter_end'] = df['month'].isin([3, 6, 9, 12]).astype(int)
        df['is_earnings_season'] = df['month'].isin([1, 4, 7, 10]).astype(int)
        
        # 3. Price-based features
        df['entry_price_log'] = np.log(df['entry_price'] + 1)
        df['price_level'] = pd.cut(df['entry_price'], bins=5, labels=False)
        
        # 4. Volatility features
        df['volatility_level'] = pd.cut(df['volatility'], bins=5, labels=False)
        df['high_volatility'] = (df['volatility'] > df['volatility'].quantile(0.75)).astype(int)
        df['low_volatility'] = (df['volatility'] < df['volatility'].quantile(0.25)).astype(int)
        
        # 5. Return-based features (targets)
        df['positive_return'] = (df['return_pct'] > 0).astype(int)
        df['strong_positive_return'] = (df['return_pct'] > 0.05).astype(int)
        df['negative_return'] = (df['return_pct'] < 0).astype(int)
        df['strong_negative_return'] = (df['return_pct'] < -0.05).astype(int)
        
        # 6. Risk-adjusted features
        df['return_volatility_ratio'] = df['return_pct'] / (df['volatility'] + 0.001)
        df['sharpe_positive'] = (df['sharpe_ratio'] > 0).astype(int)
        df['high_sharpe'] = (df['sharpe_ratio'] > df['sharpe_ratio'].quantile(0.75)).astype(int)
        
        logger.info(f"Base features created: {df.shape[1]} columns")
        return df
    
    def add_market_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add market context features"""
        logger.info("Adding market context features...")
        
        # Get NIFTY data for market context
        nifty_data = self._get_nifty_context(df['entry_date'].min(), df['entry_date'].max())
        
        if nifty_data is not None:
            # Merge market data
            df = df.merge(nifty_data, left_on='entry_date', right_on='date', how='left')
            
            # Market regime features
            df['bull_market'] = (df['market_regime'] == 'BULL').astype(int)
            df['bear_market'] = (df['market_regime'] == 'BEAR').astype(int)
            df['sideways_market'] = (df['market_regime'] == 'SIDEWAYS').astype(int)
            df['high_vol_market'] = (df['market_regime'] == 'HIGH_VOLATILITY').astype(int)
            
            # Market momentum features
            df['market_momentum_positive'] = (df['market_momentum_20d'] > 0).astype(int)
            df['strong_market_momentum'] = (df['market_momentum_20d'] > 0.05).astype(int)
            df['market_momentum_level'] = pd.cut(df['market_momentum_20d'], bins=5, labels=False)
            
            # Market volatility features
            df['high_market_volatility'] = (df['market_volatility'] > 0.25).astype(int)
            df['low_market_volatility'] = (df['market_volatility'] < 0.15).astype(int)
            
        else:
            # Default market features if data unavailable
            df['bull_market'] = 0
            df['bear_market'] = 0
            df['sideways_market'] = 1
            df['high_vol_market'] = 0
            df['market_momentum_positive'] = 0
            df['strong_market_momentum'] = 0
            df['market_momentum_level'] = 2
            df['high_market_volatility'] = 0
            df['low_market_volatility'] = 1
            df['market_momentum_20d'] = 0
            df['market_volatility'] = 0.20
        
        logger.info(f"Market features added: {df.shape[1]} columns")
        return df
    
    def add_strategy_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add strategy-specific features"""
        logger.info("Adding strategy-specific features...")
        
        # Strategy performance features
        strategy_stats = df.groupby('strategy').agg({
            'success': ['mean', 'count'],
            'return_pct': ['mean', 'std'],
            'sharpe_ratio': 'mean',
            'volatility': 'mean'
        }).round(4)
        
        strategy_stats.columns = ['_'.join(col).strip() for col in strategy_stats.columns]
        strategy_stats = strategy_stats.reset_index()
        
        # Merge strategy statistics
        df = df.merge(strategy_stats, on='strategy', how='left')
        
        # Strategy interaction features
        df['confidence_x_strategy_success'] = df['confidence_score'] * df['success_mean']
        df['confidence_x_market_momentum'] = df['confidence_score'] * df['market_momentum_20d']
        
        # Strategy-market regime interactions
        df['momentum_in_bull'] = ((df['strategy'] == 'momentum') & (df['bull_market'] == 1)).astype(int)
        df['low_vol_in_bear'] = ((df['strategy'] == 'low_volatility') & (df['bear_market'] == 1)).astype(int)
        df['growth_in_bull'] = ((df['strategy'] == 'fundamental_growth') & (df['bull_market'] == 1)).astype(int)
        df['mean_reversion_in_sideways'] = ((df['strategy'] == 'mean_reversion') & (df['sideways_market'] == 1)).astype(int)
        df['breakout_in_bull'] = ((df['strategy'] == 'breakout') & (df['bull_market'] == 1)).astype(int)
        
        # Strategy confidence adjustments
        df['adjusted_confidence'] = df['confidence_score'] * df['success_mean']
        df['confidence_deviation'] = df['confidence_score'] - df['confidence_score'].mean()
        
        logger.info(f"Strategy features added: {df.shape[1]} columns")
        return df
    
    def add_technical_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add technical analysis features"""
        logger.info("Adding technical features...")
        
        # Extract technical features from signal metadata
        technical_features = []
        
        for idx, row in df.iterrows():
            try:
                symbol = row['symbol']
                entry_date = row['entry_date']
                
                # Get technical indicators for the entry date
                tech_features = self._calculate_technical_features(symbol, entry_date)
                tech_features['index'] = idx
                technical_features.append(tech_features)
                
                if len(technical_features) % 100 == 0:
                    logger.info(f"Processed technical features for {len(technical_features)} signals...")
                    
            except Exception as e:
                logger.error(f"Error calculating technical features for {symbol}: {str(e)}")
                # Default technical features
                tech_features = {
                    'index': idx,
                    'rsi': 50,
                    'macd': 0,
                    'bb_position': 0.5,
                    'sma_20_ratio': 1.0,
                    'sma_50_ratio': 1.0,
                    'volume_ratio': 1.0,
                    'price_momentum_5d': 0,
                    'price_momentum_20d': 0
                }
                technical_features.append(tech_features)
        
        # Convert to DataFrame and merge
        tech_df = pd.DataFrame(technical_features)
        df = df.merge(tech_df, left_index=True, right_on='index', how='left')
        df = df.drop('index', axis=1)
        
        # Technical feature engineering
        df['rsi_oversold'] = (df['rsi'] < 30).astype(int)
        df['rsi_overbought'] = (df['rsi'] > 70).astype(int)
        df['rsi_neutral'] = ((df['rsi'] >= 40) & (df['rsi'] <= 60)).astype(int)
        
        df['macd_positive'] = (df['macd'] > 0).astype(int)
        df['strong_macd'] = (abs(df['macd']) > 0.02).astype(int)
        
        df['bb_oversold'] = (df['bb_position'] < 0.2).astype(int)
        df['bb_overbought'] = (df['bb_position'] > 0.8).astype(int)
        
        df['above_sma20'] = (df['sma_20_ratio'] > 1.0).astype(int)
        df['above_sma50'] = (df['sma_50_ratio'] > 1.0).astype(int)
        df['sma_bullish'] = (df['sma_20_ratio'] > df['sma_50_ratio']).astype(int)
        
        df['high_volume'] = (df['volume_ratio'] > 1.5).astype(int)
        df['low_volume'] = (df['volume_ratio'] < 0.5).astype(int)
        
        df['positive_momentum_5d'] = (df['price_momentum_5d'] > 0).astype(int)
        df['positive_momentum_20d'] = (df['price_momentum_20d'] > 0).astype(int)
        df['strong_momentum'] = (df['price_momentum_20d'] > 0.05).astype(int)
        
        logger.info(f"Technical features added: {df.shape[1]} columns")
        return df
    
    def add_interaction_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add interaction features between different feature groups"""
        logger.info("Adding interaction features...")
        
        # Confidence interactions
        df['confidence_x_rsi'] = df['confidence_score'] * df['rsi'] / 100
        df['confidence_x_volatility'] = df['confidence_score'] * df['volatility']
        df['confidence_x_market_vol'] = df['confidence_score'] * df['market_volatility']
        
        # Technical interactions
        df['rsi_x_macd'] = df['rsi'] * df['macd']
        df['momentum_x_volume'] = df['price_momentum_20d'] * df['volume_ratio']
        df['volatility_x_momentum'] = df['volatility'] * df['price_momentum_20d']
        
        # Market interactions
        df['market_momentum_x_stock_momentum'] = df['market_momentum_20d'] * df['price_momentum_20d']
        df['market_vol_x_stock_vol'] = df['market_volatility'] * df['volatility']
        
        # Strategy-specific interactions
        df['momentum_strategy_x_bull_market'] = df['momentum_in_bull'] * df['market_momentum_20d']
        df['low_vol_strategy_x_market_vol'] = df['low_vol_in_bear'] * df['market_volatility']
        
        # Time-based interactions
        df['quarter_x_strategy'] = df['quarter'] * df['strategy_encoded']
        df['earnings_season_x_confidence'] = df['is_earnings_season'] * df['confidence_score']
        
        # Risk interactions
        df['sharpe_x_confidence'] = df['sharpe_ratio'] * df['confidence_score']
        df['return_vol_ratio_x_confidence'] = df['return_volatility_ratio'] * df['confidence_score']
        
        logger.info(f"Interaction features added: {df.shape[1]} columns")
        return df
    
    def create_target_variables(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create target variables for different ML tasks"""
        logger.info("Creating target variables...")
        
        # Primary classification targets
        df['target_success'] = df['success']  # Binary success (>2% return)
        df['target_profitable'] = (df['return_pct'] > 0).astype(int)  # Any profit
        df['target_strong_success'] = (df['return_pct'] > 0.10).astype(int)  # >10% return
        
        # Multi-class classification targets
        df['target_return_category'] = pd.cut(
            df['return_pct'], 
            bins=[-np.inf, -0.10, -0.02, 0.02, 0.10, np.inf],
            labels=['strong_loss', 'loss', 'neutral', 'gain', 'strong_gain']
        )
        
        # Regression targets
        df['target_return'] = df['return_pct']
        df['target_risk_adjusted_return'] = df['risk_adjusted_return']
        df['target_sharpe_ratio'] = df['sharpe_ratio']
        
        # Risk targets
        df['target_low_risk'] = (df['max_loss_pct'] > -0.05).astype(int)  # Max loss < 5%
        df['target_high_sharpe'] = (df['sharpe_ratio'] > 0.5).astype(int)
        
        logger.info(f"Target variables created: {df.shape[1]} columns")
        return df
    
    def _encode_categorical(self, series: pd.Series, column_name: str) -> pd.Series:
        """Encode categorical variables"""
        if column_name not in self.label_encoders:
            self.label_encoders[column_name] = LabelEncoder()
            return pd.Series(self.label_encoders[column_name].fit_transform(series))
        else:
            return pd.Series(self.label_encoders[column_name].transform(series))
    
    def _get_nifty_context(self, start_date: datetime, end_date: datetime) -> Optional[pd.DataFrame]:
        """Get NIFTY market context data"""
        try:
            nifty_data = yf.download('^NSEI', start=start_date - timedelta(days=300), 
                                   end=end_date + timedelta(days=10), progress=False)
            
            if nifty_data.empty:
                return None
            
            # Calculate market indicators
            nifty_data['sma_50'] = nifty_data['Close'].rolling(50).mean()
            nifty_data['sma_200'] = nifty_data['Close'].rolling(200).mean()
            
            # Market momentum
            nifty_data['market_momentum_20d'] = nifty_data['Close'].pct_change(20)
            nifty_data['market_momentum_50d'] = nifty_data['Close'].pct_change(50)
            
            # Market volatility
            returns = nifty_data['Close'].pct_change()
            nifty_data['market_volatility'] = returns.rolling(20).std() * np.sqrt(252)
            
            # Market regime
            conditions = [
                (nifty_data['sma_50'] > nifty_data['sma_200']) & (nifty_data['market_volatility'] < 0.20),
                (nifty_data['sma_50'] < nifty_data['sma_200']) & (nifty_data['market_volatility'] < 0.25),
                nifty_data['market_volatility'] > 0.25
            ]
            choices = ['BULL', 'BEAR', 'HIGH_VOLATILITY']
            nifty_data['market_regime'] = np.select(conditions, choices, default='SIDEWAYS')
            
            # Prepare for merge
            market_df = nifty_data.reset_index()
            market_df['date'] = market_df['Date'].dt.date
            market_df = market_df[['date', 'market_regime', 'market_momentum_20d', 
                                 'market_momentum_50d', 'market_volatility']].dropna()
            
            return market_df
            
        except Exception as e:
            logger.error(f"Error getting NIFTY context: {str(e)}")
            return None
    
    def _calculate_technical_features(self, symbol: str, entry_date: datetime) -> Dict:
        """Calculate technical features for a specific stock and date"""
        try:
            # Add .NS suffix for NSE stocks
            yf_symbol = f"{symbol}.NS"
            
            # Get historical data
            start_date = entry_date - timedelta(days=100)
            end_date = entry_date + timedelta(days=5)
            
            stock_data = yf.download(yf_symbol, start=start_date, end=end_date, progress=False)
            
            if stock_data.empty or len(stock_data) < 20:
                return self._default_technical_features()
            
            # Find the entry date index
            entry_idx = -1
            for i, date in enumerate(stock_data.index):
                if date.date() >= entry_date.date():
                    entry_idx = i
                    break
            
            if entry_idx == -1 or entry_idx == 0:
                return self._default_technical_features()
            
            # Calculate technical indicators up to entry date
            data_up_to_entry = stock_data.iloc[:entry_idx+1]
            
            # RSI
            delta = data_up_to_entry['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            current_rsi = rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50
            
            # MACD
            ema_12 = data_up_to_entry['Close'].ewm(span=12).mean()
            ema_26 = data_up_to_entry['Close'].ewm(span=26).mean()
            macd = (ema_12 - ema_26).iloc[-1] / data_up_to_entry['Close'].iloc[-1]
            
            # Bollinger Bands
            sma_20 = data_up_to_entry['Close'].rolling(20).mean()
            bb_std = data_up_to_entry['Close'].rolling(20).std()
            bb_upper = sma_20 + (2 * bb_std)
            bb_lower = sma_20 - (2 * bb_std)
            
            current_price = data_up_to_entry['Close'].iloc[-1]
            bb_position = ((current_price - bb_lower.iloc[-1]) / 
                          (bb_upper.iloc[-1] - bb_lower.iloc[-1])) if bb_upper.iloc[-1] != bb_lower.iloc[-1] else 0.5
            
            # Moving averages
            sma_50 = data_up_to_entry['Close'].rolling(50).mean()
            sma_20_ratio = current_price / sma_20.iloc[-1] if not pd.isna(sma_20.iloc[-1]) else 1.0
            sma_50_ratio = current_price / sma_50.iloc[-1] if not pd.isna(sma_50.iloc[-1]) else 1.0
            
            # Volume
            avg_volume = data_up_to_entry['Volume'].rolling(20).mean().iloc[-1]
            current_volume = data_up_to_entry['Volume'].iloc[-1]
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
            
            # Price momentum
            price_5d_ago = data_up_to_entry['Close'].iloc[-5] if len(data_up_to_entry) >= 5 else current_price
            price_20d_ago = data_up_to_entry['Close'].iloc[-20] if len(data_up_to_entry) >= 20 else current_price
            
            momentum_5d = (current_price / price_5d_ago - 1) if price_5d_ago > 0 else 0
            momentum_20d = (current_price / price_20d_ago - 1) if price_20d_ago > 0 else 0
            
            return {
                'rsi': current_rsi,
                'macd': macd,
                'bb_position': bb_position,
                'sma_20_ratio': sma_20_ratio,
                'sma_50_ratio': sma_50_ratio,
                'volume_ratio': volume_ratio,
                'price_momentum_5d': momentum_5d,
                'price_momentum_20d': momentum_20d
            }
            
        except Exception as e:
            logger.error(f"Error calculating technical features for {symbol}: {str(e)}")
            return self._default_technical_features()
    
    def _default_technical_features(self) -> Dict:
        """Default technical features when calculation fails"""
        return {
            'rsi': 50,
            'macd': 0,
            'bb_position': 0.5,
            'sma_20_ratio': 1.0,
            'sma_50_ratio': 1.0,
            'volume_ratio': 1.0,
            'price_momentum_5d': 0,
            'price_momentum_20d': 0
        }
    
    def engineer_features(self, outcomes_df: pd.DataFrame) -> pd.DataFrame:
        """Main feature engineering pipeline"""
        logger.info("Starting feature engineering pipeline...")
        
        # Step 1: Base features
        df = self.create_base_features(outcomes_df)
        
        # Step 2: Market features
        df = self.add_market_features(df)
        
        # Step 3: Strategy features
        df = self.add_strategy_features(df)
        
        # Step 4: Technical features
        df = self.add_technical_features(df)
        
        # Step 5: Interaction features
        df = self.add_interaction_features(df)
        
        # Step 6: Target variables
        df = self.create_target_variables(df)
        
        # Clean up
        df = df.dropna(subset=['target_success'])  # Remove rows without target
        
        logger.info(f"Feature engineering complete: {df.shape}")
        
        return df
    
    def save_features(self, features_df: pd.DataFrame, filename: str = None):
        """Save engineered features"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'ml/features/engineered_features_{timestamp}.pkl'
        
        features_df.to_pickle(filename)
        logger.info(f"Features saved to {filename}")
        
        # Save feature list
        feature_list = {
            'total_features': len(features_df.columns),
            'feature_names': list(features_df.columns),
            'target_variables': [col for col in features_df.columns if col.startswith('target_')],
            'categorical_features': [col for col in features_df.columns if col.endswith('_encoded')],
            'interaction_features': [col for col in features_df.columns if '_x_' in col]
        }
        
        feature_list_file = filename.replace('.pkl', '_feature_list.json')
        import json
        with open(feature_list_file, 'w') as f:
            json.dump(feature_list, f, indent=2)
        
        logger.info(f"Feature list saved to {feature_list_file}")

def main():
    """Run feature engineering on outcomes data"""
    print("🔧 Starting Feature Engineering for ML Training")
    print("=" * 60)
    
    # Find the latest outcomes file
    outcomes_files = [f for f in os.listdir('ml/data/') if f.startswith('signal_outcomes_') and f.endswith('.pkl')]
    
    if not outcomes_files:
        print("❌ No outcomes files found in ml/data/")
        print("Run outcome_tracker.py first to generate outcomes")
        return
    
    # Use the latest outcomes file
    latest_file = sorted(outcomes_files)[-1]
    outcomes_file = f'ml/data/{latest_file}'
    
    try:
        outcomes_df = pd.read_pickle(outcomes_file)
        print(f"📊 Loaded {len(outcomes_df)} signal outcomes from {latest_file}")
        
        # Initialize feature engineer
        engineer = FeatureEngineer()
        
        # Engineer features
        features_df = engineer.engineer_features(outcomes_df)
        
        if len(features_df) > 0:
            print(f"\n✅ Feature Engineering Complete!")
            print(f"📊 Results:")
            print(f"   Total samples: {len(features_df)}")
            print(f"   Total features: {len(features_df.columns)}")
            print(f"   Target variables: {len([col for col in features_df.columns if col.startswith('target_')])}")
            
            # Show feature categories
            feature_categories = {
                'Base': len([col for col in features_df.columns if not any(x in col for x in ['_x_', 'target_', 'market_', 'strategy_'])]),
                'Market': len([col for col in features_df.columns if 'market_' in col]),
                'Strategy': len([col for col in features_df.columns if 'strategy_' in col or col.endswith('_mean') or col.endswith('_count')]),
                'Technical': len([col for col in features_df.columns if any(x in col for x in ['rsi', 'macd', 'bb_', 'sma_', 'volume_', 'momentum_'])]),
                'Interaction': len([col for col in features_df.columns if '_x_' in col]),
                'Target': len([col for col in features_df.columns if col.startswith('target_')])
            }
            
            print(f"\n📈 Feature Categories:")
            for category, count in feature_categories.items():
                print(f"   {category}: {count} features")
            
            # Save features
            engineer.save_features(features_df)
            
            print(f"\n💾 Features saved to ml/features/")
            print(f"🔄 Next step: Run model training")
            
        else:
            print("❌ No features generated")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()
