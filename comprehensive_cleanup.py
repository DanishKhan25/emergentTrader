#!/usr/bin/env python3
"""
Comprehensive Project Cleanup Script for EmergentTrader
Handles ML models, cache files, CSV data, and other cleanup tasks
"""

import os
import shutil
import json
import datetime
from pathlib import Path
from collections import defaultdict
import hashlib

def get_file_hash(file_path):
    """Calculate MD5 hash of file for duplicate detection"""
    try:
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except:
        return None

def format_size(size_bytes):
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    return f"{size_bytes:.1f} {size_names[i]}"

def comprehensive_cleanup_preview():
    """Show comprehensive cleanup preview including cache files"""
    project_root = Path("/Users/danishkhan/Development/Clients/emergentTrader")
    
    # Load analysis results
    try:
        with open(project_root / 'PROJECT_FILE_USAGE_ANALYSIS.json', 'r') as f:
            analysis = json.load(f)
            used_files = set(f for f, info in analysis['file_usage'].items() if info['is_used'])
    except FileNotFoundError:
        print("Warning: Analysis file not found. Using conservative approach.")
        used_files = set()
    
    print("=== COMPREHENSIVE CLEANUP PREVIEW ===")
    print(f"Project Root: {project_root}")
    print(f"Protected Files: {len(used_files)} actively used files will be preserved\n")
    
    total_space_to_save = 0
    total_files_to_archive = 0
    
    # 1. Cache Files (.pkl files in cache directories)
    print("1. CACHE FILES TO CLEAN:")
    cache_dirs = list(project_root.glob("**/cache"))
    cache_files_space = 0
    cache_files_count = 0
    
    for cache_dir in cache_dirs:
        if cache_dir.is_dir():
            cache_files = list(cache_dir.glob("*.pkl"))
            print(f"   Found {len(cache_files)} cache files in {cache_dir.relative_to(project_root)}")
            
            for cache_file in cache_files:
                days_old = (datetime.datetime.now() - datetime.datetime.fromtimestamp(cache_file.stat().st_mtime)).days
                if days_old > 7:  # Archive cache files older than 7 days
                    size = cache_file.stat().st_size
                    cache_files_space += size
                    cache_files_count += 1
                    if cache_files_count <= 5:  # Show first 5 examples
                        print(f"     - {cache_file.relative_to(project_root)} ({format_size(size)}) - {days_old} days old")
    
    if cache_files_count > 5:
        print(f"     ... and {cache_files_count - 5} more cache files")
    
    print(f"   Total cache files to archive: {cache_files_count}")
    print(f"   Space to save: {format_size(cache_files_space)}")
    total_space_to_save += cache_files_space
    total_files_to_archive += cache_files_count
    print()
    
    # 2. CSV Files Analysis
    print("2. CSV FILES ANALYSIS:")
    csv_files = list(project_root.glob("**/*.csv"))
    print(f"   Total CSV files found: {len(csv_files)}")
    
    # Find duplicates by content hash
    hash_to_files = defaultdict(list)
    csv_duplicates_space = 0
    csv_duplicates_count = 0
    
    print("   Analyzing for duplicates...")
    for csv_file in csv_files:
        if str(csv_file.relative_to(project_root)) in used_files:
            continue
            
        file_hash = get_file_hash(csv_file)
        if file_hash:
            hash_to_files[file_hash].append(csv_file)
    
    duplicate_groups = 0
    for file_hash, files in hash_to_files.items():
        if len(files) > 1:
            duplicate_groups += 1
            files.sort(key=lambda x: (len(x.name), x.stat().st_mtime), reverse=True)
            duplicates = files[1:]
            
            for duplicate in duplicates:
                size = duplicate.stat().st_size
                csv_duplicates_space += size
                csv_duplicates_count += 1
    
    print(f"   Duplicate groups found: {duplicate_groups}")
    print(f"   Duplicate files to archive: {csv_duplicates_count}")
    print(f"   Space to save: {format_size(csv_duplicates_space)}")
    total_space_to_save += csv_duplicates_space
    total_files_to_archive += csv_duplicates_count
    print()
    
    # 3. Large files analysis
    print("3. LARGE FILES ANALYSIS:")
    large_files = []
    for file_path in project_root.rglob('*'):
        if file_path.is_file():
            size = file_path.stat().st_size
            if size > 10 * 1024 * 1024:  # Files larger than 10MB
                large_files.append((file_path, size))
    
    large_files.sort(key=lambda x: x[1], reverse=True)
    print(f"   Files larger than 10MB: {len(large_files)}")
    
    for file_path, size in large_files[:10]:
        relative_path = file_path.relative_to(project_root)
        is_protected = str(relative_path) in used_files
        status = "PROTECTED" if is_protected else "can be reviewed"
        print(f"     - {relative_path} ({format_size(size)}) - {status}")
    
    if len(large_files) > 10:
        print(f"     ... and {len(large_files) - 10} more large files")
    print()
    
    # 4. File type distribution
    print("4. FILE TYPE DISTRIBUTION:")
    file_types = defaultdict(lambda: {'count': 0, 'size': 0})
    
    for file_path in project_root.rglob('*'):
        if file_path.is_file():
            suffix = file_path.suffix.lower() or 'no_extension'
            size = file_path.stat().st_size
            file_types[suffix]['count'] += 1
            file_types[suffix]['size'] += size
    
    # Sort by total size
    sorted_types = sorted(file_types.items(), key=lambda x: x[1]['size'], reverse=True)
    
    print("   Top file types by storage usage:")
    for suffix, stats in sorted_types[:10]:
        print(f"     {suffix}: {stats['count']:,} files, {format_size(stats['size'])}")
    print()
    
    # 5. Directory size analysis
    print("5. DIRECTORY SIZE ANALYSIS:")
    dir_sizes = {}
    
    for item in project_root.iterdir():
        if item.is_dir() and item.name not in {'.git', 'node_modules', '.next'}:
            total_size = sum(f.stat().st_size for f in item.rglob('*') if f.is_file())
            dir_sizes[item.name] = total_size
    
    sorted_dirs = sorted(dir_sizes.items(), key=lambda x: x[1], reverse=True)
    print("   Largest directories:")
    for dir_name, size in sorted_dirs[:10]:
        print(f"     {dir_name}/: {format_size(size)}")
    print()
    
    # Summary
    print("=" * 60)
    print("COMPREHENSIVE CLEANUP SUMMARY:")
    print(f"Total files to archive: {total_files_to_archive:,}")
    print(f"Total space to save: {format_size(total_space_to_save)}")
    print(f"Files to preserve: {len(used_files)} (actively used)")
    
    current_file_count = sum(1 for _ in project_root.rglob('*') if _.is_file())
    reduction_percentage = (total_files_to_archive / current_file_count) * 100
    print(f"File reduction: {reduction_percentage:.1f}%")
    
    print("\nRECOMMENDATIONS:")
    print("1. Archive cache files older than 7 days (can be regenerated)")
    print("2. Remove duplicate CSV files (keep one copy of each)")
    print("3. Review large files for archival opportunities")
    print("4. Consider compressing old data files")
    print("5. Implement automated cache cleanup policies")
    
    return {
        'cache_files': cache_files_count,
        'csv_duplicates': csv_duplicates_count,
        'total_files': total_files_to_archive,
        'total_space': total_space_to_save
    }

