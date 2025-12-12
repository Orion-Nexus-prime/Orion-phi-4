"""
Trading Engine - Main engine for executing trades
"""
import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum

from src.utils.logger import get_logger
from src.utils.config_manager import get_config
from src.core.memory_manager import get_memory_manager

logger = get_logger(__name__)


class OrderType(Enum):
    """Order types"""
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"


class OrderSide(Enum):
    """Order sides"""
    BUY = "buy"
    SELL = "sell"


class OrderStatus(Enum):
    """Order status"""
    PENDING = "pending"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class Order:
    """Trading order"""
    
    def __init__(
        self,
        symbol: str,
        side: OrderSide,
        order_type: OrderType,
        quantity: float,
        price: Optional[float] = None,
        stop_price: Optional[float] = None
    ):
        self.order_id = self._generate_order_id()
        self.symbol = symbol
        self.side = side
        self.order_type = order_type
        self.quantity = quantity
        self.price = price
        self.stop_price = stop_price
        self.status = OrderStatus.PENDING
        self.filled_quantity = 0.0
        self.average_price = 0.0
        self.timestamp = datetime.now()
        self.filled_timestamp = None
    
    @staticmethod
    def _generate_order_id() -> str:
        """Generate unique order ID"""
        import uuid
        return f"ORD_{uuid.uuid4().hex[:8].upper()}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert order to dictionary"""
        return {
            'order_id': self.order_id,
            'symbol': self.symbol,
            'side': self.side.value,
            'order_type': self.order_type.value,
            'quantity': self.quantity,
            'price': self.price,
            'stop_price': self.stop_price,
            'status': self.status.value,
            'filled_quantity': self.filled_quantity,
            'average_price': self.average_price,
            'timestamp': self.timestamp.isoformat(),
            'filled_timestamp': self.filled_timestamp.isoformat() if self.filled_timestamp else None
        }


