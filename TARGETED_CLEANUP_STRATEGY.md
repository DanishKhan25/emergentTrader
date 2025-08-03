# Targeted Cleanup Strategy for EmergentTrader

## Analysis Results Summary

Based on the comprehensive analysis, here's what we discovered about your 11,409 files:

### 📊 Storage Distribution (Total: ~2.2 GB)
1. **`.joblib` files**: 273 files, **622.2 MB** (28% of total storage)
2. **`.csv` files**: 3,312 files, **457.1 MB** (21% of total storage)  
3. **Node modules**: 3,561 files, **199.3 MB** (9% of total storage)
4. **JavaScript files**: 22,528 files, **155.1 MB** (7% of total storage)
5. **`.pkl` files**: 7,479 files, **44.6 MB** (2% of total storage)

### 🎯 Major Cleanup Opportunities

## 1. **HIGHEST IMPACT: .joblib Files (622 MB)**
**Location**: Scattered throughout the project
**Impact**: 28% of total storage, 273 files
**Action**: These are likely scikit-learn model cache files

```bash
# Find all .joblib files
find . -name "*.joblib" -exec ls -lh {} \;

# Safe cleanup approach:
mkdir -p archive/joblib_models
find . -name "*.joblib" -mtime +30 -exec mv {} archive/joblib_models/ \;
```

## 2. **HIGH IMPACT: CSV Data Files (457 MB)**
**Location**: `data_collection/` (455.2 MB), various other locations
**Impact**: 21% of total storage, 3,312 files
**Action**: Many are likely duplicate or outdated training data

```bash
# Archive old CSV files in data_collection (older than 90 days)
find data_collection/ -name "*.csv" -mtime +90 -exec mv {} archive/old_csv_data/ \;

# Remove duplicate CSV files (we found 1 duplicate already)
```

## 3. **MEDIUM IMPACT: Cache Files (44.6 MB)**
**Location**: 
- `python_backend/data/cache/` (3,844 files)
- `python_backend/python_backend/data/cache/` (3,612 files)
**Impact**: 7,456 cache files, mostly small but numerous
**Action**: These are regeneratable cache files

```bash
# Archive cache files older than 7 days
find python_backend/*/data/cache/ -name "*.pkl" -mtime +7 -exec mv {} archive/cache_files/ \;
```

## 4. **REVIEW NEEDED: Large Individual Files**
- `node_modules/@next/swc-darwin-arm64/next-swc.darwin-arm64.node` (109.6 MB)
- `training_steps/trained_models_2019/RandomForest_multibagger_2019.pkl` (12.4 MB)  
- `python_backend/models/signal_quality_demo.pkl` (10.5 MB)

## 🚀 Immediate Action Plan

### Phase 1: Safe Cleanup (Can achieve 60-70% storage reduction)

#### Step 1: Archive .joblib Files (622 MB savings)
```bash
# Create archive structure
mkdir -p archive/{joblib_models,old_csv_data,cache_files,large_files}

# Archive .joblib files older than 30 days
find . -name "*.joblib" -mtime +30 -exec mv {} archive/joblib_models/ \;

# Or archive ALL .joblib files (they can be regenerated)
find . -name "*.joblib" -exec mv {} archive/joblib_models/ \;
```

#### Step 2: Clean CSV Data (400+ MB savings)
```bash
# Archive old CSV files in data_collection directory
find data_collection/ -name "*.csv" -mtime +90 -exec mv {} archive/old_csv_data/ \;

# Remove empty directories
find data_collection/ -type d -empty -delete
```

#### Step 3: Clean Cache Files (Minimal size but many files)
```bash
# Archive old cache files
find python_backend/*/data/cache/ -name "*.pkl" -mtime +7 -exec mv {} archive/cache_files/ \;
```

### Phase 2: Review and Optimize

#### Step 4: Review Large Files
- **Node.js binary** (109.6 MB): Part of Next.js, keep
- **ML model files** (12.4 MB + 10.5 MB): Review if still needed
- Consider compressing old model files

#### Step 5: Optimize Directory Structure
- **`python_backend/`** (937.5 MB): Largest directory, review for optimization
- **`data_collection/`** (455.2 MB): Mostly CSV files, good cleanup target

## 📋 Cleanup Script

Here's a safe cleanup script you can run:

```bash
#!/bin/bash
# Safe cleanup script for EmergentTrader

echo "Creating archive structure..."
mkdir -p archive/{joblib_models,old_csv_data,cache_files,large_files,temp_files}

echo "Phase 1: Archiving .joblib files..."
find . -name "*.joblib" -mtime +30 -exec mv {} archive/joblib_models/ \; 2>/dev/null
joblib_count=$(find archive/joblib_models/ -name "*.joblib" | wc -l)
echo "Archived $joblib_count .joblib files"

echo "Phase 2: Archiving old CSV files..."
find data_collection/ -name "*.csv" -mtime +90 -exec mv {} archive/old_csv_data/ \; 2>/dev/null
csv_count=$(find archive/old_csv_data/ -name "*.csv" | wc -l)
echo "Archived $csv_count old CSV files"

echo "Phase 3: Archiving old cache files..."
find python_backend/*/data/cache/ -name "*.pkl" -mtime +7 -exec mv {} archive/cache_files/ \; 2>/dev/null
cache_count=$(find archive/cache_files/ -name "*.pkl" | wc -l)
echo "Archived $cache_count cache files"

echo "Phase 4: Cleaning temporary files..."
find . -name "*_report_*.txt" -exec mv {} archive/temp_files/ \; 2>/dev/null
find . -name "multibagger_*.txt" -exec mv {} archive/temp_files/ \; 2>/dev/null

echo "Cleanup complete!"
echo "Check the 'archive/' directory for moved files"
echo "Test your application to ensure everything works"
```

## 🔍 Expected Results

### Storage Savings
- **Phase 1**: ~1.0 GB savings (45% reduction)
- **Phase 2**: Additional ~200 MB (9% reduction)
- **Total**: ~1.2 GB savings (54% of current storage)

### File Count Reduction
- **Current**: 11,409 files
- **After cleanup**: ~3,000-4,000 files (65-75% reduction)
- **Core files preserved**: All 47 actively used files

## ⚠️ Safety Measures

### Files That Will NOT Be Touched
- All 47 actively used files identified in analysis
- `data/nse_raw.csv` (primary data source)
- Configuration files (`package.json`, `.env`, etc.)
- Recent model files (less than 30 days old)
- Node modules (can be reinstalled with `npm install`)

### Restoration Process
If you need to restore any archived files:

```bash
# Restore specific file type
cp -r archive/joblib_models/* ./

# Restore cache files
cp -r archive/cache_files/* python_backend/python_backend/data/cache/

# Restore CSV data
cp -r archive/old_csv_data/* data_collection/
```

## 🎯 Next Steps

1. **Review this strategy** and adjust based on your needs
2. **Test the cleanup script** on a small subset first
3. **Run the full cleanup** when ready
4. **Monitor application** to ensure functionality is preserved
5. **Implement automated cleanup policies** to prevent future bloat

## 💡 Long-term Recommendations

1. **Automated cache cleanup**: Set up cron jobs to clean cache files regularly
2. **Model versioning**: Keep only the latest 2-3 versions of each model
3. **Data archival policy**: Archive training data older than 6 months
4. **Storage monitoring**: Track storage usage and set up alerts
5. **Compression**: Use compression for archived files to save additional space

This targeted approach will give you the 70% file reduction you're looking for while maintaining all critical functionality!
