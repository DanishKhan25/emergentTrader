"""
Data Cache Manager - Handles caching of stock data to reduce API calls
Implements file-based caching with TTL (Time To Live) support
"""

import os
import json
import pickle
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class DataCache:
    def __init__(self, cache_dir: str = "python_backend/data/cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Cache TTL settings (in hours)
        self.ttl_settings = {
            'stock_data': 4,      # Stock price data - 4 hours
            'stock_info': 24,     # Fundamental data - 24 hours
            'nse_universe': 168,  # NSE stock list - 1 week
            'shariah_universe': 24, # Shariah stocks - 24 hours
            'shariah_compliance': 2160,  # Individual Shariah compliance - 3 months (90 days * 24 hours)
            'signals': 1,         # Generated signals - 1 hour
            'technical_indicators': 2  # Technical analysis - 2 hours
        }
        
        logger.info(f"Data cache initialized at: {self.cache_dir}")
    
    def _get_cache_file(self, cache_type: str, key: str) -> Path:
        """Get cache file path for given type and key"""
        safe_key = key.replace('/', '_').replace('\\', '_').replace(':', '_')
        return self.cache_dir / f"{cache_type}_{safe_key}.pkl"
    
    def _is_cache_valid(self, cache_file: Path, cache_type: str) -> bool:
        """Check if cache file is still valid based on TTL"""
        if not cache_file.exists():
            return False
        
        try:
            file_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
            ttl_hours = self.ttl_settings.get(cache_type, 24)
            expiry_time = file_time + timedelta(hours=ttl_hours)
            
            is_valid = datetime.now() < expiry_time
            if not is_valid:
                logger.debug(f"Cache expired for {cache_file.name}")
            
            return is_valid
            
        except Exception as e:
            logger.error(f"Error checking cache validity: {str(e)}")
            return False
    
    def get(self, cache_type: str, key: str) -> Optional[Any]:
        """Get data from cache if valid"""
        try:
            cache_file = self._get_cache_file(cache_type, key)
            
            if not self._is_cache_valid(cache_file, cache_type):
                return None
            
            with open(cache_file, 'rb') as f:
                data = pickle.load(f)
                logger.debug(f"Cache hit for {cache_type}:{key}")
                return data
                
        except Exception as e:
            logger.error(f"Error reading from cache: {str(e)}")
            return None
    
    def set(self, cache_type: str, key: str, data: Any) -> bool:
        """Store data in cache"""
        try:
            cache_file = self._get_cache_file(cache_type, key)
            
            with open(cache_file, 'wb') as f:
                pickle.dump(data, f)
                logger.debug(f"Cache stored for {cache_type}:{key}")
                return True
                
        except Exception as e:
            logger.error(f"Error writing to cache: {str(e)}")
            return False
    
    def delete(self, cache_type: str, key: str) -> bool:
        """Delete specific cache entry"""
        try:
            cache_file = self._get_cache_file(cache_type, key)
            if cache_file.exists():
                cache_file.unlink()
                logger.debug(f"Cache deleted for {cache_type}:{key}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error deleting cache: {str(e)}")
            return False
    
    def clear_expired(self) -> int:
        """Clear all expired cache entries"""
        cleared_count = 0
        
        try:
            for cache_file in self.cache_dir.glob("*.pkl"):
                # Extract cache type from filename
                cache_type = cache_file.stem.split('_')[0]
                
                if not self._is_cache_valid(cache_file, cache_type):
                    cache_file.unlink()
                    cleared_count += 1
                    logger.debug(f"Cleared expired cache: {cache_file.name}")
            
            logger.info(f"Cleared {cleared_count} expired cache entries")
            return cleared_count
            
        except Exception as e:
            logger.error(f"Error clearing expired cache: {str(e)}")
            return 0
    
    def clear_all(self, cache_type: Optional[str] = None) -> int:
        """Clear all cache entries or specific type"""
        cleared_count = 0
        
        try:
            pattern = f"{cache_type}_*.pkl" if cache_type else "*.pkl"
            
            for cache_file in self.cache_dir.glob(pattern):
                cache_file.unlink()
                cleared_count += 1
                logger.debug(f"Cleared cache: {cache_file.name}")
            
            logger.info(f"Cleared {cleared_count} cache entries")
            return cleared_count
            
        except Exception as e:
            logger.error(f"Error clearing cache: {str(e)}")
            return 0
    
    def clear_cache_type(self, cache_type: str) -> bool:
        """Clear all cache entries of a specific type"""
        try:
            cache_dir = os.path.join(self.cache_dir, cache_type)
            if os.path.exists(cache_dir):
                import shutil
                shutil.rmtree(cache_dir)
                os.makedirs(cache_dir, exist_ok=True)
                logger.info(f"Cleared cache type: {cache_type}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error clearing cache type {cache_type}: {str(e)}")
            return False
    
    def clear_all_cache(self) -> bool:
        """Clear all cache entries"""
        try:
            if os.path.exists(self.cache_dir):
                import shutil
                shutil.rmtree(self.cache_dir)
                os.makedirs(self.cache_dir, exist_ok=True)
                logger.info("Cleared all cache")
                return True
            return False
        except Exception as e:
            logger.error(f"Error clearing all cache: {str(e)}")
            return False
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        stats = {
            'total_files': 0,
            'total_size_mb': 0,
            'by_type': {},
            'expired_count': 0
        }
        
        try:
            for cache_file in self.cache_dir.glob("*.pkl"):
                stats['total_files'] += 1
                stats['total_size_mb'] += cache_file.stat().st_size / (1024 * 1024)
                
                # Extract cache type
                cache_type = cache_file.stem.split('_')[0]
                if cache_type not in stats['by_type']:
                    stats['by_type'][cache_type] = {'count': 0, 'size_mb': 0}
                
                stats['by_type'][cache_type]['count'] += 1
                stats['by_type'][cache_type]['size_mb'] += cache_file.stat().st_size / (1024 * 1024)
                
                # Check if expired
                if not self._is_cache_valid(cache_file, cache_type):
                    stats['expired_count'] += 1
            
            stats['total_size_mb'] = round(stats['total_size_mb'], 2)
            for cache_type in stats['by_type']:
                stats['by_type'][cache_type]['size_mb'] = round(stats['by_type'][cache_type]['size_mb'], 2)
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting cache stats: {str(e)}")
            return stats

# Global cache instance
cache = DataCache()

def get_cached_stock_data(symbol: str, period: str = "1y") -> Optional[pd.DataFrame]:
    """Get cached stock data"""
    cache_key = f"{symbol}_{period}"
    return cache.get('stock_data', cache_key)

def set_cached_stock_data(symbol: str, period: str, data: pd.DataFrame) -> bool:
    """Cache stock data"""
    cache_key = f"{symbol}_{period}"
    return cache.set('stock_data', cache_key, data)

def get_cached_stock_info(symbol: str) -> Optional[Dict]:
    """Get cached stock info"""
    return cache.get('stock_info', symbol)

def set_cached_stock_info(symbol: str, info: Dict) -> bool:
    """Cache stock info"""
    return cache.set('stock_info', symbol, info)

def get_cached_signals(strategy: str, symbols: List[str]) -> Optional[List[Dict]]:
    """Get cached signals"""
    cache_key = f"{strategy}_{'_'.join(sorted(symbols))}"
    return cache.get('signals', cache_key)

def set_cached_signals(strategy: str, symbols: List[str], signals: List[Dict]) -> bool:
    """Cache signals"""
    cache_key = f"{strategy}_{'_'.join(sorted(symbols))}"
    return cache.set('signals', cache_key, signals)

def get_cached_shariah_compliance(symbol: str) -> Optional[Dict]:
    """Get cached Shariah compliance data"""
    return cache.get('shariah_compliance', symbol)

def set_cached_shariah_compliance(symbol: str, compliance_data: Dict) -> bool:
    """Cache Shariah compliance data"""
    return cache.set('shariah_compliance', symbol, compliance_data)

def refresh_shariah_compliance_cache(symbol: str) -> bool:
    """Force refresh Shariah compliance cache for a symbol"""
    return cache.delete('shariah_compliance', symbol)

def get_cached_shariah_summary() -> Optional[Dict]:
    """Get cached Shariah compliance summary"""
    return cache.get('shariah_summary', 'latest')

def set_cached_shariah_summary(summary_data: Dict) -> bool:
    """Cache Shariah compliance summary"""
    return cache.set('shariah_summary', 'latest', summary_data)

if __name__ == "__main__":
    # Test cache functionality
    cache = DataCache()
    
    # Test basic operations
    test_data = {"test": "data", "timestamp": datetime.now().isoformat()}
    
    print("Testing cache operations...")
    print(f"Set: {cache.set('test', 'key1', test_data)}")
    print(f"Get: {cache.get('test', 'key1')}")
    print(f"Stats: {cache.get_cache_stats()}")
    print(f"Clear: {cache.clear_all('test')}")
