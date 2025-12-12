"""
Dark Pool Predictor v3 - Detects and predicts dark pool activity
"""
import numpy as np
from typing import Any, Dict, List, Optional
from src.utils.logger import get_logger
from src.utils.config_manager import get_config

logger = get_logger(__name__)


class DarkPoolPredictorStrategy:
    """
    Strategy that detects dark pool activity and trades accordingly
    Dark pools are private exchanges where large trades happen
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.logger = get_logger(__name__)
        self.config = config or {}
        
        # Strategy parameters
        self.detection_threshold = get_config(
            'trading', 'strategies.dark_pool_predictor.detection_threshold', 0.7
        )
        self.volume_multiplier = get_config(
            'trading', 'strategies.dark_pool_predictor.volume_multiplier', 1.5
        )
        
        self.logger.info("Dark Pool Predictor Strategy v3 initialized")
    
    def analyze(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze market data for dark pool activity
        
        Args:
            market_data: Market data with prices and volumes
            
        Returns:
            Trading signal
        """
        try:
            prices = market_data.get('prices', [])
            volumes = market_data.get('volumes', [])
            
            if len(prices) < 20 or len(volumes) < 20:
                return {
                    'success': False,
                    'error': 'Insufficient data',
                    'signal': 'hold'
                }
            
            # Detect dark pool activity
            dark_pool_score = self._detect_dark_pool_activity(prices, volumes)
            
            # Analyze price impact
            price_impact = self._analyze_price_impact(prices, volumes)
            
            # Predict future movement
            prediction = self._predict_movement(dark_pool_score, price_impact, prices)
            
            # Generate signal
            signal = self._generate_signal(prediction, prices[-1], dark_pool_score)
            
            return {
                'success': True,
                'signal': signal['action'],
                'confidence': signal['confidence'],
                'entry_price': signal.get('entry_price'),
                'stop_loss': signal.get('stop_loss'),
                'take_profit': signal.get('take_profit'),
                'rationale': signal.get('rationale'),
                'dark_pool_score': float(dark_pool_score),
                'price_impact': float(price_impact),
                'strategy': 'dark_pool_predictor'
            }
            
        except Exception as e:
            self.logger.error(f"Error in strategy analysis: {e}")
            return {
                'success': False,
                'error': str(e),
                'signal': 'hold'
            }
    
    def _detect_dark_pool_activity(self, prices: List[float], volumes: List[float]) -> float:
        """
        Detect dark pool activity based on volume and price patterns
        
        Args:
            prices: Price history
            volumes: Volume history
            
        Returns:
            Dark pool activity score (0-1)
        """
        prices_array = np.array(prices[-20:])
        volumes_array = np.array(volumes[-20:])
        
        # Calculate average volume
        avg_volume = np.mean(volumes_array[:-5])
        recent_volume = np.mean(volumes_array[-5:])
        
        # Volume spike indicator
        volume_spike = recent_volume / (avg_volume + 1e-10)
        
        # Price movement analysis
        price_change = abs(prices_array[-1] - prices_array[-5]) / prices_array[-5]
        
        # Dark pool characteristics:
        # 1. High volume with low price movement (hidden trades)
        # 2. Sudden volume spikes followed by price movement
        
        # Score based on volume spike with minimal price impact
        if volume_spike > self.volume_multiplier and price_change < 0.02:
            # High volume, low price change = potential dark pool
            dark_pool_score = min(volume_spike / 3.0, 1.0)
        else:
            dark_pool_score = 0.0
        
        return float(dark_pool_score)
    
    def _analyze_price_impact(self, prices: List[float], volumes: List[float]) -> float:
        """
        Analyze price impact of volume changes
        
        Args:
            prices: Price history
            volumes: Volume history
            
        Returns:
            Price impact score
        """
        prices_array = np.array(prices[-20:])
        volumes_array = np.array(volumes[-20:])
        
        # Calculate price changes
        price_changes = np.diff(prices_array) / prices_array[:-1]
        
        # Calculate volume changes
        volume_changes = np.diff(volumes_array)
        
        # Correlation between volume and price changes
        if len(price_changes) > 1 and len(volume_changes) > 1:
            # Low correlation suggests dark pool activity
            correlation = np.corrcoef(price_changes[-10:], volume_changes[-10:])[0, 1]
            
            # Inverse correlation score (lower correlation = higher dark pool likelihood)
            impact_score = 1.0 - abs(correlation)
        else:
            impact_score = 0.5
        
        return float(impact_score)
    
    def _predict_movement(
        self,
        dark_pool_score: float,
        price_impact: float,
        prices: List[float]
    ) -> Dict[str, Any]:
        """
        Predict future price movement based on dark pool activity
        
        Args:
            dark_pool_score: Dark pool activity score
            price_impact: Price impact score
            prices: Price history
            
        Returns:
            Movement prediction
        """
        # Calculate price momentum
        prices_array = np.array(prices[-10:])
        momentum = (prices_array[-1] - prices_array[0]) / prices_array[0]
        
        # Dark pool activity often precedes large moves
        # Direction depends on whether accumulation or distribution
        
        if dark_pool_score > self.detection_threshold:
            # High dark pool activity detected
            
            if momentum > 0:
                # Positive momentum + dark pool = likely continuation up
                direction = 'up'
                strength = min(dark_pool_score * 1.5, 1.0)
            else:
                # Negative momentum + dark pool = likely continuation down
                direction = 'down'
                strength = min(dark_pool_score * 1.5, 1.0)
        else:
            # No significant dark pool activity
            direction = 'neutral'
            strength = 0.5
        
        return {
            'direction': direction,
            'strength': strength,
            'momentum': float(momentum)
        }
    
    def _generate_signal(
        self,
        prediction: Dict[str, Any],
        current_price: float,
        dark_pool_score: float
    ) -> Dict[str, Any]:
        """
        Generate trading signal from prediction
        
        Args:
            prediction: Movement prediction
            current_price: Current price
            dark_pool_score: Dark pool activity score
            
        Returns:
            Trading signal
        """
        direction = prediction['direction']
        strength = prediction['strength']
        
        if direction == 'up' and strength > 0.6:
            return {
                'action': 'buy',
                'confidence': strength,
                'entry_price': current_price,
                'stop_loss': current_price * 0.96,  # 4% stop loss
                'take_profit': current_price * 1.08,  # 8% take profit
                'rationale': f'Dark pool accumulation detected (score: {dark_pool_score:.2f}), expecting upward movement'
            }
        
        elif direction == 'down' and strength > 0.6:
            return {
                'action': 'sell',
                'confidence': strength,
                'entry_price': current_price,
                'stop_loss': current_price * 1.04,  # 4% stop loss
                'take_profit': current_price * 0.92,  # 8% take profit
                'rationale': f'Dark pool distribution detected (score: {dark_pool_score:.2f}), expecting downward movement'
            }
        
        else:
            return {
                'action': 'hold',
                'confidence': 0.5,
                'rationale': 'No significant dark pool activity or unclear direction'
            }
    
    def _detect_block_trades(self, volumes: List[float]) -> List[int]:
        """
        Detect block trades (unusually large trades)
        
        Args:
            volumes: Volume history
            
        Returns:
            Indices of detected block trades
        """
        volumes_array = np.array(volumes)
        mean_volume = np.mean(volumes_array)
        std_volume = np.std(volumes_array)
        
        # Block trades are typically > 3 standard deviations
        threshold = mean_volume + 3 * std_volume
        
        block_trades = []
        for i, vol in enumerate(volumes_array):
            if vol > threshold:
                block_trades.append(i)
        
        return block_trades
    
    def get_parameters(self) -> Dict[str, Any]:
        """Get current strategy parameters"""
        return {
            'detection_threshold': self.detection_threshold,
            'volume_multiplier': self.volume_multiplier
        }
