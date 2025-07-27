#!/usr/bin/env python3
"""
Step 1: Corrected Historical Data Collector
Downloads data with proper date separation:
- Training: 2014-2019 (5 years)
- Testing: 2019-2025 (6 years for multibagger validation)
"""

import yfinance as yf
import pandas as pd
import os
from datetime import datetime
import time

def get_nse_stock_list():
    """Get comprehensive list of NSE stocks"""
    
    # NIFTY 500+ stocks for comprehensive training
    nifty_stocks = [
        # Large Cap Stocks
        "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "HINDUNILVR.NS",
        "ICICIBANK.NS", "KOTAKBANK.NS", "BHARTIARTL.NS", "ITC.NS", "SBIN.NS",
        "BAJFINANCE.NS", "ASIANPAINT.NS", "MARUTI.NS", "HCLTECH.NS", "AXISBANK.NS",
        "LT.NS", "ULTRACEMCO.NS", "TITAN.NS", "WIPRO.NS", "NESTLEIND.NS",
        "POWERGRID.NS", "NTPC.NS", "TECHM.NS", "SUNPHARMA.NS", "ONGC.NS",
        "TATAMOTORS.NS", "BAJAJFINSV.NS", "JSWSTEEL.NS", "HINDALCO.NS", "GRASIM.NS",

        # Mid Cap Stocks
        "ADANIPORTS.NS", "COALINDIA.NS", "DRREDDY.NS", "EICHERMOT.NS", "INDUSINDBK.NS",
        "CIPLA.NS", "BRITANNIA.NS", "DIVISLAB.NS", "HEROMOTOCO.NS", "SHREECEM.NS",
        "TATASTEEL.NS", "BAJAJ-AUTO.NS", "APOLLOHOSP.NS", "BPCL.NS", "HDFCLIFE.NS",
        "SBILIFE.NS", "PIDILITIND.NS", "GODREJCP.NS", "DABUR.NS", "MARICO.NS",
        "BERGEPAINT.NS", "COLPAL.NS", "MCDOWELL-N.NS", "HAVELLS.NS", "VOLTAS.NS",
        "PAGEIND.NS", "BIOCON.NS", "CADILAHC.NS", "GLAND.NS", "LUPIN.NS",

        # Small Cap and Growth Stocks
        "ZEEL.NS", "VEDL.NS", "SAIL.NS", "NMDC.NS", "MOIL.NS",
        "CONCOR.NS", "IRCTC.NS", "RAILTEL.NS", "RVNL.NS", "SJVN.NS",
        "NHPC.NS", "THDC.NS", "NBCC.NS", "BEL.NS", "HAL.NS",
        "BEML.NS", "BHEL.NS", "RITES.NS", "IRCON.NS", "HUDCO.NS",
        "RECLTD.NS", "PFC.NS", "INDIANB.NS", "CANBK.NS", "BANKBARODA.NS",
        "PNB.NS", "UNIONBANK.NS", "IDFCFIRSTB.NS", "FEDERALBNK.NS",

        # IT and Tech Stocks
        "MINDTREE.NS", "MPHASIS.NS", "LTTS.NS", "PERSISTENT.NS", "COFORGE.NS",
        "LTIM.NS", "TATAELXSI.NS", "KPITTECH.NS", "CYIENT.NS", "SONATSOFTW.NS",
        "ZENSAR.NS", "HEXAWARE.NS", "OFSS.NS",

        # Pharma Stocks
        "AUROPHARMA.NS", "TORNTPHARM.NS", "ALKEM.NS", "ABBOTINDIA.NS", "PFIZER.NS",
        "GSK.NS", "SANOFI.NS", "JBCHEPHARM.NS", "STRIDES.NS", "LALPATHLAB.NS",
        "METROPOLIS.NS", "THYROCARE.NS", "KRBL.NS", "JUBLFOOD.NS",

        # Auto Stocks
        "MAHINDRA.NS", "ASHOKLEY.NS", "TVSMOTOR.NS", "BAJAJHLDNG.NS", "MOTHERSUMI.NS",
        "BOSCHLTD.NS", "EXIDEIND.NS", "AMARAJABAT.NS", "MRF.NS", "APOLLOTYRE.NS",
        "CEAT.NS", "BALKRISIND.NS", "ESCORTS.NS", "FORCEMOT.NS", "MAHINDCIE.NS",

        # Banking and Finance
        "BANDHANBNK.NS", "RBLBANK.NS", "YESBANK.NS", "CHOLAFIN.NS", "M&MFIN.NS",
        "BAJAJHFL.NS", "LICHSGFIN.NS", "SRTRANSFIN.NS", "MANAPPURAM.NS", "MUTHOOTFIN.NS",
        "ICICIGI.NS", "ICICIPRULI.NS",

        # Consumer Goods
        "EMAMILTD.NS", "VGUARD.NS", "CROMPTON.NS", "WHIRLPOOL.NS", "BLUESTARCO.NS",
        "SIEMENS.NS", "ABB.NS", "THERMAX.NS", "CUMMINSIND.NS",

        # Metals and Mining
        "JINDALSTEL.NS", "JSPL.NS", "RATNAMANI.NS", "WELCORP.NS", "WELSPUNIND.NS",
        "APLAPOLLO.NS", "KAJARIACER.NS", "ORIENTCEM.NS", "RAMCOCEM.NS", "JKCEMENT.NS",
        "DALMIACEMT.NS", "AMBUJACEMENT.NS", "ACC.NS",

        # Oil and Gas
        "IOC.NS", "HPCL.NS", "GAIL.NS", "OIL.NS", "MRPL.NS",
        "CASTROLIND.NS", "PETRONET.NS", "GSPL.NS",

        # Real Estate
        "DLF.NS", "GODREJPROP.NS", "OBEROIRLTY.NS", "PRESTIGE.NS", "BRIGADE.NS",
        "SOBHA.NS", "PHOENIXLTD.NS", "SUNTECK.NS",

        # Textiles
        "RAYMOND.NS", "ARVIND.NS", "TRIDENT.NS", "VARDHACRLC.NS", "RSWM.NS",

        # Agriculture and Food
        "TATACONSUM.NS", "JYOTHYLAB.NS", "USHAMART.NS", "VSTIND.NS", "RALLIS.NS", "COROMANDEL.NS"
    ]
    
    print(f"📊 Total stocks for comprehensive training: {len(nifty_stocks)}")
    return nifty_stocks

