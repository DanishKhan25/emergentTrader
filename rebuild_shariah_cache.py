#!/usr/bin/env python3
"""
Script to completely rebuild the Shariah compliance cache from the JSON results
This will remove all old cache files and create fresh ones
"""

import json
import pickle
import os
import shutil
from datetime import datetime, timedelta
import sys

def rebuild_shariah_cache():
    """Completely rebuild the Shariah compliance cache"""
    
    # Load the JSON results
    json_file = 'nse_shariah_compliance_results.json'
    if not os.path.exists(json_file):
        print(f"❌ Error: {json_file} not found!")
        return False
    
    print(f"📖 Loading Shariah compliance data from {json_file}...")
    
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    compliant_stocks = data.get('compliant_stocks', [])
    print(f"📊 Found {len(compliant_stocks)} compliant stocks in JSON file")
    
    # Remove all existing Shariah compliance cache files
    cache_dir = 'python_backend/data/cache'
    if os.path.exists(cache_dir):
        print("🧹 Removing all existing Shariah compliance cache files...")
        
        removed_count = 0
        for filename in os.listdir(cache_dir):
            if filename.startswith('shariah_compliance_') and filename.endswith('.pkl'):
                try:
                    os.remove(os.path.join(cache_dir, filename))
                    removed_count += 1
                except Exception as e:
                    print(f"⚠️  Error removing {filename}: {e}")
        
        print(f"✅ Removed {removed_count} old cache files")
    else:
        os.makedirs(cache_dir, exist_ok=True)
        print("📁 Created cache directory")
    
    # Create fresh cache entries for compliant stocks only
    print("📝 Creating fresh cache entries...")
    
    created_count = 0
    for stock in compliant_stocks:
        symbol = stock.get('symbol')
        if not symbol:
            continue
            
        # Create cache entry
        cache_entry = {
            'symbol': symbol,
            'shariah_compliant': True,
            'compliance_status': 'compliant',
            'confidence_level': stock.get('confidence_level', 'high'),
            'business_activity_compliant': stock.get('compliance_details', {}).get('business_activity_compliant', True),
            'business_confidence': stock.get('compliance_details', {}).get('business_confidence', 'high'),
            'business_reason': stock.get('compliance_details', {}).get('business_reason', 'Business activity compliant'),
            'financial_ratios_compliant': stock.get('compliance_details', {}).get('financial_ratios_compliant', True),
            'financial_confidence': stock.get('compliance_details', {}).get('financial_confidence', 'high'),
            'compliance_score': stock.get('compliance_score', 1.0),
            'check_date': stock.get('compliance_details', {}).get('check_date', datetime.now().isoformat()),
            'cache_expires': (datetime.now() + timedelta(days=90)).isoformat(),
            'details': {
                'sector': stock.get('sector', 'Unknown'),
                'market_cap': stock.get('market_cap', 0),
                'company_name': stock.get('company_name', symbol)
            }
        }
        
        # Save to cache file
        cache_file = os.path.join(cache_dir, f'shariah_compliance_{symbol}.pkl')
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(cache_entry, f)
            created_count += 1
        except Exception as e:
            print(f"⚠️  Error creating cache for {symbol}: {e}")
    
    print(f"✅ Created {created_count} fresh Shariah compliance cache files")
    
    # Verify the cache
    print("\n🔍 Verifying rebuilt cache...")
    compliant_in_cache = 0
    total_cache_files = 0
    
    for cache_file in os.listdir(cache_dir):
        if cache_file.startswith('shariah_compliance_') and cache_file.endswith('.pkl'):
            total_cache_files += 1
            try:
                with open(os.path.join(cache_dir, cache_file), 'rb') as f:
                    cache_data = pickle.load(f)
                    if cache_data.get('shariah_compliant') == True:
                        compliant_in_cache += 1
            except:
                pass
    
    print(f"📊 Cache verification:")
    print(f"   • Total cache files: {total_cache_files}")
    print(f"   • Compliant stocks in cache: {compliant_in_cache}")
    print(f"   • Expected compliant stocks: {len(compliant_stocks)}")
    
    if compliant_in_cache == len(compliant_stocks) and total_cache_files == len(compliant_stocks):
        print("✅ Cache rebuild successful! Perfect match.")
        return True
    else:
        print("⚠️  Cache count doesn't match expected values.")
        return False

def clear_app_cache():
    """Clear any application-level cache that might interfere"""
    print("🧹 Clearing application-level cache...")
    
    cache_dir = 'python_backend/data/cache'
    
    # Remove NSE universe cache
    nse_cache_file = os.path.join(cache_dir, 'nse_universe_stocks_list.pkl')
    if os.path.exists(nse_cache_file):
        try:
            os.remove(nse_cache_file)
            print("✅ Removed NSE universe cache")
        except Exception as e:
            print(f"⚠️  Error removing NSE cache: {e}")
    
    # Clear any other relevant cache files
    cache_patterns = ['stock_info_', 'market_data_', 'price_data_']
    removed_count = 0
    
    if os.path.exists(cache_dir):
        for filename in os.listdir(cache_dir):
            for pattern in cache_patterns:
                if filename.startswith(pattern) and filename.endswith('.pkl'):
                    try:
                        os.remove(os.path.join(cache_dir, filename))
                        removed_count += 1
                        break
                    except Exception as e:
                        print(f"⚠️  Error removing {filename}: {e}")
    
    if removed_count > 0:
        print(f"✅ Removed {removed_count} additional cache files")

if __name__ == "__main__":
    print("🚀 Starting complete Shariah compliance cache rebuild...")
    print("=" * 70)
    
    # Clear application cache first
    clear_app_cache()
    
    # Rebuild cache from JSON
    success = rebuild_shariah_cache()
    
    print("\n" + "=" * 70)
    if success:
        print("✅ CACHE REBUILD COMPLETED SUCCESSFULLY!")
        print("📱 The app should now show exactly 1295 Shariah compliant stocks.")
        print("🔄 Please restart the app to see the changes.")
        print("\n💡 To verify:")
        print("   1. Restart your app")
        print("   2. Check the /api/stocks/shariah endpoint")
        print("   3. The frontend should now display 1295 stocks")
    else:
        print("❌ Cache rebuild had issues!")
        print("🔧 You may need to check the JSON file format or permissions.")
        sys.exit(1)
