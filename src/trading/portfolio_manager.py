"""
Portfolio Manager - Manages trading portfolio and positions
"""
from typing import Any, Dict, List, Optional
from datetime import datetime
from src.utils.logger import get_logger
from src.utils.config_manager import get_config

logger = get_logger(__name__)


class Position:
    """Represents a trading position"""
    
    def __init__(
        self,
        symbol: str,
        side: str,
        quantity: float,
        entry_price: float,
        timestamp: Optional[datetime] = None
    ):
        self.symbol = symbol
        self.side = side  # 'long' or 'short'
        self.quantity = quantity
        self.entry_price = entry_price
        self.current_price = entry_price
        self.timestamp = timestamp or datetime.now()
        self.realized_pnl = 0.0
        
    def update_price(self, price: float):
        """Update current price"""
        self.current_price = price
    
    def get_unrealized_pnl(self) -> float:
        """Calculate unrealized PnL"""
        if self.side == 'long':
            return (self.current_price - self.entry_price) * self.quantity
        else:  # short
            return (self.entry_price - self.current_price) * self.quantity
    
    def get_value(self) -> float:
        """Get current position value"""
        return self.current_price * self.quantity
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'symbol': self.symbol,
            'side': self.side,
            'quantity': self.quantity,
            'entry_price': self.entry_price,
            'current_price': self.current_price,
            'unrealized_pnl': self.get_unrealized_pnl(),
            'value': self.get_value(),
            'timestamp': self.timestamp.isoformat()
        }


