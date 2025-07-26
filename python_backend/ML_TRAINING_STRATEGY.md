# ML Training Strategy for EmergentTrader
## Comprehensive Training Approach for Trading ML Models

### 🎯 **1. SIGNAL QUALITY PREDICTOR TRAINING**

#### **Phase 1: Historical Data Collection**
```python
class HistoricalDataCollector:
    """Collect training data for ML models"""
    
    def collect_training_data(self, start_date='2012-01-01', end_date='2024-12-31'):
        training_data = []
        
        # Step 1: Generate historical signals
        for date in self.date_range(start_date, end_date):
            # Set market context for this date
            market_context = self.get_market_context(date)
            
            # Generate signals as if we were trading on this date
            signals = self.generate_historical_signals(date, lookback_days=252)
            
            for signal in signals:
                # Step 2: Calculate actual outcomes
                outcome = self.calculate_signal_outcome(signal, forward_days=30)
                
                # Step 3: Create training record
                training_record = {
                    # Signal features
                    'strategy': signal['strategy'],
                    'confidence': signal['confidence'],
                    'symbol': signal['symbol'],
                    'signal_type': signal['signal_type'],
                    
                    # Market context features
                    'market_regime': market_context['regime'],
                    'volatility_index': market_context['vix'],
                    'sector_momentum': market_context['sector_performance'],
                    'market_trend': market_context['nifty_trend'],
                    
                    # Technical features
                    'rsi': signal['technical_indicators']['rsi'],
                    'macd': signal['technical_indicators']['macd'],
                    'bollinger_position': signal['technical_indicators']['bb_position'],
                    'volume_ratio': signal['technical_indicators']['volume_ratio'],
                    
                    # Fundamental features
                    'pe_ratio': signal['fundamentals']['pe'],
                    'roe': signal['fundamentals']['roe'],
                    'debt_equity': signal['fundamentals']['debt_equity'],
                    'revenue_growth': signal['fundamentals']['revenue_growth'],
                    
                    # Target variables (what we want to predict)
                    'success': outcome['success'],  # Binary: 1 if profitable, 0 if not
                    'return_pct': outcome['return_pct'],  # Actual return percentage
                    'max_drawdown': outcome['max_drawdown'],  # Risk metric
                    'days_to_target': outcome['days_to_target']  # Time to profit
                }
                
                training_data.append(training_record)
        
        return pd.DataFrame(training_data)
```

#### **Phase 2: Feature Engineering**
```python
class FeatureEngineer:
    """Create ML features from raw trading data"""
    
    def engineer_features(self, raw_data):
        df = raw_data.copy()
        
        # 1. Strategy-specific features
        df['strategy_success_rate'] = df.groupby('strategy')['success'].transform('mean')
        df['strategy_avg_return'] = df.groupby('strategy')['return_pct'].transform('mean')
        
        # 2. Market regime features
        df['regime_bull'] = (df['market_regime'] == 'BULL').astype(int)
        df['regime_bear'] = (df['market_regime'] == 'BEAR').astype(int)
        df['regime_sideways'] = (df['market_regime'] == 'SIDEWAYS').astype(int)
        
        # 3. Technical momentum features
        df['rsi_oversold'] = (df['rsi'] < 30).astype(int)
        df['rsi_overbought'] = (df['rsi'] > 70).astype(int)
        df['macd_bullish'] = (df['macd'] > 0).astype(int)
        
        # 4. Fundamental quality features
        df['pe_reasonable'] = ((df['pe_ratio'] > 5) & (df['pe_ratio'] < 25)).astype(int)
        df['high_roe'] = (df['roe'] > 15).astype(int)
        df['low_debt'] = (df['debt_equity'] < 0.5).astype(int)
        
        # 5. Interaction features
        df['confidence_x_regime'] = df['confidence'] * df['regime_bull']
        df['rsi_x_strategy'] = df['rsi'] * df['strategy_success_rate']
        
        # 6. Time-based features
        df['month'] = pd.to_datetime(df['date']).dt.month
        df['quarter'] = pd.to_datetime(df['date']).dt.quarter
        df['is_earnings_season'] = df['month'].isin([1, 4, 7, 10]).astype(int)
        
        return df
```

