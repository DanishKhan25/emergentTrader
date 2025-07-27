#!/usr/bin/env python3
"""
Cleanup Script - Remove raw data before committing to git
Keeps essential files while removing large data files
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
    """Remove raw data files before git commit"""
    
    print("🧹 CLEANUP BEFORE COMMIT")
    print("=" * 50)
    
    # Large directories to clean up
    cleanup_dirs = [
        "training_data_2014_2019",
        "testing_data_2019_2025", 
        "comprehensive_historical_data"
    ]
    
    # Cache and temporary files
    cleanup_patterns = [
        "python_backend/python_backend/data/cache",
        "*.log",
        "nse_*.json",
        "ml_demo_results_*.json",
        "strategy_test_results.json",
        "comprehensive_test_report.json"
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
    
    # Remove large data directories
    for directory in cleanup_dirs:
        if os.path.exists(directory):
            try:
                shutil.rmtree(directory)
                print(f"✅ Removed: {directory}/")
            except Exception as e:
                print(f"❌ Error removing {directory}: {e}")
    
    # Remove cache directory
    cache_dir = "python_backend/python_backend/data/cache"
    if os.path.exists(cache_dir):
        try:
            shutil.rmtree(cache_dir)
            print(f"✅ Removed: {cache_dir}/")
        except Exception as e:
            print(f"❌ Error removing {cache_dir}: {e}")
    
    # Remove log files and temporary files
    import glob
    temp_patterns = ["*.log", "nse_*.json", "ml_demo_results_*.json"]
    
    for pattern in temp_patterns:
        for file in glob.glob(pattern):
            try:
                os.remove(file)
                print(f"✅ Removed: {file}")
            except Exception as e:
                print(f"❌ Error removing {file}: {e}")
    
    print(f"\n🎉 Cleanup completed! Freed ~{total_space_freed:.1f} MB")
    return True

def verify_essential_files():
    """Verify that essential files are still present"""
    
    print("\n🔍 VERIFYING ESSENTIAL FILES:")
    
    essential_items = [
        "trained_models_2019/",
        "signals_2019/", 
        "validation_results/",
        "reports/",
        "analysis/",
        "backtesting/",
        "data_collection/",
        "training_steps/",
        "python_backend/",
        "app/",
        "components/"
    ]
    
    all_good = True
    
    for item in essential_items:
        if os.path.exists(item):
            if os.path.isdir(item):
                file_count = sum([len(files) for r, d, files in os.walk(item)])
                print(f"✅ {item}: {file_count} files")
            else:
                print(f"✅ {item}: exists")
        else:
            print(f"⚠️ {item}: Missing")
            if item in ["trained_models_2019/", "signals_2019/"]:
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
        f.write("PRE-COMMIT CLEANUP SUMMARY\n")
        f.write("=" * 30 + "\n")
        f.write(f"Cleanup Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("REMOVED (Large Data Files):\n")
        f.write("- training_data_2014_2019/ (raw training CSV files)\n")
        f.write("- testing_data_2019_2025/ (raw testing CSV files)\n") 
        f.write("- comprehensive_historical_data/ (downloaded CSV files)\n")
        f.write("- python_backend/python_backend/data/cache/ (cache files)\n")
        f.write("- Various log files and temporary JSON files\n\n")
        
        f.write("PRESERVED (Essential Files):\n")
        f.write("- trained_models_2019/ (ML models)\n")
        f.write("- signals_2019/ (generated signals)\n")
        f.write("- validation_results/ (performance metrics)\n")
        f.write("- reports/ (analysis reports)\n")
        f.write("- All Python source code\n")
        f.write("- All configuration files\n")
        f.write("- Documentation and README files\n\n")
        
        f.write("NOTE: Raw data can be re-downloaded if needed using:\n")
        f.write("python data_collection/step1_corrected_data_collector.py\n\n")
        
        f.write("READY FOR GIT COMMIT:\n")
        f.write("- Repository size significantly reduced\n")
        f.write("- Only essential code and models preserved\n")
        f.write("- Raw data excluded from version control\n")
    
    print(f"📝 Cleanup summary saved: {summary_file}")

def main():
    """Main cleanup function"""
    
    print("🚀 Pre-Commit Cleanup Tool")
    print("🎯 Removes large data files while preserving code and models")
    print("=" * 60)
    
    # Verify essential files first
    if not verify_essential_files():
        print("\n⚠️ WARNING: Some essential files may be missing!")
        response = input("Continue cleanup anyway? (y/N): ").lower().strip()
        if response != 'y':
            print("❌ Cleanup aborted")
            return
    
    # Perform cleanup
    if cleanup_raw_data():
        create_cleanup_summary()
        
        print("\n🎉 SUCCESS!")
        print("✅ Raw data cleaned up")
        print("✅ Essential files preserved") 
        print("✅ Ready for git commit")
        print("\n💡 NEXT STEPS:")
        print("   1. git add .")
        print("   2. git commit -m 'Update multibagger strategy and training system'")
        print("   3. git push")
        print("\n💡 TIP: Raw data can be re-downloaded anytime using:")
        print("   python data_collection/step1_corrected_data_collector.py")
    else:
        print("\n❌ Cleanup was not completed")

if __name__ == "__main__":
    main()
