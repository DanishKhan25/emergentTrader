"""
Signal Engine - Enhanced multi-strategy consensus signal generation system
Integrates all 10 trading strategies with consensus engine for high-quality signals
"""

import sys
import os
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

# Add the python_backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import the enhanced signal engine with consensus capabilities
from core.enhanced_signal_engine import EnhancedSignalEngine

logger = logging.getLogger(__name__)

class SignalEngine(EnhancedSignalEngine):
    """
    Main Signal Engine - Now inherits from EnhancedSignalEngine
    Provides backward compatibility while adding consensus capabilities
    """
    
    def __init__(self):
        """Initialize signal engine with enhanced consensus capabilities"""
        super().__init__()
        logger.info("Signal Engine initialized with enhanced consensus capabilities")
    
    # Maintain backward compatibility for existing API calls
    def generate_signals_legacy(self, symbols: Optional[List[str]] = None, 
                               strategy_name: str = 'momentum', 
                               shariah_only: bool = True, 
                               min_confidence: float = 0.6) -> List[Dict]:
        """
        Legacy signal generation method for backward compatibility
        Now defaults to consensus signals for better quality
        """
        # Default to consensus signals for best results
        if strategy_name == 'momentum':
            logger.info("Upgrading momentum strategy request to consensus signals")
            return self.generate_consensus_signals(
                symbols=symbols,
                shariah_only=shariah_only,
                max_symbols=50
            )
        
        # Use parent class method for specific strategy requests
        return super().generate_signals(symbols, strategy_name, shariah_only, min_confidence)

# For backward compatibility, create an alias
SignalEngineV1 = SignalEngine

# Example usage and testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Initialize signal engine
    engine = SignalEngine()
    
    # Test consensus signal generation
    print("Testing enhanced signal engine with consensus...")
    signals = engine.generate_signals(strategy_name='consensus', shariah_only=True)
    print(f"Generated {len(signals)} consensus signals")
    
    # Get system status
    status = engine.get_system_status()
    print(f"System status: {status}")
    
    # Get consensus summary
    summary = engine.get_consensus_summary()
    print(f"Consensus summary: {summary}")