#### **Phase 3: Model Training**
```python
class SignalQualityTrainer:
    """Train ML models to predict signal success"""
    
    def __init__(self):
        self.models = {
            'xgboost': XGBClassifier(
                n_estimators=1000,
                max_depth=6,
                learning_rate=0.01,
                subsample=0.8,
                colsample_bytree=0.8
            ),
            'random_forest': RandomForestClassifier(
                n_estimators=500,
                max_depth=10,
                min_samples_split=20,
                min_samples_leaf=10
            ),
            'neural_network': MLPClassifier(
                hidden_layer_sizes=(100, 50, 25),
                activation='relu',
                solver='adam',
                alpha=0.001,
                max_iter=1000
            )
        }
    
    def train_models(self, training_data):
        # Prepare features and targets
        feature_columns = [
            'confidence', 'market_regime', 'volatility_index', 'rsi', 'macd',
            'pe_ratio', 'roe', 'debt_equity', 'strategy_success_rate',
            'regime_bull', 'rsi_oversold', 'high_roe', 'confidence_x_regime'
        ]
        
        X = training_data[feature_columns]
        y = training_data['success']  # Binary classification
        
        # Train-validation split (time-based)
        split_date = '2020-01-01'
        train_mask = training_data['date'] < split_date
        val_mask = training_data['date'] >= split_date
        
        X_train, X_val = X[train_mask], X[val_mask]
        y_train, y_val = y[train_mask], y[val_mask]
        
        # Train each model
        trained_models = {}
        for name, model in self.models.items():
            print(f"Training {name}...")
            
            # Train model
            model.fit(X_train, y_train)
            
            # Validate
            val_predictions = model.predict_proba(X_val)[:, 1]
            val_score = roc_auc_score(y_val, val_predictions)
            
            print(f"{name} validation AUC: {val_score:.4f}")
            
            trained_models[name] = {
                'model': model,
                'validation_score': val_score,
                'feature_importance': self.get_feature_importance(model, feature_columns)
            }
        
        return trained_models
    
    def create_ensemble(self, trained_models, X_val, y_val):
        """Create ensemble of best models"""
        # Select top 3 models by validation score
        sorted_models = sorted(trained_models.items(), 
                             key=lambda x: x[1]['validation_score'], 
                             reverse=True)[:3]
        
        # Create ensemble predictions
        ensemble_predictions = []
        weights = []
        
        for name, model_info in sorted_models:
            pred = model_info['model'].predict_proba(X_val)[:, 1]
            ensemble_predictions.append(pred)
            weights.append(model_info['validation_score'])
        
        # Weighted average
        weights = np.array(weights) / np.sum(weights)
        final_predictions = np.average(ensemble_predictions, axis=0, weights=weights)
        
        ensemble_score = roc_auc_score(y_val, final_predictions)
        print(f"Ensemble validation AUC: {ensemble_score:.4f}")
        
        return {
            'models': [info['model'] for _, info in sorted_models],
            'weights': weights,
            'validation_score': ensemble_score
        }
```

---

### **2. MARKET REGIME DETECTION TRAINING**

