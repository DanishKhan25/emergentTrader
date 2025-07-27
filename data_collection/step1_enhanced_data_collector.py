#!/usr/bin/env python3
"""
Step 1: Enhanced Data Collector for 2000+ Stocks
Downloads comprehensive historical data for maximum ML training coverage
"""

import yfinance as yf
import pandas as pd
import os
from datetime import datetime
import time
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import warnings
warnings.filterwarnings('ignore')

class EnhancedDataCollector:
    def __init__(self):
        self.training_data_dir = "training_data_2014_2019"
        self.testing_data_dir = "testing_data_2019_2025"
        self.logs_dir = "download_logs"
        
        # Create directories
        os.makedirs(self.training_data_dir, exist_ok=True)
        os.makedirs(self.testing_data_dir, exist_ok=True)
        os.makedirs(self.logs_dir, exist_ok=True)
        
        # Download statistics
        self.stats = {
            'total_stocks': 0,
            'successful_downloads': 0,
            'failed_downloads': 0,
            'insufficient_data': 0,
            'start_time': None,
            'end_time': None
        }
        
    def get_comprehensive_stock_list(self):
        """Get the comprehensive list of 2000+ Indian stocks"""
        
        stocks = ['20MICRONS', '21STCENMGM', '360ONE', '3IINFOLTD', '3MINDIA', '3PLAND', '5PAISA', '63MOONS', 'A2ZINFRA', 'AAATECH', 'AADHARHFC', 'AAKASH', 'AAREYDRUGS', 'AARON', 'AARTECH', 'AARTIDRUGS', 'AARTIIND', 'AARTIPHARM', 'AARTISURF', 'AARVEEDEN', 'AARVI', 'AAVAS', 'ABAN', 'ABB', 'ABBOTINDIA', 'ABCAPITAL', 'ABDL', 'ABFRL', 'ABINFRA', 'ABLBL', 'ABMINTLLTD', 'ABREL', 'ABSLAMC', 'ACC', 'ACCELYA', 'ACCURACY', 'ACE', 'ACEINTEG', 'ACI', 'ACL', 'ACLGATI', 'ACMESOLAR', 'ACUTAAS', 'ADANIENSOL', 'ADANIENT', 'ADANIGREEN', 'ADANIPORTS', 'ADANIPOWER', 'ADFFOODS', 'ADL', 'ADOR', 'ADROITINFO', 'ADSL', 'ADVANIHOTR', 'ADVENZYMES', 'AEGISLOG', 'AEGISVOPAK', 'AEROENTER', 'AEROFLEX', 'AETHER', 'AFCONS', 'AFFLE', 'AFFORDABLE', 'AFIL', 'AFSL', 'AGARIND', 'AGARWALEYE', 'AGI', 'AGIIL', 'AGRITECH', 'AGROPHOS', 'AGSTRA', 'AHLADA', 'AHLEAST', 'AHLUCONT', 'AIAENG', 'AIIL', 'AIRAN', 'AIROLAM', 'AJANTPHARM', 'AJAXENGG', 'AJMERA', 'AJOONI', 'AKASH', 'AKG', 'AKI', 'AKSHAR', 'AKSHARCHEM', 'AKSHOPTFBR', 'AKUMS', 'AKZOINDIA', 'ALANKIT', 'ALBERTDAVD', 'ALEMBICLTD', 'ALICON', 'ALIVUS', 'ALKALI', 'ALKEM', 'ALKYLAMINE', 'ALLCARGO', 'ALLDIGI', 'ALMONDZ', 'ALOKINDS', 'ALPA', 'ALPHAGEO', 'AMBER', 'AMBICAAGAR', 'AMBIKCO', 'AMBUJACEM', 'AMDIND', 'AMJLAND', 'AMNPLST', 'AMRUTANJAN', 'ANANDRATHI', 'ANANTRAJ', 'ANDHRAPAP', 'ANDHRSUGAR', 'ANGELONE', 'ANIKINDS', 'ANKITMETAL', 'ANMOL', 'ANSALAPI', 'ANTGRAPHIC', 'ANUHPHR', 'ANUP', 'ANURAS', 'APARINDS', 'APCL', 'APCOTEXIND', 'APEX', 'APLAPOLLO', 'APLLTD', 'APOLLO', 'APOLLOHOSP', 'APOLLOPIPE', 'APOLLOTYRE', 'APOLSINHOT', 'APTECHT', 'APTUS', 'ARCHIDPLY', 'ARCHIES', 'ARE&M', 'ARENTERP', 'ARIES', 'ARIHANTCAP', 'ARIHANTSUP', 'ARISINFRA', 'ARKADE', 'ARMANFIN', 'AROGRANITE', 'ARROWGREEN', 'ARSHIYA', 'ARSSINFRA', 'ARTEMISMED', 'ARTNIRMAN', 'ARVEE', 'ARVIND', 'ARVINDFASN', 'ARVSMART', 'ASAHIINDIA', 'ASAHISONG', 'ASAL', 'ASALCBR', 'ASHAPURMIN', 'ASHIANA', 'ASHIMASYN', 'ASHOKA', 'ASHOKAMET', 'ASHOKLEY', 'ASIANENE', 'ASIANHOTNR', 'ASIANPAINT', 'ASIANTILES', 'ASKAUTOLTD', 'ASMS', 'ASPINWALL', 'ASTEC', 'ASTEC-RE', 'ASTERDM', 'ASTRAL', 'ASTRAMICRO', 'ASTRAZEN', 'ASTRON', 'ATALREAL', 'ATAM', 'ATGL', 'ATHERENERG', 'ATL', 'ATLANTAA', 'ATLASCYCLE', 'ATUL', 'ATULAUTO', 'AUBANK', 'AURIONPRO', 'AUROPHARMA', 'AURUM', 'AUSOMENT', 'AUTOAXLES', 'AUTOIND', 'AVADHSUGAR', 'AVALON', 'AVANTEL', 'AVANTIFEED', 'AVG', 'AVL', 'AVONMORE', 'AVROIND', 'AVTNPL', 'AWFIS', 'AWHCL', 'AWL', 'AXISBANK', 'AXISCADES', 'AXITA', 'AYMSYNTEX', 'AZAD']
        
        # Add .NS suffix for NSE stocks
        nse_stocks = [stock + '.NS' for stock in stocks]
        
        print(f"📊 Total stocks to download: {len(nse_stocks)}")
        return nse_stocks
        
    def download_single_stock(self, symbol):
        """Download data for a single stock with error handling"""
        try:
            # Clean symbol for filename
            clean_symbol = symbol.replace('.NS', '')
            
            # Download complete data (2014-2025)
            ticker = yf.Ticker(symbol)
            complete_data = ticker.history(start="2014-01-01", end="2025-01-28")
            
            if len(complete_data) < 500:  # Need sufficient data
                return {
                    'symbol': clean_symbol,
                    'status': 'insufficient_data',
                    'records': len(complete_data),
                    'message': f'Only {len(complete_data)} records available'
                }
            
            # Split into training and testing periods
            training_data = complete_data[
                (complete_data.index >= "2014-01-01") & 
                (complete_data.index <= "2019-12-31")
            ]
            
            testing_data = complete_data[
                (complete_data.index >= "2019-01-01") & 
                (complete_data.index <= "2025-01-27")
            ]
            
            # Save training data (2014-2019)
            training_saved = False
            if len(training_data) >= 200:  # At least 200 trading days
                training_filename = f"{self.training_data_dir}/{clean_symbol}_training.csv"
                training_data.to_csv(training_filename)
                training_saved = True
                
            # Save testing data (2019-2025)
            testing_saved = False
            if len(testing_data) >= 200:  # At least 200 trading days
                testing_filename = f"{self.testing_data_dir}/{clean_symbol}_testing.csv"
                testing_data.to_csv(testing_filename)
                testing_saved = True
                
            if training_saved and testing_saved:
                return {
                    'symbol': clean_symbol,
                    'status': 'success',
                    'training_records': len(training_data),
                    'testing_records': len(testing_data),
                    'message': 'Both files saved successfully'
                }
            else:
                return {
                    'symbol': clean_symbol,
                    'status': 'partial_success',
                    'training_records': len(training_data) if training_saved else 0,
                    'testing_records': len(testing_data) if testing_saved else 0,
                    'message': f'Training: {training_saved}, Testing: {testing_saved}'
                }
                
        except Exception as e:
            return {
                'symbol': symbol.replace('.NS', ''),
                'status': 'error',
                'records': 0,
                'message': str(e)
            }
            
    def download_with_progress(self, symbols, batch_size=50, max_workers=10):
        """Download stocks in batches with progress tracking"""
        
        print(f"🚀 Starting download of {len(symbols)} stocks")
        print(f"📦 Batch size: {batch_size}, Workers: {max_workers}")
        print("=" * 60)
        
        self.stats['total_stocks'] = len(symbols)
        self.stats['start_time'] = datetime.now()
        
        results = []
        
        # Process in batches to avoid overwhelming the API
        for batch_start in range(0, len(symbols), batch_size):
            batch_end = min(batch_start + batch_size, len(symbols))
            batch_symbols = symbols[batch_start:batch_end]
            
            print(f"\n📦 Processing batch {batch_start//batch_size + 1}/{(len(symbols)-1)//batch_size + 1}")
            print(f"📊 Stocks {batch_start + 1}-{batch_end} of {len(symbols)}")
            
            # Download batch with threading
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_symbol = {
                    executor.submit(self.download_single_stock, symbol): symbol 
                    for symbol in batch_symbols
                }
                
                batch_results = []
                for future in as_completed(future_to_symbol):
                    result = future.result()
                    batch_results.append(result)
                    
                    # Update statistics
                    if result['status'] == 'success':
                        self.stats['successful_downloads'] += 1
                        print(f"✅ {result['symbol']}: {result['training_records']}+{result['testing_records']} records")
                    elif result['status'] == 'partial_success':
                        self.stats['successful_downloads'] += 1
                        print(f"⚡ {result['symbol']}: Partial - {result['message']}")
                    elif result['status'] == 'insufficient_data':
                        self.stats['insufficient_data'] += 1
                        print(f"⚠️ {result['symbol']}: {result['message']}")
                    else:
                        self.stats['failed_downloads'] += 1
                        print(f"❌ {result['symbol']}: {result['message']}")
                        
            results.extend(batch_results)
            
            # Progress summary
            completed = batch_end
            success_rate = (self.stats['successful_downloads'] / completed) * 100
            print(f"\n📊 Progress: {completed}/{len(symbols)} ({completed/len(symbols)*100:.1f}%)")
            print(f"✅ Success rate: {success_rate:.1f}%")
            
            # Small delay between batches
            if batch_end < len(symbols):
                print("⏳ Waiting 10 seconds before next batch...")
                time.sleep(10)
                
        self.stats['end_time'] = datetime.now()
        return results