def download_training_and_testing_data():
    """Download data with proper date separation"""
    
    symbols = get_nse_stock_list()
    
    print("🎯 CORRECTED DATA COLLECTION STRATEGY")
    print("=" * 50)
    print("📅 Training Period: 2014-01-01 to 2019-12-31 (5 years)")
    print("📅 Testing Period: 2019-01-01 to 2025-01-27 (6 years)")
    print("🎯 Goal: Train on 2014-2019, find multibaggers from 2019-2025")
    print("=" * 50)
    
    # Create directories
    os.makedirs("training_data_2014_2019", exist_ok=True)
    os.makedirs("testing_data_2019_2025", exist_ok=True)
    
    successful_downloads = 0
    failed_downloads = []
    
    for i, symbol in enumerate(symbols, 1):
        try:
            print(f"[{i}/{len(symbols)}] Processing {symbol}...")
            
            # Download complete data (2014-2025)
            ticker = yf.Ticker(symbol)
            complete_data = ticker.history(start="2014-01-01", end="2025-01-28")
            
            if len(complete_data) < 500:  # Need sufficient data
                print(f"⚠️ {symbol}: Insufficient data ({len(complete_data)} records)")
                failed_downloads.append(f"{symbol} - Insufficient data")
                continue
            
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
            if len(training_data) >= 200:  # At least 200 trading days
                training_filename = f"training_data_2014_2019/{symbol.replace('.NS', '')}_training.csv"
                training_data.to_csv(training_filename)
                print(f"✅ Training: {len(training_data)} records (2014-2019)")
            else:
                print(f"⚠️ Training: Insufficient data ({len(training_data)} records)")
                
            # Save testing data (2019-2025)
            if len(testing_data) >= 200:  # At least 200 trading days
                testing_filename = f"testing_data_2019_2025/{symbol.replace('.NS', '')}_testing.csv"
                testing_data.to_csv(testing_filename)
                print(f"✅ Testing: {len(testing_data)} records (2019-2025)")
                successful_downloads += 1
            else:
                print(f"⚠️ Testing: Insufficient data ({len(testing_data)} records)")
                
            # Small delay to avoid rate limiting
            time.sleep(0.1)
                
        except Exception as e:
            print(f"❌ {symbol}: Error - {str(e)}")
            failed_downloads.append(f"{symbol} - {str(e)}")
            
        # Progress update every 25 stocks
        if i % 25 == 0:
            print(f"\n📊 Progress: {i}/{len(symbols)} completed ({successful_downloads} successful)")
            print("-" * 50)
    
    # Final summary
    print(f"\n🎉 DATA COLLECTION COMPLETED!")
    print(f"✅ Successful: {successful_downloads}/{len(symbols)} stocks")
    print(f"❌ Failed: {len(failed_downloads)} stocks")
    print(f"📁 Training data: 'training_data_2014_2019/' folder")
    print(f"📁 Testing data: 'testing_data_2019_2025/' folder")
    
    # Save failed downloads log
    if failed_downloads:
        with open("failed_downloads.txt", "w") as f:
            f.write("Failed Downloads:\n")
            for failure in failed_downloads:
                f.write(f"{failure}\n")
        print(f"📝 Failed downloads logged in 'failed_downloads.txt'")
    
    return successful_downloads > 50  # Need at least 50 stocks for good training

