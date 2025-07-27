#!/usr/bin/env python3
"""
AI Price Prediction System Demo
Showcases the complete functionality of the AI prediction system
"""

import requests
import json
import time
from datetime import datetime

def demo_ai_predictions():
    """Demonstrate the AI prediction system capabilities"""
    
    print("🤖 AI PRICE PREDICTION SYSTEM DEMO")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Test symbols
    symbols = ['RELIANCE', 'TCS', 'INFY']
    
    print(f"\n🔍 Testing {len(symbols)} symbols: {', '.join(symbols)}")
    
    for symbol in symbols:
        print(f"\n📊 PROCESSING {symbol}")
        print("-" * 30)
        
        # Step 1: Train model
        print(f"🔧 Training AI model for {symbol}...")
        train_response = requests.post(f"{base_url}/ai/train", 
            json={"symbol": symbol, "retrain": True})
        
        if train_response.status_code == 200:
            train_data = train_response.json()
            if train_data['success']:
                print(f"✅ Training started: {train_data['data']['message']}")
                print(f"⏱️  Estimated time: {train_data['data']['estimated_time']}")
            else:
                print(f"❌ Training failed: {train_data.get('error', 'Unknown error')}")
                continue
        else:
            print(f"❌ Training request failed: {train_response.status_code}")
            continue
        
        # Wait for training to complete
        print("⏳ Waiting for training to complete...")
        time.sleep(45)  # Wait 45 seconds for training
        
        # Step 2: Generate predictions
        print(f"🔮 Generating AI predictions for {symbol}...")
        
        for days in [1, 7, 30]:
            try:
                pred_response = requests.post(f"{base_url}/ai/predict",
                    json={"symbol": symbol, "days_ahead": days})
                
                if pred_response.status_code == 200:
                    pred_data = pred_response.json()
                    
                    if pred_data['success']:
                        data = pred_data['data']
                        
                        # Extract prediction for the specific horizon
                        if days == 1:
                            prediction = data['predictions']['1_day']
                        elif days == 7:
                            prediction = data['predictions']['7_day']
                        else:
                            prediction = data['predictions']['30_day']
                        
                        print(f"  📅 {days}D Prediction:")
                        print(f"    Current: ₹{data['current_price']}")
                        print(f"    Predicted: ₹{prediction['price']} ({prediction['change_percent']:+.2f}%)")
                        print(f"    Confidence: {prediction['confidence']}%")
                        print(f"    Trend: {data['analysis']['trend_direction']}")
                        print(f"    Risk Score: {data['analysis']['risk_score']}%")
                        
                    else:
                        print(f"    ❌ {days}D prediction failed: {pred_data.get('error', 'Unknown error')}")
                else:
                    print(f"    ❌ {days}D prediction request failed: {pred_response.status_code}")
                    
            except Exception as e:
                print(f"    ❌ {days}D prediction error: {str(e)}")
        
        # Step 3: Get model performance
        print(f"📊 Model performance for {symbol}:")
        try:
            perf_response = requests.get(f"{base_url}/ai/model/performance/{symbol}")
            
            if perf_response.status_code == 200:
                perf_data = perf_response.json()
                
                if perf_data['success']:
                    performance = perf_data['data']
                    print(f"  Trained: {performance.get('trained_at', 'Unknown')}")
                    
                    # Show best performing models
                    for horizon, models in performance.get('horizons', {}).items():
                        best_model = max(models.items(), key=lambda x: x[1]['accuracy_percentage'])
                        model_name, metrics = best_model
                        print(f"  {horizon.upper()}: {model_name} - {metrics['accuracy_percentage']}% accuracy")
                        
                else:
                    print(f"  ❌ Performance data failed: {perf_data.get('error', 'Unknown error')}")
            else:
                print(f"  ❌ Performance request failed: {perf_response.status_code}")
                
        except Exception as e:
            print(f"  ❌ Performance error: {str(e)}")
    
    # Step 4: List all trained models
    print(f"\n📋 TRAINED MODELS SUMMARY")
    print("-" * 30)
    
    try:
        models_response = requests.get(f"{base_url}/ai/models/list")
        
        if models_response.status_code == 200:
            models_data = models_response.json()
            
            if models_data['success']:
                models = models_data['data']['models']
                print(f"Total trained models: {len(models)}")
                
                for model in models:
                    print(f"  {model['symbol']}: {len(model['model_types'])} algorithms, {model['features_count']} features")
                    
            else:
                print(f"❌ Models list failed: {models_data.get('error', 'Unknown error')}")
        else:
            print(f"❌ Models list request failed: {models_response.status_code}")
            
    except Exception as e:
        print(f"❌ Models list error: {str(e)}")
    
    # Step 5: Health check
    print(f"\n🏥 SYSTEM HEALTH CHECK")
    print("-" * 30)
    
    try:
        health_response = requests.get(f"{base_url}/ai/health")
        
        if health_response.status_code == 200:
            health_data = health_response.json()
            
            if health_data['success']:
                health = health_data['data']
                print(f"Status: {health['status']}")
                print(f"Service: {health['service']}")
                print(f"Models Directory: {health['models_directory']}")
                print(f"Timestamp: {health['timestamp']}")
            else:
                print(f"❌ Health check failed: {health_data.get('error', 'Unknown error')}")
        else:
            print(f"❌ Health check request failed: {health_response.status_code}")
            
    except Exception as e:
        print(f"❌ Health check error: {str(e)}")
    
    print(f"\n🎉 AI PREDICTION SYSTEM DEMO COMPLETE")
    print("\n🚀 FEATURES DEMONSTRATED:")
    print("✅ Model training with background processing")
    print("✅ Multi-horizon predictions (1D, 7D, 30D)")
    print("✅ Confidence scoring and trend analysis")
    print("✅ Risk assessment and volatility forecasting")
    print("✅ Model performance metrics")
    print("✅ System health monitoring")
    print("✅ Comprehensive error handling")
    
    print(f"\n🎯 NEXT STEPS:")
    print("1. Open http://localhost:3000 in your browser")
    print("2. Navigate to the 'AI Predictions' tab")
    print("3. Enter a stock symbol (e.g., RELIANCE)")
    print("4. Generate predictions and explore the interface")
    print("5. View support/resistance levels and analysis")

if __name__ == "__main__":
    demo_ai_predictions()
