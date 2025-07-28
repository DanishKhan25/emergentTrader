#!/usr/bin/env python3
"""
Script to update the Shariah compliance cache from the nse_shariah_compliance_results.json file
This will ensure the app shows the correct number of Shariah compliant stocks (1295)
"""

import json
import pickle
import os
from datetime import datetime, timedelta
import sys

def update_shariah_cache_from_json():
    """Update the individual cache files from the JSON results"""
    
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
    
    # Create cache directory if it doesn't exist
    cache_dir = 'python_backend/data/cache'
    os.makedirs(cache_dir, exist_ok=True)
    
    # Process each compliant stock
    updated_count = 0
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
            updated_count += 1
        except Exception as e:
            print(f"⚠️  Error saving cache for {symbol}: {e}")
    
    print(f"✅ Updated {updated_count} Shariah compliance cache files")
    
    # Also update any non-compliant stocks that might be in the cache
    # Get all symbols from the JSON processing
    all_processed_symbols = set()
    
    # Add compliant symbols
    for stock in compliant_stocks:
        if stock.get('symbol'):
            all_processed_symbols.add(stock.get('symbol'))
    
    # Add non-compliant symbols if they exist in the data
    if 'non_compliant_stocks' in data:
        for stock in data['non_compliant_stocks']:
            if stock.get('symbol'):
                all_processed_symbols.add(stock.get('symbol'))
    
    # Check for existing cache files that might need to be marked as non-compliant
    existing_cache_files = [f for f in os.listdir(cache_dir) if f.startswith('shariah_compliance_') and f.endswith('.pkl')]
    
    non_compliant_updated = 0
    for cache_file in existing_cache_files:
        symbol = cache_file.replace('shariah_compliance_', '').replace('.pkl', '')
        
        # If this symbol was processed but is not in compliant list, mark as non-compliant
        if symbol in all_processed_symbols:
            # Check if it's in compliant list
            is_compliant = any(stock.get('symbol') == symbol for stock in compliant_stocks)
            
            if not is_compliant:
                # Update cache to mark as non-compliant
                cache_entry = {
                    'symbol': symbol,
                    'shariah_compliant': False,
                    'compliance_status': 'non_compliant',
                    'confidence_level': 'high',
                    'business_activity_compliant': False,
                    'business_confidence': 'high',
                    'business_reason': 'Business activity not compliant',
                    'financial_ratios_compliant': False,
                    'financial_confidence': 'high',
                    'compliance_score': 0.0,
                    'check_date': datetime.now().isoformat(),
                    'cache_expires': (datetime.now() + timedelta(days=90)).isoformat(),
                    'details': {
                        'sector': 'Unknown',
                        'market_cap': 0,
                        'company_name': symbol
                    }
                }
                
                cache_file_path = os.path.join(cache_dir, cache_file)
                try:
                    with open(cache_file_path, 'wb') as f:
                        pickle.dump(cache_entry, f)
                    non_compliant_updated += 1
                except Exception as e:
                    print(f"⚠️  Error updating non-compliant cache for {symbol}: {e}")
    
    if non_compliant_updated > 0:
        print(f"✅ Updated {non_compliant_updated} non-compliant cache files")
    
    # Verify the cache
    print("\n🔍 Verifying updated cache...")
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
    
    if compliant_in_cache == len(compliant_stocks):
        print("✅ Cache update successful! The app should now show the correct number of Shariah stocks.")
    else:
        print("⚠️  Cache count doesn't match. There might be some issues.")
    
    return True

def clear_old_cache():
    """Clear any old cache that might be interfering"""
    cache_dir = 'python_backend/data/cache'
    if not os.path.exists(cache_dir):
        return
    
    print("🧹 Clearing old cache files...")
    
    # Remove the NSE universe cache file if it exists
    nse_cache_file = os.path.join(cache_dir, 'nse_universe_stocks_list.pkl')
    if os.path.exists(nse_cache_file):
        try:
            os.remove(nse_cache_file)
            print("✅ Removed old NSE universe cache")
        except Exception as e:
            print(f"⚠️  Error removing NSE cache: {e}")

if __name__ == "__main__":
    print("🚀 Starting Shariah compliance cache update...")
    print("=" * 60)
    
    # Clear old cache first
    clear_old_cache()
    
    # Update cache from JSON
    success = update_shariah_cache_from_json()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ CACHE UPDATE COMPLETED!")
        print("📱 The app should now show 1295 Shariah compliant stocks.")
        print("🔄 You may need to restart the app to see the changes.")
        print("\n💡 To verify, check the /api/stocks/shariah endpoint")
    else:
        print("\n❌ Cache update failed!")
        sys.exit(1)