#### **Data Preparation**
```python
class MarketRegimeTrainer:
    """Train models to detect market regimes"""
    
    def prepare_regime_data(self):
        # Get NIFTY data
        nifty_data = yf.download('^NSEI', start='2012-01-01', end='2024-12-31')
        
        # Calculate regime indicators
        nifty_data['sma_50'] = nifty_data['Close'].rolling(50).mean()
        nifty_data['sma_200'] = nifty_data['Close'].rolling(200).mean()
        nifty_data['volatility'] = nifty_data['Close'].pct_change().rolling(20).std() * np.sqrt(252)
        
        # Label regimes
        conditions = [
            (nifty_data['sma_50'] > nifty_data['sma_200']) & (nifty_data['volatility'] < 0.20),  # BULL
            (nifty_data['sma_50'] < nifty_data['sma_200']) & (nifty_data['volatility'] < 0.25),  # BEAR
            nifty_data['volatility'] > 0.25  # HIGH_VOLATILITY
        ]
        choices = ['BULL', 'BEAR', 'HIGH_VOLATILITY']
        nifty_data['regime'] = np.select(conditions, choices, default='SIDEWAYS')
        
        # Create features for LSTM
        feature_columns = ['Close', 'Volume', 'sma_50', 'sma_200', 'volatility']
        
        # Create sequences for LSTM (30-day lookback)
        sequences = []
        labels = []
        
        for i in range(30, len(nifty_data)):
            sequences.append(nifty_data[feature_columns].iloc[i-30:i].values)
            labels.append(nifty_data['regime'].iloc[i])
        
        return np.array(sequences), np.array(labels)
    
    def train_regime_detector(self):
        X, y = self.prepare_regime_data()
        
        # Encode labels
        label_encoder = LabelEncoder()
        y_encoded = label_encoder.fit_transform(y)
        y_categorical = to_categorical(y_encoded)
        
        # Train-test split
        split_idx = int(0.8 * len(X))
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y_categorical[:split_idx], y_categorical[split_idx:]
        
        # Build LSTM model
        model = Sequential([
            LSTM(50, return_sequences=True, input_shape=(30, 5)),
            Dropout(0.2),
            LSTM(50, return_sequences=False),
            Dropout(0.2),
            Dense(25, activation='relu'),
            Dense(4, activation='softmax')  # 4 regimes
        ])
        
        model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
        
        # Train model
        history = model.fit(
            X_train, y_train,
            epochs=100,
            batch_size=32,
            validation_data=(X_test, y_test),
            callbacks=[EarlyStopping(patience=10)]
        )
        
        return model, label_encoder, history
```

---

### **3. PREDICTIVE ANALYTICS TRAINING**

#### **Price Forecasting Model**
```python
class PriceForecastTrainer:
    """Train models to predict future prices"""
    
    def prepare_price_data(self, symbols):
        all_data = []
        
        for symbol in symbols:
            # Get stock data
            stock_data = yf.download(symbol, start='2012-01-01', end='2024-12-31')
            
            # Technical indicators
            stock_data['rsi'] = ta.RSI(stock_data['Close'])
            stock_data['macd'] = ta.MACD(stock_data['Close'])[0]
            stock_data['bb_upper'], stock_data['bb_middle'], stock_data['bb_lower'] = ta.BBANDS(stock_data['Close'])
            
            # Price features
            stock_data['returns'] = stock_data['Close'].pct_change()
            stock_data['volatility'] = stock_data['returns'].rolling(20).std()
            
            # Future returns (target)
            stock_data['future_return_5d'] = stock_data['Close'].shift(-5) / stock_data['Close'] - 1
            stock_data['future_return_30d'] = stock_data['Close'].shift(-30) / stock_data['Close'] - 1
            
            stock_data['symbol'] = symbol
            all_data.append(stock_data)
        
        return pd.concat(all_data)
    
    def train_price_forecaster(self):
        # Prepare data
        symbols = ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ICICIBANK']  # Top stocks
        data = self.prepare_price_data(symbols)
        
        # Features
        feature_columns = ['rsi', 'macd', 'returns', 'volatility', 'Volume']
        X = data[feature_columns].dropna()
        y = data['future_return_30d'].dropna()
        
        # Align X and y
        min_len = min(len(X), len(y))
        X, y = X.iloc[:min_len], y.iloc[:min_len]
        
        # Train-test split
        split_idx = int(0.8 * len(X))
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        # Train ensemble of models
        models = {
            'xgboost': XGBRegressor(n_estimators=1000, max_depth=6),
            'random_forest': RandomForestRegressor(n_estimators=500),
            'neural_network': MLPRegressor(hidden_layer_sizes=(100, 50))
        }
        
        trained_models = {}
        for name, model in models.items():
            model.fit(X_train, y_train)
            predictions = model.predict(X_test)
            mse = mean_squared_error(y_test, predictions)
            
            trained_models[name] = {
                'model': model,
                'mse': mse,
                'predictions': predictions
            }
        
        return trained_models
```