class TradingEngine:
    """
    Main trading engine for order execution
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = get_logger(__name__)
        self.memory = get_memory_manager()
        
        # Configuration
        self.paper_trading = get_config('trading', 'paper_trading.enabled', True)
        self.order_timeout = get_config('trading', 'execution.timeout_seconds', 30)
        self.slippage_tolerance = get_config('trading', 'execution.slippage_tolerance', 0.001)
        
        # State
        self.orders: Dict[str, Order] = {}
        self.running = False
        
        self.logger.info(f"Trading Engine initialized (Paper Trading: {self.paper_trading})")
    
    async def start(self):
        """Start the trading engine"""
        self.running = True
        self.logger.info("Trading Engine started")
    
    async def stop(self):
        """Stop the trading engine"""
        self.running = False
        self.logger.info("Trading Engine stopped")
    
    async def execute_order(self, order: Order) -> Dict[str, Any]:
        """
        Execute a trading order
        
        Args:
            order: Order to execute
            
        Returns:
            Execution result
        """
        if not self.running:
            return {'success': False, 'error': 'Trading engine not running'}
        
        self.logger.info(f"Executing order: {order.order_id} {order.side.value} {order.quantity} {order.symbol}")
        
        # Store order
        self.orders[order.order_id] = order
        
        # Execute based on trading mode
        if self.paper_trading:
            result = await self._execute_paper_order(order)
        else:
            result = await self._execute_live_order(order)
        
        # Store result in memory
        self.memory.store('trading_signals', order.order_id, result)
        
        return result
    
    async def _execute_paper_order(self, order: Order) -> Dict[str, Any]:
        """Execute order in paper trading mode"""
        try:
            # Simulate order execution
            await asyncio.sleep(0.1)  # Simulate network delay
            
            # Simulate fill
            order.status = OrderStatus.FILLED
            order.filled_quantity = order.quantity
            order.filled_timestamp = datetime.now()
            
            # Simulate price with slippage
            if order.price:
                slippage = order.price * self.slippage_tolerance
                if order.side == OrderSide.BUY:
                    order.average_price = order.price + slippage
                else:
                    order.average_price = order.price - slippage
            else:
                # Market order - use simulated current price
                order.average_price = 100.0  # Placeholder
            
            self.logger.info(f"Paper order filled: {order.order_id} at {order.average_price}")
            
            return {
                'success': True,
                'order_id': order.order_id,
                'status': order.status.value,
                'filled_quantity': order.filled_quantity,
                'average_price': order.average_price,
                'mode': 'paper'
            }
            
        except Exception as e:
            order.status = OrderStatus.REJECTED
            self.logger.error(f"Error executing paper order: {e}")
            return {
                'success': False,
                'order_id': order.order_id,
                'error': str(e)
            }
    
    async def _execute_live_order(self, order: Order) -> Dict[str, Any]:
        """Execute order in live trading mode"""
        # WARNING: Live trading is not implemented
        # This is a placeholder that should be implemented with actual exchange API
        
        self.logger.warning("Live trading not implemented - use paper trading mode")
        order.status = OrderStatus.REJECTED
        
        return {
            'success': False,
            'order_id': order.order_id,
            'error': 'Live trading not implemented'
        }
    
    async def create_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        order_type: str = "market",
        price: Optional[float] = None,
        stop_price: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Create and execute a new order
        
        Args:
            symbol: Trading symbol
            side: 'buy' or 'sell'
            quantity: Order quantity
            order_type: Order type ('market', 'limit', etc.)
            price: Limit price (for limit orders)
            stop_price: Stop price (for stop orders)
            
        Returns:
            Execution result
        """
        try:
            # Convert strings to enums
            order_side = OrderSide.BUY if side.lower() == 'buy' else OrderSide.SELL
            order_type_enum = OrderType[order_type.upper()]
            
            # Create order
            order = Order(
                symbol=symbol,
                side=order_side,
                order_type=order_type_enum,
                quantity=quantity,
                price=price,
                stop_price=stop_price
            )
            
            # Execute order
            return await self.execute_order(order)
            
        except Exception as e:
            self.logger.error(f"Error creating order: {e}")
            return {'success': False, 'error': str(e)}
    
    async def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """
        Cancel an order
        
        Args:
            order_id: Order ID to cancel
            
        Returns:
            Cancellation result
        """
        if order_id not in self.orders:
            return {'success': False, 'error': 'Order not found'}
        
        order = self.orders[order_id]
        
        if order.status in [OrderStatus.FILLED, OrderStatus.CANCELLED]:
            return {'success': False, 'error': f'Cannot cancel order with status {order.status.value}'}
        
        order.status = OrderStatus.CANCELLED
        self.logger.info(f"Order cancelled: {order_id}")
        
        return {
            'success': True,
            'order_id': order_id,
            'status': OrderStatus.CANCELLED.value
        }
    
    def get_order(self, order_id: str) -> Optional[Order]:
        """Get order by ID"""
        return self.orders.get(order_id)
    
    def get_all_orders(self) -> List[Order]:
        """Get all orders"""
        return list(self.orders.values())
    
    def get_open_orders(self) -> List[Order]:
        """Get all open orders"""
        return [
            order for order in self.orders.values()
            if order.status in [OrderStatus.PENDING, OrderStatus.PARTIALLY_FILLED]
        ]
    
    def get_filled_orders(self) -> List[Order]:
        """Get all filled orders"""
        return [
            order for order in self.orders.values()
            if order.status == OrderStatus.FILLED
        ]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get trading statistics"""
        all_orders = self.get_all_orders()
        
        return {
            'total_orders': len(all_orders),
            'open_orders': len(self.get_open_orders()),
            'filled_orders': len(self.get_filled_orders()),
            'cancelled_orders': len([o for o in all_orders if o.status == OrderStatus.CANCELLED]),
            'rejected_orders': len([o for o in all_orders if o.status == OrderStatus.REJECTED]),
            'paper_trading': self.paper_trading
        }


# Global trading engine instance
_trading_engine = None


def get_trading_engine(config: Optional[Dict[str, Any]] = None) -> TradingEngine:
    """Get or create global trading engine instance"""
    global _trading_engine
    if _trading_engine is None:
        _trading_engine = TradingEngine(config)
    return _trading_engine
