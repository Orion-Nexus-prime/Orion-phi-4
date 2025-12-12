"""
Quantum Mean Reversion v6 - Quantum-inspired mean reversion strategy
"""
import numpy as np
from typing import Any, Dict, List, Optional
from src.utils.logger import get_logger
from src.utils.config_manager import get_config

logger = get_logger(__name__)


class QuantumMeanReversionStrategy:
    """
    Mean reversion strategy using quantum-inspired algorithms
    Trades when price deviates significantly from mean and predicts return to mean
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.logger = get_logger(__name__)
        self.config = config or {}
        
        # Strategy parameters
        self.lookback_period = get_config(
            'trading', 'strategies.quantum_mean_reversion.lookback_period', 20
        )
        self.std_threshold = get_config(
            'trading', 'strategies.quantum_mean_reversion.std_threshold', 2.0
        )
        self.quantum_iterations = get_config(
            'trading', 'strategies.quantum_mean_reversion.quantum_iterations', 100
        )
        
        self.logger.info("Quantum Mean Reversion Strategy v6 initialized")
    
    def analyze(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze market data and generate trading signal
        
        Args:
            market_data: Market data with prices
            
        Returns:
            Trading signal with entry, stop loss, take profit
        """
        try:
            prices = market_data.get('prices', [])
            
            if len(prices) < self.lookback_period:
                return {
                    'success': False,
                    'error': 'Insufficient data',
                    'signal': 'hold'
                }
            
            # Calculate mean and standard deviation
            recent_prices = np.array(prices[-self.lookback_period:])
            mean_price = np.mean(recent_prices)
            std_price = np.std(recent_prices)
            current_price = prices[-1]
            
            # Calculate z-score
            z_score = (current_price - mean_price) / std_price if std_price > 0 else 0
            
            # Apply quantum superposition analysis
            quantum_score = self._quantum_mean_analysis(recent_prices)
            
            # Calculate reversion probability
            reversion_prob = self._calculate_reversion_probability(z_score, quantum_score)
            
            # Generate signal
            signal = self._generate_signal(z_score, reversion_prob, current_price, mean_price)
            
            return {
                'success': True,
                'signal': signal['action'],
                'confidence': signal['confidence'],
                'entry_price': signal.get('entry_price'),
                'stop_loss': signal.get('stop_loss'),
                'take_profit': signal.get('take_profit'),
                'rationale': signal.get('rationale'),
                'z_score': float(z_score),
                'mean_price': float(mean_price),
                'quantum_score': float(quantum_score),
                'reversion_prob': float(reversion_prob),
                'strategy': 'quantum_mean_reversion'
            }
            
        except Exception as e:
            self.logger.error(f"Error in strategy analysis: {e}")
            return {
                'success': False,
                'error': str(e),
                'signal': 'hold'
            }
    
    def _quantum_mean_analysis(self, prices: np.ndarray) -> float:
        """
        Quantum-inspired analysis of price distribution
        
        Args:
            prices: Price array
            
        Returns:
            Quantum score (0-1)
        """
        # Normalize prices
        normalized = (prices - np.min(prices)) / (np.ptp(prices) + 1e-10)
        
        # Create quantum state vector
        state = normalized / (np.linalg.norm(normalized) + 1e-10)
        
        # Apply quantum rotation for iterations
        angle = np.pi / self.quantum_iterations
        for _ in range(self.quantum_iterations):
            # Quantum rotation transformation
            state = state * np.cos(angle) + np.roll(state, 1) * np.sin(angle)
        
        # Measure quantum state (collapse to definite value)
        quantum_score = np.mean(np.abs(state))
        
        return float(quantum_score)
    
    def _calculate_reversion_probability(self, z_score: float, quantum_score: float) -> float:
        """
        Calculate probability of mean reversion
        
        Args:
            z_score: Standard deviations from mean
            quantum_score: Quantum analysis score
            
        Returns:
            Reversion probability (0-1)
        """
        # Higher z-score = higher reversion probability
        z_prob = 1.0 / (1.0 + np.exp(-abs(z_score)))
        
        # Combine with quantum score
        reversion_prob = (z_prob * 0.7 + quantum_score * 0.3)
        
        return float(np.clip(reversion_prob, 0.0, 1.0))
    
    def _generate_signal(
        self,
        z_score: float,
        reversion_prob: float,
        current_price: float,
        mean_price: float
    ) -> Dict[str, Any]:
        """
        Generate trading signal based on analysis
        
        Args:
            z_score: Z-score
            reversion_prob: Reversion probability
            current_price: Current price
            mean_price: Mean price
            
        Returns:
            Trading signal
        """
        # Mean reversion signals
        if z_score > self.std_threshold and reversion_prob > 0.6:
            # Price is significantly above mean - expect reversion down
            return {
                'action': 'sell',
                'confidence': reversion_prob,
                'entry_price': current_price,
                'stop_loss': current_price * 1.02,  # 2% stop loss
                'take_profit': mean_price,
                'rationale': f'Price {z_score:.2f} std above mean, high reversion probability'
            }
        
        elif z_score < -self.std_threshold and reversion_prob > 0.6:
            # Price is significantly below mean - expect reversion up
            return {
                'action': 'buy',
                'confidence': reversion_prob,
                'entry_price': current_price,
                'stop_loss': current_price * 0.98,  # 2% stop loss
                'take_profit': mean_price,
                'rationale': f'Price {abs(z_score):.2f} std below mean, high reversion probability'
            }
        
        else:
            # No clear signal
            return {
                'action': 'hold',
                'confidence': 0.5,
                'rationale': 'Price within acceptable range or low reversion probability'
            }
    
    def get_parameters(self) -> Dict[str, Any]:
        """Get current strategy parameters"""
        return {
            'lookback_period': self.lookback_period,
            'std_threshold': self.std_threshold,
            'quantum_iterations': self.quantum_iterations
        }