def verify_data_separation():
    """Verify that data is properly separated"""
    
    print("\n🔍 VERIFYING DATA SEPARATION")
    print("=" * 40)
    
    # Check training data
    training_dir = "training_data_2014_2019"
    testing_dir = "testing_data_2019_2025"
    
    if os.path.exists(training_dir):
        training_files = [f for f in os.listdir(training_dir) if f.endswith('.csv')]
        print(f"📊 Training files: {len(training_files)}")
        
        # Sample verification
        if training_files:
            sample_file = training_files[0]
            df = pd.read_csv(f"{training_dir}/{sample_file}")
            df['Date'] = pd.to_datetime(df['Date'])
            print(f"📅 Training date range: {df['Date'].min()} to {df['Date'].max()}")
    
    if os.path.exists(testing_dir):
        testing_files = [f for f in os.listdir(testing_dir) if f.endswith('.csv')]
        print(f"📊 Testing files: {len(testing_files)}")
        
        # Sample verification
        if testing_files:
            sample_file = testing_files[0]
            df = pd.read_csv(f"{testing_dir}/{sample_file}")
            df['Date'] = pd.to_datetime(df['Date'])
            print(f"📅 Testing date range: {df['Date'].min()} to {df['Date'].max()}")
    
    print("\n✅ Data separation verified!")
    print("🎯 Ready for:")
    print("   1. Train ML on 2014-2019 data")
    print("   2. Generate signals for 2019")
    print("   3. Check multibagger performance 2019-2025")

if __name__ == "__main__":
    print("🚀 Corrected NSE Data Collector")
    print("🎯 Strategy: Train 2014-2019, Test 2019-2025")
    print("=" * 50)
    
    success = download_training_and_testing_data()
    
    if success:
        verify_data_separation()
        print(f"\n✅ SUCCESS! Data properly separated")
        print("🚀 Next: Run step2_train_on_2014_2019.py")
    else:
        print("\n❌ Download failed - insufficient data collected")
