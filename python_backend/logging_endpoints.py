"""
Logging API Endpoints for EmergentTrader
Add these endpoints to your main.py
"""

from fastapi import HTTPException
from services.logging_service import get_logger_service, get_logger

# Add these endpoints to your main.py:

@app.get("/logging/status")
async def get_logging_status():
    """Get current logging status and configuration"""
    try:
        logger_service = get_logger_service()
        
        return {
            'success': True,
            'data': {
                'current_level': logger_service.get_log_level(),
                'available_levels': list(logger_service.log_levels.keys()),
                'log_directory': str(logger_service.log_dir),
                'stats': logger_service.get_log_stats()
            }
        }
    except Exception as e:
        logger = get_logger('api')
        logger.error(f"Error getting logging status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/logging/level")
async def set_log_level(request: dict):
    """Set logging level dynamically"""
    try:
        level = request.get('level', 'INFO')
        logger_service = get_logger_service()
        
        result = logger_service.set_log_level(level)
        
        if result['success']:
            return result
        else:
            raise HTTPException(status_code=400, detail=result['error'])
            
    except HTTPException:
        raise
    except Exception as e:
        logger = get_logger('api')
        logger.error(f"Error setting log level: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/logging/files")
async def get_log_files():
    """Get list of available log files"""
    try:
        logger_service = get_logger_service()
        
        return {
            'success': True,
            'data': logger_service.get_log_files()
        }
    except Exception as e:
        logger = get_logger('api')
        logger.error(f"Error getting log files: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/logging/recent/{component}")
async def get_recent_logs(component: str, lines: int = 100):
    """Get recent log entries from specific component"""
    try:
        logger_service = get_logger_service()
        
        return {
            'success': True,
            'data': {
                'component': component,
                'lines': lines,
                'logs': logger_service.get_recent_logs(component, lines)
            }
        }
    except Exception as e:
        logger = get_logger('api')
        logger.error(f"Error getting recent logs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/logging/search")
async def search_logs(request: dict):
    """Search logs for specific patterns"""
    try:
        query = request.get('query', '')
        component = request.get('component')
        days = request.get('days', 7)
        
        if not query:
            raise HTTPException(status_code=400, detail="Query parameter is required")
        
        logger_service = get_logger_service()
        results = logger_service.search_logs(query, component, days)
        
        return {
            'success': True,
            'data': {
                'query': query,
                'component': component,
                'results_count': len(results),
                'results': results
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger = get_logger('api')
        logger.error(f"Error searching logs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/logging/cleanup")
async def cleanup_old_logs(request: dict):
    """Clean up old log files"""
    try:
        days = request.get('days', 30)
        logger_service = get_logger_service()
        
        result = logger_service.cleanup_old_logs(days)
        
        return result
    except Exception as e:
        logger = get_logger('api')
        logger.error(f"Error cleaning up logs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/logging/stats")
async def get_logging_stats():
    """Get detailed logging statistics"""
    try:
        logger_service = get_logger_service()
        
        return {
            'success': True,
            'data': logger_service.get_log_stats()
        }
    except Exception as e:
        logger = get_logger('api')
        logger.error(f"Error getting logging stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Add this to integrate logging into your existing API handler
def integrate_logging_into_api_handler():
    """
    Add this code to your existing api_handler.py to integrate logging
    """
    
    # At the top of api_handler.py, add:
    """
    from services.logging_service import get_logger, log_info, log_warning, log_error, log_debug, log_performance
    """
    
    # Replace existing logging calls with:
    """
    # Instead of: print("Signal generated")
    log_info("Signal generated successfully", "signals")
    
    # Instead of: print(f"Error: {e}")
    log_error(f"Signal generation failed: {e}", "signals", exc_info=True)
    
    # For performance monitoring:
    @log_performance("signals")
    def generate_signals(self, ...):
        # Your existing code
    """
    
    # Example integration in generate_signals method:
    """
    def generate_signals(self, strategy='momentum', symbols=None):
        logger = get_logger('signals')
        logger.info(f"Starting signal generation with strategy: {strategy}")
        
        try:
            # Your existing signal generation code
            result = self.signal_engine.generate_signals(...)
            
            if result.get('success'):
                signal_count = len(result.get('data', []))
                logger.info(f"Successfully generated {signal_count} signals")
            else:
                logger.warning(f"Signal generation returned no results")
            
            return result
            
        except Exception as e:
            logger.error(f"Signal generation failed: {str(e)}", exc_info=True)
            return {'success': False, 'error': str(e)}
    """
