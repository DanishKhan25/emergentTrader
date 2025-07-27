"""
Advanced Logging Service for EmergentTrader
Provides comprehensive logging with dynamic level configuration
"""

import os
import logging
import logging.handlers
from datetime import datetime
from typing import Dict, List, Optional
import json
from pathlib import Path

class EmergentTraderLogger:
    def __init__(self, log_dir: str = "logs"):
        """Initialize the advanced logging system"""
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Current log level (can be changed dynamically)
        self.current_level = logging.INFO
        
        # Available log levels
        self.log_levels = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        
        # Initialize loggers
        self.loggers = {}
        self.setup_loggers()
        
        # Log configuration file
        self.config_file = self.log_dir / "logging_config.json"
        self.load_config()
        
    def setup_loggers(self):
        """Setup different loggers for different components"""
        
        # Main application logger
        self.setup_logger(
            'main', 
            self.log_dir / 'emergent_trader.log',
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Trading signals logger
        self.setup_logger(
            'signals',
            self.log_dir / 'signals.log',
            '%(asctime)s - SIGNAL - %(levelname)s - %(message)s'
        )
        
        # Portfolio operations logger
        self.setup_logger(
            'portfolio',
            self.log_dir / 'portfolio.log',
            '%(asctime)s - PORTFOLIO - %(levelname)s - %(message)s'
        )
        
        # API requests logger
        self.setup_logger(
            'api',
            self.log_dir / 'api.log',
            '%(asctime)s - API - %(levelname)s - %(message)s'
        )
        
        # Notifications logger
        self.setup_logger(
            'notifications',
            self.log_dir / 'notifications.log',
            '%(asctime)s - NOTIFY - %(levelname)s - %(message)s'
        )
        
        # Errors logger (all errors from all components)
        self.setup_logger(
            'errors',
            self.log_dir / 'errors.log',
            '%(asctime)s - ERROR - %(name)s - %(levelname)s - %(message)s',
            level=logging.ERROR
        )
        
        # Performance logger
        self.setup_logger(
            'performance',
            self.log_dir / 'performance.log',
            '%(asctime)s - PERF - %(message)s'
        )
        
    def setup_logger(self, name: str, log_file: Path, format_str: str, level: int = None):
        """Setup individual logger with rotation"""
        logger = logging.getLogger(f'emergent_trader.{name}')
        logger.setLevel(level or self.current_level)
        
        # Remove existing handlers
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # File handler with rotation (10MB max, keep 5 files)
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(level or self.current_level)
        file_formatter = logging.Formatter(format_str)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        # Console handler for important logs
        if level is None or level >= logging.WARNING:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.WARNING)
            console_formatter = logging.Formatter(
                '%(levelname)s - %(name)s - %(message)s'
            )
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)
        
        self.loggers[name] = logger
        
    def get_logger(self, component: str = 'main') -> logging.Logger:
        """Get logger for specific component"""
        return self.loggers.get(component, self.loggers['main'])
    
    def set_log_level(self, level: str) -> Dict:
        """Dynamically change log level for all loggers"""
        try:
            if level.upper() not in self.log_levels:
                return {
                    'success': False,
                    'error': f'Invalid log level. Available: {list(self.log_levels.keys())}'
                }
            
            new_level = self.log_levels[level.upper()]
            self.current_level = new_level
            
            # Update all loggers
            for logger_name, logger in self.loggers.items():
                if logger_name != 'errors':  # Keep errors logger at ERROR level
                    logger.setLevel(new_level)
                    for handler in logger.handlers:
                        if not isinstance(handler, logging.StreamHandler):
                            handler.setLevel(new_level)
            
            # Save configuration
            self.save_config()
            
            # Log the change
            self.get_logger('main').info(f"Log level changed to {level.upper()}")
            
            return {
                'success': True,
                'message': f'Log level set to {level.upper()}',
                'level': level.upper()
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_log_level(self) -> str:
        """Get current log level"""
        for name, level in self.log_levels.items():
            if level == self.current_level:
                return name
        return 'INFO'
    
    def save_config(self):
        """Save logging configuration"""
        config = {
            'log_level': self.get_log_level(),
            'log_dir': str(self.log_dir),
            'last_updated': datetime.now().isoformat()
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def load_config(self):
        """Load logging configuration"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                
                level = config.get('log_level', 'INFO')
                self.set_log_level(level)
                
        except Exception as e:
            # If config loading fails, use default INFO level
            self.get_logger('main').warning(f"Could not load logging config: {e}")
    
    def get_log_files(self) -> List[Dict]:
        """Get list of available log files"""
        log_files = []
        
        for log_file in self.log_dir.glob('*.log*'):
            try:
                stat = log_file.stat()
                log_files.append({
                    'name': log_file.name,
                    'path': str(log_file),
                    'size': stat.st_size,
                    'size_mb': round(stat.st_size / (1024*1024), 2),
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'component': log_file.stem
                })
            except Exception as e:
                continue
        
        return sorted(log_files, key=lambda x: x['modified'], reverse=True)
    
    def get_recent_logs(self, component: str = 'main', lines: int = 100) -> List[str]:
        """Get recent log entries from a specific component"""
        try:
            log_file = self.log_dir / f'{component}.log'
            if not log_file.exists():
                return []
            
            with open(log_file, 'r') as f:
                all_lines = f.readlines()
                return [line.strip() for line in all_lines[-lines:]]
                
        except Exception as e:
            return [f"Error reading log file: {str(e)}"]
    
    def search_logs(self, query: str, component: str = None, days: int = 7) -> List[Dict]:
        """Search logs for specific patterns"""
        results = []
        
        # Determine which log files to search
        if component:
            log_files = [self.log_dir / f'{component}.log']
        else:
            log_files = list(self.log_dir.glob('*.log'))
        
        for log_file in log_files:
            if not log_file.exists():
                continue
                
            try:
                with open(log_file, 'r') as f:
                    for line_num, line in enumerate(f, 1):
                        if query.lower() in line.lower():
                            results.append({
                                'file': log_file.name,
                                'line_number': line_num,
                                'content': line.strip(),
                                'component': log_file.stem
                            })
            except Exception as e:
                continue
        
        return results[-1000:]  # Limit to last 1000 matches
    
    def get_log_stats(self) -> Dict:
        """Get logging statistics"""
        stats = {
            'current_level': self.get_log_level(),
            'total_log_files': len(list(self.log_dir.glob('*.log*'))),
            'total_size_mb': 0,
            'components': {},
            'recent_errors': 0
        }
        
        # Calculate total size and component stats
        for log_file in self.log_dir.glob('*.log*'):
            try:
                size = log_file.stat().st_size
                stats['total_size_mb'] += size / (1024*1024)
                
                component = log_file.stem
                if component not in stats['components']:
                    stats['components'][component] = {
                        'files': 0,
                        'size_mb': 0
                    }
                
                stats['components'][component]['files'] += 1
                stats['components'][component]['size_mb'] += size / (1024*1024)
                
            except Exception:
                continue
        
        stats['total_size_mb'] = round(stats['total_size_mb'], 2)
        
        # Count recent errors (last 24 hours)
        try:
            error_log = self.log_dir / 'errors.log'
            if error_log.exists():
                with open(error_log, 'r') as f:
                    lines = f.readlines()
                    # Simple count of recent errors (could be more sophisticated)
                    stats['recent_errors'] = len([l for l in lines[-100:] if 'ERROR' in l])
        except Exception:
            pass
        
        return stats
    
    def cleanup_old_logs(self, days: int = 30) -> Dict:
        """Clean up log files older than specified days"""
        try:
            import time
            cutoff_time = time.time() - (days * 24 * 60 * 60)
            
            cleaned_files = []
            total_size_freed = 0
            
            for log_file in self.log_dir.glob('*.log.*'):  # Only backup files
                try:
                    if log_file.stat().st_mtime < cutoff_time:
                        size = log_file.stat().st_size
                        log_file.unlink()
                        cleaned_files.append(log_file.name)
                        total_size_freed += size
                except Exception:
                    continue
            
            self.get_logger('main').info(
                f"Cleaned up {len(cleaned_files)} old log files, "
                f"freed {total_size_freed / (1024*1024):.2f} MB"
            )
            
            return {
                'success': True,
                'files_cleaned': len(cleaned_files),
                'size_freed_mb': round(total_size_freed / (1024*1024), 2),
                'files': cleaned_files
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}

# Global logger instance
_logger_instance = None

def get_logger_service() -> EmergentTraderLogger:
    """Get global logger service instance"""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = EmergentTraderLogger()
    return _logger_instance

def get_logger(component: str = 'main') -> logging.Logger:
    """Convenience function to get logger for component"""
    return get_logger_service().get_logger(component)

# Convenience functions for different log levels
def log_info(message: str, component: str = 'main'):
    """Log info message"""
    get_logger(component).info(message)

def log_warning(message: str, component: str = 'main'):
    """Log warning message"""
    get_logger(component).warning(message)

def log_error(message: str, component: str = 'main', exc_info: bool = False):
    """Log error message"""
    get_logger(component).error(message, exc_info=exc_info)
    # Also log to errors logger
    get_logger('errors').error(f"[{component}] {message}", exc_info=exc_info)

def log_debug(message: str, component: str = 'main'):
    """Log debug message"""
    get_logger(component).debug(message)

def log_critical(message: str, component: str = 'main'):
    """Log critical message"""
    get_logger(component).critical(message)
    get_logger('errors').critical(f"[{component}] {message}")

# Performance logging decorator
def log_performance(component: str = 'performance'):
    """Decorator to log function performance"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            import time
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                get_logger(component).info(
                    f"{func.__name__} executed in {execution_time:.4f}s"
                )
                
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                get_logger(component).error(
                    f"{func.__name__} failed after {execution_time:.4f}s: {str(e)}"
                )
                raise
                
        return wrapper
    return decorator
