# 📊 EmergentTrader Logging System Guide

## 🎯 Overview

The EmergentTrader platform includes a comprehensive logging system that provides detailed insights into system operations, trading activities, and performance metrics. This guide covers how to view logs, configure log levels, and troubleshoot issues.

## 📁 Log File Locations

All log files are stored in the `python_backend/logs/` directory:

```
python_backend/logs/
├── emergent_trader.log      # Main application logs
├── signals.log              # Trading signal generation logs
├── portfolio.log            # Portfolio operations logs
├── api.log                  # API request/response logs
├── notifications.log        # Notification system logs
├── errors.log              # All errors from all components
├── performance.log         # Performance metrics and timing
└── logging_config.json     # Logging configuration
```

## 🔍 Log Levels

The system supports 5 log levels in order of verbosity:

| Level | Description | When to Use |
|-------|-------------|-------------|
| **DEBUG** | Detailed diagnostic information | Development and troubleshooting |
| **INFO** | General information about system operation | Normal monitoring |
| **WARNING** | Warning messages for potential issues | Default production level |
| **ERROR** | Error messages for failures | Critical issue tracking |
| **CRITICAL** | Critical errors that may stop the system | Emergency situations |

## 🎛️ Changing Log Levels

### Method 1: Via Web Dashboard

1. Open the Enhanced Dashboard
2. Navigate to the "Logging Control Panel" section
3. Click on the desired log level button (DEBUG, INFO, WARNING, ERROR)
4. The change takes effect immediately

### Method 2: Via API

```bash
# Set log level to DEBUG
curl -X POST http://localhost:8000/logging/level \
  -H "Content-Type: application/json" \
  -d '{"level": "DEBUG"}'

# Set log level to INFO
curl -X POST http://localhost:8000/logging/level \
  -H "Content-Type: application/json" \
  -d '{"level": "INFO"}'
```

### Method 3: Via Python Code

```python
from services.logging_service import get_logger_service

logger_service = get_logger_service()
result = logger_service.set_log_level('DEBUG')
print(result)
```

## 👀 Viewing Logs

### Method 1: Web Dashboard

1. Open the Enhanced Dashboard
2. In the "Logging Control Panel", click "View Logs"
3. Recent logs will be displayed in a terminal-style interface

### Method 2: API Endpoints

```bash
# Get recent logs from main component (last 100 lines)
curl http://localhost:8000/logging/recent/main?lines=100

# Get recent logs from signals component
curl http://localhost:8000/logging/recent/signals?lines=50

# Get recent logs from portfolio component
curl http://localhost:8000/logging/recent/portfolio?lines=50
```

### Method 3: Direct File Access

```bash
# View main application logs
tail -f python_backend/logs/emergent_trader.log

# View signal generation logs
tail -f python_backend/logs/signals.log

# View error logs only
tail -f python_backend/logs/errors.log

# View last 100 lines of portfolio logs
tail -100 python_backend/logs/portfolio.log
```

### Method 4: Search Logs

```bash
# Search for specific patterns across all logs
curl -X POST http://localhost:8000/logging/search \
  -H "Content-Type: application/json" \
  -d '{"query": "error", "days": 7}'

# Search in specific component
curl -X POST http://localhost:8000/logging/search \
  -H "Content-Type: application/json" \
  -d '{"query": "signal generated", "component": "signals"}'
```

## 📈 Log Analysis and Monitoring

### Getting Log Statistics

```bash
# Get comprehensive logging statistics
curl http://localhost:8000/logging/stats
```

This returns:
- Current log level
- Total log files and sizes
- Component-wise statistics
- Recent error counts

### Available Log Files

```bash
# List all available log files
curl http://localhost:8000/logging/files
```

Returns information about:
- File names and paths
- File sizes
- Last modified timestamps
- Associated components

## 🧹 Log Maintenance

### Automatic Log Rotation

The system automatically rotates log files when they exceed 10MB:
- Keeps 5 backup files per component
- Old files are compressed and archived
- Format: `component.log.1`, `component.log.2`, etc.

### Manual Log Cleanup

```bash
# Clean up log files older than 30 days
curl -X POST http://localhost:8000/logging/cleanup \
  -H "Content-Type: application/json" \
  -d '{"days": 30}'

# Clean up log files older than 7 days
curl -X POST http://localhost:8000/logging/cleanup \
  -H "Content-Type: application/json" \
  -d '{"days": 7}'
```

## 🔧 Component-Specific Logging

### Trading Signals (`signals.log`)

**What's logged:**
- Signal generation requests
- Strategy execution details
- Confidence calculations
- Market regime analysis
- Signal filtering results

**Example entries:**
```
2024-01-15 09:30:15 - SIGNAL - INFO - Starting signal generation with strategy: multibagger
2024-01-15 09:30:18 - SIGNAL - INFO - Successfully generated 15 signals
2024-01-15 09:30:18 - SIGNAL - DEBUG - Signal for RELIANCE: confidence=0.94, entry=2450.0
```

### Portfolio Operations (`portfolio.log`)

**What's logged:**
- Position additions and modifications
- Portfolio value calculations
- Risk management decisions
- Position sizing calculations

