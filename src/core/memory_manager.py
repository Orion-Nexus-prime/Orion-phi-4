"""
Quantum Memory Manager - High-performance memory management for trading system
"""
import asyncio
from collections import deque
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from src.utils.logger import get_logger
from src.utils.config_manager import get_config

logger = get_logger(__name__)


class QuantumMemory:
    """
    Quantum-inspired memory system for caching and historical data
    Uses circular buffers and efficient lookup structures
    """
    
    def __init__(self, max_size: int = 10000):
        self.max_size = max_size
        self.memory: deque = deque(maxlen=max_size)
        self.index: Dict[str, Any] = {}
        self.logger = get_logger(__name__)
        
    def store(self, key: str, value: Any, timestamp: Optional[datetime] = None):
        """Store a value with key and timestamp"""
        if timestamp is None:
            timestamp = datetime.now()
        
        entry = {
            'key': key,
            'value': value,
            'timestamp': timestamp
        }
        
        self.memory.append(entry)
        self.index[key] = entry
        
    def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve the most recent value for a key"""
        entry = self.index.get(key)
        return entry['value'] if entry else None
    
    def retrieve_historical(
        self, 
        key: str, 
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Any]:
        """Retrieve historical values for a key within time range"""
        results = []
        
        for entry in self.memory:
            if entry['key'] == key:
                ts = entry['timestamp']
                
                if start_time and ts < start_time:
                    continue
                if end_time and ts > end_time:
                    continue
                
                results.append(entry['value'])
        
        return results
    
    def clear(self):
        """Clear all memory"""
        self.memory.clear()
        self.index.clear()
        
    def size(self) -> int:
        """Get current memory size"""
        return len(self.memory)


class MemoryManager:
    """
    Main memory manager for the trading system
    Manages multiple memory channels and cleanup
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = get_logger(__name__)
        
        # Get configuration
        self.max_history = get_config('system', 'memory.max_history_items', 10000)
        self.cleanup_interval = get_config('system', 'memory.cleanup_interval_seconds', 300)
        
        # Initialize memory channels
        self.channels: Dict[str, QuantumMemory] = {
            'market_data': QuantumMemory(self.max_history),
            'agent_results': QuantumMemory(self.max_history),
            'trading_signals': QuantumMemory(self.max_history),
            'portfolio_state': QuantumMemory(1000),
            'system_events': QuantumMemory(5000)
        }
        
        self._cleanup_task = None
        self._running = False
        
        self.logger.info("Memory Manager initialized")
    
    async def start(self):
        """Start the memory manager and cleanup task"""
        self._running = True
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        self.logger.info("Memory Manager started")
    
    async def stop(self):
        """Stop the memory manager"""
        self._running = False
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        self.logger.info("Memory Manager stopped")
    
    def store(self, channel: str, key: str, value: Any, timestamp: Optional[datetime] = None):
        """
        Store data in a specific channel
        
        Args:
            channel: Memory channel name
            key: Storage key
            value: Value to store
            timestamp: Optional timestamp
        """
        if channel not in self.channels:
            self.logger.warning(f"Unknown channel: {channel}, creating new channel")
            self.channels[channel] = QuantumMemory(self.max_history)
        
        self.channels[channel].store(key, value, timestamp)
    
    def retrieve(self, channel: str, key: str) -> Optional[Any]:
        """
        Retrieve data from a specific channel
        
        Args:
            channel: Memory channel name
            key: Storage key
            
        Returns:
            Retrieved value or None
        """
        if channel not in self.channels:
            return None
        
        return self.channels[channel].retrieve(key)
    
    def retrieve_historical(
        self,
        channel: str,
        key: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Any]:
        """
        Retrieve historical data from a channel
        
        Args:
            channel: Memory channel name
            key: Storage key
            start_time: Start of time range
            end_time: End of time range
            
        Returns:
            List of historical values
        """
        if channel not in self.channels:
            return []
        
        return self.channels[channel].retrieve_historical(key, start_time, end_time)
    
    def get_recent(self, channel: str, key: str, count: int = 10) -> List[Any]:
        """
        Get most recent N items for a key
        
        Args:
            channel: Memory channel name
            key: Storage key
            count: Number of recent items to retrieve
            
        Returns:
            List of recent values
        """
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=24)  # Last 24 hours
        
        historical = self.retrieve_historical(channel, key, start_time, end_time)
        return historical[-count:] if len(historical) > count else historical
    
    def clear_channel(self, channel: str):
        """Clear all data in a channel"""
        if channel in self.channels:
            self.channels[channel].clear()
            self.logger.info(f"Cleared channel: {channel}")
    
    def clear_all(self):
        """Clear all memory channels"""
        for channel in self.channels.values():
            channel.clear()
        self.logger.info("Cleared all memory channels")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        stats = {
            'channels': {},
            'total_items': 0
        }
        
        for channel_name, channel in self.channels.items():
            size = channel.size()
            stats['channels'][channel_name] = {
                'size': size,
                'max_size': channel.max_size,
                'usage_pct': (size / channel.max_size * 100) if channel.max_size > 0 else 0
            }
            stats['total_items'] += size
        
        return stats
    
    async def _cleanup_loop(self):
        """Background task for periodic memory cleanup"""
        while self._running:
            try:
                await asyncio.sleep(self.cleanup_interval)
                self._perform_cleanup()
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in cleanup loop: {e}")
    
    def _perform_cleanup(self):
        """Perform memory cleanup"""
        # Memory cleanup is automatic with deque maxlen
        # This method can be extended for more sophisticated cleanup
        
        stats = self.get_stats()
        self.logger.debug(f"Memory stats: {stats['total_items']} total items")
        
        # Log warnings for high memory usage
        for channel_name, channel_stats in stats['channels'].items():
            if channel_stats['usage_pct'] > 90:
                self.logger.warning(
                    f"High memory usage in channel {channel_name}: "
                    f"{channel_stats['usage_pct']:.1f}%"
                )


# Global memory manager instance
_memory_manager = None


def get_memory_manager(config: Optional[Dict[str, Any]] = None) -> MemoryManager:
    """Get or create global memory manager instance"""
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = MemoryManager(config)
    return _memory_manager
