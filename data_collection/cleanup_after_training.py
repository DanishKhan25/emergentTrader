#!/usr/bin/env python3
"""
Data Cleanup Script - Run after ML training is complete
Removes raw data files to save disk space while preserving trained models
"""

import os
import shutil
from datetime import datetime

def get_directory_size(path):
    """Calculate directory size in MB"""
    total_size = 0
    if os.path.exists(path):
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if os.path.exists(filepath):
                    total_size += os.path.getsize(filepath)
    return total_size / (1024 * 1024)  # Convert to MB

def cleanup_raw_data():
    """Remove raw data files after training"""
    
    print("🧹 POST-TRAINING DATA CLEANUP")
    print("=" * 50)
    
    # Directories to clean up
    cleanup_dirs = [
        "training_data_2014_2019",
        "testing_data_2019_2025", 
        "comprehensive_historical_data"
    ]
    
    # Files to clean up
    cleanup_files = [
        "failed_downloads.txt",
        "nse_fast_results_*.json",
        "*.log"
    ]
    
    total_space_freed = 0
    
    # Check what will be deleted
    print("📊 SPACE ANALYSIS:")
    for directory in cleanup_dirs:
        if os.path.exists(directory):
            size_mb = get_directory_size(directory)
            file_count = sum([len(files) for r, d, files in os.walk(directory)])
            print(f"   📁 {directory}: {size_mb:.1f} MB ({file_count} files)")
            total_space_freed += size_mb
        else:
            print(f"   📁 {directory}: Not found")
    
    print(f"\n💾 Total space to be freed: {total_space_freed:.1f} MB")
    
    # Ask for confirmation
    response = input("\n❓ Proceed with cleanup? (y/N): ").lower().strip()
    
    if response != 'y':
        print("❌ Cleanup cancelled")
        return False
    
    print("\n🗑️ CLEANING UP...")
    
    # Remove directories
    for directory in cleanup_dirs:
        if os.path.exists(directory):
            try:
                shutil.rmtree(directory)
                print(f"✅ Removed: {directory}/")
            except Exception as e:
                print(f"❌ Error removing {directory}: {e}")
    
    # Remove individual files
    for pattern in cleanup_files:
        if '*' in pattern:
            # Handle wildcard patterns
            import glob
            for file in glob.glob(pattern):
                try:
                    os.remove(file)
                    print(f"✅ Removed: {file}")
                except Exception as e:
                    print(f"❌ Error removing {file}: {e}")
        else:
            if os.path.exists(pattern):
                try:
                    os.remove(pattern)
                    print(f"✅ Removed: {pattern}")
                except Exception as e:
                    print(f"❌ Error removing {pattern}: {e}")
    
    print(f"\n🎉 Cleanup completed! Freed ~{total_space_freed:.1f} MB")
    return True

def verify_essential_files():
    """Verify that essential files are still present"""
    
    print("\n🔍 VERIFYING ESSENTIAL FILES:")
    
    essential_dirs = [
        "trained_models_2019",
        "signals_2019", 
        "validation_results",
        "reports"
    ]
    
    essential_files = [
        "*.pkl",  # Model files
        "*.joblib",  # Scikit-learn models
        "*.json",  # Results and configs
        "*.csv"   # Signal outputs
    ]
    
    all_good = True
    
    # Check directories
    for directory in essential_dirs:
        if os.path.exists(directory):
            file_count = sum([len(files) for r, d, files in os.walk(directory)])
            print(f"✅ {directory}: {file_count} files")
        else:
            print(f"⚠️ {directory}: Missing")
            all_good = False
    
    # Check for model files
    import glob
    model_files = glob.glob("*.pkl") + glob.glob("*.joblib") + glob.glob("trained_models_2019/*.pkl")
    if model_files:
        print(f"✅ Found {len(model_files)} model files")
    else:
        print("⚠️ No model files found")
        all_good = False
    
    if all_good:
        print("\n✅ All essential files verified!")
    else:
        print("\n⚠️ Some essential files may be missing")
    
    return all_good

def create_cleanup_summary():
    """Create a summary of what was cleaned up"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    summary_file = f"cleanup_summary_{timestamp}.txt"
    
    with open(summary_file, "w") as f:
        f.write("DATA CLEANUP SUMMARY\n")
        f.write("=" * 30 + "\n")
        f.write(f"Cleanup Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("REMOVED:\n")
        f.write("- training_data_2014_2019/ (raw training data)\n")
        f.write("- testing_data_2019_2025/ (raw testing data)\n") 
        f.write("- comprehensive_historical_data/ (downloaded CSV files)\n")
        f.write("- Various log files and temporary data\n\n")
        
        f.write("PRESERVED:\n")
        f.write("- trained_models_2019/ (ML models)\n")
        f.write("- signals_2019/ (generated signals)\n")
        f.write("- validation_results/ (performance metrics)\n")
        f.write("- reports/ (analysis reports)\n")
        f.write("- All Python scripts and code\n\n")
        
        f.write("NOTE: Raw data can be re-downloaded if needed using:\n")
        f.write("python data_collection/step1_corrected_data_collector.py\n")
    
    print(f"📝 Cleanup summary saved: {summary_file}")

def main():
    """Main cleanup function"""
    
    print("🚀 ML Training Data Cleanup Tool")
    print("🎯 Removes raw data while preserving trained models")
    print("=" * 60)
    
    # Verify essential files first
    if not verify_essential_files():
        print("\n⚠️ WARNING: Essential files may be missing!")
        response = input("Continue anyway? (y/N): ").lower().strip()
        if response != 'y':
            print("❌ Cleanup aborted")
            return
    
    # Perform cleanup
    if cleanup_raw_data():
        create_cleanup_summary()
        
        print("\n🎉 SUCCESS!")
        print("✅ Raw data cleaned up")
        print("✅ Trained models preserved") 
        print("✅ Ready for production use")
        print("\n💡 TIP: You can re-download data anytime using:")
        print("   python data_collection/step1_corrected_data_collector.py")
    else:
        print("\n❌ Cleanup was not completed")

if __name__ == "__main__":
    main()
