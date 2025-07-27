#!/usr/bin/env python3
"""
Step 1: Comprehensive Historical Data Collector
Downloads 10 years of data for ALL available NSE stocks
"""

import yfinance as yf
import pandas as pd
import os
import requests
from datetime import datetime
import time

def get_nse_stock_list():
    """Get comprehensive list of NSE stocks"""
    
    # NIFTY 500 stocks (comprehensive list)
    nifty_500_symbols = [
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
        "CONCOR.NS", "CONTAINER.NS", "IRCTC.NS", "RAILTEL.NS", "RVNL.NS",
        "SJVN.NS", "NHPC.NS", "THDC.NS", "NBCC.NS", "BEL.NS",
        "HAL.NS", "BEML.NS", "BHEL.NS", "RITES.NS", "IRCON.NS",
        "HUDCO.NS", "RECLTD.NS", "PFC.NS", "INDIANB.NS", "CANBK.NS",
        "BANKBARODA.NS", "PNB.NS", "UNIONBANK.NS", "IDFCFIRSTB.NS", "FEDERALBNK.NS",
        
        # IT and Tech Stocks
        "MINDTREE.NS", "MPHASIS.NS", "LTTS.NS", "PERSISTENT.NS", "COFORGE.NS",
        "LTIM.NS", "TATAELXSI.NS", "KPITTECH.NS", "NIITTECH.NS", "CYIENT.NS",
        "ROLTA.NS", "SONATSOFTW.NS", "ZENSAR.NS", "HEXAWARE.NS", "OFSS.NS",
        
        # Pharma Stocks
        "AUROPHARMA.NS", "TORNTPHARM.NS", "ALKEM.NS", "ABBOTINDIA.NS", "PFIZER.NS",
        "GSK.NS", "NOVARTIS.NS", "SANOFI.NS", "JBCHEPHARM.NS", "STRIDES.NS",
        "LALPATHLAB.NS", "METROPOLIS.NS", "THYROCARE.NS", "KRBL.NS", "JUBLFOOD.NS",
        
        # Auto Stocks
        "MAHINDRA.NS", "ASHOKLEY.NS", "TVSMOTOR.NS", "BAJAJHLDNG.NS", "MOTHERSUMI.NS",
        "BOSCHLTD.NS", "EXIDEIND.NS", "AMARAJABAT.NS", "MRF.NS", "APOLLOTYRE.NS",
        "CEAT.NS", "BALKRISIND.NS", "ESCORTS.NS", "FORCEMOT.NS", "MAHINDCIE.NS",
        
        # Banking and Finance
        "BANDHANBNK.NS", "RBLBANK.NS", "YESBANK.NS", "EQUITAS.NS", "CHOLAFIN.NS",
        "M&MFIN.NS", "BAJAJHFL.NS", "LICHSGFIN.NS", "REPCO.NS", "SRTRANSFIN.NS",
        "MANAPPURAM.NS", "MUTHOOTFIN.NS", "GOLDENBEES.NS", "ICICIGI.NS", "ICICIPRULI.NS",
        
        # Consumer Goods
        "EMAMILTD.NS", "VGUARD.NS", "CROMPTON.NS", "WHIRLPOOL.NS", "BLUESTARCO.NS",
        "RAJESHEXPO.NS", "TITAN.NS", "KALPATPOWR.NS", "SIEMENS.NS", "ABB.NS",
        "SCHNEIDER.NS", "HONAUT.NS", "THERMAX.NS", "CUMMINSIND.NS", "KIRLOSENG.NS",
        
        # Metals and Mining
        "JINDALSTEL.NS", "JSPL.NS", "RATNAMANI.NS", "WELCORP.NS", "WELSPUNIND.NS",
        "APLAPOLLO.NS", "CAPLIPOINT.NS", "KAJARIACER.NS", "ORIENTCEM.NS", "HEIDELBERG.NS",
        "RAMCOCEM.NS", "JKCEMENT.NS", "DALMIACEMT.NS", "AMBUJACEMENT.NS", "ACC.NS",
        
        # Oil and Gas
        "RELIANCE.NS", "IOC.NS", "BPCL.NS", "HPCL.NS", "GAIL.NS",
        "OIL.NS", "MRPL.NS", "CASTROLIND.NS", "PETRONET.NS", "GSPL.NS",
        
        # Telecom
        "BHARTIARTL.NS", "IDEA.NS", "RCOM.NS", "GTLINFRA.NS", "RPOWER.NS",
        
        # Real Estate
        "DLF.NS", "GODREJPROP.NS", "OBEROIRLTY.NS", "PRESTIGE.NS", "BRIGADE.NS",
        "SOBHA.NS", "PHOENIXLTD.NS", "MAHLIFE.NS", "SUNTECK.NS", "KOLTEPATIL.NS",
        
        # Textiles
        "RAYMOND.NS", "ARVIND.NS", "WELSPUNIND.NS", "TRIDENT.NS", "VARDHACRLC.NS",
        "ALOKTEXT.NS", "RSWM.NS", "SPENTEX.NS", "ORIENTBELL.NS", "GARFIBRES.NS",
        
        # Agriculture and Food
        "BRITANNIA.NS", "NESTLEIND.NS", "JUBLFOOD.NS", "TATACONSUM.NS", "GODREJCP.NS",
        "MARICO.NS", "DABUR.NS", "EMAMILTD.NS", "JYOTHYLAB.NS", "CHOLAHLDNG.NS",
        "KRBL.NS", "USHAMART.NS", "VSTIND.NS", "RALLIS.NS", "COROMANDEL.NS",
        
        # Additional Growth Stocks
        "ZOMATO.NS", "PAYTM.NS", "NYKAA.NS", "POLICYBZR.NS", "CARTRADE.NS",
        "EASEMYTRIP.NS", "DEVYANI.NS", "SAPPHIRE.NS", "CLEAN.NS", "ANURAS.NS"
    ]
    
    print(f"📊 Total stocks to download: {len(nifty_500_symbols)}")
    return nifty_500_symbols

