#!/usr/bin/env python3
"""
Preview Cleanup Script - Shows what will be cleaned up without making changes
"""

import os
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

def preview_cleanup():
    project_root = Path("/Users/danishkhan/Development/Clients/emergentTrader")
    
    # Load analysis results
    try:
        with open(project_root / 'PROJECT_FILE_USAGE_ANALYSIS.json', 'r') as f:
            analysis = json.load(f)
            used_files = set(f for f, info in analysis['file_usage'].items() if info['is_used'])
    except FileNotFoundError:
        print("Warning: Analysis file not found. Using conservative approach.")
        used_files = set()
    
    cleanup_preview = {
        'ml_models': [],
        'csv_duplicates': [],
        'old_logs': [],
        'temp_files': [],
        'old_docs': [],
        'test_artifacts': [],
        'backup_files': []
    }
    
    total_space_to_save = 0
    total_files_to_archive = 0
    
    print("=== CLEANUP PREVIEW ===")
    print(f"Project Root: {project_root}")
    print(f"Protected Files: {len(used_files)} actively used files will be preserved\n")
    
    # 1. ML Models Preview
    print("1. ML MODELS TO ARCHIVE:")
    model_dirs = [
        project_root / "models",
        project_root / "trained_models_2019", 
        project_root / "trained_models_2019_2025"
    ]
    
    ml_models_space = 0
    ml_models_count = 0
    
    for model_dir in model_dirs:
        if not model_dir.exists():
            continue
            
        pkl_files = list(model_dir.glob("**/*.pkl"))
        if not pkl_files:
            continue
        
        # Group files by base name
        file_groups = defaultdict(list)
        for pkl_file in pkl_files:
            base_name = pkl_file.stem.split('_')[0] if '_' in pkl_file.stem else pkl_file.stem
            file_groups[base_name].append(pkl_file)
        
        for base_name, files in file_groups.items():
            if len(files) > 2:
                files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                files_to_archive = files[2:]
                
                for file_to_archive in files_to_archive:
                    size = file_to_archive.stat().st_size
                    ml_models_space += size
                    ml_models_count += 1
                    cleanup_preview['ml_models'].append({
                        'file': str(file_to_archive.relative_to(project_root)),
                        'size': format_size(size),
                        'reason': f'Old version of {base_name} (keeping 2 recent)'
                    })
    
    print(f"   Files to archive: {ml_models_count}")
    print(f"   Space to save: {format_size(ml_models_space)}")
    if ml_models_count > 0:
        print("   Sample files:")
        for item in cleanup_preview['ml_models'][:5]:
            print(f"     - {item['file']} ({item['size']})")
        if ml_models_count > 5:
            print(f"     ... and {ml_models_count - 5} more")
    print()
    
    # 2. CSV Duplicates Preview
    print("2. DUPLICATE CSV FILES:")
    csv_files = list(project_root.glob("**/*.csv"))
    
    # Find duplicates by content hash
    hash_to_files = defaultdict(list)
    csv_duplicates_space = 0
    csv_duplicates_count = 0
    
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
                size = duplicate.stat().st_size
                csv_duplicates_space += size
                csv_duplicates_count += 1
                cleanup_preview['csv_duplicates'].append({
                    'file': str(duplicate.relative_to(project_root)),
                    'size': format_size(size),
                    'reason': f'Duplicate of {files[0].name}'
                })
    
    print(f"   Files to archive: {csv_duplicates_count}")
    print(f"   Space to save: {format_size(csv_duplicates_space)}")
    if csv_duplicates_count > 0:
        print("   Sample files:")
        for item in cleanup_preview['csv_duplicates'][:5]:
            print(f"     - {item['file']} ({item['size']})")
        if csv_duplicates_count > 5:
            print(f"     ... and {csv_duplicates_count - 5} more")
    print()
    
    # 3. Old Logs Preview
    print("3. OLD LOG FILES (>30 days):")
    log_files = list(project_root.glob("**/*.log"))
    old_logs_space = 0
    old_logs_count = 0
    
    for log_file in log_files:
        days_old = (datetime.datetime.now() - datetime.datetime.fromtimestamp(log_file.stat().st_mtime)).days
        if days_old > 30:
            size = log_file.stat().st_size
            old_logs_space += size
            old_logs_count += 1
            cleanup_preview['old_logs'].append({
                'file': str(log_file.relative_to(project_root)),
                'size': format_size(size),
                'reason': f'{days_old} days old'
            })
    
    print(f"   Files to archive: {old_logs_count}")
    print(f"   Space to save: {format_size(old_logs_space)}")
    if old_logs_count > 0:
        print("   Sample files:")
        for item in cleanup_preview['old_logs'][:3]:
            print(f"     - {item['file']} ({item['size']}) - {item['reason']}")
    print()
    
    # 4. Temporary Files Preview
    print("4. TEMPORARY FILES:")
    temp_patterns = [
        "*_report_*.txt",
        "*_signals_*.txt", 
        "*_validation_*.txt",
        "multibagger_*.txt"
    ]
    
    temp_files_space = 0
    temp_files_count = 0
    
    for pattern in temp_patterns:
        temp_files = list(project_root.glob(pattern))
        for temp_file in temp_files:
            size = temp_file.stat().st_size
            temp_files_space += size
            temp_files_count += 1
            cleanup_preview['temp_files'].append({
                'file': str(temp_file.relative_to(project_root)),
                'size': format_size(size),
                'reason': 'Temporary report file'
            })
    
    # Empty database files
    db_files = list(project_root.glob("**/*.db")) + list(project_root.glob("**/*.sqlite"))
    for db_file in db_files:
        if db_file.stat().st_size == 0:
            temp_files_count += 1
            cleanup_preview['temp_files'].append({
                'file': str(db_file.relative_to(project_root)),
                'size': '0 B',
                'reason': 'Empty database file'
            })
    
    print(f"   Files to archive: {temp_files_count}")
    print(f"   Space to save: {format_size(temp_files_space)}")
    if temp_files_count > 0:
        print("   Sample files:")
        for item in cleanup_preview['temp_files'][:3]:
            print(f"     - {item['file']} ({item['size']})")
    print()
    
    # 5. Documentation Preview
    print("5. OLD DOCUMENTATION FILES:")
    md_files = list(project_root.glob("*.md"))
    
    doc_groups = {
        'status_reports': [],
        'implementation_guides': [],
        'analysis_reports': [],
        'training_guides': [],
        'other': []
    }
    
    for md_file in md_files:
        name_lower = md_file.name.lower()
        if any(keyword in name_lower for keyword in ['status', 'complete', 'percent']):
            doc_groups['status_reports'].append(md_file)
        elif any(keyword in name_lower for keyword in ['implementation', 'guide', 'setup']):
            doc_groups['implementation_guides'].append(md_file)
        elif any(keyword in name_lower for keyword in ['analysis', 'summary', 'report']):
            doc_groups['analysis_reports'].append(md_file)
        elif any(keyword in name_lower for keyword in ['training', 'ml', 'ai']):
            doc_groups['training_guides'].append(md_file)
        else:
            doc_groups['other'].append(md_file)
    
    old_docs_space = 0
    old_docs_count = 0
    
    for category, files in doc_groups.items():
        if len(files) > 3:
            files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            files_to_archive = files[3:]
            
            for doc_file in files_to_archive:
                size = doc_file.stat().st_size
                old_docs_space += size
                old_docs_count += 1
                cleanup_preview['old_docs'].append({
                    'file': str(doc_file.relative_to(project_root)),
                    'size': format_size(size),
                    'reason': f'Old {category} (keeping 3 recent)'
                })
    
    print(f"   Files to archive: {old_docs_count}")
    print(f"   Space to save: {format_size(old_docs_space)}")
    if old_docs_count > 0:
        print("   Sample files:")
        for item in cleanup_preview['old_docs'][:3]:
            print(f"     - {item['file']} ({item['size']})")
    print()
    
    # Calculate totals
    total_space_to_save = ml_models_space + csv_duplicates_space + old_logs_space + temp_files_space + old_docs_space
    total_files_to_archive = ml_models_count + csv_duplicates_count + old_logs_count + temp_files_count + old_docs_count
    
    print("=" * 60)
    print("CLEANUP SUMMARY:")
    print(f"Total files to archive: {total_files_to_archive:,}")
    print(f"Total space to save: {format_size(total_space_to_save)}")
    print(f"Files to preserve: {len(used_files)} (actively used)")
    
    current_file_count = sum(1 for _ in project_root.rglob('*') if _.is_file())
    reduction_percentage = (total_files_to_archive / current_file_count) * 100
    print(f"File reduction: {reduction_percentage:.1f}%")
    
    print("\nARCHIVE STRUCTURE TO BE CREATED:")
    print("archive/")
    print("├── old_ml_models/")
    print("├── duplicate_csv_files/")
    print("├── old_logs/")
    print("├── temp_files/")
    print("├── old_documentation/")
    print("├── test_artifacts/")
    print("└── backup_files/")
    
    print(f"\nPROTECTED FILES (will NOT be touched):")
    print("These are the 47 actively used files identified in the analysis:")
    for used_file in sorted(list(used_files)[:10]):
        print(f"  - {used_file}")
    if len(used_files) > 10:
        print(f"  ... and {len(used_files) - 10} more")
    
    print("\n" + "=" * 60)
    print("To proceed with the actual cleanup, run:")
    print("python3 safe_project_cleanup.py")

if __name__ == "__main__":
    preview_cleanup()
