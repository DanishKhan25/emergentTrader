#!/usr/bin/env python3
"""
AI Endpoint Log Monitor
Real-time monitoring for AI training and prediction endpoints
"""

import subprocess
import time
import sys
import os
from datetime import datetime
import threading
import queue

def monitor_logs():
    """Monitor AI endpoint logs in real-time"""
    
    print("🔍 AI ENDPOINT LOG MONITOR")
    print("=" * 50)
    print("Monitoring logs for /ai-signals/train/batch and related endpoints...")
    print("Press Ctrl+C to stop monitoring")
    print()
    
    # Log files to monitor
    log_files = [
        "python_backend/backend.log",
        "python_backend/logs/api.log", 
        "python_backend/logs/signals.log",
        "python_backend/logs/emergent_trader.log",
        "python_backend/logs/errors.log"
    ]
    
    # Filter keywords for AI endpoints
    ai_keywords = [
        "ai-signals",
        "train/batch", 
        "AI Enhanced",
        "batch_train",
        "ai_enhanced_generator",
        "ai_predictor",
        "model training",
        "Background training",
        "Batch training"
    ]
    
    print("📋 Monitoring log files:")
    for log_file in log_files:
        if os.path.exists(log_file):
            print(f"  ✅ {log_file}")
        else:
            print(f"  ❌ {log_file} (not found)")
    
    print(f"\n🔍 Filtering for keywords: {', '.join(ai_keywords)}")
    print("\n" + "="*50)
    print("LIVE LOG OUTPUT:")
    print("="*50)
    
    # Start monitoring each log file
    processes = []
    
    for log_file in log_files:
        if os.path.exists(log_file):
            try:
                # Use tail -f to follow log files
                process = subprocess.Popen(
                    ['tail', '-f', log_file],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True,
                    bufsize=1
                )
                processes.append((process, log_file))
            except Exception as e:
                print(f"❌ Error monitoring {log_file}: {e}")
    
    try:
        while True:
            for process, log_file in processes:
                try:
                    # Check if there's new output
                    line = process.stdout.readline()
                    if line:
                        line = line.strip()
                        # Filter for AI-related logs
                        if any(keyword.lower() in line.lower() for keyword in ai_keywords):
                            timestamp = datetime.now().strftime("%H:%M:%S")
                            log_name = os.path.basename(log_file)
                            print(f"[{timestamp}] [{log_name}] {line}")
                except:
                    continue
            
            time.sleep(0.1)  # Small delay to prevent high CPU usage
            
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping log monitoring...")
        for process, _ in processes:
            process.terminate()
        print("✅ Log monitoring stopped")

def test_ai_endpoint_with_logging():
    """Test the AI endpoint and monitor logs simultaneously"""
    
    print("🧪 TESTING AI ENDPOINT WITH LOG MONITORING")
    print("=" * 50)
    
    # Start log monitoring in background thread
    import threading
    log_thread = threading.Thread(target=monitor_logs, daemon=True)
    log_thread.start()
    
    time.sleep(2)  # Give log monitoring time to start
    
    print("\n🚀 Starting AI batch training test...")
    
    # Test the endpoint
    import requests
    import json
    
    try:
        test_request = {
            "symbols": ["RELIANCE", "TCS"],
            "shariah_only": True,
            "max_concurrent": 2
        }
        
        print(f"📤 Sending request to /ai-signals/train/batch")
        print(f"   Request: {json.dumps(test_request, indent=2)}")
        
        response = requests.post(
            "http://localhost:8000/ai-signals/train/batch",
            json=test_request,
            timeout=30
        )
        
        print(f"\n📥 Response received:")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Success: {data.get('success')}")
            if data.get('success'):
                print(f"   Message: {data['data'].get('message')}")
                print(f"   Symbols: {data['data'].get('symbols_count', 'N/A')}")
                print(f"   Estimated time: {data['data'].get('estimated_time', 'N/A')}")
        else:
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing endpoint: {e}")
    
    print(f"\n⏳ Monitoring logs for 60 seconds...")
    print(f"   Watch for training progress and completion messages")
    
    # Keep monitoring for 60 seconds
    time.sleep(60)
    
    print(f"\n✅ Test complete. Check logs above for training progress.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_ai_endpoint_with_logging()
    else:
        monitor_logs()