class PortfolioManager:
    """
    Manages trading portfolio, positions, and performance
    """
    
    def __init__(self, initial_capital: Optional[float] = None):
        self.logger = get_logger(__name__)
        
        # Initialize capital
        self.initial_capital = initial_capital or get_config(
            'trading', 'portfolio.initial_capital', 100000.0
        )
        self.cash = self.initial_capital
        
        # Positions
        self.positions: Dict[str, Position] = {}
        
        # Performance tracking
        self.realized_pnl = 0.0
        self.peak_value = self.initial_capital
        self.trades_history: List[Dict[str, Any]] = []
        
        self.logger.info(f"Portfolio Manager initialized with capital: {self.initial_capital}")
    
    def open_position(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float
    ) -> Dict[str, Any]:
        """
        Open a new position
        
        Args:
            symbol: Trading symbol
            side: 'long' or 'short'
            quantity: Position size
            price: Entry price
            
        Returns:
            Operation result
        """
        cost = quantity * price
        
        # Check if enough cash
        if cost > self.cash:
            return {
                'success': False,
                'error': 'Insufficient cash',
                'required': cost,
                'available': self.cash
            }
        
        # Check if position already exists
        if symbol in self.positions:
            return {
                'success': False,
                'error': f'Position already exists for {symbol}'
            }
        
        # Create position
        position = Position(symbol, side, quantity, price)
        self.positions[symbol] = position
        
        # Update cash
        self.cash -= cost
        
        # Record trade
        self.trades_history.append({
            'type': 'open',
            'symbol': symbol,
            'side': side,
            'quantity': quantity,
            'price': price,
            'timestamp': datetime.now().isoformat()
        })
        
        self.logger.info(f"Opened {side} position: {quantity} {symbol} @ {price}")
        
        return {
            'success': True,
            'position': position.to_dict(),
            'remaining_cash': self.cash
        }
    
    def close_position(self, symbol: str, price: float) -> Dict[str, Any]:
        """
        Close an existing position
        
        Args:
            symbol: Trading symbol
            price: Exit price
            
        Returns:
            Operation result
        """
        if symbol not in self.positions:
            return {
                'success': False,
                'error': f'No position found for {symbol}'
            }
        
        position = self.positions[symbol]
        
        # Calculate PnL
        if position.side == 'long':
            pnl = (price - position.entry_price) * position.quantity
        else:  # short
            pnl = (position.entry_price - price) * position.quantity
        
        # Update cash
        proceeds = position.quantity * price
        self.cash += proceeds
        self.realized_pnl += pnl
        
        # Record trade
        self.trades_history.append({
            'type': 'close',
            'symbol': symbol,
            'side': position.side,
            'quantity': position.quantity,
            'entry_price': position.entry_price,
            'exit_price': price,
            'pnl': pnl,
            'timestamp': datetime.now().isoformat()
        })
        
        # Remove position
        del self.positions[symbol]
        
        self.logger.info(f"Closed position: {symbol} @ {price}, PnL: {pnl:.2f}")
        
        return {
            'success': True,
            'pnl': pnl,
            'exit_price': price,
            'remaining_cash': self.cash
        }
    
    def update_position_price(self, symbol: str, price: float):
        """Update position with current market price"""
        if symbol in self.positions:
            self.positions[symbol].update_price(price)
    
    def get_position(self, symbol: str) -> Optional[Position]:
        """Get position by symbol"""
        return self.positions.get(symbol)
    
    def get_all_positions(self) -> List[Position]:
        """Get all open positions"""
        return list(self.positions.values())
    
    def get_total_value(self) -> float:
        """Calculate total portfolio value"""
        positions_value = sum(pos.get_value() for pos in self.positions.values())
        return self.cash + positions_value
    
    def get_unrealized_pnl(self) -> float:
        """Calculate total unrealized PnL"""
        return sum(pos.get_unrealized_pnl() for pos in self.positions.values())
    
    def get_total_pnl(self) -> float:
        """Calculate total PnL (realized + unrealized)"""
        return self.realized_pnl + self.get_unrealized_pnl()
    
    def get_return_pct(self) -> float:
        """Calculate portfolio return percentage"""
        total_value = self.get_total_value()
        return ((total_value - self.initial_capital) / self.initial_capital) * 100
    
    def get_drawdown(self) -> float:
        """Calculate current drawdown"""
        total_value = self.get_total_value()
        self.peak_value = max(self.peak_value, total_value)
        
        if self.peak_value == 0:
            return 0.0
        
        drawdown = (self.peak_value - total_value) / self.peak_value
        return drawdown
    
    def get_portfolio_state(self) -> Dict[str, Any]:
        """Get complete portfolio state"""
        return {
            'total_value': self.get_total_value(),
            'cash': self.cash,
            'positions_value': sum(pos.get_value() for pos in self.positions.values()),
            'num_positions': len(self.positions),
            'unrealized_pnl': self.get_unrealized_pnl(),
            'realized_pnl': self.realized_pnl,
            'total_pnl': self.get_total_pnl(),
            'return_pct': self.get_return_pct(),
            'drawdown': self.get_drawdown(),
            'positions': [pos.to_dict() for pos in self.positions.values()]
        }
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        closed_trades = [t for t in self.trades_history if t['type'] == 'close']
        
        if not closed_trades:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0.0,
                'avg_win': 0.0,
                'avg_loss': 0.0
            }
        
        winning_trades = [t for t in closed_trades if t.get('pnl', 0) > 0]
        losing_trades = [t for t in closed_trades if t.get('pnl', 0) < 0]
        
        avg_win = sum(t['pnl'] for t in winning_trades) / len(winning_trades) if winning_trades else 0
        avg_loss = sum(t['pnl'] for t in losing_trades) / len(losing_trades) if losing_trades else 0
        
        return {
            'total_trades': len(closed_trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': len(winning_trades) / len(closed_trades) if closed_trades else 0,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': abs(avg_win / avg_loss) if avg_loss != 0 else 0
        }


# Global portfolio manager instance
_portfolio_manager = None


def get_portfolio_manager(initial_capital: Optional[float] = None) -> PortfolioManager:
    """Get or create global portfolio manager instance"""
    global _portfolio_manager
    if _portfolio_manager is None:
        _portfolio_manager = PortfolioManager(initial_capital)
    return _portfolio_manager