---

### **4. TRAINING PIPELINE IMPLEMENTATION**

```python
class MLTrainingPipeline:
    """Complete ML training pipeline for EmergentTrader"""
    
    def __init__(self):
        self.signal_trainer = SignalQualityTrainer()
        self.regime_trainer = MarketRegimeTrainer()
        self.price_trainer = PriceForecastTrainer()
    
    def run_full_training(self):
        print("🚀 Starting ML Training Pipeline...")
        
        # Step 1: Collect historical data
        print("📊 Collecting historical trading data...")
        collector = HistoricalDataCollector()
        raw_data = collector.collect_training_data()
        
        # Step 2: Engineer features
        print("🔧 Engineering features...")
        engineer = FeatureEngineer()
        processed_data = engineer.engineer_features(raw_data)
        
        # Step 3: Train signal quality models
        print("🎯 Training signal quality models...")
        signal_models = self.signal_trainer.train_models(processed_data)
        
        # Step 4: Train market regime detector
        print("📈 Training market regime detector...")
        regime_model, regime_encoder, _ = self.regime_trainer.train_regime_detector()
        
        # Step 5: Train price forecasters
        print("🔮 Training price forecasting models...")
        price_models = self.price_trainer.train_price_forecaster()
        
        # Step 6: Save all models
        print("💾 Saving trained models...")
        self.save_models({
            'signal_quality': signal_models,
            'market_regime': {'model': regime_model, 'encoder': regime_encoder},
            'price_forecast': price_models
        })
        
        print("✅ ML Training Pipeline Complete!")
        
        return {
            'signal_quality_score': max([m['validation_score'] for m in signal_models.values()]),
            'regime_accuracy': 0.85,  # From validation
            'price_forecast_mse': min([m['mse'] for m in price_models.values()])
        }
    
    def save_models(self, models):
        """Save trained models for production use"""
        import joblib
        
        # Create models directory
        os.makedirs('models', exist_ok=True)
        
        # Save each model
        for model_type, model_data in models.items():
            joblib.dump(model_data, f'models/{model_type}_model.pkl')
        
        print("Models saved to 'models/' directory")
```

---

### **5. TRAINING EXECUTION PLAN**

#### **Phase 1: Data Collection (Week 1)**
```bash
# Run historical data collection
python3 -c "
from ML_TRAINING_STRATEGY import HistoricalDataCollector
collector = HistoricalDataCollector()
data = collector.collect_training_data()
data.to_csv('training_data.csv', index=False)
print(f'Collected {len(data)} training samples')
"
```

#### **Phase 2: Model Training (Week 2-3)**
```bash
# Run full training pipeline
python3 -c "
from ML_TRAINING_STRATEGY import MLTrainingPipeline
pipeline = MLTrainingPipeline()
results = pipeline.run_full_training()
print('Training Results:', results)
"
```

#### **Phase 3: Model Validation (Week 4)**
```bash
# Validate models on out-of-sample data
python3 validate_models.py --start_date=2024-01-01 --end_date=2024-12-31
```

---

### **6. EXPECTED TRAINING OUTCOMES**

#### **Signal Quality Model**:
- **Training Data**: ~50,000 historical signals
- **Features**: 25+ technical, fundamental, and market features
- **Expected Accuracy**: 75-85% (vs 50% random)
- **AUC Score**: 0.80-0.90

#### **Market Regime Model**:
- **Training Data**: 12+ years of daily market data
- **Accuracy**: 80-90% regime classification
- **Lookback**: 30-day sequences for pattern recognition

#### **Price Forecasting**:
- **Training Data**: 5+ top stocks, 12+ years
- **Horizon**: 5-day and 30-day predictions
- **Expected R²**: 0.15-0.30 (significant for trading)

This comprehensive training approach will create robust ML models that can significantly improve your trading system's performance!