def download_comprehensive_data():
    """Download comprehensive historical data"""
    
    symbols = get_nse_stock_list()
    
    print("📊 Starting comprehensive data download...")
    print(f"🎯 Target: {len(symbols)} stocks")
    print("📅 Period: 2014-2025 (10+ years)")
    
    # Create data directory
    os.makedirs("comprehensive_historical_data", exist_ok=True)
    
    successful_downloads = 0
    failed_downloads = []
    
    for i, symbol in enumerate(symbols, 1):
        try:
            print(f"[{i}/{len(symbols)}] Downloading {symbol}...")
            
            # Download 2014-2025 data
            ticker = yf.Ticker(symbol)
            data = ticker.history(start="2014-01-01", end="2025-01-01")
            
            if len(data) > 500:  # At least 2 years of data
                # Save to CSV
                filename = f"comprehensive_historical_data/{symbol.replace('.NS', '')}_10year.csv"
                data.to_csv(filename)
                print(f"✅ {symbol}: {len(data)} records saved")
                successful_downloads += 1
            else:
                print(f"⚠️ {symbol}: Insufficient data ({len(data)} records)")
                failed_downloads.append(f"{symbol} - Insufficient data")
                
            # Small delay to avoid rate limiting
            time.sleep(0.1)
                
        except Exception as e:
            print(f"❌ {symbol}: Error - {str(e)}")
            failed_downloads.append(f"{symbol} - {str(e)}")
            
        # Progress update every 50 stocks
        if i % 50 == 0:
            print(f"\n📊 Progress: {i}/{len(symbols)} completed ({successful_downloads} successful)")
            print("-" * 50)
    
    # Final summary
    print(f"\n🎉 DOWNLOAD COMPLETED!")
    print(f"✅ Successful: {successful_downloads}/{len(symbols)} stocks")
    print(f"❌ Failed: {len(failed_downloads)} stocks")
    print(f"📁 Data saved in 'comprehensive_historical_data/' folder")
    
    # Save failed downloads log
    if failed_downloads:
        with open("failed_downloads.txt", "w") as f:
            f.write("Failed Downloads:\n")
            for failure in failed_downloads:
                f.write(f"{failure}\n")
        print(f"📝 Failed downloads logged in 'failed_downloads.txt'")
    
    return successful_downloads > 100  # Need at least 100 stocks for good training

def get_data_summary():
    """Get summary of downloaded data"""
    data_dir = "comprehensive_historical_data"
    
    if not os.path.exists(data_dir):
        print("❌ No data directory found")
        return
        
    files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    
    print(f"\n📊 DATA SUMMARY:")
    print(f"📁 Total files: {len(files)}")
    
    total_records = 0
    date_ranges = []
    
    for file in files[:10]:  # Sample first 10 files
        try:
            df = pd.read_csv(f"{data_dir}/{file}")
            total_records += len(df)
            
            if 'Date' in df.columns:
                dates = pd.to_datetime(df['Date'])
                date_ranges.append({
                    'symbol': file.replace('_10year.csv', ''),
                    'start': dates.min(),
                    'end': dates.max(),
                    'records': len(df)
                })
        except:
            continue
    
    print(f"📈 Sample records: {total_records:,}")
    print(f"📅 Date range: {min(dr['start'] for dr in date_ranges)} to {max(dr['end'] for dr in date_ranges)}")
    
    return len(files)

if __name__ == "__main__":
    print("🚀 Comprehensive NSE Data Collector")
    print("=" * 50)
    
    success = download_comprehensive_data()
    
    if success:
        file_count = get_data_summary()
        print(f"\n✅ SUCCESS! Downloaded {file_count} stock files")
        print("🚀 Next: Run step2_train_2019.py")
    else:
        print("\n❌ Download failed - insufficient data collected")