**Example entries:**
```
2024-01-15 10:15:22 - PORTFOLIO - INFO - Position added for RELIANCE: 100 shares at ₹2450
2024-01-15 10:15:22 - PORTFOLIO - DEBUG - Portfolio value updated: ₹1,245,000
2024-01-15 10:15:23 - PORTFOLIO - INFO - Position size calculated: 100 shares (2.1% risk)
```

### API Requests (`api.log`)

**What's logged:**
- HTTP requests and responses
- API endpoint usage
- Request processing times
- Authentication events

### Notifications (`notifications.log`)

**What's logged:**
- Notification sending attempts
- Email and Telegram delivery status
- Notification preferences changes
- Delivery failures and retries

### Performance (`performance.log`)

**What's logged:**
- Function execution times
- Database query performance
- API response times
- System resource usage

## 🚨 Troubleshooting Common Issues

### Issue: No logs appearing

**Possible causes:**
1. Log level set too high (e.g., ERROR when you need INFO)
2. Log files not being created due to permissions
3. Logging service not initialized

**Solutions:**
```bash
# Check current log level
curl http://localhost:8000/logging/status

# Set to DEBUG for maximum verbosity
curl -X POST http://localhost:8000/logging/level -d '{"level": "DEBUG"}'

# Check log directory permissions
ls -la python_backend/logs/
```

### Issue: Log files growing too large

**Solutions:**
```bash
# Clean up old logs
curl -X POST http://localhost:8000/logging/cleanup -d '{"days": 7}'

# Check current log sizes
curl http://localhost:8000/logging/stats
```

### Issue: Cannot find specific error

**Solutions:**
```bash
# Search across all logs
curl -X POST http://localhost:8000/logging/search -d '{"query": "your_error_message"}'

# Check errors.log specifically
tail -100 python_backend/logs/errors.log | grep "your_error"
```

### Issue: Performance problems

**Check performance logs:**
```bash
# View performance logs
tail -50 python_backend/logs/performance.log

# Look for slow operations
grep "executed in" python_backend/logs/performance.log | sort -k4 -n
```

## 📋 Log Format Reference

### Standard Log Format
```
TIMESTAMP - COMPONENT - LEVEL - MESSAGE
```

### Example Formats by Component

**Main Application:**
```
2024-01-15 09:30:15 - emergent_trader.main - INFO - Application started successfully
```

**Signals:**
```
2024-01-15 09:30:15 - SIGNAL - INFO - Signal generation completed: 15 signals
```

**Portfolio:**
```
2024-01-15 09:30:15 - PORTFOLIO - INFO - Position added: RELIANCE 100 shares
```

**API:**
```
2024-01-15 09:30:15 - API - INFO - POST /signals/generate - 200 - 1.234s
```

**Errors:**
```
2024-01-15 09:30:15 - ERROR - signals - ERROR - Signal generation failed: Invalid symbol
```

## 🔄 Integration with Code

### Adding Logging to Your Code

```python
from services.logging_service import get_logger, log_info, log_error, log_performance

# Get component-specific logger
logger = get_logger('signals')

# Log different levels
log_info("Signal generation started", "signals")
log_error("Signal generation failed", "signals", exc_info=True)

# Performance logging decorator
@log_performance('signals')
def generate_signals():
    # Your code here
    pass
```

### Custom Log Messages

```python
# Structured logging
logger.info(f"Generated {count} signals for {strategy} strategy")

# Error logging with context
logger.error(f"Failed to process {symbol}: {error}", exc_info=True)

# Debug logging
logger.debug(f"Processing signal: {signal_data}")
```

## 📊 Monitoring Best Practices

### Development Environment
- Use **DEBUG** level for detailed troubleshooting
- Monitor `errors.log` for any issues
- Check `performance.log` for optimization opportunities

### Production Environment
- Use **INFO** or **WARNING** level for normal operation
- Set up log monitoring alerts for ERROR level messages
- Regularly clean up old log files
- Monitor log file sizes and disk usage

### Performance Monitoring
- Check `performance.log` for slow operations
- Monitor API response times in `api.log`
- Track signal generation times in `signals.log`

## 🎯 Quick Reference Commands

```bash
# View current logging status
curl http://localhost:8000/logging/status

# Change log level to DEBUG
curl -X POST http://localhost:8000/logging/level -d '{"level": "DEBUG"}'

# View recent main logs
curl http://localhost:8000/logging/recent/main?lines=50

# Search for errors in last 24 hours
curl -X POST http://localhost:8000/logging/search -d '{"query": "ERROR", "days": 1}'

# Get logging statistics
curl http://localhost:8000/logging/stats

# Clean up logs older than 30 days
curl -X POST http://localhost:8000/logging/cleanup -d '{"days": 30}'

# View live logs (terminal)
tail -f python_backend/logs/emergent_trader.log
```

## 🆘 Support and Troubleshooting

If you encounter issues with the logging system:

1. **Check log level**: Ensure it's set appropriately for your needs
2. **Verify permissions**: Make sure the application can write to the logs directory
3. **Check disk space**: Ensure sufficient disk space for log files
4. **Review configuration**: Check `logging_config.json` for any issues
5. **Restart application**: Sometimes a restart resolves logging issues

For additional support, check the error logs and search for specific error messages using the search functionality.