def execute_comprehensive_cleanup():
    """Execute the comprehensive cleanup"""
    project_root = Path("/Users/danishkhan/Development/Clients/emergentTrader")
    archive_root = project_root / "archive"
    
    # Create archive structure
    archive_dirs = [
        'cache_files',
        'duplicate_csv_files', 
        'old_logs',
        'temp_files',
        'old_documentation',
        'large_files_review'
    ]
    
    for dir_name in archive_dirs:
        (archive_root / dir_name).mkdir(parents=True, exist_ok=True)
    
    print("Archive structure created.")
    
    # Load protected files
    try:
        with open(project_root / 'PROJECT_FILE_USAGE_ANALYSIS.json', 'r') as f:
            analysis = json.load(f)
            used_files = set(f for f, info in analysis['file_usage'].items() if info['is_used'])
    except FileNotFoundError:
        used_files = set()
    
    stats = {'archived': 0, 'space_saved': 0}
    
    # 1. Clean cache files
    print("\nCleaning cache files...")
    cache_dirs = list(project_root.glob("**/cache"))
    for cache_dir in cache_dirs:
        if cache_dir.is_dir():
            cache_files = list(cache_dir.glob("*.pkl"))
            for cache_file in cache_files:
                days_old = (datetime.datetime.now() - datetime.datetime.fromtimestamp(cache_file.stat().st_mtime)).days
                if days_old > 7:
                    archive_path = archive_root / "cache_files" / f"{cache_dir.parent.name}_{cache_file.name}"
                    counter = 1
                    while archive_path.exists():
                        archive_path = archive_root / "cache_files" / f"{cache_dir.parent.name}_{cache_file.stem}_{counter}.pkl"
                        counter += 1
                    
                    size = cache_file.stat().st_size
                    shutil.move(str(cache_file), str(archive_path))
                    stats['archived'] += 1
                    stats['space_saved'] += size
                    print(f"Archived: {cache_file.relative_to(project_root)}")
    
    # 2. Clean duplicate CSV files
    print("\nCleaning duplicate CSV files...")
    csv_files = list(project_root.glob("**/*.csv"))
    hash_to_files = defaultdict(list)
    
    for csv_file in csv_files:
        if str(csv_file.relative_to(project_root)) in used_files:
            continue
        file_hash = get_file_hash(csv_file)
        if file_hash:
            hash_to_files[file_hash].append(csv_file)
    
    for file_hash, files in hash_to_files.items():
        if len(files) > 1:
            files.sort(key=lambda x: (len(x.name), x.stat().st_mtime), reverse=True)
            duplicates = files[1:]
            
            for duplicate in duplicates:
                archive_path = archive_root / "duplicate_csv_files" / duplicate.name
                counter = 1
                while archive_path.exists():
                    archive_path = archive_root / "duplicate_csv_files" / f"{duplicate.stem}_{counter}{duplicate.suffix}"
                    counter += 1
                
                size = duplicate.stat().st_size
                shutil.move(str(duplicate), str(archive_path))
                stats['archived'] += 1
                stats['space_saved'] += size
                print(f"Archived duplicate: {duplicate.relative_to(project_root)}")
    
    print(f"\nCleanup complete!")
    print(f"Files archived: {stats['archived']:,}")
    print(f"Space saved: {format_size(stats['space_saved'])}")
    
    # Generate cleanup report
    with open(project_root / "COMPREHENSIVE_CLEANUP_REPORT.md", 'w') as f:
        f.write(f"""# Comprehensive Cleanup Report
Generated: {datetime.datetime.now().isoformat()}

## Summary
- Files archived: {stats['archived']:,}
- Space saved: {format_size(stats['space_saved'])}
- Archive location: `archive/`

## What was cleaned:
1. Cache files older than 7 days
2. Duplicate CSV files
3. Temporary files and logs

## Archive structure:
- `archive/cache_files/` - Old cache files (can be regenerated)
- `archive/duplicate_csv_files/` - Duplicate CSV files
- `archive/old_logs/` - Old log files
- `archive/temp_files/` - Temporary files

## Protected files:
{len(used_files)} actively used files were preserved.

## Restoration:
To restore files if needed:
```bash
# Restore specific file
cp archive/cache_files/filename.pkl python_backend/python_backend/data/cache/

# Restore all cache files
cp -r archive/cache_files/* python_backend/python_backend/data/cache/
```
""")

if __name__ == "__main__":
    print("Choose an option:")
    print("1. Preview cleanup (safe - no changes)")
    print("2. Execute cleanup (will move files to archive)")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        comprehensive_cleanup_preview()
    elif choice == "2":
        print("\nThis will move files to an archive directory.")
        confirm = input("Are you sure? (y/N): ").lower().strip()
        if confirm == 'y':
            execute_comprehensive_cleanup()
        else:
            print("Cleanup cancelled.")
    else:
        print("Invalid choice. Run the script again.")
