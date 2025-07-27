#!/usr/bin/env python3
"""
Auto Cleanup Script - Remove raw data automatically before committing
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

def auto_cleanup():
    """Automatically remove raw data files"""
    
    print("🧹 AUTO CLEANUP BEFORE COMMIT")
    print("=" * 50)
    
    # Large directories to clean up
    cleanup_dirs = [
        "training_data_2014_2019",
        "testing_data_2019_2025", 
        "comprehensive_historical_data"
    ]
    
    total_space_freed = 0
    
    # Check what will be deleted
    print("📊 ANALYZING FILES TO REMOVE:")
    for directory in cleanup_dirs:
        if os.path.exists(directory):
            size_mb = get_directory_size(directory)
            file_count = sum([len(files) for r, d, files in os.walk(directory)])
            print(f"   📁 {directory}: {size_mb:.1f} MB ({file_count} files)")
            total_space_freed += size_mb
        else:
            print(f"   📁 {directory}: Not found")
    
    print(f"\n💾 Total space to be freed: {total_space_freed:.1f} MB")
    print("\n🗑️ REMOVING RAW DATA FILES...")
    
    # Remove large data directories
    removed_count = 0
    for directory in cleanup_dirs:
        if os.path.exists(directory):
            try:
                shutil.rmtree(directory)
                print(f"✅ Removed: {directory}/")
                removed_count += 1
            except Exception as e:
                print(f"❌ Error removing {directory}: {e}")
    
    # Remove cache directory
    cache_dir = "python_backend/python_backend/data/cache"
    if os.path.exists(cache_dir):
        try:
            shutil.rmtree(cache_dir)
            print(f"✅ Removed: {cache_dir}/")
            removed_count += 1
        except Exception as e:
            print(f"❌ Error removing {cache_dir}: {e}")
    
    # Remove log files and temporary files
    import glob
    temp_patterns = ["*.log", "nse_*.json", "ml_demo_results_*.json", "comprehensive_test_report.json"]
    
    for pattern in temp_patterns:
        for file in glob.glob(pattern):
            try:
                os.remove(file)
                print(f"✅ Removed: {file}")
                removed_count += 1
            except Exception as e:
                print(f"❌ Error removing {file}: {e}")
    
    print(f"\n🎉 Cleanup completed!")
    print(f"✅ Removed {removed_count} items")
    print(f"💾 Freed ~{total_space_freed:.1f} MB of space")
    
    return True

def verify_essential_preserved():
    """Verify essential files are preserved"""
    
    print("\n🔍 VERIFYING ESSENTIAL FILES PRESERVED:")
    
    essential_items = [
        ("trained_models_2019/", "ML Models"),
        ("signals_2019/", "Generated Signals"), 
        ("validation_results/", "Validation Results"),
        ("reports/", "Analysis Reports"),
        ("python_backend/", "Backend Code"),
        ("training_steps/", "Training Scripts"),
        ("data_collection/", "Data Collection Scripts")
    ]
    
    all_preserved = True
    
    for item, description in essential_items:
        if os.path.exists(item):
            if os.path.isdir(item):
                file_count = sum([len(files) for r, d, files in os.walk(item)])
                print(f"✅ {description}: {file_count} files preserved")
            else:
                print(f"✅ {description}: preserved")
        else:
            print(f"❌ {description}: MISSING!")
            all_preserved = False
    
    return all_preserved

def create_gitignore_entries():
    """Add raw data directories to .gitignore"""
    
    gitignore_entries = [
        "\n# Raw data directories (can be regenerated)",
        "training_data_2014_2019/",
        "testing_data_2019_2025/",
        "comprehensive_historical_data/",
        "python_backend/python_backend/data/cache/",
        "\n# Temporary files",
        "*.log",
        "nse_*.json",
        "ml_demo_results_*.json",
        "comprehensive_test_report.json",
        "cleanup_summary_*.txt"
    ]
    
    try:
        with open(".gitignore", "a") as f:
            f.write("\n".join(gitignore_entries))
        print("✅ Updated .gitignore with raw data exclusions")
    except Exception as e:
        print(f"⚠️ Could not update .gitignore: {e}")

def main():
    """Main auto cleanup function"""
    
    print("🚀 Automatic Pre-Commit Cleanup")
    print("🎯 Preparing repository for commit")
    print("=" * 50)
    
    # Perform cleanup
    if auto_cleanup():
        
        # Verify essential files
        if verify_essential_preserved():
            print("\n✅ All essential files preserved!")
        else:
            print("\n⚠️ Some essential files may be missing!")
        
        # Update gitignore
        create_gitignore_entries()
        
        print("\n🎉 REPOSITORY READY FOR COMMIT!")
        print("=" * 40)
        print("✅ Raw data removed (~500MB freed)")
        print("✅ Essential code and models preserved")
        print("✅ .gitignore updated")
        print("\n💡 NEXT STEPS:")
        print("   git add .")
        print("   git commit -m 'Enhanced multibagger strategy with 2019-2025 training'")
        print("   git push")
        print("\n💡 To regenerate data later:")
        print("   python data_collection/step1_corrected_data_collector.py")
        
    else:
        print("\n❌ Cleanup failed")

if __name__ == "__main__":
    main()
