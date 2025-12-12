"""
Market Feeds - Real-time market data management
"""
import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional
import numpy as np

from src.utils.logger import get_logger
from src.utils.config_manager import get_config
from src.data.quantum_cache import get_quantum_cache

logger = get_logger(__name__)


class MarketData:
    """Container for market data"""
    
    def __init__(
        self,
        symbol: str,
        timestamp: datetime,
        open: float,
        high: float,
        low: float,
        close: float,
        volume: float
    ):
        self.symbol = symbol
        self.timestamp = timestamp
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'symbol': self.symbol,
            'timestamp': self.timestamp.isoformat(),
            'open': self.open,
            'high': self.high,
            'low': self.low,
            'close': self.close,
            'volume': self.volume
        }


class MarketFeed:
    """
    Market data feed manager
    Simulates real-time market data (placeholder for actual exchange connections)
    """
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.cache = get_quantum_cache()
        
        # Configuration
        self.symbols = get_config('trading', 'market_data.symbols', ['BTC/USDT'])
        self.update_interval = get_config('trading', 'market_data.update_interval_seconds', 5)
        
        # State
        self.running = False
        self._feed_task = None
        self._subscribers: Dict[str, List[asyncio.Queue]] = {}
        
        self.logger.info(f"Market Feed initialized for symbols: {self.symbols}")
    
    async def start(self):
        """Start the market data feed"""
        self.running = True
        self._feed_task = asyncio.create_task(self._feed_loop())
        self.logger.info("Market Feed started")
    
    async def stop(self):
        """Stop the market data feed"""
        self.running = False
        if self._feed_task:
            self._feed_task.cancel()
            try:
                await self._feed_task
            except asyncio.CancelledError:
                pass
        self.logger.info("Market Feed stopped")
    
    async def _feed_loop(self):
        """Main feed loop for generating market data"""
        while self.running:
            try:
                for symbol in self.symbols:
                    # Generate simulated market data
                    data = self._generate_market_data(symbol)
                    
                    # Cache the data
                    cache_key = f"market_data:{symbol}"
                    await self.cache.set(cache_key, data)
                    
                    # Notify subscribers
                    await self._notify_subscribers(symbol, data)
                
                await asyncio.sleep(self.update_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in feed loop: {e}")
                await asyncio.sleep(1)
    
    def _generate_market_data(self, symbol: str) -> MarketData:
        """
        Generate simulated market data
        In production, this would fetch from real exchange
        """
        # Get previous close or start at base price
        cache_key = f"market_data:{symbol}"
        
        # Simulate price movement
        base_price = 50000.0 if 'BTC' in symbol else 3000.0 if 'ETH' in symbol else 100.0
        
        # Random walk for simulation
        change_pct = np.random.normal(0, 0.01)  # 1% std dev
        close = base_price * (1 + change_pct)
        
        # Generate OHLC
        high = close * (1 + abs(np.random.normal(0, 0.005)))
        low = close * (1 - abs(np.random.normal(0, 0.005)))
        open_price = base_price
        
        volume = np.random.uniform(100, 1000)
        
        return MarketData(
            symbol=symbol,
            timestamp=datetime.now(),
            open=open_price,
            high=high,
            low=low,
            close=close,
            volume=volume
        )
    
    async def get_latest(self, symbol: str) -> Optional[MarketData]:
        """
        Get latest market data for symbol
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Latest market data or None
        """
        cache_key = f"market_data:{symbol}"
        data = await self.cache.get(cache_key)
        
        if data is None:
            # Generate on-demand if not in cache
            data = self._generate_market_data(symbol)
            await self.cache.set(cache_key, data)
        
        return data
    
    async def get_historical(
        self,
        symbol: str,
        periods: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get historical market data
        
        Args:
            symbol: Trading symbol
            periods: Number of periods to retrieve
            
        Returns:
            List of historical data points
        """
        # In production, this would query a database or API
        # For now, generate simulated historical data
        
        historical = []
        base_price = 50000.0 if 'BTC' in symbol else 3000.0 if 'ETH' in symbol else 100.0
        price = base_price
        
        for i in range(periods):
            change_pct = np.random.normal(0, 0.01)
            price = price * (1 + change_pct)
            
            high = price * (1 + abs(np.random.normal(0, 0.005)))
            low = price * (1 - abs(np.random.normal(0, 0.005)))
            open_price = historical[-1]['close'] if historical else base_price
            
            data = {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'open': open_price,
                'high': high,
                'low': low,
                'close': price,
                'volume': np.random.uniform(100, 1000)
            }
            
            historical.append(data)
        
        return historical
    
    async def subscribe(self, symbol: str) -> asyncio.Queue:
        """
        Subscribe to market data updates
        
        Args:
            symbol: Symbol to subscribe to
            
        Returns:
            Queue that will receive updates
        """
        if symbol not in self._subscribers:
            self._subscribers[symbol] = []
        
        queue = asyncio.Queue()
        self._subscribers[symbol].append(queue)
        
        self.logger.info(f"New subscriber for {symbol}")
        return queue
    
    async def unsubscribe(self, symbol: str, queue: asyncio.Queue):
        """Unsubscribe from market data updates"""
        if symbol in self._subscribers:
            try:
                self._subscribers[symbol].remove(queue)
                self.logger.info(f"Unsubscribed from {symbol}")
            except ValueError:
                pass
    
    async def _notify_subscribers(self, symbol: str, data: MarketData):
        """Notify all subscribers of new data"""
        if symbol in self._subscribers:
            for queue in self._subscribers[symbol]:
                try:
                    await queue.put(data)
                except Exception as e:
                    self.logger.error(f"Error notifying subscriber: {e}")
    
    def get_symbols(self) -> List[str]:
        """Get list of available symbols"""
        return self.symbols.copy()
    
    async def add_symbol(self, symbol: str):
        """Add a new symbol to track"""
        if symbol not in self.symbols:
            self.symbols.append(symbol)
            self.logger.info(f"Added symbol: {symbol}")
    
    async def remove_symbol(self, symbol: str):
        """Remove a symbol from tracking"""
        if symbol in self.symbols:
            self.symbols.remove(symbol)
            self.logger.info(f"Removed symbol: {symbol}")


# Global market feed instance
_market_feed = None


def get_market_feed() -> MarketFeed:
    """Get or create global market feed instance"""
    global _market_feed
    if _market_feed is None:
        _market_feed = MarketFeed()
    return _market_feed
