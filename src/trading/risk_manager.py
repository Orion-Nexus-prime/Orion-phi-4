"""
Risk Manager - Portfolio risk management
"""
from typing import Any, Dict, Optional
from src.utils.logger import get_logger
from src.utils.config_manager import get_config

logger = get_logger(__name__)


class RiskManager:
    """
    Manages trading risk and position sizing
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = get_logger(__name__)
        
        # Load risk parameters
        self.max_portfolio_risk = get_config('trading', 'risk.max_portfolio_risk', 0.02)
        self.max_position_risk = get_config('trading', 'risk.max_position_risk', 0.01)
        self.max_drawdown = get_config('trading', 'risk.max_drawdown', 0.15)
        self.stop_loss_pct = get_config('trading', 'risk.stop_loss_pct', 0.05)
        self.take_profit_pct = get_config('trading', 'risk.take_profit_pct', 0.10)
        self.max_leverage = get_config('trading', 'risk.max_leverage', 2.0)
        self.max_concentration = get_config('trading', 'risk.max_concentration', 0.20)
        
        self.logger.info("Risk Manager initialized")
    
    def calculate_position_size(
        self,
        capital: float,
        entry_price: float,
        stop_loss_price: float,
        risk_per_trade: Optional[float] = None
    ) -> float:
        """
        Calculate position size based on risk
        
        Args:
            capital: Available capital
            entry_price: Entry price
            stop_loss_price: Stop loss price
            risk_per_trade: Risk amount (optional, uses max_position_risk if not provided)
            
        Returns:
            Position size in units
        """
        if risk_per_trade is None:
            risk_per_trade = capital * self.max_position_risk
        
        # Calculate risk per unit
        risk_per_unit = abs(entry_price - stop_loss_price)
        
        if risk_per_unit == 0:
            self.logger.warning("Zero risk per unit, using minimum position size")
            return 0.0
        
        # Position size = Risk amount / Risk per unit
        position_size = risk_per_trade / risk_per_unit
        
        return position_size
    
    def check_position_risk(
        self,
        position_value: float,
        portfolio_value: float,
        current_drawdown: float = 0.0
    ) -> Dict[str, Any]:
        """
        Check if position meets risk requirements
        
        Args:
            position_value: Value of proposed position
            portfolio_value: Total portfolio value
            current_drawdown: Current portfolio drawdown
            
        Returns:
            Risk check result
        """
        # Check concentration
        concentration = position_value / portfolio_value if portfolio_value > 0 else 1.0
        concentration_ok = concentration <= self.max_concentration
        
        # Check drawdown
        drawdown_ok = current_drawdown <= self.max_drawdown
        
        # Overall approval
        approved = concentration_ok and drawdown_ok
        
        result = {
            'approved': approved,
            'concentration': concentration,
            'max_concentration': self.max_concentration,
            'concentration_ok': concentration_ok,
            'current_drawdown': current_drawdown,
            'max_drawdown': self.max_drawdown,
            'drawdown_ok': drawdown_ok
        }
        
        if not approved:
            reasons = []
            if not concentration_ok:
                reasons.append(f"Position concentration {concentration:.2%} exceeds max {self.max_concentration:.2%}")
            if not drawdown_ok:
                reasons.append(f"Drawdown {current_drawdown:.2%} exceeds max {self.max_drawdown:.2%}")
            result['rejection_reasons'] = reasons
        
        return result
    
    def calculate_stop_loss(self, entry_price: float, side: str) -> float:
        """
        Calculate stop loss price
        
        Args:
            entry_price: Entry price
            side: 'buy' or 'sell'
            
        Returns:
            Stop loss price
        """
        if side.lower() == 'buy':
            return entry_price * (1 - self.stop_loss_pct)
        else:
            return entry_price * (1 + self.stop_loss_pct)
    
    def calculate_take_profit(self, entry_price: float, side: str) -> float:
        """
        Calculate take profit price
        
        Args:
            entry_price: Entry price
            side: 'buy' or 'sell'
            
        Returns:
            Take profit price
        """
        if side.lower() == 'buy':
            return entry_price * (1 + self.take_profit_pct)
        else:
            return entry_price * (1 - self.take_profit_pct)
    
    def assess_trade_risk(
        self,
        signal: Dict[str, Any],
        portfolio_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Comprehensive trade risk assessment
        
        Args:
            signal: Trading signal with entry, stop loss, etc.
            portfolio_state: Current portfolio state
            
        Returns:
            Risk assessment result
        """
        entry_price = signal.get('entry_price', 0)
        stop_loss = signal.get('stop_loss', entry_price * 0.95)
        position_size = signal.get('position_size', 0)
        side = signal.get('side', 'buy')
        
        portfolio_value = portfolio_state.get('total_value', 100000)
        current_drawdown = portfolio_state.get('drawdown', 0.0)
        
        # Calculate position value
        position_value = position_size * entry_price
        
        # Check position risk
        risk_check = self.check_position_risk(
            position_value,
            portfolio_value,
            current_drawdown
        )
        
        # Calculate risk-reward ratio
        take_profit = self.calculate_take_profit(entry_price, side)
        risk = abs(entry_price - stop_loss)
        reward = abs(take_profit - entry_price)
        risk_reward_ratio = reward / risk if risk > 0 else 0
        
        assessment = {
            'approved': risk_check['approved'],
            'position_value': position_value,
            'risk_amount': position_size * risk,
            'reward_amount': position_size * reward,
            'risk_reward_ratio': risk_reward_ratio,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            **risk_check
        }
        
        return assessment


# Global risk manager instance
_risk_manager = None


def get_risk_manager(config: Optional[Dict[str, Any]] = None) -> RiskManager:
    """Get or create global risk manager instance"""
    global _risk_manager
    if _risk_manager is None:
        _risk_manager = RiskManager(config)
    return _risk_manager
